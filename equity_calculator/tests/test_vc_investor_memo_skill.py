"""The vc-investor-memo skill keeps its shape: the memo's sections, its outcome rules, its dissent pass and its evals.

The founder drafts the memo their champion partner is likely to write; the skill writes it in the third person with no
recommendation, speaks as no investor or firm, and does no fund math. Every calculator tool it names must be a tool the
MCP server serves (never ``equity_investor``, which is the founder's trade test, not an investor return), and every
skill it hands off to by name must be a folder in skills/. The memo's sections are fixed rows, each citing a read
source, the calculator or the skill's own unverified judgment. The outcome case keeps the round's payouts and a later
round's stake apart with a fixed label. The dissent pass keeps both stages: five lenses named by what they test, each
objection quoting a line word for word, and a refute pass with the fixed verdicts; the survivors become a ranked fix
list in three tiers. Each eval in evals/vc-investor-memo/ has a prompt, an expected tool call and an expected answer;
each call is labelled with its tool, is valid, and carries an excerpt that is lines of the report that call prints.
The tools' flags come back as bare codes over MCP, so the skill carries a meaning for every code. An eval run in a live
session records an excerpt of that run under "Recorded answer"; the others say they have not been run.
"""

from __future__ import annotations

import json
import re
import shlex
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.__main__ import _INPUT_MODELS, run
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag
from equity_calculator.schemas.equity_waterfall import WaterfallInput
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-investor-memo" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-investor-memo").glob("*.md"))
_EVAL_COUNT = 6
# The repository gives each made-up company its own letters; this skill's evals use BM to BR.
_EVAL_LETTERS = ("bm", "bn", "bo", "bp", "bq", "br")
_NO_CALL = "## Expected tool call\n\nNone:"
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
# Each eval call sits under its own heading naming the tool, so a call is never matched to the wrong scenario.
_CALL_HEADING = re.compile(r"^### Call \d+: `equity_([a-z_]+)`", re.MULTILINE)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_TOOLS_USED = {
    "equity_deal_check",
    "equity_round",
    "equity_pool",
    "equity_waterfall",
    "equity_dilution",
    "equity_runway_plan",
}
_NOT_USED = "equity_investor"
_HANDOFF_SKILLS = (
    "vc-deck-review",
    "vc-claims-check",
    "vc-partner-meeting",
    "vc-deal-math",
    "equity-calculator",
    "vc-positioning",
    "vc-diligence-questions",
    "vc-metrics-readiness",
    "vc-market-sizing",
    "vc-round-sizing",
    "vc-term-sheet-review",
)
# Evals run in a live session: each records an excerpt of the run, blockquoted, under "## Recorded answer".
_RECORDED = ("bm",)
_NOT_RUN_LIVE = "has not been run in a live session"
_RECORDED_HEADING = "\n## Recorded answer\n"
_ONE_PER_SUBAGENT = "launch one subagent per objection in a single message; never put two objections in one subagent"
_RAISE_ANYWAY = (
    "Do not judge whether another line answers an objection: raise it anyway, however short the material; the refute "
    "pass decides."
)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "write the investment memo for my champion",
    "draft our IC memo",
    "what will the partner write about us",
    "make the case for us internally",
)
_SECTIONS = (
    "Summary",
    "The company",
    "Why now",
    "Market and competition",
    "Traction",
    "Team",
    "The round",
    "Top risks and mitigations",
    "The outcome case",
    "Open questions",
)
_LENSES = ("Market and why now", "Traction and evidence", "Team", "Round and outcome", "Risks left out")
_REFUTE_VERDICTS = ("Dropped, answered:", "Dropped, not grounded:", "Kept:")
_TIERS = ("**sinks the case**", "**weakens it**", "**minor**")
_PATTERN_ROWS = 8
_SOURCES_USED = {
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
    "https://www.sequoiacap.com/article/writing-a-business-plan/",
    "https://paulgraham.com/swan.html",
}
# The short names a Source cell may start with: the three read guides, the shipped skill, the tool, or its own call.
_SOURCE_NAMES = ("YC seed guide", "Sequoia", "Graham", "vc-claims-check", "the calculator", "Ours")
_UNVERIFIED = "unverified"
_OURS_UNVERIFIED = "Ours, unverified"
_URL = re.compile(r"https?://\S+")
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_FIX_COLUMNS = re.compile(
    r"Rank, Tier, Section, Lens, The line \(quoted\), Why a partner arguing against the\s+deal uses it, Fix"
)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_SCORE = re.compile(r"/\s*100\b|out of 100", re.IGNORECASE)
# Fund-math words that may appear only where the skill says it does not do fund math.
_FUND_MATH = ("IRR", "fund size of", "returns the fund", "multiple on invested", "share of a fund")
_HEADER_LINE = (
    "Drafted by the founders from their own material; figures from the equity calculator; not the firm's format."
)
_NOT_RUN = "not run: the waterfall needs whole share counts; send the pro forma cap table"
# A SAFE or note round runs no waterfall at all: the SAFE holds no shares until the priced round it converts in.
_NOT_RUN_SAFE = (
    "not run: a SAFE or note holds no shares until the priced round it converts in, so this round has no payout to show"
)
_SAFE_LABEL = (
    "The stake is [stake] after the founder's assumed priced round and [final stake] after the founder's assumed later "
    "rounds (calculator); what the stake pays at an exit is not checked: no tool computes this."
)
_NOT_CHECKED = "not checked: no tool computes this"
_LABEL = (
    "The payouts above use the cap table right after this round, before any later round. After the founder's assumed "
    "later rounds the stake is [final stake] (calculator); the payout after those rounds is not checked: no tool "
    "computes this."
)
# Company BM's round, as the skill's own excerpt under "The round" was printed from it.
_COMPANY_BM_ROUND = {
    "investment": "3000000",
    "pre_money": "12000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "holder_shares": 8000000,
    "stated_holder_percent": "59",
    "cash_on_hand": "400000",
    "planned_monthly_gross_burn": "190000",
    "planned_monthly_revenue": "40000",
    "stated_runway_months": "23",
}
# The skill's prose quotes the whole-share effective pre-money of Company BM's round from this pool call.
_COMPANY_BM_POOL = {
    "fully_diluted_shares": 10000000,
    "unissued_pool_shares": 500000,
    "pre_money": "12000000",
    "investment": "3000000",
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "share_rounding": "whole_shares",
}
_NEGATION = re.compile(r"\b(no|never|not)\b")
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|-?\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")


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


