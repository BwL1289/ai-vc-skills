"""``deal_check``: a founder's raise checked exactly, against itself, the cap table and the deck's own figures.

Pure arithmetic: no DB, no network, nothing written. Expected values are exact fractions worked by hand:

- Company A: V = 12M, I = 3M, a 10% pool in the pre-money on 8M founder shares. r = 1/5, T = 8M/(1 - 1/5 - 1/10) =
  80M/7, P = T/10 = 8M/7, p = 12M/(8M + 8M/7) = 21/16, founders 8M/T = 7/10, effective pre-money 8M·21/16 = 10.5M.
  Runway (400k + 3M)/180k = 170/9 months against the 24 claimed.
- Company B: two post-money SAFEs (1M/10M and 1.5M/15M, 20% in all) and a pool to 10% in the pre-money of a 32M/8M
  Series A. C = 10M/(1 - 1/5) = 12.5M, T = (12.5M - 400k)/(1 - 1/5 - 1/10) = 121M/7, p = 280/121; every pre-round
  share keeps FD/T = 70/121, so the founders' 90% becomes 9/10·70/121 = 63/121, not the 72% claimed.
- Company C: a 500k note at 6% simple for 18 months (545k converts) with an 8M cap over 8M shares and a 20% discount
  in a 10M/2.5M seed. The discount wins: p = (10M - 545k/0.8)/8M = 1491/1280, founders 8M·p/12.5M = 1491/2000.
  Runway (300k + 2.5M)/(210k - 35k) = 16 months planned, 28 today; the 24 claimed is near today's gross figure, 70/3.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction

import pytest
from equity_calculator.errors import RoundHasNoPrice
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealCheckResult
from pydantic import ValidationError
from tests.support import DEAL_A, DEAL_B, DEAL_C, deal_check, pool, round_

_SEED = 20261122
_CASES = 60
_BENCHMARK = "unverified (a common benchmark, not a rule)"


def _checks(result: DealCheckResult) -> dict[str, tuple[Fraction, Fraction, str]]:
    return {check.key: (check.stated.exact, check.computed.exact, check.verdict) for check in result.checks}


def test_company_a_pool_in_the_pre_money_and_a_runway_claim_that_does_not_hold() -> None:
    result = deal_check(**DEAL_A)

    assert result.path == "pool"
    assert result.verdict == "mismatch"
    assert _checks(result) == {
        "investor_percent": (Fraction(1, 5), Fraction(1, 5), "consistent"),
        "runway_months": (Fraction(24), Fraction(170, 9), "mismatch"),
    }
    assert result.checks[1].difference.exact == Fraction(-46, 9)
    assert result.post_money.exact == 15_000_000
    assert result.price_per_share is not None and result.price_per_share.exact == Fraction(21, 16)
    assert result.effective_pre_money.exact == 10_500_000
    assert result.holder_ownership_after is not None and result.holder_ownership_after.exact == Fraction(7, 10)
    assert result.pool_ownership_after is not None and result.pool_ownership_after.exact == Fraction(1, 10)
    assert result.flags == ("pool_in_pre_money_lowers_price",)
    assert [(line.part, line.value.exact) for line in result.pre_money_split] == [
        ("existing_holders", 10_500_000),
        ("existing_pool", 0),
        ("new_pool", 1_500_000),
        ("conversions", 0),
    ]


def test_company_b_safes_and_a_pool_take_the_founders_to_63_of_121() -> None:
    result = deal_check(**DEAL_B)

    assert result.path == "round"
    assert _checks(result) == {
        "post_money": (Fraction(40_000_000), Fraction(40_000_000), "consistent"),
        "investor_percent": (Fraction(1, 5), Fraction(1, 5), "consistent"),
        "holder_percent": (Fraction(18, 25), Fraction(63, 121), "mismatch"),
    }
    assert result.pre_round_stake_kept.exact == Fraction(70, 121)
    assert result.existing_holders_ownership is not None
    assert result.existing_holders_ownership.exact == Fraction(336, 605)
    assert result.conversions_ownership is not None and result.conversions_ownership.exact == Fraction(35, 242)
    assert result.price_per_share is not None and result.price_per_share.exact == Fraction(280, 121)
    assert result.flags == ("pool_in_pre_money_lowers_price", "conversions_bought_by_pre_money")
    split = {line.part: str(line.value.rounded) for line in result.pre_money_split}
    assert split == {
        "existing_holders": "22214876.03",
        "existing_pool": "925619.83",
        "new_pool": "3074380.17",
        "conversions": "5785123.97",
    }
    assert result.effective_pre_money.exact == Fraction(2_688_000_000, 121)


def test_company_c_a_note_on_its_discount_and_runway_on_the_wrong_burn() -> None:
    result = deal_check(**DEAL_C)

    assert result.verdict == "mismatch"
    assert _checks(result) == {
        "holder_percent": (Fraction(4, 5), Fraction(1491, 2000), "mismatch"),
        "runway_months": (Fraction(24), Fraction(16), "mismatch"),
        "use_of_funds_total": (Fraction(1), Fraction(1), "consistent"),
    }
    assert result.round is not None
    (note,) = result.round.conversions
    assert (note.basis, note.converting_amount.exact, note.conversion_price.exact) == (
        "discount",
        545_000,
        Fraction(1491, 1600),
    )
    runway = {row.basis: (row.net_burn.exact, row.gross_runway.exact) for row in result.runway}
    assert runway == {"planned": (175_000, Fraction(40, 3)), "current": (100_000, Fraction(70, 3))}
    assert [row.net_runway.exact for row in result.runway if row.net_runway is not None] == [16, 28]
    assert [value.exact for value in result.use_of_funds] == [1_250_000, 750_000, 500_000]
    assert result.flags == (
        "conversions_bought_by_pre_money",
        "discount_beat_cap",
        "note_interest_converts",
        "current_burn_runway_longer",
        "runway_below_band",
    )


def test_the_plain_path_with_no_share_counts_is_i_over_v_plus_i() -> None:
    result = deal_check(investment="2000000", pre_money="8000000", holder_percent="60", stated_holder_percent="48")

    assert result.path == "plain"
    assert result.investor_ownership.exact == Fraction(1, 5)
    assert result.holder_ownership_after is not None and result.holder_ownership_after.exact == Fraction(12, 25)
    assert result.price_per_share is None and result.pre_money_split == ()
    assert result.effective_pre_money.exact == 8_000_000
    assert result.verdict == "consistent"


def test_the_plain_path_with_share_counts_prices_at_v_over_fd() -> None:
    result = deal_check(investment="2000000", pre_money="8000000", fully_diluted_shares=4_000_000)

    assert result.price_per_share is not None and result.price_per_share.exact == 2
    assert result.post_money_at_round_price is not None and result.post_money_at_round_price.exact == 10_000_000
    assert sum(line.value.exact for line in result.pre_money_split) == 8_000_000
    assert result.verdict == "not_checked"


@pytest.mark.parametrize("timing", ["pre_money", "post_money"])
def test_the_pool_path_reads_the_pool_scenario_for_the_deals_timing(timing: str) -> None:
    fields = {"fully_diluted_shares": 10_000_000, "unissued_pool_shares": 500_000, "target_pool_percent": "15"}
    worked = pool(**fields, pre_money="8000000", investment="2000000", pool_timing=timing)
    result = deal_check(**fields, pre_money="8000000", investment="2000000", pool_timing=timing)
    table = worked.pool_in_pre_money if timing == "pre_money" else worked.pool_in_post_money

    assert result.pool == worked
    assert result.price_per_share == table.price_per_share
    assert result.effective_pre_money == table.effective_pre_money
    assert result.investor_ownership.exact == table.rows[-1].ownership.exact
    assert ("pool_in_post_money_dilutes_investor" in result.flags) is (timing == "post_money")


def test_property_the_round_path_agrees_with_the_round_scenario() -> None:
    """On seeded rounds with SAFEs, both pool timings: the cap table, price and split agree with ``round``."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        fully_diluted = rng.randint(1, 20) * 1_000_000
        pre_money = rng.randint(5, 60) * 1_000_000
        fields = {
            "fully_diluted_shares": fully_diluted,
            "unissued_pool_shares": rng.randint(0, fully_diluted // 10),
            "pre_money": str(pre_money),
            "investment": str(rng.randint(1, 15) * 1_000_000),
            "target_pool_percent": str(rng.choice([0, 5, 10, 12])),
            "pool_timing": rng.choice(["pre_money", "post_money"]),
            "instruments": [
                {"kind": "safe", "purchase_amount": str(rng.randint(1, 9) * 100_000), "valuation_cap": "20000000"},
                {"kind": "safe", "purchase_amount": "250000", "discount_percent": str(rng.choice([10, 20]))},
            ],
        }
        worked = round_(**fields)
        result = deal_check(**fields)
        by_holder = {row.holder: row.ownership.exact for row in worked.rows if row.instrument is None}

        assert result.round == worked
        assert result.investor_ownership.exact == by_holder["investor"]
        assert result.pool_ownership_after is not None
        assert result.pool_ownership_after.exact == by_holder["option_pool"]
        assert sum(line.value.exact for line in result.pre_money_split) == pre_money
        assert sum(line.value.rounded for line in result.pre_money_split) == result.pre_money.rounded


@pytest.mark.parametrize(
    ("fields", "keys", "flags"),
    [
        ({"pre_money": "8000000"}, [], ()),
        ({"post_money": "10000000"}, [], ()),
        ({"stated_investor_percent": "20"}, [], ("valuation_back_solved",)),
        ({"pre_money": "8000000", "post_money": "10000000"}, ["post_money"], ()),
        (
            {"pre_money": "8000000", "post_money": "10000000", "stated_investor_percent": "25"},
            ["post_money", "investor_percent"],
            (),
        ),
        ({"post_money": "10000000", "stated_investor_percent": "20"}, ["investor_percent"], ()),
    ],
    ids=["pre", "post", "percent", "pre-and-post", "all-three", "post-and-percent"],
)
def test_the_first_valuation_given_sets_v_and_the_rest_are_checked(
    fields: dict[str, str], keys: list[str], flags: tuple[str, ...]
) -> None:
    result = deal_check(investment="2000000", **fields)

    assert result.pre_money.exact == 8_000_000
    assert [check.key for check in result.checks] == keys
    assert result.flags == flags
    assert ("back_solve" in {row.key for row in result.assumptions}) is ("valuation_back_solved" in flags)


def test_all_three_valuations_flag_a_percent_that_disagrees() -> None:
    result = deal_check(investment="2000000", pre_money="8000000", post_money="10000000", stated_investor_percent="25")

    assert _checks(result)["investor_percent"] == (Fraction(1, 4), Fraction(1, 5), "mismatch")
    assert result.checks[1].difference.exact == Fraction(-1, 20)


@pytest.mark.parametrize(
    ("stated", "verdict"),
    [("20.5", "consistent"), ("19.5", "consistent"), ("20.5000001", "mismatch"), ("19.4999999", "mismatch")],
    ids=["edge-above", "edge-below", "just-outside-above", "just-outside-below"],
)
def test_a_percent_within_the_points_tolerance_is_consistent(stated: str, verdict: str) -> None:
    result = deal_check(
        investment="2000000", pre_money="8000000", post_money="10000000", stated_investor_percent=stated
    )

    assert result.checks[-1].verdict == verdict


@pytest.mark.parametrize(
    ("post_money", "verdict"),
    [("10200000", "consistent"), ("9800000", "consistent"), ("10200001", "mismatch"), ("9799999", "mismatch")],
    ids=["edge-above", "edge-below", "just-outside-above", "just-outside-below"],
)
def test_money_within_the_relative_tolerance_is_consistent(post_money: str, verdict: str) -> None:
    """2% of the computed 10M is 200k either way, the edge included."""
    result = deal_check(investment="2000000", pre_money="8000000", post_money=post_money)

    assert result.checks[0].verdict == verdict


def test_a_zero_tolerance_needs_the_exact_figure() -> None:
    fields = {"investment": "2000000", "pre_money": "8000000", "tolerance_percent": "0", "tolerance_points": "0"}

    assert deal_check(**fields, post_money="10000000").verdict == "consistent"
    assert deal_check(**fields, post_money="10000000.01").verdict == "mismatch"


@pytest.mark.parametrize(
    ("revenue", "net", "flags"),
    [("100000", 0, ("net_burn_not_positive",)), ("150000", -50_000, ("net_burn_not_positive",)), ("0", 100_000, ())],
    ids=["net-zero", "net-negative", "no-revenue"],
)
def test_revenue_at_or_above_the_burn_leaves_no_net_runway(revenue: str, net: int, flags: tuple[str, ...]) -> None:
    result = deal_check(
        investment="2000000",
        pre_money="8000000",
        cash_on_hand="400000",
        planned_monthly_gross_burn="100000",
        planned_monthly_revenue=revenue,
        stated_runway_months="24",
        runway_band_months="1",
    )
    (row,) = result.runway

    assert row.net_burn.exact == net
    assert row.gross_runway.exact == 24
    assert (row.net_runway is None) is (net <= 0)
    assert result.flags == flags
    assert [check.key for check in result.checks] == ([] if net <= 0 else ["runway_months"])


def test_runway_is_checked_on_todays_burn_when_no_plan_is_given() -> None:
    result = deal_check(
        investment="2000000",
        pre_money="8000000",
        current_monthly_gross_burn="120000",
        current_monthly_revenue="20000",
        stated_runway_months="20",
    )

    assert _checks(result) == {"runway_months": (Fraction(20), Fraction(20), "consistent")}
    assert result.flags == ()


def test_a_pool_already_large_enough_is_flagged_only_with_a_target() -> None:
    with_target = deal_check(
        investment="2000000",
        pre_money="8000000",
        fully_diluted_shares=10_000_000,
        unissued_pool_shares=2_000_000,
        target_pool_percent="10",
    )
    no_target = deal_check(**DEAL_C)

    assert "pool_already_large_enough" in with_target.flags
    assert no_target.round is not None and no_target.round.pool_already_large_enough is True
    assert "pool_already_large_enough" not in no_target.flags


def test_amount_lines_are_checked_against_the_raise() -> None:
    result = deal_check(
        investment="2500000", pre_money="10000000", use_of_funds=[{"amount": "1500000"}, {"amount": "900000"}]
    )

    assert _checks(result) == {"use_of_funds_total": (Fraction(2_400_000), Fraction(2_500_000), "mismatch")}
    assert result.use_of_funds_percent_total is not None
    assert result.use_of_funds_percent_total.exact == Fraction(24, 25)


def test_percent_lines_add_up_to_the_raise_to_the_cent() -> None:
    result = deal_check(investment="1000000", pre_money="4000000", use_of_funds=[{"percent": "33.333"}] * 3)
    total = result.use_of_funds_total

    assert total is not None
    assert sum(value.rounded for value in result.use_of_funds) == total.rounded
    assert result.checks[0].verdict == "consistent"


def test_dilution_above_the_band_is_a_question_not_a_mismatch() -> None:
    result = deal_check(investment="4000000", pre_money="8000000", stated_investor_percent="33.33")

    assert result.flags == ("dilution_above_band",)
    assert result.verdict == "consistent"


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({}, "give pre_money, post_money or stated_investor_percent"),
        ({"post_money": "2000000"}, "post_money must be above investment"),
        ({"pre_money": "8000000", "target_pool_percent": "10"}, "fully_diluted_shares is needed"),
        ({"pre_money": "8000000", "unissued_pool_shares": 5}, "unissued_pool_shares needs fully_diluted_shares"),
        (
            {"pre_money": "8000000", "fully_diluted_shares": 5, "unissued_pool_shares": 5},
            "unissued_pool_shares must be below fully_diluted_shares",
        ),
        ({"pre_money": "8000000", "stated_holder_percent": "50"}, "stated_holder_percent needs holder_percent"),
        ({"pre_money": "8000000", "stated_runway_months": "20"}, "stated_runway_months needs"),
        ({"pre_money": "8000000", "planned_monthly_revenue": "5"}, "planned_monthly_revenue needs"),
        ({"pre_money": "8000000", "current_monthly_revenue": "5"}, "current_monthly_revenue needs"),
        (
            {"pre_money": "8000000", "use_of_funds": [{"amount": "5"}, {"percent": "5"}]},
            "every use_of_funds line as an amount or every one as a percent",
        ),
        ({"pre_money": "8000000", "use_of_funds": [{"amount": "5", "percent": "5"}]}, "give exactly one of amount"),
        (
            {"stated_investor_percent": "20", "pool_timing": "post_money"},
            "a stated_investor_percent with no valuation needs pool_timing pre_money",
        ),
        (
            {"stated_investor_percent": "7", "fully_diluted_shares": 100, "target_pool_percent": "10"},
            "which no decimal holds exactly",
        ),
        (
            {"pre_money": "1000000", "fully_diluted_shares": 100, "target_pool_percent": "40"},
            "target_pool_percent must be below pre_money / (pre_money + investment)",
        ),
        (
            {
                "pre_money": "8000000",
                "fully_diluted_shares": 100,
                "instruments": [{"kind": "safe", "purchase_amount": "1", "valuation_cap": "1.5"}] * 2,
            },
            "at their caps they would own the whole company",
        ),
    ],
    ids=[
        "no-valuation",
        "post-below-raise",
        "pool-without-shares",
        "unissued-without-shares",
        "unissued-is-everything",
        "stated-holder-alone",
        "runway-without-burn",
        "planned-revenue-alone",
        "current-revenue-alone",
        "mixed-funds",
        "funds-line-both",
        "percent-with-post-pool",
        "back-solve-not-a-decimal",
        "nested-pool-too-big",
        "nested-caps-over-100",
    ],
)
def test_each_refusal_names_its_fields(fields: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=re.escape(message)):
        DealCheckInput.model_validate({"investment": "2000000", **fields})


