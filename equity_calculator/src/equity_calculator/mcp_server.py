"""``equity_calculator_mcp`` — the calculator as an MCP server over stdio, one tool per scenario.

    equity_calculator_mcp [--output-dir DIR]

Each scenario is one tool, ``equity_<scenario>`` (``equity_investor``, ``equity_employee``, ``equity_pool``,
``equity_round``, ``equity_dilution``, ``equity_vesting``, ``equity_waterfall``, ``equity_deal_check``,
``equity_runway_plan``, ``equity_metrics_check``, ``equity_market_sizing``, ``equity_instrument_compare``). A tool takes
one argument, ``inputs``: that scenario's input model (``equity_calculator.schemas``). It returns exactly the text
``equity_calculator <scenario> --json`` prints: the result model as JSON, exact fractions and labelled assumptions
included. An input the model refuses, or one it accepts that has no answer (``equity_calculator.errors``), comes back
as a tool error that says why. The arithmetic runs on a worker thread, so a large round never stalls the server.

With ``--output-dir DIR`` the server adds one more tool, ``equity_workbook``: it works a scenario and writes its
formatted workbook as a NEW ``.xlsx`` file inside DIR. The file name must be a bare name (no folder, no ``..``, no
leading dot, no control, format or surrogate character); a name that would land outside DIR, an existing file and a
link are refused, and so is a scenario whose answer is too large for a workbook (no file is made). While it saves,
the Excel library (openpyxl) also writes and then deletes a short-lived file in the system's temporary folder
(``TMPDIR`` if set), so that folder must be writable too; DIR receives only the new workbook. Without
``--output-dir`` the server writes nothing at all.

The package's own code reads no network, database or settings; all it takes from the environment is ``HOME``, to
expand a leading ``~`` in ``--output-dir``. The MCP SDK it runs on (``mcp`` 1.28.1) reads ``FASTMCP_*`` environment
variables, in any letter case, and a ``.env`` file in the folder the server starts in. No value there changes this
server's settings, but three things stop it at start-up: a ``.env`` the server has no permission to read, or that is
not valid text in the system's encoding (UTF-8 on most systems); any value of ``FASTMCP_DEPENDENCIES`` that is not
valid JSON, an empty one included; and a non-empty value that is not valid JSON (a bare word, say) in
``FASTMCP_TRANSPORT_SECURITY__ALLOWED_HOSTS`` or ``FASTMCP_TRANSPORT_SECURITY__ALLOWED_ORIGINS``.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import unicodedata
import warnings
from collections.abc import Awaitable, Callable, Sequence
from pathlib import Path

from openpyxl import Workbook

try:
    from mcp.server.fastmcp import FastMCP
    from mcp.server.fastmcp.exceptions import ToolError
    from mcp.types import ToolAnnotations
except ModuleNotFoundError as error:  # the optional extra is missing
    if (error.name or "").partition(".")[0] != "mcp":
        raise
    raise SystemExit("equity_calculator_mcp needs the MCP SDK: pip install 'mcp==1.28.1'") from None

from equity_calculator.errors import EquityComputeError
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import (
    DealCheckInput,
    DilutionInput,
    EmployeeInput,
    EquityInput,
    InstrumentCompareInput,
    InvestorInput,
    MarketSizingInput,
    MetricsCheckInput,
    PoolInput,
    RoundInput,
    RunwayPlanInput,
    ScenarioInput,
    VestingInput,
    WaterfallInput,
)
from equity_calculator.workbook import build_workbook

_PROG = "equity_calculator_mcp"
_SERVER_NAME = "equity_calculator"
_TOOL_PREFIX = "equity_"
_WORKBOOK_TOOL = "equity_workbook"
_JSON_INDENT = 2
# The SDK's settings class warns about its own ``lifespan`` field each time a server is made (pydantic-settings 2.16).
_LIFESPAN_WARNING = "Field 'lifespan' has an incomplete definition"
_WORKBOOK_SUFFIX = ".xlsx"
# A file name longer than this is refused (most file systems stop at 255 bytes).
_MAX_NAME_LENGTH = 255
_PATH_SEPARATORS = ("/", "\\")
# Unicode categories refused in a file name: control (Cc: U+0000 to U+001F and U+007F to U+009F, such as NUL, a line
# break or escape), format (Cf: invisible marks such as U+202E, which shows the text after it reversed) and surrogate
# (Cs: half of a UTF-16 pair, which no file system can store on its own).
_REFUSED_CATEGORIES = frozenset({"Cc", "Cf", "Cs"})
# New file only: fail on an existing name (a link included) and never follow a link in the last part.
_CREATE_FLAGS = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_BINARY", 0)
_FILE_MODE = 0o666
_OUT_OF_RANGE = "a number is outside the range the calculator can work with: use a smaller magnitude"
_DIGITS_ADVICE = (
    'Send a number with more than 15 significant digits as a JSON string ("1234567.891234567"): a JSON number with a '
    "decimal point reaches the calculator as a binary float, which keeps about 15 digits."
)
_RESULT_NOTE = (
    "Returns the exact result as JSON text, the same text `equity_calculator {scenario} --json` prints: every value, "
    "the exact fractions, and the labelled assumptions with their sources. An input with no answer comes back as a "
    "tool error that says why."
)

# Each scenario: its input model, a title and what it answers (the formula and its source in a few words).
_SCENARIOS: dict[str, tuple[type[ScenarioInput], str, str]] = {
    "investor": (
        InvestorInput,
        "Investor test (PG's equity equation)",
        'Paul Graham\'s test, "The Equity Equation" (2007): is selling a stake n worth what the deal does to the '
        "company's average outcome? Worth it when (1 - n)·m > 1, with n the stake sold (equity_percent, or "
        "investment / (pre_money + investment)) and m the outcome multiplier (outcome_multiplier, or "
        "1 + growth_percent/100). Gives the value ratio, the break-even multiplier 1/(1 - n) and the verdict.",
    ),
    "employee": (
        EmployeeInput,
        "Employee test (most a hire is worth)",
        "PG's test turned round for a hire: the most of the company worth giving someone who multiplies the average "
        "outcome by i is n = (i - 1)/i (outcome_multiplier, or 1 + gain_percent/100). Optionally checks an offered "
        "stake and PG's rule-of-thumb offer from annual_cost, valuation and margin_percent.",
    ),
    "pool": (
        PoolInput,
        "Option-pool shuffle",
        "The option-pool shuffle: a new pool sized as target_pool_percent of the company after the round, counted in "
        "the pre-money (the usual term sheet) or the post-money. Gives the price per share, the new pool and investor "
        "shares, and who owns what after the round.",
    ),
    "round": (
        RoundInput,
        "Priced round with SAFEs and notes",
        "A priced round with YC post-money SAFEs and convertible notes converting (caps, discounts, MFN, interest): "
        "the price per share, which instruments take their cap, each conversion and the cap table after the round.",
    ),
    "dilution": (
        DilutionInput,
        "Dilution through rounds",
        "One holder's stake through a series of rounds: h_k = h_(k-1)·(1 - n_k - p_k), with n_k the share each round "
        "sells and p_k the new pool it adds.",
    ),
    "vesting": (
        VestingInput,
        "Vesting at a month",
        "A grant vesting by month: the cliff, a termination month, single- or double-trigger acceleration, and the "
        "value above the strike price at a common price.",
    ),
    "waterfall": (
        WaterfallInput,
        "Exit waterfall",
        "Who gets what of an exit: liquidation preferences paid by rank (multiples, caps, participation), then each "
        "preferred class's best response, convert to common or keep its preference.",
    ),
    "deal_check": (
        DealCheckInput,
        "Deal check (your raise as a VC will read it)",
        "A founder's fundraising ask checked before a VC does: post-money = pre_money + investment (or the pre-money "
        "worked from post_money or stated_investor_percent), the share the investor really gets (pool timing, SAFEs "
        "and notes counted), one holder group's stake after the round (holder_percent), the effective pre-money and "
        "what the pre-money pays for, runway = (cash_on_hand + investment) / monthly net burn on the planned and "
        "current figures, and the use_of_funds total. Each figure the deck states comes back consistent or a "
        "mismatch with its difference. A stated_investor_percent, stated_holder_percent or stated_runway_months row "
        "also says whether the stated figure is the computed one rounded half away from zero to the places it is "
        "typed with, which makes it consistent even past the tolerance (send it as text, those places as the deck "
        "writes them); the post-money and the use_of_funds total keep the tolerance alone. Flags name what a VC is "
        "likely to ask, a figure consistent by the tolerance alone among them, and never change a verdict.",
    ),
    "runway_plan": (
        RunwayPlanInput,
        "Runway plan (how long a raise lasts, and what it buys)",
        "A founder's runway on their own phased plan, cash only (no valuation or ownership): cases (the plan's "
        "phases of monthly gross_burn and revenue from each from_month, plus a downside or lean case as its own "
        "phases or as revenue_percent_of_plan / gross_burn_percent_of_plan), raises (amount landing after "
        "lands_month whole months) and milestones (months from today). Runway is when cash_on_hand + the raise - "
        "cash_floor first goes below zero under the phased net burn, worked exactly segment by segment; a no-raise "
        "row is always included. Each milestone is covered when the runway reaches its month + months_to_raise, "
        "with the slack; the smallest raise per milestone and landing month is max(0, max cumulative net burn on "
        "[landing, target] - available cash), none when the cash runs out first. Stated runways (no raise, or per "
        "raise from today or from landing) and each raise's use_of_funds total come back consistent or a mismatch; "
        "a runway stated from landing is not checked when the cash runs out before the money lands. Each "
        "stated_runway_months row also says whether the stated runway is the computed one rounded half away from "
        "zero to the places it is typed with, which makes it consistent even past the tolerance (send it as text, "
        "those places as the founder writes them); the use_of_funds total keeps the tolerance alone. The phases, "
        "percents, milestones, months_to_raise and lands_month are the founder's figures: never assume one. Flags "
        "name what to be ready to answer, a runway consistent by the tolerance alone among them, and never change a "
        "verdict.",
    ),
    "metrics_check": (
        MetricsCheckInput,
        "Metrics check (ARR, retention, churn, CAC payback, burn multiple, LTV, Rule of 40, magic number)",
        "A founder's traction metrics worked exactly from their parts over one period_months, and each figure the "
        "document states checked. Recurring revenue in recurring_unit (monthly or annual; k = 12 or 1, the only "
        "conversion): starting_recurring S and the period's new N, expansion E, contraction C and churned X. ARR at "
        "the end = k(S + N + E - C - X), net new ARR = k(N + E - C - X); the latest month's ARR = 12(month_total - "
        "one_time - usage) against its run-rate 12 x month_total. Gross revenue retention (S - C - X)/S and net "
        "(S + E - C - X)/S, on the cohort_* movements of the starting customers when given, over the period and "
        "never annualised; gross revenue churn (C + X)/S, net (C + X - E)/S, logo churn customers_lost / "
        "customers_start. CAC = sales_marketing_spend / customers_new (paid: / customers_new_paid); CAC payback = "
        "spend / (new monthly recurring x gross margin), and on revenue only; burn multiple = net_burn / net new "
        "ARR (none at or below zero); concentration = largest_customer_revenue / period_revenue. LTV = arpa (in "
        "recurring_unit, scaled to the period) x the contribution_margin_percent, else gross_margin_percent (flagged), "
        "/ the period's churn on ltv_churn_basis (gross_revenue unless given; a churn at or below 0, or no margin, is "
        "refused); LTV/CAC = LTV / blended CAC. Rule of 40 = revenue_growth_percent + profit_margin_percent, both the "
        "founder's, added as given, with profit_margin_basis naming the margin (unlabelled is flagged). Magic number "
        "= 4 x (quarter_revenue - prior_quarter_revenue) / prior_quarter_sales_marketing_spend, or on ARR "
        "(quarter_ending_arr - prior_quarter_ending_arr) / that spend with no 4; magic_number_variant names which. No "
        "benchmark for LTV/CAC, the Rule of 40 or the magic number. Each stated_* "
        "figure comes back consistent or a mismatch, or not_checked for a stated burn multiple with no multiple to "
        "work (the overall verdict is then never consistent); a stated ARR against the movement's ending ARR or the "
        "latest month's, whichever it is within the tolerance of (arr_basis names it); a churn with no basis once per "
        "basis, a churn below 0 only as net revenue churn; a stated retention or churn over period_months, so set it "
        "to the period the document's figure covers, 1 for a monthly churn, 12 for an annual NRR, one call per "
        "period. Each percent, "
        "months or multiple row also says whether the stated figure is the computed one rounded half away from zero to "
        "the places it is typed with, which makes it consistent even past the tolerance (send it as text, those "
        "places as the document writes them). Flags name the likely cause of a mismatch (a run-rate called ARR, new "
        "customers in NRR, payback on revenue, new not net new ARR, an LTV or LTV/CAC on revenue, a Rule of 40 on "
        "gross margin, a magic number without its 4), a figure consistent by the tolerance alone, a "
        "movement and latest month that disagree, "
        "and three benchmark questions (payback by customer_segment, burn multiple 3x, monthly net revenue churn "
        "2%), never errors. Every part is the founder's figure: never assume one.",
    ),
    "market_sizing": (
        MarketSizingInput,
        "Market sizing (TAM, SAM and SOM bottom-up, with a cross-check and sensitivity)",
        "A founder's market size worked exactly from their own segments (one to eight, numbered in order, no names). "
        "Per segment: value = price x 12 / price_period_months x units_per_customer x take_rate_percent/100 (the "
        "annual revenue from one buying customer; price_period_months left out is 12, a yearly price, and is flagged: "
        "send 1 for a monthly price); gross spend = customers x price x 12 / price_period_months x units_per_customer "
        "(before the take rate); TAM = customers x value; SAM = customers x serviceable_percent/100 x value; SOM = "
        "obtainable_customers (preferred) or SAM customers x obtainable_percent/100, x value. Totals are sums (SOM "
        "only when every segment gives one). The path: SOM customers / customers_today and (SOM customers - "
        "customers_today) / som_years a year, a straight line, no compound rate. Each top_down figure (amount x "
        "comparable_percent/100) is set beside the bottom-up TAM or SAM as a cross-check, never a verdict. stated_tam, "
        "stated_sam and stated_som come back consistent or a mismatch within tolerance_percent. Each sensitivity row "
        "works one field of one segment at the founder's own values, the rest at base, with the SOM range and swing "
        "and the exact value at which SOM reaches som_target (does_not_move first, for a field that is no factor of "
        "SOM; else met_without_it when the base SOM already reaches it) and the total reaches the first top-down "
        "figure. A unit price prints to the cent when exact, else with the places it needs ($0.0075). Flags name a "
        "price period left out, double counting, a SOM given only as a share, no horizon, a SOM below the target and "
        "a target no row reaches, never errors. Every count, price, share and figure is the founder's: never assume "
        "or look one up.",
    ),
    "instrument_compare": (
        InstrumentCompareInput,
        "Priced round now vs a convertible note now (side by side, never a pick)",
        "A founder choosing between a priced round now (option A: priced_pre_money, any priced_target_pool_percent, "
        "priced_preference) and a convertible note now (option B, the same investment: note_valuation_cap, "
        "note_discount_percent, note_interest_rate_percent, note_compounding, note_months_to_conversion) for the "
        "same raise, from today's cap table by holder group (founder_shares, team_shares, unissued_pool_shares, "
        "existing_series, existing_instruments). Each next_rounds scenario (pre_money, investment, any "
        "target_pool_percent, preference) is the same for both: A prices it on A's shares, B's note converts in it "
        "at the lower of its cap price (cap / today's fully diluted shares) and discount price (round price x (1 - "
        "discount)), interest included unless paid in cash. Gives, A beside B with B - A: ownership by group right "
        "after today (B's note outstanding, no shares), after each next round, and each group's payout at each of "
        "exit_amounts after it through the exit waterfall with every series' preference honoured (converted shares "
        "take their round's series terms, a preference on the amount converted). A series' preference is the "
        "founder's terms, or standard (1x, non-participating) only when the founder says standard; an existing "
        "series gives its own preference_multiple and participation, and an existing note its compounding. Flags "
        "(the note on its cap or discount, a cap below today's price, interest converting or paid in cash, maturity "
        "not given or before conversion, a next round below A's price, A's price below an existing series', an "
        "existing MFN SAFE beside the note) never pick an option. No next round is refused (no_next_round_given). "
        "Every term is the founder's: never assume one.",
    ),
}

_INSTRUCTIONS = (
    "Exact startup-equity arithmetic. Pick the tool for the question: equity_investor (should we sell stock for this "
    "deal?), equity_employee (the most a hire is worth), equity_pool (option-pool shuffle), equity_round (priced "
    "round with SAFEs and notes), equity_dilution (one holder through rounds), equity_vesting (a grant at a month), "
    "equity_waterfall (who gets what of an exit), equity_deal_check (a founder's raise checked: valuation, ownership "
    "after the round, runway, the deck's own figures), equity_runway_plan (how long each raise lasts on a phased "
    "plan and a downside, which milestones it reaches, the smallest raise that gets there), equity_metrics_check "
    "(a founder's ARR, retention, churn, CAC payback, burn multiple, concentration, LTV, LTV/CAC, Rule of 40 and magic "
    "number worked from their parts and checked against the document's figures), equity_market_sizing (a founder's "
    "TAM, SAM and SOM built bottom-up from their own segments, checked against the deck, set beside any top-down "
    "figure, with ranges), "
    "equity_instrument_compare (a priced round now beside a convertible note now: ownership after today and after "
    "each next round, and each exit's payouts, side by side, never a pick). Pass the "
    "scenario's fields in `inputs`; give money and percents as JSON strings to keep every digit. Quote the result's "
    "numbers and its labelled assumptions; never round them further without saying so. A value whose unit is "
    "fraction is a share of the whole: show it as a percent by moving the decimal point of its rounded value two "
    "places to the right (0.166667 is 16.6667%), as the command line's report prints it."
)


def _refusal(error: ArithmeticError | ValueError) -> ToolError:
    """The tool error for an accepted input that has no answer, or for a number too large to work."""
    if isinstance(error, EquityComputeError):
        return ToolError(f"no answer for these inputs: {error}")

    # Inputs inside the models' bounds can still overflow a step (an integer too long to print is a ValueError, a
    # rounding past the decimal context an ArithmeticError); Python's own message would not help the caller.
    return ToolError(_OUT_OF_RANGE)


def _work(inputs: ScenarioInput) -> str:
    """The result of ``inputs`` as the CLI's ``--json`` text (blocking: run on a worker thread)."""
    try:
        return compute(inputs).model_dump_json(indent=_JSON_INDENT)
    except (ArithmeticError, ValueError) as error:  # EquityComputeError is a ValueError
        raise _refusal(error) from None


