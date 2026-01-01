#!/usr/bin/env python3
"""Generate KG-based seed data for follow-up searches.

This turns the knowledge graph into:
- a seed entity list (high-centrality entities)
- a set of query templates aligned to agent.md audit areas
- a ready-to-run query list (with site: restrictions)

It does not perform any network access.

Outputs:
- research_results/kg_seed_pack_20251231.json
- research_results/kg_seed_queries_20251231.txt

"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from datetime import datetime
from typing import Any

KG_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"
OUT_JSON = "research_results/kg_seed_pack_20251231.json"
OUT_TXT = "research_results/kg_seed_queries_20251231.txt"

# Default audit scope domains (from agent.md strategy)
SITES = [
    "clackamas.us",
    "www.clackamas.us",
    "oregon.gov",
    "www.oregon.gov",
    "state.or.us",
    "oregonlegislature.gov",
    "oregonbuys.gov",
    "hud.gov",
    "www.hud.gov",
    "hudexchange.info",
    "www.hudexchange.info",
    # vendor/partners
    "quantumresidential.com",
    "www.quantumresidential.com",
    "paycom.com",
    "paycomonline.net",
]

# Audit-aligned term blocks
TERM_BLOCKS = [
    {
        "name": "contracts_procurement",
        "terms": [
            "procurement",
            "contract",
            "contracting",
            "agreement",
            "RFP",
            "RFQ",
            "bid",
            "solicitation",
            "subaward",
            "subgrant",
            "monitoring",
            "nondiscrimination clause",
        ],
    },
    {
        "name": "proxies_equity",
        "terms": [
            "cultural competence",
            "lived experience",
            "equity lens",
            "equity framework",
            "diverse slate",
            "quota",
            "MWBE",
            "DBE",
            "COBID",
        ],
    },
    {
        "name": "complaints_retaliation",
        "terms": [
            "complaint",
            "grievance",
            "investigation",
            "anti-retaliation",
            "retaliation",
            "whistleblower",
        ],
    },
]

ENTITY_TYPE_ALLOW = {
    "government_body",
    "policy_or_law",
    "program",
    "organization",
    "entity",
}

STOP_LABELS = {
    "ISO",
    "GET",
    "POST",
    "HTML",
    "FAX",
    "All Rights Reserved",
    "Privacy Policy",
}


def load_kg() -> dict[str, Any]:
    with open(KG_JSON, "r", encoding="utf-8") as f:
        return json.load(f)


def entity_ok(label: str) -> bool:
    if not label:
        return False
    if label in STOP_LABELS:
        return False
    if len(label) > 80:
        return False
    if re.fullmatch(r"[A-Z]{2,}", label) and len(label) >= 8:
        return False
    return True


def compute_top_entities(kg: dict[str, Any], limit: int = 60) -> list[dict[str, Any]]:
    nodes = {n.get("id"): n for n in kg.get("nodes", []) if isinstance(n, dict) and n.get("id")}
    mentions = Counter()
    for e in kg.get("edges", []):
        if not isinstance(e, dict):
            continue
        if e.get("type") != "MENTIONS":
            continue
        dst = e.get("target") or ""
        if dst.startswith("ent:"):
            mentions[dst] += int(e.get("weight") or 1)

    ranked = []
    for ent_id, w in mentions.most_common(800):
        n = nodes.get(ent_id) or {}
        label = (n.get("label") or "").strip()
        et = (n.get("type") or "entity").strip()
        if et not in ENTITY_TYPE_ALLOW:
            continue
        if not entity_ok(label):
            continue
        ranked.append({"id": ent_id, "label": label, "type": et, "weight": w})

    # de-dupe by label
    out = []
    seen = set()
    for r in ranked:
        key = r["label"].lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(r)
        if len(out) >= limit:
            break
    return out


def build_queries(entities: list[dict[str, Any]]) -> list[str]:
    queries: list[str] = []

    for site in SITES:
        site_prefix = f"site:{site}"
        for ent in entities:
            label = ent["label"]
            ent_q = f'"{label}"' if " " in label else label
            for block in TERM_BLOCKS:
                # keep it readable; OR-join terms
                terms = block["terms"]
                term_expr = " OR ".join([f'"{t}"' if " " in t else t for t in terms])
                queries.append(f"{site_prefix} {ent_q} ({term_expr})")

    # include non-entity baseline queries too
    baseline = [
        "(\"nondiscrimination clause\" OR nondiscrimination OR \"anti-retaliation\" OR retaliation)",
        "(procurement OR contract OR RFP OR RFQ OR bid OR solicitation)",
        "(\"cultural competence\" OR \"lived experience\" OR \"equity lens\" OR \"diverse slate\" OR quota)",
    ]
    for site in SITES:
        site_prefix = f"site:{site}"
        for b in baseline:
            queries.append(f"{site_prefix} {b}")

    # de-dupe
    seen = set()
    out = []
    for q in queries:
        qn = re.sub(r"\s+", " ", q).strip()
        if qn in seen:
            continue
        seen.add(qn)
        out.append(qn)
    return out


def main() -> None:
    if not os.path.exists(KG_JSON):
        raise SystemExit(f"missing {KG_JSON}")

    kg = load_kg()
    entities = compute_top_entities(kg, limit=60)
    queries = build_queries(entities)

    pack = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "inputs": {"knowledge_graph": KG_JSON},
        "sites": SITES,
        "term_blocks": TERM_BLOCKS,
        "seed_entities": entities,
        "queries": queries,
    }

    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)

    with open(OUT_TXT, "w", encoding="utf-8") as f:
        for q in queries:
            f.write(q + "\n")

    print("wrote", OUT_JSON)
    print("wrote", OUT_TXT)
    print("seed_entities", len(entities))
    print("queries", len(queries))


if __name__ == "__main__":
    main()
