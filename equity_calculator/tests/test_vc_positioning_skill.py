"""The vc-positioning skill keeps its shape: its frontmatter, its tool names, its adversarial review and its evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The adversarial review must keep both stages: independent attack lenses named by what
they test (never by a person or firm), each objection quoting the founder's own line; a refute pass that may use only
the founder's material and records why each dropped objection fell; and the ranked survivors, with quotes, in the
answer. The contrarian row and its lens ask for a belief most investors would reject today, test whether it is one,
and never write one for the founder. Each eval in evals/vc-positioning/ has a prompt, an expected tool call and an
expected answer; the one eval with an ``equity_deal_check`` call carries a valid call and an excerpt that is lines of
the report that call prints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import _INPUT_MODELS
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-positioning" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-positioning").glob("*.md"))
_EVAL_COUNT = 5
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_RECORDED = "## Recorded answer"
# A recorded run's verdict line, in the shape the repository's recorded evals use.
_VERDICT_LINE = re.compile(r"\*\*(?:Pass|Partial|Fail)\b[^*]*\*\*")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_HANDOFF_SKILLS = (
    "vc-deal-math",
    "equity-calculator",
    "vc-claims-check",
    "vc-deck-review",
    "vc-partner-meeting",
    "vc-taste-check",
    "vc-round-sizing",
    "vc-term-sheet-review",
    "vc-diligence-questions",
    "vc-current-investor-update",
    "vc-metrics-readiness",
    "vc-investor-memo",
    "vc-market-sizing",
    "vc-prospective-investor-update",
)
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "tighten my pitch",
    "stress-test my pitch",
    "how should we position this round",
    "what should I not say to VCs",
    "prep me before we go out to raise",
    "what is our contrarian insight",
    "what do we believe that others don't",
)
_PHRASES = ("no competitors", "we only need 1% of the market", "our projections are conservative")
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = (
    "sequoia",
    "a16z",
    "andreessen",
    "y combinator",
    "yc",
    "graham",
    "dixon",
    "thiel",
    "stebbings",
    "20vc",
)
_MIN_LENSES = 5
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|\s*Dimensions\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_SURVIVOR_COLUMNS = re.compile(
    r"Rank, Tier, Lens, The founder's line \(quoted\), Why a partner reads it that way,\s+Rewrite"
)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_CONTRARIAN_LENS = "Is it really contrarian?"
_CONTRARIAN_PROMPTS = (
    '"What do you believe about this market that most investors would reject?" and "What did you see first-hand that'
    ' others have not?"'
)
_CONTRARIAN_ASK = "`[the belief about this market that most investors would reject today, in one sentence]`"
_CONSENSUS_CLAIM = "Insurance claims work is moving from paper to software."


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


def _lens_names() -> list[str]:
    table = _section("### Stage A: attack")
    head = _LENS_HEAD.search(table)
    assert head is not None
    rows = table[head.end() :].strip().split("\n\n", 1)[0].splitlines()[1:]
    return [match.group(1) for row in rows if (match := _ROW.match(row))]


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-positioning"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in _PHRASES:
        assert phrase in description, phrase
    assert "founder" in description and "adversarial review" in description


def test_the_first_when_to_use_bullet_holds_the_contrarian_triggers() -> None:
    """The contrarian triggers were in the description only; the first "When to use it" bullet lists them too."""
    when = _TEXT.split("\n## When to use it\n", 1)[1].split("\n## ", 1)[0]
    first = " ".join(line.strip() for line in when.strip().split("\n- ", 1)[0].splitlines())

    assert '"What is our contrarian insight?" "What do we believe that others don\'t?"' in first


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_round", "equity_dilution"} <= named
    assert named <= served, named - served


def test_every_skill_it_hands_off_to_exists() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = _lens_names()

    assert len(lenses) >= _MIN_LENSES
    for lens in lenses:
        assert not any(re.search(rf"\b{name}\b", lens.lower()) for name in _PEOPLE_AND_FIRMS), lens
    assert "quoted word for word" in attack
    assert "subagent" in attack and "only the founder's material and its lens brief" in attack
    assert "one after another" in attack
    assert "do no arithmetic" in attack


def test_every_dimension_row_names_a_lens_that_exists() -> None:
    lenses = set(_lens_names())
    table = _section("## The dimensions")
    rows = [row for row in table.splitlines() if re.match(r"^\|\s*\d+\s*\|", row)]

    assert rows
    for row in rows:
        assert row.rstrip(" |").rsplit("|", 1)[1].strip() in lenses, row


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))

    assert "using only the founder's material" in refute
    assert "one subagent per objection" in refute
    for verdict in ("Dropped, answered:", "Dropped, not grounded:", "Kept:"):
        assert verdict in refute, verdict
    assert "Quote the founder's line that answers it" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "an answering line that is not in the material word for word does not drop the objection" in refute
    assert "The refute brief:" in refute and "do no arithmetic" in refute and "Bring in no outside fact" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_survivors_are_ranked_with_quotes_and_feed_the_rest_of_the_answer() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    answering = _unwrapped(_section("## Answering"))

    assert "the founder's line, quoted word for word" in rank
    assert "no percentages and no score" in rank
    for destination in ("biggest issues", "say-and-avoid list", "tightened narrative", "prep script"):
        assert destination in rank, destination
    assert "**Adversarial review:**" in answering and "**Dropped,**" in answering
    assert _SURVIVOR_COLUMNS.search(answering)


def test_the_steps_run_the_adversarial_review() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "**Run the adversarial review**" in steps
    assert "every surviving objection quotes a line that is in the material word for word" in steps


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
        # and says what changed since.
        assert text.index(f"\n{_RECORDED}\n") > positions[-1], path.name
        assert '"Recorded answer" is an excerpt of a recorded run' in _unwrapped(text.split("\n## ", 1)[0]), path.name
        recorded = _section(_RECORDED, text)
        assert _VERDICT_LINE.match(recorded.strip("\n").split("\n\n")[1]), path.name
        assert "Since this run" in _unwrapped(recorded), path.name
        assert _fences("json", recorded) == [] and _fences("text", recorded) == [], path.name


def test_one_eval_has_the_phrases_that_cost_the_meeting() -> None:
    prompts = {path.name: _unwrapped(_section("## Prompt", path.read_text(encoding="utf-8"))) for path in _EVALS}
    (name,) = (name for name, prompt in prompts.items() if all(phrase in prompt for phrase in _PHRASES[:2]))
    answer = _section("## Expected answer", (_ROOT / "evals" / "vc-positioning" / name).read_text(encoding="utf-8"))

    assert "survive" in answer and "We have no competitors." in answer
    assert "names the vc-market-sizing skill, which checks that size" in _unwrapped(answer)


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    dropping = [path for path in _EVALS if "Dropped, answered" in _unwrapped(path.read_text(encoding="utf-8"))]
    assert dropping
    for path in dropping:
        text = path.read_text(encoding="utf-8")
        prompt = _unwrapped(_section("## Prompt", text))
        answer = _unwrapped(_section("## Expected answer", text))
        objection, dropped = answer.split("Dropped, answered", 1)
        # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
        # founder's material, not the line the objection was about.
        answering_line = _DOUBLE_QUOTED.findall(dropped)[0]
        assert answering_line in prompt
        assert answering_line not in _DOUBLE_QUOTED.findall(objection)


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS
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


_SAFE_UNCHECKED = "not checked: no tool computes this for a SAFE or note raise"
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")
# A share as the MCP tool returns it: a fraction with six places and no percent sign.
_JSON_FRACTION = re.compile(r"(?<![\d.])-?\d+\.\d{6}(?![\d%])")


def test_the_refute_brief_is_handed_over_whole_and_judges_rather_than_argues() -> None:
    """The pass that drops objections gets its verdicts and rules, the phrase list, and the lens ban's own limits."""
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))

    assert "| Phrase or pattern" in _section("## Phrases that cost credibility")
    assert "the Phrase or pattern column of the phrase table below" in handoff
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "Bring in no outside fact about the company, its market or its competitors",
        "How a partner is likely to read a line is not an outside fact",
        "never answers an objection",
        "When you cannot decide, return Kept",
        "a line of the material other than the objected line supplies the specific thing the objection says is missing",
        "rests on an outside fact about the company, its market or its competitors",
        "invents nothing on the founder's behalf",
        "neither does one that is the objected line itself or that matches a phrase in the phrase table",
    ):
        assert rule in brief, rule
    assert "argue the founder's side" not in _unwrapped(stage)


