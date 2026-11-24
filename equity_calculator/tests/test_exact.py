"""Exactness: rounding half away from zero by integers, largest-remainder cents, the models' refusals, no global
decimal context.

Pure arithmetic: no DB, no network. Every result carries an exact ``Fraction`` and a ``Decimal`` rounded from it; a
caller's ``decimal.localcontext()`` must not change either, so the same inputs are worked inside a hostile context
(2 digits, rounding up, Inexact trapped) and compared byte for byte.
"""

from __future__ import annotations

import decimal
import random
from decimal import ROUND_UP, Decimal
from fractions import Fraction

import pytest
from equity_calculator.exact import DISPLAY_PLACES, quantity, round_to_places, split_cents
from equity_calculator.layout import sheet_for
from equity_calculator.rounding import round_half_away, rounds_to
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import (
    EmployeeInput,
    EquityQuantity,
    EquityResult,
    EquityUnit,
    InvestorInput,
    PoolInput,
    ScenarioInput,
)
from equity_calculator.schemas.equity_common import round_half_away_whole
from equity_calculator.schemas.equity_deal_check import DealCheckInput
from equity_calculator.schemas.equity_dilution import DilutionInput
from equity_calculator.schemas.equity_market_sizing import MarketSizingInput
from equity_calculator.schemas.equity_metrics_check import MetricsCheckInput
from equity_calculator.schemas.equity_round import RoundInput
from equity_calculator.schemas.equity_runway_plan import RunwayPlanInput
from equity_calculator.schemas.equity_vesting import VestingInput
from equity_calculator.schemas.equity_waterfall import WaterfallInput
from equity_calculator.text import display, render_sheet
from pydantic import RootModel, ValidationError
from tests.support import POOL_EXAMPLE

_SEED = 20261118
_CASES = 500
_HOSTILE_PRECISION = 2


class _ResultRoundTrip(RootModel[EquityResult]):
    """Any scenario's result, read back from its JSON (the ``EquityResult`` union)."""


_FIRST = 0
_CAP_MULTIPLE = "3.25"
_CAPPED_INVESTED = "5125000"
# The exit sits where class 1's cap binds (3.25 x 5,125,000 = 16,656,250 is its payout), so the cap decides a number
# the context test compares. Below that band the cap is still worked out but moves nothing, so no test there sees it.
_CAPPED_WATERFALL = WaterfallInput.model_validate(
    {
        "exit_amount": "75125000",
        "common_shares": 7_000_000,
        "classes": [
            {
                "shares": 2_000_000,
                "invested": _CAPPED_INVESTED,
                "preference_multiple": "1.25",
                "participation": "capped",
                "cap_multiple": _CAP_MULTIPLE,
            },
            {"shares": 1_000_000, "invested": "10250000", "rank": 2},
        ],
    }
)

