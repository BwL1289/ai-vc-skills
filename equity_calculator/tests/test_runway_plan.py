"""The runway plan: exact runways, milestones and required raises, refusals, flags, checks and assumption rows.

Pure arithmetic: no DB, no network. Companies W, X and Y (``tests.support``) are made up; their runways are written
out as exact fractions. The properties check the segment walk against ``cumulative_burn`` evaluated at breakpoints,
and the smallest raise against the runway it buys, on seeded random plans.
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.funds import use_of_funds_assumption
from equity_calculator.layout import sheet_for
from equity_calculator.runway_plan import Phase, cumulative_burn, required_raise, runway
from equity_calculator.schemas.equity_runway_plan import (
    MAX_CASES,
    MAX_MILESTONES,
    MAX_PHASES,
    MAX_RAISES,
    RunwayPlanFlag,
    RunwayPlanInput,
    RunwayPlanResult,
)
from equity_calculator.text import render_sheet
from pydantic import ValidationError
from tests.support import RUNWAY_W, RUNWAY_W_PLAN, RUNWAY_X, RUNWAY_Y, deal_check, runway_plan

_SEED = 20261123
_CASES = 200
_FLAT = [{"from_month": 1, "gross_burn": "100000"}]
_PLAN_FLAT = {"name": "plan", "phases": _FLAT}
_MILESTONE_QUOTE = (
    '"raise as much money as needed to get to their next “fundable” milestone, which will usually be 12 to 18 months '
    'later"'
)
_BAND_QUOTE = '"raising for N months (usually 12-18)"'
_YC_GUIDE = 'Y Combinator, "A guide to seed fundraising"'


def _runway(result: RunwayPlanResult, case: str, option: int) -> Fraction | None:
    row = next(row for row in result.runway if row.case == case and row.option == option)
    return None if row.runway_months is None else row.runway_months.exact


def _required(result: RunwayPlanResult, case: str, lands: int = 0, milestone: int = 1) -> Fraction | None:
    row = next(
        row for row in result.required if row.case == case and row.lands_month == lands and row.milestone == milestone
    )
    return None if row.amount is None else row.amount.exact


def _verdict(result: RunwayPlanResult, case: str, option: int, milestone: int = 1) -> str:
    return next(
        row.verdict
        for row in result.milestones
        if row.case == case and row.option == option and row.milestone == milestone
    )


def _plan(*phases: tuple[int, str, str], **fields: object) -> dict[str, object]:
    """A plan from (from_month, gross, revenue) phases, plus other ``RunwayPlanInput`` fields."""
    steps = [{"from_month": month, "gross_burn": gross, "revenue": revenue} for month, gross, revenue in phases]
    return {"cash_on_hand": "100000", "cases": [{"name": "plan", "phases": steps}], **fields}


# --- exact worked plans -------------------------------------------------------------------------------------------


def test_company_w_runways_milestones_and_required_raises_are_exact() -> None:
    """$500k, three phases, $3M or $4M now: the plan, the downside at half revenue, and the no-raise row."""
    result = runway_plan(**RUNWAY_W)

    assert _runway(result, "plan", 0) == Fraction(151, 39)
    assert _runway(result, "plan", 1) == Fraction(859, 48)
    assert _runway(result, "plan", 2) == Fraction(353, 16)
    assert _runway(result, "downside", 1) == Fraction(1811, 108)
    assert _runway(result, "downside", 2) == Fraction(737, 36)
    assert _required(result, "plan") == 3_745_000
    assert _required(result, "downside") == 4_142_500
    assert [_verdict(result, "plan", option) for option in range(3)] == ["short", "short", "covered"]
    assert [_verdict(result, "downside", option) for option in range(3)] == ["short", "short", "short"]
    no_raise = next(row for row in result.runway if row.case == "plan" and row.option == 0)
    assert no_raise.start_raising_by is not None and no_raise.start_raising_by.exact == Fraction(-83, 39)
    assert str(no_raise.start_raising_by.rounded) == "-2.13"
    assert result.flags == (
        "milestone_short_on_plan",
        "downside_short_where_plan_covers",
        "start_raising_date_passed",
        "runway_below_band",
    )
    assert result.verdict == "not_checked"


def test_company_x_waiting_six_months_lands_before_the_cash_runs_out() -> None:
    """$2M now against $3M after six months: the waiting option lands with cash left and lasts longer."""
    result = runway_plan(**RUNWAY_X)
    wait = next(row for row in result.runway if row.case == "plan" and row.option == 2)

    assert _runway(result, "plan", 1) == Fraction(187, 9)
    assert wait.runway_months is not None and wait.runway_months.exact == Fraction(79, 3)
    assert _runway(result, "downside", 1) == Fraction(983, 53)
    assert _runway(result, "downside", 2) == Fraction(1233, 53)
    assert not wait.ran_out_before_landing
    assert wait.cash_at_landing is not None and wait.cash_at_landing.exact == 1_200_000 - 6 * 120_000
    assert wait.runway_from_landing is not None and wait.runway_from_landing.exact == Fraction(79, 3) - 6
    assert _required(result, "plan", 0) == _required(result, "plan", 6) == 2_580_000
    assert _required(result, "downside", 0) == _required(result, "downside", 6) == 3_156_000
    assert "downside_short_where_plan_covers" in result.flags


def test_company_y_stated_runway_is_a_mismatch() -> None:
    """$1.5M with a stated 24 months lasts 66/5 months: a mismatch of -54/5, and the milestone is short."""
    result = runway_plan(**RUNWAY_Y)
    (check,) = result.checks

    assert (check.key, check.option, check.verdict) == ("runway_months", 1, "mismatch")
    assert check.computed.exact == Fraction(66, 5)
    assert check.difference.exact == Fraction(-54, 5)
    assert _required(result, "plan") == 2_220_000
    assert _verdict(result, "plan", 1) == "short"
    assert result.verdict == "mismatch"


def test_one_flat_phase_agrees_with_the_deal_checks_planned_net_runway() -> None:
    """On one flat phase, a raise landing now and no floor, the runway is deal_check's (cash + I)/net burn exactly."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        gross = rng.randint(10_000, 900_000)
        revenue = rng.randint(0, gross - 1)
        cash, investment = rng.randint(0, 5_000_000), rng.randint(1, 20_000_000)
        phases = [{"from_month": 1, "gross_burn": str(gross), "revenue": str(revenue)}]
        plan = runway_plan(
            cash_on_hand=str(cash), cases=[{"name": "plan", "phases": phases}], raises=[{"amount": str(investment)}]
        )
        deal = deal_check(
            investment=str(investment),
            pre_money="10000000",
            cash_on_hand=str(cash),
            planned_monthly_gross_burn=str(gross),
            planned_monthly_revenue=str(revenue),
        )
        net_runway = deal.runway[0].net_runway
        assert net_runway is not None
        assert _runway(plan, "plan", 1) == net_runway.exact


