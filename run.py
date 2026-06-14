#!/usr/bin/env python3
"""Quick launcher — run the game without installing the package.

Usage:
    python run.py          # normal
    python run.py admin    # all chapters/levels unlocked
"""

import sys
from src.core import config

config.ADMIN_MODE = "admin" in sys.argv[1:]

from src.main import main

main()
