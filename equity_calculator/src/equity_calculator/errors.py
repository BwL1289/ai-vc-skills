"""The named errors ``compute`` can raise on an input its model accepted: a round with no price, a search that ran out.

Every model refuses what it can check alone (a negative amount, a pool too big for any price). A few inputs pass
that check and still have no answer: SAFEs and notes whose conversions leave no positive price, or a search that
does not settle within its stated bound. Those raise one of the errors below, never a bare traceback, so the CLI
prints the reason and the MCP server can answer it as a refused input. Each is a ``ValueError``.
``ResultOutOfRange`` is raised by the workbook writer, and by ``equity_calculator.result_range.check_result_range``
for a caller that runs it, when an answer holds a value too large for a spreadsheet cell.
"""

from __future__ import annotations

__all__ = [
    "ConversionDidNotSettle",
    "EquityComputeError",
    "NoConversionEquilibrium",
    "ResultOutOfRange",
    "RoundHasNoPrice",
]


class EquityComputeError(ValueError):
    """An input the model accepted that has no answer; the message says why, in plain words."""


class RoundHasNoPrice(EquityComputeError):
    """The SAFEs, notes and pool target together leave no positive price per share for the new money."""


class ConversionDidNotSettle(EquityComputeError):
    """The search for which SAFEs and notes convert at their cap did not settle within its pass limit."""


class NoConversionEquilibrium(EquityComputeError):
    """No choice of which preferred classes convert to common leaves every class content (the exit waterfall)."""


class ResultOutOfRange(EquityComputeError):
    """The answer holds a value too large for a workbook cell (``equity_calculator.result_range``)."""
