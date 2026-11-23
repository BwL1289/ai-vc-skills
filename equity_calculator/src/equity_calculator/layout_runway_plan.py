"""A runway plan's report lines (the ``Runway plan`` sheet): the plan as given, each case, runway, milestones, checks.

One value column. The inputs come first, then each case's phases as worked, a runway line per option and case (with
the cash when a later raise lands, and when to start raising), a slack and a verdict line per option, case and
milestone, the smallest raise per milestone, case and landing month, each option's use-of-funds lines (with their
live total), each stated figure checked, the flags in plain words and the overall verdict. Option 0 is ``no raise``;
the raises are ``raise 1``, ``raise 2``, … in the order given. Values only: no line carries a live formula beyond the
``=SUM`` totals.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_runway_plan import (
    MilestoneRow,
    OptionFunds,
    OptionRunway,
    PhaseRow,
    RequiredRaiseRow,
    RunwayCase,
    RunwayPlanCheck,
    RunwayPlanFlag,
    RunwayPlanResult,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Runway plan"
_HEADING = "How long each raise lasts on the founder's plan and cases, and which milestones it reaches"
_COLUMNS = ("This plan",)
_NEVER = "none: the cash never runs out"
_NO_AMOUNT = "none: the cash runs out before it lands"
_CHECK_HOW = {
    "runway_months": "the plan case's runway",
    "use_of_funds_total": "against the raise (or 100%)",
}


def option_name(option: int) -> str:
    """Option 0 is ``no raise``; the raises are ``raise 1``, ``raise 2``, … in the order given."""
    return "no raise" if option == 0 else f"raise {option}"


def _flag_words(flag: RunwayPlanFlag, result: RunwayPlanResult) -> str:
    """What a flag means for the founder, in plain words."""
    inputs = result.inputs
    words: dict[RunwayPlanFlag, str] = {
        "cash_never_runs_out": "On at least one case revenue covers the burn before the cash runs out, so that "
        "runway has no end; a stated runway there is not checked",
        "cash_out_before_raise_lands": "On at least one case the cash goes below the floor before a later raise "
        "lands, so that raise comes too late as planned",
        "milestone_short_on_plan": "A raise does not reach a milestone"
        + ("" if inputs.months_to_raise is None else ", with the months to raise,")
        + " on the plan itself",
        "downside_short_where_plan_covers": "A raise reaches a milestone on the plan but not on the downside; be "
        "ready to say what happens if the plan is missed",
        "covered_without_raise": "The cash already reaches a milestone with no raise on at least one case",
        "start_raising_date_passed": "With no raise, the plan's runway less the months to raise is already at or "
        "past today: on the plan, raising the next round takes longer than the cash lasts",
        "no_time_to_raise_given": "No months to raise were given, so each milestone is checked at its own month, "
        "with no time left to raise the next round",
        "runway_below_band": f"A raise lasts under {inputs.runway_band_months} months on the plan; be ready to say "
        "which milestone it reaches (a common benchmark, not a rule)",
    }
    return words[flag]


def _maybe(value: Decimal | None, unit: EquityUnit = "months") -> EquityQuantity | None:
    return None if value is None else given(unit, value)


def _given_lines(result: RunwayPlanResult) -> list[Line]:
    """The plan as given: cash, floor, months to raise, the stated runway, each raise, the milestones, tolerances."""
    inputs = result.inputs
    checked = bool(result.checks)
    shown: list[tuple[str, str, EquityQuantity | str | None, str]] = [
        ("cash_on_hand", "Cash on hand", given("money", inputs.cash_on_hand), GIVEN),
        ("cash_floor", "Cash floor (kept in the bank)", _maybe(inputs.cash_floor or None, "money"), GIVEN),
        ("months_to_raise", "Months to raise the next round", _maybe(_whole(inputs.months_to_raise)), GIVEN),
        ("given_runway", "Runway with no raise as stated", _maybe(inputs.stated_runway_months), GIVEN),
    ]
    for option, raise_given in enumerate(inputs.raises, start=1):
        name = f"Raise {option}"
        lands = _whole(raise_given.lands_month or None)
        stated = raise_given.stated_runway_months
        shown += [
            (f"raise_{option}_amount", f"{name}: amount", given("money", raise_given.amount), GIVEN),
            (f"raise_{option}_lands", f"{name}: lands after", _maybe(lands), "whole months from today"),
            (
                f"raise_{option}_stated_runway",
                f"{name}: runway as stated",
                _maybe(stated),
                _stated_how(result, option),
            ),
        ]
    for number, month in enumerate(inputs.milestones, start=1):
        shown.append(
            (f"milestone_{number}", f"Milestone {number}", given("months", Decimal(month)), "months from today")
        )
    shown += [
        (
            "tolerance_points",
            "Tolerance for percent lines",
            given_percent(inputs.tolerance_points) if checked else None,
            GIVEN,
        ),
        (
            "tolerance_percent",
            "Tolerance for months or money",
            given_percent(inputs.tolerance_percent) if checked else None,
            GIVEN,
        ),
        (
            "runway_band",
            "Runway benchmark",
            given("months", inputs.runway_band_months) if inputs.raises else None,
            GIVEN,
        ),
    ]
    return [Line(key, label, (value,), how) for key, label, value, how in shown if value is not None]


def _stated_how(result: RunwayPlanResult, option: int) -> str:
    """How a raise's stated runway counts, and why it is not checked when it counts from a landing the cash does not
    reach on the plan."""
    if result.inputs.raises[option - 1].stated_runway_from == "today":
        return "given, counted from today"
    plan_row = next(row for row in result.runway if row.case == result.cases[0].name and row.option == option)
    if plan_row.ran_out_before_landing:
        return "given, counted from when it lands; not checked: on the plan the cash runs out before it lands"
    return "given, counted from when it lands"


def _whole(value: int | None) -> Decimal | None:
    return None if value is None else Decimal(value)


def _phase_months(phase: PhaseRow) -> str:
    """The months a phase covers: ``month 4 on`` for the last, ``month 3`` for one month, else ``months 1-3``."""
    if phase.to_month is None:
        return f"month {phase.from_month} on"
    if phase.to_month == phase.from_month:
        return f"month {phase.from_month}"
    return f"months {phase.from_month}-{phase.to_month}"


def _case_lines(case: RunwayCase, derived: bool) -> list[Line]:
    """One case's phases as worked: gross burn, revenue and net burn a month for each."""
    how = "the plan's, scaled by the case's percent" if derived else GIVEN
    lines = []
    for number, phase in enumerate(case.phases, start=1):
        name = f"{case.name.capitalize()}, phase {number} ({_phase_months(phase)})"
        key = f"{case.name}_phase_{number}"
        lines += [
            Line(f"{key}_gross", f"{name}: gross burn a month", (phase.gross_burn,), how),
            Line(f"{key}_revenue", f"{name}: revenue a month", (phase.revenue,), how),
            Line(f"{key}_net", f"{name}: net burn a month", (phase.net_burn,), "gross burn - revenue"),
        ]
    return lines


