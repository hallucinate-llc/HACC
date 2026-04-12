#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path("/home/barberb/HACC")
PACKAGE_ROOT = ROOT / "complaint-generator" / "ipfs_datasets_py"
MANIFEST_PATH = ROOT / "workspace" / "full_evidence_binder_manifest.json"

if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from ipfs_datasets_py.processors.legal_data import build_full_evidence_binder_from_manifest


def main() -> None:
    lean_mode = "--lean" in sys.argv
    payload = build_full_evidence_binder_from_manifest(MANIFEST_PATH, lean_mode=lean_mode)
    print(payload["output_pdf"])


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        raise
