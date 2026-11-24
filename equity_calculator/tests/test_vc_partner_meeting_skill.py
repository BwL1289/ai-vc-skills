"""The vc-partner-meeting skill keeps its shape: a moderator's rehearsal, its lenses, review, bank and evals.

The skill is the rehearsal's moderator, never an investor: questions in the third person, no pass or invest verdict
and no score. Every calculator tool it names must be one the MCP server serves, and every skill it hands off to by
name must be a folder in skills/. Its lenses are frameworks named by stage and by a partner's background, never a
person or firm. The adversarial review keeps both stages (lenses that quote the founder's own line, then a refute pass
that may use only the founder's material), the standing prep questions are never refuted, and the debrief builds each
stronger answer only from the founder's material. The question bank in references/ is one table per category with
fixed columns, no figures and no names, competition rows at four fixed levels, and the standing prep questions word
for word. The calculator flags table, the standing prep table, the debrief's full shape and how the live drill runs
live in references/ beside the bank, so the skill stays under its line cap with its lines wrapped like the rest; the
skill links each, keeps the rules that bind it, and the checks on each read it there. The skill's first live drill left
five rules, each pinned here: the top questions are answered in the founder's own words before any draft is shown; a
follow-up uses the founder's everyday words; a draft whose figure changed is marked stale and redone; a spoken answer
weaker than the material's own line gets a tiered rewrite; and each short standing answer gets one next step. Each eval
in evals/vc-partner-meeting/ has a prompt, an expected tool call and an expected answer; the one eval with calculator
calls carries valid calls and excerpts that are lines of the reports those calls print.
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
from equity_calculator.schemas.equity import ScenarioInput, ScenarioResult
from equity_calculator.schemas.equity_deal_check import DealFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag, RunwayPlanInput
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_FOLDER = _ROOT / "skills" / "vc-partner-meeting"
_TEXT = (_FOLDER / "SKILL.md").read_text(encoding="utf-8")
_BANK_PATH = _FOLDER / "references" / "question-bank.md"
_BANK = _BANK_PATH.read_text(encoding="utf-8")
_FLAGS_LINK = "[`references/calculator-flags.md`](references/calculator-flags.md)"
_FLAGS = (_FOLDER / "references" / "calculator-flags.md").read_text(encoding="utf-8")
_STANDING_LINK = "[`references/standing-prep.md`](references/standing-prep.md)"
_STANDING_PREP = (_FOLDER / "references" / "standing-prep.md").read_text(encoding="utf-8")
_DEBRIEF_LINK = "[`references/debrief.md`](references/debrief.md)"
_DEBRIEF = (_FOLDER / "references" / "debrief.md").read_text(encoding="utf-8")
_DRILL_LINK = "[`references/drill.md`](references/drill.md)"
_DRILL = (_FOLDER / "references" / "drill.md").read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVAL_DIR = _ROOT / "evals" / "vc-partner-meeting"
_EVALS = sorted(_EVAL_DIR.glob("*.md"))
_EVAL_COUNT = 5
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
_HANDOFF_SKILLS = (
    "vc-deal-math",
    "equity-calculator",
    "vc-positioning",
    "vc-claims-check",
    "vc-metrics-readiness",
    "vc-round-sizing",
    "vc-investor-memo",
    "vc-market-sizing",
)
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
_NOT_COMPUTED = "not checked: no tool computes this"
_THIRD_PERSON = "A partner is likely to ask ..."
_SKILL_MARKS = {_NOT_REHEARSED, _YOUR_QUESTION, _NOT_COMPUTED, _THIRD_PERSON}
# The one sentence every attack brief in the pack carries since a live run's attacker judged the material for itself.
_RAISE_IT_ANYWAY = "raise it anyway, however short the material, and the refute pass decides"
# The questions a founder answers in their own words before any draft is shown: with a one-click draft on every
# question, a founder may rehearse few answers in their own words.
_OWN_WORDS_FIRST = (
    "The first three questions, and every one in the ends-the-meeting tier, are answered in the founder's own words"
    " before any draft is shown"
)
# The debrief's label for an answer that is a draft the founder took, and the one step it gives.
_DRAFT_TAKEN = '"Draft taken: rehearse it in your own words before the meeting."'
# The mark a draft takes when a figure it cites changes mid-session; no square brackets, which mark an ask.
_STALE = "\"stale\" followed by the figure's name in the founder's words"
# An eval's call: a line that starts with the tool's name and ends with a colon, then its JSON fence.
_LABELLED_CALL = re.compile(r"^`equity_([a-z_]+)`[^\n]*:\n\n```json\n(.*?)^```$", re.MULTILINE | re.DOTALL)
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


def _calls(text: str) -> list[tuple[str, ScenarioInput]]:
    """Each labelled call of an eval: the scenario its label names, and its inputs, validated by that model."""
    calls: list[tuple[str, ScenarioInput]] = []
    for scenario, body in _LABELLED_CALL.findall(_section("## Expected tool call", text)):
        calls.append((scenario, _INPUT_MODELS[scenario].model_validate(json.loads(body)["inputs"])))
    return calls


def _results(text: str) -> list[ScenarioResult]:
    return [compute(inputs) for _, inputs in _calls(text)]


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
    assert "launch one subagent per question in a single message" in refute
    assert "never put two questions in one subagent" in refute
    # A question-bank question is raised by no lens, so lean mode gives it a subagent of its own.
    assert "one that no lens raised gets a subagent of its own" in refute
    assert "you argue neither side" in refute
    assert "When you cannot decide, return Kept" in refute
    assert "Bring in no outside fact" in refute and "do no arithmetic" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "an answering line that is not in the material word for word does not drop the question" in refute
    assert "goes to the quick-rehearsal list" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes
    assert "no percentages and no score" in _unwrapped(_section("### Rank what survives"))


def test_the_calculators_mismatches_head_the_drill_with_no_tier_and_its_flags_open_their_tier() -> None:
    """Where each mismatch and flag goes lives in the flags file beside the codes' meanings, so the skill stays under
    its line cap; the skill keeps the rule that none goes through the review and points to that file."""
    rank = _unwrapped(_section("### Rank what survives"))
    attack = _unwrapped(_section("### Stage A: attack"))
    placed = _unwrapped(_section("## Where the calculator's mismatches and flags go", _FLAGS))

    assert rank.strip().startswith("The calculator's mismatches head the drill, ahead of the tiers")
    assert "the calculator's flags come first, in the order the tool reports them, ahead of everything else" in rank
    assert "flags open weakens it" in rank and "ends the meeting, quoting" not in attack + placed
    assert rank.index("the calculator's flags come first") < rank.index("raised by more than one lens")
    assert "It carries no tier: how much a gap hurts depends on its size" in placed
    # Only a runway below the computed one understates; a percent sold or use of funds below the tool's is a mismatch.
    assert "a runway claim below the computed runway understates it, so it does not head the drill" in placed
    assert "minor tier at most" in placed and "below the tool's figure understates it" not in _TEXT + _FLAGS
    assert "A percent sold or use-of-funds total below the tool's figure is still a mismatch" in placed
    assert "(an understated runway goes in minor)" in rank and "an understated one" not in rank
    assert "Neither goes through the quote check or the refute pass" in placed
    assert "go through neither the lenses, the quote check nor the refute pass" in attack
    assert '"Calculator flags" above' in attack and "a mismatch or a flag" in _unwrapped(_FLAGS)
    assert "read it when a tool returns either" in _unwrapped(_section("## Calculator flags"))
    assert _RAISE_IT_ANYWAY in attack and "rather than a weak question" not in attack


def test_one_cap_rule_sets_how_many_questions_each_lens_returns() -> None:
    """The skill had two caps, three per lens in the brief and two per background lens in the lens section; a lens
    subagent sees only its brief, so the brief now carries the cap it is given."""
    lenses = _unwrapped(_section("## The lenses"))
    attack = _unwrapped(_section("### Stage A: attack"))

    assert "with its own name, test and cap filled in. The cap is the one rule for how many questions a lens" in attack
    assert "three, or two for each background lens run because the background is unknown" in attack
    assert "Return at most [the cap: three, or two] questions" in attack and "Return at most three" not in attack
    assert "with at most two questions each (the Stage A brief's cap)" in lenses


def test_a_question_answered_in_part_is_kept_whole_and_counted_once() -> None:
    """A question answered in part had no rule: it could be split into a kept and a dropped part and counted twice."""
    refute = _unwrapped(_section("### Stage B: refute"))
    answering = _unwrapped(_section("## Answering"))

    assert "stays Kept, whole, never split into a kept and a dropped part" in refute
    assert "the part left is the bracketed ask" in refute
    assert (
        "counts only the lens questions, each once (two lenses' merged question is one, and so is one answered in"
        " part)" in answering
    )


def test_no_runway_call_runs_on_a_cash_figure_the_founder_did_not_give() -> None:
    """A $0 sent for cash the founder had not given makes the no-raise runway row read 0.00 months."""
    steps = _unwrapped(_section("## Steps"))

    assert "Never send cash the founder did not give (no stand-in zero)" in steps
    assert '"not computed: waiting for [cash in the bank today]", never 0.00 months' in steps
    # A zero the founder states is a real input, so its runway is the tool's, as printed.
    assert "A zero the founder states is theirs: send it, and quote the tool's runway as printed" in steps


def test_one_message_mode_debriefs_every_pasted_answer_even_one_no_lens_kept() -> None:
    steps = _unwrapped(_section("## Steps"))
    debrief = _unwrapped(_section("## The debrief"))

    assert "One-message mode: debrief every pasted answer" in steps
    assert "a dropped, answered question with a pasted answer is debriefed too" in steps
    assert f'labelled "{_YOUR_QUESTION}" in place of a lens' in steps
    assert f'"{_NOT_REHEARSED}"' in steps
    assert "each other pasted answer" in debrief and f'"{_YOUR_QUESTION}"' in debrief


def test_the_standing_prep_questions_are_not_refuted_and_invent_nothing() -> None:
    rows = _table("## The questions", _STANDING_PREP)
    text = _unwrapped(_section("## Standing prep questions"))

    assert _STANDING_LINK in text
    assert len(rows) == 6
    assert "are not refuted" in text and "unverified" in text
    assert "never invents a fund, a commitment, a term sheet or a reference" in text


def test_the_debrief_builds_only_from_the_material_and_never_predicts_a_decision() -> None:
    debrief = _unwrapped(_section("## The debrief"))
    answering = _unwrapped(_section("## Answering"))
    shape = _unwrapped(_DEBRIEF)

    assert _DEBRIEF_LINK in debrief
    assert "never an argument about which assumptions would make the stated figure true" in shape
    assert "built only from the founder's material" in shape and "never say a partner or a" in shape
    assert f'in the third person ("{_THIRD_PERSON}")' in answering
    assert '"from the calculator; not refuted"' in answering and "counts only the lens questions" in answering

    assert "built only from the founder's material" in debrief
    assert "bracketed ask" in debrief
    assert "what a yes would need" in debrief
    assert "never say a partner or a firm would invest, pass or score" in debrief


def test_figures_go_to_the_calculator_and_runway_with_no_raise_or_on_a_safe_goes_to_the_runway_plan() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))
    limits = _unwrapped(_section("## Limits"))
    (example,) = re.findall(r"`(\{\"inputs\": .*?\})`", steps)

    assert "no tool computes runway without a raise" not in _TEXT and 'for a SAFE or note raise"' not in _TEXT
    # The example's "..." stand for the founder's figures; with figures in, it is a valid call with no raise.
    assert RunwayPlanInput.model_validate(json.loads(example.replace('"..."', '"1"'))["inputs"]).raises == ()
    assert "the founder's figure as the top-level `stated_runway_months`" in steps
    assert "With no cash or burn given, ask for them; never divide cash by burn yourself" in steps
    assert "the runway claim and the use-of-funds lines go to `equity_runway_plan` too, the raise as cash only" in steps
    assert "from `equity_runway_plan`" in answering and "runway with no raise comes from `equity_runway_plan`" in limits
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps
    assert "Make one call per version of the ask" in steps and "as printed" in steps
    assert "in bracketed asks, table cells and debrief notes too" in steps
    assert '("from $80k to $120k a month", never "$40k more")' in steps


def test_metrics_and_market_sizes_go_to_their_skills_and_only_growth_and_ltv_have_no_tool() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "ARR, retention, churn, CAC payback and burn multiple belong to the vc-metrics-readiness skill" in steps
    assert "a market size to the vc-market-sizing skill (`equity_market_sizing`)" in steps
    assert "LTV, LTV/CAC, the Rule of 40 and the magic number belong to that skill too" in steps
    assert f'Growth rates are quoted with "{_NOT_COMPUTED}"' in steps


def test_a_fully_diluted_total_and_an_unlabelled_valuation_are_handled_as_the_pack_does() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "Fully diluted shares, for the tool, leave SAFEs and notes out" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "never subtract the SAFE or note shares yourself" in steps
    assert "A check that is a mismatch under one reading only is not a calculator mismatch" in steps
    assert "Only a mismatch under every reading is the calculator's mismatch" in steps


def test_every_flag_the_calculator_raises_is_relayed_and_a_benchmark_band_is_never_a_bar() -> None:
    steps = _unwrapped(_section("## Steps"))
    answering = _unwrapped(_section("## Answering"))

    flags = _FLAGS
    deal, runway = flags.split("\n| Flag (`equity_runway_plan`)", 1)
    rows = re.findall(r"^\| `([a-z_]+)` +\|", deal, re.MULTILINE)

    assert _FLAGS_LINK in _section("## Calculator flags")

    assert "Read every code in each tool's `flags` too" in steps
    assert "joins the kept questions as weakens it, with its meaning from the calculator flags table below" in steps
    assert "in the tool's words" not in _TEXT
    # Over MCP a tool returns bare codes, so the skill carries each code's meaning itself, with no band of its own.
    assert rows == list(get_args(DealFlag))
    assert "`cash_never_runs_out`" in flags and "18 months" not in flags and "25%" not in flags
    # Every runway-plan code has its row: a call with a milestone brings codes past the three a plain call returns.
    assert re.findall(r"^\| `([a-z_]+)` +\|", runway, re.MULTILINE) == list(get_args(RunwayPlanFlag))
    assert "only `cash_never_runs_out`, `runway_below_band` and `consistent_beyond_rounding` come back" in _unwrapped(
        flags
    )
    for code in ("`runway_below_band`", "`dilution_above_band`", "`runway_band`", "`dilution_band`"):
        assert code in steps, code
    # The runway plan's band row cites a guide and the deal check's does not, so the skill quotes whichever source the
    # row gives rather than calling every band unverified.
    assert "with the source that row gives, as a common benchmark" in steps and "never as a bar" in steps
    # The answer's Numbers are laid out as the flags file says, so the skill stays under its line cap.
    numbers = _unwrapped(_section("## Numbers in the answer", flags))
    assert '"Numbers in the answer"' in answering and _FLAGS_LINK in answering
    assert "its meaning from the tables below" in numbers and "with the source that row gives" in numbers
    assert "`unverified` source" not in _TEXT
    # Each question keeps to what the tool's own sentence says, never a motive or a doubt the tool does not raise.
    meanings = dict(re.findall(r"^\| `([a-z_]+)` +\| (.+?) +\|$", flags, re.MULTILINE))
    assert "as a VC prices it" in meanings["pool_in_pre_money_lowers_price"]
    assert meanings["net_burn_not_positive"].endswith("which burn does the runway claim use?")
    assert "why?" not in flags and "which burn is real?" not in flags


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
    standing = [row[0] for row in _table("## The questions", _STANDING_PREP)]
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


def test_the_runway_eval_checks_the_no_raise_runway_with_the_runway_plan_and_records_its_live_run() -> None:
    text = _eval("r").read_text(encoding="utf-8")
    answer = _unwrapped(_section("## Expected answer", text))

    assert _eval("r") in _CALL_EVALS
    assert [scenario for scenario, _ in _calls(text)] == ["deal_check", "runway_plan"]
    assert "checked with `equity_runway_plan` on today's spend" in answer and "6.00 months stated, consistent" in answer
    # The founder's "6" is 6.25 months rounded to whole months, so the runway plan's rounding rule holds it.
    assert "rounded to the whole months it is written with" in answer and "minor tier" not in answer
    assert "ahead of the tiers and with no tier" in answer
    assert "## Recorded answer" in text and text.index("## Expected answer") < text.index("## Recorded answer")


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    excerpts = _fences("text", _section("## What the calculator prints (excerpt)", text))

    assert len(_calls(text)) == len(_fences("json", text)) == len(excerpts)
    for result, excerpt in zip(_results(text), excerpts, strict=True):
        printed = [line.rstrip() for line in render_sheet(sheet_for(result)).splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents in the expected answer is a line the report prints."""
    text = path.read_text(encoding="utf-8")
    results = _results(text)
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
    for reference in (_FLAGS, _STANDING_PREP, _DEBRIEF, _DRILL):
        assert not _URL.search(reference) and not _BARE_LINK.search(reference)
    assert "github.com/xiapeli/vc-skills" in sources and "MIT-licensed" in sources
    assert "no text was taken" in sources


