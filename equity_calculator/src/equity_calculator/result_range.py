"""The size limit on a computed answer: no value of ``RESULT_LIMIT`` or more in size reaches a workbook.

Every input is bounded (``equity_calculator.schemas.equity_common``: under 1e16 in size, at least 1e-15 when nonzero, at
most 28 significant digits), yet an accepted round can still give an enormous answer: SAFEs whose discounted amounts use
up all but a sliver of the pre-money leave a price per share near zero, and the share counts that follow from it
grow far past any real cap table. Nine such SAFEs give an answer whose largest value is about 1.8e321 to 3.9e322,
by how they are set (``tests/support.sliver_round(9)`` is the
3.9e322 case). Excel's largest number is 9.99999999999999E+307 ("Excel
specifications and limits"); openpyxl writes a larger value as a blank cell, and an ``=SUM`` over that row then
adds the blank as zero, so the workbook shows a wrong total with no warning. A reader that turns the JSON's number
strings into doubles gets infinity.

``RESULT_LIMIT`` (1e300) sits below Excel's largest number with room for a workbook ``=SUM`` of every row of a
sheet: no report adds anything like 10**7 rows, so a total of values each below the limit stays below 1e307.
The workbook writer refuses such a value (``equity_calculator.workbook``), so ``--xlsx`` and the MCP server's
``equity_workbook`` tool make no file for it. ``check_result_range`` gives a caller the same check on any result; the
printed report, ``--json`` and the MCP scenario tools do not run it. The limit bounds size only: a tiny value is not
refused, it rounds to zero at its unit's display places (``equity_calculator.exact.DISPLAY_PLACES``), and Excel keeps 15
significant digits of any value it holds.
"""

from __future__ import annotations

import math
from collections.abc import Iterator, Mapping
from decimal import Decimal
from fractions import Fraction
from typing import Final

from equity_calculator.errors import ResultOutOfRange
from pydantic import BaseModel

RESULT_LIMIT: Final = Decimal("1e300")
_LIMIT: Final = Fraction(RESULT_LIMIT)
OUT_OF_RANGE_REASON: Final = (
    f"the answer holds a value of {RESULT_LIMIT} or more in size, more than a spreadsheet cell can hold; "
    "no result is given for these inputs"
)


def beyond_limit(value: object) -> bool:
    """Whether ``value`` is a number of ``RESULT_LIMIT`` or more in size, or not a finite number at all.

    Compared exactly: a ``Decimal`` by ``copy_abs`` (which reads no context), a ``Fraction``, an ``int`` or a
    ``float`` against the limit as a ``Fraction`` (a ``bool`` is an ``int``, 0 or 1). A string or ``None`` is not
    a number here.
    """
    if isinstance(value, Decimal):
        return not value.is_finite() or value.copy_abs() >= RESULT_LIMIT
    if isinstance(value, float):
        return not math.isfinite(value) or abs(value) >= _LIMIT
    if isinstance(value, int | Fraction):
        return abs(value) >= _LIMIT
    return False


def _leaves(item: object) -> Iterator[object]:
    """Every value inside ``item``: a model's fields, a mapping's values and a list's or tuple's items, recursively."""
    if isinstance(item, BaseModel):
        for name in type(item).model_fields:
            yield from _leaves(getattr(item, name))
    elif isinstance(item, Mapping):
        for value in item.values():
            yield from _leaves(value)
    elif isinstance(item, list | tuple):
        for value in item:
            yield from _leaves(value)
    else:
        yield item


def check_result_range(result: BaseModel) -> None:
    """Raise ``ResultOutOfRange`` when any number in ``result`` (exact or rounded) is beyond the limit."""
    if any(beyond_limit(leaf) for leaf in _leaves(result)):
        raise ResultOutOfRange(OUT_OF_RANGE_REASON)
