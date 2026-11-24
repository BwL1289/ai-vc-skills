"""A pool sized from the hiring plan beside the term sheet's (the ``Pool plan`` sheet): plan, requested, requested -
plan.

The inputs come first (in both columns), then each hire with its grant and whether it counts, then the round worked at
each pool: the pool's share, the new pool, the price, who owns what, the pool left when the next round comes and the
effective pre-money, each with the requested column less the plan's; then the flags in plain words. A cell that does
not apply is empty. Values only: no line carries a live formula, and no line says which pool to accept.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_pool import CapTableGroup, PoolCapTable
from equity_calculator.schemas.equity_pool_plan import PlannedHire, PoolPlanFlag, PoolPlanResult
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Pool plan"
_HEADING = (
    "The option pool the hiring plan needs to the next round beside the pool the term sheet asks for: the round at "
    "each, the pool created in the pre-money"
)
_COLUMNS = ("Plan: hires to the next round", "Term sheet: requested pool", "Requested - plan")
_EMPTY = ""
_GROUP_NAMES: dict[CapTableGroup, str] = {
    "existing_holders": "existing holders",
    "option_pool": "option pool",
    "investor": "investor",
}
_TARGET_HOW = {
    "shares": "plan: G·V/((V + I)(FD - U + G)), the pool holding exactly G; requested: given",
    "percent": "plan: the counted grants' percents added up; requested: given",
}
# Grants in shares that fit in today's pool: no top-up, so the plan column has FD shares before the round and t_plan is
# the grants' share of its total, G/T.
_TARGET_HOW_SHARES_FIT = "plan: G·V/((V + I)·FD), the grants' share with today's pool kept whole; requested: given"
_GRANTS_HOW = {
    "shares": "G: the counted grants added up",
    "percent": "the counted grants' percents of this column's T",
}


def _both(value: EquityQuantity | str) -> tuple[EquityQuantity | str, ...]:
    """A value shown in both columns, with no difference."""
    return (value, value, _EMPTY)


def _given_lines(result: PoolPlanResult) -> list[Line]:
    """The inputs, the same in both columns."""
    inputs = result.inputs
    lines = [
        Line(
            "fully_diluted_shares",
            "Fully diluted shares before (FD)",
            _both(given("shares", Decimal(inputs.fully_diluted_shares))),
            GIVEN,
        ),
        Line(
            "unissued_pool_shares",
            "Unissued pool before (U)",
            _both(given("shares", Decimal(inputs.unissued_pool_shares))),
            GIVEN,
        ),
    ]
    if inputs.founder_shares is not None:
        lines.append(
            Line(
                "founder_shares", "Founders' shares (F)", _both(given("shares", Decimal(inputs.founder_shares))), GIVEN
            )
        )
    lines += [
        Line("pre_money", "Pre-money valuation (V)", _both(given("money", inputs.pre_money)), GIVEN),
        Line("investment", "Investment (I)", _both(given("money", inputs.investment)), GIVEN),
        Line(
            "next_round_month",
            "Next round, months from today",
            _both(given("months", Decimal(inputs.next_round_month))),
            GIVEN,
        ),
    ]
    return lines


def _grant(hire: PlannedHire) -> EquityQuantity:
    """A hire's grant as given: shares, or the percent of the post-round fully diluted shares as a fraction."""
    if hire.grant_shares is not None:
        return given("shares", Decimal(hire.grant_shares))
    return given_percent(hire.grant_percent if hire.grant_percent is not None else Decimal(0))


def _hire_lines(result: PoolPlanResult) -> list[Line]:
    """Each hire: its grant in the plan column, and whether it starts by the next round."""
    month = result.inputs.next_round_month
    lines = []
    for index, hire in enumerate(result.inputs.hires, start=1):
        counted = hire.start_month <= month
        how = (
            f"counted: starts by month {month}" if counted else f"left out: starts after month {month}, the next round"
        )
        label = f"Hire {index}: {hire.role}, from month {hire.start_month}"
        lines.append(Line(f"hire_{index}", label, (_grant(hire), _EMPTY, _EMPTY), how))
    return lines


def _ownership(table: PoolCapTable, group: CapTableGroup) -> EquityQuantity:
    return next(row.ownership for row in table.rows if row.group == group)


def _shares(table: PoolCapTable, group: CapTableGroup) -> EquityQuantity:
    return next(row.shares for row in table.rows if row.group == group)


