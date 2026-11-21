"""The Excel workbook, written and read back: number formats, frozen header, live totals, verdict rules, values.

File output only: no DB, no network. Each test writes under pytest's temporary directory with ``save_workbook`` and
reads the file back with openpyxl, so what is checked is what Excel opens, not the objects in memory.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.layout import Line, Sheet, sheet_for
from equity_calculator.schemas.equity import EquityQuantity
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from tests.support import POOL_EXAMPLE, employee, investor, pool

_LABEL_WIDTH = 44
_VALUE_WIDTH = 24
_TEXT_WIDTH = 60
_FIRST = 0
_LAST = -1
_HALF = Fraction(1, 2)
# Each pool total and the lines it adds, written out here rather than read from the layout's ``total_of``, so a total
# that drops, adds or swaps a part fails instead of agreeing with itself.
_POOL_TOTAL_PARTS: dict[str, tuple[str, ...]] = {
    "total_shares": ("shares_existing_holders", "shares_option_pool", "shares_investor"),
    "total_ownership": ("ownership_existing_holders", "ownership_option_pool", "ownership_investor"),
    "post_money": ("value_existing_holders", "value_option_pool", "value_investor"),
}


def _sheets() -> tuple[Sheet, ...]:
    """All three scenarios with every optional line present: amounts and a holder, an offer, the rule of thumb."""
    return (
        sheet_for(investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.3", holder_percent="50")),
        sheet_for(
            employee(
                gain_percent="20",
                annual_cost="60000",
                valuation="2000000",
                margin_percent="50",
                offered_percent="7",
            )
        ),
        sheet_for(pool(**POOL_EXAMPLE)),
    )


def _written(tmp_path: Path, sheets: tuple[Sheet, ...]) -> dict[str, Worksheet]:
    """Save ``sheets`` to a new folder and read the file back, by sheet title."""
    target = tmp_path / "written" / "equity.xlsx"
    save_workbook(target, sheets)
    workbook = load_workbook(target)
    return {title: workbook[title] for title in workbook.sheetnames}


def _rows(sheet: Sheet) -> dict[str, int]:
    """Where each line lands: the header is row 1, the lines follow in order."""
    return {line.key: row for row, line in enumerate(sheet.lines, start=2)}


def _column(offset: int) -> str:
    return chr(ord("B") + offset)


def test_one_sheet_per_scenario_with_a_bold_frozen_header(tmp_path: Path) -> None:
    """Sheets come in order; row 1 is bold and frozen, naming the line, each column and how it is computed."""
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    assert list(written) == ["Investor", "Employee", "Pool"]
    for sheet in sheets:
        page = written[sheet.title]
        header = page[1][: 2 + len(sheet.columns)]  # the assumptions' source column sits past the header
        assert page.freeze_panes == FROZEN_PANE == "A2"
        assert [cell.value for cell in header] == ["Line", *sheet.columns, "How it is computed"]
        assert all(cell.font.bold for cell in header)
        for line, row in _rows(sheet).items():
            assert page.cell(row=row, column=1).value == next(item.label for item in sheet.lines if item.key == line)


def test_each_value_carries_its_units_format_and_the_models_rounding(tmp_path: Path) -> None:
    """Every number is the model's display rounding under its unit's format; text cells hold the text."""
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    for sheet in sheets:
        page, rows = written[sheet.title], _rows(sheet)
        for line in sheet.lines:
            for offset, value in enumerate(line.values):
                cell = page[f"{_column(offset)}{rows[line.key]}"]
                if isinstance(value, EquityQuantity):
                    assert cell.number_format == NUMBER_FORMATS[value.unit], (sheet.title, line.key)
                    if not line.total_of:
                        assert Decimal(str(cell.value)) == value.rounded, (sheet.title, line.key)
                else:
                    assert cell.value == value


def test_each_kind_of_number_gets_its_format(tmp_path: Path) -> None:
    """Percent, whole dollars, a six-place price, whole shares and a four-place multiplier, on real lines."""
    written = _written(tmp_path, _sheets())
    investor_page, pool_page = written["Investor"], written["Pool"]
    investor_rows, pool_rows = _rows(_sheets()[0]), _rows(_sheets()[2])

    assert investor_page[f"B{investor_rows['equity_sold']}"].number_format == "0.00%"
    assert investor_page[f"B{investor_rows['value_ratio']}"].number_format == '0.0000"x"'
    assert investor_page[f"B{investor_rows['post_money']}"].number_format == '"$"#,##0'
    assert pool_page[f"B{pool_rows['price_per_share']}"].number_format == '"$"#,##0.000000'
    assert pool_page[f"B{pool_rows['total_shares']}"].number_format == "#,##0"


def test_totals_are_live_sum_formulas_over_their_parts(tmp_path: Path) -> None:
    """Each total is ``=SUM`` over its own lines in each column, and the parts read back add up to the model's total.

    The parts come from ``_POOL_TOTAL_PARTS``, never from the layout, so a total over too few, too many or the wrong
    lines fails. Money parts add to the rounded total exactly (cents by largest remainder); shares and ownership are
    each rounded alone, so their sum is within half a last place per part of the exact total.
    """
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    investor_rows = _rows(sheets[0])
    assert written["Investor"][f"B{investor_rows['post_money']}"].value == (
        f"=SUM(B{investor_rows['pre_money']}:B{investor_rows['investment']})"
    )

    pool_sheet, page = sheets[2], written["Pool"]
    rows = _rows(pool_sheet)
    lines = {line.key: line for line in pool_sheet.lines}
    assert {line.key: line.total_of for line in pool_sheet.lines if line.total_of} == _POOL_TOTAL_PARTS
    for total, parts in _POOL_TOTAL_PARTS.items():
        first, last = rows[parts[_FIRST]], rows[parts[_LAST]]
        assert last - first == len(parts) - 1
        for offset in range(len(pool_sheet.columns)):
            letter = _column(offset)
            model_total = lines[total].values[offset]
            assert isinstance(model_total, EquityQuantity)
            read_back = sum(Fraction(Decimal(str(page[f"{letter}{rows[key]}"].value))) for key in parts)

            assert page[f"{letter}{rows[total]}"].value == f"=SUM({letter}{first}:{letter}{last})", total
            if model_total.unit == "money":
                assert read_back == Fraction(model_total.rounded), total
            else:
                last_place = Fraction(Decimal(1).scaleb(-DISPLAY_PLACES[model_total.unit]))
                assert abs(read_back - model_total.exact) <= len(parts) * _HALF * last_place, total


def test_parts_that_are_not_adjacent_sum_as_a_list(tmp_path: Path) -> None:
    """A total over rows with a gap between them lists each cell rather than a range that takes in the gap."""
    part = EquityQuantity.model_validate({"unit": "money", "exact": "1", "rounded": "1.00"})
    report = Sheet(
        "Gap",
        "A total that skips a line",
        ("Value",),
        (
            Line("first", "First", (part,), "given"),
            Line("skipped", "Skipped", (part,), "given"),
            Line("third", "Third", (part,), "given"),
            Line("total", "First + third", (part,), "first + third", ("first", "third")),
        ),
        (),
    )

    page = _written(tmp_path, (report,))["Gap"]

    assert page["B5"].value == "=SUM(B2,B4)"


def test_verdict_cells_carry_one_colour_rule_per_verdict(tmp_path: Path) -> None:
    """Each verdict cell has a rule per verdict text: green accept and grant, amber break even, red reject, no grant."""
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    checked = 0
    for sheet in sheets:
        page, rows = written[sheet.title], _rows(sheet)
        rules: dict[str, dict[str, str]] = {}
        for cells in page.conditional_formatting:
            for rule in cells.rules:
                assert rule.type == "cellIs" and rule.operator == "equal"
                assert rule.dxf is not None and rule.dxf.fill is not None
                rules.setdefault(str(cells.sqref), {})[rule.formula[0]] = str(rule.dxf.fill.start_color.rgb)

        verdict_cells = {f"B{rows[line.key]}" for line in sheet.lines if line.verdict}
        assert set(rules) == verdict_cells
        for coordinate in verdict_cells:
            assert set(rules[coordinate]) == {f'"{verdict}"' for verdict in VERDICT_FILLS}
            for verdict, colour in VERDICT_FILLS.items():
                assert rules[coordinate][f'"{verdict}"'].endswith(colour)
            checked += 1

    assert checked == len(["investor verdict", "employee verdict", "offer verdict"])
    assert VERDICT_FILLS["accept"] == VERDICT_FILLS["grant"] == "C6EFCE"
    assert VERDICT_FILLS["break_even"] == "FFEB9C"
    assert VERDICT_FILLS["reject"] == VERDICT_FILLS["no_grant"] == "FFC7CE"


def test_assumptions_follow_under_their_own_bold_header(tmp_path: Path) -> None:
    """One blank row after the lines, a bold header, then each assumption: key, setting, statement and source."""
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    for sheet in sheets:
        page = written[sheet.title]
        how_column = 2 + len(sheet.columns)
        header_row = 1 + len(sheet.lines) + 2
        header = [page.cell(row=header_row, column=column) for column in (1, 2, how_column, how_column + 1)]

        assert page.cell(row=header_row - 1, column=1).value is None
        assert [cell.value for cell in header] == ["Assumption", "Setting", "Statement", "Source"]
        assert all(cell.font.bold for cell in header)
        for row, item in enumerate(sheet.assumptions, start=header_row + 1):
            texts = [page.cell(row=row, column=column).value for column in (1, 2, how_column, how_column + 1)]
            assert texts == [item.key, item.setting, item.statement, item.source]
        assert len(sheet.assumptions) > 0


def test_column_widths_fit_labels_values_and_text(tmp_path: Path) -> None:
    """Labels are 44 wide, each value column 24, the how-it-is-computed and source columns 60."""
    sheets = _sheets()
    written = _written(tmp_path, sheets)

    for sheet in sheets:
        dimensions = written[sheet.title].column_dimensions
        value_letters = [_column(offset) for offset in range(len(sheet.columns))]
        text_letters = [_column(len(sheet.columns)), _column(len(sheet.columns) + 1)]

        assert dimensions["A"].width == _LABEL_WIDTH
        assert [dimensions[letter].width for letter in value_letters] == [_VALUE_WIDTH] * len(value_letters)
        assert [dimensions[letter].width for letter in text_letters] == [_TEXT_WIDTH] * 2
