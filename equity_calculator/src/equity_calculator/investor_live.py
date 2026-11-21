"""The investor sheet's live formulas, and the check that a spreadsheet working them gets the model's answers.

The workbook writes the investor test's derived lines (the stake from the amounts, R, m*, g*, the verdict and the
holder's lines) as formulas over the input cells, so an edited input re-works the whole test (``layout_pg``). A
spreadsheet works those formulas in binary floating point from inputs held as the nearest binary float, so before
the sheet is written live, ``spreadsheet_agrees`` works the same formulas the same way here and keeps them only when
every number lands within the display rounding of the model's exact value and the verdict is the model's. Otherwise
the sheet keeps the model's values, as every other sheet does.

The verdict reads the sign of R - 1 rounded to ``VERDICT_PLACES`` places, so an exact break even that floating point
puts a hair off 1 still reads break even. An R within ``UNDECIDABLE_GAP`` of 1 without being 1 is closer to break
even than floating point can tell apart, so such a sheet is never live.
"""

from __future__ import annotations

import math
from fractions import Fraction

from equity_calculator.exact import DISPLAY_PLACES
from equity_calculator.schemas.equity import EquityQuantity, InvestorResult, TradeVerdict

VERDICT_PLACES = 12
UNDECIDABLE_GAP = Fraction(1, 10**11)

STAKE_FROM_AMOUNTS = "{investment}/({pre_money}+{investment})"
VALUE_RATIO = "(1-{equity_sold})*{outcome_multiplier}"
BREAK_EVEN_MULTIPLIER = "1/(1-{equity_sold})"
BREAK_EVEN_GROWTH = "{equity_sold}/(1-{equity_sold})"
VERDICT = (
    f'IF(ROUND({{value_ratio}}-1,{VERDICT_PLACES})>0,"accept",'
    f'IF(ROUND({{value_ratio}}-1,{VERDICT_PLACES})=0,"break_even","reject"))'
)
HOLDER_AFTER = "{holder_before}*(1-{equity_sold})"
HOLDER_VALUE_BEFORE = "{holder_before}*{pre_money}"
HOLDER_VALUE_AFTER = "{holder_value_before}*{value_ratio}"

# ROUND(x, 12) is 0 exactly when |x| is under half of the 12th place.
_ROUNDS_TO_ZERO = 0.5 * 10.0**-VERDICT_PLACES
_HALF = Fraction(1, 2)
_BASE = 10


def _verdict(ratio: float) -> TradeVerdict:
    """The verdict formula, worked on a floating-point R."""
    gap = ratio - 1.0
    if abs(gap) < _ROUNDS_TO_ZERO:
        return "break_even"
    return "accept" if gap > 0 else "reject"


def _within_display(value: float, quantity: EquityQuantity) -> bool:
    """``value`` is finite and within half the last displayed place of ``quantity``'s exact value."""
    if not math.isfinite(value):
        return False
    return abs(Fraction(value) - quantity.exact) <= _HALF / _BASE ** DISPLAY_PLACES[quantity.unit]


def spreadsheet_agrees(result: InvestorResult) -> bool:
    """Whether a spreadsheet working the investor formulas from full-precision inputs shows the model's answers."""
    if Fraction(0) < abs(result.value_ratio.exact - 1) < UNDECIDABLE_GAP:
        return False

    inputs = result.inputs
    pre_money: float | None = None
    if inputs.pre_money is not None and inputs.investment is not None:
        pre_money, investment = float(Fraction(inputs.pre_money)), float(Fraction(inputs.investment))
        stake = investment / (pre_money + investment)
    else:
        stake = float(result.equity_sold.exact)
    if stake >= 1.0:
        return False

    ratio = (1.0 - stake) * float(result.outcome_multiplier.exact)
    worked: list[tuple[float, EquityQuantity]] = [
        (stake, result.equity_sold),
        (ratio, result.value_ratio),
        (1.0 / (1.0 - stake), result.break_even_multiplier),
        (stake / (1.0 - stake), result.break_even_growth),
    ]
    holder = result.holder
    if holder is not None:
        holder_stake = float(holder.stake_before.exact)
        worked.append((holder_stake * (1.0 - stake), holder.stake_after))
        if pre_money is not None and holder.value_before is not None and holder.value_after is not None:
            value_before = holder_stake * pre_money
            worked += [(value_before, holder.value_before), (value_before * ratio, holder.value_after)]

    return _verdict(ratio) == result.verdict and all(_within_display(value, exact) for value, exact in worked)
