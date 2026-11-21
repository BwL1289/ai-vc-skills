"""``equity_calculator``: how the command line reads its inputs — grouped numbers, negative percents, cost years.

No DB, no network, no file written: ``run`` is awaited in process and returns the printed report.
"""

from __future__ import annotations

import re

import pytest
from equity_calculator.__main__ import run

_ARGPARSE_EXIT = 2
_GROUPING_REFUSAL = (
    "a comma must separate thousands (1 to 3 digits not starting with 0, then groups of 3, as in 8,000,000), got "
)
_STAKE = ["investor", "--equity-percent", "7"]
_HIRE_COST = ["--annual-cost", "60000", "--valuation", "2000000"]
_POOL = ["pool", "--fully-diluted-shares", "10000000", "--pre-money", "8", "--investment", "2"]


def _line(report: str, label: str) -> str:
    """The value printed on the report line labelled ``label`` (the label, then the value, then how)."""
    found = re.search(rf"^\s+{re.escape(label)}\s+(\S+)\s", report, re.MULTILINE)
    assert found is not None, label
    return found.group(1)


async def test_cost_years_reaches_the_rule_of_thumb_offer() -> None:
    """--cost-years 2 prices the salary at 2 years: $120,000 of stock, a 6% stake and a 10.6667% offer (not 1.5)."""
    report = await run(
        ["employee", "--gain-percent", "20", "--annual-cost", "60000", "--valuation", "2000000", "--cost-years", "2"]
    )

    assert _line(report, "Stock cost in years of salary (× a year)") == "2.000000x"
    assert _line(report, "Stock cost of the salary") == "$120,000.00"
    assert _line(report, "Stake the salary costs") == "6.0000%"
    assert _line(report, "Rule-of-thumb offer") == "10.6667%"
    assert "- cost_years = 2 years:" in report


@pytest.mark.parametrize("gain", [["--gain-percent=-5%"], ["--gain-percent", "-5"]])
async def test_a_negative_gain_percent_prints_a_hire_worth_no_stake(gain: list[str]) -> None:
    """--gain-percent=-5% (or -5 after a space) is i = 0.95: a break-even stake of 0 and the verdict no_grant."""
    report = await run(["employee", *gain])

    assert _line(report, "Hire's outcome multiplier (i)") == "0.950000x"
    assert _line(report, "Break-even stake n") == "0.0000%"
    assert _line(report, "Verdict") == "no_grant"


@pytest.mark.parametrize(
    ("pre_money", "investment"),
    [
        ("$8,000,000.00", "2,000,000"),
        ("8000000", "2_000_000"),
        ("+8,000,000", "2000000."),
        ("８,０００,０００", "２,０００,０００"),
        ("٨,٠٠٠,٠٠٠", "2,000,000"),
    ],
    ids=["dollars-and-cents", "underscores", "plus-sign", "full-width", "arabic-indic"],
)
async def test_commas_between_groups_of_three_digits_are_read_as_thousands(pre_money: str, investment: str) -> None:
    """$, underscores and commas that group thousands are dropped: $8,000,000.00 in for $2,000,000 is n = 20%."""
    report = await run(
        ["investor", "--pre-money", pre_money, "--investment", investment, "--outcome-multiplier", "1.3"]
    )

    assert _line(report, "Pre-money valuation (V)") == "$8,000,000.00"
    assert _line(report, "Equity sold (n)") == "20.0000%"


@pytest.mark.parametrize(("multiplier", "shown"), [("1,250", "1,250.000000x"), ("1,050", "1,050.000000x")])
async def test_a_comma_before_three_digits_is_read_as_thousands_even_in_a_ratio(multiplier: str, shown: str) -> None:
    """1,250 is 1250 and 1,050 is 1050: nothing can tell that comma from a decimal one, so it is always thousands."""
    report = await run([*_STAKE, "--outcome-multiplier", multiplier])

    assert _line(report, "Outcome multiplier (m)") == shown


