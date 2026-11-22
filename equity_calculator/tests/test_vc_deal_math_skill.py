"""The vc-deal-math skill stays true to the calculator: its frontmatter, its JSON example, its command and its output.

The JSON example must be a valid ``equity_deal_check`` call, the ``equity_calculator`` command must run, and every
line of the output excerpt that follows it must be a line the command really prints, so no figure in the skill is
typed by hand. The same holds for each eval prompt in evals/vc-deal-math/: its tool call is valid and its excerpt is
lines of the report that call prints. An eval whose right answer is no ``equity_deal_check`` call (a raise on a SAFE)
says so under its tool-call heading and carries no call or excerpt to check. Every flag code has a row in the skill's
flag table, since the tool's JSON gives the codes only.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import run
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealFlag
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-deal-math" / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / "vc-deal-math").glob("*.md"))
_EVAL_COUNT = 4
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "check my deck's numbers",
    "is our raise reasonable",
    "what does this round do to my ownership",
    "how much runway does this buy",
    "will a VC question our valuation",
)


def _fences(language: str, text: str = _TEXT) -> list[str]:
    found = []
    for match in _FENCE.finditer(text):
        indent, tag, body = match.groups()
        if tag == language:
            found.append("\n".join(line.removeprefix(indent) for line in body.splitlines()))
    return found


def _frontmatter() -> dict[str, str]:
    block = _FRONTMATTER.match(_TEXT)
    assert block is not None
    fields = {}
    for line in block.group(1).splitlines():
        key, _, value = line.partition(": ")
        fields[key] = value
    return fields


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()

    assert fields["name"] == "vc-deal-math"
    assert len(fields["description"]) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(fields["description"])
    assert ": " not in fields["description"]
    for trigger in _TRIGGERS:
        assert trigger in fields["description"]
    assert "founder" in fields["description"]


def test_the_json_example_is_a_valid_deal_check_call() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]

    assert DealCheckInput.model_validate(inputs).scenario == "deal_check"


async def test_the_command_runs_and_prints_every_line_of_the_excerpt() -> None:
    (command,) = _fences("")
    (excerpt,) = _fences("text")
    assert command.startswith(_PROGRAM) and "\n" not in command.strip()

    printed = (await run(shlex.split(command)[1:])).splitlines()

    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_command_and_the_json_example_are_the_same_check() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        DealCheckInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_there_is_one_eval_per_worked_company() -> None:
    assert len(_EVALS) == _EVAL_COUNT


def test_one_eval_expects_no_deal_check_call() -> None:
    (path,) = _NO_CALL_EVALS
    text = path.read_text(encoding="utf-8")

    assert _fences("json", text) == [] and _fences("text", text) == []
    assert "equity_round" in text


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    table = _TEXT.split("## Flags", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\| `([a-z_]+)` +\|", table, re.MULTILINE)

    assert rows == list(get_args(DealFlag))


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    (excerpt,) = _fences("text", text)

    report = render_sheet(sheet_for(compute(DealCheckInput.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line
