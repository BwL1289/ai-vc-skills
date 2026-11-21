"""One holder's dilution through rounds: the worked vectors, amounts, no rounds, every refusal, and seeded properties.

Pure computation: no DB, no network, nothing written. The largest run the model takes is timed in a child process
so a slow import or a cold cache never counts against it. The CLI and the Dilution sheet are ``test_holder_cli.py``.
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
from equity_calculator.schemas.equity_dilution import MAX_ROUNDS, DilutionInput, DilutionRound
from pydantic import ValidationError
from tests.support import DILUTION_ROUNDS, dilution

_SEED = 20261118
_RUNS = 60
_ONE = Fraction(1)
_CHILD_TIMEOUT_S = 60
_WORST_CASE_SECONDS = 1.0


def test_each_round_keeps_one_minus_n_minus_p_of_the_stake() -> None:
    """50% through (20%, 10% pool), (20%, 5%), (15%, none): 7/20, 21/80, then 357/1600 = 0.223125 exactly."""
    result = dilution(holder_percent="50", rounds=DILUTION_ROUNDS)

    assert [row.stake_after.exact for row in result.rows] == [Fraction(7, 20), Fraction(21, 80), Fraction(357, 1600)]
    assert [row.kept.exact for row in result.rows] == [Fraction(7, 10), Fraction(3, 4), Fraction(17, 20)]
    assert [row.stake_lost.exact for row in result.rows] == [Fraction(3, 20), Fraction(7, 80), Fraction(63, 1600)]
    assert [row.index for row in result.rows] == [1, 2, 3]
    assert result.initial_stake.exact == Fraction(1, 2)
    assert result.final_stake.exact == Fraction(357, 1600)
    assert result.final_stake.rounded == Decimal("0.223125")
    assert result.kept_overall.exact == Fraction(357, 800)
    assert {item.key for item in result.assumptions} == {"dilution_rule", "pool_basis", "no_participation"}


def test_a_round_given_as_amounts_sells_i_over_v_plus_i() -> None:
    """$8M pre-money and $2M in: n = 1/5, post-money $10M, and the holder's value is their stake at it."""
    result = dilution(holder_percent="35", rounds=[{"pre_money": "8000000", "investment": "2000000"}])
    row = result.rows[0]

    assert row.investor_share.exact == Fraction(1, 5)
    assert row.pool_share.exact == 0
    assert row.stake_after.exact == Fraction(7, 25)
    assert row.post_money is not None and row.post_money.exact == 10_000_000
    assert row.holder_value is not None and row.holder_value.exact == 2_800_000
    assert "stake_from_amounts" in {item.key for item in result.assumptions}


def test_a_round_given_as_a_percent_has_no_post_money() -> None:
    """Without amounts there is no valuation to price the stake at, so the money lines stay empty."""
    row = dilution(holder_percent="10", rounds=[{"investor_percent": "25"}]).rows[0]

    assert row.post_money is None
    assert row.holder_value is None


def test_no_rounds_leaves_the_stake_as_it_was() -> None:
    """An empty list of rounds is a holder before any round: the final stake is the first one, all of it kept."""
    result = dilution(holder_percent="12.5", rounds=[])

    assert result.rows == ()
    assert result.final_stake.exact == Fraction(1, 8)
    assert result.kept_overall.exact == _ONE


def test_a_whole_company_holder_and_a_tiny_round_stay_exact() -> None:
    """100% through a round selling 0.0001%: the stake left is 999999/1000000 of the company, not a float."""
    result = dilution(holder_percent="100", rounds=[{"investor_percent": "0.0001"}])

    assert result.final_stake.exact == Fraction(999_999, 1_000_000)


