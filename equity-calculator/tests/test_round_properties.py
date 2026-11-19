"""Seeded property tests of the priced round, plus its worst case timed in a child process.

Random rounds of one to five SAFEs and notes check what must hold for every round: the conversion search lands on
the one choice a 2^k brute force finds, nothing is negative, ownership adds to exactly 1, the cents add to the
post-money, and a SAFE with a cap and a discount gets at least the shares of either term alone. No new dependency:
``random.Random`` with fixed seeds, so a failure names its seed and reruns the same.
"""

from __future__ import annotations

import itertools
import json
import os
import random
import subprocess
import sys
from fractions import Fraction

from equity_calculator.convertibles import convertibles, next_on_cap, price_round, settle
from equity_calculator.errors import EquityComputeError, RoundHasNoPrice
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_round import MAX_INSTRUMENTS, RoundInput, SafeTerms
from pydantic import ValidationError

_SEED = 20261118
_ROUNDS = 60
# At least this many of the random rounds must be accepted and priced, so the properties are never checked on nothing.
_MIN_CHECKED = 40
_MIN_BOTH_TERMS = 10
_ONE = Fraction(1)
_CHILD_TIMEOUT_S = 60
_WORST_CASE_SECONDS = 1.0


def _terms(rng: random.Random, instrument: dict[str, object]) -> dict[str, object]:
    """``instrument`` with a cap (80% of the time), a discount (60%), or both."""
    draw = rng.random()
    if draw < 0.8:
        instrument["valuation_cap"] = str(rng.randint(3, 60) * 1_000_000)
    if draw > 0.4:
        instrument["discount_percent"] = str(rng.choice([10, 15, 20, 25]))

    return instrument


def _random_round(rng: random.Random) -> dict[str, object]:
    """A round of one to five instruments: SAFEs 60% of the time, notes of up to three years otherwise."""
    instruments = []
    for _ in range(rng.randint(1, 5)):
        if rng.random() < 0.6:
            instrument: dict[str, object] = {"kind": "safe", "purchase_amount": str(rng.randint(50, 900) * 1000)}
        else:
            instrument = {
                "kind": "note",
                "principal": str(rng.randint(50, 900) * 1000),
                "interest_rate_percent": str(rng.choice([0, 4, 6, 8])),
                "months_outstanding": rng.randint(0, 36),
                "compounding": rng.choice(["simple", "annual", "monthly"]),
            }
        instruments.append(_terms(rng, instrument))

    return {
        "fully_diluted_shares": rng.randint(5, 20) * 1_000_000,
        "unissued_pool_shares": rng.randint(0, 4) * 250_000,
        "pre_money": str(rng.randint(8, 60) * 1_000_000),
        "investment": str(rng.randint(1, 15) * 1_000_000),
        "target_pool_percent": str(rng.choice([0, 5, 10, 15])),
        "pool_timing": rng.choice(["pre_money", "post_money"]),
        "instruments": instruments,
    }


def _accepted_rounds() -> list[tuple[int, RoundInput]]:
    """Each random round the model accepts and the search prices, with its seed."""
    accepted = []
    for step in range(_ROUNDS):
        try:
            inputs = RoundInput.model_validate(_random_round(random.Random(_SEED + step)))
            settle(inputs, convertibles(inputs))
        except (ValidationError, EquityComputeError):
            continue
        accepted.append((_SEED + step, inputs))

    assert len(accepted) >= _MIN_CHECKED
    return accepted


def _brute_force_fixed_points(inputs: RoundInput) -> list[tuple[bool, ...]]:
    """Every on-cap choice (capped instruments only) that prices and that the next pass leaves unchanged."""
    items = convertibles(inputs)
    fixed = []
    for choice in itertools.product([False, True], repeat=len(items)):
        if any(on_cap and item.cap is None for on_cap, item in zip(choice, items, strict=True)):
            continue
        try:
            priced = price_round(inputs, items, choice)
        except RoundHasNoPrice:
            continue
        if next_on_cap(inputs, items, priced) == choice:
            fixed.append(choice)

    return fixed


def _without(inputs: RoundInput, index: int, dropped: str) -> RoundInput:
    """``inputs`` with one term (``dropped``) taken off instrument ``index``, validated again."""
    instruments = [item.model_dump(exclude_none=True) for item in inputs.instruments]
    del instruments[index][dropped]

    return RoundInput.model_validate({**inputs.model_dump(exclude={"instruments"}), "instruments": instruments})


def test_the_search_lands_on_the_one_choice_brute_force_finds() -> None:
    """Over all 2^k cap choices, exactly one is a fixed point, and it is the one the search settles on."""
    for seed, inputs in _accepted_rounds():
        items = convertibles(inputs)
        settled = settle(inputs, items)

        assert _brute_force_fixed_points(inputs) == [settled.on_cap], seed
        assert settled.passes <= sum(item.cap is not None for item in items) + 1, seed


