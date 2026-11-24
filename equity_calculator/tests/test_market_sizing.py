"""``market_sizing``: a founder's market worked bottom-up, exactly, with its checks, cross-checks, ranges and flags.

Pure arithmetic: no DB, no network, nothing written. Expected values are exact fractions worked by hand:

- Company AW, vet-clinic software. Segment 1: $400 a month is $4,800 a year, so TAM 18,000 · 4,800 = $86.4M, SAM
  10,800 · 4,800 = $51.84M, SOM 900 · 4,800 = $4.32M, 900/45 = 20x today, (900 - 45)/5 = 171 a year. Segment 2: 15
  locations at $300 a month is $54,000 a year, TAM 400 · 54,000 = $21.6M, SAM 200 · 54,000 = $10.8M, SOM 20 ·
  54,000 = $1.08M. Totals $108M, $62.64M (29/50 of TAM), $5.4M (5/58 of SAM, 50/3x the $324k revenue today). The
  analyst's $2.1B at 40% is $840M; the bottom-up TAM is 9/70 of it. SOM reaches $8M at a price of
  400 · (8M - 1.08M)/4.32M = 17,300/27 (about $640.74), at 900 · 6.92/4.32 = 4,325/3 clinics, or at a share of
  10 · (8M - 4.32M)/1.08M = 920/27 percent.
- Company AX, a pool marketplace keeping 15% of $1,800 a year: $270 per pool. TAM 6,500,000 · 270 = $1.755B against
  a gross spend of $11.7B (the deck's figure), SAM 1,750,000 · 270 = $472.5M, SOM 35,000 · 270 = $9.45M. The take
  rate at which TAM equals the $1.1B top-down figure is 15 · (1.1B - 675M)/1.08B = 425/72 percent.
"""

from __future__ import annotations

import json
import random
import re
from decimal import Decimal
from fractions import Fraction
from typing import get_args

import pytest
from equity_calculator.assumptions_market_sizing import (
    BOTTOM_UP_QUOTE,
    LIFECYCLE_QUOTE,
    NEW_SPACE_QUOTE,
    TAM_GLOSSARY_QUOTE,
    TOP_DOWN_QUOTE,
    YC_BOTTOM_UP_QUOTE,
)
from equity_calculator.exact import given_price, price_quantity
from equity_calculator.layout import sheet_for
from equity_calculator.market_sizing import compute_market_sizing
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_market_sizing import (
    MAX_SEGMENTS,
    MAX_SENSITIVITIES,
    MAX_SENSITIVITY_VALUES,
    MAX_TOP_DOWN,
    MarketSizingFlag,
    MarketSizingInput,
    MarketSizingResult,
    SensitivityResult,
)
from equity_calculator.text import display, render_sheet
from pydantic import ValidationError
from tests.support import MARKET_AW, MARKET_AX, market_sizing

_SEED = 20261123
_CASES = 200
# The quoted words, typed out here from the pages read, so a change to a quote in the code fails this test.
_BOTTOM_UP_WORDS = (
    "you can estimate the number of customers that would want your product and approximate how much you could charge "
    "them"
)
_LIFECYCLE_WORDS = "The lifecycle of our activity tracker is two years."
_TOP_DOWN_WORDS = (
    "I prefer the bottom up method because it helps you avoid a common top down pitfall, which is not narrowing down "
    "the customer enough."
)
_GLOSSARY_WORDS = "In pitches, this is the estimated total revenue available for the product(s) you are selling."
_NEW_SPACE_WORDS = "creating a new product or space (like Slack)"
_YC_BOTTOM_UP_WORDS = (
    "With bottom up you figure out where comparable products are sold, how many of them are sold, and what % of those "
    "sales you could take."
)
_ONE_SEGMENT: dict[str, object] = {"customers": "1000", "price": "100"}


def _with(segment: dict[str, object] | None = None, **fields: object) -> dict[str, object]:
    """One segment (``_ONE_SEGMENT`` with ``segment``'s fields) and the input's other ``fields``."""
    return {"segments": [{**_ONE_SEGMENT, **(segment or {})}], **fields}


def test_company_aw_segments_totals_and_the_deck() -> None:
    result = market_sizing(**MARKET_AW)
    one, two = result.segments

    assert one.annual_value_per_customer.exact == 4_800
    assert (one.tam.exact, one.sam_customers.exact, one.sam.exact) == (86_400_000, 10_800, 51_840_000)
    assert one.som_customers is not None and one.som is not None
    assert (one.som_customers.exact, one.som.exact) == (900, 4_320_000)
    assert one.share_of_tam.exact == Fraction(4, 5)
    assert one.som_multiple_of_today is not None and one.som_multiple_of_today.exact == 20
    assert one.new_customers_per_year is not None and one.new_customers_per_year.exact == 171
    assert two.annual_value_per_customer.exact == 54_000
    assert (two.tam.exact, two.sam.exact) == (21_600_000, 10_800_000)
    assert two.som is not None and two.som.exact == 1_080_000
    assert two.new_customers_per_year is not None and two.new_customers_per_year.exact == Fraction(18, 5)

    totals = result.totals
    assert (totals.customers.exact, totals.gross_spend.exact, totals.tam.exact) == (18_400, 108_000_000, 108_000_000)
    assert (totals.sam_customers.exact, totals.sam.exact) == (11_000, 62_640_000)
    assert totals.som_customers is not None and totals.som is not None
    assert (totals.som_customers.exact, totals.som.exact) == (920, 5_400_000)
    assert totals.sam_share_of_tam.exact == Fraction(29, 50)
    assert totals.som_share_of_sam is not None and totals.som_share_of_sam.exact == Fraction(5, 58)
    multiple = totals.som_multiple_of_revenue_today
    assert multiple is not None and multiple.exact == Fraction(50, 3)  # $5.4M over $324k

    (top,) = result.top_down
    assert (top.comparable.exact, top.bottom_up.exact) == (840_000_000, 108_000_000)
    assert (top.bottom_up_share.exact, top.difference.exact) == (Fraction(9, 70), -732_000_000)
    (check,) = result.checks
    assert (check.key, check.stated.exact, check.computed.exact) == ("tam", 120_000_000, 108_000_000)
    assert (check.difference.exact, check.verdict, result.verdict) == (-12_000_000, "mismatch", "mismatch")
    assert result.flags == ("som_as_percent_only", "som_below_target")


def test_company_aw_ranges_and_break_even_values() -> None:
    price, clinics, share = market_sizing(**MARKET_AW).sensitivity

    assert [case.som.exact for case in price.cases if case.som] == [4_320_000, 6_480_000]
    assert [case.som_change.exact for case in price.cases if case.som_change] == [-1_080_000, 1_080_000]
    assert [case.tam.exact for case in price.cases] == [86_400_000, 129_600_000]
    assert price.som_swing is not None and price.som_swing.exact == 2_160_000
    assert price.at_som_target is not None and price.at_som_target.value is not None
    assert (price.at_som_target.reach, price.at_som_target.value.exact) == ("value", Fraction(17_300, 27))
    assert price.at_som_target.value.rounded == Decimal("640.740741")
    assert price.at_top_down is not None and price.at_top_down.value is not None
    assert price.at_top_down.value.exact == Fraction(34_100, 9)

    assert clinics.som_swing is not None and clinics.som_swing.exact == 2_880_000
    assert clinics.at_som_target is not None and clinics.at_som_target.value is not None
    assert clinics.at_som_target.value.exact == Fraction(4_325, 3)
    assert clinics.at_top_down is not None and clinics.at_top_down.reach == "does_not_move"

    assert share.som_swing is not None and share.som_swing.exact == 1_080_000
    assert share.base_value.exact == Fraction(1, 10)
    assert share.at_som_target is not None and share.at_som_target.value is not None
    assert share.at_som_target.value.exact == Fraction(46, 135)  # 920/27 percent
    assert display(share.at_som_target.value) == "34.0741%"


