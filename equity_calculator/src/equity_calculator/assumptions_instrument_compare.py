"""The labelled assumptions of a priced round now set beside a convertible note now, each with its source.

The rounds reuse the ``round`` scenario's rows (``round_assumptions``: the SAFE rows when an existing SAFE converts,
the note rows, the round's price rule, ties, exact shares and the search) and the exits reuse the ``waterfall``
scenario's rows (``waterfall_assumptions``). The rows of the comparison itself follow: what the two options share,
how the note converts and what of its maturity is modelled, which series terms converted shares take, who takes
part in an exit, and how B - A is rounded. With no next round given, the comparison's own rows say what that mode
shows instead: the note at its maturity and at a sale before any priced round, each on the note's own terms; the round
rows for a conversion that never happens are left out, and the waterfall's exit row is worded for both options (option
B's note may be paid out of a sale first). No source was read for the comparison's own conventions, so they are marked
unverified or named as a display convention.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.assumptions_round import round_assumptions
from equity_calculator.assumptions_waterfall import waterfall_assumptions
from equity_calculator.convertibles import RoundTerms
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_instrument_compare import InstrumentCompareInput, SeriesTerms
from equity_calculator.schemas.equity_round import NoteTerms

if TYPE_CHECKING:  # instrument_compare imports this module, the waterfall protocol is read for type checks only
    from equity_calculator.waterfall import ExitTerms

# The reused round rows this scenario words its own way: the pool timing differs from round to round here, and the
# payouts, not the holders' value at a round price, are what is split to the cent.
_REWORDED_ROUND_ROWS = frozenset({"pool_timing", "money_split"})
_FIRST = 1
# The waterfall's row this scenario words its own way with no next round: option B's note may be paid out of a sale
# before the shareholders share the rest.
_EXIT_ROW = "exit_is_shared_amount"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _all_terms(inputs: InstrumentCompareInput) -> list[SeriesTerms]:
    return [inputs.priced_preference, *(item.preference for item in inputs.next_rounds)]


def _note_terms_text(inputs: InstrumentCompareInput) -> str:
    """The note's interest terms as given, in words."""
    if inputs.note_compounding == "simple":
        growth = "simple interest"
    else:
        growth = f"compounding {inputs.note_compounding}, stub rule {inputs.note_stub_rule}"
    paid = ", paid in cash" if inputs.note_interest_paid_in_cash else ""
    months = inputs.note_months_to_conversion
    if months is None:
        return f"{inputs.note_interest_rate_percent}% a year, {growth}{paid}, for the months each line names"
    return f"{inputs.note_interest_rate_percent}% a year, {growth}{paid}, for {months} months until it converts"


def _comparison_rows(inputs: InstrumentCompareInput) -> list[EquityAssumption]:
    """What the two options share, and how the note converts."""
    maturity = inputs.note_maturity_months
    maturity_setting = "not given" if maturity is None else f"{maturity} months, compared only"
    return [
        _assumption(
            "comparison_rule",
            "the same raise, next rounds and exits both ways",
            "Option A sells priced shares for the raise now; option B issues a note for the same amount now. Each "
            "next round's pre-money, amount, pool top-up and series terms, and each exit, are the same for both "
            "options, as the founder gave them. Each next round is an alternative for the one round after today, "
            "worked from today's cap table; the next rounds are not one after another. The comparison shows both "
            "side by side and never says which to take.",
            "method",
        ),
        _assumption(
            "note_outstanding_today",
            "no shares until the next round",
            "Right after today's financing option B issues no shares: the note is outstanding (its principal now, "
            "principal plus interest when it converts), so today's ownership counts only shares.",
            f"{UNVERIFIED} (notes have no standard form; terms vary)",
        ),
        _assumption(
            "note_price_rule",
            "the lower of cap price and discount price",
            "At each next round the note converts what it owes at the lower of its cap price (the cap over today's "
            "fully diluted shares FD) and its discount price (the round price times 1 - discount); with neither it "
            "converts at the round price.",
            f"{UNVERIFIED} (notes have no standard form; terms vary)",
        ),
        _assumption(
            "note_interest_terms",
            "as the founder gave them",
            f"The note accrues {_note_terms_text(inputs)}; the amount owed is rounded to the cent.",
            "the founder's terms",
        ),
        _assumption(
            "maturity_rule",
            maturity_setting,
            "The note's maturity is only compared with the months until it converts: no repayment, extension or "
            "conversion at maturity is modelled, and the note is taken to convert at the next round however late.",
            f"{UNVERIFIED} (what happens at maturity is in the note's own terms)",
        ),
        _assumption(
            "exit_after_next_round",
            "every exit follows the next round",
            "Each exit is after the next round, when the note has converted; an exit while the note is outstanding "
            "(paid back or converted under its own terms) is not worked here, only with no next round given.",
            "method",
        ),
        _assumption(
            "existing_instruments_rule",
            "convert at the first priced round",
            "Existing SAFEs and notes convert at the first priced round: today's in option A, the next round in "
            "option B, an existing note accruing for the months until then. An existing MFN SAFE converts on the "
            "terms given for it under both options: option B's note is a later instrument, and whether the SAFE may "
            "take the note's cap or discount is in the SAFE's own terms, not modelled here.",
            f"{UNVERIFIED} (each instrument's own terms decide)",
        ),
    ]


