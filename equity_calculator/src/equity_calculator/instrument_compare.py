"""A priced round now set beside a convertible note now: ownership after today, after each next round, and each exit.

Every price comes from the round code and every exit from the waterfall code; this module only lays the two options'
cap tables out and runs them through those:

- **Option A, today.** A priced round of I at ``priced_pre_money`` on today's fully diluted shares FD (founders + team
  + unissued pool + existing series), with its pool top-up and the existing SAFEs and notes converting in it:
  ``convertibles.settle``, the ``round`` scenario's price and conversions.
- **Option B, today.** No shares: the note is outstanding, its principal now and, at conversion, what
  ``interest.note_interest`` says it owes (to the cent).
- **Each next round.** For A, a priced round on A's shares after today (exact, often fractional, which ``RoundInput``
  cannot hold, so the round code reads them through its ``RoundTerms`` protocol), with no instruments left to
  convert. For B, a priced round on today's FD with the existing SAFEs and notes (each existing note
  ``note_months_to_conversion`` older) and the note converting in it, at the lower of its cap price and discount price.
- **Each exit.** ``waterfall.conversion_profile`` and ``split_exit`` on each option's classes after the next round:
  the existing series as given; option A's round today and every converted SAFE or note on that series' terms (their
  preference on the amount converted); the next round's investors on its terms; option B's note and existing
  instruments on the next round's terms. Common is the founders, the team and (``pool_at_exit`` ``as_common``) the
  pool.

With no next round given (the no-next-round mode) nothing converts at a priced round under B, and three things are
shown instead, each from the note's own terms as the founder gives them and never assumed:

- **Today.** Both options as above, and what the note owes (``interest.note_interest``, to the cent) at each month
  the founder names. Under B the existing SAFEs and notes stay outstanding: they hold no shares.
- **At maturity.** What the note owes then, its repayment; and, with the founder's maturity conversion valuation (over
  today's FD, as the cap is) or price, what converts (principal plus interest, or the principal alone when the
  interest is paid in cash) and its shares, with who owns what then beside option A right after today.
- **Each sale before any priced round.** Option A's cap table after today through the waterfall. Under B the note is
  paid its change-of-control term first: a multiple of its principal, paid before any share and never more than the
  sale, with the rest split among the shares; or what it owes at the sale converted at its cap price (cap / FD) into
  common shares that share the rest with the founders, the team and the pool. With no term given, or with existing
  SAFEs or notes outstanding, B is not worked at that sale and the row says why.

Ownership is each group's shares over the total; payouts are split to the cent by largest remainder within each
option, so each adds up to the exit. B - A is worked on the exact values and rounded once.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from decimal import Decimal
from fractions import Fraction
from typing import get_args

from equity_calculator.assumptions_instrument_compare import instrument_compare_assumptions
from equity_calculator.convertibles import Convertible, Priced, convertibles, settle
from equity_calculator.errors import RoundHasNoPrice
from equity_calculator.exact import ZERO, fraction, money_split, quantity
from equity_calculator.interest import NoteInterest, note_interest
from equity_calculator.round import conversion_row
from equity_calculator.schemas.equity_common import EquityQuantity, PoolTiming
from equity_calculator.schemas.equity_instrument_compare import (
    STANDARD_MULTIPLE,
    EarlyGroupPayout,
    ExitBeforeRoundComparison,
    ExitComparison,
    GroupPayout,
    GroupStake,
    HolderGroup,
    InstrumentCompareInput,
    InstrumentCompareResult,
    InstrumentFlag,
    MaturityBasis,
    MaturityConversion,
    MaturityOutcome,
    NextRound,
    NextRoundComparison,
    NoteAtExit,
    NoteExitRefusal,
    NoteExitRule,
    NoteOwed,
    SeriesTerms,
)
from equity_calculator.schemas.equity_round import ConversionRow, NoteTerms, SafeTerms
from equity_calculator.schemas.equity_waterfall import Participation
from equity_calculator.waterfall import conversion_profile, default_pass_limit, split_exit

__all__ = ["NOTE_EXIT_REFUSALS", "compute_instrument_compare", "option_b_note"]

_GROUPS: tuple[HolderGroup, ...] = get_args(HolderGroup)
_STANDARD_RANK = 1
_FIRST_INDEX = 1
# The waterfall's search bound is one pass more than the classes (``waterfall.default_pass_limit``).
_EXTRA_PASSES = 1
# The exit the assumptions are listed for: only its classes are read, never its amount.
ZERO_AMOUNT = Decimal(0)
# Option B's note in the round rows of the assumptions when no next round is given: only its kind is read.
_NO_MONTHS = 0

# Why option B is not worked at a sale before any priced round, in the words the result and the report give.
NOTE_EXIT_REFUSALS: dict[NoteExitRefusal, str] = {
    "existing_instruments_outstanding": "option B is not worked at this sale: with no priced round the existing SAFEs "
    "and notes are still outstanding, and what each is paid at a sale is in its own terms, which are not given here",
    "no_change_of_control_term": "option B is not worked at this sale: no change-of-control term was given for the "
    "note, and what it is paid at a sale before any priced round is in its own terms (a multiple of its principal, "
    "or conversion at its cap), so give that term",
    "uncapped_no_change_of_control_term": "option B is not worked at this sale: the note has no cap to convert at and "
    "no change-of-control term was given, and what it is paid at a sale before any priced round is in its own terms "
    "(for example a multiple of its principal), so give that term",
}


@dataclass(frozen=True)
class RoundShape:
    """One priced round's terms with exact share counts: what ``convertibles.RoundTerms`` reads."""

    fully_diluted_shares: Fraction
    unissued_pool_shares: Fraction
    pre_money: Decimal
    investment: Decimal
    target_pool_percent: Decimal
    pool_timing: PoolTiming
    instruments: tuple[SafeTerms | NoteTerms, ...]


