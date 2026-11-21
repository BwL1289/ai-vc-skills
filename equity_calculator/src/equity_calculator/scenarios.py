"""One entry point for every scenario: ``compute`` takes any ``EquityInput`` member and returns its result.

A new scenario adds its input and result models to ``ScenarioInput`` / ``ScenarioResult`` in
``equity_calculator.schemas.equity``, its own module here, and one overload and one ``case`` below.
"""

from __future__ import annotations

from typing import assert_never, overload

from equity_calculator.dilution import compute_dilution
from equity_calculator.employee import compute_employee
from equity_calculator.investor import compute_investor
from equity_calculator.pool import compute_pool
from equity_calculator.round import compute_round
from equity_calculator.schemas.equity import (
    DilutionInput,
    DilutionResult,
    EmployeeInput,
    EmployeeResult,
    InvestorInput,
    InvestorResult,
    PoolInput,
    PoolResult,
    RoundInput,
    RoundResult,
    ScenarioInput,
    ScenarioResult,
    VestingInput,
    VestingResult,
    WaterfallInput,
    WaterfallResult,
)
from equity_calculator.vesting import compute_vesting
from equity_calculator.waterfall import compute_waterfall


@overload
def compute(inputs: InvestorInput) -> InvestorResult:
    ...


@overload
def compute(inputs: EmployeeInput) -> EmployeeResult:
    ...


@overload
def compute(inputs: PoolInput) -> PoolResult:
    ...


@overload
def compute(inputs: RoundInput) -> RoundResult:
    ...


@overload
def compute(inputs: DilutionInput) -> DilutionResult:
    ...


@overload
def compute(inputs: VestingInput) -> VestingResult:
    ...


@overload
def compute(inputs: WaterfallInput) -> WaterfallResult:
    ...


def compute(inputs: ScenarioInput) -> ScenarioResult:
    """The worked result of ``inputs``' scenario.

    Raises an ``equity_calculator.errors.EquityComputeError`` (a ``ValueError``) when a valid input has no answer: a
    round with no positive price or whose conversions never settle (``RoundHasNoPrice``, ``ConversionDidNotSettle``), or
    an exit waterfall whose convert-or-stay search finds no stable choice (``NoConversionEquilibrium``).
    """
    match inputs:
        case InvestorInput():
            return compute_investor(inputs)
        case EmployeeInput():
            return compute_employee(inputs)
        case PoolInput():
            return compute_pool(inputs)
        case RoundInput():
            return compute_round(inputs)
        case DilutionInput():
            return compute_dilution(inputs)
        case VestingInput():
            return compute_vesting(inputs)
        case WaterfallInput():
            return compute_waterfall(inputs)
        case _:
            assert_never(inputs)
