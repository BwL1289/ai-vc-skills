"""The option-pool shuffle's report lines: both tables, the pool counted pre-money and post-money."""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import fraction, quantity
from equity_calculator.schemas.equity import PoolCapTable, PoolResult
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_POOL_HEADING = "Option-pool shuffle: the round worked with the pool in the pre-money and in the post-money"
_GROUP_LABELS = {"existing_holders": "existing holders", "option_pool": "option pool", "investor": "investor"}
_SHARES_HOW = {"existing_holders": "FD - U", "option_pool": "U + P", "investor": "N = I/p"}
# The exact total is 1; each ownership row is rounded on its own, so their sum can miss 100% in the last place.
_TOTAL_OWNERSHIP_HOW = "100% exactly; the rounded rows can miss it in the last place"

# The pool sheet's lines that are not one-per-cap-table-group, in order: (key, label, how it is computed). The
# group lines (shares, ownership, value at p) and their totals are built from the cap table's rows.
_POOL_INPUT_LINES = (
    ("fully_diluted_shares", "Fully diluted shares before (FD)", GIVEN),
    ("unissued_pool_shares", "Unissued pool before (U)", GIVEN),
    ("pre_money", "Pre-money valuation (V)", GIVEN),
    ("investment", "Investment (I)", GIVEN),
    ("target_pool", "Target pool after the round (t)", GIVEN),
    ("investor_fraction", "Investment's share of V + I (r)", "I/(V + I)"),
    (
        "new_pool_shares",
        "New pool shares (P)",
        "pre: (t·FD - (1 - r)U)/(1 - r - t); post: (t(FD + N) - U)/(1 - t); 0 when not positive",
    ),
    ("price_per_share", "Price per share (p)", "pre: V/(FD + P); post: V/FD"),
)
_POOL_CLOSING_LINES = (
    ("effective_pre_money", "Effective pre-money", "(FD - U)·p: the holders' shares at the round price"),
    ("uninvested_cash", "Cash not converted to shares", "I - N·p (whole shares only)"),
    ("pool_already_large_enough", "Unissued pool already meets the target", "then P = 0"),
)


def _pool_values(result: PoolResult, table: PoolCapTable) -> dict[str, EquityQuantity | str]:
    """One pool table's column of values by line key, the inputs repeated so both columns read alone."""
    inputs = result.inputs
    values: dict[str, EquityQuantity | str] = {
        "fully_diluted_shares": given("shares", Decimal(inputs.fully_diluted_shares)),
        "unissued_pool_shares": given("shares", Decimal(inputs.unissued_pool_shares)),
        "pre_money": given("money", inputs.pre_money),
        "investment": given("money", inputs.investment),
        "target_pool": given_percent(inputs.target_pool_percent),
        "investor_fraction": result.investor_fraction,
        "new_pool_shares": table.new_pool_shares,
        "price_per_share": table.price_per_share,
        "total_shares": table.total_shares,
        "total_ownership": quantity("fraction", sum((row.ownership.exact for row in table.rows), fraction(0))),
        "post_money": table.post_money,
        "effective_pre_money": table.effective_pre_money,
        "uninvested_cash": table.uninvested_cash,
        "pool_already_large_enough": yes_no(table.pool_already_large_enough),
    }
    for row in table.rows:
        values[f"shares_{row.group}"] = row.shares
        values[f"ownership_{row.group}"] = row.ownership
        values[f"value_{row.group}"] = row.value

    return values


def pool_sheet(result: PoolResult) -> Sheet:
    """The option-pool shuffle's lines: the inputs, then each table's pool, price and who owns what."""
    tables = (result.pool_in_pre_money, result.pool_in_post_money)
    columns = tuple(
        f"Pool in {table.timing.replace('_', '-')}"
        + (" (this deal)" if table.timing == result.inputs.pool_timing else "")
        for table in tables
    )
    by_table = [_pool_values(result, table) for table in tables]
    groups = tuple(row.group for row in result.pool_in_pre_money.rows)

    def line(key: str, label: str, how: str, total_of: tuple[str, ...] = ()) -> Line:
        return Line(key, label, tuple(values[key] for values in by_table), how, total_of)

    def group_lines(prefix: str, label: str, how: dict[str, str]) -> list[Line]:
        return [line(f"{prefix}_{group}", f"{label}: {_GROUP_LABELS[group]}", how[group]) for group in groups]

    def keys(prefix: str) -> tuple[str, ...]:
        return tuple(f"{prefix}_{group}" for group in groups)

    lines = [line(key, label, how) for key, label, how in _POOL_INPUT_LINES]
    lines += group_lines("shares", "Shares", _SHARES_HOW)
    lines.append(line("total_shares", "Total shares (T)", "FD + P + N", keys("shares")))
    lines += group_lines("ownership", "Ownership", dict.fromkeys(groups, "shares / T"))
    lines.append(line("total_ownership", "Ownership: total", _TOTAL_OWNERSHIP_HOW, keys("ownership")))
    lines += group_lines("value", "Value at p", dict.fromkeys(groups, "shares·p, cents by largest remainder"))
    lines.append(line("post_money", "Post-money (every share at p)", "T·p", keys("value")))
    lines += [line(key, label, how) for key, label, how in _POOL_CLOSING_LINES]

    return Sheet("Pool", _POOL_HEADING, columns, tuple(lines), result.assumptions)
