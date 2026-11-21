"""The result size limit: ``beyond_limit``, the walk over a result, the workbook writer's refusal and ``--xlsx``.

No DB, no network. ``RESULT_LIMIT`` is 1e300 (``equity_calculator.result_range``) and every boundary value below is
derived from it. The rounds come from ``tests/support.sliver_round``: eight SAFEs stay inside the limit, nine and ten
pass it.
"""

from __future__ import annotations

import math
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import cast

import pytest
from equity_calculator.__main__ import run
from equity_calculator.errors import ResultOutOfRange
from equity_calculator.layout import Line, Sheet, sheet_for
from equity_calculator.result_range import OUT_OF_RANGE_REASON, RESULT_LIMIT, beyond_limit, check_result_range
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.workbook import build_workbook, save_workbook
from pydantic import BaseModel
from tests.support import SAFES_INSIDE_RANGE, SAFES_PAST_RANGE, round_, sliver_round

_FIRST = 0
_TEN = 10
_LIMIT_INT = int(RESULT_LIMIT)
_LIMIT_FRACTION = Fraction(RESULT_LIMIT)
# The largest Decimal below the limit at the default 28-digit precision: 9.999...9E+299.
_JUST_UNDER = RESULT_LIMIT.next_minus()
# The value cell of a one-line sheet: row 1 holds the column headings, column A the labels.
_VALUE_CELL = "B2"
_OUT_FOLDER = "out"
_WORKBOOK_NAME = "round.xlsx"


@pytest.mark.parametrize(
    ("value", "beyond"),
    [
        (RESULT_LIMIT, True),
        (-RESULT_LIMIT, True),
        (_JUST_UNDER, False),
        (-_JUST_UNDER, False),
        (Decimal(0), False),
        (Decimal("NaN"), True),
        (Decimal("Infinity"), True),
        (Decimal("-Infinity"), True),
        (_LIMIT_INT, True),
        (-_LIMIT_INT, True),
        (_LIMIT_INT - 1, False),
        (_LIMIT_FRACTION, True),
        (-_LIMIT_FRACTION, True),
        (_LIMIT_FRACTION - Fraction(1, _LIMIT_INT), False),
        (float(RESULT_LIMIT * _TEN), True),
        (float(RESULT_LIMIT / _TEN), False),
        (math.inf, True),
        (-math.inf, True),
        (math.nan, True),
        (True, False),
        (str(RESULT_LIMIT * _TEN), False),
        (None, False),
    ],
    ids=[
        "decimal-at-limit",
        "decimal-negative-at-limit",
        "decimal-just-under",
        "decimal-negative-just-under",
        "decimal-zero",
        "decimal-nan",
        "decimal-infinity",
        "decimal-negative-infinity",
        "int-at-limit",
        "int-negative-at-limit",
        "int-just-under",
        "fraction-at-limit",
        "fraction-negative-at-limit",
        "fraction-just-under",
        "float-past",
        "float-under",
        "float-infinity",
        "float-negative-infinity",
        "float-nan",
        "bool-is-an-int",
        "string-is-not-a-number",
        "none-is-not-a-number",
    ],
)
def test_beyond_limit_compares_size_exactly_for_each_number_type(value: object, beyond: bool) -> None:
    """Each number type is compared by size against the limit itself; a non-finite number is always beyond it."""
    assert beyond_limit(value) is beyond


class _Part(BaseModel):
    """A nested model, the way a result holds one quantity per instrument."""

    amount: Decimal


class _Result(BaseModel):
    """A result-shaped model: a label, models in a list, numbers in a mapping and in a tuple."""

    label: str
    parts: list[_Part]
    by_name: dict[str, Decimal]
    counts: tuple[int, ...]


def _result(**fields: object) -> _Result:
    """A ``_Result`` whose every number is 1, with ``fields`` put in its place."""
    values: dict[str, object] = {
        "label": "inside",
        "parts": [_Part(amount=Decimal(1))],
        "by_name": {"one": Decimal(1)},
        "counts": (1,),
    }
    values.update(fields)

    return _Result.model_validate(values)


def test_a_result_with_every_value_inside_the_limit_passes() -> None:
    """The control: nothing is refused when no number reaches the limit, whatever a string field says."""
    check_result_range(_result(label=str(RESULT_LIMIT * _TEN)))


