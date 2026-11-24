"""``pool_plan``: the pool a hiring plan needs to the next round beside the term sheet's, worked by the pool code.

Company CP (``tests.support.POOL_PLAN_CP``, made up) is worked by hand in exact fractions: G = 1,400,000 shares of
grants by month 18, FD = 10,000,000, U = 1,000,000, V = $16,000,000, I = $4,000,000, so
t_plan = G·V/((V + I)(FD - U + G)) = 22,400,000,000,000/208,000,000,000,000 = 7/65, P = G - U = 400,000 and
p = V/(FD + P) = 16,000,000/10,400,000 = 20/13. At the requested 15%, r = 1/5 and
P = (3/20·FD - 4/5·U)/(1 - 1/5 - 3/20) = 700,000/(13/20) = 14,000,000/13, p = 16,000,000/(144,000,000/13) = 13/9.
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.pool import compute_pool
from equity_calculator.schemas.equity import PoolInput
from equity_calculator.schemas.equity_pool_plan import MAX_HIRES, PoolPlanFlag, PoolPlanInput
from pydantic import ValidationError
from tests.support import POOL_PLAN_CP, POOL_PLAN_CP_HIRES, pool_plan

_SEED = 20261124
_RANDOM_CASES = 200


def _with(**changes: object) -> dict[str, object]:
    return {**POOL_PLAN_CP, **changes}


def _refusal(fields: dict[str, object]) -> str:
    with pytest.raises(ValidationError) as caught:
        PoolPlanInput.model_validate(fields)
    return str(caught.value)


def test_company_cp_plan_column_is_worked_exactly() -> None:
    result = pool_plan(**POOL_PLAN_CP)
    plan = result.plan

    assert result.grant_unit == "shares"
    assert (result.hires_counted, result.hires_left_out) == (5, 1)
    assert plan.target_pool.exact == Fraction(7, 65)
    assert plan.grant_shares.exact == 1_400_000
    assert plan.cap_table.new_pool_shares.exact == 400_000
    assert plan.cap_table.price_per_share.exact == Fraction(20, 13)
    assert plan.cap_table.investor_shares.exact == 2_600_000
    assert plan.cap_table.total_shares.exact == 13_000_000
    assert plan.cap_table.effective_pre_money.exact == Fraction(180_000_000, 13)
    assert plan.pool_left_at_next_round.exact == 0
    assert plan.founders_ownership is not None and plan.founders_ownership.exact == Fraction(7, 13)
    assert result.investor_fraction.exact == Fraction(1, 5)


def test_company_cp_requested_column_and_the_difference_are_worked_exactly() -> None:
    result = pool_plan(**POOL_PLAN_CP)
    requested, difference = result.requested, result.requested_minus_plan

    assert requested.target_pool.exact == Fraction(3, 20)
    assert requested.cap_table.new_pool_shares.exact == Fraction(14_000_000, 13)
    assert requested.cap_table.price_per_share.exact == Fraction(13, 9)
    assert requested.cap_table.effective_pre_money.exact == 13_000_000
    assert requested.pool_left_at_next_round.exact == Fraction(8_800_000, 13)
    assert requested.founders_ownership is not None and requested.founders_ownership.exact == Fraction(91, 180)

    assert difference.target_pool.exact == Fraction(3, 20) - Fraction(7, 65)
    assert difference.new_pool_shares.exact == Fraction(14_000_000, 13) - 400_000
    assert difference.price_per_share.exact == Fraction(13, 9) - Fraction(20, 13)
    assert difference.effective_pre_money.exact == Fraction(-11_000_000, 13)
    assert difference.effective_pre_money.rounded == Decimal("-846153.85")
    assert difference.founders_ownership is not None
    assert difference.founders_ownership.exact == Fraction(-77, 2340)
    assert difference.pool_left_at_next_round.exact == Fraction(8_800_000, 13)
    assert result.flags == ("hires_after_next_round_ignored", "requested_above_plan")


def test_the_requested_column_is_the_pool_scenario_s_own_pre_money_table() -> None:
    """No formula of the shuffle is worked a second way: the requested column is ``compute_pool``'s table."""
    result = pool_plan(**POOL_PLAN_CP)
    pool = compute_pool(
        PoolInput(
            fully_diluted_shares=10_000_000,
            unissued_pool_shares=1_000_000,
            pre_money=Decimal(16_000_000),
            investment=Decimal(4_000_000),
            target_pool_percent=Decimal(15),
        )
    )

    assert result.requested.cap_table == pool.pool_in_pre_money


