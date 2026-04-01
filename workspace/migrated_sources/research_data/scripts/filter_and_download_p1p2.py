#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""
Filter P1/P2 Oregon links to likely policy documents and download them.
Criteria: pdf/doc/docx/xlsx and housing/fair-housing/discrimination/procurement keywords.
"""
import json
import time
import logging
from pathlib import Path
from urllib.parse import urlparse
from collections import Counter
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SOURCE_JSON = Path("research_results/oregon_p1p2_links.json")
OUTPUT_JSON = Path("research_results/oregon_p1p2_filtered_links.json")
AUDIT_JSON = Path("research_results/oregon_p1p2_filter_audit.json")
DOWNLOAD_DIR = Path("research_results/oregon_p1p2_downloads")
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

EXT_KEEP = {'.pdf', '.doc', '.docx', '.xlsx'}
KEYWORDS = [
    'fair-housing', 'fairhousing', 'housing', 'civil-rights', 'civil', 'discrimination', 'equal', 'equity',
    'procurement', 'procure', 'contract', 'rulemaking', 'rules', 'statute', 'policy', 'guidance',
    'boli', 'das', 'hud', 'fheo'
]

EXCLUDE_EXT = {'.js', '.css', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico', '.woff', '.woff2', '.ttf', '.map'}
KEEP_ALWAYS_DOMAINS = {
    'oregonbuys.gov',
    'sos.oregon.gov',
}
EXCLUDE_HOST_OR_PATH = [
    'myworkdayjobs.com', 'career', 'jobs', 'govdelivery.com', 'subscribers', 'employeesearch.dasapp.oregon.gov'
]

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Research Assistant)'})

def classify_url(url: str) -> tuple[bool, str]:
    parsed = urlparse(url)
    path = parsed.path.lower()
    host = parsed.netloc.lower()
    ext = Path(path).suffix
    if ext in EXCLUDE_EXT:
        return False, f"excluded_ext:{ext or 'none'}"

    # Explicit allow-list for high-value context domains
    if host in KEEP_ALWAYS_DOMAINS:
        return True, "kept_always_domain"

    if any(term in host or term in path for term in EXCLUDE_HOST_OR_PATH):
        return False, "excluded_host_or_path"
    if ext in EXT_KEEP:
        return True, f"kept_extension:{ext}"
    text = f"{host}{path}{parsed.query}".lower()
    if any(k in text for k in KEYWORDS):
        return True, "keyword_match"
    return False, "no_keyword_match"


def is_relevant(url: str) -> bool:
    keep, _reason = classify_url(url)
    return keep


def download(url: str, dest: Path, retries: int = 2) -> bool:
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=20, allow_redirects=True)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            return True
        except Exception as e:
            logger.warning(f"Download failed ({attempt+1}/{retries}) for {url}: {e}")
            time.sleep(1.5 ** attempt)
    return False


def main():
    if not SOURCE_JSON.exists():
        logger.error(f"Source JSON not found: {SOURCE_JSON}")
        return
    data = json.loads(SOURCE_JSON.read_text())
    filtered = []
    audit_counts = Counter()
    excluded_by_reason: dict[str, list[str]] = {}
    domain_counts = Counter()
    total_urls = 0
    kept_urls = 0
    for item in data.get('results', []):
        urls = item.get('urls', [])
        kept: list[str] = []
        for url in urls:
            total_urls += 1
            parsed = urlparse(url)
            domain_counts[parsed.netloc.lower()] += 1
            keep, reason = classify_url(url)
            audit_counts[reason] += 1
            if keep:
                kept_urls += 1
                kept.append(url)
            else:
                # Cap per-reason examples so audit output stays readable
                bucket = excluded_by_reason.setdefault(reason, [])
                if len(bucket) < 200:
                    bucket.append(url)
        if kept:
            filtered.append({
                'file': item.get('file', ''),
                'name': item.get('name', ''),
                'url_count': len(kept),
                'urls': kept
            })
    OUTPUT_JSON.write_text(json.dumps({'filtered_files': len(filtered), 'items': filtered}, indent=2))
    logger.info(f"Filtered results saved to {OUTPUT_JSON}")

    audit = {
        'source_json': str(SOURCE_JSON),
        'total_urls': total_urls,
        'kept_urls': kept_urls,
        'kept_pct': round((kept_urls / total_urls) * 100, 2) if total_urls else 0.0,
        'counts_by_reason': dict(audit_counts.most_common()),
        'top_domains': dict(domain_counts.most_common(30)),
        'excluded_examples_by_reason': excluded_by_reason,
    }
    AUDIT_JSON.write_text(json.dumps(audit, indent=2))
    logger.info(f"Audit report saved to {AUDIT_JSON}")

    # Download
    downloaded = 0
    for item in filtered:
        for url in item['urls']:
            parsed = urlparse(url)
            name = Path(parsed.path).name or "downloaded_file"
            if not Path(name).suffix:
                name = name + '.html'
            dest = DOWNLOAD_DIR / name
            if dest.exists():
                continue
            ok = download(url, dest)
            if ok:
                downloaded += 1
    logger.info(f"Downloaded {downloaded} files to {DOWNLOAD_DIR}")

if __name__ == "__main__":
    main()