def test_no_person_or_firm_is_named_outside_sources_or_in_any_eval_answer() -> None:
    sources_start = _TEXT.index("\n## Sources\n")
    sources_end = _TEXT.index("\n## ", sources_start + 1)
    outside = (_TEXT[:sources_start] + _TEXT[sources_end:]).lower()
    answers = [_section("## Expected answer", path.read_text(encoding="utf-8")).lower() for path in _EVALS]

    for text in (outside, _FLAGS.lower(), _STANDING_PREP.lower(), _DEBRIEF.lower(), _DRILL.lower(), *answers):
        for name in _PEOPLE_AND_FIRMS:
            assert not re.search(rf"\b{re.escape(name)}\b", text), name


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_every_line_an_eval_answer_quotes_is_in_its_prompt_or_is_a_mark_of_the_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))

    for quoted in _DOUBLE_QUOTED.findall(_unwrapped(_section("## Expected answer", text))):
        assert quoted in prompt or quoted in _SKILL_MARKS, quoted


def test_the_top_questions_are_answered_in_the_founders_own_words_before_any_draft_is_shown() -> None:
    """With a one-click draft offered on every question, a founder may rehearse few answers in their own words. "Top"
    is by the drill's order, so a calculator mismatch, which heads the drill with no tier, is among them."""
    steps = _unwrapped(_section("## Steps"))
    drill = _unwrapped(_DRILL)

    assert _OWN_WORDS_FIRST in steps and _DRILL_LINK in steps and "read it before question 1" in steps
    assert steps.index("6. **Drill.**") < steps.index(_OWN_WORDS_FIRST) < steps.index("One-message mode")
    assert "ask for the founder's own answer with no draft shown and no draft to pick" in drill
    assert "Once the founder has answered, or skipped it, the draft may be shown beside the answer" in drill
    assert "Every other question may offer the draft from the start" in drill
    # A founder's request for a draft on every question does not lift the rule on the top ones.
    assert "When the founder asks for a draft on every question, the rule still holds on these" in drill
    assert "say in one line that the draft comes right after their answer or a skip" in drill
    # A draft fills no gap the material leaves open, and a taken draft is never the founder's answer.
    assert (
        "A draft is built as a stronger answer is: only from the founder's material and tool results, every gap a"
        " bracketed ask, no figure worked out by hand" in drill
    )
    assert "A draft the founder takes is the skill's text, not the founder's answer" in drill
    assert "it adds nothing to the founder's material" in drill
    assert "the debrief says the draft was taken, never that the answer held up" in drill
    # The first turn's rule moved here whole, so the skill and its drill page never give two versions of it.
    assert "The first turn** names the lenses and puts question 1" in drill and "The first turn names" not in _TEXT
    assert "so the kept list is not shown before the drill" in drill


