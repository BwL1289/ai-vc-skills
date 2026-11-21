"""Pydantic models of one holder's stake through a series of rounds (``equity_calculator dilution``).

Each round sells new shares to its investors and may create a new option pool. A holder who buys nothing in the
round keeps ``1 - n - p`` of their stake: ``n`` is the new investors' share of the company after the round and
``p`` the new pool's share after it, so the stake after round k is h_k = h_{k-1}·(1 - n_k - p_k). A round gives
``n`` as a percent (``investor_percent``) or from amounts (``pre_money`` V and ``investment`` I, n = I/(V + I)).

``equity_calculator.dilution`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    ONE_HUNDRED,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    exactly_one,
    percent_text,
)
from pydantic import BaseModel, Field, model_validator

__all__ = ["MAX_ROUNDS", "DilutionInput", "DilutionResult", "DilutionRound", "DilutionRow", "DilutionScenario"]

DilutionScenario = Literal["dilution"]

# The list cap: at most 20 rounds in one run; the worst case computes in under a second.
MAX_ROUNDS = 20

_ONE = Fraction(1)


class DilutionRound(BaseModel):
    """One round: the new investors' share after it (a percent, or from amounts) and the new pool's share."""

    model_config = MODEL_CONFIG

    investor_percent: BoundedDecimal | None = Field(default=None, ge=0, lt=WHOLE_PERCENT)
    pre_money: BoundedDecimal | None = Field(default=None, gt=0)
    investment: BoundedDecimal | None = Field(default=None, gt=0)
    # 0 is a round that creates no new pool, the natural neutral value: no pool is never "not yet known".
    pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)

    def investor_fraction(self) -> Fraction:
        """n: ``investor_percent`` as a fraction, or I/(V + I) from the amounts (exact)."""
        if self.investor_percent is not None:
            return Fraction(self.investor_percent) / ONE_HUNDRED
        if self.pre_money is None or self.investment is None:
            raise ValueError("give investor_percent, or pre_money and investment")

        investment = Fraction(self.investment)
        return investment / (Fraction(self.pre_money) + investment)

    @model_validator(mode="after")
    def _one_share_and_room_left(self) -> DilutionRound:
        """Refuse a round with no way, or two ways, to read n, or one that leaves the earlier holders nothing."""
        if (self.pre_money is None) != (self.investment is None):
            raise ValueError("give pre_money and investment together")

        # pre_money stands for the pair: the check above makes the two given together or not at all.
        exactly_one(("investor_percent", "pre_money with investment"), (self.investor_percent, self.pre_money))
        taken = self.investor_fraction() + Fraction(self.pool_percent) / ONE_HUNDRED
        if taken >= _ONE:
            raise ValueError(
                f"the new investors and pool_percent together take {percent_text(taken)} of the company: "
                "they must take less than 100%, or the earlier holders keep nothing"
            )

        return self


class DilutionInput(BaseModel):
    """One holder's stake before the first round and the rounds that follow, in order (none is allowed)."""

    model_config = MODEL_CONFIG

    scenario: DilutionScenario = "dilution"
    holder_percent: BoundedDecimal = Field(gt=0, le=WHOLE_PERCENT)
    rounds: tuple[DilutionRound, ...] = Field(max_length=MAX_ROUNDS)


class DilutionRow(BaseModel):
    """One round worked: n, p, the share kept, the holder's stake before and after, and the post-money if known."""

    model_config = MODEL_CONFIG

    index: int
    investor_share: EquityQuantity
    pool_share: EquityQuantity
    kept: EquityQuantity
    stake_before: EquityQuantity
    stake_after: EquityQuantity
    stake_lost: EquityQuantity
    # Only for a round given as amounts: V + I, and the holder's stake after the round times it.
    post_money: EquityQuantity | None = None
    holder_value: EquityQuantity | None = None


class DilutionResult(BaseModel):
    """The holder's stake through every round: h_k = h_{k-1}·(1 - n_k - p_k), and the final stake."""

    model_config = MODEL_CONFIG

    scenario: DilutionScenario = "dilution"
    inputs: DilutionInput
    initial_stake: EquityQuantity
    final_stake: EquityQuantity
    kept_overall: EquityQuantity
    rows: tuple[DilutionRow, ...]
    assumptions: tuple[EquityAssumption, ...]
