"""The equity calculator: should we trade stock, and what does a round do to the cap table?

Built from the ``equity_equation`` script this repository first held (``src/equity_equation/``, now in its git history)
and the essay it implements, Paul Graham's "The Equity Equation" (July 2007). Every number is exact (``Fraction``
inside, ``Decimal`` in and out); the input and result models live in ``equity_calculator.schemas.equity`` and the
``equity_calculator.schemas.equity_*`` modules it re-exports (``equity_common``, ``equity_pool``, ``equity_round``,
``equity_dilution``, ``equity_vesting``, ``equity_waterfall``, ``equity_deal_check``, ``equity_runway_plan``,
``equity_metrics_check``, ``equity_market_sizing``, ``equity_instrument_compare``, ``equity_pool_plan``,
``equity_raise_pipeline``).

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
  - ``deal_check``  — a fundraising ask checked against itself: valuation, ownership after the round, runway, checks;
  - ``assumptions_deal_check`` — the deal check's labelled assumptions (post = pre + raise from YC, the rest
    unverified);
  - ``funds``       — a raise's use-of-funds lines worked and checked, shared by the deal check and the runway plan;
  - ``runway_plan`` — how long each raise lasts on a phased plan and its cases, milestones, the smallest raise;
  - ``assumptions_runway_plan`` — the runway plan's labelled assumptions (the YC seed guide's milestone and band,
    the rest unverified);
  - ``metrics_check`` — traction metrics worked from their parts: ARR, retention, churn, CAC, payback, burn multiple;
  - ``assumptions_metrics_check`` — the metrics check's labelled assumptions (a16z, Bessemer, Sacks and Skok quoted,
    the rest unverified);
  - ``market_sizing`` — a market built bottom-up: TAM, SAM and SOM per segment, a top-down cross-check, the checks,
    each sensitivity row and its exact break-even value;
  - ``assumptions_market_sizing`` — the market size's labelled assumptions (two YC pages quoted, the rest unverified);
  - ``instrument_compare`` — a priced round now beside a convertible note now: ownership after today and after each
    next round, and each exit's payouts, with B - A, worked through the round and waterfall code;
  - ``assumptions_instrument_compare`` — the comparison's labelled assumptions (the round's and the waterfall's rows
    reused, its own unverified);
  - ``pool_plan``   — the pool a hiring plan needs to the next round beside a term sheet's requested pool, both
    worked through the pool code, with requested - plan;
  - ``assumptions_pool_plan`` — the pool plan's labelled assumptions (the pool's rows reused, its own unverified);
  - ``raise_pipeline`` — a founder's round: the allocation left, the term sheets their funnel is expected to give,
    the targets needed, and the start-raising month from the runway plan;
  - ``assumptions_raise_pipeline`` — the pipeline's labelled assumptions (its own unverified, the runway plan's
    reused);
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
  - ``layout_deal_check`` — the report lines of a deal check (the Deal check sheet);
  - ``layout_runway_plan`` — the report lines of a runway plan (the Runway plan sheet);
  - ``layout_metrics_check`` — the report lines of a metrics check (the Metrics check sheet);
  - ``layout_market_sizing`` — the report lines of a market size (the Market sizing sheet);
  - ``layout_instrument_compare`` — the report lines of the comparison (the Priced vs note sheet);
  - ``layout_pool_plan`` — the report lines of a pool plan (the Pool plan sheet);
  - ``layout_raise_pipeline`` — the report lines of a raise pipeline (the Raise pipeline sheet);
  - ``text``        — the CLI's printed report;
  - ``workbook``    — the formatted Excel workbook (real formulas, number formats, verdict colours);
  - ``cli_numbers`` — the CLI's number readers (amounts, percents, whole counts, customers, investors, the workbook
    path);
  - ``cli_arguments`` — each scenario's CLI flags;
  - ``cli_instruments`` — the repeated-flag readers: ``--safe``, ``--note``, ``--round``, ``--class``, ``--phase``,
    ``--raise``, the use-of-funds lines, ``--segment``, ``--top-down``, ``--sensitivity``, ``--priced-preference``,
    ``--next-round``, ``--hire``, ``--commitment`` and ``--stage``;
  - ``cli_runway_plan`` — a runway plan's flags gathered into its cases and raises, and where each came from;
  - ``cli_raise_pipeline`` — a raise pipeline's cash and burn flags gathered into its runway;
  - ``__main__``    — the CLI, ``equity_calculator investor|employee|pool|round|dilution|vesting|waterfall|deal_check|
    runway_plan|metrics_check|market_sizing|instrument_compare|pool_plan|raise_pipeline [--json] [--xlsx PATH]``;
  - ``mcp_server``  — the MCP server, ``equity_calculator_mcp [--output-dir DIR]``: one tool per scenario over stdio.

Nothing here reads the network or a database; it is pure arithmetic plus the workbook writes: the CLI's ``--xlsx``
file and the MCP server's ``equity_workbook`` tool, which makes files only inside its ``--output-dir`` folder.
While saving, the Excel library also writes and deletes a short-lived file in the system's temporary folder
(``TMPDIR`` if set), so that folder must be writable. ``mcp_server`` says what the MCP SDK under the server reads
from the environment.
"""
