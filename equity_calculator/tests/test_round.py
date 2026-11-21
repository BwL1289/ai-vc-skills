"""A priced round: SAFE vectors, the named errors and every model refusal (note interest: test_round_notes.py).

Each vector's exact value is worked by hand in its docstring (sigma, C, the pool, p) and checked as a ``Fraction``,
so a rounding or ordering slip cannot hide behind the display. Pure arithmetic: no DB, no network.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.convertibles import convertibles, settle
from equity_calculator.errors import ConversionDidNotSettle, EquityComputeError, RoundHasNoPrice
from equity_calculator.schemas.equity_round import MAX_INSTRUMENTS, MAX_NOTE_MONTHS, RoundInput
from pydantic import ValidationError
from tests.support import ROUND_EXAMPLE, ROUND_NOTE, ROUND_SAFES, round_

_FIRST = 0
_SECOND = 1
# A post-money SAFE of $1M with both terms: a $40M cap and a 20% discount (the discount wins in this round).
_CAP_AND_DISCOUNT = {
    "kind": "safe",
    "purchase_amount": "1000000",
    "valuation_cap": "40000000",
    "discount_percent": "20",
}


def test_two_capped_safes_with_the_pool_in_the_pre_money() -> None:
    """sigma = 0.1 + 0.1, C = FD/(1 - sigma) = 12.5M; p = (V - t(V + I))/(C - U) = 14M/12M = 7/6.

    The new pool is P = t(V + I)/p - U = 8.5M/7 and the investor buys N = I/p = 24M/7, so the post-money at p is
    exactly V + I. Each SAFE converts a/(K/C) = 1.25M shares at its cap price K/C (2/5 and 4/5).
    """
    result = round_(**ROUND_EXAMPLE, instruments=ROUND_SAFES)

    assert result.capped_safe_fraction.exact == Fraction(1, 5)
    assert result.company_capitalization.exact == 12_500_000
    assert result.price_per_share.exact == Fraction(7, 6)
    assert result.new_pool_shares.exact == Fraction(8_500_000, 7)
    assert result.investor_shares.exact == Fraction(24_000_000, 7)
    assert result.total_shares.exact == Fraction(120_000_000, 7)
    assert result.post_money.exact == 20_000_000
    assert result.passes == 1
    assert [row.cap_price.exact for row in result.conversions if row.cap_price] == [Fraction(2, 5), Fraction(4, 5)]
    assert [row.basis for row in result.conversions] == ["cap", "cap"]
    assert [row.shares.exact for row in result.conversions] == [1_250_000, 1_250_000]
    assert [row.ownership.exact for row in result.rows] == [
        Fraction(133, 240),
        Fraction(7, 96),
        Fraction(7, 96),
        Fraction(1, 10),
        Fraction(1, 5),
    ]
    assert [row.value.rounded for row in result.rows] == [
        Decimal("11083333.34"),
        Decimal("1458333.33"),
        Decimal("1458333.33"),
        Decimal("2000000.00"),
        Decimal("4000000.00"),
    ]
    assert [(row.holder, row.instrument) for row in result.rows] == [
        ("existing_holders", None),
        ("safe", 1),
        ("safe", 2),
        ("option_pool", None),
        ("investor", None),
    ]


def test_the_same_safes_with_the_pool_in_the_post_money() -> None:
    """p = V(1 - sigma)/FD = 16M·0.8/10M = 32/25, and the pool is topped up after: P = (t(C + N) - U)/(1 - t)."""
    result = round_(**ROUND_EXAMPLE, pool_timing="post_money", instruments=ROUND_SAFES)

    assert result.price_per_share.exact == Fraction(32, 25)
    assert result.new_pool_shares.exact == Fraction(10_625_000, 9)
    assert [row.ownership.exact for row in result.rows] == [
        Fraction(342, 605),
        Fraction(9, 121),
        Fraction(9, 121),
        Fraction(1, 10),
        Fraction(45, 242),
    ]


def test_a_cap_and_discount_safe_leaves_its_cap_in_the_second_pass() -> None:
    """Both start on their caps; at that price the $40M-cap SAFE's discount price is lower, so pass 2 moves it off.

    Settled: sigma = 0.1 (the first SAFE only), D = 1M/0.8, C = (FD + D/p)/(1 - sigma) and p = 227/191.
    """
    instruments = [ROUND_SAFES[_FIRST], _CAP_AND_DISCOUNT]
    result = round_(**ROUND_EXAMPLE, instruments=instruments)

    assert result.price_per_share.exact == Fraction(227, 191)
    assert result.company_capitalization.exact == Fraction(2_787_500_000, 227)
    assert result.passes == 2
    assert [row.basis for row in result.conversions] == ["cap", "discount"]
    assert [row.shares.exact for row in result.conversions] == [
        Fraction(278_750_000, 227),
        Fraction(238_750_000, 227),
    ]
    discounted = result.conversions[_SECOND]
    assert discounted.discount_price is not None and discounted.cap_price is not None
    assert discounted.discount_price.exact == result.price_per_share.exact * Fraction(4, 5)
    assert discounted.discount_price.exact < discounted.cap_price.exact


def test_a_safe_whose_two_prices_tie_stays_on_its_cap() -> None:
    """A $500k SAFE with an $8M cap and a 20% discount in a $10M pre-money round, no pool: a tie, so it keeps its cap.

    On its cap: sigma = 500k/8M = 1/16, p = V(1 - sigma)/FD = 15/16 and C = FD/(1 - sigma) = 32M/3, so the cap price
    K/C = 3/4 and the discount price p·0.8 = 3/4 are equal. The tie rule keeps the cap and the first pass settles.
    """
    safe = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "8000000", "discount_percent": "20"}
    result = round_(fully_diluted_shares=10_000_000, pre_money="10000000", investment="2000000", instruments=[safe])

    tied = result.conversions[_FIRST]
    assert tied.cap_price is not None and tied.discount_price is not None
    assert tied.cap_price.exact == tied.discount_price.exact == Fraction(3, 4)
    assert result.price_per_share.exact == Fraction(15, 16)
    assert result.company_capitalization.exact == Fraction(32_000_000, 3)
    assert (tied.basis, result.passes) == ("cap", 1)
    assert tied.shares.exact == Fraction(2_000_000, 3)


def test_a_search_held_to_one_pass_is_refused_by_name() -> None:
    """The same round needs two passes; a pass limit of one raises ``ConversionDidNotSettle``, never a guess."""
    inputs = RoundInput.model_validate({**ROUND_EXAMPLE, "instruments": [ROUND_SAFES[_FIRST], _CAP_AND_DISCOUNT]})

    with pytest.raises(ConversionDidNotSettle, match="still changed after 1 passes"):
        settle(inputs, convertibles(inputs), pass_limit=1)


def test_an_mfn_safe_that_took_no_terms_converts_at_the_round_price() -> None:
    """No cap and no discount: its price is p itself, shown as the round price, with no cap or discount line."""
    result = round_(**ROUND_EXAMPLE, instruments=[{"kind": "safe", "purchase_amount": "250000", "mfn": True}])
    row = result.conversions[_FIRST]

    assert row.basis == "round_price"
    assert row.conversion_price.exact == result.price_per_share.exact
    assert row.cap_price is None and row.discount_price is None
    assert {assumption.key for assumption in result.assumptions} >= {"mfn", "safe_price_rule"}


def test_a_round_whose_discounted_safes_leave_no_price_is_refused_by_name() -> None:
    """$12M at a 20% discount needs D = 15M of the 14M the pre-money leaves after the pool: no positive price."""
    instruments = [{"kind": "safe", "purchase_amount": "12000000", "discount_percent": "20"}]

    with pytest.raises(RoundHasNoPrice) as raised:
        round_(**ROUND_EXAMPLE, instruments=instruments)

    assert isinstance(raised.value, EquityComputeError)
    assert "price" in str(raised.value)


# A $500k SAFE at a 50% discount converts as D = 500k/0.5 = $1M off its cap: at a $1M pre-money it takes all of it.
_HALF_OFF_SAFE = {"kind": "safe", "purchase_amount": "500000", "discount_percent": "50"}
_TAKES_THE_WHOLE_PRE_MONEY = "take the whole pre-money valuation: no positive price"


@pytest.mark.parametrize("timing", ["post_money", "pre_money"])
def test_a_round_whose_safes_take_exactly_the_whole_pre_money_is_refused(timing: str) -> None:
    """V(1 - sigma) - D = 1M - 1M = 0 exactly: a zero price is no price, so the first check refuses it by name.

    Let through, the post-money timing would divide by the zero price and the pre-money timing would fail the pool
    check with another reason, so the message pins the zero case to the first check under both timings.
    """
    fields = {**ROUND_EXAMPLE, "pre_money": "1000000", "pool_timing": timing}

    with pytest.raises(RoundHasNoPrice, match=_TAKES_THE_WHOLE_PRE_MONEY):
        round_(**fields, instruments=[_HALF_OFF_SAFE])


def test_one_dollar_more_pre_money_than_the_safes_take_gives_a_positive_price() -> None:
    """At V = $1,000,001 the numerator is $1 and p = 1/FD: the smallest positive price, priced, not refused."""
    fields = {**ROUND_EXAMPLE, "pre_money": "1000001", "pool_timing": "post_money"}

    result = round_(**fields, instruments=[_HALF_OFF_SAFE])

    assert result.price_per_share.exact == Fraction(1, 10_000_000)


_SAFE = ROUND_SAFES[_FIRST]
# A $1,000 SAFE capped at $10M (a/K = 0.01%): 48 of them stay far below the capped total of 100%.
_SMALL_SAFE = {"kind": "safe", "purchase_amount": "1000", "valuation_cap": "10000000"}
# A note dated by its days, for the day-count bound: 2000-01-01 to 2050-01-01 is 18,263 days, one past the cap.
_DATED_NOTE = {**ROUND_NOTE, "months_outstanding": None, "issue_date": "2000-01-01"}


@pytest.mark.parametrize(
    ("changes", "reason"),
    [
        ({"instruments": [{"kind": "safe", "purchase_amount": "1000"}]}, "needs valuation_cap or discount_percent"),
        ({"instruments": [{**_SAFE, "purchase_amount": "5000000"}]}, "must be below valuation_cap"),
        ({"instruments": [{**_SAFE, "mfn": "yes"}]}, "valid boolean"),
        ({"instruments": [{**_SAFE, "discount_percent": "100"}]}, "less than 100"),
        ({"instruments": [{**ROUND_NOTE, "issue_date": "2025-01-01"}]}, "not both and not neither"),
        ({"instruments": [{**ROUND_NOTE, "months_outstanding": None, "issue_date": "2025-01-01"}]}, "go together"),
        (
            {
                "instruments": [
                    {
                        **ROUND_NOTE,
                        "months_outstanding": None,
                        "issue_date": "2026-01-02",
                        "conversion_date": "2026-01-01",
                    }
                ]
            },
            "days after issue_date",
        ),
        (
            {"instruments": [{**_DATED_NOTE, "conversion_date": "2050-01-01"}]},
            r"0 to 18,262 days after issue_date \(got 18,263\)",
        ),
        (
            {"instruments": [{**_DATED_NOTE, "issue_date": "0001-01-01", "conversion_date": "9999-12-31"}]},
            r"\(got 3,652,058\)",
        ),
        ({"instruments": [{**ROUND_NOTE, "months_outstanding": MAX_NOTE_MONTHS + 1}]}, "less than or equal to 600"),
        ({"instruments": [{**ROUND_NOTE, "months_outstanding": "18"}]}, "valid integer"),
        ({"instruments": []}, "at least 1 item"),
        ({"instruments": [_SAFE] * (MAX_INSTRUMENTS + 1)}, "at most 50 items"),
        ({"unissued_pool_shares": 10_000_000, "instruments": [_SAFE]}, "unissued_pool_shares must be below"),
        ({"target_pool_percent": "80", "instruments": [_SAFE]}, "target_pool_percent must be below"),
        (
            {"instruments": [{"kind": "safe", "purchase_amount": "6000000", "valuation_cap": "10000000"}] * 2},
            "add up to 120.0000%",
        ),
    ],
    ids=[
        "safe-no-terms",
        "safe-owns-its-cap",
        "mfn-not-a-bool",
        "discount-100",
        "note-months-and-a-date",
        "note-one-date",
        "note-dates-reversed",
        "note-one-day-past-the-cap",
        "note-dates-year-1-to-9999",
        "note-too-long",
        "note-months-as-text",
        "no-instruments",
        "too-many-instruments",
        "pool-is-everything",
        "pool-target-too-big",
        "caps-over-100-percent",
    ],
)
def test_each_impossible_round_is_refused_for_its_reason(changes: dict[str, object], reason: str) -> None:
    """Every input the model can check alone is refused with a message that names what is wrong."""
    with pytest.raises(ValidationError, match=reason):
        RoundInput.model_validate({**ROUND_EXAMPLE, **changes})


def test_the_largest_allowed_round_is_accepted() -> None:
    """Fifty instruments, a 600-month note and dates 18,262 days apart (2000-01-01 to 2049-12-31) are accepted."""
    dated = {**ROUND_NOTE, "months_outstanding": None, "issue_date": "2000-01-01", "conversion_date": "2049-12-31"}
    notes = [{**ROUND_NOTE, "months_outstanding": MAX_NOTE_MONTHS}, dated]

    inputs = RoundInput.model_validate(
        {**ROUND_EXAMPLE, "instruments": [*notes, *[_SMALL_SAFE] * (MAX_INSTRUMENTS - len(notes))]}
    )

    assert len(inputs.instruments) == MAX_INSTRUMENTS
