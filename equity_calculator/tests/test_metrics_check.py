"""``metrics_check``: a founder's traction metrics worked exactly from their parts, and each stated figure checked.

Pure arithmetic: no DB, no network, nothing written. Expected values are exact fractions worked by hand:

- Company AM, 12 months of MRR: S = 80k, N = 24k, E = 6k, C = 2k, X = 8k, so ending MRR 100k and ARR 12·100k =
  1.2M, while 12 × last month's 125k (25k of it implementation fees) is the 1.5M the deck calls ARR. Net revenue
  retention (80k + 6k - 10k)/80k = 19/20, not the 125% of ending over starting MRR; gross 70k/80k = 7/8. Net new ARR
  12·20k = 240k, so the burn multiple is 1.8M/240k = 15/2, not 1.8M/(12·24k) = 25/4 on new ARR only.
- Company AN, one month: logo churn 12/400 = 3/100, gross revenue churn 1.5k/50k = 3/100, net (1.5k - 500)/50k =
  1/50, so an unlabelled 2% holds only as net revenue churn. CAC payback 36k/(5k·3/4) = 48/5 months on gross margin,
  36/5 on revenue: the deck's 7.2 is the revenue figure, the model's 9.6 the margin one. Blended CAC 36k/45 = 800,
  paid 36k/20 = 1,800.
"""

from __future__ import annotations

import random
import re
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.assumptions_metrics_check import (
    BESSEMER_SOURCE,
    BURN_MULTIPLE_BAND_QUOTE,
    NET_REVENUE_CHURN_BAND_QUOTE,
    PAYBACK_BAND_QUOTE,
    SACKS_SOURCE,
    SKOK_SOURCE,
)
from equity_calculator.schemas.equity_metrics_check import (
    MAX_PERIOD_MONTHS,
    MetricsCheckInput,
    MetricsCheckResult,
    MetricsFlag,
)
from pydantic import ValidationError
from tests.support import METRICS_AM, METRICS_AN_DECK, METRICS_AN_MODEL, metrics_check

_SEED = 20261123
_CASES = 200
_MONTHS_PER_YEAR = 12
_BENCHMARK = "(a benchmark, not a rule)"
# The three benchmark lines, typed out here from the pages read so a change to a quote in the code fails this test.
_PAYBACK_WORDS = (
    "For cloud companies selling into SMB-focused accounts, you should target CAC payback <12 months; for "
    "mid-market-focused accounts, target CAC payback <18 months; and for enterprise-focused accounts, target <24 "
    "months."
)
_BURN_WORDS = (
    "If extraordinary investment (3x burn or more) is required to deliver that growth, it’s an indicator that "
    "product-market fit isn’t quite what it appears to be"
)
_CHURN_WORDS = (
    "If your Net Revenue Churn is high (above 2% per month) it is an indicator that there is something wrong in your "
    "business."
)


def _checks(result: MetricsCheckResult) -> dict[tuple[str, str | None], tuple[Fraction, Fraction, str]]:
    return {
        (check.key, check.basis): (check.stated.exact, check.computed.exact, check.verdict) for check in result.checks
    }


def _exact(result: MetricsCheckResult, name: str) -> Fraction:
    value = getattr(result, name)
    assert value is not None, name
    return value.exact


def test_company_am_a_run_rate_called_arr_new_customers_in_nrr_and_a_multiple_on_new_arr() -> None:
    result = metrics_check(**METRICS_AM)

    assert _exact(result, "starting_arr") == 960_000
    assert _exact(result, "ending_arr") == 1_200_000
    assert _exact(result, "net_new_arr") == 240_000
    assert _exact(result, "new_arr") == 288_000
    assert _exact(result, "month_arr") == 1_200_000
    assert _exact(result, "run_rate") == 1_500_000
    assert result.arr_basis == "movement"
    assert _exact(result, "gross_revenue_retention") == Fraction(7, 8)
    assert _exact(result, "net_revenue_retention") == Fraction(19, 20)
    assert _exact(result, "gross_revenue_churn") == Fraction(1, 8)
    assert _exact(result, "net_revenue_churn") == Fraction(1, 20)
    assert _exact(result, "burn_multiple") == Fraction(15, 2)
    assert _exact(result, "burn_multiple_on_new_arr") == Fraction(25, 4)
    assert _checks(result) == {
        ("arr", None): (Fraction(1_500_000), Fraction(1_200_000), "mismatch"),
        ("nrr", None): (Fraction(5, 4), Fraction(19, 20), "mismatch"),
        ("burn_multiple", None): (Fraction(25, 4), Fraction(15, 2), "mismatch"),
    }
    assert result.flags == (
        "stated_arr_matches_run_rate",
        "run_rate_includes_non_recurring",
        "stated_nrr_includes_new",
        "stated_burn_multiple_uses_new_not_net_arr",
        "burn_multiple_above_band",
    )
    assert result.verdict == "mismatch"
    assert result.logo_churn is None and result.blended_cac is None and result.concentration is None


