"""A priced round now beside a convertible note now: Company BU worked by hand, both branches, interest, several next
rounds, exits on both sides of the preferences, cross-checks against the round and pool scenarios, and refusals.

Pure computation: no DB, no network, nothing written. The CLI, the sheet and the workbook are
``test_instrument_compare_cli.py``; the MCP tool's text path is the shared sample in ``test_mcp_server.py``.

Company BU (``tests.support.COMPARE_BU``), worked by hand. FD = 8M + 1M + 1M = 10M shares.

- Option A today: p = $8M / 10M = 4/5, N = $2M / (4/5) = 2.5M, total 12.5M; founders 8/12.5 = 16/25.
- Option B today: no shares; the note owes $2M × (1 + 5% × 1) = $2.1M at conversion; its cap price is $6M / 10M = 3/5.
- Next round 1 ($6M at $27M pre). B: on its cap, the note takes $2.1M / (3/5) = 3.5M shares; p = $27M / 13.5M = 2;
  N = 3M; total 16.5M; founders 8/16.5 = 16/33. A: p = $27M / 12.5M = 54/25, N = $6M / (54/25) = 25M/9, total
  137.5M/9; founders 8M / (137.5M/9) = 144/275. Founders B - A = 16/33 - 144/275 = -32/825.
- Exit $20M after round 1. A: the next round stays ($6M), A's investors convert, $14M over 12.5M shares = 1.12 each:
  founders $8.96M. B: the next round stays, the note converts, $14M over 13.5M shares = 28/27 each: founders
  $224M/27. Founders B - A = -$17.92M/27.
- Next round 2 ($2M at $9M pre). B: the cap would give 3.5M shares and p = $9M / 13.5M = 2/3, above the cap price, so
  the discount price is lower: p = 9M/(10M + 2.1M / (0.8p)) gives p = 51/80, the note at 51/100 takes 70M/17 shares.
  A: p = $9M / 12.5M = 18/25, below A's 4/5 today.
"""

from __future__ import annotations

from decimal import Decimal
from fractions import Fraction
from typing import Any

import pytest
from equity_calculator.errors import RoundHasNoPrice
from equity_calculator.instrument_compare import option_b_note
from equity_calculator.interest import note_interest
from equity_calculator.schemas.equity_instrument_compare import (
    MAX_EXISTING_INSTRUMENTS,
    MAX_EXISTING_SERIES,
    MAX_EXITS,
    MAX_NEXT_ROUNDS,
    ExitComparison,
    GroupStake,
    HolderGroup,
    InstrumentCompareInput,
    NextRoundComparison,
)
from pydantic import ValidationError
from tests.support import COMPARE_BU, instrument_compare, pool, round_

_STANDARD = {"standard": True}
_FIRST, _SECOND, _THIRD = 0, 1, 2
_M = 1_000_000
_ROUND_ONE = {"pre_money": "27000000", "investment": "6000000", "preference": _STANDARD}


def _stake(stakes: tuple[GroupStake, ...], group: HolderGroup) -> GroupStake:
    return next(stake for stake in stakes if stake.group == group)


def _paid(item: ExitComparison, group: HolderGroup) -> tuple[Fraction, Fraction, Fraction]:
    """``group``'s exact payout under A, under B (each the rounded cents' exact value) and the exact B - A."""
    payout = next(payout for payout in item.payouts if payout.group == group)
    return payout.priced.exact, payout.note.exact, payout.difference.exact


def _bu(**changes: object) -> dict[str, Any]:
    return {**COMPARE_BU, **changes}


def _round(result_rounds: tuple[NextRoundComparison, ...], index: int) -> NextRoundComparison:
    return result_rounds[index]


