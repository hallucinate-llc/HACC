#!/usr/bin/env python3
"""ingest_third_party_into_corpus.py

Ingest downloaded third-party/partner materials into the existing parsed corpus
used by index/tag/report scripts.

Inputs:
- research_results/third_party_download_manifest.json (from download_third_party_queue.py)

Behavior:
- For PDFs: copy into research_results/documents/raw/<doc_id>.pdf and parse into
  research_results/documents/parsed/<doc_id>.txt using existing PDFParser.
- For HTML (and other text-like files): extract visible text and write directly
  to research_results/documents/parsed/<doc_id>.txt.
- Writes per-document metadata JSON next to the parsed text.
- Finally runs index_and_tag + report_generator to refresh findings outputs.

This is a compliance-oriented workflow; it does not infer wrongdoing.
"""

from __future__ import annotations

import json
import logging
import argparse
import re
import sys
import hashlib
import shutil
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MANIFEST = Path("research_results/third_party_download_manifest.json")
RAW_DIR = Path("research_results/documents/raw")
PARSED_DIR = Path("research_results/documents/parsed")
OUTPUT_DIR = Path("research_results")

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# Import existing pipeline pieces
from parse_pdfs import PDFParser  # type: ignore
from index_and_tag import DocumentIndexer  # type: ignore
from report_generator import ReportGenerator  # type: ignore


class VisibleTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript"}:
            self._skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"} and self._skip > 0:
            self._skip -= 1

    def handle_data(self, data: str) -> None:
        if self._skip:
            return
        if data:
            self._chunks.append(data)

    def text(self) -> str:
        txt = " ".join(self._chunks)
        txt = txt.replace("\u00a0", " ")
        txt = re.sub(r"\s+", " ", txt)
        return txt.strip()


def md5_hex(s: str) -> str:
    return hashlib.md5(s.encode("utf-8", errors="ignore")).hexdigest()


def doc_id_for(url: str) -> str:
    # Stable id based on canonical URL
    return md5_hex(url)


def _has_pdf_magic_bytes(path: Path) -> bool:
    try:
        with path.open("rb") as f:
            head = f.read(8)
        return head.startswith(b"%PDF-")
    except Exception:
        return False


def guess_is_pdf(saved_path: Path, content_type: str) -> bool:
    ct = (content_type or "").lower()
    looks_like_pdf = saved_path.suffix.lower() == ".pdf" or "application/pdf" in ct
    if not looks_like_pdf:
        return False
    return _has_pdf_magic_bytes(saved_path)


def extract_text_from_html(raw: str) -> str:
    parser = VisibleTextExtractor()
    try:
        parser.feed(raw)
        return parser.text() or raw
    except Exception:
        return raw


