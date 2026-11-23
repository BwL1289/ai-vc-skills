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


# A stated burn multiple with no multiple to work: ARR shrinks, so the row is not checked.
_UNCHECKED_MULTIPLE: dict[str, object] = {
    "period_months": 12,
    "starting_recurring": "100000",
    "new_recurring": "24000",
    "churned_recurring": "30000",
    "net_burn": "1800000",
    "stated_burn_multiple": "6.25",
}


@pytest.mark.parametrize(
    ("fields", "overall"),
    [(METRICS_AM, "mismatch"), (METRICS_AN_DECK, "mismatch"), (_UNCHECKED_MULTIPLE, "not_checked")],
    ids=["company-am", "company-an", "multiple-left-unchecked"],
)
def test_the_sheet_reads_back_with_formats_and_verdict_fills(
    tmp_path: Path, fields: dict[str, object], overall: str
) -> None:
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
    assert page[f"B{rows['verdict']}"].value == overall


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
    metrics_check(period_months=1, starting_recurring="100", month_total_revenue="110"),
    metrics_check(period_months=1, starting_recurring="100", churned_recurring="2.1", stated_churn_percent="1.7"),
)


def test_every_flag_has_plain_words() -> None:
    flags = [line for result in _EVERY_FLAG for line in sheet_for(result).lines if line.key.startswith("flag_")]

    assert {line.values[_FIRST] for line in flags} == set(get_args(MetricsFlag))
    assert all(line.how and "_" not in line.how for line in flags)


def test_a_multiple_left_unchecked_prints_none_and_why_the_overall_verdict_cannot_be_consistent() -> None:
    lines = {line.key: line for line in sheet_for(metrics_check(**_UNCHECKED_MULTIPLE)).lines}

    assert lines["check_burn_multiple_computed"].values == ("none",)
    assert "check_burn_multiple_difference" not in lines
    assert "check_burn_multiple_rounding" not in lines
    assert lines["check_burn_multiple_verdict"].values == ("not_checked",)
    assert "cannot be consistent" in lines["check_burn_multiple_verdict"].how
    assert lines["verdict"].values == ("not_checked",)


# Net burn with no burn multiple to work, each beside a stated ARR that checks out: ARR shrinks (12·94k = 1,128,000),
# or there is no net burn (12·120k = 1,440,000).
_NO_MULTIPLE: dict[str, dict[str, object]] = {
    "burn_multiple_not_defined": {
        "new_recurring": "24000",
        "churned_recurring": "30000",
        "net_burn": "1800000",
        "stated_arr": "1128000",
    },
    "no_net_burn": {"new_recurring": "20000", "net_burn": "0", "stated_arr": "1440000"},
}


@pytest.mark.parametrize("flag", list(_NO_MULTIPLE))
def test_a_burn_flag_says_the_verdict_cannot_be_consistent_only_beside_a_stated_multiple(flag: str) -> None:
    """With no multiple stated the flag ends at "no burn multiple", since the overall verdict is consistent; with one
    stated, that multiple is not checked and the verdict is not consistent, as the flag says."""
    parts = {"period_months": 12, "starting_recurring": "100000", **_NO_MULTIPLE[flag]}
    bare = metrics_check(**parts)
    stated = metrics_check(**parts, stated_burn_multiple="1.5")
    bare_words = {line.values[_FIRST]: line.how for line in sheet_for(bare).lines if line.key.startswith("flag_")}
    stated_words = {line.values[_FIRST]: line.how for line in sheet_for(stated).lines if line.key.startswith("flag_")}

    assert bare.verdict == "consistent"
    assert bare_words[flag].endswith("so there is no burn multiple")
    assert stated.verdict == "not_checked"
    assert stated_words[flag].endswith(
        "; a stated multiple is not checked, and the overall verdict cannot be consistent"
    )


def test_no_flag_says_the_verdict_cannot_be_consistent_beside_a_consistent_verdict() -> None:
    parts = [{"period_months": 12, "starting_recurring": "100000", **fields} for fields in _NO_MULTIPLE.values()]
    results = [*_EVERY_FLAG, metrics_check(**_UNCHECKED_MULTIPLE), *(metrics_check(**fields) for fields in parts)]

    for result in results:
        words = " ".join(line.how for line in sheet_for(result).lines if line.key.startswith("flag_"))
        assert result.verdict != "consistent" or "cannot be consistent" not in words