def _fences(language: str, text: str = _TEXT) -> list[str]:
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


def _names_a_person_or_firm(text: str) -> bool:
    return any(re.search(rf"\b{name}\b", text.lower()) for name in _PEOPLE_AND_FIRMS)


def _cites_a_source_or_ours(cell: str) -> bool:
    """Each ``; ``-separated part of a Source cell names a read source, the calculator, or is its own judgment."""
    return all(part.startswith(_SOURCE_NAMES) or _UNVERIFIED in part for part in cell.split("; "))


def _calls(text: str) -> list[tuple[str, dict[str, object], str]]:
    """Each eval call as its scenario, its ``inputs`` and its excerpt, read from under its labelled heading."""
    body = _section("## Expected tool call", text)
    heads = list(_CALL_HEADING.finditer(body))
    calls = []
    for head, after in zip(heads, [*heads[1:], None], strict=True):
        block = body[head.end() : after.start() if after else len(body)]
        (call,) = _fences("json", block)
        (excerpt,) = _fences("text", block)
        calls.append((head.group(1), json.loads(call)["inputs"], excerpt))
    return calls


def _report(scenario: str, inputs: dict[str, object]) -> str:
    return render_sheet(sheet_for(compute(_INPUT_MODELS[scenario].model_validate(inputs))))


