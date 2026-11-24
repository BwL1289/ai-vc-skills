"""The vc-competitive-landscape skill keeps its shape: its frontmatter, its rules, its adversarial review and evals.

The skill builds a founder's competition map and slide from the competitors the founder names: each competitor at one
of four levels with the problem it solves, three to five axes with their anchors stated before anything is placed,
every placement the founder's own with its evidence, and the substitutes story, a "why customers pick us" line per
competitor, the platform-risk answer and a slide draft with a table and a 2x2. It names no competitor or platform
itself, adds no fact about any company, looks nothing up, places no company on an axis, adds nothing into a score,
names no calculator tool and cites no source, since none was read for it. Its adversarial review keeps the pack's two
stages: independent attack lenses named by what they test (never a person or firm), and a refute pass that uses only
the founder's material, in which a fact the founder marks unverified never answers an objection that asks for
evidence. Each eval has a prompt, an expected tool call and an expected answer, makes no calculator call, quotes only
lines its prompt contains, and carries no figure its prompt lacks beyond the 1-to-5 scale.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-competitive-landscape" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-competitive-landscape").glob("*.md"))
_EVAL_COUNT = 4
_NO_CALL = "## Expected tool call\n\nNone: no calculator call."
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_URL = re.compile(r"https?://\S+")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "build our competition slide",
    "map our competitors",
    "our competition slide is a logo grid",
    "what if a big platform builds this",
    "who do we really compete with",
)
_DESCRIPTION_WORDS = (
    "founder",
    "four levels",
    "substitutes, doing nothing included",
    "1-to-5 anchors stated up front",
    "suggests no placement and adds nothing into a score",
    "adversarial review",
    "Looks nothing up",
)
# The hand-offs the brief names: the whole deck, the claims and the messaging, each to the skill that does it.
_HANDOFFS = {
    "vc-deck-review": "The whole deck, slide by slide: the vc-deck-review skill.",
    "vc-claims-check": "the vc-claims-check skill (preview)",
    "vc-positioning": (
        "Messaging (the one-liner, the story and the say-and-avoid list): the vc-positioning skill (preview)."
    ),
}
_OTHER_HANDOFFS = ("vc-market-sizing", "vc-taste-check", "vc-partner-meeting", "vc-pass-debrief")
_LEVELS = ("Direct", "Indirect", "Adjacent", "Substitutes")
_ADJACENT_KINDS = (
    "a company with the same technology aimed at another use",
    "one that sells something else to the same buyer",
    "a platform the buyer already uses that could add this as a feature",
)
_HALVES = "on every axis, 1 and 2 are the low half, 4 and 5 the high half, and 3 sits on the line"
_UNVERIFIED_RULE = "never answers an objection that asks for evidence"
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_MIN_LENSES = 5
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|$", re.MULTILINE)
_LEVEL_HEAD = re.compile(r"^\|\s*Level\s*\|\s*What it covers\s*\|\s*The buyer's question\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_SURVIVOR_COLUMNS = re.compile(
    r"Rank, Tier, Lens, The founder's line \(quoted\), Why a partner reads it that way,\s+Fix or evidence to add"
)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_DIGITS = re.compile(r"\d+")
# The 1-to-5 axis scale: the anchors, the halves and the placements use these digits whatever the prompt holds.
_SCALE = {"1", "2", "3", "4", "5"}
_EVAL_TITLE = re.compile(r"\A# Eval (\d+): ")
_RAISE_IT_ANYWAY = "raise it anyway, however short the material, and the refute pass decides"


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


def _first_column(heading: str, head: re.Pattern[str]) -> list[str]:
    """The first cell of every body row of the table under ``heading`` whose header row ``head`` matches."""
    table = _section(heading)
    found = head.search(table)
    assert found is not None
    rows = table[found.end() :].strip().split("\n\n", 1)[0].splitlines()[1:]
    return [match.group(1) for row in rows if (match := _ROW.match(row))]


def _eval_parts(path: Path) -> tuple[str, str]:
    """An eval's prompt and expected answer, each unwrapped."""
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-competitive-landscape"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    assert "Use when" in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for word in _DESCRIPTION_WORDS:
        assert word in description, word
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_skill_it_hands_off_to_exists_and_the_brief_s_three_hand_offs_are_there() -> None:
    when = _unwrapped(_section("## When to use it"))

    for name, line in _HANDOFFS.items():
        assert line in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    for name in _OTHER_HANDOFFS:
        assert f"the {name} skill (preview)" in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_it_names_no_calculator_tool_and_does_no_arithmetic() -> None:
    limits = _unwrapped(_section("## Limits"))
    facts = _unwrapped(_section("## Competitor facts"))

    assert _TOOL_NAME.findall(_TEXT) == []
    assert "No arithmetic and no calculator tool" in limits
    assert "never computed, converted or rounded" in facts


