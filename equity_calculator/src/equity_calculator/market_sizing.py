"""A founder's market size worked bottom-up: TAM, SAM and SOM per segment and in total, checks, cross-checks, ranges.

Notation (``equity_calculator.schemas.equity_market_sizing``), per segment s, every input the founder's:

- value_s = price_s · 12 / price_period_months_s · units_per_customer_s · take_rate_percent_s / 100, the annual
  revenue to the company from one buying customer (a two-year device at $200 is price 200, period 24: $100 a year);
  gross_s = customers_s · price_s · 12 / price_period_months_s · units_per_customer_s, the customers' whole annual
  spend before the take rate.
- TAM_s = customers_s · value_s; serviceable customers c_s = customers_s · serviceable_percent_s / 100;
  SAM_s = c_s · value_s; SOM customers = obtainable_customers_s, or c_s · obtainable_percent_s / 100;
  SOM_s = SOM customers · value_s. Totals are sums; the SOM total exists only when every segment gives a SOM.
- Path: SOM customers / customers today (today above 0), and (SOM customers - customers today) / som_years a year,
  a straight line. No compound rate (it would need a root, which an exact fraction cannot hold).
- Cross-check: comparable = amount · comparable_percent / 100; the bottom-up TAM (or SAM) over it and the difference.
  Never a verdict.
- Checks: a stated TAM, SAM or SOM within ``tolerance_percent`` of the computed one is consistent, the edge
  included (``deal_check``'s rule).
- Sensitivity: one field of one segment at each of the founder's values, everything else at base, the totals worked
  again. Every total is linear in any single field that moves it, so with T the target, M the total and M_s the
  segment's part, the value at which the total reaches T is x_0 · (T - (M - M_s)) / M_s, exactly.

Money parts are rounded to the cent by largest remainder, and counts of customers to the hundredth the same way, so
the segments add up to the rounded totals. A unit price the founder typed (given, a sensitivity base or value) is
shown exactly, to the cent at least, with no trailing zeros past it: a $0.0075 usage price never prints as $0.01,
nor a $0.00000125 one as $0.0000012. A break-even price, which is worked, is shown to the cent when that is
exact, else to as many places as it needs up to 6, and one under a hundred-thousandth of a dollar keeps two
significant digits (up to 15 places, the input floor).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import get_args

from equity_calculator.assumptions_market_sizing import market_sizing_assumptions
from equity_calculator.exact import (
    DISPLAY_PLACES,
    HUNDRED,
    ZERO,
    fraction,
    from_percent,
    given_price,
    price_quantity,
    quantity,
    round_to_places,
    split_cents,
)
from equity_calculator.schemas.equity_common import MIN_ADJUSTED_EXPONENT, SIZE_LIMIT, EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import DealVerdict
from equity_calculator.schemas.equity_market_sizing import (
    PERCENT_FIELDS,
    BreakEvenReach,
    BreakEvenRow,
    MarketCheck,
    MarketMetric,
    MarketSegment,
    MarketSizingFlag,
    MarketSizingInput,
    MarketSizingResult,
    MarketTotals,
    SegmentField,
    SegmentRow,
    SensitivityCase,
    SensitivityResult,
    SensitivityRow,
    TopDownRow,
)

__all__ = ["compute_market_sizing", "field_quantity", "field_unit"]

_MONTHS_PER_YEAR = 12
# The smallest nonzero size a decimal input may have (``BoundedDecimal``'s floor; its ceiling is ``SIZE_LIMIT``).
_SIZE_FLOOR = Fraction(1, 10**-MIN_ADJUSTED_EXPONENT)
_SPLIT_PLACES = 2
_HUNDREDTHS = 10**_SPLIT_PLACES

# Which fields of a segment move which total: TAM moves with every factor of the annual value and the customers; SAM
# also with the serviceable share; SOM given as a share with all of those plus that share; SOM given as a count with
# the factors of the annual value and the count only.
_MOVES_TAM: frozenset[SegmentField] = frozenset({"customers", "price", "units_per_customer", "take_rate_percent"})
_MOVES_SAM: frozenset[SegmentField] = frozenset({*_MOVES_TAM, "serviceable_percent"})
_MOVES_SOM_BY_PERCENT: frozenset[SegmentField] = frozenset({*_MOVES_SAM, "obtainable_percent"})
_MOVES_SOM_BY_COUNT: frozenset[SegmentField] = frozenset(
    {"price", "units_per_customer", "take_rate_percent", "obtainable_customers"}
)


@dataclass(frozen=True)
class _Segment:
    """One segment's figures as exact fractions (the SOM ones none without a SOM)."""

    customers: Fraction
    value: Fraction
    gross: Fraction
    tam: Fraction
    sam_customers: Fraction
    sam: Fraction
    som_customers: Fraction | None
    som: Fraction | None

    def metric(self, name: MarketMetric) -> Fraction | None:
        return {"tam": self.tam, "sam": self.sam, "som": self.som}[name]


