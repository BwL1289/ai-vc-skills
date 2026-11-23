"""A raise's use-of-funds lines, worked once for every scenario that takes them (``deal_check``, ``runway_plan``).

Amount lines are kept as given and checked against the raise; percent lines become dollars of the raise, split to the
cent, and their total is checked against 100%. Each scenario builds its own check row from the parts returned here,
so the arithmetic and the tolerance rule live in one place. The labelled assumption row is here too.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.exact import ONE, ZERO, fraction, from_percent, money_split, quantity
from equity_calculator.schemas.equity_common import EquityAssumption, EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import FundsLine

__all__ = ["WorkedFunds", "use_of_funds_assumption", "work_use_of_funds"]


@dataclass(frozen=True)
class WorkedFunds:
    """The lines in dollars, their total, their share of the raise, and what the total is checked against.

    ``unit`` is ``fraction`` for percent lines (their share against 100%) and ``money`` for amount lines (their total
    against the raise); ``stated``, ``computed`` and ``tolerance`` are in that unit, the edge counting as consistent.
    """

    lines: tuple[EquityQuantity, ...]
    total: EquityQuantity
    share: EquityQuantity
    unit: EquityUnit
    stated: Fraction
    computed: Fraction
    tolerance: Fraction


def work_use_of_funds(
    lines: Sequence[FundsLine], investment: Fraction, tolerance_points: Decimal, tolerance_percent: Decimal
) -> WorkedFunds | None:
    """``lines`` worked against a raise of ``investment``, or ``None`` with no lines.

    Percent lines are checked within ``tolerance_points`` percentage points of 100%; amount lines within
    ``tolerance_percent`` percent of the raise. The models refuse a mix of the two kinds.
    """
    if not lines:
        return None

    percents = [from_percent(line.percent) for line in lines if line.percent is not None]
    if percents:
        dollars = [investment * share for share in percents]
        share = sum(percents, ZERO)
        unit: EquityUnit = "fraction"
        stated, computed, tolerance = share, ONE, from_percent(tolerance_points)
    else:
        dollars = [fraction(line.amount) for line in lines if line.amount is not None]
        total = sum(dollars, ZERO)
        share = total / investment
        unit = "money"
        stated, computed, tolerance = total, investment, from_percent(tolerance_percent) * investment

    return WorkedFunds(
        lines=money_split(dollars),
        total=quantity("money", sum(dollars, ZERO)),
        share=quantity("fraction", share),
        unit=unit,
        stated=stated,
        computed=computed,
        tolerance=tolerance,
    )


def use_of_funds_assumption() -> EquityAssumption:
    """The labelled rule for use-of-funds lines: they are checked only for adding up to the raise."""
    return EquityAssumption(
        key="use_of_funds_rule",
        setting="the lines add up to the raise",
        statement="Use-of-funds lines are checked only for adding up to the raise (or to 100%); percent lines become "
        "dollars of the raise, split to the cent. No split by category is judged.",
        source=UNVERIFIED,
    )