def test_an_unlabelled_churn_below_zero_says_it_was_checked_as_net_revenue_churn_alone() -> None:
    """-3% with logo and gross revenue churn both worked (2% each): only the net revenue row is checked, and the flag
    says so instead of "every basis"; a 3% churn on the same parts is checked on all three."""
    parts = {"period_months": 1, "starting_recurring": "100000", "expansion_recurring": "5000"}
    parts |= {"churned_recurring": "2000", "customers_start": 100, "customers_lost": 2}
    below = {line.key: line for line in sheet_for(metrics_check(**parts, stated_churn_percent="-3")).lines}
    above = {line.key: line for line in sheet_for(metrics_check(**parts, stated_churn_percent="3")).lines}

    assert [key for key in below if key.startswith("check_churn_") and key.endswith("_verdict")] == [
        "check_churn_net_revenue_verdict"
    ]
    assert "below zero it can only be net revenue churn, so it was checked on that alone" in (
        below["flag_churn_basis_unlabelled"].how
    )
    assert "every basis" not in below["flag_churn_basis_unlabelled"].how
    assert "checked on every basis these figures give" in above["flag_churn_basis_unlabelled"].how


async def test_a_zero_typed_with_a_place_keeps_it_through_the_command() -> None:
    """--stated-churn-percent 0.0 against 0.4% is no rounding of it; 0 is (0.4 rounds to 0)."""
    argv = ["metrics_check", "--period-months", "1", "--starting-recurring", "100000", "--churned-recurring", "400"]
    argv += ["--stated-churn-basis", "gross_revenue", "--json", "--stated-churn-percent"]
    one_place = json.loads(await run([*argv, "0.0"]))
    whole = json.loads(await run([*argv, "0"]))

    assert one_place["inputs"]["stated_churn_percent"] == "0.0"
    assert one_place["checks"][_FIRST]["within_rounding"] is False
    assert "consistent_beyond_rounding" in one_place["flags"]
    assert whole["checks"][_FIRST]["within_rounding"] is True


def test_retention_and_revenue_churn_print_primed_letters_once_a_starting_customers_figure_is_given() -> None:
    """The printed formula must give the printed value: with the starting customers' churn (2k) in place of the
    period's 15k, gross retention is (100k - 5k - 2k)/100k = 93%, which only the primed formula describes."""
    parts = {"period_months": 12, "starting_recurring": "100000", "new_recurring": "50000"}
    parts |= {"expansion_recurring": "20000", "contraction_recurring": "5000", "churned_recurring": "15000"}
    plain = {line.key: line for line in sheet_for(metrics_check(**parts, stated_grr_percent="80")).lines}
    cohort = metrics_check(**parts, cohort_churned_recurring="2000", stated_grr_percent="80")
    primed = {line.key: line for line in sheet_for(cohort).lines}

    assert plain["grr"].how == "(S - C - X)/S"
    assert plain["check_grr_computed"].how == "(S - C - X)/S"
    assert primed["grr"].how.startswith("(S - C' - X')/S; E', C', X' the starting customers' own when given")
    assert primed["nrr"].how.startswith("(S + E' - C' - X')/S")
    assert primed["gross_churn"].how.startswith("(C' + X')/S")
    assert primed["net_churn"].how.startswith("(C' + X' - E')/S")
    assert primed["check_grr_computed"].how == primed["grr"].how
    rows = {row.key: row for row in cohort.assumptions}
    assert rows["retention_rule"].setting.startswith("GRR = (S - C' - X')/S")
    # The churn rule's revenue formulas are primed the same way; logo churn has no primes.
    assert rows["churn_rule"].setting == (
        "logo = customers lost / at the start; gross = (C' + X')/S; net = (C' + X' - E')/S (primed: the starting "
        "customers' own)"
    )
    plain_rows = {row.key: row for row in metrics_check(**parts, stated_grr_percent="80").assumptions}
    assert (
        plain_rows["churn_rule"].setting
        == "logo = customers lost / at the start; gross = (C + X)/S; net = (C + X - E)/S"
    )


