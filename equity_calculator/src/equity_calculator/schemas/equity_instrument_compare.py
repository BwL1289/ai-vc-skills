"""Pydantic models of a priced round now set beside a convertible note now (``equity_calculator instrument_compare``).

A founder raising ``investment`` today can sell priced shares now (option A, the ``priced_*`` fields) or issue a
convertible note now (option B, the ``note_*`` fields) that converts at the next priced round. Both options lead to
the same next round, given as one or more alternatives for it (``next_rounds``: its pre-money, the amount it raises,
any pool top-up and its series' terms), each worked from today's cap table and never after the one before, and the
company is then sold for each of ``exit_amounts``. The result shows, side by
side, who owns what right after today's financing, after each next round, and who gets what at each exit, with
B - A for every holder group. It never says which option to take.

Today's cap table is given by holder group: ``founder_shares``, ``team_shares`` (the team's granted options and
common), ``unissued_pool_shares`` and the existing investors: ``existing_series`` (each a preferred class with its own
terms, the waterfall's ``PreferredClass``) and ``existing_instruments`` (SAFEs and notes outstanding, the round's
``SafeTerms`` and ``NoteTerms``), which convert at the first priced round: today's in option A, the next one in B.
A new series' liquidation terms are a ``SeriesTerms``: ``standard`` (1x, non-participating), or the multiple and the
participation the founder gives.

Like ``equity_deal_check``, this module reuses other scenarios' models (``equity_round``'s instruments and checks,
``equity_waterfall``'s class, rank and cap check), which import only ``equity_common``, so no cycle.
``equity_calculator.instrument_compare`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    PoolTiming,
    ShareCount,
)
from equity_calculator.schemas.equity_round import (
    MAX_NOTE_MONTHS,
    ConversionRow,
    Instrument,
    NoteCompounding,
    NoteTerms,
    StubRule,
    refuse_caps_over_whole,
    refuse_pool_too_large,
)
from equity_calculator.schemas.equity_waterfall import Participation, PreferredClass, Rank, refuse_cap_mismatch
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "MAX_EXISTING_INSTRUMENTS",
    "MAX_EXISTING_SERIES",
    "MAX_EXITS",
    "MAX_NEXT_ROUNDS",
    "STANDARD_MULTIPLE",
    "ExitComparison",
    "GroupPayout",
    "GroupStake",
    "HolderGroup",
    "InstrumentCompareInput",
    "InstrumentCompareResult",
    "InstrumentCompareScenario",
    "InstrumentFlag",
    "NextRound",
    "NextRoundComparison",
    "PoolAtExit",
    "SeriesTerms",
]

InstrumentCompareScenario = Literal["instrument_compare"]

# A line of the cap table by who holds it: the founders, the team (granted options and the team's common), the option
# pool (unissued), the existing investors (their series and their SAFEs and notes once converted), the new money
# (option A's priced-round investors; option B's note once it converts) and the next round's investors.
HolderGroup = Literal["founders", "team", "option_pool", "existing_investors", "new_money", "next_round_investors"]

# Who takes part in an exit as common: ``as_common`` counts every option-pool share as if granted and exercised (the
# same fully diluted basis as the ownership lines); ``left_out`` leaves the pool out, as unexercised options take
# nothing.
PoolAtExit = Literal["as_common", "left_out"]

# Facts the comparison turns up. They never change a number and never say which option to take; their plain words are
# in ``equity_calculator.layout_instrument_compare``. ``cap_below_round_price_now``: the note's cap price (cap / FD) is
# below option A's price per share today. ``note_converts_at_*``: in at least one next round, the price the note took.
# ``maturity_not_given`` / ``converts_after_maturity``: the note's maturity is unknown, or comes before the next round.
# ``next_round_below_priced_round_price``: a next round prices below option A's round today (a down round for A).
InstrumentFlag = Literal[
    "cap_below_round_price_now",
    "note_converts_at_cap",
    "note_converts_at_discount",
    "note_converts_at_round_price",
    "note_interest_converts",
    "maturity_not_given",
    "converts_after_maturity",
    "next_round_below_priced_round_price",
]

# The list caps. With every existing series and instrument, an exit has 6 + 4 classes plus option A's two new series
# (or B's note and next round), 12 in all: the waterfall's own cap (``equity_waterfall.MAX_CLASSES``).
MAX_EXISTING_SERIES = 6
MAX_EXISTING_INSTRUMENTS = 4
MAX_NEXT_ROUNDS = 4
MAX_EXITS = 6

# The multiple a ``standard`` series is owed: 1x what it invested, with no participation.
STANDARD_MULTIPLE = Decimal(1)

# strict: a flag is a real bool and a month count a real int; "yes", 1.0 or "12" is refused, never read as one.
StrictFlag = Annotated[bool, Field(strict=True)]
NoteMonths = Annotated[int, Field(strict=True, ge=0, le=MAX_NOTE_MONTHS)]
MaturityMonths = Annotated[int, Field(strict=True, ge=1, le=MAX_NOTE_MONTHS)]
# An exit: what the shareholders share, zero or more.
ExitAmount = Annotated[BoundedDecimal, Field(ge=0)]


class SeriesTerms(BaseModel):
    """A new preferred series' liquidation terms: ``standard`` (1x, non-participating), or the founder's own terms.

    ``standard`` sets the multiple to 1 and the participation to none, and only when the founder says the terms are
    standard; otherwise ``preference_multiple`` and ``participation`` are both given (a ``capped`` one with its
    ``cap_multiple``). ``rank`` is the seniority either way: 1 is paid first, equal ranks share pro rata, and it is 1
    when not given (every series side by side, the waterfall's neutral order).
    """

    model_config = MODEL_CONFIG

    standard: StrictFlag = False
    preference_multiple: BoundedDecimal | None = Field(default=None, ge=0)
    participation: Participation | None = None
    cap_multiple: BoundedDecimal | None = Field(default=None, gt=0)
    rank: Rank | None = None

    @model_validator(mode="after")
    def _standard_or_the_terms(self) -> SeriesTerms:
        """Refuse terms given beside ``standard``, terms missing without it, or a cap that does not fit them."""
        if self.standard:
            given = [
                name
                for name, value in (
                    ("preference_multiple", self.preference_multiple),
                    ("participation", self.participation),
                    ("cap_multiple", self.cap_multiple),
                )
                if value is not None
            ]
            if given:
                raise ValueError(
                    f"standard is 1x with no participation: give it alone (rank aside), not with {', '.join(given)}"
                )
            return self

        if self.preference_multiple is None or self.participation is None:
            raise ValueError(
                "give standard (only when the founder says the terms are standard: 1x, non-participating), or both "
                "preference_multiple and participation"
            )
        refuse_cap_mismatch(self.participation, self.cap_multiple, self.preference_multiple)
        return self


class NextRound(BaseModel):
    """One scenario for the next priced round, the same for both options: its pre-money valuation ``pre_money``, the
    amount it raises ``investment``, its pool top-up (``target_pool_percent`` of the shares after it, default 0: none;
    counted per ``pool_timing``, default the pre-money) and its series' ``preference``."""

    model_config = MODEL_CONFIG

    pre_money: BoundedDecimal = Field(gt=0)
    investment: BoundedDecimal = Field(gt=0)
    target_pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)
    pool_timing: PoolTiming = "pre_money"
    preference: SeriesTerms

    @model_validator(mode="after")
    def _round_can_price(self) -> NextRound:
        """Refuse a pool target that would take the whole pre-money (the round check of ``equity_round``)."""
        refuse_pool_too_large(self.pre_money, self.investment, self.target_pool_percent)
        return self


