"""
Combined Title 18 + contract deontic analysis for the HACC eviction bar theory.

This package formalizes the proposition that HACC was forbidden to file eviction
while triggered Section 18 relocation duties and HACC's undertaken relocation-
process commitments remained materially incomplete.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import sys
from typing import Any, Dict, List

if __package__ in {None, ""}:
    workspace_root = Path(__file__).resolve().parent.parent
    workspace_root_str = str(workspace_root)
    if workspace_root_str not in sys.path:
        sys.path.insert(0, workspace_root_str)

from formal_logic.frame_logic import FrameKnowledgeBase


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUT_DIR = ROOT / "outputs"
CURRENT_DATE = datetime(2026, 4, 6)


@dataclass(frozen=True)
class PartySpec:
    party_id: str
    name: str
    role: str


PARTIES: Dict[str, PartySpec] = {
    "org:hacc": PartySpec("org:hacc", "Housing Authority of Clackamas County", "PHA / relocating party"),
    "org:quantum": PartySpec("org:quantum", "Quantum Residential", "Property manager / intake actor"),
    "person:benjamin_barber": PartySpec("person:benjamin_barber", "Benjamin Barber", "Household member / applicant"),
    "person:jane_cortez": PartySpec("person:jane_cortez", "Jane Cortez", "Household member / applicant"),
    "person:household": PartySpec("person:household", "Barber-Cortez household", "Displaced household"),
}


AUTHORITIES: List[Dict[str, Any]] = [
    {
        "authority_id": "auth:42_usc_1437p_d",
        "title": "42 U.S.C. § 1437p(d)",
        "type": "statute",
        "proposition": "When public housing demolition or disposition is approved, the public housing agency must provide relocation assistance and replacement housing protections before displacement is treated as complete.",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1437p&num=0&edition=prelim",
    },
    {
        "authority_id": "auth:24_cfr_970_21",
        "title": "24 C.F.R. § 970.21",
        "type": "regulation",
        "proposition": "Relocation housing must be comparable, relocation assistance must be provided, and displacement may not be treated as complete until the relocation framework is satisfied.",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-970/section-970.21",
    },
    {
        "authority_id": "auth:ors_105_135",
        "title": "ORS 105.135",
        "type": "statute",
        "proposition": "Oregon law recognizes noncompliance with Section 18 federal relocation requirements as an affirmative defense in the eviction setting.",
        "sourceUrl": "https://www.oregonlegislature.gov/bills_laws/ors/ors105.html",
    },
    {
        "authority_id": "auth:staley_v_taylor",
        "title": "Staley v. Taylor, 165 Or App 256 (2000)",
        "type": "case",
        "proposition": "An implied-in-fact contract has the same legal effect as an express contract, though the agreement is inferred from conduct.",
        "sourceUrl": "https://law.justia.com/cases/oregon/court-of-appeals/2000/a101516.html",
    },
    {
        "authority_id": "auth:wiggins_v_barrett",
        "title": "Wiggins v. Barrett & Associates, 295 Or 679 (1983)",
        "type": "case",
        "proposition": "A public entity may be bound in a narrow contract setting where its conduct or clothed agents create a lawful undertaking on which the other side relies.",
        "sourceUrl": "https://law.justia.com/cases/oregon/supreme-court/1983/295-or-679-0.html",
    },
    {
        "authority_id": "auth:neiss_v_ehlers",
        "title": "Neiss v. Ehlers, 135 Or App 218 (1995)",
        "type": "case",
        "proposition": "Promissory estoppel can supply relief where a sufficiently concrete promise induces reliance even if a complete contract is disputed.",
        "sourceUrl": "https://law.justia.com/cases/oregon/court-of-appeals/1995/135-or-app-218.html",
    },
]


def _source(path: str, note: str = "") -> Dict[str, str]:
    payload = {"path": path}
    if note:
        payload["note"] = note
    return payload


EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "ev:phase2_notice_triggered_section18",
        "headline": "Phase II notice triggered the redevelopment-relocation framework",
        "kind": "notice",
        "proposition": "HACC's September 19, 2024 Phase II notice shows Section 18 demolition/disposition approval and triggered relocation duties.",
        "sources": [
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/full-evidence-review-run/chronology/formal_complaint_recommended_filing_packet/included/02_Exhibit_B_HACC_phase2_2024.pdf"),
            _source("/home/barberb/HACC/Breach of Contract/outputs/title18_breach_report.json", "Finding breach:hacc:premature_eviction and related relocation findings rely on the Phase II notice."),
        ],
    },
    {
        "evidence_id": "ev:jan8_blossom_notice",
        "headline": "January 8 notice directed the household into the Blossom / TPV path",
        "kind": "notice",
        "proposition": "HACC's January 8, 2026 notice directed the household to contact Ashley Ferron to start the Blossom / Tenant Protection Voucher process.",
        "sources": [
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/full-evidence-review-run/chronology/formal_complaint_recommended_filing_packet/included/07_Exhibit_G_HACC_Jan_2026_blossom.pdf"),
            _source("/home/barberb/HACC/Breach of Contract/outputs/contract_breach_report.json", "Supporting evidence for contract:hacc:relocation_commitment and implied_contract:hacc:relocation_process."),
        ],
    },
    {
        "evidence_id": "ev:quantum_packet_not_forwarded",
        "headline": "HACC acknowledged the intake packet was left with Quantum but did not reach HACC",
        "kind": "email",
        "proposition": "HACC wrote that the intake packet was submitted to Quantum Residential staff at the Hillside Manor leasing office but was not provided to HACC.",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml"),
            _source("/home/barberb/HACC/Breach of Contract/outputs/contract_breach_report.json", "Supporting evidence for implied_contract:hacc:relocation_process and Quantum intake-processing findings."),
        ],
    },
    {
        "evidence_id": "ev:waterleaf_port_pending_late_march",
        "headline": "The alternative Waterleaf / Multnomah path remained incomplete into late March 2026",
        "kind": "application_and_email",
        "proposition": "The Waterleaf application existed by December 23, 2025 and the household was still waiting on voucher issuance in late March 2026.",
        "sources": [
            _source("/home/barberb/HACC/evidence/history/waterleaf_application.png"),
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml"),
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/full-evidence-review-run/chronology/emergency_motion_packet/exhibits/Exhibit M - starworks5-ktilton-orientation-import/0008-Re-HCV-Orientation-CAMTdTS_hM81x2YFGZBGX3tGzBJjMjn5WhiFW-NwOC0k23-63LQ-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:no_counseling_no_expenses_no_comparable_unit",
        "headline": "The formal Title 18 record treats relocation as incomplete at eviction time",
        "kind": "formal_finding",
        "proposition": "The title18 report states there was no completed counseling, relocation-expense support, or comparable replacement-housing outcome by the time HACC moved toward eviction.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/outputs/title18_breach_report.json", "Findings breach:hacc:premature_eviction, breach:hacc:relocation_services, and breach:hacc:inaccessible_replacement_offer."),
        ],
    },
    {
        "evidence_id": "ev:contract_relocation_commitment",
        "headline": "The formal contract report treats HACC's relocation commitment as a concrete household undertaking",
        "kind": "formal_finding",
        "proposition": "The contract report concludes that HACC put the household into a specific relocation transaction and failed to carry it through before suing for possession.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/outputs/contract_breach_report.json", "Findings contract:hacc:relocation_commitment, implied_contract:hacc:relocation_process, and promissory_estoppel:hacc:relocation_reliance."),
        ],
    },
    {
        "evidence_id": "ev:household_substantial_performance",
        "headline": "The current record does not strongly show household breach of the application path",
        "kind": "formal_finding",
        "proposition": "The title18 report currently finds no strong evidence that Benjamin Barber or Jane Cortez breached the packet-submission duty.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/outputs/title18_breach_report.json", "Finding no_breach:household:submission_duty."),
        ],
    },
    {
        "evidence_id": "ev:eviction_filed_with_relocation_incomplete",
        "headline": "The formal reports treat the March 2026 eviction as filed while relocation remained incomplete",
        "kind": "formal_finding",
        "proposition": "The reports treat the March 31, 2026 eviction event as occurring while relocation remained incomplete.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/outputs/title18_breach_report.json"),
            _source("/home/barberb/HACC/Breach of Contract/outputs/contract_breach_report.json"),
        ],
    },
]


EVENTS: List[Dict[str, Any]] = [
    {
        "event_id": "evt_phase2_notice",
        "date": "2024-09-19",
        "label": "Section 18 relocation triggered by Phase II notice",
        "event_type": "trigger",
        "actors": ["org:hacc"],
        "targets": ["person:household"],
        "evidence_ids": ["ev:phase2_notice_triggered_section18"],
    },
    {
        "event_id": "evt_jan8_directed_blossom_path",
        "date": "2026-01-08",
        "label": "HACC directed the household into the Blossom / TPV path",
        "event_type": "direction",
        "actors": ["org:hacc"],
        "targets": ["person:household"],
        "evidence_ids": ["ev:jan8_blossom_notice"],
    },
    {
        "event_id": "evt_quantum_packet_nontransmission",
        "date": "2026-01-26",
        "label": "HACC acknowledged Quantum-side packet nontransmission",
        "event_type": "processing_failure_notice",
        "actors": ["org:hacc", "org:quantum"],
        "targets": ["person:household"],
        "evidence_ids": ["ev:quantum_packet_not_forwarded"],
    },
    {
        "event_id": "evt_waterleaf_path_still_pending",
        "date": "2026-03-25",
        "label": "Waterleaf / Multnomah portability path remained pending",
        "event_type": "pending_transfer",
        "actors": ["org:hacc", "person:household"],
        "targets": ["person:household"],
        "evidence_ids": ["ev:waterleaf_port_pending_late_march"],
    },
    {
        "event_id": "evt_relocation_still_incomplete",
        "date": "2026-03-31",
        "label": "Relocation remained incomplete at eviction time",
        "event_type": "state_of_affairs",
        "actors": ["org:hacc"],
        "targets": ["person:household"],
        "evidence_ids": [
            "ev:no_counseling_no_expenses_no_comparable_unit",
            "ev:contract_relocation_commitment",
            "ev:household_substantial_performance",
            "ev:eviction_filed_with_relocation_incomplete",
        ],
    },
]


OBLIGATIONS: List[Dict[str, Any]] = [
    {
        "obligation_id": "obl_hacc_complete_section18_relocation",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "complete triggered Section 18 relocation duties before displacement is treated as complete",
        "legal_basis": "42 U.S.C. § 1437p(d); 24 C.F.R. § 970.21",
        "trigger_event_ids": ["evt_phase2_notice"],
        "evidence_ids": ["ev:phase2_notice_triggered_section18", "ev:no_counseling_no_expenses_no_comparable_unit"],
        "duty_scope": "title18_direct_duty",
    },
    {
        "obligation_id": "obl_hacc_relocation_counseling",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "provide relocation counseling before displacement is completed",
        "legal_basis": "42 U.S.C. § 1437p(d); 24 C.F.R. § 970.21",
        "trigger_event_ids": ["evt_phase2_notice"],
        "evidence_ids": ["ev:no_counseling_no_expenses_no_comparable_unit"],
        "duty_scope": "title18_component_duty",
    },
    {
        "obligation_id": "obl_hacc_moving_expense_support",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "pay or commit relocation moving-expense support before displacement is completed",
        "legal_basis": "42 U.S.C. § 1437p(d); 24 C.F.R. § 970.21",
        "trigger_event_ids": ["evt_phase2_notice"],
        "evidence_ids": ["ev:no_counseling_no_expenses_no_comparable_unit"],
        "duty_scope": "title18_component_duty",
    },
    {
        "obligation_id": "obl_hacc_comparable_replacement_housing",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "offer comparable replacement housing before displacement is completed",
        "legal_basis": "42 U.S.C. § 1437p(d); 24 C.F.R. § 970.21",
        "trigger_event_ids": ["evt_phase2_notice"],
        "evidence_ids": ["ev:no_counseling_no_expenses_no_comparable_unit"],
        "duty_scope": "title18_component_duty",
    },
    {
        "obligation_id": "obl_hacc_perform_relocation_commitment",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "perform the relocation commitment and linked replacement-housing pathway HACC undertook for the household",
        "legal_basis": "contract:hacc:relocation_commitment finding; 24 C.F.R. § 970.21 as incorporated/implied performance standard",
        "trigger_event_ids": ["evt_phase2_notice", "evt_jan8_directed_blossom_path"],
        "evidence_ids": ["ev:contract_relocation_commitment", "ev:jan8_blossom_notice"],
        "duty_scope": "contractual_or_undertaking_duty",
    },
    {
        "obligation_id": "obl_hacc_administer_implied_relocation_process",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "obligatory",
        "action": "administer the implied relocation-process agreement with continuity and ordinary care",
        "legal_basis": "Staley v. Taylor; Wiggins v. Barrett; implied_contract:hacc:relocation_process finding",
        "trigger_event_ids": ["evt_jan8_directed_blossom_path", "evt_quantum_packet_nontransmission"],
        "evidence_ids": ["ev:contract_relocation_commitment", "ev:quantum_packet_not_forwarded"],
        "duty_scope": "implied_contract_duty",
    },
    {
        "obligation_id": "obl_household_substantial_performance_preserves_hacc_duties",
        "actor": "person:household",
        "recipient": "org:hacc",
        "modality": "permitted",
        "action": "rely on substantial performance of the application and relocation path to keep HACC's duties live",
        "legal_basis": "title18 no_breach:household:submission_duty finding; contract no_contract_breach:household:substantial_performance finding",
        "trigger_event_ids": ["evt_jan8_directed_blossom_path", "evt_quantum_packet_nontransmission"],
        "evidence_ids": ["ev:household_substantial_performance"],
        "duty_scope": "counterparty_performance_status",
    },
    {
        "obligation_id": "obl_hacc_no_eviction_before_relocation_complete",
        "actor": "org:hacc",
        "recipient": "person:household",
        "modality": "prohibited",
        "action": "file eviction before triggered relocation duties and undertaken relocation-process commitments are materially completed",
        "legal_basis": "42 U.S.C. § 1437p(d); 24 C.F.R. § 970.21; contract:hacc:relocation_commitment; implied_contract:hacc:relocation_process",
        "trigger_event_ids": ["evt_relocation_still_incomplete"],
        "evidence_ids": [
            "ev:no_counseling_no_expenses_no_comparable_unit",
            "ev:contract_relocation_commitment",
            "ev:household_substantial_performance",
            "ev:eviction_filed_with_relocation_incomplete",
        ],
        "duty_scope": "combined_bar_on_eviction",
    },
]


FINDINGS: List[Dict[str, Any]] = [
    {
        "finding_id": "finding_hacc_eviction_bar_active",
        "status": "supported",
        "summary": "The combined Title 18 and contract record supports that HACC was forbidden to file eviction while triggered relocation duties and undertaken relocation-process commitments remained materially incomplete.",
        "supporting_obligation_ids": ["obl_hacc_no_eviction_before_relocation_complete"],
        "supporting_evidence_ids": [
            "ev:phase2_notice_triggered_section18",
            "ev:no_counseling_no_expenses_no_comparable_unit",
            "ev:contract_relocation_commitment",
            "ev:household_substantial_performance",
            "ev:eviction_filed_with_relocation_incomplete",
        ],
    },
    {
        "finding_id": "finding_hacc_failed_component_relocation_duties",
        "status": "supported",
        "summary": "The formal Title 18 record supports failures in counseling, moving-expense support, and comparable replacement housing before displacement was treated as complete.",
        "supporting_obligation_ids": [
            "obl_hacc_relocation_counseling",
            "obl_hacc_moving_expense_support",
            "obl_hacc_comparable_replacement_housing",
        ],
        "supporting_evidence_ids": ["ev:no_counseling_no_expenses_no_comparable_unit"],
    },
    {
        "finding_id": "finding_hacc_failed_undertaken_relocation_process",
        "status": "supported",
        "summary": "The formal contract record supports that HACC undertook a specific relocation transaction and implied relocation process and failed to carry it through before suing for possession.",
        "supporting_obligation_ids": [
            "obl_hacc_perform_relocation_commitment",
            "obl_hacc_administer_implied_relocation_process",
        ],
        "supporting_evidence_ids": ["ev:contract_relocation_commitment", "ev:quantum_packet_not_forwarded"],
    },
]


def _build_frames() -> Dict[str, Any]:
    kb = FrameKnowledgeBase()
    for party in PARTIES.values():
        kb.add_fact(party.party_id, party.name, "role", party.role, "party_catalog")
    for authority in AUTHORITIES:
        kb.add_fact(authority["authority_id"], authority["title"], "type", authority["type"], authority["sourceUrl"])
        kb.add_fact(authority["authority_id"], authority["title"], "proposition", authority["proposition"], authority["sourceUrl"])
    for evidence in EVIDENCE:
        for src in evidence["sources"]:
            kb.add_fact(evidence["evidence_id"], evidence["headline"], "source", src["path"], src["path"])
        kb.add_fact(evidence["evidence_id"], evidence["headline"], "kind", evidence["kind"], evidence["sources"][0]["path"])
        kb.add_fact(evidence["evidence_id"], evidence["headline"], "proposition", evidence["proposition"], evidence["sources"][0]["path"])
    for event in EVENTS:
        for eid in event["evidence_ids"]:
            kb.add_fact(event["event_id"], event["label"], "supportedBy", eid, eid)
        kb.add_fact(event["event_id"], event["label"], "date", event["date"], event["event_id"])
        kb.add_fact(event["event_id"], event["label"], "type", event["event_type"], event["event_id"])
    for obligation in OBLIGATIONS:
        kb.add_fact(obligation["obligation_id"], obligation["action"], "actor", obligation["actor"], obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "recipient", obligation["recipient"], obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "modality", obligation["modality"], obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "legal_basis", obligation["legal_basis"], obligation["legal_basis"])
        for event_id in obligation["trigger_event_ids"]:
            kb.add_fact(obligation["obligation_id"], obligation["action"], "triggeredBy", event_id, event_id)
        for evidence_id in obligation["evidence_ids"]:
            kb.add_fact(obligation["obligation_id"], obligation["action"], "supportedBy", evidence_id, evidence_id)
    return kb.to_dict()


def _build_knowledge_graph() -> Dict[str, Any]:
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, Any]] = []

    for party in PARTIES.values():
        nodes[party.party_id] = {"label": party.name, "type": "party", "role": party.role}
    for authority in AUTHORITIES:
        nodes[authority["authority_id"]] = {"label": authority["title"], "type": "authority"}
    for evidence in EVIDENCE:
        nodes[evidence["evidence_id"]] = {"label": evidence["headline"], "type": "evidence"}
    for event in EVENTS:
        nodes[event["event_id"]] = {"label": event["label"], "type": "event", "date": event["date"]}
    for obligation in OBLIGATIONS:
        nodes[obligation["obligation_id"]] = {
            "label": obligation["action"],
            "type": "obligation",
            "modality": obligation["modality"],
        }
        edges.append({"from": obligation["actor"], "to": obligation["obligation_id"], "relation": "bears"})
        edges.append({"from": obligation["obligation_id"], "to": obligation["recipient"], "relation": "owed_to"})
        for event_id in obligation["trigger_event_ids"]:
            edges.append({"from": event_id, "to": obligation["obligation_id"], "relation": "triggers"})
        for evidence_id in obligation["evidence_ids"]:
            edges.append({"from": evidence_id, "to": obligation["obligation_id"], "relation": "supports"})
    for finding in FINDINGS:
        nodes[finding["finding_id"]] = {"label": finding["summary"], "type": "finding", "status": finding["status"]}
        for oid in finding["supporting_obligation_ids"]:
            edges.append({"from": oid, "to": finding["finding_id"], "relation": "supports"})
        for eid in finding["supporting_evidence_ids"]:
            edges.append({"from": eid, "to": finding["finding_id"], "relation": "supports"})
    return {"nodes": nodes, "edges": edges}


def _build_dependency_graph() -> Dict[str, Any]:
    return {
        "nodes": {
            "section18_triggered_imposes_relocation_duties": {
                "label": "Section 18 trigger imposes relocation duties",
                "authorities": ["auth:42_usc_1437p_d", "auth:24_cfr_970_21"],
                "evidence": ["ev:phase2_notice_triggered_section18"],
            },
            "relocation_component_duties_must_be_satisfied": {
                "label": "Counseling, moving-expense support, and comparable housing are component duties",
                "authorities": ["auth:42_usc_1437p_d", "auth:24_cfr_970_21"],
                "evidence": ["ev:no_counseling_no_expenses_no_comparable_unit"],
            },
            "hacc_undertook_specific_relocation_process": {
                "label": "HACC undertook a specific relocation and replacement-housing process",
                "authorities": ["auth:staley_v_taylor", "auth:wiggins_v_barrett", "auth:neiss_v_ehlers"],
                "evidence": ["ev:jan8_blossom_notice", "ev:contract_relocation_commitment", "ev:quantum_packet_not_forwarded"],
            },
            "household_substantial_performance_keeps_duties_live": {
                "label": "Household substantial performance keeps HACC duties live",
                "authorities": ["auth:staley_v_taylor"],
                "evidence": ["ev:household_substantial_performance"],
            },
            "eviction_forbidden_while_duties_incomplete": {
                "label": "Eviction is forbidden while triggered duties and undertaken performance remain incomplete",
                "authorities": ["auth:42_usc_1437p_d", "auth:24_cfr_970_21", "auth:ors_105_135", "auth:staley_v_taylor"],
                "evidence": ["ev:eviction_filed_with_relocation_incomplete", "ev:no_counseling_no_expenses_no_comparable_unit", "ev:contract_relocation_commitment"],
            },
        },
        "edges": [
            {"from": "section18_triggered_imposes_relocation_duties", "to": "relocation_component_duties_must_be_satisfied", "relation": "implies"},
            {"from": "section18_triggered_imposes_relocation_duties", "to": "eviction_forbidden_while_duties_incomplete", "relation": "supports"},
            {"from": "relocation_component_duties_must_be_satisfied", "to": "eviction_forbidden_while_duties_incomplete", "relation": "supports"},
            {"from": "hacc_undertook_specific_relocation_process", "to": "eviction_forbidden_while_duties_incomplete", "relation": "reinforces"},
            {"from": "household_substantial_performance_keeps_duties_live", "to": "eviction_forbidden_while_duties_incomplete", "relation": "reinforces"},
        ],
    }


def _build_formal_models(report: Dict[str, Any]) -> Dict[str, Any]:
    tdfol_formulas = [
        {"label": "section18_relocation_completion_required", "formula": "O(CompleteTriggeredSection18RelocationDuties)"},
        {"label": "hacc_relocation_counseling_required", "formula": "O(ProvideRelocationCounselingBeforeDisplacement)"},
        {"label": "hacc_moving_expenses_required", "formula": "O(ProvideOrCommitRelocationMovingExpensesBeforeDisplacement)"},
        {"label": "hacc_comparable_replacement_required", "formula": "O(OfferComparableReplacementHousingBeforeDisplacement)"},
        {"label": "hacc_perform_relocation_commitment", "formula": "O(PerformUndertakenRelocationCommitment)"},
        {"label": "hacc_administer_implied_relocation_process", "formula": "O(AdministerImpliedRelocationProcessWithContinuityAndOrdinaryCare)"},
        {"label": "eviction_forbidden_while_duties_incomplete", "formula": "F(FileEvictionWhileTriggeredRelocationDutiesRemainIncomplete)"},
        {"label": "eviction_forbidden_while_undertaken_performance_incomplete", "formula": "F(FileEvictionWhileUndertakenRelocationPerformanceRemainsIncomplete)"},
    ]

    dcec = {
        "happens": [
            "Happens(Phase2NoticeTriggeredSection18, t_phase2)",
            "Happens(HaccDirectedBlossomPath, t_jan8)",
            "Happens(HaccAcknowledgedQuantumPacketNontransmission, t_jan26)",
            "Happens(WaterleafPathStillPending, t_mar25)",
            "Happens(EvictionFiledByHacc, t_evict)",
        ],
        "initiates": [
            {"formula": "Initiates(Phase2NoticeTriggeredSection18, TriggeredSection18RelocationDuties, t_phase2)"},
            {"formula": "Initiates(HaccDirectedBlossomPath, UndertakenRelocationCommitment, t_jan8)"},
            {"formula": "Initiates(HaccDirectedBlossomPath, ImpliedRelocationProcess, t_jan8)"},
        ],
        "holdsAt": [
            {"formula": "HoldsAt(TriggeredSection18RelocationDuties, t_evict)"},
            {"formula": "HoldsAt(UndertakenRelocationCommitment, t_evict)"},
            {"formula": "HoldsAt(ImpliedRelocationProcess, t_evict)"},
            {"formula": "HoldsAt(RelocationIncomplete, t_evict)"},
            {"formula": "HoldsAt(HouseholdSubstantiallyPerformed, t_evict)"},
        ],
        "breaches": [
            {"formula": "HoldsAt(RelocationIncomplete, t_evict) -> Forbidden(FileEvictionByHacc, t_evict)"},
            {"formula": "HoldsAt(TriggeredSection18RelocationDuties, t_evict) & HoldsAt(RelocationIncomplete, t_evict) -> Breach(HaccPrematureEvictionBar)"},
            {"formula": "HoldsAt(UndertakenRelocationCommitment, t_evict) & HoldsAt(RelocationIncomplete, t_evict) -> Breach(HaccContractualRelocationFailureBeforeEviction)"},
        ],
    }

    return {
        "frameLogic": {"frames": report["frames"]},
        "dcec": dcec,
        "tdfol": {"formulas": tdfol_formulas},
    }


def _render_flogic(report: Dict[str, Any]) -> str:
    lines = ["%% title18_contract_eviction_bar_knowledge_graph.flogic", ""]
    for party in report["parties"].values():
        pid = party["party_id"].replace(":", "_")
        lines.append(f"{pid}:Party[label->\"{party['name']}\"; role->\"{party['role']}\"].")
    lines.append("")
    for obligation in report["obligations"]:
        oid = obligation["obligation_id"]
        actor = obligation["actor"].replace(":", "_")
        recipient = obligation["recipient"].replace(":", "_")
        lines.append(
            f"{oid}:DeonticObligation[actor->{actor}; recipient->{recipient}; modality->\"{obligation['modality']}\"; action->\"{obligation['action']}\"; legalBasis->\"{obligation['legal_basis']}\"] ."
        )
    return "\n".join(lines).rstrip() + "\n"


def _render_dcec(report: Dict[str, Any]) -> str:
    dcec = report["formalModels"]["dcec"]
    lines = [
        "% title18_contract_eviction_bar_obligations_dcec.pl",
        "% DCEC-style export for Title 18 + contract eviction-bar reasoning",
        "",
    ]
    for formula in dcec["happens"]:
        lines.append(f"{formula}.")
    lines.append("")
    for entry in dcec["initiates"]:
        lines.append(f"{entry['formula']}.")
    lines.append("")
    for entry in dcec["holdsAt"]:
        lines.append(f"{entry['formula']}.")
    lines.append("")
    for entry in dcec["breaches"]:
        lines.append(f"{entry['formula']}.")
    return "\n".join(lines).rstrip() + "\n"


def _run_tdfol_audit() -> Dict[str, Any]:
    repo_path = Path("/home/barberb/HACC/complaint-generator/ipfs_datasets_py")
    if str(repo_path) not in sys.path:
        sys.path.insert(0, str(repo_path))
    try:
        from ipfs_datasets_py.logic.TDFOL.tdfol_core import TDFOLKnowledgeBase, Predicate, DeonticFormula, DeonticOperator
        from ipfs_datasets_py.logic.TDFOL.strategies.modal_tableaux import ModalTableauxStrategy
    except Exception as exc:  # pragma: no cover
        return {"available": False, "error": str(exc), "proofs": []}

    kb = TDFOLKnowledgeBase()
    strategy = ModalTableauxStrategy()
    axioms = {
        "section18_relocation_completion_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("CompleteTriggeredSection18RelocationDuties", ())),
        "hacc_relocation_counseling_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ProvideRelocationCounselingBeforeDisplacement", ())),
        "hacc_moving_expenses_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ProvideOrCommitRelocationMovingExpensesBeforeDisplacement", ())),
        "hacc_comparable_replacement_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("OfferComparableReplacementHousingBeforeDisplacement", ())),
        "hacc_perform_relocation_commitment": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("PerformUndertakenRelocationCommitment", ())),
        "hacc_administer_implied_relocation_process": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("AdministerImpliedRelocationProcessWithContinuityAndOrdinaryCare", ())),
        "eviction_forbidden_while_duties_incomplete": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("FileEvictionWhileTriggeredRelocationDutiesRemainIncomplete", ())),
        "eviction_forbidden_while_undertaken_performance_incomplete": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("FileEvictionWhileUndertakenRelocationPerformanceRemainsIncomplete", ())),
    }
    for formula in axioms.values():
        kb.add_axiom(formula)

    queries = dict(axioms)
    queries["eviction_permitted_before_completion"] = DeonticFormula(DeonticOperator.PERMISSION, Predicate("FileEvictionBeforeRelocationCompletion", ()))

    proofs = []
    for label, formula in queries.items():
        result = strategy._prove_basic_modal(formula, kb, timeout_ms=5000, start_time=0)
        proofs.append({
            "label": label,
            "formula": formula.to_string(),
            "status": result.status.value,
            "method": "ModalTableauxStrategy._prove_basic_modal",
            "proofSteps": [step.justification for step in result.proof_steps],
        })
    return {
        "available": True,
        "engine": "ipfs_datasets_py.logic.TDFOL modal tableaux",
        "proofs": proofs,
        "note": "This prover audit validates the encoded normative model that eviction is forbidden while triggered relocation and undertaken process duties remain incomplete. It does not, by itself, resolve every disputed historical fact.",
    }


def build_case_report() -> Dict[str, Any]:
    report = {
        "metadata": {
            "generatedAt": CURRENT_DATE.isoformat(),
            "caseId": "title18_contract_eviction_bar",
            "scope": "Combined Title 18, contract, implied-contract, and promissory-estoppel deontic analysis of why HACC was forbidden to file eviction while relocation remained incomplete.",
            "disclaimer": "Research artifact for issue-spotting and formal analysis. Not legal advice.",
        },
        "parties": {party_id: vars(spec) for party_id, spec in PARTIES.items()},
        "authorities": AUTHORITIES,
        "evidence": EVIDENCE,
        "events": EVENTS,
        "obligations": OBLIGATIONS,
        "findings": FINDINGS,
    }
    report["frames"] = _build_frames()
    report["knowledgeGraph"] = _build_knowledge_graph()
    report["dependencyGraph"] = _build_dependency_graph()
    report["formalModels"] = _build_formal_models(report)
    report["formalModels"]["tdfol"]["proofAudit"] = _run_tdfol_audit()
    return report


def _render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Title 18 + Contract Eviction Bar Report",
        "",
        f"- Generated: `{report['metadata']['generatedAt']}`",
        "- Thesis: HACC was forbidden to file eviction while triggered Section 18 relocation duties and HACC's undertaken relocation-process commitments remained materially incomplete.",
        "",
        "## Core Deontic Formula",
        "",
        "```text",
        "O(HACC, complete triggered Section 18 relocation duties)",
        "O(HACC, perform undertaken relocation-process commitments)",
        "not completed(triggered relocation duties)",
        "  -> F(HACC, file eviction)",
        "```",
        "",
        "## Source-Linked Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.append(f"- `{finding['finding_id']}`: {finding['summary']}")
    lines.extend([
        "",
        "## TDFOL Audit",
        "",
        f"- Prover available: `{report['formalModels']['tdfol']['proofAudit']['available']}`",
    ])
    if report["formalModels"]["tdfol"]["proofAudit"]["available"]:
        for proof in report["formalModels"]["tdfol"]["proofAudit"]["proofs"]:
            lines.append(f"- `{proof['label']}` -> `{proof['status']}`")
    lines.extend([
        "",
        "## Outputs",
        "",
        "- `title18_contract_eviction_bar_report.json`",
        "- `title18_contract_eviction_bar_report.md`",
        "- `title18_contract_eviction_bar_knowledge_graph.json`",
        "- `title18_contract_eviction_bar_dependency_graph.json`",
        "- `title18_contract_eviction_bar_knowledge_graph.flogic`",
        "- `title18_contract_eviction_bar_obligations_dcec.pl`",
        "- `title18_contract_eviction_bar_tdfol_proof_audit.json`",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: Dict[str, Any]) -> Dict[str, Path]:
    paths = {
        "report_json": OUTPUT_DIR / "title18_contract_eviction_bar_report.json",
        "report_md": OUTPUT_DIR / "title18_contract_eviction_bar_report.md",
        "knowledge_graph": OUTPUT_DIR / "title18_contract_eviction_bar_knowledge_graph.json",
        "dependency_graph": OUTPUT_DIR / "title18_contract_eviction_bar_dependency_graph.json",
        "flogic": OUTPUT_DIR / "title18_contract_eviction_bar_knowledge_graph.flogic",
        "dcec": OUTPUT_DIR / "title18_contract_eviction_bar_obligations_dcec.pl",
        "tdfol_audit": OUTPUT_DIR / "title18_contract_eviction_bar_tdfol_proof_audit.json",
    }
    paths["report_json"].write_text(json.dumps(report, indent=2) + "\n")
    paths["report_md"].write_text(_render_markdown(report))
    paths["knowledge_graph"].write_text(json.dumps(report["knowledgeGraph"], indent=2) + "\n")
    paths["dependency_graph"].write_text(json.dumps(report["dependencyGraph"], indent=2) + "\n")
    paths["flogic"].write_text(_render_flogic(report))
    paths["dcec"].write_text(_render_dcec(report))
    paths["tdfol_audit"].write_text(json.dumps(report["formalModels"]["tdfol"]["proofAudit"], indent=2) + "\n")
    return paths


def main() -> None:
    report = build_case_report()
    write_outputs(report)
    print("Wrote Title 18 + contract eviction-bar formal outputs.")


if __name__ == "__main__":
    main()
