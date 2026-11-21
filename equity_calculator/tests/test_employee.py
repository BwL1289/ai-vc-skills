"""The employee test: n = (i - 1)/i (PG), its inverse, the grant verdicts and PG's rule-of-thumb offer.

Pure arithmetic: no DB, no network. PG's worked hire (paulgraham.com/equity.html): a hacker who adds 20% is worth
"n = (1.2 - 1)/1.2 = .167"; with a 50% "profit", $60k a year "x 1.5 = $90k" and a $2 million valuation, "11.1% - 4.5%
= an offer of 6.6%".
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.equation import break_even_multiplier, break_even_stake
from tests.support import employee

_SEED = 20261118
_CASES = 400


def test_pg_hire_is_worth_one_sixth() -> None:
    """i = 1.2 gives n = 0.2/1.2 = 1/6 exactly (16.6667% at display rounding), and a grant."""
    result = employee(outcome_multiplier="1.2")

    assert result.break_even_stake.exact == Fraction(1, 6)
    assert result.break_even_stake.rounded == Decimal("0.166667")
    assert result.verdict == "grant"
    assert result.rule_of_thumb is None
    assert result.offered_stake is None and result.offer_verdict is None


def test_gain_percent_reads_as_the_same_multiplier() -> None:
    """--gain-percent 20 is i = 1.2."""
    assert employee(gain_percent="20").break_even_stake == employee(outcome_multiplier="1.2").break_even_stake


@pytest.mark.parametrize(("gain_percent", "multiplier"), [("-5", Fraction(19, 20)), ("-20", Fraction(4, 5))])
def test_a_negative_gain_percent_is_a_hire_who_lowers_the_outcome(gain_percent: str, multiplier: Fraction) -> None:
    """--gain-percent -5 is i = 0.95 (never 1.05 or 1): a hire who lowers the outcome is worth no stake, no grant."""
    result = employee(gain_percent=gain_percent)

    assert result.outcome_multiplier.exact == multiplier
    assert result.break_even_stake.exact == 0
    assert result.verdict == "no_grant"


def test_a_salary_exactly_worth_the_stake_offers_zero_and_is_not_flagged() -> None:
    """$60k x 1.5 of a $540k company is 1/6, exactly the hire's worth: offer 0, and the salary does not exceed it."""
    result = employee(gain_percent="20", annual_cost="60000", valuation="540000")

    rule = result.rule_of_thumb
    assert rule is not None
    assert rule.retail_stake.exact == rule.cost_stake.exact == Fraction(1, 6)
    assert rule.offer_stake.exact == 0
    assert rule.salary_exceeds_value is False


def test_pg_rule_of_thumb_offer() -> None:
    """$60k x 1.5 = $90k is 4.5% of $2M; 1/6 less a third is 1/9 (11.1%); the offer is 1/9 - 9/200 = 119/1800."""
    result = employee(gain_percent="20", annual_cost="60000", valuation="2000000", margin_percent="50")

    rule = result.rule_of_thumb
    assert rule is not None
    assert rule.stock_cost.rounded == Decimal("90000.00")
    assert rule.cost_stake.exact == Fraction(9, 200)
    assert rule.retail_stake.exact == Fraction(1, 9)
    assert rule.offer_stake.exact == Fraction(119, 1800)
    assert rule.offer_stake.rounded == Decimal("0.066111")
    assert rule.salary_exceeds_value is False


def test_a_changed_cost_years_prices_the_salary_with_that_many_years() -> None:
    """--cost-years 2: $60k x 2 = $120k is 3/50 (6%) of $2M; 1/6 - 3/50 = 8/75 (10.6667%), never PG's 1.5 years."""
    result = employee(gain_percent="20", annual_cost="60000", valuation="2000000", cost_years="2")

    rule = result.rule_of_thumb
    assert rule is not None
    assert rule.stock_cost.exact == Fraction(120_000)
    assert rule.stock_cost.rounded == Decimal("120000.00")
    assert rule.cost_stake.exact == Fraction(3, 50)
    assert rule.retail_stake.exact == Fraction(1, 6)
    assert rule.offer_stake.exact == Fraction(8, 75)
    assert rule.offer_stake.rounded == Decimal("0.106667")
    assert rule.salary_exceeds_value is False
    assert {item.key: item.setting for item in result.assumptions}["cost_years"] == "2 years"


