"""The parts every scenario's report is built from: ``Line``, ``Sheet`` and the helpers for inputs shown as given.

A ``Sheet`` is one scenario's report: its value columns (one, or several for a table such as the pool's pre-money
and post-money columns or one column per holder), its ``Line`` rows and its labelled assumptions. A line holds the
model's quantities, never a recomputed number; a total line names the lines it adds, so the workbook writes it as a
live ``=SUM`` formula under each number while the text shows the model's own total. A line may also carry a workbook
formula over other lines (``formula``), so an edited input recomputes it; the printed report and JSON never use it.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from equity_calculator.exact import fraction, from_percent, quantity
from equity_calculator.schemas.equity_common import EquityAssumption, EquityQuantity, EquityUnit

GIVEN = "given"
_YES = "yes"
_NO = "no"


@dataclass(frozen=True)
class Line:
    """One report row: a label, one value per value column, and how the value is computed.

    ``formula`` is a workbook formula without its ``=``, naming other lines as ``{key}``; the workbook writes it in
    place of the value, each ``{key}`` read as that line's cell in the same column. Empty: the value is written.
    ``full_precision`` writes a quantity's exact value (as the nearest binary float, which is what a spreadsheet holds)
    rather than its display rounding: an input that formulas read, so they work from what was given.
    """

    key: str
    label: str
    values: tuple[EquityQuantity | str, ...]
    how: str
    total_of: tuple[str, ...] = ()
    verdict: bool = False
    formula: str = ""
    full_precision: bool = False


@dataclass(frozen=True)
class Sheet:
    """One scenario's report: a sheet title, a one-line heading, its value columns, lines and labelled assumptions."""

    title: str
    heading: str
    columns: tuple[str, ...]
    lines: tuple[Line, ...]
    assumptions: tuple[EquityAssumption, ...]


def given(unit: EquityUnit, value: Decimal) -> EquityQuantity:
    """An input shown as given: ``value`` as a quantity of ``unit``."""
    return quantity(unit, fraction(value))


def given_percent(value: Decimal) -> EquityQuantity:
    """A percent input (``7`` for 7%) shown as the fraction it names."""
    return quantity("fraction", from_percent(value))


def yes_no(flag: bool) -> str:
    """A flag as the report's ``yes`` or ``no``."""
    return _YES if flag else _NO
