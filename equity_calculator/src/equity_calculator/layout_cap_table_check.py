"""A cap table check's report lines (the ``Cap table check`` sheet): the table as given, its tie-outs, the checks.

One value column. The table as given comes first (each class, then each holder line), then each class worked (its
shares, the shares in none of partial holder lines, its share of the fully diluted shares and of the outstanding
stock, its authorised shares and what is left), the fully diluted total (a live ``=SUM`` of the class lines) and the
outstanding stock, each holder line's share, the founders' share and the departed holders' share, the option plan's
and authorised common's headroom, the SAFEs and notes outstanding (with their live total), each stated figure checked
(stated, computed, difference, for a percent whether the figure as typed is a rounding of the computed one, verdict),
the conversion preview (the round's own lines for its pool and for what each instrument converts,
``equity_calculator.layout_round``) and the founders' path when given, the flags in plain words, and the overall
verdict. Values only: no line carries a live formula beyond the ``=SUM`` totals.
"""

from __future__ import annotations

from decimal import Decimal

from equity_calculator.exact import fraction, quantity
from equity_calculator.layout_round import converting_lines, new_pool_line, pool_met_line, pool_target_lines
from equity_calculator.rounding import rounding_how, rounding_label, rounding_verdict_how
from equity_calculator.schemas.equity_cap_table_check import (
    CapCheck,
    CapTableCheckInput,
    CapTableCheckResult,
    CapTableFlag,
    ShareClassKind,
)
from equity_calculator.schemas.equity_common import EquityQuantity
from equity_calculator.schemas.equity_round import instrument_amount
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given, given_percent, yes_no

_TITLE = "Cap table check"
_HEADING = "A cap table checked against itself: totals, each line's share, authorised shares, instruments, departures"
_COLUMNS = ("This cap table",)
_KIND_NAMES: dict[ShareClassKind, str] = {
    "common": "common",
    "preferred": "preferred",
    "options_granted": "options granted",
    "options_unissued": "unissued pool",
    "warrants": "warrants",
}
_INSTRUMENT_NAMES = {"safe": "SAFE", "note": "Note"}
_BASIS_NAMES = {"fully_diluted": "of the fully diluted shares", "outstanding": "of the outstanding stock"}
_TOTAL_NAMES = {"class_percent_total": "Classes' percents", "line_percent_total": "Percent column, line by line"}
# The rounding test's words (``equity_calculator.rounding``), said of the table rather than a deck.
_DOCUMENT = "table"
_TOTAL_VERDICT_HOW = "a gap within what rounding explains, plus the tolerance for each, is consistent"
# The preview's keys start with this, beside the instruments section's own (the round's lines it reuses included).
_PREVIEW = "preview_"
_PATH_AFTER_PREVIEW = "Founders' path: after the next round (the preview)"


def _class_name(index: int, kind: ShareClassKind) -> str:
    return f"Class {index} ({_KIND_NAMES[kind]})"


def _holder_name(index: int, share_class: int, kind: ShareClassKind) -> str:
    return f"Holder line {index} (class {share_class}, {_KIND_NAMES[kind]})"


def _shares(value: int) -> EquityQuantity:
    return quantity("shares", fraction(value))


