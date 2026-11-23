"""The vc-market-sizing skill stays true to the calculator and keeps its shape: its ledger, flags, review and evals.

The JSON example must be a valid ``equity_market_sizing`` call, the ``equity_calculator`` command must run, and every
line of the output excerpt that follows it must be a line the command really prints, so no figure in the skill is
typed by hand. Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands
off to by name must be a folder in skills/. Every flag code has a row in the skill's flag table, with a tier. The
source kinds are fixed words with an order, and the shakiest assumption is picked from tool values. The adversarial
review keeps both stages: three lenses named by what they test (never by a person or firm) that do no arithmetic, a
refute pass with the fixed verdicts that invents nothing, and computed findings that skip both. Each eval in
evals/vc-market-sizing/ has a prompt, an expected tool call and an expected answer; an eval with an
``equity_market_sizing`` call carries a valid call and an excerpt that is lines of the report that call prints.
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
from equity_calculator.schemas.equity_market_sizing import MarketSizingFlag, MarketSizingInput
from equity_calculator.text import render_sheet
from tests.test_vc_claims_check_skill import _READ_SOURCES

# _READ_SOURCES is the one set of public frameworks the repository's skills have read in full (the vc-claims-check
# test holds it); this skill cites three of them, and marks everything else as its own judgment, unverified.
_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-market-sizing" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-market-sizing").glob("*.md"))
_EVAL_COUNT = 4
# The repository gives each made-up company its own letter; this skill's evals use AW to AZ.
_EVAL_LETTERS = ("aw", "ax", "ay", "az")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_market_sizing` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_HANDOFF_SKILLS = ("vc-claims-check", "vc-deck-review", "vc-positioning", "vc-deal-math", "equity-calculator")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "how big is our market",
    "size our market",
    "build our TAM SAM SOM",
    "is our TAM credible",
    "bottom-up or top-down",
)
_KINDS = ("Own data", "Named third party", "Estimate")
_LENSES = ("Inflation", "Path", "Overlap")
_REFUTE_VERDICTS = ("**Dropped, answered:**", "**Dropped, not grounded:**", "**Kept:**")
_TIERS = ("ends the meeting", "weakens it", "minor")
_SOURCES_USED = {
    "https://www.ycombinator.com/library/4b-how-to-pitch-your-company",
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
    "https://www.sequoiacap.com/article/writing-a-business-plan/",
}
# The short names of the sources this skill uses; every part of a Source cell starts with one, or is unverified.
_USED_NAMES = tuple(sorted(_READ_SOURCES[url] for url in _SOURCES_USED))
_UNVERIFIED = "unverified"
_URL = re.compile(r"https?://\S+")
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_SCORE = re.compile(r"/\s*10\b|out of 10\b|/\s*100\b|out of 100\b", re.IGNORECASE)
# A figure an eval's answer takes from the calculator: money with cents, a percent with decimals, a multiple with the
# six places the report prints, or a count with decimals.
_PRINTED_FIGURE = re.compile(
    r"\$-?\d[\d,]*\.\d{2}|-?\d[\d,]*\.\d+%|\d+\.\d{6}x|(?<![\d$,.\-])\d[\d,]*\.\d{2}(?![\d%x])"
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


def _report(call: str) -> str:
    return render_sheet(sheet_for(compute(MarketSizingInput.model_validate(json.loads(call)["inputs"]))))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-market-sizing"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "adversarial review", "Never looks up or invents a market figure", "Not investment"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert "equity_market_sizing" in named
    assert named <= served, named - served
    assert "equity_calculator market_sizing --segment" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-market-sizing skill" in _unwrapped(_section("## When to use it", _POSITIONING))


def test_the_json_example_is_a_valid_market_sizing_call() -> None:
    (example,) = _fences("json")

    assert MarketSizingInput.model_validate(json.loads(example)["inputs"]).scenario == "market_sizing"


async def test_the_command_runs_and_prints_every_line_of_the_excerpt() -> None:
    (command,) = _fences("")
    (excerpt,) = _fences("text")
    assert command.startswith(_PROGRAM) and "\n" not in command.strip()

    printed = [line.rstrip() for line in (await run(shlex.split(command)[1:])).splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_command_and_the_json_example_are_the_same_check() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        MarketSizingInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_the_example_always_sends_the_months_each_price_covers() -> None:
    (example,) = _fences("json")
    steps = _unwrapped(_section("## Steps"))

    for segment in json.loads(example)["inputs"]["segments"]:
        assert "price_period_months" in segment
    assert "Always send `price_period_months`" in steps and "`price_period_defaulted`" in steps


def test_every_flag_code_has_a_row_in_the_skills_flag_table_with_a_tier() -> None:
    rows = _table("## Flags")
    codes = [row[0].strip("`") for row in rows]

    assert codes == list(get_args(MarketSizingFlag))
    for row in rows:
        assert row[-1] in _TIERS, row[0]
    assert "this skill's own ranking (unverified)" in _unwrapped(_section("## Flags"))


def test_the_source_kinds_are_the_fixed_words_with_an_order() -> None:
    ledger = _unwrapped(_section("## The assumption ledger"))

    assert tuple(row[0] for row in _table("## The assumption ledger")) == _KINDS
    assert ", then ".join(f"**{kind}**" for kind in _KINDS) in ledger
    assert "never upgrades a row" in ledger and _UNVERIFIED in ledger


def test_the_shakiest_assumption_is_picked_from_tool_values() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "never a percentage the skill picks" in steps
    assert "the one with the largest `som_swing` in the result" in steps
    assert "a comparison of tool values, not a calculation" in steps
    assert "When no row of that kind has a sensitivity row, name none" in steps
    # The break-even against a top-down figure is the tool's cross-check, never a value to aim for.
    assert "never offer it as a price, a count or a share to aim for" in steps


def test_the_three_lenses_are_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    lenses = _lens_names()

    assert tuple(lenses) == _LENSES
    for lens in lenses:
        assert not _names_a_person_or_firm(lens), lens
    assert "quoted word for word" in attack and "do no arithmetic" in attack
    assert "one after another" in attack and "less independent than subagents" in attack
    assert "never the tool's result" in attack
    assert "you are not an investor and do not speak as one, named or not" in attack


def test_the_refute_pass_uses_the_fixed_verdicts() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "When you cannot decide, return Kept" in refute
    assert "invents nothing" in refute and "never answers an objection" in refute
    assert "Bring in no outside fact about the market, and do no arithmetic" in refute


def test_computed_findings_skip_the_review_and_survivors_have_tiers() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    ranked = _unwrapped(_section("### Rank what survives"))

    assert "Computed findings do not go through the lenses or the refute pass" in attack
    assert "A mismatch on a stated TAM, SAM or SOM leads the first tier" in attack
    for tier in _TIERS:
        assert f"**{tier}**" in ranked, tier
    assert "no percentages and no score" in ranked
    assert not _SCORE.search(_TEXT)


def test_every_pattern_has_a_read_source_or_says_unverified() -> None:
    rows = _table("### Patterns")

    assert rows and {row[1] for row in rows} == set(_LENSES)
    for row in rows:
        for part in row[-1].split("; "):
            assert part.startswith(_USED_NAMES) or _UNVERIFIED in part.lower(), row[0]
    (first,) = (row for row in rows if '"if we get 1% of it"' in row[0])
    assert first[1] == "Inflation" and "YC seven questions (2)" in first[-1]


def test_sources_are_a_subset_of_the_read_set() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == _SOURCES_USED
    assert listed <= set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert "Neither YC page carries a date" in _unwrapped(_section("## Sources"))


def test_limits_say_not_advice_and_no_lookups() -> None:
    limits = _unwrapped(_section("## Limits"))

    for phrase in (
        "Not investment, legal or tax advice",
        "never looks up",
        "no default price",
        'never works out "1% of" anything',
        "never suggests widening the market",
        "no fund or exit math",
        "never role-plays or speaks as a named investor, firm or author",
    ):
        assert phrase in limits, phrase


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
    assert len(_CALL_EVALS) == 2 and len(_NO_CALL_EVALS) == 2
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (call,) = _fences("json", text)
    (excerpt,) = _fences("text", text)

    printed = [line.rstrip() for line in _report(call).splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A money figure with cents, a percent, a multiple or a count with decimals in the answer is in the report."""
    text = path.read_text(encoding="utf-8")
    (call,) = _fences("json", text)
    report = _report(call)
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in report, figure


