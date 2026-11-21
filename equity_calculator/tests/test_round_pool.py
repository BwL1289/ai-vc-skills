"""A priced round's option-pool edges: a pooled price of exactly zero, and an unissued pool exactly at the target.

The SAFE vectors and the other refusals are ``test_round.py``. Pure arithmetic: no DB, no network.
"""

from __future__ import annotations

from fractions import Fraction

import pytest
from equity_calculator.errors import RoundHasNoPrice
from tests.support import ROUND_EXAMPLE, round_

_TIMINGS = ["pre_money", "post_money"]

# A $250k SAFE at a 50% discount converts as D = 250k/0.5 = $500k off its cap (sigma = 0).
_HALF_OFF_SAFE = {"kind": "safe", "purchase_amount": "250000", "discount_percent": "50"}
# $1M in at a $1M pre-money with a 25% pool target: V - t(V + I) - D = 1M - 0.25·2M - 500k = 0 exactly.
_NO_POOLED_PRICE = {
    **ROUND_EXAMPLE,
    "pre_money": "1000000",
    "investment": "1000000",
    "target_pool_percent": "25",
    "pool_timing": "pre_money",
}
# One dollar more pre-money leaves a pooled numerator of $0.75 over C - U = 9.5M: p = 3/38,000,000.
_ONE_DOLLAR_MORE_PRICE = Fraction(3, 38_000_000)

# 10M fully diluted (1M of it unissued pool), $18M pre-money, $6M in, a 6.75% target, and one $1M SAFE capped at
# $10M (sigma = 0.1). Its cap price K/C = 10M/(10M/0.9) = 0.9 is below the price, so it stays on its cap.
_AT_TARGET = {
    "fully_diluted_shares": 10_000_000,
    "unissued_pool_shares": 1_000_000,
    "pre_money": "18000000",
    "investment": "6000000",
    "target_pool_percent": "6.75",
    "instruments": [{"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "10000000"}],
}
_AT_TARGET_PRICE = Fraction(81, 50)
_TARGET_SHARE = Fraction(27, 400)
_ONE_SHARE_SHORT = 999_999


def test_a_pool_target_that_leaves_exactly_no_pooled_price_is_refused_by_name() -> None:
    """The pooled numerator V - t(V + I) - D/(1 - sigma) is exactly 0: a zero price is no price, so it is refused.

    The first check passes (V(1 - sigma) - D = $500k), so the pool check is the one that must refuse; let through,
    the zero price would divide the pool target by zero.
    """
    with pytest.raises(RoundHasNoPrice, match="pool target"):
        round_(**_NO_POOLED_PRICE, instruments=[_HALF_OFF_SAFE])


def test_one_dollar_more_pre_money_gives_the_smallest_pooled_price() -> None:
    """At V = $1,000,001 the pooled numerator is 1,000,001 - 0.25·2,000,001 - 500k = $0.75: priced, not refused."""
    result = round_(**{**_NO_POOLED_PRICE, "pre_money": "1000001"}, instruments=[_HALF_OFF_SAFE])

    assert result.price_per_share.exact == _ONE_DOLLAR_MORE_PRICE
    assert result.pool_already_large_enough is False


@pytest.mark.parametrize("timing", _TIMINGS)
def test_an_unissued_pool_exactly_at_target_in_a_round_counts_as_large_enough(timing: str) -> None:
    """p = V(1 - sigma)/FD = 18M·0.9/10M = 81/50, C = 100M/9 and N = I/p = 100M/27, so t(C + N) = 1M = U exactly.

    Before the round the pooled price is the same 81/50 and the needed pool t(V + I)/p - U = 1.62M/1.62 - 1M is 0;
    after it the needed pool (t(C + N) - U)/(1 - t) is 0. Either way no new shares, and the pool is large enough.
    """
    result = round_(**_AT_TARGET, pool_timing=timing)

    assert result.price_per_share.exact == _AT_TARGET_PRICE
    assert result.new_pool_shares.exact == 0
    assert result.pool_already_large_enough is True
    assert [row.basis for row in result.conversions] == ["cap"]
    assert {row.holder: row.ownership.exact for row in result.rows}["option_pool"] == _TARGET_SHARE


@pytest.mark.parametrize("timing", _TIMINGS)
def test_one_share_short_of_the_target_needs_a_new_pool(timing: str) -> None:
    """With 999,999 unissued the same round falls one share short in both timings, so it adds a pool."""
    result = round_(**{**_AT_TARGET, "unissued_pool_shares": _ONE_SHARE_SHORT}, pool_timing=timing)

    assert result.new_pool_shares.exact > 0
    assert result.pool_already_large_enough is False