def test_company_ax_gross_spend_is_the_decks_figure_and_the_segments_overlap() -> None:
    result = market_sizing(**MARKET_AX)

    assert result.segments[0].annual_value_per_customer.exact == 270
    totals = result.totals
    assert (totals.gross_spend.exact, totals.tam.exact, totals.sam.exact) == (
        11_700_000_000,
        1_755_000_000,
        472_500_000,
    )
    assert totals.som is not None and totals.som.exact == 9_450_000
    assert totals.som_share_of_sam is not None and totals.som_share_of_sam.exact == Fraction(1, 50)
    assert totals.sam_share_of_tam.exact == Fraction(7, 26)
    assert result.segments[0].som_multiple_of_today is not None
    assert result.segments[0].som_multiple_of_today.exact == Fraction(20, 3)
    assert result.segments[0].new_customers_per_year is None  # no horizon
    (top,) = result.top_down
    assert (top.bottom_up_share.exact, top.difference.exact) == (Fraction(351, 220), 655_000_000)
    (fee,) = result.sensitivity
    assert [case.som.exact for case in fee.cases if case.som] == [7_650_000, 11_250_000]
    assert fee.som_swing is not None and fee.som_swing.exact == 3_600_000
    assert fee.at_top_down is not None and fee.at_top_down.value is not None
    assert fee.at_top_down.value.exact == Fraction(17, 288)  # 425/72 percent
    assert result.checks[0].difference.exact == -9_945_000_000
    assert result.flags == (
        "segments_exceed_population",
        "bottom_up_above_top_down",
        "som_as_percent_only",
        "no_horizon_given",
    )


def _random_segment(rng: random.Random) -> dict[str, object]:
    customers = rng.randint(1, 10**6)
    serviceable = rng.choice([100, 60, 37, 5])
    segment: dict[str, object] = {
        "customers": str(customers),
        "price": f"{rng.randint(1, 10**6)}e-2",
        "price_period_months": rng.choice([1, 3, 12, 24, 120]),
        "units_per_customer": str(rng.randint(1, 30)),
        "take_rate_percent": rng.choice(["100", "15", "2.5"]),
        "serviceable_percent": str(serviceable),
        "customers_today": str(rng.randint(0, customers)),
    }
    serviceable_count = customers * serviceable // 100
    if rng.random() < 0.5:
        segment["obtainable_percent"] = rng.choice(["1", "10", "33.3", "100"])
    elif serviceable_count >= 1:
        segment["obtainable_customers"] = str(rng.randint(1, serviceable_count))
    return segment


def _random_input(rng: random.Random) -> dict[str, object]:
    segments = [_random_segment(rng) for _ in range(rng.randint(1, 4))]
    every_som = all("obtainable_percent" in s or "obtainable_customers" in s for s in segments)
    rows = []
    for number, segment in enumerate(segments, start=1):
        field = rng.choice(["price", "units_per_customer", "take_rate_percent"])
        rows.append({"field": field, "segment": number, "values": [str(segment[field]), "1"]})
    fields: dict[str, object] = {
        "segments": segments,
        "top_down": [{"amount": str(rng.randint(1, 10**10)), "compare_to": rng.choice(["tam", "sam"])}],
        "sensitivity": rows[:MAX_SENSITIVITIES],
    }
    if every_som:
        fields["som_target"] = str(rng.randint(1, 10**9))
    return fields


def _moved(inputs: MarketSizingInput, segment: int, field: str, value: Fraction) -> MarketSizingResult:
    """The result with one field of one segment at the exact ``value`` (a break-even value need not be a decimal, so
    the segment is copied without validation), no sensitivity rows and no top-down figures."""
    segments = list(inputs.segments)
    segments[segment - 1] = segments[segment - 1].model_copy(update={field: value})
    moved = inputs.model_copy(update={"segments": tuple(segments), "sensitivity": (), "top_down": ()})
    return compute_market_sizing(moved)


def test_property_the_totals_hold_their_identities() -> None:
    """On seeded random markets: segments add up to the totals, SOM <= SAM <= TAM <= gross spend, a sensitivity row at
    its base value is the base, the rounded parts add up to the rounded totals, and a break-even value at the base
    reaches its target exactly."""
    rng = random.Random(_SEED)
    for _ in range(_CASES):
        fields = _random_input(rng)
        result = market_sizing(**fields)
        totals, rows = result.totals, result.segments

        assert totals.tam.exact == sum(row.tam.exact for row in rows)
        assert totals.sam.exact == sum(row.sam.exact for row in rows)
        assert totals.tam.rounded == sum(row.tam.rounded for row in rows)
        assert totals.customers.rounded == sum(row.customers.rounded for row in rows)
        assert totals.sam.exact <= totals.tam.exact <= totals.gross_spend.exact
        for row in rows:
            assert row.sam.exact <= row.tam.exact <= row.gross_spend.exact
            assert row.som is None or row.som.exact <= row.sam.exact
        if totals.som is not None:
            assert totals.som.exact <= totals.sam.exact
            assert totals.som.rounded == sum(row.som.rounded for row in rows if row.som)
        for sensitivity in result.sensitivity:
            base_case = sensitivity.cases[0]  # each row's first value is the segment's own
            assert (base_case.tam.exact, base_case.sam.exact) == (totals.tam.exact, totals.sam.exact)
            assert base_case.som_change is None or base_case.som_change.exact == 0


def test_property_a_break_even_value_reaches_its_target_exactly() -> None:
    """A break-even value with reach ``value`` reaches its target exactly when the field is set to it."""
    rng = random.Random(_SEED + 1)
    reached = 0
    for _ in range(_CASES):
        fields = _random_input(rng)
        result = market_sizing(**fields)
        for row in result.sensitivity:
            for break_even in (row.at_som_target, row.at_top_down):
                if break_even is None or break_even.value is None or break_even.reach != "value":
                    continue
                value = break_even.value.exact * (100 if break_even.value.unit == "fraction" else 1)
                moved = _moved(result.inputs, row.segment, row.field, value)
                total = {"tam": moved.totals.tam, "sam": moved.totals.sam, "som": moved.totals.som}[break_even.metric]
                assert total is not None and total.exact == break_even.target.exact
                reached += 1
    assert reached > 0


def test_a_price_period_turns_into_a_year() -> None:
    """A $200 device that lasts two years is $100 a year; a monthly price is twelve of them."""
    two_years = market_sizing(**_with({"price": "200", "price_period_months": 24}))
    yearly = market_sizing(**_with({"price": "100"}))
    monthly = market_sizing(**_with({"price": "100", "price_period_months": 1}))

    assert two_years.totals.tam == yearly.totals.tam
    assert monthly.totals.tam.exact == 12 * yearly.totals.tam.exact


def test_the_take_rate_scales_tam_but_not_the_gross_spend() -> None:
    full = market_sizing(**_with())
    fee = market_sizing(**_with({"take_rate_percent": "15"}))

    assert fee.totals.tam.exact == Fraction(15, 100) * full.totals.tam.exact
    assert fee.totals.gross_spend == full.totals.gross_spend == full.totals.tam


