"""
Build a consolidated operational status report for the Title 18 packet workflow.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_override_audit import build_title18_override_audit
from formal_logic.title18_override_templates import build_title18_override_templates
from formal_logic.title18_readiness import build_title18_readiness_report


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _track_override_paths(track: str) -> List[str]:
    base = "title18_render_context_overrides.json"
    if track == "hacc":
        return [base, "title18_hacc_context_overrides.json"]
    if track == "quantum":
        return [base, "title18_quantum_context_overrides.json"]
    raise ValueError(f"Unsupported track: {track}")


def _next_actions(track: str, audit: Dict[str, Any], readiness: Dict[str, Any]) -> List[str]:
    actions: List[str] = []
    if audit["unexpectedCount"]:
        actions.append(f"Remove or rename unexpected keys in {track.upper()} editable overrides before filing.")
    if audit["missingCount"]:
        actions.append(f"Fill the remaining {audit['missingCount']} editable override keys for the {track.upper()} track.")
    if readiness["missingCount"]:
        actions.append(f"Resolve the remaining {readiness['missingCount']} rendered filing placeholders for the {track.upper()} track.")
    if not actions:
        actions.append(f"Regenerate the {track.upper()} packet and perform a final filing review.")
    return actions


def build_title18_status_report() -> Dict[str, Any]:
    template_bundle = build_title18_override_templates()
    audit_report = build_title18_override_audit()
    tracks: Dict[str, Any] = {}

    for track in ["hacc", "quantum"]:
        readiness_report = build_title18_readiness_report(
            merged_order_track=track,
            override_paths=_track_override_paths(track),
        )
        audit_track = audit_report["tracks"][track]
        completion_track = template_bundle["completion"][track]
        readiness_track = readiness_report["tracks"][track]
        tracks[track] = {
            "editableOverridePath": audit_track["editableOverridePath"],
            "overrideCompletion": completion_track,
            "overrideAudit": {
                "ready": audit_track["ready"],
                "filledCount": audit_track["filledCount"],
                "missingCount": audit_track["missingCount"],
                "unexpectedCount": audit_track["unexpectedCount"],
                "missingKeys": audit_track["missingKeys"],
                "unexpectedKeys": audit_track["unexpectedKeys"],
            },
            "readiness": {
                "readyToFile": readiness_track["readyToFile"],
                "missingCount": readiness_track["missingCount"],
                "missingFields": readiness_track["missingFields"],
                "overridePaths": readiness_report["meta"]["overridePaths"],
            },
            "nextActions": _next_actions(track, audit_track, readiness_track),
        }

    return {
        "meta": {
            "statusId": "title18_status_report_001",
            "generatedAt": template_bundle["meta"]["generatedAt"],
            "worksheetPath": str(OUTPUTS / "title18_override_worksheet.md"),
            "auditPath": str(OUTPUTS / "title18_override_audit.md"),
        },
        "commands": {
            "doctor": "make doctor-title18",
            "prepOverrides": "make prep-title18-overrides",
            "auditOverrides": "make audit-title18-overrides",
            "buildStatus": "make status-title18",
            "regenHacc": "make regen-hacc",
            "regenQuantum": "make regen-quantum",
            "checkHacc": "make check-title18-hacc",
            "checkQuantum": "make check-title18-quantum",
        },
        "commonMissingFields": template_bundle["commonMissingFields"],
        "tracks": tracks,
    }


def render_title18_status_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Status Report")
    lines.append("")
    lines.append(f"- Worksheet: {report['meta']['worksheetPath']}")
    lines.append(f"- Override audit: {report['meta']['auditPath']}")
    lines.append("")
    lines.append("## Commands")
    lines.append("")
    lines.append(f"- Doctor run: {report['commands']['doctor']}")
    lines.append(f"- Refresh override templates: {report['commands']['prepOverrides']}")
    lines.append(f"- Audit editable overrides: {report['commands']['auditOverrides']}")
    lines.append(f"- Rebuild this status report: {report['commands']['buildStatus']}")
    lines.append(f"- Regenerate HACC packet: {report['commands']['regenHacc']}")
    lines.append(f"- Regenerate Quantum packet: {report['commands']['regenQuantum']}")
    lines.append(f"- Check HACC readiness: {report['commands']['checkHacc']}")
    lines.append(f"- Check Quantum readiness: {report['commands']['checkQuantum']}")
    lines.append("")
    lines.append("## Common Missing Fields")
    lines.append("")
    if report["commonMissingFields"]:
        for key in report["commonMissingFields"]:
            lines.append(f"- {key}")
    else:
        lines.append("- None")
    lines.append("")
    for track in ["hacc", "quantum"]:
        payload = report["tracks"][track]
        lines.append(f"## {track.upper()}")
        lines.append("")
        lines.append(f"- Editable override file: {payload['editableOverridePath']}")
        lines.append(
            f"- Override completion: {payload['overrideCompletion']['filledCount']} / {payload['overrideCompletion']['totalCount']}"
        )
        lines.append(f"- Override audit ready: {'yes' if payload['overrideAudit']['ready'] else 'no'}")
        lines.append(f"- Ready to file: {'yes' if payload['readiness']['readyToFile'] else 'no'}")
        lines.append(f"- Remaining rendered placeholders: {payload['readiness']['missingCount']}")
        lines.append("")
        lines.append("Next actions:")
        for item in payload["nextActions"]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_status_report(report: Dict[str, Any] | None = None) -> Dict[str, Path]:
    report = report or build_title18_status_report()
    outputs = {
        "json": OUTPUTS / "title18_status_report.json",
        "markdown": OUTPUTS / "title18_status_report.md",
    }
    outputs["json"].write_text(json.dumps(report, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_status_markdown(report))
    return outputs


def main() -> int:
    outputs = write_title18_status_report()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())