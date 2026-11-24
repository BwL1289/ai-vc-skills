"""Pydantic models of a founder's cap table checked against itself (``equity_calculator cap_table_check``).

A cap table lists share classes (common, each preferred series, options granted, the unissued option pool, warrants),
often with a line per holder, the percent each class or holder holds, the shares each class may issue, and the SAFEs
and notes not yet converted. The check adds every class up to the fully diluted shares, works each class's and each
holder's exact share, sets every percent the table states beside it (consistent when it is the computed figure
rounded to the places it is typed with), compares issued with authorised shares, lists the unconverted instruments
and the share held by people who have left, and, on the founder's own figures, converts the instruments in a preview
of the next priced round (the ``round`` scenario) and follows the founders through their planned rounds (the
``dilution`` scenario). It never rules on whether a share was validly issued: what the arithmetic cannot settle is a
flag, a question for the company's lawyer.

Classes are numbered in the order given (1 is the first) and holder lines likewise; neither carries a name. A class's
shares are its stated total, or the sum of its holder lines when no total is given; with both, the lines are checked
against the total. Preferred counts one common share per preferred share and a warrant one share per warrant share;
SAFEs and notes stay out of the fully diluted shares until they convert.

Like ``equity_deal_check``, this module reuses other scenarios' models (``equity_round``'s instruments and checks,
``equity_dilution``'s round, the deal check's verdict words), which import no scenario of their own, so no cycle.
``equity_calculator.cap_table_check`` works it; the arithmetic and each convention's source are in ``README.md``.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated, Literal

from equity_calculator.schemas.equity_common import (
    AS_WRITTEN,
    MODEL_CONFIG,
    SIZE_LIMIT,
    WHOLE_PERCENT,
    BoundedDecimal,
    EquityAssumption,
    EquityQuantity,
    PoolTiming,
    ShareCount,
    WrittenDecimal,
)
from equity_calculator.schemas.equity_deal_check import CheckVerdict, DealVerdict
from equity_calculator.schemas.equity_dilution import MAX_ROUNDS, DilutionResult, DilutionRound
from equity_calculator.schemas.equity_round import (
    MAX_INSTRUMENTS,
    Instrument,
    RoundInput,
    RoundResult,
    refuse_caps_over_whole,
    refuse_pool_too_large,
)
from pydantic import BaseModel, Field, ValidationError, model_validator

__all__ = [
    "MAX_CLASSES",
    "MAX_HOLDERS",
    "OPTION_KINDS",
    "STOCK_KINDS",
    "CapCheck",
    "CapCheckKey",
    "CapClassRow",
    "CapHolderRow",
    "CapPreview",
    "CapPreviewClass",
    "CapPreviewInstrument",
    "CapTableCheckInput",
    "CapTableCheckResult",
    "CapTableCheckScenario",
    "CapTableFlag",
    "CommonReserve",
    "FounderPath",
    "Holder",
    "PercentBasis",
    "PlanReserve",
    "PreviewRound",
    "ShareClass",
    "ShareClassKind",
    "class_totals",
    "preview_input",
    "unissued_pool",
]

CapTableCheckScenario = Literal["cap_table_check"]

# A class of the cap table. ``common`` and ``preferred`` are issued stock (each preferred series its own class, counted
# one common share per preferred share); ``options_granted`` are options outstanding under the plan;
# ``options_unissued`` is the unissued pool (reserved, not granted); ``warrants`` count one share per warrant share, as
# if exercised.
ShareClassKind = Literal["common", "preferred", "options_granted", "options_unissued", "warrants"]
STOCK_KINDS: tuple[ShareClassKind, ...] = ("common", "preferred")
OPTION_KINDS: tuple[ShareClassKind, ...] = ("options_granted", "options_unissued")

# What a stated percent is a share of: every fully diluted share, or the issued stock only (common and preferred), on
# which an option or a warrant has no percent.
PercentBasis = Literal["fully_diluted", "outstanding"]

# Which stated figure a check is about: the table's fully diluted total, a class's total against its holder lines, a
# class's or a holder line's percent, or a column of stated percents against 100%: the classes' own
# (``class_percent_total``), or the table read line by line (``line_percent_total``: each class's holder lines where
# every one states a percent, the class's own percent where not).
CapCheckKey = Literal[
    "fully_diluted_total",
    "class_shares",
    "class_percent",
    "class_percent_total",
    "holder_percent",
    "line_percent_total",
]

# What the check turns up beyond the checks. They never change the verdict; their plain words are in
# ``equity_calculator.layout_cap_table_check``. ``percents_do_not_sum``: a column of stated percents (the classes', or
# the table's line by line) cannot all be roundings of shares that add up to 100%. ``consistent_beyond_rounding``: a
# stated figure holds by the tolerance alone. ``over_authorised``: a class issued more than its authorised shares, or
# the option plan granted and reserved more than its reserve. ``common_authorised_below_fully_diluted``: authorised
# common is below the fully diluted shares, every one of which would be common once converted or exercised.
# ``unconverted_instruments_present``: SAFEs or notes are outstanding, outside the fully diluted shares.
# ``departed_holders_share``: people who have left hold shares. ``path_leaves_out_instruments``: the founders' path
# through the planned rounds converts no SAFE or note.
CapTableFlag = Literal[
    "percents_do_not_sum",
    "consistent_beyond_rounding",
    "over_authorised",
    "common_authorised_below_fully_diluted",
    "unconverted_instruments_present",
    "departed_holders_share",
    "path_leaves_out_instruments",
]

# The list caps; the worst case computes at once.
MAX_CLASSES = 20
MAX_HOLDERS = 100

_PERCENT_AS_WRITTEN = "Percent points. " + AS_WRITTEN.format(examples='"40", "12.50"')
# strict: a flag is a real bool and a class number a real int; "yes", 1 or "2" is refused, never read as one.
StrictFlag = Annotated[bool, Field(strict=True)]
ClassNumber = Annotated[int, Field(strict=True, ge=1, le=MAX_CLASSES)]


class ShareClass(BaseModel):
    """One class of the cap table: its kind, its shares as the table states them (optional when holder lines give
    them), the shares it may issue (common and preferred only) and the percent the table states for it."""

    model_config = MODEL_CONFIG

    kind: ShareClassKind
    shares: ShareCount | None = Field(default=None, ge=0)
    authorised_shares: ShareCount | None = Field(default=None, gt=0)
    stated_percent: WrittenDecimal | None = Field(default=None, ge=0, le=WHOLE_PERCENT, description=_PERCENT_AS_WRITTEN)

    @model_validator(mode="after")
    def _authorised_only_for_stock(self) -> ShareClass:
        """Refuse authorised shares on an option or warrant class (the option plan's reserve is its own field)."""
        if self.authorised_shares is not None and self.kind not in STOCK_KINDS:
            raise ValueError(
                "authorised_shares is for a common or preferred class; give the option plan's reserve as "
                "option_plan_reserve"
            )

        return self


class Holder(BaseModel):
    """One holder's line: the class it sits in (``share_class``, 1 for the first class), its shares, the percent the
    table states for it, whether it is a founder's, and whether it is held by someone who has left (vested shares
    they keep)."""

    model_config = MODEL_CONFIG

    share_class: ClassNumber
    shares: ShareCount = Field(gt=0)
    stated_percent: WrittenDecimal | None = Field(default=None, ge=0, le=WHOLE_PERCENT, description=_PERCENT_AS_WRITTEN)
    founder: StrictFlag = False
    departed: StrictFlag = False


class PreviewRound(BaseModel):
    """The next priced round as the founder gives it, to convert the SAFEs and notes in a preview: its pre-money
    valuation, the amount it raises, any pool top-up (``target_pool_percent`` of the shares after it, default 0) and
    where that top-up is counted (default the pre-money)."""

    model_config = MODEL_CONFIG

    pre_money: BoundedDecimal = Field(gt=0)
    investment: BoundedDecimal = Field(gt=0)
    target_pool_percent: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)
    pool_timing: PoolTiming = "pre_money"

    @model_validator(mode="after")
    def _round_can_price(self) -> PreviewRound:
        """Refuse a pool target that would take the whole pre-money (the round's own check)."""
        refuse_pool_too_large(self.pre_money, self.investment, self.target_pool_percent)
        return self