def test_a_mismatch_a_hair_past_the_tolerance_says_it_is_just_over() -> None:
    """NRR (2.5M - 112,499)/2.5M = 95.50004%: 0.50004 points from the deck's 95, past 0.5 but shown as 0.5000%."""
    close = sheet_for(
        metrics_check(
            period_months=12, starting_recurring="2500000", churned_recurring="112499", stated_nrr_percent="95"
        )
    )
    clear = sheet_for(
        metrics_check(
            period_months=12, starting_recurring="2500000", churned_recurring="112499", stated_nrr_percent="90"
        )
    )
    close_lines = {line.key: line for line in close.lines}
    clear_lines = {line.key: line for line in clear.lines}

    assert close_lines["check_nrr_difference"].values[_FIRST].rounded == Decimal("0.005000")
    assert close_lines["check_nrr_verdict"].values == ("mismatch",)
    assert "just over the tolerance" in close_lines["check_nrr_verdict"].how
    assert "just over" not in clear_lines["check_nrr_verdict"].how


def test_a_verdict_line_names_the_rounding_where_the_row_has_one() -> None:
    """A payback of 12 against 12.40 holds by rounding alone (0.4 months is past 2%), and its verdict line says what
    holds; a money row keeps the tolerance alone, and its line says only that."""
    rounded = sheet_for(
        metrics_check(
            period_months=1,
            starting_recurring="0",
            new_recurring="10",
            sales_marketing_spend="124",
            gross_margin_percent="100",
            stated_cac_payback_months="12",
            stated_arr="120",
        )
    )
    lines = {line.key: line for line in rounded.lines}

    assert lines["check_cac_payback_rounding"].values == ("yes",)
    assert lines["check_cac_payback_verdict"].values == ("consistent",)
    assert lines["check_cac_payback_verdict"].how == "within the tolerance, or rounding to the deck's, is consistent"
    assert lines["check_arr_verdict"].how == "within the tolerance is consistent"
    assert not any(key.startswith("flag_") for key in lines)


def test_each_rounding_line_says_yes_or_no_and_money_has_none() -> None:
    result = metrics_check(
        period_months=1,
        starting_recurring="100000",
        churned_recurring="2100",
        stated_churn_percent="1.7",
        stated_churn_basis="net_revenue",
        stated_arr="1174800",
    )
    lines = {line.key: line for line in sheet_for(result).lines}

    assert lines["check_churn_net_revenue_rounding"].values == ("no",)
    assert lines["check_churn_net_revenue_rounding"].label == 'Churn (net revenue): rounds to the deck\'s "1.7"'
    assert "check_arr_rounding" not in lines


async def test_the_rounding_line_shows_the_figure_as_typed_since_its_places_decide_it() -> None:
    """A payback of 12.40 months: "12" and "12.0" both print as 12.00 months on the deck's line, so the rounding line
    shows what was typed, the only line that tells the consistent report from the mismatch."""
    parts = ["metrics_check", "--period-months", "1", "--starting-recurring", "0", "--new-recurring", "10"]
    parts += ["--sales-marketing-spend", "124", "--gross-margin-percent", "100", "--stated-cac-payback-months"]
    whole = await run([*parts, "12"])
    one_place = await run([*parts, "12.0"])

    assert re.search(r'CAC payback: rounds to the deck\'s "12" +yes', whole)
    assert re.search(r'CAC payback: rounds to the deck\'s "12\.0" +no', one_place)
    assert re.search(r"CAC payback: the deck says +12\.00 months", whole)
    assert re.search(r"CAC payback: the deck says +12\.00 months", one_place)


@pytest.mark.parametrize(
    ("stated", "words"),
    [("1200000", "the latest month's ARR"), ("1176000", "the movement's ending ARR")],
    ids=["the-months", "the-movements"],
)
def test_a_stated_arr_names_the_arr_it_holds_against(stated: str, words: str) -> None:
    """Movement 1.176M and the latest month 1.2M disagree; each is consistent with the deck's own figure, and both the
    basis line and the ARR row's computed line name the one it was checked against."""
    result = metrics_check(
        period_months=12,
        starting_recurring="80000",
        new_recurring="18000",
        month_total_revenue="100000",
        stated_arr=stated,
    )
    lines = {line.key: line for line in sheet_for(result).lines}

    assert lines["arr_basis"].values == (words,)
    assert lines["check_arr_computed"].how == words
    assert lines["check_arr_verdict"].values == ("consistent",)
    assert lines["flag_arr_movement_and_month_disagree"].values == ("arr_movement_and_month_disagree",)