def test_nothing_is_negative_ownership_is_one_and_the_cents_add_up() -> None:
    """Every share count, stake and value is at least 0; ownership adds to exactly 1; values add to the post-money."""
    for seed, inputs in _accepted_rounds():
        result = compute(inputs)

        assert result.price_per_share.exact > 0, seed
        assert all(row.shares.exact > 0 and row.conversion_price.exact > 0 for row in result.conversions), seed
        assert all(row.shares.exact >= 0 and row.value.exact >= 0 for row in result.rows), seed
        assert sum((row.ownership.exact for row in result.rows), Fraction(0)) == _ONE, seed
        assert sum((row.shares.exact for row in result.rows), Fraction(0)) == result.total_shares.exact, seed
        assert sum(row.value.rounded for row in result.rows) == result.post_money.rounded, seed


def test_a_safe_with_both_terms_gets_at_least_either_term_alone() -> None:
    """Dropping a cap-and-discount SAFE's cap, or its discount, never gives it more shares."""
    compared = 0
    for seed, inputs in _accepted_rounds():
        both = compute(inputs)
        for index, terms in enumerate(inputs.instruments):
            if not isinstance(terms, SafeTerms) or terms.valuation_cap is None or terms.discount_percent is None:
                continue
            for dropped in ("valuation_cap", "discount_percent"):
                try:
                    alone = compute(_without(inputs, index, dropped))
                except (ValidationError, EquityComputeError):
                    continue
                assert both.conversions[index].shares.exact >= alone.conversions[index].shares.exact, (seed, dropped)
                compared += 1

    assert compared >= _MIN_BOTH_TERMS


# The child builds the largest round the model takes, at every bound at once, and times each stage itself.
_CHILD_CODE = """
import json, time
from equity_calculator.schemas.equity_round import MAX_INSTRUMENTS, MAX_NOTE_MONTHS, RoundInput
from equity_calculator.convertibles import convertibles, next_on_cap, price_round
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.text import render_sheet
from equity_calculator.workbook import build_workbook

def instrument(index):
    if index % 2:
        return {"kind": "safe", "purchase_amount": f"{1234 + index}.567890123456789012345678",
                "valuation_cap": "98765432109.87654321098765432", "discount_percent": "17.12345678901234567890123456"}
    note = {"kind": "note", "principal": f"{2345 + index}.678901234567890123456789",
            "interest_rate_percent": "7.123456789012345678901234567", "valuation_cap": "87654321098.76543210987654321",
            "discount_percent": "23.45678901234567890123456789"}
    if index % 4 == 0:
        return {**note, "compounding": "annual", "stub_rule": "fractional_power",
                "months_outstanding": MAX_NOTE_MONTHS - 1}
    if index % 4 == 2 and index < 10:
        return {**note, "compounding": "monthly", "stub_rule": "fractional_power", "day_count": "actual_360",
                "issue_date": "2000-01-01", "conversion_date": "2049-12-31"}
    return {**note, "compounding": "monthly", "months_outstanding": MAX_NOTE_MONTHS}

fields = {"fully_diluted_shares": 9_999_999_999_999_999, "unissued_pool_shares": 1_234_567_890_123_457,
          "pre_money": "123456789012345.6789012345678", "investment": "98765432109876.54321098765432",
          "target_pool_percent": "12.34567890123456789012345678",
          "instruments": [instrument(index) for index in range(MAX_INSTRUMENTS)]}
timings = {}
started = time.perf_counter()
inputs = RoundInput.model_validate(fields)
result = compute(inputs)
sheet = sheet_for(result)
render_sheet(sheet)
build_workbook([sheet])
timings["validate, compute, report and workbook"] = time.perf_counter() - started

items = convertibles(inputs)
on_cap = tuple(item.cap is not None for item in items)
started = time.perf_counter()
for _ in range(sum(item.cap is not None for item in items) + 1):
    next_on_cap(inputs, items, price_round(inputs, items, on_cap))
timings["the most passes the search may take"] = time.perf_counter() - started
print(json.dumps({"instruments": len(inputs.instruments), "passes": result.passes, "timings": timings}))
"""


def test_the_largest_round_computes_within_a_second() -> None:
    """Fifty instruments with 28-digit values, 600-month and 50-year notes: each stage under a second, in a child."""
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
    assert report["instruments"] == MAX_INSTRUMENTS
    assert report["passes"] >= 1
    for stage, seconds in report["timings"].items():
        assert seconds < _WORST_CASE_SECONDS, (stage, seconds)
