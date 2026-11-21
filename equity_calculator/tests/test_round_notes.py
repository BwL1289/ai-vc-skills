"""Convertible notes in a priced round: the cap on FD, interest by compounding and day count, cash-paid interest.

Each note's owed amount is worked by hand in its docstring and checked exactly (the interest rounded to the cent
first, as the round converts it). Pure arithmetic: no DB, no network.
"""

from __future__ import annotations

import decimal
from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.interest import note_interest
from equity_calculator.schemas.equity_round import NoteTerms
from tests.support import ROUND_EXAMPLE, ROUND_NOTE, ROUND_SAFES, round_

_FIRST = 0
# Four fractional_power notes at or near the largest the bounds allow: a 16-digit principal with the rate under 100%,
# for 599 of the 600 months or up to all 18,262 days. Each owed amount was worked to the cent at 200 digits two ways
# (the power itself; the exact whole-period power times exp(stub x ln(growth))), and both agree. For that cent the
# stub needs 35 digits on the yearly note, 39 and 42 on the two monthly actual/360 ones (the second uses every digit
# the principal and rate allow) and 44 on the actual/365 one, the most a review's random sample of notes needed. At 28
# digits they are off from $21,288.28 to about -$2.7 trillion; one digit short of each need, $0.03, -$0.20, -$0.01 and
# -$0.01.
_LARGEST_NOTES: dict[str, tuple[dict[str, object], Fraction]] = {
    "annual-599-months": (
        {
            "principal": "9999999999999999",
            "interest_rate_percent": "99.99",
            "compounding": "annual",
            "stub_rule": "fractional_power",
            "months_outstanding": 599,
        },
        Fraction(1_060_058_899_672_118_333_630_798_292_659_328, 100),
    ),
    "monthly-dated-actual-360": (
        {
            "principal": "9990000000000000",
            "interest_rate_percent": "99.99",
            "compounding": "monthly",
            "stub_rule": "fractional_power",
            "issue_date": "2000-01-01",
            "conversion_date": "2049-12-15",
            "day_count": "actual_360",
        },
        Fraction(1_379_897_021_528_119_698_071_595_021_011_540_961_972, 100),
    ),
    "monthly-bound-maximal-actual-360": (
        {
            "principal": "9999999999999999.999999999999",
            "interest_rate_percent": "99.99999999999999999999999999",
            "compounding": "monthly",
            "stub_rule": "fractional_power",
            "issue_date": "2000-01-01",
            "conversion_date": "2049-12-31",
            "day_count": "actual_360",
        },
        Fraction(1_448_280_945_476_274_347_077_089_587_551_420_252_233, 100),
    ),
    "monthly-worst-need-actual-365": (
        {
            "principal": "4738677950554764",
            "interest_rate_percent": "99.7633106005",
            "compounding": "monthly",
            "stub_rule": "fractional_power",
            "issue_date": "2000-01-01",
            "conversion_date": "2049-08-02",
            "day_count": "actual_365",
        },
        Fraction(212_313_235_298_525_939_772_346_339_883_370_199_506, 100),
    ),
}
_HOSTILE_PRECISION = 2
_HOSTILE_EMAX = 0
# ROUND_NOTE's $500k at 8% for 18 months with no compounding and no stub rule named: the defaults apply.
_NO_TERMS_NOTE: dict[str, object] = {key: value for key, value in ROUND_NOTE.items() if key != "compounding"}
_TWO_YEARS_OF_MONTHS = 24
# What that note owes, worked by hand and by an independent Fraction script: 500k·1.08^1.5 to the cent (a year and a
# fractional-power half-year stub); 500k·1.08·1.04 (simple stub); 500k·(1 + 0.08·1.5) (simple interest);
# 500k·(1 + 0.08/12)^18 to the cent (18 whole months); 500k·1.08² (two whole years).
_YEARLY_POWER_18_MONTHS = Fraction(56_118_446, 100)
_YEARLY_SIMPLE_STUB_18_MONTHS = Fraction(561_600)
_SIMPLE_18_MONTHS = Fraction(560_000)
_MONTHLY_18_MONTHS = Fraction(56_352_397, 100)
_YEARLY_24_MONTHS = Fraction(583_200)


def test_a_note_on_its_pre_money_cap() -> None:
    """Cap price K/FD = 6M/10M = 3/5; F = 560k·FD/K, p = 14M/(FD + F - U) = 420/313; shares 560k/(3/5)."""
    result = round_(**ROUND_EXAMPLE, instruments=[{**ROUND_NOTE, "valuation_cap": "6000000"}])
    note = result.conversions[_FIRST]

    assert note.accrued_interest is not None and note.cap_price is not None
    assert note.accrued_interest.exact == 60_000
    assert note.converting_amount.exact == 560_000
    assert note.cap_price.exact == Fraction(3, 5)
    assert note.basis == "cap"
    assert note.shares.exact == Fraction(2_800_000, 3)
    assert result.price_per_share.exact == Fraction(420, 313)
    assert not note.interest_approximate


