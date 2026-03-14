#!/usr/bin/env python3
"""Generate KG-based seed data by delegating to the violation-focused seed builder."""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import kg_violation_seed_queries as violation_seed_queries


KG_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"
OUT_JSON = "research_results/kg_seed_pack_20251231.json"
OUT_TXT = "research_results/kg_seed_queries_20251231.txt"


def main() -> None:
    kg_path = Path(KG_JSON)
    if not kg_path.exists():
        raise SystemExit(f"missing {KG_JSON}")

    kg_nodes = violation_seed_queries.load_kg_nodes(kg_path)
    top_entities: list[violation_seed_queries.Entity] = []
    for label, node in sorted(
        ((node.get("label") or "", node) for node in kg_nodes.values()),
        key=lambda item: len(item[0]),
    ):
        label = (label or "").strip()
        if not violation_seed_queries.entity_label_ok(label):
            continue
        entity_type = (node.get("type") or "entity").strip()
        if entity_type not in violation_seed_queries.ENTITY_TYPE_ALLOW:
            continue
        top_entities.append(violation_seed_queries.Entity(label=label, type=entity_type, score=1))
        if len(top_entities) >= 60:
            break

    focus_terms: list[str] = []
    for category in ("selection_contracting", "proxies", "retaliation_protections"):
        focus_terms.extend(violation_seed_queries.CATEGORY_TERMS.get(category, []))

    queries = violation_seed_queries.make_queries(
        entities=top_entities,
        sites=violation_seed_queries.DEFAULT_SITES,
        include_sites=True,
        max_queries=1500,
        category_focus_terms=focus_terms,
        max_query_chars=280,
        terms_per_query=3,
        max_focus_terms=12,
        legal_terms_per_query=1,
    )

    pack = {
        "generated": violation_seed_queries.datetime.now().isoformat(timespec="seconds"),
        "inputs": {"knowledge_graph": KG_JSON},
        "sites": violation_seed_queries.DEFAULT_SITES,
        "focus_terms": focus_terms,
        "seed_entities": [entity.__dict__ for entity in top_entities],
        "queries": queries,
        "generated_by": "kg_violation_seed_queries.make_queries",
    }

    Path(OUT_JSON).write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(OUT_TXT).write_text("\n".join(queries) + "\n", encoding="utf-8")

    print("wrote", OUT_JSON)
    print("wrote", OUT_TXT)
    print("seed_entities", len(top_entities))
    print("queries", len(queries))


if __name__ == "__main__":
    main()