def _flag_words(flag: CapTableFlag) -> str:
    """What a flag means for the founder, in plain words, and the question it raises (for the lawyer where legal)."""
    words: dict[CapTableFlag, str] = {
        "holder_lines_exceed_class": "A class's holder lines add up to more than its stated shares, so the holder "
        "lines' percents rest on a total that does not hold them; the founders' and departed holders' shares, the "
        "preview's lines for them and the founders' path are left out until the lines or the class's shares are "
        "corrected",
        "percents_do_not_sum": "The stated percents cannot all be roundings of shares that add up to 100%: a line is "
        "missing, counted twice, or on another basis; find it before the table goes to an investor",
        "consistent_beyond_rounding": "A stated figure is consistent only by the tolerance: it is not the computed "
        "figure rounded to the places it is written with, so an investor recomputing gets a different figure; quote "
        "the calculator's",
        "over_authorised": "A class has issued more shares than the authorised figure given, or the option plan has "
        "granted and reserved more than its reserve; ask the company's lawyer whether the charter or the plan was "
        "amended to cover them",
        "common_authorised_below_fully_diluted": "Authorised common is below the fully diluted shares, all of which "
        "would be common once converted or exercised; ask the company's lawyer whether the charter reserves enough "
        "common",
        "unconverted_instruments_present": "SAFEs or notes are outstanding and hold no shares yet, so every percent "
        "here falls when they convert; list them for investors, and ask the company's lawyer to confirm their terms",
        "departed_holders_share": "People who have left hold shares (the lines marked departed); investors often "
        "ask about it, and the company's lawyer can say whether any repurchase right or unvested shares were handled",
        "path_leaves_out_instruments": "The founders' path starts today and converts no SAFE or note, so it shows "
        "more than the founders would keep once they convert; give the next round as a preview to convert them",
    }
    return words[flag]


def _optional_shares(value: int | None) -> EquityQuantity | str:
    return "from its holder lines" if value is None else _shares(value)


def _given_lines(inputs: CapTableCheckInput, checked: bool) -> list[Line]:
    """The table as given: each class, each holder line, the stated total, the basis, the reserve, the tolerance."""
    lines = []
    for index, item in enumerate(inputs.classes, start=1):
        name = _class_name(index, item.kind)
        lines.append(
            Line(f"given_class_{index}_shares", f"{name}: shares as given", (_optional_shares(item.shares),), GIVEN)
        )
        if item.authorised_shares is not None:
            authorised = _shares(item.authorised_shares)
            lines.append(Line(f"given_class_{index}_authorised", f"{name}: authorised shares", (authorised,), GIVEN))
        if item.stated_percent is not None:
            stated = given_percent(item.stated_percent)
            lines.append(Line(f"given_class_{index}_percent", f"{name}: percent as stated", (stated,), GIVEN))
        if item.holder_lines is not None:
            listed = (item.holder_lines,)
            lines.append(Line(f"given_class_{index}_holder_lines", f"{name}: its holder lines are", listed, GIVEN))
    for index, holder in enumerate(inputs.holders, start=1):
        name = _holder_name(index, holder.share_class, inputs.classes[holder.share_class - 1].kind)
        marks = [word for word, on in (("founder", holder.founder), ("departed", holder.departed)) if on]
        how = GIVEN if not marks else f"{GIVEN}; {' and '.join(marks)}"
        lines.append(Line(f"given_holder_{index}_shares", f"{name}: shares", (_shares(holder.shares),), how))
        if holder.stated_percent is not None:
            stated = given_percent(holder.stated_percent)
            lines.append(Line(f"given_holder_{index}_percent", f"{name}: percent as stated", (stated,), GIVEN))
    if inputs.stated_fully_diluted_shares is not None:
        stated = _shares(inputs.stated_fully_diluted_shares)
        lines.append(Line("given_fully_diluted", "Fully diluted shares as stated", (stated,), GIVEN))
    if inputs.stated_percent_basis is not None:
        basis = _BASIS_NAMES[inputs.stated_percent_basis]
        lines.append(Line("given_basis", "Stated percents are a share", (basis,), GIVEN))
    if inputs.option_plan_reserve is not None:
        reserve = _shares(inputs.option_plan_reserve)
        lines.append(Line("given_plan_reserve", "Option plan reserve", (reserve,), GIVEN))
    if checked:
        tolerance = given_percent(inputs.tolerance_points)
        lines.append(Line("given_tolerance", "Tolerance for a percent", (tolerance,), GIVEN))

    return lines