def test_without_a_subagent_tool_the_lenses_run_before_step_1_and_the_answer_says_so() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    note = "Without a subagent tool, run Stage A of the adversarial review first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    assert "run Stage A first, before step 1" in attack and "less independent than subagents" in attack
    assert "less independent than separate subagents" in _unwrapped(_section("## Answering"))


def test_a_safe_raise_sends_its_runway_and_use_of_funds_to_the_runway_plan_tool() -> None:
    """The runway tool takes a SAFE raise as cash; with no cash or burn given, the answer asks for them first."""
    steps = _unwrapped(_section("## Steps"))
    prompts = {path: _unwrapped(_section("## Prompt", path.read_text(encoding="utf-8"))) for path in _EVALS}
    (path,) = (path for path, prompt in prompts.items() if "on a SAFE" in prompt and "months of runway" in prompt)
    text = path.read_text(encoding="utf-8")
    answer = _unwrapped(_section("## Expected answer", text))

    assert "Runway with no raise, or on a SAFE or note raise, and the use-of-funds lines on such a raise go to" in steps
    assert "`equity_runway_plan`, as vc-deal-math step 2 says" in steps
    assert "With no cash or burn given, ask for them by name" in steps and "make no call until they are given" in steps
    assert "never work it out by hand" in steps
    assert "`equity_runway_plan`'s rows" in _unwrapped(_section("## Answering"))
    assert _SAFE_UNCHECKED not in _TEXT and "no tool checks the runway claim" not in _TEXT
    # The SAFE eval's prompt gives no cash or burn: the true reason it is not checked yet, and the ask, not a tool gap.
    assert "`equity_runway_plan`" in answer and "asks for the cash on hand, monthly spend and revenue" in answer
    assert _SAFE_UNCHECKED not in answer and _NO_CALL in text


