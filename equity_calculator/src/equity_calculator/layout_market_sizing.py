"""A market size's report lines (the ``Market sizing`` sheet): the inputs, each segment, the totals, the checks.

One value column. The inputs as given come first (segment by segment, then the top-down figures and the rest), then
each segment worked (its annual revenue per customer, gross spend, TAM, SAM, SOM, share of the total TAM and its path
from today's customers), the totals (each a live ``=SUM`` of the segment lines in the workbook), the SAM and SOM
shares, each top-down figure set beside the bottom-up one, each stated figure checked, each sensitivity row with its
SOM range and break-even values, the flags in plain words, and the overall verdict. Segments are numbered, never
named: the calculator holds no free text.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import fraction, given_price
from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_market_sizing import (
    BreakEvenRow,
    MarketCheck,
    MarketSegment,
    MarketSizingFlag,
    MarketSizingResult,
    SegmentField,
    SegmentRow,
    SensitivityResult,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent
from equity_calculator.text import display

__all__ = ["market_sizing_sheet"]

_TITLE = "Market sizing"
_HEADING = (
    "A market size built bottom-up: TAM, SAM and SOM per segment and in total, the deck's figures checked, and the "
    "ranges that move it"
)
_COLUMNS = ("This market",)
_METRIC_NAMES = {"tam": "TAM", "sam": "SAM", "som": "SOM"}
_FIELD_NAMES: dict[SegmentField, str] = {
    "customers": "customers",
    "price": "price",
    "units_per_customer": "units per customer",
    "take_rate_percent": "take rate",
    "second_line_percent": "second line",
    "serviceable_percent": "serviceable share",
    "obtainable_percent": "share to win",
    "obtainable_customers": "customers to win",
    "obtainable_units": "units to win",
}
_CROSS_CHECK_NOTE = "; a cross-check with the top-down figure, not a target"
_UNDER_SMALLEST_SHARE = "under 0.0001%"
_PERIOD_DEFAULT = "not given: read as a yearly price (give 1 for a monthly one)"
_CUSTOMERS_SPLIT = "given, shown rounded so the segments add up to the total"
_PER_YEAR_HOW = "(SOM customers - customers today) / years, a straight line"
_NOT_WORKED = "not worked"
# The two fields that add up to the share of the main bill the company books.
_SHARE_FIELDS = ("take_rate_percent", "second_line_percent")
_NO_COUNT_HOW = "no market count (none given, or one equal to the customers to win): TAM and SAM would be the SOM again"
_PER_YEAR_MONTHS_HOW = "(SOM customers - customers today) / (months / 12), a straight line"
_REACH_WORDS = {
    "value": "reaches it exactly",
    "met_without_it": "met already with this field at its base",
    "does_not_move": "this field does not move that total",
    "out_of_range": "the segment would be refused at this value",
}


def _years(count: int) -> str:
    return "1 year" if count == 1 else f"{count} years"


def _months(count: int) -> str:
    return "1 month" if count == 1 else f"{count} months"


def _flag_words(flag: MarketSizingFlag) -> str:
    """What a flag means for the founder, in plain words, and what a VC is likely to ask."""
    words: dict[MarketSizingFlag, str] = {
        "segments_exceed_population": "The segments' customers add up to more than the population they come from, "
        "so a buyer is likely counted twice; a VC is likely to ask which segments overlap",
        "bottom_up_above_top_down": "The bottom-up figure is above the comparable part of a top-down figure; a VC is "
        "likely to ask whether segments overlap or the definitions differ",
        "sam_equals_tam": "No segment gives a serviceable share below 100%, so SAM equals TAM; a VC is likely to ask "
        "who the product cannot reach today",
        "som_not_given": "A segment gives no customers to win, so no SOM total is worked",
        "som_as_percent_only": "A SOM is given as a share of the serviceable customers, not as a count of customers; "
        "a VC is likely to ask for the customers, the channel and the year behind it",
        "som_from_zero_customers": "A segment with a SOM has no customers today; a VC is likely to ask what shows "
        "the first ones will come",
        "som_below_customers_today": "A segment's SOM customers are fewer than its customers today; check the count",
        "no_horizon_given": "A SOM is given with no year to reach it; a VC is likely to ask by when",
        "som_below_target": "The SOM total is below the revenue the plan needs from this market; a VC is likely to "
        "ask where the rest comes from",
        "som_target_out_of_reach": "No sensitivity row reaches the plan's revenue at a value its segment can take: "
        "each that moves the SOM would need a share above 100%, more customers to win than the segment can serve, or "
        "a number past the calculator's range; a VC is likely to ask which assumptions together close the gap",
        "price_period_defaulted": "A segment gives no months for its price, so the price is read as a yearly one; if "
        "it is a monthly price, that segment's TAM, SAM and SOM are 12 times too small: give the months it covers",
        "no_market_count": "A segment gives the customers to win and no count of its whole market (none, or one equal "
        "to the customers to win), so its TAM and SAM are not worked, nor the totals and comparisons built on them; "
        "a VC is likely to ask how many buyers there are in all",
    }
    return words[flag]


def _segment_given_lines(row: SegmentRow, segment: MarketSegment) -> list[Line]:
    """One segment's inputs as given (the price period marked as the default when it was left out). The buying
    customers show the model's split rounding, so the segments' lines add up to the total line that sums them; a line
    whose figure is not the typed count says it was rounded so."""
    name = f"Segment {row.segment}"
    key = f"segment_{row.segment}"
    if row.customers is not None and segment.customers is not None:
        customers_how = GIVEN if fraction(row.customers.rounded) == fraction(segment.customers) else _CUSTOMERS_SPLIT
        customers = Line(f"{key}_customers", f"{name}: buying customers", (row.customers,), customers_how)
    elif segment.customers is not None:
        how = "given, equal to what you plan to win: not a market count"
        customers = Line(f"{key}_customers", f"{name}: buying customers", (given("count", segment.customers),), how)
    else:
        customers = Line(f"{key}_customers", f"{name}: buying customers", ("not given",), "no count of the market")
    shown: list[tuple[str, str, EquityQuantity | str | None]] = [
        (f"{key}_price", f"{name}: price per unit", given_price(segment.price)),
        (f"{key}_units", f"{name}: units per customer", given("count", segment.units_per_customer)),
        (f"{key}_take_rate", f"{name}: take rate", given_percent(segment.take_rate_percent)),
        (
            f"{key}_second_line",
            f"{name}: second line (share of the main bill)",
            None if segment.second_line_percent is None else given_percent(segment.second_line_percent),
        ),
        (
            f"{key}_serviceable",
            f"{name}: serviceable share",
            given_percent(segment.serviceable_percent) if row.market_counted else None,
        ),
        (
            f"{key}_obtainable_percent",
            f"{name}: share of serviceable customers to win",
            None if segment.obtainable_percent is None else given_percent(segment.obtainable_percent),
        ),
        (
            f"{key}_obtainable_customers",
            f"{name}: customers to win",
            None if segment.obtainable_customers is None else given("count", segment.obtainable_customers),
        ),
        (
            f"{key}_obtainable_units",
            f"{name}: units to win (the price's unit)",
            None if segment.obtainable_units is None else given("count", segment.obtainable_units),
        ),
        (
            f"{key}_customers_today",
            f"{name}: customers today",
            None if segment.customers_today is None else given("count", segment.customers_today),
        ),
    ]
    lines = [Line(line_key, label, (value,), GIVEN) for line_key, label, value in shown if value is not None]
    period = Line(
        f"{key}_price_period",
        f"{name}: the price covers",
        (_months(segment.period_months()),),
        GIVEN if row.price_period_given else _PERIOD_DEFAULT,
    )
    return [customers, lines[0], period, *lines[1:]]


def _given_lines(result: MarketSizingResult) -> list[Line]:
    """Every input as given: the segments, the top-down figures, and the founder's other figures."""
    inputs = result.inputs
    lines: list[Line] = []
    for row, segment in zip(result.segments, inputs.segments, strict=True):
        lines += _segment_given_lines(row, segment)
    for number, top in enumerate(inputs.top_down, start=1):
        name = f"Top-down {number}"
        lines += [
            Line(f"top_down_{number}_amount", f"{name}: annual figure as stated", (given("money", top.amount),), GIVEN),
            Line(
                f"top_down_{number}_comparable_percent",
                f"{name}: share matching your definition",
                (given_percent(top.comparable_percent),),
                GIVEN,
            ),
            Line(f"top_down_{number}_compare_to", f"{name}: compared with", (_METRIC_NAMES[top.compare_to],), GIVEN),
        ]
    optional: list[tuple[str, str, EquityQuantity | str | None]] = [
        ("population", "Population the segments come from", _maybe("count", inputs.population)),
        ("annual_revenue_today", "Annual revenue today", _maybe("money", inputs.annual_revenue_today)),
        ("som_years", "Years to reach the SOM", None if inputs.som_years is None else _years(inputs.som_years)),
        ("som_months", "Months to reach the SOM", None if inputs.som_months is None else _months(inputs.som_months)),
        ("som_target", "Revenue the plan needs from this market", _maybe("money", inputs.som_target)),
        ("stated_tam", "TAM as stated", _maybe("money", inputs.stated_tam)),
        ("stated_sam", "SAM as stated", _maybe("money", inputs.stated_sam)),
        ("stated_som", "SOM as stated", _maybe("money", inputs.stated_som)),
        ("tolerance", "Tolerance", given_percent(inputs.tolerance_percent) if result.checks else None),
    ]
    lines += [Line(key, label, (value,), GIVEN) for key, label, value in optional if value is not None]
    return lines


