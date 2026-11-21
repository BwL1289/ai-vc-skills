"""One holder's dilution through a series of rounds: h_k = h_{k-1}·(1 - n_k - p_k), every step exact.

A holder who buys nothing in a round keeps ``1 - n - p`` of their stake, where ``n`` is the new investors' share of
the company after the round and ``p`` the new pool's share after it. For a round given as amounts the post-money
V + I and the holder's value at it follow.
"""

from __future__ import annotations

from equity_calculator.assumptions_holder import dilution_assumptions
from equity_calculator.exact import ONE, fraction, from_percent, quantity
from equity_calculator.schemas.equity_dilution import DilutionInput, DilutionResult, DilutionRow

__all__ = ["compute_dilution"]

# Rounds are numbered from 1, in the order given.
_ROUND_START = 1


def compute_dilution(inputs: DilutionInput) -> DilutionResult:
    """The holder's stake before and after every round, the share each round kept, and the final stake."""
    initial = from_percent(inputs.holder_percent)
    stake = initial
    rows: list[DilutionRow] = []
    for index, item in enumerate(inputs.rounds, start=_ROUND_START):
        investor = item.investor_fraction()
        pool = from_percent(item.pool_percent)
        kept = ONE - investor - pool
        after = stake * kept
        post_money = None
        if item.pre_money is not None and item.investment is not None:
            post_money = fraction(item.pre_money) + fraction(item.investment)

        rows.append(
            DilutionRow(
                index=index,
                investor_share=quantity("fraction", investor),
                pool_share=quantity("fraction", pool),
                kept=quantity("fraction", kept),
                stake_before=quantity("fraction", stake),
                stake_after=quantity("fraction", after),
                stake_lost=quantity("fraction", stake - after),
                post_money=None if post_money is None else quantity("money", post_money),
                holder_value=None if post_money is None else quantity("money", after * post_money),
            )
        )
        stake = after

    return DilutionResult(
        inputs=inputs,
        initial_stake=quantity("fraction", initial),
        final_stake=quantity("fraction", stake),
        kept_overall=quantity("fraction", stake / initial),
        rows=tuple(rows),
        assumptions=dilution_assumptions(inputs),
    )
