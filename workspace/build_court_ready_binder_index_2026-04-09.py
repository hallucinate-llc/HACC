#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path("/home/barberb/HACC")
PACKAGE_ROOT = ROOT / "complaint-generator" / "ipfs_datasets_py"

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from ipfs_datasets_py.processors.legal_data import (
    build_court_ready_binder_index_from_config,
    build_default_court_ready_binder_index,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the default court-ready evidence binder index PDF."
    )
    parser.add_argument(
        "--config-path",
        default="",
        help="Optional JSON config path for reusable binder-index rendering.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.config_path:
        if build_court_ready_binder_index_from_config is None:
            raise RuntimeError("config-driven binder index builder is unavailable in this environment")
        payload = build_court_ready_binder_index_from_config(args.config_path)
        print(payload["output_path"])
        return 0
    if build_default_court_ready_binder_index is None:
        raise RuntimeError("court-ready binder index builder is unavailable in this environment")
    out = build_default_court_ready_binder_index()
    print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
