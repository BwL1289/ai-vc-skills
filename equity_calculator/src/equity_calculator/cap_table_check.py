"""A founder's cap table checked against itself: totals, exact percents, authorised shares, instruments, departures.

Every class's shares (its stated total, else its holder lines' sum) add up to the fully diluted shares FD; common and
preferred add up to the outstanding stock O. Each class and holder line holds shares/FD (and shares/O when it is
stock), exactly. Each figure the table states becomes one check:

- the table's fully diluted total against FD, and a class's total against its holder lines when the founder says
  they are every holder of it (``holder_lines`` complete), or when they add up to more than it: share counts,
  consistent only when equal;
- a class's or holder line's stated percent against its share on the basis the founder names: consistent when it is
  the computed figure rounded half away from zero to the places it is typed with (``equity_calculator.rounding``), or
  within ``tolerance_points`` (0 by default);
- the stated percents' total, of the classes and of the holder lines, when they cover the whole table: consistent when
  its gap from 100% is no more than half a unit in the last place of each percent added (what their rounding can
  explain), plus the tolerance per percent.

Issued shares are set against each class's authorised shares, the option plan's granted and unissued options against
its reserve, and authorised common against FD. SAFEs and notes are listed, never counted; ``conversion_preview``
converts them with ``compute_round`` at the next round the founder gives, and ``planned_rounds`` takes the founders'
share through ``compute_dilution``: from today's share of FD, or, with a preview, from their share after it. When a
class's holder lines add up to more than its stated shares, the founders' and departed holders' shares and the path
rest on a total that does not hold those lines, so they are left out and flagged. Flags never change the verdict; no
line rules on legal validity.
"""

from __future__ import annotations

from collections.abc import Sequence
from decimal import Decimal
from fractions import Fraction

from equity_calculator.assumptions_cap_table_check import cap_table_check_assumptions
from equity_calculator.dilution import compute_dilution
from equity_calculator.exact import HUNDRED, ONE, ZERO, fraction, from_percent, quantity
from equity_calculator.round import compute_round
from equity_calculator.rounding import half_unit, rounds_to
from equity_calculator.schemas.equity_cap_table_check import (
    STOCK_KINDS,
    CapCheck,
    CapCheckKey,
    CapClassRow,
    CapHolderRow,
    CapPreview,
    CapPreviewClass,
    CapPreviewInstrument,
    CapTableCheckInput,
    CapTableCheckResult,
    CapTableFlag,
    CommonReserve,
    FounderPath,
    PathStart,
    PlanReserve,
    ShareClass,
    ShareClassKind,
    class_totals,
    preview_input,
)
from equity_calculator.schemas.equity_common import EquityAssumption, EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import DealVerdict
from equity_calculator.schemas.equity_dilution import DilutionInput
from equity_calculator.schemas.equity_round import RoundInput, instrument_amount

__all__ = ["compute_cap_table_check"]

_WHOLE_STAKE = Decimal(100)


def _on_basis(kind: ShareClassKind, inputs: CapTableCheckInput) -> bool:
    """Whether a line of ``kind`` has a percent on the founder's basis (every line on the fully diluted basis)."""
    return inputs.stated_percent_basis != "outstanding" or kind in STOCK_KINDS


def _optional(unit: EquityUnit, value: Fraction | None) -> EquityQuantity | None:
    return None if value is None else quantity(unit, value)


def _unlisted(item: ShareClass, total: int, held: int | None) -> EquityQuantity | None:
    """A class's shares in none of its holder lines: only where the founder says the lines are some of its holders
    and they stay within its shares."""
    if item.holder_lines != "partial" or held is None or held > total:
        return None

    return quantity("shares", fraction(total - held))