# --- properties -----------------------------------------------------------------------------------------------------


def _random_phases(rng: random.Random) -> tuple[Phase, ...]:
    months = sorted(rng.sample(range(2, 30), rng.randint(0, 4)))
    phases = []
    for month in [1, *months]:
        gross = Fraction(rng.randint(1, 300), rng.choice([1, 2, 3, 7]))
        revenue = Fraction(rng.randint(0, 400), rng.choice([1, 3]))
        phases.append(Phase(month, gross, revenue))
    return tuple(phases)


def _cash(phases: tuple[Phase, ...], available: Fraction, amount: Fraction, lands: int, at: Fraction) -> Fraction:
    """Cash above the floor at elapsed time ``at``, the money in from ``lands`` on."""
    return available + (amount if at >= lands else 0) - cumulative_burn(phases, at)


def _points(phases: tuple[Phase, ...], lands: int, until: Fraction) -> list[Fraction]:
    starts = {Fraction(phase.from_month - 1) for phase in phases} | {Fraction(lands), Fraction(0)}
    return sorted(point for point in starts if point <= until)


def test_property_the_runway_is_where_cash_first_goes_below_the_floor() -> None:
    """Cash is at or above the floor at every breakpoint before R (just before a landing too), at zero at R, and
    below it just after; with no R, the last phase's net burn is not positive and cash never goes below it."""
    rng = random.Random(_SEED + 1)
    for _ in range(_CASES * 5):
        phases = _random_phases(rng)
        available = Fraction(rng.randint(0, 2_000), rng.choice([1, 2]))
        amount, lands = Fraction(rng.randint(0, 3_000)), rng.randint(0, 25)
        months, before = runway(phases, available, amount, lands)
        horizon = Fraction(40) if months is None else months
        for point in _points(phases, lands, horizon):
            if point < horizon:
                assert _cash(phases, available, amount, lands, point) >= 0
        if 0 < lands <= horizon:
            assert available - cumulative_burn(phases, Fraction(lands)) >= 0
        if months is None:
            assert phases[-1].net <= 0
            assert not before
            continue
        nearest = min([p for p in _points(phases, lands, Fraction(10**6)) if p > months] or [months + 1])
        step = (nearest - months) / 2
        assert _cash(phases, available, amount, lands, months) == 0
        assert _cash(phases, available, amount, lands, months + step) < 0
        assert before == (months < lands)


