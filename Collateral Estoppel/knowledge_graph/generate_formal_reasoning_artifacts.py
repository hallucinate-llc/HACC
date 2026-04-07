#!/usr/bin/env python3
"""Generate full case knowledge/dependency graphs and formal logic artifacts.

Outputs are written to knowledge_graph/generated/.
"""

from __future__ import annotations

from dataclasses import dataclass
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


def build_facts(
    ocr_dates: Dict[str, List[str]],
    solomon_events: List[Dict[str, object]],
    solomon_repo_hits: List[Dict[str, object]],
    active_service_rows: List[Dict[str, str]],
) -> List[Fact]:
    g_dates = ocr_dates.get("solomon_motion_for_guardianship_ocr.txt", [])
    r_dates = ocr_dates.get("sam_barber_restraining_order_ocr.txt", [])

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
        Fact("f_client_prior_appointment", "PriorAppointmentExists", ("person:jane_cortez", "person:benjamin_barber"), True, "alleged", "client_assertion"),
        Fact("f_client_benjamin_avoided_service", "AvoidedService", ("person:benjamin_barber", "order:prior_guardianship_order"), True, "alleged", "client_assertion"),
        Fact("f_client_benjamin_order_disregard", "DisregardedOrder", ("person:benjamin_barber", "order:prior_guardianship_order"), True, "alleged", "client_assertion"),
        Fact("f_client_benjamin_housing_interference", "Interference", ("person:benjamin_barber", "process:hacc_housing_contract"), True, "alleged", "client_assertion"),
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
    authority_placeholder_file = FINAL_SET / "06_oregon_authority_table_placeholders.md"

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
            ("doc:06_oregon_authority_table_placeholders.md",),
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

            # Incomplete response heuristic once service occurred:
            # awaiting production, explicit deficiency stage, or missing required return artifacts.
            if (
                (status in {"awaiting_production", "deficiency_notice_stage", "motion_to_compel_stage"})
                or (date_served and (checklist_received in {"n", "no", "false", ""} or search_report_received in {"n", "no", "false", ""}))
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
            ("f_client_prior_appointment",),
            DeonticConclusion(
                "c1_benjamin_permitted_guardian_scope",
                "P",
                "person:benjamin_barber",
                "act_within_valid_guardian_scope",
                "person:jane_cortez",
            ),
            "If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.",
            "hypothesis",
        ),
        Rule(
            "r2_noninterference_prohibition_for_benjamin",
            ("f_client_prior_appointment", "f_client_benjamin_housing_interference"),
            DeonticConclusion(
                "c2_benjamin_forbidden_interference",
                "F",
                "person:benjamin_barber",
                "interfere_with_guardian_or_housing_process",
                "process:hacc_housing_contract",
            ),
            "If prior appointment exists and interference is alleged, Benjamin is forbidden from interference.",
            "hypothesis",
        ),
        Rule(
            "r3_benjamin_obligation_comply_or_seek_relief",
            ("f_client_prior_appointment", "f_client_benjamin_order_disregard"),
            DeonticConclusion(
                "c3_benjamin_obligated_comply_or_seek_relief",
                "O",
                "person:benjamin_barber",
                "comply_with_order_or_seek_relief",
                "order:prior_guardianship_order",
            ),
            "If prior appointment is in force and Benjamin disregarded order, Benjamin was obligated to comply or seek relief.",
            "hypothesis",
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
        ),
        Rule(
            "r22_case_obligated_finalize_authority_citations_before_filing",
            ("f_authority_table_placeholders_unresolved",),
            DeonticConclusion(
                "c22_case_obligated_finalize_authority_citations_before_filing",
                "O",
                "case:guardianship_collateral_estoppel",
                "finalize_governing_authority_citations_before_final_filing",
                "doc:06_oregon_authority_table_placeholders.md",
            ),
            "If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.",
            "filing",
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
    ]


def evaluate_rule(rule: Rule, facts_by_id: Dict[str, Fact], mode: str) -> Tuple[str, List[Dict[str, object]], str | None]:
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

    activation_date = max(known_dates) if known_dates else None

    if not all_true:
        return "inactive", detail, activation_date

    if mode == "strict":
        return ("active" if all_verified else "unresolved"), detail, activation_date

    if mode == "inclusive":
        if rule.track == "hypothesis":
            return "unresolved", detail, activation_date
        allowed = {"verified", "alleged"}
        if all(facts_by_id[fid].status in allowed and facts_by_id[fid].value for fid in rule.antecedents):
            return "active", detail, activation_date
        return "unresolved", detail, activation_date

    raise ValueError(f"Unknown mode: {mode}")


def build_reasoning_report(
    facts: List[Fact],
    rules: List[Rule],
    ocr_dates: Dict[str, List[str]],
    solomon_events: List[Dict[str, object]],
    solomon_repo_hits: List[Dict[str, object]],
) -> Dict[str, object]:
    facts_by_id = {f.fact_id: f for f in facts}
    report: Dict[str, object] = {
        "generated_at": str(date.today()),
        "ocr_date_index": ocr_dates,
        "solomon_event_feed_count": len(solomon_events),
        "solomon_repository_hit_count": len(solomon_repo_hits),
        "solomon_repository_fact_count": sum(1 for f in facts if f.predicate == "RepositorySourceMentionsSolomonCaseContext"),
        "modes": {},
    }

    for mode in ("strict", "inclusive"):
        active = []
        unresolved = []
        inactive = []
        party_state: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

        for rule in rules:
            state, antecedent_detail, activation_date = evaluate_rule(rule, facts_by_id, mode)
            item = {
                "rule_id": rule.rule_id,
                "track": rule.track,
                "authority_refs": list(rule.authority_refs),
                "description": rule.description,
                "activation_date_estimate": activation_date,
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


def report_markdown(report: Dict[str, object], matrix: Dict[str, object]) -> str:
    lines = [
        "# Deontic Reasoning Report",
        "",
        f"Generated: {report['generated_at']}",
        "",
    ]
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
            lines.append(f"- {item['rule_id']}: {item.get('activation_date_estimate')}")
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
    facts = build_facts(ocr_dates, solomon_events, solomon_repo_hits, active_service_rows)
    rules = build_rules()
    report = build_reasoning_report(facts, rules, ocr_dates, solomon_events, solomon_repo_hits)
    kg = to_knowledge_graph(facts, rules, report)
    dep = to_dependency_graph(rules, report)
    matrix = to_litigation_matrix(report)

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


if __name__ == "__main__":
    main()
