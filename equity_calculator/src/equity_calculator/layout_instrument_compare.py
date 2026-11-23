"""A priced round now beside a convertible note now (the ``Priced vs note`` sheet): A, B and B - A in three columns.

The inputs come first (the ones both options share in both columns, an option's own terms in its column), then
today's financing (option A's price, new shares and any existing SAFEs and notes converting; option B's note
outstanding, what it owes when it converts and its cap price), who owns what right after it, then a block per next
round (its terms, each option's price and new shares, the note's conversion in B, who owns what after it, and every
exit's payouts by holder group), then the flags in plain words. A cell that does not apply to an option is empty.
Values only: no line carries a live formula, and no line says which option to take.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity, PoolTiming
from equity_calculator.schemas.equity_instrument_compare import (
    ExitComparison,
    GroupStake,
    HolderGroup,
    InstrumentCompareResult,
    InstrumentFlag,
    NextRound,
    NextRoundComparison,
    SeriesTerms,
)
from equity_calculator.schemas.equity_round import ConversionRow
from equity_calculator.schemas.equity_waterfall import Participation
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Priced vs note"
_HEADING = (
    "A priced round now (A) beside a convertible note now (B): who owns what after today and after each next round, "
    "and who gets what at each exit"
)
_COLUMNS = ("Priced round now (A)", "Note now (B)", "B - A")
_EMPTY = ""
_KIND_NAMES = {"safe": "SAFE", "note": "Note"}
_GROUP_NAMES: dict[HolderGroup, str] = {
    "founders": "founders",
    "team": "team",
    "option_pool": "option pool",
    "existing_investors": "existing investors",
    "new_money": "new money",
    "next_round_investors": "next round's investors",
}
_BASIS_NAMES = {"cap": "its cap price", "discount": "its discount price", "round_price": "the round price"}
_PARTICIPATION_NAMES = {"none": "non-participating", "full": "full participation"}
_SERIES_HOW = "given (standard: 1x, non-participating)"
_OWED_HOW = "principal + interest, to the cent"


def _participation_text(participation: Participation, cap_multiple: Decimal | None) -> str:
    """A class's participation in words: non-participating, full, or up to its cap."""
    if participation == "capped":
        return f"participating up to {cap_multiple}x"
    return _PARTICIPATION_NAMES[participation]


def _series_text(terms: SeriesTerms) -> str:
    """A series' terms in words: standard, or the multiple, participation and rank given."""
    rank = 1 if terms.rank is None else terms.rank
    if terms.standard:
        return f"standard, rank {rank}"
    participation = _participation_text(terms.participation or "none", terms.cap_multiple)
    return f"{terms.preference_multiple}x, {participation}, rank {rank}"


def _both(key: str, label: str, value: EquityQuantity | str, how: str = GIVEN) -> Line:
    """A line both options share: the same value under A and B."""
    return Line(key, label, (value, value, _EMPTY), how)


def _priced(key: str, label: str, value: EquityQuantity | str, how: str = GIVEN) -> Line:
    """A line of option A's only."""
    return Line(key, label, (value, _EMPTY, _EMPTY), how)


def _note(key: str, label: str, value: EquityQuantity | str, how: str = GIVEN) -> Line:
    """A line of option B's only."""
    return Line(key, label, (_EMPTY, value, _EMPTY), how)