def _class_lines(result: CapTableCheckResult) -> list[Line]:
    """Each class worked, then the fully diluted total (a live sum of the class lines) and the outstanding stock."""
    lines = []
    keys = []
    for row in result.classes:
        name = _class_name(row.index, row.kind)
        key = f"class_{row.index}"
        how = "as given" if result.inputs.classes[row.index - 1].shares is not None else "its holder lines added up"
        lines.append(Line(f"{key}_shares", f"{name}: shares", (row.shares,), how))
        keys.append(f"{key}_shares")
        if row.holder_shares is not None and result.inputs.classes[row.index - 1].shares is not None:
            lines.append(Line(f"{key}_holder_shares", f"{name}: its holder lines", (row.holder_shares,), "added up"))
        if row.unlisted_shares is not None:
            unlisted = row.unlisted_shares
            how = "shares - its holder lines (a partial list)"
            lines.append(Line(f"{key}_unlisted", f"{name}: in no holder line", (unlisted,), how))
        lines.append(Line(f"{key}_fd", f"{name}: of fully diluted", (row.fully_diluted_fraction,), "shares/FD"))
        if row.outstanding_fraction is not None:
            lines.append(Line(f"{key}_out", f"{name}: of outstanding", (row.outstanding_fraction,), "shares/O"))
        if row.authorised_headroom is not None and row.over_authorised is not None:
            headroom = row.authorised_headroom
            lines += [
                Line(f"{key}_headroom", f"{name}: authorised left", (headroom,), "authorised - shares (below 0: over)"),
                Line(f"{key}_over", f"{name}: over authorised", (yes_no(row.over_authorised),), "shares > authorised"),
            ]
    lines += [
        Line("fully_diluted", "Fully diluted shares (FD)", (result.fully_diluted_shares,), "every class", tuple(keys)),
        Line("outstanding", "Outstanding stock (O)", (result.outstanding_shares,), "common and preferred"),
    ]

    return lines


def _holder_lines(result: CapTableCheckResult) -> list[Line]:
    """Each holder line's share, then the founders' and the departed holders' share."""
    lines = []
    for row in result.holders:
        name = _holder_name(row.index, row.share_class, row.kind)
        key = f"holder_{row.index}"
        lines.append(Line(f"{key}_fd", f"{name}: of fully diluted", (row.fully_diluted_fraction,), "shares/FD"))
        if row.outstanding_fraction is not None:
            lines.append(Line(f"{key}_out", f"{name}: of outstanding", (row.outstanding_fraction,), "shares/O"))
    if result.founders_fraction is not None:
        founders = result.founders_fraction
        lines.append(Line("founders", "Founders' lines: of fully diluted", (founders,), "founder lines' shares/FD"))
    if result.departed_fraction is not None:
        departed = result.departed_fraction
        lines.append(Line("departed", "Departed holders: of fully diluted", (departed,), "departed lines' shares/FD"))

    return lines


def _reserve_lines(result: CapTableCheckResult) -> list[Line]:
    """The option plan's reserve and authorised common, each against what it covers."""
    lines = []
    plan = result.plan_reserve
    if plan is not None:
        lines += [
            Line("plan_used", "Option plan: granted and unissued", (plan.granted_and_unissued,), "options classes"),
            Line("plan_headroom", "Option plan: reserve left", (plan.headroom,), "reserve - granted and unissued"),
            Line("plan_over", "Option plan: over its reserve", (yes_no(plan.over_authorised),), "used > reserve"),
        ]
    common = result.common_reserve
    if common is not None:
        lines += [
            Line("common_authorised", "Authorised common", (common.authorised_common,), "every common class"),
            Line("common_headroom", "Authorised common left over FD", (common.headroom,), "authorised common - FD"),
            Line("common_short", "Authorised common below FD", (yes_no(common.short),), "authorised common < FD"),
        ]

    return lines