def test_property_an_option_covers_a_milestone_exactly_when_it_raises_the_required_amount() -> None:
    """For random plans, floors, landings and targets: with I* the runway reaches T, with less it does not; with no
    I*, no amount does."""
    rng = random.Random(_SEED + 2)
    for _ in range(_CASES * 5):
        phases = _random_phases(rng)
        available = Fraction(rng.randint(0, 2_000))
        lands, target = rng.randint(0, 20), rng.randint(1, 30)
        needed = required_raise(phases, available, lands, target)

        def covers(
            amount: Fraction,
            phases: tuple[Phase, ...] = phases,
            available: Fraction = available,
            lands: int = lands,
            target: int = target,
        ) -> bool:
            months, _ = runway(phases, available, amount, lands)
            return months is None or months >= target

        if needed is None:
            assert not covers(Fraction(10**9))
            continue
        assert covers(needed)
        if needed > 0:
            assert not covers(needed - Fraction(1, 1000))
        for point in _points(phases, lands, Fraction(target)):
            assert _cash(phases, available, needed, lands, point) >= 0


# --- edge cases -----------------------------------------------------------------------------------------------------


def test_cash_that_touches_zero_and_then_rises_does_not_run_out() -> None:
    """$100k, net $50k for two months, then revenue above the burn: cash reaches zero at month 2 and recovers."""
    result = runway_plan(
        **_plan((1, "100000", "50000"), (3, "100000", "150000"), raises=[{"amount": "1", "lands_month": 5}])
    )

    assert _runway(result, "plan", 0) is None
    assert _runway(result, "plan", 1) is None
    assert "cash_never_runs_out" in result.flags


def test_cash_exactly_at_zero_as_the_money_lands_survives() -> None:
    """$100k at $100k a month with $1M landing after one month: zero at the landing, then 10 more months."""
    result = runway_plan(**_plan((1, "100000", "0"), raises=[{"amount": "1000000", "lands_month": 1}]))
    row = next(row for row in result.runway if row.option == 1)

    assert row.runway_months is not None and row.runway_months.exact == 11
    assert not row.ran_out_before_landing
    assert row.cash_at_landing is not None and row.cash_at_landing.exact == 0


def test_a_raise_landing_after_the_cash_runs_out_comes_too_late() -> None:
    """$300k at $100k a month, $1M after five months: the cash runs out at month 3, so no amount landing then works."""
    result = runway_plan(
        **_plan((1, "100000", "0"), cash_on_hand="300000", raises=[{"amount": "1000000", "lands_month": 5}]),
        milestones=[2, 8],
        months_to_raise=0,
    )
    late = next(row for row in result.runway if row.option == 1)

    assert late.ran_out_before_landing
    assert late.runway_months is not None and late.runway_months.exact == _runway(result, "plan", 0) == 3
    assert late.cash_at_landing is None and late.runway_from_landing is None
    assert _required(result, "plan", 5, milestone=2) is None
    assert _required(result, "plan", 0, milestone=2) == 500_000
    assert _required(result, "plan", 5, milestone=1) == 0
    assert "cash_out_before_raise_lands" in result.flags


def test_a_cash_floor_comes_off_the_cash() -> None:
    """A $100k floor on $400k at $100k a month leaves 3 months, as $300k with no floor does."""
    floored = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="400000", cash_floor="100000"))

    assert _runway(floored, "plan", 0) == 3


# --- derived cases --------------------------------------------------------------------------------------------------


def test_a_derived_case_scales_every_plan_phase_exactly() -> None:
    """Revenue at 50% halves each phase's revenue; gross burn at 110% scales each phase's gross; 100 when left out."""
    result = runway_plan(
        cash_on_hand="500000",
        cases=[
            {"name": "plan", "phases": RUNWAY_W_PLAN},
            {"name": "downside", "revenue_percent_of_plan": "50"},
            {"name": "lean", "gross_burn_percent_of_plan": "110"},
        ],
    )
    plan, downside, lean = result.cases

    for given, worked in zip(plan.phases, downside.phases, strict=True):
        assert worked.revenue.exact == given.revenue.exact / 2
        assert worked.gross_burn.exact == given.gross_burn.exact
    for given, worked in zip(plan.phases, lean.phases, strict=True):
        assert worked.gross_burn.exact == given.gross_burn.exact * Fraction(11, 10)
        assert worked.revenue.exact == given.revenue.exact
    assert [phase.to_month for phase in plan.phases] == [3, 12, None]


