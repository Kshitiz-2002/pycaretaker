#!/usr/bin/env python3
"""
PyCareTaker v0.1 — Smart Python Package Manager Companion
========================================================
Entry point.  Run `python package_manager.py --help` for usage.
"""

import sys
import os

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pycaretaker.cli import main

if __name__ == "__main__":
    main()