# One example per scenario, the new ones with values of 3 or more significant digits, worked in a 2-digit, round-up
# context that traps Inexact. A step that reads that context changes such a value (a 1- or 2-digit one it leaves as it
# was), and a step that copies it and sets its own digits (the localcontext() idiom) raises on its first inexact result.
# A copy that also resets the traps is not seen: at its own digits the caller's rounding and exponent range leave these
# cents as they are. The round's note compounds yearly for 19 months with a fractional_power stub, so its power is
# inexact and its 19/12 exponent and growth 1.0775 do not fit in 2 digits; the waterfall's capped class is paid exactly
# its cap, so the cap's two factors (3.25 and 5,125,000) are read too.
_EXAMPLES: tuple[ScenarioInput, ...] = (
    InvestorInput(
        pre_money=Decimal("8000000"),
        investment=Decimal("2000000"),
        outcome_multiplier=Decimal("1.3"),
        holder_percent=Decimal("37.5"),
    ),
    EmployeeInput(
        gain_percent=Decimal("20"),
        annual_cost=Decimal("60000"),
        valuation=Decimal("2000000"),
        margin_percent=Decimal("50"),
        offered_percent=Decimal("7"),
    ),
    PoolInput.model_validate(POOL_EXAMPLE),
    PoolInput.model_validate({**POOL_EXAMPLE, "share_rounding": "whole_shares", "pool_timing": "post_money"}),
    RoundInput.model_validate(
        {
            "fully_diluted_shares": 10_250_000,
            "unissued_pool_shares": 512_500,
            "pre_money": "16250000",
            "investment": "4125000",
            "target_pool_percent": "10.5",
            "instruments": [
                {"kind": "safe", "purchase_amount": "512500", "valuation_cap": "5125000"},
                {
                    "kind": "note",
                    "principal": "512500",
                    "interest_rate_percent": "7.75",
                    "compounding": "annual",
                    "stub_rule": "fractional_power",
                    "months_outstanding": 19,
                    "valuation_cap": "6250000",
                    "discount_percent": "17.5",
                },
            ],
        }
    ),
    DilutionInput.model_validate(
        {
            "holder_percent": "37.5",
            "rounds": [
                {"investor_percent": "17.5", "pool_percent": "7.25"},
                {"pre_money": "24125000", "investment": "6375000", "pool_percent": "2.75"},
                {"investor_percent": "12.75"},
            ],
        }
    ),
    VestingInput.model_validate(
        {
            "grant_shares": 48_000,
            "month": 30,
            "strike_price": "0.125",
            "common_price": "2.375",
            "termination_month": 27,
            "acceleration": "double_trigger",
            "acceleration_percent": "62.5",
            "change_of_control_month": 24,
        }
    ),
    _CAPPED_WATERFALL,
    # A deal check worked from its post-money, so the validator's V = post - I runs in the hostile context too: a
    # SAFE with a cap and a discount, a pool topped up to 10.5%, a holder group, both burns and amount lines.
    DealCheckInput.model_validate(
        {
            "investment": "4125000",
            "post_money": "20375000",
            "stated_investor_percent": "20.25",
            "fully_diluted_shares": 10_250_000,
            "unissued_pool_shares": 512_500,
            "target_pool_percent": "10.5",
            "instruments": [
                {
                    "kind": "safe",
                    "purchase_amount": "512500",
                    "valuation_cap": "5125000",
                    "discount_percent": "17.5",
                }
            ],
            "holder_percent": "87.5",
            "stated_holder_percent": "62.5",
            "cash_on_hand": "312500",
            "planned_monthly_gross_burn": "187500",
            "planned_monthly_revenue": "12500",
            "current_monthly_gross_burn": "112500",
            "current_monthly_revenue": "7500",
            "stated_runway_months": "22.5",
            "use_of_funds": [{"amount": "2062500"}, {"amount": "1237500"}, {"amount": "825000"}],
        }
    ),
    # A runway plan with every part: a floor, a derived downside, a lean case of its own, a raise landing later with
    # a runway stated from landing, percent use-of-funds lines, two milestones and months to raise.
    RunwayPlanInput.model_validate(
        {
            "cash_on_hand": "812500",
            "cash_floor": "62500",
            "cases": [
                {
                    "name": "plan",
                    "phases": [
                        {"from_month": 1, "gross_burn": "137500", "revenue": "12500"},
                        {"from_month": 5, "gross_burn": "212500", "revenue": "37500"},
                    ],
                },
                {"name": "downside", "revenue_percent_of_plan": "62.5", "gross_burn_percent_of_plan": "105"},
                {"name": "lean", "phases": [{"from_month": 1, "gross_burn": "112500", "revenue": "7500"}]},
            ],
            "raises": [
                {"amount": "2125000"},
                {
                    "amount": "3125000",
                    "lands_month": 3,
                    "stated_runway_months": "17.5",
                    "stated_runway_from": "landing",
                    "use_of_funds": [{"percent": "62.5"}, {"percent": "37.5"}],
                },
            ],
            "milestones": [9, 14],
            "months_to_raise": 5,
            "stated_runway_months": "5.5",
        }
    ),
    # A metrics check with every part: an annual unit, the starting customers' own movements, a month with one-time
    # and usage revenue, customers, spend and margin, burn, concentration, every stated figure and a segment band.
    MetricsCheckInput.model_validate(
        {
            "period_months": 7,
            "recurring_unit": "annual",
            "starting_recurring": "1312500",
            "new_recurring": "437500",
            "expansion_recurring": "112500",
            "contraction_recurring": "37500",
            "churned_recurring": "87500",
            "cohort_expansion_recurring": "62500",
            "cohort_contraction_recurring": "12500",
            "cohort_churned_recurring": "62500",
            "month_total_revenue": "162500",
            "month_one_time_revenue": "12500",
            "month_usage_revenue": "7500",
            "customers_start": 333,
            "customers_lost": 17,
            "customers_new": 61,
            "customers_new_paid": 23,
            "sales_marketing_spend": "487500",
            "gross_margin_percent": "72.5",
            "net_burn": "912500",
            "largest_customer_revenue": "137500",
            "period_revenue": "862500",
            "stated_arr": "1750000",
            "stated_nrr_percent": "103",
            "stated_grr_percent": "94",
            "stated_churn_percent": "5.1",
            "stated_cac": "8000",
            "stated_cac_payback_months": "18.5",
            "stated_burn_multiple": "2.3",
            "stated_concentration_percent": "16",
            "customer_segment": "mid_market",
        }
    ),
    # A market size with every part: odd prices and periods, units, take rates, both SOM forms, customers today, two
    # top-down figures (one against SAM), a sensitivity row per kind of field, a population and every stated figure.
    MarketSizingInput.model_validate(
        {
            "segments": [
                {
                    "customers": "12345",
                    "price": "333.33",
                    "price_period_months": 7,
                    "units_per_customer": "3",
                    "take_rate_percent": "12.5",
                    "serviceable_percent": "37",
                    "obtainable_customers": "1001",
                    "customers_today": "17",
                },
                {
                    "customers": "678.5",
                    "price": "1999",
                    "price_period_months": 24,
                    "serviceable_percent": "83",
                    "obtainable_percent": "6.6",
                    "customers_today": "0",
                },
            ],
            "top_down": [{"amount": "98765432", "comparable_percent": "33"}, {"amount": "1e7", "compare_to": "sam"}],
            "sensitivity": [
                {"field": "price", "segment": 1, "values": ["111.11", "777"]},
                {"field": "obtainable_percent", "segment": 2, "values": ["1.1", "9.9"]},
                {"field": "customers", "segment": 2, "values": ["500"]},
            ],
            "population": "13000",
            "annual_revenue_today": "123456.78",
            "som_years": 3,
            "som_target": "2000000",
            "stated_tam": "70000000",
            "stated_sam": "26000000",
            "stated_som": "2500000",
        }
    ),
)
_EXAMPLE_IDS = [
    "investor",
    "employee",
    "pool",
    "pool-whole-post",
    "round-note-stub",
    "dilution",
    "vesting-double-trigger",
    "waterfall-capped",
    "deal-check-from-post-money",
    "runway-plan-with-a-late-raise",
    "metrics-check-with-every-part",
    "market-sizing-with-every-part",
]


