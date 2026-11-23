"""Pydantic models of a fundraising ask checked against itself (``equity_calculator deal_check``).

A founder's deck states some of: the raise (``investment``, I), a pre-money (V) or post-money valuation, the percent
the investors get, one holder group's percent after the round (the founders', say), an option pool target, the SAFEs
and notes outstanding, cash on hand, burn and revenue, a runway claim and the use-of-funds lines. The check works
what the round really does (reusing the ``pool`` and ``round`` scenarios when there is a pool top-up or a SAFE or
note) and returns each stated figure as ``consistent`` or a ``mismatch``, with flags for what a VC is likely to ask.

The first valuation given sets V: ``pre_money``; else ``post_money`` - I; else the stated percent x, V = I/x - I.
The others become checks. The nested ``RoundInput`` or ``PoolInput`` is built in this model's validator, so its
refusals surface here, naming the same fields; it is never stored as a field.

Like ``equity_dilution``'s builders, this module reuses another scenario's models (``equity_round``'s instruments and
``RoundInput``, ``equity_pool``'s ``PoolInput`` and their results), which import only ``equity_common``, so no cycle.
``equity_calculator.deal_check`` works it; the arithmetic and each convention's source are in ``README.md``.
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
    PoolTiming,
    ShareCount,
    exactly_one,
)
from equity_calculator.schemas.equity_pool import PoolInput, PoolResult
from equity_calculator.schemas.equity_round import MAX_INSTRUMENTS, Instrument, RoundInput, RoundResult
from pydantic import BaseModel, Field, ValidationError, model_validator

__all__ = [
    "DEFAULT_DILUTION_BAND_PERCENT",
    "DEFAULT_RUNWAY_BAND_MONTHS",
    "DEFAULT_TOLERANCE_PERCENT",
    "DEFAULT_TOLERANCE_POINTS",
    "MAX_USE_OF_FUNDS_LINES",
    "CheckKey",
    "CheckVerdict",
    "DealCheck",
    "DealCheckInput",
    "DealCheckResult",
    "DealCheckScenario",
    "DealFlag",
    "DealMoneyLine",
    "DealPath",
    "DealVerdict",
    "FundsLine",
    "PreMoneyPart",
    "RunwayBasis",
    "RunwayRow",
    "deal_path",
    "deal_valuation",
    "nested_input",
    "unissued_shares",
]

DealCheckScenario = Literal["deal_check"]

# How the round is worked: ``plain`` (no pool top-up, no SAFE or note: I/(V + I) directly), ``pool`` (a pool
# top-up, the pool scenario) or ``round`` (SAFEs or notes converting, the round scenario).
DealPath = Literal["plain", "pool", "round"]

# One stated figure against the computed one: within the tolerance it is ``consistent``, else a ``mismatch``.
CheckVerdict = Literal["consistent", "mismatch"]

# Which stated figure a check is about: the post-money, the investors' percent, the holder group's percent after the
# round, the runway claim, or the use-of-funds lines' total.
CheckKey = Literal["post_money", "investor_percent", "holder_percent", "runway_months", "use_of_funds_total"]

# The whole check: a ``mismatch`` if any check is one, ``consistent`` if every check is, ``not_checked`` when no stated
# figure could be checked (none was stated, or a runway claim met revenue covering every burn given).
DealVerdict = Literal["consistent", "mismatch", "not_checked"]

# Facts and questions a VC is likely to raise. They never change a verdict; their plain words are in
# ``equity_calculator.layout_deal_check``.
DealFlag = Literal[
    "valuation_back_solved",
    "pool_in_pre_money_lowers_price",
    "pool_in_post_money_dilutes_investor",
    "pool_already_large_enough",
    "conversions_bought_by_pre_money",
    "discount_beat_cap",
    "note_interest_converts",
    "net_burn_not_positive",
    "current_burn_runway_longer",
    "runway_below_band",
    "dilution_above_band",
]

# What the pre-money pays for: the existing holders' shares, the unissued pool already there, the new pool, and the
# SAFE and note conversions.
PreMoneyPart = Literal["existing_holders", "existing_pool", "new_pool", "conversions"]

# Which burn a runway row uses: the planned figures after the raise, or today's.
RunwayBasis = Literal["planned", "current"]

# The list cap on use-of-funds lines; the worst case computes at once.
MAX_USE_OF_FUNDS_LINES = 20

# The defaults of the tolerances and the two benchmark bands; the runway plan reuses them (``equity_runway_plan``).
DEFAULT_TOLERANCE_POINTS = Decimal("0.5")
DEFAULT_TOLERANCE_PERCENT = Decimal("2")
DEFAULT_DILUTION_BAND_PERCENT = Decimal("25")
DEFAULT_RUNWAY_BAND_MONTHS = Decimal("18")
_TWO = 2
_FIVE = 5
_ZERO = Fraction(0)
_VALUE_ERROR_PREFIX = "Value error, "


class FundsLine(BaseModel):
    """One use-of-funds line: an ``amount`` in dollars or a ``percent`` of the raise, not both."""

    model_config = MODEL_CONFIG

    amount: BoundedDecimal | None = Field(default=None, gt=0)
    percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)

    @model_validator(mode="after")
    def _one_of_the_two(self) -> FundsLine:
        """Refuse a line with neither or both of an amount and a percent."""
        exactly_one(("amount", "percent"), (self.amount, self.percent))
        return self


def _terminating_decimal(value: Fraction) -> Decimal | None:
    """``value`` as an exact ``Decimal`` built from text (no context read), or ``None`` when it does not terminate."""
    denominator = value.denominator
    twos = fives = 0
    while denominator % _TWO == 0:
        denominator //= _TWO
        twos += 1
    while denominator % _FIVE == 0:
        denominator //= _FIVE
        fives += 1
    if denominator != 1:
        return None

    places = max(twos, fives)
    scaled = value * 10**places
    return Decimal(f"{scaled.numerator}E-{places}")


def deal_valuation(inputs: DealCheckInput) -> tuple[Fraction, Literal["pre_money", "post_money", "percent"]]:
    """(V, which figure set it): ``pre_money``, else ``post_money`` - I, else I/x - I from the stated percent."""
    investment = Fraction(inputs.investment)
    if inputs.pre_money is not None:
        return Fraction(inputs.pre_money), "pre_money"
    if inputs.post_money is not None:
        return Fraction(inputs.post_money) - investment, "post_money"
    if inputs.stated_investor_percent is None:
        raise ValueError("give pre_money, post_money or stated_investor_percent (the round needs a valuation)")

    return investment * ONE_HUNDRED / Fraction(inputs.stated_investor_percent) - investment, "percent"


def deal_path(inputs: DealCheckInput) -> DealPath:
    """``round`` with any SAFE or note, ``pool`` with a pool top-up and no instruments, else ``plain``."""
    if inputs.instruments:
        return "round"
    if inputs.target_pool_percent > 0:
        return "pool"

    return "plain"


def unissued_shares(inputs: DealCheckInput) -> int:
    """U: ``unissued_pool_shares``, or ``unissued_pool_percent`` of FD (a whole number, as the validator checks)."""
    if inputs.unissued_pool_percent is None or inputs.fully_diluted_shares is None:
        return inputs.unissued_pool_shares

    return int(Fraction(inputs.unissued_pool_percent) * inputs.fully_diluted_shares / ONE_HUNDRED)


def _refused_pre_money(error: ValidationError) -> str | None:
    """The nested model's reason for refusing ``pre_money``, or ``None`` when it refused something else."""
    for failure in error.errors(include_url=False):
        if failure["loc"][:1] == ("pre_money",):
            return str(failure["msg"]).removeprefix(_VALUE_ERROR_PREFIX)

    return None


