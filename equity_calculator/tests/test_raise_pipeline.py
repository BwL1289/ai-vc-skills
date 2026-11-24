"""``raise_pipeline``: the allocation left, the funnel's expected term sheets and targets, and the runway plan's month.

Company RA (``tests.support.RAISE_PIPELINE_RA``, made up) is worked by hand in exact fractions. The allocation:
R = 4,000,000, L = 2,500,000, F = 500,000 (S = 500,000 soft, never counted), P = 400,000, so R - L - F = 1,000,000 and
the allocation left is 600,000. The funnel: rates 1/2, 3/10 and 1/4, so q_3 = 1/4, q_2 = 3/40, q_1 = 3/80; with 40,
10 and 2 investors at the stages, E = 40·3/80 + 10·3/40 + 2·1/4 = 3/2 + 3/4 + 1/2 = 11/4. For W = 3:
T = ceiling(3·80/3) = 80, M = ceiling((3 - 11/4)·80/3) = ceiling(20/3) = 7, and per stage ceiling(3/q_k) = 80, 40, 12.
The runway: $1,200,000 at $120,000 net a month lasts 10 months; less 6 months to raise, start raising by month 4.
"""

from __future__ import annotations

import math
import random
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.raise_pipeline import compute_raise_pipeline, conversion_from, expected_term_sheets
from equity_calculator.runway_plan import compute_runway_plan
from equity_calculator.schemas.equity_raise_pipeline import MAX_STAGES, RaisePipelineFlag, RaisePipelineInput
from equity_calculator.schemas.equity_runway_plan import RunwayPlanInput
from pydantic import ValidationError
from tests.support import RAISE_PIPELINE_RA, RAISE_PIPELINE_RA_STAGES, raise_pipeline

_SEED = 20261124
_RANDOM_CASES = 200


def _with(**changes: object) -> dict[str, object]:
    return {**RAISE_PIPELINE_RA, **changes}


def _refusal(fields: dict[str, object]) -> str:
    with pytest.raises(ValidationError) as caught:
        RaisePipelineInput.model_validate(fields)
    return str(caught.value)


def test_company_ra_allocation_is_worked_exactly() -> None:
    allocation = raise_pipeline(**RAISE_PIPELINE_RA).allocation

    assert allocation.round_size.exact == 4_000_000
    assert allocation.lead_cheque is not None and allocation.lead_cheque.exact == 2_500_000
    assert allocation.firm_total.exact == 500_000
    assert allocation.soft_total.exact == 500_000
    assert allocation.pro_rata_total.exact == 400_000
    assert allocation.room_after_lead_and_firm.exact == 1_000_000
    assert allocation.allocation_left.exact == 600_000


def test_soft_commitments_are_never_counted() -> None:
    """Turning every soft commitment into nothing leaves the allocation left where it was; turning one firm moves it."""
    soft_only = [{"amount": "250000", "kind": "soft"}] * 2
    without_soft = raise_pipeline(**_with(commitments=[{"amount": "500000", "kind": "firm"}]))
    with_more_soft = raise_pipeline(**_with(commitments=[{"amount": "500000", "kind": "firm"}, *soft_only, *soft_only]))
    one_firmed = raise_pipeline(
        **_with(commitments=[{"amount": "500000", "kind": "firm"}, {"amount": "250000", "kind": "firm"}])
    )

    assert without_soft.allocation.allocation_left.exact == 600_000
    assert with_more_soft.allocation.allocation_left.exact == 600_000
    assert with_more_soft.allocation.soft_total.exact == 1_000_000
    assert one_firmed.allocation.allocation_left.exact == 350_000
    assert "soft_commitments_not_counted" not in without_soft.flags


def test_company_ra_funnel_is_worked_exactly() -> None:
    funnel = raise_pipeline(**RAISE_PIPELINE_RA).funnel
    assert funnel is not None

    assert funnel.conversion.exact == Fraction(3, 80)
    assert funnel.expected_term_sheets.exact == Fraction(11, 4)
    assert funnel.term_sheets_wanted == 3
    assert funnel.targets_needed.exact == 80
    assert funnel.more_targets_needed.exact == 7
    assert [row.rate.exact for row in funnel.stages] == [Fraction(1, 2), Fraction(3, 10), Fraction(1, 4)]
    assert [row.rate_to_term_sheet.exact for row in funnel.stages] == [Fraction(3, 80), Fraction(3, 40), Fraction(1, 4)]
    assert [row.expected_here.exact for row in funnel.stages] == [40, 30, 11]
    assert [row.expected_to_next.exact for row in funnel.stages] == [20, 9, Fraction(11, 4)]
    assert [row.needed_here.exact for row in funnel.stages] == [80, 40, 12]
    assert [row.name for row in funnel.stages] == ["Intro asked", "First meeting", "Partner meeting"]