class InstrumentCompareInput(BaseModel):
    """The same raise two ways, the next round both lead to and the exits; see the module docstring.

    Percent fields take percent points (``20`` is 20%). Option A prices the raise now at ``priced_pre_money``, with
    any pool top-up (``priced_target_pool_percent``, counted per ``priced_pool_timing``) and its series' terms
    (``priced_preference``). Option B is a note for the same ``investment``: its cap (a pre-money cap over today's
    fully diluted shares) and discount, each optional; its interest rate and compounding, both required; and the
    months until it converts at the next round. ``note_maturity_months`` (optional) is only compared with those months:
    no repayment or conversion at maturity is modelled.
    """

    model_config = MODEL_CONFIG

    scenario: InstrumentCompareScenario = "instrument_compare"
    founder_shares: ShareCount = Field(gt=0)
    team_shares: ShareCount = Field(default=0, ge=0)
    unissued_pool_shares: ShareCount = Field(default=0, ge=0)
    existing_series: tuple[PreferredClass, ...] = Field(default=(), max_length=MAX_EXISTING_SERIES)
    existing_instruments: tuple[Instrument, ...] = Field(default=(), max_length=MAX_EXISTING_INSTRUMENTS)
    investment: BoundedDecimal = Field(gt=0)
    priced_pre_money: BoundedDecimal = Field(gt=0)
    priced_target_pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)
    priced_pool_timing: PoolTiming = "pre_money"
    priced_preference: SeriesTerms
    note_valuation_cap: BoundedDecimal | None = Field(default=None, gt=0)
    note_discount_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    note_interest_rate_percent: BoundedDecimal = Field(ge=0, lt=WHOLE_PERCENT)
    note_compounding: NoteCompounding
    note_stub_rule: StubRule = "fractional_power"
    note_months_to_conversion: NoteMonths
    note_maturity_months: MaturityMonths | None = None
    note_interest_paid_in_cash: StrictFlag = False
    next_rounds: tuple[NextRound, ...] = Field(default=(), max_length=MAX_NEXT_ROUNDS)
    exit_amounts: tuple[ExitAmount, ...] = Field(default=(), max_length=MAX_EXITS)
    pool_at_exit: PoolAtExit = "as_common"

    @model_validator(mode="after")
    def _comparison_can_run(self) -> InstrumentCompareInput:
        """Refuse a comparison with no next round or no exit, an existing note it cannot move, or a round with no
        price whatever happens (a pool target or capped SAFEs taking the whole company)."""
        if not self.next_rounds:
            raise ValueError(
                "no_next_round_given: option B's note converts only at a next priced round, so give at least one "
                "next_rounds scenario (that round's pre-money, raise and series terms, from the founder)"
            )
        if not self.exit_amounts:
            raise ValueError(
                "exit_amounts is empty: give at least one exit, what the company sells for after the next round"
            )
        for item in self.existing_instruments:
            if not isinstance(item, NoteTerms):
                continue
            if item.months_outstanding is None:
                raise ValueError(
                    "an existing note in existing_instruments gives months_outstanding as of today, not dates: "
                    "option A converts it today and option B at the next round"
                )
            if item.months_outstanding + self.note_months_to_conversion > MAX_NOTE_MONTHS:
                raise ValueError(
                    f"an existing note's months_outstanding plus note_months_to_conversion is over {MAX_NOTE_MONTHS} "
                    "months: option B converts it that much later"
                )
        refuse_pool_too_large(
            self.priced_pre_money,
            self.investment,
            self.priced_target_pool_percent,
            ("priced_target_pool_percent", "priced_pre_money", "investment"),
        )
        refuse_caps_over_whole(self.existing_instruments)
        return self


