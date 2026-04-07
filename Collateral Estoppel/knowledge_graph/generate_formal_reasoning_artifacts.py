#!/usr/bin/env python3
"""Generate full case knowledge/dependency graphs and formal logic artifacts.

Outputs are written to knowledge_graph/generated/.
"""

from __future__ import annotations

from dataclasses import dataclass
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


def _pick_date(candidates: List[str], preferred: str) -> Tuple[str, ...]:
    if preferred in candidates:
        return (preferred,)
    if candidates:
        return (candidates[0],)
    return ()


def build_facts(
    ocr_dates: Dict[str, List[str]],
    solomon_events: List[Dict[str, object]],
    solomon_repo_hits: List[Dict[str, object]],
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
            "f_petition_claims_no_prior_guardian",
            "PetitionStatesNoPriorGuardian",
            ("case:26PR00641", "person:jane_cortez"),
            True,
            "verified",
            "solomon_motion_for_guardianship_ocr.txt",
            _pick_date(g_dates, "2026-03-31"),
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
        Fact("f_hacc_process_exists", "HousingProcessActive", ("org:hacc", "person:jane_cortez", "process:hacc_housing_contract"), True, "alleged", "client_assertion"),
        Fact("f_collateral_estoppel_candidate", "PotentialIssuePreclusion", ("issue:guardianship_authority",), True, "theory", "motion_to_dismiss_for_collateral_estoppel.md"),
    ]

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
        ),
        Rule(
            "r6_hacc_obligated_process_consistently_with_valid_authority",
            ("f_hacc_process_exists", "f_client_prior_appointment"),
            DeonticConclusion(
                "c6_hacc_obligated_process_consistent_with_order",
                "O",
                "org:hacc",
                "process_housing_consistent_with_valid_guardian_authority",
                "person:jane_cortez",
            ),
            "If housing process is active and appointment exists, HACC is obligated to process consistently with valid authority.",
        ),
        Rule(
            "r6b_hacc_obligated_document_lease_basis",
            ("f_hacc_lease_adjustment_effective_2026_01_01",),
            DeonticConclusion(
                "c6b_hacc_obligated_document_lease_basis",
                "O",
                "org:hacc",
                "document_basis_for_household_composition_or_lease_adjustment",
                "household:jane_cortez_household",
            ),
            "If HACC implemented a January 1, 2026 lease adjustment, HACC was obligated to document the basis for that household-composition change.",
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
        ),
        Rule(
            "r7_solomon_forbidden_refile_precluded_issue",
            ("f_collateral_estoppel_candidate", "f_client_solomon_barred_refile"),
            DeonticConclusion(
                "c7_solomon_forbidden_refile_precluded_issue",
                "F",
                "person:solomon",
                "relitigate_precluded_issue",
                "issue:guardianship_authority",
            ),
            "If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.",
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
        party_state: Dict[str, Dict[str, List[Dict[str, str]]]] = {}

        for rule in rules:
            state, antecedent_detail, activation_date = evaluate_rule(rule, facts_by_id, mode)
            item = {
                "rule_id": rule.rule_id,
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
            else:
                unresolved.append(item)

        report["modes"][mode] = {
            "active_rules": active,
            "unresolved_rules": unresolved,
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
        nodes.append({"id": rid, "kind": "rule", "description": rule.description})
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
        "% Deontic conclusions as fluents",
        "holdsAt(forbidden(solomon, abuse_contact_or_control_property, jane_cortez), T) :-",
        "    holdsAt(valid_order(eppdapa_order), T).",
        "",
        "holdsAt(obligated(solomon, appear_and_answer_show_cause, related_order_hearing), T) :-",
        "    happens(assert_refiled_barred_issue(solomon, guardianship_authority), T).",
        "",
        "holdsAt(permitted(benjamin_barber, act_within_valid_guardian_scope, jane_cortez), T) :-",
        "    holdsAt(prior_appointment(jane_cortez, benjamin_barber), T).",
        "",
        "holdsAt(forbidden(benjamin_barber, interfere_with_guardian_or_housing_process, hacc_housing_contract), T) :-",
        "    holdsAt(prior_appointment(jane_cortez, benjamin_barber), T),",
        "    holdsAt(interference(benjamin_barber, hacc_housing_contract), T).",
        "",
        "% Temporal anchors inferred from OCR",
    ]

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
    facts = build_facts(ocr_dates, solomon_events, solomon_repo_hits)
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