def test_company_an_an_unlabelled_churn_and_a_payback_the_deck_and_model_state_differently() -> None:
    deck = metrics_check(**METRICS_AN_DECK)
    model = metrics_check(**METRICS_AN_MODEL)

    assert _exact(deck, "logo_churn") == Fraction(3, 100)
    assert _exact(deck, "logo_retention") == Fraction(97, 100)
    assert _exact(deck, "gross_revenue_churn") == Fraction(3, 100)
    assert _exact(deck, "net_revenue_churn") == Fraction(1, 50)
    assert _exact(deck, "blended_cac") == 800
    assert _exact(deck, "paid_cac") == 1_800
    assert _exact(deck, "cac_payback_months") == Fraction(48, 5)
    assert _exact(deck, "revenue_payback_months") == Fraction(36, 5)
    assert _exact(deck, "payback_band_months") == _MONTHS_PER_YEAR
    assert _checks(deck) == {
        ("churn", "logo"): (Fraction(1, 50), Fraction(3, 100), "mismatch"),
        ("churn", "gross_revenue"): (Fraction(1, 50), Fraction(3, 100), "mismatch"),
        ("churn", "net_revenue"): (Fraction(1, 50), Fraction(1, 50), "consistent"),
        ("cac_payback", None): (Fraction(36, 5), Fraction(48, 5), "mismatch"),
    }
    assert deck.flags == ("churn_basis_unlabelled", "stated_payback_not_margin_adjusted")
    assert deck.verdict == "mismatch"
    assert _checks(model) == {("cac_payback", None): (Fraction(48, 5), Fraction(48, 5), "consistent")}
    assert model.flags == ()
    assert model.verdict == "consistent"


def _random_input(rng: random.Random) -> dict[str, object]:
    start = rng.randint(1, 10**6)
    contraction = rng.randint(0, start)
    churned = rng.randint(0, start - contraction)
    new = rng.randint(1, 10**6)
    expansion = rng.randint(0, 10**5)
    return {
        "period_months": rng.randint(1, MAX_PERIOD_MONTHS),
        "starting_recurring": str(start),
        "new_recurring": str(new),
        "expansion_recurring": str(expansion),
        "contraction_recurring": str(contraction),
        "churned_recurring": str(churned),
        "sales_marketing_spend": str(rng.randint(1, 10**7)),
        "gross_margin_percent": str(rng.randint(1, 100)),
        "net_burn": str(rng.randint(-(10**6), 10**7)),
    }


