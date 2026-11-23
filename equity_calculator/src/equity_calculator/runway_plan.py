"""A founder's runway plan worked exactly: how long each raise lasts on each case, and which milestones it reaches.

Time t is elapsed months from today. A phase starting in month a covers t in [a - 1, a' - 1), a' the next phase's
month; the last phase runs on. With net burn n = gross - revenue in each phase, the cumulative net burn S(t) is
continuous and piecewise linear. The cash above the floor is A = cash_on_hand - cash_floor; a raise of I landing in
month L adds I at time L (with L = 0, from the start), so cash(t) = A - S(t) before L and A + I - S(t) from L on.

- **Runway** R = inf{t >= 0 : cash(t) < 0}, worked segment by segment (breakpoints at the phase starts and at L):
  from a level c >= 0 at the start of a segment with rate n > 0, the cash runs out at c/n later, if that falls before
  the segment ends. Cash that touches zero and then holds or rises does not end the runway, and cash exactly at zero
  as the money lands survives. On the open last segment with n <= 0 the cash never runs out (R none).
- **Milestone**: with T = month + months_to_raise (the month alone when that is not given), covered when R is none
  or R >= T; the slack is R - month.
- **Required raise** to land at L and last to T: I* = max(0, max S(t) - A over t in [L, T]), the maximum of a
  piecewise-linear function being at a breakpoint or an end; none when S(t) > A for some t in [0, min(L, T)] (the
  cash runs out first). An option landing at L covers T exactly when its amount is at least I*.
- A downside or lean case given as percents scales every plan phase's revenue by R/100 and gross burn by G/100.

Each stated runway becomes one check (relative tolerance, the edge included), each option's use-of-funds lines one
more (``equity_calculator.funds``); flags name what to be ready to answer and never change a verdict.
"""

from __future__ import annotations

import math
from collections.abc import Iterator
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from equity_calculator.assumptions_runway_plan import runway_plan_assumptions
from equity_calculator.exact import ZERO, fraction, from_percent, quantity, round_to_places
from equity_calculator.funds import work_use_of_funds
from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import DealVerdict
from equity_calculator.schemas.equity_runway_plan import (
    BurnCase,
    CaseName,
    MilestoneRow,
    OptionFunds,
    OptionRunway,
    PhaseRow,
    RaiseOption,
    RequiredRaiseRow,
    RunwayCase,
    RunwayCheckKey,
    RunwayPlanCheck,
    RunwayPlanFlag,
    RunwayPlanInput,
    RunwayPlanResult,
)

__all__ = ["Phase", "compute_runway_plan", "cumulative_burn", "required_raise", "runway"]

_NO_RAISE = 0
_CENTS = 100
_MONEY_PLACES = 2
_PLAN: CaseName = "plan"
_DOWNSIDE: CaseName = "downside"


@dataclass(frozen=True)
class Phase:
    """One phase as worked: its first month, its gross burn and revenue a month (exact)."""

    from_month: int
    gross: Fraction
    revenue: Fraction

    @property
    def net(self) -> Fraction:
        return self.gross - self.revenue


@dataclass(frozen=True)
class _Segment:
    """A stretch of elapsed time [start, end) (end none: runs on) at one net burn a month."""

    start: Fraction
    end: Fraction | None
    rate: Fraction


def _segments(phases: tuple[Phase, ...]) -> Iterator[_Segment]:
    """Each phase as elapsed time: month a starts at a - 1 and runs until the next phase's start."""
    for index, phase in enumerate(phases):
        end = None if index + 1 == len(phases) else Fraction(phases[index + 1].from_month - 1)
        yield _Segment(Fraction(phase.from_month - 1), end, phase.net)


def cumulative_burn(phases: tuple[Phase, ...], elapsed: Fraction) -> Fraction:
    """S(t): the net burn from today through elapsed time ``elapsed``."""
    total = ZERO
    for segment in _segments(phases):
        if elapsed <= segment.start:
            break
        end = elapsed if segment.end is None else min(elapsed, segment.end)
        total += segment.rate * (end - segment.start)

    return total


