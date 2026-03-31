#!/usr/bin/env python3
"""Generate a topic-focused triage view for risk_score>0 documents.

Does NOT change risk scoring. It adds topic tags and produces a priority-sorted
subset report for review (government + housing + finance + procurement).

Inputs:
  - research_results/risk_score_gt0_full_analysis_20251231.csv

Outputs:
  - research_results/risk_score_gt0_topic_triage_20251231.csv
  - research_results/risk_score_gt0_topic_triage_20251231.md

"""

from __future__ import annotations

import csv
import os
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

IN_CSV = "research_results/risk_score_gt0_full_analysis_20251231.csv"
OUT_CSV = "research_results/risk_score_gt0_topic_triage_20251231.csv"
OUT_MD = "research_results/risk_score_gt0_topic_triage_20251231.md"

WS_RE = re.compile(r"\s+")
TERM_COUNT_RE = re.compile(r"\((\d+)\)")


def normalize(text: str) -> str:
    return WS_RE.sub(" ", text or "").strip()


def read_text(path: str, limit_chars: int = 250_000) -> str:
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read(limit_chars)
    except Exception:
        return ""


def sum_term_counts(term_field: str) -> int:
    if not term_field:
        return 0
    return sum(int(m.group(1)) for m in TERM_COUNT_RE.finditer(term_field))


@dataclass(frozen=True)
class Topic:
    name: str
    patterns: tuple[re.Pattern[str], ...]


def _make_patterns(phrases: Iterable[str]) -> tuple[re.Pattern[str], ...]:
    pats = []
    for p in phrases:
        # word-ish boundaries, but allow spaces inside phrase
        if re.search(r"[\\W_]", p):
            pats.append(re.compile(re.escape(p), re.IGNORECASE))
        else:
            pats.append(re.compile(rf"\b{re.escape(p)}\b", re.IGNORECASE))
    return tuple(pats)


TOPICS: tuple[Topic, ...] = (
    Topic(
        "government",
        _make_patterns(
            [
                "hud",
                "hud exchange",
                "hudexchange",
                "oregon",
                "ohcs",
                "boli",
                "oar",
                "ors",
                "executive order",
                "regulation",
                "ordinance",
                "statute",
                "compliance",
                "public contracting",
                "statewide",
            ]
        ),
    ),
    Topic(
        "housing",
        _make_patterns(
            [
                "housing",
                "fair housing",
                "public housing",
                "section 8",
                "voucher",
                "hap",
                "tenant",
                "landlord",
                "rent",
                "apartment",
                "property management",
                "homeless",
                "shelter",
            ]
        ),
    ),
    Topic(
        "finance",
        _make_patterns(
            [
                "finance",
                "financial",
                "budget",
                "accounting",
                "audit",
                "fiscal",
                "payment",
                "invoice",
                "reimbursement",
                "grant",
                "funding",
                "subsidy",
                "bond",
                "interest",
            ]
        ),
    ),
    Topic(
        "procurement",
        _make_patterns(
            [
                "procurement",
                "contracting",
                "contract",
                "agreement",
                "rfp",
                "rfq",
                "itb",
                "bid",
                "solicitation",
                "vendor",
                "subcontractor",
                "purchase order",
                "oregonbuys",
            ]
        ),
    ),
)


def topic_hits(text: str) -> dict[str, int]:
    hits: dict[str, int] = {}
    for t in TOPICS:
        n = 0
        for pat in t.patterns:
            n += len(pat.findall(text))
        hits[t.name] = n
    return hits


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


