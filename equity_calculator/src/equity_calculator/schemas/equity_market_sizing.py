"""Pydantic models of a founder's market size built bottom-up (``equity_calculator market_sizing``).

The founder gives who buys, as one to eight segments: how many buying customers each has, what one of them pays (a
price for a number of months, per unit such as a seat or a location, and the share of the spend the company keeps),
the share of them the product can serve and reach today, and the customers the founder plans to win (a count, or a
share of the serviceable ones) with the customers today. The calculator works TAM, SAM and SOM per segment and in
total, checks the deck's stated TAM, SAM and SOM, compares the bottom-up figure with any top-down figure the founder
has (a cross-check, never a verdict), and works the totals again on the founder's own low and high values for one
field of one segment at a time, with the value at which SOM reaches the founder's target.

No market figure, price, share or count is ever supplied by the tool: every input is the founder's. No free text:
segments are numbered in the order given. No money raised, valuation or ownership: those stay with ``deal_check``,
``round`` and ``runway_plan``. This module reuses ``equity_deal_check``'s verdict words and default relative
tolerance, so no cycle. ``equity_calculator.market_sizing`` works it; the arithmetic and each convention's source are
in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
)
from equity_calculator.schemas.equity_deal_check import DEFAULT_TOLERANCE_PERCENT, CheckVerdict, DealVerdict
from pydantic import BaseModel, Field, ValidationError, model_validator
from pydantic_core import ErrorDetails

__all__ = [
    "MAX_PRICE_PERIOD_MONTHS",
    "MAX_SEGMENTS",
    "MAX_SENSITIVITIES",
    "MAX_SENSITIVITY_VALUES",
    "MAX_SOM_YEARS",
    "MAX_TOP_DOWN",
    "PERCENT_FIELDS",
    "BreakEvenReach",
    "BreakEvenRow",
    "CompareTo",
    "MarketCheck",
    "MarketMetric",
    "MarketSegment",
    "MarketSizingFlag",
    "MarketSizingInput",
    "MarketSizingResult",
    "MarketSizingScenario",
    "MarketTotals",
    "SegmentField",
    "SegmentRow",
    "SensitivityCase",
    "SensitivityResult",
    "SensitivityRow",
    "TopDownFigure",
    "TopDownRow",
]

MarketSizingScenario = Literal["market_sizing"]

# The fields of a segment a sensitivity row may change, one at a time.
SegmentField = Literal[
    "customers",
    "price",
    "units_per_customer",
    "take_rate_percent",
    "serviceable_percent",
    "obtainable_percent",
    "obtainable_customers",
]
PERCENT_FIELDS: frozenset[SegmentField] = frozenset({"take_rate_percent", "serviceable_percent", "obtainable_percent"})

# The three totals a stated figure, a top-down comparison or a break-even value is about.
MarketMetric = Literal["tam", "sam", "som"]
# What a top-down figure is compared with: the bottom-up TAM or SAM.
CompareTo = Literal["tam", "sam"]

# How a break-even value came out: ``value`` (the field at that value reaches the target exactly), ``met_without_it``
# (the target is reached with the field at its base: the other segments alone reach it, or, for the plan's SOM target,
# the base SOM is already at or above it), ``does_not_move`` (the field is not a factor of that total) or
# ``out_of_range`` (the value is returned, but the segment would be refused with it: a percent above 100, say, or a
# number outside the size every decimal input has). ``does_not_move`` is tested first: a field that is no factor of
# the total is reported so even when the target is already met.
BreakEvenReach = Literal["value", "met_without_it", "does_not_move", "out_of_range"]

# Facts and questions a VC is likely to raise. They never change a verdict; their plain words are in
# ``equity_calculator.layout_market_sizing``.
MarketSizingFlag = Literal[
    "price_period_defaulted",
    "segments_exceed_population",
    "bottom_up_above_top_down",
    "sam_equals_tam",
    "som_not_given",
    "som_as_percent_only",
    "som_from_zero_customers",
    "som_below_customers_today",
    "no_horizon_given",
    "som_below_target",
    "som_target_out_of_reach",
]

# The list caps (design open question 6's defaults) and the longest price period and SOM horizon.
MAX_SEGMENTS = 8
MAX_TOP_DOWN = 3
MAX_SENSITIVITIES = 6
MAX_SENSITIVITY_VALUES = 4
MAX_PRICE_PERIOD_MONTHS = 120
MAX_SOM_YEARS = 20

_MONTHS_PER_YEAR = 12
_HUNDRED = Fraction(WHOLE_PERCENT)
_OBTAINABLE = ("obtainable_percent", "obtainable_customers")


class MarketSegment(BaseModel):
    """One group of buying customers, every figure the founder's own.

    ``price`` is what one unit costs for ``price_period_months`` (1 for a monthly price, 12 for a yearly one, 24 for a
    device that lasts two years); ``units_per_customer`` the seats or locations one customer buys;
    ``take_rate_percent`` the share of the spend the company keeps (100 unless it is a marketplace or a payments
    business); ``serviceable_percent`` the share of the customers the product can serve and reach today. SOM is
    ``obtainable_customers`` (preferred) or ``obtainable_percent`` of the serviceable customers, never both.
    ``price_period_months`` left out (or null) reads the price as a yearly one (12) and is flagged
    ``price_period_defaulted``: send 1 for a monthly price. "Not given" is the value none, never an absent key, so a
    result's echoed ``inputs`` fed back keep the flag (``period_months`` is the months the arithmetic uses).
    """

    model_config = MODEL_CONFIG

    customers: BoundedDecimal = Field(gt=0)
    price: BoundedDecimal = Field(gt=0)
    price_period_months: int | None = Field(default=None, strict=True, ge=1, le=MAX_PRICE_PERIOD_MONTHS)
    units_per_customer: BoundedDecimal = Field(default=Decimal(1), gt=0)
    take_rate_percent: BoundedDecimal = Field(default=Decimal(WHOLE_PERCENT), gt=0, le=WHOLE_PERCENT)
    serviceable_percent: BoundedDecimal = Field(default=Decimal(WHOLE_PERCENT), gt=0, le=WHOLE_PERCENT)
    obtainable_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)
    obtainable_customers: BoundedDecimal | None = Field(default=None, gt=0)
    customers_today: BoundedDecimal | None = Field(default=None, ge=0)

    @model_validator(mode="after")
    def _segment_holds_together(self) -> MarketSegment:
        """Refuse both SOM fields, more customers today than in the segment, and a SOM count above the serviceable
        customers."""
        if self.obtainable_percent is not None and self.obtainable_customers is not None:
            raise ValueError("give obtainable_percent or obtainable_customers, not both")
        if self.customers_today is not None and self.customers_today > self.customers:
            raise ValueError("customers_today is above customers")
        if self.obtainable_customers is not None and Fraction(self.obtainable_customers) > self.serviceable_count():
            raise ValueError(
                "obtainable_customers is above the serviceable customers (customers × serviceable_percent / 100)"
            )
        return self

    def period_months(self) -> int:
        """The months the price covers: ``price_period_months``, or 12 (a yearly price) when it was not given."""
        return _MONTHS_PER_YEAR if self.price_period_months is None else self.price_period_months

    def period_given(self) -> bool:
        """Whether the founder gave the months the price covers (not given, the price is read as a yearly one)."""
        return self.price_period_months is not None

    def serviceable_count(self) -> Fraction:
        """The customers the product can serve today: customers × serviceable_percent / 100, exactly."""
        return Fraction(self.customers) * Fraction(self.serviceable_percent) / _HUNDRED

    def has_som(self) -> bool:
        """Whether the segment gives a SOM (either obtainable field)."""
        return self.obtainable_percent is not None or self.obtainable_customers is not None


class TopDownFigure(BaseModel):
    """A top-down market figure the founder has: the annual amount as its publisher states it, the share of it that
    matches the founder's own definition, and whether it is compared with the bottom-up TAM or SAM."""

    model_config = MODEL_CONFIG

    amount: BoundedDecimal = Field(gt=0)
    comparable_percent: BoundedDecimal = Field(default=Decimal(WHOLE_PERCENT), gt=0, le=WHOLE_PERCENT)
    compare_to: CompareTo = "tam"


