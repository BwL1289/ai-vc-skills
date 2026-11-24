"""The labelled assumptions of a market size, each with its source; a row appears only when the input uses it.

Two Y Combinator pages are quoted word for word, each read in full: "How to Pitch Your Company" (customers times what
you could charge them, its method for a new product or space; the Bellabeat example's two-year lifecycle; its own
bottom-up, counting comparable products' sales, and why it prefers that to top-down) and "A guide to seed
fundraising" (its glossary: TAM is the total revenue available for what you sell). The pitch guide never calls the
customers-times-price build bottom-up: that name is common usage, marked unverified, and the preference is quoted
beside the build it is about. Neither page defines SAM or SOM, so those rules, the population rule, the sensitivity
and break-even rule and the tolerance are marked unverified: common usage, standard arithmetic or a modelling choice
no source read fixes. No row supplies a market figure: every count, price and share is the founder's.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.assumptions_runway_plan import YC_SEED_GUIDE_SOURCE
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_deal_check import DEFAULT_TOLERANCE_PERCENT
from equity_calculator.schemas.equity_market_sizing import MarketSizingInput

__all__ = [
    "BOTTOM_UP_QUOTE",
    "LIFECYCLE_QUOTE",
    "NEW_SPACE_QUOTE",
    "TAM_GLOSSARY_QUOTE",
    "TOP_DOWN_QUOTE",
    "YC_BOTTOM_UP_QUOTE",
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
# The condition the customers-times-price sentence is given under (the words before it, "If you're", left out).
NEW_SPACE_QUOTE = '"creating a new product or space (like Slack)"'
LIFECYCLE_QUOTE = '"The lifecycle of our activity tracker is two years."'
# The page's own bottom-up, a different build from customers × price: the sentence just before its preference.
YC_BOTTOM_UP_QUOTE = (
    '"With bottom up you figure out where comparable products are sold, how many of them are sold, and what % of '
    'those sales you could take."'
)
TOP_DOWN_QUOTE = (
    '"I prefer the bottom up method because it helps you avoid a common top down pitfall, which is not narrowing down '
    'the customer enough."'
)
TAM_GLOSSARY_QUOTE = '"In pitches, this is the estimated total revenue available for the product(s) you are selling."'


def _years(count: int) -> str:
    return "1 year" if count == 1 else f"{count} years"


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
            f"{YC_PITCH_SOURCE}, question 2, its method for {NEW_SPACE_QUOTE}: {BOTTOM_UP_QUOTE}. The page does "
            f"not call this build bottom-up (its own bottom-up counts comparable products' sales); the name is common "
            f"usage, {UNVERIFIED}",
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
    if not all(segment.market_counted() for segment in inputs.segments):
        rows.append(
            _assumption(
                "no_market_count_rule",
                "no TAM or SAM for a segment with only the customers to win",
                "A segment that gives the customers to win and no count of its whole market (none given, or a count "
                "equal to the customers to win) has no TAM or SAM: they would be the SOM again, not a market size. "
                "Its SOM is worked as usual; the TAM and SAM totals, the shares built on them and the top-down "
                "comparison are not, and a stated TAM or SAM or a population is refused.",
                f"{UNVERIFIED} (a modelling choice)",
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
        horizon = "no horizon given"
        if inputs.som_years is not None:
            horizon = f"in {_years(inputs.som_years)}"
        elif inputs.som_months is not None:
            horizon = f"in {inputs.som_months} month" + ("" if inputs.som_months == 1 else "s")
        rows.append(
            _assumption(
                "som_rule",
                f"SOM = the customers the founder plans to win × annual revenue from one, {horizon}",
                "SOM is the founder's own plan: a count of customers (preferred) or a share of the serviceable ones, "
                "with a straight-line path from today's customers; no compound growth rate is worked.",
                f"{UNVERIFIED} (common usage; neither YC page defines SOM)",
            )
        )
    if any(segment.second_line_percent is not None for segment in inputs.segments):
        rows.append(
            _assumption(
                "second_line_rule",
                "annual revenue from one customer = the main bill × (take rate + second line)",
                "A second revenue line from the same buyer (support, services, a second product) is the founder's "
                "share of the main bill (the buyer's spend on the main line, before the take rate). The company keeps "
                "all of it, so it is added to the take rate; the gross spend includes it; it is held at that share "
                "over the horizon.",
                f"{UNVERIFIED} (a modelling choice)",
            )
        )
    units_segments = [segment for segment in inputs.segments if segment.obtainable_units is not None]
    if units_segments:
        # With a second line the company keeps it too, so the units' SOM is on the take rate plus that line.
        share = (
            "(the take rate + the second line)"
            if any(segment.second_line_percent is not None for segment in units_segments)
            else "the take rate"
        )
        rows.append(
            _assumption(
                "units_rule",
                f"SOM = the units to win × the price a year × {share}",
                "A SOM given in the price's own unit (seats, locations, licences) is worked in that unit, "
                "with no SOM customers, so a unit is never shown as a fraction of a customer.",
                f"{UNVERIFIED} (standard arithmetic)",
            )
        )
    if inputs.top_down:
        rows.append(
            _assumption(
                "top_down_rule",
                "a top-down figure is a cross-check only",
                "A top-down figure (an analyst's or a publisher's) is set beside the bottom-up one, the founder's "
                "comparable share of it only; it never sets the market size or the verdict.",
                f"{YC_PITCH_SOURCE}, question 2 (the preference is for the page's own bottom-up, comparable "
                f"products' sales; that it carries over to customers × price is {UNVERIFIED}): {YC_BOTTOM_UP_QUOTE} "
                f"{TOP_DOWN_QUOTE}",
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
                f"{inputs.tolerance_percent:f}% of the computed figure",
                "A stated TAM, SAM or SOM within this share of the computed one is consistent, the edge included.",
                f"{UNVERIFIED} (deal_check's default is {DEFAULT_TOLERANCE_PERCENT}%)",
            )
        )
    return rows


def market_sizing_assumptions(inputs: MarketSizingInput, checked: bool) -> tuple[EquityAssumption, ...]:
    """The assumptions a market size rests on: how it is built, then SOM and top-down, then the checks."""
    return (*_size_rows(inputs), *_som_rows(inputs), *_check_rows(inputs, checked))
