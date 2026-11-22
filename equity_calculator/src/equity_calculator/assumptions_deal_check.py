"""The labelled assumptions of a deal check, each with its source, merged with the nested round's or pool's rows.

Only one rule here has a primary source read in full: post-money = pre-money + the raise, from Y Combinator's
Post-Money Safe User Guide. The runway formula, the order valuations are read in, the tolerances and the two
benchmark bands are marked unverified; each band is a common benchmark, not a rule, and an input the founder can
change. A row appears only when the input uses it.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.assumptions_round import YC_GUIDE_SOURCE
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_deal_check import DealCheckInput, deal_valuation

__all__ = ["deal_check_assumptions"]

_POST_MONEY_QUOTE = (
    '"$2 million at a $10 million pre-money valuation ... the same as saying ... $2 million at a $12 million '
    'post-money valuation"'
)
_BENCHMARK = f"{UNVERIFIED} (a common benchmark, not a rule)"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _valuation_rows(inputs: DealCheckInput) -> list[EquityAssumption]:
    """post = pre + raise always; the reading order with two or more valuations; the back-solve from a percent."""
    rows = [
        _assumption(
            "post_money_rule",
            "post-money = V + I",
            "The post-money valuation is the pre-money plus the raise, and the headline share sold is I/(V + I).",
            f"{YC_GUIDE_SOURCE}: {_POST_MONEY_QUOTE}",
        )
    ]
    stated = (inputs.pre_money, inputs.post_money, inputs.stated_investor_percent)
    if sum(value is not None for value in stated) > 1:
        rows.append(
            _assumption(
                "valuation_order",
                "pre_money, then post_money, then stated_investor_percent",
                "When the deck gives more than one valuation figure, the first in this order sets the pre-money; "
                "the others are checked against it.",
                UNVERIFIED,
            )
        )
    if deal_valuation(inputs)[1] == "percent":
        rows.append(
            _assumption(
                "back_solve",
                "post-money = I / percent",
                "With no valuation given, the stated percent is read as the raise over the post-money, so the "
                "pre-money is I / percent - I (true only with the pool in the pre-money).",
                f"{UNVERIFIED} (standard arithmetic)",
            )
        )

    return rows


def _ownership_rows(inputs: DealCheckInput) -> list[EquityAssumption]:
    """How a holder group's stake is scaled, and what the effective pre-money counts."""
    rows = []
    if inputs.holder_percent is not None:
        rows.append(
            _assumption(
                "holder_scaling",
                "h × (share of the stake every pre-round share keeps)",
                "A group's stake after the round is its share of the pre-round fully diluted shares times the share "
                "of their stake those shares keep: FD/T with a cap table, V/(V + I) without one.",
                UNVERIFIED,
            )
        )
    rows.append(
        _assumption(
            "effective_pre_money",
            "(FD - U) × price",
            "The effective pre-money is what the pre-round holders' shares, the unissued pool excluded, are worth "
            "at the round price; with no share counts it is the pre-money itself.",
            UNVERIFIED,
        )
    )

    return rows


def _runway_rows(inputs: DealCheckInput) -> list[EquityAssumption]:
    """The runway formula and its benchmark band, only when a burn is given."""
    if inputs.planned_monthly_gross_burn is None and inputs.current_monthly_gross_burn is None:
        return []

    return [
        _assumption(
            "runway_rule",
            f"(cash on hand ${inputs.cash_on_hand:,f} + I) / monthly burn",
            "Runway in months is cash on hand plus the raise over the monthly burn, net (gross burn - revenue) and "
            "gross: no fees, the whole raise lands at once, and burn and revenue stay as given.",
            f"{UNVERIFIED} (standard arithmetic)",
        ),
        _assumption(
            "runway_band",
            f"{inputs.runway_band_months} months",
            "Planned net runway below this many months is flagged as something a VC is likely to ask about; it is "
            "a question, never an error, and the band is an input.",
            _BENCHMARK,
        ),
    ]


def _check_rows(inputs: DealCheckInput, checked: bool) -> list[EquityAssumption]:
    """The tolerance (when anything was checked), the dilution band, and the use-of-funds rule."""
    rows = []
    if checked:
        rows.append(
            _assumption(
                "tolerance",
                f"{inputs.tolerance_points} points; {inputs.tolerance_percent}% relative",
                "A stated percent within this many percentage points of the computed one, or a stated money or "
                "months figure within this share of it, is consistent (decks round their figures).",
                UNVERIFIED,
            )
        )
    rows.append(
        _assumption(
            "dilution_band",
            f"{inputs.dilution_band_percent}%",
            "An investor share above this in one round is flagged as something a VC is likely to ask about; it is "
            "a question, never an error, and the band is an input.",
            _BENCHMARK,
        )
    )
    if inputs.use_of_funds:
        rows.append(
            _assumption(
                "use_of_funds_rule",
                "the lines add up to the raise",
                "Use-of-funds lines are checked only for adding up to the raise (or to 100%); percent lines become "
                "dollars of the raise, split to the cent. No split by category is judged.",
                UNVERIFIED,
            )
        )

    return rows


def deal_check_assumptions(
    inputs: DealCheckInput, checked: bool, nested: tuple[EquityAssumption, ...]
) -> tuple[EquityAssumption, ...]:
    """The deal check's rows, then the nested round's or pool's rows whose key is not already listed."""
    rows = [*_valuation_rows(inputs), *_ownership_rows(inputs), *_runway_rows(inputs), *_check_rows(inputs, checked)]
    keys = {row.key for row in rows}

    return (*rows, *(row for row in nested if row.key not in keys))
