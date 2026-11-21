"""An exit waterfall: preferences by rank, then the rest per share, with each class's convert-or-stay best response.

For one choice of which classes convert (a profile), ``split_exit`` pays each rank in turn, most senior first: the
classes of that rank that stay are owed ``preference_multiple`` × ``invested`` each and share what is left pro rata
to what they are owed. The rest R is shared per share among the common stock, the converted classes and the
participating classes. A capped class whose preference plus part would pass ``cap_multiple`` × ``invested`` takes
exactly that much, and the rest is shared again among the others (water-filling: each round removes at least one
class, so at most k rounds).

``conversion_profile`` finds a profile no class wants to leave: start with nobody converting, visit the classes in
the order given, and let each convert exactly when converting pays it strictly more than staying, the others'
current choices held fixed; stop after a pass that changes nothing. The cost is bounded and stated: at most
``pass_limit`` passes (k + 1 from ``default_pass_limit``), each evaluating two waterfalls per class, each O(k²) —
O(k⁴) in all, so 12 classes compute in well under a second. A search that does not settle raises
``NoConversionEquilibrium``.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from fractions import Fraction

from equity_calculator.assumptions_waterfall import waterfall_assumptions
from equity_calculator.errors import NoConversionEquilibrium
from equity_calculator.exact import ZERO, fraction, money_split, quantity
from equity_calculator.schemas.equity_waterfall import (
    PreferredClass,
    WaterfallClassRow,
    WaterfallInput,
    WaterfallResult,
)

__all__ = [
    "Split",
    "compute_waterfall",
    "conversion_profile",
    "converting_pays_more",
    "default_pass_limit",
    "split_exit",
]

# Classes are numbered from 1, in the order given; passes are counted from 1.
_INDEX_START = 1
_FIRST_PASS = 1
# The default bound on the best-response search: one pass more than the number of classes.
_EXTRA_PASSES = 1
# money_split takes the classes' payouts then the common stock's, so the common's is the last part.
_COMMON_PART = -1


@dataclass(frozen=True)
class Split:
    """One profile's waterfall: each class's preference owed and paid, its part of the rest, and the common's part."""

    owed: tuple[Fraction, ...]
    paid: tuple[Fraction, ...]
    parts: tuple[Fraction, ...]
    capped: tuple[bool, ...]
    residual: Fraction
    price: Fraction
    common: Fraction

    def payout(self, index: int) -> Fraction:
        """What class ``index`` (0-based) takes in all: its preference paid plus its part of the rest."""
        return self.paid[index] + self.parts[index]


def _owed(item: PreferredClass) -> Fraction:
    """What a class that stays is owed ahead of common: ``preference_multiple`` × ``invested``."""
    return fraction(item.preference_multiple) * fraction(item.invested)


def _cap(item: PreferredClass) -> Fraction | None:
    """A capped class's whole take at most, ``cap_multiple`` × ``invested``; None for a class with no cap."""
    if item.cap_multiple is None:
        return None

    return fraction(item.cap_multiple) * fraction(item.invested)


def _preferences(classes: Sequence[PreferredClass], converts: Sequence[bool], exit_amount: Fraction) -> list[Fraction]:
    """Each class's preference paid: rank by rank, pro rata to what is owed within a rank, never past the exit."""
    remaining = exit_amount
    paid = [ZERO] * len(classes)
    for rank in sorted({item.rank for item in classes}):
        members = [index for index, item in enumerate(classes) if item.rank == rank and not converts[index]]
        owed_total = sum((_owed(classes[index]) for index in members), ZERO)
        if owed_total == ZERO:
            continue

        paid_total = min(owed_total, remaining)
        for index in members:
            paid[index] = paid_total * _owed(classes[index]) / owed_total
        remaining -= paid_total

    return paid


