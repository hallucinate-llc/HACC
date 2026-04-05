"""
Build a single merged motion package from the generated Title 18 filing artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_filing_draft import build_title18_filing_draft
from formal_logic.title18_motion_support import build_motion_support_packet
from formal_logic.title18_proposed_orders import build_title18_proposed_orders, render_proposed_order_markdown


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def build_title18_merged_motion(order_track: str = "hacc") -> Dict[str, Any]:
    filing_draft = build_title18_filing_draft()
    motion_packet = build_motion_support_packet()
    proposed_orders = build_title18_proposed_orders()
    proposed_order = render_proposed_order_markdown(proposed_orders["renderedOrders"][order_track]).rstrip()

    sections = [
        {
            "id": "caption",
            "title": "Caption",
            "content": filing_draft["sections"][0]["content"],
        },
        {
            "id": "motion_title",
            "title": "Motion Title",
            "content": [
                "DEFENDANTS' MOTION TO STAY OR DENY DISPLACEMENT RELIEF, COMPEL SECTION 18 COMPLIANCE DISCOVERY, AND GRANT FURTHER EQUITABLE RELIEF",
            ],
        },
        {
            "id": "preliminary_statement",
            "title": "Preliminary Statement",
            "content": filing_draft["sections"][1]["content"],
        },
        {
            "id": "summary_of_argument",
            "title": "Summary of Argument",
            "content": [
                "Section 18 duties were triggered no later than September 19, 2024, yet the current record supports that HACC pursued eviction while counseling, relocation expenses, and comparable accessible replacement housing remained incomplete.",
                "Quantum's intake role is part of the same relocation transaction because HACC's own communications place Quantum staff at the packet-receipt and non-transmission point for the replacement-housing path.",
                "The court should not grant possession or displacement relief on a record showing unresolved federal relocation preconditions and an incomplete actor record.",
            ],
        },
        {
            "id": "key_breaches",
            "title": "Key Breaches",
            "content": motion_packet["headline"]["likelyBreaches"],
        },
        {
            "id": "argument_points",
            "title": "Argument Points",
            "content": filing_draft["sections"][3]["content"],
        },
        {
            "id": "priority_exhibits",
            "title": "Priority Exhibits",
            "content": filing_draft["sections"][5]["content"],
        },
        {
            "id": "requested_relief",
            "title": "Requested Relief",
            "content": filing_draft["sections"][4]["content"],
        },
        {
            "id": "priority_discovery",
            "title": "Priority Discovery Requests",
            "content": filing_draft["sections"][6]["content"],
        },
        {
            "id": "proposed_order",
            "title": "Proposed Order",
            "content": [proposed_order],
        },
    ]

    return {
        "meta": {
            "motionId": "title18_merged_motion_001",
            "generatedAt": motion_packet["meta"]["generatedAt"],
            "sourceDraftId": filing_draft["meta"]["draftId"],
            "sourcePacketId": motion_packet["meta"]["packetId"],
            "proposedOrderTrack": order_track,
        },
        "sections": sections,
        "headline": motion_packet["headline"],
        "requestedRelief": motion_packet["requestedRelief"],
        "exhibitMap": motion_packet["exhibitMap"],
    }


def render_title18_merged_motion_markdown(motion: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Merged Motion Package")
    lines.append("")
    for section in motion["sections"]:
        lines.append(f"## {section['title']}")
        lines.append("")
        for item in section["content"]:
            if "\n" in item:
                lines.append(item)
            else:
                lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_merged_motion(motion: Dict[str, Any] | None = None) -> Dict[str, Path]:
    motion = motion or build_title18_merged_motion()
    outputs = {
        "json": OUTPUTS / "title18_merged_motion.json",
        "markdown": OUTPUTS / "title18_merged_motion.md",
    }
    outputs["json"].write_text(json.dumps(motion, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_merged_motion_markdown(motion))
    return outputs


def main() -> int:
    outputs = write_title18_merged_motion()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())