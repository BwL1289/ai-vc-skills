"""Bounds coverage: every scenario's decimal and count inputs are bounded, the CLI's number limits, small percents.

A walk over every input model (nested ones included) checks each field on its own, so a scenario that joins later is
checked without a new test. Pure checks plus the CLI awaited in process: no DB, no network, nothing written. Each
bound's edges and the hostile sizes timed in a child process are ``test_bounds.py``.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any, get_args, get_origin

import pytest
from equity_calculator.__main__ import run
from equity_calculator.schemas.equity import EquityInput, PoolInput
from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT, SIZE_LIMIT, percent_text
from pydantic import BaseModel, TypeAdapter, ValidationError
from tests.support import BELOW_SMALLEST, DIGIT_REFUSAL, POOL_EXAMPLE, SIZE_REFUSAL

_ARGPARSE_EXIT = 2
# Near 1, so it passes every field's own range (percents, multipliers, amounts) and only the digit bound refuses it.
_TWENTY_NINE_DIGITS_NEAR_ONE = "1.0000000000000000000000000001"
_POOL_ARGV = ["pool", "--fully-diluted-shares", "10000000", "--investment", "2", "--target-pool-percent", "10"]


def _mentions(annotation: object, wanted: type) -> bool:
    """Whether ``wanted`` appears anywhere in ``annotation`` (inside unions, lists and ``Annotated``)."""
    if annotation is wanted:
        return True

    return any(_mentions(argument, wanted) for argument in get_args(annotation))


def _models(annotation: object) -> list[type[BaseModel]]:
    """Every model class inside ``annotation``, nested models included."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        nested = [model for field in annotation.model_fields.values() for model in _models(field.annotation)]
        return [annotation, *nested]

    return [model for argument in get_args(annotation) for model in _models(argument)]


def _input_fields(wanted: type) -> list[tuple[str, TypeAdapter[Any]]]:
    """Each input field that holds a ``wanted`` value, as a validator for that field alone (its bounds included).

    A field that is a list of values (a market size's sensitivity values) is checked item by item: a probe sent to the
    list itself would be refused as not a list, which says nothing about the bound on each value.
    """
    fields = []
    for model in dict.fromkeys(_models(EquityInput)):
        for name, field in model.model_fields.items():
            if not _mentions(field.annotation, wanted):
                continue
            if get_origin(field.annotation) in (tuple, list):
                fields.append((f"{model.__name__}.{name}[]", TypeAdapter(get_args(field.annotation)[0])))
            else:
                fields.append((f"{model.__name__}.{name}", TypeAdapter(field.rebuild_annotation())))

    return fields


def test_the_walk_sees_every_scenario_input() -> None:
    """The coverage walk below reaches every scenario's input model, so a new scenario is checked when it joins."""
    walked = {model.__name__ for model in _models(EquityInput)}

    assert {model.__name__ for model in get_args(get_args(EquityInput)[0])} <= walked
    assert len(_input_fields(Decimal)) > 0
    assert len(_input_fields(int)) > 0


@pytest.mark.parametrize(
    ("probe", "reason"),
    [(_TWENTY_NINE_DIGITS_NEAR_ONE, DIGIT_REFUSAL), (BELOW_SMALLEST, SIZE_REFUSAL), ("1e999999999", "")],
    ids=["29-digits", "below-1e-15", "huge"],
)
def test_every_decimal_input_is_bounded(probe: str, reason: str) -> None:
    """Every decimal field of every input model refuses a value outside the bounds, for the bounds' own reason."""
    unbounded = []
    for name, adapter in _input_fields(Decimal):
        try:
            adapter.validate_python(probe)
            unbounded.append(f"{name} accepted {probe}")
        except ValidationError as error:
            if reason not in str(error):
                unbounded.append(f"{name} refused {probe} without saying {reason!r}")

    assert unbounded == []


def test_every_count_input_has_a_ceiling_below_1e16() -> None:
    """Every whole-number field of every input model refuses 1e16, so no count can grow a huge Fraction."""
    unbounded = []
    for name, adapter in _input_fields(int):
        try:
            adapter.validate_python(SIZE_LIMIT)
            unbounded.append(name)
        except ValidationError:
            pass

    assert unbounded == []


async def test_padded_numbers_are_read_once_the_spaces_are_dropped() -> None:
    """Spaces around a typed number (as a quoted shell argument keeps them) are dropped before it is read."""
    report = await run(
        ["investor", "--pre-money", "  $8,000,000  ", "--investment", " 2,000,000 ", "--outcome-multiplier", " 1.3 "]
    )
    stake = await run(["investor", "--equity-percent", " 7% ", "--outcome-multiplier", "1.1"])

    assert "$8,000,000.00" in report
    assert "20.0000%" in report
    assert "7.0000%" in stake


async def test_cli_text_longer_than_any_bounded_number_is_refused(capsys: pytest.CaptureFixture[str]) -> None:
    """A typed number longer than the models could accept exits 2 before it is read as a number."""
    with pytest.raises(SystemExit) as caught:
        await run([*_POOL_ARGV, "--pre-money", "1" * (MAX_NUMBER_TEXT + 1)])

    assert caught.value.code == _ARGPARSE_EXIT
    assert f"at most {MAX_NUMBER_TEXT} characters long" in capsys.readouterr().err


_OUT_OF_BOUNDS = "a nonzero number here is at least 1e-15 and under 1e16 in size"


@pytest.mark.parametrize(
    ("argv", "message"),
    [
        ([*_POOL_ARGV, "--pre-money", "1e999999999"], f"--pre-money: {_OUT_OF_BOUNDS} (got 1E+999999999)"),
        (
            ["investor", "--equity-percent", "7", "--outcome-multiplier=-1e999999999"],
            f"--outcome-multiplier: {_OUT_OF_BOUNDS} (got -1E+999999999)",
        ),
        (
            ["investor", "--equity-percent", "7", "--outcome-multiplier=-9.9e-16"],
            f"--outcome-multiplier: {_OUT_OF_BOUNDS} (got -9.9E-16)",
        ),
    ],
    ids=["huge", "huge-negative", "tiny-negative"],
)
async def test_cli_names_the_flag_of_an_out_of_bounds_number(argv: list[str], message: str) -> None:
    """A size outside the bounds exits 1 with the flag named, the bound stated and the value given, sign and all."""
    with pytest.raises(SystemExit) as caught:
        await run(argv)

    assert caught.value.code == message


@pytest.mark.parametrize(
    ("value", "text"),
    [
        (Fraction(1, 10**7), "under 0.0001%"),
        (Fraction(-1, 10**7), "between -0.0001% and 0%"),
        (Fraction(0), "0.0000%"),
        (Fraction(1, 2), "50.0000%"),
        (Fraction(1, 10**6), "0.0001%"),
    ],
    ids=["tiny", "tiny-negative", "zero", "half", "smallest-shown"],
)
def test_a_tiny_percent_in_a_message_never_reads_zero(value: Fraction, text: str) -> None:
    """A nonzero share that rounds to 0.0000% reads 'under 0.0001%', so a stated bound is never a false zero."""
    assert percent_text(value) == text


def test_the_pool_refusal_never_states_a_false_zero_bound() -> None:
    """$1 pre-money against $1e15 in: the holders keep under 0.0001%, and the refusal says so rather than 0.0000%."""
    with pytest.raises(ValidationError) as caught:
        PoolInput.model_validate({**POOL_EXAMPLE, "pre_money": "1", "investment": "1000000000000000"})

    assert "= under 0.0001%" in str(caught.value)
