"""Pydantic models of a founder's raise pipeline (``equity_calculator raise_pipeline``): how much of the round is still
open, how many term sheets the founder's own funnel is expected to give, and when to start raising.

The founder gives the round size, the lead's cheque when one is planned, each commitment marked soft or firm, the
existing investors' pro rata amounts, and the funnel: the investors at each stage today (each counted once, at the
furthest stage it has reached) and the founder's own rate from each stage to the next (from the last stage, to a term
sheet), with the term sheets wanted. A rate the founder takes from elsewhere is marked ``benchmark`` and needs its
source; a missing rate is refused, never assumed. Investors are never named here: only amounts and counts.

With the founder's cash and burn phases and the months they allow to raise (``runway``), the start-raising month comes
from the runway plan scenario itself: this module reuses ``equity_runway_plan``'s ``BurnPhase``, its caps and its
whole input check (which imports only ``equity_common`` and ``equity_deal_check``), so there is no cycle.
``equity_calculator.raise_pipeline`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
)
from equity_calculator.schemas.equity_runway_plan import (
    MAX_MONTHS_TO_RAISE,
    MAX_PHASES,
    BurnPhase,
    RunwayPlanFlag,
    RunwayPlanInput,
)
from pydantic import AfterValidator, BaseModel, Field, ValidationError, model_validator

__all__ = [
    "MAX_COMMITMENTS",
    "MAX_PRO_RATA",
    "MAX_STAGES",
    "MAX_STAGE_INVESTORS",
    "MAX_TERM_SHEETS",
    "SOURCE_MAX_LENGTH",
    "STAGE_NAME_MAX_LENGTH",
    "Commitment",
    "CommitmentKind",
    "FunnelResult",
    "FunnelStage",
    "RaiseAllocation",
    "RaisePipelineFlag",
    "RaisePipelineInput",
    "RaisePipelineResult",
    "RaisePipelineScenario",
    "RaiseRunway",
    "RaiseTiming",
    "RateBasis",
    "StageRow",
]

RaisePipelineScenario = Literal["raise_pipeline"]

# A commitment the founder holds: ``firm`` (counted against the round) or ``soft`` (shown on its own, never counted).
CommitmentKind = Literal["soft", "firm"]

# Where a stage's rate comes from: ``own`` (the founder's own rate, the default) or ``benchmark`` (a rate the founder
# took from elsewhere, which needs its ``benchmark_source``).
RateBasis = Literal["own", "benchmark"]

# Facts the pipeline turns up. They never change a number and never say whom to pitch; their plain words are in
# ``equity_calculator.layout_raise_pipeline``. ``no_lead_cheque_given``: no lead cheque, so none is counted.
# ``no_pro_rata_given``: no pro rata amount, so none is counted (the founder may have said there is none; the input
# cannot tell). ``soft_commitments_not_counted``: at least one soft commitment, shown on its own. ``oversubscribed``:
# the lead's cheque and the firm commitments alone come to more than the round. ``pro_rata_exceeds_left``: those fit,
# but the pro rata is larger than the room they leave. ``fully_allocated``: nothing is left, exactly.
# ``no_funnel_given``: no stage, so no expected term sheets. ``benchmark_rates_given``: a rate is the founder's
# benchmark, not their own. ``funnel_short_of_wanted``: the funnel today is expected to give fewer term sheets than
# wanted. ``no_runway_given``: no cash and burn, so no start-raising month. ``cash_never_runs_out`` and
# ``start_raising_date_passed``: the runway plan's own flags of the same names, on its plan with no raise.
RaisePipelineFlag = Literal[
    "no_lead_cheque_given",
    "no_pro_rata_given",
    "soft_commitments_not_counted",
    "oversubscribed",
    "pro_rata_exceeds_left",
    "fully_allocated",
    "no_funnel_given",
    "benchmark_rates_given",
    "funnel_short_of_wanted",
    "no_runway_given",
    "cash_never_runs_out",
    "start_raising_date_passed",
]

# The list caps: a few dozen commitments, twenty pro rata rights, eight funnel stages of at most 10,000 investors each,
# and at most 100 term sheets wanted.
MAX_COMMITMENTS = 40
MAX_PRO_RATA = 20
MAX_STAGES = 8
MAX_STAGE_INVESTORS = 10_000
MAX_TERM_SHEETS = 100
# A stage's name is a label of a few words, and a benchmark's source a short citation: letters and digits in any
# script, spaces and a little punctuation, starting with a letter or a digit, so neither can read as a spreadsheet
# formula (=, +, -, @) or carry a control character.
STAGE_NAME_MAX_LENGTH = 40
SOURCE_MAX_LENGTH = 120
_LABEL_PUNCTUATION = frozenset(" .,&/()'-+#:")
_LABEL_CHARACTERS = "letters, digits, spaces and . , & / ( ) ' - + # :"
_VALUE_ERROR_PREFIX = "Value error, "
_TOO_SHORT = "too_short"


def _plain_label(value: str, what: str, example: str) -> str:
    """A label, its outer spaces dropped: refused when empty, starting with anything but a letter or a digit, or holding
    a character other than letters, digits, spaces and a little punctuation."""
    text = value.strip()
    if not text:
        raise ValueError(f"{what} is empty: give it in a few words ({example})")
    if not text[0].isalnum():
        raise ValueError(f"{what} starts with a letter or a digit, got {text[0]!r}")
    for character in text:
        if not (character.isalnum() or character in _LABEL_PUNCTUATION):
            raise ValueError(f"{what} holds only {_LABEL_CHARACTERS}, got {character!r}")

    return text


def _stage_name(value: str) -> str:
    return _plain_label(value, "a stage's name", "First meeting")


def _source(value: str) -> str:
    return _plain_label(value, "a benchmark's source", "a survey's title and year")


StageName = Annotated[
    str, Field(strict=True, min_length=1, max_length=STAGE_NAME_MAX_LENGTH), AfterValidator(_stage_name)
]
SourceText = Annotated[str, Field(strict=True, min_length=1, max_length=SOURCE_MAX_LENGTH), AfterValidator(_source)]
PositiveAmount = Annotated[BoundedDecimal, Field(gt=0)]


class Commitment(BaseModel):
    """One commitment the founder holds (not the lead's cheque): its amount and whether it is ``soft`` or ``firm``, as
    the founder marks it. A commitment with no kind is refused: none is assumed firm."""

    model_config = MODEL_CONFIG

    amount: PositiveAmount
    kind: CommitmentKind | None = None

    @model_validator(mode="after")
    def _marked(self) -> Commitment:
        if self.kind is None:
            raise ValueError(
                "commitment_kind_missing: mark each commitment soft or firm, as the founder does; none is assumed "
                "firm"
            )
        return self


class FunnelStage(BaseModel):
    """One stage of the founder's funnel, in order: the investors at it today (each counted once, at the furthest stage
    it has reached) and the founder's rate from it to the next stage (from the last, to a term sheet), in percent.

    ``rate_basis`` is ``own`` (the founder's own rate) unless the founder took the rate from elsewhere: then it is
    ``benchmark`` and ``benchmark_source`` says where from, in the founder's words. A missing rate is refused.
    """

    model_config = MODEL_CONFIG

    name: StageName
    investors: int = Field(strict=True, ge=0, le=MAX_STAGE_INVESTORS)
    rate_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)
    rate_basis: RateBasis = "own"
    benchmark_source: SourceText | None = None

    @model_validator(mode="after")
    def _a_rate_with_its_basis(self) -> FunnelStage:
        """Refuse a stage with no rate, a benchmark with no source, or a source on the founder's own rate."""
        if self.rate_percent is None:
            raise ValueError(
                f"stage_rate_missing: {self.name} has no rate: ask the founder for their own rate from this stage "
                "to the next (from the last stage, to a term sheet), in percent; no rate is assumed"
            )
        if self.rate_basis == "benchmark" and self.benchmark_source is None:
            raise ValueError(
                f"benchmark_rate_without_source: {self.name}'s rate is a benchmark, so give benchmark_source, the "
                "founder's source for it; with no source, use the founder's own rate"
            )
        if self.rate_basis == "own" and self.benchmark_source is not None:
            raise ValueError(
                f"{self.name}: benchmark_source goes with rate_basis benchmark; the founder's own rate takes none"
            )

        return self


class RaiseRunway(BaseModel):
    """The founder's cash and burn, worked by the runway plan scenario for the start-raising month.

    ``cash_on_hand``, ``cash_floor`` and ``phases`` are the runway plan's own fields for its plan case (its first phase
    from month 1); ``months_to_raise`` is the time the founder allows to raise, and is needed here: the start-raising
    month is the runway with no raise less it. A ``cash_floor`` left out is ``None`` and worked as none, so "not given"
    survives a result's echoed ``inputs`` read back from JSON (a stated 0 stays 0).
    """

    model_config = MODEL_CONFIG

    cash_on_hand: BoundedDecimal = Field(ge=0)
    cash_floor: BoundedDecimal | None = Field(default=None, ge=0)
    phases: tuple[BurnPhase, ...] = Field(min_length=1, max_length=MAX_PHASES)
    months_to_raise: int | None = Field(default=None, strict=True, ge=0, le=MAX_MONTHS_TO_RAISE)

    @model_validator(mode="after")
    def _a_plan_the_runway_plan_takes(self) -> RaiseRunway:
        """Refuse no months to raise, and any plan the runway plan scenario would refuse, with its own words."""
        if self.months_to_raise is None:
            raise ValueError(
                "no_months_to_raise_given: the start-raising month is how long the cash lasts with no raise less the "
                "months the founder allows to raise, so give months_to_raise, from the founder"
            )
        try:
            self.runway_plan_input()
        except ValidationError as error:
            # A case whose phases failed also leaves the cases list too short: say the cause only.
            failures = [item for item in error.errors() if item["type"] != _TOO_SHORT] or error.errors()
            reasons = "; ".join(str(item["msg"]).removeprefix(_VALUE_ERROR_PREFIX) for item in failures)
            raise ValueError(reasons) from None

        return self

    def runway_plan_input(self) -> RunwayPlanInput:
        """The runway plan's input for this cash and burn: its plan case alone, no raise, no milestone."""
        return RunwayPlanInput.model_validate(
            {
                "cash_on_hand": self.cash_on_hand,
                "cash_floor": Decimal(0) if self.cash_floor is None else self.cash_floor,
                "cases": [{"name": "plan", "phases": self.phases}],
                "months_to_raise": self.months_to_raise,
            }
        )


class RaisePipelineInput(BaseModel):
    """A founder's round, commitments, funnel and (optionally) cash and burn; see the module docstring.

    ``round_size`` (R), ``lead_cheque`` (L, when a lead is planned), each commitment's ``amount`` and each of
    ``pro_rata`` are dollars. ``stages`` and ``term_sheets_wanted`` go together: both, or neither.
    """

    model_config = MODEL_CONFIG

    scenario: RaisePipelineScenario = "raise_pipeline"
    round_size: BoundedDecimal = Field(gt=0)
    lead_cheque: BoundedDecimal | None = Field(default=None, gt=0)
    commitments: tuple[Commitment, ...] = Field(default=(), max_length=MAX_COMMITMENTS)
    pro_rata: tuple[PositiveAmount, ...] = Field(default=(), max_length=MAX_PRO_RATA)
    stages: tuple[FunnelStage, ...] = Field(default=(), max_length=MAX_STAGES)
    term_sheets_wanted: int | None = Field(default=None, strict=True, ge=1, le=MAX_TERM_SHEETS)
    runway: RaiseRunway | None = None

    @model_validator(mode="after")
    def _a_funnel_with_its_goal(self) -> RaisePipelineInput:
        """Refuse term sheets wanted with no funnel, or a funnel with no term sheets wanted."""
        if self.term_sheets_wanted is not None and not self.stages:
            raise ValueError(
                "no_funnel_given: term_sheets_wanted needs the founder's funnel: each stage's investors today and the "
                "founder's own rate from it to the next"
            )
        if self.stages and self.term_sheets_wanted is None:
            raise ValueError(
                "no_term_sheet_count_given: give term_sheets_wanted, the founder's own count, with the funnel"
            )
        names = [stage.name.casefold() for stage in self.stages]
        if len(set(names)) != len(names):
            raise ValueError("stages: each stage's name may appear once")

        return self


class RaiseAllocation(BaseModel):
    """The round's money: what is counted against it and what is left.

    ``room_after_lead_and_firm`` is R - L - the firm commitments; ``allocation_left`` is that less the pro rata (below
    zero: more is counted than the round holds). ``soft_total`` is shown on its own and never counted.
    """

    model_config = MODEL_CONFIG

    round_size: EquityQuantity
    lead_cheque: EquityQuantity | None
    firm_total: EquityQuantity
    soft_total: EquityQuantity
    pro_rata_total: EquityQuantity
    room_after_lead_and_firm: EquityQuantity
    allocation_left: EquityQuantity


class StageRow(BaseModel):
    """One stage worked: its rate as a fraction, the expected investors at it (today's plus those expected to arrive
    from the stage before), the expected number moving on, the rate from it to a term sheet (the product of its rate
    and every later one) and the investors needed at it for the term sheets wanted, rounded up to whole investors."""

    model_config = MODEL_CONFIG

    stage: int
    name: str
    investors: int
    rate: EquityQuantity
    rate_basis: RateBasis
    benchmark_source: str | None
    expected_here: EquityQuantity
    expected_to_next: EquityQuantity
    rate_to_term_sheet: EquityQuantity
    needed_here: EquityQuantity


class FunnelResult(BaseModel):
    """The funnel worked: each stage, the product of every rate, the term sheets expected from today's funnel (an
    expectation from the founder's own rates, not a forecast), and the targets needed.

    ``targets_needed`` is ceiling(W / the product): the first-stage targets that give W term sheets from an empty
    funnel. ``more_targets_needed`` is ceiling((W - expected) / the product), 0 when today's funnel is expected to give
    W or more: the first-stage targets to add to today's funnel.
    """

    model_config = MODEL_CONFIG

    stages: tuple[StageRow, ...]
    conversion: EquityQuantity
    expected_term_sheets: EquityQuantity
    term_sheets_wanted: int
    targets_needed: EquityQuantity
    more_targets_needed: EquityQuantity


class RaiseTiming(BaseModel):
    """The runway plan scenario's own figures for the founder's plan with no raise: the runway (none when the cash
    never runs out), the months to raise, the start-raising month (the runway less them; none when the cash never runs
    out) and the runway plan's flags."""

    model_config = MODEL_CONFIG

    runway_months: EquityQuantity | None
    months_to_raise: int
    start_raising_by: EquityQuantity | None
    runway_flags: tuple[RunwayPlanFlag, ...]


class RaisePipelineResult(BaseModel):
    """The pipeline worked: the allocation, the funnel (none with no stages), the timing (none with no runway), flags
    and assumptions."""

    model_config = MODEL_CONFIG

    scenario: RaisePipelineScenario = "raise_pipeline"
    inputs: RaisePipelineInput
    allocation: RaiseAllocation
    funnel: FunnelResult | None
    timing: RaiseTiming | None
    flags: tuple[RaisePipelineFlag, ...]
    assumptions: tuple[EquityAssumption, ...]
