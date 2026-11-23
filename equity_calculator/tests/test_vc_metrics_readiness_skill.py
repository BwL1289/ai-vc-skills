"""The vc-metrics-readiness skill keeps its shape: its definitions, verdicts, patterns, flags, review, stages and evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The definitions table holds the fixed metrics, each computed by ``metrics_check`` or
quoted, each citing a source the repository has read or saying it is unverified. The four verdicts are
vc-claims-check's words in its order. The Flags table explains every flag the tool can raise, and benchmark figures
appear only through the tool's assumption rows. The adversarial review keeps both stages: lenses named by what they
test (never by a person or firm) that do no arithmetic, a refute pass that uses only the founder's material, and a
ranked fix list that puts the calculator's mismatches ahead of its tiers and gives no score. Each eval in
evals/vc-metrics-readiness/ has a prompt, an expected tool call and an expected answer; an eval with
``equity_metrics_check`` calls pairs each call with an excerpt that is lines of the report that call prints, and an
eval with a recorded run also carries its excerpt and verdict.
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
from equity_calculator.schemas.equity_metrics_check import MetricsCheckInput, MetricsCheckResult, MetricsFlag
from equity_calculator.text import render_sheet
from pydantic import ValidationError
from tests.test_vc_claims_check_skill import _READ_SOURCES as _SHARED_READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-metrics-readiness" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_CLAIMS_CHECK = (_ROOT / "skills" / "vc-claims-check" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-metrics-readiness").glob("*.md"))
_EVAL_COUNT = 5
# The repository gives each made-up company its own letter; this skill's evals use AM to AP and BT (sorted by file
# name, so BT comes last).
_EVAL_LETTERS = ("am", "an", "ao", "ap", "bt")
_NO_CALL = "## Expected tool call\n\nNone: no `equity_metrics_check` call."
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
    "vc-claims-check",
    "vc-deal-math",
    "vc-positioning",
    "equity-calculator",
    "vc-deck-review",
    "vc-market-sizing",
    "vc-round-sizing",
    "vc-current-investor-update",
    "vc-prospective-investor-update",
)
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "are my metrics ready",
    "check my ARR",
    "is this NRR right",
    "burn multiple",
    "CAC payback",
    "do my metrics match",
    "what metrics does a Series A fund expect",
)
# The public frameworks the repository has read in full: the shared seven, plus the four this skill's authors read in
# full for it (a16z's second metrics post, Sacks on the burn multiple, Skok on SaaS metrics, Bessemer on scaling).
_READ_SOURCES = {
    **_SHARED_READ_SOURCES,
    "https://a16z.com/16-more-startup-metrics/": 'a16z "16 More"',
    "https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200": "Sacks",
    "https://www.forentrepreneurs.com/saas-metrics-2/": "Skok",
    "https://www.bvp.com/atlas/scaling-to-100-million": "Bessemer",
}
_SOURCES_USED = {
    "https://a16z.com/16-startup-metrics/",
    "https://a16z.com/16-more-startup-metrics/",
    "https://sacks.substack.com/p/the-burn-multiple-51a7e43cb200",
    "https://www.forentrepreneurs.com/saas-metrics-2/",
    "https://www.bvp.com/atlas/scaling-to-100-million",
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising",
}
# The short names of the sources this skill uses; every part of a Source cell starts with one, or is unverified.
_USED_NAMES = tuple(sorted(_READ_SOURCES[url] for url in _SOURCES_USED))
_UNVERIFIED = "unverified"
_COMPUTED_METRICS = (
    "ARR",
    "Revenue run-rate",
    "Gross revenue retention",
    "Net revenue retention",
    "Gross revenue churn",
    "Net revenue churn",
    "Logo churn",
    "CAC",
    "CAC payback",
    "Burn multiple",
    "Customer concentration",
)
_VERDICTS = ("Contradicted", "Will be discounted", "Needs a source", "Supported")
_REFUTE_VERDICTS = ("**Dropped, answered:**", "**Dropped, not grounded:**", "**Kept:**")
_TIERS = ("**ends the meeting**", "**weakens it**", "**minor**")
_LENS_COUNT = 5
_BAND_FLAGS = ("payback_above_band", "burn_multiple_above_band", "net_revenue_churn_above_band")
_URL = re.compile(r"https?://\S+")
# Names a lens or a brief must never carry: the skill tests definitions, never people or firms.
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
    "bessemer",
    "sacks",
    "skok",
)
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_FIX_COLUMNS = re.compile(r"Rank, Tier, Where, Lens, The line \(quoted\), Why a partner reads it that way, Fix")
_SCORE = re.compile(r"/\s*10\b|out of 10\b|/\s*100\b|out of 100\b", re.IGNORECASE)
# The benchmark figures the tool's bands use; outside the founder's quoted phrasings they appear only in tool output.
_BENCHMARK_FIGURE = re.compile(r"(?<![\d.])(?:12 months|18 months|24 months|3x|2%)")
_STAGE_VALUE = re.compile(r"\d[\d.,]*\s*(?:%|x\b|months)")
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
# A figure an eval's answer takes from the calculator: a percent or months with decimals, money with cents, or a
# multiple with the six places the report prints.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$-?\d[\d,]*\.\d{2}|\d+\.\d{6}x")
# A recorded run's verdict line, in the shape the repository's recorded evals use.
_RECORDED = "## Recorded answer"
_VERDICT_LINE = re.compile(r"^\*\*(?:Pass|Partial|Fail)\b[^*]*\*\*", re.MULTILINE)


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


def _cites_only_used_sources(cell: str) -> bool:
    """Each ``; ``-separated part of a Source cell names a source this skill uses or says it is unverified."""
    return all(part.startswith(_USED_NAMES) or _UNVERIFIED in part.lower() for part in cell.split("; "))


def _eval(letter: str) -> tuple[str, str]:
    """The unwrapped prompt and expected answer of the eval for Company ``letter``."""
    (path,) = (path for path in _EVALS if path.name.startswith(f"company-{letter}-"))
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def _calls(path: Path) -> list[dict[str, object]]:
    return [json.loads(call)["inputs"] for call in _fences("json", path.read_text(encoding="utf-8"))]


def _result(inputs: dict[str, object]) -> MetricsCheckResult:
    result = compute(MetricsCheckInput.model_validate(inputs))
    assert isinstance(result, MetricsCheckResult)
    return result


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-metrics-readiness"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for phrase in (
        "founder",
        "metrics_check",
        "adversarial review",
        "No score",
        "no firm named as a fit",
        "Never invents",
    ):
        assert phrase in description, phrase
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_metrics_check", "equity_deal_check"} <= named
    assert named <= served, named - served
    assert "`equity_calculator metrics_check`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_to_it() -> None:
    handoff = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert f"the {name} skill" in handoff, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "the vc-metrics-readiness skill" in _unwrapped(_section("## When to use it", _POSITIONING))
    assert "Planned, not yet shipped" not in handoff


def test_the_definitions_table_has_the_fixed_metrics_each_computed_or_quoted_with_a_read_source() -> None:
    rows = _table("## Definitions")
    computed = tuple(row[0] for row in rows if row[3].startswith("Computed"))

    assert computed == _COMPUTED_METRICS
    for metric, _, _, how, source in rows:
        assert how.startswith(("Computed", "Quoted")), metric
        assert _cites_only_used_sources(source), metric
    assert "not checked: no tool computes this" in _unwrapped(_section("## Definitions"))
    assert "not checked: no tool computes this" in _unwrapped(_section("## Steps"))
    by_metric = {row[0]: row for row in rows}
    # Bessemer is cited for gross against net only; the tool's row marks the new-customer rule as its own judgment.
    nrr_source = by_metric["Net revenue retention"][4]
    assert nrr_source.startswith("Bessemer (gross against net)")
    assert "leaving new customers out, and counting them in as the mistake: ours, unverified" in nrr_source
    # The burn row points to step 4, which routes each runway to the tool that checks it.
    assert by_metric["Net and gross burn"][3] == "Quoted (runway: step 4)"


def test_the_verdicts_are_claims_checks_words_in_its_order() -> None:
    verdicts = _unwrapped(_section("## The four verdicts"))

    assert ", then ".join(f"**{verdict}**" for verdict in _VERDICTS) in verdicts
    assert "in vc-claims-check's words and order" in verdicts
    # An unlabelled churn is Contradicted only when every basis the tool checked is a mismatch.
    assert "for an unlabelled churn, a mismatch on every basis" in verdicts
    for verdict in _VERDICTS:
        assert f"**{verdict}**" in _section("## The four verdicts", _CLAIMS_CHECK), verdict


def test_the_pattern_table_rows_have_a_fix_and_a_read_source_or_say_unverified() -> None:
    rows = _table("## Definitional patterns")

    assert rows
    for pattern, why, fix, source in rows:
        assert why and fix, pattern
        assert _cites_only_used_sources(source), pattern
    assert "Signals, not rules" in _section("## Definitional patterns")


def test_the_flags_table_explains_every_flag_the_tool_raises() -> None:
    rows = _table("## Flags")
    flags = tuple(row[0].strip("`") for row in rows)

    assert flags == get_args(MetricsFlag)
    for flag, meaning, change in rows:
        assert meaning and change, flag
    for flag, _, change in (row for row in rows if row[0].strip("`") in _BAND_FLAGS):
        assert "the tool's assumption row, a benchmark, not a rule" in change, flag
    (payback,) = (row for row in rows if row[0] == "`payback_above_band`")
    # The tool raises it at the band itself, not only above it.
    assert "at or above" in payback[1]
    assert "never a figure from memory" in _unwrapped(_section("## Flags"))


def test_benchmarks_appear_only_as_the_tools_assumption_rows() -> None:
    # The founder's own phrasings in "When to use it" may hold figures ("Is our churn 2% or 3%?"); nothing else may.
    outside = _TEXT.replace(_section("## When to use it"), "")

    assert not _BENCHMARK_FIGURE.search(outside), _BENCHMARK_FIGURE.findall(outside)
    assert "Benchmarks appear only as the tool's assumption rows" in _unwrapped(_section("## Limits"))


def test_the_model_converts_nothing_and_the_calculator_does_every_ratio() -> None:
    steps = _unwrapped(_section("## Steps"))

    for rule in (
        "never convert",
        "The tool converts MRR to ARR; the model never does",
        # A live run trimmed the tool's digits and abbreviated money; the notation keeps every digit the report prints.
        "0.950000 is 95.0000%, 0.875000 is 87.5000%",
        "A multiple keeps its six decimals (7.500000x) and money its cents ($1,200,000.00), never abbreviated ($1.2M)",
        "customer counts and `period_months` as whole numbers, never strings",
        "a change of notation, not a calculation; never round it",
        "One call per document's version of the figures",
        "never prorate",
        "never compute, convert or round one",
    ):
        assert rule in steps, rule
    # An unlabelled churn's basis rows are one check: one consistent basis is enough.
    assert "the churn is a calculator mismatch only when no basis row is consistent" in steps
    assert "`cohort_rule`" in steps
    assert "Each code in the result's `flags` goes to the answer as a question a partner is likely to ask" in steps
    for rule in (
        # A stated ratio is checked over the period the document states for it, or not at all.
        "A stated retention or churn figure goes in a call whose `period_months` is the period the document states",
        "With no stated period, or no parts for that period, it is not passed",
        # Period-total retention is never offered as a slide figure in place of the starting customers' own.
        "the tool's retention values are not offered as replacement figures for a slide",
        # The tool checks blended CAC only, so a paid CAC never goes in as stated_cac.
        "`stated_cac` is checked against blended CAC only. A CAC the document labels paid is not passed",
        # A stated figure without its parts would make the tool refuse the whole call, so it is left out.
        "A stated figure whose parts the founder did not give is left out of the call",
        "A refusal that comes anyway is relayed with the parts it names",
        "gets no check row: it is not checked, and the flag (`burn_multiple_not_defined` or `no_net_burn`) says why",
        "With no recurring revenue at all, a stated burn multiple and its net burn are not passed",
        "make no call only when nothing is left to pass",
        "Net burn goes into a call only when that call's document states a burn multiple",
        # The report's fixed label is renamed to the call's document when a row is relayed.
        'name that call\'s document instead ("the model says", "the update says")',
        "relay the flag as answered and quote that line",
        # A live run set the deck's own multiple against the band the tool raised only for its computed one.
        "A benchmark flag is relayed for the tool value it was raised on only",
        "a stated figure is never set against the benchmark by eye",
    ):
        assert rule in steps, rule
    # Each figure goes to the tool or skill that checks it; growth rates and LTV have none.
    for rule in (
        "go to `equity_deal_check` as the vc-deal-math skill says",
        "A runway with no raise, a runway on a SAFE or note raise and that raise's use-of-funds lines go to "
        "`equity_runway_plan`",
        "as the vc-round-sizing skill calls it; with no cash or burn given, ask for them",
        "A market size goes to `equity_market_sizing` as the vc-market-sizing skill says",
        'Growth rates, LTV and every other metric the table marks quoted: quote as stated with "not checked: no tool '
        'computes this"',
    ):
        assert rule in steps, rule
    assert "No arithmetic outside the equity calculator's tools" in _unwrapped(_section("## Limits"))


def test_the_attack_stage_runs_independent_lenses_named_by_what_they_test() -> None:
    attack = _unwrapped(_section("### Stage A: attack"))
    brief = attack.split("Every lens gets the same brief", 1)[1].split("**How to run the lenses.**", 1)[0]
    lenses = _lens_names()

    assert len(lenses) == _LENS_COUNT
    for lens in lenses:
        assert not _names_a_person_or_firm(lens), lens
    assert not _names_a_person_or_firm(brief)
    assert "quoted word for word with its document and place" in attack
    assert "only the founder's material, the Definitions table and its lens brief" in attack
    # A subagent lens gets no other section, so the stage-fit lens is handed the table it tests against.
    assert "Stage fit" in lenses and "the Stage fit lens also gets the Stage expectations table" in attack
    # A missing metric has no line of its own, so the stage-fit lens anchors on the stage or the metrics slide.
    assert "quotes the line that states the stage, or the metrics slide as a whole" in attack
    assert "not the tool's output" in attack
    assert "one after another" in attack and "less independent than subagents" in attack
    assert "do no arithmetic" in brief
    assert "do not go through the lenses" in attack
    # A lens that sees the answering line must still raise the objection, or the refute pass has nothing to drop.
    assert "Do not judge whether another line of the material answers an objection: raise it anyway" in brief
    assert "Never turn an objection into a gap because another line may answer it" in brief
    assert "run the lenses as parallel subagents, however short the material" in attack
    assert "rather than a weak objection" not in attack


def test_without_a_subagent_tool_the_lenses_run_before_step_1_and_the_answer_says_so() -> None:
    steps = _unwrapped(_section("## Steps"))
    note = "Without a subagent tool, run Stage A of the adversarial review first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **List every metric word for word,**")
    assert "less independent than separate subagents" in _unwrapped(_section("## Answering"))
    # A live run had the Task tool and still ran the lenses in the main agent: Steps open with the subagent path.
    subagents = "With a subagent tool (the Agent or Task tool), run the five lenses as subagents (Stage A)"
    assert subagents in steps and steps.index(subagents) < steps.index(note)
    assert "the fallback below is only for a session without that tool" in steps


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in brief, verdict
    assert not _names_a_person_or_firm(brief)
    assert "one subagent per objection" in handoff
    assert "launch one subagent per objection in a single message" in handoff
    assert "never put two objections in one subagent, and never judge them in the main agent instead" in handoff
    # The refute pass is handed claims-check's pattern list, so the column must exist there under that name.
    assert "the Pattern column of this skill's pattern table and of vc-claims-check's discount table" in handoff
    assert "| Pattern" in _section("## Discount patterns", _CLAIMS_CHECK)
    for rule in (
        "you argue neither side",
        "Bring in no outside fact about the company, its market or its competitors",
        "do no arithmetic",
        "How a partner is likely to read a line is not an outside fact",
        "never answers an objection",
        "When you cannot decide, return Kept",
        "put the definition beside the figure",
        "invents nothing on the founder's behalf",
        "an answering line that is not in the material word for word does not drop the objection",
    ):
        assert rule in brief, rule
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_calculator_mismatches_lead_the_list_and_there_is_no_score() -> None:
    ranked = _unwrapped(_section("### The ranked fix list"))
    answering = _unwrapped(_section("## Answering"))

    for tier in _TIERS:
        assert tier in ranked, tier
    # The pack's one rule for a computed mismatch: ahead of the tiers, with no tier; an understated figure is minor.
    assert "The calculator's mismatches lead the list ahead of the tiers, with no tier" in ranked
    assert "except an understated figure, which is minor at most" in ranked
    attack = _unwrapped(_section("### Stage A: attack"))
    assert "added to the ranked fix list ahead of the tiers" in attack
    assert "It carries no tier: how much a gap hurts depends on its size, which the founder weighs" in attack
    # Which way flatters depends on the metric: a lower churn, CAC, payback or multiple flatters.
    assert (
        "A stated figure less flattering than the tool's value (an ARR or retention below it; a churn, CAC, payback, "
        "burn multiple or concentration above it) understates: it goes in the minor tier at most"
    ) in attack
    assert "`[how the model works this figure, unrounded]`" in attack
    assert "merges into that mismatch's entry and keeps the lens name" in _unwrapped(_section("### Check the quotes"))
    assert "no percentages and no score" in ranked
    assert "An unlabelled churn with one consistent basis row is not a mismatch" in _unwrapped(
        _section("### Stage A: attack")
    )
    assert answering.index("**The biggest fixes,**") < answering.index("**Ranked fix list,**")
    assert _FIX_COLUMNS.search(answering) and "**Dropped,**" in answering
    # A live run left out the lens results, relayed flags as statements, skipped `cohort_rule` and credited a source
    # the tool's row does not give.
    for rule in (
        'Then each lens with what it returned, "nothing found" included, and how many refute subagents ran',
        "each flag as the question a partner is likely to ask",
        "the source and date the tool's row gives, never a source from the Definitions table",
        "When no `cohort_*` fields were passed, name the `cohort_rule` row and its setting",
        "A Missing row carries its bracketed ask in the same row",
        "a metric whose parts were given is Missing with the fix: show it with the tool's values",
    ):
        assert rule in answering, rule
    assert not _SCORE.search(_TEXT)
    limits = _unwrapped(_section("## Limits"))
    assert 'no "ready" or "not ready"' in limits and 'no "raise now or wait"' in limits
    # Firms and authors are cited as sources; none is named as a fit or speaks.
    assert "never names a firm or person as an investor to approach or as one the metrics fit" in limits
    assert "names firms and authors only as cited sources" in limits
    assert "names a firm as a fit or a voice (firms and authors appear only as cited sources)" in _unwrapped(
        _section("## Steps")
    )


def test_stage_expectations_name_kinds_of_metric_never_values() -> None:
    rows = _table("## Stage expectations")
    section = _unwrapped(_section("## Stage expectations"))

    assert rows
    for stage, metrics, source in rows:
        assert not _STAGE_VALUE.search(metrics), stage
        assert _cites_only_used_sources(source), stage
    assert "this skill's own judgment, unverified" in section
    assert "rates no figure against a stage bar" in section and "without a threshold" in section


def test_sources_are_frameworks_the_repository_has_read() -> None:
    listed = set(_URL.findall(_section("## Sources")))

    assert listed == _SOURCES_USED
    assert listed <= set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert "this skill's own judgment, unverified" in _unwrapped(_section("## Sources"))


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    assert tuple(path.name.split("-")[1] for path in _EVALS) == _EVAL_LETTERS
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name
        if _RECORDED not in text:
            assert "has not been run in a live session" in text, path.name
            continue
        # A recorded run: the intro says so, the excerpt follows the expected answer, and it opens with its verdict
        # and what changed since.
        assert text.index(f"\n{_RECORDED}\n") > positions[-1], path.name
        assert '"Recorded answer" is an excerpt of a recorded run' in _unwrapped(text.split("\n## ", 1)[0]), path.name
        recorded = _section(_RECORDED, text)
        assert _VERDICT_LINE.search(recorded) and "Since this run" in _unwrapped(recorded), path.name
        assert _fences("json", recorded) == [] and _fences("text", recorded) == [], path.name


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls, excerpts = _calls(path), _fences("text", text)

    assert calls and len(calls) == len(excerpts)
    for call, excerpt in zip(calls, excerpts, strict=True):
        report = render_sheet(sheet_for(_result(call)))
        printed = [line.rstrip() for line in report.splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, line


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_every_flag_an_eval_call_raises_reaches_its_expected_answer(path: Path) -> None:
    """Step 4 relays each flag code as a question, so each one the calls raise is named in the expected answer."""
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    for call in _calls(path):
        for flag in _result(call).flags:
            assert f"`{flag}`" in answer, flag


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, months, money with cents or a multiple in the expected answer is a figure the report prints."""
    text = path.read_text(encoding="utf-8")
    reports = "\n".join(render_sheet(sheet_for(_result(call))) for call in _calls(path))
    figures = _PRINTED_FIGURE.findall(_unwrapped(_section("## Expected answer", text)))

    assert figures
    for figure in figures:
        assert figure in reports, figure


