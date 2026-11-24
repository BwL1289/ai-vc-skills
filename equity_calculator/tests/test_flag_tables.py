"""Every flag code a scenario can return has a row in every skill table that gives that scenario's flags their meaning.

A tool call over MCP returns flag codes only, so a skill that keeps a flag table is where the founder's agent reads
what each code means. A code missing from that table reaches the answer with no meaning: a real run of the pack got
``runway_plan``'s ``no_time_to_raise_given`` back where the skill listed only the three codes a call with no milestone
raises.

Each table is registered here with the scenarios it covers, read from the schemas' flag Literals. A table either holds
every code those scenarios can return, or it is a restricted table: its skill makes one call shape, says in its own
words that the call raises no other flag, and the codes that shape cannot raise are listed here with the skill's
sentence. Either way, the codes tabled and the codes excused add up to the scenarios' codes exactly. A table in the
skills that holds any flag code and is not registered fails, so a new table is registered when it is written.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import get_args

import pytest
from equity_calculator.schemas.equity_cap_table_check import CapTableFlag
from equity_calculator.schemas.equity_deal_check import DealFlag
from equity_calculator.schemas.equity_instrument_compare import InstrumentFlag
from equity_calculator.schemas.equity_market_sizing import MarketSizingFlag
from equity_calculator.schemas.equity_metrics_check import MetricsFlag
from equity_calculator.schemas.equity_pool_plan import PoolPlanFlag
from equity_calculator.schemas.equity_raise_pipeline import RaisePipelineFlag
from equity_calculator.schemas.equity_runway_plan import RunwayPlanFlag

_ROOT = Path(__file__).resolve().parents[2]
_SKILLS = _ROOT / "skills"
# Every scenario that returns flags, and the codes its schema says it can return.
_FLAGS: dict[str, frozenset[str]] = {
    "cap_table_check": frozenset(get_args(CapTableFlag)),
    "deal_check": frozenset(get_args(DealFlag)),
    "instrument_compare": frozenset(get_args(InstrumentFlag)),
    "market_sizing": frozenset(get_args(MarketSizingFlag)),
    "metrics_check": frozenset(get_args(MetricsFlag)),
    "pool_plan": frozenset(get_args(PoolPlanFlag)),
    "raise_pipeline": frozenset(get_args(RaisePipelineFlag)),
    "runway_plan": frozenset(get_args(RunwayPlanFlag)),
}
_ALL_CODES = frozenset().union(*_FLAGS.values())
_ROW_CODE = re.compile(r"^\| `([a-z0-9_]+)` +\|")
_DIVIDER = re.compile(r"^\| *-")
# The codes a runway plan with no raise and no milestone in the call cannot raise: the two investor-update skills'
# one call shape, which each skill names in its own words.
_NOT_WITHOUT_RAISE_OR_MILESTONE = frozenset(
    {
        "cash_out_before_raise_lands",
        "milestone_short_on_plan",
        "downside_short_where_plan_covers",
        "covered_without_raise",
        "no_time_to_raise_given",
        "runway_below_band",
    }
)
_NO_RAISE_NO_MILESTONE = "With no raise and no milestone in the call, the tool raises no other flag"


@dataclass(frozen=True)
class _Table:
    """One registered flag table: its file under ``skills/``, the heading it sits under, its header's first cell, the
    scenarios it covers, and (a restricted table only) the codes its skill's call shape cannot raise with the skill's
    sentence that says so."""

    path: str
    section: str
    header: str
    scenarios: tuple[str, ...]
    excused: frozenset[str] = field(default_factory=frozenset)
    because: str = ""


_TABLES = (
    _Table("vc-cap-table-check/SKILL.md", "## Flags", "Flag", ("cap_table_check",)),
    _Table(
        "vc-current-investor-update/SKILL.md",
        "## Runway",
        "Flag",
        ("runway_plan",),
        _NOT_WITHOUT_RAISE_OR_MILESTONE,
        _NO_RAISE_NO_MILESTONE,
    ),
    _Table("vc-deal-math/SKILL.md", "## Flags", "Flag", ("deal_check",)),
    _Table("vc-deal-math/SKILL.md", "## Flags", "`equity_runway_plan` flag", ("runway_plan",)),
    _Table("vc-deck-review/SKILL.md", "## Calculator flags", "Flag", ("deal_check",)),
    _Table("vc-deck-review/SKILL.md", "## Calculator flags", "`equity_runway_plan` flag", ("runway_plan",)),
    _Table("vc-diligence-questions/SKILL.md", "## Flags", "`equity_deal_check` flag", ("deal_check",)),
    _Table("vc-diligence-questions/SKILL.md", "## Flags", "`equity_runway_plan` flag", ("runway_plan",)),
    _Table("vc-investor-memo/references/flags.md", "## Flags", "Flag", ("deal_check", "runway_plan")),
    _Table("vc-market-sizing/SKILL.md", "## Flags", "Flag", ("market_sizing",)),
    _Table("vc-metrics-readiness/SKILL.md", "## Flags", "Flag", ("metrics_check",)),
    _Table("vc-option-pool-plan/SKILL.md", "## Flags", "Flag", ("pool_plan",)),
    _Table(
        "vc-partner-meeting/references/calculator-flags.md",
        "## What each flag code means",
        "Flag (`equity_deal_check`)",
        ("deal_check",),
    ),
    _Table(
        "vc-partner-meeting/references/calculator-flags.md",
        "## What each flag code means",
        "Flag (`equity_runway_plan`)",
        ("runway_plan",),
    ),
    _Table("vc-positioning/SKILL.md", "## Calculator flags", "Flag", ("deal_check",)),
    _Table("vc-positioning/SKILL.md", "## Calculator flags", "`equity_runway_plan` flag", ("runway_plan",)),
    _Table(
        "vc-prospective-investor-update/SKILL.md",
        "## Runway",
        "Flag",
        ("runway_plan",),
        _NOT_WITHOUT_RAISE_OR_MILESTONE,
        _NO_RAISE_NO_MILESTONE,
    ),
    _Table("vc-raise-plan/SKILL.md", "## Flags", "Flag", ("raise_pipeline",)),
    _Table("vc-round-sizing/SKILL.md", "## Flags", "Flag", ("runway_plan",)),
    _Table("vc-round-sizing/SKILL.md", "## Ownership flags", "Flag", ("deal_check",)),
    _Table("vc-term-sheet-review/SKILL.md", "## Flags", "Flag", ("deal_check",)),
)


def _first_cell(line: str) -> str:
    return line.strip().strip("|").split("|", 1)[0].strip()


def _flag_tables(path: Path) -> dict[tuple[str, str], list[str]]:
    """Every table in ``path`` whose rows hold a flag code, by the heading it sits under and its header's first cell:
    the codes its rows open with."""
    lines = path.read_text(encoding="utf-8").splitlines()
    tables: dict[tuple[str, str], list[str]] = {}
    section, index = "", 0
    while index < len(lines):
        if lines[index].startswith("#"):
            section = lines[index].strip()
        if not (lines[index].startswith("|") and index + 1 < len(lines) and _DIVIDER.match(lines[index + 1])):
            index += 1
            continue
        key, end = (section, _first_cell(lines[index])), index + 2
        codes = []
        while end < len(lines) and lines[end].startswith("|"):
            match = _ROW_CODE.match(lines[end])
            if match:
                codes.append(match.group(1))
            end += 1
        if any(code in _ALL_CODES for code in codes):
            assert key not in tables, f"{path}: two flag tables under {key[0]!r} open with {key[1]!r}"
            tables[key] = codes
        index = end
    return tables


def _unwrapped(path: Path) -> str:
    return " ".join(line.lstrip("> ").strip() for line in path.read_text(encoding="utf-8").splitlines())


@pytest.mark.parametrize("table", _TABLES, ids=[f"{table.path}:{table.section}:{table.header}" for table in _TABLES])
def test_each_registered_table_holds_every_code_its_scenarios_can_return(table: _Table) -> None:
    path = _SKILLS / table.path
    codes = _flag_tables(path).get((table.section, table.header))
    assert codes is not None, f"{table.path} has no flag table under {table.section!r} opening with {table.header!r}"
    expected = frozenset().union(*(_FLAGS[name] for name in table.scenarios))

    assert len(codes) == len(set(codes)), f"a code appears twice in {table.path}:{table.header}"
    assert table.excused <= expected and not table.excused & set(codes)
    missing = sorted(expected - table.excused - set(codes))
    assert missing == [], f"{table.path}:{table.header} gives no meaning for {missing}"
    assert set(codes) | table.excused == expected
    if table.excused:
        assert table.because and table.because in _unwrapped(path), table.because


def test_every_flag_table_in_the_skills_is_registered() -> None:
    """A new flag table, or a renamed header, is registered here so the check above reaches it."""
    found = {
        (str(path.relative_to(_SKILLS)), section, header)
        for path in sorted(_SKILLS.rglob("*.md"))
        for section, header in _flag_tables(path)
    }
    registered = {(table.path, table.section, table.header) for table in _TABLES}

    assert found - registered == set()
    assert registered - found == set()


def test_every_scenario_that_returns_flags_has_a_full_table_in_some_skill() -> None:
    """Each scenario's every code has a meaning in at least one skill, with nothing excused."""
    full = {name for table in _TABLES if not table.excused for name in table.scenarios}

    assert full == set(_FLAGS) - {"instrument_compare"}
    # instrument_compare's codes are explained in the deal-math skill's step 7, one by one in its own prose, where
    # that skill's own test checks each.
    step = (_SKILLS / "vc-deal-math" / "SKILL.md").read_text(encoding="utf-8")
    assert [code for code in sorted(_FLAGS["instrument_compare"]) if f"`{code}`" not in step] == []