def _maybe(unit: EquityUnit, value: Decimal | None) -> EquityQuantity | None:
    return None if value is None else given(unit, value)


def _share_how(how: str, share: EquityQuantity | None) -> str:
    """``how``, plus a note when a share above zero rounds to 0.0000%, so it never reads as none."""
    if share is not None and share.exact != 0 and share.rounded == 0:
        return f"{how}; {_UNDER_SMALLEST_SHARE}, not zero"
    return how


def _segment_lines(row: SegmentRow, per_year_how: str, *, second_line: bool = False) -> list[Line]:
    """One segment worked: its annual revenue per customer, gross spend, TAM, SAM, SOM, share and path."""
    name = f"Segment {row.segment}"
    key = f"segment_{row.segment}"
    share = "(take rate + second line)" if second_line else "take rate"
    gross_how = "customers × price a year × units" + (" × (1 + second line)" if second_line else "")
    shown: list[tuple[str, str, EquityQuantity | None, str]] = [
        (
            "value",
            "annual revenue per customer",
            row.annual_value_per_customer,
            f"price × 12 / months covered × units × {share}",
        ),
        ("gross_spend", "gross spend (before the take rate)", row.gross_spend, gross_how),
        ("tam", "TAM", row.tam, "customers × annual revenue per customer"),
        ("sam_customers", "SAM customers", row.sam_customers, "customers × serviceable share"),
        ("sam", "SAM", row.sam, "SAM customers × annual revenue per customer"),
        ("som_customers", "SOM customers", row.som_customers, "customers to win, or SAM customers × share to win"),
        ("som_units", "SOM units", row.som_units, "units to win, in the price's unit"),
        (
            "som",
            "SOM",
            row.som,
            "SOM customers × annual revenue per customer"
            if row.som_units is None
            else f"SOM units × price a year × {share}",
        ),
        (
            "share_of_tam",
            "share of total TAM",
            row.share_of_tam,
            _share_how("segment TAM / total TAM", row.share_of_tam),
        ),
        ("som_multiple", "SOM customers / today", row.som_multiple_of_today, "SOM customers / customers today"),
        (
            "new_per_year",
            "new customers a year to SOM",
            row.new_customers_per_year,
            per_year_how,
        ),
    ]
    lines = [
        Line(f"{key}_{suffix}", f"{name}: {label}", (value,), how)
        for suffix, label, value, how in shown
        if value is not None
    ]
    if not row.market_counted:
        lines.insert(1, Line(f"{key}_tam_sam", f"{name}: TAM and SAM", (_NOT_WORKED,), _NO_COUNT_HOW))
    return lines