def test_a_plan_that_fits_today_s_pool_tops_up_nothing_and_keeps_the_pool_whole() -> None:
    """G = 1,400,000 <= U = 1,500,000: P = 0, p = V/FD = 8/5, and 100,000 of today's pool is left at the next round.
    t_plan is the grants' share of the plan column's own total: G·V/((V + I)·FD) = 1,400,000 × 16,000,000/(20,000,000 ×
    10,000,000) = 14/125, which is G/T = 1,400,000/12,500,000."""
    result = pool_plan(**_with(unissued_pool_shares=1_500_000, founder_shares=None))
    plan = result.plan

    assert plan.cap_table.new_pool_shares.exact == 0
    assert plan.cap_table.price_per_share.exact == Fraction(8, 5)
    assert plan.cap_table.pool_already_large_enough
    assert plan.pool_left_at_next_round.exact == 100_000
    assert plan.target_pool.exact == Fraction(14, 125)
    assert plan.target_pool.exact == plan.grant_shares.exact / plan.cap_table.total_shares.exact
    assert "plan_fits_current_pool" in result.flags
    assert plan.founders_ownership is None and result.requested_minus_plan.founders_ownership is None


def test_grants_as_percents_set_the_plan_s_pool_to_their_sum_and_fill_it_exactly() -> None:
    """2 + 1.5 + 1.5 + 3 = 8%: t_plan = 2/25, P = (0.08·FD - 0.8·U)/0.72 = 5,000,000/9, T = 475,000,000/36, and the
    grants take 8% of T = 19,000,000/18 shares, exactly U + P."""
    hires = [
        {"role": "Engineer", "start_month": 2, "grant_percent": "2"},
        {"role": "Engineer", "start_month": 5, "grant_percent": "1.5"},
        {"role": "Account executive", "start_month": 8, "grant_percent": "1.5"},
        {"role": "VP sales", "start_month": 18, "grant_percent": "3"},
    ]
    result = pool_plan(**_with(unissued_pool_shares=500_000, hires=hires))
    plan = result.plan

    assert result.grant_unit == "percent"
    assert result.hires_counted == len(hires)
    assert plan.target_pool.exact == Fraction(2, 25)
    assert plan.cap_table.new_pool_shares.exact == Fraction(5_000_000, 9)
    assert plan.cap_table.price_per_share.exact == Fraction(144, 95)
    assert plan.grant_shares.exact == Fraction(19_000_000, 18)
    assert plan.pool_left_at_next_round.exact == 0
    assert result.requested.grant_shares.exact == Fraction(2, 25) * result.requested.cap_table.total_shares.exact


@pytest.mark.parametrize(
    ("unissued", "shares", "percent", "requested", "side"),
    [
        (1_500_000, 562_500, "4.5", "4.7", "requested_above_plan"),
        (1_500_000, 562_500, "4.5", "4.3", "requested_below_plan"),
        (200_000, 1_400_000, "10", "12", "requested_above_plan"),
    ],
    ids=["fits-ask-above", "fits-ask-below", "tops-up"],
)
def test_the_same_plan_in_shares_and_as_percents_gives_the_same_plan_target(
    unissued: int, shares: int, percent: str, requested: str, side: str
) -> None:
    """The same grants given as shares or as their percent of the plan column's total give one t_plan, one cap table
    and one flag, whether they fit today's pool (562,500 of T = 12,500,000 is 4.5%) or need a top-up (1,400,000 of
    T = 14,000,000 is 10%, with P = 1,200,000). The requested column is not compared beyond its target: there, grants
    as percents take their percent of that column's own total, by design."""
    terms = {
        "fully_diluted_shares": 10_000_000,
        "unissued_pool_shares": unissued,
        "pre_money": "12000000",
        "investment": "3000000",
        "requested_pool_percent": requested,
        "next_round_month": 15,
    }
    by_shares = pool_plan(**terms, hires=[{"role": "Engineer", "start_month": 2, "grant_shares": shares}])
    by_percent = pool_plan(**terms, hires=[{"role": "Engineer", "start_month": 2, "grant_percent": percent}])

    assert by_shares.plan.target_pool.exact == by_percent.plan.target_pool.exact == Fraction(percent) / 100
    assert by_shares.plan.cap_table == by_percent.plan.cap_table
    assert by_shares.plan.grant_shares.exact == by_percent.plan.grant_shares.exact == shares
    assert by_shares.requested_minus_plan.target_pool == by_percent.requested_minus_plan.target_pool
    assert by_shares.flags == by_percent.flags
    assert side in by_shares.flags


def test_a_hire_starting_in_the_next_round_s_month_counts_and_one_after_it_does_not() -> None:
    hires = [
        {"role": "Engineer", "start_month": 18, "grant_shares": 300_000},
        {"role": "Engineer", "start_month": 19, "grant_shares": 300_000},
    ]
    result = pool_plan(**_with(hires=hires))

    assert (result.hires_counted, result.hires_left_out) == (1, 1)
    assert result.plan.grant_shares.exact == 300_000