class GroupStake(BaseModel):
    """One holder group's shares and ownership under each option at one point, and the ownership B - A."""

    model_config = MODEL_CONFIG

    group: HolderGroup
    priced_shares: EquityQuantity
    note_shares: EquityQuantity
    priced: EquityQuantity
    note: EquityQuantity
    difference: EquityQuantity


class GroupPayout(BaseModel):
    """One holder group's payout at one exit under each option (cents by largest remainder within the option, so each
    option's payouts add up to the exit), and B - A of the exact payouts, rounded once."""

    model_config = MODEL_CONFIG

    group: HolderGroup
    priced: EquityQuantity
    note: EquityQuantity
    difference: EquityQuantity


class ExitComparison(BaseModel):
    """One exit after one next round: each group's payout both ways, the preferences paid, the founders' B - A."""

    model_config = MODEL_CONFIG

    exit_amount: EquityQuantity
    payouts: tuple[GroupPayout, ...]
    priced_preferences_paid: EquityQuantity
    note_preferences_paid: EquityQuantity
    founders_payout_difference: EquityQuantity


class NextRoundComparison(BaseModel):
    """One next round both ways: each option's price and new shares, the note's conversion in B, who owns what after
    it, the founders' ownership B - A and every exit.

    ``note_conversion`` is option B's note converting in this round (its interest included unless paid in cash), and
    ``existing_conversions`` the existing SAFEs and notes converting beside it; in option A they converted today.
    """

    model_config = MODEL_CONFIG

    index: int
    priced_price: EquityQuantity
    note_price: EquityQuantity
    priced_new_pool_shares: EquityQuantity
    note_new_pool_shares: EquityQuantity
    priced_investor_shares: EquityQuantity
    note_investor_shares: EquityQuantity
    priced_total_shares: EquityQuantity
    note_total_shares: EquityQuantity
    note_conversion: ConversionRow
    existing_conversions: tuple[ConversionRow, ...]
    stakes: tuple[GroupStake, ...]
    founders_ownership_difference: EquityQuantity
    exits: tuple[ExitComparison, ...]


class InstrumentCompareResult(BaseModel):
    """The comparison worked: today's financing both ways, then each next round and its exits, flags, assumptions.

    ``fully_diluted_shares`` is today's FD: founders + team + unissued pool + existing series. Option A's round today
    is its price, new pool, investor shares, total and the existing SAFEs and notes converting in it
    (``priced_conversions``). Option B issues no shares today: its note is outstanding, ``note_principal`` now and
    ``note_owed_at_conversion`` (rounded to the cent) when it converts, and its cap price is the cap over FD.
    """

    model_config = MODEL_CONFIG

    scenario: InstrumentCompareScenario = "instrument_compare"
    inputs: InstrumentCompareInput
    fully_diluted_shares: EquityQuantity
    priced_price: EquityQuantity
    priced_new_pool_shares: EquityQuantity
    priced_investor_shares: EquityQuantity
    priced_total_shares: EquityQuantity
    priced_conversions: tuple[ConversionRow, ...]
    note_cap_price: EquityQuantity | None = None
    note_principal: EquityQuantity
    note_interest_at_conversion: EquityQuantity
    note_owed_at_conversion: EquityQuantity
    note_interest_approximate: bool
    stakes_now: tuple[GroupStake, ...]
    founders_ownership_difference_now: EquityQuantity
    next_rounds: tuple[NextRoundComparison, ...]
    flags: tuple[InstrumentFlag, ...]
    assumptions: tuple[EquityAssumption, ...]
