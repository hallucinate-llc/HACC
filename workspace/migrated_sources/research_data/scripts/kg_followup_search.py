#!/usr/bin/env python3
"""Use the audit knowledge graph to drive follow-up discovery searches via the shared HACC engine."""

from __future__ import annotations

import csv
import json
import os
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_research import HACCResearchEngine


KG_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"
AUDIT_CSV = "research_results/audit_policy_reviews_20251231.csv"

OUT_MD = "research_results/kg_followup_discovery_20251231.md"
OUT_CSV = "research_results/kg_followup_discovery_20251231.csv"
OUT_QUEUE = "research_results/kg_followup_query_queue_20251231.txt"

MAX_ENTITY_LABEL_LEN = 80
MAX_ENTITIES = 60
MAX_TOTAL_HITS = 2500
WS_RE = re.compile(r"\s+")


def normalize(s: str) -> str:
    return WS_RE.sub(" ", s or "").strip()


def load_kg() -> dict[str, Any]:
    with open(KG_JSON, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_audit_map() -> dict[str, dict[str, str]]:
    if not os.path.exists(AUDIT_CSV):
        return {}
    out: dict[str, dict[str, str]] = {}
    with open(AUDIT_CSV, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            did = row.get("document_id") or ""
            if not did:
                continue
            out[did] = {
                "assessment": row.get("assessment") or "",
                "classification": row.get("classification") or "",
                "domain": row.get("domain") or "",
                "url": row.get("url") or "",
            }
    return out


def compute_entity_centrality(kg: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], Counter[str]]:
    nodes_by_id = {node["id"]: node for node in kg.get("nodes", []) if isinstance(node, dict) and node.get("id")}
    mentions_weight = Counter()
    for edge in kg.get("edges", []):
        if not isinstance(edge, dict):
            continue
        if edge.get("type") != "MENTIONS":
            continue
        dst = edge.get("target") or ""
        if dst.startswith("ent:"):
            mentions_weight[dst] += int(edge.get("weight") or 1)
    return nodes_by_id, mentions_weight


def entity_ok(label: str) -> bool:
    if not label:
        return False
    if len(label) > MAX_ENTITY_LABEL_LEN:
        return False
    low = label.lower()
    if low in {"percentage of", "average for", "requirement to", "respond to the"}:
        return False
    if re.fullmatch(r"[a-z]+", label):
        return False
    if re.fullmatch(r"[A-Z]{2,}", label) and len(label) >= 8:
        return False
    return True


def build_query_queue(entities: list[str]) -> list[str]:
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
    for entity in entities:
        ent_q = f'"{entity}"' if " " in entity else entity
        for site in sites:
            for term_block in term_blocks:
                out.append(f"{site} {ent_q} {term_block}")
    seen = set()
    final = []
    for query in out:
        if query in seen:
            continue
        seen.add(query)
        final.append(query)
    return final


def main() -> None:
    if not os.path.exists(KG_JSON):
        raise SystemExit(f"missing {KG_JSON}")

    kg = load_kg()
    audit_map = load_audit_map()
    nodes_by_id, mentions = compute_entity_centrality(kg)
    engine = HACCResearchEngine(repo_root=REPO_ROOT)

    ranked = []
    for ent_id, weight in mentions.most_common(500):
        node = nodes_by_id.get(ent_id)
        if not node:
            continue
        label = node.get("label") or ""
        if not entity_ok(label):
            continue
        ranked.append((ent_id, label, node.get("type") or "entity", weight))

    seen_labels = set()
    top_entities: list[tuple[str, str, str, int]] = []
    for ent_id, label, entity_type, weight in ranked:
        if label.lower() in seen_labels:
            continue
        seen_labels.add(label.lower())
        top_entities.append((ent_id, label, entity_type, weight))
        if len(top_entities) >= MAX_ENTITIES:
            break

    all_hits: list[dict[str, str]] = []
    for _ent_id, label, entity_type, weight in top_entities:
        if entity_type not in ("government_body", "policy_or_law", "program", "organization"):
            continue
        search_payload = engine.search(label, top_k=5, search_mode="package")
        for result in search_payload.get("results", []):
            document_id = str(result.get("document_id") or "")
            audit = audit_map.get(document_id, {})
            all_hits.append(
                {
                    "entity": label,
                    "entity_type": entity_type,
                    "entity_weight": str(weight),
                    "term": "(engine-match)",
                    "file": str(result.get("source_path") or ""),
                    "document_id": document_id,
                    "doc_assessment": audit.get("assessment", ""),
                    "doc_classification": audit.get("classification", ""),
                    "doc_domain": audit.get("domain", ""),
                    "doc_url": audit.get("url", ""),
                    "snippet": normalize(str(result.get("snippet") or "")),
                }
            )
            if len(all_hits) >= MAX_TOTAL_HITS:
                break
        if len(all_hits) >= MAX_TOTAL_HITS:
            break

    all_hits.sort(key=lambda hit: int(hit.get("entity_weight") or 0), reverse=True)

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
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for hit in all_hits:
            writer.writerow({key: hit.get(key, "") for key in fieldnames})

    query_entities = [label for _eid, label, entity_type, _weight in top_entities if entity_type in ("government_body", "policy_or_law", "program", "organization")]
    queries = build_query_queue(query_entities[:25])
    with open(OUT_QUEUE, "w", encoding="utf-8") as handle:
        for query in queries[:600]:
            handle.write(query + "\n")

    md = [
        "# KG-driven follow-up discovery",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Inputs",
        f"- Knowledge graph: {KG_JSON}",
        f"- Audit review CSV: {AUDIT_CSV}",
        "",
        "## Top entities (by mentions weight)",
    ]
    for _ent_id, label, entity_type, weight in top_entities[:30]:
        md.append(f"- {label} ({entity_type}) weight={weight}")
    md.extend(
        [
            "",
            "## Follow-up hit summary",
            f"- Shared engine corpus searched: {len(engine.load_corpus())}",
            f"- Hits written: {len(all_hits)}",
            "",
            "## High-signal hits (top 60)",
            "",
        ]
    )
    for hit in all_hits[:60]:
        md.append(f"### {hit.get('entity')} + {hit.get('term')}")
        if hit.get("document_id"):
            md.append(f"- document_id: {hit.get('document_id')}")
        if hit.get("doc_assessment"):
            md.append(f"- doc_assessment: {hit.get('doc_assessment')}")
        if hit.get("file"):
            md.append(f"- file: {hit.get('file')}")
        if hit.get("snippet"):
            md.append(f"- snippet: {hit.get('snippet')}")
        md.append("")
    md.append("## Web query queue")
    md.append(f"- Wrote: {OUT_QUEUE} (first {min(600, len(queries))} queries)")

    with open(OUT_MD, "w", encoding="utf-8") as handle:
        handle.write("\n".join(md))

    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("wrote", OUT_QUEUE)
    print("hits", len(all_hits))


if __name__ == "__main__":
    main()
