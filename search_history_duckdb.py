#!/usr/bin/env python3
"""Thin wrapper around the package DuckDB history search CLI."""

from __future__ import annotations

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
PKG_ROOT = REPO_ROOT / "complaint-generator" / "ipfs_datasets_py"
if str(PKG_ROOT) not in sys.path:
    sys.path.insert(0, str(PKG_ROOT))

from ipfs_datasets_py.cli.history_index_cli import main, search_duckdb

__all__ = ["main", "search_duckdb"]


if __name__ == "__main__":
    raise SystemExit(main())