def write_parsed(text: str, out_txt: Path, metadata: dict) -> None:
    out_txt.parent.mkdir(parents=True, exist_ok=True)
    out_txt.write_text(text, encoding="utf-8", errors="ignore")
    out_json = out_txt.with_suffix(".json")
    out_json.write_text(json.dumps(metadata, indent=2), encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--manifest",
        default=str(DEFAULT_MANIFEST),
        help="Path to a download manifest JSON produced by download_third_party_queue.py",
    )
    ap.add_argument(
        "--enable-ocr",
        action="store_true",
        help="If set, attempt OCR reprocessing for PDFs previously flagged 'needs_ocr' (requires ocrmypdf)",
    )
    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    rows = json.loads(manifest_path.read_text(encoding="utf-8"))
    ok_rows = [r for r in rows if r.get("status") == "ok" and r.get("saved_path")]

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PARSED_DIR.mkdir(parents=True, exist_ok=True)

    parser = PDFParser(raw_dir=str(RAW_DIR), parsed_dir=str(PARSED_DIR))

    ingested_html = 0
    ingested_pdf = 0
    parsed_pdf = 0

    for r in ok_rows:
        domain = (r.get("domain") or "").strip()
        url = (r.get("final_url") or r.get("url") or "").strip()
        saved_path = Path(r.get("saved_path"))
        content_type = r.get("content_type", "")

        if not url or not saved_path.exists():
            continue

        did = doc_id_for(url)
        out_txt = PARSED_DIR / f"{did}.txt"
        if out_txt.exists():
            # Allow re-processing if a prior run created an empty placeholder due to PDF parse failure
            meta_path = out_txt.with_suffix(".json")
            try:
                existing_meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
            except Exception:
                existing_meta = {}
            should_reprocess = (
                out_txt.stat().st_size == 0
                and existing_meta.get("parse_error") in {"pdf_text_extraction_failed", "not_a_pdf"}
            )
            # If OCR is now available, allow reprocessing for PDFs that were previously flagged as needing OCR.
            if not should_reprocess:
                needs_ocr = bool(existing_meta.get("needs_ocr"))
                ocr_available_now = shutil.which("ocrmypdf") is not None
                should_reprocess = (
                    needs_ocr and getattr(args, "enable_ocr", False) and ocr_available_now
                )
            if not should_reprocess:
                continue

        base_meta = {
            "source": f"third_party:{domain}",
            "url": url,
            "domain": domain,
            "ingest_date": datetime.now().isoformat(),
            "content_type": content_type,
            "original_saved_path": str(saved_path),
        }

        if guess_is_pdf(saved_path, content_type):
            dest_pdf = RAW_DIR / f"{did}.pdf"
            if not dest_pdf.exists():
                dest_pdf.write_bytes(saved_path.read_bytes())
                ingested_pdf += 1

            parsed_path = parser.parse_pdf(str(dest_pdf), {"url": url, "source": base_meta["source"]})
            if parsed_path:
                # Merge/augment metadata json written by PDFParser
                meta_path = Path(parsed_path).with_suffix(".json")
                try:
                    existing = json.loads(meta_path.read_text(encoding="utf-8"))
                except Exception:
                    existing = {}
                existing.update(base_meta)
                meta_path.write_text(json.dumps(existing, indent=2), encoding="utf-8")
                parsed_pdf += 1
            else:
                # If parsing fails, at least record metadata for visibility
                write_parsed("", out_txt, {**base_meta, "parse_error": "pdf_text_extraction_failed"})

        else:
            raw = saved_path.read_text(encoding="utf-8", errors="ignore")
            ct_lower = (content_type or "").lower()

            # Some servers return HTML error pages with a .pdf filename or PDF-ish content-type.
            # If the download isn't a real PDF, extract text as HTML/plain instead of writing an empty parse.
            looks_like_html = (
                saved_path.suffix.lower() in {".html", ".htm", ".aspx"}
                or "html" in ct_lower
                or bool(re.search(r"<!doctype\s+html|<html\b", raw[:200], flags=re.IGNORECASE))
            )
            if looks_like_html:
                text = extract_text_from_html(raw)
            else:
                text = re.sub(r"\s+", " ", raw).strip()

            meta = {
                **base_meta,
                "text_length": len(text),
                "checksum": hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest(),
            }
            write_parsed(text, out_txt, meta)
            ingested_html += 1

    logger.info(f"Ingested PDFs copied: {ingested_pdf}; PDFs parsed: {parsed_pdf}; HTML/text parsed: {ingested_html}")

    # Refresh index + reports
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
        "ingested_pdf_copied": ingested_pdf,
        "parsed_pdf": parsed_pdf,
        "parsed_html_text": ingested_html,
        "documents_indexed": len(indexer.index),
        "index_file": index_file,
        "csv_file": csv_file,
        "summary_file": summary_file,
        "detailed_file": detailed_file,
        "timestamp": datetime.now().isoformat(),
    }

    results_path = OUTPUT_DIR / f"workflow_results_third_party_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    results_path.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info(f"Wrote {results_path}")


if __name__ == "__main__":
    main()