def test_bands_and_tolerances_typed_in_exponent_form_print_as_plain_numbers() -> None:
    result = metrics_check(
        period_months=1,
        starting_recurring="100",
        new_recurring="10",
        churned_recurring="3",
        net_burn="1000",
        stated_arr="1284",
        burn_multiple_band="3E+0",
        net_revenue_churn_band_percent="2E+0",
        tolerance_points="5E-1",
        tolerance_percent="2E+0",
    )
    rows = {row.key: row for row in result.assumptions}
    words = {line.values[_FIRST]: line.how for line in sheet_for(result).lines if line.key.startswith("flag_")}

    assert rows["tolerance"].setting == "0.5 points; 2% relative"
    assert rows["burn_multiple_band"].setting == "3x"
    assert rows["net_revenue_churn_band"].setting == "2% a month"
    assert "at or above 3x" in words["burn_multiple_above_band"]
    assert "above 2%;" in words["net_revenue_churn_above_band"]
    assert "E+" not in str(words) + str([row.setting for row in result.assumptions])


def test_the_flag_words_blame_what_the_parts_show() -> None:
    """NRR with the period's expansion over the starting customers' own: revenue from customers who were not there at
    the start, not new customers by name; a revenue-only payback past the band says the margin only lengthens it."""
    nrr = metrics_check(
        period_months=12,
        starting_recurring="100000",
        expansion_recurring="20000",
        cohort_expansion_recurring="10000",
        churned_recurring="5000",
        stated_nrr_percent="115",
    )
    payback = metrics_check(
        period_months=12,
        starting_recurring="100000",
        new_recurring="10000",
        sales_marketing_spend="300000",
        customer_segment="smb",
    )
    nrr_words = {line.values[_FIRST]: line.how for line in sheet_for(nrr).lines if line.key.startswith("flag_")}
    payback_words = {line.values[_FIRST]: line.how for line in sheet_for(payback).lines if line.key.startswith("flag_")}

    assert "customers who were not there at the start" in nrr_words["stated_nrr_includes_new"]
    assert "on revenue alone is at or above the 12.00 months benchmark" in payback_words["payback_above_band"]
    assert "a margin only lengthens it" in payback_words["payback_above_band"]


async def test_a_negative_net_revenue_churn_reads_from_the_command_line() -> None:
    report = await run(
        [
            "metrics_check",
            "--period-months",
            "1",
            "--starting-recurring",
            "100000",
            "--expansion-recurring",
            "5000",
            "--churned-recurring",
            "2000",
            "--stated-churn-percent",
            "-3",
            "--stated-churn-basis",
            "net_revenue",
        ]
    )

    assert re.search(r"Churn \(net revenue\): the deck says +-3\.0000%", report)
    assert re.search(r"Overall verdict +consistent", report)


async def test_a_negative_churn_with_its_percent_sign_reads_in_the_equals_form(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """argparse reads ``-3%`` as a flag, so a lone one exits 2; ``--stated-churn-percent=-3%`` reads as -3%."""
    parts = ["metrics_check", "--period-months", "1", "--starting-recurring", "100000"]
    parts += ["--expansion-recurring", "5000", "--churned-recurring", "2000", "--stated-churn-basis", "net_revenue"]
    report = await run([*parts, "--stated-churn-percent=-3%"])

    assert re.search(r"Churn \(net revenue\): the deck says +-3\.0000%", report)
    with pytest.raises(SystemExit) as raised:
        await run([*parts, "--stated-churn-percent", "-3%"])
    assert raised.value.code == _ARGPARSE_EXIT
    assert "--stated-churn-percent: expected one argument" in capsys.readouterr().err


def test_the_disagreeing_arr_flag_names_both_figures_and_the_tolerance() -> None:
    result = metrics_check(
        period_months=12,
        starting_recurring="80000",
        new_recurring="18000",
        month_total_revenue="100000",
        stated_arr="1200000",
    )
    words = {line.values[_FIRST]: line.how for line in sheet_for(result).lines if line.key.startswith("flag_")}

    assert "($1,176,000.00)" in words["arr_movement_and_month_disagree"]
    assert "($1,200,000.00)" in words["arr_movement_and_month_disagree"]
    assert "differ by more than 2%" in words["arr_movement_and_month_disagree"]
