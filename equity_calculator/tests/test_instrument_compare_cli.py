"""``equity_calculator instrument_compare``: the report, ``--json``, the Priced vs note sheet read back, refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company BU from ``test_instrument_compare.py`` and, with no next round, Company DX
from ``test_instrument_compare_no_round.py``.
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
from tests.support import COMPARE_BU, COMPARE_DX, instrument_compare

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
# Company DX: no next round, a note with no cap.
_COMPANY_DX = [
    "instrument_compare",
    "--founder-shares",
    "9,000,000",
    "--team-shares",
    "500,000",
    "--unissued-pool-shares",
    "500,000",
    "--investment",
    "$1,500,000",
    "--priced-pre-money",
    "$6,000,000",
    "--priced-preference",
    "standard",
    "--note-discount-percent",
    "20",
    "--note-interest-rate-percent",
    "6",
    "--note-compounding",
    "simple",
    "--note-owed-month",
    "12",
    "--note-owed-month",
    "24",
    "--note-maturity-months",
    "24",
    "--note-maturity-conversion-valuation",
    "$5,000,000",
    "--note-change-of-control-multiple",
    "2",
    "--exit",
    "3,000,000",
    "--exit",
    "10,000,000",
    "--exit",
    "40,000,000",
]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


def _flags(report: str) -> dict[str, str]:
    """Each printed flag's code and its whole line, trailing space dropped."""
    return {line.split()[1]: line.rstrip() for line in report.splitlines() if line.startswith("  Flag ")}


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
        ([*_TODAY, *_EXITS], "no_next_round_given: --note-months-to-conversion is the months until the note"),
        (
            [*_TODAY, *_ROUNDS, *_EXITS, "--note-change-of-control-multiple", "2"],
            "--note-change-of-control-multiple: a term of a note with no next round",
        ),
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


