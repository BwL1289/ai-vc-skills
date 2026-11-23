"""``equity_calculator instrument_compare``: the report, ``--json``, the Priced vs note sheet read back, refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company BU from ``test_instrument_compare.py``.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_instrument_compare import InstrumentFlag
from equity_calculator.workbook import save_workbook
from openpyxl import load_workbook
from tests.support import COMPARE_BU, instrument_compare

_ARGPARSE_EXIT = 2
_COLUMNS = ("Priced round now (A)", "Note now (B)", "B - A")
_TODAY = [
    "instrument_compare",
    "--founder-shares",
    "8,000,000",
    "--team-shares",
    "1,000,000",
    "--unissued-pool-shares",
    "1,000,000",
    "--investment",
    "$2,000,000",
    "--priced-pre-money",
    "$8,000,000",
    "--priced-preference",
    "standard",
    "--note-valuation-cap",
    "$6,000,000",
    "--note-discount-percent",
    "20%",
    "--note-interest-rate-percent",
    "5",
    "--note-compounding",
    "simple",
    "--note-months-to-conversion",
    "12",
]
_ROUNDS = [
    "--next-round",
    "pre-money=27,000,000 investment=6,000,000 standard",
    "--next-round",
    "pre-money=9000000 investment=2000000 standard",
]
_EXITS = ["--exit", "5000000", "--exit", "$20,000,000", "--exit", "100000000"]
_COMPANY_BU = [*_TODAY, *_ROUNDS, *_EXITS]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


async def test_the_report_sets_a_beside_b_with_b_minus_a() -> None:
    report = await run(_COMPANY_BU)

    header = report.splitlines()[1]
    for column in _COLUMNS:
        assert column in header
    assert "$0.800000" in _line(report, "Today: price per share")
    assert "$0.600000" in _line(report, "Note's cap price")
    assert "$2,100,000.00" in _line(report, "Note owed when it converts")
    founders_now = _line(report, "Today: founders")
    assert "64.0000%" in founders_now and "80.0000%" in founders_now and "16.0000%" in founders_now
    founders_one = _line(report, "Next round 1: founders")
    assert "52.3636%" in founders_one and "48.4848%" in founders_one and "-3.8788%" in founders_one
    founders_exit = _line(report, "Next round 1: exit $20,000,000.00: founders")
    assert "$8,960,000.00" in founders_exit and "$8,296,296.29" in founders_exit and "$-663,703.70" in founders_exit
    assert "its cap price, the lower" in _line(report, "Next round 1: B's note: converts at")
    assert "its discount price, the lower" in _line(report, "Next round 2: B's note: converts at")
    assert "\nAssumptions:\n" in report


async def test_the_report_never_picks_an_option() -> None:
    lines = (await run(_COMPANY_BU)).lower().split("\nassumptions:\n")[0]

    for word in ("better", "worse", "recommend", "should", "choose", "pick", "we suggest"):
        assert re.search(rf"\b{word}\b", lines) is None, word


async def test_every_flag_prints_with_its_plain_words() -> None:
    report = await run(_COMPANY_BU)
    flags = instrument_compare(**COMPARE_BU).flags

    printed = [line.split()[1] for line in report.splitlines() if line.startswith("  Flag ")]
    assert tuple(printed) == flags
    assert set(flags) <= set(get_args(InstrumentFlag))


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_BU, "--json"]))

    assert printed == json.loads(instrument_compare(**COMPARE_BU).model_dump_json())
    first = printed["next_rounds"][0]
    assert Fraction(first["founders_ownership_difference"]["exact"]) == Fraction(-32, 825)


async def test_xlsx_writes_the_priced_vs_note_sheet(tmp_path: Path) -> None:
    target = tmp_path / "compare.xlsx"
    report = await run([*_COMPANY_BU, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    page = load_workbook(target)["Priced vs note"]
    labels = [row[0] for row in page.iter_rows(values_only=True)]
    assert "Today: founders" in labels
    assert "Next round 2: B's note: shares" in labels


def test_the_sheet_has_three_columns_and_a_value_for_each() -> None:
    sheet = sheet_for(instrument_compare(**COMPARE_BU))

    assert sheet.columns == _COLUMNS
    assert all(len(line.values) == len(_COLUMNS) for line in sheet.lines)
    assert len({line.key for line in sheet.lines}) == len(sheet.lines)


def test_the_workbook_saves_every_line(tmp_path: Path) -> None:
    target = tmp_path / "compare.xlsx"
    sheet = sheet_for(instrument_compare(**COMPARE_BU))
    save_workbook(target, (sheet,))

    page = load_workbook(target)[sheet.title]
    labels = [row[0] for row in page.iter_rows(values_only=True) if row[0]]
    assert [line.label for line in sheet.lines] == labels[1 : len(sheet.lines) + 1]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([*_TODAY, *_EXITS], "no_next_round_given: option B's note converts only at a next priced round"),
        ([*_TODAY, *_ROUNDS], "--exit is empty: give at least one exit"),
        (
            [*_TODAY, *_EXITS, "--next-round", "investment=1000000 standard"],
            "--next-round #1 pre-money: Field required",
        ),
        (
            [*_TODAY, *_EXITS, "--next-round", "pre-money=9000000 investment=1000000"],
            "--next-round #1 preference: give standard",
        ),
        ([*_COMPANY_BU, "--note-discount-percent", "100"], "--note-discount-percent: Input should be less than 100"),
        ([*_COMPANY_BU, "--founder-shares", "0"], "--founder-shares: Input should be greater than 0"),
        ([*_COMPANY_BU, "--exit", "-5"], "--exit #4: Input should be greater than or equal to 0"),
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert message in str(caught.value.code)
    assert "next_rounds" not in str(caught.value.code).replace("no_next_round_given", "")


@pytest.mark.parametrize(
    ("argv", "fragment"),
    [
        ([*_COMPANY_BU, "--next-round", "pre-money=9 bogus=1"], "unknown term"),
        ([*_COMPANY_BU, "--priced-preference", "standard standard"], "given twice"),
        ([*_COMPANY_BU, "--note-compounding", "weekly"], "invalid choice"),
        ([*_COMPANY_BU, "--note-months-to-conversion", "1.5"], "whole number of months"),
    ],
)
async def test_unreadable_arguments_exit_2(argv: list[str], fragment: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert fragment in capsys.readouterr().err


async def test_option_a_s_terms_are_required(capsys: pytest.CaptureFixture[str]) -> None:
    without = [item for item in _COMPANY_BU if item not in ("--priced-preference", "standard")]
    with pytest.raises(SystemExit) as caught:
        await run(without)

    assert caught.value.code == _ARGPARSE_EXIT
    assert re.search(r"required: --priced-preference", capsys.readouterr().err)


async def test_existing_holders_and_the_founder_s_own_terms_print_on_their_lines() -> None:
    """An existing series and SAFE, a capped participating series, a compounding note with no cap: each has its line."""
    argv = [
        "instrument_compare",
        "--founder-shares",
        "7000000",
        "--team-shares",
        "1000000",
        "--unissued-pool-shares",
        "1000000",
        "--existing-series",
        "shares=1000000 invested=1000000",
        "--existing-safe",
        "500000 valuation-cap=10000000",
        "--investment",
        "2000000",
        "--priced-pre-money",
        "8000000",
        "--priced-preference",
        "preference-multiple=1 participation=capped cap-multiple=3 rank=2",
        "--note-discount-percent",
        "20",
        "--note-interest-rate-percent",
        "6",
        "--note-compounding",
        "annual",
        "--note-months-to-conversion",
        "18",
        "--note-maturity-months",
        "24",
        "--next-round",
        "pre-money=27000000 investment=6000000 preference-multiple=1 participation=full",
        "--exit",
        "20000000",
    ]
    report = await run(argv)

    assert "1x of $1,000,000 invested, non-participating, rank 1" in _line(report, "Existing series 1: shares")
    assert "1x, participating up to 3x, rank 2" in _line(report, "A: series terms")
    assert "1x, full participation, rank 1" in _line(report, "Next round 1: series terms")
    assert "compounding annual, fractional power stub" in _line(report, "B: how interest accrues")
    assert "none" in _line(report, "B: valuation cap (pre-money)")
    assert "the round price, the lower" in _line(report, "Today: existing SAFE 1: converts at")
    assert "Next round 1: existing SAFE 1: shares" in report
    assert "approximate stub" in _line(report, "Note owed when it converts")
    assert "Note's cap price" not in report
    assert "Next round 1: existing investors" in report
