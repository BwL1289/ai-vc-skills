"""The rounding test every check of a document's stated figure shares (``metrics_check``, ``deal_check``,
``runway_plan``, ``cap_table_check``).

People write figures rounded to the places they show: "12 months" for a computed 12.40, "17%" for 16.6667%. A stated
percent, months or multiple is therefore consistent when it is the computed figure rounded half away from zero to the
places it is typed with, past the tolerance or not; ``0.0`` is one place. Money keeps the tolerance alone, since a
figure like $1.2M typed as 1200000 says nothing about its places. Each scenario builds its own check row; the test
and the report wording live here, so the four read the same (a deck's figures by default, a cap table's as
``document="table"``). Exact: integer arithmetic on fractions, never the decimal context.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

from equity_calculator.exact import HUNDRED, fraction
from equity_calculator.schemas.equity_common import EquityUnit, round_half_away_whole

__all__ = [
    "ROUNDING_HOW",
    "ROUNDING_VERDICT_HOW",
    "half_unit",
    "round_half_away",
    "rounding_how",
    "rounding_label",
    "rounding_verdict_how",
    "rounds_to",
    "typed_places",
]

_DECIMAL_BASE = 10
_HALF = Fraction(1, 2)
# The document whose figures a check reads, unless the scenario names another.
_DECK = "deck"


def rounding_verdict_how(document: str = _DECK) -> str:
    """The report's words on the verdict line of a row the rounding test applies to."""
    return f"within the tolerance, or rounding to the {document}'s, is consistent"


def rounding_how(document: str = _DECK) -> str:
    """The report's words on the rounding line of a row the rounding test applies to."""
    return f"the computed figure, rounded half away from zero to the places the {document} writes, is the {document}'s"


ROUNDING_VERDICT_HOW = rounding_verdict_how()
ROUNDING_HOW = rounding_how()


def typed_places(written: Decimal) -> int:
    """The decimal places ``written`` is typed with: ``12`` none, ``12.40`` two, ``0.0`` one (a zero keeps its places,
    ``WrittenDecimal``); an exponent form counts what it spells out (``1.2E+1`` none)."""
    exponent = written.as_tuple().exponent
    return max(0, -exponent) if isinstance(exponent, int) else 0


def half_unit(written: Decimal) -> Fraction:
    """Half a unit in the last place ``written`` is typed with, in its own units (``12.50``: 0.005), exactly: the most
    rounding to those places can move a figure."""
    return _HALF / _DECIMAL_BASE ** typed_places(written)


def round_half_away(value: Fraction, places: int) -> Fraction:
    """``value`` rounded half away from zero to ``places`` decimal places, exactly (12.5 to 13, -2.5 to -3)."""
    scale = _DECIMAL_BASE**places
    return Fraction(round_half_away_whole(value * scale), scale)


def rounds_to(written: Decimal, unit: EquityUnit, computed: Fraction) -> bool | None:
    """Whether ``written`` (percent points for a fraction) is ``computed`` rounded half away from zero to the places
    ``written`` is typed with; none for money, whose round figures (ARR of $1.2M) say nothing about their places."""
    if unit == "money":
        return None
    shown = computed * HUNDRED if unit == "fraction" else computed
    return round_half_away(shown, typed_places(written)) == fraction(written)


def rounding_label(name: str, written: Decimal, document: str = _DECK) -> str:
    """The rounding line's label: the figure as typed, since its places decide the test and the document's line prints
    ``12`` and ``12.0`` alike (12.00 months)."""
    return f'{name}: rounds to the {document}\'s "{written:f}"'
