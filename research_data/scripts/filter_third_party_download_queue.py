#!/usr/bin/env python3
"""filter_third_party_download_queue.py

Purpose
- Create a *tighter* download queue from an existing third-party queue by removing
  obvious social/media/CDN/tech-noise domains.

Inputs
- research_results/third_party_download_queue.json (default)

Outputs
- research_results/third_party_download_queue_filtered.json (default)
- research_results/third_party_download_queue_filtered_summary.json

This is a compliance-oriented workflow; it does not infer wrongdoing.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path


NOISE_DOMAIN_SUBSTR = [
    # Social / media
    "tiktok.com",
    "tiktokv.",
    "instagram.com",
    "facebook.com",
    "fbcdn.",
    "linkedin.com",
    "threads.net",
    "bsky.app",
    "twitter.com",
    "t.co",
    "twimg.com",
    "x.com",
    "youtu.be",
    "youtube.com",

    # Search / tracking / analytics
    "google.com",
    "gstatic.com",
    "googleusercontent.com",
    "googletagmanager",
    "google-analytics",
    "doubleclick.net",
    "googleapis.com",

    # Common embedded tech metadata
    "schema.org",
    "ogp.me",
    "rdfs.org",
    "gmpg.org",
    "xmlns.com",
    "w3.org",
    "api.w.org",
    "s.w.org",
    "wordpress.org",
    "wordpress.com",

    # CDNs / assets
    "cloudfront.net",
    "fastly.net",
    "akamai",
    "jsdelivr.net",
    "stripe.com",
    "learnworlds.com",
    "thrillshare.com",
    "mycourse.app",
    "mouseflow.com",
    "heapanalytics.com",
    "adobedtm.com",
    "licdn.com",
    "confiant-integrations.net",
    "slideshare.net",
    "bonfire.com",

    # News / media / UGC that tends to be low-signal for proxy org discovery
    "cbs8.com",
    "wnycstudios.org",
    "flickr.com",
    "wikimedia.org",
    "wikipedia.org",
    "cdn.",
    "static.",
    "assets.",

    # Shorteners / placeholders
    "tinyurl.com",
    "goo.gl",
    "bit.ly",
    "example.com",
]

# Keep specific portals if the user wants a mixed queue that includes key public portals.
DEFAULT_KEEP_DOMAINS = {
    "oregonbuys.gov",
    "sos.oregon.gov",
}


@dataclass(frozen=True)
class FilterDecision:
    keep: bool
    reason: str


def _norm_domain(d: str) -> str:
    return (d or "").strip().lower()


def is_govish(domain: str) -> bool:
    d = _norm_domain(domain)
    return d.endswith(".gov") or d.endswith(".us") or d.endswith(".state.or.us") or d.endswith(".oregon.gov")


def decide_keep(domain: str, *, keep_domains: set[str], keep_gov: bool) -> FilterDecision:
    d = _norm_domain(domain)
    if not d:
        return FilterDecision(False, "empty_domain")

    if d in keep_domains:
        return FilterDecision(True, "allowlist")

    if not keep_gov and is_govish(d):
        return FilterDecision(False, "gov_filtered")

    for s in NOISE_DOMAIN_SUBSTR:
        if s in d:
            return FilterDecision(False, f"noise:{s}")

    # Common asset-host patterns
    if d.startswith("www.") and any(x in d for x in ["static", "assets", "cdn"]):
        return FilterDecision(False, "asset_host_pattern")

    return FilterDecision(True, "ok")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--in",
        dest="in_path",
        default="research_results/third_party_download_queue.json",
        help="Input queue JSON to filter",
    )
    ap.add_argument(
        "--out",
        dest="out_path",
        default="research_results/third_party_download_queue_next_hop.json",
        help="Output filtered queue JSON",
    )
    ap.add_argument(
        "--summary",
        dest="summary_path",
        default="research_results/third_party_download_queue_next_hop_summary.json",
        help="Output filtering summary JSON",
    )
    ap.add_argument(
        "--min-score",
        type=int,
        default=50,
        help="Minimum queue item score to keep (default: 50)",
    )
    ap.add_argument(
        "--max-domains",
        type=int,
        default=150,
        help="Maximum number of domains to keep after filtering (default: 150)",
    )
    ap.add_argument(
        "--keep-gov",
        action="store_true",
        help="Keep .gov/.us domains (default: filter them out)",
    )
    ap.add_argument(
        "--keep-domain",
        action="append",
        default=[],
        help="Allowlist a domain even if it matches noise filters (repeatable)",
    )

    args = ap.parse_args()

    in_path = Path(args.in_path)
    out_path = Path(args.out_path)
    summary_path = Path(args.summary_path)

    if not in_path.exists():
        raise SystemExit(f"Missing input queue: {in_path}")

    data = json.loads(in_path.read_text(encoding="utf-8"))
    items = data.get("items", [])
    if not isinstance(items, list):
        raise SystemExit("Input queue JSON missing 'items' list")

    keep_domains = set(DEFAULT_KEEP_DOMAINS)
    for d in args.keep_domain:
        keep_domains.add(_norm_domain(d))

    kept = []
    dropped_by_reason: Counter[str] = Counter()
    dropped_examples: dict[str, list[str]] = defaultdict(list)

    for it in items:
        if not isinstance(it, dict):
            dropped_by_reason["bad_item"] += 1
            continue
        domain = it.get("domain", "")
        decision = decide_keep(domain, keep_domains=keep_domains, keep_gov=args.keep_gov)
        if decision.keep:
            score = int(it.get("score") or 0)
            if score < int(args.min_score):
                dropped_by_reason["score_below_min"] += 1
                if len(dropped_examples["score_below_min"]) < 10:
                    dropped_examples["score_below_min"].append(_norm_domain(domain))
                continue
            kept.append(it)
        else:
            dropped_by_reason[decision.reason] += 1
            if len(dropped_examples[decision.reason]) < 10:
                dropped_examples[decision.reason].append(_norm_domain(domain))

    # Sort + cap
    kept.sort(key=lambda x: int(x.get("score") or 0), reverse=True)
    kept = kept[: int(args.max_domains)]

    out = {
        "source": str(in_path),
        "domain_count": len(kept),
        "notes": "Filtered to reduce obvious social/media/CDN/tech-noise domains; verify relevance before crawling.",
        "filters": {
            "keep_gov": bool(args.keep_gov),
            "min_score": int(args.min_score),
            "max_domains": int(args.max_domains),
            "allowlist": sorted(keep_domains),
            "noise_domain_substr": NOISE_DOMAIN_SUBSTR,
        },
        "items": kept,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    summary = {
        "input": str(in_path),
        "input_domain_count": len(items),
        "output": str(out_path),
        "output_domain_count": len(kept),
        "dropped_domain_count": len(items) - len(kept),
        "dropped_by_reason": dict(dropped_by_reason.most_common()),
        "dropped_examples": dict(dropped_examples),
    }
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Wrote {out_path} ({len(kept)} domains)")
    print(f"Wrote {summary_path}")


if __name__ == "__main__":
    main()
