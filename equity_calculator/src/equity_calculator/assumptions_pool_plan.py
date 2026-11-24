"""The labelled assumptions a pool plan rests on: the pool's own rows reused word for word, the plan's own unverified.

No primary source says how big a pool a hiring plan needs; the plan's conventions (the pool holds exactly the grants
to the next round, a hire in the next round's month counts, every grant in one unit) are this calculator's, marked
unverified, like the pool rules they build on.
"""

from __future__ import annotations

from equity_calculator.assumptions import (
    POOL_TIMING_SOURCE,
    UNVERIFIED,
    money_split_assumption,
    price_basis_assumption,
    target_pool_assumption,
)
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_pool_plan import GrantUnit, PoolPlanInput


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


_GRANT_STATEMENTS: dict[GrantUnit, str] = {
    "shares": "Every grant is a share count; the plan's pool holds exactly their sum, G, after the round.",
    "percent": "Every grant is a percent of the fully diluted shares after this round, so the plan's pool is their "
    "sum; in each column a grant takes that percent of the column's own total shares.",
}


def pool_plan_assumptions(inputs: PoolPlanInput, unit: GrantUnit) -> tuple[EquityAssumption, ...]:
    """The pool plan's assumptions, with this run's next-round month and grant unit."""
    return (
        _assumption(
            "pool_timing",
            "pre_money",
            "Both columns create the new pool inside the pre-money valuation, as the usual term sheet does, so only "
            "the existing holders pay for it (the pool scenario also works the post-money timing).",
            POOL_TIMING_SOURCE,
        ),
        target_pool_assumption(),
        _assumption(
            "plan_pool",
            "U + P = the grants to the next round",
            "The plan's pool is the unissued pool after the round that holds exactly the grants of the hires "
            "counted; when those fit in today's unissued pool, the plan needs no top-up (P = 0) and today's pool is "
            "kept whole, never cut.",
            f"{UNVERIFIED} (this calculator's convention; no source sizes a pool from a hiring plan)",
        ),
        _assumption(
            "next_round_cutoff",
            f"month {inputs.next_round_month}",
            "A hire starting on or before the next round's month counts; one starting after it is left out of the "
            "plan, as the next round's own pool would cover it.",
            UNVERIFIED,
        ),
        _assumption("grant_unit", unit, _GRANT_STATEMENTS[unit], UNVERIFIED),
        price_basis_assumption(),
        _assumption(
            "share_rounding",
            "exact",
            "Share counts are exact fractions; a real cap table rounds to whole shares, which moves a figure by a "
            "share or a cent.",
            UNVERIFIED,
        ),
        _assumption(
            "difference",
            "requested - plan",
            "Each difference is the requested column less the plan's, worked exactly and rounded once; it is "
            "negative where the requested pool gives the lower figure. Neither column is a recommendation.",
            "display convention",
        ),
        money_split_assumption(),
    )
