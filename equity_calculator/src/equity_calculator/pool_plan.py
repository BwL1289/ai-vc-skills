"""A pool sized from the founder's hiring plan to the next round, beside the pool a term sheet asks for.

With FD fully diluted shares before the round (the unissued pool U included), pre-money V and investment I, the pool
scenario's target t is the unissued pool after the round as a share of every post-round share, the new pool P created
in the pre-money: price p = V/(FD + P) and total T = (FD + P)(V + I)/V, so t = (U + P)·V/((FD + P)(V + I)).

The plan's pool holds exactly the grants G of the hires starting on or before the next round's month (U + P = G, so
P = G - U):

- grants in shares: t_plan = G·V/((V + I)(FD - U + G));
- grants as percents of the post-round fully diluted shares: t_plan is their sum.

Both columns are the pool scenario's own pre-money table (``pool.pool_in_pre_money``), at t_plan and at the requested
percent: no formula of the shuffle is worked a second way here. When the grants fit in today's pool (G <= U, or a sum
of percents at most U's share with no top-up), the shuffle's own clamp gives P = 0: no top-up, and today's pool is
kept whole. Every difference is the requested column less the plan's, exact, rounded once.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import get_args

from equity_calculator.assumptions_pool_plan import pool_plan_assumptions
from equity_calculator.exact import HUNDRED, ZERO, fraction, from_percent, quantity
from equity_calculator.pool import pool_in_pre_money
from equity_calculator.schemas.equity_common import EquityQuantity, ShareRounding
from equity_calculator.schemas.equity_pool import CapTableGroup, PoolCapTable
from equity_calculator.schemas.equity_pool_plan import (
    GrantUnit,
    PlannedHire,
    PoolPlanDifference,
    PoolPlanFlag,
    PoolPlanInput,
    PoolPlanResult,
    PoolPlanSide,
    hires_by_next_round,
)


@dataclass(frozen=True)
class _Terms:
    """The pool scenario's terms with an exact target in percent points (``pool.PoolTerms``), share counts exact."""

    fully_diluted_shares: int
    unissued_pool_shares: int
    pre_money: Decimal
    investment: Decimal
    target_pool_percent: Fraction
    share_rounding: ShareRounding = "exact"


def _ownership(table: PoolCapTable, group: CapTableGroup) -> Fraction:
    """``group``'s exact share of ``table``'s post-round shares."""
    return next(row.ownership.exact for row in table.rows if row.group == group)


def _grants(counted: tuple[PlannedHire, ...], unit: GrantUnit) -> Fraction:
    """The counted grants: their share count G, or the sum of their percents as a fraction of the post-round shares."""
    if unit == "percent":
        return sum((from_percent(hire.grant_percent) for hire in counted if hire.grant_percent is not None), ZERO)

    return Fraction(sum(hire.grant_shares for hire in counted if hire.grant_shares is not None))


def _plan_target(inputs: PoolPlanInput, counted: tuple[PlannedHire, ...], unit: GrantUnit) -> Fraction:
    """t_plan: the pool after the round, of every post-round share, that holds exactly the counted grants."""
    grants = _grants(counted, unit)
    if unit == "percent":
        return grants

    pre_money = fraction(inputs.pre_money)
    held = inputs.fully_diluted_shares - inputs.unissued_pool_shares
    return grants * pre_money / ((pre_money + fraction(inputs.investment)) * (held + grants))


def _side(
    inputs: PoolPlanInput, counted: tuple[PlannedHire, ...], unit: GrantUnit, target: Fraction
) -> tuple[PoolPlanSide, Fraction | None]:
    """One column at ``target``: the pool scenario's pre-money table, the grants it must hold and what is left; with
    the founders' exact ownership (``None`` without ``founder_shares``) for the difference."""
    table = pool_in_pre_money(
        _Terms(
            fully_diluted_shares=inputs.fully_diluted_shares,
            unissued_pool_shares=inputs.unissued_pool_shares,
            pre_money=inputs.pre_money,
            investment=inputs.investment,
            target_pool_percent=target * HUNDRED,
        )
    )
    total = table.total_shares.exact
    grants = _grants(counted, unit)
    grant_shares = grants * total if unit == "percent" else grants
    pool_after = inputs.unissued_pool_shares + table.new_pool_shares.exact
    founders = None if inputs.founder_shares is None else Fraction(inputs.founder_shares) / total

    side = PoolPlanSide(
        target_pool=quantity("fraction", target),
        grant_shares=quantity("shares", grant_shares),
        pool_left_at_next_round=quantity("shares", pool_after - grant_shares),
        founders_ownership=None if founders is None else quantity("fraction", founders),
        cap_table=table,
    )
    return side, founders


