"""A founder's raise pipeline (the ``Raise pipeline`` sheet): the allocation left, the funnel, the start-raising month.

One value column. The round and every amount counted against it come first, each commitment marked firm or soft (soft
never counted), with live totals; then each funnel stage as given and as worked, the expected term sheets and the
targets needed; then, with cash and burn, the cash, the floor and each phase as given and the runway plan's runway
and start-raising month; then the flags in plain words. Values only: no line carries a live formula beyond the
``=SUM`` totals (the room and the allocation left say so in their how text), and no line says whom to pitch.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_raise_pipeline import (
    FunnelResult,
    RaisePipelineFlag,
    RaisePipelineResult,
    RaiseRunway,
    RaiseTiming,
    StageRow,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given

_TITLE = "Raise pipeline"
_HEADING = (
    "The founder's round: what is left to allocate, the term sheets the funnel is expected to give on the founder's "
    "own rates, and when to start raising"
)
_COLUMNS = ("This pipeline",)
_NEVER = "none: the cash never runs out"
# The room and the allocation left are values, as every line but a total is outside the investor sheet: in the
# workbook, the totals above them re-total when a part is edited, and these two do not.
_AS_RUN = "the value when run, not a live formula"
_REVENUE = "revenue"
_REVENUE_NOT_GIVEN = "not given: read as none"
_FLOOR = "cash_floor"
_FLOOR_NOT_GIVEN = "not given: read as none"


def _floor_how(runway: RaiseRunway) -> str:
    return GIVEN if _FLOOR in runway.model_fields_set else _FLOOR_NOT_GIVEN


def _allocation_lines(result: RaisePipelineResult) -> list[Line]:
    """The round, the lead, each commitment and pro rata amount, their totals, the room and the allocation left."""
    inputs, allocation = result.inputs, result.allocation
    lines = [Line("round_size", "Round size (R)", (allocation.round_size,), GIVEN)]
    if allocation.lead_cheque is not None:
        lines.append(Line("lead_cheque", "Lead's cheque (L)", (allocation.lead_cheque,), GIVEN))
    firm, soft = [], []
    for number, commitment in enumerate(inputs.commitments, start=1):
        key = f"commitment_{number}"
        counted = commitment.kind == "firm"
        how = "given; firm, counted" if counted else "given; soft, never counted"
        lines.append(Line(key, f"Commitment {number} ({commitment.kind})", (given("money", commitment.amount),), how))
        (firm if counted else soft).append(key)
    pro_rata = []
    for number, amount in enumerate(inputs.pro_rata, start=1):
        key = f"pro_rata_{number}"
        lines.append(Line(key, f"Pro rata {number}", (given("money", amount),), GIVEN))
        pro_rata.append(key)
    lines += [
        Line("firm_total", "Firm commitments (F)", (allocation.firm_total,), "the firm commitments", tuple(firm)),
        Line(
            "soft_total",
            "Soft commitments, never counted (S)",
            (allocation.soft_total,),
            "the soft commitments, shown on their own",
            tuple(soft),
        ),
        Line("pro_rata_total", "Pro rata (P)", (allocation.pro_rata_total,), "every pro rata amount", tuple(pro_rata)),
        Line(
            "room_after_lead_and_firm",
            "Room after the lead and the firm commitments",
            (allocation.room_after_lead_and_firm,),
            f"R - L - F; {_AS_RUN}",
        ),
        Line(
            "allocation_left",
            "Allocation left",
            (allocation.allocation_left,),
            f"R - L - F - P; below 0, more is counted than the round holds; {_AS_RUN}",
        ),
    ]
    return lines


def _rate_how(row: StageRow) -> str:
    if row.rate_basis == "benchmark":
        return f"a benchmark the founder gave, from: {row.benchmark_source}"
    return "the founder's own rate"


def _stage_lines(row: StageRow, wanted: int, last: bool) -> list[Line]:
    """One stage as given and as worked."""
    name = f"Stage {row.stage}, {row.name}"
    key = f"stage_{row.stage}"
    rate_label = "rate to a term sheet" if last else "rate to the next stage"
    arrives = "today's" if row.stage == 1 else f"today's + those expected to move on from stage {row.stage - 1}"
    return [
        Line(f"{key}_investors", f"{name}: investors today", (given("count", Decimal(row.investors)),), GIVEN),
        Line(f"{key}_rate", f"{name}: {rate_label}", (row.rate,), _rate_how(row)),
        Line(f"{key}_expected_here", f"{name}: expected here", (row.expected_here,), arrives),
        Line(
            f"{key}_expected_to_next", f"{name}: expected to move on", (row.expected_to_next,), "expected here × rate"
        ),
        Line(
            f"{key}_rate_to_term_sheet",
            f"{name}: rate to a term sheet from here",
            (row.rate_to_term_sheet,),
            "the product of the rates from this stage on",
        ),
        Line(
            f"{key}_needed_here",
            f"{name}: needed here for {wanted} term sheets",
            (row.needed_here,),
            "ceiling(W / the rate to a term sheet from here)",
        ),
    ]


def _funnel_lines(funnel: FunnelResult) -> list[Line]:
    """Each stage, then the conversion, the expected term sheets and the targets needed."""
    wanted = funnel.term_sheets_wanted
    lines = []
    for index, row in enumerate(funnel.stages):
        lines += _stage_lines(row, wanted, last=index + 1 == len(funnel.stages))
    lines += [
        Line(
            "conversion", "Conversion, first stage to a term sheet", (funnel.conversion,), "the product of every rate"
        ),
        Line(
            "expected_term_sheets",
            "Expected term sheets from today's funnel (E)",
            (funnel.expected_term_sheets,),
            "the sum of each stage's investors × its rate to a term sheet; an expectation from the founder's rates, "
            "not a forecast",
        ),
        Line("term_sheets_wanted", "Term sheets wanted (W)", (given("count", Decimal(wanted)),), GIVEN),
        Line(
            "targets_needed",
            "First-stage targets needed, from an empty funnel",
            (funnel.targets_needed,),
            "ceiling(W / the conversion)",
        ),
        Line(
            "more_targets_needed",
            "More first-stage targets needed beyond today's funnel",
            (funnel.more_targets_needed,),
            "ceiling((W - E) / the conversion); 0 when E >= W",
        ),
    ]
    return lines


def _phase_lines(runway: RaiseRunway) -> list[Line]:
    """Each phase of the burn the runway is worked on, as given: its gross burn and its revenue a month, from its
    month. A phase given with no revenue is worked as none, and its line says so."""
    lines = []
    for number, phase in enumerate(runway.phases, start=1):
        name = f"Phase {number}, from month {phase.from_month}"
        key = f"phase_{number}"
        revenue_how = GIVEN if _REVENUE in phase.model_fields_set else _REVENUE_NOT_GIVEN
        lines += [
            Line(f"{key}_gross_burn", f"{name}: gross burn a month", (given("money", phase.gross_burn),), GIVEN),
            Line(f"{key}_revenue", f"{name}: revenue a month", (given("money", phase.revenue),), revenue_how),
        ]
    return lines


def _timing_lines(result: RaisePipelineResult, timing: RaiseTiming) -> list[Line]:
    """The cash, the floor and the burn as given, then the runway plan's runway with no raise, the months to raise and
    the start-raising month."""
    runway = result.inputs.runway
    lines = []
    if runway is not None:
        lines += [
            Line("cash_on_hand", "Cash on hand", (given("money", runway.cash_on_hand),), GIVEN),
            Line("cash_floor", "Cash floor", (given("money", runway.cash_floor),), _floor_how(runway)),
            *_phase_lines(runway),
        ]
    runway_months: EquityQuantity | str = _NEVER if timing.runway_months is None else timing.runway_months
    start: EquityQuantity | str = _NEVER if timing.start_raising_by is None else timing.start_raising_by
    lines += [
        Line(
            "runway_no_raise",
            "Runway with no raise (the runway plan's)",
            (runway_months,),
            "months until cash less the floor goes below zero, on the plan",
        ),
        Line(
            "months_to_raise",
            "Months to raise",
            (given("months", Decimal(timing.months_to_raise)),),
            GIVEN,
        ),
        Line(
            "start_raising_by",
            "Start raising by (the runway plan's)",
            (start,),
            "runway with no raise - months to raise, in months from today",
        ),
    ]
    return lines


def _flag_words(flag: RaisePipelineFlag, result: RaisePipelineResult) -> str:
    """What a flag means for the founder, in plain words; none says whom to pitch."""
    wanted = result.inputs.term_sheets_wanted
    words: dict[RaisePipelineFlag, str] = {
        "no_lead_cheque_given": "No lead cheque was given, so none is counted: the allocation left still holds the "
        "lead's part of the round",
        "no_pro_rata_given": "No pro rata amount was given, so none is counted: if existing investors hold pro rata "
        "rights, the allocation left is smaller than shown",
        "soft_commitments_not_counted": "At least one commitment is soft: soft commitments are shown on their own "
        "line and never counted against the round",
        "oversubscribed": "The lead's cheque and the firm commitments alone come to more than the round: the "
        "allocation left is below zero before any pro rata",
        "pro_rata_exceeds_left": "The lead's cheque and the firm commitments fit in the round, but the pro rata is "
        "larger than the room they leave: the allocation left is below zero",
        "fully_allocated": "The lead's cheque, the firm commitments and the pro rata take the whole round exactly: "
        "nothing is left to allocate",
        "no_funnel_given": "No funnel was given, so there are no expected term sheets and no targets needed",
        "benchmark_rates_given": "At least one rate is a benchmark the founder gave with its source, not the "
        "founder's own: the expected term sheets lean on it",
        "funnel_short_of_wanted": f"On the founder's rates, today's funnel is expected to give fewer than the "
        f"{wanted} term sheets wanted: see the more targets needed line",
        "no_runway_given": "No cash and burn were given, so there is no start-raising month",
        "cash_never_runs_out": "On the plan with no raise, revenue covers the burn before the cash runs out, so the "
        "runway gives no start-raising month",
        "start_raising_date_passed": "With no raise, the plan's runway less the months to raise is already at or "
        "past today: on the plan, raising takes longer than the cash lasts",
    }
    return words[flag]


def raise_pipeline_sheet(result: RaisePipelineResult) -> Sheet:
    """The pipeline's lines: the allocation, the funnel, the timing, then the flags."""
    lines = _allocation_lines(result)
    if result.funnel is not None:
        lines += _funnel_lines(result.funnel)
    if result.timing is not None:
        lines += _timing_lines(result, result.timing)
    lines += [Line(f"flag_{flag}", "Flag", (flag,), _flag_words(flag, result)) for flag in result.flags]
    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
