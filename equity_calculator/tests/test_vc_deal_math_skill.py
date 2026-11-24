"""The vc-deal-math skill stays true to the calculator: its frontmatter, its JSON example, its command and its output.

The JSON example must be a valid ``equity_deal_check`` call, the ``equity_calculator`` command must run, and every
line of the output excerpt that follows it must be a line the command really prints, so no figure in the skill is
typed by hand. The same holds for each eval prompt in evals/vc-deal-math/: its tool call is valid for the tool it
names (``equity_deal_check``, or ``equity_instrument_compare`` for a founder choosing between a priced round and a
note, with a next round or, for a founder who hopes today's raise is the only one, with none) and its excerpt is lines
of the report that call prints. An eval whose right answer is no ``equity_deal_check``
call (a raise on a SAFE) says so under its tool-call heading and carries no call or excerpt to check, and so do the two
evals whose runway call waits for a planned spend's start month or its monthly spend (no ``equity_runway_plan`` call
yet). Every flag code has a row in the skill's flag table, since the tool's JSON gives the codes only. The fully
diluted count the tool takes leaves SAFEs and notes out, so step 2 asks which way the founder's total counts them;
runway with no raise, or on a SAFE or note raise, goes to ``equity_runway_plan``, whose flags the skill explains in
words too.
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
from equity_calculator.schemas.equity_instrument_compare import InstrumentFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag
from equity_calculator.text import render_sheet

_ROOT = Path(__file__).resolve().parents[2]
_SKILL = _ROOT / "skills" / "vc-deal-math" / "SKILL.md"
_EVALS = sorted((_ROOT / "evals" / "vc-deal-math").glob("*.md"))


def _headings(path: Path) -> set[str]:
    """Which of the no-call openings the eval's tool-call heading starts with (none for an eval with a call)."""
    text = path.read_text(encoding="utf-8")
    return {opening for opening in (_NO_CALL, _HELD_FOR_MONTH, _HELD_FOR_SPEND) if opening in text}


_EVAL_COUNT = 8
_NO_CALL = "## Expected tool call\n\nNone: no `equity_deal_check` call."
# A SAFE raise's runway held for the month its planned spend starts, or for that spend once the month is given: no call
# yet, and the runway line says why. "the month the" keeps the first opening from matching the second's "monthly".
_HELD = "## Expected tool call\n\nNone yet: no `equity_runway_plan` call until the founder gives the "
_HELD_FOR_MONTH = _HELD + "month the"
_HELD_FOR_SPEND = _HELD + "monthly spend"
_WAITING_FOR_MONTH = '"not checked: waiting for [the month the planned spend starts]"'
_WAITING_FOR_SPEND = '"not checked: waiting for [the planned monthly spend from that month]"'
# The tool an eval's call goes to, named first under its tool-call heading ("`equity_deal_check`, once:").
_CALLED_TOOL = re.compile(r"^## Expected tool call\n\n`equity_([a-z_]+)`, once:$", re.MULTILINE)
_CALL_EVALS = [path for path in _EVALS if not _headings(path)]
_NO_CALL_EVALS = [path for path in _EVALS if _NO_CALL in _headings(path)]
_HELD_FOR_MONTH_EVALS = [path for path in _EVALS if _HELD_FOR_MONTH in _headings(path)]
_HELD_FOR_SPEND_EVALS = [path for path in _EVALS if _HELD_FOR_SPEND in _headings(path)]
_OWNERSHIP_OFFER = "it still offers `equity_round` (the equity-calculator skill) with the SAFE as an instrument"
_TEXT = _SKILL.read_text(encoding="utf-8")
_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
# A fence inside a list item is indented; the indent is captured so it can be taken off each line.
_FENCE = re.compile(r"^( *)```([a-z]*)\n(.*?)^\1```$", re.MULTILINE | re.DOTALL)
_PROGRAM = "equity_calculator "
_DESCRIPTION_LIMIT = 1024
_TRIGGERS = (
    "check my deck's numbers",
    "is our raise reasonable",
    "what does this round do to my ownership",
    "how much runway does this buy",
    "will a VC question our valuation",
)
_HANDOFF_SKILLS = (
    "equity-calculator",
    "vc-round-sizing",
    "vc-metrics-readiness",
    "vc-market-sizing",
    "vc-term-sheet-review",
)
# A runway_plan call with no milestone, months to raise or landing month can raise only these three flags.
_RUNWAY_FLAGS_WITHOUT_MILESTONES = ("runway_below_band", "cash_never_runs_out", "consistent_beyond_rounding")
_NO_TOOL = "not checked: no tool computes this"
_COMPARE_STEP = "7. **A founder who has not chosen between a priced round now and a convertible note now**"


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


