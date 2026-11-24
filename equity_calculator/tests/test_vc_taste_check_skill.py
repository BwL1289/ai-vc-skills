"""The vc-taste-check skill keeps its shape: its frontmatter, its fixed words, its adversarial review and its evals.

The skill reads a founder's own product, brand and scope decisions, including what they said no to, and helps them
show the judgment behind them. It names no calculator tool, does no arithmetic and cites no source, since none was
read in full. Every skill it hands off to by name must be a folder in skills/, and vc-positioning must point back to
it. The three checks and the flags are fixed words. The adversarial review keeps vc-positioning's two stages:
independent attack lenses named by what they test (never by a person or firm), each objection quoting the founder's
own line; and a refute pass that may use only the founder's material, grounds a copying claim only in the founder's
own words, and records why each dropped objection fell. Each eval in evals/vc-taste-check/ has a prompt, an expected
tool call and an expected answer, makes no calculator call, and quotes only lines its prompt contains.
"""

from __future__ import annotations

import re
from pathlib import Path

from tests.test_vc_claims_check_skill import _READ_SOURCES

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-taste-check" / "SKILL.md"
_TEXT = _SKILL.read_text(encoding="utf-8")
_POSITIONING = (_ROOT / "skills" / "vc-positioning" / "SKILL.md").read_text(encoding="utf-8")
_EVALS = sorted((_ROOT / "evals" / "vc-taste-check").glob("*.md"))
_EVAL_COUNT = 4
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
_EVAL_HEADINGS = ("## Prompt", "## Expected tool call", "## Expected answer")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_TOOL_NAME = re.compile(r"`(equity_[a-z_]+)`")
_URL = re.compile(r"https?://\S+")
_HANDOFF_SKILLS = ("vc-positioning", "vc-claims-check", "vc-deal-math", "equity-calculator", "vc-metrics-readiness")
_DESCRIPTION_LIMIT = 1024
_LINE_LIMIT = 500
_TRIGGERS = (
    "does our product show taste",
    "what should we cut",
    "is our brand generic",
    "does this sound AI-written",
    "which decisions should I show investors",
)
_DESCRIPTION_WORDS = ("founder", "adversarial review", "said no to", "taste-washed", "AI-sounding", "copycat")
_CHECKS = ("Clarity", "Usefulness", "Trust")
_FLAGS = ("Generic", "AI-sounding", "Copycat", "Taste-washed", "Claimed quality")
_SCOPE_FLAG = "Scope"
# Names a lens must never carry: the skill tests frameworks, never people or firms.
_PEOPLE_AND_FIRMS = ("sequoia", "a16z", "andreessen", "y combinator", "yc", "graham", "dixon", "stebbings", "20vc")
_MIN_LENSES = 5
_LENS_HEAD = re.compile(r"^\|\s*Lens\s*\|\s*What it tests\s*\|$", re.MULTILINE)
_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|", re.MULTILINE)
_TABLE_ROW = re.compile(r"^\|(.+)\|$", re.MULTILINE)
_SURVIVOR_COLUMNS = re.compile(
    r"Rank, Tier, Lens, The founder's line \(quoted\), Why a partner reads it that way,\s+Fix"
)
_DECISION_COLUMNS = "#, Decision (quoted), Said no to (quoted), Clarity, Usefulness, Trust, Flags, Placement"
_DOUBLE_QUOTED = re.compile(r'"([^"]+)"')
_DIGITS = re.compile(r"\d+")
_EVAL_TITLE = re.compile(r"\A# Eval (\d+): ")
_BADGE = re.compile(r'alt="Skills: (\d+)" src="https://img\.shields\.io/badge/skills-(\d+)-')
_CATCH_ALL = "**Not yet:** every other decision"
_OUTRANKS = "a kept objection that ends the meeting or weakens it, or a flag, which outranks the meeting"
# The one sentence every attack brief in the pack carries since a live run's attacker judged the material for itself.
_RAISE_IT_ANYWAY = "raise it anyway, however short the material, and the refute pass decides"
# An objection that only says an input is missing is an open ask, never a kept objection (a live run kept one).
_MISSING_INPUT = "an input from the Inputs list is missing (what changed, the alternatives, the material)"
_JUDGMENT_RULE = "A call the founder labels a judgment before data, saying how they will know it was right"
# Words a prompt uses when the founder's own material grounds a copying claim; an eval that drops a copying claim as
# not grounded must have none of them.
_COPYING_WORDS = ("competitor", "copied", "copy", "borrowed", "industry standard", "because every")


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
    body = _section(heading)
    rows = [[cell.strip() for cell in match.group(1).split("|")] for match in _TABLE_ROW.finditer(body)]
    return rows[2:]


