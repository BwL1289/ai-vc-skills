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
- Company DL, one month: gross revenue churn (1k + 3k)/200k = 1/50, so LTV on the 60% contribution margin is
  2k·(3/5)/(1/50) = 60k, 80k on the 80% gross margin, and 100k on revenue alone: the deck's $100k. Blended CAC
  150k/25 = 6k, so LTV/CAC 10 (the deck's 10x) and 50/3 on revenue. Rule of 40 70% - 35% = 7/20 (the deck's 35). Magic
  number 4·(600k - 510k)/450k = 4/5; the deck's 0.2 is 90k/450k = 1/5, the change without the 4.
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
from equity_calculator.metrics_check import compute_metrics_check
from equity_calculator.schemas.equity_metrics_check import (
    MAX_PERIOD_MONTHS,
    MetricsCheckInput,
    MetricsCheckResult,
    MetricsFlag,
)
from pydantic import ValidationError
from tests.support import METRICS_AM, METRICS_AN_DECK, METRICS_AN_MODEL, METRICS_DL, metrics_check

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


def test_company_dl_an_ltv_on_revenue_and_a_magic_number_without_its_4() -> None:
    result = metrics_check(**METRICS_DL)

    assert _exact(result, "ltv") == 60_000
    assert result.ltv_margin_basis == "contribution"
    assert _exact(result, "ltv_on_revenue") == 100_000
    assert _exact(result, "gross_margin_ltv") == 80_000
    assert _exact(result, "ltv_to_cac") == 10
    assert _exact(result, "ltv_to_cac_on_revenue") == Fraction(50, 3)
    assert _exact(result, "rule_of_40") == Fraction(7, 20)
    assert _exact(result, "magic_number") == Fraction(4, 5)
    assert result.magic_number_variant == "revenue"
    assert _exact(result, "magic_number_unannualised") == Fraction(1, 5)
    assert _checks(result) == {
        ("ltv", None): (Fraction(100_000), Fraction(60_000), "mismatch"),
        ("ltv_to_cac", None): (Fraction(10), Fraction(10), "consistent"),
        ("rule_of_40", None): (Fraction(7, 20), Fraction(7, 20), "consistent"),
        ("magic_number", None): (Fraction(1, 5), Fraction(4, 5), "mismatch"),
    }
    assert result.flags == ("stated_ltv_uses_revenue_not_margin", "stated_magic_number_not_annualised")
    assert result.verdict == "mismatch"


def test_the_new_figures_are_none_without_their_parts() -> None:
    result = metrics_check(**METRICS_AN_DECK)

    for name in (
        "ltv",
        "ltv_margin_basis",
        "ltv_on_revenue",
        "gross_margin_ltv",
        "ltv_to_cac",
        "ltv_to_cac_on_revenue",
        "rule_of_40",
        "magic_number",
        "magic_number_variant",
        "magic_number_unannualised",
    ):
        assert getattr(result, name) is None, name


# LTV's minimal parts: 100 MRR at the start, 5 cancelled (gross revenue churn 1/20), $10 ARPA and a 50% gross margin.
_LTV_PARTS: dict[str, object] = {
    "starting_recurring": "100",
    "churned_recurring": "5",
    "arpa": "10",
    "gross_margin_percent": "50",
}


def test_ltv_is_on_the_contribution_margin_when_given_else_the_gross_margin() -> None:
    gross = metrics_check(period_months=1, **_LTV_PARTS)
    contribution = metrics_check(period_months=1, **_LTV_PARTS, contribution_margin_percent="40")

    assert _exact(gross, "ltv") == 100 and gross.ltv_margin_basis == "gross"
    assert _exact(contribution, "ltv") == 80 and contribution.ltv_margin_basis == "contribution"
    assert "ltv_on_gross_margin" in gross.flags and "ltv_on_gross_margin" not in contribution.flags
    # LTV/CAC is worked only with a blended CAC; the revenue figures only beside a stated one.
    assert gross.ltv_to_cac is None and gross.ltv_on_revenue is None


def test_ltv_on_gross_margin_is_worked_only_beside_a_stated_ltv_on_a_contribution_margin() -> None:
    """With a stated LTV and both margins, LTV on the 50% gross margin is 100 beside 80 on the 40% contribution margin;
    with no stated LTV, or no contribution margin, it is not worked."""
    both = metrics_check(period_months=1, **_LTV_PARTS, contribution_margin_percent="40", stated_ltv="80")
    unstated = metrics_check(period_months=1, **_LTV_PARTS, contribution_margin_percent="40")
    gross_only = metrics_check(period_months=1, **_LTV_PARTS, stated_ltv="100")

    assert _exact(both, "gross_margin_ltv") == 100
    assert unstated.gross_margin_ltv is None and gross_only.gross_margin_ltv is None
    # The stated 80 holds on the contribution margin, so no LTV flag; the 5% month's churn raises its benchmark alone.
    assert both.flags == ("net_revenue_churn_above_band",)