@pytest.mark.parametrize(
    ("value", "places", "expected"),
    [
        (Fraction(1, 8), 2, "0.13"),  # 12.5 cents rounds away from zero to 13, never to the even 12
        (Fraction(3, 8), 2, "0.38"),  # 37.5 rounds to 38
        (Fraction(-1, 8), 2, "-0.13"),
        (Fraction(97, 8), 2, "12.13"),  # 12.125 prints 12.13, as the rounding test rounds it
        (Fraction(-97, 8), 2, "-12.13"),
        (Fraction(5, 2), 0, "3"),
        (Fraction(-5, 2), 0, "-3"),
        (Fraction(-1, 1000), 2, "0.00"),  # a negative that rounds to nothing prints a plain zero
        (Fraction(2, 3), 6, "0.666667"),
        (Fraction(5), 2, "5.00"),
        (Fraction(19_000_000, 7), 3, "2714285.714"),
    ],
)
def test_round_to_places_is_half_away_from_zero_with_fixed_places(value: Fraction, places: int, expected: str) -> None:
    """Rounding is half away from zero on the exact fraction, and the result always carries exactly ``places``
    places."""
    rounded = round_to_places(value, places)

    assert str(rounded) == expected
    assert rounded.as_tuple().exponent == -places


@pytest.mark.parametrize(
    "value",
    [Fraction(97, 8), Fraction(-97, 8), Fraction(1, 2), Fraction(-1, 2), Fraction(5, 10**7), Fraction(-5, 10**7)],
    ids=["12.125", "minus-12.125", "0.5", "minus-0.5", "a-half-at-the-seventh-place", "minus-that"],
)
@pytest.mark.parametrize("unit", sorted(DISPLAY_PLACES))
def test_every_printed_figure_is_what_the_rounding_test_rounds_to(unit: EquityUnit, value: Fraction) -> None:
    """A figure the report prints is the computed one rounded half away from zero, the rule ``rounds_to`` applies to a
    document's figure, so a deck that copies the report's figure (12.13 for 12.125, not 12.12) holds."""
    shown = quantity(unit, value)
    # The figure as the report prints it, its unit's marks taken off: "12.13 months", "$12.13", "-12.1250%".
    printed = Decimal(display(shown).removesuffix(" months").strip("$%x").replace(",", ""))
    percent = unit == "fraction"

    assert Fraction(shown.rounded) == round_half_away(value, DISPLAY_PLACES[unit])
    assert Fraction(printed) == round_half_away(value * 100 if percent else value, DISPLAY_PLACES[unit] - 2 * percent)
    assert rounds_to(printed, unit, value) is (None if unit == "money" else True)


