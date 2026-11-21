"""A grant vesting month by month: the schedule, termination, both triggers, prices, refusals and seeded properties.

Pure computation: no DB, no network, nothing written. The longest schedule the model takes is timed in a child
process. The CLI and the Vesting sheet are ``test_holder_cli.py``.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction

import pytest
from equity_calculator.schemas.equity_vesting import MAX_VESTING_MONTHS, VestingInput
from pydantic import ValidationError
from tests.support import vesting

_GRANT = 48_000
_SEED = 20261118
_RUNS = 40
_CHILD_TIMEOUT_S = 60
_WORST_CASE_SECONDS = 1.0


def _vested(**fields: object) -> Fraction:
    return vesting(grant_shares=_GRANT, **fields).vested.exact


@pytest.mark.parametrize(
    ("month", "vested"),
    [(0, 0), (11, 0), (12, 12_000), (13, 13_000), (30, 30_000), (47, 47_000), (48, _GRANT), (600, _GRANT)],
)
def test_the_standard_schedule_vests_nothing_before_the_cliff_then_a_48th_a_month(month: int, vested: int) -> None:
    """4 years with a 1-year cliff: 0 at month 11, the 12 months at once at month 12, then 1,000 a month to 48,000."""
    assert _vested(month=month) == vested


def test_a_termination_stops_the_schedule_and_one_before_the_cliff_forfeits_all() -> None:
    """Terminated at month 20, the grant stays at 20,000 by month 30; terminated at month 10, nothing ever vests."""
    stopped = vesting(grant_shares=_GRANT, month=30, termination_month=20)

    assert stopped.vested.exact == 20_000
    assert stopped.unvested.exact == 28_000
    assert stopped.stopped_month == 20
    assert _vested(month=30, termination_month=10) == 0


def test_a_strike_and_a_common_price_give_the_cost_and_the_intrinsic_value() -> None:
    """30,000 vested at a $0.50 strike: $15,000 to exercise; at $2 common, $1.50 spread and $45,000 of value."""
    result = vesting(grant_shares=_GRANT, month=30, strike_price="0.50", common_price="2")

    assert result.exercise_cost is not None and result.exercise_cost.exact == 15_000
    assert result.spread is not None and result.spread.exact == Fraction(3, 2)
    assert result.intrinsic_value is not None and result.intrinsic_value.exact == 45_000
    assert result.moneyness == "in_the_money"
    assert "intrinsic_value" in {item.key for item in result.assumptions}


@pytest.mark.parametrize(("common", "moneyness"), [("0.50", "at_the_money"), ("0.10", "underwater")])
def test_a_common_price_at_or_below_the_strike_is_worth_nothing(common: str, moneyness: str) -> None:
    """The value never goes below 0: at or under the strike the spread and the value are 0."""
    result = vesting(grant_shares=_GRANT, month=30, strike_price="0.50", common_price=common)

    assert result.spread is not None and result.spread.exact == 0
    assert result.intrinsic_value is not None and result.intrinsic_value.exact == 0
    assert result.moneyness == moneyness


def test_a_strike_alone_gives_the_cost_and_no_value() -> None:
    """Without a common price there is a cost to exercise but no spread, value or verdict.

    The ``intrinsic_value`` row is still listed: it says how the exercise cost is worked, which the strike gives.
    """
    result = vesting(grant_shares=_GRANT, month=30, strike_price="0.50")

    assert result.exercise_cost is not None and result.exercise_cost.exact == 15_000
    assert (result.spread, result.intrinsic_value, result.moneyness) == (None, None, None)
    assert "intrinsic_value" in {item.key for item in result.assumptions}


def test_a_grant_with_no_prices_lists_no_value_row() -> None:
    """No strike and no common price: no cost, no value, and no ``intrinsic_value`` row."""
    result = vesting(grant_shares=_GRANT, month=30)

    assert (result.exercise_cost, result.intrinsic_value) == (None, None)
    assert "intrinsic_value" not in {item.key for item in result.assumptions}


_SINGLE: dict[str, object] = {"acceleration": "single_trigger", "change_of_control_month": 24}


@pytest.mark.parametrize(
    ("fields", "vested", "fired"),
    [
        ({**_SINGLE, "acceleration_percent": "50", "month": 24}, 36_000, 24),
        ({**_SINGLE, "acceleration_percent": "50", "month": 23}, 23_000, None),
        ({**_SINGLE, "acceleration_percent": "50", "month": 30}, 42_000, 24),
        ({**_SINGLE, "acceleration_percent": "100", "month": 24}, _GRANT, 24),
        ({**_SINGLE, "acceleration_percent": "50", "month": 30, "termination_month": 20}, 20_000, None),
        ({**_SINGLE, "acceleration_percent": "50", "month": 30, "termination_month": 24}, 36_000, 24),
        ({**_SINGLE, "acceleration_percent": "50", "month": 30, "termination_month": 26}, 38_000, 24),
        ({**_SINGLE, "acceleration_percent": "50", "change_of_control_month": 6, "month": 6}, 24_000, 6),
        ({**_SINGLE, "acceleration_percent": "25", "acceleration_base": "grant", "month": 24}, 36_000, 24),
        ({**_SINGLE, "acceleration_percent": "75", "acceleration_base": "grant", "month": 24}, _GRANT, 24),
    ],
)
def test_a_single_trigger_vests_part_of_the_unvested_at_the_change_of_control(
    fields: dict[str, object], vested: int, fired: int | None
) -> None:
    """50% of the 24,000 unvested at month 24 adds 12,000; the schedule then runs on; a holder gone before the deal
    gets nothing more; before the cliff the whole grant is unvested; a grant base is capped at what is unvested."""
    result = vesting(grant_shares=_GRANT, **fields)

    assert result.vested.exact == vested
    assert result.fired_month == fired
    assert result.acceleration_fired is (fired is not None)
    assert result.accelerated.exact == result.vested.exact - result.base_vested.exact


_DOUBLE: dict[str, object] = {"acceleration": "double_trigger", "acceleration_percent": "100"}


@pytest.mark.parametrize(
    ("fields", "vested", "fired"),
    [
        ({**_DOUBLE, "change_of_control_month": 24, "termination_month": 26, "month": 30}, _GRANT, 26),
        ({**_DOUBLE, "change_of_control_month": 24, "termination_month": 26, "month": 25}, 25_000, None),
        ({**_DOUBLE, "change_of_control_month": 24, "termination_month": 24, "month": 24}, _GRANT, 24),
        ({**_DOUBLE, "change_of_control_month": 24, "termination_month": 20, "month": 30}, 20_000, None),
        ({**_DOUBLE, "change_of_control_month": 24, "month": 30}, 30_000, None),
    ],
)
def test_a_double_trigger_needs_the_deal_and_a_termination_at_or_after_it(
    fields: dict[str, object], vested: int, fired: int | None
) -> None:
    """The deal alone vests nothing more; a termination at or after it accelerates; one before it only forfeits."""
    result = vesting(grant_shares=_GRANT, **fields)

    assert result.vested.exact == vested
    assert result.fired_month == fired
    assert "double_trigger_window" in {item.key for item in result.assumptions}


def test_whole_shares_rounds_the_vested_count_down() -> None:
    """1,000 shares at month 13 of 48: 270 5/6 exact, 270 whole; the accelerated part is what rounding leaves."""
    exact = vesting(grant_shares=1_000, month=13)
    whole = vesting(grant_shares=1_000, month=13, share_rounding="whole_shares")

    assert exact.vested.exact == Fraction(1_625, 6)
    assert whole.vested.exact == 270
    assert whole.unvested.exact == 730
    assert whole.accelerated.exact == 0


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"month": 30, "cliff_months": 60}, "cliff_months must be at most total_months"),
        ({"month": 30, "common_price": "2"}, "give strike_price with common_price"),
        ({"month": 30, "acceleration": "single_trigger"}, "needs acceleration_percent and change_of_control_month"),
        ({"month": 30, "acceleration_percent": "50"}, "go with acceleration single_trigger or double_trigger"),
        ({"month": 30, "change_of_control_month": 24}, "go with acceleration single_trigger or double_trigger"),
        ({"month": 30, **_SINGLE, "acceleration_percent": "0"}, "greater than 0"),
        ({"month": 30, **_SINGLE, "acceleration_percent": "101"}, "less than or equal to 100"),
        ({"month": MAX_VESTING_MONTHS + 1}, "less than or equal to 600"),
        ({"month": 30, "total_months": 0}, "greater than or equal to 1"),
        ({"month": "30"}, "Input should be a valid integer"),
        ({"month": 30, "strike_price": "-1"}, "greater than or equal to 0"),
        ({}, "Field required"),
    ],
)
def test_a_grant_that_does_not_fit_together_is_refused(fields: dict[str, object], message: str) -> None:
    """The cliff fits the schedule, a common price comes with a strike, acceleration terms come with acceleration."""
    with pytest.raises(ValidationError) as caught:
        VestingInput.model_validate({"grant_shares": _GRANT, **fields})

    assert message in str(caught.value)


@pytest.mark.parametrize("grant", [0, -1, "48000"])
def test_a_grant_must_be_a_positive_whole_count(grant: object) -> None:
    with pytest.raises(ValidationError):
        VestingInput.model_validate({"grant_shares": grant, "month": 12})


def _random_grant(rng: random.Random) -> dict[str, object]:
    """A grant with a random schedule, sometimes a termination, an acceleration, prices or whole shares."""
    total = rng.randint(1, MAX_VESTING_MONTHS)
    fields: dict[str, object] = {
        "grant_shares": rng.randint(1, 10_000_000),
        "total_months": total,
        "cliff_months": rng.randint(0, total),
        "share_rounding": rng.choice(["exact", "whole_shares"]),
    }
    if rng.random() < 0.5:
        fields["termination_month"] = rng.randint(0, MAX_VESTING_MONTHS)
    if rng.random() < 0.6:
        fields["acceleration"] = rng.choice(["single_trigger", "double_trigger"])
        fields["acceleration_percent"] = str(rng.randint(1, 100))
        fields["acceleration_base"] = rng.choice(["unvested", "grant"])
        fields["change_of_control_month"] = rng.randint(0, MAX_VESTING_MONTHS)
    if rng.random() < 0.5:
        fields["strike_price"] = str(Decimal(rng.randint(0, 500)).scaleb(-2))
        fields["common_price"] = str(Decimal(rng.randint(0, 500)).scaleb(-2))

    return fields


def test_seeded_grants_never_lose_shares_as_the_months_pass() -> None:
    """Random grants checked month by month: vested never falls, stays within the grant, and the money lines agree."""
    for step in range(_RUNS):
        fields = _random_grant(random.Random(_SEED + step))
        months = sorted({0, MAX_VESTING_MONTHS, *random.Random(-step).sample(range(MAX_VESTING_MONTHS), 60)})
        grant = Fraction(int(str(fields["grant_shares"])))
        previous = Fraction(0)
        for month in months:
            result = vesting(**fields, month=month)
            vested = result.vested.exact
            assert vested >= previous, (step, month)
            assert 0 <= result.base_vested.exact <= vested <= grant, (step, month)
            assert result.accelerated.exact >= 0, (step, month)
            assert result.unvested.exact == grant - vested, (step, month)
            if result.intrinsic_value is not None:
                assert result.intrinsic_value.exact >= 0, (step, month)
            previous = vested


# The child computes the longest schedule at every month it takes, then reports and writes the worst one.
_CHILD_CODE = """
import json, time
from equity_calculator.schemas.equity_vesting import MAX_VESTING_MONTHS, VestingInput
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.text import render_sheet
from equity_calculator.workbook import build_workbook