def test_company_bu_today_matches_the_hand_working_to_the_fraction() -> None:
    result = instrument_compare(**COMPARE_BU)

    assert result.fully_diluted_shares.exact == 10 * _M
    assert result.priced_price.exact == Fraction(4, 5)
    assert result.priced_investor_shares.exact == Fraction(5, 2) * _M
    assert result.priced_total_shares.exact == Fraction(25, 2) * _M
    assert result.note_cap_price is not None and result.note_cap_price.exact == Fraction(3, 5)
    assert result.note_principal.exact == 2 * _M
    assert result.note_owed_at_conversion.exact == Fraction(21, 10) * _M
    assert result.note_interest_at_conversion.exact == Fraction(1, 10) * _M
    founders = _stake(result.stakes_now, "founders")
    assert (founders.priced.exact, founders.note.exact) == (Fraction(16, 25), Fraction(4, 5))
    assert result.founders_ownership_difference_now.exact == Fraction(4, 25)
    new_money = _stake(result.stakes_now, "new_money")
    assert (new_money.priced.exact, new_money.note.exact, new_money.note_shares.exact) == (Fraction(1, 5), 0, 0)


def test_company_bu_next_round_one_matches_the_hand_working_to_the_fraction() -> None:
    first = _round(instrument_compare(**COMPARE_BU).next_rounds, _FIRST)

    assert first.index == 1
    assert first.priced_price.exact == Fraction(54, 25)
    assert first.note_price.exact == 2
    assert first.priced_investor_shares.exact == Fraction(25 * _M, 9)
    assert first.note_investor_shares.exact == 3 * _M
    assert first.priced_total_shares.exact == Fraction(137_500_000, 9)
    assert first.note_total_shares.exact == Fraction(33, 2) * _M
    assert first.note_conversion.basis == "cap"
    assert first.note_conversion.converting_amount.exact == Fraction(21, 10) * _M
    assert first.note_conversion.shares.exact == Fraction(7, 2) * _M
    founders = _stake(first.stakes, "founders")
    assert (founders.priced.exact, founders.note.exact) == (Fraction(144, 275), Fraction(16, 33))
    assert first.founders_ownership_difference.exact == Fraction(-32, 825)
    assert sum(stake.priced.exact for stake in first.stakes) == 1
    assert sum(stake.note.exact for stake in first.stakes) == 1


def test_company_bu_exit_between_the_preferences_matches_the_hand_working() -> None:
    twenty = _round(instrument_compare(**COMPARE_BU).next_rounds, _FIRST).exits[_SECOND]

    assert twenty.exit_amount.exact == 20 * _M
    priced, note, difference = _paid(twenty, "founders")
    assert priced == Fraction(896 * _M, 100)
    assert note == Fraction(224 * _M, 27)
    founders_b = next(payout for payout in twenty.payouts if payout.group == "founders").note
    assert founders_b.rounded == Decimal("8296296.29")  # $8,296,296.296…: the cent goes elsewhere by largest remainder
    assert difference == Fraction(-17_920_000, 27)
    assert twenty.founders_payout_difference.exact == Fraction(-17_920_000, 27)
    assert twenty.priced_preferences_paid.exact == twenty.note_preferences_paid.exact == 6 * _M
    assert _paid(twenty, "next_round_investors")[:2] == (6 * _M, 6 * _M)


def test_the_cap_branch_and_the_discount_branch() -> None:
    """Round 1 puts the note on its cap; round 2's lower price puts it on its discount (51/80 × 80%)."""
    result = instrument_compare(**COMPARE_BU)
    second = _round(result.next_rounds, _SECOND)

    assert _round(result.next_rounds, _FIRST).note_conversion.basis == "cap"
    assert second.note_conversion.basis == "discount"
    assert second.note_price.exact == Fraction(51, 80)
    assert second.note_conversion.discount_price is not None
    assert second.note_conversion.discount_price.exact == Fraction(51, 100)
    assert second.note_conversion.cap_price is not None and second.note_conversion.cap_price.exact == Fraction(3, 5)
    assert second.note_conversion.shares.exact == Fraction(70 * _M, 17)
    assert second.priced_price.exact == Fraction(18, 25)
    for flag in ("cap_below_round_price_now", "note_converts_at_cap", "note_converts_at_discount"):
        assert flag in result.flags
    assert "next_round_below_priced_round_price" in result.flags
    assert "note_converts_at_round_price" not in result.flags


