"""The employee test: the most of the company a hire is worth, n = (i - 1)/i, and PG's rule-of-thumb offer.

i is the hire's multiplier on the company's average outcome. i above 1 allows a grant of up to n; i exactly 1 is
break even (a zero grant: "there's no reason to do it"); i below 1 grants nothing, a verdict and not an error. An
offered stake o is tested the other way, i = 1/(1 - o): the hire must multiply the outcome by at least that. With
the salary and the valuation given, PG's worked offer follows: the break-even stake less the company's margin, less
the stake the salary costs (``cost_years`` of it, 1.5 by default).
"""

from __future__ import annotations

from fractions import Fraction

from equity_calculator.assumptions import employee_assumptions
from equity_calculator.equation import (
    break_even_multiplier,
    break_even_stake,
    grant_verdict,
    outcome_multiplier,
    trade_verdict,
    value_ratio,
)
from equity_calculator.exact import ONE, ZERO, fraction, from_percent, quantity
from equity_calculator.schemas.equity import EmployeeInput, EmployeeResult, EmployeeRuleOfThumb


def _rule_of_thumb(inputs: EmployeeInput, stake: Fraction) -> EmployeeRuleOfThumb | None:
    """PG's worked offer, or ``None`` without the salary and the valuation."""
    if inputs.annual_cost is None or inputs.valuation is None:
        return None

    stock_cost = fraction(inputs.annual_cost) * fraction(inputs.cost_years)
    cost_stake = stock_cost / fraction(inputs.valuation)
    retail_stake = stake / (ONE + from_percent(inputs.margin_percent))
    surplus = retail_stake - cost_stake

    return EmployeeRuleOfThumb(
        stock_cost=quantity("money", stock_cost),
        cost_stake=quantity("fraction", cost_stake),
        retail_stake=quantity("fraction", retail_stake),
        offer_stake=quantity("fraction", max(ZERO, surplus)),
        salary_exceeds_value=surplus < ZERO,
    )


def compute_employee(inputs: EmployeeInput) -> EmployeeResult:
    """The employee test worked exactly: the break-even stake, the grant verdict, an offer's test, the rule of thumb."""
    hire_multiplier = outcome_multiplier(inputs.outcome_multiplier, inputs.gain_percent)
    stake = break_even_stake(hire_multiplier)
    offered = None if inputs.offered_percent is None else from_percent(inputs.offered_percent)

    return EmployeeResult(
        inputs=inputs,
        outcome_multiplier=quantity("multiplier", hire_multiplier),
        break_even_stake=quantity("fraction", stake),
        verdict=grant_verdict(hire_multiplier),
        offered_stake=None if offered is None else quantity("fraction", offered),
        required_multiplier=None if offered is None else quantity("multiplier", break_even_multiplier(offered)),
        offer_verdict=None if offered is None else trade_verdict(value_ratio(offered, hire_multiplier)),
        rule_of_thumb=_rule_of_thumb(inputs, stake),
        assumptions=employee_assumptions(inputs),
    )
