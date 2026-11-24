"""Each scenario's CLI flags (``equity_calculator investor|employee|pool|round|dilution|vesting|waterfall|deal_check|``
``runway_plan|metrics_check|market_sizing|instrument_compare|pool_plan|raise_pipeline|cap_table_check``).

The number readers are ``cli_numbers``; a repeated flag's one-argument terms are ``cli_instruments``.
"""

from __future__ import annotations

import argparse
from typing import get_args

from equity_calculator.cli_instruments import (
    parse_cap_class,
    parse_class,
    parse_commitment,
    parse_funds_line,
    parse_hire,
    parse_holder,
    parse_next_round,
    parse_note,
    parse_phase,
    parse_preview,
    parse_raise,
    parse_raise_funds_line,
    parse_round,
    parse_safe,
    parse_segment,
    parse_sensitivity,
    parse_series,
    parse_stage,
    parse_top_down,
)
from equity_calculator.cli_numbers import (
    parse_count,
    parse_customers,
    parse_decimal,
    parse_months,
    parse_percent,
    parse_whole,
    parse_years,
)
from equity_calculator.schemas.equity import PoolTiming, ShareRounding
from equity_calculator.schemas.equity_cap_table_check import PercentBasis
from equity_calculator.schemas.equity_instrument_compare import PoolAtExit
from equity_calculator.schemas.equity_metrics_check import (
    ChurnBasis,
    CustomerSegment,
    ProfitMarginBasis,
    RecurringUnit,
    StatedChurnBasis,
)
from equity_calculator.schemas.equity_round import NoteCompounding, StubRule
from equity_calculator.schemas.equity_runway_plan import MilestoneType
from equity_calculator.schemas.equity_vesting import Acceleration, AccelerationBase

_INSTRUMENTS = "instruments"
_TERMS = '"TERMS"'
_ROUNDS = "rounds"
_CLASSES = "classes"
_FUNDS = "use_of_funds"
_SAFE_HELP = "A post-money SAFE: 'AMOUNT [valuation-cap=X] [discount-percent=D] [mfn]'. Repeat for each SAFE."
_NOTE_HELP = (
    "A convertible note: 'PRINCIPAL interest-rate-percent=R (months-outstanding=M | issue-date=YYYY-MM-DD "
    "conversion-date=YYYY-MM-DD) [compounding=simple|annual|monthly] [stub-rule=simple|fractional_power] "
    "[day-count=actual_365|actual_360] [valuation-cap=X] [discount-percent=D] [interest-paid-in-cash]'. "
    "Compounding defaults to annual and stub-rule to fractional_power."
)


def investor_arguments(parser: argparse.ArgumentParser) -> None:
    """The investor test's flags."""
    parser.add_argument("--equity-percent", type=parse_percent, help="The stake sold, in percent (n).")
    parser.add_argument(
        "--pre-money", type=parse_decimal, help="Pre-money valuation in dollars (V); needs --investment."
    )
    parser.add_argument("--investment", type=parse_decimal, help="Dollars invested (I); n = I/(V + I).")
    parser.add_argument(
        "--outcome-multiplier",
        type=parse_decimal,
        help="What the deal does to the company's average outcome, cash included (m; 1.1 is +10%%).",
    )
    parser.add_argument("--growth-percent", type=parse_percent, help="The same as a percent gain (m = 1 + g/100).")
    parser.add_argument("--holder-percent", type=parse_percent, help="One holder's stake before the round, in percent.")


def employee_arguments(parser: argparse.ArgumentParser) -> None:
    """The employee test's flags."""
    parser.add_argument(
        "--outcome-multiplier", type=parse_decimal, help="What the hire does to the average outcome (i; 1.2 is +20%%)."
    )
    parser.add_argument("--gain-percent", type=parse_percent, help="The same as a percent gain (i = 1 + g/100).")
    parser.add_argument("--offered-percent", type=parse_percent, help="A stake to test against the hire, in percent.")
    parser.add_argument("--annual-cost", type=parse_decimal, help="Salary and overhead a year, in dollars.")
    parser.add_argument(
        "--valuation", type=parse_decimal, help="The company's valuation, in dollars (with --annual-cost)."
    )
    parser.add_argument(
        "--margin-percent", type=parse_percent, help="The company's 'profit' on the hire, in percent (default 0)."
    )
    parser.add_argument(
        "--cost-years", type=parse_decimal, help="Years of salary paid in stock (default 1.5, PG's rule of thumb)."
    )


def pool_arguments(parser: argparse.ArgumentParser) -> None:
    """The option-pool shuffle's flags."""
    parser.add_argument(
        "--fully-diluted-shares", type=parse_whole, required=True, help="Every pre-round share, unissued pool included."
    )
    parser.add_argument(
        "--unissued-pool-shares", type=parse_whole, help="The unissued pool before the round (default 0)."
    )
    parser.add_argument("--pre-money", type=parse_decimal, required=True, help="Pre-money valuation in dollars (V).")
    parser.add_argument("--investment", type=parse_decimal, required=True, help="Dollars invested (I).")
    parser.add_argument(
        "--target-pool-percent",
        type=parse_percent,
        required=True,
        help="The unissued pool after the round, in percent.",
    )
    parser.add_argument(
        "--pool-timing",
        choices=get_args(PoolTiming),
        help="Where the pool is counted (default pre_money, the usual term sheet); both are always shown.",
    )
    parser.add_argument(
        "--share-rounding",
        choices=get_args(ShareRounding),
        help="exact (fractional shares, the default) or whole_shares (rounded down, the cash left over shown).",
    )