class SensitivityRow(BaseModel):
    """One field of one segment (1 is the first) worked again at each of the founder's own values."""

    model_config = MODEL_CONFIG

    field: SegmentField
    segment: int = Field(strict=True, ge=1, le=MAX_SEGMENTS)
    values: tuple[BoundedDecimal, ...] = Field(min_length=1, max_length=MAX_SENSITIVITY_VALUES)


class MarketSizingInput(BaseModel):
    """A founder's market, bottom-up, as segments; see the module docstring.

    ``population`` is the total the segments are drawn from, in the same buying unit; ``annual_revenue_today`` the
    company's revenue today, to set the SOM against; ``som_years`` the horizon by which the SOM customers are won;
    ``som_target`` the annual revenue the founder's own plan needs from this market by then. ``stated_tam``,
    ``stated_sam`` and ``stated_som`` are the deck's figures, each checked within ``tolerance_percent`` of the
    computed one (``deal_check``'s default).
    """

    model_config = MODEL_CONFIG

    scenario: MarketSizingScenario = "market_sizing"
    segments: tuple[MarketSegment, ...] = Field(min_length=1, max_length=MAX_SEGMENTS)
    top_down: tuple[TopDownFigure, ...] = Field(default=(), max_length=MAX_TOP_DOWN)
    sensitivity: tuple[SensitivityRow, ...] = Field(default=(), max_length=MAX_SENSITIVITIES)
    population: BoundedDecimal | None = Field(default=None, gt=0)
    annual_revenue_today: BoundedDecimal | None = Field(default=None, gt=0)
    som_years: int | None = Field(default=None, strict=True, ge=1, le=MAX_SOM_YEARS)
    som_target: BoundedDecimal | None = Field(default=None, gt=0)
    stated_tam: BoundedDecimal | None = Field(default=None, gt=0)
    stated_sam: BoundedDecimal | None = Field(default=None, gt=0)
    stated_som: BoundedDecimal | None = Field(default=None, gt=0)
    tolerance_percent: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_PERCENT, ge=0, lt=WHOLE_PERCENT)

    @model_validator(mode="after")
    def _market_can_be_worked(self) -> MarketSizingInput:
        """Refuse a SOM figure with no SOM to compare it with, and sensitivity rows that name no real value."""
        if not all(segment.has_som() for segment in self.segments):
            for name in ("stated_som", "som_target"):
                if getattr(self, name) is not None:
                    raise ValueError(
                        f"{name} needs obtainable_percent or obtainable_customers in every segment (the SOM is "
                        "totalled only when every segment gives one)"
                    )
        seen: set[tuple[str, int]] = set()
        for number, row in enumerate(self.sensitivity, start=1):
            self._sensitivity_rules(number, row, seen)
        return self

    def _sensitivity_rules(self, number: int, row: SensitivityRow, seen: set[tuple[str, int]]) -> None:
        """Refuse a row past the last segment, on a SOM field the segment leaves out, given twice, or with a value
        that would make its segment invalid (the segment is checked again with each value in place)."""
        place = f"sensitivity #{number}"
        if row.segment > len(self.segments):
            raise ValueError(f"{place} names segment {row.segment}, past the last one given ({len(self.segments)})")
        segment = self.segments[row.segment - 1]
        if row.field in _OBTAINABLE and getattr(segment, row.field) is None:
            raise ValueError(f"{place}: segment {row.segment} gives no {row.field} to change")
        if (row.field, row.segment) in seen:
            raise ValueError(f"{place}: {row.field} of segment {row.segment} is already a row")
        seen.add((row.field, row.segment))
        for index, value in enumerate(row.values, start=1):
            try:
                MarketSegment.model_validate({**segment.model_dump(), row.field: value})
            except ValidationError as error:
                reasons = "; ".join(_reason(failure) for failure in error.errors(include_url=False))
                raise ValueError(f"{place} value #{index} ({value}): {reasons}") from None


