"""The equity calculator: should we trade stock, and what does a round do to the cap table?

Built from the ``equity_equation`` script this repository first held (``src/equity_equation/``, now in its git history)
and the essay it implements, Paul Graham's "The Equity Equation" (July 2007). Every number is exact (``Fraction``
inside, ``Decimal`` in and out); the input and result models live in ``equity_calculator.schemas.equity`` and the
``equity_calculator.schemas.equity_*`` modules it re-exports (``equity_common``, ``equity_pool``, ``equity_round``,
``equity_dilution``, ``equity_vesting``, ``equity_waterfall``).

  - ``exact``       — exact arithmetic, display rounding, the money split that adds up to the cent;
  - ``equation``    — PG's test, R = (1 - n)·m, and its inverse for a hire, n = (i - 1)/i;
  - ``assumptions`` — the labelled assumptions every result carries, each with its source;
  - ``investor``    — the investor test (sell n of the company for a deal that multiplies the outcome by m?);
  - ``employee``    — the employee test (the most a hire is worth) and PG's rule-of-thumb offer;
  - ``pool``        — the option-pool shuffle, the pool counted pre-money and post-money;
  - ``errors``      — the named errors ``compute`` raises on an accepted input with no answer;
  - ``interest``    — a convertible note's interest (simple, annual or monthly, months or dates, day count);
  - ``convertibles`` — a priced round's price and which SAFEs and notes take their cap (``settle``);
  - ``round``       — a priced round with post-money SAFEs and notes: each conversion and the cap table after;
  - ``assumptions_round`` — the round's labelled assumptions, the YC SAFE rules quoted word for word;
  - ``dilution``    — one holder's stake through a series of rounds, h_k = h_{k-1}·(1 - n_k - p_k);
  - ``vesting``     — a grant vesting by month (cliff, termination, single- or double-trigger acceleration);
  - ``assumptions_holder`` — the labelled assumptions of dilution and vesting;
  - ``waterfall``   — an exit waterfall: preferences by rank, then each class's convert-or-stay best response;
  - ``assumptions_waterfall`` — the waterfall's labelled assumptions (all marked unverified);
  - ``scenarios``   — ``compute``: any scenario's input to its result;
  - ``result_range`` — the size limit on an answer: no value a spreadsheet cell cannot hold reaches a workbook;
  - ``sheet_parts`` — ``Line`` and ``Sheet``, the parts every report is built from;
  - ``layout``      — ``sheet_for``: any result's report (lines, units, how each is computed) for text and workbook;
  - ``layout_pg``   — the report lines of the investor and employee tests;
  - ``layout_pool`` — the report lines of the option-pool shuffle;
  - ``layout_round`` — the report lines of the round (the Convertibles sheet);
  - ``layout_dilution`` — the report lines of dilution through rounds (the Dilution sheet);
  - ``layout_vesting`` — the report lines of a grant's vesting (the Vesting sheet);
  - ``layout_waterfall`` — the report lines of an exit waterfall (the Waterfall sheet);
  - ``text``        — the CLI's printed report;
  - ``workbook``    — the formatted Excel workbook (real formulas, number formats, verdict colours);
  - ``cli_numbers`` — the CLI's number readers (amounts, percents, whole counts, the workbook path);
  - ``cli_arguments`` — each scenario's CLI flags;
  - ``cli_instruments`` — the repeated-flag readers: ``--safe``, ``--note``, ``--round`` and ``--class``;
  - ``__main__``    — the CLI, ``equity_calculator investor|employee|pool|round|dilution|vesting|waterfall
    [--json] [--xlsx PATH]``;
  - ``mcp_server``  — the MCP server, ``equity_calculator_mcp [--output-dir DIR]``: one tool per scenario over stdio.

Nothing here reads the network or a database; it is pure arithmetic plus the workbook writes: the CLI's ``--xlsx``
file and the MCP server's ``equity_workbook`` tool, which makes files only inside its ``--output-dir`` folder.
While saving, the Excel library also writes and deletes a short-lived file in the system's temporary folder
(``TMPDIR`` if set), so that folder must be writable. ``mcp_server`` says what the MCP SDK under the server reads
from the environment.
"""
