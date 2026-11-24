"""The exit waterfall against a brute force over every convert-or-stay profile, seeded properties and a timing.

The oracle shares no code with ``equity_calculator.waterfall``: it pays each rank the share of what it is owed that the
exit covers, finds the per-share price of the rest by walking the caps' breakpoints in order, then works all 2^k
profiles and keeps those no class wants to leave (each converts exactly when converting pays it strictly more). Seeds
are fixed (``random.Random``), so a failure names its seed and reruns the same. The 12-class worst case is timed in a
child process.
"""

from __future__ import annotations

import itertools
import json
import os
import random
import subprocess
import sys
from decimal import ROUND_HALF_UP, Decimal
from fractions import Fraction
from typing import NamedTuple

from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_waterfall import MAX_CLASSES, WaterfallInput

_SEED = 20261118
_ORACLE_RUNS = 300
_ORACLE_MAX_CLASSES = 6
_PROPERTY_RUNS = 60
_MAX_SHARES = 5_000_000
_MAX_INVESTED = 20_000_000
_MAX_COMMON = 10_000_000
_EXIT_SCALES = (1, 3, 10, 40)
_RANKS = (1, 1, 2, 3, MAX_CLASSES)
_MULTIPLES = ("0", "0.5", "1", "1", "1.25", "2", "3")
_CAP_HEADROOM = ("0", "0.75", "1", "2", "5")
_PARTICIPATIONS = ("none", "full", "capped")
_SMALLEST_CAP = Decimal("0.5")
# One exit in this many carries tenths of a cent, so the cents split has a remainder to place.
_MILS_ONE_IN = 4
_MILS = 999
_CENT = Decimal("0.01")
_ZERO = Fraction(0)
_WHOLE = Fraction(1)
_CHOICES = (False, True)
_CHILD_TIMEOUT_S = 60
_WORST_CASE_SECONDS = 1.0

Profile = tuple[bool, ...]


class _Take(NamedTuple):
    """What each class and the common stock take under one profile."""

    classes: tuple[Fraction, ...]
    common: Fraction


def _random_class(rng: random.Random) -> dict[str, object]:
    """One preferred class: any participation, a multiple from 0 to 3x, ranks with gaps, a cap at or above it."""
    multiple = rng.choice(_MULTIPLES)
    participation = rng.choice(_PARTICIPATIONS)
    fields: dict[str, object] = {
        "shares": rng.randint(1, _MAX_SHARES),
        "invested": str(rng.randint(1, _MAX_INVESTED)),
        "preference_multiple": multiple,
        "rank": rng.choice(_RANKS),
        "participation": participation,
    }
    if participation == "capped":
        fields["cap_multiple"] = str(max(Decimal(multiple) + Decimal(rng.choice(_CAP_HEADROOM)), _SMALLEST_CAP))

    return fields


def _random_exit(rng: random.Random, max_classes: int) -> WaterfallInput:
    """An exit over 0 to ``max_classes`` random classes, from nothing to many times what they put in."""
    classes = [_random_class(rng) for _ in range(rng.randint(0, max_classes))]
    invested = sum(int(str(item["invested"])) for item in classes)
    amount = str(rng.randint(0, max(invested, 1) * rng.choice(_EXIT_SCALES)))
    if rng.randrange(_MILS_ONE_IN) == 0:
        amount = f"{amount}.{rng.randint(0, _MILS):03d}"
    fields = {"exit_amount": amount, "common_shares": rng.randint(1, _MAX_COMMON), "classes": classes}

    return WaterfallInput.model_validate(fields)


def _oracle_take(inputs: WaterfallInput, converts: Profile) -> _Take:
    """Each class's take and the common's for one profile, worked independently of ``equity_calculator.waterfall``."""
    classes = inputs.classes
    owed = [Fraction(item.preference_multiple) * Fraction(item.invested) for item in classes]
    paid = [_ZERO] * len(classes)
    left = Fraction(inputs.exit_amount)
    for rank in sorted({item.rank for item in classes}):
        staying = [index for index, item in enumerate(classes) if item.rank == rank and not converts[index]]
        rank_owed = sum((owed[index] for index in staying), _ZERO)
        if rank_owed == _ZERO:
            continue

        covered = min(_WHOLE, left / rank_owed)
        for index in staying:
            paid[index] = owed[index] * covered
        left -= rank_owed * covered

    takers = [index for index, item in enumerate(classes) if converts[index] or item.participation != "none"]
    headroom = {
        index: Fraction(cap) * Fraction(classes[index].invested) - paid[index]
        for index in takers
        if not converts[index] and (cap := classes[index].cap_multiple) is not None
    }
    slope = Fraction(inputs.common_shares + sum(classes[index].shares for index in takers))
    fixed = _ZERO
    stopped: set[int] = set()
    for level, index in sorted((room / classes[index].shares, index) for index, room in headroom.items()):
        if fixed + slope * level >= left:
            break
        fixed += headroom[index]
        slope -= classes[index].shares
        stopped.add(index)
    price = (left - fixed) / slope
    takes = list(paid)
    for index in takers:
        takes[index] += headroom[index] if index in stopped else classes[index].shares * price

    return _Take(tuple(takes), inputs.common_shares * price)


def _with(profile: Profile, index: int, choice: bool) -> Profile:
    return (*profile[:index], choice, *profile[index + 1 :])