def _difference(
    plan: PoolPlanSide,
    requested: PoolPlanSide,
    founders: tuple[Fraction | None, Fraction | None],
) -> PoolPlanDifference:
    """The requested column less the plan's, each figure exact and rounded once."""
    plan_table, requested_table = plan.cap_table, requested.cap_table
    plan_founders, requested_founders = founders

    def minus(requested_value: EquityQuantity, plan_value: EquityQuantity) -> EquityQuantity:
        return quantity(requested_value.unit, requested_value.exact - plan_value.exact)

    return PoolPlanDifference(
        target_pool=minus(requested.target_pool, plan.target_pool),
        new_pool_shares=minus(requested_table.new_pool_shares, plan_table.new_pool_shares),
        price_per_share=minus(requested_table.price_per_share, plan_table.price_per_share),
        existing_holders_ownership=quantity(
            "fraction",
            _ownership(requested_table, "existing_holders") - _ownership(plan_table, "existing_holders"),
        ),
        option_pool_ownership=quantity(
            "fraction", _ownership(requested_table, "option_pool") - _ownership(plan_table, "option_pool")
        ),
        founders_ownership=(
            None
            if plan_founders is None or requested_founders is None
            else quantity("fraction", requested_founders - plan_founders)
        ),
        pool_left_at_next_round=minus(requested.pool_left_at_next_round, plan.pool_left_at_next_round),
        effective_pre_money=minus(requested_table.effective_pre_money, plan_table.effective_pre_money),
    )


def _flags(
    counted: tuple[PlannedHire, ...],
    left_out: tuple[PlannedHire, ...],
    plan: PoolPlanSide,
    requested: PoolPlanSide,
) -> tuple[PoolPlanFlag, ...]:
    """The flags that hold, in the order ``PoolPlanFlag`` lists them."""
    plan_target, requested_target = plan.target_pool.exact, requested.target_pool.exact
    holds: dict[PoolPlanFlag, bool] = {
        "no_hires_before_next_round": not counted,
        "hires_after_next_round_ignored": bool(left_out),
        "plan_fits_current_pool": plan.cap_table.pool_already_large_enough,
        "requested_met_by_current_pool": requested.cap_table.pool_already_large_enough,
        "requested_above_plan": requested_target > plan_target,
        "requested_below_plan": requested_target < plan_target,
    }
    return tuple(flag for flag in get_args(PoolPlanFlag) if holds[flag])


def compute_pool_plan(inputs: PoolPlanInput) -> PoolPlanResult:
    """The round at the plan's pool and at the requested one, side by side, exactly; never a pick."""
    counted, left_out = hires_by_next_round(inputs.hires, inputs.next_round_month)
    unit = inputs.hires[0].unit
    plan, plan_founders = _side(inputs, counted, unit, _plan_target(inputs, counted, unit))
    requested, requested_founders = _side(inputs, counted, unit, from_percent(inputs.requested_pool_percent))
    pre_money = fraction(inputs.pre_money)
    investment = fraction(inputs.investment)

    return PoolPlanResult(
        inputs=inputs,
        grant_unit=unit,
        hires_counted=len(counted),
        hires_left_out=len(left_out),
        investor_fraction=quantity("fraction", investment / (pre_money + investment)),
        plan=plan,
        requested=requested,
        requested_minus_plan=_difference(plan, requested, (plan_founders, requested_founders)),
        flags=_flags(counted, left_out, plan, requested),
        assumptions=pool_plan_assumptions(inputs, unit),
    )
