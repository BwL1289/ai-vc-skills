"""The vc-intro-email skill keeps its shape: its frontmatter, its drafts, its figure rules, its reader pass and evals.

The skill drafts, from the founder's own material only, a note asking a mutual contact for an intro with a blurb they
can forward, a cold email and two follow-ups, each with one ask and every figure quoted exactly as the founder gave it.
A reader pass flags hype words, claims with no source the founder can show and figures that disagree across the
founder's documents, and hands the source and disagreement flags to the vc-claims-check skill. It never looks up an
investor or a contact detail, never sends, adds no personal data beyond what the founder pastes, names no calculator
tool and cites no source, since none was read for it. Each eval has a prompt, an expected tool call and an expected
answer, makes no calculator call, quotes only lines its prompt contains and carries no figure its prompt lacks.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-intro-email" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-intro-email").glob("*.md"))
_EVAL_COUNT = 4
_NO_CALL = "## Expected tool call\n\nNone: no calculator call."
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_RECORDED = "## Recorded answer"
# A recorded run's verdict line, in the shape the repository's recorded evals use.
_VERDICT_LINE = re.compile(r"\*\*(?:Pass|Partial|Fail)\b[^*]*\*\*")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_URL = re.compile(r"https?://\S+")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "write an intro blurb",
    "draft a forwardable email",
    "write a cold email to a VC",
    "help me follow up with an investor",
    "ask for a warm intro to a fund",
)
_DESCRIPTION_WORDS = (
    "founder's own material only",
    "forwardable intro blurb",
    "a cold email, and two follow-ups",
    "every figure quoted exactly as the founder gave it",
    "hype words",
    "figures that disagree across the founder's documents",
    "vc-claims-check skill",
    "never looks up the investor or anyone's contact details, never sends",
)
# The brief's hand-offs: messaging, the update to prospective investors, and the claims the reader pass flags.
_HANDOFFS = {
    "vc-positioning": "Messaging (the one-liner, the story and the say-and-avoid list): the vc-positioning skill.",
    "vc-prospective-investor-update": "vc-prospective-investor-update skill (preview)",
    "vc-claims-check": "the vc-claims-check skill (preview)",
}
_OTHER_HANDOFFS = ("vc-deck-review", "vc-pass-debrief")
_DRAFTS = (
    "**The note to the connector:**",
    "**The forwardable blurb:**",
    "**The cold email:**",
    "**Follow-up 1:**",
    "**Follow-up 2:**",
)
_PATTERN_HEAD = re.compile(r"^\|\s*Pattern\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_DIGITS = re.compile(r"\d+")
_EVAL_TITLE = re.compile(r"\A# Eval (\d+): ")
_ADDRESS_LINE = "`[the investor's email, from you]`"
_CONNECTOR_LINE = "`[the connector's email, from you]`"
# A made-up fund, product or company label, or a brand-like fund name: an answer may name only those its prompt names.
_LABELLED = re.compile(
    r"\b[A-Z][a-z]+ (?:Seed|Capital|Ventures|Partners|Fund)\b" r"|\b(?:Fund|Product|Suite|Company) [A-Z]{1,2}\b"
)


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


def _pattern_rows() -> list[list[str]]:
    """The reader pass's pattern table, each body row as its stripped cells."""
    body = _section("## Reader pass")
    head = _PATTERN_HEAD.search(body)
    assert head is not None
    table = body[head.start() :]
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(table)]
    return rows[2:]


def _eval_parts(path: Path) -> tuple[str, str]:
    """An eval's prompt and expected answer, each unwrapped."""
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-intro-email"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    assert "Use when" in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for word in _DESCRIPTION_WORDS:
        assert word in description, word
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_skill_it_hands_off_to_exists_and_the_brief_s_hand_offs_are_there() -> None:
    when = _unwrapped(_section("## When to use it"))

    for name, line in _HANDOFFS.items():
        assert line in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    for name in _OTHER_HANDOFFS:
        assert f"the {name} skill" in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-pass-debrief skill (preview)" in when
    # Back to the skill that keeps the investor list and the tracker, once the email is written.
    assert (
        "The investor list and the tracker (who to write to next, who passed and why, what is left of the round): the "
        "vc-raise-plan skill (preview)."
    ) in when
    assert (_ROOT / "skills" / "vc-raise-plan" / "SKILL.md").is_file()


def test_it_names_no_calculator_tool_and_cites_no_source() -> None:
    sources = _unwrapped(_section("## Sources")).strip()
    urls = set(_URL.findall(_TEXT))
    for path in _EVALS:
        urls |= set(_URL.findall(path.read_text(encoding="utf-8")))

    assert _TOOL_NAME.findall(_TEXT) == []
    assert "No arithmetic and no calculator tool" in _unwrapped(_section("## Limits"))
    assert urls <= set(_READ_SOURCES) and urls == set()
    assert sources.startswith("None.") and "unverified" in sources


def test_it_drafts_the_five_pieces_each_with_one_ask() -> None:
    drafts = _unwrapped(_section("## The drafts"))

    for draft in _DRAFTS:
        assert draft in drafts, draft
    assert "Each draft is short, in the founder's voice, with one ask" in drafts
    assert "with no connector named, leave out the note and the blurb" in drafts
    assert "the note to the connector goes with the blurb" in drafts
    assert "asking them to check with the investor first that the intro is welcome" in drafts
    assert "so the connector can forward it unchanged" in drafts
    assert "at most five short sentences" in drafts
    assert "the skill suggests no interval" in drafts
    assert "never a guilt line" in drafts


