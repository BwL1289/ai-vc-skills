"""A fundraising ask checked against itself and the cap table: what the round does, runway, and each stated figure.

The first valuation given sets the pre-money V (``equity_calculator.schemas.equity_deal_check``); post-money is
V + I and the headline share sold I/(V + I). The round is then worked on one of three paths:

- ``round`` (any SAFE or note): ``compute_round``. ``pool`` (a pool top-up, no instruments): ``compute_pool``, the
  deal's pool timing. ``plain`` (neither): the investor gets I/(V + I); with share counts the price is V/FD.
- Every pre-round share keeps FD/T of its stake (V/(V + I) on the plain path); a holder group with h of FD before
  (``holder_percent``, or ``holder_shares``/FD) holds h·FD/T after. The effective pre-money is (FD - U) at the
  round price, as in the pool scenario. The pre-money is split, to the cent, into what it buys: the existing
  holders' shares, the unissued pool, the new pool (when it is counted in the pre-money) and the SAFE and note
  shares; the parts add up to V.
- Runway on each burn given: (cash on hand + I) / burn, net (gross - revenue) and gross; no net runway when revenue
  covers the burn. A runway claim is checked against the planned net runway, else today's.

Each figure the deck states becomes one check: consistent within the tolerance (``tolerance_points`` points for a
percent, ``tolerance_percent`` of the computed figure for the post-money and the runway, the edge included), else a
mismatch. A stated investors' percent, holder group's percent or runway is also consistent when it is the computed
figure rounded half away from zero to the places it is typed with (``12`` months against 12.40, ``17`` against
16.6667%; ``equity_calculator.rounding``): people write figures rounded to the places they show. The post-money is
money, and money keeps the tolerance alone; so does the use-of-funds total, a sum of lines set against the raise or
100%, never a figure the deck types. ``consistent_beyond_rounding`` names a figure that holds by the tolerance alone.
Flags name what a VC is likely to ask and never change a verdict.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction

from equity_calculator.assumptions_deal_check import deal_check_assumptions
from equity_calculator.exact import ONE, ZERO, fraction, from_percent, money_split, quantity
from equity_calculator.funds import work_use_of_funds
from equity_calculator.pool import compute_pool
from equity_calculator.round import compute_round
from equity_calculator.rounding import rounds_to
from equity_calculator.schemas.equity_common import EquityAssumption, EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import (
    CheckKey,
    DealCheck,
    DealCheckInput,
    DealCheckResult,
    DealFlag,
    DealMoneyLine,
    DealPath,
    DealVerdict,
    PreMoneyPart,
    RunwayBasis,
    RunwayRow,
    deal_valuation,
    nested_input,
    unissued_shares,
)
from equity_calculator.schemas.equity_pool import PoolInput, PoolResult
from equity_calculator.schemas.equity_round import RoundInput, RoundResult

__all__ = ["compute_deal_check"]

_CONVERTED = ("safe", "note")


@dataclass(frozen=True)
class _Worked:
    """The round worked on the deal's path: price and shares (with share counts), each group's share, the nested."""

    path: DealPath
    price: Fraction | None
    total_shares: Fraction | None
    investor: Fraction
    kept: Fraction
    existing: Fraction | None
    conversions: Fraction | None
    pool_after: Fraction | None
    new_pool_shares: Fraction
    conversion_shares: Fraction
    round: RoundResult | None = None
    pool: PoolResult | None = None
    assumptions: tuple[EquityAssumption, ...] = ()


def _round_path(inputs: RoundInput) -> _Worked:
    """The round scenario's cap table read as the deal's shares."""
    result = compute_round(inputs)
    total = result.total_shares.exact
    by_holder: dict[str, Fraction] = {}
    for row in result.rows:
        by_holder[row.holder] = by_holder.get(row.holder, ZERO) + row.ownership.exact

    return _Worked(
        path="round",
        price=result.price_per_share.exact,
        total_shares=total,
        investor=by_holder["investor"],
        kept=fraction(inputs.fully_diluted_shares) / total,
        existing=by_holder["existing_holders"],
        conversions=sum((by_holder.get(kind, ZERO) for kind in _CONVERTED), ZERO),
        pool_after=by_holder["option_pool"],
        new_pool_shares=result.new_pool_shares.exact,
        conversion_shares=sum((row.shares.exact for row in result.conversions), ZERO),
        round=result,
        assumptions=result.assumptions,
    )


def _pool_path(inputs: PoolInput) -> _Worked:
    """The pool scenario's table for the deal's own pool timing, read as the deal's shares."""
    result = compute_pool(inputs)
    table = result.pool_in_pre_money if inputs.pool_timing == "pre_money" else result.pool_in_post_money
    by_group = {row.group: row.ownership.exact for row in table.rows}

    return _Worked(
        path="pool",
        price=table.price_per_share.exact,
        total_shares=table.total_shares.exact,
        investor=by_group["investor"],
        kept=fraction(inputs.fully_diluted_shares) / table.total_shares.exact,
        existing=by_group["existing_holders"],
        conversions=None,
        pool_after=by_group["option_pool"],
        new_pool_shares=table.new_pool_shares.exact,
        conversion_shares=ZERO,
        pool=result,
        assumptions=result.assumptions,
    )


