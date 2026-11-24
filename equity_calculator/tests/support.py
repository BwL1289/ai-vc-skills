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
from equity_calculator.schemas.equity_cap_table_check import CapTableCheckInput, CapTableCheckResult
from equity_calculator.schemas.equity_common import (
    MAX_ADJUSTED_EXPONENT,
    MAX_SIGNIFICANT_DIGITS,
    MIN_ADJUSTED_EXPONENT,
    SIZE_LIMIT,
)
from equity_calculator.schemas.equity_deal_check import DealCheckInput, DealCheckResult
from equity_calculator.schemas.equity_dilution import DilutionInput, DilutionResult
from equity_calculator.schemas.equity_instrument_compare import InstrumentCompareInput, InstrumentCompareResult
from equity_calculator.schemas.equity_market_sizing import MarketSizingInput, MarketSizingResult
from equity_calculator.schemas.equity_metrics_check import MetricsCheckInput, MetricsCheckResult
from equity_calculator.schemas.equity_round import RoundInput, RoundResult
from equity_calculator.schemas.equity_runway_plan import RunwayPlanInput, RunwayPlanResult
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


# Made-up runway plans, worked by exact fractions in test_runway_plan.py.
# Company W: $500k in the bank; months 1-3 spend $120k with $10k revenue, months 4-12 $220k with $25k, month 13 on
# $300k with $60k; a downside at half the revenue; $3M or $4M raised now; milestone month 15 with 6 months to raise.
RUNWAY_W_PLAN: list[dict[str, object]] = [
    {"from_month": 1, "gross_burn": "120000", "revenue": "10000"},
    {"from_month": 4, "gross_burn": "220000", "revenue": "25000"},
    {"from_month": 13, "gross_burn": "300000", "revenue": "60000"},
]
RUNWAY_W: dict[str, object] = {
    "cash_on_hand": "500000",
    "cases": [{"name": "plan", "phases": RUNWAY_W_PLAN}, {"name": "downside", "revenue_percent_of_plan": "50"}],
    "raises": [{"amount": "3000000"}, {"amount": "4000000"}],
    "milestones": [15],
    "months_to_raise": 6,
}
# Company X: $1.2M in the bank, $2M now against $3M landing after six months; milestone month 18, 6 months to raise.
RUNWAY_X: dict[str, object] = {
    "cash_on_hand": "1200000",
    "cases": [
        {
            "name": "plan",
            "phases": [
                {"from_month": 1, "gross_burn": "150000", "revenue": "30000"},
                {"from_month": 7, "gross_burn": "200000", "revenue": "50000"},
                {"from_month": 13, "gross_burn": "260000", "revenue": "80000"},
            ],
        },
        {"name": "downside", "revenue_percent_of_plan": "60"},
    ],
    "raises": [{"amount": "2000000"}, {"amount": "3000000", "lands_month": 6}],
    "milestones": [18],
    "months_to_raise": 6,
}
# Company Y: $300k in the bank, $90k a month for three months then $160k with $10k revenue; $1.5M with a stated
# 24-month runway; milestone month 12, 6 months to raise.
RUNWAY_Y: dict[str, object] = {
    "cash_on_hand": "300000",
    "cases": [
        {
            "name": "plan",
            "phases": [
                {"from_month": 1, "gross_burn": "90000"},
                {"from_month": 4, "gross_burn": "160000", "revenue": "10000"},
            ],
        }
    ],
    "raises": [{"amount": "1500000", "stated_runway_months": "24"}],
    "milestones": [12],
    "months_to_raise": 6,
}


def runway_plan(**fields: object) -> RunwayPlanResult:
    """The runway plan for ``fields`` (a ``RunwayPlanInput``'s fields)."""
    return compute(RunwayPlanInput.model_validate(fields))


# Made-up metrics, worked by exact fractions in test_metrics_check.py.
# Company AM, over 12 months: $80k MRR at the start, $24k new, $6k expansion, $2k downgrades, $8k cancelled; last
# month's revenue $125k with $25k of implementation fees; $1.8M net burn. Its deck says $1.5M ARR, 125% net revenue
# retention and a 6.25x burn multiple.
METRICS_AM: dict[str, object] = {
    "period_months": 12,
    "recurring_unit": "monthly",
    "starting_recurring": "80000",
    "new_recurring": "24000",
    "expansion_recurring": "6000",
    "contraction_recurring": "2000",
    "churned_recurring": "8000",
    "month_total_revenue": "125000",
    "month_one_time_revenue": "25000",
    "net_burn": "1800000",
    "stated_arr": "1500000",
    "stated_nrr_percent": "125",
    "stated_burn_multiple": "6.25",
}
# Company AN, one month: 400 customers at the start, 12 lost, 45 new (20 from paid ads); $50k MRR at the start, $5k new,
# $500 expansion, $500 downgrades, $1k cancelled; $36k sales and marketing spend; 75% gross margin; it sells to small
# businesses. Its deck says "monthly churn 2%" and a 7.2-month CAC payback; its model says 9.6 months.
METRICS_AN_PARTS: dict[str, object] = {
    "period_months": 1,
    "starting_recurring": "50000",
    "new_recurring": "5000",
    "expansion_recurring": "500",
    "contraction_recurring": "500",
    "churned_recurring": "1000",
    "customers_start": 400,
    "customers_lost": 12,
    "customers_new": 45,
    "customers_new_paid": 20,
    "sales_marketing_spend": "36000",
    "gross_margin_percent": "75",
    "customer_segment": "smb",
}
METRICS_AN_DECK: dict[str, object] = {
    **METRICS_AN_PARTS,
    "stated_churn_percent": "2",
    "stated_cac_payback_months": "7.2",
}
METRICS_AN_MODEL: dict[str, object] = {**METRICS_AN_PARTS, "stated_cac_payback_months": "9.6"}


