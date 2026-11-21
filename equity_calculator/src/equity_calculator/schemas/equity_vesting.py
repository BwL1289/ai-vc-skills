"""Pydantic models of an option or stock grant vesting month by month (``equity_calculator vesting``).

A grant of G shares vests over T months: nothing before the cliff, then G·m/T at month m (the cliff months vest at
once), all of it at month T. A termination stops vesting. Acceleration vests part of what is still unvested at once:
``single_trigger`` at the change of control (the deal alone), ``double_trigger`` only when the holder is also
terminated at or after the deal. With a strike and a common price, the vested shares' exercise cost and their
value above the strike follow. ``equity_calculator.vesting`` works it; each convention and its source are in
``README.md``.
"""

from __future__ import annotations

from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    ShareCount,
    ShareRounding,
)
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "MAX_VESTING_MONTHS",
    "Acceleration",
    "AccelerationBase",
    "Moneyness",
    "VestingInput",
    "VestingResult",
    "VestingScenario",
]

VestingScenario = Literal["vesting"]

# ``none``: no acceleration. ``single_trigger``: part of the unvested shares vests at the change of control.
# ``double_trigger``: the same, only when the holder is also terminated at or after the change of control.
Acceleration = Literal["none", "single_trigger", "double_trigger"]

# What the acceleration percent is a percent of: ``unvested`` (the shares still unvested when it fires, the
# default) or ``grant`` (the whole grant, capped at what is still unvested).
AccelerationBase = Literal["unvested", "grant"]

# Where the common price sits against the strike: above (``in_the_money``), equal, or below (``underwater``).
Moneyness = Literal["in_the_money", "at_the_money", "underwater"]

# The list cap: a schedule and every month in it run at most 600 months (50 years).
MAX_VESTING_MONTHS = 600

# The usual grant: 4 years with a 1-year cliff (Sam Altman, "Employee Equity"). Real defaults, never "missing".
_DEFAULT_TOTAL_MONTHS = 48
_DEFAULT_CLIFF_MONTHS = 12

Month = Annotated[int, Field(strict=True, ge=0, le=MAX_VESTING_MONTHS)]
ScheduleLength = Annotated[int, Field(strict=True, ge=1, le=MAX_VESTING_MONTHS)]


class VestingInput(BaseModel):
    """One grant: its shares, schedule and cliff, the month asked about, prices, termination and acceleration."""

    model_config = MODEL_CONFIG

    scenario: VestingScenario = "vesting"
    grant_shares: ShareCount = Field(gt=0)
    total_months: ScheduleLength = _DEFAULT_TOTAL_MONTHS
    cliff_months: Month = _DEFAULT_CLIFF_MONTHS
    month: Month
    strike_price: BoundedDecimal | None = Field(default=None, ge=0)
    common_price: BoundedDecimal | None = Field(default=None, ge=0)
    termination_month: Month | None = None
    acceleration: Acceleration = "none"
    acceleration_percent: BoundedDecimal | None = Field(default=None, gt=0, le=WHOLE_PERCENT)
    acceleration_base: AccelerationBase = "unvested"
    change_of_control_month: Month | None = None
    share_rounding: ShareRounding = "exact"

    @model_validator(mode="after")
    def _schedule_prices_and_trigger(self) -> VestingInput:
        """Refuse a cliff past the schedule, a common price with no strike, or acceleration terms that do not fit."""
        if self.cliff_months > self.total_months:
            raise ValueError("cliff_months must be at most total_months")
        if self.common_price is not None and self.strike_price is None:
            raise ValueError("give strike_price with common_price (the value is the vested shares above the strike)")

        accelerated = self.acceleration != "none"
        terms_given = self.acceleration_percent is not None or self.change_of_control_month is not None
        if not accelerated and terms_given:
            raise ValueError(
                "acceleration_percent and change_of_control_month go with acceleration single_trigger or double_trigger"
            )
        if accelerated and (self.acceleration_percent is None or self.change_of_control_month is None):
            raise ValueError(f"acceleration {self.acceleration} needs acceleration_percent and change_of_control_month")

        return self


class VestingResult(BaseModel):
    """The grant at the month asked about: shares vested on schedule, accelerated, in all, unvested, and money."""

    model_config = MODEL_CONFIG

    scenario: VestingScenario = "vesting"
    inputs: VestingInput
    grant: EquityQuantity
    base_vested: EquityQuantity
    accelerated: EquityQuantity
    vested: EquityQuantity
    unvested: EquityQuantity
    vested_fraction: EquityQuantity
    # The month vesting stopped (the termination), and whether and when acceleration fired by the month asked about.
    stopped_month: int | None = None
    acceleration_fired: bool
    fired_month: int | None = None
    # Only with a strike price: the cost to exercise the vested shares; with a common price too, their value.
    exercise_cost: EquityQuantity | None = None
    spread: EquityQuantity | None = None
    intrinsic_value: EquityQuantity | None = None
    moneyness: Moneyness | None = None
    assumptions: tuple[EquityAssumption, ...]
