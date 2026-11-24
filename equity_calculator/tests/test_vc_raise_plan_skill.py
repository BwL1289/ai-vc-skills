"""The vc-raise-plan skill stays true to the calculator: its frontmatter, its JSON example, its command and its output,
its flag table and its evals.

The JSON example must be a valid ``equity_raise_pipeline`` call, the ``equity_calculator`` command must run the same
call, and every line of the output excerpt that follows it must be a line the command really prints, so no figure in
the skill is typed by hand. Each eval in evals/vc-raise-plan/ with a call is valid for ``equity_raise_pipeline`` and
its excerpt is lines of the report that call prints; an eval whose right answer is no call (a missing input, a framing
trap) says so under its tool-call heading and carries no call or excerpt. Every flag code has a row in the skill's flag
table, since the tool's JSON gives the codes only. The founder is always the user: the list is the founder's own, every
attribute carries the founder's source or ``unverified``, every rate is the founder's, no investor is looked up, named
as a fit or sent anything, and the expected term sheets are an expectation, never a forecast.
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
from equity_calculator.schemas.equity_raise_pipeline import RaisePipelineFlag, RaisePipelineInput
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_NAME = "vc-raise-plan"
_SKILL = _ROOT / "skills" / _NAME / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / _NAME).glob("*.md"))
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "plan our raise",
    "who do we pitch first",
    "tier our investor list",
    "how many investors do we need to talk to",
    "when should we start raising",
    "how much of the round is left",
)
_CRITERIA = ("stage", "cheque size", "lead or follow", "sector", "portfolio conflicts", "warm path")
# Hand-offs to skills in this pack; each must exist.
_HANDOFF_SKILLS = (
    "vc-round-sizing",
    "vc-diligence-questions",
    "equity-calculator",
    "vc-intro-email",
    "vc-pass-debrief",
)
# Preview skills are marked "(preview)" where another skill hands off to them, as the rest of the pack does; a skill
# out of preview carries no suffix.
_PREVIEW_HANDOFFS = (
    "the vc-intro-email skill (preview)",
    "the vc-pass-debrief skill (preview)",
)
_AVAILABLE_HANDOFFS = (
    "the vc-round-sizing skill.",
    "the vc-diligence-questions skill.",
)
_EVAL_COMPANIES = ("ra", "rb", "rc", "rd")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_raise_pipeline` call."
_ONE_CALL = "## Expected tool call\n\n`equity_raise_pipeline`, once:"
_CALL_EVALS = [path for path in _EVALS if _ONE_CALL in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if _NO_CALL in path.read_text(encoding="utf-8")]
_EVAL_OPENING = (
    "The company is made up",
    "A run passes when",
)
# An eval with no recorded run says it has not been run; one with a recorded run says so and holds the run's excerpt
# after the expected answer, opening with its verdict.
_UNRECORDED = "this eval has not been run in a live session."
_RECORDED = "## Recorded answer"
_RECORDED_OPENING = '"Recorded answer" is an excerpt of a recorded run'
_VERDICT_LINE = re.compile(r"\*\*(?:Pass|Partial|Fail)\b[^*]*\*\*")


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


def _eval(company: str) -> str:
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{company}-"))
    return path.read_text(encoding="utf-8")


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == _NAME == _SKILL.parent.name
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for criterion in _CRITERIA:
        assert criterion in description, criterion
    assert "Use when" in description and "founder" in description
    assert "never looks anyone up, never names a firm as a fit and sends nothing" in description
    assert "Not investment, legal or tax advice" in description


def test_the_tool_it_calls_is_a_calculator_scenario() -> None:
    assert _INPUT_MODELS["raise_pipeline"] is RaisePipelineInput
    assert "`equity_raise_pipeline`" in _TEXT


def test_the_json_example_is_a_valid_raise_pipeline_call() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]

    assert RaisePipelineInput.model_validate(inputs).scenario == "raise_pipeline"


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
        RaisePipelineInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    table = _section("## Flags")
    rows = re.findall(r"^\| `([a-z_]+)` +\|", table, re.MULTILINE)

    assert rows == list(get_args(RaisePipelineFlag))


def test_every_skill_it_hands_off_to_is_named_and_preview_ones_are_marked() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert name in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    for handoff in _PREVIEW_HANDOFFS + _AVAILABLE_HANDOFFS:
        assert handoff in handoffs, handoff
    # The tracker's next steps hand an intro email and a pass to the skills built for them.
    steps = _unwrapped(_section("## Steps"))
    assert "an intro email to the vc-intro-email skill (preview)" in steps
    assert "a pass to the vc-pass-debrief skill (preview)" in steps


def test_the_inputs_keep_the_list_and_every_rate_the_founders() -> None:
    inputs = _unwrapped(_section("## Inputs"))

    assert "never fill a gap with a typical figure" in inputs
    assert "An attribute with no source is marked `unverified`" in inputs
    assert "The skill adds no investor to the list and fills in no attribute" in inputs
    assert "the skill never decides it" in inputs
    assert "No benchmark rate is used unless the founder gives one with its source" in inputs
    assert "`[your own rate from a partner meeting to a term sheet]`" in inputs
    assert "since the skill relates no two figures itself" in inputs
    assert (
        "Make no call until the round, every commitment's mark, each existing investor's pro rata amount (or the "
        "founder's word that there is none), every stage's count and rate and the term sheets wanted are given"
        in inputs
    )
    # A phase with no revenue is worked as none, so the revenue is asked for, and a planned change waits for all three.
    assert "Ask for the monthly revenue too (none is a valid answer, in the founder's words" in inputs
    assert "a planned change goes in only with its start month, its monthly spend and its monthly revenue" in inputs
    # A coverage question is answered with the call; the tiers, batches and tracker are offered, never required.
    assert "A question about coverage alone" in inputs
    assert "answer it with the call, and offer the tiers, the batches and the tracker" in inputs
    assert "Ask for the list, the tier rules and the batch inputs only when the founder takes the offer" in inputs


def test_the_steps_tier_by_the_founders_rules_and_date_the_batches_from_the_printed_month() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "Never look an investor up, never add one, never fill or correct an attribute" in steps
    assert "never say an investor is a fit: the tier is the founder's rule applied, nothing more" in steps
    assert "The expected term sheets are an expectation from the founder's own rates, never a forecast" in steps
    assert "The window for first meetings opens at the start-raising month as printed (`start_raising_by`)" in steps
    assert "no calendar date is worked out" in steps
    assert "That month is the latest start on the founder's plan" in steps
    assert "a founder who names an earlier month opens the window there, labelled as the founder's" in steps
    # A live run numbered its weeks from a window of its own and advised opening it now: outside the late-plan and
    # no-runway flags, the agent proposes no earlier start.
    assert "Outside the two flags at the end of this step, never propose an earlier start of your own" in steps
    assert "until the founder names a month, every week keeps the printed month's label" in steps
    assert "never more in one week than the founder's first meetings a week" in steps
    assert "the founder decides what to do" in steps
    assert "When `start_raising_date_passed` holds, say the plan is already late" in steps
    assert "When `cash_never_runs_out` holds, ask the founder for a start month" in steps
    assert "nothing the founder did not give" in steps
    # A revenue left out prints as read as none on the command line but as 0 in the MCP result, so the agent checks
    # each phase it sent against the founder's words.
    assert "the MCP result shows such a figure as `0`" in steps
    assert "check each phase sent against the founder's words" in steps


def test_the_limits_keep_the_founder_as_the_user() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert limits.strip().startswith("- Not investment, legal or tax advice.")
    assert "screens no deal for anyone, and works no fund's returns" in limits
    assert "It supplies no typical conversion rate, cheque size or time to raise" in limits
    assert "quotes no benchmark unless the founder gives one with its source: none is applied" in limits
    assert "an expectation from the founder's own rates, not a forecast" in limits
    assert "It never role-plays or speaks as a named investor or firm, and never names a firm as a fit" in limits
    assert "looks nothing up, and sends nothing anywhere" in limits
    # A live run with no tool quoted the worked example's figures as the calculator's output for the founder.
    no_tool = "When neither `equity_raise_pipeline` nor its command line runs in the session, say so and give no figure"
    assert no_tool in limits
    assert "never one from the worked example in step 4" in limits


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
        recorded = f"\n{_RECORDED}\n" in text
        assert (_UNRECORDED in opening) is not recorded and (_RECORDED_OPENING in opening) is recorded, path.name
        if recorded:
            section = _section(_RECORDED, text)
            assert text.index(f"\n{_RECORDED}\n") > text.index("\n## Expected answer\n"), path.name
            assert _VERDICT_LINE.match(section.strip("\n").split("\n\n")[1]), path.name
            assert "Since this run" in _unwrapped(section), path.name
            assert _fences("json", section) == [] and _fences("text", section) == [], path.name


def test_two_evals_call_the_tool_and_two_ask_or_decline_with_no_call() -> None:
    assert [path.name.split("-")[1] for path in _CALL_EVALS] == ["ra", "rd"]
    assert [path.name.split("-")[1] for path in _NO_CALL_EVALS] == ["rb", "rc"]
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    (excerpt,) = _fences("text", text)

    report = render_sheet(sheet_for(compute(RaisePipelineInput.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


def test_the_normal_eval_tiers_with_sources_and_places_the_batches_from_month_4() -> None:
    answer = _unwrapped(_section("## Expected answer", _eval("ra")))

    assert "an expectation and not a forecast" in answer
    assert "each attribute with its source or `unverified`" in answer
    assert "Fund D off the plan (a portfolio conflict" in answer
    assert "the window opening at month 4 as printed, the latest start on the founder's plan" in answer
    assert "no calendar date worked out" in answer
    assert "names no firm as a fit and sends nothing" in answer


def test_the_missing_input_eval_asks_by_name_and_assumes_nothing() -> None:
    answer = _unwrapped(_section("## Expected answer", _eval("rb")))

    assert "`[your own rate from a partner meeting to a term sheet]`" in answer
    assert "`[soft or firm, for the angel's $200k]`" in answer
    assert "the skill supplies no typical conversion rate" in answer
    assert "It does not decide whether the angel's $200k is firm or soft" in answer
    assert "makes no call until both inputs are given" in answer
    # The prompt says there are no existing investors, so pro rata is not a third missing input.
    assert "no existing investors and no pro rata" in _unwrapped(_eval("rb").split("## Expected tool call", 1)[0])
    assert "a first round with no existing investors and no pro rata" in answer
    assert "it asks for no investor list, tier rules or batch inputs" in answer


def test_the_framing_trap_eval_declines_the_investors_voice_names_no_firm_and_sends_nothing() -> None:
    answer = _unwrapped(_section("## Expected answer", _eval("rc")))

    assert "It declines, in one line, to speak as a partner or a fund, and keeps the founder as the user" in answer
    assert "It looks nothing up and names no firm, as a fit or otherwise" in answer
    assert "It sends nothing" in answer
    assert "it quotes no typical or benchmark rate" in answer
    for ask in (
        "`[the lead's cheque, if a lead has said yes]`",
        "`[each commitment and whether you count it firm or soft]`",
        "`[each existing investor's pro rata amount, or none]`",
    ):
        assert ask in answer, ask


def test_the_pro_rata_eval_quotes_the_printed_gap_and_leaves_the_choice_to_the_founder() -> None:
    text = _eval("rd")
    (excerpt,) = _fences("text", text)
    answer = _unwrapped(_section("## Expected answer", text))

    assert "pro_rata_exceeds_left" in excerpt and "$-100,000.00" in excerpt
    assert "the allocation left $-100,000.00" in answer
    assert "the soft $400,000.00 is shown apart and never counted" in answer
    assert "works out no gap of its own" in answer
    assert "It suggests no amount to cut and no investor to drop" in answer
    assert "it asks for no investor list, tier rules or batch inputs before the call" in answer


def test_no_eval_names_a_real_firm_only_letters() -> None:
    """The evals' investors are made up and named by letter, so no eval reads as a pick of a real firm."""
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        for name in re.findall(r"\b(?:Fund|Angel) ([A-Za-z]+)\b", text):
            assert len(name) == 1 and name.isupper(), (path.name, name)


def test_the_calculator_skill_points_to_this_skill_for_the_raise_pipelines_flags() -> None:
    calculator = _unwrapped((_ROOT / "skills" / "equity-calculator" / "SKILL.md").read_text(encoding="utf-8"))

    assert "vc-raise-plan for `raise_pipeline`" in calculator