def test_break_even_edges() -> None:
    """Met by the other segments, a percent above 100, a count above the serviceable customers, and a field that does
    not move the total; the value is still returned when it is out of range."""
    met = market_sizing(
        segments=[{**_ONE_SEGMENT, "obtainable_customers": "500"}, {**_ONE_SEGMENT, "obtainable_customers": "500"}],
        sensitivity=[{"field": "price", "segment": 1, "values": ["90"]}],
        som_target="50000",
    )
    assert met.sensitivity[0].at_som_target is not None
    assert met.sensitivity[0].at_som_target.reach == "met_without_it"
    assert met.sensitivity[0].at_som_target.value is None

    share = market_sizing(
        **_with(
            {"obtainable_percent": "50"},
            sensitivity=[{"field": "obtainable_percent", "segment": 1, "values": ["40"]}],
            som_target="200000",
        )
    )
    beyond = share.sensitivity[0].at_som_target
    assert beyond is not None and beyond.value is not None
    assert (beyond.reach, beyond.value.exact) == ("out_of_range", Fraction(2))  # 200%
    assert share.flags[-1] == "som_target_out_of_reach"

    count = market_sizing(
        **_with(
            {"serviceable_percent": "50", "obtainable_customers": "100"},
            sensitivity=[{"field": "obtainable_customers", "segment": 1, "values": ["200"]}],
            som_target="60000",
        )
    )
    above = count.sensitivity[0].at_som_target
    assert above is not None and above.value is not None
    assert (above.reach, above.value.exact) == ("out_of_range", 600)

    fewer = market_sizing(
        **_with(
            {"customers_today": "800"},
            top_down=[{"amount": "50000"}],
            sensitivity=[{"field": "customers", "segment": 1, "values": ["900"]}],
        )
    )
    below_today = fewer.sensitivity[0].at_top_down
    assert below_today is not None and below_today.value is not None
    assert (below_today.reach, below_today.value.exact) == ("out_of_range", 500)


def test_a_target_the_base_som_already_reaches_is_met_and_never_out_of_reach() -> None:
    """SOM is $500 against a $100 target: the customers at which SOM equals $100 (20) are fewer than today's 40, which
    is no reason to call the target out of reach."""
    above = market_sizing(
        **_with(
            {"customers": "100", "price": "10", "obtainable_percent": "50", "customers_today": "40"},
            som_years=2,
            som_target="100",
            sensitivity=[{"field": "customers", "segment": 1, "values": ["90", "110"]}],
        )
    )
    met = above.sensitivity[0].at_som_target

    assert above.totals.som is not None and above.totals.som.exact == 500
    assert met is not None and (met.reach, met.value) == ("met_without_it", None)
    assert not {"som_below_target", "som_target_out_of_reach"} & set(above.flags)


def test_the_target_is_out_of_reach_only_when_no_row_reaches_it() -> None:
    """SOM $1,000 against $2,100: segment 1's share to win would need 160% (out of range), but segment 2's customers
    reach it at 320, so the target is below the SOM yet not out of reach; with the share row alone it is."""
    halves = [{"customers": "100", "price": "10", "obtainable_percent": "50"}] * 2
    share = {"field": "obtainable_percent", "segment": 1, "values": ["40"]}
    customers = {"field": "customers", "segment": 2, "values": ["120"]}
    mixed = market_sizing(segments=halves, som_target="2100", sensitivity=[share, customers])
    alone = market_sizing(segments=halves, som_target="2100", sensitivity=[share])

    first, second = (row.at_som_target for row in mixed.sensitivity)
    assert first is not None and first.value is not None
    assert (first.reach, first.value.exact) == ("out_of_range", Fraction(8, 5))  # 160%
    assert second is not None and second.value is not None
    assert (second.reach, second.value.exact) == ("value", 320)
    assert "som_below_target" in mixed.flags
    assert "som_target_out_of_reach" not in mixed.flags
    assert "som_target_out_of_reach" in alone.flags


@pytest.mark.parametrize(
    ("segment", "amount", "reach"),
    [
        ({"customers": "1"}, "0.000000000000001", "value"),  # a price of 1e-15, the smallest size an input may have
        ({"customers": "2"}, "0.000000000000001", "out_of_range"),  # 5e-16
        ({"customers": "1"}, "9999999999999999", "value"),  # just under 1e16
        ({"customers": "1", "units_per_customer": "0.5"}, "9999999999999999", "out_of_range"),  # about 2e16
    ],
)
def test_a_break_even_past_the_size_of_any_input_is_out_of_range(
    segment: dict[str, object], amount: str, reach: str
) -> None:
    """A $1 yearly price: the price at which TAM equals the top-down figure keeps the size every decimal input has (at
    least 1e-15 and under 1e16), or the segment would refuse it."""
    result = market_sizing(
        segments=[{"price": "1", **segment}],
        top_down=[{"amount": amount}],
        sensitivity=[{"field": "price", "segment": 1, "values": ["2"]}],
    )
    at_top_down = result.sensitivity[0].at_top_down

    assert at_top_down is not None and at_top_down.reach == reach


def test_a_som_target_past_the_size_of_any_input_is_out_of_reach() -> None:
    """The price at which SOM reaches the target would be about 1e34, which no segment takes: out of range, and the
    flag fires, never "reaches it exactly"."""
    result = market_sizing(
        segments=[
            {"customers": "1", "price": "1", "units_per_customer": "0.000000000000001", "obtainable_customers": "1"}
        ],
        som_target="9999999999999999",
        sensitivity=[{"field": "price", "segment": 1, "values": ["1"]}],
    )
    at_target = result.sensitivity[0].at_som_target

    assert at_target is not None and at_target.reach == "out_of_range"
    assert "som_target_out_of_reach" in result.flags


@pytest.mark.parametrize(
    ("field", "value", "metric", "moves"),
    [
        ("obtainable_customers", "200", "tam", False),
        ("serviceable_percent", "90", "tam", False),
        ("customers", "900", "som", False),  # the SOM is a count of customers here
        ("price", "90", "som", True),
        ("customers", "900", "tam", True),
    ],
)
def test_which_fields_move_which_total(field: str, value: str, metric: str, moves: bool) -> None:
    result = market_sizing(
        **_with(
            {"serviceable_percent": "50", "obtainable_customers": "100"},
            top_down=[{"amount": "1", "compare_to": "tam"}],
            sensitivity=[{"field": field, "segment": 1, "values": [value]}],
            som_target="1",
        )
    )
    (row,) = result.sensitivity
    break_even = row.at_som_target if metric == "som" else row.at_top_down

    assert break_even is not None
    assert (break_even.reach != "does_not_move") is moves


@pytest.mark.parametrize(
    ("stated", "verdict"),
    [("98000", "consistent"), ("102000", "consistent"), ("97999.99", "mismatch"), ("102000.01", "mismatch")],
)
def test_a_stated_figure_within_the_relative_tolerance_is_consistent_edge_included(stated: str, verdict: str) -> None:
    """TAM is $100,000; 2% of it is $2,000 either way, the edge included."""
    result = market_sizing(**_with(stated_tam=stated))

    assert result.checks[0].verdict == result.verdict == verdict


def test_sam_and_som_are_checked_and_nothing_stated_is_not_checked() -> None:
    checked = market_sizing(**_with({"obtainable_customers": "10"}, stated_sam="100000", stated_som="1000"))
    nothing = market_sizing(**_with({"obtainable_customers": "10"}))

    assert [(check.key, check.verdict) for check in checked.checks] == [("sam", "consistent"), ("som", "consistent")]
    assert (nothing.checks, nothing.verdict) == ((), "not_checked")