fields = {"grant_shares": 9_999_999_999_999_999, "total_months": MAX_VESTING_MONTHS,
          "cliff_months": MAX_VESTING_MONTHS - 1, "termination_month": MAX_VESTING_MONTHS,
          "acceleration": "double_trigger", "acceleration_percent": "33.33333333333333333333333333",
          "acceleration_base": "grant", "change_of_control_month": MAX_VESTING_MONTHS - 1,
          "strike_price": "0.1234567890123456789012345678", "common_price": "98765432.10987654321098765432"}
timings = {}
started = time.perf_counter()
for month in range(MAX_VESTING_MONTHS + 1):
    result = compute(VestingInput.model_validate({**fields, "month": month}))
timings["every month of the longest schedule"] = time.perf_counter() - started
started = time.perf_counter()
sheet = sheet_for(result)
render_sheet(sheet)
build_workbook([sheet])
timings["report and workbook"] = time.perf_counter() - started
print(json.dumps({"fired": result.acceleration_fired, "timings": timings}))
"""


def test_the_longest_schedule_computes_within_a_second() -> None:
    """600 months with 28-digit prices, every month 0 to 600, then the report and workbook: each under a second."""
    environment = {**os.environ, "PYTHONPATH": os.pathsep.join(path for path in sys.path if path)}
    finished = subprocess.run(
        [sys.executable, "-c", _CHILD_CODE],
        capture_output=True,
        text=True,
        env=environment,
        timeout=_CHILD_TIMEOUT_S,
        check=False,
    )
    assert finished.returncode == 0, finished.stderr

    report = json.loads(finished.stdout)
    assert report["fired"] is True
    for stage, seconds in report["timings"].items():
        assert seconds < _WORST_CASE_SECONDS, (stage, seconds)
