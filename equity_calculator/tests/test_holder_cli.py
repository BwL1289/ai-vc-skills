"""``equity_calculator dilution`` and ``vesting``: the reports, ``--json``, ``--xlsx`` and every refusal.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks, under pytest's temporary
directory. ``parse_round``'s own cases are in ``test_cli_instruments.py``; both sheets read back in
``test_holder_sheets.py``.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from equity_calculator.__main__ import run
from openpyxl import load_workbook

_DILUTION = [
    "dilution",
    "--holder-percent",
    "50",
    "--round",
    "investor-percent=20 pool-percent=10",
    "--round",
    "pre-money=8,000,000 investment=$2,000,000",
]
_VESTING = ["vesting", "--grant-shares", "48,000", "--month", "30", "--strike-price", "0.50", "--common-price", "2"]
_SINGLE = ["--acceleration", "single_trigger", "--acceleration-percent", "50", "--change-of-control-month", "24"]
_ARGPARSE_EXIT = 2


async def test_dilution_report_shows_each_round_and_the_final_stake() -> None:
    """50% through (20%, 10% pool) then $8M + $2M: 35%, then 28%, 22% lost in all, the post-money and value."""
    report = await run(_DILUTION)

    assert report.startswith("One holder's stake through a series of rounds")
    for line in (
        "Round 1: stake after",
        "35.0000%",
        "Round 2: new investors' share (n)",
        "I/(V + I)",
        "Round 2: post-money",
        "$10,000,000.00",
        "$2,800,000.00",
        "Stake lost in all",
        "22.0000%",
        "Final stake",
        "28.0000%",
        "56.0000%",
    ):
        assert line in report
    assert "dilution_rule" in report and "stake_from_amounts" in report and "Source: Paul Graham" in report


async def test_dilution_json_prints_exact_stakes() -> None:
    """--json prints the exact fractions: 7/20 after round 1, 7/25 after round 2, kept 14/25 overall."""
    printed = json.loads(await run([*_DILUTION, "--json"]))

    assert printed["scenario"] == "dilution"
    assert [row["stake_after"]["exact"] for row in printed["rows"]] == ["7/20", "7/25"]
    assert printed["final_stake"] == {"unit": "fraction", "exact": "7/25", "rounded": "0.280000"}
    assert printed["kept_overall"]["exact"] == "14/25"
    assert printed["rows"][1]["post_money"]["exact"] == "10000000"
    assert printed["rows"][0]["post_money"] is None


async def test_vesting_report_shows_the_schedule_the_acceleration_and_the_value() -> None:
    """Month 30 with 50% single trigger at 24: 30,000 on schedule, 12,000 accelerated, $63,000 above the strike."""
    report = await run([*_VESTING, *_SINGLE])

    assert report.startswith("A grant vesting month by month")
    for line in (
        "Month asked about (m)",
        "30 months",
        "single trigger",
        "Vested on schedule",
        "30,000",
        "12,000",
        "42,000",
        "87.5000%",
        "at 24 months",
        "$21,000.00",
        "$63,000.00",
        "in_the_money",
    ):
        assert line in report
    assert "acceleration_order" in report and "Source: Sam Altman" in report


async def test_vesting_json_prints_exact_shares_and_money() -> None:
    """--json prints the vested count, the month it fired and the exact intrinsic value."""
    printed = json.loads(await run([*_VESTING, *_SINGLE, "--json"]))

    assert printed["scenario"] == "vesting"
    assert printed["vested"]["exact"] == "42000"
    assert printed["accelerated"]["exact"] == "12000"
    assert printed["fired_month"] == 24
    assert printed["intrinsic_value"]["exact"] == "63000"
    assert printed["moneyness"] == "in_the_money"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (["dilution", "--holder-percent", "0", "--round", "investor-percent=20"], "--holder-percent: Input should be"),
        (
            ["dilution", "--holder-percent", "50", "--round", "investor-percent=60 pool-percent=40"],
            "--round #1: the new investors and pool-percent together take 100.0000% of the company",
        ),
        (
            [*_DILUTION, "--round", "pre-money=8000000"],
            "--round #3: give pre-money and investment together",
        ),
        (
            ["dilution", "--holder-percent", "50", "--round", "investor-percent=20 pre-money=1 investment=1"],
            "--round #1: give exactly one of investor-percent, pre-money with investment (got 2)",
        ),
        (
            ["dilution", "--holder-percent", "50", "--round", "pool-percent=10"],
            "--round #1: give exactly one of investor-percent, pre-money with investment (got 0)",
        ),
        (
            ["dilution", "--holder-percent", "50", "--round", ""],
            "--round #1: give exactly one of investor-percent, pre-money with investment (got 0)",
        ),
        (
            ["dilution", "--holder-percent", "50", *(["--round", "investor-percent=1"] * 21)],
            "--round: Tuple should have at most 20 items",
        ),
        (["vesting", "--grant-shares", "48000", "--month", "30", "--cliff-months", "60"], "--cliff-months must be"),
        (["vesting", "--grant-shares", "48000", "--month", "30", "--common-price", "2"], "give --strike-price with"),
        (
            ["vesting", "--grant-shares", "48000", "--month", "30", "--acceleration", "single_trigger"],
            "--acceleration single_trigger needs --acceleration-percent and --change-of-control-month",
        ),
        (
            ["vesting", "--grant-shares", "48000", "--month", "30", "--acceleration-percent", "50"],
            "--acceleration-percent and --change-of-control-month go with --acceleration single_trigger or",
        ),
        (
            ["vesting", "--grant-shares", "48000", "--month", "601"],
            "--month: Input should be less than or equal to 600",
        ),
        (["vesting", "--grant-shares", "48000", "--month", "1", "--total-months", "0"], "--total-months: Input"),
        (["vesting", "--grant-shares", "0", "--month", "30"], "--grant-shares: Input should be greater than 0"),
    ],
)
async def test_refused_inputs_exit_naming_the_flag_and_item(argv: list[str], message: str) -> None:
    """An input the model refuses exits with the flag (and which repeated --round) named, never a model field."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert isinstance(caught.value.code, str)
    assert message in caught.value.code
    assert not re.search(r"\b(rounds|investor_percent|pool_percent|grant_shares|strike_price)\b", caught.value.code)