def _class_rows(inputs: CapTableCheckInput, totals: Sequence[int], outstanding: int) -> tuple[CapClassRow, ...]:
    """Each class: its shares, its holder lines' sum (and the shares in none of partial lines), its shares of FD and
    of O, and its authorised shares."""
    fully_diluted = fraction(sum(totals))
    rows = []
    for number, (item, total) in enumerate(zip(inputs.classes, totals, strict=True), start=1):
        lines = [holder.shares for holder in inputs.holders if holder.share_class == number]
        held = sum(lines) if lines else None
        stock = item.kind in STOCK_KINDS and outstanding > 0
        authorised = item.authorised_shares
        rows.append(
            CapClassRow(
                index=number,
                kind=item.kind,
                shares=quantity("shares", fraction(total)),
                holder_shares=None if held is None else quantity("shares", fraction(held)),
                unlisted_shares=_unlisted(item, total, held),
                fully_diluted_fraction=quantity("fraction", fraction(total) / fully_diluted),
                outstanding_fraction=quantity("fraction", fraction(total) / outstanding) if stock else None,
                authorised_shares=None if authorised is None else quantity("shares", fraction(authorised)),
                authorised_headroom=None if authorised is None else quantity("shares", fraction(authorised - total)),
                over_authorised=None if authorised is None else total > authorised,
            )
        )

    return tuple(rows)


def _holder_rows(inputs: CapTableCheckInput, fully_diluted: int, outstanding: int) -> tuple[CapHolderRow, ...]:
    """Each holder line: its class, its shares, and its shares of FD and (stock only) of O."""
    rows = []
    for number, holder in enumerate(inputs.holders, start=1):
        kind = inputs.classes[holder.share_class - 1].kind
        stock = kind in STOCK_KINDS and outstanding > 0
        rows.append(
            CapHolderRow(
                index=number,
                share_class=holder.share_class,
                kind=kind,
                shares=quantity("shares", fraction(holder.shares)),
                fully_diluted_fraction=quantity("fraction", fraction(holder.shares) / fully_diluted),
                outstanding_fraction=quantity("fraction", fraction(holder.shares) / outstanding) if stock else None,
                founder=holder.founder,
                departed=holder.departed,
            )
        )

    return tuple(rows)


def _share_check(key: CapCheckKey, index: int | None, stated: int, computed: int) -> CapCheck:
    """A share count checked: consistent only when it equals the computed count."""
    difference = fraction(computed - stated)
    return CapCheck(
        key=key,
        index=index,
        stated=quantity("shares", fraction(stated)),
        computed=quantity("shares", fraction(computed)),
        difference=quantity("shares", difference),
        verdict="consistent" if difference == ZERO else "mismatch",
    )


def _percent_check(key: CapCheckKey, index: int, written: Decimal, computed: Fraction, tolerance: Fraction) -> CapCheck:
    """A stated percent checked: the computed figure rounded to the places it is typed with, or within the tolerance."""
    stated = from_percent(written)
    difference = computed - stated
    rounds = rounds_to(written, "fraction", computed)
    return CapCheck(
        key=key,
        index=index,
        stated=quantity("fraction", stated),
        computed=quantity("fraction", computed),
        difference=quantity("fraction", difference),
        verdict="consistent" if rounds or abs(difference) <= tolerance else "mismatch",
        within_rounding=rounds,
    )


def _total_check(key: CapCheckKey, written: Sequence[Decimal], tolerance: Fraction) -> CapCheck:
    """The stated percents' total against 100%: consistent within what their rounding explains, plus the tolerance
    for each."""
    stated = sum((from_percent(value) for value in written), ZERO)
    # Each percent's half unit in its last place, in points, as a fraction of the whole (12.50: 0.005 points).
    allowance = sum((half_unit(value) / HUNDRED for value in written), ZERO)
    gap = abs(ONE - stated)
    return CapCheck(
        key=key,
        stated=quantity("fraction", stated),
        computed=quantity("fraction", ONE),
        difference=quantity("fraction", ONE - stated),
        verdict="consistent" if gap <= allowance + tolerance * len(written) else "mismatch",
        within_rounding=gap <= allowance,
        rounding_allowance=quantity("fraction", allowance),
    )


def _fraction_on_basis(row: CapClassRow | CapHolderRow, inputs: CapTableCheckInput) -> Fraction:
    """The line's share on the founder's basis (its validator makes the outstanding share exist when it is used)."""
    if inputs.stated_percent_basis == "outstanding" and row.outstanding_fraction is not None:
        return row.outstanding_fraction.exact

    return row.fully_diluted_fraction.exact


