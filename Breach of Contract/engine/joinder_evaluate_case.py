#!/usr/bin/env python3
"""Evaluate the joinder eviction-defense case fixture.

Parallel to evaluate_case.py, but specific to the HACC v. Barber/Cortez
Motion for Joinder of Quantum Residential case.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Finding → fact key mapping (mirrored from joinder_grounding.py)
JOINDER_FINDING_FACT_SOURCES: Dict[str, List[str]] = {
    "joinder": [
        "hacc_routed_intake_through_quantum_office",
        "quantum_received_cortez_documents",
        "quantum_failed_to_transmit_to_hacc",
        "quantum_falsely_denied_receiving_application",
        "joint_email_notice_hacc_and_quantum",
        "ferron_misrepresentation_quantum_separate",
        "ferron_misrepresentation_contradicted_by_admin_plan",
        "household_still_in_eviction_no_completed_relocation",
    ],
    "successorInInterest": [
        "hacc_pha_owns_hillside_manor",
        "quantum_named_pm_admin_plan_ch17",
        "quantum_named_pm_admin_plan_ch18_rad",
        "hillside_manor_lp_rad_successor",
        "eminent_domain_acquisition_documented",
        "rad_conversion_closed_2021_01_01",
        "rad_pih_2019_23_governs",
        "quantum_portfolio_wide_hacc_relationship",
    ],
    "section18Violation": [
        "section18_phase2_notice_served_sept_2024",
        "no_hqs_comparability_analysis_produced",
        "no_relocation_expenses_paid",
        "no_counseling_provided",
        "no_consultation_records_produced",
        "household_still_in_eviction_no_completed_relocation",
    ],
    "radObligations": [
        "hillside_manor_lp_rad_successor",
        "rad_conversion_closed_2021_01_01",
        "rad_pih_2019_23_governs",
        "quantum_named_pm_admin_plan_ch18_rad",
    ],
    "disabilityAccommodation": [
        "third_floor_unit_offered_mobility_impaired",
        "disability_accommodation_unmet",
    ],
    "preventionDefense": [
        "quantum_failed_to_transmit_to_hacc",
        "quantum_falsely_denied_receiving_application",
        "ferron_misrepresentation_quantum_separate",
        "ferron_misrepresentation_contradicted_by_admin_plan",
        "household_still_in_eviction_no_completed_relocation",
    ],
}

# Finding → authority ID mapping (mirrored from joinder_grounding.py)
JOINDER_FINDING_AUTHORITY_SOURCES: Dict[str, List[str]] = {
    "joinder": ["orcp_29a", "orcp_22b", "ors_105_135_eviction_defense"],
    "successorInInterest": ["hud_pih_2019_23_rad", "hacc_admin_plan_rad_obligations"],
    "section18Violation": [
        "usc_1437p_section18",
        "cfr_970_7",
        "cfr_970_21",
        "ors_105_135_eviction_defense",
    ],
    "radObligations": ["hud_pih_2019_23_rad", "hacc_admin_plan_rad_obligations"],
    "disabilityAccommodation": ["cfr_8_disability", "fha_42_usc_3604", "giebeler"],
    "preventionDefense": ["orcp_29a", "ors_105_135_eviction_defense"],
}


def _resolve_facts(payload: Dict[str, Any]) -> tuple[Dict[str, bool], List[Dict[str, Any]]]:
    """Merge assertedFacts and acceptedFindings; report conflicts."""
    asserted = payload["assertedFacts"]
    accepted = payload.get("acceptedFindings", {})
    resolved = dict(asserted)
    fact_conflicts: List[Dict[str, Any]] = []
    for key, accepted_value in accepted.items():
        asserted_value = asserted.get(key)
        if asserted_value is not None and asserted_value != accepted_value:
            fact_conflicts.append(
                {
                    "fact": key,
                    "asserted": asserted_value,
                    "accepted": accepted_value,
                }
            )
        resolved[key] = accepted_value
    return resolved, fact_conflicts


def _authority_map(authorities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    """Route authorities into joinder finding buckets."""

    def slim(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        return [
            {
                "id": item["id"],
                "label": item["label"],
                "weight": item["weight"],
            }
            for item in items
        ]

    buckets = {
        "joinder": [],
        "successorInInterest": [],
        "section18Violation": [],
        "radObligations": [],
        "disabilityAccommodation": [],
        "preventionDefense": [],
    }

    for authority in authorities:
        label = (authority["label"] + " " + authority.get("notes", "")).lower()
        citation = (authority.get("citation") or "").lower()
        text = f"{label} {citation}"

        if any(term in text for term in ["orcp 29", "joinder", "compulsory"]):
            buckets["joinder"].append(authority)
        if any(term in text for term in ["successor", "rad", "property management"]):
            buckets["successorInInterest"].append(authority)
        if any(term in text for term in ["section 18", "1437p", "demolition", "disposition"]):
            buckets["section18Violation"].append(authority)
        if any(term in text for term in ["rad", "pih 2019", "tenant protections"]):
            buckets["radObligations"].append(authority)
        if any(term in text for term in ["disability", "accommodation", "handicap"]):
            buckets["disabilityAccommodation"].append(authority)
        if any(term in text for term in ["estoppel", "defense", "prevention"]):
            buckets["preventionDefense"].append(authority)

    return {key: slim(value) for key, value in buckets.items()}


def _evidence_support_map(evidence: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Index evidence by fact/finding it supports."""
    support: Dict[str, List[Dict[str, Any]]] = {}
    for item in evidence:
        for target in item.get("supports", []):
            support.setdefault(target, []).append(
                {
                    "id": item["id"],
                    "type": item["type"],
                    "status": item["status"],
                    "confidence": item.get("confidence"),
                }
            )
    return support


