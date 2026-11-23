"""The labelled assumptions of an exit waterfall, each with its source.

No source for liquidation-preference arithmetic was read for this calculator, so every row here is marked
unverified: they are the usual terms of a preferred class, stated so a reader can see each one and change the input
that sets it. The participation rows appear only when some class participates or is capped.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.schemas.equity_common import EquityAssumption

if TYPE_CHECKING:  # waterfall imports this module, so its protocol is read for type checks only
    from equity_calculator.waterfall import ExitTerms

__all__ = ["waterfall_assumptions"]

_STANDARD = f"{UNVERIFIED} (the usual preferred-stock terms; no source was read for them)"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def waterfall_assumptions(inputs: ExitTerms, pass_limit: int) -> tuple[EquityAssumption, ...]:
    """The waterfall's rows (``pass_limit`` the search's bound); participation and cap rows only when used."""
    participations = {item.participation for item in inputs.classes}
    rows = [
        _assumption(
            "exit_is_shared_amount",
            "nothing ahead of the shareholders",
            "The exit amount is what the shareholders share: no debt, fees, escrow, accrued dividends or option "
            "exercise cash is taken out first, and common_shares counts every common share that takes part "
            "(exercised options included; unexercised options take nothing).",
            _STANDARD,
        ),
        _assumption(
            "preference_order",
            "rank 1 first; pro rata within a rank",
            "Preferences are paid rank by rank, the most senior (rank 1) first; the classes of one rank share what "
            "is left pro rata to what each is owed (preference_multiple × invested). A class that converts gives "
            "up its preference.",
            _STANDARD,
        ),
        _assumption(
            "conversion_one_to_one",
            "1 common share per preferred share",
            "A class that converts takes the rest per share like common, one common share for each preferred share; "
            "no conversion-ratio change (anti-dilution) is applied.",
            _STANDARD,
        ),
        _assumption(
            "convert_when_strictly_better",
            "a tie stays",
            "Each class converts exactly when that pays it strictly more than staying, the other classes' choices "
            "held fixed; a class that would take the same either way stays and keeps its preference.",
            _STANDARD,
        ),
        _assumption(
            "best_response_search",
            f"from none converting, at most {pass_limit} passes",
            "The search starts with no class converting and visits the classes in the order given, each choosing "
            "its better side; it stops after a pass that changes nothing, which is a choice no class wants to "
            "leave. When terms allow more than one such choice, this is the one the search reaches first.",
            _STANDARD,
        ),
    ]
    if participations & {"full", "capped"}:
        rows.append(
            _assumption(
                "participation",
                "preference, then a per-share part of the rest",
                "A participating class that stays takes its preference and then its per-share part of the rest "
                "beside the common stock (full: with no limit).",
                _STANDARD,
            )
        )
    if "capped" in participations:
        rows.append(
            _assumption(
                "cap_includes_preference",
                "cap_multiple × invested, preference included",
                "A capped class's whole take, its preference included, stops at cap_multiple × invested; what it "
                "would have taken past that is shared among the other takers, and it can still convert instead.",
                _STANDARD,
            )
        )

    return tuple(rows)
