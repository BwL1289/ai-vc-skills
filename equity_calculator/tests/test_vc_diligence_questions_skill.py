"""The vc-diligence-questions skill keeps its shape: six areas, the shared bank read in place, its review and evals.

The skill helps a founder prepare for a fund's due diligence after a first meeting. It never speaks as an investor,
gives no score and invents no document or figure. Every calculator tool it names must be one the MCP server serves,
and every skill it hands off to by name must be a folder in skills/ (one exception, named below, for a skill built in
parallel). It reads vc-partner-meeting's question bank in place, never a copy: the link must resolve, the columns it
reads must be the bank's, its category-to-area table must cover the bank's categories exactly, and no bank question
may be copied into the skill. Its own file, references/data-room.md, holds the data-room checklist, which names every
bank row's Diligence document exactly once, and its own legal and cap-table questions. The adversarial review keeps
partner-meeting's two stages, with the refute pass free to point at a document on the founder's list. The cap table
goes to ``equity_deal_check`` and runway with no raise or on a SAFE or note raise to ``equity_runway_plan``, in the
input shape the skill writes out whole; what no tool checks is quoted as not checked. The data room at seed is the
core set, the pre-seed rows, plus the seed rows a document or a kept question points to. Each eval in
evals/vc-diligence-questions/ has a prompt, an expected tool call and an expected answer; each eval with a call
carries a valid call for the tool it names and an excerpt that is lines of the report that call prints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from equity_calculator.__main__ import _INPUT_MODELS
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_runway_plan import RunwayPlanInput
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_FOLDER = _ROOT / "skills" / "vc-diligence-questions"
_TEXT = (_FOLDER / "SKILL.md").read_text(encoding="utf-8")
_DATA_ROOM_PATH = _FOLDER / "references" / "data-room.md"
_DATA_ROOM = _DATA_ROOM_PATH.read_text(encoding="utf-8")
_BANK_LINK = "../vc-partner-meeting/references/question-bank.md"
_BANK_PATH = _ROOT / "skills" / "vc-partner-meeting" / "references" / "question-bank.md"
_BANK = _BANK_PATH.read_text(encoding="utf-8")
_PARTNER_MEETING = (_ROOT / "skills" / "vc-partner-meeting" / "SKILL.md").read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-diligence-questions").glob("*.md"))
_EVAL_COUNT = 5
_EVAL_LETTERS = ("ac", "ad", "ae", "af", "al")
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
_TOOLS = {"equity_deal_check", "equity_round", "equity_runway_plan"}
_HANDOFF_SKILLS = ("vc-partner-meeting", "vc-claims-check", "vc-deal-math", "vc-positioning", "equity-calculator")
# Built in a parallel lane and merged before this skill: named in "When to use it" now; its folder check joins
# _HANDOFF_SKILLS once the branch is rebased on a main that has the folder.
_PARALLEL_HANDOFFS = ("vc-term-sheet-review",)
_README_BOTH_FOLDERS = "`vc-diligence-questions` reads `vc-partner-meeting`'s question bank, so load both folders."
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "prepare me for diligence",
    "what will they ask in diligence",
    "build my data room",
    "data-room checklist",
    "the fund wants to start diligence",
)
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
# This skill's own read set: both URLs were read in full for its design, and both are in the shared seven.
_SOURCES = {
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
    "https://a16z.com/16-startup-metrics/",
}
_STAGE_RULE = "Do not spend too much time developing diligence documents for a seed round"
_AREAS = ("Team", "Market", "Product", "Traction and metrics", "Financials and cap table", "Legal")
_TIERS = ("stops the process", "slows it", "minor")
_STATUSES = ("Contradicted", "Missing", "Ready")
_REFUTE_VERDICTS = ("Dropped, answered:", "Dropped, not grounded:", "Kept:")
_CAP_UNCHECKED = "not checked: no tool adds up a cap table"
_NEXT_ROUND = "for the next round"
_IF_ASKED = "if asked"
# Strings an eval's answer quotes that are the skill's own marks or its source's words, not the founder's lines.
_SKILL_MARKS = {_CAP_UNCHECKED, _NEXT_ROUND, _IF_ASKED, _STAGE_RULE}
_FD_ASK = "`[fully diluted shares before the round, SAFEs and notes left out]`"
_FLAG_CODES = ("conversions_bought_by_pre_money", "pool_in_pre_money_lowers_price")
_CORE_STAGE = "pre-seed"
# The step the no-subagent note sends the agent back to, and the title of the review step it must be.
_RESUME_STEP = re.compile(r"; step (\d+) then starts at the quote check\.")
_REVIEW_STEP = "**Run the adversarial review**"
_BANK_COLUMNS = ["ID", "Question", "Probes", "Lenses", "Stages", "Grounding", "Diligence"]
_READ_COLUMNS = ("ID", "Question", "Probes", "Stages", "Grounding", "Diligence")
_MAPPING_COLUMNS = ["Bank category", "Area", "Also read by"]
_AREA_COLUMNS = ["Area", "What a partner checks in diligence"]
_CHECKLIST_COLUMNS = ["ID", "Document", "What it shows", "Area", "From", "Bank IDs"]
_OWN_COLUMNS = ["ID", "Question", "Probes", "Area", "Stages", "Grounding", "Diligence"]
_STAGES = ("pre-seed", "seed", "Series A", "later")
_ALL_STAGES = "all"
_NONE = "none"
_CHECKLIST_ID = re.compile(r"^[A-Z]+-D\d+$")
_OWN_ID = re.compile(r"^(LEGAL|CAP)-\d+$")
_OWN_AREAS = {"Legal", "Financials and cap table"}
_EXECUTIVE_SUMMARY = "An executive summary"
_LEGAL_READS = ("RISK-3", "RISK-4")
_BANK_ID = re.compile(r"\b[A-Z]+-\d+\b")
_URL = re.compile(r"https?://\S+")
# The README badge: its alt text and its image URL both carry the number of skills.
_BADGE = re.compile(r'alt="Skills: (\d+)" src="https://img\.shields\.io/badge/skills-(\d+)-')
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")
# A bar or benchmark the data-room file must never carry: money, a percent, or a multiple such as 3x.
_FIGURE = re.compile(r"[$%]|\d\s*x\b")
_FILLER = "1"
# A whole runway_plan input the skill writes out in step 2, in one code span.
_RUNWAY_INPUT = re.compile(r'`(\{"cash_on_hand": .*?\})`')


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


def _cells(row: str) -> list[str]:
    return [cell.strip() for cell in row.strip()[1:-1].split("|")]


def _tables(text: str, columns: list[str]) -> list[list[str]]:
    """The body rows of every Markdown table in ``text`` whose header is ``columns``."""
    rows: list[list[str]] = []
    for block in text.split("\n\n"):
        lines = [line for line in block.splitlines() if line.startswith("|")]
        if lines and _cells(lines[0]) == columns:
            rows += [_cells(line) for line in lines[2:]]
    return rows


def _bank_rows() -> list[list[str]]:
    return _tables(_BANK, _BANK_COLUMNS)


def _bank_categories() -> list[str]:
    """Each heading of the bank that holds a table of bank rows."""
    categories = []
    for heading in re.findall(r"^## (.+)$", _BANK, re.MULTILINE):
        if _tables(_section(f"## {heading}", _BANK), _BANK_COLUMNS):
            categories.append(heading)
    return categories


def _checklist() -> list[list[str]]:
    return _tables(_DATA_ROOM, _CHECKLIST_COLUMNS)


def _own_questions() -> list[list[str]]:
    return _tables(_DATA_ROOM, _OWN_COLUMNS)


def _eval(letter: str) -> Path:
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    return path


def _answer(letter: str) -> str:
    return _unwrapped(_section("## Expected answer", _eval(letter).read_text(encoding="utf-8")))


def _report(text: str) -> str:
    """The report the calculator prints for the eval's call, run on the input model of the tool the eval names."""
    (example,) = _fences("json", text)
    tool = _TOOL_NAME.search(_section("## Expected tool call", text))
    assert tool is not None
    model = _INPUT_MODELS[tool.group(1).removeprefix(_TOOL_PREFIX)]
    return render_sheet(sheet_for(compute(model.model_validate(json.loads(example)["inputs"]))))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-diligence-questions"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "adversarial review", "data-room checklist", "question bank"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_the_skill_never_speaks_as_an_investor_and_gives_no_score() -> None:
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])

    assert "The founder is always the user" in intro
    assert "never plays an investor" in intro and "never speaks as a named investor or firm" in intro
    assert "no score and no readiness percentage" in intro


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert named == _TOOLS
    assert named <= served, named - served