def _runway_lines(row: OptionRunway) -> list[Line]:
    """One option on one case: its runway, and with a later raise the cash then and the runway from landing."""
    name = f"{row.case}, {option_name(row.option)}"
    key = f"{row.case}_{row.option}"
    runway: EquityQuantity | str = _NEVER if row.runway_months is None else row.runway_months
    lines = [Line(f"runway_{key}", f"Runway, {name}", (runway,), "months until cash less the floor goes below zero")]
    if row.lands_month > 0:
        lines.append(
            Line(
                f"ran_out_{key}",
                f"Ran out before the money lands, {name}",
                (yes_no(row.ran_out_before_landing),),
                f"cash below the floor before month {row.lands_month} ends",
            )
        )
    if row.cash_at_landing is not None:
        lines.append(
            Line(
                f"cash_at_landing_{key}",
                f"Cash above the floor when it lands, {name}",
                (row.cash_at_landing,),
                "before the raise",
            )
        )
    if row.runway_from_landing is not None:
        lines.append(
            Line(
                f"runway_from_landing_{key}",
                f"Runway from landing, {name}",
                (row.runway_from_landing,),
                "runway - months until it lands",
            )
        )
    if row.start_raising_by is not None:
        lines.append(
            Line(
                f"start_raising_{key}", f"Start raising by, {name}", (row.start_raising_by,), "runway - months to raise"
            )
        )
    return lines


