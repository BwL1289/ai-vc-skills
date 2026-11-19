"""The investor test: is the stake a round sells worth what the round does to the company's average outcome?

The stake sold is ``equity_percent``, or n = I/(V + I) from the amounts. The verdict is PG's: R = (1 - n)·m, accept
only when R > 1, break even at exactly 1. A holder's stake after the round is h(1 - n); its dollar value, when the
amounts are given, is h·V before and h(1 - n)·m·V after, so the holder gains exactly when R > 1.
"""

from __future__ import annotations

from fractions import Fraction

from equity_calculator.assumptions import investor_assumptions
from equity_calculator.equation import (
    break_even_growth,
    break_even_multiplier,
    outcome_multiplier,
    trade_verdict,
    value_ratio,
)
from equity_calculator.exact import ONE, fraction, from_percent, quantity
from equity_calculator.schemas.equity import HolderOutcome, InvestorInput, InvestorResult

_FIRST = 0  # the amounts are (pre-money V, investment I)


def _amounts(inputs: InvestorInput) -> tuple[Fraction, Fraction] | None:
    """(pre-money V, investment I) when the stake comes from amounts, else ``None``."""
    if inputs.pre_money is None or inputs.investment is None:
        return None

    return fraction(inputs.pre_money), fraction(inputs.investment)


def _stake_sold(inputs: InvestorInput, amounts: tuple[Fraction, Fraction] | None) -> Fraction:
    """n: the equity percent given, or I/(V + I) from the amounts."""
    if amounts is not None:
        pre_money, investment = amounts
        return investment / (pre_money + investment)

    if inputs.equity_percent is None:
        raise ValueError("give equity_percent, or pre_money with investment")

    return from_percent(inputs.equity_percent)


def _holder(
    inputs: InvestorInput, stake_sold: Fraction, multiplier: Fraction, pre_money: Fraction | None
) -> HolderOutcome | None:
    """One holder's stake (and, with a pre-money valuation, its dollar value) before and after the round."""
    if inputs.holder_percent is None:
        return None

    before = from_percent(inputs.holder_percent)
    after = before * (ONE - stake_sold)
    if pre_money is None:
        return HolderOutcome(stake_before=quantity("fraction", before), stake_after=quantity("fraction", after))

    return HolderOutcome(
        stake_before=quantity("fraction", before),
        stake_after=quantity("fraction", after),
        value_before=quantity("money", before * pre_money),
        value_after=quantity("money", after * multiplier * pre_money),
    )


def compute_investor(inputs: InvestorInput) -> InvestorResult:
    """PG's investor test worked exactly: the stake, R, the break-even multiplier and growth, and the verdict."""
    amounts = _amounts(inputs)
    stake_sold = _stake_sold(inputs, amounts)
    multiplier = outcome_multiplier(inputs.outcome_multiplier, inputs.growth_percent)
    ratio = value_ratio(stake_sold, multiplier)
    pre_money = None if amounts is None else amounts[_FIRST]

    return InvestorResult(
        inputs=inputs,
        equity_sold=quantity("fraction", stake_sold),
        outcome_multiplier=quantity("multiplier", multiplier),
        value_ratio=quantity("multiplier", ratio),
        break_even_multiplier=quantity("multiplier", break_even_multiplier(stake_sold)),
        break_even_growth=quantity("fraction", break_even_growth(stake_sold)),
        verdict=trade_verdict(ratio),
        post_money=None if amounts is None else quantity("money", sum(amounts, Fraction(0))),
        holder=_holder(inputs, stake_sold, multiplier, pre_money),
        assumptions=investor_assumptions(inputs),
    )
