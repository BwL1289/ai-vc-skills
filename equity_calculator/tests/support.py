"""Shared builders for the equity tests: each scenario's input from plain text values, worked by ``compute``.

Values are strings so every number reaches the models as an exact ``Decimal`` (never a binary float).
"""

from __future__ import annotations

import math
from decimal import Decimal

from equity_calculator.scenarios import compute
from equity_calculator.schemas.equity import (
    EmployeeInput,
    EmployeeResult,
    InvestorInput,
    InvestorResult,
    PoolInput,
    PoolResult,
)
from equity_calculator.schemas.equity_common import (
    MAX_ADJUSTED_EXPONENT,
    MAX_SIGNIFICANT_DIGITS,
    MIN_ADJUSTED_EXPONENT,
    SIZE_LIMIT,
)
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealCheckResult
from equity_calculator.schemas.equity_dilution import DilutionInput, DilutionResult
from equity_calculator.schemas.equity_round import RoundInput, RoundResult
from equity_calculator.schemas.equity_vesting import VestingInput, VestingResult
from equity_calculator.schemas.equity_waterfall import WaterfallInput, WaterfallResult

# The words a bounds refusal names, and a size just below the smallest nonzero one (1e-15) the bounds allow.
DIGIT_REFUSAL = "significant digits"
SIZE_REFUSAL = "in size"
BELOW_SMALLEST = "1e-16"

# The worked option-pool example: 10M fully diluted shares (0.5M unissued pool), $8M pre-money, $2M in, 10% target.
POOL_EXAMPLE: dict[str, object] = {
    "fully_diluted_shares": 10_000_000,
    "unissued_pool_shares": 500_000,
    "pre_money": "8000000",
    "investment": "2000000",
    "target_pool_percent": "10",
}


def investor(**fields: object) -> InvestorResult:
    """The investor test for ``fields`` (an ``InvestorInput``'s fields)."""
    return compute(InvestorInput.model_validate(fields))


def employee(**fields: object) -> EmployeeResult:
    """The employee test for ``fields`` (an ``EmployeeInput``'s fields)."""
    return compute(EmployeeInput.model_validate(fields))


def pool(**fields: object) -> PoolResult:
    """The option-pool shuffle for ``fields`` (a ``PoolInput``'s fields)."""
    return compute(PoolInput.model_validate(fields))