@dataclass(frozen=True)
class SeriesClass:
    """One preferred class after a round, with exact shares: what ``waterfall.ClassTerms`` reads, and its group."""

    group: HolderGroup
    shares: Fraction
    invested: Fraction
    preference_multiple: Decimal
    rank: int
    participation: Participation
    cap_multiple: Decimal | None


@dataclass(frozen=True)
class ExitShape:
    """One exit of one option's cap table: what ``waterfall.ExitTerms`` reads (exact: what a note leaves of a sale)."""

    exit_amount: Decimal | Fraction
    common_shares: Fraction
    classes: tuple[SeriesClass, ...]


@dataclass(frozen=True)
class _Table:
    """One option's cap table at one point: the common holders' shares, the preferred classes and, with no next round,
    option B's note converted into shares at its maturity or at a sale (``note_common``, the new money's)."""

    founders: Fraction
    team: Fraction
    pool: Fraction
    classes: tuple[SeriesClass, ...]
    note_common: Fraction = ZERO

    def shares(self) -> dict[HolderGroup, Fraction]:
        by_group = dict.fromkeys(_GROUPS, ZERO)
        by_group["founders"] = self.founders
        by_group["team"] = self.team
        by_group["option_pool"] = self.pool
        by_group["new_money"] = self.note_common
        for item in self.classes:
            by_group[item.group] += item.shares
        return by_group

    def total(self) -> Fraction:
        return sum(self.shares().values(), ZERO)


@dataclass(frozen=True)
class _Worked:
    """One round priced and settled: its price and new shares, each instrument and the row it converted to."""

    priced: Priced
    items: tuple[Convertible, ...]
    rows: tuple[ConversionRow, ...]


def _months_to_conversion(inputs: InstrumentCompareInput) -> int:
    """The months until option B's note converts at a next round (given whenever one is: the input model sees to it)."""
    if inputs.note_months_to_conversion is None:
        raise ValueError("note_months_to_conversion is needed with a next round (InstrumentCompareInput checks this)")
    return inputs.note_months_to_conversion