def test_no_hire_before_the_next_round_needs_no_pool() -> None:
    hires = [{"role": "Engineer", "start_month": 30, "grant_shares": 300_000}]
    result = pool_plan(**_with(hires=hires))

    assert result.plan.target_pool.exact == 0
    assert result.plan.cap_table.new_pool_shares.exact == 0
    assert result.flags == (
        "no_hires_before_next_round",
        "hires_after_next_round_ignored",
        "plan_fits_current_pool",
        "requested_above_plan",
    )


def test_a_requested_pool_below_the_plan_runs_short_before_the_next_round() -> None:
    """5% is met by today's 1,000,000-share pool (needed P < 0), so the 1,400,000 shares of grants leave it 400,000
    short at the next round."""
    result = pool_plan(**_with(requested_pool_percent="5"))

    assert result.requested.cap_table.new_pool_shares.exact == 0
    assert result.requested.pool_left_at_next_round.exact == -400_000
    assert result.flags == ("hires_after_next_round_ignored", "requested_met_by_current_pool", "requested_below_plan")


@pytest.mark.parametrize(("percent", "side"), [("11", "requested_below_plan"), ("11.5", "requested_above_plan")])
def test_when_today_s_pool_holds_the_plan_an_ask_it_also_meets_moves_nothing(percent: str, side: str) -> None:
    """U = 1,500,000 holds the 1,400,000 shares of grants (t_plan = 14/125, 11.2%), and 11% or 11.5% is met by today's
    pool too: no top-up either way, the same price, and 100,000 shares left in both columns."""
    result = pool_plan(**_with(unissued_pool_shares=1_500_000, requested_pool_percent=percent))

    assert result.flags == (
        "hires_after_next_round_ignored",
        "plan_fits_current_pool",
        "requested_met_by_current_pool",
        side,
    )
    assert result.plan.cap_table.new_pool_shares.exact == result.requested.cap_table.new_pool_shares.exact == 0
    assert result.plan.pool_left_at_next_round.exact == result.requested.pool_left_at_next_round.exact == 100_000
    assert result.requested_minus_plan.effective_pre_money.exact == 0
    assert result.requested_minus_plan.price_per_share.exact == 0


def test_flags_come_in_the_order_the_literal_lists_them() -> None:
    order = get_args(PoolPlanFlag)
    for changes in ({}, {"requested_pool_percent": "5"}, {"unissued_pool_shares": 1_500_000, "founder_shares": None}):
        flags = pool_plan(**_with(**changes)).flags
        assert list(flags) == sorted(flags, key=order.index)


def test_the_assumptions_name_the_plan_s_conventions_and_reuse_the_pool_s() -> None:
    result = pool_plan(**POOL_PLAN_CP)
    pool = compute_pool(
        PoolInput(
            fully_diluted_shares=10_000_000,
            pre_money=Decimal(16_000_000),
            investment=Decimal(4_000_000),
            target_pool_percent=Decimal(15),
        )
    )
    keys = [item.key for item in result.assumptions]

    assert keys == [
        "pool_timing",
        "target_pool",
        "plan_pool",
        "next_round_cutoff",
        "grant_unit",
        "price_basis",
        "share_rounding",
        "difference",
        "money_split",
    ]
    shared = {item.key: item for item in pool.assumptions}
    for key in ("target_pool", "price_basis", "money_split"):
        assert next(item for item in result.assumptions if item.key == key) == shared[key], key
    assert next(item for item in result.assumptions if item.key == "next_round_cutoff").setting == "month 18"


