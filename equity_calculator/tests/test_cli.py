"""``equity_calculator``: the printed report, ``--json``, ``--xlsx``, and every refusal naming the flag at fault.

No DB, no network: ``run`` is awaited in process and one test runs the real module in a child process. The only
file written is the workbook, under pytest's temporary directory.
"""

from __future__ import annotations

import errno
import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
from equity_calculator.__main__ import main, run
from equity_calculator.schemas.equity import EquityAssumption
from openpyxl import load_workbook
from tests.support import (
    DEAL_A,
    METRICS_AN_DECK,
    POOL_EXAMPLE,
    RUNWAY_Y,
    deal_check,
    employee,
    investor,
    metrics_check,
    pool,
    runway_plan,
)

_INVESTOR = ["investor", "--equity-percent", "7", "--outcome-multiplier", "1.10"]
# Company A's deck (tests.support.DEAL_A) as flags: a pool in the pre-money and a runway claim.
_DEAL_A = [
    "deal_check",
    "--investment",
    "3000000",
    "--pre-money",
    "12000000",
    "--stated-investor-percent",
    "20",
    "--fully-diluted-shares",
    "8000000",
    "--target-pool-percent",
    "10",
    "--pool-timing",
    "pre_money",
    "--holder-percent",
    "100",
    "--cash-on-hand",
    "400000",
    "--planned-monthly-gross-burn",
    "180000",
    "--stated-runway-months",
    "24",
]
# Company Y's plan (tests.support.RUNWAY_Y) as flags: two phases, one raise with a runway claim, a milestone.
_RUNWAY_Y = [
    "runway_plan",
    "--cash-on-hand",
    "300000",
    "--phase",
    "from-month=1 gross-burn=90000",
    "--phase",
    "from-month=4 gross-burn=160000 revenue=10000",
    "--raise",
    "amount=1500000 stated-runway-months=24",
    "--milestone",
    "12",
    "--months-to-raise",
    "6",
]
# Company AN's deck (tests.support.METRICS_AN_DECK) as flags: one month's parts, an unlabelled churn and a payback.
_METRICS_AN = [
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
_EMPLOYEE = [
    "employee",
    "--gain-percent",
    "20",
    "--annual-cost",
    "60000",
    "--valuation",
    "2,000,000",
    "--margin-percent",
    "50",
]
_POOL = [
    "pool",
    "--fully-diluted-shares",
    "10,000,000",
    "--unissued-pool-shares",
    "500_000",
    "--pre-money",
    "$8,000,000",
    "--investment",
    "2000000",
    "--target-pool-percent",
    "10%",
]
_CHILD_TIMEOUT_S = 120
_ARGPARSE_EXIT = 2


async def test_investor_report_shows_the_test_and_its_assumptions() -> None:
    """The report carries R, the break-even lines, the verdict and every assumption with its source."""
    report = await run(_INVESTOR)

    assert report.startswith('Investor test (Paul Graham, "The Equity Equation")')
    assert "1.023000x" in report
    assert "1.075269x" in report
    assert "7.5269%" in report
    assert "accept" in report
    assert "Assumptions:" in report
    assert "- break_even_verdict = R = 1 is break even, not accept:" in report


async def test_employee_report_runs_pg_rule_of_thumb() -> None:
    """PG's hire: 16.6667% break even, 4.5000% for the salary, 11.1111% retail, a 6.6111% offer."""
    report = await run(_EMPLOYEE)

    for expected in ("16.6667%", "4.5000%", "11.1111%", "6.6111%", "$90,000.00", "grant"):
        assert expected in report


async def test_pool_report_has_both_timings_and_names_the_deal() -> None:
    """Numbers may carry $, commas, underscores and %; both pool timings print, the deal's column marked."""
    report = await run(_POOL)

    header = report.splitlines()[1]
    assert "Pool in pre-money (this deal)" in header
    assert "Pool in post-money" in header
    assert "$0.736842" in report
    assert "857,142.857" in report
    assert "$7,000,000.00" in report
    assert "10,000,000" in report


@pytest.mark.parametrize(
    ("argv", "assumptions"),
    [
        (_INVESTOR, investor(equity_percent="7", outcome_multiplier="1.10").assumptions),
        (
            _EMPLOYEE,
            employee(gain_percent="20", annual_cost="60000", valuation="2000000", margin_percent="50").assumptions,
        ),
        (_POOL, pool(**POOL_EXAMPLE).assumptions),
        (_DEAL_A, deal_check(**DEAL_A).assumptions),
        (_RUNWAY_Y, runway_plan(**RUNWAY_Y).assumptions),
        (_METRICS_AN, metrics_check(**METRICS_AN_DECK).assumptions),
    ],
    ids=["investor", "employee", "pool", "deal_check", "runway_plan", "metrics_check"],
)
async def test_every_assumption_prints_with_its_setting_statement_and_source(
    argv: list[str], assumptions: tuple[EquityAssumption, ...]
) -> None:
    """The report's last block is every assumption of the result, one line each, its source named, nothing else."""
    report = await run(argv)

    _, printed = report.split("\nAssumptions:\n")
    expected = [f"  - {item.key} = {item.setting}: {item.statement} Source: {item.source}." for item in assumptions]
    assert assumptions
    assert printed.splitlines() == expected


@pytest.mark.parametrize("growth", [["--growth-percent=-10%"], ["--growth-percent", "-10"]])
async def test_a_negative_growth_percent_prints_a_shrinking_outcome(growth: list[str]) -> None:
    """--growth-percent=-10% (or -10 after a space) is m = 0.9: R = .837 and the verdict is reject."""
    report = await run(["investor", "--equity-percent", "7", *growth])

    assert "0.900000x" in report
    assert "1 + g (g = -10%)" in report
    assert "0.837000x" in report
    assert re.search(r"^\s+Verdict\s+reject\s", report, re.MULTILINE)


async def test_json_prints_the_whole_result_with_exact_fractions() -> None:
    """--json prints the result model: each quantity has its unit, its exact fraction and its display value."""
    printed = json.loads(await run([*_INVESTOR, "--json"]))

    assert printed["scenario"] == "investor"
    assert printed["verdict"] == "accept"
    assert printed["value_ratio"] == {"unit": "multiplier", "exact": "1023/1000", "rounded": "1.023000"}
    assert {item["key"] for item in printed["assumptions"]} == {"outcome_multiplier", "break_even_verdict"}


async def test_xlsx_writes_the_workbook_and_the_report_names_it(tmp_path: Path) -> None:
    """--xlsx writes one formatted sheet (making the folder) and the report's last line says where."""
    target = tmp_path / "out" / "pool.xlsx"

    report = await run([*_POOL, "--xlsx", str(target)])

    assert report.endswith(f"\nWorkbook: {target}")
    assert load_workbook(target).sheetnames == ["Pool"]


async def test_xlsx_with_json_still_writes_the_workbook(tmp_path: Path) -> None:
    """With --json too, the output is the JSON alone and the workbook is still written."""
    target = tmp_path / "investor.xlsx"

    printed = await run([*_INVESTOR, "--json", "--xlsx", str(target)])

    assert json.loads(printed)["verdict"] == "accept"
    assert target.is_file()


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            ["investor", "--equity-percent", "7", "--pre-money", "8", "--investment", "2", "--outcome-multiplier", "2"],
            "give exactly one of --equity-percent, --pre-money with --investment (got 2)",
        ),
        (["investor", "--equity-percent", "7"], "give exactly one of --outcome-multiplier, --growth-percent (got 0)"),
        (["investor", "--equity-percent", "0", "--growth-percent", "5"], "--equity-percent: Input should be greater"),
        (["employee", "--gain-percent", "20", "--valuation", "1"], "give --annual-cost and --valuation together"),
        (
            [*_POOL[:-1], "80"],
            "--target-pool-percent must be below --pre-money / (--pre-money + --investment) = 80.0000%",
        ),
        (
            [*_POOL[:4], "10000000", *_POOL[5:]],
            "--unissued-pool-shares must be below --fully-diluted-shares",
        ),
    ],
)
async def test_refused_inputs_exit_with_the_flag_named(argv: list[str], message: str) -> None:
    """An input the model refuses exits with one line per reason, naming CLI flags rather than model fields."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert "_" not in caught.value.code.split(":")[0]  # never a model field name such as equity_percent


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([*_INVESTOR, "--xlsx", "out.csv"], "must end .xlsx, got 'out.csv'"),
        (["investor", "--equity-percent", "seven", "--outcome-multiplier", "1.1"], "must be a number, got 'seven'"),
        (["investor", "--equity-percent", "abc%", "--outcome-multiplier", "1.1"], "must be a number, got 'abc%'"),
        (["investor", "--equity-percent", "10%%", "--outcome-multiplier", "1.1"], "must be a number, got '10%%'"),
        (["investor", "--equity-percent", "nan", "--outcome-multiplier", "1.1"], "must be a finite number"),
        (["investor", "--equity-percent", "7", "--outcome-multiplier", "inf"], "must be a finite number"),
        ([*_POOL[:2], "1.5", *_POOL[3:]], "must be a whole number of shares, got '1.5'"),
        (["pool", "--pre-money", "8"], "the following arguments are required"),
        (["option"], "invalid choice"),
    ],
)
async def test_bad_arguments_exit_2_with_argparse_usage(
    argv: list[str], message: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A value that is not a number, a share count that is not whole, a non-.xlsx path: argparse refuses (exit 2)."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert message in capsys.readouterr().err


async def test_an_unwritable_workbook_exits_with_a_clean_message(tmp_path: Path) -> None:
    """A path under a file cannot be written: the exit names --xlsx and the path, with no traceback."""
    blocker = tmp_path / "a-file"
    blocker.write_text("not a folder")
    target = blocker / "out.xlsx"

    with pytest.raises(SystemExit) as caught:
        await run([*_INVESTOR, "--xlsx", str(target)])

    assert isinstance(caught.value.code, str)
    assert caught.value.code.startswith(f"--xlsx: cannot write {target} (")


@pytest.mark.parametrize(
    ("error", "reason"),
    [(PermissionError(errno.EACCES, "Permission denied"), "Permission denied"), (OSError(), "OSError")],
    ids=["os-reason", "no-os-reason"],
)
async def test_an_unwritable_workbook_names_the_reason(
    error: OSError, reason: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The exit gives the operating system's reason, or the error's type when the system gave none."""
    target = tmp_path / "out.xlsx"

    def refuse(path: Path, sheets: object) -> None:
        raise error

    monkeypatch.setattr("equity_calculator.__main__.save_workbook", refuse)
    with pytest.raises(SystemExit) as caught:
        await run([*_INVESTOR, "--xlsx", str(target)])

    assert caught.value.code == f"--xlsx: cannot write {target} ({reason})"
    assert not target.exists()


def test_main_writes_the_report_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    """``main`` prints the same report ``run`` returns, followed by a newline."""
    main(_INVESTOR)

    printed = capsys.readouterr().out
    assert printed.endswith("\n")
    assert "Value ratio R" in printed


def _child(argv: list[str]) -> subprocess.CompletedProcess[str]:
    """``equity_calculator`` in a child process that sees the same packages as this test run."""
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    return subprocess.run(
        [sys.executable, "-m", "equity_calculator", *argv],
        capture_output=True,
        text=True,
        env=environment,
        timeout=_CHILD_TIMEOUT_S,
        check=False,
    )


def test_python_dash_m_equity_end_to_end(tmp_path: Path) -> None:
    """The real entry point: exit 0 with the report and a workbook; exit 1 on a refused input, the reason on stderr."""
    target = tmp_path / "pool.xlsx"

    worked = _child([*_POOL, "--xlsx", str(target)])
    refused = _child(["investor", "--equity-percent", "7"])

    assert worked.returncode == 0, worked.stderr
    assert "Option-pool shuffle" in worked.stdout
    assert target.is_file()
    assert refused.returncode == 1
    assert refused.stdout == ""
    assert "give exactly one of --outcome-multiplier, --growth-percent (got 0)" in refused.stderr