def test_the_attack_brief_raises_every_objection_and_the_refute_pass_judges_one_each() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    refute = _unwrapped(_section("### Stage B: refute"))

    # A lens that sees the answering line must still raise the objection, or the refute pass has nothing to drop.
    assert "Do not judge whether another line of the material answers an objection: raise it anyway" in attack
    assert "however short the material; the refute pass decides" in attack
    assert "rather than a weak objection" not in attack
    assert "launch one subagent per objection in a single message" in refute
    assert "never put two objections in one subagent" in refute


def test_computed_mismatches_head_the_survivors_with_no_tier_and_an_understated_runway_is_minor_at_most() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    rank = _unwrapped(_section("### Rank what survives"))
    (company_f,) = (path for path in _EVALS if path.name.startswith("company-f-"))
    answer = _unwrapped(_section("## Expected answer", company_f.read_text(encoding="utf-8")))

    assert "heads the survivors, ahead of the tiers, under **figures that do not match (computed)**" in attack
    assert "It carries no tier" in attack and "added to the survivors as ends the meeting" not in attack
    assert "a runway claim below the computed runway understates it" in attack
    assert "it goes in the minor tier at most" in attack
    assert "head the list, ahead of the tiers, with no tier" in rank
    assert "head the surviving objections, ahead of the tiers" in answer and "with no tier" in answer
    assert "ranked as ends the meeting" not in answer


def test_a_mismatch_under_one_reading_of_an_unlabelled_valuation_is_a_fix_to_label_it() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))

    assert "A check that is a mismatch under one reading only is not a calculator mismatch" in steps
    assert "it becomes one fix, to label the valuation pre- or post-money" in steps
    assert "Only a check that is a mismatch under every reading is the calculator's mismatch" in steps
    assert "A fix to label the valuation (a mismatch under one reading only) is not a calculator mismatch" in attack


def test_step_4_asks_which_way_the_founders_fully_diluted_total_counts_safes_and_notes() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "SAFEs and notes excluded" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "`[fully diluted shares before the round, SAFEs and notes left out]`" in steps
    assert "never subtract the SAFE or note shares yourself" in steps


def test_every_flag_code_has_its_meaning_in_the_skill() -> None:
    """The MCP tool returns flag codes only, so the skill carries each flag's meaning itself."""
    table = _section("## Calculator flags")
    deal, runway = table.split("\n| `equity_runway_plan` flag", 1)
    prose = _unwrapped(table.split("\n|", 1)[0])

    assert re.findall(r"^\| `([a-z_]+)` +\|", deal, re.MULTILINE) == list(get_args(DealFlag))
    # Every runway-plan code has its row, as a call with a milestone brings codes past the three a plain call returns.
    assert re.findall(r"^\| `([a-z_]+)` +\|", runway, re.MULTILINE) == list(get_args(RunwayPlanFlag))
    plain = "returns only `runway_below_band`, `cash_never_runs_out` and `consistent_beyond_rounding`"
    assert plain in prose
    assert 'with its meaning from "Calculator flags" below' in _unwrapped(_section("## Steps"))