def test_seeded_plans_size_the_pool_to_exactly_the_grants_and_reuse_the_pool_code() -> None:
    """For random plans, the plan's pool after the round is exactly G when G > U (P = G - U, nothing left), today's
    pool when G <= U (P = 0), t_plan is always the grants' share of the plan column's own total, and the requested
    column is always ``compute_pool``'s pre-money table."""
    rng = random.Random(_SEED)
    for _ in range(_RANDOM_CASES):
        fully_diluted = rng.randrange(1_000_000, 50_000_000)
        unissued = rng.randrange(0, fully_diluted // 5)
        pre_money = rng.randrange(1_000_000, 100_000_000)
        investment = rng.randrange(100_000, 30_000_000)
        ceiling = Fraction(pre_money, pre_money + investment) * 100
        requested = Decimal(rng.randrange(1, max(2, int(ceiling) - 1)))
        hires = [
            {"role": f"Hire {index}", "start_month": rng.randrange(0, 40), "grant_shares": rng.randrange(1, 900_000)}
            for index in range(rng.randrange(1, 12))
        ]
        next_round = rng.randrange(1, 40)
        result = pool_plan(
            fully_diluted_shares=fully_diluted,
            unissued_pool_shares=unissued,
            pre_money=str(pre_money),
            investment=str(investment),
            requested_pool_percent=str(requested),
            next_round_month=next_round,
            hires=hires,
        )
        grants = sum(hire["grant_shares"] for hire in hires if int(str(hire["start_month"])) <= next_round)
        plan = result.plan.cap_table

        assert result.plan.target_pool.exact == Fraction(grants) / plan.total_shares.exact
        if grants > unissued:
            assert plan.new_pool_shares.exact == grants - unissued
            assert result.plan.pool_left_at_next_round.exact == 0
            option_pool = next(row.ownership.exact for row in plan.rows if row.group == "option_pool")
            assert option_pool == result.plan.target_pool.exact
        else:
            assert plan.new_pool_shares.exact == 0
            assert "plan_fits_current_pool" in result.flags
            assert result.plan.pool_left_at_next_round.exact == unissued - grants
        pool = compute_pool(
            PoolInput(
                fully_diluted_shares=fully_diluted,
                unissued_pool_shares=unissued,
                pre_money=Decimal(pre_money),
                investment=Decimal(investment),
                target_pool_percent=requested,
            )
        )
        assert result.requested.cap_table == pool.pool_in_pre_money


@pytest.mark.parametrize(
    ("changes", "fragment"),
    [
        ({"hires": []}, "no_hiring_plan_given"),
        (
            {
                "hires": [
                    {"role": "Engineer", "start_month": 1, "grant_shares": 100_000},
                    {"role": "Designer", "start_month": 2, "grant_percent": "1"},
                ]
            },
            "grants_mixed_units",
        ),
        (
            {"hires": [{"role": "Engineer", "start_month": 1, "grant_shares": 100_000, "grant_percent": "1"}]},
            "exactly one of grant_shares, grant_percent",
        ),
        ({"hires": [{"role": "Engineer", "start_month": 1}]}, "exactly one of grant_shares, grant_percent"),
        ({"hires": [{"role": "=SUM(A1)", "start_month": 1, "grant_shares": 1}]}, "starts with a letter or a digit"),
        ({"hires": [{"role": "Engi\tneer", "start_month": 1, "grant_shares": 1}]}, "holds only"),
        ({"hires": [{"role": "Engineer\x07x", "start_month": 1, "grant_shares": 1}]}, "holds only"),
        ({"hires": [{"role": "E" * 41, "start_month": 1, "grant_shares": 1}]}, "at most 40 characters"),
        ({"hires": [{"role": "   ", "start_month": 1, "grant_shares": 1}]}, "role is empty"),
        ({"hires": [{"role": "Engineer", "start_month": 121, "grant_shares": 1}]}, "less than or equal to 120"),
        ({"hires": [{"role": "Engineer", "start_month": "3", "grant_shares": 1}]}, "valid integer"),
        ({"hires": [{"role": "Engineer", "start_month": 1, "grant_shares": 0}]}, "greater than 0"),
        ({"next_round_month": 0}, "greater than or equal to 1"),
        ({"unissued_pool_shares": 10_000_000}, "unissued_pool_shares must be below fully_diluted_shares"),
        ({"founder_shares": 9_000_001}, "founder_shares must be at most"),
        ({"requested_pool_percent": "80"}, "requested_pool_percent"),
        (
            {
                "hires": [
                    {"role": "Engineer", "start_month": 1, "grant_percent": "50"},
                    {"role": "Engineer", "start_month": 2, "grant_percent": "30"},
                ]
            },
            "add up to 80.0000%",
        ),
    ],
)
def test_inputs_with_no_plan_or_no_price_are_refused(changes: dict[str, object], fragment: str) -> None:
    assert fragment in _refusal(_with(**changes))


def test_percents_of_hires_after_the_next_round_are_not_held_to_the_price_limit() -> None:
    hires = [
        {"role": "Engineer", "start_month": 1, "grant_percent": "2"},
        {"role": "Engineer", "start_month": 60, "grant_percent": "79"},
    ]
    result = pool_plan(**_with(hires=hires))

    assert result.plan.target_pool.exact == Fraction(1, 50)


def test_at_most_forty_hires() -> None:
    hire = POOL_PLAN_CP_HIRES[0]

    assert pool_plan(**_with(hires=[hire] * MAX_HIRES)).hires_counted == MAX_HIRES
    assert "at most 40 items" in _refusal(_with(hires=[hire] * (MAX_HIRES + 1)))