@pytest.mark.parametrize(
    ("basis", "parts", "ltv"),
    [
        # Logo churn 2/40 = 1/20: 10·(1/2)/(1/20) = 100.
        ("logo", {"customers_start": 40, "customers_lost": 2}, Fraction(100)),
        # Net revenue churn (5 - 1)/100 = 1/25: 10·(1/2)/(1/25) = 125.
        ("net_revenue", {"expansion_recurring": "1"}, Fraction(125)),
    ],
)
def test_ltv_divides_by_the_churn_the_founder_picks(basis: str, parts: dict[str, object], ltv: Fraction) -> None:
    result = metrics_check(period_months=1, **_LTV_PARTS, **parts, ltv_churn_basis=basis)

    assert _exact(result, "ltv") == ltv
    assert {row.key: row for row in result.assumptions}["ltv_rule"].setting.endswith(
        f"/ {basis.replace('_', ' ')} churn over 1 month"
    )


def test_ltv_scales_arpa_to_the_period_in_either_unit() -> None:
    """Over 6 months a monthly ARPA counts 6 times and an annual one half: the same business, the same LTV."""
    monthly = metrics_check(period_months=6, **_LTV_PARTS)
    annual = metrics_check(period_months=6, recurring_unit="annual", **{**_LTV_PARTS, "arpa": "120"})

    assert _exact(monthly, "ltv") == _exact(annual, "ltv") == 600
    settings = [{row.key: row for row in result.assumptions}["ltv_rule"].setting for result in (monthly, annual)]
    assert settings == [
        "monthly ARPA × 6 months × 50% gross margin / gross revenue churn over 6 months",
        "annual ARPA × 1/2 of a year × 50% gross margin / gross revenue churn over 6 months",
    ]


