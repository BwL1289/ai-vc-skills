"""One holder's dilution report lines (the ``Dilution`` sheet): the stake before, each round, the stake after.

One value column. Each round gets a block (the new investors' share n, the new pool's share p, the share kept, the
post-money and the holder's value at it when the round was given as amounts, the stake after); the stake each round
took follows with its live total, which equals the stake before minus the final stake.
"""

from __future__ import annotations

from equity_calculator.exact import quantity
from equity_calculator.schemas.equity_dilution import DilutionResult, DilutionRow
from equity_calculator.sheet_parts import GIVEN, Line, Sheet, given_percent

_TITLE = "Dilution"
_HEADING = "One holder's stake through a series of rounds: h_k = h_(k-1)·(1 - n_k - p_k)"
_COLUMNS = ("This holder",)


def _round_lines(row: DilutionRow) -> list[Line]:
    """One round's block: n (given or I/(V + I)), p, the share kept, the post-money if known, the stake after."""
    name = f"Round {row.index}"
    key = f"round_{row.index}"
    from_amounts = row.post_money is not None
    lines = [
        Line(
            f"{key}_investors",
            f"{name}: new investors' share (n)",
            (row.investor_share,),
            "I/(V + I)" if from_amounts else GIVEN,
        ),
        Line(f"{key}_pool", f"{name}: new pool's share (p)", (row.pool_share,), GIVEN),
        Line(f"{key}_kept", f"{name}: share of the stake kept", (row.kept,), "1 - n - p"),
    ]
    if row.post_money is not None and row.holder_value is not None:
        lines += [
            Line(f"{key}_post_money", f"{name}: post-money", (row.post_money,), "V + I"),
            Line(f"{key}_holder_value", f"{name}: holder's value at post-money", (row.holder_value,), "stake·(V + I)"),
        ]
    lines.append(Line(f"{key}_stake", f"{name}: stake after", (row.stake_after,), "stake before·(1 - n - p)"))

    return lines


def dilution_sheet(result: DilutionResult) -> Sheet:
    """The dilution lines: the stake before, every round's block, the stake each round took, the final stake."""
    lines = [
        Line("initial_stake", "Stake before the first round", (given_percent(result.inputs.holder_percent),), GIVEN)
    ]
    for row in result.rows:
        lines += _round_lines(row)
    lost_keys = tuple(f"round_{row.index}_lost" for row in result.rows)
    lines += [
        Line(key, f"Stake lost in round {row.index}", (row.stake_lost,), "stake before - stake after")
        for key, row in zip(lost_keys, result.rows, strict=True)
    ]
    if lost_keys:
        lost = result.initial_stake.exact - result.final_stake.exact
        lines.append(
            Line(
                "total_lost",
                "Stake lost in all",
                (quantity("fraction", lost),),
                "stake before - final stake",
                lost_keys,
            )
        )
    lines += [
        Line("final_stake", "Final stake", (result.final_stake,), "h_0·(1 - n_1 - p_1)···(1 - n_k - p_k)"),
        Line("kept_overall", "Share of the first stake kept", (result.kept_overall,), "final stake / stake before"),
    ]

    return Sheet(_TITLE, _HEADING, _COLUMNS, tuple(lines), result.assumptions)
