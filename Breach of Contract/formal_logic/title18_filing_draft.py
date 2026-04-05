"""
Generate a fuller court-facing Title 18 filing draft from the synthesized packet.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_motion_support import build_motion_support_packet


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _load_text(path: Path) -> str:
    return path.read_text()


def build_title18_filing_draft() -> Dict[str, Any]:
    motion_packet = build_motion_support_packet()
    emergency_motion = _load_text(ROOT / "docs" / "emergency_short_motion_quantum_joinder.md")
    proposed_order = _load_text(ROOT / "docs" / "proposed_order_joinder_quantum.md")
    joinder_draft = _load_text(ROOT / "docs" / "eviction_joinder_third_party_quantum_draft_filled.md")

    sections = [
        {
            "id": "caption",
            "title": "Caption",
            "content": [
                "IN THE CIRCUIT COURT OF THE STATE OF OREGON FOR THE COUNTY OF CLACKAMAS",
                "HOUSING AUTHORITY OF CLACKAMAS COUNTY v. BENJAMIN JAY BARBER and JANE KAY CORTEZ",
                "Case No. [CASE NUMBER]",
            ],
        },
        {
            "id": "preliminary_statement",
            "title": "Preliminary Statement",
            "content": [
                "This filing arises from an eviction/displacement action pursued while the Section 18 relocation process remained incomplete after the September 19, 2024 Phase II trigger.",
                "The current synthesized record supports a unified theory that HACC and Quantum participated in one relocation transaction, and that unresolved relocation breaches materially overlap with the eviction basis now asserted.",
            ],
        },
        {
            "id": "core_breaches",
            "title": "Core Breaches",
            "content": motion_packet["headline"]["likelyBreaches"],
        },
        {
            "id": "argument_points",
            "title": "Argument Points",
            "content": [
                "Section 18 relocation duties were triggered no later than September 19, 2024 by HUD approval and HACC's Phase II notice.",
                "The record presently shows no completed counseling, no relocation-expense commitment, and no compliant comparable accessible replacement-housing offer before the March 31, 2026 eviction timeline.",
                "Quantum's packet-handling role is not collateral; HACC's own communications tie Quantum staff to the failed intake and forwarding path for replacement housing.",
                "The court should not adjudicate possession while the relocation preconditions and interlocking actor conduct remain unresolved.",
            ],
        },
        {
            "id": "requested_relief",
            "title": "Requested Relief",
            "content": motion_packet["requestedRelief"],
        },
        {
            "id": "priority_exhibits",
            "title": "Priority Exhibits",
            "content": [f"{item['exhibit']}: {item['use']}" for item in motion_packet["exhibitMap"]],
        },
        {
            "id": "priority_discovery",
            "title": "Priority Discovery Requests",
            "content": motion_packet["sections"][-1]["content"],
        },
    ]

    return {
        "meta": {
            "draftId": "title18_filing_draft_001",
            "generatedAt": motion_packet["meta"]["generatedAt"],
            "sourcePacketId": motion_packet["meta"]["packetId"],
        },
        "sections": sections,
        "referenceDrafts": {
            "emergencyMotion": emergency_motion,
            "proposedOrder": proposed_order,
            "joinderDraft": joinder_draft,
        },
    }


def render_title18_filing_draft_markdown(draft: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Filing Draft")
    lines.append("")
    for section in draft["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        for paragraph in section["content"]:
            lines.append(f"- {paragraph}")
        lines.append("")
    lines.append("## Reference Draft Sources")
    lines.append("")
    lines.append("- Emergency motion source included in JSON output.")
    lines.append("- Proposed order source included in JSON output.")
    lines.append("- Joinder draft source included in JSON output.")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_filing_draft(draft: Dict[str, Any] | None = None) -> Dict[str, Path]:
    draft = draft or build_title18_filing_draft()
    outputs = {
        "json": OUTPUTS / "title18_filing_draft.json",
        "markdown": OUTPUTS / "title18_filing_draft.md",
    }
    outputs["json"].write_text(json.dumps(draft, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_filing_draft_markdown(draft))
    return outputs


def main() -> int:
    outputs = write_title18_filing_draft()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())