def option_b_note(inputs: InstrumentCompareInput, months: int | None = None) -> NoteTerms:
    """Option B's note: the raise as principal, the note's terms, and as its age ``months`` (by default the months
    until it converts at the next round)."""
    age = _months_to_conversion(inputs) if months is None else months
    return NoteTerms.model_validate(
        {
            "principal": inputs.investment,
            "interest_rate_percent": inputs.note_interest_rate_percent,
            "compounding": inputs.note_compounding,
            "stub_rule": inputs.note_stub_rule,
            "months_outstanding": age,
            "valuation_cap": inputs.note_valuation_cap,
            "discount_percent": inputs.note_discount_percent,
            "interest_paid_in_cash": inputs.note_interest_paid_in_cash,
        }
    )


def _older(item: SafeTerms | NoteTerms, months: int) -> SafeTerms | NoteTerms:
    """An existing instrument at option B's next round: a note ``months`` older (a SAFE does not change)."""
    if isinstance(item, SafeTerms) or item.months_outstanding is None:
        return item

    return NoteTerms.model_validate({**item.model_dump(), "months_outstanding": item.months_outstanding + months})


def _work(shape: RoundShape, label: str) -> _Worked:
    """``shape`` priced and settled by the round code; a round with no price is refused naming ``label``."""
    items = convertibles(shape)
    try:
        settled = settle(shape, items)
    except RoundHasNoPrice as error:
        raise RoundHasNoPrice(f"{label}: {error}") from None
    fully_diluted = fraction(shape.fully_diluted_shares)
    rows = tuple(
        conversion_row(item, capped, settled.priced, fully_diluted)
        for item, capped in zip(items, settled.on_cap, strict=True)
    )
    return _Worked(settled.priced, items, rows)


def _series(group: HolderGroup, shares: Fraction, invested: Fraction, terms: SeriesTerms) -> SeriesClass:
    """A class of ``shares`` on a new series' ``terms``, owed its multiple of ``invested``."""
    rank = _STANDARD_RANK if terms.rank is None else terms.rank
    if terms.standard:
        return SeriesClass(group, shares, invested, STANDARD_MULTIPLE, rank, "none", None)
    if terms.preference_multiple is None or terms.participation is None:
        raise ValueError("a series gives standard, or preference_multiple and participation (SeriesTerms checks this)")

    return SeriesClass(
        group, shares, invested, terms.preference_multiple, rank, terms.participation, terms.cap_multiple
    )


def _converted(worked: _Worked, items: Iterable[int], group: HolderGroup, terms: SeriesTerms) -> list[SeriesClass]:
    """The instruments at ``items`` (0-based) as classes on ``terms``, each owed its multiple of what converted."""
    return [_series(group, worked.rows[index].shares.exact, worked.items[index].converting, terms) for index in items]


def _stakes(priced: _Table, note: _Table) -> tuple[GroupStake, ...]:
    """Each group either option gives shares to: its shares and ownership both ways, and the ownership B - A."""
    priced_shares, note_shares = priced.shares(), note.shares()
    priced_total, note_total = priced.total(), note.total()
    stakes = []
    for group in _GROUPS:
        if priced_shares[group] == ZERO and note_shares[group] == ZERO:
            continue
        priced_part = priced_shares[group] / priced_total
        note_part = note_shares[group] / note_total
        stakes.append(
            GroupStake(
                group=group,
                priced_shares=quantity("shares", priced_shares[group]),
                note_shares=quantity("shares", note_shares[group]),
                priced=quantity("fraction", priced_part),
                note=quantity("fraction", note_part),
                difference=quantity("fraction", note_part - priced_part),
            )
        )
    return tuple(stakes)


def _payouts(
    table: _Table, exit_amount: Decimal | Fraction, pool_takes_part: bool
) -> tuple[dict[HolderGroup, Fraction], Fraction]:
    """Each group's exact payout from the waterfall at ``exit_amount``, and the preferences paid in all."""
    pool = table.pool if pool_takes_part else ZERO
    shape = ExitShape(exit_amount, table.founders + table.team + pool + table.note_common, table.classes)
    converts, _ = conversion_profile(shape, default_pass_limit(shape))
    split = split_exit(shape, converts)
    paid = dict.fromkeys(_GROUPS, ZERO)
    paid["founders"] = table.founders * split.price
    paid["team"] = table.team * split.price
    paid["option_pool"] = pool * split.price
    paid["new_money"] = table.note_common * split.price
    for index, item in enumerate(table.classes):
        paid[item.group] += split.payout(index)
    return paid, sum(split.paid, ZERO)