def _line_percents(inputs: CapTableCheckInput, on_basis: Sequence[int]) -> list[Decimal] | None:
    """The table's percent column read line by line: each class's holder lines' stated percents where every one of
    them states one and they are not a partial list, else the class's own; ``None`` when a class has neither, or when
    no holder line's percent is used (the class total covers that)."""
    written: list[Decimal] = []
    used_holder = False
    for number in on_basis:
        lines = [holder.stated_percent for holder in inputs.holders if holder.share_class == number]
        partial = inputs.classes[number - 1].holder_lines == "partial"
        if lines and not partial and all(value is not None for value in lines):
            written.extend(value for value in lines if value is not None)
            used_holder = True
            continue
        own = inputs.classes[number - 1].stated_percent
        if own is None:
            return None
        written.append(own)

    return written if used_holder else None


def _checks(
    inputs: CapTableCheckInput, fully_diluted: int, classes: Sequence[CapClassRow], holders: Sequence[CapHolderRow]
) -> list[CapCheck]:
    """Every stated figure's check, in order: the total, the class totals, the class percents and their total, the
    holder percents, and the percent column's total line by line."""
    tolerance = from_percent(inputs.tolerance_points)
    checks = []
    if inputs.stated_fully_diluted_shares is not None:
        checks.append(_share_check("fully_diluted_total", None, inputs.stated_fully_diluted_shares, fully_diluted))
    for item, row in zip(inputs.classes, classes, strict=True):
        if item.shares is not None and row.holder_shares is not None:
            computed = int(row.holder_shares.exact)
            if item.holder_lines == "complete" or computed > item.shares:
                checks.append(_share_check("class_shares", row.index, item.shares, computed))
    on_basis = [row.index for item, row in zip(inputs.classes, classes, strict=True) if _on_basis(item.kind, inputs)]
    for number in on_basis:
        written = inputs.classes[number - 1].stated_percent
        if written is not None:
            computed = _fraction_on_basis(classes[number - 1], inputs)
            checks.append(_percent_check("class_percent", number, written, computed, tolerance))
    class_written = [inputs.classes[number - 1].stated_percent for number in on_basis]
    if class_written and all(value is not None for value in class_written):
        checks.append(_total_check("class_percent_total", [v for v in class_written if v is not None], tolerance))
    for holder, row in zip(inputs.holders, holders, strict=True):
        if holder.stated_percent is not None and _on_basis(row.kind, inputs):
            computed = _fraction_on_basis(row, inputs)
            checks.append(_percent_check("holder_percent", row.index, holder.stated_percent, computed, tolerance))
    line_written = _line_percents(inputs, on_basis)
    if line_written is not None:
        checks.append(_total_check("line_percent_total", line_written, tolerance))

    return checks


def _plan_reserve(inputs: CapTableCheckInput, totals: Sequence[int]) -> PlanReserve | None:
    """The option plan's reserve against its granted and unissued options, when the reserve is given."""
    reserve = inputs.option_plan_reserve
    if reserve is None:
        return None

    used = sum(
        total
        for item, total in zip(inputs.classes, totals, strict=True)
        if item.kind in ("options_granted", "options_unissued")
    )
    return PlanReserve(
        reserve=quantity("shares", fraction(reserve)),
        granted_and_unissued=quantity("shares", fraction(used)),
        headroom=quantity("shares", fraction(reserve - used)),
        over_authorised=used > reserve,
    )


def _common_reserve(inputs: CapTableCheckInput, fully_diluted: int) -> CommonReserve | None:
    """Authorised common against FD, when every common class gives its authorised shares."""
    common = [item for item in inputs.classes if item.kind == "common"]
    if not common or any(item.authorised_shares is None for item in common):
        return None

    authorised = sum(item.authorised_shares or 0 for item in common)
    return CommonReserve(
        authorised_common=quantity("shares", fraction(authorised)),
        fully_diluted_shares=quantity("shares", fraction(fully_diluted)),
        headroom=quantity("shares", fraction(authorised - fully_diluted)),
        short=authorised < fully_diluted,
    )