def runway(
    phases: tuple[Phase, ...], available: Fraction, amount: Fraction, lands: int
) -> tuple[Fraction | None, bool]:
    """(R, ran out before landing): when cash above the floor first goes below zero, ``amount`` landing at ``lands``.

    R is none when the cash never runs out. Cash exactly at zero as the money lands survives.
    """
    landing = Fraction(lands)
    landed = lands == 0
    level = available + (amount if landed else ZERO)
    for segment in _segments(phases):
        splits_here = not landed and segment.start <= landing and (segment.end is None or landing < segment.end)
        ends = [landing, segment.end] if splits_here else [segment.end]
        start = segment.start
        for end in ends:
            if segment.rate > ZERO:
                out = start + level / segment.rate
                if end is None or out < end:
                    return out, not landed
            if end is None:
                return None, False
            level -= segment.rate * (end - start)
            start = end
            if not landed and end == landing:
                level += amount
                landed = True

    return None, False


def _breakpoints(phases: tuple[Phase, ...], low: Fraction, high: Fraction) -> set[Fraction]:
    """``low``, ``high`` and every phase start between them: where S's maximum on [low, high] can fall."""
    starts = {Fraction(phase.from_month - 1) for phase in phases}
    return {low, high} | {start for start in starts if low <= start <= high}


def required_raise(phases: tuple[Phase, ...], available: Fraction, lands: int, target: int) -> Fraction | None:
    """The smallest raise landing at ``lands`` that keeps cash above the floor through ``target``; none when the cash
    runs out before the money lands (or before the target, when the target is not after the landing)."""
    landing, until = Fraction(lands), Fraction(target)
    before = _breakpoints(phases, ZERO, min(landing, until))
    if any(cumulative_burn(phases, point) > available for point in before):
        return None
    if until <= landing:
        return ZERO

    peak = max(cumulative_burn(phases, point) for point in _breakpoints(phases, landing, until))
    return max(peak - available, ZERO)


def _case_phases(case: BurnCase, plan: tuple[Phase, ...]) -> tuple[Phase, ...]:
    """A case's phases: its own, or the plan's with revenue and gross burn scaled by its percents (100 if left out)."""
    if case.phases:
        return tuple(Phase(p.from_month, fraction(p.gross_burn), fraction(p.revenue)) for p in case.phases)

    revenue = _share(case.revenue_percent_of_plan)
    gross = _share(case.gross_burn_percent_of_plan)
    return tuple(Phase(p.from_month, p.gross * gross, p.revenue * revenue) for p in plan)


def _share(percent: Decimal | None) -> Fraction:
    return Fraction(1) if percent is None else from_percent(percent)


def _case_row(name: CaseName, phases: tuple[Phase, ...]) -> RunwayCase:
    rows = []
    for index, phase in enumerate(phases):
        to_month = phases[index + 1].from_month - 1 if index + 1 < len(phases) else None
        rows.append(
            PhaseRow(
                from_month=phase.from_month,
                to_month=to_month,
                gross_burn=quantity("money", phase.gross),
                revenue=quantity("money", phase.revenue),
                net_burn=quantity("money", phase.net),
            )
        )
    return RunwayCase(name=name, phases=tuple(rows))


def _covering(amount: Fraction | None) -> EquityQuantity | None:
    """A required raise, exact, with its display rounded up to the next cent (never half-even), so raising the amount
    shown always reaches the milestone."""
    if amount is None:
        return None
    cents = math.ceil(amount * _CENTS)
    return EquityQuantity(unit="money", exact=amount, rounded=round_to_places(Fraction(cents, _CENTS), _MONEY_PLACES))


def _optional(unit: EquityUnit, value: Fraction | None) -> EquityQuantity | None:
    return None if value is None else quantity(unit, value)


@dataclass(frozen=True)
class _Worked:
    """The runway, milestone and required-raise rows of every case."""

    runway: tuple[OptionRunway, ...]
    milestones: tuple[MilestoneRow, ...]
    required: tuple[RequiredRaiseRow, ...]


def _options(inputs: RunwayPlanInput) -> tuple[tuple[Fraction, int], ...]:
    """(amount, landing month) per option: the no-raise row first, then each raise in order."""
    return ((ZERO, 0), *((fraction(option.amount), option.lands_month) for option in inputs.raises))


def _target(inputs: RunwayPlanInput, month: int) -> int:
    return month + (inputs.months_to_raise or 0)


