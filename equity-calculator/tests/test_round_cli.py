"""``equity-calculator round``: the report, ``--json``, the Convertibles sheet read back, and every refusal.

No DB, no network: ``run`` is awaited in process. The only file written is the workbook, under pytest's temporary
directory. The ``--safe`` and ``--note`` readers on their own, term by term, are ``test_cli_instruments.py``.
"""

from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from equity_calculator.__main__ import run
from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.workbook import FROZEN_PANE, NUMBER_FORMATS, save_workbook
from openpyxl import load_workbook
from tests.support import ROUND_EXAMPLE, ROUND_SAFES, round_

_ROUND = [
    "round",
    "--fully-diluted-shares",
    "10,000,000",
    "--unissued-pool-shares",
    "500000",
    "--pre-money",
    "$16,000,000",
    "--investment",
    "4000000",
    "--target-pool-percent",
    "10%",
]
_TWO_SAFES = ["--safe", "500000 valuation-cap=5000000", "--safe", "1000000 valuation-cap=10000000"]
_ARGPARSE_EXIT = 2
_FIRST = 0
_LAST = -1
_HALF = Fraction(1, 2)
# The two-SAFE round's totals and the lines each adds, written out so a total over the wrong lines fails.
_HOLDERS = ("existing_holders", "safe_1", "safe_2", "option_pool", "investor")
_ROUND_TOTAL_PARTS: dict[str, tuple[str, ...]] = {
    "total_shares": tuple(f"shares_{holder}" for holder in _HOLDERS),
    "total_ownership": tuple(f"ownership_{holder}" for holder in _HOLDERS),
    "post_money": tuple(f"value_{holder}" for holder in _HOLDERS),
}


async def test_round_report_shows_each_conversion_the_price_and_the_cap_table() -> None:
    """The report names each SAFE's prices and basis, the round price, C, and every holder's stake."""
    report = await run([*_ROUND, *_TWO_SAFES])

    assert report.startswith("SAFEs and notes converting in a priced round")
    for line in (
        "SAFE 1: cap price",
        "SAFE 2: converts at",
        "its cap",
        "Company Capitalization (C)",
        "12,500,000",
        "Price per share (p)",
        "$1.166667",
        "Ownership: investor",
        "20.0000%",
        "Post-money (every share at p)",
        "$20,000,000.00",
    ):
        assert line in report
    assert "safe_price_rule" in report and "Source: Y Combinator" in report


async def test_round_json_prints_exact_fractions_for_every_conversion() -> None:
    """--json prints the round result: the exact price 7/6, each conversion's basis, five cap-table rows."""
    printed = json.loads(await run([*_ROUND, *_TWO_SAFES, "--json"]))

    assert printed["scenario"] == "round"
    assert printed["price_per_share"] == {"unit": "price", "exact": "7/6", "rounded": "1.166667"}
    assert printed["post_money"]["exact"] == "20000000"
    assert [row["basis"] for row in printed["conversions"]] == ["cap", "cap"]
    assert [row["holder"] for row in printed["rows"]] == ["existing_holders", "safe", "safe", "option_pool", "investor"]
    assert {"safe_price_rule", "tie_rule", "search"} <= {item["key"] for item in printed["assumptions"]}