def _total_lines(result: MarketSizingResult) -> list[Line]:
    """The totals, each the sum of its segment lines, then the shares and the SOM against today's revenue."""
    totals, numbers = result.totals, [row.segment for row in result.segments]

    def parts(suffix: str) -> tuple[str, ...]:
        return tuple(f"segment_{number}_{suffix}" for number in numbers)

    summed: list[tuple[str, str, EquityQuantity | None, str]] = [
        ("total_customers", "Total buying customers", totals.customers, "customers"),
        ("total_gross_spend", "Total gross spend (before the take rate)", totals.gross_spend, "gross_spend"),
        ("total_tam", "Total TAM", totals.tam, "tam"),
        ("total_sam_customers", "Total SAM customers", totals.sam_customers, "sam_customers"),
        ("total_sam", "Total SAM", totals.sam, "sam"),
        ("total_som_customers", "Total SOM customers", totals.som_customers, "som_customers"),
        ("total_som", "Total SOM", totals.som, "som"),
    ]
    lines = [
        Line(key, label, (value,), "sum of the segments", total_of=parts(suffix))
        for key, label, value, suffix in summed
        if value is not None
    ]
    if totals.tam is None:
        how = "a segment has no market count, so TAM, SAM and the shares built on them are not totalled"
        lines.insert(0, Line("total_tam_sam", "Total TAM and SAM", (_NOT_WORKED,), how))
    shares: list[tuple[str, str, EquityQuantity | None, str]] = [
        (
            "sam_share_of_tam",
            "SAM share of TAM",
            totals.sam_share_of_tam,
            _share_how("total SAM / total TAM", totals.sam_share_of_tam),
        ),
        (
            "som_share_of_sam",
            "SOM share of SAM",
            totals.som_share_of_sam,
            _share_how("total SOM / total SAM", totals.som_share_of_sam),
        ),
        (
            "som_multiple_of_revenue_today",
            "SOM / annual revenue today",
            totals.som_multiple_of_revenue_today,
            "total SOM / annual revenue today",
        ),
    ]
    lines += [Line(key, label, (value,), how) for key, label, value, how in shares if value is not None]
    return lines