def _option_rows(
    inputs: RunwayPlanInput, name: CaseName, phases: tuple[Phase, ...], available: Fraction
) -> tuple[list[OptionRunway], list[MilestoneRow]]:
    """The runway row and the milestone rows of every option on one case."""
    runways, milestones = [], []
    for option, (amount, lands) in enumerate(_options(inputs)):
        months, before = runway(phases, available, amount, lands)
        late = lands > 0 and not before
        months_to_raise = inputs.months_to_raise
        runways.append(
            OptionRunway(
                option=option,
                case=name,
                amount=quantity("money", amount),
                lands_month=lands,
                runway_months=_optional("months", months),
                ran_out_before_landing=before,
                cash_at_landing=quantity("money", available - cumulative_burn(phases, Fraction(lands)))
                if late
                else None,
                runway_from_landing=_optional("months", None if months is None or not late else months - lands),
                start_raising_by=_optional(
                    "months", None if months is None or months_to_raise is None else months - months_to_raise
                ),
            )
        )
        for number, month in enumerate(inputs.milestones, start=1):
            target = _target(inputs, month)
            milestones.append(
                MilestoneRow(
                    option=option,
                    case=name,
                    milestone=number,
                    month=month,
                    target_month=target,
                    slack_months=_optional("months", None if months is None else months - month),
                    verdict="covered" if months is None or months >= target else "short",
                )
            )
    return runways, milestones


def _required_rows(
    inputs: RunwayPlanInput, name: CaseName, phases: tuple[Phase, ...], available: Fraction
) -> list[RequiredRaiseRow]:
    """The smallest raise per milestone and distinct landing month (0 always included) on one case."""
    landings = sorted({0, *(option.lands_month for option in inputs.raises)})
    rows = []
    for number, month in enumerate(inputs.milestones, start=1):
        target = _target(inputs, month)
        for lands in landings:
            amount = required_raise(phases, available, lands, target)
            rows.append(
                RequiredRaiseRow(
                    case=name,
                    milestone=number,
                    month=month,
                    lands_month=lands,
                    target_month=target,
                    amount=_covering(amount),
                )
            )
    return rows


def _work(inputs: RunwayPlanInput, cases: tuple[tuple[CaseName, tuple[Phase, ...]], ...]) -> _Worked:
    available = fraction(inputs.cash_on_hand) - fraction(inputs.cash_floor)
    runways: list[OptionRunway] = []
    milestones: list[MilestoneRow] = []
    required: list[RequiredRaiseRow] = []
    for name, phases in cases:
        case_runways, case_milestones = _option_rows(inputs, name, phases, available)
        runways += case_runways
        milestones += case_milestones
        required += _required_rows(inputs, name, phases, available)

    return _Worked(tuple(runways), tuple(milestones), tuple(required))


def _check(
    key: RunwayCheckKey, option: int, unit: EquityUnit, stated: Fraction, computed: Fraction, tolerance: Fraction
) -> RunwayPlanCheck:
    """One check: within ``tolerance`` of the computed figure (the edge included) is consistent."""
    difference = computed - stated

    return RunwayPlanCheck(
        key=key,
        option=option,
        stated=quantity(unit, stated),
        computed=quantity(unit, computed),
        difference=quantity(unit, difference),
        verdict="consistent" if abs(difference) <= tolerance else "mismatch",
    )


def _plan_runway(worked: _Worked, option: int) -> OptionRunway:
    return next(row for row in worked.runway if row.case == _PLAN and row.option == option)


def _runway_check(
    inputs: RunwayPlanInput, worked: _Worked, option: int, stated: Decimal, from_landing: bool
) -> RunwayPlanCheck | None:
    """A stated runway against the plan case's runway for ``option`` (less the landing month when it counts from
    there); none when the cash never runs out, or when it counts from landing and the cash runs out before the money
    lands (there is no runway from landing; ``cash_out_before_raise_lands`` says why)."""
    row = _plan_runway(worked, option)
    if row.runway_months is None or (from_landing and row.ran_out_before_landing):
        return None

    computed = row.runway_months.exact - (row.lands_month if from_landing else 0)
    relative = from_percent(inputs.tolerance_percent)
    return _check("runway_months", option, "months", fraction(stated), computed, relative * abs(computed))


def _checks_and_funds(
    inputs: RunwayPlanInput, worked: _Worked
) -> tuple[tuple[RunwayPlanCheck, ...], tuple[OptionFunds, ...]]:
    """Every stated runway, and each option's use-of-funds total, checked; the options' use-of-funds lines."""
    checks: list[RunwayPlanCheck | None] = []
    funds: list[OptionFunds] = []
    if inputs.stated_runway_months is not None:
        checks.append(_runway_check(inputs, worked, _NO_RAISE, inputs.stated_runway_months, False))
    for option, given in enumerate(inputs.raises, start=1):
        checks += _option_checks(inputs, worked, option, given, funds)

    return tuple(check for check in checks if check is not None), tuple(funds)


