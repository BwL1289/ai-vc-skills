"""Exactness: half-even rounding by integers, largest-remainder cents, the models' refusals, no global decimal context.

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
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import (
    EmployeeInput,
    EquityQuantity,
    EquityResult,
    InvestorInput,
    PoolInput,
    ScenarioInput,
)
from equity_calculator.schemas.equity_deal_check import DealCheckInput
from equity_calculator.schemas.equity_dilution import DilutionInput
from equity_calculator.schemas.equity_round import RoundInput
from equity_calculator.schemas.equity_vesting import VestingInput
from equity_calculator.schemas.equity_waterfall import WaterfallInput
from equity_calculator.text import render_sheet
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
]


@pytest.mark.parametrize(
    ("value", "places", "expected"),
    [
        (Fraction(1, 8), 2, "0.12"),  # 12.5 cents rounds to the even 12
        (Fraction(3, 8), 2, "0.38"),  # 37.5 rounds to the even 38
        (Fraction(-1, 8), 2, "-0.12"),
        (Fraction(2, 3), 6, "0.666667"),
        (Fraction(5), 2, "5.00"),
        (Fraction(19_000_000, 7), 3, "2714285.714"),
    ],
)
def test_round_to_places_is_half_even_with_fixed_places(value: Fraction, places: int, expected: str) -> None:
    """Rounding is half-even on the exact fraction, and the result always carries exactly ``places`` places."""
    rounded = round_to_places(value, places)

    assert str(rounded) == expected
    assert rounded.as_tuple().exponent == -places


def test_each_unit_rounds_to_its_display_places() -> None:
    """Fractions, multipliers and prices keep 6 places, money 2, shares 3, months 2."""
    assert DISPLAY_PLACES == {"fraction": 6, "multiplier": 6, "money": 2, "price": 6, "shares": 3, "months": 2}
    for unit, places in DISPLAY_PLACES.items():
        assert quantity(unit, Fraction(1, 3)).rounded.as_tuple().exponent == -places


@pytest.mark.parametrize(
    ("parts", "expected"),
    [
        ((Fraction(1, 3),) * 3, (34, 33, 33)),  # a tie goes to the earlier part
        ((Fraction(1, 200), Fraction(1, 200)), (1, 0)),  # half a cent each: one cent in all
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

        assert sum(cents) == round(sum(parts) * 100)
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
