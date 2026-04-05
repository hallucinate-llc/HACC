"""
Assemble the generated Title 18 obligation, breach, discovery, and reasoning artifacts
into one litigation-ready filing bundle.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"


ARTIFACT_PATHS = {
    "obligationReport": OUTPUTS / "title18_graphrag_obligations.json",
    "breachReport": OUTPUTS / "title18_breach_report.json",
    "claimChart": OUTPUTS / "title18_claim_chart.json",
    "discoveryGapPlan": OUTPUTS / "title18_discovery_gap_plan.json",
    "reasoningManifest": OUTPUTS / "title18_reasoning_exports_manifest.json",
    "prologExport": OUTPUTS / "title18_obligations.pl",
    "dcecExport": OUTPUTS / "title18_obligations_dcec.pl",
    "flogicExport": OUTPUTS / "title18_obligations.flogic",
}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _read_text(path: Path) -> str:
    return path.read_text()


def _artifact_entry(label: str, path: Path, why: str, kind: str) -> Dict[str, Any]:
    return {
        "label": label,
        "path": str(path),
        "kind": kind,
        "whyOpenThis": why,
        "exists": path.exists(),
    }


def build_title18_filing_bundle() -> Dict[str, Any]:
    obligation_report = _load_json(ARTIFACT_PATHS["obligationReport"])
    breach_report = _load_json(ARTIFACT_PATHS["breachReport"])
    claim_chart = _load_json(ARTIFACT_PATHS["claimChart"])
    discovery_plan = _load_json(ARTIFACT_PATHS["discoveryGapPlan"])
    reasoning_manifest = _load_json(ARTIFACT_PATHS["reasoningManifest"])

    artifacts = [
        _artifact_entry(
            "Obligation report",
            ARTIFACT_PATHS["obligationReport"],
            "Open this for the full party-to-party obligation matrix, event extraction, and formal models.",
            "json",
        ),
        _artifact_entry(
            "Breach report",
            ARTIFACT_PATHS["breachReport"],
            "Open this for the strongest current breach theories and missing-proof gaps.",
            "json",
        ),
        _artifact_entry(
            "Claim chart",
            ARTIFACT_PATHS["claimChart"],
            "Open this for defendant-by-defendant claim framing keyed to obligations and evidence.",
            "json",
        ),
        _artifact_entry(
            "Discovery gap plan",
            ARTIFACT_PATHS["discoveryGapPlan"],
            "Open this for prioritized requests for production and missing-proof targets.",
            "json",
        ),
        _artifact_entry(
            "Prolog export",
            ARTIFACT_PATHS["prologExport"],
            "Open this to feed obligation facts and derived predicates into Prolog-style tooling.",
            "prolog",
        ),
        _artifact_entry(
            "DCEC export",
            ARTIFACT_PATHS["dcecExport"],
            "Open this to feed Happens/Initiates/HoldsAt clauses into event-calculus reasoning tools.",
            "prolog",
        ),
        _artifact_entry(
            "F-logic export",
            ARTIFACT_PATHS["flogicExport"],
            "Open this to inspect frame-oriented obligation objects and slot values.",
            "flogic",
        ),
    ]

    likely_breaches = breach_report["summary"]["strongestLikelyBreaches"]
    developing = breach_report["summary"]["weakerOrDevelopingTheories"]
    no_breach = breach_report["summary"]["currentNoBreachShowing"]
    urgent_requests = [item for item in discovery_plan["requests"] if item["priority"] == "high"]
    obligation_counts_by_actor: Dict[str, int] = {}
    for actor, recipients in obligation_report["obligationMatrix"].items():
        obligation_counts_by_actor[actor] = sum(len(items) for items in recipients.values())

    return {
        "meta": {
            "bundleId": "title18_filing_packet_001",
            "generatedAt": obligation_report["metadata"]["generatedAt"],
            "generatedFrom": str(OUTPUTS),
            "caseFocus": "Title 18 demolition relocation obligations and inter-party breaches",
            "recommendedFirstStop": str(ARTIFACT_PATHS["breachReport"]),
        },
        "summary": {
            "documentsScanned": obligation_report["metadata"]["documentsScanned"],
            "eventsExtracted": obligation_report["metadata"]["eventsExtracted"],
            "obligationCount": len(obligation_report["obligations"]),
            "likelyBreachCount": breach_report["meta"]["likelyBreachCount"],
            "claimCount": sum(len(item["claims"]) for item in claim_chart["defendants"]),
            "highPriorityDiscoveryCount": len(urgent_requests),
            "reasoningExports": reasoning_manifest["exports"],
        },
        "topline": {
            "likelyBreaches": likely_breaches,
            "developingTheories": developing,
            "currentNoBreachShowing": no_breach,
        },
        "partyObligationCounts": obligation_counts_by_actor,
        "artifacts": artifacts,
        "priorityDiscoveryRequests": urgent_requests,
        "embedded": {
            "breachReport": breach_report,
            "claimChart": claim_chart,
            "discoveryGapPlan": discovery_plan,
        },
    }


def render_title18_filing_bundle_markdown(bundle: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Filing Packet")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Bundle ID: {bundle['meta']['bundleId']}")
    lines.append(f"- Documents scanned: {bundle['summary']['documentsScanned']}")
    lines.append(f"- Events extracted: {bundle['summary']['eventsExtracted']}")
    lines.append(f"- Obligations computed: {bundle['summary']['obligationCount']}")
    lines.append(f"- Likely breach findings: {bundle['summary']['likelyBreachCount']}")
    lines.append(f"- High-priority discovery requests: {bundle['summary']['highPriorityDiscoveryCount']}")
    lines.append("")
    lines.append("## Topline")
    lines.append("")
    for item in bundle["topline"]["likelyBreaches"]:
        lines.append(f"- Likely breach: {item}")
    for item in bundle["topline"]["developingTheories"]:
        lines.append(f"- Developing theory: {item}")
    for item in bundle["topline"]["currentNoBreachShowing"]:
        lines.append(f"- Current no-breach showing: {item}")
    lines.append("")
    lines.append("## Artifacts")
    lines.append("")
    for artifact in bundle["artifacts"]:
        lines.append(f"- {artifact['label']}: {artifact['path']}")
        lines.append(f"  Why open this: {artifact['whyOpenThis']}")
    lines.append("")
    lines.append("## Priority Discovery Requests")
    lines.append("")
    for item in bundle["priorityDiscoveryRequests"]:
        lines.append(f"- {item['findingId']}: {item['request']}")
    return "\n".join(lines).rstrip() + "\n"


def write_title18_filing_bundle(bundle: Dict[str, Any] | None = None) -> Dict[str, Path]:
    bundle = bundle or build_title18_filing_bundle()
    outputs = {
        "json": OUTPUTS / "title18_filing_packet.json",
        "markdown": OUTPUTS / "title18_filing_packet.md",
        "manifest": OUTPUTS / "title18_filing_packet_manifest.json",
    }
    outputs["json"].write_text(json.dumps(bundle, indent=2) + "\n")
    outputs["markdown"].write_text(render_title18_filing_bundle_markdown(bundle))
    outputs["manifest"].write_text(
        json.dumps(
            {
                "bundleId": bundle["meta"]["bundleId"],
                "generatedAt": bundle["meta"]["generatedAt"],
                "artifactCount": len(bundle["artifacts"]),
                "recommendedFirstStop": bundle["meta"]["recommendedFirstStop"],
                "paths": {key: str(path) for key, path in outputs.items()},
            },
            indent=2,
        )
        + "\n"
    )
    return outputs


def main() -> int:
    outputs = write_title18_filing_bundle()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())