@pytest.mark.parametrize(
    ("argv", "raw"),
    [
        (["investor", "--equity-percent", "7,5", "--outcome-multiplier", "1.2"], "'7,5'"),
        (["investor", "--equity-percent", "7,5%", "--outcome-multiplier", "1.2"], "'7,5%'"),
        (["investor", "--equity-percent", "7.5", "--outcome-multiplier", "1,2"], "'1,2'"),
        (
            ["investor", "--pre-money", "8,00,000", "--investment", "2,000,000", "--outcome-multiplier", "1.2"],
            "'8,00,000'",
        ),
        (["investor", "--pre-money", ",800", "--investment", "2", "--outcome-multiplier", "1.2"], "',800'"),
        (["investor", "--pre-money", "1,000,", "--investment", "2", "--outcome-multiplier", "1.2"], "'1,000,'"),
        (["investor", "--pre-money", "8000,000", "--investment", "2", "--outcome-multiplier", "1.2"], "'8000,000'"),
        (
            [
                "pool",
                "--fully-diluted-shares",
                "10,0000",
                "--pre-money",
                "8",
                "--investment",
                "2",
                "--target-pool-percent",
                "10",
            ],
            "'10,0000'",
        ),
    ],
    ids=[
        "decimal-comma",
        "decimal-comma-percent",
        "multiplier",
        "lakh-grouping",
        "leading",
        "trailing",
        "long-first-group",
        "shares",
    ],
)
async def test_a_comma_that_does_not_group_thousands_is_refused(
    argv: list[str], raw: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """A comma that does not group thousands (7,5 or 8,00,000) is refused with exit 2, never read as 75 or 800,000."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"{_GROUPING_REFUSAL}{raw}" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("argv", "raw"),
    [
        ([*_STAKE, "--outcome-multiplier", "0,500"], "'0,500'"),
        ([*_STAKE, "--outcome-multiplier", "00,500"], "'00,500'"),
        ([*_STAKE, "--outcome-multiplier", "000,500"], "'000,500'"),
        ([*_STAKE, "--outcome-multiplier", "+0,500"], "'+0,500'"),
        ([*_STAKE, "--outcome-multiplier", "0,500.5"], "'0,500.5'"),
        ([*_STAKE, "--outcome-multiplier", "０,５００"], "'０,５００'"),
        ([*_STAKE, "--outcome-multiplier", "٠,٥٠٠"], "'٠,٥٠٠'"),
        ([*_STAKE, "--growth-percent=-0,500"], "'-0,500'"),
        (["investor", "--pre-money", "$0,500", "--investment", "2", "--outcome-multiplier", "1.2"], "'$0,500'"),
        (["investor", "--equity-percent", "0,500%", "--outcome-multiplier", "1.2"], "'0,500%'"),
        (["investor", "--equity-percent", "0,070", "--outcome-multiplier", "1.2"], "'0,070'"),
        (["employee", "--gain-percent", "0,500"], "'0,500'"),
        (["employee", "--gain-percent", "20", *_HIRE_COST, "--cost-years", "0,125"], "'0,125'"),
        ([*_POOL, "--target-pool-percent", "10", "--unissued-pool-shares", "0,500"], "'0,500'"),
    ],
    ids=[
        "multiplier",
        "two-zeros",
        "three-zeros",
        "plus-sign",
        "with-decimals",
        "full-width-zero",
        "arabic-indic-zero",
        "negative-growth",
        "dollars",
        "percent-sign",
        "stake",
        "gain",
        "cost-years",
        "pool-shares",
    ],
)
async def test_a_comma_after_a_leading_zero_is_refused(
    argv: list[str], raw: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """0,500 is refused with exit 2, never read as 500: a first group led by 0 (in any script) groups no thousands."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"{_GROUPING_REFUSAL}{raw}" in capsys.readouterr().err
