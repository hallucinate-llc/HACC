#!/usr/bin/env python3
"""extract_external_documents_from_quantum_pages.py

Scan locally-downloaded Quantum Residential HTML pages (from a download manifest)
for outbound links that plausibly point to documents (PDF/DOC/etc), including
"download" URLs that may not end with a file extension.

Outputs:
- A downloader queue JSON compatible with download_third_party_queue.py
- An evidence JSON mapping source page -> extracted candidate URLs

This is intentionally conservative: it prioritizes the most likely document URLs
and caps total candidates.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qs, unquote, urljoin, urldefrag, urlparse


DOC_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".xls",
    ".xlsx",
    ".ppt",
    ".pptx",
    ".rtf",
    ".txt",
    ".csv",
}

HREF_SRC_RE = re.compile(r"(?i)\b(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]")
RAW_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)


@dataclass(frozen=True)
class EvidenceRow:
    source_saved_path: str
    source_url: str
    candidate_url: str
    reason: str
    score: int


def load_manifest_rows(manifest_path: Path) -> list[dict]:
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    raise ValueError("Unsupported manifest format (expected a JSON list)")


def maybe_unwrap_google(url: str) -> str:
    try:
        parsed = urlparse(url)
    except Exception:
        return url

    host = (parsed.netloc or "").lower()
    if host not in {"www.google.com", "google.com"}:
        return url

    qs = parse_qs(parsed.query or "")
    candidate = qs.get("q", [""])[0] or qs.get("url", [""])[0]
    if not candidate:
        return url

    candidate = unquote(candidate)
    if candidate.startswith("http://") or candidate.startswith("https://"):
        return candidate

    return url


def normalize_url(raw: str, base_url: str) -> str | None:
    raw = (raw or "").strip()
    if not raw:
        return None

    lowered = raw.lower()
    if lowered.startswith(("mailto:", "tel:", "javascript:")):
        return None

    try:
        absolute = urljoin(base_url, raw)
        absolute, _frag = urldefrag(absolute)
        absolute = maybe_unwrap_google(absolute)
        parsed = urlparse(absolute)
    except Exception:
        return None

    if parsed.scheme not in {"http", "https"}:
        return None

    return absolute


def is_quantum_domain(domain: str) -> bool:
    d = domain.lower().strip()
    return d == "quantumresidential.com" or d.endswith(".quantumresidential.com")


def score_candidate(url: str) -> tuple[int, str] | None:
    """Return (score, reason) if URL is a plausible doc/download link."""
    try:
        parsed = urlparse(url)
    except Exception:
        return None

    path = (parsed.path or "")
    lpath = path.lower()
    qs = parse_qs(parsed.query or "")

    suffix = Path(lpath).suffix
    if suffix in DOC_EXTENSIONS:
        return (100, f"extension:{suffix}")

    # Heuristics for non-extension document URLs
    joined_qs = "&".join(f"{k}={v[0] if v else ''}" for k, v in qs.items()).lower()

    if "pdf" in lpath or "pdf" in joined_qs:
        return (80, "contains:pdf")

    if any(tok in lpath for tok in ["/download", "download/", "/attachment", "/uploads/"]):
        return (60, "path:downloadish")

    if any(k in qs for k in ["download", "attachment", "file", "filename", "document", "doc"]):
        return (60, "query:downloadish")

    return None


def extract_links(html_text: str) -> Iterable[str]:
    for m in HREF_SRC_RE.finditer(html_text):
        yield m.group(1)
    for m in RAW_URL_RE.finditer(html_text):
        yield m.group(0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--manifest",
        default="research_results/third_party_download_manifest_quantum_pages_from_sitemaps.json",
        help="Manifest JSON list that contains downloaded Quantum pages (saved_path + final_url)",
    )
    ap.add_argument(
        "--out-queue",
        default="research_results/quantum_external_documents_queue.json",
        help="Output queue JSON (compatible with download_third_party_queue.py)",
    )
    ap.add_argument(
        "--out-evidence",
        default="research_results/quantum_external_documents_evidence.json",
        help="Output evidence JSON mapping source page -> candidate URLs",
    )
    ap.add_argument(
        "--max-candidates",
        type=int,
        default=800,
        help="Cap total unique candidate URLs collected",
    )

    args = ap.parse_args()

    manifest_path = Path(args.manifest)
    rows = load_manifest_rows(manifest_path)

    evidence: list[EvidenceRow] = []
    candidates_by_domain: dict[str, dict[str, tuple[int, str]]] = defaultdict(dict)

    total_files = 0
    total_links_seen = 0

    for row in rows:
        if row.get("status") != "ok":
            continue

        saved_path = row.get("saved_path")
        base_url = row.get("final_url") or row.get("url")
        if not saved_path or not base_url:
            continue

        p = Path(saved_path)
        if not p.exists():
            continue

        # Only scan HTML-ish files; skip obvious binaries
        ctype = (row.get("content_type") or "").lower()
        if "text/html" not in ctype and p.suffix.lower() not in {".html", ".htm"}:
            continue

        html = p.read_text("utf-8", errors="ignore")
        total_files += 1

        for raw in extract_links(html):
            total_links_seen += 1
            normalized = normalize_url(raw, base_url)
            if not normalized:
                continue

            parsed = urlparse(normalized)
            domain = (parsed.netloc or "").lower()
            if not domain:
                continue

            # We focus on outbound docs; keep non-Quantum domains.
            if is_quantum_domain(domain):
                continue

            scored = score_candidate(normalized)
            if not scored:
                continue

            score, reason = scored

            # Keep best score per (domain, url)
            existing = candidates_by_domain[domain].get(normalized)
            if existing is None or score > existing[0]:
                candidates_by_domain[domain][normalized] = (score, reason)

            evidence.append(
                EvidenceRow(
                    source_saved_path=str(saved_path),
                    source_url=str(base_url),
                    candidate_url=str(normalized),
                    reason=reason,
                    score=score,
                )
            )

    # Build a globally-ranked unique URL list
    unique_rows: list[tuple[str, str, int, str]] = []
    for domain, urls in candidates_by_domain.items():
        for u, (score, reason) in urls.items():
            unique_rows.append((domain, u, score, reason))

    unique_rows.sort(key=lambda r: (-r[2], r[0], r[1]))
    unique_rows = unique_rows[: max(0, int(args.max_candidates))]

    # Rebuild candidates_by_domain after cap
    capped_by_domain: dict[str, list[str]] = defaultdict(list)
    for domain, u, _score, _reason in unique_rows:
        capped_by_domain[domain].append(u)

    queue_items = []
    for domain in sorted(capped_by_domain.keys()):
        urls = capped_by_domain[domain]
        queue_items.append(
            {
                "domain": domain,
                "score": 100,
                "evidence_urls": urls,
                "seed_urls": [],
                "guessed_urls": [],
                "notes": "Extracted from Quantum Residential pages (outbound doc-like links)",
            }
        )

    queue = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "manifest": str(manifest_path),
            "notes": "Outbound doc-like URL candidates extracted from downloaded Quantum pages",
        },
        "stats": {
            "html_files_scanned": total_files,
            "raw_links_seen": total_links_seen,
            "unique_candidate_urls": sum(len(v) for v in capped_by_domain.values()),
            "candidate_domains": len(capped_by_domain),
        },
        "items": queue_items,
    }

    evidence_json = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {"manifest": str(manifest_path)},
        "rows": [
            {
                "source_saved_path": e.source_saved_path,
                "source_url": e.source_url,
                "candidate_url": e.candidate_url,
                "reason": e.reason,
                "score": e.score,
            }
            for e in evidence
        ],
    }

    Path(args.out_queue).write_text(json.dumps(queue, indent=2), encoding="utf-8")
    Path(args.out_evidence).write_text(json.dumps(evidence_json, indent=2), encoding="utf-8")

    print(json.dumps(queue["stats"], indent=2))


if __name__ == "__main__":
    main()
