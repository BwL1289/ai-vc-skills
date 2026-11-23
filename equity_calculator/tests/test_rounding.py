"""``equity_calculator.rounding``: the one rounding test ``metrics_check`` and ``deal_check`` share.

Pure arithmetic: exact fractions, no decimal context. A figure as typed carries its places (``12`` none, ``12.0`` one,
a zero written ``0.0`` one); the computed figure rounded half away from zero to those places must equal it.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.rounding import round_half_away, rounding_label, rounds_to, typed_places
from equity_calculator.schemas.equity_common import WrittenDecimal
from pydantic import TypeAdapter


@pytest.mark.parametrize(
    ("typed", "places"), [("12", 0), ("12.0", 1), ("12.40", 2), ("0.0", 1), ("0", 0), ("1.2E+1", 0), ("1.25E-1", 3)]
)
def test_the_places_are_the_ones_typed(typed: str, places: int) -> None:
    assert typed_places(Decimal(typed)) == places


@pytest.mark.parametrize(
    ("value", "places", "rounded"),
    [
        (Fraction(25, 2), 0, Fraction(13)),
        (Fraction(-25, 2), 0, Fraction(-13)),
        (Fraction(23, 2), 0, Fraction(12)),
        (Fraction(1, 6) * 100, 1, Fraction(167, 10)),
        (Fraction(1, 20), 1, Fraction(1, 10)),
        (Fraction(-1, 20), 1, Fraction(-1, 10)),
    ],
    ids=["12.5-up", "minus-12.5-down", "11.5-up", "16.6667-one-place", "0.05-up", "minus-0.05-down"],
)
def test_a_half_rounds_away_from_zero_exactly(value: Fraction, places: int, rounded: Fraction) -> None:
    assert round_half_away(value, places) == rounded


@pytest.mark.parametrize(
    ("computed", "zero_one_place", "zero_none"),
    [(Fraction(4, 10000), True, True), (Fraction(5, 10000), False, True), (Fraction(5, 1000), False, False)],
    ids=["0.04%", "0.05%", "0.5%"],
)
def test_a_zero_with_places_holds_only_what_rounds_to_it(
    computed: Fraction, zero_one_place: bool, zero_none: bool
) -> None:
    """A zero written "0.0" is a claim to one place: it holds 0.04% (0.0 at one place) but not 0.05% (0.1); "0" holds
    both and not 0.5% (1). The schema keeps the zero's places (``WrittenDecimal``), so the test sees them."""
    one_place = TypeAdapter(WrittenDecimal).validate_python("0.0")

    assert rounds_to(one_place, "fraction", computed) is zero_one_place
    assert rounds_to(Decimal(0), "fraction", computed) is zero_none


def test_money_has_no_rounding_test() -> None:
    assert rounds_to(Decimal("1200000"), "money", Fraction(1_234_567)) is None


def test_months_and_multiples_compare_unscaled_and_a_percent_in_points() -> None:
    assert rounds_to(Decimal("12"), "months", Fraction(62, 5)) is True
    assert rounds_to(Decimal("12.0"), "months", Fraction(62, 5)) is False
    assert rounds_to(Decimal("1.5"), "multiplier", Fraction(3, 2)) is True
    assert rounds_to(Decimal("17"), "fraction", Fraction(1, 6)) is True


def test_the_rounding_label_shows_the_figure_as_typed() -> None:
    assert rounding_label("Runway", Decimal("12.0")) == 'Runway: rounds to the deck\'s "12.0"'
    assert rounding_label("Runway", Decimal("1.2E+1")) == 'Runway: rounds to the deck\'s "12"'
