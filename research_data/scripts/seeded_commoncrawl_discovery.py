#!/usr/bin/env python3
"""Seeded discovery using CommonCrawl + query-derived keywords.

Why this exists:
- DuckDuckGo HTML sometimes returns interstitials / 202 homepage responses that produce 0
  parseable results.
- CommonCrawl can reliably enumerate URLs for a domain; we can then *rank* URLs using
  query-derived terms and fetch a limited number of top candidates.

Input:
- A seeded queries file (one query per line). We extract:
  - `site:` domains
  - quoted phrases + remaining tokens (as keyword terms)

Output (timestamped under research_results/):
- seeded_commoncrawl_candidates_<ts>.json : ranked URL candidates per site
- seeded_commoncrawl_fetch_<ts>.json      : fetched page text matches (optional)

This script does network access (CommonCrawl + optional HTTP GET for pages).
"""

from __future__ import annotations

import argparse
import json
import re
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


@dataclass(frozen=True)
class QuerySpec:
    sites: list[str]
    phrases: list[str]
    tokens: list[str]


def normalize_site(site: str) -> str:
    s = (site or "").strip().lower()
    s = re.sub(r"^https?://", "", s)
    s = s.split("/", 1)[0]
    if s.startswith("www."):
        s = s[4:]
    return s


def parse_query(q: str) -> QuerySpec:
    qn = re.sub(r"\s+", " ", (q or "").strip())
    sites = [normalize_site(s) for s in re.findall(r"\bsite:([^\s)]+)", qn, flags=re.I)]
    phrases = [p.strip() for p in re.findall(r"\"([^\"]+)\"", qn) if p.strip()]

    # Remove quoted phrases for tokenization
    q2 = re.sub(r"\"[^\"]+\"", " ", qn)
    q2 = re.sub(r"\([^)]*\)", " ", q2)
    raw = [t for t in re.split(r"\s+", q2) if t]

    drop = {
        "or",
        "and",
        "policy",
        "rule",
        "statute",
        "complaint",
        "nondiscrimination",
    }
    tokens: list[str] = []
    for t in raw:
        tl = t.lower()
        if tl.startswith("site:"):
            continue
        if tl in drop:
            continue
        if not re.search(r"[a-z0-9]", tl):
            continue
        if len(t) <= 2 and tl not in {"vi", "ii"}:
            continue
        tokens.append(t)

    # de-dupe tokens while preserving order
    seen: set[str] = set()
    out_tokens: list[str] = []
    for t in tokens:
        tl = t.lower()
        if tl in seen:
            continue
        seen.add(tl)
        out_tokens.append(t)

    return QuerySpec(sites=[s for s in sites if s], phrases=phrases, tokens=out_tokens)


def load_queries(path: Path) -> list[str]:
    queries: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        queries.append(s)
    return queries


def commoncrawl_latest_index(session: requests.Session) -> str:
    r = session.get("https://index.commoncrawl.org/collinfo.json", timeout=30)
    r.raise_for_status()
    indexes = r.json()
    if not indexes:
        raise RuntimeError("CommonCrawl collinfo.json returned no indexes")
    return indexes[0]["cdx-api"]


def commoncrawl_list_urls(session: requests.Session, cdx_api: str, site: str, limit: int) -> list[dict[str, Any]]:
    # CommonCrawl CDX supports url=<pattern>
    params = {"url": f"{site}/*", "output": "json", "limit": int(limit)}
    r = session.get(cdx_api, params=params, timeout=60)
    r.raise_for_status()

    out: list[dict[str, Any]] = []
    for line in (r.text or "").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def score_url(url: str, terms: list[str]) -> int:
    u = (url or "").lower()
    score = 0
    for term in terms:
        tl = term.lower()
        if not tl:
            continue
        if tl in u:
            score += 3
        else:
            # token-by-token contains for multiword phrases
            parts = [p for p in re.split(r"\s+", tl) if p]
            if len(parts) > 1 and all(p in u for p in parts):
                score += 2
    return score


