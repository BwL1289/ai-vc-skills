"""The vc-round-sizing skill stays true to the calculator and keeps its shape: example, flags, review and evals.

The JSON example must be a valid ``equity_runway_plan`` call, the ``equity_calculator runway_plan`` command must run
and be the same plan, and every line of the excerpt after it must be a line the command prints, so no figure in the
skill is typed by hand. Every calculator tool the skill names must be served, and every skill it hands off to must be a
folder in skills/. Every flag code has a row in the flag table. The adversarial review keeps a skeptic that quotes the
founder and does no arithmetic, a refute pass with the three fixed verdicts, and computed results that never go
through it. Benchmark figures reach an answer only through the calculator's own assumption rows: the skill and its
evals' prose never state them. Each eval in evals/vc-round-sizing/ has a prompt, the expected tool calls and an
expected answer; each call is valid for the tool its label names, and its excerpt is lines of the report it prints.
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
from equity_calculator.schemas.equity import ScenarioInput, ScenarioResult
from equity_calculator.schemas.equity_deal_check import DealFlag
from equity_calculator.schemas.equity_runway_plan import (
    BurnCase,
    CaseName,
    RaiseOption,
    RunwayPlanFlag,
    RunwayPlanInput,
    RunwayPlanResult,
)
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-round-sizing" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_DEAL_MATH = (_ROOT / "skills" / "vc-deal-math" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-round-sizing").glob("*.md"))
_EVAL_COUNT = 4
# The repository gives each made-up company its own letter; this skill's evals use W to Z.
_EVAL_LETTERS = ("w", "x", "y", "z")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_runway_plan` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
# An eval's call: a line that starts with the tool's name and ends with a colon, then its JSON fence.
_LABELLED_CALL = re.compile(r"^`equity_([a-z_]+)`[^\n]*:\n\n```json\n(.*?)^```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_FLAG_NAME = re.compile(r"`([a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_PROGRAM = "equity_calculator "
_NEEDED_TOOLS = {"equity_runway_plan", "equity_deal_check", "equity_round", "equity_dilution"}
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator", "vc-positioning", "vc-claims-check", "vc-metrics-readiness")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "how much should we raise",
    "raise now or wait",
    "what milestone does this buy",
    "how long will this last",
    "what if we miss plan",
)
_REFUTE_VERDICTS = ("Kept, grounded:", "Dropped, answered:", "Dropped, not grounded:")
_GUIDE_URL = "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising"
_SOURCES_USED = {_GUIDE_URL}
_GUIDE = _READ_SOURCES[_GUIDE_URL]
_URL = re.compile(r"https?://\S+?(?=[.,)]?(?:\s|$))")
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
# Benchmark figures from public guides reach an answer only as the calculator's assumption rows print them.
_FREE_BENCHMARKS = ("12 to 18", "12-18", "more than 25", "up to 20%", "a quarter of the company", "15k", "$15,000")
_SAFE_SHARE = "not computed: set at the next priced round"
_NOT_CHECKED = "not checked: no tool computes this"
# The pattern rows that name something said: an attack on one stays Kept even when the material shows evidence. Every
# other row names something missing, and a line of the material that supplies it answers the attack.
_SAID_PATTERNS = (
    "Runway that ends at the milestone month",
    "Runway quoted on today's burn while the plan hires",
    "A monthly revenue milestone above the plan's revenue a month then",
    "Detailed multi-year financials at seed",
    "A large share of the company sold in the round",
)
_MISSING_MARKERS = ("no ", "No ", "One amount only")
_SKEPTIC_RAN = "whether the skeptic ran as a subagent"
# The one sentence every attack brief in the pack carries since a live run's attacker judged the material for itself.
_RAISE_IT_ANYWAY = "raise it anyway, however short the material, and the refute pass decides"
# The eval whose live runs are recorded in its file; the others say they have not been run.
_RECORDED_EVALS = ("w",)
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|-?\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")


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


def _table(heading: str) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(_section(heading))]
    return rows[2:]


def _names_a_person_or_firm(text: str) -> bool:
    return any(re.search(rf"\b{name}\b", text.lower()) for name in _PEOPLE_AND_FIRMS)


def _calls(text: str) -> list[tuple[str, ScenarioInput]]:
    """Each labelled call of an eval: the scenario its label names, and its inputs, validated by that model."""
    calls: list[tuple[str, ScenarioInput]] = []
    for scenario, body in _LABELLED_CALL.findall(_section("## Expected tool call", text)):
        calls.append((scenario, _INPUT_MODELS[scenario].model_validate(json.loads(body)["inputs"])))
    return calls


def _results(text: str) -> list[ScenarioResult]:
    return [compute(inputs) for _, inputs in _calls(text)]


def _eval(letter: str) -> tuple[str, str, str]:
    """The full text, the unwrapped prompt and the unwrapped expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return text, _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-round-sizing"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "adversarial review", "gives no recommendation", "Not investment advice"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert _NEEDED_TOOLS <= named
    assert named <= served, named - served
    assert "`equity_calculator runway_plan`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-round-sizing skill" in _unwrapped(_section("## When to use it", _POSITIONING))
    assert "the vc-round-sizing skill" in _unwrapped(_section("## When to use it", _DEAL_MATH))