def test_property_the_metrics_hold_their_identities() -> None:
    """NRR - GRR = E/S, gross churn = 1 - GRR, net churn = 1 - NRR, end - start ARR = net new ARR, and the margin
    payback times the margin is the revenue payback, on seeded random inputs."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        fields = _random_input(rng)
        result = metrics_check(**fields)
        start = Fraction(str(fields["starting_recurring"]))
        margin = Fraction(str(fields["gross_margin_percent"])) / 100
        grr, nrr = _exact(result, "gross_revenue_retention"), _exact(result, "net_revenue_retention")

        assert nrr - grr == Fraction(str(fields["expansion_recurring"])) / start
        assert _exact(result, "gross_revenue_churn") == 1 - grr
        assert _exact(result, "net_revenue_churn") == 1 - nrr
        assert _exact(result, "ending_arr") - _exact(result, "starting_arr") == _exact(result, "net_new_arr")
        assert _exact(result, "cac_payback_months") * margin == _exact(result, "revenue_payback_months")
        net_new, burn = _exact(result, "net_new_arr"), Fraction(str(fields["net_burn"]))
        if net_new > 0 and burn > 0:
            assert _exact(result, "burn_multiple") == burn / net_new
        else:
            assert result.burn_multiple is None


def test_annual_and_monthly_units_give_the_same_business() -> None:
    monthly = metrics_check(**{**METRICS_AN_DECK, "period_months": 3})
    annual = metrics_check(
        **{
            **METRICS_AN_DECK,
            "period_months": 3,
            "recurring_unit": "annual",
            **{
                name: str(Fraction(str(METRICS_AN_DECK[name])) * _MONTHS_PER_YEAR)
                for name in (
                    "starting_recurring",
                    "new_recurring",
                    "expansion_recurring",
                    "contraction_recurring",
                    "churned_recurring",
                )
            },
        }
    )

    for name in ("ending_arr", "net_new_arr", "gross_revenue_retention", "net_revenue_retention", "cac_payback_months"):
        assert _exact(annual, name) == _exact(monthly, name), name


def test_the_starting_customers_movements_drive_retention_and_the_totals_drive_arr() -> None:
    totals = {"period_months": 6, "starting_recurring": "1000", "new_recurring": "300", "expansion_recurring": "200"}
    totals |= {"contraction_recurring": "50", "churned_recurring": "100"}
    plain = metrics_check(**totals)
    cohort = metrics_check(**totals, cohort_expansion_recurring="80", cohort_churned_recurring="60")

    assert _exact(cohort, "ending_arr") == _exact(plain, "ending_arr") == 12 * 1350
    assert _exact(plain, "net_revenue_retention") == Fraction(1050, 1000)
    # Contraction left out of the cohort fields falls back to the period's total.
    assert _exact(cohort, "net_revenue_retention") == Fraction(1000 + 80 - 50 - 60, 1000)
    assert _exact(cohort, "gross_revenue_retention") == Fraction(1000 - 50 - 60, 1000)
    rows = {row.key: row for row in cohort.assumptions}
    # The setting names which movements are the starting customers' own and which fell back to the totals.
    assert (
        rows["cohort_rule"].setting == "the starting customers' own expansion and churn; the period's total contraction"
    )
    assert {row.key: row for row in plain.assumptions}["cohort_rule"].setting == "the period's totals"


def test_the_periods_losses_may_exceed_the_start_when_customers_won_in_it_leave() -> None:
    """A small start and fast growth over 12 months: 15k lost in total, 5k of it from the 10k there at the start and
    10k from customers won in the period. ARR at the end 12(10k + 100k - 15k) = 1.14M; gross retention 5k/10k."""
    result = metrics_check(
        period_months=12,
        starting_recurring="10000",
        new_recurring="100000",
        churned_recurring="15000",
        cohort_churned_recurring="5000",
    )

    assert _exact(result, "ending_arr") == 1_140_000
    assert _exact(result, "gross_revenue_retention") == Fraction(1, 2)
    assert _exact(result, "net_revenue_retention") == Fraction(1, 2)


def test_a_first_paying_period_starts_from_zero() -> None:
    """Nothing at the start, 5k new MRR over a quarter and 1k of it lost again: ARR 12 x 4k = 48k, all of it net new,
    so the burn multiple is 72k/48k = 3/2. No retention or churn is worked, with nothing at the start to divide by."""
    result = metrics_check(
        period_months=3,
        starting_recurring="0",
        new_recurring="5000",
        churned_recurring="1000",
        cohort_churned_recurring="0",
        net_burn="72000",
        stated_arr="48000",
        stated_burn_multiple="1.5",
    )

    assert _exact(result, "starting_arr") == 0
    assert _exact(result, "ending_arr") == _exact(result, "net_new_arr") == 48_000
    assert _exact(result, "burn_multiple") == Fraction(3, 2)
    assert result.gross_revenue_retention is None and result.net_revenue_retention is None
    assert result.gross_revenue_churn is None and result.net_revenue_churn is None
    assert _checks(result) == {
        ("arr", None): (Fraction(48_000), Fraction(48_000), "consistent"),
        ("burn_multiple", None): (Fraction(3, 2), Fraction(3, 2), "consistent"),
    }
    assert result.verdict == "consistent"
    assert "stated_nrr_includes_new" not in result.flags


def test_a_stated_arr_is_checked_against_the_latest_month_when_no_movement_is_given() -> None:
    result = metrics_check(
        period_months=1, month_total_revenue="100000", month_usage_revenue="10000", stated_arr="1.2e6"
    )

    assert result.arr_basis == "month"
    assert result.ending_arr is None
    assert _checks(result) == {("arr", None): (Fraction(1_200_000), Fraction(1_080_000), "mismatch")}
    assert result.flags == ("stated_arr_matches_run_rate", "run_rate_includes_non_recurring")


@pytest.mark.parametrize(
    ("stated", "verdict"),
    [("94.5", "consistent"), ("95.5", "consistent"), ("94.49", "mismatch"), ("95.51", "mismatch")],
)
def test_a_percent_within_the_points_tolerance_is_consistent_edge_included(stated: str, verdict: str) -> None:
    result = metrics_check(**{**METRICS_AM, "stated_nrr_percent": stated})

    assert _checks(result)[("nrr", None)][2] == verdict


@pytest.mark.parametrize(
    ("stated", "verdict"),
    [("1176000", "consistent"), ("1224000", "consistent"), ("1175999", "mismatch"), ("1224001", "mismatch")],
)
def test_money_within_the_relative_tolerance_is_consistent_edge_included(stated: str, verdict: str) -> None:
    result = metrics_check(**{**METRICS_AM, "stated_arr": stated})

    assert _checks(result)[("arr", None)][2] == verdict


def test_a_zero_tolerance_needs_the_exact_figure() -> None:
    exact = metrics_check(**{**METRICS_AN_MODEL, "tolerance_percent": "0"})
    off = metrics_check(**{**METRICS_AN_MODEL, "tolerance_percent": "0", "stated_cac_payback_months": "9.61"})

    assert exact.verdict == "consistent"
    assert off.verdict == "mismatch"


def test_a_named_churn_basis_gets_one_row_and_an_unlabelled_one_a_row_per_basis() -> None:
    named = metrics_check(**{**METRICS_AN_DECK, "stated_churn_basis": "logo"})
    logo_only = metrics_check(period_months=1, customers_start=50, customers_lost=1, stated_churn_percent="2")

    assert [(row.basis, row.verdict) for row in named.checks if row.key == "churn"] == [("logo", "mismatch")]
    assert "churn_basis_unlabelled" not in named.flags
    assert [(row.basis, row.verdict) for row in logo_only.checks] == [("logo", "consistent")]
    assert logo_only.flags == ("churn_basis_unlabelled",)
    assert logo_only.verdict == "consistent"


def test_an_unlabelled_churn_matching_no_basis_is_one_mismatch() -> None:
    result = metrics_check(**{**METRICS_AN_DECK, "stated_churn_percent": "5", "stated_cac_payback_months": "9.6"})

    assert [row.verdict for row in result.checks if row.key == "churn"] == ["mismatch"] * 3
    assert result.verdict == "mismatch"


# Each flag: a minimal input that sets it, and its nearest neighbour that does not.
_FLAG_CASES: dict[MetricsFlag, tuple[dict[str, object], dict[str, object]]] = {
    "stated_arr_matches_run_rate": (
        {"month_total_revenue": "100", "month_one_time_revenue": "20", "stated_arr": "1200"},
        {"month_total_revenue": "100", "month_one_time_revenue": "20", "stated_arr": "1000"},
    ),
    "run_rate_includes_non_recurring": (
        {"month_total_revenue": "100", "month_usage_revenue": "10"},
        {"month_total_revenue": "100"},
    ),
    "stated_nrr_includes_new": (
        {"starting_recurring": "100", "new_recurring": "30", "expansion_recurring": "10", "stated_nrr_percent": "140"},
        {"starting_recurring": "100", "new_recurring": "30", "expansion_recurring": "10", "stated_nrr_percent": "120"},
    ),
    "expansion_hides_churn": (
        {"starting_recurring": "100", "expansion_recurring": "10", "churned_recurring": "5"},
        {"starting_recurring": "100", "expansion_recurring": "4", "churned_recurring": "5"},
    ),
    "churn_basis_unlabelled": (
        {"starting_recurring": "100", "churned_recurring": "5", "stated_churn_percent": "5"},
        {
            "starting_recurring": "100",
            "churned_recurring": "5",
            "stated_churn_percent": "5",
            "stated_churn_basis": "gross_revenue",
        },
    ),
    "blended_cac_only": (
        {"sales_marketing_spend": "1000", "customers_new": 10},
        {"sales_marketing_spend": "1000", "customers_new": 10, "customers_new_paid": 5},
    ),
    "payback_not_margin_adjusted": (
        {"starting_recurring": "100", "new_recurring": "10", "sales_marketing_spend": "1000"},
        {
            "starting_recurring": "100",
            "new_recurring": "10",
            "sales_marketing_spend": "1000",
            "gross_margin_percent": "50",
        },
    ),
    "stated_payback_not_margin_adjusted": (
        {
            "starting_recurring": "100",
            "new_recurring": "10",
            "sales_marketing_spend": "1000",
            "gross_margin_percent": "50",
            "stated_cac_payback_months": "100",
        },
        {
            "starting_recurring": "100",
            "new_recurring": "10",
            "sales_marketing_spend": "1000",
            "gross_margin_percent": "50",
            "stated_cac_payback_months": "150",
        },
    ),
    "stated_burn_multiple_uses_new_not_net_arr": (
        {"starting_recurring": "100", "new_recurring": "10", "churned_recurring": "5", "net_burn": "60"},
        {"starting_recurring": "100", "new_recurring": "10", "churned_recurring": "5", "net_burn": "60"},
    ),
    "burn_multiple_not_defined": (
        {"starting_recurring": "100", "new_recurring": "5", "churned_recurring": "5", "net_burn": "100"},
        {"starting_recurring": "100", "new_recurring": "10", "churned_recurring": "5", "net_burn": "100"},
    ),
    "no_net_burn": (
        {"starting_recurring": "100", "new_recurring": "10", "net_burn": "-50"},
        {"starting_recurring": "100", "new_recurring": "10", "net_burn": "50"},
    ),
    "payback_above_band": (
        {
            "starting_recurring": "100",
            "new_recurring": "10",
            "sales_marketing_spend": "60",
            "gross_margin_percent": "50",
            "customer_segment": "smb",
        },
        {
            "starting_recurring": "100",
            "new_recurring": "10",
            "sales_marketing_spend": "59",
            "gross_margin_percent": "50",
            "customer_segment": "smb",
        },
    ),
    "burn_multiple_above_band": (
        {"starting_recurring": "100", "new_recurring": "10", "net_burn": "360"},
        {"starting_recurring": "100", "new_recurring": "10", "net_burn": "359"},
    ),
    "net_revenue_churn_above_band": (
        {"starting_recurring": "100", "churned_recurring": "2.01"},
        {"starting_recurring": "100", "churned_recurring": "2"},
    ),
    # The movement's ending ARR 12·100 = 1,200 against the month's 12·110 = 1,320 (10% apart), then 12·101 (1%).
    "arr_movement_and_month_disagree": (
        {"starting_recurring": "100", "month_total_revenue": "110"},
        {"starting_recurring": "100", "month_total_revenue": "101"},
    ),
    # Net revenue churn 2.1%: a stated 1.7% is within 0.5 points but no rounding of it; a stated 2% is both.
    "consistent_beyond_rounding": (
        {"starting_recurring": "100", "churned_recurring": "2.1", "stated_churn_percent": "1.7"},
        {"starting_recurring": "100", "churned_recurring": "2.1", "stated_churn_percent": "2"},
    ),
    # Payback 124/10 = 12.4 months: a stated 12 is past 2% (0.248 months) but is 12.4 rounded; 12.0 is neither.
    "mismatch_within_rounding": (
        {
            "starting_recurring": "0",
            "new_recurring": "10",
            "sales_marketing_spend": "124",
            "gross_margin_percent": "100",
            "stated_cac_payback_months": "12",
        },
        {
            "starting_recurring": "0",
            "new_recurring": "10",
            "sales_marketing_spend": "124",
            "gross_margin_percent": "100",
            "stated_cac_payback_months": "12.0",
        },
    ),
}
# The burn-multiple pair differs only in the stated figure: on new ARR (12·10 = 120) 60/120 = 1/2; net new ARR 60
# gives 1.
_FLAG_CASES["stated_burn_multiple_uses_new_not_net_arr"][0]["stated_burn_multiple"] = "0.5"
_FLAG_CASES["stated_burn_multiple_uses_new_not_net_arr"][1]["stated_burn_multiple"] = "0.75"


@pytest.mark.parametrize("flag", sorted(_FLAG_CASES))
def test_each_flag_fires_on_its_minimal_input_and_not_on_its_neighbour(flag: MetricsFlag) -> None:
    fires, neighbour = _FLAG_CASES[flag]

    assert flag in metrics_check(period_months=1, **fires).flags
    assert flag not in metrics_check(period_months=1, **neighbour).flags


def test_every_flag_is_tested() -> None:
    assert set(_FLAG_CASES) == set(get_args(MetricsFlag))


def test_definition_flags_need_a_mismatch() -> None:
    """A stated ARR equal to both ARR and the run-rate (no one-time revenue) is consistent and names no cause."""
    result = metrics_check(period_months=1, starting_recurring="100", month_total_revenue="100", stated_arr="1200")

    assert result.verdict == "consistent"
    assert result.flags == ()


@pytest.mark.parametrize(
    ("movement", "month", "stated"),
    [
        # An all-recurring month: its run-rate is its ARR, so a stated 12 x 125k names no fees.
        ({"starting_recurring": "100000", "new_recurring": "10000"}, {"month_total_revenue": "125000"}, "1500000"),
        # A month with fees whose stated figure sits within tolerance of both its run-rate (1,200) and its ARR (1,188).
        ({"starting_recurring": "50"}, {"month_total_revenue": "100", "month_one_time_revenue": "1"}, "1194"),
    ],
    ids=["all-recurring-month", "within-both"],
)
def test_a_stated_arr_off_the_movement_names_the_run_rate_only_when_fees_set_it_apart(
    movement: dict[str, str], month: dict[str, str], stated: str
) -> None:
    """The movement's ending ARR (12 x 110k = 1.32M; 12 x 50 = 600) and the latest month disagree: the mismatch is
    real, yet the stated figure is the month's own ARR, so the run-rate flag would name a cause that is not there."""
    result = metrics_check(period_months=1, **movement, **month, stated_arr=stated)

    assert [check.verdict for check in result.checks] == ["mismatch"]
    assert "stated_arr_matches_run_rate" not in result.flags


