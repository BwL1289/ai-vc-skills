"""A founder's raise pipeline worked exactly: the allocation left, the term sheets the funnel is expected to give, the
targets needed and, with cash and burn, the start-raising month from the runway plan.

**Allocation.** With round size R, the lead's cheque L (0 when none is planned), firm commitments F and pro rata
amounts P (each a sum), the room after the lead and the firm commitments is R - L - F and the allocation left is
R - L - F - P. Soft commitments S are summed and shown on their own; they are never counted. The flags split an
overfull round by its cause: ``oversubscribed`` when L + F > R (the lead and the firm commitments alone), and
``pro_rata_exceeds_left`` when L + F <= R < L + F + P (they fit, the pro rata does not), so exactly one holds whenever
the allocation left is below zero; ``fully_allocated`` when it is exactly zero.

**Funnel.** Stages k = 1..K in order, n_k investors at stage k today (each counted once, at the furthest stage it has
reached) and r_k the founder's rate from stage k to the next (from K, to a term sheet), as a fraction. The rate to a
term sheet from stage k is q_k = r_k·r_(k+1)···r_K, and the conversion is q_1. The expected investors at a stage are
e_1 = n_1 and e_k = n_k + e_(k-1)·r_(k-1); the expected term sheets are E = e_K·r_K = Σ n_k·q_k, which is n_1·q_1, the
targets times the product of the rates, when only the first stage has investors. For W term sheets wanted:

- targets needed T = ceiling(W / q_1), the first-stage targets that give W from an empty funnel;
- more targets needed M = ceiling((W - E) / q_1), 0 when E >= W: the first-stage targets to add to today's funnel;
- needed at stage k: ceiling(W / q_k).

Each is an expectation from the founder's own rates, every investor moving on independently at its stage's rate, not
a forecast. Every rate is the founder's; a stage with none is refused (``schemas.equity_raise_pipeline``).

**Timing.** Given the founder's cash and burn phases and months to raise, the runway plan scenario works its plan case
with no raise (``runway_plan.compute_runway_plan``): this module reads that row's runway and start-raising month and
the runway plan's flags, and derives neither again.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import get_args

from equity_calculator.assumptions_raise_pipeline import raise_pipeline_assumptions
from equity_calculator.exact import ZERO, fraction, from_percent, quantity
from equity_calculator.runway_plan import compute_runway_plan
from equity_calculator.schemas.equity_common import EquityAssumption, EquityQuantity
from equity_calculator.schemas.equity_raise_pipeline import (
    FunnelResult,
    FunnelStage,
    RaiseAllocation,
    RaisePipelineFlag,
    RaisePipelineInput,
    RaisePipelineResult,
    RaiseRunway,
    RaiseTiming,
    StageRow,
)
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag

__all__ = ["compute_raise_pipeline", "conversion_from", "expected_term_sheets"]

_NO_RAISE = 0
_PLAN = "plan"
_RUNWAY_FLAGS: tuple[RunwayPlanFlag, ...] = ("cash_never_runs_out", "start_raising_date_passed")


def _money(value: Fraction) -> EquityQuantity:
    return quantity("money", value)


def _count(value: Fraction) -> EquityQuantity:
    return quantity("count", value)


def _whole_count(value: Fraction) -> EquityQuantity:
    """A count of investors rounded up to a whole one: half an investor cannot be pitched."""
    return quantity("count", Fraction(max(math.ceil(value), 0)))


def _sum(amounts: list[Decimal]) -> Fraction:
    return sum((fraction(amount) for amount in amounts), ZERO)


@dataclass(frozen=True)
class _Money:
    """The round's exact sums: R, L (0 when none), F, S and P."""

    round_size: Fraction
    lead: Fraction
    firm: Fraction
    soft: Fraction
    pro_rata: Fraction

    @property
    def room(self) -> Fraction:
        return self.round_size - self.lead - self.firm

    @property
    def left(self) -> Fraction:
        return self.room - self.pro_rata


def _sums(inputs: RaisePipelineInput) -> _Money:
    return _Money(
        round_size=fraction(inputs.round_size),
        lead=ZERO if inputs.lead_cheque is None else fraction(inputs.lead_cheque),
        firm=_sum([item.amount for item in inputs.commitments if item.kind == "firm"]),
        soft=_sum([item.amount for item in inputs.commitments if item.kind == "soft"]),
        pro_rata=_sum(list(inputs.pro_rata)),
    )


def _allocation(inputs: RaisePipelineInput, sums: _Money) -> RaiseAllocation:
    return RaiseAllocation(
        round_size=_money(sums.round_size),
        lead_cheque=None if inputs.lead_cheque is None else _money(sums.lead),
        firm_total=_money(sums.firm),
        soft_total=_money(sums.soft),
        pro_rata_total=_money(sums.pro_rata),
        room_after_lead_and_firm=_money(sums.room),
        allocation_left=_money(sums.left),
    )


