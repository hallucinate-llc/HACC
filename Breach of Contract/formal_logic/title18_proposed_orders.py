"""
Shared proposed-order builders for Title 18 filing artifacts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List

from formal_logic.title18_context import build_render_context


PLACEHOLDER_PATTERN = re.compile(r"\[[A-Za-z0-9&'._/ -]+\]")
PLACEHOLDER_ALIASES = {
    "[Signature]": "[SIGNATURE]",
    "[Signature block]": "[SIGNATURE]",
}


def _base_caption() -> List[str]:
    return [
        "IN THE CIRCUIT COURT OF THE STATE OF OREGON FOR THE COUNTY OF CLACKAMAS",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY v. BENJAMIN JAY BARBER and JANE KAY CORTEZ",
        "Case No. [CASE NUMBER]",
    ]


def _apply_context(text: str, context: Dict[str, Any]) -> str:
    rendered = text
    items = sorted(
        {**context["requiredUserInputs"], **context["substitutions"]}.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for placeholder, value in items:
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
        placeholders.add(PLACEHOLDER_ALIASES.get(match, match))
    return sorted(placeholders)


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


def _render_order(order: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    rendered = {
        **order,
        "caption": [_apply_context(item, context) for item in order["caption"]],
        "body": [_apply_context(item, context) for item in order["body"]],
        "submittedBy": [_apply_context(item, context) for item in order["submittedBy"]],
    }
    rendered["unresolvedPlaceholders"] = _collect_placeholders(render_proposed_order_markdown(rendered))
    return rendered


def build_title18_proposed_orders() -> Dict[str, Any]:
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
            "[SIGNATURE]",
        ],
        "sourceMotionId": "title18_hacc_party_motion_001",
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
            "[SIGNATURE]",
        ],
        "sourceMotionId": "title18_quantum_party_motion_001",
    }
    orders = {
        "meta": {
            "packetId": "title18_proposed_orders_001",
            "generatedAt": context["substitutions"]["[DATE]"],
        },
        "orders": {
            "hacc": hacc_order,
            "quantum": quantum_order,
        },
        "renderContextId": context["meta"]["contextId"],
    }
    orders["renderedOrders"] = {
        key: _render_order(order, context) for key, order in orders["orders"].items()
    }
    return orders