def metrics_check(**fields: object) -> MetricsCheckResult:
    """The metrics check for ``fields`` (a ``MetricsCheckInput``'s fields)."""
    return compute(MetricsCheckInput.model_validate(fields))


# Made-up markets, worked by exact fractions in test_market_sizing.py.
# Company AW, vet-clinic software: 18,000 independent clinics at $400 a month, 60% on the systems it integrates with,
# 900 to win, 45 today; 400 multi-site groups, 15 locations each at $300 a location a month, 50% serviceable, 10% of
# them to win, 2 today. An analyst's $2.1B, 40% of it matching; 5 years; the plan needs $8M a year from this market;
# $324k revenue today (45 clinics × $4,800 and 2 groups × $54,000); the deck says a $120M TAM. Its own ranges: price
# $300 to $500, clinics to win 600 to 1,200, the groups' share 5% to 15%.
MARKET_AW: dict[str, object] = {
    "segments": [
        {
            "customers": "18000",
            "price": "400",
            "price_period_months": 1,
            "serviceable_percent": "60",
            "obtainable_customers": "900",
            "customers_today": "45",
        },
        {
            "customers": "400",
            "price": "300",
            "price_period_months": 1,
            "units_per_customer": "15",
            "serviceable_percent": "50",
            "obtainable_percent": "10",
            "customers_today": "2",
        },
    ],
    "top_down": [{"amount": "2100000000", "comparable_percent": "40"}],
    "sensitivity": [
        {"field": "price", "segment": 1, "values": ["300", "500"]},
        {"field": "obtainable_customers", "segment": 1, "values": ["600", "1200"]},
        {"field": "obtainable_percent", "segment": 2, "values": ["5", "15"]},
    ],
    "annual_revenue_today": "324000",
    "som_years": 5,
    "som_target": "8000000",
    "stated_tam": "120000000",
}
# Company AX, a pool-cleaning marketplace keeping a 15% fee: 4,000,000 Sun Belt pools at $1,800 a year, 25%
# serviceable, 2% to win, 3,000 today; 2,500,000 Texas and Florida pools (inside the Sun Belt, so counted twice), 30%
# serviceable, 2% to win; 5,200,000 pools in all; an analyst's $1.1B; the deck says $11.7B; the fee at 10% or 20%.
MARKET_AX: dict[str, object] = {
    "segments": [
        {
            "customers": "4000000",
            "price": "1800",
            "price_period_months": 12,
            "take_rate_percent": "15",
            "serviceable_percent": "25",
            "obtainable_percent": "2",
            "customers_today": "3000",
        },
        {
            "customers": "2500000",
            "price": "1800",
            "price_period_months": 12,
            "take_rate_percent": "15",
            "serviceable_percent": "30",
            "obtainable_percent": "2",
        },
    ],
    "top_down": [{"amount": "1100000000"}],
    "sensitivity": [{"field": "take_rate_percent", "segment": 1, "values": ["10", "20"]}],
    "population": "5200000",
    "stated_tam": "11700000000",
}


def market_sizing(**fields: object) -> MarketSizingResult:
    """The market size for ``fields`` (a ``MarketSizingInput``'s fields)."""
    return compute(MarketSizingInput.model_validate(fields))


# Company BU, made up, worked by exact fractions in test_instrument_compare.py: 8,000,000 founder shares, 1,000,000 for
# the team and a 1,000,000 unissued pool (FD 10,000,000), raising $2,000,000. A: priced at an $8,000,000 pre-money,
# standard terms. B: a note with a $6,000,000 cap, a 20% discount and 5% simple interest, converting in 12 months.
# Next round 1: $6,000,000 at $27,000,000 pre (the note on its cap); next round 2: $2,000,000 at $9,000,000 pre (the
# note on its discount, a down round for A). Exits of $5,000,000 (below the preferences), $20,000,000 and $100,000,000.
COMPARE_BU: dict[str, object] = {
    "founder_shares": 8_000_000,
    "team_shares": 1_000_000,
    "unissued_pool_shares": 1_000_000,
    "investment": "2000000",
    "priced_pre_money": "8000000",
    "priced_preference": {"standard": True},
    "note_valuation_cap": "6000000",
    "note_discount_percent": "20",
    "note_interest_rate_percent": "5",
    "note_compounding": "simple",
    "note_months_to_conversion": 12,
    "next_rounds": [
        {"pre_money": "27000000", "investment": "6000000", "preference": {"standard": True}},
        {"pre_money": "9000000", "investment": "2000000", "preference": {"standard": True}},
    ],
    "exit_amounts": ["5000000", "20000000", "100000000"],
}


