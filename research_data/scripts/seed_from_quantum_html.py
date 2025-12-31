#!/usr/bin/env python3
"""seed_from_quantum_html.py

Purpose
- Treat local HTML artifacts (e.g., Quantum_residential*.html) as *seed sources*.
- Extract outbound URLs/domains (including Google redirect links), de-noise them,
  and generate a small conservative download queue.

Outputs
- research_results/quantum_seed_links.json
- research_results/quantum_seed_domains.json
- research_results/quantum_seed_download_queue.json

Notes
- This is for compliance-oriented document collection; it does not infer wrongdoing.
"""

from __future__ import annotations

import argparse
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import parse_qs, unquote, urldefrag, urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

OUT_LINKS = Path("research_results/quantum_seed_links.json")
OUT_DOMAINS = Path("research_results/quantum_seed_domains.json")
OUT_QUEUE = Path("research_results/quantum_seed_download_queue.json")

URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)

ASSET_EXTS = {
    ".js",
    ".css",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".map",
}

# Domains that are typically not useful as third-party policy/procurement sources
NOISE_DOMAIN_SUBSTR = [
    "google.com",
    "gstatic.com",
    "googletagmanager",
    "google-analytics",
    "fonts.googleapis.com",
    "fonts.gstatic.com",
    "schema.org",
    "ogp.me",
    "api.w.org",
    "s.w.org",
    "rdfs.org",
    "gmpg.org",
    "cloudfront.net",
    "drupal.org",
    "github.com",
    "example.com",
    "tinyurl.com",
    "x.com",
    "twitter.com",
    "youtube.com",
    "w3.org",
    "googleusercontent.com",
]

# Keep these even if they look "governmenty" because they are primary portals
KEEP_PORTALS = {
    "oregonbuys.gov",
    "sos.oregon.gov",
    "www.oregon.gov",
    "oregon.gov",
    "www.portland.gov",
    "portland.gov",
    "www.oregonmetro.gov",
    "oregonmetro.gov",
}

# Specifically ignore Berkeley as requested
IGNORE_DOMAIN_SUBSTR = ["berkeley.edu"]

COMMON_PATHS = [
    "/about",
    "/about-us",
    "/who-we-are",
    "/mission",
    "/leadership",
    "/programs",
    "/services",
    "/resources",
    "/publications",
    "/reports",
    "/documents",
    "/policies",
    "/policy",
    "/nondiscrimination",
    "/non-discrimination",
    "/civil-rights",
    "/fair-housing",
    "/fairhousing",
    "/complaints",
    "/grants",
    "/contracts",
    "/rfp",
    "/rfq",
    "/procurement",
]


def normalize_url(url: str) -> str:
    url = url.replace("\x00", "").strip()
    url = url.strip("\"'()[]{}<>.,;\n\r\t ")
    url, _frag = urldefrag(url)
    return url


def is_asset_url(url: str) -> bool:
    try:
        p = urlparse(url)
    except Exception:
        return True
    return Path(p.path.lower()).suffix in ASSET_EXTS


def extract_google_redirect_target(url: str) -> str | None:
    """Google SERP links often use /url?q=<target>&..."""
    try:
        p = urlparse(url)
    except Exception:
        return None

    if p.netloc.lower() not in {"www.google.com", "google.com"}:
        return None
    if not p.path.startswith("/url"):
        return None

    qs = parse_qs(p.query)
    q = qs.get("q")
    if not q:
        return None
    target = q[0]
    try:
        target = unquote(target)
    except Exception:
        pass
    target = normalize_url(target)
    if target.startswith("http://") or target.startswith("https://"):
        return target
    return None


def extract_google_search_q_target(url: str) -> str | None:
    """Some captures contain https://www.google.com/search?q=<url>"""
    try:
        p = urlparse(url)
    except Exception:
        return None

    if p.netloc.lower() not in {"www.google.com", "google.com"}:
        return None
    if not p.path.startswith("/search"):
        return None

    qs = parse_qs(p.query)
    q = qs.get("q")
    if not q:
        return None

    target = q[0]
    try:
        target = unquote(target)
    except Exception:
        pass
    target = normalize_url(target)
    if target.startswith("http://") or target.startswith("https://"):
        return target
    return None


def domain_of(url: str) -> str:
    try:
        d = urlparse(url).netloc.lower().strip()
        d = d.replace("\x00", "")
        return d
    except Exception:
        return ""


def domain_is_noise(domain: str) -> bool:
    d = (domain or "").lower()
    if not d:
        return True
    if any(s in d for s in IGNORE_DOMAIN_SUBSTR):
        return True
    if any(s in d for s in NOISE_DOMAIN_SUBSTR):
        return True
    return False