def _exit(priced: _Table, note: _Table, groups: Sequence[HolderGroup], amount: Decimal, pool: bool) -> ExitComparison:
    """One exit both ways: each group's payout, cents by largest remainder within each option, and B - A."""
    priced_paid, priced_preferences = _payouts(priced, amount, pool)
    note_paid, note_preferences = _payouts(note, amount, pool)
    priced_money = money_split([priced_paid[group] for group in groups])
    note_money = money_split([note_paid[group] for group in groups])
    payouts = tuple(
        GroupPayout(
            group=group,
            priced=priced_value,
            note=note_value,
            difference=quantity("money", note_paid[group] - priced_paid[group]),
        )
        for group, priced_value, note_value in zip(groups, priced_money, note_money, strict=True)
    )
    return ExitComparison(
        exit_amount=quantity("money", fraction(amount)),
        payouts=payouts,
        priced_preferences_paid=quantity("money", priced_preferences),
        note_preferences_paid=quantity("money", note_preferences),
        founders_payout_difference=quantity("money", note_paid["founders"] - priced_paid["founders"]),
    )


def _difference(stakes: Sequence[GroupStake], group: HolderGroup) -> EquityQuantity:
    """``group``'s ownership B - A (zero when neither option gives it shares)."""
    return next((stake.difference for stake in stakes if stake.group == group), quantity("fraction", ZERO))


@dataclass(frozen=True)
class _RoundPair:
    """One next round worked both ways: the comparison, option B's round terms and both cap tables after it."""

    comparison: NextRoundComparison
    note_shape: RoundShape
    priced_after: _Table
    note_after: _Table


def _next_round(
    inputs: InstrumentCompareInput, index: int, round_terms: NextRound, priced_now: _Table, fully_diluted: Fraction
) -> _RoundPair:
    """Next round ``index`` (from 1) both ways and its exits."""
    common = (round_terms.pre_money, round_terms.investment, round_terms.target_pool_percent, round_terms.pool_timing)
    priced = _work(RoundShape(priced_now.total(), priced_now.pool, *common, ()), f"next round {index}, option A")
    existing = tuple(_older(item, _months_to_conversion(inputs)) for item in inputs.existing_instruments)
    unissued = fraction(inputs.unissued_pool_shares)
    note_shape = RoundShape(fully_diluted, unissued, *common, (*existing, option_b_note(inputs)))
    note = _work(note_shape, f"next round {index}, option B")
    series = round_terms.preference
    raised = fraction(round_terms.investment)
    priced_after = _Table(
        priced_now.founders,
        priced_now.team,
        priced_now.pool + priced.priced.new_pool,
        (*priced_now.classes, _series("next_round_investors", priced.priced.investor_shares, raised, series)),
    )
    note_index = len(existing)
    note_after = _Table(
        priced_now.founders,
        priced_now.team,
        unissued + note.priced.new_pool,
        (
            *_existing_series(inputs),
            *_converted(note, range(note_index), "existing_investors", series),
            *_converted(note, (note_index,), "new_money", series),
            _series("next_round_investors", note.priced.investor_shares, raised, series),
        ),
    )
    stakes = _stakes(priced_after, note_after)
    groups: tuple[HolderGroup, ...] = tuple(stake.group for stake in stakes)
    pool = inputs.pool_at_exit == "as_common"
    comparison = NextRoundComparison(
        index=index,
        priced_price=quantity("price", priced.priced.price),
        note_price=quantity("price", note.priced.price),
        priced_new_pool_shares=quantity("shares", priced.priced.new_pool),
        note_new_pool_shares=quantity("shares", note.priced.new_pool),
        priced_investor_shares=quantity("shares", priced.priced.investor_shares),
        note_investor_shares=quantity("shares", note.priced.investor_shares),
        priced_total_shares=quantity("shares", priced_after.total()),
        note_total_shares=quantity("shares", note_after.total()),
        note_conversion=note.rows[note_index],
        existing_conversions=note.rows[:note_index],
        stakes=stakes,
        founders_ownership_difference=_difference(stakes, "founders"),
        exits=tuple(_exit(priced_after, note_after, groups, amount, pool) for amount in inputs.exit_amounts),
    )
    return _RoundPair(comparison, note_shape, priced_after, note_after)


