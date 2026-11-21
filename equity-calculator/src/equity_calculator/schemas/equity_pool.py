"""Pydantic models of the option-pool shuffle (``equity-calculator pool``): a priced round that tops the pool up.

Split out of ``equity_calculator.schemas.equity``, which re-exports every name here and keeps the tagged unions.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    ONE_HUNDRED,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    PoolTiming,
    ShareCount,
    ShareRounding,
    percent_text,
)
from pydantic import BaseModel, Field, model_validator

__all__ = ["CapTableGroup", "CapTableRow", "PoolCapTable", "PoolInput", "PoolResult", "PoolScenario"]

# The option-pool shuffle's tag, the discriminator of ``EquityInput`` and ``EquityResult``.
PoolScenario = Literal["pool"]

# Each row of a cap table. ``existing_holders`` the shares already issued (fully diluted minus the unissued pool);
# ``option_pool`` the unissued pool after the round, old and new; ``investor`` the round's new shares.
CapTableGroup = Literal["existing_holders", "option_pool", "investor"]


class PoolInput(BaseModel):
    """The option-pool shuffle: a priced round that tops the unissued pool up to ``target_pool_percent`` after it.

    ``fully_diluted_shares`` (FD) counts every pre-round share, the unissued pool (``unissued_pool_shares``, U)
    included; ``pre_money`` (V) and ``investment`` (I) are dollars. The target must stay below the existing holders'
    post-round share V/(V + I): above it the pre-money timing, always worked too, has no positive share price.
    """

    model_config = MODEL_CONFIG

    scenario: PoolScenario = "pool"
    fully_diluted_shares: ShareCount = Field(gt=0)
    unissued_pool_shares: ShareCount = Field(default=0, ge=0)
    pre_money: BoundedDecimal = Field(gt=0)
    investment: BoundedDecimal = Field(gt=0)
    target_pool_percent: BoundedDecimal = Field(gt=0, lt=WHOLE_PERCENT)
    pool_timing: PoolTiming = "pre_money"
    share_rounding: ShareRounding = "exact"

    @model_validator(mode="after")
    def _a_price_exists(self) -> PoolInput:
        """Refuse a pool at or above the holders' post-round share, or an unissued pool of every share."""
        if self.unissued_pool_shares >= self.fully_diluted_shares:
            raise ValueError("unissued_pool_shares must be below fully_diluted_shares (someone must hold a share)")

        pre_money = Fraction(self.pre_money)
        holders_share = pre_money / (pre_money + Fraction(self.investment))
        if Fraction(self.target_pool_percent) / ONE_HUNDRED >= holders_share:
            raise ValueError(
                "target_pool_percent must be below pre_money / (pre_money + investment) = "
                f"{percent_text(holders_share)}: a larger pool leaves no positive share price in the pre-money timing"
            )

        return self


class CapTableRow(BaseModel):
    """One group's line in a post-round cap table; ``value`` is its shares at the round price, split to the cent."""

    model_config = MODEL_CONFIG

    group: CapTableGroup
    shares: EquityQuantity
    ownership: EquityQuantity
    value: EquityQuantity


class PoolCapTable(BaseModel):
    """The round worked one way (pool counted pre-money or post-money): price, new shares, and who owns what.

    ``post_money`` is every post-round share at the round price (V + I with the pool in the pre-money; more, by the
    new pool's paper value, with the pool added after the round); ``effective_pre_money`` is (FD - U) at that price."""

    model_config = MODEL_CONFIG

    timing: PoolTiming
    new_pool_shares: EquityQuantity
    price_per_share: EquityQuantity
    investor_shares: EquityQuantity
    total_shares: EquityQuantity
    rows: tuple[CapTableRow, ...]
    post_money: EquityQuantity
    effective_pre_money: EquityQuantity
    uninvested_cash: EquityQuantity
    pool_already_large_enough: bool


class PoolResult(BaseModel):
    """The option-pool shuffle, worked both ways; ``inputs.pool_timing`` names the deal, the other is the comparison."""

    model_config = MODEL_CONFIG

    scenario: PoolScenario = "pool"
    inputs: PoolInput
    investor_fraction: EquityQuantity
    pool_in_pre_money: PoolCapTable
    pool_in_post_money: PoolCapTable
    assumptions: tuple[EquityAssumption, ...]
