#!/usr/bin/env python3
"""Generate full case knowledge/dependency graphs and formal logic artifacts.

Outputs are written to knowledge_graph/generated/.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import csv
from datetime import date, datetime
import json
from pathlib import Path
import re
from typing import Dict, List, Tuple


ROOT = Path("/home/barberb/HACC/Collateral Estoppel/knowledge_graph")
OUT = ROOT / "generated"
EVIDENCE = Path("/home/barberb/HACC/Collateral Estoppel/evidence_notes")
SOLOMON_FEED = EVIDENCE / "solomon_evidence_graph_feed.json"
SOLOMON_REPO_INDEX = EVIDENCE / "solomon_repository_evidence_index.json"
FINAL_SET = Path("/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set")
ACTIVE_SERVICE_LOG = FINAL_SET / "28_active_service_log_2026-04-07.csv"
FACT_OVERRIDES_CSV = ROOT / "evidence_fact_overrides_2026-04-07.csv"
CERTIFIED_RECORDS_DIR = EVIDENCE / "certified_records"
ISSUE_PRECLUSION_MAPPING_FILE = CERTIFIED_RECORDS_DIR / "issue_preclusion_mapping.json"
ORCP17_MAPPING_FILE = CERTIFIED_RECORDS_DIR / "orcp17_filing_mapping.json"


@dataclass(frozen=True)
class Fact:
    fact_id: str
    predicate: str
    args: Tuple[str, ...]
    value: bool
    status: str  # verified | alleged | theory
    source: str
    dates: Tuple[str, ...] = ()
    confidence_level: str | None = None
    confidence_score: float | None = None
    evidence_kind: str | None = None


@dataclass(frozen=True)
class DeonticConclusion:
    conclusion_id: str
    modality: str  # O | P | F
    actor: str
    action: str
    target: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    antecedents: Tuple[str, ...]
    conclusion: DeonticConclusion
    description: str
    track: str = "filing"  # filing | hypothesis | workflow
    authority_refs: Tuple[str, ...] = ()


VALID_FACT_STATUSES = {"verified", "alleged", "theory"}


@dataclass(frozen=True)
class TemporalInterval:
    interval_id: str
    label: str
    start_date: str
    end_date: str | None
    status: str
    source: str
    tags: Tuple[str, ...] = ()


def _normalize_date(token: str) -> str | None:
    token = token.strip()
    for fmt in ("%m/%d/%Y", "%m-%d-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(token, fmt).date().isoformat()
        except ValueError:
            pass
    return None


def extract_dates_from_text(text: str) -> List[str]:
    raw = set()
    for m in re.findall(r"\b\d{1,2}/\d{1,2}/\d{4}\b", text):
        d = _normalize_date(m)
        if d:
            raw.add(d)
    for m in re.findall(r"\b\d{1,2}-\d{1,2}-\d{4}\b", text):
        d = _normalize_date(m)
        if d:
            raw.add(d)
    for m in re.findall(r"\b\d{4}-\d{2}-\d{2}\b", text):
        d = _normalize_date(m)
        if d:
            raw.add(d)
    return sorted(raw)


def load_ocr_date_index() -> Dict[str, List[str]]:
    index: Dict[str, List[str]] = {}
    for name in ("solomon_motion_for_guardianship_ocr.txt", "sam_barber_restraining_order_ocr.txt"):
        p = EVIDENCE / name
        if p.exists():
            index[name] = extract_dates_from_text(p.read_text(encoding="utf-8", errors="ignore"))
        else:
            index[name] = []
    return index


def load_solomon_event_feed() -> List[Dict[str, object]]:
    if not SOLOMON_FEED.exists():
        return []
    obj = json.loads(SOLOMON_FEED.read_text(encoding="utf-8"))
    raw_events = list(obj.get("events", []))
    merged: Dict[str, Dict[str, object]] = {}
    source_sets: Dict[str, set] = {}

    for ev in raw_events:
        event_id = str(ev.get("event_id", "")).strip()
        if not event_id:
            continue
        if event_id not in merged:
            merged[event_id] = dict(ev)
            source_sets[event_id] = set()
        src = str(ev.get("source", "")).strip()
        if src:
            source_sets[event_id].add(src)

        # Keep earliest non-null date for stable activation floor.
        existing_date = merged[event_id].get("date")
        incoming_date = ev.get("date")
        if existing_date and incoming_date:
            if str(incoming_date) < str(existing_date):
                merged[event_id]["date"] = incoming_date
        elif incoming_date and not existing_date:
            merged[event_id]["date"] = incoming_date

    out = []
    for event_id, ev in sorted(merged.items()):
        sources = sorted(source_sets.get(event_id, set()))
        if sources:
            ev["source"] = " | ".join(sources)
        out.append(ev)
    return out


def load_solomon_repository_index() -> List[Dict[str, object]]:
    if not SOLOMON_REPO_INDEX.exists():
        return []
    obj = json.loads(SOLOMON_REPO_INDEX.read_text(encoding="utf-8"))
    return list(obj.get("hits", []))


def load_active_service_rows() -> List[Dict[str, str]]:
    if not ACTIVE_SERVICE_LOG.exists():
        return []
    with ACTIVE_SERVICE_LOG.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def load_fact_overrides() -> List[Dict[str, str]]:
    if not FACT_OVERRIDES_CSV.exists():
        return []
    with FACT_OVERRIDES_CSV.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [{k: (v or "").strip() for k, v in row.items()} for row in reader]


def _pick_date(candidates: List[str], preferred: str) -> Tuple[str, ...]:
    if preferred in candidates:
        return (preferred,)
    if candidates:
        return (candidates[0],)
    return ()


def _extract_iso_date(value: str | None) -> str | None:
    if not value:
        return None
    s = value.strip()
    if not s:
        return None
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
    return m.group(1) if m else None


def apply_fact_overrides(facts: List[Fact], overrides: List[Dict[str, str]]) -> Tuple[List[Fact], Dict[str, object]]:
    by_id = {f.fact_id: f for f in facts}
    applied = []
    skipped = []

    for i, row in enumerate(overrides, start=1):
        fid = row.get("fact_id", "").strip()
        if not fid:
            skipped.append({"row": i, "reason": "missing_fact_id"})
            continue
        if fid not in by_id:
            skipped.append({"row": i, "fact_id": fid, "reason": "fact_id_not_found"})
            continue

        current = by_id[fid]
        raw_status = row.get("override_status", "").strip().lower()
        raw_value = row.get("override_value", "").strip().lower()
        raw_source = row.get("override_source", "").strip()
        raw_date = row.get("override_date", "").strip()
        if not any([raw_status, raw_value, raw_source, raw_date]):
            skipped.append({"row": i, "fact_id": fid, "reason": "no_override_fields_set"})
            continue

        next_status = raw_status or current.status
        if next_status not in VALID_FACT_STATUSES:
            skipped.append({"row": i, "fact_id": fid, "reason": f"invalid_status:{next_status}"})
            continue

        if raw_value in {"true", "1", "yes", "y"}:
            next_value = True
        elif raw_value in {"false", "0", "no", "n"}:
            next_value = False
        elif raw_value == "":
            next_value = current.value
        else:
            skipped.append({"row": i, "fact_id": fid, "reason": f"invalid_override_value:{raw_value}"})
            continue

        next_source = raw_source or current.source
        next_dates = list(current.dates)
        d = _extract_iso_date(raw_date)
        if d and d not in next_dates:
            next_dates.append(d)
            next_dates = sorted(next_dates)

        source_changed = next_source != current.source
        date_added = bool(d and d not in current.dates)
        status_changed = next_status != current.status
        value_changed = next_value != current.value

        updated = replace(
            current,
            status=next_status,
            value=next_value,
            source=next_source,
            dates=tuple(next_dates),
        )
        by_id[fid] = updated
        applied.append(
            {
                "row": i,
                "fact_id": fid,
                "from_status": current.status,
                "to_status": next_status,
                "from_value": current.value,
                "to_value": next_value,
                "source": next_source,
                "status_changed": status_changed,
                "value_changed": value_changed,
                "source_changed": source_changed,
                "date_added": date_added,
                "note": row.get("note", "").strip(),
            }
        )

    ordered = [by_id[f.fact_id] for f in facts]
    status_changes = sum(1 for x in applied if x.get("status_changed"))
    value_changes = sum(1 for x in applied if x.get("value_changed"))
    source_changes = sum(1 for x in applied if x.get("source_changed"))
    date_additions = sum(1 for x in applied if x.get("date_added"))
    summary = {
        "override_file": str(FACT_OVERRIDES_CSV),
        "rows_read": len(overrides),
        "applied_count": len(applied),
        "skipped_count": len(skipped),
        "applied_status_changes": status_changes,
        "applied_value_changes": value_changes,
        "applied_status_or_value_changes": status_changes + value_changes,
        "applied_source_changes": source_changes,
        "applied_date_additions": date_additions,
        "applied": applied,
        "skipped": skipped,
    }
    return ordered, summary


def _sorted_iso_dates(values: List[str]) -> List[str]:
    uniq = sorted({v for v in values if re.fullmatch(r"\d{4}-\d{2}-\d{2}", v or "")})
    return uniq


def _max_iso_date(values: List[str]) -> str | None:
    ordered = _sorted_iso_dates(values)
    return ordered[-1] if ordered else None


def build_temporal_profile(rule: Rule, facts_by_id: Dict[str, Fact]) -> Dict[str, object]:
    known_dates: List[str] = []
    fact_ids = set(rule.antecedents)
    for fid in rule.antecedents:
        known_dates.extend(facts_by_id[fid].dates)

    ordered = _sorted_iso_dates(known_dates)
    earliest = ordered[0] if ordered else None
    latest = ordered[-1] if ordered else None

    profile: Dict[str, object] = {
        "earliest_date": earliest,
        "latest_date": latest,
        "date_count": len(ordered),
        "spans_multiple_dates": len(ordered) > 1,
        "temporal_tags": [],
    }

    tags: List[str] = []
    if len(ordered) > 1:
        tags.append("multi_date_window")

    notice_dates = list(facts_by_id.get("f_solomon_actual_notice_on_2025_11_17", Fact("", "", (), False, "verified", "")).dates)
    order_dates = list(facts_by_id.get("f_restraining_order_granted", Fact("", "", (), False, "verified", "")).dates)
    objection_dates = list(facts_by_id.get("f_respondent_objection_form_present", Fact("", "", (), False, "verified", "")).dates)
    hacc_removal_dates = list(facts_by_id.get("f_hacc_removed_benjamin_effective_2026_01_01", Fact("", "", (), False, "verified", "")).dates)

    notice_date = _max_iso_date(notice_dates)
    order_date = _max_iso_date(order_dates)
    objection_date = _max_iso_date(objection_dates)
    hacc_removal_date = _max_iso_date(hacc_removal_dates)

    if latest and notice_date and latest > notice_date and (
        "f_solomon_actual_notice_on_2025_11_17" in fact_ids
        or any(fid.startswith("f_solomon_") for fid in fact_ids)
    ):
        tags.append("post_notice")

    if latest and order_date and latest > order_date and (
        "f_restraining_order_granted" in fact_ids
        or any(fid.startswith("f_solomon_") for fid in fact_ids)
    ):
        tags.append("post_order_effective")

    if latest and objection_date and latest >= objection_date and (
        "f_notice_to_respondent" in fact_ids or "f_respondent_objection_form_present" in fact_ids
    ):
        tags.append("objection_window_or_later")

    if latest and hacc_removal_date and latest >= hacc_removal_date and any(fid.startswith("f_hacc_") for fid in fact_ids):
        tags.append("post_hacc_lease_change")

    if order_date and latest and latest <= "2026-11-20" and any(fid.startswith("f_solomon_") for fid in fact_ids):
        tags.append("within_estimated_order_lifespan")

    profile["temporal_tags"] = tags
    return profile


def build_temporal_intervals(facts_by_id: Dict[str, Fact]) -> List[TemporalInterval]:
    def latest(fid: str) -> str | None:
        fact = facts_by_id.get(fid)
        if not fact:
            return None
        return _max_iso_date(list(fact.dates))

    def earliest(fid: str) -> str | None:
        fact = facts_by_id.get(fid)
        if not fact:
            return None
        vals = _sorted_iso_dates(list(fact.dates))
        return vals[0] if vals else None

    intervals: List[TemporalInterval] = []

    order_start = latest("f_restraining_order_in_effect") or latest("f_restraining_order_granted")
    if order_start:
        intervals.append(
            TemporalInterval(
                "ti_restraining_order_effective_period",
                "Restraining order effective period",
                order_start,
                "2026-11-20",
                "estimated",
                "sam_barber_restraining_order_ocr.txt",
                ("order_effective_period", "estimated_expiration"),
            )
        )

    notice_start = latest("f_notice_to_respondent") or earliest("f_petition_exists")
    objection_end = latest("f_respondent_objection_form_present")
    if notice_start:
        intervals.append(
            TemporalInterval(
                "ti_probate_notice_objection_window",
                "Probate notice and objection window",
                notice_start,
                objection_end,
                "verified" if objection_end else "open",
                "guardianship_timeline.md",
                ("notice_window", "objection_window"),
            )
        )

    hacc_start = earliest("f_hacc_removed_benjamin_effective_2026_01_01")
    hacc_end = latest("f_hacc_court_documentation_basis_claimed") or latest("f_hacc_internal_review_claimed")
    if hacc_start:
        intervals.append(
            TemporalInterval(
                "ti_hacc_lease_change_sequence",
                "HACC lease change sequence",
                hacc_start,
                hacc_end,
                "verified" if hacc_end else "open",
                "0014-Re-Allegations-of-Fraud---JC-Household/message.eml",
                ("hacc_lease_change", "authority_chain_gap"),
            )
        )

    subpoena_start = str(date.today()) if latest("f_hacc_exhibit_r_requires_compelled_production") else None
    if subpoena_start:
        intervals.append(
            TemporalInterval(
                "ti_exhibit_r_compelled_production_track",
                "Exhibit R compelled-production track",
                subpoena_start,
                None,
                "open",
                "subpoena_target_memo_hacc_lease_authority_record.md",
                ("subpoena_workflow", "compelled_production"),
            )
        )

    return intervals


def _date_in_interval(d: str, interval: TemporalInterval) -> bool:
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", d or ""):
        return False
    if d < interval.start_date:
        return False
    if interval.end_date and d > interval.end_date:
        return False
    return True


def attach_intervals_to_profile(profile: Dict[str, object], intervals: List[TemporalInterval], rule: Rule) -> Dict[str, object]:
    out = dict(profile)
    earliest = out.get("earliest_date")
    latest = out.get("latest_date")
    matched: List[str] = []
    rule_text = f"{rule.rule_id} {rule.description} {rule.conclusion.actor} {rule.conclusion.action} {rule.conclusion.target}".lower()
    for interval in intervals:
        if not ((earliest and _date_in_interval(earliest, interval)) or (latest and _date_in_interval(latest, interval))):
            continue

        interval_id = interval.interval_id
        include = False
        if interval_id == "ti_restraining_order_effective_period":
            include = any(k in rule_text for k in ["solomon", "restraining", "order", "contempt", "self_help", "service"])
        elif interval_id == "ti_probate_notice_objection_window":
            include = any(k in rule_text for k in ["objection", "notice", "protective", "jane_cortez", "counsel", "hearing"])
        elif interval_id == "ti_hacc_lease_change_sequence":
            include = any(k in rule_text for k in ["hacc", "lease", "household", "authority_chain", "compelled_production"])
        elif interval_id == "ti_exhibit_r_compelled_production_track":
            include = any(k in rule_text for k in ["subpoena", "compel", "production", "exhibit_r", "custodian"])

        if include:
            matched.append(interval.interval_id)
    out["interval_refs"] = matched
    return out


def _fact_status_label(facts_by_id: Dict[str, Fact], fid: str) -> str:
    fact = facts_by_id.get(fid)
    if not fact:
        return "missing"
    if not fact.value:
        return "missing"
    return fact.status


def load_issue_preclusion_mapping() -> Dict[str, object]:
    if not ISSUE_PRECLUSION_MAPPING_FILE.exists():
        return {}
    try:
        obj = json.loads(ISSUE_PRECLUSION_MAPPING_FILE.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def load_orcp17_mapping() -> Dict[str, object]:
    if not ORCP17_MAPPING_FILE.exists():
        return {}
    try:
        obj = json.loads(ORCP17_MAPPING_FILE.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def build_element_audits(facts_by_id: Dict[str, Fact], intervals: List[TemporalInterval]) -> List[Dict[str, object]]:
    ip_map = load_issue_preclusion_mapping()
    orcp17_map = load_orcp17_mapping()

    def mapped_flag(key: str) -> bool:
        val = ip_map.get(key, False)
        return bool(val)

    def filing_flag(key: str) -> bool:
        val = orcp17_map.get(key, False)
        return bool(val)

    def interval_ref(interval_id: str) -> str | None:
        return interval_id if any(x.interval_id == interval_id for x in intervals) else None

    audits: List[Dict[str, object]] = []

    contempt_elements = [
        {
            "element_id": "valid_order",
            "label": "Valid restraining order in effect",
            "fact_ids": ["f_restraining_order_granted", "f_restraining_order_in_effect"],
            "status": "verified"
            if all(_fact_status_label(facts_by_id, fid) == "verified" for fid in ["f_restraining_order_granted", "f_restraining_order_in_effect"])
            else "open",
        },
        {
            "element_id": "notice",
            "label": "Solomon had notice or equivalent appearance-based notice",
            "fact_ids": ["f_solomon_actual_notice_on_2025_11_17", "f_restraining_order_no_further_service_needed"],
            "status": "verified"
            if all(_fact_status_label(facts_by_id, fid) == "verified" for fid in ["f_solomon_actual_notice_on_2025_11_17", "f_restraining_order_no_further_service_needed"])
            else "open",
        },
        {
            "element_id": "post_notice_conduct",
            "label": "Later post-notice conduct inconsistent with compliance",
            "fact_ids": ["f_solomon_service_position_statement", "f_solomon_noncooperation_statement"],
            "status": "verified"
            if all(_fact_status_label(facts_by_id, fid) == "verified" for fid in ["f_solomon_service_position_statement", "f_solomon_noncooperation_statement"])
            else "open",
        },
        {
            "element_id": "service_or_appearance_record",
            "label": "Certified service or appearance record for litigation use",
            "fact_ids": [],
            "status": "proof_gated",
            "note": "The local repository supports notice strongly, but a cleaner certified docket / appearance record remains preferable for filing-grade contempt proof.",
        },
    ]
    audits.append(
        {
            "audit_id": "audit_remedial_contempt_timing",
            "label": "Remedial contempt timing audit",
            "governing_authority": ["auth:ors_33_055", "auth:ors_33_075", "auth:ors_33_105"],
            "interval_refs": [x for x in [interval_ref("ti_restraining_order_effective_period")] if x],
            "elements": contempt_elements,
        }
    )

    probate_elements = [
        {
            "element_id": "notice_issued",
            "label": "Probate notice issued",
            "fact_ids": ["f_notice_to_respondent"],
            "status": _fact_status_label(facts_by_id, "f_notice_to_respondent"),
        },
        {
            "element_id": "objection_presented",
            "label": "Respondent objection presented",
            "fact_ids": ["f_respondent_objection_form_present"],
            "status": _fact_status_label(facts_by_id, "f_respondent_objection_form_present"),
        },
        {
            "element_id": "hearing_required",
            "label": "Hearing path triggered under ORS 125.075 / 125.080",
            "fact_ids": ["f_notice_to_respondent", "f_respondent_objection_form_present"],
            "status": "verified"
            if all(_fact_status_label(facts_by_id, fid) == "verified" for fid in ["f_notice_to_respondent", "f_respondent_objection_form_present"])
            else "open",
        },
    ]
    audits.append(
        {
            "audit_id": "audit_probate_objection_hearing_timing",
            "label": "Probate objection and hearing timing audit",
            "governing_authority": ["auth:ors_125_075", "auth:ors_125_080"],
            "interval_refs": [x for x in [interval_ref("ti_probate_notice_objection_window")] if x],
            "elements": probate_elements,
        }
    )

    subpoena_elements = [
        {
            "element_id": "local_search_negative",
            "label": "Local search negative for HACC actor-identification record",
            "fact_ids": ["f_hacc_actor_identification_record_not_found_locally"],
            "status": _fact_status_label(facts_by_id, "f_hacc_actor_identification_record_not_found_locally"),
        },
        {
            "element_id": "compelled_production_needed",
            "label": "Compelled production path identified",
            "fact_ids": ["f_hacc_exhibit_r_requires_compelled_production"],
            "status": _fact_status_label(facts_by_id, "f_hacc_exhibit_r_requires_compelled_production"),
        },
        {
            "element_id": "service_stage_complete",
            "label": "Subpoena service stage complete",
            "fact_ids": ["f_subpoena_service_completed_any"],
            "status": (
                "verified"
                if facts_by_id.get("f_subpoena_service_completed_any") and facts_by_id["f_subpoena_service_completed_any"].value
                else "missing"
            ),
            "note": "Promotes automatically from the active service log once any subpoena service is logged.",
        },
        {
            "element_id": "deficiency_or_compel_stage",
            "label": "Deficiency or compel stage reached",
            "fact_ids": ["f_deficiency_notice_sent_any", "f_motion_to_compel_stage_any"],
            "status": (
                "verified"
                if (
                    (facts_by_id.get("f_deficiency_notice_sent_any") and facts_by_id["f_deficiency_notice_sent_any"].value)
                    or (facts_by_id.get("f_motion_to_compel_stage_any") and facts_by_id["f_motion_to_compel_stage_any"].value)
                )
                else "missing"
            ),
            "note": "Promotes automatically from the active service log when a deficiency notice or motion-to-compel stage is entered.",
        },
        {
            "element_id": "pre_service_only",
            "label": "Subpoena workflow still in pre-service posture",
            "fact_ids": ["f_subpoena_pre_service_phase_only"],
            "status": (
                "verified"
                if facts_by_id.get("f_subpoena_pre_service_phase_only") and facts_by_id["f_subpoena_pre_service_phase_only"].value
                else "inactive"
            ),
            "note": "This captures the current no-service-yet posture when the service log has been initialized but no service entries have been completed.",
        },
    ]
    audits.append(
        {
            "audit_id": "audit_exhibit_r_subpoena_timing",
            "label": "Exhibit R subpoena timing audit",
            "governing_authority": ["auth:orcp_55", "auth:orcp_46"],
            "interval_refs": [x for x in [interval_ref("ti_exhibit_r_compelled_production_track")] if x],
            "elements": subpoena_elements,
        }
    )

    orcp17_elements = [
        {
            "element_id": "sanctions_authority_available",
            "label": "ORCP 17 sanctions authority identified",
            "fact_ids": ["f_authority_orcp_17_improper_purpose_and_support"],
            "status": _fact_status_label(facts_by_id, "f_authority_orcp_17_improper_purpose_and_support"),
        },
        {
            "element_id": "proof_state_caution_present",
            "label": "Proof-state caution preserved for unsupported or inferential allegations",
            "fact_ids": ["f_hacc_named_notice_to_solomon_order_not_found", "f_prior_appointment_source_order_not_found"],
            "status": "verified"
            if all(_fact_status_label(facts_by_id, fid) == "verified" for fid in ["f_hacc_named_notice_to_solomon_order_not_found", "f_prior_appointment_source_order_not_found"])
            else "open",
        },
        {
            "element_id": "improper_purpose_or_unsupported_filing_proof",
            "label": "Improper purpose or unsupported filing proof tied to a specific filing",
            "fact_ids": ["f_client_solomon_barred_refile"],
            "status": "verified"
            if all(
                filing_flag(key)
                for key in [
                    "challenged_filing_identified",
                    "improper_purpose_mapped",
                    "unsupported_legal_position_mapped",
                    "unsupported_factual_assertion_mapped",
                ]
            )
            else "proof_gated",
            "note": "The current record supports inquiry and caution, but final ORCP 17 findings still require the filing-by-filing manifest to identify the challenged filing and map the specific sanction predicates.",
        },
        {
            "element_id": "challenged_filing_identified",
            "label": "Specific challenged filing identified",
            "fact_ids": [],
            "status": "verified" if filing_flag("challenged_filing_identified") else "proof_gated",
            "note": str(orcp17_map.get("challenged_filing_note", "")).strip() or "Awaiting challenged-filing identification.",
        },
        {
            "element_id": "improper_purpose_mapped",
            "label": "Improper purpose mapped to a specific filing",
            "fact_ids": [],
            "status": "verified" if filing_flag("improper_purpose_mapped") else "proof_gated",
            "note": str(orcp17_map.get("improper_purpose_note", "")).strip() or "Awaiting improper-purpose mapping note.",
        },
        {
            "element_id": "unsupported_legal_position_mapped",
            "label": "Unsupported legal position mapped to a specific filing",
            "fact_ids": [],
            "status": "verified" if filing_flag("unsupported_legal_position_mapped") else "proof_gated",
            "note": str(orcp17_map.get("unsupported_legal_position_note", "")).strip() or "Awaiting unsupported-legal-position mapping note.",
        },
        {
            "element_id": "unsupported_factual_assertion_mapped",
            "label": "Unsupported factual assertion mapped to a specific filing",
            "fact_ids": [],
            "status": "verified" if filing_flag("unsupported_factual_assertion_mapped") else "proof_gated",
            "note": str(orcp17_map.get("unsupported_factual_assertion_note", "")).strip() or "Awaiting unsupported-factual-assertion mapping note.",
        },
    ]
    audits.append(
        {
            "audit_id": "audit_orcp17_sanctions_elements",
            "label": "ORCP 17 sanctions element audit",
            "governing_authority": ["auth:orcp_17_c"],
            "interval_refs": [],
            "elements": orcp17_elements,
        }
    )

    issue_preclusion_elements = [
        {
            "element_id": "doctrine_grounded",
            "label": "Issue-preclusion doctrine grounded in Oregon authority",
            "fact_ids": [
                "f_authority_issue_preclusion_elements_official_oregon_cases",
                "f_authority_issue_preclusion_requires_prior_separate_proceeding",
            ],
            "status": "verified"
            if all(
                _fact_status_label(facts_by_id, fid) == "verified"
                for fid in [
                    "f_authority_issue_preclusion_elements_official_oregon_cases",
                    "f_authority_issue_preclusion_requires_prior_separate_proceeding",
                ]
            )
            else "open",
        },
        {
            "element_id": "candidate_refile_theory",
            "label": "Candidate barred-refile theory identified",
            "fact_ids": ["f_collateral_estoppel_candidate", "f_client_solomon_barred_refile"],
            "status": "proof_gated",
            "note": "The local model carries a barred-refile candidate theory, but not yet a certified prior proceeding record proving application of the doctrine.",
        },
        {
            "element_id": "prior_separate_proceeding_record",
            "label": "Prior separate proceeding established by source record",
            "fact_ids": ["f_certified_prior_order_material_present", "f_certified_prior_docket_material_present"],
            "status": "verified"
            if all(
                facts_by_id.get(fid) and facts_by_id[fid].value
                for fid in ["f_certified_prior_order_material_present", "f_certified_prior_docket_material_present"]
            )
            else "missing",
            "note": "Promotes automatically when certified prior-order and docket/register materials are staged in evidence_notes/certified_records.",
        },
        {
            "element_id": "identical_issue_and_finality_mapping",
            "label": "Identical issue, finality, party/privity, and full-and-fair opportunity mapped from certified materials",
            "fact_ids": [
                "f_certified_prior_order_material_present",
                "f_certified_prior_docket_material_present",
                "f_certified_prior_hearing_material_present",
            ],
            "status": "verified"
            if all(
                facts_by_id.get(fid) and facts_by_id[fid].value
                for fid in [
                    "f_certified_prior_order_material_present",
                    "f_certified_prior_docket_material_present",
                    "f_certified_prior_hearing_material_present",
                ]
            ) and all(
                mapped_flag(key)
                for key in [
                    "identical_issue_mapped",
                    "finality_mapped",
                    "party_privity_mapped",
                    "full_fair_opportunity_mapped",
                ]
            )
            else "proof_gated",
            "note": "These elements remain open until certified prior-order, docket, and hearing materials are staged and the issue_preclusion_mapping.json manifest marks the element mapping complete.",
        },
        {
            "element_id": "identical_issue_mapped",
            "label": "Identical issue mapped from certified materials",
            "fact_ids": ["f_certified_prior_order_material_present", "f_certified_prior_docket_material_present"],
            "status": "verified" if mapped_flag("identical_issue_mapped") else "proof_gated",
            "note": str(ip_map.get("identical_issue_note", "")).strip() or "Awaiting element-by-element mapping note.",
        },
        {
            "element_id": "finality_mapped",
            "label": "Finality mapped from certified materials",
            "fact_ids": ["f_certified_prior_order_material_present", "f_certified_prior_docket_material_present"],
            "status": "verified" if mapped_flag("finality_mapped") else "proof_gated",
            "note": str(ip_map.get("finality_note", "")).strip() or "Awaiting finality mapping note.",
        },
        {
            "element_id": "party_privity_mapped",
            "label": "Party or privity alignment mapped from certified materials",
            "fact_ids": ["f_certified_prior_order_material_present", "f_certified_prior_docket_material_present"],
            "status": "verified" if mapped_flag("party_privity_mapped") else "proof_gated",
            "note": str(ip_map.get("party_privity_note", "")).strip() or "Awaiting party/privity mapping note.",
        },
        {
            "element_id": "full_fair_opportunity_mapped",
            "label": "Full and fair opportunity mapped from certified materials",
            "fact_ids": ["f_certified_prior_hearing_material_present"],
            "status": "verified" if mapped_flag("full_fair_opportunity_mapped") else "proof_gated",
            "note": str(ip_map.get("full_fair_opportunity_note", "")).strip() or "Awaiting hearing/opportunity mapping note.",
        },
    ]
    audits.append(
        {
            "audit_id": "audit_issue_preclusion_elements",
            "label": "Issue-preclusion element audit",
            "governing_authority": [
                "auth:oregon_issue_preclusion_cases",
                "auth:oregon_issue_preclusion_prior_separate_proceeding_cases",
            ],
            "interval_refs": [],
            "elements": issue_preclusion_elements,
        }
    )

    return audits


def build_facts(
    ocr_dates: Dict[str, List[str]],
    solomon_events: List[Dict[str, object]],
    solomon_repo_hits: List[Dict[str, object]],
    active_service_rows: List[Dict[str, str]],
) -> List[Fact]:
    g_dates = ocr_dates.get("solomon_motion_for_guardianship_ocr.txt", [])
    ip_map = load_issue_preclusion_mapping()
    r_dates = ocr_dates.get("sam_barber_restraining_order_ocr.txt", [])
    certified_record_hits = {
        "prior_order": False,
        "docket": False,
        "hearing": False,
    }
    if CERTIFIED_RECORDS_DIR.exists():
        for path in CERTIFIED_RECORDS_DIR.iterdir():
            if not path.is_file():
                continue
            low = path.name.lower()
            if any(k in low for k in ["prior_order", "prior-order", "priororder", "judgment", "signed_order"]):
                certified_record_hits["prior_order"] = True
            if any(k in low for k in ["docket", "register", "register_of_actions", "roa"]):
                certified_record_hits["docket"] = True
            if any(k in low for k in ["hearing", "minutes", "appearance", "transcript"]):
                certified_record_hits["hearing"] = True

    ip_mapping_flags = {
        "identical_issue_mapped": bool(ip_map.get("identical_issue_mapped", False)),
        "finality_mapped": bool(ip_map.get("finality_mapped", False)),
        "party_privity_mapped": bool(ip_map.get("party_privity_mapped", False)),
        "full_fair_opportunity_mapped": bool(ip_map.get("full_fair_opportunity_mapped", False)),
    }
    ip_mapping_complete = all(ip_mapping_flags.values())

    overclaim_files = [
        EVIDENCE / "repeated_usurpation_pattern_memo.md",
        FINAL_SET.parent / "petition_guardianship_working_memo.md",
    ]
    overclaim_patterns = [
        "already fully proves",
        "directly proves",
        "barred as a matter of collateral estoppel",
    ]
    overclaim_detected = False
    for p in overclaim_files:
        if not p.exists():
            continue
        txt = p.read_text(encoding="utf-8", errors="ignore").lower()
        if any(token in txt for token in overclaim_patterns):
            overclaim_detected = True
            break

    facts = [
        Fact(
            "f_petition_exists",
            "PetitionFiled",
            ("person:solomon", "case:26PR00641"),
            True,
            "verified",
            "solomon_motion_for_guardianship_ocr.txt",
            _pick_date(g_dates, "2026-03-31"),
        ),
        Fact(
            "f_notice_to_respondent",
            "NoticeIssued",
            ("case:26PR00641", "person:jane_cortez", "2026-04-02"),
            True,
            "verified",
            "solomon_motion_for_guardianship_ocr.txt",
            _pick_date(g_dates, "2026-04-02"),
        ),
        Fact(
            "f_respondent_objection_form_present",
            "RespondentObjectionFormPresent",
            ("case:26PR00641", "person:jane_cortez"),
            True,
            "verified",
            "guardianship_timeline.md",
            ("2026-04-05",),
        ),
        Fact(
            "f_petition_claims_no_prior_guardian",
            "PetitionStatesNoPriorGuardian",
            ("case:26PR00641", "person:jane_cortez"),
            True,
            "verified",
            "solomon_motion_for_guardianship_ocr.txt",
            _pick_date(g_dates, "2026-03-31"),
        ),
        Fact(
            "f_prior_appointment_source_order_not_found",
            "SourceOrderNotFoundInRepository",
            ("issue:prior_appointment_for_jane_cortez",),
            True,
            "verified",
            "deontic_logic_gap_review_2026-04-07.md",
            ("2026-04-07",),
        ),
        Fact(
            "f_certified_prior_order_material_present",
            "CertifiedPriorOrderMaterialPresent",
            ("issue:prior_separate_proceeding_record",),
            certified_record_hits["prior_order"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_certified_prior_docket_material_present",
            "CertifiedPriorDocketMaterialPresent",
            ("issue:prior_separate_proceeding_record",),
            certified_record_hits["docket"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_certified_prior_docket_material_missing",
            "CertifiedPriorDocketMaterialMissing",
            ("issue:prior_separate_proceeding_record",),
            not certified_record_hits["docket"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_certified_prior_hearing_material_present",
            "CertifiedPriorHearingMaterialPresent",
            ("issue:prior_separate_proceeding_record",),
            certified_record_hits["hearing"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_certified_prior_order_material_missing",
            "CertifiedPriorOrderMaterialMissing",
            ("issue:prior_separate_proceeding_record",),
            not certified_record_hits["prior_order"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_certified_prior_hearing_material_missing",
            "CertifiedPriorHearingMaterialMissing",
            ("issue:prior_separate_proceeding_record",),
            not certified_record_hits["hearing"],
            "verified",
            str(CERTIFIED_RECORDS_DIR.name),
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_mapping_completed",
            "IssuePreclusionMappingCompleted",
            ("issue:guardianship_authority",),
            ip_mapping_complete,
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_mapping_incomplete",
            "IssuePreclusionMappingIncomplete",
            ("issue:guardianship_authority",),
            not ip_mapping_complete,
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_finality_element_mapped",
            "IssuePreclusionFinalityElementMapped",
            ("issue:guardianship_authority",),
            ip_mapping_flags["finality_mapped"],
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_full_fair_element_mapped",
            "IssuePreclusionFullFairElementMapped",
            ("issue:guardianship_authority",),
            ip_mapping_flags["full_fair_opportunity_mapped"],
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_finality_element_missing",
            "IssuePreclusionFinalityElementMissing",
            ("issue:guardianship_authority",),
            not ip_mapping_flags["finality_mapped"],
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_issue_preclusion_full_fair_element_missing",
            "IssuePreclusionFullFairElementMissing",
            ("issue:guardianship_authority",),
            not ip_mapping_flags["full_fair_opportunity_mapped"],
            "verified",
            ISSUE_PRECLUSION_MAPPING_FILE.name,
            (str(date.today()),),
        ),
        Fact(
            "f_overclaim_issue_preclusion_statement_detected",
            "OverclaimIssuePreclusionStatementDetected",
            ("repo:collateral_estoppel_workspace",),
            overclaim_detected,
            "verified",
            "repeated_usurpation_pattern_memo.md | petition_guardianship_working_memo.md",
            (str(date.today()),),
        ),
        Fact("f_client_prior_appointment", "PriorAppointmentExists", ("person:jane_cortez", "person:benjamin_barber"), True, "alleged", "client_assertion"),
        Fact("f_client_solomon_avoided_service", "AvoidedService", ("person:solomon", "order:prior_guardianship_order"), True, "alleged", "client_assertion"),
        Fact("f_client_solomon_order_disregard", "DisregardedOrder", ("person:solomon", "order:prior_guardianship_order"), True, "alleged", "client_assertion"),
        Fact("f_client_solomon_housing_interference", "Interference", ("person:solomon", "process:hacc_housing_contract"), True, "alleged", "client_assertion"),
        Fact(
            "f_solomon_actual_notice_on_2025_11_17",
            "ActualNotice",
            ("person:solomon", "order:eppdapa_restraining_order"),
            True,
            "verified",
            "uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml",
            ("2025-11-17",),
        ),
        Fact(
            "f_solomon_order_filed_on_2025_11_19",
            "OrderFiled",
            ("order:eppdapa_restraining_order", "person:jane_cortez", "person:solomon"),
            True,
            "verified",
            "14161-Me-to-solomon-gv-b2df7cbf8706d9fe/transcript.txt",
            ("2025-11-19",),
        ),
        Fact(
            "f_client_solomon_failed_appearance",
            "FailedToAppear",
            ("person:solomon", "proceeding:related_order_hearing"),
            True,
            "alleged",
            "client_assertion",
            ("2026-03-10",),
        ),
        Fact(
            "f_client_solomon_barred_refile",
            "RefiledBarredIssue",
            ("person:solomon", "issue:guardianship_authority"),
            True,
            "alleged",
            "client_assertion",
            ("2026-03-31",),
        ),
        Fact(
            "f_restraining_order_granted",
            "OrderGranted",
            ("order:eppdapa_restraining_order", "person:jane_cortez", "person:solomon"),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_in_effect",
            "OrderInEffect",
            ("order:eppdapa_restraining_order",),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_no_further_service_needed",
            "NoFurtherServiceNeeded",
            ("order:eppdapa_restraining_order", "person:solomon"),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_gal_appoints_benjamin_for_jane",
            "OrderAppointsGAL",
            ("order:eppdapa_restraining_order", "person:benjamin_barber", "person:jane_cortez"),
            True,
            "verified",
            "restraining_order_visual_verification_2026-04-07.md",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_solomon_named_respondent",
            "OrderNamesRespondent",
            ("order:eppdapa_restraining_order", "person:solomon"),
            True,
            "verified",
            "restraining_order_visual_verification_2026-04-07.md",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_requires_follow_guardian_or_conservator_instructions",
            "OrderRequiresFollowGuardianOrConservatorInstructions",
            ("order:eppdapa_restraining_order", "person:solomon", "person:jane_cortez"),
            True,
            "verified",
            "restraining_order_visual_verification_2026-04-07.md",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_contact_restrictions",
            "OrderRestrictsContact",
            ("order:eppdapa_restraining_order", "person:solomon", "person:jane_cortez"),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_residence_restrictions",
            "OrderRestrictsResidenceAccess",
            ("order:eppdapa_restraining_order", "person:solomon", "location:10043_se_32nd_ave"),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_property_restrictions",
            "OrderRestrictsPropertyControl",
            ("order:eppdapa_restraining_order", "person:solomon", "person:jane_cortez"),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_restraining_order_one_year_duration",
            "OrderDurationOneYear",
            ("order:eppdapa_restraining_order",),
            True,
            "verified",
            "sam_barber_restraining_order_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_solomon_noncooperation_statement",
            "NoncooperationStatement",
            ("person:solomon", "order:eppdapa_restraining_order"),
            True,
            "verified",
            "14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt",
            ("2026-03-10",),
        ),
        Fact(
            "f_solomon_service_position_statement",
            "ServicePositionStatement",
            ("person:solomon", "order:eppdapa_restraining_order"),
            True,
            "verified",
            "14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt",
            ("2026-03-10",),
        ),
        Fact(
            "f_message_requested_service_address_2025_11_17",
            "MessageRequestServiceAddress",
            ("person:benjamin_barber", "person:solomon"),
            True,
            "verified",
            "14159-solomon-gv-ed9289921a300dc7/transcript.txt",
            ("2025-11-17",),
        ),
        Fact(
            "f_message_requested_service_address_2025_11_20",
            "MessageRequestServiceAddress",
            ("person:benjamin_barber", "person:solomon"),
            True,
            "verified",
            "14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_message_stated_intent_alternative_service_if_avoidance_2025_11_21",
            "MessageStatedAlternativeServiceIfAvoidance",
            ("person:benjamin_barber", "person:solomon"),
            True,
            "verified",
            "14165-Me-to-solomon-gv-e6594297d713efde/transcript.txt",
            ("2025-11-21",),
        ),
        Fact(
            "f_counsel_disclaimed_accepting_service_for_solomon_2026_04_04",
            "CounselDisclaimedAcceptingServiceForClient",
            ("person:solomon", "person:alex_bluestone"),
            True,
            "verified",
            "msg_CO1PR10MB44826703707F0BD1A5D81F64AC5FA-CO1PR10MB4482.namprd10.prod.outlook.com_20260404_Re-SERVICE.../message.json",
            ("2026-04-04",),
        ),
        Fact(
            "f_service_email_sent_to_alex_bluestone_re_jane_solomon_2026_04_03",
            "ServiceEmailSentToCounsel",
            ("person:benjamin_barber", "person:alex_bluestone", "person:solomon", "person:jane_cortez"),
            True,
            "verified",
            "msg_CAMTdTS--K-3f4FAEGwKV5TY9qYTnsswDvLK_1XjMwQ50VY4ENw-mail.gmail.com_20260403_SERVICE.../message.json",
            ("2026-04-03",),
        ),
        Fact(
            "f_bluestone_acknowledged_representation_for_jane_guardianship_2026_04_04",
            "CounselAcknowledgedRepresentationForJaneGuardianshipMatter",
            ("person:alex_bluestone", "person:solomon", "person:jane_cortez"),
            True,
            "verified",
            "msg_CO1PR10MB44826703707F0BD1A5D81F64AC5FA-CO1PR10MB4482.namprd10.prod.outlook.com_20260404_Re-SERVICE.../message.json",
            ("2026-04-04",),
        ),
        Fact(
            "f_service_channel_conflict_or_evasion_pattern_documented",
            "ServiceChannelConflictOrEvasionPatternDocumented",
            ("person:solomon",),
            True,
            "verified",
            "r5_r24_service_evasion_text_chain_2026-04-07.md",
            ("2025-11-17", "2025-11-20", "2025-11-21", "2026-03-10", "2026-04-04"),
        ),
        Fact(
            "f_motion_to_waive_or_modify_notice_re_gal_filed_2025_11_20",
            "MotionToWaiveOrModifyNoticeReGALFiled",
            ("person:benjamin_barber", "person:jane_cortez", "person:solomon"),
            True,
            "verified",
            "14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_order_on_motion_to_waive_or_modify_notice_re_gal_granted_2025_11_20",
            "OrderOnMotionToWaiveOrModifyNoticeReGALGranted",
            ("person:jane_cortez", "person:solomon"),
            True,
            "verified",
            "14164-Me-to-solomon-gv-3f38fb3f900d4de1/enrichments/solomon - Text - 2025-11-20T19_06_58Z-10-1.image_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_order_notice_requirements_orcp27_waived_or_modified_2025_11_20",
            "OrderNoticeRequirementsORCP27WaivedOrModified",
            ("person:jane_cortez", "person:solomon"),
            True,
            "verified",
            "14164-Me-to-solomon-gv-3f38fb3f900d4de1/enrichments/solomon - Text - 2025-11-20T19_06_58Z-10-1.image_ocr.txt",
            ("2025-11-20",),
        ),
        Fact(
            "f_hacc_lease_adjustment_effective_2026_01_01",
            "LeaseAdjustmentEffective",
            ("org:hacc", "household:jane_cortez_household", "2026-01-01"),
            True,
            "verified",
            "HACC vawa violation.pdf",
            ("2026-01-01",),
        ),
        Fact(
            "f_hacc_removed_benjamin_effective_2026_01_01",
            "HouseholdMemberRemovedEffective",
            ("org:hacc", "person:benjamin_barber", "household:jane_cortez_household", "2026-01-01"),
            True,
            "verified",
            "0014-Re-Allegations-of-Fraud---JC-Household/message.eml",
            ("2026-01-01", "2026-01-12"),
        ),
        Fact(
            "f_hacc_internal_review_claimed",
            "HaccInternalReviewClaimed",
            ("org:hacc", "household:jane_cortez_household"),
            True,
            "verified",
            "0014-Re-Allegations-of-Fraud---JC-Household/message.eml",
            ("2026-01-12",),
        ),
        Fact(
            "f_hacc_court_documentation_basis_claimed",
            "HaccCourtDocumentationBasisClaimed",
            ("org:hacc", "household:jane_cortez_household"),
            True,
            "verified",
            "0014-Re-Allegations-of-Fraud---JC-Household/message.eml",
            ("2026-01-12",),
        ),
        Fact(
            "f_hacc_actor_identification_record_not_found_locally",
            "LocalSearchNegativeForActorIdentificationRecord",
            ("org:hacc", "issue:lease_change_actor_identification"),
            True,
            "verified",
            "missing_exhibit_search_status_2026-04-07.md",
            ("2026-04-07",),
        ),
        Fact(
            "f_hacc_exhibit_r_requires_compelled_production",
            "CompelledProductionRequired",
            ("issue:lease_change_actor_identification", "org:hacc"),
            True,
            "verified",
            "subpoena_target_memo_hacc_lease_authority_record.md",
            ("2026-04-07",),
        ),
        Fact(
            "f_january_2026_hacc_removed_benjamin_restored_restrained_party",
            "LeaseRemovalAndRestorationNarrative",
            ("org:hacc", "person:benjamin_barber", "person:restrained_party"),
            True,
            "alleged",
            "did-key-hacc-temp-session.json",
            ("2026-01",),
        ),
        Fact(
            "f_solomon_interference_with_hacc_lease_theory",
            "InterferenceTheory",
            ("person:solomon", "process:hacc_household_composition_and_lease"),
            True,
            "alleged",
            "solomon_interference_and_lease_tampering_theory.md",
            ("2026-01",),
        ),
        Fact(
            "f_hacc_named_notice_to_solomon_order_not_found",
            "NamedHaccNoticeMessageNotFound",
            ("org:hacc", "order:eppdapa_restraining_order", "person:solomon"),
            True,
            "verified",
            "protective_order_and_hacc_notice_timeline.md",
            ("2026-04-07",),
        ),
        Fact(
            "f_ashley_ferron_case_26P000432_denied",
            "ProtectivePetitionDenied",
            ("case:26P000432", "person:jane_cortez", "person:ashley_ferron"),
            True,
            "verified",
            "protective_order_and_hacc_notice_timeline.md",
            ("2026-01-26",),
        ),
        Fact(
            "f_ashley_ferron_case_26P000433_denied",
            "ProtectivePetitionDenied",
            ("case:26P000433", "person:benjamin_barber", "person:ashley_ferron"),
            True,
            "verified",
            "protective_order_and_hacc_notice_timeline.md",
            ("2026-01-26",),
        ),
        Fact(
            "f_julio_order_case_25PO11318_exists",
            "RestrainingOrderExists",
            ("case:25PO11318", "person:julio_cortez"),
            True,
            "verified",
            "protective_order_and_hacc_notice_timeline.md",
            ("2025-11-17",),
        ),
        Fact(
            "f_hacc_process_exists",
            "HousingProcessActive",
            ("org:hacc", "person:jane_cortez", "process:hacc_housing_contract"),
            True,
            "verified",
            "0014-Re-Allegations-of-Fraud---JC-Household/message.eml",
            ("2026-01-12",),
        ),
        Fact("f_collateral_estoppel_candidate", "PotentialIssuePreclusion", ("issue:guardianship_authority",), True, "theory", "motion_to_dismiss_for_collateral_estoppel.md"),
        Fact(
            "f_actor_assignment_conflict_benjamin_vs_solomon_interference",
            "ActorAssignmentConflict",
            ("issue:interference_actor_assignment", "person:benjamin_barber", "person:solomon"),
            True,
            "verified",
            "generate_formal_reasoning_artifacts.py",
            (str(date.today()),),
        ),
    ]

    # Subpoena/deadline workflow facts from staged filing set.
    protocol_file = FINAL_SET / "11B_attachment_a2_definitions_and_instructions_final.md"
    cover_file = FINAL_SET / "19_subpoena_cover_instruction_sheet_final.md"
    checklist_file = FINAL_SET / "18_subpoena_custodian_compliance_checklist_final.md"
    search_report_template_file = FINAL_SET / "21_search_execution_report_template_final.md"
    deficiency_file = FINAL_SET / "22_subpoena_deficiency_notice_template_final.md"
    declaration_file = FINAL_SET / "23_declaration_re_subpoena_noncompliance_final.md"
    compel_file = FINAL_SET / "24_motion_to_compel_subpoena_compliance_and_sanctions_final.md"
    manifests_file = FINAL_SET / "25_ready_to_serve_recipient_manifests_final.md"
    deadline_guide_file = FINAL_SET / "30_service_deadline_calculator_guide_final.md"
    deadline_template_file = FINAL_SET / "31_service_deadline_calculator_template.csv"
    authority_placeholder_file = FINAL_SET / "06_oregon_authority_table_final.md"

    staged_components = [
        cover_file,
        checklist_file,
        search_report_template_file,
        deficiency_file,
        declaration_file,
        compel_file,
        manifests_file,
        deadline_guide_file,
        deadline_template_file,
    ]

    facts.append(
        Fact(
            "f_subpoena_workflow_components_staged",
            "SubpoenaWorkflowComponentsStaged",
            ("case:26PR00641",),
            all(p.exists() for p in staged_components),
            "verified",
            "final_filing_set",
            (str(date.today()),),
        )
    )

    protocol_has_or_blocks = False
    if protocol_file.exists():
        txt = protocol_file.read_text(encoding="utf-8", errors="ignore")
        low = txt.lower()
        has_range_hint = ("paragraphs 10-27" in low) or (re.search(r"(?m)^10\.", txt) is not None and re.search(r"(?m)^27\.", txt) is not None)
        has_or_signal = (" or " in low) or ("or-joined" in low)
        has_report_req = "search execution report" in low
        protocol_has_or_blocks = bool(has_range_hint and has_or_signal and has_report_req)
    facts.append(
        Fact(
            "f_or_joined_search_protocol_defined",
            "OrJoinedSearchProtocolDefined",
            ("doc:11B_attachment_a2_definitions_and_instructions_final.md",),
            protocol_has_or_blocks,
            "verified",
            str(protocol_file.name),
            (str(date.today()),),
        )
    )

    authority_placeholders_unresolved = True
    if authority_placeholder_file.exists():
        authority_text = authority_placeholder_file.read_text(encoding="utf-8", errors="ignore")
        authority_placeholders_unresolved = "[insert" in authority_text.lower()

    facts.append(
        Fact(
            "f_authority_table_placeholders_unresolved",
            "AuthorityCitationsUnresolved",
            ("doc:06_oregon_authority_table_final.md",),
            authority_placeholders_unresolved,
            "verified",
            authority_placeholder_file.name,
            (str(date.today()),),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_33_055_remedial_contempt_procedure",
            "AuthorityAvailable",
            ("auth:ors_33_055", "topic:remedial_contempt_procedure"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_33_075_compel_appearance",
            "AuthorityAvailable",
            ("auth:ors_33_075", "topic:compel_appearance_after_order_to_appear"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_33_105_remedial_sanctions",
            "AuthorityAvailable",
            ("auth:ors_33_105", "topic:remedial_contempt_sanctions"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_orcp_17_improper_purpose_and_support",
            "AuthorityAvailable",
            ("auth:orcp_17_c", "topic:improper_purpose_and_fact_law_support"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_orcp_46_discovery_sanctions",
            "AuthorityAvailable",
            ("auth:orcp_46", "topic:discovery_motion_expenses_and_just_orders"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_orcp_55_subpoena_obedience",
            "AuthorityAvailable",
            ("auth:orcp_55", "topic:subpoena_must_be_obeyed_unless_judge_orders_otherwise"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_124_020_eppdapa_restraining_relief",
            "AuthorityAvailable",
            ("auth:ors_124_020", "topic:eppdapa_restraining_order_relief"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_050_protective_orcp_oec",
            "AuthorityAvailable",
            ("auth:ors_125_050", "topic:orcp_and_oec_apply_in_protective_proceedings"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_060_notice_recipients",
            "AuthorityAvailable",
            ("auth:ors_125_060", "topic:protective_proceeding_notice_recipients"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_065_notice_manner_and_timing",
            "AuthorityAvailable",
            ("auth:ors_125_065", "topic:protective_proceeding_notice_manner_and_timing"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_075_objections",
            "AuthorityAvailable",
            ("auth:ors_125_075", "topic:protective_proceeding_objections"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_080_hearing_and_counsel",
            "AuthorityAvailable",
            ("auth:ors_125_080", "topic:protective_proceeding_hearing_and_counsel"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_ors_125_120_protected_person_special_advocate",
            "AuthorityAvailable",
            ("auth:ors_125_120", "topic:protected_person_special_advocate"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_orcp_9_service_of_later_filed_papers",
            "AuthorityAvailable",
            ("auth:orcp_9", "topic:service_of_later_filed_papers"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_orcp_10_time_computation",
            "AuthorityAvailable",
            ("auth:orcp_10", "topic:time_computation_and_additional_service_days"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_issue_preclusion_elements_official_oregon_cases",
            "AuthorityAvailable",
            ("auth:oregon_issue_preclusion_cases", "topic:issue_preclusion_elements_and_identical_issue"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_issue_preclusion_requires_prior_separate_proceeding",
            "AuthorityAvailable",
            ("auth:oregon_issue_preclusion_prior_separate_proceeding_cases", "topic:prior_separate_proceeding_requirement"),
            True,
            "verified",
            "oregon_authority_grounding_memo_2026-04-07.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_case_nelson_1993",
            "AuthorityCaseAvailable",
            ("case:nelson_v_emerald_peoples_utility_dist_1993", "topic:issue_preclusion_elements"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_case_rawls_2010",
            "AuthorityCaseAvailable",
            ("case:rawls_v_evans_2010", "topic:issue_preclusion_elements"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_case_hayes_oyster_2005",
            "AuthorityCaseAvailable",
            ("case:hayes_oyster_v_dulcich_2005", "topic:prior_separate_proceeding_requirement"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_case_westwood_2002",
            "AuthorityCaseAvailable",
            ("case:westwood_construction_v_hallmark_inns_2002", "topic:prior_separate_proceeding_requirement"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_clackamas_slr_9_035_probate_practice",
            "AuthorityAvailable",
            ("auth:clackamas_slr_9_035", "topic:clackamas_probate_local_rule_practice"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )
    facts.append(
        Fact(
            "f_authority_clackamas_slr_9_076_probate_practice",
            "AuthorityAvailable",
            ("auth:clackamas_slr_9_076", "topic:clackamas_probate_local_rule_practice"),
            True,
            "verified",
            "06_oregon_authority_table_final.md",
            ("2026-04-07",),
        )
    )

    for ev in solomon_events:
        event_id = str(ev.get("event_id", "")).strip()
        predicate = str(ev.get("predicate", "")).strip()
        status = str(ev.get("status", "alleged")).strip() or "alleged"
        if not event_id or not predicate:
            continue

        actor = str(ev.get("actor", "unknown:actor"))
        target = str(ev.get("target", "unknown:target"))
        dt = ev.get("date")
        dates: Tuple[str, ...] = (str(dt),) if dt else ()
        facts.append(
            Fact(
                fact_id=f"f_feed_{event_id}",
                predicate=predicate,
                args=(actor, target),
                value=True,
                status=status,
                source=str(ev.get("source", str(SOLOMON_FEED))),
                dates=dates,
                confidence_level=(str(ev.get("confidence_level")) if ev.get("confidence_level") is not None else None),
                confidence_score=(float(ev.get("confidence_score")) if ev.get("confidence_score") is not None else None),
                evidence_kind=(str(ev.get("evidence_kind")) if ev.get("evidence_kind") is not None else None),
            )
        )

    # Bridge in repository evidence mentions as additional fact nodes.
    # Keep high/medium relevance only to avoid graph bloat from weak hits.
    for idx, hit in enumerate(solomon_repo_hits):
        relevance = str(hit.get("relevance", "")).strip().lower()
        if relevance not in {"high", "medium"}:
            continue
        rel_path = str(hit.get("relative_path", "")).strip()
        if not rel_path:
            continue
        dates = tuple(str(x) for x in hit.get("dates_found", [])[:3] if x)
        facts.append(
            Fact(
                fact_id=f"f_repo_solomon_mention_{idx+1}",
                predicate="RepositorySourceMentionsSolomonCaseContext",
                args=("person:solomon", f"source:{rel_path}"),
                value=True,
                status="verified",
                source=rel_path,
                dates=dates,
                confidence_level="medium_high" if relevance == "high" else "medium",
                confidence_score=0.8 if relevance == "high" else 0.7,
                evidence_kind="repository_index_extract",
            )
        )

    if active_service_rows:
        observed_dates: List[str] = []
        for row in active_service_rows:
            for key in (
                "log_date",
                "date_served",
                "production_due",
                "date_production_received",
                "deficiency_notice_sent",
                "cure_deadline",
                "cure_received",
                "motion_to_compel_filed",
            ):
                d = _extract_iso_date(row.get(key, ""))
                if d:
                    observed_dates.append(d)
        inferred_date = max(observed_dates) if observed_dates else str(date.today())

        facts.append(
            Fact(
                "f_active_service_log_initialized",
                "ActiveServiceLogInitialized",
                ("case:26PR00641",),
                True,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )

        ready_count = 0
        served_count = 0
        deficiency_count = 0
        incomplete_response_count = 0
        compel_stage_count = 0
        for row in active_service_rows:
            status = row.get("status", "").lower()
            date_served = _extract_iso_date(row.get("date_served", ""))
            production_due = _extract_iso_date(row.get("production_due", ""))
            date_production_received = _extract_iso_date(row.get("date_production_received", ""))
            deficiency_sent = _extract_iso_date(row.get("deficiency_notice_sent", ""))
            compel_filed = _extract_iso_date(row.get("motion_to_compel_filed", ""))

            checklist_received = (row.get("checklist_received", "") or "").strip().lower()
            search_report_received = (row.get("search_report_received", "") or "").strip().lower()

            if status == "ready_to_serve":
                ready_count += 1
            if status in {"served", "awaiting_production", "production_received", "deficiency_notice_stage", "motion_to_compel_stage"} or date_served:
                served_count += 1
            if status in {"deficiency_notice_stage", "motion_to_compel_stage"} or deficiency_sent:
                deficiency_count += 1
            if status in {"motion_to_compel_stage"} or compel_filed:
                compel_stage_count += 1

            # Incomplete response heuristic (temporal):
            # - explicit deficiency/compel stage, or
            # - production received but required artifacts missing, or
            # - production overdue after service and still missing production/artifacts.
            overdue_after_service = bool(date_served and production_due and production_due < str(date.today()))
            artifacts_missing = checklist_received in {"n", "no", "false", ""} or search_report_received in {"n", "no", "false", ""}
            if (
                status in {"deficiency_notice_stage", "motion_to_compel_stage"}
                or (status == "production_received" and artifacts_missing)
                or (overdue_after_service and (not date_production_received or artifacts_missing))
            ):
                incomplete_response_count += 1

        facts.append(
            Fact(
                "f_subpoena_recipients_ready_to_serve",
                "SubpoenaRecipientsReadyToServe",
                ("case:26PR00641", "count:6"),
                ready_count >= 6,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )
        facts.append(
            Fact(
                "f_subpoena_service_completed_any",
                "SubpoenaServiceCompletedAny",
                ("case:26PR00641",),
                served_count > 0,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )
        facts.append(
            Fact(
                "f_subpoena_pre_service_phase_only",
                "SubpoenaPreServicePhaseOnly",
                ("case:26PR00641",),
                served_count == 0,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )
        facts.append(
            Fact(
                "f_deficiency_notice_sent_any",
                "DeficiencyNoticeSentAny",
                ("case:26PR00641",),
                deficiency_count > 0,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )
        facts.append(
            Fact(
                "f_subpoena_response_incomplete_any",
                "SubpoenaResponseIncompleteAny",
                ("case:26PR00641",),
                incomplete_response_count > 0,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )
        facts.append(
            Fact(
                "f_motion_to_compel_stage_any",
                "MotionToCompelStageAny",
                ("case:26PR00641",),
                compel_stage_count > 0,
                "verified",
                ACTIVE_SERVICE_LOG.name,
                (inferred_date,),
            )
        )

    return facts


def build_rules() -> List[Rule]:
    return [
        Rule(
            "r1_guardian_permission_if_prior_appointment",
            ("f_authority_ors_125_050_protective_orcp_oec", "f_client_prior_appointment"),
            DeonticConclusion(
                "c1_benjamin_permitted_guardian_scope",
                "P",
                "person:benjamin_barber",
                "act_within_valid_guardian_scope",
                "person:jane_cortez",
            ),
            "If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.",
            "hypothesis",
            ("auth:ors_125_050",),
        ),
        Rule(
            "r2_target_noninterference_prohibition_if_prior_appointment",
            ("f_authority_ors_125_050_protective_orcp_oec", "f_client_prior_appointment", "f_client_solomon_housing_interference"),
            DeonticConclusion(
                "c2_target_forbidden_interference",
                "F",
                "person:solomon",
                "interfere_with_guardian_or_housing_process",
                "process:hacc_housing_contract",
            ),
            "If prior appointment exists and interference is alleged, the alleged interfering actor is forbidden from interference.",
            "hypothesis",
            ("auth:ors_125_050",),
        ),
        Rule(
            "r3_target_obligation_comply_or_seek_relief_if_prior_appointment",
            ("f_authority_ors_125_050_protective_orcp_oec", "f_client_prior_appointment", "f_client_solomon_order_disregard"),
            DeonticConclusion(
                "c3_target_obligated_comply_or_seek_relief",
                "O",
                "person:solomon",
                "comply_with_order_or_seek_relief",
                "order:prior_guardianship_order",
            ),
            "If prior appointment is in force and an alleged actor disregarded the order, that actor was obligated to comply or seek relief.",
            "hypothesis",
            ("auth:ors_125_050",),
        ),
        Rule(
            "r40_benjamin_permitted_act_as_gal_under_signed_eppdapa_order",
            (
                "f_authority_ors_124_020_eppdapa_restraining_relief",
                "f_restraining_order_gal_appoints_benjamin_for_jane",
                "f_restraining_order_in_effect",
            ),
            DeonticConclusion(
                "c40_benjamin_permitted_act_as_gal_under_signed_eppdapa_order",
                "P",
                "person:benjamin_barber",
                "act_as_gal_within_signed_eppdapa_order_scope",
                "person:jane_cortez",
            ),
            "If ORS 124.020 authority is available and the signed EPPDAPA order appoints Benjamin as GAL for Jane, Benjamin is permitted to act within that order scope.",
            "filing",
            ("auth:ors_124_020", "order:eppdapa_restraining_order"),
        ),
        Rule(
            "r41_solomon_obligated_follow_petitioner_guardian_or_conservator_instructions",
            (
                "f_authority_ors_124_020_eppdapa_restraining_relief",
                "f_restraining_order_solomon_named_respondent",
                "f_restraining_order_requires_follow_guardian_or_conservator_instructions",
                "f_restraining_order_in_effect",
            ),
            DeonticConclusion(
                "c41_solomon_obligated_follow_petitioner_guardian_or_conservator_instructions",
                "O",
                "person:solomon",
                "follow_petitioner_guardian_or_conservator_instructions",
                "person:jane_cortez",
            ),
            "If ORS 124.020 authority is available and the signed EPPDAPA order requires it, Solomon is obligated to follow petitioner guardian or conservator instructions while the order is in effect.",
            "filing",
            ("auth:ors_124_020", "order:eppdapa_restraining_order"),
        ),
        Rule(
            "r42_solomon_forbidden_disobey_guardian_instruction_term_after_appearance",
            (
                "f_authority_ors_124_020_eppdapa_restraining_relief",
                "f_restraining_order_solomon_named_respondent",
                "f_restraining_order_requires_follow_guardian_or_conservator_instructions",
                "f_restraining_order_no_further_service_needed",
            ),
            DeonticConclusion(
                "c42_solomon_forbidden_disobey_guardian_instruction_term_after_appearance",
                "F",
                "person:solomon",
                "disobey_guardian_instruction_term_after_appearance",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon is the named respondent and no further service was required because he appeared, disobeying the signed guardian-instruction term is forbidden in this model.",
            "filing",
            ("auth:ors_124_020", "order:eppdapa_restraining_order"),
        ),
        Rule(
            "r4_solomon_forbidden_abuse_contact_property_control",
            (
                "f_solomon_actual_notice_on_2025_11_17",
                "f_restraining_order_granted",
                "f_restraining_order_in_effect",
                "f_restraining_order_contact_restrictions",
                "f_restraining_order_property_restrictions",
            ),
            DeonticConclusion(
                "c4_solomon_forbidden_contact_property_control",
                "F",
                "person:solomon",
                "abuse_contact_or_control_property",
                "person:jane_cortez",
            ),
            "Given granted in-effect restraining order with property restrictions, Solomon is forbidden to abuse/contact/interfere/control property.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r4b_solomon_forbidden_enter_residence",
            (
                "f_solomon_actual_notice_on_2025_11_17",
                "f_restraining_order_granted",
                "f_restraining_order_residence_restrictions",
            ),
            DeonticConclusion(
                "c4b_solomon_forbidden_enter_residence",
                "F",
                "person:solomon",
                "enter_or_remain_at_petitioner_residence",
                "location:10043_se_32nd_ave",
            ),
            "Given the granted restraining order and residence restriction, Solomon is forbidden from entering or remaining at the protected residence.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r5_solomon_obligated_appear_and_answer",
            ("f_restraining_order_no_further_service_needed", "f_client_solomon_failed_appearance"),
            DeonticConclusion(
                "c5_solomon_obligated_appear_and_answer",
                "O",
                "person:solomon",
                "appear_and_answer_show_cause",
                "proceeding:related_order_hearing",
            ),
            "If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.",
            "hypothesis",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r5b_solomon_obligated_seek_hearing_or_comply",
            (
                "f_restraining_order_granted",
                "f_restraining_order_in_effect",
                "f_solomon_service_position_statement",
            ),
            DeonticConclusion(
                "c5b_solomon_obligated_seek_hearing_or_comply",
                "O",
                "person:solomon",
                "seek_hearing_or_comply_with_existing_order",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon stated he would comply only once served despite an already in-effect order, he was obligated to seek a hearing or comply rather than self-suspend effectiveness.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r5c_solomon_forbidden_self_help_noncooperation",
            (
                "f_restraining_order_granted",
                "f_restraining_order_in_effect",
                "f_solomon_noncooperation_statement",
            ),
            DeonticConclusion(
                "c5c_solomon_forbidden_self_help_noncooperation",
                "F",
                "person:solomon",
                "adopt_self_help_noncooperation_posture",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon adopted an explicit noncooperation posture after the granted in-effect order, self-help noncooperation is forbidden.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r6_hacc_obligated_document_authority_chain_for_lease_change",
            ("f_hacc_removed_benjamin_effective_2026_01_01", "f_hacc_internal_review_claimed", "f_hacc_court_documentation_basis_claimed"),
            DeonticConclusion(
                "c6_hacc_obligated_document_authority_chain_for_lease_change",
                "O",
                "org:hacc",
                "identify_actor_document_and_authority_chain_for_lease_change",
                "household:jane_cortez_household",
            ),
            "If HACC states that a lease change followed internal review and court documentation on file, HACC is obligated in this model to identify the actor, document, and authority chain behind that change.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r6b_hacc_obligated_document_lease_basis",
            ("f_hacc_lease_adjustment_effective_2026_01_01", "f_hacc_removed_benjamin_effective_2026_01_01"),
            DeonticConclusion(
                "c6b_hacc_obligated_document_lease_basis",
                "O",
                "org:hacc",
                "document_basis_for_household_composition_or_lease_adjustment",
                "household:jane_cortez_household",
            ),
            "If HACC implemented a January 1, 2026 lease adjustment, HACC was obligated to document the basis for that household-composition change.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r6c_solomon_interference_not_proved_by_named_hacc_notice_gap",
            ("f_hacc_named_notice_to_solomon_order_not_found",),
            DeonticConclusion(
                "c6c_solomon_interference_not_yet_directly_proved",
                "P",
                "case:guardianship_collateral_estoppel",
                "treat_solomon_hacc_interference_as_inference_not_direct_proof",
                "person:solomon",
            ),
            "Because no named HACC notice message about the Solomon order has been found in preserved mail, the HACC-interference theory should presently be treated as an inference rather than direct proof.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r6d_case_obligated_treat_prior_appointment_as_hypothesis_only",
            ("f_prior_appointment_source_order_not_found",),
            DeonticConclusion(
                "c6d_case_obligated_treat_prior_appointment_as_hypothesis_only",
                "O",
                "case:guardianship_collateral_estoppel",
                "treat_prior_appointment_theory_as_hypothesis_until_source_order_found",
                "issue:prior_appointment_for_jane_cortez",
            ),
            "If no source order has been found for the claimed prior appointment, the prior-appointment theory must remain hypothesis-only in filing-facing outputs.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain",
            ("f_hacc_actor_identification_record_not_found_locally", "f_hacc_exhibit_r_requires_compelled_production"),
            DeonticConclusion(
                "c6e_case_permitted_seek_compelled_production_for_hacc_actor_chain",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_compelled_production_of_hacc_actor_document_authority_chain",
                "issue:lease_change_actor_identification",
            ),
            "If local search did not locate the HACC actor-identification record and compelled production is required, the case posture is permitted to pursue Exhibit R production.",
            "filing",
            ("auth:orcp_55", "auth:orcp_46"),
        ),
        Rule(
            "r7_solomon_forbidden_refile_precluded_issue",
            ("f_authority_issue_preclusion_elements_official_oregon_cases", "f_authority_issue_preclusion_requires_prior_separate_proceeding", "f_collateral_estoppel_candidate", "f_client_solomon_barred_refile"),
            DeonticConclusion(
                "c7_solomon_forbidden_refile_precluded_issue",
                "F",
                "person:solomon",
                "relitigate_precluded_issue",
                "issue:guardianship_authority",
            ),
            "If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.",
            "hypothesis",
            ("auth:oregon_issue_preclusion_cases", "auth:oregon_issue_preclusion_prior_separate_proceeding_cases"),
        ),
        Rule(
            "r8_solomon_notice_ack_triggers_court_relief_path",
            ("f_feed_ev_solomon_ack_heard_restraining_order", "f_restraining_order_in_effect"),
            DeonticConclusion(
                "c8_solomon_obligated_seek_relief_via_court",
                "O",
                "person:solomon",
                "seek_clarification_or_relief_through_court",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon acknowledged awareness of restraining order and the order is in effect, Solomon is obligated to seek court relief rather than self-help noncompliance.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r9_solomon_wait_for_service_conflicts_with_no_further_service",
            ("f_feed_ev_solomon_wait_for_service_statement", "f_restraining_order_no_further_service_needed"),
            DeonticConclusion(
                "c9_solomon_forbidden_condition_compliance_on_extra_service",
                "F",
                "person:solomon",
                "condition_compliance_on_additional_service",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon stated he would wait for service but the order states no further service needed due to appearance, conditioning compliance on extra service is forbidden in this model.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r10_solomon_noncooperation_statement_conflicts_with_effective_order",
            ("f_feed_ev_solomon_not_incentivized_statement", "f_restraining_order_in_effect"),
            DeonticConclusion(
                "c10_solomon_forbidden_intentional_noncooperation",
                "F",
                "person:solomon",
                "intentional_noncooperation_with_effective_order",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon states non-incentivized cooperation while order is in effect, intentional noncooperation is forbidden in this model.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r11_solomon_already_have_order_statement_supports_notice",
            ("f_feed_ev_solomon_ack_already_have_order", "f_restraining_order_in_effect"),
            DeonticConclusion(
                "c11_solomon_obligated_recognize_existing_order_status",
                "O",
                "person:solomon",
                "recognize_existing_order_status",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon stated the other party already had the restraining order and order is in effect, Solomon is obligated to recognize existing order status.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order",
            ("f_feed_ev_solomon_order_not_in_effect_statement", "f_restraining_order_in_effect"),
            DeonticConclusion(
                "c12_solomon_forbidden_assert_order_ineffective_without_relief",
                "F",
                "person:solomon",
                "assert_order_ineffective_without_court_relief",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon states the order is not in effect while the order is in effect, asserting ineffectiveness without court relief is forbidden in this model.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r13_solomon_judge_overturn_statement_triggers_motion_path",
            ("f_feed_ev_solomon_judge_overturn_statement", "f_restraining_order_in_effect"),
            DeonticConclusion(
                "c13_solomon_obligated_file_motion_not_self_help",
                "O",
                "person:solomon",
                "file_motion_to_modify_or_vacate_before_noncompliance",
                "order:eppdapa_restraining_order",
            ),
            "If Solomon states he would have the judge overturn the order while it is in effect, he is obligated to seek court modification before noncompliance.",
            "filing",
            ("order:eppdapa_restraining_order",),
        ),
        Rule(
            "r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling",
            ("f_feed_ev_hacc_notice_brother_calls_after_granted_order", "f_feed_ev_hacc_notice_third_party_contact_with_restrained_person"),
            DeonticConclusion(
                "c14_hacc_obligated_avoid_third_party_housing_contact_with_restrained_person",
                "O",
                "org:hacc",
                "avoid_third_party_housing_contact_with_restrained_person_and_document_response",
                "person:jane_cortez",
            ),
            "If HACC is told that Jane is receiving calls about a restrained brother and third-party housing contact is occurring with a restrained person, HACC is obligated in this model to stop that contact path and document the response.",
            "filing",
            ("auth:orcp_17_c", "order:eppdapa_restraining_order"),
        ),
        Rule(
            "r15_benjamin_permitted_serve_subpoena_packets",
            ("f_subpoena_workflow_components_staged", "f_subpoena_recipients_ready_to_serve"),
            DeonticConclusion(
                "c15_benjamin_permitted_serve_subpoena_packets",
                "P",
                "person:benjamin_barber",
                "serve_staged_subpoena_packets",
                "case:26PR00641",
            ),
            "If subpoena workflow components are staged and recipients are ready-to-serve, Benjamin is permitted to serve the staged subpoena packets.",
            "workflow",
            ("auth:orcp_55",),
        ),
        Rule(
            "r16_benjamin_obligated_track_service_and_deadlines",
            ("f_active_service_log_initialized", "f_subpoena_workflow_components_staged"),
            DeonticConclusion(
                "c16_benjamin_obligated_track_service_and_deadlines",
                "O",
                "person:benjamin_barber",
                "maintain_service_and_deadline_tracking",
                "case:26PR00641",
            ),
            "If service log and workflow components exist, Benjamin is obligated in this model to maintain service/deadline tracking.",
            "workflow",
            ("auth:orcp_55",),
        ),
        Rule(
            "r17_responding_custodian_obligated_execute_or_query_protocol_upon_service",
            ("f_subpoena_service_completed_any", "f_or_joined_search_protocol_defined"),
            DeonticConclusion(
                "c17_responding_custodian_obligated_execute_or_query_protocol",
                "O",
                "role:responding_custodian",
                "execute_or_joined_identifier_queries_and_produce_search_execution_report",
                "case:26PR00641",
            ),
            "If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.",
            "workflow",
            ("auth:orcp_55",),
        ),
        Rule(
            "r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response",
            ("f_subpoena_response_incomplete_any", "f_subpoena_workflow_components_staged"),
            DeonticConclusion(
                "c18_benjamin_permitted_issue_deficiency_notice",
                "P",
                "person:benjamin_barber",
                "issue_subpoena_deficiency_notice_and_set_cure_deadline",
                "case:26PR00641",
            ),
            "If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.",
            "workflow",
            ("auth:orcp_46", "auth:orcp_55"),
        ),
        Rule(
            "r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage",
            ("f_deficiency_notice_sent_any", "f_subpoena_workflow_components_staged"),
            DeonticConclusion(
                "c19_benjamin_permitted_move_to_compel",
                "P",
                "person:benjamin_barber",
                "move_to_compel_and_seek_sanctions_for_subpoena_noncompliance",
                "case:26PR00641",
            ),
            "If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.",
            "workflow",
            ("auth:orcp_46", "auth:orcp_55"),
        ),
        Rule(
            "r20_case_permitted_treat_enforcement_path_as_pending_pre_service",
            ("f_subpoena_pre_service_phase_only",),
            DeonticConclusion(
                "c20_case_permitted_treat_enforcement_path_as_pending_pre_service",
                "P",
                "case:guardianship_collateral_estoppel",
                "treat_subpoena_enforcement_motion_path_as_pending_until_service",
                "case:26PR00641",
            ),
            "If no subpoena service is yet completed, subpoena-enforcement motion path remains pending pre-service in this model.",
            "workflow",
            ("auth:orcp_55",),
        ),
        Rule(
            "r21_case_obligated_resolve_actor_assignment_conflict",
            ("f_actor_assignment_conflict_benjamin_vs_solomon_interference",),
            DeonticConclusion(
                "c21_case_obligated_resolve_actor_assignment_conflict",
                "O",
                "case:guardianship_collateral_estoppel",
                "resolve_benjamin_vs_solomon_interference_actor_assignment_with_source_record",
                "issue:interference_actor_assignment",
            ),
            "If the model contains a Benjamin-vs-Solomon interference actor conflict, the case posture is obligated to resolve that assignment with source records before final legal attribution.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r22_case_obligated_finalize_authority_citations_before_filing",
            ("f_authority_table_placeholders_unresolved",),
            DeonticConclusion(
                "c22_case_obligated_finalize_authority_citations_before_filing",
                "O",
                "case:guardianship_collateral_estoppel",
                "finalize_governing_authority_citations_before_final_filing",
                "doc:06_oregon_authority_table_final.md",
            ),
            "If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r23_case_permitted_initiate_remedial_contempt_path",
            ("f_authority_ors_33_055_remedial_contempt_procedure", "f_restraining_order_in_effect", "f_solomon_service_position_statement"),
            DeonticConclusion(
                "c23_case_permitted_initiate_remedial_contempt_path",
                "P",
                "case:guardianship_collateral_estoppel",
                "initiate_remedial_contempt_or_show_cause_path",
                "person:solomon",
            ),
            "If remedial-contempt authority is available and the record includes an in-effect order plus Solomon's service-position statement, the case posture is permitted to pursue a remedial contempt or show-cause path.",
            "filing",
            ("auth:ors_33_055",),
        ),
        Rule(
            "r23b_case_permitted_seek_court_direction_on_service_channel_if_evasion_pattern",
            (
                "f_authority_ors_33_055_remedial_contempt_procedure",
                "f_authority_orcp_9_service_of_later_filed_papers",
                "f_service_channel_conflict_or_evasion_pattern_documented",
            ),
            DeonticConclusion(
                "c23b_case_permitted_seek_court_direction_on_service_channel_if_evasion_pattern",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_court_direction_on_service_channel_and_document_attempts",
                "person:solomon",
            ),
            "If service-channel conflict or evasion pattern is documented, the case posture may seek court direction on proper service mechanics and present documented service attempts.",
            "filing",
            ("auth:ors_33_055", "auth:orcp_9"),
        ),
        Rule(
            "r23c_case_permitted_rely_on_court_notice_modification_order_if_documented",
            (
                "f_motion_to_waive_or_modify_notice_re_gal_filed_2025_11_20",
                "f_order_on_motion_to_waive_or_modify_notice_re_gal_granted_2025_11_20",
                "f_order_notice_requirements_orcp27_waived_or_modified_2025_11_20",
            ),
            DeonticConclusion(
                "c23c_case_permitted_rely_on_court_notice_modification_order_if_documented",
                "P",
                "case:guardianship_collateral_estoppel",
                "rely_on_documented_court_order_modifying_notice_requirements_for_related_service_pathways",
                "issue:service_and_notice",
            ),
            "If a motion to waive/modify notice was filed and a related order granting notice modification is documented, the case posture may rely on that court-approved notice modification in framing service and notice mechanics.",
            "filing",
            ("auth:orcp_27", "auth:utcr_5_100"),
        ),
        Rule(
            "r23d_case_permitted_characterize_counsel_contact_as_same_matter_notice_channel_for_collateral_estoppel_briefing",
            (
                "f_service_email_sent_to_alex_bluestone_re_jane_solomon_2026_04_03",
                "f_bluestone_acknowledged_representation_for_jane_guardianship_2026_04_04",
                "f_counsel_disclaimed_accepting_service_for_solomon_2026_04_04",
            ),
            DeonticConclusion(
                "c23d_case_permitted_characterize_counsel_contact_as_same_matter_notice_channel_for_collateral_estoppel_briefing",
                "P",
                "case:guardianship_collateral_estoppel",
                "characterize_counsel_contact_as_same_matter_notice_channel_while_preserving_service_validity_dispute",
                "issue:collateral_estoppel_same_matter_notice",
            ),
            "If service email was sent to counsel and counsel acknowledged representation in the Jane guardianship matter while disclaiming acceptance of service, the case posture may characterize counsel contact as same-matter notice channel while preserving any service-validity dispute for court determination.",
            "filing",
            ("auth:orcp_9", "auth:orcp_17_c"),
        ),
        Rule(
            "r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved",
            ("f_authority_ors_33_075_compel_appearance", "f_client_solomon_failed_appearance"),
            DeonticConclusion(
                "c24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_order_or_warrant_to_compel_appearance_if_order_to_appear_is_served_and_ignored",
                "person:solomon",
            ),
            "If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.",
            "filing",
            ("auth:ors_33_075",),
        ),
        Rule(
            "r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved",
            ("f_authority_ors_33_105_remedial_sanctions", "f_hacc_removed_benjamin_effective_2026_01_01"),
            DeonticConclusion(
                "c25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_compensatory_or_compliance_oriented_remedial_sanctions_if_contempt_is_proved",
                "issue:prejudice_and_noninterference_relief",
            ),
            "If remedial-sanctions authority is available and prejudice-related housing change is documented, the case posture may seek compensatory or compliance-oriented remedial sanctions if contempt elements are later proved.",
            "filing",
            ("auth:ors_33_105",),
        ),
        Rule(
            "r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown",
            ("f_authority_orcp_17_improper_purpose_and_support", "f_hacc_named_notice_to_solomon_order_not_found"),
            DeonticConclusion(
                "c26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_orcp_17_sanctions_if_filing_is_shown_improper_or_factually_or_legally_unsupported",
                "issue:sanctions_track",
            ),
            "If ORCP 17 authority is available, the case posture may seek filing-related sanctions if improper purpose or inadequate factual/legal support is shown; current proof-state cautions remain in force.",
            "filing",
            ("auth:orcp_17_c",),
        ),
        Rule(
            "r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46",
            ("f_authority_orcp_55_subpoena_obedience", "f_authority_orcp_46_discovery_sanctions", "f_hacc_exhibit_r_requires_compelled_production"),
            DeonticConclusion(
                "c27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_subpoena_enforcement_and_related_expenses_after_nonparty_noncompliance",
                "org:hacc",
            ),
            "If subpoena-obedience and discovery-sanctions authority are available and compelled production is required, the case posture may pursue subpoena enforcement and related expense-shifting when the required noncompliance predicate is met.",
            "workflow",
            ("auth:orcp_55", "auth:orcp_46"),
        ),
        Rule(
            "r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding",
            ("f_authority_ors_125_050_protective_orcp_oec", "f_petition_exists"),
            DeonticConclusion(
                "c28_case_permitted_apply_orcp_and_oec_in_protective_proceeding",
                "P",
                "case:26PR00641",
                "apply_orcp_and_oec_subject_to_specific_chapter_125_overrides",
                "proceeding:protective_proceeding",
            ),
            "If ORS 125.050 authority is available and the protective petition is filed, the proceeding may apply ORCP and the Oregon Evidence Code except where chapter 125 provides otherwise.",
            "filing",
            ("auth:ors_125_050",),
        ),
        Rule(
            "r29_case_obligated_preserve_notice_and_objection_window",
            ("f_authority_ors_125_060_notice_recipients", "f_authority_ors_125_065_notice_manner_and_timing", "f_notice_to_respondent"),
            DeonticConclusion(
                "c29_case_obligated_preserve_notice_and_objection_window",
                "O",
                "case:26PR00641",
                "preserve_statutory_notice_and_objection_window_for_protective_petition",
                "person:jane_cortez",
            ),
            "If chapter 125 notice authorities are available and notice issued to the respondent, the proceeding is obligated to preserve the statutory notice and objection framework.",
            "filing",
            ("auth:ors_125_060", "auth:ors_125_065"),
        ),
        Rule(
            "r30_case_obligated_schedule_hearing_on_presented_objection",
            ("f_authority_ors_125_075_objections", "f_authority_ors_125_080_hearing_and_counsel", "f_respondent_objection_form_present"),
            DeonticConclusion(
                "c30_case_obligated_schedule_hearing_on_presented_objection",
                "O",
                "case:26PR00641",
                "schedule_and_process_hearing_on_guardianship_objection",
                "person:jane_cortez",
            ),
            "If objection and hearing authorities are available and the packet includes a respondent objection form, the proceeding is obligated in this model to route the matter through the objection-hearing path.",
            "filing",
            ("auth:ors_125_075", "auth:ors_125_080"),
        ),
        Rule(
            "r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel",
            ("f_authority_ors_125_080_hearing_and_counsel", "f_notice_to_respondent"),
            DeonticConclusion(
                "c31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel",
                "P",
                "case:26PR00641",
                "assert_respondent_right_to_appear_in_person_or_by_counsel",
                "person:jane_cortez",
            ),
            "If ORS 125.080 authority is available and notice has issued, the case posture may assert the protected person's right to appear in person or by counsel at hearing.",
            "filing",
            ("auth:ors_125_080",),
        ),
        Rule(
            "r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines",
            ("f_authority_orcp_9_service_of_later_filed_papers", "f_authority_orcp_10_time_computation", "f_petition_exists"),
            DeonticConclusion(
                "c32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines",
                "P",
                "case:guardianship_collateral_estoppel",
                "use_orcp9_service_and_orcp10_deadline_computation_for_later_filed_motion_packets",
                "issue:service_and_deadlines",
            ),
            "If ORCP 9 and ORCP 10 authority are available, the case posture may use those rules for service and deadline computation on later-filed motion packets, subject to more specific chapter 125 notice rules where applicable.",
            "workflow",
            ("auth:orcp_9", "auth:orcp_10", "auth:ors_125_050"),
        ),
        Rule(
            "r33_case_permitted_request_special_advocate_or_gal_under_chapter_125",
            ("f_authority_ors_125_120_protected_person_special_advocate", "f_petition_exists", "f_actor_assignment_conflict_benjamin_vs_solomon_interference"),
            DeonticConclusion(
                "c33_case_permitted_request_special_advocate_or_gal_under_chapter_125",
                "P",
                "case:26PR00641",
                "request_special_advocate_or_guardian_ad_litem_to_protect_person_interests",
                "person:jane_cortez",
            ),
            "If ORS 125.120 authority is available and the petition includes unresolved actor-assignment conflict affecting protective-person interests, the case posture may request a special advocate or GAL under chapter 125.",
            "filing",
            ("auth:ors_125_120",),
        ),
        Rule(
            "r34_case_obligated_check_clackamas_probate_slr_requirements_before_filing",
            ("f_authority_clackamas_slr_9_035_probate_practice", "f_authority_clackamas_slr_9_076_probate_practice", "f_petition_exists"),
            DeonticConclusion(
                "c34_case_obligated_check_clackamas_probate_slr_requirements_before_filing",
                "O",
                "case:26PR00641",
                "check_and_document_clackamas_probate_slr_requirements_for_current_motion_packet",
                "court:clackamas_probate",
            ),
            "If Clackamas SLR 9.035 and 9.076 authority are available and the petition posture is active, the case posture is obligated to check and document local probate-rule requirements before filing.",
            "workflow",
            ("auth:clackamas_slr_9_035", "auth:clackamas_slr_9_076"),
        ),
        Rule(
            "r35_case_obligated_treat_issue_preclusion_as_provisional_until_certified_prior_record_staged",
            (
                "f_authority_issue_preclusion_requires_prior_separate_proceeding",
                "f_authority_case_hayes_oyster_2005",
                "f_authority_case_westwood_2002",
                "f_certified_prior_order_material_missing",
                "f_certified_prior_docket_material_missing",
            ),
            DeonticConclusion(
                "c35_case_obligated_treat_issue_preclusion_as_provisional_until_certified_prior_record_staged",
                "O",
                "case:guardianship_collateral_estoppel",
                "treat_issue_preclusion_theory_as_provisional_until_certified_prior_order_and_docket_are_staged",
                "issue:guardianship_authority",
            ),
            "If prior-proceeding record requirements are recognized and certified prior-order/docket materials are still missing, issue-preclusion merits claims stay provisional pending certified record staging.",
            "filing",
            ("auth:oregon_issue_preclusion_prior_separate_proceeding_cases",),
        ),
        Rule(
            "r36_case_obligated_complete_issue_preclusion_element_mapping_before_merits_reliance",
            (
                "f_authority_issue_preclusion_elements_official_oregon_cases",
                "f_authority_case_nelson_1993",
                "f_authority_case_rawls_2010",
                "f_issue_preclusion_mapping_incomplete",
            ),
            DeonticConclusion(
                "c36_case_obligated_complete_issue_preclusion_element_mapping_before_merits_reliance",
                "O",
                "case:guardianship_collateral_estoppel",
                "complete_identical_issue_finality_privity_and_full_fair_mapping_before_merits_reliance",
                "issue:guardianship_authority",
            ),
            "If element authorities are present but the issue-preclusion mapping is incomplete, the case posture is obligated to complete element-by-element mapping before merits-level reliance.",
            "filing",
            ("auth:oregon_issue_preclusion_cases",),
        ),
        Rule(
            "r37_case_obligated_add_targeted_record_citations_for_finality_and_full_fair_elements",
            (
                "f_authority_issue_preclusion_elements_official_oregon_cases",
                "f_issue_preclusion_finality_element_missing",
                "f_issue_preclusion_full_fair_element_missing",
            ),
            DeonticConclusion(
                "c37_case_obligated_add_targeted_record_citations_for_finality_and_full_fair_elements",
                "O",
                "case:guardianship_collateral_estoppel",
                "add_targeted_certified_record_citations_for_finality_and_full_fair_elements",
                "issue:guardianship_authority",
            ),
            "If finality and full-fair element mappings are still missing, the model obligates targeted certified record citation development for those specific elements.",
            "filing",
            ("auth:oregon_issue_preclusion_cases",),
        ),
        Rule(
            "r38_case_obligated_qualify_overclaim_language_until_elements_are_proved",
            (
                "f_overclaim_issue_preclusion_statement_detected",
                "f_issue_preclusion_mapping_incomplete",
                "f_certified_prior_order_material_missing",
            ),
            DeonticConclusion(
                "c38_case_obligated_qualify_overclaim_language_until_elements_are_proved",
                "O",
                "case:guardianship_collateral_estoppel",
                "qualify_issue_preclusion_language_as_contingent_and_not_fully_proved",
                "doc:petition_guardianship_working_memo",
            ),
            "If overclaim language appears while mapping and certified prior-order support are incomplete, filing language must be qualified as contingent rather than fully proved.",
            "filing",
            ("auth:orcp_17_c", "auth:oregon_issue_preclusion_cases"),
        ),
        Rule(
            "r39_case_permitted_seek_targeted_nonparty_production_for_missing_issue_preclusion_elements",
            (
                "f_authority_orcp_55_subpoena_obedience",
                "f_issue_preclusion_mapping_incomplete",
                "f_certified_prior_hearing_material_missing",
            ),
            DeonticConclusion(
                "c39_case_permitted_seek_targeted_nonparty_production_for_missing_issue_preclusion_elements",
                "P",
                "case:guardianship_collateral_estoppel",
                "seek_targeted_nonparty_production_for_hearing_and_appearance_materials_supporting_issue_preclusion_elements",
                "issue:guardianship_authority",
            ),
            "If issue-preclusion mapping remains incomplete and certified hearing material is missing, the case posture may pursue targeted nonparty production for missing element support.",
            "workflow",
            ("auth:orcp_55",),
        ),
    ]


def evaluate_rule(rule: Rule, facts_by_id: Dict[str, Fact], mode: str) -> Tuple[str, List[Dict[str, object]], str | None, Dict[str, object]]:
    detail: List[Dict[str, object]] = []
    all_true = True
    all_verified = True
    known_dates: List[str] = []

    for fid in rule.antecedents:
        f = facts_by_id[fid]
        if f.dates:
            known_dates.extend(f.dates)
        detail.append({
            "fact_id": fid,
            "status": f.status,
            "value": str(f.value).lower(),
            "dates": list(f.dates),
        })
        all_true = all_true and f.value
        all_verified = all_verified and (f.status == "verified")

    activation_date = _max_iso_date(known_dates)
    temporal_profile = build_temporal_profile(rule, facts_by_id)

    if not all_true:
        return "inactive", detail, activation_date, temporal_profile

    if mode == "strict":
        return ("active" if all_verified else "unresolved"), detail, activation_date, temporal_profile

    if mode == "inclusive":
        if rule.track == "hypothesis":
            return "unresolved", detail, activation_date, temporal_profile
        allowed = {"verified", "alleged"}
        if all(facts_by_id[fid].status in allowed and facts_by_id[fid].value for fid in rule.antecedents):
            return "active", detail, activation_date, temporal_profile
        return "unresolved", detail, activation_date, temporal_profile

    raise ValueError(f"Unknown mode: {mode}")


def build_reasoning_report(
    facts: List[Fact],
    rules: List[Rule],
    ocr_dates: Dict[str, List[str]],
    solomon_events: List[Dict[str, object]],
    solomon_repo_hits: List[Dict[str, object]],
    fact_override_summary: Dict[str, object] | None = None,
) -> Dict[str, object]:
    facts_by_id = {f.fact_id: f for f in facts}
    intervals = build_temporal_intervals(facts_by_id)
    report: Dict[str, object] = {
        "generated_at": str(date.today()),
        "ocr_date_index": ocr_dates,
        "solomon_event_feed_count": len(solomon_events),
        "solomon_repository_hit_count": len(solomon_repo_hits),
        "solomon_repository_fact_count": sum(1 for f in facts if f.predicate == "RepositorySourceMentionsSolomonCaseContext"),
        "fact_override_summary": fact_override_summary
        if fact_override_summary is not None
        else {
            "override_file": str(FACT_OVERRIDES_CSV),
            "rows_read": 0,
            "applied_count": 0,
            "skipped_count": 0,
            "applied": [],
            "skipped": [],
        },
        "temporal_intervals": [
            {
                "interval_id": interval.interval_id,
                "label": interval.label,
                "start_date": interval.start_date,
                "end_date": interval.end_date,
                "status": interval.status,
                "source": interval.source,
                "tags": list(interval.tags),
            }
            for interval in intervals
        ],
        "element_audits": build_element_audits(facts_by_id, intervals),
        "modes": {},
    }

    for mode in ("strict", "inclusive"):
        active = []
        unresolved = []
        inactive = []
        party_state: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

        for rule in rules:
            state, antecedent_detail, activation_date, temporal_profile = evaluate_rule(rule, facts_by_id, mode)
            item = {
                "rule_id": rule.rule_id,
                "track": rule.track,
                "authority_refs": list(rule.authority_refs),
                "description": rule.description,
                "activation_date_estimate": activation_date,
                "temporal_profile": attach_intervals_to_profile(temporal_profile, intervals, rule),
                "antecedents": antecedent_detail,
                "conclusion": {
                    "conclusion_id": rule.conclusion.conclusion_id,
                    "modality": rule.conclusion.modality,
                    "actor": rule.conclusion.actor,
                    "action": rule.conclusion.action,
                    "target": rule.conclusion.target,
                },
            }
            if state == "active":
                active.append(item)
                actor = rule.conclusion.actor
                modality = rule.conclusion.modality
                party_state.setdefault(actor, {"O": [], "P": [], "F": []})[modality].append(
                    {
                        "action": rule.conclusion.action,
                        "target": rule.conclusion.target,
                        "rule_id": rule.rule_id,
                        "activation_date_estimate": activation_date,
                        "temporal_profile": attach_intervals_to_profile(temporal_profile, intervals, rule),
                    }
                )
            elif state == "unresolved":
                unresolved.append(item)
            else:
                inactive.append(item)

        report["modes"][mode] = {
            "active_rules": active,
            "unresolved_rules": unresolved,
            "inactive_rules": inactive,
            "party_deontic_state": party_state,
        }

    return report


def to_knowledge_graph(facts: List[Fact], rules: List[Rule], report: Dict[str, object]) -> Dict[str, object]:
    nodes = []
    edges = []

    party_nodes = {
        "person:solomon": "Solomon Barber",
        "person:jane_cortez": "Jane Cortez",
        "person:benjamin_barber": "Benjamin Barber",
        "person:ashley_ferron": "Ashley Ferron",
        "person:julio_cortez": "Julio Cortez",
        "org:adult_protective_services": "Adult Protective Services",
        "org:hacc": "Housing Authority of Clackamas County",
        "court:clackamas_probate": "Clackamas County Circuit Court Probate Department",
        "location:10043_se_32nd_ave": "10043 SE 32nd Ave, Milwaukie, Oregon 97222",
        "role:responding_custodian": "Responding Records Custodian Role",
    }
    for pid, name in party_nodes.items():
        nodes.append({"id": pid, "kind": "party", "name": name})

    for f in facts:
        fid = f"fact:{f.fact_id}"
        nodes.append(
            {
                "id": fid,
                "kind": "fact",
                "predicate": f.predicate,
                "args": list(f.args),
                "value": f.value,
                "status": f.status,
                "source": f.source,
                "dates": list(f.dates),
                "confidence_level": f.confidence_level,
                "confidence_score": f.confidence_score,
                "evidence_kind": f.evidence_kind,
            }
        )

    for interval in report.get("temporal_intervals", []):
        nodes.append(
            {
                "id": f"interval:{interval['interval_id']}",
                "kind": "temporal_interval",
                "label": interval["label"],
                "start_date": interval["start_date"],
                "end_date": interval["end_date"],
                "status": interval["status"],
                "source": interval["source"],
                "tags": interval.get("tags", []),
            }
        )

    for rule in rules:
        rid = f"rule:{rule.rule_id}"
        cid = f"conclusion:{rule.conclusion.conclusion_id}"
        nodes.append(
            {
                "id": rid,
                "kind": "rule",
                "description": rule.description,
                "track": rule.track,
                "authority_refs": list(rule.authority_refs),
            }
        )
        nodes.append(
            {
                "id": cid,
                "kind": "deontic_conclusion",
                "modality": rule.conclusion.modality,
                "actor": rule.conclusion.actor,
                "action": rule.conclusion.action,
                "target": rule.conclusion.target,
            }
        )
        for ant in rule.antecedents:
            edges.append({"from": f"fact:{ant}", "to": rid, "relation": "antecedent_of"})
        rule_report = next((x for x in report["modes"]["strict"]["active_rules"] if x["rule_id"] == rule.rule_id), None)
        if not rule_report:
            rule_report = next((x for x in report["modes"]["inclusive"]["active_rules"] if x["rule_id"] == rule.rule_id), None)
        if rule_report:
            for interval_id in rule_report.get("temporal_profile", {}).get("interval_refs", []):
                edges.append({"from": f"interval:{interval_id}", "to": rid, "relation": "temporal_context_for"})
        edges.append({"from": rid, "to": cid, "relation": "yields"})
        edges.append({"from": rule.conclusion.actor, "to": cid, "relation": "bears"})

    strict_active = {x["rule_id"] for x in report["modes"]["strict"]["active_rules"]}
    incl_active = {x["rule_id"] for x in report["modes"]["inclusive"]["active_rules"]}
    for rule in rules:
        rid = f"rule:{rule.rule_id}"
        status = "inactive"
        if rule.rule_id in strict_active:
            status = "active_verified"
        elif rule.rule_id in incl_active:
            status = "active_inclusive_alleged"
        edges.append({"from": rid, "to": "case:guardianship_collateral_estoppel", "relation": status})

    nodes.append(
        {
            "id": "case:guardianship_collateral_estoppel",
            "kind": "case",
            "name": "Guardianship/Collateral Estoppel Working Case",
            "as_of": str(date.today()),
        }
    )

    return {
        "metadata": {
            "generated_at": str(date.today()),
            "purpose": "Full case knowledge graph for guardianship + collateral estoppel reasoning",
            "modalities": ["O", "P", "F"],
            "reasoning_modes": ["strict", "inclusive"],
        },
        "nodes": nodes,
        "edges": edges,
    }


def to_dependency_graph(rules: List[Rule], report: Dict[str, object]) -> Dict[str, object]:
    active_strict = {x["rule_id"] for x in report["modes"]["strict"]["active_rules"]}
    active_inclusive = {x["rule_id"] for x in report["modes"]["inclusive"]["active_rules"]}
    nodes = []
    edges = []

    for rule in rules:
        nodes.append({"id": rule.rule_id, "kind": "rule", "description": rule.description})
        nodes.append({"id": rule.conclusion.conclusion_id, "kind": "conclusion", "modality": rule.conclusion.modality})
        edges.append({"from": rule.rule_id, "to": rule.conclusion.conclusion_id, "relation": "produces"})
        for ant in rule.antecedents:
            nodes.append({"id": ant, "kind": "fact_dependency"})
            edges.append({"from": ant, "to": rule.rule_id, "relation": "required_by"})

    return {
        "metadata": {
            "generated_at": str(date.today()),
            "strict_active_rules": sorted(active_strict),
            "inclusive_active_rules": sorted(active_inclusive),
        },
        "nodes": nodes,
        "edges": edges,
    }


def to_dot(dep: Dict[str, object]) -> str:
    lines = [
        "digraph CaseDependencyGraph {",
        '  rankdir=LR;',
        '  node [shape=box, style="rounded,filled", fillcolor="#f7f7f7"];',
    ]

    seen = set()
    for n in dep["nodes"]:
        nid = n["id"]
        if nid in seen:
            continue
        seen.add(nid)
        label = nid.replace('"', "")
        lines.append(f'  "{nid}" [label="{label}"];')

    for e in dep["edges"]:
        lines.append(f'  "{e["from"]}" -> "{e["to"]}" [label="{e["relation"]}"];')

    lines.append("}")
    return "\n".join(lines) + "\n"


def to_flogic(facts: List[Fact], rules: List[Rule]) -> str:
    lines = [
        "% Frame Logic program for guardianship/collateral-estoppel case",
        "% Facts are annotated as verified/alleged/theory.",
        "",
        "% Parties (frames)",
        "person:solomon[role->respondent_or_petitioner].",
        "person:jane_cortez[role->protected_person].",
        "person:benjamin_barber[role->related_actor].",
        "org:hacc[role->housing_authority].",
        "",
        "% Atomic facts",
    ]
    for f in facts:
        arg_str = ", ".join(f.args)
        truth = "true" if f.value else "false"
        date_ann = f", dates({list(f.dates)})" if f.dates else ""
        conf_ann = ""
        if f.confidence_level is not None:
            conf_ann += f", confidence_level({f.confidence_level})"
        if f.confidence_score is not None:
            conf_ann += f", confidence_score({f.confidence_score})"
        if f.evidence_kind is not None:
            conf_ann += f", evidence_kind({f.evidence_kind})"
        lines.append(f"fact({f.fact_id}, {f.predicate}({arg_str}), status({f.status}), value({truth}){date_ann}{conf_ann}).")

    lines.append("\n% Deontic rules")
    for r in rules:
        ant = ", ".join([f"holds({aid})" for aid in r.antecedents])
        c = r.conclusion
        lines.append(f"deontic({c.modality}, {c.actor}, {c.action}, {c.target}) :- {ant}.")
        lines.append(f"% track({r.rule_id}) = {r.track}")
        if r.authority_refs:
            lines.append(f"% authority_refs({r.rule_id}) = {list(r.authority_refs)}")

    lines.append("\n% Helper: strict mode")
    lines.append("holds(F) :- fact(F, _, status(verified), value(true)).")
    lines.append("% Helper: inclusive mode")
    lines.append("holds_inclusive(F) :- fact(F, _, status(verified), value(true)).")
    lines.append("holds_inclusive(F) :- fact(F, _, status(alleged), value(true)).")
    return "\n".join(lines) + "\n"


def to_tdfol(facts: List[Fact], rules: List[Rule]) -> str:
    lines = [
        "% Temporal Deontic First-Order Logic model",
        "% O(a,act,tgt) obligation, P(...) permission, F(...) prohibition",
        "",
        "% Facts",
    ]
    for f in facts:
        args = ", ".join(f.args)
        t = f.dates[0] if f.dates else date.today().isoformat()
        lines.append(f"At({t}, {f.predicate}({args}))  % status={f.status}, value={str(f.value).lower()}")

    facts_by_id = {f.fact_id: f for f in facts}
    intervals = build_temporal_intervals(facts_by_id)

    lines.append("\n% Temporal intervals")
    for interval in intervals:
        lines.append(
            f"Interval({interval.interval_id}, {interval.start_date}, {interval.end_date or 'open_end'})"
            f"  % status={interval.status}, source={interval.source}, tags={list(interval.tags)}"
        )

    lines.append("\n% Rules")
    for r in rules:
        premise_terms = []
        for aid in r.antecedents:
            ff = next(x for x in facts if x.fact_id == aid)
            tt = ff.dates[0] if ff.dates else "t"
            premise_terms.append(f"At({tt}, {ff.predicate}({', '.join(ff.args)}))")
        premise = " /\\ ".join(premise_terms)
        c = r.conclusion
        lines.append(f"forall t: ({premise}) -> {c.modality}({c.actor}, {c.action}, {c.target}, t)")

    lines.append("\n% Conflict monitor")
    lines.append(
        "forall t: (At(t, PetitionStatesNoPriorGuardian(case:26PR00641, person:jane_cortez)) /\\ At(t, PriorAppointmentExists(person:jane_cortez, person:benjamin_barber))) -> ConflictFlag(prior_guardian_status, t)"
    )
    return "\n".join(lines) + "\n"


def to_event_calculus(facts: List[Fact], rules: List[Rule]) -> str:
    def pl_atom(token: str) -> str:
        return "'" + token.replace("'", "\\'") + "'"

    lines = [
        "% Deontic Cognitive Event Calculus program",
        "% Fluents: notice/2, valid_order/1, interference/2, preclusion_applies/1",
        "",
        "% Event declarations",
        "event(file_petition(solomon, case_26PR00641)).",
        "event(issue_notice(case_26PR00641, jane_cortez)).",
        "event(grant_restraining_order(eppdapa_order, jane_cortez, solomon)).",
        "event(assert_prior_appointment(jane_cortez, benjamin_barber)).",
        "event(assert_interference(benjamin_barber, hacc_housing_contract)).",
        "event(assert_refiled_barred_issue(solomon, guardianship_authority)).",
        "",
        "% Initiates / terminates",
        "initiates(grant_restraining_order(Order, _, _), valid_order(Order), T).",
        "initiates(issue_notice(Case, Person), notice(Person, Case), T).",
        "initiates(assert_interference(Person, Process), interference(Person, Process), T).",
        "initiates(assert_prior_appointment(Jane, Ben), prior_appointment(Jane, Ben), T).",
        "initiates(assert_refiled_barred_issue(solomon, Issue), relitigates(solomon, Issue), T).",
        "",
        "% Cognitive state",
        "holdsAt(knows(solomon, valid_order(eppdapa_order)), T) :- holdsAt(notice(solomon, case_26PR00641), T).",
        "",
        "% Truth anchors for model facts",
    ]

    for f in facts:
        if f.value:
            lines.append(f"fact_true({pl_atom(f.fact_id)}).")

    lines.extend([
        "",
        "% Rule-level derivations from fact truth",
    ])
    for r in rules:
        ant = ", ".join([f"fact_true({pl_atom(aid)})" for aid in r.antecedents]) if r.antecedents else "true"
        lines.append(f"rule_holds({pl_atom(r.rule_id)}) :- {ant}.")

    lines.extend([
        "",
        "% Deontic conclusions generated for all rules",
    ])
    for r in rules:
        c = r.conclusion
        lines.append(
            "deontic_conclusion("
            f"{pl_atom(r.rule_id)}, {pl_atom(c.modality)}, {pl_atom(c.actor)}, {pl_atom(c.action)}, {pl_atom(c.target)}) :- "
            f"rule_holds({pl_atom(r.rule_id)})."
        )

    lines.extend([
        "",
        "% Temporal anchors inferred from OCR",
    ])

    for f in facts:
        if f.dates:
            for d in f.dates:
                lines.append(f"happens(fact_event({f.fact_id}), {d}).")

    lines.append("\n% Fact status comments")
    for f in facts:
        lines.append(f"% {f.fact_id}: status={f.status}, source={f.source}, dates={list(f.dates)}")

    lines.append("\n% Rule mapping comments")
    for r in rules:
        lines.append(f"% {r.rule_id}: {r.description}")

    return "\n".join(lines) + "\n"


def to_litigation_matrix(report: Dict[str, object]) -> Dict[str, object]:
    out = {
        "generated_at": report["generated_at"],
        "modes": {},
    }
    for mode, data in report["modes"].items():
        parties = []
        for party, state in sorted(data["party_deontic_state"].items()):
            parties.append(
                {
                    "party": party,
                    "obligations": state["O"],
                    "permissions": state["P"],
                    "prohibitions": state["F"],
                    "counts": {
                        "O": len(state["O"]),
                        "P": len(state["P"]),
                        "F": len(state["F"]),
                    },
                }
            )
        out["modes"][mode] = {
            "active_rule_count": len(data["active_rules"]),
            "unresolved_rule_count": len(data["unresolved_rules"]),
            "inactive_rule_count": len(data.get("inactive_rules", [])),
            "parties": parties,
        }
    return out


def build_case_state_dashboard(report: Dict[str, object]) -> Dict[str, object]:
    audits = {a["audit_id"]: a for a in report.get("element_audits", [])}

    def statuses(audit_id: str) -> Dict[str, str]:
        audit = audits.get(audit_id, {})
        return {el["element_id"]: el["status"] for el in audit.get("elements", [])}

    dashboard = {
        "generated_at": report["generated_at"],
        "filing_ready_now": [],
        "proof_gated_now": [],
        "workflow_open_now": [],
    }

    contempt = statuses("audit_remedial_contempt_timing")
    if (
        contempt.get("valid_order") == "verified"
        and contempt.get("notice") == "verified"
        and contempt.get("post_notice_conduct") == "verified"
    ):
        dashboard["filing_ready_now"].append(
            {
                "branch_id": "remedial_contempt_show_cause",
                "label": "Remedial contempt / show-cause timing branch",
                "status": "substantially_filing_ready",
                "promotion_trigger": "Stage certified appearance or docket materials to strengthen filing-grade contempt support.",
            }
        )

    probate = statuses("audit_probate_objection_hearing_timing")
    if all(probate.get(k) == "verified" for k in ("notice_issued", "objection_presented", "hearing_required")):
        dashboard["filing_ready_now"].append(
            {
                "branch_id": "probate_objection_hearing",
                "label": "Probate objection / hearing branch",
                "status": "filing_ready",
                "promotion_trigger": "No additional promotion trigger required for baseline hearing posture.",
            }
        )

    exhibit_r = statuses("audit_exhibit_r_subpoena_timing")
    if exhibit_r.get("local_search_negative") == "verified" and exhibit_r.get("compelled_production_needed") == "verified":
        dashboard["filing_ready_now"].append(
            {
                "branch_id": "hacc_exhibit_r_compelled_production",
                "label": "HACC Exhibit R compelled-production branch",
                "status": "filing_ready_for_subpoena",
                "promotion_trigger": "Serve the nonparty HACC packet and log service in the active service log.",
            }
        )

    sanctions = statuses("audit_orcp17_sanctions_elements")
    if any(v == "proof_gated" for v in sanctions.values()):
        dashboard["proof_gated_now"].append(
            {
                "branch_id": "orcp17_sanctions_merits",
                "label": "ORCP 17 sanctions merits branch",
                "status": "proof_gated",
                "current_progress": "challenged filing identified; sanctions predicates still proof-gated",
                "promotion_trigger": "Complete orcp17_filing_mapping.json for a specific challenged filing.",
            }
        )

    preclusion = statuses("audit_issue_preclusion_elements")
    if preclusion.get("prior_separate_proceeding_record") in {"missing", "proof_gated"} or any(
        preclusion.get(k) == "proof_gated"
        for k in (
            "identical_issue_mapped",
            "finality_mapped",
            "party_privity_mapped",
            "full_fair_opportunity_mapped",
        )
    ):
        dashboard["proof_gated_now"].append(
            {
                "branch_id": "issue_preclusion_merits",
                "label": "Issue-preclusion merits branch",
                "status": "proof_gated",
                "current_progress": "doctrine grounded; prior proceeding record and element mapping still incomplete",
                "promotion_trigger": "Stage certified prior-proceeding materials and complete issue_preclusion_mapping.json.",
            }
        )

    if exhibit_r.get("service_stage_complete") == "missing" or exhibit_r.get("deficiency_or_compel_stage") == "missing":
        dashboard["workflow_open_now"].append(
            {
                "branch_id": "exhibit_r_subpoena_workflow",
                "label": "Exhibit R subpoena workflow",
                "status": "workflow_open",
                "promotion_trigger": "Update 28_active_service_log_2026-04-07.csv as service and later deficiency/compel events occur.",
            }
        )

    if preclusion.get("prior_separate_proceeding_record") == "missing":
        dashboard["workflow_open_now"].append(
            {
                "branch_id": "certified_prior_proceeding_staging",
                "label": "Certified prior-proceeding staging hook",
                "status": "workflow_open",
                "promotion_trigger": "Place certified prior-order, docket/register, and hearing/appearance files in evidence_notes/certified_records.",
            }
        )

    return dashboard


def build_orcp17_readiness_snapshot(report: Dict[str, object]) -> Dict[str, object]:
    audits = {a["audit_id"]: a for a in report.get("element_audits", [])}
    sanctions_audit = audits.get("audit_orcp17_sanctions_elements", {})
    sanctions_elements = sanctions_audit.get("elements", [])
    statuses = {el["element_id"]: el["status"] for el in sanctions_elements}
    notes = {el["element_id"]: el.get("note", "") for el in sanctions_elements if el.get("note")}

    promotion_targets = {
        "challenged_filing_identified": "Keep a caption/date/source anchor in orcp17_filing_mapping.json.",
        "unsupported_factual_assertion_mapped": "Stage the conflicting prior-order record, complete the factual-assertion worksheet, then update the manifest boolean.",
        "unsupported_legal_position_mapped": "Stage the prior-proceeding record, complete issue-preclusion mapping, then update the legal-position worksheet and manifest boolean.",
        "improper_purpose_mapped": "Add stronger filing-specific motive support, then update the improper-purpose worksheet and manifest boolean.",
    }
    priority_order = [
        "unsupported_factual_assertion_mapped",
        "unsupported_legal_position_mapped",
        "improper_purpose_mapped",
    ]
    next_priority = next((item for item in priority_order if statuses.get(item) != "verified"), None)

    snapshot = {
        "generated_at": report["generated_at"],
        "branch_id": "orcp17_sanctions_merits",
        "label": "ORCP 17 sanctions readiness snapshot",
        "overall_status": "proof_gated" if any(v != "verified" for v in statuses.values()) else "mapped",
        "current_progress": (
            "challenged filing identified; sanctions predicates still proof-gated"
            if statuses.get("challenged_filing_identified") == "verified"
            else "challenged filing not yet identified"
        ),
        "next_priority": next_priority,
        "elements": [],
    }

    for element_id in (
        "challenged_filing_identified",
        "unsupported_factual_assertion_mapped",
        "unsupported_legal_position_mapped",
        "improper_purpose_mapped",
    ):
        snapshot["elements"].append(
            {
                "element_id": element_id,
                "status": statuses.get(element_id, "missing"),
                "note": notes.get(element_id, ""),
                "promotion_trigger": promotion_targets.get(element_id, ""),
            }
        )

    return snapshot


def dashboard_markdown(dashboard: Dict[str, object]) -> str:
    lines = [
        "# Formal Case State Dashboard",
        "",
        f"Generated: {dashboard['generated_at']}",
        "",
    ]
    for section, title in (
        ("filing_ready_now", "Filing-Ready Now"),
        ("proof_gated_now", "Proof-Gated Now"),
        ("workflow_open_now", "Workflow-Open Now"),
    ):
        lines.append(f"## {title}")
        for item in dashboard.get(section, []):
            lines.append(f"- {item['branch_id']}: {item['label']}")
            lines.append(f"- Status: {item['status']}")
            if item.get("current_progress"):
                lines.append(f"- Current progress: {item['current_progress']}")
            lines.append(f"- Promotion trigger: {item['promotion_trigger']}")
            lines.append("")
    return "\n".join(lines) + "\n"


def orcp17_snapshot_markdown(snapshot: Dict[str, object]) -> str:
    lines = [
        "# ORCP 17 Readiness Snapshot",
        "",
        f"Generated: {snapshot['generated_at']}",
        "",
        f"- Branch: {snapshot['branch_id']}",
        f"- Label: {snapshot['label']}",
        f"- Overall status: {snapshot['overall_status']}",
        f"- Current progress: {snapshot['current_progress']}",
    ]
    if snapshot.get("next_priority"):
        lines.append(f"- Next priority: {snapshot['next_priority']}")
    lines.append("")
    lines.append("## Elements")
    for element in snapshot.get("elements", []):
        lines.append(f"- {element['element_id']}: {element['status']}")
        if element.get("note"):
            lines.append(f"- Note: {element['note']}")
        if element.get("promotion_trigger"):
            lines.append(f"- Promotion trigger: {element['promotion_trigger']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def report_markdown(report: Dict[str, object], matrix: Dict[str, object]) -> str:
    lines = [
        "# Deontic Reasoning Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
    ]
    fos = report.get("fact_override_summary", {})
    lines.append("## Fact Override Intake")
    lines.append(f"- Override file: {fos.get('override_file')}")
    lines.append(f"- Rows read: {fos.get('rows_read', 0)}")
    lines.append(f"- Applied: {fos.get('applied_count', 0)}")
    lines.append(f"- Skipped: {fos.get('skipped_count', 0)}")
    lines.append(f"- Applied status changes: {fos.get('applied_status_changes', 0)}")
    lines.append(f"- Applied value changes: {fos.get('applied_value_changes', 0)}")
    lines.append(f"- Applied status/value changes: {fos.get('applied_status_or_value_changes', 0)}")
    lines.append(f"- Applied source changes: {fos.get('applied_source_changes', 0)}")
    lines.append(f"- Applied date additions: {fos.get('applied_date_additions', 0)}")
    lines.append("")
    lines.append("## Temporal Intervals")
    for interval in report.get("temporal_intervals", []):
        lines.append(
            f"- {interval['interval_id']}: {interval['start_date']} -> {interval.get('end_date')} "
            f"[{interval.get('status')}; tags: {', '.join(interval.get('tags', [])) or 'none'}]"
        )
    lines.append("")
    lines.append("## Element Audits")
    for audit in report.get("element_audits", []):
        lines.append(f"- {audit['audit_id']}: {audit['label']}")
        lines.append(f"- Authority: {audit.get('governing_authority')}")
        lines.append(f"- Intervals: {audit.get('interval_refs')}")
        for el in audit.get("elements", []):
            lines.append(
                f"- Element {el['element_id']}: {el['status']} "
                f"(facts={el.get('fact_ids', [])})"
            )
            if el.get("note"):
                lines.append(f"- Note: {el['note']}")
        lines.append("")
    for mode in ("strict", "inclusive"):
        lines.append(f"## Mode: {mode}")
        m = report["modes"][mode]
        lines.append(f"- Active rules: {len(m['active_rules'])}")
        lines.append(f"- Unresolved rules: {len(m['unresolved_rules'])}")
        lines.append(f"- Inactive rules: {len(m.get('inactive_rules', []))}")
        lines.append("- Party deontic state:")
        for party, state in sorted(m["party_deontic_state"].items()):
            lines.append(f"- {party}: O={len(state['O'])}, P={len(state['P'])}, F={len(state['F'])}")
        lines.append("- Active rule activation-date estimates:")
        for item in m["active_rules"]:
            profile = item.get("temporal_profile", {})
            tags = ", ".join(profile.get("temporal_tags", [])) or "none"
            refs = ", ".join(profile.get("interval_refs", [])) or "none"
            lines.append(
                f"- {item['rule_id']}: {item.get('activation_date_estimate')} "
                f"[window {profile.get('earliest_date')} -> {profile.get('latest_date')}; tags: {tags}; intervals: {refs}]"
            )
        lines.append("")

    lines.append("## Litigation Matrix Snapshot")
    for mode in ("strict", "inclusive"):
        lines.append(f"- {mode}: {len(matrix['modes'][mode]['parties'])} parties with active O/P/F states")
    lines.append("")
    return "\n".join(lines) + "\n"


def matrix_markdown(matrix: Dict[str, object]) -> str:
    lines = [
        "# Deontic Litigation Matrix",
        "",
        f"Generated: {matrix['generated_at']}",
        "",
    ]
    for mode in ("strict", "inclusive"):
        m = matrix["modes"][mode]
        lines.append(f"## Mode: {mode}")
        lines.append(f"- Active rules: {m['active_rule_count']}")
        lines.append(f"- Unresolved rules: {m['unresolved_rule_count']}")
        lines.append(f"- Inactive rules: {m.get('inactive_rule_count', 0)}")
        for row in m["parties"]:
            lines.append(f"- Party: {row['party']}")
            lines.append(f"- Counts: O={row['counts']['O']} P={row['counts']['P']} F={row['counts']['F']}")
            if row["obligations"]:
                lines.append("- Obligations:")
                for o in row["obligations"]:
                    lines.append(f"- {o['action']} -> {o['target']} ({o['rule_id']}, at {o.get('activation_date_estimate')})")
            if row["permissions"]:
                lines.append("- Permissions:")
                for p in row["permissions"]:
                    lines.append(f"- {p['action']} -> {p['target']} ({p['rule_id']}, at {p.get('activation_date_estimate')})")
            if row["prohibitions"]:
                lines.append("- Prohibitions:")
                for f in row["prohibitions"]:
                    lines.append(f"- {f['action']} -> {f['target']} ({f['rule_id']}, at {f.get('activation_date_estimate')})")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    ocr_dates = load_ocr_date_index()
    solomon_events = load_solomon_event_feed()
    solomon_repo_hits = load_solomon_repository_index()
    active_service_rows = load_active_service_rows()
    facts_raw = build_facts(ocr_dates, solomon_events, solomon_repo_hits, active_service_rows)
    fact_overrides = load_fact_overrides()
    facts, fact_override_summary = apply_fact_overrides(facts_raw, fact_overrides)
    rules = build_rules()
    report = build_reasoning_report(
        facts,
        rules,
        ocr_dates,
        solomon_events,
        solomon_repo_hits,
        fact_override_summary=fact_override_summary,
    )
    kg = to_knowledge_graph(facts, rules, report)
    dep = to_dependency_graph(rules, report)
    matrix = to_litigation_matrix(report)
    dashboard = build_case_state_dashboard(report)
    orcp17_snapshot = build_orcp17_readiness_snapshot(report)

    (OUT / "full_case_knowledge_graph.json").write_text(json.dumps(kg, indent=2), encoding="utf-8")
    (OUT / "case_dependency_graph.json").write_text(json.dumps(dep, indent=2), encoding="utf-8")
    (OUT / "case_dependency_graph.dot").write_text(to_dot(dep), encoding="utf-8")
    (OUT / "case_flogic.flr").write_text(to_flogic(facts, rules), encoding="utf-8")
    (OUT / "case_temporal_deontic_fol.tfol").write_text(to_tdfol(facts, rules), encoding="utf-8")
    (OUT / "case_deontic_cognitive_event_calculus.pl").write_text(to_event_calculus(facts, rules), encoding="utf-8")
    (OUT / "deontic_reasoning_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    (OUT / "deontic_litigation_matrix.json").write_text(json.dumps(matrix, indent=2), encoding="utf-8")
    (OUT / "deontic_reasoning_report.md").write_text(report_markdown(report, matrix), encoding="utf-8")
    (OUT / "deontic_litigation_matrix.md").write_text(matrix_markdown(matrix), encoding="utf-8")
    (OUT / "formal_case_state_dashboard.json").write_text(json.dumps(dashboard, indent=2), encoding="utf-8")
    (OUT / "formal_case_state_dashboard.md").write_text(dashboard_markdown(dashboard), encoding="utf-8")
    (OUT / "orcp17_readiness_snapshot.json").write_text(json.dumps(orcp17_snapshot, indent=2), encoding="utf-8")
    (OUT / "orcp17_readiness_snapshot.md").write_text(orcp17_snapshot_markdown(orcp17_snapshot), encoding="utf-8")


if __name__ == "__main__":
    main()
