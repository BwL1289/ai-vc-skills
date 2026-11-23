"""The labelled assumptions of a priced round now set beside a convertible note now, each with its source.

The rounds reuse the ``round`` scenario's rows (``round_assumptions``: the SAFE rows when an existing SAFE converts,
the note rows, the round's price rule, ties, exact shares and the search) and the exits reuse the ``waterfall``
scenario's rows (``waterfall_assumptions``). The rows of the comparison itself follow: what the two options share,
how the note converts and what of its maturity is modelled, which series terms converted shares take, who takes
part in an exit, and how B - A is rounded. No source was read for the comparison's own conventions, so they are
marked unverified or named as a display convention.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.assumptions_round import round_assumptions
from equity_calculator.assumptions_waterfall import waterfall_assumptions
from equity_calculator.convertibles import RoundTerms
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_instrument_compare import InstrumentCompareInput, SeriesTerms

if TYPE_CHECKING:  # instrument_compare imports this module, the waterfall protocol is read for type checks only
    from equity_calculator.waterfall import ExitTerms

# The reused round rows this scenario words its own way: the pool timing differs from round to round here, and the
# payouts, not the holders' value at a round price, are what is split to the cent.
_REWORDED_ROUND_ROWS = frozenset({"pool_timing", "money_split"})
_FIRST = 1


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
    return (
        f"{inputs.note_interest_rate_percent}% a year, {growth}{paid}, for {inputs.note_months_to_conversion} months "
        "until it converts"
    )


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
            "(paid back or converted under its own terms) is not modelled.",
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


def _series_rows(inputs: InstrumentCompareInput) -> list[EquityAssumption]:
    """Which preference each class carries, the standard row when the founder said standard, who takes part."""
    terms = _all_terms(inputs)
    rows = [
        _assumption(
            "series_terms",
            "converted shares take their round's series terms",
            "Shares a SAFE or note converts into carry the terms of the series sold in the round they convert in, "
            "with a preference on the amount converted (not on the shares' value at the round price); the existing "
            "series keep the terms given for them.",
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


def instrument_compare_assumptions(
    inputs: InstrumentCompareInput, note_round: RoundTerms, exits: ExitTerms, pass_limit: int
) -> tuple[EquityAssumption, ...]:
    """The comparison's rows: the rounds' (from ``note_round``, option B's first next round, which holds the note and
    every existing SAFE and note that option A's round today holds), then the comparison's own, then the exits'
    (``exits`` holds every class any exit splits among, ``pass_limit`` the largest search bound)."""
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
    return (
        *round_rows,
        pool_row,
        *_comparison_rows(inputs),
        *_series_rows(inputs),
        *_rounding_rows(),
        *waterfall_assumptions(exits, pass_limit),
    )