def test_a_note_with_neither_cap_nor_discount_converts_at_the_round_price() -> None:
    result = instrument_compare(
        **_bu(note_valuation_cap=None, note_discount_percent=None, next_rounds=[_ROUND_ONE], exit_amounts=["0"])
    )
    first = _round(result.next_rounds, _FIRST)

    assert first.note_conversion.basis == "round_price"
    assert result.note_cap_price is None
    assert result.flags == ("note_converts_at_round_price", "note_interest_converts", "maturity_not_given")


def test_interest_converts_and_compounding_is_the_interest_code() -> None:
    """Monthly compounding for 12 months is the interest code's figure to the cent; paid in cash, only $2M converts."""
    monthly = _bu(note_compounding="monthly", next_rounds=[_ROUND_ONE])
    result = instrument_compare(**monthly)
    expected = note_interest(option_b_note(InstrumentCompareInput.model_validate(monthly)))

    assert result.note_owed_at_conversion.exact == expected.owed
    assert result.note_owed_at_conversion.rounded == Decimal("2102323.80")
    assert _round(result.next_rounds, _FIRST).note_conversion.converting_amount.exact == expected.owed

    cash = instrument_compare(**_bu(note_interest_paid_in_cash=True, next_rounds=[_ROUND_ONE]))
    converted = _round(cash.next_rounds, _FIRST).note_conversion
    assert converted.converting_amount.exact == 2 * _M
    assert converted.shares.exact == Fraction(10 * _M, 3)
    assert "note_interest_converts" not in cash.flags


def test_several_next_rounds_each_priced_on_option_a_s_shares_and_today_s_fd() -> None:
    result = instrument_compare(**COMPARE_BU)

    assert [comparison.index for comparison in result.next_rounds] == [1, 2]
    assert [comparison.priced_price.exact for comparison in result.next_rounds] == [Fraction(54, 25), Fraction(18, 25)]
    assert [len(comparison.exits) for comparison in result.next_rounds] == [3, 3]
    second_founders = _stake(_round(result.next_rounds, _SECOND).stakes, "founders")
    assert second_founders.note.exact == 8 * _M / (
        10 * _M + Fraction(70 * _M, 17) + Fraction(2 * _M) / Fraction(51, 80)
    )


def test_an_exit_below_every_preference_pays_the_common_nothing() -> None:
    """$5M under $8M (A) and $8.1M (B) of rank-1 preferences: shared as owed, 2:6 and 2.1:6."""
    five = _round(instrument_compare(**COMPARE_BU).next_rounds, _FIRST).exits[_FIRST]

    for group in ("founders", "team", "option_pool"):
        assert _paid(five, group) == (0, 0, 0)
    assert _paid(five, "new_money")[0] == Fraction(5 * _M, 4)
    assert _paid(five, "new_money")[2] == Fraction(35 * _M, 27) - Fraction(5 * _M, 4)
    assert five.priced_preferences_paid.exact == five.note_preferences_paid.exact == 5 * _M


def test_an_exit_above_every_preference_pays_by_ownership() -> None:
    hundred = _round(instrument_compare(**COMPARE_BU).next_rounds, _FIRST).exits[_THIRD]

    assert hundred.priced_preferences_paid.exact == hundred.note_preferences_paid.exact == 0
    assert hundred.founders_payout_difference.exact == (Fraction(16, 33) - Fraction(144, 275)) * 100 * _M


def test_each_option_s_payouts_add_up_to_the_exit_to_the_cent() -> None:
    for comparison in instrument_compare(**COMPARE_BU).next_rounds:
        for item in comparison.exits:
            assert sum(payout.priced.rounded for payout in item.payouts) == item.exit_amount.rounded
            assert sum(payout.note.rounded for payout in item.payouts) == item.exit_amount.rounded


