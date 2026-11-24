# Command-line interface: stdout is the report.
"""``equity_calculator`` — an equity question: PG's two tests, the option pool, a round, dilution, vesting, an exit,
a fundraising ask checked before a VC reads it, how long a raise lasts on a founder's plan, a founder's traction
metrics checked against their parts, a founder's market size built bottom-up, or a priced round now set beside a
convertible note now.

    equity_calculator investor (--equity-percent N | --pre-money V --investment I)
        (--outcome-multiplier M | --growth-percent G) [--holder-percent H]
    equity_calculator employee (--outcome-multiplier I | --gain-percent G) [--offered-percent O]
        [--annual-cost C --valuation V] [--margin-percent M] [--cost-years Y]
    equity_calculator pool --fully-diluted-shares FD [--unissued-pool-shares U] --pre-money V --investment I
        --target-pool-percent T [--pool-timing pre_money|post_money] [--share-rounding exact|whole_shares]
    equity_calculator round --fully-diluted-shares FD [--unissued-pool-shares U] --pre-money V --investment I
        [--target-pool-percent T] [--pool-timing pre_money|post_money] (--safe "TERMS" | --note "TERMS")...
    equity_calculator dilution --holder-percent H (--round "TERMS")...
    equity_calculator vesting --grant-shares G --month M [--total-months T] [--cliff-months C]
        [--strike-price S [--common-price P]] [--termination-month E]
        [--acceleration single_trigger|double_trigger --acceleration-percent A --change-of-control-month C
        [--acceleration-base unvested|grant]] [--share-rounding exact|whole_shares]
    equity_calculator waterfall --exit-amount E --common-shares C (--class "TERMS")...
    equity_calculator deal_check --investment I [--pre-money V] [--post-money P] [--stated-investor-percent X]
        [--fully-diluted-shares FD [--unissued-pool-shares U | --unissued-pool-percent UP] [--target-pool-percent T]
        [--pool-timing pre_money|post_money] [--safe "TERMS" | --note "TERMS"]...]
        [(--holder-percent H | --holder-shares HS) [--stated-holder-percent S]] [--cash-on-hand C]
        [--planned-monthly-gross-burn B [--planned-monthly-revenue R]]
        [--current-monthly-gross-burn B [--current-monthly-revenue R]] [--stated-runway-months M]
        [--use-of-funds AMOUNT|PCT%]... [--tolerance-points P] [--tolerance-percent Q]
        [--dilution-band-percent D] [--runway-band-months M]
    equity_calculator runway_plan --cash-on-hand C [--cash-floor F] (--phase "TERMS")...
        [--downside-phase "TERMS"... | [--downside-revenue-percent R] [--downside-gross-burn-percent G]]
        [--lean-phase "TERMS"... | [--lean-revenue-percent R] [--lean-gross-burn-percent G]]
        [--raise "TERMS"]... [--raise-use-of-funds "N AMOUNT|PCT%"]... [--milestone M]... [--months-to-raise T]
        [--stated-runway-months S] [--tolerance-points P] [--tolerance-percent Q] [--runway-band-months B]
    equity_calculator metrics_check --period-months P [--recurring-unit monthly|annual]
        [--starting-recurring S [--new-recurring N] [--expansion-recurring E] [--contraction-recurring C]
        [--churned-recurring X] [--cohort-expansion-recurring E] [--cohort-contraction-recurring C]
        [--cohort-churned-recurring X]] [--month-total-revenue T [--month-one-time-revenue O]
        [--month-usage-revenue U]] [--customers-start S [--customers-lost L]] [--customers-new N
        [--customers-new-paid P]] [--sales-marketing-spend M [--gross-margin-percent G]] [--net-burn B]
        [--largest-customer-revenue L --period-revenue R] [--arpa A [--contribution-margin-percent M]
        [--ltv-churn-basis BASIS]] [--revenue-growth-percent G --profit-margin-percent M
        [--profit-margin-basis BASIS]] [(--quarter-revenue Q --prior-quarter-revenue Q' |
        --quarter-ending-arr A --prior-quarter-ending-arr A') --prior-quarter-sales-marketing-spend S]
        [--stated-arr A] [--stated-nrr-percent N]
        [--stated-grr-percent G] [--stated-churn-percent C [--stated-churn-basis BASIS]] [--stated-cac C]
        [--stated-cac-payback-months M] [--stated-burn-multiple X] [--stated-concentration-percent C]
        [--stated-ltv L] [--stated-ltv-to-cac X] [--stated-rule-of-40-percent R] [--stated-magic-number M]
        [--tolerance-points P] [--tolerance-percent Q] [--customer-segment smb|mid_market|enterprise]
        [--payback-band-months B] [--burn-multiple-band X] [--net-revenue-churn-band-percent C]
    equity_calculator market_sizing --segment "TERMS"... [--top-down "TERMS"]... [--sensitivity "TERMS"]...
        [--population N] [--annual-revenue-today R] [--som-years Y] [--som-target T] [--stated-tam X]
        [--stated-sam X] [--stated-som X] [--tolerance-percent Q]
    equity_calculator instrument_compare --founder-shares F --team-shares T --unissued-pool-shares U
        [--existing-series "TERMS"]... [--existing-safe "TERMS" | --existing-note "TERMS"]... --investment I
        --priced-pre-money V [--priced-target-pool-percent T] [--priced-pool-timing pre_money|post_money]
        --priced-preference "TERMS" [--note-valuation-cap K] [--note-discount-percent D]
        --note-interest-rate-percent R --note-compounding simple|annual|monthly [--note-stub-rule RULE]
        --note-months-to-conversion M [--note-maturity-months M] [--note-interest-paid-in-cash]
        (--next-round "TERMS")... (--exit E)... [--pool-at-exit as_common|left_out]

Every scenario also takes ``--json`` (print the whole result model, exact fractions included, instead of the
report) and ``--xlsx PATH`` (also write the formatted workbook to PATH; the report then names it). The report is
the command's whole output, so it goes to stdout. Numbers may carry ``$``, ``_`` and commas that separate thousands
(``$8,000,000``). A comma before exactly three digits, after a first group that does not start with 0, is always read
as thousands, so ``1,250`` is 1250; any other comma (``7,5``, ``0,500``, ``8,00,000``) is refused. A percent may
carry ``%`` (a negative one then needs ``=``, as in ``--growth-percent=-10%``, since argparse reads a lone ``-10%``
as a flag). Its own code reads no network, database or environment variable (Python's standard library reads a few, such
as ``COLUMNS`` to wrap the help, none of which changes a number); its one output file is ``--xlsx``, which also makes
any folders on its path that do not exist yet; while saving, the Excel library also writes and deletes a short-lived
file in the system's temporary folder (``TMPDIR`` if set), so that folder must be writable. The number readers are
``equity_calculator.cli_numbers``; each scenario's flags are ``equity_calculator.cli_arguments``; a ``--safe``,
``--note``, ``--round``, ``--class``, ``--use-of-funds``, ``--phase``, ``--raise``, ``--raise-use-of-funds``,
``--segment``, ``--top-down``, ``--sensitivity``, ``--priced-preference`` or ``--next-round`` is one argument of
terms (``equity_calculator.cli_instruments``); a runway plan's flags become its cases and raises in
``equity_calculator.cli_runway_plan``. A refusal names the flag,
or a repeated flag's item as ``--note #2`` (the second instrument in the order given) and its term.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any, get_args

from equity_calculator.cli_arguments import (
    deal_check_arguments,
    dilution_arguments,
    employee_arguments,
    instrument_compare_arguments,
    investor_arguments,
    market_sizing_arguments,
    metrics_check_arguments,
    pool_arguments,
    round_arguments,
    runway_plan_arguments,
    vesting_arguments,
    waterfall_arguments,
)
from equity_calculator.cli_numbers import parse_workbook_path
from equity_calculator.cli_runway_plan import Places, runway_plan_fields
from equity_calculator.errors import EquityComputeError
from equity_calculator.layout import sheet_for
from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import (
    DealCheckInput,
    DilutionInput,
    EmployeeInput,
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
from equity_calculator.text import render_sheet
from equity_calculator.workbook import save_workbook
from pydantic import BaseModel, ValidationError

_PROG = "equity_calculator"
_VALUE_ERROR_PREFIX = "Value error, "
_JSON_INDENT = 2
_INPUT_MODELS: dict[str, type[ScenarioInput]] = {
    "investor": InvestorInput,
    "employee": EmployeeInput,
    "pool": PoolInput,
    "round": RoundInput,
    "dilution": DilutionInput,
    "vesting": VestingInput,
    "waterfall": WaterfallInput,
    "deal_check": DealCheckInput,
    "runway_plan": RunwayPlanInput,
    "metrics_check": MetricsCheckInput,
    "market_sizing": MarketSizingInput,
    "instrument_compare": InstrumentCompareInput,
}
# A scenario whose flags do not map one to one onto its model's fields: the fields they make, and where each came from.
_SHAPES: dict[str, Callable[[dict[str, Any]], tuple[dict[str, object], Places]]] = {"runway_plan": runway_plan_fields}
_OUTPUT_FLAGS = ("json", "xlsx")
_FIRST = 0
_TOO_SHORT = "too_short"
_FLAG_JOIN = "/"
# A repeated flag's items are numbered from 1 in a refusal, in the order given.
_ORDINAL_START = 1


def _build_parser() -> argparse.ArgumentParser:
    outputs = argparse.ArgumentParser(add_help=False)
    outputs.add_argument("--json", action="store_true", help="Print the whole result as JSON instead of the report.")
    outputs.add_argument(
        "--xlsx", type=parse_workbook_path, help="Also write the formatted workbook to this .xlsx path."
    )

    parser = argparse.ArgumentParser(
        prog=_PROG,
        description="Should we trade stock, what does a round do to the cap table, who gets what of an exit? "
        "Exact arithmetic; reads nothing; writes the --xlsx file (and missing folders) using a short-lived temp file.",
    )
    scenarios = parser.add_subparsers(dest="scenario", required=True)
    scenarios_help = (
        ("investor", "Paul Graham's test: is the stake worth what the deal adds? R = (1 - n)·m", investor_arguments),
        ("employee", "The most of the company a hire is worth, n = (i - 1)/i, and PG's offer", employee_arguments),
        ("pool", "The option-pool shuffle: price, new shares, who owns what", pool_arguments),
        ("round", "A priced round with post-money SAFEs and notes converting: price, cap table", round_arguments),
        ("dilution", "One holder's stake through rounds: h_k = h_(k-1)·(1 - n_k - p_k)", dilution_arguments),
        ("vesting", "A grant at a month: cliff, termination, acceleration, value above the strike", vesting_arguments),
        ("waterfall", "Who gets what of an exit: preferences by rank, each class converts or not", waterfall_arguments),
        (
            "deal_check",
            "Check your raise before a VC does: valuation, ownership after the round, runway, the deck's figures",
            deal_check_arguments,
        ),
        (
            "runway_plan",
            "How long each raise lasts on your plan and a downside, which milestones it reaches, how much is needed",
            runway_plan_arguments,
        ),
        (
            "metrics_check",
            "Check your traction metrics before a VC does: ARR, retention, churn, CAC payback, burn multiple, LTV, "
            "Rule of 40, magic number",
            metrics_check_arguments,
        ),
        (
            "market_sizing",
            "Build your market size bottom-up before a VC does: TAM, SAM and SOM per segment, the deck's figures "
            "checked, and the ranges that move it",
            market_sizing_arguments,
        ),
        (
            "instrument_compare",
            "A priced round now beside a convertible note now: who owns what after today and after each next "
            "round, and who gets what at each exit, B - A; never a recommendation",
            instrument_compare_arguments,
        ),
    )
    for name, summary, add_arguments in scenarios_help:
        add_arguments(scenarios.add_parser(name, parents=[outputs], help=summary, description=summary))

    return parser


def _flags_by_field(parser: argparse.ArgumentParser, scenario: str) -> dict[str, str]:
    """``scenario``'s model fields and the flags that fill them (``instruments``: ``--safe/--note``)."""
    subparsers = next(action for action in parser._actions if isinstance(action, argparse._SubParsersAction))
    flags: dict[str, list[str]] = {}
    for action in subparsers.choices[scenario]._actions:
        flags.setdefault(action.dest, []).extend(action.option_strings)

    return {field: _FLAG_JOIN.join(names) for field, names in flags.items() if names}


