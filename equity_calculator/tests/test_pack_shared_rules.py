"""Rules the review skills share word for word, so one founder input gets the same treatment whichever skill runs.

Four sentences are copied into several skills and must stay identical there:

- Which monthly spend goes into ``equity_runway_plan`` for a runway claim on a SAFE or note raise, and what happens
  while a planned change's start month, its monthly spend or its monthly revenue is missing. When the skills
  disagreed, the same founder input ($400,000 in the bank, a $1,000,000 raise, $80,000 a month today and $120,000
  planned after the raise) gave 11.67 months in one skill, which sent the planned $120,000 as the only phase, and 17.50
  in another, which sent today's $80,000 and left the rise out. The founder's plan, $80,000 and then $120,000 from
  month 4, gives 12.67. A plan with the rise and no start month cannot be run, so the call waits for the month and the
  runway line says so; a rise with its month and no amount cannot be run either, so it waits the same way, under its
  own label, and so does one with no word on its revenue: the tool reads a phase with no revenue as none, which on one
  plan ($300,000 in the bank, a $1,200,000 raise, $60,000 a month and $15,000 of revenue, then $95,000 from month 4)
  gives the raise 17.37 months, against 20.06 with the $15,000 kept. Every skill that sends a SAFE or note raise's
  runway to that tool carries the sentence.
- No working out how two of the founder's figures relate in founder-facing text: a live positioning run wrote that
  users "more than doubled", which neither the founder nor the calculator said. Every skill that writes rewrites,
  lines, draft answers, update text or deck fixes for the founder carries the sentence, except the partner-meeting
  skill, whose own ban says the same in other words and is checked here too.
- A lean refute pass. One refute subagent per objection is the default, and the deck review's seven lenses may raise up
  to three objections each, so one review could start more than twenty refute subagents, as a real deck run showed.
  Every skill whose lenses feed a refute pass of one subagent per objection (or per question) now names one exception,
  word for word: with more than eight, one subagent per lens, given an instruction to judge each of its lens's
  objections as if it were the only one, with a verdict of its own; one no lens raised gets its own subagent, and one
  that comes back without its own verdict stays Kept. The section the answer is composed from says, in the same words
  in every such skill, that a lean pass is less independent and that the founder may ask for the full pass. The claims
  and round-sizing skills are not on the list: one skeptic raises at most three attacks there, and a test says so. The
  lean paragraph stands as its own paragraph, wrapped like the rest, so no line cap is met by joining lines.
- A file the founder gives is read, never pasted. Every skill with an Inputs section, and the deal-math skill's first
  step, reads a file the agent can open (a PDF, HTML, a slides export, Markdown), lists what it holds place by place in
  the file's own words, lists a place it could not read as not read and asks for it, never reads a figure off a chart
  or a picture, and never asks for a paste of what it read; and every "When to use it" bullet that names pasted
  material says it may come as a file. No line of those two sections is wider than 120 characters.

A refute pass checks its answering line as the quote check does, spacing and line breaks aside: a line that wraps in
the founder's file is still the founder's line, and a line that is not there does not drop the item.

Every eval that records a live run states the README's verdict rule in its first paragraph and opens its recording
with a verdict under it: Pass when every clause of the pass sentence is met, Partial when exactly one is missed or met
only in part, Fail when two or more are missed. The verdict counts the pass sentence as it was at the run. Each
recorded eval's sentence at its run is pinned here; one whose sentence has changed since says so in its first
paragraph and its recording, names the clauses that changed, and says how the run reads against today's sentence.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SKILLS = _ROOT / "skills"
_RECORDED = "\n## Recorded answer\n"
_RECORDED_EVALS = sorted(
    path for path in (_ROOT / "evals").glob("*/*.md") if _RECORDED in path.read_text(encoding="utf-8")
)
_VERDICT_RULE = (
    "The verdict is Pass when every clause of that sentence is met, Partial when exactly one clause is missed or met"
    " only in part, and Fail when two or more are missed"
)
_THEN = "graded against the pass sentence this eval had then"
_THEN_VERDICT = re.compile(r"\*\*(Pass|Partial|Fail), against the pass sentence this eval had then[;:]")
_TODAY = "today's sentence"
_MEMO_HANDOFF = (
    "The memo a champion partner is likely to write for the partnership: the vc-investor-memo skill (preview)."
)
# Every recorded eval with the pass sentence it had when its run was recorded: the first 12 hex digits of the SHA-256
# of that sentence, its line breaks taken out (_pass_sentence). A recording adds its eval here. A pass sentence changed
# after its run keeps its digest here, so the test sees the change and asks for the README's rule in that file.
_PASS_SENTENCE_AT_RUN = {
    "company-ac-a-cap-table-the-deck-misstates": "0b1fd724fbe7",
    "company-ag-a-runway-that-ignores-planned-hires": "341cf1179008",
    "company-am-run-rate-called-arr": "d554795c549d",
    "company-ar-a-2x-participating-seed": "8d634ea67d45",
    "company-aw-bottom-up-against-the-deck": "d7ee0daae37d",
    "company-be-a-moved-target-and-a-redefined-customer-count": "686844b0304f",
    "company-bm-a-memo-that-hides-its-biggest-risk": "a949dba188d6",
    "company-e-phrases-that-cost-the-meeting": "b0c28683e6ff",
    "company-f-numbers-go-to-the-calculator": "4245cbea0f66",
    "company-g-an-objection-the-material-answers": "1ab43e33700b",
    "company-h-asked-to-imitate-named-investors": "5d5c9d89c8dd",
    "company-j-figures-that-disagree": "701e7373824c",
    "company-k-patterns-a-vc-discounts": "b64ad6e93730",
    "company-l-an-attack-the-material-does-not-ground": "c59bfc8ce84d",
    "company-m-use-of-funds-that-does-not-add-up": "330879e16c4d",
    "company-r-a-runway-answer-the-calculator-checks": "891fe89e539a",
    "company-t-a-no-that-answers-the-objection": "6a76e240266a",
    "company-w-how-much-should-we-raise": "b5ae91a9f0a7",
}
# The recordings re-graded from their recorded answers: one that carried an outside grader's word on an unchanged pass
# sentence, and every one whose pass sentence changed after its run, each counted on the sentence it had then.
_REGRADED = {
    "company-ar-a-2x-participating-seed": "**Pass, with shortfalls against the expected answer",
    "company-ac-a-cap-table-the-deck-misstates": (
        "**Fail, against the pass sentence this eval had then: two clauses missed.**"
    ),
    "company-bm-a-memo-that-hides-its-biggest-risk": (
        "**Pass, against the pass sentence this eval had then; it missed the four clauses added since.**"
    ),
    "company-aw-bottom-up-against-the-deck": (
        "**Pass, against the pass sentence this eval had then; it missed the one clause added since.**"
    ),
    "company-am-run-rate-called-arr": (
        "**Pass, against the pass sentence this eval had then; it missed the one clause added since.**"
    ),
    "company-be-a-moved-target-and-a-redefined-customer-count": (
        "**Fail, against the pass sentence this eval had then: two clauses missed and one met only in part.**"
    ),
    "company-r-a-runway-answer-the-calculator-checks": (
        "**Partial, against the pass sentence this eval had then: one clause missed.**"
    ),
    "company-t-a-no-that-answers-the-objection": (
        "**Fail, against the pass sentence this eval had then: two clauses missed.**"
    ),
}
_UNCHANGED_REGRADE = "company-ar-a-2x-participating-seed"
_PLAN_PHASES = (
    "On a SAFE or note raise, the `plan` case's phases are the founder's own figures: today's monthly spend and revenue"
    " as the first phase, from month 1, and each change the founder plans (more spend after the raise, say) as a later"
    " phase from the month the founder names, each asked for by name when missing (`[planned monthly spend and"
    " revenue, from which month]`), never assumed. Until a planned change's start month, its monthly spend and its"
    ' monthly revenue are all given, make no runway call and give no runway figure; mark the runway line "not checked:'
    ' waiting for [the month the planned spend starts]" while the month is missing, "not checked: waiting for [the'
    ' planned monthly spend from that month]" while the month is given and the spend is missing, or "not checked:'
    ' waiting for [the planned monthly revenue from that month]" while only the revenue is missing.'
)
# The three labels the runway line takes while a planned change waits: for its start month, then for its monthly
# spend, then for its monthly revenue.
_WAITING_FOR_MONTH = '"not checked: waiting for [the month the planned spend starts]"'
_WAITING_FOR_SPEND = '"not checked: waiting for [the planned monthly spend from that month]"'
_WAITING_FOR_REVENUE = '"not checked: waiting for [the planned monthly revenue from that month]"'
_NO_COMPARISON = (
    "Never work out how two of the founder's figures relate (a difference, a sum, a ratio or multiple, a share left"
    ' over, "doubled") in a rewrite, a line or a table cell unless the founder\'s material states it or a tool returned'
    ' it; quote both figures as stated instead ("from 2,000 to 4,500", never "more than doubled").'
)
_SAFE_RUNWAY_SKILLS = (
    "vc-claims-check",
    "vc-deal-math",
    "vc-deck-review",
    "vc-diligence-questions",
    "vc-investor-memo",
    "vc-metrics-readiness",
    "vc-partner-meeting",
    "vc-positioning",
)
_FOUNDER_TEXT_SKILLS = (
    "vc-competitive-landscape",
    "vc-positioning",
    "vc-deck-review",
    "vc-claims-check",
    "vc-deal-math",
    "vc-round-sizing",
    "vc-prospective-investor-update",
    "vc-current-investor-update",
    "vc-investor-memo",
    "vc-diligence-questions",
    "vc-pass-debrief",
)
_PARTNER_MEETING_BAN = 'never a difference, sum or ratio of two figures the founder gave ("from $80k to $120k a month"'
# The lean refute pass, with {noun} filled by what the skill's lenses raise: an objection, or a question.
_LEAN_REFUTE = (
    "**Lean mode,** the one exception: with more than eight {noun}s after the quote check, the refute pass may instead"
    " run one subagent per lens, all in a single message. Each gets what a one-{noun} subagent gets, but with every"
    " {noun} from its lens (one that two lenses raised goes to one of them only; one that no lens raised gets a"
    ' subagent of its own), and with this instruction, word for word: "Apply the brief to each {noun} as if it were the'
    " only one you were given. Return one verdict for each, with its own quote where the verdict needs one. Never let"
    ' one {noun}, its verdict or its answering line decide another." Any {noun} that comes back without a verdict of'
    " its own stays Kept. The answer then says the refute pass ran per lens, which is less independent than one"
    " subagent per {noun}, and that the founder may ask for the full pass, one subagent per {noun}."
)
# What the answer says after a lean refute pass, in the section the agent composes the answer from.
_LEAN_ANSWER = (
    "When the refute pass ran per lens (lean mode), say so, say it is less independent than one subagent per {noun},"
    " and say the founder may ask for the full pass."
)
_LEAN_PARAGRAPH = "\n\n**Lean mode,** the one exception:"
_LINE_WIDTH = 120
_LEAN_REFUTE_SKILLS = {
    "vc-competitive-landscape": "objection",
    "vc-current-investor-update": "objection",
    "vc-deck-review": "objection",
    "vc-diligence-questions": "question",
    "vc-investor-memo": "objection",
    "vc-market-sizing": "objection",
    "vc-metrics-readiness": "objection",
    "vc-partner-meeting": "question",
    "vc-positioning": "objection",
    "vc-prospective-investor-update": "objection",
    "vc-taste-check": "objection",
    "vc-term-sheet-review": "objection",
}
_READ_THE_FILE = (
    "When the founder gives a file the agent can read (a PDF, HTML, a slides export, Markdown), read it yourself and"
    " list what it holds place by place (slide by slide for a deck), in the file's own words, so the founder sees what"
    " was read from each. A place you could not read (a slide that is only a picture, a page whose text did not come"
    " out, a file that opened only in part) is listed as not read and asked for, never filled in from its title or the"
    " places around it, and a figure is never read off a chart or a picture. Ask only for what you could not read and"
    " what the file does not show (speaker notes, the figures behind a chart, an input below that it leaves out), and"
    " never ask the founder to paste what you already read."
)
_READ_THE_FILE_SKILLS = (
    "vc-claims-check",
    "vc-competitive-landscape",
    "vc-current-investor-update",
    "vc-deck-review",
    "vc-diligence-questions",
    "vc-investor-memo",
    "vc-market-sizing",
    "vc-metrics-readiness",
    "vc-partner-meeting",
    "vc-pass-debrief",
    "vc-positioning",
    "vc-prospective-investor-update",
    "vc-round-sizing",
    "vc-taste-check",
    "vc-term-sheet-review",
)
_FILE_TOO = "Any of these may come as a file the agent can read in this session."
# The one paste bullet that names its file in its own words, inside its list of what may be pasted.
_FILE_TOO_OWN_WORDING = {"vc-term-sheet-review": "or a term sheet file the agent can read in this session"}
_PASTE_BULLETS = 12
# How a refute pass checks the line it says answers an item: as the quote check does, spacing and line breaks aside,
# through to what such a line does not do.
_ANSWER_SPACING = re.compile(
    r"[Ss]pacing and line breaks aside, an? (?:answering )?line that is not[^.]*?word for word[^.]*?does not drop the"
    r" (?:objection|question|attack)"
    r"|check every answering line the same way as the (?:objections' )?quotes: an answering line that is not in the"
    r" material word for word does not drop the (?:objection|question)"
)
# The skills with one skeptic and at most three attacks, whose refute pass is small enough to need no lean mode.
_NO_LEAN_SKILLS = ("vc-claims-check", "vc-round-sizing")


def _unwrapped(name: str) -> str:
    """The skill's text with its Markdown line breaks taken out, so a wrapped sentence reads as one."""
    text = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


