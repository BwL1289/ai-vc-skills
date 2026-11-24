"""Pydantic models of a priced round now set beside a convertible note now (``equity_calculator instrument_compare``).

A founder raising ``investment`` today can sell priced shares now (option A, the ``priced_*`` fields) or issue a
convertible note now (option B, the ``note_*`` fields) that converts at the next priced round. Both options lead to
the same next round, given as one or more alternatives for it (``next_rounds``: its pre-money, the amount it raises,
any pool top-up and its series' terms), each worked from today's cap table and never after the one before, and the
company is then sold for each of ``exit_amounts``. The result shows, side by
side, who owns what right after today's financing, after each next round, and who gets what at each exit, with
B - A for every holder group. It never says which option to take. A short ``summary`` comes first: the founders' and
the new money's ownership at each point and the founders' payout at each exit, both ways, copied from the full rows
after it.

With no next round given (``next_rounds`` empty: the founder hopes today's raise is the only one), the comparison runs
in its no-next-round mode instead (``mode`` ``no_next_round``, flag ``no_next_round_given``): who owns what right after
today, with the note unconverted and what it owes at each month the founder names (``note_owed_months``); the note at
its maturity on its own terms only (``note_maturity_months``: the repayment of what it owes then, and its conversion
at a ``note_maturity_conversion_valuation`` or ``note_maturity_conversion_price`` only when the founder gives one); and
each exit as a sale before any priced round, option A through the waterfall and option B's note paid its own
change-of-control term (``note_change_of_control_multiple`` of its principal, or ``note_change_of_control_at_cap``
with the months to the sale, ``note_months_to_exit``). A row whose term is not given says why it is not worked.

Today's cap table is given by holder group: ``founder_shares``, ``team_shares`` (the team's granted options and
common), ``unissued_pool_shares`` and the existing investors: ``existing_series`` (each a preferred class with its own
terms, the waterfall's ``PreferredClass``) and ``existing_instruments`` (SAFEs and notes outstanding, the round's
``SafeTerms`` and ``NoteTerms``), which convert at the first priced round: today's in option A, the next one in B
(with no next round, none under B).
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
    "MAX_OWED_MONTHS",
    "STANDARD_MULTIPLE",
    "CompareMode",
    "CompareSummary",
    "EarlyGroupPayout",
    "ExitBeforeRoundComparison",
    "ExitComparison",
    "GroupPayout",
    "GroupStake",
    "HolderGroup",
    "InstrumentCompareInput",
    "InstrumentCompareResult",
    "InstrumentCompareScenario",
    "InstrumentFlag",
    "MaturityBasis",
    "MaturityConversion",
    "MaturityOutcome",
    "NextRound",
    "NextRoundComparison",
    "NoteAtExit",
    "NoteExitRefusal",
    "NoteExitRule",
    "NoteOwed",
    "OwnershipSummary",
    "PayoutSummary",
    "PoolAtExit",
    "SeriesTerms",
    "SummaryPoint",
    "SummaryValue",
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

# Which comparison ran: ``next_round`` (at least one next round given: the note converts there, and every exit follows
# it) or ``no_next_round`` (none given: the note stays unconverted, its maturity is shown on its own terms, and every
# exit is a sale before any priced round).
CompareMode = Literal["next_round", "no_next_round"]

# Where a summary ownership row stands: right after today's financing, after a next round, or at option B's maturity
# conversion (no next round; option A as right after today).
SummaryPoint = Literal["today", "next_round", "maturity"]

# How option B's note is paid at a sale before any priced round, as the founder gives the note's own term: ``multiple``
# (a multiple of its principal, paid before any share) or ``converts_at_cap`` (converted at its cap price into common).
NoteExitRule = Literal["multiple", "converts_at_cap"]

# Why option B is not worked at a sale before any priced round: existing SAFEs or notes are still outstanding there and
# their own sale terms are not given; or the note's change-of-control term is not given (the note has a cap, or has
# none to convert at). The result carries the reason in words beside the code.
NoteExitRefusal = Literal[
    "existing_instruments_outstanding", "no_change_of_control_term", "uncapped_no_change_of_control_term"
]

# The price a note converts at on maturity: a valuation over today's fully diluted shares (as its cap is), or a price
# per share, either as the founder gives it from the note's own terms.
MaturityBasis = Literal["valuation", "price"]

# Facts the comparison turns up. They never change a number and never say which option to take; their plain words are
# in ``equity_calculator.layout_instrument_compare``. ``cap_below_round_price_now``: the note's cap price (cap / FD) is
# below option A's price per share today. ``note_converts_at_*``: in at least one next round, the price the note took.
# ``note_interest_paid_in_cash``: the note's interest is paid in cash at conversion, so it is in no payout line.
# ``maturity_not_given`` / ``converts_after_maturity``: the note's maturity is unknown, or comes before the next round.
# ``next_round_below_priced_round_price``: a next round prices below option A's round today (a down round for A).
# ``priced_round_below_existing_series_price``: option A's round today prices below what an existing series paid per
# share. ``existing_mfn_safe_beside_note``: with a next round, an existing MFN SAFE converts on its given terms under
# both options, although option B's note is a later instrument with a cap or discount. With no next round:
# ``no_next_round_given`` (the mode switch), ``discount_unused_without_round`` (a discount applies only at a priced
# round), ``cap_unused_without_round`` (the cap sets a price only at a worked sale on the converts-at-its-cap term),
# ``maturity_conversion_not_given`` (a maturity but no conversion term), ``change_of_control_not_given`` (no term for a
# sale before any priced round), ``existing_instruments_outstanding`` (under B the existing SAFEs and notes never
# convert), ``exit_after_maturity`` (B is worked at sales whose months pass the note's maturity) and
# ``note_paid_below_owed_at_sale`` (converted at its cap, the note is paid less than it owes at some sale).
InstrumentFlag = Literal[
    "no_next_round_given",
    "cap_below_round_price_now",
    "note_converts_at_cap",
    "note_converts_at_discount",
    "note_converts_at_round_price",
    "note_interest_converts",
    "note_interest_paid_in_cash",
    "maturity_not_given",
    "converts_after_maturity",
    "next_round_below_priced_round_price",
    "priced_round_below_existing_series_price",
    "existing_mfn_safe_beside_note",
    "discount_unused_without_round",
    "cap_unused_without_round",
    "maturity_conversion_not_given",
    "change_of_control_not_given",
    "existing_instruments_outstanding",
    "exit_after_maturity",
    "note_paid_below_owed_at_sale",
]

# The list caps. With every existing series and instrument, an exit has 6 + 4 classes plus option A's two new series
# (or B's note and next round), 12 in all: the waterfall's own cap (``equity_waterfall.MAX_CLASSES``).
MAX_EXISTING_SERIES = 6
MAX_EXISTING_INSTRUMENTS = 4
MAX_NEXT_ROUNDS = 4
MAX_EXITS = 6
# The months at which the note's amount owed is shown.
MAX_OWED_MONTHS = 6

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
    fully diluted shares) and discount, each optional; its interest rate and compounding, both required; and, with a
    next round, the months until it converts there. With a next round, ``note_maturity_months`` (optional) is only
    compared with those months: no repayment or conversion at maturity is modelled. ``note_owed_months`` shows what the
    note owes at each month named, in either mode.

    With no next round (``next_rounds`` empty) there is no conversion month: ``note_months_to_conversion`` is refused,
    the note's maturity is shown on its own terms (the repayment, and a conversion at the founder's
    ``note_maturity_conversion_valuation`` or ``note_maturity_conversion_price``) and each exit is a sale before any
    priced round, where the note is paid its ``note_change_of_control_multiple`` of the principal or converts at its cap
    (``note_change_of_control_at_cap``, with ``note_months_to_exit`` for the interest). Those terms are refused with a
    next round, where every exit follows the round the note converts in.
    """

    model_config = MODEL_CONFIG

    scenario: InstrumentCompareScenario = "instrument_compare"
    founder_shares: ShareCount = Field(gt=0)
    # Required, 0 for none: today's fully diluted shares are built from the holder groups, so a group left out would
    # lower them (and the note's cap price) without a word.
    team_shares: ShareCount = Field(ge=0)
    unissued_pool_shares: ShareCount = Field(ge=0)
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
    # Needed with a next round, refused with none: the month the note converts at that round (``_months_fit_the_mode``).
    note_months_to_conversion: NoteMonths | None = None
    note_maturity_months: MaturityMonths | None = None
    note_interest_paid_in_cash: StrictFlag = False
    note_owed_months: tuple[NoteMonths, ...] = Field(default=(), max_length=MAX_OWED_MONTHS)
    # The terms of a note with no next round, each from the note's own terms and never assumed.
    note_maturity_conversion_valuation: BoundedDecimal | None = Field(default=None, gt=0)
    note_maturity_conversion_price: BoundedDecimal | None = Field(default=None, gt=0)
    note_change_of_control_multiple: BoundedDecimal | None = Field(default=None, gt=0)
    note_change_of_control_at_cap: StrictFlag = False
    note_months_to_exit: NoteMonths | None = None
    next_rounds: tuple[NextRound, ...] = Field(default=(), max_length=MAX_NEXT_ROUNDS)
    exit_amounts: tuple[ExitAmount, ...] = Field(default=(), max_length=MAX_EXITS)
    pool_at_exit: PoolAtExit = "as_common"

    def _no_round_terms_given(self) -> list[str]:
        """The terms of a note with no next round that were given, by field name."""
        terms = (
            ("note_maturity_conversion_valuation", self.note_maturity_conversion_valuation is not None),
            ("note_maturity_conversion_price", self.note_maturity_conversion_price is not None),
            ("note_change_of_control_multiple", self.note_change_of_control_multiple is not None),
            ("note_change_of_control_at_cap", self.note_change_of_control_at_cap),
            ("note_months_to_exit", self.note_months_to_exit is not None),
        )
        return [name for name, given in terms if given]

    def _months_fit_the_mode(self) -> None:
        """With a next round: its conversion month is given and no term of a note with no next round is. With none:
        no conversion month, and each no-next-round term with what it needs."""
        if self.next_rounds:
            if self.note_months_to_conversion is None:
                raise ValueError(
                    "note_months_to_conversion is needed with a next round: the months from today until option B's "
                    "note converts there, from the founder"
                )
            given = self._no_round_terms_given()
            if given:
                raise ValueError(
                    f"{', '.join(given)}: a term of a note with no next round (at its maturity or at a sale before "
                    "any priced round); with next_rounds given the note converts there and every exit follows that "
                    "round, so leave it out, or leave next_rounds out to see the note with no next round"
                )
            return

        if self.note_months_to_conversion is not None:
            raise ValueError(
                "no_next_round_given: note_months_to_conversion is the months until the note converts at a next "
                "round, and no next round is given; leave it out to see the note with no next round (ownership "
                "today, the note at its maturity, each exit before any priced round), or give next_rounds"
            )
        self._no_round_terms_fit()

    def _no_round_terms_fit(self) -> None:
        """Refuse no-next-round terms that clash or lack what they need: never one assumed in place of another."""
        valuation, price = self.note_maturity_conversion_valuation, self.note_maturity_conversion_price
        if valuation is not None and price is not None:
            raise ValueError(
                "give note_maturity_conversion_valuation or note_maturity_conversion_price, not both: the note's own "
                "terms name one"
            )
        if (valuation is not None or price is not None) and self.note_maturity_months is None:
            raise ValueError(
                "a maturity conversion needs note_maturity_months: the month the note matures, from its own terms"
            )
        if self.note_change_of_control_at_cap and self.note_change_of_control_multiple is not None:
            raise ValueError(
                "give one change-of-control term, note_change_of_control_multiple or note_change_of_control_at_cap, "
                "as the note's own terms give it"
            )
        if self.note_change_of_control_at_cap and self.note_valuation_cap is None:
            raise ValueError(
                "note_change_of_control_at_cap needs note_valuation_cap: an uncapped note has no cap to convert at, "
                "so give its own change-of-control term as note_change_of_control_multiple"
            )
        if self.note_change_of_control_at_cap and self.note_months_to_exit is None:
            raise ValueError(
                "note_change_of_control_at_cap needs note_months_to_exit: the months from today to the sale, for the "
                "interest the note converts (never assumed)"
            )

    @model_validator(mode="after")
    def _comparison_can_run(self) -> InstrumentCompareInput:
        """Refuse a comparison with no exit, a conversion month or term that does not fit the mode (a next round or
        none), an existing series or note whose terms would be assumed, an existing note it cannot move, or a round
        with no price whatever happens (a pool target or capped SAFEs taking the whole company)."""
        self._months_fit_the_mode()
        repeated = sorted({month for month in self.note_owed_months if self.note_owed_months.count(month) > 1})
        if repeated:
            raise ValueError(
                f"note_owed_months gives month {', '.join(str(month) for month in repeated)} more than once: give each "
                "month once"
            )
        if not self.exit_amounts:
            after = "after the next round" if self.next_rounds else "before any priced round (no next round is given)"
            raise ValueError(f"exit_amounts is empty: give at least one exit, what the company sells for {after}")
        for item in self.existing_series:
            if not {"preference_multiple", "participation"} <= item.model_fields_set:
                raise ValueError(
                    "an existing series in existing_series gives preference_multiple and participation (that "
                    "series' own terms, from the founder): they are never assumed"
                )
        for item in self.existing_instruments:
            if not isinstance(item, NoteTerms):
                continue
            if item.months_outstanding is None:
                raise ValueError(
                    "an existing note in existing_instruments gives months_outstanding as of today, not dates: "
                    "option A converts it today and option B at the next round"
                )
            later = self.note_months_to_conversion
            if later is not None and item.months_outstanding + later > MAX_NOTE_MONTHS:
                raise ValueError(
                    f"an existing note's months_outstanding plus note_months_to_conversion is over {MAX_NOTE_MONTHS} "
                    "months: option B converts it that much later"
                )
            if "compounding" not in item.model_fields_set:
                raise ValueError(
                    "an existing note in existing_instruments gives compounding (simple, annual or monthly), as "
                    "option B's note does: it is never assumed"
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


class NoteOwed(BaseModel):
    """What option B's note owes after ``months``: its interest and principal plus interest, each to the cent
    (``approximate`` when a fractional-power stub was raised)."""

    model_config = MODEL_CONFIG

    months: int
    interest: EquityQuantity
    owed: EquityQuantity
    approximate: bool


class MaturityConversion(BaseModel):
    """Option B's note converting at its maturity at the founder's valuation (over today's FD) or price: what converts
    (principal + interest, or the principal alone when the interest is paid in cash), its shares, and who owns what
    then beside option A right after today, with B - A."""

    model_config = MODEL_CONFIG

    basis: MaturityBasis
    price: EquityQuantity
    converting_amount: EquityQuantity
    shares: EquityQuantity
    total_shares: EquityQuantity
    stakes: tuple[GroupStake, ...]
    founders_ownership_difference: EquityQuantity


class MaturityOutcome(BaseModel):
    """Option B's note at its maturity with no next round: what it owes then (its repayment), and its conversion when
    the founder gives the note's maturity conversion term (``None`` otherwise: that depends on the note's own terms)."""

    model_config = MODEL_CONFIG

    owed: NoteOwed
    conversion: MaturityConversion | None = None


class NoteAtExit(BaseModel):
    """Option B's note at a sale before any priced round, the same at every exit: with ``multiple``, its ``claim``
    (that multiple of the principal), paid before any share and never more than the exit; with ``converts_at_cap``,
    what it owes at the sale (``owed``), what converts and its common shares at its cap price."""

    model_config = MODEL_CONFIG

    rule: NoteExitRule
    claim: EquityQuantity | None = None
    owed: NoteOwed | None = None
    converting_amount: EquityQuantity | None = None
    conversion_price: EquityQuantity | None = None
    shares: EquityQuantity | None = None


class EarlyGroupPayout(BaseModel):
    """One holder group's payout at a sale before any priced round under each option, and B - A; option B's and the
    difference are ``None`` when option B is not worked at that sale."""

    model_config = MODEL_CONFIG

    group: HolderGroup
    priced: EquityQuantity
    note: EquityQuantity | None = None
    difference: EquityQuantity | None = None


class ExitBeforeRoundComparison(BaseModel):
    """One sale before any priced round (no next round given): each group's payout both ways and B - A.

    Option A splits its cap table after today through the waterfall. Option B pays its note's change-of-control term
    first (``NoteAtExit``) and splits the rest; when that term is not given, or existing SAFEs and notes are still
    outstanding, option B is not worked at this sale and ``note_refusal`` and ``note_refusal_reason`` say why.
    """

    model_config = MODEL_CONFIG

    exit_amount: EquityQuantity
    payouts: tuple[EarlyGroupPayout, ...]
    priced_preferences_paid: EquityQuantity
    note_preferences_paid: EquityQuantity | None = None
    founders_payout_difference: EquityQuantity | None = None
    note_refusal: NoteExitRefusal | None = None
    note_refusal_reason: str | None = None


class SummaryValue(BaseModel):
    """One figure under each option and B - A; option B's and the difference are ``None`` where B is not worked."""

    model_config = MODEL_CONFIG

    priced: EquityQuantity
    note: EquityQuantity | None = None
    difference: EquityQuantity | None = None


class OwnershipSummary(BaseModel):
    """The founders' and the new money's ownership at one point (``next_round`` numbers the round, from 1): the same
    values as that point's ``stakes`` rows. The new money is today's raise: option A's priced shares, option B's note
    once it converts (none before)."""

    model_config = MODEL_CONFIG

    point: SummaryPoint
    next_round: int | None = None
    founders: SummaryValue
    new_money: SummaryValue


class PayoutSummary(BaseModel):
    """The founders' payout at one exit (after next round ``next_round``, or with ``next_round`` ``None`` at a sale
    before any priced round): the same values as that exit's founders' payout row; ``note_refusal`` says why option B is
    not worked there."""

    model_config = MODEL_CONFIG

    next_round: int | None = None
    exit_amount: EquityQuantity
    founders: SummaryValue
    note_refusal: NoteExitRefusal | None = None


class CompareSummary(BaseModel):
    """The comparison in short, both ways: ownership at each point, then the founders' payout at each exit."""

    model_config = MODEL_CONFIG

    ownership: tuple[OwnershipSummary, ...]
    founders_payouts: tuple[PayoutSummary, ...]


class InstrumentCompareResult(BaseModel):
    """The comparison worked: today's financing both ways, then each next round and its exits, flags, assumptions.

    ``fully_diluted_shares`` is today's FD: founders + team + unissued pool + existing series. Option A's round today
    is its price, new pool, investor shares, total and the existing SAFEs and notes converting in it
    (``priced_conversions``). Option B issues no shares today: its note is outstanding, ``note_principal`` now and
    ``note_owed_at_conversion`` (rounded to the cent) when it converts, and its cap price is the cap over FD;
    ``note_owed`` is what it owes at each of ``note_owed_months``.

    In the no-next-round mode (``mode`` ``no_next_round``) nothing converts at a next round, so ``next_rounds`` is
    empty and the ``note_*_at_conversion`` fields are ``None``; ``maturity`` is the note at its maturity (``None``
    when no maturity is given), ``note_at_exit`` its change-of-control term (``None`` when none is given, or when
    option B is not worked at the sales because existing SAFEs or notes are outstanding) and
    ``exits_before_any_round`` each sale before any priced round.

    ``summary`` comes first, so a reader meets the short answer before the detail; every value in it is a copy of a
    full row's.
    """

    model_config = MODEL_CONFIG

    scenario: InstrumentCompareScenario = "instrument_compare"
    summary: CompareSummary
    inputs: InstrumentCompareInput
    fully_diluted_shares: EquityQuantity
    priced_price: EquityQuantity
    priced_new_pool_shares: EquityQuantity
    priced_investor_shares: EquityQuantity
    priced_total_shares: EquityQuantity
    priced_conversions: tuple[ConversionRow, ...]
    note_cap_price: EquityQuantity | None = None
    note_principal: EquityQuantity
    note_interest_at_conversion: EquityQuantity | None = None
    note_owed_at_conversion: EquityQuantity | None = None
    note_interest_approximate: bool | None = None
    note_owed: tuple[NoteOwed, ...]
    stakes_now: tuple[GroupStake, ...]
    founders_ownership_difference_now: EquityQuantity
    mode: CompareMode
    next_rounds: tuple[NextRoundComparison, ...]
    maturity: MaturityOutcome | None = None
    note_at_exit: NoteAtExit | None = None
    exits_before_any_round: tuple[ExitBeforeRoundComparison, ...] = ()
    flags: tuple[InstrumentFlag, ...]
    assumptions: tuple[EquityAssumption, ...]
