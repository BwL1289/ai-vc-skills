"""The price of a priced round with SAFEs and notes converting in it, and which of them convert at their cap.

Each instrument converts an amount a (a SAFE's purchase amount; a note's principal plus accrued interest, or the
principal alone when the interest is paid in cash) at the lower of its cap price and its other price. A post-money
SAFE's cap price is its cap K over YC's Company Capitalization C; a note's is its pre-money cap K over the fully
diluted pre-round shares FD. The other price is the round price p times keep = 1 - discount (keep = 1 with no
discount: the round price itself). With a choice of which capped instruments sit on their cap:

  sigma = sum of a/K over SAFEs on their cap        F = sum of a·FD/K over notes on their cap
  D = sum of a/keep over the rest                    C = (FD + F + D/p)/(1 - sigma)

since C counts FD, the unissued pool included, and every converted share, but not the pool increase made for the
round. Pool in the pre-money (the usual term sheet), with the round's pool target t, unissued pool U, pre-money V
and investment I: num = V - t(V + I) - D/(1 - sigma) must be positive (it is exactly the condition for any price to
exist), p = num/((FD + F)/(1 - sigma) - U) and the new pool is P = t(V + I)/p - U; when P <= 0 the pool is already
large enough, P = 0 and p = (V(1 - sigma) - D)/(FD + F). Pool in the post-money: p = (V(1 - sigma) - D)/(FD + F),
the investor buys N = I/p, and the pool is topped up after, P = max(0, (t(C + N) - U)/(1 - t)). N = I/p either way.

``settle`` finds the choice: every capped instrument starts on its cap; each pass prices the round and puts an
instrument on its cap exactly when its cap price is at most its other price (a tie stays on the cap); it stops when
a pass changes nothing, and raises ``ConversionDidNotSettle`` past its pass limit, one more pass than there are
capped instruments.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from decimal import Decimal
from fractions import Fraction
from typing import Protocol

from equity_calculator.errors import ConversionDidNotSettle, RoundHasNoPrice
from equity_calculator.exact import ONE, ZERO, fraction, from_percent
from equity_calculator.interest import NoteInterest, note_interest
from equity_calculator.schemas.equity_common import PoolTiming
from equity_calculator.schemas.equity_round import NoteTerms, SafeTerms

__all__ = [
    "Convertible",
    "Priced",
    "RoundTerms",
    "Settled",
    "cap_price",
    "convertibles",
    "next_on_cap",
    "other_price",
    "price_round",
    "settle",
]

_FIRST_INDEX = 1


class RoundTerms(Protocol):
    """What pricing a round reads: a ``RoundInput``, or the same terms with exact share counts.

    A round that follows another priced round starts from that round's exact, often fractional, share counts, which
    ``RoundInput``'s whole-number fields cannot hold (``equity_calculator.instrument_compare`` prices such a round).
    """

    @property
    def fully_diluted_shares(self) -> int | Fraction:
        ...

    @property
    def unissued_pool_shares(self) -> int | Fraction:
        ...

    @property
    def pre_money(self) -> Decimal:
        ...

    @property
    def investment(self) -> Decimal:
        ...

    @property
    def target_pool_percent(self) -> Decimal:
        ...

    @property
    def pool_timing(self) -> PoolTiming:
        ...

    @property
    def instruments(self) -> Sequence[SafeTerms | NoteTerms]:
        ...


@dataclass(frozen=True)
class Convertible:
    """One SAFE or note ready to convert: its place (from 1), its terms, what converts, its keep and its cap."""

    index: int
    terms: SafeTerms | NoteTerms
    converting: Fraction
    keep: Fraction
    cap: Fraction | None
    interest: NoteInterest | None


@dataclass(frozen=True)
class Priced:
    """The round priced for one choice of instruments on their cap."""

    price: Fraction
    capitalization: Fraction
    capped_safe_fraction: Fraction
    new_pool: Fraction
    investor_shares: Fraction
    pool_already_large_enough: bool


@dataclass(frozen=True)
class Settled:
    """The settled round: its price, which instruments sit on their cap, and the passes the search took."""

    priced: Priced
    on_cap: tuple[bool, ...]
    passes: int


def _convertible(index: int, terms: SafeTerms | NoteTerms) -> Convertible:
    """``terms`` as a ``Convertible``: a SAFE converts its purchase amount, a note what ``note_interest`` says."""
    keep = ONE if terms.discount_percent is None else ONE - from_percent(terms.discount_percent)
    cap = None if terms.valuation_cap is None else fraction(terms.valuation_cap)
    if isinstance(terms, SafeTerms):
        return Convertible(index, terms, fraction(terms.purchase_amount), keep, cap, None)

    interest = note_interest(terms)
    return Convertible(index, terms, interest.converting, keep, cap, interest)


def convertibles(inputs: RoundTerms) -> tuple[Convertible, ...]:
    """Every instrument of ``inputs`` ready to convert, in the order given."""
    return tuple(_convertible(index, terms) for index, terms in enumerate(inputs.instruments, start=_FIRST_INDEX))


def price_round(inputs: RoundTerms, items: Sequence[Convertible], on_cap: Sequence[bool]) -> Priced:
    """The round's price, Company Capitalization and new shares with exactly the ``on_cap`` instruments on their cap.

    Raises ``RoundHasNoPrice`` when the conversions off their cap leave no positive price.
    """
    fully_diluted = fraction(inputs.fully_diluted_shares)
    unissued = fraction(inputs.unissued_pool_shares)
    pre_money = fraction(inputs.pre_money)
    investment = fraction(inputs.investment)
    target = from_percent(inputs.target_pool_percent)
    sigma = sum(
        (
            item.converting / item.cap
            for item, capped in zip(items, on_cap, strict=True)
            if capped and item.cap is not None and isinstance(item.terms, SafeTerms)
        ),
        ZERO,
    )
    notes_on_cap = sum(
        (
            item.converting * fully_diluted / item.cap
            for item, capped in zip(items, on_cap, strict=True)
            if capped and item.cap is not None and isinstance(item.terms, NoteTerms)
        ),
        ZERO,
    )
    off_cap = sum((item.converting / item.keep for item, capped in zip(items, on_cap, strict=True) if not capped), ZERO)
    base = fully_diluted + notes_on_cap
    no_pool_numerator = pre_money * (ONE - sigma) - off_cap
    if no_pool_numerator <= ZERO:
        raise RoundHasNoPrice(
            "the SAFEs and notes converting off their cap take the whole pre-money valuation: no positive price"
        )

    price = no_pool_numerator / base
    new_pool = ZERO
    already_large_enough = True
    if inputs.pool_timing == "pre_money":
        numerator = pre_money - target * (pre_money + investment) - off_cap / (ONE - sigma)
        if numerator <= ZERO:
            raise RoundHasNoPrice(
                "the pool target and the SAFEs and notes converting off their cap leave no positive price"
            )
        pooled_price = numerator / (base / (ONE - sigma) - unissued)
        needed = target * (pre_money + investment) / pooled_price - unissued
        if needed > ZERO:
            price, new_pool, already_large_enough = pooled_price, needed, False

    capitalization = (base + off_cap / price) / (ONE - sigma)
    investor_shares = investment / price
    if inputs.pool_timing == "post_money":
        needed = (target * (capitalization + investor_shares) - unissued) / (ONE - target)
        new_pool, already_large_enough = max(ZERO, needed), needed <= ZERO

    return Priced(price, capitalization, sigma, new_pool, investor_shares, already_large_enough)


def cap_price(item: Convertible, priced: Priced, fully_diluted: Fraction) -> Fraction | None:
    """``item``'s cap price: a SAFE's cap over Company Capitalization, a note's cap over FD; ``None`` with no cap."""
    if item.cap is None:
        return None
    if isinstance(item.terms, SafeTerms):
        return item.cap / priced.capitalization

    return item.cap / fully_diluted