def _item_models(annotation: object) -> list[type[BaseModel]]:
    """The models inside a field's type: a list's items, a union's members (the items a repeated flag adds), and the
    models nested in those (a runway plan's case holds its phases)."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        nested = [model for field in annotation.model_fields.values() for model in _item_models(field.annotation)]
        return [annotation, *nested]

    return [model for argument in get_args(annotation) for model in _item_models(argument)]


def _as_flag(field: str) -> str:
    return "--" + _as_term(field)


def _as_term(field: str) -> str:
    return field.replace("_", "-")


def _cli_names(model: type[BaseModel], flags: dict[str, str]) -> dict[str, str]:
    """Each field name a message may mention, as the command line writes it: a flag, or an item's term."""
    names = {
        term: _as_term(term)
        for field in model.model_fields.values()
        for item in _item_models(field.annotation)
        for term in item.model_fields
        if term != "kind"
    }
    names.update({field: flags.get(field, _as_flag(field)) for field in model.model_fields if field != "scenario"})

    return names


def _place(location: tuple[int | str, ...], flags: dict[str, str], places: Places) -> str:
    """Where a failure is, as the command line names it: a flag, or a repeated flag's item and its term.

    A location under one of ``places`` (the longest that matches) is named by the flag that place came from.
    """
    for length in range(len(location), 0, -1):
        if location[:length] in places:
            return _named_place(places[location[:length]], location[length:])

    field, *rest = location
    flag = flags.get(str(field), _as_flag(str(field)))
    if not rest or not isinstance(rest[_FIRST], int):
        return flag

    index, *inner = rest
    # A union's items carry their kind first (``instruments.0.note.principal``): the kind names its own flag.
    if inner and _as_flag(str(inner[_FIRST])) in flag.split(_FLAG_JOIN):
        flag, *inner = _as_flag(str(inner[_FIRST])), *inner[_FIRST + 1 :]
    place = f"{flag} #{int(index) + _ORDINAL_START}"

    return " ".join([place, *(_as_term(str(part)) for part in inner)])


