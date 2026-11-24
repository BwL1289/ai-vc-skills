"""A raise pipeline's flags turned into its model's fields, and where each runway field's failures came from.

``--cash-on-hand``, ``--cash-floor``, each ``--phase`` and ``--months-to-raise`` are gathered into ``runway`` (none of
them given: no runway); every other flag fills its field directly. The places map a model location
(``("runway", "phases")``) to the flag it came from, so a refusal names the flag the user typed, as every other
scenario's does.
"""

from __future__ import annotations

from typing import Any

from equity_calculator.cli_runway_plan import Places

__all__ = ["raise_pipeline_fields"]

_RUNWAY = "runway"
# Each runway field and the flag (and argparse name) it comes from.
_RUNWAY_FLAGS = {
    "cash_on_hand": ("cash_on_hand", "--cash-on-hand"),
    "cash_floor": ("cash_floor", "--cash-floor"),
    "phases": ("runway_phases", "--phase"),
    "months_to_raise": ("months_to_raise", "--months-to-raise"),
}
_FLAG_JOIN = "/"


def raise_pipeline_fields(given: dict[str, Any]) -> tuple[dict[str, object], Places]:
    """The ``RaisePipelineInput`` fields the flags in ``given`` (argparse's names, ``None`` dropped) describe, and the
    flag each runway field came from."""
    names = {name for name, _ in _RUNWAY_FLAGS.values()}
    fields: dict[str, object] = {name: value for name, value in given.items() if name not in names}
    runway = {field: given[name] for field, (name, _) in _RUNWAY_FLAGS.items() if name in given}
    places: Places = {(_RUNWAY,): _FLAG_JOIN.join(flag for _, flag in _RUNWAY_FLAGS.values())}
    places.update({(_RUNWAY, field): flag for field, (_, flag) in _RUNWAY_FLAGS.items()})
    if runway:
        fields[_RUNWAY] = runway

    return fields, places
