"""
Build matched proposed orders and a filing index for rendered Title 18 motion outputs.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_rendered_filings import build_render_context, build_rendered_title18_filings
from formal_logic.title18_service_packet import build_title18_service_packet


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"
PLACEHOLDER_PATTERN = re.compile(r"\[[A-Za-z0-9&'._/ -]+\]")


def _base_caption() -> List[str]:
    return [
        "IN THE CIRCUIT COURT OF THE STATE OF OREGON FOR THE COUNTY OF CLACKAMAS",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY v. BENJAMIN JAY BARBER and JANE KAY CORTEZ",
        "Case No. [CASE NUMBER]",
    ]


def build_title18_proposed_orders() -> Dict[str, Any]:
    rendered = build_rendered_title18_filings()
    context = build_render_context()
    hacc_order = {
        "orderId": "title18_hacc_proposed_order_001",
        "title": "Proposed Order Staying or Denying Displacement Relief and Compelling Section 18 Discovery",
        "caption": _base_caption(),
        "body": [
            "The Court, having reviewed Defendants' HACC-Focused Motion to Stay or Deny Displacement Relief, Compel Section 18 Discovery, and Preserve Accessible Relocation Remedies, and being fully advised, ORDERS:",
            "1. HACC's request for eviction or displacement relief is [GRANTED / DENIED / STAYED] pending resolution of the household-specific Section 18 relocation record.",
            "2. HACC shall produce the Section 18 approval, relocation-plan, comparability, counseling, accommodation, and payment materials identified in Defendants' motion within [insert schedule].",
            "3. No displacement or possession transfer shall occur unless and until the Court is satisfied that HACC has established lawful comparable and accessible replacement-housing compliance for this household.",
            "4. Any further scheduling, evidentiary, or compliance deadlines are set as follows: [insert schedule].",
            "IT IS SO ORDERED.",
            "DATED: [DATE]",
            "__________________________________",
            "[JUDGE NAME]",
        ],
        "submittedBy": [
            "Submitted by:",
            "[NAME]",
            "[ADDRESS]",
            "[PHONE]",
            "[EMAIL]",
            "[Signature]",
        ],
        "sourceMotionId": rendered["documents"]["hacc_party_motion"]["sourceId"],
    }
    quantum_order = {
        "orderId": "title18_quantum_proposed_order_001",
        "title": "Proposed Order Granting Joinder and Leave to File Third-Party Claims Against Quantum Residential",
        "caption": _base_caption(),
        "body": [
            "The Court, having reviewed Defendants' Quantum-Focused Motion for Joinder, Leave to File Third-Party Claims, and Related Discovery, and being fully advised, ORDERS:",
            "1. Defendants' motion for joinder is [GRANTED / DENIED].",
            "2. If granted, Quantum Residential [FULL LEGAL ENTITY NAME] is joined as a party in this action.",
            "3. If granted, Defendants are granted leave to file and serve their related third-party claims within [insert schedule].",
            "4. Quantum Residential shall respond within the time provided by law after service.",
            "5. Related discovery and case-management deadlines are set as follows: [insert schedule].",
            "IT IS SO ORDERED.",
            "DATED: [DATE]",
            "__________________________________",
            "[JUDGE NAME]",
        ],
        "submittedBy": [
            "Submitted by:",
            "[NAME]",
            "[ADDRESS]",
            "[PHONE]",
            "[EMAIL]",
            "[Signature]",
        ],
        "sourceMotionId": rendered["documents"]["quantum_party_motion"]["sourceId"],
    }
    orders = {
        "meta": {
            "packetId": "title18_proposed_orders_001",
            "generatedAt": rendered["context"]["substitutions"]["[DATE]"],
        },
        "orders": {
            "hacc": hacc_order,
            "quantum": quantum_order,
        },
    }
    rendered_orders = {
        key: _render_order(order, context) for key, order in orders["orders"].items()
    }
    orders["renderContextId"] = context["meta"]["contextId"]
    orders["renderedOrders"] = rendered_orders
    return orders


def _apply_context(text: str, context: Dict[str, Any]) -> str:
    rendered = text
    for placeholder, value in {**context["requiredUserInputs"], **context["substitutions"]}.items():
        if value:
            rendered = rendered.replace(placeholder, str(value))
    return rendered


def _collect_placeholders(value: str) -> List[str]:
    placeholders = set()
    for match in PLACEHOLDER_PATTERN.findall(value):
        inner = match[1:-1].strip()
        if len(inner) < 4:
            continue
        if not any(character.isalpha() for character in inner):
            continue
        placeholders.add(match)
    return sorted(placeholders)


def _render_order(order: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rendered = {
        **order,
        "caption": [_apply_context(item, context) for item in order["caption"]],
        "body": [_apply_context(item, context) for item in order["body"]],
        "submittedBy": [_apply_context(item, context) for item in order["submittedBy"]],
    }
    rendered["unresolvedPlaceholders"] = _collect_placeholders(render_proposed_order_markdown(rendered))
    return rendered


def render_proposed_order_markdown(order: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {order['title']}")
    lines.append("")
    for item in order["caption"]:
        lines.append(item)
    lines.append("")
    for item in order["body"]:
        lines.append(item)
    lines.append("")
    for item in order["submittedBy"]:
        lines.append(item)
    return "\n".join(lines).rstrip() + "\n"


def build_title18_filing_index() -> Dict[str, Any]:
    rendered = build_rendered_title18_filings()
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


def write_title18_filing_index(bundle: Dict[str, Any] | None = None) -> Dict[str, Path]:
    bundle = bundle or build_title18_filing_index()
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