def split_exit(inputs: WaterfallInput, converts: Sequence[bool]) -> Split:
    """The waterfall for one profile (``converts[i]`` True when class i converts); payouts sum to the exit exactly."""
    classes = inputs.classes
    exit_amount = fraction(inputs.exit_amount)
    paid = _preferences(classes, converts, exit_amount)
    residual = exit_amount - sum(paid, ZERO)
    caps = [None if converts[index] else _cap(item) for index, item in enumerate(classes)]
    takers = {index for index, item in enumerate(classes) if converts[index] or item.participation != "none"}
    parts = [ZERO] * len(classes)
    capped = [False] * len(classes)
    left = residual
    while True:
        price = left / (inputs.common_shares + sum(classes[index].shares for index in takers))
        over = [
            (index, cap)
            for index in sorted(takers)
            if (cap := caps[index]) is not None and paid[index] + classes[index].shares * price > cap
        ]
        if not over:
            break

        for index, cap in over:
            parts[index] = cap - paid[index]
            capped[index] = True
            left -= parts[index]
            takers.discard(index)
    for index in takers:
        parts[index] = classes[index].shares * price

    return Split(
        owed=tuple(_owed(item) for item in classes),
        paid=tuple(paid),
        parts=tuple(parts),
        capped=tuple(capped),
        residual=residual,
        price=price,
        common=inputs.common_shares * price,
    )


def _flipped(converts: Sequence[bool], index: int, choice: bool) -> list[bool]:
    """The profile ``converts`` with class ``index``'s choice set to ``choice``."""
    profile = list(converts)
    profile[index] = choice

    return profile


def converting_pays_more(inputs: WaterfallInput, converts: Sequence[bool], index: int) -> bool:
    """True when class ``index`` takes strictly more converting than staying, the others' choices held fixed."""
    stays = split_exit(inputs, _flipped(converts, index, False)).payout(index)
    converted = split_exit(inputs, _flipped(converts, index, True)).payout(index)

    return converted > stays


def default_pass_limit(inputs: WaterfallInput) -> int:
    """The search's bound: one pass more than the number of classes."""
    return len(inputs.classes) + _EXTRA_PASSES


def conversion_profile(inputs: WaterfallInput, pass_limit: int) -> tuple[tuple[bool, ...], int]:
    """A profile no class wants to leave, and the passes the search took (at most ``pass_limit``).

    Raises ``NoConversionEquilibrium`` when a pass still changes a choice at the limit.
    """
    count = len(inputs.classes)
    converts = [False] * count
    for passes in range(_FIRST_PASS, pass_limit + 1):
        changed = False
        for index in range(count):
            choice = converting_pays_more(inputs, converts, index)
            if choice != converts[index]:
                converts[index] = choice
                changed = True
        if not changed:
            return tuple(converts), passes

    raise NoConversionEquilibrium(
        f"no stable choice of which preferred classes convert was found in {pass_limit} passes (the search starts "
        "with none converting and lets each class in turn convert when that pays it strictly more); these terms may "
        "have no such choice"
    )


def compute_waterfall(inputs: WaterfallInput) -> WaterfallResult:
    """Every class's payout and choice at the stable profile, both sides of each choice, and the common's payout."""
    limit = default_pass_limit(inputs)
    converts, passes = conversion_profile(inputs, limit)
    split = split_exit(inputs, converts)
    payouts = money_split([*(split.payout(index) for index in range(len(converts))), split.common])
    rows = []
    for index, item in enumerate(inputs.classes):
        stays = split_exit(inputs, _flipped(converts, index, False)).payout(index)
        converted = split_exit(inputs, _flipped(converts, index, True)).payout(index)
        rows.append(
            WaterfallClassRow(
                index=index + _INDEX_START,
                preference_owed=quantity("money", split.owed[index]),
                preference_paid=quantity("money", split.paid[index]),
                residual_share=quantity("money", split.parts[index]),
                converts=converts[index],
                capped=split.capped[index],
                payout=payouts[index],
                payout_per_share=quantity("price", split.payout(index) / item.shares),
                payout_if_stays=quantity("money", stays),
                payout_if_converts=quantity("money", converted),
            )
        )

    return WaterfallResult(
        inputs=inputs,
        rows=tuple(rows),
        preferences_paid=quantity("money", sum(split.paid, ZERO)),
        residual=quantity("money", split.residual),
        common_payout=payouts[_COMMON_PART],
        common_per_share=quantity("price", split.price),
        total=quantity("money", sum((payout.exact for payout in payouts), ZERO)),
        passes=passes,
        assumptions=waterfall_assumptions(inputs, limit),
    )