def _inputs(name: str) -> str:
    """The skill's Inputs section, its line breaks taken out."""
    text = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    section = text.split("\n## Inputs\n", 1)[1].split("\n## ", 1)[0]
    return " ".join(line.strip() for line in section.splitlines())


def test_the_skills_that_send_a_safe_raises_runway_to_the_runway_plan_are_the_ones_listed() -> None:
    """A new skill that routes a SAFE or note raise's runway to the tool joins the list, and so gets the sentence."""
    texts = {path.parent.name: _unwrapped(path.parent.name) for path in _SKILLS.glob("*/SKILL.md")}
    routing = {name for name, text in texts.items() if "SAFE or note raise" in text and "`equity_runway_plan`" in text}

    assert routing == set(_SAFE_RUNWAY_SKILLS)


@pytest.mark.parametrize("name", _SAFE_RUNWAY_SKILLS)
def test_a_safe_raises_runway_takes_each_planned_change_as_a_later_phase_and_waits_for_its_start_month(
    name: str,
) -> None:
    text = _unwrapped(name)

    assert _PLAN_PHASES in text
    # A planned change waits for whichever of its three inputs is missing, each under its own label, so a rise with a
    # month and no amount, or with both and no word on its revenue, is held like one with an amount and no month, never
    # sent with a spend or a revenue the founder did not give (the tool reads a phase with no revenue as none).
    assert _WAITING_FOR_MONTH in text and _WAITING_FOR_SPEND in text and _WAITING_FOR_REVENUE in text
    # Sending only the spend planned after the raise, from month 1, gives a shorter runway than the founder's plan; the
    # partner-meeting skill used to do that.
    assert "on a `plan` case of the spend planned after the raise" not in text
    assert "today's spend, if it differs, takes its own no-raise call" not in text


