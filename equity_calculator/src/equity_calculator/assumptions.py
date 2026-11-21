"""The labelled assumptions each result carries, with their sources ("unverified" when no primary source says it).

Every setting a reader could reasonably want another way is listed with the value this run used, so the CLI, the
JSON and the workbook all show what the numbers rest on. The two primary sources are Paul Graham's essay and Sam
Altman's post on employee equity; neither covers option pools, so the pool rules are standard priced-round
arithmetic, marked unverified.
"""

from __future__ import annotations

from equity_calculator.schemas.equity import EmployeeInput, EquityAssumption, InvestorInput, PoolInput

PG_SOURCE = 'Paul Graham, "The Equity Equation", paulgraham.com/equity.html (July 2007)'
ALTMAN_SOURCE = 'Sam Altman, "Employee Equity", blog.samaltman.com/employee-equity (18 Apr 2014)'
UNVERIFIED = "unverified"


def _assumption(key: str, setting: str, statement: str, source: str) -> EquityAssumption:
    return EquityAssumption(key=key, setting=setting, statement=statement, source=source)


def investor_assumptions(inputs: InvestorInput) -> tuple[EquityAssumption, ...]:
    """The investor test's assumptions; the amounts rows appear only when the stake came from amounts."""
    rows = [
        _assumption(
            "outcome_multiplier",
            "the deal's whole effect",
            "m is the deal's whole effect on the company's average outcome, the investor's cash included; a round "
            "that adds only its cash at a fair price has m = (V + I)/V = 1/(1 - n) and breaks even.",
            f'{PG_SOURCE}: "improves your average outcome enough that the (100 - n)% you have left is worth more '
            'than the whole company was before"',
        ),
        _assumption(
            "break_even_verdict",
            "R = 1 is break even, not accept",
            "Accept needs R > 1 strictly; R exactly 1 is its own verdict.",
            f'{PG_SOURCE}: "if the company merely breaks even on the deal, there\'s no reason to do it" (said of '
            "hires; the same test)",
        ),
    ]
    if inputs.pre_money is not None:
        rows.append(
            _assumption(
                "stake_from_amounts",
                "n = I/(V + I)",
                "From amounts, the stake sold is the investment over the post-money valuation: a priced round with "
                "no pool top-up and no other securities converting (the pool scenario covers a top-up).",
                f"{UNVERIFIED} (standard priced-round arithmetic; neither source states it)",
            )
        )
        if inputs.holder_percent is not None:
            rows.append(
                _assumption(
                    "holder_value",
                    "value before = h·V, after = h(1 - n)·m·V",
                    "A holder's dollar value takes the pre-money valuation V as the company's worth before the deal.",
                    UNVERIFIED,
                )
            )

    return tuple(rows)


def employee_assumptions(inputs: EmployeeInput) -> tuple[EquityAssumption, ...]:
    """The employee test's assumptions; the rule-of-thumb rows appear only when its inputs are given."""
    rows = [
        _assumption(
            "grant_rule",
            "i <= 1 grants nothing",
            "A hire who does not raise the average outcome (i = 1, break even) or lowers it (i < 1) is worth no "
            "stake; the break-even stake is floored at 0.",
            f'{PG_SOURCE}: "if the company merely breaks even on the deal, there\'s no reason to do it"',
        ),
    ]
    if inputs.annual_cost is not None:
        rows += [
            _assumption(
                "cost_years",
                f"{inputs.cost_years} years",
                "Rule of thumb: salary and overhead cost this many years of pay in stock (PG's 1.5 assumes the "
                "valuation grows about 3x a year).",
                f'{PG_SOURCE}: "multiply the annual rate by about 1.5"',
            ),
            _assumption(
                "valuation",
                "the valuation given",
                "Rule of thumb: the valuation that prices the salary in stock; PG suggests the post-money valuation "
                "of the last round, which probably undervalues the company.",
                f"{PG_SOURCE}, note 2",
            ),
            _assumption(
                "margin",
                f"{inputs.margin_percent}%",
                "Rule of thumb: the company's \"profit\" on the hire; the retail stake is n/(1 + margin). PG's worked "
                "example uses 50% and says the market sets it.",
                PG_SOURCE,
            ),
            _assumption(
                "offer_floor",
                "offer floored at 0",
                "When the salary's stake cost exceeds the retail stake, the offer is 0 and the result says so.",
                UNVERIFIED,
            ),
        ]

    return tuple(rows)


def pool_assumptions(inputs: PoolInput) -> tuple[EquityAssumption, ...]:
    """The option-pool shuffle's assumptions, with this run's pool timing and share rounding."""
    return (
        _assumption(
            "pool_timing",
            inputs.pool_timing,
            "Which way the deal counts the pool: pre_money (created inside the pre-money valuation, diluting only "
            "the existing holders) or post_money (diluting the investor too). Both are computed; this one is the deal.",
            f"{UNVERIFIED} (common term-sheet practice; neither PG's essay nor Altman's post covers pools)",
        ),
        _assumption(
            "target_pool",
            "unissued pool after the round",
            "The target is the unissued pool's share of the fully diluted shares after the round (old and new "
            "unissued options together).",
            UNVERIFIED,
        ),
        _assumption(
            "price_basis",
            "fully diluted",
            "The price per share divides the pre-money valuation by every pre-round share, the unissued pool "
            "included (and, pool pre-money, the new pool shares too).",
            f'{UNVERIFIED}; {ALTMAN_SOURCE} measures grants as "what percentage of the fully-diluted shares"',
        ),
        _assumption(
            "share_rounding",
            inputs.share_rounding,
            "exact keeps fractional shares; whole_shares rounds the new pool and the investor's shares down at the "
            "exact price and reports the cash left unconverted.",
            UNVERIFIED,
        ),
        _assumption(
            "money_split",
            "largest remainder",
            "Each row's dollar value is rounded to the cent so the rows add up to the rounded total exactly.",
            "display convention",
        ),
    )
