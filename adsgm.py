#!/usr/bin/env python3
"""Launcher: python adsgm.py <command> ...  (see godmode/cli.py)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from godmode.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