def _plain_path(inputs: DealCheckInput, valuation: Fraction) -> _Worked:
    """No pool top-up and no instruments: the investor gets I/(V + I); with share counts the price is V/FD."""
    investment = fraction(inputs.investment)
    kept = valuation / (valuation + investment)
    if inputs.fully_diluted_shares is None:
        return _Worked("plain", None, None, ONE - kept, kept, None, None, None, ZERO, ZERO)

    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(unissued_shares(inputs))
    price = valuation / fully_diluted
    total = fully_diluted + investment / price

    return _Worked(
        path="plain",
        price=price,
        total_shares=total,
        investor=ONE - kept,
        kept=kept,
        existing=(fully_diluted - unissued) / total,
        conversions=None,
        pool_after=unissued / total,
        new_pool_shares=ZERO,
        conversion_shares=ZERO,
    )


def _work(inputs: DealCheckInput, valuation: Fraction) -> _Worked:
    """The deal's path worked; the nested input was already checked by ``DealCheckInput``'s validator."""
    nested = nested_input(inputs)
    if isinstance(nested, RoundInput):
        return _round_path(nested)
    if isinstance(nested, PoolInput):
        return _pool_path(nested)

    return _plain_path(inputs, valuation)


def _pre_money_split(inputs: DealCheckInput, worked: _Worked) -> tuple[DealMoneyLine, ...]:
    """What the pre-money buys, to the cent: existing holders, unissued pool, new pool (pre-money only), conversions."""
    if inputs.fully_diluted_shares is None or worked.price is None:
        return ()

    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(unissued_shares(inputs))
    new_pool = worked.new_pool_shares if inputs.pool_timing == "pre_money" else ZERO
    parts: tuple[tuple[PreMoneyPart, Fraction], ...] = (
        ("existing_holders", fully_diluted - unissued),
        ("existing_pool", unissued),
        ("new_pool", new_pool),
        ("conversions", worked.conversion_shares),
    )
    values = money_split([shares * worked.price for _, shares in parts])

    return tuple(DealMoneyLine(part=part, value=value) for (part, _), value in zip(parts, values, strict=True))


def _runway(inputs: DealCheckInput) -> tuple[RunwayRow, ...]:
    """One row per burn given: net burn, then (cash + I) over the gross and over the net burn (none when net <= 0)."""
    cash = fraction(inputs.cash_on_hand) + fraction(inputs.investment)
    burns: tuple[tuple[RunwayBasis, Decimal | None, Decimal | None], ...] = (
        ("planned", inputs.planned_monthly_gross_burn, inputs.planned_monthly_revenue),
        ("current", inputs.current_monthly_gross_burn, inputs.current_monthly_revenue),
    )
    rows = []
    for basis, gross_given, revenue_given in burns:
        if gross_given is None:
            continue
        gross = fraction(gross_given)
        revenue = ZERO if revenue_given is None else fraction(revenue_given)
        net = gross - revenue
        rows.append(
            RunwayRow(
                basis=basis,
                gross_burn=quantity("money", gross),
                revenue=quantity("money", revenue),
                net_burn=quantity("money", net),
                gross_runway=quantity("months", cash / gross),
                net_runway=quantity("months", cash / net) if net > ZERO else None,
            )
        )

    return tuple(rows)