def test_metrics_and_market_sizes_go_to_their_skills_and_growth_stays_unchecked() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "ARR, retention, churn, CAC payback and burn multiple are checked by the vc-metrics-readiness skill" in steps
    assert "a market size by the vc-market-sizing skill" in steps
    assert "LTV, LTV/CAC, the Rule of 40 and the magic number go to the vc-metrics-readiness skill too" in steps
    assert (
        'Growth rates: no tool computes them; quote them as stated with "not checked: no tool computes this"' in steps
    )
    assert "no tool in this repository computes them" not in steps


def test_a_fraction_from_the_tool_is_shown_as_a_percent_by_notation_only() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps


def test_the_letters_of_intent_row_cites_only_the_a16z_items_that_say_so() -> None:
    table = _section("## Phrases that cost credibility")
    (row,) = (row for row in table.splitlines() if row.startswith("| Letters of intent"))

    assert row.rstrip(" |").rsplit("|", 1)[1].strip() == 'a16z "16 Startup Metrics" (1, 6)'
    assert "pipeline" not in row.lower()


def test_the_prep_session_credits_no_unread_source_and_is_marked_unverified() -> None:
    """No one read the post the prep session was first credited to, so the skill credits no person or post for it."""
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])
    sources = _unwrapped(_section("## Sources"))
    limits = _unwrapped(_section("## Limits"))

    for unread in ("Stebbings", "20VC", "LinkedIn", "did not fetch", "the post that inspired it"):
        assert unread not in _TEXT, unread
    assert "The prep session has no public source read and is marked unverified." in intro
    assert (
        "The prep session has no public source read and is marked unverified; no person or post is credited for it."
        in sources
    )
    assert "plus the prep session (unverified: no public source read)" in limits


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


def _dimension_row(name: str) -> list[str]:
    """The cells of the dimension table's row called ``name``."""
    for row in _section("## The dimensions").splitlines():
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if re.match(r"^\|\s*\d+\s*\|", row) and cells[1] == name:
            return cells
    raise AssertionError(name)


def test_the_contrarian_row_asks_for_a_belief_most_reject_with_who_disagrees_and_the_evidence() -> None:
    number, _, clear, source, lens = _dimension_row("Contrarian insight")
    dimensions = _unwrapped(_section("## The dimensions"))
    sources = _unwrapped(_section("## Sources"))

    assert number == "12" and lens == _CONTRARIAN_LENS
    for part in ("One-sentence belief most people reject today", "who disagrees and why", "the evidence"):
        assert part in clear, part
    # A published question is cited by its source, never played as a person; the evidence test is the skill's own.
    assert 'Thiel, "Zero to One"' in source and 'YC "How to Apply"' in source
    assert "https://fortune.com/2014/09/04/peter-thiels-the-challenge-of-the-future" in sources
    assert "Row 12 is not row 5" in dimensions
    assert "who disagrees, the evidence test and the business resting on it are this skill's own framing." in dimensions
    assert "its interview question asking for an important truth few others accept, read in the excerpt" in sources


def test_the_contrarian_lens_tests_consensus_evidence_and_dependence_by_its_brief() -> None:
    table = _section("### Stage A: attack")
    attack = _unwrapped(table)
    (row,) = (row for row in table.splitlines() if row.startswith(f"| {_CONTRARIAN_LENS} "))

    assert row.rstrip(" |").rsplit("|", 1)[1].strip() == "12"
    assert "its brief carries this paragraph as its test" in attack
    assert "(for Is it really contrarian?, the whole paragraph above)" in attack
    for question in (
        "would reject today, and does the founder say who disagrees and why they are wrong?",
        "Or is it a consensus view reworded",
        "or a side already taken in a well-known argument",
        "That is a partner's likely reading of the founder's line, not an outside fact",
        "Does the material show evidence the belief is right",
        "Contrarian with no evidence is only a guess",
        "And does the business depend on it?",
    ):
        assert question in attack, question
    # The refute pass sees only its brief, so the brief says a consensus objection rests on a reading, not a fact.
    refute = _unwrapped(_section("### Stage B: refute"))
    assert "or that a belief stated as contrarian is one most investors already hold, rests on that reading" in refute
    assert "answered only by a line that names who rejects the belief and why" in refute
    # A live run's judge dropped the objection quoting slide 4, which shows others acting on the belief, as not grounded
    # because slide 4 never names the belief: such a line supports the objection, in the brief and in the verdict.
    assert (
        "A line showing others already acting on that belief supports the objection even when the line never names the"
        " belief or calls it contrarian: never drop it as not grounded then."
    ) in refute
    assert (
        "A line showing others acting on a belief stated as contrarian says what an objection that most investors"
        " already hold that belief claims."
    ) in refute


