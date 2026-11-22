"""The vc-positioning skill keeps its shape: its frontmatter, its tool names, its adversarial review and its evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The adversarial review must keep both stages: independent attack lenses named by what
they test (never by a person or firm), each objection quoting the founder's own line; a refute pass that may use only
the founder's material and records why each dropped objection fell; and the ranked survivors, with quotes, in the
answer. Each eval in evals/vc-positioning/ has a prompt, an expected tool call and an expected answer; the one eval
with an ``equity_deal_check`` call carries a valid call and an excerpt that is lines of the report that call prints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from equity_calculator.__main__ import _INPUT_MODELS
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-positioning" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-positioning").glob("*.md"))
_EVAL_COUNT = 4
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator")
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "tighten my pitch",
    "stress-test my pitch",
    "how should we position this round",
    "what should I not say to VCs",
    "prep me before we go out to raise",
)
_PHRASES = ("no competitors", "we only need 1% of the market", "our projections are conservative")
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_MIN_LENSES = 5
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|\s*Dimensions\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_SURVIVOR_COLUMNS = re.compile(
    r"Rank, Tier, Lens, The founder's line \(quoted\), Why a partner reads it that way,\s+Rewrite"
)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')


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


def _fences(language: str, text: str) -> list[str]:
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


def _lens_names() -> list[str]:
    table = _section("### Stage A: attack")
    head = _LENS_HEAD.search(table)
    assert head is not None
    rows = table[head.end() :].strip().split("\n\n", 1)[0].splitlines()[1:]
    return [match.group(1) for row in rows if (match := _ROW.match(row))]


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-positioning"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in _PHRASES:
        assert phrase in description, phrase
    assert "founder" in description and "adversarial review" in description


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_round", "equity_dilution"} <= named
    assert named <= served, named - served


def test_every_skill_it_hands_off_to_exists() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = _lens_names()

    assert len(lenses) >= _MIN_LENSES
    for lens in lenses:
        assert not any(re.search(rf"\b{name}\b", lens.lower()) for name in _PEOPLE_AND_FIRMS), lens
    assert "quoted word for word" in attack
    assert "subagent" in attack and "only the founder's material and its lens brief" in attack
    assert "one after another" in attack
    assert "do no arithmetic" in attack


def test_every_dimension_row_names_a_lens_that_exists() -> None:
    lenses = set(_lens_names())
    table = _section("## The dimensions")
    rows = [row for row in table.splitlines() if re.match(r"^\|\s*\d+\s*\|", row)]

    assert rows
    for row in rows:
        assert row.rstrip(" |").rsplit("|", 1)[1].strip() in lenses, row


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))

    assert "using only the founder's material" in refute
    assert "one subagent per objection" in refute
    for verdict in ("Dropped, answered:", "Dropped, not grounded:", "Kept:"):
        assert verdict in refute, verdict
    assert "Quote the founder's line that answers it" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_survivors_are_ranked_with_quotes_and_feed_the_rest_of_the_answer() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    answering = _unwrapped(_section("## Answering"))

    assert "the founder's line, quoted word for word" in rank
    assert "no percentages and no score" in rank
    for destination in ("biggest issues", "say-and-avoid list", "tightened narrative", "prep script"):
        assert destination in rank, destination
    assert "**Adversarial review:**" in answering and "**Dropped,**" in answering
    assert _SURVIVOR_COLUMNS.search(answering)


def test_the_steps_run_the_adversarial_review() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "**Run the adversarial review**" in steps
    assert "every surviving objection quotes a line that is in the material word for word" in steps


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name


def test_one_eval_has_the_phrases_that_cost_the_meeting() -> None:
    prompts = {path.name: _unwrapped(_section("## Prompt", path.read_text(encoding="utf-8"))) for path in _EVALS}
    (name,) = (name for name, prompt in prompts.items() if all(phrase in prompt for phrase in _PHRASES[:2]))
    answer = _section("## Expected answer", (_ROOT / "evals" / "vc-positioning" / name).read_text(encoding="utf-8"))

    assert "survive" in answer and "We have no competitors." in answer


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    dropping = [path for path in _EVALS if "Dropped, answered" in _unwrapped(path.read_text(encoding="utf-8"))]
    assert dropping
    for path in dropping:
        text = path.read_text(encoding="utf-8")
        prompt = _unwrapped(_section("## Prompt", text))
        answer = _unwrapped(_section("## Expected answer", text))
        objection, dropped = answer.split("Dropped, answered", 1)
        # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
        # founder's material, not the line the objection was about.
        answering_line = _DOUBLE_QUOTED.findall(dropped)[0]
        assert answering_line in prompt
        assert answering_line not in _DOUBLE_QUOTED.findall(objection)


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


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
