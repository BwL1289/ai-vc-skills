"""The vc-partner-meeting skill keeps its shape: a moderator's rehearsal, its lenses, review, bank and evals.

The skill is the rehearsal's moderator, never an investor: questions in the third person, no pass or invest verdict
and no score. Every calculator tool it names must be one the MCP server serves, and every skill it hands off to by
name must be a folder in skills/. Its lenses are frameworks named by stage and by a partner's background, never a
person or firm. The adversarial review keeps both stages (lenses that quote the founder's own line, then a refute pass
that may use only the founder's material), the standing prep questions are never refuted, and the debrief builds each
stronger answer only from the founder's material. The question bank in references/ is one table per category with
fixed columns, no figures and no names, competition rows at four fixed levels, and the standing prep questions word
for word. Each eval in evals/vc-partner-meeting/ has a prompt, an expected tool call and an expected answer; the one
eval with an ``equity_deal_check`` call carries a valid call and an excerpt that is lines of the report that call
prints.
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
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_FOLDER = _ROOT / "skills" / "vc-partner-meeting"
_TEXT = (_FOLDER / "SKILL.md").read_text(encoding="utf-8")
_BANK_PATH = _FOLDER / "references" / "question-bank.md"
_BANK = _BANK_PATH.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVAL_DIR = _ROOT / "evals" / "vc-partner-meeting"
_EVALS = sorted(_EVAL_DIR.glob("*.md"))
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
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator", "vc-positioning", "vc-claims-check")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 350
_TRIGGERS = (
    "rehearse my partner meeting",
    "run a mock partner meeting",
    "practice my investor meeting",
    "VC pitch meeting",
    "what will the partners ask",
    "what will VCs ask me",
    "drill me on the hard questions",
    "prep me for my partner meeting",
    "debrief my answers",
)
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_STAGE_LENSES = ("Pre-seed", "Seed", "Series A", "Later stage")
_BACKGROUND_LENSES = ("Operator", "Finance", "Product", "Network", "Sector thesis")
_STAGES = ("pre-seed", "seed", "Series A", "later")
_ALL_STAGES = "all"
_STANDING = "standing"
# The four levels a competition question reads the market at; the planned deck review uses the same four.
_COMPETITION_LEVELS = ("Direct", "Indirect", "Adjacent and platform", "Doing nothing")
_COMPETITION_PREFIX = "COMP-"
_BANK_COLUMNS = ["ID", "Question", "Probes", "Lenses", "Stages", "Grounding", "Diligence"]
_BANK_ID = re.compile(r"^[A-Z]+-\d+$")
_MIN_BANK_ROWS = 80
_MAX_BANK_ROWS = 100
_BANK_CATEGORIES = 11
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_URL = re.compile(r"https?://\S+")
# A link written without its scheme, such as example.com/path; the one such credit the skill carries is allowed by name.
_BARE_LINK = re.compile(r"(?<![/\w.])(?:[\w-]+\.)+(?:com|org|io|me|net|dev)/[\w./-]*[\w/]")
_BARE_LINKS_ALLOWED = {"github.com/xiapeli/vc-skills"}
# The README badge: its alt text and its image URL both carry the number of skills.
_BADGE = re.compile(r'alt="Skills: (\d+)" src="https://img\.shields\.io/badge/skills-(\d+)-')
# Strings an eval's answer quotes that are the skill's own marks, not lines of the founder's material.
_NOT_REHEARSED = "not rehearsed"
_YOUR_QUESTION = "your question"
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_SAFE_UNCHECKED = "not checked: no tool computes this for a SAFE or note raise"
_NO_RAISE_UNCHECKED = "not checked: no tool computes runway without a raise"
_SKILL_MARKS = {_NOT_REHEARSED, _YOUR_QUESTION, _SAFE_UNCHECKED, _NO_RAISE_UNCHECKED}
_REFUTE_VERDICTS = ("Dropped, answered:", "Dropped, not grounded:", "Kept:")
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")
# A share as the MCP tool returns it: a fraction with six places and no percent sign.
_JSON_FRACTION = re.compile(r"(?<![\d.])-?\d+\.\d{6}(?![\d%])")
# A bar or benchmark the bank must never carry: money, a percent, or a multiple such as 3x.
_BANK_FIGURE = re.compile(r"[$%]|\d\s*x\b")


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


def _table(heading: str, text: str = _TEXT) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    rows = [_cells(match.group(0)) for match in _TABLE_ROW.finditer(_section(heading, text))]
    return rows[2:]


def _bank_rows() -> list[list[str]]:
    """Every question row of the bank: the body rows of each table whose header is the bank's seven columns."""
    rows: list[list[str]] = []
    for block in _BANK.split("\n\n"):
        lines = [line for line in block.splitlines() if line.startswith("|")]
        if lines and _cells(lines[0]) == _BANK_COLUMNS:
            rows += [_cells(line) for line in lines[2:]]
    return rows


