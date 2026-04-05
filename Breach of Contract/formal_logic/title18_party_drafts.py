"""
Build party-specific Title 18 motion drafts from the merged packet.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_merged_motion import build_title18_merged_motion


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _load_text(path: Path) -> str:
    return path.read_text()


def _base_party_metadata(motion: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generatedAt": motion["meta"]["generatedAt"],
        "sourceMotionId": motion["meta"]["motionId"],
    }


def build_hacc_party_motion() -> Dict[str, Any]:
    motion = build_title18_merged_motion()
    subpoena_requests = _load_text(ROOT / "docs" / "section18_targeted_rfp_and_subpoena_requests.md")
    combined_answer = _load_text(ROOT / "docs" / "fed_combined_answer_counterclaims_and_joinder_package.md")

    sections = [
        {
            "id": "caption",
            "title": "Caption",
            "content": motion["sections"][0]["content"],
        },
        {
            "id": "motion_title",
            "title": "Motion Title",
            "content": [
                "DEFENDANTS' HACC-FOCUSED MOTION TO STAY OR DENY DISPLACEMENT RELIEF, COMPEL SECTION 18 DISCOVERY, AND PRESERVE ACCESSIBLE RELOCATION REMEDIES",
            ],
        },
        {
            "id": "preliminary_statement",
            "title": "Preliminary Statement",
            "content": [
                "This HACC-focused motion isolates the housing authority's own Section 18 duties: counseling, relocation expense support, comparable accessible replacement housing, and compliance before eviction or displacement relief.",
                "The present record supports that HACC pursued possession while those federal relocation preconditions remained incomplete and while household accessibility issues were still unresolved.",
            ],
        },
        {
            "id": "hacc_core_failures",
            "title": "HACC Core Failures",
            "content": [
                item for item in motion["headline"]["likelyBreaches"] if "Quantum" not in item
            ],
        },
        {
            "id": "stay_theory",
            "title": "Stay and Denial Theory",
            "content": [
                "HACC cannot obtain displacement relief on an incomplete federal-relocation record because the same record supports missing counseling, missing relocation-expense commitment, and the absence of a comparable accessible replacement path.",
                "The current evidence also supports an accessibility failure because the household was routed toward non-usable housing configurations despite documented mobility limitations and a live-in-aide need.",
            ],
        },
        {
            "id": "priority_discovery",
            "title": "Priority HACC Discovery",
            "content": [subpoena_requests],
        },
        {
            "id": "requested_relief",
            "title": "Requested Relief",
            "content": [
                "Stay or deny HACC's eviction or displacement relief until HACC proves household-specific Section 18 compliance.",
                "Compel HACC to produce the approval, relocation-plan, comparability, counseling, accommodation, and payment record needed to test statutory compliance.",
                "Require HACC to identify a lawful, comparable, and accessible replacement-housing path that matches the household's documented mobility and caregiver needs.",
                "Preserve all counterclaims, offsets, and equitable defenses tied to HACC's incomplete relocation performance.",
            ],
        },
        {
            "id": "reference_draft",
            "title": "Reference Draft",
            "content": [combined_answer],
        },
    ]

    return {
        "meta": {
            "draftId": "title18_hacc_party_motion_001",
            **_base_party_metadata(motion),
            "focusParty": "org:hacc",
        },
        "sections": sections,
        "requestedRelief": sections[6]["content"],
        "exhibitMap": motion["exhibitMap"],
    }


def build_quantum_party_motion() -> Dict[str, Any]:
    motion = build_title18_merged_motion()
    joinder_template = _load_text(ROOT / "docs" / "eviction_joinder_third_party_quantum_template.md")
    subpoena_requests = _load_text(ROOT / "docs" / "section18_targeted_rfp_and_subpoena_requests.md")

    sections = [
        {
            "id": "caption",
            "title": "Caption",
            "content": motion["sections"][0]["content"],
        },
        {
            "id": "motion_title",
            "title": "Motion Title",
            "content": [
                "DEFENDANTS' QUANTUM-FOCUSED MOTION FOR JOINDER, LEAVE TO FILE THIRD-PARTY CLAIMS, AND RELATED DISCOVERY",
            ],
        },
        {
            "id": "preliminary_statement",
            "title": "Preliminary Statement",
            "content": [
                "This Quantum-focused draft isolates the owner-manager side of the relocation transaction because HACC's own communications place Quantum staff at the intake and non-transmission point for the replacement-housing packet.",
                "Quantum's alleged packet handling, application delay, and accessibility failures are part of the same facts the court must assess before it can fairly decide prevention, causation, and equitable relief.",
            ],
        },
        {
            "id": "quantum_core_theories",
            "title": "Quantum Core Theories",
            "content": [
                item for item in motion["headline"]["likelyBreaches"] if "Quantum" in item
            ]
            + [
                "Quantum's role in the Blossom and related replacement-housing path should be tested through joinder discovery because the current record supports recurring intake and application obstruction.",
                "Quantum's alleged handling of an inaccessible or unavailable replacement path bears directly on prevention, causation, and equitable defenses in the eviction case.",
            ],
        },
        {
            "id": "joinder_basis",
            "title": "Joinder Basis",
            "content": [
                "Quantum's role should be adjudicated in the same proceeding because the relocation packet, replacement-housing intake, and accessibility path overlap with HACC's asserted grounds for displacement.",
                "Separate litigation would risk inconsistent rulings on who prevented completion of the relocation path and whether the household was denied a real opportunity to secure replacement housing.",
            ],
        },
        {
            "id": "quantum_discovery",
            "title": "Priority Quantum Discovery",
            "content": [subpoena_requests],
        },
        {
            "id": "requested_relief",
            "title": "Requested Relief",
            "content": [
                "Join Quantum Residential as a necessary or proper party for full adjudication of the relocation and intake failures tied to the eviction record.",
                "Grant leave to file related third-party claims against Quantum concerning packet non-transmission, application obstruction, and accessibility-related housing failures.",
                "Compel production of Quantum communications, intake logs, management agreements, unit-availability records, and any records tying Quantum to the HACC-linked replacement-housing process.",
                "Preserve equitable defenses showing HACC and Quantum participated in one incomplete relocation transaction.",
            ],
        },
        {
            "id": "reference_draft",
            "title": "Reference Draft",
            "content": [joinder_template],
        },
    ]

    return {
        "meta": {
            "draftId": "title18_quantum_party_motion_001",
            **_base_party_metadata(motion),
            "focusParty": "org:quantum",
        },
        "sections": sections,
        "requestedRelief": sections[6]["content"],
        "exhibitMap": motion["exhibitMap"],
    }


def render_party_motion_markdown(draft: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {draft['meta']['draftId']}")
    lines.append("")
    for section in draft["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        for item in section["content"]:
            if "\n" in item:
                lines.append(item)
            else:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_party_drafts() -> Dict[str, Path]:
    hacc = build_hacc_party_motion()
    quantum = build_quantum_party_motion()
    outputs = {
        "hacc_json": OUTPUTS / "title18_hacc_party_motion.json",
        "hacc_markdown": OUTPUTS / "title18_hacc_party_motion.md",
        "quantum_json": OUTPUTS / "title18_quantum_party_motion.json",
        "quantum_markdown": OUTPUTS / "title18_quantum_party_motion.md",
    }
    outputs["hacc_json"].write_text(json.dumps(hacc, indent=2) + "\n")
    outputs["hacc_markdown"].write_text(render_party_motion_markdown(hacc))
    outputs["quantum_json"].write_text(json.dumps(quantum, indent=2) + "\n")
    outputs["quantum_markdown"].write_text(render_party_motion_markdown(quantum))
    return outputs


def main() -> int:
    outputs = write_title18_party_drafts()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())