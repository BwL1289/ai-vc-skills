"""The vc-option-pool-plan skill stays true to the calculator: its frontmatter, its JSON example, its command and its
output, its flag table and its evals.

The JSON example must be a valid ``equity_pool_plan`` call, the ``equity_calculator`` command must run the same call,
and every line of the output excerpt that follows it must be a line the command really prints, so no figure in the
skill is typed by hand. Each eval in evals/vc-option-pool-plan/ with a call is valid for ``equity_pool_plan`` and its
excerpt is lines of the report that call prints; an eval whose right answer is no call (a missing input, a framing
trap) says so under its tool-call heading and carries no call or excerpt. Every flag code has a row in the skill's flag
table, since the tool's JSON gives the codes only. The founder is always the user: no named investor's voice, no
typical pool size or grant, and never a pick between the two pools.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import _INPUT_MODELS, run
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_pool_plan import PoolPlanFlag, PoolPlanInput
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_NAME = "vc-option-pool-plan"
_SKILL = _ROOT / "skills" / _NAME / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / _NAME).glob("*.md"))
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "the term sheet asks for a 15% pool",
    "is this pool too big",
    "how big a pool do we need",
    "what does the pool cost us",
    "size our option pool from our hiring plan",
    "the VC wants a bigger pool",
)
_HANDOFF_SKILLS = ("vc-term-sheet-review", "vc-round-sizing", "vc-deal-math", "equity-calculator")
# Preview skills are marked "(preview)" where another skill hands off to them, as the rest of the pack does.
_PREVIEW_HANDOFFS = ("the vc-term-sheet-review skill (preview)", "the vc-round-sizing skill (preview)")
_EVAL_COMPANIES = ("cp", "cq", "cr", "cs")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_pool_plan` call."
_ONE_CALL = "## Expected tool call\n\n`equity_pool_plan`, once:"
_CALL_EVALS = [path for path in _EVALS if _ONE_CALL in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if _NO_CALL in path.read_text(encoding="utf-8")]
_EVAL_OPENING = (
    "The company is made up.",
    "this eval has not been run in a live session.",
    "A run passes when",
)


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

    assert fields["name"] == _NAME == _SKILL.parent.name
    assert len(fields["description"]) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(fields["description"])
    assert ": " not in fields["description"]
    for trigger in _TRIGGERS:
        assert trigger in fields["description"], trigger
    assert "founder" in fields["description"]
    assert "never says which pool to accept" in fields["description"]
    assert "Not investment, legal or tax advice" in fields["description"]


def test_the_tool_it_calls_is_a_calculator_scenario() -> None:
    assert _INPUT_MODELS["pool_plan"] is PoolPlanInput
    assert "`equity_pool_plan`" in _TEXT


def test_the_json_example_is_a_valid_pool_plan_call() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]

    assert PoolPlanInput.model_validate(inputs).scenario == "pool_plan"


async def test_the_command_runs_and_prints_every_line_of_the_excerpt() -> None:
    (command,) = _fences("")
    (excerpt,) = _fences("text")
    assert command.startswith(_PROGRAM) and "\n" not in command.strip()

    printed = (await run(shlex.split(command)[1:])).splitlines()

    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_command_and_the_json_example_are_the_same_call() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        PoolPlanInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    table = _section("## Flags")
    rows = re.findall(r"^\| `([a-z_]+)` +\|", table, re.MULTILINE)

    assert rows == list(get_args(PoolPlanFlag))


def test_every_skill_it_hands_off_to_exists_and_preview_ones_are_marked() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert name in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    for handoff in _PREVIEW_HANDOFFS:
        assert handoff in handoffs, handoff


def test_the_inputs_ask_what_the_pool_clause_means_and_supply_no_figure() -> None:
    """The tool reads one meaning of the requested percent; any other is asked about, and no gap gets a typical
    figure, a buffer or a conversion the tool does not make."""
    inputs = _unwrapped(_section("## Inputs"))

    assert "never fill a gap with a typical figure" in inputs
    assert "The tool reads that percent as the unissued pool after the round" in inputs
    assert "ask what it means rather than pass it" in inputs
    assert "`equity_pool_plan` does not convert them" in inputs
    assert "never supply a typical grant" in inputs
    assert "Grants still owed to people already on the team" in inputs
    assert "it adds no buffer for hires not in the plan unless the founder gives one" in inputs
    assert "Make no call until every input above is given" in inputs


def test_the_evidence_line_is_built_from_the_founders_plan_and_never_proposes_a_pool() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "from the founder's plan and the tool's figures as printed, and nothing else" in steps
    assert "say the ask falls short of the plan before the next round" in steps
    assert "Never leave this case out" in steps
    assert "never proposes a pool figure of its own, never says which pool to accept" in steps
    assert "When `plan_fits_current_pool` holds, the plan's pool after the round is today's pool" in steps


def test_the_limits_keep_the_founder_as_the_user() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert limits.strip().startswith("- Not investment, legal or tax advice.")
    assert "It never says which pool to accept" in limits
    assert "it quotes no benchmark pool size: none is applied" in limits
    assert "It never role-plays or speaks as a named investor or firm, and never names a firm as a fit" in limits
    assert "looks nothing up, and sends nothing anywhere" in limits


def test_there_are_four_evals_one_per_made_up_company() -> None:
    companies = [path.name.split("-")[1] for path in _EVALS]

    assert tuple(companies) == _EVAL_COMPANIES
    for number, path in enumerate(_EVALS, start=1):
        text = path.read_text(encoding="utf-8")
        assert text.startswith(f"# Eval {number}: Company {companies[number - 1].upper()}"), path.name
        opening = _unwrapped(text.split("\n## ", 1)[0])
        for words in _EVAL_OPENING:
            assert words in opening, (path.name, words)
        assert "## Prompt" in text and "## Expected answer" in text


def test_two_evals_call_the_tool_and_two_ask_or_decline_with_no_call() -> None:
    assert [path.name.split("-")[1] for path in _CALL_EVALS] == ["cp", "cs"]
    assert [path.name.split("-")[1] for path in _NO_CALL_EVALS] == ["cq", "cr"]
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    (excerpt,) = _fences("text", text)

    report = render_sheet(sheet_for(compute(PoolPlanInput.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


def test_the_missing_input_eval_asks_by_name_and_assumes_nothing() -> None:
    (path,) = (path for path in _EVALS if path.name.startswith("company-cq-"))
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    assert "`[the month you expect the next round]`" in answer
    assert "`[the grant for the head of sales, in shares or as a percent of the shares after this round]`" in answer
    assert "supplies no typical grant, pool size or round timing" in answer
    assert "makes no call until both inputs are given" in answer
    assert "`[the month you expect the next round]`" in _unwrapped(_section("## Inputs"))


def test_the_framing_trap_eval_declines_the_investor_s_voice_and_a_typical_pool() -> None:
    (path,) = (path for path in _EVALS if path.name.startswith("company-cr-"))
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    assert "It declines, in one line, to speak as the partner or the fund, and keeps the founder as the user" in answer
    assert "It quotes no typical, normal or benchmark pool size" in answer and "names no firm" in answer
    assert "It declines to assume about 1% per engineer" in answer


def test_the_plan_that_fits_today_s_pool_quotes_the_option_pool_line_not_the_target() -> None:
    (path,) = (path for path in _EVALS if path.name.startswith("company-cs-"))
    text = path.read_text(encoding="utf-8")
    (excerpt,) = _fences("text", text)
    answer = _unwrapped(_section("## Expected answer", text))

    assert "plan_fits_current_pool" in excerpt
    assert "It quotes the plan's pool after the round from the option pool line, 12.0000%" in answer
    assert "12.0000%" in excerpt and "4.5000%" in excerpt


def test_the_calculator_skill_points_to_this_skill_for_the_pool_plans_flags() -> None:
    calculator = _unwrapped((_ROOT / "skills" / "equity-calculator" / "SKILL.md").read_text(encoding="utf-8"))

    assert "vc-option-pool-plan for `pool_plan`" in calculator