def class_totals(inputs: CapTableCheckInput) -> tuple[int, ...]:
    """Each class's shares: its stated total, else the sum of its holder lines."""
    held = [0] * len(inputs.classes)
    for holder in inputs.holders:
        held[holder.share_class - 1] += holder.shares

    return tuple(item.shares if item.shares is not None else held[index] for index, item in enumerate(inputs.classes))


def unissued_pool(inputs: CapTableCheckInput) -> int:
    """The unissued pool: every ``options_unissued`` class's shares."""
    totals = class_totals(inputs)
    return sum(total for item, total in zip(inputs.classes, totals, strict=True) if item.kind == "options_unissued")


def preview_input(inputs: CapTableCheckInput) -> RoundInput | None:
    """The ``RoundInput`` the conversion preview works, or ``None`` without a preview.

    Built in the validator, so its refusals surface there, and compute only rebuilds a known-valid input.
    """
    preview = inputs.conversion_preview
    if preview is None:
        return None

    try:
        return RoundInput.model_validate(
            {
                "fully_diluted_shares": sum(class_totals(inputs)),
                "unissued_pool_shares": unissued_pool(inputs),
                "pre_money": preview.pre_money,
                "investment": preview.investment,
                "target_pool_percent": preview.target_pool_percent,
                "pool_timing": preview.pool_timing,
                "instruments": inputs.instruments,
            }
        )
    except ValidationError as error:
        reasons = "; ".join(str(failure["msg"]).removeprefix("Value error, ") for failure in error.errors())
        raise ValueError(f"conversion_preview cannot be worked on this cap table: {reasons}") from None


