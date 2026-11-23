"""Pydantic models of an exit waterfall: who gets what of a sale price (``equity_calculator waterfall``).

Each preferred class is owed its liquidation preference, ``preference_multiple`` × ``invested``. Preferences are
paid by seniority ``rank`` (1 is the most senior), and classes of equal rank share what is left pro rata to what they
are owed. The rest of the exit is shared per share among the common stock, the classes that converted to common
(one common share per preferred share) and the participating classes; a capped class's whole take, its preference
included, stops at ``cap_multiple`` × ``invested`` and the excess is shared among the others. Each class converts or
stays as its best response to the other classes' choices; a class converts only when that pays strictly more.

``equity_calculator.waterfall`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    MODEL_CONFIG,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    ShareCount,
)
from pydantic import BaseModel, Field, model_validator

__all__ = [
    "MAX_CLASSES",
    "Participation",
    "PreferredClass",
    "Rank",
    "WaterfallClassRow",
    "WaterfallInput",
    "WaterfallResult",
    "WaterfallScenario",
    "refuse_cap_mismatch",
]

WaterfallScenario = Literal["waterfall"]
# none: the preference only (or convert); full: the preference, then a per-share part of the rest with no limit;
# capped: the same, until the class's whole take reaches cap_multiple × invested.
Participation = Literal["none", "full", "capped"]

# The list cap: at most 12 preferred classes in one run; the worst case computes in under a second.
MAX_CLASSES = 12

# A seniority rank: 1 is paid first; equal ranks share pro rata. Gaps are allowed (ranks only order the classes).
Rank = Annotated[int, Field(strict=True, ge=1, le=MAX_CLASSES)]


class PreferredClass(BaseModel):
    """One preferred class: its shares, what it invested, its preference, seniority and participation."""

    model_config = MODEL_CONFIG

    shares: ShareCount = Field(gt=0)
    invested: BoundedDecimal = Field(gt=0)
    # 1x is the usual preference; 0 is a real setting (a class owed nothing ahead of common), never a stand-in.
    preference_multiple: BoundedDecimal = Field(default=Decimal(1), ge=0)
    # Every class at rank 1 is every class paid side by side (pari passu), the neutral order when none is given.
    rank: Rank = 1
    participation: Participation = "none"
    # Only for a capped class: its whole take, the preference included, as a multiple of what it invested.
    cap_multiple: BoundedDecimal | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def _cap_goes_with_capped(self) -> PreferredClass:
        """Refuse a capped class without a cap, a cap on any other class, or a cap below the preference."""
        refuse_cap_mismatch(self.participation, self.cap_multiple, self.preference_multiple)
        return self


def refuse_cap_mismatch(
    participation: Participation, cap_multiple: Decimal | None, preference_multiple: Decimal
) -> None:
    """Refuse a capped class without a cap, a cap on any other class, or a cap below the preference."""
    if participation == "capped" and cap_multiple is None:
        raise ValueError("participation capped needs cap_multiple: the whole take as a multiple of invested")
    if participation != "capped" and cap_multiple is not None:
        raise ValueError("cap_multiple goes with participation capped only")

    if cap_multiple is not None and cap_multiple < preference_multiple:
        raise ValueError(
            f"cap_multiple ({cap_multiple}) is below preference_multiple ({preference_multiple}): "
            "the cap includes the preference, so it is at least the preference"
        )


class WaterfallInput(BaseModel):
    """The exit amount, the common shares and the preferred classes, in the order they choose (none is allowed)."""

    model_config = MODEL_CONFIG

    scenario: WaterfallScenario = "waterfall"
    exit_amount: BoundedDecimal = Field(ge=0)
    # Every common share that takes part, exercised options included; above 0, so the rest always has an owner.
    common_shares: ShareCount = Field(gt=0)
    classes: tuple[PreferredClass, ...] = Field(max_length=MAX_CLASSES)


class WaterfallClassRow(BaseModel):
    """One class worked: what it is owed and paid, its part of the rest, its choice and both sides of that choice."""

    model_config = MODEL_CONFIG

    index: int
    preference_owed: EquityQuantity
    preference_paid: EquityQuantity
    # Its per-share part of what is left after the preferences: as common if it converted, else as a participant.
    residual_share: EquityQuantity
    converts: bool
    # True when a capped class's take stopped at its cap (always False for any other class).
    capped: bool
    payout: EquityQuantity
    payout_per_share: EquityQuantity
    # The class's payout if it stays and if it converts, the other classes' choices held as they are.
    payout_if_stays: EquityQuantity
    payout_if_converts: EquityQuantity


class WaterfallResult(BaseModel):
    """Every class's payout and choice, the common stock's payout, and the passes the search took."""

    model_config = MODEL_CONFIG

    scenario: WaterfallScenario = "waterfall"
    inputs: WaterfallInput
    rows: tuple[WaterfallClassRow, ...]
    preferences_paid: EquityQuantity
    residual: EquityQuantity
    common_payout: EquityQuantity
    # The per-share part of the rest every uncapped taker gets, after any cap has stopped a class.
    common_per_share: EquityQuantity
    total: EquityQuantity
    passes: int
    assumptions: tuple[EquityAssumption, ...]