def test_a_top_down_figure_never_changes_the_verdict() -> None:
    far = market_sizing(**_with(stated_tam="100000", top_down=[{"amount": "1"}]))

    assert far.verdict == "consistent"
    assert "bottom_up_above_top_down" in far.flags


_FLAG_CASES: dict[str, tuple[dict[str, object], dict[str, object]]] = {
    "price_period_defaulted": (_with(), _with({"price_period_months": 12})),
    "no_market_count": (_with({"obtainable_customers": "1000"}), _with({"obtainable_customers": "999"})),
    "segments_exceed_population": (_with(population="999"), _with(population="1000")),
    "bottom_up_above_top_down": (_with(top_down=[{"amount": "99999"}]), _with(top_down=[{"amount": "100000"}])),
    "sam_equals_tam": (_with(), _with({"serviceable_percent": "99"})),
    "som_not_given": (_with(), _with({"obtainable_customers": "1"})),
    "som_as_percent_only": (_with({"obtainable_percent": "1"}), _with({"obtainable_customers": "10"})),
    "som_from_zero_customers": (
        _with({"obtainable_customers": "10", "customers_today": "0"}),
        _with({"obtainable_customers": "10", "customers_today": "1"}),
    ),
    "som_below_customers_today": (
        _with({"obtainable_customers": "10", "customers_today": "11"}),
        _with({"obtainable_customers": "10", "customers_today": "10"}),
    ),
    "no_horizon_given": (_with({"obtainable_customers": "10"}), _with({"obtainable_customers": "10"}, som_years=3)),
    "som_below_target": (
        _with({"obtainable_customers": "10"}, som_target="1000.01"),
        _with({"obtainable_customers": "10"}, som_target="1000"),
    ),
    "som_target_out_of_reach": (
        _with(
            {"obtainable_percent": "50"},
            som_target="100000.01",
            sensitivity=[{"field": "obtainable_percent", "segment": 1, "values": ["40"]}],
        ),
        _with(
            {"obtainable_percent": "50"},
            som_target="100000",
            sensitivity=[{"field": "obtainable_percent", "segment": 1, "values": ["40"]}],
        ),
    ),
}


@pytest.mark.parametrize("flag", sorted(_FLAG_CASES))
def test_each_flag_fires_on_its_minimal_input_and_not_on_its_neighbour(flag: MarketSizingFlag) -> None:
    fires, neighbour = _FLAG_CASES[flag]

    assert flag in market_sizing(**fires).flags
    assert flag not in market_sizing(**neighbour).flags


def test_every_flag_is_tested() -> None:
    assert set(_FLAG_CASES) == set(get_args(MarketSizingFlag))


def test_flags_never_change_the_verdict() -> None:
    flagged = market_sizing(**_with(population="1", stated_tam="100000"))

    assert flagged.flags and flagged.verdict == "consistent"


def test_a_source_ending_in_a_quoted_sentence_gets_no_second_period() -> None:
    report = render_sheet(sheet_for(market_sizing(**MARKET_AX)))

    assert '.".' not in report
    assert f"{TOP_DOWN_QUOTE}\n" in report and f"{TAM_GLOSSARY_QUOTE}\n" in report
    assert "(a modelling choice).\n" in report


def test_assumption_rows_appear_only_when_used() -> None:
    plain = {row.key for row in market_sizing(**_with()).assumptions}
    every = {row.key for row in market_sizing(**MARKET_AX).assumptions}
    aw = {row.key for row in market_sizing(**MARKET_AW).assumptions}

    assert plain == {"bottom_up_rule", "annual_rule", "sam_rule"}
    assert every == {
        "bottom_up_rule",
        "annual_rule",
        "revenue_rule",
        "sam_rule",
        "som_rule",
        "top_down_rule",
        "population_rule",
        "sensitivity_rule",
        "tolerance",
    }
    assert "revenue_rule" not in aw  # no take rate below 100%


def test_the_yc_rows_quote_the_pages_word_for_word() -> None:
    rows = {row.key: row.source for row in market_sizing(**MARKET_AX).assumptions}

    assert (BOTTOM_UP_QUOTE, LIFECYCLE_QUOTE) == (f'"{_BOTTOM_UP_WORDS}"', f'"{_LIFECYCLE_WORDS}"')
    assert (TOP_DOWN_QUOTE, TAM_GLOSSARY_QUOTE) == (f'"{_TOP_DOWN_WORDS}"', f'"{_GLOSSARY_WORDS}"')
    assert _BOTTOM_UP_WORDS in rows["bottom_up_rule"] and "4b-how-to-pitch-your-company" in rows["bottom_up_rule"]
    assert _LIFECYCLE_WORDS in rows["annual_rule"]
    assert _TOP_DOWN_WORDS in rows["top_down_rule"]
    assert (NEW_SPACE_QUOTE, YC_BOTTOM_UP_QUOTE) == (f'"{_NEW_SPACE_WORDS}"', f'"{_YC_BOTTOM_UP_WORDS}"')
    # The customers × price sentence is YC's method for a new product or space; the page's own bottom-up counts
    # comparable products' sales, and its preference is quoted beside that sentence, never beside customers × price.
    assert _NEW_SPACE_WORDS in rows["bottom_up_rule"] and "common usage, unverified" in rows["bottom_up_rule"]
    assert rows["top_down_rule"].index(_YC_BOTTOM_UP_WORDS) < rows["top_down_rule"].index(_TOP_DOWN_WORDS)
    assert _YC_BOTTOM_UP_WORDS not in rows["bottom_up_rule"]
    assert _GLOSSARY_WORDS in rows["revenue_rule"] and "4A-a-guide-to-seed-fundraising" in rows["revenue_rule"]
    for key in ("sam_rule", "som_rule", "population_rule", "sensitivity_rule", "tolerance"):
        assert rows[key].startswith("unverified"), key


def test_a_count_prints_whole_without_decimals_and_a_fraction_with_two() -> None:
    report = render_sheet(sheet_for(market_sizing(**MARKET_AW)))

    assert "Segment 1: SAM customers" in report and "10,800  customers" in report
    assert "1,441.67  base ×" in report
    assert "3.60  (SOM customers" in report


def test_each_segment_and_sensitivity_row_is_named_by_number_only() -> None:
    """No free text reaches the calculator: segments and rows are numbered in the order given."""
    result = market_sizing(**MARKET_AW)

    assert [row.segment for row in result.segments] == [1, 2]
    assert [(row.row, row.segment, row.field) for row in result.sensitivity] == [
        (1, 1, "price"),
        (2, 1, "obtainable_customers"),
        (3, 2, "obtainable_percent"),
    ]