def _workbook(inputs: ScenarioInput) -> Workbook:
    """The formatted workbook of ``inputs``, built in memory (blocking: run on a worker thread).

    Building it before the file is made means an input with no answer, or one whose answer is too large for a
    workbook (``ResultOutOfRange``), is refused with no file left behind.
    """
    try:
        return build_workbook([sheet_for(compute(inputs))])
    except (ArithmeticError, ValueError) as error:  # ResultOutOfRange is an EquityComputeError, a ValueError
        raise _refusal(error) from None


def _scenario_tool(model: type[ScenarioInput]) -> Callable[[ScenarioInput], Awaitable[str]]:
    """The tool function for one scenario: its ``inputs`` argument is annotated with that scenario's model."""

    async def tool(inputs: ScenarioInput) -> str:
        return await asyncio.to_thread(_work, inputs)

    # The SDK builds each tool's argument schema from its annotations: give this one the scenario's own model.
    tool.__annotations__ = {"inputs": model, "return": str}

    return tool


def _workbook_name(file_name: str) -> str:
    """``file_name`` when it is a bare ``.xlsx`` name; a ``ToolError`` saying what is wrong otherwise."""
    if not file_name or len(file_name) > _MAX_NAME_LENGTH:
        raise ToolError(f"file_name must be 1 to {_MAX_NAME_LENGTH} characters")
    # The name is not echoed back: a control or format character could rewrite a terminal or a log line that shows it.
    if any(unicodedata.category(character) in _REFUSED_CATEGORIES for character in file_name):
        raise ToolError(
            "file_name must not contain a control, format or surrogate character (such as a line break, U+202E or a "
            "lone U+D800)"
        )
    if any(separator in file_name for separator in _PATH_SEPARATORS) or Path(file_name).name != file_name:
        raise ToolError("file_name must be a bare file name, with no folder: the file is written in the output folder")
    if file_name.startswith("."):
        raise ToolError("file_name must not start with a dot")
    if not file_name.lower().endswith(_WORKBOOK_SUFFIX) or len(file_name) == len(_WORKBOOK_SUFFIX):
        raise ToolError(f"file_name must end in {_WORKBOOK_SUFFIX}, as in round.xlsx")

    return file_name