def test_one_eval_leads_with_three_mismatches_and_the_flag_that_explains_each() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-am-"))
    (call,) = _calls(path)
    result = _result(call)
    _, answer = _eval("am")

    assert [check.verdict for check in result.checks] == ["mismatch"] * 3
    for flag in ("stated_arr_matches_run_rate", "stated_nrr_includes_new", "stated_burn_multiple_uses_new_not_net_arr"):
        assert flag in result.flags and f"`{flag}`" in answer, flag
    assert "lead the ranked fix list ahead of the tiers, with no tier" in answer
    assert "All three metrics are Contradicted" in answer
    # Twelve months with no starting-customer movements: the cohort rule applies and the answer asks for them.
    assert "`cohort_rule`" in answer and "alone]`" in answer
    assert "a benchmark, not a rule" in answer and "No score" in answer
    # The live run is recorded: the lenses ran in the main agent, so one clause of the pass sentence was missed.
    assert "the deck's 6.25x is never set against the benchmark" in answer and "has a Lens column" in answer
    assert "runs the five lenses as subagents" in _unwrapped(path.read_text(encoding="utf-8").split("\n## ", 1)[0])
    assert "**Partial: one clause missed.**" in _section(_RECORDED, path.read_text(encoding="utf-8"))


def test_a_three_document_eval_runs_one_call_per_document_with_only_its_figures() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-an-"))
    deck, model, update = _calls(path)
    stated = [{key for key in call if key.startswith("stated_")} for call in (deck, model, update)]
    parts = [
        {key: value for key, value in call.items() if not key.startswith("stated_")} for call in (deck, model, update)
    ]

    assert stated == [
        {"stated_churn_percent", "stated_cac_payback_months"},
        {"stated_cac_payback_months"},
        {"stated_churn_percent", "stated_churn_basis"},
    ]
    assert parts[0] == parts[1] == parts[2]
    # The deck's unlabelled churn holds on one basis only, so it is not a calculator mismatch.
    churn = [check for check in _result(deck).checks if check.key == "churn"]
    assert [check.verdict for check in churn].count("consistent") == 1
    _, answer = _eval("an")
    assert "is not a calculator mismatch, because one basis row is consistent" in answer
    assert "Will be discounted" in answer and "CAC payback is Contradicted" in answer
    assert '"the model says" and "the update says"' in answer
    assert "`[the stage of this raise and the business model]`" in answer


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    prompt, answer = _eval("an")
    objection, dropped = answer.split("Dropped, answered", 1)
    # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
    # founder's material, not the line the objection was about.
    answering_line = _DOUBLE_QUOTED.findall(dropped)[0]

    assert answering_line in prompt
    assert answering_line not in _DOUBLE_QUOTED.findall(objection)
    assert "put that definition beside the figure" in answer


