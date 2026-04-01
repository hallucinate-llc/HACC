#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""Extract outbound document queues from Quantum pages via complaint-generator bootstrap helpers."""

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

from complaint_analysis.research_bootstrap_workflow import (
    extract_external_document_queue,
    load_manifest_rows,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default="research_results/third_party_download_manifest_quantum_pages_from_sitemaps.json",
    )
    parser.add_argument(
        "--out-queue",
        default="research_results/quantum_external_documents_queue.json",
    )
    parser.add_argument(
        "--out-evidence",
        default="research_results/quantum_external_documents_evidence.json",
    )
    parser.add_argument("--max-candidates", type=int, default=800)
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    rows = load_manifest_rows(manifest_path)
    queue, evidence = extract_external_document_queue(rows, max_candidates=args.max_candidates)
    queue["source"] = {
        "manifest": str(manifest_path),
        "notes": "Outbound doc-like URL candidates extracted from downloaded Quantum pages",
    }
    evidence["source"] = {"manifest": str(manifest_path)}

    Path(args.out_queue).write_text(json.dumps(queue, indent=2), encoding="utf-8")
    Path(args.out_evidence).write_text(json.dumps(evidence, indent=2), encoding="utf-8")
    print(json.dumps(queue["stats"], indent=2))


if __name__ == "__main__":
    main()
