"""The vc-investor-update skill keeps its shape: its sections, its tie-out, its runway call, its reader pass, its evals.

The skill writes the update a founder sends their current investors. Every calculator tool it names must be a tool the
MCP server serves, and it names one: ``equity_runway_plan``, called with no raise and no milestone. Its JSON example
must be a valid call, its command must run and print every line of the excerpt after it, and the two must be the same
check. Its flag table holds exactly the flags such a call can raise. The update's sections, the tie-out statuses and
the reader pass's four lenses are fixed; the refute verdicts are word for word the repository's; the ranked fix list
has three tiers and no score. Every source is one the skill's authors read in full, and every pattern row cites one of
them or says it is unverified. Each eval in evals/vc-investor-update/ has a prompt, an expected tool call and an
expected answer, and every call is valid and every excerpt is lines of the report that call prints.

Two skills it points to are planned, not yet shipped: sizing the next round (vc-round-sizing) and updates to
prospective investors (vc-founder-update). A test checks that their folders do not exist yet, so the pull request that
adds either one has to turn the planned line here into a hand-off.
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
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag, RunwayPlanInput
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-investor-update" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-investor-update").glob("*.md"))
_EVAL_COUNT = 4
# The repository gives each made-up company its own letter; this skill's evals use AG, AH, AJ and AK (no AI, as the
# repository skips I).
_EVAL_LETTERS = ("ag", "ah", "aj", "ak")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_runway_plan` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_PROGRAM = "equity_calculator "
_HANDOFF_SKILLS = ("vc-claims-check", "vc-deal-math", "equity-calculator", "vc-positioning")
_PLANNED_SKILLS = ("vc-round-sizing", "vc-founder-update")
_PLANNED = "Planned, not yet shipped:"
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "write my investor update",
    "review my investor update before I send it",
    "draft our monthly update",
    "how do I tell investors about a bad month",
    "should I skip this month's update",
)
_SECTIONS = (
    "Summary",
    "Metrics",
    "Highlights",
    "Lowlights",
    "Asks",
    "Cash and runway",
    "Next period",
    "Thanks",
    "Definitions",
)
_STATUSES = ("Same", "Restated", "Different form", "Changed definition", "Dropped", "New")
_LENSES = ("Spin", "Missing bad news", "Definitions", "Tie-out")
_REFUTE_VERDICTS = ("**Dropped, answered:**", "**Dropped, not grounded:**", "**Kept:**")
_TIERS = ("**fix before sending**", "**worth fixing**", "**minor**")
_FLAGS = ("cash_never_runs_out", "start_raising_date_passed")
# The public guides this skill's authors read in full, each with the short name its Source cells use.
_READ_SOURCES = {
    "https://500.co/content/founders-guide-sending-investor-updates": "500 Global guide",
    "https://mercury.com/blog/how-to-write-an-effective-investor-update": "Mercury guide",
    "https://a16z.com/16-startup-metrics/": 'a16z "16 Startup Metrics"',
}
_OURS = "Ours"
_UNVERIFIED = "unverified"
_URL = re.compile(r"https?://\S+")
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = (
    "sequoia",
    "a16z",
    "andreessen",
    "y combinator",
    "yc",
    "graham",
    "dixon",
    "stebbings",
    "20vc",
    "500 global",
    "mercury",
)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_FIX_COLUMNS = re.compile(r"Rank, Tier, Section, Lens, The line \(quoted\), Why an investor\s+reads it that way, Fix")
_TIE_OUT_COLUMNS = "Metric or item, Period, The last update said (quoted), This update says (quoted), Status"
_SCORE = re.compile(r"/\s*100\b|out of 100", re.IGNORECASE)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_NOT_CHECKED = "not checked: no tool computes this"
_CASH_BRIDGE = (
    "[a one-line bridge from the last update's cash to this one's: net burn plus anything else that moved cash]"
)
# A figure an eval's answer takes from the calculator: months with decimals.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+ months")
# How far the flag check reaches: every months-to-raise from 0 to two years on the skill's own example.
_MONTHS_TO_RAISE = range(25)


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


def _table(heading: str, text: str = _TEXT) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    section = _section(heading, text)
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(section)]
    return rows[2:]


def _names_a_person_or_firm(text: str) -> bool:
    return any(re.search(rf"\b{name}\b", text.lower()) for name in _PEOPLE_AND_FIRMS)


def _cites_only_read_sources(cell: str) -> bool:
    """Each ``; ``-separated part of a Source cell names a read source, is ours, or says it is unverified."""
    names = tuple(_READ_SOURCES.values())
    return all(part.startswith((*names, _OURS)) or _UNVERIFIED in part.lower() for part in cell.split("; "))


def _calls(text: str) -> list[RunwayPlanInput]:
    return [RunwayPlanInput.model_validate(json.loads(call)["inputs"]) for call in _fences("json", text)]


def _report(inputs: RunwayPlanInput) -> list[str]:
    return [line.rstrip() for line in render_sheet(sheet_for(compute(inputs))).splitlines()]


def _eval(letter: str) -> tuple[str, str, str]:
    """The whole text, the unwrapped prompt and the unwrapped expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return text, _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-investor-update"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "current investors", "adversarial reader pass", "runway_plan", "Never invents or hides"):
        assert phrase in description, phrase
    # Updates to people who are not yet investors belong to a planned sibling skill, so no such phrasing triggers this.
    assert "prospective" not in description
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert named == {"equity_runway_plan"}
    assert named <= served, named - served
    assert "`equity_calculator runway_plan`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    handoff = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoff, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-investor-update skill" in _unwrapped(_section("## When to use it", _POSITIONING))