# A $16M pre-money, $4M round on 10M fully diluted shares (0.5M unissued pool, 10% target pool after the round),
# with two post-money SAFEs: $500k capped at $5M and $1M capped at $10M (each a/K = 10% of the capitalization).
ROUND_EXAMPLE: dict[str, object] = {
    "fully_diluted_shares": 10_000_000,
    "unissued_pool_shares": 500_000,
    "pre_money": "16000000",
    "investment": "4000000",
    "target_pool_percent": "10",
}
ROUND_SAFES: list[dict[str, object]] = [
    {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "5000000"},
    {"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "10000000"},
]
# A note of $500k at 8% for 18 months: $60k simple interest, so $560k converts. Simple is named, since a note that
# names no compounding compounds yearly.
ROUND_NOTE: dict[str, object] = {
    "kind": "note",
    "principal": "500000",
    "interest_rate_percent": "8",
    "compounding": "simple",
    "months_outstanding": 18,
}


def round_(**fields: object) -> RoundResult:
    """The priced round for ``fields`` (a ``RoundInput``'s fields)."""
    return compute(RoundInput.model_validate(fields))


# A round whose discount-only SAFEs use up all of the pre-money but a sliver, so the price per share is near zero and
# the share counts grow about 28 orders of magnitude per SAFE: the largest value is about 4.3e294 with eight SAFEs
# (inside ``equity_calculator.result_range.RESULT_LIMIT``, 1e300), about 3.9e322 with nine and about 3.5e350 with
# ten (past it).
SAFES_INSIDE_RANGE = 8
SAFES_PAST_RANGE = (9, 10)
# Each SAFE pays K / 10**28 of the round price (a discount just over 10%): K counts down from here over odd numbers
# coprime with 10 and with the K already taken, so each SAFE's share of the sum below can be solved for on its own.
_SCALE = 10**MAX_SIGNIFICANT_DIGITS
_LARGEST_FACTOR = 9 * 10 ** (MAX_SIGNIFICANT_DIGITS - 1) - 1
_FACTOR_STEP = 2
_BASE = 10
# Purchase amounts are integers times 1e-40, the pre-money one times 1e-39, a discount percent one times 1e-26: so a
# SAFE's discounted amount is 1e27 * p / K in units of the pre-money's last digit, and every number has at most 28
# significant digits and is at least 1e-15 in size.
_AMOUNT_EXPONENT = -40
_PRE_MONEY_EXPONENT = -39
_PERCENT_EXPONENT = -26
_SHIFT = _BASE ** (_AMOUNT_EXPONENT + MAX_SIGNIFICANT_DIGITS - _PRE_MONEY_EXPONENT)
_SMALLEST_AMOUNT_DIGITS = _BASE ** (MIN_ADJUSTED_EXPONENT - _AMOUNT_EXPONENT)
_SMALLEST_PRE_MONEY_DIGITS = _BASE ** (MIN_ADJUSTED_EXPONENT - _PRE_MONEY_EXPONENT)
_INTEGER_DIGITS = MAX_ADJUSTED_EXPONENT + 1
_LARGEST_MONEY = "9" * _INTEGER_DIGITS + "." + "9" * (MAX_SIGNIFICANT_DIGITS - _INTEGER_DIGITS)


def _plain(digits: int, exponent: int) -> str:
    """``digits`` times 10**``exponent`` written out with no exponent (the CLI's number reader takes no ``E``)."""
    return format(Decimal(digits).scaleb(exponent), "f")


def sliver_round(safe_count: int) -> dict[str, object]:
    """A ``RoundInput``'s fields (text values) whose ``safe_count`` SAFEs leave 1 / (10**39 * L) of the pre-money.

    L is the product of the SAFEs' factors K. Each purchase amount p is solved modulo its K (the Chinese remainder
    theorem) so that the discounted amounts, 1e27 * sum(p / K), fall short of the pre-money's digits v by exactly
    1 / L; the investment is the largest the bounds accept, on just under 1e16 fully diluted shares and no pool
    target. Every value is within the input bounds (``equity_calculator.schemas.equity_common``); ``ValueError`` when a
    solved number would not be (measured over 1 to 50 SAFEs: every count up to 20 builds except 6, none above 20).
    """
    factors: list[int] = []
    taken = _BASE
    candidate = _LARGEST_FACTOR
    while len(factors) < safe_count:
        if math.gcd(candidate, taken) == 1:
            factors.append(candidate)
            taken *= candidate
        candidate -= _FACTOR_STEP
    product = taken // _BASE
    amounts = [(-pow(_SHIFT * (product // factor) % factor, -1, factor)) % factor for factor in factors]
    discounted = _SHIFT * sum(amount * (product // factor) for amount, factor in zip(amounts, factors, strict=True))
    pre_money, remainder = divmod(1 + discounted, product)
    if remainder or min(amounts) < _SMALLEST_AMOUNT_DIGITS or not _SMALLEST_PRE_MONEY_DIGITS <= pre_money < _SCALE:
        raise ValueError(f"no in-bounds sliver round with {safe_count} SAFEs")

    safes = [
        {
            "kind": "safe",
            "purchase_amount": _plain(amount, _AMOUNT_EXPONENT),
            "discount_percent": _plain(_SCALE - factor, _PERCENT_EXPONENT),
        }
        for amount, factor in zip(amounts, factors, strict=True)
    ]
    return {
        "fully_diluted_shares": SIZE_LIMIT - 1,
        "pre_money": _plain(pre_money, _PRE_MONEY_EXPONENT),
        "investment": _LARGEST_MONEY,
        "target_pool_percent": "0",
        "instruments": safes,
    }


# Three rounds for a 50% holder: 20% sold with a 10% new pool, 20% with 5%, then 15% with no pool, so the stake goes
# 1/2 -> 7/20 -> 21/80 -> 357/1600 (0.223125).
DILUTION_ROUNDS: list[dict[str, object]] = [
    {"investor_percent": "20", "pool_percent": "10"},
    {"investor_percent": "20", "pool_percent": "5"},
    {"investor_percent": "15"},
]


def dilution(**fields: object) -> DilutionResult:
    """One holder's dilution for ``fields`` (a ``DilutionInput``'s fields)."""
    return compute(DilutionInput.model_validate(fields))


def vesting(**fields: object) -> VestingResult:
    """A grant's vesting for ``fields`` (a ``VestingInput``'s fields; months and shares are ints)."""
    return compute(VestingInput.model_validate(fields))


# Two preferred classes beside 7M common shares, each 1x and rank 1 with no participation: A holds 2M shares and put
# in $5M, B holds 1M shares and put in $10M. At a $50M exit B takes its $10M and A converts for 2/9 of the $40M left.
WATERFALL_A: dict[str, object] = {"shares": 2_000_000, "invested": "5000000"}
WATERFALL_B: dict[str, object] = {"shares": 1_000_000, "invested": "10000000"}
WATERFALL_COMMON = 7_000_000


def waterfall(exit_amount: str, *classes: dict[str, object], common_shares: int = WATERFALL_COMMON) -> WaterfallResult:
    """The exit waterfall of ``exit_amount`` over ``classes`` (``PreferredClass`` fields) and the common shares."""
    fields = {"exit_amount": exit_amount, "common_shares": common_shares, "classes": list(classes)}

    return compute(WaterfallInput.model_validate(fields))


# Three made-up decks, worked by hand in the design notes and by exact fractions in test_deal_check.py.
# Company A: $3M at a $12M pre-money for 20%, a 10% pool in the pre-money, 8M founder shares, $400k in the bank and a
# planned $180k a month: runway 170/9 months, not the 24 the deck claims.
DEAL_A: dict[str, object] = {
    "investment": "3000000",
    "pre_money": "12000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 8_000_000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "holder_percent": "100",
    "cash_on_hand": "400000",
    "planned_monthly_gross_burn": "180000",
    "stated_runway_months": "24",
}
# Company B: an $8M Series A at $32M pre ($40M post) for 20%, two post-money SAFEs ($1M at a $10M cap, $1.5M at a
# $15M cap) and a pool topped up to 10% in the pre-money; founders hold 90% of 10M shares and the deck says 72% after.
DEAL_B: dict[str, object] = {
    "investment": "8000000",
    "pre_money": "32000000",
    "post_money": "40000000",
    "stated_investor_percent": "20",
    "fully_diluted_shares": 10_000_000,
    "unissued_pool_shares": 400_000,
    "target_pool_percent": "10",
    "pool_timing": "pre_money",
    "instruments": [
        {"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "10000000"},
        {"kind": "safe", "purchase_amount": "1500000", "valuation_cap": "15000000"},
    ],
    "holder_percent": "90",
    "stated_holder_percent": "72",
}
# Company C: a $2.5M seed at $10M pre with a $500k note (6% simple for 18 months, $8M cap, 20% discount), founders at
# 100% of 8M shares (the deck says 80% after), $300k in the bank, today $120k burn and $20k revenue a month, planned
# $210k and $35k, a 24-month runway claim and a 50/30/20 use of funds.
DEAL_C: dict[str, object] = {
    "investment": "2500000",
    "pre_money": "10000000",
    "fully_diluted_shares": 8_000_000,
    "instruments": [
        {
            "kind": "note",
            "principal": "500000",
            "interest_rate_percent": "6",
            "months_outstanding": 18,
            "compounding": "simple",
            "valuation_cap": "8000000",
            "discount_percent": "20",
        }
    ],
    "holder_percent": "100",
    "stated_holder_percent": "80",
    "cash_on_hand": "300000",
    "planned_monthly_gross_burn": "210000",
    "planned_monthly_revenue": "35000",
    "current_monthly_gross_burn": "120000",
    "current_monthly_revenue": "20000",
    "stated_runway_months": "24",
    "use_of_funds": [{"percent": "50"}, {"percent": "30"}, {"percent": "20"}],
}


def deal_check(**fields: object) -> DealCheckResult:
    """The deal check for ``fields`` (a ``DealCheckInput``'s fields)."""
    return compute(DealCheckInput.model_validate(fields))
