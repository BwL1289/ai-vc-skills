"""The labelled assumptions of a market size, each with its source; a row appears only when the input uses it.

Two Y Combinator pages are quoted word for word, each read in full: "How to Pitch Your Company" (customers times what
you could charge them, the Bellabeat example's two-year lifecycle, and why bottom-up beats top-down) and "A guide to
seed fundraising" (its glossary: TAM is the total revenue available for what you sell). Neither page defines SAM or
SOM, so those rules, the population rule, the sensitivity and break-even rule and the tolerance are marked
unverified: common usage, standard arithmetic or a modelling choice no source read fixes. No row supplies a market
figure: every count, price and share is the founder's.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.assumptions_runway_plan import YC_SEED_GUIDE_SOURCE
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_market_sizing import MarketSizingInput

__all__ = [
    "BOTTOM_UP_QUOTE",
    "LIFECYCLE_QUOTE",
    "TAM_GLOSSARY_QUOTE",
    "TOP_DOWN_QUOTE",
    "YC_PITCH_SOURCE",
    "market_sizing_assumptions",
]

YC_PITCH_SOURCE = (
    'Y Combinator, "How to Pitch Your Company", ycombinator.com/library/4b-how-to-pitch-your-company '
    "(no date on the page; read in full 23 Nov 2026)"
)
BOTTOM_UP_QUOTE = (
    '"you can estimate the number of customers that would want your product and approximate how much you could charge '
    'them"'
)
LIFECYCLE_QUOTE = '"The lifecycle of our activity tracker is two years."'
TOP_DOWN_QUOTE = (
    '"I prefer the bottom up method because it helps you avoid a common top down pitfall, which is not narrowing down '
    'the customer enough."'
)
TAM_GLOSSARY_QUOTE = '"In pitches, this is the estimated total revenue available for the product(s) you are selling."'


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _size_rows(inputs: MarketSizingInput) -> list[EquityAssumption]:
    """How TAM is built (always), how a price becomes a year (always), the take rate (when one is below 100%) and
    the SAM rule (always)."""
    rows = [
        _assumption(
            "bottom_up_rule",
            "TAM = customers × annual revenue from one customer, per segment, summed",
            "The market is built from the founder's own count of buying customers and what one of them pays; no "
            "count, price or share is supplied by the calculator.",
            f"{YC_PITCH_SOURCE}, question 2: {BOTTOM_UP_QUOTE}",
        ),
        _assumption(
            "annual_rule",
            "annual price = price × 12 / the months it covers",
            "A price is turned into a year by the months it covers (a two-year device's price counts half a year's "
            "worth each year); no growth, churn or price change is modelled.",
            f"{YC_PITCH_SOURCE}, the Bellabeat example: {LIFECYCLE_QUOTE} The straight-line year is {UNVERIFIED} "
            "(a modelling choice)",
        ),
    ]
    if any(segment.take_rate_percent < 100 for segment in inputs.segments):
        rows.append(
            _assumption(
                "revenue_rule",
                "TAM = the customers' spend × the take rate",
                "The market is the revenue the company can earn, so a marketplace or a payments business counts the "
                "share of the spend it keeps, not the whole spend (shown apart as the gross spend).",
                f"{YC_SEED_GUIDE_SOURCE}, glossary, TAM: {TAM_GLOSSARY_QUOTE}",
            )
        )
    rows.append(
        _assumption(
            "sam_rule",
            "SAM = TAM × serviceable_percent / 100, per segment",
            "SAM is the part of TAM the product can serve and reach today (where it sells, what it integrates "
            "with, its channel), by the founder's own percent; 100% when none is given.",
            f"{UNVERIFIED} (common usage; neither YC page defines SAM)",
        )
    )
    return rows


def _som_rows(inputs: MarketSizingInput) -> list[EquityAssumption]:
    """The SOM rule (with any SOM) and the top-down rule (with a top-down figure)."""
    rows = []
    if any(segment.has_som() for segment in inputs.segments):
        horizon = "no horizon given" if inputs.som_years is None else f"in {inputs.som_years} years"
        rows.append(
            _assumption(
                "som_rule",
                f"SOM = the customers the founder plans to win × annual revenue from one, {horizon}",
                "SOM is the founder's own plan: a count of customers (preferred) or a share of the serviceable ones, "
                "with a straight-line path from today's customers; no compound growth rate is worked.",
                f"{UNVERIFIED} (common usage; neither YC page defines SOM)",
            )
        )
    if inputs.top_down:
        rows.append(
            _assumption(
                "top_down_rule",
                "a top-down figure is a cross-check only",
                "A top-down figure (an analyst's or a publisher's) is set beside the bottom-up one, the founder's "
                "comparable share of it only; it never sets the market size or the verdict.",
                f"{YC_PITCH_SOURCE}, question 2: {TOP_DOWN_QUOTE}",
            )
        )
    return rows


def _check_rows(inputs: MarketSizingInput, checked: bool) -> list[EquityAssumption]:
    """The population rule, the sensitivity rule and the tolerance, each when used."""
    rows = []
    if inputs.population is not None:
        rows.append(
            _assumption(
                "population_rule",
                f"the segments' customers at most {inputs.population:,f}",
                "Segments drawn from one population cannot add up to more than it; when they do, a buyer is likely "
                "counted twice.",
                f"{UNVERIFIED} (standard arithmetic)",
            )
        )
    if inputs.sensitivity:
        rows.append(
            _assumption(
                "sensitivity_rule",
                "one field of one segment at a time, the rest at base",
                "Each value is the founder's own; every total is linear in one field, so the value at which a total "
                "reaches a target is exact.",
                f"{UNVERIFIED} (standard arithmetic)",
            )
        )
    if checked:
        rows.append(
            _assumption(
                "tolerance",
                f"{inputs.tolerance_percent}% of the computed figure",
                "A stated TAM, SAM or SOM within this share of the computed one is consistent, the edge included.",
                f"{UNVERIFIED} (deal_check's default)",
            )
        )
    return rows


def market_sizing_assumptions(inputs: MarketSizingInput, checked: bool) -> tuple[EquityAssumption, ...]:
    """The assumptions a market size rests on: how it is built, then SOM and top-down, then the checks."""
    return (*_size_rows(inputs), *_som_rows(inputs), *_check_rows(inputs, checked))
