"""``equity_calculator raise_pipeline``: the report, ``--json``, the Raise pipeline sheet read back, ``--commitment``,
``--stage``, the runway flags and refusals.

No DB, no network: ``run`` is awaited in process. The only files written are workbooks under pytest's temporary
directory. The worked values are Company RA from ``test_raise_pipeline.py``.
"""

from __future__ import annotations

import json
import re
from fractions import Fraction
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.cli_instruments import parse_commitment, parse_stage
from equity_calculator.layout import sheet_for
from equity_calculator.schemas.equity_raise_pipeline import RaisePipelineFlag
from equity_calculator.workbook import save_workbook
from openpyxl import load_workbook
from tests.support import RAISE_PIPELINE_RA, raise_pipeline

_ARGPARSE_EXIT = 2
_ROUND = [
    "raise_pipeline",
    "--round-size",
    "$4,000,000",
    "--lead-cheque",
    "2,500,000",
    "--commitment",
    "500000 kind=firm",
    "--commitment",
    "250,000 kind=soft",
    "--commitment",
    "250000 kind=soft",
    "--pro-rata",
    "400000",
]
_FUNNEL = [
    "--stage",
    "Intro asked: investors=40 rate-percent=50",
    "--stage",
    "First meeting: investors=10 rate-percent=30%",
    "--stage",
    "Partner meeting: investors=2 rate-percent=25",
    "--term-sheets-wanted",
    "3",
]
_RUNWAY = [
    "--cash-on-hand",
    "1,200,000",
    "--phase",
    "from-month=1 gross-burn=150000 revenue=30000",
    "--months-to-raise",
    "6",
]
_COMPANY_RA = [*_ROUND, *_FUNNEL, *_RUNWAY]


def _line(report: str, label: str) -> str:
    return next(line for line in report.splitlines() if line.strip().startswith(label))


def _flag_lines(report: str) -> dict[str, str]:
    """Each printed flag's code and its whole line."""
    return {line.split()[1]: line for line in report.splitlines() if line.startswith("  Flag ")}


async def test_the_report_shows_the_allocation_the_funnel_and_the_start_raising_month() -> None:
    report = await run(_COMPANY_RA)

    assert "$600,000.00" in _line(report, "Allocation left")
    assert "$1,000,000.00" in _line(report, "Room after the lead and the firm commitments")
    assert "$500,000.00" in _line(report, "Soft commitments, never counted (S)")
    assert "never counted" in _line(report, "Commitment 2 (soft)")
    assert "3.7500%" in _line(report, "Conversion, first stage to a term sheet")
    assert "2.75" in _line(report, "Expected term sheets from today's funnel (E)")
    assert "not a forecast" in _line(report, "Expected term sheets from today's funnel (E)")
    assert re.search(r"\s80\s", _line(report, "First-stage targets needed, from an empty funnel"))
    assert re.search(r"\s7\s", _line(report, "More first-stage targets needed beyond today's funnel"))
    assert "12" in _line(report, "Stage 3, Partner meeting: needed here for 3 term sheets")
    assert "25.0000%" in _line(report, "Stage 3, Partner meeting: rate to a term sheet")
    assert "the founder's own rate" in _line(report, "Stage 1, Intro asked: rate to the next stage")
    assert "10.00 months" in _line(report, "Runway with no raise (the runway plan's)")
    assert "4.00 months" in _line(report, "Start raising by (the runway plan's)")
    assert "\nAssumptions:\n" in report


async def test_the_report_never_says_whom_to_pitch() -> None:
    lines = (await run(_COMPANY_RA)).lower().split("\nassumptions:\n")[0]

    for word in ("better", "worse", "recommend", "should", "choose", "pick", "best", "fit", "we suggest", "typical"):
        assert re.search(rf"\b{word}\b", lines) is None, word


async def test_every_flag_prints_with_its_plain_words() -> None:
    report = await run(_COMPANY_RA)
    flags = raise_pipeline(**RAISE_PIPELINE_RA).flags

    printed = [line.split()[1] for line in report.splitlines() if line.startswith("  Flag ")]
    assert tuple(printed) == flags
    assert set(flags) <= set(get_args(RaisePipelineFlag))
    assert "fewer than the 3 term sheets wanted" in _flag_lines(report)["funnel_short_of_wanted"]