def _existing_series(inputs: InstrumentCompareInput) -> tuple[SeriesClass, ...]:
    """The existing preferred series as given, each its own class."""
    return tuple(
        SeriesClass(
            "existing_investors",
            fraction(item.shares),
            fraction(item.invested),
            item.preference_multiple,
            item.rank,
            item.participation,
            item.cap_multiple,
        )
        for item in inputs.existing_series
    )


@dataclass(frozen=True)
class _NoteSale:
    """Option B's note at a sale before any priced round: its rule, and its claim or its common shares (exact)."""

    rule: NoteExitRule
    claim: Fraction
    shares: Fraction


@dataclass(frozen=True)
class _NoRound:
    """The no-next-round mode worked: the note at maturity, at a sale, each sale both ways, and what converts."""

    maturity: MaturityOutcome | None
    note_at_exit: NoteAtExit | None
    exits: tuple[ExitBeforeRoundComparison, ...]
    converted: tuple[NoteInterest, ...]


def _interest_at(inputs: InstrumentCompareInput, months: int) -> NoteInterest:
    """What option B's note owes after ``months``: the interest code's figure, to the cent."""
    return note_interest(option_b_note(inputs, months))


def _owed_row(months: int, interest: NoteInterest) -> NoteOwed:
    return NoteOwed(
        months=months,
        interest=quantity("money", interest.accrued),
        owed=quantity("money", interest.owed),
        approximate=interest.approximate,
    )


def _maturity_price(inputs: InstrumentCompareInput, fully_diluted: Fraction) -> tuple[MaturityBasis, Fraction] | None:
    """The price the note converts at on maturity: the founder's valuation over FD, or the founder's price; ``None``
    when the founder gives neither."""
    if inputs.note_maturity_conversion_valuation is not None:
        return "valuation", fraction(inputs.note_maturity_conversion_valuation) / fully_diluted
    if inputs.note_maturity_conversion_price is not None:
        return "price", fraction(inputs.note_maturity_conversion_price)
    return None


def _maturity(
    inputs: InstrumentCompareInput, priced_now: _Table, note_now: _Table, fully_diluted: Fraction
) -> tuple[MaturityOutcome | None, NoteInterest | None]:
    """The note at its maturity (``None`` with no maturity given), and its interest when it converts there."""
    months = inputs.note_maturity_months
    if months is None:
        return None, None
    interest = _interest_at(inputs, months)
    owed = _owed_row(months, interest)
    conversion = _maturity_price(inputs, fully_diluted)
    if conversion is None:
        return MaturityOutcome(owed=owed), None

    basis, price = conversion
    shares = interest.converting / price
    after = replace(note_now, note_common=shares)
    stakes = _stakes(priced_now, after)
    converted = MaturityConversion(
        basis=basis,
        price=quantity("price", price),
        converting_amount=quantity("money", interest.converting),
        shares=quantity("shares", shares),
        total_shares=quantity("shares", after.total()),
        stakes=stakes,
        founders_ownership_difference=_difference(stakes, "founders"),
    )
    return MaturityOutcome(owed=owed, conversion=converted), interest