def _maturity_setting(inputs: InstrumentCompareInput) -> str:
    """The maturity row's setting with no next round: not given, or the months and the conversion term given."""
    maturity = inputs.note_maturity_months
    if maturity is None:
        return "not given"
    if inputs.note_maturity_conversion_valuation is not None:
        return f"{maturity} months: repaid, or converted at a ${inputs.note_maturity_conversion_valuation:,f} valuation"
    if inputs.note_maturity_conversion_price is not None:
        return f"{maturity} months: repaid, or converted at ${inputs.note_maturity_conversion_price:,f} a share"
    return f"{maturity} months: what it owes then; no conversion term given"


def _sale_setting(inputs: InstrumentCompareInput) -> str:
    """The sale row's setting with no next round: the note's change-of-control term as given, or not given."""
    if inputs.note_change_of_control_multiple is not None:
        return f"{inputs.note_change_of_control_multiple}x the principal, before any share"
    if inputs.note_change_of_control_at_cap:
        return f"converts at its cap price, owing {inputs.note_months_to_exit} months' interest"
    return "no change-of-control term given"


def _cap_and_discount_rows(inputs: InstrumentCompareInput) -> list[EquityAssumption]:
    """With no next round, a note's discount has no price to come off, and its cap sets a price only at a sale on the
    converts-at-its-cap term: one row each for a discount and a cap given."""
    rows = []
    if inputs.note_valuation_cap is not None:
        rows.append(
            _assumption(
                "note_cap_rule",
                "applies only where the note converts at it",
                "A note's cap price (cap / FD) sets the price it converts at only at a priced round (where it is the "
                "lower price) or at a sale on a converts-at-its-cap term; with no next round it changes a figure here "
                "only at a sale worked on that term.",
                f"{UNVERIFIED} (notes have no standard form; terms vary)",
            )
        )
    if inputs.note_discount_percent is not None:
        rows.append(
            _assumption(
                "note_discount_rule",
                "applies only at a priced round",
                "A note's discount comes off a priced round's price; with no next round it changes no figure here.",
                f"{UNVERIFIED} (notes have no standard form; terms vary)",
            )
        )
    return rows