def test_every_skill_it_hands_off_to_exists_and_two_skills_point_here() -> None:
    hand_off = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert name in hand_off, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    for name in _PARALLEL_HANDOFFS:
        assert f"the {name} skill" in hand_off, name
        # Once the folder lands (at the rebase), the name must move to _HANDOFF_SKILLS so the folder check runs.
        assert not (_ROOT / "skills" / name / "SKILL.md").is_file(), f"move {name} into _HANDOFF_SKILLS"
    assert '"Review my term sheet": the vc-term-sheet-review skill' in hand_off
    assert "vc-diligence-questions" in _section("## When to use it", _POSITIONING)
    assert "the vc-diligence-questions skill" in _unwrapped(_section("## When to use it", _PARTNER_MEETING))
    assert "Planned, not yet shipped" not in _PARTNER_MEETING


def test_the_runway_inputs_the_skill_writes_out_are_ones_the_runway_tool_takes_whole() -> None:
    """Each runway input in step 2 is a whole object, parsed from the skill's text with nothing added by the test."""
    steps = _section("## Steps")
    inputs = [json.loads(found.replace("...", _FILLER)) for found in _RUNWAY_INPUT.findall(steps)]

    assert len(inputs) == 2
    no_raise, on_a_raise = inputs
    assert "raises" not in no_raise and "stated_runway_months" in no_raise
    assert "stated_runway_months" not in on_a_raise and "stated_runway_months" in on_a_raise["raises"][0]
    for found in inputs:
        assert set(found) <= set(RunwayPlanInput.model_fields), set(found) - set(RunwayPlanInput.model_fields)
        compute(RunwayPlanInput.model_validate(found))


