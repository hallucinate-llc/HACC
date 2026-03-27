#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pypdf import PdfReader


REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_ROOT = REPO_ROOT / "evidence"
EMAIL_ROOT = EVIDENCE_ROOT / "email_imports"
AGENTIC_ROOT = EVIDENCE_ROOT / "agentic_downloads"
PAPER_ROOT = EVIDENCE_ROOT / "paper documents"
RESULTS_ROOT = REPO_ROOT / "research_results"
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"

if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_generator.email_graphrag import build_email_graphrag_artifacts  # noqa: E402

try:  # noqa: E402
    from complaint_phases.knowledge_graph import Entity, KnowledgeGraph, KnowledgeGraphBuilder, Relationship
except Exception:  # pragma: no cover - defensive fallback for partial environments
    Entity = None
    KnowledgeGraph = None
    KnowledgeGraphBuilder = None
    Relationship = None


RECENT_CLASS_KEYWORDS: list[tuple[str, tuple[str, ...]]] = [
    ("protected_status_or_vawa", ("vawa", "violence against women", "domestic violence")),
    ("case_caption_or_dispute", ("jane kay cortez", "solomon samuel barber", "cortez vs", " vs ")),
    ("orientation_or_compliance", ("orientation", "required signatures", "hcv", "voucher orientation")),
    ("application_or_intake", ("application", "vera", "intake", "eligibility")),
    ("program_policy_or_brochure", ("brochure", "administrative plan", "project based voucher", "relocation road map")),
    ("lease_or_occupancy", ("lease", "occupancy", "add to lease", "rent adjustment", "tenant")),
    ("inspection_or_unit_condition", ("inspection", "unit condition", "damages", "nspire")),
    ("notice_or_adverse_action", ("notice", "termination", "relocation", "adverse", "vacate", "90 day")),
    ("financial_verification", ("1040", "tax", "income", "asset", "bank", "coinbase", "financial", "additional information required")),
]

HIGH_SENSITIVITY_KEYWORDS = (
    "1040",
    "tax",
    "bank",
    "coinbase",
    "financial",
    "asset",
    "application",
    "vawa",
)

HOUSING_RELEVANCE_KEYWORDS = (
    "hacc",
    "housing",
    "voucher",
    "clackamas",
    "tenant",
    "lease",
    "orientation",
    "hearing",
    "accommodation",
    "vawa",
)

COMPLAINT_FOCUS_KEYWORDS = (
    "cortez",
    "barber",
    "clackamas",
    "housing",
    "hacc",
    "voucher",
    "lease",
    "termination",
    "notice",
    "inspection",
    "orientation",
    "accommodation",
    "relocation",
    "vawa",
    "blossom",
    "vera",
    "tilton",
    "callahan",
    "jane",
    "benjamin",
    "hud",
)

NOISE_ENTITY_KEYWORDS = (
    "linux foundation",
    "jp morgan",
    "chase bank",
    "hallucinate llc",
    "free standards group",
    "inifiniedge",
    "storacha prize",
    "coinbase",
)

LOW_SIGNAL_ENTITY_EXACT = (
    "hi benjamin",
    "hey benjamin",
    "reduction act notice",
    "automatic reply",
)

LOW_SIGNAL_ENTITY_PREFIXES = (
    "hi ",
    "hey ",
    "dear ",
    "re: ",
    "fw: ",
    "fwd: ",
)

MONTH_PATTERN = (
    r"(?:jan|january|feb|february|mar|march|apr|april|may|jun|june|jul|july|aug|august|"
    r"sep|sept|september|oct|october|nov|november|dec|december)"
)

LITIGATION_DATE_POSITIVE_KEYWORDS = (
    "notice",
    "termination",
    "eligibility",
    "displaced",
    "inspection",
    "orientation",
    "additional information",
    "action required",
    "dear jane",
    "dear resident",
    "hud",
    "resident",
    "vacate",
    "hearing",
    "relocation",
)

LITIGATION_DATE_NEGATIVE_KEYWORDS = (
    "printed on",
    "paperwork reduction",
    "privacy act",
    "instructions",
    "page ",
    "unit id",
    "annual",
    "interim",
    "occupation",
    "identity protection",
    "tax return",
    "signature",
    "form 1040",
)