def test_a_founder_with_no_contrarian_belief_is_asked_once_and_never_given_one() -> None:
    dimensions = _unwrapped(_section("## The dimensions"))
    attack = _unwrapped(_section("### Stage A: attack"))
    answering = _unwrapped(_section("## Answering"))

    assert "Row 12 is a question, not a required box: many good companies have no contrarian story." in dimensions
    assert "mark the row Not stated, never Missing, keep it out of the survivors and the biggest issues" in dimensions
    assert (
        f"ask for it once, in the message that asks for the missing inputs, with two prompts: {_CONTRARIAN_PROMPTS}"
        in dimensions
    )
    fallen = "the lens's objection that most investors already hold it survives, ask the same two prompts once"
    assert fallen in dimensions
    assert "a surviving objection about its evidence, or about whether the business depends on it, asks for that" in (
        dimensions
    )
    assert "Never write a contrarian belief for the founder, in a rewrite, the narrative or a refute pass" in dimensions
    assert "When no line of the material puts a belief forward as contrarian, or as one others reject" in attack
    assert "the lens raises no objection and returns one gap" in attack
    assert "it never writes a belief for the founder" in attack
    assert "(Not stated for row 12)" in answering


def test_the_answer_has_a_contrarian_block_with_at_most_two_rewrites_from_the_founders_material() -> None:
    answering = _unwrapped(_section("## Answering"))

    assert "**Contrarian insight:** the belief as the founder stated it, quoted word for word" in answering
    assert "the surviving objections of the Is it really contrarian? lens, or that none survived" in answering
    assert "up to two rewrites of the one-sentence belief, each using only the founder's material" in answering
    assert "A rewrite only rewords, shortens or joins lines the founder wrote" in answering
    assert "carries its own bracketed ask and no prompt" in answering
    assert (
        "When the belief is not stated, or the objection that most investors already hold it survives: up to two"
        " includes none, so unless a line of the material states a sharper belief in the founder's own words, give the"
        f" bracketed ask {_CONTRARIAN_ASK}" in answering
    )
    assert "and say that not every good company needs a contrarian story" in answering
    assert "never a belief written for the founder" in answering
    # The prompts are asked once: one item in the open asks, which the block points to rather than repeats.
    assert "the two prompts from row 12 go to the open asks once, as one item with that bracketed ask" in answering


def test_one_eval_catches_a_contrarian_claim_most_investors_already_hold() -> None:
    (path,) = (path for path in _EVALS if path.name.startswith("company-bk-"))
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))
    answer = _unwrapped(_section("## Expected answer", text))
    others_act = (
        "Every large insurer now runs claims on its own software, and four funded startups sell claims software to"
        " insurers."
    )

    assert _NO_CALL in text
    # The objection quotes the founder's line, and the founder's own slide shows the belief is shared.
    assert _CONSENSUS_CLAIM in prompt and f'"{_CONSENSUS_CLAIM}"' in answer
    assert others_act in prompt and f'"{others_act}"' in answer
    assert "That objection survives the refute pass." in answer
    assert "does not drop it as resting on an outside fact" in answer
    assert "The answer writes no contrarian belief the founder did not state." in answer
    assert _CONTRARIAN_ASK in answer
    assert "It asks once, in one message, with the two prompts" in answer
    assert "not every good company needs a contrarian story" in answer
    # The live run is recorded: it met the pass sentence, and the slide-4 objection it dropped led to a fix.
    recorded = _unwrapped(_section(_RECORDED, text)).strip()
    assert recorded.startswith("Recorded with Claude Code 2.1.331 on 2026-11-24")
    assert "**Pass, with shortfalls against the expected answer.** It met every clause of the pass sentence" in recorded
    assert "the one quoting slide 4" in recorded and "Since this run the refute brief says" in recorded
