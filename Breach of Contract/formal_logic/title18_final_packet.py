"""
Build selectable final filing packets for the HACC and Quantum motion tracks.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_filing_index import build_title18_filing_index, build_title18_proposed_orders, render_proposed_order_markdown
from formal_logic.title18_rendered_filings import build_rendered_title18_filings
from formal_logic.title18_service_packet import build_title18_service_packet, render_service_checklist_markdown


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"
PLACEHOLDER_PATTERN = re.compile(r"\[[A-Za-z0-9&'._/ -]+\]")
PLACEHOLDER_ALIASES = {
    "[Signature]": "[SIGNATURE]",
    "[Signature block]": "[SIGNATURE]",
}


def _packet_spec(track: str) -> Dict[str, str]:
    specs = {
        "hacc": {
            "packetId": "title18_hacc_final_packet_001",
            "title": "Title 18 HACC Final Filing Packet",
            "documentKey": "hacc_party_motion",
            "orderKey": "hacc",
            "motionLabel": "HACC-focused motion",
            "theory": "Stay or deny displacement relief and compel HACC-specific Section 18 discovery before any possession transfer.",
        },
        "quantum": {
            "packetId": "title18_quantum_final_packet_001",
            "title": "Title 18 Quantum Final Filing Packet",
            "documentKey": "quantum_party_motion",
            "orderKey": "quantum",
            "motionLabel": "Quantum-focused motion",
            "theory": "Join Quantum Residential, allow third-party claims, and compel the intake/application records tied to the relocation failure.",
        },
    }
    if track not in specs:
        raise ValueError(f"Unsupported track: {track}")
    return specs[track]


def _collect_placeholders(text: str) -> List[str]:
    placeholders = set()
    for match in PLACEHOLDER_PATTERN.findall(text):
        inner = match[1:-1].strip()
        if len(inner) < 4:
            continue
        if not any(character.isalpha() for character in inner):
            continue
        placeholders.add(PLACEHOLDER_ALIASES.get(match, match))
    return sorted(placeholders)


def _render_packet_motion(document: Dict[str, Any]) -> Dict[str, Any]:
    rendered_json = document["renderedJson"]
    sections = [
        section for section in rendered_json.get("sections", []) if section.get("id") != "reference_draft"
    ]
    lines: List[str] = []
    lines.append(f"# {rendered_json['meta']['draftId']}")
    lines.append("")
    for section in sections:
        lines.append(f"## {section['title']}")
        lines.append("")
        for item in section["content"]:
            if "\n" in item:
                lines.append(item)
            else:
                lines.append(f"- {item}")
        lines.append("")
    markdown = "\n".join(lines).rstrip() + "\n"
    return {
        "sourceId": document["sourceId"],
        "markdown": markdown,
        "unresolvedPlaceholders": _collect_placeholders(markdown),
    }


def build_title18_final_packet(track: str) -> Dict[str, Any]:
    spec = _packet_spec(track)
    rendered = build_rendered_title18_filings()
    orders = build_title18_proposed_orders()
    service_packet = build_title18_service_packet()
    filing_index = build_title18_filing_index()

    motion = _render_packet_motion(rendered["documents"][spec["documentKey"]])
    order = orders["renderedOrders"][spec["orderKey"]]
    unresolved = sorted(
        set(motion["unresolvedPlaceholders"])
        | set(order["unresolvedPlaceholders"])
        | set(service_packet["certificateOfService"]["unresolvedPlaceholders"])
    )

    checklist = [
        f"Use the {spec['motionLabel']} as the lead filing document.",
        "Pair it with the matched proposed order in the same packet.",
        "Use the shared certificate of service and adjust the listed documents and service method before filing.",
        "Review the filing index for any unresolved placeholders that remain outside this packet.",
    ]

    return {
        "meta": {
            "packetId": spec["packetId"],
            "title": spec["title"],
            "generatedAt": rendered["context"]["substitutions"]["[DATE]"],
            "track": track,
            "renderContextId": rendered["context"]["meta"]["contextId"],
        },
        "theory": spec["theory"],
        "motion": {
            "sourceId": motion["sourceId"],
            "markdown": motion["markdown"],
            "unresolvedPlaceholders": motion["unresolvedPlaceholders"],
        },
        "proposedOrder": {
            "orderId": order["orderId"],
            "markdown": render_proposed_order_markdown(order),
            "unresolvedPlaceholders": order["unresolvedPlaceholders"],
        },
        "certificateOfService": service_packet["certificateOfService"],
        "serviceChecklist": {
            "markdown": render_service_checklist_markdown(service_packet),
            "items": service_packet["checklist"]["items"],
        },
        "aggregateUnresolvedPlaceholders": unresolved,
        "packetChecklist": checklist,
        "filingIndexId": filing_index["meta"]["indexId"],
    }


def render_title18_final_packet_markdown(packet: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {packet['meta']['title']}")
    lines.append("")
    lines.append("## Filing Theory")
    lines.append("")
    lines.append(f"- {packet['theory']}")
    lines.append("")
    lines.append("## Packet Checklist")
    lines.append("")
    for item in packet["packetChecklist"]:
        lines.append(f"- {item}")
    lines.append("")
    lines.append("## Aggregate Unresolved Placeholders")
    lines.append("")
    if packet["aggregateUnresolvedPlaceholders"]:
        for item in packet["aggregateUnresolvedPlaceholders"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Motion")
    lines.append("")
    lines.append(packet["motion"]["markdown"].rstrip())
    lines.append("")
    lines.append("## Proposed Order")
    lines.append("")
    lines.append(packet["proposedOrder"]["markdown"].rstrip())
    lines.append("")
    lines.append("## Certificate Of Service")
    lines.append("")
    lines.append(packet["certificateOfService"]["markdown"].rstrip())
    lines.append("")
    lines.append("## Service Checklist")
    lines.append("")
    lines.append(packet["serviceChecklist"]["markdown"].rstrip())
    return "\n".join(lines).rstrip() + "\n"


def write_title18_final_packets() -> Dict[str, Path]:
    hacc = build_title18_final_packet("hacc")
    quantum = build_title18_final_packet("quantum")
    outputs = {
        "hacc_json": OUTPUTS / "title18_hacc_final_packet.json",
        "hacc_markdown": OUTPUTS / "title18_hacc_final_packet.md",
        "quantum_json": OUTPUTS / "title18_quantum_final_packet.json",
        "quantum_markdown": OUTPUTS / "title18_quantum_final_packet.md",
    }
    outputs["hacc_json"].write_text(json.dumps(hacc, indent=2) + "\n")
    outputs["hacc_markdown"].write_text(render_title18_final_packet_markdown(hacc))
    outputs["quantum_json"].write_text(json.dumps(quantum, indent=2) + "\n")
    outputs["quantum_markdown"].write_text(render_title18_final_packet_markdown(quantum))
    return outputs


def main() -> int:
    outputs = write_title18_final_packets()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())