@pytest.mark.parametrize("name", _FOUNDER_TEXT_SKILLS)
def test_founder_facing_text_never_works_out_how_two_founder_figures_compare(name: str) -> None:
    assert _NO_COMPARISON in _unwrapped(name)


def test_the_partner_meeting_skill_keeps_its_own_ban_on_combining_two_founder_figures() -> None:
    assert _PARTNER_MEETING_BAN in _unwrapped("vc-partner-meeting")


def test_the_skills_whose_refute_pass_runs_one_subagent_per_objection_or_question_are_the_ones_listed() -> None:
    """A new skill whose lenses feed a refute pass of one subagent per item joins the list, and so gets lean mode."""
    found = {}
    for path in _SKILLS.glob("*/SKILL.md"):
        text = _unwrapped(path.parent.name)
        for noun in ("objection", "question"):
            if f"one subagent per {noun}" in text:
                found[path.parent.name] = noun

    assert found == _LEAN_REFUTE_SKILLS


@pytest.mark.parametrize("name", sorted(_LEAN_REFUTE_SKILLS))
def test_a_refute_pass_of_more_than_eight_may_run_one_subagent_per_lens_and_says_so(name: str) -> None:
    noun = _LEAN_REFUTE_SKILLS[name]
    text = _unwrapped(name)
    lean = _LEAN_REFUTE.format(noun=noun)

    assert lean in text
    # One subagent per item stays the rule; lean mode is its one named exception, for the agent that runs the pass,
    # so it comes before the brief the refute subagents are given.
    assert f"launch one subagent per {noun} in a single message" in text
    assert f"never put two {noun}s in one subagent" in text
    raw = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    before_brief = raw.split("\nThe refute brief:\n", 1)[0]
    assert lean in " ".join(line.strip() for line in before_brief.splitlines())
    # The per-lens subagent is handed the rule that keeps each item on its own, and an item left without a verdict of
    # its own is not dropped.
    assert "as if it were the only one you were given" in lean and "stays Kept" in lean