def round_arguments(parser: argparse.ArgumentParser) -> None:
    """The priced round's flags: the round, then one ``--safe`` or ``--note`` per instrument, in order."""
    parser.add_argument(
        "--fully-diluted-shares",
        type=parse_whole,
        required=True,
        help="Every pre-round share, unissued pool included, SAFEs and notes not (FD).",
    )
    parser.add_argument(
        "--unissued-pool-shares", type=parse_whole, help="The unissued pool before the round (U, default 0)."
    )
    parser.add_argument("--pre-money", type=parse_decimal, required=True, help="Pre-money valuation in dollars (V).")
    parser.add_argument("--investment", type=parse_decimal, required=True, help="New money in dollars (I).")
    parser.add_argument(
        "--target-pool-percent",
        type=parse_percent,
        help="The unissued pool after the round, in percent (t, default 0: no top-up).",
    )
    parser.add_argument(
        "--pool-timing",
        choices=get_args(PoolTiming),
        help="Where a pool top-up is counted (default pre_money).",
    )
    parser.add_argument(
        "--safe",
        type=parse_safe,
        action="append",
        dest=_INSTRUMENTS,
        metavar=_TERMS,
        help=_SAFE_HELP,
    )
    parser.add_argument(
        "--note",
        type=parse_note,
        action="append",
        dest=_INSTRUMENTS,
        metavar=_TERMS,
        help=_NOTE_HELP,
    )


def dilution_arguments(parser: argparse.ArgumentParser) -> None:
    """One holder's dilution: their stake before the first round, then one ``--round`` per round, in order."""
    parser.add_argument(
        "--holder-percent", type=parse_percent, required=True, help="The holder's stake before the first round (h0)."
    )
    parser.add_argument(
        "--round",
        type=parse_round,
        action="append",
        dest=_ROUNDS,
        required=True,
        metavar=_TERMS,
        help="One round: '(investor-percent=N | pre-money=V investment=I) [pool-percent=P]'; n = I/(V + I) from the "
        "amounts, P the new pool's share after the round. Repeat for each round, in order.",
    )


def vesting_arguments(parser: argparse.ArgumentParser) -> None:
    """One grant's vesting at a month: schedule, termination, acceleration and prices."""
    parser.add_argument("--grant-shares", type=parse_whole, required=True, help="Shares in the grant (G).")
    parser.add_argument("--total-months", type=parse_months, help="Months until fully vested (T, default 48).")
    parser.add_argument("--cliff-months", type=parse_months, help="Months before anything vests (default 12).")
    parser.add_argument("--month", type=parse_months, required=True, help="The month asked about, from the grant.")
    parser.add_argument("--strike-price", type=parse_decimal, help="The option's exercise price per share.")
    parser.add_argument(
        "--common-price", type=parse_decimal, help="The common stock's price per share (needs --strike-price)."
    )
    parser.add_argument("--termination-month", type=parse_months, help="The month the holder left; vesting stops.")
    parser.add_argument(
        "--acceleration",
        choices=get_args(Acceleration),
        help="none (the default), single_trigger (at the change of control) or double_trigger (the change of "
        "control and a termination at or after it).",
    )
    parser.add_argument(
        "--acceleration-percent", type=parse_percent, help="How much vests at once when acceleration fires."
    )
    parser.add_argument(
        "--acceleration-base",
        choices=get_args(AccelerationBase),
        help="What the percent is of: unvested (the default) or grant (capped at what is unvested).",
    )
    parser.add_argument("--change-of-control-month", type=parse_months, help="The month of the change of control.")
    parser.add_argument(
        "--share-rounding",
        choices=get_args(ShareRounding),
        help="exact (fractional shares, the default) or whole_shares (the vested count rounded down).",
    )


def waterfall_arguments(parser: argparse.ArgumentParser) -> None:
    """An exit waterfall: the exit amount, the common shares, then one ``--class`` per preferred class."""
    parser.add_argument("--exit-amount", type=parse_decimal, required=True, help="What the shareholders share (E).")
    parser.add_argument(
        "--common-shares",
        type=parse_whole,
        required=True,
        help="Every common share that takes part, exercised options included (above 0).",
    )
    parser.add_argument(
        "--class",
        type=parse_class,
        action="append",
        dest=_CLASSES,
        required=True,
        metavar=_TERMS,
        help="One preferred class: 'shares=S invested=I [preference-multiple=M] [rank=K] "
        "[participation=none|full|capped] [cap-multiple=C]'; rank 1 is paid first, a cap includes the preference. "
        "Repeat for each class.",
    )


