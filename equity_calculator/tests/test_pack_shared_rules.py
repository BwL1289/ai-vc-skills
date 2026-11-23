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
"""

from __future__ import annotations

from pathlib import Path

import pytest

_SKILLS = Path(__file__).resolve().parents[2] / "skills"
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
    routing = {
        path.parent.name
        for path in _SKILLS.glob("*/SKILL.md")
        if "SAFE or note raise" in _unwrapped(path.parent.name) and "`equity_runway_plan`" in _unwrapped(path.parent.name)
    }

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