def nested_input(inputs: DealCheckInput) -> RoundInput | PoolInput | None:
    """The ``RoundInput`` or ``PoolInput`` the deal's path works, or ``None`` on the plain path.

    Raises ``ValueError`` (naming fields) when the pre-money came out as a fraction no decimal holds exactly or one the
    nested model refuses as a pre-money (named by the figure it was worked from, not ``pre_money``), or when the nested
    model refuses the inputs; built in the validator, so compute only rebuilds a known-valid input.
    """
    path = deal_path(inputs)
    if path == "plain":
        return None

    valuation, source = deal_valuation(inputs)
    pre_money = _terminating_decimal(valuation)
    given = "post_money" if source == "post_money" else "stated_investor_percent"
    if pre_money is None:
        raise ValueError(
            f"the pre-money worked from {given} is {valuation}, which no decimal holds exactly: give pre_money to "
            "convert SAFEs and notes or to top up the pool"
        )
    fields: dict[str, object] = {
        "fully_diluted_shares": inputs.fully_diluted_shares,
        "unissued_pool_shares": unissued_shares(inputs),
        "pre_money": pre_money,
        "investment": inputs.investment,
        "target_pool_percent": inputs.target_pool_percent,
        "pool_timing": inputs.pool_timing,
    }
    try:
        if path == "round":
            return RoundInput.model_validate({**fields, "instruments": inputs.instruments})
        return PoolInput.model_validate(fields)
    except ValidationError as error:
        reason = None if source == "pre_money" else _refused_pre_money(error)
        if reason is None:
            raise
        raise ValueError(
            f"the pre-money worked from {given} is {pre_money}, which the calculator does not take as a pre-money "
            f"({reason}): give pre_money"
        ) from None


