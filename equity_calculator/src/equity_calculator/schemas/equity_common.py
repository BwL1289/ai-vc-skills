"""The parts every equity calculator model shares: config, units, the quantity and assumption models, helpers.

``equity_calculator.schemas.equity`` (the investor and employee scenarios and the ``EquityInput`` / ``EquityResult``
unions) and each later scenario's module (``equity_pool``, ``equity_round``, ``equity_dilution``, ``equity_vesting``,
``equity_waterfall``) import from here, never from each other, so the unions can import every scenario without a cycle.
The exceptions are ``equity_deal_check``, which reuses the round's instruments and the pool and round models (those
two import only this module), ``equity_runway_plan``, which reuses the deal check's use-of-funds line, verdict words
and defaults, and ``equity_metrics_check``, which reuses the deal check's verdict words and default tolerances; there
is still no cycle.

How the models read a decimal: text and ``Decimal`` values are kept digit for digit, never through a binary float.
A Python ``float``, and a JSON number given to ``model_validate_json``, reach the model as the float's shortest
decimal text, about 17 significant digits (``0.30000000000000004441`` arrives as ``0.30000000000000004``); a caller
that needs every digit sends the number as text. A JSON number too small for a float (``1e-4400``) underflows to 0
before the model sees it, so it is read as zero; sent as text, it is refused as too small.

Every decimal input is a ``BoundedDecimal``, checked before anything turns it into a ``Fraction`` (a Fraction of
``1e999999999`` is a billion-digit integer that never finishes building): at most 28 significant digits, trailing
zeros included, and a nonzero value at least 1e-15 and under 1e16 in size. A share count is a ``ShareCount``, below
1e16. Every amount therefore stays far below 1e308, the largest number a spreadsheet cell or a JSON float holds.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, BeforeValidator, ConfigDict, Field

# The kind of number an ``EquityQuantity`` holds, which sets its display rounding and its workbook format.
# ``fraction`` a share of the company or a growth rate (shown as a percent); ``multiplier`` a ratio of outcomes;
# ``money`` dollars; ``price`` dollars per share; ``shares`` a share count; ``months`` a span of months (runway).
EquityUnit = Literal["fraction", "multiplier", "money", "price", "shares", "months"]

# Where the round's option pool is counted. ``pre_money``: created before the round, inside the pre-money
# valuation, so only the existing holders are diluted by it (the usual term sheet, the "option-pool shuffle").
# ``post_money``: added after the round, so the investor is diluted by it too.
PoolTiming = Literal["pre_money", "post_money"]

# How share counts are reported. ``exact``: fractional shares, the exact algebra. ``whole_shares``: new pool and
# investor shares rounded down to whole shares at the exact price, the cash left unconverted reported.
ShareRounding = Literal["exact", "whole_shares"]

MODEL_CONFIG = ConfigDict(frozen=True, extra="forbid", allow_inf_nan=False)

WHOLE_PERCENT = 100  # a stake is below 100% of the company; a fall in outcome is above -100% (everything lost)
ONE_HUNDRED = Fraction(WHOLE_PERCENT)

_MESSAGE_PERCENT_PLACES = 4

# The bounds every decimal input meets (see the module docstring). 28 digits is Decimal's default precision; the
# size limits keep each exact Fraction small: 1e-15 is far below any share, price or rate step, 1e16 far above any
# real valuation, and both far inside a float's range. Text longer than any bounded decimal is refused unread.
MAX_SIGNIFICANT_DIGITS = 28
MIN_ADJUSTED_EXPONENT = -15
MAX_ADJUSTED_EXPONENT = 15
SIZE_LIMIT = 10 ** (MAX_ADJUSTED_EXPONENT + 1)
MAX_NUMBER_TEXT = 100
_CEILING_TEXT = f"under 1e{MAX_ADJUSTED_EXPONENT + 1} in size"
_BOUNDS_TEXT = f"at least 1e{MIN_ADJUSTED_EXPONENT} and {_CEILING_TEXT}"


def percent_text(value: Fraction) -> str:
    """``value`` as a percent with four places, rounded half-even, without the global decimal context.

    A nonzero value that rounds to zero reads ``under 0.0001%`` (``between -0.0001% and 0%`` below zero), never
    ``0.0000%``, so a message never states a bound of zero that is not zero.
    """
    scaled = round(value * ONE_HUNDRED * 10**_MESSAGE_PERCENT_PLACES)
    if scaled == 0 and value != 0:
        smallest = Decimal(f"1E-{_MESSAGE_PERCENT_PLACES}")
        return f"between -{smallest}% and 0%" if value < 0 else f"under {smallest}%"

    return f"{Decimal(f'{scaled}E-{_MESSAGE_PERCENT_PLACES}')}%"


def _refuse_unbounded_raw(value: object) -> object:
    """Before Pydantic reads ``value`` as a ``Decimal``: refuse text too long, or an int too large, to be bounded."""
    if isinstance(value, str) and len(value) > MAX_NUMBER_TEXT:
        raise ValueError(f"a number here is at most {MAX_NUMBER_TEXT} characters long (got {len(value)})")
    if isinstance(value, int) and not isinstance(value, bool) and abs(value) >= SIZE_LIMIT:
        raise ValueError(f"a number here is {_CEILING_TEXT}")

    return value


def _bounded(value: Decimal) -> Decimal:
    """Refuse a decimal with too many digits or a nonzero one too large or too small; every zero becomes ``0``."""
    digits = len(value.as_tuple().digits)
    if digits > MAX_SIGNIFICANT_DIGITS:
        raise ValueError(
            f"a number here has at most {MAX_SIGNIFICANT_DIGITS} significant digits, trailing zeros included "
            f"(got {digits})"
        )
    if value.is_zero():
        return Decimal(0)
    if not MIN_ADJUSTED_EXPONENT <= value.adjusted() <= MAX_ADJUSTED_EXPONENT:
        raise ValueError(f"a nonzero number here is {_BOUNDS_TEXT} (got {value})")

    return value


BoundedDecimal = Annotated[Decimal, BeforeValidator(_refuse_unbounded_raw), AfterValidator(_bounded)]

# strict: a share count is a real int; a bool, a float or a numeric string is refused, never read as one.
ShareCount = Annotated[int, Field(strict=True, lt=SIZE_LIMIT)]


def exactly_one(names: tuple[str, ...], values: tuple[object, ...]) -> None:
    """Refuse unless exactly one of ``values`` is given (not ``None``); the message names the choices."""
    given = sum(value is not None for value in values)
    if given != 1:
        raise ValueError(f"give exactly one of {', '.join(names)} (got {given})")


class EquityQuantity(BaseModel):
    """One computed number: its exact value and that value rounded half-even for display
    (``equity_calculator.exact``)."""

    model_config = MODEL_CONFIG

    unit: EquityUnit
    exact: Fraction
    rounded: Decimal


class EquityAssumption(BaseModel):
    """A labelled assumption a result rests on: its setting, what it means, and where it comes from."""

    model_config = MODEL_CONFIG

    key: str
    setting: str
    statement: str
    source: str