def _write_workbook(folder: Path, file_name: str, inputs: ScenarioInput) -> Path:
    """Work ``inputs`` and write its workbook as the new file ``folder/file_name`` (blocking: run on a worker thread).

    The workbook is built first, so a refused input creates nothing. The file is created with ``O_EXCL`` (an existing
    name, a link included, is refused) and ``O_NOFOLLOW``; a write that fails part way removes the file it created.
    openpyxl's save also uses a short-lived file in the system's temporary folder, which it deletes.
    """
    target = folder / file_name
    if Path(os.path.realpath(target.parent)) != folder:
        raise ToolError("the output folder has moved since the server started; restart the server")
    workbook = _workbook(inputs)
    try:
        descriptor = os.open(target, _CREATE_FLAGS, _FILE_MODE)
    except FileExistsError:
        raise ToolError(f"{file_name} already exists in the output folder: choose a new name") from None
    except OSError as error:
        raise ToolError(f"cannot create {file_name} ({error.strerror or type(error).__name__})") from None

    try:
        with os.fdopen(descriptor, "wb") as handle:
            workbook.save(handle)
    except BaseException as error:
        target.unlink(missing_ok=True)
        if isinstance(error, OSError):
            raise ToolError(f"cannot write {file_name} ({error.strerror or type(error).__name__})") from None
        raise

    return target