def _given_lines(result: InstrumentCompareResult) -> list[Line]:
    """The inputs: what both options share, then option A's terms, then option B's."""
    inputs = result.inputs
    lines = [
        _both("investment", "Raise (I)", given("money", inputs.investment)),
        _both("founder_shares", "Founders' shares today", given("shares", Decimal(inputs.founder_shares))),
        _both("team_shares", "Team's shares and options today", given("shares", Decimal(inputs.team_shares))),
        _both("unissued_pool", "Unissued pool today (U)", given("shares", Decimal(inputs.unissued_pool_shares))),
    ]
    for index, item in enumerate(inputs.existing_series, start=1):
        participation = _participation_text(item.participation, item.cap_multiple)
        terms = f"{item.preference_multiple}x of ${item.invested:,f} invested, {participation}, rank {item.rank}"
        shares = given("shares", Decimal(item.shares))
        lines.append(_both(f"existing_series_{index}", f"Existing series {index}: shares", shares, terms))
    lines += [
        _both("existing_instruments", "Existing SAFEs and notes", str(len(inputs.existing_instruments))),
        _both(
            "fully_diluted",
            "Fully diluted shares today (FD)",
            result.fully_diluted_shares,
            "founders + team + U + existing series",
        ),
        _priced("priced_pre_money", "A: pre-money valuation (V)", given("money", inputs.priced_pre_money)),
        _priced(
            "priced_pool_target", "A: target pool after the round", given_percent(inputs.priced_target_pool_percent)
        ),
        _priced("priced_pool_timing", "A: pool counted in the", inputs.priced_pool_timing.replace("_", "-")),
        _priced("priced_series", "A: series terms", _series_text(inputs.priced_preference), _SERIES_HOW),
    ]
    cap = inputs.note_valuation_cap
    discount = inputs.note_discount_percent
    maturity = inputs.note_maturity_months
    lines += [
        _note("note_cap", "B: valuation cap (pre-money)", "none" if cap is None else given("money", cap)),
        _note("note_discount", "B: discount", "none" if discount is None else given_percent(discount)),
        _note("note_rate", "B: interest rate a year", given_percent(inputs.note_interest_rate_percent)),
        _note("note_compounding", "B: how interest accrues", _interest_text(result)),
        _note("note_months", "B: months until it converts", given("months", Decimal(inputs.note_months_to_conversion))),
        _note("note_maturity", "B: maturity", "not given" if maturity is None else given("months", Decimal(maturity))),
        _note("note_cash", "B: interest paid in cash", yes_no(inputs.note_interest_paid_in_cash)),
        _both("pool_at_exit", "Pool at an exit", inputs.pool_at_exit.replace("_", " ")),
    ]
    return lines


def _interest_text(result: InstrumentCompareResult) -> str:
    inputs = result.inputs
    if inputs.note_compounding == "simple":
        return "simple"
    return f"compounding {inputs.note_compounding}, {inputs.note_stub_rule.replace('_', ' ')} stub"


def _conversion_lines(prefix: str, name: str, row: ConversionRow, in_note: bool) -> list[Line]:
    """One SAFE or note converting: what converts, the price it took (and why) and its shares, in B's or A's column."""
    place = _note if in_note else _priced
    # A SAFE converts its purchase amount; with no cap there is one price only, so nothing for it to be the lower of.
    converting_how = "plus interest unless paid in cash" if row.kind == "note" else "the purchase amount"
    basis = _BASIS_NAMES[row.basis]
    price_how = basis if row.cap_price is None else f"{basis}, the lower"
    return [
        place(f"{prefix}_converting", f"{name}: amount converting", row.converting_amount, converting_how),
        place(f"{prefix}_price", f"{name}: converts at", row.conversion_price, price_how),
        place(f"{prefix}_shares", f"{name}: shares", row.shares, "amount converting / price"),
    ]


def _instrument_name(label: str, row: ConversionRow) -> str:
    """An existing SAFE or note by its place in the inputs, under a section's label."""
    return f"{label}existing {_KIND_NAMES[row.kind]} {row.index}"


def _stake_lines(prefix: str, label: str, stakes: tuple[GroupStake, ...]) -> list[Line]:
    """Each holder group's ownership both ways and B - A."""
    return [
        Line(
            f"{prefix}_{stake.group}",
            f"{label}{_GROUP_NAMES[stake.group]}",
            (stake.priced, stake.note, stake.difference),
            "group's shares / total shares",
        )
        for stake in stakes
    ]