@pytest.mark.parametrize("name", sorted(_LEAN_REFUTE_SKILLS))
def test_the_answer_says_when_the_refute_pass_ran_per_lens(name: str) -> None:
    """The disclosure sits in the section the answer is composed from, not only in Stage B."""
    raw = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    answering = raw.split("\n## Answering\n", 1)[1].split("\n## ", 1)[0]

    assert _LEAN_ANSWER.format(noun=_LEAN_REFUTE_SKILLS[name]) in " ".join(
        line.strip() for line in answering.splitlines()
    )


@pytest.mark.parametrize("name", sorted(_LEAN_REFUTE_SKILLS))
def test_the_lean_paragraph_stands_alone_and_is_wrapped_like_the_rest(name: str) -> None:
    """A line cap is a stand-in for size, so it is never met by joining a new paragraph onto an old line."""
    raw = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    # The paragraph as written, its first line whole: the marker and the rest of that line are measured together.
    paragraph = _LEAN_PARAGRAPH.lstrip("\n") + raw.split(_LEAN_PARAGRAPH, 1)[1].split("\n\n", 1)[0]

    assert _LEAN_PARAGRAPH in raw
    assert all(len(line) <= _LINE_WIDTH for line in paragraph.splitlines()), name


@pytest.mark.parametrize("name", _NO_LEAN_SKILLS)
def test_a_skill_with_one_skeptic_and_at_most_three_attacks_has_no_lean_mode(name: str) -> None:
    text = _unwrapped(name)

    assert "Return at most three attacks" in text and "never put two attacks in one subagent" in text
    assert "Lean mode" not in text and "one subagent per lens" not in text


