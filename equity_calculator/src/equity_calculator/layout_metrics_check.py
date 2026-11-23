"""A metrics check's report lines (the ``Metrics check`` sheet): the parts as given, each metric, the checks, flags.

One value column. The parts as given come first, then the ARR figures and which one a stated ARR is checked against,
retention and churn (each labelled with its period, never annualised), CAC and payback, the burn multiple,
concentration and the payback benchmark in force, then each stated figure checked (stated, computed, difference,
verdict; an unlabelled churn once per basis), the flags in plain words, and the overall verdict. Values only: no line
carries a live formula.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_metrics_check import (
    MetricsCheck,
    MetricsCheckInput,
    MetricsCheckResult,
    MetricsFlag,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent

_TITLE = "Metrics check"
_HEADING = (
    "Traction metrics worked from their parts: ARR, retention, churn, CAC payback, burn multiple, the document's "
    "figures"
)
_COLUMNS = ("These figures",)
_UNIT_NAMES = {"monthly": "monthly", "annual": "annual"}
_BASIS_NAMES = {"logo": "logo", "gross_revenue": "gross revenue", "net_revenue": "net revenue"}
_ARR_BASIS_WORDS = {
    "movement": "the movement's ending ARR",
    "month": "the latest month's ARR",
}
_CHECK_NAMES = {
    "arr": "ARR",
    "nrr": "Net revenue retention",
    "grr": "Gross revenue retention",
    "churn": "Churn",
    "cac": "CAC",
    "cac_payback": "CAC payback",
    "burn_multiple": "Burn multiple",
    "concentration": "Customer concentration",
}
_CHECK_HOW = {
    "arr": "the movement's ending ARR, else the latest month's",
    "nrr": "(S + E - C - X)/S",
    "grr": "(S - C - X)/S",
    "cac": "spend / new customers (blended)",
    "cac_payback": "spend/(new monthly recurring·margin), or on revenue with no margin",
    "burn_multiple": "net burn / net new ARR",
    "concentration": "largest customer / period revenue",
}
_CHURN_HOW = {
    "logo": "customers lost / customers at the start",
    "gross_revenue": "(C + X)/S",
    "net_revenue": "(C + X - E)/S",
}


def _months(count: int) -> str:
    """``count`` months in words: "1 month", "12 months"."""
    return "1 month" if count == 1 else f"{count} months"


def _flag_words(flag: MetricsFlag, result: MetricsCheckResult) -> str:
    """What a flag means for the founder, in plain words, and what a VC is likely to ask."""
    inputs = result.inputs
    period = _months(inputs.period_months)
    band = "none" if result.payback_band_months is None else f"{result.payback_band_months.rounded} months"
    words: dict[MetricsFlag, str] = {
        "stated_arr_matches_run_rate": "The stated ARR matches the run-rate (12 x the whole month's revenue), not "
        "recurring revenue; a VC will recompute ARR without one-time, services and usage fees",
        "run_rate_includes_non_recurring": "The latest month has one-time or usage revenue, so its run-rate is above "
        "its ARR; say which figure the document shows",
        "stated_nrr_includes_new": "The stated net retention matches ending over starting recurring revenue, which "
        "counts new customers; a VC will ask for the starting customers alone",
        "expansion_hides_churn": "Expansion covers the revenue lost, so net revenue churn is zero or below while "
        "gross revenue churn is not; show both, as a VC will ask what was lost",
        "churn_basis_unlabelled": "The churn figure names no basis, so it was checked on every basis these figures "
        "give; label it logo, gross revenue or net revenue churn",
        "blended_cac_only": "CAC is blended over every new customer; a VC is likely to ask for paid CAC, over the "
        "customers paid channels brought in",
        "payback_not_margin_adjusted": "No gross margin was given, so CAC payback is on revenue only and shorter than "
        "on gross margin; give the margin",
        "stated_payback_not_margin_adjusted": "The stated payback matches the revenue-only payback, not the payback "
        "on gross margin; a VC measures it after gross margin",
        "stated_burn_multiple_uses_new_not_net_arr": "The stated burn multiple matches net burn over new ARR only, "
        "not over net new ARR after churn and contraction",
        "burn_multiple_not_defined": "Net new ARR is zero or below in the period, so there is no burn multiple; a "
        "stated multiple is not checked",
        "no_net_burn": "Net burn is zero or below in the period, so there is no burn multiple; a stated multiple is "
        "not checked",
        "payback_above_band": f"CAC payback on gross margin is at or above the {band} benchmark; a VC is likely to "
        "ask how it comes down (a benchmark, not a rule)",
        "burn_multiple_above_band": f"The burn multiple is at or above {inputs.burn_multiple_band}x; a VC is likely "
        "to ask what the spend buys (a benchmark, not a rule)",
        "net_revenue_churn_above_band": f"Net revenue churn over {period} is above "
        f"{inputs.net_revenue_churn_band_percent}%; a VC is likely to ask what is driving it (a benchmark, not a rule)",
    }
    return words[flag]


def _maybe(unit: EquityUnit, value: Decimal | None) -> EquityQuantity | None:
    return None if value is None else given(unit, value)


def _maybe_percent(value: Decimal | None) -> EquityQuantity | None:
    return None if value is None else given_percent(value)


def _maybe_count(value: int | None) -> EquityQuantity | None:
    return None if value is None else given("shares", Decimal(value))


def _movement_lines(inputs: MetricsCheckInput) -> list[tuple[str, str, EquityQuantity | str | None]]:
    """The recurring revenue at the start and its movement, shown only when the movement is given."""
    if inputs.starting_recurring is None:
        return []

    unit = _UNIT_NAMES[inputs.recurring_unit]
    return [
        (
            "starting_recurring",
            f"Recurring revenue at the start ({unit}, S)",
            given("money", inputs.starting_recurring),
        ),
        ("new_recurring", f"New recurring revenue ({unit}, N)", given("money", inputs.new_recurring)),
        ("expansion_recurring", f"Expansion ({unit}, E)", given("money", inputs.expansion_recurring)),
        ("contraction_recurring", f"Contraction ({unit}, C)", given("money", inputs.contraction_recurring)),
        ("churned_recurring", f"Churned ({unit}, X)", given("money", inputs.churned_recurring)),
        (
            "cohort_expansion",
            "Expansion, starting customers only",
            _maybe("money", inputs.cohort_expansion_recurring),
        ),
        (
            "cohort_contraction",
            "Contraction, starting customers only",
            _maybe("money", inputs.cohort_contraction_recurring),
        ),
        ("cohort_churned", "Churned, starting customers only", _maybe("money", inputs.cohort_churned_recurring)),
    ]


def _given_lines(result: MetricsCheckResult) -> list[Line]:
    """The parts as given and each figure the document states, then the tolerances and bands in use."""
    inputs = result.inputs
    checked = bool(result.checks)
    month = inputs.month_total_revenue is not None
    basis = None if inputs.stated_churn_percent is None else inputs.stated_churn_basis.replace("_", " ")
    shown: list[tuple[str, str, EquityQuantity | str | None]] = [
        ("period", "Period", _months(inputs.period_months)),
        *_movement_lines(inputs),
        ("month_total_revenue", "Latest month's revenue (T)", _maybe("money", inputs.month_total_revenue)),
        ("month_one_time", "of which one-time (O)", given("money", inputs.month_one_time_revenue) if month else None),
        ("month_usage", "of which usage (U)", given("money", inputs.month_usage_revenue) if month else None),
        ("customers_start", "Customers at the start", _maybe_count(inputs.customers_start)),
        ("customers_lost", "Customers lost", _maybe_count(inputs.customers_lost)),
        ("customers_new", "New customers", _maybe_count(inputs.customers_new)),
        ("customers_new_paid", "New customers from paid channels", _maybe_count(inputs.customers_new_paid)),
        ("spend", "Sales and marketing spend", _maybe("money", inputs.sales_marketing_spend)),
        ("gross_margin", "Gross margin", _maybe_percent(inputs.gross_margin_percent)),
        ("net_burn", "Net burn", _maybe("money", inputs.net_burn)),
        ("largest_customer", "Largest customer's revenue", _maybe("money", inputs.largest_customer_revenue)),
        ("period_revenue", "Revenue in the period", _maybe("money", inputs.period_revenue)),
        ("given_arr", "ARR as stated", _maybe("money", inputs.stated_arr)),
        ("given_nrr", "Net revenue retention as stated", _maybe_percent(inputs.stated_nrr_percent)),
        ("given_grr", "Gross revenue retention as stated", _maybe_percent(inputs.stated_grr_percent)),
        ("given_churn", "Churn as stated", _maybe_percent(inputs.stated_churn_percent)),
        ("given_churn_basis", "Churn basis as stated", basis),
        ("given_cac", "CAC as stated", _maybe("money", inputs.stated_cac)),
        ("given_payback", "CAC payback as stated", _maybe("months", inputs.stated_cac_payback_months)),
        ("given_burn_multiple", "Burn multiple as stated", _maybe("multiplier", inputs.stated_burn_multiple)),
        ("given_concentration", "Concentration as stated", _maybe_percent(inputs.stated_concentration_percent)),
        ("customer_segment", "Customer segment", inputs.customer_segment),
        ("tolerance_points", "Tolerance for a percent", given_percent(inputs.tolerance_points) if checked else None),
        (
            "tolerance_percent",
            "Tolerance for money, months or a multiple",
            given_percent(inputs.tolerance_percent) if checked else None,
        ),
    ]
    return [Line(key, label, (value,), GIVEN) for key, label, value in shown if value is not None]


def _metric_lines(result: MetricsCheckResult) -> list[Line]:
    """Each metric worked, labelled with its period where it is over the period, and the payback benchmark."""
    period = _months(result.inputs.period_months)
    arr_basis = None if result.arr_basis is None else _ARR_BASIS_WORDS[result.arr_basis]
    metrics: list[tuple[str, str, EquityQuantity | str | None, str]] = [
        ("starting_arr", "ARR at the start of the period", result.starting_arr, "k·S"),
        ("ending_arr", "ARR at the end of the period", result.ending_arr, "k·(S + N + E - C - X)"),
        ("net_new_arr", "Net new ARR", result.net_new_arr, "k·(N + E - C - X)"),
        ("new_arr", "New ARR", result.new_arr, "k·N"),
        ("month_arr", "ARR from the latest month", result.month_arr, "12·(T - O - U)"),
        ("run_rate", "Run-rate (12 x the month's revenue)", result.run_rate, "12·T"),
        ("arr_basis", "A stated ARR is checked against", arr_basis, "the movement when given, else the month"),
        ("grr", f"Gross revenue retention ({period})", result.gross_revenue_retention, "(S - C - X)/S"),
        ("nrr", f"Net revenue retention ({period})", result.net_revenue_retention, "(S + E - C - X)/S"),
        ("gross_churn", f"Gross revenue churn ({period})", result.gross_revenue_churn, "(C + X)/S"),
        ("net_churn", f"Net revenue churn ({period})", result.net_revenue_churn, "(C + X - E)/S"),
        ("logo_churn", f"Logo churn ({period})", result.logo_churn, "customers lost / at the start"),
        ("logo_retention", f"Logo retention ({period})", result.logo_retention, "1 - logo churn"),
        ("blended_cac", "CAC, blended", result.blended_cac, "spend / new customers"),
        ("paid_cac", "CAC, paid", result.paid_cac, "spend / new customers from paid channels"),
        ("payback", "CAC payback (gross margin)", result.cac_payback_months, "spend/(new monthly recurring·margin)"),
        ("revenue_payback", "CAC payback (revenue only)", result.revenue_payback_months, "spend/new monthly recurring"),
        ("burn_multiple", "Burn multiple", result.burn_multiple, "net burn / net new ARR"),
        ("burn_multiple_new", "Burn multiple on new ARR only", result.burn_multiple_on_new_arr, "net burn / new ARR"),
        ("concentration", "Customer concentration", result.concentration, "largest customer / period revenue"),
        ("payback_band", "CAC payback benchmark", result.payback_band_months, "the band given, else the segment's"),
    ]
    lines = [Line(key, label, (value,), how) for key, label, value, how in metrics if value is not None]
    if result.burn_multiple is not None:
        band = given("multiplier", result.inputs.burn_multiple_band)
        lines.append(Line("burn_multiple_band", "Burn multiple benchmark", (band,), GIVEN))
    if result.inputs.period_months == 1 and result.net_revenue_churn is not None:
        band = given_percent(result.inputs.net_revenue_churn_band_percent)
        lines.append(Line("net_revenue_churn_band", "Net revenue churn benchmark (1 month)", (band,), GIVEN))
    return lines


def _check_lines(check: MetricsCheck) -> list[Line]:
    """One check: what the document says, what the calculator gives, the difference and the verdict."""
    if check.basis is None:
        name, how, key = _CHECK_NAMES[check.key], _CHECK_HOW[check.key], f"check_{check.key}"
    else:
        name = f"{_CHECK_NAMES[check.key]} ({_BASIS_NAMES[check.basis]})"
        how, key = _CHURN_HOW[check.basis], f"check_{check.key}_{check.basis}"
    return [
        Line(f"{key}_stated", f"{name}: the deck says", (check.stated,), GIVEN),
        Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), how),
        Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
        Line(
            f"{key}_verdict", f"{name}: verdict", (check.verdict,), "within the tolerance is consistent", verdict=True
        ),
    ]


def metrics_check_sheet(result: MetricsCheckResult) -> Sheet:
    """The metrics check's lines: the parts, the metrics, each check, the flags and the overall verdict."""
    lines = [*_given_lines(result), *_metric_lines(result)]
    for check in result.checks:
        lines += _check_lines(check)
    lines += [
        Line(f"flag_{flag}", "A VC is likely to ask", (flag,), _flag_words(flag, result)) for flag in result.flags
    ]
    lines.append(
        Line(
            "verdict",
            "Overall verdict",
            (result.verdict,),
            "mismatch if any figure is (an unlabelled churn holds when any basis does); not_checked with none",
            verdict=True,
        )
    )

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