def _eval(letter: str) -> Path:
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    return path


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-partner-meeting"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    assert "founder" in description and "adversarial review" in description
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_round"} <= named
    assert named <= served, named - served


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_here() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "vc-partner-meeting" in _section("## When to use it", _POSITIONING)


def test_the_skill_moderates_and_never_speaks_as_an_investor() -> None:
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])
    limits = _unwrapped(_section("## Limits"))

    assert "third person" in intro
    assert "never speaks as an investor" in intro
    assert "no pass or invest verdict and no score" in intro
    assert 'Asked to "be" a named partner, it declines in one line' in limits


def test_the_lenses_are_frameworks_by_stage_and_background_with_no_bars() -> None:
    rows = _table("## The lenses")
    lenses = {row[0]: row[1] for row in rows}
    text = _unwrapped(_section("## The lenses"))

    assert [name for name, kind in lenses.items() if kind == "Stage"] == list(_STAGE_LENSES)
    assert [name for name, kind in lenses.items() if kind == "Background"] == list(_BACKGROUND_LENSES)
    assert set(lenses.values()) == {"Stage", "Background"}
    for lens in lenses:
        assert not any(re.search(rf"\b{name}\b", lens.lower()) for name in _PEOPLE_AND_FIRMS), lens
    assert "Stage lenses carry no numeric bars" in text
    assert ", ".join(_COMPETITION_LEVELS[:3]) + ", and " + _COMPETITION_LEVELS[3] in text


def test_the_attack_stage_runs_independent_lenses_before_the_numbers_and_the_bank() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    note = "Without a subagent tool, run Stage A of the adversarial review right after step 2, before step 3"

    assert note in steps and steps.index(note) < steps.index("1. **Intake.**")
    assert "2. **Pick the lenses**" in steps
    assert "quoted word for word" in attack
    assert "only the founder's material and its lens brief" in attack
    assert "one after another" in attack and "do no arithmetic" in attack
    assert "right after step 2, before step 3, without reading the question bank" in attack
    assert "is read only after Stage A" in attack
    assert "enters the drill only when it is tied to a founder's line quoted word for word" in attack
    assert "less independent than subagents" in attack
    assert "[`references/question-bank.md`](references/question-bank.md)" in _TEXT


def test_the_refute_stage_judges_with_only_the_material_and_moves_answered_questions_to_rehearsal() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "one subagent per question" in refute
    assert "you argue neither side" in refute
    assert "When you cannot decide, return Kept" in refute
    assert "Bring in no outside fact" in refute and "do no arithmetic" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "an answering line that is not in the material word for word does not drop the question" in refute
    assert "goes to the quick-rehearsal list" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes
    assert "no percentages and no score" in _unwrapped(_section("### Rank what survives"))


def test_the_calculators_rows_open_their_tiers_ahead_of_questions_from_more_than_one_lens() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    mismatches = _unwrapped(_section("### Stage A: attack"))

    assert "the calculator's rows come first, in the order the tool reports them, ahead of everything else" in rank
    assert "mismatches open ends the meeting, flags open weakens it" in rank
    assert rank.index("the calculator's rows come first") < rank.index("raised by more than one lens")
    assert "Neither is refuted" in mismatches


def test_one_message_mode_debriefs_every_pasted_answer_even_one_no_lens_kept() -> None:
    steps = _unwrapped(_section("## Steps"))
    debrief = _unwrapped(_section("## The debrief"))

    assert "One-message mode: debrief every pasted answer" in steps
    assert "a dropped, answered question with a pasted answer is debriefed too" in steps
    assert f'labelled "{_YOUR_QUESTION}" in place of a lens' in steps
    assert f'"{_NOT_REHEARSED}"' in steps
    assert "each other pasted answer" in debrief and f'"{_YOUR_QUESTION}"' in debrief