def test_the_shared_bank_is_read_in_place_and_mapped_whole() -> None:
    text = _unwrapped(_section("## The six areas and the shared question bank"))
    mapping = _tables(_TEXT, _MAPPING_COLUMNS)
    header = next(line for line in _BANK.splitlines() if line.startswith("| ID ") and "Lenses" in line)
    bank_ids = {row[0] for row in _bank_rows()}

    assert f"[`{_BANK_LINK}`]({_BANK_LINK})" in _TEXT
    assert (_FOLDER / _BANK_LINK).resolve() == _BANK_PATH.resolve()
    assert "the " + ", ".join(_READ_COLUMNS[:-1]) + " and " + _READ_COLUMNS[-1] + " columns" in text
    assert set(_READ_COLUMNS) <= set(_cells(header))
    assert sorted(row[0] for row in mapping) == sorted(_bank_categories())
    assert len({row[0] for row in mapping}) == len(mapping)
    assert {row[1] for row in mapping} <= set(_AREAS)
    for risk in _LEGAL_READS:
        assert risk in bank_ids and risk in text, risk
    assert "it keeps no copy of it" in text
    assert "never write bank questions from memory and cite no bank ID" in text
    for row in _bank_rows():
        assert row[1] not in _unwrapped(_TEXT), row[0]


def test_the_bank_names_this_skill_and_no_longer_a_planned_one() -> None:
    bank = _unwrapped(_BANK)

    assert "The vc-diligence-questions skill reads the same file" in bank
    assert "read by the vc-diligence-questions skill" in bank
    assert "planned due-diligence skill" not in bank


def test_the_data_room_checklist_covers_the_banks_diligence_cells_once_each() -> None:
    rows = _checklist()
    ids = [row[0] for row in rows]
    bank = {row[0]: row[6] for row in _bank_rows()}
    named = [bank_id for row in rows if row[5] != _NONE for bank_id in row[5].split(", ")]

    assert rows
    assert len(set(ids)) == len(ids)
    assert not set(ids) & set(bank)
    for row in rows:
        assert len(row) == len(_CHECKLIST_COLUMNS) and all(row), row[0]
        assert _CHECKLIST_ID.match(row[0]), row[0]
        assert row[3] in _AREAS, row[0]
        assert row[4] in _STAGES, row[0]
    assert set(named) <= set(bank), set(named) - set(bank)
    assert sorted(named) == sorted(bank_id for bank_id, cell in bank.items() if cell != _NONE)
    assert {row[3] for row in rows} == set(_AREAS)
    assert any(row[1] == _EXECUTIVE_SUMMARY for row in rows)