@pytest.mark.parametrize(
    ("argv", "flag", "words"),
    [
        (
            ["raise_pipeline", "--round-size", "1000", "--lead-cheque", "900", "--commitment", "200 kind=firm"],
            "oversubscribed",
            "alone come to more than the round",
        ),
        (
            ["raise_pipeline", "--round-size", "1000", "--lead-cheque", "900", "--pro-rata", "200"],
            "pro_rata_exceeds_left",
            "larger than the room they leave",
        ),
        (
            ["raise_pipeline", "--round-size", "1000", "--lead-cheque", "900", "--pro-rata", "100"],
            "fully_allocated",
            "take the whole round exactly",
        ),
    ],
    ids=["oversubscribed", "pro-rata", "full"],
)
async def test_an_overfull_or_full_round_says_which(argv: list[str], flag: str, words: str) -> None:
    flags = _flag_lines(await run(argv))

    assert words in flags[flag]
    assert len({"oversubscribed", "pro_rata_exceeds_left", "fully_allocated"} & set(flags)) == 1


async def test_the_command_line_and_the_model_give_the_same_result() -> None:
    printed = json.loads(await run([*_COMPANY_RA, "--json"]))

    assert printed == json.loads(raise_pipeline(**RAISE_PIPELINE_RA).model_dump_json())
    assert Fraction(printed["funnel"]["expected_term_sheets"]["exact"]) == Fraction(11, 4)
    assert Fraction(printed["timing"]["start_raising_by"]["exact"]) == 4


async def test_without_the_funnel_or_the_runway_there_are_no_such_lines() -> None:
    report = await run(_ROUND)

    assert "Stage 1" not in report and "Start raising by" not in report
    assert {"no_funnel_given", "no_runway_given"} <= set(_flag_lines(report))


async def test_a_benchmark_s_source_runs_to_the_end_of_the_stage() -> None:
    stage = "First meeting: investors=10 rate-percent=30 rate-basis=benchmark benchmark-source=A founders' survey, 2025"
    argv = [*_ROUND, "--stage", stage, "--term-sheets-wanted", "1"]
    report = await run(argv)

    assert "a benchmark the founder gave, from: A founders' survey, 2025" in _line(
        report, "Stage 1, First meeting: rate"
    )
    assert "benchmark_rates_given" in _flag_lines(report)


async def test_the_timing_block_shows_the_burn_the_start_month_rests_on() -> None:
    """The cash, the floor and each phase print beside the runway; a revenue or a floor not given says it was read as
    none, while a revenue given as 0 reads as given."""
    report = await run(_COMPANY_RA)

    assert "$1,200,000.00" in _line(report, "Cash on hand")
    assert "not given: read as none" in _line(report, "Cash floor")
    assert "$150,000.00" in _line(report, "Phase 1, from month 1: gross burn a month")
    revenue = _line(report, "Phase 1, from month 1: revenue a month")
    assert "$30,000.00" in revenue and revenue.endswith("given")

    phases = ["--phase", "from-month=1 gross-burn=150000", "--phase", "from-month=4 gross-burn=180000 revenue=0"]
    argv = [*_ROUND, "--cash-on-hand", "1,200,000", "--cash-floor", "100000", *phases, "--months-to-raise", "6"]
    report = await run(argv)

    assert "not given: read as none" in _line(report, "Phase 1, from month 1: revenue a month")
    later = _line(report, "Phase 2, from month 4: revenue a month")
    assert "$0.00" in later and later.endswith("given") and "not given" not in later
    floor = _line(report, "Cash floor")
    assert "$100,000.00" in floor and "not given" not in floor


async def test_the_room_and_the_allocation_left_say_they_are_values_not_live_formulas() -> None:
    """Outside the investor sheet only totals are live, so the two lines worked from the totals say so."""
    report = await run(_COMPANY_RA)

    for label in ("Room after the lead and the firm commitments", "Allocation left"):
        assert _line(report, label).endswith("the value when run, not a live formula"), label
    lines = {line.key: line for line in sheet_for(raise_pipeline(**RAISE_PIPELINE_RA)).lines}
    assert not lines["room_after_lead_and_firm"].formula and not lines["allocation_left"].formula


async def test_xlsx_writes_the_raise_pipeline_sheet(tmp_path: Path) -> None:
    target = tmp_path / "raise_pipeline.xlsx"
    report = await run([*_COMPANY_RA, "--xlsx", str(target)])

    assert report.endswith(f"Workbook: {target}")
    page = load_workbook(target)["Raise pipeline"]
    labels = [row[0] for row in page.iter_rows(values_only=True)]
    assert "Allocation left" in labels
    assert "Stage 2, First meeting: expected here" in labels


def test_the_sheet_has_one_column_and_unique_keys() -> None:
    sheet = sheet_for(raise_pipeline(**RAISE_PIPELINE_RA))

    assert sheet.columns == ("This pipeline",)
    assert all(len(line.values) == 1 for line in sheet.lines)
    assert len({line.key for line in sheet.lines}) == len(sheet.lines)


