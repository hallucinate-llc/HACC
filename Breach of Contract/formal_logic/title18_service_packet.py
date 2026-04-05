"""
Build service-ready companion documents for the rendered Title 18 filing packet.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List

from formal_logic.title18_context import build_render_context


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _apply_context(text: str, context: Dict[str, Any]) -> str:
    rendered = text
    for placeholder, value in {**context["requiredUserInputs"], **context["substitutions"]}.items():
        if value:
            rendered = rendered.replace(placeholder, str(value))
    return rendered


def build_title18_service_packet(override_paths: Iterable[Path | str] | None = None) -> Dict[str, Any]:
    context = build_render_context(override_paths=override_paths)
    certificate_lines = [
        "IN THE CIRCUIT COURT OF THE STATE OF OREGON FOR THE COUNTY OF CLACKAMAS",
        "HOUSING AUTHORITY OF CLACKAMAS COUNTY, Plaintiff,",
        "v.",
        "Benjamin Jay Barber and Jane Kay Cortez, Defendant.",
        "Case No. [CASE NUMBER]",
        "",
        "CERTIFICATE OF SERVICE",
        "",
        "I certify that on [DATE], I served true and correct copies of the following documents:",
        "1. Rendered motion selected for filing;",
        "2. Matching proposed order;",
        "3. Supporting declarations and exhibits;",
        "4. Any related joinder or discovery attachments.",
        "",
        "Service recipients:",
        "- [HACC COUNSEL NAME], counsel for HACC, at [HACC COUNSEL ADDRESS], by [SERVICE METHOD].",
        "- [QUANTUM'S REGISTERED AGENT NAME], registered agent for Quantum Residential, at [QUANTUM'S REGISTERED AGENT ADDRESS], by [SERVICE METHOD].",
        "",
        "I declare under penalty of perjury that the foregoing is true and correct.",
        "",
        "DATED: [DATE]",
        "[SIGNATURE]",
        "[NAME]",
        "[ADDRESS]",
        "[PHONE]",
        "[EMAIL]",
    ]
    checklist_items = [
        "Confirm the selected motion, matched proposed order, and certificate of service all carry the same [CASE NUMBER].",
        "Fill judge, counsel, entity-name, signature, and service-method fields before filing.",
        "Attach the motion-specific exhibits and declarations referenced in the rendered filing index.",
        "Serve HACC counsel and Quantum's registered agent using a method allowed by the applicable Oregon rules and local court practice.",
        "Retain a timestamped copy of the filed packet and service proof for the hearing binder.",
    ]
    rendered_certificate = "\n".join(_apply_context(line, context) for line in certificate_lines).rstrip() + "\n"
    rendered_checklist = {
        "title": "Title 18 Filing Service Checklist",
        "items": [_apply_context(item, context) for item in checklist_items],
    }
    return {
        "meta": {
            "packetId": "title18_service_packet_001",
            "generatedAt": context["substitutions"]["[DATE]"],
            "contextId": context["meta"]["contextId"],
        },
        "certificateOfService": {
            "title": "Title 18 Certificate of Service",
            "markdown": rendered_certificate,
            "unresolvedPlaceholders": [
                "[CASE NUMBER]",
                "[HACC COUNSEL NAME]",
                "[HACC COUNSEL ADDRESS]",
                "[QUANTUM'S REGISTERED AGENT NAME]",
                "[QUANTUM'S REGISTERED AGENT ADDRESS]",
                "[SERVICE METHOD]",
                "[SIGNATURE]",
                "[NAME]",
                "[ADDRESS]",
                "[PHONE]",
                "[EMAIL]",
            ],
        },
        "checklist": rendered_checklist,
    }


def render_service_checklist_markdown(packet: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append(f"# {packet['checklist']['title']}")
    lines.append("")
    for item in packet["checklist"]["items"]:
        lines.append(f"- {item}")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_service_packet(
    packet: Dict[str, Any] | None = None,
    override_paths: Iterable[Path | str] | None = None,
) -> Dict[str, Path]:
    packet = packet or build_title18_service_packet(override_paths=override_paths)
    outputs = {
        "packet_json": OUTPUTS / "title18_service_packet.json",
        "certificate_markdown": OUTPUTS / "title18_certificate_of_service.md",
        "checklist_markdown": OUTPUTS / "title18_service_checklist.md",
    }
    outputs["packet_json"].write_text(json.dumps(packet, indent=2) + "\n")
    outputs["certificate_markdown"].write_text(packet["certificateOfService"]["markdown"])
    outputs["checklist_markdown"].write_text(render_service_checklist_markdown(packet))
    return outputs


def main() -> int:
    outputs = write_title18_service_packet()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())