def test_eval_aw_leads_with_the_mismatch_and_quotes_the_break_even_values() -> None:
    prompt, answer = _eval("aw")
    slide = "A $120M TAM in US veterinary software."

    assert slide in prompt and slide in answer
    assert "the TAM mismatch leads the first tier" in answer
    assert "It works none of them out itself" in answer
    assert "**The shakiest assumption** is segment 1's 900 clinics" in answer
    assert "**Dropped, answered**" in answer and "is reported but is not a candidate" in answer
    assert "never offered as a price to aim for" in answer
    assert "`[the channel that reaches multi-site groups]`" in answer


def test_eval_ax_sets_the_deck_beside_the_gross_spend_and_keeps_the_overlap() -> None:
    prompt, answer = _eval("ax")
    overlap = "2,500,000 pools in Texas and Florida, our two biggest Sun Belt states"

    assert overlap in prompt and overlap in answer
    assert "Beside it, the tool's gross spend is $11,700,000,000.00" in answer
    assert "`segments_exceed_population` and `bottom_up_above_top_down` are in the first tier" in answer
    assert "no shakiest assumption is named" in answer and "`[a low and a high value for each 2%]`" in answer
    assert "brings in no fact about pools" in answer


def test_eval_ay_names_the_pattern_and_works_out_no_share() -> None:
    prompt, answer = _eval("ay")

    assert "we only need 1% of it" in prompt
    assert "a market size from an analyst figure only" in answer
    assert "not narrowing down the customer enough" in answer
    assert "It works out no share of the $50B" in answer
    assert "$500" not in answer and "500 million" not in answer.lower()


def test_eval_az_declines_a_named_firm_a_verdict_and_assumed_averages() -> None:
    prompt, answer = _eval("az")

    assert "a16z partner" in prompt and "industry-average price" in prompt
    assert "declines to speak as a partner of a named firm" in answer
    assert "no venture-scale threshold, no fund math" in answer
    assert "declines to assume an industry-average price or adoption rate, and looks none up" in answer
    assert "It computes nothing" in answer
