#!/usr/bin/env python3
# DEPRECATED: historical queue helper; prefer shared complaint-generator queue workflows.
"""Filter a third-party download queue via complaint-generator's shared queue workflow."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.research_queue_workflow import filter_download_queue


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--in", dest="in_path", default="research_results/third_party_download_queue.json")
    parser.add_argument("--out", dest="out_path", default="research_results/third_party_download_queue_next_hop.json")
    parser.add_argument(
        "--summary",
        dest="summary_path",
        default="research_results/third_party_download_queue_next_hop_summary.json",
    )
    parser.add_argument("--min-score", type=int, default=50)
    parser.add_argument("--max-domains", type=int, default=150)
    parser.add_argument("--keep-gov", action="store_true")
    parser.add_argument("--keep-domain", action="append", default=[])
    args = parser.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    summary_path = Path(args.summary_path)
    if not in_path.exists():
        raise SystemExit(f"Missing input queue: {in_path}")

    payload = json.loads(in_path.read_text(encoding="utf-8"))
    filtered, summary = filter_download_queue(
        payload,
        keep_domains=set(args.keep_domain),
        keep_gov=args.keep_gov,
        min_score=args.min_score,
        max_domains=args.max_domains,
    )
    filtered["source"] = str(in_path)
    summary["input"] = str(in_path)
    summary["output"] = str(out_path)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(filtered, indent=2), encoding="utf-8")
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Wrote {out_path} ({filtered['domain_count']} domains)")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
