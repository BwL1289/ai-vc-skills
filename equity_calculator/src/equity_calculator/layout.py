"""The report of any scenario's result, shared by the printed report (``text``) and the workbook (``workbook``).

``sheet_for`` picks the scenario's sheet builder (``layout_pg``, ``layout_pool``, …, ``layout_deal_check``,
``layout_runway_plan``, ``layout_metrics_check``, ``layout_market_sizing``, ``layout_instrument_compare``); the parts
a sheet is built from (``Line``, ``Sheet``) live in ``sheet_parts`` and are re-exported here for callers that read a
report.
"""

from __future__ import annotations

from typing import assert_never

from equity_calculator.layout_deal_check import deal_check_sheet
from equity_calculator.layout_dilution import dilution_sheet
from equity_calculator.layout_instrument_compare import instrument_compare_sheet
from equity_calculator.layout_market_sizing import market_sizing_sheet
from equity_calculator.layout_metrics_check import metrics_check_sheet
from equity_calculator.layout_pg import employee_sheet, investor_sheet
from equity_calculator.layout_pool import pool_sheet
from equity_calculator.layout_round import round_sheet
from equity_calculator.layout_runway_plan import runway_plan_sheet
from equity_calculator.layout_vesting import vesting_sheet
from equity_calculator.layout_waterfall import waterfall_sheet
from equity_calculator.schemas.equity import (
    DealCheckResult,
    DilutionResult,
    EmployeeResult,
    InstrumentCompareResult,
    InvestorResult,
    MarketSizingResult,
    MetricsCheckResult,
    PoolResult,
    RoundResult,
    RunwayPlanResult,
    ScenarioResult,
    VestingResult,
    WaterfallResult,
)
from equity_calculator.sheet_parts import GIVEN, Line, Sheet

__all__ = ["GIVEN", "Line", "Sheet", "sheet_for"]


def sheet_for(result: ScenarioResult) -> Sheet:
    """The report of any scenario's result (a new scenario adds one ``case``)."""
    match result:
        case InvestorResult():
            return investor_sheet(result)
        case EmployeeResult():
            return employee_sheet(result)
        case PoolResult():
            return pool_sheet(result)
        case RoundResult():
            return round_sheet(result)
        case DilutionResult():
            return dilution_sheet(result)
        case VestingResult():
            return vesting_sheet(result)
        case WaterfallResult():
            return waterfall_sheet(result)
        case DealCheckResult():
            return deal_check_sheet(result)
        case RunwayPlanResult():
            return runway_plan_sheet(result)
        case MetricsCheckResult():
            return metrics_check_sheet(result)
        case MarketSizingResult():
            return market_sizing_sheet(result)
        case InstrumentCompareResult():
            return instrument_compare_sheet(result)
        case _:
            assert_never(result)