def test_it_cites_no_source_since_none_was_read_for_it() -> None:
    sources = _unwrapped(_section("## Sources")).strip()
    urls = set(_URL.findall(_TEXT))
    for path in _EVALS:
        urls |= set(_URL.findall(path.read_text(encoding="utf-8")))

    # The lasting rule: any source the skill or its evals cite comes from the one set of read sources.
    assert urls <= set(_READ_SOURCES)
    # Today's state: none is cited. Adding a read source later means deleting only this line.
    assert urls == set()
    assert sources.startswith("None.") and "unverified" in sources


def test_the_four_levels_are_the_fixed_words_with_adjacent_in_three_kinds() -> None:
    levels = _first_column("## The four levels", _LEVEL_HEAD)
    table = _section("## The four levels")
    (adjacent,) = (row for row in table.splitlines() if row.startswith("| Adjacent"))
    (substitutes,) = (row for row in table.splitlines() if row.startswith("| Substitutes"))

    assert levels == list(_LEVELS)
    for kind in _ADJACENT_KINDS:
        assert kind in adjacent, kind
    assert "doing nothing" in substitutes and "by hand" in substitutes
    assert "the vc-deck-review and vc-claims-check skills use" in _unwrapped(table)


def test_it_names_no_competitor_and_adds_no_fact_about_any_company() -> None:
    levels = _unwrapped(_section("## The four levels"))
    facts = _unwrapped(_section("## Competitor facts"))
    limits = _unwrapped(_section("## Limits"))
    inputs = _unwrapped(_section("## Inputs"))

    assert "The skill names no competitor itself" in levels
    assert "never a name, not even one the agent has heard of" in levels
    assert "never a guess" in levels
    assert "The agent adds nothing about a company it has heard of" in facts
    assert "no correction of the founder's facts from what it knows" in facts
    assert "never offer a competitor's name to fill in" in inputs
    assert "With no competitor named at all, name none" in inputs
    assert "names no competitor or platform the founder did not name, looks nothing up" in limits


def test_a_fact_the_founder_marks_unverified_stays_labelled_and_answers_no_objection_on_evidence() -> None:
    facts = _unwrapped(_section("## Competitor facts"))
    refute = _unwrapped(_section("### Stage B: refute"))

    assert "A fact marked unverified stays on the map with its label" in facts
    assert "The slide shows it only with that label, or leaves it off" in facts
    assert _UNVERIFIED_RULE in facts and _UNVERIFIED_RULE in refute
    assert "one marked unverified that is offered as evidence" in refute


def test_axes_have_anchors_up_front_and_the_founder_places_every_company() -> None:
    axes = _unwrapped(_section("## Axes"))

    assert "three to five" in axes and "never more than five in all" in axes
    assert "has anchors stated up front, before any company is placed" in axes
    assert "what a 1, a 3 and a 5 mean" in axes
    assert _HALVES in axes and "the 2x2 follows these halves and nothing else" in axes
    assert "The founder places every company, their own included, on every axis" in axes
    assert "suggests no placement, fills no cell and never changes one" in axes
    assert "adds nothing up: no total, average, weighted score or rank across axes" in axes
    assert '"buyer evidence: none given"' in axes
    assert "never after the founder's own feature or description" in axes