@pytest.mark.parametrize("flag", ["--team-shares", "--unissued-pool-shares"])
async def test_the_team_s_shares_and_the_pool_are_required(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    at = _COMPANY_BU.index(flag)
    with pytest.raises(SystemExit) as caught:
        await run([*_COMPANY_BU[:at], *_COMPANY_BU[at + 2 :]])

    assert caught.value.code == _ARGPARSE_EXIT
    assert re.search(rf"required: {flag}", capsys.readouterr().err)


async def test_existing_terms_left_to_a_default_are_refused_naming_the_flag() -> None:
    for argv, message in (
        (
            [*_COMPANY_BU, "--existing-series", "shares=1000000 invested=3000000"],
            "an existing series in --existing-series gives preference-multiple and participation",
        ),
        (
            [*_COMPANY_BU, "--existing-note", "300000 interest-rate-percent=8 months-outstanding=6"],
            "an existing note in --existing-safe/--existing-note gives compounding (simple, annual or monthly)",
        ),
    ):
        with pytest.raises(SystemExit) as caught:
            await run(argv)
        assert message in str(caught.value.code)


async def test_interest_paid_in_cash_shows_the_principal_converting_and_the_cash_interest() -> None:
    report = await run([*_COMPANY_BU, "--note-interest-paid-in-cash"])

    assert "$2,000,000.00" in _line(report, "Note converting (principal)")
    assert "$100,000.00" in _line(report, "Note interest paid in cash at conversion")
    assert "Note owed when it converts" not in report
    assert _flags(report)["note_interest_paid_in_cash"].endswith(
        "that cash is in no payout line and option A pays none"
    )


async def test_a_discount_only_note_beside_an_mfn_safe_names_no_cap_and_no_safe_interest() -> None:
    """With no cap there is one price, so nothing is "the lower"; a SAFE converts its purchase amount, no interest."""
    argv = [*_TODAY, "--existing-safe", "500000 mfn", *_ROUNDS[:2], "--exit", "20000000"]
    argv.remove("--note-valuation-cap")
    argv.remove("$6,000,000")
    report = await run(argv)

    assert "none" in _line(report, "B: valuation cap (pre-money)")
    converting = _line(report, "Next round 1: existing SAFE 1: amount converting").rstrip()
    assert converting.endswith("the purchase amount") and "interest" not in converting
    safe_price = _line(report, "Next round 1: existing SAFE 1: converts at").rstrip()
    assert "$2.387500" in safe_price and safe_price.endswith(" the round price")
    note_price = _line(report, "Next round 1: B's note: converts at").rstrip()
    assert "$1.910000" in note_price and note_price.endswith(" its discount price")
    flags = _flags(report)
    assert flags["note_converts_at_discount"].endswith(
        "In at least one next round the note converts at its discount price"
    )
    assert "existing_mfn_safe_beside_note" in flags


async def test_a_post_money_pool_is_left_out_of_the_price_text() -> None:
    """Under post-money timing the new pool is added after the round, so the price text leaves it out."""
    post = "pre-money=27000000 investment=6000000 target-pool-percent=15 pool-timing=post_money standard"
    argv = [*_TODAY, "--priced-target-pool-percent", "15", "--priced-pool-timing", "post_money", "--next-round", post]
    report = await run([*argv, *_ROUNDS[2:], "--exit", "20000000"])

    added = "; the new pool is added after the round"
    today = _line(report, "Today: price per share").rstrip()
    assert "$0.800000" in today and today.endswith(f" p = V/(FD + converted){added}")
    first = _line(report, "Next round 1: price per share").rstrip()
    assert first.endswith(f"p = V/(each option's shares + converted){added}")
    second = _line(report, "Next round 2: price per share").rstrip()
    assert second.endswith("p = V/(each option's shares + converted + new pool)")


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
        "shares=1000000 invested=1000000 preference-multiple=1 participation=none",
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


async def test_with_no_next_round_the_report_says_so_and_shows_the_note_at_maturity_and_each_sale() -> None:
    report = await run(_COMPANY_DX)

    assert report.splitlines()[0].startswith("A priced round now (A) beside a convertible note now (B), with no next")
    mode = _line(report, "Mode")
    assert "no next round" in mode and "the note is never converted at a priced round here" in mode
    assert "no next round" in _line(report, "B: months until it converts")
    assert "2x the principal" in _line(report, "B: at a sale before any round")
    assert "B: months to the sales" not in report  # needed only to convert at the cap, and not given
    assert "$1,590,000.00" in _line(report, "Note owed at month 12")
    assert "$1,680,000.00" in _line(report, "At maturity (month 24): note owed")
    assert "$0.500000" in _line(report, "At maturity (month 24): converts at")
    founders = _line(report, "At maturity (month 24): founders")
    assert "72.0000%" in founders and "67.3653%" in founders and "-4.6347%" in founders
    assert "$3,000,000.00" in _line(report, "At a sale: note's claim")
    sale = _line(report, "Sale before any round, $3,000,000.00: founders")
    assert "$1,350,000.00" in sale and "$0.00" in sale and "$-1,350,000.00" in sale
    forty = _line(report, "Sale before any round, $40,000,000.00: founders")
    assert "$28,800,000.00" in forty and "$33,300,000.00" in forty and "$4,500,000.00" in forty
    assert "Note owed when it converts" not in report and "Next round" not in report
    flags = _flags(report)
    assert list(flags)[0] == "no_next_round_given"
    assert flags["discount_unused_without_round"].endswith("it changes no figure here")


async def test_with_a_next_round_the_report_shows_what_the_note_owes_at_each_month_named() -> None:
    report = await run([*_COMPANY_BU, "--note-owed-month", "18"])

    assert "$2,150,000.00" in _line(report, "Note owed at month 18")
    assert "next round" in _line(report, "Mode")


async def test_the_no_next_round_report_never_picks_an_option() -> None:
    for argv in (_COMPANY_DX, [*_TODAY[:-2], *_EXITS]):
        lines = (await run(argv)).lower().split("\nassumptions:\n")[0]
        for word in ("better", "worse", "recommend", "should", "choose", "pick", "we suggest"):
            assert re.search(rf"\b{word}\b", lines) is None, word


async def test_a_sale_option_b_cannot_be_worked_for_says_why_on_its_row() -> None:
    """No change-of-control term for a capped note: A is paid, B is "not worked", and the reason is on the row."""
    report = await run([*_TODAY[:-2], *_EXITS])

    founders = _line(report, "Sale before any round, $20,000,000.00: founders")
    assert "$12,800,000.00" in founders and "not worked" in founders
    reason = _line(report, "Sale before any round, $20,000,000.00: option B").rstrip()
    assert reason.endswith(
        "option B is not worked at this sale: no change-of-control term was given for the note, and what it is paid "
        "at a sale before any priced round is in its own terms (a multiple of its principal, or conversion at its "
        "cap), so give that term"
    )
    assert _flags(report)["maturity_not_given"].endswith(
        "whether it is repaid or converts are in the note's own terms, not shown here"
    )
    assert "change_of_control_not_given" in _flags(report)


async def test_with_no_next_round_the_command_line_and_the_model_give_the_same_result(tmp_path: Path) -> None:
    printed = json.loads(await run([*_COMPANY_DX, "--json"]))

    assert printed == json.loads(instrument_compare(**COMPARE_DX).model_dump_json())
    assert printed["mode"] == "no_next_round"
    target = tmp_path / "only-round.xlsx"
    await run([*_COMPANY_DX, "--xlsx", str(target)])
    labels = [row[0] for row in load_workbook(target)["Priced vs note"].iter_rows(values_only=True)]
    assert "At maturity (month 24): founders" in labels
    sheet = sheet_for(instrument_compare(**COMPARE_DX))
    assert all(len(line.values) == len(_COLUMNS) for line in sheet.lines)
    assert len({line.key for line in sheet.lines}) == len(sheet.lines)


@pytest.mark.parametrize(
    ("extra", "message"),
    [
        (
            ["--note-change-of-control-at-cap"],
            "give one change-of-control term, --note-change-of-control-multiple or --note-change-of-control-at-cap",
        ),
        (["--note-months-to-conversion", "12"], "no_next_round_given: --note-months-to-conversion"),
        (["--note-owed-month", "12"], "--note-owed-month gives month 12 more than once: give each month once"),
        (
            ["--note-maturity-conversion-price", "0.5"],
            "give --note-maturity-conversion-valuation or --note-maturity-conversion-price, not both",
        ),
    ],
)
async def test_no_next_round_refusals_name_flags(extra: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run([*_COMPANY_DX, *extra])

    assert message in str(caught.value.code)