@pytest.mark.parametrize(
    ("round_terms", "message"),
    [
        ({"investor_percent": "60", "pool_percent": "40"}, "must take less than 100%"),
        ({"investor_percent": "90", "pool_percent": "10.5"}, "take 100.5000% of the company"),
        ({"pool_percent": "10"}, "give exactly one of investor_percent, pre_money with investment (got 0)"),
        (
            {"investor_percent": "20", "pre_money": "8000000", "investment": "2000000"},
            "give exactly one of investor_percent, pre_money with investment (got 2)",
        ),
        ({"pre_money": "8000000"}, "give pre_money and investment together"),
        ({"investment": "2000000"}, "give pre_money and investment together"),
        ({"investor_percent": "100"}, "less than 100"),
        ({"investor_percent": "-1"}, "greater than or equal to 0"),
        ({"pre_money": "0", "investment": "1"}, "greater than 0"),
        ({"investor_percent": "20", "colour": "red"}, "Extra inputs are not permitted"),
    ],
)
def test_a_round_that_cannot_be_read_or_leaves_nothing_is_refused(round_terms: dict[str, object], message: str) -> None:
    """Each round needs exactly one way to read n, and n + p below 1 so the earlier holders keep something."""
    with pytest.raises(ValidationError) as caught:
        DilutionRound.model_validate(round_terms)

    assert message in str(caught.value)


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"holder_percent": "0", "rounds": []}, "greater than 0"),
        ({"holder_percent": "100.01", "rounds": []}, "less than or equal to 100"),
        ({"rounds": []}, "Field required"),
        ({"holder_percent": "50"}, "Field required"),
        ({"holder_percent": "50", "rounds": [{"investor_percent": "1"}] * (MAX_ROUNDS + 1)}, "at most 20 items"),
    ],
)
def test_a_holder_out_of_range_or_too_many_rounds_is_refused(fields: dict[str, object], message: str) -> None:
    """The stake is above 0 and at most 100%, the rounds are given (even if none), and there are at most 20."""
    with pytest.raises(ValidationError) as caught:
        DilutionInput.model_validate(fields)

    assert message in str(caught.value)


def _random_round(rng: random.Random) -> dict[str, object]:
    """A round as a percent (two places, up to 40%) or as amounts (n up to 1/2), with a new pool of up to 15% half the
    time, so n + p stays below 1 and every round is accepted."""
    terms: dict[str, object] = {}
    if rng.random() < 0.5:
        terms["investor_percent"] = str(Decimal(rng.randint(0, 4000)).scaleb(-2))
    else:
        terms["pre_money"] = str(rng.randint(4, 200) * 500_000)
        terms["investment"] = str(rng.randint(1, 20) * 100_000)
    if rng.random() < 0.5:
        terms["pool_percent"] = str(rng.randint(0, 15))

    return terms


def test_seeded_runs_hold_every_property_exactly() -> None:
    """Random holders through 0 to 20 rounds: nothing negative, never growing, each step and the whole chain exact."""
    for step in range(_RUNS):
        rng = random.Random(_SEED + step)
        result = dilution(
            holder_percent=str(Decimal(rng.randint(1, 10_000)).scaleb(-2)),
            rounds=[_random_round(rng) for _ in range(rng.randint(0, MAX_ROUNDS))],
        )
        product = _ONE
        before = result.initial_stake.exact
        for row in result.rows:
            kept = row.kept.exact
            assert 0 < kept <= _ONE, step
            assert row.stake_before.exact == before, step
            assert row.stake_after.exact == before * kept, step
            assert 0 < row.stake_after.exact <= before, step
            assert row.stake_lost.exact >= 0, step
            assert kept == _ONE - row.investor_share.exact - row.pool_share.exact, step
            before = row.stake_after.exact
            product *= kept

        assert result.final_stake.exact == result.initial_stake.exact * product, step
        assert sum((row.stake_lost.exact for row in result.rows), Fraction(0)) == (
            result.initial_stake.exact - result.final_stake.exact
        ), step
        assert result.kept_overall.exact == product, step


# The child builds the largest run the model takes: 20 rounds of 28-digit values, half of them given as amounts.
_CHILD_CODE = """
import json, time
from equity_calculator.schemas.equity_dilution import MAX_ROUNDS, DilutionInput
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.text import render_sheet
from equity_calculator.workbook import build_workbook

def item(index):
    if index % 2:
        return {"pre_money": f"{98765432109 + index}.87654321098765432", "investment": "1234567890.123456789012345678",
                "pool_percent": "1.234567890123456789012345678"}
    return {"investor_percent": "2.345678901234567890123456789", "pool_percent": "0.9876543210987654321098765432"}

fields = {"holder_percent": "33.33333333333333333333333333", "rounds": [item(index) for index in range(MAX_ROUNDS)]}
started = time.perf_counter()
result = compute(DilutionInput.model_validate(fields))
sheet = sheet_for(result)
render_sheet(sheet)
build_workbook([sheet])
print(json.dumps({"rounds": len(result.rows), "seconds": time.perf_counter() - started}))
"""


def test_the_largest_run_computes_within_a_second() -> None:
    """Twenty rounds with 28-digit values: validate, compute, report and workbook under a second, in a child."""
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
    assert report["rounds"] == MAX_ROUNDS
    assert report["seconds"] < _WORST_CASE_SECONDS, report