def test_the_json_example_is_a_valid_runway_plan_call() -> None:
    (example,) = _fences("json")

    assert RunwayPlanInput.model_validate(json.loads(example)["inputs"]).scenario == "runway_plan"


async def test_the_command_runs_and_prints_every_line_of_the_excerpt() -> None:
    (command,) = _fences("")
    (excerpt,) = _fences("text")
    assert command.startswith(f"{_PROGRAM}runway_plan ") and "\n" not in command.strip()

    printed = (await run(shlex.split(command)[1:])).splitlines()

    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_command_and_the_json_example_are_the_same_plan() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        RunwayPlanInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    rows = re.findall(r"^\| `([a-z_]+)` +\|", _section("## Flags"), re.MULTILINE)

    assert rows == list(get_args(RunwayPlanFlag))
    assert "never present it as a shortfall" in _unwrapped(_section("## Flags"))


def test_every_ownership_flag_code_carries_its_meaning_in_this_skill() -> None:
    """Over MCP a tool returns bare codes, so the skill carries each deal check code's meaning itself."""
    rows = re.findall(r"^\| `([a-z_]+)` +\|", _section("## Ownership flags"), re.MULTILINE)
    table = _section("## Ownership flags")

    assert rows == list(get_args(DealFlag))
    assert "18 months" not in table and "25%" not in table


def test_the_steps_send_both_runway_claims_and_a_safe_to_the_right_place() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "the top-level `stated_runway_months`" in steps and "that option's `stated_runway_months`" in steps
    assert "`stated_runway_from` set to `landing`" in steps
    assert "The no-raise row is always worked" in steps
    assert "no burn fields" in steps and "never shows two runway figures" in steps
    assert _SAFE_SHARE in steps and "never pass a SAFE as `investment`" in steps
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps
    assert "`slack_months`" in steps and "`start_raising_by`" in steps and "never added or subtracted by hand" in steps
    assert "No recommendation." in steps
    assert "means what this skill's Ownership flags table says (the tool returns codes only)" in steps
    assert "its `dilution_band` row is quoted with its source, flag or not" in steps
    assert "never from the table's text" in steps
    assert "a mismatch, or not checked" in steps and "the answer lists it as not checked" in steps


def test_the_steps_name_the_landing_month_the_reserve_and_the_lean_case() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))
    fields = set(RunwayPlanInput.model_fields) | set(RaiseOption.model_fields) | set(BurnCase.model_fields)

    for name in ("lands_month", "cash_floor", "gross_burn_percent_of_plan", "revenue_percent_of_plan"):
        assert f"`{name}`" in steps and name in fields, name
    assert "a third case named `lean`" in steps and "lean" in get_args(CaseName)
    assert "read the lean rows only for the option the founder ties the plan to, and say so" in steps
    assert "`milestone_short_on_plan` counts the plan case only" in answering
    assert "`lands_month`" in _unwrapped(_section("## Steps")).split("6. **Raise now or wait**")[1]


def test_a_milestone_verdict_says_only_that_the_cash_lasts() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "only that the cash lasts to the milestone month plus the months to raise" in steps
    assert "a milestone is covered only when the slack is at least the months to raise" in steps
    assert _NOT_CHECKED in steps and _NOT_CHECKED in answering
    # An ARR milestone has a tool since the metrics check shipped; only a customer count or a launch has none.
    assert "an ARR target is checked by the vc-metrics-readiness skill" in steps
    assert "an ARR target with the vc-metrics-readiness skill named as where it is checked" in answering
    assert "never converted by hand" in steps and "`milestone_rule`" in answering


