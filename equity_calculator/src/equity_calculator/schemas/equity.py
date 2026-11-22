"""Pydantic models for the equity calculator (``equity_calculator``): the investor and employee tests, and the unions.

``equity_calculator`` turns each input decimal into a ``fractions.Fraction`` and does every step exactly (how the
decimals are read: ``equity_calculator.schemas.equity_common``). Each computed number is an ``EquityQuantity``: the
exact fraction plus one half-even rounding of it for display, so the CLI, the JSON and the workbook all show the same
rounding of the same exact answer. Percent fields take percent points (``7`` means 7%).

A scenario is an input and a result model sharing a ``scenario`` tag; ``EquityInput`` and ``EquityResult`` are the
tagged unions, so a later scenario only adds members. The shared parts (config, units, ``EquityQuantity``,
``EquityAssumption``) live in ``equity_calculator.schemas.equity_common`` and are re-exported here under their old
names.
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
    EquityUnit,
    PoolTiming,
    ShareRounding,
    exactly_one,
)
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealCheckResult
from equity_calculator.schemas.equity_dilution import DilutionInput, DilutionResult
from equity_calculator.schemas.equity_pool import (
    CapTableGroup,
    CapTableRow,
    PoolCapTable,
    PoolInput,
    PoolResult,
    PoolScenario,
)
from equity_calculator.schemas.equity_round import RoundInput, RoundResult
from equity_calculator.schemas.equity_vesting import VestingInput, VestingResult
from equity_calculator.schemas.equity_waterfall import WaterfallInput, WaterfallResult
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "CapTableGroup",
    "CapTableRow",
    "DealCheckInput",
    "DealCheckResult",
    "DilutionInput",
    "DilutionResult",
    "EmployeeInput",
    "EmployeeResult",
    "EmployeeRuleOfThumb",
    "EmployeeScenario",
    "EquityAssumption",
    "EquityInput",
    "EquityQuantity",
    "EquityResult",
    "EquityUnit",
    "GrantVerdict",
    "HolderOutcome",
    "InvestorInput",
    "InvestorResult",
    "InvestorScenario",
    "PoolCapTable",
    "PoolInput",
    "PoolResult",
    "PoolScenario",
    "PoolTiming",
    "RoundInput",
    "RoundResult",
    "ScenarioInput",
    "ScenarioResult",
    "ShareRounding",
    "TradeVerdict",
    "VestingInput",
    "VestingResult",
    "WaterfallInput",
    "WaterfallResult",
]

# Each scenario's tag, the discriminator of ``EquityInput`` and ``EquityResult``. ``investor``: sell part of the
# company for what the deal does to its average outcome (Paul Graham, "The Equity Equation"). ``employee``: the
# largest stake a hire is worth, n = (i - 1)/i. ``pool``: the option-pool shuffle of a priced round.
InvestorScenario = Literal["investor"]
EmployeeScenario = Literal["employee"]

# PG's test of a trade of stock, R = (1 - n)·m. ``accept`` R > 1: what the holders keep is worth more than the
# whole company was. ``break_even`` R exactly 1: no gain, so no reason to trade ("if the company merely breaks
# even on the deal, there's no reason to do it"). ``reject`` R < 1.
TradeVerdict = Literal["accept", "break_even", "reject"]

# What a hire's outcome multiplier i allows. ``grant`` i > 1: up to n = (i - 1)/i of the company. ``break_even``
# i exactly 1: the hire adds nothing, the break-even grant is 0. ``no_grant`` i < 1: the hire makes things worse.
GrantVerdict = Literal["grant", "break_even", "no_grant"]

# PG's rule of thumb: "multiply the annual rate by about 1.5" to turn salary and overhead into stock, because a
# company growing 3x a year pays next year's salary out of next year's valuation.
_DEFAULT_COST_YEARS = Decimal("1.5")


class InvestorInput(BaseModel):
    """PG's investor test: is the stake ``n`` worth selling for what the deal does to the company's average outcome?

    The stake is ``equity_percent``, or ``investment`` and ``pre_money`` together (n = I/(V + I)). The deal's effect
    is ``outcome_multiplier`` (m, the whole effect on the average outcome, cash included) or ``growth_percent``
    (m = 1 + g/100). ``holder_percent`` (optional) is one holder's stake before the round.
    """

    model_config = MODEL_CONFIG

    scenario: InvestorScenario = "investor"
    equity_percent: BoundedDecimal | None = Field(default=None, gt=0, lt=WHOLE_PERCENT)
    pre_money: BoundedDecimal | None = Field(default=None, gt=0)
    investment: BoundedDecimal | None = Field(default=None, gt=0)
    outcome_multiplier: BoundedDecimal | None = Field(default=None, gt=0)
    growth_percent: BoundedDecimal | None = Field(default=None, gt=-WHOLE_PERCENT)
    holder_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)

    @model_validator(mode="after")
    def _one_stake_and_one_effect(self) -> InvestorInput:
        """Refuse an input with no way, or two ways, to read the stake sold or the deal's effect."""
        if (self.pre_money is None) != (self.investment is None):
            raise ValueError("give pre_money and investment together")

        # pre_money stands for the pair: the check above makes the two given together or not at all.
        exactly_one(("equity_percent", "pre_money with investment"), (self.equity_percent, self.pre_money))
        exactly_one(("outcome_multiplier", "growth_percent"), (self.outcome_multiplier, self.growth_percent))
        return self