def _deal_round_arguments(parser: argparse.ArgumentParser) -> None:
    """A deal check's raise, valuation, share counts, pool and SAFEs or notes (none required but the raise)."""
    parser.add_argument("--investment", type=parse_decimal, required=True, help="The raise in dollars (I).")
    parser.add_argument("--pre-money", type=parse_decimal, help="The pre-money valuation as stated (V).")
    parser.add_argument("--post-money", type=parse_decimal, help="The post-money valuation as stated.")
    parser.add_argument(
        "--stated-investor-percent", type=parse_percent, help="The percent the deck says the investors get."
    )
    parser.add_argument(
        "--fully-diluted-shares",
        type=parse_whole,
        help="Every pre-round share, unissued pool included, SAFEs and notes not (FD); needed for SAFEs, notes or a "
        "pool top-up.",
    )
    parser.add_argument(
        "--unissued-pool-shares", type=parse_whole, help="The unissued pool before the round (U, default 0)."
    )
    parser.add_argument(
        "--unissued-pool-percent",
        type=parse_percent,
        help="The unissued pool before the round as a percent of FD, instead of --unissued-pool-shares.",
    )
    parser.add_argument(
        "--target-pool-percent",
        type=parse_percent,
        help="The unissued pool after the round, in percent (t, default 0: no top-up).",
    )
    parser.add_argument(
        "--pool-timing", choices=get_args(PoolTiming), help="Where a pool top-up is counted (default pre_money)."
    )
    parser.add_argument("--safe", type=parse_safe, action="append", dest=_INSTRUMENTS, metavar=_TERMS, help=_SAFE_HELP)
    parser.add_argument("--note", type=parse_note, action="append", dest=_INSTRUMENTS, metavar=_TERMS, help=_NOTE_HELP)
    parser.add_argument(
        "--holder-percent", type=parse_percent, help="One group's share of FD before the round (the founders, say)."
    )
    parser.add_argument(
        "--holder-shares", type=parse_whole, help="That group's shares before the round, instead of --holder-percent."
    )
    parser.add_argument(
        "--stated-holder-percent", type=parse_percent, help="The percent the deck says that group keeps after."
    )


def deal_check_arguments(parser: argparse.ArgumentParser) -> None:
    """A deal check's flags: the round as the deck states it, then runway, use of funds, tolerances and bands."""
    _deal_round_arguments(parser)
    parser.add_argument("--cash-on-hand", type=parse_decimal, help="Cash before the raise lands (default 0).")
    parser.add_argument(
        "--planned-monthly-gross-burn", type=parse_decimal, help="Planned monthly cash spend after the raise."
    )
    parser.add_argument(
        "--planned-monthly-revenue", type=parse_decimal, help="Planned monthly cash revenue after the raise."
    )
    parser.add_argument("--current-monthly-gross-burn", type=parse_decimal, help="Today's monthly cash spend.")
    parser.add_argument("--current-monthly-revenue", type=parse_decimal, help="Today's monthly cash revenue.")
    parser.add_argument("--stated-runway-months", type=parse_decimal, help="The runway the deck claims, in months.")
    parser.add_argument(
        "--use-of-funds",
        type=parse_funds_line,
        action="append",
        dest=_FUNDS,
        metavar=_TERMS,
        help="One use-of-funds line: dollars ('1250000') or a percent of the raise ('50%%'). Repeat for each line.",
    )
    parser.add_argument(
        "--tolerance-points",
        type=parse_percent,
        help="How far a stated percent may sit from the computed one, in percentage points (default 0.5).",
    )
    parser.add_argument(
        "--tolerance-percent",
        type=parse_percent,
        help="How far a stated money or months figure may sit, in percent of the computed one (default 2).",
    )
    parser.add_argument(
        "--dilution-band-percent",
        type=parse_percent,
        help="Flag an investor share above this percent (default 25; a common benchmark, not a rule).",
    )
    parser.add_argument(
        "--runway-band-months",
        type=parse_decimal,
        help="Flag planned net runway below this many months (default 18; a common benchmark, not a rule).",
    )


_PHASE_TERMS = "'from-month=M gross-burn=G [revenue=R | revenue-run-rate=Y]'"


def _case_arguments(parser: argparse.ArgumentParser, case: str) -> None:
    """A downside or lean case: its own phases, or percents of the plan's revenue and gross burn (not both)."""
    parser.add_argument(
        f"--{case}-phase",
        type=parse_phase,
        action="append",
        dest=f"{case}_phases",
        metavar=_TERMS,
        help=f"One phase of the {case} case, as --phase. Repeat for each phase; or give the percents below instead.",
    )
    parser.add_argument(
        f"--{case}-revenue-percent",
        type=parse_percent,
        dest=f"{case}_revenue_percent",
        help=f"The {case} case's revenue as a percent of the plan's in every phase (left out: 100).",
    )
    parser.add_argument(
        f"--{case}-gross-burn-percent",
        type=parse_percent,
        dest=f"{case}_gross_burn_percent",
        help=f"The {case} case's gross burn as a percent of the plan's in every phase (left out: 100).",
    )


