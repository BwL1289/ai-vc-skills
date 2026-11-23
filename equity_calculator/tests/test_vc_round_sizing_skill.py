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
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag, RunwayPlanInput, RunwayPlanResult
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-round-sizing" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
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
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator", "vc-positioning", "vc-claims-check")
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


def test_every_pattern_cites_a_read_source_the_calculator_or_says_unverified() -> None:
    rows = _table("### Patterns")

    assert len(rows) >= len(_REFUTE_VERDICTS)
    for pattern, _, fix, source in rows:
        assert fix, pattern
        assert source.startswith(_GUIDE) or "unverified" in source.lower(), pattern
    (dilution,) = (row for row in rows if "share of the company sold" in row[0])
    assert "`dilution_band` row of `equity_deal_check`" in dilution[-1]


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
    assert "only the founder's material, the brief above and the Pattern column below" in skeptic
    assert "run it before step 1" in skeptic and "Say in the answer which way it ran" in skeptic
    assert "Calculator results do not go through the review." in skeptic
    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")


def test_the_refute_pass_has_the_three_verdicts_and_keeps_what_it_cannot_decide() -> None:
    refute = _unwrapped(_section("### The refute pass"))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "a subagent per attack" in refute and "do no arithmetic" in refute
    assert "is Kept, grounded even when the material shows evidence" in refute
    assert "When you cannot decide, return Kept." in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "word for word" in quotes and "as not grounded" in quotes


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


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "has not been run in a live session" in text, path.name


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


def test_the_named_firm_eval_declines_the_voice_and_the_growth_rate() -> None:
    _, prompt, answer = _eval("z")

    assert "Sequoia" in prompt and "3x a year" in prompt
    assert "declines to speak as a partner of a named firm" in answer
    assert "labelled as a framework" in answer and "declines to assume a growth rate" in answer
    assert "five intake questions in one message" in answer
    assert "no round size and no recommendation" in answer