def test_a_draft_the_founder_takes_is_labelled_draft_taken_never_held_up() -> None:
    """A taken draft is the skill's text, not the founder's answer, so its debrief entry is labelled "Draft taken", with
    the step a founder needs (rehearse it in their own words), in place of what was weak or "held up". The debrief page
    defines it where "held up" is, the drill names it, and the skill's debrief summary and hardest three carry it."""
    shape = _unwrapped(_DEBRIEF)
    drill = _unwrapped(_DRILL)

    assert (
        '- **Draft taken,** in place of what was weak or "held up", when the founder took the skill\'s draft' in shape
    )
    assert "quoted as the skill's text, with no answer label, since it adds nothing to the founder's material" in shape
    assert "gets no weak notes and no stronger answer, being one already" in shape
    assert f"The entry reads {_DRAFT_TAKEN}" in shape
    # Only a draft that is the whole answer takes the label; the founder's own words beside it are debriefed as usual.
    assert "It is used only where the taken draft is the whole answer" in shape
    assert "an answer the founder also gave in their own words is debriefed as any answer" in shape
    held_up = shape.index('Say "held up" when nothing was weak')
    assert held_up < shape.index("**Draft taken,**") < shape.index("**A stronger answer,**")
    # The drill's rule names the label after its pinned sentence, which stays as it was.
    assert 'The debrief labels it "Draft taken", with the step [debrief.md](debrief.md) gives it' in drill
    assert drill.index("never that the answer held up") < drill.index('labels it "Draft taken"')
    assert 'what was weak, "held up" or "Draft taken"' in _unwrapped(_section("## The debrief"))
    answering = _unwrapped(_section("## Answering"))
    assert (
        "whether the founder's answer held up, or \"Draft taken\" where the founder took the skill's draft" in answering
    )
    assert 'a stronger one (none for "Draft taken")' in _unwrapped(_section("## Steps"))