def _eval(letter: str) -> tuple[str, str]:
    """The unwrapped prompt and expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-investor-memo"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "champion", "dissent pass", "no fund math", "Never invents traction"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert named == _TOOLS_USED, named ^ _TOOLS_USED
    assert named <= served, named - served
    assert _NOT_USED not in _TEXT
    assert "`equity_calculator deal_check`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    when = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in when, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "Planned, not yet shipped" not in when
    assert "the vc-investor-memo skill" in _unwrapped(_section("## When to use it", _POSITIONING))


def test_the_memo_shape_is_the_fixed_sections_each_with_a_read_source_or_ours() -> None:
    rows = _table("## The memo's shape")
    shape = _unwrapped(_section("## The memo's shape"))

    assert tuple(row[0] for row in rows) == _SECTIONS
    for section, _, source in rows:
        assert _cites_a_source_or_ours(source), section
    for section in ("Top risks and mitigations", "Open questions"):
        (row,) = (row for row in rows if row[0] == section)
        assert row[-1] == _OURS_UNVERIFIED, section
    assert "The shape is this skill's own, unverified" in shape
    assert "Never volunteer a market-size threshold" in shape
    assert f'"{_NOT_CHECKED}"' in shape


def test_the_memo_is_third_person_with_no_recommendation() -> None:
    shape = _unwrapped(_section("## The memo's shape"))
    intro = _unwrapped(_TEXT.split("\n## ", 1)[0])
    answering = _unwrapped(_section("## Answering"))

    assert "**Third person, no verdict.**" in shape
    for banned in ('"we recommend"', '"we should invest"', '"pass"', '"a strong yes"'):
        assert banned in shape, banned
    assert "the memo leaves no slot for one" in shape
    assert "carries no recommendation" in intro and "never plays an investor" in intro
    assert f'"{_HEADER_LINE}"' in answering
    assert "no conviction score, no grade and no odds" in _unwrapped(_section("## Limits"))
    assert not _SCORE.search(_TEXT)


def test_the_round_goes_to_the_round_tools_and_asks_the_fully_diluted_basis() -> None:
    round_ = _unwrapped(_section("## The round"))
    inputs = _unwrapped(_section("## Inputs"))

    assert "`equity_deal_check`" in round_ and "`equity_round`" in round_ and "`equity_runway_plan`" in round_
    assert "not passed as `investment`" in round_ and "vc-deal-math step 2" in round_
    assert "call twice, once as `pre_money`, once as `post_money`" in round_
    assert "A mismatch that appears under only one reading is not listed as a computed mismatch" in round_
    # A SAFE converting in a priced round goes to the tool, or the founders' percent comes out too high.
    assert "each SAFE or note converting in this round as `instruments`" in round_
    assert "`current_monthly_gross_burn`" in round_ and "as planned after the raise and today's" in inputs
    assert "without a verdict" in round_
    # The calculator leaves SAFEs and notes out of the fully diluted count, so both the intake and the round ask.
    assert "SAFEs and notes excluded" in round_ and "ask which way the founder's does" in round_
    assert "the calculator's count leaves them out" in inputs
    assert "`[fully diluted shares before the round, SAFEs and notes left out]`" in round_
    assert "never subtract the SAFE or note shares yourself" in round_
    # Use of funds on a SAFE raise, and runway with no raise, go to the runway plan; missing cash or burn is asked.
    assert "The runway claim and the use-of-funds lines on a SAFE or note raise go to `equity_runway_plan`" in round_
    assert '"use_of_funds": [{"percent"}]' in round_
    assert "**Runway with no raise** (what happens if the round does not close), on any instrument" in round_
    assert "With no cash on hand or no burn given, ask for them; make no runway call until they are in" in round_
    # Today's figures go to the tool only when they differ from the plan.
    assert "`current_monthly_revenue`) only when the founder gives a different figure for today" in round_
    # A flag is a bare code over MCP: it goes to the fix list and to Numbers with the skill's own meaning.
    assert "in the words the tool prints" not in _TEXT
    assert (
        "goes into the fix list, after the computed mismatches and with no tier" in round_ and "into Numbers" in round_
    )
    assert "Over MCP a flag comes back as a bare code" in round_
    assert "with the source that row gives" in round_
    assert "0.200000 is 20.0000%" in round_ and "That is notation, not a calculation; never round it" in round_
    assert "common benchmarks, not rules" in round_


def test_the_deal_check_excerpt_is_what_the_calculator_prints() -> None:
    (excerpt, _) = _fences("text")
    report = render_sheet(sheet_for(compute(DealCheckInput.model_validate(_COMPANY_BM_ROUND))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


def test_the_waterfall_example_is_valid_and_prints_its_excerpt() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]
    (_, excerpt) = _fences("text")

    assert WaterfallInput.model_validate(inputs).scenario == "waterfall"
    printed = [line.rstrip() for line in _report("waterfall", inputs).splitlines()]
    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_waterfall_command_is_the_same_call_as_the_json_example() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")
    assert command.startswith(_PROGRAM) and "\n" not in command.strip()

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        WaterfallInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_the_outcome_rules_name_no_fund_math() -> None:
    outcome = _unwrapped(_section("## The outcome case"))
    limits = _unwrapped(_section("## Limits"))

    for phrase in (
        "takes no fund size",
        'never writes "this returns the fund"',
        # A payout beside the amount invested reads as a return multiple at a glance, so the two never sit together.
        "The amount invested never sits beside a payout, in the table or in a sentence",
        'The amount invested appears only in "The round"',
        "Never multiply a stake by an exit value",
        f'"{_LABEL}"',
        f'"{_NOT_RUN}"',
        "the founder's assumption",
        "`whole_shares`",
        "`exit_is_shared_amount`",
        "these are the calculator's defaults, not agreed terms",
        "the round's tool printed it",
        # On a SAFE round, the SAFE's own row is the stake, and the priced round equity_round counted is not repeated.
        'the row `equity_round` prints for the instrument this round sells, never "Ownership: investor"',
        "pass the outstanding ones first and this round's last, and take the row with that number",
        "one `equity_dilution` call per row",
        "`rounds` holds only the rounds after that priced round",
        f'"{_NOT_RUN_SAFE}"',
        f'"{_SAFE_LABEL}"',
        # The existing_holders row holds earlier preferred too, so it is common_shares only with no earlier class.
        "only when there are no granted options (or the founder says to count them all as exercised) and no earlier "
        "preferred class; otherwise take issued common from the pro forma or the founder's count, or the earlier class "
        "is counted twice",
        "Each SAFE or note converted in this priced round is its own class too, never part of `common_shares`",
        "`equity_pool` refuses a `target_pool_percent` of 0",
        "Never add or subtract shares yourself",
        "pass it as the integer `2714285`",
    ):
        assert phrase in outcome, phrase
    assert 'no multiple on invested, no return rate, no "returns the fund"' in limits
    # A fund-math term appears only in a sentence that says the skill does not do it.
    for sentence in re.split(r"(?<=\.)\s+", _unwrapped(_TEXT)):
        for term in _FUND_MATH:
            if term in sentence:
                assert _NEGATION.search(sentence), (term, sentence)


def test_the_outcome_table_and_the_evals_never_set_a_payout_beside_the_amount_invested() -> None:
    answering = _unwrapped(_section("## Answering"))

    assert "beside the amount invested" not in _unwrapped(_TEXT)
    assert "each class's payout, Converts?, Common's payout; never the amount invested" in answering
    assert "Invested," not in answering
    for path in _EVALS:
        expected = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))
        assert not re.search(r"beside \$[\d,]+ invested|\.\d{2} beside \$", expected), path.name


def test_the_prose_figure_from_the_pool_tool_is_what_it_prints() -> None:
    printed = _report("pool", _COMPANY_BM_POOL)

    assert re.search(r"^  Effective pre-money +\$10,500,000\.83  ", printed, re.MULTILINE)
    assert "$10,500,000.83 against $10,500,000.00 for Company BM's effective pre-money" in _unwrapped(_TEXT)


def test_the_lenses_are_the_five_and_name_no_person_or_firm() -> None:
    attack = _section("### Stage A: attack")
    rows = _table("### Stage A: attack")
    brief = _unwrapped(attack)

    assert tuple(row[0] for row in rows) == _LENSES
    assert not _names_a_person_or_firm(attack)
    for phrase in (
        "third person",
        "do no arithmetic",
        '"nothing found"',
        "quoted word for word",
        _RAISE_ANYWAY,
        "run the lenses as parallel subagents, however short the material, all launched in one message",
        "not the tool results",
        "less independent than subagents",
        # Without subagents a draft has no memo when the lenses run, so two checks run on the draft after step 6.
        "After step 6, two draft checks run on the drafted memo, each written down before Stage B",
        "is not objected to for lacking that answer",
        "do not go through the lenses or the refute pass",
    ):
        assert phrase in brief, phrase
    steps = _unwrapped(_section("## Steps"))
    note = "Without a subagent tool, run Stage A of the dissent pass first, before step 1"
    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    subagents_first = "With a subagent tool (in Claude Code, the Agent or Task tool), step 7 runs the five lenses"
    assert subagents_first in steps and steps.index(subagents_first) < steps.index(note)
    assert "it goes in the minor tier at most" in brief and "the claim below the computed runway" in brief


def test_the_refute_pass_uses_the_fixed_verdicts_and_names_no_person_or_firm() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = stage.split("\n\nThe refute brief:\n\n", 1)
    words = _unwrapped("\n".join(line for line in brief.splitlines() if not line.startswith("|")))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in words, verdict
    assert _ONE_PER_SUBAGENT in _unwrapped(handoff)
    assert 'everything from "The refute brief:" to the end of this stage' in _unwrapped(handoff)
    for rule in (
        "you argue neither side",
        "When you cannot decide, return Kept",
        "Bring in no outside fact about the company, its market or its competitors",
        "do no arithmetic",
        "invents nothing on the founder's behalf",
        "neither does one that is the objected line itself",
        "does not drop it: the objection is Kept for the part left",
    ):
        assert rule in words, rule
    assert not _names_a_person_or_firm(words)
    quotes = _unwrapped(_section("### Check the quotes"))
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_every_pattern_row_cites_a_read_source_or_says_unverified() -> None:
    rows = _table("### Stage B: refute")

    assert len(rows) == _PATTERN_ROWS
    for pattern, why, source in rows:
        assert why, pattern
        assert _cites_a_source_or_ours(source), pattern
    assert sum(_UNVERIFIED in row[-1] for row in rows) >= len(rows) // 2


def test_the_ranked_fix_list_has_the_three_tiers_and_no_score() -> None:
    ranked = _unwrapped(_section("### The ranked fix list"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    assert "**figures that do not match (computed)**" in ranked and "with no tier" in ranked
    assert "no percentages and no score" in ranked
    assert "goes into the memo's Top risks, in the founder's words" in ranked
    assert "the flags follow them, also with no tier" in ranked
    assert "A Kept objection answered in part says so in its Fix cell" in ranked
    assert "its Open questions section lists its own bracketed asks in full" in answering
    assert "never points to the answer's Open asks" in answering
    assert "Say how the lenses and the refute pass ran (as subagents, one refute subagent per objection)" in answering
    assert "each flag as its code with its meaning from the flag table" in answering
    shape = _unwrapped(_section("## The memo's shape"))
    assert 'never restated in words ("nearly half", "most")' in shape
    assert "no figure is restated in words" in _unwrapped(_section("## Steps"))
    assert answering.index("**The biggest fixes,**") < answering.index("**Ranked fix list,**")
    assert "Lead with the biggest fixes, then the memo, then the full fix list." in answering
    assert _FIX_COLUMNS.search(answering) and "**Dropped,**" in answering
    assert "not investment, legal or tax advice" in answering


def test_sources_are_the_read_set() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == _SOURCES_USED
    assert set(_URL.findall(_TEXT)) == listed
    assert listed - set(_READ_SOURCES) == {"https://paulgraham.com/swan.html"}
    sources = _unwrapped(_section("## Sources"))
    assert "this skill's own judgment, unverified" in sources and "claims no such knowledge" in sources


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name
        assert "A run passes when" in _unwrapped(text), path.name
        recorded = path.name.split("-")[1] in _RECORDED
        assert (_RECORDED_HEADING in text) == recorded, path.name
        assert (_NOT_RUN_LIVE in text) != recorded, path.name


@pytest.mark.parametrize("letter", _RECORDED)
def test_a_recorded_run_is_a_blockquoted_excerpt_after_the_expected_answer(letter: str) -> None:
    """The recorded answer is the run's own text, quoted, so no heading or fence in it is read as the eval's own."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    header = _unwrapped(text.split("\n## Prompt\n", 1)[0])
    recorded = text.split(_RECORDED_HEADING, 1)[1]
    lines = [line for line in recorded.splitlines() if line.strip()]
    quoted = [line for line in lines if line.startswith(">")]

    assert text.index("\n## Expected answer\n") < text.index(_RECORDED_HEADING)
    assert "is an excerpt of a recorded run (Claude Code" in header
    assert "Recorded with Claude Code" in recorded and quoted
    assert all(line.startswith(">") for line in lines[lines.index(quoted[0]) :])
    assert not any(line.startswith(("#", "```")) for line in lines)


