"""
Audit the editable Title 18 override files for missing and unexpected keys.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_override_templates import build_title18_override_templates


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _collect_section_keys(payload: Dict[str, Any], section: str) -> List[str]:
    return sorted(payload.get(section, {}).keys())


def _filled_keys(payload: Dict[str, Any]) -> List[str]:
    filled: List[str] = []
    for section in ["substitutions", "requiredUserInputs"]:
        for key, value in payload.get(section, {}).items():
            if value not in {None, ""}:
                filled.append(key)
    return sorted(filled)


def _missing_keys(payload: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
    missing: List[str] = []
    for section in ["substitutions", "requiredUserInputs"]:
        for key in template.get(section, {}):
            value = payload.get(section, {}).get(key)
            if value in {None, ""}:
                missing.append(key)
    return sorted(missing)


def _unexpected_keys(payload: Dict[str, Any], template: Dict[str, Any]) -> List[str]:
    unexpected: List[str] = []
    for section in ["substitutions", "requiredUserInputs"]:
        allowed = set(template.get(section, {}))
        for key in payload.get(section, {}):
            if key not in allowed:
                unexpected.append(key)
    return sorted(unexpected)


def build_title18_override_audit() -> Dict[str, Any]:
    bundle = build_title18_override_templates()
    tracks: Dict[str, Any] = {}
    for track in ["hacc", "quantum"]:
        editable = bundle["editable"][track]
        template = bundle["templates"][track]
        filled = _filled_keys(editable)
        missing = _missing_keys(editable, template)
        unexpected = _unexpected_keys(editable, template)
        tracks[track] = {
            "filledKeys": filled,
            "missingKeys": missing,
            "unexpectedKeys": unexpected,
            "filledCount": len(filled),
            "missingCount": len(missing),
            "unexpectedCount": len(unexpected),
            "ready": not missing and not unexpected,
            "editableOverridePath": bundle["meta"]["editableOverridePaths"][track],
        }
    return {
        "meta": {
            "auditId": "title18_override_audit_001",
            "generatedAt": bundle["meta"]["generatedAt"],
        },
        "tracks": tracks,
    }


def render_title18_override_audit_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Override Audit")
    lines.append("")
    for track in ["hacc", "quantum"]:
        payload = report["tracks"][track]
        lines.append(f"## {track.upper()}")
        lines.append("")
        lines.append(f"- Editable override file: {payload['editableOverridePath']}")
        lines.append(f"- Ready: {'yes' if payload['ready'] else 'no'}")
        lines.append(f"- Filled keys: {payload['filledCount']}")
        lines.append(f"- Missing keys: {payload['missingCount']}")
        lines.append(f"- Unexpected keys: {payload['unexpectedCount']}")
        lines.append("")
        lines.append("Missing keys:")
        if payload["missingKeys"]:
            for key in payload["missingKeys"]:
                lines.append(f"- {key}")
        else:
            lines.append("- None")
        lines.append("")
        lines.append("Unexpected keys:")
        if payload["unexpectedKeys"]:
            for key in payload["unexpectedKeys"]:
                lines.append(f"- {key}")
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_override_audit(report: Dict[str, Any] | None = None) -> Dict[str, Path]:
    report = report or build_title18_override_audit()
    outputs = {
        "json": OUTPUTS / "title18_override_audit.json",
        "markdown": OUTPUTS / "title18_override_audit.md",
    }
    outputs["json"].write_text(json.dumps(report, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_override_audit_markdown(report))
    return outputs


def main() -> int:
    outputs = write_title18_override_audit()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())