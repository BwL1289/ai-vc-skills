"""Input bounds: each bound refused just outside and kept exactly just inside, and a hostile size refused fast.

A ``Fraction`` of ``1e999999999`` is a billion-digit integer that never finishes building, so the bounds must refuse
such a value before anything converts it. The timing cases run in a child process: a regression hangs the child,
which the timeout kills, never this test run. The walk over every input field, the CLI's number limits and the
small-percent text are ``test_bounds_coverage.py``.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from decimal import Decimal
from typing import Any

import pytest
from equity_calculator.schemas.equity import EmployeeInput, InvestorInput, PoolInput
from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT, MAX_SIGNIFICANT_DIGITS, SIZE_LIMIT
from equity_calculator.schemas.equity_metrics_check import MetricsCheckInput
from pydantic import ValidationError
from tests.support import BELOW_SMALLEST, DIGIT_REFUSAL, POOL_EXAMPLE, SIZE_REFUSAL

_CHILD_TIMEOUT_S = 60
_REFUSAL_SECONDS = 1.0
_HOSTILE = ("1e4400", "1e-4400", "1e999999999", "-1e999999999")
_TWENTY_NINE_DIGITS = "0.12345678901234567890123456789"
_TWENTY_EIGHT_DIGITS = "0.1234567890123456789012345678"
_LENGTH_REFUSAL = "characters long"
# $8M written with trailing zeros: 7 digits before the point, the rest after it, each one counted.
_INTEGER_DIGITS = 7
_PAST_DIGIT_BOUND = "8000000." + "0" * (MAX_SIGNIFICANT_DIGITS + 1 - _INTEGER_DIGITS)
_AT_DIGIT_BOUND = "8000000." + "0" * (MAX_SIGNIFICANT_DIGITS - _INTEGER_DIGITS)
# The text cap the README states, written out so a change to MAX_NUMBER_TEXT fails here: $8M padded with zeros.
_LONGEST_TEXT = 100
_AT_TEXT_CAP = "8000000".rjust(_LONGEST_TEXT, "0")
_PAST_TEXT_CAP = "8000000".rjust(_LONGEST_TEXT + 1, "0")
# An int with more digits than the digit bound allows: only the int pre-check refuses it for its size.
_PAST_DIGITS_INT = SIZE_LIMIT**2

# The child works each hostile value through the models and the CLI, timing each refusal itself.
_CHILD_CODE = """
import asyncio, contextlib, io, json, sys, time
from decimal import Decimal
from pydantic import ValidationError
from equity_calculator.schemas.equity import EmployeeInput, InvestorInput, PoolInput
from equity_calculator.__main__ import run

POOL = json.loads(sys.argv[1])
HOSTILE = json.loads(sys.argv[2])
CASES = []
for text in HOSTILE:
    for given in (text, Decimal(text)):
        CASES.append((f"pool pre_money {given!r}", PoolInput, {**POOL, "pre_money": given}))
        CASES.append(
            (f"investor pre_money {given!r}", InvestorInput,
             {"pre_money": given, "investment": "2", "outcome_multiplier": "1.3"}),
        )
        CASES.append((f"employee annual_cost {given!r}", EmployeeInput,
                      {"outcome_multiplier": "1.2", "annual_cost": given, "valuation": "2000000"}))
CASES.append(("pool pre_money int 10**4400", PoolInput, {**POOL, "pre_money": 10**4400}))
CASES.append(("pool shares int 10**4400", PoolInput, {**POOL, "fully_diluted_shares": 10**4400}))
CASES.append(("pool pre_money int 10**1000000", PoolInput, {**POOL, "pre_money": 10**1000000}))

for name, model, fields in CASES:
    started = time.perf_counter()
    try:
        model.model_validate(fields)
        refused, clean = False, False
    except ValidationError as error:
        refused, clean = True, bool(str(error))
    print(json.dumps({"case": name, "refused": refused, "clean": clean, "seconds": time.perf_counter() - started}))

