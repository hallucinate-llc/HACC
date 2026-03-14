#!/usr/bin/env python3
"""Build violation-focused search queries via complaint-generator's research seed module."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.research_seed_generator import (
    CATEGORY_TERMS,
    DEFAULT_SITES,
    ENTITY_TYPE_ALLOW,
    Entity,
    build_entity_pool,
    entity_label_ok,
    load_kg_nodes,
    make_queries,
    parse_top_entities,
)


DEFAULT_REVIEWS = "research_results/audit_policy_reviews_20251231.csv"
DEFAULT_KG = "research_results/audit_policy_knowledge_graph_20251231.json"


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate violation-focused search queries from audit review + KG.")
    parser.add_argument("--reviews", default=DEFAULT_REVIEWS, help="Audit policy reviews CSV")
    parser.add_argument("--kg", default=DEFAULT_KG, help="Knowledge graph JSON")
    parser.add_argument("--min-score", type=int, default=2, help="Minimum max_checklist_score to include (default: 2)")
    parser.add_argument("--top-entities", type=int, default=40, help="How many top entities to use (default: 40)")
    parser.add_argument("--max-docs", type=int, default=None, help="Optional cap on number of docs scanned")
    parser.add_argument("--max-queries", type=int, default=1500, help="Cap the number of queries emitted")
    parser.add_argument("--max-query-chars", type=int, default=280, help="Max characters per emitted query")
    parser.add_argument("--terms-per-query", type=int, default=3, help="How many focus terms to include per query")
    parser.add_argument("--max-focus-terms", type=int, default=12, help="Use only the top N focus terms after dedupe")
    parser.add_argument("--legal-terms-per-query", type=int, default=1, help="How many legal terms to append per query")
    parser.add_argument("--no-sites", action="store_true", help="Do not emit site: restricted queries")
    parser.add_argument(
        "--category",
        action="append",
        default=[],
        help=f"Restrict to a specific max_checklist_category (repeatable). Options: {sorted(CATEGORY_TERMS.keys())}",
    )
    args = parser.parse_args()

    reviews_path = Path(args.reviews)
    kg_path = Path(args.kg)
    if not reviews_path.exists():
        raise SystemExit(f"missing reviews CSV: {reviews_path}")
    if not kg_path.exists():
        raise SystemExit(f"missing KG JSON: {kg_path}")

    kg_nodes = load_kg_nodes(kg_path)
    selected_rows, entity_scores, _doc_categories = build_entity_pool(
        reviews_path=reviews_path,
        kg_nodes_by_label=kg_nodes,
        min_checklist_score=args.min_score,
        max_docs=args.max_docs,
    )

    if args.category:
        allowed = set(args.category)
        filtered_rows = [row for row in selected_rows if (row.get("max_checklist_category") or "") in allowed]
        selected_rows = filtered_rows
        from collections import Counter

        entity_scores = Counter()
        for row in selected_rows:
            for label, count in parse_top_entities(row.get("top_entities") or ""):
                if not entity_label_ok(label):
                    continue
                node = kg_nodes.get(label.lower())
                node_type = (node.get("type") if node else None) or "entity"
                if node_type not in ENTITY_TYPE_ALLOW:
                    continue
                entity_scores[label] += count

    top_entities: list[Entity] = []
    for label, score in entity_scores.most_common(500):
        node = kg_nodes.get(label.lower()) or {}
        entity_type = (node.get("type") or "entity").strip()
        if entity_type not in ENTITY_TYPE_ALLOW:
            continue
        top_entities.append(Entity(label=label, type=entity_type, score=int(score)))
        if len(top_entities) >= args.top_entities:
            break

    from collections import Counter

    category_counts: Counter[str] = Counter()
    for row in selected_rows:
        category = (row.get("max_checklist_category") or "").strip()
        if category:
            category_counts[category] += 1

    focus_terms: list[str] = []
    for category, _count in category_counts.most_common():
        focus_terms.extend(CATEGORY_TERMS.get(category, []))
    if not focus_terms:
        for category in ("selection_contracting", "proxies", "preferential_treatment"):
            focus_terms.extend(CATEGORY_TERMS[category])

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_pack = Path("research_results") / f"kg_violation_seed_pack_{ts}.json"
    out_txt = Path("research_results") / f"kg_violation_seed_queries_{ts}.txt"

    queries = make_queries(
        entities=top_entities,
        sites=DEFAULT_SITES,
        include_sites=not args.no_sites,
        max_queries=args.max_queries,
        category_focus_terms=focus_terms,
        max_query_chars=args.max_query_chars,
        terms_per_query=args.terms_per_query,
        max_focus_terms=args.max_focus_terms,
        legal_terms_per_query=args.legal_terms_per_query,
    )

    pack = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "inputs": {"reviews": str(reviews_path), "kg": str(kg_path)},
        "filters": {
            "min_checklist_score": args.min_score,
            "categories": args.category,
            "top_entities": args.top_entities,
            "max_docs": args.max_docs,
            "emit_site_restricted": (not args.no_sites),
        },
        "selected_docs": len(selected_rows),
        "category_counts": dict(category_counts),
        "top_entities": [entity.__dict__ for entity in top_entities],
        "sites": ([] if args.no_sites else DEFAULT_SITES),
        "focus_terms": focus_terms,
        "queries": queries,
        "generated_by": "complaint_analysis.research_seed_generator",
    }

    out_pack.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    out_txt.write_text("\n".join(queries) + "\n", encoding="utf-8")

    print("wrote", out_pack)
    print("wrote", out_txt)
    print("selected_docs", len(selected_rows))
    print("top_entities", len(top_entities))
    print("queries", len(queries))
    if category_counts:
        print("category_counts", dict(category_counts))


if __name__ == "__main__":
    main()
