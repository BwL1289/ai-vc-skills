"""The vc-term-sheet-review skill keeps its shape: its terms table, marks, calculator rules, review and evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The terms table is a fixed list of rows, each worked by a served tool, "not modelled" or
"none (text)", and each citing a source the skill lists. The four marks are facts about two texts, never a verdict,
and no sentence says whether to sign. The waterfall takes only exit values the sheet, the tool or the founder gave.
The adversarial review keeps both stages: lenses named by what they test (never by a person or firm) that run after
the calculator and before the marks, and a refute pass in which a line that differs from the baseline never answers an
objection. The Sources are exactly the pages read in full for this skill, with no survey figure. Each eval in
evals/vc-term-sheet-review/ has a prompt, its expected calls and an expected answer; each call is valid and its excerpt
is lines of the report that call prints, and every figure an answer takes from the calculator is one it printed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
from equity_calculator.__main__ import _INPUT_MODELS
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.text import render_sheet
from pydantic import ValidationError

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-term-sheet-review" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-term-sheet-review").glob("*.md"))
_EVAL_COUNT = 5
# The repository gives each made-up company its own letter; this skill's evals use AQ to AU.
_EVAL_LETTERS = ("aq", "ar", "as", "at", "au")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` or `equity_waterfall` call."
_CALL_EVALS = [path for path in _EVALS if _NO_CALL not in path.read_text(encoding="utf-8")]
_NO_CALL_EVALS = [path for path in _EVALS if path not in _CALL_EVALS]
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_CALL_HEADING = re.compile(r"^### Call (\d+): `(equity_[a-z_]+)`", re.MULTILINE)
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_SERVED = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator", "vc-positioning", "vc-claims-check", "vc-deck-review")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "review my term sheet",
    "what does this term mean",
    "is this term sheet standard",
    "what do I get at a low exit",
    "what is the liquidation preference doing",
)
_TERMS = (
    "Amount and valuation",
    "Option pool",
    "Liquidation preference",
    "Participation",
    "Seniority",
    "Dividends",
    "Conversion",
    "Anti-dilution",
    "Protective provisions",
    "Board",
    "Operational approvals",
    "Drag-along",
    "Founder vesting",
    "Pro rata, first refusal, co-sale, information, registration rights",
    "Redemption",
    "Pay-to-play",
    "Warrants",
    "No-shop and conditions",
)
_NOT_MODELLED_TERMS = ("Dividends", "Anti-dilution", "Redemption", "Pay-to-play", "Warrants")
_NOT_MODELLED = "not modelled"
_TEXT_ONLY = "none (text)"
_NOT_MODELLED_STRING = "not modelled: no tool computes this term's effect"
_NOT_RUN = "not run: the waterfall needs whole share counts; send the pro forma cap table"
_NOT_SPLIT = "not checked: no tool splits the common payout by holder"
_MARKS = ("Matches", "Differs", "Not in the baseline", "Missing")
_REFUTE_VERDICTS = ("Dropped, answered:", "Dropped, not grounded:", "Kept:")
_TIERS = (
    "**a later deal is likely to stall on it**",
    "**a later deal is likely to ask about it**",
    "**minor**",
)
_MIN_LENSES = 4
# Words that would turn a mark or a tier into a verdict on the sheet; "do not sign" is allowed only as a prohibition.
_VERDICT_WORDS = ("sign it", "don't sign", "off-market", "market standard", "negotiable")
_ALLOWED_DO_NOT_SIGN = 'no "do not sign"'
# The sources read in full for this skill. The YC pages are cited undated: the date YC's library shows is an import
# stamp, not the article's date.
_READ_SOURCES = {
    "https://www.ycombinator.com/library/4P-a-standard-and-clean-series-a-term-sheet": "YC article",
    "https://www.ycombinator.com/series_a_term_sheet": "YC template",
    "https://feld.com/archives/2005/01/term-sheet-price/": "Price",
    "https://feld.com/archives/2005/01/term-sheet-liquidation-preference/": "Liquidation Preference",
    "https://feld.com/archives/2005/01/term-sheet-board-of-directors/": "Board of Directors",
    "https://feld.com/archives/2005/01/term-sheet-protective-provisions/": "Protective Provisions",
    "https://feld.com/archives/2005/02/term-sheet-drag-along/": "Drag Along",
    "https://feld.com/archives/2005/03/term-sheet-anti-dilution/": "Anti-Dilution",
    "https://feld.com/archives/2005/03/term-sheet-pay-to-play/": "Pay-to-Play",
    "https://feld.com/archives/2005/03/term-sheet-redemption-rights/": "Redemption Rights",
    "https://feld.com/archives/2005/03/term-sheet-dividends/": "Dividends",
    "https://feld.com/archives/2005/04/term-sheet-conversion/": "Conversion",
    "https://feld.com/archives/2005/04/term-sheet-conditions-precedent-to-financing/": "Conditions Precedent",
    "https://feld.com/archives/2005/05/term-sheet-vesting/": "Vesting",
    "https://feld.com/archives/2005/06/term-sheet-right-of-first-refusal/": "Right of First Refusal",
    "https://www.cooley.com/news/insight/2026/2026-08-17-q2-2026-venture-financing-report": "Cooley",
}
_YC_SOURCES = ("YC template", "YC article")
_FELD_SOURCE = re.compile(r'^Feld "([^"]+)"$')
_URL = re.compile(r"https?://\S+")
_PERCENT = re.compile(r"\d+(\.\d+)?%")
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = (
    "sequoia",
    "a16z",
    "andreessen",
    "y combinator",
    "yc",
    "graham",
    "dixon",
    "stebbings",
    "20vc",
    "benchmark",
    "feld",
    "mendelson",
    "cooley",
)
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
# A figure an eval's answer takes from the calculator: money with cents, or a percent with four decimals.
_PRINTED_FIGURE = re.compile(r"\$\d[\d,]*\.\d{2}|-?\d+\.\d{4}%")


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


def _eval(letter: str) -> tuple[str, str, str]:
    """The text, the unwrapped prompt and the unwrapped expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return text, _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def _calls(text: str) -> list[tuple[str, dict[str, Any], list[str]]]:
    """Each ``### Call N`` of an eval: its tool, its ``inputs`` and the excerpt lines under it, in order."""
    block = _section("## Expected tool call", text)
    heads = list(_CALL_HEADING.finditer(block))
    calls = []
    for number, head in enumerate(heads, start=1):
        assert int(head.group(1)) == number, head.group(0)
        end = heads[number].start() if number < len(heads) else len(block)
        body = block[head.end() : end]
        (call,) = _fences("json", body)
        (excerpt,) = _fences("text", body)
        calls.append((head.group(2), json.loads(call)["inputs"], excerpt.splitlines()))
    return calls


