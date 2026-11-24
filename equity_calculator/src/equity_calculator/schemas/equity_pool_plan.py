"""Pydantic models of a pool sized from the founder's hiring plan, beside the pool a term sheet asks for
(``equity_calculator pool_plan``).

A term sheet asks for an option pool of ``requested_pool_percent`` of the fully diluted shares after the round, created
in the pre-money (the option-pool shuffle). The founder gives the hires planned until the next round (``hires``: each
one's role, start month and grant, in shares or as a percent of the post-round fully diluted shares) and the month the
next round is expected (``next_round_month``). The grants of the hires starting on or before that month set the pool
the plan needs; the result works the round both ways, at the plan's pool and at the requested one, with the requested
column less the plan's for every figure. It never says which pool to accept.

Like ``equity_deal_check``, this module reuses another scenario's models (``equity_pool``'s cap table and
``equity_round``'s pool-size check), which import only ``equity_common``, so there is no cycle.
``equity_calculator.pool_plan`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    ONE_HUNDRED,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    ShareCount,
    exactly_one,
    percent_text,
)
from equity_calculator.schemas.equity_pool import PoolCapTable
from equity_calculator.schemas.equity_round import refuse_pool_too_large
from pydantic import AfterValidator, BaseModel, Field, model_validator

__all__ = [
    "MAX_HIRES",
    "MAX_PLAN_MONTH",
    "ROLE_MAX_LENGTH",
    "GrantUnit",
    "PlannedHire",
    "PoolPlanDifference",
    "PoolPlanFlag",
    "PoolPlanInput",
    "PoolPlanResult",
    "PoolPlanScenario",
    "PoolPlanSide",
    "hires_by_next_round",
]

PoolPlanScenario = Literal["pool_plan"]

# How the plan's grants are given: every grant in shares, or every grant as a percent of the post-round fully diluted
# shares. A plan that mixes the two is refused (``grants_mixed_units``): a percent of shares not yet priced cannot be
# added to a count of shares without choosing a column to price it in.
GrantUnit = Literal["shares", "percent"]

# Facts the comparison turns up. They never change a number and never say which pool to accept; their plain words are
# in ``equity_calculator.layout_pool_plan``. ``no_hires_before_next_round``: no hire starts on or before the next
# round's month, so the plan needs no pool. ``hires_after_next_round_ignored``: at least one hire starts after it and
# is left out of the plan. ``plan_fits_current_pool``: the plan's grants fit in today's unissued pool, so the plan
# needs no top-up. ``requested_met_by_current_pool``: today's unissued pool already meets the requested percent, so the
# term sheet's pool needs no top-up either. ``requested_above_plan`` / ``requested_below_plan``: the requested percent
# is above or below the plan's.
PoolPlanFlag = Literal[
    "no_hires_before_next_round",
    "hires_after_next_round_ignored",
    "plan_fits_current_pool",
    "requested_met_by_current_pool",
    "requested_above_plan",
    "requested_below_plan",
]

# At most 40 hires, each starting within 120 months (ten years) of today; the next round is expected within the same.
MAX_HIRES = 40
MAX_PLAN_MONTH = 120
# A hire's role is a label of a few words: letters and digits in any script, spaces and a little punctuation, starting
# with a letter or a digit, so no role can read as a spreadsheet formula (=, +, -, @) or carry a control character.
ROLE_MAX_LENGTH = 40
_ROLE_PUNCTUATION = frozenset(" .,&/()'-+#")
_ROLE_CHARACTERS = "letters, digits, spaces and . , & / ( ) ' - + #"

# strict: a month count is a real int; 1.0 or "12" is refused, never read as one.
PlanMonth = Annotated[int, Field(strict=True, ge=0, le=MAX_PLAN_MONTH)]
NextRoundMonth = Annotated[int, Field(strict=True, ge=1, le=MAX_PLAN_MONTH)]


def _plain_role(value: str) -> str:
    """A hire's role, its outer spaces dropped: refused when empty, starting with anything but a letter or a digit,
    or holding a character other than letters, digits, spaces and a little punctuation."""
    text = value.strip()
    if not text:
        raise ValueError("a hire's role is empty: give it in a few words (Senior engineer)")
    if not text[0].isalnum():
        raise ValueError(f"a hire's role starts with a letter or a digit, got {text[0]!r}")
    for character in text:
        if not (character.isalnum() or character in _ROLE_PUNCTUATION):
            raise ValueError(f"a hire's role holds only {_ROLE_CHARACTERS}, got {character!r}")

    return text


HireRole = Annotated[str, Field(strict=True, min_length=1, max_length=ROLE_MAX_LENGTH), AfterValidator(_plain_role)]


class PlannedHire(BaseModel):
    """One planned hire: a role, the month they start (whole months from today, 0 for now) and the grant, as a share
    count (``grant_shares``) or as a percent of the fully diluted shares after this round (``grant_percent``), exactly
    one of the two."""

    model_config = MODEL_CONFIG

    role: HireRole
    start_month: PlanMonth
    grant_shares: ShareCount | None = Field(default=None, gt=0)
    grant_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)

    @model_validator(mode="after")
    def _one_grant(self) -> PlannedHire:
        """Refuse a hire with no grant or with both kinds."""
        exactly_one(("grant_shares", "grant_percent"), (self.grant_shares, self.grant_percent))
        return self

    @property
    def unit(self) -> GrantUnit:
        """How this hire's grant is given."""
        return "shares" if self.grant_shares is not None else "percent"


def hires_by_next_round(
    hires: Sequence[PlannedHire], next_round_month: int
) -> tuple[tuple[PlannedHire, ...], tuple[PlannedHire, ...]]:
    """(the hires starting on or before ``next_round_month``, the ones starting after it), each in the order given."""
    counted = tuple(hire for hire in hires if hire.start_month <= next_round_month)
    left_out = tuple(hire for hire in hires if hire.start_month > next_round_month)
    return counted, left_out


