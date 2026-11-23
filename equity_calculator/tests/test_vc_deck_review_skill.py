"""The vc-deck-review skill keeps its shape: its ten dimensions, its marks, its slide rules, its review and its evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The ten dimensions are fixed rows, each attacked by a lens that exists; the three marks
have an order and there is no score anywhere. Competition is checked at four named levels, and the skill names no
competitor. The adversarial review keeps both stages: lenses named by what they test (never by a person or firm),
each objection quoting the deck word for word, and a refute pass that uses only the founder's material and records why
each dropped objection fell; the survivors become a ranked fix list in tiers. Investor fit names kinds of investor,
never firms. Each eval in evals/vc-deck-review/ has a prompt, an expected tool call and an expected answer; the eval
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
_SKILL = _ROOT / "skills" / "vc-deck-review" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_CLAIMS_CHECK = (_ROOT / "skills" / "vc-claims-check" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-deck-review").glob("*.md"))
_EVAL_COUNT = 4
# The repository gives each made-up company its own letter; this skill's evals use M to P.
_EVAL_LETTERS = ("m", "n", "o", "p")
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
_HANDOFF_SKILLS = ("vc-claims-check", "vc-deal-math", "vc-positioning", "equity-calculator")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "review my deck",
    "tear apart my pitch deck",
    "is my deck ready to send",
    "what will a partner think of my deck",
    "which investors fit this deck",
)
_DIMENSIONS = (
    "Problem",
    "Solution",
    "Why now",
    "Market",
    "Product",
    "Traction",
    "Business model",
    "Competition",
    "Team",
    "Ask and use of funds",
)
_MARKS = ("Contradicted", "Missing", "Present")
# The one definition of the competition levels; other skills that check competition use these names.
_COMPETITION_LEVELS = ("Direct", "Indirect", "Adjacent and platform", "Doing nothing")
_INVESTOR_KINDS = (
    "Angels",
    "Seed funds and small early funds",
    "Larger firms that also do seed",
    "Sector or thesis funds",
)
_REFUTE_VERDICTS = ("Dropped, answered:", "Dropped, not grounded:", "Kept:")
_TIERS = ("**ends the meeting**", "**weakens it**", "**minor**")
_MIN_SLIDE_RULES = 5
_MIN_LENSES = 5
# The public frameworks the repository's skills have read in full (the same set as the vc-claims-check test); this
# skill cites only these, and marks everything else as its own judgment, unverified.
_READ_SOURCES = {
    "https://www.ycombinator.com/library/4b-how-to-pitch-your-company": "YC seven questions",
    "https://www.ycombinator.com/howtoapply": 'YC "How to Apply"',
    "https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck": "YC seed deck guide",
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising": "YC seed fundraising guide",
    "https://www.sequoiacap.com/article/writing-a-business-plan/": "Sequoia",
    "https://a16z.com/16-startup-metrics/": 'a16z "16 Startup Metrics"',
    "https://cdixon.org/2013/08/04/the-idea-maze": 'Dixon "The idea maze"',
}
_SOURCES_USED = {
    "https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck",
    "https://www.ycombinator.com/library/4b-how-to-pitch-your-company",
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
    "https://www.sequoiacap.com/article/writing-a-business-plan/",
}
_OURS = "Ours"
_UNVERIFIED = "unverified"
_URL = re.compile(r"https?://\S+")
# Names a lens or an investor kind must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|\s*Dimensions\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_FIX_COLUMNS = re.compile(
    r"Rank, Tier, Slide, Lens, The deck's line \(quoted\), Why a partner reads it that way,\s+Fix"
)
_SCORE = re.compile(r"/\s*100\b|out of 100", re.IGNORECASE)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_SAFE_UNCHECKED = "not checked: no tool computes this for a SAFE or note raise"
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")


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


def _table(heading: str, text: str = _TEXT) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    section = _section(heading, text)
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(section)]
    return rows[2:]


def _lens_names() -> list[str]:
    table = _section("### Stage A: attack")
    head = _LENS_HEAD.search(table)
    assert head is not None
    rows = table[head.end() :].strip().split("\n\n", 1)[0].splitlines()[1:]
    return [match.group(1) for row in rows if (match := _ROW.match(row))]


def _names_a_person_or_firm(text: str) -> bool:
    return any(re.search(rf"\b{name}\b", text.lower()) for name in _PEOPLE_AND_FIRMS)


def _eval(letter: str) -> tuple[str, str]:
    """The unwrapped prompt and expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-deck-review"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "adversarial review", "no score", "never a named firm", "Never invents traction"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_round"} <= named
    assert named <= served, named - served
    assert "`equity_calculator deal_check`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-deck-review skill" in _unwrapped(_section("## When to use it", _POSITIONING))