def _check(
    key: CheckKey,
    unit: EquityUnit,
    stated: Fraction,
    computed: Fraction,
    tolerance: Fraction,
    written: Decimal | None = None,
) -> DealCheck:
    """One check: within ``tolerance`` of the computed figure (the edge included) is consistent, or, given the figure
    as ``written`` (percent points for a fraction), when it is the computed figure rounded to the places it is typed
    with (``within_rounding``)."""
    difference = computed - stated
    rounds = None if written is None else rounds_to(written, unit, computed)

    return DealCheck(
        key=key,
        stated=quantity(unit, stated),
        computed=quantity(unit, computed),
        difference=quantity(unit, difference),
        verdict="consistent" if abs(difference) <= tolerance or rounds else "mismatch",
        within_rounding=rounds,
    )


@dataclass(frozen=True)
class _Funds:
    """The use-of-funds lines in dollars, their total, their share of the raise and the check on them."""

    lines: tuple[EquityQuantity, ...] = ()
    total: EquityQuantity | None = None
    share: EquityQuantity | None = None
    check: DealCheck | None = None


def _use_of_funds(inputs: DealCheckInput) -> _Funds:
    """Amount lines as given, percent lines as dollars of the raise; the total checked against the raise or 100%."""
    worked = work_use_of_funds(
        inputs.use_of_funds, fraction(inputs.investment), inputs.tolerance_points, inputs.tolerance_percent
    )
    if worked is None:
        return _Funds()

    check = _check("use_of_funds_total", worked.unit, worked.stated, worked.computed, worked.tolerance)
    return _Funds(worked.lines, worked.total, worked.share, check)


def _checks(
    inputs: DealCheckInput,
    post_money: Fraction,
    worked: _Worked,
    holder_after: Fraction | None,
    runway: tuple[RunwayRow, ...],
) -> list[DealCheck]:
    """One check per valuation, ownership or runway figure the deck states (the use-of-funds check is added after); the
    percents and the runway go in as written, for the rounding test."""
    source = deal_valuation(inputs)[1]
    points = from_percent(inputs.tolerance_points)
    relative = from_percent(inputs.tolerance_percent)
    checks = []
    if inputs.post_money is not None and source == "pre_money":
        checks.append(_check("post_money", "money", fraction(inputs.post_money), post_money, relative * post_money))
    if inputs.stated_investor_percent is not None and source != "percent":
        written = inputs.stated_investor_percent
        checks.append(_check("investor_percent", "fraction", from_percent(written), worked.investor, points, written))
    if inputs.stated_holder_percent is not None and holder_after is not None:
        written = inputs.stated_holder_percent
        checks.append(_check("holder_percent", "fraction", from_percent(written), holder_after, points, written))
    # The planned burn's net runway, else today's: the first row that has one (none when revenue covers every burn).
    basis = next((row.net_runway for row in runway if row.net_runway is not None), None)
    if inputs.stated_runway_months is not None and basis is not None:
        computed = basis.exact
        written = inputs.stated_runway_months
        checks.append(_check("runway_months", "months", fraction(written), computed, relative * computed, written))

    return checks


def _conversion_flags(worked: _Worked) -> list[DealFlag]:
    """The SAFE and note flags: conversions bought by the pre-money, a discount below the cap, note interest."""
    if worked.round is None:
        return []

    conversions = worked.round.conversions
    flags: list[DealFlag] = ["conversions_bought_by_pre_money"]
    if any(row.cap_price is not None and row.basis == "discount" for row in conversions):
        flags.append("discount_beat_cap")
    if any(row.kind == "note" and row.converting_amount.exact > row.amount.exact for row in conversions):
        flags.append("note_interest_converts")

    return flags


