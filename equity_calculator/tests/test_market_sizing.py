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
from equity_calculator.exact import price_quantity
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