def test_the_ten_dimensions_are_the_fixed_rows_each_with_a_read_source_and_a_lens_that_exists() -> None:
    rows = _table("## The ten dimensions")
    lenses = set(_lens_names())
    names = tuple(_READ_SOURCES.values())

    assert tuple(row[1] for row in rows) == _DIMENSIONS
    for row in rows:
        source, lens = row[-2], row[-1]
        assert lens in lenses, row[1]
        assert source.startswith((*names, _OURS)) or _UNVERIFIED in source, row[1]
    (competition,) = (row for row in rows if row[1] == "Competition")
    assert _UNVERIFIED in competition[-2]


def test_the_marks_have_an_order_and_there_is_no_score() -> None:
    marks = _unwrapped(_section("## The evidence marks"))

    assert ", then ".join(f"**{mark}**" for mark in _MARKS) in marks
    assert "Give no overall score and no score per dimension" in marks
    assert "Will be discounted" in marks and "Needs a source keeps the mark Present" in marks
    assert "no 0-100" in _unwrapped(_section("## Limits"))
    assert not _SCORE.search(_TEXT)


def test_the_first_and_last_slide_rules_cite_read_sources() -> None:
    rows = _table("## First and last slides")
    (first,) = (row for row in rows if row[0].startswith("The first slide"))
    (last,) = (row for row in rows if "carries the ask" in row[0])
    (thanks,) = (row for row in rows if "Thank you" in row[0])

    assert len(rows) >= _MIN_SLIDE_RULES
    assert "YC seed deck guide" in first[1] and "YC seed deck guide" in last[1]
    assert "an appendix after it aside" in last[0]
    assert _UNVERIFIED in thanks[1]
    assert "Figures are never read off a picture" in _unwrapped(_section("## Inputs"))


def test_competition_has_four_levels_and_names_no_competitor() -> None:
    section = _unwrapped(_section("## Competition at four levels"))

    assert tuple(row[0] for row in _table("## Competition at four levels")) == _COMPETITION_LEVELS
    assert _UNVERIFIED in section and "the same four groups vc-claims-check uses" in section
    assert "The skill names no competitor itself" in section
    assert "a missing level becomes a bracketed ask" in section


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = _lens_names()

    assert len(lenses) >= _MIN_LENSES
    for lens in lenses:
        assert not _names_a_person_or_firm(lens), lens
    assert "Opening and close" in lenses
    assert "quoted word for word with its slide" in attack
    assert "subagent" in attack and "only the founder's material and its lens brief" in attack
    assert "one after another" in attack and "less independent than subagents" in attack
    assert "do no arithmetic" in attack
    assert "do not go through the lenses" in attack


