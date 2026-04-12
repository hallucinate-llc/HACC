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
    build_default_official_form_drafts,
    build_official_form_drafts_from_config,
)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build default JS-44 and AO-440 draft form PDFs."
    )
    parser.add_argument(
        "--config-path",
        default="",
        help="Optional JSON config path for reusable official-form draft rendering.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.config_path:
        if build_official_form_drafts_from_config is None:
            raise RuntimeError("config-driven official-form draft builder is unavailable in this environment")
        payload = build_official_form_drafts_from_config(args.config_path)
        for path in payload["output_paths"]:
            print(path)
        return 0
    if build_default_official_form_drafts is None:
        raise RuntimeError("official form draft builder is unavailable in this environment")
    for path in build_default_official_form_drafts():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