def test_the_own_questions_have_fixed_columns_and_point_at_checklist_rows() -> None:
    rows = _own_questions()
    ids = [row[0] for row in rows]
    checklist = {row[0] for row in _checklist()}

    assert rows
    assert len(set(ids)) == len(ids)
    for row in rows:
        assert len(row) == len(_OWN_COLUMNS) and all(row), row[0]
        assert _OWN_ID.match(row[0]), row[0]
        assert row[1].endswith("?"), row[0]
        assert row[3] in _OWN_AREAS, row[0]
        assert row[4] == _ALL_STAGES or set(row[4].split(", ")) <= set(_STAGES), row[0]
        assert row[6] in checklist, row[0]
    assert not _FIGURE.search(_DATA_ROOM), _FIGURE.search(_DATA_ROOM)
    assert not _URL.search(_DATA_ROOM)
    for name in _PEOPLE_AND_FIRMS:
        assert not re.search(rf"\b{re.escape(name)}\b", _DATA_ROOM.lower()), name
    assert "unverified" in _DATA_ROOM


def test_every_id_the_skill_or_its_file_cites_exists() -> None:
    known = {row[0] for row in _bank_rows()} | {row[0] for row in _own_questions()}
    known |= {row[0] for row in _checklist()}
    cited = set(_BANK_ID.findall(_TEXT)) | set(_BANK_ID.findall(_DATA_ROOM))
    cited |= {match for path in _EVALS for match in _BANK_ID.findall(path.read_text(encoding="utf-8"))}
    cited |= {match for path in _EVALS for match in re.findall(r"\b[A-Z]+-D\d+\b", path.read_text(encoding="utf-8"))}

    assert cited <= known, cited - known


def test_the_attack_stage_runs_six_area_lenses_before_the_numbers_and_the_bank() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    areas = [row[0] for row in _tables(_TEXT, _AREA_COLUMNS)]
    note = "Without a subagent tool, run Stage A of the adversarial review right after step 1, before step 2"
    resume = _RESUME_STEP.search(steps)

    assert areas == list(_AREAS)
    assert note in steps and steps.index(note) < steps.index("1. **Intake.**")
    assert resume is not None
    assert f" {resume.group(1)}. {_REVIEW_STEP}" in steps, resume.group(1)
    assert "quoted word for word" in attack
    assert "only the founder's material, the document list and its lens brief" in attack
    assert "one after another" in attack and "do no arithmetic" in attack
    assert "right after step 1, before step 2, without reading the bank or the checklist" in attack
    assert "not the bank, not the checklist, not the calculator's output" in attack
    assert "less independent than subagents" in attack
    assert "never by a person or firm" in attack


def test_the_refute_stage_judges_with_only_the_material_and_the_document_list() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "one subagent per question" in refute
    assert "you argue neither side" in refute
    assert "When you cannot decide, return Kept" in refute
    assert "Bring in no outside fact" in refute and "do no arithmetic" in refute
    assert "counts only for what the founder says it shows" in refute
    assert "goes to the have-it-ready list" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "an answering line that is not in the material word for word does not drop the question" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_ranking_has_three_tiers_and_no_score() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    outside_limits = _unwrapped(_TEXT[: _TEXT.index("\n## Limits\n")]).lower()

    for tier in _TIERS:
        assert f"**{tier}**" in rank, tier
    assert "The calculator's mismatches lead the first tier" in rank
    assert "give no percentages and no score" in rank
    assert rank.index("lead the first tier") < rank.index("raised by more than one lens")
    assert "It is not refuted: the calculator computed it" in _unwrapped(_section("### Stage A: attack"))
    for score in ("/100", "out of 100", "readiness score"):
        assert score not in outside_limits, score


