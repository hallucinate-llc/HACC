from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path("/home/barberb/HACC/workspace")
DEFAULT_MANIFEST_PATH = ROOT / "combined_state_court_packet_manifest.json"
PACKAGE_ROOT = Path("/home/barberb/HACC/complaint-generator/ipfs_datasets_py")

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from ipfs_datasets_py.processors.legal_data import build_state_court_filing_packet_from_manifest


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build state-court filing packet from manifest.")
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST_PATH),
        help="Path to packet manifest JSON.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    payload = build_state_court_filing_packet_from_manifest(args.manifest)
    for pdf_path in payload["rendered_paths"]:
        print(pdf_path)
    print(payload["packet_path"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