def _instrument_lines(result: CapTableCheckResult) -> list[Line]:
    """Each SAFE or note outstanding with its amount and terms, and the amounts' live total."""
    if result.instruments_amount is None:
        return []

    lines = []
    keys = []
    for index, item in enumerate(result.inputs.instruments, start=1):
        name = f"{_INSTRUMENT_NAMES[item.kind]} {index}"
        key = f"instrument_{index}"
        amount, label = instrument_amount(item)
        lines.append(Line(f"{key}_amount", f"{name}: {label}", (given("money", amount),), GIVEN))
        keys.append(f"{key}_amount")
        if item.valuation_cap is not None:
            lines.append(Line(f"{key}_cap", f"{name}: valuation cap", (given("money", item.valuation_cap),), GIVEN))
        if item.discount_percent is not None:
            lines.append(Line(f"{key}_discount", f"{name}: discount", (given_percent(item.discount_percent),), GIVEN))
    total = result.instruments_amount
    lines.append(Line("instruments_total", "SAFEs and notes: amount", (total,), "before interest", tuple(keys)))

    return lines


def _typed(check: CapCheck, inputs: CapTableCheckInput) -> Decimal | None:
    """A stated percent as typed (percent points), its places kept; none for a share count or a total."""
    if check.index is None:
        return None
    if check.key == "class_percent":
        return inputs.classes[check.index - 1].stated_percent
    if check.key == "holder_percent":
        return inputs.holders[check.index - 1].stated_percent

    return None


def _check_name(check: CapCheck, inputs: CapTableCheckInput) -> str:
    if check.key == "fully_diluted_total":
        return "Fully diluted shares"
    if check.key in _TOTAL_NAMES:
        return _TOTAL_NAMES[check.key]
    index = check.index or 0
    if check.key == "holder_percent":
        holder = inputs.holders[index - 1]
        return f"{_holder_name(index, holder.share_class, inputs.classes[holder.share_class - 1].kind)} percent"
    name = _class_name(index, inputs.classes[index - 1].kind)
    return f"{name} shares" if check.key == "class_shares" else f"{name} percent"


def _check_how(check: CapCheck, inputs: CapTableCheckInput) -> str:
    if check.key == "fully_diluted_total":
        return "every class added up"
    if check.key == "class_shares":
        return "its holder lines added up"
    if check.key in _TOTAL_NAMES:
        return "every share is 100%"
    basis = inputs.stated_percent_basis or "fully_diluted"
    return "shares/FD" if basis == "fully_diluted" else "shares/O"


def _check_lines(check: CapCheck, inputs: CapTableCheckInput) -> list[Line]:
    """One check: what the table says, what the calculator gives, the difference, the rounding test, the verdict."""
    name = _check_name(check, inputs)
    key = f"check_{check.key}" if check.index is None else f"check_{check.key}_{check.index}"
    lines = [
        Line(f"{key}_stated", f"{name}: the table says", (check.stated,), GIVEN),
        Line(f"{key}_computed", f"{name}: the calculator gives", (check.computed,), _check_how(check, inputs)),
        Line(f"{key}_difference", f"{name}: difference", (check.difference,), "computed - stated"),
    ]
    typed = _typed(check, inputs)
    if check.within_rounding is not None and typed is not None:
        label = rounding_label(name, typed, _DOCUMENT)
        lines.append(Line(f"{key}_rounding", label, (yes_no(check.within_rounding),), rounding_how(_DOCUMENT)))
    if check.rounding_allowance is not None and check.within_rounding is not None:
        allowance = check.rounding_allowance
        lines += [
            Line(f"{key}_allowance", f"{name}: what rounding explains", (allowance,), "half the last place of each"),
            Line(f"{key}_rounding", f"{name}: gap within it", (yes_no(check.within_rounding),), "|difference| ≤ it"),
        ]
    how = "consistent only when equal" if check.within_rounding is None else rounding_verdict_how(_DOCUMENT)
    if check.rounding_allowance is not None:
        how = _TOTAL_VERDICT_HOW
    lines.append(Line(f"{key}_verdict", f"{name}: verdict", (check.verdict,), how, verdict=True))

    return lines


