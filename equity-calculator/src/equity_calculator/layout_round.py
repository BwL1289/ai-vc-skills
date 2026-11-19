"""The round's report lines (the ``Convertibles`` sheet): the inputs, each SAFE or note converted, the cap table.

One value column. Each instrument gets a block of lines (what converts, its cap and discount prices, the price it
took and its shares); the round's price, Company Capitalization and new shares follow, then the cap table with live
totals of shares, ownership and value.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import fraction, quantity
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_round import ConversionRow, RoundCapTableRow, RoundResult
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Convertibles"
_HEADING = "SAFEs and notes converting in a priced round: the price, each conversion and who owns what after"
_COLUMNS = ("This round",)
_KIND_NAMES = {"safe": "SAFE", "note": "Note"}
_HOLDER_NAMES = {"existing_holders": "existing holders", "option_pool": "option pool", "investor": "investor"}
_HOLDER_SHARES_HOW = {"existing_holders": "FD - U", "option_pool": "U + P", "investor": "N = I/p"}
_CAP_HOW = {"safe": "K/C (post-money cap over Company Capitalization)", "note": "K/FD (pre-money cap over FD)"}
_BASIS_NAMES = {"cap": "its cap", "discount": "its discount", "round_price": "the round price"}
_TOTAL_OWNERSHIP_HOW = "100% exactly; the rounded rows can miss it in the last place"
_TIMING_HOW = {
    "pre_money": "p = num/((FD + F)/(1 - sigma) - U), num = V - t(V + I) - D/(1 - sigma)",
    "post_money": "p = (V(1 - sigma) - D)/(FD + F)",
}


def _instrument_name(kind: str, index: int) -> str:
    return f"{_KIND_NAMES[kind]} {index}"


def _conversion_lines(row: ConversionRow) -> list[Line]:
    """One instrument's block: amount, interest, what converts, its prices, the one it took, its shares."""
    name = _instrument_name(row.kind, row.index)
    key = f"{row.kind}_{row.index}"
    lines = [
        Line(
            f"{key}_amount", f"{name}: {'purchase amount' if row.kind == 'safe' else 'principal'}", (row.amount,), GIVEN
        )
    ]
    if row.accrued_interest is not None:
        how = "owed at the round (to the cent) - principal" + (
            "; fractional-power stub, approximate" if row.interest_approximate else ""
        )
        lines.append(Line(f"{key}_interest", f"{name}: accrued interest", (row.accrued_interest,), how))
    lines.append(
        Line(
            f"{key}_converting",
            f"{name}: amount converting (a)",
            (row.converting_amount,),
            "the amount, plus interest unless paid in cash",
        )
    )
    if row.cap_price is not None:
        lines.append(Line(f"{key}_cap_price", f"{name}: cap price", (row.cap_price,), _CAP_HOW[row.kind]))
    if row.discount_price is not None:
        lines.append(
            Line(f"{key}_discount_price", f"{name}: discount price", (row.discount_price,), "p·(1 - discount)")
        )
    lines += [
        Line(
            f"{key}_price", f"{name}: conversion price", (row.conversion_price,), "the lower price; a tie takes the cap"
        ),
        Line(f"{key}_basis", f"{name}: converts at", (_BASIS_NAMES[row.basis],), "the price it took"),
        Line(f"{key}_shares", f"{name}: shares", (row.shares,), "a / conversion price"),
    ]

    return lines


def _holder_label(row: RoundCapTableRow) -> tuple[str, str]:
    """(line key part, label part) for one cap-table row."""
    if row.instrument is None:
        return row.holder, _HOLDER_NAMES[row.holder]

    return f"{row.holder}_{row.instrument}", _instrument_name(row.holder, row.instrument)


def _cap_table_lines(result: RoundResult) -> list[Line]:
    """Shares, ownership and value per holder, each with its live total."""
    labelled = [(_holder_label(row), row) for row in result.rows]
    shares_how = {row.holder: _HOLDER_SHARES_HOW.get(row.holder, "from its conversion") for row in result.rows}
    total_ownership = quantity("fraction", sum((row.ownership.exact for row in result.rows), fraction(0)))
    lines = [
        Line(f"shares_{part}", f"Shares: {label}", (row.shares,), shares_how[row.holder])
        for (part, label), row in labelled
    ]
    lines.append(
        Line(
            "total_shares",
            "Total shares (T)",
            (result.total_shares,),
            "every holder's shares",
            tuple(f"shares_{part}" for (part, _), _ in labelled),
        )
    )
    lines += [
        Line(f"ownership_{part}", f"Ownership: {label}", (row.ownership,), "shares / T")
        for (part, label), row in labelled
    ]
    lines.append(
        Line(
            "total_ownership",
            "Ownership: total",
            (total_ownership,),
            _TOTAL_OWNERSHIP_HOW,
            tuple(f"ownership_{part}" for (part, _), _ in labelled),
        )
    )
    lines += [
        Line(f"value_{part}", f"Value at p: {label}", (row.value,), "shares·p, cents by largest remainder")
        for (part, label), row in labelled
    ]
    lines.append(
        Line(
            "post_money",
            "Post-money (every share at p)",
            (result.post_money,),
            "T·p",
            tuple(f"value_{part}" for (part, _), _ in labelled),
        )
    )

    return lines


def round_sheet(result: RoundResult) -> Sheet:
    """The round's lines: inputs, each conversion, the price and new shares, the cap table."""
    inputs = result.inputs
    values: tuple[tuple[str, str, EquityQuantity | str, str], ...] = (
        (
            "fully_diluted_shares",
            "Fully diluted shares before (FD)",
            given("shares", Decimal(inputs.fully_diluted_shares)),
            GIVEN,
        ),
        (
            "unissued_pool_shares",
            "Unissued pool before (U)",
            given("shares", Decimal(inputs.unissued_pool_shares)),
            GIVEN,
        ),
        ("pre_money", "Pre-money valuation (V)", given("money", inputs.pre_money), GIVEN),
        ("investment", "Investment (I)", given("money", inputs.investment), GIVEN),
        ("target_pool", "Target pool after the round (t)", given_percent(inputs.target_pool_percent), GIVEN),
        ("pool_timing", "Pool counted in the", inputs.pool_timing.replace("_", "-"), GIVEN),
    )
    lines = [Line(key, label, (value,), how) for key, label, value, how in values]
    for row in result.conversions:
        lines += _conversion_lines(row)
    lines += [
        Line(
            "capped_safe_fraction",
            "Capped SAFEs' share of C (sigma)",
            (result.capped_safe_fraction,),
            "sum of a/K over SAFEs on their cap",
        ),
        Line(
            "company_capitalization",
            "Company Capitalization (C)",
            (result.company_capitalization,),
            "(FD + F + D/p)/(1 - sigma)",
        ),
        Line(
            "new_pool_shares",
            "New pool shares (P)",
            (result.new_pool_shares,),
            "pre: t(V + I)/p - U; post: (t(C + N) - U)/(1 - t); 0 when not positive",
        ),
        Line("price_per_share", "Price per share (p)", (result.price_per_share,), _TIMING_HOW[inputs.pool_timing]),
        Line("investor_shares", "Investor shares (N)", (result.investor_shares,), "I/p"),
        Line(
            "passes",
            "Passes of the conversion search",
            (str(result.passes),),
            "at most one more than the capped instruments",
        ),
    ]
    lines += _cap_table_lines(result)
    lines.append(
        Line(
            "pool_already_large_enough",
            "Unissued pool already meets the target",
            (yes_no(result.pool_already_large_enough),),
            "then P = 0",
        )
    )

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