def runway_plan_arguments(parser: argparse.ArgumentParser) -> None:
    """A runway plan's flags: cash, the plan's phases, a downside and a lean case, the raises, milestones, checks."""
    parser.add_argument("--cash-on-hand", type=parse_decimal, required=True, help="Cash in the bank today.")
    parser.add_argument(
        "--cash-floor", type=parse_decimal, help="Cash kept in the bank that the plan never spends (default 0)."
    )
    parser.add_argument(
        "--phase",
        type=parse_phase,
        action="append",
        dest="phases",
        required=True,
        metavar=_TERMS,
        help=f"One phase of the plan: {_PHASE_TERMS}, monthly figures from that month until the next phase (the "
        "last runs on); Y is an annualised revenue run-rate, divided by 12 for you. The first starts at month 1. "
        "Repeat for each phase, in order.",
    )
    _case_arguments(parser, "downside")
    _case_arguments(parser, "lean")
    parser.add_argument(
        "--raise",
        type=parse_raise,
        action="append",
        dest="raises",
        metavar=_TERMS,
        help="One raise to compare, of any instrument (a priced round, a SAFE, a note) as cash in: 'amount=I "
        "[lands-month=L] [stated-runway-months=M] [stated-runway-from=today|landing]'; L whole months from today "
        "(default 0: now). Repeat for each raise.",
    )
    parser.add_argument(
        "--raise-use-of-funds",
        type=parse_raise_funds_line,
        action="append",
        dest="raise_use_of_funds",
        metavar=_TERMS,
        help="One use-of-funds line of a raise: its number (1 is the first --raise), then dollars ('1 1250000') or "
        "a percent of that raise ('1 50%%'). Repeat for each line.",
    )
    parser.add_argument(
        "--milestone",
        type=parse_months,
        action="append",
        dest="milestones",
        help="A milestone, as a month from today. Repeat for each milestone.",
    )
    parser.add_argument(
        "--milestone-type",
        choices=get_args(MilestoneType),
        help="What the milestones are for: next_round (the default; the months to raise count after each) or "
        "self_funding (this is the only round: no follow-on assumed, no months to raise).",
    )
    parser.add_argument(
        "--months-to-raise",
        type=parse_months,
        help="Months allowed to raise the next round after a milestone (left out: none, flagged).",
    )
    parser.add_argument(
        "--stated-runway-months", type=parse_decimal, help="The runway you state with no raise, in months."
    )
    parser.add_argument(
        "--tolerance-points",
        type=parse_percent,
        help="How far percent use-of-funds lines may sit from 100%%, in percentage points (default 0.5).",
    )
    parser.add_argument(
        "--tolerance-percent",
        type=parse_percent,
        help="How far a stated runway or a use-of-funds total may sit, in percent of the computed one (default 2).",
    )
    parser.add_argument(
        "--runway-band-months",
        type=parse_decimal,
        help="Flag a raise lasting under this many months on the plan (default 18; a common benchmark, not a rule).",
    )


def _metrics_parts_arguments(parser: argparse.ArgumentParser) -> None:
    """A metrics check's parts: the period, the recurring revenue movement, the latest month, customers, spend."""
    parser.add_argument(
        "--period-months",
        type=parse_months,
        required=True,
        help="The period every flow figure covers, in whole months (1 to 36): movement, customers, spend, burn.",
    )
    parser.add_argument(
        "--recurring-unit",
        choices=get_args(RecurringUnit),
        help="The unit the recurring revenue figures are in: monthly (MRR) or annual (ARR) (default monthly).",
    )
    movements = (
        ("--starting-recurring", "Recurring revenue at the start of the period (S; give 0 when there was none)."),
        ("--new-recurring", "Recurring revenue from customers won in the period (N, default 0)."),
        ("--expansion-recurring", "Recurring revenue added by upsells and expansion in the period (E, default 0)."),
        ("--contraction-recurring", "Recurring revenue lost to downgrades in the period (C, default 0)."),
        ("--churned-recurring", "Recurring revenue lost to cancellations in the period (X, default 0)."),
        ("--cohort-expansion-recurring", "Expansion from the customers there at the start only (retention uses it)."),
        ("--cohort-contraction-recurring", "Contraction of the customers there at the start only."),
        ("--cohort-churned-recurring", "Recurring revenue the customers there at the start cancelled."),
        ("--month-total-revenue", "The latest month's total revenue (T)."),
        ("--month-one-time-revenue", "Of it, one-time revenue: setup, implementation, services (O, default 0)."),
        ("--month-usage-revenue", "Of it, variable usage revenue (U, default 0)."),
    )
    for flag, words in movements:
        parser.add_argument(flag, type=parse_decimal, help=words)
    customers = (
        ("--customers-start", "Customers at the start of the period."),
        ("--customers-lost", "Of them, customers lost in the period."),
        ("--customers-new", "Customers won in the period, every channel."),
        ("--customers-new-paid", "Of them, customers won through paid channels."),
    )
    for flag, words in customers:
        parser.add_argument(flag, type=parse_customers, help=words)
    parser.add_argument(
        "--sales-marketing-spend", type=parse_decimal, help="Sales and marketing spend in the period, every cost."
    )
    parser.add_argument("--gross-margin-percent", type=parse_percent, help="Gross margin, in percent.")
    parser.add_argument(
        "--net-burn",
        type=parse_decimal,
        help="Net burn in the period (spend less cash in); give a negative value as --net-burn=-50000.",
    )
    parser.add_argument("--largest-customer-revenue", type=parse_decimal, help="The largest customer's revenue.")
    parser.add_argument("--period-revenue", type=parse_decimal, help="Total revenue in the period.")
    _metrics_later_parts_arguments(parser)