def main() -> None:
    if not os.path.exists(IN_CSV):
        raise SystemExit(f"missing input: {IN_CSV}")

    with open(IN_CSV, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    out_rows: list[dict[str, str]] = []

    counts_any = 0
    counts_by_topic = Counter()

    for r in rows:
        blob_parts = [
            r.get("title_guess") or "",
            r.get("summary_sentences") or "",
            r.get("url") or "",
            r.get("domain") or "",
            r.get("binding_context") or "",
            r.get("dei_context") or "",
        ]

        fp = r.get("file_path") or ""
        if fp and os.path.exists(fp) and not is_asset_like(r):
            blob_parts.append(read_text(fp))

        blob = normalize("\n".join(blob_parts))
        hits = topic_hits(blob)

        tags = [k for k, v in hits.items() if v > 0]
        in_scope = bool(tags)

        if in_scope:
            counts_any += 1
            for t in tags:
                counts_by_topic[t] += 1

        risk = int(r.get("risk_score") or 0)
        bind_sum = sum_term_counts(r.get("top_binding_terms") or "")
        dei_sum = sum_term_counts(r.get("top_dei_terms") or "")

        # Priority score emphasizes in-scope topics + binding language.
        topic_score = sum(hits.values())
        priority_score = (1000 if in_scope else 0) + (risk * 100) + (bind_sum * 5) + (dei_sum * 2) + min(topic_score, 200)

        rr = dict(r)
        rr.update(
            {
                "topic_tags": ";".join(tags),
                "topic_hits_government": str(hits["government"]),
                "topic_hits_housing": str(hits["housing"]),
                "topic_hits_finance": str(hits["finance"]),
                "topic_hits_procurement": str(hits["procurement"]),
                "binding_terms_total": str(bind_sum),
                "dei_terms_total": str(dei_sum),
                "priority_score": str(priority_score),
                "in_scope_priority": "yes" if in_scope else "no",
            }
        )
        out_rows.append(rr)

    out_rows.sort(
        key=lambda r: (
            1 if (r.get("in_scope_priority") == "yes") else 0,
            int(r.get("priority_score") or 0),
            int(r.get("risk_score") or 0),
            int(r.get("text_length") or 0),
        ),
        reverse=True,
    )

    # Write CSV
    fieldnames = list(out_rows[0].keys())
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    # Write Markdown subset (only in-scope priority)
    md_lines: list[str] = []
    md_lines.append("# Topic triage: risk_score > 0 (government + housing + finance + procurement)")
    md_lines.append("")
    md_lines.append(f"Generated: {datetime.now().isoformat(timespec='seconds')}")
    md_lines.append("")
    md_lines.append(f"Input rows: {len(rows)}")
    md_lines.append(f"In-scope priority rows: {counts_any}")
    md_lines.append("")
    md_lines.append("## Coverage")
    for t in ("government", "housing", "finance", "procurement"):
        md_lines.append(f"- {t}: {counts_by_topic[t]}")
    md_lines.append("")

    md_lines.append("## Priority list (in-scope only)")
    md_lines.append("")

    shown = 0
    for r in out_rows:
        if r.get("in_scope_priority") != "yes":
            continue
        shown += 1
        md_lines.append(f"### {r.get('document_id')} (priority={r.get('priority_score')}, risk={r.get('risk_score')})")
        md_lines.append(f"- Classification: {r.get('classification')}")
        if r.get("domain"):
            md_lines.append(f"- Domain: {r.get('domain')}")
        if r.get("content_type"):
            md_lines.append(f"- Content-Type: {r.get('content_type')}")
        if r.get("topic_tags"):
            md_lines.append(f"- Topic tags: {r.get('topic_tags')}")
        if r.get("title_guess"):
            md_lines.append(f"- Title guess: {r.get('title_guess')}")
        if r.get("url"):
            md_lines.append(f"- URL: {r.get('url')}")
        if r.get("summary_sentences"):
            md_lines.append("- Summary:")
            for s in (r.get("summary_sentences") or "").split(" | "):
                s = s.strip()
                if s:
                    md_lines.append(f"  - {s}")
        if r.get("binding_context"):
            md_lines.append("- Binding-language context snippets:")
            for s in (r.get("binding_context") or "").split(" | "):
                s = s.strip()
                if s:
                    md_lines.append(f"  - {s}")
        md_lines.append("")

        if shown >= 200:
            md_lines.append("(truncated after 200 items; use the CSV for the full set)")
            md_lines.append("")
            break

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    print("wrote", OUT_CSV)
    print("wrote", OUT_MD)
    print("in-scope priority rows", counts_any, "of", len(rows))


if __name__ == "__main__":
    main()