def test_a_follow_up_is_in_the_founders_everyday_words_never_the_skills_or_investors_terms() -> None:
    """A follow-up worded in the skill's own terms or investors' jargon leaves a founder asking for plain language."""
    drill = _unwrapped(_DRILL)

    assert "Ask at most one follow-up per question" in drill and "Ask at most one follow-up" not in _TEXT
    assert "only when the answer leaves out the specific thing the question asked for" in drill
    assert "Word it in the founder's everyday words, never this skill's terms" in drill
    assert "(a lens, a tier, a kept question) or investors' jargon" in drill
    # The good form: a plain question, then what is enough to answer it.
    assert "a plain question, then what is enough to answer it" in drill and "rough timing is enough" in drill
    assert "a follow-up in the founder's everyday words" in _unwrapped(_section("## Steps"))
    # The skill puts every partner question in the third person; a follow-up is the moderator's own.
    assert "A follow-up is the moderator's own question, put to the founder directly" in drill
    assert "it is never worded as a partner's" in drill


def test_a_draft_that_cites_a_figure_the_founder_changes_is_marked_stale_and_redone_through_the_tool() -> None:
    """A figure can change mid-session, and every draft that cites it is then redone from the new figure."""
    drill = _unwrapped(_DRILL)

    assert "When the founder changes a figure mid-session" in drill
    assert "mark every draft that cites the old one, in the drill, the standing prep or a stronger answer" in drill
    assert f"a stronger answer, {_STALE}, then redo each from the new figure" in drill
    # A computed figure is computed again, never patched or worked out by hand.
    assert "A figure a tool computed goes through that tool again" in drill
    assert "a new call with the new figure as step 3 says" in drill
    assert "never an edit of the old result or the new figure worked out by hand" in drill
    assert "Make one call per version of the ask" in _unwrapped(_section("## Steps"))
    assert "a draft redone when a figure changes" in _unwrapped(_section("## Steps"))
    # Only the founder's word makes a figure changed; a figure that merely differs is the debrief's disagreement.
    assert "A figure has changed only when the founder says the new one replaces one they gave" in drill
    assert (
        "an answer whose figure differs from the material's with no such word is a disagreement for the debrief"
        in drill
    )
    assert "a bracketed ask asks which stands before anything is redone" in drill
    assert "The old line stays quoted as written and is no longer a disagreement" in drill
    assert "bringing it up to date is one open ask" in drill
    assert "For the changed figure the new call replaces the old one" in drill
    assert "its verdict, mismatches and flags are the ones the drill's order, the kept table" in drill
    assert "the kept table and the answer's Numbers use" in drill
    # The rule reaches one-message mode too, through the page both modes read.
    assert "When the founder changes a figure after an answer was drafted or debriefed" in _unwrapped(_DEBRIEF)
    assert '"A figure that changes" in [drill.md](drill.md) applies, in either mode' in _unwrapped(_DEBRIEF)