def _top_down_lines(result: MarketSizingResult) -> list[Line]:
    """Each top-down figure beside the bottom-up one: a cross-check, never a verdict."""
    lines = []
    for row in result.top_down:
        name, key, metric = f"Top-down {row.figure}", f"top_down_{row.figure}", _METRIC_NAMES[row.compare_to]
        if row.bottom_up is None or row.bottom_up_share is None or row.difference is None:
            how = f"no bottom-up {metric} to compare: a segment has no market count"
            lines += [
                Line(f"{key}_comparable", f"{name}: comparable part", (row.comparable,), "figure × share matching"),
                Line(f"{key}_bottom_up", f"{name}: bottom-up comparison", (_NOT_WORKED,), how),
            ]
            continue
        lines += [
            Line(f"{key}_comparable", f"{name}: comparable part", (row.comparable,), "figure × share matching"),
            Line(f"{key}_bottom_up", f"{name}: bottom-up {metric}", (row.bottom_up,), f"total {metric}"),
            Line(
                f"{key}_bottom_up_share",
                f"{name}: bottom-up as a share of it",
                (row.bottom_up_share,),
                _share_how(f"bottom-up {metric} / comparable part (a cross-check)", row.bottom_up_share),
            ),
            Line(f"{key}_difference", f"{name}: difference", (row.difference,), f"bottom-up {metric} - comparable"),
        ]
    return lines


def _check_lines(check: MarketCheck) -> list[Line]:
    """One check: what the deck says, what the calculator gives, the difference and the verdict."""
    name, key = _METRIC_NAMES[check.key], f"check_{check.key}"
    return [
        Line(f"{key}_stated", f"{name}: the deck says", (check.stated,), GIVEN),
        Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), f"total {name}"),
        Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
        Line(
            f"{key}_verdict", f"{name}: verdict", (check.verdict,), "within the tolerance is consistent", verdict=True
        ),
    ]