def _rate(stage: FunnelStage) -> Fraction:
    """A stage's rate as a fraction (the model refuses a stage with none)."""
    return from_percent(stage.rate_percent if stage.rate_percent is not None else Decimal(0))


def conversion_from(stages: tuple[FunnelStage, ...], index: int) -> Fraction:
    """q_k: the product of the rates from stage ``index`` (0-based) to a term sheet."""
    product = Fraction(1)
    for stage in stages[index:]:
        product *= _rate(stage)
    return product


def expected_term_sheets(stages: tuple[FunnelStage, ...]) -> Fraction:
    """E = Σ n_k·q_k: the term sheets today's funnel is expected to give on the founder's rates."""
    return sum((stage.investors * conversion_from(stages, index) for index, stage in enumerate(stages)), ZERO)


def _funnel(inputs: RaisePipelineInput) -> FunnelResult | None:
    """Each stage worked, the conversion, the expected term sheets and the targets needed; none with no stage."""
    stages = inputs.stages
    wanted = inputs.term_sheets_wanted
    if not stages or wanted is None:
        return None

    rows = []
    arriving = ZERO
    for index, stage in enumerate(stages):
        here = stage.investors + arriving
        rate = _rate(stage)
        to_term_sheet = conversion_from(stages, index)
        rows.append(
            StageRow(
                stage=index + 1,
                name=stage.name,
                investors=stage.investors,
                rate=quantity("fraction", rate),
                rate_basis=stage.rate_basis,
                benchmark_source=stage.benchmark_source,
                expected_here=_count(here),
                expected_to_next=_count(here * rate),
                rate_to_term_sheet=quantity("fraction", to_term_sheet),
                needed_here=_whole_count(Fraction(wanted) / to_term_sheet),
            )
        )
        arriving = here * rate

    conversion = conversion_from(stages, 0)
    expected = expected_term_sheets(stages)
    return FunnelResult(
        stages=tuple(rows),
        conversion=quantity("fraction", conversion),
        expected_term_sheets=_count(expected),
        term_sheets_wanted=wanted,
        targets_needed=_whole_count(Fraction(wanted) / conversion),
        more_targets_needed=_whole_count((wanted - expected) / conversion),
    )


def _timing(runway: RaiseRunway | None) -> tuple[RaiseTiming | None, tuple[EquityAssumption, ...]]:
    """The runway plan's own row for the plan with no raise, its flags and its assumptions; none with no cash and burn
    given."""
    if runway is None:
        return None, ()

    plan = runway.runway_plan_input()
    result = compute_runway_plan(plan)
    row = next(item for item in result.runway if item.case == _PLAN and item.option == _NO_RAISE)
    timing = RaiseTiming(
        runway_months=row.runway_months,
        months_to_raise=plan.months_to_raise or 0,
        start_raising_by=row.start_raising_by,
        runway_flags=result.flags,
    )
    return timing, result.assumptions


def _flags(
    inputs: RaisePipelineInput, sums: _Money, funnel: FunnelResult | None, timing: RaiseTiming | None
) -> tuple[RaisePipelineFlag, ...]:
    """The flags that hold, in the order ``RaisePipelineFlag`` lists them."""
    over = sums.lead + sums.firm > sums.round_size
    runway_flags = () if timing is None else timing.runway_flags
    holds: dict[RaisePipelineFlag, bool] = {
        "no_lead_cheque_given": inputs.lead_cheque is None,
        "no_pro_rata_given": not inputs.pro_rata,
        "soft_commitments_not_counted": any(item.kind == "soft" for item in inputs.commitments),
        "oversubscribed": over,
        "pro_rata_exceeds_left": not over and sums.left < ZERO,
        "fully_allocated": sums.left == ZERO,
        "no_funnel_given": funnel is None,
        "benchmark_rates_given": any(stage.rate_basis == "benchmark" for stage in inputs.stages),
        "funnel_short_of_wanted": funnel is not None and funnel.expected_term_sheets.exact < funnel.term_sheets_wanted,
        "no_runway_given": timing is None,
        "cash_never_runs_out": _RUNWAY_FLAGS[0] in runway_flags,
        "start_raising_date_passed": _RUNWAY_FLAGS[1] in runway_flags,
    }
    return tuple(flag for flag in get_args(RaisePipelineFlag) if holds[flag])


def compute_raise_pipeline(inputs: RaisePipelineInput) -> RaisePipelineResult:
    """The allocation, the funnel and the timing, exactly; never a pick of whom to pitch."""
    sums = _sums(inputs)
    funnel = _funnel(inputs)
    timing, runway_assumptions = _timing(inputs.runway)

    return RaisePipelineResult(
        inputs=inputs,
        allocation=_allocation(inputs, sums),
        funnel=funnel,
        timing=timing,
        flags=_flags(inputs, sums, funnel, timing),
        assumptions=raise_pipeline_assumptions(inputs, runway_assumptions),
    )