def test_every_pattern_cites_a_read_source_the_calculator_or_says_unverified() -> None:
    rows = _table("### Patterns")

    assert len(rows) >= len(_REFUTE_VERDICTS)
    for pattern, _, fix, source in rows:
        assert fix, pattern
        assert source.startswith(_GUIDE) or "unverified" in source.lower(), pattern
    (dilution,) = (row for row in rows if "share of the company sold" in row[0])
    assert "`dilution_band` row of `equity_deal_check`" in dilution[-1]
    # The guide calls "raising for N months" a great answer, so the doubt about it is never cited to the guide.
    (months,) = (row for row in rows if "Raising for N months" in row[0])
    assert months[-1].startswith("Unverified")
    (financials,) = (row for row in rows if "Detailed multi-year financials" in row[0])
    assert "this skill's own, unverified" in financials[-1]


def test_sources_are_only_what_the_repository_has_read() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == _SOURCES_USED
    assert listed <= set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert "this skill's own judgment, unverified" in _unwrapped(_section("## Sources"))


def test_named_people_and_firms_appear_only_as_cited_sources() -> None:
    uncited = _TEXT.replace(_section("## Sources"), "")
    for _, _, _, source in _table("### Patterns"):
        uncited = uncited.replace(source, "")
    uncited = _unwrapped(uncited).replace(_GUIDE, "")

    assert not _names_a_person_or_firm(uncited)


def test_benchmark_figures_reach_the_answer_only_through_the_calculators_rows() -> None:
    prose = [_TEXT] + [
        _section("## Prompt", text) + _section("## Expected answer", text)
        for text in (path.read_text(encoding="utf-8") for path in _EVALS)
    ]

    for text in prose:
        for figure in _FREE_BENCHMARKS:
            assert figure not in text, figure
    assert "`runway_band` row" in _section("## Flags")
    assert "only from the tool's own assumption row" in _unwrapped(_section("## Answering"))


def test_the_skeptic_reads_only_the_material_and_quotes_it() -> None:
    skeptic = _unwrapped(_section("### The skeptic"))
    steps = _unwrapped(_section("## Steps"))
    note = "Without a subagent tool, run the skeptic (Adversarial review) first, before step 1"

    assert not _names_a_person_or_firm(skeptic)
    assert "third person" in skeptic and "do not speak as one" in skeptic
    assert "Read only the founder's material" in skeptic and "do no arithmetic" in skeptic
    assert "quoted word for word" in skeptic and '"nothing found"' in skeptic
    assert _RAISE_IT_ANYWAY in skeptic and "rather than a weak attack" not in skeptic
    assert "run the skeptic as a subagent, however short the material" in skeptic
    assert "only the founder's material, the brief above and the Pattern column below" in skeptic
    assert "run it before step 1" in skeptic and "Say in the answer which way it ran" in skeptic
    assert "Calculator results do not go through the review." in skeptic
    assert "listed ahead of the kept attacks with no tier" in skeptic
    assert "below the tool's figure understates it" in skeptic and "as minor at most" in skeptic
    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")


def test_the_refute_pass_has_the_three_verdicts_and_keeps_what_it_cannot_decide() -> None:
    refute = _unwrapped(_section("### The refute pass"))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "a subagent per attack, all in a single message" in refute and "do no arithmetic" in refute
    assert "never put two attacks in one subagent" in refute
    assert "Only without a subagent tool, take the attacks one at a time" in refute
    assert "asserts a result no tool computed" in refute and "Say in the answer which way the refute pass ran" in refute
    assert "is Kept, grounded even when the material shows evidence" in refute
    assert "applies only while the material lacks that thing" in refute
    assert "the attack is Dropped, answered, quoting that line" in refute
    assert "When you cannot decide, return Kept." in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "word for word" in quotes and "as not grounded" in quotes


def test_every_pattern_row_names_something_said_or_something_missing() -> None:
    """A row the refute pass lists as something said keeps its attack; every other row is answered by the material."""
    refute = _unwrapped(_section("### The refute pass"))
    patterns = [row[0] for row in _table("### Patterns")]

    for said in _SAID_PATTERNS:
        assert said in patterns and f'"{said}"' in refute, said
    for pattern in patterns:
        if pattern not in _SAID_PATTERNS:
            assert any(marker in pattern for marker in _MISSING_MARKERS), pattern