def _note_sale(
    inputs: InstrumentCompareInput, note_cap: Fraction | None
) -> tuple[NoteAtExit | None, _NoteSale | None, NoteInterest | None]:
    """The note's change-of-control term worked (``None`` when none is given), and its interest when it converts."""
    multiple = inputs.note_change_of_control_multiple
    if multiple is not None:
        claim = fraction(multiple) * fraction(inputs.investment)
        return NoteAtExit(rule="multiple", claim=quantity("money", claim)), _NoteSale("multiple", claim, ZERO), None
    months = inputs.note_months_to_exit
    if not inputs.note_change_of_control_at_cap or note_cap is None or months is None:
        return None, None, None

    interest = _interest_at(inputs, months)
    shares = interest.converting / note_cap
    at_exit = NoteAtExit(
        rule="converts_at_cap",
        owed=_owed_row(months, interest),
        converting_amount=quantity("money", interest.converting),
        conversion_price=quantity("price", note_cap),
        shares=quantity("shares", shares),
    )
    return at_exit, _NoteSale("converts_at_cap", ZERO, shares), interest


def _sale_refusal(inputs: InstrumentCompareInput, sale: _NoteSale | None) -> NoteExitRefusal | None:
    """Why option B is not worked at a sale before any priced round, or ``None`` when it is."""
    if inputs.existing_instruments:
        return "existing_instruments_outstanding"
    if sale is None:
        return (
            "uncapped_no_change_of_control_term" if inputs.note_valuation_cap is None else "no_change_of_control_term"
        )
    return None


def _sale_payouts(
    note_now: _Table, amount: Decimal, pool: bool, sale: _NoteSale
) -> tuple[dict[HolderGroup, Fraction], Fraction]:
    """Option B at a sale: the note's common shares share it, or its claim is paid first and the rest is split."""
    if sale.rule == "converts_at_cap":
        return _payouts(replace(note_now, note_common=sale.shares), amount, pool)

    take = min(sale.claim, fraction(amount))
    paid, preferences = _payouts(note_now, fraction(amount) - take, pool)
    paid["new_money"] += take
    return paid, preferences


def _exit_before_round(
    tables: tuple[_Table, _Table],
    groups: Sequence[HolderGroup],
    amount: Decimal,
    pool: bool,
    sale: _NoteSale | NoteExitRefusal,
) -> ExitBeforeRoundComparison:
    """One sale before any priced round both ways (B only when ``sale`` is its term, not a refusal), and B - A."""
    priced_now, note_now = tables
    priced_paid, priced_preferences = _payouts(priced_now, amount, pool)
    priced_money = money_split([priced_paid[group] for group in groups])
    exit_amount = quantity("money", fraction(amount))
    if isinstance(sale, str):
        return ExitBeforeRoundComparison(
            exit_amount=exit_amount,
            payouts=tuple(
                EarlyGroupPayout(group=group, priced=value) for group, value in zip(groups, priced_money, strict=True)
            ),
            priced_preferences_paid=quantity("money", priced_preferences),
            note_refusal=sale,
            note_refusal_reason=NOTE_EXIT_REFUSALS[sale],
        )

    note_paid, note_preferences = _sale_payouts(note_now, amount, pool, sale)
    note_money = money_split([note_paid[group] for group in groups])
    payouts = tuple(
        EarlyGroupPayout(
            group=group,
            priced=priced_value,
            note=note_value,
            difference=quantity("money", note_paid[group] - priced_paid[group]),
        )
        for group, priced_value, note_value in zip(groups, priced_money, note_money, strict=True)
    )
    return ExitBeforeRoundComparison(
        exit_amount=exit_amount,
        payouts=payouts,
        priced_preferences_paid=quantity("money", priced_preferences),
        note_preferences_paid=quantity("money", note_preferences),
        founders_payout_difference=quantity("money", note_paid["founders"] - priced_paid["founders"]),
    )


