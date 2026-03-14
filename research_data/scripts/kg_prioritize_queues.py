#!/usr/bin/env python3
"""Prioritize existing URL queues using knowledge-graph entities + audit terms.

This does not fetch anything. It produces a smaller, ranked queue you can feed into
whatever downloader/collector you already use.

Inputs:
- research_results/audit_policy_knowledge_graph_20251231.json
- One or more existing queue files (JSON) in research_results/ (third-party queues, quantum queues, etc.)

Outputs:
- research_results/kg_prioritized_download_queue_20251231.json
- research_results/kg_prioritized_download_queue_20251231.csv

Scoring (simple):
- +5 if URL contains a high-value entity token (agency/program/law/vendor)
- +3 if URL contains an audit keyword (nondiscrimination, retaliation, procurement, etc.)
- +1 if domain matches government (.gov, hudexchange, clackamas.us, oregon.gov)

"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kg_violation_seed_queries as violation_seed_queries

KG_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"

QUEUE_GLOBS = [
    "research_results/*queue*.json",
    "research_results/*_links.json",
]

OUT_JSON = "research_results/kg_prioritized_download_queue_20251231.json"
OUT_CSV = "research_results/kg_prioritized_download_queue_20251231.csv"

AUDIT_URL_KEYWORDS = [
    "nondiscrimination",
    "non-discrimination",
    "anti-retaliation",
    "retaliation",
    "whistleblower",
    "procurement",
    "contract",
    "contracts",
    "contracting",
    "rfp",
    "rfq",
    "bid",
    "solicitation",
    "subaward",
    "subgrant",
    "mwbe",
    "dbe",
    "cobid",
    "civil-rights",
    "fair-housing",
    "affirmatively-furthering-fair-housing",
    "complaint",
    "grievance",
    "policy",
    "policies",
    "handbook",
]

GOV_DOMAIN_HINTS = [
    ".gov",
    "oregon.gov",
    "clackamas.us",
    "hud.gov",
    "hudexchange.info",
]

# Exclude obvious non-document/media/social noise from queues.
DENY_DOMAIN_SUBSTRINGS = [
    "googlevideo.com",
    "youtube.com",
    "youtu.be",
    "tiktok.com",
    "facebook.com",
    "instagram.com",
    "twitter.com",
    "x.com",
    "linkedin.com",
]

DENY_URL_SUBSTRINGS = [
    "initplayback",
    "videoplayback",
    "/wp-json/oembed",
]

# When producing an audit-oriented download queue, prefer likely authoritative sources.
ALLOW_DOMAIN_SUBSTRINGS = [
    "clackamas.us",
    "oregon.gov",
    "state.or.us",
    "oregonlegislature.gov",
    "oregonbuys.gov",
    "hud.gov",
    "hudexchange.info",
    "quantumresidential.com",
    "paycomonline.net",
    "paycom.com",
]


def _tokenize_label(label: str) -> str:
    token = label.lower().strip()
    token = re.sub(r"[^a-z0-9]+", "-", token).strip("-")
    return token


def load_kg_entities() -> list[str]:
    kg_nodes = violation_seed_queries.load_kg_nodes(Path(KG_JSON))
    ranked = []
    for label, node in kg_nodes.items():
        entity_label = (node.get("label") or label).strip()
        entity_type = (node.get("type") or "entity").strip()
        if entity_type not in violation_seed_queries.ENTITY_TYPE_ALLOW:
            continue
        if not violation_seed_queries.entity_label_ok(entity_label):
            continue
        ranked.append(entity_label)

    tokens: list[str] = []
    seen = set()
    stop_tokens = {
        "get",
        "put",
        "post",
        "html",
        "json",
        "http",
        "https",
        "www",
        "iso",
        "utc",
        "fax",
        "rights",
        "reserved",
        "team",
        "member",
        "portal",
        "privacy",
        "policy",
    }
    for label in ranked:
        t = _tokenize_label(label)
        if len(t) < 4:
            continue
        if t in stop_tokens:
            continue
        if t in seen:
            continue
        seen.add(t)
        tokens.append(t)
        if len(tokens) >= 120:
            break

    # Add a few hard-coded high-value tokens that might not survive OCR cleanly
    for t in ["ohcs", "orca", "oar", "ors", "boli", "hacc", "housingauthority", "oregonbuys"]:
        if t not in seen:
            tokens.append(t)
            seen.add(t)

    return tokens


def extract_urls(obj: Any) -> list[str]:
    urls: list[str] = []
    if isinstance(obj, str):
        if obj.startswith("http://") or obj.startswith("https://"):
            urls.append(obj)
        return urls

    if isinstance(obj, list):
        for it in obj:
            urls.extend(extract_urls(it))
        return urls

    if isinstance(obj, dict):
        # common patterns
        for k in ("url", "urls", "seed_urls", "guessed_urls", "items"):
            if k in obj:
                urls.extend(extract_urls(obj[k]))
        # also walk shallowly to catch weird shapes
        for v in obj.values():
            if isinstance(v, (dict, list)):
                urls.extend(extract_urls(v))
        return urls

    return urls


def score_url(url: str, entity_tokens: list[str]) -> tuple[int, dict[str, Any]]:
    u = url.lower()
    # hard filters
    if any(d in u for d in DENY_DOMAIN_SUBSTRINGS):
        return 0, {"entity_hits": [], "keyword_hits": [], "gov_hint": False}
    if any(s in u for s in DENY_URL_SUBSTRINGS):
        return 0, {"entity_hits": [], "keyword_hits": [], "gov_hint": False}

    # allowlist filter: keep only likely audit-relevant domains.
    if not any(a in u for a in ALLOW_DOMAIN_SUBSTRINGS):
        return 0, {"entity_hits": [], "keyword_hits": [], "gov_hint": False}

    score = 0
    reasons: dict[str, Any] = {"entity_hits": [], "keyword_hits": [], "gov_hint": False}

    for kw in AUDIT_URL_KEYWORDS:
        if kw in u:
            score += 3
            if len(reasons["keyword_hits"]) < 6:
                reasons["keyword_hits"].append(kw)

    for tok in entity_tokens:
        if tok and tok in u:
            score += 5
            if len(reasons["entity_hits"]) < 6:
                reasons["entity_hits"].append(tok)

    if any(h in u for h in GOV_DOMAIN_HINTS):
        score += 1
        reasons["gov_hint"] = True

    return score, reasons


def main() -> None:
    if not os.path.exists(KG_JSON):
        raise SystemExit(f"missing {KG_JSON}")

    entity_tokens = load_kg_entities()

    queue_files: list[str] = []
    for g in QUEUE_GLOBS:
        queue_files.extend(glob.glob(g))
    queue_files = sorted(set(queue_files))

    all_urls: list[tuple[str, str]] = []  # (source_file, url)

    for path in queue_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                obj = json.load(f)
        except Exception:
            continue
        urls = extract_urls(obj)
        for u in urls:
            all_urls.append((path, u))

    # de-dupe by URL keeping first source
    seen = set()
    dedup: list[tuple[str, str]] = []
    for src, u in all_urls:
        if u in seen:
            continue
        seen.add(u)
        dedup.append((src, u))

    scored = []
    for src, u in dedup:
        s, reasons = score_url(u, entity_tokens)
        if s <= 0:
            continue
        scored.append({"score": s, "url": u, "source": src, **reasons})

    scored.sort(key=lambda r: int(r.get("score") or 0), reverse=True)

    # write JSON
    out_obj = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "inputs": {"kg": KG_JSON, "queue_globs": QUEUE_GLOBS},
        "entity_tokens_used": entity_tokens[:80],
        "items": scored[:2000],
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(out_obj, f, ensure_ascii=False, indent=2)

    # write CSV
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=["score", "url", "source", "gov_hint", "entity_hits", "keyword_hits"],
        )
        w.writeheader()
        for r in scored[:2000]:
            w.writerow(
                {
                    "score": r.get("score"),
                    "url": r.get("url"),
                    "source": r.get("source"),
                    "gov_hint": r.get("gov_hint"),
                    "entity_hits": ";".join(r.get("entity_hits") or []),
                    "keyword_hits": ";".join(r.get("keyword_hits") or []),
                }
            )

    print("queue files scanned", len(queue_files))
    print("unique urls", len(dedup))
    print("scored urls", len(scored))
    print("wrote", OUT_JSON)
    print("wrote", OUT_CSV)


if __name__ == "__main__":
    main()