# --- refusals ---------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"cases": [{"name": "downside", "phases": _FLAT}]}, "the first case must be the plan"),
        ({"cases": [{"name": "plan", "revenue_percent_of_plan": "50"}]}, "the plan needs its own phases"),
        (
            {"cases": [_PLAN_FLAT, {"name": "lean", "phases": _FLAT}, {"name": "lean", "phases": _FLAT}]},
            "cases: each case name may appear once",
        ),
        (
            {"cases": [_PLAN_FLAT, {"name": "downside", "phases": _FLAT, "revenue_percent_of_plan": "50"}]},
            "not both",
        ),
        ({"cases": [_PLAN_FLAT, {"name": "downside"}]}, "revenue_percent_of_plan or gross_burn_percent_of_plan"),
        ({"cases": [{"name": "plan", "phases": [{"from_month": 2, "gross_burn": "1"}]}]}, "start at month 1"),
        (
            {"cases": [{"name": "plan", "phases": [*_FLAT, {"from_month": 1, "gross_burn": "2"}]}]},
            "a later month than the one before it",
        ),
        ({"cash_floor": "100001"}, "cash_floor is above cash_on_hand"),
        ({"milestones": [12, 12]}, "milestones: each milestone month may appear once"),
        (
            {"raises": [{"amount": "1", "use_of_funds": [{"amount": "1"}, {"percent": "50"}]}]},
            "every use_of_funds line as an amount or every one as a percent",
        ),
        (
            {"raises": [{"amount": "1", "lands_month": 2, "stated_runway_from": "landing"}]},
            "stated_runway_from needs a stated runway on the same raise",
        ),
    ],
    ids=[
        "plan-not-first",
        "plan-as-percent",
        "case-twice",
        "phases-and-percent",
        "neither",
        "first-month",
        "not-increasing",
        "floor-above-cash",
        "milestone-twice",
        "mixed-funds",
        "basis-without-runway",
    ],
)
def test_each_refusal_says_what_is_wrong(fields: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        RunwayPlanInput.model_validate({"cash_on_hand": "100000", "cases": [_PLAN_FLAT], **fields})


@pytest.mark.parametrize(
    ("field", "items"),
    [
        ("raises", [{"amount": "1"}] * (MAX_RAISES + 1)),
        ("milestones", list(range(1, MAX_MILESTONES + 2))),
        ("cases", [_PLAN_FLAT] * (MAX_CASES + 1)),
    ],
)
def test_every_list_is_capped(field: str, items: list[object]) -> None:
    with pytest.raises(ValidationError, match="at most"):
        RunwayPlanInput.model_validate({"cash_on_hand": "1", "cases": [_PLAN_FLAT], field: items})


def test_the_phases_are_capped() -> None:
    phases = [{"from_month": month, "gross_burn": "1"} for month in range(1, MAX_PHASES + 2)]

    with pytest.raises(ValidationError, match="at most"):
        RunwayPlanInput.model_validate({"cash_on_hand": "1", "cases": [{"name": "plan", "phases": phases}]})


@pytest.mark.parametrize(
    "fields",
    [
        {"milestones": [601]},
        {"months_to_raise": 61},
        {"raises": [{"amount": "1", "lands_month": 601}]},
        {"milestones": ["12"]},
        {"cases": [{"name": "plan", "phases": [{"from_month": 1.0, "gross_burn": "1"}]}]},
    ],
    ids=["milestone", "months-to-raise", "lands-month", "month-as-text", "month-as-float"],
)
def test_month_counts_are_whole_and_bounded(fields: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        RunwayPlanInput.model_validate({"cash_on_hand": "1", "cases": [_PLAN_FLAT], **fields})


# --- flags ----------------------------------------------------------------------------------------------------------

_SHORT_PLAN = _plan((1, "100000", "0"), raises=[{"amount": "500000"}], milestones=[10], months_to_raise=0)
# Each flag: a minimal plan that sets it, and a neighbour that does not.
FLAG_CASES: dict[str, tuple[dict[str, object], dict[str, object]]] = {
    "cash_never_runs_out": (_plan((1, "100000", "100000")), _plan((1, "100000", "99999"))),
    "cash_out_before_raise_lands": (
        _plan((1, "100000", "0"), raises=[{"amount": "1", "lands_month": 2}]),
        _plan((1, "100000", "0"), raises=[{"amount": "1", "lands_month": 1}]),
    ),
    "milestone_short_on_plan": (_SHORT_PLAN, {**_SHORT_PLAN, "milestones": [6]}),
    "downside_short_where_plan_covers": (
        {
            **_SHORT_PLAN,
            "milestones": [6],
            "cases": [{"name": "plan", "phases": _FLAT}, {"name": "downside", "gross_burn_percent_of_plan": "200"}],
        },
        {
            **_SHORT_PLAN,
            "milestones": [6],
            "cases": [{"name": "plan", "phases": _FLAT}, {"name": "downside", "gross_burn_percent_of_plan": "100"}],
        },
    ),
    "covered_without_raise": ({**_SHORT_PLAN, "milestones": [1]}, {**_SHORT_PLAN, "milestones": [2]}),
    "start_raising_date_passed": (
        _plan((1, "100000", "0"), months_to_raise=1),
        _plan((1, "100000", "0"), months_to_raise=0, cash_on_hand="100001"),
    ),
    "no_time_to_raise_given": (_plan((1, "100000", "0"), milestones=[1]), _plan((1, "100000", "0"))),
    "runway_below_band": (
        _plan((1, "100000", "0"), raises=[{"amount": "1699999"}]),
        _plan((1, "100000", "0"), raises=[{"amount": "1700000"}]),
    ),
    # 12.62 months: 12.5 is within 2% of it (0.2524) but not it rounded to one place (12.6); 12.6 is.
    "consistent_beyond_rounding": (
        _plan((1, "100000", "0"), cash_on_hand="1262000", stated_runway_months="12.5"),
        _plan((1, "100000", "0"), cash_on_hand="1262000", stated_runway_months="12.6"),
    ),
}


@pytest.mark.parametrize("flag", list(FLAG_CASES))
def test_each_flag_fires_on_its_case_and_not_on_its_neighbour(flag: str) -> None:
    on, off = FLAG_CASES[flag]

    assert flag in runway_plan(**on).flags
    assert flag not in runway_plan(**off).flags


def test_the_flag_cases_cover_every_flag() -> None:
    assert list(FLAG_CASES) == list(get_args(RunwayPlanFlag))


def test_the_runway_band_counts_raises_only() -> None:
    """The no-raise row's short runway never sets the band flag; only a raise's plan runway does."""
    assert "runway_below_band" not in runway_plan(**_plan((1, "100000", "0"))).flags


# --- checks ---------------------------------------------------------------------------------------------------------


def test_the_no_raise_runway_claim_is_checked_with_no_raise_given() -> None:
    """'We have 3 months without raising': option 0's plan runway is checked, with no raise needed."""
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="300000", stated_runway_months="3"))
    (check,) = result.checks

    assert (check.key, check.option, check.verdict) == ("runway_months", 0, "consistent")
    assert result.verdict == "consistent"