def test_a_spoken_answer_weaker_than_the_materials_own_line_gets_a_tiered_rewrite() -> None:
    """A spoken answer weaker than the material's own line is rewritten: checkable items first, the rest plainly."""
    shape = _unwrapped(_DEBRIEF)

    assert "it claims less than the material's own line on the same point (both quoted)" in shape
    assert "When the spoken answer claims less than the material's own line, the stronger answer is tiered" in shape
    assert "it leads with the strongest items a partner can check, each with its label" in shape
    assert "then says the rest plainly for what it is" in shape and "never dressed up as more" in shape
    assert "the stronger answer is tiered within the same four sentences" in shape
    # A lower figure, or a claim taken back, is a disagreement: the founder's spoken answer may be the truer one.
    assert (
        "Where the answer gives a different figure, count or date than the line, or takes the claim back, it is a"
        " disagreement, as above, and the stronger answer never restores the bigger claim: its bracketed ask asks"
        " which stands" in shape
    )
    # The tiered rewrite is still a stronger answer: built only from the material, every gap a bracketed ask.
    assert shape.index("built only from the founder's material") < shape.index("the stronger answer is tiered")


def test_each_short_standing_answer_gets_one_specific_next_step_and_a_silent_one_its_bracketed_ask() -> None:
    """A standing question the material says nothing on keeps its bracketed ask, and each short answer gets one specific
    next step, the one that gets the answer ready before the meeting."""
    rows = _table("## The questions", _STANDING_PREP)
    steps = {row[0]: row[2] for row in rows}
    prep = _unwrapped(_STANDING_PREP)
    shape = _unwrapped(_DEBRIEF)
    standing = _unwrapped(_section("## Standing prep questions"))
    answering = _unwrapped(_section("## Answering"))

    assert all(len(row) == 3 and row[2] for row in rows)
    others = steps["Which other investors are you meeting, and who has committed?"]
    # Spoken interest is not a yes, so the step covers both and treats neither as a commitment.
    assert "in writing" in others and "whose interest or yes is only spoken" in others
    assert "today's cash, spend and revenue" in steps["What happens if this round does not close?"]
    assert "Line up the references" in steps["Whom will the partner call, on your list and off it?"]
    assert "today's runway in months" in steps["What happens if this round does not close?"]
    assert "`equity_runway_plan`" in steps["What happens if this round does not close?"]
    assert "Where the material says nothing on a standing question, its bracketed ask carries it" in prep
    assert "a next step never assumes an answer the founder did not give" in prep
    # Short means not yet ready, wherever the answer came from; a brief, complete answer gets no step.
    assert (
        "An answer is short when it does not yet give what the middle column says the founder should have ready,"
        " whether it came with the material or in the drill; a brief answer that gives it gets no next step" in prep
    )
    assert "The sixth question's step always shows, since it is the founder's to ask" in prep
    # The step is written once, in the answer's Standing prep.
    assert "written once, in the answer's Standing prep" in prep
    assert "It is written once, in the answer's Standing prep, not again in this question's debrief" in shape
    assert "putting spoken interest in writing" in shape and "spoken yes" not in shape
    assert "**One next step,** for a standing question only" in _DEBRIEF
    assert "where the founder's answer is short, it gets the one specific next step that file names for it" in shape
    assert "the one next step a short answer gets" in standing and "and a short answer's next step" in answering