@dataclass
class RecentPathRecord:
    path: str
    status: str
    commit: str
    committed_at: str
    subject: str


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return cleaned.strip("._-") or "item"


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_recent_git_paths(days: int) -> dict[str, RecentPathRecord]:
    cmd = [
        "git",
        "-C",
        str(REPO_ROOT),
        "log",
        f"--since={days} days ago",
        "--name-status",
        "--format=commit:%H%x09%cI%x09%s",
        "--",
        "evidence",
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError:
        return {}

    records: dict[str, RecentPathRecord] = {}
    current_commit = ""
    current_date = ""
    current_subject = ""
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        if line.startswith("commit:"):
            _, payload = line.split(":", 1)
            parts = payload.split("\t", 2)
            current_commit = parts[0] if len(parts) > 0 else ""
            current_date = parts[1] if len(parts) > 1 else ""
            current_subject = parts[2] if len(parts) > 2 else ""
            continue
        status, _, path = line.partition("\t")
        if not path:
            continue
        records.setdefault(
            path,
            RecentPathRecord(
                path=path,
                status=status.strip(),
                commit=current_commit,
                committed_at=current_date,
                subject=current_subject,
            ),
        )
    return records


def _extract_text_from_pdf(path: Path, max_pages: int = 8) -> dict[str, Any]:
    pages_read = 0
    page_texts: list[str] = []
    errors: list[str] = []
    try:
        reader = PdfReader(str(path))
        total_pages = len(reader.pages)
        for page in reader.pages[:max_pages]:
            pages_read += 1
            try:
                page_texts.append(page.extract_text() or "")
            except Exception as exc:  # pragma: no cover - per-page fallback
                errors.append(f"page_{pages_read}: {exc}")
    except Exception as exc:
        total_pages = 0
        errors.append(f"pypdf: {exc}")

    text = "\n".join(fragment for fragment in page_texts if fragment).strip()
    if text:
        return {
            "text": text,
            "pages_read": pages_read,
            "total_pages": total_pages,
            "extractor": "pypdf",
            "errors": errors,
        }

    pdftotext = shutil_which("pdftotext")
    if pdftotext:
        try:
            proc = subprocess.run(
                [pdftotext, "-f", "1", "-l", str(max_pages), str(path), "-"],
                capture_output=True,
                text=True,
                check=True,
            )
            text = proc.stdout.strip()
            if text:
                return {
                    "text": text,
                    "pages_read": max_pages,
                    "total_pages": total_pages,
                    "extractor": "pdftotext",
                    "errors": errors,
                }
        except Exception as exc:  # pragma: no cover - binary dependency fallback
            errors.append(f"pdftotext: {exc}")

    return {
        "text": "",
        "pages_read": pages_read,
        "total_pages": total_pages,
        "extractor": "none",
        "errors": errors,
    }


def shutil_which(command: str) -> str | None:
    for folder in os.environ.get("PATH", "").split(os.pathsep):
        candidate = Path(folder) / command
        if candidate.exists() and os.access(candidate, os.X_OK):
            return str(candidate)
    return None


def _classify_text(text: str, path_hint: str) -> dict[str, Any]:
    haystack = f"{path_hint}\n{text}".lower()
    matches: list[str] = []
    scored_matches: list[tuple[int, int, str]] = []
    for label, keywords in RECENT_CLASS_KEYWORDS:
        hit_count = sum(1 for keyword in keywords if keyword in haystack)
        if hit_count > 0:
            matches.append(label)
            scored_matches.append((hit_count, -len(matches), label))
    primary = max(scored_matches)[2] if scored_matches else "general_housing_evidence"
    sensitivity = "high" if any(keyword in haystack for keyword in HIGH_SENSITIVITY_KEYWORDS) else "medium"
    relevance_hits = sum(1 for keyword in HOUSING_RELEVANCE_KEYWORDS if keyword in haystack)
    if relevance_hits >= 5:
        relevance = "high"
    elif relevance_hits >= 2:
        relevance = "medium"
    else:
        relevance = "low"
    return {
        "primary_class": primary,
        "tags": matches,
        "sensitivity": sensitivity,
        "housing_relevance": relevance,
        "keyword_hit_count": relevance_hits,
    }


def _build_document_graphrag(path: Path, text: str) -> dict[str, Any]:
    graphrag_root = PAPER_ROOT / "graphrag" / _slugify(path.stem)
    graphrag_root.mkdir(parents=True, exist_ok=True)
    summary_path = graphrag_root / "document_graphrag_summary.json"
    if summary_path.exists():
        return _read_json(summary_path)

    if not text.strip() or KnowledgeGraphBuilder is None:
        summary = {
            "document_path": str(path),
            "graphrag_dir": str(graphrag_root),
            "status": "unavailable" if KnowledgeGraphBuilder is None else "empty_text",
            "knowledge_graph_summary": {},
        }
        summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        return summary

    graph = KnowledgeGraphBuilder().build_from_text(text[:60000])
    graph_path = graphrag_root / "document_knowledge_graph.json"
    graph.to_json(str(graph_path))
    summary = {
        "document_path": str(path),
        "graphrag_dir": str(graphrag_root),
        "status": "generated",
        "knowledge_graph_summary": graph.summary(),
        "graph_path": str(graph_path),
    }
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    return summary


def _summarize_snippet(text: str, limit: int = 220) -> str:
    cleaned = _clean_text(text)
    if len(cleaned) <= limit:
        return cleaned
    return cleaned[: limit - 3].rstrip() + "..."


def _graph_entity_text(entity: Entity) -> str:
    attributes = entity.attributes if isinstance(entity.attributes, dict) else {}
    parts = [str(entity.name or "")]
    for key in ("description", "event_label", "event_date_or_range", "content", "summary"):
        if key in attributes:
            parts.append(str(attributes.get(key) or ""))
    return _clean_text(" ".join(parts)).lower()


def _is_low_signal_entity(entity: Entity) -> bool:
    name = _clean_text(str(entity.name or "")).lower()
    if not name:
        return True
    if name in LOW_SIGNAL_ENTITY_EXACT:
        return True
    return any(name.startswith(prefix) for prefix in LOW_SIGNAL_ENTITY_PREFIXES)


def _parse_human_date(value: str) -> datetime | None:
    raw = _clean_text(value)
    if not raw:
        return None
    candidates = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d",
        "%B %d, %Y",
        "%b %d, %Y",
        "%m/%d/%Y",
        "%m/%d/%y",
    ]
    for fmt in candidates:
        try:
            parsed = datetime.strptime(raw, fmt)
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
        except ValueError:
            continue
    return None


