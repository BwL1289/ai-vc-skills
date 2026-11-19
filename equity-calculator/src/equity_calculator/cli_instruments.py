"""The repeated-flag readers: a round's ``--safe`` or ``--note``, a dilution ``--round``, a waterfall ``--class``.

A ``--safe`` or ``--note`` starts with the amount (a SAFE's purchase amount, a note's principal) and goes on with
``name=value`` terms named like the model fields, hyphens for underscores, plus bare flags; a ``--round`` or a
``--class`` is terms only::

    --safe "500000 valuation-cap=5000000 discount-percent=20"
    --safe "250000 mfn"
    --note "500000 interest-rate-percent=8 compounding=annual months-outstanding=18 valuation-cap=6000000"
    --note "100000 interest-rate-percent=6 issue-date=2025-01-15 conversion-date=2026-03-01 discount-percent=20"
    --round "investor-percent=20 pool-percent=10"
    --round "pre-money=8000000 investment=2000000"
    --class "shares=2000000 invested=5000000 preference-multiple=1 rank=1 participation=capped cap-multiple=3"

Numbers read as every other flag's do (``equity_calculator.cli_numbers``); a date is ``YYYY-MM-DD``. An unknown,
repeated or malformed term is refused naming the term; which terms go together is the model's check
(``equity_calculator.schemas.equity_round``, ``equity_calculator.schemas.equity_dilution``,
``equity_calculator.schemas.equity_waterfall``).
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
from typing import get_args

from equity_calculator.cli_numbers import parse_decimal, parse_months, parse_percent, parse_rank, parse_whole
from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT
from equity_calculator.schemas.equity_round import DayCount, NoteCompounding, StubRule
from equity_calculator.schemas.equity_waterfall import Participation

__all__ = ["parse_class", "parse_note", "parse_round", "parse_safe"]

_TERM_SEPARATOR = "="
_ISO_DATE_LENGTH = len("2026-11-18")
# A whole argument is at most this long: every term at its longest number, which no real item comes near.
_MAX_TERMS_TEXT = 20 * MAX_NUMBER_TEXT

_Reader = Callable[[str], object]


def _choice(allowed: tuple[str, ...]) -> _Reader:
    """A reader that accepts exactly one of ``allowed``."""

    def read(raw: str) -> object:
        if raw not in allowed:
            raise argparse.ArgumentTypeError(f"must be one of {', '.join(allowed)}, got {raw!r}")

        return raw

    return read


def _parse_date(raw: str) -> date:
    """A ``YYYY-MM-DD`` date; anything longer is refused before it is read."""
    if len(raw) != _ISO_DATE_LENGTH:
        raise argparse.ArgumentTypeError(f"must be a date written YYYY-MM-DD, got {raw!r}")
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be a real date written YYYY-MM-DD, got {raw!r}") from None


# Each kind's first term, then its named terms and its bare flags (field names, hyphens for underscores).
_SAFE_AMOUNT = "purchase_amount"
_SAFE_TERMS: dict[str, _Reader] = {"valuation_cap": parse_decimal, "discount_percent": parse_percent}
_SAFE_FLAGS = ("mfn",)
_NOTE_AMOUNT = "principal"
_NOTE_TERMS: dict[str, _Reader] = {
    "interest_rate_percent": parse_percent,
    "compounding": _choice(get_args(NoteCompounding)),
    "stub_rule": _choice(get_args(StubRule)),
    "months_outstanding": parse_months,
    "issue_date": _parse_date,
    "conversion_date": _parse_date,
    "day_count": _choice(get_args(DayCount)),
    "valuation_cap": parse_decimal,
    "discount_percent": parse_percent,
}
_NOTE_FLAGS = ("interest_paid_in_cash",)
_ROUND_TERMS: dict[str, _Reader] = {
    "investor_percent": parse_percent,
    "pre_money": parse_decimal,
    "investment": parse_decimal,
    "pool_percent": parse_percent,
}
_CLASS_TERMS: dict[str, _Reader] = {
    "shares": parse_whole,
    "invested": parse_decimal,
    "preference_multiple": parse_decimal,
    "rank": parse_rank,
    "participation": _choice(get_args(Participation)),
    "cap_multiple": parse_decimal,
}


def _as_term(field: str) -> str:
    return field.replace("_", "-")


def _checked_length(raw: str) -> str:
    """``raw``, refused before it is read when it is longer than any real item's terms."""
    if len(raw) > _MAX_TERMS_TEXT:
        raise argparse.ArgumentTypeError(f"one item's terms are at most {_MAX_TERMS_TEXT:,} characters long")

    return raw


def _named_terms(
    tokens: list[str], item: dict[str, object], terms: dict[str, _Reader], flags: tuple[str, ...]
) -> dict[str, object]:
    """``item`` with each ``name=value`` term and bare flag in ``tokens`` added; unknown or repeated ones refused."""
    known = ", ".join([*(f"{_as_term(name)}=" for name in terms), *(_as_term(name) for name in flags)])
    for token in tokens:
        name, separator, value = token.partition(_TERM_SEPARATOR)
        field = name.replace("-", "_")
        if field in item:
            raise argparse.ArgumentTypeError(f"{name!r} is given twice")
        if field in flags and not separator:
            item[field] = True
        elif field in terms and separator:
            item[field] = terms[field](value)
        else:
            raise argparse.ArgumentTypeError(f"unknown term {token!r} (the terms are: {known})")

    return item


def _instrument(
    raw: str, kind: str, amount: str, terms: dict[str, _Reader], flags: tuple[str, ...]
) -> dict[str, object]:
    """``raw`` read as one instrument of ``kind``: its amount first, then named terms and bare flags."""
    first, *rest = _checked_length(raw).split() or [""]
    if not first:
        raise argparse.ArgumentTypeError(f"starts with the {_as_term(amount)} in dollars, got {raw!r}")

    return _named_terms(rest, {"kind": kind, amount: parse_decimal(first)}, terms, flags)


def parse_safe(raw: str) -> dict[str, object]:
    """argparse type for ``--safe``: ``AMOUNT [valuation-cap=X] [discount-percent=D] [mfn]``."""
    return _instrument(raw, "safe", _SAFE_AMOUNT, _SAFE_TERMS, _SAFE_FLAGS)


def parse_note(raw: str) -> dict[str, object]:
    """argparse type for ``--note``: ``PRINCIPAL interest-rate-percent=R (months-outstanding=M | the two dates) …``."""
    return _instrument(raw, "note", _NOTE_AMOUNT, _NOTE_TERMS, _NOTE_FLAGS)


def parse_round(raw: str) -> dict[str, object]:
    """argparse type for ``--round``: ``(investor-percent=N | pre-money=V investment=I) [pool-percent=P]``."""
    return _named_terms(_checked_length(raw).split(), {}, _ROUND_TERMS, ())


def parse_class(raw: str) -> dict[str, object]:
    """argparse type for ``--class``: ``shares=S invested=I [preference-multiple=M] [rank=K] [participation=…]``."""
    return _named_terms(_checked_length(raw).split(), {}, _CLASS_TERMS, ())
