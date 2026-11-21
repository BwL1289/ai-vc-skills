"""The investor test (Paul Graham, "The Equity Equation"): PG's worked examples, the verdict boundary, the holder.

Pure arithmetic: no DB, no network. The expected values are PG's own examples (paulgraham.com/equity.html, July
2007) worked by hand as exact fractions: "the remaining .93 you hold is worth .93 x 1.1 = 1.023", "1/(1 - n) is
1.075", "1/.7 = 1.43".
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction

import pytest
from tests.support import investor

_SEED = 20261118
_CASES = 400


def test_yc_example_accepts_with_the_break_even_lines() -> None:
    """7% for a 10% better outcome: R = .93 x 1.1 = 1.023, m* = 100/93, g* = 7/93, accept."""
    result = investor(equity_percent="7", outcome_multiplier="1.10")

    assert result.verdict == "accept"
    assert result.equity_sold.exact == Fraction(7, 100)
    assert result.value_ratio.exact == Fraction(1023, 1000)
    assert result.value_ratio.rounded == Decimal("1.023000")
    assert result.break_even_multiplier.exact == Fraction(100, 93)
    assert result.break_even_multiplier.rounded == Decimal("1.075269")
    assert result.break_even_growth.exact == Fraction(7, 93)
    assert result.break_even_growth.rounded == Decimal("0.075269")
    assert result.post_money is None
    assert result.holder is None


@pytest.mark.parametrize(
    ("equity_percent", "multiplier", "verdict"),
    [
        ("7", "1.05", "reject"),  # .93 x 1.05 = .9765
        ("50", "2", "break_even"),  # half the company for a doubled outcome: exactly even
        ("30", "1.43", "accept"),  # PG's Sequoia example: .7 x 1.43 = 1.001
        ("30", "1.428", "reject"),  # .7 x 1.428 = .9996
        ("7", "0.9", "reject"),  # a deal that shrinks the outcome
    ],
)
def test_verdict_vectors(equity_percent: str, multiplier: str, verdict: str) -> None:
    """Accept only when R > 1; R exactly 1 is break even; below 1 rejects."""
    result = investor(equity_percent=equity_percent, outcome_multiplier=multiplier)

    assert result.verdict == verdict


def test_break_even_ratio_is_exactly_one() -> None:
    """Selling 50% for m = 2 gives R = 1 exactly, not a rounding of it."""
    result = investor(equity_percent="50", outcome_multiplier="2")

    assert result.value_ratio.exact == 1
    assert result.break_even_multiplier.exact == 2
    assert result.break_even_growth.exact == 1


def test_growth_percent_reads_as_the_same_multiplier() -> None:
    """--growth-percent 10 is m = 1.10: the same result as giving the multiplier."""
    by_growth = investor(equity_percent="7", growth_percent="10")
    by_multiplier = investor(equity_percent="7", outcome_multiplier="1.10")

    assert by_growth.outcome_multiplier == by_multiplier.outcome_multiplier
    assert by_growth.value_ratio == by_multiplier.value_ratio
    assert by_growth.verdict == by_multiplier.verdict


def test_a_negative_growth_percent_shrinks_the_outcome() -> None:
    """--growth-percent -10 is m = 0.9, never 1.1 or 1: R = .93 x .9 = .837, a reject."""
    result = investor(equity_percent="7", growth_percent="-10")

    assert result.outcome_multiplier.exact == Fraction(9, 10)
    assert result.value_ratio.exact == Fraction(837, 1000)
    assert result.value_ratio.rounded == Decimal("0.837000")
    assert result.verdict == "reject"


def test_stake_from_amounts_is_investment_over_post_money() -> None:
    """$2M into an $8M pre-money is n = 2/10 = 20%; the post-money is $10M."""
    result = investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.3")

    assert result.equity_sold.exact == Fraction(1, 5)
    assert result.post_money is not None
    assert result.post_money.rounded == Decimal("10000000.00")
    assert result.value_ratio.exact == Fraction(104, 100)
    assert result.verdict == "accept"
    assert {item.key for item in result.assumptions} >= {"stake_from_amounts"}


def test_holder_stake_and_value_after_the_round() -> None:
    """A 50% holder keeps h(1 - n) = 40%; their value goes from h·V = $4M to h(1 - n)·m·V = $4.16M."""
    result = investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.3", holder_percent="50")

    holder = result.holder
    assert holder is not None
    assert holder.stake_before.exact == Fraction(1, 2)
    assert holder.stake_after.exact == Fraction(2, 5)
    assert holder.value_before is not None and holder.value_after is not None
    assert holder.value_before.rounded == Decimal("4000000.00")
    assert holder.value_after.rounded == Decimal("4160000.00")
    assert "holder_value" in {item.key for item in result.assumptions}


def test_holder_without_amounts_has_stakes_but_no_dollar_values() -> None:
    """With only a percent sold there is no valuation, so the holder's line carries stakes alone."""
    result = investor(equity_percent="7", outcome_multiplier="1.10", holder_percent="10")

    holder = result.holder
    assert holder is not None
    assert holder.stake_after.exact == Fraction(93, 1000)
    assert holder.value_before is None
    assert holder.value_after is None
    assert "holder_value" not in {item.key for item in result.assumptions}


