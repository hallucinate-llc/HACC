"""
Formal analysis for the live-in aide / caregiver income-verification issue.

This module produces:
- a record-grounded party/event knowledge graph,
- a dependency graph for the governing HUD/HACC rules,
- F-logic and DCEC-style exports, and
- a lightweight TDFOL audit using the vendored ipfs_datasets_py prover stack.
"""

from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional


CURRENT_DATE = date(2026, 4, 5)
OUTPUT_DIR = Path("/home/barberb/HACC/Breach of Contract/outputs")


PARTIES: Dict[str, Dict[str, str]] = {
    "org:hacc": {"name": "Housing Authority of Clackamas County", "role": "public_housing_authority"},
    "person:benjamin_barber": {"name": "Benjamin Jay Barber", "role": "proposed_live_in_aide_or_functional_caregiver"},
    "person:jane_cortez": {"name": "Jane Kay Cortez", "role": "disabled_tenant_and_care_recipient"},
    "person:kati_tilton": {"name": "Kati Tilton", "role": "hacc_operations_manager"},
}


def _source(path: str, note: str = "") -> Dict[str, str]:
    payload = {"path": path}
    if note:
        payload["note"] = note
    return payload


AUTHORITIES: List[Dict[str, Any]] = [
    {
        "authority_id": "auth:24_cfr_982_316",
        "title": "24 C.F.R. § 982.316",
        "type": "regulation",
        "proposition": "PHA must approve a live-in aide if needed as a reasonable accommodation for a person with disabilities.",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-982/section-982.316",
    },
    {
        "authority_id": "auth:24_cfr_5_403",
        "title": "24 C.F.R. § 5.403",
        "type": "regulation",
        "proposition": "Defines a live-in aide as a person essential to the care and well-being of a person with disabilities, not obligated for support, and who would not live in the unit but for the supportive services.",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-5/section-5.403",
    },
    {
        "authority_id": "auth:24_cfr_5_609",
        "title": "24 C.F.R. § 5.609",
        "type": "regulation",
        "proposition": "Income of a live-in aide is excluded from annual income.",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-5/section-5.609",
    },
    {
        "authority_id": "auth:pih_2013_04",
        "title": "PIH Notice 2013-04",
        "type": "hud_notice",
        "proposition": "For fully excluded income, including income from a live-in aide, PHAs may accept self-certification and need not use the normal verification hierarchy unless further checking is needed to determine whether the exclusion applies.",
        "sourceUrl": "https://www.hud.gov/sites/documents/PIH2013-04.PDF",
    },
    {
        "authority_id": "auth:hud_4350_3",
        "title": "HUD Handbook 4350.3",
        "type": "hud_handbook",
        "proposition": "Owner must verify the need for a live-in aide, but may only verify the need to the extent necessary and may not require access to confidential medical records; the income of a live-in aide is excluded from annual income.",
        "sourceUrl": "https://www.hud.gov/sites/documents/43503hsgh.pdf",
    },
    {
        "authority_id": "auth:hacc_adminplan_2025",
        "title": "HACC Admin Plan 7/1/2025",
        "type": "local_policy",
        "proposition": "HACC states that a live-in aide's income is not counted in annual income and that live-in aides are not family members, while still requiring targeted screening and verification for the aide role.",
        "sources": [
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt"),
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/a38c7914-ea37-4c2f-a815-711d4a97c92b.txt"),
        ],
    },
    {
        "authority_id": "auth:home_forward_packet",
        "title": "Home Forward Request to Add a Live-in Aide Packet",
        "type": "regional_policy_example",
        "proposition": "A live-in aide is part of the household but not the family, and the live-in aide's income is not considered in family-income calculations, although role-related paperwork may still be requested.",
        "sources": [
            _source("/home/barberb/HACC/evidence/history/Request to Add a Live-in Aide Packet.pdf"),
        ],
    },
]


EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "ev:provider_supported_live_in_caregiver_need",
        "headline": "Record states Benjamin served as live-in caregiver / functional live-in aide",
        "kind": "accommodation_record",
        "proposition": "HACC was on notice that Benjamin was being presented as Jane's live-in caregiver or functional live-in aide.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/docs/live_in_aide_income_rule_memo.md"),
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/workspace-generated/improved-complaint-from-temporary-session.cited.md"),
        ],
    },
    {
        "evidence_id": "ev:feb_25_broad_financial_request",
        "headline": "HACC demanded tax, business, crypto, and bank records",
        "kind": "email_thread",
        "proposition": "On February 25, 2026, HACC requested 2025 tax filings for several businesses, six months of crypto statements, and all personal and business bank statements for 90 days.",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-additional-info-import/0015-Re-Additional-Information-Needed-CAMTdTS_aghRN0G5nwdnU6BxS-Jx9ZU45kOsj0EC4txrk_8oA6A-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:nerd_party_stale_entity_response",
        "headline": "Benjamin said Nerd Party was from about 10 years earlier",
        "kind": "email_thread",
        "proposition": "Benjamin responded that Nerd Party was from about 10 years earlier and that some entities did not exist long enough to file taxes, suggesting the request reached stale or defunct entities.",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-additional-info-import/0015-Re-Additional-Information-Needed-CAMTdTS_aghRN0G5nwdnU6BxS-Jx9ZU45kOsj0EC4txrk_8oA6A-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:hacc_policy_income_excluded",
        "headline": "HACC policy says live-in aide income is not counted",
        "kind": "policy_text",
        "proposition": "HACC policy text states that the income of a live-in aide is not counted in annual income and that live-in aides are not family members.",
        "sources": [
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt"),
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/texts/a38c7914-ea37-4c2f-a815-711d4a97c92b.txt"),
        ],
    },
    {
        "evidence_id": "ev:classification_gap",
        "headline": "Current record does not show a clean HACC classification decision",
        "kind": "record_gap",
        "proposition": "The present record does not yet pin down whether HACC had formally stopped treating Benjamin as a proposed live-in aide and reclassified him as an ordinary counted household member before making the broad income requests.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/docs/live_in_aide_income_audit_discovery_requests.md"),
            _source("/home/barberb/HACC/Breach of Contract/docs/live_in_aide_income_rule_memo.md"),
        ],
    },
]


EVENTS: List[Dict[str, Any]] = [
    {
        "event_id": "evt_notice_of_live_in_caregiver_role",
        "date": "2026-03-24",
        "actor_ids": ["person:benjamin_barber", "person:jane_cortez", "org:hacc"],
        "kind": "caregiver_notice",
        "summary": "Accommodation record reflected that Benjamin served as Jane's live-in caregiver or functional live-in aide.",
        "evidence_ids": ["ev:provider_supported_live_in_caregiver_need"],
    },
    {
        "event_id": "evt_hacc_broad_income_and_asset_request",
        "date": "2026-02-25",
        "actor_ids": ["person:kati_tilton", "org:hacc", "person:benjamin_barber"],
        "kind": "income_verification_request",
        "summary": "HACC requested broad tax, business, crypto, and banking records as part of the eligibility process.",
        "evidence_ids": ["ev:feb_25_broad_financial_request"],
    },
    {
        "event_id": "evt_benjamin_identifies_stale_business_requests",
        "date": "2026-02-25",
        "actor_ids": ["person:benjamin_barber", "org:hacc"],
        "kind": "response_to_request",
        "summary": "Benjamin said Nerd Party was from about 10 years earlier and that some entities did not exist long enough to file taxes.",
        "evidence_ids": ["ev:nerd_party_stale_entity_response"],
    },
    {
        "event_id": "evt_hacc_policy_treats_live_in_aide_income_as_excluded",
        "date": "2025-07-01",
        "actor_ids": ["org:hacc"],
        "kind": "policy_baseline",
        "summary": "HACC policy text states that live-in aide income is not counted and that live-in aides are not family members.",
        "evidence_ids": ["ev:hacc_policy_income_excluded"],
    },
]