@pytest.mark.parametrize(("months", "units"), [(12, "1 year"), (24, "2 years")])
def test_an_annual_arpa_over_whole_years_names_the_years(months: int, units: str) -> None:
    result = metrics_check(period_months=months, recurring_unit="annual", **{**_LTV_PARTS, "arpa": "120"})

    assert _exact(result, "ltv") == 120 * (months // 12) * Fraction(1, 2) / Fraction(1, 20)
    assert {row.key: row for row in result.assumptions}["ltv_rule"].setting.startswith(f"annual ARPA × {units} ×")


def test_an_ltv_to_cac_on_revenue_alone_is_named() -> None:
    """LTV/CAC 100/50 = 2 on margin, 200/50 = 4 on revenue: a stated 4 is a mismatch the flag explains."""
    result = metrics_check(
        period_months=1, **_LTV_PARTS, sales_marketing_spend="500", customers_new=10, stated_ltv_to_cac="4"
    )

    assert _checks(result) == {("ltv_to_cac", None): (Fraction(4), Fraction(2), "mismatch")}
    assert _exact(result, "ltv_to_cac_on_revenue") == 4
    assert "stated_ltv_uses_revenue_not_margin" in result.flags


@pytest.mark.parametrize(
    ("growth", "margin", "stated", "computed"),
    [("-10", "-20", "-30", Fraction(-3, 10)), ("120", "-95.5", "24.5", Fraction(49, 200))],
    ids=["both-below-zero", "fast-growth-deep-loss"],
)
def test_the_rule_of_40_adds_the_founders_two_percents_of_either_sign(
    growth: str, margin: str, stated: str, computed: Fraction
) -> None:
    result = metrics_check(
        period_months=1,
        revenue_growth_percent=growth,
        profit_margin_percent=margin,
        profit_margin_basis="free_cash_flow",
        stated_rule_of_40_percent=stated,
    )

    assert _exact(result, "rule_of_40") == computed
    assert _checks(result) == {("rule_of_40", None): (computed, computed, "consistent")}
    assert result.flags == ()


def test_the_magic_number_on_arr_has_no_4_and_may_fall_below_zero() -> None:
    """ARR from 100 to 90 on 50 of spend: -1/5. A stated -0.196 holds by the tolerance (2% of the size, 0.004), not
    as a rounding of -0.200, so the tolerance reads the size of a figure below zero."""
    result = metrics_check(
        period_months=1,
        quarter_ending_arr="90",
        prior_quarter_ending_arr="100",
        prior_quarter_sales_marketing_spend="50",
        stated_magic_number="-0.196",
    )

    assert _exact(result, "magic_number") == Fraction(-1, 5)
    assert result.magic_number_variant == "arr"
    assert result.magic_number_unannualised is None
    assert _checks(result) == {("magic_number", None): (Fraction(-49, 250), Fraction(-1, 5), "consistent")}
    assert result.flags == ("consistent_beyond_rounding",)
    rows = {row.key: row for row in result.assumptions}
    assert rows["magic_number_rule"].setting.startswith("(ARR at this quarter's end - at the prior quarter's end)")


def test_a_magic_number_on_revenue_with_none_stated_works_no_figure_without_the_4() -> None:
    """4·(110 - 100)/50 = 4/5. With no stated figure there is nothing to test, so the change without the 4 is not
    worked, and with no check at all the verdict is not_checked."""
    result = metrics_check(
        period_months=1, quarter_revenue="110", prior_quarter_revenue="100", prior_quarter_sales_marketing_spend="50"
    )

    assert _exact(result, "magic_number") == Fraction(4, 5)
    assert result.magic_number_variant == "revenue"
    assert result.magic_number_unannualised is None
    assert result.checks == ()
    assert result.verdict == "not_checked"


def test_the_later_rows_print_a_percent_in_exponent_form_as_its_digits() -> None:
    """A percent sent as "5E+1" through the MCP tool or the Python API prints as 50%, never 5E+1%; one typed with a
    place keeps it (60.0%)."""
    exponent = metrics_check(
        period_months=1,
        starting_recurring="100",
        churned_recurring="5",
        new_recurring="1E+1",
        sales_marketing_spend="500",
        arpa="10",
        gross_margin_percent="5E+1",
        revenue_growth_percent="7E+1",
        profit_margin_percent="-3.5E+1",
        profit_margin_basis="ebitda",
    )
    placed = metrics_check(period_months=1, **{**_LTV_PARTS, "contribution_margin_percent": "60.0"})

    rows = {row.key: row.setting for row in exponent.assumptions}
    assert rows["ltv_rule"] == "monthly ARPA × 1 month × 50% gross margin / gross revenue churn over 1 month"
    assert rows["rule_of_40_rule"] == "revenue growth 70% + EBITDA margin -35%"
    assert rows["payback_rule"] == "spend / (new monthly recurring revenue × 50% gross margin)"
    assert {row.key: row.setting for row in placed.assumptions}["ltv_rule"].startswith(
        "monthly ARPA × 1 month × 60.0% contribution margin /"
    )


def test_the_later_rules_cite_what_was_read_and_quote_nothing_unread() -> None:
    rows = {row.key: row for row in metrics_check(**METRICS_DL).assumptions}

    setting = "monthly ARPA × 1 month × 60% contribution margin / gross revenue churn over 1 month"
    assert rows["ltv_rule"].setting == setting
    assert "item 5, paraphrased" in rows["ltv_rule"].source and "unverified" in rows["ltv_rule"].source
    assert rows["rule_of_40_rule"].setting == "revenue growth 70% + EBITDA margin -35%"
    assert rows["magic_number_rule"].setting.startswith("4 × (this quarter's revenue - the prior quarter's)")
    for key in ("rule_of_40_rule", "magic_number_rule"):
        assert rows[key].source.startswith("unverified") and '"' not in rows[key].source, key
        # With no source read, no person or firm is credited either: a name is no citation.
        assert rows[key].source.endswith("no source was read for it, so none is credited or quoted"), key
        assert "no benchmark" in rows[key].statement or "No line is set" in rows[key].statement, key
    assert "outside this period" in rows["period_rule"].statement
    assert "outside this period" not in metrics_check(**METRICS_AN_DECK).assumptions[0].statement


def _random_input(rng: random.Random) -> dict[str, object]:
    start = rng.randint(1, 10**6)
    contraction = rng.randint(0, start)
    churned = rng.randint(0, start - contraction)
    new = rng.randint(1, 10**6)
    expansion = rng.randint(0, 10**5)
    fields: dict[str, object] = {
        "period_months": rng.randint(1, MAX_PERIOD_MONTHS),
        "starting_recurring": str(start),
        "new_recurring": str(new),
        "expansion_recurring": str(expansion),
        "contraction_recurring": str(contraction),
        "churned_recurring": str(churned),
        "sales_marketing_spend": str(rng.randint(1, 10**7)),
        "gross_margin_percent": str(rng.randint(1, 100)),
        "net_burn": str(rng.randint(-(10**6), 10**7)),
        "customers_new": rng.randint(1, 1000),
    }
    # LTV needs a churn above zero to divide by, so ARPA and its margin come only when something was lost.
    if contraction + churned > 0:
        fields |= {"arpa": str(rng.randint(1, 10**4)), "contribution_margin_percent": str(rng.randint(1, 100))}
    return fields


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
        # LTV times the churn is the period's ARPA after margin; LTV/CAC times CAC is LTV; no churn, no LTV.
        if "arpa" not in fields:
            assert result.ltv is None and result.ltv_to_cac is None
            continue
        months = Fraction(int(str(fields["period_months"])))
        contribution = Fraction(str(fields["contribution_margin_percent"])) / 100
        arpa = Fraction(str(fields["arpa"]))
        assert _exact(result, "ltv") * _exact(result, "gross_revenue_churn") == arpa * months * contribution
        assert _exact(result, "ltv_to_cac") * _exact(result, "blended_cac") == _exact(result, "ltv")


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


def test_a_zero_tolerance_needs_the_exact_figure_or_its_rounding_to_the_places_typed() -> None:
    """Payback 9.6 months with no tolerance: 9.6 and 10 (9.6 to no places) hold; 9.61 (9.60 to two places) does not."""
    exact = metrics_check(**{**METRICS_AN_MODEL, "tolerance_percent": "0"})
    off = metrics_check(**{**METRICS_AN_MODEL, "tolerance_percent": "0", "stated_cac_payback_months": "9.61"})
    rounded = metrics_check(**{**METRICS_AN_MODEL, "tolerance_percent": "0", "stated_cac_payback_months": "10"})

    assert exact.verdict == "consistent"
    assert off.verdict == "mismatch"
    assert rounded.verdict == "consistent"


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
_RULE_OF_40_PARTS: dict[str, object] = {
    "revenue_growth_percent": "30",
    "profit_margin_percent": "10",
    "profit_margin_basis": "operating",
    "gross_margin_percent": "70",
}
_MAGIC_PARTS: dict[str, object] = {
    "quarter_revenue": "110",
    "prior_quarter_revenue": "100",
    "prior_quarter_sales_marketing_spend": "50",
}
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
    "ltv_on_gross_margin": (_LTV_PARTS, {**_LTV_PARTS, "contribution_margin_percent": "40"}),
    # A 60% contribution margin above the 50% gross margin; equal margins are not above.
    "contribution_margin_above_gross_margin": (
        {**_LTV_PARTS, "contribution_margin_percent": "60"},
        {**_LTV_PARTS, "contribution_margin_percent": "50"},
    ),
    # On the 40% contribution margin LTV is 10·(2/5)/(1/20) = 80; on the 50% gross margin 100.
    "stated_ltv_uses_gross_margin": (
        {**_LTV_PARTS, "contribution_margin_percent": "40", "stated_ltv": "100"},
        {**_LTV_PARTS, "contribution_margin_percent": "40", "stated_ltv": "90"},
    ),
    # LTV 10·(1/2)/(1/20) = 100 on margin, 200 on revenue alone.
    "stated_ltv_uses_revenue_not_margin": ({**_LTV_PARTS, "stated_ltv": "200"}, {**_LTV_PARTS, "stated_ltv": "150"}),
    "rule_of_40_margin_basis_unlabelled": (
        {"revenue_growth_percent": "30", "profit_margin_percent": "10"},
        {"revenue_growth_percent": "30", "profit_margin_percent": "10", "profit_margin_basis": "ebitda"},
    ),
    # Growth 30 + operating margin 10 = 40; growth 30 + gross margin 70 = 100.
    "stated_rule_of_40_uses_gross_margin": (
        {**_RULE_OF_40_PARTS, "stated_rule_of_40_percent": "100"},
        {**_RULE_OF_40_PARTS, "stated_rule_of_40_percent": "90"},
    ),
    # 4·(110 - 100)/50 = 0.8 with the 4, 0.2 without it.
    "stated_magic_number_not_annualised": (
        {**_MAGIC_PARTS, "stated_magic_number": "0.2"},
        {**_MAGIC_PARTS, "stated_magic_number": "0.5"},
    ),
    # Net revenue churn 2.1%: a stated 1.7% is within 0.5 points but no rounding of it; a stated 2% is both.
    "consistent_beyond_rounding": (
        {"starting_recurring": "100", "churned_recurring": "2.1", "stated_churn_percent": "1.7"},
        {"starting_recurring": "100", "churned_recurring": "2.1", "stated_churn_percent": "2"},
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
def test_a_stated_arr_off_the_movement_but_on_the_months_own_arr_holds_and_names_no_run_rate(
    movement: dict[str, str], month: dict[str, str], stated: str
) -> None:
    """The movement's ending ARR (12 x 110k = 1.32M; 12 x 50 = 600) and the latest month disagree, but the stated
    figure is the month's own ARR: consistent, checked against that ARR, and the run-rate flag names no cause."""
    result = metrics_check(period_months=1, **movement, **month, stated_arr=stated)

    assert [check.verdict for check in result.checks] == ["consistent"]
    assert result.arr_basis == "month"
    assert "stated_arr_matches_run_rate" not in result.flags
    assert "arr_movement_and_month_disagree" in result.flags


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
    ("stated", "verdict"),
    [("100.4", "consistent"), ("100.45", "consistent"), ("100.5", "mismatch"), ("101", "mismatch")],
)
def test_a_stated_gross_retention_above_100_within_the_tolerance_is_consistent_as_the_docs_say(
    stated: str, verdict: str
) -> None:
    """(100k - 50)/100k = 99.95%: 100.4% is 0.45 points off and 100.45% 0.5 (the edge), within the half-point tolerance,
    so each is checked like any figure (the README, the schema comment and the skill say "a mismatch unless within the
    tolerance"); 100.5% and 101% are past it."""
    result = metrics_check(
        period_months=12, starting_recurring="100000", churned_recurring="50", stated_grr_percent=stated
    )

    (row,) = result.checks
    assert row.computed is not None and row.computed.exact == Fraction(9995, 10000)
    assert (row.verdict, result.verdict) == (verdict, verdict)


# One-place, two-place and whole zeros, each against a computed 0.4% (or 0.416667x): only a whole "0" is a rounding of
# it (0.4 rounds half away from zero to 0); "0.0" holds only below 0.05 and "0.00" below 0.005, as typed.
_ZERO_FIELDS: dict[str, dict[str, object]] = {
    "stated_nrr_percent": {"period_months": 12, "starting_recurring": "100000", "churned_recurring": "99600"},
    "stated_grr_percent": {"period_months": 12, "starting_recurring": "100000", "churned_recurring": "99600"},
    "stated_churn_percent": {
        "period_months": 1,
        "starting_recurring": "100000",
        "churned_recurring": "400",
        "stated_churn_basis": "gross_revenue",
    },
    "stated_burn_multiple": {
        "period_months": 12,
        "starting_recurring": "100000",
        "new_recurring": "20000",
        "net_burn": "100000",
    },
    "stated_concentration_percent": {"period_months": 12, "largest_customer_revenue": "4", "period_revenue": "1000"},
}


@pytest.mark.parametrize("field", list(_ZERO_FIELDS))
@pytest.mark.parametrize(("typed", "within"), [("0", True), ("0.0", False), ("0.00", False), ("-0.0", False)])
def test_a_stated_zero_is_read_with_the_places_it_is_written_with(field: str, typed: str, within: bool) -> None:
    result = metrics_check(**_ZERO_FIELDS[field], **{field: typed})

    (row,) = result.checks
    assert row.stated.exact == 0
    assert row.within_rounding is within
    # A rounding is consistent whatever the tolerance (the multiple's 0.416667x is far past 2% of itself); a figure
    # consistent without being one is flagged.
    if within:
        assert row.verdict == "consistent"
    flagged = "consistent_beyond_rounding" in result.flags
    assert flagged is (row.verdict == "consistent" and not within)


def test_a_stated_zero_keeps_its_places_when_its_echoed_inputs_are_fed_back() -> None:
    """The places live in the value itself: "0.0" is echoed as "0.0", and the echo gives the same rounding row."""
    first = metrics_check(**_ZERO_FIELDS["stated_churn_percent"], stated_churn_percent="0.0")
    echoed = MetricsCheckInput.model_validate_json(first.inputs.model_dump_json())

    assert first.model_dump(mode="json")["inputs"]["stated_churn_percent"] == "0.0"
    assert echoed.stated_churn_percent is not None and echoed.stated_churn_percent.as_tuple().exponent == -1
    assert compute_metrics_check(echoed) == first
    assert compute_metrics_check(echoed).checks[0].within_rounding is False


@pytest.mark.parametrize(
    ("stated", "spend", "within"),
    [
        ("12", "124", True),
        ("12.0", "124", False),
        ("12", "125", False),
        ("13", "125", True),
        ("12", "115", True),
        ("12", "114.99", False),
        ("1.2E+1", "124", True),
    ],
    ids=[
        "whole-month-rounds",
        "one-place-does-not",
        "half-goes-up-not-to-12",
        "half-goes-up-to-13",
        "half-below-rounds-up",
        "just-below-half",
        "exponent-form-whole",
    ],
)
def test_each_row_says_whether_the_stated_figure_is_a_rounding_of_the_computed_one(
    stated: str, spend: str, within: bool
) -> None:
    """Payback = spend / (10 x 100%): the stated figure is a rounding when the computed figure, rounded half away from
    zero to the stated figure's own places, is it (12.5 rounds to 13, never to 12; 11.5 rounds to 12)."""
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


# Payback = spend / (10 x 100%) months, beside the deck's figure, with the default 2% relative tolerance.
_PAYBACK = {"period_months": 12, "starting_recurring": "0", "new_recurring": "10", "gross_margin_percent": "100"}


@pytest.mark.parametrize(
    ("stated", "spend", "verdict", "within"),
    [
        ("12", "124", "consistent", True),
        ("12.0", "124", "mismatch", False),
        ("12.4", "124", "consistent", True),
        ("12", "125", "mismatch", False),
        ("13", "125", "consistent", True),
    ],
    ids=["12-against-12.40", "12.0-against-12.40", "exact", "12-against-12.5", "13-against-12.5"],
)
def test_a_figure_that_is_the_computed_one_rounded_to_its_places_is_consistent_past_the_tolerance(
    stated: str, spend: str, verdict: str, within: bool
) -> None:
    """The operator's ruling: a stated 12 months against a computed 12.40 is consistent, though 0.4 months is past 2%
    of 12.4 (0.248); "12.0" claims a place 12.4 does not round to. At the half, 12.5 rounds away from zero to 13: 13
    holds and 12 does not (12.5 - 12 = 0.5 is past 2% of 12.5 as well)."""
    result = metrics_check(**_PAYBACK, sales_marketing_spend=spend, stated_cac_payback_months=stated)

    (row,) = result.checks
    assert (row.verdict, row.within_rounding, result.verdict) == (verdict, within, verdict)
    assert "consistent_beyond_rounding" not in result.flags


@pytest.mark.parametrize(
    ("churned", "points", "verdict", "within"),
    [
        ("2.4", "0.5", "consistent", True),
        ("2.4", "0.1", "consistent", True),
        ("2.6", "0.5", "mismatch", False),
        ("2.5", "0.1", "mismatch", False),
        ("1.5", "0.1", "consistent", True),
    ],
    ids=["2.4-default", "2.4-tight-tolerance", "2.6", "2.5-rounds-up-to-3", "1.5-rounds-up-to-2"],
)
def test_a_stated_2_percent_churn_holds_on_what_rounds_to_2(
    churned: str, points: str, verdict: str, within: bool
) -> None:
    """The ruling's churn: "2%" monthly against a computed 2.4% is consistent because 2.4 rounds to 2, even with the
    tolerance tightened to 0.1 points; against 2.6% it is not. 2.5% rounds to 3, 1.5% to 2."""
    result = metrics_check(
        period_months=1,
        starting_recurring="100",
        churned_recurring=churned,
        stated_churn_percent="2",
        stated_churn_basis="gross_revenue",
        tolerance_points=points,
    )

    (row,) = result.checks
    assert (row.verdict, row.within_rounding) == (verdict, within)


@pytest.mark.parametrize(
    ("typed", "churned", "verdict"),
    [("0.0", "40", "consistent"), ("0.0", "50", "mismatch"), ("0", "400", "consistent"), ("0", "500", "mismatch")],
    ids=["0.0-against-0.04", "0.0-against-0.05", "0-against-0.4", "0-against-0.5"],
)
def test_a_stated_zero_rounds_from_the_places_it_is_typed_with(typed: str, churned: str, verdict: str) -> None:
    """No tolerance, so only the rounding decides: "0.0" holds a computed 0.04% (0.0 to one place) and not 0.05%
    (0.1); "0" holds 0.4% and not 0.5% (half away from zero, to 1)."""
    result = metrics_check(
        period_months=1,
        starting_recurring="100000",
        churned_recurring=churned,
        stated_churn_percent=typed,
        stated_churn_basis="gross_revenue",
        tolerance_points="0",
    )

    (row,) = result.checks
    assert (row.verdict, row.within_rounding) == (verdict, verdict == "consistent")


@pytest.mark.parametrize(
    ("stated", "verdict"),
    [("-2", "consistent"), ("-3", "mismatch"), ("-1.6", "consistent"), ("-1.5", "mismatch")],
)
def test_a_negative_figure_rounds_half_away_from_zero(stated: str, verdict: str) -> None:
    """Net revenue churn (1,550 - 3,100)/100k = -1.55%, no tolerance: -1.55 rounds to -2 (not -1) and to -1.6 (not
    -1.5), away from zero as a positive figure does."""
    result = metrics_check(
        period_months=1,
        starting_recurring="100000",
        expansion_recurring="3100",
        churned_recurring="1550",
        stated_churn_percent=stated,
        stated_churn_basis="net_revenue",
        tolerance_points="0",
    )

    (row,) = result.checks
    assert row.computed is not None and row.computed.exact == Fraction(-155, 10000)
    assert (row.verdict, row.within_rounding) == (verdict, verdict == "consistent")


def test_a_cause_flag_reads_the_other_definition_by_the_tolerance_alone() -> None:
    """The rounding rule decides verdicts, not causes. Spend 124 on 10 of new monthly revenue at 50% margin: 24.8
    months on gross margin, 12.4 on revenue alone. A stated "12.3" is within 2% of 12.4 (0.248), so the flag names that
    cause; a stated "12" is 12.4 rounded to its places but 0.4 months off it, so no flag."""
    parts = {**_PAYBACK, "gross_margin_percent": "50", "sales_marketing_spend": "124"}
    within = metrics_check(**parts, stated_cac_payback_months="12.3")
    rounded = metrics_check(**parts, stated_cac_payback_months="12")

    assert [row.verdict for row in within.checks] == [row.verdict for row in rounded.checks] == ["mismatch"]
    assert "stated_payback_not_margin_adjusted" in within.flags
    assert "stated_payback_not_margin_adjusted" not in rounded.flags


@pytest.mark.parametrize(
    ("churned", "burn", "stated"),
    [("5", "180", "2"), ("7.5", "60", "1")],
    ids=["2x-against-1.5x-on-new", "1x-against-0.5x-on-new"],
)
def test_a_stated_multiple_that_is_only_the_new_arr_multiple_rounded_names_no_cause(
    churned: str, burn: str, stated: str
) -> None:
    """New ARR 12·10 = 120. Burn 180: 1.5x on new ARR, 3x on net new (12·5 = 60); a deck's 2x is 1.5 rounded, not
    within 2% of it. Burn 60 with 7.5 churned: 0.5x on new, 2x on net new (30); a deck's 1x is 0.5 rounded."""
    result = metrics_check(
        period_months=12,
        starting_recurring="100",
        new_recurring="10",
        churned_recurring=churned,
        net_burn=burn,
        stated_burn_multiple=stated,
    )

    assert [row.verdict for row in result.checks] == ["mismatch"]
    assert "stated_burn_multiple_uses_new_not_net_arr" not in result.flags


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


@pytest.mark.parametrize(
    ("stated", "basis", "against", "verdict"),
    [
        ("1200000", "month", 1_200_000, "consistent"),
        ("1176000", "movement", 1_176_000, "consistent"),
        ("1300000", "movement", 1_176_000, "mismatch"),
    ],
    ids=["the-months", "the-movements", "neither"],
)
def test_a_stated_arr_holds_against_either_arr_and_the_result_says_which(
    stated: str, basis: str, against: int, verdict: str
) -> None:
    """Movement 12·98k = 1.176M, the latest month 12·100k = 1.2M, 2% apart and more: a deck's 1.2M is the month's ARR
    and holds against it, 1.176M holds against the movement's, and 1.3M, within 2% of neither, is a mismatch against
    the movement's. The flag says the founder's two sets of parts disagree whatever the verdict."""
    result = metrics_check(
        period_months=12,
        starting_recurring="80000",
        new_recurring="18000",
        month_total_revenue="100000",
        stated_arr=stated,
    )

    assert _checks(result) == {("arr", None): (Fraction(int(stated)), Fraction(against), verdict)}
    assert result.verdict == verdict
    assert result.arr_basis == basis
    assert "arr_movement_and_month_disagree" in result.flags
    assert "stated_arr_matches_run_rate" not in result.flags


def test_a_stated_arr_within_the_tolerance_of_the_months_alone_holds_with_no_disagreement() -> None:
    """Movement 12·100 = 1,200 and the month 12·102 = 1,224 agree (24 apart, 2% of 1,200, the edge included); a
    stated 1,248 is 48 off the movement's but 24 off the month's (2% of 1,224 is 24.48), so it holds against the
    month's, with no disagreement flag."""
    result = metrics_check(period_months=1, starting_recurring="100", month_total_revenue="102", stated_arr="1248")

    assert _checks(result) == {("arr", None): (Fraction(1248), Fraction(1224), "consistent")}
    assert result.arr_basis == "month"
    assert result.flags == ()


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
    assert {row.key for row in metrics_check(**METRICS_DL).assumptions} >= {
        "ltv_rule",
        "rule_of_40_rule",
        "magic_number_rule",
    }
    assert not {"ltv_rule", "rule_of_40_rule", "magic_number_rule"} & full


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
        ({"contribution_margin_percent": "50"}, "contribution_margin_percent needs arpa"),
        ({"ltv_churn_basis": "logo"}, "ltv_churn_basis needs arpa"),
        (
            {"starting_recurring": "100", "churned_recurring": "5", "arpa": "10"},
            "arpa needs contribution_margin_percent or gross_margin_percent: LTV is worked on a margin, never on "
            "revenue alone",
        ),
        (
            {"starting_recurring": "100", "arpa": "10", "gross_margin_percent": "50"},
            "arpa needs gross revenue churn above 0 in the period to work LTV (starting_recurring above 0 and some "
            "contraction or churn; ltv_churn_basis picks another churn): with no churn the lifetime has no end, so "
            "LTV does not compute",
        ),
        (
            {"arpa": "10", "gross_margin_percent": "50"},
            "arpa needs gross revenue churn above 0 in the period to work LTV",
        ),
        (
            {**_LTV_PARTS, "expansion_recurring": "5", "ltv_churn_basis": "net_revenue"},
            "arpa needs net revenue churn above 0 in the period to work LTV (starting_recurring above 0 and "
            "contraction plus churn above expansion;",
        ),
        (
            {**_LTV_PARTS, "customers_start": 10, "customers_lost": 0, "ltv_churn_basis": "logo"},
            "arpa needs logo churn above 0 in the period to work LTV (customers_start above 0 and customers_lost "
            "above 0;",
        ),
        (
            {"arpa": "10", "gross_margin_percent": "50", "ltv_churn_basis": "logo"},
            "arpa needs logo churn above 0 in the period to work LTV",
        ),
        ({**_LTV_PARTS, "contribution_margin_percent": "0"}, "greater than 0"),
        ({"revenue_growth_percent": "30"}, "revenue_growth_percent needs profit_margin_percent: the Rule of 40 adds"),
        ({"profit_margin_percent": "10"}, "profit_margin_percent needs revenue_growth_percent"),
        ({"profit_margin_basis": "net"}, "profit_margin_basis needs profit_margin_percent"),
        ({"revenue_growth_percent": "-100.5", "profit_margin_percent": "1"}, "greater than or equal to -100"),
        (
            {"quarter_revenue": "1"},
            "quarter_revenue needs prior_quarter_revenue: the magic number compares two consecutive quarters",
        ),
        ({"prior_quarter_ending_arr": "1"}, "prior_quarter_ending_arr needs quarter_ending_arr"),
        (
            {**_MAGIC_PARTS, "quarter_ending_arr": "1", "prior_quarter_ending_arr": "1"},
            "give the magic number's quarters as revenue (quarter_revenue, prior_quarter_revenue) or as ARR "
            "(quarter_ending_arr, prior_quarter_ending_arr), not both",
        ),
        (
            {"quarter_ending_arr": "2", "prior_quarter_ending_arr": "1"},
            "quarter_ending_arr needs prior_quarter_sales_marketing_spend",
        ),
        (
            {"prior_quarter_sales_marketing_spend": "1"},
            "prior_quarter_sales_marketing_spend needs quarter_revenue and prior_quarter_revenue, or "
            "quarter_ending_arr and prior_quarter_ending_arr",
        ),
        ({"stated_ltv": "1"}, f"stated_ltv needs arpa {_NEEDS}"),
        (
            {**_LTV_PARTS, "stated_ltv_to_cac": "3"},
            f"stated_ltv_to_cac needs arpa, sales_marketing_spend and customers_new above 0 {_NEEDS}",
        ),
        (
            {"stated_rule_of_40_percent": "40"},
            f"stated_rule_of_40_percent needs revenue_growth_percent and profit_margin_percent {_NEEDS}",
        ),
        ({"stated_magic_number": "1"}, "stated_magic_number needs quarter_revenue and prior_quarter_revenue, or"),
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
        "contribution-margin-without-arpa",
        "ltv-churn-basis-without-arpa",
        "arpa-without-a-margin",
        "arpa-with-no-churn",
        "arpa-with-nothing-at-the-start",
        "arpa-with-net-churn-at-zero",
        "arpa-with-no-logo-lost",
        "arpa-with-no-customer-counts",
        "contribution-margin-zero",
        "growth-without-margin",
        "margin-without-growth",
        "margin-basis-without-margin",
        "growth-below-minus-100",
        "quarter-without-prior",
        "prior-arr-without-quarter-arr",
        "both-magic-number-variants",
        "quarters-without-spend",
        "spend-without-quarters",
        "ltv-without-arpa",
        "ltv-to-cac-without-cac",
        "rule-of-40-without-parts",
        "magic-number-without-quarters",
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