def _option_checks(
    inputs: RunwayPlanInput, worked: _Worked, option: int, given: RaiseOption, funds: list[OptionFunds]
) -> list[RunwayPlanCheck | None]:
    """One option's stated runway and use-of-funds checks; its worked lines go into ``funds``."""
    checks: list[RunwayPlanCheck | None] = []
    if given.stated_runway_months is not None:
        from_landing = given.stated_runway_from == "landing"
        checks.append(_runway_check(inputs, worked, option, given.stated_runway_months, from_landing))
    lines = work_use_of_funds(
        given.use_of_funds, fraction(given.amount), inputs.tolerance_points, inputs.tolerance_percent
    )
    if lines is not None:
        funds.append(OptionFunds(option=option, lines=lines.lines, total=lines.total, share=lines.share))
        checks.append(_check("use_of_funds_total", option, lines.unit, lines.stated, lines.computed, lines.tolerance))
    return checks


def _milestone_flags(inputs: RunwayPlanInput, worked: _Worked) -> list[RunwayPlanFlag]:
    """The milestone flags: a raise short on the plan, a downside short where the plan covers, covered with no raise."""
    flags: list[RunwayPlanFlag] = []
    verdicts = {(row.option, row.case, row.milestone): row.verdict for row in worked.milestones}
    if any(row.case == _PLAN and row.option != _NO_RAISE and row.verdict == "short" for row in worked.milestones):
        flags.append("milestone_short_on_plan")
    if any(
        row.case == _DOWNSIDE and row.verdict == "short" and verdicts[(row.option, _PLAN, row.milestone)] == "covered"
        for row in worked.milestones
    ):
        flags.append("downside_short_where_plan_covers")
    if any(row.option == _NO_RAISE and row.verdict == "covered" for row in worked.milestones):
        flags.append("covered_without_raise")
    return flags


def _flags(inputs: RunwayPlanInput, worked: _Worked) -> tuple[RunwayPlanFlag, ...]:
    """Every flag that holds, in ``RunwayPlanFlag``'s order."""
    flags: list[RunwayPlanFlag] = []
    if any(row.runway_months is None for row in worked.runway):
        flags.append("cash_never_runs_out")
    if any(row.ran_out_before_landing for row in worked.runway):
        flags.append("cash_out_before_raise_lands")
    flags += _milestone_flags(inputs, worked)
    start = _plan_runway(worked, _NO_RAISE).start_raising_by
    if start is not None and start.exact <= ZERO:
        flags.append("start_raising_date_passed")
    if inputs.milestones and inputs.months_to_raise is None:
        flags.append("no_time_to_raise_given")
    band = fraction(inputs.runway_band_months)
    plan_raises = [row for row in worked.runway if row.case == _PLAN and row.option != _NO_RAISE]
    if any(row.runway_months is not None and row.runway_months.exact < band for row in plan_raises):
        flags.append("runway_below_band")

    return tuple(flags)


def _verdict(checks: tuple[RunwayPlanCheck, ...]) -> DealVerdict:
    """``mismatch`` if any check is, ``consistent`` if all are, ``not_checked`` with none (``deal_check``'s rule)."""
    if not checks:
        return "not_checked"

    return "mismatch" if any(check.verdict == "mismatch" for check in checks) else "consistent"


def compute_runway_plan(inputs: RunwayPlanInput) -> RunwayPlanResult:
    """The plan worked exactly: each case's phases, runway per option and case, milestones, required raises, checks."""
    plan_case, *others = inputs.cases
    plan = _case_phases(plan_case, ())
    cases: tuple[tuple[CaseName, tuple[Phase, ...]], ...] = (
        (plan_case.name, plan),
        *((case.name, _case_phases(case, plan)) for case in others),
    )
    worked = _work(inputs, cases)
    checks, funds = _checks_and_funds(inputs, worked)

    return RunwayPlanResult(
        inputs=inputs,
        cases=tuple(_case_row(name, phases) for name, phases in cases),
        runway=worked.runway,
        milestones=worked.milestones,
        required=worked.required,
        use_of_funds=funds,
        checks=checks,
        flags=_flags(inputs, worked),
        verdict=_verdict(checks),
        assumptions=runway_plan_assumptions(inputs, bool(checks)),
    )