@pytest.mark.parametrize(
    ("argv", "flag"),
    [
        (["dilution", "--holder-percent", "50"], "--round"),
        (["dilution", "--holder-percent", "50", "--round", "investor-percent=20 colour=red"], "--round"),
        (["dilution", "--holder-percent", "50", "--round", "investor-percent=20 investor-percent=30"], "--round"),
        (["dilution", "--holder-percent", "50", "--round", "8000000"], "--round"),
        (["vesting", "--grant-shares", "48000", "--month", "12.5"], "--month"),
        (["vesting", "--grant-shares", "48000", "--month", "30", "--acceleration", "triple"], "--acceleration"),
        (["vesting", "--grant-shares", "4.5", "--month", "30"], "--grant-shares"),
        (["vesting", "--month", "30"], "--grant-shares"),
    ],
)
async def test_malformed_arguments_exit_2_with_argparse_usage(
    argv: list[str], flag: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A missing or malformed flag is refused by argparse (exit 2) naming the flag."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert flag in capsys.readouterr().err


@pytest.mark.parametrize(("argv", "title"), [(_DILUTION, "Dilution"), ([*_VESTING, *_SINGLE], "Vesting")])
async def test_xlsx_writes_the_scenarios_sheet(argv: list[str], title: str, tmp_path: Path) -> None:
    """--xlsx writes one sheet named for the scenario and the report says where."""
    target = tmp_path / "out" / f"{title}.xlsx"

    report = await run([*argv, "--xlsx", str(target)])

    assert report.endswith(f"\nWorkbook: {target}")
    assert load_workbook(target).sheetnames == [title]