def _metrics_later_parts_arguments(parser: argparse.ArgumentParser) -> None:
    """LTV's parts, the Rule of 40's two percents and the magic number's two quarters."""
    parser.add_argument(
        "--arpa",
        type=parse_decimal,
        help="Average recurring revenue per account, in --recurring-unit; LTV is worked from it.",
    )
    parser.add_argument(
        "--contribution-margin-percent",
        type=parse_percent,
        help="Contribution margin, in percent; LTV uses it over --gross-margin-percent.",
    )
    parser.add_argument(
        "--ltv-churn-basis",
        choices=get_args(ChurnBasis),
        help="The period's churn LTV divides by (default gross_revenue).",
    )
    parser.add_argument(
        "--revenue-growth-percent",
        type=parse_percent,
        help="Revenue growth for the Rule of 40, in percent, as you state it (below 0 as --revenue-growth-percent=-5).",
    )
    parser.add_argument(
        "--profit-margin-percent",
        type=parse_percent,
        help="Profit margin for the Rule of 40, in percent (below 0 as --profit-margin-percent=-20).",
    )
    parser.add_argument(
        "--profit-margin-basis",
        choices=get_args(ProfitMarginBasis),
        help="Which margin --profit-margin-percent is (default unlabelled, which is flagged).",
    )
    quarters = (
        ("--quarter-revenue", "The latest quarter's revenue (Q), for the magic number."),
        ("--prior-quarter-revenue", "The quarter before's revenue (Q')."),
        ("--quarter-ending-arr", "ARR at the latest quarter's end (A), for the magic number on ARR."),
        ("--prior-quarter-ending-arr", "ARR at the end of the quarter before (A')."),
        ("--prior-quarter-sales-marketing-spend", "Sales and marketing spend in the quarter before, every cost."),
    )
    for flag, words in quarters:
        parser.add_argument(flag, type=parse_decimal, help=words)


def metrics_check_arguments(parser: argparse.ArgumentParser) -> None:
    """A metrics check's flags: the parts, then what the document states, the tolerances and the benchmarks."""
    _metrics_parts_arguments(parser)
    stated = (
        ("--stated-arr", parse_decimal, "The ARR the document states, in dollars."),
        ("--stated-nrr-percent", parse_percent, "The net revenue retention it states, in percent."),
        ("--stated-grr-percent", parse_percent, "The gross revenue retention it states, in percent."),
        (
            "--stated-churn-percent",
            parse_percent,
            "The churn it states, in percent (below 0 only as net revenue churn).",
        ),
    )
    for flag, reader, words in stated:
        parser.add_argument(flag, type=reader, help=words)
    parser.add_argument(
        "--stated-churn-basis",
        choices=get_args(StatedChurnBasis),
        help="What the stated churn counts (default unlabelled: it is checked on every basis the figures give).",
    )
    stated = (
        ("--stated-cac", parse_decimal, "The CAC it states, in dollars."),
        ("--stated-cac-payback-months", parse_decimal, "The CAC payback it states, in months."),
        ("--stated-burn-multiple", parse_decimal, "The burn multiple it states (2.5 for 2.5x)."),
        ("--stated-concentration-percent", parse_percent, "The largest customer's share of revenue it states."),
        ("--stated-ltv", parse_decimal, "The LTV it states, in dollars."),
        ("--stated-ltv-to-cac", parse_decimal, "The LTV/CAC it states (3 for 3x)."),
        ("--stated-rule-of-40-percent", parse_percent, "The Rule of 40 it states, in percent (45 for 45%%)."),
        ("--stated-magic-number", parse_decimal, "The magic number it states (0.8 for 0.8)."),
        (
            "--tolerance-points",
            parse_percent,
            "How far a stated percent may sit from the computed one, in percentage points (default 0.5).",
        ),
        (
            "--tolerance-percent",
            parse_percent,
            "How far a stated money, months or multiple figure may sit, in percent of the computed one (default 2).",
        ),
    )
    for flag, reader, words in stated:
        parser.add_argument(flag, type=reader, help=words)
    parser.add_argument(
        "--customer-segment",
        choices=get_args(CustomerSegment),
        help="Who you sell to; it sets the CAC payback benchmark (a benchmark, not a rule).",
    )
    parser.add_argument(
        "--payback-band-months",
        type=parse_decimal,
        help="Flag a CAC payback on gross margin at or above this many months; used over the segment's.",
    )
    parser.add_argument(
        "--burn-multiple-band",
        type=parse_decimal,
        help="Flag a burn multiple at or above this (default 3; a benchmark, not a rule).",
    )
    parser.add_argument(
        "--net-revenue-churn-band-percent",
        type=parse_percent,
        help="Flag one month's net revenue churn above this percent (default 2; a benchmark, not a rule).",
    )


