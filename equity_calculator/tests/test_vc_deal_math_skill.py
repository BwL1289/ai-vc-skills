"""The vc-deal-math skill stays true to the calculator: its frontmatter, its JSON example, its command and its output.

The JSON example must be a valid ``equity_deal_check`` call, the ``equity_calculator`` command must run, and every
line of the output excerpt that follows it must be a line the command really prints, so no figure in the skill is
typed by hand. The same holds for each eval prompt in evals/vc-deal-math/: its tool call is valid for the tool it
names (``equity_deal_check``, or ``equity_instrument_compare`` for a founder choosing between a priced round and a
note) and its excerpt is lines of the report that call prints. An eval whose right answer is no ``equity_deal_check``
call (a raise on a SAFE) says so under its tool-call heading and carries no call or excerpt to check. Every flag code
has a row in the skill's flag table, since the tool's JSON gives the codes only. The fully diluted count the tool
takes leaves SAFEs and notes out, so step 2 asks which way the founder's total counts them; runway with no raise, or
on a SAFE or note raise, goes to ``equity_runway_plan``, whose flags the skill explains in words too.
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
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-deal-math" / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / "vc-deal-math").glob("*.md"))
_EVAL_COUNT = 5
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
# The tool an eval's call goes to, named first under its tool-call heading ("`equity_deal_check`, once:").
_CALLED_TOOL = re.compile(r"^## Expected tool call\n\n`equity_([a-z_]+)`, once:$", re.MULTILINE)
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
_HANDOFF_SKILLS = (
    "equity-calculator",
    "vc-round-sizing",
    "vc-metrics-readiness",
    "vc-market-sizing",
    "vc-term-sheet-review",
)
# A runway_plan call with no milestone, months to raise or landing month can raise only these three flags.
_RUNWAY_FLAGS_WITHOUT_MILESTONES = ("runway_below_band", "cash_never_runs_out", "consistent_beyond_rounding")
_NO_TOOL = "not checked: no tool computes this"


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
    tool = _CALLED_TOOL.search(text)
    assert tool is not None and tool.group(1) in ("deal_check", "instrument_compare")
    model = _INPUT_MODELS[tool.group(1)]

    report = render_sheet(sheet_for(compute(model.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


def test_every_skill_it_hands_off_to_exists() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert name in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_step_2_asks_which_way_the_founders_fully_diluted_total_counts_safes_and_notes() -> None:
    """The tool's count leaves SAFEs and notes out; a total that counts them gives the founders too low a figure."""
    steps = _unwrapped(_section("## Steps"))
    (company_b,) = (path for path in _EVALS if path.name.startswith("company-b-"))
    answer = _unwrapped(_section("## Expected answer", company_b.read_text(encoding="utf-8")))

    assert "SAFEs and notes left out, since the tool converts them itself" in steps
    assert "Some cap tables count SAFEs and notes in their fully diluted total" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "`[fully diluted shares before the round, SAFEs and notes left out]`" in steps
    assert "never subtract the SAFE or note shares yourself" in steps
    assert "leave the two SAFEs out, as the tool's count does" in answer
    assert "the figures stand only on that basis" in answer


def test_the_stand_in_share_count_is_named_as_this_skills_placeholder() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "offer a stand-in of 10,000,000 shares" in steps
    assert "call it this skill's placeholder in the answer, never a company figure" in steps


def test_runway_with_no_raise_or_on_a_safe_goes_to_the_runway_plan_tool() -> None:
    steps = _unwrapped(_section("## Steps"))
    handoffs = _unwrapped(_section("## When to use it"))

    assert "**Runway with no raise, or on a SAFE or note raise,** goes to `equity_runway_plan`" in steps
    assert "never to `deal_check`, which needs a priced round" in steps
    assert "With no cash or burn given, ask for them by name" in steps
    assert "make no call until they are given" in steps
    assert "`equity_runway_plan`" in handoffs
    # The MCP result gives flag codes only, so the skill carries the meaning of each flag such a call can raise.
    for flag in _RUNWAY_FLAGS_WITHOUT_MILESTONES:
        assert flag in get_args(RunwayPlanFlag), flag
        assert f"`{flag}` (" in steps, flag
    assert "no runway-plan flag" not in steps
    assert "which today is `unverified`" not in _TEXT


def test_figures_outside_the_deal_terms_go_to_the_skills_built_for_them() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert "ARR, retention, churn, CAC payback and burn multiple to the vc-metrics-readiness skill" in limits
    assert "a market size to the vc-market-sizing skill" in limits
    assert f'Growth rates and LTV are quoted as stated with "{_NO_TOOL}"' in limits
    assert "(a growth rate, a market size, unit economics)" not in limits


def test_one_eval_calls_the_comparison_tool_and_the_rest_deal_check() -> None:
    tools = [_CALLED_TOOL.search(path.read_text(encoding="utf-8")) for path in _CALL_EVALS]

    assert sorted(match.group(1) for match in tools if match is not None) == [
        "deal_check",
        "deal_check",
        "deal_check",
        "instrument_compare",
    ]


def test_a_founder_choosing_between_a_priced_round_and_a_note_goes_to_the_comparison_tool() -> None:
    """The step asks for both sets of terms, the next rounds and the exits, never picks, and hands law to a lawyer."""
    steps = _unwrapped(_section("## Steps"))
    (company_bu,) = (path for path in _EVALS if path.name.startswith("company-bu-"))
    answer = _unwrapped(_section("## Expected answer", company_bu.read_text(encoding="utf-8")))

    assert "has not chosen between a priced round now and a convertible note now** goes to" in steps
    assert "`equity_instrument_compare`" in steps and "never to `deal_check`" in steps
    assert 'Pass `{"standard": true}` only when the founder says the terms are standard' in steps
    assert "with no next round the tool refuses (`no_next_round_given`)" in steps
    assert "never assume one" in steps
    assert "Never pick one for them or call one better" in steps
    assert "to their lawyer" in steps
    assert "It never picks an option or calls one better" in answer
    assert "It does not call `equity_deal_check`" in answer