@pytest.mark.parametrize(
    "fields",
    [
        {"parts": [_Part(amount=Decimal(1)), _Part(amount=RESULT_LIMIT)]},
        {"by_name": {"one": Decimal(1), "big": -RESULT_LIMIT}},
        {"counts": (1, _LIMIT_INT)},
    ],
    ids=["model-in-a-list", "mapping-value", "tuple-item"],
)
def test_a_value_past_the_limit_is_found_wherever_the_result_holds_it(fields: dict[str, object]) -> None:
    """The walk reaches a nested model's field, a mapping's value and a tuple's item."""
    with pytest.raises(ResultOutOfRange) as caught:
        check_result_range(_result(**fields))

    assert str(caught.value) == OUT_OF_RANGE_REASON


def test_eight_safe_sliver_round_passes_the_check() -> None:
    """The largest answer the bounds give with eight SAFEs (about 4.3e294) is inside the limit."""
    check_result_range(round_(**sliver_round(SAFES_INSIDE_RANGE)))


@pytest.mark.parametrize("safe_count", SAFES_PAST_RANGE)
def test_sliver_rounds_past_the_limit_are_refused(safe_count: int) -> None:
    """Nine and ten SAFEs give share counts past the limit (about 3.9e322 and 3.5e350): one named refusal."""
    with pytest.raises(ResultOutOfRange) as caught:
        check_result_range(round_(**sliver_round(safe_count)))

    assert str(caught.value) == OUT_OF_RANGE_REASON


def _one_value_sheet(value: Decimal) -> Sheet:
    """A one-line sheet whose single value is ``value`` shares."""
    quantity = EquityQuantity(unit="shares", exact=Fraction(value), rounded=value)

    return Sheet(
        "Range", "One value at the edge of the limit", ("Value",), (Line("value", "Value", (quantity,), "given"),), ()
    )


@pytest.mark.parametrize("value", [RESULT_LIMIT, -RESULT_LIMIT], ids=["at-limit", "negative-at-limit"])
def test_workbook_writer_refuses_a_value_past_the_limit(value: Decimal) -> None:
    """The writer refuses a value a cell cannot hold instead of leaving the cell blank, even with no check before it."""
    with pytest.raises(ResultOutOfRange) as caught:
        build_workbook([_one_value_sheet(value)])

    assert str(caught.value) == OUT_OF_RANGE_REASON


def test_workbook_writer_writes_a_value_just_under_the_limit() -> None:
    """The control: the largest value under the limit lands in its cell unchanged."""
    book = build_workbook([_one_value_sheet(_JUST_UNDER)])

    assert book.worksheets[_FIRST][_VALUE_CELL].value == _JUST_UNDER


def test_save_workbook_past_the_limit_writes_no_file_and_no_folder(tmp_path: Path) -> None:
    """A refused workbook leaves nothing behind: the build fails before the folder is made or the file opened."""
    target = tmp_path / _OUT_FOLDER / _WORKBOOK_NAME

    with pytest.raises(ResultOutOfRange):
        save_workbook(target, [sheet_for(round_(**sliver_round(SAFES_PAST_RANGE[_FIRST])))])

    assert not target.parent.exists()


def _cli_round(safe_count: int, workbook: Path) -> list[str]:
    """``equity-calculator round`` arguments for ``sliver_round(safe_count)``, writing the workbook to ``workbook``."""
    fields = sliver_round(safe_count)
    safes = cast(list[dict[str, str]], fields["instruments"])
    argv = [
        "round",
        "--fully-diluted-shares",
        str(fields["fully_diluted_shares"]),
        "--pre-money",
        str(fields["pre_money"]),
        "--investment",
        str(fields["investment"]),
        "--target-pool-percent",
        str(fields["target_pool_percent"]),
    ]
    for safe in safes:
        argv.extend(["--safe", f"{safe['purchase_amount']} discount-percent={safe['discount_percent']}"])

    return [*argv, "--xlsx", str(workbook)]


async def test_cli_xlsx_past_the_limit_exits_with_the_reason_and_writes_nothing(tmp_path: Path) -> None:
    """``--xlsx`` on a round past the limit exits naming the flag and the reason, and leaves no file or folder."""
    workbook = tmp_path / _OUT_FOLDER / _WORKBOOK_NAME

    with pytest.raises(SystemExit) as caught:
        await run(_cli_round(SAFES_PAST_RANGE[_FIRST], workbook))

    assert caught.value.code == f"--xlsx: {OUT_OF_RANGE_REASON}"
    assert not workbook.parent.exists()


async def test_cli_xlsx_inside_the_limit_writes_the_workbook(tmp_path: Path) -> None:
    """The control: the same arguments with eight SAFEs write the workbook and the report names it."""
    workbook = tmp_path / _OUT_FOLDER / _WORKBOOK_NAME

    report = await run(_cli_round(SAFES_INSIDE_RANGE, workbook))

    assert workbook.is_file()
    assert str(workbook) in report
