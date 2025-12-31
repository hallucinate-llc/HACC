#!/usr/bin/env python3
"""generate_third_party_download_queue.py

Build a prioritized download queue for candidate third-party organizations/domains
based on `research_results/third_party_candidates.json`.

Goal: create a *conservative* list of URLs to fetch (about/policies/program docs)
for likely relevant non-government organizations and portals.

Output:
- research_results/third_party_download_queue.json

This script does not download; it only prepares the queue.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from urllib.parse import urlparse

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

CANDIDATES_JSON = Path("research_results/third_party_candidates.json")
OUTPUT_JSON = Path("research_results/third_party_download_queue.json")

EXCLUDE_DOMAIN_SUBSTR = [
    "myworkdayjobs.com",
    "govdelivery.com",
    "employeesearch.",
    "google.com",
    "youtu.be",
    "youtube.com",
    "t.co",
    "goo.gl",
    "berkeley.edu",

    # Common metadata/tech noise
    "schema.org",
    "ogp.me",
    "wikipedia.org",
    "api.w.org",
    "s.w.org",
    "rdfs.org",
    "gmpg.org",
    "drupal.org",
    "github.com",
    "cloudfront.net",
    "tinyurl.com",
    "example.com",
    "x.com",
]

# User-directed manual additions (ensures coverage even if not yet referenced in corpus)
MANUAL_INCLUDE_DOMAINS = [
    "quantumresidential.com",
    "www.quantumresidential.com",
]


def domain_is_valid(domain: str) -> bool:
    d = domain.lower().strip()
    if not d or "\x00" in d:
        return False
    if len(d) > 253:
        return False
    # Only common hostname characters
    if any(ch for ch in d if not (ch.isalnum() or ch in {".", "-"})):
        return False
    # Label constraints
    labels = d.split(".")
    if any((not lab) or len(lab) > 63 for lab in labels):
        return False

    # Heuristic TLD check: allow any 2-letter ccTLD, and a small set of common gTLDs.
    tld = labels[-1]
    common_gtlds = {
        "com", "org", "net", "edu", "gov", "us", "info", "io", "co", "biz", "me",
    }
    if not (len(tld) == 2 and tld.isalpha()) and tld not in common_gtlds:
        return False
    return True

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


def domain_ok(domain: str) -> bool:
    d = domain.lower()
    if not d:
        return False
    if not domain_is_valid(d):
        return False
    return not any(s in d for s in EXCLUDE_DOMAIN_SUBSTR)


def is_non_gov(domain: str) -> bool:
    d = domain.lower()
    return not (d.endswith(".gov") or d.endswith(".us") or d.endswith(".state.or.us") or d.endswith(".oregon.gov"))


def uniq(seq: list[str]) -> list[str]:
    seen = set()
    out = []
    for x in seq:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


@dataclass
class QueueItem:
    domain: str
    score: int
    seed_urls: list[str]
    guessed_urls: list[str]
    evidence_urls: list[str]


def main() -> None:
    if not CANDIDATES_JSON.exists():
        raise SystemExit(f"Missing {CANDIDATES_JSON}")

    data = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))
    candidates = data.get("candidates", [])

    # Select domain candidates only
    domain_candidates = [c for c in candidates if c.get("candidate_type") == "domain"]

    queue: list[QueueItem] = []
    queued_domains: set[str] = set()
    for c in domain_candidates:
        domain = c.get("domain") or c.get("candidate")
        if not domain_ok(domain):
            continue

        domain = domain.lower().strip()
        if domain in queued_domains:
            continue

        score = int(c.get("score", 0))

        # Prefer non-government orgs; keep a few portals if they were ranked highly.
        if not is_non_gov(domain) and score < 35:
            continue

        evidence_urls = []
        for ev in c.get("evidence", []) or []:
            url = ev.get("url")
            if url:
                evidence_urls.append(url)

        # Seed URLs
        seed_urls = [f"https://{domain}", f"http://{domain}"]

        guessed_urls = []
        for base in [f"https://{domain}", f"http://{domain}"]:
            for p in COMMON_PATHS:
                guessed_urls.append(base.rstrip("/") + p)

        queue.append(QueueItem(
            domain=domain,
            score=score,
            seed_urls=uniq(seed_urls),
            guessed_urls=uniq(guessed_urls),
            evidence_urls=uniq(evidence_urls),
        ))
        queued_domains.add(domain)

    # Manual seeds
    for domain in MANUAL_INCLUDE_DOMAINS:
        domain = domain.lower().strip()
        if domain in queued_domains:
            continue
        if not domain_ok(domain):
            continue

        seed_urls = [f"https://{domain}", f"http://{domain}"]
        guessed_urls = []
        for base in [f"https://{domain}", f"http://{domain}"]:
            for p in COMMON_PATHS:
                guessed_urls.append(base.rstrip("/") + p)

        queue.append(QueueItem(
            domain=domain,
            score=50,
            seed_urls=uniq(seed_urls),
            guessed_urls=uniq(guessed_urls),
            evidence_urls=[],
        ))
        queued_domains.add(domain)

    queue.sort(key=lambda x: x.score, reverse=True)

    out = {
        "source": str(CANDIDATES_JSON),
        "domain_count": len(queue),
        "notes": "Queue is conservative; verify relevance before large-scale crawling.",
        "items": [asdict(i) for i in queue],
    }

    OUTPUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")
    logger.info(f"Wrote {OUTPUT_JSON} ({len(queue)} domains)")


if __name__ == "__main__":
    main()
