"""The formatted Excel workbook: one sheet per scenario, real number formats, live ``=SUM`` totals, verdict colours.

Each value cell holds the model's display rounding (a ``Decimal``) under its unit's number format; a total line
holds a live ``=SUM`` of the cells it adds, so an edited part re-totals; a verdict cell is coloured by conditional
formatting (green accept / grant / in the money, amber break even / at the money, red reject / no grant /
underwater; a waterfall class's choice is blue for converts and grey for stays, neither good nor bad), so an edited
verdict recolours. Row 1 is the bold header, frozen; the labelled assumptions follow under their own bold header.
A value of ``equity_calculator.result_range.RESULT_LIMIT`` or more in size is refused with ``ResultOutOfRange`` before
any file is written: openpyxl would write it as a blank cell and an ``=SUM`` over it would add it as zero.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from pathlib import Path

from equity_calculator.errors import ResultOutOfRange
from equity_calculator.result_range import OUT_OF_RANGE_REASON, beyond_limit
from equity_calculator.schemas.equity import EquityQuantity, EquityUnit
from equity_calculator.sheet_parts import Line, Sheet
from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

NUMBER_FORMATS: dict[EquityUnit, str] = {
    "fraction": "0.00%",
    "money": '"$"#,##0',
    "price": '"$"#,##0.000000',
    "shares": "#,##0",
    "multiplier": '0.0000"x"',
}

_GREEN = "C6EFCE"
_AMBER = "FFEB9C"
_RED = "FFC7CE"
# A waterfall class's choice is a fact, not a judgement: blue for a class that converts, grey for one that stays.
_BLUE = "BDD7EE"
_GREY = "EDEDED"
VERDICT_FILLS: dict[str, str] = {
    "accept": _GREEN,
    "grant": _GREEN,
    "break_even": _AMBER,
    "reject": _RED,
    "no_grant": _RED,
    "in_the_money": _GREEN,
    "at_the_money": _AMBER,
    "underwater": _RED,
    "converts": _BLUE,
    "stays": _GREY,
}

FROZEN_PANE = "A2"
_HEADER_ROW = 1
_LABEL_COLUMN = 1
_FIRST_VALUE_COLUMN = 2
_FIRST = 0
_LAST = -1
_ROWS_BEFORE_ASSUMPTIONS = 2
_LABEL_WIDTH = 44
_VALUE_WIDTH = 24
_TEXT_WIDTH = 60
_HOW_HEADER = "How it is computed"
_ASSUMPTION_KEY_HEADER = "Assumption"
_ASSUMPTION_SETTING_HEADER = "Setting"
_ASSUMPTION_STATEMENT_HEADER = "Statement"
_ASSUMPTION_SOURCE_HEADER = "Source"


def _fill(colour: str) -> PatternFill:
    return PatternFill(start_color=colour, end_color=colour, fill_type="solid")


def _sum_formula(column: int, rows: Sequence[int]) -> str:
    """``=SUM`` of ``rows`` in ``column``: a range when they are consecutive, else a list of cells."""
    letter = get_column_letter(column)
    ordered = sorted(rows)
    if ordered == list(range(ordered[_FIRST], ordered[_LAST] + 1)):
        return f"=SUM({letter}{ordered[_FIRST]}:{letter}{ordered[_LAST]})"

    return "=SUM(" + ",".join(f"{letter}{row}" for row in ordered) + ")"


def _colour_verdict(sheet: Worksheet, coordinate: str) -> None:
    """Conditional fills on a verdict cell, one rule per verdict text."""
    for verdict, colour in VERDICT_FILLS.items():
        rule = CellIsRule(operator="equal", formula=[f'"{verdict}"'], fill=_fill(colour))
        sheet.conditional_formatting.add(coordinate, rule)


def _write_line(sheet: Worksheet, row: int, line: Line, rows_by_key: dict[str, int]) -> None:
    """One line: its label, each value (or ``=SUM`` total) under its unit's format, and how it is computed."""
    sheet.cell(row=row, column=_LABEL_COLUMN, value=line.label)
    for offset, value in enumerate(line.values):
        column = _FIRST_VALUE_COLUMN + offset
        written: Decimal | str
        if line.total_of:
            written = _sum_formula(column, [rows_by_key[key] for key in line.total_of])
        elif isinstance(value, EquityQuantity):
            if beyond_limit(value.rounded):
                raise ResultOutOfRange(OUT_OF_RANGE_REASON)
            written = value.rounded
        else:
            written = value

        cell = sheet.cell(row=row, column=column, value=written)
        if isinstance(value, EquityQuantity):
            cell.number_format = NUMBER_FORMATS[value.unit]
        if line.verdict:
            _colour_verdict(sheet, cell.coordinate)

    sheet.cell(row=row, column=_FIRST_VALUE_COLUMN + len(line.values), value=line.how)


def _write_assumptions(sheet: Worksheet, report: Sheet, how_column: int) -> None:
    """The labelled assumptions under their own bold header; the statement sits in the wide how column."""
    header_row = sheet.max_row + _ROWS_BEFORE_ASSUMPTIONS
    columns = (_LABEL_COLUMN, _FIRST_VALUE_COLUMN, how_column, how_column + 1)
    headers = (
        _ASSUMPTION_KEY_HEADER,
        _ASSUMPTION_SETTING_HEADER,
        _ASSUMPTION_STATEMENT_HEADER,
        _ASSUMPTION_SOURCE_HEADER,
    )
    for column, text in zip(columns, headers, strict=True):
        sheet.cell(row=header_row, column=column, value=text).font = Font(bold=True)

    for row, item in enumerate(report.assumptions, start=header_row + 1):
        texts = (item.key, item.setting, item.statement, item.source)
        for column, text in zip(columns, texts, strict=True):
            sheet.cell(row=row, column=column, value=text).alignment = Alignment(wrap_text=True, vertical="top")


def write_sheet(sheet: Worksheet, report: Sheet) -> None:
    """Fill ``sheet`` with ``report``: bold frozen header, formatted lines, live totals, coloured verdicts."""
    sheet.append(["Line", *report.columns, _HOW_HEADER])
    for cell in sheet[_HEADER_ROW]:
        cell.font = Font(bold=True)
    sheet.freeze_panes = FROZEN_PANE

    rows_by_key: dict[str, int] = {}
    for row, line in enumerate(report.lines, start=_HEADER_ROW + 1):
        rows_by_key[line.key] = row
        _write_line(sheet, row, line, rows_by_key)

    how_column = _FIRST_VALUE_COLUMN + len(report.columns)
    _write_assumptions(sheet, report, how_column)
    sheet.column_dimensions[get_column_letter(_LABEL_COLUMN)].width = _LABEL_WIDTH
    for column in range(_FIRST_VALUE_COLUMN, how_column):
        sheet.column_dimensions[get_column_letter(column)].width = _VALUE_WIDTH
    for column in (how_column, how_column + 1):
        sheet.column_dimensions[get_column_letter(column)].width = _TEXT_WIDTH


def build_workbook(reports: Sequence[Sheet]) -> Workbook:
    """A workbook with one formatted sheet per report, in order."""
    workbook = Workbook()
    default = workbook.active
    if default is not None:
        workbook.remove(default)

    for report in reports:
        sheet: Worksheet = workbook.create_sheet(report.title)
        write_sheet(sheet, report)

    return workbook


def save_workbook(path: Path, reports: Sequence[Sheet]) -> None:
    """Write the workbook to ``path``, creating its folder (blocking: callers run it on a worker thread)."""
    workbook = build_workbook(reports)
    path.parent.mkdir(parents=True, exist_ok=True)
    workbook.save(path)
