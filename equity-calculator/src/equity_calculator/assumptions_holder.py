"""The labelled assumptions of one holder's stake: dilution through rounds and a grant vesting, each with its source.

Dilution rests on PG's "(100 - n)% you have left" plus standard priced-round arithmetic for the pool; vesting on
Altman's standard schedule. Acceleration, termination and option-value conventions have no primary source here,
so they are marked unverified; each one a reader could want another way is a setting the inputs can change.
"""

from __future__ import annotations

from equity_calculator.assumptions import ALTMAN_SOURCE, PG_SOURCE, UNVERIFIED
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_dilution import DilutionInput
from equity_calculator.schemas.equity_vesting import VestingInput

__all__ = ["dilution_assumptions", "vesting_assumptions"]

_ALTMAN_SCHEDULE_QUOTE = '"The standard at startups is 4 years with a 1-year cliff"'


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def dilution_assumptions(inputs: DilutionInput) -> tuple[EquityAssumption, ...]:
    """The dilution rows; the amounts row appears only when a round is given as amounts."""
    rows = [
        _assumption(
            "dilution_rule",
            "h_k = h_(k-1)·(1 - n - p)",
            "A holder who buys nothing in a round keeps 1 - n - p of their stake: n is the new investors' share of "
            "the company after the round, p the new pool's; every earlier holder is diluted by the same factor.",
            f'{PG_SOURCE}: "the (100 - n)% you have left" (the pool term p: {UNVERIFIED}, standard priced-round '
            "arithmetic)",
        ),
        _assumption(
            "pool_basis",
            "new pool's share after the round",
            "pool_percent is only the pool created in the round, as a share of the company after it; a pool "
            "carried over is already in the holder's stake, and a top-up to a target is the pool scenario.",
            UNVERIFIED,
        ),
        _assumption(
            "no_participation",
            "the holder buys nothing",
            "The holder takes up no pro-rata right in any round, and no SAFE or note converts (that is the round "
            "scenario).",
            "scope of this scenario",
        ),
    ]
    if any(item.pre_money is not None for item in inputs.rounds):
        rows.append(
            _assumption(
                "stake_from_amounts",
                "n = I/(V + I)",
                "A round given as amounts sells the investment over its post-money valuation V + I; the holder's "
                "value after it is their stake times V + I.",
                f"{UNVERIFIED} (standard priced-round arithmetic; neither source states it)",
            )
        )

    return tuple(rows)


def _acceleration_rows(inputs: VestingInput) -> list[EquityAssumption]:
    """The rows of a grant with acceleration: what the percent applies to, what it shortens, the double window."""
    rows = [
        _assumption(
            "acceleration_base",
            inputs.acceleration_base,
            "unvested: the percent is of the shares still unvested when acceleration fires. grant: it is of the "
            "whole grant, capped at what is still unvested.",
            UNVERIFIED,
        ),
        _assumption(
            "acceleration_order",
            "off the end of the schedule",
            "Accelerated shares are the last ones the schedule would have vested: monthly vesting goes on at the same "
            "rate afterwards, so the grant is fully vested earlier.",
            UNVERIFIED,
        ),
    ]
    if inputs.acceleration == "double_trigger":
        rows.append(
            _assumption(
                "double_trigger_window",
                "any termination at or after the change of control",
                "The double trigger fires at the termination month when it is at or after the change of control; a "
                "window that ends the protection some months after the deal is not modelled.",
                UNVERIFIED,
            )
        )

    return rows


def vesting_assumptions(inputs: VestingInput) -> tuple[EquityAssumption, ...]:
    """The vesting rows; the acceleration rows appear only with acceleration, the value row only with a strike.

    The value row also says how the exercise cost is worked, which a strike alone gives, so it does not wait for a
    common price.
    """
    rows = [
        _assumption(
            "schedule",
            f"{inputs.total_months} months, {inputs.cliff_months}-month cliff, monthly after",
            "Nothing vests before the cliff; at the cliff the months served vest at once; then 1/T of the grant a "
            "month until all of it has vested at month T.",
            f"{ALTMAN_SOURCE}: {_ALTMAN_SCHEDULE_QUOTE} (monthly vesting after the cliff: {UNVERIFIED})",
        ),
        _assumption(
            "termination",
            "vesting stops; the unvested shares are forfeited",
            "A termination at month e stops the schedule at e; nothing vests after it except what acceleration "
            "adds when it fires.",
            UNVERIFIED,
        ),
        _assumption(
            "share_rounding",
            inputs.share_rounding,
            "exact keeps fractional shares; whole_shares rounds the vested count down to a whole share (the "
            "schedule and the acceleration together, then the accelerated part is what that adds).",
            UNVERIFIED,
        ),
    ]
    if inputs.acceleration != "none":
        rows += _acceleration_rows(inputs)
    if inputs.strike_price is not None:
        rows.append(
            _assumption(
                "intrinsic_value",
                "vested × max(0, common - strike)",
                "The exercise cost is the vested shares times the strike; their value is what the common price adds "
                "above the strike, never below 0. No tax and no time value.",
                f"{UNVERIFIED} (an option's intrinsic value)",
            )
        )

    return tuple(rows)
