"""A metrics check's report lines (the ``Metrics check`` sheet): the parts as given, each metric, the checks, flags.

One value column. The parts as given come first, then the ARR figures and which one a stated ARR is checked against,
retention and churn (each labelled with its period, never annualised), CAC and payback, the burn multiple,
concentration, LTV (labelled with its margin) and LTV/CAC, the Rule of 40 (labelled with its margin), the magic number
(labelled with its variant) and the payback benchmark in force, then each stated figure checked (stated, computed,
difference, whether the figure as typed is a rounding of the computed one, which is consistent even past the tolerance,
verdict; an unlabelled churn once per basis; a burn multiple with no multiple to work shows "none" and not_checked), the
flags in plain words, and the overall verdict. Values only: no line carries a live formula. When a starting-customers
figure is given, retention and revenue churn print primed letters (C' for the starting customers' own contraction, else
the period's total).
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import from_percent, quantity
from equity_calculator.rounding import ROUNDING_HOW, ROUNDING_VERDICT_HOW, rounding_label
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
    "Traction metrics worked from their parts: ARR, retention, churn, CAC payback, burn multiple, LTV, the Rule of 40, "
    "the magic number, the document's figures"
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
    "ltv": "LTV",
    "ltv_to_cac": "LTV/CAC",
    "rule_of_40": "Rule of 40",
    "magic_number": "Magic number",
}
_CHECK_HOW = {
    "arr": "the movement's ending ARR or the latest month's",
    "nrr": "(S + E - C - X)/S",
    "grr": "(S - C - X)/S",
    "cac": "spend / new customers (blended)",
    "cac_payback": "spend/(new monthly recurring·margin), or on revenue with no margin",
    "burn_multiple": "net burn / net new ARR",
    "concentration": "largest customer / period revenue",
    "ltv_to_cac": "LTV / blended CAC",
    "rule_of_40": "revenue growth + margin, as given",
}
# The magic number's working, by the variant the inputs give.
_MAGIC_HOW = {
    "revenue": "4·(quarter revenue - prior quarter's) / prior quarter's spend",
    "arr": "(quarter-end ARR - prior quarter's) / prior quarter's spend",
}
_LTV_MARGIN_NAMES = {"contribution": "contribution margin", "gross": "gross margin"}
_CHURN_WORDS = {"gross_revenue": "gross revenue churn", "net_revenue": "net revenue churn", "logo": "logo churn"}
# A profit margin's basis as the given line shows it.
_BASIS_WORDS = {
    "ebitda": "EBITDA",
    "operating": "operating",
    "free_cash_flow": "free cash flow",
    "net": "net",
    "unlabelled": "unlabelled",
}
_PROFIT_MARGIN_WORDS = {
    "ebitda": "EBITDA margin",
    "operating": "operating margin",
    "free_cash_flow": "free cash flow margin",
    "net": "net margin",
    "unlabelled": "margin, basis not named",
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
        "ARR within the tolerance of either is consistent: say which figure the document shows and why the two "
        "differ",
        "consistent_beyond_rounding": "A stated figure is consistent only by the tolerance: it is not the computed "
        "figure rounded to the places it is written with, so a VC recomputing gets a different figure; quote the "
        "calculator's",
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
        "ltv_on_gross_margin": "LTV is on gross margin, as no contribution margin was given; a16z works LTV on "
        "contribution margin, which also takes out the other costs that grow with each account, so a VC may work it "
        "lower: give the contribution margin",
        "stated_ltv_uses_revenue_not_margin": "A stated LTV or LTV/CAC matches the figure on revenue alone, with no "
        "margin taken out; a VC is likely to recompute it on margin",
        "rule_of_40_margin_basis_unlabelled": "The Rule of 40's margin names no basis; a VC is likely to ask which "
        "margin it adds (EBITDA, operating, free cash flow or net): name it beside the figure",
        "stated_rule_of_40_uses_gross_margin": "The stated Rule of 40 matches revenue growth plus gross margin, not "
        "plus a profit margin; a VC is likely to recompute it on profit",
        "stated_magic_number_not_annualised": "The stated magic number matches the quarter's revenue change over the "
        "prior quarter's spend without the 4 that annualises it; a VC is likely to recompute it with the 4",
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


def _later_given(inputs: MetricsCheckInput) -> list[tuple[str, str, EquityQuantity | str | None]]:
    """LTV's parts, the Rule of 40's two percents and the magic number's quarters, each shown only when given."""
    unit = _UNIT_NAMES[inputs.recurring_unit]
    ltv = inputs.arpa is not None
    margin = inputs.profit_margin_percent is not None
    return [
        ("arpa", f"Average revenue per account ({unit}, ARPA)", _maybe("money", inputs.arpa)),
        ("contribution_margin", "Contribution margin", _maybe_percent(inputs.contribution_margin_percent)),
        ("ltv_churn_basis", "LTV divides by", _CHURN_WORDS[inputs.ltv_churn_basis] if ltv else None),
        ("revenue_growth", "Revenue growth", _maybe_percent(inputs.revenue_growth_percent)),
        ("profit_margin", "Profit margin", _maybe_percent(inputs.profit_margin_percent)),
        ("profit_margin_basis", "Profit margin basis", _BASIS_WORDS[inputs.profit_margin_basis] if margin else None),
        ("quarter_revenue", "This quarter's revenue (Q)", _maybe("money", inputs.quarter_revenue)),
        ("prior_quarter_revenue", "The prior quarter's revenue (Q')", _maybe("money", inputs.prior_quarter_revenue)),
        ("quarter_ending_arr", "ARR at this quarter's end (A)", _maybe("money", inputs.quarter_ending_arr)),
        (
            "prior_quarter_ending_arr",
            "ARR at the prior quarter's end (A')",
            _maybe("money", inputs.prior_quarter_ending_arr),
        ),
        (
            "prior_quarter_spend",
            "The prior quarter's sales and marketing spend",
            _maybe("money", inputs.prior_quarter_sales_marketing_spend),
        ),
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
        *_later_given(inputs),
        ("given_arr", "ARR as stated", _maybe("money", inputs.stated_arr)),
        ("given_nrr", "Net revenue retention as stated", _maybe_percent(inputs.stated_nrr_percent)),
        ("given_grr", "Gross revenue retention as stated", _maybe_percent(inputs.stated_grr_percent)),
        ("given_churn", "Churn as stated", _maybe_percent(inputs.stated_churn_percent)),
        ("given_churn_basis", "Churn basis as stated", basis),
        ("given_cac", "CAC as stated", _maybe("money", inputs.stated_cac)),
        ("given_payback", "CAC payback as stated", _maybe("months", inputs.stated_cac_payback_months)),
        ("given_burn_multiple", "Burn multiple as stated", _maybe("multiplier", inputs.stated_burn_multiple)),
        ("given_concentration", "Concentration as stated", _maybe_percent(inputs.stated_concentration_percent)),
        ("given_ltv", "LTV as stated", _maybe("money", inputs.stated_ltv)),
        ("given_ltv_to_cac", "LTV/CAC as stated", _maybe("multiplier", inputs.stated_ltv_to_cac)),
        ("given_rule_of_40", "Rule of 40 as stated", _maybe_percent(inputs.stated_rule_of_40_percent)),
        ("given_magic_number", "Magic number as stated", _maybe("multiplier", inputs.stated_magic_number)),
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
        (
            "arr_basis",
            "A stated ARR is checked against",
            arr_basis,
            "the movement's when given, else the month's; the month's too when a stated ARR is within the tolerance of "
            "it alone",
        ),
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
        *_later_metrics(result),
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


def _later_metrics(result: MetricsCheckResult) -> list[tuple[str, str, EquityQuantity | str | None, str]]:
    """LTV and LTV/CAC (labelled with the margin and churn they use), the Rule of 40 (with its margin) and the magic
    number (with its variant), and each figure on the other definition worked beside a stated one."""
    inputs = result.inputs
    margin = "none" if result.ltv_margin_basis is None else _LTV_MARGIN_NAMES[result.ltv_margin_basis]
    churn = _CHURN_WORDS[inputs.ltv_churn_basis]
    variant = result.magic_number_variant
    on = "revenue" if variant == "revenue" else "ARR"
    return [
        ("ltv", f"LTV ({margin})", result.ltv, f"ARPA × the period's units × margin / {churn}"),
        ("ltv_on_revenue", "LTV on revenue alone", result.ltv_on_revenue, f"ARPA × the period's units / {churn}"),
        ("ltv_to_cac", "LTV/CAC", result.ltv_to_cac, "LTV / blended CAC"),
        ("ltv_to_cac_on_revenue", "LTV/CAC on revenue alone", result.ltv_to_cac_on_revenue, "LTV on revenue / CAC"),
        (
            "rule_of_40",
            f"Rule of 40 (growth + {_PROFIT_MARGIN_WORDS[inputs.profit_margin_basis]})",
            result.rule_of_40,
            "revenue growth + margin, as given",
        ),
        ("magic_number", f"Magic number (on {on})", result.magic_number, _MAGIC_HOW[variant or "revenue"]),
        (
            "magic_number_unannualised",
            "Magic number without the 4",
            result.magic_number_unannualised,
            "(quarter revenue - prior quarter's) / prior quarter's spend",
        ),
    ]


def _verdict_how(check: MetricsCheck, inputs: MetricsCheckInput) -> str:
    """How a checked figure's verdict is read (a percent, months or multiple also when it rounds to the deck's); a
    mismatch whose difference rounds to the tolerance says it is just over it, so the row never reads as a difference
    equal to the tolerance marked a mismatch."""
    how = "within the tolerance is consistent" if check.within_rounding is None else ROUNDING_VERDICT_HOW
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


def _typed(check: MetricsCheck, inputs: MetricsCheckInput) -> Decimal | None:
    """The stated percent, months or multiple as typed (percent points for a percent), its places kept; none for
    money."""
    typed: dict[str, Decimal | None] = {
        "nrr": inputs.stated_nrr_percent,
        "grr": inputs.stated_grr_percent,
        "churn": inputs.stated_churn_percent,
        "cac_payback": inputs.stated_cac_payback_months,
        "burn_multiple": inputs.stated_burn_multiple,
        "concentration": inputs.stated_concentration_percent,
        "ltv_to_cac": inputs.stated_ltv_to_cac,
        "rule_of_40": inputs.stated_rule_of_40_percent,
        "magic_number": inputs.stated_magic_number,
    }
    return typed.get(check.key)


def _check_lines(check: MetricsCheck, result: MetricsCheckResult) -> list[Line]:
    """One check: what the document says, what the calculator gives (for ARR, from which ARR), the difference, whether
    the stated figure as typed is a rounding of the computed one, and the verdict; a figure with nothing to check it
    against says so."""
    inputs = result.inputs
    if check.basis is None:
        name, key = _CHECK_NAMES[check.key], f"check_{check.key}"
        if check.key == "arr" and result.arr_basis is not None:
            how = _ARR_BASIS_WORDS[result.arr_basis]
        elif check.key == "magic_number":
            how = _MAGIC_HOW[result.magic_number_variant or "revenue"]
        elif check.key == "ltv":
            how = f"ARPA × the period's units × margin / {_CHURN_WORDS[inputs.ltv_churn_basis]}"
        else:
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
    typed = _typed(check, inputs)
    if check.within_rounding is not None and typed is not None:
        label = rounding_label(name, typed)
        lines.append(Line(f"{key}_rounding", label, (yes_no(check.within_rounding),), ROUNDING_HOW))
    lines.append(Line(f"{key}_verdict", f"{name}: verdict", (check.verdict,), verdict_how, verdict=True))
    return lines


def metrics_check_sheet(result: MetricsCheckResult) -> Sheet:
    """The metrics check's lines: the parts, the metrics, each check, the flags and the overall verdict."""
    lines = [*_given_lines(result), *_metric_lines(result)]
    for check in result.checks:
        lines += _check_lines(check, result)
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
