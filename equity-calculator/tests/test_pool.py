"""The option-pool shuffle: the worked example both ways, the clamp, whole shares, refusals and properties.

Pure arithmetic: no DB, no network. The example deal is 10M fully diluted shares (0.5M unissued pool), an $8M
pre-money, $2M invested and a 10% target pool: with the pool in the pre-money, P = 600,000/0.7 = 6M/7 new shares
at p = 8M/(10M + 6M/7) = $14/19, so the holders really sold at a $7M pre-money.
"""

from __future__ import annotations

import random
from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.schemas.equity import PoolCapTable, PoolInput
from pydantic import ValidationError
from tests.support import POOL_EXAMPLE, pool

_SEED = 20261118
_CASES = 300


def _ownership(table: PoolCapTable) -> dict[str, Fraction]:
    return {row.group: row.ownership.exact for row in table.rows}


def test_pool_in_the_pre_money_matches_the_worked_example() -> None:
    """P = 857,142.857, p = $0.736842, N = 2,714,285.714, T = 13,571,428.571; 70/10/20%; effective pre-money $7M."""
    table = pool(**POOL_EXAMPLE).pool_in_pre_money

    assert table.new_pool_shares.exact == Fraction(6_000_000, 7)
    assert table.new_pool_shares.rounded == Decimal("857142.857")
    assert table.price_per_share.exact == Fraction(14, 19)
    assert table.price_per_share.rounded == Decimal("0.736842")
    assert table.investor_shares.exact == Fraction(19_000_000, 7)
    assert table.investor_shares.rounded == Decimal("2714285.714")
    assert table.total_shares.exact == Fraction(95_000_000, 7)
    assert table.total_shares.rounded == Decimal("13571428.571")
    assert _ownership(table) == {
        "existing_holders": Fraction(7, 10),
        "option_pool": Fraction(1, 10),
        "investor": Fraction(1, 5),
    }
    assert table.effective_pre_money.rounded == Decimal("7000000.00")
    assert table.post_money.rounded == Decimal("10000000.00")
    assert table.uninvested_cash.exact == 0
    assert table.pool_already_large_enough is False


def test_pool_in_the_post_money_matches_the_worked_example() -> None:
    """The same deal with the pool after the round: p = $0.80, holders 71.25%, pool 10%, investor 18.75%."""
    result = pool(**POOL_EXAMPLE)
    table = result.pool_in_post_money

    assert table.price_per_share.exact == Fraction(4, 5)
    assert table.investor_shares.exact == 2_500_000
    assert table.new_pool_shares.exact == Fraction(2_500_000, 3)
    assert _ownership(table) == {
        "existing_holders": Fraction(57, 80),
        "option_pool": Fraction(1, 10),
        "investor": Fraction(3, 16),
    }
    assert table.effective_pre_money.rounded == Decimal("7600000.00")
    assert result.investor_fraction.exact == Fraction(1, 5)


def test_an_unissued_pool_already_at_target_needs_no_new_shares() -> None:
    """With 2M of the 10M unissued: P = 0, p = $0.80, N = 2.5M, T = 12.5M; pool 16%, holders 64%, investor 20%."""
    result = pool(**{**POOL_EXAMPLE, "unissued_pool_shares": 2_000_000})

    for table in (result.pool_in_pre_money, result.pool_in_post_money):
        assert table.pool_already_large_enough is True
        assert table.new_pool_shares.exact == 0
        assert table.price_per_share.exact == Fraction(4, 5)
        assert table.investor_shares.exact == 2_500_000
        assert table.total_shares.exact == 12_500_000
        assert _ownership(table) == {
            "existing_holders": Fraction(16, 25),
            "option_pool": Fraction(4, 25),
            "investor": Fraction(1, 5),
        }


def test_an_unissued_pool_exactly_at_target_counts_as_large_enough() -> None:
    """With 1.25M unissued the needed pool is exactly 0 in both timings: P = 0 and the pool counts as large enough."""
    result = pool(**{**POOL_EXAMPLE, "unissued_pool_shares": 1_250_000})

    before = result.pool_in_pre_money
    assert before.new_pool_shares.exact == 0
    assert before.pool_already_large_enough is True
    after = result.pool_in_post_money
    assert after.new_pool_shares.exact == 0
    assert after.pool_already_large_enough is True


def test_money_rows_add_up_to_the_rounded_post_money() -> None:
    """Post-money pool values are $7.6M + $1,066,666.67 + $2M: the cents land on the row with the largest remainder."""
    table = pool(**POOL_EXAMPLE).pool_in_post_money

    values = [row.value.rounded for row in table.rows]
    assert values == [Decimal("7600000.00"), Decimal("1066666.67"), Decimal("2000000.00")]
    assert sum(values) == table.post_money.rounded == Decimal("10666666.67")


def test_whole_shares_round_down_and_report_the_cash_left_over() -> None:
    """whole_shares floors P and N at the exact price; the cash that did not buy a whole share is reported."""
    result = pool(**POOL_EXAMPLE, share_rounding="whole_shares")

    for table in (result.pool_in_pre_money, result.pool_in_post_money):
        for quantity in (table.new_pool_shares, table.investor_shares, table.total_shares):
            assert quantity.exact.denominator == 1
        assert 0 <= table.uninvested_cash.exact < table.price_per_share.exact
    assert result.pool_in_pre_money.new_pool_shares.exact == 857_142
    assert result.pool_in_pre_money.investor_shares.exact == 2_714_285
    # $2M at $4,000,000/5,428,571 a share buys 2,714,285 whole shares; the rest is $2,000,000/5,428,571 = $0.37.
    assert result.pool_in_pre_money.uninvested_cash.exact == Fraction(2_000_000, 5_428_571)
    assert result.pool_in_pre_money.uninvested_cash.rounded == Decimal("0.37")
    assert result.pool_in_post_money.uninvested_cash.exact == 0
    assert {item.key: item.setting for item in result.assumptions}["share_rounding"] == "whole_shares"