def _milestone_lines(row: MilestoneRow) -> list[Line]:
    """One option, case and milestone: the slack and the verdict."""
    name = f"Milestone {row.milestone} (month {row.month}), {row.case}, {option_name(row.option)}"
    key = f"milestone_{row.milestone}_{row.case}_{row.option}"
    slack: EquityQuantity | str = _NEVER if row.slack_months is None else row.slack_months
    return [
        Line(f"{key}_slack", f"{name}: slack", (slack,), "runway - the milestone month"),
        Line(
            f"{key}_verdict",
            f"{name}: verdict",
            (row.verdict,),
            f"covered when the runway reaches month {row.target_month}",
            verdict=True,
        ),
    ]


def _required_line(row: RequiredRaiseRow) -> Line:
    """The smallest raise for one milestone, case and landing month."""
    amount: EquityQuantity | str = _NO_AMOUNT if row.amount is None else row.amount
    return Line(
        f"required_{row.milestone}_{row.case}_{row.lands_month}",
        f"Required raise, milestone {row.milestone}, {row.case}, landing month {row.lands_month}",
        (amount,),
        f"smallest raise keeping cash at or above the floor to month {row.target_month}",
    )


def _funds_lines(funds: OptionFunds) -> list[Line]:
    """One option's use-of-funds lines in dollars, their live total and their share of the raise."""
    name = f"Raise {funds.option} use of funds"
    lines = [
        Line(f"funds_{funds.option}_{index}", f"{name}: line {index}", (value,), "as given, or percent·amount")
        for index, value in enumerate(funds.lines, start=1)
    ]
    keys = tuple(line.key for line in lines)
    lines += [
        Line(f"funds_{funds.option}_total", f"{name}: total", (funds.total,), "every line", keys),
        Line(f"funds_{funds.option}_share", f"{name}: share of the raise", (funds.share,), "total/amount"),
    ]
    return lines


def _check_lines(check: RunwayPlanCheck, result: RunwayPlanResult) -> list[Line]:
    """One check: what the founder states, what the calculator gives, the difference and the verdict."""
    subject = "Runway" if check.key == "runway_months" else "Use of funds total"
    name = f"{subject}, {option_name(check.option)}"
    key = f"check_{check.key}_{check.option}"
    how = _CHECK_HOW[check.key]
    if check.key == "runway_months" and check.option > 0:
        if result.inputs.raises[check.option - 1].stated_runway_from == "landing":
            how += ", from when the money lands"
    return [
        Line(f"{key}_stated", f"{name}: stated", (check.stated,), GIVEN),
        Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), how),
        Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
        Line(
            f"{key}_verdict", f"{name}: verdict", (check.verdict,), "within the tolerance is consistent", verdict=True
        ),
    ]


def runway_plan_sheet(result: RunwayPlanResult) -> Sheet:
    """The runway plan's lines: the inputs, the cases, runway, milestones, required raises, funds, checks, flags."""
    lines = _given_lines(result)
    for case, given_case in zip(result.cases, result.inputs.cases, strict=True):
        lines += _case_lines(case, derived=not given_case.phases)
    for row in result.runway:
        lines += _runway_lines(row)
    for milestone in result.milestones:
        lines += _milestone_lines(milestone)
    lines += [_required_line(row) for row in result.required]
    for funds in result.use_of_funds:
        lines += _funds_lines(funds)
    for check in result.checks:
        lines += _check_lines(check, result)
    lines += [Line(f"flag_{flag}", "Be ready to answer", (flag,), _flag_words(flag, result)) for flag in result.flags]
    lines.append(
        Line(
            "verdict",
            "Overall verdict",
            (result.verdict,),
            "mismatch if any check is; consistent if all are; not_checked with none",
            verdict=True,
        )
    )

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