def _brute_force(inputs: WaterfallInput) -> tuple[dict[Profile, _Take], set[Profile]]:
    """Every profile's takes, and the profiles where each class's choice is its strictly better side."""
    count = len(inputs.classes)
    table = {profile: _oracle_take(inputs, profile) for profile in itertools.product(_CHOICES, repeat=count)}
    stable = {
        profile
        for profile in table
        if all(
            profile[index]
            == (table[_with(profile, index, True)].classes[index] > table[_with(profile, index, False)].classes[index])
            for index in range(count)
        )
    }

    return table, stable


def test_the_stable_choice_matches_a_brute_force_over_every_profile() -> None:
    """300 seeded exits of 0 to 6 classes: the choice found is one the brute force calls stable, and every payout,
    both sides of every choice and the common's payout equal the oracle's exactly."""
    seen = {"some class converts": 0, "no class converts": 0, "a cap stops a class": 0}
    for step in range(_ORACLE_RUNS):
        seed = _SEED + step
        inputs = _random_exit(random.Random(seed), _ORACLE_MAX_CLASSES)
        table, stable = _brute_force(inputs)
        result = compute(inputs)
        ours = tuple(row.converts for row in result.rows)

        assert ours in stable, (seed, ours, stable)
        for index, row in enumerate(result.rows):
            assert row.payout.exact == table[ours].classes[index], (seed, index)
            assert row.payout_if_stays.exact == table[_with(ours, index, False)].classes[index], (seed, index)
            assert row.payout_if_converts.exact == table[_with(ours, index, True)].classes[index], (seed, index)
        assert result.common_payout.exact == table[ours].common, seed
        seen["some class converts"] += any(ours)
        seen["no class converts"] += not any(ours)
        seen["a cap stops a class"] += any(row.capped for row in result.rows)

    assert all(seen.values()), seen


def test_seeded_exits_up_to_twelve_classes_pay_non_negative_amounts_that_add_up_exactly() -> None:
    """60 seeded exits of 0 to 12 classes: no payout is negative, the exact payouts sum to the exit, the cents sum
    to the exit rounded to the cent, and each class's choice and payout follow from both sides it was shown."""
    for step in range(_PROPERTY_RUNS):
        seed = _SEED + _ORACLE_RUNS + step
        inputs = _random_exit(random.Random(seed), MAX_CLASSES)
        result = compute(inputs)
        payouts = [*(row.payout for row in result.rows), result.common_payout]

        assert all(payout.exact >= 0 and payout.rounded >= 0 for payout in payouts), seed
        assert sum(payout.exact for payout in payouts) == Fraction(inputs.exit_amount) == result.total.exact, seed
        # Decimal's ROUND_HALF_UP is half away from zero, the calculator's display rounding.
        assert sum(payout.rounded for payout in payouts) == inputs.exit_amount.quantize(_CENT, ROUND_HALF_UP), seed
        assert result.passes <= len(inputs.classes) + 1, seed
        for item, row in zip(inputs.classes, result.rows, strict=True):
            chosen = row.payout_if_converts if row.converts else row.payout_if_stays
            assert row.converts == (row.payout_if_converts.exact > row.payout_if_stays.exact), (seed, row.index)
            assert row.payout.exact == chosen.exact == row.preference_paid.exact + row.residual_share.exact, seed
            if row.converts:
                assert (row.preference_paid.exact, row.capped) == (0, False), (seed, row.index)
            if item.cap_multiple is not None and not row.converts:
                assert row.payout.exact <= Fraction(item.cap_multiple) * Fraction(item.invested), (seed, row.index)
            if item.participation == "none" and not row.converts:
                assert row.residual_share.exact == 0, (seed, row.index)


# The child computes 12 classes of every participation over a sweep of exits, then reports and writes the last.
_CHILD_CODE = """
import json, time
from equity_calculator.schemas.equity_waterfall import MAX_CLASSES, WaterfallInput
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.text import render_sheet
from equity_calculator.workbook import build_workbook

kinds = ("none", "full", "capped")
classes = []
for index in range(MAX_CLASSES):
    item = {"shares": 1_000_000 + 37_000 * index, "invested": str(2_000_000 + 450_000 * index),
            "preference_multiple": ("1", "1.5", "2")[index % 3], "rank": index % 4 + 1,
            "participation": kinds[index % 3]}
    if item["participation"] == "capped":
        item["cap_multiple"] = str(2 + index % 4)
    classes.append(item)
slowest, passes = 0.0, 0
for exit_amount in ("0", "1000000", "25000000", "60000000", "120000000", "300000000", "999999999999.99"):
    started = time.perf_counter()
    fields = {"exit_amount": exit_amount, "common_shares": 9_000_000, "classes": classes}
    result = compute(WaterfallInput.model_validate(fields))
    slowest = max(slowest, time.perf_counter() - started)
    passes = max(passes, result.passes)
started = time.perf_counter()
sheet = sheet_for(result)
render_sheet(sheet)
build_workbook([sheet])
timings = {"slowest exit": slowest, "report and workbook": time.perf_counter() - started}
print(json.dumps({"passes": passes, "converts": [row.converts for row in result.rows], "timings": timings}))
"""


def test_twelve_classes_compute_within_a_second() -> None:
    """12 classes of every participation over 7 exits, then the report and workbook: each step under a second."""
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
    assert report["passes"] > 1
    assert any(report["converts"])
    for stage, seconds in report["timings"].items():
        assert seconds < _WORST_CASE_SECONDS, (stage, seconds)
