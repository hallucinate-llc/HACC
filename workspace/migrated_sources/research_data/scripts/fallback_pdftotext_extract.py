#!/usr/bin/env python3
"""Fallback extraction: run `pdftotext -layout` on PDFs that lack parsed JSON.
Writes `parsed/<stem>.txt` and `parsed/<stem>.json`, and merges entries into
`research_results/documents/parse_manifest.json`.
"""
import os
import sys
import json
import hashlib
import subprocess
from datetime import datetime


WORKDIR = os.path.abspath(os.curdir)
RAW_DIR = os.path.join(WORKDIR, "research_results", "documents", "raw")
PARSED_DIR = os.path.join(WORKDIR, "research_results", "documents", "parsed")
MANIFEST_PATH = os.path.join(WORKDIR, "research_results", "documents", "parse_manifest.json")


def sha256_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8", errors="ignore")).hexdigest()


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            return {"parsed_documents": []}
    return {"parsed_documents": []}


def save_manifest(m):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as fh:
        json.dump(m, fh, indent=2, ensure_ascii=False)


def main():
    os.makedirs(PARSED_DIR, exist_ok=True)

    existing = {os.path.splitext(f)[0] for f in os.listdir(PARSED_DIR) if f.endswith('.json')}

    pdfs = [f for f in os.listdir(RAW_DIR) if f.lower().endswith('.pdf')]
    failed = [p for p in pdfs if os.path.splitext(p)[0] not in existing]

    if not failed:
        print('No PDFs to process (all have parsed .json).')
        return

    manifest = load_manifest()
    added = 0
    skipped = 0

    for fname in failed:
        pdf_path = os.path.join(RAW_DIR, fname)
        stem = os.path.splitext(fname)[0]
        out_txt = os.path.join(PARSED_DIR, f"{stem}.txt")
        out_json = os.path.join(PARSED_DIR, f"{stem}.json")

        print('Processing', fname)
        try:
            p = subprocess.run(["pdftotext", "-layout", pdf_path, "-"], capture_output=True, text=True, timeout=60)
            text = p.stdout if p.returncode == 0 else ""
        except Exception as e:
            print('  pdftotext error:', e)
            text = ""

        if not text or len(text.strip()) < 200:
            print('  insufficient text extracted (len', len(text), ') — skipping')
            skipped += 1
            continue

        with open(out_txt, "w", encoding="utf-8") as fh:
            fh.write(text)

        meta = {
            "pdf_path": os.path.relpath(pdf_path, WORKDIR),
            "parsed_text_path": os.path.relpath(out_txt, WORKDIR),
            "parse_date": datetime.utcnow().isoformat(),
            "source": "fallback:pdftotext",
            "url": f"file://{os.path.relpath(pdf_path, WORKDIR)}",
            "text_length": len(text),
            "checksum": sha256_text(text),
            "extraction_method": "pdftotext_only",
            "ocr_available": False,
            "ocr_attempted": False,
            "ocr_used": False,
            "needs_ocr": False
        }

        with open(out_json, "w", encoding="utf-8") as fh:
            json.dump(meta, fh, indent=2, ensure_ascii=False)

        manifest.setdefault("parsed_documents", []).append(meta)
        added += 1

    save_manifest(manifest)
    print(f'Done. added={added}, skipped={skipped}, total_checked={len(failed)}')


if __name__ == '__main__':
    main()
