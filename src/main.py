#!/usr/bin/env python3
"""Run the equity calculator, which replaced the equity_equation script.

The calculator lives in equity-calculator/. Install it from the repository root with
``pip install ./equity-calculator``, then run ``equity-calculator --help`` (or this file) to list the scenarios.
"""

import sys


def run() -> None:
    """Start the equity calculator's command line, or say how to install it."""
    try:
        from equity_calculator.__main__ import main
    except ImportError:
        sys.exit(
            "The equity calculator is not installed: run pip install ./equity-calculator from the repository root."
        )
    main()


if __name__ == "__main__":
    run()
