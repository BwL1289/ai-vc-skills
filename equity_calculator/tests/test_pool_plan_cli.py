"""``equity_calculator pool_plan``: the report, ``--json``, the Pool plan sheet read back, ``--hire`` and refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company CP from ``test_pool_plan.py``.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.cli_instruments import parse_hire
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_pool_plan import PoolPlanFlag
from equity_calculator.workbook import save_workbook
from openpyxl import load_workbook
from tests.support import POOL_PLAN_CP, pool_plan

_ARGPARSE_EXIT = 2
_COLUMNS = ("Plan: hires to the next round", "Term sheet: requested pool", "Requested - plan")
_ROUND = [
    "pool_plan",
    "--fully-diluted-shares",
    "10,000,000",
    "--unissued-pool-shares",
    "1,000,000",
    "--pre-money",
    "$16,000,000",
    "--investment",
    "4000000",
    "--requested-pool-percent",
    "15%",
    "--next-round-month",
    "18",
]
_HIRES = [
    "--hire",
    "Founding engineer: start-month=1 grant-shares=400000",
    "--hire",
    "Senior engineer: start-month=4 grant-shares=250000",
    "--hire",
    "Senior engineer: start-month=6 grant-shares=250,000",
    "--hire",
    "Head of sales: start-month=9 grant-shares=350000",
    "--hire",
    "Designer: start-month=12 grant-shares=150000",
    "--hire",
    "VP engineering: start-month=24 grant-shares=500000",
]
_COMPANY_CP = [*_ROUND, "--founder-shares", "7,000,000", *_HIRES]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


def _flag_lines(report: str) -> dict[str, str]:
    """Each printed flag's code and its whole line."""
    return {line.split()[1]: line for line in report.splitlines() if line.startswith("  Flag ")}


async def test_the_report_sets_the_plan_beside_the_requested_pool_with_the_difference() -> None:
    report = await run(_COMPANY_CP)

    header = report.splitlines()[1]
    for column in _COLUMNS:
        assert column in header
    target = _line(report, "Target pool after the round (t)")
    assert "10.7692%" in target and "15.0000%" in target and "4.2308%" in target
    price = _line(report, "Price per share (p)")
    assert "$1.538462" in price and "$1.444444" in price and "$-0.094017" in price
    effective = _line(report, "Effective pre-money")
    assert "$13,846,153.85" in effective and "$13,000,000.00" in effective and "$-846,153.85" in effective
    founders = _line(report, "Ownership: founders")
    assert "53.8462%" in founders and "50.5556%" in founders and "-3.2906%" in founders
    assert "left out: starts after month 18" in _line(report, "Hire 6: VP engineering, from month 24")
    assert "counted: starts by month 18" in _line(report, "Hire 5: Designer, from month 12")
    assert "\nAssumptions:\n" in report


async def test_the_report_never_says_which_pool_to_accept() -> None:
    lines = (await run(_COMPANY_CP)).lower().split("\nassumptions:\n")[0]

    for word in ("better", "worse", "recommend", "should", "choose", "pick", "accept", "reject", "we suggest"):
        assert re.search(rf"\b{word}\b", lines) is None, word


async def test_every_flag_prints_with_its_plain_words() -> None:
    report = await run(_COMPANY_CP)
    flags = pool_plan(**POOL_PLAN_CP).flags

    printed = [line.split()[1] for line in report.splitlines() if line.startswith("  Flag ")]
    assert tuple(printed) == flags
    assert set(flags) <= set(get_args(PoolPlanFlag))
    assert "1 hire starts after month 18 and is left out of the plan" in _line(report, "Flag  ")


@pytest.mark.parametrize(
    ("percent", "flag", "words", "never"),
    [
        ("5", "requested_below_plan", "the plan's grants would run short of it", "already holds the plan's grants"),
        ("16", "requested_above_plan", "the difference column shows what the larger pool does", "adds no shares"),
    ],
)
async def test_a_pool_that_tops_up_or_runs_short_says_so(percent: str, flag: str, words: str, never: str) -> None:
    report = await run([*_COMPANY_CP, "--requested-pool-percent", percent])
    flags = _flag_lines(report)

    assert words in flags[flag] and never not in flags[flag]


@pytest.mark.parametrize(
    ("percent", "flag", "words", "never"),
    [
        ("11", "requested_below_plan", "today's unissued pool already holds the plan's grants", "run short"),
        ("11.5", "requested_above_plan", "already meets it, so it adds no shares and moves no price", "larger pool"),
    ],
)
async def test_when_today_s_pool_holds_the_plan_the_flags_say_nothing_runs_short_or_moves(
    percent: str, flag: str, words: str, never: str
) -> None:
    """With U = 1,500,000 the plan's 1,400,000 shares of grants fit today's pool (t_plan = 14/125, 11.2%), and an 11%
    or 11.5% ask is met by it too: no top-up either way, so neither flag claims a shortfall or a price move."""
    argv = [*_COMPANY_CP, "--unissued-pool-shares", "1,500,000", "--requested-pool-percent", percent]
    report = await run(argv)
    flags = _flag_lines(report)

    assert words in flags[flag] and never not in flags[flag]
    assert "plan_fits_current_pool" in flags and "requested_met_by_current_pool" in flags
    assert "100,000" in _line(report, "Pool left ungranted at the next round")
    # The plan's target is the grants' share with today's pool kept whole, so its line names that formula, not the
    # top-up's.
    target = _line(report, "Target pool after the round (t)")
    assert "11.2000%" in target and "G·V/((V + I)·FD)" in target and "FD - U + G" not in target


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_CP, "--json"]))

    assert printed == json.loads(pool_plan(**POOL_PLAN_CP).model_dump_json())
    assert Fraction(printed["plan"]["target_pool"]["exact"]) == Fraction(7, 65)
    assert Fraction(printed["requested_minus_plan"]["effective_pre_money"]["exact"]) == Fraction(-11_000_000, 13)


