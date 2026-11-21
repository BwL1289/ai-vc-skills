"""An exit waterfall's report lines (the ``Waterfall`` sheet): each class's terms, choice and payout, then common.

One value column. The exit and the common shares come first; then a block per preferred class (its terms as given,
the preference it is owed, its payout if it stays and if it converts with the other classes' choices held, its choice
as a coloured verdict, the preference it was paid, its part of the rest, its payout and payout per share); then the
preferences paid in all, the rest after them, the per-share part of the rest, the common stock's payout, the total
paid out as a live sum of every payout (the cents split by largest remainder, so they add up to the exit), and the
passes the search took.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_waterfall import PreferredClass, WaterfallClassRow, WaterfallResult
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, yes_no

_TITLE = "Waterfall"
_HEADING = "Who gets what of an exit: preferences by rank, then the rest per share, each class converting or staying"
_COLUMNS = ("This exit",)
CONVERTS = "converts"
STAYS = "stays"
_COMMON_PAYOUT_KEY = "common_payout"


def _participation_text(item: PreferredClass) -> str:
    """The class's participation in words: none, full, or capped at its multiple of what it invested."""
    match item.participation:
        case "none":
            return "no participation"
        case "full":
            return "full participation"
        case "capped":
            return f"participates up to {item.cap_multiple}x invested in all"


def _plural(count: int, word: str) -> str:
    return f"{count} {word}" if count == 1 else f"{count} {word}es"


def _payout_key(row: WaterfallClassRow) -> str:
    return f"class_{row.index}_payout"


def _class_lines(item: PreferredClass, row: WaterfallClassRow) -> list[Line]:
    """One class's block: terms, what it is owed, both sides of its choice, the choice, what it takes."""
    name = f"Class {row.index}"
    key = f"class_{row.index}"
    lines = [
        Line(f"{key}_shares", f"{name}: shares", (given("shares", Decimal(item.shares)),), GIVEN),
        Line(f"{key}_invested", f"{name}: invested", (given("money", item.invested),), GIVEN),
        Line(
            f"{key}_multiple", f"{name}: preference multiple", (given("multiplier", item.preference_multiple),), GIVEN
        ),
        Line(
            f"{key}_terms",
            f"{name}: seniority, participation",
            (f"rank {item.rank}, {_participation_text(item)}",),
            GIVEN,
        ),
        Line(f"{key}_owed", f"{name}: preference owed", (row.preference_owed,), "multiple × invested"),
        Line(f"{key}_if_stays", f"{name}: payout if it stays", (row.payout_if_stays,), "the others' choices held"),
        Line(
            f"{key}_if_converts",
            f"{name}: payout if it converts",
            (row.payout_if_converts,),
            "the others' choices held",
        ),
        Line(
            f"{key}_choice",
            f"{name}: choice",
            (CONVERTS if row.converts else STAYS,),
            "converts only when that pays strictly more",
            verdict=True,
        ),
        Line(f"{key}_paid", f"{name}: preference paid", (row.preference_paid,), "rank by rank, pro rata in a rank"),
        Line(f"{key}_part", f"{name}: part of the rest", (row.residual_share,), "shares × per-share part, to any cap"),
    ]
    if item.participation == "capped":
        lines.append(Line(f"{key}_capped", f"{name}: stopped at its cap", (yes_no(row.capped),), "cap × invested"))
    lines += [
        Line(_payout_key(row), f"{name}: payout", (row.payout,), "preference paid + part of the rest"),
        Line(f"{key}_per_share", f"{name}: payout per share", (row.payout_per_share,), "payout / shares"),
    ]

    return lines


def waterfall_sheet(result: WaterfallResult) -> Sheet:
    """The waterfall lines: the exit and common shares, every class's block, the common's payout, the live total."""
    inputs = result.inputs
    lines = [
        Line("exit_amount", "Exit amount (E)", (given("money", inputs.exit_amount),), GIVEN),
        Line("common_shares", "Common shares", (given("shares", Decimal(inputs.common_shares)),), GIVEN),
    ]
    for item, row in zip(inputs.classes, result.rows, strict=True):
        lines += _class_lines(item, row)
    payout_keys = tuple(_payout_key(row) for row in result.rows)

    lines += [
        Line("preferences_paid", "Preferences paid in all", (result.preferences_paid,), "sum of preferences paid"),
        Line("residual", "Rest after preferences (R)", (result.residual,), "E - preferences paid"),
        Line(
            "common_per_share",
            "Per-share part of the rest",
            (result.common_per_share,),
            "what caps leave of R / the shares taking part",
        ),
        Line(_COMMON_PAYOUT_KEY, "Common stock's payout", (result.common_payout,), "common shares × per-share part"),
        Line(
            "total",
            "Total paid out",
            (result.total,),
            "every payout, cents by largest remainder (= E)",
            (*payout_keys, _COMMON_PAYOUT_KEY),
        ),
        Line("passes", "Search passes", (_plural(result.passes, "pass"),), "until a pass changes no choice"),
    ]

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