def _note_owed_lines(result: InstrumentCompareResult) -> list[Line]:
    """What option B's note converts when it does: principal + interest, or (interest paid in cash) the principal,
    with the cash interest on its own line."""
    stub = "; approximate stub" if result.note_interest_approximate else ""
    if not result.inputs.note_interest_paid_in_cash:
        return [_note("note_owed", "Note owed when it converts", result.note_owed_at_conversion, f"{_OWED_HOW}{stub}")]
    return [
        _note("note_converting", "Note converting (principal)", result.note_principal, "the interest is paid in cash"),
        _note(
            "note_interest_cash",
            "Note interest paid in cash at conversion",
            result.note_interest_at_conversion,
            f"interest, to the cent{stub}",
        ),
    ]


def _price_how(timing: PoolTiming, shares: str) -> str:
    """How a round's price was worked: the new pool in the price (pre-money timing) or added after the round."""
    if timing == "post_money":
        return f"p = V/({shares} + converted); the new pool is added after the round"
    return f"p = V/({shares} + converted + new pool)"


def _today_lines(result: InstrumentCompareResult) -> list[Line]:
    """Option A's round today, option B's note outstanding, and who owns what right after."""
    price_how = _price_how(result.inputs.priced_pool_timing, "FD")
    lines = [
        _priced("today_price", "Today: price per share", result.priced_price, price_how),
        Line(
            "today_new_pool",
            "Today: new pool shares",
            (result.priced_new_pool_shares, given("shares", Decimal(0)), _EMPTY),
            "to the target (B: no round today)",
        ),
        _priced("today_investor_shares", "Today: new money's shares", result.priced_investor_shares, "I/p"),
    ]
    for row in result.priced_conversions:
        lines += _conversion_lines(
            f"today_{row.kind}_{row.index}", _instrument_name("Today: ", row), row, in_note=False
        )
    lines += [
        Line(
            "today_total",
            "Today: total shares",
            (result.priced_total_shares, result.fully_diluted_shares, _EMPTY),
            "every share after today (B: FD)",
        ),
        _note("note_principal", "Today: note outstanding (principal)", result.note_principal, "the raise"),
        *_note_owed_lines(result),
    ]
    if result.note_cap_price is not None:
        lines.append(_note("note_cap_price", "Note's cap price", result.note_cap_price, "cap / FD"))
    return lines + _stake_lines("today", "Today: ", result.stakes_now)


def _exit_lines(prefix: str, label: str, item: ExitComparison) -> list[Line]:
    """One exit: each group's payout both ways and B - A, then the preferences paid."""
    exit_label = f"{label}exit ${item.exit_amount.rounded:,f}: "
    lines = [
        Line(
            f"{prefix}_{payout.group}",
            f"{exit_label}{_GROUP_NAMES[payout.group]}",
            (payout.priced, payout.note, payout.difference),
            "the waterfall, every preference honoured",
        )
        for payout in item.payouts
    ]
    lines.append(
        Line(
            f"{prefix}_preferences",
            f"{exit_label}preferences paid",
            (item.priced_preferences_paid, item.note_preferences_paid, _EMPTY),
            "classes that stay",
        )
    )
    return lines


