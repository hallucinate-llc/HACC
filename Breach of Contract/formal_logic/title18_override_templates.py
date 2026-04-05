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
EDITABLE_HACC_OVERRIDES = ROOT / "title18_hacc_context_overrides.json"
EDITABLE_QUANTUM_OVERRIDES = ROOT / "title18_quantum_context_overrides.json"


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


def _merge_template_into_editable(existing: Dict[str, Any], template: Dict[str, Any]) -> Dict[str, Any]:
    merged = {
        "substitutions": dict(existing.get("substitutions", {})),
        "requiredUserInputs": dict(existing.get("requiredUserInputs", {})),
    }
    for section in ["substitutions", "requiredUserInputs"]:
        for key, value in template.get(section, {}).items():
            if key not in merged[section]:
                merged[section][key] = value
    return merged


def _load_editable_payload(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"substitutions": {}, "requiredUserInputs": {}}
    payload = json.loads(path.read_text())
    return {
        "substitutions": dict(payload.get("substitutions", {})),
        "requiredUserInputs": dict(payload.get("requiredUserInputs", {})),
    }


def _completion_summary(payload: Dict[str, Any]) -> Dict[str, int]:
    values = [
        *payload.get("substitutions", {}).values(),
        *payload.get("requiredUserInputs", {}).values(),
    ]
    filled = sum(1 for value in values if value not in {None, ""})
    total = len(values)
    return {
        "filledCount": filled,
        "missingCount": total - filled,
        "totalCount": total,
    }


def build_title18_override_templates(merged_order_track: str = "hacc") -> Dict[str, Any]:
    context = build_render_context()
    readiness = build_title18_readiness_report(merged_order_track=merged_order_track)
    hacc_missing = readiness["tracks"]["hacc"]["missingFields"]
    quantum_missing = readiness["tracks"]["quantum"]["missingFields"]

    hacc_editable = _merge_template_into_editable(
        _load_editable_payload(EDITABLE_HACC_OVERRIDES),
        _build_track_template(context, hacc_missing),
    )
    quantum_editable = _merge_template_into_editable(
        _load_editable_payload(EDITABLE_QUANTUM_OVERRIDES),
        _build_track_template(context, quantum_missing),
    )

    return {
        "meta": {
            "templateId": "title18_override_templates_001",
            "generatedAt": readiness["meta"]["generatedAt"],
            "mergedOrderTrack": merged_order_track,
            "overridePath": readiness["meta"]["overridePath"],
            "editableOverridePaths": {
                "hacc": str(EDITABLE_HACC_OVERRIDES),
                "quantum": str(EDITABLE_QUANTUM_OVERRIDES),
            },
        },
        "commonMissingFields": readiness["summary"]["commonMissingFields"],
        "templates": {
            "hacc": _build_track_template(context, hacc_missing),
            "quantum": _build_track_template(context, quantum_missing),
        },
        "editable": {
            "hacc": hacc_editable,
            "quantum": quantum_editable,
        },
        "completion": {
            "hacc": _completion_summary(hacc_editable),
            "quantum": _completion_summary(quantum_editable),
        },
    }


def render_title18_override_worksheet_markdown(bundle: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Override Worksheet")
    lines.append("")
    lines.append(f"- Override file: {bundle['meta']['overridePath']}")
    lines.append(f"- Editable HACC override file: {bundle['meta']['editableOverridePaths']['hacc']}")
    lines.append(f"- Editable Quantum override file: {bundle['meta']['editableOverridePaths']['quantum']}")
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
        lines.append(
            f"- Filled fields: {bundle['completion'][track]['filledCount']} / {bundle['completion'][track]['totalCount']}"
        )
        lines.append(f"- Missing fields: {bundle['completion'][track]['missingCount']}")
        lines.append("")
        lines.append("Substitutions:")
        for key in sorted(bundle["editable"][track]["substitutions"]):
            value = bundle["editable"][track]["substitutions"][key]
            lines.append(f"- {key}: {'' if value is None else value}")
        lines.append("")
        lines.append("Required user inputs:")
        for key in sorted(bundle["editable"][track]["requiredUserInputs"]):
            value = bundle["editable"][track]["requiredUserInputs"][key]
            lines.append(f"- {key}: {'' if value is None else value}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_override_templates(bundle: Dict[str, Any] | None = None, merged_order_track: str = "hacc") -> Dict[str, Path]:
    bundle = bundle or build_title18_override_templates(merged_order_track=merged_order_track)
    outputs = {
        "hacc_json": OUTPUTS / "title18_hacc_override_template.json",
        "quantum_json": OUTPUTS / "title18_quantum_override_template.json",
        "worksheet_markdown": OUTPUTS / "title18_override_worksheet.md",
        "editable_hacc_json": EDITABLE_HACC_OVERRIDES,
        "editable_quantum_json": EDITABLE_QUANTUM_OVERRIDES,
    }
    outputs["hacc_json"].write_text(json.dumps(bundle["templates"]["hacc"], indent=2) + "\n")
    outputs["quantum_json"].write_text(json.dumps(bundle["templates"]["quantum"], indent=2) + "\n")
    outputs["worksheet_markdown"].write_text(render_title18_override_worksheet_markdown(bundle))
    hacc_editable = _merge_template_into_editable(
        _load_editable_payload(outputs["editable_hacc_json"]),
        bundle["templates"]["hacc"],
    )
    quantum_editable = _merge_template_into_editable(
        _load_editable_payload(outputs["editable_quantum_json"]),
        bundle["templates"]["quantum"],
    )
    outputs["editable_hacc_json"].write_text(json.dumps(hacc_editable, indent=2) + "\n")
    outputs["editable_quantum_json"].write_text(json.dumps(quantum_editable, indent=2) + "\n")
    return outputs


def main() -> int:
    outputs = write_title18_override_templates()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())