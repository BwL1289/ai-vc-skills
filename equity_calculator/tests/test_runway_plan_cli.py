"""``equity_calculator runway_plan``: the report, ``--json``, the sheet read back, and refusals naming flags.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Companies W and Y from ``test_runway_plan.py``.
"""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.layout_runway_plan import option_name
from equity_calculator.rounding import ROUNDING_HOW, ROUNDING_VERDICT_HOW
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag, RunwayPlanInput
from equity_calculator.workbook import NUMBER_FORMATS, VERDICT_FILLS, save_workbook
from openpyxl import load_workbook
from tests.support import RUNWAY_W, RUNWAY_Y, runway_plan
from tests.test_runway_plan import FLAG_CASES

_ARGPARSE_EXIT = 2
_FIRST = 0
_COMPANY_W = [
    "runway_plan",
    "--cash-on-hand",
    "$500,000",
    "--phase",
    "from-month=1 gross-burn=120000 revenue=10000",
    "--phase",
    "from-month=4 gross-burn=220000 revenue=25000",
    "--phase",
    "from-month=13 gross-burn=300000 revenue=60000",
    "--downside-revenue-percent",
    "50%",
    "--raise",
    "amount=3000000",
    "--raise",
    "amount=4000000",
    "--milestone",
    "15",
    "--months-to-raise",
    "6",
]
_COMPANY_Y = [
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
_FLAT = ["runway_plan", "--cash-on-hand", "300000", "--phase", "from-month=1 gross-burn=100000"]
# Company Y's raise with a 60/40 use of funds in percents.
_Y_WITH_FUNDS: dict[str, object] = {
    **RUNWAY_Y,
    "raises": [
        {"amount": "1500000", "stated_runway_months": "24", "use_of_funds": [{"percent": "60"}, {"percent": "40"}]}
    ],
}


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    """Company W from flags is the same input, and so the same result, as Company W from the model's fields."""
    printed = json.loads(await run([*_COMPANY_W, "--json"]))

    assert printed == json.loads(runway_plan(**RUNWAY_W).model_dump_json())
    assert RunwayPlanInput.model_validate(printed["inputs"]) == RunwayPlanInput.model_validate(RUNWAY_W)


async def test_the_report_shows_runway_milestones_required_raises_and_the_check() -> None:
    report = (await run(_COMPANY_Y)).splitlines()

    for line in [
        "  Runway, plan, no raise                                            3.20 months  "
        "months until cash less the floor goes below zero",
        "  Milestone 1 (month 12), plan, raise 1: verdict                          short  "
        "covered when the runway reaches month 18",
        "  Required raise, milestone 1, plan, landing month 0              $2,220,000.00  "
        "smallest raise keeping cash at or above the floor to month 18 (rounded up to the cent)",
        "  Runway, raise 1: difference                                     -10.80 months  computed - stated",
        "  Overall verdict                                                      mismatch  "
        "mismatch if any check is; consistent if all are; not_checked with none",
    ]:
        assert line in report


async def test_a_downside_a_lean_case_a_late_raise_and_funds_lines_come_from_their_flags() -> None:
    printed = json.loads(
        await run(
            [
                *_FLAT,
                "--phase",
                "from-month=4 gross-burn=150000 revenue=20000",
                "--downside-phase",
                "from-month=1 gross-burn=120000",
                "--lean-gross-burn-percent",
                "80",
                "--raise",
                "amount=2000000",
                "--raise",
                "amount=3000000 lands-month=2 stated-runway-months=18 stated-runway-from=landing",
                "--raise-use-of-funds",
                "2 1800000",
                "--raise-use-of-funds",
                "2 1,200,000",
                "--stated-runway-months",
                "3",
                "--cash-floor",
                "50000",
                "--json",
            ]
        )
    )
    inputs = printed["inputs"]

    assert [case["name"] for case in inputs["cases"]] == ["plan", "downside", "lean"]
    # A revenue left out echoes as null, not 0, so a result read back from JSON still knows it was not given.
    assert inputs["cases"][1]["phases"] == [
        {"from_month": 1, "gross_burn": "120000", "revenue": None, "revenue_run_rate": None}
    ]
    assert inputs["cases"][2]["gross_burn_percent_of_plan"] == "80"
    assert inputs["raises"][0]["use_of_funds"] == []
    assert inputs["raises"][1]["use_of_funds"] == [
        {"amount": "1800000", "percent": None},
        {"amount": "1200000", "percent": None},
    ]
    assert inputs["raises"][1]["stated_runway_from"] == "landing"
    assert inputs["stated_runway_months"] == "3"
    assert [(check["key"], check["option"]) for check in printed["checks"]] == [
        ("runway_months", 0),
        ("runway_months", 2),
        ("use_of_funds_total", 2),
    ]


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([*_FLAT, "--phase", "from-month=1 gross-burn=0"], "--phase #2 gross-burn: Input should be greater than 0"),
        (
            ["runway_plan", "--cash-on-hand", "1", "--phase", "from-month=2 gross-burn=1"],
            "--phase: the first phase must start at month 1 (got month 2)",
        ),
        (
            [*_FLAT, "--downside-phase", "from-month=1 gross-burn=1", "--downside-revenue-percent", "50"],
            "--downside-phase/--downside-revenue-percent/--downside-gross-burn-percent: give a case its own phases or "
            "percents of the plan, not both",
        ),
        (
            [*_FLAT, "--lean-revenue-percent", "1001"],
            "--lean-revenue-percent: Input should be less than or equal to 1000",
        ),
        ([*_FLAT, "--raise", "amount=0"], "--raise #1 amount: Input should be greater than 0"),
        (
            [*_FLAT, "--raise", "amount=1", "--raise-use-of-funds", "1 50%", "--raise-use-of-funds", "1 101%"],
            "--raise-use-of-funds #2 percent: Input should be less than or equal to 100",
        ),
        (
            [*_FLAT, "--raise", "amount=1", "--raise-use-of-funds", "1 50%", "--raise-use-of-funds", "1 5"],
            "--raise #1: give every use-of-funds line as an amount or every one as a percent, not a mix",
        ),
        (
            [*_FLAT, "--raise-use-of-funds", "2 5"],
            "--raise-use-of-funds #1: there is no --raise #2 (no --raise was given)",
        ),
        ([*_FLAT, "--cash-floor", "300001"], "--cash-floor is above --cash-on-hand"),
        ([*_FLAT, "--milestone", "601"], "--milestone #1: Input should be less than or equal to 600"),
        ([*_FLAT, "--milestone", "6", "--milestone", "6"], "--milestone: each milestone month may appear once"),
        (
            [*_FLAT, "--phase", "from-month=2 gross-burn=1 revenue=1 revenue-run-rate=12"],
            "--phase #2: give a phase's revenue a month or its revenue-run-rate (annualised), not both",
        ),
        (
            [*_FLAT, "--milestone", "6", "--milestone-type", "self_funding", "--months-to-raise", "3"],
            "a self-funding --milestone-type assumes no next round: leave --months-to-raise out",
        ),
        ([*_FLAT, "--milestone-type", "self_funding"], "a self-funding --milestone-type needs at least one milestone"),
    ],
    ids=[
        "phase-term",
        "first-month",
        "phases-and-percent",
        "case-percent",
        "raise-term",
        "funds-line",
        "funds-mix",
        "no-such-raise",
        "floor",
        "milestone-bound",
        "milestone-twice",
        "revenue-twice",
        "self-funding-months-to-raise",
        "self-funding-no-milestone",
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    printed = str(caught.value.code)
    assert message in printed
    assert "cases" not in printed and "_" not in printed.replace("not_checked", "")


@pytest.mark.parametrize(
    ("flag", "raw", "said"),
    [
        ("--phase", "from-month=1 burn=5", "unknown term 'burn=5'"),
        ("--phase", "from-month=1 from-month=2", "'from-month' is given twice"),
        ("--raise", "amount=1 stated-runway-from=close", "must be one of today, landing"),
        ("--raise-use-of-funds", "first 50%", "starts with the raise's number"),
        ("--raise-use-of-funds", "1", "needs the raise's number and then an amount or a percent"),
        ("--milestone", "12.5", "must be a whole number of months"),
        ("--milestone-type", "only_round", "invalid choice"),
    ],
)
async def test_unreadable_arguments_exit_2(flag: str, raw: str, said: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run([*_FLAT, flag, raw])

    assert caught.value.code == _ARGPARSE_EXIT
    assert said in capsys.readouterr().err


async def test_xlsx_writes_the_runway_plan_sheet(tmp_path: Path) -> None:
    target = tmp_path / "runway.xlsx"
    report = await run([*_COMPANY_W, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    assert load_workbook(target).sheetnames == ["Runway plan"]


def test_the_sheet_reads_back_with_formats_live_totals_and_verdict_fills(tmp_path: Path) -> None:
    """Every number under its unit's format, the use-of-funds total a live sum, and each verdict cell coloured."""
    sheet = sheet_for(runway_plan(**_Y_WITH_FUNDS))
    target = tmp_path / "runway.xlsx"
    save_workbook(target, [sheet])
    page = load_workbook(target)["Runway plan"]
    rows = {line.key: row for row, line in enumerate(sheet.lines, start=2)}

    for line in sheet.lines:
        value, cell = line.values[_FIRST], page[f"B{rows[line.key]}"]
        if isinstance(value, EquityQuantity):
            assert cell.number_format == NUMBER_FORMATS[value.unit], line.key
            if not line.total_of:
                assert Decimal(str(cell.value)) == value.rounded, line.key
    assert page[f"B{rows['funds_1_total']}"].value == f"=SUM(B{rows['funds_1_1']}:B{rows['funds_1_2']})"
    verdicts = [line.key for line in sheet.lines if line.verdict]
    assert "milestone_1_plan_1_verdict" in verdicts and "verdict" in verdicts
    fills = {str(cells.sqref): cells.rules for cells in page.conditional_formatting}
    for key in verdicts:
        assert {rule.formula[_FIRST] for rule in fills[f"B{rows[key]}"]} == {f'"{word}"' for word in VERDICT_FILLS}
    assert VERDICT_FILLS["covered"] == VERDICT_FILLS["consistent"]
    assert VERDICT_FILLS["short"] == VERDICT_FILLS["mismatch"]


def test_every_flag_has_plain_words() -> None:
    """Each flag's line, on the plan that sets it, explains it in words (no field names); the band's names the band."""
    seen: dict[str, str] = {}
    for flag, (on, _) in FLAG_CASES.items():
        sheet = sheet_for(runway_plan(**{**on, "runway_band_months": "24"}))
        line = next(line for line in sheet.lines if line.key == f"flag_{flag}")
        seen[flag] = line.how

    assert list(seen) == list(get_args(RunwayPlanFlag))
    assert all(words and "_" not in words for words in seen.values())
    assert "under 24 months" in seen["runway_below_band"]


@pytest.mark.parametrize(("months_to_raise", "named"), [(None, False), (0, True)])
def test_the_short_milestone_flag_names_the_months_to_raise_only_when_given(
    months_to_raise: int | None, named: bool
) -> None:
    on, _ = FLAG_CASES["milestone_short_on_plan"]
    sheet = sheet_for(runway_plan(**{**on, "months_to_raise": months_to_raise}))
    words = next(line.how for line in sheet.lines if line.key == "flag_milestone_short_on_plan")

    assert ("with the months to raise" in words) is named


def test_a_runway_stated_from_a_landing_the_cash_misses_says_it_is_not_checked() -> None:
    """The stated line says why there is no check line: on the plan the cash runs out before the money lands."""
    raises = [{"amount": "2400000", "lands_month": 5, "stated_runway_months": "24", "stated_runway_from": "landing"}]
    phases = [{"from_month": 1, "gross_burn": "100000"}, {"from_month": 2, "gross_burn": "100000"}]
    sheet = sheet_for(runway_plan(cash_on_hand="300000", cases=[{"name": "plan", "phases": phases}], raises=raises))
    lines = {line.key: line for line in sheet.lines}

    assert lines["raise_1_stated_runway"].how.endswith("not checked: on the plan the cash runs out before it lands")
    assert not any(key.startswith("check_") for key in lines)
    assert lines["plan_phase_1_gross"].label == "Plan, phase 1 (month 1): gross burn a month"
    assert lines["plan_phase_2_gross"].label == "Plan, phase 2 (month 2 on): gross burn a month"


async def test_a_use_of_funds_line_for_a_raise_not_given_counts_the_raises() -> None:
    argv = [*_FLAT, "--raise", "amount=1", "--raise-use-of-funds", "2 50%"]
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert str(caught.value.code) == "--raise-use-of-funds #1: there is no --raise #2 (only 1 was given)"


async def test_a_run_rate_phase_and_a_self_funding_milestone_come_from_their_flags() -> None:
    """Company RR (made up): a $600,000 run-rate is $50,000 a month, divided by the tool; an only round's milestone
    is checked at its own month, with no months to raise and no flag asking for them."""
    argv = [
        "runway_plan",
        "--cash-on-hand",
        "900000",
        "--phase",
        "from-month=1 gross-burn=100000 revenue-run-rate=600000",
        "--phase",
        "from-month=7 gross-burn=120000 revenue-run-rate=900000",
        "--milestone",
        "12",
        "--milestone-type",
        "self_funding",
    ]
    result = json.loads(await run([*argv, "--json"]))
    report = (await run(argv)).splitlines()
    phases = result["cases"][0]["phases"]

    assert result["inputs"]["cases"][0]["phases"][0]["revenue_run_rate"] == "600000"
    assert [phase["revenue"]["rounded"] for phase in phases] == ["50000.00", "75000.00"]
    assert [phase["revenue_run_rate"]["rounded"] for phase in phases] == ["600000.00", "900000.00"]
    assert result["inputs"]["milestone_type"] == "self_funding"
    assert "no_time_to_raise_given" not in result["flags"]
    assert any(line.endswith("$50,000.00  the run-rate / 12") for line in report)
    assert any("revenue run-rate, a year" in line and line.endswith("$600,000.00  given") for line in report)
    assert any(line.startswith("  Milestones are for") and "self-funding, the only round" in line for line in report)
    # The echoed inputs, revenue 0 beside each run-rate, are taken back as they are and work the same plan.
    again = runway_plan(**result["inputs"]).model_dump(mode="json")
    assert again["runway"] == result["runway"] and again["cases"] == result["cases"]


def test_a_plan_with_nothing_to_check_says_so() -> None:
    lines = {line.key: line for line in sheet_for(runway_plan(**RUNWAY_W)).lines}

    assert lines["verdict"].values == ("not_checked",)
    assert not any(key.startswith("check_") for key in lines)
    assert "tolerance_points" not in lines and "runway_band" in lines


def test_the_options_are_named_no_raise_then_raise_by_number() -> None:
    assert [option_name(option) for option in range(3)] == ["no raise", "raise 1", "raise 2"]


async def test_the_help_lists_the_scenario(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        await run(["--help"])

    assert "runway_plan" in capsys.readouterr().out


@pytest.mark.parametrize(("typed", "rounds", "verdict"), [("12", "yes", "consistent"), ("12.0", "no", "mismatch")])
async def test_the_runway_as_typed_decides_its_rounding_line_through_the_command(
    typed: str, rounds: str, verdict: str
) -> None:
    """$1.24M at $100k a month is 12.40 months: --stated-runway-months 12 is that rounded to no places, 12.0 is not.
    The rounding line shows the figure as typed (the stated line prints both as 12.00 months), and the JSON echo keeps
    the places."""
    argv = ["runway_plan", "--cash-on-hand", "1240000", "--phase", "from-month=1 gross-burn=100000"]
    argv += ["--stated-runway-months", typed]
    lines = {line.split("  ")[1]: line for line in (await run(argv)).splitlines() if line.startswith("  ")}
    answer = json.loads(await run([*argv, "--json"]))

    assert answer["inputs"]["stated_runway_months"] == typed
    assert [(row["key"], row["within_rounding"]) for row in answer["checks"]] == [("runway_months", rounds == "yes")]
    assert lines["Runway, no raise: stated"].split()[-3:] == ["12.00", "months", "given"]
    assert lines[f'Runway, no raise: rounds to the deck\'s "{typed}"'].endswith(f" {rounds}  {ROUNDING_HOW}")
    assert lines["Runway, no raise: verdict"].endswith(f"{verdict}  {ROUNDING_VERDICT_HOW}")


async def test_a_raises_runway_from_landing_takes_the_rounding_line_and_the_use_of_funds_does_not() -> None:
    """$1M at $100k a month, $1.24M landing after 6 months: 16.40 months from landing, so "16" holds as a rounding; the
    use-of-funds total beside it has no rounding line and keeps the tolerance's words."""
    argv = ["runway_plan", "--cash-on-hand", "1000000", "--phase", "from-month=1 gross-burn=100000"]
    argv += ["--raise", "amount=1240000 lands-month=6 stated-runway-months=16 stated-runway-from=landing"]
    argv += ["--raise-use-of-funds", "1 60%", "--raise-use-of-funds", "1 40%"]
    lines = {line.split("  ")[1]: line for line in (await run(argv)).splitlines() if line.startswith("  ")}
    answer = json.loads(await run([*argv, "--json"]))

    assert answer["inputs"]["raises"][0]["stated_runway_months"] == "16"
    assert [(row["key"], row["within_rounding"]) for row in answer["checks"]] == [
        ("runway_months", True),
        ("use_of_funds_total", None),
    ]
    assert lines['Runway, raise 1: rounds to the deck\'s "16"'].endswith(f" yes  {ROUNDING_HOW}")
    assert lines["Runway, raise 1: verdict"].endswith(f"consistent  {ROUNDING_VERDICT_HOW}")
    assert lines["Use of funds total, raise 1: verdict"].endswith("consistent  within the tolerance is consistent")
    assert not any(label.startswith("Use of funds total, raise 1: rounds") for label in lines)


def test_a_runway_held_by_the_tolerance_alone_prints_its_flag_in_words() -> None:
    """12.5 against 12.62 months: within 2%, not 12.6 rounded to one place."""
    on, _ = FLAG_CASES["consistent_beyond_rounding"]
    lines = {line.key: line for line in sheet_for(runway_plan(**on)).lines}

    assert lines["check_runway_months_0_rounding"].values == ("no",)
    assert lines["check_runway_months_0_verdict"].values == ("consistent",)
    assert lines["flag_consistent_beyond_rounding"].how.startswith(
        "A stated runway is consistent only by the tolerance"
    )