def test_each_unit_rounds_to_its_display_places() -> None:
    """Fractions, multipliers and prices keep 6 places, money 2, shares 3, months 2, counts of customers 2."""
    assert DISPLAY_PLACES == {
        "fraction": 6,
        "multiplier": 6,
        "money": 2,
        "price": 6,
        "shares": 3,
        "months": 2,
        "count": 2,
    }
    for unit, places in DISPLAY_PLACES.items():
        assert quantity(unit, Fraction(1, 3)).rounded.as_tuple().exponent == -places


def test_a_fraction_prints_as_its_rounded_value_with_the_point_moved_two_places() -> None:
    """The skills tell an agent on the MCP path, which returns a share as a fraction, to show it as a percent by moving
    the decimal point of ``rounded`` two places: that must be exactly what the command line's report prints."""
    rng = random.Random(20261122)
    values = [Fraction(0), Fraction(1), Fraction(1, 6), Fraction(-1, 30), Fraction(1, 20), Fraction(2, 3)]
    values += [Fraction(rng.randint(-(10**9), 10**9), rng.randint(1, 10**7)) for _ in range(500)]
    for value in values:
        shown = quantity("fraction", value)
        assert display(shown) == f"{shown.rounded.scaleb(2):,f}%", value


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        ((Fraction(1, 3),) * 3, (34, 33, 33)),  # a tie goes to the earlier part
        ((Fraction(1, 200), Fraction(1, 200)), (1, 0)),  # half a cent each: one cent in all
        ((Fraction(1, 400), Fraction(1, 400)), (1, 0)),  # half a cent in all rounds away from zero to one cent
        ((Fraction(7_600_000), Fraction(3_200_000, 3), Fraction(2_000_000)), (760_000_000, 106_666_667, 200_000_000)),
        ((), ()),
    ],
)
def test_split_cents_by_largest_remainder(parts: tuple[Fraction, ...], expected: tuple[int, ...]) -> None:
    """Each part floors to whole cents and the leftover cents go to the largest remainders."""
    assert split_cents(parts) == expected


def test_split_cents_refuses_a_negative_part() -> None:
    """A negative dollar value is never split: it would mean a cap-table row worth less than nothing."""
    with pytest.raises(ValueError, match="non-negative parts only"):
        split_cents([Fraction(1), Fraction(-1, 100)])


def test_property_cents_add_up_and_stay_within_a_cent() -> None:
    """On random parts: the cents sum to the total rounded to the cent, and each part moves by less than a cent."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        parts = [Fraction(rng.randint(0, 10**9), rng.randint(1, 997)) for _ in range(rng.randint(1, 6))]
        cents = split_cents(parts)

        assert sum(cents) == round_half_away_whole(sum(parts) * 100)
        assert all(abs(cent - part * 100) < 1 for cent, part in zip(cents, parts, strict=True))


def _rendered(inputs: ScenarioInput) -> tuple[str, str]:
    result = compute(inputs)
    return result.model_dump_json(), render_sheet(sheet_for(result))


@pytest.mark.parametrize("inputs", _EXAMPLES, ids=_EXAMPLE_IDS)
def test_a_callers_decimal_context_changes_nothing(inputs: ScenarioInput) -> None:
    """In a 2-digit, round-up context that traps Inexact, every result and report is identical; the context survives."""
    expected = _rendered(inputs)

    with decimal.localcontext(prec=_HOSTILE_PRECISION, rounding=ROUND_UP) as hostile:
        hostile.traps[decimal.Inexact] = True
        assert _rendered(inputs) == expected
        assert _rendered(type(inputs).model_validate_json(inputs.model_dump_json())) == expected  # parsed in context
        assert decimal.getcontext() is hostile
        assert (hostile.prec, hostile.rounding, hostile.traps[decimal.Inexact]) == (_HOSTILE_PRECISION, ROUND_UP, True)


def test_the_context_waterfall_pays_its_capped_class_exactly_the_cap() -> None:
    """The waterfall the context test works is one where the cap binds, so a cap read in the caller's context shows."""
    row = compute(_CAPPED_WATERFALL).rows[_FIRST]

    assert row.capped is True
    assert row.converts is False
    assert row.payout.exact == Fraction(_CAP_MULTIPLE) * Fraction(_CAPPED_INVESTED)


