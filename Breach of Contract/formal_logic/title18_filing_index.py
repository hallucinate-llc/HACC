"""Build matched proposed orders and a filing index for rendered Title 18 motion outputs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_proposed_orders import build_title18_proposed_orders, render_proposed_order_markdown
from formal_logic.title18_rendered_filings import build_rendered_title18_filings
from formal_logic.title18_service_packet import build_title18_service_packet


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def build_title18_filing_index(merged_order_track: str = "hacc") -> Dict[str, Any]:
    rendered = build_rendered_title18_filings(merged_order_track=merged_order_track)
    proposed_orders = build_title18_proposed_orders()
    service_packet = build_title18_service_packet()
    unresolved_by_document = {
        item["documentKey"]: item["unresolvedPlaceholders"] for item in rendered["manifest"]["documents"]
    }
    unresolved_by_document["hacc_proposed_order"] = proposed_orders["renderedOrders"]["hacc"]["unresolvedPlaceholders"]
    unresolved_by_document["quantum_proposed_order"] = proposed_orders["renderedOrders"]["quantum"]["unresolvedPlaceholders"]
    unresolved_by_document["certificate_of_service"] = service_packet["certificateOfService"]["unresolvedPlaceholders"]

    artifacts = [
        {
            "label": "Merged motion",
            "path": "outputs/title18_merged_motion_rendered.md",
            "purpose": "Unified court-facing motion package with shared narrative and requested relief.",
        },
        {
            "label": "HACC motion",
            "path": "outputs/title18_hacc_party_motion_rendered.md",
            "purpose": "Stay/deny relief and Section 18 compliance discovery focused on HACC.",
        },
        {
            "label": "Quantum motion",
            "path": "outputs/title18_quantum_party_motion_rendered.md",
            "purpose": "Joinder and third-party claims package focused on Quantum Residential.",
        },
        {
            "label": "HACC proposed order",
            "path": "outputs/title18_hacc_proposed_order.md",
            "purpose": "Matched proposed order for stay/deny relief and discovery against HACC.",
        },
        {
            "label": "Quantum proposed order",
            "path": "outputs/title18_quantum_proposed_order.md",
            "purpose": "Matched proposed order for joinder and third-party leave against Quantum.",
        },
        {
            "label": "Render context",
            "path": "outputs/title18_render_context.json",
            "purpose": "Shared substitution values and remaining required user fields.",
        },
        {
            "label": "Certificate of service",
            "path": "outputs/title18_certificate_of_service.md",
            "purpose": "Service-ready certificate tied to the rendered motion packet.",
        },
        {
            "label": "Service checklist",
            "path": "outputs/title18_service_checklist.md",
            "purpose": "Short pre-filing and service checklist for the selected motion package.",
        },
    ]

    return {
        "meta": {
            "indexId": "title18_filing_index_001",
            "generatedAt": rendered["context"]["substitutions"]["[DATE]"],
            "renderManifestId": rendered["manifest"]["renderId"],
            "mergedOrderTrack": merged_order_track,
            "proposedOrderPacketId": proposed_orders["meta"]["packetId"],
        },
        "artifacts": artifacts,
        "unresolvedPlaceholdersByDocument": unresolved_by_document,
        "recommendedSequence": [
            "Fill [CASE NUMBER] across all rendered motions and proposed orders first.",
            "Complete judge, counsel, entity-name, and signature fields in the proposed orders and Quantum filing materials.",
            "File the motion selected for the immediate hearing posture together with its matched proposed order and service materials.",
        ],
    }


def render_title18_filing_index_markdown(index: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Filing Index")
    lines.append("")
    lines.append("## Filing Artifacts")
    lines.append("")
    for item in index["artifacts"]:
        lines.append(f"- {item['label']}: {item['path']} -- {item['purpose']}")
    lines.append("")
    lines.append("## Remaining Placeholders")
    lines.append("")
    for key, placeholders in index["unresolvedPlaceholdersByDocument"].items():
        joined = ", ".join(placeholders) if placeholders else "None"
        lines.append(f"- {key}: {joined}")
    lines.append("")
    lines.append("## Recommended Sequence")
    lines.append("")
    for item in index["recommendedSequence"]:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_filing_index(bundle: Dict[str, Any] | None = None, merged_order_track: str = "hacc") -> Dict[str, Path]:
    bundle = bundle or build_title18_filing_index(merged_order_track=merged_order_track)
    proposed_orders = build_title18_proposed_orders()
    outputs = {
        "hacc_order_json": OUTPUTS / "title18_hacc_proposed_order.json",
        "hacc_order_markdown": OUTPUTS / "title18_hacc_proposed_order.md",
        "quantum_order_json": OUTPUTS / "title18_quantum_proposed_order.json",
        "quantum_order_markdown": OUTPUTS / "title18_quantum_proposed_order.md",
        "index_json": OUTPUTS / "title18_filing_index.json",
        "index_markdown": OUTPUTS / "title18_filing_index.md",
    }
    outputs["hacc_order_json"].write_text(json.dumps(proposed_orders["renderedOrders"]["hacc"], indent=2) + "\n")
    outputs["hacc_order_markdown"].write_text(render_proposed_order_markdown(proposed_orders["renderedOrders"]["hacc"]))
    outputs["quantum_order_json"].write_text(json.dumps(proposed_orders["renderedOrders"]["quantum"], indent=2) + "\n")
    outputs["quantum_order_markdown"].write_text(render_proposed_order_markdown(proposed_orders["renderedOrders"]["quantum"]))
    outputs["index_json"].write_text(json.dumps(bundle, indent=2) + "\n")
    outputs["index_markdown"].write_text(render_title18_filing_index_markdown(bundle))
    return outputs


def main() -> int:
    outputs = write_title18_filing_index()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())