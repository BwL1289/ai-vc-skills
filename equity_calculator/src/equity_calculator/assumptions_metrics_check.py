"""The labelled assumptions of a metrics check, each with its source; a row appears only when the input uses it.

Five public sources are quoted word for word: a16z's "16 Startup Metrics" (churn, CAC) and "16 More Startup Metrics"
(ARR, customer concentration), Bessemer's "Scaling to $100 Million" (retention, the margin-adjusted payback and its
payback targets by customer segment), David Sacks's "The Burn Multiple" (the multiple and its 3x line) and David
Skok's "SaaS Metrics 2.0" (the 2%-a-month net revenue churn line). Each was read in full on 23 Nov 2026, text only
(charts, images and embedded slides not seen). The three benchmark lines are questions, never errors, and inputs the
founder can change. The period rule, the cohort rule, which customers net retention leaves out, the exact payback
formula and the tolerances are marked unverified: modelling choices or arithmetic no source read fixes.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_metrics_check import (
    DEFAULT_BURN_MULTIPLE_BAND,
    DEFAULT_NET_REVENUE_CHURN_BAND_PERCENT,
    MetricsCheckInput,
    payback_band,
)

__all__ = [
    "A16Z_METRICS_SOURCE",
    "A16Z_MORE_METRICS_SOURCE",
    "BESSEMER_SOURCE",
    "BURN_MULTIPLE_BAND_QUOTE",
    "NET_REVENUE_CHURN_BAND_QUOTE",
    "PAYBACK_BAND_QUOTE",
    "SACKS_SOURCE",
    "SKOK_SOURCE",
    "metrics_check_assumptions",
]

_READ = "read in full 23 Nov 2026, text only"
A16Z_METRICS_SOURCE = f'a16z, "16 Startup Metrics", a16z.com/16-startup-metrics (21 Aug 2015; {_READ})'
A16Z_MORE_METRICS_SOURCE = f'a16z, "16 More Startup Metrics", a16z.com/16-more-startup-metrics (23 Sep 2015; {_READ})'
BESSEMER_SOURCE = (
    'Bessemer Venture Partners, "Scaling to $100 Million", bvp.com/atlas/scaling-to-100-million '
    f"(21 Sep 2021; {_READ}; its data is Bessemer's own cloud portfolio, 2010 to 1H21, not a random sample)"
)
SACKS_SOURCE = (
    f'David Sacks, "The Burn Multiple", sacks.substack.com/p/the-burn-multiple-51a7e43cb200 (23 Apr 2020; {_READ})'
)
SKOK_SOURCE = f'David Skok, "SaaS Metrics 2.0", forentrepreneurs.com/saas-metrics-2 (no date on the page; {_READ})'

_ARR_QUOTE = '"It should exclude one-time fees, professional service fees, and any variable usage fees."'
_RETENTION_QUOTE = (
    'gross retention "nets out the revenue from customers who turned off or downgraded your service, but does not '
    'account for any expansion"; net retention differs "by accounting for the upsells and expansion revenue"'
)
_CHURN_QUOTE = (
    '"Monthly unit churn = lost customers/prior month total"; "Gross churn: MRR lost in a given month/MRR at the '
    'beginning of the month."; "Net churn: (MRR lost minus MRR from upsells) in a given month/MRR at the beginning of '
    'the month."'
)
_CAC_QUOTE = (
    'blended CAC "[total acquisition cost / total new customers acquired across all channels]"; paid CAC "[total '
    'acquisition cost/ new customers acquired through paid marketing]"'
)
_PAYBACK_QUOTE = '"We also measure CAC payback against gross margin-adjusted ARR"'
_BURN_MULTIPLE_QUOTE = (
    '"Burn Multiple = Net Burn / Net New ARR"; for a pre-revenue startup "net new ARR will be zero so the ratio will '
    'not even compute"'
)
# The essay on a company at break-even: the multiple heads to 0. The calculator does not work 0x; see the row.
_ZERO_BURN_QUOTE = '"burn must reach 0, which implies that the Burn Multiple should also approach 0 over time"'
_COHORT_PARTS = (
    ("expansion", "cohort_expansion_recurring"),
    ("contraction", "cohort_contraction_recurring"),
    ("churn", "cohort_churned_recurring"),
)
_CONCENTRATION_QUOTE = (
    '"the revenue of your largest customer or handful of customers relative to total revenue, with both revenues '
    'reflecting the same time period"'
)
PAYBACK_BAND_QUOTE = (
    '"For cloud companies selling into SMB-focused accounts, you should target CAC payback <12 months; for '
    "mid-market-focused accounts, target CAC payback <18 months; and for enterprise-focused accounts, target <24 "
    'months."'
)
BURN_MULTIPLE_BAND_QUOTE = (
    '"If extraordinary investment (3x burn or more) is required to deliver that growth, it’s an indicator that '
    'product-market fit isn’t quite what it appears to be"'
)
NET_REVENUE_CHURN_BAND_QUOTE = (
    '"If your Net Revenue Churn is high (above 2% per month) it is an indicator that there is something wrong in your '
    'business."'
)
_BENCHMARK = "a benchmark, not a rule"
_SEGMENT_NAMES = {"smb": "SMB", "mid_market": "mid-market", "enterprise": "enterprise"}


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _months(count: int) -> str:
    """``count`` months in words: "1 month", "12 months"."""
    return "1 month" if count == 1 else f"{count} months"


def _listed(names: list[str]) -> str:
    """``names`` as words: "churn", "expansion and churn", "expansion, contraction and churn"."""
    return names[0] if len(names) == 1 else f"{', '.join(names[:-1])} and {names[-1]}"


def _revenue_rows(inputs: MetricsCheckInput, used: frozenset[str]) -> list[EquityAssumption]:
    """The period rule always; the ARR rule with any ARR; retention, cohort and churn rules when worked."""
    rows = [
        _assumption(
            "period_rule",
            _months(inputs.period_months),
            "Every flow figure (the recurring revenue movement, customers, spend, burn and revenue) is for this one "
            "period; retention and churn are over the period and never annualised or compounded.",
            f"{UNVERIFIED} (a modelling choice)",
        )
    ]
    if used & {"ending_arr", "month_arr"}:
        # Built from the ARR figures actually worked: the movement's in its unit, the month's always 12 × the month.
        built = []
        if "ending_arr" in used:
            unit = (
                "12 × monthly recurring revenue" if inputs.recurring_unit == "monthly" else "annual recurring revenue"
            )
            built.append(f"ARR = {unit}")
        if "month_arr" in used:
            built.append("ARR from the latest month = 12 × its recurring revenue; run-rate = 12 × its whole revenue")
        rows.append(
            _assumption(
                "arr_rule",
                "; ".join(built),
                "ARR is recurring revenue on an annual basis, without one-time, services or usage fees; the run-rate "
                "annualises the whole month, so it is not ARR. With the movement and the latest month both given, a "
                "stated ARR is checked against the movement's ending ARR.",
                f"{A16Z_MORE_METRICS_SOURCE}, item 2: {_ARR_QUOTE}",
            )
        )
    own = [name for name, field in _COHORT_PARTS if getattr(inputs, field) is not None]
    if "grr" in used:
        totals = [name for name, field in _COHORT_PARTS if getattr(inputs, field) is None]
        if not own:
            cohort = "the period's totals"
            formulas = "GRR = (S - C - X)/S; NRR = (S + E - C - X)/S"
        else:
            cohort = f"the starting customers' own {_listed(own)}"
            if totals:
                cohort += f"; the period's total {_listed(totals)}"
            formulas = "GRR = (S - C' - X')/S; NRR = (S + E' - C' - X')/S (primed: the starting customers' own)"
        rows += [
            _assumption(
                "retention_rule",
                formulas,
                "Gross revenue retention keeps the recurring revenue at the start less contraction and churn, with no "
                "expansion; net revenue retention adds the starting customers' expansion back. New customers are left "
                f"out of both (ours, {UNVERIFIED}).",
                f"{BESSEMER_SOURCE}: {_RETENTION_QUOTE}",
            ),
            _assumption(
                "cohort_rule",
                cohort,
                "Retention and revenue churn use the starting customers' own expansion, contraction and churn when "
                "given (any left out falls back to the period's total); the period's totals include customers won "
                "during the period, exact only when none of them moved.",
                f"{UNVERIFIED} (a modelling choice)",
            ),
        ]
    if used & {"gross_churn", "logo_churn"}:
        # Primed as the retention rule is, so the printed formula gives the printed churn.
        revenue = (
            "gross = (C' + X')/S; net = (C' + X' - E')/S (primed: the starting customers' own)"
            if own
            else "gross = (C + X)/S; net = (C + X - E)/S"
        )
        rows.append(
            _assumption(
                "churn_rule",
                f"logo = customers lost / at the start; {revenue}",
                "Logo churn counts customers, revenue churn recurring revenue; net revenue churn subtracts expansion "
                f"and can be below zero. The source states each per month; over a longer period it is ours, "
                f"{UNVERIFIED}.",
                f"{A16Z_METRICS_SOURCE}, item 11: {_CHURN_QUOTE}",
            )
        )

    return rows


def _efficiency_rows(inputs: MetricsCheckInput, used: frozenset[str]) -> list[EquityAssumption]:
    """The CAC, payback, burn multiple and concentration rules, each only when worked."""
    rows = []
    if "blended_cac" in used or "paid_cac" in used:
        rows.append(
            _assumption(
                "cac_rule",
                "blended = spend / new customers; paid = spend / paid-channel customers",
                "The spend is the founder's sales and marketing figure for the period; it should hold every cost of "
                "acquiring customers.",
                f"{A16Z_METRICS_SOURCE}, item 8: {_CAC_QUOTE}",
            )
        )
    if "revenue_payback" in used:
        margin = inputs.gross_margin_percent
        setting = (
            "spend / new monthly recurring revenue (no gross margin given)"
            if margin is None
            else f"spend / (new monthly recurring revenue × {margin}% gross margin)"
        )
        rows.append(
            _assumption(
                "payback_rule",
                setting,
                "CAC payback is the months the new recurring revenue, after gross margin, takes to repay the period's "
                "sales and marketing spend; the revenue-only payback leaves the margin out. A stated payback is "
                f"checked on gross margin when it is given. The exact formula is ours, {UNVERIFIED}.",
                f"{BESSEMER_SOURCE}: {_PAYBACK_QUOTE}",
            )
        )
    if inputs.net_burn is not None and inputs.starting_recurring is not None:
        rows.append(
            _assumption(
                "burn_multiple_rule",
                "net burn / net new ARR, the same period",
                "No multiple is worked when net new ARR or the net burn is zero or less, and a stated multiple is "
                "then not checked. The source gives no ratio for a pre-revenue company's zero net new ARR, and says "
                "the multiple approaches 0 as burn reaches 0; working none at zero burn, and none for a negative "
                f"burn or net new ARR, is ours, {UNVERIFIED}.",
                f"{SACKS_SOURCE}: {_BURN_MULTIPLE_QUOTE}; {_ZERO_BURN_QUOTE}",
            )
        )
    if "concentration" in used:
        rows.append(
            _assumption(
                "concentration_rule",
                "largest customer's revenue / the period's revenue",
                "Both revenues are for the same period; no benchmark is set.",
                f"{A16Z_MORE_METRICS_SOURCE}, item 14: {_CONCENTRATION_QUOTE}",
            )
        )

    return rows


def _band_rows(inputs: MetricsCheckInput, used: frozenset[str], checked: bool) -> list[EquityAssumption]:
    """The tolerance (when anything was checked) and each benchmark band its metric was worked for."""
    rows = []
    if checked:
        rows.append(
            _assumption(
                "tolerance",
                f"{inputs.tolerance_points:f} points; {inputs.tolerance_percent:f}% relative",
                "A stated percent within this many percentage points of the computed one, or a stated money, months "
                "or multiple figure within this share of it, is consistent. So is a stated percent, months or multiple "
                "that is the computed figure rounded half away from zero to the places it is written with, whatever "
                "the tolerance: people write figures rounded to the places they show, so a whole number holds what "
                "rounds to it and a figure typed with one place (a zero written with one included) holds what rounds "
                "to it at one place. Money is held to the share alone, since a round money figure typed in full "
                "carries no places. A flag names a figure consistent by the tolerance alone, not a rounding of the "
                "computed one.",
                f"{UNVERIFIED} (the rounding test is standard arithmetic)",
            )
        )
    band = payback_band(inputs)
    if band is not None and used & {"payback", "revenue_payback"}:
        rows.append(_payback_band_row(inputs, band, margin_given="payback" in used))
    if "burn_multiple" in used:
        default = inputs.burn_multiple_band == DEFAULT_BURN_MULTIPLE_BAND
        rows.append(
            _assumption(
                "burn_multiple_band",
                f"{inputs.burn_multiple_band:f}x",
                "A burn multiple at or above this is flagged as something a VC is likely to ask about; it is a "
                "question, never an error, and the band is an input"
                + ("." if default else " (the founder's own band here)."),
                f"{SACKS_SOURCE}: {BURN_MULTIPLE_BAND_QUOTE} ({_BENCHMARK})",
            )
        )
    if inputs.period_months == 1 and "net_churn" in used:
        default = inputs.net_revenue_churn_band_percent == DEFAULT_NET_REVENUE_CHURN_BAND_PERCENT
        rows.append(
            _assumption(
                "net_revenue_churn_band",
                f"{inputs.net_revenue_churn_band_percent:f}% a month",
                "One month's net revenue churn above this is flagged as a question, never an error; it is checked "
                "only on a one-month period, since the calculator compounds nothing, and the band is an input"
                + ("." if default else " (the founder's own band here)."),
                f"{SKOK_SOURCE}: {NET_REVENUE_CHURN_BAND_QUOTE} ({_BENCHMARK})",
            )
        )

    return rows


def _payback_band_row(inputs: MetricsCheckInput, band: Decimal, *, margin_given: bool) -> EquityAssumption:
    """The payback benchmark: the founder's band, or their segment's target, and which one won; with no gross margin,
    how far it could be applied."""
    segment = inputs.customer_segment
    statement = (
        "A CAC payback on gross margin at or above this many months is flagged as a question, never an error: the "
        "target is to stay under it."
    )
    if not margin_given:
        statement += (
            " No gross margin was given, so only the revenue-only payback, a floor under the payback on gross margin, "
            "is set against it: at or above the band it is flagged; below it the benchmark is not applied."
        )
    if inputs.payback_band_months is None and segment is not None:
        return _assumption(
            "payback_band",
            f"{band:f} months ({_SEGMENT_NAMES[segment]})",
            f"{statement} The band is the target for the customer segment given, an input.",
            f"{BESSEMER_SOURCE}: {PAYBACK_BAND_QUOTE} ({_BENCHMARK})",
        )

    over = "" if segment is None else f" It is used over the {_SEGMENT_NAMES[segment]} target."
    return _assumption(
        "payback_band",
        f"{band:f} months (given)",
        f"{statement} The band is the founder's own.{over}",
        f"given; the segment targets are {BESSEMER_SOURCE}: {PAYBACK_BAND_QUOTE} ({_BENCHMARK})",
    )


def metrics_check_assumptions(
    inputs: MetricsCheckInput, checked: bool, used: frozenset[str]
) -> tuple[EquityAssumption, ...]:
    """The metrics check's rows, each only when the input uses it; ``used`` names the metrics that were worked."""
    return (*_revenue_rows(inputs, used), *_efficiency_rows(inputs, used), *_band_rows(inputs, used, checked))