def test_a_runway_claim_is_not_checked_when_the_cash_never_runs_out() -> None:
    result = runway_plan(**_plan((1, "100000", "100000"), stated_runway_months="12"))

    assert result.checks == ()
    assert result.verdict == "not_checked"
    assert "cash_never_runs_out" in result.flags


@pytest.mark.parametrize(("stated", "verdict"), [("9.8", "consistent"), ("9.79", "mismatch"), ("10.2", "consistent")])
def test_the_runway_tolerance_edge_counts_as_consistent(stated: str, verdict: str) -> None:
    """$1M at $100k a month is 10 months; 2% of it is 0.2 months either side, the edge included."""
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1000000", stated_runway_months=stated))

    assert result.checks[0].verdict == verdict


def test_a_runway_counted_from_landing_drops_the_months_before_it() -> None:
    """$1M at $100k a month with $1.2M landing after 6 months: 22 months from today, 16 from landing."""
    raises = [{"amount": "1200000", "lands_month": 6, "stated_runway_months": "16", "stated_runway_from": "landing"}]
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1000000", raises=raises))
    (check,) = result.checks

    assert check.computed.exact == 16
    assert check.verdict == "consistent"


def test_a_runway_counted_from_landing_is_not_checked_when_the_cash_runs_out_first() -> None:
    """$300k at $100k a month runs out at month 3, before $2.4M lands after 5: no runway from landing to check."""
    raises = [{"amount": "2400000", "lands_month": 5, "stated_runway_months": "24", "stated_runway_from": "landing"}]
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="300000", raises=raises))
    row = next(row for row in result.runway if row.case == "plan" and row.option == 1)

    assert (row.ran_out_before_landing, row.runway_from_landing) == (True, None)
    assert result.checks == ()
    assert result.verdict == "not_checked"
    assert "cash_out_before_raise_lands" in result.flags
    assert "tolerance" not in {assumption.key for assumption in result.assumptions}


def test_a_runway_counted_from_landing_today_is_still_checked() -> None:
    """$1.2M landing today on $1M at $100k a month lasts 22 months, the same counted from today or from landing."""
    raises = [{"amount": "1200000", "lands_month": 0, "stated_runway_months": "22", "stated_runway_from": "landing"}]
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1000000", raises=raises))
    (check,) = result.checks

    assert (check.option, check.computed.exact, check.verdict) == (1, 22, "consistent")


@pytest.mark.parametrize(
    "lines",
    [
        [{"amount": "1500000"}, {"amount": "1000000"}, {"amount": "400000"}],
        [{"percent": "50"}, {"percent": "30"}, {"percent": "19.4"}],
        [{"percent": "50"}, {"percent": "30"}, {"percent": "19.6"}],
    ],
    ids=["amounts-short", "percents-short", "percents-within"],
)
def test_the_use_of_funds_check_matches_the_deal_checks(lines: list[dict[str, str]]) -> None:
    """The same lines on a $3M raise: the same dollars, total, share and verdict as deal_check's."""
    plan = runway_plan(**_plan((1, "100000", "0"), raises=[{"amount": "3000000", "use_of_funds": lines}]))
    deal = deal_check(investment="3000000", pre_money="12000000", use_of_funds=lines)
    (funds,) = plan.use_of_funds
    (check,) = plan.checks
    (deal_funds,) = deal.checks

    assert funds.lines == deal.use_of_funds
    assert funds.total == deal.use_of_funds_total
    assert funds.share == deal.use_of_funds_percent_total
    assert (check.stated, check.computed, check.difference, check.verdict) == (
        deal_funds.stated,
        deal_funds.computed,
        deal_funds.difference,
        deal_funds.verdict,
    )


