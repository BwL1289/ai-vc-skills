"""The vc-cap-table-check skill stays true to the calculator: its frontmatter, its JSON example, its command and output.

The JSON example must be a valid ``equity_cap_table_check`` call, the ``equity_calculator`` command must run and be the
same check, and every line of the output excerpt that follows it must be a line the command really prints, so no
figure in the skill is typed by hand. The same holds for each eval in evals/vc-cap-table-check/: its call is valid and
its excerpt is lines of the report that call prints. One eval's right answer is no call yet (percents with no basis,
and a SAFE with no next round): it asks for both by name. Every flag code has a row in the skill's flag table, since
the tool's JSON gives the codes only. The skill never rules on legal validity or says what to accept, lists the
questions for the company's lawyer, and hands round math, the pool, term sheets and diligence to the skills for them.
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
from equity_calculator.schemas.equity_cap_table_check import CapTableCheckInput, CapTableFlag
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-cap-table-check" / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / "vc-cap-table-check").glob("*.md"))
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_EVAL_COUNT = 4
_TRIGGERS = (
    "check my cap table",
    "does our cap table add up",
    "how much do the founders really own",
    "what do our SAFEs do to the cap table",
    "how much dead equity do we have",
)
# Each is a skill folder in this repository.
_POOL_SKILL = "vc-option-pool-plan"
_HANDOFF_SKILLS = ("equity-calculator", "vc-deal-math", "vc-term-sheet-review", "vc-diligence-questions", _POOL_SKILL)
_NO_CALL = "## Expected tool call\n\nNone: no `equity_cap_table_check` call yet."
_CALLED_TOOL = re.compile(r"^## Expected tool call\n\n`equity_([a-z_]+)`, once:$", re.MULTILINE)
_BASIS_ASK = "`[what the table's percents are a share of: fully diluted or outstanding]`"
_READ_THE_FILE = (
    "When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and"
    " list what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what"
    " was read from each. A place you could not read (a slide that is only a picture, a page whose text did not come"
    " out, a file that opened only in part) is listed as not read and asked for, never filled in from its title or the"
    " places around it, and a figure is never read off a chart or a picture. Ask only for what you could not read and"
    " what the file does not show (speaker notes, the figures behind a chart, an input below that it leaves out), and"
    " never ask the founder to paste what you already read."
)
_NO_COMPARISON = (
    "Never work out how two of the founder's figures relate (a difference, a sum, a ratio or multiple, a share left"
    ' over, "doubled") in a rewrite, a line or a table cell unless the founder\'s material states it or a tool returned'
    ' it; quote both figures as stated instead ("from 2,000 to 4,500", never "more than doubled").'
)
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if _NO_CALL in path.read_text(encoding="utf-8")]


def _section(heading: str, text: str = _TEXT) -> str:
    """The body under ``heading`` up to the next heading of the same or a higher level."""
    level = heading.split(" ", 1)[0]
    start = text.index(f"\n{heading}\n") + len(heading) + 2
    stops = [text.find(f"\n{'#' * depth} ", start) for depth in range(1, len(level) + 1)]
    ends = [stop for stop in stops if stop != -1]
    return text[start : min(ends)] if ends else text[start:]


def _unwrapped(text: str) -> str:
    """``text`` with its Markdown line breaks and blockquote marks taken out, so a wrapped sentence reads as one."""
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


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

    assert fields["name"] == "vc-cap-table-check"
    assert len(fields["description"]) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(fields["description"])
    assert ": " not in fields["description"]
    for trigger in _TRIGGERS:
        assert trigger in fields["description"], trigger
    assert "founder" in fields["description"]
    assert "never says whether a share was validly issued" in fields["description"]


def test_the_skill_stays_under_the_line_limit() -> None:
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_the_json_example_is_a_valid_cap_table_check_call() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]

    assert CapTableCheckInput.model_validate(inputs).scenario == "cap_table_check"


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
        CapTableCheckInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_there_are_four_evals_three_with_a_call() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert len(_CALL_EVALS) == _EVAL_COUNT - 1


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    (excerpt,) = _fences("text", text)
    tool = _CALLED_TOOL.search(text)
    assert tool is not None and tool.group(1) == "cap_table_check"

    report = render_sheet(sheet_for(compute(CapTableCheckInput.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_every_percent_in_an_eval_answer_is_one_the_calculator_printed(path: Path) -> None:
    """A percent the answer quotes with four places is the report's own, never one worked out in the answer's text."""
    text = path.read_text(encoding="utf-8")
    (excerpt,) = _fences("text", text)
    answer = _section("## Expected answer", text)

    for figure in re.findall(r"-?\d+\.\d{4}%", answer):
        assert figure in excerpt, figure


def test_the_missing_input_eval_asks_for_the_basis_and_the_next_round_by_name() -> None:
    (path,) = _NO_CALL_EVALS
    text = path.read_text(encoding="utf-8")
    answer = _unwrapped(_section("## Expected answer", text))

    assert _fences("json", text) == [] and _fences("text", text) == []
    assert _BASIS_ASK in answer and _BASIS_ASK in _unwrapped(_TEXT)
    assert "never picks one" in answer
    assert "never assumes a price or a valuation" in answer
    assert "It gives no percent, total or conversion figure of its own" in answer


def test_the_framing_trap_eval_rules_on_nothing_and_accepts_nothing() -> None:
    (path,) = (path for path in _EVALS if "legally-valid" in path.name)
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    assert "it does not say whether the shares were validly issued" in answer
    assert "does not answer in the voice of the investor's counsel or any named person or firm" in answer
    assert "It never says whether to accept the request" in answer
    assert f"the {_POOL_SKILL} skill" in answer
    assert "questions for the company's lawyer" in answer


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    table = _TEXT.split("## Flags", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\| `([a-z_]+)` +\|", table, re.MULTILINE)

    assert rows == list(get_args(CapTableFlag))


def test_every_skill_it_hands_off_to_is_named_and_exists() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "`equity_pool_plan`" in handoffs
    assert "being built" not in _TEXT
    assert "until it is there" not in _TEXT


def test_it_never_rules_on_legal_validity_and_lists_the_lawyer_s_questions() -> None:
    limits = _unwrapped(_section("## Limits"))
    questions = _section("## Questions for the lawyer")

    assert "It never says whether a share, a grant, a vesting schedule or a transfer is legally valid" in limits
    assert "never says whether to accept a term or a request" in limits
    assert "never the voice or opinion of a named investor or firm" in limits
    assert len(re.findall(r"^- .+\?$", questions, re.MULTILINE)) >= 5
    assert "never answer them yourself" in _unwrapped(questions)


def test_it_asks_for_the_basis_and_the_next_round_and_never_assumes_them() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert _BASIS_ASK in steps
    assert "never pick one because the figures fit it better" in steps
    assert "never assume a price or a valuation" in steps
    assert "The founders' path needs the rounds the founder plans" in steps and "Never invent one" in steps


def test_it_reads_a_file_and_never_works_out_a_relation_of_its_own() -> None:
    text = _unwrapped(_TEXT)

    assert _READ_THE_FILE in text
    assert _NO_COMPARISON in text
    when = _unwrapped(_section("## When to use it"))
    assert "Any of these may come as a file the agent can read in this session." in when