def test_every_flag_code_each_round_tool_returns_has_a_meaning_in_the_skill() -> None:
    """Over MCP the tools return bare codes, so the skill must say what each one means."""
    rows = {row[0].strip("`"): row[1] for row in _table("## Flags")}

    for code in get_args(DealFlag):
        assert "deal check" in rows[code], code
    for code in get_args(RunwayPlanFlag):
        assert "runway plan" in rows[code], code
    assert set(rows) == set(get_args(DealFlag)) | set(get_args(RunwayPlanFlag))


def test_the_exit_statement_the_skill_quotes_is_the_waterfalls_own() -> None:
    """The memo quotes the waterfall's exit_is_shared_amount statement word for word, so the skill's copy must match."""
    result = compute(WaterfallInput.model_validate(json.loads(_fences("json")[0])["inputs"]))
    (statement,) = (row.statement for row in result.assumptions if row.key == "exit_is_shared_amount")

    assert f'`exit_is_shared_amount`: "{statement}"' in _unwrapped(_section("## The outcome case"))


def test_metrics_and_market_sizes_go_to_their_skills_and_only_growth_and_ltv_stay_unchecked() -> None:
    shape = _unwrapped(_section("## The memo's shape"))
    limits = _unwrapped(_section("## Limits"))

    assert "ARR, retention, churn, CAC payback and burn multiple are checked against their parts by the" in shape
    assert "a market size is built bottom-up by the vc-market-sizing skill" in shape
    assert f'Growth rates and LTV are quoted as stated, with "{_NOT_CHECKED}"' in shape
    assert "Growth rates, market sizes, retention and unit economics" not in _TEXT
    assert "checked by the vc-metrics-readiness and vc-market-sizing skills" in limits


