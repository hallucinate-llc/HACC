"""
Evidence-backed breach analysis for the Title 18 GraphRAG obligation report.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OBLIGATION_REPORT_PATH = ROOT / "outputs" / "title18_graphrag_obligations.json"
JOINDER_FIXTURE_PATH = ROOT / "fixtures" / "joinder_quantum_case.json"


PARTY_LABELS = {
    "org:hacc": "Housing Authority of Clackamas County",
    "org:quantum": "Quantum Residential",
    "org:hud": "Housing and Urban Development",
    "person:benjamin_barber": "Benjamin Barber",
    "person:jane_cortez": "Jane Cortez",
}


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _find_obligations(report: Dict[str, Any], actor: str, recipient: str, action_substring: str) -> List[Dict[str, Any]]:
    results = []
    for item in report["obligations"]:
        if item["actor"] != actor or item["recipient"] != recipient:
            continue
        if action_substring.lower() in item["action"].lower():
            results.append(item)
    return results


def _evidence_map(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in fixture.get("evidence", [])}


def _event_map(fixture: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in fixture.get("events", [])}


def _summary_line(evidence: Dict[str, Any]) -> str:
    label = evidence.get("documentLabel") or evidence["id"]
    date = evidence.get("emailDate") or evidence.get("documentDate")
    text = evidence.get("sourceText", "")
    short = text if len(text) <= 220 else text[:217] + "..."
    if date:
        return f"{label} ({date}): {short}"
    return f"{label}: {short}"


def _event_line(event: Dict[str, Any]) -> str:
    date = event.get("time", "undated")
    details = json.dumps(event.get("details", {}), sort_keys=True)
    return f"{event['event']} ({date}): {details}"


def build_breach_report() -> Dict[str, Any]:
    obligation_report = _load_json(OBLIGATION_REPORT_PATH)
    fixture = _load_json(JOINDER_FIXTURE_PATH)
    evidence = _evidence_map(fixture)
    events = _event_map(fixture)

    findings: List[Dict[str, Any]] = []

    def add_finding(
        finding_id: str,
        actor: str,
        recipients: Sequence[str],
        disposition: str,
        confidence: str,
        rule: str,
        obligation_refs: Sequence[Dict[str, Any]],
        supporting_evidence_ids: Sequence[str],
        supporting_event_ids: Sequence[str],
        why: str,
        missing_proof: Sequence[str],
    ) -> None:
        findings.append(
            {
                "findingId": finding_id,
                "actor": actor,
                "actorLabel": PARTY_LABELS[actor],
                "recipients": list(recipients),
                "recipientLabels": [PARTY_LABELS[item] for item in recipients],
                "disposition": disposition,
                "confidence": confidence,
                "rule": rule,
                "whyItMatters": why,
                "obligations": [
                    {
                        "obligationId": item["obligation_id"],
                        "action": item["action"],
                        "modality": item["modality"],
                        "legalBasis": item["legal_basis"],
                    }
                    for item in obligation_refs
                ],
                "supportingEvidence": [
                    {
                        "id": item_id,
                        "summary": _summary_line(evidence[item_id]),
                    }
                    for item_id in supporting_evidence_ids
                ],
                "supportingEvents": [
                    {
                        "id": item_id,
                        "summary": _event_line(events[item_id]),
                    }
                    for item_id in supporting_event_ids
                ],
                "missingProof": list(missing_proof),
            }
        )

    add_finding(
        finding_id="breach:hacc:premature_eviction",
        actor="org:hacc",
        recipients=["person:benjamin_barber", "person:jane_cortez"],
        disposition="likely_breach",
        confidence="high",
        rule="A PHA may not evict before completing triggered Section 18 relocation duties.",
        obligation_refs=_find_obligations(obligation_report, "org:hacc", "person:benjamin_barber", "evict before relocation")
        + _find_obligations(obligation_report, "org:hacc", "person:jane_cortez", "evict before relocation"),
        supporting_evidence_ids=["evidence:section18_phase2_notice"],
        supporting_event_ids=["evt:e1_section18_hud_approval", "evt:e9_eviction_filed"],
        why="The record shows Section 18 relocation was triggered in September 2024, but the March 31, 2026 eviction event itself states relocation remained incomplete.",
        missing_proof=[
            "Certified copy or docket record for the eviction filing and service.",
            "Any HACC record claiming relocation was complete before March 31, 2026, to negate anticipated defenses.",
        ],
    )

    add_finding(
        finding_id="breach:hacc:relocation_services",
        actor="org:hacc",
        recipients=["person:benjamin_barber", "person:jane_cortez"],
        disposition="likely_breach",
        confidence="high",
        rule="Once Phase II approval and displacement are triggered, HACC must provide counseling and moving-expense support before displacement is completed.",
        obligation_refs=_find_obligations(obligation_report, "org:hacc", "person:benjamin_barber", "relocation counseling")
        + _find_obligations(obligation_report, "org:hacc", "person:jane_cortez", "relocation counseling")
        + _find_obligations(obligation_report, "org:hacc", "person:benjamin_barber", "moving expenses")
        + _find_obligations(obligation_report, "org:hacc", "person:jane_cortez", "moving expenses"),
        supporting_evidence_ids=["evidence:section18_phase2_notice"],
        supporting_event_ids=["evt:e1_section18_hud_approval", "evt:e9_eviction_filed"],
        why="The strongest current proof is HACC's own event record that, as of the eviction deadline, there was still no counseling and no relocation expenses.",
        missing_proof=[
            "Any written relocation-counseling logs or absence thereof.",
            "Any HACC payment ledger or relocation reimbursement file showing no commitment/payment.",
        ],
    )

    add_finding(
        finding_id="breach:hacc:inaccessible_replacement_offer",
        actor="org:hacc",
        recipients=["person:benjamin_barber", "person:jane_cortez"],
        disposition="likely_breach",
        confidence="high",
        rule="Replacement housing offered under the relocation track must be comparable and, on this record, should accommodate the household's mobility limitations.",
        obligation_refs=_find_obligations(obligation_report, "org:hacc", "person:benjamin_barber", "comparable replacement housing")
        + _find_obligations(obligation_report, "org:hacc", "person:jane_cortez", "comparable replacement housing"),
        supporting_evidence_ids=["evidence:admin_plan_excluded_units", "evidence:accommodation_records"],
        supporting_event_ids=["evt:e8_third_floor_unit_offered"],
        why="The record ties Blossom and Hillside Manor to replacement housing for a demolished project, yet the concrete offer identified in the timeline was a third-floor unit that the household's mobility scooter could not access.",
        missing_proof=[
            "Any formal denial or refusal of an accessible ground-floor alternative.",
            "Comparability/HQS analysis documents for the offered unit.",
        ],
    )

    add_finding(
        finding_id="breach:quantum:packet_forwarding",
        actor="org:quantum",
        recipients=["org:hacc", "person:benjamin_barber", "person:jane_cortez"],
        disposition="likely_breach",
        confidence="high",
        rule="A property manager handling the replacement-housing intake path must process and forward submitted materials instead of obstructing the intake chain.",
        obligation_refs=_find_obligations(obligation_report, "org:quantum", "org:hacc", "forward resident intake")
        + _find_obligations(obligation_report, "org:quantum", "person:benjamin_barber", "accept, process, and transmit")
        + _find_obligations(obligation_report, "org:quantum", "person:jane_cortez", "accept, process, and transmit"),
        supporting_evidence_ids=[
            "evidence:ferron_email_jan26_hacc_directs_quantum",
            "evidence:vera_application_owner_agent_duty",
            "evidence:blossom_graphrag_pbv_waitlist",
        ],
        supporting_event_ids=[
            "evt:e3_blossom_application_submitted",
            "evt:e4_ferron_acknowledges_quantum_received_packet",
            "evt:e5_ferron_directs_quantum_to_forward",
        ],
        why="The strongest evidence is a direct HACC acknowledgement that Quantum staff received the packet but did not provide it to HACC, followed by an instruction to Quantum to send it.",
        missing_proof=[
            "Any internal Quantum intake log showing receipt date and no transmission.",
            "Any later proof that Quantum eventually forwarded the packet, to assess duration and cure arguments.",
        ],
    )

    add_finding(
        finding_id="breach:quantum:false_denial_or_obstruction",
        actor="org:quantum",
        recipients=["person:benjamin_barber", "person:jane_cortez"],
        disposition="supported_but_needs_corroboration",
        confidence="medium",
        rule="If Quantum falsely denied receiving the application after receipt, that would reinforce obstruction and bad-faith processing.",
        obligation_refs=_find_obligations(obligation_report, "org:quantum", "person:benjamin_barber", "accept, process, and transmit")
        + _find_obligations(obligation_report, "org:quantum", "person:jane_cortez", "accept, process, and transmit"),
        supporting_evidence_ids=["evidence:email_falsely_claimed_quote"],
        supporting_event_ids=["evt:e7_household_asserts_falsely_claimed"],
        why="The current proof is household testimony/email, which is useful but not yet as strong as the Ferron admission regarding non-transmission.",
        missing_proof=[
            "Quantum email, CRM note, or witness statement showing an express false denial.",
            "Any timestamped submission confirmation from the leasing office.",
        ],
    )

    add_finding(
        finding_id="breach:hud:oversight",
        actor="org:hud",
        recipients=["org:hacc", "person:benjamin_barber", "person:jane_cortez"],
        disposition="possible_breach_needs_more_evidence",
        confidence="low",
        rule="HUD's approval role can imply a continuing monitoring/enforcement obligation, but breach requires evidence of notice plus non-enforcement.",
        obligation_refs=_find_obligations(obligation_report, "org:hud", "org:hacc", "monitor and enforce")
        + _find_obligations(obligation_report, "org:hud", "person:benjamin_barber", "monitor and enforce")
        + _find_obligations(obligation_report, "org:hud", "person:jane_cortez", "monitor and enforce"),
        supporting_evidence_ids=["evidence:section18_phase2_notice"],
        supporting_event_ids=["evt:e1_section18_hud_approval"],
        why="The current file clearly shows HUD approval, but it does not yet show HUD received notice of the later compliance failures and declined to act.",
        missing_proof=[
            "HUD complaint, escalation, or correspondence showing notice of HACC/Quantum noncompliance.",
            "Any HUD response or refusal to intervene after notice.",
        ],
    )

    add_finding(
        finding_id="no_breach:household:submission_duty",
        actor="person:benjamin_barber",
        recipients=["org:quantum"],
        disposition="no_current_breach_shown",
        confidence="medium",
        rule="The household's main application-duty issue is whether they submitted the required packet; current evidence tends to show submission, not noncompliance.",
        obligation_refs=_find_obligations(obligation_report, "person:benjamin_barber", "org:quantum", "submit complete application")
        + _find_obligations(obligation_report, "person:jane_cortez", "org:quantum", "submit complete application"),
        supporting_evidence_ids=["evidence:ferron_email_jan26_hacc_directs_quantum"],
        supporting_event_ids=["evt:e3_blossom_application_submitted", "evt:e4_ferron_acknowledges_quantum_received_packet"],
        why="The best present evidence indicates the packet was submitted at the Quantum office and later acknowledged as received there.",
        missing_proof=[
            "Full packet contents and completeness checklist, in case the other side argues the submission was materially incomplete.",
        ],
    )

    likely = [item for item in findings if item["disposition"] == "likely_breach"]
    return {
        "meta": {
            "generatedFrom": str(OBLIGATION_REPORT_PATH),
            "fixtureUsed": str(JOINDER_FIXTURE_PATH),
            "findingCount": len(findings),
            "likelyBreachCount": len(likely),
        },
        "summary": {
            "strongestLikelyBreaches": [
                "HACC: premature eviction before relocation completion",
                "HACC: failure to provide relocation counseling and moving-expense support",
                "HACC: inaccessible/non-comparable replacement housing offer",
                "Quantum: failure to process and forward the intake packet",
            ],
            "weakerOrDevelopingTheories": [
                "Quantum falsely denying receipt of the application",
                "HUD failing to monitor or enforce after approval",
            ],
            "currentNoBreachShowing": [
                "No strong current evidence that Benjamin Barber or Jane Cortez breached the packet-submission duty",
            ],
        },
        "findings": findings,
    }


def render_breach_report_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Breach Analysis")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Likely breach findings: {report['meta']['likelyBreachCount']}")
    for item in report["summary"]["strongestLikelyBreaches"]:
        lines.append(f"- {item}")
    for item in report["summary"]["weakerOrDevelopingTheories"]:
        lines.append(f"- Developing theory: {item}")
    for item in report["summary"]["currentNoBreachShowing"]:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    for finding in report["findings"]:
        lines.append(f"### {finding['findingId']}")
        lines.append("")
        lines.append(f"- Actor: {finding['actorLabel']}")
        lines.append(f"- Recipients: {', '.join(finding['recipientLabels'])}")
        lines.append(f"- Disposition: `{finding['disposition']}`")
        lines.append(f"- Confidence: `{finding['confidence']}`")
        lines.append(f"- Rule: {finding['rule']}")
        lines.append(f"- Why it matters: {finding['whyItMatters']}")
        lines.append("- Obligations:")
        for item in finding["obligations"]:
            lines.append(f"  - `{item['obligationId']}`: {item['action']} ({item['modality']})")
        lines.append("- Supporting evidence:")
        for item in finding["supportingEvidence"]:
            lines.append(f"  - `{item['id']}`: {item['summary']}")
        lines.append("- Supporting events:")
        for item in finding["supportingEvents"]:
            lines.append(f"  - `{item['id']}`: {item['summary']}")
        lines.append("- Missing proof:")
        for item in finding["missingProof"]:
            lines.append(f"  - {item}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    report = build_breach_report()
    json_path = ROOT / "outputs" / "title18_breach_report.json"
    md_path = ROOT / "outputs" / "title18_breach_report.md"
    json_path.write_text(json.dumps(report, indent=2) + "\n")
    md_path.write_text(render_breach_report_markdown(report))
    print(json_path)
    print(md_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
