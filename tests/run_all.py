#!/usr/bin/env python3
"""Run every test suite. Stdlib only: python tests/run_all.py"""

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))

SUITES = ["connector-routing", "account-isolation", "write-gating", "budget-safety", "approval-flow",
          "portfolio-learning", "creative", "repo-hygiene"]


def main() -> int:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for name in SUITES:
        d = os.path.join(HERE, name)
        suite.addTests(loader.discover(start_dir=d, pattern="test_*.py", top_level_dir=d))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