def test_a_back_solved_pre_money_that_no_decimal_holds_still_works_on_the_plain_path() -> None:
    result = deal_check(investment="3000000", stated_investor_percent="7")

    assert result.pre_money.exact == Fraction(279_000_000, 7)
    assert result.investor_ownership.exact == Fraction(7, 100)


def test_a_nested_round_with_no_price_raises_the_rounds_own_error() -> None:
    inputs = DealCheckInput.model_validate(
        {
            "fully_diluted_shares": 10_000_000,
            "unissued_pool_shares": 500_000,
            "pre_money": "1000000",
            "investment": "1000000",
            "target_pool_percent": "25",
            "instruments": [{"kind": "safe", "purchase_amount": "250000", "discount_percent": "50"}],
        }
    )

    with pytest.raises(RoundHasNoPrice):
        compute(inputs)


def test_assumption_rows_appear_only_when_used_and_bands_are_benchmarks() -> None:
    bare = {row.key: row for row in deal_check(investment="2000000", pre_money="8000000").assumptions}
    rows = deal_check(**DEAL_C).assumptions
    full = {row.key: row for row in rows}

    assert list(bare) == ["post_money_rule", "effective_pre_money", "dilution_band"]
    assert "Post-Money Safe User Guide" in bare["post_money_rule"].source
    assert bare["dilution_band"].source == _BENCHMARK
    assert full["runway_band"].source == _BENCHMARK
    assert full["runway_rule"].source.startswith("unverified")
    assert {"holder_scaling", "tolerance", "use_of_funds_rule", "note_interest", "pool_timing"} <= set(full)
    assert len(full) == len(rows)