class DealCheckInput(BaseModel):
    """A fundraising ask as a deck states it, plus the cap-table facts the check needs; see the module docstring.

    Percent fields take percent points (``20`` is 20%). ``fully_diluted_shares`` (FD) counts every share before the
    round, the unissued pool (U: ``unissued_pool_shares``, or ``unissued_pool_percent`` of FD) included and the SAFEs
    and notes excluded; it is needed only to convert SAFEs and notes or to top up the pool. One group's stake before
    the round is ``holder_percent`` of FD or ``holder_shares`` of it; ``stated_holder_percent`` is the deck's figure
    for it after. Runway takes the planned and/or current monthly
    gross burn, each with its revenue. The tolerances say how far a stated figure may sit from the computed one; the
    two bands raise a benchmark question, never an error.
    """

    model_config = MODEL_CONFIG

    scenario: DealCheckScenario = "deal_check"
    investment: BoundedDecimal = Field(gt=0)
    pre_money: BoundedDecimal | None = Field(default=None, gt=0)
    post_money: BoundedDecimal | None = Field(default=None, gt=0)
    stated_investor_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    fully_diluted_shares: ShareCount | None = Field(default=None, gt=0)
    unissued_pool_shares: ShareCount = Field(default=0, ge=0)
    unissued_pool_percent: BoundedDecimal | None = Field(default=None, ge=0, lt=WHOLE_PERCENT)
    target_pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)
    pool_timing: PoolTiming = "pre_money"
    instruments: tuple[Instrument, ...] = Field(default=(), max_length=MAX_INSTRUMENTS)
    holder_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)
    holder_shares: ShareCount | None = Field(default=None, gt=0)
    stated_holder_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    cash_on_hand: BoundedDecimal = Field(default=Decimal(0), ge=0)
    planned_monthly_gross_burn: BoundedDecimal | None = Field(default=None, gt=0)
    planned_monthly_revenue: BoundedDecimal | None = Field(default=None, ge=0)
    current_monthly_gross_burn: BoundedDecimal | None = Field(default=None, gt=0)
    current_monthly_revenue: BoundedDecimal | None = Field(default=None, ge=0)
    stated_runway_months: BoundedDecimal | None = Field(default=None, gt=0)
    use_of_funds: tuple[FundsLine, ...] = Field(default=(), max_length=MAX_USE_OF_FUNDS_LINES)
    tolerance_points: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_POINTS, ge=0, lt=WHOLE_PERCENT)
    tolerance_percent: BoundedDecimal = Field(default=DEFAULT_TOLERANCE_PERCENT, ge=0, lt=WHOLE_PERCENT)
    dilution_band_percent: BoundedDecimal = Field(default=DEFAULT_DILUTION_BAND_PERCENT, gt=0, lt=WHOLE_PERCENT)
    runway_band_months: BoundedDecimal = Field(default=DEFAULT_RUNWAY_BAND_MONTHS, gt=0)

    @model_validator(mode="after")
    def _deal_can_be_checked(self) -> DealCheckInput:
        """Refuse a deal with no valuation, a valuation of zero or less, or inputs that only make sense together."""
        valuation, source = deal_valuation(self)
        if valuation <= _ZERO:
            raise ValueError("post_money must be above investment (the pre-money would be zero or less)")
        if source == "percent" and self.pool_timing == "post_money":
            # The value is written in words: the command line turns every field name in a message into its flag.
            raise ValueError(
                "a stated_investor_percent with no valuation needs the pool counted in the pre-money: leave "
                "pool_timing at its default"
            )
        needs_shares = bool(self.instruments) or self.target_pool_percent > 0
        if self.fully_diluted_shares is None and needs_shares:
            raise ValueError("fully_diluted_shares is needed to convert SAFEs and notes or to top up the pool")
        self._share_rules()
        self._burn_rules()
        if len({line.amount is None for line in self.use_of_funds}) > 1:
            raise ValueError("give every use_of_funds line as an amount or every one as a percent, not a mix")

        nested_input(self)
        return self

    def _share_rules(self) -> None:
        """Refuse a pool or holder group given twice, without FD, not whole, or larger than the shares there are."""
        if self.unissued_pool_percent is not None and self.unissued_pool_shares > 0:
            raise ValueError("give unissued_pool_shares or unissued_pool_percent, not both")
        if self.holder_percent is not None and self.holder_shares is not None:
            raise ValueError("give holder_percent or holder_shares, not both")
        if self.stated_holder_percent is not None and self.holder_percent is None and self.holder_shares is None:
            raise ValueError(
                "stated_holder_percent needs holder_percent or holder_shares (the group's share before the round)"
            )
        fully_diluted = self.fully_diluted_shares
        if fully_diluted is None:
            needing = (
                ("unissued_pool_shares", self.unissued_pool_shares or None),
                ("unissued_pool_percent", self.unissued_pool_percent),
                ("holder_shares", self.holder_shares),
            )
            for name, value in needing:
                if value is not None:
                    raise ValueError(f"{name} needs fully_diluted_shares")
            return

        if self.unissued_pool_percent is not None:
            pool = Fraction(self.unissued_pool_percent) * fully_diluted / ONE_HUNDRED
            if pool.denominator != 1:
                raise ValueError(
                    "unissued_pool_percent of fully_diluted_shares is not a whole number of shares: give "
                    "unissued_pool_shares"
                )
        elif self.unissued_pool_shares >= fully_diluted:
            raise ValueError("unissued_pool_shares must be below fully_diluted_shares (someone must hold a share)")
        held = fully_diluted - unissued_shares(self)
        if self.holder_shares is not None and self.holder_shares > held:
            raise ValueError("holder_shares is more than the fully_diluted_shares held outside the unissued pool")
        if self.holder_percent is not None and Fraction(self.holder_percent) * fully_diluted / ONE_HUNDRED > held:
            raise ValueError(
                "holder_percent is more than the share of fully_diluted_shares held outside the unissued pool: give "
                "the group's share of every fully diluted share, the unissued pool counted"
            )

    def _burn_rules(self) -> None:
        """Refuse a revenue without its burn, or a runway claim with no burn to check it against."""
        if self.planned_monthly_revenue is not None and self.planned_monthly_gross_burn is None:
            raise ValueError("planned_monthly_revenue needs planned_monthly_gross_burn")
        if self.current_monthly_revenue is not None and self.current_monthly_gross_burn is None:
            raise ValueError("current_monthly_revenue needs current_monthly_gross_burn")
        no_burn = self.planned_monthly_gross_burn is None and self.current_monthly_gross_burn is None
        if self.stated_runway_months is not None and no_burn:
            raise ValueError(
                "stated_runway_months needs planned_monthly_gross_burn or current_monthly_gross_burn to check it"
            )