@pytest.mark.parametrize("name", [*sorted(_LEAN_REFUTE_SKILLS), "vc-claims-check"])
def test_a_refute_pass_checks_its_answering_line_as_the_quote_check_does(name: str) -> None:
    """A line that wraps in the founder's file, quoted on one line, is still word for word."""
    assert _ANSWER_SPACING.search(_unwrapped(name)), name


def test_the_skills_that_read_a_file_the_founder_gives_are_every_skill_with_inputs() -> None:
    with_inputs = {path.parent.name for path in _SKILLS.glob("*/SKILL.md") if "\n## Inputs\n" in path.read_text()}

    assert with_inputs == set(_READ_THE_FILE_SKILLS)


@pytest.mark.parametrize("name", _READ_THE_FILE_SKILLS)
def test_a_file_the_founder_gives_is_read_never_asked_for_as_a_paste(name: str) -> None:
    inputs = _inputs(name)

    assert _READ_THE_FILE in inputs
    # It comes with the first instruction, before the list of what to ask for.
    assert inputs.index(_READ_THE_FILE) < inputs.index("1. ")
    text = _unwrapped(name)
    assert "from text the founder pastes" not in text
    assert "the pasted text plus every answer" not in text


def test_a_place_the_agent_could_not_read_is_listed_and_asked_for() -> None:
    """A slide that is only a picture is still in the file; it is asked for, never filled in from what surrounds it."""
    assert "is listed as not read and asked for, never filled in" in _READ_THE_FILE
    assert "in the file's own words" in _READ_THE_FILE