def test_the_answer_leads_with_what_each_amount_buys_and_gives_no_recommendation() -> None:
    answering = _unwrapped(_section("## Answering"))
    limits = _unwrapped(_section("## Limits"))

    assert answering.index("**What each amount buys,**") < answering.index("**Ownership per option:**")
    assert answering.index("**Ownership per option:**") < answering.index("**Adversarial review:**")
    assert "The no-raise row first" in answering and "**Dropped,**" in answering
    assert "not investment, legal or tax advice" in answering
    assert "Not investment, legal or tax advice" in limits
    assert "does not recommend raising now or waiting" in limits
    assert "never role-plays or speaks as a named investor" in limits
    assert "No arithmetic outside the equity calculator's tools" in limits
    assert "no gap to a required raise or difference between two options stated" in limits
    assert "never builds a case the founder did not state" in limits


def test_the_answer_has_required_headings_and_states_no_gap_or_verdict_of_its_own() -> None:
    """A live run computed gaps, merged two cases and wrote its own layout; the text now rules each out."""
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert 'required headings, in this order; write "none"' in answering
    assert "No headline verdict of the skill's own" in answering
    assert '"safe", "works", "fails", "only works", "needs to"' in answering
    assert "the lean rows for the other amounts are left out" in answering
    assert 'never "already passed"' in answering and "never their difference" in answering
    assert "each skeptic attack with its refute verdict" in answering
    assert "Never state the gap between an option's amount and a required raise" in steps
    assert "3745000.00 is $3,745,000.00" in steps and "0.680000 is 68.0000%, never 68%" in steps
    assert "never merge two" in steps and "make no second call" in steps
    assert "[would you cut spend in the downside, and to what?]" in steps
    for check in (
        "a difference, a total, a gap, a remainder",
        "Every case is one the founder named",
        "appears once, with its",
    ):
        assert check in steps, check
    # The re-run's one slip: the skeptic wrote "the other 15%" for a lean plan at 85%, and the answer relayed it.
    assert "the skeptic's relayed text included" in steps and '85% of plan never becomes "the other 15%"' in steps


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name
        if path.name.split("-")[1] in _RECORDED_EVALS:
            assert "## Recorded answer" in text and "is an excerpt of a recorded run" in _unwrapped(text), path.name
            assert text.index("## Expected answer") < text.index("## Recorded answer"), path.name
        else:
            assert "has not been run in a live session" in text, path.name


