"""An exit waterfall: worked vectors, both sides of each choice, refusals and the search's pass bound.

Pure computation: no DB, no network, nothing written. The brute-force oracle over every convert-or-stay profile, the
seeded properties and the 12-class timing are ``test_waterfall_oracle.py``; the CLI and the sheet are
``test_waterfall_cli.py``.
"""

from __future__ import annotations

from decimal import Decimal

import pytest
from equity_calculator.errors import EquityComputeError, NoConversionEquilibrium
from equity_calculator.schemas.equity_waterfall import MAX_CLASSES, PreferredClass, WaterfallInput
from equity_calculator.waterfall import conversion_profile, default_pass_limit
from pydantic import ValidationError
from tests.support import WATERFALL_A, WATERFALL_B, WATERFALL_COMMON, waterfall

_A_FULL = {**WATERFALL_A, "participation": "full"}
_A_CAPPED = {**WATERFALL_A, "participation": "capped", "cap_multiple": "3"}
_A_JUNIOR = {**WATERFALL_A, "rank": 2}
_ONE_PASS = 1
_FIRST, _SECOND = 0, 1


@pytest.mark.parametrize(
    ("exit_amount", "classes", "converts", "payouts", "common", "passes"),
    [
        # B's $10M first; A converts: 2/9 of the $40M left beats its $5M preference.
        ("50000000", (WATERFALL_A, WATERFALL_B), (True, False), ("8888888.89", "10000000.00"), "31111111.11", 2),
        # B is senior: it takes $10M of $12M, A takes the $2M left of its $5M; converting would give A 2/9 of $2M.
        ("12000000", (_A_JUNIOR, WATERFALL_B), (False, False), ("2000000.00", "10000000.00"), "0.00", 1),
        # Equal rank, short of both preferences ($15M owed): $6M is shared 1:2 as owed, $2M and $4M.
        ("6000000", (WATERFALL_A, WATERFALL_B), (False, False), ("2000000.00", "4000000.00"), "0.00", 1),
        # Full participation: A keeps its $5M and takes 2/9 of the $35M left beside the common.
        ("50000000", (_A_FULL, WATERFALL_B), (False, False), ("12777777.78", "10000000.00"), "27222222.22", 1),
        # Capped at 3x ($15M), $40M: A's $5M + 2/9 of $25M is under the cap, and more than converting would give.
        ("40000000", (_A_CAPPED, WATERFALL_B), (False, False), ("10555555.56", "10000000.00"), "19444444.44", 1),
        # $70M: A would reach $17.2M, so it stops at $15M and the common takes the $45M left; converting gives $13.3M.
        ("70000000", (_A_CAPPED, WATERFALL_B), (False, False), ("15000000.00", "10000000.00"), "45000000.00", 1),
        # $100M: converting (2/9 of $90M = $20M) beats the $15M cap; B then takes $10M either way, a tie, so it stays.
        ("100000000", (_A_CAPPED, WATERFALL_B), (True, False), ("20000000.00", "10000000.00"), "70000000.00", 2),
    ],
)
def test_worked_exits_give_each_class_its_better_side(
    exit_amount: str,
    classes: tuple[dict[str, object], ...],
    converts: tuple[bool, ...],
    payouts: tuple[str, ...],
    common: str,
    passes: int,
) -> None:
    """Hand-worked exits: each class's choice, its payout in cents, the common's payout, and the passes taken."""
    result = waterfall(exit_amount, *classes)

    assert tuple(row.converts for row in result.rows) == converts
    assert tuple(row.payout.rounded for row in result.rows) == tuple(Decimal(payout) for payout in payouts)
    assert result.common_payout.rounded == Decimal(common)
    assert result.total.exact == Decimal(exit_amount)
    assert result.passes == passes
    assert [row.index for row in result.rows] == list(range(1, len(classes) + 1))