def _marked_shares(inputs: CapTableCheckInput) -> tuple[Fraction, Fraction]:
    """The founder lines' shares and the departed lines' shares; a line with both marks counts in each."""
    founders = sum((fraction(holder.shares) for holder in inputs.holders if holder.founder), ZERO)
    departed = sum((fraction(holder.shares) for holder in inputs.holders if holder.departed), ZERO)
    return founders, departed


def _lines_exceed_a_class(classes: Sequence[CapClassRow]) -> bool:
    """Whether a class's holder lines add up to more than its shares (only a stated total can be exceeded)."""
    return any(row.holder_shares is not None and row.holder_shares.exact > row.shares.exact for row in classes)


def _preview(nested: RoundInput, classes: Sequence[CapClassRow], founders: Fraction, departed: Fraction) -> CapPreview:
    """The instruments converted in the founder's next round, read back as the cap table's lines after it; the
    founders' and departed holders' lines only for shares given (zero when they are left out)."""
    result = compute_round(nested)
    total = result.total_shares.exact
    pool = next(row.ownership for row in result.rows if row.holder == "option_pool")
    investors = next(row.ownership for row in result.rows if row.holder == "investor")
    owned = {row.instrument: row.ownership for row in result.rows if row.instrument is not None}

    return CapPreview(
        price_per_share=result.price_per_share,
        stake_kept=quantity("fraction", fraction(nested.fully_diluted_shares) / total),
        classes=tuple(
            CapPreviewClass(
                index=row.index,
                kind=row.kind,
                shares=row.shares,
                fraction_after=quantity("fraction", row.shares.exact / total),
            )
            for row in classes
            if row.kind != "options_unissued"
        ),
        option_pool_after=pool,
        instruments=tuple(
            CapPreviewInstrument(
                index=row.index,
                kind=row.kind,
                conversion_price=row.conversion_price,
                basis=row.basis,
                shares=row.shares,
                fraction_after=owned[row.index],
            )
            for row in result.conversions
        ),
        investors_after=investors,
        founders_after=_optional("fraction", founders / total if founders > ZERO else None),
        departed_after=_optional("fraction", departed / total if departed > ZERO else None),
        round=result,
    )


def _founder_path(
    inputs: CapTableCheckInput, start: Fraction, starts_from: PathStart
) -> tuple[FounderPath, tuple[EquityAssumption, ...]]:
    """The founders' share through the planned rounds, from ``start``: the dilution scenario's share kept per round,
    run on a whole stake so only its kept and post-money figures are read (its stakes are not the founders'); and the
    dilution scenario's assumptions."""
    dilution = compute_dilution(DilutionInput(holder_percent=_WHOLE_STAKE, rounds=inputs.planned_rounds))
    stakes = []
    stake = start
    for row in dilution.rows:
        stake *= row.kept.exact
        stakes.append(quantity("fraction", stake))

    path = FounderPath(
        start=quantity("fraction", start),
        starts_from=starts_from,
        kept=tuple(row.kept for row in dilution.rows),
        post_money=tuple(row.post_money for row in dilution.rows),
        stakes=tuple(stakes),
        final=quantity("fraction", stake),
    )
    return path, dilution.assumptions


def _flags(
    inputs: CapTableCheckInput,
    classes: Sequence[CapClassRow],
    checks: Sequence[CapCheck],
    plan: PlanReserve | None,
    common: CommonReserve | None,
    departed: Fraction,
    exceeded: bool,
) -> tuple[CapTableFlag, ...]:
    """Every flag that holds, in ``CapTableFlag``'s order."""
    flags: list[CapTableFlag] = []
    if exceeded:
        flags.append("holder_lines_exceed_class")
    totals = ("class_percent_total", "line_percent_total")
    if any(check.key in totals and check.verdict == "mismatch" for check in checks):
        flags.append("percents_do_not_sum")
    # A rounding is always consistent, so a figure consistent with no rounding held by the tolerance alone.
    if any(check.verdict == "consistent" and check.within_rounding is False for check in checks):
        flags.append("consistent_beyond_rounding")
    if any(row.over_authorised for row in classes) or (plan is not None and plan.over_authorised):
        flags.append("over_authorised")
    if common is not None and common.short:
        flags.append("common_authorised_below_fully_diluted")
    if inputs.instruments:
        flags.append("unconverted_instruments_present")
    if departed > ZERO:
        flags.append("departed_holders_share")
    # With a preview the path starts after it, its SAFEs and notes converted; with lines past a class there is none.
    if inputs.instruments and inputs.planned_rounds and inputs.conversion_preview is None and not exceeded:
        flags.append("path_leaves_out_instruments")

    return tuple(flags)