def test_the_payback_band_is_the_segments_target_unless_one_is_given() -> None:
    base = {"period_months": 1, "starting_recurring": "100", "new_recurring": "10", "sales_marketing_spend": "100"}
    base |= {"gross_margin_percent": "50"}
    bands = {
        segment: metrics_check(**base, customer_segment=segment) for segment in ("smb", "mid_market", "enterprise")
    }
    given = metrics_check(**base, customer_segment="smb", payback_band_months="30")
    none = metrics_check(**base)

    assert {segment: _exact(result, "payback_band_months") for segment, result in bands.items()} == {
        "smb": 12,
        "mid_market": 18,
        "enterprise": 24,
    }
    assert [("payback_above_band" in result.flags) for result in bands.values()] == [True, True, False]
    smb = {row.key: row for row in bands["smb"].assumptions}["payback_band"]
    assert smb.setting == "12 months (SMB)"
    assert smb.source == f"{BESSEMER_SOURCE}: {PAYBACK_BAND_QUOTE} {_BENCHMARK}"
    row = {row.key: row for row in given.assumptions}["payback_band"]
    assert _exact(given, "payback_band_months") == 30
    assert row.setting == "30 months (given)"
    assert "used over the SMB target" in row.statement
    assert given.flags == ()
    assert none.payback_band_months is None
    assert "payback_band" not in {row.key for row in none.assumptions}


