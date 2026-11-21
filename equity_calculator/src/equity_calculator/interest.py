"""A convertible note's interest: how long it ran, what it owes at the round, and what converts.

The time is whole months (``months_outstanding`` / 12 years) or the days between its two dates over the day count's
year (365 or 360 days). Simple interest is P(1 + r·years). Compounding ``annual`` or ``monthly`` runs n = 1 or 12
periods a year, so the note ran years·n periods: ``whole`` of them and a ``stub`` left over (18 months yearly is one
period and half a stub). A note that names neither compounds yearly with the default stub rule,
``fractional_power``: the growth raised to the fractional power, P(1 + r/n)^(whole + stub), in a private 50-digit
decimal context and marked approximate; that context sets every field itself, so neither the global context nor
``decimal.DefaultContext`` can change the result. Stub rule ``simple`` compounds the whole periods and gives the stub
simple interest, P(1 + r/n)^whole·(1 + (r/n)·stub), which is exact; compounding ``simple`` stays an option too.
A whole number of periods leaves no stub, so both rules then give the exact P(1 + r/n)^whole, never marked approximate.

The amount owed is then rounded to the cent (half-even, by integers) before the note converts: the note's holder is
owed cents, and exact powers of a 28-digit rate grow too long for a 50-instrument round to stay quick.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from decimal import MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN, Context, Decimal, DivisionByZero, InvalidOperation, Overflow
from fractions import Fraction

from equity_calculator.exact import ONE, ZERO, fraction, from_percent
from equity_calculator.schemas.equity_round import DayCount, NoteCompounding, NoteTerms

__all__ = ["NoteInterest", "note_interest", "years_outstanding"]

_MONTHS_PER_YEAR = 12
_DAYS_PER_YEAR: dict[DayCount, int] = {"actual_365": 365, "actual_360": 360}
_PERIODS_PER_YEAR: dict[NoteCompounding, int] = {"simple": 1, "annual": 1, "monthly": _MONTHS_PER_YEAR}
_CENTS_PER_DOLLAR = 100
# Digits for the fractional-power stub. Four pinned notes at or near the largest the bounds allow (a 16-digit principal
# under 100% for about 50 years) need 35, 39, 42 and 44 digits for the cent to match a 200-digit reference, and 44 is
# the most a review's random sample of notes needed; 50 matches all four, a margin rather than a proof for every note.
_POWER_DIGITS = 50
# The stub's context sets every field, so a caller's decimal.DefaultContext (digits, rounding, exponent range, traps)
# never reaches it; a bad operation still raises, as under Python's stock context.
_POWER_TRAPS = (InvalidOperation, DivisionByZero, Overflow)
_POWER_CAPITALS = 1  # exponents print as "E", Python's stock choice
_POWER_CLAMP = 0  # exponents are never clamped, Python's stock choice


@dataclass(frozen=True)
class NoteInterest:
    """What a note owes at the round (rounded to the cent), its accrued interest and the amount that converts."""

    owed: Fraction
    accrued: Fraction
    converting: Fraction
    approximate: bool


def years_outstanding(note: NoteTerms) -> Fraction:
    """How long ``note`` ran, in years: months/12, or days between its dates over its day count's year."""
    if note.months_outstanding is not None:
        return Fraction(note.months_outstanding, _MONTHS_PER_YEAR)
    if note.issue_date is None or note.conversion_date is None:
        raise ValueError("a note gives months_outstanding or both dates (NoteTerms checks this)")

    return Fraction((note.conversion_date - note.issue_date).days, _DAYS_PER_YEAR[note.day_count])


def _power_context() -> Context:
    """A fresh 50-digit context with every field set, so nothing comes from ``decimal.DefaultContext``."""
    return Context(
        prec=_POWER_DIGITS,
        rounding=ROUND_HALF_EVEN,
        Emin=MIN_EMIN,
        Emax=MAX_EMAX,
        capitals=_POWER_CAPITALS,
        clamp=_POWER_CLAMP,
        flags=[],
        traps=list(_POWER_TRAPS),
    )


def _fractional_power(principal: Fraction, growth: Fraction, periods: Fraction) -> Fraction:
    """principal·growth^periods in a private 50-digit context that sets every field (the global one is never read)."""
    context = _power_context()
    base = context.divide(Decimal(growth.numerator), Decimal(growth.denominator))
    exponent = context.divide(Decimal(periods.numerator), Decimal(periods.denominator))
    factor = context.power(base, exponent)

    return principal * Fraction(factor)


def _owed_exact(note: NoteTerms, years: Fraction) -> tuple[Fraction, bool]:
    """(amount owed before rounding, approximate?) for ``note`` after ``years``."""
    principal = fraction(note.principal)
    rate = from_percent(note.interest_rate_percent)
    if note.compounding == "simple":
        return principal * (ONE + rate * years), False

    per_year = _PERIODS_PER_YEAR[note.compounding]
    periods = years * per_year
    whole = math.floor(periods)
    stub = periods - whole
    growth = ONE + rate / per_year
    if note.stub_rule == "fractional_power" and stub != ZERO:
        return _fractional_power(principal, growth, periods), True

    return principal * growth**whole * (ONE + rate / per_year * stub), False


def note_interest(note: NoteTerms) -> NoteInterest:
    """The amount ``note`` owes at the round, rounded to the cent, and what of it converts."""
    exact, approximate = _owed_exact(note, years_outstanding(note))
    owed = Fraction(round(exact * _CENTS_PER_DOLLAR), _CENTS_PER_DOLLAR)
    principal = fraction(note.principal)

    return NoteInterest(
        owed=owed,
        accrued=owed - principal,
        converting=principal if note.interest_paid_in_cash else owed,
        approximate=approximate,
    )