def _flags(
    inputs: DealCheckInput,
    worked: _Worked,
    headline: Fraction,
    runway: tuple[RunwayRow, ...],
    checks: tuple[DealCheck, ...],
) -> tuple[DealFlag, ...]:
    """Every flag that holds, in ``DealFlag``'s order."""
    flags: list[DealFlag] = []
    if deal_valuation(inputs)[1] == "percent":
        flags.append("valuation_back_solved")
    if inputs.pool_timing == "pre_money" and worked.new_pool_shares > ZERO:
        flags.append("pool_in_pre_money_lowers_price")
    if worked.investor < headline:
        flags.append("pool_in_post_money_dilutes_investor")
    if inputs.target_pool_percent > 0 and worked.new_pool_shares == ZERO:
        flags.append("pool_already_large_enough")
    flags += _conversion_flags(worked)
    # A rounding is always consistent, so a figure consistent with no rounding held by the tolerance alone.
    if any(check.verdict == "consistent" and check.within_rounding is False for check in checks):
        flags.append("consistent_beyond_rounding")
    if any(row.net_runway is None for row in runway):
        flags.append("net_burn_not_positive")
    by_basis = {row.basis: row.net_runway for row in runway}
    planned, current = by_basis.get("planned"), by_basis.get("current")
    if planned is not None and current is not None and current.exact > planned.exact:
        flags.append("current_burn_runway_longer")
    basis = runway[0].net_runway if runway else None
    if basis is not None and basis.exact < fraction(inputs.runway_band_months):
        flags.append("runway_below_band")
    if worked.investor > from_percent(inputs.dilution_band_percent):
        flags.append("dilution_above_band")

    return tuple(flags)


def _verdict(checks: tuple[DealCheck, ...]) -> DealVerdict:
    """``mismatch`` if any check is one, ``consistent`` if all are, ``not_checked`` with none."""
    if not checks:
        return "not_checked"

    return "mismatch" if any(check.verdict == "mismatch" for check in checks) else "consistent"


def _holder_before(inputs: DealCheckInput) -> Fraction | None:
    """The named group's share of FD before the round: ``holder_shares``/FD, else ``holder_percent``, else none."""
    if inputs.holder_shares is not None and inputs.fully_diluted_shares is not None:
        return fraction(inputs.holder_shares) / fraction(inputs.fully_diluted_shares)
    if inputs.holder_percent is not None:
        return from_percent(inputs.holder_percent)

    return None


def _optional(unit: EquityUnit, value: Fraction | None) -> EquityQuantity | None:
    return None if value is None else quantity(unit, value)


def compute_deal_check(inputs: DealCheckInput) -> DealCheckResult:
    """The ask checked exactly: what the round does, the runway, each stated figure's verdict and the flags.

    Raises ``RoundHasNoPrice`` or ``ConversionDidNotSettle`` (``equity_calculator.errors``) when the nested round has
    no answer.
    """
    valuation = deal_valuation(inputs)[0]
    investment = fraction(inputs.investment)
    post_money = valuation + investment
    headline = investment / post_money
    worked = _work(inputs, valuation)
    holder_before = _holder_before(inputs)
    holder_after = None if holder_before is None else holder_before * worked.kept
    runway = _runway(inputs)
    funds = _use_of_funds(inputs)
    checks = tuple(_checks(inputs, post_money, worked, holder_after, runway)) + (
        () if funds.check is None else (funds.check,)
    )
    if inputs.fully_diluted_shares is None or worked.price is None:
        effective = valuation
    else:
        effective = (fraction(inputs.fully_diluted_shares) - fraction(unissued_shares(inputs))) * worked.price
    at_round_price = None if worked.price is None or worked.total_shares is None else worked.total_shares * worked.price

    return DealCheckResult(
        inputs=inputs,
        path=worked.path,
        pre_money=quantity("money", valuation),
        post_money=quantity("money", post_money),
        effective_pre_money=quantity("money", effective),
        post_money_at_round_price=_optional("money", at_round_price),
        price_per_share=_optional("price", worked.price),
        headline_investor_fraction=quantity("fraction", headline),
        investor_ownership=quantity("fraction", worked.investor),
        pre_round_stake_kept=quantity("fraction", worked.kept),
        holder_ownership_after=_optional("fraction", holder_after),
        existing_holders_ownership=_optional("fraction", worked.existing),
        conversions_ownership=_optional("fraction", worked.conversions),
        pool_ownership_after=_optional("fraction", worked.pool_after),
        pre_money_split=_pre_money_split(inputs, worked),
        runway=runway,
        use_of_funds=funds.lines,
        use_of_funds_total=funds.total,
        use_of_funds_percent_total=funds.share,
        checks=checks,
        flags=_flags(inputs, worked, headline, runway, checks),
        verdict=_verdict(checks),
        round=worked.round,
        pool=worked.pool,
        assumptions=deal_check_assumptions(inputs, bool(checks), worked.assumptions),
    )
