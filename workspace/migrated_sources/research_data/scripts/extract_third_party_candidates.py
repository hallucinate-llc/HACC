#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""Extract third-party candidates via complaint-generator's shared bootstrap workflow."""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.research_bootstrap_workflow import (
    extract_third_party_candidates_from_corpus,
    write_candidates_csv,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(".")
OUTPUT_JSON = Path("research_results/third_party_candidates.json")
OUTPUT_CSV = Path("research_results/third_party_candidates.csv")


def main() -> None:
    roots = [
        WORKSPACE_ROOT / "research_results/hacc_documents",
        WORKSPACE_ROOT / "research_results/oregon_documents",
        WORKSPACE_ROOT / "research_results/oregon_p1p2_downloads",
        WORKSPACE_ROOT / "research_results/third_party_downloads",
        WORKSPACE_ROOT / "research_results/documents/parsed",
        WORKSPACE_ROOT / "raw_documents",
    ]
    payload = extract_third_party_candidates_from_corpus(roots)
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    write_candidates_csv(payload, OUTPUT_CSV)
    logger.info("Wrote %s and %s", OUTPUT_JSON, OUTPUT_CSV)


if __name__ == "__main__":
    main()
