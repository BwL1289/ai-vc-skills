"""Pydantic models of a runway plan (``equity_calculator runway_plan``): how long each raise lasts, and what it buys.

A founder's plan is cash on hand and a few phases of monthly gross burn and revenue, each running from its month
until the next phase starts (the last runs on). A downside or a lean case is given as its own phases, or as percents
of the plan's revenue and gross burn. Each raise option is an amount landing after some whole months (0: now); the
no-raise row is always worked too. Milestones are months from today; ``months_to_raise`` is the time the founder
allows to raise the next round after reaching one. The scenario is cash only: valuation, instrument and ownership
stay with ``deal_check``, ``round`` and ``dilution``.

Stated runways are checked: ``stated_runway_months`` for the plan with no raise, and each option's own
``stated_runway_months`` (from today, or from when its money lands). Each is a ``WrittenDecimal``: a stated runway
that is the computed one rounded half away from zero to the places it is typed with is consistent even past the
tolerance (``deal_check``'s rule, ``equity_calculator.rounding``), so it goes in with the places the founder writes.
Each option's use-of-funds lines are checked against its amount as ``deal_check`` checks them, with the same
tolerances and defaults, and keep the tolerance alone.

This module reuses ``equity_deal_check``'s ``FundsLine``, its list cap, its verdict words and its default
tolerances and runway band (which import only ``equity_common`` and two other scenario modules), so no cycle.
``equity_calculator.runway_plan`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    AS_WRITTEN,
    MODEL_CONFIG,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    WrittenDecimal,
)
from equity_calculator.schemas.equity_deal_check import (
    DEFAULT_RUNWAY_BAND_MONTHS,
    DEFAULT_TOLERANCE_PERCENT,
    DEFAULT_TOLERANCE_POINTS,
    MAX_USE_OF_FUNDS_LINES,
    CheckVerdict,
    DealVerdict,
    FundsLine,
)
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "MAX_CASES",
    "MAX_MILESTONES",
    "MAX_MONTH",
    "MAX_MONTHS_TO_RAISE",
    "MAX_PHASES",
    "MAX_RAISES",
    "BurnCase",
    "BurnPhase",
    "CaseName",
    "MilestoneRow",
    "MilestoneVerdict",
    "OptionFunds",
    "OptionRunway",
    "PhaseRow",
    "RaiseOption",
    "RequiredRaiseRow",
    "RunwayCase",
    "RunwayCheckKey",
    "RunwayFrom",
    "RunwayPlanCheck",
    "RunwayPlanFlag",
    "RunwayPlanInput",
    "RunwayPlanResult",
    "RunwayPlanScenario",
]

RunwayPlanScenario = Literal["runway_plan"]

# The cases a plan can carry: the plan itself (always first), a downside and a lean plan (say, for a smaller raise).
CaseName = Literal["plan", "downside", "lean"]

# A milestone is ``covered`` when the cash lasts to its month plus the months to raise, else ``short``.
MilestoneVerdict = Literal["covered", "short"]

# Which stated figure a check is about: a runway claim, or an option's use-of-funds total.
RunwayCheckKey = Literal["runway_months", "use_of_funds_total"]

# Where an option's stated runway counts from: today, or the month its money lands (a deck's "24 months" often counts
# from the close).
RunwayFrom = Literal["today", "landing"]

# Facts and questions about the plan. They never change a verdict; their plain words are in
# ``equity_calculator.layout_runway_plan``. ``consistent_beyond_rounding`` names a stated runway consistent by the
# tolerance alone, not as the computed runway rounded to the places the founder writes it with.
RunwayPlanFlag = Literal[
    "cash_never_runs_out",
    "cash_out_before_raise_lands",
    "milestone_short_on_plan",
    "downside_short_where_plan_covers",
    "covered_without_raise",
    "start_raising_date_passed",
    "no_time_to_raise_given",
    "runway_below_band",
    "consistent_beyond_rounding",
]

# The list caps; the worst case (3 cases x 7 options x 10 milestones, 12 phases) computes at once.
MAX_PHASES = 12
MAX_CASES = 3
MAX_RAISES = 6
MAX_MILESTONES = 10
# A month is at most 50 years out, the same cap as a vesting schedule's.
MAX_MONTH = 600
MAX_MONTHS_TO_RAISE = 60
# A derived case's percents may go up to ten times the plan (a lean or upside case can raise revenue).
_MAX_PERCENT_OF_PLAN = WHOLE_PERCENT * 10
_PLAN: CaseName = "plan"
# The description each stated runway carries in the JSON schema (``AS_WRITTEN``).
_MONTHS_AS_WRITTEN = AS_WRITTEN.format(examples='"18", "18.0"')

# strict: a month is a real int; a bool, a float or a numeric string is refused, never read as one.
Month = Annotated[int, Field(strict=True, ge=1, le=MAX_MONTH)]


class BurnPhase(BaseModel):
    """From ``from_month`` until the next phase starts (the last runs on): monthly gross burn and revenue, flat."""

    model_config = MODEL_CONFIG

    from_month: Month
    gross_burn: BoundedDecimal = Field(gt=0)
    revenue: BoundedDecimal = Field(default=Decimal(0), ge=0)


class BurnCase(BaseModel):
    """One case: its own phases, or (not for the plan) percents of the plan's revenue and gross burn in every phase.

    A percent left out counts as 100. The plan's phases must start at month 1 and strictly increase.
    """

    model_config = MODEL_CONFIG

    name: CaseName
    phases: tuple[BurnPhase, ...] = Field(default=(), max_length=MAX_PHASES)
    revenue_percent_of_plan: BoundedDecimal | None = Field(default=None, ge=0, le=_MAX_PERCENT_OF_PLAN)
    gross_burn_percent_of_plan: BoundedDecimal | None = Field(default=None, gt=0, le=_MAX_PERCENT_OF_PLAN)

    @model_validator(mode="after")
    def _phases_or_percents(self) -> BurnCase:
        """Refuse a case with both phases and a percent, or neither, and phases that do not start at month 1."""
        percents = self.revenue_percent_of_plan is not None or self.gross_burn_percent_of_plan is not None
        if self.phases and percents:
            raise ValueError("give a case its own phases or percents of the plan, not both")
        if not self.phases and not percents:
            raise ValueError("give a case its own phases, or revenue_percent_of_plan or gross_burn_percent_of_plan")
        months = [phase.from_month for phase in self.phases]
        if months and months[0] != 1:
            raise ValueError(f"the first phase must start at month 1 (got month {months[0]})")
        if any(later <= earlier for earlier, later in zip(months, months[1:], strict=False)):
            raise ValueError("each phase must start in a later month than the one before it")

        return self


class RaiseOption(BaseModel):
    """One amount to compare: when it lands (whole months from today), a stated runway, and its use-of-funds lines.

    The whole amount lands at once, at the start of month ``lands_month`` + 1 (0: today).
    """

    model_config = MODEL_CONFIG

    amount: BoundedDecimal = Field(gt=0)
    lands_month: int = Field(default=0, strict=True, ge=0, le=MAX_MONTH)
    # A ``WrittenDecimal``, whose places the rounding test reads (above zero, so no zero's places to keep).
    stated_runway_months: WrittenDecimal | None = Field(default=None, gt=0, description=_MONTHS_AS_WRITTEN)
    stated_runway_from: RunwayFrom = "today"
    use_of_funds: tuple[FundsLine, ...] = Field(default=(), max_length=MAX_USE_OF_FUNDS_LINES)

    @model_validator(mode="after")
    def _one_kind_of_funds_line(self) -> RaiseOption:
        """Refuse use-of-funds lines that mix amounts and percents (``deal_check``'s rule and message), and a basis
        for a stated runway with no stated runway (a claim typed without its figure would go unchecked unseen)."""
        if len({line.amount is None for line in self.use_of_funds}) > 1:
            raise ValueError("give every use_of_funds line as an amount or every one as a percent, not a mix")
        if self.stated_runway_from == "landing" and self.stated_runway_months is None:
            raise ValueError(
                "stated_runway_from needs a stated runway on the same raise: give its stated runway months too, or "
                "leave the basis out"
            )

        return self


class RunwayPlanInput(BaseModel):
    """A founder's plan, its cases, the raises to compare and the milestones; see the module docstring.

    ``cash_floor`` is cash kept in the bank that the plan must never spend. ``stated_runway_months`` is the runway the
    founder states with no raise. The tolerances say how far a stated figure may sit from the computed one
    (``deal_check``'s defaults); a stated runway that is the computed one rounded to the places it is typed with holds
    even past them, so it goes in with the places the founder writes. The runway band raises a question, never an
    error.
    """

    model_config = MODEL_CONFIG

    scenario: RunwayPlanScenario = "runway_plan"
    cash_on_hand: BoundedDecimal = Field(ge=0)
    cash_floor: BoundedDecimal = Field(default=Decimal(0), ge=0)
    cases: tuple[BurnCase, ...] = Field(min_length=1, max_length=MAX_CASES)
    raises: tuple[RaiseOption, ...] = Field(default=(), max_length=MAX_RAISES)
    milestones: tuple[Month, ...] = Field(default=(), max_length=MAX_MILESTONES)
    months_to_raise: int | None = Field(default=None, strict=True, ge=0, le=MAX_MONTHS_TO_RAISE)
    stated_runway_months: WrittenDecimal | None = Field(default=None, gt=0, description=_MONTHS_AS_WRITTEN)
    tolerance_points: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_POINTS, ge=0, lt=WHOLE_PERCENT)
    tolerance_percent: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_PERCENT, ge=0, lt=WHOLE_PERCENT)
    runway_band_months: BoundedDecimal = Field(default=DEFAULT_RUNWAY_BAND_MONTHS, gt=0)

    @model_validator(mode="after")
    def _plan_can_be_worked(self) -> RunwayPlanInput:
        """Refuse a plan that is not first or not given as phases, a case named twice, a floor above the cash, or a
        milestone given twice."""
        first = self.cases[0]
        if first.name != _PLAN:
            raise ValueError(f"the first case must be the plan (got {first.name})")
        if not first.phases:
            raise ValueError("the plan needs its own phases: only a downside or a lean case can be percents of it")
        names = [case.name for case in self.cases]
        if len(set(names)) != len(names):
            raise ValueError("cases: each case name may appear once")
        if self.cash_floor > self.cash_on_hand:
            raise ValueError(
                "cash_floor is above cash_on_hand: the floor is cash kept in the bank, so it cannot exceed the cash"
            )
        if len(set(self.milestones)) != len(self.milestones):
            raise ValueError("milestones: each milestone month may appear once")

        return self


class PhaseRow(BaseModel):
    """One phase as worked: its months (``to_month`` none for the last, which runs on), gross, revenue and net burn."""

    model_config = MODEL_CONFIG

    from_month: int
    to_month: int | None = None
    gross_burn: EquityQuantity
    revenue: EquityQuantity
    net_burn: EquityQuantity


class RunwayCase(BaseModel):
    """One case's phases as worked; a case given as percents shows the figures derived from the plan."""

    model_config = MODEL_CONFIG

    name: CaseName
    phases: tuple[PhaseRow, ...]


class OptionRunway(BaseModel):
    """One option on one case. Option 0 is the no-raise row (amount 0); options 1 on are the raises, in order.

    ``runway_months`` is none when the cash never runs out. ``ran_out_before_landing``: the cash went below the floor
    before the money landed, so the runway is the no-raise runway. ``cash_at_landing`` (money landing after today and
    not run out first) is the cash above the floor just before it lands; ``runway_from_landing`` is the runway less
    the landing month; ``start_raising_by`` is the runway less ``months_to_raise`` (negative: already late).
    """

    model_config = MODEL_CONFIG

    option: int
    case: CaseName
    amount: EquityQuantity
    lands_month: int
    runway_months: EquityQuantity | None = None
    ran_out_before_landing: bool = False
    cash_at_landing: EquityQuantity | None = None
    runway_from_landing: EquityQuantity | None = None
    start_raising_by: EquityQuantity | None = None


class MilestoneRow(BaseModel):
    """One option, case and milestone: the target (month plus months to raise), the slack (runway less the month,
    none when the cash never runs out) and the verdict."""

    model_config = MODEL_CONFIG

    option: int
    case: CaseName
    milestone: int
    month: int
    target_month: int
    slack_months: EquityQuantity | None = None
    verdict: MilestoneVerdict


class RequiredRaiseRow(BaseModel):
    """The smallest raise landing in ``lands_month`` that keeps cash at or above the floor through ``target_month``;
    ``amount`` is none when the cash runs out before that landing, so no amount works."""

    model_config = MODEL_CONFIG

    case: CaseName
    milestone: int
    month: int
    lands_month: int
    target_month: int
    amount: EquityQuantity | None = None


class OptionFunds(BaseModel):
    """One option's use-of-funds lines in dollars, their total and their share of the option's amount."""

    model_config = MODEL_CONFIG

    option: int
    lines: tuple[EquityQuantity, ...]
    total: EquityQuantity
    share: EquityQuantity


class RunwayPlanCheck(BaseModel):
    """One stated figure checked for one option (0: no raise): stated, computed, computed - stated, the verdict.

    ``within_rounding`` says whether a stated runway is the computed one rounded half away from zero to the places it
    is typed with, which makes it consistent even past the tolerance; none for a use-of-funds total (a sum of lines,
    set against the raise or 100%, never a figure typed as one).
    """

    model_config = MODEL_CONFIG

    key: RunwayCheckKey
    option: int
    stated: EquityQuantity
    computed: EquityQuantity
    difference: EquityQuantity
    verdict: CheckVerdict
    within_rounding: bool | None = None


class RunwayPlanResult(BaseModel):
    """The plan worked: each case's phases, the runway per option and case, each milestone, the smallest raise per
    milestone, use of funds, each stated figure's verdict, flags, the verdict and the assumptions."""

    model_config = MODEL_CONFIG

    scenario: RunwayPlanScenario = "runway_plan"
    inputs: RunwayPlanInput
    cases: tuple[RunwayCase, ...]
    runway: tuple[OptionRunway, ...]
    milestones: tuple[MilestoneRow, ...]
    required: tuple[RequiredRaiseRow, ...]
    use_of_funds: tuple[OptionFunds, ...]
    checks: tuple[RunwayPlanCheck, ...]
    flags: tuple[RunwayPlanFlag, ...]
    verdict: DealVerdict
    assumptions: tuple[EquityAssumption, ...]