class CapTableCheckInput(BaseModel):
    """A cap table as the founder gives it; see the module docstring.

    Percent fields take percent points (``40`` is 40%). ``classes`` (at least one) and ``holders`` describe the table;
    ``stated_fully_diluted_shares`` is the table's own total, checked against the classes' sum. Every stated percent
    is a share of ``stated_percent_basis``, which is required whenever a percent is stated and has no default.
    ``option_plan_reserve`` is the plan's authorised reserve, set against its granted and unissued options.
    ``instruments`` are the SAFEs and notes outstanding (the round's terms); ``conversion_preview`` converts them at
    the next round the founder gives, and ``planned_rounds`` follows the founders' holder lines through the rounds
    the founder plans. ``tolerance_points`` (default 0) is how far a stated percent may sit from the computed one
    beyond rounding to its own places.
    """

    model_config = MODEL_CONFIG

    scenario: CapTableCheckScenario = "cap_table_check"
    classes: tuple[ShareClass, ...] = Field(min_length=1, max_length=MAX_CLASSES)
    holders: tuple[Holder, ...] = Field(default=(), max_length=MAX_HOLDERS)
    stated_fully_diluted_shares: ShareCount | None = Field(default=None, gt=0)
    stated_percent_basis: PercentBasis | None = None
    option_plan_reserve: ShareCount | None = Field(default=None, gt=0)
    instruments: tuple[Instrument, ...] = Field(default=(), max_length=MAX_INSTRUMENTS)
    conversion_preview: PreviewRound | None = None
    planned_rounds: tuple[DilutionRound, ...] = Field(default=(), max_length=MAX_ROUNDS)
    tolerance_points: BoundedDecimal = Field(default=Decimal(0), ge=0, lt=WHOLE_PERCENT)

    @model_validator(mode="after")
    def _table_can_be_checked(self) -> CapTableCheckInput:
        """Refuse a table with an empty class, a line in a class not given, no shares, a percent with no basis, or a
        preview, path or reserve that has nothing to work on."""
        self._class_rules()
        fully_diluted = sum(class_totals(self))
        if fully_diluted == 0:
            raise ValueError("no class holds a share: give each class's shares or its holder lines")
        if fully_diluted >= SIZE_LIMIT:
            raise ValueError("the shares add up to 1e16 or more, past the calculator's bounds")
        self._percent_rules()
        if self.option_plan_reserve is not None and not any(item.kind in OPTION_KINDS for item in self.classes):
            raise ValueError("option_plan_reserve needs an options_granted or options_unissued class")
        if self.planned_rounds and not any(holder.founder for holder in self.holders):
            raise ValueError("planned_rounds needs at least one holder line marked founder (the founders' shares)")
        if self.conversion_preview is not None:
            if not self.instruments:
                raise ValueError("conversion_preview needs at least one SAFE or note in instruments (it converts them)")
            refuse_caps_over_whole(self.instruments)
            preview_input(self)

        return self

    def _class_rules(self) -> None:
        """Refuse a holder line in a class not given or in the unissued pool, or a class with neither shares nor a
        holder line."""
        held = {holder.share_class for holder in self.holders}
        for number, holder in enumerate(self.holders, start=1):
            if holder.share_class > len(self.classes):
                raise ValueError(
                    f"holders item {number} names share_class {holder.share_class}, past the last of the "
                    f"{len(self.classes)} given"
                )
            if self.classes[holder.share_class - 1].kind == "options_unissued":
                raise ValueError(
                    f"holders item {number} is in the unissued pool, which no one holds: give the pool's shares on "
                    "its class"
                )
        for number, item in enumerate(self.classes, start=1):
            if item.shares is None and number not in held:
                raise ValueError(f"classes item {number} gives neither shares nor a holder line in it")

    def _percent_rules(self) -> None:
        """Refuse a stated percent with no basis, a basis with no stated percent, a stated percent on an option or
        warrant line on the outstanding basis, or the outstanding basis with no stock."""
        class_stated = [(item.kind, item.stated_percent) for item in self.classes]
        holder_stated = [(self.classes[holder.share_class - 1].kind, holder.stated_percent) for holder in self.holders]
        stated = [(kind, value) for kind, value in (*class_stated, *holder_stated) if value is not None]
        if stated and self.stated_percent_basis is None:
            raise ValueError(
                "a stated_percent needs stated_percent_basis: say whether the table's percents are of the fully "
                "diluted shares or of the outstanding stock (common and preferred)"
            )
        if not stated and self.stated_percent_basis is not None:
            raise ValueError("stated_percent_basis is given, but no class or holder line has a stated_percent")
        if self.stated_percent_basis != "outstanding":
            return

        if any(kind not in STOCK_KINDS for kind, _ in stated):
            raise ValueError(
                "on the outstanding basis only common and preferred lines have a percent: leave stated_percent off "
                "option and warrant lines, or use the fully_diluted basis"
            )
        totals = class_totals(self)
        if sum(total for item, total in zip(self.classes, totals, strict=True) if item.kind in STOCK_KINDS) == 0:
            raise ValueError("the outstanding basis needs common or preferred shares")


