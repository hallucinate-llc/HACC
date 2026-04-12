#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path("/home/barberb/HACC")
PACKAGE_ROOT = ROOT / "complaint-generator" / "ipfs_datasets_py"

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from ipfs_datasets_py.processors.legal_data import build_default_courtstyle_packet
from ipfs_datasets_py.processors.legal_data import build_courtstyle_packet_from_config


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build default court-style complaint packet and supporting exhibit assets."
    )
    parser.add_argument(
        "--config-path",
        default="",
        help="Optional JSON config path for reusable courtstyle packet rendering.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.config_path:
        if build_courtstyle_packet_from_config is None:
            raise RuntimeError("config-driven courtstyle packet builder is unavailable in this environment")
        payload = build_courtstyle_packet_from_config(args.config_path)
        print(payload["complaint_output"])
        return 0
    if build_default_courtstyle_packet is None:
        raise RuntimeError("courtstyle packet builder is unavailable in this environment")
    build_default_courtstyle_packet()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