def _lens_names() -> list[str]:
    table = _section("### Stage A: attack")
    head = _LENS_HEAD.search(table)
    assert head is not None
    rows = table[head.end() :].strip().split("\n\n", 1)[0].splitlines()[1:]
    return [match.group(1) for row in rows if (match := _ROW.match(row))]


def _eval_parts(path: Path) -> tuple[str, str]:
    """An eval's prompt and expected answer, each unwrapped."""
    text = path.read_text(encoding="utf-8")
    return _unwrapped(_section("## Prompt", text)), _unwrapped(_section("## Expected answer", text))


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()
    description = fields["description"]

    assert fields["name"] == "vc-taste-check"
    assert len(description) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(description)
    assert ": " not in description
    for trigger in _TRIGGERS:
        assert trigger in description, trigger
    for word in _DESCRIPTION_WORDS:
        assert word in description, word
    assert len(_TEXT.splitlines()) < _LINE_LIMIT


def test_every_skill_it_hands_off_to_exists_and_vc_positioning_points_back() -> None:
    for name in _HANDOFF_SKILLS:
        assert name in _TEXT
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name
    assert "vc-taste-check" in _section("## When to use it", _POSITIONING)


def test_it_names_no_calculator_tool_and_does_no_arithmetic() -> None:
    limits = _unwrapped(_section("## Limits"))
    steps = _unwrapped(_section("## Steps"))

    assert _TOOL_NAME.findall(_TEXT) == []
    assert "No arithmetic and no calculator tool" in limits
    assert "never computed, converted or rounded" in steps


def test_it_cites_no_source_since_none_was_read_in_full() -> None:
    sources = _unwrapped(_section("## Sources")).strip()
    urls = set(_URL.findall(_TEXT))
    for path in _EVALS:
        urls |= set(_URL.findall(path.read_text(encoding="utf-8")))

    # The lasting rule: any source the skill or its evals cite comes from the one set of read sources.
    assert urls <= set(_READ_SOURCES)
    # Today's state: none is cited. Adding a read source later means deleting only this line.
    assert urls == set()
    assert sources.startswith("None.") and "unverified" in sources


def test_the_no_list_is_required_and_decisions_are_never_offered() -> None:
    inputs = _section("## Inputs")
    no_list = _unwrapped(inputs.split("\n2. ", 1)[1].split("\n3. ", 1)[0])

    assert "said no to" in no_list and "This item is required" in no_list
    assert "A decision list with no NOs is itself the first open ask" in _unwrapped(inputs)
    assert "never offer example decisions" in _unwrapped(inputs)
    assert "never a row" in _unwrapped(_section("## Steps"))
    assert "never offers sample decisions" in _unwrapped(_section("## Limits"))
    assert "With no decisions listed at all, run no checks and no review" in _unwrapped(inputs)


def test_the_checks_and_flags_are_the_fixed_words() -> None:
    checks = [row[0] for row in _table("## The three checks")]
    flags = [row[0] for row in _table("## Flags")]

    assert checks == list(_CHECKS)
    assert set(flags) <= set(_FLAGS) | {_SCOPE_FLAG}
    for flag in _FLAGS:
        assert flag in flags, flag
    assert "Clear, Needs work or Missing" in _unwrapped(_section("## The three checks"))


def test_the_flags_are_quotable_rather_than_a_feeling() -> None:
    flags = _section("## Flags")
    rows = _table("## Flags")
    washed = [" ".join(row) for row in rows if row[0] == "Taste-washed"]

    assert any("no cut or trade-off" in row for row in washed)
    assert "Never say or imply that a model wrote it" in _unwrapped(flags)
    assert "| Pattern" in flags


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
    assert _RAISE_IT_ANYWAY in attack and "rather than a weak objection" not in attack
    assert "as parallel subagents, however short the material" in attack
    assert "no list of what the founder did not provide" in attack