def test_property_the_stock_cost_is_the_yearly_cost_times_the_years() -> None:
    """On random costs, years and valuations: stock cost = cost x years and its stake = stock cost / valuation."""
    rng = random.Random(_SEED + 2)
    for _ in range(_CASES):
        annual_cost = Decimal(rng.randint(1, 500_000))
        cost_years = Decimal(rng.randint(1, 1_000)) / Decimal(100)
        valuation = Decimal(rng.randint(1, 10**9))
        result = employee(
            gain_percent="20", annual_cost=str(annual_cost), valuation=str(valuation), cost_years=str(cost_years)
        )

        rule = result.rule_of_thumb
        assert rule is not None
        assert rule.stock_cost.exact == Fraction(annual_cost) * Fraction(cost_years)
        assert rule.cost_stake.exact == rule.stock_cost.exact / Fraction(valuation)


def test_rule_of_thumb_lines_are_labelled_as_a_rule_of_thumb() -> None:
    """The rule-of-thumb assumptions say so in their statements, and cost years default to PG's 1.5."""
    result = employee(gain_percent="20", annual_cost="60000", valuation="2000000")

    statements = {item.key: item.statement for item in result.assumptions}
    for key in ("cost_years", "valuation", "margin"):
        assert statements[key].startswith("Rule of thumb:")
    settings = {item.key: item.setting for item in result.assumptions}
    assert settings["cost_years"] == "1.5 years"
    assert settings["margin"] == "0%"


def test_salary_that_costs_more_than_the_stake_offers_zero_and_says_so() -> None:
    """i = 1.05 is worth 1/21 (4.8%); $100k x 1.5 of a $1M company is 15%, so the offer floors at 0, flagged."""
    result = employee(gain_percent="5", annual_cost="100000", valuation="1000000")

    rule = result.rule_of_thumb
    assert rule is not None
    assert result.break_even_stake.exact == Fraction(1, 21)
    assert rule.offer_stake.exact == 0
    assert rule.salary_exceeds_value is True


@pytest.mark.parametrize(
    ("multiplier", "verdict"),
    [("0.8", "no_grant"), ("0.999", "no_grant"), ("1", "break_even"), ("1.0001", "grant")],
)
def test_a_hire_who_adds_nothing_or_less_is_worth_no_stake(multiplier: str, verdict: str) -> None:
    """i < 1 is a verdict (no_grant), not an error; i = 1 is break even; both have a break-even stake of 0."""
    result = employee(outcome_multiplier=multiplier)

    assert result.verdict == verdict
    if verdict == "grant":
        assert result.break_even_stake.exact > 0
    else:
        assert result.break_even_stake.exact == 0


@pytest.mark.parametrize(
    ("offered", "multiplier", "needed", "verdict"),
    [
        ("10", "1.2", Fraction(10, 9), "accept"),  # .9 x 1.2 = 1.08
        ("20", "1.2", Fraction(5, 4), "reject"),  # .8 x 1.2 = .96
        ("50", "2", Fraction(2), "break_even"),  # .5 x 2 = 1
        ("0", "1.2", Fraction(1), "accept"),  # a free hire who adds 20%
    ],
)
def test_an_offered_stake_runs_the_investor_test(offered: str, multiplier: str, needed: Fraction, verdict: str) -> None:
    """Offering o of the company to a hire with i is the investor test: accept when (1 - o)·i > 1, so i > 1/(1 - o)."""
    result = employee(outcome_multiplier=multiplier, offered_percent=offered)

    assert result.required_multiplier is not None
    assert result.required_multiplier.exact == needed
    assert result.offer_verdict == verdict


def test_property_the_inverse_recovers_the_multiplier() -> None:
    """On random i > 1: i = 1/(1 - n) undoes n = (i - 1)/i exactly, and n stays inside (0, 1)."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        hire = Fraction(rng.randint(10_001, 1_000_000), 10_000)
        stake = break_even_stake(hire)

        assert 0 < stake < 1
        assert break_even_multiplier(stake) == hire


def test_property_no_stake_is_negative() -> None:
    """On random hires, gains and losses alike: every stake is between 0 and 1, and a loss never earns a grant."""
    rng = random.Random(_SEED + 1)
    for _ in range(_CASES):
        gain_percent = Decimal(rng.randint(-9_999, 50_000)) / Decimal(100)
        result = employee(
            gain_percent=str(gain_percent),
            annual_cost=str(rng.randint(1, 500_000)),
            valuation=str(rng.randint(1, 10**9)),
            margin_percent=str(rng.randint(0, 200)),
        )

        rule = result.rule_of_thumb
        assert rule is not None
        assert 0 <= result.break_even_stake.exact < 1
        assert rule.offer_stake.exact >= 0
        assert rule.retail_stake.exact >= 0
        assert rule.salary_exceeds_value == (rule.retail_stake.exact < rule.cost_stake.exact)
        if gain_percent < 0:
            assert result.verdict == "no_grant"
            assert result.break_even_stake.exact == 0
