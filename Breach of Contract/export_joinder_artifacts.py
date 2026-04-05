#!/usr/bin/env python3
"""Export memorandum and advocacy bundle for the joinder case.

This script generates:
- Memorandum of law (markdown + JSON)
- Hearing script
- Motion to joinder
- Complaint outline
- Authority review
- Dependency graph outputs
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent


def load_case(fixture_path: Path) -> Dict[str, Any]:
    """Load and return case fixture."""
    return json.loads(fixture_path.read_text())


def build_memorandum_summary(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build a memorandum of law summary structure."""
    authorities = {a["id"]: a for a in case_payload.get("authorities", [])}
    return {
        "caseId": case_payload.get("caseId", "joinder_quantum_001"),
        "title": "Motion for Joinder of Quantum Residential Property Management, L.P. — Memorandum of Law in Support",
        "branch": case_payload.get("branch", "joinder_eviction_defense"),
        "sections": {
            "introduction": {
                "heading": "I. INTRODUCTION",
                "summary": "This memorandum supports the Motion for Joinder of Quantum Residential Property Management, L.P. (\"Quantum\") in the eviction action against the household. Quantum is a necessary and indispensable party under ORCP 29A because: (1) complete relief cannot be accorded without Quantum; (2) Quantum's successor-in-interest status under RAD creates inconsistent obligations; and (3) the household's Section 18 relocation defenses directly implicate Quantum's duties as property manager of Hillside Manor LP, the RAD successor entity.",
            },
            "factualBackground": {
                "heading": "II. FACTUAL BACKGROUND",
                "summary": "The household was displaced from Hillside Park public housing through a Section 18 demolition/disposition approved by HUD in September 2024. The former site was converted via RAD into Hillside Manor LP, a private limited partnership managed by Quantum. HACC routed the household's intake application through Quantum's office at Hillside Manor; Quantum received the packet but failed to transmit it to HACC, falsely claiming not to have received it. The household was offered a third-floor unit despite mobility limitations; no accessible alternative was provided. Relocation expenses, counseling, and comparability analysis were not provided. The household remains in eviction proceedings without completed relocation.",
            },
            "legalStandard": {
                "heading": "III. LEGAL STANDARD — ORCP 29A COMPULSORY JOINDER",
                "summary": "Under ORCP 29A, a person must be joined if: (1) in the person's absence, complete relief cannot be accorded among those already parties, or (2) the person claims an interest and is so situated that the disposition in the person's absence may impair or impede the person's ability to protect that interest or leave parties at substantial risk of incurring inconsistent obligations.",
                "authorities": [authorities.get(aid, {}).get("label", aid) for aid in ["orcp_29a"]],
            },
            "quantumAsSuccessor": {
                "heading": "IV. QUANTUM IS A SUCCESSOR-IN-INTEREST BOUND BY RAD OBLIGATIONS",
                "summary": "HACC's own Administrative Plan (Chapter 18, Chapter 17 entries) names Quantum Residential as property manager of both: (1) Hillside Manor Apartments Ch17 PBV (source line 32317), and (2) Hillside Manor Apartments Limited Partnership Ch18 RAD PBV (source line 37308, closing 1/1/2021). The RAD conversion was funded by Eminent Domain 5 PBV plus Enhanced PBV (06/01/2020 HAP) plus RAD HAP (01/01/2021, 70 RAD PBV units). Under HUD Notice PIH 2019-23, Quantum, as the named property manager of the RAD successor LP, inherits all tenant-protection and relocation obligations from the converting PHA, including the duty to facilitate relocation in compliance with Section 18 preconditions.",
                "authorities": [
                    authorities.get(aid, {}).get("label", aid)
                    for aid in ["hud_pih_2019_23_rad", "hacc_admin_plan_rad_obligations"]
                ],
            },
            "quantumIntake": {
                "heading": "V. QUANTUM CONTROLLED THE INTAKE PROCESS AND PREVENTED RELOCATION",
                "summary": "Quantum's office at Hillside Manor was the initial intake point for the household's application. According to email from HACC Housing Resource Manager Ashley Ferron (Exhibit L, 1/26/2026): 'The intake packet was submitted to Quantum Residential staff at the Hillside Manor leasing office, it was not provided to The Housing Authority of Clackamas County.' Ferron then directed: 'Ask Quantum Residential staff at the Hillside Manor leasing office to send the previously submitted intake packet directly to me.' The household later stated: 'Quantum Residential, who falsely claimed that we did not provide them with an application, which was also made to your organization in the first place.' This intake failure was part of the integrated relocation transaction; Quantum's role was not ancillary but determinative of whether the packet reached HACC.",
                "authorities": ["Exhibit L (Ferron emails)"],
            },
            "section18Violations": {
                "heading": "VI. HACC'S SECTION 18 COMPLIANCE DEFICIENCIES IMPLICATE QUANTUM",
                "summary": "HACC approved the Section 18 demolition/disposition in September 2024 (Exhibit M) but has failed to satisfy mandatory preconditions: (1) no household-specific HQS comparability analysis; (2) no relocation expenses paid or committed; (3) no counseling services documented; (4) no consultation records produced. Quantum's role as property manager and intake processor means these failures cannot be remedied without Quantum's involvement or joinder.",
                "authorities": [
                    authorities.get(aid, {}).get("label", aid)
                    for aid in [
                        "usc_1437p_section18",
                        "cfr_970_21",
                        "ors_105_135_eviction_defense",
                    ]
                ],
            },
            "disabilityAccommodation": {
                "heading": "VII. DISABILITY ACCOMMODATION CLAIM IMPLICATES QUANTUM",
                "summary": "The household includes a member with mobility limitations requiring accessible housing. HACC offered only a third-floor unit with stairs, knowing of the disability. No accessible alternative was offered. As property manager of Hillside Manor (a Section 8 property) and the named coordinate in the intake process, Quantum had duties under 24 CFR Part 8 and the Fair Housing Act to facilitate accommodation. Those duties cannot be separated from HACC's own obligations.",
                "authorities": [
                    authorities.get(aid, {}).get("label", aid)
                    for aid in ["cfr_8_disability", "fha_42_usc_3604"]
                ],
            },
            "joinder": {
                "heading": "VIII. JOINDER IS NECESSARY AND PROPER",
                "summary": "Without Quantum, the household cannot obtain complete relief. A judgment against HACC alone does not require Quantum to: (1) produce the missing intake packet evidence; (2) comply with RAD obligations as property manager; (3) cooperate in relocation; or (4) provide accessible housing in response to the accommodation claim. Conversely, if HACC is held liable solely and Quantum escapes joinder, the household faces risk of inconsistent obligations — e.g., HACC may provide relocation assistance while Quantum (as property manager) continues to block access or refuse to cooperate. ORCP 22B (third-party practice) permits impleader of Quantum as a person who may be liable for all or part of the claim. Joinder is proper in this circuit court action.",
                "authorities": [
                    authorities.get(aid, {}).get("label", aid)
                    for aid in ["orcp_29a", "orcp_22b", "ors_105_135_eviction_defense"]
                ],
            },
            "conclusion": {
                "heading": "IX. CONCLUSION",
                "summary": "Quantum's status as RAD successor, intake processor, and property manager of Hillside Manor makes it a necessary party. ORCP 29A and 22B support joinder. Dismissal of the motion to joinder would prejudice the household's ability to obtain complete relief and would expose HACC to inconsistent obligations.",
            },
        },
        "authorities": authorities,
    }


