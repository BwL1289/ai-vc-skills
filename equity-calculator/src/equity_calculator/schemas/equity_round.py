"""Pydantic models of converting instruments in a priced round (``equity-calculator round``).

A round converts every SAFE and note at once, together with the new investor and the option pool target. SAFEs are
Y Combinator's post-money SAFE: a valuation cap (``valuation_cap``, post-money), a discount, both, or neither when the
SAFE is an MFN SAFE that took no terms. A note has a principal, an interest rate and how long it ran (whole months,
or an issue and a conversion date with a day count), and converts with its accrued interest at the lower of its cap
price (a pre-money cap on the fully diluted pre-round shares) and its discount price. Pre-money SAFEs are not
supported: YC publishes no current pre-money form, and its post-money user guide works one pre-money Safe Price
only as an example, not as a form's definitions.

``equity_calculator.round`` works the round; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from datetime import date
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
    PoolTiming,
    ShareCount,
    percent_text,
)
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "MAX_INSTRUMENTS",
    "MAX_NOTE_DAYS",
    "MAX_NOTE_MONTHS",
    "ConversionBasis",
    "ConversionRow",
    "DayCount",
    "NoteCompounding",
    "NoteKind",
    "NoteTerms",
    "RoundCapTableRow",
    "RoundHolder",
    "RoundInput",
    "RoundResult",
    "RoundScenario",
    "SafeKind",
    "SafeTerms",
    "StubRule",
]

RoundScenario = Literal["round"]
SafeKind = Literal["safe"]
NoteKind = Literal["note"]

# How a note's interest grows: ``annual`` compounding (the default) or ``monthly``; ``simple`` on the principal only.
NoteCompounding = Literal["simple", "annual", "monthly"]

# The part of a compounding period left at conversion (18 months compounded yearly leaves half a year).
# ``fractional_power`` (the default): the growth factor is raised to the fractional number of periods (approximate,
# 50 digits). ``simple``: whole periods compound, the stub earns simple interest on the grown amount (exact).
# A whole number of periods leaves no stub, so both rules then compound exactly.
StubRule = Literal["simple", "fractional_power"]

# Days per year when a note runs between dates: ``actual_365`` (the default) or ``actual_360``.
DayCount = Literal["actual_365", "actual_360"]

# Which price an instrument converted at: its cap price, its discount price, or the round's own price.
ConversionBasis = Literal["cap", "discount", "round_price"]

# A row of the post-round cap table: the existing holders, one row per SAFE or note, the option pool, the investor.
RoundHolder = Literal["existing_holders", "safe", "note", "option_pool", "investor"]

# The list caps: at most 50 instruments in one round, and a note runs at most 600 months (50 years),
# or 18,262 days between its dates (50 years of 365.25 days). The worst case of each computes in under a second.
MAX_INSTRUMENTS = 50
MAX_NOTE_MONTHS = 600
MAX_NOTE_DAYS = 18_262

# strict: a flag is a real bool; "yes" or 1 is refused, never read as one.
StrictFlag = Annotated[bool, Field(strict=True)]


class SafeTerms(BaseModel):
    """One post-money SAFE: the amount paid, its post-money valuation cap and its discount (either, both, or MFN)."""

    model_config = MODEL_CONFIG

    kind: SafeKind = "safe"
    purchase_amount: BoundedDecimal = Field(gt=0)
    valuation_cap: BoundedDecimal | None = Field(default=None, gt=0)
    discount_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    # An MFN SAFE converts on the terms it took from a later instrument, given here as its cap and discount;
    # with neither it converts at the round price. False is the plain SAFE, not a missing answer.
    mfn: StrictFlag = False

    @model_validator(mode="after")
    def _terms_named(self) -> SafeTerms:
        """Refuse a plain SAFE with no cap and no discount, or one paying at least its own post-money cap."""
        if not self.mfn and self.valuation_cap is None and self.discount_percent is None:
            raise ValueError(
                "a SAFE needs valuation_cap or discount_percent (an MFN SAFE that took no terms, mfn, converts at "
                "the round price)"
            )
        if self.valuation_cap is not None and self.purchase_amount >= self.valuation_cap:
            raise ValueError("purchase_amount must be below valuation_cap (the SAFE would own the whole company)")

        return self


class NoteTerms(BaseModel):
    """One convertible note: principal, rate, how long it ran, and its pre-money cap and discount (if any)."""

    model_config = MODEL_CONFIG

    kind: NoteKind = "note"
    principal: BoundedDecimal = Field(gt=0)
    interest_rate_percent: BoundedDecimal = Field(ge=0, lt=WHOLE_PERCENT)
    # Yearly compounding with a fractional-power stub unless the note says otherwise (the default).
    compounding: NoteCompounding = "annual"
    stub_rule: StubRule = "fractional_power"
    months_outstanding: Annotated[int, Field(strict=True, ge=0, le=MAX_NOTE_MONTHS)] | None = None
    issue_date: date | None = None
    conversion_date: date | None = None
    day_count: DayCount = "actual_365"
    valuation_cap: BoundedDecimal | None = Field(default=None, gt=0)
    discount_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    # True when the accrued interest is paid in cash at the round, so only the principal converts.
    interest_paid_in_cash: StrictFlag = False

    @model_validator(mode="after")
    def _one_term(self) -> NoteTerms:
        """Refuse a note that gives both or neither of months_outstanding and the two dates, or dates out of order."""
        dated = self.issue_date is not None or self.conversion_date is not None
        if (self.months_outstanding is None) == (not dated):
            raise ValueError("give months_outstanding, or issue_date and conversion_date, not both and not neither")
        if self.months_outstanding is not None:
            return self

        if self.issue_date is None or self.conversion_date is None:
            raise ValueError("issue_date and conversion_date go together")
        days = (self.conversion_date - self.issue_date).days
        if not 0 <= days <= MAX_NOTE_DAYS:
            raise ValueError(f"conversion_date must be 0 to {MAX_NOTE_DAYS:,} days after issue_date (got {days:,})")

        return self


Instrument = Annotated[SafeTerms | NoteTerms, Field(discriminator="kind")]


class RoundInput(BaseModel):
    """A priced round with its converting instruments: shares before, the money, the pool target, each SAFE or note.

    ``fully_diluted_shares`` (FD) counts every share before the round, the unissued pool (U) included and the SAFEs
    and notes excluded; ``pre_money`` (V) and ``investment`` (I) are the new money's terms. ``target_pool_percent``
    (t, default 0: no top-up) is the unissued pool's share after the round. Instruments convert in the order given.
    """

    model_config = MODEL_CONFIG

    scenario: RoundScenario = "round"
    fully_diluted_shares: ShareCount = Field(gt=0)
    unissued_pool_shares: ShareCount = Field(default=0, ge=0)
    pre_money: BoundedDecimal = Field(gt=0)
    investment: BoundedDecimal = Field(gt=0)
    target_pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)
    pool_timing: PoolTiming = "pre_money"
    instruments: tuple[Instrument, ...] = Field(min_length=1, max_length=MAX_INSTRUMENTS)

    @model_validator(mode="after")
    def _round_can_price(self) -> RoundInput:
        """Refuse what leaves no share price whatever the instruments do: no holder, too big a pool, caps over 100%."""
        if self.unissued_pool_shares >= self.fully_diluted_shares:
            raise ValueError("unissued_pool_shares must be below fully_diluted_shares (someone must hold a share)")

        pre_money = Fraction(self.pre_money)
        holders_share = pre_money / (pre_money + Fraction(self.investment))
        if Fraction(self.target_pool_percent) / ONE_HUNDRED >= holders_share:
            raise ValueError(
                "target_pool_percent must be below pre_money / (pre_money + investment) = "
                f"{percent_text(holders_share)}: a larger pool leaves no positive share price"
            )

        capped = sum(
            (
                Fraction(item.purchase_amount) / Fraction(item.valuation_cap)
                for item in self.instruments
                if isinstance(item, SafeTerms) and item.valuation_cap is not None
            ),
            Fraction(0),
        )
        if capped >= 1:
            raise ValueError(
                "the capped SAFEs' purchase_amount / valuation_cap add up to "
                f"{percent_text(capped)}: at their caps they would own the whole company"
            )

        return self


class ConversionRow(BaseModel):
    """One instrument converted: what converts, its cap and discount prices, the price it took, the shares it got.

    ``index`` is the instrument's place in ``inputs.instruments``, from 1. A note's ``accrued_interest`` is its
    amount owed (rounded to the cent) less its principal; ``interest_approximate`` marks a fractional-power stub.
    """

    model_config = MODEL_CONFIG

    index: int
    kind: SafeKind | NoteKind
    amount: EquityQuantity
    accrued_interest: EquityQuantity | None = None
    interest_approximate: bool = False
    converting_amount: EquityQuantity
    cap_price: EquityQuantity | None = None
    discount_price: EquityQuantity | None = None
    conversion_price: EquityQuantity
    basis: ConversionBasis
    shares: EquityQuantity


class RoundCapTableRow(BaseModel):
    """One holder's line in the post-round cap table (``instrument`` is the SAFE's or note's index, from 1)."""

    model_config = MODEL_CONFIG

    holder: RoundHolder
    instrument: int | None = None
    shares: EquityQuantity
    ownership: EquityQuantity
    value: EquityQuantity


class RoundResult(BaseModel):
    """The round worked: its price, YC's Company Capitalization, each conversion and the cap table after it.

    ``capped_safe_fraction`` is sigma, the capped SAFEs' purchase amount over cap added up (their share of the
    capitalization); ``passes`` counts the passes the conversion search took (at most one more than the instruments).
    """

    model_config = MODEL_CONFIG

    scenario: RoundScenario = "round"
    inputs: RoundInput
    price_per_share: EquityQuantity
    company_capitalization: EquityQuantity
    capped_safe_fraction: EquityQuantity
    new_pool_shares: EquityQuantity
    investor_shares: EquityQuantity
    total_shares: EquityQuantity
    post_money: EquityQuantity
    pool_already_large_enough: bool
    passes: int
    conversions: tuple[ConversionRow, ...]
    rows: tuple[RoundCapTableRow, ...]
    assumptions: tuple[EquityAssumption, ...]