# The number goes into the JSON as a bare number token, the way an API body carries it.
REST = json.dumps({key: value for key, value in POOL.items() if key != "pre_money"})
for text in HOSTILE:
    started = time.perf_counter()
    try:
        PoolInput.model_validate_json(REST[:-1] + ', "pre_money": ' + text + "}")
        refused, clean = False, False
    except ValidationError as error:
        refused, clean = True, bool(str(error))
    print(json.dumps({"case": f"json pre_money {text}", "refused": refused, "clean": clean,
                      "seconds": time.perf_counter() - started}))

ARGVS = [(f"cli --pre-money {text}", ["pool", "--pre-money", text, *json.loads(sys.argv[3])]) for text in HOSTILE]
ARGVS.append(("cli --fully-diluted-shares 1e999999999",
              ["pool", "--pre-money", "8", "--investment", "2", "--target-pool-percent", "10",
               "--fully-diluted-shares", "1e999999999"]))
ARGVS.append(("cli --fully-diluted-shares 4401 digits",
              ["pool", "--pre-money", "8", "--investment", "2", "--target-pool-percent", "10",
               "--fully-diluted-shares", "1" + "0" * 4400]))
for name, argv in ARGVS:
    started = time.perf_counter()
    errors = io.StringIO()
    try:
        with contextlib.redirect_stderr(errors):
            asyncio.run(run(argv))
        refused, clean = False, False
    except SystemExit as stop:
        refused = True
        clean = (isinstance(stop.code, str) or stop.code == 2) and "Traceback" not in errors.getvalue()
    print(json.dumps({"case": name, "refused": refused, "clean": clean, "seconds": time.perf_counter() - started}))