@dataclass(frozen=True)
class _Totals:
    """The segments added up (the SOM ones none unless every segment gives a SOM)."""

    customers: Fraction
    gross: Fraction
    tam: Fraction
    sam_customers: Fraction
    sam: Fraction
    som_customers: Fraction | None
    som: Fraction | None

    def metric(self, name: MarketMetric) -> Fraction | None:
        return {"tam": self.tam, "sam": self.sam, "som": self.som}[name]


def _worked(segment: MarketSegment) -> _Segment:
    """One segment's annual value, gross spend, TAM, SAM and SOM."""
    customers = fraction(segment.customers)
    yearly_price = fraction(segment.price) * _MONTHS_PER_YEAR / segment.period_months()
    spend = yearly_price * fraction(segment.units_per_customer)
    value = spend * from_percent(segment.take_rate_percent)
    sam_customers = segment.serviceable_count()
    if segment.obtainable_customers is not None:
        som_customers: Fraction | None = fraction(segment.obtainable_customers)
    elif segment.obtainable_percent is not None:
        som_customers = sam_customers * from_percent(segment.obtainable_percent)
    else:
        som_customers = None

    return _Segment(
        customers=customers,
        value=value,
        gross=customers * spend,
        tam=customers * value,
        sam_customers=sam_customers,
        sam=sam_customers * value,
        som_customers=som_customers,
        som=None if som_customers is None else som_customers * value,
    )


def _total(parts: Sequence[Fraction | None]) -> Fraction | None:
    """The sum of ``parts``, or none when any is none."""
    if any(part is None for part in parts):
        return None
    return sum((part for part in parts if part is not None), ZERO)


def _totals(segments: Sequence[_Segment]) -> _Totals:
    return _Totals(
        customers=sum((s.customers for s in segments), ZERO),
        gross=sum((s.gross for s in segments), ZERO),
        tam=sum((s.tam for s in segments), ZERO),
        sam_customers=sum((s.sam_customers for s in segments), ZERO),
        sam=sum((s.sam for s in segments), ZERO),
        som_customers=_total([s.som_customers for s in segments]),
        som=_total([s.som for s in segments]),
    )


def _replaced(inputs: MarketSizingInput, row: SensitivityRow, value: Decimal) -> list[_Segment]:
    """Every segment worked, with ``row``'s field of its segment at ``value`` (already checked by the input model)."""
    worked = [_worked(segment) for segment in inputs.segments]
    index = row.segment - 1
    worked[index] = _worked(inputs.segments[index].model_copy(update={row.field: value}))
    return worked


def field_unit(name: SegmentField) -> EquityUnit:
    """The unit a value of ``name`` is shown in: a percent field as a fraction, the price as a unit price (never
    money, whose cents would hide a usage price's fraction of a cent), the rest as a count."""
    if name in PERCENT_FIELDS:
        return "fraction"
    return "price" if name == "price" else "count"


def field_quantity(name: SegmentField, value: Fraction) -> EquityQuantity:
    """A worked value of the field ``name`` (a break-even) as its quantity (a percent field's value as the fraction it
    names, a price as a unit price, rounded)."""
    if name == "price":
        return price_quantity(value)
    return quantity(field_unit(name), value / HUNDRED if name in PERCENT_FIELDS else value)


def given_field_quantity(name: SegmentField, value: Decimal) -> EquityQuantity:
    """A typed value of the field ``name`` (a sensitivity base or value): as ``field_quantity``, but a price exactly
    as typed, never rounded."""
    if name == "price":
        return given_price(value)
    return field_quantity(name, fraction(value))