def _no_round(
    inputs: InstrumentCompareInput,
    tables: tuple[_Table, _Table],
    groups: Sequence[HolderGroup],
    fully_diluted: Fraction,
    note_cap: Fraction | None,
) -> _NoRound:
    """The no-next-round mode: the note at its maturity, its change-of-control term, and each sale both ways."""
    priced_now, note_now = tables
    maturity, at_maturity = _maturity(inputs, priced_now, note_now, fully_diluted)
    at_exit, sale, at_sale = _note_sale(inputs, note_cap)
    refusal = _sale_refusal(inputs, sale)
    term: _NoteSale | NoteExitRefusal | None = refusal if refusal is not None else sale
    if term is None:
        raise ValueError("a sale is worked with the note's term or refused with a reason (_sale_refusal sees to it)")
    pool = inputs.pool_at_exit == "as_common"
    exits = tuple(_exit_before_round(tables, groups, amount, pool, term) for amount in inputs.exit_amounts)
    # The note converts at its maturity when that term is given, and at the sales only when they are worked.
    converted = tuple(item for item in (at_maturity, None if refusal else at_sale) if item is not None)
    return _NoRound(maturity, at_exit, exits, converted)


def _flags(
    inputs: InstrumentCompareInput,
    price_now: Fraction,
    note_cap: Fraction | None,
    converted: Sequence[NoteInterest],
    rounds: Sequence[NextRoundComparison],
) -> tuple[InstrumentFlag, ...]:
    """The flags that hold, in the order ``InstrumentFlag`` lists them; ``converted`` is each place the note converts
    (its next-round conversion, or with no next round its maturity and sale conversions)."""
    bases = {comparison.note_conversion.basis for comparison in rounds}
    maturity = inputs.note_maturity_months
    no_round = not inputs.next_rounds
    months_to_conversion = inputs.note_months_to_conversion
    months_to_exit = inputs.note_months_to_exit
    note_has_terms = inputs.note_valuation_cap is not None or inputs.note_discount_percent is not None
    mfn_safe = any(isinstance(item, SafeTerms) and item.mfn for item in inputs.existing_instruments)
    interest_converts = any(item.accrued > ZERO for item in converted)
    maturity_converts = (
        inputs.note_maturity_conversion_valuation is not None or inputs.note_maturity_conversion_price is not None
    )
    sale_term = inputs.note_change_of_control_multiple is not None or inputs.note_change_of_control_at_cap
    holds: dict[InstrumentFlag, bool] = {
        "no_next_round_given": no_round,
        "cap_below_round_price_now": note_cap is not None and note_cap < price_now,
        "note_converts_at_cap": "cap" in bases,
        "note_converts_at_discount": "discount" in bases,
        "note_converts_at_round_price": "round_price" in bases,
        "note_interest_converts": interest_converts and not inputs.note_interest_paid_in_cash,
        "note_interest_paid_in_cash": interest_converts and inputs.note_interest_paid_in_cash,
        "maturity_not_given": maturity is None,
        "converts_after_maturity": maturity is not None
        and months_to_conversion is not None
        and months_to_conversion > maturity,
        "next_round_below_priced_round_price": any(comparison.priced_price.exact < price_now for comparison in rounds),
        "priced_round_below_existing_series_price": any(
            price_now < fraction(item.invested) / fraction(item.shares) for item in inputs.existing_series
        ),
        "existing_mfn_safe_beside_note": mfn_safe and note_has_terms,
        "discount_unused_without_round": no_round and inputs.note_discount_percent is not None,
        "maturity_conversion_not_given": no_round and maturity is not None and not maturity_converts,
        "change_of_control_not_given": no_round and not sale_term,
        "existing_instruments_outstanding": no_round and bool(inputs.existing_instruments),
        "exit_after_maturity": no_round
        and maturity is not None
        and months_to_exit is not None
        and months_to_exit > maturity,
    }
    return tuple(flag for flag in get_args(InstrumentFlag) if holds[flag])