async def test_safes_and_notes_keep_the_order_given() -> None:
    """A note given first is instrument 1 and a SAFE after it instrument 2, whatever the flag."""
    report = await run(
        [
            *_ROUND,
            "--note",
            "100000 interest-rate-percent=8 issue-date=2025-01-15 conversion-date=2026-03-01 discount-percent=20",
            "--safe",
            "250000 mfn",
        ]
    )

    assert "Note 1: principal" in report
    assert "Note 1: accrued interest" in report
    assert "SAFE 2: converts at" in report
    assert "SAFE 2: discount price" not in report


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (_ROUND, "--safe/--note: Field required"),
        (
            [*_ROUND, "--safe", "500000"],
            "--safe #1: a SAFE needs valuation-cap or discount-percent",
        ),
        (
            [*_ROUND, "--safe", "500000 valuation-cap=5000000", "--note", "100000 interest-rate-percent=8"],
            "--note #2: give months-outstanding, or issue-date and conversion-date, not both and not neither",
        ),
        (
            [*_ROUND, "--note", "100000 interest-rate-percent=100 months-outstanding=12 valuation-cap=6000000"],
            "--note #1 interest-rate-percent: Input should be less than 100",
        ),
        (
            [*_ROUND, *(["--safe", "6000000 valuation-cap=10000000"] * 2)],
            "the capped SAFEs' purchase-amount / valuation-cap add up to 120.0000%",
        ),
    ],
)
async def test_refused_rounds_exit_naming_the_flag_and_item(argv: list[str], message: str) -> None:
    """A round the model refuses exits with the flag (and which repeated item) named, never a model field."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert "instruments" not in caught.value.code


_NO_PRICE_ROUND = ["round", "--fully-diluted-shares", "10000000", "--pre-money", "1000000", "--investment", "4000000"]


@pytest.mark.parametrize(
    "terms",
    [
        ["--safe", "900000 discount-percent=20 valuation-cap=1000000"],
        # $500k at 50% off takes exactly the $1M pre-money: a zero price, refused the same way.
        ["--pool-timing", "post_money", "--safe", "500000 discount-percent=50"],
    ],
    ids=["more-than-the-pre-money", "exactly-the-pre-money"],
)
async def test_a_round_with_no_price_exits_with_the_reason(terms: list[str]) -> None:
    """Instruments that take the whole pre-money off their caps leave no positive price: a clean exit, no traceback."""
    argv = [*_NO_PRICE_ROUND, *terms]

    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == (
        "the SAFEs and notes converting off their cap take the whole pre-money valuation: no positive price"
    )


@pytest.mark.parametrize(
    ("flag", "raw"),
    [
        ("--safe", "500000 valuation-cap=5000000 colour=red"),
        ("--safe", "500000 valuation-cap=5000000 valuation-cap=6000000"),
        ("--safe", "500000 mfn=yes"),
        ("--safe", ""),
        ("--note", "100000 interest-rate-percent=8 issue-date=2025-02-30 conversion-date=2026-01-01"),
        ("--note", "100000 interest-rate-percent=8 months-outstanding=12 compounding=daily"),
    ],
)
async def test_malformed_terms_exit_2_with_argparse_usage(
    flag: str, raw: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A malformed --safe or --note argument is refused by argparse (exit 2) naming the flag."""
    with pytest.raises(SystemExit) as caught:
        await run([*_ROUND, flag, raw])

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"argument {flag}:" in capsys.readouterr().err


def test_the_convertibles_sheet_reads_back_with_formats_frozen_header_and_live_totals(tmp_path: Path) -> None:
    """The Convertibles sheet: frozen header, each number under its unit's format, totals as =SUM over their lines.

    Money parts add to the rounded total exactly (cents by largest remainder); shares and ownership are each rounded
    alone, so their sum is within half a last place per part of the exact total. No verdict fills on this sheet.
    """
    sheet = sheet_for(round_(**ROUND_EXAMPLE, instruments=ROUND_SAFES))
    target = tmp_path / "round.xlsx"

    save_workbook(target, (sheet,))
    page = load_workbook(target)["Convertibles"]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}
    lines = {line.key: line for line in sheet.lines}

    assert page.freeze_panes == FROZEN_PANE
    assert [cell.value for cell in page[1][:3]] == ["Line", "This round", "How it is computed"]
    assert len(page.conditional_formatting) == 0
    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
        else:
            assert cell.value == value, line.key

    assert {line.key: line.total_of for line in sheet.lines if line.total_of} == _ROUND_TOTAL_PARTS
    for total, parts in _ROUND_TOTAL_PARTS.items():
        first, last = rows[parts[_FIRST]], rows[parts[_LAST]]
        model_total = lines[total].values[_FIRST]
        assert isinstance(model_total, EquityQuantity)
        read_back = sum(Fraction(Decimal(str(page[f"B{rows[key]}"].value))) for key in parts)

        assert last - first == len(parts) - 1
        assert page[f"B{rows[total]}"].value == f"=SUM(B{first}:B{last})", total
        if model_total.unit == "money":
            assert read_back == Fraction(model_total.rounded), total
        else:
            last_place = Fraction(Decimal(1).scaleb(-DISPLAY_PLACES[model_total.unit]))
            assert abs(read_back - model_total.exact) <= len(parts) * _HALF * last_place, total


async def test_round_xlsx_writes_the_convertibles_sheet(tmp_path: Path) -> None:
    """--xlsx on a round writes one sheet named Convertibles and the report says where."""
    target = tmp_path / "out" / "round.xlsx"

    report = await run([*_ROUND, *_TWO_SAFES, "--xlsx", str(target)])

    assert report.endswith(f"\nWorkbook: {target}")
    assert load_workbook(target).sheetnames == ["Convertibles"]