def _finding_evidence(
    evidence_support: Dict[str, List[Dict[str, Any]]], findings: Dict[str, bool]
) -> Dict[str, List[str]]:
    """Map each finding to evidence IDs."""
    mapping: Dict[str, List[str]] = {}
    for finding_name, active in findings.items():
        if not active:
            mapping[finding_name] = []
            continue
        ids: List[str] = []
        for source in JOINDER_FINDING_FACT_SOURCES.get(finding_name, []):
            ids.extend(item["id"] for item in evidence_support.get(source, []))
        mapping[finding_name] = sorted(set(ids))
    return mapping


def _finding_authorities(
    authority_support: Dict[str, List[Dict[str, str]]], findings: Dict[str, bool]
) -> Dict[str, List[str]]:
    """Map each finding to authority IDs."""
    mapping: Dict[str, List[str]] = {}
    for finding_name, active in findings.items():
        if not active:
            mapping[finding_name] = []
            continue
        ids: List[str] = []
        for source in JOINDER_FINDING_AUTHORITY_SOURCES.get(finding_name, []):
            ids.extend(item["id"] for item in authority_support.get(source, []))
        mapping[finding_name] = sorted(set(ids))
    return mapping


def evaluate_case(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluate the joinder case fixture and return findings + authority support."""
    facts, conflicts = _resolve_facts(case_payload)

    # Compute findings: each finding bucket is true if any of its fact sources is true
    findings: Dict[str, bool] = {
        bucket: any(facts.get(k, False) for k in fact_keys)
        for bucket, fact_keys in JOINDER_FINDING_FACT_SOURCES.items()
    }

    # Route authorities
    authority_support_map = _authority_map(case_payload.get("authorities", []))

    # Index evidence and map to findings
    evidence_support = _evidence_support_map(case_payload.get("evidence", []))
    finding_evidence = _finding_evidence(evidence_support, findings)
    finding_authorities = _finding_authorities(authority_support_map, findings)

    # Compute outcome: joinder is viable if at least 3 of the 6 finding buckets are true
    active_finding_count = sum(1 for v in findings.values() if v)
    joinder_viable = active_finding_count >= 3

    return {
        "caseId": case_payload.get("caseId", "joinder_quantum_001"),
        "branch": case_payload.get("branch", "joinder_eviction_defense"),
        "outcome": {
            "joinder_viable": joinder_viable,
            **findings,
        },
        "findings": findings,
        "authoritySupport": authority_support_map,
        "findingEvidence": finding_evidence,
        "findingAuthorities": finding_authorities,
        "conflictsFacts": conflicts,
        "confidence": 0.85 if joinder_viable else 0.70,
    }


def write_result_file(fixture_path: Path, result: Dict[str, Any]) -> Path:
    """Write result to outputs directory."""
    output_dir = fixture_path.resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{result['caseId']}.result.json"
    tmp_path = output_path.with_name(f".{output_path.name}.tmp")
    tmp_path.write_text(json.dumps(result, indent=2) + "\n")
    tmp_path.replace(output_path)
    return output_path


def main(argv: List[str]) -> int:
    if len(argv) not in {2, 3}:
        print(
            "usage: joinder_evaluate_case.py <fixture.json> [--write]",
            file=sys.stderr,
        )
        return 2

    write_output = len(argv) == 3 and argv[2] == "--write"
    if len(argv) == 3 and not write_output:
        print(
            "usage: joinder_evaluate_case.py <fixture.json> [--write]",
            file=sys.stderr,
        )
        return 2

    path = Path(argv[1])
    if not path.exists():
        print(f"error: fixture not found: {path}", file=sys.stderr)
        return 1

    payload = json.loads(path.read_text())
    result = evaluate_case(payload)
    print(json.dumps(result, indent=2))

    if write_output:
        output_path = write_result_file(path, result)
        print(f"\nWrote result to {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