def test_a_senior_next_round_is_paid_first() -> None:
    senior = {**_ROUND_ONE, "preference": {"standard": True, "rank": 1}}
    junior = {"standard": True, "rank": 2}
    result = instrument_compare(**_bu(priced_preference=junior, next_rounds=[senior], exit_amounts=["5000000"]))
    five = _round(result.next_rounds, _FIRST).exits[_FIRST]

    assert _paid(five, "next_round_investors")[0] == 5 * _M
    assert _paid(five, "new_money")[0] == 0


def test_the_pool_left_out_takes_nothing_and_the_rest_still_adds_up() -> None:
    result = instrument_compare(**_bu(pool_at_exit="left_out", next_rounds=[_ROUND_ONE], exit_amounts=["100000000"]))
    hundred = _round(result.next_rounds, _FIRST).exits[_FIRST]

    assert _paid(hundred, "option_pool") == (0, 0, 0)
    assert sum(payout.note.rounded for payout in hundred.payouts) == Decimal("100000000.00")
    assert any(row.key == "pool_at_exit" and row.setting == "the pool is left out" for row in result.assumptions)


def test_option_a_today_is_the_pool_scenario_when_only_a_pool_is_added() -> None:
    """With a 10% pre-money pool target and no SAFE or note, option A's round is the pool scenario's to the share."""
    result = instrument_compare(**_bu(unissued_pool_shares=500_000, priced_target_pool_percent="10"))
    same = pool(
        fully_diluted_shares=9_500_000,
        unissued_pool_shares=500_000,
        pre_money="8000000",
        investment="2000000",
        target_pool_percent="10",
    )
    table = same.pool_in_pre_money

    assert result.priced_price.exact == table.price_per_share.exact
    assert result.priced_new_pool_shares.exact == table.new_pool_shares.exact


def test_existing_instruments_convert_today_in_a_and_at_the_next_round_in_b_as_the_round_scenario_says() -> None:
    """An existing SAFE and a note 6 months old: A's round today and B's round 1 are the round scenario's."""
    safe = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "5000000"}
    old_note = {
        "kind": "note",
        "principal": "250000",
        "interest_rate_percent": "6",
        "compounding": "simple",
        "months_outstanding": 6,
        "discount_percent": "20",
    }
    series = {"shares": 1_000_000, "invested": "1000000", "preference_multiple": "1", "participation": "none"}
    fields = _bu(existing_series=[series], existing_instruments=[safe, old_note], next_rounds=[_ROUND_ONE])
    result = instrument_compare(**fields)
    today = round_(
        fully_diluted_shares=11_000_000,
        unissued_pool_shares=1_000_000,
        pre_money="8000000",
        investment="2000000",
        instruments=[safe, old_note],
    )
    later_note = {**old_note, "months_outstanding": 18}
    b_note = option_b_note(InstrumentCompareInput.model_validate(fields)).model_dump(mode="json")
    later = round_(
        fully_diluted_shares=11_000_000,
        unissued_pool_shares=1_000_000,
        pre_money="27000000",
        investment="6000000",
        instruments=[safe, later_note, b_note],
    )
    first = _round(result.next_rounds, _FIRST)

    assert result.priced_price.exact == today.price_per_share.exact
    assert result.priced_conversions == today.conversions
    assert first.note_price.exact == later.price_per_share.exact
    assert (*first.existing_conversions, first.note_conversion) == later.conversions
    existing = _stake(first.stakes, "existing_investors")
    converted = sum((row.shares.exact for row in later.conversions[:2]), Fraction(0))
    assert existing.note_shares.exact == 1_000_000 + converted