def test_every_figure_is_quoted_exactly_and_figures_that_disagree_go_into_no_draft() -> None:
    figures = _unwrapped(_section("## Figures as the founder gave them"))

    assert "every figure keeps the founder's own words, units, period and form" in figures
    assert "never turned into a yearly figure" in figures
    assert "goes into no draft until the founder says which is right" in figures
    assert 'no growth rate, multiple, total or "doubled" worked out from two figures' in figures
    assert "the skill never says whether the claim holds" in figures


def test_the_reader_pass_flags_hype_unsourced_claims_and_disagreeing_figures_for_the_claims_skill() -> None:
    rows = _pattern_rows()
    patterns = " ".join(row[0] for row in rows)
    reader = _unwrapped(_section("## Reader pass"))
    to_claims = [row for row in rows if "vc-claims-check" in row[2]]

    assert "Hype words" in patterns and "no source the founder can show" in patterns
    assert "disagrees with the same figure in another of the founder's documents" in patterns
    assert "Other investors named or hinted at" in patterns
    assert len(to_claims) >= 2
    assert "is handed to the vc-claims-check skill" in reader
    assert "Every flag revises the drafts" in reader
    assert "this skill names that check and does not run it here" in reader
    assert "Every row is this skill's own judgment, unverified" in reader


def test_it_looks_no_one_up_and_adds_no_personal_data() -> None:
    personal = _unwrapped(_section("## Personal data"))
    limits = _unwrapped(_section("## Limits"))
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])

    assert "adds no name, title, firm, email address, phone number or link, and looks no one up" in personal
    assert _ADDRESS_LINE in personal and _CONNECTOR_LINE in personal
    assert "The forwardable blurb has no address line: the connector forwards it" in personal
    assert "the connector is named only with the founder's say-so" in personal
    assert "It keeps nothing between conversations" in personal
    assert "never names an investor to write to, never looks up an investor" in intro
    assert "It drafts only. It sends nothing" in limits


def test_it_never_speaks_as_an_investor_or_takes_a_named_voice() -> None:
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])
    limits = _unwrapped(_section("## Limits"))
    steps = _unwrapped(_section("## Steps"))

    assert "The founder is always the user" in intro
    assert (
        "never plays an investor, never speaks as a named investor or firm, never writes in a named person's voice"
    ) in intro
    assert "never role-plays or writes in the voice of a named investor, firm or author" in limits
    assert "no sentence speaks as an investor or imitates a named person" in steps


def test_with_no_material_it_writes_no_email() -> None:
    inputs = _unwrapped(_section("## Inputs"))

    assert "never offer a figure or a reason to fill in" in inputs
    assert "With no material at all" in inputs and "write no email" in inputs
    assert "The skill adds no reason of its own" in inputs


def test_the_steps_and_answer_keep_the_rules() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    assert "**Run the reader pass**" in steps
    assert "no figure that disagrees across documents is in a draft" in steps
    assert "each draft has one ask" in steps
    for part in ("**The drafts,**", "**Reader pass:**", "**Figures used:**", "**Open asks:**", "**Close:**"):
        assert part in answering, part
    assert "not investment, legal or tax advice" in answering and "the founder sends every email" in answering
    assert "declines in one line and writes in the founder's own voice" in _unwrapped(_section("## Limits"))


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name
        if _RECORDED not in text:
            assert "not a recorded run" in text and "has not been run in a live session" in text, path.name
            continue
        # A recorded run: the intro says so, the excerpt follows the expected answer, and it opens with its verdict
        # and says whether the skill changed since.
        assert text.index(f"\n{_RECORDED}\n") > positions[-1], path.name
        assert '"Recorded answer" is an excerpt of a recorded run' in _unwrapped(text.split("\n## ", 1)[0]), path.name
        recorded = _section(_RECORDED, text)
        assert _VERDICT_LINE.match(recorded.strip("\n").split("\n\n")[1]), path.name
        assert "Since this run" in _unwrapped(recorded) or "led to no change in it" in _unwrapped(recorded), path.name
        assert _fences("json", recorded) == [] and _fences("text", recorded) == [], path.name


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


def test_every_eval_that_drafts_leaves_the_address_line_for_the_founder() -> None:
    drafting = [path for path in _EVALS if re.search(r"[Nn]othing is sent", _eval_parts(path)[1])]
    assert drafting
    for path in drafting:
        assert _ADDRESS_LINE in _eval_parts(path)[1], path.name


def test_no_eval_answer_names_a_company_fund_or_product_its_prompt_does_not() -> None:
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        assert set(_LABELLED.findall(answer)) <= set(_LABELLED.findall(prompt)), path.name


def test_the_note_to_the_connector_is_addressed_to_the_connector() -> None:
    (path,) = (path for path in _EVALS if "can introduce me" in _eval_parts(path)[0])

    assert _CONNECTOR_LINE in _eval_parts(path)[1]


def test_one_eval_writes_no_multiple_and_quotes_both_figures() -> None:
    (path,) = (path for path in _EVALS if "tripled" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert 'It does not write "tripled", nor any multiple or growth rate of its own' in answer
    assert 'from "$20k MRR in June" to "$50k MRR in October"' in answer
    assert "without saying whether it holds" in answer
    assert "It declines to find any email address" in answer
    assert "It declines in one line to write in a named person's voice" in answer


def test_one_eval_keeps_two_disagreeing_figures_out_of_every_draft() -> None:
    (path,) = (path for path in _EVALS if "31 paying customers" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "Neither goes into a draft" in answer and "handed to the vc-claims-check skill" in answer
    assert "left out and flagged as pressure" in answer
    assert "no total revenue is worked out" in answer


def test_one_eval_with_no_material_writes_no_email_and_picks_no_investor() -> None:
    (path,) = (path for path in _EVALS if "a top fintech VC" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "It names no investor or firm to write to and looks nothing up" in answer
    assert "It writes no email with a figure" in answer
    assert "asks in one message" in answer
