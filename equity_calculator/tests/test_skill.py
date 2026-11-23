"""The agent skill stays true to the calculator: its frontmatter, its field table, its JSON example and its commands.

The field table must name every input field of every scenario (nested instruments, rounds and classes included) and
nothing that is not a field or an allowed value; the JSON example must be a valid ``equity_investor`` call; and each
``equity_calculator`` command in it must run and print a report.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Any

import pytest
from equity_calculator.__main__ import _INPUT_MODELS, run

# The skill sits in the repository root's skills/ folder, where the Claude Code plugin finds it.
_SKILL = Path(__file__).resolve().parents[2] / "skills" / "equity-calculator" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_FENCE = re.compile(r"^```([a-z]*)\n(.*?)^```$", re.MULTILINE | re.DOTALL)
# The field table's header row, however its cells are padded (a Markdown formatter may align the columns).
_TABLE_HEAD = re.compile(r"^\|\s*Scenario\s*\|\s*Fields \(required in bold\)\s*\|$", re.MULTILINE)
_NAME = re.compile(r'[`"]([a-z_]+)[`"]')
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024


def _schema_names(schema: dict[str, Any]) -> tuple[set[str], set[str]]:
    """Every property name and every allowed string value in ``schema`` and its definitions."""
    fields: set[str] = set()
    values: set[str] = set()

    def walk(node: object) -> None:
        if isinstance(node, dict):
            fields.update(node.get("properties", {}))
            values.update(str(value) for value in node.get("enum", []))
            if isinstance(node.get("const"), str):
                values.add(node["const"])
            for child in node.values():
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(schema)
    return fields, values


def _table_rows() -> dict[str, str]:
    head = _TABLE_HEAD.search(_TEXT)
    assert head is not None
    lines = _TEXT[head.start() :].splitlines()[2:]
    rows: dict[str, str] = {}
    for line in lines:
        if not line.startswith("|"):
            break
        scenario, _, rest = line.strip("|").partition("|")
        rows[scenario.strip()] = rest
    return rows


def _commands() -> list[str]:
    commands: list[str] = []
    for tag, body in _FENCE.findall(_TEXT):
        if tag:
            continue
        lines = body.splitlines()
        while lines:
            command = lines.pop(0)
            while command.endswith(" \\"):
                command = command[:-2] + " " + lines.pop(0).strip()
            if command.startswith(_PROGRAM):
                commands.append(command)
    return commands


def test_the_frontmatter_names_the_skill_and_describes_it() -> None:
    match = _FRONTMATTER.match(_TEXT)
    assert match is not None
    entries = dict(line.split(": ", 1) for line in match.group(1).splitlines())

    assert entries["name"] == _SKILL.parent.name
    assert 0 < len(entries["description"]) <= _DESCRIPTION_LIMIT


def test_it_hands_a_founders_review_to_the_skill_built_for_it_and_asks_for_the_tools_share_basis() -> None:
    """A review goes to the skill that reads the results; a fully diluted total that counts SAFEs is asked about."""
    text = " ".join(line.strip() for line in _TEXT.splitlines())

    for name in ("vc-deal-math", "vc-round-sizing", "vc-metrics-readiness", "vc-market-sizing", "vc-term-sheet-review"):
        assert f"the {name} skill" in text, name
        assert (_SKILL.parents[1] / name / "SKILL.md").is_file(), name
    assert "leaves SAFEs and notes out" in text and "ask which way the user's does" in text
    assert "never subtract the SAFE or note shares yourself" in text
    assert "never strings" in text and "For `deal_check`, never assume one" in text
    assert "never as an assumed figure" in text and "State any value you had to assume" not in text


def test_the_field_table_names_every_input_field_and_nothing_else() -> None:
    rows = _table_rows()

    assert sorted(rows) == sorted(_INPUT_MODELS)
    for scenario, model in _INPUT_MODELS.items():
        fields, values = _schema_names(model.model_json_schema())
        named = set(_NAME.findall(rows[scenario]))
        assert fields - {"scenario"} <= named, scenario
        assert named <= fields | values, scenario


def test_the_json_example_is_a_valid_investor_call() -> None:
    (example,) = (body for tag, body in _FENCE.findall(_TEXT) if tag == "json")
    arguments = json.loads(example)

    assert list(arguments) == ["inputs"]
    _INPUT_MODELS["investor"].model_validate(arguments["inputs"])


@pytest.mark.parametrize("command", _commands(), ids=lambda command: command.split()[1])
async def test_each_skill_command_runs(command: str) -> None:
    printed = await run(shlex.split(command)[1:])

    assert printed.strip()


def test_the_skill_has_its_commands() -> None:
    assert len(_commands()) >= 3


def test_the_skill_asks_the_founders_basis_assumes_no_figure_and_points_to_the_review_skills() -> None:
    text = " ".join(line.strip() for line in _TEXT.splitlines())
    rows = _table_rows()

    # Fully diluted shares leave SAFEs and notes out; a cap table that counts them is asked for its total without them.
    for scenario in ("round", "deal_check"):
        assert "`fully_diluted_shares` (SAFEs and notes left out: see below)" in rows[scenario].replace(
            "**", ""
        ), scenario
    assert "ask which way the user's does, and pass the tool its own basis" in text
    assert "never subtract the SAFE or note shares yourself" in text
    # Counts of customers and months are whole numbers, like share counts.
    assert "customer counts" in text and "month counts" in text and "JSON integers, never strings" in text
    # No figure is assumed: a default left in place is named as one.
    assert "Never fill a gap with a figure the user did not give" in text and "never as an assumed figure" in text
    assert "For `deal_check`, never assume one" in text
    for name in (
        "vc-deal-math",
        "vc-round-sizing",
        "vc-metrics-readiness",
        "vc-market-sizing",
        "vc-term-sheet-review",
        "vc-current-investor-update",
    ):
        assert f"the {name} skill" in text, name
        assert (_SKILL.parents[1] / name / "SKILL.md").is_file(), name