def _workbook_tool(folder: Path) -> Callable[[EquityInput, str], Awaitable[str]]:
    """The ``equity_workbook`` tool, bound to the output folder."""

    async def tool(inputs: EquityInput, file_name: str) -> str:
        name = _workbook_name(file_name)
        written = await asyncio.to_thread(_write_workbook, folder, name, inputs)

        return f"Wrote {written} (the {inputs.scenario} scenario's workbook, one sheet)."

    tool.__annotations__ = {"inputs": EquityInput, "file_name": str, "return": str}

    return tool


def _output_folder(path: Path) -> Path:
    """``path`` made if missing and resolved to its real, absolute folder (links followed once, at start-up)."""
    try:
        path.expanduser().mkdir(parents=True, exist_ok=True)
        folder = path.expanduser().resolve(strict=True)
    except OSError as error:
        raise SystemExit(
            f"{_PROG}: --output-dir {path} is not a folder that can be made or used ({error.strerror})"
        ) from error
    if not folder.is_dir():
        raise SystemExit(f"{_PROG}: --output-dir {path} is not a folder")

    return folder


def _settings_warning() -> type[Warning]:
    """The class of the SDK's settings warning, or ``UserWarning`` on a pydantic-settings without that class."""
    try:
        from pydantic_settings import IncompleteFieldDefinitionWarning
    except ImportError:
        return UserWarning

    return IncompleteFieldDefinitionWarning


