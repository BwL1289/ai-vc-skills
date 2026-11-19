"""A grant vesting month by month, with termination and single- or double-trigger acceleration, every step exact.

On schedule: nothing before the cliff, then G·min(s, T)/T at month m, where s = min(m, e) is the months served (e the
termination month, if any). Acceleration vests part of what is still unvested at the month it fires: the change of
control c for ``single_trigger`` (when the holder was not terminated before it), the termination e for
``double_trigger`` (only when e is at or after c). With a strike, the exercise cost is vested × strike; with a common
price too, the intrinsic value is vested × max(0, common - strike).
"""

from __future__ import annotations

import math
from fractions import Fraction

from equity_calculator.assumptions_holder import vesting_assumptions
from equity_calculator.exact import ZERO, fraction, from_percent, quantity
from equity_calculator.schemas.equity_vesting import Moneyness, VestingInput, VestingResult

__all__ = ["compute_vesting"]


def _on_schedule(inputs: VestingInput, month: int) -> Fraction:
    """Shares vested on schedule by ``month``: 0 before the cliff, G·min(s, T)/T after, s the months served."""
    served = month if inputs.termination_month is None else min(month, inputs.termination_month)
    if served < inputs.cliff_months:
        return ZERO

    return fraction(inputs.grant_shares) * min(served, inputs.total_months) / inputs.total_months


def _fired_month(inputs: VestingInput) -> int | None:
    """The month acceleration fires by the month asked about, or None when it has not (or never will)."""
    change = inputs.change_of_control_month
    termination = inputs.termination_month
    if change is None:
        return None

    if inputs.acceleration == "single_trigger":
        terminated_before = termination is not None and termination < change
        return change if inputs.month >= change and not terminated_before else None

    if inputs.acceleration == "double_trigger" and termination is not None and termination >= change:
        return termination if inputs.month >= termination else None

    return None


def _accelerated(inputs: VestingInput, fired: int) -> Fraction:
    """Shares acceleration adds at month ``fired``: a percent of the unvested shares, or of the grant.

    Uncapped here: ``compute_vesting`` caps the vested total at the grant, which also caps a grant-based percent at
    the shares still unvested.
    """
    grant = fraction(inputs.grant_shares)
    # The validator makes the percent present whenever acceleration is not "none"; 0 is never a stand-in here.
    percent = ZERO if inputs.acceleration_percent is None else from_percent(inputs.acceleration_percent)
    if inputs.acceleration_base == "grant":
        return percent * grant

    return percent * (grant - _on_schedule(inputs, fired))


def _moneyness(common: Fraction, strike: Fraction) -> Moneyness:
    if common > strike:
        return "in_the_money"
    if common == strike:
        return "at_the_money"

    return "underwater"


def compute_vesting(inputs: VestingInput) -> VestingResult:
    """The grant at the month asked about: vested on schedule, accelerated, in all, unvested, and the money lines."""
    grant = fraction(inputs.grant_shares)
    base = _on_schedule(inputs, inputs.month)
    fired = _fired_month(inputs)
    vested = base if fired is None else min(grant, base + _accelerated(inputs, fired))
    if inputs.share_rounding == "whole_shares":
        base = Fraction(math.floor(base))
        vested = Fraction(math.floor(vested))

    exercise_cost = spread = intrinsic = None
    moneyness: Moneyness | None = None
    if inputs.strike_price is not None:
        strike = fraction(inputs.strike_price)
        exercise_cost = quantity("money", vested * strike)
        if inputs.common_price is not None:
            common = fraction(inputs.common_price)
            gap = max(ZERO, common - strike)
            spread = quantity("price", gap)
            intrinsic = quantity("money", vested * gap)
            moneyness = _moneyness(common, strike)

    return VestingResult(
        inputs=inputs,
        grant=quantity("shares", grant),
        base_vested=quantity("shares", base),
        accelerated=quantity("shares", vested - base),
        vested=quantity("shares", vested),
        unvested=quantity("shares", grant - vested),
        vested_fraction=quantity("fraction", vested / grant),
        stopped_month=inputs.termination_month,
        acceleration_fired=fired is not None,
        fired_month=fired,
        exercise_cost=exercise_cost,
        spread=spread,
        intrinsic_value=intrinsic,
        moneyness=moneyness,
        assumptions=vesting_assumptions(inputs),
    )
