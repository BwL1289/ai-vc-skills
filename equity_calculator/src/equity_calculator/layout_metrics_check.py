"""A metrics check's report lines (the ``Metrics check`` sheet): the parts as given, each metric, the checks, flags.

One value column. The parts as given come first, then the ARR figures and which one a stated ARR is checked against,
retention and churn (each labelled with its period, never annualised), CAC and payback, the burn multiple,
concentration and the payback benchmark in force, then each stated figure checked (stated, computed, difference,
whether it is a rounding of the computed figure, verdict; an unlabelled churn once per basis; a burn multiple with no
multiple to work shows "none" and not_checked), the flags in plain words, and the overall verdict. Values only: no
line carries a live formula. When a starting-customers figure is given, retention and revenue churn print primed
letters (C' for the starting customers' own contraction, else the period's total).
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import from_percent, quantity
from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_metrics_check import (
    MetricsCheck,
    MetricsCheckInput,
    MetricsCheckResult,
    MetricsFlag,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no
from equity_calculator.text import display

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
# The same formulas with the starting customers' own movements, printed when any ``cohort_*`` figure is given.
_PRIMED_HOW = {
    "grr": "(S - C' - X')/S",
    "nrr": "(S + E' - C' - X')/S",
    "gross_revenue": "(C' + X')/S",
    "net_revenue": "(C' + X' - E')/S",
}
_PRIMED_NOTE = "; E', C', X' the starting customers' own when given, else the period's total"
_UNCHECKED_BURN_MULTIPLE = "none"
_ROUNDING_HOW = "the computed figure, rounded to the places the deck writes, is the deck's (within half its last place)"


def _months(count: int) -> str:
    """``count`` months in words: "1 month", "12 months"."""
    return "1 month" if count == 1 else f"{count} months"


def _flag_words(flag: MetricsFlag, result: MetricsCheckResult) -> str:
    """What a flag means for the founder, in plain words, and what a VC is likely to ask."""
    inputs = result.inputs
    period = _months(inputs.period_months)
    band = "none" if result.payback_band_months is None else f"{result.payback_band_months.rounded} months"
    payback_band = (
        f"CAC payback on gross margin is at or above the {band} benchmark"
        if result.cac_payback_months is not None
        else f"CAC payback on revenue alone is at or above the {band} benchmark, so on gross margin it is too (a "
        "margin only lengthens it)"
    )
    movement = "none" if result.ending_arr is None else display(result.ending_arr)
    month = "none" if result.month_arr is None else display(result.month_arr)
    # Only a stated multiple is left unchecked, and only then can the overall verdict not be consistent.
    unchecked = (
        "; a stated multiple is not checked, and the overall verdict cannot be consistent"
        if inputs.stated_burn_multiple is not None
        else ""
    )
    unlabelled = (
        "The churn figure names no basis; below zero it can only be net revenue churn, so it was checked on that "
        "alone; label it net revenue churn"
        if inputs.stated_churn_percent is not None and inputs.stated_churn_percent < 0
        else "The churn figure names no basis, so it was checked on every basis these figures give; label it logo, "
        "gross revenue or net revenue churn"
    )
    words: dict[MetricsFlag, str] = {
        "stated_arr_matches_run_rate": "The stated ARR matches the run-rate (12 x the whole month's revenue), not "
        "recurring revenue; a VC is likely to recompute ARR without one-time, services and usage fees",
        "run_rate_includes_non_recurring": "The latest month has one-time or usage revenue, so its run-rate is above "
        "its ARR; say which figure the document shows",
        "stated_nrr_includes_new": "The stated net retention matches ending over starting recurring revenue, which "
        "counts revenue from customers who were not there at the start (new customers, or their expansion); a VC is "
        "likely to ask for the starting customers alone",
        "arr_movement_and_month_disagree": f"The movement's ending ARR ({movement}) and the latest month's ARR "
        f"({month}) differ by more than {inputs.tolerance_percent:f}%, so the parts disagree with each other; a stated "
        "ARR is checked against the movement's: say which figure the document shows and why the two differ",
        "consistent_beyond_rounding": "A stated figure is within the tolerance but is not the computed figure rounded "
        "to the places it is written with; a VC recomputing gets a different figure: quote the calculator's",
        "mismatch_within_rounding": "A stated figure is past the tolerance but is the computed figure rounded to the "
        "places it is written with, so the gap may be rounding alone; give it with more places",
        "expansion_hides_churn": "Expansion covers the revenue lost, so net revenue churn is zero or below while "
        "gross revenue churn is not; show both, as a VC is likely to ask what was lost",
        "churn_basis_unlabelled": unlabelled,
        "blended_cac_only": "CAC is blended over every new customer; a VC is likely to ask for paid CAC, over the "
        "customers paid channels brought in",
        "payback_not_margin_adjusted": "No gross margin was given, so CAC payback is on revenue only and shorter than "
        "on gross margin; give the margin",
        "stated_payback_not_margin_adjusted": "The stated payback matches the revenue-only payback, not the payback "
        "on gross margin; Bessemer measures it after gross margin, so a VC may recompute it that way",
        "stated_burn_multiple_uses_new_not_net_arr": "The stated burn multiple matches net burn over new ARR only, "
        "not over net new ARR after churn and contraction",
        "burn_multiple_not_defined": "Net new ARR is zero or below in the period, so there is no burn multiple"
        + unchecked,
        "no_net_burn": f"Net burn is zero or below in the period, so there is no burn multiple{unchecked}",
        "payback_above_band": f"{payback_band}; a VC is likely to ask how it comes down (a benchmark, not a rule)",
        "burn_multiple_above_band": f"The burn multiple is at or above {inputs.burn_multiple_band:f}x; a VC is likely "
        "to ask what the spend buys (a benchmark, not a rule)",
        "net_revenue_churn_above_band": f"Net revenue churn over {period} is above "
        f"{inputs.net_revenue_churn_band_percent:f}%; a VC is likely to ask what is driving it (a benchmark, not a "
        "rule)",
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


def _cohort_given(inputs: MetricsCheckInput) -> bool:
    """Whether any starting-customers figure was given (retention and revenue churn then use it)."""
    return any(
        value is not None
        for value in (
            inputs.cohort_expansion_recurring,
            inputs.cohort_contraction_recurring,
            inputs.cohort_churned_recurring,
        )
    )


def _retention_how(inputs: MetricsCheckInput, key: str, plain: str) -> str:
    """A retention or revenue churn formula: primed, with what the primes mean, when a cohort figure is given."""
    return f"{_PRIMED_HOW[key]}{_PRIMED_NOTE}" if _cohort_given(inputs) else plain


def _metric_lines(result: MetricsCheckResult) -> list[Line]:
    """Each metric worked, labelled with its period where it is over the period, and the payback benchmark."""
    inputs = result.inputs
    period = _months(inputs.period_months)
    arr_basis = None if result.arr_basis is None else _ARR_BASIS_WORDS[result.arr_basis]
    metrics: list[tuple[str, str, EquityQuantity | str | None, str]] = [
        ("starting_arr", "ARR at the start of the period", result.starting_arr, "k·S"),
        ("ending_arr", "ARR at the end of the period", result.ending_arr, "k·(S + N + E - C - X)"),
        ("net_new_arr", "Net new ARR", result.net_new_arr, "k·(N + E - C - X)"),
        ("new_arr", "New ARR", result.new_arr, "k·N"),
        ("month_arr", "ARR from the latest month", result.month_arr, "12·(T - O - U)"),
        ("run_rate", "Run-rate (12 x the month's revenue)", result.run_rate, "12·T"),
        ("arr_basis", "A stated ARR is checked against", arr_basis, "the movement when given, else the month"),
        (
            "grr",
            f"Gross revenue retention ({period})",
            result.gross_revenue_retention,
            _retention_how(inputs, "grr", "(S - C - X)/S"),
        ),
        (
            "nrr",
            f"Net revenue retention ({period})",
            result.net_revenue_retention,
            _retention_how(inputs, "nrr", "(S + E - C - X)/S"),
        ),
        (
            "gross_churn",
            f"Gross revenue churn ({period})",
            result.gross_revenue_churn,
            _retention_how(inputs, "gross_revenue", "(C + X)/S"),
        ),
        (
            "net_churn",
            f"Net revenue churn ({period})",
            result.net_revenue_churn,
            _retention_how(inputs, "net_revenue", "(C + X - E)/S"),
        ),
        ("logo_churn", f"Logo churn ({period})", result.logo_churn, "customers lost / at the start"),
        ("logo_retention", f"Logo retention ({period})", result.logo_retention, "1 - logo churn"),
        ("blended_cac", "CAC, blended", result.blended_cac, "spend / new customers"),
        ("paid_cac", "CAC, paid", result.paid_cac, "spend / new customers from paid channels"),
        ("payback", "CAC payback (gross margin)", result.cac_payback_months, "spend/(new monthly recurring·margin)"),
        ("revenue_payback", "CAC payback (revenue only)", result.revenue_payback_months, "spend/new monthly recurring"),
        ("burn_multiple", "Burn multiple", result.burn_multiple, "net burn / net new ARR"),
        ("burn_multiple_new", "Burn multiple on new ARR only", result.burn_multiple_on_new_arr, "net burn / new ARR"),
        ("concentration", "Customer concentration", result.concentration, "largest customer / period revenue"),
        (
            "payback_band",
            "CAC payback benchmark",
            result.payback_band_months,
            "the band given, else the segment's"
            + (
                ""
                if result.cac_payback_months is not None
                else "; on gross margin, so applied to the revenue-only " "payback as a floor (no margin given)"
            ),
        ),
    ]
    lines = [Line(key, label, (value,), how) for key, label, value, how in metrics if value is not None]
    if result.burn_multiple is not None:
        band = given("multiplier", inputs.burn_multiple_band)
        lines.append(Line("burn_multiple_band", "Burn multiple benchmark", (band,), GIVEN))
    if inputs.period_months == 1 and result.net_revenue_churn is not None:
        band = given_percent(inputs.net_revenue_churn_band_percent)
        lines.append(Line("net_revenue_churn_band", "Net revenue churn benchmark (1 month)", (band,), GIVEN))
    return lines


def _verdict_how(check: MetricsCheck, inputs: MetricsCheckInput) -> str:
    """How a checked figure's verdict is read; a mismatch whose difference rounds to the tolerance says it is just
    over it, so the row never reads as a difference equal to the tolerance marked a mismatch."""
    how = "within the tolerance is consistent"
    if check.verdict != "mismatch" or check.computed is None or check.difference is None:
        return how
    unit = check.stated.unit
    if unit == "fraction":
        tolerance = from_percent(inputs.tolerance_points)
    else:
        tolerance = from_percent(inputs.tolerance_percent) * abs(check.computed.exact)
    if quantity(unit, abs(check.difference.exact)).rounded == quantity(unit, tolerance).rounded:
        return f"{how}; this one is just over the tolerance, by less than the last place shown"
    return how


def _check_lines(check: MetricsCheck, inputs: MetricsCheckInput) -> list[Line]:
    """One check: what the document says, what the calculator gives, the difference, whether the stated figure is a
    rounding of the computed one, and the verdict; a figure with nothing to check it against says so."""
    if check.basis is None:
        name, key = _CHECK_NAMES[check.key], f"check_{check.key}"
        how = _CHECK_HOW[check.key]
        if check.key in ("grr", "nrr"):
            how = _retention_how(inputs, check.key, how)
    else:
        name = f"{_CHECK_NAMES[check.key]} ({_BASIS_NAMES[check.basis]})"
        how, key = _CHURN_HOW[check.basis], f"check_{check.key}_{check.basis}"
        if check.basis != "logo":
            how = _retention_how(inputs, check.basis, how)
    lines = [Line(f"{key}_stated", f"{name}: the deck says", (check.stated,), GIVEN)]
    if check.computed is None or check.difference is None:
        lines.append(
            Line(
                f"{key}_computed",
                f"{name}: the calculator gives",
                (_UNCHECKED_BURN_MULTIPLE,),
                "no multiple: net burn or net new ARR is zero or below",
            )
        )
        verdict_how = "nothing to check it against, so the overall verdict cannot be consistent"
    else:
        lines += [
            Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), how),
            Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
        ]
        verdict_how = _verdict_how(check, inputs)
    if check.within_rounding is not None:
        lines.append(
            Line(f"{key}_rounding", f"{name}: rounds to the deck's", (yes_no(check.within_rounding),), _ROUNDING_HOW)
        )
    lines.append(Line(f"{key}_verdict", f"{name}: verdict", (check.verdict,), verdict_how, verdict=True))
    return lines


def metrics_check_sheet(result: MetricsCheckResult) -> Sheet:
    """The metrics check's lines: the parts, the metrics, each check, the flags and the overall verdict."""
    lines = [*_given_lines(result), *_metric_lines(result)]
    for check in result.checks:
        lines += _check_lines(check, result.inputs)
    lines += [
        Line(f"flag_{flag}", "A VC is likely to ask", (flag,), _flag_words(flag, result)) for flag in result.flags
    ]
    lines.append(
        Line(
            "verdict",
            "Overall verdict",
            (result.verdict,),
            "mismatch if any figure is (an unlabelled churn holds when any basis does); else not_checked with none "
            "checked or one left unchecked; else consistent",
            verdict=True,
        )
    )

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