def test_with_every_investor_at_the_first_stage_e_is_the_targets_times_the_product_of_the_rates() -> None:
    """The spec's two formulas hold literally when only the first stage has a count: E = n·q_1, T = ceiling(W/q_1)."""
    stages = [
        {**RAISE_PIPELINE_RA_STAGES[0], "investors": 80},
        *({**stage, "investors": 0} for stage in RAISE_PIPELINE_RA_STAGES[1:]),
    ]
    funnel = raise_pipeline(**_with(stages=stages)).funnel
    assert funnel is not None

    assert funnel.expected_term_sheets.exact == 80 * Fraction(3, 80) == 3
    assert funnel.targets_needed.exact == 80
    assert funnel.more_targets_needed.exact == 0


def test_the_last_stage_s_expected_to_move_on_is_the_expected_term_sheets() -> None:
    funnel = raise_pipeline(**RAISE_PIPELINE_RA).funnel
    assert funnel is not None

    assert funnel.stages[-1].expected_to_next.exact == funnel.expected_term_sheets.exact


def test_seeded_funnels_agree_with_the_stage_by_stage_walk() -> None:
    """Σ n_k·q_k equals the walk e_k = n_k + e_(k-1)·r_(k-1), and each ceiling is the least whole count that reaches W
    in expectation."""
    generator = random.Random(_SEED)
    for _ in range(_RANDOM_CASES):
        count = generator.randint(1, MAX_STAGES)
        stages = [
            {
                "name": f"Stage {index}",
                "investors": generator.randint(0, 60),
                "rate_percent": str(generator.randint(1, 100)),
            }
            for index in range(1, count + 1)
        ]
        wanted = generator.randint(1, 10)
        funnel = raise_pipeline(**_with(stages=stages, term_sheets_wanted=wanted)).funnel
        assert funnel is not None
        rates = [Fraction(int(str(stage["rate_percent"])), 100) for stage in stages]
        walked = Fraction(0)
        for stage, rate in zip(stages, rates, strict=True):
            walked = (int(str(stage["investors"])) + walked) * rate
        assert funnel.expected_term_sheets.exact == walked
        conversion = math.prod(rates, start=Fraction(1))
        assert funnel.conversion.exact == conversion
        targets = funnel.targets_needed.exact
        assert targets * conversion >= wanted > (targets - 1) * conversion
        more = funnel.more_targets_needed.exact
        assert more >= 0
        assert walked + more * conversion >= wanted
        assert more == 0 or walked + (more - 1) * conversion < wanted


def test_the_helpers_are_the_funnel_s_own_figures() -> None:
    inputs = RaisePipelineInput.model_validate(RAISE_PIPELINE_RA)

    assert conversion_from(inputs.stages, 0) == Fraction(3, 80)
    assert conversion_from(inputs.stages, 2) == Fraction(1, 4)
    assert expected_term_sheets(inputs.stages) == Fraction(11, 4)


def test_company_ra_start_raising_month_is_the_runway_plan_s_own() -> None:
    """The timing is the runway plan scenario's own no-raise row on the plan, never worked a second way."""
    result = raise_pipeline(**RAISE_PIPELINE_RA)
    timing = result.timing
    assert timing is not None
    runway = compute_runway_plan(
        RunwayPlanInput.model_validate(
            {
                "cash_on_hand": "1200000",
                "cases": [{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "150000", "revenue": "30000"}]}],
                "months_to_raise": 6,
            }
        )
    )
    row = next(item for item in runway.runway if item.case == "plan" and item.option == 0)

    assert timing.runway_months == row.runway_months
    assert timing.start_raising_by == row.start_raising_by
    assert timing.runway_months is not None and timing.runway_months.exact == 10
    assert timing.start_raising_by is not None and timing.start_raising_by.exact == 4
    assert timing.months_to_raise == 6
    assert timing.runway_flags == runway.flags
    # The runway plan's own assumption rows follow the pipeline's, word for word.
    assert result.assumptions[-len(runway.assumptions) :] == runway.assumptions