_TOO_MANY_VALUES = [str(value) for value in range(1, MAX_SENSITIVITY_VALUES + 2)]


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        (_with({"obtainable_percent": "1", "obtainable_customers": "1"}), "obtainable_percent or obtainable_customers"),
        (_with({"customers_today": "1001"}), "customers_today is above customers"),
        (_with({"serviceable_percent": "50", "obtainable_customers": "501"}), "above the serviceable customers"),
        (_with({"take_rate_percent": "100.01"}), "less than or equal to 100"),
        (_with({"price_period_months": 121}), "less than or equal to 120"),
        (_with({"price_period_months": 0}), "greater than or equal to 1"),
        (_with({"price_period_months": "12"}), "valid integer"),
        (_with(som_years=21), "less than or equal to 20"),
        (_with(stated_som="1"), "stated_som needs obtainable_percent or obtainable_customers in every segment"),
        (_with(som_target="1"), "som_target needs obtainable_percent or obtainable_customers in every segment"),
        (
            _with(sensitivity=[{"field": "price", "segment": 2, "values": ["1"]}]),
            "sensitivity #1 names segment 2, past the last one given (1)",
        ),
        (
            _with(sensitivity=[{"field": "obtainable_percent", "segment": 1, "values": ["1"]}]),
            "sensitivity #1: segment 1 gives no obtainable_percent to change",
        ),
        (
            _with(sensitivity=[{"field": "price", "segment": 1, "values": ["1"]}] * 2),
            "sensitivity #2: price of segment 1 is already a row",
        ),
        (
            _with(sensitivity=[{"field": "take_rate_percent", "segment": 1, "values": ["50", "101"]}]),
            "sensitivity #1 value #2 (101): take_rate_percent input should be less than or equal to 100",
        ),
        (
            _with({"customers_today": "500"}, sensitivity=[{"field": "customers", "segment": 1, "values": ["499"]}]),
            "sensitivity #1 value #1 (499): customers_today is above customers",
        ),
        (_with(sensitivity=[{"field": "price", "segment": 1, "values": _TOO_MANY_VALUES}]), "at most 4 items"),
        ({"segments": [_ONE_SEGMENT] * (MAX_SEGMENTS + 1)}, "at most 8 items"),
        (_with(top_down=[{"amount": "1"}] * (MAX_TOP_DOWN + 1)), "at most 3 items"),
        ({"segments": []}, "at least 1 item"),
        (_with(sensitivity=[{"field": "price", "segment": 1, "values": []}]), "at least 1 item"),
    ],
)
def test_each_refusal_names_its_fields(fields: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=re.escape(message)):
        MarketSizingInput.model_validate(fields)


def test_seven_sensitivity_rows_are_refused() -> None:
    fields = ("customers", "price", "units_per_customer", "take_rate_percent", "serviceable_percent")
    rows = [{"field": field, "segment": segment, "values": ["1"]} for segment in (1, 2) for field in fields]

    with pytest.raises(ValidationError, match="at most 6 items"):
        MarketSizingInput.model_validate({"segments": [_ONE_SEGMENT, _ONE_SEGMENT], "sensitivity": rows[:7]})


_USAGE_PRICE = {
    "customers": "2,000".replace(",", ""),
    "price": "0.0075",
    "price_period_months": 1,
    "units_per_customer": "400000",
    "obtainable_customers": "150",
}


def test_a_sub_cent_price_is_shown_with_the_places_it_needs_never_as_whole_cents() -> None:
    """A $0.0075 usage price prints as $0.0075 everywhere it appears (the given line, the sensitivity base, each case
    and its label, the break-even value), so a 67% price rise never prints as no change."""
    result = market_sizing(
        segments=[_USAGE_PRICE],
        som_target="9000000",
        sensitivity=[{"field": "price", "segment": 1, "values": ["0.005", "0.0125"]}],
    )
    (row,) = result.sensitivity
    report = render_sheet(sheet_for(result))

    assert row.base_value.rounded == Decimal("0.0075") and row.base_value.unit == "price"
    assert [case.value.rounded for case in row.cases] == [Decimal("0.005"), Decimal("0.0125")]
    assert row.at_som_target is not None and row.at_som_target.value is not None
    assert (row.at_som_target.value.exact, row.at_som_target.value.rounded) == (Fraction(1, 80), Decimal("0.0125"))
    assert re.search(r"Segment 1: price per unit +\$0\.0075  given", report)
    assert re.search(r"Sensitivity 1: segment 1 price, base +\$0\.0075  given", report)
    assert "Sensitivity 1 at $0.005: SOM " in report and "Sensitivity 1 at $0.0125: SOM " in report
    assert re.search(r"price at SOM = \$9,000,000\.00 +\$0\.0125  base", report)
    assert "$0.01 " not in report and "$0.00 " not in report


@pytest.mark.parametrize(
    ("value", "rounded"),
    [
        (Fraction(400), "400.00"),
        (Fraction(49, 100), "0.49"),
        (Fraction(3, 400), "0.0075"),
        (Fraction(17_300, 27), "640.740741"),
        (Fraction(15, 10**8), "0.00000015"),
        (Fraction(1, 3 * 10**7), "0.000000033"),
        (Fraction(1, 10**15), "0.000000000000001"),
        (Fraction(1, 10**16), "0.00"),
    ],
)
def test_a_unit_price_keeps_cents_and_the_places_it_needs(value: Fraction, rounded: str) -> None:
    """Whole cents when exact, up to 6 places when needed, two significant digits under $0.00001 (up to 15 places, the
    input floor; a break-even value below it shows as zero, and is refused as out of range), the exact value kept."""
    shown = price_quantity(value)

    assert (shown.unit, shown.exact, f"{shown.rounded:f}") == ("price", value, rounded)


@pytest.mark.parametrize(
    ("typed", "shown"),
    [
        ("400", "400.00"),
        ("12.5", "12.50"),
        ("1.10", "1.10"),
        ("0.0075000", "0.0075"),
        ("0.3333333", "0.3333333"),
        ("0.00000125", "0.00000125"),
        ("0.00001667", "0.00001667"),
        ("1E-15", "0.000000000000001"),
    ],
)
def test_a_typed_price_is_shown_exactly_never_rounded(typed: str, shown: str) -> None:
    """A price the founder typed is never rounded: the fewest places from 2 that show it exactly."""
    price = given_price(Decimal(typed))

    assert (price.unit, price.exact, f"{price.rounded:f}") == ("price", Fraction(Decimal(typed)), shown)


def test_typed_prices_below_a_ten_thousandth_print_as_typed_and_a_break_even_price_stays_rounded() -> None:
    """$0.00000125 with cases $0.00000115 and $0.00000135: each prints as typed (the given line, the base, each case and
    its label), so two prices never share one label. SOM 150 · 0.00000125 · 12 · 4e9 = $9M; the price at a $10M SOM,
    0.00000125 · 10/9, is worked and keeps two significant digits ($0.0000014)."""
    result = market_sizing(
        segments=[
            {
                "customers": "2000",
                "price": "0.00000125",
                "price_period_months": 1,
                "units_per_customer": "4000000000",
                "obtainable_customers": "150",
            }
        ],
        som_target="10000000",
        sensitivity=[{"field": "price", "segment": 1, "values": ["0.00000115", "0.00000135"]}],
    )
    (row,) = result.sensitivity
    report = render_sheet(sheet_for(result))

    assert result.totals.som is not None and result.totals.som.exact == 9_000_000
    assert row.base_value.rounded == Decimal("0.00000125")
    assert [case.value.rounded for case in row.cases] == [Decimal("0.00000115"), Decimal("0.00000135")]
    assert re.search(r"Segment 1: price per unit +\$0\.00000125  given", report)
    assert re.search(r"Sensitivity 1: segment 1 price, base +\$0\.00000125  given", report)
    assert "Sensitivity 1 at $0.00000115: SOM " in report and "Sensitivity 1 at $0.00000135: SOM " in report
    assert row.at_som_target is not None and row.at_som_target.value is not None
    assert row.at_som_target.value.exact == Fraction(125, 10**8) * Fraction(10, 9)
    assert row.at_som_target.value.rounded == Decimal("0.0000014")
    assert "$0.0000012 " not in report