def test_maturity_flags() -> None:
    assert "maturity_not_given" in instrument_compare(**COMPARE_BU).flags
    late = instrument_compare(**_bu(note_maturity_months=6, next_rounds=[_ROUND_ONE]))
    assert "converts_after_maturity" in late.flags and "maturity_not_given" not in late.flags
    on_time = instrument_compare(**_bu(note_maturity_months=24, next_rounds=[_ROUND_ONE]))
    assert not {"converts_after_maturity", "maturity_not_given"} & set(on_time.flags)
    maturity = next(row for row in on_time.assumptions if row.key == "maturity_rule")
    assert maturity.setting == "24 months, compared only"


def test_assumptions_reuse_the_round_and_waterfall_rows_and_state_the_note_terms() -> None:
    keys = [row.key for row in instrument_compare(**COMPARE_BU).assumptions]

    assert len(keys) == len(set(keys))
    for key in ("note_cap_basis", "note_interest", "search", "preference_order", "best_response_search"):
        assert key in keys
    for key in ("comparison_rule", "note_price_rule", "note_interest_terms", "maturity_rule", "series_terms"):
        assert key in keys
    terms = next(row for row in instrument_compare(**COMPARE_BU).assumptions if row.key == "note_interest_terms")
    assert terms.statement.startswith("The note accrues 5% a year, simple interest, for 12 months")


def test_the_founder_s_own_series_terms_replace_standard() -> None:
    """A 2x participating series for A: at $20M its investors keep $4M and share the rest, so founders get less."""
    terms = {"preference_multiple": "2", "participation": "full"}
    plain = {**_ROUND_ONE, "preference": {"preference_multiple": "1", "participation": "none"}}
    result = instrument_compare(**_bu(priced_preference=terms, next_rounds=[plain], exit_amounts=["20000000"]))
    twenty = _round(result.next_rounds, _FIRST).exits[_FIRST]

    assert _paid(twenty, "founders")[0] == Fraction(8 * _M, 12_500_000) * (20 * _M - 6 * _M - 4 * _M)
    assert "standard_preference" not in {row.key for row in result.assumptions}


def test_a_round_with_no_price_is_refused_naming_it() -> None:
    """A $1 next round at a $1 pre-money with a 99% pool target leaves no positive price in B (the note's shares)."""
    no_price = {"pre_money": "1", "investment": "1", "target_pool_percent": "49", "preference": _STANDARD}
    with pytest.raises(RoundHasNoPrice, match="next round 1, option B"):
        instrument_compare(**_bu(note_valuation_cap=None, next_rounds=[no_price]))


def test_no_next_round_with_a_conversion_month_is_refused_and_without_one_switches_mode() -> None:
    """The month the note converts at a next round has no round to belong to: refused, naming the mode. Left out, the
    comparison runs with no next round (``test_instrument_compare_no_round.py``)."""
    with pytest.raises(ValidationError, match="no_next_round_given: note_months_to_conversion"):
        InstrumentCompareInput.model_validate(_bu(next_rounds=[]))
    without = {
        key: value for key, value in COMPARE_BU.items() if key not in ("next_rounds", "note_months_to_conversion")
    }
    assert instrument_compare(**without).mode == "no_next_round"
    assert instrument_compare(**COMPARE_BU).mode == "next_round"


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"investment": "-1"}, "greater than 0"),
        ({"founder_shares": 0}, "greater than 0"),
        ({"team_shares": -1}, "greater than or equal to 0"),
        ({"priced_pre_money": "0"}, "greater than 0"),
        ({"note_discount_percent": "100"}, "less than 100"),
        ({"note_discount_percent": "150"}, "less than 100"),
        ({"note_discount_percent": "0"}, "greater than 0"),
        ({"note_interest_rate_percent": "-5"}, "greater than or equal to 0"),
        ({"note_months_to_conversion": 601}, "less than or equal to 600"),
        ({"note_months_to_conversion": "12"}, "valid integer"),
        ({"note_maturity_months": 0}, "greater than or equal to 1"),
        ({"exit_amounts": ["-1"]}, "greater than or equal to 0"),
        ({"exit_amounts": []}, "exit_amounts is empty"),
        ({"priced_preference": {}}, "give standard"),
        ({"priced_preference": {"standard": True, "participation": "none"}}, "give it alone"),
        ({"priced_preference": {"standard": "yes"}}, "valid boolean"),
        ({"priced_preference": {"preference_multiple": "1", "participation": "capped"}}, "needs cap_multiple"),
        ({"priced_target_pool_percent": "80"}, "priced_target_pool_percent must be below"),
        ({"next_rounds": [{**_ROUND_ONE, "investment": "0"}]}, "greater than 0"),
        ({"next_rounds": [{**_ROUND_ONE, "target_pool_percent": "90"}]}, "target_pool_percent must be below"),
        ({"next_rounds": [{"pre_money": "27000000", "investment": "6000000"}]}, "Field required"),
        ({"existing_series": [{"shares": 0, "invested": "1"}]}, "greater than 0"),
        ({"unknown": 1}, "Extra inputs are not permitted"),
    ],
)
def test_validation_errors(changes: dict[str, object], message: str) -> None:
    with pytest.raises(ValidationError, match=message):
        InstrumentCompareInput.model_validate(_bu(**changes))