def test_the_planned_skills_are_named_as_planned_until_their_folders_exist() -> None:
    handoff = _unwrapped(_section("## When to use it"))
    planned = handoff[handoff.index(_PLANNED) :]

    for name in _PLANNED_SKILLS:
        assert f"(the {name} skill)" in planned, name
        # When the folder lands, move the name out of the planned line into a hand-off and into _HANDOFF_SKILLS.
        assert not (_ROOT / "skills" / name).exists(), name
    assert "Until each ships, say so" in planned
    assert "writes no version for people who are not yet investors" in planned


def test_the_skill_writes_for_current_investors_only() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert "Built for the founder's current investors" in _unwrapped(_section("## When to use it"))
    assert "It writes for current investors only" in limits
    assert "prospect version" not in _TEXT.lower()
    assert "## Current and prospective investors" not in _TEXT


def test_the_json_example_is_a_valid_runway_plan_call_with_no_raise_or_milestone() -> None:
    (example,) = _fences("json")
    inputs = RunwayPlanInput.model_validate(json.loads(example)["inputs"])

    assert inputs.scenario == "runway_plan"
    assert inputs.raises == () and inputs.milestones == ()
    assert [case.name for case in inputs.cases] == ["plan"]
    assert inputs.stated_runway_months is not None


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
        RunwayPlanInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_the_flag_table_holds_exactly_the_flags_a_no_raise_call_can_raise() -> None:
    rows = tuple(row[0].strip("`") for row in _table("## Runway"))
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]
    raised: set[str] = set()
    for months in _MONTHS_TO_RAISE:
        call = RunwayPlanInput.model_validate({**inputs, "months_to_raise": months})
        raised |= set(compute(call).flags)
    # Revenue that covers the spend from month 1: the cash never runs out.
    covered = {**inputs, "cases": [{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "1", "revenue": "2"}]}]}
    raised |= set(compute(RunwayPlanInput.model_validate(covered)).flags)

    assert rows == _FLAGS
    assert set(rows) <= set(get_args(RunwayPlanFlag))
    assert raised == set(_FLAGS)
    assert "With no raise and no milestone in the call, the tool raises no other flag" in _unwrapped(
        _section("## Runway")
    )


def test_the_runway_call_takes_one_call_and_names_the_flat_spend_case() -> None:
    runway = _unwrapped(_section("## Runway"))

    assert "No `raises` and no `milestones`" in runway
    assert "One call for the update" in runway and "Make no other call the founder did not ask for" in runway
    assert '"today\'s spend held flat"' in runway
    assert 'a "30+ months" claim is passed as `"30"`' in runway
    assert "12.79 months stays 12.79 months" in runway and "never round again or recompute" in runway


def test_the_update_shape_is_the_fixed_sections_each_with_a_read_source_or_ours() -> None:
    rows = _table("## The update's shape")

    assert tuple(row[0] for row in rows) == _SECTIONS
    for section, _, source in rows:
        assert _cites_only_read_sources(source), section
    assert "The Definitions block is this skill's own addition, unverified" in _unwrapped(
        _section("## The update's shape")
    )


def test_the_tie_out_statuses_are_the_fixed_words_and_compare_as_stated() -> None:
    tie_out = _unwrapped(_section("## Tying out to the last update"))

    assert tuple(row[0] for row in _table("## Tying out to the last update")) == _STATUSES
    assert "The same metric, in the same form, for a period both updates give" in tie_out
    assert "whether one is larger may be said, never by how much" in tie_out
    assert "The last update's own promises are tied out too" in tie_out
    assert _NOT_CHECKED in tie_out
    assert f"`{_CASH_BRIDGE}`" in tie_out
    assert "Never convert one into the other" in _unwrapped(_section("## Metrics and their definitions"))
    assert "Growth rates are quoted, never computed" in _unwrapped(_section("## Metrics and their definitions"))


def test_the_lenses_are_the_four_and_name_no_person_or_firm() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = tuple(row[0] for row in _table("### Stage A: attack"))

    assert lenses == _LENSES
    for lens in lenses:
        assert not _names_a_person_or_firm(lens), lens
    for rule in (
        "Write in the third person",
        "do no arithmetic",
        "quoted word for word with its place",
        "the material's line the draft omits",
        "raise it anyway, and the refute pass decides",
        'Return "nothing found" only when',
        "less independent than subagents",
        "do not go through the lenses or the refute pass",
    ):
        assert rule in attack, rule
    assert "rather than a weak objection" not in attack