def test_the_cap_table_goes_to_the_calculator_and_its_sums_are_quoted_unchecked() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert _CAP_UNCHECKED in steps and _CAP_UNCHECKED in answering
    assert "Never divide the shares yourself" in steps
    assert "never add, subtract or divide shares yourself" in steps
    assert "SAFEs and notes excluded" in steps and "ask which way the founder's does" in steps
    assert "0.536170 is 53.6170%" in steps and "a change of notation, not a calculation" in steps
    fd_rule = "If the founder's total counts them, ask the founder for the total without them, as a bracketed ask"
    assert f"{fd_rule}, {_FD_ASK}" in steps
    assert "never subtract the SAFE or note shares yourself" in steps
    assert "`equity_round` gives no verdict, no mismatch and no flags" in steps
    assert "both as printed; no difference is computed" in steps
    assert "is not passed as `investment`" in steps
    assert "Runway with no raise, or on a SAFE or note raise, goes to `equity_runway_plan`" in steps
    assert "One call per document's version of the ask" in steps
    assert "Read every code in the tool's `flags` too, and relay each in the tool's words" in steps
    assert "with its `unverified` source, never as a bar" in steps
    assert "each flag, one line, in the tool's words" in answering
    round_rule = "each `equity_round` result as its price per share and ownership rows, as printed, with no verdict"
    assert round_rule in answering
    assert "`equity_round` verdict" not in answering
    for unchecked in ("no tool computes runway without a raise", "no tool computes this for a SAFE or note raise"):
        assert unchecked not in _TEXT, unchecked


def test_the_checklist_has_three_statuses_in_order_and_keeps_to_the_stage() -> None:
    checklist = _unwrapped(_section("## The data-room checklist"))

    assert "**Contradicted**, then **Missing**, then **Ready**" in checklist
    for status in _STATUSES:
        assert f"- **{status}:**" in _section("## The data-room checklist"), status
    assert "Rows for a later stage are not listed as missing" in checklist
    assert "the rows whose From stage is the founder's stage or earlier" in checklist
    assert f'Name every other seed row once, in one line, as "{_IF_ASKED}", never as Missing' in checklist
    assert f'"{_NEXT_ROUND}"' in checklist
    assert "The skill has not seen the document" in checklist


def test_the_seed_core_set_is_the_pre_seed_rows_and_the_skill_names_them() -> None:
    """At seed the checklist lists the pre-seed rows, not every seed row; the skill's list of them is the file's."""
    checklist = _unwrapped(_section("## The data-room checklist"))
    core = [row[0] for row in _checklist() if row[4] == _CORE_STAGE]
    seed = [row[0] for row in _checklist() if row[4] == "seed"]
    named = re.search(r"the rows whose From is pre-seed \(([^)]*)\)", checklist)

    assert named is not None
    listed: list[str] = []
    for part in re.split(r", | and ", named.group(1)):
        first, _, last = part.partition(" to ")
        prefix, start = first.rsplit("D", 1)
        stop = last.rsplit("D", 1)[1] if last else start
        listed += [f"{prefix}D{number}" for number in range(int(start), int(stop) + 1)]
    assert sorted(listed) == sorted(core)
    assert len(core) < len(seed)
    assert "plus a seed row only when a document on the founder's list shows what it needs" in checklist
    assert "except at seed: there it lists the pre-seed rows (the core set)" in _unwrapped(_DATA_ROOM)


def test_the_area_prep_list_gives_legal_the_two_risk_rows() -> None:
    prep = _unwrapped(_section("## The area prep list"))

    assert "Legal also takes RISK-3 and RISK-4 (the mapping's Also read by)" in prep
    assert "they stay in Product's list too" in prep


def test_draft_answers_build_only_from_the_material_and_never_judge_the_law() -> None:
    drafts = _unwrapped(_section("## Draft answers"))

    assert "built only from the founder's material and tool results" in drafts
    assert "bracketed ask" in drafts
    assert "never says whether something is legally sufficient" in drafts


def test_limits_refuse_invention_hiding_and_legal_opinions() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert "Not legal, tax or investment advice" in limits
    assert "backdates" in limits
    assert "never helps leave out a known dispute" in limits
    assert "legally sufficient" in limits
    assert "opens no folder of files" in limits
    assert "No investor research" in limits


def test_the_sources_are_ones_the_authors_read_and_the_stage_rule_is_quoted() -> None:
    sources = _unwrapped(_section("## Sources"))

    assert set(_URL.findall(_TEXT)) == _SOURCES
    assert _SOURCES <= set(_READ_SOURCES)
    assert _STAGE_RULE in sources
    assert "unverified" in sources