def _verdict(checks: Sequence[CapCheck]) -> DealVerdict:
    """``mismatch`` if any check is one, ``consistent`` if all are, ``not_checked`` with none."""
    if not checks:
        return "not_checked"

    return "mismatch" if any(check.verdict == "mismatch" for check in checks) else "consistent"


def _instruments_amount(inputs: CapTableCheckInput) -> Fraction | None:
    """What the SAFEs and notes hold before interest: purchase amounts and principals."""
    if not inputs.instruments:
        return None

    return sum((fraction(instrument_amount(item)[0]) for item in inputs.instruments), ZERO)


def compute_cap_table_check(inputs: CapTableCheckInput) -> CapTableCheckResult:
    """The cap table checked exactly: totals, each line's share, each stated figure's verdict, authorised shares, the
    instruments, the departed holders' share, and the founder's preview and path when given (the path from the
    founders' share after the preview when there is one, from today's when not).

    Raises ``RoundHasNoPrice`` or ``ConversionDidNotSettle`` (``equity_calculator.errors``) when the preview round has
    no answer.
    """
    totals = class_totals(inputs)
    fully_diluted = sum(totals)
    outstanding = sum(total for item, total in zip(inputs.classes, totals, strict=True) if item.kind in STOCK_KINDS)
    classes = _class_rows(inputs, totals, outstanding)
    holders = _holder_rows(inputs, fully_diluted, outstanding)
    checks = tuple(_checks(inputs, fully_diluted, classes, holders))
    founders, departed = _marked_shares(inputs)
    # Lines past their class's shares sit on a total that does not hold them: no founders' or departed share then.
    exceeded = _lines_exceed_a_class(classes)
    shown_founders = ZERO if exceeded else founders
    shown_departed = ZERO if exceeded else departed
    plan = _plan_reserve(inputs, totals)
    common = _common_reserve(inputs, fully_diluted)
    nested = preview_input(inputs)
    preview = None if nested is None else _preview(nested, classes, shown_founders, shown_departed)
    path: FounderPath | None = None
    path_rows: tuple[EquityAssumption, ...] = ()
    if inputs.planned_rounds and not exceeded:
        after = None if preview is None else preview.founders_after
        if after is None:
            path, path_rows = _founder_path(inputs, founders / fully_diluted, "today")
        else:
            path, path_rows = _founder_path(inputs, after.exact, "conversion_preview")
    nested_rows = (*(() if preview is None else preview.round.assumptions), *path_rows)

    return CapTableCheckResult(
        inputs=inputs,
        classes=classes,
        holders=holders,
        fully_diluted_shares=quantity("shares", fraction(fully_diluted)),
        outstanding_shares=quantity("shares", fraction(outstanding)),
        founders_fraction=_optional("fraction", shown_founders / fully_diluted if shown_founders > ZERO else None),
        departed_fraction=_optional("fraction", shown_departed / fully_diluted if shown_departed > ZERO else None),
        plan_reserve=plan,
        common_reserve=common,
        instruments_amount=_optional("money", _instruments_amount(inputs)),
        checks=checks,
        flags=_flags(inputs, classes, checks, plan, common, departed, exceeded),
        verdict=_verdict(checks),
        preview=preview,
        founder_path=path,
        assumptions=cap_table_check_assumptions(
            inputs, bool(checks), nested_rows, None if path is None else path.starts_from
        ),
    )