def test_one_eval_makes_no_call_for_a_marketplace_and_computes_no_take() -> None:
    prompt, answer = _eval("ao")

    assert "marketplace" in prompt and "we take 12%" in prompt
    assert "computes nothing" in answer and "not the 12% take" in answer and "no annual figure" in answer
    assert "Needs a source" in answer


def test_one_eval_declines_a_score_a_verdict_and_a_named_firm() -> None:
    prompt, answer = _eval("ap")

    assert "Score our metrics out of 10" in prompt and "yes or no" in prompt
    assert "no score" in answer and "no yes or no" in answer
    assert "does not speak as or for a named firm" in answer
    assert "the ratio does not compute" in answer


def test_one_eval_takes_the_edge_paths_cohort_movements_no_multiple_and_a_left_out_figure() -> None:
    (path,) = (path for path in _CALL_EVALS if path.name.startswith("company-bt-"))
    (call,) = _calls(path)
    result = _result(call)
    _, answer = _eval("bt")

    # The starting customers' own movements go in, so the cohort rule names them.
    assert {"cohort_expansion_recurring", "cohort_contraction_recurring", "cohort_churned_recurring"} <= set(call)
    (cohort,) = (row for row in result.assumptions if row.key == "cohort_rule")
    assert cohort.setting == "the starting customers' own movements"
    # A stated multiple with net new ARR below zero gets no check row and the flag that says why.
    assert "stated_burn_multiple" in call and "burn_multiple_not_defined" in result.flags
    assert all(check.key != "burn_multiple" for check in result.checks)
    # An unlabelled churn that holds on no basis is a calculator mismatch.
    churn = [check.verdict for check in result.checks if check.key == "churn"]
    assert len(churn) == 3 and set(churn) == {"mismatch"} and result.verdict == "mismatch"
    assert "Contradicted" in answer and "with no tier" in answer
    # The payback was left out: with it, the tool refuses the whole call.
    assert "stated_cac_payback_months" not in call
    with pytest.raises(ValidationError, match="stated_cac_payback_months needs"):
        MetricsCheckInput.model_validate({**call, "stated_cac_payback_months": "8"})
    assert "left out of the call" in answer