def test_the_no_call_eval_carries_no_call_or_excerpt() -> None:
    (path,) = _NO_CALL_EVALS
    text = path.read_text(encoding="utf-8")

    assert path.name.startswith("company-bo-")
    assert _fences("json", text) == [] and _fences("text", text) == []
    assert not _CALL_HEADING.search(text)


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls = _calls(text)

    assert calls and len(calls) == len(_fences("json", text)) == len(_fences("text", text))
    for scenario, inputs, excerpt in calls:
        printed = [line.rstrip() for line in _report(scenario, inputs).splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, (scenario, line)


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents the expected answer gives is one a report prints."""
    text = path.read_text(encoding="utf-8")
    reports = "\n".join(_report(scenario, inputs) for scenario, inputs, _ in _calls(text))
    # A line quoted from the founder's material keeps its own figures ("SAFE investors own 12.5%"); only the rest of
    # the answer takes figures from the calculator.
    prompt = _unwrapped(_section("## Prompt", text))
    answer = _DOUBLE_QUOTED.sub(
        lambda quoted: "" if quoted.group(1) in prompt else quoted.group(0),
        _unwrapped(_section("## Expected answer", text)),
    )
    figures = _PRINTED_FIGURE.findall(answer)

    assert figures
    for figure in figures:
        assert figure in reports, figure


@pytest.mark.parametrize("path", _EVALS, ids=[path.stem for path in _EVALS])
def test_every_line_an_eval_answer_quotes_is_in_its_prompt_or_in_the_skill(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))
    skill = _unwrapped(_TEXT)

    for quoted in _DOUBLE_QUOTED.findall(_unwrapped(_section("## Expected answer", text))):
        assert quoted in prompt or quoted in skill, quoted


def test_one_eval_feeds_the_tools_percent_to_dilution() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-bn-"))
    calls = _calls(path.read_text(encoding="utf-8"))
    (deal,) = (inputs for scenario, inputs, _ in calls if scenario == "deal_check")
    (dilution,) = (inputs for scenario, inputs, _ in calls if scenario == "dilution")
    printed = _report("deal_check", deal)

    assert re.search(r"^  Investors' share of the cap table +25\.0000%  ", printed, re.MULTILINE)
    assert dilution["holder_percent"] == "25" and deal["stated_investor_percent"] == "20"


def test_one_eval_runs_no_waterfall_without_whole_shares() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-bp-"))
    text = path.read_text(encoding="utf-8")
    scenarios = [scenario for scenario, _, _ in _calls(text)]
    _, answer = _eval("bp")

    assert scenarios == ["round", "runway_plan", "dilution"]
    assert _NOT_RUN_SAFE in answer and re.search(r"^  SAFE 1: shares +1,428,571\.429  ", text, re.MULTILINE)


def test_the_safe_eval_feeds_the_safes_own_row_to_dilution() -> None:
    """A SAFE round's later-round stake starts from the SAFE's row of equity_round, never the priced round's buyer."""
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-bp-"))
    calls = _calls(path.read_text(encoding="utf-8"))
    (round_,) = (inputs for scenario, inputs, _ in calls if scenario == "round")
    (dilution,) = (inputs for scenario, inputs, _ in calls if scenario == "dilution")
    printed = _report("round", round_)
    safe = re.search(r"^  Ownership: SAFE 1 +([\d.]+)%  ", printed, re.MULTILINE)
    investor = re.search(r"^  Ownership: investor +([\d.]+)%  ", printed, re.MULTILINE)
    rounds = dilution["rounds"]

    assert safe and investor
    assert dilution["holder_percent"] == safe.group(1) != investor.group(1)
    # Only the Series B: equity_round already counted the Series A the SAFE converts in.
    assert isinstance(rounds, list) and len(rounds) == 1


def test_one_eval_takes_issued_common_not_the_existing_holders_row_with_an_earlier_class() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-bq-"))
    calls = _calls(path.read_text(encoding="utf-8"))
    (pool,) = (inputs for scenario, inputs, _ in calls if scenario == "pool")
    waterfalls = [inputs for scenario, inputs, _ in calls if scenario == "waterfall"]
    existing = re.search(r"^  Shares: existing holders +([\d,]+) ", _report("pool", pool), re.MULTILINE)
    prompt, _ = _eval("bq")

    assert existing and waterfalls
    for waterfall in waterfalls:
        classes = waterfall["classes"]
        assert isinstance(classes, list)
        assert waterfall["common_shares"] == 7500000 != int(existing.group(1).replace(",", ""))
        assert f"{waterfall['common_shares']:,} are issued common" in prompt
        # The earlier Seed class is passed as its own class, junior to the new series.
        assert [(c["shares"], c["rank"]) for c in classes] == [(2714285, 1), (2000000, 2)]


def test_one_eval_passes_a_converting_safe_as_an_instrument_and_its_own_class() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-br-"))
    calls = _calls(path.read_text(encoding="utf-8"))
    (deal,) = (inputs for scenario, inputs, _ in calls if scenario == "deal_check")
    (waterfall,) = (inputs for scenario, inputs, _ in calls if scenario == "waterfall")
    prompt, _ = _eval("br")
    classes = waterfall["classes"]

    assert deal["instruments"] and isinstance(classes, list)
    assert "9,000,000 common, 1,428,571 SAFE preferred, 2,979,591 Series A preferred" in prompt
    assert waterfall["common_shares"] == 9000000
    assert {(c["shares"], c["invested"]) for c in classes} == {(2979591, "4000000"), (1428571, "1000000")}


def test_one_eval_keeps_an_objection_a_line_answers_only_in_part() -> None:
    prompt, answer = _eval("bm")
    _, kept = answer.split("Kept, answered only in part", 1)
    objected, answering = _DOUBLE_QUOTED.findall(kept)[:2]

    assert objected in prompt and answering in prompt and objected != answering
    assert "`[one specific achievement for each other founder, and their role]`" in kept
    assert "Dropped, answered by slide 6" not in answer
    assert "Its Fix cell says it is answered in part and quotes the slide 6 line with its place" in kept
    # The run that graded Partial batched the refute pass; the eval now says which form passes.
    assert "one subagent deciding several objections, even one at a time, does not pass" in answer
    assert "a pointer to the answer's Open asks does not pass" in answer
    assert "statement quoted word for word with its key" in answer
    assert "the Sources citations the skill prescribes are excepted" in answer


@pytest.mark.parametrize("letter", ["bp"])
def test_one_eval_drops_an_objection_by_quoting_the_founders_line(letter: str) -> None:
    prompt, answer = _eval(letter)
    _, dropped = answer.split("Dropped, answered", 1)
    answering, objected = _DOUBLE_QUOTED.findall(dropped)[:2]

    assert answering in prompt and objected in prompt and answering != objected


def test_the_fund_and_firm_eval_declines_both_and_names_no_firm() -> None:
    prompt, answer = _eval("bn")

    assert "$250 million" in prompt and "a famous fund's partners" in prompt
    assert "declines to write in any named or chosen fund's format" in answer
    assert "declines the fund math" in answer and "is not used anywhere" in answer
    assert not _names_a_person_or_firm(answer)
