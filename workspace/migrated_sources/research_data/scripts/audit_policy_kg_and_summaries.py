#!/usr/bin/env python3
"""Audit-policy summaries + knowledge graph for risk_score>0 documents.

This script uses the checklist and scoring rubric described in `agent.md`.
It does NOT claim legal violations; it produces an evidence-backed, automated
triage mapping:
  - 0: no evidence found
  - 1: possible issue (weak indicators)
  - 2: probable issue (multiple indicators / clearer context)
  - 3: clear issue indicator (explicit red-flag style language)

Inputs (existing artifacts):
  - research_results/risk_score_gt0_full_analysis_20251231.csv
  - research_results/document_index_20251231_100922.json (optional enrichment)

Outputs:
  - research_results/audit_policy_reviews_20251231.csv
  - research_results/audit_policy_reviews_20251231.md
  - research_results/audit_policy_knowledge_graph_20251231.json
  - research_results/audit_policy_knowledge_graph_20251231.dot

"""

from __future__ import annotations

import csv
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable

IN_CSV = "research_results/risk_score_gt0_full_analysis_20251231.csv"
INDEX_JSON = "research_results/document_index_20251231_100922.json"

OUT_CSV = "research_results/audit_policy_reviews_20251231.csv"
OUT_MD = "research_results/audit_policy_reviews_20251231.md"
OUT_GRAPH_JSON = "research_results/audit_policy_knowledge_graph_20251231.json"
OUT_GRAPH_DOT = "research_results/audit_policy_knowledge_graph_20251231.dot"

MAX_TEXT_CHARS = 250_000
MAX_ENTITIES_PER_DOC = 15
MAX_CO_MENTION_EDGES_PER_DOC = 40

WS_RE = re.compile(r"\s+")
SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")
TERM_COUNT_RE = re.compile(r"\((\d+)\)")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", text or "").strip()


def read_text(path: str, limit_chars: int = MAX_TEXT_CHARS) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit_chars)
    except Exception:
        return ""


def sum_term_counts(term_field: str) -> int:
    if not term_field:
        return 0
    return sum(int(m.group(1)) for m in TERM_COUNT_RE.finditer(term_field))


def is_asset_like(row: dict[str, str]) -> bool:
    ct = (row.get("content_type") or "").lower()
    classification = (row.get("classification") or "").lower()
    if classification.startswith("quantumresidential:asset-"):
        return True
    if ct.startswith("image/"):
        return True
    if ct in ("application/javascript", "text/javascript", "text/css"):
        return True
    return False


@dataclass(frozen=True)
class ChecklistCategory:
    key: str
    title: str
    # patterns that strongly suggest score 3
    strong: tuple[re.Pattern[str], ...]
    # patterns that suggest score 2
    medium: tuple[re.Pattern[str], ...]
    # patterns that suggest score 1
    weak: tuple[re.Pattern[str], ...]


def _p(phrases: Iterable[str]) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(p, re.IGNORECASE) for p in phrases)