def test_the_frontmatter_names_the_skill_and_the_founders_questions() -> None:
    fields = _frontmatter()

    assert fields["name"] == "vc-deal-math"
    assert len(fields["description"]) <= _DESCRIPTION_LIMIT
    assert not set("<>") & set(fields["description"])
    assert ": " not in fields["description"]
    for trigger in _TRIGGERS:
        assert trigger in fields["description"]
    assert "founder" in fields["description"]


def test_the_json_example_is_a_valid_deal_check_call() -> None:
    (example,) = _fences("json")
    inputs = json.loads(example)["inputs"]

    assert DealCheckInput.model_validate(inputs).scenario == "deal_check"


async def test_the_command_runs_and_prints_every_line_of_the_excerpt() -> None:
    (command,) = _fences("")
    (excerpt,) = _fences("text")
    assert command.startswith(_PROGRAM) and "\n" not in command.strip()

    printed = (await run(shlex.split(command)[1:])).splitlines()

    for line in excerpt.splitlines():
        assert line in printed, line


async def test_the_command_and_the_json_example_are_the_same_check() -> None:
    (example,) = _fences("json")
    (command,) = _fences("")

    printed = json.loads(await run([*shlex.split(command)[1:], "--json"]))

    assert printed["inputs"] == json.loads(
        DealCheckInput.model_validate(json.loads(example)["inputs"]).model_dump_json()
    )


def test_there_is_one_eval_per_worked_company() -> None:
    assert len(_EVALS) == _EVAL_COUNT


def test_one_eval_expects_no_deal_check_call() -> None:
    (path,) = _NO_CALL_EVALS
    text = path.read_text(encoding="utf-8")

    assert _fences("json", text) == [] and _fences("text", text) == []
    assert "equity_round" in text


def test_one_eval_holds_a_safe_raises_runway_until_its_planned_spend_has_a_start_month() -> None:
    """The founder gives the planned spend but not its month: no call, no runway figure, the month asked for by name,
    and the runway line marked with the shared hold sentence's label, which the skill's step 2 carries. The SAFE's
    ownership does not wait: step 2 offers `equity_round` with the next priced round on any SAFE raise."""
    (path,) = _HELD_FOR_MONTH_EVALS
    text = path.read_text(encoding="utf-8")
    answer = _unwrapped(_section("## Expected answer", text))
    steps = _unwrapped(_section("## Steps"))

    assert path.name.startswith("company-bv-")
    assert _fences("json", text) == [] and _fences("text", text) == []
    assert "no `equity_deal_check` call" in _unwrapped(_section("## Expected tool call", text))
    assert f"marks the runway line {_WAITING_FOR_MONTH}" in answer
    assert _WAITING_FOR_MONTH in steps
    assert "It gives no runway figure" in answer and "It never assumes the month" in answer
    assert "`[planned monthly spend and revenue, from which month]` with only the month missing" in answer
    assert "The ownership offer does not wait for the month: it still offers `equity_round`" in answer
    assert _OWNERSHIP_OFFER in answer
    # No runway figure of any kind: the only months in the answer are the deck's own 24 and the phases' month 1.
    assert re.findall(r"(\d[\d.,]*) months?\b", answer) == ["24", "24"]


def test_one_eval_holds_a_safe_raises_runway_until_its_planned_change_has_a_monthly_spend() -> None:
    """The founder gives the month a planned rise starts but not its spend: no call, no runway figure, the spend asked
    for by name and never guessed, the runway line marked with the shared hold sentence's spend label, which the skill's
    step 2 carries, and the SAFE's ownership still offered to `equity_round`."""
    (path,) = _HELD_FOR_SPEND_EVALS
    text = path.read_text(encoding="utf-8")
    answer = _unwrapped(_section("## Expected answer", text))
    steps = _unwrapped(_section("## Steps"))

    assert path.name.startswith("company-bw-")
    assert _fences("json", text) == [] and _fences("text", text) == []
    assert _HELD_FOR_MONTH not in text
    assert "no `equity_deal_check` call" in _unwrapped(_section("## Expected tool call", text))
    assert f"marks the runway line {_WAITING_FOR_SPEND}" in answer
    assert _WAITING_FOR_SPEND in _unwrapped(text.split("## Prompt", 1)[0])
    assert _WAITING_FOR_SPEND in steps
    assert "It gives no runway figure" in answer and "It never assumes the spend" in answer
    assert "`[planned monthly spend and revenue, from which month]` with only the spend missing" in answer
    assert "The ownership offer does not wait for the spend: it still offers `equity_round`" in answer
    assert _OWNERSHIP_OFFER in answer
    # No runway figure and no guessed spend: the only months are the deck's own 24, and no dollar figure is new.
    assert re.findall(r"(\d[\d.,]*) months?\b", answer) == ["24", "24"]
    assert set(re.findall(r"\$[\d,]+", answer)) == {"$60,000", "$15,000"}