def _no_round_rows(inputs: InstrumentCompareInput) -> list[EquityAssumption]:
    """What the two options share with no next round, and how the note is shown at maturity and at a sale."""
    return [
        _assumption(
            "comparison_rule",
            "no next round: today, the note at maturity, each sale before any priced round",
            "Option A sells priced shares for the raise now; option B issues a note for the same amount now. No next "
            "round was given, so the note never converts at a priced round here: the comparison shows who owns what "
            "right after today, what the note owes at each month named, the note at its maturity on its own terms, "
            "and each exit as a sale before any priced round, the same for both options, as the founder gave them. "
            "It shows both side by side and never says which to take.",
            "method",
        ),
        _assumption(
            "note_outstanding_today",
            "no shares while it is outstanding",
            "Right after today's financing option B issues no shares: the note is outstanding (its principal now, "
            "principal plus interest at each month named), so today's ownership counts only shares.",
            f"{UNVERIFIED} (notes have no standard form; terms vary)",
        ),
        _assumption(
            "note_interest_terms",
            "as the founder gave them",
            f"The note accrues {_note_terms_text(inputs)}; the amount owed is rounded to the cent.",
            "the founder's terms",
        ),
        _assumption(
            "maturity_rule",
            _maturity_setting(inputs),
            "At its maturity the note owes its principal plus interest to then, to the cent: the repayment shown. "
            "With a maturity conversion valuation (taken over today's fully diluted shares FD, as the cap is) or "
            "price from the founder, it is also shown converting what it owes (the principal alone when the "
            "interest is paid in cash) into shares at that price, with who owns what then beside option A right "
            "after today. Whether it is repaid, converted or extended is in the note's own terms; the comparison "
            "shows each figure and never says which happens.",
            f"{UNVERIFIED} (what happens at maturity is in the note's own terms)",
        ),
        _assumption(
            "exit_before_any_round",
            _sale_setting(inputs),
            "Each exit is a sale before any priced round. Option A's sale splits A's cap table after today through "
            "the waterfall. Under option B the note is still outstanding and is paid its change-of-control term from "
            "the founder: a multiple of its principal (the principal alone, no interest), paid before any share and "
            "never more than the sale, with the rest split among the shares; or what it owes at the sale (the "
            "principal alone when the interest is paid in cash) converted at its cap price (cap / FD) into common "
            "shares, which share the rest with the founders, the team and the pool after any preference; interest "
            "paid in cash at that conversion is not taken off the sale and is in no payout line. With no term given, "
            "or with existing SAFEs or notes still outstanding, option B is not worked at that sale and the row says "
            "why. A term that adds interest to the multiple, or gives the holder the greater of the two, is not "
            "modelled.",
            f"{UNVERIFIED} (the note's own terms decide)",
        ),
        *_cap_and_discount_rows(inputs),
        _assumption(
            "existing_instruments_rule",
            "convert in option A's round today; outstanding under option B",
            "Existing SAFEs and notes convert in option A's round today. Under option B no priced round comes, so "
            "they stay outstanding: they hold no shares in its ownership lines, and option B is not worked at a sale "
            "while they are outstanding, as what each is paid then is in its own terms.",
            f"{UNVERIFIED} (each instrument's own terms decide)",
        ),
    ]


def _series_rows(inputs: InstrumentCompareInput) -> list[EquityAssumption]:
    """Which preference each class carries, the standard row when the founder said standard, who takes part."""
    terms = _all_terms(inputs)
    if inputs.next_rounds:
        series = (
            "converted shares take their round's series terms",
            "Shares a SAFE or note converts into carry the terms of the series sold in the round they convert in, "
            "with a preference on the amount converted (not on the shares' value at the round price); the existing "
            "series keep the terms given for them.",
        )
    else:
        series = (
            "option A's series terms; option B's note converts into common",
            "Option A's new money and the SAFEs and notes converting in its round today carry the terms given for "
            "that series, with a preference on the amount invested or converted; the existing series keep the terms "
            "given for them. Option B's note, converted at its cap at a sale, takes common shares; converted at "
            "maturity, only its shares are counted.",
        )
    rows = [
        _assumption(
            "series_terms",
            *series,
            f"{UNVERIFIED} (shadow series and their preferences vary by deal)",
        ),
        _assumption(
            "series_rank",
            "rank 1 when not given",
            "A series, new or existing, with no rank given is rank 1: it shares its preference pro rata with every "
            "other rank-1 class.",
            "method",
        ),
    ]
    if any(item.standard for item in terms):
        rows.append(
            _assumption(
                "standard_preference",
                "1x, non-participating",
                "A series given as standard is owed 1x what it invested and does not participate; it is used only "
                "where the founder said the terms are standard.",
                f"{UNVERIFIED} (the usual preferred-stock terms; no source was read for them)",
            )
        )
    pool_setting = "the pool takes part as common" if inputs.pool_at_exit == "as_common" else "the pool is left out"
    rows.append(
        _assumption(
            "pool_at_exit",
            pool_setting,
            "as_common counts every option-pool share as granted and exercised, the same fully diluted basis as "
            "the ownership lines; left_out gives the pool nothing, as unexercised options take nothing.",
            "method",
        )
    )
    return rows