@pytest.mark.parametrize("name", _READ_THE_FILE_SKILLS)
def test_no_line_of_the_inputs_or_when_to_use_it_section_is_wider_than_the_rest(name: str) -> None:
    """The shared sentences are wrapped at the repository's width, so a line cap is never met by joining lines."""
    raw = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    for heading in ("\n## Inputs\n", "\n## When to use it\n"):
        section = raw.split(heading, 1)[1].split("\n## ", 1)[0]
        wide = [line for line in section.splitlines() if len(line) > _LINE_WIDTH]
        assert not wide, (name, heading.strip(), wide[0][:60] if wide else "")


def test_the_deal_math_skill_reads_a_file_by_the_same_rule() -> None:
    """Its figures go straight to the calculator, so a figure off a chart or a half-read page must never reach it."""
    text = _unwrapped("vc-deal-math")

    assert _READ_THE_FILE in text
    assert "It does not read a deck file" not in text


def _paragraphs(text: str) -> list[str]:
    return [" ".join(line.strip() for line in block.splitlines()) for block in text.split("\n\n")]


def _pass_sentence(text: str) -> str:
    """An eval's pass sentence, from "A run passes when" to the full stop that ends it, its line breaks taken out."""
    first = " ".join(_paragraphs(text.split("\n## ", 1)[0])[1].split())
    match = re.search(r"A run passes when .*?\.(?= [A-Z]|$)", first)
    assert match, first[:80]
    return match.group(0)


def _changed_since_run(path: Path) -> bool:
    """Whether the eval's pass sentence differs from the one pinned for its run."""
    digest = hashlib.sha256(_pass_sentence(path.read_text(encoding="utf-8")).encode("utf-8")).hexdigest()[:12]
    return digest != _PASS_SENTENCE_AT_RUN.get(path.stem)


