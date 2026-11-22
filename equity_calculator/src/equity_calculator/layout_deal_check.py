"""A deal check's report lines (the ``Deal check`` sheet): the ask as given, what the round does, runway, the checks.

One value column. The ask as given comes first, then the valuation, ownership after the round (one line per SAFE or
note), what the pre-money pays for (with its live total), runway per burn, the use-of-funds lines (with their live
total), each stated figure checked (stated, computed, difference, verdict), the flags in plain words, and the
overall verdict. Values only: no line carries a live formula beyond the ``=SUM`` totals.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.schemas.equity_common import EquityQuantity, EquityUnit
from equity_calculator.schemas.equity_deal_check import DealCheck, DealCheckResult, DealFlag, RunwayRow
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent

_TITLE = "Deal check"
_HEADING = "A fundraising ask checked against itself: valuation, ownership after the round, runway, the deck's figures"
_COLUMNS = ("This ask",)
_KIND_NAMES = {"safe": "SAFE", "note": "Note"}
_VALUATION_HOW = {"pre_money": GIVEN, "post_money": "post-money - I (worked from it)", "percent": "I/percent - I"}
_PART_NAMES = {
    "existing_holders": "existing holders' shares",
    "existing_pool": "unissued pool already there",
    "new_pool": "new pool",
    "conversions": "SAFE and note shares",
}
_PART_HOW = {
    "existing_holders": "(FD - U)·p: the effective pre-money",
    "existing_pool": "U·p",
    "new_pool": "P·p (pool in the pre-money)",
    "conversions": "converted shares·p",
}
_CHECK_NAMES = {
    "post_money": "Post-money",
    "investor_percent": "Investors' percent",
    "holder_percent": "Holder group's percent after",
    "runway_months": "Runway",
    "use_of_funds_total": "Use of funds total",
}
_CHECK_HOW = {
    "post_money": "V + I",
    "investor_percent": "the investor's cap-table share",
    "holder_percent": "h·(share every pre-round share keeps)",
    "runway_months": "(cash + I)/net burn, planned (else current)",
    "use_of_funds_total": "against the raise (or 100%)",
}
_BASIS_NAMES = {"planned": "planned burn", "current": "today's burn"}


def _flag_words(flag: DealFlag, result: DealCheckResult) -> str:
    """What a flag means for the founder, in plain words, and what a VC is likely to ask."""
    inputs = result.inputs
    words: dict[DealFlag, str] = {
        "valuation_back_solved": "No valuation was given, so post-money = raise / percent; label it pre- or "
        "post-money, as a VC will ask which it is",
        "pool_in_pre_money_lowers_price": "The new pool is paid for out of the pre-money, so the effective "
        "pre-money and the price per share are below the headline; a VC prices it this way",
        "pool_in_post_money_dilutes_investor": "The pool is counted after the money, so the investor gets less "
        "than raise / post-money; a VC will likely ask to move it into the pre-money",
        "pool_already_large_enough": "The unissued pool already meets the target: no new pool shares are needed",
        "conversions_bought_by_pre_money": "SAFE and note shares come out of the pre-round holders, not the new "
        "investor, so their stake falls by more than the percent sold; a VC reads the cap table this way",
        "discount_beat_cap": "A discount gave a lower price than the cap, so a cap-only conversion in the deck "
        "would be wrong",
        "note_interest_converts": "Note interest converts too, so a note gets more than its principal's worth of "
        "shares; count it in the cap table",
        "net_burn_not_positive": "Revenue covers the burn on these figures, so there is no net runway figure",
        "current_burn_runway_longer": "Runway on today's burn is longer than on the planned burn; say which one "
        "the deck uses, as a VC will check it against the planned spend",
        "runway_below_band": f"Planned runway is under {inputs.runway_band_months} months; a VC is likely to ask "
        "whether the raise reaches the next milestone (a common benchmark, not a rule)",
        "dilution_above_band": f"The investors get more than {inputs.dilution_band_percent}% in one round; a VC "
        "may ask why so much is sold (a common benchmark, not a rule)",
    }
    return words[flag]


def _given_lines(result: DealCheckResult) -> list[Line]:
    """The ask as given: each input stated, the instruments as a count, the tolerances and bands."""
    inputs = result.inputs
    checked = bool(result.checks)
    shown: list[tuple[str, str, EquityQuantity | str | None]] = [
        ("investment", "Raise (I)", given("money", inputs.investment)),
        ("given_pre_money", "Pre-money as stated", _maybe("money", inputs.pre_money)),
        ("given_post_money", "Post-money as stated", _maybe("money", inputs.post_money)),
        ("given_investor_percent", "Investors' percent as stated", _maybe_percent(inputs.stated_investor_percent)),
        ("fully_diluted_shares", "Fully diluted shares before (FD)", _maybe_shares(inputs.fully_diluted_shares)),
        ("unissued_pool_shares", "Unissued pool before (U)", _maybe_shares(inputs.unissued_pool_shares or None)),
        ("target_pool", "Target pool after the round (t)", _maybe_percent(inputs.target_pool_percent or None)),
        ("pool_timing", "Pool counted in the", inputs.pool_timing.replace("_", "-")),
        ("instruments", "SAFEs and notes", str(len(inputs.instruments))),
        ("holder_percent", "Holder group before (h)", _maybe_percent(inputs.holder_percent)),
        ("given_holder_percent", "Holder group after as stated", _maybe_percent(inputs.stated_holder_percent)),
        ("cash_on_hand", "Cash on hand", given("money", inputs.cash_on_hand) if result.runway else None),
        ("planned_gross_burn", "Planned monthly gross burn", _maybe("money", inputs.planned_monthly_gross_burn)),
        ("planned_revenue", "Planned monthly revenue", _maybe("money", inputs.planned_monthly_revenue)),
        ("current_gross_burn", "Today's monthly gross burn", _maybe("money", inputs.current_monthly_gross_burn)),
        ("current_revenue", "Today's monthly revenue", _maybe("money", inputs.current_monthly_revenue)),
        ("given_runway", "Runway as stated", _maybe("months", inputs.stated_runway_months)),
        ("tolerance_points", "Tolerance for a percent", _when(checked, given_percent(inputs.tolerance_points))),
        ("tolerance_percent", "Tolerance for money or months", _when(checked, given_percent(inputs.tolerance_percent))),
        ("dilution_band", "Dilution benchmark", given_percent(inputs.dilution_band_percent)),
        ("runway_band", "Runway benchmark", _when(bool(result.runway), given("months", inputs.runway_band_months))),
    ]
    return [Line(key, label, (value,), GIVEN) for key, label, value in shown if value is not None]


def _when(shown: bool, value: EquityQuantity) -> EquityQuantity | None:
    return value if shown else None


def _maybe(unit: EquityUnit, value: Decimal | None) -> EquityQuantity | None:
    return None if value is None else given(unit, value)


def _maybe_percent(value: Decimal | None) -> EquityQuantity | None:
    return None if value is None else given_percent(value)


def _maybe_shares(value: int | None) -> EquityQuantity | None:
    return None if value is None else given("shares", Decimal(value))


def _valuation_lines(result: DealCheckResult) -> list[Line]:
    """Pre-money (and how it was read), post-money, the headline share, the investor's real share, the price."""
    source = "pre_money" if result.inputs.pre_money is not None else None
    if source is None:
        source = "post_money" if result.inputs.post_money is not None else "percent"
    lines = [
        Line("pre_money", "Pre-money valuation (V)", (result.pre_money,), _VALUATION_HOW[source]),
        Line("post_money", "Post-money valuation", (result.post_money,), "V + I"),
        Line("headline_investor", "Investors' headline share", (result.headline_investor_fraction,), "I/(V + I)"),
        Line("investor_ownership", "Investors' share of the cap table", (result.investor_ownership,), "N/T"),
    ]
    if result.price_per_share is not None:
        lines.append(Line("price_per_share", "Price per share (p)", (result.price_per_share,), "the round's price"))
    if result.post_money_at_round_price is not None:
        lines.append(
            Line("post_money_at_price", "Every share at the round price", (result.post_money_at_round_price,), "T·p")
        )
    lines.append(
        Line(
            "effective_pre_money",
            "Effective pre-money",
            (result.effective_pre_money,),
            "(FD - U)·p: the pre-round holders' shares at the round price",
        )
    )
    return lines


