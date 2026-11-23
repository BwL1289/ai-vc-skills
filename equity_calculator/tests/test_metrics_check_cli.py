"""``equity_calculator metrics_check``: the report, ``--json``, the Metrics check sheet read back, and refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company AM and AN from ``test_metrics_check.py``.
"""

from __future__ import annotations

import json
import re
from decimal import Decimal
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_metrics_check import MetricsFlag
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from tests.support import METRICS_AM, METRICS_AN_DECK, metrics_check

_ARGPARSE_EXIT = 2
_FIRST = 0
_COMPANY_AM = [
    "metrics_check",
    "--period-months",
    "12",
    "--starting-recurring",
    "$80,000",
    "--new-recurring",
    "24000",
    "--expansion-recurring",
    "6000",
    "--contraction-recurring",
    "2000",
    "--churned-recurring",
    "8000",
    "--month-total-revenue",
    "125000",
    "--month-one-time-revenue",
    "25000",
    "--net-burn",
    "1800000",
    "--stated-arr",
    "1,500,000",
    "--stated-nrr-percent",
    "125%",
    "--stated-burn-multiple",
    "6.25",
]
_COMPANY_AN = [
    "metrics_check",
    "--period-months",
    "1",
    "--starting-recurring",
    "50000",
    "--new-recurring",
    "5000",
    "--expansion-recurring",
    "500",
    "--contraction-recurring",
    "500",
    "--churned-recurring",
    "1000",
    "--customers-start",
    "400",
    "--customers-lost",
    "12",
    "--customers-new",
    "45",
    "--customers-new-paid",
    "20",
    "--sales-marketing-spend",
    "36000",
    "--gross-margin-percent",
    "75",
    "--customer-segment",
    "smb",
    "--stated-churn-percent",
    "2",
    "--stated-cac-payback-months",
    "7.2",
]
_VERDICT_COLOURS = {"consistent": "C6EFCE", "mismatch": "FFC7CE", "not_checked": "FFEB9C"}
_MODEL_FIELD = re.compile(r"\b[a-z]+_[a-z_]+\b")


async def test_the_report_shows_each_check_the_flags_and_the_verdict() -> None:
    report = await run(_COMPANY_AM)

    assert report.startswith("Traction metrics worked from their parts")
    for text in (
        "ARR at the end of the period",
        "$1,200,000.00",
        "Run-rate (12 x the month's revenue)",
        "$1,500,000.00",
        "Net revenue retention (12 months)",
        "95.0000%",
        "Burn multiple on new ARR only",
        "6.250000x",
        "ARR: the deck says",
        "stated_nrr_includes_new",
        "A VC is likely to ask",
    ):
        assert text in report
    assert re.search(r"Overall verdict +mismatch", report)
    assert "burn_multiple_rule = net burn / net new ARR, the same period" in report


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_AN, "--json"]))
    expected = json.loads(metrics_check(**METRICS_AN_DECK).model_dump_json())

    assert printed == expected
    assert printed["scenario"] == "metrics_check"
    assert printed["verdict"] == "mismatch"
    assert [(check["key"], check["basis"]) for check in printed["checks"]] == [
        ("churn", "logo"),
        ("churn", "gross_revenue"),
        ("churn", "net_revenue"),
        ("cac_payback", None),
    ]


async def test_the_dollar_and_percent_spellings_read_as_the_model_fields() -> None:
    printed = json.loads(await run([*_COMPANY_AM, "--json"]))

    assert printed == json.loads(metrics_check(**METRICS_AM).model_dump_json())


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["--new-recurring", "5"], "--new-recurring needs --starting-recurring"),
        (["--customers-start", "1", "--customers-lost", "2"], "--customers-lost is above --customers-start"),
        (
            ["--month-total-revenue", "10", "--month-one-time-revenue", "6", "--month-usage-revenue", "5"],
            "--month-one-time-revenue + --month-usage-revenue is above --month-total-revenue",
        ),
        (["--stated-churn-basis", "logo"], "--stated-churn-basis needs --stated-churn-percent"),
        (["--stated-cac", "1"], "--stated-cac needs --sales-marketing-spend and --customers-new above 0 to check it"),
        (
            ["--stated-churn-percent", "1", "--customers-start", "5"],
            "--stated-churn-percent needs --customers-start above 0 with --customers-lost, or --starting-recurring "
            "above 0, to check it",
        ),
        (["--customers-start=-1"], "--customers-start: Input should be greater than or equal to 0"),
        (["--period-months", "40"], "--period-months: Input should be less than or equal to 36"),
    ],
    ids=[
        "movement-without-start",
        "more-customers-lost",
        "month-parts",
        "basis-without-churn",
        "cac-without-parts",
        "churn-without-a-basis",
        "negative-customers",
        "period-too-long",
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["metrics_check", "--period-months", "1", *argv])

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert _MODEL_FIELD.findall(caught.value.code) == []


