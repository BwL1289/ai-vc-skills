"""The labelled assumptions a raise pipeline rests on: its own conventions, unverified, and the runway plan's rows.

No primary source says how to count a round's allocation or a fundraising funnel; the rules here (soft commitments
never counted, pro rata counted in full, one investor at one stage, each moving on independently at the founder's
rate) are this calculator's, marked unverified. The start-raising month is the runway plan scenario's, so its own
assumption rows follow, word for word, whenever cash and burn are given.
"""

from __future__ import annotations

from equity_calculator.assumptions import UNVERIFIED
from equity_calculator.schemas.equity_common import EquityAssumption
from equity_calculator.schemas.equity_raise_pipeline import RaisePipelineInput

__all__ = ["raise_pipeline_assumptions"]

_FOUNDER = "the founder"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def _allocation_rows(inputs: RaisePipelineInput) -> list[EquityAssumption]:
    lead = "L = the lead's cheque" if inputs.lead_cheque is not None else "L = 0: no lead cheque given"
    return [
        _assumption(
            "allocation_rule",
            f"left = R - L - firm - pro rata; {lead}",
            "The allocation left is the round less the lead's cheque, the firm commitments and the pro rata amounts. "
            "A soft commitment is summed and shown on its own, never counted against the round.",
            f"{UNVERIFIED} (standard arithmetic; soft or firm as the founder marks each)",
        ),
        _assumption(
            "pro_rata_rule",
            "each pro rata amount counted in full",
            "Each existing investor's pro rata amount, as the founder gives it, is counted as taken, whether or not "
            "that investor has said it will use it.",
            f"{UNVERIFIED} (a planning convention)",
        ),
    ]


def _funnel_rows(inputs: RaisePipelineInput) -> list[EquityAssumption]:
    if not inputs.stages:
        return []

    benchmarks = [stage.name for stage in inputs.stages if stage.rate_basis == "benchmark"]
    basis = "every rate the founder's own" if not benchmarks else f"benchmark rates at {', '.join(benchmarks)}"
    rate_source = (
        _FOUNDER
        if not benchmarks
        else "the founder; each benchmark from the source the founder gave beside its stage (not checked here)"
    )
    return [
        _assumption(
            "stage_counting",
            "each investor counted once, at the furthest stage it has reached",
            "An investor at a later stage today moves on from there at that stage's rate and every later one.",
            f"{UNVERIFIED} (a modelling choice)",
        ),
        _assumption(
            "expected_term_sheets",
            "E = the sum of the investors at each stage times the product of the rates from it on",
            "An expectation from the founder's own rates, not a forecast: each investor moves on independently of "
            "the others at its stage's rate, so the term sheets that arrive can be more or fewer.",
            f"{UNVERIFIED} (standard arithmetic of expected values)",
        ),
        _assumption(
            "rate_basis", basis, "Every rate is one the founder gave; none is assumed or looked up.", rate_source
        ),
        _assumption(
            "targets_needed",
            "ceiling(W / the product of every rate); more = ceiling((W - E) / it), 0 when E >= W",
            "Targets are whole investors, so each count needed is rounded up; the targets needed start from an empty "
            "funnel, the more needed from today's.",
            f"{UNVERIFIED} (standard arithmetic)",
        ),
    ]


def raise_pipeline_assumptions(
    inputs: RaisePipelineInput, runway_rows: tuple[EquityAssumption, ...]
) -> tuple[EquityAssumption, ...]:
    """The pipeline's rows, each only when the input uses it, then the runway plan's own rows when it was worked."""
    rows = [*_allocation_rows(inputs), *_funnel_rows(inputs)]
    if inputs.runway is not None:
        rows.append(
            _assumption(
                "start_raising_rule",
                f"runway with no raise less {inputs.runway.months_to_raise} months to raise",
                "The start-raising month is the runway plan scenario's own figure for the plan case with no raise, "
                "in months from today; none when the cash never runs out.",
                f"{UNVERIFIED} (the runway plan's arithmetic; the months to raise are the founder's)",
            )
        )
        rows += runway_rows

    return tuple(rows)
