"""The vc-pass-debrief skill keeps its shape: its frontmatter, its reason groups, its readings, its replies and evals.

The skill reads the passes a founder pastes, quotes each word for word, groups them by the reason given, labels every
common reading unverified and never says what an investor meant, maps each reason to the fix or the skill that works
on it (traction, market, team and story, deck, among others), lists every "come back when" condition beside the
founder's own figure without working out the gap, and drafts short replies that keep the door open and ask for at most
one referral. It sends nothing, looks nobody up, names no fund to try next, repeats no contact detail, names no
calculator tool and cites no source, since none was read for it. Each eval has a prompt, an expected tool call and an
expected answer, makes no calculator call, quotes only lines its prompt contains and carries no figure its prompt lacks.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-pass-debrief" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-pass-debrief").glob("*.md"))
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
    "a VC passed on us",
    "what does this pass email mean",
    "why do investors keep passing",
    "help me reply to a VC rejection",
    "what should we change after these passes",
)
_DESCRIPTION_WORDS = (
    "founder",
    "word for word",
    "labelled unverified",
    "never says what an investor really meant",
    "come back when",
    "at most one referral",
    "sends nothing",
)
# The brief's four mappings, each a reason group and the skill whose name its fix cell gives.
_MAPPINGS = {
    "Traction": "vc-metrics-readiness",
    "Market": "vc-market-sizing",
    "Team and story": "vc-positioning",
    "Deck and materials": "vc-deck-review",
}
_GROUPS = (
    "Traction",
    "Market",
    "Team and story",
    "Deck and materials",
    "Competition",
    "Belief in a claim",
    "Round and terms",
    "Product",
    "Stage or timing",
    "Fund fit",
    "No reason given",
)
_HANDOFF_SKILLS = (
    "vc-metrics-readiness",
    "vc-market-sizing",
    "vc-positioning",
    "vc-deck-review",
    "vc-competitive-landscape",
    "vc-claims-check",
    "vc-round-sizing",
    "vc-deal-math",
    "vc-partner-meeting",
    "vc-taste-check",
    "vc-prospective-investor-update",
)
_READING_LABEL = '"unverified: a common reading, not what this investor meant"'
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_DIGITS = re.compile(r"\d+")
_EVAL_TITLE = re.compile(r"\A# Eval (\d+): ")
# Names the skill must never take a voice from: it writes in the founder's voice only.
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "graham", "stebbings", "20vc")


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


def _table(heading: str) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    body = _section(heading)
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(body)]
    return rows[2:]


def _eval_parts(path: Path) -> tuple[str, str]:
    """An eval's prompt and expected answer, each unwrapped."""
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-pass-debrief"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    assert "Use when" in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for word in _DESCRIPTION_WORDS:
        assert word in description, word
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_skill_it_hands_off_to_exists() -> None:
    when = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_it_names_no_calculator_tool_and_cites_no_source() -> None:
    sources = _unwrapped(_section("## Sources")).strip()
    urls = set(_URL.findall(_TEXT))
    for path in _EVALS:
        urls |= set(_URL.findall(path.read_text(encoding="utf-8")))

    assert _TOOL_NAME.findall(_TEXT) == []
    assert "No arithmetic and no calculator tool" in _unwrapped(_section("## Limits"))
    assert urls <= set(_READ_SOURCES) and urls == set()
    assert sources.startswith("None.") and "unverified" in sources


def test_the_reason_groups_are_the_fixed_words_and_map_to_their_skills() -> None:
    rows = _table("## The reason groups")
    groups = [row[0] for row in rows]
    fixes = {row[0]: row[2] for row in rows}

    assert groups == list(_GROUPS)
    for group, skill in _MAPPINGS.items():
        assert f"The {skill} skill" in fixes[group], group
    assert fixes["Competition"].startswith("The vc-competitive-landscape skill")
    for group in ("Fund fit", "No reason given"):
        assert fixes[group].startswith("Nothing to fix"), group


def test_passes_are_grouped_by_their_words_never_by_a_guess() -> None:
    groups = _unwrapped(_section("## The reason groups"))

    assert "**Group by the words, never by a guess.**" in groups
    assert "never to the reason the founder suspects or the agent would guess" in groups
    assert '**"Too early" is read both ways.**' in groups
    assert "**Fund fit and No reason given map to no fix.**" in groups
    assert "give no percentage, share or rate" in groups