def test_company_ra_flags() -> None:
    assert raise_pipeline(**RAISE_PIPELINE_RA).flags == ("soft_commitments_not_counted", "funnel_short_of_wanted")


@pytest.mark.parametrize(
    ("lead", "firm", "pro_rata", "flags", "left"),
    [
        ("3600000", "500000", ["100000"], ("oversubscribed",), -200_000),
        ("3000000", "500000", ["600000"], ("pro_rata_exceeds_left",), -100_000),
        ("3000000", "500000", ["500000"], ("fully_allocated",), 0),
        ("3000000", "1000000", [], ("fully_allocated",), 0),
        ("3000000", "500000", [], (), 500_000),
    ],
    ids=["lead-and-firm-alone-over", "pro-rata-over", "exactly-full", "full-without-pro-rata", "room-left"],
)
def test_an_overfull_round_names_one_cause(
    lead: str, firm: str, pro_rata: list[str], flags: tuple[str, ...], left: int
) -> None:
    """oversubscribed (L + F > R) and pro_rata_exceeds_left (L + F <= R < L + F + P) never hold together, and exactly
    one holds whenever the allocation left is below zero."""
    result = raise_pipeline(
        **_with(lead_cheque=lead, commitments=[{"amount": firm, "kind": "firm"}], pro_rata=pro_rata)
    )
    allocation_flags = tuple(
        flag for flag in result.flags if flag in ("oversubscribed", "pro_rata_exceeds_left", "fully_allocated")
    )

    assert allocation_flags == flags
    assert result.allocation.allocation_left.exact == left


def test_seeded_rounds_flag_an_overfull_round_once() -> None:
    generator = random.Random(_SEED)
    for _ in range(_RANDOM_CASES):
        lead = generator.choice([None, str(generator.randint(1, 30) * 100_000)])
        commitments = [
            {"amount": str(generator.randint(1, 10) * 50_000), "kind": generator.choice(["soft", "firm"])}
            for _ in range(generator.randint(0, 5))
        ]
        pro_rata = [str(generator.randint(1, 10) * 50_000) for _ in range(generator.randint(0, 3))]
        result = raise_pipeline(round_size="4000000", lead_cheque=lead, commitments=commitments, pro_rata=pro_rata)
        left = result.allocation.allocation_left.exact
        over = {"oversubscribed", "pro_rata_exceeds_left"} & set(result.flags)

        assert len(over) == (1 if left < 0 else 0)
        assert ("fully_allocated" in result.flags) == (left == 0)
        firm = sum((Fraction(item["amount"]) for item in commitments if item["kind"] == "firm"), Fraction(0))
        lead_amount = Fraction(0) if lead is None else Fraction(lead)
        taken = lead_amount + firm + sum((Fraction(amount) for amount in pro_rata), Fraction(0))
        assert left == 4_000_000 - taken


def test_with_no_lead_no_funnel_and_no_runway_each_is_flagged() -> None:
    result = raise_pipeline(round_size="2000000")

    assert result.funnel is None and result.timing is None
    assert result.allocation.lead_cheque is None
    assert result.allocation.allocation_left.exact == 2_000_000
    assert result.flags == ("no_lead_cheque_given", "no_funnel_given", "no_runway_given")
    assert [item.key for item in result.assumptions] == ["allocation_rule", "pro_rata_rule"]
    assert "L = 0: no lead cheque given" in result.assumptions[0].setting


def test_a_benchmark_rate_is_flagged_and_its_source_kept() -> None:
    stages = [
        RAISE_PIPELINE_RA_STAGES[0],
        {**RAISE_PIPELINE_RA_STAGES[1], "rate_basis": "benchmark", "benchmark_source": "A founders' survey, 2025"},
        RAISE_PIPELINE_RA_STAGES[2],
    ]
    result = raise_pipeline(**_with(stages=stages))
    assert result.funnel is not None

    assert "benchmark_rates_given" in result.flags
    assert result.funnel.stages[1].benchmark_source == "A founders' survey, 2025"
    basis = next(item for item in result.assumptions if item.key == "rate_basis")
    assert basis.setting == "benchmark rates at First meeting"