def test_an_existing_note_needs_months_and_fits_the_month_limit() -> None:
    dated = {
        "kind": "note",
        "principal": "100000",
        "interest_rate_percent": "5",
        "issue_date": "2025-01-01",
        "conversion_date": "2025-07-01",
    }
    with pytest.raises(ValidationError, match="months_outstanding as of today"):
        InstrumentCompareInput.model_validate(_bu(existing_instruments=[dated]))
    old = {"kind": "note", "principal": "100000", "interest_rate_percent": "5", "months_outstanding": 595}
    with pytest.raises(ValidationError, match="over 600 months"):
        InstrumentCompareInput.model_validate(_bu(existing_instruments=[old]))


@pytest.mark.parametrize(
    "series",
    [
        {"shares": 1_000_000, "invested": "3000000"},
        {"shares": 1_000_000, "invested": "3000000", "preference_multiple": "1"},
        {"shares": 1_000_000, "invested": "3000000", "participation": "none"},
    ],
)
def test_an_existing_series_without_its_own_multiple_and_participation_is_refused(series: dict[str, object]) -> None:
    """The waterfall's 1x non-participating default is never taken for an existing series: the founder gives both."""
    with pytest.raises(ValidationError, match="gives preference_multiple and participation"):
        InstrumentCompareInput.model_validate(_bu(existing_series=[series]))
    given = {**series, "preference_multiple": "1", "participation": "none"}
    InstrumentCompareInput.model_validate(_bu(existing_series=[given]))


def test_an_existing_note_without_compounding_is_refused() -> None:
    """The round's yearly-compounding default is never taken for an existing note: it is asked for, as B's is."""
    note = {"kind": "note", "principal": "300000", "interest_rate_percent": "8", "months_outstanding": 6}
    with pytest.raises(ValidationError, match="gives compounding"):
        InstrumentCompareInput.model_validate(_bu(existing_instruments=[note]))
    simple = instrument_compare(
        **_bu(existing_instruments=[{**note, "compounding": "simple"}], next_rounds=[_ROUND_ONE])
    )
    assert simple.priced_conversions[_FIRST].converting_amount.exact == 312_000


@pytest.mark.parametrize("field", ["team_shares", "unissued_pool_shares"])
def test_the_team_s_shares_and_the_pool_are_required(field: str) -> None:
    """Today's FD is built from the holder groups, so a group left out is refused rather than read as 0."""
    without = {key: value for key, value in COMPARE_BU.items() if key != field}
    with pytest.raises(ValidationError, match=rf"{field}\n\s+Field required"):
        InstrumentCompareInput.model_validate(without)
    InstrumentCompareInput.model_validate(_bu(**{field: 0}))


