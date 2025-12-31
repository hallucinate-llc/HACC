#!/usr/bin/env python3
"""
Extract hyperlinks from P1/P2 Oregon documents (critical/high priority).
Scans text/binary content for http/https URLs and saves JSON results.
"""

import re
import json
from pathlib import Path

INPUT_DIR = Path("research_results/oregon_documents")
OUTPUT_FILE = Path("research_results/oregon_p1p2_links.json")

# Only P1 and P2 files
TARGET_FILES = sorted([p for p in INPUT_DIR.glob("P[12]_*") if p.is_file()])

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

results = []

cwd = Path.cwd()

for file_path in TARGET_FILES:
    try:
        data = file_path.read_bytes()
        # Attempt text decode with fallback
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            text = data.decode("latin-1", errors="ignore")
        urls = set(URL_PATTERN.findall(text))
        if urls:
            results.append({
                "file": str(file_path.resolve().relative_to(cwd)),
                "name": file_path.name,
                "url_count": len(urls),
                "urls": sorted(urls)
            })
    except Exception as e:
        results.append({
            "file": str(file_path),
            "name": file_path.name,
            "error": str(e)
        })

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump({"files_processed": len(TARGET_FILES), "results": results}, f, indent=2)

print(f"Processed {len(TARGET_FILES)} files; found links in {sum(1 for r in results if 'urls' in r)} files.")
print(f"Saved to {OUTPUT_FILE}")
