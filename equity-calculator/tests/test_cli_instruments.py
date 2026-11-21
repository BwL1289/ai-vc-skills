"""The ``--safe``, ``--note`` and ``--round`` readers on their own: each term read, each malformed term refused by name.

Pure parsing: no DB, no network, nothing written. ``equity-calculator round`` end to end is ``test_round_cli.py``;
``dilution`` is ``test_holder_cli.py``.
"""

from __future__ import annotations

import argparse
from datetime import date
from decimal import Decimal

import pytest
from equity_calculator.cli_instruments import parse_note, parse_round, parse_safe
from equity_calculator.schemas.equity_common import MAX_NUMBER_TEXT

# cli_instruments' cap on one --safe/--note/--round argument, written out: twenty terms at the longest number.
_LONGEST_TERMS = 20 * MAX_NUMBER_TEXT


def test_parse_safe_reads_the_amount_terms_and_flag() -> None:
    """The amount first (commas read as everywhere else), then named terms and the bare mfn flag."""
    assert parse_safe("1,500,000 valuation-cap=5000000 discount-percent=20 mfn") == {
        "kind": "safe",
        "purchase_amount": Decimal("1500000"),
        "valuation_cap": Decimal("5000000"),
        "discount_percent": Decimal("20"),
        "mfn": True,
    }


def test_parse_note_reads_dates_choices_and_the_cash_flag() -> None:
    """Dates become dates, choices stay their text, and interest-paid-in-cash is a bare flag."""
    assert parse_note(
        "100000 interest-rate-percent=8 issue-date=2025-01-15 conversion-date=2026-03-01 day-count=actual_360 "
        "interest-paid-in-cash"
    ) == {
        "kind": "note",
        "principal": Decimal("100000"),
        "interest_rate_percent": Decimal("8"),
        "issue_date": date(2025, 1, 15),
        "conversion_date": date(2026, 3, 1),
        "day_count": "actual_360",
        "interest_paid_in_cash": True,
    }


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("500000 valuation-cap=1 valuation-cap=2", "'valuation-cap' is given twice"),
        ("500000 mfn mfn", "'mfn' is given twice"),
        ("500000 colour=red", "unknown term 'colour=red' (the terms are: valuation-cap=, discount-percent=, mfn)"),
        ("500000 mfn=yes", "unknown term 'mfn=yes'"),
        ("500000 valuation-cap", "unknown term 'valuation-cap'"),
        ("500000 principal=1", "unknown term 'principal=1'"),
        ("", "starts with the purchase-amount in dollars, got ''"),
        ("   ", "starts with the purchase-amount in dollars"),
        ("five valuation-cap=1", "must be a number, got 'five'"),
        ("500000 discount-percent=abc", "must be a number, got 'abc'"),
    ],
)
def test_parse_safe_refuses_each_malformed_term(raw: str, message: str) -> None:
    """A repeated, unknown, valueless or unreadable term is refused naming the term."""
    with pytest.raises(argparse.ArgumentTypeError) as caught:
        parse_safe(raw)

    assert message in str(caught.value)


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("100000 issue-date=2025-1-15", "must be a date written YYYY-MM-DD, got '2025-1-15'"),
        ("100000 issue-date=2025-01-15T00:00", "must be a date written YYYY-MM-DD"),
        ("100000 conversion-date=2025-02-30", "must be a real date written YYYY-MM-DD, got '2025-02-30'"),
        ("100000 compounding=daily", "must be one of simple, annual, monthly, got 'daily'"),
        ("100000 stub-rule=round", "must be one of simple, fractional_power, got 'round'"),
        ("100000 day-count=30_360", "must be one of actual_365, actual_360, got '30_360'"),
        ("100000 months-outstanding=1.5", "must be a whole number of months, got '1.5'"),
        ("100000 interest-paid-in-cash=yes", "unknown term 'interest-paid-in-cash=yes'"),
        ("100000 mfn", "unknown term 'mfn'"),
        ("", "starts with the principal in dollars, got ''"),
    ],
)
def test_parse_note_refuses_bad_dates_choices_and_terms(raw: str, message: str) -> None:
    """A date that is not YYYY-MM-DD or not real, a choice outside the list, a SAFE-only term: each refused."""
    with pytest.raises(argparse.ArgumentTypeError) as caught:
        parse_note(raw)

    assert message in str(caught.value)


def test_an_argument_over_the_length_cap_is_refused_before_it_is_read() -> None:
    """One character past the cap is refused for its length; at the cap the argument is read (and refused otherwise)."""
    with pytest.raises(argparse.ArgumentTypeError) as over:
        parse_safe("1" * (_LONGEST_TERMS + 1))
    with pytest.raises(argparse.ArgumentTypeError) as at_cap:
        parse_safe("1" * _LONGEST_TERMS)

    assert f"at most {_LONGEST_TERMS:,} characters long" in str(over.value)
    assert "characters long" in str(at_cap.value)
    assert f"{_LONGEST_TERMS:,}" not in str(at_cap.value)


def test_parse_round_reads_a_percent_round_or_an_amounts_round() -> None:
    """Named terms only, in any order, with the money read as everywhere else; no terms is an empty round."""
    assert parse_round("pool-percent=10 investor-percent=20") == {
        "pool_percent": Decimal("10"),
        "investor_percent": Decimal("20"),
    }
    assert parse_round("pre-money=$8,000,000 investment=2,000,000") == {
        "pre_money": Decimal("8000000"),
        "investment": Decimal("2000000"),
    }
    assert parse_round("") == {}


@pytest.mark.parametrize(
    ("raw", "message"),
    [
        ("investor-percent=20 investor-percent=30", "'investor-percent' is given twice"),
        (
            "8000000",
            "unknown term '8000000' (the terms are: investor-percent=, pre-money=, investment=, pool-percent=)",
        ),
        ("investor-percent", "unknown term 'investor-percent'"),
        ("colour=red", "unknown term 'colour=red'"),
        ("investor-percent=abc", "must be a number, got 'abc'"),
        ("pre-money=five", "must be a number, got 'five'"),
    ],
)
def test_parse_round_refuses_each_malformed_term(raw: str, message: str) -> None:
    """A repeated, unknown, valueless or unreadable term is refused naming the term; which terms make a whole round
    is the model's to say."""
    with pytest.raises(argparse.ArgumentTypeError) as caught:
        parse_round(raw)

    assert message in str(caught.value)


def test_a_round_over_the_length_cap_is_refused_before_it_is_read() -> None:
    """The --round reader shares the cap: one character past it is refused for its length alone."""
    with pytest.raises(argparse.ArgumentTypeError) as over:
        parse_round("1" * (_LONGEST_TERMS + 1))

    assert f"one item's terms are at most {_LONGEST_TERMS:,} characters long" in str(over.value)
