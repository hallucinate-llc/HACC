#!/usr/bin/env python3
"""Use the audit knowledge graph to drive follow-up discovery searches.

What this does (offline / within current workspace artifacts):
- Computes the most central entities in the knowledge graph (by MENTIONS edge weight).
- Builds an audit-focused query list for future web searches (Brave/Google/CC).
- Searches existing local corpora for additional evidence and co-occurrence:
  - research_results/documents/parsed/*.txt
  - raw_documents/**/* (html/txt)
  - research_results/*search_results*.json and *commoncrawl_results*.json

Outputs:
- research_results/kg_followup_discovery_20251231.md
- research_results/kg_followup_discovery_20251231.csv
- research_results/kg_followup_query_queue_20251231.txt

Note: This script does not hit the network; it prepares targets and mines what we already have.
"""

from __future__ import annotations

import csv
import glob
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

KG_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"
AUDIT_CSV = "research_results/audit_policy_reviews_20251231.csv"

OUT_MD = "research_results/kg_followup_discovery_20251231.md"
OUT_CSV = "research_results/kg_followup_discovery_20251231.csv"
OUT_QUEUE = "research_results/kg_followup_query_queue_20251231.txt"

SEARCH_JSON_GLOBS = [
    "research_results/search_results_*.json",
    "research_results/commoncrawl_results_*.json",
    "research_results/*_links.json",
    "research_results/*_queue.json",
    "research_results/*_evidence.json",
]

LOCAL_TEXT_GLOBS = [
    "research_results/documents/parsed/*.txt",
    "raw_documents/**/*.txt",
    "raw_documents/**/*.html",
]

MAX_ENTITY_LABEL_LEN = 80
MAX_ENTITIES = 60
MAX_HITS_PER_ENTITY = 25
MAX_TOTAL_HITS = 2500

WS_RE = re.compile(r"\s+")

AUDIT_TERMS = [
    # direct red flags
    "diverse slate",
    "quota",
    "diversity quota",
    "BIPOC-only",
    "minority-only",
    "women-only",
    "women-owned",
    "minority-owned",
    "MWBE",
    "DBE",
    "set-aside",
    "tie-break",
    "tiebreak",
    "cultural competence",
    "lived experience",
    "equity lens",
    "equity framework",
    "safe space",
    "privilege",
    "oppressive",
    "anti-retaliation",
    "retaliation",
    "whistleblower",
    "nondiscrimination",
    "nondiscrimination clause",
    "monitoring",
    "corrective action",
    "termination",
    # audit areas
    "procurement",
    "contract",
    "agreement",
    "subaward",
    "subgrant",
    "RFP",
    "RFQ",
    "bid",
    "solicitation",
    "scoring rubric",
]


def normalize(s: str) -> str:
    return WS_RE.sub(" ", s or "").strip()


def read_text(path: str, limit_chars: int = 300_000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit_chars)
    except Exception:
        return ""


def iter_local_files() -> list[str]:
    files: list[str] = []
    for g in LOCAL_TEXT_GLOBS:
        files.extend(glob.glob(g, recursive=True))
    # de-dupe and keep stable-ish order
    return sorted(set(files))


def iter_json_files() -> list[str]:
    files: list[str] = []
    for g in SEARCH_JSON_GLOBS:
        files.extend(glob.glob(g))
    return sorted(set(files))


def best_snippet(text: str, needle: str, window: int = 220) -> str:
    low = text.lower()
    nlow = needle.lower()
    idx = low.find(nlow)
    if idx == -1:
        return ""
    start = max(0, idx - window)
    end = min(len(text), idx + len(needle) + window)
    return "…" + normalize(text[start:end]) + "…"