def other_price(item: Convertible, priced: Priced) -> Fraction:
    """``item``'s price off its cap: the round price times keep (the round price itself with no discount)."""
    return priced.price * item.keep


def next_on_cap(inputs: RoundTerms, items: Sequence[Convertible], priced: Priced) -> tuple[bool, ...]:
    """Which instruments take their cap at ``priced``: those whose cap price is at most their other price."""
    fully_diluted = fraction(inputs.fully_diluted_shares)
    caps = (cap_price(item, priced, fully_diluted) for item in items)

    return tuple(cap is not None and cap <= other_price(item, priced) for item, cap in zip(items, caps, strict=True))


def settle(inputs: RoundTerms, items: Sequence[Convertible], pass_limit: int | None = None) -> Settled:
    """The self-consistent choice of instruments on their cap, from all capped ones on their cap.

    ``pass_limit`` defaults to one more pass than there are capped instruments; raises ``ConversionDidNotSettle``
    when the choice still changes after that many passes.
    """
    limit = sum(item.cap is not None for item in items) + 1 if pass_limit is None else pass_limit
    on_cap = tuple(item.cap is not None for item in items)
    for passes in range(_FIRST_INDEX, limit + 1):
        priced = price_round(inputs, items, on_cap)
        moved = next_on_cap(inputs, items, priced)
        if moved == on_cap:
            return Settled(priced, on_cap, passes)
        on_cap = moved

    raise ConversionDidNotSettle(
        f"which SAFEs and notes convert at their cap still changed after {limit} passes; "
        "this round has no settled conversion"
    )
