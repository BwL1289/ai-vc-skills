"""``equity_calculator market_sizing``: the report, ``--json``, the Market sizing sheet read back, and refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company AW and AX from ``test_market_sizing.py``.
"""

from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.cli_arguments import market_sizing_arguments
from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_market_sizing import MarketSizingFlag, SegmentField
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from tests.support import MARKET_AW, MARKET_AX, market_sizing

_ARGPARSE_EXIT = 2
_FIRST = 0
_HALF = Fraction(1, 2)
_COMPANY_AW = [
    "market_sizing",
    "--segment",
    "customers=18,000 price=$400 price-period-months=1 serviceable-percent=60% obtainable-customers=900 "
    "customers-today=45",
    "--segment",
    "customers=400 price=300 price-period-months=1 units-per-customer=15 serviceable-percent=50 obtainable-percent=10 "
    "customers-today=2",
    "--top-down",
    "amount=$2,100,000,000 comparable-percent=40",
    "--sensitivity",
    "field=price segment=1 values=$300/$500",
    "--sensitivity",
    "values=600/1,200 segment=1 field=obtainable-customers",
    "--sensitivity",
    "field=obtainable-percent segment=2 values=5%/15",
    "--annual-revenue-today",
    "324000",
    "--som-years",
    "5",
    "--som-target",
    "8,000,000",
    "--stated-tam",
    "120000000",
]
_ONE = ["market_sizing", "--segment", "customers=1000 price=100"]
_VERDICT_COLOURS = {"consistent": "C6EFCE", "mismatch": "FFC7CE", "not_checked": "FFEB9C"}
_MODEL_FIELD = re.compile(r"\b[a-z]+_[a-z_]+\b")


async def test_the_report_shows_the_segments_totals_check_ranges_and_flags() -> None:
    report = await run(_COMPANY_AW)

    assert report.startswith("A market size built bottom-up")
    for text in (
        "Segment 1: annual revenue per customer",
        "$4,800.00",
        "Total TAM",
        "$108,000,000.00",
        "Total SOM customers",
        "TAM: the deck says",
        "Top-down 1: bottom-up as a share of it",
        "12.8571%",
        "Sensitivity 1: segment 1 price at SOM = $8,000,000.00",
        "$640.740741",
        "Sensitivity 3: segment 2 share to win at SOM = $8,000,000.00",
        "34.0741%",
        "som_below_target",
    ):
        assert text in report
    assert re.search(r"Overall verdict +mismatch", report)
    assert "top_down_rule = a top-down figure is a cross-check only" in report


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_AW, "--json"]))

    assert printed == json.loads(market_sizing(**MARKET_AW).model_dump_json())
    assert printed["scenario"] == "market_sizing"
    assert [row["field"] for row in printed["sensitivity"]] == ["price", "obtainable_customers", "obtainable_percent"]


async def test_company_ax_from_flags_matches_the_model() -> None:
    argv = [
        "market_sizing",
        "--segment",
        "customers=4000000 price=1800 price-period-months=12 take-rate-percent=15 serviceable-percent=25 "
        "obtainable-percent=2 customers-today=3000",
        "--segment",
        "customers=2500000 price=1800 price-period-months=12 take-rate-percent=15 serviceable-percent=30 "
        "obtainable-percent=2",
        "--top-down",
        "amount=1100000000",
        "--sensitivity",
        "field=take-rate-percent segment=1 values=10/20",
        "--population",
        "5200000",
        "--stated-tam",
        "11700000000",
        "--json",
    ]

    assert json.loads(await run(argv)) == json.loads(market_sizing(**MARKET_AX).model_dump_json())