def market_sizing_arguments(parser: argparse.ArgumentParser) -> None:
    """A market size's flags: the segments, the top-down figures, the sensitivity rows, then the founder's other
    figures and what the deck states."""
    parser.add_argument(
        "--segment",
        type=parse_segment,
        action="append",
        dest="segments",
        required=True,
        metavar=_TERMS,
        help="One group of buying customers: '[customers=N] price=P [price-period-months=M] [units-per-customer=U] "
        "[take-rate-percent=T] [second-line-percent=L] [serviceable-percent=S] [obtainable-percent=O | "
        "obtainable-customers=C | obtainable-units=V] [customers-today=D]'. The price is for M months (default 12). "
        "Leave customers out with only the customers or units to win. Repeat for each segment (at most 8).",
    )
    parser.add_argument(
        "--top-down",
        type=parse_top_down,
        action="append",
        dest="top_down",
        metavar=_TERMS,
        help="A top-down figure to compare with: 'amount=A [comparable-percent=P] [compare-to=tam|sam]' (a "
        "cross-check, never a verdict). Repeat for each (at most 3).",
    )
    parser.add_argument(
        "--sensitivity",
        type=parse_sensitivity,
        action="append",
        dest="sensitivity",
        metavar=_TERMS,
        help="One field of one segment worked again at your own values: 'field=F segment=K values=V1/V2' (F one of "
        "customers, price, units-per-customer, take-rate-percent, second-line-percent, serviceable-percent, "
        "obtainable-percent, obtainable-customers, obtainable-units; K 1 for the first --segment). Repeat for each (at "
        "most 6, 4 values each).",
    )
    parser.add_argument(
        "--population", type=parse_decimal, help="The total the segments are drawn from, in the same buying unit."
    )
    parser.add_argument("--annual-revenue-today", type=parse_decimal, help="The company's annual revenue today.")
    parser.add_argument("--som-years", type=parse_years, help="Years to win the SOM customers (1 to 20).")
    parser.add_argument(
        "--som-months",
        type=parse_months,
        help="Months to win the SOM customers (1 to 240), for a horizon such as 30 months; or --som-years.",
    )
    parser.add_argument(
        "--som-target",
        type=parse_decimal,
        help="The annual revenue your plan needs from this market by then; needs a SOM in every segment.",
    )
    stated = (
        ("--stated-tam", "The TAM the deck states, in dollars a year."),
        ("--stated-sam", "The SAM the deck states, in dollars a year."),
        ("--stated-som", "The SOM the deck states, in dollars a year; needs a SOM in every segment."),
    )
    for flag, words in stated:
        parser.add_argument(flag, type=parse_decimal, help=words)
    parser.add_argument(
        "--tolerance-percent",
        type=parse_percent,
        help="How far a stated figure may sit from the computed one, in percent of the computed one (default 2).",
    )


_SERIES_HELP = (
    "'standard' (1x, non-participating; only when the founder says the terms are standard) or "
    "'preference-multiple=M participation=none|full|capped [cap-multiple=C]', either with [rank=K] (default 1)"
)


def _today_arguments(parser: argparse.ArgumentParser) -> None:
    """A comparison's cap table today, by holder group."""
    parser.add_argument("--founder-shares", type=parse_whole, required=True, help="The founders' shares today.")
    parser.add_argument(
        "--team-shares",
        type=parse_whole,
        required=True,
        help="The team's common and granted options today (0 for none).",
    )
    parser.add_argument(
        "--unissued-pool-shares", type=parse_whole, required=True, help="The unissued pool today (U, 0 for none)."
    )
    parser.add_argument(
        "--existing-series",
        type=parse_class,
        action="append",
        dest="existing_series",
        metavar=_TERMS,
        help="An existing preferred series: 'shares=S invested=I preference-multiple=M "
        "participation=none|full|capped [cap-multiple=C] [rank=K]' (the multiple and participation are that "
        "series' own terms, always given; rank default 1). Repeat for each (at most 6).",
    )
    parser.add_argument(
        "--existing-safe",
        type=parse_safe,
        action="append",
        dest="existing_instruments",
        metavar=_TERMS,
        help="An existing post-money SAFE, as --safe takes it in a round. Repeat for each.",
    )
    parser.add_argument(
        "--existing-note",
        type=parse_note,
        action="append",
        dest="existing_instruments",
        metavar=_TERMS,
        help="An existing note, as --note takes it in a round, with months-outstanding=M as of today and "
        "compounding=simple|annual|monthly always given. Repeat for each (at most 4 SAFEs and notes in all).",
    )


def _note_arguments(parser: argparse.ArgumentParser) -> None:
    """Option B, a convertible note for the raise: its cap and discount, its interest and when it converts."""
    parser.add_argument(
        "--note-valuation-cap", type=parse_decimal, help="B: the note's valuation cap, pre-money over today's FD."
    )
    parser.add_argument("--note-discount-percent", type=parse_percent, help="B: the note's discount, in percent.")
    parser.add_argument(
        "--note-interest-rate-percent",
        type=parse_percent,
        required=True,
        help="B: the note's interest rate a year, in percent (0 for none).",
    )
    parser.add_argument(
        "--note-compounding",
        choices=get_args(NoteCompounding),
        required=True,
        help="B: simple interest, or compounding annual or monthly.",
    )
    parser.add_argument(
        "--note-stub-rule",
        choices=get_args(StubRule),
        help="B: how a part period compounds (default fractional_power).",
    )
    parser.add_argument(
        "--note-months-to-conversion",
        type=parse_months,
        help="B: months from today until the note converts at the next round (needed with --next-round; left out "
        "with none).",
    )
    parser.add_argument(
        "--note-maturity-months",
        type=parse_months,
        help="B: the note's maturity in months (with a next round, compared only; with none, its maturity is shown).",
    )
    parser.add_argument(
        "--note-interest-paid-in-cash",
        action="store_true",
        default=None,
        help="B: the interest is paid in cash, so only the principal converts.",
    )
    parser.add_argument(
        "--note-owed-month",
        type=parse_months,
        action="append",
        dest="note_owed_months",
        metavar="M",
        help="B: a month at which to show what the note owes, principal plus interest (its maturity, say). Repeat "
        "for each (at most 6).",
    )
    _no_round_note_arguments(parser)


