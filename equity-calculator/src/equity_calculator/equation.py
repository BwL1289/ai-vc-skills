"""Paul Graham's equity equation, the one test every trade of stock runs (``paulgraham.com/equity.html``, July 2007).

"You should give up n% of your company if what you trade it for improves your average outcome enough that the
(100 - n)% you have left is worth more than the whole company was before." With m the deal's multiplier on the
average outcome, the holders' value ratio is R = (1 - n)·m; the trade wins only when R > 1, which is m > 1/(1 - n).
The same formula, run backwards, prices a hire: a person who multiplies the outcome by i is worth n = (i - 1)/i.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

from equity_calculator.exact import HUNDRED, ONE, ZERO, fraction
from equity_calculator.schemas.equity import GrantVerdict, TradeVerdict


def outcome_multiplier(multiplier: Decimal | None, percent_change: Decimal | None) -> Fraction:
    """The multiplier given directly, or 1 + g/100 from a percent change (the schema requires exactly one)."""
    if multiplier is not None:
        return fraction(multiplier)

    if percent_change is None:
        raise ValueError("give a multiplier or a percent change")

    return ONE + fraction(percent_change) / HUNDRED


def value_ratio(stake_sold: Fraction, multiplier: Fraction) -> Fraction:
    """R = (1 - n)·m: what the holders keep after the trade, as a multiple of the whole company before it."""
    return (ONE - stake_sold) * multiplier


def break_even_multiplier(stake_sold: Fraction) -> Fraction:
    """m* = 1/(1 - n): the multiplier at which selling ``stake_sold`` leaves the holders exactly even."""
    return ONE / (ONE - stake_sold)


def break_even_growth(stake_sold: Fraction) -> Fraction:
    """g* = n/(1 - n) = m* - 1: the growth in the average outcome the trade must beat."""
    return stake_sold / (ONE - stake_sold)


def trade_verdict(ratio: Fraction) -> TradeVerdict:
    """Accept only when R > 1 (strictly); R exactly 1 is its own verdict, break even; below 1 is reject."""
    if ratio > ONE:
        return "accept"

    if ratio == ONE:
        return "break_even"

    return "reject"


def break_even_stake(hire_multiplier: Fraction) -> Fraction:
    """n = (i - 1)/i, floored at 0: the most of the company a hire who multiplies the outcome by i is worth."""
    return max(ZERO, (hire_multiplier - ONE) / hire_multiplier)


def grant_verdict(hire_multiplier: Fraction) -> GrantVerdict:
    """``grant`` for i > 1, ``break_even`` for i exactly 1 (a zero grant), ``no_grant`` for i < 1."""
    if hire_multiplier > ONE:
        return "grant"

    if hire_multiplier == ONE:
        return "break_even"

    return "no_grant"
