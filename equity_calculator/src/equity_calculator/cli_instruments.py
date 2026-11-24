"""The repeated-flag readers: ``--safe``, ``--note``, ``--round``, ``--class``, ``--use-of-funds``, a runway plan's,
a market size's, a priced-round-or-note comparison's, a pool plan's ``--hire`` and a raise pipeline's
``--commitment`` and ``--stage``.

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
    --use-of-funds 1250000       (a deal check's use-of-funds line in dollars)
    --use-of-funds 50%           (or as a percent of the raise)
    --phase "from-month=4 gross-burn=220000 revenue=25000"     (a runway plan's phase; also --downside-phase, …)
    --raise "amount=3000000 lands-month=6 stated-runway-months=24 stated-runway-from=landing"
    --raise-use-of-funds "1 50%"  (a runway plan's use-of-funds line for the first --raise)
    --segment "customers=18000 price=400 price-period-months=1 serviceable-percent=60 obtainable-customers=900"
    --top-down "amount=2100000000 comparable-percent=40 compare-to=tam"
    --sensitivity "field=obtainable-customers segment=1 values=600/1200"   (values split on "/")
    --priced-preference "standard"   (a comparison's series terms: standard, 1x non-participating, only when so said)
    --priced-preference "preference-multiple=1 participation=none rank=1"
    --next-round "pre-money=27000000 investment=6000000 target-pool-percent=10 standard"
    --hire "Senior engineer: start-month=4 grant-shares=250000"   (a pool plan's hire: its role, a colon, then terms)
    --hire "Head of sales: start-month=9 grant-percent=1.5"
    --commitment "500000 kind=firm"   (a raise pipeline's commitment: its amount, then soft or firm)
    --stage "First meeting: investors=10 rate-percent=30"   (a funnel stage: its name, a colon, then terms)
    --stage "Partner meeting: investors=2 rate-percent=25 rate-basis=benchmark benchmark-source=A survey, 2025"

Numbers read as every other flag's do (``equity_calculator.cli_numbers``); a date is ``YYYY-MM-DD``. An unknown,
repeated or malformed term is refused naming the term; which terms go together is the model's check
(``equity_calculator.schemas.equity_round``, ``equity_calculator.schemas.equity_dilution``,
``equity_calculator.schemas.equity_waterfall``, ``equity_calculator.schemas.equity_runway_plan``,
``equity_calculator.schemas.equity_market_sizing``, ``equity_calculator.schemas.equity_instrument_compare``,
``equity_calculator.schemas.equity_pool_plan``, ``equity_calculator.schemas.equity_raise_pipeline``). A
``--stage``'s ``benchmark-source=`` term comes last and takes the rest of the argument, spaces included.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable
from datetime import date
from typing import get_args

from equity_calculator.cli_numbers import (
    parse_count,
    parse_decimal,
    parse_months,
    parse_percent,
    parse_rank,
    parse_whole,
)
from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT, PoolTiming
from equity_calculator.schemas.equity_market_sizing import PERCENT_FIELDS, CompareTo, SegmentField
from equity_calculator.schemas.equity_raise_pipeline import CommitmentKind, RateBasis
from equity_calculator.schemas.equity_round import DayCount, NoteCompounding, StubRule
from equity_calculator.schemas.equity_runway_plan import RunwayFrom
from equity_calculator.schemas.equity_waterfall import Participation

__all__ = [
    "parse_class",
    "parse_commitment",
    "parse_funds_line",
    "parse_hire",
    "parse_next_round",
    "parse_note",
    "parse_phase",
    "parse_raise",
    "parse_raise_funds_line",
    "parse_round",
    "parse_safe",
    "parse_segment",
    "parse_sensitivity",
    "parse_stage",
    "parse_series",
    "parse_top_down",
]

_TERM_SEPARATOR = "="
_PERCENT_SIGN = "%"
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
# A new series' terms (a comparison's ``--priced-preference``, and inside a ``--next-round``): the bare flag standard,
# or the multiple and participation the founder gives.
_SERIES_TERMS: dict[str, _Reader] = {
    "preference_multiple": parse_decimal,
    "participation": _choice(get_args(Participation)),
    "cap_multiple": parse_decimal,
    "rank": parse_rank,
}
_SERIES_FLAGS = ("standard",)
_NEXT_ROUND_TERMS: dict[str, _Reader] = {
    "pre_money": parse_decimal,
    "investment": parse_decimal,
    "target_pool_percent": parse_percent,
    "pool_timing": _choice(get_args(PoolTiming)),
}
_PREFERENCE = "preference"
# A pool plan's hire: the role (free words) before the first colon, then its start month and one grant.
_ROLE_SEPARATOR = ":"
_HIRE_TERMS: dict[str, _Reader] = {
    "start_month": parse_months,
    "grant_shares": parse_whole,
    "grant_percent": parse_percent,
}
# A raise pipeline's commitment: its amount first, then whether it is soft or firm. A funnel stage: its name (free
# words) before the first colon, then its investors today, the founder's rate and where the rate comes from; a
# benchmark's source is the last term and runs to the end of the argument.
_COMMITMENT_AMOUNT = "amount"
_COMMITMENT_TERMS: dict[str, _Reader] = {"kind": _choice(get_args(CommitmentKind))}
_STAGE_TERMS: dict[str, _Reader] = {
    "investors": parse_count,
    "rate_percent": parse_percent,
    "rate_basis": _choice(get_args(RateBasis)),
}
_SOURCE_TERM = "benchmark-source="
_PHASE_TERMS: dict[str, _Reader] = {
    "from_month": parse_months,
    "gross_burn": parse_decimal,
    "revenue": parse_decimal,
}
_RAISE_TERMS: dict[str, _Reader] = {
    "amount": parse_decimal,
    "lands_month": parse_months,
    "stated_runway_months": parse_decimal,
    "stated_runway_from": _choice(get_args(RunwayFrom)),
}

_SEGMENT_TERMS: dict[str, _Reader] = {
    "customers": parse_decimal,
    "price": parse_decimal,
    "price_period_months": parse_months,
    "units_per_customer": parse_decimal,
    "take_rate_percent": parse_percent,
    "serviceable_percent": parse_percent,
    "obtainable_percent": parse_percent,
    "obtainable_customers": parse_decimal,
    "customers_today": parse_decimal,
}
_TOP_DOWN_TERMS: dict[str, _Reader] = {
    "amount": parse_decimal,
    "comparable_percent": parse_percent,
    "compare_to": _choice(get_args(CompareTo)),
}
# A sensitivity row's values are one term, split on "/" (a comma is a thousands separator), each read by its field's
# reader once the field is known, so the terms may come in any order.
_VALUES = "values"
_VALUE_SEPARATOR = "/"
_SENSITIVITY_FIELDS = tuple(field.replace("_", "-") for field in get_args(SegmentField))


def _sensitivity_field(raw: str) -> object:
    """A sensitivity row's field, written with hyphens (``obtainable-customers``), as the model's name."""
    if raw not in _SENSITIVITY_FIELDS:
        raise argparse.ArgumentTypeError(f"must be one of {', '.join(_SENSITIVITY_FIELDS)}, got {raw!r}")

    return raw.replace("-", "_")


def _segment_number(raw: str) -> object:
    """A segment's number in a ``--sensitivity`` row: a whole number, 1 for the first ``--segment``."""
    try:
        return int(raw)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"must be a segment's number (1 for the first --segment), got {raw!r}"
        ) from None


