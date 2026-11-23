"""The vc-claims-check skill keeps its shape: its classes, its verdicts, its discount table, its review and its evals.

Every calculator tool the skill names must be a tool the MCP server serves, and every skill it hands off to by name
must be a folder in skills/. The six classes and four verdicts are fixed words, with an order for a claim that earns
two verdicts. Each discount pattern names a source the skill lists, or says it is unverified. The consistency check
compares figures as stated and sends deal terms to the calculator, one call per document's version of the ask. The
adversarial review keeps both passes: a skeptic that quotes the founder word for word and reads only their material,
and a refute pass that keeps an attack only when that material grounds it. Each eval in evals/vc-claims-check/ has a
prompt, an expected tool call and an expected answer; an eval with ``equity_deal_check`` calls pairs each call with an
excerpt that is lines of the report that call prints.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest
from equity_calculator.__main__ import _INPUT_MODELS
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity_deal_check import DealCheckInput
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-claims-check" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-claims-check").glob("*.md"))
_EVAL_COUNT = 3
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
_HANDOFF_SKILLS = ("vc-deal-math", "equity-calculator", "vc-positioning", "vc-metrics-readiness", "vc-market-sizing")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "check my claims",
    "fact-check my deck",
    "will a VC believe this",
    "do my numbers agree",
    "what will a partner check first",
)
_PATTERNS = ("no competitors", "top-down-only", "advisors as decoration", "AI bolted on", "GMV called revenue")
_CLASSES = ("Figure", "Market size", "Customer or partner", "Team credential", "Competition", "Technology claim")
_VERDICTS = ("Contradicted", "Will be discounted", "Needs a source", "Supported")
_REFUTE_VERDICTS = ("Kept, grounded:", "Dropped, answered:", "Dropped, not grounded:")
# The public frameworks this skill's authors read; any other source is marked unverified.
_READ_SOURCES = {
    "https://www.ycombinator.com/library/4b-how-to-pitch-your-company": "YC seven questions",
    "https://www.ycombinator.com/howtoapply": 'YC "How to Apply"',
    "https://www.ycombinator.com/library/2u-how-to-build-your-seed-round-pitch-deck": "YC seed deck guide",
    "https://www.ycombinator.com/library/4A-a-guide-to-seed-fundraising": "YC seed fundraising guide",
    "https://www.sequoiacap.com/article/writing-a-business-plan/": "Sequoia",
    "https://a16z.com/16-startup-metrics/": 'a16z "16 Startup Metrics"',
    "https://cdixon.org/2013/08/04/the-idea-maze": 'Dixon "The idea maze"',
}
_UNVERIFIED = "Unverified"
_URL = re.compile(r"https?://\S+")
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_CLAIMS_COLUMNS = re.compile(
    r"#, Claim \(quoted\), Where, Class, Evidence the founder can show, Agrees across the materials\?,\s+Verdict, Fix"
)
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')


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


def _table(heading: str) -> list[list[str]]:
    """The body rows of the first Markdown table under ``heading``, each as its stripped cells."""
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(_section(heading))]
    return rows[2:]


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-claims-check"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for pattern in _PATTERNS:
        assert pattern in description, pattern
    for verdict in _VERDICTS:
        assert verdict.lower() in description, verdict
    assert "founder" in description and "adversarial review" in description
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_tool_the_skill_names_is_a_tool_the_server_serves() -> None:
    served = {f"{_TOOL_PREFIX}{scenario}" for scenario in _INPUT_MODELS} | {_WORKBOOK_TOOL}
    named = set(_TOOL_NAME.findall(_TEXT))

    assert {"equity_deal_check", "equity_round"} <= named
    assert named <= served, named - served
    assert "`equity_calculator deal_check`" in _TEXT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_back() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "vc-claims-check" in _section("## When to use it", _POSITIONING)


def test_the_classes_and_verdicts_are_the_fixed_words_with_an_order() -> None:
    classes = [row[0] for row in _table("## The six classes")]
    verdicts = [row[0] for row in _table("## The four verdicts")]
    order = _unwrapped(_section("## The four verdicts"))

    assert classes == list(_CLASSES)
    assert verdicts == list(_VERDICTS)
    assert ", then ".join(f"**{verdict}**" for verdict in _VERDICTS) in order
    assert "does not see or verify that evidence" in order


def test_every_discount_pattern_has_a_class_a_fix_and_a_read_source_or_says_unverified() -> None:
    rows = _table("## Discount patterns")
    sources_list = _section("## Sources")
    listed = set(_URL.findall(sources_list))
    names = tuple(_READ_SOURCES.values())

    assert listed == set(_READ_SOURCES)
    assert set(_URL.findall(_TEXT)) == listed
    assert len(rows) >= len(_PATTERNS)
    for pattern, kind, _, fix, source in rows:
        assert kind in _CLASSES, pattern
        assert fix, pattern
        assert source.startswith(names) or source == _UNVERIFIED, pattern
        if "AI" in pattern:
            assert source == _UNVERIFIED, pattern
    joined = " ".join(row[0] for row in rows)
    for phrase in ("No competitors", "analyst figure only", "Advisors", "AI-powered", "Letters of intent", "GMV"):
        assert phrase in joined, phrase


def test_the_consistency_check_compares_as_stated_and_sends_deal_terms_to_the_calculator() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "compute no difference" in steps
    assert "do not convert one into the other" in steps
    assert "**One call per version of the ask.**" in steps
    assert "Never match a figure against the tool's output by eye across documents" in steps
    assert "not passed as `investment`" in steps and "vc-deal-math step 2" in steps
    assert "never compute, convert or round one" in steps
    assert "**Run the adversarial review**" in steps


def test_the_skeptic_reads_only_the_material_and_quotes_it() -> None:
    skeptic = _unwrapped(_section("### The skeptic"))

    assert not any(re.search(rf"\b{name}\b", skeptic.lower()) for name in _PEOPLE_AND_FIRMS)
    assert "check first" in skeptic
    assert "third person" in skeptic and "do not speak as one" in skeptic
    assert "Read only the founder's material" in skeptic and "do no arithmetic" in skeptic
    assert "quoted word for word" in skeptic
    assert "only the founder's material and the brief above" in skeptic and "not the claims list" in skeptic
    assert "run the skeptic before step 1" in skeptic
    assert "do not go through the skeptic or the refute pass" in skeptic


def test_the_refute_pass_keeps_an_attack_only_when_the_material_grounds_it() -> None:
    refute = _unwrapped(_section("### The refute pass"))
    quotes = _unwrapped(_section("### Check the quotes"))

    for verdict in _REFUTE_VERDICTS:
        assert verdict in refute, verdict
    assert "one subagent per attack" in refute
    # A discount pattern is one of the grounds, so the pass that judges grounds is handed the patterns.
    assert "a pattern from the discount table" in refute
    assert "the Pattern column of the discount table below and the brief below with its three verdicts" in refute
    assert "An attack is kept only if it is grounded" in refute
    assert "A line that is not in the material word for word does not drop the attack" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "Bring in no outside fact" in refute and "do no arithmetic" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_answer_leads_with_what_a_partner_checks_first() -> None:
    answering = _unwrapped(_section("## Answering"))

    assert answering.index("**Checked first:**") < answering.index("**Claims table:**")
    assert "**Dropped,**" in answering
    assert _CLAIMS_COLUMNS.search(answering)
    assert "not investment, legal or tax advice" in answering


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name


def test_one_eval_flags_the_patterns_a_vc_discounts() -> None:
    prompts = {path: _unwrapped(_section("## Prompt", path.read_text(encoding="utf-8"))) for path in _EVALS}
    (path,) = (path for path, prompt in prompts.items() if "We have no competitors." in prompt)
    answer = _unwrapped(_section("## Expected answer", path.read_text(encoding="utf-8")))

    assert "letters of intent" in prompts[path] and "1% of it" in prompts[path]
    assert answer.count("Will be discounted") >= len(_PATTERNS) - 1
    assert "does not work out 1% of $40B" in answer


def test_one_eval_keeps_a_grounded_attack_and_drops_one_answered_and_one_not_grounded() -> None:
    (path,) = (path for path in _EVALS if "Dropped, not grounded" in path.read_text(encoding="utf-8"))
    text = path.read_text(encoding="utf-8")
    prompt = _unwrapped(_section("## Prompt", text))
    answer = _unwrapped(_section("## Expected answer", text))

    assert "Kept, grounded" in answer and "Dropped, answered" in answer
    for quoted in _DOUBLE_QUOTED.findall(answer):
        assert quoted in prompt, quoted
    attacked, answered = answer.split("Dropped, answered", 1)
    answering_line = _DOUBLE_QUOTED.findall(answered)[0]
    assert answering_line not in _DOUBLE_QUOTED.findall(attacked)


def test_the_no_call_evals_carry_no_call_or_excerpt() -> None:
    assert len(_NO_CALL_EVALS) == _EVAL_COUNT - len(_CALL_EVALS) and _NO_CALL_EVALS and _CALL_EVALS
    for path in _NO_CALL_EVALS:
        text = path.read_text(encoding="utf-8")
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: each excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    calls, excerpts = _fences("json", text), _fences("text", text)

    assert calls and len(calls) == len(excerpts)
    for call, excerpt in zip(calls, excerpts, strict=True):
        report = render_sheet(sheet_for(compute(DealCheckInput.model_validate(json.loads(call)["inputs"]))))
        printed = [line.rstrip() for line in report.splitlines()]
        for line in excerpt.splitlines():
            assert line in printed, line


def test_a_two_document_eval_runs_one_call_per_document() -> None:
    (path,) = (path for path in _CALL_EVALS if len(_fences("json", path.read_text(encoding="utf-8"))) > 1)
    stated = [
        json.loads(call)["inputs"]["stated_investor_percent"]
        for call in _fences("json", path.read_text(encoding="utf-8"))
    ]

    assert len(set(stated)) == len(stated)


_SAFE_UNCHECKED = "not checked: no tool computes this for a SAFE or note raise"
_SAME_FORM = "same metric, in the same form, for the same period"
# A figure an eval's answer takes from the calculator: a percent or months with decimals, or money with cents.
_PRINTED_FIGURE = re.compile(r"-?\d[\d,]*\.\d+%|\d[\d,]*\.\d+ months|\$\d[\d,]*\.\d{2}")
# A share as the MCP tool returns it: a fraction with six places and no percent sign.
_JSON_FRACTION = re.compile(r"(?<![\d.])-?\d+\.\d{6}(?![\d%])")


def test_the_refute_brief_itself_carries_the_pattern_precedence_and_the_same_form_rule() -> None:
    """The rules that settle a tie sit inside what each refute subagent is handed, never only in the text before it."""
    handoff, brief = (_unwrapped(part) for part in _section("### The refute pass").split("The brief:\n", 1))

    assert "the brief below with its three verdicts and the rules after them" in handoff
    assert "is Kept, grounded even when the material shows evidence" in brief
    assert "even when" not in handoff
    assert f"For a figure, a second line counts as a conflict only when it states the {_SAME_FORM}" in brief
    assert "never as a conflict" in brief
    assert "the material already shows the evidence the attack asks for, and the attack matches no pattern" in brief
    assert "An attack is kept only if it is grounded" in brief


def test_figures_in_different_forms_are_needs_a_source_in_every_rule_that_sets_a_verdict() -> None:
    steps = _unwrapped(_section("## Steps"))
    verdicts = {row[0]: row[1] for row in _table("## The four verdicts")}

    assert steps.index("**Set each verdict**") < steps.index(f"states the {_SAME_FORM}")
    assert "make the attack Needs a source, never Contradicted" in steps
    assert "the same metric in the same form for the same period" in verdicts["Contradicted"]
    assert "MRR against ARR" in verdicts["Needs a source"]


def test_the_skeptic_can_attack_with_a_discount_pattern_and_runs_before_step_1_without_subagents() -> None:
    skeptic = _unwrapped(_section("### The skeptic"))
    steps = _unwrapped(_section("## Steps"))
    note = "Without a subagent tool, run the skeptic first, before step 1"

    assert "the discount pattern it matches" in skeptic
    assert "plus the Pattern column of the discount table below" in skeptic
    assert note in steps and steps.index(note) < steps.index("1. **List the claims, word for word.**")
    assert "Say whether the skeptic ran as a subagent or in the same agent" in _unwrapped(_section("## Answering"))


def test_checked_first_lists_every_mismatch_outside_the_cap_of_three() -> None:
    answering = _unwrapped(_section("## Answering"))

    assert "the calculator's mismatches first, each one, outside any cap; then the skeptic's kept attacks" in answering


def test_a_safe_raise_has_no_ownership_verdict_and_its_runway_goes_to_the_runway_plan_tool() -> None:
    steps = _unwrapped(_section("## Steps"))
    verdicts = {row[0]: row[1] for row in _table("## The four verdicts")}

    assert "it gives no consistent or mismatch verdict" in steps
    assert (
        "Only a consistent `equity_deal_check` row, or for a runway an `equity_runway_plan` row, makes a deal term "
        "Supported"
    ) in steps
    assert "Runway with no raise, or on a SAFE or note raise, and the use-of-funds lines on such a raise go to" in steps
    assert "`equity_runway_plan`, as vc-deal-math step 2 says" in steps
    assert "With no cash or burn given, ask for them by name" in steps and "make no call until they are given" in steps
    assert "is never worked out by hand" in steps
    assert _SAFE_UNCHECKED not in _TEXT and "no tool checks the runway claim" not in _TEXT
    assert "`equity_runway_plan`" in verdicts["Supported"]
    assert "a SAFE or note raise's ownership" in verdicts["Needs a source"]
    assert "0.166667 is 16.6667%" in steps and "a change of notation, not a calculation" in steps


def test_step_5_asks_which_way_the_founders_fully_diluted_total_counts_safes_and_notes() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "SAFEs and notes excluded" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "`[fully diluted shares before the round, SAFEs and notes left out]`" in steps
    assert "never subtract the SAFE or note shares yourself" in steps


def test_a_mismatch_under_one_reading_of_an_unlabelled_valuation_is_needs_a_source() -> None:
    steps = _unwrapped(_section("## Steps"))
    verdicts = {row[0]: row[1] for row in _table("## The four verdicts")}

    assert "A check that is a mismatch under one reading only is not a calculator mismatch" in steps
    assert "the claim is Needs a source with both readings in its fix" in steps
    assert "Only a check that is a mismatch under every reading is the calculator's mismatch" in steps
    assert "under every reading of a valuation with no label" in verdicts["Contradicted"]
    assert "a mismatch under one reading only of a valuation with no label" in verdicts["Needs a source"]


def test_an_understated_runway_is_never_contradicted_or_checked_first() -> None:
    steps = _unwrapped(_section("## Steps"))
    skeptic = _unwrapped(_section("### The skeptic"))
    verdicts = {row[0]: row[1] for row in _table("## The four verdicts")}

    assert "a runway claim below the computed runway understates it, so it is Needs a source" in steps
    assert "never Contradicted" in steps
    assert "apart from a runway claim below the computed runway" in verdicts["Contradicted"]
    assert "a runway claim below the computed runway (it understates)" in verdicts["Needs a source"]
    assert "A runway claim below the computed runway" in skeptic and "are not among them" in skeptic
    # A runway the tool gives no check row for says why, in words, since the MCP result gives flag codes only.
    assert "`net_burn_not_positive` or `cash_never_runs_out` flag (revenue covers the burn" in steps


def test_the_skeptic_raises_every_attack_and_the_refute_pass_judges_one_each() -> None:
    skeptic = _unwrapped(_section("### The skeptic"))
    refute = _unwrapped(_section("### The refute pass"))

    assert "raise it anyway, however short the material; the refute pass decides" in skeptic
    assert "run the skeptic as a subagent, however short the material" in skeptic
    assert "launch one subagent per attack in a single message" in refute
    assert "never put two attacks in one subagent" in refute


def test_metrics_and_market_sizes_go_to_their_skills_and_growth_and_ltv_stay_unchecked() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "ARR, retention, churn, CAC payback and burn multiple are checked by the vc-metrics-readiness skill" in steps
    assert "a market size by the vc-market-sizing skill" in steps
    assert 'Growth rates and LTV: no tool computes them; quote them with "not checked: no tool computes this"' in steps
    assert "have no tool here" not in steps


def test_the_letters_of_intent_row_cites_only_the_a16z_items_that_say_so() -> None:
    rows = _table("## Discount patterns")
    (letters,) = (row for row in rows if row[0].startswith("Letters of intent"))
    (pipeline,) = (row for row in rows if "Pipeline" in row[0])

    assert letters[-1] == 'a16z "16 Startup Metrics" (1, 6)' and "pipeline" not in letters[0].lower()
    assert pipeline[-1] == _UNVERIFIED and "pipeline called revenue" in _unwrapped(_section("## Sources"))
    for path in _EVALS:
        assert "items 1 and 2" not in path.read_text(encoding="utf-8"), path.name


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_figure_an_eval_answer_takes_from_the_calculator_is_what_it_prints(path: Path) -> None:
    """A percent, a months figure or a money figure with cents in the expected answer is a line a report prints."""
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