@pytest.mark.parametrize(("period", "flagged"), [("", True), (" price-period-months=12", False)])
async def test_a_price_period_left_out_is_flagged_and_marked_on_its_line(period: str, flagged: bool) -> None:
    """Left out, the price is read as a yearly one, the line says so and the flag fires; 12 given is the founder's."""
    argv = ["market_sizing", "--segment", f"customers=1000 price=400{period}"]
    printed = await run([*argv, "--json"])
    report = await run(argv)

    result = json.loads(printed)
    assert ("price_period_defaulted" in result["flags"]) is flagged
    assert result["segments"][0]["price_period_given"] is not flagged
    assert ("not given: read as a yearly price" in report) is flagged


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            ["--segment", "customers=10 price=1 obtainable-customers=11"],
            "--segment #2: obtainable-customers is above the serviceable customers",
        ),
        (["--segment", "customers=10 price=1 take-rate-percent=0"], "--segment #2 take-rate-percent: Input should"),
        (
            ["--sensitivity", "field=price segment=3 values=1"],
            "--sensitivity #1 names segment 3, past the last one given (1)",
        ),
        (
            ["--sensitivity", "field=serviceable-percent segment=1 values=50/120"],
            "--sensitivity #1 value #2 (120): serviceable-percent input should be less than or equal to 100",
        ),
        (
            ["--sensitivity", "field=obtainable-customers segment=1 values=5"],
            "--sensitivity #1: segment 1 gives no obtainable-customers to change",
        ),
        (
            ["--stated-som", "1"],
            "--stated-som needs obtainable-percent or obtainable-customers in every segment",
        ),
        (["--som-years", "21"], "--som-years: Input should be less than or equal to 20"),
        (["--som-months", "241"], "--som-months: Input should be less than or equal to 240"),
        (["--som-years", "1", "--som-months", "30"], "give --som-years or --som-months, not both"),
        (["--top-down", "amount=0"], "--top-down #1 amount: Input should be greater than 0"),
    ],
    ids=[
        "som-above-serviceable",
        "zero-take-rate",
        "row-past-the-last-segment",
        "value-above-100",
        "row-on-a-field-not-given",
        "stated-som-without-a-som",
        "horizon-too-long",
        "months-too-long",
        "horizon-twice",
        "zero-top-down",
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run([*_ONE, *argv])

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert _MODEL_FIELD.findall(caught.value.code) == []


@pytest.mark.parametrize(
    ("flag", "raw"),
    [
        ("--segment", "customers=10 price=1 seats=3"),
        ("--segment", "customers=10 price=1 price=2"),
        ("--segment", "customers=10 price=1 price-period-months=1.5"),
        ("--top-down", "amount=1 compare-to=som"),
        ("--sensitivity", "field=period segment=1 values=1"),
        ("--sensitivity", "field=price segment=first values=1"),
        ("--sensitivity", "field=price segment=1 values=1/"),
        ("--som-years", "2.5"),
    ],
    ids=[
        "unknown-term",
        "term-twice",
        "fractional-period",
        "compare-to-som",
        "unknown-field",
        "segment-not-a-number",
        "empty-value",
        "fractional-years",
    ],
)
async def test_unreadable_arguments_exit_2(flag: str, raw: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run([*_ONE, flag, raw])

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"argument {flag}:" in capsys.readouterr().err


async def test_a_segment_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["market_sizing", "--stated-tam", "1"])

    assert caught.value.code == _ARGPARSE_EXIT
    assert "--segment" in capsys.readouterr().err


async def test_xlsx_writes_the_market_sizing_sheet(tmp_path: Path) -> None:
    target = tmp_path / "market.xlsx"
    report = await run([*_COMPANY_AW, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    assert load_workbook(target).sheetnames == ["Market sizing"]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


async def test_a_segment_with_no_market_count_says_tam_and_sam_are_not_worked(tmp_path: Path) -> None:
    """The report names the gap on the segment, the totals and the top-down rows, and the workbook still saves."""
    target = tmp_path / "no-count.xlsx"
    argv = [
        "market_sizing",
        "--segment",
        "price=50000 price-period-months=12 obtainable-customers=40",
        "--top-down",
        "amount=2000000000",
    ]
    report = await run([*argv, "--xlsx", str(target)])

    assert "not given" in _line(report, "Segment 1: buying customers")
    assert "not worked" in _line(report, "Segment 1: TAM and SAM")
    assert "not worked" in _line(report, "Total TAM and SAM")
    assert "not worked" in _line(report, "Top-down 1: bottom-up comparison")
    assert "  Total TAM  " not in report and "  Segment 1: SAM  " not in report
    equal = await run(["market_sizing", "--segment", "customers=40 price=50000 obtainable-customers=40"])
    assert "not a market count" in _line(equal, "Segment 1: buying customers")
    assert load_workbook(target).sheetnames == ["Market sizing"]


async def test_a_second_line_prints_its_share_and_a_break_even_that_holds_the_other_share() -> None:
    segment = "customers=1000 price=10000 price-period-months=12 take-rate-percent=10 second-line-percent=20"
    argv = ["market_sizing", "--segment", f"{segment} obtainable-customers=100", "--som-target", "400000"]
    report = await run([*argv, "--sensitivity", "field=take-rate-percent segment=1 values=5"])

    assert "20.0000%" in _line(report, "Segment 1: second line (share of the main bill)")
    assert "(take rate + second line)" in _line(report, "Segment 1: annual revenue per customer")
    assert "the other share" in _line(report, "Sensitivity 1: segment 1 take rate at SOM")
    plain = await run(["market_sizing", "--segment", "customers=10 price=1 obtainable-customers=5"])
    assert "second line" not in plain


@pytest.mark.parametrize("fields", [MARKET_AW, MARKET_AX], ids=["company-aw", "company-ax"])
def test_the_sheet_reads_back_with_formats_live_totals_and_verdict_fills(
    tmp_path: Path, fields: dict[str, object]
) -> None:
    sheet = sheet_for(market_sizing(**fields))
    target = tmp_path / "market.xlsx"
    save_workbook(target, (sheet,))
    page = load_workbook(target)["Market sizing"]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}

    assert len(rows) == len(sheet.lines)
    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[1][:3]] == ["Line", "This market", "How it is computed"]
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key

    totals = [line for line in sheet.lines if line.total_of]
    assert {line.key for line in totals} >= {"total_customers", "total_tam", "total_sam", "total_gross_spend"}
    for line in totals:
        cells = [f"B{rows[key]}" for key in line.total_of]
        assert page[f"B{rows[line.key]}"].value == "=SUM(" + ",".join(cells) + ")", line.key
        parts = sum(Fraction(Decimal(str(page[cell].value))) for cell in cells)
        total = line.values[_FIRST]
        assert isinstance(total, EquityQuantity)
        last_place = Fraction(Decimal(1).scaleb(-DISPLAY_PLACES[total.unit]))
        assert abs(parts - total.exact) <= len(cells) * _HALF * last_place, line.key
        assert parts == Fraction(total.rounded), line.key

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


def test_a_count_cell_is_formatted_with_two_places() -> None:
    assert NUMBER_FORMATS["count"] == "#,##0.00"


def test_a_market_with_nothing_stated_says_so() -> None:
    sheet = sheet_for(market_sizing(segments=[{"customers": "10", "price": "1"}]))
    lines = {line.key: line for line in sheet.lines}

    assert lines["verdict"].values == ("not_checked",)
    assert not any(key.startswith(("check_", "tolerance", "total_som")) for key in lines)


# Results that together raise every flag, so each flag's sheet line can be read.
_EVERY_FLAG = (
    market_sizing(**MARKET_AW),
    market_sizing(**MARKET_AX),
    market_sizing(segments=[{"customers": "10", "price": "1"}]),
    market_sizing(segments=[{"customers": "10", "price": "1", "obtainable_customers": "5", "customers_today": "0"}]),
    market_sizing(segments=[{"price": "1", "obtainable_customers": "5"}]),
    market_sizing(segments=[{"customers": "10", "price": "1", "obtainable_customers": "5", "customers_today": "6"}]),
    market_sizing(
        segments=[{"customers": "10", "price": "1", "obtainable_percent": "50"}],
        som_target="11",
        sensitivity=[{"field": "obtainable_percent", "segment": 1, "values": ["40"]}],
    ),
)


def test_every_flag_has_plain_words() -> None:
    flags = [line for result in _EVERY_FLAG for line in sheet_for(result).lines if line.key.startswith("flag_")]

    assert {line.values[_FIRST] for line in flags} == set(get_args(MarketSizingFlag))
    assert all(line.how and "_" not in line.how for line in flags)


def test_the_sensitivity_help_names_every_field_the_tool_varies() -> None:
    """The help listed seven fields after the tool took nine (the second line and the units to win)."""
    parser = argparse.ArgumentParser()
    market_sizing_arguments(parser)
    (action,) = (item for item in parser._actions if "--sensitivity" in item.option_strings)
    named = re.search(r"\(F one of (.*?); K 1", action.help or "")

    assert named is not None
    assert named.group(1).split(", ") == [field.replace("_", "-") for field in get_args(SegmentField)]