def _round_lines(result: PoolPlanResult) -> list[Line]:
    """The round at each pool, with the requested column less the plan's where the result carries it."""
    plan, requested, difference = result.plan, result.requested, result.requested_minus_plan
    unit = result.grant_unit
    plan_table, requested_table = plan.cap_table, requested.cap_table

    def pair(
        plan_value: EquityQuantity, requested_value: EquityQuantity, diff: EquityQuantity | None = None
    ) -> tuple[EquityQuantity | str, ...]:
        return (plan_value, requested_value, _EMPTY if diff is None else diff)

    fits = unit == "shares" and plan_table.pool_already_large_enough
    lines = [
        Line(
            "grant_shares",
            "Shares the counted grants take",
            pair(plan.grant_shares, requested.grant_shares),
            _GRANTS_HOW[unit],
        ),
        Line(
            "target_pool",
            "Target pool after the round (t)",
            pair(plan.target_pool, requested.target_pool, difference.target_pool),
            _TARGET_HOW_SHARES_FIT if fits else _TARGET_HOW[unit],
        ),
        Line("investor_fraction", "Investment's share of V + I (r)", _both(result.investor_fraction), "I/(V + I)"),
        Line(
            "new_pool_shares",
            "New pool shares (P)",
            pair(plan_table.new_pool_shares, requested_table.new_pool_shares, difference.new_pool_shares),
            "(t·FD - (1 - r)U)/(1 - r - t), 0 when not positive: the pool scenario's",
        ),
        Line(
            "price_per_share",
            "Price per share (p)",
            pair(plan_table.price_per_share, requested_table.price_per_share, difference.price_per_share),
            "V/(FD + P)",
        ),
        Line(
            "total_shares",
            "Total shares (T)",
            pair(plan_table.total_shares, requested_table.total_shares),
            "FD + P + N",
        ),
    ]
    for group in ("existing_holders", "option_pool", "investor"):
        lines.append(
            Line(
                f"shares_{group}",
                f"Shares: {_GROUP_NAMES[group]}",
                pair(_shares(plan_table, group), _shares(requested_table, group)),
                {"existing_holders": "FD - U", "option_pool": "U + P", "investor": "N = I/p"}[group],
            )
        )
    group_differences: dict[CapTableGroup, EquityQuantity | None] = {
        "existing_holders": difference.existing_holders_ownership,
        "option_pool": difference.option_pool_ownership,
        "investor": None,
    }
    for group, diff in group_differences.items():
        lines.append(
            Line(
                f"ownership_{group}",
                f"Ownership: {_GROUP_NAMES[group]}",
                pair(_ownership(plan_table, group), _ownership(requested_table, group), diff),
                "shares / T",
            )
        )
    if plan.founders_ownership is not None and requested.founders_ownership is not None:
        lines.append(
            Line(
                "ownership_founders",
                "Ownership: founders",
                pair(plan.founders_ownership, requested.founders_ownership, difference.founders_ownership),
                "F / T (founders are among the existing holders)",
            )
        )
    lines += [
        Line(
            "pool_left_at_next_round",
            "Pool left ungranted at the next round",
            pair(plan.pool_left_at_next_round, requested.pool_left_at_next_round, difference.pool_left_at_next_round),
            "U + P - the counted grants' shares; below 0, the pool runs short before the next round",
        ),
        Line(
            "effective_pre_money",
            "Effective pre-money",
            pair(plan_table.effective_pre_money, requested_table.effective_pre_money, difference.effective_pre_money),
            "(FD - U)·p: the holders' shares at the round price",
        ),
        Line(
            "post_money",
            "Post-money (every share at p)",
            pair(plan_table.post_money, requested_table.post_money),
            "T·p = V + I",
        ),
        Line(
            "pool_already_large_enough",
            "Unissued pool already meets it",
            (yes_no(plan_table.pool_already_large_enough), yes_no(requested_table.pool_already_large_enough), _EMPTY),
            "then P = 0: no top-up",
        ),
    ]
    return lines


def _flag_words(flag: PoolPlanFlag, result: PoolPlanResult) -> str:
    """What a flag means for the founder, in plain words; none says which pool to accept."""
    month = result.inputs.next_round_month
    left_out = result.hires_left_out
    requested_adds_nothing = result.requested.cap_table.new_pool_shares.exact == 0
    runs_short = result.requested.pool_left_at_next_round.exact < 0
    words: dict[PoolPlanFlag, str] = {
        "no_hires_before_next_round": f"No hire starts on or before month {month}, so the plan needs no pool before "
        "the next round",
        "hires_after_next_round_ignored": (
            f"1 hire starts after month {month} and is left out of the plan: the next round's own pool would cover it"
            if left_out == 1
            else f"{left_out} hires start after month {month} and are left out of the plan: the next round's own "
            "pool would cover them"
        ),
        "plan_fits_current_pool": "The plan's grants fit in today's unissued pool, so the plan needs no top-up",
        "requested_met_by_current_pool": "Today's unissued pool already meets the requested percent, so the term "
        "sheet's pool needs no top-up either",
        "requested_above_plan": (
            "The requested pool's target is above the plan's, but today's unissued pool already meets it, so it adds "
            "no shares and moves no price"
            if requested_adds_nothing
            else "The requested pool is larger than the plan's: the difference column shows what the larger pool does "
            "to the price, the effective pre-money and who owns what"
        ),
        "requested_below_plan": (
            "The requested pool is smaller than the plan's: the plan's grants would run short of it before the next "
            "round (see the pool left line)"
            if runs_short
            else "The requested pool's target is below the plan's, but today's unissued pool already holds the plan's "
            "grants (see the pool left line)"
        ),
    }
    return words[flag]


def pool_plan_sheet(result: PoolPlanResult) -> Sheet:
    """The pool plan's lines: the inputs, the hires, the round at each pool and the difference, then the flags."""
    lines = _given_lines(result) + _hire_lines(result) + _round_lines(result)
    lines += [Line(f"flag_{flag}", "Flag", (flag, _EMPTY, _EMPTY), _flag_words(flag, result)) for flag in result.flags]
    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