def test_the_no_call_eval_carries_no_call_or_excerpt() -> None:
    (path,) = _NO_CALL_EVALS
    text = path.read_text(encoding="utf-8")

    assert path.name.startswith("company-z-")
    assert _fences("json", text) == [] and _fences("text", text) == []


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls = _calls(text)
    excerpts = _fences("text", _section("## What the calculator prints (excerpt)", text))

    assert calls and calls[0][0] == "runway_plan"
    assert len(calls) == len(_fences("json", text)) == len(excerpts)
    for result, excerpt in zip(_results(text), excerpts, strict=True):
        printed = [line.rstrip() for line in render_sheet(sheet_for(result)).splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_and_flag_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, months or money figure in the expected answer is a line a report prints, and every flag the runway
    plan returns is named in the answer."""
    text = path.read_text(encoding="utf-8")
    results = _results(text)
    reports = "\n".join(render_sheet(sheet_for(result)) for result in results)
    answer = _unwrapped(_section("## Expected answer", text))
    figures = _PRINTED_FIGURE.findall(answer)
    plan = results[0]

    assert figures
    for figure in figures:
        assert figure in reports, figure
    assert isinstance(plan, RunwayPlanResult)
    assert plan.flags and set(plan.flags) <= set(_FLAG_NAME.findall(answer)), plan.flags


def test_the_two_amounts_eval_runs_ownership_per_option_and_quotes_the_benchmark_from_the_tool() -> None:
    text, _, answer = _eval("w")

    assert [scenario for scenario, _ in _calls(text)] == [
        "runway_plan",
        "deal_check",
        "deal_check",
        "dilution",
        "dilution",
    ]
    assert "Dilution benchmark 25.0000%" in answer and "`dilution_band` row" in answer
    assert "No recommendation" in answer


def test_the_two_amounts_eval_reads_the_lean_plan_for_the_smaller_raise_only() -> None:
    text, prompt, answer = _eval("w")
    plan = _calls(text)[0][1]

    assert isinstance(plan, RunwayPlanInput)
    assert [case.name for case in plan.cases] == ["plan", "downside", "lean"]
    assert "If we only get $3M, we cut spend to 85% of plan" in prompt
    assert (
        "On the founder's lean plan, which is for $3M" in answer and "The lean rows the tool prints for $4M" in answer
    )
    assert "`milestone_short_on_plan` counts the plan case only" in answer


def test_the_two_amounts_eval_leaves_the_arr_figure_unchecked_and_drops_what_the_material_answers() -> None:
    _, prompt, answer = _eval("w")
    answered = ("Downside: revenue comes in at half of plan", "If we only get $3M, we cut spend to 85% of plan")

    assert '"$1M ARR" itself is quoted as stated and not checked' in answer and "vc-metrics-readiness" in answer
    assert '"A revenue milestone with no monthly figure"' in answer
    # A drop can be scored only when the skeptic raises the attack, so it is conditional; no merged case is run.
    assert "If the skeptic raises an attack" in answer and "Dropped, answered" in answer
    assert '"No downside case"' in answer and "no case merges the downside's revenue cut into the lean plan" in answer
    assert "the open asks ask whether spend would also be cut in the downside" in answer
    for line in answered:
        assert line in prompt and f'"{line}"' in answer, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_with_a_call_runs_the_review_after_the_computed_results(path: Path) -> None:
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    assert "Dropped" in answer and _SKEPTIC_RAN in answer


def test_the_wait_eval_lands_the_later_raise_later_and_labels_its_valuation() -> None:
    text, prompt, answer = _eval("x")
    plan = _calls(text)[0][1]

    assert isinstance(plan, RunwayPlanInput)
    assert [option.lands_month for option in plan.raises] == [0, 6]
    assert "now at $8M pre, or wait six months" in prompt
    assert "the founder's assumption" in answer and "What has to be true for waiting to work" in answer
    assert "No recommendation" in answer


def test_the_safe_eval_checks_both_runway_claims_and_makes_no_deal_check() -> None:
    text, _, answer = _eval("y")
    ((_, plan),) = _calls(text)

    assert isinstance(plan, RunwayPlanInput)
    assert plan.stated_runway_months is not None and plan.raises[0].stated_runway_months is not None
    assert _SAFE_SHARE in answer and "`equity_round`" in answer
    assert "does not pass the SAFE to `equity_deal_check`" in answer
    assert not any(case.name == "downside" for case in plan.cases)
    assert "the open asks ask for a downside case" in answer and "picks no percent of its own" in answer
    assert "Adversarial review, after the two computed mismatches" in answer


def test_the_named_firm_eval_declines_the_voice_and_the_growth_rate() -> None:
    _, prompt, answer = _eval("z")

    assert "Sequoia" in prompt and "3x a year" in prompt
    assert "declines to speak as a partner of a named firm" in answer
    assert "labelled as a framework" in answer and "declines to assume a growth rate" in answer
    assert "five intake questions in one message" in answer
    assert "no round size and no recommendation" in answer


def test_the_table_says_what_a_start_raising_by_cell_holds_when_the_tool_printed_none() -> None:
    """With no months to raise the tool prints no start raising by, yet the table requires the column."""
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert (
        'With no months to raise the tool prints no start raising by, so the cell reads "not computed: give'
        in answering
    )
    assert '(with `self_funding`, "not computed: no follow-on round")' in answering
    # Months to raise given, and the row's cash never runs out: the tool prints none either, and the cause differs.
    assert (
        "when the months were given and the row's cash never runs out, the tool also prints none, and the cell reads "
        '"none: the cash never runs out"'
    ) in answering
    assert "or item 2's text for why the tool printed none" in steps


def test_a_case_whose_rows_are_the_plans_is_said_once_and_not_repeated() -> None:
    """A revenue downside on a plan with $0.00 revenue prints the plan's rows again, row for row."""
    answering = _unwrapped(_section("## Answering"))

    assert "A case whose rows are the plan's, row for row as printed" in answering
    assert "\"the downside's rows are the plan's, as printed\", and not repeated" in answering


def test_the_tools_own_difference_row_is_quoted_and_step_ones_list_has_a_heading() -> None:
    """The no-gap rule did not say whether the runway check's printed difference may be quoted, and step 1's quoted
    figures had no heading in the answer."""
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "A difference the tool prints itself (a deck claim's `difference` row, `computed - stated`)" in steps
    assert "not a gap worked by hand: quote it as printed, with its label" in steps
    assert "The list leads Answering item 5" in steps
    assert "**Deck claims:** first step 1's list of what the founder states, word for word" in answering
    assert "(with the tool's own difference row as printed)" in answering
