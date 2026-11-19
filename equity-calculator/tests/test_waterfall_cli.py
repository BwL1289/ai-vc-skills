"""``equity-calculator waterfall``: the report, ``--json``, ``--xlsx``, every refusal, and the Waterfall sheet read
back.

No DB, no network: ``run`` is awaited in process and the sheet is built from ``compute``. The only files written are
workbooks, under pytest's temporary directory. The worked vectors and the brute-force oracle are
``test_waterfall.py`` and ``test_waterfall_oracle.py``.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.layout_waterfall import CONVERTS, STAYS
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.sheet_parts import Sheet
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from openpyxl.worksheet.worksheet import Worksheet
from tests.support import WATERFALL_A, WATERFALL_B, waterfall

_BASE = ["waterfall", "--exit-amount", "50,000,000", "--common-shares", "7000000"]
_A = "shares=2000000 invested=5000000"
_B = "shares=1000000 invested=10000000"
_B_CAPPED = f"{_B} participation=capped cap-multiple=3"
_PLAIN = [*_BASE, "--class", _A, "--class", _B]
_CAPPED = [*_BASE, "--class", _A, "--class", _B_CAPPED]
_ARGPARSE_EXIT = 2
_FIRST, _SECOND = 0, 1
_HEADER_ROW = 1
_HEADER_CELLS = 3
_FIRST_LINE_ROW = 2
_MODEL_FIELDS = re.compile(r"\b(classes|cap_multiple|preference_multiple|common_shares|exit_amount)\b")
_SUM = re.compile(r"^=SUM\((B\d+(?:[:,]B\d+)*)\)$")
_SUM_PART = re.compile(r"B(\d+)(?::B(\d+))?")
_PADDING = re.compile(" {2,}")
_COLUMN_GAP = "  "
_CONVERTS_FILL = "BDD7EE"
_STAYS_FILL = "EDEDED"
# Two classes owed nothing (0x) beside one common share: all three take a third of $100, so plain rounding of each
# gives $99.99 and only the largest-remainder split adds up to the exit.
_THIRDS: dict[str, object] = {"shares": 1, "invested": "1", "preference_multiple": "0"}


def _squeezed(report: str) -> str:
    """The report with each run of column padding cut to two spaces, so a line reads ``label  value  how``."""
    return re.sub(_PADDING, _COLUMN_GAP, report)


async def test_the_report_shows_each_class_choice_payouts_and_the_search() -> None:
    """$50M over A (2M shares, $5M) and B (1M shares, $10M): A converts for $8.9M, B stays for $10M, 2 passes."""
    report = _squeezed(await run(_PLAIN))

    assert report.startswith("Who gets what of an exit: preferences by rank, then the rest per share")
    for line in (
        "Class 1: payout if it converts  $8,888,888.89",
        "Class 1: choice  converts",
        "Class 2: choice  stays",
        "Class 2: seniority, participation  rank 1, no participation",
        "Common stock's payout  $31,111,111.11",
        "Total paid out  $50,000,000.00  every payout, cents by largest remainder (= E)",
        "Search passes  2 passes",
        "best_response_search = from none converting, at most 3 passes",
        "convert_when_strictly_better = a tie stays",
    ):
        assert line in report
    assert "stopped at its cap" not in report
    assert "cap_includes_preference" not in report


async def test_a_capped_class_reports_its_cap_line_and_the_participation_assumptions() -> None:
    """B capped at 3x: it stays and takes $10M + 1/10 of $40M = $14M (under its $30M cap); A converts for $8M."""
    report = _squeezed(await run(_CAPPED))

    for line in (
        "rank 1, participates up to 3x invested in all",
        "Class 2: stopped at its cap  no  cap × invested",
        "Class 1: choice  converts",
        "Class 2: choice  stays",
        "Class 1: payout  $8,000,000.00",
        "Class 2: payout  $14,000,000.00",
        "Common stock's payout  $28,000,000.00",
        "participation = ",
        "cap_includes_preference = ",
    ):
        assert line in report
    assert "Class 1: stopped at its cap" not in report


async def test_json_prints_exact_payouts_both_sides_and_the_passes() -> None:
    """--json: A's payout is exactly 80,000,000/9 (2/9 of the $40M rest), B's $10M, the common's 280,000,000/9."""
    printed = json.loads(await run([*_PLAIN, "--json"]))
    first, second = printed["rows"][_FIRST], printed["rows"][_SECOND]

    assert printed["scenario"] == "waterfall"
    assert printed["inputs"]["classes"][_FIRST] == {
        "shares": 2_000_000,
        "invested": "5000000",
        "preference_multiple": "1",
        "rank": 1,
        "participation": "none",
        "cap_multiple": None,
    }
    assert (first["index"], first["converts"], first["capped"]) == (1, True, False)
    assert first["payout"] == {"unit": "money", "exact": "80000000/9", "rounded": "8888888.89"}
    assert first["payout_per_share"]["exact"] == "40/9"
    assert first["payout_if_stays"]["exact"] == "5000000"
    assert first["preference_paid"]["exact"] == "0"
    assert (second["converts"], second["payout"]["exact"], second["payout_if_converts"]["exact"]) == (
        False,
        "10000000",
        "5000000",
    )
    assert printed["common_payout"] == {"unit": "money", "exact": "280000000/9", "rounded": "31111111.11"}
    assert printed["total"]["exact"] == "50000000"
    assert printed["passes"] == 2