def _report(tool: str, inputs: dict[str, Any]) -> list[str]:
    model = _INPUT_MODELS[tool.removeprefix(_TOOL_PREFIX)]
    return [line.rstrip() for line in render_sheet(sheet_for(compute(model.model_validate(inputs)))).splitlines()]


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-term-sheet-review"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in ("founder", "lawyer", "adversarial review", "Never says whether to sign", "Not legal, tax"):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_pool", "equity_waterfall", "equity_dilution", "equity_vesting"} <= named
    assert named <= _SERVED, named - _SERVED
    assert "`equity_calculator deal_check`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-term-sheet-review skill" in _unwrapped(_section("## When to use it", _POSITIONING))
    # A verdict request is answered with the review, never with a verdict.
    assert '"Should we take this term sheet?": run the review' in handoffs


def test_the_terms_table_rows_are_fixed_and_each_cites_a_listed_source() -> None:
    rows = _table("## The terms")
    sources = _unwrapped(_section("## Sources"))

    assert tuple(row[0] for row in rows) == _TERMS
    for term, _, _, worked_by, source in rows:
        if worked_by not in (_NOT_MODELLED, _TEXT_ONLY):
            assert worked_by.startswith("`equity_"), term
            assert set(_TOOL_NAME.findall(worked_by)) <= _SERVED, term
        for part in source.split("; "):
            feld = _FELD_SOURCE.match(part)
            assert part.startswith(_YC_SOURCES) or feld is not None, (term, part)
            if feld is not None:
                assert feld.group(1) in sources, (term, part)
    assert tuple(row[0] for row in rows if row[3] == _NOT_MODELLED) == _NOT_MODELLED_TERMS
    # No survey figure reaches the table, and the template's money amounts and rates are left out.
    for row in rows:
        assert not _PERCENT.search(" ".join(row)), row[0]
    assert "no figure from a market survey appears in the answer" in _unwrapped(_section("## The terms"))