def test_the_band_rows_quote_their_sources_word_for_word() -> None:
    result = metrics_check(period_months=1, starting_recurring="100", new_recurring="10", churned_recurring="3")
    result_burn = metrics_check(period_months=1, starting_recurring="100", new_recurring="10", net_burn="400")
    rows = {row.key: row for row in (*result.assumptions, *result_burn.assumptions)}

    assert PAYBACK_BAND_QUOTE == f'"{_PAYBACK_WORDS}"'
    assert BURN_MULTIPLE_BAND_QUOTE == f'"{_BURN_WORDS}"'
    assert NET_REVENUE_CHURN_BAND_QUOTE == f'"{_CHURN_WORDS}"'
    assert rows["burn_multiple_band"].source == f"{SACKS_SOURCE}: {BURN_MULTIPLE_BAND_QUOTE} {_BENCHMARK}"
    assert rows["net_revenue_churn_band"].source == f"{SKOK_SOURCE}: {NET_REVENUE_CHURN_BAND_QUOTE} {_BENCHMARK}"
    assert result.flags == ("net_revenue_churn_above_band",)
    assert result_burn.flags == ("burn_multiple_above_band",)


def test_the_net_revenue_churn_band_is_asked_only_over_one_month() -> None:
    fields = {"starting_recurring": "100", "churned_recurring": "10"}
    month = metrics_check(period_months=1, **fields)
    quarter = metrics_check(period_months=3, **fields)

    assert "net_revenue_churn_above_band" in month.flags
    assert "net_revenue_churn_above_band" not in quarter.flags
    assert "net_revenue_churn_band" not in {row.key for row in quarter.assumptions}


def test_bands_are_inputs() -> None:
    fields = {"period_months": 1, "starting_recurring": "100", "new_recurring": "10", "churned_recurring": "3"}
    lifted = metrics_check(**fields, net_burn="400", burn_multiple_band="5", net_revenue_churn_band_percent="3")

    assert lifted.flags == ()
    rows = {row.key: row for row in lifted.assumptions}
    assert rows["burn_multiple_band"].setting == "5x"
    assert "the founder's own band here" in rows["burn_multiple_band"].statement


def test_nothing_stated_is_not_checked() -> None:
    result = metrics_check(**{key: value for key, value in METRICS_AM.items() if not key.startswith("stated_")})

    assert result.checks == ()
    assert result.verdict == "not_checked"
    assert "tolerance" not in {row.key for row in result.assumptions}


@pytest.mark.parametrize(
    ("burn", "new", "flag"),
    [("100", "5", "burn_multiple_not_defined"), ("0", "10", "no_net_burn"), ("-10", "10", "no_net_burn")],
    ids=["no-net-new-arr", "zero-burn", "cash-generative"],
)
def test_a_burn_multiple_with_nothing_to_divide_is_not_checked_and_flagged(burn: str, new: str, flag: str) -> None:
    result = metrics_check(
        period_months=1,
        starting_recurring="100",
        new_recurring=new,
        churned_recurring="5",
        net_burn=burn,
        stated_burn_multiple="2",
    )

    assert result.burn_multiple is None
    (row,) = result.checks
    assert (row.key, row.computed, row.difference, row.verdict) == ("burn_multiple", None, None, "not_checked")
    assert row.stated.exact == 2
    assert result.verdict == "not_checked"
    assert flag in result.flags


