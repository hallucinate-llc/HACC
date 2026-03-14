#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""extract_third_party_candidates.py

Scan the existing local corpus (HACC + Oregon pages + parsed text) to identify
third-party organizations/domains that appear to be partners, contractors,
subrecipients, vendors, training providers, portals, or associations.

This is a *lead generation* tool for compliance due diligence. It does not
infer or assert wrongdoing.

Outputs:
- research_results/third_party_candidates.json
- research_results/third_party_candidates.csv

Notes:
- Uses lightweight heuristics (no ML / NER) to keep dependencies minimal.
- Keeps evidence: source file + small context snippets.
"""

from __future__ import annotations

import csv
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse, urldefrag

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

WORKSPACE_ROOT = Path(".")
OUTPUT_JSON = Path("research_results/third_party_candidates.json")
OUTPUT_CSV = Path("research_results/third_party_candidates.csv")

TEXT_FILE_EXTS = {".txt", ".md", ".html", ".htm", ".aspx"}

ASSET_EXTS = {".js", ".css", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".map"}

RELATIONSHIP_TERMS = [
    "partner", "partnership", "in partnership", "in coordination", "collaborat",
    "administered by", "managed by", "operated by", "run by",
    "contractor", "vendor", "consultant", "provider", "service provider",
    "subrecipient", "sub-recipient", "subaward", "sub-award", "pass-through",
    "grant agreement", "mou", "memorandum of understanding",
    "training vendor", "facilitated by", "curriculum",
    "application portal", "intake", "screening", "waitlist", "wait list",
]

ORG_SUFFIXES = [
    "Inc", "Incorporated", "LLC", "L.L.C", "Ltd", "Limited", "Co", "Company",
    "Corporation", "Corp", "Foundation", "Association", "Coalition", "Council",
    "Network", "Partners", "Partnership", "Services", "Service", "Center", "Centre",
    "Institute", "Initiative", "Alliance", "Agency", "Authority",
]

# Domain allowlist/ignore lists for scoring
IGNORE_DOMAINS_SUBSTR = [
    "google-analytics", "googletagmanager", "gtranslate", "fontawesome", "cloudflare",
    "cdnjs", "code.jquery.com", "ns.adobe.com", "w3.org", "purl.org", "siteimprove",
    "getsitecontrol", "bestvpn.org", "browsehappy.com", "fonts.googleapis.com",
    "fonts.gstatic.com", "gstatic.com", "facebook.com", "twitter.com", "instagram.com",
    "linkedin.com", "youtube.com", "youtu.be", "goo.gl", "t.co", "google.com",
    "berkeley.edu",

    # Common metadata/tech noise (not useful as "proxy org" leads)
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

KEEP_GOV_DOMAINS = {
    # keep a few gov domains that act as primary portals or policy sources
    "oregonbuys.gov",
    "sos.oregon.gov",
    "www.hud.gov",
    "hud.gov",
}

GOV_NAME_HINTS = [
    "department of", "state of", "oregon", "county", "housing authority", "bureau of", "division of",
    "administrative services", "secretary of state",
]


def is_asset_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except Exception:
        return True
    ext = Path(parsed.path.lower()).suffix
    return ext in ASSET_EXTS


def normalize_url(url: str) -> str:
    url = url.strip()
    url = url.replace("\x00", "")
    url = url.strip("\"'()[]{}<>.,;\n\r\t ")
    url, _frag = urldefrag(url)
    return url


def domain_of(url: str) -> str:
    try:
        dom = urlparse(url).netloc.lower()
        dom = dom.replace("\x00", "").strip()
        return dom
    except Exception:
        return ""


def is_government_domain(domain: str) -> bool:
    d = domain.lower()
    return d.endswith(".gov") or d.endswith(".us") or d.endswith(".state.or.us") or d.endswith(".oregon.gov")


def looks_like_ignored_domain(domain: str) -> bool:
    d = domain.lower()
    return any(s in d for s in IGNORE_DOMAINS_SUBSTR)


def normalize_whitespace(s: str) -> str:
    s = s.replace("\u00a0", " ")
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def org_name_is_noise(name: str) -> bool:
    n = normalize_whitespace(name)
    if len(n) < 6:
        return True
    if len(n) > 80:
        return True
    lowered = n.lower()
    if any(hint in lowered for hint in ["menu", "home", "address", "skip to", "explore", "search"]):
        return True
    return False


def org_name_is_gov_like(name: str) -> bool:
    lowered = normalize_whitespace(name).lower()
    return any(h in lowered for h in GOV_NAME_HINTS)


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self._chunks.append(data)

    def text(self) -> str:
        return " ".join(self._chunks)


URL_RE = re.compile(r"https?://[^\s\"'<>]+", re.IGNORECASE)


def extract_urls(raw: str) -> list[str]:
    urls = [normalize_url(u) for u in URL_RE.findall(raw)]
    # Deduplicate while preserving order
    seen = set()
    out = []
    for u in urls:
        if u and u not in seen:
            seen.add(u)
            out.append(u)
    return out


def extract_text_from_file(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="ignore")
    if path.suffix.lower() in {".html", ".htm", ".aspx"}:
        parser = TextExtractor()
        try:
            parser.feed(raw)
            return parser.text()
        except Exception:
            return raw
    return raw


def find_org_name_candidates(text: str) -> list[str]:
    # Heuristic: capitalized phrases ending with a common org suffix
    suffix_group = "|".join(re.escape(s) for s in ORG_SUFFIXES)
    pattern = re.compile(
        rf"\b([A-Z][A-Za-z&.,'\-]+(?:\s+[A-Z][A-Za-z&.,'\-]+){{0,6}}\s+(?:{suffix_group})\.?)\b"
    )
    candidates = pattern.findall(text)

    cleaned: list[str] = []
    for c in candidates:
        c = normalize_whitespace(c.strip().rstrip(",.;"))
        if org_name_is_noise(c):
            continue
        cleaned.append(c)

    # Deduplicate, preserve order
    seen = set()
    out = []
    for c in cleaned:
        key = c.lower()
        if key not in seen:
            seen.add(key)
            out.append(c)
    return out


def context_snippets(text: str, needle: str, window: int = 160, max_snips: int = 3) -> list[str]:
    out: list[str] = []
    t = text
    n = needle
    start = 0
    while len(out) < max_snips:
        idx = t.lower().find(n.lower(), start)
        if idx == -1:
            break
        left = max(0, idx - window)
        right = min(len(t), idx + len(n) + window)
        snippet = t[left:right].replace("\n", " ").replace("\r", " ")
        snippet = re.sub(r"\s+", " ", snippet).strip()
        out.append(snippet)
        start = idx + len(n)
    return out


def relationship_score(text_lower: str) -> int:
    # rough signal: count distinct relationship terms present
    found = 0
    for term in RELATIONSHIP_TERMS:
        if term in text_lower:
            found += 1
    return found


@dataclass
class Candidate:
    candidate_type: str  # domain | org_name
    candidate: str
    domain: str
    score: int
    mentions: int
    sources: list[str]
    evidence: list[dict]


def iter_corpus_files() -> Iterable[Path]:
    roots = [
        Path("research_results/hacc_documents"),
        Path("research_results/oregon_documents"),
        Path("research_results/oregon_p1p2_downloads"),
        Path("research_results/third_party_downloads"),
        Path("research_results/documents/parsed"),
        Path("raw_documents"),
    ]

    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix.lower() in TEXT_FILE_EXTS or path.suffix == "":
                # Some saved pages may have no suffix; attempt to parse anyway.
                yield path


def main() -> None:
    domain_mentions: Counter[str] = Counter()
    domain_sources: defaultdict[str, set[str]] = defaultdict(set)
    domain_evidence: defaultdict[str, list[dict]] = defaultdict(list)

    name_mentions: Counter[str] = Counter()
    name_sources: defaultdict[str, set[str]] = defaultdict(set)
    name_evidence: defaultdict[str, list[dict]] = defaultdict(list)

    processed = 0
    for path in iter_corpus_files():
        try:
            text_raw = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue

        urls = extract_urls(text_raw)
        processed += 1

        # For scoring relationship context, use rendered text (HTML stripped).
        text = extract_text_from_file(path)
        text_lower = text.lower()
        rel_sig = relationship_score(text_lower)

        # Domains from URLs
        for url in urls:
            if not url.lower().startswith(("http://", "https://")):
                continue
            if is_asset_url(url):
                continue
            dom = domain_of(url)
            if not dom:
                continue
            if looks_like_ignored_domain(dom):
                continue

            dom_key = dom
            domain_mentions[dom_key] += 1
            domain_sources[dom_key].add(str(path))

            # Evidence: include URL and a couple snippets around the domain string (if present)
            if len(domain_evidence[dom_key]) < 8:
                snips = context_snippets(text, dom, window=140, max_snips=2)
                domain_evidence[dom_key].append({
                    "source": str(path),
                    "url": url,
                    "relationship_signal_count": rel_sig,
                    "snippets": snips,
                })

        # Organization name candidates
        org_names = find_org_name_candidates(text)
        for name in org_names:
            key = name.lower()
            name_mentions[key] += 1
            name_sources[key].add(str(path))
            if len(name_evidence[key]) < 8:
                name_evidence[key].append({
                    "source": str(path),
                    "name": name,
                    "relationship_signal_count": rel_sig,
                    "snippets": context_snippets(text, name, window=160, max_snips=2),
                })

    logger.info(f"Scanned {processed} files")

    # Build candidates
    candidates: list[Candidate] = []

    # Domain candidates
    for dom, mentions in domain_mentions.most_common():
        srcs = sorted(domain_sources[dom])
        gov = is_government_domain(dom)

        # Drop noisy/asset/service domains; keep a few specific gov portals.
        if looks_like_ignored_domain(dom):
            continue
        if gov and dom not in KEEP_GOV_DOMAINS:
            continue

        score = 0
        score += min(mentions, 30)
        score += min(len(srcs) * 2, 40)
        if not gov:
            score += 10
        # Favor domains that appear in high-signal evidence
        score += sum(min(e.get("relationship_signal_count", 0), 5) for e in domain_evidence[dom])

        candidates.append(Candidate(
            candidate_type="domain",
            candidate=dom,
            domain=dom,
            score=score,
            mentions=mentions,
            sources=srcs[:50],
            evidence=domain_evidence[dom],
        ))

    # Name candidates
    for key, mentions in name_mentions.most_common():
        srcs = sorted(name_sources[key])
        display = name_evidence[key][0]["name"] if name_evidence[key] else key

        if org_name_is_noise(display):
            continue

        score = 0
        score += min(mentions, 20)
        score += min(len(srcs) * 2, 30)
        score += sum(min(e.get("relationship_signal_count", 0), 5) for e in name_evidence[key])

        # Deprioritize government-like names; still keep them as context leads.
        if org_name_is_gov_like(display):
            score -= 10

        candidates.append(Candidate(
            candidate_type="org_name",
            candidate=display,
            domain="",
            score=score,
            mentions=mentions,
            sources=srcs[:50],
            evidence=name_evidence[key],
        ))

    candidates.sort(key=lambda c: c.score, reverse=True)

    out = {
        "scanned_files": processed,
        "candidate_count": len(candidates),
        "notes": "Candidates are leads for due diligence; verify using source evidence.",
        "candidates": [asdict(c) for c in candidates],
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(out, indent=2), encoding="utf-8")

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["candidate_type", "candidate", "domain", "score", "mentions", "source_count", "sample_sources"])
        for c in candidates[:500]:
            w.writerow([
                c.candidate_type,
                c.candidate,
                c.domain,
                c.score,
                c.mentions,
                len(c.sources),
                " | ".join(c.sources[:5]),
            ])

    logger.info(f"Wrote {OUTPUT_JSON} and {OUTPUT_CSV}")


if __name__ == "__main__":
    main()