CHECKLIST: tuple[ChecklistCategory, ...] = (
    ChecklistCategory(
        key="preferential_treatment",
        title="Preferential Treatment",
        strong=_p(
            [
                r"\bdiversity\s+quota\b",
                r"\bracial\s+quota\b",
                r"\bgender\s+quota\b",
                r"\bBIPOC\s*-?only\b",
                r"\bminority\s*-?only\b",
                r"\bwomen\s*-?only\b",
                r"\brace\s*-?exclusive\b",
                r"\bsex\s*-?exclusive\b",
                r"\brequired\s+(?:racial|race|sex|gender)\b",
            ]
        ),
        medium=_p(
            [
                r"\bdiverse\s+slate\b",
                r"\brepresentation\s+minimum\b",
                r"\bminimum\s+representation\b",
                r"\bset-?aside\b",
            ]
        ),
        weak=_p(
            [
                r"\bunderrepresented\b",
                r"\bunderserved\b",
                r"\bequity\b",
                r"\bdiversity\b",
                r"\binclusion\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="proxies",
        title="Use of Proxies",
        strong=_p(
            [
                r"\b(?:must|shall|required)\b.{0,60}\b(?:cultural competence|lived experience|equity lens|equity framework)\b",
                r"\bscoring\s+rubric\b.{0,120}\b(?:cultural competence|lived experience)\b",
            ]
        ),
        medium=_p(
            [
                r"\bcultural competence\b",
                r"\blived experience\b",
                r"\bequity lens\b",
                r"\bequity framework\b",
                r"\bsafe space\b",
                r"\bbarrier reduction\b",
                r"\bdiversity statement\b",
            ]
        ),
        weak=_p(
            [
                r"\bunderrepresented\b",
                r"\bunderserved\b",
                r"\bcommunity engagement\b",
                r"\baccessibility\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="segregation_exclusion",
        title="Segregation / Exclusion",
        strong=_p(
            [
                r"\bseparate\b.{0,80}\b(?:session|training|meeting|event|facility|room|restroom|locker)\b.{0,80}\b(?:race|sex|gender|religion|national origin)\b",
                r"\bBIPOC\s*-?only\b",
                r"\brestricted\s+to\b.{0,40}\b(?:race|sex|gender)\b",
            ]
        ),
        medium=_p(
            [
                r"\bexclusive\b.{0,40}\b(?:race|sex|gender)\b",
                r"\bidentity\s+based\b",
            ]
        ),
        weak=_p(
            [
                r"\baffinity\s+group\b",
                r"\bsafe space\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="selection_contracting",
        title="Selection & Contracting Practices",
        strong=_p(
            [
                r"\b(?:must|shall|required)\b.{0,80}\b(?:women-owned|minority-owned|BIPOC)\b",
                r"\btiebreak\w*\b.{0,80}\b(?:race|sex|gender)\b",
                r"\b(?:require|required)\b.{0,80}\bhours\b.{0,80}\b(?:minority|women|BIPOC)\b",
            ]
        ),
        medium=_p(
            [
                r"\bMWBE\b",
                r"\bDBE\b",
                r"\bwomen-owned\b",
                r"\bminority-owned\b",
                r"\bdisadvantaged business enterprise\b",
                r"\bprocurement\b",
                r"\bRFP\b",
                r"\bRFQ\b",
                r"\bbid\b",
                r"\bcontract\b",
                r"\bsubaward\b",
                r"\bsubgrant\b",
                r"\bsolicitation\b",
            ]
        ),
        weak=_p(
            [
                r"\bvendor\b",
                r"\baward\b",
                r"\bscoring\b",
                r"\bevaluation\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="training_hostile_environment",
        title="Training Content & Hostile Environment",
        strong=_p(
            [
                r"\b(?:must|required)\b.{0,120}\b(?:confess|admit)\b",
                r"\b(?:white|male)\s+privilege\b.{0,120}\b(?:must|required)\b",
                r"\boppressive\b.{0,120}\b(?:protected class|race|sex|gender)\b",
            ]
        ),
        medium=_p(
            [
                r"\bprivilege\b",
                r"\boppressor\b",
                r"\boppressive\b",
                r"\binherent\s+bias\b",
                r"\banti-?racist\b",
                r"\bantiracist\b",
                r"\bDEI\s+training\b",
            ]
        ),
        weak=_p(
            [
                r"\btraining\b",
                r"\bworkshop\b",
                r"\bcurriculum\b",
                r"\bmandatory\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="third_party_funding_monitoring",
        title="Third-Party Funding & Monitoring",
        strong=_p(
            [
                r"\bfunding\b.{0,120}\b(?:only|exclusive)\b.{0,120}\b(?:race|sex|gender|religion)\b",
            ]
        ),
        medium=_p(
            [
                r"\bnondiscrimination\b",
                r"\bmonitoring\b",
                r"\bcorrective action\b",
                r"\btermination\b",
                r"\bsubrecipient\b",
                r"\bsubaward\b",
                r"\bsubgrant\b",
            ]
        ),
        weak=_p(
            [
                r"\bMOU\b",
                r"\bagreement\b",
                r"\bcontract\b",
                r"\bgrant\b",
            ]
        ),
    ),
    ChecklistCategory(
        key="retaliation_protections",
        title="Retaliation Protections",
        strong=_p(
            [
                r"\bretaliat\w+\b.{0,80}\bcomplain\w*\b",
                r"\bdisciplin\w+\b.{0,80}\bcomplain\w*\b",
                r"\bterminated\b.{0,80}\bcomplain\w*\b",
            ]
        ),
        medium=_p(
            [
                r"\banti-?retaliation\b",
                r"\bretaliat\w+\b",
                r"\bwhistleblower\b",
                r"\bcomplaint\b",
                r"\bgrievance\b",
            ]
        ),
        weak=_p(
            [
                r"\breporting\b",
                r"\bconfidential\b",
                r"\binvestigation\b",
            ]
        ),
    ),
)


def score_category(text: str, cat: ChecklistCategory) -> tuple[int, list[str]]:
    """Return (score, evidence_snippets)."""
    low = text.lower()

    def first_snips(patterns: Iterable[re.Pattern[str]], limit: int) -> list[str]:
        out: list[str] = []
        for pat in patterns:
            m = pat.search(text)
            if not m:
                continue
            start = max(0, m.start() - 140)
            end = min(len(text), m.end() + 140)
            out.append("…" + normalize(text[start:end]) + "…")
            if len(out) >= limit:
                break
        return out

    strong_hits = sum(1 for p in cat.strong if p.search(low))
    if strong_hits:
        return 3, first_snips(cat.strong, 2)

    medium_hits = sum(1 for p in cat.medium if p.search(low))
    weak_hits = sum(1 for p in cat.weak if p.search(low))

    if medium_hits >= 2:
        return 2, first_snips(cat.medium, 2)
    if medium_hits == 1 and weak_hits >= 1:
        return 2, first_snips(cat.medium, 2)
    if medium_hits == 1:
        return 1, first_snips(cat.medium, 1)
    if weak_hits >= 2:
        return 1, first_snips(cat.weak, 1)

    return 0, []


# Basic entity extraction (lightweight heuristics, no external NLP deps).
ENTITY_PHRASE = re.compile(
    r"\b(?:[A-Z]{2,}|[A-Z][a-z]+)(?:\s+(?:[A-Z]{2,}|[A-Z][a-z]+|&|of|and|for|the|in|to|&))+\b|\b[A-Z]{2,}\b"
)
LAW_HINT = re.compile(r"\b(?:OAR\s*\d+|ORS\s*\d+|Executive\s+Order\s*\d+|Fair\s+Housing\s+Act|Civil\s+Rights\s+Act|Title\s+VI)\b", re.IGNORECASE)

STOP_ENTITY = {
    "The",
    "A",
    "An",
    "And",
    "Or",
    "Of",
    "For",
    "To",
    "In",
    "On",
    "With",
    "By",
    "From",
    "Page",
    "Table",
    "Contents",
    "Figure",
}


def guess_entity_type(label: str) -> str:
    l = label.strip()
    low = l.lower()
    if LAW_HINT.search(l):
        return "policy_or_law"
    if any(s in low for s in ("department", "authority", "agency", "commission", "council", "county", "state", "hud", "boli")):
        return "government_body"
    if re.search(r"\b(inc|llc|ltd|corporation|corp|company|co\.)\b", low):
        return "organization"
    if re.search(r"\b(program|plan|initiative|project|grant)\b", low):
        return "program"
    # two tokens Title Case often a person name
    toks = [t for t in re.split(r"\s+", l) if t]
    if len(toks) == 2 and all(t[0].isupper() for t in toks) and toks[0].isalpha() and toks[1].isalpha():
        return "person"
    return "entity"


def extract_entities(text: str) -> list[tuple[str, str, int]]:
    """Return list of (entity_label, entity_type, count) sorted by count desc."""
    counts: Counter[str] = Counter()

    # include explicit law references
    for m in LAW_HINT.finditer(text):
        counts[normalize(m.group(0))] += 2

    for m in ENTITY_PHRASE.finditer(text):
        ent = normalize(m.group(0))
        if not ent or ent in STOP_ENTITY:
            continue
        if len(ent) < 3:
            continue
        if len(ent) > 80:
            continue
        # filter obvious junk from OCR (very repetitive single letters)
        if re.fullmatch(r"[A-Z]{2,}", ent) and len(ent) > 10:
            continue
        counts[ent] += 1

    out = []
    for ent, c in counts.most_common(200):
        et = guess_entity_type(ent)
        out.append((ent, et, c))
    return out


def extract_summary(text: str, max_sentences: int = 4) -> list[str]:
    clean = normalize(text)
    sents = SENT_SPLIT.split(clean)
    out: list[str] = []
    for s in sents:
        s = s.strip()
        if len(s) < 40:
            continue
        low = s.lower()
        if "skip to main content" in low:
            continue
        if any(k in low for k in ("housing", "procurement", "contract", "agreement", "policy", "civil rights", "fair housing", "hud", "oar", "ors", "grant", "audit")):
            out.append(s[:260])
        if len(out) >= max_sentences:
            break
    if out:
        return out

    # fallback: first longer sentences
    for s in sents:
        s = s.strip()
        if len(s) >= 70:
            out.append(s[:260])
        if len(out) >= max_sentences:
            break
    return out


def overall_assessment(max_score: int) -> str:
    if max_score >= 3:
        return "likely-violation-indicator (score 3 red-flag language)"
    if max_score == 2:
        return "needs-review (probable issue indicators)"
    if max_score == 1:
        return "needs-review (possible issue indicators)"
    return "no-issue-indicators-found"


def applicability_note(classification: str, domain: str, url: str) -> str:
    dom = (domain or "").lower()
    cls = (classification or "").lower()
    u = (url or "").lower()

    if cls.startswith("document:local-pdf") or u.startswith("file://"):
        return "local document (potentially binding if policy/contract; needs context)"
    if dom.endswith(".gov") or dom in ("www.hud.gov", "www.hudexchange.info"):
        return "government source (more likely binding/authoritative)"
    if dom.endswith("quantumresidential.com"):
        return "vendor/partner site (may be contractual or informational; verify incorporation by reference)"
    if cls.startswith("third-party"):
        return "third-party informational (not binding unless adopted/required by contract/policy)"
    return "unknown applicability"


def load_index_by_id() -> dict[str, dict[str, Any]]:
    if not os.path.exists(INDEX_JSON):
        return {}
    with open(INDEX_JSON, "r", encoding="utf-8") as f:
        docs = json.load(f)
    return {d.get("id"): d for d in docs if d.get("id")}


def main() -> None:
    if not os.path.exists(IN_CSV):
        raise SystemExit(f"missing input: {IN_CSV}")

    with open(IN_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    index_by_id = load_index_by_id()

    # Graph structures
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}

    def add_node(node_id: str, node_type: str, label: str, **attrs: Any) -> None:
        if node_id in nodes:
            # merge a few counters if needed
            for k, v in attrs.items():
                if isinstance(v, int) and isinstance(nodes[node_id].get(k), int):
                    nodes[node_id][k] += v
                else:
                    nodes[node_id].setdefault(k, v)
            return
        nodes[node_id] = {"id": node_id, "type": node_type, "label": label, **attrs}

    def add_edge(src: str, dst: str, rel: str, weight: int = 1, evidence: str | None = None) -> None:
        key = (src, dst, rel)
        if key not in edges:
            edges[key] = {"source": src, "target": dst, "type": rel, "weight": 0, "evidence": []}
        edges[key]["weight"] += weight
        if evidence:
            if len(edges[key]["evidence"]) < 3:
                edges[key]["evidence"].append(evidence)

    # Add checklist category nodes
    for cat in CHECKLIST:
        add_node(f"cat:{cat.key}", "checklist_category", cat.title)

    out_rows: list[dict[str, Any]] = []
    assessment_counts = Counter()
    category_score_counts = Counter()

    for r in rows:
        doc_id = r.get("document_id") or ""
        if not doc_id:
            continue

        meta = index_by_id.get(doc_id, {}).get("metadata") if index_by_id.get(doc_id) else {}
        url = (r.get("url") or "")
        domain = (r.get("domain") or "") or (meta.get("domain") if isinstance(meta, dict) else "") or ""
        content_type = r.get("content_type") or ""
        classification = r.get("classification") or ""
        fp = r.get("file_path") or ""

        risk_score = int(r.get("risk_score") or 0)
        dei_total = sum_term_counts(r.get("top_dei_terms") or "")
        binding_total = sum_term_counts(r.get("top_binding_terms") or "")
        proxy_total = sum_term_counts(r.get("top_proxy_terms") or "")

        # Text blob for analysis
        base_blob_parts = [
            r.get("title_guess") or "",
            r.get("summary_sentences") or "",
            r.get("binding_context") or "",
            r.get("dei_context") or "",
            url,
            domain,
        ]

        text = ""
        if fp and os.path.exists(fp) and not is_asset_like(r):
            text = read_text(fp)
            blob = normalize("\n".join(base_blob_parts + [text]))
        else:
            blob = normalize("\n".join(base_blob_parts))

        # Per-category scoring + evidence
        cat_scores: dict[str, int] = {}
        cat_evidence: dict[str, list[str]] = {}
        max_score = 0
        max_cat = ""

        for cat in CHECKLIST:
            s, ev = score_category(blob, cat)
            cat_scores[cat.key] = s
            cat_evidence[cat.key] = ev
            category_score_counts[(cat.key, s)] += 1
            if s > max_score:
                max_score = s
                max_cat = cat.key

        assessment = overall_assessment(max_score)
        assessment_counts[assessment] += 1

        # Summary (use existing summary_sentences if present; else derive)
        summary = (r.get("summary_sentences") or "").strip()
        if not summary and text:
            summary = " | ".join(extract_summary(text, 4))

        # Entities
        entities: list[tuple[str, str, int]] = []
        if text and not is_asset_like(r):
            entities = extract_entities(text)
        else:
            # minimal entities from domain/url
            if domain:
                entities = [(domain, "organization", 2)]

        entities = entities[:MAX_ENTITIES_PER_DOC]

        # Graph: document node
        add_node(
            f"doc:{doc_id}",
            "document",
            doc_id,
            risk_score=risk_score,
            classification=classification,
            domain=domain,
            content_type=content_type,
            url=url,
        )

        # Graph: document -> category edges for score>0
        for cat in CHECKLIST:
            s = cat_scores[cat.key]
            if s <= 0:
                continue
            ev = " | ".join(cat_evidence[cat.key][:1]) if cat_evidence[cat.key] else None
            add_edge(f"doc:{doc_id}", f"cat:{cat.key}", "TRIGGERS", weight=s, evidence=ev)

        # Graph: entities nodes + mention edges
        entity_nodes: list[str] = []
        for ent_label, ent_type, count in entities:
            ent_key = f"ent:{ent_label.lower()}"
            add_node(ent_key, ent_type, ent_label)
            add_edge(f"doc:{doc_id}", ent_key, "MENTIONS", weight=count)
            entity_nodes.append(ent_key)

        # Graph: co-mentions (limit per doc)
        co_edges = 0
        for i in range(len(entity_nodes)):
            for j in range(i + 1, len(entity_nodes)):
                add_edge(entity_nodes[i], entity_nodes[j], "CO_MENTIONED_WITH", weight=1)
                co_edges += 1
                if co_edges >= MAX_CO_MENTION_EDGES_PER_DOC:
                    break
            if co_edges >= MAX_CO_MENTION_EDGES_PER_DOC:
                break

        # Build row output
        row_out: dict[str, Any] = {
            "document_id": doc_id,
            "risk_score": risk_score,
            "assessment": assessment,
            "max_checklist_score": max_score,
            "max_checklist_category": max_cat,
            "classification": classification,
            "applicability": applicability_note(classification, domain, url),
            "domain": domain,
            "content_type": content_type,
            "url": url,
            "file_path": fp,
            "text_length": int(r.get("text_length") or 0),
            "binding_terms_total": binding_total,
            "dei_terms_total": dei_total,
            "proxy_terms_total": proxy_total,
            "summary_sentences": summary,
        }

        # Flatten category scores + 1 evidence field
        for cat in CHECKLIST:
            row_out[f"score_{cat.key}"] = cat_scores[cat.key]
            row_out[f"evidence_{cat.key}"] = " | ".join(cat_evidence[cat.key][:2])

        # Entities list for spreadsheet filtering
        row_out["top_entities"] = "; ".join([f"{lbl}({cnt})" for lbl, _t, cnt in entities])

        out_rows.append(row_out)

    # Sort: prioritize likely-violation indicators then by risk score and binding total
    def sort_key(rr: dict[str, Any]) -> tuple[int, int, int, int]:
        assess = rr.get("assessment") or ""
        tier = 0
        if assess.startswith("likely-violation-indicator"):
            tier = 3
        elif "probable" in assess:
            tier = 2
        elif "possible" in assess:
            tier = 1
        return (tier, int(rr.get("max_checklist_score") or 0), int(rr.get("risk_score") or 0), int(rr.get("binding_terms_total") or 0))

    out_rows.sort(key=sort_key, reverse=True)

    # Write CSV
    fieldnames = list(out_rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    # Write Markdown
    md: list[str] = []
    md.append("# Audit-policy review (agent.md checklist) for risk_score > 0 documents")
    md.append("")
    md.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    md.append("")
    md.append("Notes")
    md.append("- This is an automated triage against the checklist in agent.md; it is not legal advice.")
    md.append("- 'likely-violation-indicator' means explicit red-flag language was detected (score 3) and should be reviewed by counsel.")
    md.append("")
    md.append("## Rollups")
    md.append(f"- Total documents reviewed: {len(out_rows)}")
    md.append("- Assessment counts: " + ", ".join([f"{k}={v}" for k, v in assessment_counts.most_common()]))
    md.append("")
    md.append("## Category score distribution")
    for cat in CHECKLIST:
        counts = {s: category_score_counts[(cat.key, s)] for s in (0, 1, 2, 3)}
        md.append(f"- {cat.title}: 0={counts[0]} 1={counts[1]} 2={counts[2]} 3={counts[3]}")
    md.append("")

    md.append("## Per-document findings")
    md.append("")

    for rr in out_rows:
        md.append(f"### {rr['document_id']} (assessment={rr['assessment']}, risk={rr['risk_score']}, max_score={rr['max_checklist_score']})")
        md.append(f"- Classification: {rr['classification']}")
        if rr.get("applicability"):
            md.append(f"- Applicability: {rr['applicability']}")
        if rr.get("domain"):
            md.append(f"- Domain: {rr['domain']}")
        if rr.get("content_type"):
            md.append(f"- Content-Type: {rr['content_type']}")
        if rr.get("url"):
            md.append(f"- URL: {rr['url']}")
        if rr.get("summary_sentences"):
            md.append("- Summary:")
            for s in str(rr.get("summary_sentences") or "").split(" | "):
                s = s.strip()
                if s:
                    md.append(f"  - {s}")

        md.append("- Checklist scores:")
        for cat in CHECKLIST:
            s = int(rr.get(f"score_{cat.key}") or 0)
            if s <= 0:
                continue
            md.append(f"  - {cat.title}: {s}")
            ev = rr.get(f"evidence_{cat.key}")
            if ev:
                for e in str(ev).split(" | "):
                    e = e.strip()
                    if e:
                        md.append(f"    - {e}")

        if rr.get("top_entities"):
            md.append(f"- Top entities: {rr['top_entities']}")

        md.append("")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # Graph output
    graph = {
        "generated": datetime.now().isoformat(timespec="seconds"),
        "source": {
            "csv": IN_CSV,
            "index": INDEX_JSON,
            "policy": "agent.md",
        },
        "nodes": list(nodes.values()),
        "edges": list(edges.values()),
    }

    with open(OUT_GRAPH_JSON, "w", encoding="utf-8") as f:
        json.dump(graph, f, ensure_ascii=False, indent=2)

    # Graphviz DOT (best-effort, keep small)
    dot: list[str] = []
    dot.append("digraph AuditKG {")
    dot.append("  rankdir=LR;")
    dot.append('  node [shape=box];')

    # Emit category nodes
    for cat in CHECKLIST:
        cid = f"cat:{cat.key}"
        lbl = nodes[cid]["label"].replace('"', "'")
        dot.append(f'  "{cid}" [shape=oval,label="{lbl}"];')

    # Emit a limited number of document nodes (top 80) for readability
    doc_nodes = [n for n in nodes.values() if n.get("type") == "document"]
    doc_nodes.sort(key=lambda n: (int(n.get("risk_score") or 0), int(n.get("classification") == "document:local-pdf")), reverse=True)
    doc_keep = {n["id"] for n in doc_nodes[:80]}

    for did in doc_keep:
        lbl = did.replace("doc:", "")
        dot.append(f'  "{did}" [shape=box,label="{lbl}"];')

    # Emit edges among kept docs and categories + their entity mentions (limit entities)
    emitted_entities: set[str] = set()
    for e in edges.values():
        s = e["source"]
        t = e["target"]
        rel = e["type"]
        w = int(e.get("weight") or 1)
        if s.startswith("doc:") and s in doc_keep and t.startswith("cat:") and rel == "TRIGGERS":
            dot.append(f'  "{s}" -> "{t}" [label="{w}"];')
        if s.startswith("doc:") and s in doc_keep and t.startswith("ent:") and rel == "MENTIONS" and w >= 2:
            # emit entity node if not yet
            if t not in emitted_entities:
                ent_lbl = nodes[t]["label"].replace('"', "'")
                shape = "diamond" if nodes[t]["type"] in ("policy_or_law",) else "box"
                dot.append(f'  "{t}" [shape={shape},label="{ent_lbl}"];')
                emitted_entities.add(t)
            dot.append(f'  "{s}" -> "{t}" [label="{w}"];')

    dot.append("}")
    with open(OUT_GRAPH_DOT, "w", encoding="utf-8") as f:
        f.write("\n".join(dot))

    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("wrote", OUT_GRAPH_JSON)
    print("wrote", OUT_GRAPH_DOT)
    print("assessment counts", dict(assessment_counts))


if __name__ == "__main__":
    main()