class CapClassRow(BaseModel):
    """One class worked: its shares, its holder lines' sum, its share of the fully diluted shares and (common and
    preferred only) of the outstanding stock, and its authorised shares with what is left (below 0 when over)."""

    model_config = MODEL_CONFIG

    index: int
    kind: ShareClassKind
    shares: EquityQuantity
    holder_shares: EquityQuantity | None = None
    fully_diluted_fraction: EquityQuantity
    outstanding_fraction: EquityQuantity | None = None
    authorised_shares: EquityQuantity | None = None
    authorised_headroom: EquityQuantity | None = None
    over_authorised: bool | None = None


class CapHolderRow(BaseModel):
    """One holder line worked: its class, its shares and its share of the fully diluted shares and (common and
    preferred only) of the outstanding stock."""

    model_config = MODEL_CONFIG

    index: int
    share_class: int
    kind: ShareClassKind
    shares: EquityQuantity
    fully_diluted_fraction: EquityQuantity
    outstanding_fraction: EquityQuantity | None = None
    founder: bool
    departed: bool


class CapCheck(BaseModel):
    """One stated figure checked: what the table says, what the calculator gives, computed - stated, the verdict.

    ``index`` is the class's or holder line's number (none for a total). ``within_rounding`` says whether a stated
    percent is the computed one rounded half away from zero to the places it is typed with, or, for a percents'
    total, whether its gap from 100% is no more than ``rounding_allowance``: half a unit in the last place of each
    percent added, the most their rounding can explain. None for a share count, which is consistent only when equal.
    """

    model_config = MODEL_CONFIG

    key: CapCheckKey
    index: int | None = None
    stated: EquityQuantity
    computed: EquityQuantity
    difference: EquityQuantity
    verdict: CheckVerdict
    within_rounding: bool | None = None
    rounding_allowance: EquityQuantity | None = None