def _parsed_date_in_scope(parsed: datetime) -> bool:
    minimum = datetime(2024, 1, 1, tzinfo=timezone.utc)
    maximum = datetime(2026, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    normalized = parsed.astimezone(timezone.utc)
    return minimum <= normalized <= maximum


def _extract_dates_from_text(text: str) -> list[str]:
    limited = text[:6000]
    patterns = [
        rf"\b{MONTH_PATTERN}\s+\d{{1,2}},\s+\d{{4}}\b",
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    matches: list[str] = []
    for pattern in patterns:
        for match in re.findall(pattern, limited, flags=re.IGNORECASE):
            cleaned = _clean_text(match)
            if cleaned not in matches:
                matches.append(cleaned)
    return matches


def _extract_scored_dates_from_text(text: str) -> list[dict[str, Any]]:
    limited = text[:6000]
    pattern = rf"\b(?:{MONTH_PATTERN}\s+\d{{1,2}},\s+\d{{4}}|\d{{4}}-\d{{2}}-\d{{2}}|\d{{1,2}}/\d{{1,2}}/\d{{2,4}})\b"
    scored: list[dict[str, Any]] = []
    for match in re.finditer(pattern, limited, flags=re.IGNORECASE):
        raw_date = _clean_text(match.group(0))
        parsed = _parse_human_date(raw_date)
        if parsed is None or not _parsed_date_in_scope(parsed):
            continue
        start = max(0, match.start() - 120)
        end = min(len(limited), match.end() + 120)
        context = _clean_text(limited[start:end]).lower()
        score = 0
        score += sum(2 for keyword in LITIGATION_DATE_POSITIVE_KEYWORDS if keyword in context)
        score -= sum(3 for keyword in LITIGATION_DATE_NEGATIVE_KEYWORDS if keyword in context)
        if raw_date.lower().startswith(("01/", "02/", "03/", "04/", "05/", "06/", "07/", "08/", "09/", "10/", "11/", "12/")):
            score += 0
        scored.append({
            "raw_date": raw_date,
            "parsed": parsed,
            "score": score,
            "context": context,
            "position": match.start(),
        })
    return scored


def _score_paper_dates_for_item(text: str, item: dict[str, Any]) -> list[dict[str, Any]]:
    stem = Path(str(item.get("path") or "")).stem.lower()
    adjusted: list[dict[str, Any]] = []
    for entry in _extract_scored_dates_from_text(text):
        score = int(entry.get("score") or 0)
        context = str(entry.get("context") or "")
        position = int(entry.get("position") or 0)

        if position <= 400:
            score += 3

        if "brochure" in stem:
            if any(keyword in context for keyword in (
                "annual plan",
                "board of commissioners",
                "mtw supplement",
                "scheduled for",
            )):
                score -= 8

        if "90 day notice" in stem or "steering" in stem:
            if any(keyword in context for keyword in (
                "effective date of your eligibility",
                "move by",
                "move out of this unit by",
                "must vacate your unit by",
                "vacate the residence by",
                "unit vacate date",
                "unit vacate da",
                "vacate deadline",
                "previously notified on",
                "still living in the unit after",
                "10 business days from the date of this notice",
                "within 10 business days from the date of this notice",
                "request a hearing",
                "your lease will be terminated on",
            )):
                score -= 8

        if "inspection" in stem:
            if any(keyword in context for keyword in (
                "entry to your unit",
                "notice mailed to resident",
            )):
                score -= 6

        updated = dict(entry)
        updated["score"] = score
        adjusted.append(updated)
    return adjusted


def _paper_timeline_item_is_general_reference(text: str, item: dict[str, Any]) -> bool:
    stem = Path(str(item.get("path") or "")).stem.lower()
    limited = _clean_text(text[:1600]).lower()
    if "brochure" in stem and any(keyword in limited for keyword in (
        "relocation road map",
        "annual plan",
        "board of commissioners",
        "mtw supplement",
    )):
        return True
    return False


def _select_paper_chronology_dates(text: str, item: dict[str, Any]) -> list[tuple[str, datetime]]:
    classifier = str(item.get("classification", {}).get("primary_class") or "")
    if _paper_timeline_item_is_general_reference(text, item):
        return []
    scored_dates = _score_paper_dates_for_item(text, item)
    if not scored_dates:
        return []

    limits = {
        "notice_or_adverse_action": 2,
        "lease_or_occupancy": 2,
        "inspection_or_unit_condition": 2,
        "financial_verification": 1,
        "orientation_or_compliance": 1,
        "protected_status_or_vawa": 1,
        "application_or_intake": 1,
    }
    minimum_score = {
        "notice_or_adverse_action": 1,
        "lease_or_occupancy": 1,
        "inspection_or_unit_condition": 1,
        "financial_verification": 2,
        "orientation_or_compliance": 2,
        "protected_status_or_vawa": 1,
        "application_or_intake": 1,
    }

    ranked = sorted(
        scored_dates,
        key=lambda entry: (entry["score"], -entry["parsed"].timestamp()),
        reverse=True,
    )
    selected: list[tuple[str, datetime]] = []
    seen_days: set[str] = set()
    threshold = minimum_score.get(classifier, 1)
    max_count = limits.get(classifier, 1)
    for entry in ranked:
        day_key = entry["parsed"].date().isoformat()
        if day_key in seen_days:
            continue
        if entry["score"] < threshold:
            continue
        seen_days.add(day_key)
        selected.append((str(entry["raw_date"]), entry["parsed"]))
        if len(selected) >= max_count:
            break

    if selected:
        selected.sort(key=lambda pair: pair[1])
        return selected

    fallback: list[tuple[str, datetime]] = []
    for entry in sorted(scored_dates, key=lambda entry: entry["parsed"]):
        day_key = entry["parsed"].date().isoformat()
        if day_key in seen_days:
            continue
        seen_days.add(day_key)
        fallback.append((str(entry["raw_date"]), entry["parsed"]))
        if len(fallback) >= 1:
            break
    return fallback


def _date_has_textual_month(raw_date: str) -> bool:
    return any(character.isalpha() for character in raw_date)


def _select_primary_paper_date(text: str, item: dict[str, Any]) -> tuple[str, datetime] | None:
    classifier = str(item.get("classification", {}).get("primary_class") or "")
    if _paper_timeline_item_is_general_reference(text, item):
        return None
    scored_dates = _score_paper_dates_for_item(text, item)
    if not scored_dates:
        return None

    direction = -1 if classifier in {
        "notice_or_adverse_action",
        "protected_status_or_vawa",
        "financial_verification",
        "orientation_or_compliance",
    } else 1

    ranked = sorted(
        scored_dates,
        key=lambda entry: (
            1 if _date_has_textual_month(str(entry["raw_date"])) else 0,
            entry["score"],
            direction * entry["parsed"].timestamp(),
        ),
        reverse=True,
    )
    best = ranked[0]
    return str(best["raw_date"]), best["parsed"]


def _build_pleading_timeline(payload: dict[str, Any], chronology_dir: Path) -> dict[str, Any]:
    items = _substantive_recent_items(list(payload.get("items") or []))
    selected: list[dict[str, Any]] = []
    email_seen: set[tuple[str, str]] = set()

    for item in items:
        path = REPO_ROOT / str(item.get("path") or "")
        if item.get("item_type") == "paper_pdf" and path.exists():
            extraction = _extract_text_from_pdf(path, max_pages=6)
            text = str(extraction.get("text") or "")
            chosen = _select_primary_paper_date(text, item)
            if chosen is None:
                continue
            raw_date, parsed = chosen
            selected.append({
                "date": raw_date,
                "sort_key": parsed.isoformat(),
                "source_path": str(item.get("path") or ""),
                "event_label": _event_label_for_item(item),
                "classification": item.get("classification", {}).get("primary_class"),
                "snippet": _summarize_snippet(text or item.get("snippet") or ""),
            })
            continue

        if item.get("item_type") == "email_manifest" and path.exists():
            manifest = _read_json(path)
            for email in list(manifest.get("emails") or [])[:20]:
                raw_date = str(email.get("date") or "").strip()
                parsed = _parse_human_date(raw_date)
                if parsed is None or not _parsed_date_in_scope(parsed):
                    continue
                subject = _normalize_email_subject(str(email.get("subject") or ""))
                if subject.lower().startswith("automatic reply"):
                    continue
                dedup_key = (parsed.date().isoformat(), subject)
                if dedup_key in email_seen:
                    continue
                email_seen.add(dedup_key)
                selected.append({
                    "date": raw_date,
                    "sort_key": parsed.isoformat(),
                    "source_path": str(item.get("path") or ""),
                    "event_label": f"Email thread: {subject}",
                    "classification": item.get("classification", {}).get("primary_class"),
                    "snippet": _summarize_snippet(
                        f"From {email.get('from') or ''} to {email.get('to') or ''} on {raw_date}"
                    ),
                })

    selected.sort(key=lambda event: (str(event.get("sort_key") or ""), str(event.get("source_path") or "")))
    json_path = chronology_dir / "pleading_timeline.json"
    md_path = chronology_dir / "pleading_timeline.md"
    summary = {
        "status": "success",
        "event_count": len(selected),
        "events": selected,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md_lines = ["# Pleading Timeline", "", f"Event count: {len(selected)}", ""]
    if selected:
        md_lines.extend(
            f"- {event.get('date')}: {event.get('event_label')} ({event.get('source_path')}) - {event.get('snippet')}"
            for event in selected
        )
    else:
        md_lines.append("- No pleading-ready events extracted.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _event_label_for_item(item: dict[str, Any]) -> str:
    path = str(item.get("path") or "")
    classifier = str(item.get("classification", {}).get("primary_class") or "")
    stem = Path(path).stem.replace("_", " ").replace("-", " ")
    if classifier == "notice_or_adverse_action":
        return f"Notice or adverse action: {stem}"
    if classifier == "lease_or_occupancy":
        return f"Lease or occupancy event: {stem}"
    if classifier == "financial_verification":
        return f"Financial verification request: {stem}"
    if classifier == "orientation_or_compliance":
        return f"Orientation or compliance event: {stem}"
    if classifier == "protected_status_or_vawa":
        return f"Protected-status or VAWA issue: {stem}"
    if classifier == "application_or_intake":
        return f"Application or intake event: {stem}"
    return stem


def _litigation_timeline_label(classification: str) -> str:
    mapping = {
        "notice_or_adverse_action": "Notices and adverse actions",
        "lease_or_occupancy": "Lease and occupancy",
        "inspection_or_unit_condition": "Inspection and unit condition",
        "financial_verification": "Financial verification",
        "orientation_or_compliance": "Orientation and compliance",
        "protected_status_or_vawa": "Protected-status and VAWA",
        "application_or_intake": "Application and intake",
    }
    return mapping.get(classification, "Other events")


def _normalize_email_subject(subject: str) -> str:
    normalized = _clean_text(subject)
    normalized = re.sub(r"^(?:re|fw|fwd):\s*", "", normalized, flags=re.IGNORECASE)
    return normalized or "Email"


def _build_litigation_timeline(events: list[dict[str, Any]], chronology_dir: Path) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    selected: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for event in events:
        classification = str(event.get("classification") or "")
        if classification == "general_housing_evidence":
            continue
        label = str(event.get("event_label") or "")
        source_path = str(event.get("source_path") or "")
        sort_key = str(event.get("sort_key") or "")
        if label.startswith("Email:"):
            subject = _normalize_email_subject(label.replace("Email:", "", 1).strip())
            if subject.lower().startswith("automatic reply"):
                continue
            dedup_key = (classification, sort_key[:10], subject)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
            event = dict(event)
            event["event_label"] = f"Email thread: {subject}"
        else:
            dedup_key = (classification, str(event.get("date") or ""), source_path)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)
        selected.append(event)
        grouped.setdefault(_litigation_timeline_label(classification), []).append(event)

    section_order = [
        "Notices and adverse actions",
        "Lease and occupancy",
        "Inspection and unit condition",
        "Financial verification",
        "Orientation and compliance",
        "Protected-status and VAWA",
        "Application and intake",
        "Other events",
    ]
    md_lines = ["# Litigation Timeline", "", f"Event count: {len(selected)}", ""]
    for section in section_order:
        section_events = grouped.get(section) or []
        if not section_events:
            continue
        md_lines.extend([f"## {section}", ""])
        for event in section_events:
            md_lines.append(
                f"- {event.get('date')}: {event.get('event_label')} ({event.get('source_path')}) - {event.get('snippet')}"
            )
        md_lines.append("")
    if not selected:
        md_lines.append("No litigation-style events extracted.")

    timeline_path = chronology_dir / "litigation_timeline.md"
    timeline_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return {
        "event_count": len(selected),
        "markdown_path": str(timeline_path),
        "sections": {section: len(grouped.get(section) or []) for section in section_order if grouped.get(section)},
    }


def _build_filtered_cross_document_graph(combined: KnowledgeGraph, loaded_sources: list[str], output_dir: Path) -> dict[str, Any]:
    cross_dir = output_dir / "cross_document"
    cross_dir.mkdir(parents=True, exist_ok=True)
    if KnowledgeGraph is None or Entity is None or Relationship is None:
        return {
            "status": "unavailable",
            "reason": "knowledge_graph_filtering_unavailable",
            "source_count": len(loaded_sources),
            "sources": loaded_sources,
        }

    connected_ids: set[str] = set()
    for rel in combined.relationships.values():
        connected_ids.add(rel.source_id)
        connected_ids.add(rel.target_id)

    keep_ids: set[str] = set()
    for entity in combined.entities.values():
        if _is_low_signal_entity(entity):
            continue
        text = _graph_entity_text(entity)
        has_focus = any(keyword in text for keyword in COMPLAINT_FOCUS_KEYWORDS)
        has_noise = any(keyword in text for keyword in NOISE_ENTITY_KEYWORDS)
        is_connected = entity.id in connected_ids
        confidence_ok = float(entity.confidence or 0.0) >= 0.72
        if has_noise:
            continue
        if entity.type == "claim" and is_connected:
            keep_ids.add(entity.id)
            continue
        if entity.type in {"person", "organization", "fact", "evidence"}:
            if has_focus and (confidence_ok or is_connected):
                keep_ids.add(entity.id)
            continue
        if entity.type == "date" and is_connected:
            parsed = _parse_human_date(str(entity.name or ""))
            if parsed is None or _parsed_date_in_scope(parsed):
                keep_ids.add(entity.id)

    filtered = KnowledgeGraph()
    for entity_id in keep_ids:
        entity = combined.entities.get(entity_id)
        if entity is not None:
            filtered.add_entity(entity)
    for rel in combined.relationships.values():
        if rel.source_id in keep_ids and rel.target_id in keep_ids:
            filtered.add_relationship(rel)

    filtered_graph_path = cross_dir / "cross_document_filtered_knowledge_graph.json"
    filtered_summary_path = cross_dir / "cross_document_filtered_summary.json"
    filtered_md_path = cross_dir / "cross_document_filtered_summary.md"
    filtered.to_json(str(filtered_graph_path))
    gaps = filtered.find_gaps()
    summary = {
        "status": "success",
        "source_count": len(loaded_sources),
        "sources": loaded_sources,
        "graph_path": str(filtered_graph_path),
        "knowledge_graph_summary": filtered.summary(),
        "gap_count": len(gaps),
        "gaps": gaps[:20],
        "filtering": {
            "kept_entities": len(filtered.entities),
            "kept_relationships": len(filtered.relationships),
            "dropped_entities": max(0, len(combined.entities) - len(filtered.entities)),
            "dropped_relationships": max(0, len(combined.relationships) - len(filtered.relationships)),
        },
    }
    filtered_summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md_lines = [
        "# Filtered Cross-Document Graph",
        "",
        f"Status: {summary['status']}",
        f"Source count: {summary['source_count']}",
        f"Total entities: {summary['knowledge_graph_summary'].get('total_entities', 0)}",
        f"Total relationships: {summary['knowledge_graph_summary'].get('total_relationships', 0)}",
        f"Dropped entities: {summary['filtering'].get('dropped_entities', 0)}",
        f"Dropped relationships: {summary['filtering'].get('dropped_relationships', 0)}",
        f"Gap count: {summary['gap_count']}",
        "",
        "## Gaps",
        "",
    ]
    if gaps:
        md_lines.extend(f"- {gap.get('type')}: {gap.get('suggested_question') or ''}" for gap in gaps[:20])
    else:
        md_lines.append("- No graph gaps reported.")
    filtered_md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    summary["summary_json_path"] = str(filtered_summary_path)
    summary["summary_markdown_path"] = str(filtered_md_path)
    return summary


def _build_chronology_report(payload: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    items = _substantive_recent_items(list(payload.get("items") or []))
    chronology_events: list[dict[str, Any]] = []
    for item in items:
        path = REPO_ROOT / str(item.get("path") or "")
        if item.get("item_type") == "paper_pdf" and path.exists():
            extraction = _extract_text_from_pdf(path, max_pages=6)
            text = str(extraction.get("text") or "")
            for raw_date, parsed in _select_paper_chronology_dates(text, item):
                chronology_events.append({
                    "date": raw_date,
                    "sort_key": parsed.isoformat(),
                    "source_path": str(item.get("path") or ""),
                    "event_label": _event_label_for_item(item),
                    "classification": item.get("classification", {}).get("primary_class"),
                    "snippet": _summarize_snippet(text or item.get("snippet") or ""),
                })
        elif item.get("item_type") == "email_manifest" and path.exists():
            manifest = _read_json(path)
            for email in list(manifest.get("emails") or [])[:20]:
                raw_date = str(email.get("date") or "").strip()
                if not raw_date:
                    continue
                parsed = _parse_human_date(raw_date)
                if parsed is None:
                    continue
                if not _parsed_date_in_scope(parsed):
                    continue
                chronology_events.append({
                    "date": raw_date,
                    "sort_key": parsed.isoformat(),
                    "source_path": str(item.get("path") or ""),
                    "event_label": f"Email: {str(email.get('subject') or '').strip() or item.get('folder')}",
                    "classification": item.get("classification", {}).get("primary_class"),
                    "snippet": _summarize_snippet(
                        f"From {email.get('from') or ''} to {email.get('to') or ''} on {raw_date}"
                    ),
                })

    chronology_events.sort(key=lambda event: (event.get("sort_key") or "", event.get("source_path") or ""))
    deduped: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for event in chronology_events:
        key = (str(event.get("date") or ""), str(event.get("event_label") or ""), str(event.get("source_path") or ""))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(event)

    chronology_dir = output_dir / "chronology"
    chronology_dir.mkdir(parents=True, exist_ok=True)
    json_path = chronology_dir / "chronology_report.json"
    md_path = chronology_dir / "chronology_report.md"
    summary = {
        "status": "success",
        "event_count": len(deduped),
        "events": deduped,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    md_lines = ["# Chronology Report", "", f"Event count: {len(deduped)}", "", "## Timeline", ""]
    if deduped:
        md_lines.extend(
            f"- {event.get('date')}: {event.get('event_label')} [{event.get('classification')}] ({event.get('source_path')}) - {event.get('snippet')}"
            for event in deduped
        )
    else:
        md_lines.append("- No chronology events extracted.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    summary["litigation_timeline"] = _build_litigation_timeline(deduped, chronology_dir)
    summary["pleading_timeline"] = _build_pleading_timeline(payload, chronology_dir)
    return summary


def _email_has_real_bundle(manifest: dict[str, Any], manifest_path: Path) -> bool:
    for email in manifest.get("emails") or []:
        bundle_dir_raw = str(email.get("bundle_dir") or "").strip()
        if not bundle_dir_raw or bundle_dir_raw == ".":
            continue
        bundle_dir = Path(bundle_dir_raw)
        if not bundle_dir.is_absolute():
            bundle_dir = manifest_path.parent / bundle_dir
        if (bundle_dir / "message.eml").exists() or (bundle_dir / "message.json").exists():
            return True
    return False


def _classify_email_manifest(manifest_path: Path, recent_paths: dict[str, RecentPathRecord]) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    relative_manifest = manifest_path.relative_to(REPO_ROOT).as_posix()
    folder_name = manifest_path.parent.name.lower()
    has_real_bundle = _email_has_real_bundle(manifest, manifest_path)
    existing_summary_path = manifest_path.parent / "graphrag" / "email_graphrag_summary.json"
    graphrag_status = "existing" if existing_summary_path.exists() else "missing"
    generated_summary: dict[str, Any] | None = None

    if graphrag_status == "missing" and has_real_bundle and "smoke" not in folder_name:
        try:
            generated_summary = build_email_graphrag_artifacts(manifest_path=manifest_path)
            graphrag_status = "generated"
        except Exception as exc:
            graphrag_status = f"error: {exc}"
    elif graphrag_status == "missing" and not has_real_bundle:
        graphrag_status = "skipped_preview_manifest"
    elif graphrag_status == "missing" and "smoke" in folder_name:
        graphrag_status = "skipped_smoke_manifest"

    summary_payload = generated_summary or (_read_json(existing_summary_path) if existing_summary_path.exists() else {})
    subject_text = " ".join(str(email.get("subject") or "") for email in manifest.get("emails") or [])
    attachment_names = " ".join(
        str(attachment.get("filename") or "")
        for email in manifest.get("emails") or []
        for attachment in email.get("attachments") or []
    )
    search_text = str(manifest.get("search") or "")
    classifier = _classify_text(f"{subject_text}\n{attachment_names}\n{search_text}", relative_manifest)
    if "smoke" in folder_name:
        source_tier = "test_or_noise"
    elif any(token in folder_name for token in ("preview", "crawl")) or not has_real_bundle:
        source_tier = "preview_or_cache_only"
    else:
        source_tier = "substantive_email_evidence"

    item_paths = [relative_manifest]
    item_paths.extend(
        path for path in recent_paths
        if path.startswith(f"{manifest_path.parent.relative_to(REPO_ROOT).as_posix()}/")
    )
    recent_matches = sorted(set(item_paths).intersection(recent_paths))
    is_recent = bool(recent_matches)

    return {
        "item_type": "email_manifest",
        "path": relative_manifest,
        "folder": manifest_path.parent.name,
        "is_recent": is_recent,
        "recent_paths": recent_matches,
        "matched_email_count": int(manifest.get("matched_email_count") or 0),
        "scanned_message_count": int(manifest.get("scanned_message_count") or 0),
        "has_real_bundle": has_real_bundle,
        "source_tier": source_tier,
        "classification": classifier,
        "graphrag_status": graphrag_status,
        "graphrag_summary": summary_payload,
        "snippet": _summarize_snippet(subject_text or search_text),
    }


def _classify_agentic_manifest(manifest_path: Path, recent_paths: dict[str, RecentPathRecord]) -> dict[str, Any]:
    manifest = _read_json(manifest_path)
    relative_manifest = manifest_path.relative_to(REPO_ROOT).as_posix()
    complaint_query = str(manifest.get("complaint_query") or "")
    classifier = _classify_text(complaint_query, relative_manifest)
    downloaded_count = int(manifest.get("downloaded_count") or 0)
    candidate_count = int(manifest.get("candidate_count") or 0)
    if downloaded_count > 0:
        source_tier = "downloaded_external_evidence"
    elif candidate_count > 0:
        source_tier = "download_candidates_only"
    else:
        source_tier = "external_research_gap"
    recent_matches = [path for path in recent_paths if path.startswith(f"{manifest_path.parent.relative_to(REPO_ROOT).as_posix()}/")]
    return {
        "item_type": "agentic_manifest",
        "path": relative_manifest,
        "folder": manifest_path.parent.name,
        "is_recent": bool(recent_matches),
        "recent_paths": recent_matches,
        "candidate_count": candidate_count,
        "downloaded_count": downloaded_count,
        "source_tier": source_tier,
        "classification": classifier,
        "graphrag_status": "not_applicable" if downloaded_count == 0 else "not_implemented",
        "snippet": _summarize_snippet(complaint_query),
        "quality": manifest.get("quality") or {},
    }


def _classify_paper_pdf(path: Path, recent_paths: dict[str, RecentPathRecord]) -> dict[str, Any]:
    relative_path = path.relative_to(REPO_ROOT).as_posix()
    extraction = _extract_text_from_pdf(path)
    text = str(extraction.get("text") or "")
    classifier = _classify_text(text or path.stem, relative_path)
    graphrag_summary = _build_document_graphrag(path, text)
    recent_matches = [relative_path] if relative_path in recent_paths else []
    source_tier = "substantive_paper_evidence"
    if not text.strip():
        source_tier = "binary_or_ocr_needed"
    return {
        "item_type": "paper_pdf",
        "path": relative_path,
        "folder": path.parent.name,
        "is_recent": bool(recent_matches),
        "recent_paths": recent_matches,
        "source_tier": source_tier,
        "classification": classifier,
        "graphrag_status": graphrag_summary.get("status") or "unknown",
        "graphrag_summary": graphrag_summary,
        "text_extraction": {
            "extractor": extraction.get("extractor"),
            "pages_read": extraction.get("pages_read"),
            "total_pages": extraction.get("total_pages"),
            "errors": extraction.get("errors") or [],
            "character_count": len(text),
        },
        "snippet": _summarize_snippet(text or path.stem),
    }


def _build_inventory(days: int) -> dict[str, Any]:
    recent_paths = _extract_recent_git_paths(days)
    items: list[dict[str, Any]] = []

    for manifest_path in sorted(EMAIL_ROOT.glob("*/email_import_manifest.json")):
        items.append(_classify_email_manifest(manifest_path, recent_paths))

    for manifest_path in sorted(AGENTIC_ROOT.glob("*/agentic_evidence_manifest.json")):
        items.append(_classify_agentic_manifest(manifest_path, recent_paths))

    for pdf_path in sorted(PAPER_ROOT.glob("*.pdf")):
        items.append(_classify_paper_pdf(pdf_path, recent_paths))

    recent_items = [item for item in items if item.get("is_recent")]
    substantive_recent = [
        item for item in recent_items
        if item.get("source_tier") in {"substantive_email_evidence", "substantive_paper_evidence", "binary_or_ocr_needed"}
    ]
    graph_generated = [item for item in items if str(item.get("graphrag_status") or "").startswith("generated")]
    graph_existing = [item for item in items if item.get("graphrag_status") == "existing"]
    graph_skipped = [
        item for item in items
        if str(item.get("graphrag_status") or "").startswith("skipped") or item.get("graphrag_status") == "not_applicable"
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "days": days,
        "recent_git_paths": [record.__dict__ for record in recent_paths.values()],
        "summary": {
            "inventory_count": len(items),
            "recent_item_count": len(recent_items),
            "recent_substantive_count": len(substantive_recent),
            "graphrag_generated_count": len(graph_generated),
            "graphrag_existing_count": len(graph_existing),
            "graphrag_skipped_count": len(graph_skipped),
        },
        "items": items,
    }


def _substantive_recent_items(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        item for item in items
        if item.get("is_recent")
        and item.get("source_tier") in {"substantive_email_evidence", "substantive_paper_evidence", "binary_or_ocr_needed"}
    ]


def _build_cross_document_graph(payload: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    items = list(payload.get("items") or [])
    substantive_items = _substantive_recent_items(items)
    graph_candidates: list[tuple[str, Path]] = []
    for item in substantive_items:
        summary = item.get("graphrag_summary") or {}
        graph_path_value = summary.get("graph_path")
        if not graph_path_value:
            continue
        graph_path = Path(str(graph_path_value))
        if graph_path.exists():
            graph_candidates.append((str(item.get("path") or ""), graph_path))

    if KnowledgeGraph is None:
        return {
            "status": "unavailable",
            "reason": "knowledge_graph_class_unavailable",
            "source_count": len(graph_candidates),
            "sources": [path for path, _ in graph_candidates],
        }

    if not graph_candidates:
        return {
            "status": "empty",
            "reason": "no_recent_substantive_graphs",
            "source_count": 0,
            "sources": [],
        }

    combined = KnowledgeGraph()
    loaded_sources: list[str] = []
    for source_path, graph_path in graph_candidates:
        try:
            graph = KnowledgeGraph.from_json(str(graph_path))
        except Exception:
            continue
        combined.merge_with(graph)
        loaded_sources.append(source_path)

    if not loaded_sources:
        return {
            "status": "empty",
            "reason": "graph_load_failed",
            "source_count": 0,
            "sources": [],
        }

    cross_dir = output_dir / "cross_document"
    cross_dir.mkdir(parents=True, exist_ok=True)
    graph_json_path = cross_dir / "cross_document_knowledge_graph.json"
    summary_json_path = cross_dir / "cross_document_summary.json"
    summary_md_path = cross_dir / "cross_document_summary.md"
    combined.to_json(str(graph_json_path))
    gaps = combined.find_gaps()
    filtered_summary = _build_filtered_cross_document_graph(combined, loaded_sources, output_dir)
    summary = {
        "status": "success",
        "source_count": len(loaded_sources),
        "sources": loaded_sources,
        "graph_path": str(graph_json_path),
        "knowledge_graph_summary": combined.summary(),
        "gap_count": len(gaps),
        "gaps": gaps[:20],
        "filtered_graph": filtered_summary,
    }
    summary_json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Cross-Document Graph",
        "",
        f"Status: {summary['status']}",
        f"Source count: {summary['source_count']}",
        f"Total entities: {summary['knowledge_graph_summary'].get('total_entities', 0)}",
        f"Total relationships: {summary['knowledge_graph_summary'].get('total_relationships', 0)}",
        f"Gap count: {summary['gap_count']}",
        "",
        "## Sources",
        "",
    ]
    md_lines.extend(f"- {source}" for source in loaded_sources)
    md_lines.extend(["", "## Gaps", ""])
    if gaps:
        md_lines.extend(
            f"- {gap.get('type')}: {gap.get('suggested_question') or ''}" for gap in gaps[:20]
        )
    else:
        md_lines.append("- No graph gaps reported.")
    summary_md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    summary["summary_json_path"] = str(summary_json_path)
    summary["summary_markdown_path"] = str(summary_md_path)
    return summary


def _markdown_report(payload: dict[str, Any]) -> str:
    lines: list[str] = []
    summary = payload.get("summary") or {}
    items = list(payload.get("items") or [])
    recent_items = [item for item in items if item.get("is_recent")]
    substantive_recent = _substantive_recent_items(items)
    substantive_recent.sort(
        key=lambda item: (
            0 if item.get("classification", {}).get("housing_relevance") == "high" else 1,
            item.get("item_type") != "paper_pdf",
            item.get("path", ""),
        )
    )

    lines.append("# Evidence Review")
    lines.append("")
    lines.append(f"Generated at: {payload.get('generated_at')}")
    lines.append(f"Inventory count: {summary.get('inventory_count', 0)}")
    lines.append(f"Recent item count: {summary.get('recent_item_count', 0)}")
    lines.append(f"Recent substantive evidence count: {summary.get('recent_substantive_count', 0)}")
    lines.append(f"GraphRAG generated this run: {summary.get('graphrag_generated_count', 0)}")
    lines.append(f"GraphRAG already present: {summary.get('graphrag_existing_count', 0)}")
    lines.append(f"GraphRAG skipped or not applicable: {summary.get('graphrag_skipped_count', 0)}")
    cross_doc = payload.get("cross_document_graph") or {}
    if cross_doc:
        lines.append(f"Cross-document graph status: {cross_doc.get('status')}")
        lines.append(f"Cross-document graph sources: {cross_doc.get('source_count', 0)}")
        filtered = cross_doc.get("filtered_graph") or {}
        if filtered:
            lines.append(f"Filtered cross-document graph entities: {filtered.get('knowledge_graph_summary', {}).get('total_entities', 0)}")
    lines.append("")
    lines.append("## Recent Substantive Evidence")
    lines.append("")
    if not substantive_recent:
        lines.append("No substantive evidence items were added in the selected window.")
    else:
        for item in substantive_recent:
            classifier = item.get("classification") or {}
            lines.append(
                "- "
                f"{item.get('path')}: class={classifier.get('primary_class')}, "
                f"relevance={classifier.get('housing_relevance')}, "
                f"graphrag={item.get('graphrag_status')}, "
                f"snippet={item.get('snippet') or 'n/a'}"
            )
    lines.append("")
    lines.append("## Review Notes")
    lines.append("")

    preview_count = sum(1 for item in items if item.get("source_tier") == "preview_or_cache_only")
    gap_count = sum(1 for item in items if item.get("source_tier") == "external_research_gap")
    binary_count = sum(1 for item in items if item.get("source_tier") == "binary_or_ocr_needed")
    lines.append(f"- Preview or cache-only email manifests: {preview_count}")
    lines.append("- Preview manifests cannot be promoted into substantive GraphRAG from the current repo state because the cache index stores metadata only, not saved message bodies.")
    lines.append(f"- Agentic download runs with no harvested evidence: {gap_count}")
    lines.append(f"- Paper PDFs that may still need OCR review: {binary_count}")
    if cross_doc:
        lines.append(f"- Cross-document graph summary: {cross_doc.get('knowledge_graph_summary', {}).get('total_entities', 0)} entities, {cross_doc.get('knowledge_graph_summary', {}).get('total_relationships', 0)} relationships.")
        filtered = cross_doc.get("filtered_graph") or {}
        if filtered:
            lines.append(f"- Filtered graph summary: {filtered.get('knowledge_graph_summary', {}).get('total_entities', 0)} entities, {filtered.get('knowledge_graph_summary', {}).get('total_relationships', 0)} relationships.")
    chronology = payload.get("chronology_report") or {}
    if chronology:
        lines.append(f"- Chronology report events extracted: {chronology.get('event_count', 0)}")
        litigation = chronology.get("litigation_timeline") or {}
        if litigation:
            lines.append(f"- Litigation timeline events extracted: {litigation.get('event_count', 0)}")
        pleading = chronology.get("pleading_timeline") or {}
        if pleading:
            lines.append(f"- Pleading timeline events extracted: {pleading.get('event_count', 0)}")
    return "\n".join(lines).strip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Review recent evidence and classify the current evidence inventory.")
    parser.add_argument("--days", type=int, default=7, help="Window for recent evidence review.")
    parser.add_argument("--output-dir", default="", help="Optional output directory under research_results.")
    args = parser.parse_args(argv)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    if args.output_dir:
        output_dir = Path(args.output_dir).expanduser().resolve()
    else:
        output_dir = RESULTS_ROOT / f"evidence_review_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)

    payload = _build_inventory(args.days)
    payload["cross_document_graph"] = _build_cross_document_graph(payload, output_dir)
    payload["chronology_report"] = _build_chronology_report(payload, output_dir)
    json_path = output_dir / "evidence_review.json"
    md_path = output_dir / "evidence_review.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(_markdown_report(payload), encoding="utf-8")

    print(
        json.dumps(
            {
                "status": "success",
                "output_dir": str(output_dir),
                "json_report": str(json_path),
                "markdown_report": str(md_path),
                "summary": payload.get("summary") or {},
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())