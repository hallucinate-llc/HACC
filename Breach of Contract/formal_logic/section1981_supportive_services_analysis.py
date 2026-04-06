"""
Formal analysis for 42 U.S.C. § 1981 / supportive-services / cherry-picking / lemon-dropping issues.

This module produces:
- a grounded case report,
- a fact knowledge graph,
- a dependency graph of the governing law,
- F-logic and DCEC-style exports, and
- a short audit identifying where the record is strong or weak.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any, Dict, List


CURRENT_DATE = date(2026, 4, 5)
OUTPUT_DIR = Path("/home/barberb/HACC/Breach of Contract/outputs")


def _source(path: str, note: str = "") -> Dict[str, str]:
    payload = {"path": path}
    if note:
        payload["note"] = note
    return payload


PARTIES: Dict[str, Dict[str, str]] = {
    "org:hacc": {"name": "Housing Authority of Clackamas County", "role": "public_housing_authority"},
    "org:quantum": {"name": "Quantum Residential", "role": "property_manager_or_private_housing_actor"},
    "org:metro_shs": {"name": "Metro SHS / RLRA program environment", "role": "regional_supportive_housing_services_funder_framework"},
    "org:blossom": {"name": "Blossom housing path / project", "role": "housing_opportunity_pipeline"},
    "person:benjamin_barber": {"name": "Benjamin Barber", "role": "applicant_and_complainant"},
    "person:jane_cortez": {"name": "Jane Cortez", "role": "applicant_and_displaced_tenant"},
    "person:kati_tilton": {"name": "Kati Tilton", "role": "hacc_operations_manager"},
    "person:ashley_ferron": {"name": "Ashley Ferron", "role": "hacc_housing_resource_staff"},
}


AUTHORITIES: List[Dict[str, Any]] = [
    {
        "authority_id": "auth:42_usc_1981",
        "title": "42 U.S.C. § 1981",
        "type": "statute",
        "proposition": "All persons shall have the same right to make and enforce contracts as is enjoyed by white citizens; make and enforce contracts includes the making, performance, modification, termination, and enjoyment of all benefits, privileges, terms, and conditions of the contractual relationship.",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1981&num=0&edition=prelim",
    },
    {
        "authority_id": "auth:comcast_2020",
        "title": "Comcast Corp. v. NAAAOM, 589 U.S. 327 (2020)",
        "type": "supreme_court_case",
        "proposition": "A § 1981 plaintiff bears the burden of showing that race was a but-for cause of the injury.",
        "sourceUrl": "https://www.supremecourt.gov/opinions/19pdf/589us2r18_097c.pdf",
    },
    {
        "authority_id": "auth:dominos_2006",
        "title": "Domino's Pizza, Inc. v. McDonald, 546 U.S. 470 (2006)",
        "type": "supreme_court_case",
        "proposition": "A § 1981 plaintiff must identify an impaired contractual relationship under which the plaintiff has rights; the statute protects the plaintiff's own right to contract, not someone else's contract in the abstract.",
        "sourceUrl": "https://supreme.justia.com/cases/federal/us/546/470/",
    },
    {
        "authority_id": "auth:runyon_1976",
        "title": "Runyon v. McCrary, 427 U.S. 160 (1976)",
        "type": "supreme_court_case",
        "proposition": "Section 1981 reaches private discrimination in the making and enforcement of contracts.",
        "sourceUrl": "https://supreme.justia.com/cases/federal/us/427/160/",
    },
    {
        "authority_id": "auth:jett_1989",
        "title": "Jett v. Dallas Independent School District, 491 U.S. 701 (1989)",
        "type": "supreme_court_case",
        "proposition": "For state actors, § 1983 is generally the exclusive federal damages remedy for violation of rights secured by § 1981.",
        "sourceUrl": "https://www.govinfo.gov/content/pkg/USREPORTS-491/pdf/USREPORTS-491-701.pdf",
    },
    {
        "authority_id": "auth:42_usc_1983",
        "title": "42 U.S.C. § 1983",
        "type": "statute",
        "proposition": "A person acting under color of state law who deprives another of federal rights may be liable under § 1983.",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title42-section1983&num=0&edition=prelim",
    },
    {
        "authority_id": "auth:affh_24cfr",
        "title": "HUD AFFH framework / 24 C.F.R. §§ 5.150-5.180 and related certifications",
        "type": "regulatory_framework",
        "proposition": "Program participants certify they will take meaningful actions to further fair housing and may adopt planning and monitoring frameworks addressing segregation, disparities in opportunity, and disproportionate housing needs.",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/subtitle-A/part-5/subpart-A",
    },
]


EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "ev:shs_public_outcome_goal_exact_quote",
        "headline": "Public SHS documents contain the exact quote about providing housing and services to BIPOC at higher rates than representation",
        "kind": "public_policy_text",
        "proposition": "Public Clackamas County / HACC SHS documents say: Advance housing equity by providing access to services and housing to Black, Indigenous and people of color at higher rates than their representation among those experiencing homelessness.",
        "sources": [
            _source("https://dochub.clackamas.us/documents/drupal/ed77538a-1d00-45f2-b95b-9aecca79e5f3", "Clackamas County HCDD SHS document; exact quote appears on page 5 in the public document."),
            _source("https://dochub.clackamas.us/documents/drupal/cb82a322-0394-479e-a4e5-2eca891e9b98", "HACC SHS contract / scope-of-work document; exact quote appears on page 10 in the public document."),
            _source("https://dochub.clackamas.us/documents/drupal/5f774a98-6539-473a-b098-470323b34f11", "Additional HACC-linked SHS document containing the same outcome-goal language."),
        ],
    },
    {
        "evidence_id": "ev:shs_cropped_screenshot_preserved",
        "headline": "The exact SHS outcome-goal sentence was preserved in a cropped screenshot used in the complaint packet",
        "kind": "preserved_screenshot",
        "proposition": "The workspace contains a preserved screenshot highlighting the SHS sentence about providing access to services and housing to Black, Indigenous and people of color at higher rates than their representation among those experiencing homelessness.",
        "sources": [
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.shs-race-goal.png", "Preserved cropped screenshot."),
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.exhibit-map.md", "Exhibit S description."),
        ],
    },
    {
        "evidence_id": "ev:shs_race_equity_policy_language",
        "headline": "RLRA / SHS policy says program is rooted in racial equity and BIPOC-focused outcomes",
        "kind": "policy_text",
        "proposition": "The RLRA program states it is rooted in a commitment to lead with racial equity by especially meeting the needs of Black, Indigenous and people of color, using equity criteria and disaggregated data to ensure racially equitable outcomes.",
        "sources": [
            _source("/home/barberb/HACC/workspace/evidence/did-key-hacc-temp-session/local-import/0001_945af141-c7d1-4973-88c0-b57024243114.txt/945af141-c7d1-4973-88c0-b57024243114.txt", "Regional Long-term Rent Assistance Program Policies, updated 1/23/25."),
        ],
    },
    {
        "evidence_id": "ev:shs_equitable_referral_pathways",
        "headline": "RLRA policy ties referral pathways to housing options and supportive services",
        "kind": "policy_text",
        "proposition": "The RLRA policy says counties are accountable for ensuring referral pathways are equitable, inclusive, and effective at connecting eligible participants with appropriate housing options and supportive services.",
        "sources": [
            _source("/home/barberb/HACC/workspace/evidence/did-key-hacc-temp-session/local-import/0001_945af141-c7d1-4973-88c0-b57024243114.txt/945af141-c7d1-4973-88c0-b57024243114.txt", "RLRA tenant referral section."),
        ],
    },
    {
        "evidence_id": "ev:hacc_afh_racial_equity_lens_for_forms_and_letters",
        "headline": "Clackamas County and HACC AFH required a racial-equity lens for housing forms, letters, and internal practices",
        "kind": "official_planning_text",
        "proposition": "The Clackamas County / HACC Assessment of Fair Housing states that internal policies and practices should be reviewed with a trauma-informed, accessibility, and racial equity lens, that HACC forms and letters should be racially equitable and accessible, and that housing stability outcomes for Black, Indigenous and People of Color should be monitored.",
        "sources": [
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/embeddings/hacc_text_chunks.records.jsonl", "Chunks 5, 6, 16, 17, and 172 preserve the AFH language."),
            _source("https://www.clackamas.us/communitydevelopment/maps.html", "County planning page linking the AFH."),
        ],
    },
    {
        "evidence_id": "ev:hacc_afh_bipoc_outreach_waitlist",
        "headline": "HACC AFH says waitlist opening focused on BIPOC outreach",
        "kind": "official_planning_text",
        "proposition": "The Clackamas County / HACC AFH states that HACC last opened its waitlists in June 2020 with a focus on BIPOC outreach, including BIPOC media outlets and partner agencies working directly with BIPOC populations.",
        "sources": [
            _source("/home/barberb/HACC/workspace/migrated_sources/hacc_website/knowledge_graph/embeddings/hacc_text_chunks.records.jsonl", "Chunks 100, 101, 113, and 114 preserve the AFH outreach language."),
        ],
    },
    {
        "evidence_id": "ev:ohcs_hb2100_racial_disparities_task_force",
        "headline": "OHCS and the Oregon Housing Stability Council were tasked with modifying funding and contracting methods to address racial disparities",
        "kind": "state_policy_text",
        "proposition": "OHCS states that House Bill 2100 directed OHCS to establish a task force investigating methods by which the state, OHCS, and the Oregon Housing Stability Council may change funding structures, contracting processes, eligibility, and service delivery to address racial disparities among people experiencing homelessness and housing insecurity.",
        "sources": [
            _source("https://www.oregon.gov/ohcs/get-involved/pages/hb-2100-task-force.aspx", "OHCS task force page."),
        ],
    },
    {
        "evidence_id": "ev:ohcs_ori_racial_disparities_and_set_asides",
        "headline": "OHCS Oregon Rehousing Initiative tied homelessness programs to racial-disparity reduction and culturally responsive set-asides",
        "kind": "state_policy_text",
        "proposition": "OHCS states that the Oregon Rehousing Initiative and Housing 360 pilot seek to reduce racial disparities in housing outcomes and included a 25 percent set-aside for direct awards to culturally responsive organizations.",
        "sources": [
            _source("https://www.oregon.gov/ohcs/homelessness-response/Pages/oregon-rehousing-initiative.aspx", "OHCS Oregon Rehousing Initiative page."),
        ],
    },
    {
        "evidence_id": "ev:quantum_received_blossom_packet",
        "headline": "HACC said Quantum staff received the intake packet but did not provide it to HACC",
        "kind": "email_statement",
        "proposition": "Ashley Ferron wrote that the intake packet was submitted to Quantum staff at the Hillside Manor office but was not provided to HACC, and asked Quantum staff to send the previously submitted packet directly to her.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/fixtures/joinder_quantum_case.json", "Evidence item evidence:ferron_email_jan26_hacc_directs_quantum."),
        ],
    },
    {
        "evidence_id": "ev:blossom_processed_through_hacc_waitlist",
        "headline": "Blossom applications were processed through the HACC PBV waitlist",
        "kind": "pipeline_structure",
        "proposition": "The Blossom project application path was processed through the HACC PBV waitlist, tying the housing opportunity to a structured placement and contracting pipeline.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/fixtures/joinder_quantum_case.json", "Evidence item evidence:blossom_graphrag_pbv_waitlist."),
        ],
    },
    {
        "evidence_id": "ev:written_race_discrimination_complaints",
        "headline": "Record preserves written race-discrimination complaints tied to Blossom nonprocessing",
        "kind": "complaint_record",
        "proposition": "The complaint materials say Benjamin wrote that Blossom had refused to process submitted applications for two months and had engaged in race discrimination.",
        "sources": [
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.message-support.md", "Message-level support memo summarizing preserved February 26, March 2, and March 9 complaints."),
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.cited.md", "Complaint Count IV paragraphs 79-84."),
        ],
    },
    {
        "evidence_id": "ev:feb2_black_family_comparator_email",
        "headline": "February 2 email to Ashley Ferron and blossom@quantumres.com preserved the Black-family comparator and race-based lemon-dropping accusation",
        "kind": "direct_email_record",
        "proposition": "On February 2, 2026, Benjamin emailed Ashley Ferron and blossom@quantumres.com that he had met a Black couple with one child at Balfour Park who had just been granted Section 8 and were interviewing for Blossom, while his household's application had never been sent on to HACC, and he expressly accused Quantum of race-based lemon dropping.",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0047-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-00cFTv4dFf8yZ3NpPztCKwr2LB-on4Xxz-BFEv9_5jA-mail.gmail.com/message.eml", "Exact contemporaneous .eml export."),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0047-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-00cFTv4dFf8yZ3NpPztCKwr2LB-on4Xxz-BFEv9_5jA-mail.gmail.com/message.json", "Parsed message metadata with recipients and body text."),
        ],
    },
    {
        "evidence_id": "ev:feb2_indeed_followup_to_same_recipients",
        "headline": "Five minutes later Benjamin sent Quantum Indeed material to the same recipients and quoted the comparator email below it",
        "kind": "direct_email_record",
        "proposition": "On February 2, 2026, Benjamin sent a follow-up email to Ashley Ferron and blossom@quantumres.com attaching Quantum Indeed material and quoting the 6:10 PM Balfour Park comparator and race-based lemon-dropping email below it.",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0048-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-EBH-Kk7XM2aU5btp7WByE3F09iYJksws9fYbHfhHkw-mail.gmail.com/message.eml", "Exact contemporaneous follow-up .eml export."),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0048-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-EBH-Kk7XM2aU5btp7WByE3F09iYJksws9fYbHfhHkw-mail.gmail.com/message.json", "Parsed message metadata with recipients and quoted body text."),
        ],
    },
    {
        "evidence_id": "ev:quantum_false_nonreceipt_allegation",
        "headline": "Benjamin wrote that Quantum falsely claimed no application was provided",
        "kind": "complaint_record",
        "proposition": "Benjamin wrote that Quantum falsely claimed the household had not provided an application, despite the same application being made to HACC's organization in the first place.",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/fixtures/joinder_quantum_case.json", "Evidence item evidence:email_falsely_claimed_quote."),
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.cited.md", "Complaint Count IV paragraphs 78-83."),
        ],
    },
    {
        "evidence_id": "ev:other_households_advanced_allegation",
        "headline": "Complaint alleges other displaced households moved forward while this application stalled",
        "kind": "allegation_needing_discovery",
        "proposition": "The complaint alleges that other displaced households were moved into Blossom while plaintiffs' application was never processed at all, and that plaintiffs spoke with a Black family who had been interviewed for Blossom even though plaintiffs' application did not move forward.",
        "sources": [
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.cited.md", "Complaint paragraph 79."),
        ],
    },
    {
        "evidence_id": "ev:service_animal_and_nonprocessing_complaints",
        "headline": "Complaints tied Blossom nonprocessing to service-animal and unequal-treatment concerns",
        "kind": "complaint_record",
        "proposition": "The preserved complaint support says Blossom had refused to process applications for two months and had refused to house a service animal.",
        "sources": [
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.message-support.md", "J-12, J-13, and J-16 summary."),
        ],
    },
]


EVENTS: List[Dict[str, Any]] = [
    {
        "event_id": "evt_rlra_policy_sets_race_equity_context",
        "date": "2025-01-23",
        "actor_ids": ["org:metro_shs", "org:hacc"],
        "kind": "policy_context",
        "summary": "RLRA / SHS policy set a race-equity and BIPOC-centered supportive-services and referral environment.",
        "evidence_ids": ["ev:shs_race_equity_policy_language", "ev:shs_equitable_referral_pathways", "ev:ohcs_hb2100_racial_disparities_task_force", "ev:ohcs_ori_racial_disparities_and_set_asides"],
    },
    {
        "event_id": "evt_hacc_afh_translated_race_equity_into_housing_administration",
        "date": "2022-04-14",
        "actor_ids": ["org:hacc"],
        "kind": "policy_context",
        "summary": "Clackamas County and HACC adopted AFH planning language tying racial equity to HACC forms, letters, internal practices, monitoring, and BIPOC outreach.",
        "evidence_ids": ["ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist"],
    },
    {
        "event_id": "evt_household_submits_blossom_packet_to_quantum_path",
        "date": "2025-12",
        "actor_ids": ["person:benjamin_barber", "person:jane_cortez", "org:quantum", "org:blossom"],
        "kind": "application_submission",
        "summary": "The household submitted a Blossom packet through the Quantum-linked intake path.",
        "evidence_ids": ["ev:quantum_received_blossom_packet", "ev:blossom_processed_through_hacc_waitlist"],
    },
    {
        "event_id": "evt_packet_not_transmitted_to_hacc",
        "date": "2026-01-26",
        "actor_ids": ["org:quantum", "org:hacc", "person:ashley_ferron"],
        "kind": "nontransmission",
        "summary": "HACC said Quantum had received the packet but had not provided it onward to HACC.",
        "evidence_ids": ["ev:quantum_received_blossom_packet"],
    },
    {
        "event_id": "evt_written_race_discrimination_and_nonprocessing_complaints",
        "date": "2026-02-26",
        "actor_ids": ["person:benjamin_barber", "org:hacc", "org:quantum"],
        "kind": "protected_complaint",
        "summary": "Benjamin wrote that Blossom had not processed applications for two months and had engaged in race discrimination.",
        "evidence_ids": ["ev:written_race_discrimination_complaints", "ev:service_animal_and_nonprocessing_complaints"],
    },
    {
        "event_id": "evt_feb2_quantum_put_on_notice_of_race_based_lemon_dropping_claim",
        "date": "2026-02-02",
        "actor_ids": ["person:benjamin_barber", "person:ashley_ferron", "org:quantum", "org:hacc", "org:blossom"],
        "kind": "protected_complaint",
        "summary": "Benjamin directly emailed Ashley Ferron and blossom@quantumres.com that a Black family with a fresh Section 8 grant was interviewing for Blossom while his household's application had not been transmitted to HACC, and he accused Quantum of race-based lemon dropping.",
        "evidence_ids": ["ev:feb2_black_family_comparator_email", "ev:feb2_indeed_followup_to_same_recipients"],
    },
    {
        "event_id": "evt_pipeline_harm_occurred_inside_race_conscious_program_environment",
        "date": "2026-02",
        "actor_ids": ["org:hacc", "org:quantum", "org:metro_shs", "org:blossom"],
        "kind": "causation_theory",
        "summary": "The challenged Blossom nonprocessing and comparator-skewed treatment occurred inside a county-linked housing pipeline already shaped by SHS, RLRA, AFH, and HACC race-conscious planning, outreach, monitoring, and referral language.",
        "evidence_ids": ["ev:shs_public_outcome_goal_exact_quote", "ev:shs_race_equity_policy_language", "ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:feb2_black_family_comparator_email", "ev:quantum_received_blossom_packet"],
    },
    {
        "event_id": "evt_quantum_false_nonreceipt_claim_alleged",
        "date": "2026-03-12",
        "actor_ids": ["person:benjamin_barber", "org:quantum"],
        "kind": "unequal_handling_allegation",
        "summary": "Benjamin wrote that Quantum falsely claimed the application had not been provided.",
        "evidence_ids": ["ev:quantum_false_nonreceipt_allegation"],
    },
    {
        "event_id": "evt_other_households_allegedly_advanced",
        "date": "2026-03",
        "actor_ids": ["org:blossom", "org:quantum", "org:hacc"],
        "kind": "comparator_allegation",
        "summary": "The complaint alleges that other displaced households moved forward while this application stalled.",
        "evidence_ids": ["ev:other_households_advanced_allegation"],
    },
]


OBLIGATIONS: List[Dict[str, Any]] = [
    {
        "obligation_id": "obl_private_actor_must_not_impair_contracting_opportunity_on_racial_terms",
        "actor": "org:quantum",
        "modality": "forbidden",
        "summary": "Quantum may not impair the household's own housing-related contracting opportunity on unequal racial terms.",
        "authorities": ["auth:42_usc_1981", "auth:comcast_2020", "auth:dominos_2006", "auth:runyon_1976"],
        "trigger_event_ids": ["evt_household_submits_blossom_packet_to_quantum_path"],
    },
    {
        "obligation_id": "obl_state_actor_1981_theory_must_run_through_1983",
        "actor": "org:hacc",
        "modality": "structural_limit",
        "summary": "Any HACC race-discrimination theory tied to § 1981 must be analyzed cautiously because the direct damages route generally runs through § 1983 for state actors.",
        "authorities": ["auth:jett_1989", "auth:42_usc_1983"],
        "trigger_event_ids": ["evt_rlra_policy_sets_race_equity_context", "evt_written_race_discrimination_and_nonprocessing_complaints"],
    },
    {
        "obligation_id": "obl_supportive_services_policy_context_not_enough_by_itself",
        "actor": "org:metro_shs",
        "modality": "caution",
        "summary": "A race-conscious supportive-services policy environment is relevant context, but it is not by itself enough to prove intentional discrimination in a specific contracting opportunity.",
        "authorities": ["auth:42_usc_1981", "auth:comcast_2020"],
        "trigger_event_ids": ["evt_rlra_policy_sets_race_equity_context"],
    },
]


FINDINGS: List[Dict[str, Any]] = [
    {
        "finding_id": "finding_quantum_1981_contracting_theory",
        "subject": "org:quantum",
        "status": "plausible_supported_but_needs_but_for_proof",
        "confidence": 0.74,
        "headline": "A direct § 1981 theory against Quantum is plausible because Blossom was a housing-related contracting opportunity and Quantum allegedly received but did not process or transmit the application.",
        "why": [
            "The current record supports a concrete housing-application / placement path rather than a purely abstract service complaint.",
            "Quantum is the cleaner direct § 1981 target because it is a private actor in the contracting pipeline.",
            "The February 2, 2026 email materially strengthens the record because it put both Ashley Ferron and blossom@quantumres.com on direct contemporaneous notice of a Black-family comparator and expressly framed the unequal handling as race-based lemon dropping.",
            "The main remaining issue is still proof that race was a but-for cause of the unequal handling, rather than only one suspicion among several.",
        ],
        "evidence_ids": [
            "ev:quantum_received_blossom_packet",
            "ev:blossom_processed_through_hacc_waitlist",
            "ev:feb2_black_family_comparator_email",
            "ev:feb2_indeed_followup_to_same_recipients",
            "ev:written_race_discrimination_complaints",
            "ev:quantum_false_nonreceipt_allegation",
        ],
        "authority_ids": ["auth:42_usc_1981", "auth:comcast_2020", "auth:dominos_2006", "auth:runyon_1976"],
    },
    {
        "finding_id": "finding_hacc_direct_1981_theory_weak",
        "subject": "org:hacc",
        "status": "weak_as_direct_1981_claim",
        "confidence": 0.82,
        "headline": "A direct standalone § 1981 damages claim against HACC is weaker because HACC is a state actor and the better route is generally through § 1983, Title VI, FHA, or related theories.",
        "why": [
            "The current record may support race-discrimination or steering theories against HACC, but the direct § 1981 route is structurally constrained.",
            "That does not eliminate HACC exposure; it shifts the better federal vehicle.",
        ],
        "evidence_ids": ["ev:written_race_discrimination_complaints", "ev:shs_race_equity_policy_language", "ev:shs_public_outcome_goal_exact_quote"],
        "authority_ids": ["auth:jett_1989", "auth:42_usc_1983"],
    },
    {
        "finding_id": "finding_supportive_services_cherry_picking_context",
        "subject": "org:metro_shs",
        "status": "contextual_support_not_standalone_proof",
        "confidence": 0.68,
        "headline": "The supportive-housing-services and RLRA policy materials strengthen motive, notice, and comparator discovery, but they do not by themselves prove a § 1981 violation.",
        "why": [
            "The policies show a race-conscious environment and make the comparator question more important.",
            "The current case-specific proof still turns on what happened to this Blossom application compared with others in the same pipeline.",
        ],
        "evidence_ids": ["ev:shs_public_outcome_goal_exact_quote", "ev:shs_cropped_screenshot_preserved", "ev:shs_race_equity_policy_language", "ev:shs_equitable_referral_pathways", "ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:ohcs_hb2100_racial_disparities_task_force", "ev:ohcs_ori_racial_disparities_and_set_asides"],
        "authority_ids": ["auth:42_usc_1981", "auth:comcast_2020", "auth:affh_24cfr"],
    },
    {
        "finding_id": "finding_cherry_picking_lemon_dropping_needs_comparators",
        "subject": "org:blossom",
        "status": "descriptive_theory_needs_discovery",
        "confidence": 0.66,
        "headline": "Cherry-picking and lemon-dropping are useful descriptive theories, but they need comparator and pipeline evidence before they can strongly support but-for race causation.",
        "why": [
            "The file already supports a lemon-dropping description: accepted or received, then not processed, not transmitted, and not lawfully resolved.",
            "The February 2 email now provides direct contemporaneous comparator evidence of a Black family interviewing for Blossom after recently receiving Section 8 while plaintiffs' file remained stalled.",
            "Cherry-picking becomes materially stronger if discovery confirms that similarly situated displaced households were advanced during the same period.",
        ],
        "evidence_ids": ["ev:other_households_advanced_allegation", "ev:feb2_black_family_comparator_email", "ev:quantum_received_blossom_packet", "ev:quantum_false_nonreceipt_allegation"],
        "authority_ids": ["auth:42_usc_1981", "auth:comcast_2020"],
    },
    {
        "finding_id": "finding_county_hacc_policy_extension_theory_plausible",
        "subject": "org:hacc",
        "status": "plausible_policy_extension_theory",
        "confidence": 0.71,
        "headline": "A stronger current theory is that plaintiffs' harms were an extension of a county-linked race-conscious housing administration environment, though direct implementation proof is still needed.",
        "why": [
            "Official county and HACC AFH materials tied racial equity to HACC forms, letters, internal practices, outcome monitoring, and BIPOC outreach.",
            "SHS and RLRA materials tied referral pathways, housing access, and supportive services to race-conscious outcome goals.",
            "The challenged Blossom application path sat inside that same county-linked intake, referral, voucher, and placement pipeline.",
            "The February 2 email directly described the harm as race-linked while the pipeline was still active.",
            "The strongest current extension theory is therefore county / HACC implementation, with the state layer more structural unless more direct state operating criteria are found.",
        ],
        "evidence_ids": ["ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:shs_public_outcome_goal_exact_quote", "ev:shs_race_equity_policy_language", "ev:shs_equitable_referral_pathways", "ev:ohcs_hb2100_racial_disparities_task_force", "ev:ohcs_ori_racial_disparities_and_set_asides", "ev:feb2_black_family_comparator_email", "ev:quantum_received_blossom_packet"],
        "authority_ids": ["auth:42_usc_1981", "auth:comcast_2020", "auth:affh_24cfr", "auth:jett_1989", "auth:42_usc_1983"],
    },
]


def _build_knowledge_graph() -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []

    for party_id, party in PARTIES.items():
        nodes.append({"id": party_id, "kind": "party", **party})
    for evidence in EVIDENCE:
        nodes.append({
            "id": evidence["evidence_id"],
            "kind": "evidence",
            "headline": evidence["headline"],
            "proposition": evidence["proposition"],
        })
    for event in EVENTS:
        nodes.append({
            "id": event["event_id"],
            "kind": "event",
            "date": event["date"],
            "summary": event["summary"],
        })
    for finding in FINDINGS:
        nodes.append({
            "id": finding["finding_id"],
            "kind": "finding",
            "status": finding["status"],
            "headline": finding["headline"],
        })

    for event in EVENTS:
        for actor_id in event["actor_ids"]:
            edges.append({"source": actor_id, "target": event["event_id"], "relation": "participates_in"})
        for evidence_id in event["evidence_ids"]:
            edges.append({"source": evidence_id, "target": event["event_id"], "relation": "supports"})

    for finding in FINDINGS:
        edges.append({"source": finding["subject"], "target": finding["finding_id"], "relation": "subject_of"})
        for evidence_id in finding["evidence_ids"]:
            edges.append({"source": evidence_id, "target": finding["finding_id"], "relation": "supports"})

    return {
        "metadata": {"generatedAt": CURRENT_DATE.isoformat(), "purpose": "42 U.S.C. § 1981 supportive-services knowledge graph"},
        "nodes": nodes,
        "edges": edges,
    }


def _build_dependency_graph() -> Dict[str, Any]:
    nodes = [
        "same_right_to_make_and_enforce_contracts",
        "plaintiff_must_have_own_contracting_interest",
        "private_actor_can_violate_1981",
        "race_must_be_but_for_cause",
        "state_actor_route_generally_runs_through_1983",
        "public_shs_quote_is_real_policy_context",
        "supportive_services_policy_context_relevant_but_not_sufficient",
        "county_hacc_implementation_environment_strengthens_causation",
        "state_layer_more_structural_than_operational",
        "direct_contemporaneous_comparator_notice_strengthens_case",
        "comparator_evidence_can_strengthen_but_for_inference",
        "quantum_1981_theory_plausible",
        "hacc_direct_1981_theory_weak",
        "cherry_picking_and_lemon_dropping_need_comparators",
    ]
    edges = [
        ["same_right_to_make_and_enforce_contracts", "quantum_1981_theory_plausible"],
        ["plaintiff_must_have_own_contracting_interest", "quantum_1981_theory_plausible"],
        ["private_actor_can_violate_1981", "quantum_1981_theory_plausible"],
        ["race_must_be_but_for_cause", "quantum_1981_theory_plausible"],
        ["state_actor_route_generally_runs_through_1983", "hacc_direct_1981_theory_weak"],
        ["public_shs_quote_is_real_policy_context", "supportive_services_policy_context_relevant_but_not_sufficient"],
        ["supportive_services_policy_context_relevant_but_not_sufficient", "county_hacc_implementation_environment_strengthens_causation"],
        ["county_hacc_implementation_environment_strengthens_causation", "hacc_direct_1981_theory_weak"],
        ["state_layer_more_structural_than_operational", "county_hacc_implementation_environment_strengthens_causation"],
        ["supportive_services_policy_context_relevant_but_not_sufficient", "hacc_direct_1981_theory_weak"],
        ["supportive_services_policy_context_relevant_but_not_sufficient", "cherry_picking_and_lemon_dropping_need_comparators"],
        ["direct_contemporaneous_comparator_notice_strengthens_case", "comparator_evidence_can_strengthen_but_for_inference"],
        ["comparator_evidence_can_strengthen_but_for_inference", "quantum_1981_theory_plausible"],
        ["comparator_evidence_can_strengthen_but_for_inference", "cherry_picking_and_lemon_dropping_need_comparators"],
    ]
    node_support = {
        "same_right_to_make_and_enforce_contracts": {"authorities": ["auth:42_usc_1981"], "evidence": []},
        "plaintiff_must_have_own_contracting_interest": {"authorities": ["auth:dominos_2006"], "evidence": ["ev:blossom_processed_through_hacc_waitlist"]},
        "private_actor_can_violate_1981": {"authorities": ["auth:runyon_1976"], "evidence": ["ev:quantum_received_blossom_packet"]},
        "race_must_be_but_for_cause": {"authorities": ["auth:comcast_2020"], "evidence": ["ev:written_race_discrimination_complaints", "ev:other_households_advanced_allegation"]},
        "state_actor_route_generally_runs_through_1983": {"authorities": ["auth:jett_1989", "auth:42_usc_1983"], "evidence": ["ev:written_race_discrimination_complaints"]},
        "public_shs_quote_is_real_policy_context": {"authorities": [], "evidence": ["ev:shs_public_outcome_goal_exact_quote", "ev:shs_cropped_screenshot_preserved"]},
        "supportive_services_policy_context_relevant_but_not_sufficient": {"authorities": ["auth:42_usc_1981", "auth:comcast_2020", "auth:affh_24cfr"], "evidence": ["ev:shs_public_outcome_goal_exact_quote", "ev:shs_race_equity_policy_language", "ev:shs_equitable_referral_pathways", "ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:ohcs_hb2100_racial_disparities_task_force", "ev:ohcs_ori_racial_disparities_and_set_asides"]},
        "county_hacc_implementation_environment_strengthens_causation": {"authorities": ["auth:42_usc_1981", "auth:comcast_2020", "auth:affh_24cfr"], "evidence": ["ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:shs_public_outcome_goal_exact_quote", "ev:shs_race_equity_policy_language", "ev:feb2_black_family_comparator_email", "ev:quantum_received_blossom_packet"]},
        "state_layer_more_structural_than_operational": {"authorities": ["auth:affh_24cfr"], "evidence": ["ev:ohcs_hb2100_racial_disparities_task_force", "ev:ohcs_ori_racial_disparities_and_set_asides"]},
        "direct_contemporaneous_comparator_notice_strengthens_case": {"authorities": ["auth:42_usc_1981", "auth:comcast_2020"], "evidence": ["ev:feb2_black_family_comparator_email", "ev:feb2_indeed_followup_to_same_recipients"]},
        "comparator_evidence_can_strengthen_but_for_inference": {"authorities": ["auth:comcast_2020"], "evidence": ["ev:other_households_advanced_allegation", "ev:feb2_black_family_comparator_email"]},
        "quantum_1981_theory_plausible": {"authorities": ["auth:42_usc_1981", "auth:comcast_2020", "auth:dominos_2006", "auth:runyon_1976"], "evidence": ["ev:quantum_received_blossom_packet", "ev:blossom_processed_through_hacc_waitlist", "ev:feb2_black_family_comparator_email", "ev:feb2_indeed_followup_to_same_recipients", "ev:written_race_discrimination_complaints", "ev:quantum_false_nonreceipt_allegation"]},
        "hacc_direct_1981_theory_weak": {"authorities": ["auth:jett_1989", "auth:42_usc_1983"], "evidence": ["ev:shs_public_outcome_goal_exact_quote", "ev:shs_race_equity_policy_language", "ev:hacc_afh_racial_equity_lens_for_forms_and_letters", "ev:hacc_afh_bipoc_outreach_waitlist", "ev:written_race_discrimination_complaints"]},
        "cherry_picking_and_lemon_dropping_need_comparators": {"authorities": ["auth:42_usc_1981", "auth:comcast_2020"], "evidence": ["ev:other_households_advanced_allegation", "ev:feb2_black_family_comparator_email", "ev:quantum_received_blossom_packet"]},
    }
    return {
        "metadata": {"generatedAt": CURRENT_DATE.isoformat(), "purpose": "42 U.S.C. § 1981 supportive-services dependency graph"},
        "nodes": nodes,
        "edges": edges,
        "nodeSupport": node_support,
    }


def _build_report() -> Dict[str, Any]:
    return {
        "metadata": {
            "reportId": "section1981_supportive_services_001",
            "generatedAt": CURRENT_DATE.isoformat(),
        },
        "authorities": AUTHORITIES,
        "evidence": EVIDENCE,
        "events": EVENTS,
        "obligations": OBLIGATIONS,
        "findings": FINDINGS,
        "summary": {
            "strongestCurrentTheory": "The strongest current § 1981 theory is against Quantum, not HACC, because Quantum is a private actor in the Blossom housing-contracting path, the record supports receipt plus nonprocessing/nontransmission of the application, and a February 2, 2026 email directly put blossom@quantumres.com on notice of a Black-family comparator and alleged race-based lemon dropping.",
            "mainLimiters": [
                "Comcast but-for causation requirement.",
                "Need for broader comparator or pipeline evidence beyond the currently preserved February 2 comparator email.",
                "HACC state-actor route problem for direct § 1981 damages claims.",
                "Supportive-services and AFH race-equity policy language are now grounded to official county, HACC, and OHCS materials, but they remain causation support rather than standalone proof.",
            ],
            "bestRecordStrengtheningTasks": [
                "Obtain Blossom / Quantum intake logs, scanning logs, and status codes.",
                "Obtain comparative Blossom applicant movement records for displaced households during the same period.",
                "Obtain SHS / RLRA / HACC referral and prioritization criteria actually used in the pipeline.",
                "Obtain the AFH implementation materials, staff guidance, or dashboards showing how the racial-equity lens was operationalized in HACC forms, letters, referrals, or placement handling.",
                "Obtain any contracts, assurances, or certifications tying supportive-services administration to nondiscrimination obligations.",
            ],
        },
    }


def _build_flogic(report: Dict[str, Any]) -> str:
    lines: List[str] = ["%% section1981_supportive_services_knowledge_graph.flogic", ""]
    for party_id, party in PARTIES.items():
        token = party_id.replace(":", "_").replace("-", "_")
        lines.append(f"{token}:party[")
        lines.append(f'  name -> "{party["name"]}";')
        lines.append(f'  role -> "{party["role"]}"')
        lines.append("] .")
        lines.append("")
    for finding in FINDINGS:
        token = finding["finding_id"].replace(":", "_").replace("-", "_")
        subj = finding["subject"].replace(":", "_").replace("-", "_")
        lines.append(f"{token}:finding[")
        lines.append(f"  subject -> {subj};")
        lines.append(f'  status -> "{finding["status"]}"')
        lines.append("] .")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_dcec(report: Dict[str, Any]) -> str:
    lines: List[str] = ["% section1981_supportive_services_obligations_dcec.pl", ""]
    for event in EVENTS:
        event_atom = event["event_id"].replace(":", "_").replace("-", "_")
        date_atom = event["date"].replace("-", "_")
        lines.append(f"Happens({event_atom}, t_{date_atom}).")
    lines.append("")
    for obligation in OBLIGATIONS:
        obl_atom = obligation["obligation_id"].replace(":", "_").replace("-", "_")
        actor_atom = obligation["actor"].replace(":", "_").replace("-", "_")
        lines.append(f"Ought({actor_atom}, {obl_atom}).")
    return "\n".join(lines).rstrip() + "\n"


def _build_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "# 42 U.S.C. § 1981 / Supportive Services Analysis",
        "",
        "## Bottom Line",
        "",
        f"- {report['summary']['strongestCurrentTheory']}",
    ]
    for item in report["summary"]["mainLimiters"]:
        lines.append(f"- Limiter: {item}")
    lines.extend(["", "## Findings", ""])
    for finding in report["findings"]:
        lines.append(f"### {finding['finding_id']}")
        lines.append("")
        lines.append(f"- Status: `{finding['status']}`")
        lines.append(f"- Headline: {finding['headline']}")
        for item in finding["why"]:
            lines.append(f"- Why: {item}")
        lines.append("- Evidence:")
        for evidence_id in finding["evidence_ids"]:
            evidence = next(item for item in EVIDENCE if item["evidence_id"] == evidence_id)
            lines.append(f"  - `{evidence_id}`: {evidence['proposition']}")
        lines.append("- Authorities:")
        for authority_id in finding["authority_ids"]:
            authority = next(item for item in AUTHORITIES if item["authority_id"] == authority_id)
            lines.append(f"  - `{authority_id}`: {authority['proposition']}")
        lines.append("")
    lines.extend(["## Best Next Discovery", ""])
    for item in report["summary"]["bestRecordStrengtheningTasks"]:
        lines.append(f"- {item}")
    lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_audit(report: Dict[str, Any]) -> Dict[str, Any]:
    tasks = [
        {
            "taskId": "task_get_quantum_intake_logs",
            "priority": "high",
            "why": "The strongest direct § 1981 theory against Quantum turns on receipt, nonprocessing, and who else moved through the same pipeline.",
        },
        {
            "taskId": "task_get_comparators",
            "priority": "high",
            "why": "Comparator evidence is the cleanest way to strengthen but-for race causation in a cherry-picking or lemon-dropping theory.",
        },
        {
            "taskId": "task_get_shs_rlra_selection_records",
            "priority": "medium",
            "why": "The supportive-services / racial-equity policy environment is useful context, but actual operating criteria are needed to connect it to this case.",
        },
        {
            "taskId": "task_route_hacc_theory_through_1983_or_title_vi",
            "priority": "medium",
            "why": "If HACC is targeted on race-discrimination grounds, the direct standalone § 1981 route is weaker and should be analyzed through alternative federal vehicles.",
        },
    ]
    return {
        "metadata": {"generatedAt": CURRENT_DATE.isoformat()},
        "recordStrengtheningTasks": tasks,
        "weakFindings": [item for item in FINDINGS if "weak" in item["status"] or "needs" in item["status"] or "discovery" in item["status"]],
    }


def write_outputs() -> Dict[str, Path]:
    report = _build_report()
    knowledge_graph = _build_knowledge_graph()
    dependency_graph = _build_dependency_graph()
    audit = _build_audit(report)

    paths = {
        "report_json": OUTPUT_DIR / "section1981_supportive_services_report.json",
        "report_md": OUTPUT_DIR / "section1981_supportive_services_report.md",
        "knowledge_graph": OUTPUT_DIR / "section1981_supportive_services_knowledge_graph.json",
        "dependency_graph": OUTPUT_DIR / "section1981_supportive_services_dependency_graph.json",
        "flogic": OUTPUT_DIR / "section1981_supportive_services_knowledge_graph.flogic",
        "dcec": OUTPUT_DIR / "section1981_supportive_services_obligations_dcec.pl",
        "audit": OUTPUT_DIR / "section1981_supportive_services_audit.json",
    }
    paths["report_json"].write_text(json.dumps(report, indent=2) + "\n")
    paths["report_md"].write_text(_build_markdown(report))
    paths["knowledge_graph"].write_text(json.dumps(knowledge_graph, indent=2) + "\n")
    paths["dependency_graph"].write_text(json.dumps(dependency_graph, indent=2) + "\n")
    paths["flogic"].write_text(_build_flogic(report))
    paths["dcec"].write_text(_build_dcec(report))
    paths["audit"].write_text(json.dumps(audit, indent=2) + "\n")
    return paths


def main() -> int:
    for path in write_outputs().values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