def test_a_stated_multiple_left_unchecked_keeps_the_overall_verdict_off_consistent() -> None:
    """ARR shrinks by 12·6k = 72k, so there is no net-new multiple; the deck's 6.25x is net burn over new ARR
    (1.8M / 12·24k). The ARR check holds, but the overall verdict can never read consistent, and the cause is named."""
    parts = {"starting_recurring": "100000", "new_recurring": "24000", "churned_recurring": "30000"}
    shrinking = metrics_check(period_months=12, **parts, net_burn="1800000", stated_burn_multiple="6.25")
    with_arr = metrics_check(
        period_months=12, **parts, net_burn="1800000", stated_burn_multiple="6.25", stated_arr="1128000"
    )
    wrong_arr = metrics_check(
        period_months=12, **parts, net_burn="1800000", stated_burn_multiple="6.25", stated_arr="2000000"
    )

    assert shrinking.verdict == with_arr.verdict == "not_checked"
    assert [row.verdict for row in with_arr.checks] == ["consistent", "not_checked"]
    assert wrong_arr.verdict == "mismatch"
    assert "stated_burn_multiple_uses_new_not_net_arr" in shrinking.flags
    assert "burn_multiple_not_defined" in shrinking.flags
    # A stated multiple off new ARR too names no cause.
    other = metrics_check(period_months=12, **parts, net_burn="1800000", stated_burn_multiple="9")
    assert "stated_burn_multiple_uses_new_not_net_arr" not in other.flags


def test_a_break_even_company_may_state_zero_and_it_is_not_checked() -> None:
    """The source says the multiple approaches 0 as burn reaches 0; the calculator works none at zero burn, so a
    stated 0x comes back not_checked, never refused; a stated multiple below 0 is still refused."""
    parts = {"period_months": 12, "starting_recurring": "100000", "new_recurring": "20000", "net_burn": "0"}
    result = metrics_check(**parts, stated_burn_multiple="0")

    assert [(row.key, row.verdict) for row in result.checks] == [("burn_multiple", "not_checked")]
    assert result.verdict == "not_checked"
    assert "no_net_burn" in result.flags
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        MetricsCheckInput.model_validate({**parts, "stated_burn_multiple": "-1"})


def test_the_burn_multiple_rule_attributes_only_what_the_essay_says() -> None:
    result = metrics_check(period_months=12, starting_recurring="100", new_recurring="20", net_burn="0")
    row = {row.key: row for row in result.assumptions}["burn_multiple_rule"]

    assert "approach 0 over time" in row.source
    assert "covers" not in row.statement
    assert "working none at zero burn, and none for a negative burn or net new ARR, is ours" in row.statement


def test_negative_net_revenue_churn_is_checked_on_net_revenue_alone() -> None:
    """Expansion 5k above churn 2k on 100k: net revenue churn is -3%, which a deck may state; gross and logo churn
    cannot go below 0, so an unlabelled -3% is checked only on net revenue."""
    parts = {"period_months": 1, "starting_recurring": "100000", "expansion_recurring": "5000"}
    parts |= {"churned_recurring": "2000", "customers_start": 50, "customers_lost": 1}
    net = metrics_check(**parts, stated_churn_percent="-3", stated_churn_basis="net_revenue")
    unlabelled = metrics_check(**parts, stated_churn_percent="-3")

    assert [(row.basis, row.verdict) for row in net.checks] == [("net_revenue", "consistent")]
    assert [(row.basis, row.verdict) for row in unlabelled.checks] == [("net_revenue", "consistent")]
    assert net.verdict == unlabelled.verdict == "consistent"


@pytest.mark.parametrize(
    "fields",
    [
        {"customers_start": 5, "customers_lost": 1, "stated_churn_basis": "logo"},
        {"starting_recurring": "100", "stated_churn_basis": "gross_revenue"},
        {"customers_start": 5, "customers_lost": 1},
    ],
    ids=["logo", "gross-revenue", "unlabelled-with-only-logo"],
)
def test_a_churn_below_zero_on_a_basis_that_cannot_go_there_is_refused_with_why(fields: dict[str, object]) -> None:
    with pytest.raises(ValidationError, match="stated_churn_percent is below 0, which only net revenue churn can be"):
        MetricsCheckInput.model_validate({"period_months": 1, "stated_churn_percent": "-1", **fields})


def test_a_stated_gross_retention_above_100_is_a_mismatch_not_a_refusal() -> None:
    """Expansion netted into gross retention: 104% against (100k - 5k)/100k = 95%."""
    result = metrics_check(
        period_months=12,
        starting_recurring="100000",
        expansion_recurring="9000",
        churned_recurring="5000",
        stated_grr_percent="104",
    )

    assert _checks(result)[("grr", None)] == (Fraction(104, 100), Fraction(95, 100), "mismatch")
    assert result.verdict == "mismatch"


@pytest.mark.parametrize(
    ("stated", "spend", "within"),
    [
        ("12", "124", True),
        ("12.0", "124", False),
        ("12", "125", True),
        ("12", "125.01", False),
        ("1.2E+1", "124", True),
    ],
    ids=["whole-month-rounds", "one-place-does-not", "half-a-month-edge", "just-past-half", "exponent-form-whole"],
)
def test_each_row_says_whether_the_stated_figure_is_a_rounding_of_the_computed_one(
    stated: str, spend: str, within: bool
) -> None:
    """Payback = spend / (10 x 100%): the stated figure is a rounding when within half its own last place."""
    result = metrics_check(
        period_months=12,
        starting_recurring="0",
        new_recurring="10",
        sales_marketing_spend=spend,
        gross_margin_percent="100",
        stated_cac_payback_months=stated,
    )

    (row,) = result.checks
    assert row.within_rounding is within