def instrument_compare(**fields: object) -> InstrumentCompareResult:
    """The priced-round-or-note comparison for ``fields`` (an ``InstrumentCompareInput``'s fields)."""
    return compute(InstrumentCompareInput.model_validate(fields))


# Company CQ, made up, worked by exact fractions in test_cap_table_check.py: two founders' common (4,500,000 and
# 3,500,000) and a departed early hire's 250,000, under 8,000,000 authorised common; 1,000,000 seed preferred (all of
# its 1,000,000 authorised); 500,000 options granted and a 250,000 unissued pool under a 750,000 reserve; 100,000
# warrants; and a $1,000,000 SAFE at a $12,000,000 cap. The table states 10,000,000 fully diluted shares and percents
# to two places that were worked on it, before the warrants: they add up to 101.00%, against 10,100,000 shares.
CAP_TABLE_CQ: dict[str, object] = {
    "classes": [
        {"kind": "common", "authorised_shares": 8_000_000},
        {"kind": "preferred", "shares": 1_000_000, "authorised_shares": 1_000_000, "stated_percent": "10.00"},
        {"kind": "options_granted", "shares": 500_000, "stated_percent": "5.00"},
        {"kind": "options_unissued", "shares": 250_000, "stated_percent": "2.50"},
        {"kind": "warrants", "shares": 100_000, "stated_percent": "1.00"},
    ],
    "holders": [
        {"share_class": 1, "shares": 4_500_000, "stated_percent": "45.00", "founder": True},
        {"share_class": 1, "shares": 3_500_000, "stated_percent": "35.00", "founder": True},
        {"share_class": 1, "shares": 250_000, "stated_percent": "2.50", "departed": True},
    ],
    "stated_fully_diluted_shares": 10_000_000,
    "stated_percent_basis": "fully_diluted",
    "option_plan_reserve": 750_000,
    "instruments": [{"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "12000000"}],
}

# Company CR, made up: two founders' common (5,000,000 and 3,000,000) and a departed co-founder's 500,000 (marked
# departed only: the founder counts just the two of them as founders), 1,000,000 options granted and a 500,000
# unissued pool (10,000,000 fully diluted), two SAFEs ($1,000,000 at a $10,000,000 cap; $500,000 at an $8,000,000 cap
# and a 20% discount), the founder's next round ($4,000,000 at an $18,000,000 pre-money) and the two rounds planned
# after it (20% sold with a 5% new pool, then 20% sold).
CAP_TABLE_CR: dict[str, object] = {
    "classes": [
        {"kind": "common"},
        {"kind": "options_granted", "shares": 1_000_000},
        {"kind": "options_unissued", "shares": 500_000},
    ],
    "holders": [
        {"share_class": 1, "shares": 5_000_000, "stated_percent": "50", "founder": True},
        {"share_class": 1, "shares": 3_000_000, "stated_percent": "30", "founder": True},
        {"share_class": 1, "shares": 500_000, "stated_percent": "5", "departed": True},
    ],
    "stated_percent_basis": "fully_diluted",
    "instruments": [
        {"kind": "safe", "purchase_amount": "1000000", "valuation_cap": "10000000"},
        {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "8000000", "discount_percent": "20"},
    ],
    "conversion_preview": {"pre_money": "18000000", "investment": "4000000"},
    "planned_rounds": [{"investor_percent": "20", "pool_percent": "5"}, {"investor_percent": "20"}],
}
# Company CR as the command takes it.
CAP_TABLE_CR_ARGV = [
    "cap_table_check",
    "--share-class",
    "kind=common",
    "--share-class",
    "kind=options_granted shares=1,000,000",
    "--share-class",
    "kind=options_unissued shares=500,000",
    "--holder",
    "share-class=1 shares=5,000,000 stated-percent=50 founder",
    "--holder",
    "share-class=1 shares=3,000,000 stated-percent=30 founder",
    "--holder",
    "share-class=1 shares=500,000 stated-percent=5 departed",
    "--stated-percent-basis",
    "fully_diluted",
    "--safe",
    "1,000,000 valuation-cap=10,000,000",
    "--safe",
    "500,000 valuation-cap=8,000,000 discount-percent=20",
    "--preview",
    "pre-money=18,000,000 investment=4,000,000",
    "--planned-round",
    "investor-percent=20 pool-percent=5",
    "--planned-round",
    "investor-percent=20",
]


def cap_table_check(**fields: object) -> CapTableCheckResult:
    """The cap table check for ``fields`` (a ``CapTableCheckInput``'s fields)."""
    return compute(CapTableCheckInput.model_validate(fields))