def test_the_refute_stage_uses_only_the_founders_material_and_says_why_each_objection_fell() -> None:
    refute = _unwrapped(_section("### Stage B: refute"))
    quotes = _unwrapped(_section("### Check the quotes"))

    assert "using only the founder's material" in refute
    assert "launch one subagent per objection in a single message" in refute
    assert "never put two objections in one subagent" in refute
    assert "is missing (what changed, the alternatives, the material) rather than about what the line says" in refute
    assert _MISSING_INPUT in quotes and "is never kept against that decision" in quotes
    for verdict in ("Dropped, answered:", "Dropped, not grounded:", "Kept:"):
        assert verdict in refute, verdict
    assert "Quote the founder's line that answers it" in refute
    assert "invents nothing on the founder's behalf" in refute
    assert "an answering line that is not in the material word for word does not drop the objection" in refute
    assert "word for word" in quotes and "dropped as not grounded" in quotes


def test_the_refute_brief_is_handed_over_whole_and_grounds_copying_in_the_founders_words() -> None:
    stage = _section("### Stage B: refute")
    handoff, brief = (_unwrapped(part) for part in stage.split("\n\nThe refute brief:\n\n", 1))

    assert "the Pattern column of the flags table above" in handoff
    assert 'everything from "The refute brief:" to the end of this stage' in handoff
    for rule in (
        "you argue neither side",
        "Bring in no outside fact about the company, its market or its competitors",
        "How a partner is likely to read a line is not an outside fact",
        "grounded only when the founder's own material names that company",
        "never answers an objection",
        "When you cannot decide, return Kept",
        _JUDGMENT_RULE,
        "invents nothing on the founder's behalf",
    ):
        assert rule in brief, rule
    assert "argue the founder's side" not in _unwrapped(stage)


def test_the_survivors_are_ranked_with_quotes_and_feed_the_rest_of_the_answer() -> None:
    rank = _unwrapped(_section("### Rank what survives"))
    answering = _unwrapped(_section("## Answering"))

    assert "the founder's line, quoted word for word" in rank
    assert "no percentages and no score" in rank
    assert "biggest issues" in rank and '"not yet"' in rank
    assert "objection that ends the meeting or weakens it is placed" in rank
    assert "A minor survivor does not move a decision" in rank
    assert "**Adversarial review:**" in answering and "**Dropped,**" in answering
    assert _SURVIVOR_COLUMNS.search(answering)
    assert _DECISION_COLUMNS in answering
    assert "not investment, legal or tax advice" in answering and "no review can score taste" in answering


def test_without_a_subagent_tool_the_lenses_run_before_step_1_and_the_answer_says_so() -> None:
    steps = _unwrapped(_section("## Steps"))
    attack = _unwrapped(_section("### Stage A: attack"))
    note = "Without a subagent tool, run Stage A of the adversarial review first, before step 1"

    assert note in steps and steps.index(note) < steps.index("1. **Quote first.**")
    assert "**Run the adversarial review**" in steps
    assert "every surviving objection quotes a line that is in the material word for word" in steps
    assert "run Stage A first, before step 1" in attack and "less independent than subagents" in attack
    assert "less independent than separate subagents" in _unwrapped(_section("## Answering"))


def test_the_lines_are_placed_in_the_deck_the_meeting_or_not_yet() -> None:
    placement = _unwrapped(_section("## Why we built it this way"))

    for where in ("**In the deck:**", "**In the meeting:**", "**Not yet:**"):
        assert where in placement, where
    assert "at most three" in placement
    assert "Never a slide about the founder's taste" in placement
    assert "never the word taste" in placement
    # Every row of the decisions table needs a placement, so Not yet takes every decision the other two do not, and a
    # kept objection or a flag outranks the meeting.
    assert "Every row of the decisions table gets exactly one placement" in placement
    assert _CATCH_ALL in placement and _OUTRANKS in placement
    assert "any decision marked Needs work or Missing on a check, a story or not" in placement.split(_CATCH_ALL, 1)[1]
    assert placement.count("no kept objection above minor and no flag") == 2
    # The deck and the meeting share one bar (a deck run found the meeting's bar lower than the deck's, with "needs a
    # story" undefined): both say Clear on all three checks, and the story is defined by what happened.
    assert placement.count("no kept objection above minor and no flag, Clear on all three") == 2
    assert "The deck and the meeting share one bar, and the deck adds to it" in placement
    assert "A decision **needs a story** when what it turned down happened rather than was only decided" in placement
    assert "tied to the core workflow, and needing no story" in placement
    assert "naming every kept objection on it" in placement
    assert "A second sentence is allowed only for the founder's evidence line" in placement