def _ownership_lines(result: DealCheckResult) -> list[Line]:
    """Who owns what after the round: existing holders, the named group, each SAFE or note, the pool, the investor."""
    lines = []
    if result.existing_holders_ownership is not None:
        lines.append(
            Line("own_existing", "After: existing holders", (result.existing_holders_ownership,), "(FD - U)/T")
        )
    if result.holder_ownership_after is not None:
        lines.append(Line("own_holder", "After: holder group", (result.holder_ownership_after,), "h·kept"))
    if result.round is not None:
        for row in result.round.rows:
            if row.instrument is not None:
                name = f"{_KIND_NAMES[row.holder]} {row.instrument}"
                lines.append(Line(f"own_{row.holder}_{row.instrument}", f"After: {name}", (row.ownership,), "shares/T"))
    if result.pool_ownership_after is not None:
        lines.append(Line("own_pool", "After: option pool", (result.pool_ownership_after,), "(U + P)/T"))
    lines += [
        Line("own_investor", "After: investors", (result.investor_ownership,), "N/T"),
        Line(
            "kept",
            "Share of their stake every pre-round share keeps",
            (result.pre_round_stake_kept,),
            "FD/T, or V/(V + I) with no share counts",
        ),
    ]
    return lines


def _split_lines(result: DealCheckResult) -> list[Line]:
    """What the pre-money pays for, each part to the cent, and its live total (the pre-money)."""
    if not result.pre_money_split:
        return []

    lines = [
        Line(f"split_{item.part}", f"Pre-money pays for: {_PART_NAMES[item.part]}", (item.value,), _PART_HOW[item.part])
        for item in result.pre_money_split
    ]
    keys = tuple(line.key for line in lines)
    lines.append(Line("split_total", "Pre-money pays for: total", (result.pre_money,), "V", keys))
    return lines


