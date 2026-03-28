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
    raw = _normalize_ocr_month_tokens(_clean_text(value))
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


def _normalize_ocr_month_tokens(text: str) -> str:
    normalized = text
    for month in (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ):
        pattern = r"\b" + r"\s*".join(re.escape(char) for char in month) + r"\b"
        normalized = re.sub(pattern, month, normalized, flags=re.IGNORECASE)
    return normalized


def _extract_dates_from_text(text: str) -> list[str]:
    limited = _normalize_ocr_month_tokens(text[:6000])
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
    limited = _normalize_ocr_month_tokens(text[:6000])
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

        if "on or about" in context:
            score -= 6

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

        if "first amendment" in stem:
            if any(keyword in context for keyword in (
                "option to cure",
                "vacate premises by",
                "lease termination notice with option to cure",
                "upon delivery of this notice",
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


def _source_display_name(source_path: str) -> str:
    return Path(source_path).stem.replace("_", " ").replace("-", " ")


def _clean_fact_text(text: str) -> str:
    cleaned = _clean_text(text).rstrip(".")
    cleaned = cleaned.replace("...", "")
    return cleaned.strip()


def _format_fact_date(raw_date: str) -> str:
    parsed = _parse_human_date(raw_date)
    if parsed is None:
        return raw_date
    if "T" in raw_date:
        return parsed.strftime("%B %d, %Y at %I:%M %p %z")
    return raw_date


def _excerpt_for_pleading(snippet: str, limit: int = 180) -> str:
    cleaned = _clean_fact_text(snippet)
    if len(cleaned) <= limit:
        return cleaned
    truncated = cleaned[: limit - 1].rsplit(" ", 1)[0].strip()
    return f"{truncated}..."


def _email_participants(snippet: str) -> tuple[str, str] | None:
    match = re.search(r"From\s+(.+?)\s+to\s+(.+?)\s+on\s+", snippet, flags=re.IGNORECASE)
    if not match:
        return None
    sender = _clean_text(match.group(1))
    recipient = _clean_text(match.group(2))
    return sender, recipient


def _document_fact_prefix(classification: str, title: str) -> str:
    if classification == "notice_or_adverse_action":
        return f"the document \"{title}\" reflects a notice or adverse action"
    if classification == "lease_or_occupancy":
        return f"the document \"{title}\" reflects a lease or occupancy event"
    if classification == "financial_verification":
        return f"the document \"{title}\" reflects a financial verification request"
    if classification == "orientation_or_compliance":
        return f"the document \"{title}\" reflects an orientation or compliance event"
    if classification == "protected_status_or_vawa":
        return f"the document \"{title}\" reflects a protected-status or VAWA-related issue"
    if classification == "application_or_intake":
        return f"the document \"{title}\" reflects an application or intake event"
    return f"the document \"{title}\" reflects a relevant event"


def _allegation_section_title(classification: str) -> str:
    mapping = {
        "notice_or_adverse_action": "Notices and Adverse Actions",
        "lease_or_occupancy": "Lease and Occupancy",
        "financial_verification": "Financial Verification and Intake Barriers",
        "orientation_or_compliance": "Orientation and Compliance",
        "protected_status_or_vawa": "Protected Status and VAWA",
        "application_or_intake": "Application and Intake",
    }
    return mapping.get(classification, "Other Supporting Facts")


def _cause_of_action_title(section_title: str) -> str:
    mapping = {
        "Notices and Adverse Actions": "Potential Claim Theme: Deficient Notice and Adverse Housing Action",
        "Lease and Occupancy": "Potential Claim Theme: Lease, Occupancy, and Displacement Conduct",
        "Financial Verification and Intake Barriers": "Potential Claim Theme: Documentation Demands and Intake Barriers",
        "Protected Status and VAWA": "Potential Claim Theme: Protected Status and VAWA-Related Conduct",
        "Orientation and Compliance": "Potential Claim Theme: Orientation and Compliance Delays",
        "Application and Intake": "Potential Claim Theme: Application and Intake Process Issues",
        "Other Supporting Facts": "Potential Claim Theme: Additional Supporting Facts",
    }
    return mapping.get(section_title, f"Potential Claim Theme: {section_title}")


def _cause_of_action_intro(section_title: str) -> str:
    mapping = {
        "Notices and Adverse Actions": "These facts support a draft theory that HACC issued or escalated adverse housing actions through notices and displacement-related communications.",
        "Lease and Occupancy": "These facts support a draft theory centered on lease amendments, occupancy changes, inspections, and relocation-related housing conditions.",
        "Financial Verification and Intake Barriers": "These facts support a draft theory that repeated documentation demands and related email exchanges created material barriers in the housing process.",
        "Protected Status and VAWA": "These facts support a draft theory that protected-status and VAWA-related issues were implicated in later housing actions.",
        "Orientation and Compliance": "These facts support a draft theory that orientation and compliance requirements became a distinct procedural track affecting housing progression.",
        "Application and Intake": "These facts support a draft theory involving application and intake-stage process defects.",
        "Other Supporting Facts": "These facts may support additional claim development after manual review.",
    }
    return mapping.get(section_title, "These facts may support additional claim development after manual review.")


def _cause_of_action_element_prompts(section_title: str) -> list[str]:
    mapping = {
        "Notices and Adverse Actions": [
            "Identify the specific notice requirements imposed by the lease, program rules, ORS chapter 90, HUD guidance, or relocation rules.",
            "State how the notices were deficient, inconsistent, untimely, or misleading.",
            "Explain the concrete housing harm threatened or imposed by the adverse action.",
        ],
        "Lease and Occupancy": [
            "Identify the lease, occupancy, inspection, transfer, or displacement obligation at issue.",
            "State how HACC's conduct departed from that obligation or from ordinary housing process requirements.",
            "Explain the resulting loss of housing stability, access, or tenancy rights.",
        ],
        "Financial Verification and Intake Barriers": [
            "Describe the specific documentation demands or intake conditions imposed on plaintiff.",
            "State why those demands were unreasonable, inconsistently applied, retaliatory, discriminatory, or otherwise improper.",
            "Explain how the demands delayed, burdened, or obstructed housing access or retention.",
        ],
        "Protected Status and VAWA": [
            "Identify the protected status, VAWA protection, or related legal protection implicated by the facts.",
            "Connect the protected status facts to the challenged notice, lease action, or housing decision.",
            "State the resulting discriminatory, retaliatory, or procedurally unlawful harm.",
        ],
        "Orientation and Compliance": [
            "Identify the orientation or compliance requirement and the source of that requirement.",
            "Explain how the timing or administration of the requirement affected plaintiff's housing position.",
            "State the concrete delay, denial, or prejudice caused by that process.",
        ],
        "Application and Intake": [
            "Identify the application or intake rule at issue.",
            "State how the process was mishandled or inconsistently applied.",
            "Explain the resulting denial, delay, or loss of housing opportunity.",
        ],
        "Other Supporting Facts": [
            "State how these facts connect to a recognized claim or defense.",
            "Explain the injury or prejudice flowing from those facts.",
        ],
    }
    return mapping.get(section_title, [
        "State the governing rule or duty.",
        "State how the conduct violated that rule or duty.",
        "State the resulting harm.",
    ])


def _classification_narrative_phrase(classification: str) -> str:
    mapping = {
        "notice_or_adverse_action": "a notice or adverse housing action",
        "lease_or_occupancy": "a lease, occupancy, inspection, or displacement-related housing event",
        "financial_verification": "a documentation or financial verification demand",
        "orientation_or_compliance": "an orientation or compliance requirement",
        "protected_status_or_vawa": "a protected-status or VAWA-related housing issue",
        "application_or_intake": "an application or intake event",
    }
    return mapping.get(classification, "a relevant housing-related event")


def _narrative_fact_from_entry(entry: dict[str, Any]) -> str:
    paragraph = str(entry.get("paragraph") or "").strip()
    if paragraph.startswith("Between "):
        return paragraph
    classification = str(entry.get("classification") or "")
    source_path = str(entry.get("source_path") or "")
    date = _format_fact_date(str(entry.get("date") or ""))
    title = _source_display_name(source_path)
    phrase = _classification_narrative_phrase(classification)
    return (
        f"On {date}, HACC generated or used the document \"{title}\" in connection with {phrase}. "
        f"Source: {source_path}."
    )


def _entry_is_email(entry: dict[str, Any]) -> bool:
    return str(entry.get("event_label") or "").startswith("Email thread:")


def _entry_email_subject(entry: dict[str, Any]) -> str:
    label = str(entry.get("event_label") or "")
    return label.replace("Email thread:", "", 1).strip() or "Email"


def _entry_date_for_grouping(entry: dict[str, Any]) -> datetime | None:
    return _parse_human_date(str(entry.get("date") or ""))


def _extract_email_participants_from_paragraph(paragraph: str) -> tuple[str, str] | None:
    match = re.search(r"was sent from\s+(.+?)\s+to\s+(.+?)\.\s+Source:", paragraph, flags=re.IGNORECASE)
    if not match:
        return None
    return _clean_text(match.group(1)), _clean_text(match.group(2))


def _format_grouped_date(parsed: datetime | None) -> str:
    if parsed is None:
        return ""
    return parsed.strftime("%B %d, %Y")


def _participants_summary(entries: list[dict[str, Any]]) -> str:
    participants: list[str] = []
    for entry in entries:
        parsed = _extract_email_participants_from_paragraph(str(entry.get("paragraph") or ""))
        if not parsed:
            continue
        sender, recipient = parsed
        for participant in (sender, recipient):
            if participant not in participants:
                participants.append(participant)
    if not participants:
        return "the captured participants"
    if len(participants) == 1:
        return participants[0]
    if len(participants) == 2:
        return f"{participants[0]} and {participants[1]}"
    preview = ", ".join(participants[:3])
    if len(participants) > 3:
        return f"{preview}, and others"
    return preview


def _compress_email_entries(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    compressed: list[dict[str, Any]] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        if not _entry_is_email(entry):
            compressed.append(entry)
            index += 1
            continue

        subject = _entry_email_subject(entry)
        classification = str(entry.get("classification") or "")
        source_path = str(entry.get("source_path") or "")
        group = [entry]
        look_ahead = index + 1
        while look_ahead < len(entries):
            candidate = entries[look_ahead]
            if not _entry_is_email(candidate):
                break
            if _entry_email_subject(candidate) != subject:
                break
            if str(candidate.get("classification") or "") != classification:
                break
            if str(candidate.get("source_path") or "") != source_path:
                break
            group.append(candidate)
            look_ahead += 1

        if len(group) == 1:
            compressed.append(entry)
            index = look_ahead
            continue

        first_date = _entry_date_for_grouping(group[0])
        last_date = _entry_date_for_grouping(group[-1])
        date_span = _format_grouped_date(first_date)
        last_date_text = _format_grouped_date(last_date)
        if last_date_text and last_date_text != date_span:
            date_span = f"{date_span} and {last_date_text}"
        participants = _participants_summary(group)
        summary_entry = dict(group[0])
        summary_entry["paragraph"] = (
            f"Between {date_span}, the email thread \"{subject}\" included {len(group)} captured messages involving {participants}. "
            f"Source: {source_path}."
        )
        compressed.append(summary_entry)
        index = look_ahead

    return compressed


def _build_complaint_ready_chronology(pleading_timeline: dict[str, Any], chronology_dir: Path) -> dict[str, Any]:
    events = list(pleading_timeline.get("events") or [])
    json_path = chronology_dir / "complaint_ready_chronology.json"
    md_path = chronology_dir / "complaint_ready_chronology.md"

    paragraphs: list[dict[str, Any]] = []
    for index, event in enumerate(events, start=1):
        raw_date = str(event.get("date") or "")
        date = _format_fact_date(raw_date)
        source_path = str(event.get("source_path") or "")
        label = str(event.get("event_label") or _source_display_name(source_path))
        snippet = _clean_fact_text(str(event.get("snippet") or ""))
        classification = str(event.get("classification") or "")
        if label.startswith("Email thread:"):
            subject = label.replace("Email thread:", "", 1).strip() or "Email"
            participants = _email_participants(snippet)
            if participants:
                sender, recipient = participants
                sentence = (
                    f"On {date}, an email regarding \"{subject}\" was sent from {sender} to {recipient}. "
                    f"Source: {source_path}."
                )
            else:
                sentence = (
                    f"On {date}, an email thread regarding \"{subject}\" reflects: \"{_excerpt_for_pleading(snippet)}\". "
                    f"Source: {source_path}."
                )
        else:
            title = _source_display_name(source_path)
            prefix = _document_fact_prefix(classification, title)
            sentence = (
                f"On {date}, {prefix} stating: \"{_excerpt_for_pleading(snippet)}\". "
                f"Source: {source_path}."
            )
        paragraphs.append({
            "number": index,
            "date": raw_date,
            "source_path": source_path,
            "event_label": label,
            "classification": classification,
            "paragraph": sentence,
        })

    summary = {
        "status": "success",
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = ["# Complaint-Ready Chronology", "", f"Paragraph count: {len(paragraphs)}", ""]
    if paragraphs:
        md_lines.extend(f"{entry['number']}. {entry['paragraph']}" for entry in paragraphs)
    else:
        md_lines.append("No complaint-ready chronology paragraphs generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_claim_grouped_allegations(complaint_ready: dict[str, Any], chronology_dir: Path) -> dict[str, Any]:
    paragraphs = list(complaint_ready.get("paragraphs") or [])
    grouped: dict[str, list[dict[str, Any]]] = {}
    for paragraph in paragraphs:
        classification = str(paragraph.get("classification") or "")
        grouped.setdefault(_allegation_section_title(classification), []).append(paragraph)

    section_order = [
        "Notices and Adverse Actions",
        "Lease and Occupancy",
        "Financial Verification and Intake Barriers",
        "Protected Status and VAWA",
        "Orientation and Compliance",
        "Application and Intake",
        "Other Supporting Facts",
    ]
    json_path = chronology_dir / "claim_grouped_allegations.json"
    md_path = chronology_dir / "claim_grouped_allegations.md"

    sections: list[dict[str, Any]] = []
    for title in section_order:
        entries = grouped.get(title) or []
        if not entries:
            continue
        sections.append({
            "title": title,
            "paragraph_count": len(entries),
            "paragraphs": entries,
        })

    summary = {
        "status": "success",
        "section_count": len(sections),
        "paragraph_count": len(paragraphs),
        "sections": sections,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = ["# Claim-Grouped Allegations", "", f"Section count: {len(sections)}", f"Paragraph count: {len(paragraphs)}", ""]
    if sections:
        for section in sections:
            md_lines.extend([f"## {section['title']}", ""])
            md_lines.extend(f"{entry['number']}. {entry['paragraph']}" for entry in section["paragraphs"])
            md_lines.append("")
    else:
        md_lines.append("No claim-grouped allegations generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_cause_of_action_draft(grouped_allegations: dict[str, Any], chronology_dir: Path) -> dict[str, Any]:
    sections = list(grouped_allegations.get("sections") or [])
    json_path = chronology_dir / "cause_of_action_draft.json"
    md_path = chronology_dir / "cause_of_action_draft.md"

    drafted_sections: list[dict[str, Any]] = []
    for section in sections:
        section_paragraphs = _compress_email_entries(list(section.get("paragraphs") or []))
        section_title = str(section.get("title") or "Other Supporting Facts")
        drafted_sections.append({
            "title": _cause_of_action_title(section_title),
            "source_section": section_title,
            "intro": _cause_of_action_intro(section_title),
            "element_prompts": _cause_of_action_element_prompts(section_title),
            "paragraph_count": len(section_paragraphs),
            "paragraphs": section_paragraphs,
        })

    summary = {
        "status": "success",
        "section_count": len(drafted_sections),
        "paragraph_count": sum(int(section.get("paragraph_count") or 0) for section in drafted_sections),
        "sections": drafted_sections,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = ["# Cause-of-Action Draft", "", f"Section count: {len(drafted_sections)}", ""]
    if drafted_sections:
        for section in drafted_sections:
            md_lines.extend([
                f"## {section['title']}",
                "",
                section["intro"],
                "",
                f"Source allegation group: {section['source_section']}",
                "",
                "Elements to Plead:",
                "",
            ])
            md_lines.extend(f"- {prompt}" for prompt in section["element_prompts"])
            md_lines.append("")
            md_lines.extend(f"{entry['number']}. {entry['paragraph']}" for entry in section["paragraphs"])
            md_lines.append("")
    else:
        md_lines.append("No cause-of-action draft sections generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_complaint_skeleton(cause_draft: dict[str, Any], complaint_ready: dict[str, Any], chronology_dir: Path) -> dict[str, Any]:
    cause_sections = list(cause_draft.get("sections") or [])
    chronology_paragraphs = _compress_email_entries(list(complaint_ready.get("paragraphs") or []))
    json_path = chronology_dir / "complaint_skeleton.json"
    md_path = chronology_dir / "complaint_skeleton.md"

    factual_background = chronology_paragraphs[: min(12, len(chronology_paragraphs))]
    cause_blocks = []
    for section in cause_sections:
        cause_blocks.append({
            "title": str(section.get("title") or "Potential Claim Theme"),
            "intro": str(section.get("intro") or ""),
            "source_section": str(section.get("source_section") or ""),
            "element_prompts": list(section.get("element_prompts") or []),
            "paragraphs": list(section.get("paragraphs") or []),
        })

    summary = {
        "status": "success",
        "cause_section_count": len(cause_blocks),
        "factual_background_count": len(factual_background),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(
        json.dumps(
            {
                **summary,
                "factual_background": factual_background,
                "cause_sections": cause_blocks,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    md_lines = [
        "# Complaint Skeleton",
        "",
        "## Caption",
        "",
        "[Plaintiff],",
        "",
        "v.",
        "",
        "Housing Authority of Clackamas County and Doe Defendants,",
        "",
        "## Preliminary Statement",
        "",
        "This draft skeleton organizes the currently extracted evidence into pleading-ready sections. It is a drafting aid and should be checked against the underlying evidence before filing.",
        "",
        "## Parties",
        "",
        "1. Plaintiff: [fill in].",
        "2. Defendant Housing Authority of Clackamas County: [fill in].",
        "3. Additional defendants if supported by evidence: [fill in].",
        "",
        "## Jurisdiction and Venue",
        "",
        "1. Jurisdiction basis: [fill in].",
        "2. Venue basis: [fill in].",
        "",
        "## Factual Background",
        "",
    ]
    if factual_background:
        md_lines.extend(f"{entry['number']}. {entry['paragraph']}" for entry in factual_background)
    else:
        md_lines.append("No factual background paragraphs generated.")

    md_lines.extend(["", "## Causes of Action", ""])
    if cause_blocks:
        for idx, block in enumerate(cause_blocks, start=1):
            md_lines.extend([
                f"### Count {idx}: {block['title']}",
                "",
                block["intro"],
                "",
                f"Supporting source group: {block['source_section']}",
                "",
                "Elements to Plead:",
            ])
            md_lines.extend(f"- {prompt}" for prompt in block["element_prompts"])
            md_lines.append("")
            md_lines.extend(f"{entry['number']}. {entry['paragraph']}" for entry in block["paragraphs"])
            md_lines.extend([
                "",
                "Requested theory language: [fill in legal elements and requested relief].",
                "",
            ])
    else:
        md_lines.append("No cause-of-action sections generated.")

    md_lines.extend([
        "## Prayer for Relief",
        "",
        "1. Declaratory relief: [fill in].",
        "2. Injunctive relief: [fill in].",
        "3. Damages, fees, and costs if applicable: [fill in].",
        "",
        "## Jury Demand",
        "",
        "[Fill in if applicable].",
    ])
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_narrative_complaint_draft(
    complaint_ready: dict[str, Any],
    cause_draft: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    factual_entries = _compress_email_entries(list(complaint_ready.get("paragraphs") or []))
    cause_sections = list(cause_draft.get("sections") or [])
    json_path = chronology_dir / "narrative_complaint_draft.json"
    md_path = chronology_dir / "narrative_complaint_draft.md"

    factual_background = [_narrative_fact_from_entry(entry) for entry in factual_entries[:10]]
    count_summaries = []
    for section in cause_sections:
        entries = list(section.get("paragraphs") or [])
        count_summaries.append({
            "title": str(section.get("title") or "Potential Claim Theme"),
            "intro": str(section.get("intro") or ""),
            "element_prompts": list(section.get("element_prompts") or []),
            "facts": [_narrative_fact_from_entry(entry) for entry in entries[:3]],
        })

    summary = {
        "status": "success",
        "factual_background_count": len(factual_background),
        "count_count": len(count_summaries),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
    json_path.write_text(
        json.dumps(
            {
                **summary,
                "factual_background": factual_background,
                "counts": count_summaries,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    md_lines = [
        "# Narrative Complaint Draft",
        "",
        "## Preliminary Statement",
        "",
        "This narrative draft converts the extracted evidence into shorter pleading-style prose. It remains a drafting aid and should be checked against the underlying evidence before filing.",
        "",
        "## Factual Allegations",
        "",
    ]
    if factual_background:
        md_lines.extend(f"{index}. {fact}" for index, fact in enumerate(factual_background, start=1))
    else:
        md_lines.append("No factual allegations generated.")

    md_lines.extend(["", "## Counts", ""])
    if count_summaries:
        for idx, count in enumerate(count_summaries, start=1):
            md_lines.extend([
                f"### Count {idx}: {count['title']}",
                "",
                count["intro"],
                "",
                "Elements to Plead:",
            ])
            md_lines.extend(f"- {prompt}" for prompt in count["element_prompts"])
            md_lines.extend(["", "Representative Allegations:"])
            md_lines.extend(f"- {fact}" for fact in count["facts"])
            md_lines.extend(["", "Draft theory paragraph: [fill in].", ""])
    else:
        md_lines.append("No count summaries generated.")

    md_lines.extend([
        "## Relief Requested",
        "",
        "- Declaratory relief: [fill in].",
        "- Injunctive relief: [fill in].",
        "- Damages, fees, and costs if applicable: [fill in].",
    ])
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _roman_count_label(value: int) -> str:
    numerals = {
        1: "I",
        2: "II",
        3: "III",
        4: "IV",
        5: "V",
        6: "VI",
        7: "VII",
        8: "VIII",
        9: "IX",
        10: "X",
    }
    return numerals.get(value, str(value))


def _alpha_exhibit_label(value: int) -> str:
    if value <= 0:
        return str(value)
    label = ""
    current = value
    while current > 0:
        current -= 1
        label = chr(ord("A") + (current % 26)) + label
        current //= 26
    return label


def _build_exhibit_map(
    factual_entries: list[dict[str, Any]],
    cause_sections: list[dict[str, Any]],
) -> dict[str, str]:
    ordered_paths: list[str] = []
    for entry in factual_entries:
        source_path = str(entry.get("source_path") or "")
        if source_path and source_path not in ordered_paths:
            ordered_paths.append(source_path)
    for section in cause_sections:
        for entry in list(section.get("paragraphs") or []):
            source_path = str(entry.get("source_path") or "")
            if source_path and source_path not in ordered_paths:
                ordered_paths.append(source_path)
    return {
        source_path: _alpha_exhibit_label(index)
        for index, source_path in enumerate(ordered_paths, start=1)
    }


def _paragraph_with_exhibit_tag(paragraph: str, exhibit_label: str | None) -> str:
    if not exhibit_label:
        return paragraph
    stripped = paragraph.rstrip()
    if stripped.endswith("."):
        return stripped[:-1] + f" [Exhibit {exhibit_label}]."
    return stripped + f" [Exhibit {exhibit_label}]"


def _source_type_for_path(source_path: str) -> str:
    lowered = source_path.lower()
    if lowered.endswith(".pdf"):
        return "paper_pdf"
    if lowered.endswith("email_import_manifest.json"):
        return "email_manifest"
    if lowered.endswith(".json"):
        return "json_record"
    return "file"


def _suggested_exhibit_title(source_path: str, source_name: str) -> str:
    source_type = _source_type_for_path(source_path)
    if source_type == "paper_pdf":
        return f"{source_name} PDF"
    if source_type == "email_manifest":
        parent = Path(source_path).parent.name.replace("-", " ")
        return f"Email Thread Export: {parent}"
    return source_name


def _exhibit_handling_note(source_path: str) -> str:
    source_type = _source_type_for_path(source_path)
    if source_type == "paper_pdf":
        return "Attach the underlying PDF as the exhibit file."
    if source_type == "email_manifest":
        return "Use the manifest with underlying saved messages or representative thread exports; see the email exhibit manifest for message-level detail."
    return "Verify filing format before attaching this source."


def _subexhibit_label(exhibit_label: str, value: int) -> str:
    return f"{exhibit_label}-{value}"


def _normalized_saved_email_path(value: str) -> str:
    cleaned = str(value or "").strip()
    if cleaned in {"", "."}:
        return ""
    return cleaned


def _build_email_exhibit_manifest(
    exhibit_packet: list[dict[str, Any]],
    chronology_dir: Path,
) -> dict[str, Any]:
    json_path = chronology_dir / "formal_complaint_email_exhibits.json"
    md_path = chronology_dir / "formal_complaint_email_exhibits.md"

    threads: list[dict[str, Any]] = []
    total_messages = 0
    total_attachments = 0
    total_saved_messages = 0
    for packet_entry in exhibit_packet:
        if str(packet_entry.get("source_type") or "") != "email_manifest":
            continue
        source_path = str(packet_entry.get("source_path") or "")
        manifest_path = REPO_ROOT / source_path
        manifest = _read_json(manifest_path)
        messages: list[dict[str, Any]] = []
        for index, email in enumerate(list(manifest.get("emails") or []), start=1):
            subject = _normalize_email_subject(str(email.get("subject") or ""))
            if subject.lower().startswith("automatic reply"):
                continue
            attachments = []
            for attachment in list(email.get("attachments") or []):
                attachments.append({
                    "filename": str(attachment.get("filename") or ""),
                    "path": str(attachment.get("path") or ""),
                    "content_type": str(attachment.get("content_type") or ""),
                    "size": int(attachment.get("size") or 0),
                    "sha256": str(attachment.get("sha256") or ""),
                })
            email_path = _normalized_saved_email_path(str(email.get("email_path") or ""))
            parsed_path = _normalized_saved_email_path(str(email.get("parsed_path") or ""))
            if email_path:
                total_saved_messages += 1
            messages.append({
                "subexhibit": _subexhibit_label(str(packet_entry.get("label") or "?"), len(messages) + 1),
                "date": str(email.get("date") or ""),
                "from": str(email.get("from") or ""),
                "to": str(email.get("to") or ""),
                "subject": subject,
                "email_path": email_path,
                "parsed_path": parsed_path,
                "bundle_dir": str(email.get("bundle_dir") or ""),
                "has_saved_message": bool(email_path),
                "attachment_count": len(attachments),
                "attachments": attachments,
            })
        total_messages += len(messages)
        total_attachments += sum(int(message.get("attachment_count") or 0) for message in messages)
        threads.append({
            "exhibit_label": str(packet_entry.get("label") or ""),
            "source_path": source_path,
            "source_name": str(packet_entry.get("source_name") or ""),
            "suggested_title": str(packet_entry.get("suggested_title") or ""),
            "message_count": len(messages),
            "messages": messages,
        })

    summary = {
        "status": "success",
        "thread_count": len(threads),
        "message_count": total_messages,
        "attachment_count": total_attachments,
        "saved_message_count": total_saved_messages,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "threads": threads,
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Formal Complaint Email Exhibits",
        "",
        f"Thread count: {len(threads)}",
        f"Message count: {total_messages}",
        f"Saved message files: {total_saved_messages}",
        f"Attachment count: {total_attachments}",
        "",
    ]
    if threads:
        for thread in threads:
            md_lines.extend([
                f"## Exhibit {thread['exhibit_label']}: {thread['suggested_title']}",
                "",
                f"Source: {thread['source_path']}",
                f"Message count: {thread['message_count']}",
                "",
            ])
            for message in thread["messages"]:
                email_path_display = message["email_path"] or "unavailable (metadata-only entry)"
                md_lines.append(
                    f"- {message['subexhibit']} | {message['date']} | {message['subject']} | from {message['from']} | to {message['to']} | attachments={message['attachment_count']} | eml={email_path_display}"
                )
                for attachment in message["attachments"]:
                    md_lines.append(
                        f"- attachment: {attachment['filename']} | {attachment['content_type']} | size={attachment['size']} | {attachment['path']}"
                    )
            md_lines.append("")
    else:
        md_lines.append("No email exhibit threads generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_formal_complaint_filing_checklist(
    exhibit_packet: list[dict[str, Any]],
    citation_map: list[dict[str, Any]],
    email_exhibit_manifest: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    json_path = chronology_dir / "formal_complaint_filing_checklist.json"
    md_path = chronology_dir / "formal_complaint_filing_checklist.md"

    email_threads = {
        str(thread.get("exhibit_label") or ""): thread
        for thread in list(email_exhibit_manifest.get("threads") or [])
    }
    checklist_entries: list[dict[str, Any]] = []
    for exhibit in exhibit_packet:
        label = str(exhibit.get("label") or "")
        citations = [
            entry for entry in citation_map
            if str(entry.get("exhibit_label") or "") == label
        ]
        paragraphs = sorted(int(entry.get("paragraph_number") or 0) for entry in citations)
        sections = []
        for entry in citations:
            section = str(entry.get("section") or "")
            if section and section not in sections:
                sections.append(section)
        source_path = str(exhibit.get("source_path") or "")
        source_exists = (REPO_ROOT / source_path).exists()
        thread = email_threads.get(label) or {}
        checklist_entries.append({
            "label": label,
            "packet_order": int(exhibit.get("packet_order") or 0),
            "suggested_title": str(exhibit.get("suggested_title") or ""),
            "source_path": source_path,
            "source_type": str(exhibit.get("source_type") or ""),
            "source_exists": source_exists,
            "paragraph_numbers": paragraphs,
            "section_names": sections,
            "citation_count": len(citations),
            "message_count": int(thread.get("message_count") or 0),
            "saved_message_count": sum(1 for message in list(thread.get("messages") or []) if message.get("has_saved_message")),
            "handling_note": str(exhibit.get("handling_note") or ""),
        })

    summary = {
        "status": "success",
        "entry_count": len(checklist_entries),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "entries": checklist_entries,
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = ["# Formal Complaint Filing Checklist", "", f"Entry count: {len(checklist_entries)}", ""]
    if checklist_entries:
        for entry in checklist_entries:
            paragraphs = ", ".join(str(number) for number in entry["paragraph_numbers"]) or "not cited"
            sections = ", ".join(entry["section_names"]) or "not cited"
            email_detail = ""
            if entry["source_type"] == "email_manifest":
                email_detail = (
                    f" | messages={entry['message_count']}"
                    f" | saved_messages={entry['saved_message_count']}"
                )
            md_lines.append(
                f"- Exhibit {entry['label']} | order={entry['packet_order']} | paragraphs={paragraphs} | sections={sections} | exists={entry['source_exists']}{email_detail} | {entry['handling_note']}"
            )
    else:
        md_lines.append("No filing checklist entries generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _attachment_triage_reasons(attachment: dict[str, Any], duplicate_count: int) -> list[str]:
    reasons: list[str] = []
    filename = str(attachment.get("filename") or "")
    content_type = str(attachment.get("content_type") or "")
    if duplicate_count > 1:
        reasons.append("duplicate-content")
    if content_type.startswith("image/") and re.search(r"^(image\d*|img[_-]?\d+|image[_-]?\d+)", filename, flags=re.IGNORECASE):
        reasons.append("generic-image-name")
    if content_type.startswith("image/"):
        reasons.append("image-attachment")
    return reasons


def _attachment_triage_action(attachment: dict[str, Any], duplicate_count: int) -> str:
    content_type = str(attachment.get("content_type") or "")
    filename = str(attachment.get("filename") or "")
    if duplicate_count > 1 and content_type.startswith("image/"):
        return "review_for_deduplication"
    if duplicate_count > 1:
        return "review_duplicate_document"
    if content_type == "application/pdf":
        return "likely_keep"
    if content_type.startswith("image/") and re.search(r"^(image\d*|img[_-]?\d+|image[_-]?\d+)", filename, flags=re.IGNORECASE):
        return "review_low_signal_image"
    if content_type.startswith("image/"):
        return "review_image_attachment"
    return "review_other_attachment"


def _build_formal_complaint_attachment_triage(
    email_exhibit_manifest: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    json_path = chronology_dir / "formal_complaint_attachment_triage.json"
    md_path = chronology_dir / "formal_complaint_attachment_triage.md"

    attachments: list[dict[str, Any]] = []
    duplicate_counts: dict[str, int] = {}
    for thread in list(email_exhibit_manifest.get("threads") or []):
        exhibit_label = str(thread.get("exhibit_label") or "")
        for message in list(thread.get("messages") or []):
            for attachment in list(message.get("attachments") or []):
                key = str(attachment.get("sha256") or "") or f"{attachment.get('filename')}|{attachment.get('size')}|{attachment.get('content_type')}"
                duplicate_counts[key] = duplicate_counts.get(key, 0) + 1
                attachments.append({
                    "exhibit_label": exhibit_label,
                    "subexhibit": str(message.get("subexhibit") or ""),
                    "date": str(message.get("date") or ""),
                    **attachment,
                    "duplicate_key": key,
                })

    triaged: list[dict[str, Any]] = []
    for attachment in attachments:
        duplicate_count = duplicate_counts.get(str(attachment.get("duplicate_key") or ""), 1)
        triaged.append({
            **attachment,
            "duplicate_count": duplicate_count,
            "reasons": _attachment_triage_reasons(attachment, duplicate_count),
            "recommended_action": _attachment_triage_action(attachment, duplicate_count),
        })

    triaged.sort(key=lambda entry: (str(entry.get("recommended_action") or ""), str(entry.get("exhibit_label") or ""), str(entry.get("filename") or "")))
    flagged_count = sum(1 for entry in triaged if str(entry.get("recommended_action") or "") != "likely_keep")
    summary = {
        "status": "success",
        "attachment_count": len(triaged),
        "flagged_count": flagged_count,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "attachments": triaged,
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Formal Complaint Attachment Triage",
        "",
        f"Attachment count: {len(triaged)}",
        f"Flagged count: {flagged_count}",
        "",
    ]
    if triaged:
        for entry in triaged:
            reasons = ", ".join(list(entry.get("reasons") or [])) or "none"
            md_lines.append(
                f"- {entry['subexhibit']} | {entry['filename']} | {entry['content_type']} | size={entry['size']} | action={entry['recommended_action']} | duplicates={entry['duplicate_count']} | reasons={reasons} | {entry['path']}"
            )
    else:
        md_lines.append("No attachment triage entries generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_formal_complaint_email_exhibit_recommendations(
    email_exhibit_manifest: dict[str, Any],
    attachment_triage: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    json_path = chronology_dir / "formal_complaint_email_exhibit_recommendations.json"
    md_path = chronology_dir / "formal_complaint_email_exhibit_recommendations.md"

    triaged_attachments = list(attachment_triage.get("attachments") or [])
    representative_keys: set[str] = set()
    representative_lookup: dict[tuple[str, str], dict[str, Any]] = {}
    deferred_lookup: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for entry in triaged_attachments:
        duplicate_key = str(entry.get("duplicate_key") or "")
        subexhibit = str(entry.get("subexhibit") or "")
        attachment_path = str(entry.get("path") or "")
        recommended_action = str(entry.get("recommended_action") or "")
        pair = (subexhibit, attachment_path)

        if recommended_action == "likely_keep":
            representative_lookup[pair] = entry
            continue

        if recommended_action == "review_for_deduplication" and duplicate_key and duplicate_key not in representative_keys:
            representative_keys.add(duplicate_key)
            representative_lookup[pair] = {
                **entry,
                "recommended_action": "keep_representative_duplicate",
            }
            continue

        deferred_lookup.setdefault(pair, []).append(entry)

    thread_recommendations: list[dict[str, Any]] = []
    retained_count = 0
    deferred_count = 0
    for thread in list(email_exhibit_manifest.get("threads") or []):
        exhibit_label = str(thread.get("exhibit_label") or "")
        recommended_messages: list[dict[str, Any]] = []
        thread_retained = 0
        thread_deferred = 0
        for message in list(thread.get("messages") or []):
            subexhibit = str(message.get("subexhibit") or "")
            recommended_attachments: list[dict[str, Any]] = []
            deferred_attachments: list[dict[str, Any]] = []
            for attachment in list(message.get("attachments") or []):
                pair = (subexhibit, str(attachment.get("path") or ""))
                if pair in representative_lookup:
                    recommended_attachments.append(representative_lookup[pair])
                deferred_attachments.extend(deferred_lookup.get(pair, []))

            thread_retained += len(recommended_attachments)
            thread_deferred += len(deferred_attachments)
            if not recommended_attachments and not deferred_attachments and not message.get("has_saved_message"):
                continue

            recommended_messages.append({
                "subexhibit": subexhibit,
                "date": str(message.get("date") or ""),
                "subject": str(message.get("subject") or ""),
                "has_saved_message": bool(message.get("has_saved_message")),
                "email_path": str(message.get("email_path") or ""),
                "recommended_attachments": recommended_attachments,
                "deferred_attachments": deferred_attachments,
            })

        retained_count += thread_retained
        deferred_count += thread_deferred
        thread_recommendations.append({
            "exhibit_label": exhibit_label,
            "suggested_title": str(thread.get("suggested_title") or ""),
            "message_count": int(thread.get("message_count") or 0),
            "recommended_attachment_count": thread_retained,
            "deferred_attachment_count": thread_deferred,
            "messages": recommended_messages,
        })

    summary = {
        "status": "success",
        "thread_count": len(thread_recommendations),
        "retained_attachment_count": retained_count,
        "deferred_attachment_count": deferred_count,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "threads": thread_recommendations,
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Formal Complaint Email Exhibit Recommendations",
        "",
        f"Thread count: {len(thread_recommendations)}",
        f"Retained attachment count: {retained_count}",
        f"Deferred attachment count: {deferred_count}",
        "",
    ]
    if thread_recommendations:
        for thread in thread_recommendations:
            md_lines.extend([
                f"## Exhibit {thread['exhibit_label']}: {thread['suggested_title']}",
                "",
                f"Recommended attachments: {thread['recommended_attachment_count']}",
                f"Deferred attachments: {thread['deferred_attachment_count']}",
                "",
            ])
            for message in list(thread.get("messages") or []):
                md_lines.append(
                    f"- {message['subexhibit']} | {message['date']} | {message['subject']} | saved_message={message['has_saved_message']}"
                )
                for attachment in list(message.get("recommended_attachments") or []):
                    md_lines.append(
                        f"- keep: {attachment['filename']} | {attachment['content_type']} | action={attachment['recommended_action']} | duplicates={attachment['duplicate_count']} | {attachment['path']}"
                    )
                for attachment in list(message.get("deferred_attachments") or []):
                    md_lines.append(
                        f"- defer: {attachment['filename']} | {attachment['content_type']} | action={attachment['recommended_action']} | duplicates={attachment['duplicate_count']}"
                    )
                if not message.get("recommended_attachments") and not message.get("deferred_attachments"):
                    md_lines.append("- no attachment recommendation entries for this message")
            md_lines.append("")
    else:
        md_lines.append("No email exhibit recommendations generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_formal_complaint_proposed_filing_packet(
    exhibit_packet: list[dict[str, Any]],
    email_exhibit_manifest: dict[str, Any],
    email_exhibit_recommendations: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    json_path = chronology_dir / "formal_complaint_proposed_filing_packet.json"
    md_path = chronology_dir / "formal_complaint_proposed_filing_packet.md"

    manifest_threads = {
        str(thread.get("exhibit_label") or ""): thread
        for thread in list(email_exhibit_manifest.get("threads") or [])
    }
    recommendation_threads = {
        str(thread.get("exhibit_label") or ""): thread
        for thread in list(email_exhibit_recommendations.get("threads") or [])
    }

    packet_entries: list[dict[str, Any]] = []
    total_representative_messages = 0
    total_retained_attachments = 0
    for exhibit in exhibit_packet:
        label = str(exhibit.get("label") or "")
        source_type = str(exhibit.get("source_type") or "")
        entry = {
            "packet_order": int(exhibit.get("packet_order") or 0),
            "label": label,
            "suggested_title": str(exhibit.get("suggested_title") or ""),
            "source_path": str(exhibit.get("source_path") or ""),
            "source_type": source_type,
            "handling_note": str(exhibit.get("handling_note") or ""),
        }
        if source_type != "email_manifest":
            entry["proposed_materials"] = [
                {
                    "kind": "exhibit_file",
                    "path": str(exhibit.get("source_path") or ""),
                    "note": str(exhibit.get("handling_note") or ""),
                }
            ]
            packet_entries.append(entry)
            continue

        manifest_thread = manifest_threads.get(label) or {}
        recommendation_thread = recommendation_threads.get(label) or {}
        manifest_messages = {
            str(message.get("subexhibit") or ""): message
            for message in list(manifest_thread.get("messages") or [])
        }
        recommendation_messages = list(recommendation_thread.get("messages") or [])
        representative_messages: list[dict[str, Any]] = []
        if recommendation_messages:
            first_subexhibit = str(recommendation_messages[0].get("subexhibit") or "")
            last_subexhibit = str(recommendation_messages[-1].get("subexhibit") or "")
            for message in recommendation_messages:
                subexhibit = str(message.get("subexhibit") or "")
                manifest_message = manifest_messages.get(subexhibit) or {}
                recommended_attachments = list(message.get("recommended_attachments") or [])
                selection_reasons: list[str] = []
                if recommended_attachments:
                    selection_reasons.append("retained-attachment")
                if subexhibit == first_subexhibit:
                    selection_reasons.append("thread-start")
                if subexhibit == last_subexhibit and last_subexhibit != first_subexhibit:
                    selection_reasons.append("thread-end")
                if not selection_reasons:
                    continue
                representative_messages.append({
                    "subexhibit": subexhibit,
                    "date": str(message.get("date") or ""),
                    "subject": str(message.get("subject") or ""),
                    "email_path": str(manifest_message.get("email_path") or message.get("email_path") or ""),
                    "has_saved_message": bool(manifest_message.get("has_saved_message") or message.get("has_saved_message")),
                    "selection_reasons": selection_reasons,
                    "retained_attachments": recommended_attachments,
                })

        total_representative_messages += len(representative_messages)
        total_retained_attachments += sum(
            len(list(message.get("retained_attachments") or []))
            for message in representative_messages
        )
        entry["representative_message_count"] = len(representative_messages)
        entry["retained_attachment_count"] = sum(
            len(list(message.get("retained_attachments") or []))
            for message in representative_messages
        )
        entry["proposed_materials"] = [
            {
                "kind": "representative_saved_message",
                "subexhibit": message.get("subexhibit"),
                "date": message.get("date"),
                "subject": message.get("subject"),
                "email_path": message.get("email_path"),
                "has_saved_message": message.get("has_saved_message"),
                "selection_reasons": message.get("selection_reasons"),
                "retained_attachments": message.get("retained_attachments"),
            }
            for message in representative_messages
        ]
        packet_entries.append(entry)

    summary = {
        "status": "success",
        "packet_count": len(packet_entries),
        "representative_message_count": total_representative_messages,
        "retained_attachment_count": total_retained_attachments,
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "entries": packet_entries,
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    md_lines = [
        "# Formal Complaint Proposed Filing Packet",
        "",
        f"Packet count: {len(packet_entries)}",
        f"Representative saved messages: {total_representative_messages}",
        f"Retained email attachments: {total_retained_attachments}",
        "",
    ]
    if packet_entries:
        for entry in packet_entries:
            md_lines.append(
                f"## {entry['packet_order']}. Exhibit {entry['label']}: {entry['suggested_title']}"
            )
            md_lines.append("")
            md_lines.append(f"Source: {entry['source_path']}")
            md_lines.append(f"Type: {entry['source_type']}")
            md_lines.append(f"Handling: {entry['handling_note']}")
            if entry["source_type"] != "email_manifest":
                md_lines.append("- include: underlying exhibit file")
                md_lines.append("")
                continue
            md_lines.append(f"Representative saved messages: {entry.get('representative_message_count', 0)}")
            md_lines.append(f"Retained attachments: {entry.get('retained_attachment_count', 0)}")
            md_lines.append("")
            for material in list(entry.get("proposed_materials") or []):
                reasons = ", ".join(list(material.get("selection_reasons") or [])) or "none"
                email_path = str(material.get("email_path") or "unavailable (metadata-only entry)")
                md_lines.append(
                    f"- message: {material.get('subexhibit')} | {material.get('date')} | {material.get('subject')} | reasons={reasons} | eml={email_path}"
                )
                for attachment in list(material.get("retained_attachments") or []):
                    md_lines.append(
                        f"- attachment: {attachment['filename']} | {attachment['content_type']} | action={attachment['recommended_action']} | {attachment['path']}"
                    )
            md_lines.append("")
    else:
        md_lines.append("No proposed filing packet entries generated.")
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")
    return summary


def _build_formal_complaint_draft(
    complaint_ready: dict[str, Any],
    cause_draft: dict[str, Any],
    chronology_dir: Path,
) -> dict[str, Any]:
    factual_entries = _compress_email_entries(list(complaint_ready.get("paragraphs") or []))
    cause_sections = list(cause_draft.get("sections") or [])
    json_path = chronology_dir / "formal_complaint_draft.json"
    md_path = chronology_dir / "formal_complaint_draft.md"
    exhibit_json_path = chronology_dir / "formal_complaint_exhibit_index.json"
    exhibit_md_path = chronology_dir / "formal_complaint_exhibit_index.md"
    citation_json_path = chronology_dir / "formal_complaint_citation_map.json"
    citation_md_path = chronology_dir / "formal_complaint_citation_map.md"
    packet_json_path = chronology_dir / "formal_complaint_exhibit_packet.json"
    packet_md_path = chronology_dir / "formal_complaint_exhibit_packet.md"

    factual_background = factual_entries[: min(14, len(factual_entries))]
    exhibit_map = _build_exhibit_map(factual_background, cause_sections)
    count_blocks = []
    for section in cause_sections:
        section_entries = list(section.get("paragraphs") or [])[:3]
        count_blocks.append({
            "title": str(section.get("title") or "Potential Claim Theme"),
            "intro": str(section.get("intro") or ""),
            "source_section": str(section.get("source_section") or ""),
            "element_prompts": list(section.get("element_prompts") or []),
            "entries": section_entries,
            "paragraphs": [
                _paragraph_with_exhibit_tag(
                    _narrative_fact_from_entry(entry),
                    exhibit_map.get(str(entry.get("source_path") or "")),
                )
                for entry in section_entries
            ],
        })

    exhibit_index = [
        {
            "label": label,
            "source_path": source_path,
            "source_name": _source_display_name(source_path),
            "source_type": _source_type_for_path(source_path),
            "suggested_title": _suggested_exhibit_title(source_path, _source_display_name(source_path)),
            "handling_note": _exhibit_handling_note(source_path),
        }
        for source_path, label in exhibit_map.items()
    ]

    exhibit_packet = [
        {
            "packet_order": index,
            **entry,
        }
        for index, entry in enumerate(exhibit_index, start=1)
    ]
    email_exhibit_manifest = _build_email_exhibit_manifest(exhibit_packet, chronology_dir)
    attachment_triage = _build_formal_complaint_attachment_triage(email_exhibit_manifest, chronology_dir)

    citation_map: list[dict[str, Any]] = []

    summary = {
        "status": "success",
        "factual_background_count": len(factual_background),
        "count_count": len(count_blocks),
        "exhibit_count": len(exhibit_index),
        "json_path": str(json_path),
        "markdown_path": str(md_path),
        "exhibit_json_path": str(exhibit_json_path),
        "exhibit_markdown_path": str(exhibit_md_path),
        "citation_json_path": str(citation_json_path),
        "citation_markdown_path": str(citation_md_path),
        "packet_json_path": str(packet_json_path),
        "packet_markdown_path": str(packet_md_path),
        "email_exhibit_json_path": str(email_exhibit_manifest.get("json_path") or ""),
        "email_exhibit_markdown_path": str(email_exhibit_manifest.get("markdown_path") or ""),
        "email_exhibit_thread_count": int(email_exhibit_manifest.get("thread_count") or 0),
        "email_exhibit_message_count": int(email_exhibit_manifest.get("message_count") or 0),
        "attachment_triage_json_path": str(attachment_triage.get("json_path") or ""),
        "attachment_triage_markdown_path": str(attachment_triage.get("markdown_path") or ""),
        "attachment_triage_flagged_count": int(attachment_triage.get("flagged_count") or 0),
    }

    md_lines = [
        "# Formal Complaint Draft",
        "",
        "IN THE [COURT NAME]",
        "",
        "Jane Cortez and Benjamin Barber,",
        "Plaintiffs,",
        "",
        "v.",
        "",
        "Housing Authority of Clackamas County; DOES 1-10,",
        "Defendants.",
        "",
        "## Nature of Action",
        "",
        "1. This draft complaint organizes the currently extracted evidence into a more conventional complaint format.",
        "2. It remains a drafting aid and should be checked against the underlying evidence, governing claims, and filing requirements before use.",
        "",
        "## Parties",
        "",
        "3. Plaintiffs are Jane Cortez and Benjamin Barber, subject to confirmation of full legal names, capacity, and proper party alignment.",
        "4. Defendant Housing Authority of Clackamas County is alleged to have issued the housing-related notices, amendments, requests, and communications reflected in the evidence summarized below.",
        "5. Doe defendants may be named if later investigation supports individual-capacity or agency-role allegations.",
        "",
        "## Jurisdiction and Venue",
        "",
        "6. Jurisdiction basis: [fill in federal question, state-law, supplemental, or other basis].",
        "7. Venue basis: [fill in county, district, and operative-events basis].",
        "",
        "## General Allegations",
        "",
    ]

    paragraph_number = 8
    if factual_background:
        for entry in factual_background:
            source_path = str(entry.get("source_path") or "")
            tagged = _paragraph_with_exhibit_tag(
                str(entry.get("paragraph") or ""),
                exhibit_map.get(source_path),
            )
            md_lines.append(f"{paragraph_number}. {tagged}")
            citation_map.append({
                "paragraph_number": paragraph_number,
                "section": "General Allegations",
                "source_path": source_path,
                "source_name": _source_display_name(source_path) if source_path else "",
                "exhibit_label": exhibit_map.get(source_path),
                "event_label": str(entry.get("event_label") or ""),
            })
            paragraph_number += 1
    else:
        md_lines.append(f"{paragraph_number}. No general allegations were generated from the current evidence set.")
        paragraph_number += 1

    md_lines.extend(["", "## Counts", ""])
    factual_end = paragraph_number - 1
    if count_blocks:
        for idx, block in enumerate(count_blocks, start=1):
            md_lines.extend([
                f"### Count {_roman_count_label(idx)}: {block['title']}",
                "",
                f"{paragraph_number}. Plaintiffs repeat and reallege Paragraphs 1 through {factual_end} as if fully set out here.",
            ])
            paragraph_number += 1
            md_lines.append(f"{paragraph_number}. {block['intro']}")
            paragraph_number += 1
            md_lines.append(
                f"{paragraph_number}. This count is presently organized around the evidence group labeled \"{block['source_section']}\"."
            )
            paragraph_number += 1
            for entry, fact in zip(block["entries"], block["paragraphs"]):
                md_lines.append(f"{paragraph_number}. {fact}")
                source_path = str(entry.get("source_path") or "")
                citation_map.append({
                    "paragraph_number": paragraph_number,
                    "section": block["title"],
                    "source_path": source_path,
                    "source_name": _source_display_name(source_path) if source_path else "",
                    "exhibit_label": exhibit_map.get(source_path),
                    "event_label": str(entry.get("event_label") or ""),
                })
                paragraph_number += 1
            md_lines.append(f"{paragraph_number}. Legal elements and claim language to be added: [fill in].")
            paragraph_number += 1
            md_lines.append("")
            md_lines.append("Elements to Plead:")
            md_lines.extend(f"- {prompt}" for prompt in block["element_prompts"])
            md_lines.append("")
    else:
        md_lines.append(f"{paragraph_number}. No counts were generated from the current evidence set.")
        paragraph_number += 1

    md_lines.extend([
        "## Prayer for Relief",
        "",
        f"{paragraph_number}. Plaintiffs request declaratory relief as permitted by law. [fill in specific declaration].",
        f"{paragraph_number + 1}. Plaintiffs request injunctive or equitable relief as permitted by law. [fill in specific injunction].",
        f"{paragraph_number + 2}. Plaintiffs request damages, fees, costs, and any additional relief authorized by law. [fill in].",
        "",
        "## Jury Demand",
        "",
        f"{paragraph_number + 3}. Plaintiffs demand a jury on all issues so triable, if applicable.",
    ])

    filing_checklist = _build_formal_complaint_filing_checklist(
        exhibit_packet,
        citation_map,
        email_exhibit_manifest,
        chronology_dir,
    )
    email_exhibit_recommendations = _build_formal_complaint_email_exhibit_recommendations(
        email_exhibit_manifest,
        attachment_triage,
        chronology_dir,
    )
    proposed_filing_packet = _build_formal_complaint_proposed_filing_packet(
        exhibit_packet,
        email_exhibit_manifest,
        email_exhibit_recommendations,
        chronology_dir,
    )

    summary["filing_checklist_json_path"] = str(filing_checklist.get("json_path") or "")
    summary["filing_checklist_markdown_path"] = str(filing_checklist.get("markdown_path") or "")
    summary["email_exhibit_recommendations_json_path"] = str(email_exhibit_recommendations.get("json_path") or "")
    summary["email_exhibit_recommendations_markdown_path"] = str(email_exhibit_recommendations.get("markdown_path") or "")
    summary["email_exhibit_recommendations_retained_count"] = int(email_exhibit_recommendations.get("retained_attachment_count") or 0)
    summary["email_exhibit_recommendations_deferred_count"] = int(email_exhibit_recommendations.get("deferred_attachment_count") or 0)
    summary["proposed_filing_packet_json_path"] = str(proposed_filing_packet.get("json_path") or "")
    summary["proposed_filing_packet_markdown_path"] = str(proposed_filing_packet.get("markdown_path") or "")
    summary["proposed_filing_packet_message_count"] = int(proposed_filing_packet.get("representative_message_count") or 0)
    summary["proposed_filing_packet_attachment_count"] = int(proposed_filing_packet.get("retained_attachment_count") or 0)

    json_path.write_text(
        json.dumps(
            {
                **summary,
                "factual_background": factual_background,
                "counts": count_blocks,
                "exhibit_index": exhibit_index,
                "exhibit_packet": exhibit_packet,
                "email_exhibit_manifest": email_exhibit_manifest,
                "filing_checklist": filing_checklist,
                "attachment_triage": attachment_triage,
                "email_exhibit_recommendations": email_exhibit_recommendations,
                "proposed_filing_packet": proposed_filing_packet,
                "citation_map": citation_map,
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    md_path.write_text("\n".join(md_lines).strip() + "\n", encoding="utf-8")

    exhibit_json_path.write_text(
        json.dumps({"status": "success", "exhibit_count": len(exhibit_index), "exhibits": exhibit_index}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    exhibit_md_lines = ["# Formal Complaint Exhibit Index", "", f"Exhibit count: {len(exhibit_index)}", ""]
    if exhibit_index:
        exhibit_md_lines.extend(
            f"- Exhibit {entry['label']}: {entry['source_path']} ({entry['source_name']})"
            for entry in exhibit_index
        )
    else:
        exhibit_md_lines.append("No exhibits indexed.")
    exhibit_md_path.write_text("\n".join(exhibit_md_lines).strip() + "\n", encoding="utf-8")

    packet_json_path.write_text(
        json.dumps({"status": "success", "packet_count": len(exhibit_packet), "packet": exhibit_packet}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    packet_md_lines = ["# Formal Complaint Exhibit Packet", "", f"Packet count: {len(exhibit_packet)}", ""]
    if exhibit_packet:
        packet_md_lines.extend(
            (
                f"- {entry['packet_order']}. Exhibit {entry['label']} | {entry['suggested_title']} | "
                f"{entry['source_path']} | type={entry['source_type']} | {entry['handling_note']}"
            )
            for entry in exhibit_packet
        )
    else:
        packet_md_lines.append("No exhibit packet entries generated.")
    packet_md_path.write_text("\n".join(packet_md_lines).strip() + "\n", encoding="utf-8")

    citation_json_path.write_text(
        json.dumps({"status": "success", "citation_count": len(citation_map), "citations": citation_map}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    citation_md_lines = ["# Formal Complaint Citation Map", "", f"Citation count: {len(citation_map)}", ""]
    if citation_map:
        citation_md_lines.extend(
            f"- Paragraph {entry['paragraph_number']}: Exhibit {entry['exhibit_label'] or '?'} | {entry['source_path']} | {entry['section']}"
            for entry in citation_map
        )
    else:
        citation_md_lines.append("No paragraph-to-source citations generated.")
    citation_md_path.write_text("\n".join(citation_md_lines).strip() + "\n", encoding="utf-8")
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
    summary["complaint_ready_chronology"] = _build_complaint_ready_chronology(summary["pleading_timeline"], chronology_dir)
    summary["claim_grouped_allegations"] = _build_claim_grouped_allegations(summary["complaint_ready_chronology"], chronology_dir)
    summary["cause_of_action_draft"] = _build_cause_of_action_draft(summary["claim_grouped_allegations"], chronology_dir)
    summary["complaint_skeleton"] = _build_complaint_skeleton(
        summary["cause_of_action_draft"],
        summary["complaint_ready_chronology"],
        chronology_dir,
    )
    summary["narrative_complaint_draft"] = _build_narrative_complaint_draft(
        summary["complaint_ready_chronology"],
        summary["cause_of_action_draft"],
        chronology_dir,
    )
    summary["formal_complaint_draft"] = _build_formal_complaint_draft(
        summary["complaint_ready_chronology"],
        summary["cause_of_action_draft"],
        chronology_dir,
    )
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
        complaint_ready = chronology.get("complaint_ready_chronology") or {}
        if complaint_ready:
            lines.append(f"- Complaint-ready chronology paragraphs generated: {complaint_ready.get('paragraph_count', 0)}")
        grouped_allegations = chronology.get("claim_grouped_allegations") or {}
        if grouped_allegations:
            lines.append(
                f"- Claim-grouped allegation sections generated: {grouped_allegations.get('section_count', 0)}"
            )
        cause_draft = chronology.get("cause_of_action_draft") or {}
        if cause_draft:
            lines.append(f"- Cause-of-action draft sections generated: {cause_draft.get('section_count', 0)}")
        complaint_skeleton = chronology.get("complaint_skeleton") or {}
        if complaint_skeleton:
            lines.append(
                f"- Complaint skeleton cause sections generated: {complaint_skeleton.get('cause_section_count', 0)}"
            )
        narrative_draft = chronology.get("narrative_complaint_draft") or {}
        if narrative_draft:
            lines.append(
                f"- Narrative complaint counts generated: {narrative_draft.get('count_count', 0)}"
            )
        formal_draft = chronology.get("formal_complaint_draft") or {}
        if formal_draft:
            lines.append(
                f"- Formal complaint counts generated: {formal_draft.get('count_count', 0)}"
            )
            lines.append(
                f"- Formal complaint exhibits indexed: {formal_draft.get('exhibit_count', 0)}"
            )
            lines.append(
                f"- Formal complaint email exhibit messages indexed: {formal_draft.get('email_exhibit_message_count', 0)}"
            )
            lines.append(
                f"- Formal complaint attachment triage flagged items: {formal_draft.get('attachment_triage_flagged_count', 0)}"
            )
            lines.append(
                f"- Formal complaint email exhibit recommendations retained/deferred: {formal_draft.get('email_exhibit_recommendations_retained_count', 0)}/{formal_draft.get('email_exhibit_recommendations_deferred_count', 0)}"
            )
            lines.append(
                f"- Formal complaint proposed filing packet representative messages/attachments: {formal_draft.get('proposed_filing_packet_message_count', 0)}/{formal_draft.get('proposed_filing_packet_attachment_count', 0)}"
            )
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