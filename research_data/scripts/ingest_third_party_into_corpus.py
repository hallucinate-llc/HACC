#!/usr/bin/env python3
"""Ingest downloaded third-party materials via the shared complaint-generator adapter."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from integrations.ipfs_datasets.documents import ingest_download_manifest
from index_and_tag import DocumentIndexer
from report_generator import ReportGenerator


DEFAULT_MANIFEST = Path("research_results/third_party_download_manifest.json")
PARSED_DIR = Path("research_results/documents/parsed")
OUTPUT_DIR = Path("research_results")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="Path to a download manifest JSON produced by download_third_party_queue.py",
    )
    parser.add_argument(
        "--enable-ocr",
        action="store_true",
        help="If set, attempt OCR parsing for PDF inputs when the shared adapter detects low-text PDFs.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    PARSED_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    payload = ingest_download_manifest(
        manifest_path,
        output_dir=PARSED_DIR,
        enable_ocr=bool(args.enable_ocr),
    )
    if payload.get("status") != "success":
        raise SystemExit(f"Failed to ingest manifest: {payload.get('error') or payload.get('status')}")

    records = list(payload.get("records", []) or [])
    parsed_pdf = sum(1 for record in records if "pdf" in str(record.get("content_type", "")).lower() and record.get("status") == "success")
    parsed_html = sum(1 for record in records if "pdf" not in str(record.get("content_type", "")).lower() and record.get("status") == "success")
    parse_errors = sum(1 for record in records if record.get("status") != "success")

    logger.info(
        "Ingested %s record(s): PDFs=%s HTML/text=%s errors=%s",
        len(records),
        parsed_pdf,
        parsed_html,
        parse_errors,
    )

    indexer = DocumentIndexer(
        parsed_dir=str(PARSED_DIR),
        output_dir=str(OUTPUT_DIR),
        exclude_source_substrings=["berkeley.edu"],
    )
    indexer.batch_index()
    index_file = indexer.save_index()
    csv_file = indexer.export_csv_summary()

    reporter = ReportGenerator(output_dir=str(OUTPUT_DIR))
    reporter.load_index(index_file)
    summary_file = reporter.save_summary()
    detailed_file = reporter.save_detailed_report()

    results = {
        "ingested_records": len(records),
        "parsed_pdf": parsed_pdf,
        "parsed_html_text": parsed_html,
        "parse_errors": parse_errors,
        "documents_indexed": len(indexer.index),
        "index_file": index_file,
        "csv_file": csv_file,
        "summary_file": summary_file,
        "detailed_file": detailed_file,
        "manifest_path": str(manifest_path),
        "adapter_status": {
            "provider": "complaint-generator",
            "operation": "ingest_download_manifest",
        },
        "timestamp": datetime.now().isoformat(),
    }

    results_path = OUTPUT_DIR / f"workflow_results_third_party_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info("Wrote %s", results_path)


if __name__ == "__main__":
    main()
