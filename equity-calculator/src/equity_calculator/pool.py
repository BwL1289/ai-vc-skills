"""The option-pool shuffle: what topping the option pool up in a priced round does to the price and the cap table.

With FD fully diluted shares before the round (the unissued pool U included), pre-money V, investment I, the
investor's share r = I/(V + I) and a target pool t of the post-round shares:

- pool in the pre-money (the usual term sheet): the new pool P is created before the round, inside V, so the price
  is p = V/(FD + P) and only the existing holders pay for it. P = (t·FD - (1 - r)·U)/(1 - r - t), which gives
  p = (V - t(V + I))/(FD - U). When the unissued pool already meets the target (P <= 0), P = 0 and p = V/FD.
- pool in the post-money (the comparison): the price is p = V/FD, the investor buys N = I/p, then the pool is topped
  up after the round, P = max(0, (t(FD + N) - U)/(1 - t)), diluting everyone.

Either way N = I/p and T = FD + P + N; the existing holders keep FD - U shares, the pool is U + P. The effective
pre-money is what the existing holders' shares are worth at the round price, (FD - U)·p.
"""

from __future__ import annotations

import math
from fractions import Fraction

from equity_calculator.assumptions import pool_assumptions
from equity_calculator.exact import ONE, ZERO, fraction, from_percent, money_split, quantity
from equity_calculator.schemas.equity import CapTableGroup, CapTableRow, PoolCapTable, PoolInput, PoolResult, PoolTiming


def _whole(shares: Fraction, inputs: PoolInput) -> Fraction:
    """``shares`` rounded down to a whole share in ``whole_shares`` mode; unchanged in ``exact`` mode."""
    if inputs.share_rounding == "whole_shares":
        return Fraction(math.floor(shares))

    return shares


def _pool_in_pre_money(inputs: PoolInput) -> tuple[Fraction, Fraction, Fraction, bool]:
    """(new pool P, price p, investor shares N, pool already large enough) with the pool inside the pre-money."""
    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    pre_money = fraction(inputs.pre_money)
    investment = fraction(inputs.investment)
    target = from_percent(inputs.target_pool_percent)
    investor_share = investment / (pre_money + investment)

    needed = (target * fully_diluted - (ONE - investor_share) * unissued) / (ONE - investor_share - target)
    already_large_enough = needed <= ZERO
    new_pool = _whole(max(ZERO, needed), inputs)
    price = pre_money / (fully_diluted + new_pool)

    return new_pool, price, _whole(investment / price, inputs), already_large_enough


def _pool_in_post_money(inputs: PoolInput) -> tuple[Fraction, Fraction, Fraction, bool]:
    """(new pool P, price p, investor shares N, pool already large enough) with the pool added after the round."""
    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    target = from_percent(inputs.target_pool_percent)
    price = fraction(inputs.pre_money) / fully_diluted
    investor_shares = _whole(fraction(inputs.investment) / price, inputs)

    needed = (target * (fully_diluted + investor_shares) - unissued) / (ONE - target)
    already_large_enough = needed <= ZERO

    return _whole(max(ZERO, needed), inputs), price, investor_shares, already_large_enough


def _cap_table(
    inputs: PoolInput,
    timing: PoolTiming,
    worked: tuple[Fraction, Fraction, Fraction, bool],
) -> PoolCapTable:
    """The post-round cap table for one pool timing, from its new pool, price and investor shares."""
    new_pool, price, investor_shares, already_large_enough = worked
    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    total = fully_diluted + new_pool + investor_shares
    groups: tuple[tuple[CapTableGroup, Fraction], ...] = (
        ("existing_holders", fully_diluted - unissued),
        ("option_pool", unissued + new_pool),
        ("investor", investor_shares),
    )
    values = money_split([shares * price for _, shares in groups])

    rows = tuple(
        CapTableRow(
            group=group,
            shares=quantity("shares", shares),
            ownership=quantity("fraction", shares / total),
            value=value,
        )
        for (group, shares), value in zip(groups, values, strict=True)
    )

    return PoolCapTable(
        timing=timing,
        new_pool_shares=quantity("shares", new_pool),
        price_per_share=quantity("price", price),
        investor_shares=quantity("shares", investor_shares),
        total_shares=quantity("shares", total),
        rows=rows,
        post_money=quantity("money", total * price),
        effective_pre_money=quantity("money", (fully_diluted - unissued) * price),
        uninvested_cash=quantity("money", fraction(inputs.investment) - investor_shares * price),
        pool_already_large_enough=already_large_enough,
    )


def compute_pool(inputs: PoolInput) -> PoolResult:
    """The option-pool shuffle worked both ways, exactly; ``inputs.pool_timing`` names which one is the deal."""
    pre_money = fraction(inputs.pre_money)
    investment = fraction(inputs.investment)

    return PoolResult(
        inputs=inputs,
        investor_fraction=quantity("fraction", investment / (pre_money + investment)),
        pool_in_pre_money=_cap_table(inputs, "pre_money", _pool_in_pre_money(inputs)),
        pool_in_post_money=_cap_table(inputs, "post_money", _pool_in_post_money(inputs)),
        assumptions=pool_assumptions(inputs),
    )