@pytest.mark.parametrize(
    ("flag", "raw"),
    [
        ("--customers-start", "1.5"),
        ("--customers-new", "many"),
        ("--recurring-unit", "weekly"),
        ("--stated-churn-basis", "revenue"),
        ("--customer-segment", "startup"),
    ],
)
async def test_unreadable_arguments_exit_2(flag: str, raw: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["metrics_check", "--period-months", "1", flag, raw])

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"argument {flag}:" in capsys.readouterr().err


async def test_the_period_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["metrics_check", "--starting-recurring", "1"])

    assert caught.value.code == _ARGPARSE_EXIT
    assert "--period-months" in capsys.readouterr().err


async def test_xlsx_writes_the_metrics_check_sheet(tmp_path: Path) -> None:
    target = tmp_path / "metrics.xlsx"
    report = await run([*_COMPANY_AM, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    assert load_workbook(target).sheetnames == ["Metrics check"]


@pytest.mark.parametrize("fields", [METRICS_AM, METRICS_AN_DECK], ids=["company-am", "company-an"])
def test_the_sheet_reads_back_with_formats_and_verdict_fills(tmp_path: Path, fields: dict[str, object]) -> None:
    sheet = sheet_for(metrics_check(**fields))
    target = tmp_path / "metrics.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)["Metrics check"]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}

    assert len(rows) == len(sheet.lines)
    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[1][:3]] == ["Line", "These figures", "How it is computed"]
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key

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


def test_the_churn_check_lines_name_their_basis() -> None:
    keys = [line.key for line in sheet_for(metrics_check(**METRICS_AN_DECK)).lines]

    for basis in ("logo", "gross_revenue", "net_revenue"):
        assert f"check_churn_{basis}_verdict" in keys, basis


def test_a_document_with_nothing_to_check_says_so() -> None:
    sheet = sheet_for(metrics_check(period_months=1, starting_recurring="100", new_recurring="10"))
    lines = {line.key: line for line in sheet.lines}

    assert lines["verdict"].values == ("not_checked",)
    assert not any(key.startswith("check_") for key in lines)
    assert not any(key.startswith("tolerance") for key in lines)


# One result per flag, together raising every flag, so each flag's sheet line can be read.
_EVERY_FLAG = (
    metrics_check(**METRICS_AM),
    metrics_check(**METRICS_AN_DECK),
    metrics_check(period_months=1, starting_recurring="100", expansion_recurring="10", churned_recurring="5"),
    metrics_check(period_months=1, sales_marketing_spend="1000", customers_new=10),
    metrics_check(period_months=1, starting_recurring="100", new_recurring="10", sales_marketing_spend="1000"),
    metrics_check(period_months=1, starting_recurring="100", new_recurring="5", churned_recurring="5", net_burn="1"),
    metrics_check(period_months=1, starting_recurring="100", new_recurring="10", net_burn="-1"),
    metrics_check(
        period_months=1,
        starting_recurring="100",
        new_recurring="10",
        sales_marketing_spend="1000",
        gross_margin_percent="50",
        customer_segment="smb",
    ),
    metrics_check(period_months=1, starting_recurring="100", churned_recurring="3"),
)


def test_every_flag_has_plain_words() -> None:
    flags = [line for result in _EVERY_FLAG for line in sheet_for(result).lines if line.key.startswith("flag_")]

    assert {line.values[_FIRST] for line in flags} == set(get_args(MetricsFlag))
    assert all(line.how and "_" not in line.how for line in flags)
