"""The labelled assumptions of a runway plan, each with its source; a row appears only when the input uses it.

Two rows quote Y Combinator's "A guide to seed fundraising", read in full: the milestone rule (a startup that will
need a follow-on round raises enough to reach its next fundable milestone) and the runway band (raising for N months,
usually 12 to 18). The default band of 18 months is the top of that range, so the flag is a question, not a shortfall;
the band is a benchmark, not a rule, and an input the founder can change. The time left to raise the next round, the
runway, phase, run-rate, landing and required-raise rules and the tolerances (and the rounding test beside them) are
marked unverified: standard arithmetic or a modelling choice no source was read for, and so is the milestone rule of a
founder's only round (self-funding), which assumes no follow-on round and so cannot rest on the guide's.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.funds import use_of_funds_assumption
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_runway_plan import RunwayPlanInput

__all__ = ["YC_SEED_GUIDE_SOURCE", "runway_plan_assumptions"]

YC_SEED_GUIDE_SOURCE = (
    'Y Combinator, "A guide to seed fundraising", ycombinator.com/library/4A-a-guide-to-seed-fundraising '
    "(no date on the page; read in full 22 Nov 2026)"
)
_MILESTONE_QUOTE = (
    '"raise as much money as needed to get to their next “fundable” milestone, which will usually be 12 to 18 months '
    'later"'
)
_BAND_QUOTE = '"raising for N months (usually 12-18)"'


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _cash_rows(inputs: RunwayPlanInput) -> list[EquityAssumption]:
    """How runway is worked, how phases run, and (with a raise) how the money lands."""
    rows = [
        _assumption(
            "runway_rule",
            f"cash on hand ${inputs.cash_on_hand:,f} less the floor ${inputs.cash_floor:,f}, plus the raise",
            "Runway ends when cash on hand plus the raise, less the floor, first goes below zero under the phased net "
            "burn (gross burn - revenue): no fees, interest or collection lag.",
            f"{UNVERIFIED} (standard arithmetic)",
        ),
        _assumption(
            "phase_rule",
            "a phase runs until the next starts; the last runs on",
            "Each phase's burn and revenue are flat for every month it covers; the last phase runs for as long as "
            "the cash lasts.",
            f"{UNVERIFIED} (a modelling choice)",
        ),
    ]
    if any(phase.revenue_run_rate is not None for case in inputs.cases for phase in case.phases):
        rows.append(
            _assumption(
                "run_rate_rule",
                "revenue a month = the annualised run-rate / 12",
                "A phase's revenue given as an annualised run-rate is twelve times a month's revenue, so the "
                "calculator takes one twelfth of it, exactly, flat for every month the phase covers; the run-rate is "
                "the founder's, not a forecast of growth.",
                f"{UNVERIFIED} (standard arithmetic)",
            )
        )
    if inputs.raises:
        rows.append(
            _assumption(
                "landing_rule",
                "the whole raise lands at once, at the start of month lands_month + 1",
                "A raise lands in one amount after its whole months from today (0: today); cash that is exactly at "
                "the floor as the money lands has not run out. A raise is cash whatever its instrument: a priced "
                "round, a SAFE or a note adds its amount, and nothing converts here.",
                f"{UNVERIFIED} (a modelling choice)",
            )
        )
    if any(not case.phases for case in inputs.cases):
        rows.append(
            _assumption(
                "derived_case_rule",
                "the plan's phases, revenue and gross burn scaled by the case's percents",
                "A downside or lean case given as percents scales each plan phase's revenue and gross burn; a "
                "percent left out is 100. The percents are the founder's: the calculator supplies no default.",
                f"{UNVERIFIED} (a modelling choice)",
            )
        )

    return rows


def _milestone_rows(inputs: RunwayPlanInput) -> list[EquityAssumption]:
    """The milestone rule and the required-raise rule, only with milestones."""
    if not inputs.milestones:
        return []

    required = _assumption(
        "required_raise_rule",
        "the smallest raise that keeps cash at or above the floor through the target month",
        "For each milestone and landing month, the least amount that, landing then, keeps the cash from going "
        "below the floor before the target; none when the cash runs out before it lands.",
        f"{UNVERIFIED} (standard arithmetic)",
    )
    if inputs.milestone_type == "self_funding":
        only_round = _assumption(
            "milestone_rule",
            "covered when the cash lasts to the milestone month; no follow-on round assumed (self-funding)",
            "The founder plans this as the only round, so each milestone is checked at its own month, with no time "
            "left to raise a next one. The seed guide's rule, sizing a raise to the next fundable milestone, is for "
            "a startup that will need a follow-on round, so it is not applied; whether the cash lasts after a "
            "milestone shows in the runway rows, where a runway that ends is the plan running out.",
            f"{UNVERIFIED} (a modelling choice)",
        )
        return [only_round, required]
    if inputs.months_to_raise is None:
        setting = "covered when the cash lasts to the milestone month (no months to raise given)"
    else:
        setting = f"covered when the cash lasts to the milestone month plus {inputs.months_to_raise} months to raise"
    return [
        _assumption(
            "milestone_rule",
            setting,
            "For a startup that will need a follow-on round, a raise is sized to reach its next milestone (the "
            "guide); the milestones and the months to raise are the founder's, and leaving months to raise the "
            f"next round is ours, {UNVERIFIED}.",
            f"{YC_SEED_GUIDE_SOURCE}: {_MILESTONE_QUOTE}",
        ),
        required,
    ]


def _check_rows(inputs: RunwayPlanInput, checked: bool) -> list[EquityAssumption]:
    """The tolerance (when anything was checked), the runway band (with a raise), and the use-of-funds rule."""
    rows = []
    if checked:
        rows.append(
            _assumption(
                "tolerance",
                f"{inputs.tolerance_points:f} points; {inputs.tolerance_percent:f}% relative",
                "A stated runway within this share of the computed one, a use-of-funds total within this share of "
                "the raise, or percent lines within this many points of 100%, is consistent. So is a stated runway "
                "that is the computed one rounded half away from zero to the places it is written with, whatever the "
                "tolerance: people write figures rounded to the places they show, so a whole number holds what "
                "rounds to it and a figure typed with one place holds what rounds to it at one place. The "
                "use-of-funds total is held to the tolerance alone: it is a sum of the lines, not a figure typed as "
                "one. A flag names a runway consistent by the tolerance alone, not a rounding of the computed one.",
                f"{UNVERIFIED} (the rounding test is standard arithmetic)",
            )
        )
    if inputs.raises:
        rows.append(
            _assumption(
                "runway_band",
                f"{inputs.runway_band_months:f} months",
                "A raise whose runway on the plan, from today, is below this many months is flagged as a question, "
                "never an error; the band is an input. The default, 18 months, is the top of the guide's usual 12 to "
                "18, so a raise lasting 12 to 18 months is within the guide's range: the flag asks which milestone it "
                "reaches, not whether it falls short.",
                f"{YC_SEED_GUIDE_SOURCE}: {_BAND_QUOTE} (a common benchmark, not a rule)",
            )
        )
    if any(option.use_of_funds for option in inputs.raises):
        rows.append(use_of_funds_assumption())

    return rows


def runway_plan_assumptions(inputs: RunwayPlanInput, checked: bool) -> tuple[EquityAssumption, ...]:
    """The runway plan's rows, each only when the input uses it."""
    return (*_cash_rows(inputs), *_milestone_rows(inputs), *_check_rows(inputs, checked))