def _break_even_lines(
    key: str, name: str, field: str, row: BreakEvenRow, note: str = "", *, shares: bool = False
) -> list[Line]:
    """Where a field takes a total to its target: the value (when there is one) and how it came out; ``note`` ends the
    value line's words. With ``shares`` the field is one of the take rate and the second line, which add up."""
    metric = _METRIC_NAMES[row.metric]
    how = f"base × (target - other segments' {metric}) / this segment's {metric}"
    if shares:
        how = (
            f"(base + the other share) × (target - other segments' {metric}) / this segment's {metric} - the other "
            "share (take rate and second line add up)"
        )
    target = display(row.target)
    lines = [
        Line(
            f"{key}_reach",
            f"{name}: {field} for {metric} = {target}",
            (row.reach,),
            _REACH_WORDS[row.reach],
        )
    ]
    if row.value is not None:
        lines.append(
            Line(
                f"{key}_value",
                f"{name}: {field} at {metric} = {target}",
                (row.value,),
                f"{how}{note}",
            )
        )
    return lines


def _sensitivity_lines(row: SensitivityResult, *, shares: bool = False) -> list[Line]:
    """One sensitivity row: the base value, each case's totals, the SOM range and the break-even values."""
    name, key = f"Sensitivity {row.row}", f"sensitivity_{row.row}"
    field = f"segment {row.segment} {_FIELD_NAMES[row.field]}"
    lines = [Line(f"{key}_base", f"{name}: {field}, base", (row.base_value,), GIVEN)]
    for number, case in enumerate(row.cases, start=1):
        at = f"{name} at {display(case.value)}"
        case_key = f"{key}_case_{number}"
        shown: list[tuple[str, str, EquityQuantity | None]] = [
            ("tam", "TAM", case.tam),
            ("sam", "SAM", case.sam),
            ("som", "SOM", case.som),
            ("som_change", "SOM change", case.som_change),
        ]
        lines += [
            Line(f"{case_key}_{suffix}", f"{at}: {label}", (value,), "the rest at base")
            for suffix, label, value in shown
            if value is not None
        ]
    ranges: list[tuple[str, str, EquityQuantity | None, str]] = [
        ("som_low", "SOM low", row.som_low, "lowest SOM over the values and the base"),
        ("som_high", "SOM high", row.som_high, "highest SOM over the values and the base"),
        ("som_swing", "SOM swing", row.som_swing, "SOM high - SOM low"),
    ]
    lines += [
        Line(f"{key}_{suffix}", f"{name}: {label}", (value,), how)
        for suffix, label, value, how in ranges
        if value is not None
    ]
    ends = (
        ("low", row.som_low_at, row.value_at_som_low, "above"),
        ("high", row.som_high_at, row.value_at_som_high, "below"),
    )
    for end, at, value, side in ends:
        if at == "base" and value is not None:
            how = f"every value you gave is {side} the base, so the SOM {end} is the base's"
            lines.append(Line(f"{key}_som_{end}_at_base", f"{name}: SOM {end} is at the base", (value,), how))
    if row.at_som_target is not None:
        lines += _break_even_lines(f"{key}_at_som_target", name, field, row.at_som_target, shares=shares)
    if row.at_top_down is not None:
        lines += _break_even_lines(f"{key}_at_top_down", name, field, row.at_top_down, _CROSS_CHECK_NOTE, shares=shares)
    return lines


def market_sizing_sheet(result: MarketSizingResult) -> Sheet:
    """The market size's lines: the inputs, each segment, the totals, cross-checks, checks, ranges, flags, verdict."""
    lines = _given_lines(result)
    per_year_how = _PER_YEAR_HOW if result.inputs.som_months is None else _PER_YEAR_MONTHS_HOW
    for row, segment in zip(result.segments, result.inputs.segments, strict=True):
        lines += _segment_lines(row, per_year_how, second_line=segment.second_line_percent is not None)
    lines += [*_total_lines(result), *_top_down_lines(result)]
    for check in result.checks:
        lines += _check_lines(check)
    for row in result.sensitivity:
        has_second = result.inputs.segments[row.segment - 1].second_line_percent is not None
        lines += _sensitivity_lines(row, shares=has_second and row.field in _SHARE_FIELDS)
    lines += [Line(f"flag_{flag}", "A VC is likely to ask", (flag,), _flag_words(flag)) for flag in result.flags]
    lines.append(
        Line(
            "verdict",
            "Overall verdict",
            (result.verdict,),
            "mismatch if any stated figure is; not_checked with none; a top-down figure never counts",
            verdict=True,
        )
    )
    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
