"""Rules the review skills share word for word, so one founder input gets the same treatment whichever skill runs.

Two sentences are copied into several skills and must stay identical there:

- Which monthly spend goes into ``equity_runway_plan`` for a runway claim on a SAFE or note raise. When the skills
  disagreed, the same founder input gave 11.67 months in one skill and 17.50 in another (a runway plan with today's
  spend of $120,000 against one with $80,000 and the later phase left out). Every skill that sends a SAFE or note
  raise's runway to that tool carries the sentence.
- No working out how two of the founder's figures relate in founder-facing text: a live positioning run wrote that
  users "more than doubled", which neither the founder nor the calculator said. Every skill that writes rewrites,
  lines or update text for the founder carries the sentence, except the partner-meeting skill, whose own ban says
  the same in other words and is checked here too.

Every eval that records a live run states the README's verdict rule in its first paragraph and opens its recording
with a verdict under it: Pass when every clause of the pass sentence is met, Partial when exactly one is missed or met
only in part, Fail when two or more are missed. Four recordings once carried an outside grader's word instead, one of
them Partial beside "met every clause"; they are re-graded from their recorded answers.
"""

from __future__ import annotations

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
_MEMO_HANDOFF = (
    "The memo a champion partner is likely to write for the partnership: the vc-investor-memo skill (preview)."
)
# The four recordings re-graded under the rule, each from its own recorded answer.
_REGRADED = {
    "company-ar-a-2x-participating-seed": "**Pass, with shortfalls against the expected answer",
    "company-ac-a-cap-table-the-deck-misstates": "**Fail: two clauses missed.**",
    "company-bm-a-memo-that-hides-its-biggest-risk": (
        "**Pass, against the pass sentence this eval had then; it missed the four clauses added since.**"
    ),
    "company-aw-bottom-up-against-the-deck": (
        "**Pass, against the pass sentence this eval had then; it missed the one clause added since.**"
    ),
}
_PLAN_PHASES = (
    "On a SAFE or note raise, the `plan` case's phases are the founder's own figures: today's monthly spend and revenue"
    " as the first phase, from month 1, and each change the founder plans (more spend after the raise, say) as a later"
    " phase from the month the founder names, each asked for by name when missing (`[planned monthly spend and"
    " revenue, from which month]`), never assumed."
)
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
    "vc-positioning",
    "vc-deck-review",
    "vc-claims-check",
    "vc-round-sizing",
    "vc-prospective-investor-update",
    "vc-current-investor-update",
    "vc-investor-memo",
)
_PARTNER_MEETING_BAN = 'never a difference, sum or ratio of two figures the founder gave ("from $80k to $120k a month"'


def _unwrapped(name: str) -> str:
    """The skill's text with its Markdown line breaks taken out, so a wrapped sentence reads as one."""
    text = (_SKILLS / name / "SKILL.md").read_text(encoding="utf-8")
    return " ".join(line.lstrip("> ").strip() for line in text.splitlines())


def test_the_skills_that_send_a_safe_raises_runway_to_the_runway_plan_are_the_ones_listed() -> None:
    """A new skill that routes a SAFE or note raise's runway to the tool joins the list, and so gets the sentence."""
    texts = {path.parent.name: _unwrapped(path.parent.name) for path in _SKILLS.glob("*/SKILL.md")}
    routing = {name for name, text in texts.items() if "SAFE or note raise" in text and "`equity_runway_plan`" in text}

    assert routing == set(_SAFE_RUNWAY_SKILLS)


@pytest.mark.parametrize("name", _SAFE_RUNWAY_SKILLS)
def test_a_safe_raises_runway_takes_todays_spend_first_and_each_planned_change_as_a_later_phase(name: str) -> None:
    text = _unwrapped(name)

    assert _PLAN_PHASES in text
    # The partner-meeting skill used to send only the spend planned after the raise, which gives a longer runway when
    # spend rises later and the rise is left out.
    assert "on a `plan` case of the spend planned after the raise" not in text
    assert "today's spend, if it differs, takes its own no-raise call" not in text


@pytest.mark.parametrize("name", _FOUNDER_TEXT_SKILLS)
def test_founder_facing_text_never_works_out_how_two_founder_figures_compare(name: str) -> None:
    assert _NO_COMPARISON in _unwrapped(name)


def test_the_partner_meeting_skill_keeps_its_own_ban_on_combining_two_founder_figures() -> None:
    assert _PARTNER_MEETING_BAN in _unwrapped("vc-partner-meeting")


def _paragraphs(text: str) -> list[str]:
    return [" ".join(line.strip() for line in block.splitlines()) for block in text.split("\n\n")]


@pytest.mark.parametrize("path", _RECORDED_EVALS, ids=[path.stem for path in _RECORDED_EVALS])
def test_a_recorded_eval_states_the_verdict_rule_and_opens_its_recording_with_a_verdict_under_it(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    first = _paragraphs(text.split("\n## ", 1)[0])[1]
    header, verdict = _paragraphs(text.split(_RECORDED, 1)[1].strip("\n"))[:2]

    assert _VERDICT_RULE in first
    # An outside grader's word is not a verdict under the rule, and no other point of an eval can make a run Partial.
    assert "graded Partial" not in first and "a run that misses one of them is graded Partial" not in text
    assert re.match(r"\*\*(Pass|Partial|Fail)\b", verdict), verdict[:60]
    if "met every clause" in verdict:
        assert verdict.startswith("**Pass"), verdict[:60]
    # A verdict counted on the pass sentence as it stood at the run says so, and says which clauses came after.
    if _THEN in first:
        assert "pass sentence this eval had then" in verdict or "Fail" in verdict
        assert ", when this eval" in header


def test_the_four_regraded_evals_carry_the_verdict_their_recorded_answers_give() -> None:
    graded = {path.stem: path.read_text(encoding="utf-8") for path in _RECORDED_EVALS if path.stem in _REGRADED}

    assert set(graded) == set(_REGRADED)
    for stem, opening in _REGRADED.items():
        verdict = _paragraphs(graded[stem].split(_RECORDED, 1)[1].strip("\n"))[1]
        assert verdict.startswith(opening), stem


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