def test_a_workbook_price_cell_shows_every_place_it_was_rounded_to() -> None:
    from equity_calculator.workbook import build_workbook

    result = market_sizing(segments=[{**_USAGE_PRICE, "price": "0.00000015"}])
    sheet = build_workbook([sheet_for(result)]).active
    assert sheet is not None
    formats = {
        str(row[1].value): row[1].number_format
        for row in sheet.iter_rows()
        if isinstance(row[0].value, str) and row[0].value.endswith("price per unit")
    }

    assert formats == {"1.5E-7": '"$"#,##0.00000000'}


def test_the_echoed_inputs_fed_back_keep_the_price_period_flag() -> None:
    """Left out, the price period is null in the echo, so a call built from a result's own inputs keeps
    price_period_defaulted; given (12 included), it stays given."""
    for segment, flagged in (({}, True), ({"price_period_months": 12}, False), ({"price_period_months": None}, True)):
        first = compute(MarketSizingInput.model_validate(_with(segment)))
        echoed = json.loads(first.model_dump_json())["inputs"]
        again = compute(MarketSizingInput.model_validate(echoed))

        assert echoed["segments"][0]["price_period_months"] == (None if flagged else 12)
        assert again.flags == first.flags
        assert ("price_period_defaulted" in again.flags) is flagged
        assert again.segments[0].price_period_given is not flagged
        assert again.totals.tam.exact == first.totals.tam.exact == 100_000


def test_the_input_schema_shows_no_default_period_of_12() -> None:
    period = MarketSizingInput.model_json_schema()["$defs"]["MarketSegment"]["properties"]["price_period_months"]

    assert period["default"] is None


def test_fractional_customer_lines_add_up_to_the_total_line() -> None:
    """The segments' buying-customer lines show the model's split rounding, so they add up to the total that sums
    them (10.005 and 20.005 print as 10.01 and 20.00 above 30.01)."""
    result = market_sizing(segments=[{"customers": "10.005", "price": "100"}, {"customers": "20.005", "price": "100"}])
    lines = {line.key: line for line in sheet_for(result).lines}
    parts = [lines[f"segment_{number}_customers"].values[0] for number in (1, 2)]

    assert [part.rounded for part in parts if not isinstance(part, str)] == [Decimal("10.01"), Decimal("20.00")]
    total = lines["total_customers"].values[0]
    assert not isinstance(total, str) and total.rounded == Decimal("30.01")


_SPLIT_HOW = "given, shown rounded so the segments add up to the total"


def test_a_customer_line_shown_rounded_for_the_total_says_so_and_a_typed_count_says_given() -> None:
    """0.335 in each of two segments prints 0.34 and 0.33 (they add up to 0.67), so neither line is the typed count
    and each says why; 10.5 and 1,000 print as typed and say given."""
    split = {
        line.key: line for line in sheet_for(market_sizing(segments=[{"customers": "0.335", "price": "100"}] * 2)).lines
    }
    typed = {
        line.key: line
        for line in sheet_for(
            market_sizing(segments=[{"customers": "10.5", "price": "100"}, {"customers": "1000", "price": "100"}])
        ).lines
    }

    shown = [split[f"segment_{number}_customers"].values[0] for number in (1, 2)]
    assert [part.rounded for part in shown if not isinstance(part, str)] == [Decimal("0.34"), Decimal("0.33")]
    assert [split[f"segment_{number}_customers"].how for number in (1, 2)] == [_SPLIT_HOW, _SPLIT_HOW]
    assert [typed[f"segment_{number}_customers"].how for number in (1, 2)] == ["given", "given"]


def test_a_share_above_zero_that_rounds_to_zero_says_so() -> None:
    result = market_sizing(
        segments=[{"customers": "40", "price": "100", "price_period_months": 1}], top_down=[{"amount": "840000000000"}]
    )
    report = render_sheet(sheet_for(result))

    assert "bottom-up TAM / comparable part (a cross-check); under 0.0001%, not zero" in report
    plain = render_sheet(sheet_for(market_sizing(**MARKET_AW)))
    assert "not zero" not in plain


def test_the_som_rule_says_one_year_and_the_tolerance_source_names_the_default() -> None:
    one = {
        row.key: row
        for row in market_sizing(**_with({"obtainable_customers": "10"}, som_years=1, stated_tam="1")).assumptions
    }
    five = {row.key: row for row in market_sizing(**_with({"obtainable_customers": "10"}, som_years=5)).assumptions}
    changed = market_sizing(**_with(stated_tam="1", tolerance_percent="5")).assumptions

    assert one["som_rule"].setting.endswith("in 1 year") and five["som_rule"].setting.endswith("in 5 years")
    assert one["tolerance"].source == "unverified (deal_check's default is 2%)"
    assert {row.key: row.setting for row in changed}["tolerance"] == "5% of the computed figure"


def test_a_tolerance_typed_in_exponent_form_prints_as_a_plain_number() -> None:
    rows = {row.key: row for row in market_sizing(**_with(stated_tam="1", tolerance_percent="2e1")).assumptions}

    assert rows["tolerance"].setting == "20% of the computed figure"


def test_does_not_move_is_reported_before_met_without_it() -> None:
    """A field that is no factor of SOM is does_not_move even when the base SOM already meets the target; a field
    that is a factor is met_without_it."""
    result = market_sizing(
        **_with(
            {"obtainable_customers": "100"},
            som_target="5000",
            sensitivity=[
                {"field": "customers", "segment": 1, "values": ["2000"]},
                {"field": "price", "segment": 1, "values": ["200"]},
            ],
        )
    )

    assert [row.at_som_target.reach for row in result.sensitivity if row.at_som_target] == [
        "does_not_move",
        "met_without_it",
    ]


def test_a_horizon_in_months_is_months_over_12_years_and_a_horizon_in_years_is_unchanged() -> None:
    """30 months is 5/2 years: (30 - 5) / (5/2) = 10 new customers a year, exactly; the years path keeps its words."""
    segment = {"customers": "100", "price": "1000", "price_period_months": 12, "obtainable_customers": "30"}
    months = market_sizing(segments=[{**segment, "customers_today": "5"}], som_months=30)
    years = market_sizing(segments=[{**segment, "customers_today": "5"}], som_years=2)
    rows = {row.key: row for row in months.assumptions}

    assert months.segments[0].new_customers_per_year is not None
    assert months.segments[0].new_customers_per_year.exact == 10
    assert years.segments[0].new_customers_per_year is not None
    assert years.segments[0].new_customers_per_year.exact == Fraction(25, 2)
    assert rows["som_rule"].setting.endswith("in 30 months")
    assert "no_horizon_given" not in months.flags
    assert "no_horizon_given" in market_sizing(segments=[segment]).flags
    one = {row.key: row for row in market_sizing(segments=[segment], som_months=1).assumptions}
    assert one["som_rule"].setting.endswith("in 1 month")
    with pytest.raises(ValidationError, match="give som_years or som_months, not both"):
        market_sizing(segments=[segment], som_years=1, som_months=12)