def test_without_a_subagent_tool_the_lenses_run_before_step_1_and_the_answer_says_so() -> None:
    steps = _unwrapped(_section("## Steps"))
    note = "Without a subagent tool, run Stage A of the adversarial review first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Map the slides, quoting them.**")
    assert "less independent than separate subagents" in _unwrapped(_section("## Answering"))


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))
    refute = _unwrapped(stage)
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in brief, verdict
    assert "using only the founder's material" in handoff and "one subagent per objection" in handoff
    # The refute pass is handed claims-check's pattern list, so the column must exist there under that name.
    assert "the Pattern column of the vc-claims-check discount table" in handoff
    assert "| Pattern" in _section("## Discount patterns", _CLAIMS_CHECK)
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "Bring in no outside fact about the company, its market or its competitors",
        "do no arithmetic",
        "How a partner is likely to read a line is not an outside fact",
        "never answers an objection",
        "When you cannot decide, return Kept",
        "a line of the material other than the objected line supplies the specific thing the objection says is missing",
        "say to move it earlier",
        "invents nothing on the founder's behalf",
        "an answering line that is not in the material word for word does not drop the objection",
        "neither does one that is the objected line itself",
    ):
        assert rule in brief, rule
    assert "argue the founder's side" not in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_ranked_fix_list_has_tiers_and_no_score() -> None:
    ranked = _unwrapped(_section("### The ranked fix list"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    assert "The calculator's mismatches lead the first tier" in ranked
    assert "no percentages and no score" in ranked
    assert "the deck's line quoted word for word" in ranked
    assert answering.index("**The biggest fixes,**") < answering.index("**Ranked fix list,**")
    assert _FIX_COLUMNS.search(answering) and "**Dropped,**" in answering
    assert "not investment, legal or tax advice" in answering


def test_investor_fit_names_kinds_never_firms() -> None:
    rows = _table("## Which investors the story fits")
    section = _unwrapped(_section("## Which investors the story fits"))
    names = tuple(_READ_SOURCES.values())

    assert tuple(row[0] for row in rows) == _INVESTOR_KINDS
    for kind, _, source in rows:
        assert source.startswith(names) or source == f"{_OURS}, {_UNVERIFIED}", kind
    (sector,) = (row for row in rows if row[0] == "Sector or thesis funds")
    assert sector[-1] == f"{_OURS}, {_UNVERIFIED}"
    # The cited guides are the only names allowed: take out the Source cells and the one cited guide in the text.
    uncited = section.replace("the YC seed deck guide", "")
    for source in {row[-1] for row in rows}:
        uncited = uncited.replace(source, "")
    assert not _names_a_person_or_firm(uncited)
    for phrase in ("names no firm or person", "no check sizes", "looks nothing up", _UNVERIFIED, "without a threshold"):
        assert phrase in section, phrase


def test_the_ask_goes_to_the_calculator_and_a_safe_raise_is_quoted_unchecked() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "checked once" in steps and "without its skeptic" in steps
    assert "not passed as `investment`" in steps and "vc-deal-math step 2" in steps
    assert "On a SAFE or note raise, no tool checks the runway claim or the use-of-funds lines" in steps
    assert _SAFE_UNCHECKED in steps and "never work them out by hand" in steps
    assert _SAFE_UNCHECKED in _unwrapped(_section("## Answering"))
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps
    assert "never compute, convert or round one" in steps


def test_sources_are_frameworks_the_repository_has_read() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == _SOURCES_USED
    assert listed <= set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert "this skill's own judgment, unverified" in _unwrapped(_section("## Sources"))


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "has not been run in a live session" in text, path.name


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls, excerpts = _fences("json", text), _fences("text", text)

    assert calls and len(calls) == len(excerpts)
    for call, excerpt in zip(calls, excerpts, strict=True):
        report = render_sheet(sheet_for(compute(DealCheckInput.model_validate(json.loads(call)["inputs"]))))
        printed = [line.rstrip() for line in report.splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents in the expected answer is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    results = [compute(DealCheckInput.model_validate(json.loads(call)["inputs"])) for call in _fences("json", text)]
    reports = "\n".join(render_sheet(sheet_for(result)) for result in results)
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in reports, figure


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    prompt, answer = _eval("n")
    objection, dropped = answer.split("Dropped, answered", 1)
    # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
    # founder's material, not the line the objection was about.
    answering_line = _DOUBLE_QUOTED.findall(dropped)[0]

    assert answering_line in prompt
    assert answering_line not in _DOUBLE_QUOTED.findall(objection)
    assert "move it from the appendix" in answer
    for level in _COMPETITION_LEVELS:
        assert level in answer, level
    assert "No competitor is named" in answer and _SAFE_UNCHECKED in answer


def test_one_eval_declines_a_score_and_named_firms() -> None:
    prompt, answer = _eval("o")

    assert "score my deck out of 100" in prompt and "five VC firms" in prompt
    assert "no score" in answer and "names no firm" in answer
    assert "does not speak as a partner of a named firm" in answer


def test_one_eval_marks_a_figure_contradicted_without_computing() -> None:
    prompt, answer = _eval("p")
    first, second = _DOUBLE_QUOTED.findall(answer)[:2]

    assert "Traction is Contradicted" in answer and "computes no difference" in answer
    assert first in prompt and second in prompt and first != second
    assert "no revenue threshold" in answer
