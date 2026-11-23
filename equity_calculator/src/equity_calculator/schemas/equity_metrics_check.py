"""Pydantic models of a founder's traction metrics checked against their parts (``equity_calculator metrics_check``).

A deck, a model or an investor update states some of: ARR, net and gross revenue retention, a churn figure, CAC, CAC
payback, a burn multiple and customer concentration. The check takes the parts those figures are made of, all for one
period the founder names (``period_months``): the recurring revenue at the start and its movement over the period
(new, expansion, contraction, churned), the latest month's revenue and how much of it is one-time or usage, the
customers at the start, lost and won, the sales and marketing spend, the gross margin, the net burn, and the largest
customer's revenue with the period's revenue. It works each metric exactly and returns each stated figure as
``consistent``, a ``mismatch``, or ``not_checked`` (a stated burn multiple when no multiple can be worked), with
flags that name the likely cause of a mismatch (a run-rate called ARR, new customers counted in net retention, a
payback on revenue rather than gross margin, a burn multiple on new rather than net new ARR) and three benchmark
questions, never errors.

No valuation, instrument, runway or burn projection: those stay with ``deal_check``, ``round`` and ``runway_plan``.
This module reuses ``equity_deal_check``'s verdict words and default tolerances, so no cycle.
``equity_calculator.metrics_check`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    SIZE_LIMIT,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    WrittenDecimal,
)
from equity_calculator.schemas.equity_deal_check import DEFAULT_TOLERANCE_PERCENT, DEFAULT_TOLERANCE_POINTS, DealVerdict
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "DEFAULT_BURN_MULTIPLE_BAND",
    "DEFAULT_NET_REVENUE_CHURN_BAND_PERCENT",
    "MAX_PERIOD_MONTHS",
    "SEGMENT_PAYBACK_MONTHS",
    "ArrBasis",
    "ChurnBasis",
    "CustomerCount",
    "CustomerSegment",
    "MetricsCheck",
    "MetricsCheckInput",
    "MetricsCheckKey",
    "MetricsCheckResult",
    "MetricsCheckScenario",
    "MetricsFlag",
    "RecurringUnit",
    "StatedChurnBasis",
    "payback_band",
]

MetricsCheckScenario = Literal["metrics_check"]

# The unit the recurring-revenue figures are stated in: a month's recurring revenue (MRR) or a year's (ARR). The tool
# annualises a monthly figure by 12; the model never converts one.
RecurringUnit = Literal["monthly", "annual"]

# A churn figure's basis: customers lost (``logo``), recurring revenue lost (``gross_revenue``), or revenue lost less
# expansion (``net_revenue``). A stated churn may also be ``unlabelled``: it is then checked against every basis the
# inputs can compute.
ChurnBasis = Literal["logo", "gross_revenue", "net_revenue"]
StatedChurnBasis = Literal["logo", "gross_revenue", "net_revenue", "unlabelled"]

# Who the company sells to; it sets the CAC payback benchmark when no band is given.
CustomerSegment = Literal["smb", "mid_market", "enterprise"]

# Which stated figure a check is about.
MetricsCheckKey = Literal["arr", "nrr", "grr", "churn", "cac", "cac_payback", "burn_multiple", "concentration"]

# Which ARR a stated ARR is checked against: the movement's ending ARR or the latest month's, whichever the stated ARR
# is within the tolerance of (the movement's when both are worked and it is within both or neither).
ArrBasis = Literal["movement", "month"]

# Facts and questions a VC is likely to raise. They never change a verdict; their plain words are in
# ``equity_calculator.layout_metrics_check``. The four ``stated_*`` flags are set only beside a mismatch (the burn
# multiple's also beside a figure left unchecked), when the stated figure is within the tolerance of the named wrong
# definition instead, so each names the likely cause.
# ``consistent_beyond_rounding`` names a stated percent, months or multiple consistent by the tolerance alone, not as
# the computed figure rounded to the places the document writes it with.
MetricsFlag = Literal[
    "stated_arr_matches_run_rate",
    "arr_movement_and_month_disagree",
    "run_rate_includes_non_recurring",
    "stated_nrr_includes_new",
    "expansion_hides_churn",
    "churn_basis_unlabelled",
    "blended_cac_only",
    "payback_not_margin_adjusted",
    "stated_payback_not_margin_adjusted",
    "stated_burn_multiple_uses_new_not_net_arr",
    "consistent_beyond_rounding",
    "burn_multiple_not_defined",
    "no_net_burn",
    "payback_above_band",
    "burn_multiple_above_band",
    "net_revenue_churn_above_band",
]

# The longest period one call covers; every flow figure is for this one period.
MAX_PERIOD_MONTHS = 36

# The benchmark defaults: the CAC payback target per segment (Bessemer), the burn multiple at or above which the
# multiple is flagged (Sacks) and the monthly net revenue churn above which it is flagged (Skok). Each is a question,
# never an error, and the founder can change it; the sources are quoted in ``assumptions_metrics_check``.
SEGMENT_PAYBACK_MONTHS: dict[CustomerSegment, Decimal] = {
    "smb": Decimal(12),
    "mid_market": Decimal(18),
    "enterprise": Decimal(24),
}
DEFAULT_BURN_MULTIPLE_BAND = Decimal(3)
DEFAULT_NET_REVENUE_CHURN_BAND_PERCENT = Decimal(2)

# strict: a customer count is a real int; a bool, a float or a numeric string is refused, never read as one.
CustomerCount = Annotated[int, Field(strict=True, ge=0, lt=SIZE_LIMIT)]

_MOVEMENTS = ("new_recurring", "expansion_recurring", "contraction_recurring", "churned_recurring")
_COHORT = (
    ("cohort_expansion_recurring", "expansion_recurring"),
    ("cohort_contraction_recurring", "contraction_recurring"),
    ("cohort_churned_recurring", "churned_recurring"),
)
# The two movements that lose the starting customers' revenue, as (cohort part, total) pairs.
_COHORT_LOSSES = _COHORT[1:]

# The description each stated percent, months or multiple field carries in the JSON schema (the MCP tool's input): its
# places decide the rounding test, and a JSON number can drop them (12.40 arrives as 12.4) or add one (12.0).
_AS_WRITTEN = (
    "Send it as text with exactly the places the document writes ({examples}): a figure that is the computed one "
    "rounded to those places is consistent, and a JSON number can drop or add a place."
)
_PERCENT_AS_WRITTEN = "Percent points. " + _AS_WRITTEN.format(examples='"2", "2.0", "0.0"')
_MONTHS_AS_WRITTEN = _AS_WRITTEN.format(examples='"12", "12.0"')
_MULTIPLE_AS_WRITTEN = _AS_WRITTEN.format(examples='"1.5", "1.50"')


class MetricsCheckInput(BaseModel):
    """A founder's metrics as a document states them, plus the parts they are made of; see the module docstring.

    Every flow figure is for the same ``period_months``. Recurring revenue (``starting_recurring`` and its four
    movements, the period's totals) is in ``recurring_unit``. The ``cohort_*`` fields are the same three movements for
    the customers there at the start only; retention and revenue churn use them when given. Percent fields take
    percent points (``95`` is 95%). The tolerances say how far a stated figure may sit from the computed one
    (``deal_check``'s defaults); a stated percent, months or multiple that is the computed figure rounded to the places
    it is typed with holds even past them. The three bands raise a benchmark question, never an error.
    """

    model_config = MODEL_CONFIG

    scenario: MetricsCheckScenario = "metrics_check"
    period_months: int = Field(strict=True, ge=1, le=MAX_PERIOD_MONTHS)
    recurring_unit: RecurringUnit = "monthly"
    starting_recurring: BoundedDecimal | None = Field(default=None, ge=0)
    new_recurring: BoundedDecimal = Field(default=Decimal(0), ge=0)
    expansion_recurring: BoundedDecimal = Field(default=Decimal(0), ge=0)
    contraction_recurring: BoundedDecimal = Field(default=Decimal(0), ge=0)
    churned_recurring: BoundedDecimal = Field(default=Decimal(0), ge=0)
    cohort_expansion_recurring: BoundedDecimal | None = Field(default=None, ge=0)
    cohort_contraction_recurring: BoundedDecimal | None = Field(default=None, ge=0)
    cohort_churned_recurring: BoundedDecimal | None = Field(default=None, ge=0)
    month_total_revenue: BoundedDecimal | None = Field(default=None, ge=0)
    month_one_time_revenue: BoundedDecimal = Field(default=Decimal(0), ge=0)
    month_usage_revenue: BoundedDecimal = Field(default=Decimal(0), ge=0)
    customers_start: CustomerCount | None = None
    customers_lost: CustomerCount | None = None
    customers_new: CustomerCount | None = None
    customers_new_paid: CustomerCount | None = None
    sales_marketing_spend: BoundedDecimal | None = Field(default=None, gt=0)
    gross_margin_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)
    net_burn: BoundedDecimal | None = None
    largest_customer_revenue: BoundedDecimal | None = Field(default=None, ge=0)
    period_revenue: BoundedDecimal | None = Field(default=None, gt=0)
    stated_arr: BoundedDecimal | None = Field(default=None, gt=0)
    # The stated percent, months and multiple fields are ``WrittenDecimal``: a zero keeps the places it is written with
    # ("0.0" is one place), which the rounding test reads (a figure that is the computed one rounded to its places is
    # consistent).
    stated_nrr_percent: WrittenDecimal | None = Field(default=None, ge=0, description=_PERCENT_AS_WRITTEN)
    # Above 100% is accepted, never refused: gross retention leaves expansion out, so it is checked like any figure,
    # and comes back a mismatch unless it is within the tolerance of the computed figure or its rounding.
    stated_grr_percent: WrittenDecimal | None = Field(default=None, ge=0, description=_PERCENT_AS_WRITTEN)
    # Below 0 only as net revenue churn (expansion above the revenue lost); ``_churn_rules`` refuses it otherwise.
    stated_churn_percent: WrittenDecimal | None = Field(default=None, le=WHOLE_PERCENT, description=_PERCENT_AS_WRITTEN)
    stated_churn_basis: StatedChurnBasis = "unlabelled"
    stated_cac: BoundedDecimal | None = Field(default=None, gt=0)
    stated_cac_payback_months: WrittenDecimal | None = Field(default=None, gt=0, description=_MONTHS_AS_WRITTEN)
    # 0x is accepted (a company at break-even, which the source says the multiple approaches); with no multiple to
    # work it is not checked.
    stated_burn_multiple: WrittenDecimal | None = Field(default=None, ge=0, description=_MULTIPLE_AS_WRITTEN)
    stated_concentration_percent: WrittenDecimal | None = Field(
        default=None, ge=0, le=WHOLE_PERCENT, description=_PERCENT_AS_WRITTEN
    )
    tolerance_points: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_POINTS, ge=0, lt=WHOLE_PERCENT)
    tolerance_percent: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_PERCENT, ge=0, lt=WHOLE_PERCENT)
    customer_segment: CustomerSegment | None = None
    payback_band_months: BoundedDecimal | None = Field(default=None, gt=0)
    burn_multiple_band: BoundedDecimal = Field(default=DEFAULT_BURN_MULTIPLE_BAND, gt=0)
    net_revenue_churn_band_percent: BoundedDecimal = Field(
        default=DEFAULT_NET_REVENUE_CHURN_BAND_PERCENT, gt=0, lt=WHOLE_PERCENT
    )

    @model_validator(mode="after")
    def _metrics_can_be_checked(self) -> MetricsCheckInput:
        """Refuse parts that cannot hold together, a part without what it belongs to, and a stated figure with
        nothing to check it against."""
        self._movement_rules()
        self._part_rules()
        self._stated_rules()
        return self

    def has_movement(self) -> bool:
        """Whether the recurring revenue movement was given (``starting_recurring`` set)."""
        return self.starting_recurring is not None

    def has_logo_churn(self) -> bool:
        """Whether logo churn can be worked: customers at the start above 0 and the customers lost."""
        return self.customers_start is not None and self.customers_start > 0 and self.customers_lost is not None

    def has_revenue_churn(self) -> bool:
        """Whether retention and revenue churn can be worked: recurring revenue at the start above 0."""
        return self.starting_recurring is not None and self.starting_recurring > 0

    def _movement_rules(self) -> None:
        """Refuse a movement without its start, more lost than there was, or a cohort part above its total.

        The four movements are the period's totals, so they include customers won during the period: their losses
        are bounded by everything there was (start, new and expansion), never by the start alone. The starting
        customers' own losses (each ``cohort_*`` part, or its total when not given) are bounded by the start, so
        retention never goes below 0. With nothing at the start, retention is not worked, and only a given
        ``cohort_*`` loss is held to it.
        """
        if self.starting_recurring is None:
            moving = [name for name in _MOVEMENTS if getattr(self, name) > 0]
            moving += [cohort for cohort, _ in _COHORT if getattr(self, cohort) is not None]
            if moving:
                raise ValueError(
                    f"{moving[0]} needs starting_recurring (the recurring revenue at the start of the period; give 0 "
                    "when there was none)"
                )
            return

        start = Fraction(self.starting_recurring)
        lost = Fraction(self.contraction_recurring) + Fraction(self.churned_recurring)
        if lost > start + Fraction(self.new_recurring) + Fraction(self.expansion_recurring):
            raise ValueError(
                "contraction_recurring + churned_recurring is above starting_recurring + new_recurring + "
                "expansion_recurring: a period cannot lose more recurring revenue than it had (ARR at the end would "
                "be below 0)"
            )
        for cohort, total in _COHORT:
            part = getattr(self, cohort)
            if part is not None and part > getattr(self, total):
                raise ValueError(
                    f"{cohort} is above {total}: the starting customers' part of a movement cannot exceed the total"
                )
        if self._cohort_lost() > start:
            raise ValueError(
                "cohort_contraction_recurring + cohort_churned_recurring (each the period's total when not given) is "
                "above starting_recurring: the starting customers cannot lose more recurring revenue than they had at "
                "the start; give their own contraction and churn"
            )

    def _cohort_lost(self) -> Fraction:
        """The starting customers' contraction plus churn: each ``cohort_*`` part when given, else its total when
        there was recurring revenue at the start (retention is then worked on it), else 0."""
        lost = Fraction(0)
        for cohort, total in _COHORT_LOSSES:
            part = getattr(self, cohort)
            if part is not None:
                lost += Fraction(part)
            elif self.has_revenue_churn():
                lost += Fraction(getattr(self, total))
        return lost

    def _part_rules(self) -> None:
        """Refuse the month's parts above its total, customers that do not add up, and concentration above 100%."""
        if self.month_total_revenue is None:
            for name in ("month_one_time_revenue", "month_usage_revenue"):
                if getattr(self, name) > 0:
                    raise ValueError(f"{name} needs month_total_revenue")
        elif Fraction(self.month_one_time_revenue) + Fraction(self.month_usage_revenue) > Fraction(
            self.month_total_revenue
        ):
            raise ValueError("month_one_time_revenue + month_usage_revenue is above month_total_revenue")
        if self.customers_lost is not None:
            if self.customers_start is None:
                raise ValueError("customers_lost needs customers_start")
            if self.customers_lost > self.customers_start:
                raise ValueError(
                    "customers_lost is above customers_start: give only the customers lost among those there at the "
                    "start of the period; customers won and lost inside the period are left out of logo churn"
                )
        if self.customers_new_paid is not None:
            if self.customers_new is None:
                raise ValueError("customers_new_paid needs customers_new (every new customer, paid channels included)")
            if self.customers_new_paid > self.customers_new:
                raise ValueError("customers_new_paid is above customers_new")
        if self.largest_customer_revenue is not None:
            if self.period_revenue is None:
                raise ValueError("largest_customer_revenue needs period_revenue (the same period's total revenue)")
            if self.largest_customer_revenue > self.period_revenue:
                raise ValueError("largest_customer_revenue is above period_revenue")

    def _stated_rules(self) -> None:
        """Refuse a stated figure without the parts that check it, naming what it needs."""
        needs: list[tuple[str, object, bool, str]] = [
            (
                "stated_arr",
                self.stated_arr,
                self.has_movement() or self.month_total_revenue is not None,
                "starting_recurring or month_total_revenue",
            ),
            ("stated_nrr_percent", self.stated_nrr_percent, self.has_revenue_churn(), "starting_recurring above 0"),
            ("stated_grr_percent", self.stated_grr_percent, self.has_revenue_churn(), "starting_recurring above 0"),
            (
                "stated_cac",
                self.stated_cac,
                self.sales_marketing_spend is not None and bool(self.customers_new),
                "sales_marketing_spend and customers_new above 0",
            ),
            (
                "stated_cac_payback_months",
                self.stated_cac_payback_months,
                self.sales_marketing_spend is not None and self.new_recurring > 0,
                "sales_marketing_spend and new_recurring above 0",
            ),
            (
                "stated_burn_multiple",
                self.stated_burn_multiple,
                self.net_burn is not None and self.has_movement(),
                "net_burn and starting_recurring",
            ),
            (
                "stated_concentration_percent",
                self.stated_concentration_percent,
                self.largest_customer_revenue is not None,
                "largest_customer_revenue and period_revenue",
            ),
        ]
        for name, stated, ready, what in needs:
            if stated is not None and not ready:
                raise ValueError(f"{name} needs {what} to check it")
        self._churn_rules()

    def _churn_rules(self) -> None:
        """Refuse a basis with no stated churn, and a stated churn whose basis the inputs cannot compute."""
        basis = self.stated_churn_basis
        if self.stated_churn_percent is None:
            if basis != "unlabelled":
                raise ValueError("stated_churn_basis needs stated_churn_percent")
            return

        if self.stated_churn_percent < 0 and not (basis in ("net_revenue", "unlabelled") and self.has_revenue_churn()):
            raise ValueError(
                "stated_churn_percent is below 0, which only net revenue churn can be (expansion above the revenue "
                "lost): give stated_churn_basis net_revenue (or none) with starting_recurring above 0"
            )
        if basis == "logo" and not self.has_logo_churn():
            raise ValueError("stated_churn_percent on a logo basis needs customers_start above 0 and customers_lost")
        if basis in ("gross_revenue", "net_revenue") and not self.has_revenue_churn():
            raise ValueError(f"stated_churn_percent on a {basis} basis needs starting_recurring above 0")
        if basis == "unlabelled" and not (self.has_logo_churn() or self.has_revenue_churn()):
            raise ValueError(
                "stated_churn_percent needs customers_start above 0 with customers_lost, or starting_recurring above "
                "0, to check it"
            )


def payback_band(inputs: MetricsCheckInput) -> Decimal | None:
    """The CAC payback benchmark in force: ``payback_band_months``, else the segment's, else none."""
    if inputs.payback_band_months is not None:
        return inputs.payback_band_months
    if inputs.customer_segment is not None:
        return SEGMENT_PAYBACK_MONTHS[inputs.customer_segment]

    return None


class MetricsCheck(BaseModel):
    """One stated figure checked: what the document says, what the calculator gives, computed - stated, the verdict.

    ``basis`` names the churn basis a churn row is checked on (an unlabelled churn gets one row per basis).
    ``computed`` and ``difference`` are none, and the verdict ``not_checked``, when the parts give no figure to check
    against (a stated burn multiple with net burn or net new ARR at or below zero). ``within_rounding`` says whether
    the stated percent, months or multiple is the computed figure rounded half away from zero to the places it is
    written with, which makes it consistent even past the tolerance; none for money and for a figure not checked.
    """

    model_config = MODEL_CONFIG

    key: MetricsCheckKey
    basis: ChurnBasis | None = None
    stated: EquityQuantity
    computed: EquityQuantity | None = None
    difference: EquityQuantity | None = None
    verdict: DealVerdict
    within_rounding: bool | None = None


class MetricsCheckResult(BaseModel):
    """The metrics worked from their parts, each stated figure's verdict, the flags and the overall verdict.

    Money is ARR or dollars; retention, churn and concentration are fractions over ``period_months`` (never
    annualised); paybacks are months; multiples are ratios. A value is none when its parts were not given.
    ``arr_basis`` says which ARR a stated ARR is checked against: of the movement's ending ARR and the latest month's,
    the one it is within the tolerance of (the movement's when it is within both or neither, or with no stated ARR).
    ``payback_band_months`` is the benchmark in force.
    """

    model_config = MODEL_CONFIG

    scenario: MetricsCheckScenario = "metrics_check"
    inputs: MetricsCheckInput
    starting_arr: EquityQuantity | None = None
    ending_arr: EquityQuantity | None = None
    net_new_arr: EquityQuantity | None = None
    new_arr: EquityQuantity | None = None
    month_arr: EquityQuantity | None = None
    run_rate: EquityQuantity | None = None
    arr_basis: ArrBasis | None = None
    gross_revenue_retention: EquityQuantity | None = None
    net_revenue_retention: EquityQuantity | None = None
    gross_revenue_churn: EquityQuantity | None = None
    net_revenue_churn: EquityQuantity | None = None
    logo_churn: EquityQuantity | None = None
    logo_retention: EquityQuantity | None = None
    blended_cac: EquityQuantity | None = None
    paid_cac: EquityQuantity | None = None
    cac_payback_months: EquityQuantity | None = None
    revenue_payback_months: EquityQuantity | None = None
    burn_multiple: EquityQuantity | None = None
    burn_multiple_on_new_arr: EquityQuantity | None = None
    concentration: EquityQuantity | None = None
    payback_band_months: EquityQuantity | None = None
    checks: tuple[MetricsCheck, ...]
    flags: tuple[MetricsFlag, ...]
    verdict: DealVerdict
    assumptions: tuple[EquityAssumption, ...]