def _no_round_note_arguments(parser: argparse.ArgumentParser) -> None:
    """Option B's own terms for no next round: its conversion at maturity, and what it is paid at a sale before any
    priced round. Each is the note's own term, from the founder; with a --next-round each is refused."""
    parser.add_argument(
        "--note-maturity-conversion-valuation",
        type=parse_decimal,
        help="B, no next round: the valuation the note converts at on maturity, over today's FD, from its own terms.",
    )
    parser.add_argument(
        "--note-maturity-conversion-price",
        type=parse_decimal,
        help="B, no next round: the price a share the note converts at on maturity, from its own terms.",
    )
    parser.add_argument(
        "--note-change-of-control-multiple",
        type=parse_decimal,
        help="B, no next round: at a sale before any priced round the note is paid this multiple of its principal, "
        "before any share, from its own terms.",
    )
    parser.add_argument(
        "--note-change-of-control-at-cap",
        action="store_true",
        default=None,
        help="B, no next round: at a sale before any priced round the note converts at its cap price into common, "
        "from its own terms (needs --note-valuation-cap and --note-months-to-exit).",
    )
    parser.add_argument(
        "--note-months-to-exit",
        type=parse_months,
        help="B, no next round: months from today to the sales, for the interest the note owes then.",
    )


def instrument_compare_arguments(parser: argparse.ArgumentParser) -> None:
    """A priced round now (A) beside a note now (B): the cap table today, the raise, each option's terms, the next
    rounds and the exits."""
    _today_arguments(parser)
    parser.add_argument("--investment", type=parse_decimal, required=True, help="The raise in dollars (I), both ways.")
    parser.add_argument(
        "--priced-pre-money", type=parse_decimal, required=True, help="A: the priced round's pre-money (V)."
    )
    parser.add_argument(
        "--priced-target-pool-percent",
        type=parse_percent,
        help="A: the unissued pool after the round, in percent (default 0: no top-up).",
    )
    parser.add_argument(
        "--priced-pool-timing",
        choices=get_args(PoolTiming),
        help="A: where a pool top-up is counted (default pre_money).",
    )
    parser.add_argument(
        "--priced-preference",
        type=parse_series,
        required=True,
        metavar=_TERMS,
        help=f"A: the series' liquidation terms, {_SERIES_HELP}.",
    )
    _note_arguments(parser)
    parser.add_argument(
        "--next-round",
        type=parse_next_round,
        action="append",
        dest="next_rounds",
        metavar=_TERMS,
        help="The next priced round, the same for both options: 'pre-money=V investment=I [target-pool-percent=T] "
        f"[pool-timing=pre_money|post_money]' and its series' terms, {_SERIES_HELP}. Repeat for each alternative "
        "(at most 4): each is worked from today, never after the one before. With none, the comparison runs with no "
        "next round: ownership today, the note at its maturity and each exit as a sale before any priced round.",
    )
    parser.add_argument(
        "--exit",
        type=parse_decimal,
        action="append",
        dest="exit_amounts",
        metavar="E",
        help="What the company sells for after the next round (with no --next-round, before any priced round), in "
        "dollars. Repeat for each (at most 6); at least one is needed.",
    )
    parser.add_argument(
        "--pool-at-exit",
        choices=get_args(PoolAtExit),
        help="as_common (default: the pool counted as exercised, as in the ownership lines) or left_out.",
    )


def pool_plan_arguments(parser: argparse.ArgumentParser) -> None:
    """A pool sized from the hiring plan beside the term sheet's: today's shares, the round, the requested pool, the
    next round's month and one ``--hire`` per planned hire."""
    parser.add_argument(
        "--fully-diluted-shares",
        type=parse_whole,
        required=True,
        help="Every pre-round share, granted options and the unissued pool included (FD).",
    )
    parser.add_argument(
        "--unissued-pool-shares", type=parse_whole, required=True, help="The unissued pool today (U, 0 for none)."
    )
    parser.add_argument(
        "--founder-shares", type=parse_whole, help="The founders' own shares among FD, for their ownership line."
    )
    parser.add_argument("--pre-money", type=parse_decimal, required=True, help="The term sheet's pre-money (V).")
    parser.add_argument("--investment", type=parse_decimal, required=True, help="The round's new money (I).")
    parser.add_argument(
        "--requested-pool-percent",
        type=parse_percent,
        required=True,
        help="The term sheet's pool: the unissued pool after the round, in percent, created in the pre-money.",
    )
    parser.add_argument(
        "--next-round-month",
        type=parse_months,
        required=True,
        help="When the next round is expected, in whole months from today; hires starting after it are left out.",
    )
    parser.add_argument(
        "--hire",
        type=parse_hire,
        action="append",
        dest="hires",
        metavar='"ROLE: TERMS"',
        help="A planned hire: 'ROLE: start-month=M (grant-shares=S | grant-percent=P)', the grant in shares or as a "
        "percent of the post-round fully diluted shares, every hire the same way. Repeat for each (at most 40).",
    )