def _rounding_rows() -> list[EquityAssumption]:
    return [
        _assumption(
            "money_split",
            "largest remainder within each option",
            "Each option's payouts at an exit are rounded to the cent so they add up to the exit.",
            "display convention",
        ),
        _assumption(
            "difference_rounding",
            "B - A of the exact values, rounded once",
            "Every B - A is worked on the exact values and rounded once, so it can differ by a cent from the "
            "difference of the two rounded payouts.",
            "display convention",
        ),
    ]


def _exit_amount_row(row: EquityAssumption) -> EquityAssumption:
    """The waterfall's exit row worded for both options with no next round, its key and source kept."""
    return row.model_copy(
        update={
            "setting": "option A: nothing ahead of the shareholders; option B: only the note's own claim",
            "statement": "Under option A the exit amount is what the shareholders share. Under option B the note's "
            "change-of-control claim, when it is a multiple of the principal, is paid out of the exit amount first "
            "and the shareholders share the rest. Nothing else is taken out first under either option: no other "
            "debt, fees, escrow, accrued dividends or option exercise cash.",
        }
    )


def _no_round_round_rows(inputs: InstrumentCompareInput, rows: list[EquityAssumption]) -> list[EquityAssumption]:
    """With no next round, the round rows for a conversion that happens: only option A's round today converts the
    existing SAFEs and notes, and option B's note converts only at its maturity or at a worked sale at its cap."""
    existing_notes = [item for item in inputs.existing_instruments if isinstance(item, NoteTerms)]
    maturity_converts = (
        inputs.note_maturity_conversion_valuation is not None or inputs.note_maturity_conversion_price is not None
    )
    sale_converts = inputs.note_change_of_control_at_cap and not inputs.existing_instruments
    keep = {
        "note_cap_basis": inputs.note_valuation_cap is not None
        or any(item.valuation_cap is not None for item in existing_notes),
        "interest_conversion": maturity_converts or sale_converts or bool(existing_notes),
        "tie_rule": bool(inputs.existing_instruments),
        "search": bool(inputs.existing_instruments),
    }
    return [row for row in rows if keep.get(row.key, True)]


def instrument_compare_assumptions(
    inputs: InstrumentCompareInput, note_round: RoundTerms, exits: ExitTerms, pass_limit: int
) -> tuple[EquityAssumption, ...]:
    """The comparison's rows: the rounds' (from ``note_round``, option B's first next round, which holds the note and
    every existing SAFE and note that option A's round today holds; with no next round, option A's round today with
    the note beside it), then the comparison's own, then the exits' (``exits`` holds every class any exit splits
    among, ``pass_limit`` the largest search bound)."""
    round_rows = [row for row in round_assumptions(note_round) if row.key not in _REWORDED_ROUND_ROWS]
    timings = ", ".join(
        [f"option A today {inputs.priced_pool_timing}"]
        + [f"next round {index} {item.pool_timing}" for index, item in enumerate(inputs.next_rounds, start=_FIRST)]
    )
    pool_row = _assumption(
        "pool_timing",
        timings,
        "pre_money: a round's new pool is made inside its pre-money valuation, before the round; post_money: it is "
        "topped up after the round, diluting that round's investor too. A round with no top-up target adds no pool.",
        UNVERIFIED,
    )
    exit_rows = waterfall_assumptions(exits, pass_limit)
    if inputs.next_rounds:
        comparison_rows = _comparison_rows(inputs)
    else:
        round_rows = _no_round_round_rows(inputs, round_rows)
        comparison_rows = _no_round_rows(inputs)
        exit_rows = tuple(_exit_amount_row(row) if row.key == _EXIT_ROW else row for row in exit_rows)
    return (
        *round_rows,
        pool_row,
        *comparison_rows,
        *_series_rows(inputs),
        *_rounding_rows(),
        *exit_rows,
    )