class DealCheck(BaseModel):
    """One stated figure checked: what the deck says, what the calculator gives, computed - stated, the verdict."""

    model_config = MODEL_CONFIG

    key: CheckKey
    stated: EquityQuantity
    computed: EquityQuantity
    difference: EquityQuantity
    verdict: CheckVerdict


class DealMoneyLine(BaseModel):
    """One part of the pre-money: what it pays for and how much, split to the cent so the parts add up to V."""

    model_config = MODEL_CONFIG

    part: PreMoneyPart
    value: EquityQuantity


class RunwayRow(BaseModel):
    """Months of runway on one burn: net burn = gross - revenue; runway = (cash + I)/burn (net: none at or below 0)."""

    model_config = MODEL_CONFIG

    basis: RunwayBasis
    gross_burn: EquityQuantity
    revenue: EquityQuantity
    net_burn: EquityQuantity
    gross_runway: EquityQuantity
    net_runway: EquityQuantity | None = None


class DealCheckResult(BaseModel):
    """The ask checked: what the round does, runway, use of funds, each stated figure's verdict, flags, the verdict.

    ``investor_ownership`` is the investor's cap-table share (I/(V + I) unless the pool is counted after the money);
    ``pre_round_stake_kept`` the share of their stake every pre-round share keeps; ``holder_ownership_after`` the
    named group's stake after the round; ``effective_pre_money`` the pre-round holders' shares (the unissued pool
    excluded) at the round price. ``round`` or ``pool`` is the nested scenario's whole result.
    """

    model_config = MODEL_CONFIG

    scenario: DealCheckScenario = "deal_check"
    inputs: DealCheckInput
    path: DealPath
    pre_money: EquityQuantity
    post_money: EquityQuantity
    effective_pre_money: EquityQuantity
    post_money_at_round_price: EquityQuantity | None = None
    price_per_share: EquityQuantity | None = None
    headline_investor_fraction: EquityQuantity
    investor_ownership: EquityQuantity
    pre_round_stake_kept: EquityQuantity
    holder_ownership_after: EquityQuantity | None = None
    existing_holders_ownership: EquityQuantity | None = None
    conversions_ownership: EquityQuantity | None = None
    pool_ownership_after: EquityQuantity | None = None
    pre_money_split: tuple[DealMoneyLine, ...]
    runway: tuple[RunwayRow, ...]
    use_of_funds: tuple[EquityQuantity, ...]
    use_of_funds_total: EquityQuantity | None = None
    use_of_funds_percent_total: EquityQuantity | None = None
    checks: tuple[DealCheck, ...]
    flags: tuple[DealFlag, ...]
    verdict: DealVerdict
    round: RoundResult | None = None
    pool: PoolResult | None = None
    assumptions: tuple[EquityAssumption, ...]
