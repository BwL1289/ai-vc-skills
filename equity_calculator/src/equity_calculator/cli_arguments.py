"""Each scenario's CLI flags (``equity_calculator investor|employee|pool|round|dilution|vesting|waterfall``).

The number readers are ``cli_numbers``; a repeated flag's one-argument terms are ``cli_instruments``.
"""

from __future__ import annotations

import argparse
from typing import get_args

from equity_calculator.cli_instruments import parse_class, parse_note, parse_round, parse_safe
from equity_calculator.cli_numbers import parse_decimal, parse_months, parse_percent, parse_whole
from equity_calculator.schemas.equity import PoolTiming, ShareRounding
from equity_calculator.schemas.equity_vesting import Acceleration, AccelerationBase

_INSTRUMENTS = "instruments"
_TERMS = '"TERMS"'
_ROUNDS = "rounds"
_CLASSES = "classes"


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
        help="A post-money SAFE: 'AMOUNT [valuation-cap=X] [discount-percent=D] [mfn]'. Repeat for each SAFE.",
    )
    parser.add_argument(
        "--note",
        type=parse_note,
        action="append",
        dest=_INSTRUMENTS,
        metavar=_TERMS,
        help="A convertible note: 'PRINCIPAL interest-rate-percent=R (months-outstanding=M | issue-date=YYYY-MM-DD "
        "conversion-date=YYYY-MM-DD) [compounding=simple|annual|monthly] [stub-rule=simple|fractional_power] "
        "[day-count=actual_365|actual_360] [valuation-cap=X] [discount-percent=D] [interest-paid-in-cash]'. "
        "Compounding defaults to annual and stub-rule to fractional_power.",
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