def test_no_two_by_two_or_slide_is_drawn_until_the_founder_has_placed() -> None:
    axes = _unwrapped(_section("## Axes"))
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "Until the founder has placed their own company and at least one competitor on both axes" in axes
    assert "draw no 2x2 and draft no slide" in axes
    assert 'is listed under it as "not placed", and its placements stay among the open asks' in axes
    assert "The adversarial review runs once, on the full draft, when the placements come back" in axes
    assert "stop as Axes says" in steps
    assert '"waiting for your placements"' in answering
    assert "No total, average or rank column" in answering


def test_the_platform_answer_has_three_parts_and_predicts_nothing_about_the_platform() -> None:
    platform = _unwrapped(_section("## The platform-risk answer"))

    for part in ("**Why it has not:**", "**What a feature would lack:**", "**If it does:**"):
        assert part in platform, part
    assert "never one the skill picks" in platform
    assert "Never predict what a named company will do" in platform
    assert 'never write that it "will not" or "cannot" build something' in platform
    assert "marked as the founder's view" in platform
    assert "With no platform named, ask which larger product the buyer already uses; never name one" in platform


def test_the_lines_and_the_slide_use_only_the_founders_facts() -> None:
    lines = _unwrapped(_section("## Why customers pick us"))
    slide = _unwrapped(_section("## The competition slide"))
    substitutes = _unwrapped(_section("## The substitutes story"))

    assert "The reason and the evidence are the founder's, quoted" in lines
    assert "no line runs a competitor down with a fact the founder did not give" in lines
    assert "Each substitute gets a line too" in lines
    for part in ("**Headline:**", "**Table:**", "**2x2:**", "**Speaker note:**"):
        assert part in slide, part
    assert "Draw it as a text grid" in slide and "split by the halves" in slide
    assert 'listed under the grid as "not placed", never drawn' in slide
    assert "never the two that put the company alone in a corner" in slide
    assert "Every figure is quoted as stated" in substitutes


def test_the_patterns_include_the_ones_a_partner_discounts_first() -> None:
    table = _section("## Patterns a partner is likely to discount")
    patterns = " ".join(row.split("|")[1] for row in table.splitlines() if row.startswith("| ") and "---" not in row)

    assert "| Pattern" in table
    for phrase in ("No competitors", "grid of logos", "alone in the best corner", "5 on every axis", "no anchors"):
        assert phrase in patterns, phrase
    assert "they will never build this" in patterns


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = _first_column("### Stage A: attack", _LENS_HEAD)

    assert len(lenses) >= _MIN_LENSES
    for lens in lenses:
        assert not any(re.search(rf"\b{name}\b", lens.lower()) for name in _PEOPLE_AND_FIRMS), lens
    assert {"Coverage", "Honest axes", "Why customers pick us", "Platform risk"} <= set(lenses)
    assert "quoted word for word" in attack
    assert "subagent" in attack and "only the founder's material and its lens brief" in attack
    assert "one after another" in attack and "do no arithmetic" in attack
    assert "not even about a competitor or platform you have heard of" in attack
    assert _RAISE_IT_ANYWAY in attack
    assert "as parallel subagents, however short the material" in attack


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))
    handoff = _unwrapped(_section("### Stage B: refute").split("\n\nThe refute brief:\n\n", 1)[0])

    assert "using only the founder's material" in refute
    assert "the Pattern column of the patterns table above" in handoff
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "Bring in no outside fact about the company, its market or its competitors",
        "is an outside fact, however well known the company",
        "How a partner is likely to read a line is not an outside fact",
        "never answers an objection",
        "When you cannot decide, return Kept",
        "invents nothing on the founder's behalf",
    ):
        assert rule in refute, rule
    for verdict in ("Dropped, answered:", "Dropped, not grounded:", "Kept:"):
        assert verdict in refute, verdict
    assert "Quote the founder's line that answers it" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_survivors_are_ranked_with_quotes_and_feed_the_drafts() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    answering = _unwrapped(_section("## Answering"))

    assert "the founder's line, quoted word for word" in rank
    assert "no percentages and no score" in rank
    assert "biggest issues" in rank and "carried into the slide draft" in rank
    assert "**Adversarial review:**" in answering and "**Dropped,**" in answering
    assert _SURVIVOR_COLUMNS.search(answering)
    for part in ("**The map:**", "**Axes:**", "**Placements:**", "**The competition slide:**", "**Open asks:**"):
        assert part in answering, part
    assert "not investment, legal or tax advice" in answering
    assert "a lawyer should review comparative claims" in answering