def test_the_som_range_says_when_its_low_or_high_is_the_base_not_a_founder_value() -> None:
    """Prices of $600 and $800 against a $1,000 base: the high is the base's $30,000, not the founder's best case; a
    tie with the base (a field that does not move SOM) goes to the founder's value; no SOM total, no range ends."""
    segment = {"customers": "100", "price": "1000", "price_period_months": 12, "obtainable_customers": "30"}

    def row(field: str, values: list[str], **extra: object) -> SensitivityResult:
        rows = [{"field": field, "segment": 1, "values": values}]
        return market_sizing(segments=[{**segment, **extra}], sensitivity=rows).sensitivity[0]

    below = row("price", ["600", "800"])
    assert (below.som_low_at, below.som_high_at) == ("founder_value", "base")
    assert below.som_high is not None and below.som_high.exact == 30000
    assert below.value_at_som_high is not None and below.value_at_som_high.exact == 1000
    assert below.value_at_som_low is not None and below.value_at_som_low.exact == 600
    above = row("price", ["1100", "1200"])
    assert (above.som_low_at, above.som_high_at) == ("base", "founder_value")
    tie = row("serviceable_percent", ["50", "90"])
    assert (tie.som_low_at, tie.som_high_at) == ("founder_value", "founder_value")
    no_som = market_sizing(
        segments=[{key: value for key, value in segment.items() if key != "obtainable_customers"}],
        sensitivity=[{"field": "price", "segment": 1, "values": ["600"]}],
    ).sensitivity[0]
    assert (no_som.som_low_at, no_som.value_at_som_high) == (None, None)


# Company NC (made up): 40 customers to win at $50,000 a year, with no count of the market (left out, or typed equal to
# the 40), beside a counted segment of 1,000 at $1,000 a year winning 100.
_NC_TO_WIN = {"price": "50000", "price_period_months": 12, "obtainable_customers": "40"}
_NC_COUNTED = {"customers": "1000", "price": "1000", "price_period_months": 12, "obtainable_customers": "100"}


@pytest.mark.parametrize("to_win", [_NC_TO_WIN, {**_NC_TO_WIN, "customers": "40"}], ids=["left-out", "equal"])
def test_a_segment_with_no_market_count_works_its_som_and_no_tam_or_sam(to_win: dict[str, object]) -> None:
    """Its TAM, SAM, customers and share are none, and so are the market totals and the shares on them; the counted
    segment keeps its own; the SOM is worked and totalled; a sensitivity value never brings TAM back; the top-down
    comparison and its break-even are not worked; the flag and the rule row say why; the echoed inputs read back."""
    result = market_sizing(
        segments=[to_win, _NC_COUNTED],
        top_down=[{"amount": "2000000000"}],
        sensitivity=[{"field": "obtainable_customers", "segment": 1, "values": ["30"]}],
        som_target="3000000",
    )
    uncounted, counted = result.segments
    totals = result.totals

    assert not uncounted.market_counted and counted.market_counted
    assert (uncounted.customers, uncounted.gross_spend, uncounted.tam, uncounted.sam, uncounted.share_of_tam) == (
        None,
        None,
        None,
        None,
        None,
    )
    assert counted.tam is not None and counted.tam.exact == 1_000_000 and counted.share_of_tam is None
    assert uncounted.som is not None and uncounted.som.exact == 2_000_000
    assert totals.som is not None and totals.som.exact == 2_100_000
    assert (totals.customers, totals.tam, totals.sam, totals.sam_share_of_tam, totals.som_share_of_sam) == (
        None,
        None,
        None,
        None,
        None,
    )
    (row,) = result.sensitivity
    assert row.cases[0].tam is None and row.cases[0].som is not None and row.cases[0].som.exact == 1_600_000
    assert row.at_top_down is None and row.at_som_target is not None
    (top,) = result.top_down
    assert (top.bottom_up, top.bottom_up_share, top.difference) == (None, None, None)
    assert "no_market_count" in result.flags
    assert not {"sam_equals_tam", "bottom_up_above_top_down"} & set(result.flags)
    assert "no_market_count_rule" in {row.key for row in result.assumptions}
    again = market_sizing(**result.inputs.model_dump(mode="json"))
    assert again.model_dump() == result.model_dump()