class EmployeeInput(BaseModel):
    """The employee test: the most of the company a hire is worth, from what they do to its average outcome.

    The hire's effect is ``outcome_multiplier`` (i) or ``gain_percent`` (i = 1 + g/100). ``offered_percent``
    (optional) is a stake to test against it. ``annual_cost`` and ``valuation`` (optional, together) turn on PG's
    rule-of-thumb lines: salary and overhead cost ``cost_years`` years of pay in stock, and the company wants a
    ``margin_percent`` "profit" on the hire (0 means it only breaks even).
    """

    model_config = MODEL_CONFIG

    scenario: EmployeeScenario = "employee"
    outcome_multiplier: BoundedDecimal | None = Field(default=None, gt=0)
    gain_percent: BoundedDecimal | None = Field(default=None, gt=-WHOLE_PERCENT)
    offered_percent: BoundedDecimal | None = Field(default=None, ge=0, lt=WHOLE_PERCENT)
    annual_cost: BoundedDecimal | None = Field(default=None, gt=0)
    valuation: BoundedDecimal | None = Field(default=None, gt=0)
    margin_percent: BoundedDecimal = Field(default=Decimal(0), ge=0)
    cost_years: BoundedDecimal = Field(default=_DEFAULT_COST_YEARS, gt=0)

    @model_validator(mode="after")
    def _one_effect_and_whole_rule_of_thumb(self) -> EmployeeInput:
        """Refuse an input with no way, or two ways, to read the hire's effect, or half the rule-of-thumb inputs."""
        exactly_one(("outcome_multiplier", "gain_percent"), (self.outcome_multiplier, self.gain_percent))
        if (self.annual_cost is None) != (self.valuation is None):
            raise ValueError("give annual_cost and valuation together (the rule-of-thumb lines need both)")

        return self


class HolderOutcome(BaseModel):
    """One holder's stake through an investor round; the values are dollars and need ``pre_money``."""

    model_config = MODEL_CONFIG

    stake_before: EquityQuantity
    stake_after: EquityQuantity
    value_before: EquityQuantity | None = None
    value_after: EquityQuantity | None = None


class InvestorResult(BaseModel):
    """PG's investor test, worked: R = (1 - n)·m against the break-even m* = 1/(1 - n) and g* = n/(1 - n)."""

    model_config = MODEL_CONFIG

    scenario: InvestorScenario = "investor"
    inputs: InvestorInput
    equity_sold: EquityQuantity
    outcome_multiplier: EquityQuantity
    value_ratio: EquityQuantity
    break_even_multiplier: EquityQuantity
    break_even_growth: EquityQuantity
    verdict: TradeVerdict
    post_money: EquityQuantity | None = None
    holder: HolderOutcome | None = None
    assumptions: tuple[EquityAssumption, ...]


class EmployeeRuleOfThumb(BaseModel):
    """PG's worked offer: the break-even stake less the margin, less the stake the salary costs."""

    model_config = MODEL_CONFIG

    stock_cost: EquityQuantity
    cost_stake: EquityQuantity
    retail_stake: EquityQuantity
    offer_stake: EquityQuantity
    salary_exceeds_value: bool


class EmployeeResult(BaseModel):
    """The employee test, worked: n = (i - 1)/i, and for an offered stake the multiplier it needs, i = 1/(1 - n)."""

    model_config = MODEL_CONFIG

    scenario: EmployeeScenario = "employee"
    inputs: EmployeeInput
    outcome_multiplier: EquityQuantity
    break_even_stake: EquityQuantity
    verdict: GrantVerdict
    offered_stake: EquityQuantity | None = None
    required_multiplier: EquityQuantity | None = None
    offer_verdict: TradeVerdict | None = None
    rule_of_thumb: EmployeeRuleOfThumb | None = None
    assumptions: tuple[EquityAssumption, ...]


# Every scenario's input and result, as plain unions for signatures (``compute``, ``sheet_for``); a new scenario
# adds one member to each. ``EquityInput`` and ``EquityResult`` are the same unions tagged for validation.
ScenarioInput = (
    InvestorInput
    | EmployeeInput
    | PoolInput
    | RoundInput
    | DilutionInput
    | VestingInput
    | WaterfallInput
    | DealCheckInput
)
ScenarioResult = (
    InvestorResult
    | EmployeeResult
    | PoolResult
    | RoundResult
    | DilutionResult
    | VestingResult
    | WaterfallResult
    | DealCheckResult
)

EquityInput = Annotated[ScenarioInput, Field(discriminator="scenario")]
EquityResult = Annotated[ScenarioResult, Field(discriminator="scenario")]
