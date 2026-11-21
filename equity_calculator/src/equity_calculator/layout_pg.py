"""The report lines of Paul Graham's two tests: the investor test and the employee test
(``equity_calculator.layout``)."""

from __future__ import annotations

from equity_calculator import investor_live as live
from equity_calculator.schemas.equity import EmployeeResult, InvestorResult
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_INVESTOR_HEADING = 'Investor test (Paul Graham, "The Equity Equation"): is the stake worth what the deal adds?'
_EMPLOYEE_HEADING = "Employee test: the most of the company a hire is worth, n = (i - 1)/i"


def investor_sheet(result: InvestorResult) -> Sheet:
    """The investor test's lines: the stake, the amounts when given, R against the break-even, the verdict.

    When a spreadsheet would work them to the model's answers (``investor_live.spreadsheet_agrees``), every derived
    line is a live formula over the input cells and the inputs are held at full precision; otherwise the sheet holds
    the model's values.
    """
    inputs = result.inputs
    is_live = live.spreadsheet_agrees(result)

    def formula(template: str) -> str:
        return template if is_live else ""

    from_amounts = inputs.pre_money is not None and inputs.investment is not None
    lines = [
        Line(
            "equity_sold",
            "Equity sold (n)",
            (result.equity_sold,),
            GIVEN if inputs.equity_percent is not None else "I/(V + I)",
            formula=formula(live.STAKE_FROM_AMOUNTS) if from_amounts else "",
            full_precision=is_live and not from_amounts,
        )
    ]
    if inputs.pre_money is not None and inputs.investment is not None and result.post_money is not None:
        lines += [
            Line(
                "pre_money",
                "Pre-money valuation (V)",
                (given("money", inputs.pre_money),),
                GIVEN,
                full_precision=is_live,
            ),
            Line(
                "investment",
                "Investment (I)",
                (given("money", inputs.investment),),
                GIVEN,
                full_precision=is_live,
            ),
            Line("post_money", "Post-money valuation", (result.post_money,), "V + I", ("pre_money", "investment")),
        ]

    effect_how = GIVEN if inputs.outcome_multiplier is not None else f"1 + g (g = {inputs.growth_percent}%)"
    lines += [
        Line(
            "outcome_multiplier",
            "Outcome multiplier (m)",
            (result.outcome_multiplier,),
            effect_how,
            full_precision=is_live,
        ),
        Line(
            "value_ratio",
            "Value ratio R",
            (result.value_ratio,),
            "(1 - n)·m: what the holders keep vs. before",
            formula=formula(live.VALUE_RATIO),
        ),
        Line(
            "break_even_multiplier",
            "Break-even multiplier m*",
            (result.break_even_multiplier,),
            "1/(1 - n)",
            formula=formula(live.BREAK_EVEN_MULTIPLIER),
        ),
        Line(
            "break_even_growth",
            "Break-even growth g*",
            (result.break_even_growth,),
            "n/(1 - n) = m* - 1",
            formula=formula(live.BREAK_EVEN_GROWTH),
        ),
        Line(
            "verdict",
            "Verdict",
            (result.verdict,),
            "accept: R > 1; break_even: R = 1; reject: R < 1",
            verdict=True,
            formula=formula(live.VERDICT),
        ),
    ]
    holder = result.holder
    if holder is not None:
        lines += [
            Line(
                "holder_before",
                "Holder's stake before (h)",
                (holder.stake_before,),
                GIVEN,
                full_precision=is_live,
            ),
            Line(
                "holder_after",
                "Holder's stake after",
                (holder.stake_after,),
                "h(1 - n)",
                formula=formula(live.HOLDER_AFTER),
            ),
        ]
        if holder.value_before is not None and holder.value_after is not None:
            lines += [
                Line(
                    "holder_value_before",
                    "Holder's value before",
                    (holder.value_before,),
                    "h·V",
                    formula=formula(live.HOLDER_VALUE_BEFORE),
                ),
                Line(
                    "holder_value_after",
                    "Holder's value after",
                    (holder.value_after,),
                    "h(1 - n)·m·V = h·V·R",
                    formula=formula(live.HOLDER_VALUE_AFTER),
                ),
            ]

    return Sheet("Investor", _INVESTOR_HEADING, ("Value",), tuple(lines), result.assumptions)


def employee_sheet(result: EmployeeResult) -> Sheet:
    """The employee test's lines: the break-even stake and verdict, an offer's test, PG's rule-of-thumb offer."""
    inputs = result.inputs
    effect_how = GIVEN if inputs.outcome_multiplier is not None else f"1 + g (g = {inputs.gain_percent}%)"
    lines = [
        Line("outcome_multiplier", "Hire's outcome multiplier (i)", (result.outcome_multiplier,), effect_how),
        Line("break_even_stake", "Break-even stake n", (result.break_even_stake,), "(i - 1)/i, floored at 0"),
        Line("verdict", "Verdict", (result.verdict,), "grant: i > 1; break_even: i = 1; no_grant: i < 1", verdict=True),
    ]
    offered, needed, offer_verdict = result.offered_stake, result.required_multiplier, result.offer_verdict
    if offered is not None and needed is not None and offer_verdict is not None:
        lines += [
            Line("offered_stake", "Offered stake (o)", (offered,), GIVEN),
            Line("required_multiplier", "Multiplier the offer needs", (needed,), "1/(1 - o)"),
            Line("offer_verdict", "Offer verdict", (offer_verdict,), "accept: (1 - o)·i > 1", verdict=True),
        ]

    rule = result.rule_of_thumb
    if rule is not None and inputs.annual_cost is not None and inputs.valuation is not None:
        lines += [
            Line("annual_cost", "Salary and overhead a year", (given("money", inputs.annual_cost),), GIVEN),
            Line(
                "cost_years",
                "Stock cost in years of salary (× a year)",
                (given("multiplier", inputs.cost_years),),
                GIVEN,
            ),
            Line("stock_cost", "Stock cost of the salary", (rule.stock_cost,), "a year's cost × years"),
            Line("valuation", "Valuation", (given("money", inputs.valuation),), GIVEN),
            Line("cost_stake", "Stake the salary costs", (rule.cost_stake,), "stock cost / valuation"),
            Line("margin", "Company's margin on the hire", (given_percent(inputs.margin_percent),), GIVEN),
            Line("retail_stake", "Retail stake", (rule.retail_stake,), "n/(1 + margin)"),
            Line("offer_stake", "Rule-of-thumb offer", (rule.offer_stake,), "retail - salary's stake, floored at 0"),
            Line(
                "salary_exceeds_value",
                "Salary costs more than the stake",
                (yes_no(rule.salary_exceeds_value),),
                "then the offer is 0",
            ),
        ]

    return Sheet("Employee", _EMPLOYEE_HEADING, ("Value",), tuple(lines), result.assumptions)