class PoolPlanInput(BaseModel):
    """A term sheet's requested pool set beside the pool the founder's hiring plan to the next round needs.

    ``fully_diluted_shares`` (FD) counts every pre-round share, granted options and the unissued pool
    (``unissued_pool_shares``, U, 0 for none) included; ``founder_shares``, when given, are the founders' own shares
    among them. ``pre_money`` (V) and ``investment`` (I) are dollars; ``requested_pool_percent`` is the term sheet's
    pool, the unissued pool after the round as a percent of every post-round share, created in the pre-money.
    ``hires`` lists the plan; the ones starting on or before ``next_round_month`` count.
    """

    model_config = MODEL_CONFIG

    scenario: PoolPlanScenario = "pool_plan"
    fully_diluted_shares: ShareCount = Field(gt=0)
    unissued_pool_shares: ShareCount = Field(ge=0)
    founder_shares: ShareCount | None = Field(default=None, gt=0)
    pre_money: BoundedDecimal = Field(gt=0)
    investment: BoundedDecimal = Field(gt=0)
    requested_pool_percent: BoundedDecimal = Field(gt=0, lt=WHOLE_PERCENT)
    next_round_month: NextRoundMonth
    hires: tuple[PlannedHire, ...] = Field(default=(), max_length=MAX_HIRES)

    @model_validator(mode="after")
    def _a_plan_that_prices(self) -> PoolPlanInput:
        """Refuse no hiring plan, a plan mixing shares and percents, a pool that leaves no price, or share counts that
        do not fit inside the fully diluted shares."""
        if not self.hires:
            raise ValueError(
                "no_hiring_plan_given: the plan's pool is the grants of each hire starting by the next round, so "
                "give every planned hire (role, start month, grant in shares or as a percent of the post-round fully "
                "diluted shares), from the founder"
            )
        if len({hire.unit for hire in self.hires}) > 1:
            raise ValueError(
                "grants_mixed_units: give every hire's grant as grant_shares, or every one as grant_percent (a "
                "percent of the post-round fully diluted shares), never some of each"
            )
        if self.unissued_pool_shares >= self.fully_diluted_shares:
            raise ValueError("unissued_pool_shares must be below fully_diluted_shares (someone must hold a share)")
        held = self.fully_diluted_shares - self.unissued_pool_shares
        if self.founder_shares is not None and self.founder_shares > held:
            raise ValueError(
                f"founder_shares must be at most fully_diluted_shares - unissued_pool_shares = {held:,}: the "
                "founders' shares are among the shares already held"
            )
        refuse_pool_too_large(
            self.pre_money,
            self.investment,
            self.requested_pool_percent,
            ("requested_pool_percent", "pre_money", "investment"),
        )
        counted, _ = hires_by_next_round(self.hires, self.next_round_month)
        percents = [hire.grant_percent for hire in counted if hire.grant_percent is not None]
        if percents:
            _refuse_percents_too_large(self.pre_money, self.investment, percents)

        return self


def _refuse_percents_too_large(pre_money: Decimal, investment: Decimal, percents: Sequence[Decimal]) -> None:
    """Refuse grant_percent values (of the hires counted) adding up to V/(V + I) or more: a pool that large leaves no
    positive share price."""
    pre = Fraction(pre_money)
    holders_share = pre / (pre + Fraction(investment))
    total = sum((Fraction(percent) for percent in percents), Fraction(0)) / ONE_HUNDRED
    if total >= holders_share:
        raise ValueError(
            f"the grant_percent values of each hire starting by next_round_month add up to {percent_text(total)}, "
            f"which must be below pre_money / (pre_money + investment) = {percent_text(holders_share)}: a larger pool "
            "leaves no positive share price"
        )


class PoolPlanSide(BaseModel):
    """The round worked at one pool (the plan's or the requested one), the pool counted in the pre-money.

    ``target_pool`` is the pool after the round as a share of every post-round share; ``grant_shares`` the shares the
    counted grants take in this column (their sum, or their percents of this column's total shares);
    ``pool_left_at_next_round`` the pool after the round less those grants (negative when the pool runs short before
    the next round); ``founders_ownership`` the founders' shares over the total, when ``founder_shares`` is given.
    """

    model_config = MODEL_CONFIG

    target_pool: EquityQuantity
    grant_shares: EquityQuantity
    pool_left_at_next_round: EquityQuantity
    founders_ownership: EquityQuantity | None
    cap_table: PoolCapTable


class PoolPlanDifference(BaseModel):
    """The requested column less the plan's, each exact and rounded once: negative where the requested pool gives the
    lower figure."""

    model_config = MODEL_CONFIG

    target_pool: EquityQuantity
    new_pool_shares: EquityQuantity
    price_per_share: EquityQuantity
    existing_holders_ownership: EquityQuantity
    option_pool_ownership: EquityQuantity
    founders_ownership: EquityQuantity | None
    pool_left_at_next_round: EquityQuantity
    effective_pre_money: EquityQuantity


class PoolPlanResult(BaseModel):
    """The plan's pool beside the requested one: the hires counted, both columns, the difference, flags, assumptions."""

    model_config = MODEL_CONFIG

    scenario: PoolPlanScenario = "pool_plan"
    inputs: PoolPlanInput
    grant_unit: GrantUnit
    hires_counted: int
    hires_left_out: int
    investor_fraction: EquityQuantity
    plan: PoolPlanSide
    requested: PoolPlanSide
    requested_minus_plan: PoolPlanDifference
    flags: tuple[PoolPlanFlag, ...]
    assumptions: tuple[EquityAssumption, ...]
