"""
Generate packet-specific override templates from the current Title 18 readiness report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_context import build_render_context
from formal_logic.title18_readiness import build_title18_readiness_report


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _build_track_template(context: Dict[str, Any], missing_fields: List[str]) -> Dict[str, Any]:
    substitutions: Dict[str, Any] = {}
    required_user_inputs: Dict[str, Any] = {}
    for field in missing_fields:
        if field in context["substitutions"]:
            substitutions[field] = context["substitutions"][field]
        elif field in context["requiredUserInputs"]:
            required_user_inputs[field] = context["requiredUserInputs"][field]
        else:
            required_user_inputs[field] = None
    return {
        "substitutions": substitutions,
        "requiredUserInputs": required_user_inputs,
    }


def build_title18_override_templates(merged_order_track: str = "hacc") -> Dict[str, Any]:
    context = build_render_context()
    readiness = build_title18_readiness_report(merged_order_track=merged_order_track)
    hacc_missing = readiness["tracks"]["hacc"]["missingFields"]
    quantum_missing = readiness["tracks"]["quantum"]["missingFields"]

    return {
        "meta": {
            "templateId": "title18_override_templates_001",
            "generatedAt": readiness["meta"]["generatedAt"],
            "mergedOrderTrack": merged_order_track,
            "overridePath": readiness["meta"]["overridePath"],
        },
        "commonMissingFields": readiness["summary"]["commonMissingFields"],
        "templates": {
            "hacc": _build_track_template(context, hacc_missing),
            "quantum": _build_track_template(context, quantum_missing),
        },
    }


def render_title18_override_worksheet_markdown(bundle: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Override Worksheet")
    lines.append("")
    lines.append(f"- Override file: {bundle['meta']['overridePath']}")
    lines.append(f"- Merged order track: {bundle['meta']['mergedOrderTrack']}")
    lines.append("")
    lines.append("## Common Missing Fields")
    lines.append("")
    if bundle["commonMissingFields"]:
        for field in bundle["commonMissingFields"]:
            lines.append(f"- {field}")
    else:
        lines.append("- None")
    lines.append("")
    for track in ["hacc", "quantum"]:
        lines.append(f"## {track.upper()} Template")
        lines.append("")
        lines.append("Substitutions:")
        for key in sorted(bundle["templates"][track]["substitutions"]):
            lines.append(f"- {key}: ")
        lines.append("")
        lines.append("Required user inputs:")
        for key in sorted(bundle["templates"][track]["requiredUserInputs"]):
            lines.append(f"- {key}: ")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_override_templates(bundle: Dict[str, Any] | None = None, merged_order_track: str = "hacc") -> Dict[str, Path]:
    bundle = bundle or build_title18_override_templates(merged_order_track=merged_order_track)
    outputs = {
        "hacc_json": OUTPUTS / "title18_hacc_override_template.json",
        "quantum_json": OUTPUTS / "title18_quantum_override_template.json",
        "worksheet_markdown": OUTPUTS / "title18_override_worksheet.md",
    }
    outputs["hacc_json"].write_text(json.dumps(bundle["templates"]["hacc"], indent=2) + "\n")
    outputs["quantum_json"].write_text(json.dumps(bundle["templates"]["quantum"], indent=2) + "\n")
    outputs["worksheet_markdown"].write_text(render_title18_override_worksheet_markdown(bundle))
    return outputs


def main() -> int:
    outputs = write_title18_override_templates()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())