#!/usr/bin/env python3
"""Run the equity calculator, which replaced the equity_equation script.

The calculator lives in equity_calculator/. Install it from the repository root with
``pip install ./equity_calculator``, then run ``equity_calculator --help`` (or this file) to list the scenarios.
"""

import sys


def run() -> None:
    """Start the equity calculator's command line, or say how to install it."""
    try:
        from equity_calculator.__main__ import main
    except ImportError:
        sys.exit(
            "The equity calculator is not installed: run pip install ./equity_calculator from the repository root."
        )
    main()


if __name__ == "__main__":
    run()