@pytest.mark.parametrize("inputs", _EXAMPLES, ids=_EXAMPLE_IDS)
def test_results_round_trip_through_json_with_exact_fractions(inputs: ScenarioInput) -> None:
    """JSON carries each fraction as "a/b"; reading it back (by its scenario tag) gives the same result."""
    result = compute(inputs)

    assert _ResultRoundTrip.model_validate_json(result.model_dump_json()).root == result


def test_json_writes_a_fraction_as_numerator_over_denominator() -> None:
    """The pool example's price, 14/19 of a dollar, is written exactly."""
    assert '"exact":"14/19"' in compute(PoolInput.model_validate(POOL_EXAMPLE)).model_dump_json()


def test_models_are_frozen_and_closed() -> None:
    """A computed quantity or an input cannot be changed after the fact, and unknown fields are refused."""
    item = quantity("money", Fraction(1))
    inputs = InvestorInput(equity_percent=Decimal("7"), outcome_multiplier=Decimal("1.1"))

    with pytest.raises(ValidationError, match="frozen"):
        item.rounded = Decimal("2")
    with pytest.raises(ValidationError, match="frozen"):
        inputs.equity_percent = Decimal("8")
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        EquityQuantity.model_validate({"unit": "money", "exact": "1", "rounded": "1.00", "note": "x"})


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"equity_percent": "NaN", "outcome_multiplier": "1.1"}, "finite number"),
        ({"equity_percent": "Infinity", "outcome_multiplier": "1.1"}, "finite number"),
        ({"equity_percent": "100", "outcome_multiplier": "1.1"}, "less than 100"),
        ({"equity_percent": "0", "outcome_multiplier": "1.1"}, "greater than 0"),
        ({"equity_percent": "7", "growth_percent": "-100"}, "greater than -100"),
        ({"equity_percent": "7", "outcome_multiplier": "0"}, "greater than 0"),
        ({"equity_percent": "7", "outcome_multiplier": "1.1", "holder_percent": "100.01"}, "less than or equal to 100"),
        ({"equity_percent": "7"}, "give exactly one of outcome_multiplier, growth_percent (got 0)"),
        ({"equity_percent": "7", "outcome_multiplier": "1.1", "growth_percent": "10"}, "(got 2)"),
        ({"outcome_multiplier": "1.1"}, "give exactly one of equity_percent, pre_money with investment (got 0)"),
        ({"pre_money": "8", "outcome_multiplier": "1.1"}, "give pre_money and investment together"),
        ({"equity_percent": "7", "pre_money": "8", "investment": "2", "outcome_multiplier": "1.1"}, "(got 2)"),
    ],
)
def test_investor_inputs_are_refused_with_a_reason(fields: dict[str, str], message: str) -> None:
    """Out-of-range stakes, non-finite numbers and ambiguous inputs are refused, each with its reason."""
    with pytest.raises(ValidationError) as caught:
        InvestorInput.model_validate(fields)

    assert message in str(caught.value)


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({}, "give exactly one of outcome_multiplier, gain_percent (got 0)"),
        ({"gain_percent": "20", "annual_cost": "60000"}, "give annual_cost and valuation together"),
        ({"gain_percent": "20", "offered_percent": "100"}, "less than 100"),
        ({"gain_percent": "20", "margin_percent": "-1"}, "greater than or equal to 0"),
        ({"gain_percent": "20", "cost_years": "0"}, "greater than 0"),
    ],
)
def test_employee_inputs_are_refused_with_a_reason(fields: dict[str, str], message: str) -> None:
    """The employee test refuses an ambiguous effect, half the rule-of-thumb inputs, or an out-of-range offer."""
    with pytest.raises(ValidationError) as caught:
        EmployeeInput.model_validate(fields)

    assert message in str(caught.value)