def test_figure_lines_are_quoted_whole_and_every_not_yet_names_its_objections() -> None:
    """A live run turned "11 of 12" into "the twelfth" and gave a count of facts its own table did not match."""
    steps = _unwrapped(_section("## Steps"))

    assert "A figure line goes into a why-we-built-it line word for word" in steps
    assert "never states what a figure leaves over" in steps
    assert 'every "not yet" placement names every kept objection on that decision' in steps
    assert "retention or churn to the vc-metrics-readiness skill" in steps


def test_a_labelled_judgment_before_data_counts_for_trust_in_the_lenses_and_the_refute_pass() -> None:
    trust = " ".join(row[1] for row in _table("## The three checks") if row[0] == "Trust")
    attack = _unwrapped(_section("### Stage A: attack"))
    refute = _unwrapped(_section("### Stage B: refute"))

    assert "labels it a judgment" in trust
    assert "is not untrustworthy for lacking data yet" in attack
    assert _JUDGMENT_RULE in refute and "even when the objection quotes the label itself" in refute


def test_there_is_one_eval_per_worked_company_and_each_has_the_three_parts() -> None:
    assert len(_EVALS) == _EVAL_COUNT
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        positions = [text.find(f"\n{heading}\n") for heading in _EVAL_HEADINGS]
        assert -1 not in positions and positions == sorted(positions), path.name
        assert _section("## Prompt", text).strip().startswith("> "), path.name
        assert "made up" in text, path.name


def test_the_evals_are_numbered_in_letter_order() -> None:
    for number, path in enumerate(_EVALS, start=1):
        title = _EVAL_TITLE.match(path.read_text(encoding="utf-8"))
        assert title is not None and int(title.group(1)) == number, path.name


def test_the_readme_badge_counts_the_skill_folders() -> None:
    badge = _BADGE.search((_ROOT / "README.md").read_text(encoding="utf-8"))
    folders = sorted((_ROOT / "skills").glob("*/SKILL.md"))

    assert badge is not None
    assert int(badge.group(1)) == int(badge.group(2)) == len(folders)


def test_every_eval_makes_no_calculator_call() -> None:
    for path in _EVALS:
        text = path.read_text(encoding="utf-8")
        assert _NO_CALL in text, path.name
        assert _fences("json", text) == [] and _fences("text", text) == [], path.name


def test_every_quote_in_an_eval_answer_is_in_its_prompt() -> None:
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        for quoted in _DOUBLE_QUOTED.findall(answer):
            assert quoted in prompt, (path.name, quoted)


def test_no_eval_answer_carries_a_figure_its_prompt_does_not() -> None:
    # Figures are quoted as stated, never computed, converted or rounded, so an expected answer holds no number and
    # no percent its prompt lacks, and the skill itself prints no percent.
    assert "%" not in _TEXT
    for path in _EVALS:
        prompt, answer = _eval_parts(path)
        assert set(_DIGITS.findall(answer)) <= set(_DIGITS.findall(prompt)), path.name
        assert "%" not in answer or "%" in prompt, path.name


def test_one_eval_drops_an_objection_by_quoting_the_line_that_answers_it() -> None:
    dropping = [path for path in _EVALS if "Dropped, answered" in _eval_parts(path)[1]]
    assert dropping
    for path in dropping:
        prompt, answer = _eval_parts(path)
        objection, dropped = answer.split("Dropped, answered", 1)
        # The first quote after the verdict is the founder's line that answers the objection: a whole line of the
        # founder's material, not the line the objection was about.
        answering_line = _DOUBLE_QUOTED.findall(dropped)[0]
        assert answering_line in prompt
        assert answering_line not in _DOUBLE_QUOTED.findall(objection)