def test_every_reading_is_labelled_unverified_and_none_says_what_an_investor_meant() -> None:
    readings = _unwrapped(_section("## Common readings"))
    rows = _table("## Common readings")
    (bare,) = (row for row in rows if row[0].startswith('"Not a fit at this time"'))

    assert _READING_LABEL in readings
    assert "None is presented as a fact, none says what the investor thinks or felt" in readings
    assert "none adds a reason the pass does not give" in readings
    assert 'Asked what an investor "really" meant, say once that the text does not show it' in readings
    assert "give none" in bare[1]
    assert len(rows) >= len(_GROUPS) - 2
    assert "never says what an investor really meant or thinks" in _unwrapped(_section("## Limits"))


def test_the_come_back_list_quotes_both_figures_and_works_out_no_gap() -> None:
    come_back = _unwrapped(_section("## Come back when"))

    assert "Quote the condition and the founder's figure as stated, side by side" in come_back
    assert "Never work out the gap, a share of the way there, a growth rate or the month it will be met" in come_back
    assert "say they cannot be compared as stated" in come_back and "never convert one" in come_back
    assert "The skill keeps no tracker between conversations" in come_back


def test_each_reply_keeps_the_door_open_and_asks_for_at_most_one_referral() -> None:
    replies = _unwrapped(_section("## The replies"))

    for part in ("**Thanks**", "**Keeps the door open:**", "**Asks for at most one referral,**", "**Nothing else:**"):
        assert part in replies, part
    assert "without arguing with the reason" in replies
    assert "Never more than one, and never a list of funds" in replies
    assert "no other investor named or hinted at" in replies and "no deadline or pressure" in replies
    assert "at most five sentences" in replies
    assert "The skill sends nothing" in replies


def test_it_adds_no_contact_detail_and_names_no_fund_to_try() -> None:
    personal = _unwrapped(_section("## Personal data"))
    limits = _unwrapped(_section("## Limits"))
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])

    assert "The skill adds no name, title, email address or link, and looks no one up" in personal
    assert "is not repeated in the answer" in personal
    assert "It keeps nothing between conversations" in personal
    assert "never names an investor or firm to try next" in intro
    assert "names no fund or person to try next" in limits


def test_a_pass_with_no_words_gets_no_reading_and_no_reply() -> None:
    inputs = _unwrapped(_section("## Inputs"))

    assert "never offer a likely reason to fill in" in inputs
    assert "quoted as the founder's retelling and marked so" in inputs
    assert "With no pass pasted or retold at all, give no reading and draft no reply" in inputs


def test_the_steps_and_answer_keep_the_rules() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "every reading is labelled unverified and none says what an investor meant or thinks" in steps
    assert "each reply asks for at most one referral" in steps
    for part in ("**The pattern:**", "**The passes:**", "**Come back when:**", "**Replies:**", "**Open asks:**"):
        assert part in answering, part
    assert "not investment, legal or tax advice" in answering and "the founder sends the replies" in answering


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
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        assert set(_DIGITS.findall(answer)) <= set(_DIGITS.findall(prompt)), path.name
        assert "%" not in answer, path.name


def test_one_eval_keeps_the_come_back_bar_beside_the_founders_figure() -> None:
    (path,) = (path for path in _EVALS if "Come back when you're at" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "both as stated" in answer
    assert "No gap, share of the way there or month to reach it is worked out" in answer
    assert "the vc-metrics-readiness skill" in answer and "the vc-market-sizing skill" in answer
    assert "Every reading is labelled unverified" in answer


def test_one_eval_declines_to_read_minds_borrow_a_voice_or_add_pressure() -> None:
    (path,) = (path for path in _EVALS if "they obviously think" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "It declines to say what Jamie thinks" in answer
    assert "It declines in one line to write in a named person's voice" in answer
    assert "names and hints at no other fund" in answer
    assert "the vc-positioning skill" in answer


def test_one_eval_maps_fund_fit_and_a_bare_pass_to_nothing_and_names_no_fund() -> None:
    (path,) = (path for path in _EVALS if "Which funds should I go to instead?" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "under Fund fit, marked nothing to fix in the company" in answer
    assert "under No reason given. No reason is guessed" in answer
    assert "It names no fund or person to try next and looks nothing up" in answer
    assert "It adds no email address" in answer


def test_no_eval_answer_takes_a_named_persons_voice() -> None:
    for path in _EVALS:
        answer = _eval_parts(path)[1].lower()
        assert not any(re.search(rf"\b{name}\b", answer) for name in _PEOPLE_AND_FIRMS), path.name