def test_the_rounding_test_reads_a_percent_in_points_and_leaves_money_out() -> None:
    """Net revenue churn 2.1% on one month: 1.7 is no rounding of it, 2.1 is, and an ARR row has no rounding test."""
    parts = {"period_months": 1, "starting_recurring": "100000", "churned_recurring": "2100"}
    off = metrics_check(**parts, stated_churn_percent="1.7", stated_churn_basis="net_revenue", stated_arr="1174800")
    exact = metrics_check(**parts, stated_churn_percent="2.10", stated_churn_basis="net_revenue")

    rows = {row.key: row for row in off.checks}
    assert (rows["churn"].verdict, rows["churn"].within_rounding) == ("consistent", False)
    assert rows["arr"].within_rounding is None
    assert "consistent_beyond_rounding" in off.flags
    assert exact.checks[0].within_rounding is True
    assert "consistent_beyond_rounding" not in exact.flags


def test_a_revenue_only_payback_already_past_the_band_is_flagged_and_the_row_says_how_far_it_applies() -> None:
    """SMB target under 12 months, no gross margin: 300k / 10k = 30 months on revenue alone, a floor under the
    payback on gross margin, so the band flag fires; at 3 months nothing can be said and the row says so."""
    parts = {"period_months": 12, "starting_recurring": "100000", "new_recurring": "10000", "customer_segment": "smb"}
    slow = metrics_check(**parts, sales_marketing_spend="300000")
    fast = metrics_check(**parts, sales_marketing_spend="30000")

    assert "payback_above_band" in slow.flags
    assert "payback_above_band" not in fast.flags
    assert _exact(slow, "payback_band_months") == _exact(fast, "payback_band_months") == 12
    row = {row.key: row for row in fast.assumptions}["payback_band"]
    assert "below it the benchmark is not applied" in row.statement
    margin = metrics_check(**parts, sales_marketing_spend="30000", gross_margin_percent="50")
    margin_row = {row.key: row for row in margin.assumptions}["payback_band"]
    assert "not applied" not in margin_row.statement


def test_a_stated_arr_equal_to_the_months_arr_names_the_disagreeing_parts() -> None:
    """Movement 12·98k = 1.176M, the latest month 12·100k = 1.2M: a deck's 1.2M is a mismatch against the movement,
    and the flag says the founder's two sets of parts disagree."""
    result = metrics_check(
        period_months=12,
        starting_recurring="80000",
        new_recurring="18000",
        month_total_revenue="100000",
        stated_arr="1200000",
    )

    assert result.verdict == "mismatch"
    assert "arr_movement_and_month_disagree" in result.flags
    assert "stated_arr_matches_run_rate" not in result.flags


def test_a_stated_concentration_and_cac_are_checked() -> None:
    result = metrics_check(
        period_months=12,
        sales_marketing_spend="90000",
        customers_new=30,
        largest_customer_revenue="150000",
        period_revenue="1000000",
        stated_cac="3000",
        stated_concentration_percent="12",
    )

    assert _checks(result) == {
        ("cac", None): (Fraction(3000), Fraction(3000), "consistent"),
        ("concentration", None): (Fraction(3, 25), Fraction(3, 20), "mismatch"),
    }
    assert result.flags == ("blended_cac_only",)


def test_assumption_rows_appear_only_when_used() -> None:
    bare = metrics_check(period_months=3)
    full = {row.key for row in metrics_check(**METRICS_AN_DECK).assumptions}

    assert [row.key for row in bare.assumptions] == ["period_rule"]
    assert bare.assumptions[0].setting == "3 months"
    assert metrics_check(period_months=1).assumptions[0].setting == "1 month"
    assert full == {
        "period_rule",
        "arr_rule",
        "retention_rule",
        "cohort_rule",
        "churn_rule",
        "cac_rule",
        "payback_rule",
        "tolerance",
        "payback_band",
        "net_revenue_churn_band",
    }