def fetch_text(session: requests.Session, url: str) -> str:
    r = session.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
    r.raise_for_status()
    # rough HTML-to-text stripping
    html = r.text or ""
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def main() -> None:
    ap = argparse.ArgumentParser(description="Seeded CommonCrawl discovery using query-derived keyword terms")
    ap.add_argument("--queries-file", required=True, help="Path to seeded queries file")
    ap.add_argument("--cc-limit", type=int, default=1000, help="Max CommonCrawl URLs per site (default: 1000)")
    ap.add_argument("--top-per-site", type=int, default=50, help="How many top-scored URLs per site to keep")
    ap.add_argument("--fetch-top", type=int, default=0, help="If >0, fetch text for this many top URLs per site")
    ap.add_argument("--sleep", type=float, default=0.5, help="Delay between network calls (default: 0.5s)")
    args = ap.parse_args()

    qpath = Path(args.queries_file)
    if not qpath.exists():
        raise SystemExit(f"missing queries file: {qpath}")

    queries = load_queries(qpath)
    specs = [parse_query(q) for q in queries]

    site_terms: dict[str, list[str]] = defaultdict(list)
    for spec in specs:
        terms = []
        terms.extend(spec.phrases)
        terms.extend(spec.tokens)
        # keep this short and focused
        terms = [t for t in terms if t and len(t) <= 60]
        for site in spec.sites:
            if not site:
                continue
            site_terms[site].extend(terms)

    # de-dupe terms per site
    for site, terms in list(site_terms.items()):
        seen: set[str] = set()
        out: list[str] = []
        for t in terms:
            k = t.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(t)
        site_terms[site] = out[:200]

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = Path("research_results")
    out_dir.mkdir(exist_ok=True)

    session = requests.Session()
    cdx_api = commoncrawl_latest_index(session)

    candidates: dict[str, Any] = {"generated": datetime.now().isoformat(timespec="seconds"), "cdx_api": cdx_api, "sites": {}}

    for site, terms in sorted(site_terms.items()):
        if not site:
            continue
        time.sleep(args.sleep)
        rows = commoncrawl_list_urls(session, cdx_api, site, limit=args.cc_limit)
        scored = []
        for row in rows:
            url = row.get("url") or ""
            s = score_url(url, terms)
            if s <= 0:
                continue
            scored.append({
                "url": url,
                "score": s,
                "timestamp": row.get("timestamp"),
                "mime": row.get("mime"),
                "status": row.get("status"),
            })
        scored.sort(key=lambda d: (d["score"], d.get("url", "")), reverse=True)
        candidates["sites"][site] = {
            "terms": terms[:50],
            "total_cc_rows": len(rows),
            "scored_rows": len(scored),
            "top": scored[: args.top_per_site],
        }

    out_candidates = out_dir / f"seeded_commoncrawl_candidates_{ts}.json"
    out_candidates.write_text(json.dumps(candidates, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", out_candidates)

    if args.fetch_top > 0:
        fetched: dict[str, Any] = {"generated": datetime.now().isoformat(timespec="seconds"), "sites": {}}
        for site, info in candidates["sites"].items():
            top = info.get("top") or []
            fetched_rows = []
            for item in top[: args.fetch_top]:
                url = item.get("url")
                if not url:
                    continue
                try:
                    time.sleep(args.sleep)
                    text = fetch_text(session, url)
                except Exception as e:
                    fetched_rows.append({"url": url, "error": str(e)})
                    continue

                # simple term hit counts
                terms = info.get("terms") or []
                hits = []
                tlow = text.lower()
                for t in terms[:50]:
                    if t.lower() in tlow:
                        hits.append(t)
                fetched_rows.append({"url": url, "hits": hits[:25], "text_snippet": text[:500]})

            fetched["sites"][site] = {
                "requested": args.fetch_top,
                "fetched": len(fetched_rows),
                "rows": fetched_rows,
            }

        out_fetch = out_dir / f"seeded_commoncrawl_fetch_{ts}.json"
        out_fetch.write_text(json.dumps(fetched, ensure_ascii=False, indent=2), encoding="utf-8")
        print("wrote", out_fetch)


if __name__ == "__main__":
    main()