_SENSITIVITY_TERMS: dict[str, _Reader] = {"field": _sensitivity_field, "segment": _segment_number, _VALUES: str}


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


def parse_funds_line(raw: str) -> dict[str, object]:
    """argparse type for ``--use-of-funds``: an amount in dollars (``1250000``) or a percent of the raise (``50%``)."""
    text = _checked_length(raw).strip()
    if text.endswith(_PERCENT_SIGN):
        return {"percent": parse_percent(text)}

    return {"amount": parse_decimal(text)}


def parse_round(raw: str) -> dict[str, object]:
    """argparse type for ``--round``: ``(investor-percent=N | pre-money=V investment=I) [pool-percent=P]``."""
    return _named_terms(_checked_length(raw).split(), {}, _ROUND_TERMS, ())


def parse_class(raw: str) -> dict[str, object]:
    """argparse type for ``--class``: ``shares=S invested=I [preference-multiple=M] [rank=K] [participation=…]``."""
    return _named_terms(_checked_length(raw).split(), {}, _CLASS_TERMS, ())


def parse_series(raw: str) -> dict[str, object]:
    """argparse type for ``--priced-preference``: ``standard [rank=K]`` or ``preference-multiple=M
    participation=none|full|capped [cap-multiple=C] [rank=K]``."""
    return _named_terms(_checked_length(raw).split(), {}, _SERIES_TERMS, _SERIES_FLAGS)


def parse_next_round(raw: str) -> dict[str, object]:
    """argparse type for ``--next-round``: ``pre-money=V investment=I [target-pool-percent=T]
    [pool-timing=pre_money|post_money]`` and the series' terms as ``--priced-preference`` takes them."""
    terms = _named_terms(_checked_length(raw).split(), {}, {**_NEXT_ROUND_TERMS, **_SERIES_TERMS}, _SERIES_FLAGS)
    round_terms = {name: value for name, value in terms.items() if name in _NEXT_ROUND_TERMS}
    series = {name: value for name, value in terms.items() if name not in _NEXT_ROUND_TERMS}
    return {**round_terms, _PREFERENCE: series}


