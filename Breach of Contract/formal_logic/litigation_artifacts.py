"""
Build litigation-facing claim-chart and discovery artifacts from the breach report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path("/home/barberb/HACC/Breach of Contract")
BREACH_REPORT_PATH = ROOT / "outputs" / "title18_breach_report.json"


DISCOVERY_TARGETS = {
    "Certified copy or docket record for the eviction filing and service.": {
        "target": "HACC / Clackamas County Circuit Court",
        "request": "Produce the eviction complaint, summons, proof of service, filing receipt, and docket sheet for the March 31, 2026 eviction action.",
    },
    "Any HACC record claiming relocation was complete before March 31, 2026, to negate anticipated defenses.": {
        "target": "HACC",
        "request": "Produce every record, memo, or communication stating that Barber/Cortez relocation was complete or substantially complete before March 31, 2026.",
    },
    "Any written relocation-counseling logs or absence thereof.": {
        "target": "HACC",
        "request": "Produce all relocation counseling logs, calendars, case notes, call logs, and advisory-service records for the Barber/Cortez household, or certify none exist.",
    },
    "Any HACC payment ledger or relocation reimbursement file showing no commitment/payment.": {
        "target": "HACC",
        "request": "Produce the complete relocation-expense file, ledger entries, approvals, denials, and payment records for the Barber/Cortez household.",
    },
    "Any formal denial or refusal of an accessible ground-floor alternative.": {
        "target": "HACC",
        "request": "Produce all records of requests for accessible or ground-floor replacement units and all responses, denials, or proposed alternatives.",
    },
    "Comparability/HQS analysis documents for the offered unit.": {
        "target": "HACC",
        "request": "Produce HQS inspections, comparability analyses, accessibility evaluations, and approval notes for each replacement unit offered to the household.",
    },
    "Any internal Quantum intake log showing receipt date and no transmission.": {
        "target": "Quantum Residential",
        "request": "Produce intake logs, leasing-office receipt logs, scanning logs, CRM entries, and transmission records for the Barber/Cortez Blossom/Hillside packet.",
    },
    "Any later proof that Quantum eventually forwarded the packet, to assess duration and cure arguments.": {
        "target": "Quantum Residential / HACC",
        "request": "Produce every record showing whether, when, and how Quantum transmitted the packet to HACC, including email attachments and metadata.",
    },
    "Quantum email, CRM note, or witness statement showing an express false denial.": {
        "target": "Quantum Residential",
        "request": "Produce all communications, CRM notes, and staff statements concerning whether Quantum received or denied receiving the household application.",
    },
    "Any timestamped submission confirmation from the leasing office.": {
        "target": "Quantum Residential",
        "request": "Produce receipts, scans, timestamps, sign-in logs, surveillance retention notices, or other records confirming the date and manner of packet submission.",
    },
    "HUD complaint, escalation, or correspondence showing notice of HACC/Quantum noncompliance.": {
        "target": "HUD / Household records",
        "request": "Collect and produce all HUD-directed complaints, escalations, emails, portal submissions, and acknowledgements regarding Section 18 noncompliance.",
    },
    "Any HUD response or refusal to intervene after notice.": {
        "target": "HUD",
        "request": "Produce all HUD response letters, internal notes, enforcement referrals, and closure determinations concerning the household's relocation complaints.",
    },
    "Full packet contents and completeness checklist, in case the other side argues the submission was materially incomplete.": {
        "target": "Household / Quantum / HACC",
        "request": "Assemble the full submitted packet, attachment list, and any completeness checklist or deficiency notice tied to the submission.",
    },
}


def _load_report() -> Dict[str, Any]:
    return json.loads(BREACH_REPORT_PATH.read_text())


def build_claim_chart(report: Dict[str, Any]) -> Dict[str, Any]:
    defendants: Dict[str, Dict[str, Any]] = {}
    for finding in report["findings"]:
        actor = finding["actor"]
        if actor.startswith("person:"):
            continue
        bucket = defendants.setdefault(
            actor,
            {
                "actor": actor,
                "actorLabel": finding["actorLabel"],
                "claims": [],
            },
        )
        bucket["claims"].append(
            {
                "findingId": finding["findingId"],
                "disposition": finding["disposition"],
                "confidence": finding["confidence"],
                "rule": finding["rule"],
                "recipientLabels": finding["recipientLabels"],
                "obligationActions": [item["action"] for item in finding["obligations"]],
                "keyEvidenceIds": [item["id"] for item in finding["supportingEvidence"]],
                "keyEventIds": [item["id"] for item in finding["supportingEvents"]],
                "theme": finding["whyItMatters"],
                "missingProof": finding["missingProof"],
            }
        )
    return {
        "meta": report["meta"],
        "defendants": [item for item in defendants.values() if item["claims"]],
    }


def build_discovery_plan(report: Dict[str, Any]) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    seen = set()
    priority_map = {
        "likely_breach": "high",
        "supported_but_needs_corroboration": "medium",
        "possible_breach_needs_more_evidence": "medium",
        "no_current_breach_shown": "low",
    }
    for finding in report["findings"]:
        for gap in finding["missingProof"]:
            key = (finding["findingId"], gap)
            if key in seen:
                continue
            seen.add(key)
            target_info = DISCOVERY_TARGETS.get(
                gap,
                {
                    "target": "Unknown",
                    "request": gap,
                },
            )
            items.append(
                {
                    "findingId": finding["findingId"],
                    "actorLabel": finding["actorLabel"],
                    "priority": priority_map.get(finding["disposition"], "medium"),
                    "target": target_info["target"],
                    "gap": gap,
                    "request": target_info["request"],
                }
            )
    items.sort(key=lambda item: ({"high": 0, "medium": 1, "low": 2}[item["priority"]], item["target"], item["findingId"]))
    return {
        "meta": report["meta"],
        "requests": items,
    }


def render_claim_chart_markdown(chart: Dict[str, Any]) -> str:
    lines: List[str] = ["# Title 18 Claim Chart", ""]
    for defendant in chart["defendants"]:
        lines.append(f"## {defendant['actorLabel']}")
        lines.append("")
        for claim in defendant["claims"]:
            lines.append(f"### {claim['findingId']}")
            lines.append("")
            lines.append(f"- Disposition: `{claim['disposition']}`")
            lines.append(f"- Confidence: `{claim['confidence']}`")
            lines.append(f"- Recipients: {', '.join(claim['recipientLabels'])}")
            lines.append(f"- Rule: {claim['rule']}")
            lines.append(f"- Obligation actions: {'; '.join(claim['obligationActions'])}")
            lines.append(f"- Key evidence: {', '.join(claim['keyEvidenceIds'])}")
            lines.append(f"- Key events: {', '.join(claim['keyEventIds'])}")
            lines.append(f"- Theme: {claim['theme']}")
            if claim["missingProof"]:
                lines.append("- Missing proof:")
                for item in claim["missingProof"]:
                    lines.append(f"  - {item}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_discovery_plan_markdown(plan: Dict[str, Any]) -> str:
    lines: List[str] = ["# Title 18 Discovery Gap Plan", ""]
    for request in plan["requests"]:
        lines.append(f"## {request['findingId']}")
        lines.append("")
        lines.append(f"- Actor: {request['actorLabel']}")
        lines.append(f"- Priority: `{request['priority']}`")
        lines.append(f"- Target: {request['target']}")
        lines.append(f"- Gap: {request['gap']}")
        lines.append(f"- Proposed request: {request['request']}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = _load_report()
    chart = build_claim_chart(report)
    plan = build_discovery_plan(report)

    chart_json = ROOT / "outputs" / "title18_claim_chart.json"
    chart_md = ROOT / "outputs" / "title18_claim_chart.md"
    plan_json = ROOT / "outputs" / "title18_discovery_gap_plan.json"
    plan_md = ROOT / "outputs" / "title18_discovery_gap_plan.md"

    chart_json.write_text(json.dumps(chart, indent=2) + "\n")
    chart_md.write_text(render_claim_chart_markdown(chart))
    plan_json.write_text(json.dumps(plan, indent=2) + "\n")
    plan_md.write_text(render_discovery_plan_markdown(plan))

    print(chart_json)
    print(chart_md)
    print(plan_json)
    print(plan_md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