def test_an_existing_mfn_safe_beside_a_note_with_a_cap_or_discount_is_flagged() -> None:
    """The MFN SAFE converts on its given terms under both options; the flag and the assumption row say so."""
    mfn = {"kind": "safe", "purchase_amount": "500000", "mfn": True}
    flagged = instrument_compare(**_bu(existing_instruments=[mfn], next_rounds=[_ROUND_ONE]))
    rule = next(row for row in flagged.assumptions if row.key == "existing_instruments_rule")

    assert "existing_mfn_safe_beside_note" in flagged.flags
    assert "An existing MFN SAFE converts on the terms given for it under both options" in rule.statement
    discount_only = instrument_compare(
        **_bu(existing_instruments=[mfn], note_valuation_cap=None, next_rounds=[_ROUND_ONE])
    )
    assert "existing_mfn_safe_beside_note" in discount_only.flags
    plain_note = _bu(existing_instruments=[mfn], note_valuation_cap=None, note_discount_percent=None)
    assert "existing_mfn_safe_beside_note" not in instrument_compare(**plain_note).flags
    capped = {"kind": "safe", "purchase_amount": "500000", "valuation_cap": "10000000"}
    assert "existing_mfn_safe_beside_note" not in instrument_compare(**_bu(existing_instruments=[capped])).flags


@pytest.mark.parametrize(("invested", "flagged"), [("3000000", True), ("500000", False)])
def test_option_a_s_price_below_what_an_existing_series_paid_is_flagged(invested: str, flagged: bool) -> None:
    """FD 11M at an $8M pre-money prices A at 8/11 a share: below $3.00 a share (flagged), above $0.50 (not)."""
    series = {"shares": 1_000_000, "invested": invested, "preference_multiple": "1", "participation": "none"}
    result = instrument_compare(**_bu(existing_series=[series], next_rounds=[_ROUND_ONE]))

    assert result.priced_price.exact == Fraction(8, 11)
    assert ("priced_round_below_existing_series_price" in result.flags) is flagged


def test_interest_paid_in_cash_is_flagged_only_when_there_is_interest() -> None:
    cash = instrument_compare(**_bu(note_interest_paid_in_cash=True, next_rounds=[_ROUND_ONE]))
    assert "note_interest_paid_in_cash" in cash.flags and "note_interest_converts" not in cash.flags
    no_interest = _bu(note_interest_paid_in_cash=True, note_interest_rate_percent="0", next_rounds=[_ROUND_ONE])
    assert "note_interest_paid_in_cash" not in instrument_compare(**no_interest).flags


def test_capped_safes_owning_the_whole_company_are_refused() -> None:
    safes = [{"kind": "safe", "purchase_amount": "600000", "valuation_cap": "1000000"}] * 2
    with pytest.raises(ValidationError, match="own the whole company"):
        InstrumentCompareInput.model_validate(_bu(existing_instruments=safes))


@pytest.mark.parametrize(
    ("field", "item", "limit"),
    [
        (
            "existing_series",
            {"shares": 1, "invested": "1", "preference_multiple": "1", "participation": "none"},
            MAX_EXISTING_SERIES,
        ),
        (
            "existing_instruments",
            {"kind": "safe", "purchase_amount": "1", "valuation_cap": "1000000"},
            MAX_EXISTING_INSTRUMENTS,
        ),
        ("next_rounds", _ROUND_ONE, MAX_NEXT_ROUNDS),
        ("exit_amounts", "1", MAX_EXITS),
    ],
)
def test_each_list_has_its_limit(field: str, item: object, limit: int) -> None:
    InstrumentCompareInput.model_validate(_bu(**{field: [item] * limit}))
    with pytest.raises(ValidationError, match=f"at most {limit} items"):
        InstrumentCompareInput.model_validate(_bu(**{field: [item] * (limit + 1)}))
