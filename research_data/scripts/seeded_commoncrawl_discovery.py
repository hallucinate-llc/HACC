#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""Run seeded CommonCrawl discovery via complaint-generator's shared search adapter."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from integrations.ipfs_datasets import discover_seeded_commoncrawl


def main() -> None:
    parser = argparse.ArgumentParser(description="Seeded CommonCrawl discovery using shared adapter workflows")
    parser.add_argument("--queries-file", required=True, help="Path to seeded queries file")
    parser.add_argument("--cc-limit", type=int, default=1000)
    parser.add_argument("--top-per-site", type=int, default=50)
    parser.add_argument("--fetch-top", type=int, default=0)
    parser.add_argument("--sleep", type=float, default=0.5)
    args = parser.parse_args()

    result = discover_seeded_commoncrawl(
        args.queries_file,
        cc_limit=args.cc_limit,
        top_per_site=args.top_per_site,
        fetch_top=args.fetch_top,
        sleep_seconds=args.sleep,
    )
    if result.get("status") != "success":
        raise SystemExit(result.get("error") or "seeded commoncrawl discovery failed")

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("research_results")
    out_dir.mkdir(exist_ok=True)
    out_candidates = out_dir / f"seeded_commoncrawl_candidates_{ts}.json"
    out_candidates.write_text(json.dumps(result["candidates"], ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out_candidates)

    fetched = result.get("fetched")
    if fetched:
        out_fetch = out_dir / f"seeded_commoncrawl_fetch_{ts}.json"
        out_fetch.write_text(json.dumps(fetched, ensure_ascii=False, indent=2), encoding="utf-8")
        print("wrote", out_fetch)


if __name__ == "__main__":
    main()
