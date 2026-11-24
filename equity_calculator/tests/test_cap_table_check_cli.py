"""``equity_calculator cap_table_check``: the report, ``--json``, the Cap table check sheet read back, refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Companies CQ and CR from ``test_cap_table_check.py``.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_cap_table_check import CapTableFlag
from equity_calculator.workbook import save_workbook
from openpyxl import load_workbook
from tests.support import CAP_TABLE_CQ, CAP_TABLE_CR, cap_table_check

_ARGPARSE_EXIT = 2
_COMPANY_CQ = [
    "cap_table_check",
    "--share-class",
    "kind=common authorised-shares=8,000,000",
    "--share-class",
    "kind=preferred shares=1,000,000 authorised-shares=1,000,000 stated-percent=10.00",
    "--share-class",
    "kind=options_granted shares=500,000 stated-percent=5.00",
    "--share-class",
    "kind=options_unissued shares=250,000 stated-percent=2.50",
    "--share-class",
    "kind=warrants shares=100,000 stated-percent=1.00",
    "--holder",
    "share-class=1 shares=4,500,000 stated-percent=45.00 founder",
    "--holder",
    "share-class=1 shares=3,500,000 stated-percent=35.00 founder",
    "--holder",
    "share-class=1 shares=250,000 stated-percent=2.50 departed",
    "--stated-fully-diluted-shares",
    "10,000,000",
    "--stated-percent-basis",
    "fully_diluted",
    "--option-plan-reserve",
    "750,000",
    "--safe",
    "$1,000,000 valuation-cap=$12,000,000",
]
_COMPANY_CR = [
    "cap_table_check",
    "--share-class",
    "kind=common",
    "--share-class",
    "kind=options_granted shares=1,000,000",
    "--share-class",
    "kind=options_unissued shares=500,000",
    "--holder",
    "share-class=1 shares=5,000,000 stated-percent=50 founder",
    "--holder",
    "share-class=1 shares=3,000,000 stated-percent=30 founder",
    "--holder",
    "share-class=1 shares=500,000 stated-percent=5 departed",
    "--stated-percent-basis",
    "fully_diluted",
    "--safe",
    "1,000,000 valuation-cap=10,000,000",
    "--safe",
    "500,000 valuation-cap=8,000,000 discount-percent=20",
    "--preview",
    "pre-money=18,000,000 investment=4,000,000",
    "--planned-round",
    "investor-percent=20 pool-percent=5",
    "--planned-round",
    "investor-percent=20",
]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


async def test_the_report_ties_out_company_cq() -> None:
    report = await run(_COMPANY_CQ)

    assert "10,100,000" in _line(report, "Fully diluted shares (FD)")
    assert "44.5545%" in _line(report, "Holder line 1 (class 1, common): of fully diluted")
    assert "-250,000" in _line(report, "Class 1 (common): authorised left")
    assert "2.4752%" in _line(report, "Departed holders: of fully diluted")
    assert "101.0000%" in _line(report, "Percent column, line by line: the table says")
    assert 'rounds to the table\'s "45.00"' in report
    assert "mismatch" in _line(report, "Overall verdict")


async def test_every_flag_prints_with_its_plain_words_and_the_lawyer_where_legal() -> None:
    report = await run(_COMPANY_CQ)
    flags = cap_table_check(**CAP_TABLE_CQ).flags

    printed = [line.split()[1] for line in report.splitlines() if line.startswith("  Flag ")]
    assert tuple(printed) == flags
    assert set(flags) <= set(get_args(CapTableFlag))
    words = {line.split()[1]: line for line in report.splitlines() if line.startswith("  Flag ")}
    for flag in ("over_authorised", "common_authorised_below_fully_diluted", "unconverted_instruments_present"):
        assert "ask the company's lawyer" in words[flag], flag


async def test_the_report_never_rules_on_legal_validity() -> None:
    report = (await run(_COMPANY_CQ)).lower()

    assert "legal_validity = not checked" in report
    for ruling in ("is valid", "is invalid", "is legal", "is illegal", "validly issued."):
        assert ruling not in report, ruling


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_CQ, "--json"]))

    assert printed == json.loads(cap_table_check(**CAP_TABLE_CQ).model_dump_json())
    assert Fraction(printed["founders_fraction"]["exact"]) == Fraction(80, 101)


async def test_company_cr_s_preview_and_path_print_after_the_checks() -> None:
    report = await run(_COMPANY_CR)
    printed = json.loads(await run([*_COMPANY_CR, "--json"]))

    assert printed == json.loads(cap_table_check(**CAP_TABLE_CR).model_dump_json())
    assert "$1.507500" in _line(report, "Next round: price per share")
    assert "54.8182%" in _line(report, "After: founders' lines")
    assert "48.0000%" in _line(report, "Founders' path: after the last round")
    lines = report.splitlines()
    assert lines.index(_line(report, "Next round: pre-money")) > lines.index(_line(report, "Holder line 3 (class 1"))


async def test_xlsx_writes_the_cap_table_check_sheet_with_a_live_total(tmp_path: Path) -> None:
    target = tmp_path / "cap.xlsx"
    report = await run([*_COMPANY_CQ, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    page = load_workbook(target)["Cap table check"]
    rows = {row[0]: row[1] for row in page.iter_rows(values_only=True) if row[0]}
    assert str(rows["Fully diluted shares (FD)"]).startswith("=SUM(")
    assert str(rows["SAFEs and notes: amount"]).startswith("=SUM(")


def test_the_sheet_has_one_column_and_unique_keys() -> None:
    for fields in (CAP_TABLE_CQ, CAP_TABLE_CR):
        sheet = sheet_for(cap_table_check(**fields))

        assert sheet.columns == ("This cap table",)
        assert all(len(line.values) == 1 for line in sheet.lines)
        assert len({line.key for line in sheet.lines}) == len(sheet.lines)


def test_the_workbook_saves_every_line(tmp_path: Path) -> None:
    target = tmp_path / "cap.xlsx"
    sheet = sheet_for(cap_table_check(**CAP_TABLE_CR))
    save_workbook(target, (sheet,))

    page = load_workbook(target)[sheet.title]
    labels = [row[0] for row in page.iter_rows(values_only=True) if row[0]]
    assert [line.label for line in sheet.lines] == labels[1 : len(sheet.lines) + 1]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            [item for item in _COMPANY_CQ if item not in ("--stated-percent-basis", "fully_diluted")],
            "a stated-percent needs --stated-percent-basis",
        ),
        (
            ["cap_table_check", "--share-class", "kind=common", "--holder", "share-class=2 shares=10"],
            "--holder item 1 names share-class 2, past the last of the 1 given",
        ),
        (["cap_table_check", "--share-class", "kind=common"], "--share-class item 1 gives neither shares"),
        (
            ["cap_table_check", "--share-class", "kind=common shares=10", "--preview", "pre-money=9 investment=1"],
            "--preview needs at least one SAFE or note",
        ),
        (
            ["cap_table_check", "--share-class", "kind=common shares=10", "--planned-round", "investor-percent=20"],
            "--planned-round needs at least one holder line marked founder",
        ),
        (
            ["cap_table_check", "--share-class", "kind=warrants shares=10 authorised-shares=20"],
            "--share-class #1: Value error, authorised-shares is for a common or preferred class",
        ),
        (
            ["cap_table_check", "--share-class", "kind=common", "--holder", "share-class=1 shares=0"],
            "--holder #1 shares: Input should be greater than 0",
        ),
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    text = str(caught.value.code)
    assert message.replace("Value error, ", "") in text
    for field in ("stated_percent_basis", "conversion_preview", "planned_rounds", "share_class"):
        assert field not in text, field


@pytest.mark.parametrize(
    ("argv", "fragment"),
    [
        (["cap_table_check", "--share-class", "kind=stock"], "must be one of common"),
        (["cap_table_check", "--share-class", "kind=common", "--holder", "share-class=x shares=1"], "class's number"),
        (["cap_table_check", "--share-class", "kind=common", "--holder", "share-class=1 founder=yes"], "unknown term"),
        (["cap_table_check", "--share-class", "kind=common shares=1.5"], "whole number of shares"),
        (["cap_table_check", "--share-class", "kind=common kind=common"], "given twice"),
        (["cap_table_check", "--share-class", "kind=common", "--stated-percent-basis", "issued"], "invalid choice"),
        (["cap_table_check"], "required: --share-class"),
    ],
)
async def test_unreadable_arguments_exit_2(argv: list[str], fragment: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert fragment in capsys.readouterr().err
