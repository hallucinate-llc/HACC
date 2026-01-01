#!/usr/bin/env python3
"""Build a *violation-focused* search query list from the audit review + KG.

Goal: Use the knowledge graph + audit-policy scoring to identify the entities most associated
with potential policy/law risk indicators, then generate keyword queries for web search.

Inputs (defaults match current outputs):
- research_results/audit_policy_reviews_20251231.csv
- research_results/audit_policy_knowledge_graph_20251231.json

Outputs (timestamped):
- research_results/kg_violation_seed_pack_<ts>.json
- research_results/kg_violation_seed_queries_<ts>.txt

This script does NOT perform any network access.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

DEFAULT_REVIEWS = "research_results/audit_policy_reviews_20251231.csv"
DEFAULT_KG = "research_results/audit_policy_knowledge_graph_20251231.json"

DEFAULT_SITES = [
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

ENTITY_TYPE_ALLOW = {
    "government_body",
    "policy_or_law",
    "program",
    "organization",
    "entity",
}

# Filter out boilerplate / address artifacts that show up as "entities".
STOP_LABELS = {
    "fax",
    "phone",
    "suite",
    "ne suite",
    "summer st",
    "summer street ne",
    "center st",
    "capitol street ne",
    "salem",
    "page",
    "section",
    "initial",
    "continue to",
    "due to",
    "try our",
    "marketplace catalog manager",
    "all rights reserved",
}

ACRONYM_ALLOW = {
    "OHCS",
    "HUD",
    "ORS",
    "OAR",
    "ORCA",
    "NSF",
    "OED",
    "ODOE",
    "OBO",
    "PSH",
    "AMI",
    "COBID",
    "MWESB",
    "DBE",
    "LIHTC",
    "NTIA",
    "OHA",
    "ODE",
    "DCBS",
    "DEQ",
    "DLCD",
    "OREA",
    "HACC",
    "EIC",
    "VBE",
    "WBE",
    "MBE",
    "GINA",
    "USC",
    "ADA",
    "BIPOC",
    "LGBTQ",
    "LGBTQIA",
    "DEI",
    "STEM",
}


def entity_label_ok(label: str) -> bool:
    s = (label or "").strip()
    if not s:
        return False
    if len(s) > 90:
        return False
    sl = s.lower()
    if sl in STOP_LABELS:
        return False

    # common extraction artifacts from documents
    if re.search(r"\b(initial|materials?|packet|mtg|agenda)\b", sl):
        return False

    # drop unknown short all-caps codes (keeps allowlisted acronyms)
    if re.fullmatch(r"[A-Z]{2,6}", s):
        if s not in ACRONYM_ALLOW:
            return False
    # must contain at least one letter
    if not re.search(r"[A-Za-z]", s):
        return False
    # address-ish patterns
    if re.search(r"\b(street|\bst\b|ave|avenue|blvd|suite|ste\b|\bne\b|\bnw\b|\bse\b|\bsw\b)\b", sl):
        # allow law cites like "ORS"/"OAR" even if they co-occur elsewhere
        if sl not in {"ors", "oar"}:
            return False
    # discard pure boilerplate acronyms
    if sl in {"pdf", "html", "get", "post", "iso"}:
        return False
    return True

# Category-aligned term banks
CATEGORY_TERMS: dict[str, list[str]] = {
    "preferential_treatment": [
        "quota",
        "set-aside",
        "preference",
        "race-based",
        "sex-based",
        "affirmative action",
        "prioritize",
        "eligibility",
        "scoring criteria",
    ],
    "proxies": [
        "equity lens",
        "racial equity framework",
        "cultural competence",
        "lived experience",
        "targeted universalism",
        "equity impact",
    ],
    "selection_contracting": [
        "procurement",
        "contract",
        "RFP",
        "RFQ",
        "bid",
        "solicitation",
        "subaward",
        "monitoring",
        "nondiscrimination clause",
        "COBID",
        "MWESB",
        "DBE",
    ],
    "training_hostile_environment": [
        "mandatory training",
        "anti-racist training",
        "implicit bias",
        "unconscious bias",
        "hostile environment",
        "harassment",
    ],
    "third_party_funding_monitoring": [
        "subrecipient",
        "subaward",
        "grant agreement",
        "contract compliance",
        "certification",
        "reporting requirements",
        "self-report",
    ],
    "retaliation_protections": [
        "retaliation",
        "anti-retaliation",
        "whistleblower",
        "complaint procedure",
        "grievance",
        "investigation",
    ],
    "segregation_exclusion": [
        "segregation",
        "separate",
        "exclusion",
        "restricted to",
        "race-specific",
    ],
}

# Baseline “law-ish” terms used to focus results toward authoritative content.
LEGAL_TERMS = [
    "policy",
    "rule",
    "statute",
    "ORS",
    "OAR",
    "Title VI",
    "Civil Rights Act",
    "nondiscrimination",
    "complaint",
]


@dataclass(frozen=True)
class Entity:
    label: str
    type: str
    score: int


def load_kg_nodes(kg_path: Path) -> dict[str, dict[str, Any]]:
    kg = json.loads(kg_path.read_text(encoding="utf-8"))
    out: dict[str, dict[str, Any]] = {}
    for n in kg.get("nodes", []):
        if not isinstance(n, dict):
            continue
        label = (n.get("label") or "").strip()
        if not label:
            continue
        out[label.lower()] = n
    return out


def parse_top_entities(cell: str) -> list[tuple[str, int]]:
    # Format looks like: "Race Forward(3); Racial Equity(2); ..."
    out: list[tuple[str, int]] = []
    if not cell:
        return out
    for part in cell.split(";"):
        s = part.strip()
        if not s:
            continue
        m = re.match(r"^(.*)\((\d+)\)\s*$", s)
        if not m:
            continue
        label = m.group(1).strip()
        try:
            cnt = int(m.group(2))
        except ValueError:
            cnt = 1
        if label:
            out.append((label, cnt))
    return out


def row_is_violation_relevant(row: dict[str, str], min_checklist_score: int) -> bool:
    try:
        max_score = int(row.get("max_checklist_score") or 0)
    except ValueError:
        max_score = 0

    assessment = (row.get("assessment") or "").lower()
    if "likely-violation-indicator" in assessment:
        return True

    return max_score >= min_checklist_score


def build_entity_pool(
    reviews_path: Path,
    kg_nodes_by_label: dict[str, dict[str, Any]],
    min_checklist_score: int,
    max_docs: int | None,
) -> tuple[list[dict[str, str]], Counter[str], dict[str, list[str]]]:
    selected_rows: list[dict[str, str]] = []
    entity_scores: Counter[str] = Counter()
    doc_categories: dict[str, list[str]] = {}

    with reviews_path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row_is_violation_relevant(row, min_checklist_score=min_checklist_score):
                continue
            selected_rows.append(row)
            if max_docs is not None and len(selected_rows) >= max_docs:
                break

    for row in selected_rows:
        doc_id = row.get("document_id") or ""
        cat = (row.get("max_checklist_category") or "").strip()
        if doc_id:
            if cat:
                doc_categories[doc_id] = [cat]
            else:
                doc_categories[doc_id] = []

        for label, cnt in parse_top_entities(row.get("top_entities") or ""):
            if not entity_label_ok(label):
                continue
            n = kg_nodes_by_label.get(label.lower())
            node_type = (n.get("type") if n else None) or "entity"
            if node_type not in ENTITY_TYPE_ALLOW:
                continue
            # Aggregate counts; prefer stronger entities
            entity_scores[label] += cnt

    return selected_rows, entity_scores, doc_categories


def quote_if_needed(s: str) -> str:
    if re.search(r"\s", s):
        return f'"{s}"'
    return s


def make_queries(
    entities: list[Entity],
    sites: list[str],
    include_sites: bool,
    max_queries: int,
    category_focus_terms: list[str],
    *,
    max_query_chars: int = 280,
    terms_per_query: int = 3,
    max_focus_terms: int = 12,
    legal_terms_per_query: int = 1,
) -> list[str]:
    queries: list[str] = []

    # DDG is sensitive to long/complex queries (especially big OR blocks).
    # Emit multiple *short* queries instead: entity + a few focus terms (+ optional legal term).
    def dedupe_preserve(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for it in items:
            s = (it or "").strip()
            if not s:
                continue
            k = s.lower()
            if k in seen:
                continue
            seen.add(k)
            out.append(s)
        return out

    focus_terms = dedupe_preserve(category_focus_terms)[:max_focus_terms]
    legal_terms = dedupe_preserve(LEGAL_TERMS)

    def add(q: str) -> None:
        qn = re.sub(r"\s+", " ", q).strip()
        if not qn:
            return
        if len(qn) > max_query_chars:
            # Trim at word boundary.
            qn = qn[:max_query_chars].rsplit(" ", 1)[0].strip()
            if not qn:
                return
        queries.append(qn)

    def chunk_terms(items: list[str], n: int) -> list[list[str]]:
        if n <= 0:
            return []
        out: list[list[str]] = []
        for i in range(0, len(items), n):
            out.append(items[i : i + n])
        return out

    focus_bundles = chunk_terms(focus_terms, max(1, terms_per_query))
    # Keep legal terms very small; they broaden results toward authoritative sources.
    legal_bundle = legal_terms[: max(0, legal_terms_per_query)]

    if include_sites:
        for site in sites:
            site_prefix = f"site:{site}"
            for ent in entities:
                # If we have no focus terms, still emit a minimal query.
                if not focus_bundles:
                    add(f"{site_prefix} {quote_if_needed(ent.label)} {' '.join([quote_if_needed(t) for t in legal_bundle])}")
                    continue

                for bundle in focus_bundles:
                    parts = [site_prefix, quote_if_needed(ent.label)]
                    parts.extend([quote_if_needed(t) for t in bundle])
                    parts.extend([quote_if_needed(t) for t in legal_bundle])
                    add(" ".join([p for p in parts if p]))
    else:
        for ent in entities:
            if not focus_bundles:
                add(f"{quote_if_needed(ent.label)} {' '.join([quote_if_needed(t) for t in legal_bundle])}")
                continue
            for bundle in focus_bundles:
                parts = [quote_if_needed(ent.label)]
                parts.extend([quote_if_needed(t) for t in bundle])
                parts.extend([quote_if_needed(t) for t in legal_bundle])
                add(" ".join([p for p in parts if p]))

    # de-dupe
    out: list[str] = []
    seen: set[str] = set()
    for q in queries:
        if q in seen:
            continue
        seen.add(q)
        out.append(q)
        if len(out) >= max_queries:
            break
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description="Generate violation-focused search queries from audit review + KG.")
    ap.add_argument("--reviews", default=DEFAULT_REVIEWS, help="Audit policy reviews CSV")
    ap.add_argument("--kg", default=DEFAULT_KG, help="Knowledge graph JSON")
    ap.add_argument("--min-score", type=int, default=2, help="Minimum max_checklist_score to include (default: 2)")
    ap.add_argument("--top-entities", type=int, default=40, help="How many top entities to use (default: 40)")
    ap.add_argument("--max-docs", type=int, default=None, help="Optional cap on number of docs scanned")
    ap.add_argument("--max-queries", type=int, default=1500, help="Cap the number of queries emitted")
    ap.add_argument("--max-query-chars", type=int, default=280, help="Max characters per emitted query (default: 280)")
    ap.add_argument("--terms-per-query", type=int, default=3, help="How many focus terms to include per query (default: 3)")
    ap.add_argument("--max-focus-terms", type=int, default=12, help="Use only the top N focus terms after dedupe (default: 12)")
    ap.add_argument("--legal-terms-per-query", type=int, default=1, help="How many legal terms to append per query (default: 1)")
    ap.add_argument("--no-sites", action="store_true", help="Do not emit site: restricted queries")
    ap.add_argument(
        "--category",
        action="append",
        default=[],
        help=f"Restrict to a specific max_checklist_category (repeatable). Options: {sorted(CATEGORY_TERMS.keys())}",
    )
    args = ap.parse_args()

    reviews_path = Path(args.reviews)
    kg_path = Path(args.kg)
    if not reviews_path.exists():
        raise SystemExit(f"missing reviews CSV: {reviews_path}")
    if not kg_path.exists():
        raise SystemExit(f"missing KG JSON: {kg_path}")

    kg_nodes = load_kg_nodes(kg_path)

    selected_rows, entity_scores, _doc_cats = build_entity_pool(
        reviews_path=reviews_path,
        kg_nodes_by_label=kg_nodes,
        min_checklist_score=args.min_score,
        max_docs=args.max_docs,
    )

    if args.category:
        allow = set(args.category)
        filtered_rows = []
        for r in selected_rows:
            if (r.get("max_checklist_category") or "") in allow:
                filtered_rows.append(r)
        selected_rows = filtered_rows

        # rebuild entity scores based on filtered docs
        entity_scores = Counter()
        for row in selected_rows:
            for label, cnt in parse_top_entities(row.get("top_entities") or ""):
                if not entity_label_ok(label):
                    continue
                n = kg_nodes.get(label.lower())
                node_type = (n.get("type") if n else None) or "entity"
                if node_type not in ENTITY_TYPE_ALLOW:
                    continue
                entity_scores[label] += cnt

    top_entities: list[Entity] = []
    for label, score in entity_scores.most_common(500):
        n = kg_nodes.get(label.lower()) or {}
        etype = (n.get("type") or "entity").strip()
        if etype not in ENTITY_TYPE_ALLOW:
            continue
        top_entities.append(Entity(label=label, type=etype, score=int(score)))
        if len(top_entities) >= args.top_entities:
            break

    # Build category-focused term set based on selected docs
    cat_counts: Counter[str] = Counter()
    for r in selected_rows:
        c = (r.get("max_checklist_category") or "").strip()
        if c:
            cat_counts[c] += 1

    focus_terms: list[str] = []
    for cat, _n in cat_counts.most_common():
        focus_terms.extend(CATEGORY_TERMS.get(cat, []))

    # If categories were sparse, default to contracting/proxies/preferential
    if not focus_terms:
        for cat in ("selection_contracting", "proxies", "preferential_treatment"):
            focus_terms.extend(CATEGORY_TERMS[cat])

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
        "category_counts": dict(cat_counts),
        "top_entities": [e.__dict__ for e in top_entities],
        "sites": ([] if args.no_sites else DEFAULT_SITES),
        "focus_terms": focus_terms,
        "queries": queries,
    }

    out_pack.write_text(json.dumps(pack, ensure_ascii=False, indent=2), encoding="utf-8")
    out_txt.write_text("\n".join(queries) + "\n", encoding="utf-8")

    print("wrote", out_pack)
    print("wrote", out_txt)
    print("selected_docs", len(selected_rows))
    print("top_entities", len(top_entities))
    print("queries", len(queries))
    if cat_counts:
        print("category_counts", dict(cat_counts))


if __name__ == "__main__":
    main()