OBLIGATIONS: List[Dict[str, Any]] = [
    {
        "obligation_id": "obl_hacc_must_approve_live_in_aide_if_need_verified",
        "actor": "org:hacc",
        "modality": "obligated",
        "summary": "HACC must approve a live-in aide if disability-related need is verified.",
        "authorities": ["auth:24_cfr_982_316", "auth:24_cfr_5_403", "auth:hud_4350_3"],
        "trigger_event_ids": ["evt_notice_of_live_in_caregiver_role"],
    },
    {
        "obligation_id": "obl_hacc_must_treat_true_live_in_aide_income_as_excluded",
        "actor": "org:hacc",
        "modality": "obligated",
        "summary": "If Benjamin was a true live-in aide, HACC had to treat his income as excluded from annual income.",
        "authorities": ["auth:24_cfr_5_609", "auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "trigger_event_ids": ["evt_notice_of_live_in_caregiver_role", "evt_hacc_policy_treats_live_in_aide_income_as_excluded"],
    },
    {
        "obligation_id": "obl_hacc_may_request_targeted_live_in_aide_screening_materials",
        "actor": "org:hacc",
        "modality": "permitted",
        "summary": "HACC may request targeted material needed to determine whether a person qualifies as a live-in aide and to complete role-related screening.",
        "authorities": ["auth:24_cfr_982_316", "auth:hud_4350_3", "auth:hacc_adminplan_2025"],
        "trigger_event_ids": ["evt_notice_of_live_in_caregiver_role"],
    },
    {
        "obligation_id": "obl_hacc_must_not_use_fully_excluded_income_rules_to_force_normal_verification_hierarchy_without_reason",
        "actor": "org:hacc",
        "modality": "forbidden",
        "summary": "HACC should not force the normal verification hierarchy for fully excluded live-in-aide income without a specific reason to test whether the exclusion applies.",
        "authorities": ["auth:pih_2013_04", "auth:24_cfr_5_609"],
        "trigger_event_ids": ["evt_notice_of_live_in_caregiver_role", "evt_hacc_broad_income_and_asset_request"],
    },
    {
        "obligation_id": "obl_hacc_must_not_demand_stale_or_unrelated_business_records_if_live_in_aide_income_is_excluded",
        "actor": "org:hacc",
        "modality": "forbidden",
        "summary": "If Benjamin was being treated as a live-in aide, HACC should not have demanded stale or unrelated business records that did not bear on current counted family income or live-in-aide status.",
        "authorities": ["auth:pih_2013_04", "auth:hacc_adminplan_2025", "auth:home_forward_packet"],
        "trigger_event_ids": ["evt_hacc_broad_income_and_asset_request", "evt_benjamin_identifies_stale_business_requests"],
    },
    {
        "obligation_id": "obl_hacc_must_tailor_requests_to_role_and_issue",
        "actor": "org:hacc",
        "modality": "obligated",
        "summary": "HACC had to tailor its requests to the live-in-aide role question rather than auditing Benjamin as an ordinary counted household member without a shown reclassification basis.",
        "authorities": ["auth:hud_4350_3", "auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "trigger_event_ids": ["evt_hacc_broad_income_and_asset_request"],
    },
    {
        "obligation_id": "obl_benjamin_may_self_certify_fully_excluded_live_in_aide_income",
        "actor": "person:benjamin_barber",
        "modality": "permitted",
        "summary": "Benjamin may rely on self-certification for fully excluded live-in-aide income unless HACC has a specific reason to question whether the exclusion applies.",
        "authorities": ["auth:pih_2013_04"],
        "trigger_event_ids": ["evt_hacc_broad_income_and_asset_request"],
    },
    {
        "obligation_id": "obl_benjamin_must_provide_targeted_live_in_aide_screening_materials_if_requested",
        "actor": "person:benjamin_barber",
        "modality": "conditional",
        "summary": "Benjamin had a conditional duty to provide targeted screening and qualification material if HACC was genuinely evaluating live-in-aide status.",
        "authorities": ["auth:hud_4350_3", "auth:hacc_adminplan_2025"],
        "trigger_event_ids": ["evt_notice_of_live_in_caregiver_role"],
    },
]


PARTY_DEONTIC_PROFILES: List[Dict[str, Any]] = [
    {
        "party_id": "org:hacc",
        "classification": "primary_public_housing_decision_maker",
        "directDutyStatus": "primary_duty_bearer",
        "related_obligation_ids": [
            "obl_hacc_must_approve_live_in_aide_if_need_verified",
            "obl_hacc_must_treat_true_live_in_aide_income_as_excluded",
            "obl_hacc_may_request_targeted_live_in_aide_screening_materials",
            "obl_hacc_must_not_use_fully_excluded_income_rules_to_force_normal_verification_hierarchy_without_reason",
            "obl_hacc_must_not_demand_stale_or_unrelated_business_records_if_live_in_aide_income_is_excluded",
            "obl_hacc_must_tailor_requests_to_role_and_issue",
        ],
    },
    {
        "party_id": "person:benjamin_barber",
        "classification": "proposed_live_in_aide_and_reporting_actor",
        "directDutyStatus": "rights_holder_and_conditional_information_provider",
        "related_obligation_ids": [
            "obl_benjamin_may_self_certify_fully_excluded_live_in_aide_income",
            "obl_benjamin_must_provide_targeted_live_in_aide_screening_materials_if_requested",
        ],
    },
    {
        "party_id": "person:jane_cortez",
        "classification": "disabled_tenant_and_care_recipient",
        "directDutyStatus": "beneficiary_of_live_in_aide_accommodation_rules",
        "related_obligation_ids": [
            "obl_hacc_must_approve_live_in_aide_if_need_verified",
            "obl_hacc_must_treat_true_live_in_aide_income_as_excluded",
        ],
    },
    {
        "party_id": "person:kati_tilton",
        "classification": "hacc_agent_who_sent_document_request",
        "directDutyStatus": "derivative_implementation_actor",
        "related_obligation_ids": [
            "obl_hacc_must_tailor_requests_to_role_and_issue",
            "obl_hacc_must_not_demand_stale_or_unrelated_business_records_if_live_in_aide_income_is_excluded",
        ],
    },
]


FINDINGS: List[Dict[str, Any]] = [
    {
        "finding_id": "finding_live_in_aide_exclusion_rule_clear",
        "subject": "HACC and Benjamin",
        "headline": "Live-in-aide income exclusion rule is clear",
        "status": "supported",
        "confidence": "high",
        "summary": "Federal and local materials align that a true live-in aide's income is excluded from annual income.",
        "authority_ids": ["auth:24_cfr_5_609", "auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "evidence_ids": ["ev:hacc_policy_income_excluded"],
    },
    {
        "finding_id": "finding_targeted_screening_but_not_full_income_audit",
        "subject": "HACC",
        "headline": "Targeted screening is allowed, but that is different from a generalized income audit",
        "status": "supported",
        "confidence": "medium_high",
        "summary": "The authorities permit targeted live-in-aide qualification and screening review, not an automatic ordinary-family-income audit.",
        "authority_ids": ["auth:24_cfr_982_316", "auth:hud_4350_3", "auth:hacc_adminplan_2025"],
        "evidence_ids": ["ev:provider_supported_live_in_caregiver_need", "ev:hacc_policy_income_excluded"],
    },
    {
        "finding_id": "finding_feb_25_request_looks_overbroad_if_live_in_aide_status_applies",
        "subject": "HACC",
        "headline": "February 25, 2026 request looks overbroad if live-in-aide status applies",
        "status": "supported_but_conditional",
        "confidence": "medium_high",
        "summary": "The broad request for business, crypto, and bank records appears more like an ordinary household income audit than a targeted live-in-aide review, especially given the stale Nerd Party request.",
        "authority_ids": ["auth:pih_2013_04", "auth:hacc_adminplan_2025", "auth:home_forward_packet"],
        "evidence_ids": ["ev:feb_25_broad_financial_request", "ev:nerd_party_stale_entity_response"],
    },
    {
        "finding_id": "finding_classification_gap_prevents_final_liability_conclusion",
        "subject": "HACC",
        "headline": "Classification gap remains the main limiter",
        "status": "unresolved",
        "confidence": "medium",
        "summary": "The current record does not yet show whether HACC had a legitimate classification basis to stop treating Benjamin as a live-in aide and instead count him as a regular household member.",
        "authority_ids": ["auth:hacc_adminplan_2025", "auth:pih_2013_04"],
        "evidence_ids": ["ev:classification_gap"],
    },
]


def _build_actor_deontic_matrix() -> List[Dict[str, Any]]:
    actors = list(PARTIES.keys())
    rows: List[Dict[str, Any]] = []
    for actor in actors:
        row = {
            "actor": actor,
            "actorName": PARTIES[actor]["name"],
            "role": PARTIES[actor]["role"],
            "obligated": [],
            "forbidden": [],
            "permitted": [],
            "restrained": [],
            "conditional": [],
        }
        for item in OBLIGATIONS:
            if item["actor"] != actor:
                continue
            entry = {
                "obligationId": item["obligation_id"],
                "summary": item["summary"],
                "authorities": item["authorities"],
            }
            modality = item["modality"]
            if modality == "obligated":
                row["obligated"].append(entry)
            elif modality == "forbidden":
                row["forbidden"].append(entry)
            elif modality == "permitted":
                row["permitted"].append(entry)
            elif modality == "conditional":
                row["conditional"].append(entry)
            else:
                row["restrained"].append(entry)
        rows.append(row)
    return rows


def _build_knowledge_graph() -> Dict[str, Any]:
    nodes: Dict[str, Dict[str, Any]] = {}
    edges: List[Dict[str, str]] = []
    for party_id, spec in PARTIES.items():
        nodes[party_id] = {"type": "party", "label": spec["name"], "role": spec["role"]}
    for event in EVENTS:
        nodes[event["event_id"]] = {
            "type": "event",
            "label": event["summary"],
            "date": event["date"],
            "kind": event["kind"],
            "evidenceIds": event["evidence_ids"],
        }
        for actor_id in event["actor_ids"]:
            edges.append({"from": actor_id, "to": event["event_id"], "type": "participated_in"})
        for evidence_id in event["evidence_ids"]:
            edges.append({"from": event["event_id"], "to": evidence_id, "type": "supported_by"})
    for evidence in EVIDENCE:
        nodes[evidence["evidence_id"]] = {
            "type": "evidence",
            "label": evidence["headline"],
            "kind": evidence["kind"],
        }
    for finding in FINDINGS:
        nodes[finding["finding_id"]] = {
            "type": "finding",
            "label": finding["headline"],
            "status": finding["status"],
        }
        for evidence_id in finding["evidence_ids"]:
            edges.append({"from": evidence_id, "to": finding["finding_id"], "type": "supports"})
        for authority_id in finding["authority_ids"]:
            edges.append({"from": authority_id, "to": finding["finding_id"], "type": "grounds"})
    for authority in AUTHORITIES:
        nodes[authority["authority_id"]] = {
            "type": "authority",
            "label": authority["title"],
            "authorityType": authority["type"],
        }
    for obligation in OBLIGATIONS:
        nodes[obligation["obligation_id"]] = {
            "type": "obligation",
            "label": obligation["summary"],
            "modality": obligation["modality"],
            "actor": obligation["actor"],
        }
        edges.append({"from": obligation["actor"], "to": obligation["obligation_id"], "type": "bears"})
        for authority_id in obligation["authorities"]:
            edges.append({"from": authority_id, "to": obligation["obligation_id"], "type": "grounds"})
        for event_id in obligation["trigger_event_ids"]:
            edges.append({"from": event_id, "to": obligation["obligation_id"], "type": "triggers"})
    return {
        "branch": "live_in_aide_income_review",
        "nodes": nodes,
        "edges": edges,
    }


DEPENDENCY_NODES: Dict[str, Dict[str, Any]] = {
    "live_in_aide_role_definition_controls": {
        "label": "Live-in aide role definition controls who qualifies for the exclusion",
        "authorities": ["auth:24_cfr_5_403", "auth:24_cfr_982_316"],
        "evidence": ["ev:provider_supported_live_in_caregiver_need"],
    },
    "true_live_in_aide_income_is_excluded": {
        "label": "True live-in aide income is excluded from annual income",
        "authorities": ["auth:24_cfr_5_609", "auth:hacc_adminplan_2025"],
        "evidence": ["ev:hacc_policy_income_excluded"],
    },
    "fully_excluded_income_may_be_self_certified": {
        "label": "Fully excluded income may be self-certified absent a specific reason for further checking",
        "authorities": ["auth:pih_2013_04"],
        "evidence": ["ev:hacc_policy_income_excluded"],
    },
    "pha_may_request_targeted_screening_only": {
        "label": "PHA may request targeted role-related screening and qualification materials",
        "authorities": ["auth:hud_4350_3", "auth:hacc_adminplan_2025", "auth:24_cfr_982_316"],
        "evidence": ["ev:provider_supported_live_in_caregiver_need"],
    },
    "broad_financial_audit_requires_non_aide_theory_or_specific_basis": {
        "label": "Broad financial auditing requires either a non-aide classification or a specific reason to doubt the exclusion",
        "authorities": ["auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "evidence": ["ev:feb_25_broad_financial_request", "ev:classification_gap"],
    },
    "stale_nerd_party_request_is_overbreadth_signal": {
        "label": "Request for Nerd Party and other stale entities is an overbreadth signal",
        "authorities": ["auth:pih_2013_04", "auth:home_forward_packet"],
        "evidence": ["ev:nerd_party_stale_entity_response", "ev:feb_25_broad_financial_request"],
    },
    "classification_gap_limits_final_fault_conclusion": {
        "label": "Classification gap limits the final liability conclusion",
        "authorities": ["auth:hacc_adminplan_2025", "auth:pih_2013_04"],
        "evidence": ["ev:classification_gap"],
    },
    "hacc_overbreadth_theory_supported_conditionally": {
        "label": "HACC overbreadth theory is conditionally supported",
        "authorities": ["auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "evidence": ["ev:feb_25_broad_financial_request", "ev:nerd_party_stale_entity_response", "ev:classification_gap"],
    },
    "false_positive_control": {
        "label": "Do not conclude full liability without resolving how HACC classified Benjamin",
        "authorities": ["auth:pih_2013_04", "auth:hacc_adminplan_2025"],
        "evidence": ["ev:classification_gap"],
    },
}


DEPENDENCY_EDGES: List[List[str]] = [
    ["live_in_aide_role_definition_controls", "true_live_in_aide_income_is_excluded"],
    ["true_live_in_aide_income_is_excluded", "fully_excluded_income_may_be_self_certified"],
    ["live_in_aide_role_definition_controls", "pha_may_request_targeted_screening_only"],
    ["true_live_in_aide_income_is_excluded", "broad_financial_audit_requires_non_aide_theory_or_specific_basis"],
    ["fully_excluded_income_may_be_self_certified", "broad_financial_audit_requires_non_aide_theory_or_specific_basis"],
    ["broad_financial_audit_requires_non_aide_theory_or_specific_basis", "stale_nerd_party_request_is_overbreadth_signal"],
    ["stale_nerd_party_request_is_overbreadth_signal", "hacc_overbreadth_theory_supported_conditionally"],
    ["classification_gap_limits_final_fault_conclusion", "false_positive_control"],
    ["classification_gap_limits_final_fault_conclusion", "hacc_overbreadth_theory_supported_conditionally", "defeater"],
]


def _build_dependency_graph() -> Dict[str, Any]:
    edges = []
    for entry in DEPENDENCY_EDGES:
        if len(entry) == 2:
            src, dst = entry
            kind = "supports"
        else:
            src, dst, kind = entry
        edges.append({"from": src, "to": dst, "type": kind})
    return {
        "branch": "live_in_aide_income_review",
        "activeOutcome": "hacc_overbreadth_theory_supported_conditionally",
        "nodes": DEPENDENCY_NODES,
        "edges": edges,
    }


def _build_dependency_citations(graph: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "branch": graph["branch"],
        "nodeCitations": {
            node_id: {
                "authorities": spec["authorities"],
                "evidence": spec["evidence"],
            }
            for node_id, spec in graph["nodes"].items()
        },
    }


def _build_formal_models() -> Dict[str, Any]:
    dfol = {
        "partyUniverse": list(PARTIES.keys()),
        "obligationFormulas": [
            {
                "id": item["obligation_id"],
                "actor": item["actor"],
                "modality": item["modality"],
                "formula": f"{item['modality'].upper()}({item['actor']}, {item['obligation_id']})",
            }
            for item in OBLIGATIONS
        ],
    }
    dcec = {
        "happens": [
            f"happens({event['event_id']}, '{event['date']}')" for event in EVENTS
        ],
        "initiates": [
            {
                "id": item["obligation_id"],
                "formula": f"initiates({item['trigger_event_ids'][0]}, {item['obligation_id']}, t_{index + 1})",
            }
            for index, item in enumerate(OBLIGATIONS)
            if item["trigger_event_ids"]
        ],
        "holdsAt": [
            {
                "id": item["obligation_id"],
                "formula": f"holdsAt({item['obligation_id']}, t_{index + 1})",
            }
            for index, item in enumerate(OBLIGATIONS)
        ],
        "breaches": [
            {
                "id": "br:feb_25_overbreadth_if_excluded_income",
                "formula": "breach(obl_hacc_must_not_demand_stale_or_unrelated_business_records_if_live_in_aide_income_is_excluded, evt_hacc_broad_income_and_asset_request)",
            }
        ],
    }
    return {
        "deonticFirstOrderLogic": dfol,
        "deonticCognitiveEventCalculus": dcec,
        "tdfol": {},
    }


def _normalize_token(raw: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in raw).strip("_").lower()


def _build_flogic_export(events: List[Dict[str, Any]], obligations: List[Dict[str, Any]], findings: List[Dict[str, Any]]) -> str:
    lines = [
        "%% live_in_aide_income_case_knowledge_graph.flogic",
        "%% F-logic export for the HACC live-in aide income verification record",
        "",
    ]
    for party_id, spec in PARTIES.items():
        token = _normalize_token(party_id)
        lines.append(f"{token}:party[")
        lines.append(f"  name -> \"{spec['name']}\";")
        lines.append(f"  role -> \"{spec['role']}\"")
        lines.append("].")
    lines.append("")
    for event in events:
        token = _normalize_token(event["event_id"])
        lines.append(f"{token}:event[")
        lines.append(f"  date -> \"{event['date']}\";")
        lines.append(f"  kind -> \"{event['kind']}\";")
        lines.append(f"  summary -> \"{event['summary']}\"")
        lines.append("].")
    lines.append("")
    for obligation in obligations:
        token = _normalize_token(obligation["obligation_id"])
        lines.append(f"{token}:obligation[")
        lines.append(f"  actor -> \"{obligation['actor']}\";")
        lines.append(f"  modality -> \"{obligation['modality']}\";")
        lines.append(f"  summary -> \"{obligation['summary']}\"")
        lines.append("].")
    lines.append("")
    for finding in findings:
        token = _normalize_token(finding["finding_id"])
        lines.append(f"{token}:finding[")
        lines.append(f"  status -> \"{finding['status']}\";")
        lines.append(f"  headline -> \"{finding['headline']}\"")
        lines.append("].")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_dcec_export(formal_models: Dict[str, Any]) -> str:
    dcec = formal_models["deonticCognitiveEventCalculus"]
    lines = [
        "% live_in_aide_income_case_obligations_dcec.pl",
        "% DCEC-style export for the HACC live-in aide income verification issue",
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
        "approve_live_in_aide_if_need_verified": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ApproveLiveInAideIfNeedVerified", ())),
        "exclude_true_live_in_aide_income": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ExcludeTrueLiveInAideIncome", ())),
        "targeted_screening_permitted": DeonticFormula(DeonticOperator.PERMISSION, Predicate("RequestTargetedLiveInAideScreening", ())),
        "normal_verification_hierarchy_not_required_for_excluded_income": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("ForceNormalVerificationHierarchyForExcludedLiveInAideIncomeWithoutSpecificReason", ())),
        "stale_unrelated_records_forbidden_if_excluded_income": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("DemandStaleOrUnrelatedBusinessRecordsIfIncomeExcluded", ())),
        "requests_must_be_tailored": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("TailorRequestsToLiveInAideRoleQuestion", ())),
        "benjamin_self_certification_permitted": DeonticFormula(DeonticOperator.PERMISSION, Predicate("BenjaminSelfCertifyFullyExcludedIncome", ())),
    }
    for formula in axioms.values():
        kb.add_axiom(formula)

    queries = {
        "approve_live_in_aide_if_need_verified": axioms["approve_live_in_aide_if_need_verified"],
        "exclude_true_live_in_aide_income": axioms["exclude_true_live_in_aide_income"],
        "targeted_screening_permitted": axioms["targeted_screening_permitted"],
        "normal_verification_hierarchy_not_required_for_excluded_income": axioms["normal_verification_hierarchy_not_required_for_excluded_income"],
        "stale_unrelated_records_forbidden_if_excluded_income": axioms["stale_unrelated_records_forbidden_if_excluded_income"],
        "requests_must_be_tailored": axioms["requests_must_be_tailored"],
        "benjamin_self_certification_permitted": axioms["benjamin_self_certification_permitted"],
        "nerd_party_request_was_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("DemandNerdPartyRecords", ())),
        "hacc_reclassified_benjamin_before_request": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("HaccReclassifiedBenjaminAsOrdinaryCountedMemberBeforeRequest", ())),
    }

    proofs = []
    for label, formula in queries.items():
        result = strategy._prove_basic_modal(formula, kb, timeout_ms=5000, start_time=0)
        proofs.append(
            {
                "label": label,
                "formula": formula.to_string(),
                "status": result.status.value,
                "method": "ModalTableauxStrategy._prove_basic_modal",
                "proofSteps": [step.justification for step in result.proof_steps],
            }
        )
    return {
        "available": True,
        "engine": "ipfs_datasets_py.logic.TDFOL modal tableaux",
        "proofs": proofs,
        "note": "The prover validates the encoded normative model. It does not resolve the disputed historical classification decision by itself.",
    }


def _build_grounding_audit(report: Dict[str, Any]) -> Dict[str, Any]:
    dependency_audit = []
    for node_id, spec in report["dependencyGraph"]["nodes"].items():
        grounding = "strong"
        if "gap" in node_id or "limits" in node_id:
            grounding = "weak_record"
        dependency_audit.append(
            {
                "nodeId": node_id,
                "grounding": grounding,
                "authorities": spec["authorities"],
                "evidence": spec["evidence"],
            }
        )
    return {
        "purpose": "Grounding audit for live-in-aide income knowledge and dependency graphs",
        "dependencyNodeAudit": dependency_audit,
        "recordStrengtheningTasks": [
            {
                "taskId": "task_pin_down_hacc_classification_of_benjamin",
                "summary": "Locate any HACC note, code, add-person packet, or internal decision showing whether Benjamin was classified as a live-in aide, family member, or other category before February 25, 2026.",
            },
            {
                "taskId": "task_prove_if_benjamin_income_was_actually_counted",
                "summary": "Obtain rent-calculation worksheets, subsidy calculations, or family-composition forms showing whether Benjamin's income was actually included in annual-income calculations.",
            },
            {
                "taskId": "task_identify_reason_for_nerd_party_request",
                "summary": "Seek internal notes or testimony explaining why HACC thought Nerd Party and other stale entities were relevant to any current eligibility or income calculation.",
            },
            {
                "taskId": "task_link_document_request_to_delay_or_denial",
                "summary": "Pin down whether voucher issuance, relocation processing, or accommodation review was delayed while HACC waited for the disputed business and banking records.",
            },
        ],
    }


def build_case_report() -> Dict[str, Any]:
    actor_matrix = _build_actor_deontic_matrix()
    knowledge_graph = _build_knowledge_graph()
    dependency_graph = _build_dependency_graph()
    formal_models = _build_formal_models()
    proof_audit = _run_tdfol_audit()
    formal_models["tdfol"]["proofAudit"] = proof_audit
    report = {
        "metadata": {
            "generatedAt": CURRENT_DATE.isoformat(),
            "caseId": "live_in_aide_income_review",
            "scope": "Formal analysis of live-in aide income verification and overbreadth issues in the HACC record",
            "disclaimer": "Research artifact for issue-spotting and formal analysis. Not legal advice.",
        },
        "parties": PARTIES,
        "authorities": AUTHORITIES,
        "evidence": EVIDENCE,
        "events": EVENTS,
        "obligations": OBLIGATIONS,
        "partyDeonticProfiles": PARTY_DEONTIC_PROFILES,
        "actorDeonticMatrix": actor_matrix,
        "findings": FINDINGS,
        "knowledgeGraph": knowledge_graph,
        "dependencyGraph": dependency_graph,
        "formalModels": formal_models,
    }
    report["groundingAudit"] = _build_grounding_audit(report)
    return report


def _build_markdown_summary(report: Dict[str, Any]) -> str:
    lines = [
        "# Live-In Aide Income Formal Analysis Summary",
        "",
        "## Bottom line",
        "",
        "- A true live-in aide's income is excluded from annual income under both HUD and HACC policy materials.",
        "- HACC may request targeted live-in-aide qualification and screening materials.",
        "- The February 25, 2026 request for multiple business filings, crypto records, and broad bank statements looks overbroad if Benjamin was still being treated as a live-in aide.",
        "- The main remaining limiter is the classification gap: the current record does not yet show whether HACC had formally reclassified Benjamin as an ordinary counted household member before making that request.",
        "",
        "## Formal findings",
        "",
    ]
    for finding in report["findings"]:
        lines.append(f"- `{finding['subject']}`: **{finding['headline']}** (`{finding['status']}`, confidence `{finding['confidence']}`)")
    lines.extend([
        "",
        "## Actor deontic matrix",
        "",
    ])
    for row in report["actorDeonticMatrix"]:
        lines.append(
            f"- `{row['actor']}`: O={len(row['obligated'])} F={len(row['forbidden'])} P={len(row['permitted'])} C={len(row['conditional'])}"
        )
    lines.extend([
        "",
        "## Prover audit",
        "",
        f"- Prover available: `{report['formalModels']['tdfol']['proofAudit']['available']}`",
    ])
    if report["formalModels"]["tdfol"]["proofAudit"]["available"]:
        for proof in report["formalModels"]["tdfol"]["proofAudit"]["proofs"]:
            lines.append(f"- `{proof['label']}` -> `{proof['status']}`")
    lines.extend([
        "",
        "## Generated artifacts",
        "",
        "- `live_in_aide_income_case_report.json`",
        "- `live_in_aide_income_case_report.md`",
        "- `live_in_aide_income_knowledge_graph.json`",
        "- `live_in_aide_income_dependency_graph.json`",
        "- `live_in_aide_income_dependency_citations.jsonld`",
        "- `live_in_aide_income_grounding_audit.json`",
        "- `live_in_aide_income_case_knowledge_graph.flogic`",
        "- `live_in_aide_income_case_obligations_dcec.pl`",
        "- `live_in_aide_income_tdfol_proof_audit.json`",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
    report = report or build_case_report()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "report_json": OUTPUT_DIR / "live_in_aide_income_case_report.json",
        "report_md": OUTPUT_DIR / "live_in_aide_income_case_report.md",
        "knowledge_graph": OUTPUT_DIR / "live_in_aide_income_knowledge_graph.json",
        "dependency_graph": OUTPUT_DIR / "live_in_aide_income_dependency_graph.json",
        "dependency_citations": OUTPUT_DIR / "live_in_aide_income_dependency_citations.jsonld",
        "grounding_audit_json": OUTPUT_DIR / "live_in_aide_income_grounding_audit.json",
        "flogic": OUTPUT_DIR / "live_in_aide_income_case_knowledge_graph.flogic",
        "dcec": OUTPUT_DIR / "live_in_aide_income_case_obligations_dcec.pl",
        "tdfol_audit": OUTPUT_DIR / "live_in_aide_income_tdfol_proof_audit.json",
    }
    paths["report_json"].write_text(json.dumps(report, indent=2) + "\n")
    paths["report_md"].write_text(_build_markdown_summary(report))
    paths["knowledge_graph"].write_text(json.dumps(report["knowledgeGraph"], indent=2) + "\n")
    paths["dependency_graph"].write_text(json.dumps(report["dependencyGraph"], indent=2) + "\n")
    paths["dependency_citations"].write_text(json.dumps(_build_dependency_citations(report["dependencyGraph"]), indent=2) + "\n")
    paths["grounding_audit_json"].write_text(json.dumps(report["groundingAudit"], indent=2) + "\n")
    paths["flogic"].write_text(_build_flogic_export(report["events"], report["obligations"], report["findings"]))
    paths["dcec"].write_text(_build_dcec_export(report["formalModels"]))
    paths["tdfol_audit"].write_text(json.dumps(report["formalModels"]["tdfol"]["proofAudit"], indent=2) + "\n")
    return paths


def main() -> int:
    paths = write_outputs()
    for path in paths.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