"""


def _child_results() -> list[dict[str, Any]]:
    """Each hostile case as the child process timed it."""
    cli_rest = ["--fully-diluted-shares", "10000000", "--investment", "2", "--target-pool-percent", "10"]
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    finished = subprocess.run(
        [sys.executable, "-c", _CHILD_CODE, json.dumps(POOL_EXAMPLE), json.dumps(list(_HOSTILE)), json.dumps(cli_rest)],
        capture_output=True,
        text=True,
        env=environment,
        timeout=_CHILD_TIMEOUT_S,
        check=False,
    )
    assert finished.returncode == 0, finished.stderr

    return [json.loads(line) for line in finished.stdout.splitlines()]


def test_hostile_sizes_are_refused_cleanly_within_a_second() -> None:
    """1e4400, 1e-4400 and 1e999999999 (text, Decimal, int, JSON, CLI) are each refused within a second, cleanly.

    The int 10**1000000 is among them: read as a Decimal before its size is checked, it takes about 18 seconds.
    """
    results = _child_results()

    assert len(results) == len(_HOSTILE) * 2 * 3 + 3 + len(_HOSTILE) + len(_HOSTILE) + 2
    for result in results:
        assert result["refused"], result["case"]
        assert result["clean"], result["case"]
        assert result["seconds"] < _REFUSAL_SECONDS, result


def _pool(**changes: object) -> PoolInput:
    return PoolInput.model_validate({**POOL_EXAMPLE, **changes})


@pytest.mark.parametrize(
    ("given", "reason"),
    [
        (_TWENTY_NINE_DIGITS, DIGIT_REFUSAL),
        (_PAST_DIGIT_BOUND, DIGIT_REFUSAL),
        ("1e16", SIZE_REFUSAL),
        ("10000000000000000", SIZE_REFUSAL),
        (Decimal("1E+16"), SIZE_REFUSAL),
        (SIZE_LIMIT, SIZE_REFUSAL),
        (_PAST_DIGITS_INT, SIZE_REFUSAL),
        ("0." + "0" * MAX_NUMBER_TEXT + "1", _LENGTH_REFUSAL),
        (_PAST_TEXT_CAP, f"at most {_LONGEST_TEXT} characters long (got {_LONGEST_TEXT + 1})"),
    ],
    ids=[
        "29-digits",
        "29-with-trailing-zeros",
        "1e16-text",
        "1e16-digits",
        "1e16-decimal",
        "1e16-int",
        "33-digit-int",
        "long-text",
        "101-characters",
    ],
)
def test_a_decimal_just_outside_the_bounds_is_refused(given: object, reason: str) -> None:
    """One digit or one power of ten past a bound is refused, and the reason names the bound."""
    with pytest.raises(ValidationError) as caught:
        _pool(pre_money=given)

    assert reason in str(caught.value)


@pytest.mark.parametrize(
    ("given", "kept"),
    [
        ("9999999999999999", Decimal("9999999999999999")),
        (SIZE_LIMIT - 1, Decimal(SIZE_LIMIT - 1)),
        (_AT_DIGIT_BOUND, Decimal(_AT_DIGIT_BOUND)),
        (_AT_TEXT_CAP, Decimal("8000000")),
    ],
    ids=["largest-text", "largest-int", "28-digits", "100-characters"],
)
def test_a_decimal_just_inside_the_bounds_is_kept_digit_for_digit(given: object, kept: Decimal) -> None:
    """The largest value and the longest one the bounds allow are read exactly."""
    assert _pool(pre_money=given).pre_money.as_tuple() == kept.as_tuple()


def test_the_smallest_nonzero_size_and_28_digits_are_kept() -> None:
    """1e-15 and a 28-digit fraction pass; 1e-16 is refused as too small."""
    deal = InvestorInput.model_validate({"equity_percent": "1e-15", "outcome_multiplier": "1.3"})
    precise = InvestorInput.model_validate({"equity_percent": _TWENTY_EIGHT_DIGITS, "outcome_multiplier": "1.3"})

    assert deal.equity_percent == Decimal("1e-15")
    assert precise.equity_percent == Decimal(_TWENTY_EIGHT_DIGITS)
    with pytest.raises(ValidationError, match=SIZE_REFUSAL):
        InvestorInput.model_validate({"equity_percent": BELOW_SMALLEST, "outcome_multiplier": "1.3"})


@pytest.mark.parametrize("zero", ["0e999999999", "-0E-999999999", "0.000"])
def test_every_zero_reads_as_a_plain_zero(zero: str) -> None:
    """A zero with any exponent is kept as 0, so no huge exponent survives the model."""
    hire = EmployeeInput.model_validate({"outcome_multiplier": "1.2", "margin_percent": zero})

    assert hire.margin_percent.as_tuple() == Decimal(0).as_tuple()


@pytest.mark.parametrize(
    ("zero", "kept"),
    [("0", "0"), ("0.0", "0.0"), ("-0.00", "0.00"), ("0e999999999", "0"), ("-0E-999999999", "0E-15")],
)
def test_a_stated_zero_keeps_the_places_it_is_written_with_up_to_15_and_no_sign(zero: str, kept: str) -> None:
    """A metrics check's stated figure keeps a zero's places for its rounding test ("0.0%" is a claim to one place),
    at most 15 (the smallest nonzero input's), so no huge exponent survives; its sign is dropped."""
    parts = {"period_months": 1, "starting_recurring": "100", "churned_recurring": "1"}
    check = MetricsCheckInput.model_validate({**parts, "stated_nrr_percent": zero})

    assert check.stated_nrr_percent is not None
    assert check.stated_nrr_percent.as_tuple() == Decimal(kept).as_tuple()


@pytest.mark.parametrize(
    "shares",
    [SIZE_LIMIT, True, 1.0e7, "10000000"],
    ids=["1e16", "bool", "float", "text"],
)
def test_a_share_count_is_a_real_int_below_1e16(shares: object) -> None:
    """A share count of 1e16 or more is refused, and so is a bool, a float or a numeric string."""
    with pytest.raises(ValidationError):
        _pool(fully_diluted_shares=shares)


def test_the_largest_share_count_is_kept() -> None:
    """A share count just below 1e16 is read as given."""
    assert _pool(fully_diluted_shares=SIZE_LIMIT - 1).fully_diluted_shares == SIZE_LIMIT - 1