def _preview_lines(result: CapTableCheckResult) -> list[Line]:
    """The SAFEs and notes converted in the founder's next round: its terms and pool, the price, then every line after
    it, each instrument with what it converts (a note's interest included) so its shares multiply out."""
    preview = result.preview
    if preview is None:
        return []

    terms = preview.round.inputs
    conversions = {row.index: row for row in preview.round.conversions}
    lines = [
        Line("preview_pre_money", "Next round: pre-money", (given("money", terms.pre_money),), GIVEN),
        Line("preview_investment", "Next round: raise", (given("money", terms.investment),), GIVEN),
        *pool_target_lines(terms, _PREVIEW),
        Line("preview_price", "Next round: price per share", (preview.price_per_share,), "the round scenario's price"),
        Line("preview_kept", "Next round: share every share today keeps", (preview.stake_kept,), "FD/T"),
        new_pool_line(preview.round, _PREVIEW),
        pool_met_line(preview.round, _PREVIEW),
    ]
    for row in preview.classes:
        name = _class_name(row.index, row.kind)
        lines.append(Line(f"preview_class_{row.index}", f"After: {name}", (row.fraction_after,), "shares/T"))
    lines.append(Line("preview_pool", "After: option pool", (preview.option_pool_after,), "the round's pool/T"))
    for row in preview.instruments:
        name = f"{_INSTRUMENT_NAMES[row.kind]} {row.index}"
        lines += [
            *converting_lines(conversions[row.index], _PREVIEW),
            Line(f"preview_{row.kind}_{row.index}_price", f"{name}: converts at", (row.conversion_price,), row.basis),
            Line(f"preview_{row.kind}_{row.index}_shares", f"{name}: shares", (row.shares,), "amount converting/price"),
            Line(f"preview_{row.kind}_{row.index}_after", f"After: {name}", (row.fraction_after,), "shares/T"),
        ]
    lines.append(Line("preview_investors", "After: new investors", (preview.investors_after,), "shares/T"))
    if preview.founders_after is not None:
        lines.append(Line("preview_founders", "After: founders' lines", (preview.founders_after,), "shares/T"))
    if preview.departed_after is not None:
        lines.append(Line("preview_departed", "After: departed holders", (preview.departed_after,), "shares/T"))

    return lines


def _path_lines(result: CapTableCheckResult) -> list[Line]:
    """The founders' share where the path starts (today, or after the preview's round), after each planned round,
    and at the end."""
    path = result.founder_path
    if path is None:
        return []

    if path.starts_from == "conversion_preview":
        start = Line("path_start", _PATH_AFTER_PREVIEW, (path.start,), "the preview's founders' lines (shares/T)")
        final_how = "after the preview × every kept"
    else:
        start = Line("path_start", "Founders' path: today", (path.start,), "founder lines' shares/FD")
        final_how = "today × every kept"
    lines = [start]
    for index, (stake, kept) in enumerate(zip(path.stakes, path.kept, strict=True), start=1):
        lines.append(Line(f"path_kept_{index}", f"Founders' path: round {index} keeps", (kept,), "1 - n - p"))
        lines.append(Line(f"path_after_{index}", f"Founders' path: after round {index}", (stake,), "before × kept"))
    lines.append(Line("path_final", "Founders' path: after the last round", (path.final,), final_how))

    return lines


def cap_table_check_sheet(result: CapTableCheckResult) -> Sheet:
    """The cap table check's lines: the table, the classes, the holders, reserves, instruments, checks, flags."""
    inputs = result.inputs
    lines = [
        *_given_lines(inputs, bool(result.checks)),
        *_class_lines(result),
        *_holder_lines(result),
        *_reserve_lines(result),
        *_instrument_lines(result),
    ]
    for check in result.checks:
        lines += _check_lines(check, inputs)
    lines += [*_preview_lines(result), *_path_lines(result)]
    lines += [Line(f"flag_{flag}", "Flag", (flag,), _flag_words(flag)) for flag in result.flags]
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
