#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path("/home/barberb/HACC")
WORKSPACE_ROOT = ROOT / "workspace" / "exhibit-binder-court-ready"
DEFAULT_MANIFEST_PATH = WORKSPACE_ROOT / "exhibit_binder_manifest.json"
PACKAGE_ROOT = ROOT / "complaint-generator" / "ipfs_datasets_py"

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from ipfs_datasets_py.processors.legal_data import build_exhibit_binder_from_manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build exhibit binder PDF from a JSON manifest."
    )
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to exhibit binder manifest JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_exhibit_binder_from_manifest(args.manifest)
    for packet_path in payload["packet_paths"]:
        print(packet_path)
    print(payload["output_pdf"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