def test_pool_timing_names_the_deal_and_both_are_worked() -> None:
    """--pool-timing only picks the deal; both tables are always present and their assumptions say which."""
    result = pool(**POOL_EXAMPLE, pool_timing="post_money")

    assert result.pool_in_pre_money.timing == "pre_money"
    assert result.pool_in_post_money.timing == "post_money"
    assert {item.key: item.setting for item in result.assumptions}["pool_timing"] == "post_money"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        (
            {"target_pool_percent": "80"},
            "target_pool_percent must be below pre_money / (pre_money + investment) = 80.0000%",
        ),
        ({"target_pool_percent": "95"}, "a larger pool leaves no positive share price"),
        ({"target_pool_percent": "85", "pool_timing": "post_money"}, "share price in the pre-money timing"),
        ({"unissued_pool_shares": 10_000_000}, "unissued_pool_shares must be below fully_diluted_shares"),
        ({"fully_diluted_shares": 0}, "greater than 0"),
        ({"investment": "0"}, "greater than 0"),
        ({"target_pool_percent": "0"}, "greater than 0"),
        ({"unissued_pool_shares": -1}, "greater than or equal to 0"),
        ({"pre_money": "NaN"}, "finite number"),
        ({"pool_timing": "sometime"}, "'pre_money' or 'post_money'"),
        ({"surprise": 1}, "Extra inputs are not permitted"),
    ],
)
def test_inputs_with_no_positive_price_are_refused(changes: dict[str, object], message: str) -> None:
    """t >= 1 - r, every share unissued, non-positive amounts and unknown fields are refused with a clean message."""
    with pytest.raises(ValidationError) as caught:
        PoolInput.model_validate({**POOL_EXAMPLE, **changes})

    assert message in str(caught.value)


@pytest.mark.parametrize("field", ["fully_diluted_shares", "unissued_pool_shares"])
@pytest.mark.parametrize("value", [True, 1e6, "1000000"], ids=["bool", "float", "string"])
def test_share_counts_must_be_ints(field: str, value: object) -> None:
    """A bool, a float or a numeric string is refused as a share count, never read as the number it looks like."""
    with pytest.raises(ValidationError) as caught:
        PoolInput.model_validate({**POOL_EXAMPLE, field: value})

    assert "Input should be a valid integer" in str(caught.value)


@pytest.mark.parametrize("field", ["fully_diluted_shares", "unissued_pool_shares"])
def test_an_int_share_count_is_accepted(field: str) -> None:
    """The same count as a real int is taken as given."""
    count = 1_000_000

    assert getattr(PoolInput.model_validate({**POOL_EXAMPLE, field: count}), field) == count


def _random_inputs(rng: random.Random) -> dict[str, object]:
    """A random deal whose target pool stays below the holders' post-round share (so a price exists)."""
    fully_diluted = rng.randint(1, 10**8)
    pre_money = rng.randint(1, 10**9)
    investment = rng.randint(1, 10**9)
    holders_share = Fraction(pre_money, pre_money + investment)
    ceiling = max(1, int(holders_share * 10_000) - 1)
    return {
        "fully_diluted_shares": fully_diluted,
        "unissued_pool_shares": rng.randint(0, fully_diluted - 1),
        "pre_money": str(pre_money),
        "investment": str(investment),
        "target_pool_percent": str(Decimal(rng.randint(1, ceiling)) / Decimal(100)),
        "share_rounding": rng.choice(["exact", "whole_shares"]),
    }


def test_property_cap_tables_are_whole() -> None:
    """On random deals, both timings: no negative stake, ownership sums to exactly 1, money rows sum to the total."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        inputs = _random_inputs(rng)
        try:
            result = pool(**inputs)
        except ValidationError:
            continue  # the target rounded onto the holders' share: a refusal, covered above

        for table in (result.pool_in_pre_money, result.pool_in_post_money):
            assert all(row.shares.exact >= 0 and row.ownership.exact >= 0 for row in table.rows)
            assert sum(row.ownership.exact for row in table.rows) == 1
            assert sum(row.shares.exact for row in table.rows) == table.total_shares.exact
            assert sum(row.value.rounded for row in table.rows) == table.post_money.rounded
            assert table.price_per_share.exact > 0
            assert 0 <= table.uninvested_cash.exact < table.price_per_share.exact
            investment = Fraction(int(str(inputs["investment"])))
            spent = table.investor_shares.exact * table.price_per_share.exact
            assert table.uninvested_cash.exact == investment - spent


def test_property_exact_pools_hit_the_target_and_the_price_is_fair() -> None:
    """Exact shares: a new pool lands the pool on t exactly, and with the pool pre-money T·p = V + I."""
    rng = random.Random(_SEED + 1)
    for _ in range(_CASES):
        inputs = {**_random_inputs(rng), "share_rounding": "exact"}
        try:
            result = pool(**inputs)
        except ValidationError:
            continue

        target = Fraction(Decimal(str(inputs["target_pool_percent"]))) / 100
        pre_money = Fraction(int(str(inputs["pre_money"])))
        investment = Fraction(int(str(inputs["investment"])))
        before = result.pool_in_pre_money
        assert before.total_shares.exact * before.price_per_share.exact == pre_money + investment
        assert before.effective_pre_money.exact <= pre_money
        for table in (before, result.pool_in_post_money):
            assert table.uninvested_cash.exact == 0
            if not table.pool_already_large_enough:
                assert _ownership(table)["option_pool"] == target
            else:
                assert table.new_pool_shares.exact == 0
                assert _ownership(table)["option_pool"] >= target