def test_without_a_subagent_tool_the_lenses_run_before_step_1_and_the_answer_says_so() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    note = "without a subagent tool, run Stage A of the adversarial review first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    assert "**Run the adversarial review**" in steps
    assert "every surviving objection quotes a line that is in the material word for word" in steps
    assert "no total, average or rank of placements appears" in steps
    assert "run Stage A first, before step 1" in attack and "less independent than subagents" in attack
    assert "less independent than separate subagents" in _unwrapped(_section("## Answering"))


def test_it_never_speaks_as_an_investor_or_names_a_firm_that_fits() -> None:
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])
    limits = _unwrapped(_section("## Limits"))

    assert "never speaks as a named investor or firm" in intro and "never names a firm the map fits" in intro
    assert "never names a firm the map fits" in limits and "offers the lenses instead" in limits
    assert "sends nothing anywhere" in limits


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "not a recorded run" in text, path.name
        assert "## Recorded answer" not in text, path.name


def test_the_evals_are_numbered_in_letter_order() -> None:
    for number, path in enumerate(_EVALS, start=1):
        title = _EVAL_TITLE.match(path.read_text(encoding="utf-8"))
        assert title is not None and int(title.group(1)) == number, path.name


def test_every_eval_makes_no_calculator_call() -> None:
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        assert _NO_CALL in text, path.name
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


def test_every_quote_in_an_eval_answer_is_in_its_prompt() -> None:
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        for quoted in _DOUBLE_QUOTED.findall(answer):
            assert quoted in prompt, (path.name, quoted)


def test_no_eval_answer_carries_a_figure_its_prompt_does_not() -> None:
    """Figures are quoted as stated, never computed: an answer's digits are its prompt's, plus the 1-to-5 scale."""
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        assert set(_DIGITS.findall(answer)) <= set(_DIGITS.findall(prompt)) | _SCALE, path.name
        assert "%" not in answer, path.name


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    dropping = [path for path in _EVALS if "Dropped, answered" in _eval_parts(path)[1]]
    assert dropping
    for path in dropping:
        prompt, answer = _eval_parts(path)
        objection, dropped = answer.split("Dropped, answered", 1)
        # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
        # founder's material, not the line the objection was about.
        answering_line = _DOUBLE_QUOTED.findall(dropped)[0]
        assert answering_line in prompt
        assert answering_line not in _DOUBLE_QUOTED.findall(objection)


def test_a_no_competitors_request_gets_the_pattern_and_no_name() -> None:
    (path,) = (path for path in _EVALS if "We have no real competitors" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "no-competitors pattern" in answer
    assert "It names no competitor itself" in answer
    assert "drafts no slide" in answer and "draws no 2x2" in answer


def test_a_request_to_play_a_named_firm_and_score_rivals_is_declined() -> None:
    (path,) = (path for path in _EVALS if "Pretend you're a partner" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "declines in one line to speak as a partner of a named firm" in answer
    assert "It places no company on any axis" in answer and "`not placed`" in answer
    assert "looks nothing up" in answer and "names no firm as a fit" in answer


def test_an_unverified_fact_drops_no_objection_in_the_evals() -> None:
    unverified = [path for path in _EVALS if re.search(r"unverified|no source", _eval_parts(path)[0])]
    assert unverified
    for path in unverified:
        answer = _eval_parts(path)[1]
        assert "labelled unverified" in answer and "off the slide" in answer, path.name


def test_the_two_by_two_follows_the_halves_in_every_eval_that_draws_one() -> None:
    drawn = [path for path in _EVALS if "The 2x2" in _eval_parts(path)[1]]
    assert drawn
    for path in drawn:
        answer = _eval_parts(path)[1]
        assert "follows the halves alone" in answer and "high-high quadrant" in answer, path.name
        assert "No total, average, rank or winner appears" in answer, path.name