# --- the rounding test ---------------------------------------------------------------------------------------------
# A stated runway that is the computed one rounded half away from zero to the places it is typed with is consistent,
# whatever the tolerance (equity_calculator.rounding, deal_check's rule); the use-of-funds total keeps the tolerance
# alone. $1.24M at $100k a month is 12.40 months, and 2% of it is 0.248 months, so 12 holds only as a rounding.


@pytest.mark.parametrize(
    ("typed", "verdict", "within"),
    [
        ("12", "consistent", True),
        ("12.0", "mismatch", False),
        ("12.4", "consistent", True),
        ("12.40", "consistent", True),
    ],
    ids=["whole", "one-place", "exact", "two-places"],
)
def test_a_12_month_runway_holds_against_12_40_but_12_0_does_not(typed: str, verdict: str, within: bool) -> None:
    """0.4 months is past 2% of 12.40, so 12 holds only as 12.40 rounded to no places; 12.0 claims a place that rounds
    to 12.4. The rounding verdict matches deal_check's on the same runway."""
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1240000", stated_runway_months=typed))
    deal = deal_check(
        investment="1000000",
        pre_money="4000000",
        cash_on_hand="240000",
        planned_monthly_gross_burn="100000",
        stated_runway_months=typed,
    )
    (check,) = result.checks

    assert (check.option, check.computed.exact) == (0, Fraction(62, 5))
    assert (check.verdict, check.within_rounding, result.verdict) == (verdict, within, verdict)
    assert (check.verdict, check.within_rounding) == (deal.checks[0].verdict, deal.checks[0].within_rounding)
    assert "consistent_beyond_rounding" not in result.flags


@pytest.mark.parametrize(
    ("fields", "held", "missed"),
    [
        ({"cash_on_hand": "1250000"}, "13", "12"),
        ({"cash_on_hand": "1245000", "tolerance_percent": "0"}, "12.5", "12.4"),
    ],
    ids=["no-places-12.5", "one-place-12.45"],
)
def test_a_half_rounds_away_from_zero(fields: dict[str, object], held: str, missed: str) -> None:
    """12.5 months rounds to 13, never to the even 12; 12.45 rounds to 12.5 at one place, never to 12.4 (with no
    tolerance, only the rounding can hold)."""
    up = runway_plan(**_plan((1, "100000", "0"), **fields, stated_runway_months=held)).checks[0]
    even = runway_plan(**_plan((1, "100000", "0"), **fields, stated_runway_months=missed)).checks[0]

    assert (up.verdict, up.within_rounding) == ("consistent", True)
    assert (even.verdict, even.within_rounding) == ("mismatch", False)


@pytest.mark.parametrize(
    ("raised", "computed", "typed", "verdict", "within"),
    [
        ({"amount": "240000"}, Fraction(62, 5), "12", "consistent", True),
        ({"amount": "240000"}, Fraction(62, 5), "12.0", "mismatch", False),
        (
            {"amount": "1240000", "lands_month": 6, "stated_runway_from": "landing"},
            Fraction(82, 5),
            "16",
            "consistent",
            True,
        ),
        (
            {"amount": "1240000", "lands_month": 6, "stated_runway_from": "landing"},
            Fraction(82, 5),
            "16.0",
            "mismatch",
            False,
        ),
    ],
    ids=["today-whole", "today-one-place", "landing-whole", "landing-one-place"],
)
def test_a_raises_stated_runway_takes_the_rounding_test_on_its_own_basis(
    raised: dict[str, object], computed: Fraction, typed: str, verdict: str, within: bool
) -> None:
    """$1M at $100k a month: $240k now lasts 12.40 months; $1.24M landing after 6 months lasts 22.40 months from today,
    16.40 from landing, and the rounding test reads the figure the claim counts from (0.4 months is past 2% of
    16.40, so 16 holds only as a rounding)."""
    raises = [{**raised, "stated_runway_months": typed}]
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1000000", raises=raises))
    (check,) = result.checks

    assert (check.option, check.computed.exact) == (1, computed)
    assert (check.verdict, check.within_rounding, result.verdict) == (verdict, within, verdict)


def test_the_no_raise_and_each_raise_are_tested_apart() -> None:
    """Two claims in one call: the no-raise 12 holds against 12.40 as a rounding, the raise's 22.0 against 22.40 by the
    tolerance alone (0.4 is within 2% of 22.40, 0.448, but 22.40 rounds to 22.4), so the verdict is consistent and the
    flag fires for the second."""
    raises = [{"amount": "1000000", "lands_month": 0, "stated_runway_months": "22.0"}]
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1240000", stated_runway_months="12", raises=raises))

    assert [(check.option, check.verdict, check.within_rounding) for check in result.checks] == [
        (0, "consistent", True),
        (1, "consistent", False),
    ]
    assert result.verdict == "consistent"
    assert "consistent_beyond_rounding" in result.flags


