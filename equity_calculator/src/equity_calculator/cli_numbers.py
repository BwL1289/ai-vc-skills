"""The CLI's number readers (argparse ``type=`` functions): amounts, percents, counts, ranks and the workbook path.

Numbers may carry ``$``, ``_`` and commas that separate thousands (``$8,000,000``). A comma before exactly three
digits, after a first group that does not start with 0, is always read as thousands, so ``1,250`` is 1250; any other
comma (``7,5``, ``0,500``, ``8,00,000``) is refused. A percent may carry ``%``. Every refusal quotes the argument as
it was typed, and text longer than any number the models accept is refused before anything reads it as a number.
"""

from __future__ import annotations

import argparse
import re
from decimal import Decimal, InvalidOperation
from pathlib import Path

from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT

_NUMBER_NOISE = ("$", "_")
_THOUSANDS_SEPARATOR = ","
# A comma separates thousands only: a sign, 1 to 3 digits whose first is not 0, then groups of exactly 3
# ("8,000,000.50"). Such a comma is always read as thousands ("1,250" is 1250, whatever was meant); any other comma
# ("7,5", "0,500", "8,00,000") is refused rather than read as a larger number. The first digit goes through int(),
# so a full-width or Arabic-Indic zero is refused like "0" while their other digits still read.
_GROUPED_NUMBER = re.compile(r"[+-]?(?P<lead>\d)\d{0,2}(?:,\d{3})+(?:\.\d*)?")
_ZERO_DIGIT = 0
_GROUPING_RULE = (
    "a comma must separate thousands (1 to 3 digits not starting with 0, then groups of 3, as in 8,000,000)"
)
_PERCENT_SIGN = "%"
_WORKBOOK_SUFFIX = ".xlsx"


def _clean(text: str, raw: str) -> str:
    """``text`` without ``$``, ``_`` and thousands commas; any other comma is refused, quoting ``raw`` as typed.

    Text longer than any number the models accept is refused before anything reads it as a number.
    """
    cleaned = text.strip()
    if len(cleaned) > MAX_NUMBER_TEXT:
        raise argparse.ArgumentTypeError(f"a number here is at most {MAX_NUMBER_TEXT} characters long")
    for noise in _NUMBER_NOISE:
        cleaned = cleaned.replace(noise, "")
    if _THOUSANDS_SEPARATOR in cleaned:
        grouped = _GROUPED_NUMBER.fullmatch(cleaned)
        if grouped is None or int(grouped["lead"]) == _ZERO_DIGIT:
            raise argparse.ArgumentTypeError(f"{_GROUPING_RULE}, got {raw!r}")

    return cleaned.replace(_THOUSANDS_SEPARATOR, "")


def _number(text: str, raw: str) -> Decimal:
    """``text`` as a finite decimal; every refusal quotes ``raw``, the argument as it was typed."""
    try:
        value = Decimal(_clean(text, raw))
    except InvalidOperation:
        raise argparse.ArgumentTypeError(f"must be a number, got {raw!r}") from None
    if not value.is_finite():
        raise argparse.ArgumentTypeError(f"must be a finite number, got {raw!r}")

    return value


def parse_decimal(raw: str) -> Decimal:
    """argparse type for an amount or a ratio: a finite decimal, ``$`` and ``_`` ignored, ``,`` only in thousands."""
    return _number(raw, raw)


def parse_percent(raw: str) -> Decimal:
    """argparse type for a percent in points (``7`` or ``7%`` is 7%); a refusal quotes the value with its ``%``."""
    return _number(raw.strip().removesuffix(_PERCENT_SIGN), raw)


def _whole(raw: str, expected: str) -> int:
    """``raw`` as a whole number (``_`` ignored, ``,`` only between thousands); a refusal says it ``expected``."""
    try:
        return int(_clean(raw, raw))
    except ValueError:
        raise argparse.ArgumentTypeError(f"must be {expected}, got {raw!r}") from None


def parse_whole(raw: str) -> int:
    """argparse type for a share count: a whole number, ``_`` ignored, ``,`` only between thousands."""
    return _whole(raw, "a whole number of shares")


def parse_months(raw: str) -> int:
    """argparse type for a count of months: a whole number, ``_`` ignored, ``,`` only between thousands."""
    return _whole(raw, "a whole number of months")


def parse_customers(raw: str) -> int:
    """argparse type for a count of customers: a whole number, ``_`` ignored, ``,`` only between thousands."""
    return _whole(raw, "a whole number of customers")


def parse_rank(raw: str) -> int:
    """argparse type for a seniority rank: a whole number, 1 the most senior (the model bounds it)."""
    return _whole(raw, "a whole-number rank (1 is paid first)")


def parse_workbook_path(raw: str) -> Path:
    """argparse type for ``--xlsx``: a path ending ``.xlsx``, so Excel opens what is written."""
    path = Path(raw)
    if path.suffix.lower() != _WORKBOOK_SUFFIX:
        raise argparse.ArgumentTypeError(f"must end {_WORKBOOK_SUFFIX}, got {raw!r}")

    return path
