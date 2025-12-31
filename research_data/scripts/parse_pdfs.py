#!/usr/bin/env python3
"""
parse_pdfs.py — Extract text from PDFs with OCR fallback and metadata tagging.
Produces parsed text files and metadata JSON for each document.
"""

import os
import json
import subprocess
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


MIN_TEXT_LEN_FOR_NON_SCANNED_PDF = 100

class PDFParser:
    """Parse PDFs and extract text with OCR fallback."""
    
    def __init__(self, raw_dir: str = "research_results/documents/raw",
                 parsed_dir: str = "research_results/documents/parsed",
                 metadata_file: str = "research_results/documents/parse_manifest.json"):
        self.raw_dir = Path(raw_dir)
        self.parsed_dir = Path(parsed_dir)
        self.metadata_file = Path(metadata_file)
        self.parsed_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load or create parse manifest."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"parsed_documents": []}
    
    def _save_manifest(self):
        """Save manifest."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def extract_text_pdftotext(self, pdf_path: str) -> Optional[str]:
        """Extract text using pdftotext. Return text or None on failure."""
        try:
            result = subprocess.run(
                ['pdftotext', '-layout', pdf_path, '-'],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return result.stdout
            else:
                logger.warning(f"pdftotext failed for {pdf_path}: {result.stderr}")
                return None
        except FileNotFoundError:
            logger.warning("pdftotext not installed. Run: apt-get install poppler-utils")
            return None
        except Exception as e:
            logger.error(f"Error in pdftotext: {e}")
            return None
    
    def extract_text_with_ocr(self, pdf_path: str) -> Optional[str]:
        """Extract text with OCR (ocrmypdf + pdftotext). For scanned PDFs."""
        try:
            if shutil.which("ocrmypdf") is None:
                logger.warning("ocrmypdf not installed. Run: apt-get install ocrmypdf")
                return None

            pdf_path_p = Path(pdf_path)
            temp_ocr = pdf_path_p.with_name(pdf_path_p.stem + "_ocr.pdf")

            # Run ocrmypdf to produce an OCR'd PDF, then extract text from it.
            # --skip-text avoids re-OCRing pages that already have text.
            result = subprocess.run(
                [
                    "ocrmypdf",
                    "--skip-text",
                    str(pdf_path_p),
                    str(temp_ocr),
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode != 0:
                stderr = (result.stderr or "").strip()
                logger.warning(f"ocrmypdf failed for {pdf_path}: {stderr}")
                return None

            ocr_text = self.extract_text_pdftotext(str(temp_ocr))

            try:
                if temp_ocr.exists():
                    temp_ocr.unlink()
            except Exception:
                # Best-effort cleanup only.
                pass

            return ocr_text
        except FileNotFoundError:
            return None
        except Exception as e:
            logger.error(f"Error in OCR: {e}")
            return None
    
    def parse_pdf(self, pdf_path: str, source_metadata: Dict) -> Optional[str]:
        """
        Parse a single PDF file. Return path to parsed text file or None.
        source_metadata should include: url, source, download_date, etc.
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            logger.error(f"File not found: {pdf_path}")
            return None
        
        logger.info(f"Parsing: {pdf_path}")

        ocr_available = shutil.which("ocrmypdf") is not None
        ocr_attempted = False
        ocr_used = False
        extraction_method = "pdftotext"
        
        # Try pdftotext first
        text = self.extract_text_pdftotext(str(pdf_path))
        
        # Fallback to OCR if pdftotext returned little text (likely scanned)
        if text and len(text.strip()) < MIN_TEXT_LEN_FOR_NON_SCANNED_PDF:
            logger.info("PDF appears to be scanned, attempting OCR...")
            ocr_attempted = True
            ocr_text = self.extract_text_with_ocr(str(pdf_path))
            if ocr_text and len(ocr_text) > len(text):
                text = ocr_text
                ocr_used = True
                extraction_method = "ocrmypdf+pdftotext"
        
        if not text:
            logger.error(f"Could not extract text from {pdf_path}")
            return None

        needs_ocr = (
            len(text.strip()) < MIN_TEXT_LEN_FOR_NON_SCANNED_PDF and (not ocr_used)
        )
        
        # Generate output filename
        base_name = pdf_path.stem
        out_path = self.parsed_dir / f"{base_name}.txt"
        
        # Save parsed text
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        # Save metadata
        metadata = {
            "pdf_path": str(pdf_path),
            "parsed_text_path": str(out_path),
            "parse_date": datetime.now().isoformat(),
            "source": source_metadata.get("source"),
            "url": source_metadata.get("url"),
            "text_length": len(text),
            "checksum": hashlib.sha256(text.encode()).hexdigest(),
            "extraction_method": extraction_method,
            "ocr_available": ocr_available,
            "ocr_attempted": ocr_attempted,
            "ocr_used": ocr_used,
            "needs_ocr": needs_ocr,
        }
        
        meta_path = out_path.with_suffix('.json')
        with open(meta_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        self.manifest["parsed_documents"].append(metadata)
        self._save_manifest()
        
        logger.info(f"Parsed to: {out_path}")
        return str(out_path)
    
    def batch_parse(self, pdf_list: Dict[str, Dict]) -> Dict[str, Optional[str]]:
        """
        Batch parse PDFs. pdf_list format:
        {"filepath": {"url": "...", "source": "...", ...}, ...}
        Returns dict of filepath -> parsed_text_path or None.
        """
        results = {}
        for pdf_path, metadata in pdf_list.items():
            results[pdf_path] = self.parse_pdf(pdf_path, metadata)
        return results

if __name__ == "__main__":
    parser = PDFParser()
    # Example: parse a single file
    # results = parser.parse_pdf("path/to/sample.pdf", {"url": "...", "source": "..."})
    logger.info("PDF parser initialized and ready.")
