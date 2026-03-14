#!/usr/bin/env python3
"""Retry problematic downloads via the shared complaint-generator adapter."""

from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from integrations.ipfs_datasets.search import recover_manifest_downloads


ROOT = Path(os.getcwd())
MANIFEST_PATH = ROOT / "research_results" / "documents" / "download_manifest.json"
MIN_PDF_SIZE = 512


def main() -> None:
    payload = recover_manifest_downloads(MANIFEST_PATH, min_pdf_size=MIN_PDF_SIZE)
    if payload.get("status") != "success":
        print(f"Recovery failed: {payload.get('error') or payload.get('status')}")
        return
    print(f"Done. recovered={payload.get('recovered', 0)}")


if __name__ == "__main__":
    main()
