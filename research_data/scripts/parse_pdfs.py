#!/usr/bin/env python3
"""
parse_pdfs.py — compatibility wrapper over complaint-generator's document adapter.
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from integrations.ipfs_datasets.documents import parse_pdf_to_record


class PDFParser:
    """Compatibility wrapper that preserves the older manifest contract."""

    def __init__(
        self,
        raw_dir: str = "research_results/documents/raw",
        parsed_dir: str = "research_results/documents/parsed",
        metadata_file: str = "research_results/documents/parse_manifest.json",
    ):
        self.raw_dir = Path(raw_dir)
        self.parsed_dir = Path(parsed_dir)
        self.metadata_file = Path(metadata_file)
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()

    def _load_manifest(self) -> Dict:
        if self.metadata_file.exists():
            with open(self.metadata_file, "r", encoding="utf-8") as handle:
                return json.load(handle)
        return {"parsed_documents": []}

    def _save_manifest(self) -> None:
        with open(self.metadata_file, "w", encoding="utf-8") as handle:
            json.dump(self.manifest, handle, indent=2)

    def extract_text_pdftotext(self, pdf_path: str) -> Optional[str]:
        payload = parse_pdf_to_record(pdf_path, output_dir=self.parsed_dir, enable_ocr=False)
        return str(payload.get("text") or "") or None

    def extract_text_with_ocr(self, pdf_path: str) -> Optional[str]:
        payload = parse_pdf_to_record(pdf_path, output_dir=self.parsed_dir, enable_ocr=True)
        return str(payload.get("text") or "") or None

    def parse_pdf(self, pdf_path: str, source_metadata: Dict) -> Optional[str]:
        payload = parse_pdf_to_record(
            pdf_path,
            metadata=source_metadata,
            output_dir=self.parsed_dir,
            enable_ocr=True,
        )
        if payload.get("status") != "success":
            logger.error("Could not extract text from %s: %s", pdf_path, payload.get("error") or payload.get("status"))
            return None

        parse_metadata = dict(payload.get("metadata") or {})
        manifest_entry = {
            "pdf_path": pdf_path,
            "parsed_text_path": payload["parsed_text_path"],
            "parse_date": parse_metadata.get("parse_date") or parse_metadata.get("added_at") or "",
            "source": source_metadata.get("source"),
            "url": source_metadata.get("url"),
            "text_length": payload.get("text_length", 0),
            "checksum": payload.get("checksum", ""),
            "extraction_method": payload.get("extraction_method", ""),
            "ocr_available": parse_metadata.get("ocr_attempted", False) or parse_metadata.get("ocr_used", False),
            "ocr_attempted": payload.get("ocr_attempted", False),
            "ocr_used": payload.get("ocr_used", False),
            "needs_ocr": payload.get("needs_ocr", False),
        }
        self.manifest["parsed_documents"].append(manifest_entry)
        self._save_manifest()
        logger.info("Parsed to: %s", payload["parsed_text_path"])
        return str(payload["parsed_text_path"])

    def batch_parse(self, pdf_list: Dict[str, Dict]) -> Dict[str, Optional[str]]:
        return {pdf_path: self.parse_pdf(pdf_path, metadata) for pdf_path, metadata in pdf_list.items()}


if __name__ == "__main__":
    logger.info("PDF parser compatibility wrapper ready.")
