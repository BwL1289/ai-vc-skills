"""The CLI's printed report for one scenario: its heading, an aligned table of its lines, its labelled assumptions.

Numbers print as the model's display rounding: a fraction as a percent with four places (7.5269%), a multiplier
with an ``x``, money and prices with a dollar sign and thousands separators, share counts with thousands separators
(a whole count without decimals). Nothing is recomputed here, and no step reads the decimal context.
"""

from __future__ import annotations

from equity_calculator.exact import HUNDRED, round_to_places
from equity_calculator.schemas.equity import EquityQuantity
from equity_calculator.sheet_parts import Sheet

# A fraction is rounded to 6 places for display, which is 4 places of its percent.
_PERCENT_PLACES = 4
_FIRST = 0
_COLUMN_GAP = "  "
_INDENT = "  "


def display(value: EquityQuantity | str) -> str:
    """``value`` as the report prints it (text values print as they are)."""
    if isinstance(value, str):
        return value

    match value.unit:
        case "fraction":
            return f"{round_to_places(value.exact * HUNDRED, _PERCENT_PLACES):,f}%"
        case "multiplier":
            return f"{value.rounded:,f}x"
        case "money" | "price":
            return f"${value.rounded:,f}"
        case "shares":
            # A whole count prints as one (10,000,000); a fractional count keeps its display places.
            whole = value.exact.denominator == 1
            return f"{value.exact.numerator:,}" if whole else f"{value.rounded:,f}"


def render_sheet(sheet: Sheet) -> str:
    """The printed report: heading, then label / value(s) / how-computed columns, then the assumptions."""
    header = ("Line", *sheet.columns, "How it is computed")
    rows = [(line.label, *(display(value) for value in line.values), line.how) for line in sheet.lines]
    widths = [max(len(row[index]) for row in (header, *rows)) for index in range(len(header))]
    last = len(header) - 1

    def aligned(row: tuple[str, ...]) -> str:
        cells = [
            cell.ljust(widths[index]) if index in (_FIRST, last) else cell.rjust(widths[index])
            for index, cell in enumerate(row)
        ]
        return (_INDENT + _COLUMN_GAP.join(cells)).rstrip()

    assumptions = [
        f"{_INDENT}- {item.key} = {item.setting}: {item.statement} Source: {item.source}." for item in sheet.assumptions
    ]

    return "\n".join([sheet.heading, aligned(header), *(aligned(row) for row in rows), "Assumptions:", *assumptions])