def test_the_marks_are_four_and_none_is_a_verdict() -> None:
    marks = _unwrapped(_section("## The baseline and the marks"))
    lowered = _TEXT.lower()

    for mark in _MARKS:
        assert f"**{mark}:**" in marks, mark
    assert "never a verdict on the term" in marks
    assert "It is a Series A sheet: say so when the round is a seed round" in marks
    # Silence is Missing only on a whole sheet; a term a partial paste leaves out is an open ask, not a mark.
    assert "**Missing:** the founder has said the text is the whole sheet, the baseline has the term" in marks
    assert 'leaves out gets no mark: it goes to the open asks as "not in what was pasted"' in marks
    assert "Founder vesting, which the baseline leaves blank to negotiate, is Differs when the sheet fills it" in marks
    # The baseline cells are this skill's summary of the template, never presented as a quotation.
    assert "it is not a quotation, and the answer never presents it as one" in marks
    assert "Baseline (YC template, this skill's summary)" in _unwrapped(_section("## Answering"))
    assert "Baseline (quoted)" not in _TEXT
    for word in _VERDICT_WORDS:
        assert word not in lowered, word
    assert lowered.count("do not sign") == lowered.count(_ALLOWED_DO_NOT_SIGN) == 1


def test_the_round_goes_to_the_calculator_on_the_tools_own_basis() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "call twice, once as `pre_money` and once as `post_money`" in steps
    # The calculator's fully diluted count leaves SAFEs and notes out; the founder's cap table may not.
    assert "SAFEs and notes excluded" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "`equity_pool`, only when no SAFE or note converts" in steps and "`whole_shares`" in steps
    assert "passed on, never subtracted by hand" in steps
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps
    # A later round goes to equity_dilution, from deal_check's figure and the founder's own round.
    assert "`equity_dilution`, only when the founder asks" in steps
    assert "`holder_percent` is `equity_deal_check`'s `holder_ownership_after`" in steps
    assert "are the founder's own figures for that round, never assumed" in steps
    assert "`equity_vesting`, only when the founder asks" in steps
    # equity_pool returns the deal and a what-if; only the table matching the sheet's pool timing feeds the waterfall.
    assert "the same `pool_timing` as `equity_deal_check`" in steps
    assert "take the whole share counts the waterfall needs from that table's `rows` only" in steps
    assert "It holds the pre-money fixed, so its price and post-money are not the sheet's" in steps
    # Acceleration needs the sale month, and a double trigger the termination month too, both as the founder names them.
    for rule in (
        "`acceleration_base` `grant`",
        "With acceleration, also `change_of_control_month`",
        "for a double trigger, also `termination_month`",
        "without which the acceleration never fires",
        "A month the founder has not named is never picked",
        "leave `termination_month` out and say the double trigger does not fire",
        "Credit for time served has no tool input",
        "never shift a month by hand",
    ):
        assert rule in steps, rule


def test_the_waterfall_rules_name_no_computed_exit() -> None:
    steps = _unwrapped(_section("## Steps"))

    for rule in (
        "Never an exit value you worked out",
        "`share_rounding`",
        "pro forma",
        _NOT_RUN,
        _NOT_SPLIT,
        "`preference_multiple` 1 and `participation` `none`",
        "The unissued pool takes nothing",
        "Never add or subtract shares yourself",
        "Run no other what-if unless the founder asks",
        # The existing_holders row holds earlier preferred shares too, so it never stands in for common beside them.
        "and no earlier preferred class",
        "or the earlier class is counted twice",
        "table that matches the sheet's pool timing",
        # No pool target means no equity_pool call, so no tool gives the new series' whole share count.
        "when the sheet sets no pool target, `equity_pool` does not run",
        "never divide the amount by the price yourself",
    ):
        assert rule in steps, rule
    assert "Compute no difference between columns" in _unwrapped(_section("## Answering"))


def test_the_not_modelled_string_is_fixed_and_limits_name_the_same_terms() -> None:
    steps = _unwrapped(_section("## Steps"))
    limits = _unwrapped(_section("## Limits"))

    assert f'"{_NOT_MODELLED_STRING}"' in steps
    assert "Never fold one into another input" in steps
    for term in ("cumulative dividends", "anti-dilution", "redemption", "pay-to-play", "warrants"):
        assert term in steps.lower() and term in limits.lower(), term