def test_a_counted_market_keeps_every_figure_and_raises_no_no_count_flag() -> None:
    result = market_sizing(segments=[_NC_COUNTED])

    assert result.segments[0].market_counted and result.totals.tam is not None
    assert "no_market_count" not in result.flags
    assert "no_market_count_rule" not in {row.key for row in result.assumptions}


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"stated_tam": "1"}, "stated_tam needs a market count"),
        ({"stated_sam": "1"}, "stated_sam needs a market count"),
        ({"population": "1"}, "population needs a market count"),
        (
            {"sensitivity": [{"field": "customers", "segment": 1, "values": ["50"]}]},
            "segment 1 has no market count, so its customers moves nothing",
        ),
        (
            {"segments": [{"price": "1", "obtainable_percent": "10"}]},
            "give obtainable_customers, the customers to win",
        ),
        (
            {"segments": [{"price": "1", "obtainable_customers": "4", "serviceable_percent": "50"}]},
            "serviceable_percent needs customers",
        ),
    ],
    ids=["stated-tam", "stated-sam", "population", "row-on-customers", "share-to-win", "serviceable"],
)
def test_with_no_market_count_what_needs_one_is_refused(changes: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        market_sizing(**{"segments": [{**_NC_TO_WIN, "customers": "40"}], **changes})


# Company UC (made up): licences at $40,000 a licence a year, 25 licences to win, with no market count; and a
# counted market of 40 customers buying 10 seats each at $100,000 a seat a year, winning 25 seats.
_UC_LICENCES = {"price": "40000", "price_period_months": 12, "obtainable_units": "25"}
_UC_SEATS = {"customers": "40", "units_per_customer": "10", "price": "100000", "price_period_months": 12}


def test_a_som_in_units_is_units_times_one_units_year_and_never_a_fraction_of_a_customer() -> None:
    """25 licences at $40,000 is $1M with no SOM customers; 25 seats at $100,000 is $2.5M beside a $40M TAM; the units
    rule row says so; the break-even units, fed back, reach the target exactly; units above the serviceable units are
    out of range."""
    result = market_sizing(segments=[_UC_LICENCES, {**_UC_SEATS, "obtainable_units": "25"}], som_target="4500000")
    licences, seats = result.segments

    assert licences.som_customers is None and licences.som_units is not None
    assert licences.som_units.exact == 25
    assert licences.som is not None and licences.som.exact == 1_000_000
    assert seats.som is not None and seats.som.exact == 2_500_000 and seats.som_customers is None
    assert seats.tam is not None and seats.tam.exact == 40_000_000
    assert result.totals.som is not None and result.totals.som_customers is None
    assert "units_rule" in {row.key for row in result.assumptions}
    rows = [{"field": "obtainable_units", "segment": 1, "values": ["20"]}]
    at_target = market_sizing(**{**result.inputs.model_dump(mode="json"), "sensitivity": rows}).sensitivity[0]
    assert at_target.at_som_target is not None and at_target.at_som_target.value is not None
    needed = at_target.at_som_target.value.exact
    assert needed == 50
    fed_back = [{**rows[0], "values": ["50"]}]
    moved = market_sizing(**{**result.inputs.model_dump(mode="json"), "sensitivity": fed_back})
    assert moved.sensitivity[0].cases[0].som is not None and moved.sensitivity[0].cases[0].som.exact == 4_500_000
    seats_row = [{"field": "obtainable_units", "segment": 1, "values": ["30"]}]
    over = market_sizing(
        segments=[{**_UC_SEATS, "obtainable_units": "25"}], som_target="50000000", sensitivity=seats_row
    )
    assert over.sensitivity[0].at_som_target is not None and over.sensitivity[0].at_som_target.reach == "out_of_range"


@pytest.mark.parametrize(
    ("segment", "message"),
    [
        ({**_UC_SEATS, "obtainable_units": "401"}, "obtainable_units is above the serviceable units"),
        ({**_UC_SEATS, "obtainable_units": "4", "customers_today": "1"}, "customers_today counts customers"),
        ({**_UC_SEATS, "obtainable_units": "4", "obtainable_customers": "1"}, "one only"),
    ],
    ids=["above-serviceable", "customers-today", "two-soms"],
)
def test_a_som_in_units_refuses_what_mixes_units_with_customers(segment: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        market_sizing(segments=[segment])


# Company SL (made up): 1,000 buyers at $10,000 a year on the main bill, a 10% take rate and a second line at 20% of
# the main bill, winning 100.
_SL = {
    "customers": "1000",
    "price": "10000",
    "price_period_months": 12,
    "take_rate_percent": "10",
    "second_line_percent": "20",
    "obtainable_customers": "100",
}


def test_a_second_line_adds_its_share_of_the_main_bill_to_the_take_rate() -> None:
    """One buyer books $10,000 × (10% + 20%) = $3,000; the gross spend is $10,000 × 1.2 a buyer; the rule row says
    so; with no second line the figures are the take rate's alone."""
    result = market_sizing(segments=[_SL])
    (row,) = result.segments

    assert row.annual_value_per_customer.exact == 3_000
    assert row.gross_spend is not None and row.gross_spend.exact == 12_000_000
    assert row.tam is not None and row.tam.exact == 3_000_000
    assert row.som is not None and row.som.exact == 300_000
    assert "second_line_rule" in {item.key for item in result.assumptions}
    plain = market_sizing(segments=[{**_SL, "second_line_percent": None}])
    assert plain.segments[0].annual_value_per_customer.exact == 1_000
    assert "second_line_rule" not in {item.key for item in plain.assumptions}


@pytest.mark.parametrize(
    ("field", "needed"),
    [("take_rate_percent", Fraction(20)), ("second_line_percent", Fraction(30))],
    ids=["take-rate", "second-line"],
)
def test_a_break_even_on_one_share_holds_the_other_and_fed_back_reaches_the_target(
    field: str, needed: Fraction
) -> None:
    """SOM = 100 × $10,000 × (take + second): $400,000 needs a take rate of 20% beside the 20% second line, or a second
    line of 30% beside the 10% take rate; each value, fed back as a sensitivity value, reaches the target exactly."""
    row = {"field": field, "segment": 1, "values": ["5"]}
    result = market_sizing(segments=[_SL], som_target="400000", sensitivity=[row])
    at_target = result.sensitivity[0].at_som_target

    assert at_target is not None and at_target.reach == "value" and at_target.value is not None
    assert at_target.value.exact * 100 == needed
    moved = market_sizing(segments=[_SL], sensitivity=[{**row, "values": [str(needed)]}])
    assert moved.sensitivity[0].cases[0].som is not None and moved.sensitivity[0].cases[0].som.exact == 400_000


def test_a_take_rate_break_even_above_the_cap_or_at_or_below_zero_is_out_of_range() -> None:
    """A take rate above 100% is out of range (a second line has no cap); so is one the second line alone already
    passes ($200,000 needs a take rate of 0%, which no segment can take)."""
    row = {"field": "take_rate_percent", "segment": 1, "values": ["5"]}
    above = market_sizing(segments=[_SL], som_target="1500000", sensitivity=[row]).sensitivity[0].at_som_target
    second = {"field": "second_line_percent", "segment": 1, "values": ["5"]}
    big = market_sizing(segments=[_SL], som_target="1500000", sensitivity=[second]).sensitivity[0].at_som_target
    top_down = [{"amount": "2000000", "compare_to": "tam"}]
    zero = market_sizing(segments=[_SL], top_down=top_down, sensitivity=[row]).sensitivity[0].at_top_down

    assert above is not None and above.reach == "out_of_range"
    assert big is not None and big.reach == "value" and big.value is not None and big.value.exact * 100 == 140
    assert zero is not None and zero.reach == "out_of_range"


def test_a_sensitivity_row_on_a_second_line_the_segment_does_not_give_is_refused() -> None:
    row = {"field": "second_line_percent", "segment": 1, "values": ["5"]}

    with pytest.raises(ValidationError, match="gives no second_line_percent to change"):
        market_sizing(segments=[{**_SL, "second_line_percent": None}], sensitivity=[row])


def test_no_market_count_units_som_months_and_a_second_line_together() -> None:
    """25 units at $40,000 a year, a 10% second line, over 30 months, with no market count: SOM = 25 × $40,000 × 110%
    = $1,100,000, with no TAM, SAM or SOM customers, and every rule row present."""
    segment = {"price": "40000", "price_period_months": 12, "obtainable_units": "25", "second_line_percent": "10"}
    result = market_sizing(segments=[segment], som_months=30)
    (row,) = result.segments

    assert row.som is not None and row.som.exact == 1_100_000
    assert (row.tam, row.sam, row.som_customers, row.new_customers_per_year) == (None, None, None, None)
    assert {"no_market_count_rule", "units_rule", "second_line_rule"} <= {item.key for item in result.assumptions}
    assert "no_market_count" in result.flags and "no_horizon_given" not in result.flags
    # The units rule row says what the SOM line works: with a second line, on the take rate plus that line.
    rules = {item.key: item.setting for item in result.assumptions}
    assert rules["units_rule"] == "SOM = the units to win × the price a year × (the take rate + the second line)"
    plain = market_sizing(segments=[_UC_LICENCES])
    assert {item.key: item.setting for item in plain.assumptions}["units_rule"] == (
        "SOM = the units to win × the price a year × the take rate"
    )


def test_a_count_equal_to_what_is_won_is_no_ceiling_on_a_sensitivity_value_or_a_break_even() -> None:
    """The typed 40 is the SOM again, not a market: a value of 50 is taken, the break-even of 60 for $3,000,000 is a
    value (not out of range), as with the count left out."""
    rows = [{"field": "obtainable_customers", "segment": 1, "values": ["30", "50"]}]
    equal = market_sizing(segments=[{**_NC_TO_WIN, "customers": "40"}], som_target="3000000", sensitivity=rows)
    left_out = market_sizing(segments=[_NC_TO_WIN], som_target="3000000", sensitivity=rows)

    for result in (equal, left_out):
        (row,) = result.sensitivity
        assert row.cases[1].som is not None and row.cases[1].som.exact == 2_500_000
        assert row.at_som_target is not None and row.at_som_target.reach == "value"
        assert row.at_som_target.value is not None and row.at_som_target.value.exact == 60
        assert "som_target_out_of_reach" not in result.flags


def test_a_count_whose_units_equal_the_units_to_win_is_no_market_count() -> None:
    """25 customers of one unit each, winning 25 units, is the SOM typed twice: no TAM or SAM, flagged; 25 customers of
    10 units each, winning 25 units, counts its market."""
    twin = market_sizing(segments=[{**_UC_LICENCES, "customers": "25"}])
    counted = market_sizing(segments=[{**_UC_LICENCES, "customers": "25", "units_per_customer": "10"}])

    assert not twin.segments[0].market_counted and twin.segments[0].tam is None
    assert "no_market_count" in twin.flags
    assert counted.segments[0].market_counted and counted.segments[0].tam is not None