def build_guessed_urls(domain: str) -> list[str]:
    out: list[str] = []
    for base in [f"https://{domain}", f"http://{domain}"]:
        out.append(base)
        for p in COMMON_PATHS:
            out.append(base.rstrip("/") + p)
    # de-dupe preserving order
    seen = set()
    uniq = []
    for u in out:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


@dataclass
class QueueItem:
    domain: str
    score: int
    evidence_urls: list[str]
    seed_urls: list[str]
    guessed_urls: list[str]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "paths",
        nargs="*",
        default=["Quantum_residential.html", "Quantum_residential2.html"],
        help="Local HTML files to treat as seeds",
    )
    ap.add_argument(
        "--max-domains",
        type=int,
        default=25,
        help="Max unique domains to include in the generated queue",
    )
    args = ap.parse_args()

    paths = [Path(p) for p in args.paths]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise SystemExit(f"Missing seed files: {missing}")

    all_urls: list[str] = []
    by_source: dict[str, list[str]] = {}

    for p in paths:
        raw = p.read_text(encoding="utf-8", errors="ignore")
        urls = [normalize_url(u) for u in URL_RE.findall(raw)]
        # Expand google redirect targets
        expanded: list[str] = []
        for u in urls:
            t = extract_google_redirect_target(u)
            if t:
                expanded.append(t)
            t2 = extract_google_search_q_target(u)
            if t2:
                expanded.append(t2)
            expanded.append(u)

        # Filter empties + assets, keep order
        seen = set()
        cleaned = []
        for u in expanded:
            if not u:
                continue
            if is_asset_url(u):
                continue
            if u in seen:
                continue
            seen.add(u)
            cleaned.append(u)

        by_source[str(p)] = cleaned
        all_urls.extend(cleaned)

    # de-dupe across all
    seen = set()
    uniq_urls = []
    for u in all_urls:
        if u and u not in seen:
            seen.add(u)
            uniq_urls.append(u)

    domains = [domain_of(u) for u in uniq_urls if domain_of(u)]
    domain_counts = Counter(domains)

    OUT_LINKS.parent.mkdir(parents=True, exist_ok=True)

    OUT_LINKS.write_text(
        json.dumps(
            {
                "seed_files": [str(p) for p in paths],
                "url_count": len(uniq_urls),
                "urls": uniq_urls,
                "urls_by_source": by_source,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    # Build domain summary + a conservative queue
    domain_rows = []
    evidence_by_domain: dict[str, list[str]] = defaultdict(list)
    for u in uniq_urls:
        d = domain_of(u)
        if not d:
            continue
        evidence_by_domain[d].append(u)

    for d, c in domain_counts.most_common():
        domain_rows.append(
            {
                "domain": d,
                "mentions": c,
                "ignored": domain_is_noise(d) and d not in KEEP_PORTALS,
            }
        )

    OUT_DOMAINS.write_text(
        json.dumps(
            {
                "domain_count": len(domain_rows),
                "domains": domain_rows,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    queue_items: list[QueueItem] = []
    for d, c in domain_counts.most_common():
        if d not in KEEP_PORTALS and domain_is_noise(d):
            continue

        # Prefer non-gov unless it's a kept portal
        is_govish = d.endswith(".gov") or d.endswith(".us") or d.endswith(".oregon.gov")
        if is_govish and d not in KEEP_PORTALS:
            continue

        ev = []
        for u in evidence_by_domain.get(d, []):
            if u not in ev:
                ev.append(u)

        # score: mentions-based
        score = min(100, 10 + c * 5)
        queue_items.append(
            QueueItem(
                domain=d,
                score=score,
                evidence_urls=ev[:25],
                seed_urls=[f"https://{d}", f"http://{d}"],
                guessed_urls=build_guessed_urls(d),
            )
        )

    queue_items.sort(key=lambda x: x.score, reverse=True)
    queue_items = queue_items[: args.max_domains]

    OUT_QUEUE.write_text(
        json.dumps(
            {
                "source": "quantum_seed_html",
                "seed_files": [str(p) for p in paths],
                "domain_count": len(queue_items),
                "items": [asdict(i) for i in queue_items],
                "notes": "Generated from Quantum_residential*.html seed artifacts; conservative, verify relevance before scaling.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    logger.info(f"Wrote {OUT_LINKS}")
    logger.info(f"Wrote {OUT_DOMAINS}")
    logger.info(f"Wrote {OUT_QUEUE} ({len(queue_items)} domains)")


if __name__ == "__main__":
    main()