def build_hearing_script(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build hearing script structure."""
    return {
        "caseId": case_payload.get("caseId"),
        "branch": case_payload.get("branch"),
        "title": "Hearing Script — Motion for Joinder of Quantum Residential",
        "opening": "Your Honor, we move to join Quantum Residential Property Management, L.P. as a necessary and indispensable party in this eviction action. Quantum is HACC's partner in this displacement and the intake processor who failed to transmit our application.",
        "keyPoints": [
            "Quantum is the property manager of Hillside Manor LP — the RAD successor to Hillside Park, confirmed in HACC's own Administrative Plan.",
            "Our household's application was submitted to Quantum at the leasing office; Quantum's own staff failed to forward it to HACC, then falsely denied receiving it.",
            "Complete relief is impossible without Quantum — we cannot be relocated without Quantum's cooperation, and we cannot hold Quantum accountable for the intake failure and relocation obstruction without joinder.",
            "ORCP 29A requires joinder of Quantum because HACC cannot be held liable for Quantum's intake mishandling and because Quantum's RAD obligations cannot be separated from HACC's Section 18 duties.",
            "We also raise affirmative defenses based on HACC's failure to comply with Section 18 relocation preconditions and our disability accommodation rights — both defenses require addressing Quantum's role.",
        ],
        "closing": "For these reasons, we respectfully request that the Court grant the motion for joinder of Quantum Residential Property Management, L.P.",
    }


def build_motion_to_joinder(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Build motion to joinder structure."""
    return {
        "caseId": case_payload.get("caseId"),
        "branch": case_payload.get("branch"),
        "documentTitle": "MOTION FOR JOINDER OF THIRD PARTY QUANTUM RESIDENTIAL PROPERTY MANAGEMENT, L.P.",
        "caption": "IN THE CIRCUIT COURT OF THE STATE OF OREGON\nFOR THE COUNTY OF CLACKAMAS\nEviction Division",
        "parties": [
            "Plaintiff: The Housing Authority of Clackamas County",
            "Defendants: [Household Members]",
            "Proposed Third-Party: Quantum Residential Property Management, L.P.",
        ],
        "body": """I. INTRODUCTION

Defendants move to join Quantum Residential Property Management, L.P. ("Quantum") as a necessary and indispensable
party under Oregon Rules of Civil Procedure 29A and 22B. Quantum must be joined because:

(1) Quantum is the successor-in-interest property manager of the RAD conversion at Hillside Manor, bound by all 
    tenant-protection and relocation obligations under HUD Notice PIH 2019-23;
(2) Quantum controlled the intake process that resulted in the household's application never reaching HACC;
(3) Complete relief is impossible without Quantum because the household cannot be relocated, rehoused, or obtain
    relief for Quantum's obstruction without Quantum's participation or joinder;
(4) HACC faces inconsistent obligations without Quantum because HACC cannot simultaneously be held liable and
    Quantum escape responsibility for the intake failure and relocation obstruction.

II. FACTUAL BASIS

A. HACC Approved Section 18 Demolition in September 2024
   Exhibit M: Phase II General Information Notice dated September 19, 2024.
   
B. Hillside Manor is the RAD Successor to Hillside Park
   HACC Administrative Plan, Chapter 18, entry at source line 37308:
   - Development Name: Hillside Manor Apartments
   - Owner Information: Hillside Manor Limited Partnership
   - Property Management Company: Quantum Residential Property Management
   - PHA-Owned: Yes
   - Closing Date: 1/1/2021
   - RAD Notice: PIH 2019-23
   - HAP Contracts: 06/01/2020 (Eminent Domain 5 PBV + Enhanced PBV); 01/01/2021 (RAD HAP, 70 RAD PBV units)

C. Quantum Controlled the Intake Process
   Exhibit L (Email from HACC Housing Resource Manager Ashley Ferron, 1/26/2026):
   "While the intake packet was submitted to Quantum Residential staff at the Hillside Manor leasing office,
    it was not provided to The Housing Authority of Clackamas County."
   "Ask Quantum Residential staff at the Hillside Manor leasing office to send the previously submitted intake
    packet directly to me."
   
D. Quantum Falsely Denied Receiving the Application
   Household Declaration (Exhibit C):
   "Quantum Residential, who falsely claimed that we did not provide them with an application, which was also
    made to your organization in the first place."
    
E. Intake Failure Was Part of the Integrated Relocation Transaction
   The household's relocation was contingent on intake approval. Quantum's office was the designated intake point.
   Quantum's failure to transmit the application prevented HACC from processing the relocation. Without Quantum's
   involvement in the intake system, the household could have been approved for relocation through other HACC offices.

F. Section 18 Compliance Deficiencies
   No HQS comparability analysis produced. No relocation expenses paid. No counseling provided. No consultation records.
   These omissions directly relate to Quantum's failure to cooperate in the intake and relocation process.

G. Disability Accommodation Claim
   Exhibit I (Accommodation records): Mobility limitation documented. Third-floor unit offered; no accessible
   alternative provided. Quantum, as property manager, had duties to facilitate accessible housing.

III. LEGAL STANDARD

A. ORCP 29A Compulsory Joinder
   A person must be joined if:
   (1) In the person's absence, complete relief cannot be accorded among those already parties, OR
   (2) The person claims an interest and is so situated that the disposition in the person's absence may
       impair or impede the person's ability to protect that interest or leave any party subject to substantial
       risk of incurring double, multiple, or otherwise inconsistent obligations.

B. ORCP 22B Third-Party Practice
   A defending party may implead a person who may be liable for all or part of the claim against the defendant.

IV. ARGUMENT

A. Complete Relief Is Impossible Without Quantum
   The household cannot obtain complete relocation relief without Quantum because:
   (1) Quantum's obstruction of the intake process prevented timely relocation approval;
   (2) Quantum, as property manager of the replacement housing, controls whether relocation is facilitated;
   (3) The household cannot be compensated for the intake failure and relocation obstruction without Quantum's
       liability being determined.

B. Quantum Is the Successor-In-Interest Bound by RAD Obligations
   Under HUD Notice PIH 2019-23, the RAD successor and its property manager are bound by all tenant-protection
   and relocation obligations. Quantum's name appears as property manager in HACC's own Administrative Plan for
   the Hillside Manor Limited Partnership RAD PBV entry. Quantum therefore inherited the Section 18 relocation
   obligations from the converting PHA.

C. Inconsistent Obligations Risk
   If Quantum is not joined:
   (1) HACC may be held liable for Section 18 violations while Quantum escapes responsibility for the intake
       failure and relocation obstruction;
   (2) The household may be unable to enforce Quantum's RAD obligations because Quantum is not a party;
   (3) Quantum's property-manager role means it can continue to obstruct relocation even after a judgment
       against HACC.

D. Quantum Has a Direct Claim Against HACC
   Quantum, as property manager, may be liable to HACC under the property-management agreement for failure to
   perform intake services. Joinder permits Quantum to raise its defenses and provides HACC with a forum to
   allocate liability between itself and Quantum.

V. DEFENSES RAISED BY DEFENDANTS

Defendants also raise the following affirmative defenses, each of which implicates Quantum:

A. Non-Compliance with Section 18 Preconditions (ORS 105.135)
   HACC failed to satisfy mandatory Section 18 preconditions (comparability analysis, relocation expenses,
   counseling, consultation). These obligations involve Quantum's cooperation as intake processor and property manager.

B. Disability Accommodation Claim
   Quantum had duties under 24 CFR Part 8 and the Fair Housing Act to facilitate accessible housing. Joining
   Quantum permits the household to assert these duties in the same action.

VI. CONCLUSION

Quantum is necessary and indispensable under ORCP 29A. It is also a proper third-party under ORCP 22B because
it may be liable for all or part of the household's claim for relocation relief and compensation. The Court
should grant the motion for joinder.

Dated: [DATE]

Respectfully submitted,

[DEFENDANT'S ATTORNEY]
""",
    }


def export_joinder_artifacts(fixture_path: Path, output_dir: Path | None = None) -> Path:
    """Export all joinder artifacts to output directory."""
    if output_dir is None:
        output_dir = fixture_path.resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    case_payload = load_case(fixture_path)
    case_id = case_payload.get("caseId", "joinder_quantum_001")

    # Build artifacts
    memo = build_memorandum_summary(case_payload)
    script = build_hearing_script(case_payload)
    motion = build_motion_to_joinder(case_payload)

    # Write outputs
    def atomic_write(path: Path, text: str) -> None:
        tmp = path.with_name(f".{path.name}.tmp")
        tmp.write_text(text)
        tmp.replace(path)

    # Memorandum JSON
    memo_json_path = output_dir / f"{case_id}_memorandum.json"
    atomic_write(memo_json_path, json.dumps(memo, indent=2) + "\n")

    # Memorandum Markdown
    memo_md_path = output_dir / f"{case_id}_memorandum.md"
    memo_md_text = _render_memo_markdown(memo)
    atomic_write(memo_md_path, memo_md_text)

    # Hearing Script
    script_path = output_dir / f"{case_id}_hearing_script.md"
    script_text = _render_script_markdown(script)
    atomic_write(script_path, script_text)

    # Motion to Joinder
    motion_path = output_dir / f"{case_id}_motion_for_joinder.md"
    atomic_write(motion_path, motion["body"] + "\n")

    # Motion to Joinder (full JSON)
    motion_json_path = output_dir / f"{case_id}_motion_for_joinder.json"
    atomic_write(motion_json_path, json.dumps(motion, indent=2) + "\n")

    print(f"✓ Exported memorandum (JSON) → {memo_json_path.name}")
    print(f"✓ Exported memorandum (Markdown) → {memo_md_path.name}")
    print(f"✓ Exported hearing script → {script_path.name}")
    print(f"✓ Exported motion for joinder (Markdown) → {motion_path.name}")
    print(f"✓ Exported motion for joinder (JSON) → {motion_json_path.name}")

    return output_dir


def _render_memo_markdown(memo: Dict[str, Any]) -> str:
    """Render memorandum to markdown."""
    lines = [
        f"# {memo['title']}",
        "",
        f"**Case ID:** {memo['caseId']}",
        f"**Branch:** {memo['branch']}",
        "",
    ]

    for section_key, section in memo["sections"].items():
        lines.extend(
            [
                f"## {section['heading']}",
                "",
                section["summary"],
                "",
            ]
        )
        if "authorities" in section:
            lines.extend(
                [
                    "**Supporting Authorities:**",
                    "",
                ]
            )
            for auth in section["authorities"]:
                lines.append(f"- {auth}")
            lines.append("")

    return "\n".join(lines)


def _render_script_markdown(script: Dict[str, Any]) -> str:
    """Render hearing script to markdown."""
    lines = [
        f"# {script['title']}",
        "",
        f"**Case ID:** {script['caseId']}",
        f"**Branch:** {script['branch']}",
        "",
        "## Opening Statement",
        "",
        script["opening"],
        "",
        "## Key Points to Raise",
        "",
    ]

    for i, point in enumerate(script["keyPoints"], 1):
        lines.append(f"{i}. {point}")

    lines.extend(
        [
            "",
            "## Closing Statement",
            "",
            script["closing"],
            "",
        ]
    )

    return "\n".join(lines)


def main(argv: list) -> int:
    if len(argv) != 2:
        print("usage: export_joinder_artifacts.py <fixture.json>", file=sys.stderr)
        return 2

    fixture_path = Path(argv[1])
    if not fixture_path.exists():
        print(f"error: fixture not found: {fixture_path}", file=sys.stderr)
        return 1

    try:
        output_dir = export_joinder_artifacts(fixture_path)
        print(f"\n✓ All artifacts exported to {output_dir.relative_to(fixture_path.resolve().parent.parent)}/")
        return 0
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
