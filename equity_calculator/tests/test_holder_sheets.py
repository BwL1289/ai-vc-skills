"""The Dilution and Vesting sheets read back from a saved workbook: formats, the frozen header, live totals, fills.

No DB, no network: each test writes one workbook under pytest's temporary directory and loads it with openpyxl.
"""

from __future__ import annotations

import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.sheet_parts import Sheet
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from tests.support import DILUTION_ROUNDS, dilution, vesting

_FIRST = 0
_HALF = Fraction(1, 2)
_SUM = re.compile(r"^=SUM\(B(\d+):B(\d+)\)$")
_MONEYNESS_COLOURS = {"in_the_money": "C6EFCE", "at_the_money": "FFEB9C", "underwater": "FFC7CE"}


def _read_back(sheet: Sheet, tmp_path: Path) -> tuple[Worksheet, dict[str, int]]:
    """Write ``sheet`` alone, load it back, and check the header, the frozen pane, every format and plain value."""
    target = tmp_path / f"{sheet.title}.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)[sheet.title]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}

    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[1][:3]] == ["Line", *sheet.columns, "How it is computed"]
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key

    return page, rows


def _cell_value(page: Worksheet, row: int) -> Fraction:
    """A value cell as Excel would compute it: a number, or a ``=SUM`` range of cells resolved in turn."""
    value = page[f"B{row}"].value
    match = _SUM.match(str(value))
    if match is None:
        return Fraction(Decimal(str(value)))

    first, last = int(match.group(1)), int(match.group(2))
    return sum((_cell_value(page, part) for part in range(first, last + 1)), Fraction(0))


def _check_total(
    page: Worksheet, rows: dict[str, int], total: EquityQuantity, key: str, parts: tuple[str, ...]
) -> None:
    """The total at ``key`` is ``=SUM`` over exactly ``parts`` and adds to the model's total within the rounding."""
    first, last = rows[parts[_FIRST]], rows[parts[-1]]
    last_place = Fraction(Decimal(1).scaleb(-DISPLAY_PLACES[total.unit]))

    assert last - first == len(parts) - 1, key
    assert page[f"B{rows[key]}"].value == f"=SUM(B{first}:B{last})", key
    assert abs(_cell_value(page, rows[key]) - total.exact) <= len(parts) * _HALF * last_place, key


def test_the_dilution_sheet_reads_back_with_formats_and_the_live_lost_total(tmp_path: Path) -> None:
    """The Dilution sheet: percent formats, money formats on the amounts round, and the stake lost in all as a live
    =SUM over each round's lost line, equal to the stake before minus the final stake within the rounding."""
    rounds = [*DILUTION_ROUNDS, {"pre_money": "8000000", "investment": "2000000"}]
    sheet = sheet_for(dilution(holder_percent="50", rounds=rounds))
    page, rows = _read_back(sheet, tmp_path)
    lines = {line.key: line for line in sheet.lines}
    total = lines["total_lost"].values[_FIRST]
    assert isinstance(total, EquityQuantity)

    assert lines["total_lost"].total_of == tuple(f"round_{index}_lost" for index in range(1, 5))
    assert {line.key for line in sheet.lines if line.total_of} == {"total_lost"}
    assert page[f"B{rows['round_4_post_money']}"].number_format == NUMBER_FORMATS["money"]
    assert len(page.conditional_formatting) == 0
    _check_total(page, rows, total, "total_lost", lines["total_lost"].total_of)


def test_a_dilution_with_no_rounds_has_no_lost_total(tmp_path: Path) -> None:
    """No rounds: the stake before, the final stake and kept 100%, and no =SUM over nothing."""
    sheet = sheet_for(dilution(holder_percent="12.5", rounds=[]))
    page, rows = _read_back(sheet, tmp_path)

    assert [line.key for line in sheet.lines] == ["initial_stake", "final_stake", "kept_overall"]
    assert not any(str(page[f"B{row}"].value).startswith("=") for row in rows.values())


def test_the_vesting_sheet_reads_back_with_live_totals_and_the_moneyness_colours(tmp_path: Path) -> None:
    """The Vesting sheet: vested is =SUM(on schedule, accelerated), the grant =SUM(vested, unvested), both equal to
    the model within the share rounding; the moneyness cell carries one fill per verdict, its own three included."""
    result = vesting(
        grant_shares=1_000,
        month=13,
        strike_price="0.50",
        common_price="2",
        acceleration="single_trigger",
        acceleration_percent="33.3",
        change_of_control_month=13,
    )
    sheet = sheet_for(result)
    page, rows = _read_back(sheet, tmp_path)

    assert {line.key: line.total_of for line in sheet.lines if line.total_of} == {
        "vested": ("base_vested", "accelerated"),
        "grant": ("vested", "unvested"),
    }
    _check_total(page, rows, result.vested, "vested", ("base_vested", "accelerated"))
    _check_total(page, rows, result.grant, "grant", ("vested", "unvested"))
    assert page[f"B{rows['month']}"].value == "13 months"
    assert page[f"B{rows['acceleration_fired']}"].value == "yes"

    coordinate = f"B{rows['moneyness']}"
    assert page[coordinate].value == "in_the_money"
    fills: dict[str, str] = {}
    for cells in page.conditional_formatting:
        assert str(cells.sqref) == coordinate
        for rule in cells.rules:
            assert rule.dxf is not None and rule.dxf.fill is not None
            fills[rule.formula[_FIRST]] = str(rule.dxf.fill.start_color.rgb)
    assert set(fills) == {f'"{verdict}"' for verdict in VERDICT_FILLS}
    for verdict, colour in _MONEYNESS_COLOURS.items():
        assert fills[f'"{verdict}"'].endswith(colour), verdict


def test_a_grant_without_prices_has_no_money_lines_and_no_colours(tmp_path: Path) -> None:
    """No strike: the sheet stops at the share lines, with no verdict cell to colour."""
    sheet = sheet_for(vesting(grant_shares=48_000, month=30))
    page, _rows = _read_back(sheet, tmp_path)

    assert not {"strike_price", "exercise_cost", "moneyness"} & {line.key for line in sheet.lines}
    assert len(page.conditional_formatting) == 0