async def test_without_founder_shares_there_is_no_founders_line() -> None:
    report = await run([*_ROUND, *_HIRES])

    assert "Ownership: founders" not in report
    assert "Founders' shares (F)" not in report
    assert "Ownership: existing holders" in report


async def test_grants_as_percents_read_from_the_hire_terms() -> None:
    """2% + 3% = 5% fits in today's 1,000,000 shares (no top-up, T = 12,500,000): the grants take 625,000 of them."""
    hires = ["--hire", "Engineer: start-month=2 grant-percent=2%", "--hire", "VP sales: start-month=18 grant-percent=3"]
    printed = json.loads(await run([*_ROUND, *hires, "--json"]))

    assert printed["grant_unit"] == "percent"
    assert Fraction(printed["plan"]["target_pool"]["exact"]) == Fraction(1, 20)
    assert Fraction(printed["plan"]["grant_shares"]["exact"]) == 625_000
    assert Fraction(printed["plan"]["pool_left_at_next_round"]["exact"]) == 375_000
    assert "plan_fits_current_pool" in printed["flags"]


async def test_xlsx_writes_the_pool_plan_sheet(tmp_path: Path) -> None:
    target = tmp_path / "pool_plan.xlsx"
    report = await run([*_COMPANY_CP, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    page = load_workbook(target)["Pool plan"]
    labels = [row[0] for row in page.iter_rows(values_only=True)]
    assert "Effective pre-money" in labels
    assert "Hire 1: Founding engineer, from month 1" in labels


def test_the_sheet_has_three_columns_and_a_value_for_each() -> None:
    sheet = sheet_for(pool_plan(**POOL_PLAN_CP))

    assert sheet.columns == _COLUMNS
    assert all(len(line.values) == len(_COLUMNS) for line in sheet.lines)
    assert len({line.key for line in sheet.lines}) == len(sheet.lines)


def test_the_workbook_saves_every_line(tmp_path: Path) -> None:
    target = tmp_path / "pool_plan.xlsx"
    sheet = sheet_for(pool_plan(**POOL_PLAN_CP))
    save_workbook(target, (sheet,))

    page = load_workbook(target)[sheet.title]
    labels = [row[0] for row in page.iter_rows(values_only=True) if row[0]]
    assert [line.label for line in sheet.lines] == labels[1 : len(sheet.lines) + 1]


def test_a_hire_s_role_is_everything_before_the_first_colon() -> None:
    assert parse_hire(" Head of sales (EMEA) : start-month=9 grant-shares=1,000") == {
        "role": "Head of sales (EMEA)",
        "start_month": 9,
        "grant_shares": 1000,
    }


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (_ROUND, "no_hiring_plan_given: the plan's pool is the grants of each hire starting by the next round"),
        (
            [
                *_ROUND,
                "--hire",
                "Engineer: start-month=1 grant-shares=10",
                "--hire",
                "Designer: start-month=2 grant-percent=1",
            ],
            "grants_mixed_units: give every hire's grant as grant-shares, or every one as grant-percent",
        ),
        (
            [*_ROUND, *_HIRES[:2], "--hire", "Engineer: start-month=1 grant-shares=10 grant-percent=1"],
            "--hire #2: give exactly one of grant-shares, grant-percent",
        ),
        ([*_ROUND, "--hire", "=SUM(A1): start-month=1 grant-shares=10"], "--hire #1 role: a hire's role starts with"),
        ([*_ROUND, "--hire", "Engineer: start-month=121 grant-shares=10"], "--hire #1 start-month: Input should be"),
        (
            [*_ROUND, "--hire", "Engineer: start-month=1 grant-percent=90"],
            "must be below --pre-money / (--pre-money + --investment) = 80.0000%",
        ),
        ([*_COMPANY_CP, "--founder-shares", "9,500,000"], "--founder-shares must be at most"),
        ([*_COMPANY_CP, "--requested-pool-percent", "0"], "--requested-pool-percent: Input should be greater than 0"),
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    text = str(caught.value.code)
    assert message in text
    for field in ("hires", "grant_shares", "grant_percent", "start_month", "next_round_month", "founder_shares"):
        assert field not in text, field


@pytest.mark.parametrize(
    ("argv", "fragment"),
    [
        ([*_ROUND, "--hire", "Engineer start-month=1 grant-shares=10"], "starts with the role and a colon"),
        ([*_ROUND, "--hire", "Engineer: start-month=1 bogus=1"], "unknown term"),
        ([*_ROUND, "--hire", "Engineer: start-month=1 start-month=2 grant-shares=1"], "given twice"),
        ([*_ROUND, "--hire", "Engineer: start-month=1.5 grant-shares=1"], "whole number of months"),
        ([*_COMPANY_CP, "--next-round-month", "1.5"], "whole number of months"),
    ],
)
async def test_unreadable_arguments_exit_2(argv: list[str], fragment: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert fragment in capsys.readouterr().err


@pytest.mark.parametrize("flag", ["--unissued-pool-shares", "--requested-pool-percent", "--next-round-month"])
async def test_the_pool_the_ask_and_the_next_round_are_required(flag: str, capsys: pytest.CaptureFixture[str]) -> None:
    at = _COMPANY_CP.index(flag)
    with pytest.raises(SystemExit) as caught:
        await run([*_COMPANY_CP[:at], *_COMPANY_CP[at + 2 :]])

    assert caught.value.code == _ARGPARSE_EXIT
    assert re.search(rf"required: .*{flag}", capsys.readouterr().err)
