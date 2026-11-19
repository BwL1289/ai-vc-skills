"""The agent skill stays true to the calculator: its frontmatter, its field table, its JSON example and its commands.

The field table must name every input field of every scenario (nested instruments, rounds and classes included) and
nothing that is not a field or an allowed value; the JSON example must be a valid ``equity_investor`` call; and each
``equity-calculator`` command in it must run and print a report.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import Any

import pytest
from equity_calculator.__main__ import _INPUT_MODELS, run

_SKILL = Path(__file__).resolve().parents[1] / "skills" / "equity-calculator" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
_FENCE = re.compile(r"^```([a-z]*)\n(.*?)^```$", re.MULTILINE | re.DOTALL)
# The field table's header row, however its cells are padded (a Markdown formatter may align the columns).
_TABLE_HEAD = re.compile(r"^\|\s*Scenario\s*\|\s*Fields \(required in bold\)\s*\|$", re.MULTILINE)
_NAME = re.compile(r'[`"]([a-z_]+)[`"]')
_PROGRAM = "equity-calculator "
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