@pytest.mark.parametrize("path", _RECORDED_EVALS, ids=[path.stem for path in _RECORDED_EVALS])
def test_a_recorded_eval_states_the_verdict_rule_and_opens_its_recording_with_a_verdict_under_it(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    first = _paragraphs(text.split("\n## ", 1)[0])[1]
    verdict = _paragraphs(text.split(_RECORDED, 1)[1].strip("\n"))[1]

    assert _VERDICT_RULE in first
    # An outside grader's word is not a verdict under the rule, and no other point of an eval can make a run Partial.
    assert "graded Partial" not in first and "a run that misses one of them is graded Partial" not in text
    assert re.match(r"\*\*(Pass|Partial|Fail)\b", verdict), verdict[:60]
    if "met every clause" in verdict:
        assert verdict.startswith("**Pass"), verdict[:60]


def test_every_recorded_eval_has_its_pass_sentence_at_the_run_pinned() -> None:
    """A new recording adds its eval's pass sentence as it stood at the run; an eval that loses its recording comes
    off the list."""
    assert {path.stem for path in _RECORDED_EVALS} == set(_PASS_SENTENCE_AT_RUN)


@pytest.mark.parametrize("path", _RECORDED_EVALS, ids=[path.stem for path in _RECORDED_EVALS])
def test_a_verdict_counts_the_pass_sentence_the_eval_had_at_the_run(path: Path) -> None:
    """Under the README's rule a recorded verdict counts the clauses the pass sentence had at the run. An eval whose
    sentence changed since says so in its first paragraph and in its recording's header, opens its verdict with that
    rule, and says how the run reads against today's sentence; an eval whose sentence is unchanged says none of it."""
    text = path.read_text(encoding="utf-8")
    first = _paragraphs(text.split("\n## ", 1)[0])[1]
    header, verdict = _paragraphs(text.split(_RECORDED, 1)[1].strip("\n"))[:2]

    if _changed_since_run(path):
        assert _THEN in first and _TODAY in first
        assert ", when this eval" in header
        assert _THEN_VERDICT.match(verdict), verdict[:80]
        assert _TODAY in verdict
    else:
        assert _THEN not in first and ", when this eval" not in header
        assert "pass sentence this eval had then" not in verdict
    # A verdict on today's sentence with the count on the sentence at the run set beside it is the old, split rule.
    assert "this eval had when it ran" not in " ".join(text.split())


def test_every_regraded_eval_carries_the_verdict_its_recorded_answer_gives() -> None:
    graded = {path.stem: path.read_text(encoding="utf-8") for path in _RECORDED_EVALS if path.stem in _REGRADED}

    assert set(graded) == set(_REGRADED)
    for stem, opening in _REGRADED.items():
        verdict = _paragraphs(graded[stem].split(_RECORDED, 1)[1].strip("\n"))[1]
        assert verdict.startswith(opening), stem
    # Every recording whose pass sentence changed after its run was re-graded on the sentence it had then.
    changed = {path.stem for path in _RECORDED_EVALS if _changed_since_run(path)}
    assert changed == set(_REGRADED) - {_UNCHANGED_REGRADE}


def test_every_hand_off_to_the_memo_skill_says_a_champion_is_likely_to_write_it() -> None:
    """No skill claims to know how a firm works, so the memo is the one a champion is likely to write."""
    handoffs = [
        line.strip()
        for path in sorted(_SKILLS.glob("*/SKILL.md"))
        for line in path.read_text(encoding="utf-8").splitlines()
        if "the vc-investor-memo skill (preview)" in line
    ]

    assert len(handoffs) >= 4
    assert set(handoffs) == {f"- {_MEMO_HANDOFF}"}
    for path in _SKILLS.glob("*/SKILL.md"):
        assert "champion writes for the partnership" not in path.read_text(encoding="utf-8"), path.parent.name


def test_every_when_to_use_bullet_that_names_pasted_material_says_it_may_come_as_a_file() -> None:
    """A trigger written as paste-only teaches the agent to ask for a paste of a file it could read."""
    pasted = []
    for path in sorted(_SKILLS.glob("*/SKILL.md")):
        text = path.read_text(encoding="utf-8")
        if "\n## When to use it\n" not in text:
            continue
        when = text.split("\n## When to use it\n", 1)[1].split("\n## ", 1)[0]
        for bullet in re.split(r"\n(?=- )", when):
            line = " ".join(part.strip() for part in bullet.splitlines())
            if line.startswith(("- A pasted", "- Pasted material")):
                pasted.append((path.parent.name, line))

    assert len(pasted) == _PASTE_BULLETS
    for name, line in pasted:
        assert _FILE_TOO_OWN_WORDING.get(name, _FILE_TOO) in line, name
