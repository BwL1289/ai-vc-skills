"""The labelled assumptions of a priced round with SAFEs and notes, each with its source.

The SAFE rules come from Y Combinator's three current post-money SAFE forms (valuation cap, discount, MFN), quoted
word for word. YC has no current form with both a cap and a discount, so the both-terms rule (the lower price wins)
is marked unverified. The round's own price rule is the worked example in YC's Post-Money Safe User Guide. Notes have
no standard form, so their conventions are marked unverified too. SAFE rows appear only when the round has a SAFE,
note rows only when it has a note.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.convertibles import RoundTerms
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_round import NoteTerms, SafeTerms

YC_SOURCE = "Y Combinator, post-money SAFE (valuation cap; discount; MFN), ycombinator.com/documents"
YC_GUIDE_SOURCE = "Y Combinator, Post-Money Safe User Guide (version 1.2, February 2023), ycombinator.com/documents"
_ROUND_PRICE_QUOTE = (
    '"Series A Price per Share = pre-money valuation / (total fully diluted shares post safe conversion + option pool '
    'increase)"'
)
_BOTH_TERMS_NOTE = f"{UNVERIFIED} for a SAFE with both a cap and a discount (YC has no current form with both)"
_COMPANY_CAPITALIZATION_QUOTE = (
    '"Unissued Option Pool, except that any increase to the Unissued Option Pool in connection with the Equity '
    "Financing will only be included to the extent that the number of Promised Options exceeds the Unissued Option "
    'Pool prior to such increase"'
)
_SAFE_PRICE_QUOTE = (
    '"Safe Price" means the price per share equal to the Post-Money Valuation Cap divided by the Company Capitalization'
)
_GREATER_OF_QUOTE = (
    '"convert into the greater of: (1) the number of shares of Standard Preferred Stock equal to the Purchase Amount '
    "divided by the lowest price per share of the Standard Preferred Stock; or (2) the number of shares of Safe "
    'Preferred Stock equal to the Purchase Amount divided by the Safe Price"'
)
_DISCOUNT_QUOTE = (
    '"Discount Price" means the lowest price per share of the Standard Preferred Stock sold in the Equity Financing '
    "multiplied by the Discount Rate"
)
_MFN_QUOTE = (
    '"convert into the number of shares of Standard Preferred Stock equal to the Purchase Amount divided by the '
    'lowest price per share of the Standard Preferred Stock"'
)


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _safe_rows(inputs: RoundTerms) -> list[EquityAssumption]:
    """The rows every round with a SAFE carries, plus the MFN row when one is MFN."""
    rows = [
        _assumption(
            "company_capitalization",
            "FD + every converting share, no pool increase",
            "Company Capitalization C counts every pre-round share (the unissued pool included) and every share "
            "the SAFEs and notes convert into, but not the pool increase made for the round.",
            f"{YC_SOURCE}: {_COMPANY_CAPITALIZATION_QUOTE}",
        ),
        _assumption(
            "promised_options",
            "none",
            "No options are promised beyond the old pool, so none of the round's pool increase enters C.",
            f"{UNVERIFIED} (a simplification of the YC rule quoted under company_capitalization)",
        ),
        _assumption(
            "safe_price_rule",
            "the lower of cap price and discount price",
            "A SAFE converts at the lower of its cap price K/C and its other price (the round price times "
            "1 - discount, the round price itself with no discount): the greater number of shares.",
            f"{YC_SOURCE}: {_SAFE_PRICE_QUOTE}; {_GREATER_OF_QUOTE}; {_DISCOUNT_QUOTE}; {_BOTH_TERMS_NOTE}",
        ),
    ]
    if any(isinstance(item, SafeTerms) and item.mfn for item in inputs.instruments):
        rows.append(
            _assumption(
                "mfn",
                "the terms given, else the round price",
                "An MFN SAFE converts on the cap and discount it is given (the terms it took from a later "
                "instrument); with neither it converts at the round price. Which later instrument's terms it may "
                "take is not worked out here.",
                f"{YC_SOURCE} (MFN form): {_MFN_QUOTE}",
            )
        )

    return rows


def _note_rows() -> list[EquityAssumption]:
    """The rows every round with a note carries."""
    return [
        _assumption(
            "note_cap_basis",
            "pre-money cap over FD",
            "A note's cap is a pre-money cap: its cap price is the cap over the fully diluted pre-round shares FD "
            "(the unissued pool included; other SAFEs and notes and the new pool not).",
            f"{UNVERIFIED} (notes have no standard form; terms vary)",
        ),
        _assumption(
            "note_interest",
            "each note's own; default yearly with a fractional-power stub",
            "By default a note compounds yearly (n = 1) and its stub raises the growth to the fractional number of "
            "periods, P(1 + r/n)^(whole + stub) (approximate, 50 digits; a whole number of periods has no stub and "
            "stays exact). A note may instead name monthly compounding (n = 12), the simple stub rule (whole "
            "periods compound and the stub earns simple interest, P(1 + r/n)^whole·(1 + (r/n)·stub), exact) or "
            "simple interest, P(1 + r·years).",
            UNVERIFIED,
        ),
        _assumption(
            "day_count",
            "actual days over 365 (or 360)",
            "A note dated by issue and conversion dates runs the actual days between them over its day count's "
            "year; months_outstanding runs months/12 years.",
            UNVERIFIED,
        ),
        _assumption(
            "interest_rounding",
            "to the cent, half-even",
            "The amount a note owes is rounded to the cent before it converts.",
            UNVERIFIED,
        ),
        _assumption(
            "interest_conversion",
            "accrued interest converts",
            "A note converts its principal plus accrued interest, or the principal alone when the interest is paid "
            "in cash (interest_paid_in_cash).",
            UNVERIFIED,
        ),
    ]


def round_assumptions(inputs: RoundTerms) -> tuple[EquityAssumption, ...]:
    """The round's assumptions; SAFE rows only with a SAFE, note rows only with a note."""
    rows = _safe_rows(inputs) if any(isinstance(item, SafeTerms) for item in inputs.instruments) else []
    if any(isinstance(item, NoteTerms) for item in inputs.instruments):
        rows += _note_rows()

    rows += [
        _assumption(
            "converted_shares_in_pre_money",
            "V buys every pre-round and converted share",
            "The pre-money valuation buys the pre-round shares, every converted SAFE and note share and, pool "
            "pre-money, the new pool: p = V/(C + P).",
            f"{YC_GUIDE_SOURCE}, worked example: {_ROUND_PRICE_QUOTE} (notes converting the same way: {UNVERIFIED})",
        ),
        _assumption(
            "pool_timing",
            inputs.pool_timing,
            "pre_money: the new pool is made inside the pre-money valuation, before the round; post_money: it is "
            "topped up after the round, diluting the investor too.",
            UNVERIFIED,
        ),
        _assumption(
            "tie_rule",
            "a tie takes the cap",
            "When an instrument's cap price equals its other price it is shown converting at its cap (the shares "
            "are the same either way).",
            "display convention",
        ),
        _assumption(
            "fractional_shares",
            "exact",
            "Converted, pool and investor shares are exact fractions; nothing is rounded to whole shares.",
            UNVERIFIED,
        ),
        _assumption(
            "search",
            "from every cap, at most one pass more than the capped instruments",
            "Every capped instrument starts on its cap; each pass prices the round and keeps an instrument on its "
            "cap exactly when its cap price is at most its other price, until a pass changes nothing.",
            "method (each pass is exact; a round that does not settle is refused, not guessed)",
        ),
        _assumption(
            "money_split",
            "largest remainder",
            "Each holder's value at the round price is rounded to the cent so the rows add up to the rounded total.",
            "display convention",
        ),
    ]

    return tuple(rows)