def test_the_lawyer_questions_ask_and_never_propose_a_trade() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "it never recommends and never proposes a trade" in steps
    assert '"What does the 2x participating preference pay common at our low exit?" is a question' in steps
    assert "grouped as Economics, Control and Process" in steps


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    steps = _unwrapped(_section("## Steps"))
    lenses = _lens_names()

    assert len(lenses) >= _MIN_LENSES
    for lens in lenses:
        assert not _names_a_person_or_firm(lens), lens
    for rule in (
        "quoted word for word with its heading",
        "do no arithmetic",
        "Say nothing about whether to sign",
        "the calculator's printed output",
        "not the marks",
        "less independent than subagents",
        "do not go through the lenses",
    ):
        assert rule in attack, rule
    # A lens that sees the answering line must still raise the objection, or the refute pass has nothing to drop.
    assert "Do not judge whether another line of the sheet answers an objection: raise it anyway" in attack
    assert "rather than a weak objection" not in attack
    # The lenses need the tool output, so they run after the calculator steps and before any mark exists.
    assert "after step 5 and before step 2 (no mark exists yet)" in attack
    order = "take the steps in this order: 1, 3, 4, 5, then Stage A of the adversarial review"
    assert order in steps and steps.index(order) < steps.index("1. **Quote the sheet.**")