def test_the_standing_prep_questions_are_not_refuted_and_invent_nothing() -> None:
    rows = _table("## Standing prep questions")
    text = _unwrapped(_section("## Standing prep questions"))

    assert len(rows) == 6
    assert "are not refuted" in text and "unverified" in text
    assert "never invents a fund, a commitment, a term sheet or a reference" in text


def test_the_debrief_builds_only_from_the_material_and_never_predicts_a_decision() -> None:
    debrief = _unwrapped(_section("## The debrief"))

    assert "built only from the founder's material" in debrief
    assert "bracketed ask" in debrief
    assert "what a yes would need" in debrief
    assert "never say a partner or a firm would invest, pass or score" in debrief


def test_figures_go_to_the_calculator_and_runway_with_no_raise_is_quoted_unchecked() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    for unchecked in (_SAFE_UNCHECKED, _NO_RAISE_UNCHECKED):
        assert unchecked in steps and unchecked in answering, unchecked
    assert "never divide cash by burn yourself" in steps
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps
    assert "Make one call per version of the ask" in steps and "as printed" in steps


def test_every_flag_the_calculator_raises_is_relayed_and_a_benchmark_band_is_never_a_bar() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "Read every code in the tool's `flags` too" in steps
    assert "joins the kept questions as weakens it, in the tool's words, and is not refuted" in steps
    for code in ("`runway_below_band`", "`dilution_above_band`", "`runway_band`", "`dilution_band`"):
        assert code in steps, code
    assert "with its `unverified` source" in steps and "never as a bar" in steps
    assert "each flag, one line, in the tool's words" in answering and "`unverified` source" in answering
    assert "which one is meant, as ends the meeting, quoting both tool values" in steps


def test_the_question_bank_has_fixed_columns_unique_ids_and_known_lenses_and_stages() -> None:
    rows = _bank_rows()
    lenses = set(_STAGE_LENSES) | set(_BACKGROUND_LENSES)
    ids = [row[0] for row in rows]

    assert _MIN_BANK_ROWS <= len(rows) <= _MAX_BANK_ROWS
    assert len(set(ids)) == len(ids)
    for row in rows:
        assert len(row) == len(_BANK_COLUMNS), row
        assert _BANK_ID.match(row[0]), row[0]
        assert all(row), row[0]
        assert row[1].endswith("?"), row[0]
        assert set(row[3].split(", ")) <= lenses, row[0]
        assert row[4] == _ALL_STAGES or set(row[4].split(", ")) <= set(_STAGES), row[0]
    # Every table that opens with an ID column is a category table with the seven columns, except the column key, whose
    # first row describes the ID column.
    tables = [line for line in _BANK.splitlines() if line.startswith("| ID ")]
    headers = [line for line in tables if _cells(line) == _BANK_COLUMNS]
    assert len(headers) == len(tables) - 1 == _BANK_CATEGORIES
    assert len({row[0].split("-")[0] for row in rows}) == _BANK_CATEGORIES


def test_the_question_bank_carries_no_figures_and_no_names() -> None:
    assert not _BANK_FIGURE.search(_BANK), _BANK_FIGURE.search(_BANK)
    for name in _PEOPLE_AND_FIRMS:
        assert not re.search(rf"\b{re.escape(name)}\b", _BANK.lower()), name
    assert not _URL.search(_BANK)


def test_the_competition_rows_use_the_four_levels() -> None:
    rows = [row for row in _bank_rows() if row[0].startswith(_COMPETITION_PREFIX)]
    levels = [row[2].split(":", 1)[0] for row in rows]

    assert rows
    assert set(levels) == set(_COMPETITION_LEVELS), levels
    for level in _COMPETITION_LEVELS:
        assert f"**{level}**" in _BANK, level


def test_every_standing_prep_question_is_a_standing_row_of_the_bank_word_for_word() -> None:
    standing = [row[0] for row in _table("## Standing prep questions")]
    bank = {row[1] for row in _bank_rows() if row[5] == _STANDING}

    assert set(standing) == bank


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "A run passes when" in _unwrapped(text), path.name


