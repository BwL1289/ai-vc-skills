"""Exact arithmetic for ``equity_calculator``: ``Decimal`` in, ``Fraction`` inside, ``Decimal`` out, never the decimal
context.

Every input is converted with ``Fraction(Decimal)``, which is exact, and every output is rounded from the exact
fraction half away from zero by integers (``round_half_away_whole``, the rule the rounding test of a document's figure
uses too, so a printed 12.13 is what the check compares) and rebuilt as a ``Decimal`` from a string. No
step reads or changes the global ``decimal`` context, so a caller's precision or rounding mode cannot change a
result. Money split across rows uses largest-remainder rounding so the cents add up to the rounded total exactly.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction

from equity_calculator.schemas.equity import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_common import MIN_ADJUSTED_EXPONENT, round_half_away_whole

# Decimal places each unit is rounded to for display. A fraction is shown as a percent, so 6 places of the
# fraction are 4 places of the percent (7.5269%); multipliers and share prices keep 6 places (1.075269x,
# $0.736842); money is whole cents; share counts keep 3 places of a share (exact mode can hold fractional shares);
# months of runway keep 2 places (18.89 months); a count of customers keeps 2 (a share of a count can be fractional).
DISPLAY_PLACES: dict[EquityUnit, int] = {
    "fraction": 6,
    "multiplier": 6,
    "money": 2,
    "price": 6,
    "shares": 3,
    "months": 2,
    "count": 2,
}

ONE = Fraction(1)
ZERO = Fraction(0)
HUNDRED = Fraction(100)
_CENTS_PER_DOLLAR = 100
_DECIMAL_BASE = 10
_MONEY_PLACES = DISPLAY_PLACES["money"]
# A unit price is shown to the cent at least, to the ``price`` unit's 6 places when it needs them, and to at most 15
# (the smallest decimal input is 1e-15).
_CENT_PLACES = 2
_PRICE_PLACES = DISPLAY_PLACES["price"]
_FINEST_PLACES = -MIN_ADJUSTED_EXPONENT


def fraction(value: Decimal | int | Fraction) -> Fraction:
    """``value`` as an exact fraction (a ``Decimal`` converts exactly; no context is read; a ``Fraction`` is kept)."""
    return Fraction(value)


def from_percent(value: Decimal | Fraction) -> Fraction:
    """A percent field (``7`` for 7%) as the exact fraction it names (7/100); an exact ``Fraction`` of percent points
    (a pool plan's target) converts the same way."""
    return Fraction(value) / HUNDRED


def round_to_places(value: Fraction, places: int) -> Decimal:
    """``value`` rounded half away from zero to ``places`` decimal places (0.125 to 0.13, -0.125 to -0.13), built from
    an integer and a string."""
    scaled = round_half_away_whole(value * _DECIMAL_BASE**places)
    return Decimal(f"{scaled}E-{places}")


def quantity(unit: EquityUnit, value: Fraction) -> EquityQuantity:
    """An ``EquityQuantity`` holding ``value`` exactly and rounded to ``unit``'s display places."""
    return EquityQuantity(unit=unit, exact=value, rounded=round_to_places(value, DISPLAY_PLACES[unit]))


def split_cents(parts: Sequence[Fraction]) -> tuple[int, ...]:
    """Each part in whole cents, by largest remainder, so the cents sum to the parts' total rounded to the cent.

    Every part takes its floor in cents; the cents left over go one each to the parts with the largest remainders
    (ties to the earlier part). Parts must be non-negative.
    """
    if any(part < ZERO for part in parts):
        raise ValueError("split_cents takes non-negative parts only")

    total_cents = round_half_away_whole(sum(parts, ZERO) * _CENTS_PER_DOLLAR)
    exact_cents = [part * _CENTS_PER_DOLLAR for part in parts]
    floors = [math.floor(cents) for cents in exact_cents]
    leftover = total_cents - sum(floors)
    by_remainder = sorted(range(len(parts)), key=lambda index: (-(exact_cents[index] - floors[index]), index))
    for index in by_remainder[:leftover]:
        floors[index] += 1

    return tuple(floors)


def money_split(parts: Sequence[Fraction]) -> tuple[EquityQuantity, ...]:
    """Money quantities for ``parts``: each exact, each rounded to cents that add up to the rounded total."""
    cents = split_cents(parts)

    return tuple(
        EquityQuantity(
            unit="money",
            exact=part,
            rounded=round_to_places(Fraction(part_cents, _CENTS_PER_DOLLAR), _MONEY_PLACES),
        )
        for part, part_cents in zip(parts, cents, strict=True)
    )


def given_price(value: Decimal) -> EquityQuantity:
    """A unit price as the founder typed it, never rounded: the fewest places from 2 that show it exactly ($400.00,
    $0.0075, $0.00000125, $0.3333333). A typed decimal has a last place, so some count of places is exact."""
    exact = fraction(value)
    exponent = value.as_tuple().exponent
    most = max(_CENT_PLACES, -exponent if isinstance(exponent, int) else _CENT_PLACES)
    fewest = next(
        (count for count in range(_CENT_PLACES, most + 1) if Fraction(round_to_places(exact, count)) == exact), most
    )
    return EquityQuantity(unit="price", exact=exact, rounded=round_to_places(exact, fewest))


def price_quantity(value: Fraction) -> EquityQuantity:
    """A computed unit price (a break-even), exact, and rounded to the fewest places from 2 that show it as 6 places
    would ($400.00, $0.0075, $640.740741); a price under 1e-5 dollars keeps places until two significant digits show,
    up to 15. A price the founder typed is ``given_price``'s, never rounded."""
    places = _PRICE_PLACES
    while places < _FINEST_PLACES and ZERO < abs(value) < Fraction(1, _DECIMAL_BASE ** (places - 1)):
        places += 1
    shown = round_to_places(value, places)
    fewest = next(count for count in range(_CENT_PLACES, places + 1) if round_to_places(value, count) == shown)
    return EquityQuantity(unit="price", exact=value, rounded=round_to_places(value, fewest))