@pytest.mark.parametrize(
    ("compounding", "stub_rule", "owed", "approximate"),
    [
        ("simple", "simple", Decimal("560000.00"), False),
        ("annual", "simple", Decimal("561600.00"), False),
        ("annual", "fractional_power", Decimal("561184.46"), True),
        ("monthly", "simple", Decimal("563523.97"), False),
    ],
    ids=["simple", "annual-simple-stub", "annual-fractional-power", "monthly"],
)
def test_note_interest_by_compounding(compounding: str, stub_rule: str, owed: Decimal, approximate: bool) -> None:
    """$500k at 8% for 18 months: simple 1.12x; annual 1.08 then 1.04 (stub); 1.08^1.5; (1 + 0.08/12)^18."""
    note = {**ROUND_NOTE, "compounding": compounding, "stub_rule": stub_rule, "discount_percent": "20"}

    row = round_(**ROUND_EXAMPLE, instruments=[note]).conversions[_FIRST]

    assert row.converting_amount.rounded == owed
    assert row.interest_approximate is approximate
    assert row.basis == "discount"


@pytest.mark.parametrize(
    ("compounding", "owed"),
    [("annual", Fraction(583_200)), ("monthly", Fraction(58_644_397, 100))],
    ids=["annual-24-months", "monthly-24-months"],
)
def test_a_fractional_power_note_with_no_stub_is_exact(compounding: str, owed: Fraction) -> None:
    """24 months is a whole number of periods, so no fractional power: 500k·1.08² and 500k·(1 + 0.08/12)^24, exact."""
    note = {
        **ROUND_NOTE,
        "compounding": compounding,
        "stub_rule": "fractional_power",
        "months_outstanding": 24,
        "discount_percent": "20",
    }

    row = round_(**ROUND_EXAMPLE, instruments=[note]).conversions[_FIRST]

    assert row.converting_amount.exact == owed
    assert row.interest_approximate is False


def _no_terms_note(**terms: object) -> NoteTerms:
    """The $500k note at 8% for 18 months naming only ``terms`` (no compounding or stub rule unless given)."""
    return NoteTerms.model_validate({**_NO_TERMS_NOTE, **terms})


def test_a_note_naming_no_terms_compounds_yearly_with_a_fractional_power_stub() -> None:
    """No compounding or stub_rule: yearly, fractional-power stub (the default): 500k·1.08^1.5, approximate."""
    note = _no_terms_note()
    row = round_(**ROUND_EXAMPLE, instruments=[_NO_TERMS_NOTE]).conversions[_FIRST]

    assert "stub_rule" not in _NO_TERMS_NOTE
    assert (note.compounding, note.stub_rule) == ("annual", "fractional_power")
    assert row.converting_amount.exact == _YEARLY_POWER_18_MONTHS
    assert row.interest_approximate is True


def test_simple_interest_is_still_selectable() -> None:
    """compounding simple, no stub rule named: the old $560,000.00, 500k·(1 + 0.08·1.5), exact."""
    interest = note_interest(_no_terms_note(compounding="simple"))

    assert interest.owed == _SIMPLE_18_MONTHS
    assert interest.approximate is False


@pytest.mark.parametrize(
    ("terms", "owed", "approximate"),
    [
        ({}, _YEARLY_POWER_18_MONTHS, True),
        ({"stub_rule": "fractional_power"}, _YEARLY_POWER_18_MONTHS, True),
        ({"stub_rule": "simple"}, _YEARLY_SIMPLE_STUB_18_MONTHS, False),
    ],
    ids=["no-stub-rule", "fractional-power", "simple-stub"],
)
def test_an_18_month_note_compounds_a_year_and_a_half_year_stub(
    terms: dict[str, object], owed: Fraction, approximate: bool
) -> None:
    """No compounding named, so yearly: one whole year and half a year left, by each stub rule."""
    interest = note_interest(_no_terms_note(**terms))

    assert interest.owed == owed
    assert interest.approximate is approximate


@pytest.mark.parametrize(
    "terms",
    [{}, {"stub_rule": "fractional_power"}, {"stub_rule": "simple"}],
    ids=["no-stub-rule", "fractional-power", "simple-stub"],
)
def test_a_24_month_note_has_no_stub_so_both_stub_rules_agree(terms: dict[str, object]) -> None:
    """Two whole years leave no stub: 500k·1.08² = $583,200 exactly under either rule, never approximate."""
    interest = note_interest(_no_terms_note(months_outstanding=_TWO_YEARS_OF_MONTHS, **terms))

    assert interest.owed == _YEARLY_24_MONTHS
    assert interest.approximate is False