def test_without_a_subagent_tool_the_lenses_run_before_step_1_in_review_mode() -> None:
    steps = _unwrapped(_section("## Steps"))
    note = "In review mode without a subagent tool, run Stage A of the reader pass first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    assert "Say whether the lenses ran as subagents" in _unwrapped(_section("## Answering"))


def test_the_refute_pass_uses_only_the_founders_material() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in brief, verdict
    assert "one subagent per objection" in handoff and "the Pattern column of the table below" in handoff
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "Bring in no outside fact, and do no arithmetic",
        "How an investor is likely to read a line is not an outside fact",
        "never answers an objection",
        "When you cannot decide, return Kept",
        "invents nothing on the founder's behalf",
        "is the objected line itself, does not drop the objection",
    ):
        assert rule in brief, rule
    assert "word for word" in quotes and "dropped as not grounded" in quotes
    assert "| Pattern" in _section("## Patterns that cost trust")


def test_the_ranked_fix_list_has_the_three_tiers_and_no_score() -> None:
    ranked = _unwrapped(_section("### The ranked fix list"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    assert "The calculator's mismatches lead the first tier" in ranked
    assert "a Restated or Dropped status with no word in the draft goes in it too" in ranked
    assert "give no percentages and no score" in ranked
    assert _FIX_COLUMNS.search(answering) and "**Dropped,**" in answering
    assert _TIE_OUT_COLUMNS in answering
    assert "not investment, legal or tax advice" in answering
    assert not _SCORE.search(_TEXT)


def test_every_pattern_row_cites_a_read_source_or_says_unverified() -> None:
    rows = _table("## Patterns that cost trust")

    for row in rows:
        assert _cites_only_read_sources(row[-1]), row[0]
    unverified = [row[0] for row in rows if row[-1] == "Unverified"]
    assert any("next month" in pattern for pattern in unverified)
    assert any("runway" in pattern for pattern in unverified)
    # The ask row's source backs asks for introductions, not how specific they are; the row says so.
    (ask,) = (row for row in rows if row[0].startswith("An ask"))
    assert ask[-1] == "Mercury guide (asks); specificity unverified"


def test_sources_are_the_read_set() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert "this skill's own judgment, unverified" in _unwrapped(_section("## Sources"))
    assert "frameworks, not voices" in _unwrapped(_section("## Sources"))


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
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls, excerpts = _calls(text), _fences("text", text)

    assert calls and len(calls) == len(excerpts)
    for call, excerpt in zip(calls, excerpts, strict=True):
        assert call.raises == () and call.milestones == ()
        printed = _report(call)
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A months figure with decimals in the expected answer is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    reports = "\n".join("\n".join(_report(call)) for call in _calls(text))
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in reports, figure


def test_one_eval_calls_again_with_todays_spend_held_flat() -> None:
    text, _, answer = _eval("ag")
    plan, flat = _calls(text)

    assert len(plan.cases[0].phases) > 1
    assert flat.cases[0].phases == plan.cases[0].phases[:1]
    assert flat.cash_on_hand == plan.cash_on_hand and flat.stated_runway_months == plan.stated_runway_months
    assert compute(plan).verdict == "mismatch"
    assert "15.07 months at today's spend held flat" in answer
    assert "We hired one engineer, not two; the second candidate declined." in answer


def test_one_eval_drops_an_objection_by_quoting_the_drafts_own_line() -> None:
    _, prompt, answer = _eval("ah")
    objection, dropped = answer.split("Dropped, answered", 1)
    answering_line = _DOUBLE_QUOTED.findall(dropped)[0]

    assert answering_line in prompt
    assert answering_line not in _DOUBLE_QUOTED.findall(objection)
    assert "Restated" in answer and "Changed definition" in answer
    assert _NOT_CHECKED in answer


def test_one_eval_keeps_a_lowlight_the_founder_asked_to_hide() -> None:
    _, prompt, answer = _eval("aj")
    lowlight = "our biggest customer churned in August"

    assert lowlight in prompt and f'("{lowlight}")' in answer
    assert 'It does not write "revenue grew 30%"' in answer and "that is a target, not a result" in answer
    for path in _EVALS:
        assert "Customer Q" not in path.read_text(encoding="utf-8"), path.name


def test_one_eval_declines_a_named_firm_and_a_version_for_prospects() -> None:
    text, prompt, answer = _eval("ak")
    (call,) = _calls(text)

    assert "Sequoia" in prompt and "VCs we're warming up" in prompt
    assert "declines in one line to write as a partner of a named firm" in answer
    assert "a planned skill that has not shipped" in answer and "It writes no second version" in answer
    assert '"30+ months of runway." leads the fix list in the fix before sending tier' in answer
    assert str(call.stated_runway_months) == "30" and compute(call).verdict == "mismatch"
    assert "Lowlights: our VP Sales left in August." in answer