def test_each_row_shows_both_sides_of_its_choice() -> None:
    """$50M: A takes $5M staying and $8.9M converting (B staying); B takes $10M staying and $5M converting (A
    converted, so all 10M shares split $50M); each payout is the side chosen, preference plus part of the rest."""
    first, second = waterfall("50000000", WATERFALL_A, WATERFALL_B).rows

    assert (first.payout_if_stays.rounded, first.payout_if_converts.rounded) == (
        Decimal(5_000_000),
        Decimal("8888888.89"),
    )
    assert (second.payout_if_stays.rounded, second.payout_if_converts.rounded) == (
        Decimal(10_000_000),
        Decimal(5_000_000),
    )
    assert first.payout.exact == first.payout_if_converts.exact == first.residual_share.exact
    assert first.preference_paid.exact == 0 and first.preference_owed.exact == 5_000_000
    assert second.payout.exact == second.payout_if_stays.exact == second.preference_paid.exact
    assert second.residual_share.exact == 0
    assert first.payout_per_share.exact == first.payout.exact / 2_000_000


def test_a_capped_class_is_marked_when_its_cap_stops_it() -> None:
    """$70M with A capped at 3x: A stops at $15M (marked capped); at $40M it stays under the cap (not marked); at $60M
    its $5M + 2/9 of $45M is exactly the $15M cap, so the cap takes nothing from it and it is not marked either."""
    stopped = waterfall("70000000", _A_CAPPED, WATERFALL_B)
    under = waterfall("40000000", _A_CAPPED, WATERFALL_B)
    at_cap = waterfall("60000000", _A_CAPPED, WATERFALL_B)

    assert [row.capped for row in stopped.rows] == [True, False]
    assert stopped.rows[_FIRST].residual_share.exact == 10_000_000
    assert stopped.common_per_share.exact * WATERFALL_COMMON == stopped.common_payout.exact == 45_000_000
    assert [row.capped for row in under.rows] == [False, False]
    assert at_cap.rows[_FIRST].payout.exact == 15_000_000
    assert [row.capped for row in at_cap.rows] == [False, False]
    assert {item.key for item in stopped.assumptions} >= {"participation", "cap_includes_preference"}


def test_a_cap_at_the_preference_pays_as_no_participation() -> None:
    """A cap equal to the preference leaves nothing to participate with: every payout matches participation none."""
    capped_at_preference = {**WATERFALL_A, "participation": "capped", "cap_multiple": "1"}
    for exit_amount in ("0", "3000000", "12000000", "40000000", "50000000", "300000000"):
        capped = waterfall(exit_amount, capped_at_preference, WATERFALL_B)
        plain = waterfall(exit_amount, WATERFALL_A, WATERFALL_B)
        assert [row.payout.exact for row in capped.rows] == [row.payout.exact for row in plain.rows], exit_amount
        assert capped.common_payout.exact == plain.common_payout.exact, exit_amount


def test_a_zero_preference_class_takes_nothing_staying_and_converts_once_the_rest_is_positive() -> None:
    """Owed nothing ahead of common (0x), a class with no participation takes 0 staying, so it converts at any exit
    that leaves a rest; at a $0 exit converting also gives 0, a tie, so it stays."""
    zero = {**WATERFALL_A, "preference_multiple": "0"}

    assert waterfall("30000000", zero, WATERFALL_B).rows[_FIRST].converts is True
    assert waterfall("0", zero, WATERFALL_B).rows[_FIRST].converts is False


def test_a_zero_exit_pays_nobody_and_no_class_converts() -> None:
    result = waterfall("0", WATERFALL_A, _A_CAPPED, WATERFALL_B)

    assert [row.payout.exact for row in result.rows] == [0, 0, 0]
    assert [row.converts for row in result.rows] == [False, False, False]
    assert (result.common_payout.exact, result.total.exact, result.passes) == (0, 0, _ONE_PASS)