def parse_hire(raw: str) -> dict[str, object]:
    """argparse type for ``--hire``: ``ROLE: start-month=M (grant-shares=S | grant-percent=P)``, the role in the
    founder's words before the first colon (the model checks its characters)."""
    role, separator, terms = _checked_length(raw).partition(_ROLE_SEPARATOR)
    if not separator:
        raise argparse.ArgumentTypeError(
            f"starts with the role and a colon ('Senior engineer: start-month=4 grant-shares=250000'), got {raw!r}"
        )

    return _named_terms(terms.split(), {"role": role.strip()}, _HIRE_TERMS, ())


def parse_commitment(raw: str) -> dict[str, object]:
    """argparse type for ``--commitment``: ``AMOUNT kind=soft|firm``, the amount in dollars first."""
    first, *rest = _checked_length(raw).split() or [""]
    if not first:
        raise argparse.ArgumentTypeError(f"starts with the amount in dollars ('500000 kind=firm'), got {raw!r}")

    return _named_terms(rest, {_COMMITMENT_AMOUNT: parse_decimal(first)}, _COMMITMENT_TERMS, ())


def parse_stage(raw: str) -> dict[str, object]:
    """argparse type for ``--stage``: ``NAME: investors=N rate-percent=P [rate-basis=own|benchmark]
    [benchmark-source=TEXT]``, the name in the founder's words before the first colon and a benchmark's source, last,
    running to the end (the model checks the characters of both)."""
    name, separator, terms = _checked_length(raw).partition(_ROLE_SEPARATOR)
    if not separator:
        raise argparse.ArgumentTypeError(
            f"starts with the stage's name and a colon ('First meeting: investors=10 rate-percent=30'), got {raw!r}"
        )
    head, marker, source = terms.partition(_SOURCE_TERM)
    stage: dict[str, object] = {"name": name.strip()}
    if marker:
        stage["benchmark_source"] = source.strip()

    return _named_terms(head.split(), stage, _STAGE_TERMS, ())


def parse_phase(raw: str) -> dict[str, object]:
    """argparse type for a runway plan's ``--phase`` (and ``--downside-phase``, ``--lean-phase``):
    ``from-month=M gross-burn=G [revenue=R]``."""
    return _named_terms(_checked_length(raw).split(), {}, _PHASE_TERMS, ())


def parse_raise(raw: str) -> dict[str, object]:
    """argparse type for ``--raise``: ``amount=I [lands-month=L] [stated-runway-months=M]
    [stated-runway-from=today|landing]``."""
    return _named_terms(_checked_length(raw).split(), {}, _RAISE_TERMS, ())


def parse_raise_funds_line(raw: str) -> dict[str, object]:
    """argparse type for ``--raise-use-of-funds``: the raise's number (1 is the first ``--raise``), then one line in
    dollars (``1250000``) or as a percent of that raise (``50%``)."""
    first, _, rest = _checked_length(raw).strip().partition(" ")
    option = _raise_number(first, raw)
    if not rest.strip():
        raise argparse.ArgumentTypeError(f"needs the raise's number and then an amount or a percent, got {raw!r}")

    return {"option": option, **parse_funds_line(rest)}


def _raise_number(text: str, raw: str) -> int:
    """The raise's number in a ``--raise-use-of-funds`` line: a whole number from 1."""
    try:
        number = int(text)
    except ValueError:
        number = 0
    if number < 1:
        raise argparse.ArgumentTypeError(f"starts with the raise's number (1 for the first --raise), got {raw!r}")

    return number


def parse_segment(raw: str) -> dict[str, object]:
    """argparse type for ``--segment``: ``customers=N price=P [price-period-months=M] [units-per-customer=U]
    [take-rate-percent=T] [serviceable-percent=S] [obtainable-percent=O | obtainable-customers=C]
    [customers-today=D]``."""
    return _named_terms(_checked_length(raw).split(), {}, _SEGMENT_TERMS, ())


def parse_top_down(raw: str) -> dict[str, object]:
    """argparse type for ``--top-down``: ``amount=A [comparable-percent=P] [compare-to=tam|sam]``."""
    return _named_terms(_checked_length(raw).split(), {}, _TOP_DOWN_TERMS, ())


def parse_sensitivity(raw: str) -> dict[str, object]:
    """argparse type for ``--sensitivity``: ``field=F segment=K values=V1/V2``, each value read as its field reads
    (a percent field's as a percent, the price as dollars, the rest as numbers)."""
    row = _named_terms(_checked_length(raw).split(), {}, _SENSITIVITY_TERMS, ())
    text = row.get(_VALUES)
    if isinstance(text, str):
        field = row.get("field")
        reader = parse_percent if field in PERCENT_FIELDS else parse_decimal
        row[_VALUES] = [reader(part) for part in text.split(_VALUE_SEPARATOR)]

    return row