def test_the_refute_stage_has_the_shared_verdicts() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in brief, verdict
    assert "one subagent per objection" in handoff and "the baseline column of the terms table" in handoff
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "do no arithmetic",
        "is not an outside fact",
        "A line that differs from the baseline never answers an objection",
        "When you cannot decide, return Kept",
        "a line of the sheet other than the objected line supplies the specific thing the objection says is missing",
        "The refute pass invents nothing",
        "or that is the objected line itself, does not drop the objection",
    ):
        assert rule in brief, rule
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_tiers_never_read_as_a_verdict() -> None:
    ranked = _unwrapped(_section("### Rank what survives"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    assert "never a recommendation" in ranked and "no percentages, no score" in ranked
    assert "The calculator's mismatches lead the first tier" in ranked
    assert "less independent than separate subagents" in answering
    assert "not legal, tax or investment advice" in answering
    assert "have a lawyer who works on startup and venture financings review the sheet" in answering


def test_sources_are_the_read_set_and_no_survey_figure_appears() -> None:
    sources = _section("## Sources")
    listed = set(_URL.findall(sources))

    assert listed == set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert not _PERCENT.search(sources)
    # The date YC's library shows for the article is an import stamp; the YC pages are cited undated.
    assert "2020" not in _TEXT
    assert "this skill's own, unverified" in _unwrapped(sources)
    assert "Never quote a share of deals that use a term" in _unwrapped(_section("## The terms"))


def test_there_is_one_eval_per_worked_company_and_each_has_its_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text and "has not been run in a live session" in text, path.name


def test_the_no_call_eval_carries_no_call_or_excerpt() -> None:
    assert [path.name.split("-")[1] for path in _NO_CALL_EVALS] == ["as"]
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name
        assert not _CALL_HEADING.search(text), path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls = _calls(text)

    assert calls and len(calls) == len(_fences("json", text)) == len(_fences("text", text))
    for tool, inputs, excerpt in calls:
        assert tool in _SERVED, tool
        printed = _report(tool, inputs)
        for line in excerpt:
            assert line in printed, (tool, line)


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_answer_takes_from_the_calculator_is_printed(path: Path) -> None:
    """Money with cents or a four-decimal percent in the expected answer is in that eval's reports.

    Shorthand exits such as "$8M" are the founder's own words and are not matched.
    """
    text = path.read_text(encoding="utf-8")
    reports = "\n".join("\n".join(_report(tool, inputs)) for tool, inputs, _ in _calls(text))
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in reports, figure


def test_one_eval_runs_the_baseline_beside_the_sheet() -> None:
    text, _, answer = _eval("ar")
    waterfalls = [inputs for tool, inputs, _ in _calls(text) if tool == "equity_waterfall"]
    baseline = {"preference_multiple": "1", "participation": "none"}

    assert waterfalls and len(waterfalls) % 2 == 0
    for sheet, base in zip(waterfalls[::2], waterfalls[1::2], strict=True):
        assert sheet["exit_amount"] == base["exit_amount"] and sheet["common_shares"] == base["common_shares"]
        (sheet_class,) = sheet["classes"]
        (base_class,) = base["classes"]
        assert {key: base_class[key] for key in baseline} == baseline
        sheet_rest = {key: value for key, value in sheet_class.items() if key not in baseline}
        base_rest = {key: value for key, value in base_class.items() if key not in baseline}
        assert sheet_rest == base_rest and sheet_class != base_class
    assert _NOT_MODELLED_STRING in answer and "not folded into the 2x" in answer
    assert "the calculator gives 65.0000%" in answer and "It leads the first tier" in answer
    assert "What does the 2x participating preference pay common at our low exit?" in answer


def test_one_eval_passes_the_founders_stake_to_the_dilution_tool() -> None:
    text, prompt, answer = _eval("aq")
    calls = _calls(text)
    (deal,) = (excerpt for tool, _, excerpt in calls if tool == "equity_deal_check")
    (dilution,) = (inputs for tool, inputs, _ in calls if tool == "equity_dilution")
    (after,) = (line for line in deal if line.strip().startswith("After: holder group"))

    # The founders' percent after the round is passed on as the report prints it, digit for digit.
    assert after.split()[-2] == f"{dilution['holder_percent']}%"
    assert "sells 20% with a 5% pool" in prompt
    assert dilution["rounds"] == [{"investor_percent": "20", "pool_percent": "5"}]
    assert "52.5000%" in answer and "No baseline column" in answer
    # The founder did not say the paste is the whole sheet, so nothing is Missing; the rest is an open ask.
    assert "no term is marked Missing" in answer and "not in what was pasted" in answer
    assert "$42,666,665.60" in answer and "pre-money held fixed" in answer


def test_a_partial_paste_marks_nothing_missing() -> None:
    for letter in ("ar", "at"):
        _, _, answer = _eval(letter)
        assert "no term is marked Missing" in answer, letter
        assert "Differs on the label" in answer, letter


def test_one_eval_stacks_an_earlier_preferred_class_and_runs_vesting() -> None:
    text, prompt, answer = _eval("au")
    calls = _calls(text)
    (deal,) = (inputs for tool, inputs, _ in calls if tool == "equity_deal_check")
    ((pool, pool_excerpt),) = ((inputs, excerpt) for tool, inputs, excerpt in calls if tool == "equity_pool")
    waterfalls = [inputs for tool, inputs, _ in calls if tool == "equity_waterfall"]
    (vesting,) = (inputs for tool, inputs, _ in calls if tool == "equity_vesting")
    (existing,) = (line for line in pool_excerpt if line.strip().startswith("Shares: existing holders"))
    (investor,) = (line for line in pool_excerpt if line.strip().startswith("Shares: investor"))
    (header,) = (line for line in pool_excerpt if line.strip().startswith("Line"))

    # The deal's pool timing is the table the shares come from, and the report marks that table as the deal.
    assert pool["pool_timing"] == deal.get("pool_timing", "pre_money") == "pre_money"
    assert "Pool in pre-money (this deal)" in header
    deal_investor_shares = int(investor.split()[2].replace(",", ""))
    existing_holders = int(existing.split()[3].replace(",", ""))
    assert len(waterfalls) == 4
    for waterfall in waterfalls:
        # Common is the founders' own count, never the existing_holders row, which holds the seed preferred too.
        assert waterfall["common_shares"] == deal["holder_shares"] != existing_holders
        series_a, seed = waterfall["classes"]
        assert (series_a["rank"], seed["rank"]) == (1, 2)
        assert series_a["shares"] == deal_investor_shares
        assert waterfall["common_shares"] + seed["shares"] == existing_holders
    # A double trigger fires only with the termination month; without the sale month the tool refuses the call.
    assert vesting["acceleration"] == "double_trigger"
    assert {"change_of_control_month", "termination_month"} <= set(vesting)
    vesting_model = _INPUT_MODELS["vesting"]
    without_sale = {key: value for key, value in vesting.items() if key != "change_of_control_month"}
    with pytest.raises(ValidationError, match="change_of_control_month"):
        vesting_model.model_validate(without_sale)
    without_termination = {key: value for key, value in vesting.items() if key != "termination_month"}
    assert compute(vesting_model.model_validate(without_termination)).model_dump()["acceleration_fired"] is False
    assert compute(vesting_model.model_validate(vesting)).model_dump()["acceleration_fired"] is True
    assert "the whole Series A term sheet" in prompt and "nothing is left out" in prompt
    assert "are Missing, each a lawyer question" in answer and "count the seed class twice" in answer


def test_one_eval_declines_the_verdict_and_the_named_firm() -> None:
    _, prompt, answer = _eval("as")

    assert "should I sign this?" in prompt and "partner at Benchmark" in prompt
    assert "whether to sign is the founder's decision with their lawyer" in answer
    assert "does not speak as a partner of a named firm" in answer
    assert "does not guess what another investor would offer" in answer


def test_one_eval_runs_no_waterfall_without_whole_shares() -> None:
    text, _, answer = _eval("at")
    tools = [tool for tool, _, _ in _calls(text)]

    assert tools == ["equity_deal_check"]
    assert f'"{_NOT_RUN}"' in answer and "is not estimated" in answer
    assert "fully diluted shares leave the SAFEs out" in answer
    assert "55.4167%" in answer
