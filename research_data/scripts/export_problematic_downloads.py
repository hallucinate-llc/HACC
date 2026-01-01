#!/usr/bin/env python3
"""Export problematic downloaded PDFs to CSV for manual triage.

Creates research_results/documents/problematic_downloads.csv
with columns: filename,filepath,url,content_type,file_size,parsed,parse_text_length,head_snippet
"""
import csv
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOWNLOAD_MANIFEST = ROOT / "research_results" / "documents" / "download_manifest.json"
PARSE_MANIFEST = ROOT / "research_results" / "documents" / "parse_manifest.json"
OUT_CSV = ROOT / "research_results" / "documents" / "problematic_downloads.csv"


def load_json(p: Path):
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def main():
    dl = load_json(DOWNLOAD_MANIFEST).get("downloads", [])
    parsed = load_json(PARSE_MANIFEST).get("parsed_documents", [])

    parsed_pdf_paths = {}
    for p in parsed:
        pdf_path = p.get("pdf_path")
        if pdf_path:
            parsed_pdf_paths[os.path.normpath(pdf_path)] = p

    rows = []
    for item in dl:
        filepath = item.get("filepath")
        if not filepath:
            continue
        fp = Path(filepath)
        if fp.suffix.lower() != ".pdf":
            continue

        exists = fp.exists()
        parsed_entry = parsed_pdf_paths.get(os.path.normpath(filepath))
        parsed_flag = bool(parsed_entry)
        parse_text_length = parsed_entry.get("text_length") if parsed_entry else ""

        head_snip = ""
        if exists:
            try:
                with fp.open("rb") as f:
                    data = f.read(512)
                # try to decode safely
                head_snip = data.decode("utf-8", errors="replace").replace("\n", " ")
                head_snip = head_snip.strip()
                if len(head_snip) > 200:
                    head_snip = head_snip[:200]
            except Exception:
                head_snip = ""

        # Heuristic: mark problematic if not parsed OR content-type not application/pdf OR head looks like HTML
        content_type = item.get("content_type", "")
        problematic = (not parsed_flag) or (not content_type.startswith("application/pdf"))
        if head_snip.lower().lstrip().startswith("<!doctype html") or head_snip.lower().lstrip().startswith("<html"):
            problematic = True

        if problematic:
            rows.append({
                "filename": fp.name,
                "filepath": str(fp),
                "url": item.get("url", ""),
                "content_type": content_type,
                "file_size": item.get("file_size", ""),
                "parsed": parsed_flag,
                "parse_text_length": parse_text_length,
                "head_snippet": head_snip,
            })

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename","filepath","url","content_type","file_size","parsed","parse_text_length","head_snippet"])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    print(f"Wrote {len(rows)} problematic rows to {OUT_CSV}")


if __name__ == "__main__":
    main()