def test_every_flag_code_has_a_row_in_the_skills_flag_table() -> None:
    table = _TEXT.split("## Flags", 1)[1].split("\n## ", 1)[0]
    rows = re.findall(r"^\| `([a-z_]+)` +\|", table, re.MULTILINE)

    assert rows == list(get_args(DealFlag))


@pytest.mark.parametrize("path", _CALL_EVALS, ids=[path.stem for path in _CALL_EVALS])
def test_each_eval_call_is_valid_and_its_excerpt_is_what_the_calculator_prints(path: Path) -> None:
    """An eval's figures are pasted from the calculator: its excerpt must be lines of the report for its call."""
    text = path.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    (excerpt,) = _fences("text", text)
    tool = _CALLED_TOOL.search(text)
    assert tool is not None and tool.group(1) in ("deal_check", "instrument_compare")
    model = _INPUT_MODELS[tool.group(1)]

    report = render_sheet(sheet_for(compute(model.model_validate(json.loads(example)["inputs"]))))
    printed = [line.rstrip() for line in report.splitlines()]

    for line in excerpt.splitlines():
        assert line in printed, line


def test_every_skill_it_hands_off_to_exists() -> None:
    handoffs = _unwrapped(_section("## When to use it"))

    for name in _HANDOFF_SKILLS:
        assert name in handoffs, name
        assert (_ROOT / "skills" / name / "SKILL.md").is_file(), name


def test_step_2_asks_which_way_the_founders_fully_diluted_total_counts_safes_and_notes() -> None:
    """The tool's count leaves SAFEs and notes out; a total that counts them gives the founders too low a figure."""
    steps = _unwrapped(_section("## Steps"))
    (company_b,) = (path for path in _EVALS if path.name.startswith("company-b-"))
    answer = _unwrapped(_section("## Expected answer", company_b.read_text(encoding="utf-8")))

    assert "SAFEs and notes left out, since the tool converts them itself" in steps
    assert "Some cap tables count SAFEs and notes in their fully diluted total" in steps
    assert "ask which way the founder's does, and pass the tool its own basis" in steps
    assert "`[fully diluted shares before the round, SAFEs and notes left out]`" in steps
    assert "never subtract the SAFE or note shares yourself" in steps
    assert "leave the two SAFEs out, as the tool's count does" in answer
    assert "the figures stand only on that basis" in answer


def test_the_stand_in_share_count_is_named_as_this_skills_placeholder() -> None:
    steps = _unwrapped(_section("## Steps"))

    assert "offer a stand-in of 10,000,000 shares" in steps
    assert "call it this skill's placeholder in the answer, never a company figure" in steps


def test_runway_with_no_raise_or_on_a_safe_goes_to_the_runway_plan_tool() -> None:
    steps = _unwrapped(_section("## Steps"))
    handoffs = _unwrapped(_section("## When to use it"))

    assert "**Runway with no raise, or on a SAFE or note raise,** goes to `equity_runway_plan`" in steps
    assert "never to `deal_check`, which needs a priced round" in steps
    assert "With no cash or burn given, ask for them by name" in steps
    assert "make no call until they are given" in steps
    assert "`equity_runway_plan`" in handoffs
    # The MCP result gives flag codes only, so the skill carries the meaning of each flag such a call can raise.
    for flag in _RUNWAY_FLAGS_WITHOUT_MILESTONES:
        assert flag in get_args(RunwayPlanFlag), flag
        assert f"`{flag}` (" in steps, flag
    assert "no runway-plan flag" not in steps
    assert "which today is `unverified`" not in _TEXT


