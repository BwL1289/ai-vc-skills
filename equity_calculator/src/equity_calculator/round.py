"""A priced round with SAFEs and notes converting in it: the price, each conversion and the cap table after.

``equity_calculator.convertibles`` finds the price and which instruments take their cap; this module turns that into the
``RoundResult``: one ``ConversionRow`` per instrument (what converts, its cap and discount prices, the price it took,
its shares) and the post-round cap table (existing holders FD - U, each instrument, the option pool U + P, the
investor N = I/p), every share exact and each holder's value at the round price split to the cent.
"""

from __future__ import annotations

from fractions import Fraction
from typing import NamedTuple

from equity_calculator.assumptions_round import round_assumptions
from equity_calculator.convertibles import Convertible, Priced, cap_price, convertibles, other_price, settle
from equity_calculator.exact import ZERO, fraction, money_split, quantity
from equity_calculator.schemas.equity_round import (
    ConversionBasis,
    ConversionRow,
    RoundCapTableRow,
    RoundHolder,
    RoundInput,
    RoundResult,
    SafeTerms,
)

__all__ = ["compute_round", "conversion_row"]


class _Holding(NamedTuple):
    """One cap-table line before rounding: who holds it, which instrument (if one), how many shares."""

    holder: RoundHolder
    instrument: int | None
    shares: Fraction


def _basis(item: Convertible, on_cap: bool) -> ConversionBasis:
    """``cap`` on its cap; else ``discount`` with a discount, ``round_price`` without one."""
    if on_cap:
        return "cap"

    return "round_price" if item.terms.discount_percent is None else "discount"


def conversion_row(item: Convertible, on_cap: bool, priced: Priced, fully_diluted: Fraction) -> ConversionRow:
    """``item`` converted at ``priced``: its cap price, its other price, the one it took and its shares.

    ``fully_diluted`` is the round's FD, the base of a note's cap price; ``on_cap`` is the settled choice for it.
    """
    cap = cap_price(item, priced, fully_diluted)
    other = other_price(item, priced)
    price = cap if on_cap and cap is not None else other
    terms = item.terms
    principal = fraction(terms.purchase_amount if isinstance(terms, SafeTerms) else terms.principal)

    return ConversionRow(
        index=item.index,
        kind=item.terms.kind,
        amount=quantity("money", principal),
        accrued_interest=None if item.interest is None else quantity("money", item.interest.accrued),
        interest_approximate=item.interest is not None and item.interest.approximate,
        converting_amount=quantity("money", item.converting),
        cap_price=None if cap is None else quantity("price", cap),
        discount_price=None if item.terms.discount_percent is None else quantity("price", other),
        conversion_price=quantity("price", price),
        basis=_basis(item, on_cap),
        shares=quantity("shares", item.converting / price),
    )


def compute_round(inputs: RoundInput) -> RoundResult:
    """The round worked exactly: its price, YC's Company Capitalization, each conversion and the cap table.

    Raises ``RoundHasNoPrice`` or ``ConversionDidNotSettle`` (``equity_calculator.errors``) when the round has no
    answer.
    """
    items = convertibles(inputs)
    settled = settle(inputs, items)
    priced = settled.priced
    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    conversions = tuple(
        conversion_row(item, capped, priced, fully_diluted) for item, capped in zip(items, settled.on_cap, strict=True)
    )

    holders = [
        _Holding("existing_holders", None, fully_diluted - unissued),
        *(_Holding(row.kind, row.index, row.shares.exact) for row in conversions),
        _Holding("option_pool", None, unissued + priced.new_pool),
        _Holding("investor", None, priced.investor_shares),
    ]
    total = sum((holding.shares for holding in holders), ZERO)
    values = money_split([holding.shares * priced.price for holding in holders])
    rows = tuple(
        RoundCapTableRow(
            holder=holding.holder,
            instrument=holding.instrument,
            shares=quantity("shares", holding.shares),
            ownership=quantity("fraction", holding.shares / total),
            value=value,
        )
        for holding, value in zip(holders, values, strict=True)
    )

    return RoundResult(
        inputs=inputs,
        price_per_share=quantity("price", priced.price),
        company_capitalization=quantity("shares", priced.capitalization),
        capped_safe_fraction=quantity("fraction", priced.capped_safe_fraction),
        new_pool_shares=quantity("shares", priced.new_pool),
        investor_shares=quantity("shares", priced.investor_shares),
        total_shares=quantity("shares", total),
        post_money=quantity("money", total * priced.price),
        pool_already_large_enough=priced.pool_already_large_enough,
        passes=settled.passes,
        conversions=conversions,
        rows=rows,
        assumptions=round_assumptions(inputs),
    )