def load_kg() -> dict[str, Any]:
    with open(KG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def load_audit_map() -> dict[str, dict[str, str]]:
    if not os.path.exists(AUDIT_CSV):
        return {}
    out: dict[str, dict[str, str]] = {}
    with open(AUDIT_CSV, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            did = r.get("document_id") or ""
            if not did:
                continue
            out[did] = {
                "assessment": r.get("assessment") or "",
                "classification": r.get("classification") or "",
                "domain": r.get("domain") or "",
                "url": r.get("url") or "",
            }
    return out


def compute_entity_centrality(kg: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    nodes_by_id = {n["id"]: n for n in kg.get("nodes", []) if isinstance(n, dict) and n.get("id")}
    mentions_weight = Counter()

    for e in kg.get("edges", []):
        if not isinstance(e, dict):
            continue
        if e.get("type") != "MENTIONS":
            continue
        src = e.get("source") or ""
        dst = e.get("target") or ""
        if not src.startswith("doc:"):
            continue
        if not dst.startswith("ent:"):
            continue
        w = int(e.get("weight") or 1)
        mentions_weight[dst] += w

    return nodes_by_id, mentions_weight


def entity_ok(label: str) -> bool:
    if not label:
        return False
    if len(label) > MAX_ENTITY_LABEL_LEN:
        return False
    low = label.lower()
    # filter generic tokens that show up a ton in OCR
    if low in {"percentage of", "average for", "requirement to", "respond to the"}:
        return False
    if re.fullmatch(r"[a-z]+", label):
        return False
    if re.fullmatch(r"[A-Z]{2,}", label) and len(label) >= 8:
        return False
    return True


def build_query_queue(entities: list[str]) -> list[str]:
    # site-restricted queries aligned with agent.md scope
    sites = [
        "site:clackamas.us",
        "site:oregon.gov",
        "site:state.or.us",
        "site:oregonlegislature.gov",
        "site:hud.gov",
        "site:hudexchange.info",
    ]

    term_blocks = [
        '("nondiscrimination" OR "nondiscrimination clause" OR retaliation OR "anti-retaliation")',
        '(procurement OR contracting OR contract OR RFP OR RFQ OR bid OR solicitation OR subaward OR subgrant)',
        '("cultural competence" OR "lived experience" OR "equity lens" OR "diverse slate" OR quota OR "BIPOC-only" OR "women-owned" OR "minority-owned" OR MWBE OR DBE)',
    ]

    out: list[str] = []
    for ent in entities:
        # include entity as quoted phrase if it has spaces
        ent_q = f'"{ent}"' if " " in ent else ent
        for s in sites:
            for tb in term_blocks:
                out.append(f"{s} {ent_q} {tb}")
    # de-dupe while preserving order
    seen = set()
    final = []
    for q in out:
        if q in seen:
            continue
        seen.add(q)
        final.append(q)
    return final


def scan_local_for_entity_and_terms(entity: str, files: list[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    for path in files:
        text = read_text(path)
        if not text:
            continue
        low = text.lower()
        if entity.lower() not in low:
            continue

        matched_any = False
        for t in AUDIT_TERMS:
            if t.lower() in low:
                matched_any = True
                snip = best_snippet(text, t)
                hits.append(
                    {
                        "entity": entity,
                        "term": t,
                        "file": path,
                        "snippet": snip,
                    }
                )
                if len(hits) >= MAX_HITS_PER_ENTITY:
                    break
        if matched_any and len(hits) >= MAX_HITS_PER_ENTITY:
            break

    return hits


def scan_json_for_entity(entity: str, json_files: list[str]) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    needle = entity.lower()
    for path in json_files:
        raw = read_text(path, limit_chars=1_200_000)
        if not raw:
            continue
        if needle not in raw.lower():
            continue

        # Try to extract URLs if present
        urls = re.findall(r"https?://[^\s\"\)\]]+", raw)
        urls = list(dict.fromkeys(urls))[:30]
        hits.append(
            {
                "entity": entity,
                "term": "(json-match)",
                "file": path,
                "snippet": " | ".join(urls[:8]) if urls else "entity string matched in JSON",
            }
        )
    return hits


def main() -> None:
    if not os.path.exists(KG_JSON):
        raise SystemExit(f"missing {KG_JSON}")

    kg = load_kg()
    audit_map = load_audit_map()

    nodes_by_id, mentions = compute_entity_centrality(kg)

    # pick top entities by mention weight, prefer more specific entity types
    ranked = []
    for ent_id, w in mentions.most_common(500):
        node = nodes_by_id.get(ent_id)
        if not node:
            continue
        label = node.get("label") or ""
        if not entity_ok(label):
            continue
        etype = node.get("type") or "entity"
        ranked.append((ent_id, label, etype, w))

    # de-dupe by label
    seen_labels = set()
    top_entities: list[tuple[str, str, str, int]] = []
    for ent_id, label, etype, w in ranked:
        if label.lower() in seen_labels:
            continue
        seen_labels.add(label.lower())
        top_entities.append((ent_id, label, etype, w))
        if len(top_entities) >= MAX_ENTITIES:
            break

    local_files = iter_local_files()
    json_files = iter_json_files()

    all_hits: list[dict[str, str]] = []

    for _ent_id, label, etype, w in top_entities:
        # prioritize government bodies / laws / programs
        if etype not in ("government_body", "policy_or_law", "program", "organization"):
            continue

        local_hits = scan_local_for_entity_and_terms(label, local_files)
        json_hits = scan_json_for_entity(label, json_files)

        for h in (local_hits + json_hits):
            h["entity_type"] = etype
            h["entity_weight"] = str(w)

            # attempt doc_id from parsed filename
            base = os.path.basename(h["file"])
            m = re.match(r"([0-9a-f]{32})\\.txt$", base)
            if m:
                did = m.group(1)
                h["document_id"] = did
                if did in audit_map:
                    h["doc_assessment"] = audit_map[did].get("assessment", "")
                    h["doc_classification"] = audit_map[did].get("classification", "")
                    h["doc_domain"] = audit_map[did].get("domain", "")
                    h["doc_url"] = audit_map[did].get("url", "")
            all_hits.append(h)

            if len(all_hits) >= MAX_TOTAL_HITS:
                break
        if len(all_hits) >= MAX_TOTAL_HITS:
            break

    # Sort hits: prioritize strong audit terms, then entity weight
    def term_priority(t: str) -> int:
        tl = t.lower()
        if tl in ("nondiscrimination", "nondiscrimination clause", "retaliation", "anti-retaliation"):
            return 3
        if tl in ("bipoc-only", "minority-only", "women-only", "diverse slate", "diversity quota", "quota"):
            return 2
        if tl in ("cultural competence", "lived experience", "equity lens", "equity framework"):
            return 2
        if tl == "(json-match)":
            return 0
        return 1

    all_hits.sort(
        key=lambda h: (
            term_priority(h.get("term", "")),
            int(h.get("entity_weight") or 0),
        ),
        reverse=True,
    )

    # CSV
    fieldnames = [
        "entity",
        "entity_type",
        "entity_weight",
        "term",
        "file",
        "document_id",
        "doc_assessment",
        "doc_classification",
        "doc_domain",
        "doc_url",
        "snippet",
    ]

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for h in all_hits:
            row = {k: h.get(k, "") for k in fieldnames}
            w.writerow(row)

    # Query queue (for future web searches)
    query_entities = [lbl for _eid, lbl, et, _w in top_entities if et in ("government_body", "policy_or_law", "program", "organization")]
    queries = build_query_queue(query_entities[:25])

    with open(OUT_QUEUE, "w", encoding="utf-8") as f:
        for q in queries[:600]:
            f.write(q + "\n")

    # Markdown report
    md: list[str] = []
    md.append("# KG-driven follow-up discovery")
    md.append("")
    md.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    md.append("")
    md.append("## Inputs")
    md.append(f"- Knowledge graph: {KG_JSON}")
    md.append(f"- Audit review CSV: {AUDIT_CSV}")
    md.append("")

    md.append("## Top entities (by mentions weight)")
    for ent_id, label, etype, w in top_entities[:30]:
        md.append(f"- {label} ({etype}) weight={w}")
    md.append("")

    md.append("## Follow-up hit summary")
    md.append(f"- Local text files scanned: {len(local_files)}")
    md.append(f"- JSON artifacts scanned: {len(json_files)}")
    md.append(f"- Hits written: {len(all_hits)}")
    md.append("")

    md.append("## High-signal hits (top 60)")
    md.append("")
    for h in all_hits[:60]:
        md.append(f"### {h.get('entity')} + {h.get('term')}")
        if h.get("document_id"):
            md.append(f"- document_id: {h.get('document_id')}")
        if h.get("doc_assessment"):
            md.append(f"- doc_assessment: {h.get('doc_assessment')}")
        if h.get("file"):
            md.append(f"- file: {h.get('file')}")
        if h.get("snippet"):
            md.append(f"- snippet: {h.get('snippet')}")
        md.append("")

    md.append("## Web query queue")
    md.append(f"- Wrote: {OUT_QUEUE} (first {min(600, len(queries))} queries)")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("wrote", OUT_QUEUE)
    print("hits", len(all_hits))


if __name__ == "__main__":
    main()