@pytest.mark.parametrize(
    "terms",
    [{}, {"stub_rule": "fractional_power"}, {"stub_rule": "simple"}],
    ids=["no-stub-rule", "fractional-power", "simple-stub"],
)
def test_a_monthly_note_is_unchanged_by_the_default(terms: dict[str, object]) -> None:
    """Monthly for 18 months is 18 whole periods: 500k·(1 + 0.08/12)^18 = $563,523.97, exact under either rule."""
    interest = note_interest(_no_terms_note(compounding="monthly", **terms))

    assert interest.owed == _MONTHLY_18_MONTHS
    assert interest.approximate is False


@pytest.mark.parametrize(("terms", "owed"), list(_LARGEST_NOTES.values()), ids=list(_LARGEST_NOTES))
def test_the_largest_fractional_power_notes_are_exact_to_the_cent(terms: dict[str, object], owed: Fraction) -> None:
    """Near the largest the bounds allow, the stub's digits still give the cent a 200-digit reference gives."""
    interest = note_interest(NoteTerms.model_validate(terms))

    assert interest.owed == owed
    assert interest.approximate is True


@pytest.mark.parametrize(("terms", "owed"), list(_LARGEST_NOTES.values()), ids=list(_LARGEST_NOTES))
def test_a_changed_default_decimal_context_changes_no_note(
    terms: dict[str, object], owed: Fraction, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A changed decimal.DefaultContext changes no note: the stub's private context takes none of its fields.

    The test traps Inexact there, sets 2 digits, rounds up and caps the exponent at 0 (monkeypatch restores each).
    """
    note = NoteTerms.model_validate(terms)
    monkeypatch.setitem(decimal.DefaultContext.traps, decimal.Inexact, True)
    monkeypatch.setattr(decimal.DefaultContext, "prec", _HOSTILE_PRECISION)
    monkeypatch.setattr(decimal.DefaultContext, "rounding", decimal.ROUND_UP)
    monkeypatch.setattr(decimal.DefaultContext, "Emax", _HOSTILE_EMAX)

    assert note_interest(note).owed == owed


@pytest.mark.parametrize(
    ("day_count", "accrued"),
    [("actual_365", Fraction(40_000)), ("actual_360", Fraction(1_013_889, 25))],
    ids=["actual-365", "actual-360"],
)
def test_a_dated_note_counts_its_days(day_count: str, accrued: Fraction) -> None:
    """365 days at 8% simple on $500k: 8% of a year on actual/365, 365/360 of it on actual/360 (rounded to the cent)."""
    note = {
        "kind": "note",
        "principal": "500000",
        "interest_rate_percent": "8",
        "compounding": "simple",
        "issue_date": "2025-01-01",
        "conversion_date": "2026-01-01",
        "day_count": day_count,
        "discount_percent": "20",
    }

    row = round_(**ROUND_EXAMPLE, instruments=[note]).conversions[_FIRST]

    assert row.accrued_interest is not None
    assert row.accrued_interest.exact == accrued


def test_interest_paid_in_cash_leaves_only_the_principal_converting() -> None:
    """The $60k is shown as accrued but paid out, so $500k converts at the discount price p·0.8."""
    note = {**ROUND_NOTE, "discount_percent": "20", "interest_paid_in_cash": True}

    result = round_(**ROUND_EXAMPLE, instruments=[note])
    row = result.conversions[_FIRST]

    assert row.accrued_interest is not None
    assert row.accrued_interest.exact == 60_000
    assert row.converting_amount.exact == 500_000
    assert row.conversion_price.exact == result.price_per_share.exact * Fraction(4, 5)


def test_note_assumptions_appear_only_with_a_note() -> None:
    """A SAFE-only round carries no note conventions; a round with a note names its day count and stub rule."""
    safes_only = {assumption.key for assumption in round_(**ROUND_EXAMPLE, instruments=ROUND_SAFES).assumptions}
    with_note = {assumption.key for assumption in round_(**ROUND_EXAMPLE, instruments=[ROUND_NOTE]).assumptions}

    assert "note_interest" not in safes_only
    assert {"note_cap_basis", "note_interest", "day_count", "interest_rounding", "interest_conversion"} <= with_note


def test_the_round_price_cites_yc_guide_and_leaves_notes_unverified() -> None:
    """The price rule quotes YC's Post-Money Safe User Guide example; notes converting the same way stay unverified."""
    rows = {row.key: row for row in round_(**ROUND_EXAMPLE, instruments=[ROUND_NOTE]).assumptions}
    source = rows["converted_shares_in_pre_money"].source

    assert source.startswith("Y Combinator, Post-Money Safe User Guide (version 1.2, February 2023)")
    assert "pre-money valuation / (total fully diluted shares post safe conversion + option pool increase)" in source
    assert source.endswith(f"(notes converting the same way: {UNVERIFIED})")