async def test_a_search_held_past_its_pass_limit_exits_with_the_reason(monkeypatch: pytest.MonkeyPatch) -> None:
    """The $50M case settles on pass 2; held to 1 pass the CLI exits with the search's own sentence, no traceback."""
    monkeypatch.setattr("equity_calculator.waterfall.default_pass_limit", lambda inputs: 1)

    with pytest.raises(SystemExit) as caught:
        await run(_PLAIN)

    assert isinstance(caught.value.code, str)
    assert caught.value.code.startswith("no stable choice of which preferred classes convert was found in 1 passes")
    assert "Traceback" not in caught.value.code


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            [*_BASE, "--class", f"{_A} participation=capped"],
            "--class #1: participation capped needs cap-multiple: the whole take as a multiple of invested",
        ),
        ([*_BASE, "--class", f"{_A} cap-multiple=2"], "--class #1: cap-multiple goes with participation capped only"),
        (
            [*_BASE, "--class", _A, "--class", f"{_B} participation=capped cap-multiple=0.5"],
            "--class #2: cap-multiple (0.5) is below preference-multiple (1): the cap includes the preference",
        ),
        ([*_BASE, "--class", f"{_A} rank=13"], "--class #1 rank: Input should be less than or equal to 12"),
        ([*_BASE, "--class", "shares=0 invested=5000000"], "--class #1 shares: Input should be greater than 0"),
        ([*_BASE, "--class", "shares=2000000 invested=0"], "--class #1 invested: Input should be greater than 0"),
        (
            [*_BASE, "--class", f"{_A} preference-multiple=-1"],
            "--class #1 preference-multiple: Input should be greater than or equal to 0",
        ),
        ([*_BASE, "--class", "invested=5000000"], "--class #1 shares: Field required"),
        (
            ["waterfall", "--exit-amount", "1", "--common-shares", "0", "--class", _A],
            "--common-shares: Input should be greater than 0",
        ),
        (
            ["waterfall", "--exit-amount", "-1", "--common-shares", "1", "--class", _A],
            "--exit-amount: Input should be greater than or equal to 0",
        ),
        ([*_BASE, *(["--class", _A] * 13)], "--class: Tuple should have at most 12 items"),
    ],
)
async def test_refused_inputs_exit_naming_the_flag_class_and_term(argv: list[str], message: str) -> None:
    """A class the model refuses exits naming --class, which one (#N) and the term as typed, never a model field."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert not _MODEL_FIELDS.search(caught.value.code)


@pytest.mark.parametrize(
    ("argv", "detail"),
    [
        ([*_BASE, "--class", f"{_A} rank=1.5"], "must be a whole-number rank (1 is paid first), got '1.5'"),
        ([*_BASE, "--class", f"{_A} participation=some"], "must be one of none, full, capped, got 'some'"),
        ([*_BASE, "--class", f"{_A} colour=red"], "unknown term 'colour=red' (the terms are: shares=, invested="),
        ([*_BASE, "--class", f"{_A} shares=3"], "'shares' is given twice"),
        (_BASE, "the following arguments are required: --class"),
    ],
)
async def test_malformed_arguments_exit_2_with_argparse_usage(
    argv: list[str], detail: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing --class or a malformed term is refused by argparse (exit 2) naming --class and what was wrong."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    error = capsys.readouterr().err
    assert caught.value.code == _ARGPARSE_EXIT
    assert "--class" in error
    assert detail in error


async def test_xlsx_writes_one_waterfall_sheet(tmp_path: Path) -> None:
    """--xlsx writes one sheet named Waterfall and the report says where."""
    target = tmp_path / "out" / "Waterfall.xlsx"

    report = await run([*_CAPPED, "--xlsx", str(target)])

    assert report.endswith(f"\nWorkbook: {target}")
    assert load_workbook(target).sheetnames == ["Waterfall"]


def _read_back(sheet: Sheet, tmp_path: Path) -> tuple[Worksheet, dict[str, int]]:
    """Write ``sheet`` alone, load it back, and check the header, the frozen pane, every format and plain value."""
    target = tmp_path / f"{sheet.title}.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)[sheet.title]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=_FIRST_LINE_ROW)}

    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[_HEADER_ROW][:_HEADER_CELLS]] == ["Line", *sheet.columns, "How it is computed"]
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key

    return page, rows


def _cell_value(page: Worksheet, row: int) -> Decimal:
    """A value cell as Excel would compute it: a number, or a ``=SUM`` of cells and ranges resolved in turn."""
    value = page[f"B{row}"].value
    match = _SUM.match(str(value))
    if match is None:
        return Decimal(str(value))

    total = Decimal(0)
    for part in match.group(1).split(","):
        cells = _SUM_PART.fullmatch(part)
        assert cells is not None, part
        first, last = cells.group(1), cells.group(2) or cells.group(1)
        for cell_row in range(int(first), int(last) + 1):
            total += _cell_value(page, cell_row)

    return total


def test_the_sheet_total_is_a_live_sum_of_every_payout_and_adds_to_the_exit(tmp_path: Path) -> None:
    """$100 in thirds: the total is =SUM over exactly the two class payouts and the common's (not side by side, so
    a list of cells), and the cents in those cells add up to $100.00 exactly."""
    result = waterfall("100", _THIRDS, _THIRDS, common_shares=1)
    sheet = sheet_for(result)
    page, rows = _read_back(sheet, tmp_path)
    parts = ("class_1_payout", "class_2_payout", "common_payout")
    cents = [page[f"B{rows[key]}"].value for key in parts]

    assert {line.key: line.total_of for line in sheet.lines if line.total_of} == {"total": parts}
    assert page[f"B{rows['total']}"].value == "=SUM(" + ",".join(f"B{rows[key]}" for key in parts) + ")"
    assert sorted(Decimal(str(value)) for value in cents) == [Decimal("33.33"), Decimal("33.33"), Decimal("33.34")]
    assert _cell_value(page, rows["total"]) == Decimal(100)
    assert page[f"B{rows['passes']}"].value == "2 passes"


def test_a_search_that_settles_on_its_first_pass_says_one_pass() -> None:
    """$6M, short of both preferences: no class converts, so the first pass changes nothing and the line says 1 pass."""
    values = {line.key: line.values[_FIRST] for line in sheet_for(waterfall("6000000", WATERFALL_A, WATERFALL_B)).lines}

    assert values["passes"] == "1 pass"


def test_the_choice_cells_carry_the_converts_and_stays_fills(tmp_path: Path) -> None:
    """$50M with B capped: each class's choice cell has one fill per verdict, blue for converts and grey for stays;
    the cap line is on the capped class only."""
    capped = {**WATERFALL_B, "participation": "capped", "cap_multiple": "3"}
    sheet = sheet_for(waterfall("50000000", WATERFALL_A, capped))
    page, rows = _read_back(sheet, tmp_path)
    choices = {f"B{rows['class_1_choice']}": CONVERTS, f"B{rows['class_2_choice']}": STAYS}

    assert {key for key in rows if key.endswith("_capped")} == {"class_2_capped"}
    assert page[f"B{rows['class_2_capped']}"].value == "no"
    assert {coordinate: page[coordinate].value for coordinate in choices} == choices
    fills: dict[str, dict[str, str]] = {}
    for cells in page.conditional_formatting:
        coordinate = str(cells.sqref)
        for rule in cells.rules:
            assert rule.dxf is not None and rule.dxf.fill is not None
            fills.setdefault(coordinate, {})[rule.formula[_FIRST]] = str(rule.dxf.fill.start_color.rgb)
    assert set(fills) == set(choices)
    for colours in fills.values():
        assert set(colours) == {f'"{verdict}"' for verdict in VERDICT_FILLS}
        assert colours[f'"{CONVERTS}"'].endswith(_CONVERTS_FILL)
        assert colours[f'"{STAYS}"'].endswith(_STAYS_FILL)