_NEEDS = "to check it"


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"new_recurring": "5"}, "new_recurring needs starting_recurring"),
        ({"cohort_churned_recurring": "1"}, "cohort_churned_recurring needs starting_recurring"),
        (
            {"starting_recurring": "10", "new_recurring": "1", "contraction_recurring": "6", "churned_recurring": "6"},
            "contraction_recurring + churned_recurring is above starting_recurring + new_recurring + "
            "expansion_recurring",
        ),
        (
            {"starting_recurring": "10", "churned_recurring": "2", "cohort_churned_recurring": "3"},
            "cohort_churned_recurring is above churned_recurring",
        ),
        (
            {
                "starting_recurring": "10",
                "new_recurring": "100",
                "contraction_recurring": "3",
                "churned_recurring": "15",
            },
            "cohort_contraction_recurring + cohort_churned_recurring (each the period's total when not given) is "
            "above starting_recurring",
        ),
        (
            {
                "starting_recurring": "10",
                "new_recurring": "100",
                "contraction_recurring": "3",
                "churned_recurring": "15",
                "cohort_churned_recurring": "8",
            },
            "cohort_contraction_recurring + cohort_churned_recurring (each the period's total when not given) is "
            "above starting_recurring",
        ),
        (
            {
                "starting_recurring": "0",
                "new_recurring": "5",
                "churned_recurring": "2",
                "cohort_churned_recurring": "1",
            },
            "cohort_contraction_recurring + cohort_churned_recurring (each the period's total when not given) is "
            "above starting_recurring",
        ),
        ({"month_usage_revenue": "5"}, "month_usage_revenue needs month_total_revenue"),
        (
            {"month_total_revenue": "10", "month_one_time_revenue": "6", "month_usage_revenue": "5"},
            "month_one_time_revenue + month_usage_revenue is above month_total_revenue",
        ),
        ({"customers_lost": 1}, "customers_lost needs customers_start"),
        (
            {"customers_start": 1, "customers_lost": 2},
            "customers_lost is above customers_start: give only the customers lost among those there at the start of "
            "the period; customers won and lost inside the period are left out of logo churn",
        ),
        ({"customers_new_paid": 1}, "customers_new_paid needs customers_new"),
        ({"customers_new": 1, "customers_new_paid": 2}, "customers_new_paid is above customers_new"),
        ({"largest_customer_revenue": "1"}, "largest_customer_revenue needs period_revenue"),
        (
            {"largest_customer_revenue": "2", "period_revenue": "1"},
            "largest_customer_revenue is above period_revenue",
        ),
        ({"stated_arr": "1"}, f"stated_arr needs starting_recurring or month_total_revenue {_NEEDS}"),
        (
            {"starting_recurring": "0", "stated_nrr_percent": "100"},
            f"stated_nrr_percent needs starting_recurring above 0 {_NEEDS}",
        ),
        ({"stated_grr_percent": "90"}, f"stated_grr_percent needs starting_recurring above 0 {_NEEDS}"),
        ({"stated_cac": "1"}, f"stated_cac needs sales_marketing_spend and customers_new above 0 {_NEEDS}"),
        (
            {"sales_marketing_spend": "1", "customers_new": 0, "stated_cac": "1"},
            f"stated_cac needs sales_marketing_spend and customers_new above 0 {_NEEDS}",
        ),
        (
            {"starting_recurring": "1", "sales_marketing_spend": "1", "stated_cac_payback_months": "1"},
            f"stated_cac_payback_months needs sales_marketing_spend and new_recurring above 0 {_NEEDS}",
        ),
        (
            {"starting_recurring": "1", "stated_burn_multiple": "1"},
            f"stated_burn_multiple needs net_burn and starting_recurring {_NEEDS}",
        ),
        (
            {"stated_concentration_percent": "1"},
            f"stated_concentration_percent needs largest_customer_revenue and period_revenue {_NEEDS}",
        ),
        ({"stated_churn_basis": "logo"}, "stated_churn_basis needs stated_churn_percent"),
        (
            {"starting_recurring": "1", "stated_churn_percent": "1", "stated_churn_basis": "logo"},
            "stated_churn_percent on a logo basis needs customers_start above 0 and customers_lost",
        ),
        (
            {
                "customers_start": 5,
                "customers_lost": 1,
                "stated_churn_percent": "1",
                "stated_churn_basis": "net_revenue",
            },
            "stated_churn_percent on a net_revenue basis needs starting_recurring above 0",
        ),
        (
            {"customers_start": 5, "stated_churn_percent": "1"},
            "stated_churn_percent needs customers_start above 0 with customers_lost, or starting_recurring above 0",
        ),
        ({"period_months": 0}, "greater than or equal to 1"),
        ({"period_months": MAX_PERIOD_MONTHS + 1}, f"less than or equal to {MAX_PERIOD_MONTHS}"),
        ({"customers_start": True}, "Input should be a valid integer"),
        ({"customers_start": -1}, "greater than or equal to 0"),
        ({"stated_churn_percent": "100.1", "starting_recurring": "1"}, "less than or equal to 100"),
        (
            {"customers_start": 5, "customers_lost": 1, "stated_churn_percent": "-0.5"},
            "stated_churn_percent is below 0, which only net revenue churn can be (expansion above the revenue lost)",
        ),
    ],
    ids=[
        "movement-without-start",
        "cohort-without-start",
        "more-lost-than-there-was",
        "cohort-above-total",
        "starting-customers-lose-more-than-the-start",
        "cohort-part-plus-total-above-the-start",
        "cohort-loss-with-nothing-at-the-start",
        "month-part-without-total",
        "month-parts-above-total",
        "lost-without-start",
        "lost-above-start",
        "paid-without-new",
        "paid-above-new",
        "largest-without-period",
        "largest-above-period",
        "arr-without-parts",
        "nrr-on-zero-start",
        "grr-without-start",
        "cac-without-spend",
        "cac-without-new-customers",
        "payback-without-new-recurring",
        "multiple-without-burn",
        "concentration-without-parts",
        "basis-without-churn",
        "logo-basis-without-customers",
        "revenue-basis-without-start",
        "unlabelled-without-any-basis",
        "period-zero",
        "period-too-long",
        "customers-bool",
        "customers-negative",
        "churn-above-100",
        "churn-below-0-without-revenue",
    ],
)
def test_each_refusal_names_its_fields(fields: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=re.escape(message)):
        MetricsCheckInput.model_validate({"period_months": 1, **fields})


@pytest.mark.parametrize(
    ("unit", "parts", "setting"),
    [
        (
            "annual",
            {"month_total_revenue": "100"},
            "ARR from the latest month = 12 × its recurring revenue; run-rate = 12 × its whole revenue",
        ),
        ("annual", {"starting_recurring": "1200"}, "ARR = annual recurring revenue"),
        (
            "monthly",
            {"starting_recurring": "100", "month_total_revenue": "100"},
            "ARR = 12 × monthly recurring revenue; ARR from the latest month = 12 × its recurring revenue; run-rate = "
            "12 × its whole revenue",
        ),
    ],
    ids=["annual-month-only", "annual-movement-only", "both"],
)
def test_the_arr_rule_names_only_the_arr_figures_worked(unit: str, parts: dict[str, object], setting: str) -> None:
    result = metrics_check(period_months=12, recurring_unit=unit, **parts)

    assert {row.key: row for row in result.assumptions}["arr_rule"].setting == setting
