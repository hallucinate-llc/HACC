"""
VAWA-focused formal analysis for the HACC / Quantum record.

This module builds a case-specific analysis package that combines:
- a party/event knowledge graph,
- frame-logic exports,
- deontic cognitive event calculus style formulas,
- a simple dependency graph for the governing VAWA duties, and
- a lightweight TDFOL proof audit against the local prover stack.

The goal is not to replace legal judgment. It is to separate:
- duties that are clearly imposed by HUD's VAWA rules and HACC's own policy;
- record-supported factual events; and
- breach conclusions that are supported, unresolved, or presently weak.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional

if __package__ in {None, ""}:
    workspace_root = Path(__file__).resolve().parent.parent
    workspace_root_str = str(workspace_root)
    if workspace_root_str not in sys.path:
        sys.path.insert(0, workspace_root_str)

from formal_logic.frame_logic import FrameKnowledgeBase


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUT_DIR = ROOT / "outputs"
CURRENT_DATE = datetime(2026, 4, 5)


@dataclass(frozen=True)
class PartySpec:
    party_id: str
    name: str
    role: str


PARTIES: Dict[str, PartySpec] = {
    "person:benjamin_barber": PartySpec("person:benjamin_barber", "Benjamin Barber", "Resident / reporting party"),
    "person:jane_cortez": PartySpec("person:jane_cortez", "Jane Cortez", "Resident / protected household member"),
    "person:julio_cortez": PartySpec("person:julio_cortez", "Julio Cortez", "Disputed household member / alleged perpetrator"),
    "person:solomon_barber": PartySpec("person:solomon_barber", "Solomon Samuel Barber", "Restrained non-household actor / alleged outside interferer"),
    "person:ashley_ferron": PartySpec("person:ashley_ferron", "Ashley Ferron", "HACC staff"),
    "person:kati_tilton": PartySpec("person:kati_tilton", "Kati Tilton", "HACC staff"),
    "person:jamila": PartySpec("person:jamila", "Jamila / Jemiliah (county-side contact)", "County-side social-services or money-management actor"),
    "org:hacc": PartySpec("org:hacc", "Housing Authority of Clackamas County", "PHA / covered housing provider"),
    "org:hacc_relocation": PartySpec("org:hacc_relocation", "HACC Relocation", "HACC sub-office / operational actor"),
    "org:hacc_public_housing": PartySpec("org:hacc_public_housing", "HACC Public Housing", "HACC sub-office / operational actor"),
    "org:quantum": PartySpec("org:quantum", "Quantum Residential", "Property manager / owner-side participant"),
    "org:clackamas_social_services": PartySpec("org:clackamas_social_services", "Clackamas County Social Services / Money Management", "County-side program actor"),
    "org:hud": PartySpec("org:hud", "U.S. Department of Housing and Urban Development", "Federal agency"),
}


AUTHORITIES: List[Dict[str, Any]] = [
    {
        "authority_id": "auth:24_cfr_5_2003",
        "label": "24 C.F.R. § 5.2003",
        "citation": "24 C.F.R. § 5.2003",
        "court": "eCFR",
        "year": "current",
        "pincite": "definitions of bifurcate and covered housing provider",
        "sourceUrl": "https://www.womenslaw.org/laws/federal/statutes/24-cfr-ss-52003-definitions",
        "propositions": [
            "Covered housing provider includes PHAs, owners, managers, state and local governments or agencies thereof, and other entities with responsibility for administration or oversight of VAWA protections.",
            "Depending on the duty being performed, there may be more than one covered housing provider and the duty-bearer may not always be the same entity.",
            "Bifurcation means dividing a lease so that certain tenants or lawful occupants may be removed while remaining lawful occupants may continue to reside under the lease.",
        ],
    },
    {
        "authority_id": "auth:24_cfr_5_2005",
        "label": "24 C.F.R. § 5.2005",
        "citation": "24 C.F.R. § 5.2005",
        "court": "eCFR",
        "year": "current",
        "pincite": "subsections (a), (b), (c), (e)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-5/section-5.2005",
        "propositions": [
            "Covered housing providers must provide the VAWA notice of occupancy rights and certification form at specified program stages, including eviction or termination notice stages.",
            "A victim may not be denied assistance, evicted, or terminated because of domestic violence, dating violence, sexual assault, or stalking.",
            "Abuse-related incidents may not be construed as serious or repeated lease violations by the victim.",
            "Covered housing providers must maintain an emergency transfer plan and preserve transfer records confidentially.",
        ],
    },
    {
        "authority_id": "auth:34_usc_12491",
        "label": "34 U.S.C. § 12491",
        "citation": "34 U.S.C. § 12491",
        "court": "U.S. Code",
        "year": "current",
        "pincite": "subsections (b), (c), (d), (e)",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title34-section12491",
        "propositions": [
            "A public housing agency or owner or manager may not deny assistance, terminate participation, or evict on the basis that the tenant is or has been a victim of protected abuse, if the tenant otherwise qualifies.",
            "When notified of a court order, a public housing agency or owner or manager may comply with that order regarding rights of access to or control of property, including civil protection orders issued to protect a victim.",
            "Any information submitted under VAWA, including survivor status, must be maintained in confidence and not disclosed except for written consent, eviction-proceeding use, or other required law.",
            "Emergency-transfer protections require reasonable confidentiality measures so the provider does not disclose the location of the dwelling unit to the person committing the abuse.",
        ],
    },
    {
        "authority_id": "auth:34_usc_12494",
        "label": "34 U.S.C. § 12494",
        "citation": "34 U.S.C. § 12494",
        "court": "U.S. Code",
        "year": "current",
        "pincite": "subsections (a)-(c)",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?req=%28title%3A34+section%3A12494+edition%3Aprelim%29",
        "propositions": [
            "No public housing agency or owner or manager may discriminate against a person because that person opposed an unlawful VAWA-related act or participated in a matter related to VAWA housing rights.",
            "No public housing agency or owner or manager may coerce, intimidate, threaten, interfere with, or retaliate against a person exercising or aiding another person in exercising VAWA housing rights.",
            "HUD and DOJ implement and enforce these protections using Fair Housing Act-style rights and remedies.",
        ],
    },
    {
        "authority_id": "auth:24_cfr_5_2007",
        "label": "24 C.F.R. § 5.2007",
        "citation": "24 C.F.R. § 5.2007",
        "court": "eCFR",
        "year": "current",
        "pincite": "subsections (a), (b), (c)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-5/section-5.2007",
        "propositions": [
            "If VAWA documentation is requested, the request must be in writing.",
            "The tenant must receive at least 14 business days to respond.",
            "The housing provider must accept one of the listed documentation paths and may not insist on a police report or court order as the only form.",
            "VAWA-submitted information must be kept confidential except for narrow exceptions.",
        ],
    },
    {
        "authority_id": "auth:24_cfr_5_2009",
        "label": "24 C.F.R. § 5.2009",
        "citation": "24 C.F.R. § 5.2009",
        "court": "eCFR",
        "year": "current",
        "pincite": "subsections (a), (b)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-5/section-5.2009",
        "propositions": [
            "A provider may bifurcate a lease to remove the perpetrator.",
            "The provider may not thereby evict, remove, terminate assistance to, or otherwise penalize the victim or other lawful occupants.",
            "If bifurcation affects eligibility, the remaining household must receive a reasonable period to establish eligibility or find other housing.",
        ],
    },
    {
        "authority_id": "auth:hud_vawa_rights",
        "label": "HUD VAWA Rights Page",
        "citation": "HUD Your Rights Under the Violence Against Women Act (VAWA)",
        "court": "HUD",
        "year": "current",
        "pincite": "housing rights overview",
        "sourceUrl": "https://www.hud.gov/hud-partners/fair-housing-vawa",
        "propositions": [
            "A provider may not require a police report to provide VAWA protections if another allowed documentation path is chosen.",
            "Emergency transfer rights require an express request and an imminent-harm or qualifying assault basis.",
            "Confidentiality duties cover survivor status and related submissions.",
        ],
    },
    {
        "authority_id": "auth:johnson_v_palumbo",
        "label": "Matter of Johnson v. Palumbo",
        "citation": "154 A.D.3d 231 (N.Y. App. Div. 2017)",
        "court": "N.Y. App. Div.",
        "year": "2017",
        "pincite": "pp. 244-246 equivalent discussion",
        "sourceUrl": "https://law.justia.com/cases/new-york/appellate-division-second-department/2017/2014-09233.html",
        "propositions": [
            "VAWA can prohibit termination where the alleged lease violation is inextricably intertwined with domestic violence against the tenant.",
            "Sworn hearing testimony may suffice to document domestic violence for VAWA purposes.",
            "An agency errs when it terminates assistance without honoring VAWA protections on a record showing abuse-related coercion and nonvoluntary household presence.",
        ],
    },
    {
        "authority_id": "auth:pih_2017_08",
        "label": "HUD Notice PIH 2017-08",
        "citation": "HUD Notice PIH 2017-08",
        "court": "HUD",
        "year": "2017",
        "pincite": "pages 9, 18, 31-32",
        "sourceUrl": "https://www.hud.gov/sites/documents/17-08PIHN.PDF",
        "propositions": [
            "For public housing, HCV, and PBV, the PHA, not the owner, bears the primary notice-of-rights obligation.",
            "Owners and PHAs both carry confidentiality duties when VAWA information is submitted to them.",
            "Owners may still participate in tenancy-side lease bifurcation and related implementation steps.",
            "Except for PHA-owned units, the owner, not the PHA, bifurcates the lease in HCV/PBV contexts.",
            "If an owner makes a written documentation request, the owner must accept the listed documentation forms, may not require extra third-party documentation absent conflict, and may not take adverse action during the 14-business-day response period.",
        ],
    },
    {
        "authority_id": "auth:boston_housing_authority_v_ya",
        "label": "Boston Housing Authority v. Y.A.",
        "citation": "482 Mass. 240 (2019)",
        "court": "Mass. S.J.C.",
        "year": "2019",
        "pincite": "discussion of VAWA defense timing, causal nexus, and no heightened standard",
        "sourceUrl": "https://law.justia.com/cases/massachusetts/supreme-court/2019/sjc-12623.html",
        "propositions": [
            "A covered housing provider role is functional and may include a housing authority as landlord or administrator for the relevant step.",
            "A tenant may raise VAWA protection in court even if domestic violence was not previously presented to the landlord, although earlier notice is the better practice for provider-side relief.",
            "The decision-maker must examine whether domestic violence contributed to the adverse factor, such as nonpayment or another asserted lease breach.",
            "VAWA does not bar adverse action for conduct unrelated to domestic violence, but the provider may not impose a more demanding standard on a victim than on other tenants.",
        ],
    },
    {
        "authority_id": "auth:mccoy_v_hano",
        "label": "McCoy v. Housing Authority of New Orleans",
        "citation": "No. 15-398, 2016 WL 4708149 (E.D. La. Sept. 2, 2016)",
        "court": "E.D. La.",
        "year": "2016",
        "pincite": "summary judgment discussion of absent termination evidence and absent agency proof",
        "sourceUrl": "https://cases.justia.com/federal/district-courts/louisiana/laedce/2%3A2015cv00398/164919/149/0.pdf",
        "propositions": [
            "A VAWA theory weakens where the record does not show that the housing authority actually initiated termination of assistance or other covered adverse action.",
            "Derivative or vicarious fault theories weaken where the record does not show that the defendant controlled the relevant owner-side action or that an agency relationship is proved.",
            "The case is a false-positive control: not every eviction-adjacent or domestic-violence-adjacent dispute is a proved VAWA violation without the covered action and actor linkage.",
        ],
    },
    {
        "authority_id": "auth:fheo_2023_01",
        "label": "FHEO Notice 2023-01",
        "citation": "HUD FHEO Notice 2023-01",
        "court": "HUD FHEO",
        "year": "2023",
        "pincite": "HUD enforcement authority after VAWA 2022",
        "sourceUrl": "https://www.hud.gov/sites/dfiles/FHEO/documents/FHEO-2023-01-%20FHEO%20VAWA%20Notice.pdf",
        "propositions": [
            "HUD now enforces VAWA housing protections through FHEO complaint procedures using Fair Housing Act-style processes.",
            "Covered housing providers and program participants are expected to comply with VAWA 2022 housing-rights requirements, including anti-retaliation and complaint-access principles recognized by HUD's 2022 and 2023 guidance.",
        ],
    },
    {
        "authority_id": "auth:42_usc_1437d_k",
        "label": "42 U.S.C. § 1437d(k)",
        "citation": "42 U.S.C. § 1437d(k)",
        "court": "U.S. Code",
        "year": "current",
        "pincite": "grounds of adverse action, hearing, documents, witnesses, written decision",
        "sourceUrl": "https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title42-section1437d%28l%29%285%29",
        "propositions": [
            "A public housing agency must advise tenants of the specific grounds of proposed adverse action.",
            "A public housing agency must provide an opportunity for a hearing before an impartial party upon timely request.",
            "A tenant must have the opportunity to examine relevant documents, question witnesses, and receive a written decision.",
        ],
    },
    {
        "authority_id": "auth:24_cfr_982_555",
        "label": "24 C.F.R. § 982.555",
        "citation": "24 C.F.R. § 982.555",
        "court": "eCFR",
        "year": "current",
        "pincite": "subsections (a), (c), (d), (e)",
        "sourceUrl": "https://www.ecfr.gov/current/title-24/part-982/section-982.555",
        "propositions": [
            "A PHA must give a participant family an opportunity for an informal hearing for termination-of-assistance decisions and certain subsidy-size determinations.",
            "Prompt written notice must contain a brief statement of reasons, explain the right to request a hearing, and state the deadline to request one.",
            "Where a hearing is required, the PHA must proceed in a reasonably expeditious manner and permit document access, representation, evidence, and questioning of witnesses.",
            "The hearing officer must issue a written decision briefly stating the reasons for the decision.",
        ],
    },
]


def _source(path: str, note: str = "") -> Dict[str, str]:
    payload = {"path": path}
    if note:
        payload["note"] = note
    return payload


EVIDENCE: List[Dict[str, Any]] = [
    {
        "evidence_id": "ev:oct_2025_bifurcation_request",
        "date": "2025-10-15",
        "certainty": "moderate",
        "weight": 0.62,
        "polarity": "supports_violation_theory",
        "summary": "Workspace narrative states that Benjamin Barber raised abuse and requested lease bifurcation in October 2025, and HACC responded that a restraining order was required before it would act.",
        "actors": ["person:benjamin_barber", "org:hacc"],
        "kind": "record_summary",
        "sources": [
            _source("/home/barberb/HACC/workspace/did-key-hacc-temp-session.json"),
            _source("/home/barberb/HACC/workspace/improved-complaint-from-temporary-session.cited.md"),
        ],
    },
    {
        "evidence_id": "ev:nov_24_hacc_legal_docs_request",
        "date": "2025-11-24",
        "certainty": "high",
        "weight": 0.83,
        "polarity": "supports_violation_theory",
        "summary": "Ashley Ferron asked for legal documentation regarding who was and was not currently residing in the household and referenced emails regarding Julio Cortez in Jane Cortez's file.",
        "actors": ["person:ashley_ferron", "org:hacc", "person:julio_cortez", "person:jane_cortez"],
        "kind": "email_notice",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml", "Quoted November 24, 2025 Ferron message forwarding the matter to Public Housing and requesting legal documentation regarding who was and was not residing in the household."),
        ],
    },
    {
        "evidence_id": "ev:nov_24_charley_skee_file_review",
        "date": "2025-11-24",
        "certainty": "high",
        "weight": 0.79,
        "polarity": "supports_notice_theory",
        "summary": "Charley Skee responded that Public Housing would review the file for the unit at 10043 SE 32nd Ave., showing the occupancy dispute had reached HACC's Public Housing review path by November 24, 2025.",
        "actors": ["org:hacc_public_housing", "org:hacc", "person:benjamin_barber"],
        "kind": "email_notice",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml", "Quoted November 24, 2025 Charley Skee response stating that Public Housing would review the file for the unit."),
        ],
    },
    {
        "evidence_id": "ev:dec_10_lease_adjustment_objection",
        "date": "2025-12-10",
        "certainty": "high",
        "weight": 0.8,
        "polarity": "supports_violation_theory",
        "summary": "Benjamin Barber objected to HACC's December 4 lease adjustment and tied it to the December 9 court hearing involving Julio.",
        "actors": ["person:benjamin_barber", "org:hacc", "person:julio_cortez"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:jan_1_lease_amendment_remove_benjamin",
        "date": "2026-01-01",
        "certainty": "high",
        "weight": 0.93,
        "polarity": "supports_violation_theory",
        "summary": "HACC generated a lease amendment effective January 1, 2026 that removed Benjamin Barber from the lease.",
        "actors": ["org:hacc", "person:benjamin_barber"],
        "kind": "lease_document",
        "sources": [
            _source("/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0011-RE-Allegations-of-Fraud---JC-Household-c714b4b1e07348b08e939bd0c8f10431-clackamas.us/attachments/CORTEZ-JANE-7459-PH-LEASE-RIDER-WITH-SIGNATURE-1-.pdf"),
        ],
    },
    {
        "evidence_id": "ev:jan_1_lease_amendment_contains_hearing_language",
        "date": "2025-12-04",
        "certainty": "high",
        "weight": 0.86,
        "polarity": "supports_process_clarification",
        "summary": "The lease amendment removing Benjamin states that tenants have the right to request an explanation of the basis for the rent determination within 10 days of the amendment and, if they disagree, the right to request a hearing under the Housing Authority grievance procedure.",
        "actors": ["org:hacc", "person:benjamin_barber", "person:jane_cortez"],
        "kind": "lease_document",
        "sources": [
            _source("/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0011-RE-Allegations-of-Fraud---JC-Household-c714b4b1e07348b08e939bd0c8f10431-clackamas.us/attachments/CORTEZ-JANE-7459-PH-LEASE-RIDER-WITH-SIGNATURE-1-.pdf"),
        ],
    },
    {
        "evidence_id": "ev:dec_23_termination_notice_included_grievance_rights",
        "date": "2025-12-23",
        "certainty": "high",
        "weight": 0.77,
        "polarity": "supports_process_clarification",
        "summary": "A December 23, 2025 HACC termination notice told Jane she could request an informal grievance within 10 business days before a court hearing, showing that some hearing language existed in the record for a separate termination notice.",
        "actors": ["org:hacc", "person:jane_cortez"],
        "kind": "termination_notice",
        "sources": [
            _source("/home/barberb/HACC/evidence/paper documents/HACC 90 day notice 2.pdf"),
            _source("/home/barberb/HACC/evidence/paper documents/HACC 90 day notice.pdf"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_jane_does_not_want_to_live_with_julio",
        "date": "2026-01-12",
        "certainty": "high",
        "weight": 0.88,
        "polarity": "supports_violation_theory",
        "summary": "Benjamin Barber told HACC that Jane did not want to live with Julio and referenced a restraining-order path.",
        "actors": ["person:benjamin_barber", "person:jane_cortez", "person:julio_cortez", "org:hacc"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0012-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9_XT-RJqkeGndyUUwF-gUpo9vGeLevTdB2oHu-x8d88g-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_hacc_court_doc_requirement",
        "date": "2026-01-12",
        "certainty": "high",
        "weight": 0.9,
        "polarity": "supports_violation_theory",
        "summary": "HACC responded that Julio remained a household member and asked for court documentation showing that Julio could not reside in the household.",
        "actors": ["org:hacc", "person:julio_cortez", "person:benjamin_barber"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0012-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9_XT-RJqkeGndyUUwF-gUpo9vGeLevTdB2oHu-x8d88g-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_bare_reason_for_benjamin_removal",
        "date": "2026-01-12",
        "certainty": "high",
        "weight": 0.86,
        "polarity": "supports_due_process_violation_theory",
        "summary": "On January 12, 2026, HACC told Benjamin he was no longer listed as a household member effective January 1, 2026 and gave only a bare explanation that an internal review and court documentation on file led HACC to determine the household consisted of Julio and Jane.",
        "actors": ["org:hacc", "org:hacc_relocation", "person:benjamin_barber", "person:julio_cortez", "person:jane_cortez"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_port_out_and_order_notice",
        "date": "2026-01-12",
        "certainty": "high",
        "weight": 0.79,
        "polarity": "supports_violation_theory",
        "summary": "Benjamin replied that he would complete the Jane Cortez versus Julio Cortez restraining-order paperwork and send the port-out request.",
        "actors": ["person:benjamin_barber", "person:jane_cortez", "person:julio_cortez", "org:hacc"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:waterleaf_application_created_dec_23_2025",
        "date": "2025-12-23",
        "certainty": "high",
        "weight": 0.88,
        "polarity": "supports_transfer_delay_theory",
        "summary": "A preserved Waterleaf application screenshot shows a waiting-list application created on December 23, 2025, later marked submitted and placed on the waitlist on January 28, 2026.",
        "actors": ["person:benjamin_barber", "person:jane_cortez"],
        "kind": "application_screenshot",
        "sources": [
            _source("/home/barberb/HACC/evidence/history/waterleaf_application.png"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request",
        "date": "2026-01-12",
        "certainty": "high",
        "weight": 0.89,
        "polarity": "supports_transfer_delay_theory",
        "summary": "In a January 12, 2026 email quoted in the preserved HACC thread, Benjamin told HACC that Waterleaf wanted to know the voucher amount, Jane was scheduled for a tour, and she had already signed the application and turned it in.",
        "actors": ["person:benjamin_barber", "person:jane_cortez", "org:hacc"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml", "Quoted January 12, 2026 email stating Waterleaf wanted the voucher amount and the signed application had already been turned in."),
        ],
    },
    {
        "evidence_id": "ev:jan_26_hacc_acknowledged_port_to_multnomah",
        "date": "2026-01-26",
        "certainty": "high",
        "weight": 0.84,
        "polarity": "supports_transfer_delay_theory",
        "summary": "Ashley Ferron wrote on January 26, 2026 that the household had chosen to move forward with the voucher and to port to Multnomah County.",
        "actors": ["person:ashley_ferron", "org:hacc", "person:jane_cortez", "person:benjamin_barber"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml", "Quoted January 26, 2026 Ashley Ferron message acknowledging the household had chosen to port to Multnomah County."),
        ],
    },
    {
        "evidence_id": "ev:mar_17_18_waterleaf_nearly_three_months_statement",
        "date": "2026-03-17",
        "certainty": "high",
        "weight": 0.82,
        "polarity": "supports_transfer_delay_theory",
        "summary": "On March 17 and 18, 2026, Benjamin wrote that HACC was preventing the household from leaving for Waterleaf in Multnomah County and that he had been asking to live at Waterleaf for nearly three months.",
        "actors": ["person:benjamin_barber", "org:hacc", "person:jane_cortez"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_3.eml"),
            _source("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-18_additional-info_bwilliams_1.eml"),
        ],
    },
    {
        "evidence_id": "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher",
        "date": "2026-03-25",
        "certainty": "high",
        "weight": 0.87,
        "polarity": "supports_transfer_delay_theory",
        "summary": "In the March 25-26 HCV orientation thread, Benjamin told HACC that he had contacted Waterleaf in Portland and that the household had been put #4 on the waiting list for a two-bedroom apartment pending issuance of the voucher by HACC.",
        "actors": ["person:benjamin_barber", "org:hacc", "person:jane_cortez"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0020-Re-HCV-Orientation-CAMTdTS8wxYC9a01Qyhgzhk7C19ocZ2gpEc-P78V_wRTQkDN7hg-mail.gmail.com/message.json"),
        ],
    },
    {
        "evidence_id": "ev:jan_12_county_scaring_jane_statement",
        "date": "2026-01-12",
        "certainty": "moderate_to_high",
        "weight": 0.7,
        "polarity": "supports_interference_theory",
        "summary": "Benjamin told HACC that a Clackamas County employee identified as Jamila had been scaring Jane about losing Section 8 if she left Clackamas County.",
        "actors": ["person:benjamin_barber", "person:jane_cortez", "person:jamila", "org:hacc", "org:clackamas_social_services"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-confirmed-case-import/0003-RE-Allegations-of-Fraud---JC-Household-72787eff4e5c4548bd1588bd9666f7c6-clackamas.us/message.json"),
        ],
    },
    {
        "evidence_id": "ev:jan_27_one_bedroom_consequence",
        "date": "2026-01-29",
        "certainty": "high",
        "weight": 0.9,
        "polarity": "supports_violation_theory",
        "summary": "On January 29, 2026, HACC advised that the reported household composition meant the household would now be eligible for a one-bedroom voucher instead of a two-bedroom voucher, and on March 19, 2026, HACC wrote that the previously created two-bedroom subsidy worksheet and voucher issuance were sent in error and that a one-bedroom voucher would instead be issued.",
        "actors": ["org:hacc", "person:jane_cortez", "person:benjamin_barber"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml", "January 29, 2026 Ashley Ferron email stating that the reported household composition makes the household eligible for a one-bedroom voucher instead of a two-bedroom voucher."),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0015-Re-HCV-Orientation-CAMTdTS903KFx0s3rDCjW9LgXd-RbbO9U68sxDE7W-qAkfxCPOw-mail.gmail.com/message.eml", "March 24, 2026 preserved thread quoting Kati Tilton's March 19 statement that the two-bedroom worksheet and issuance were created in error and that a one-bedroom voucher would be issued."),
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/full-evidence-review-run/chronology/emergency_motion_packet/exhibits/Exhibit M - starworks5-ktilton-orientation-import/0008-Re-HCV-Orientation-CAMTdTS_hM81x2YFGZBGX3tGzBJjMjn5WhiFW-NwOC0k23-63LQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/emergency_motion_packet/exhibits/Exhibit M - starworks5-ktilton-orientation-import/0007-RE-HCV-Orientation-f9ca224dab4a4487bb20b9f7ff33afbe-clackamas.us/message.json"),
        ],
    },
    {
        "evidence_id": "ev:feb_4_for_cause_notice_exists",
        "date": "2026-02-04",
        "certainty": "high",
        "weight": 0.84,
        "polarity": "supports_notice_theory",
        "summary": "HACC issued a February 4, 2026 30-day for-cause lease termination notice with option to cure addressed to Jane Cortez and Benjamin Barber.",
        "actors": ["org:hacc", "person:jane_cortez", "person:benjamin_barber"],
        "kind": "termination_notice",
        "sources": [
            _source("/home/barberb/HACC/evidence/paper documents/HACC first amendment.pdf"),
        ],
    },
    {
        "evidence_id": "ev:feb_4_termination_notice_vawa_packet_served",
        "date": "2026-02-04",
        "certainty": "high",
        "weight": 0.93,
        "polarity": "supports_compliance_theory",
        "summary": "The February 4, 2026 cure-or-termination packet expressly states that it includes the VAWA notice, and the preserved attachment contains HUD-5380 and HUD-5382 appended to the notice.",
        "actors": ["org:hacc"],
        "kind": "notice_packet",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-confirmed-case-import-cli/0002-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/attachments/2026.02.04_Cortez_Remedy-Behavior.pdf", "February 4, 2026 cure-or-termination notice stating that it includes the VAWA notice, with HUD-5380 and HUD-5382 attached in the packet."),
            _source("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-02-04_allegations-of-fraud_notice-retaliation_hacc.eml", "Preserved February 4, 2026 transmitting email attaching the cure-or-termination packet and stating that it would also be mailed."),
        ],
    },
    {
        "evidence_id": "ev:mar_17_inspection_notice_for_march_23",
        "date": "2026-03-17",
        "certainty": "high",
        "weight": 0.75,
        "polarity": "supports_notice_theory",
        "summary": "HACC issued a March 17, 2026 notice to residents stating that a HUD NSPIRE inspection would occur on Monday, March 23, 2026.",
        "actors": ["org:hacc"],
        "kind": "inspection_notice",
        "sources": [
            _source("/home/barberb/HACC/evidence/paper documents/HACC inspection.pdf"),
        ],
    },
    {
        "evidence_id": "ev:solomon_restraining_order_and_hacc_notice_gap",
        "date": "2025-11-20",
        "certainty": "moderate",
        "weight": 0.56,
        "polarity": "supports_interference_theory",
        "summary": "The record strongly supports that a restraining order against Solomon Samuel Barber was granted on November 20, 2025, but the present preserved HACC communications do not yet show the first exact named notice to HACC about that order.",
        "actors": ["person:solomon_barber", "org:hacc"],
        "kind": "record_summary",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/docs/protective_order_and_hacc_notice_timeline.md"),
        ],
    },
    {
        "evidence_id": "ev:nov_19_20_solomon_actual_notice_of_order",
        "date": "2025-11-20",
        "certainty": "high",
        "weight": 0.84,
        "polarity": "supports_interference_theory",
        "summary": "The text-export record shows Solomon had actual notice of the restraining-order filing by November 19, 2025 and grant by November 20, 2025.",
        "actors": ["person:solomon_barber"],
        "kind": "text_message_record",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14161-Me-to-solomon-gv-b2df7cbf8706d9fe/transcript.txt"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt"),
        ],
    },
    {
        "evidence_id": "ev:mar_10_solomon_noncompliance_posture",
        "date": "2026-03-10",
        "certainty": "high",
        "weight": 0.76,
        "polarity": "supports_interference_theory",
        "summary": "The March 10, 2026 text thread shows Solomon stating he was not incentivized to cooperate and would comply only once he thought the order went into effect.",
        "actors": ["person:solomon_barber"],
        "kind": "text_message_record",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt"),
        ],
    },
    {
        "evidence_id": "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties",
        "date": "2026-03-17",
        "certainty": "high",
        "weight": 0.66,
        "polarity": "supports_notice_theory",
        "summary": "Benjamin expressly asked HACC whether it was still in communication with parties that had restraining orders against them in the courts.",
        "actors": ["person:benjamin_barber", "org:hacc"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_3.eml"),
        ],
    },
    {
        "evidence_id": "ev:mar_25_26_hacc_warned_about_brother_calls_and_third_party_contact",
        "date": "2026-03-25",
        "certainty": "high",
        "weight": 0.74,
        "polarity": "supports_notice_theory",
        "summary": "In the HCV orientation thread, Benjamin told HACC that Jane was still getting phone calls about his brother, who was under a restraining order, and objected to third-party contact about her housing with a person against whom she had a court-issued restraining order.",
        "actors": ["person:benjamin_barber", "person:jane_cortez", "person:solomon_barber", "org:hacc"],
        "kind": "email_statement",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0025-Re-HCV-Orientation-CAMTdTS8NwnM6aAhiY-HeY2Bs4EosOn2W790KYdvq-tzDKZUwPQ-mail.gmail.com/message.eml"),
        ],
    },
    {
        "evidence_id": "ev:lease_removal_reason_and_hearing_gap",
        "date": "2026-01-01",
        "certainty": "moderate",
        "weight": 0.58,
        "polarity": "supports_due_process_violation_theory",
        "summary": "The current assembled record now shows that HACC gave a bare household-composition explanation for Benjamin's lease removal and that the lease amendment itself appears to include explanation-and-hearing language, but the record still does not show whether that process was clearly served, understood, or actually made available in a meaningful way for Benjamin's challenge to the household-composition change.",
        "actors": ["org:hacc", "person:benjamin_barber"],
        "kind": "record_summary",
        "sources": [
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0025-Re-HCV-Orientation-CAMTdTS8NwnM6aAhiY-HeY2Bs4EosOn2W790KYdvq-tzDKZUwPQ-mail.gmail.com/message.eml"),
            _source("/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf"),
            _source("/home/barberb/HACC/evidence/paper documents/HACC 90 day notice 2.pdf"),
            _source("/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0011-RE-Allegations-of-Fraud---JC-Household-c714b4b1e07348b08e939bd0c8f10431-clackamas.us/attachments/CORTEZ-JANE-7459-PH-LEASE-RIDER-WITH-SIGNATURE-1-.pdf"),
        ],
    },
    {
        "evidence_id": "ev:hacc_policy_notice_packet",
        "date": "2025-07-01",
        "certainty": "high",
        "weight": 0.96,
        "polarity": "supports_rule_baseline",
        "summary": "HACC's own July 1, 2025 administrative plan states that HACC will send HUD-5382 and HUD-5380 with termination notices and request any VAWA claim within 14 business days.",
        "actors": ["org:hacc"],
        "kind": "policy_text",
        "sources": [
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/workspace-generated/evidence/did-key-legacy-temporary-session/local-import/0001_8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt", "Adminplan 7/1/2025, termination notice and VAWA packet passages"),
        ],
    },
    {
        "evidence_id": "ev:hacc_policy_documentation_options",
        "date": "2025-07-01",
        "certainty": "high",
        "weight": 0.95,
        "polarity": "supports_rule_baseline",
        "summary": "HACC's policy text says any VAWA documentation request must be in writing, give 14 business days, and describe three acceptable documentation forms.",
        "actors": ["org:hacc"],
        "kind": "policy_text",
        "sources": [
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/workspace-generated/evidence/did-key-legacy-temporary-session/local-import/0001_8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt", "Adminplan 7/1/2025, VAWA documentation section"),
        ],
    },
    {
        "evidence_id": "ev:hacc_policy_transfer_plan_and_records",
        "date": "2025-07-01",
        "certainty": "high",
        "weight": 0.94,
        "polarity": "supports_rule_baseline",
        "summary": "HACC's policy materials say HACC has adopted an emergency transfer plan and must keep confidential records of emergency transfer requests and outcomes.",
        "actors": ["org:hacc"],
        "kind": "policy_text",
        "sources": [
            _source("/home/barberb/HACC/workspace/temporary-cli-session-migration/workspace-generated/evidence/did-key-legacy-temporary-session/local-import/0001_8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt/8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt", "Adminplan 7/1/2025, record-management and emergency transfer passages"),
        ],
    },
    {
        "evidence_id": "ev:quantum_direct_vawa_gap",
        "date": "2026-04-05",
        "certainty": "moderate",
        "weight": 0.72,
        "polarity": "supports_nonfault_or_gap",
        "summary": "The present folder record does not yet show a direct Quantum communication requesting VAWA documentation, serving VAWA notices, or making the bifurcation decision itself.",
        "actors": ["org:quantum"],
        "kind": "absence_in_record",
        "sources": [
            _source("/home/barberb/HACC/Breach of Contract/docs/vawa_breach_analysis_quantum_hacc.md"),
            _source("/home/barberb/HACC/Breach of Contract/docs/quantum_pattern_and_practice_delay_analysis.md"),
        ],
    },
]


def _normalize_token(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_") or "unknown"


def _evidence_map() -> Dict[str, Dict[str, Any]]:
    return {item["evidence_id"]: item for item in EVIDENCE}


def _party_name(party_id: str) -> str:
    return PARTIES[party_id].name


def _make_events() -> List[Dict[str, Any]]:
    return [
        {
            "event_id": "evt_oct_2025_bifurcation_request",
            "date": "2025-10-15",
            "label": "Bifurcation and abuse-protection request raised with HACC",
            "event_type": "request",
            "actors": ["person:benjamin_barber"],
            "targets": ["org:hacc"],
            "facts": ["Benjamin reported abuse and requested lease bifurcation.", "HACC allegedly required a restraining order before acting."],
            "evidence_ids": ["ev:oct_2025_bifurcation_request"],
        },
        {
            "event_id": "evt_nov_24_hacc_notice_of_disputed_household_member",
            "date": "2025-11-24",
            "label": "HACC staff requested legal documentation regarding household composition",
            "event_type": "notice",
            "actors": ["person:ashley_ferron", "org:hacc"],
            "targets": ["person:benjamin_barber"],
            "facts": ["HACC was on written notice that Julio's status in the household was disputed."],
            "evidence_ids": ["ev:nov_24_hacc_legal_docs_request"],
        },
        {
            "event_id": "evt_dec_10_challenge_to_lease_adjustment",
            "date": "2025-12-10",
            "label": "Benjamin challenged HACC's December 4 lease adjustment",
            "event_type": "objection",
            "actors": ["person:benjamin_barber"],
            "targets": ["org:hacc"],
            "facts": ["The challenge tied the lease-side action to the Julio court matter."],
            "evidence_ids": ["ev:dec_10_lease_adjustment_objection"],
        },
        {
            "event_id": "evt_jan_1_remove_benjamin_from_lease",
            "date": "2026-01-01",
            "label": "HACC lease amendment removed Benjamin Barber",
            "event_type": "lease_change",
            "actors": ["org:hacc"],
            "targets": ["person:benjamin_barber"],
            "facts": ["The lease amendment names Benjamin as the departing tenant effective January 1, 2026."],
            "evidence_ids": ["ev:jan_1_lease_amendment_remove_benjamin"],
        },
        {
            "event_id": "evt_jan_2026_reason_and_hearing_gap_after_lease_removal",
            "date": "2026-01-01",
            "label": "Benjamin's lease removal proceeded with a bare stated reason and a disputed/unclear hearing path",
            "event_type": "process_gap",
            "actors": ["org:hacc"],
            "targets": ["person:benjamin_barber"],
            "facts": ["The assembled record now shows a bare household-composition explanation and lease-amendment hearing language, but it still does not show whether that process was made meaningfully available or used for the specific lease-side removal challenge."],
            "evidence_ids": ["ev:jan_12_bare_reason_for_benjamin_removal", "ev:jan_1_lease_amendment_contains_hearing_language", "ev:lease_removal_reason_and_hearing_gap"],
        },
        {
            "event_id": "evt_jan_12_survivor_side_reports_separation_need",
            "date": "2026-01-12",
            "label": "Household reported that Jane did not want to live with Julio",
            "event_type": "safety_notice",
            "actors": ["person:benjamin_barber"],
            "targets": ["org:hacc"],
            "facts": ["The household linked the request to a restraining-order path and port-out request."],
            "evidence_ids": ["ev:jan_12_jane_does_not_want_to_live_with_julio", "ev:jan_12_port_out_and_order_notice"],
        },
        {
            "event_id": "evt_dec_2025_to_mar_2026_waterleaf_external_transfer_pursuit",
            "date": "2025-12-23",
            "label": "Household pursued Waterleaf in Multnomah County as an external transfer destination",
            "event_type": "external_transfer_pursuit",
            "actors": ["person:benjamin_barber", "person:jane_cortez"],
            "targets": ["org:hacc"],
            "facts": [
                "The Waterleaf application screenshot shows an application created on December 23, 2025 and on the waitlist by January 28, 2026.",
                "By January 12, 2026, HACC was told that Waterleaf wanted the voucher amount and that Jane had already signed and turned in the application.",
                "By January 26, 2026, HACC acknowledged that the household had chosen to port to Multnomah County.",
                "By March 17-18, 2026, Benjamin wrote that he had been trying to move to Waterleaf for nearly three months.",
                "By March 25-26, 2026, Waterleaf had the household #4 on the waiting list pending issuance of the voucher.",
            ],
            "evidence_ids": [
                "ev:waterleaf_application_created_dec_23_2025",
                "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request",
                "ev:jan_26_hacc_acknowledged_port_to_multnomah",
                "ev:mar_17_18_waterleaf_nearly_three_months_statement",
                "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher",
            ],
        },
        {
            "event_id": "evt_jan_12_hacc_requires_court_doc",
            "date": "2026-01-12",
            "label": "HACC required court documentation to treat Julio as unable to reside in household",
            "event_type": "documentation_request",
            "actors": ["org:hacc", "org:hacc_relocation"],
            "targets": ["person:benjamin_barber", "person:jane_cortez"],
            "facts": ["The request, as preserved, points to court documentation and does not itself show the full written VAWA packet or 14-business-day instructions."],
            "evidence_ids": ["ev:jan_12_hacc_court_doc_requirement"],
        },
        {
            "event_id": "evt_jan_12_county_pressure_statement",
            "date": "2026-01-12",
            "label": "Benjamin reported county-side pressure about losing Section 8 if Jane left Clackamas County",
            "event_type": "pressure_report",
            "actors": ["person:benjamin_barber"],
            "targets": ["org:hacc", "person:jamila", "org:clackamas_social_services"],
            "facts": ["This is not yet a clean direct VAWA breach node by itself, but it may matter as coercion or process interference in the survivor-safety context."],
            "evidence_ids": ["ev:jan_12_county_scaring_jane_statement"],
        },
        {
            "event_id": "evt_jan_27_one_bedroom_consequence",
            "date": "2026-01-29",
            "label": "HACC applied one-bedroom voucher consequence after household change",
            "event_type": "benefit_consequence",
            "actors": ["org:hacc"],
            "targets": ["person:jane_cortez", "person:benjamin_barber"],
            "facts": ["HACC tied the household composition change to a reduction in voucher size."],
            "evidence_ids": ["ev:jan_27_one_bedroom_consequence"],
        },
        {
            "event_id": "evt_feb_4_termination_activity_with_vawa_packet_shown",
            "date": "2026-02-04",
            "label": "February 4 termination activity appears in record with the HUD VAWA packet shown",
            "event_type": "termination_notice",
            "actors": ["org:hacc"],
            "targets": ["person:benjamin_barber", "person:jane_cortez", "person:julio_cortez"],
            "facts": ["The February 4 packet states that it includes the VAWA notice, and the preserved packet contains HUD-5380 and HUD-5382."],
            "evidence_ids": ["ev:feb_4_termination_notice_vawa_packet_served"],
        },
        {
            "event_id": "evt_nov_20_solomon_order_known_but_hacc_notice_gap",
            "date": "2025-11-20",
            "label": "Solomon restraining order existed, but first exact HACC notice timestamp remains unpinned",
            "event_type": "outside_interference_context",
            "actors": ["person:solomon_barber"],
            "targets": ["org:hacc"],
            "facts": ["This event matters as context for outside interference and restraint boundaries, but not yet as a direct housing-provider VAWA duty trigger on the current record."],
            "evidence_ids": ["ev:solomon_restraining_order_and_hacc_notice_gap"],
        },
        {
            "event_id": "evt_nov_20_solomon_had_actual_notice_of_order",
            "date": "2025-11-20",
            "label": "Solomon had actual notice of restraining-order filing and grant",
            "event_type": "court_order_notice",
            "actors": ["person:solomon_barber"],
            "targets": [],
            "facts": ["The text-export record supports actual Solomon-side notice even though first exact named HACC notice remains unpinned."],
            "evidence_ids": ["ev:nov_19_20_solomon_actual_notice_of_order"],
        },
        {
            "event_id": "evt_mar_10_solomon_expressed_noncompliance_posture",
            "date": "2026-03-10",
            "label": "Solomon expressed a noncompliance posture toward the court order",
            "event_type": "interference_context",
            "actors": ["person:solomon_barber"],
            "targets": [],
            "facts": ["Solomon stated he was not incentivized to cooperate and would comply only once he believed the order had gone into effect."],
            "evidence_ids": ["ev:mar_10_solomon_noncompliance_posture"],
        },
        {
            "event_id": "evt_mar_17_hacc_warned_not_to_contact_restrained_parties",
            "date": "2026-03-17",
            "label": "HACC was warned in writing not to communicate with parties who had restraining orders against them",
            "event_type": "notice",
            "actors": ["person:benjamin_barber"],
            "targets": ["org:hacc"],
            "facts": ["This is strong latest-record notice that HACC was being told restrained-party communications were a live concern."],
            "evidence_ids": ["ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties"],
        },
    ]


OBLIGATIONS: List[Dict[str, Any]] = [
    {
        "obligation_id": "obl_hacc_notice_packet",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "serve HUD-5380 and HUD-5382 with denial, admission, and termination notices",
        "legal_basis": "24 C.F.R. § 5.2005(a); HUD Notice PIH 2017-08; HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "Notice-packet nonservice or failure to prove service.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_written_doc_request",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "request VAWA documentation only in writing and allow 14 business days",
        "legal_basis": "24 C.F.R. § 5.2007(a); HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "Documentation request appears narrower than allowed and the full compliant packet is not yet shown.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_accept_alternate_documentation",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "accept any one of the allowed documentation pathways rather than require only a restraining order or court document",
        "legal_basis": "24 C.F.R. § 5.2007(b); HUD VAWA Rights Page; HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "Possible over-demand if HACC treated a restraining order or court document as the only acceptable proof.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_consider_causal_nexus_before_adverse_action",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "consider whether domestic violence, dating violence, sexual assault, or stalking caused or materially contributed to the asserted adverse factor before imposing housing consequences",
        "legal_basis": "24 C.F.R. § 5.2005(b)-(d); Matter of Johnson v. Palumbo; Boston Housing Authority v. Y.A.; HUD Notice PIH 2017-08",
        "trigger_event_ids": ["evt_dec_10_challenge_to_lease_adjustment", "evt_jan_12_survivor_side_reports_separation_need", "evt_jan_27_one_bedroom_consequence"],
        "violation_theory": "If HACC treated the household issue as ordinary composition or rent-compliance drift without analyzing the abuse connection, that strengthens the VAWA breach theory.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_not_apply_heightened_standard_to_victim_side",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "prohibited",
        "action": "apply a more demanding evidentiary or compliance standard to the victim or protected side of the household than it would apply to other tenants",
        "legal_basis": "24 C.F.R. § 5.2005(d)(2); Boston Housing Authority v. Y.A.; Matter of Johnson v. Palumbo",
        "trigger_event_ids": ["evt_jan_12_hacc_requires_court_doc", "evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "The court-document-only request is probative if it functioned as a heightened standard rather than a neutral documentation request allowed by VAWA.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_do_not_penalize_victim",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "prohibited",
        "action": "penalize the protected side of the household because of abuse-related incidents or requests for protection",
        "legal_basis": "24 C.F.R. § 5.2005(b)-(d); 24 C.F.R. § 5.2009(a)",
        "trigger_event_ids": ["evt_oct_2025_bifurcation_request", "evt_jan_1_remove_benjamin_from_lease", "evt_jan_27_one_bedroom_consequence"],
        "violation_theory": "Supported if the January 2026 lease action and voucher consequence effectively burdened the side of the household seeking protection.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_bifurcate_against_perpetrator_only",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "if lease bifurcation is used, direct it against the perpetrator without stripping remaining lawful occupants of protected rights",
        "legal_basis": "24 C.F.R. § 5.2009(a)-(b); HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_oct_2025_bifurcation_request", "evt_jan_1_remove_benjamin_from_lease"],
        "violation_theory": "Supported against HACC more strongly than against Quantum on the current record.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_transfer_plan",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "maintain and use an emergency transfer plan, preserving confidential request and outcome records",
        "legal_basis": "24 C.F.R. § 5.2005(e); HUD VAWA Rights Page; HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "Supported as a process-gap theory if HACC treated the matter only as ordinary relocation paperwork rather than a VAWA safety transfer.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_act_on_external_emergency_transfer_or_port_request_with_reasonable_promptness",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "when a qualifying safety-based request seeks an external transfer or port-out, take concrete steps to process the external emergency transfer route with reasonable promptness rather than let the request drift while eviction pressure continues",
        "legal_basis": "24 C.F.R. § 5.2009; HUD HCV Fair Housing Guidebook Apr. 2025 at pages 12-13; HUD portability guidance; HACC Admin Plan 7/1/2025 emergency transfer plan passages",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need", "evt_dec_2025_to_mar_2026_waterleaf_external_transfer_pursuit"],
        "violation_theory": "Supported as an external-emergency-transfer delay theory where HACC knew Waterleaf in Multnomah County was a live destination yet the voucher and porting path remained stalled for months while move-out pressure intensified.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_confidentiality",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "keep survivor-status information and transfer requests confidential except for narrow permitted disclosures",
        "legal_basis": "24 C.F.R. § 5.2007(c); HUD VAWA Rights Page; HUD Notice PIH 2017-08",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need", "evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "Important but not yet mature on the present record.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_when_notified_of_court_order_must_comply_in_access_and_control_decisions",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "when notified of a protection or restraining order, comply with the court order in decisions concerning access to or control of the unit and household property rights",
        "legal_basis": "34 U.S.C. § 12491(b)(3)(C)(i); 24 C.F.R. § 5.2009(a)-(b); HUD VAWA Rights Page",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need", "evt_mar_17_hacc_warned_not_to_contact_restrained_parties"],
        "violation_theory": "If HACC knew of a relevant restraining order yet let the restrained side influence access, occupancy, or lease-control decisions contrary to the order, that supports a VAWA-adjacent breach theory against HACC rather than Solomon as the direct VAWA violator.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_not_disclose_vawa_or_location_information_to_abusive_or_restrained_actor",
        "actor": "org:hacc",
        "recipient": "person:jane_cortez",
        "modality": "prohibited",
        "action": "disclose survivor-status, transfer information, or dwelling-location information to the abusive or restrained actor except as lawfully required",
        "legal_basis": "34 U.S.C. § 12491(c)(4); 34 U.S.C. § 12491(e)(2); 24 C.F.R. § 5.2007(c); HUD VAWA Rights Page",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need", "evt_nov_20_solomon_order_known_but_hacc_notice_gap", "evt_mar_17_hacc_warned_not_to_contact_restrained_parties"],
        "violation_theory": "If HACC was communicating with Solomon or another restrained actor about household safety, unit, or transfer matters without lawful basis and without disclosure to the protected side, that is stronger as a provider confidentiality theory than as a direct VAWA claim against Solomon.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_not_coerce_or_retaliate_against_person_assisting_vawa_claim",
        "actor": "org:hacc",
        "recipient": "person:benjamin_barber",
        "modality": "prohibited",
        "action": "coerce, intimidate, threaten, interfere with, or retaliate against a person because that person opposed unlawful VAWA-related conduct or assisted another household member in asserting VAWA protections",
        "legal_basis": "34 U.S.C. § 12494(a)-(b); HUD VAWA Rights Page",
        "trigger_event_ids": ["evt_oct_2025_bifurcation_request", "evt_jan_12_survivor_side_reports_separation_need", "evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "This refines Benjamin's role: if he was penalized for helping Jane assert safety protections, that points to HACC-side retaliation or interference rather than Benjamin-side fault.",
        "duty_scope": "direct_housing_provider_duty",
    },
    {
        "obligation_id": "obl_hacc_must_give_brief_written_reason_for_lease_or_assistance_adverse_action",
        "actor": "org:hacc",
        "recipient": "person:benjamin_barber",
        "modality": "obligatory",
        "action": "give a prompt written notice containing at least a brief statement of reasons for a lease-side or assistance-side adverse action affecting the household",
        "legal_basis": "24 C.F.R. § 982.555(c)(2); 42 U.S.C. § 1437d(k); HACC grievance and adverse-action policies",
        "trigger_event_ids": ["evt_jan_1_remove_benjamin_from_lease", "evt_jan_2026_reason_and_hearing_gap_after_lease_removal", "evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "If HACC never gave a concrete official reason after the lease-side removal and after a written explanation was requested, that independently strengthens the inference of arbitrary or pretextual action.",
        "duty_scope": "due_process_or_program_hearing_duty",
    },
    {
        "obligation_id": "obl_hacc_must_offer_hearing_path_for_adverse_action_affecting_assistance_or_occupancy",
        "actor": "org:hacc",
        "recipient": "person:benjamin_barber",
        "modality": "obligatory",
        "action": "offer a hearing path, with deadline and procedures, when HACC takes an adverse action affecting assistance, unit size, or continued occupancy rights",
        "legal_basis": "24 C.F.R. § 982.555(a), (c), (d), (e); 42 U.S.C. § 1437d(k)",
        "trigger_event_ids": ["evt_jan_1_remove_benjamin_from_lease", "evt_jan_27_one_bedroom_consequence", "evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "The lack of any hearing tied to the unexplained January lease removal sharpens the HACC fault theory and undermines any claim that the household was given a fair process before the adverse action stuck.",
        "duty_scope": "due_process_or_program_hearing_duty",
    },
    {
        "obligation_id": "obl_hacc_relocation_route_vawa_request",
        "actor": "org:hacc_relocation",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "route safety-based household separation requests through HACC's VAWA-compliant process rather than only ordinary relocation paperwork",
        "legal_basis": "24 C.F.R. § 5.2005(e); 24 C.F.R. § 5.2007(a)-(c); HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need", "evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "Operational HACC sub-office duty; useful for naming the unit that handled the request even though the legal duty still runs through HACC.",
        "duty_scope": "agency_or_operational_duty",
    },
    {
        "obligation_id": "obl_ashley_ferron_confidentiality_and_routing",
        "actor": "person:ashley_ferron",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "as an HACC agent, handle VAWA-related documentation and household-safety communications consistently with HACC's confidentiality and routing duties",
        "legal_basis": "24 C.F.R. § 5.2007(c); HACC Admin Plan 7/1/2025; agency implementation of HACC duties",
        "trigger_event_ids": ["evt_nov_24_hacc_notice_of_disputed_household_member"],
        "violation_theory": "Derivative agency-level implementation duty, not a separate primary statutory provider status.",
        "duty_scope": "agency_or_operational_duty",
    },
    {
        "obligation_id": "obl_kati_tilton_confidentiality_and_supervisory_handling",
        "actor": "person:kati_tilton",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "as an HACC supervisory or assigned-contact actor, maintain confidentiality and ensure VAWA-related requests are handled through the correct process",
        "legal_basis": "24 C.F.R. § 5.2007(c); HACC Admin Plan 7/1/2025; agency implementation of HACC duties",
        "trigger_event_ids": ["evt_nov_24_hacc_notice_of_disputed_household_member", "evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "Derivative agency-level implementation duty.",
        "duty_scope": "agency_or_operational_duty",
    },
    {
        "obligation_id": "obl_jane_right_to_seek_vawa_protection",
        "actor": "person:jane_cortez",
        "recipient": "org:hacc",
        "modality": "permitted",
        "action": "invoke VAWA occupancy-rights protection, request an emergency transfer, and submit any one allowed documentation path",
        "legal_basis": "24 C.F.R. § 5.2005(a), (e); 24 C.F.R. § 5.2007(b); HUD VAWA Rights Page",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "This is a rights-holder profile entry rather than a breach allegation against Jane.",
        "duty_scope": "protected_person_right",
    },
    {
        "obligation_id": "obl_jane_may_raise_vawa_defense_even_if_notice_was_late",
        "actor": "person:jane_cortez",
        "recipient": "org:hacc",
        "modality": "permitted",
        "action": "raise VAWA protection or defense when domestic violence becomes material to an adverse housing action, even if she did not present the issue at the earliest stage",
        "legal_basis": "Boston Housing Authority v. Y.A.; Matter of Johnson v. Palumbo",
        "trigger_event_ids": ["evt_feb_4_termination_activity_with_vawa_packet_shown"],
        "violation_theory": "This refines Jane's rights-holder status and reduces false negatives where notice first becomes explicit during a later hearing or adverse-action stage.",
        "duty_scope": "protected_person_right",
    },
    {
        "obligation_id": "obl_jane_if_seeking_vawa_relief_must_provide_enough_information_for_provider_determination",
        "actor": "person:jane_cortez",
        "recipient": "org:hacc",
        "modality": "conditional",
        "action": "if seeking provider-side VAWA relief, give enough information for the provider to evaluate whether the adverse factor was caused by protected abuse",
        "legal_basis": "Boston Housing Authority v. Y.A.; HUD Notice PIH 2017-08 § 7.3; 24 C.F.R. § 5.2007(a)-(b)",
        "trigger_event_ids": ["evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "This is not a fault theory against Jane; it clarifies the tenant-side procedural burden that can trigger provider analysis duties.",
        "duty_scope": "conditional_tenant_side_procedure",
    },
    {
        "obligation_id": "obl_benjamin_may_report_and_transmit_household_safety_information",
        "actor": "person:benjamin_barber",
        "recipient": "org:hacc",
        "modality": "permitted",
        "action": "report abuse-related safety facts, transmit household documentation, and request household-protective handling on behalf of the household record",
        "legal_basis": "Record-supported household reporting role; HACC policy contemplates submissions and notice from household members seeking VAWA protection",
        "trigger_event_ids": ["evt_oct_2025_bifurcation_request", "evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "This entry explains Benjamin's role in the graph and why his communications matter to triggering HACC duties.",
        "duty_scope": "household_reporting_role",
    },
    {
        "obligation_id": "obl_benjamin_if_acting_as_household_reporting_actor_must_transmit_enough_information_to_trigger_review",
        "actor": "person:benjamin_barber",
        "recipient": "org:hacc",
        "modality": "conditional",
        "action": "if acting as the reporting household member, transmit enough abuse-related information and available documentation to allow the provider to open a VAWA review",
        "legal_basis": "Boston Housing Authority v. Y.A.; HUD Notice PIH 2017-08 § 7.3; record-supported household reporting role",
        "trigger_event_ids": ["evt_oct_2025_bifurcation_request", "evt_jan_12_survivor_side_reports_separation_need"],
        "violation_theory": "This reduces false positives by distinguishing Benjamin's trigger role from provider-side obligations.",
        "duty_scope": "conditional_tenant_side_procedure",
    },
    {
        "obligation_id": "obl_julio_not_entitled_to_victim_side_vawa_protection_if_he_is_the_perpetrator",
        "actor": "person:julio_cortez",
        "recipient": "org:hacc",
        "modality": "prohibited",
        "action": "claim perpetrator-side immunity from lease bifurcation or assistance termination if he is proved to be the abuse perpetrator",
        "legal_basis": "24 C.F.R. § 5.2009(a); HACC Admin Plan 7/1/2025",
        "trigger_event_ids": ["evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "Contingent on proof that Julio is the perpetrator under the household theory.",
        "duty_scope": "conditional_perpetrator_consequence",
    },
    {
        "obligation_id": "obl_julio_if_he_is_the_protected_person_may_invoke_vawa",
        "actor": "person:julio_cortez",
        "recipient": "org:hacc",
        "modality": "conditional",
        "action": "if he is the protected person rather than the perpetrator, invoke the same VAWA documentation and anti-penalization protections available to other protected household members",
        "legal_basis": "24 C.F.R. § 5.2005(b); 24 C.F.R. § 5.2007(b); 24 C.F.R. § 5.2001",
        "trigger_event_ids": ["evt_jan_12_hacc_requires_court_doc"],
        "violation_theory": "This preserves both branches of the disputed household-facts analysis and reduces false positives against Julio.",
        "duty_scope": "conditional_disputed_household_status",
    },
    {
        "obligation_id": "obl_solomon_no_direct_vawa_provider_duty",
        "actor": "person:solomon_barber",
        "recipient": "org:hacc",
        "modality": "optional",
        "action": "Solomon is not presently encoded as a covered housing provider or provider agent, so mere communication with the landlord does not itself make him a direct VAWA violator on the current record",
        "legal_basis": "24 C.F.R. § 5.2003; 34 U.S.C. § 12491(b)-(e); current record posture",
        "trigger_event_ids": ["evt_nov_20_solomon_order_known_but_hacc_notice_gap", "evt_nov_20_solomon_had_actual_notice_of_order"],
        "violation_theory": "This is a false-positive control: Solomon's conduct may still support protective-order, interference, or inducement theories, but VAWA direct-liability usually runs to covered providers or their agents.",
        "duty_scope": "ancillary_legal_constraint",
    },
    {
        "obligation_id": "obl_solomon_if_he_secretly_induced_provider_action_theory_is_interference_not_direct_vawa",
        "actor": "person:solomon_barber",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if he secretly contacted HACC to influence lease, occupancy, or safety decisions despite the court order, that conduct is better classified as interference or court-order circumvention than as a direct covered-provider VAWA violation",
        "legal_basis": "34 U.S.C. § 12491 allocates direct housing duties to public housing agencies, owners, and managers; current record posture",
        "trigger_event_ids": ["evt_mar_10_solomon_expressed_noncompliance_posture", "evt_nov_20_solomon_order_known_but_hacc_notice_gap"],
        "violation_theory": "This preserves the Solomon theory without mislabeling him as the direct VAWA duty-bearer.",
        "duty_scope": "ancillary_legal_constraint",
    },
    {
        "obligation_id": "obl_quantum_confidentiality",
        "actor": "org:quantum",
        "recipient": "person:jane_cortez",
        "modality": "obligatory",
        "action": "keep any VAWA-submitted information confidential if such information was submitted to or possessed by Quantum",
        "legal_basis": "24 C.F.R. § 5.2007(c); HUD Notice PIH 2017-08",
        "trigger_event_ids": [],
        "violation_theory": "Derivative only; the current folder does not yet show the necessary direct submission or disclosure proof.",
        "duty_scope": "conditional_owner_side_duty",
    },
    {
        "obligation_id": "obl_quantum_if_owner_side_documentation_request_then_written_request_and_alt_docs",
        "actor": "org:quantum",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if Quantum was the owner-side covered provider making a VAWA documentation request, use a written request, allow the response period, and accept any listed documentation path",
        "legal_basis": "24 C.F.R. § 5.2003; 24 C.F.R. § 5.2007(a)-(b); HUD Notice PIH 2017-08; Boston Housing Authority v. Y.A.",
        "trigger_event_ids": [],
        "violation_theory": "This duty exists only if discovery shows Quantum actually handled the documentation step.",
        "duty_scope": "conditional_owner_side_duty",
    },
    {
        "obligation_id": "obl_quantum_if_owner_side_then_no_adverse_action_during_doc_window",
        "actor": "org:quantum",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if Quantum made the documentation request, refrain from owner-side adverse action until the VAWA response window runs",
        "legal_basis": "24 C.F.R. § 5.2007(a); HUD Notice PIH 2017-08",
        "trigger_event_ids": [],
        "violation_theory": "This reduces false negatives by preserving an owner-side theory without assuming the current record already proves it.",
        "duty_scope": "conditional_owner_side_duty",
    },
    {
        "obligation_id": "obl_quantum_if_owner_side_bifurcation_then_target_perpetrator_only",
        "actor": "org:quantum",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if Quantum was the owner-side actor responsible for lease bifurcation or occupancy implementation, target the perpetrator and preserve remaining lawful occupants' rights",
        "legal_basis": "24 C.F.R. § 5.2003; 24 C.F.R. § 5.2009(a)-(b); HUD Notice PIH 2017-08",
        "trigger_event_ids": ["evt_jan_1_remove_benjamin_from_lease"],
        "violation_theory": "The current record does not prove Quantum handled that step, so the duty remains conditional rather than direct.",
        "duty_scope": "conditional_owner_side_duty",
    },
    {
        "obligation_id": "obl_clackamas_social_services_no_primary_vawa_provider_duty_shown",
        "actor": "org:clackamas_social_services",
        "recipient": "person:jane_cortez",
        "modality": "optional",
        "action": "the county social-services side is not presently encoded as the primary HUD-VAWA covered provider, but if it acted as a county or landlord-side agent in the housing process it remains legally constrained in how it may pressure, route, disclose, or implement housing decisions",
        "legal_basis": "Current record posture; agency and implementation context",
        "trigger_event_ids": ["evt_jan_12_county_pressure_statement"],
        "violation_theory": "This keeps county-side actors named as legally constrained implementation participants without overstating primary covered-provider status.",
        "duty_scope": "agency_or_implementation_constraint",
    },
    {
        "obligation_id": "obl_clackamas_social_services_if_it_had_vawa_admin_or_oversight_role_then_confidentiality_and_nonretaliation",
        "actor": "org:clackamas_social_services",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if the county-side entity had responsibility for administration or oversight of VAWA protections in this housing process, keep VAWA information confidential and refrain from retaliatory or coercive interference",
        "legal_basis": "24 C.F.R. § 5.2003; 24 C.F.R. § 5.2007(c); HUD FHEO Notice 2023-01",
        "trigger_event_ids": ["evt_jan_12_county_pressure_statement"],
        "violation_theory": "This is a conditional covered-provider or program-participant theory that turns on the actual county role in the housing administration chain.",
        "duty_scope": "conditional_county_side_duty",
    },
    {
        "obligation_id": "obl_county_agents_must_not_coerce_or_misroute_safety_requests",
        "actor": "person:jamila",
        "recipient": "person:jane_cortez",
        "modality": "prohibited",
        "action": "as a county-side or landlord-side agent participating in the housing process, pressure or misroute the household in a way that undermines safety-based housing protections",
        "legal_basis": "Agency and implementation context derived from the housing-administration record; relevant to whether safety requests were frustrated rather than lawfully routed",
        "trigger_event_ids": ["evt_jan_12_county_pressure_statement"],
        "violation_theory": "This is not framed as a primary covered-provider VAWA notice duty, but as a potentially unlawful interference or coercive implementation role relevant to the VAWA analysis.",
        "duty_scope": "agency_or_implementation_constraint",
    },
    {
        "obligation_id": "obl_jamila_if_acting_in_housing_admin_chain_must_not_disclose_or_discourage_vawa_use",
        "actor": "person:jamila",
        "recipient": "person:jane_cortez",
        "modality": "conditional",
        "action": "if acting in the housing-administration chain, not disclose survivor information unnecessarily and not discourage, misstate, or retaliate against the use of VAWA protections",
        "legal_basis": "24 C.F.R. § 5.2003; 24 C.F.R. § 5.2007(c); HUD FHEO Notice 2023-01",
        "trigger_event_ids": ["evt_jan_12_county_pressure_statement"],
        "violation_theory": "This remains conditional because the current file does not yet fully prove Jamila's exact administrative authority.",
        "duty_scope": "conditional_county_side_duty",
    },
]


FINDINGS: List[Dict[str, Any]] = [
    {
        "finding_id": "finding_hacc_primary_vawa_exposure",
        "subject": "org:hacc",
        "status": "supported",
        "confidence": 0.86,
        "headline": "HACC is the primary VAWA exposure point on the current record.",
        "why": [
            "HUD allocates the primary VAWA notice-of-rights duty to the PHA for HCV/public-housing contexts.",
            "The preserved record ties HACC directly to the January 2026 household-composition, documentation, and voucher-size consequences.",
            "HACC's own policy text matches the federal duties that the present record suggests were not followed cleanly.",
            "Caselaw reinforces that the provider handling the adverse action must examine the abuse connection and may not substitute a heightened standard for VAWA-compliant review.",
        ],
        "evidence_ids": [
            "ev:hacc_policy_notice_packet",
            "ev:hacc_policy_documentation_options",
            "ev:jan_1_lease_amendment_remove_benjamin",
            "ev:jan_12_hacc_court_doc_requirement",
            "ev:jan_27_one_bedroom_consequence",
        ],
    },
    {
        "finding_id": "finding_hacc_notice_packet_service_shown",
        "subject": "org:hacc",
        "status": "supported",
        "confidence": 0.92,
        "headline": "The February 4 HACC termination packet appears to have included the required VAWA notice forms.",
        "why": [
            "HACC policy says HUD-5380 and HUD-5382 must go with termination notices.",
            "The preserved February 4 cure-or-termination packet expressly states that it includes the VAWA notice.",
            "The preserved packet contains HUD-5380 and HUD-5382, so the earlier missing-packet theory is not supported on this record.",
        ],
        "evidence_ids": ["ev:hacc_policy_notice_packet", "ev:feb_4_termination_notice_vawa_packet_served"],
    },
    {
        "finding_id": "finding_hacc_documentation_overdemand",
        "subject": "org:hacc",
        "status": "supported",
        "confidence": 0.75,
        "headline": "HACC appears to have asked for narrower proof than VAWA allows.",
        "why": [
            "The preserved January 12 message asks for court documentation showing that Julio could not reside in the household.",
            "Federal and HACC policy text allow multiple documentation forms and require a written request with a 14-business-day window.",
            "The present record does not yet show the compliant written request packet that would cure that problem.",
            "Boston Housing Authority v. Y.A. and Johnson v. Palumbo both support looking past rigid proof formalism when abuse-related facts are materially in play.",
        ],
        "evidence_ids": [
            "ev:jan_12_hacc_court_doc_requirement",
            "ev:hacc_policy_documentation_options",
        ],
    },
    {
        "finding_id": "finding_hacc_survivor_penalization",
        "subject": "org:hacc",
        "status": "supported_if_household_theory_proved",
        "confidence": 0.69,
        "headline": "The strongest HACC VAWA theory is survivor-side penalization through lease and voucher actions.",
        "why": [
            "The record supports an October 2025 abuse-protection request, a January 1, 2026 lease removal of Benjamin, and a January 27 voucher-size consequence after the household change.",
            "If those actions destabilized the side of the household seeking protection while preserving or centering the alleged abuser's status, that fits the core anti-penalization logic of VAWA.",
            "This remains partly contingent because the survivor/perpetrator allocation still depends on proof of the underlying household facts.",
        ],
        "evidence_ids": [
            "ev:oct_2025_bifurcation_request",
            "ev:jan_1_lease_amendment_remove_benjamin",
            "ev:jan_12_jane_does_not_want_to_live_with_julio",
            "ev:jan_27_one_bedroom_consequence",
        ],
    },
    {
        "finding_id": "finding_hacc_transfer_process_gap",
        "subject": "org:hacc",
        "status": "supported",
        "confidence": 0.67,
        "headline": "HACC likely has an emergency-transfer process gap theory against it.",
        "why": [
            "The record shows a safety-separation request and a port-out request.",
            "HACC policy says it has an emergency transfer plan and must keep records of requests and outcomes.",
            "The present folder does not yet show that HACC routed the matter through that process.",
        ],
        "evidence_ids": [
            "ev:jan_12_port_out_and_order_notice",
            "ev:hacc_policy_transfer_plan_and_records",
        ],
    },
    {
        "finding_id": "finding_hacc_external_transfer_delay_theory_supported",
        "subject": "org:hacc",
        "status": "supported",
        "confidence": 0.78,
        "headline": "The record supports a Waterleaf-based external emergency-transfer delay theory against HACC.",
        "why": [
            "The Waterleaf application screenshot shows the household was pursuing Waterleaf by December 23, 2025 and on the waitlist by January 28, 2026.",
            "By January 12, 2026, HACC was told Waterleaf wanted the voucher amount and that the application had already been signed and turned in.",
            "By January 26, 2026, HACC acknowledged the household had chosen to port to Multnomah County.",
            "Benjamin wrote on March 17 and March 18 that he had been trying to move to Waterleaf for nearly three months, and on March 25-26 that Waterleaf had the household #4 on the waiting list pending issuance of the voucher.",
            "This does not prove a short fixed statutory deadline, but it strongly supports the theory that HACC did not act with reasonable promptness on an external safety-based transfer path while continuing move-out pressure.",
        ],
        "evidence_ids": [
            "ev:waterleaf_application_created_dec_23_2025",
            "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request",
            "ev:jan_26_hacc_acknowledged_port_to_multnomah",
            "ev:mar_17_18_waterleaf_nearly_three_months_statement",
            "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher",
        ],
    },
    {
        "finding_id": "finding_quantum_direct_vawa_theory_weak",
        "subject": "org:quantum",
        "status": "weak_on_current_record",
        "confidence": 0.34,
        "headline": "A direct primary VAWA claim against Quantum is presently weak.",
        "why": [
            "HUD guidance places the primary notice duty on the PHA, not the owner, in the HCV/public-housing context.",
            "The current folder does not yet show Quantum requesting VAWA documentation, serving VAWA rights notices, or making the bifurcation decision.",
            "Quantum remains relevant as a possible derivative participant if discovery ties it to confidentiality, occupancy implementation, or retaliatory housing access consequences.",
            "McCoy is a caution against inferring direct VAWA fault where the record has not yet linked the actor to the actual covered action.",
        ],
        "evidence_ids": ["ev:quantum_direct_vawa_gap"],
    },
    {
        "finding_id": "finding_solomon_direct_vawa_theory_weak",
        "subject": "person:solomon_barber",
        "status": "weak_on_current_record",
        "confidence": 0.24,
        "headline": "A direct VAWA claim against Solomon is presently weak, even if an interference theory remains live.",
        "why": [
            "VAWA's housing duties run primarily to public housing agencies, owners, managers, and other covered housing providers for the relevant step.",
            "The current record does not yet show Solomon acting as a covered provider or provider agent in HACC's housing administration.",
            "If Solomon contacted HACC despite the court order, that is better framed at present as interference, inducement, or protective-order circumvention unless discovery shows he functioned as an agent in the housing process.",
        ],
        "evidence_ids": [
            "ev:nov_19_20_solomon_actual_notice_of_order",
            "ev:mar_10_solomon_noncompliance_posture",
            "ev:solomon_restraining_order_and_hacc_notice_gap",
        ],
    },
    {
        "finding_id": "finding_hacc_solomon_notice_and_nondisclosure_issue_unresolved",
        "subject": "org:hacc",
        "status": "supported_but_record_gap_remains",
        "confidence": 0.64,
        "headline": "Whether HACC knew of the Solomon order early enough to owe Solomon-specific confidentiality and court-order-compliance duties remains unresolved, but the issue is material.",
        "why": [
            "The present preserved record does not yet pin down the first exact named HACC notice of the Solomon order.",
            "By March 17, 2026, HACC was expressly warned in writing about communications with parties who had restraining orders against them.",
            "By March 25-26, 2026, Benjamin also told HACC that Jane was still receiving calls about his brother and objected to third-party housing contact with a person under a court-issued restraining order.",
            "If earlier discovery shows HACC knew of Solomon's order before acting on lease or occupancy matters, the stronger legal exposure shifts to HACC's confidentiality, court-order-compliance, and nondisclosure duties rather than to Solomon as the direct VAWA violator.",
        ],
        "evidence_ids": [
            "ev:solomon_restraining_order_and_hacc_notice_gap",
            "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties",
            "ev:mar_25_26_hacc_warned_about_brother_calls_and_third_party_contact",
        ],
    },
    {
        "finding_id": "finding_hacc_reason_and_hearing_gap_strengthens_fault",
        "subject": "org:hacc",
        "status": "supported_but_record_gap_remains",
        "confidence": 0.6,
        "headline": "HACC's bare stated reason and the unresolved quality of the lease-amendment review path still strengthen the case against HACC, but less strongly than before.",
        "why": [
            "The assembled record shows a January 1, 2026 lease-side removal of Benjamin and a later January 12 email giving only a bare internal-review and court-documentation explanation for why HACC treated Julio and Jane as the household.",
            "A separate December 23, 2025 termination notice appears to have offered an informal grievance route, and direct OCR now also indicates hearing language on the lease amendment itself, which means the tighter process problem is whether that review path was clearly served and meaningfully available for the January household-composition dispute.",
            "Direct OCR of the lease amendment now indicates the amendment itself told tenants they could request an explanation within 10 days and request a hearing under the Housing Authority grievance procedure.",
            "The remaining process problem is therefore narrower: the current record still does not show whether that review path was clearly served, meaningfully available, or actually honored for Benjamin's challenge to the household-composition change.",
            "That narrower process issue does not by itself prove the underlying VAWA motive, but it still leaves HACC's action looking factually opaque and potentially pretextual.",
        ],
        "evidence_ids": [
            "ev:dec_23_termination_notice_included_grievance_rights",
            "ev:jan_1_lease_amendment_remove_benjamin",
            "ev:jan_1_lease_amendment_contains_hearing_language",
            "ev:jan_12_bare_reason_for_benjamin_removal",
            "ev:lease_removal_reason_and_hearing_gap",
            "ev:feb_4_termination_notice_vawa_packet_served",
        ],
    },
]


PARTY_DEONTIC_PROFILES: List[Dict[str, Any]] = [
    {
        "party_id": "person:benjamin_barber",
        "classification": "household_reporting_actor",
        "directVawaProviderDuty": False,
        "summary": "Benjamin is not the primary covered housing provider. His main role is as the person whose reports and submissions can trigger HACC's duties and preserve the household record, with a conditional burden to convey enough information to open a VAWA review when acting on the household's behalf.",
        "related_obligation_ids": [
            "obl_benjamin_may_report_and_transmit_household_safety_information",
            "obl_benjamin_if_acting_as_household_reporting_actor_must_transmit_enough_information_to_trigger_review",
        ],
    },
    {
        "party_id": "person:jane_cortez",
        "classification": "protected_person_and_rights_holder",
        "directVawaProviderDuty": False,
        "summary": "Jane is primarily modeled as the protected household member and rights-holder to whom HACC and, conditionally, Quantum or other covered participants owe duties. She also carries a conditional procedural burden to provide enough information when seeking provider-side relief.",
        "related_obligation_ids": [
            "obl_jane_right_to_seek_vawa_protection",
            "obl_jane_may_raise_vawa_defense_even_if_notice_was_late",
            "obl_jane_if_seeking_vawa_relief_must_provide_enough_information_for_provider_determination",
        ],
    },
    {
        "party_id": "person:julio_cortez",
        "classification": "conditional_perpetrator_or_disputed_household_member",
        "directVawaProviderDuty": False,
        "summary": "Julio's VAWA position depends on the underlying factual allocation. If he is the perpetrator, VAWA does not shield him from perpetrator-side consequences; if he is the protected person, he may invoke the same protections as any other victim.",
        "related_obligation_ids": [
            "obl_julio_not_entitled_to_victim_side_vawa_protection_if_he_is_the_perpetrator",
            "obl_julio_if_he_is_the_protected_person_may_invoke_vawa",
        ],
    },
    {
        "party_id": "person:solomon_barber",
        "classification": "outside_interference_actor",
        "directVawaProviderDuty": False,
        "summary": "Solomon is not modeled as the primary covered provider or provider agent on the current record. His importance is as a restrained outside actor whose communications may matter to interference, confidentiality, and inducement analysis, while direct VAWA liability remains weak unless discovery ties him into the housing-administration chain.",
        "related_obligation_ids": [
            "obl_solomon_no_direct_vawa_provider_duty",
            "obl_solomon_if_he_secretly_induced_provider_action_theory_is_interference_not_direct_vawa",
        ],
    },
    {
        "party_id": "person:ashley_ferron",
        "classification": "hacc_agent",
        "directVawaProviderDuty": False,
        "summary": "Ashley Ferron is modeled as an HACC agent whose handling of requests and confidentiality can matter as implementation of HACC's duties.",
        "related_obligation_ids": ["obl_ashley_ferron_confidentiality_and_routing"],
    },
    {
        "party_id": "person:kati_tilton",
        "classification": "hacc_agent",
        "directVawaProviderDuty": False,
        "summary": "Kati Tilton is modeled as an HACC supervisory or assigned-contact actor tied to implementation and routing duties, not as a separate covered housing provider.",
        "related_obligation_ids": ["obl_kati_tilton_confidentiality_and_supervisory_handling"],
    },
    {
        "party_id": "person:jamila",
        "classification": "county_side_actor",
        "directVawaProviderDuty": False,
        "summary": "Jamila is not modeled as the primary covered provider, but is treated as a county-side implementation actor whose pressure or steering can still be legally significant and may become a conditional VAWA-duty bearer if discovery shows she acted in the housing-administration chain.",
        "related_obligation_ids": [
            "obl_county_agents_must_not_coerce_or_misroute_safety_requests",
            "obl_jamila_if_acting_in_housing_admin_chain_must_not_disclose_or_discourage_vawa_use",
        ],
    },
    {
        "party_id": "org:hacc",
        "classification": "primary_covered_housing_provider",
        "directVawaProviderDuty": True,
        "summary": "HACC is the main direct VAWA duty-bearer in this record and program context.",
        "related_obligation_ids": [
            "obl_hacc_notice_packet",
            "obl_hacc_written_doc_request",
            "obl_hacc_accept_alternate_documentation",
            "obl_hacc_must_consider_causal_nexus_before_adverse_action",
            "obl_hacc_must_not_apply_heightened_standard_to_victim_side",
            "obl_hacc_do_not_penalize_victim",
            "obl_hacc_bifurcate_against_perpetrator_only",
            "obl_hacc_transfer_plan",
            "obl_hacc_must_act_on_external_emergency_transfer_or_port_request_with_reasonable_promptness",
            "obl_hacc_confidentiality",
            "obl_hacc_when_notified_of_court_order_must_comply_in_access_and_control_decisions",
            "obl_hacc_must_not_disclose_vawa_or_location_information_to_abusive_or_restrained_actor",
            "obl_hacc_must_not_coerce_or_retaliate_against_person_assisting_vawa_claim",
            "obl_hacc_must_give_brief_written_reason_for_lease_or_assistance_adverse_action",
            "obl_hacc_must_offer_hearing_path_for_adverse_action_affecting_assistance_or_occupancy",
        ],
    },
    {
        "party_id": "org:hacc_relocation",
        "classification": "operational_hacc_suboffice",
        "directVawaProviderDuty": False,
        "summary": "HACC Relocation appears as the operational unit through which HACC's duties were carried out or mishandled.",
        "related_obligation_ids": ["obl_hacc_relocation_route_vawa_request"],
    },
    {
        "party_id": "org:hacc_public_housing",
        "classification": "operational_hacc_suboffice",
        "directVawaProviderDuty": False,
        "summary": "HACC Public Housing is included as an operational HACC node for communications and routing, though not yet separately loaded with distinct formulas.",
        "related_obligation_ids": [],
    },
    {
        "party_id": "org:quantum",
        "classification": "conditional_owner_side_participant",
        "directVawaProviderDuty": False,
        "summary": "Quantum is not presently modeled as the primary notice-duty bearer, but may hold conditional owner-side duties if it received VAWA information, made a documentation request, or implemented lease-bifurcation or occupancy-side action.",
        "related_obligation_ids": [
            "obl_quantum_confidentiality",
            "obl_quantum_if_owner_side_documentation_request_then_written_request_and_alt_docs",
            "obl_quantum_if_owner_side_then_no_adverse_action_during_doc_window",
            "obl_quantum_if_owner_side_bifurcation_then_target_perpetrator_only",
        ],
    },
    {
        "party_id": "org:clackamas_social_services",
        "classification": "county_side_actor",
        "directVawaProviderDuty": False,
        "summary": "The county-side social-services or money-management actor is not modeled as the primary covered provider, but is treated as a legally constrained implementation participant and a potential conditional VAWA-duty bearer if it had administration or oversight responsibility for the relevant step.",
        "related_obligation_ids": [
            "obl_clackamas_social_services_no_primary_vawa_provider_duty_shown",
            "obl_clackamas_social_services_if_it_had_vawa_admin_or_oversight_role_then_confidentiality_and_nonretaliation",
        ],
    },
]


FAULT_MATRIX: List[Dict[str, Any]] = [
    {
        "actor": "org:hacc",
        "faultTier": "primary_fault_candidate",
        "faultScore": 0.9,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "low",
        "rationale": "HACC is the primary covered provider and the record directly connects it to notice, documentation, lease-composition, voucher-size, transfer-process, and possible confidentiality or court-order-compliance issues once restrained-party concerns were raised.",
        "supportingEvidenceIds": [
            "ev:hacc_policy_notice_packet",
            "ev:hacc_policy_documentation_options",
            "ev:hacc_policy_transfer_plan_and_records",
            "ev:jan_1_lease_amendment_remove_benjamin",
            "ev:lease_removal_reason_and_hearing_gap",
            "ev:jan_12_hacc_court_doc_requirement",
            "ev:waterleaf_application_created_dec_23_2025",
            "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request",
            "ev:jan_26_hacc_acknowledged_port_to_multnomah",
            "ev:mar_17_18_waterleaf_nearly_three_months_statement",
            "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher",
            "ev:jan_27_one_bedroom_consequence",
            "ev:feb_4_termination_notice_vawa_packet_served",
            "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties",
        ],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "org:hacc_relocation",
        "faultTier": "derivative_fault_candidate",
        "faultScore": 0.69,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "medium",
        "rationale": "The preserved January 12 communications place relocation staff at the operational point where safety and documentation issues were handled.",
        "supportingEvidenceIds": [
            "ev:jan_12_hacc_court_doc_requirement",
            "ev:jan_12_port_out_and_order_notice",
            "ev:hacc_policy_transfer_plan_and_records",
        ],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:ashley_ferron",
        "faultTier": "derivative_fault_candidate",
        "faultScore": 0.58,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "medium",
        "rationale": "Ashley Ferron is tied to legal-document requests and file-routing communications, but the present record does not yet isolate a definitive confidentiality or routing breach by her personally.",
        "supportingEvidenceIds": ["ev:nov_24_hacc_legal_docs_request"],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:kati_tilton",
        "faultTier": "derivative_fault_candidate",
        "faultScore": 0.46,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "medium",
        "rationale": "Kati Tilton appears in supervisory/contact roles, but the current record is thinner as to a specific VAWA-handling breach by her individually.",
        "supportingEvidenceIds": [],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "org:quantum",
        "faultTier": "currently_under_supported",
        "faultScore": 0.29,
        "falsePositiveRisk": "high",
        "falseNegativeRisk": "medium",
        "rationale": "Quantum may carry derivative confidentiality or occupancy-side duties, but the present record does not yet show direct notice, documentation, or bifurcation handling by Quantum.",
        "supportingEvidenceIds": [],
        "limitingEvidenceIds": ["ev:quantum_direct_vawa_gap"],
    },
    {
        "actor": "person:jamila",
        "faultTier": "possible_interference_candidate",
        "faultScore": 0.41,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "medium",
        "rationale": "The county-pressure statement may reflect coercion or misrouting, but it is presently supported by a narrower statement record rather than a full documentary trail.",
        "supportingEvidenceIds": ["ev:jan_12_county_scaring_jane_statement"],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "org:clackamas_social_services",
        "faultTier": "possible_interference_candidate",
        "faultScore": 0.37,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "medium",
        "rationale": "County-side social-services actors may have implementation or pressure-related fault, but the current record does not yet show the full agency chain or decision authority.",
        "supportingEvidenceIds": ["ev:jan_12_county_scaring_jane_statement"],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:solomon_barber",
        "faultTier": "ancillary_interference_candidate",
        "faultScore": 0.31,
        "falsePositiveRisk": "medium",
        "falseNegativeRisk": "high",
        "rationale": "Solomon is legally relevant as a restrained outside actor with actual order notice and a later noncompliance posture, but the present VAWA record still does not show a clean documented HACC-facing communication proving he handled a covered-provider step or directly violated VAWA.",
        "supportingEvidenceIds": [
            "ev:solomon_restraining_order_and_hacc_notice_gap",
            "ev:nov_19_20_solomon_actual_notice_of_order",
            "ev:mar_10_solomon_noncompliance_posture",
        ],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:jane_cortez",
        "faultTier": "not_presently_fault_actor",
        "faultScore": 0.04,
        "falsePositiveRisk": "low",
        "falseNegativeRisk": "low",
        "rationale": "Jane is modeled primarily as the protected person and rights-holder.",
        "supportingEvidenceIds": [],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:benjamin_barber",
        "faultTier": "not_presently_fault_actor",
        "faultScore": 0.08,
        "falsePositiveRisk": "low",
        "falseNegativeRisk": "low",
        "rationale": "Benjamin is modeled primarily as the reporting and triggering actor whose communications matter because they put others on notice.",
        "supportingEvidenceIds": [],
        "limitingEvidenceIds": [],
    },
    {
        "actor": "person:julio_cortez",
        "faultTier": "conditional_fault_actor",
        "faultScore": 0.5,
        "falsePositiveRisk": "high",
        "falseNegativeRisk": "high",
        "rationale": "Julio's VAWA position is highly fact-dependent because the perpetrator/protected-person allocation remains disputed in the current record.",
        "supportingEvidenceIds": ["ev:jan_12_hacc_court_doc_requirement", "ev:jan_12_jane_does_not_want_to_live_with_julio"],
        "limitingEvidenceIds": [],
    },
]


def _build_actor_deontic_matrix() -> List[Dict[str, Any]]:
    actor_to_entries: Dict[str, Dict[str, Any]] = {}
    for obligation in OBLIGATIONS:
        actor_id = obligation["actor"]
        bucket = actor_to_entries.setdefault(
            actor_id,
            {
                "actor": actor_id,
                "actorName": _party_name(actor_id),
                "role": PARTIES[actor_id].role,
                "obligated": [],
                "forbidden": [],
                "permitted": [],
                "restrained": [],
                "conditional": [],
                "legalBases": [],
                "obligationIds": [],
            },
        )
        item = {
            "obligationId": obligation["obligation_id"],
            "action": obligation["action"],
            "legalBasis": obligation["legal_basis"],
            "recipient": obligation["recipient"],
            "dutyScope": obligation.get("duty_scope"),
            "triggerEventIds": obligation["trigger_event_ids"],
        }
        bucket["obligationIds"].append(obligation["obligation_id"])
        if obligation["legal_basis"] not in bucket["legalBases"]:
            bucket["legalBases"].append(obligation["legal_basis"])
        modality = obligation["modality"]
        scope = obligation.get("duty_scope", "")
        if modality == "obligatory":
            bucket["obligated"].append(item)
        elif modality == "prohibited":
            if "conditional" in scope:
                bucket["conditional"].append(item)
            else:
                bucket["forbidden"].append(item)
        elif modality == "permitted":
            bucket["permitted"].append(item)
        elif modality == "optional":
            bucket["restrained"].append(item)
        else:
            bucket["conditional"].append(item)
    for actor_id, party in PARTIES.items():
        actor_to_entries.setdefault(
            actor_id,
            {
                "actor": actor_id,
                "actorName": party.name,
                "role": party.role,
                "obligated": [],
                "forbidden": [],
                "permitted": [],
                "restrained": [],
                "conditional": [],
                "legalBases": [],
                "obligationIds": [],
            },
        )
    return [actor_to_entries[key] for key in sorted(actor_to_entries)]


def _build_frames(
    events: List[Dict[str, Any]],
    obligations: List[Dict[str, Any]],
    findings: List[Dict[str, Any]],
) -> FrameKnowledgeBase:
    kb = FrameKnowledgeBase()
    for party in PARTIES.values():
        kb.add_fact(party.party_id, party.name, "role", party.role, "party_catalog")
    for authority in AUTHORITIES:
        kb.add_fact(authority["authority_id"], authority["label"], "citation", authority["citation"], authority["sourceUrl"])
        for proposition in authority["propositions"]:
            kb.add_fact(authority["authority_id"], authority["label"], "proposition", proposition, authority["sourceUrl"])
    evidence_index = _evidence_map()
    for event in events:
        for actor in event["actors"]:
            kb.add_fact(event["event_id"], event["label"], "actor", _party_name(actor), evidence_index[event["evidence_ids"][0]]["sources"][0]["path"])
        for target in event["targets"]:
            kb.add_fact(event["event_id"], event["label"], "target", _party_name(target), evidence_index[event["evidence_ids"][0]]["sources"][0]["path"])
        kb.add_fact(event["event_id"], event["label"], "date", event["date"], evidence_index[event["evidence_ids"][0]]["sources"][0]["path"])
        for fact in event["facts"]:
            kb.add_fact(event["event_id"], event["label"], "fact", fact, evidence_index[event["evidence_ids"][0]]["sources"][0]["path"])
    for obligation in obligations:
        kb.add_fact(obligation["obligation_id"], obligation["action"], "actor", _party_name(obligation["actor"]), obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "recipient", _party_name(obligation["recipient"]), obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "modality", obligation["modality"], obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "legal_basis", obligation["legal_basis"], obligation["legal_basis"])
        for trigger_id in obligation["trigger_event_ids"]:
            kb.add_fact(obligation["obligation_id"], obligation["action"], "triggered_by", trigger_id, obligation["legal_basis"])
        kb.add_fact(obligation["obligation_id"], obligation["action"], "violation_theory", obligation["violation_theory"], obligation["legal_basis"])
    for finding in findings:
        kb.add_fact(finding["finding_id"], finding["headline"], "subject", _party_name(finding["subject"]), "finding_catalog")
        kb.add_fact(finding["finding_id"], finding["headline"], "status", finding["status"], "finding_catalog")
        kb.add_fact(finding["finding_id"], finding["headline"], "confidence", finding["confidence"], "finding_catalog")
        for reason in finding["why"]:
            kb.add_fact(finding["finding_id"], finding["headline"], "reason", reason, "finding_catalog")
    for profile in PARTY_DEONTIC_PROFILES:
        profile_id = f"profile:{profile['party_id']}"
        kb.add_fact(profile_id, f"Profile for {_party_name(profile['party_id'])}", "classification", profile["classification"], "party_profile_catalog")
        kb.add_fact(profile_id, f"Profile for {_party_name(profile['party_id'])}", "directVawaProviderDuty", profile["directVawaProviderDuty"], "party_profile_catalog")
        kb.add_fact(profile_id, f"Profile for {_party_name(profile['party_id'])}", "summary", profile["summary"], "party_profile_catalog")
        for obligation_id in profile["related_obligation_ids"]:
            kb.add_fact(profile_id, f"Profile for {_party_name(profile['party_id'])}", "relatedObligation", obligation_id, "party_profile_catalog")
    for row in _build_actor_deontic_matrix():
        frame_id = f"deontic_matrix:{row['actor']}"
        kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "role", row["role"], "actor_deontic_matrix")
        for item in row["obligated"]:
            kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "obligated", item["action"], item["legalBasis"])
        for item in row["forbidden"]:
            kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "forbidden", item["action"], item["legalBasis"])
        for item in row["permitted"]:
            kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "permitted", item["action"], item["legalBasis"])
        for item in row["restrained"]:
            kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "restrained", item["action"], item["legalBasis"])
        for item in row["conditional"]:
            kb.add_fact(frame_id, f"Deontic matrix for {row['actorName']}", "conditional", item["action"], item["legalBasis"])
    return kb


def _build_knowledge_graph(events: List[Dict[str, Any]], findings: List[Dict[str, Any]]) -> Dict[str, Any]:
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    for party in PARTIES.values():
        nodes.append({"id": party.party_id, "type": "party", "label": party.name, "role": party.role})
    for authority in AUTHORITIES:
        nodes.append({"id": authority["authority_id"], "type": "authority", "label": authority["label"]})
    evidence_index = _evidence_map()
    for event in events:
        nodes.append({
            "id": event["event_id"],
            "type": "event",
            "label": event["label"],
            "date": event["date"],
            "eventType": event["event_type"],
        })
        for actor in event["actors"]:
            edges.append({"source": actor, "target": event["event_id"], "relation": "did_or_said", "evidence": event["evidence_ids"]})
        for target in event["targets"]:
            edges.append({"source": event["event_id"], "target": target, "relation": "affected", "evidence": event["evidence_ids"]})
        for evidence_id in event["evidence_ids"]:
            evidence = evidence_index[evidence_id]
            nodes.append({
                "id": evidence_id,
                "type": "evidence",
                "label": evidence["summary"],
                "date": evidence["date"],
                "kind": evidence["kind"],
                "weight": evidence.get("weight"),
                "polarity": evidence.get("polarity"),
            })
            edges.append({"source": evidence_id, "target": event["event_id"], "relation": "supports", "evidence": [evidence_id]})
    for obligation in OBLIGATIONS:
        nodes.append({
            "id": obligation["obligation_id"],
            "type": "obligation",
            "label": obligation["action"],
            "modality": obligation["modality"],
        })
        edges.append({"source": obligation["actor"], "target": obligation["obligation_id"], "relation": "owes", "evidence": []})
        edges.append({"source": obligation["obligation_id"], "target": obligation["recipient"], "relation": "protects", "evidence": []})
        for authority in AUTHORITIES:
            if authority["citation"] in obligation["legal_basis"] or authority["label"] in obligation["legal_basis"]:
                edges.append({"source": authority["authority_id"], "target": obligation["obligation_id"], "relation": "governs", "evidence": []})
        for trigger_id in obligation["trigger_event_ids"]:
            edges.append({"source": trigger_id, "target": obligation["obligation_id"], "relation": "triggers_or_tests", "evidence": []})
    for finding in findings:
        nodes.append({
            "id": finding["finding_id"],
            "type": "finding",
            "label": finding["headline"],
            "status": finding["status"],
            "confidence": finding["confidence"],
        })
        edges.append({"source": finding["subject"], "target": finding["finding_id"], "relation": "assessed_for", "evidence": finding["evidence_ids"]})
        for evidence_id in finding["evidence_ids"]:
            edges.append({"source": evidence_id, "target": finding["finding_id"], "relation": "supports", "evidence": [evidence_id]})
    for profile in PARTY_DEONTIC_PROFILES:
        profile_id = f"profile:{profile['party_id']}"
        nodes.append({
            "id": profile_id,
            "type": "deontic_profile",
            "label": f"Deontic profile for {_party_name(profile['party_id'])}",
            "classification": profile["classification"],
            "directVawaProviderDuty": profile["directVawaProviderDuty"],
        })
        edges.append({"source": profile["party_id"], "target": profile_id, "relation": "has_profile", "evidence": []})
        for obligation_id in profile["related_obligation_ids"]:
            edges.append({"source": profile_id, "target": obligation_id, "relation": "maps_to", "evidence": []})
    for item in FAULT_MATRIX:
        node_id = f"fault:{item['actor']}"
        nodes.append({
            "id": node_id,
            "type": "fault_assessment",
            "label": f"Fault assessment for {_party_name(item['actor'])}",
            "faultTier": item["faultTier"],
            "faultScore": item["faultScore"],
            "falsePositiveRisk": item["falsePositiveRisk"],
            "falseNegativeRisk": item["falseNegativeRisk"],
        })
        edges.append({"source": item["actor"], "target": node_id, "relation": "fault_assessed_as", "evidence": item["supportingEvidenceIds"]})
        for evidence_id in item["supportingEvidenceIds"]:
            edges.append({"source": evidence_id, "target": node_id, "relation": "supports_fault_assessment", "evidence": [evidence_id]})
        for evidence_id in item["limitingEvidenceIds"]:
            edges.append({"source": evidence_id, "target": node_id, "relation": "limits_fault_assessment", "evidence": [evidence_id]})
    return {"nodes": nodes, "edges": edges}


def _derive_trigger_date(trigger_event_ids: List[str], event_index: Dict[str, Dict[str, Any]]) -> Optional[str]:
    dates = [event_index[event_id]["date"] for event_id in trigger_event_ids if event_index.get(event_id, {}).get("date")]
    return sorted(dates)[0] if dates else None


def _derive_due_date(obligation_id: str, trigger_date: Optional[str]) -> Optional[str]:
    if not trigger_date:
        return None
    start = datetime.strptime(trigger_date, "%Y-%m-%d")
    if obligation_id == "obl_hacc_written_doc_request":
        return (start + timedelta(days=20)).strftime("%Y-%m-%d")
    if obligation_id == "obl_hacc_accept_alternate_documentation":
        return (start + timedelta(days=20)).strftime("%Y-%m-%d")
    if obligation_id == "obl_hacc_notice_packet":
        return trigger_date
    if obligation_id == "obl_hacc_transfer_plan":
        return (start + timedelta(days=1)).strftime("%Y-%m-%d")
    return None


def _derive_breach_state(obligation: Dict[str, Any], trigger_date: Optional[str], due_date: Optional[str]) -> str:
    if obligation["modality"] in {"permitted", "optional"}:
        return "informational"
    finding_lookup = {
        "obl_hacc_notice_packet": "supported",
        "obl_hacc_written_doc_request": "supported",
        "obl_hacc_accept_alternate_documentation": "supported",
        "obl_hacc_must_consider_causal_nexus_before_adverse_action": "supported_if_household_theory_proved",
        "obl_hacc_must_not_apply_heightened_standard_to_victim_side": "supported",
        "obl_hacc_do_not_penalize_victim": "supported_if_household_theory_proved",
        "obl_hacc_bifurcate_against_perpetrator_only": "supported_if_household_theory_proved",
        "obl_hacc_transfer_plan": "supported",
        "obl_hacc_must_act_on_external_emergency_transfer_or_port_request_with_reasonable_promptness": "supported",
        "obl_hacc_relocation_route_vawa_request": "supported",
        "obl_hacc_confidentiality": "unresolved",
        "obl_hacc_when_notified_of_court_order_must_comply_in_access_and_control_decisions": "unresolved",
        "obl_hacc_must_not_disclose_vawa_or_location_information_to_abusive_or_restrained_actor": "unresolved",
        "obl_hacc_must_not_coerce_or_retaliate_against_person_assisting_vawa_claim": "supported_if_household_theory_proved",
        "obl_hacc_must_give_brief_written_reason_for_lease_or_assistance_adverse_action": "supported_but_record_gap_remains",
        "obl_hacc_must_offer_hearing_path_for_adverse_action_affecting_assistance_or_occupancy": "supported_but_record_gap_remains",
        "obl_ashley_ferron_confidentiality_and_routing": "unresolved",
        "obl_kati_tilton_confidentiality_and_supervisory_handling": "unresolved",
        "obl_julio_not_entitled_to_victim_side_vawa_protection_if_he_is_the_perpetrator": "supported_if_household_theory_proved",
        "obl_quantum_if_owner_side_documentation_request_then_written_request_and_alt_docs": "weak_on_current_record",
        "obl_quantum_if_owner_side_then_no_adverse_action_during_doc_window": "weak_on_current_record",
        "obl_quantum_if_owner_side_bifurcation_then_target_perpetrator_only": "weak_on_current_record",
        "obl_clackamas_social_services_if_it_had_vawa_admin_or_oversight_role_then_confidentiality_and_nonretaliation": "unresolved",
        "obl_county_agents_must_not_coerce_or_misroute_safety_requests": "unresolved",
        "obl_jamila_if_acting_in_housing_admin_chain_must_not_disclose_or_discourage_vawa_use": "unresolved",
        "obl_quantum_confidentiality": "weak_on_current_record",
        "obl_solomon_if_he_secretly_induced_provider_action_theory_is_interference_not_direct_vawa": "unresolved",
    }
    status = finding_lookup.get(obligation["obligation_id"], "unresolved")
    if status in {"supported", "supported_but_record_gap_remains", "supported_if_household_theory_proved"}:
        return "potential_breach"
    if due_date and datetime.strptime(due_date, "%Y-%m-%d") < CURRENT_DATE:
        return "overdue"
    return "undetermined"


def _derive_temporal_status(trigger_date: Optional[str], due_date: Optional[str]) -> str:
    if due_date and datetime.strptime(due_date, "%Y-%m-%d") < CURRENT_DATE:
        return "overdue"
    if trigger_date and datetime.strptime(trigger_date, "%Y-%m-%d") <= CURRENT_DATE:
        return "active"
    return "undated"


def _build_formal_models(events: List[Dict[str, Any]], obligations: List[Dict[str, Any]], frames: FrameKnowledgeBase) -> Dict[str, Any]:
    happens = []
    initiates = []
    holds_at = []
    breaches = []
    tdfol_formulas = []
    event_index = {event["event_id"]: event for event in events}
    for event in events:
        happens.append(f"Happens({_normalize_token(event['event_id'])}, {event['date']})")
    obligation_records: List[Dict[str, Any]] = []
    for obligation in obligations:
        trigger_date = _derive_trigger_date(obligation["trigger_event_ids"], event_index)
        due_date = _derive_due_date(obligation["obligation_id"], trigger_date)
        breach_state = _derive_breach_state(obligation, trigger_date, due_date)
        temporal_status = _derive_temporal_status(trigger_date, due_date)
        action_token = _normalize_token(obligation["action"])
        actor_token = _normalize_token(obligation["actor"])
        recipient_token = _normalize_token(obligation["recipient"])
        modal_symbol = {"obligatory": "O", "prohibited": "F"}.get(obligation["modality"], "P")
        formula = f"{modal_symbol}({actor_token}, {action_token}, {recipient_token})"
        obligation_records.append({
            "obligationId": obligation["obligation_id"],
            "formula": formula,
            "triggerDate": trigger_date,
            "dueDate": due_date,
            "temporalStatus": temporal_status,
            "breachState": breach_state,
        })
        tdfol_formulas.append({
            "obligationId": obligation["obligation_id"],
            "formula": formula,
            "legalBasis": obligation["legal_basis"],
        })
        for event_id in obligation["trigger_event_ids"]:
            initiates.append({
                "obligationId": obligation["obligation_id"],
                "formula": f"Initiates({_normalize_token(event_id)}, ObligationState({actor_token}, {action_token}, {recipient_token}, {temporal_status}), {trigger_date or 'undated'})",
            })
        holds_at.append({
            "obligationId": obligation["obligation_id"],
            "formula": f"HoldsAt(ObligationState({actor_token}, {action_token}, {recipient_token}, {temporal_status}), {CURRENT_DATE.strftime('%Y-%m-%d')})",
        })
        if breach_state in {"potential_breach", "overdue"}:
            breaches.append({
                "obligationId": obligation["obligation_id"],
                "formula": f"HoldsAt(BreachState({actor_token}, {action_token}, {recipient_token}, {breach_state}), {CURRENT_DATE.strftime('%Y-%m-%d')})",
            })
    return {
        "deonticFirstOrderLogic": {
            "predicates": [item["formula"] for item in obligation_records],
            "obligationFormulas": obligation_records,
        },
        "deonticCognitiveEventCalculus": {
            "happens": happens,
            "initiates": initiates,
            "holdsAt": holds_at,
            "breaches": breaches,
        },
        "frameLogic": frames.to_dict(),
        "tdfol": {
            "formulas": tdfol_formulas,
        },
    }


def _build_dependency_graph() -> Dict[str, Any]:
    nodes = [
        "hacc_is_primary_covered_provider",
        "covered_provider_role_is_functional_and_can_be_shared_by_step",
        "quantum_is_owner_side_participant",
        "agency_actor_can_be_derivatively_bound",
        "restrained_actor_can_create_interference_risk",
        "restrained_actor_mere_contact_is_not_direct_vawa_liability",
        "county_or_landlord_side_agent_can_coerce_or_misroute",
        "tenant_may_raise_vawa_late_if_adverse_action_makes_it_material",
        "tenant_must_provide_enough_information_if_seeking_provider_relief",
        "provider_must_assess_causal_nexus_between_abuse_and_adverse_factor",
        "provider_must_not_apply_heightened_standard_to_victim",
        "provider_when_notified_of_court_order_must_comply_with_it",
        "provider_must_not_disclose_vawa_or_location_info_to_abuser",
        "provider_must_not_retaliate_against_person_assisting_vawa_claim",
        "provider_must_state_brief_reasons_for_adverse_action",
        "provider_must_offer_hearing_path_for_covered_adverse_action",
        "provider_must_process_external_emergency_transfer_with_reasonable_promptness",
        "owner_side_documentation_duty_if_owner_requests_docs",
        "owner_side_no_adverse_action_during_doc_window",
        "owner_side_bifurcation_duty_if_owner_handles_lease_step",
        "county_side_vawa_duty_if_admin_or_oversight_role_proved",
        "termination_notice_triggers_vawa_packet",
        "written_request_required",
        "14_business_day_response_required",
        "alternate_documentation_required",
        "victim_penalization_prohibited",
        "bifurcation_must_target_perpetrator",
        "emergency_transfer_plan_required",
        "confidentiality_required",
        "record_shows_hacc_termination_activity",
        "record_shows_hud_5380_5382_packet",
        "record_shows_hacc_requested_court_documentation",
        "record_shows_hacc_removed_benjamin",
        "record_shows_household_sought_safety_separation",
        "record_shows_waterleaf_external_transfer_pursuit",
        "record_shows_one_bedroom_consequence",
        "hacc_notice_packet_service_shown",
        "hacc_documentation_breach_supported",
        "hacc_survivor_penalization_theory_supported",
        "hacc_transfer_process_theory_supported",
        "hacc_external_transfer_delay_theory_supported",
        "quantum_primary_vawa_breach_not_yet_supported",
        "quantum_derivative_participation_theory",
        "county_interference_theory_not_ruled_out",
        "solomon_interference_theory_not_ruled_out",
        "solomon_direct_vawa_theory_not_supported",
        "hacc_solomon_notice_timing_unresolved",
        "jane_late_assertion_not_a_complete_bar",
        "quantum_conditional_owner_side_duties_preserved",
        "fault_false_positive_control",
        "fault_false_negative_control",
    ]
    edges = [
        ["covered_provider_role_is_functional_and_can_be_shared_by_step", "quantum_conditional_owner_side_duties_preserved"],
        ["covered_provider_role_is_functional_and_can_be_shared_by_step", "county_side_vawa_duty_if_admin_or_oversight_role_proved"],
        ["agency_actor_can_be_derivatively_bound", "hacc_transfer_process_theory_supported"],
        ["agency_actor_can_be_derivatively_bound", "quantum_derivative_participation_theory"],
        ["county_or_landlord_side_agent_can_coerce_or_misroute", "county_interference_theory_not_ruled_out"],
        ["restrained_actor_can_create_interference_risk", "solomon_interference_theory_not_ruled_out"],
        ["restrained_actor_mere_contact_is_not_direct_vawa_liability", "solomon_direct_vawa_theory_not_supported"],
        ["tenant_may_raise_vawa_late_if_adverse_action_makes_it_material", "jane_late_assertion_not_a_complete_bar"],
        ["tenant_must_provide_enough_information_if_seeking_provider_relief", "hacc_documentation_breach_supported"],
        ["provider_must_assess_causal_nexus_between_abuse_and_adverse_factor", "hacc_survivor_penalization_theory_supported"],
        ["provider_must_not_apply_heightened_standard_to_victim", "hacc_documentation_breach_supported"],
        ["provider_must_not_apply_heightened_standard_to_victim", "hacc_notice_packet_service_shown"],
        ["provider_when_notified_of_court_order_must_comply_with_it", "hacc_solomon_notice_timing_unresolved"],
        ["provider_when_notified_of_court_order_must_comply_with_it", "hacc_survivor_penalization_theory_supported"],
        ["provider_must_not_disclose_vawa_or_location_info_to_abuser", "hacc_solomon_notice_timing_unresolved"],
        ["provider_must_not_retaliate_against_person_assisting_vawa_claim", "hacc_survivor_penalization_theory_supported"],
        ["provider_must_state_brief_reasons_for_adverse_action", "hacc_notice_packet_service_shown"],
        ["provider_must_state_brief_reasons_for_adverse_action", "fault_false_positive_control"],
        ["provider_must_offer_hearing_path_for_covered_adverse_action", "hacc_notice_packet_service_shown"],
        ["provider_must_offer_hearing_path_for_covered_adverse_action", "hacc_survivor_penalization_theory_supported"],
        ["provider_must_process_external_emergency_transfer_with_reasonable_promptness", "hacc_external_transfer_delay_theory_supported"],
        ["hacc_is_primary_covered_provider", "termination_notice_triggers_vawa_packet"],
        ["termination_notice_triggers_vawa_packet", "hacc_notice_packet_service_shown"],
        ["record_shows_hacc_termination_activity", "hacc_notice_packet_service_shown"],
        ["record_shows_hud_5380_5382_packet", "hacc_notice_packet_service_shown"],
        ["written_request_required", "hacc_documentation_breach_supported"],
        ["14_business_day_response_required", "hacc_documentation_breach_supported"],
        ["alternate_documentation_required", "hacc_documentation_breach_supported"],
        ["record_shows_hacc_requested_court_documentation", "hacc_documentation_breach_supported"],
        ["victim_penalization_prohibited", "hacc_survivor_penalization_theory_supported"],
        ["bifurcation_must_target_perpetrator", "hacc_survivor_penalization_theory_supported"],
        ["record_shows_hacc_removed_benjamin", "hacc_survivor_penalization_theory_supported"],
        ["record_shows_one_bedroom_consequence", "hacc_survivor_penalization_theory_supported"],
        ["emergency_transfer_plan_required", "hacc_transfer_process_theory_supported"],
        ["record_shows_household_sought_safety_separation", "hacc_transfer_process_theory_supported"],
        ["emergency_transfer_plan_required", "hacc_external_transfer_delay_theory_supported"],
        ["record_shows_household_sought_safety_separation", "hacc_external_transfer_delay_theory_supported"],
        ["record_shows_waterleaf_external_transfer_pursuit", "hacc_external_transfer_delay_theory_supported"],
        ["owner_side_documentation_duty_if_owner_requests_docs", "quantum_conditional_owner_side_duties_preserved"],
        ["owner_side_no_adverse_action_during_doc_window", "quantum_conditional_owner_side_duties_preserved"],
        ["owner_side_bifurcation_duty_if_owner_handles_lease_step", "quantum_conditional_owner_side_duties_preserved"],
        ["quantum_is_owner_side_participant", "quantum_derivative_participation_theory"],
        ["quantum_is_owner_side_participant", "quantum_conditional_owner_side_duties_preserved"],
        ["confidentiality_required", "quantum_derivative_participation_theory"],
        ["county_side_vawa_duty_if_admin_or_oversight_role_proved", "county_interference_theory_not_ruled_out"],
        ["jane_late_assertion_not_a_complete_bar", "fault_false_negative_control"],
        ["quantum_conditional_owner_side_duties_preserved", "fault_false_negative_control"],
        ["hacc_solomon_notice_timing_unresolved", "fault_false_negative_control"],
        ["record_shows_hacc_requested_court_documentation", "fault_false_positive_control", "defeater"],
        ["quantum_primary_vawa_breach_not_yet_supported", "fault_false_positive_control"],
        ["solomon_direct_vawa_theory_not_supported", "fault_false_positive_control"],
        ["county_interference_theory_not_ruled_out", "fault_false_negative_control"],
        ["solomon_interference_theory_not_ruled_out", "fault_false_negative_control"],
        ["fault_false_positive_control", "quantum_conditional_owner_side_duties_preserved", "defeater"],
        ["quantum_is_owner_side_participant", "quantum_primary_vawa_breach_not_yet_supported", "defeater"],
        ["hacc_is_primary_covered_provider", "quantum_primary_vawa_breach_not_yet_supported", "defeater"],
    ]
    return {
        "branch": "vawa_hacc_quantum_analysis",
        "activeOutcome": "hacc_primary_vawa_breach_theory_stronger_than_quantum",
        "nodes": nodes,
        "edges": edges,
    }


def _build_dependency_citations(graph: Dict[str, Any]) -> Dict[str, Any]:
    graph_items: List[Dict[str, Any]] = [
        {
            "id": "case:vawa_hacc_quantum",
            "type": "ReasoningCase",
            "caseId": "vawa_hacc_quantum",
            "branch": graph["branch"],
            "activeOutcome": graph["activeOutcome"],
        }
    ]
    for node_id in graph["nodes"]:
        graph_items.append({
            "id": f"node:{node_id}",
            "type": "DependencyNode",
            "nodeId": node_id,
            "label": node_id.replace("_", " "),
        })
    for index, edge in enumerate(graph["edges"], start=1):
        graph_items.append({
            "id": f"edge:{index}",
            "type": "DependencyEdge",
            "edgeId": f"edge_{index}",
            "fromNode": edge[0],
            "toNode": edge[1],
            "edgeRole": edge[2] if len(edge) == 3 else "supports",
        })
    for authority in AUTHORITIES:
        graph_items.append({
            "id": authority["authority_id"],
            "type": "LegalAuthority",
            "label": authority["label"],
            "citation": authority["citation"],
            "weight": "high",
            "jurisdiction": "federal",
            "court": authority["court"],
            "year": authority["year"],
            "pincite": authority["pincite"],
            "sourceUrl": authority["sourceUrl"],
        })
        for idx, proposition in enumerate(authority["propositions"], start=1):
            excerpt_id = f"{authority['authority_id']}:excerpt:{idx}"
            graph_items.append({
                "id": excerpt_id,
                "type": "AuthorityExcerpt",
                "authority": authority["authority_id"],
                "excerptText": proposition,
                "proposition": proposition,
                "excerptKind": "paraphrase",
                "fitKind": "direct",
                "court": authority["court"],
                "year": authority["year"],
                "pincite": authority["pincite"],
                "sourceUrl": authority["sourceUrl"],
            })
    support_pairs = [
        ("hacc_notice_packet_service_shown", "auth:24_cfr_5_2005:excerpt:1"),
        ("hacc_notice_packet_service_shown", "auth:pih_2017_08:excerpt:1"),
        ("hacc_documentation_breach_supported", "auth:24_cfr_5_2007:excerpt:1"),
        ("hacc_documentation_breach_supported", "auth:24_cfr_5_2007:excerpt:2"),
        ("hacc_documentation_breach_supported", "auth:hud_vawa_rights:excerpt:1"),
        ("hacc_documentation_breach_supported", "auth:boston_housing_authority_v_ya:excerpt:4"),
        ("hacc_survivor_penalization_theory_supported", "auth:24_cfr_5_2005:excerpt:2"),
        ("hacc_survivor_penalization_theory_supported", "auth:24_cfr_5_2009:excerpt:2"),
        ("hacc_survivor_penalization_theory_supported", "auth:34_usc_12494:excerpt:2"),
        ("hacc_survivor_penalization_theory_supported", "auth:johnson_v_palumbo:excerpt:1"),
        ("hacc_survivor_penalization_theory_supported", "auth:boston_housing_authority_v_ya:excerpt:3"),
        ("hacc_notice_packet_service_shown", "auth:24_cfr_982_555:excerpt:2"),
        ("hacc_notice_packet_service_shown", "auth:42_usc_1437d_k:excerpt:1"),
        ("hacc_transfer_process_theory_supported", "auth:24_cfr_5_2005:excerpt:4"),
        ("hacc_external_transfer_delay_theory_supported", "auth:24_cfr_5_2005:excerpt:4"),
        ("hacc_external_transfer_delay_theory_supported", "auth:34_usc_12491:excerpt:4"),
        ("hacc_solomon_notice_timing_unresolved", "auth:34_usc_12491:excerpt:2"),
        ("hacc_solomon_notice_timing_unresolved", "auth:34_usc_12491:excerpt:3"),
        ("hacc_solomon_notice_timing_unresolved", "auth:34_usc_12491:excerpt:4"),
        ("jane_late_assertion_not_a_complete_bar", "auth:boston_housing_authority_v_ya:excerpt:2"),
        ("quantum_conditional_owner_side_duties_preserved", "auth:24_cfr_5_2003:excerpt:1"),
        ("quantum_conditional_owner_side_duties_preserved", "auth:pih_2017_08:excerpt:4"),
        ("quantum_conditional_owner_side_duties_preserved", "auth:pih_2017_08:excerpt:5"),
        ("quantum_derivative_participation_theory", "auth:pih_2017_08:excerpt:2"),
        ("quantum_derivative_participation_theory", "auth:pih_2017_08:excerpt:3"),
        ("solomon_direct_vawa_theory_not_supported", "auth:24_cfr_5_2003:excerpt:1"),
        ("solomon_direct_vawa_theory_not_supported", "auth:mccoy_v_hano:excerpt:3"),
        ("fault_false_positive_control", "auth:mccoy_v_hano:excerpt:1"),
        ("fault_false_positive_control", "auth:mccoy_v_hano:excerpt:2"),
    ]
    for index, (target, authority_excerpt) in enumerate(support_pairs, start=1):
        authority_id = authority_excerpt.split(":excerpt:")[0]
        graph_items.append({
            "id": f"support:{index}",
            "type": "DependencySupport",
            "supportKind": "authority",
            "findingBucket": "vawa",
            "target": target,
            "authority": authority_id,
            "authorityExcerpt": authority_excerpt,
        })
    return {
        "@context": {
            "id": "@id",
            "type": "@type",
            "court": "court",
            "year": "year",
            "pincite": "pincite",
            "sourceUrl": "sourceUrl",
            "fitKind": "fitKind",
        },
        "@graph": graph_items,
    }


DEPENDENCY_NODE_SUPPORT: Dict[str, Dict[str, List[str]]] = {
    "hacc_is_primary_covered_provider": {
        "authorities": ["auth:24_cfr_5_2003", "auth:pih_2017_08", "auth:34_usc_12491"],
        "evidence": [],
    },
    "covered_provider_role_is_functional_and_can_be_shared_by_step": {
        "authorities": ["auth:24_cfr_5_2003", "auth:boston_housing_authority_v_ya"],
        "evidence": [],
    },
    "quantum_is_owner_side_participant": {
        "authorities": ["auth:24_cfr_5_2003", "auth:pih_2017_08"],
        "evidence": ["ev:quantum_direct_vawa_gap"],
    },
    "agency_actor_can_be_derivatively_bound": {
        "authorities": ["auth:24_cfr_5_2003", "auth:mccoy_v_hano"],
        "evidence": ["ev:nov_24_hacc_legal_docs_request"],
    },
    "restrained_actor_can_create_interference_risk": {
        "authorities": ["auth:34_usc_12494"],
        "evidence": ["ev:solomon_restraining_order_and_hacc_notice_gap", "ev:mar_10_solomon_noncompliance_posture"],
    },
    "restrained_actor_mere_contact_is_not_direct_vawa_liability": {
        "authorities": ["auth:24_cfr_5_2003", "auth:mccoy_v_hano", "auth:34_usc_12491"],
        "evidence": ["ev:solomon_restraining_order_and_hacc_notice_gap"],
    },
    "county_or_landlord_side_agent_can_coerce_or_misroute": {
        "authorities": ["auth:34_usc_12494", "auth:fheo_2023_01"],
        "evidence": ["ev:jan_12_county_scaring_jane_statement"],
    },
    "tenant_may_raise_vawa_late_if_adverse_action_makes_it_material": {
        "authorities": ["auth:boston_housing_authority_v_ya", "auth:johnson_v_palumbo"],
        "evidence": ["ev:feb_4_termination_notice_vawa_packet_served"],
    },
    "tenant_must_provide_enough_information_if_seeking_provider_relief": {
        "authorities": ["auth:boston_housing_authority_v_ya", "auth:24_cfr_5_2007", "auth:34_usc_12491"],
        "evidence": ["ev:jan_12_jane_does_not_want_to_live_with_julio", "ev:jan_12_port_out_and_order_notice"],
    },
    "provider_must_assess_causal_nexus_between_abuse_and_adverse_factor": {
        "authorities": ["auth:boston_housing_authority_v_ya", "auth:johnson_v_palumbo", "auth:24_cfr_5_2005"],
        "evidence": ["ev:dec_10_lease_adjustment_objection", "ev:jan_12_jane_does_not_want_to_live_with_julio"],
    },
    "provider_must_not_apply_heightened_standard_to_victim": {
        "authorities": ["auth:boston_housing_authority_v_ya", "auth:34_usc_12491", "auth:24_cfr_5_2007"],
        "evidence": ["ev:jan_12_hacc_court_doc_requirement"],
    },
    "provider_when_notified_of_court_order_must_comply_with_it": {
        "authorities": ["auth:34_usc_12491", "auth:24_cfr_5_2009"],
        "evidence": ["ev:jan_12_port_out_and_order_notice", "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties"],
    },
    "provider_must_not_disclose_vawa_or_location_info_to_abuser": {
        "authorities": ["auth:34_usc_12491", "auth:24_cfr_5_2007", "auth:hud_vawa_rights"],
        "evidence": ["ev:hacc_policy_transfer_plan_and_records", "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties"],
    },
    "provider_must_not_retaliate_against_person_assisting_vawa_claim": {
        "authorities": ["auth:34_usc_12494"],
        "evidence": ["ev:oct_2025_bifurcation_request", "ev:jan_1_lease_amendment_remove_benjamin"],
    },
    "provider_must_state_brief_reasons_for_adverse_action": {
        "authorities": ["auth:24_cfr_982_555", "auth:42_usc_1437d_k"],
        "evidence": ["ev:lease_removal_reason_and_hearing_gap", "ev:feb_4_termination_notice_vawa_packet_served"],
    },
    "provider_must_offer_hearing_path_for_covered_adverse_action": {
        "authorities": ["auth:24_cfr_982_555", "auth:42_usc_1437d_k"],
        "evidence": ["ev:lease_removal_reason_and_hearing_gap", "ev:jan_27_one_bedroom_consequence", "ev:feb_4_termination_notice_vawa_packet_served"],
    },
    "provider_must_process_external_emergency_transfer_with_reasonable_promptness": {
        "authorities": ["auth:24_cfr_5_2005", "auth:34_usc_12491", "auth:hud_vawa_rights"],
        "evidence": ["ev:hacc_policy_transfer_plan_and_records", "ev:jan_12_port_out_and_order_notice", "ev:waterleaf_application_created_dec_23_2025"],
    },
    "owner_side_documentation_duty_if_owner_requests_docs": {
        "authorities": ["auth:24_cfr_5_2007", "auth:pih_2017_08"],
        "evidence": ["ev:quantum_direct_vawa_gap"],
    },
    "owner_side_no_adverse_action_during_doc_window": {
        "authorities": ["auth:24_cfr_5_2007", "auth:pih_2017_08"],
        "evidence": ["ev:quantum_direct_vawa_gap"],
    },
    "owner_side_bifurcation_duty_if_owner_handles_lease_step": {
        "authorities": ["auth:24_cfr_5_2009", "auth:pih_2017_08"],
        "evidence": ["ev:jan_1_lease_amendment_remove_benjamin", "ev:quantum_direct_vawa_gap"],
    },
    "county_side_vawa_duty_if_admin_or_oversight_role_proved": {
        "authorities": ["auth:24_cfr_5_2003", "auth:fheo_2023_01"],
        "evidence": ["ev:jan_12_county_scaring_jane_statement"],
    },
    "termination_notice_triggers_vawa_packet": {
        "authorities": ["auth:24_cfr_5_2005", "auth:34_usc_12491", "auth:pih_2017_08"],
        "evidence": ["ev:feb_4_termination_notice_vawa_packet_served", "ev:hacc_policy_notice_packet"],
    },
    "written_request_required": {
        "authorities": ["auth:24_cfr_5_2007", "auth:34_usc_12491"],
        "evidence": ["ev:hacc_policy_documentation_options"],
    },
    "14_business_day_response_required": {
        "authorities": ["auth:24_cfr_5_2007", "auth:34_usc_12491"],
        "evidence": ["ev:hacc_policy_documentation_options"],
    },
    "alternate_documentation_required": {
        "authorities": ["auth:24_cfr_5_2007", "auth:hud_vawa_rights", "auth:34_usc_12491"],
        "evidence": ["ev:hacc_policy_documentation_options"],
    },
    "victim_penalization_prohibited": {
        "authorities": ["auth:24_cfr_5_2005", "auth:24_cfr_5_2009", "auth:34_usc_12491"],
        "evidence": ["ev:hacc_policy_notice_packet"],
    },
    "bifurcation_must_target_perpetrator": {
        "authorities": ["auth:24_cfr_5_2009", "auth:34_usc_12491"],
        "evidence": ["ev:oct_2025_bifurcation_request"],
    },
    "emergency_transfer_plan_required": {
        "authorities": ["auth:24_cfr_5_2005", "auth:34_usc_12491", "auth:hud_vawa_rights"],
        "evidence": ["ev:hacc_policy_transfer_plan_and_records"],
    },
    "confidentiality_required": {
        "authorities": ["auth:24_cfr_5_2007", "auth:34_usc_12491", "auth:hud_vawa_rights"],
        "evidence": ["ev:hacc_policy_transfer_plan_and_records"],
    },
    "record_shows_hacc_termination_activity": {"authorities": [], "evidence": ["ev:feb_4_for_cause_notice_exists", "ev:feb_4_termination_notice_vawa_packet_served"]},
    "record_shows_hud_5380_5382_packet": {"authorities": [], "evidence": ["ev:feb_4_termination_notice_vawa_packet_served"]},
    "record_shows_hacc_requested_court_documentation": {"authorities": [], "evidence": ["ev:nov_24_hacc_legal_docs_request", "ev:jan_12_hacc_court_doc_requirement"]},
    "record_shows_hacc_removed_benjamin": {"authorities": [], "evidence": ["ev:jan_1_lease_amendment_remove_benjamin", "ev:jan_12_bare_reason_for_benjamin_removal"]},
    "record_shows_household_sought_safety_separation": {"authorities": [], "evidence": ["ev:jan_12_jane_does_not_want_to_live_with_julio", "ev:jan_12_port_out_and_order_notice"]},
    "record_shows_waterleaf_external_transfer_pursuit": {"authorities": [], "evidence": ["ev:waterleaf_application_created_dec_23_2025", "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request", "ev:jan_26_hacc_acknowledged_port_to_multnomah", "ev:mar_17_18_waterleaf_nearly_three_months_statement", "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher"]},
    "record_shows_one_bedroom_consequence": {"authorities": [], "evidence": ["ev:jan_27_one_bedroom_consequence"]},
    "hacc_notice_packet_service_shown": {"authorities": ["auth:24_cfr_5_2005", "auth:pih_2017_08", "auth:24_cfr_982_555", "auth:42_usc_1437d_k"], "evidence": ["ev:feb_4_termination_notice_vawa_packet_served", "ev:hacc_policy_notice_packet"]},
    "hacc_documentation_breach_supported": {"authorities": ["auth:24_cfr_5_2007", "auth:hud_vawa_rights", "auth:boston_housing_authority_v_ya"], "evidence": ["ev:jan_12_hacc_court_doc_requirement", "ev:hacc_policy_documentation_options"]},
    "hacc_survivor_penalization_theory_supported": {"authorities": ["auth:24_cfr_5_2005", "auth:24_cfr_5_2009", "auth:34_usc_12494", "auth:johnson_v_palumbo", "auth:boston_housing_authority_v_ya"], "evidence": ["ev:oct_2025_bifurcation_request", "ev:jan_1_lease_amendment_remove_benjamin", "ev:jan_12_jane_does_not_want_to_live_with_julio", "ev:jan_12_bare_reason_for_benjamin_removal", "ev:jan_27_one_bedroom_consequence", "ev:lease_removal_reason_and_hearing_gap"]},
    "hacc_transfer_process_theory_supported": {"authorities": ["auth:24_cfr_5_2005"], "evidence": ["ev:jan_12_port_out_and_order_notice", "ev:hacc_policy_transfer_plan_and_records"]},
    "hacc_external_transfer_delay_theory_supported": {"authorities": ["auth:24_cfr_5_2005", "auth:34_usc_12491"], "evidence": ["ev:jan_12_port_out_and_order_notice", "ev:waterleaf_application_created_dec_23_2025", "ev:jan_12_waterleaf_signed_application_and_voucher_amount_request", "ev:jan_26_hacc_acknowledged_port_to_multnomah", "ev:mar_17_18_waterleaf_nearly_three_months_statement", "ev:mar_25_26_waterleaf_waitlist_number_four_pending_voucher", "ev:hacc_policy_transfer_plan_and_records"]},
    "quantum_primary_vawa_breach_not_yet_supported": {"authorities": ["auth:mccoy_v_hano", "auth:pih_2017_08"], "evidence": ["ev:quantum_direct_vawa_gap"]},
    "quantum_derivative_participation_theory": {"authorities": ["auth:pih_2017_08", "auth:24_cfr_5_2003"], "evidence": ["ev:quantum_direct_vawa_gap"]},
    "county_interference_theory_not_ruled_out": {"authorities": ["auth:34_usc_12494", "auth:fheo_2023_01"], "evidence": ["ev:jan_12_county_scaring_jane_statement"]},
    "solomon_interference_theory_not_ruled_out": {"authorities": ["auth:34_usc_12494"], "evidence": ["ev:nov_19_20_solomon_actual_notice_of_order", "ev:mar_10_solomon_noncompliance_posture", "ev:solomon_restraining_order_and_hacc_notice_gap"]},
    "solomon_direct_vawa_theory_not_supported": {"authorities": ["auth:24_cfr_5_2003", "auth:mccoy_v_hano", "auth:34_usc_12491"], "evidence": ["ev:solomon_restraining_order_and_hacc_notice_gap"]},
    "hacc_solomon_notice_timing_unresolved": {"authorities": ["auth:34_usc_12491"], "evidence": ["ev:solomon_restraining_order_and_hacc_notice_gap", "ev:mar_17_hacc_warned_not_to_communicate_with_restrained_parties", "ev:mar_25_26_hacc_warned_about_brother_calls_and_third_party_contact"]},
    "jane_late_assertion_not_a_complete_bar": {"authorities": ["auth:boston_housing_authority_v_ya"], "evidence": ["ev:feb_4_termination_notice_vawa_packet_served"]},
    "quantum_conditional_owner_side_duties_preserved": {"authorities": ["auth:24_cfr_5_2003", "auth:pih_2017_08"], "evidence": ["ev:quantum_direct_vawa_gap"]},
    "fault_false_positive_control": {"authorities": ["auth:mccoy_v_hano"], "evidence": ["ev:quantum_direct_vawa_gap", "ev:solomon_restraining_order_and_hacc_notice_gap"]},
    "fault_false_negative_control": {"authorities": ["auth:24_cfr_5_2003", "auth:34_usc_12494"], "evidence": ["ev:jan_12_county_scaring_jane_statement", "ev:solomon_restraining_order_and_hacc_notice_gap"]},
}


def _classify_grounding(authorities: List[str], evidence: List[str]) -> str:
    if authorities and evidence:
        return "mixed_law_and_fact"
    if authorities:
        return "law_only"
    if evidence:
        return "fact_only"
    return "ungrounded"


def _grounding_strength(authorities: List[str], evidence: List[str], evidence_index: Dict[str, Dict[str, Any]]) -> str:
    evidence_items = [evidence_index[e] for e in evidence if e in evidence_index]
    evidence_source_count = sum(len(item.get("sources", [])) for item in evidence_items)
    evidence_is_multi_source = evidence_source_count >= 2

    if len(authorities) >= 2 and (len(evidence) >= 2 or evidence_is_multi_source):
        return "strong"
    if len(authorities) >= 2 and not evidence:
        return "moderate"
    if (len(evidence) >= 2 or evidence_is_multi_source) and not authorities:
        return "moderate"
    if authorities and evidence:
        return "moderate"
    if authorities or evidence:
        return "weak"
    return "missing"


def _evidence_source_stats(evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    missing_source_paths: List[Dict[str, str]] = []
    evidence_with_single_source: List[str] = []
    evidence_backed_only_by_workspace_summaries: List[str] = []
    evidence_with_missing_source_count = 0
    source_count_total = 0

    for item in evidence_items:
        sources = item.get("sources", [])
        source_count_total += len(sources)
        if len(sources) <= 1:
            evidence_with_single_source.append(item["evidence_id"])
        all_workspace_summary = True if sources else False
        item_has_missing = False
        for source in sources:
            path = source.get("path", "")
            if not path:
                continue
            source_path = Path(path)
            if not source_path.exists():
                item_has_missing = True
                missing_source_paths.append({
                    "evidenceId": item["evidence_id"],
                    "path": path,
                })
            normalized = path.lower()
            if not (
                "/workspace/" in normalized
                and (
                    normalized.endswith(".md")
                    or normalized.endswith(".json")
                    or "did-key" in normalized
                    or "timeline" in normalized
                )
            ):
                all_workspace_summary = False
        if item_has_missing:
            evidence_with_missing_source_count += 1
        if all_workspace_summary and sources:
            evidence_backed_only_by_workspace_summaries.append(item["evidence_id"])

    return {
        "evidenceCount": len(evidence_items),
        "sourceCount": source_count_total,
        "missingSourcePaths": missing_source_paths,
        "evidenceWithSingleSource": evidence_with_single_source,
        "evidenceBackedOnlyByWorkspaceSummaries": evidence_backed_only_by_workspace_summaries,
        "evidenceWithMissingSourceCount": evidence_with_missing_source_count,
    }


def _build_grounding_audit(report: Dict[str, Any]) -> Dict[str, Any]:
    evidence_items = report["evidence"]
    evidence_index = {item["evidence_id"]: item for item in evidence_items}
    authority_index = {item["authority_id"]: item for item in report["authorities"]}
    evidence_source_stats = _evidence_source_stats(evidence_items)
    dependency_nodes: List[Dict[str, Any]] = []
    weak_nodes: List[Dict[str, Any]] = []
    for node_id in report["dependencyGraph"]["nodes"]:
        support = DEPENDENCY_NODE_SUPPORT.get(node_id, {"authorities": [], "evidence": []})
        authorities = support["authorities"]
        evidence = support["evidence"]
        grounding = _classify_grounding(authorities, evidence)
        strength = _grounding_strength(authorities, evidence, evidence_index)
        node_item = {
            "nodeId": node_id,
            "grounding": grounding,
            "strength": strength,
            "authorityIds": authorities,
            "authorityLabels": [authority_index[a]["label"] for a in authorities if a in authority_index],
            "evidenceIds": evidence,
            "evidenceSummaries": [evidence_index[e]["summary"] for e in evidence if e in evidence_index],
        }
        dependency_nodes.append(node_item)
        if strength in {"weak", "missing"}:
            weak_nodes.append(node_item)

    knowledge_graph = report["knowledgeGraph"]
    node_ids_in_edges = {edge["source"] for edge in knowledge_graph["edges"]} | {edge["target"] for edge in knowledge_graph["edges"]}
    orphan_nodes = [node["id"] for node in knowledge_graph["nodes"] if node["id"] not in node_ids_in_edges]
    nodes_without_sources = [
        node["id"]
        for node in knowledge_graph["nodes"]
        if node.get("nodeType") == "evidence"
        and not node.get("sources")
    ]
    weak_findings = []
    for finding in report["findings"]:
        if finding["status"] in {"weak_on_current_record", "unresolved", "supported_but_record_gap_remains"}:
            weak_findings.append({
                "findingId": finding["finding_id"],
                "subject": finding["subject"],
                "status": finding["status"],
                "headline": finding["headline"],
                "evidenceIds": finding["evidence_ids"],
            })

    strengthening_tasks = [
        {
            "taskId": "task_pin_down_solomon_notice_to_hacc",
            "priority": "high",
            "targets": ["hacc_solomon_notice_timing_unresolved", "solomon_interference_theory_not_ruled_out"],
            "why": "The record now shows written March 17 and March 25-26 warnings to HACC about restrained-party communications, but the first exact HACC notice of Solomon's order is still not pinned down.",
            "neededEvidence": [
                "Any November-December 2025 HACC email, call log, visitor log, or case note naming Solomon, Sam Barber, or Samuel Barber.",
                "Metadata or routing records for January 2026 lease-change work showing whether Solomon was a source or subject of staff discussion.",
                "Phone logs or staff notes corresponding to the calls Benjamin reported in the March 25-26 HCV orientation thread.",
            ],
        },
        {
            "taskId": "task_secure_signed_inspection_declarations",
            "priority": "high",
            "targets": ["record_shows_hacc_removed_benjamin", "hacc_survivor_penalization_theory_supported"],
            "why": "The March 23, 2026 inspection statement attributed to Charley Skee is currently strongest as proposed witness testimony and should be converted into signed declarations to strengthen the factual chain without overstating the record.",
            "neededEvidence": [
                "Signed declaration by Benjamin Barber regarding the March 23, 2026 inspection statement.",
                "Signed declaration by Jane Cortez regarding the same March 23, 2026 inspection statement.",
                "Any contemporaneous text, email, note, or calendar entry made shortly after the March 23, 2026 inspection describing what Charley Skee said.",
            ],
        },
        {
            "taskId": "task_tie_charley_skee_statement_to_internal_lease_rationale",
            "priority": "high",
            "targets": ["task_identify_request_source_for_benjamin_removal", "record_shows_hacc_removed_benjamin"],
            "why": "If Charley Skee linked Benjamin's lease removal to outside document flows during the March 23 inspection, the strongest corroboration will be internal HACC records showing the same rationale or discussion path.",
            "neededEvidence": [
                "Internal emails, case notes, or staff diary entries by Charley Skee, Ashley Ferron, HACC PM, or HACC Relocation discussing outside family-member document submissions.",
                "Any lease-change worksheet or CRM entry explaining why Benjamin was removed from the lease.",
                "Visitor logs or inspection notes identifying the staff present during the March 23, 2026 inspection.",
            ],
        },
        {
            "taskId": "task_identify_request_source_for_benjamin_removal",
            "priority": "high",
            "targets": ["record_shows_hacc_removed_benjamin", "hacc_survivor_penalization_theory_supported"],
            "why": "The lease change is proved, but the source of the request or rationale is not.",
            "neededEvidence": [
                "Lease worksheet metadata, CRM notes, staff diary entries, approval chain, and internal emails for the January 1, 2026 amendment.",
                "Any written household request or absence of one.",
            ],
        },
        {
            "taskId": "task_prove_reason_and_hearing_request_history",
            "priority": "high",
            "targets": ["provider_must_state_brief_reasons_for_adverse_action", "provider_must_offer_hearing_path_for_covered_adverse_action"],
            "why": "The current record now shows HACC gave a bare January 12 explanation and that the lease amendment itself appears to include hearing language, so the strongest next proof is whether Benjamin actually received and could use that review path.",
            "neededEvidence": [
                "The exact written request asking for the official reason or fuller factual basis for Benjamin's removal.",
                "Any HACC response, non-response, or grievance/hearing denial record tied specifically to the January lease-side removal.",
                "Mailing records, service notes, or acknowledgments showing whether Benjamin received the lease amendment page containing the explanation-and-hearing language.",
                "Any grievance intake, hearing request, or refusal clarifying whether the lease-amendment review path was actually honored.",
            ],
        },
        {
            "taskId": "task_prove_quantum_owner_side_step_if_any",
            "priority": "medium",
            "targets": ["quantum_conditional_owner_side_duties_preserved", "quantum_primary_vawa_breach_not_yet_supported"],
            "why": "Quantum remains conditional because the record does not show it handled a covered documentation or bifurcation step.",
            "neededEvidence": [
                "Owner-side emails requesting VAWA documentation or discussing lease bifurcation.",
                "Property-management records showing Quantum implemented or directed occupancy consequences.",
            ],
        },
        {
            "taskId": "task_prove_county_admin_chain",
            "priority": "medium",
            "targets": ["county_side_vawa_duty_if_admin_or_oversight_role_proved", "county_interference_theory_not_ruled_out"],
            "why": "County actors are named, but the exact housing-administration role still needs tightening.",
            "neededEvidence": [
                "Program documents linking Money Management / Social Services to housing administration, rent control, or relocation influence.",
                "Direct communications from Jamila or county-side staff about Section 8 consequences or move restrictions.",
            ],
        },
    ]

    return {
        "metadata": {
            "generatedAt": CURRENT_DATE.isoformat(),
            "purpose": "End-to-end grounding audit for dependency and knowledge graphs",
        },
        "dependencyNodeAudit": dependency_nodes,
        "weakDependencyNodes": weak_nodes,
        "weakFindings": weak_findings,
        "knowledgeGraphChecks": {
            "nodeCount": len(knowledge_graph["nodes"]),
            "edgeCount": len(knowledge_graph["edges"]),
            "orphanNodes": orphan_nodes,
            "evidenceNodesWithoutSources": nodes_without_sources,
        },
        "evidenceSourceCoverage": evidence_source_stats,
        "recordStrengtheningTasks": strengthening_tasks,
    }


def _build_grounding_audit_markdown(audit: Dict[str, Any]) -> str:
    lines = [
        "# VAWA Grounding Audit",
        "",
        "## Bottom line",
        "",
        "- This audit checks whether each major dependency node is grounded in law, fact, or both.",
        "- Nodes marked `weak` are not necessarily wrong; they are the places where the record or authority chain still needs reinforcement.",
        "",
        "## Weak dependency nodes",
        "",
    ]
    weak_nodes = audit["weakDependencyNodes"]
    if not weak_nodes:
        lines.append("- No weak dependency nodes were identified.")
    else:
        for item in weak_nodes:
            lines.append(
                f"- `{item['nodeId']}`: grounding `{item['grounding']}`; strength `{item['strength']}`; authorities `{len(item['authorityIds'])}`; evidence `{len(item['evidenceIds'])}`"
            )
    lines.extend([
        "",
        "## Weak findings",
        "",
    ])
    for item in audit["weakFindings"]:
        lines.append(f"- `{item['findingId']}`: `{item['status']}`; {item['headline']}")
    lines.extend([
        "",
        "## Evidence-source checks",
        "",
        f"- Evidence items: `{audit['evidenceSourceCoverage']['evidenceCount']}`",
        f"- Total cited source paths: `{audit['evidenceSourceCoverage']['sourceCount']}`",
        f"- Evidence items with only one cited source: `{len(audit['evidenceSourceCoverage']['evidenceWithSingleSource'])}`",
        f"- Evidence items backed only by workspace summaries: `{len(audit['evidenceSourceCoverage']['evidenceBackedOnlyByWorkspaceSummaries'])}`",
        f"- Missing cited source paths: `{len(audit['evidenceSourceCoverage']['missingSourcePaths'])}`",
        "",
    ])
    lines.extend([
        "",
        "## Record-strengthening tasks",
        "",
    ])
    for task in audit["recordStrengtheningTasks"]:
        lines.append(f"- `{task['taskId']}` (`{task['priority']}`): {task['why']}")
    lines.extend([
        "",
        "## Knowledge-graph checks",
        "",
        f"- Nodes: `{audit['knowledgeGraphChecks']['nodeCount']}`",
        f"- Edges: `{audit['knowledgeGraphChecks']['edgeCount']}`",
        f"- Orphan nodes: `{len(audit['knowledgeGraphChecks']['orphanNodes'])}`",
        f"- Evidence nodes without sources: `{len(audit['knowledgeGraphChecks']['evidenceNodesWithoutSources'])}`",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"


def _build_flogic_export(events: List[Dict[str, Any]], obligations: List[Dict[str, Any]], findings: List[Dict[str, Any]]) -> str:
    lines: List[str] = [
        "%% vawa_case_knowledge_graph.flogic",
        "%% F-logic style export for the HACC / Quantum VAWA record",
        "",
    ]
    for party in PARTIES.values():
        lines.append(f"{_normalize_token(party.party_id)}:party[")
        lines.append(f'  name -> "{party.name}";')
        lines.append(f'  role -> "{party.role}"')
        lines.append("] .")
        lines.append("")
    for event in events:
        lines.append(f"{_normalize_token(event['event_id'])}:event[")
        lines.append(f'  label -> "{event["label"]}";')
        lines.append(f'  date -> "{event["date"]}";')
        actor_values = ", ".join(_normalize_token(actor) for actor in event["actors"])
        target_values = ", ".join(_normalize_token(target) for target in event["targets"])
        evidence_values = ", ".join(f'"{value}"' for value in event["evidence_ids"])
        lines.append(f"  actors ->> {{{actor_values}}};")
        lines.append(f"  targets ->> {{{target_values}}};")
        lines.append(f"  evidenceIds ->> {{{evidence_values}}}")
        lines.append("] .")
        lines.append("")
    for obligation in obligations:
        lines.append(f"{_normalize_token(obligation['obligation_id'])}:obligation[")
        lines.append(f"  actor -> {_normalize_token(obligation['actor'])};")
        lines.append(f"  recipient -> {_normalize_token(obligation['recipient'])};")
        lines.append(f'  modality -> "{obligation["modality"]}";')
        lines.append(f'  actionText -> "{obligation["action"]}";')
        lines.append(f'  legalBasis -> "{obligation["legal_basis"]}"')
        lines.append("] .")
        lines.append("")
    for profile in PARTY_DEONTIC_PROFILES:
        lines.append(f"{_normalize_token('profile_' + profile['party_id'])}:deontic_profile[")
        lines.append(f"  subject -> {_normalize_token(profile['party_id'])};")
        lines.append(f'  classification -> "{profile["classification"]}";')
        lines.append(f"  directVawaProviderDuty -> {str(profile['directVawaProviderDuty']).lower()}")
        lines.append("] .")
        lines.append("")
    for finding in findings:
        lines.append(f"{_normalize_token(finding['finding_id'])}:finding[")
        lines.append(f"  subject -> {_normalize_token(finding['subject'])};")
        lines.append(f'  status -> "{finding["status"]}";')
        lines.append(f"  confidence -> {finding['confidence']}")
        lines.append("] .")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _build_dcec_export(formal_models: Dict[str, Any]) -> str:
    dcec = formal_models["deonticCognitiveEventCalculus"]
    lines: List[str] = [
        "% vawa_case_obligations_dcec.pl",
        "% DCEC-style export for the HACC / Quantum VAWA record",
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
    if dcec["breaches"]:
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
    except Exception as exc:  # pragma: no cover - environment-dependent
        return {
            "available": False,
            "error": str(exc),
            "proofs": [],
        }

    kb = TDFOLKnowledgeBase()
    strategy = ModalTableauxStrategy()
    axioms = {
        "hacc_notice_packet_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ServeVawaNoticePacket", ())),
        "hacc_written_request_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("UseWrittenVawaDocumentationRequest", ())),
        "hacc_alt_doc_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("AcceptAlternativeVawaDocumentation", ())),
        "hacc_causal_nexus_review_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("AssessCausalNexusBeforeAdverseAction", ())),
        "hacc_no_heightened_standard_for_victim": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("ApplyHeightenedStandardToVictim", ())),
        "hacc_victim_penalty_forbidden": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("PenalizeProtectedHouseholdForAbuse", ())),
        "hacc_transfer_plan_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("MaintainEmergencyTransferPlan", ())),
        "hacc_court_order_compliance_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ComplyWithCourtOrderInAccessAndControlDecisions", ())),
        "hacc_no_disclosure_to_abuser_required": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("DiscloseVawaOrLocationInfoToAbuser", ())),
        "hacc_no_retaliation_against_helper": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("RetaliateAgainstPersonAssistingVawaClaim", ())),
        "hacc_brief_reason_notice_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ProvideBriefWrittenReasonForAdverseAction", ())),
        "hacc_hearing_path_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("OfferHearingPathForCoveredAdverseAction", ())),
        "hacc_relocation_route_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("RouteVawaRequestThroughRelocationUnit", ())),
        "hacc_external_transfer_promptness_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("ProcessExternalEmergencyTransferWithReasonablePromptness", ())),
        "ashley_agent_confidentiality_required": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("AshleyFerronHandleVawaInfoConfidentially", ())),
        "county_agent_noncoercion_required": DeonticFormula(DeonticOperator.PROHIBITION, Predicate("CountyAgentCoerceOrMisrouteSafetyRequest", ())),
        "quantum_confidentiality_if_info_received": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("KeepVawaInformationConfidential", ())),
        "quantum_owner_side_documentation_if_requesting": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("QuantumUseWrittenRequestAndAcceptAltDocsIfRequesting", ())),
    }
    for formula in axioms.values():
        kb.add_axiom(formula)

    queries = {
        "hacc_notice_packet_required": axioms["hacc_notice_packet_required"],
        "hacc_written_request_required": axioms["hacc_written_request_required"],
        "hacc_causal_nexus_review_required": axioms["hacc_causal_nexus_review_required"],
        "hacc_no_heightened_standard_for_victim": axioms["hacc_no_heightened_standard_for_victim"],
        "hacc_victim_penalty_forbidden": axioms["hacc_victim_penalty_forbidden"],
        "hacc_court_order_compliance_required": axioms["hacc_court_order_compliance_required"],
        "hacc_no_disclosure_to_abuser_required": axioms["hacc_no_disclosure_to_abuser_required"],
        "hacc_no_retaliation_against_helper": axioms["hacc_no_retaliation_against_helper"],
        "hacc_brief_reason_notice_required": axioms["hacc_brief_reason_notice_required"],
        "hacc_hearing_path_required": axioms["hacc_hearing_path_required"],
        "hacc_relocation_route_required": axioms["hacc_relocation_route_required"],
        "hacc_external_transfer_promptness_required": axioms["hacc_external_transfer_promptness_required"],
        "ashley_agent_confidentiality_required": axioms["ashley_agent_confidentiality_required"],
        "county_agent_noncoercion_required": axioms["county_agent_noncoercion_required"],
        "quantum_owner_side_documentation_if_requesting": axioms["quantum_owner_side_documentation_if_requesting"],
        "quantum_primary_notice_duty": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("QuantumPrimaryNoticeDuty", ())),
        "solomon_direct_provider_duty": DeonticFormula(DeonticOperator.OBLIGATION, Predicate("SolomonDirectProviderDuty", ())),
    }
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
        "note": "The prover audit here validates encoded normative duties and helps distinguish HACC's primary notice duty from Quantum's weaker primary-duty position. It does not, by itself, resolve disputed historical facts.",
    }


def build_case_report() -> Dict[str, Any]:
    events = _make_events()
    actor_deontic_matrix = _build_actor_deontic_matrix()
    frames = _build_frames(events, OBLIGATIONS, FINDINGS)
    formal_models = _build_formal_models(events, OBLIGATIONS, frames)
    dependency_graph = _build_dependency_graph()
    knowledge_graph = _build_knowledge_graph(events, FINDINGS)
    proof_audit = _run_tdfol_audit()
    formal_models["tdfol"]["proofAudit"] = proof_audit
    grounding_audit = _build_grounding_audit({
        "evidence": EVIDENCE,
        "authorities": AUTHORITIES,
        "dependencyGraph": dependency_graph,
        "knowledgeGraph": knowledge_graph,
        "findings": FINDINGS,
    })
    return {
        "metadata": {
            "generatedAt": CURRENT_DATE.isoformat(),
            "caseId": "vawa_hacc_quantum",
            "scope": "VAWA compliance analysis for HACC and Quantum based on current folder record",
            "disclaimer": "Research artifact for issue-spotting and formal analysis. Not legal advice.",
        },
        "parties": {
            party_id: {
                "name": spec.name,
                "role": spec.role,
            }
            for party_id, spec in PARTIES.items()
        },
        "authorities": AUTHORITIES,
        "evidence": EVIDENCE,
        "events": events,
        "obligations": OBLIGATIONS,
        "partyDeonticProfiles": PARTY_DEONTIC_PROFILES,
        "actorDeonticMatrix": actor_deontic_matrix,
        "faultMatrix": FAULT_MATRIX,
        "findings": FINDINGS,
        "knowledgeGraph": knowledge_graph,
        "formalModels": formal_models,
        "dependencyGraph": dependency_graph,
        "groundingAudit": grounding_audit,
    }


def _build_markdown_summary(report: Dict[str, Any]) -> str:
    finding_map = {item["finding_id"]: item for item in report["findings"]}
    lines = [
        "# VAWA Formal Analysis Summary",
        "",
        "## Bottom line",
        "",
        "- HACC is the primary VAWA exposure point on the current record.",
        "- The strongest HACC theories are: notice-packet noncompliance, over-demand for court-only documentation, survivor-side penalization through lease or voucher consequences, and failure to route the matter through a VAWA emergency-transfer process.",
        "- Quantum is not presently as strong a direct VAWA defendant. Quantum remains more plausibly a derivative participant if later discovery ties it to confidentiality misuse, occupancy implementation, or a survivor-specific denial.",
        "",
        "## Formal findings",
        "",
    ]
    for finding_id in [
        "finding_hacc_primary_vawa_exposure",
        "finding_hacc_notice_packet_service_shown",
        "finding_hacc_documentation_overdemand",
        "finding_hacc_survivor_penalization",
        "finding_hacc_transfer_process_gap",
        "finding_quantum_direct_vawa_theory_weak",
    ]:
        finding = finding_map[finding_id]
        lines.append(f"- `{finding['subject']}`: **{finding['headline']}** (`{finding['status']}`, confidence `{finding['confidence']}`)")
    lines.extend([
        "",
        "## Caselaw refinements",
        "",
        "- `Matter of Johnson v. Palumbo` and `Boston Housing Authority v. Y.A.` now explicitly support a causal-nexus inquiry, rejection of heightened proof standards, and the rule that late assertion of VAWA protection is not automatically fatal.",
        "- `McCoy v. HANO` now functions as a false-positive control against blaming an actor for VAWA violations without proof that the actor actually handled the covered adverse action or controlled the relevant owner-side step.",
        "- The graph therefore distinguishes `primary PHA duties` from `conditional owner-side duties` and from `conditional county-side duties` rather than collapsing them into one bucket.",
        "",
        "## Named party profiles",
        "",
    ])
    for profile in report["partyDeonticProfiles"]:
        lines.append(f"- `{profile['party_id']}`: `{profile['classification']}`; direct provider duty = `{profile['directVawaProviderDuty']}`")
    lines.extend([
        "",
        "## Fault matrix",
        "",
    ])
    for item in sorted(report["faultMatrix"], key=lambda x: x["faultScore"], reverse=True):
        lines.append(
            f"- `{item['actor']}`: `{item['faultTier']}`; score `{item['faultScore']}`; FP risk `{item['falsePositiveRisk']}`; FN risk `{item['falseNegativeRisk']}`"
        )
    lines.extend([
        "",
        "## Actor deontic matrix",
        "",
    ])
    for row in report["actorDeonticMatrix"]:
        counts = (
            len(row["obligated"]),
            len(row["forbidden"]),
            len(row["permitted"]),
            len(row["restrained"]),
            len(row["conditional"]),
        )
        lines.append(
            f"- `{row['actor']}`: O={counts[0]} F={counts[1]} P={counts[2]} R={counts[3]} C={counts[4]}"
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
        "- `vawa_case_report.json`",
        "- `vawa_case_report.md`",
        "- `vawa_knowledge_graph.json`",
        "- `vawa_dependency_graph.json`",
        "- `vawa_dependency_citations.jsonld`",
        "- `vawa_grounding_audit.json`",
        "- `vawa_grounding_audit.md`",
        "- `vawa_case_knowledge_graph.flogic`",
        "- `vawa_case_obligations_dcec.pl`",
        "- `vawa_tdfol_proof_audit.json`",
        "",
    ])
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(report: Optional[Dict[str, Any]] = None) -> Dict[str, Path]:
    report = report or build_case_report()
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    paths = {
        "report_json": OUTPUT_DIR / "vawa_case_report.json",
        "report_md": OUTPUT_DIR / "vawa_case_report.md",
        "knowledge_graph": OUTPUT_DIR / "vawa_knowledge_graph.json",
        "dependency_graph": OUTPUT_DIR / "vawa_dependency_graph.json",
        "dependency_citations": OUTPUT_DIR / "vawa_dependency_citations.jsonld",
        "grounding_audit_json": OUTPUT_DIR / "vawa_grounding_audit.json",
        "grounding_audit_md": OUTPUT_DIR / "vawa_grounding_audit.md",
        "flogic": OUTPUT_DIR / "vawa_case_knowledge_graph.flogic",
        "dcec": OUTPUT_DIR / "vawa_case_obligations_dcec.pl",
        "tdfol_audit": OUTPUT_DIR / "vawa_tdfol_proof_audit.json",
    }
    paths["report_json"].write_text(json.dumps(report, indent=2) + "\n")
    paths["report_md"].write_text(_build_markdown_summary(report))
    paths["knowledge_graph"].write_text(json.dumps(report["knowledgeGraph"], indent=2) + "\n")
    paths["dependency_graph"].write_text(json.dumps(report["dependencyGraph"], indent=2) + "\n")
    paths["dependency_citations"].write_text(json.dumps(_build_dependency_citations(report["dependencyGraph"]), indent=2) + "\n")
    paths["grounding_audit_json"].write_text(json.dumps(report["groundingAudit"], indent=2) + "\n")
    paths["grounding_audit_md"].write_text(_build_grounding_audit_markdown(report["groundingAudit"]))
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