def test_no_preferred_classes_leaves_the_whole_exit_to_the_common() -> None:
    """No classes: no rows, the common takes all of it, one pass that changes nothing; only the always-on rows."""
    result = waterfall("1234567.891", common_shares=3)

    assert result.rows == ()
    assert result.common_payout.exact == Decimal("1234567.891")
    assert result.common_payout.rounded == Decimal("1234567.89")
    assert result.passes == _ONE_PASS
    assert {item.key for item in result.assumptions} == {
        "exit_is_shared_amount",
        "preference_order",
        "conversion_one_to_one",
        "convert_when_strictly_better",
        "best_response_search",
    }


def test_the_search_stops_at_its_pass_limit_with_a_clean_error() -> None:
    """The $50M vector settles on pass 2; held to 1 pass it raises the named compute error (a ValueError)."""
    inputs = WaterfallInput.model_validate(
        {"exit_amount": "50000000", "common_shares": WATERFALL_COMMON, "classes": [WATERFALL_A, WATERFALL_B]}
    )

    assert default_pass_limit(inputs) == len(inputs.classes) + 1
    assert conversion_profile(inputs, default_pass_limit(inputs)) == ((True, False), 2)
    with pytest.raises(NoConversionEquilibrium, match="no stable choice") as caught:
        conversion_profile(inputs, _ONE_PASS)
    assert isinstance(caught.value, EquityComputeError)
    settings = {item.key: item.setting for item in waterfall("1", WATERFALL_A, WATERFALL_B).assumptions}
    assert settings["best_response_search"] == "from none converting, at most 3 passes"


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"participation": "capped"}, "participation capped needs cap_multiple"),
        ({"cap_multiple": "2"}, "cap_multiple goes with participation capped only"),
        ({"participation": "full", "cap_multiple": "2"}, "cap_multiple goes with participation capped only"),
        ({"participation": "capped", "cap_multiple": "0.5"}, "cap_multiple (0.5) is below preference_multiple (1)"),
        ({"participation": "capped", "cap_multiple": "0"}, "greater than 0"),
        ({"participation": "some"}, "Input should be 'none', 'full' or 'capped'"),
        ({"rank": 0}, "greater than or equal to 1"),
        ({"rank": MAX_CLASSES + 1}, "less than or equal to 12"),
        ({"rank": "1"}, "Input should be a valid integer"),
        ({"shares": 0}, "greater than 0"),
        ({"invested": "0"}, "greater than 0"),
        ({"preference_multiple": "-1"}, "greater than or equal to 0"),
        ({"colour": "red"}, "Extra inputs are not permitted"),
    ],
)
def test_a_class_that_does_not_fit_together_is_refused(fields: dict[str, object], message: str) -> None:
    """A cap goes with capped participation only and is at least the preference; ranks run 1 to 12."""
    with pytest.raises(ValidationError) as caught:
        PreferredClass.model_validate({**WATERFALL_A, **fields})

    assert message in str(caught.value)


@pytest.mark.parametrize(
    ("fields", "message"),
    [
        ({"classes": [WATERFALL_A] * (MAX_CLASSES + 1)}, "at most 12 items"),
        ({"common_shares": 0}, "greater than 0"),
        ({"exit_amount": "-1"}, "greater than or equal to 0"),
        ({"exit_amount": "1e16"}, "in size"),
        ({"classes": None}, "valid tuple"),
    ],
)
def test_an_exit_that_does_not_fit_together_is_refused(fields: dict[str, object], message: str) -> None:
    """At most 12 classes, at least one common share (so the rest always has an owner), and a bounded exit."""
    base = {"exit_amount": "50000000", "common_shares": WATERFALL_COMMON, "classes": [WATERFALL_A]}
    with pytest.raises(ValidationError) as caught:
        WaterfallInput.model_validate({**base, **fields})

    assert message in str(caught.value)


def test_twelve_classes_are_accepted() -> None:
    result = waterfall("90000000", *([WATERFALL_A] * MAX_CLASSES))

    assert len(result.rows) == MAX_CLASSES
    assert result.total.exact == 90_000_000
    assert result.rows[_SECOND].payout.exact == result.rows[_FIRST].payout.exact
