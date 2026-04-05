"""
Build a court-facing motion support packet from the generated Title 18 filing bundle.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_filing_bundle import build_title18_filing_bundle


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _load_text(path: Path) -> str:
    return path.read_text()


def build_motion_support_packet() -> Dict[str, Any]:
    bundle = build_title18_filing_bundle()
    breach_report = bundle["embedded"]["breachReport"]
    discovery_plan = bundle["embedded"]["discoveryGapPlan"]

    motion_insert = _load_text(ROOT / "docs" / "section18_demands_for_relief_motion_insert.md")
    crosswalk = _load_text(ROOT / "docs" / "section18_evidence_to_element_crosswalk.md")
    defenses = _load_text(ROOT / "docs" / "eviction_answer_affirmative_defenses_and_counterclaims_title18.md")

    exhibit_map = [
        {
            "exhibit": "Exhibit I",
            "use": "Disability accommodation and inaccessible third-floor offer.",
        },
        {
            "exhibit": "Exhibit L",
            "use": "Quantum packet receipt, non-transmission, and Ferron admissions.",
        },
        {
            "exhibit": "Exhibit M",
            "use": "Section 18 Phase II notice and September 19, 2024 trigger date.",
        },
    ]

    requested_relief = [
        "Stay or deny eviction/displacement relief until Section 18 relocation obligations are proven satisfied for this household.",
        "Compel production of the full Section 18 approval, relocation, comparability, counseling, and payment record set.",
        "Require a lawful comparable and accessible replacement-housing offer with disability accommodations.",
        "Require payment or commitment of relocation expenses and documented relocation counseling.",
        "Grant any additional equitable, declaratory, or statutory relief the court deems just and proper.",
    ]

    sections = [
        {
            "id": "summary_of_theory",
            "title": "Summary of Theory",
            "content": [
                "The record currently supports four high-confidence likely-breach theories: premature eviction before relocation completion, failure to provide relocation counseling and moving-expense support, inaccessible/non-comparable replacement housing, and Quantum's intake-packet failure.",
                "Those theories arise from the same integrated relocation transaction and are tied to the September 19, 2024 Section 18 trigger, the unresolved relocation path, and the March 31, 2026 eviction timeline.",
            ],
        },
        {
            "id": "key_breach_findings",
            "title": "Key Breach Findings",
            "content": breach_report["summary"]["strongestLikelyBreaches"],
        },
        {
            "id": "developing_theories",
            "title": "Developing Theories",
            "content": breach_report["summary"]["weakerOrDevelopingTheories"],
        },
        {
            "id": "requested_relief",
            "title": "Requested Relief",
            "content": requested_relief,
        },
        {
            "id": "priority_discovery",
            "title": "Priority Discovery",
            "content": [item["request"] for item in discovery_plan["requests"] if item["priority"] == "high"],
        },
    ]

    return {
        "meta": {
            "packetId": "title18_motion_support_001",
            "generatedAt": bundle["meta"]["generatedAt"],
            "recommendedFirstStop": bundle["meta"]["recommendedFirstStop"],
            "bundleId": bundle["meta"]["bundleId"],
        },
        "headline": bundle["topline"],
        "sections": sections,
        "exhibitMap": exhibit_map,
        "requestedRelief": requested_relief,
        "sourceDocuments": {
            "motionInsert": str(ROOT / "docs" / "section18_demands_for_relief_motion_insert.md"),
            "crosswalk": str(ROOT / "docs" / "section18_evidence_to_element_crosswalk.md"),
            "defenses": str(ROOT / "docs" / "eviction_answer_affirmative_defenses_and_counterclaims_title18.md"),
        },
        "draftInputs": {
            "motionInsert": motion_insert,
            "crosswalk": crosswalk,
            "defenses": defenses,
        },
    }


def render_motion_support_markdown(packet: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Motion Support Packet")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    for item in packet["headline"]["likelyBreaches"]:
        lines.append(f"- Likely breach: {item}")
    for item in packet["headline"]["developingTheories"]:
        lines.append(f"- Developing theory: {item}")
    lines.append("")
    for section in packet["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        for paragraph in section["content"]:
            lines.append(f"- {paragraph}")
        lines.append("")
    lines.append("## Exhibit Map")
    lines.append("")
    for item in packet["exhibitMap"]:
        lines.append(f"- {item['exhibit']}: {item['use']}")
    return "\n".join(lines).rstrip() + "\n"


def write_motion_support_packet(packet: Dict[str, Any] | None = None) -> Dict[str, Path]:
    packet = packet or build_motion_support_packet()
    outputs = {
        "json": OUTPUTS / "title18_motion_support_packet.json",
        "markdown": OUTPUTS / "title18_motion_support_packet.md",
    }
    outputs["json"].write_text(json.dumps(packet, indent=2) + "\n")
    outputs["markdown"].write_text(render_motion_support_markdown(packet))
    return outputs


def main() -> int:
    outputs = write_motion_support_packet()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())