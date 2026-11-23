"""The vc-prospective-investor-update skill keeps its shape: the line, promises, names, runway call and evals.

The skill writes the short update a founder sends the investors they hope to raise from, before the raise. Every
calculator tool it names must be a tool the MCP server serves, and it names one: ``equity_runway_plan``, called with no
raise and no milestone, and only when the update shows a runway. Its JSON example must be a valid call, its command must
run and print every line of the excerpt after it, and the two must be the same check. Its flag table holds exactly the
flags such a call can raise, and a runway claim stated as a floor ("30+ months") is judged by the printed runway.

The metric rules and the six metric status words live in one file the vc-current-investor-update skill keeps,
``skills/vc-current-investor-update/references/metric-consistency.md``, which this skill reads in place. Three guards
hold that read: the skill's fallback when the file is missing (never the rules from memory), a sentence in
docs/install.md (not yet added) and the coupling test below, which checks the link resolves, the status words this
skill names are the file's, no line of the file is copied here, and the promise statuses live here only.

The update's sections, the line table, the promise statuses, the names rule and the reader pass's four lenses are
fixed; the refute verdicts are word for word the repository's; the ranked fix list has three tiers and no score. Every
source is one the skill's authors read in full, and every pattern row cites one of them or says it is unverified. Each
eval in evals/vc-prospective-investor-update/ has a prompt, an expected tool call and an expected answer, every call is
valid and every excerpt is lines of the report that call prints.

One skill it points to is planned, not yet shipped: whether a metric's definition is the expected one
(vc-metrics-readiness). A test checks that its folder does not exist yet, so the pull request that adds it, or rebases
this one onto it, has to turn the planned line into a hand-off.
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
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag, RunwayPlanInput, RunwayPlanResult
from equity_calculator.text import render_sheet
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[2]
_FOLDER = _ROOT / "skills" / "vc-prospective-investor-update"
_TEXT = (_FOLDER / "SKILL.md").read_text(encoding="utf-8")
_SIBLING = (_ROOT / "skills" / "vc-current-investor-update" / "SKILL.md").read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
# The shared rules file, read in place from the sibling's folder; the link is relative to this skill's folder.
_RULES_LINK = "../vc-current-investor-update/references/metric-consistency.md"
_RULES_PATH = _ROOT / "skills" / "vc-current-investor-update" / "references" / "metric-consistency.md"
_RULES = _RULES_PATH.read_text(encoding="utf-8")
_FALLBACK_STATUS = "`[not tied out: the shared rules file is missing]`"
_EVALS = sorted((_ROOT / "evals" / "vc-prospective-investor-update").glob("*.md"))
_EVAL_COUNT = 4
# The repository gives each made-up company its own letter; this skill's evals use BE to BH.
_EVAL_LETTERS = ("be", "bf", "bg", "bh")
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
_HANDOFF_SKILLS = (
    "vc-current-investor-update",
    "vc-claims-check",
    "vc-positioning",
    "vc-round-sizing",
    "vc-metrics-readiness",
)
_PLANNED = "Planned, not yet shipped:"
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "write an update for the VCs we're warming up",
    "draft my monthly update to prospective investors",
    "keep investors warm before our raise",
    "review my prospect update",
)
_SECTIONS = (
    "Where we are",
    "The line",
    "Last time we said",
    "Highlights",
    "Lowlights",
    "By the next update",
    "One ask",
    "Cash and runway, optional",
    "Definitions",
)
_METRIC_STATUSES = ("Same", "Restated", "Different form", "Changed definition", "Dropped", "New")
_PROMISE_STATUSES = ("Done", "Partly done", "Not done", "Moved", "No word", "Not yet due")
# What the update does for each metric status: the shared file says when each applies, this skill what the update does.
_STATUS_ACTIONS = {
    "Same": "nothing more; this period's value sits beside the earlier ones",
    "Restated": (
        "the earlier update's cell stays as stated, and the restated value goes beside it, labelled restated, "
        "with the reason (`[why it changed]`)"
    ),
    "Different form": (
        "the line keeps the last update's form and asks for this period's figure in it, or how the two lines relate"
    ),
    "Changed definition": (
        "the Definitions block shows both labels and both definitions; the two are never compared or converted"
    ),
    "Dropped": "the metric stays in the line, or the update says it is dropped and why",
    "New": "a new row, with its definition in the Definitions block",
}
_DIFFERS = "Differs from the current-investor update"
_LENSES = ("Spin", "Moved goalposts", "Changed definitions", "Unreported promise")
_REFUTE_VERDICTS = ("**Dropped, answered:**", "**Dropped, not grounded:**", "**Kept:**")
_TIERS = ("**fix before sending**", "**worth fixing**", "**minor**")
_FLAGS = ("cash_never_runs_out", "start_raising_date_passed")
# The public pages this skill's authors read in full, each with the short name its Source cells use.
_READ_SOURCES = {
    "https://medium.com/both-sides-of-the-table/invest-in-lines-not-dots-611f36491d73": "Suster post",
    "https://500.co/content/founders-guide-sending-investor-updates": "500 Global guide",
    "https://mercury.com/blog/how-to-write-an-effective-investor-update": "Mercury guide",
}
_OURS = ("Ours", "The shared rules file")
_UNVERIFIED = "unverified"
_URL = re.compile(r"https?://\S+")
# Names that may appear only in Sources and in Source cells: the skill tests frameworks, never people or firms.
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
    "suster",
    "500 global",
    "mercury",
)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_FIX_COLUMNS = re.compile(r"Rank, Tier, Section, Lens, The line \(quoted\), Why an investor reads\s+it that way, Fix")
_TIE_OUT_COLUMNS = "Metric or item, Period, The last update said (quoted), This update says (quoted), Status"
_SCORE = re.compile(r"/\s*100\b|out of 100", re.IGNORECASE)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
# Strings an eval's answer quotes that are the skill's own section names, not lines of the founder's material.
_SKILL_MARKS = {"Last time we said", "By the next update"}
# A figure an eval's answer takes from the calculator: months with decimals.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+ months")
_NEVER_RUNS_OUT = "the cash never runs out"
# How far the flag check reaches: every months-to-raise from 0 to two and a half years on the skill's own example.
_MONTHS_TO_RAISE = range(31)
# A "30+ months" claim, passed as 30, against a runway the tool puts above it (a mismatch, yet the claim holds) and one
# within its tolerance below it (consistent, yet the claim does not hold): money as strings, one phase from month 1.
_FLOOR = 30
_FLOOR_ABOVE = ("4000000", "210000", "95000")
_FLOOR_JUST_BELOW = ("2950000", "100000", "0")
# An exact claim rounded down: the tool prints a mismatch, though the claim is below its runway and overstates nothing.
_EXACT_BELOW = ("3000000", "200000", "92000", "27")
# An eval answer that says this is the first update says so because its prompt does.
_FIRST_UPDATE = re.compile(r"This is the first (?:prospect )?update")


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


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip()[1:-1].split("|")]


def _table(heading: str, text: str = _TEXT) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    rows = [_cells(match.group(0)) for match in _TABLE_ROW.finditer(_section(heading, text))]
    return rows[2:]


def _cites_only_read_sources(cell: str) -> bool:
    """Each ``; ``-separated part of a Source cell names a read source, is ours, or says it is unverified."""
    names = (*_READ_SOURCES.values(), *_OURS)
    return all(part.startswith(names) or _UNVERIFIED in part.lower() for part in cell.split("; "))


def _without_sources_and_source_cells(text: str) -> str:
    """``text`` with its Sources section taken out, and the Source column of each table that has one."""
    start = text.index("\n## Sources\n")
    end = text.index("\n## ", start + 1)
    kept, source_column = [], False
    for line in (text[:start] + text[end:]).splitlines():
        if not line.startswith("|"):
            source_column = False
            kept.append(line)
            continue
        cells = _cells(line)
        if not source_column and cells[-1] == "Source":
            source_column = True
        kept.append(" | ".join(cells[:-1] if source_column else cells))
    return "\n".join(kept)


def _names_a_person_or_firm(text: str) -> str | None:
    return next((name for name in _PEOPLE_AND_FIRMS if re.search(rf"\b{re.escape(name)}\b", text.lower())), None)


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

    assert fields["name"] == "vc-prospective-investor-update" == _FOLDER.name
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "a line of progress", "one ask", "runway_plan", "names the founder supplies"):
        assert phrase in description, phrase
    assert "Never invents or hides numbers" in description
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    # A runway with no raise goes to runway_plan; deal_check refuses a raise of 0, so it is never named.
    assert named == {"equity_runway_plan"}
    assert named <= served, named - served
    assert "`equity_calculator runway_plan`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_points_back() -> None:
    handoff = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoff, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-prospective-investor-update skill" in _unwrapped(_section("## When to use it", _POSITIONING))
    assert "the vc-prospective-investor-update skill" in _unwrapped(_section("## When to use it", _SIBLING))


def test_no_hand_off_is_left_planned_and_the_runway_call_stays_plain() -> None:
    handoff = _unwrapped(_section("## When to use it"))

    assert _PLANNED not in _TEXT
    assert "keeps a definition the same over time without judging it" in handoff
    assert "This skill's runway call carries no raise and no milestone" in handoff


def test_the_shared_rules_file_is_read_in_place_with_its_guards() -> None:
    shared = _unwrapped(_section("## The shared rules for metrics"))
    named = re.search(r"the six metric statuses \(([^)]+)\)", shared)
    rule_lines = [line for line in _RULES.splitlines() if line.startswith(("| ", "- ")) and not line.startswith("| -")]

    # The link resolves from this skill's folder to the one file; the plugin installs both folders side by side.
    assert f"[`{_RULES_LINK}`]({_RULES_LINK})" in _TEXT
    assert (_FOLDER / _RULES_LINK).resolve() == _RULES_PATH.resolve()
    assert "vc-prospective-investor-update" in _RULES.split("\n## ", 1)[0]
    # The status words this skill names are exactly the file's, in its order.
    assert named is not None
    assert tuple(word.strip() for word in named.group(1).replace(" and ", ", ").split(", ")) == _METRIC_STATUSES
    assert tuple(row[0] for row in _table("## Metric statuses", _RULES)) == _METRIC_STATUSES
    # One home: no rule or status row of the file is copied here.
    assert rule_lines
    for line in rule_lines:
        assert line not in _TEXT, line
    # The runtime fallback: say so, name the folder, quote values, never the rules from memory.
    for rule in (
        "This skill keeps no copy",
        "If the file is not there (the vc-current-investor-update folder was not installed), say so in one line",
        "name the folder to add",
        "never write the rules or what each status means from memory",
    ):
        assert rule in shared, rule
    assert _FALLBACK_STATUS in shared
    # The promise statuses are this skill's own: here, and not in the shared file.
    promises = _section("## Last time we said")
    for status in _PROMISE_STATUSES:
        assert f"**{status}**" in promises, status
        assert not re.search(rf"\b{status}\b", _RULES), status


def test_the_json_example_is_a_valid_runway_plan_call_with_no_raise_or_milestone() -> None:
    (example,) = _fences("json")
    inputs = RunwayPlanInput.model_validate(json.loads(example)["inputs"])

    assert inputs.scenario == "runway_plan"
    assert inputs.raises == () and inputs.milestones == ()
    assert [case.name for case in inputs.cases] == ["plan"]
    assert inputs.stated_runway_months is not None
    assert isinstance(json.loads(example)["inputs"]["months_to_raise"], int)


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


def _floor_call(cash: str, gross_burn: str, revenue: str, stated: str = str(_FLOOR)) -> RunwayPlanResult:
    phase = {"from_month": 1, "gross_burn": gross_burn, "revenue": revenue}
    inputs = {"cash_on_hand": cash, "cases": [{"name": "plan", "phases": [phase]}], "stated_runway_months": stated}
    result = compute(RunwayPlanInput.model_validate(inputs))
    assert isinstance(result, RunwayPlanResult)
    return result


def test_a_claim_stated_as_a_floor_is_judged_by_the_printed_runway_not_the_verdict() -> None:
    runway = _unwrapped(_section("## Runway"))
    above, just_below = _floor_call(*_FLOOR_ABOVE), _floor_call(*_FLOOR_JUST_BELOW)

    # The tool's check is two-sided, so its verdict gets both cases wrong for a floor; the skill's rule gets them right.
    assert above.verdict == "mismatch" and above.checks[0].computed.rounded >= _FLOOR
    assert just_below.verdict == "consistent" and just_below.checks[0].computed.rounded < _FLOOR
    for rule in (
        "**A claim stated as a floor**",
        "the tool's verdict row does not decide it",
        "A printed runway at or above the number keeps the claim",
        "it goes in no tier",
        "A printed runway below the number is a fix before sending, even when the verdict row says consistent",
        "A mismatch on an exact claim is a figure to fix before sending, never softened, when the claim is above the "
        "printed runway",
    ):
        assert rule in runway, rule
    assert "neither does a printed runway below a claim stated as a floor" in _unwrapped(
        _section("### Stage A: attack")
    )


def test_an_exact_claim_below_the_printed_runway_is_minor_and_a_consistent_one_may_stay() -> None:
    runway = _unwrapped(_section("## Runway"))
    *plan, stated = _EXACT_BELOW
    below = _floor_call(*plan, stated=stated)

    # Rounded down, the claim overstates nothing, yet the tool's two-sided check calls it a mismatch.
    assert below.verdict == "mismatch" and below.checks[0].computed.rounded > int(stated)
    for rule in (
        "A mismatch with the claim below the printed runway understates it",
        "it goes in the minor tier at most",
        "An exact claim the verdict row calls consistent may stay as the founder wrote it, and the Numbers section "
        "gives the printed runway",
    ):
        assert rule in runway, rule
    assert "A mismatch with the claim below the printed runway goes in the minor tier at most" in _unwrapped(
        _section("### Stage A: attack")
    )


async def test_every_months_figure_in_the_runway_prose_is_one_the_command_prints() -> None:
    (command,) = _fences("")
    printed = await run(shlex.split(command)[1:])
    figures = _PRINTED_FIGURE.findall(_unwrapped(_FENCE.sub("", _section("## Runway"))))

    assert figures
    for figure in figures:
        assert figure in printed, figure


def test_the_runway_is_optional_and_its_inputs_say_how_to_pass_what_the_tool_refuses() -> None:
    runway = _unwrapped(_section("## Runway"))
    (example,) = _fences("json")
    late_start = json.loads(example)["inputs"]
    late_start["cases"][0]["phases"][0]["from_month"] = 2

    with pytest.raises(ValidationError):
        RunwayPlanInput.model_validate(late_start)
    with pytest.raises(ValidationError):
        RunwayPlanInput.model_validate({**json.loads(example)["inputs"], "months_to_raise": "6"})
    for net_burn in ("0", "-5000"):
        no_burn = json.loads(example)["inputs"]
        no_burn["cases"][0]["phases"][0].update(gross_burn=net_burn, revenue="0")
        with pytest.raises(ValidationError):
            RunwayPlanInput.model_validate(no_burn)
    for rule in (
        "Whether an update to prospects shows runway is the founder's choice",
        "with no runway in it, this skill asks for no cash or burn",
        "A refusal is the answer for those inputs: relay its reason",
        "call without it and quote the founder's words beside the tool's result; never turn those words into a figure",
        "a whole number, as a JSON integer, never a string",
        'A range ("4 to 6 months") is asked about once',
        "When the founder gives only net burn, ask for spend and revenue",
        "A net burn of zero or less gets no call until spend and revenue are given",
        "When the founder gives cash collected rather than revenue, pass that and say so",
        "That figure is for the founder; it goes in the update only if they want it there",
        "No `raises` and no `milestones`",
        "One call for the update, and none the founder did not ask for",
        "23.64 months stays 23.64 months",
        "never round again or recompute",
    ):
        assert rule in runway, rule


def test_the_flag_table_holds_exactly_the_flags_a_no_raise_call_can_raise() -> None:
    rows = tuple(row[0].strip("`") for row in _table("## Runway"))
    answers = {row[0].strip("`"): row[-1] for row in _table("## Runway")}
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]
    raised: set[str] = set()
    for months in _MONTHS_TO_RAISE:
        raised |= set(compute(RunwayPlanInput.model_validate({**inputs, "months_to_raise": months})).flags)
    # Revenue that covers the spend from month 1: the cash never runs out.
    covered = {**inputs, "cases": [{"name": "plan", "phases": [{"from_month": 1, "gross_burn": "1", "revenue": "2"}]}]}
    raised |= set(compute(RunwayPlanInput.model_validate(covered)).flags)

    assert rows == _FLAGS
    assert set(rows) <= set(get_args(RunwayPlanFlag))
    assert raised == set(_FLAGS)
    assert "no runway figure; a stated one is not checked" in answers["cash_never_runs_out"]
    assert "outside the update" in answers["start_raising_date_passed"]
    assert "With no raise and no milestone in the call, the tool raises no other flag" in _unwrapped(
        _section("## Runway")
    )


def test_the_update_shape_is_the_fixed_sections_each_with_a_read_source_or_ours() -> None:
    rows = _table("## The update's shape")
    shape = _unwrapped(_section("## The update's shape"))

    assert tuple(row[0] for row in rows) == _SECTIONS
    for section, _, source in rows:
        assert _cites_only_read_sources(source), section
    assert {row[0]: row[2] for row in rows}["Definitions"] == "The shared rules file"
    assert "this skill's own judgment, unverified" in shape


def test_the_line_shows_every_earlier_value_as_stated_and_computes_nothing() -> None:
    line = _unwrapped(_section("## The line"))

    for rule in (
        "At most the last six columns",
        "always the first update's column",
        '"not reported"',
        '"no update sent"',
        "**No arithmetic.**",
        "no chart drawn from the figures",
        "not in the update itself",
        "**A metric is never removed**",
        "the two are never compared or converted",
    ):
        assert rule in line, rule
    # Every metric status says what the update does, in the shared file's order.
    assert tuple(_STATUS_ACTIONS) == _METRIC_STATUSES
    for status, action in _STATUS_ACTIONS.items():
        assert f"**{status}:** {action}" in line, status


def test_only_the_last_updates_promises_get_a_status_and_the_skill_never_decides_one() -> None:
    promises = _unwrapped(_section("## Last time we said"))

    for rule in (
        "The skill never decides that something was done",
        "It never ships",
        "No word** is an item the founder's draft does not mention at all, even when the notes say what happened",
        "Only the last update's items get a status",
        "the reader pass's Unreported promise lens finds it",
        "not a forecast of metrics",
        'The first update has no "Last time we said" section',
    ):
        assert rule in promises, rule


def test_the_names_are_the_founders_and_stay_out_of_the_update() -> None:
    names = _unwrapped(_section("## The names"))

    for rule in (
        "adds none",
        "It never adds, suggests, ranks, scores or researches an investor or a firm, finds an email address",
        '"Goes to"',
        "any name that appears twice marked",
        "No name on the list appears in the update itself, except in a thanks the founder says that person agreed to",
        "No other investor is named or hinted at either",
    ):
        assert rule in names, rule
    assert "no investor named in the update, except in a thanks the founder says that person agreed to" in _unwrapped(
        _section("## Steps")
    )
    assert "**Goes to:**" in _section("## Answering")
    assert "never adds, ranks or researches one" in _unwrapped(_section("## Limits"))


def test_the_lenses_are_the_four_and_name_no_person_or_firm() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = tuple(row[0] for row in _table("### Stage A: attack"))

    assert lenses == _LENSES
    for lens in lenses:
        assert _names_a_person_or_firm(lens) is None, lens
    for rule in (
        "Write in the third person",
        "do no arithmetic",
        "quoted word for word with its place",
        "the earlier update's or the notes' line the draft omits",
        "raise it anyway, and the refute pass decides",
        'Return "nothing found" only when',
        "less independent than subagents",
        "do not go through the lenses or the refute pass",
    ):
        assert rule in attack, rule
    assert "rather than a weak objection" not in attack


def test_the_reader_pass_judges_the_founders_draft_as_given_in_review_mode() -> None:
    steps = _unwrapped(_section("## Steps"))
    note = "In review mode without a subagent tool, run Stage A of the reader pass first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    assert "In review mode, both its stages read the founder's draft as given, never the revised one" in steps
    assert "a line this skill adds at step 8 answers no objection" in steps
    assert "the founder's draft as given in review mode" in steps
    assert "the draft it judges (Steps)" in _unwrapped(_section("### Stage A: attack"))
    assert "a line this skill added at step 8 is not in it" in _unwrapped(_section("### Stage B: refute"))
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
        "**Dropped, answered:** a line of the draft given here, other than the objected line",
        "invents nothing on the founder's behalf",
        "is the objected line itself, does not drop the objection",
        # An earlier disclosure to the same readers answers an objection about an earlier update, and only what it said.
        "may also be answered by a later update sent to these same investors, after the one the objection quotes",
        "quoting the line word for word with its update and date",
        "It answers only what it said",
        "in the draft or in such a later update",
    ):
        assert rule in brief, rule
    assert "word for word" in quotes and "dropped as not grounded" in quotes
    assert "| Pattern" in _section("## Patterns that cost a prospect's trust")


def test_the_ranked_fix_list_has_the_three_tiers_and_no_score() -> None:
    ranked = _unwrapped(_section("### The ranked fix list"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    assert "The calculator's mismatches lead the first tier" in ranked
    assert (
        "a Dropped or Restated metric status, or a last-time item with no line in the founder's draft (No word, "
        "whatever the notes say), goes in it too" in ranked
    )
    assert "takes the lens names of any kept objection about the same line, and is not listed twice" in ranked
    assert "though a mismatch with the claim below the printed runway is minor at most (Runway)" in ranked
    assert "give no percentages and no score" in ranked
    assert _FIX_COLUMNS.search(answering) and "**Dropped,**" in answering
    assert _TIE_OUT_COLUMNS in answering
    assert "not investment, legal or tax advice" in answering
    assert "a lawyer should look at an update that mentions a coming raise" in answering
    assert not _SCORE.search(_TEXT)


def test_every_pattern_row_cites_a_read_source_or_says_unverified() -> None:
    rows = _table("## Patterns that cost a prospect's trust")
    by_pattern = {row[0]: row for row in rows}

    for row in rows:
        assert _cites_only_read_sources(row[-1]), row[0]
    # The rows this skill shares with vc-current-investor-update keep that skill's reviewed reason and source.
    assert by_pattern["A metric from an earlier update missing now"][1:2] == [
        "The picture over time stops being consistent and predictable"
    ]
    assert by_pattern["A metric from an earlier update missing now"][-1] == "Mercury guide (performance)"
    (target,) = (row for row in rows if row[0].startswith("A target written as a result"))
    assert target[-1] == "Mercury guide (next month); target as result unverified"
    (adjectives,) = (row for row in rows if row[0].startswith("A summary of adjectives"))
    assert adjectives[-1] == "Mercury guide (introduction); pattern and reason unverified"
    for pattern in ("Other investors named or hinted at", "A figure that differs from this period's update"):
        (row,) = (row for row in rows if row[0].startswith(pattern))
        assert row[-1] == "Unverified", pattern


def test_sources_are_the_read_set_and_no_one_is_named_outside_them() -> None:
    listed = set(_URL.findall(_section("## Sources")))
    sources = _unwrapped(_section("## Sources"))
    answers = [_section("## Expected answer", path.read_text(encoding="utf-8")) for path in _EVALS]

    assert listed == set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert not _URL.search(_RULES)
    assert "frameworks, not voices" in sources and "this skill's own judgment, unverified" in sources
    assert "is about meeting potential investors early, not written updates, and is from 2010" in sources
    assert "The metric rules and the Definitions block come from the shared rules file" in sources
    assert "not re-read for this one, so here they are unverified" in sources
    for text in (_without_sources_and_source_cells(_TEXT), *answers):
        assert _names_a_person_or_firm(text) is None, _names_a_person_or_firm(text)


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
    assert [path.name.split("-")[1] for path in _NO_CALL_EVALS] == ["bf"]
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls, excerpts = _calls(text), _fences("text", text)

    assert len(calls) == len(excerpts) == 1
    for call, excerpt in zip(calls, excerpts, strict=True):
        assert call.raises == () and call.milestones == ()
        printed = _report(call)
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A months figure with decimals in the expected answer, or a runway with no end, is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    reports = "\n".join("\n".join(_report(call)) for call in _calls(text))
    answer = _unwrapped(_section("## Expected answer", text))
    figures = _PRINTED_FIGURE.findall(answer)

    assert figures or (_NEVER_RUNS_OUT in answer and _NEVER_RUNS_OUT in reports)
    for figure in figures:
        assert figure in reports, figure


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_every_line_an_eval_answer_quotes_is_in_its_prompt_or_is_a_mark_of_the_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))

    for quoted in _DOUBLE_QUOTED.findall(_unwrapped(_section("## Expected answer", text))):
        assert quoted in prompt or quoted in _SKILL_MARKS, quoted


def test_one_eval_drops_an_objection_by_quoting_the_drafts_own_line_and_keeps_a_moved_target() -> None:
    text, prompt, answer = _eval("be")
    (call,) = _calls(text)
    objection, dropped = answer.split("Dropped, answered", 1)
    answering_line = _DOUBLE_QUOTED.findall(dropped)[0]

    assert answering_line in prompt and answering_line not in _DOUBLE_QUOTED.findall(objection)
    assert "Changed definition" in answer and "The two figures are never compared" in answer
    assert 'Moved goalposts, Kept, fix before sending: "Target: $60,000 MRR by December."' in answer
    assert "Partly done" in answer and "is Done" in answer and "it gets no status" in answer
    assert '"Alex (seed fund)" marked as listed twice' in answer
    assert str(call.stated_runway_months) == "20" and compute(call).verdict == "consistent"
    assert "gives its printed runway under Numbers" in _unwrapped(text) and "the stated 20 months stands" in answer
    # A move an earlier update already announced to the same readers is answered by that update, not kept.
    announced = "We moved the 8 enterprise accounts target to March"
    moved = answer[answer.index('"Target: 8 enterprise accounts by December."') :]
    assert announced in prompt and announced in moved
    assert moved.index("is Dropped, answered, quoting October's update") < moved.index(announced)
    assert "October's March target is Not yet due" in moved and "stays Kept" in moved


def test_one_eval_keeps_a_fallen_metric_writes_a_slip_as_moved_and_keeps_one_ask() -> None:
    _, prompt, answer = _eval("bf")

    assert "leave weekly active learners out" in prompt and "Don't show runway" in prompt
    assert 'The line keeps "Weekly active learners"' in answer and "never silently" in answer
    assert "labelled cumulative" in answer and "not put in the place of weekly active learners" in answer
    assert '"launch self-serve team billing" is Moved' in answer
    assert "`[the one ask for this update:" in answer
    assert "`[the names this update goes to]`" in answer and "the skill adds none" in answer


def test_one_eval_declines_the_look_up_and_the_voice_and_judges_a_floor_claim() -> None:
    text, prompt, answer = _eval("bg")
    (call,) = _calls(text)
    result = compute(call)

    assert "Find me 20 fintech seed investors" in prompt and "the way Paul Graham would write it" in prompt
    assert "It declines in one line each to find investors or emails" in answer and "adds none" in answer
    assert str(call.stated_runway_months) == "30" and call.months_to_raise == 6
    assert result.verdict == "mismatch" and result.checks[0].computed.rounded < _FLOOR
    assert '"30+ months" leads the fix list in the fix before sending tier' in answer
    assert "It is a claim stated as a floor, passed as 30" in answer and "the update states 30" not in answer
    assert "Start raising by 17.64 months goes to the founder under Numbers, not into the update" in answer
    assert '"three funds are already in talks" is left out' in answer
    assert '"Riley (angel)" marked as listed twice' in answer


def test_one_eval_is_cut_from_the_current_investor_update_with_no_stated_runway() -> None:
    text, prompt, answer = _eval("bh")
    (call,) = _calls(text)
    result = compute(call)

    assert "Here is our November update to current investors" in prompt
    assert call.stated_runway_months is None and len(call.cases[0].phases) == 2
    assert result.flags == ("cash_never_runs_out",) and result.verdict == "not_checked"
    assert '"MRR: $72,000" differs from the current-investor update' in answer
    assert f"step 5 marks it {_DIFFERS}" in answer and "without going through the lenses" in answer
    # The draft keeps the lowlight the founder asked to drop; the founder may cut it in their own edit.
    assert "drop the late payment" in prompt
    assert 'The draft keeps "our largest customer moved to annual billing and paid 45 days late"' in answer
    assert "may cut it in their own edit" in answer and "leaves the choice" not in text
    assert "the fractional CFO ask stays in the current-investor update only" in answer
    assert "No runway figure is stated, and none is worked out" in answer


def test_a_figure_that_differs_from_the_current_investor_update_is_checked_without_the_lenses() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    ranked = _unwrapped(_section("### The ranked fix list"))
    built = _unwrapped(_section("## Built from this period's current-investor update"))

    assert "every figure and definition in this period's update to current investors, when given" in steps
    assert "(in a draft, the notes or the request)" in steps
    assert f"**Matches** or **{_DIFFERS}**" in steps and "This check is this skill's own, not a metric status" in steps
    assert f"a figure or definition that {_DIFFERS} or a kept finding requires" in steps
    assert "every figure and definition this period's current-investor update also gives is word for word the same" in (
        steps
    )
    # The lenses see that update, yet a difference does not wait for one of them to notice it.
    assert "this period's update to current investors when given, and the draft" in attack
    assert f"nor a figure or definition that {_DIFFERS} (step 5)" in attack
    assert f"with every figure or definition that {_DIFFERS} (step 5)" in ranked
    assert "leads the first tier of the fix list with the calculator's mismatches" in built
    assert "is a finding for the reader pass" not in built
    # Its own check, not a seventh metric status.
    assert _DIFFERS not in _RULES


def test_the_draft_keeps_every_lowlight_the_founder_gave() -> None:
    built = _unwrapped(_section("## Built from this period's current-investor update"))
    limits = _unwrapped(_section("## Limits"))

    for rule in (
        "hears once why a reader may later see it as spin, and the draft keeps the lowlight",
        "the founder, who sends the update, may cut it in their own edit",
        "A lowlight inside a section that may be left out (a departure under team matters) stays in",
    ):
        assert rule in built, rule
    assert "let them decide" not in _TEXT
    assert "hears once why it costs trust; the draft keeps it" in limits
    assert "every lowlight the founder gave is in the draft" in _unwrapped(_section("## Steps"))


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_an_eval_answer_takes_a_first_update_only_from_its_prompt(path: Path) -> None:
    """The skill asks for the earlier updates, never guesses there are none: a first update is the founder's word."""
    _, prompt, answer = _eval(path.name.split("-")[1])

    if _FIRST_UPDATE.search(answer):
        assert "first update" in prompt, path.name