def _reason(failure: ErrorDetails) -> str:
    """One validation failure in plain words: the field it is about (when it has one) and why."""
    message = failure["msg"].removeprefix("Value error, ")
    location = failure["loc"]
    return f"{location[0]} {message[0].lower()}{message[1:]}" if location else message


class SegmentRow(BaseModel):
    """One segment worked: the annual revenue from one customer, its gross spend, TAM, SAM and SOM (money and
    customers), its share of the total TAM, and the path from today's customers to its SOM.

    ``som_customers`` and ``som`` are none with no SOM; ``som_multiple_of_today`` is none with no SOM or no customers
    today (or none of them); ``new_customers_per_year`` is none without ``som_years``, customers today or a SOM.
    ``price_period_given`` is false when the segment gave no ``price_period_months`` (the yearly default was used).
    """

    model_config = MODEL_CONFIG

    segment: int
    price_period_given: bool
    annual_value_per_customer: EquityQuantity
    customers: EquityQuantity
    gross_spend: EquityQuantity
    tam: EquityQuantity
    sam_customers: EquityQuantity
    sam: EquityQuantity
    som_customers: EquityQuantity | None = None
    som: EquityQuantity | None = None
    share_of_tam: EquityQuantity
    customers_today: EquityQuantity | None = None
    som_multiple_of_today: EquityQuantity | None = None
    new_customers_per_year: EquityQuantity | None = None