def _moves(segment: MarketSegment, name: SegmentField, metric: MarketMetric) -> bool:
    """Whether the field ``name`` of ``segment`` is a factor of its ``metric``."""
    if metric == "tam":
        return name in _MOVES_TAM
    if metric == "sam":
        return name in _MOVES_SAM
    if segment.obtainable_customers is not None:
        return name in _MOVES_SOM_BY_COUNT
    return name in _MOVES_SOM_BY_PERCENT


def _allowed(segment: MarketSegment, name: SegmentField, value: Fraction) -> bool:
    """Whether ``segment`` with ``name`` at ``value`` keeps the segment's rules (the input model's, in fractions): the
    size every decimal input has (at least 1e-15 and under 1e16), a percent up to 100, no fewer customers than today's,
    and no more customers to win than the serviceable ones."""
    if value != ZERO and not _SIZE_FLOOR <= abs(value) < SIZE_LIMIT:
        return False
    if name in PERCENT_FIELDS and value > HUNDRED:
        return False
    customers = value if name == "customers" else fraction(segment.customers)
    serviceable = value if name == "serviceable_percent" else fraction(segment.serviceable_percent)
    obtainable = value if name == "obtainable_customers" else segment.obtainable_customers
    if segment.customers_today is not None and fraction(segment.customers_today) > customers:
        return False
    return obtainable is None or Fraction(obtainable) <= customers * serviceable / HUNDRED


def _break_even(
    inputs: MarketSizingInput,
    row: SensitivityRow,
    base: _Totals,
    metric: MarketMetric,
    target: Fraction,
    *,
    at_least: bool = False,
) -> BreakEvenRow:
    """The value of ``row``'s field at which the total ``metric`` equals ``target``.

    With ``at_least`` (the plan's revenue, a floor to reach) a total already at or above ``target`` is
    ``met_without_it``, with no value: the field need not move. Without it (a top-down figure, a cross-check) the value
    is given either way. ``does_not_move`` is tested first, so a field that is no factor of the total is reported so
    even when the target is already met.
    """
    segment = inputs.segments[row.segment - 1]
    own = _worked(segment).metric(metric)
    total = base.metric(metric)
    target_quantity = quantity("money", target)
    if own is None or total is None or not _moves(segment, row.field, metric):
        return BreakEvenRow(metric=metric, target=target_quantity, reach="does_not_move")
    needed = target - (total - own)
    if needed <= ZERO or (at_least and total >= target):
        return BreakEvenRow(metric=metric, target=target_quantity, reach="met_without_it")
    value = fraction(getattr(segment, row.field)) * needed / own
    reach: BreakEvenReach = "value" if _allowed(segment, row.field, value) else "out_of_range"
    return BreakEvenRow(metric=metric, target=target_quantity, reach=reach, value=field_quantity(row.field, value))


def _sensitivity(inputs: MarketSizingInput, base: _Totals) -> tuple[SensitivityResult, ...]:
    """Each sensitivity row worked: its cases, the SOM range and swing, and its break-even values."""
    results = []
    first_top_down = inputs.top_down[0] if inputs.top_down else None
    for number, row in enumerate(inputs.sensitivity, start=1):
        cases = []
        soms: list[Fraction | None] = [base.som]
        for value in row.values:
            worked = _totals(_replaced(inputs, row, value))
            change = None if worked.som is None or base.som is None else worked.som - base.som
            soms.append(worked.som)
            cases.append(
                SensitivityCase(
                    value=given_field_quantity(row.field, value),
                    tam=quantity("money", worked.tam),
                    sam=quantity("money", worked.sam),
                    som=_optional("money", worked.som),
                    som_change=_optional("money", change),
                )
            )
        known = [som for som in soms if som is not None]
        low, high = (min(known), max(known)) if len(known) == len(soms) else (None, None)
        at_target = None
        if inputs.som_target is not None and base.som is not None:
            at_target = _break_even(inputs, row, base, "som", fraction(inputs.som_target), at_least=True)
        at_top_down = None
        if first_top_down is not None:
            comparable = fraction(first_top_down.amount) * from_percent(first_top_down.comparable_percent)
            at_top_down = _break_even(inputs, row, base, first_top_down.compare_to, comparable)
        results.append(
            SensitivityResult(
                row=number,
                field=row.field,
                segment=row.segment,
                base_value=given_field_quantity(row.field, getattr(inputs.segments[row.segment - 1], row.field)),
                cases=tuple(cases),
                som_low=_optional("money", low),
                som_high=_optional("money", high),
                som_swing=None if low is None or high is None else quantity("money", high - low),
                at_som_target=at_target,
                at_top_down=at_top_down,
            )
        )
    return tuple(results)


