#!/usr/bin/env python3
"""Evaluate a live-in-aide accommodation case fixture."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List


DEFAULT_PRIVACY_MODE = "inferred_from_living_room_sleeping"

FINDING_FACT_SOURCES = {
    "sleepInterruption": ["night_access_needed", "aide_sleeps_in_living_room"],
    "workInterference": [
        "night_access_needed",
        "aide_sleeps_in_living_room",
        "works_remotely",
    ],
    "caregivingImpairment": ["night_access_needed", "aide_sleeps_in_living_room"],
    "privacyLoss": ["privacy_loss", "aide_sleeps_in_living_room"],
    "necessary": [
        "night_access_needed",
        "aide_sleeps_in_living_room",
        "works_remotely",
        "privacy_loss",
    ],
    "reasonable": ["medical_verification", "undue_burden", "fundamental_alteration"],
    "dutyToGrant": [
        "disabled_tenant",
        "needs_live_in_aide",
        "requested_separate_bedroom",
        "medical_verification",
    ],
    "notEffective": ["denied_separate_bedroom", "night_access_needed", "aide_sleeps_in_living_room"],
    "constructiveDenial": [
        "approved_aide_in_principle",
        "denied_separate_bedroom",
        "night_access_needed",
        "aide_sleeps_in_living_room",
    ],
    "violation": [
        "disabled_tenant",
        "needs_live_in_aide",
        "requested_separate_bedroom",
        "medical_verification",
        "approved_aide_in_principle",
        "denied_separate_bedroom",
        "night_access_needed",
        "aide_sleeps_in_living_room",
    ],
}

FINDING_EVENT_SOURCES = {
    "sleepInterruption": ["night_access_needed"],
    "workInterference": ["night_access_needed"],
    "caregivingImpairment": ["night_access_needed"],
    "reasonable": ["medical_verification"],
    "dutyToGrant": ["requested_separate_bedroom", "medical_verification"],
    "constructiveDenial": [
        "approved_aide_in_principle",
        "denied_separate_bedroom",
        "night_access_needed",
    ],
    "violation": ["denied_separate_bedroom", "requested_separate_bedroom"],
}

FINDING_AUTHORITY_SOURCES = {
    "necessary": ["necessary"],
    "reasonable": ["reasonable"],
    "dutyToGrant": ["dutyToGrant"],
    "constructiveDenial": ["constructiveDenial"],
    "violation": ["violation", "constructiveDenial", "dutyToGrant"],
}


def _resolve_facts(payload: Dict[str, Any]) -> tuple[Dict[str, bool], List[Dict[str, Any]]]:
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
        "necessary": [],
        "reasonable": [],
        "dutyToGrant": [],
        "constructiveDenial": [],
        "violation": [],
    }
    for authority in authorities:
        label = authority["label"].lower()
        notes = authority.get("notes", "").lower()
        text = f"{label} {notes}"
        if any(term in text for term in ["usable", "equal use", "enjoyment"]):
            buckets["necessary"].append(authority)
        if any(term in text for term in ["reasonable", "accommodation", "live-in aide"]):
            buckets["reasonable"].append(authority)
        if any(term in text for term in ["allow", "must", "live-in aide", "refusal"]):
            buckets["dutyToGrant"].append(authority)
        if any(term in text for term in ["usable", "refusal", "effective"]):
            buckets["constructiveDenial"].append(authority)
        if any(term in text for term in ["violate", "violation", "refusal", "must"]):
            buckets["violation"].append(authority)
    return {key: slim(value) for key, value in buckets.items()}


def _evidence_support_map(evidence: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
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


def _event_support_map(events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, str]]]:
    support: Dict[str, List[Dict[str, str]]] = {}
    event_targets = {
        "request_accommodation": ["requested_separate_bedroom"],
        "submit_medical_verification": ["medical_verification"],
        "approve_aide_in_principle": ["approved_aide_in_principle"],
        "deny_separate_bedroom": ["denied_separate_bedroom"],
        "night_use": ["night_access_needed"],
    }
    for item in events:
        for target in event_targets.get(item.get("event", ""), []):
            support.setdefault(target, []).append(
                {
                    "id": item["id"],
                    "event": item["event"],
                    "time": item["time"],
                }
            )
    return support


def _timeline(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(events, key=lambda item: item.get("time", ""))


def _privacy_loss(facts: Dict[str, bool], privacy_mode: str) -> tuple[bool, str]:
    explicit = bool(facts.get("privacy_loss", False))
    living_room = bool(facts["aide_sleeps_in_living_room"])
    if privacy_mode == "explicit_only":
        return explicit, "explicit privacy_loss only"
    return bool(explicit or living_room), "privacy_loss or living_room_sleeping"


def _finding_evidence(evidence_support: Dict[str, List[Dict[str, Any]]], findings: Dict[str, bool]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for finding_name, active in findings.items():
        if not active:
            mapping[finding_name] = []
            continue
        ids: List[str] = []
        for source in FINDING_FACT_SOURCES.get(finding_name, []):
            ids.extend(item["id"] for item in evidence_support.get(source, []))
        mapping[finding_name] = sorted(set(ids))
    return mapping


def _finding_events(event_support: Dict[str, List[Dict[str, str]]], findings: Dict[str, bool]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for finding_name, active in findings.items():
        if not active:
            mapping[finding_name] = []
            continue
        ids: List[str] = []
        for source in FINDING_EVENT_SOURCES.get(finding_name, []):
            ids.extend(item["id"] for item in event_support.get(source, []))
        mapping[finding_name] = sorted(set(ids))
    return mapping


def _finding_authorities(
    authority_support: Dict[str, List[Dict[str, str]]], findings: Dict[str, bool]
) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for finding_name, active in findings.items():
        if not active:
            mapping[finding_name] = []
            continue
        ids: List[str] = []
        for source in FINDING_AUTHORITY_SOURCES.get(finding_name, []):
            ids.extend(item["id"] for item in authority_support.get(source, []))
        mapping[finding_name] = sorted(set(ids))
    return mapping


def _finding_provenance(
    facts: Dict[str, bool],
    findings: Dict[str, bool],
    proof: List[str],
    authority_support: Dict[str, List[Dict[str, str]]],
    finding_evidence: Dict[str, List[str]],
    finding_events: Dict[str, List[str]],
    finding_authorities: Dict[str, List[str]],
) -> Dict[str, Dict[str, Any]]:
    def normalized(text: str) -> str:
        return text.replace("_", "").lower()

    provenance: Dict[str, Dict[str, Any]] = {}
    for finding_name, active in findings.items():
        fact_sources = []
        for fact_name in FINDING_FACT_SOURCES.get(finding_name, []):
            fact_sources.append({"fact": fact_name, "value": facts.get(fact_name)})

        proof_steps = [
            step for step in proof if normalized(finding_name) in normalized(step)
        ]
        if finding_name == "necessary":
            proof_steps.extend(
                step for step in proof if "functional_harm" in step or "necessary" in step
            )
        provenance[finding_name] = {
            "active": active,
            "facts": fact_sources,
            "evidenceIds": finding_evidence.get(finding_name, []),
            "eventIds": finding_events.get(finding_name, []),
            "authorityIds": finding_authorities.get(finding_name, []),
            "proofSteps": sorted(set(proof_steps)),
        }
    return provenance


def _narrative(case_id: str, findings: Dict[str, bool], privacy_mode: str, missing: List[str], conflicts: List[Dict[str, Any]]) -> str:
    lines = [f"Case {case_id} was evaluated using privacy mode `{privacy_mode}`."]
    if findings["violation"]:
        lines.append("The current rule set concludes that the housing arrangement results in a violation.")
    else:
        lines.append("The current rule set does not conclude a violation on the accepted findings.")
    if findings["constructiveDenial"]:
        lines.append("The strongest theory triggered is constructive denial of accommodation.")
    elif findings["dutyToGrant"]:
        lines.append("The evaluator found a duty to grant, but constructive denial was not established.")
    if findings["sleepInterruption"]:
        lines.append("Sleep interruption was established from living-room sleeping plus night access needs.")
    if findings["privacyLoss"]:
        lines.append("Privacy loss was treated as a relevant harm in the necessity analysis.")
    if missing:
        lines.append("Missing or failed elements: " + ", ".join(sorted(set(missing))) + ".")
    if conflicts:
        lines.append("Accepted findings override some asserted facts, and those conflicts were preserved in the output.")
    return " ".join(lines)


def _branch_label(payload: Dict[str, Any], findings: Dict[str, bool], facts: Dict[str, bool]) -> str:
    if payload.get("policy", {}).get("privacy_mode") == "explicit_only" and facts["approved_aide_in_principle"] and not facts["denied_separate_bedroom"] and not findings["violation"]:
        return "effective_accommodation"
    if findings["constructiveDenial"] and facts["undue_burden"]:
        return "undue_burden_constructive_denial"
    if findings["constructiveDenial"]:
        return "constructive_denial"
    return "evidentiary_gap"


def _explanations(findings: Dict[str, bool], authority_support: Dict[str, List[Dict[str, str]]]) -> Dict[str, str]:
    explanations: Dict[str, str] = {}
    labels = {
        key: ", ".join(item["label"] for item in value)
        for key, value in authority_support.items()
    }
    if findings["necessary"]:
        explanations["necessary"] = (
            "Necessity was triggered because the accepted facts established one or more functional harms. "
            f"Supporting authorities: {labels.get('necessary', 'none')}"
        )
    if findings["reasonable"]:
        explanations["reasonable"] = (
            "Reasonableness was satisfied because medical support and necessity were present and no defenses defeated the request. "
            f"Supporting authorities: {labels.get('reasonable', 'none')}"
        )
    if findings["dutyToGrant"]:
        explanations["dutyToGrant"] = (
            "The evaluator found a duty to grant because disability, live-in aide need, request, and reasonableness were all present. "
            f"Supporting authorities: {labels.get('dutyToGrant', 'none')}"
        )
    if findings["constructiveDenial"]:
        explanations["constructiveDenial"] = (
            "Constructive denial was triggered because approval in principle was followed by denial of an effective functional arrangement. "
            f"Supporting authorities: {labels.get('constructiveDenial', 'none')}"
        )
    if findings["violation"]:
        explanations["violation"] = (
            "Violation was triggered by either denied duty-to-grant logic or constructive denial logic. "
            f"Supporting authorities: {labels.get('violation', 'none')}"
        )
    return explanations


def evaluate_case(payload: Dict[str, Any]) -> Dict[str, Any]:
    facts, fact_conflicts = _resolve_facts(payload)
    authorities = payload.get("authorities", [])
    evidence = payload.get("evidence", [])
    events = payload.get("events", [])
    policy = payload.get("policy", {})
    privacy_mode = policy.get("privacy_mode", DEFAULT_PRIVACY_MODE)

    proof: List[str] = []
    missing: List[str] = []

    sleep_interruption = bool(
        facts["aide_sleeps_in_living_room"] and facts["night_access_needed"]
    )
    if sleep_interruption:
        proof.append(
            "aide_sleeps_in_living_room + night_access_needed -> sleep_interruption"
        )

    work_interference = bool(sleep_interruption and facts.get("works_remotely", False))
    if work_interference:
        proof.append("sleep_interruption + works_remotely -> work_interference")

    caregiving_impairment = bool(sleep_interruption)
    if caregiving_impairment:
        proof.append("sleep_interruption -> caregiving_impairment")

    privacy_loss, privacy_basis = _privacy_loss(facts, privacy_mode)
    if privacy_loss:
        proof.append(f"{privacy_basis} -> privacy_loss")

    necessary = any(
        [sleep_interruption, work_interference, caregiving_impairment, privacy_loss]
    )
    if necessary:
        proof.append(
            "sleep_interruption/work_interference/caregiving_impairment/privacy_loss -> necessary"
        )
    else:
        missing.append("functional_harm")

    reasonable = bool(
        facts["medical_verification"]
        and necessary
        and not facts["undue_burden"]
        and not facts["fundamental_alteration"]
    )
    if reasonable:
        proof.append("medical_verification + necessary + no defenses -> reasonable")
    else:
        if not facts["medical_verification"]:
            missing.append("medical_verification")
        if facts["undue_burden"]:
            proof.append("undue_burden defeats reasonable")
        if facts["fundamental_alteration"]:
            proof.append("fundamental_alteration defeats reasonable")

    duty_to_grant = bool(
        facts["disabled_tenant"]
        and facts["needs_live_in_aide"]
        and facts["requested_separate_bedroom"]
        and reasonable
    )
    if duty_to_grant:
        proof.append(
            "disabled_tenant + needs_live_in_aide + requested_separate_bedroom + reasonable -> duty_to_grant"
        )
    else:
        if not facts["disabled_tenant"]:
            missing.append("disabled_tenant")
        if not facts["needs_live_in_aide"]:
            missing.append("needs_live_in_aide")
        if not facts["requested_separate_bedroom"]:
            missing.append("requested_separate_bedroom")

    not_effective = bool(facts["denied_separate_bedroom"] and sleep_interruption)
    if not_effective:
        proof.append("denied_separate_bedroom + sleep_interruption -> not_effective")

    constructive_denial = bool(
        facts["approved_aide_in_principle"]
        and facts["denied_separate_bedroom"]
        and not_effective
    )
    if constructive_denial:
        proof.append(
            "approved_aide_in_principle + denied_separate_bedroom + not_effective -> constructive_denial"
        )

    violation = bool(
        (duty_to_grant and facts["denied_separate_bedroom"]) or constructive_denial
    )
    if violation:
        proof.append("denied duty_to_grant or constructive_denial -> violation")

    confidence = 0.35
    if violation:
        confidence += 0.2
    if constructive_denial:
        confidence += 0.15
    if facts["medical_verification"]:
        confidence += 0.1
    if authorities:
        confidence += min(0.1, len(authorities) * 0.02)
    if evidence:
        confidence += min(0.05, len(evidence) * 0.01)
    if facts["undue_burden"] or facts["fundamental_alteration"]:
        confidence -= 0.1
    if fact_conflicts:
        confidence -= 0.05
    confidence = max(0.0, min(0.99, confidence))

    findings = {
        "sleepInterruption": sleep_interruption,
        "workInterference": work_interference,
        "caregivingImpairment": caregiving_impairment,
        "privacyLoss": privacy_loss,
        "necessary": necessary,
        "reasonable": reasonable,
        "dutyToGrant": duty_to_grant,
        "notEffective": not_effective,
        "constructiveDenial": constructive_denial,
        "violation": violation,
    }
    authority_support = _authority_map(authorities)
    evidence_support = _evidence_support_map(evidence)
    event_support = _event_support_map(events)

    finding_evidence = _finding_evidence(evidence_support, findings)
    finding_events = _finding_events(event_support, findings)
    finding_authorities = _finding_authorities(authority_support, findings)
    branch = _branch_label(payload, findings, facts)

    return {
        "caseId": payload["caseId"],
        "branch": branch,
        "policy": {
            "privacy_mode": privacy_mode,
        },
        "facts": {
            "asserted": payload["assertedFacts"],
            "accepted": payload.get("acceptedFindings", {}),
            "resolved": facts,
            "conflicts": fact_conflicts,
        },
        "outcome": findings,
        "proofTrace": proof,
        "narrative": _narrative(payload["caseId"], findings, privacy_mode, missing, fact_conflicts),
        "explanations": _explanations(findings, authority_support),
        "missingEvidence": sorted(set(missing)),
        "defeatersConsidered": {
            "undueBurden": facts["undue_burden"],
            "fundamentalAlteration": facts["fundamental_alteration"],
        },
        "authoritySupport": authority_support,
        "evidenceSupport": evidence_support,
        "eventSupport": event_support,
        "findingEvidence": finding_evidence,
        "findingEvents": finding_events,
        "findingAuthorities": finding_authorities,
        "provenance": _finding_provenance(
            facts,
            findings,
            proof,
            authority_support,
            finding_evidence,
            finding_events,
            finding_authorities,
        ),
        "timeline": _timeline(events),
        "confidence": confidence,
    }


def write_result_file(fixture_path: Path, result: Dict[str, Any]) -> Path:
    output_dir = fixture_path.resolve().parent.parent / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{result['caseId']}.result.json"
    tmp_path = output_path.with_name(f".{output_path.name}.tmp")
    tmp_path.write_text(json.dumps(result, indent=2) + "\n")
    tmp_path.replace(output_path)
    return output_path


def main(argv: List[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: evaluate_case.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    write_output = len(argv) == 3 and argv[2] == "--write"
    if len(argv) == 3 and not write_output:
        print("usage: evaluate_case.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text())
    result = evaluate_case(payload)
    print(json.dumps(result, indent=2))
    if write_output:
        output_path = write_result_file(path, result)
        print(f"\nWrote result to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
