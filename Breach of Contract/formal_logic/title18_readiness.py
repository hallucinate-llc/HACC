"""
Build a readiness report for the Title 18 filing packets.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from formal_logic.title18_context import build_render_context
from formal_logic.title18_final_packet import build_title18_final_packet
from formal_logic.title18_filing_index import build_title18_filing_index


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


def _filled_override_fields(context: Dict[str, Any]) -> List[str]:
    filled: List[str] = []
    defaults = {
        "[DATE]",
        "[date]",
        "[FOR THE COUNTY OF [COUNTY]]",
        "[COUNTY]",
        "[IN THE CIRCUIT COURT OF THE STATE OF OREGON]",
        "[TENANT FIRST NAMES]",
        "[TENANT NAMES]",
        "[DEFENDANT NAME]",
        "[DEFENDANT NAMES]",
        "[PLAINTIFF NAME]",
        "[STATE OF OREGON / COUNTY / COURT NAME]",
        "[Insert third option as reflected in documents/communications]",
    }
    for key, value in context["substitutions"].items():
        if value is not None and key not in defaults:
            filled.append(key)
    for key, value in context["requiredUserInputs"].items():
        if value is not None:
            filled.append(key)
    return sorted(set(filled))


def build_title18_readiness_report(merged_order_track: str = "hacc") -> Dict[str, Any]:
    context = build_render_context()
    index = build_title18_filing_index(merged_order_track=merged_order_track)
    hacc_packet = build_title18_final_packet("hacc")
    quantum_packet = build_title18_final_packet("quantum")

    hacc_missing = hacc_packet["aggregateUnresolvedPlaceholders"]
    quantum_missing = quantum_packet["aggregateUnresolvedPlaceholders"]
    common_missing = sorted(set(hacc_missing) & set(quantum_missing))
    filled_fields = _filled_override_fields(context)

    return {
        "meta": {
            "reportId": "title18_readiness_report_001",
            "generatedAt": context["substitutions"]["[DATE]"],
            "mergedOrderTrack": merged_order_track,
            "overridePath": context["meta"]["overridePath"],
        },
        "summary": {
            "filledOverrideFieldCount": len(filled_fields),
            "filledOverrideFields": filled_fields,
            "commonMissingFields": common_missing,
            "commonMissingCount": len(common_missing),
        },
        "tracks": {
            "hacc": {
                "readyToFile": not hacc_missing,
                "missingFields": hacc_missing,
                "missingCount": len(hacc_missing),
                "packetId": hacc_packet["meta"]["packetId"],
            },
            "quantum": {
                "readyToFile": not quantum_missing,
                "missingFields": quantum_missing,
                "missingCount": len(quantum_missing),
                "packetId": quantum_packet["meta"]["packetId"],
            },
        },
        "indexId": index["meta"]["indexId"],
    }


def render_title18_readiness_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Readiness Report")
    lines.append("")
    lines.append(f"- Merged order track: {report['meta']['mergedOrderTrack']}")
    lines.append(f"- Override file: {report['meta']['overridePath']}")
    lines.append(f"- Filled override fields: {report['summary']['filledOverrideFieldCount']}")
    lines.append("")
    lines.append("## Common Missing Fields")
    lines.append("")
    if report["summary"]["commonMissingFields"]:
        for item in report["summary"]["commonMissingFields"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines.append("")
    lines.append("## Track Status")
    lines.append("")
    for track, payload in report["tracks"].items():
        lines.append(f"### {track.upper()}")
        lines.append("")
        lines.append(f"- Ready to file: {'yes' if payload['readyToFile'] else 'no'}")
        lines.append(f"- Missing count: {payload['missingCount']}")
        for item in payload["missingFields"]:
            lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_readiness_report(report: Dict[str, Any] | None = None, merged_order_track: str = "hacc") -> Dict[str, Path]:
    report = report or build_title18_readiness_report(merged_order_track=merged_order_track)
    outputs = {
        "json": OUTPUTS / "title18_readiness_report.json",
        "markdown": OUTPUTS / "title18_readiness_report.md",
    }
    outputs["json"].write_text(json.dumps(report, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_readiness_markdown(report))
    return outputs


def main() -> int:
    outputs = write_title18_readiness_report()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())