@pytest.mark.parametrize(
    ("phases", "flag", "start"),
    [
        ([{"from_month": 1, "gross_burn": "100000", "revenue": "150000"}], "cash_never_runs_out", None),
        ([{"from_month": 1, "gross_burn": "500000"}], "start_raising_date_passed", Fraction(-18, 5)),
    ],
    ids=["revenue-covers-the-burn", "already-late"],
)
def test_the_runway_plan_s_flags_come_through(
    phases: list[dict[str, object]], flag: str, start: Fraction | None
) -> None:
    runway = {"cash_on_hand": "1200000", "phases": phases, "months_to_raise": 6}
    result = raise_pipeline(**_with(runway=runway))
    timing = result.timing
    assert timing is not None

    assert flag in result.flags and flag in timing.runway_flags
    assert (None if timing.start_raising_by is None else timing.start_raising_by.exact) == start


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"stages": [{"name": "First meeting", "investors": 10}]}, "stage_rate_missing: First meeting has no rate"),
        ({"commitments": [{"amount": "500000"}]}, "commitment_kind_missing: mark each commitment soft or firm"),
        ({"stages": []}, "no_funnel_given: term_sheets_wanted needs the founder's funnel"),
        ({"term_sheets_wanted": None}, "no_term_sheet_count_given"),
        (
            {"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "rate_basis": "benchmark"}]},
            "benchmark_rate_without_source: Intro asked's rate is a benchmark",
        ),
        (
            {"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "benchmark_source": "A survey"}]},
            "benchmark_source goes with rate_basis benchmark",
        ),
        ({"stages": [RAISE_PIPELINE_RA_STAGES[0], RAISE_PIPELINE_RA_STAGES[0]]}, "each stage's name may appear once"),
        ({"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "rate_percent": "0"}]}, "greater than 0"),
        ({"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "rate_percent": "100.5"}]}, "less than or equal to 100"),
        ({"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "name": "=HYPERLINK(1)"}]}, "a stage's name starts with"),
        ({"stages": [{**RAISE_PIPELINE_RA_STAGES[0], "investors": "40"}]}, "Input should be a valid integer"),
        ({"term_sheets_wanted": 0}, "greater than or equal to 1"),
        ({"pro_rata": ["0"]}, "greater than 0"),
        (
            {"runway": {"cash_on_hand": "100", "phases": [{"from_month": 1, "gross_burn": "10"}]}},
            "no_months_to_raise_given",
        ),
        (
            {
                "runway": {
                    "cash_on_hand": "100",
                    "phases": [{"from_month": 2, "gross_burn": "10"}],
                    "months_to_raise": 3,
                }
            },
            "the first phase must start at month 1 (got month 2)",
        ),
        (
            {
                "runway": {
                    "cash_on_hand": "100",
                    "cash_floor": "200",
                    "phases": [{"from_month": 1, "gross_burn": "10"}],
                    "months_to_raise": 3,
                }
            },
            "cash_floor is above cash_on_hand",
        ),
    ],
)
def test_refusals_say_what_to_ask_the_founder(changes: dict[str, object], message: str) -> None:
    assert message in _refusal(_with(**changes))


def test_a_runway_refusal_names_its_cause_only() -> None:
    """The runway plan's check is reused whole; a phase that fails does not also report the case list as too short."""
    text = _refusal(
        _with(runway={"cash_on_hand": "100", "phases": [{"from_month": 2, "gross_burn": "10"}], "months_to_raise": 3})
    )

    assert "should have at least 1 item" not in text


def test_every_flag_is_reachable() -> None:
    """Each flag code holds for at least one input, so none is dead text in the skill's flag table."""
    seen: set[str] = set()
    cases = [
        RAISE_PIPELINE_RA,
        {"round_size": "1000"},
        {"round_size": "1000", "lead_cheque": "900", "commitments": [{"amount": "200", "kind": "firm"}]},
        {"round_size": "1000", "lead_cheque": "900", "pro_rata": ["200"]},
        {"round_size": "1000", "lead_cheque": "900", "pro_rata": ["100"]},
        _with(stages=[{**RAISE_PIPELINE_RA_STAGES[0], "rate_basis": "benchmark", "benchmark_source": "A survey"}]),
        _with(
            runway={
                "cash_on_hand": "100",
                "phases": [{"from_month": 1, "gross_burn": "1", "revenue": "2"}],
                "months_to_raise": 1,
            }
        ),
        _with(runway={"cash_on_hand": "100", "phases": [{"from_month": 1, "gross_burn": "100"}], "months_to_raise": 6}),
    ]
    for fields in cases:
        seen.update(compute_raise_pipeline(RaisePipelineInput.model_validate(fields)).flags)

    assert seen == set(get_args(RaisePipelineFlag))