def _runway_lines(row: RunwayRow) -> list[Line]:
    """One burn's net burn and its gross and net runway."""
    name = _BASIS_NAMES[row.basis]
    net: EquityQuantity | str = "none: revenue covers the burn" if row.net_runway is None else row.net_runway
    return [
        Line(f"runway_{row.basis}_net_burn", f"Net burn, {name}", (row.net_burn,), "gross burn - revenue"),
        Line(f"runway_{row.basis}_gross", f"Gross runway, {name}", (row.gross_runway,), "(cash + I)/gross burn"),
        Line(f"runway_{row.basis}_net", f"Net runway, {name}", (net,), "(cash + I)/net burn"),
    ]


def _funds_lines(result: DealCheckResult) -> list[Line]:
    """The use-of-funds lines in dollars, their live total, and their share of the raise."""
    if result.use_of_funds_total is None or result.use_of_funds_percent_total is None:
        return []

    lines = [
        Line(f"funds_{index}", f"Use of funds: line {index}", (value,), "as given, or percent·I")
        for index, value in enumerate(result.use_of_funds, start=1)
    ]
    keys = tuple(line.key for line in lines)
    lines += [
        Line("funds_total", "Use of funds: total", (result.use_of_funds_total,), "every line", keys),
        Line("funds_share", "Use of funds: share of the raise", (result.use_of_funds_percent_total,), "total/I"),
    ]
    return lines


def _check_lines(check: DealCheck) -> list[Line]:
    """One check: what the deck says, what the calculator gives, the difference and the verdict."""
    name = _CHECK_NAMES[check.key]
    key = f"check_{check.key}"
    return [
        Line(f"{key}_stated", f"{name}: the deck says", (check.stated,), GIVEN),
        Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), _CHECK_HOW[check.key]),
        Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
        Line(
            f"{key}_verdict", f"{name}: verdict", (check.verdict,), "within the tolerance is consistent", verdict=True
        ),
    ]


def deal_check_sheet(result: DealCheckResult) -> Sheet:
    """The deal check's lines: the ask, the valuation, ownership, the pre-money split, runway, funds, checks, flags."""
    lines = [*_given_lines(result), *_valuation_lines(result), *_ownership_lines(result), *_split_lines(result)]
    for row in result.runway:
        lines += _runway_lines(row)
    lines += _funds_lines(result)
    for check in result.checks:
        lines += _check_lines(check)
    lines += [
        Line(f"flag_{flag}", "A VC is likely to ask", (flag,), _flag_words(flag, result)) for flag in result.flags
    ]
    lines.append(
        Line(
            "verdict",
            "Overall verdict",
            (result.verdict,),
            "mismatch if any check is; consistent if all are; not_checked with none",
            verdict=True,
        )
    )

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