class MarketTotals(BaseModel):
    """The segments added up. The SOM total and the shares that use it are none unless every segment gives a SOM;
    ``som_multiple_of_revenue_today`` needs ``annual_revenue_today``."""

    model_config = MODEL_CONFIG

    customers: EquityQuantity
    gross_spend: EquityQuantity
    tam: EquityQuantity
    sam_customers: EquityQuantity
    sam: EquityQuantity
    som_customers: EquityQuantity | None = None
    som: EquityQuantity | None = None
    sam_share_of_tam: EquityQuantity
    som_share_of_sam: EquityQuantity | None = None
    som_multiple_of_revenue_today: EquityQuantity | None = None


class TopDownRow(BaseModel):
    """A top-down figure set beside the bottom-up one: its comparable part, the bottom-up TAM or SAM, the bottom-up as
    a share of the comparable part, and bottom-up minus comparable. A cross-check: never a verdict."""

    model_config = MODEL_CONFIG

    figure: int
    amount: EquityQuantity
    comparable: EquityQuantity
    compare_to: CompareTo
    bottom_up: EquityQuantity
    bottom_up_share: EquityQuantity
    difference: EquityQuantity


class BreakEvenRow(BaseModel):
    """The value of a sensitivity row's field at which the total ``metric`` equals ``target`` (see ``reach``)."""

    model_config = MODEL_CONFIG

    metric: MarketMetric
    target: EquityQuantity
    reach: BreakEvenReach
    value: EquityQuantity | None = None


class SensitivityCase(BaseModel):
    """The totals with the row's field at one of the founder's values, the rest at base; ``som_change`` is that SOM
    less the base SOM (none without a SOM total)."""

    model_config = MODEL_CONFIG

    value: EquityQuantity
    tam: EquityQuantity
    sam: EquityQuantity
    som: EquityQuantity | None = None
    som_change: EquityQuantity | None = None


class SensitivityResult(BaseModel):
    """One sensitivity row worked: each case, the lowest and highest SOM over the founder's values and the base, the
    swing between them, and the break-even values for the SOM target and the first top-down figure."""

    model_config = MODEL_CONFIG

    row: int
    field: SegmentField
    segment: int
    base_value: EquityQuantity
    cases: tuple[SensitivityCase, ...]
    som_low: EquityQuantity | None = None
    som_high: EquityQuantity | None = None
    som_swing: EquityQuantity | None = None
    at_som_target: BreakEvenRow | None = None
    at_top_down: BreakEvenRow | None = None


class MarketCheck(BaseModel):
    """One stated figure checked: what the deck says, what the calculator gives, computed - stated, the verdict."""

    model_config = MODEL_CONFIG

    key: MarketMetric
    stated: EquityQuantity
    computed: EquityQuantity
    difference: EquityQuantity
    verdict: CheckVerdict


class MarketSizingResult(BaseModel):
    """The market worked per segment and in total, the top-down cross-checks, the sensitivity rows, each stated
    figure's verdict, the flags, the overall verdict (``deal_check``'s rule) and the labelled assumptions."""

    model_config = MODEL_CONFIG

    scenario: MarketSizingScenario = "market_sizing"
    inputs: MarketSizingInput
    segments: tuple[SegmentRow, ...]
    totals: MarketTotals
    top_down: tuple[TopDownRow, ...]
    sensitivity: tuple[SensitivityResult, ...]
    checks: tuple[MarketCheck, ...]
    flags: tuple[MarketSizingFlag, ...]
    verdict: DealVerdict
    assumptions: tuple[EquityAssumption, ...]