def build_server(output_dir: Path | None = None) -> FastMCP:
    """The server: one read-only tool per scenario, plus ``equity_workbook`` when ``output_dir`` is given."""
    # That warning is about the SDK, not this server, and would print on every start: silence it, and only it.
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", message=_LIFESPAN_WARNING, category=_settings_warning())
        server = FastMCP(_SERVER_NAME, instructions=_INSTRUCTIONS, log_level="WARNING")
    read_only = ToolAnnotations(readOnlyHint=True, idempotentHint=True, openWorldHint=False)
    for scenario, (model, title, what) in _SCENARIOS.items():
        description = f"{what}\n\n{_RESULT_NOTE.format(scenario=scenario)}\n\n{_DIGITS_ADVICE}"
        server.add_tool(
            _scenario_tool(model),
            name=f"{_TOOL_PREFIX}{scenario}",
            title=title,
            description=description,
            annotations=read_only,
            structured_output=False,
        )

    if output_dir is not None:
        folder = _output_folder(output_dir)
        server.add_tool(
            _workbook_tool(folder),
            name=_WORKBOOK_TOOL,
            title="Write a scenario's Excel workbook",
            description=(
                f"Works out any scenario and writes its formatted Excel workbook (real formulas, number formats) "
                f"as a NEW file in the server's output folder, {folder}. The workbook is written ONLY inside that "
                f"folder (while saving, the Excel library also writes and deletes a short-lived file in the system's "
                f"temporary folder): `file_name` must be a bare name ending in .xlsx (no folder, no '..', no leading "
                f"dot, no control, format or surrogate character), and a name that would land outside the folder, an "
                f"existing file, a link or an answer too large for a workbook is refused. `inputs` is any "
                f'scenario\'s input with its `scenario` tag set ("investor", "employee", "pool", "round", "dilution", '
                f'"vesting", "waterfall", "deal_check", "runway_plan", "metrics_check", "market_sizing" or '
                f'"instrument_compare"). Returns '
                f"the path written. {_DIGITS_ADVICE}"
            ),
            annotations=ToolAnnotations(
                readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False
            ),
            structured_output=False,
        )

    return server


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for ``equity_calculator_mcp``: serve over stdio until the client closes it."""
    parser = argparse.ArgumentParser(prog=_PROG, description="The equity calculator as an MCP server over stdio.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        help=(
            "Add the equity_workbook tool, which writes new .xlsx files only inside this folder (made if missing); "
            "a save also uses a short-lived file in the system's temporary folder, which must be writable."
        ),
    )
    args = parser.parse_args(argv)
    build_server(args.output_dir).run("stdio")


if __name__ == "__main__":
    main()