def _checks(inputs: MarketSizingInput, base: _Totals) -> tuple[MarketCheck, ...]:
    """One check per stated TAM, SAM and SOM: within the relative tolerance (the edge included) is consistent."""
    relative = from_percent(inputs.tolerance_percent)
    checks = []
    stated_figures: tuple[tuple[MarketMetric, Decimal | None], ...] = (
        ("tam", inputs.stated_tam),
        ("sam", inputs.stated_sam),
        ("som", inputs.stated_som),
    )
    for key, stated in stated_figures:
        computed = base.metric(key)
        if stated is None or computed is None:
            continue
        difference = computed - fraction(stated)
        checks.append(
            MarketCheck(
                key=key,
                stated=quantity("money", fraction(stated)),
                computed=quantity("money", computed),
                difference=quantity("money", difference),
                verdict="consistent" if abs(difference) <= relative * computed else "mismatch",
            )
        )
    return tuple(checks)


def _flags(
    inputs: MarketSizingInput, base: _Totals, sensitivity: tuple[SensitivityResult, ...]
) -> tuple[MarketSizingFlag, ...]:
    """Every flag that holds, in ``MarketSizingFlag``'s order."""
    segments = inputs.segments
    worked = [_worked(segment) for segment in segments]
    found: set[MarketSizingFlag] = set()
    if not all(segment.period_given() for segment in segments):
        found.add("price_period_defaulted")
    if inputs.population is not None and base.customers > fraction(inputs.population):
        found.add("segments_exceed_population")
    for top in inputs.top_down:
        bottom_up = base.metric(top.compare_to)
        if bottom_up is not None and bottom_up > fraction(top.amount) * from_percent(top.comparable_percent):
            found.add("bottom_up_above_top_down")
    if all(segment.serviceable_percent == 100 for segment in segments):
        found.add("sam_equals_tam")
    if not all(segment.has_som() for segment in segments):
        found.add("som_not_given")
    if any(segment.obtainable_percent is not None for segment in segments):
        found.add("som_as_percent_only")
    for segment, figures in zip(segments, worked, strict=True):
        if figures.som_customers is None or segment.customers_today is None:
            continue
        if segment.customers_today == 0:
            found.add("som_from_zero_customers")
        elif figures.som_customers < fraction(segment.customers_today):
            found.add("som_below_customers_today")
    if any(segment.has_som() for segment in segments) and inputs.som_years is None:
        found.add("no_horizon_given")
    if inputs.som_target is not None and base.som is not None and base.som < fraction(inputs.som_target):
        found.add("som_below_target")
        reaches = [row.at_som_target.reach for row in sensitivity if row.at_som_target is not None]
        if "out_of_range" in reaches and "value" not in reaches:
            found.add("som_target_out_of_reach")
    return tuple(flag for flag in _FLAG_ORDER if flag in found)


_FLAG_ORDER: tuple[MarketSizingFlag, ...] = get_args(MarketSizingFlag)


def _verdict(checks: tuple[MarketCheck, ...]) -> DealVerdict:
    """``not_checked`` with no check, ``mismatch`` if any figure is one, else ``consistent``."""
    if not checks:
        return "not_checked"
    return "mismatch" if any(check.verdict == "mismatch" for check in checks) else "consistent"


def _optional(unit: EquityUnit, value: Fraction | None) -> EquityQuantity | None:
    return None if value is None else quantity(unit, value)


def _split(unit: EquityUnit, parts: Sequence[Fraction]) -> tuple[EquityQuantity, ...]:
    """``parts`` rounded to hundredths by largest remainder, so they add up to their rounded total exactly."""
    assert DISPLAY_PLACES[unit] == _SPLIT_PLACES, unit
    hundredths = split_cents(parts)
    return tuple(
        EquityQuantity(unit=unit, exact=part, rounded=round_to_places(Fraction(count, _HUNDREDTHS), _SPLIT_PLACES))
        for part, count in zip(parts, hundredths, strict=True)
    )