def test_a_mismatch_is_never_flagged_as_held_by_the_tolerance() -> None:
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1240000", stated_runway_months="12.0"))

    assert result.verdict == "mismatch" and "consistent_beyond_rounding" not in result.flags


@pytest.mark.parametrize(
    ("lines", "verdict"),
    [
        ([{"percent": "33"}, {"percent": "33"}, {"percent": "33"}], "mismatch"),
        ([{"amount": "1000000"}, {"amount": "990000"}], "mismatch"),
        ([{"amount": "1000000"}, {"amount": "1000000"}], "consistent"),
    ],
    ids=["percents-99", "amounts-1.99m", "amounts-exact"],
)
def test_the_use_of_funds_total_keeps_the_tolerance_alone(lines: list[dict[str, str]], verdict: str) -> None:
    """With no tolerance, lines of 33% three times (99%) and $1.99M of a $2M raise are mismatches: a total is a sum of
    lines, never a figure typed as one, so it has no rounding test and no flag."""
    raises = [{"amount": "2000000", "use_of_funds": lines}]
    result = runway_plan(**_plan((1, "100000", "0"), raises=raises, tolerance_points="0", tolerance_percent="0"))
    (check,) = result.checks

    assert (check.key, check.verdict, check.within_rounding) == ("use_of_funds_total", verdict, None)
    assert "consistent_beyond_rounding" not in result.flags


@pytest.mark.parametrize("where", ["no-raise", "raise"])
def test_a_stated_zero_runway_with_places_is_still_refused(where: str) -> None:
    """A stated runway keeps a zero's places like metrics_check's, but it is above zero, so "0.0" is refused, naming
    the field, before any rounding test."""
    fields: dict[str, object] = {"cash_on_hand": "1", "cases": [_PLAN_FLAT]}
    if where == "no-raise":
        fields["stated_runway_months"] = "0.0"
    else:
        fields["raises"] = [{"amount": "1", "stated_runway_months": "0.0"}]

    with pytest.raises(ValidationError, match="stated_runway_months"):
        RunwayPlanInput.model_validate(fields)


def test_a_stated_runway_echoes_with_the_places_it_was_typed_with() -> None:
    raises = [{"amount": "240000", "stated_runway_months": "12.40"}]
    result = runway_plan(
        **_plan((1, "100000", "0"), cash_on_hand="1000000", stated_runway_months="10.0", raises=raises)
    )
    dumped = result.inputs.model_dump(mode="json")

    assert (dumped["stated_runway_months"], dumped["raises"][0]["stated_runway_months"]) == ("10.0", "12.40")


def test_the_tolerance_row_states_the_rounding_rule_and_what_keeps_the_tolerance_alone() -> None:
    result = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="1240000", stated_runway_months="12"))
    rows = {row.key: row for row in result.assumptions}

    assert "rounded half away from zero to the places it is written with" in rows["tolerance"].statement
    assert "people write figures rounded to the places they show" in rows["tolerance"].statement
    assert "The use-of-funds total is held to the tolerance alone" in rows["tolerance"].statement
    assert rows["tolerance"].source == "unverified (the rounding test is standard arithmetic)"


# --- assumption rows ------------------------------------------------------------------------------------------------


def test_a_bare_plan_lists_only_the_runway_and_phase_rules() -> None:
    result = runway_plan(**_plan((1, "100000", "0")))

    assert [row.key for row in result.assumptions] == ["runway_rule", "phase_rule"]


def test_every_row_appears_when_its_input_is_used() -> None:
    result = runway_plan(
        **{
            **RUNWAY_W,
            "raises": [{"amount": "3000000", "stated_runway_months": "18", "use_of_funds": [{"percent": "100"}]}],
        }
    )

    assert [row.key for row in result.assumptions] == [
        "runway_rule",
        "phase_rule",
        "landing_rule",
        "derived_case_rule",
        "milestone_rule",
        "required_raise_rule",
        "tolerance",
        "runway_band",
        "use_of_funds_rule",
    ]
    assert result.assumptions[-1] == use_of_funds_assumption()


def test_the_milestone_and_band_rows_quote_the_yc_seed_guide() -> None:
    rows = {row.key: row for row in runway_plan(**RUNWAY_W).assumptions}

    assert rows["milestone_rule"].source.startswith(_YC_GUIDE)
    assert rows["milestone_rule"].source.endswith(_MILESTONE_QUOTE)
    assert rows["runway_band"].source.startswith(_YC_GUIDE)
    assert _BAND_QUOTE in rows["runway_band"].source
    assert rows["runway_band"].setting == "18 months"
    assert rows["milestone_rule"].setting.endswith("plus 6 months to raise")
    assert rows["milestone_rule"].statement.startswith("For a startup that will need a follow-on round")
    assert rows["milestone_rule"].statement.endswith("leaving months to raise the next round is ours, unverified.")
    assert rows["runway_band"].statement.endswith(
        "The default, 18 months, is the top of the guide's usual 12 to 18, so a raise lasting 12 to 18 months is "
        "within the guide's range: the flag asks which milestone it reaches, not whether it falls short."
    )
    assert "tolerance" not in rows