def test_the_commitment_totals_sum_only_their_own_kind() -> None:
    """The workbook's live totals add the firm lines to F and the soft lines to S, never one into the other."""
    lines = {line.key: line for line in sheet_for(raise_pipeline(**RAISE_PIPELINE_RA)).lines}

    assert lines["firm_total"].total_of == ("commitment_1",)
    assert lines["soft_total"].total_of == ("commitment_2", "commitment_3")
    assert lines["pro_rata_total"].total_of == ("pro_rata_1",)


def test_the_workbook_saves_every_line(tmp_path: Path) -> None:
    target = tmp_path / "raise_pipeline.xlsx"
    sheet = sheet_for(raise_pipeline(**RAISE_PIPELINE_RA))
    save_workbook(target, (sheet,))

    page = load_workbook(target)[sheet.title]
    labels = [row[0] for row in page.iter_rows(values_only=True) if row[0]]
    assert [line.label for line in sheet.lines] == labels[1 : len(sheet.lines) + 1]


def test_the_readers_split_a_stage_and_a_commitment() -> None:
    assert parse_stage(" Partner meeting : investors=2 rate-percent=25%") == {
        "name": "Partner meeting",
        "investors": 2,
        "rate_percent": parse_stage("x: rate-percent=25")["rate_percent"],
    }
    assert parse_commitment("$250,000 kind=soft") == {"amount": parse_commitment("250000")["amount"], "kind": "soft"}


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        (
            [*_ROUND, "--stage", "First meeting: investors=10", "--term-sheets-wanted", "1"],
            "--stage #1: stage_rate_missing",
        ),
        ([*_ROUND, "--commitment", "100"], "--commitment #4: commitment_kind_missing"),
        ([*_ROUND, "--term-sheets-wanted", "2"], "no_funnel_given: --term-sheets-wanted needs the founder's funnel"),
        ([*_ROUND, *_FUNNEL[:2]], "no_term_sheet_count_given: give --term-sheets-wanted"),
        (
            [*_ROUND, "--stage", "A: investors=1 rate-percent=10 rate-basis=benchmark", "--term-sheets-wanted", "1"],
            "--stage #1: benchmark_rate_without_source",
        ),
        ([*_ROUND, "--stage", "=A1: investors=1 rate-percent=10", "--term-sheets-wanted", "1"], "--stage #1 name:"),
        ([*_ROUND, *_RUNWAY[:4]], "no_months_to_raise_given"),
        (
            [*_ROUND, "--cash-on-hand", "100", "--phase", "from-month=2 gross-burn=10", "--months-to-raise", "3"],
            "the first phase must start at month 1 (got month 2)",
        ),
        (
            [*_ROUND, "--phase", "from-month=1 gross-burn=10", "--months-to-raise", "3"],
            "--cash-on-hand: Field required",
        ),
        ([*_ROUND, *_RUNWAY[:2], "--months-to-raise", "3"], "--phase: Field required"),
        (["raise_pipeline", "--round-size", "0"], "--round-size: Input should be greater than 0"),
    ],
)
async def test_refusals_name_flags_never_model_fields(argv: list[str], message: str) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    text = str(caught.value.code)
    assert message in text
    for field in ("term_sheets_wanted", "rate_percent", "round_size", "lead_cheque", "cash_on_hand", "runway_phases"):
        assert field not in text, field


@pytest.mark.parametrize(
    ("argv", "fragment"),
    [
        (
            [*_ROUND, "--stage", "First meeting investors=10 rate-percent=30"],
            "starts with the stage's name and a colon",
        ),
        ([*_ROUND, "--stage", "A: investors=1.5 rate-percent=30"], "must be a whole number"),
        ([*_ROUND, "--stage", "A: investors=1 rate-percent=30 bogus=1"], "unknown term"),
        ([*_ROUND, "--stage", "A: investors=1 rate-basis=guess"], "must be one of own, benchmark"),
        ([*_ROUND, "--commitment", "100 kind=maybe"], "must be one of soft, firm"),
        ([*_ROUND, "--commitment", " "], "starts with the amount in dollars"),
        ([*_ROUND, "--term-sheets-wanted", "two"], "must be a whole number"),
    ],
)
async def test_unreadable_arguments_exit_2(argv: list[str], fragment: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert fragment in capsys.readouterr().err


async def test_the_round_size_is_required(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as caught:
        await run(["raise_pipeline", "--lead-cheque", "100"])

    assert caught.value.code == _ARGPARSE_EXIT
    assert re.search(r"required: .*--round-size", capsys.readouterr().err)