def _split_optional(unit: EquityUnit, parts: Sequence[Fraction | None]) -> tuple[EquityQuantity | None, ...]:
    """``parts`` split as ``_split`` when every one is given; else each rounded on its own (no total to add up to)."""
    if all(part is not None for part in parts):
        return _split(unit, [part for part in parts if part is not None])
    return tuple(_optional(unit, part) for part in parts)


def _segment_rows(inputs: MarketSizingInput, worked: list[_Segment], base: _Totals) -> tuple[SegmentRow, ...]:
    """Each segment's row, its money and customer parts rounded so they add up to the totals."""
    customers = _split("count", [s.customers for s in worked])
    gross = _split("money", [s.gross for s in worked])
    tam = _split("money", [s.tam for s in worked])
    sam_customers = _split("count", [s.sam_customers for s in worked])
    sam = _split("money", [s.sam for s in worked])
    som_customers = _split_optional("count", [s.som_customers for s in worked])
    som = _split_optional("money", [s.som for s in worked])
    rows = []
    for index, (segment, figures) in enumerate(zip(inputs.segments, worked, strict=True)):
        today = None if segment.customers_today is None else fraction(segment.customers_today)
        multiple = per_year = None
        if figures.som_customers is not None and today is not None:
            if today > ZERO:
                multiple = figures.som_customers / today
            if inputs.som_years is not None:
                per_year = (figures.som_customers - today) / inputs.som_years
        rows.append(
            SegmentRow(
                segment=index + 1,
                price_period_given=segment.period_given(),
                annual_value_per_customer=quantity("money", figures.value),
                customers=customers[index],
                gross_spend=gross[index],
                tam=tam[index],
                sam_customers=sam_customers[index],
                sam=sam[index],
                som_customers=som_customers[index],
                som=som[index],
                share_of_tam=quantity("fraction", figures.tam / base.tam),
                customers_today=_optional("count", today),
                som_multiple_of_today=_optional("multiplier", multiple),
                new_customers_per_year=_optional("count", per_year),
            )
        )
    return tuple(rows)


def _market_totals(inputs: MarketSizingInput, base: _Totals) -> MarketTotals:
    revenue_today = inputs.annual_revenue_today
    som_share = som_multiple = None
    if base.som is not None:
        som_share = base.som / base.sam
        if revenue_today is not None:
            som_multiple = base.som / fraction(revenue_today)
    return MarketTotals(
        customers=quantity("count", base.customers),
        gross_spend=quantity("money", base.gross),
        tam=quantity("money", base.tam),
        sam_customers=quantity("count", base.sam_customers),
        sam=quantity("money", base.sam),
        som_customers=_optional("count", base.som_customers),
        som=_optional("money", base.som),
        sam_share_of_tam=quantity("fraction", base.sam / base.tam),
        som_share_of_sam=_optional("fraction", som_share),
        som_multiple_of_revenue_today=_optional("multiplier", som_multiple),
    )


def _top_down_rows(inputs: MarketSizingInput, base: _Totals) -> tuple[TopDownRow, ...]:
    rows = []
    for number, top in enumerate(inputs.top_down, start=1):
        comparable = fraction(top.amount) * from_percent(top.comparable_percent)
        bottom_up = base.tam if top.compare_to == "tam" else base.sam
        rows.append(
            TopDownRow(
                figure=number,
                amount=quantity("money", fraction(top.amount)),
                comparable=quantity("money", comparable),
                compare_to=top.compare_to,
                bottom_up=quantity("money", bottom_up),
                bottom_up_share=quantity("fraction", bottom_up / comparable),
                difference=quantity("money", bottom_up - comparable),
            )
        )
    return tuple(rows)


def compute_market_sizing(inputs: MarketSizingInput) -> MarketSizingResult:
    """The market worked per segment and in total, the cross-checks, the sensitivity rows, the checks and flags."""
    worked = [_worked(segment) for segment in inputs.segments]
    base = _totals(worked)
    sensitivity = _sensitivity(inputs, base)
    checks = _checks(inputs, base)

    return MarketSizingResult(
        inputs=inputs,
        segments=_segment_rows(inputs, worked, base),
        totals=_market_totals(inputs, base),
        top_down=_top_down_rows(inputs, base),
        sensitivity=sensitivity,
        checks=checks,
        flags=_flags(inputs, base, sensitivity),
        verdict=_verdict(checks),
        assumptions=market_sizing_assumptions(inputs, bool(checks)),
    )
