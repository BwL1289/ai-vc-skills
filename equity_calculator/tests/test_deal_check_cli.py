"""``equity_calculator deal_check``: the report, ``--json``, the Deal check sheet read back, and refusals naming flags.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company A, B and C from ``test_deal_check.py``.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from equity_calculator.__main__ import run
from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from tests.support import DEAL_A, DEAL_C, deal_check

_ARGPARSE_EXIT = 2
_FIRST = 0
_HALF = Fraction(1, 2)
_COMPANY_A = [
    "deal_check",
    "--investment",
    "3000000",
    "--pre-money",
    "$12,000,000",
    "--stated-investor-percent",
    "20%",
    "--fully-diluted-shares",
    "8,000,000",
    "--target-pool-percent",
    "10",
    "--holder-percent",
    "100",
    "--cash-on-hand",
    "400000",
    "--planned-monthly-gross-burn",
    "180000",
    "--stated-runway-months",
    "24",
]
_COMPANY_C = [
    "deal_check",
    "--investment",
    "2500000",
    "--pre-money",
    "10000000",
    "--fully-diluted-shares",
    "8000000",
    "--note",
    "500000 interest-rate-percent=6 months-outstanding=18 compounding=simple valuation-cap=8000000 "
    "discount-percent=20",
    "--holder-percent",
    "100",
    "--stated-holder-percent",
    "80",
    "--cash-on-hand",
    "300000",
    "--planned-monthly-gross-burn",
    "210000",
    "--planned-monthly-revenue",
    "35000",
    "--current-monthly-gross-burn",
    "120000",
    "--current-monthly-revenue",
    "20000",
    "--stated-runway-months",
    "24",
    "--use-of-funds",
    "50%",
    "--use-of-funds",
    "30%",
    "--use-of-funds",
    "20%",
]
_VERDICT_COLOURS = {"consistent": "C6EFCE", "mismatch": "FFC7CE", "not_checked": "FFEB9C"}
_MODEL_FIELD = re.compile(r"\b[a-z]+_[a-z_]+\b")


async def test_the_report_shows_each_check_the_flags_and_the_verdict() -> None:
    report = await run(_COMPANY_A)

    assert report.startswith("A fundraising ask checked against itself")
    for text in (
        "Runway: the deck says",
        "24.00 months",
        "18.89 months",
        "-5.11 months",
        "Effective pre-money",
        "$10,500,000.00",
        "Pre-money pays for: new pool",
        "$1,500,000.00",
        "pool_in_pre_money_lowers_price",
        "A VC is likely to ask",
    ):
        assert text in report
    assert re.search(r"Overall verdict +mismatch", report)
    assert "post_money_rule = post-money = V + I" in report


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_C, "--json"]))
    expected = json.loads(deal_check(**DEAL_C).model_dump_json())

    assert printed == expected
    assert printed["scenario"] == "deal_check"
    assert printed["verdict"] == "mismatch"
    assert [check["key"] for check in printed["checks"]] == ["holder_percent", "runway_months", "use_of_funds_total"]


async def test_safes_and_notes_keep_their_order_and_amount_lines_read_as_dollars() -> None:
    printed = json.loads(
        await run(
            [
                "deal_check",
                "--investment",
                "2000000",
                "--pre-money",
                "8000000",
                "--fully-diluted-shares",
                "1000000",
                "--note",
                "100000 interest-rate-percent=5 months-outstanding=12",
                "--safe",
                "200000 valuation-cap=4000000",
                "--use-of-funds",
                "$1,200,000",
                "--use-of-funds",
                "800000",
                "--json",
            ]
        )
    )

    assert [row["kind"] for row in printed["round"]["conversions"]] == ["note", "safe"]
    assert [line["amount"] for line in printed["inputs"]["use_of_funds"]] == ["1200000", "800000"]
    assert printed["checks"][-1]["verdict"] == "consistent"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["deal_check", "--investment", "1"], "give --pre-money, --post-money or --stated-investor-percent"),
        (
            ["deal_check", "--investment", "1", "--pre-money", "4", "--safe", "1 valuation-cap=2"],
            "--fully-diluted-shares is needed to convert SAFEs and notes",
        ),
        (
            [
                "deal_check",
                "--investment",
                "1",
                "--pre-money",
                "4",
                "--fully-diluted-shares",
                "10",
                "--safe",
                "1 valuation-cap=2",
                "--safe",
                "1",
            ],
            "--safe #2: a SAFE needs valuation-cap or discount-percent",
        ),
        (
            ["deal_check", "--investment", "1", "--pre-money", "4", "--use-of-funds", "1", "--use-of-funds=-2"],
            "--use-of-funds #2 amount: Input should be greater than 0",
        ),
        (
            ["deal_check", "--investment", "1", "--pre-money", "4", "--use-of-funds", "1", "--use-of-funds", "5%"],
            "give every --use-of-funds line as an amount or every one as a percent",
        ),
        (
            ["deal_check", "--investment", "1", "--pre-money", "4", "--stated-runway-months", "20"],
            "--stated-runway-months needs --planned-monthly-gross-burn or --current-monthly-gross-burn",
        ),
        (
            ["deal_check", "--investment", "3", "--pre-money", "1", "--fully-diluted-shares", "10"]
            + ["--target-pool-percent", "30"],
            "--target-pool-percent must be below --pre-money / (--pre-money + --investment) = 25.0000%",
        ),
    ],
    ids=[
        "no-valuation",
        "safe-without-shares",
        "second-safe",
        "funds-line",
        "mixed-funds",
        "runway-without-burn",
        "nested-pool",
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert _MODEL_FIELD.findall(caught.value.code.replace("valuation-cap", "")) == []


async def test_a_nested_round_with_no_price_exits_with_the_reason() -> None:
    argv = ["deal_check", "--investment", "4000000", "--pre-money", "1000000", "--fully-diluted-shares", "10000000"]

    with pytest.raises(SystemExit) as caught:
        await run([*argv, "--safe", "900000 discount-percent=20 valuation-cap=1000000"])

    assert caught.value.code == (
        "the SAFEs and notes converting off their cap take the whole pre-money valuation: no positive price"
    )


@pytest.mark.parametrize(
    ("flag", "raw"),
    [("--use-of-funds", "half"), ("--stated-runway-months", "two years"), ("--pool-timing", "later")],
)
async def test_unreadable_arguments_exit_2(flag: str, raw: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["deal_check", "--investment", "1", "--pre-money", "4", flag, raw])

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"argument {flag}:" in capsys.readouterr().err


async def test_xlsx_writes_the_deal_check_sheet(tmp_path: Path) -> None:
    target = tmp_path / "deal.xlsx"
    report = await run([*_COMPANY_A, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    assert load_workbook(target).sheetnames == ["Deal check"]


def test_the_sheet_reads_back_with_formats_live_totals_and_verdict_fills(tmp_path: Path) -> None:
    sheet = sheet_for(deal_check(**DEAL_C))
    target = tmp_path / "deal.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)["Deal check"]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}

    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[1][:3]] == ["Line", "This ask", "How it is computed"]
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key
    assert page[f"B{rows['runway_planned_net']}"].number_format == '0.00" months"'

    for key in ("split_total", "funds_total"):
        line = next(item for item in sheet.lines if item.key == key)
        first, last = rows[line.total_of[_FIRST]], rows[line.total_of[-1]]
        assert last - first == len(line.total_of) - 1
        assert page[f"B{rows[key]}"].value == f"=SUM(B{first}:B{last})"
        parts = sum(Fraction(Decimal(str(page[f"B{row}"].value))) for row in range(first, last + 1))
        total = line.values[_FIRST]
        assert isinstance(total, EquityQuantity)
        last_place = Fraction(Decimal(1).scaleb(-DISPLAY_PLACES[total.unit]))
        assert abs(parts - total.exact) <= len(line.total_of) * _HALF * last_place

    verdicts = {f"B{rows[line.key]}" for line in sheet.lines if line.verdict}
    fills: dict[str, dict[str, str]] = {}
    for cells in page.conditional_formatting:
        for rule in cells.rules:
            assert rule.dxf is not None and rule.dxf.fill is not None
            fills.setdefault(str(cells.sqref), {})[rule.formula[_FIRST]] = str(rule.dxf.fill.start_color.rgb)
    assert set(fills) == verdicts
    for coloured in fills.values():
        assert set(coloured) == {f'"{verdict}"' for verdict in VERDICT_FILLS}
        for verdict, colour in _VERDICT_COLOURS.items():
            assert coloured[f'"{verdict}"'].endswith(colour), verdict
    assert page[f"B{rows['verdict']}"].value == "mismatch"


def test_a_deck_with_nothing_to_check_says_so() -> None:
    sheet = sheet_for(deal_check(investment="3000000", pre_money="12000000"))
    lines = {line.key: line for line in sheet.lines}

    assert lines["verdict"].values == ("not_checked",)
    assert not any(key.startswith("check_") for key in lines)
    assert "tolerance_points" not in lines and "runway_band" not in lines


def test_every_flag_has_plain_words() -> None:
    sheet = sheet_for(deal_check(**DEAL_A, dilution_band_percent="10", runway_band_months="30"))
    flags = [line for line in sheet.lines if line.key.startswith("flag_")]

    assert [line.values[_FIRST] for line in flags] == [
        "pool_in_pre_money_lowers_price",
        "runway_below_band",
        "dilution_above_band",
    ]
    assert all(line.how and "_" not in line.how for line in flags)
    assert "under 30 months" in flags[1].how and "more than 10%" in flags[2].how
