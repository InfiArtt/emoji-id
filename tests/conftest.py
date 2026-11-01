"""Pytest setup: install the NVDA fakes and make the add-on importable."""

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(_ROOT / "tests"), str(_ROOT / "addon"), str(_ROOT / "addon" / "globalPlugins")]

import nvda_mocks  # noqa: E402, F401