def compute_instrument_compare(inputs: InstrumentCompareInput) -> InstrumentCompareResult:
    """Option A (priced now) and option B (a note now) worked exactly to each next round and exit, side by side; with
    no next round, to the note's maturity and each sale before any priced round instead.

    Raises ``RoundHasNoPrice`` or ``ConversionDidNotSettle`` (naming the round and option) when a round has no answer,
    and ``NoConversionEquilibrium`` when an exit's convert-or-stay search does not settle.
    """
    founders = fraction(inputs.founder_shares)
    team = fraction(inputs.team_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    series_now = _existing_series(inputs)
    fully_diluted = founders + team + unissued + sum((item.shares for item in series_now), ZERO)
    today_shape = RoundShape(
        fully_diluted,
        unissued,
        inputs.priced_pre_money,
        inputs.investment,
        inputs.priced_target_pool_percent,
        inputs.priced_pool_timing,
        inputs.existing_instruments,
    )
    today = _work(today_shape, "option A's round today")
    terms = inputs.priced_preference
    priced_now = _Table(
        founders,
        team,
        unissued + today.priced.new_pool,
        (
            *series_now,
            *_converted(today, range(len(today.items)), "existing_investors", terms),
            _series("new_money", today.priced.investor_shares, fraction(inputs.investment), terms),
        ),
    )
    note_now = _Table(founders, team, unissued, series_now)
    stakes_now = _stakes(priced_now, note_now)
    # A note's cap price is its pre-money cap over today's FD, the same in every next round and at a sale.
    note_cap = None if inputs.note_valuation_cap is None else fraction(inputs.note_valuation_cap) / fully_diluted
    price_now = today.priced.price
    owed = tuple(_owed_row(months, _interest_at(inputs, months)) for months in inputs.note_owed_months)

    pairs = [
        _next_round(inputs, index, round_terms, priced_now, fully_diluted)
        for index, round_terms in enumerate(inputs.next_rounds, start=_FIRST_INDEX)
    ]
    rounds = tuple(pair.comparison for pair in pairs)
    at_conversion: dict[str, object] = {}
    if pairs:
        interest = note_interest(option_b_note(inputs))
        at_conversion = {
            "note_interest_at_conversion": quantity("money", interest.accrued),
            "note_owed_at_conversion": quantity("money", interest.owed),
            "note_interest_approximate": interest.approximate,
        }
        converted: tuple[NoteInterest, ...] = (interest,)
        no_round = _NoRound(None, None, (), ())
        note_round = pairs[0].note_shape
        tables = [table for pair in pairs for table in (pair.priced_after, pair.note_after)]
    else:
        groups: tuple[HolderGroup, ...] = tuple(stake.group for stake in stakes_now)
        no_round = _no_round(inputs, (priced_now, note_now), groups, fully_diluted, note_cap)
        converted = no_round.converted
        # The round rows of the assumptions read option A's round today with option B's note beside it (its kind only).
        note_round = replace(today_shape, instruments=(*inputs.existing_instruments, option_b_note(inputs, _NO_MONTHS)))
        tables = [priced_now, note_now]

    return InstrumentCompareResult.model_validate(
        {
            "inputs": inputs,
            "fully_diluted_shares": quantity("shares", fully_diluted),
            "priced_price": quantity("price", price_now),
            "priced_new_pool_shares": quantity("shares", today.priced.new_pool),
            "priced_investor_shares": quantity("shares", today.priced.investor_shares),
            "priced_total_shares": quantity("shares", priced_now.total()),
            "priced_conversions": today.rows,
            "note_cap_price": None if note_cap is None else quantity("price", note_cap),
            "note_principal": quantity("money", fraction(inputs.investment)),
            **at_conversion,
            "note_owed": owed,
            "stakes_now": stakes_now,
            "founders_ownership_difference_now": _difference(stakes_now, "founders"),
            "mode": "next_round" if pairs else "no_next_round",
            "next_rounds": rounds,
            "maturity": no_round.maturity,
            "note_at_exit": no_round.note_at_exit,
            "exits_before_any_round": no_round.exits,
            "flags": _flags(inputs, price_now, note_cap, converted, rounds),
            "assumptions": instrument_compare_assumptions(
                inputs,
                note_round,
                ExitShape(ZERO_AMOUNT, ZERO, tuple(item for table in tables for item in table.classes)),
                max(len(table.classes) for table in tables) + _EXTRA_PASSES,
            ),
        }
    )