class PlanReserve(BaseModel):
    """The option plan's reserve against its granted and unissued options; what is left is below 0 when over."""

    model_config = MODEL_CONFIG

    reserve: EquityQuantity
    granted_and_unissued: EquityQuantity
    headroom: EquityQuantity
    over_authorised: bool


class CommonReserve(BaseModel):
    """Authorised common (every common class) against the fully diluted shares, each of which would be common once
    converted or exercised; ``short`` when it is below them."""

    model_config = MODEL_CONFIG

    authorised_common: EquityQuantity
    fully_diluted_shares: EquityQuantity
    headroom: EquityQuantity
    short: bool


class CapPreviewClass(BaseModel):
    """One class (the unissued pool aside) after the preview round: its shares and their share of every share after."""

    model_config = MODEL_CONFIG

    index: int
    kind: ShareClassKind
    shares: EquityQuantity
    fraction_after: EquityQuantity


class CapPreviewInstrument(BaseModel):
    """One SAFE or note in the preview: the price it took, on which basis, its shares and their share after."""

    model_config = MODEL_CONFIG

    index: int
    kind: Literal["safe", "note"]
    conversion_price: EquityQuantity
    basis: Literal["cap", "discount", "round_price"]
    shares: EquityQuantity
    fraction_after: EquityQuantity


class CapPreview(BaseModel):
    """The SAFEs and notes converted in the next round the founder gives (the ``round`` scenario's result, whole),
    read back as the cap table's classes, the pool, each instrument and the new investors after it."""

    model_config = MODEL_CONFIG

    price_per_share: EquityQuantity
    stake_kept: EquityQuantity
    classes: tuple[CapPreviewClass, ...]
    option_pool_after: EquityQuantity
    instruments: tuple[CapPreviewInstrument, ...]
    investors_after: EquityQuantity
    founders_after: EquityQuantity | None = None
    departed_after: EquityQuantity | None = None
    round: RoundResult


class FounderPath(BaseModel):
    """The founders' share through the planned rounds: today's (their holder lines over the fully diluted shares),
    after each round, and after the last. ``dilution`` is the ``dilution`` scenario run on a 100% stake, so its rows
    are each round's share kept; the founders' stakes are today's share times those."""

    model_config = MODEL_CONFIG

    start: EquityQuantity
    stakes: tuple[EquityQuantity, ...]
    final: EquityQuantity
    dilution: DilutionResult


class CapTableCheckResult(BaseModel):
    """The cap table checked: classes and holders worked, totals, authorised shares, each check, flags, the verdict,
    and, on the founder's own figures, the conversion preview and the founders' path."""

    model_config = MODEL_CONFIG

    scenario: CapTableCheckScenario = "cap_table_check"
    inputs: CapTableCheckInput
    classes: tuple[CapClassRow, ...]
    holders: tuple[CapHolderRow, ...]
    fully_diluted_shares: EquityQuantity
    outstanding_shares: EquityQuantity
    founders_fraction: EquityQuantity | None = None
    departed_fraction: EquityQuantity | None = None
    plan_reserve: PlanReserve | None = None
    common_reserve: CommonReserve | None = None
    instruments_amount: EquityQuantity | None = None
    checks: tuple[CapCheck, ...]
    flags: tuple[CapTableFlag, ...]
    verdict: DealVerdict
    preview: CapPreview | None = None
    founder_path: FounderPath | None = None
    assumptions: tuple[EquityAssumption, ...]