def test_the_defaults_are_the_deal_checks() -> None:
    """The tolerances and the runway band reuse deal_check's defaults."""
    plan = RunwayPlanInput.model_validate({"cash_on_hand": "1", "cases": [_PLAN_FLAT]})
    deal = deal_check(investment="1", pre_money="1").inputs

    assert (plan.tolerance_points, plan.tolerance_percent, plan.runway_band_months) == (
        deal.tolerance_points,
        deal.tolerance_percent,
        deal.runway_band_months,
    )
    assert plan.runway_band_months == Decimal(18)


def test_a_basis_with_its_stated_runway_or_left_at_today_is_accepted() -> None:
    landing = {"amount": "1", "lands_month": 2, "stated_runway_from": "landing", "stated_runway_months": "3"}
    today = {"amount": "1", "stated_runway_from": "today"}

    accepted = RunwayPlanInput.model_validate(
        {"cash_on_hand": "100000", "cases": [_PLAN_FLAT], "raises": [landing, today]}
    )
    assert [option.stated_runway_from for option in accepted.raises] == ["landing", "today"]


def test_the_downside_flag_counts_the_no_raise_row_and_says_so() -> None:
    """Every raise covers the milestone on both cases; only the no-raise row is covered on the plan and short on the
    downside. The flag fires (with a raise and with none given), and its words cover the no-raise row."""
    downside = {"name": "downside", "gross_burn_percent_of_plan": "150"}
    base = {
        "cash_on_hand": "100",
        "cases": [{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "10"}]}, downside],
    }
    with_raise = runway_plan(**base, raises=[{"amount": "50"}], milestones=[10])
    without = runway_plan(**base, milestones=[10])

    assert _verdict(with_raise, "plan", 1) == _verdict(with_raise, "downside", 1) == "covered"
    assert (_verdict(with_raise, "plan", 0), _verdict(with_raise, "downside", 0)) == ("covered", "short")
    assert "downside_short_where_plan_covers" in with_raise.flags and "milestone_short_on_plan" not in with_raise.flags
    assert "downside_short_where_plan_covers" in without.flags
    words = next(line.how for line in sheet_for(without).lines if line.key == "flag_downside_short_where_plan_covers")
    assert words.startswith(
        "The cash reaches a milestone on the plan but not on the downside, with the same raise or " "with none"
    )
    covered = runway_plan(**base, milestones=[6])
    assert "downside_short_where_plan_covers" not in covered.flags


def test_the_required_raise_shown_is_rounded_up_so_raising_it_covers() -> None:
    """The exact requirement is $100.0002; half-even would print $100.00, which is short. The display rounds up to
    $100.01, and a raise of that amount covers the milestone; an amount already in whole cents is shown as is."""
    fields = _plan((1, "33.3334", "0"), cash_on_hand="0", milestones=[3], months_to_raise=0)
    result = runway_plan(**fields)
    row = next(row for row in result.required if row.case == "plan" and row.lands_month == 0)

    assert row.amount is not None and row.amount.exact == Fraction(1_000_002, 10_000)
    assert row.amount.rounded == Decimal("100.01")
    printed = runway_plan(**{**fields, "raises": [{"amount": str(row.amount.rounded)}]})
    assert _verdict(printed, "plan", 1) == "covered"
    assert _verdict(runway_plan(**{**fields, "raises": [{"amount": "100.00"}]}), "plan", 1) == "short"
    whole = runway_plan(**_plan((1, "100000", "0"), cash_on_hand="0", milestones=[3], months_to_raise=0))
    (whole_row,) = (row for row in whole.required if row.case == "plan")
    assert whole_row.amount is not None and whole_row.amount.rounded == Decimal("300000.00")


def test_a_band_and_tolerances_typed_in_exponent_form_print_as_plain_numbers() -> None:
    result = runway_plan(
        **_plan(
            (1, "10", "0"),
            cash_on_hand="100",
            raises=[{"amount": "5"}],
            runway_band_months="2e1",
            stated_runway_months="10",
            tolerance_points="5E-1",
        )
    )
    rows = {row.key: row.setting for row in result.assumptions}
    words = next(line.how for line in sheet_for(result).lines if line.key == "flag_runway_below_band")

    assert rows["runway_band"] == "20 months" and rows["tolerance"] == "0.5 points; 2% relative"
    assert words.startswith("A raise lasts under 20 months on the plan")
    assert "E+" not in render_sheet(sheet_for(result))