def test_one_eval_moves_a_question_to_rehearsal_by_quoting_the_line_that_answers_it() -> None:
    dropping = [path for path in _EVALS if "Dropped, answered" in _unwrapped(path.read_text(encoding="utf-8"))]
    assert dropping
    for path in dropping:
        text = path.read_text(encoding="utf-8")
        prompt = _unwrapped(_section("## Prompt", text))
        answer = _unwrapped(_section("## Expected answer", text))
        question, dropped = answer.split("Dropped, answered", 1)
        # The first quote after the verdict is the founder's line to lead with: a whole line of the material, not
        # the line the question was about.
        answering_line = _DOUBLE_QUOTED.findall(dropped)[0]
        assert answering_line in prompt
        assert answering_line not in _DOUBLE_QUOTED.findall(question)
        assert "quick-rehearsal list" in dropped


def test_the_refusal_evals_decline_and_name_no_one() -> None:
    fund = _unwrapped(_section("## Expected answer", _eval("aa").read_text(encoding="utf-8")))
    interest = _unwrapped(_section("## Expected answer", _eval("ab").read_text(encoding="utf-8")))

    assert "declines" in fund
    assert not any(re.search(rf"\b{name}\b", fund.lower()) for name in _PEOPLE_AND_FIRMS)
    assert "declines" in interest and "term sheets" in interest
    for quoted in _DOUBLE_QUOTED.findall(interest):
        assert quoted in _unwrapped(_section("## Prompt", _eval("ab").read_text(encoding="utf-8"))), quoted


def test_the_runway_eval_quotes_the_no_raise_runway_unchecked() -> None:
    text = _eval("r").read_text(encoding="utf-8")

    assert _eval("r") in _CALL_EVALS
    assert _NO_RAISE_UNCHECKED in _unwrapped(_section("## Expected answer", text))


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
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


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents in the expected answer is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    results = [compute(DealCheckInput.model_validate(json.loads(call)["inputs"])) for call in _fences("json", text)]
    reports = "\n".join(render_sheet(sheet_for(result)) for result in results)
    dumps = "\n".join(result.model_dump_json() for result in results)
    answer = _unwrapped(_section("## Expected answer", text))
    figures = _PRINTED_FIGURE.findall(answer)

    assert figures
    for figure in figures:
        assert figure in reports, figure
    for fraction in _JSON_FRACTION.findall(answer):
        assert f'"rounded":"{fraction}"' in dumps, fraction


def test_the_sources_are_ones_the_authors_read_and_the_credit_took_no_text() -> None:
    sources = _unwrapped(_section("## Sources"))

    assert set(_URL.findall(_TEXT)) <= set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT))
    assert set(_BARE_LINK.findall(_TEXT)) == _BARE_LINKS_ALLOWED
    assert not _BARE_LINK.search(_BANK)
    assert "github.com/xiapeli/vc-skills" in sources and "MIT-licensed" in sources
    assert "no text was taken" in sources


def test_no_person_or_firm_is_named_outside_sources_or_in_any_eval_answer() -> None:
    sources_start = _TEXT.index("\n## Sources\n")
    sources_end = _TEXT.index("\n## ", sources_start + 1)
    outside = (_TEXT[:sources_start] + _TEXT[sources_end:]).lower()
    answers = [_section("## Expected answer", path.read_text(encoding="utf-8")).lower() for path in _EVALS]

    for text in (outside, *answers):
        for name in _PEOPLE_AND_FIRMS:
            assert not re.search(rf"\b{re.escape(name)}\b", text), name


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_every_line_an_eval_answer_quotes_is_in_its_prompt_or_is_a_mark_of_the_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))

    for quoted in _DOUBLE_QUOTED.findall(_unwrapped(_section("## Expected answer", text))):
        assert quoted in prompt or quoted in _SKILL_MARKS, quoted


def test_the_readme_badge_counts_the_skill_folders() -> None:
    badge = _BADGE.search((_ROOT / "README.md").read_text(encoding="utf-8"))
    folders = sorted((_ROOT / "skills").glob("*/SKILL.md"))

    assert badge is not None
    assert int(badge.group(1)) == int(badge.group(2)) == len(folders), (badge.groups(), len(folders))
