#!/usr/bin/env python3
"""extract_quantum_residential_documents.py

Extract document URLs referenced by downloaded Quantum Residential pages.

Primary use-case:
- We already downloaded a few Quantum Residential HTML pages into
  research_results/third_party_downloads/{quantumresidential.com,www.quantumresidential.com}/
- This script parses those local HTML files, resolves relative links using the
  corresponding final_url from an existing download manifest, and emits:
  1) a download queue JSON compatible with download_third_party_queue.py
  2) an evidence JSON mapping source page -> extracted doc links

This is conservative: it only treats "documents" as URLs ending in common file
extensions (pdf/doc/docx/xls/xlsx/ppt/pptx/rtf/txt/csv) or obvious WP upload
assets. It does not attempt to crawl.
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


ASSET_EXTENSIONS = {
    # Web assets
    ".css",
    ".js",
    ".mjs",
    ".json",
    ".xml",
    ".map",
    ".txt",
    # Images/icons
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".svg",
    ".ico",
    # Fonts
    ".woff",
    ".woff2",
    ".ttf",
    ".otf",
    ".eot",
    # Documents already covered by DOC_EXTENSIONS; kept separate for clarity
}


HREF_SRC_RE = re.compile(r"(?i)\b(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]")
RAW_DOC_URL_RE = re.compile(r"https?://[^\s\"'<>]+\.(?:pdf|docx?|xlsx?|pptx?|rtf|txt|csv)(?:\?[^\s\"'<>]*)?", re.IGNORECASE)
RAW_HTTP_URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)


@dataclass(frozen=True)
class EvidenceRow:
    source_saved_path: str
    source_url: str
    doc_url: str


def load_manifest_rows(manifest_path: Path) -> list[dict]:
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [r for r in data if isinstance(r, dict)]
    except Exception:
        return []
    return []


def expand_paths_csv(value: str) -> list[Path]:
    """Expand a comma-separated list of paths.

    Supports glob patterns (e.g., research_results/third_party_download_manifest*.json).
    """
    out: list[Path] = []
    for token in [t.strip() for t in str(value).split(",") if t.strip()]:
        # Basic glob detection
        if any(ch in token for ch in ("*", "?", "[", "]")):
            out.extend(sorted(Path().glob(token)))
        else:
            out.append(Path(token))
    # Deduplicate while preserving order
    seen: set[str] = set()
    deduped: list[Path] = []
    for p in out:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(p)
    return deduped


def build_saved_path_to_final_url(manifest_paths: Iterable[Path]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for mp in manifest_paths:
        if not mp.exists():
            continue
        for row in load_manifest_rows(mp):
            saved_path = row.get("saved_path")
            final_url = row.get("final_url") or row.get("url")
            status = row.get("status")
            if not saved_path or not final_url or status != "ok":
                continue
            mapping[str(saved_path)] = str(final_url)
    return mapping


def is_probably_interesting_file_url(url: str, *, include_assets: bool) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    path = (parsed.path or "").lower()
    if not path:
        return False

    suffix = Path(path).suffix
    if suffix in DOC_EXTENSIONS:
        return True
    if include_assets and suffix in ASSET_EXTENSIONS:
        return True
    return False


def maybe_unwrap_google(url: str) -> str:
    """If the URL is a Google wrapper, attempt to extract the underlying target."""
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


def _unescape_common_backslash_u_sequences(s: str) -> str:
    """Best-effort unescape for strings containing literal \\uXXXX sequences."""

    if "\\u" not in s:
        return s

    replacements = {
        "\\u0026": "&",
        "\\u003d": "=",
        "\\u003f": "?",
        "\\u002f": "/",
        "\\u003a": ":",
        "\\u0025": "%",
        "\\u0023": "#",
        "\\u0020": " ",
        "\\u0022": '"',
    }
    for k, v in replacements.items():
        s = s.replace(k, v).replace(k.upper(), v)
    return s


def _strip_embedded_junk(s: str) -> str:
    """Strip common junk that appears after a URL in embedded JSON/HTML strings."""

    if not s:
        return s

    s = _unescape_common_backslash_u_sequences(s)

    # If multiple URLs are glued together, keep only the first.
    urls = RAW_HTTP_URL_RE.findall(s)
    if len(urls) > 1:
        s = urls[0]

    # Cut off at common embedded string delimiters.
    for delim in (
        "&quot;",
        "\"",
        "',",
        "\",",
        "</",
        "]",
        "}",
    ):
        if delim in s:
            s = s.split(delim, 1)[0]

    s = s.rstrip("\r\n\t ")
    s = s.rstrip(")].,;\"")
    return s


def normalize_link(raw: str, base_url: str) -> str | None:
    if not raw:
        return None

    raw = _strip_embedded_junk(raw.strip())
    if not raw:
        return None

    lowered = raw.lower()
    if lowered.startswith("mailto:") or lowered.startswith("tel:"):
        return None
    if lowered.startswith("javascript:"):
        return None
    if lowered.startswith("data:"):
        return None

    absolute = urljoin(base_url, raw)
    absolute, _frag = urldefrag(absolute)

    # Unwrap Google redirect/search wrappers when they carry the true target.
    absolute = maybe_unwrap_google(absolute)

    try:
        parsed = urlparse(absolute)
    except Exception:
        return None

    if parsed.scheme not in {"http", "https"}:
        return None
    if not parsed.netloc:
        return None

    return absolute


def extract_links_from_html(html_text: str) -> list[str]:
    return [m.group(1) for m in HREF_SRC_RE.finditer(html_text)]


def extract_raw_doc_urls(html_text: str) -> list[str]:
    # Seed HTML sometimes embeds multiple URLs inside a single JSON/string fragment.
    # Start with doc-ish matches, then split on repeated http(s) occurrences.
    out: list[str] = []
    for m in RAW_DOC_URL_RE.finditer(html_text):
        s = m.group(0)
        starts = [mm.start() for mm in re.finditer(r"https?://", s, flags=re.IGNORECASE)]
        if len(starts) <= 1:
            out.append(s)
            continue
        for i, st in enumerate(starts):
            en = starts[i + 1] if i + 1 < len(starts) else len(s)
            part = s[st:en]
            if part:
                out.append(part)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()

    ap.add_argument(
        "--downloads-root",
        default="research_results/third_party_downloads",
        help="Root folder containing per-domain download folders",
    )
    ap.add_argument(
        "--seed-html",
        default="Quantum_residential2.html",
        help="Comma-separated local HTML file(s) to scan for document URLs (in addition to downloaded pages)",
    )
    ap.add_argument(
        "--domains",
        default="quantumresidential.com,www.quantumresidential.com",
        help="Comma-separated list of domain folders to scan under downloads-root",
    )
    ap.add_argument(
        "--manifests",
        default="research_results/third_party_download_manifest*.json",
        help="Comma-separated manifest JSON paths (or glob patterns) used to resolve saved_path -> final_url",
    )
    ap.add_argument(
        "--restrict-domain-suffix",
        default="quantumresidential.com",
        help=(
            "If set, only include extracted document URLs whose host ends with this suffix. "
            "Set to empty string to allow external document hosts."
        ),
    )
    ap.add_argument(
        "--out-queue",
        default="research_results/quantum_residential_documents_queue.json",
        help="Output queue JSON (compatible with download_third_party_queue.py)",
    )
    ap.add_argument(
        "--out-evidence",
        default="research_results/quantum_residential_documents_evidence.json",
        help="Output evidence JSON mapping source page -> doc link(s)",
    )
    ap.add_argument(
        "--include-assets",
        action="store_true",
        help="Also include common static assets (images/CSS/JS/fonts) hosted on the target domain",
    )
    ap.add_argument(
        "--max-doc-urls",
        type=int,
        default=5000,
        help="Cap total unique doc URLs collected (safety valve)",
    )

    args = ap.parse_args()

    downloads_root = Path(args.downloads_root)
    domain_folders = [d.strip() for d in str(args.domains).split(",") if d.strip()]
    manifest_paths = expand_paths_csv(str(args.manifests))
    seed_html_paths = [Path(p.strip()) for p in str(args.seed_html).split(",") if p.strip()]

    restrict_suffix = (args.restrict_domain_suffix or "").strip().lower()

    saved_to_final = build_saved_path_to_final_url(manifest_paths)

    evidence: list[EvidenceRow] = []
    doc_urls_by_domain: dict[str, set[str]] = defaultdict(set)
    total_doc_urls = 0
    skipped_external = 0

    total_html_files = 0
    total_links_seen = 0

    # 1) Scan downloaded Quantum pages (helps for relative links, WP doc links, etc.)
    for domain_folder in domain_folders:
        folder = downloads_root / domain_folder
        if not folder.exists():
            continue

        for path in folder.rglob("*"):
            if not path.is_file():
                continue

            if path.suffix.lower() not in {".html", ".htm"}:
                continue

            total_html_files += 1

            # Resolve base URL for relative links.
            base_url = saved_to_final.get(str(path), "https://www.quantumresidential.com/")

            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue

            raw_links = extract_links_from_html(text)
            total_links_seen += len(raw_links)

            for raw in raw_links:
                normalized = normalize_link(raw, base_url)
                if not normalized:
                    continue

                if not is_probably_interesting_file_url(normalized, include_assets=bool(args.include_assets)):
                    continue

                doc_domain = (urlparse(normalized).netloc or "").lower().strip()
                if not doc_domain:
                    continue

                if restrict_suffix and not doc_domain.endswith(restrict_suffix):
                    skipped_external += 1
                    continue

                if total_doc_urls >= args.max_doc_urls:
                    break

                if normalized not in doc_urls_by_domain[doc_domain]:
                    doc_urls_by_domain[doc_domain].add(normalized)
                    total_doc_urls += 1
                    evidence.append(
                        EvidenceRow(
                            source_saved_path=str(path),
                            source_url=base_url,
                            doc_url=normalized,
                        )
                    )

    # 2) Scan the local seed HTML file(s) directly (e.g., Quantum_residential2.html)
    for seed_path in seed_html_paths:
        if not seed_path.exists() or not seed_path.is_file():
            continue

        try:
            seed_text = seed_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        seed_links = extract_links_from_html(seed_text)
        seed_raw_docs = extract_raw_doc_urls(seed_text)
        total_links_seen += len(seed_links) + len(seed_raw_docs)

        # For local seed files, base URL is unknown; urljoin won't help relative paths.
        base_url = "https://www.quantumresidential.com/"

        for raw in list(seed_links) + list(seed_raw_docs):
            normalized = normalize_link(raw, base_url)
            if not normalized:
                continue
            if not is_probably_interesting_file_url(normalized, include_assets=bool(args.include_assets)):
                continue

            doc_domain = (urlparse(normalized).netloc or "").lower().strip()
            if not doc_domain:
                continue

            if restrict_suffix and not doc_domain.endswith(restrict_suffix):
                skipped_external += 1
                continue

            if total_doc_urls >= args.max_doc_urls:
                break

            if normalized not in doc_urls_by_domain[doc_domain]:
                doc_urls_by_domain[doc_domain].add(normalized)
                total_doc_urls += 1
                evidence.append(
                    EvidenceRow(
                        source_saved_path=str(seed_path),
                        source_url=str(seed_path),
                        doc_url=normalized,
                    )
                )

    # Build queue structure expected by download_third_party_queue.py
    items = []
    for domain, urls in sorted(doc_urls_by_domain.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        items.append(
            {
                "domain": domain,
                "score": 100,
                "evidence_urls": sorted(urls),
                "seed_urls": [],
                "guessed_urls": [],
                "notes": "Extracted from downloaded Quantum Residential HTML pages",
            }
        )

    out_queue = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": {
            "downloads_root": str(downloads_root),
            "domains_scanned": domain_folders,
            "manifests": [str(p) for p in manifest_paths],
        },
        "stats": {
            "html_files_scanned": total_html_files,
            "raw_links_seen": total_links_seen,
            "doc_domains": len(items),
            "doc_urls_total": sum(len(i["evidence_urls"]) for i in items),
            "skipped_external_doc_urls": skipped_external,
        },
        "items": items,
    }

    Path(args.out_queue).write_text(json.dumps(out_queue, indent=2), encoding="utf-8")
    Path(args.out_evidence).write_text(
        json.dumps([e.__dict__ for e in evidence], indent=2),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "html_files_scanned": total_html_files,
                "raw_links_seen": total_links_seen,
                "doc_domains": len(items),
                "doc_urls_total": sum(len(i["evidence_urls"]) for i in items),
                "skipped_external_doc_urls": skipped_external,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
