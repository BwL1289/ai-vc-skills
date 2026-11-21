"""The input and result models of every scenario (Pydantic v2, frozen, exact ``Decimal`` in and out).

``equity`` holds the investor and employee scenarios and the tagged ``EquityInput`` / ``EquityResult`` unions, and
re-exports the other modules' names; the shared parts live in ``equity_common``.
"""