def test_the_drill_eval_asks_for_the_founders_own_words_first_and_gives_each_short_answer_a_next_step() -> None:
    text = _eval("dm").read_text(encoding="utf-8")
    first = _unwrapped(text.split("\n## ", 1)[0])
    prompt = _unwrapped(_section("## Prompt", text))
    answer = _unwrapped(_section("## Expected answer", text))

    assert _eval("dm") in _NO_CALL_EVALS and "## Recorded answer" not in text
    assert "came from the skill's first live drill" in first
    assert "offer me a draft answer I can pick on every question" in prompt
    assert "no draft shown and no draft to pick" in answer and "Once the founder answers or skips" in answer
    # The run is scripted over several turns, so one run can show both the own-words rule and the standing prep.
    assert "the tester answers question 1 in a sentence, skips question 2, answers question 3 in a sentence" in first
    assert "then says stop" in first and "on the three questions put before the stop" in first
    assert "I don't have the cap or our cash figures today, so go on without them" in prompt
    assert "On the first three questions, and on every one in the ends-the-meeting tier" in answer
    # Each of the five short answers on the round so far is quoted with its own next step.
    short = [quoted for quoted in _DOUBLE_QUOTED.findall(answer) if quoted in prompt]
    assert len(short) == 5 and "each of the five short answers is quoted and gets one specific next step" in answer
    assert "in writing" in answer and "line up references" in answer and "`[cash in the bank today]`" in answer
    assert "never calls either keen fund committed" in answer


def test_the_readme_badge_counts_the_skill_folders() -> None:
    badge = _BADGE.search((_ROOT / "README.md").read_text(encoding="utf-8"))
    folders = sorted((_ROOT / "skills").glob("*/SKILL.md"))

    assert badge is not None
    assert int(badge.group(1)) == int(badge.group(2)) == len(folders), (badge.groups(), len(folders))
