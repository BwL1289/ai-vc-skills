"""A grant's vesting report lines (the ``Vesting`` sheet): the schedule, the shares vested and unvested, the money.

One value column. The inputs come first (months shown as text, such as ``48 months``); then the shares vested on
schedule and by acceleration with their live total, the unvested shares, and the grant as the live total of vested
and unvested; then the exercise cost, the spread and the intrinsic value when a strike and a common price are given,
with the moneyness as a coloured verdict.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_vesting import VestingInput, VestingResult
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Vesting"
_HEADING = "A grant vesting month by month: the cliff, termination and acceleration at the month asked about"
_COLUMNS = ("This grant",)
_ACCELERATION_NAMES = {"none": "none", "single_trigger": "single trigger", "double_trigger": "double trigger"}
_BASE_NAMES = {"unvested": "percent of the unvested shares", "grant": "percent of the grant, capped at the unvested"}


def _months(count: int) -> str:
    return f"{count} month" if count == 1 else f"{count} months"


def _input_lines(inputs: VestingInput) -> list[Line]:
    """The grant, schedule, month asked about, termination and acceleration terms, as given."""
    lines = [
        Line("grant_shares", "Grant (G)", (given("shares", Decimal(inputs.grant_shares)),), GIVEN),
        Line("total_months", "Schedule (T)", (_months(inputs.total_months),), GIVEN),
        Line("cliff_months", "Cliff", (_months(inputs.cliff_months),), GIVEN),
        Line("month", "Month asked about (m)", (_months(inputs.month),), GIVEN),
    ]
    if inputs.termination_month is not None:
        lines.append(Line("termination_month", "Terminated at (e)", (_months(inputs.termination_month),), GIVEN))
    lines.append(Line("acceleration", "Acceleration", (_ACCELERATION_NAMES[inputs.acceleration],), GIVEN))
    if inputs.acceleration_percent is not None and inputs.change_of_control_month is not None:
        lines += [
            Line(
                "acceleration_percent",
                "Acceleration percent",
                (given_percent(inputs.acceleration_percent),),
                _BASE_NAMES[inputs.acceleration_base],
            ),
            Line(
                "change_of_control_month", "Change of control at (c)", (_months(inputs.change_of_control_month),), GIVEN
            ),
        ]

    return lines


def _money_lines(result: VestingResult) -> list[Line]:
    """Strike, exercise cost, common price, spread, intrinsic value and moneyness, as far as prices are given."""
    inputs = result.inputs
    if inputs.strike_price is None or result.exercise_cost is None:
        return []

    lines = [
        Line("strike_price", "Strike price", (given("price", inputs.strike_price),), GIVEN),
        Line("exercise_cost", "Cost to exercise the vested shares", (result.exercise_cost,), "vested·strike"),
    ]
    if (
        inputs.common_price is not None
        and result.spread is not None
        and result.intrinsic_value is not None
        and result.moneyness is not None
    ):
        lines += [
            Line("common_price", "Common price", (given("price", inputs.common_price),), GIVEN),
            Line("spread", "Spread per share", (result.spread,), "max(0, common - strike)"),
            Line("intrinsic_value", "Intrinsic value of the vested shares", (result.intrinsic_value,), "vested·spread"),
            Line("moneyness", "Common against the strike", (result.moneyness,), "above, equal or below", verdict=True),
        ]

    return lines


def vesting_sheet(result: VestingResult) -> Sheet:
    """The vesting lines: inputs, vested on schedule and by acceleration, unvested, the grant, then the money."""
    fired_how = "never" if result.fired_month is None else f"at {_months(result.fired_month)}"
    lines = _input_lines(result.inputs)
    lines += [
        Line("base_vested", "Vested on schedule", (result.base_vested,), "0 before the cliff, else G·min(s, T)/T"),
        Line("accelerated", "Vested by acceleration", (result.accelerated,), "a percent of the unvested when it fired"),
        Line("vested", "Vested in all", (result.vested,), "on schedule + accelerated", ("base_vested", "accelerated")),
        Line("unvested", "Unvested", (result.unvested,), "G - vested"),
        Line("grant", "Grant", (result.grant,), "vested + unvested", ("vested", "unvested")),
        Line("vested_fraction", "Share of the grant vested", (result.vested_fraction,), "vested / G"),
        Line("acceleration_fired", "Acceleration fired", (yes_no(result.acceleration_fired),), fired_how),
    ]
    lines += _money_lines(result)

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
