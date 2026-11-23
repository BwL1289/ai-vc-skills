"""A runway plan's flags turned into its model's fields, and where each field's failures came from on the command line.

The plan's ``--phase`` items, a downside's or a lean case's ``--downside-phase`` / ``--lean-phase`` items or percents,
and each ``--raise-use-of-funds`` line (numbered by its ``--raise``) are gathered into ``cases`` and ``raises``. The
places map a model location (``("cases", 1, "phases")``) to the flag it came from, so a refusal names the flag the
user typed, as every other scenario's does.
"""

from __future__ import annotations

from typing import Any

__all__ = ["Places", "runway_plan_fields"]

# A model location prefix and the flag (or a repeated flag's item) it came from.
Places = dict[tuple[int | str, ...], str]

_DIRECT = (
    "cash_on_hand",
    "cash_floor",
    "milestones",
    "months_to_raise",
    "stated_runway_months",
    "tolerance_points",
    "tolerance_percent",
    "runway_band_months",
)
_OTHER_CASES = ("downside", "lean")
_FLAG_JOIN = "/"


def _other_case(given: dict[str, Any], name: str) -> dict[str, object] | None:
    """A downside or lean case from its flags, or ``None`` when none of them was given."""
    fields = {
        "phases": given.get(f"{name}_phases"),
        "revenue_percent_of_plan": given.get(f"{name}_revenue_percent"),
        "gross_burn_percent_of_plan": given.get(f"{name}_gross_burn_percent"),
    }
    if all(value is None for value in fields.values()):
        return None

    return {"name": name, **{key: value for key, value in fields.items() if value is not None}}


def _cases(given: dict[str, Any], places: Places) -> list[dict[str, object]]:
    """The plan from ``--phase``, then a downside and a lean case when their flags are given."""
    cases: list[dict[str, object]] = [{"name": "plan", "phases": given.get("phases", [])}]
    places[("cases",)] = places[("cases", 0)] = places[("cases", 0, "phases")] = "--phase"
    for name in _OTHER_CASES:
        case = _other_case(given, name)
        if case is None:
            continue
        index = len(cases)
        flags = (f"--{name}-phase", f"--{name}-revenue-percent", f"--{name}-gross-burn-percent")
        places[("cases", index)] = _FLAG_JOIN.join(flags)
        places[("cases", index, "phases")] = flags[0]
        places[("cases", index, "revenue_percent_of_plan")] = flags[1]
        places[("cases", index, "gross_burn_percent_of_plan")] = flags[2]
        cases.append(case)

    return cases


def _raises(given: dict[str, Any], places: Places) -> list[dict[str, Any]]:
    """Each ``--raise``, with the ``--raise-use-of-funds`` lines that name it, in the order given."""
    raises: list[dict[str, Any]] = [dict(item) for item in given.get("raises", [])]
    for number, line in enumerate(given.get("raise_use_of_funds", []), start=1):
        option = line["option"]
        if option > len(raises):
            raise SystemExit(f"--raise-use-of-funds #{number}: there is no --raise #{option} (there are {len(raises)})")
        lines = raises[option - 1].setdefault("use_of_funds", [])
        places[("raises", option - 1, "use_of_funds", len(lines))] = f"--raise-use-of-funds #{number}"
        lines.append({key: value for key, value in line.items() if key != "option"})

    return raises


def runway_plan_fields(given: dict[str, Any]) -> tuple[dict[str, object], Places]:
    """The ``RunwayPlanInput`` fields the flags in ``given`` (argparse's names, ``None`` dropped) describe, and the
    flag each case, phase and use-of-funds line came from.

    Raises ``SystemExit`` when a ``--raise-use-of-funds`` line names a raise that was not given.
    """
    places: Places = {}
    fields: dict[str, object] = {name: given[name] for name in _DIRECT if name in given}
    fields["cases"] = _cases(given, places)
    raises = _raises(given, places)
    if raises:
        fields["raises"] = raises

    return fields, places
