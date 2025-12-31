#!/usr/bin/env python3
"""download_third_party_queue.py

Download a curated set of third-party/partner organization pages/docs from
`research_results/third_party_download_queue.json`.

Design goals:
- Conservative and resumable: skip already-downloaded URLs.
- Throttled: per-request delay + basic backoff retries.
- Traceable: write a manifest (JSON + CSV) with status, final URL, content type,
  bytes downloaded, and local path.

This tool is for compliance-oriented document collection and does not infer
wrongdoing.

Outputs (default):
- research_results/third_party_downloads/
- research_results/third_party_download_manifest.json
- research_results/third_party_download_manifest.csv
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import logging
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_QUEUE = Path("research_results/third_party_download_queue.json")
DEFAULT_OUT_DIR = Path("research_results/third_party_downloads")
DEFAULT_MANIFEST_JSON = Path("research_results/third_party_download_manifest.json")
DEFAULT_MANIFEST_CSV = Path("research_results/third_party_download_manifest.csv")

USER_AGENT = "Mozilla/5.0 (Research Assistant; compliance document collection)"

# Keep it conservative; can be overridden via CLI
DEFAULT_MAX_DOMAINS = 15
DEFAULT_MAX_URLS_PER_DOMAIN = 25
DEFAULT_DELAY_SECONDS = 1.0
DEFAULT_CONNECT_TIMEOUT_SECONDS = 10
DEFAULT_READ_TIMEOUT_SECONDS = 20
DEFAULT_MAX_BYTES = 15 * 1024 * 1024  # 15MB
DEFAULT_RETRIES = 2


@dataclass
class ManifestRow:
    domain: str
    url: str
    final_url: str
    status: str
    http_status: int
    content_type: str
    bytes: int
    saved_path: str
    error: str


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8", errors="ignore")).hexdigest()


def clean_domain(domain: str) -> str:
    """Normalize a domain string extracted from heuristics (remove control chars)."""
    if not domain:
        return ""
    d = domain.replace("\x00", "").strip().lower()
    # If something accidentally includes a scheme/path, parse it.
    if "://" in d:
        try:
            d = urlparse(d).netloc.lower()
        except Exception:
            pass
    # Remove any trailing slashes/spaces
    d = d.split("/")[0].strip()
    return d


def safe_folder_name(name: str) -> str:
    """Make a filesystem-safe folder name."""
    n = clean_domain(name)
    # Keep only common hostname chars
    n = "".join(ch for ch in n if ch.isalnum() or ch in {".", "-"})
    return n[:200]


def safe_filename_from_url(url: str, content_type: str) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        base = parsed.netloc
    else:
        base = f"{parsed.netloc}_{path.replace('/', '_')}"

    base = base.replace("%", "_")

    # Trim very long names and add hash for uniqueness
    if len(base) > 120:
        base = base[:120] + "_" + sha1(url)[:10]

    # Extension heuristics
    suffix = Path(parsed.path).suffix
    if suffix:
        return base

    ct = (content_type or "").lower()
    if "pdf" in ct:
        return base + ".pdf"
    if "msword" in ct:
        return base + ".doc"
    if "officedocument.wordprocessingml" in ct:
        return base + ".docx"
    if "officedocument.spreadsheetml" in ct:
        return base + ".xlsx"
    if "html" in ct:
        return base + ".html"

    # default
    return base + ".bin"


def same_domain(url: str, domain: str) -> bool:
    try:
        return clean_domain(urlparse(url).netloc) == clean_domain(domain)
    except Exception:
        return False


def request_with_retries(
    session: requests.Session,
    url: str,
    timeout: tuple[float, float],
    max_bytes: int,
    retries: int,
) -> tuple[Optional[bytes], str, int, str, str]:
    """Return: (content, final_url, http_status, content_type, error)"""

    last_error = ""
    for attempt in range(retries + 1):
        try:
            with session.get(url, timeout=timeout, allow_redirects=True, stream=True) as resp:
                final_url = resp.url
                http_status = int(resp.status_code)
                content_type = resp.headers.get("Content-Type", "")

                if http_status >= 400:
                    return None, final_url, http_status, content_type, f"http_{http_status}"

                # Respect max_bytes; check Content-Length if available
                cl = resp.headers.get("Content-Length")
                if cl is not None:
                    try:
                        if int(cl) > max_bytes:
                            return None, final_url, http_status, content_type, f"too_large_content_length:{cl}"
                    except ValueError:
                        pass

                chunks = []
                total = 0
                for chunk in resp.iter_content(chunk_size=64 * 1024):
                    if not chunk:
                        continue
                    total += len(chunk)
                    if total > max_bytes:
                        return None, final_url, http_status, content_type, f"too_large_streamed:{total}"
                    chunks.append(chunk)

                return b"".join(chunks), final_url, http_status, content_type, ""

        except requests.exceptions.ConnectTimeout as e:
            last_error = f"connect_timeout: {e}"
        except requests.exceptions.ReadTimeout as e:
            last_error = f"read_timeout: {e}"
        except requests.exceptions.Timeout as e:
            last_error = f"timeout: {e}"

        except Exception as e:
            last_error = f"{type(e).__name__}: {e}"

            if attempt < retries:
                time.sleep(1.5 ** attempt)
                continue
            return None, url, 0, "", last_error

        if attempt < retries:
            time.sleep(1.5 ** attempt)
            continue
        return None, url, 0, "", last_error

    return None, url, 0, "", last_error


def write_manifest(json_path: Path, csv_path: Path, rows: list[ManifestRow]) -> None:
    json_path.write_text(json.dumps([asdict(r) for r in rows], indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow([
            "domain",
            "url",
            "final_url",
            "status",
            "http_status",
            "content_type",
            "bytes",
            "saved_path",
            "error",
        ])
        for r in rows:
            w.writerow([
                r.domain,
                r.url,
                r.final_url,
                r.status,
                r.http_status,
                r.content_type,
                r.bytes,
                r.saved_path,
                r.error,
            ])


def maybe_flush_manifest(
    *,
    json_path: Path,
    csv_path: Path,
    rows: list[ManifestRow],
    dirty_counter: int,
    flush_every: int,
) -> int:
    """Persist manifest periodically so a Ctrl+C doesn't lose progress."""
    if dirty_counter >= flush_every:
        write_manifest(json_path, csv_path, rows)
        return 0
    return dirty_counter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue", default=str(DEFAULT_QUEUE))
    ap.add_argument("--out", default=str(DEFAULT_OUT_DIR))
    ap.add_argument("--manifest-json", default=str(DEFAULT_MANIFEST_JSON))
    ap.add_argument("--manifest-csv", default=str(DEFAULT_MANIFEST_CSV))
    ap.add_argument("--max-domains", type=int, default=DEFAULT_MAX_DOMAINS)
    ap.add_argument("--max-urls-per-domain", type=int, default=DEFAULT_MAX_URLS_PER_DOMAIN)
    ap.add_argument("--delay", type=float, default=DEFAULT_DELAY_SECONDS)
    ap.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Legacy: set BOTH connect+read timeout seconds (overrides --connect-timeout/--read-timeout)",
    )
    ap.add_argument("--connect-timeout", type=float, default=DEFAULT_CONNECT_TIMEOUT_SECONDS)
    ap.add_argument("--read-timeout", type=float, default=DEFAULT_READ_TIMEOUT_SECONDS)
    ap.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES)
    ap.add_argument("--retries", type=int, default=DEFAULT_RETRIES)
    ap.add_argument("--include-guessed", action="store_true", help="Also download guessed_urls, not just evidence_urls/seed_urls")
    ap.add_argument(
        "--flush-every",
        type=int,
        default=10,
        help="Write manifest every N new rows to make the run resilient to interruptions (default: 10)",
    )
    args = ap.parse_args()

    if args.timeout is None:
        timeout = (float(args.connect_timeout), float(args.read_timeout))
    else:
        timeout = (float(args.timeout), float(args.timeout))

    queue_path = Path(args.queue)
    out_dir = Path(args.out)
    manifest_json = Path(args.manifest_json)
    manifest_csv = Path(args.manifest_csv)

    if not queue_path.exists():
        raise SystemExit(f"Missing queue file: {queue_path}")

    out_dir.mkdir(parents=True, exist_ok=True)

    queue = load_json(queue_path)
    items = queue.get("items", [])

    # Load existing manifest for resumability
    existing: dict[str, ManifestRow] = {}
    if manifest_json.exists():
        try:
            prior = json.loads(manifest_json.read_text(encoding="utf-8"))
            for row in prior:
                existing[row.get("url", "")] = ManifestRow(**row)
            logger.info(f"Loaded existing manifest: {len(existing)} rows")
        except Exception:
            logger.warning("Could not parse existing manifest; starting fresh")

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    rows: list[ManifestRow] = list(existing.values())
    seen_urls = set(existing.keys())

    dirty = 0

    domains_processed = 0
    downloads_ok = 0

    try:
        for item in items:
            if domains_processed >= args.max_domains:
                break

            domain_raw = item.get("domain", "")
            domain = clean_domain(domain_raw)
            if not domain:
                continue

            evidence_urls = item.get("evidence_urls", []) or []

            # Build candidate URL list
            urls: list[str] = []
            urls.extend(evidence_urls)
            urls.extend(item.get("seed_urls", []) or [])
            if args.include_guessed:
                urls.extend(item.get("guessed_urls", []) or [])

            # Deduplicate preserving order
            deduped: list[str] = []
            seen_local: set[str] = set()
            for u in urls:
                if u and u not in seen_local:
                    seen_local.add(u)
                    deduped.append(u)

            to_fetch = deduped[: args.max_urls_per_domain]
            if not to_fetch:
                continue

            domain_dir = out_dir / (safe_folder_name(domain) or ("unknown_" + sha1(domain_raw)[:8]))
            domain_dir.mkdir(parents=True, exist_ok=True)

            domains_processed += 1
            logger.info(f"Domain {domains_processed}/{args.max_domains}: {domain} ({len(to_fetch)} urls)")

            for url in to_fetch:
                if url in seen_urls:
                    continue

                # Safety: keep to same domain when downloading guessed URLs
                if args.include_guessed and (url not in evidence_urls):
                    if not same_domain(url, domain):
                        rows.append(ManifestRow(domain, url, url, "skipped", 0, "", 0, "", "cross_domain"))
                        seen_urls.add(url)
                        dirty += 1
                        dirty = maybe_flush_manifest(
                            json_path=manifest_json,
                            csv_path=manifest_csv,
                            rows=rows,
                            dirty_counter=dirty,
                            flush_every=args.flush_every,
                        )
                        continue

                time.sleep(max(args.delay, 0))

                content, final_url, http_status, content_type, error = request_with_retries(
                    session=session,
                    url=url,
                    timeout=timeout,
                    max_bytes=args.max_bytes,
                    retries=args.retries,
                )

                if content is None:
                    rows.append(ManifestRow(domain, url, final_url, "error", http_status, content_type, 0, "", error))
                    seen_urls.add(url)
                    dirty += 1
                    dirty = maybe_flush_manifest(
                        json_path=manifest_json,
                        csv_path=manifest_csv,
                        rows=rows,
                        dirty_counter=dirty,
                        flush_every=args.flush_every,
                    )
                    continue

                filename = safe_filename_from_url(final_url, content_type)
                save_path = domain_dir / filename

                # Avoid overwriting collisions
                if save_path.exists():
                    save_path = domain_dir / (save_path.stem + "_" + sha1(final_url)[:10] + save_path.suffix)

                save_path.write_bytes(content)
                rows.append(ManifestRow(domain, url, final_url, "ok", http_status, content_type, len(content), str(save_path), ""))
                seen_urls.add(url)
                downloads_ok += 1
                dirty += 1
                dirty = maybe_flush_manifest(
                    json_path=manifest_json,
                    csv_path=manifest_csv,
                    rows=rows,
                    dirty_counter=dirty,
                    flush_every=args.flush_every,
                )

    except KeyboardInterrupt:
        # Persist partial results before exiting.
        logger.warning("Interrupted; writing partial manifest before exit")
        write_manifest(manifest_json, manifest_csv, rows)
        raise

    write_manifest(manifest_json, manifest_csv, rows)
    logger.info(f"Done. domains_processed={domains_processed} ok_downloads={downloads_ok} manifest_rows={len(rows)}")


if __name__ == "__main__":
    main()
