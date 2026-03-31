#!/usr/bin/env python3
# DEPRECATED: historical queue helper; prefer shared complaint-generator queue workflows.
"""Build a third-party download queue via complaint-generator's shared queue workflow."""

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

from complaint_analysis.research_queue_workflow import build_download_queue

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CANDIDATES_JSON = Path("research_results/third_party_candidates.json")
OUTPUT_JSON = Path("research_results/third_party_download_queue.json")


def main() -> None:
    if not CANDIDATES_JSON.exists():
        raise SystemExit(f"Missing {CANDIDATES_JSON}")

    payload = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))
    queue = build_download_queue(payload)
    queue["source"] = str(CANDIDATES_JSON)

    OUTPUT_JSON.write_text(json.dumps(queue, indent=2), encoding="utf-8")
    logger.info("Wrote %s (%s domains)", OUTPUT_JSON, queue["domain_count"])


if __name__ == "__main__":
    main()