def _round_lines(terms: NextRound, comparison: NextRoundComparison) -> list[Line]:
    """One next round: its terms, each option's price and new shares, the note converting, ownership, the exits."""
    prefix = f"round_{comparison.index}"
    label = f"Next round {comparison.index}: "
    lines = [
        _both(f"{prefix}_pre_money", f"{label}pre-money", given("money", terms.pre_money)),
        _both(f"{prefix}_investment", f"{label}raise", given("money", terms.investment)),
        _both(f"{prefix}_pool_target", f"{label}target pool", given_percent(terms.target_pool_percent)),
        _both(f"{prefix}_series", f"{label}series terms", _series_text(terms.preference), _SERIES_HOW),
        Line(
            f"{prefix}_price",
            f"{label}price per share",
            (comparison.priced_price, comparison.note_price, _EMPTY),
            _price_how(terms.pool_timing, "each option's shares"),
        ),
    ]
    for row in comparison.existing_conversions:
        lines += _conversion_lines(f"{prefix}_{row.kind}_{row.index}", _instrument_name(label, row), row, in_note=True)
    lines += _conversion_lines(f"{prefix}_note", f"{label}B's note", comparison.note_conversion, in_note=True)
    lines += [
        Line(
            f"{prefix}_new_pool",
            f"{label}new pool shares",
            (comparison.priced_new_pool_shares, comparison.note_new_pool_shares, _EMPTY),
            "to the target",
        ),
        Line(
            f"{prefix}_investor_shares",
            f"{label}next round's shares",
            (comparison.priced_investor_shares, comparison.note_investor_shares, _EMPTY),
            "raise / price",
        ),
        Line(
            f"{prefix}_total",
            f"{label}total shares",
            (comparison.priced_total_shares, comparison.note_total_shares, _EMPTY),
            "every share after the round",
        ),
        *_stake_lines(prefix, label, comparison.stakes),
    ]
    for index, item in enumerate(comparison.exits, start=1):
        lines += _exit_lines(f"{prefix}_exit_{index}", label, item)
    return lines


def _flag_words(flag: InstrumentFlag, result: InstrumentCompareResult) -> str:
    """What a flag means for the founder, in plain words; none says which option to take."""
    inputs = result.inputs
    words: dict[InstrumentFlag, str] = {
        "cap_below_round_price_now": "The note's cap price is below option A's price per share today: at its cap "
        "the note buys shares for less than option A's investors pay today",
        "note_converts_at_cap": "In at least one next round the note converts at its cap price",
        "note_converts_at_discount": "In at least one next round the note converts at its discount price"
        + ("" if inputs.note_valuation_cap is None else ", which is below its cap price there"),
        "note_converts_at_round_price": "In at least one next round the note converts at the round price: no cap or "
        "discount gave a lower one",
        "note_interest_converts": "The note's interest converts too, so it gets shares for more than the raise",
        "note_interest_paid_in_cash": "Option B pays the note's interest in cash when it converts; that cash is in "
        "no payout line and option A pays none",
        "maturity_not_given": "No maturity was given for the note: what happens if the next round comes late is in "
        "the note's own terms, not modelled here",
        "converts_after_maturity": f"The note matures ({inputs.note_maturity_months} months) before it converts "
        f"({inputs.note_months_to_conversion} months): what happens at maturity is in the note's own terms, not "
        "modelled here",
        "next_round_below_priced_round_price": "A next round prices below option A's price today, a down round for "
        "option A's investors: any anti-dilution adjustment in their terms is not modelled here",
        "priced_round_below_existing_series_price": "Option A's price today is below what an existing series paid "
        "per share (its amount invested over its shares), a down round for that series: any anti-dilution "
        "adjustment in its terms is not modelled here. Option B prices no round today",
        "existing_mfn_safe_beside_note": "An existing MFN SAFE is converted on the terms given for it under both "
        "options. Option B's note is a later instrument with a cap or discount; whether the SAFE may take those "
        "terms is in the SAFE's own terms, not modelled here",
    }
    return words[flag]


def instrument_compare_sheet(result: InstrumentCompareResult) -> Sheet:
    """The comparison's lines: the inputs, today both ways, each next round and its exits, then the flags."""
    lines = _given_lines(result) + _today_lines(result)
    for terms, comparison in zip(result.inputs.next_rounds, result.next_rounds, strict=True):
        lines += _round_lines(terms, comparison)
    lines += [Line(f"flag_{flag}", "Flag", (flag, _EMPTY, _EMPTY), _flag_words(flag, result)) for flag in result.flags]
    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