def test_a_copying_claim_the_founders_own_words_ground_is_kept() -> None:
    (path,) = (path for path in _EVALS if "every competitor launched one this year" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "Copycat" in answer and "Kept" in answer
    assert "not grounded" not in answer


def test_one_eval_drops_a_copying_claim_the_founders_material_does_not_ground() -> None:
    dropping = [path for path in _EVALS if "Dropped, not grounded" in _eval_parts(path)[1]]
    assert dropping
    for path in dropping:
        prompt = _eval_parts(path)[0].lower()
        assert not any(word in prompt for word in _COPYING_WORDS), path.name


def test_a_request_to_invent_decisions_writes_no_line_and_places_nothing() -> None:
    (path,) = (path for path in _EVALS if "come up with" in _eval_parts(path)[0])
    answer = _eval_parts(path)[1]

    assert "declines to make up decisions" in answer
    assert "No why-we-built-it line is written" in answer and "nothing is placed in the deck" in answer
    assert "open asks" in answer


def test_a_request_to_judge_as_named_people_is_declined() -> None:
    named = [
        path
        for path in _EVALS
        if any(re.search(rf"\b{name}\b", _eval_parts(path)[0].lower()) for name in _PEOPLE_AND_FIRMS)
    ]
    assert named
    for path in named:
        answer = _eval_parts(path)[1]
        assert "declines" in answer and "named person's or firm's voice" in answer


def test_the_drop_eval_scores_only_what_a_run_can_show_and_records_its_live_run() -> None:
    """A live run raised no objection to D1's reason, which every lens could read, so the drop and placements are
    conditional on what the lenses keep."""
    (path,) = (path for path in _EVALS if path.name.startswith("company-t-"))
    text = path.read_text(encoding="utf-8")
    answer = _eval_parts(path)[1]

    assert "If a lens objects to" in answer and "Raised or not, that reason sits next to D1" in answer
    assert "unless an objection that ends the meeting or weakens it survives on D1" in answer
    assert "when no objection above minor survives on it" in answer and "naming every kept objection on it" in answer
    assert "## Recorded answer" in text and text.index("## Expected answer") < text.index("## Recorded answer")


def test_decisions_are_numbered_t_so_a_founders_own_d_numbers_never_clash() -> None:
    """A founder log that numbers its own decisions D1, D2 used the same labels the skill gave its rows."""
    steps = _unwrapped(_section("## Steps"))

    assert "numbered T1, T2 and so on" in steps and "numbered D1" not in steps
    assert 'the founder\'s own label is kept and quoted beside it ("T1, your D4")' in steps


def test_a_log_of_layout_detail_or_assistant_text_keeps_only_the_founders_decisions() -> None:
    """A log of mostly layout entries, or partly written by assistant sessions, had every line checked as a decision."""
    steps = _unwrapped(_section("## Steps"))

    assert '"not checked: layout detail"' in steps and "which of them the founder wants checked" in steps
    assert "where the log itself marks an entry as an assistant's" in steps
    assert "only the founder's own words and the entries the founder marks adopted count as decisions" in steps
    assert 'labelled "assistant text, not the founder\'s"' in steps
    assert "Never infer who wrote a line from how it reads" in steps


def test_an_honesty_choice_can_be_clear_on_usefulness_and_a_claimed_quality_is_flagged() -> None:
    """Trust and honesty decisions were Needs work on Usefulness by construction, and a claimed quality other than
    taste had no flag."""
    usefulness = {row[0]: row[1] for row in _table("## The three checks")}["Usefulness"]
    flags = _unwrapped(_section("## Flags"))
    claimed = [row for row in _table("## Flags") if row[0] == "Claimed quality"]

    assert "or that customer's trust (an honesty or disclosure choice)" in usefulness
    assert len(claimed) == 1 and "claimed in place of a decision" in claimed[0][1]
    assert (
        '"Claimed quality" is the same signal as the second Taste-washed row for any quality other than taste' in flags
    )