def test_no_person_or_firm_is_named_outside_sources_or_in_any_eval_answer() -> None:
    sources_start = _TEXT.index("\n## Sources\n")
    sources_end = _TEXT.index("\n## ", sources_start + 1)
    outside = (_TEXT[:sources_start] + _TEXT[sources_end:]).lower()
    answers = [_section("## Expected answer", path.read_text(encoding="utf-8")).lower() for path in _EVALS]

    for text in (outside, *answers):
        for name in _PEOPLE_AND_FIRMS:
            assert not re.search(rf"\b{re.escape(name)}\b", text), name


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "A run passes when" in _unwrapped(text), path.name


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert _CALL_EVALS == [_eval("ac"), _eval("al")]
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (excerpt,) = _fences("text", text)

    report = _report(text)
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents in the expected answer is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    report = _report(text)
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in report, figure


def test_the_cap_table_eval_quotes_todays_percent_unchecked_and_marks_the_cap_table_contradicted() -> None:
    answer = _answer("ac")

    assert _CAP_UNCHECKED in answer
    assert "(FIN-D2) is Contradicted" in answer
    assert "is not put through the refute pass" in answer
    assert "relays the two flag codes in the tool's words" in _unwrapped(_eval("ac").read_text(encoding="utf-8"))
    for code in _FLAG_CODES:
        assert f"`{code}`" in answer, code
    assert f'named once, in one line, as "{_IF_ASKED}", and none is marked Missing' in answer


def test_the_seed_eval_keeps_the_room_to_the_stage_and_asks_for_the_assignment() -> None:
    answer = _answer("ad")

    assert f'"{_STAGE_RULE}"' in answer and f'"{_NEXT_ROUND}"' in answer
    assert "[a signed assignment of the freelance developer's work to the company]" in answer
    assert "does not say whether the company owns the code" in answer
    assert "(FIN-D4 to FIN-D6)" in answer and f'as "{_IF_ASKED}", and none of them is marked Missing' in answer


def test_the_runway_eval_leads_with_the_mismatch_and_asks_for_the_total_without_the_safe() -> None:
    text = _eval("al").read_text(encoding="utf-8")
    answer = _answer("al")
    call = _section("## Expected tool call", text)
    tool = _TOOL_NAME.search(call)

    assert tool is not None and tool.group(1) == "equity_runway_plan"
    assert "No `equity_deal_check` call" in call
    assert "The runway mismatch leads the ranked list as stops the process" in answer
    assert "is not put through the refute pass" in answer
    assert _FD_ASK in answer and "passes no share count to any tool" in answer
    assert "(FIN-D5) is Missing too, because the runway question's draft answer names it" in answer
    assert f'as "{_IF_ASKED}"' in answer


def test_the_refusal_eval_declines_and_names_no_one() -> None:
    answer = _answer("ae")

    assert "declines each request in one line" in answer
    assert "no backdated document" in answer and "will not help leave out a known claim" in answer
    assert "gives no view on whether the claim is valid" in answer


def test_one_eval_moves_a_question_to_the_have_it_ready_list_by_quoting_the_line_that_answers_it() -> None:
    text = _eval("af").read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))
    question, dropped = _answer("af").split("Dropped, answered", 1)
    # The first quote after the verdict is the founder's line to point to: a whole line of the material, not the line
    # the question was about.
    answering_line = _DOUBLE_QUOTED.findall(dropped)[0]

    assert answering_line in prompt
    assert answering_line not in _DOUBLE_QUOTED.findall(question)
    assert "have-it-ready list" in dropped


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_every_line_an_eval_answer_quotes_is_in_its_prompt_or_is_a_mark_of_the_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))

    for quoted in _DOUBLE_QUOTED.findall(_unwrapped(_section("## Expected answer", text))):
        assert quoted in prompt or quoted in _SKILL_MARKS, quoted


def test_the_readme_tells_a_manual_install_to_load_both_folders() -> None:
    assert _README_BOTH_FOLDERS in (_ROOT / "README.md").read_text(encoding="utf-8")


def test_the_readme_badge_counts_the_skill_folders() -> None:
    badge = _BADGE.search((_ROOT / "README.md").read_text(encoding="utf-8"))
    folders = sorted((_ROOT / "skills").glob("*/SKILL.md"))

    assert badge is not None
    assert int(badge.group(1)) == int(badge.group(2)) == len(folders), (badge.groups(), len(folders))