def test_figures_outside_the_deal_terms_go_to_the_skills_built_for_them() -> None:
    limits = _unwrapped(_section("## Limits"))

    assert "ARR, retention, churn, CAC payback and burn multiple to the vc-metrics-readiness skill" in limits
    assert "a market size to the vc-market-sizing skill" in limits
    assert f'Growth rates and LTV are quoted as stated with "{_NO_TOOL}"' in limits
    assert "(a growth rate, a market size, unit economics)" not in limits


def test_one_eval_calls_the_comparison_tool_and_the_rest_deal_check() -> None:
    tools = [_CALLED_TOOL.search(path.read_text(encoding="utf-8")) for path in _CALL_EVALS]

    assert sorted(match.group(1) for match in tools if match is not None) == [
        "deal_check",
        "deal_check",
        "deal_check",
        "instrument_compare",
        "instrument_compare",
    ]


def test_a_founder_choosing_between_a_priced_round_and_a_note_goes_to_the_comparison_tool() -> None:
    """The step asks for both sets of terms, the next rounds and the exits, never picks, and hands law to a lawyer."""
    steps = _unwrapped(_section("## Steps"))
    (company_bu,) = (path for path in _EVALS if path.name.startswith("company-bu-"))
    answer = _unwrapped(_section("## Expected answer", company_bu.read_text(encoding="utf-8")))

    assert "has not chosen between a priced round now and a convertible note now** goes to" in steps
    assert "`equity_instrument_compare`" in steps and "never to `deal_check`" in steps
    assert 'Pass `{"standard": true}` only when the founder says the terms are standard' in steps
    assert "Ask too whether the founder expects a next priced round, and never assume one either way" in steps
    assert "never assume one" in steps
    assert "Never pick one for them or call one better" in steps
    assert "to their lawyer" in steps
    assert "entry is an alternative for that one round after today, worked from today's cap table" in steps
    assert "a Series A and then a Series B is not modelled" in steps
    assert "It passes the two next rounds as alternatives for the one round after today" in answer
    assert "It never picks an option or calls one better" in answer
    assert "It does not call `equity_deal_check`" in answer


def test_a_founder_who_expects_no_next_round_is_asked_for_the_note_s_own_maturity_and_sale_terms() -> None:
    """With no next round the tool runs its no-next-round mode: the step explains it and asks for the maturity, what
    happens then and the change-of-control term, never assumed; the Company DX eval runs it with an uncapped note."""
    step = _unwrapped(_TEXT.split(_COMPARE_STEP, 1)[1].split("\n## ", 1)[0])
    (company_dx,) = (path for path in _EVALS if path.name.startswith("company-dx-"))
    text = company_dx.read_text(encoding="utf-8")
    (example,) = _fences("json", text)
    inputs = json.loads(example)["inputs"]
    answer = _unwrapped(_section("## Expected answer", text))

    assert "**No next round expected** (the founder hopes this raise is the only one)" in step
    assert "leave `next_rounds` and `note_months_to_conversion` out" in step
    assert "the tool runs its no-next-round mode and says so (flag `no_next_round_given`)" in step
    for field in (
        "note_maturity_months",
        "note_maturity_conversion_valuation",
        "note_maturity_conversion_price",
        "note_owed_months",
        "note_change_of_control_multiple",
        "note_change_of_control_at_cap",
        "note_months_to_exit",
    ):
        assert f"`{field}`" in step, field
    assert "Ask, from the note's own terms and never assumed" in step
    for code in ("no_change_of_control_term", "uncapped_no_change_of_control_term", "existing_instruments_outstanding"):
        assert f"`{code}`" in step, code
    assert "next_rounds" not in inputs and "note_months_to_conversion" not in inputs
    assert "note_valuation_cap" not in inputs
    assert compute(_INPUT_MODELS["instrument_compare"].model_validate(inputs)).mode == "no_next_round"
    assert "it says in words that the comparison runs with no next round (`no_next_round_given`)" in answer
    assert "It never picks an option or calls one better" in answer


def test_the_comparison_step_carries_every_flag_s_meaning() -> None:
    """The MCP result gives the comparison's flag codes only, so step 7 says what each one means, in words."""
    step = _unwrapped(_TEXT.split(_COMPARE_STEP, 1)[1].split("\n## ", 1)[0])

    assert "The MCP result gives flag codes only; relay each in these words" in step
    for flag in get_args(InstrumentFlag):
        assert f"`{flag}`" in step, flag
    assert "the command line's report for `instrument_compare`" not in _TEXT