def test_assumptions_name_their_source() -> None:
    """Every assumption carries a statement and a source: PG for the test itself, 'unverified' for the rest."""
    result = investor(pre_money="8000000", investment="2000000", outcome_multiplier="1.3", holder_percent="50")

    sources = {item.key: item.source for item in result.assumptions}
    assert sources["outcome_multiplier"].startswith("Paul Graham")
    assert sources["break_even_verdict"].startswith("Paul Graham")
    assert sources["stake_from_amounts"].startswith("unverified")
    assert sources["holder_value"] == "unverified"
    assert all(item.statement and item.setting for item in result.assumptions)


def _random_case(rng: random.Random) -> tuple[int, int, Decimal, Decimal]:
    """A pre-money, an investment, a multiplier (4 places) and a holder percent (2 places), all positive."""
    pre_money = rng.randint(1, 10**9)
    investment = rng.randint(1, 10**9)
    multiplier = Decimal(rng.randint(1, 40_000)) / Decimal(10_000)
    holder_percent = Decimal(rng.randint(1, 10_000)) / Decimal(100)
    return pre_money, investment, multiplier, holder_percent


def test_property_accept_exactly_when_the_holder_ends_up_richer() -> None:
    """On random rounds: R > 1 iff the holder's value after exceeds their value before; stakes stay in [0, 1]."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        pre_money, investment, multiplier, holder_percent = _random_case(rng)
        result = investor(
            pre_money=str(pre_money),
            investment=str(investment),
            outcome_multiplier=str(multiplier),
            holder_percent=str(holder_percent),
        )

        holder = result.holder
        assert holder is not None and holder.value_before is not None and holder.value_after is not None
        richer = holder.value_after.exact > holder.value_before.exact
        even = holder.value_after.exact == holder.value_before.exact
        assert (result.verdict == "accept") == richer
        assert (result.verdict == "break_even") == even
        assert (result.value_ratio.exact > 1) == richer
        for stake in (result.equity_sold, holder.stake_before, holder.stake_after):
            assert 0 <= stake.exact <= 1


@pytest.mark.parametrize("step", [1, 25, 100, 437])
def test_property_a_fair_cash_only_round_breaks_even(step: int) -> None:
    """m = (V + I)/V exactly offsets n = I/(V + I): the holder's value is unchanged and the verdict is break even."""
    rng = random.Random(_SEED + step)
    pre_money = 100 * rng.randint(1, 10**7)
    investment = pre_money // 100 * step
    multiplier = Decimal(100 + step) / Decimal(100)

    result = investor(
        pre_money=str(pre_money), investment=str(investment), outcome_multiplier=str(multiplier), holder_percent="25"
    )

    assert result.value_ratio.exact == 1
    assert result.verdict == "break_even"
    holder = result.holder
    assert holder is not None and holder.value_before is not None and holder.value_after is not None
    assert holder.value_after.exact == holder.value_before.exact
