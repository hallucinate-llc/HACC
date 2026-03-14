#!/usr/bin/env python3
# DEPRECATED: historical queue helper; prefer shared complaint-generator queue workflows.
"""Download a third-party queue via complaint-generator's shared queue workflow."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.research_queue_workflow import download_queue

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_QUEUE = Path("research_results/third_party_download_queue.json")
DEFAULT_OUT_DIR = Path("research_results/third_party_downloads")
DEFAULT_MANIFEST_JSON = Path("research_results/third_party_download_manifest.json")
DEFAULT_MANIFEST_CSV = Path("research_results/third_party_download_manifest.csv")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--queue", default=str(DEFAULT_QUEUE))
    parser.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    parser.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST_JSON))
    parser.add_argument("--manifest-csv", default=str(DEFAULT_MANIFEST_CSV))
    parser.add_argument("--max-domains", type=int, default=15)
    parser.add_argument("--max-urls-per-domain", type=int, default=25)
    parser.add_argument("--delay", type=float, default=1.0, help="Accepted for compatibility; handled upstream as no-op.")
    parser.add_argument("--timeout", type=float, default=None)
    parser.add_argument("--connect-timeout", type=float, default=10)
    parser.add_argument("--read-timeout", type=float, default=20)
    parser.add_argument("--max-bytes", type=int, default=15 * 1024 * 1024, help="Accepted for compatibility; handled upstream as no-op.")
    parser.add_argument("--retries", type=int, default=2, help="Accepted for compatibility; handled upstream as no-op.")
    parser.add_argument("--include-guessed", action="store_true")
    parser.add_argument("--flush-every", type=int, default=10, help="Accepted for compatibility; handled upstream as no-op.")
    args = parser.parse_args()

    queue_path = Path(args.queue)
    if not queue_path.exists():
        raise SystemExit(f"Missing queue file: {queue_path}")

    timeout = int(args.timeout) if args.timeout is not None else int(max(args.connect_timeout, args.read_timeout))
    payload = json.loads(queue_path.read_text(encoding="utf-8"))
    result = download_queue(
        payload,
        out_dir=args.out,
        manifest_json=args.manifest_json,
        manifest_csv=args.manifest_csv,
        max_domains=args.max_domains,
        max_urls_per_domain=args.max_urls_per_domain,
        include_guessed=args.include_guessed,
        timeout=timeout,
    )
    logger.info(
        "Done. domains_processed=%s ok_downloads=%s manifest_rows=%s",
        result["domains_processed"],
        result["ok_downloads"],
        result["manifest_rows"],
    )


if __name__ == "__main__":
    main()
