#!/usr/bin/env python3
"""Stable human-facing driver for the staged compiler."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from turingsynth.cli import main


if __name__ == "__main__":
    raise SystemExit(main(compiler_root=ROOT))