def raise_pipeline_arguments(parser: argparse.ArgumentParser) -> None:
    """A raise pipeline's flags: the round, the lead, each commitment and pro rata amount, the funnel's stages and the
    term sheets wanted, and (all four together, or none) the cash and burn for the start-raising month."""
    parser.add_argument("--round-size", type=parse_decimal, required=True, help="The round's size in dollars (R).")
    parser.add_argument("--lead-cheque", type=parse_decimal, help="The lead's cheque in dollars (L), when planned.")
    parser.add_argument(
        "--commitment",
        type=parse_commitment,
        action="append",
        dest="commitments",
        metavar=_TERMS,
        help="A commitment other than the lead's: 'AMOUNT kind=soft|firm', as the founder marks it; soft ones are "
        "shown on their own and never counted. Repeat for each (at most 40).",
    )
    parser.add_argument(
        "--pro-rata",
        type=parse_decimal,
        action="append",
        dest="pro_rata",
        metavar="AMOUNT",
        help="An existing investor's pro rata amount in dollars, counted in full. Repeat for each (at most 20).",
    )
    parser.add_argument(
        "--stage",
        type=parse_stage,
        action="append",
        dest="stages",
        metavar='"NAME: TERMS"',
        help="A funnel stage, in order: 'NAME: investors=N rate-percent=P [rate-basis=own|benchmark] "
        "[benchmark-source=TEXT]', N the investors at it today (each counted once, at the furthest stage reached) "
        "and P the founder's own rate from it to the next (from the last, to a term sheet); a benchmark needs its "
        "source, last. Repeat for each stage (at most 8).",
    )
    parser.add_argument(
        "--term-sheets-wanted", type=parse_count, help="The term sheets the founder wants (W), with the stages."
    )
    parser.add_argument("--cash-on-hand", type=parse_decimal, help="Cash in the bank today, for the runway.")
    parser.add_argument(
        "--cash-floor", type=parse_decimal, help="Cash kept in the bank that the plan never spends (default 0)."
    )
    parser.add_argument(
        "--phase",
        type=parse_phase,
        action="append",
        dest="runway_phases",
        metavar=_TERMS,
        help=f"One phase of the plan: {_PHASE_TERMS}, the runway plan's own; the first starts at month 1. Repeat "
        "for each phase, in order.",
    )
    parser.add_argument(
        "--months-to-raise",
        type=parse_months,
        help="Months the founder allows to raise; the start-raising month is the runway less these.",
    )


def cap_table_check_arguments(parser: argparse.ArgumentParser) -> None:
    """A cap table's flags: one ``--share-class`` per class and one ``--holder`` per holder line, in order, then the
    stated total and basis, the plan's reserve, the SAFEs and notes, and the founder's next round and planned rounds."""
    parser.add_argument(
        "--share-class",
        type=parse_cap_class,
        action="append",
        dest=_CLASSES,
        required=True,
        metavar=_TERMS,
        help="One class: 'kind=common|preferred|options_granted|options_unissued|warrants [shares=S] "
        "[authorised-shares=A] [stated-percent=P] [holder-lines=complete|partial]'; shares may be left to its holder "
        "lines. With both shares and --holder lines, holder-lines says whether the lines are every holder of the "
        "class (complete: checked against shares) or only some (partial); it is required then, never assumed. "
        "Repeat for each class, in the table's order (the first is class 1).",
    )
    parser.add_argument(
        "--holder",
        type=parse_holder,
        action="append",
        dest="holders",
        metavar=_TERMS,
        help="One holder line: 'share-class=K shares=S [stated-percent=P] [founder] [departed]', K the class's number; "
        "departed marks shares held by someone who has left. A line with both marks counts in the founders' share, "
        "the founders' path and the departed holders' share. Repeat for each line.",
    )
    parser.add_argument(
        "--stated-fully-diluted-shares", type=parse_whole, help="The table's own fully diluted total, to check."
    )
    parser.add_argument(
        "--stated-percent-basis",
        choices=get_args(PercentBasis),
        help="What the table's percents are a share of; required with any stated-percent, never assumed.",
    )
    parser.add_argument(
        "--option-plan-reserve", type=parse_whole, help="The option plan's authorised reserve (granted + unissued)."
    )
    parser.add_argument("--safe", type=parse_safe, action="append", dest=_INSTRUMENTS, metavar=_TERMS, help=_SAFE_HELP)
    parser.add_argument("--note", type=parse_note, action="append", dest=_INSTRUMENTS, metavar=_TERMS, help=_NOTE_HELP)
    parser.add_argument(
        "--preview",
        type=parse_preview,
        dest="conversion_preview",
        metavar=_TERMS,
        help="The next priced round as the founder gives it, to convert the SAFEs and notes: 'pre-money=V "
        "investment=I [target-pool-percent=T] [pool-timing=pre_money|post_money]'. Never assumed.",
    )
    parser.add_argument(
        "--planned-round",
        type=parse_round,
        action="append",
        dest="planned_rounds",
        metavar=_TERMS,
        help="One planned round for the founders' path, as --round takes it in dilution: '(investor-percent=N | "
        "pre-money=V investment=I) [pool-percent=P]'. Repeat for each round, in order. With --preview the path "
        "starts after the preview's round, so these are the rounds after it: never repeat the preview here (it "
        "would be counted twice).",
    )
    parser.add_argument(
        "--tolerance-points",
        type=parse_percent,
        help="How far a stated percent may sit from the computed one beyond rounding, in points (default 0).",
    )