def _named_place(flag: str, rest: tuple[int | str, ...]) -> str:
    """``flag``, then the rest of a location under it: an item's number from 1 and each term as the command line
    writes it."""
    parts = [f"#{part + _ORDINAL_START}" if isinstance(part, int) else _as_term(part) for part in rest]

    return " ".join([flag, *parts])


def _input_error(model: type[BaseModel], flags: dict[str, str], error: ValidationError, places: Places) -> str:
    """The validation failures as one line each, naming flags and terms rather than model fields."""
    names = _cli_names(model, flags)
    pattern = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b")
    failures = error.errors(include_url=False)
    # A list whose items failed also reports itself too short (the failed items are dropped): say the cause only.
    failed_items = {failure["loc"][_FIRST] for failure in failures if len(failure["loc"]) > 1}
    lines = []
    for failure in failures:
        if failure["type"] == _TOO_SHORT and failure["loc"] and failure["loc"][_FIRST] in failed_items:
            continue
        message = pattern.sub(lambda match: names[match.group(1)], failure["msg"].removeprefix(_VALUE_ERROR_PREFIX))
        location = failure["loc"]
        lines.append(f"{_place(location, flags, places)}: {message}" if location else message)

    return "\n".join(lines)


async def run(argv: Sequence[str] | None = None) -> str:
    """Parse ``argv``, work the scenario and return its printout (``main`` writes it; tests await this).

    Raises ``SystemExit`` with a message for a bad argument, an input the model refuses (or, for a runway plan, a
    ``--raise-use-of-funds`` line naming a raise not given), an input with no answer
    (``equity_calculator.errors``), an unwritable workbook, or a workbook value too large for a cell
    (``ResultOutOfRange``).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    model = _INPUT_MODELS[args.scenario]
    given = {
        name: value
        for name, value in vars(args).items()
        if name not in (*_OUTPUT_FLAGS, "scenario") and value is not None
    }
    places: Places = {}
    shape = _SHAPES.get(args.scenario)
    if shape is not None:
        given, places = shape(given)
    try:
        inputs = model.model_validate(given)
    except ValidationError as error:
        raise SystemExit(_input_error(model, _flags_by_field(parser, args.scenario), error, places)) from None

    try:
        result = compute(inputs)
    except EquityComputeError as error:
        raise SystemExit(str(error)) from None
    sheet = sheet_for(result)
    workbook: Path | None = args.xlsx
    if workbook is not None:
        try:
            await asyncio.to_thread(save_workbook, workbook, [sheet])
        except OSError as error:
            raise SystemExit(f"--xlsx: cannot write {workbook} ({error.strerror or type(error).__name__})") from None
        except EquityComputeError as error:
            raise SystemExit(f"--xlsx: {error}") from None

    if args.json:
        return result.model_dump_json(indent=_JSON_INDENT)

    report = render_sheet(sheet)
    return report if workbook is None else f"{report}\nWorkbook: {workbook}"


def main(argv: Sequence[str] | None = None) -> None:
    """Entry point for ``equity_calculator`` (``argv`` is for tests)."""
    sys.stdout.write(asyncio.run(run(argv)) + "\n")


if __name__ == "__main__":
    main()
