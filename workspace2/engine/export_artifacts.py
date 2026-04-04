#!/usr/bin/env python3
"""Export package-style artifacts aligned to the extracted chat."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from engine.authority_trust import build_authority_trust_profile
from engine.authority_fit import infer_fit_kind
from engine.evaluate_case import evaluate_case
from engine.generate_advocacy import generate_advocacy_bundle, generate_advocacy_outputs, write_advocacy_artifacts
from engine.generate_memorandum import generate_memorandum_bundle, write_memorandum_artifacts
from engine.legal_grounding import (
    DEPENDENCY_EDGES,
    DEPENDENCY_NODES,
    build_dependency_citations_jsonld,
    dependency_graph_payload,
)

ROOT = Path(__file__).resolve().parent.parent
SOURCE_VERIFIED_IDS = {
    "giebeler",
    "california_mobile_home",
    "mcgary",
    "hud_joint_statement",
    "cfr_982_316",
}
SOURCE_NORMALIZED_IDS = {
    "giebeler",
    "california_mobile_home",
    "mcgary",
    "hud_joint_statement",
    "cfr_982_316",
}


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)


def load_case(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _source_flags(authority: Dict[str, Any]) -> Dict[str, bool]:
    authority_id = authority["id"]
    return {
        "sourceVerified": authority_id in SOURCE_VERIFIED_IDS,
        "sourceNormalized": authority_id in SOURCE_NORMALIZED_IDS,
    }


def _recommended_first_stop_note(primary_kind: str, branch: str) -> str:
    if primary_kind == "memorandum_pdf":
        return f"Start with the printable memorandum because it is the strongest branch-aligned narrative for {branch} review."
    if primary_kind == "memorandum_markdown":
        return f"Start with the editable memorandum because it is the clearest working draft for {branch} review."
    if primary_kind == "summary":
        return f"Start with the summary because it is the quickest branch-aligned orientation for {branch} review."
    return f"Start with the primary artifact because it is the highest-priority surface for {branch} review."


def _entry_why_open_this(kind: str, branch: str, primary_kind: str) -> str:
    if kind == primary_kind:
        return _recommended_first_stop_note(primary_kind, branch)
    if kind == "summary":
        return f"Open this when you want the quickest branch-aware orientation for {branch} review."
    if kind == "result":
        return "Open this when you want the full evaluator output with resolved facts, explanations, and provenance."
    if kind == "advocacy_bundle":
        return "Open this when you want the structured drafting and citation payload that drives the advocacy outputs."
    if kind == "hearing_script_markdown":
        return "Open this when you want the hearing-oriented draft rather than the fuller memorandum package."
    if kind == "complaint_outline_markdown":
        return "Open this when you want the complaint framing and issue outline instead of prose briefing."
    if kind == "demand_letter_markdown":
        return "Open this when you want the demand-letter posture and requested remedy framing."
    if kind == "negotiation_summary_markdown":
        return "Open this when you want the shortest negotiation-oriented leverage summary."
    if kind == "memorandum_json":
        return "Open this when you want the structured memorandum bundle for downstream tooling instead of the human-readable draft."
    if kind == "memorandum_markdown":
        return "Open this when you want the editable human-readable memorandum draft."
    if kind == "memorandum_pdf":
        return "Open this when you want the printable memorandum with paragraph-level support lines."
    if kind == "dependency_graph":
        return "Open this when you want the reasoning graph behind the active branch analysis."
    if kind == "dependency_citations":
        return "Open this when you want the JSON-LD grounding that links dependency targets to authority excerpts."
    if kind == "authority_review":
        return "Open this when you want the authority audit view with support status, excerpts, and source metadata."
    if kind == "authority_research_note":
        return "Open this when you want the source-verification and proposition-mapping research note."
    if kind == "authority_summary":
        return "Open this when you want the compact authority count view instead of the fuller authority audit."
    if kind == "decision_tree":
        return "Open this when you want the compact decision-tree representation of the accommodation analysis."
    return f"Open this when you want the {kind} artifact for {branch} review."


def _manifest_artifact_guidance(brief_index: Dict[str, Any], branch: str) -> List[Dict[str, str]]:
    by_path = {entry["path"]: entry["whyOpenThis"] for entry in brief_index["entries"]}
    guidance = {
        "README.md": "Open this when you want the package landing page with branch, trust, source, fit, and first-stop guidance in one place.",
        "legal_reasoning.pl": f"Open this when you want the rule-based legal formalization for {branch} review.",
        "event_calculus.pl": f"Open this when you want the event-calculus export for {branch} review.",
        "context.json": "Open this when you want the JSON-LD context aliases and type mappings used by the package.",
        "case_instance.jsonld": "Open this when you want the JSON-LD case instance representation instead of the prose-facing drafts.",
        "hearing_script.txt": by_path.get("hearing_script.md", "Open this when you want the hearing-oriented draft rather than the fuller memorandum package."),
        "hearing_script.md": by_path.get("hearing_script.md", "Open this when you want the hearing-oriented draft rather than the fuller memorandum package."),
        "complaint_outline.txt": by_path.get("complaint_outline.md", "Open this when you want the complaint framing and issue outline instead of prose briefing."),
        "complaint_outline.md": by_path.get("complaint_outline.md", "Open this when you want the complaint framing and issue outline instead of prose briefing."),
        "demand_letter.txt": by_path.get("demand_letter.md", "Open this when you want the demand-letter posture and requested remedy framing."),
        "demand_letter.md": by_path.get("demand_letter.md", "Open this when you want the demand-letter posture and requested remedy framing."),
        "negotiation_summary.txt": by_path.get("negotiation_summary.md", "Open this when you want the shortest negotiation-oriented leverage summary."),
        "negotiation_summary.md": by_path.get("negotiation_summary.md", "Open this when you want the shortest negotiation-oriented leverage summary."),
        "advocacy_bundle.json": by_path.get("advocacy_bundle.json", "Open this when you want the structured drafting and citation payload that drives the advocacy outputs."),
        "memorandum.json": by_path.get("memorandum.json", "Open this when you want the structured memorandum bundle for downstream tooling instead of the human-readable draft."),
        "memorandum.md": by_path.get("memorandum.md", "Open this when you want the editable human-readable memorandum draft."),
        "memorandum_of_law.pdf": by_path.get("memorandum_of_law.pdf", "Open this when you want the printable memorandum with paragraph-level support lines."),
        "dependency_graph.json": by_path.get("dependency_graph.json", "Open this when you want the reasoning graph behind the active branch analysis."),
        "dependency_citations.jsonld": by_path.get("dependency_citations.jsonld", "Open this when you want the JSON-LD grounding that links dependency targets to authority excerpts."),
        "authority_review.json": by_path.get("authority_review.json", "Open this when you want the authority audit view with support status, excerpts, and source metadata."),
        "authority_review.md": by_path.get("authority_review.json", "Open this when you want the authority audit view with support status, excerpts, and source metadata."),
        "authority_research_note.json": by_path.get("authority_research_note.json", "Open this when you want the source-verification and proposition-mapping research note."),
        "authority_research_note.md": by_path.get("authority_research_note.json", "Open this when you want the source-verification and proposition-mapping research note."),
        "authority_summary.json": by_path.get("authority_summary.json", "Open this when you want the compact authority count view instead of the fuller authority audit."),
        "decision_tree.json": by_path.get("decision_tree.json", "Open this when you want the compact decision-tree representation of the accommodation analysis."),
        "summary.json": by_path.get("summary.json", f"Open this when you want the quickest branch-aware orientation for {branch} review."),
        "brief_index.json": "Open this when you want the package-local discovery index with entry priorities, warnings, and rationale.",
        "tests.json": "Open this when you want the regression fixture inventory that accompanies the package exports.",
        "manifest.json": "Open this when you want the package contract and artifact inventory for validation and downstream tooling.",
    }
    return [{"path": path, "whyOpenThis": why} for path, why in guidance.items()]


def build_prolog(case_payload: Dict[str, Any]) -> str:
    facts = case_payload.get("acceptedFindings") or case_payload["assertedFacts"]
    lines = [
        "% legal_reasoning.pl",
        "% Prototype rule set for live-in aide reasonable accommodation analysis",
        "",
        "% ---------- Facts ----------",
        "tenant(mother).",
    ]
    if facts["disabled_tenant"]:
        lines.append("disabled(mother).")
    if facts["needs_live_in_aide"]:
        lines.append("needs_live_in_aide(mother).")
    lines.extend(
        [
            "",
            "person(aide).",
            "live_in_aide(aide).",
            "live_in_aide_for(aide, mother).",
            "",
            "housing_authority(ha1).",
            "",
            "room(living1).",
            "living_room(living1).",
            "shared_space(living1).",
            "",
            "room(bed1).",
            "bedroom(bed1).",
            "",
        ]
    )
    if facts["aide_sleeps_in_living_room"]:
        lines.append("sleeps_in(aide, living1).")
    if facts["night_access_needed"]:
        lines.append("night_access_needed(mother, living1).")
    lines.append("")
    if facts["requested_separate_bedroom"]:
        lines.append("requested(mother, separate_bedroom_for(aide)).")
    if facts["medical_verification"]:
        lines.append("medical_verification(mother, separate_bedroom_for(aide)).")
    if facts["approved_aide_in_principle"]:
        lines.append("approved_in_principle(ha1, live_in_aide_status(aide, mother)).")
    if facts["denied_separate_bedroom"]:
        lines.append("denied(ha1, separate_bedroom_for(aide)).")
    if facts.get("works_remotely"):
        lines.append("works_remotely(aide).")
    lines.extend([
        "",
        "% Optional harms",
    ])
    if facts.get("dog_isolation_problem"):
        lines.append("dog_isolation_impossible(household1).")
    if facts.get("guest_management_problem"):
        lines.append("guest_management_problem(household1).")
    lines.extend([
        "",
        "% ---------- Derived factual harms ----------",
        "sleep_interruption(A) :-",
        "    sleeps_in(A, R),",
        "    living_room(R),",
        "    shared_space(R),",
        "    live_in_aide_for(A, T),",
        "    night_access_needed(T, R).",
        "",
        "work_interference(A) :-",
        "    works_remotely(A),",
        "    sleep_interruption(A).",
        "",
        "caregiving_impairment(A) :-",
        "    sleep_interruption(A).",
        "",
        "privacy_loss(A) :-",
        "    sleeps_in(A, R),",
        "    living_room(R),",
        "    shared_space(R).",
        "",
        "% ---------- Legal elements ----------",
        "medically_supported(separate_bedroom_for(A)) :-",
        "    live_in_aide_for(A, T),",
        "    medical_verification(T, separate_bedroom_for(A)).",
        "",
        "necessary(separate_bedroom_for(A)) :-",
        "    sleep_interruption(A).",
        "",
        "necessary(separate_bedroom_for(A)) :-",
        "    work_interference(A).",
        "",
        "necessary(separate_bedroom_for(A)) :-",
        "    caregiving_impairment(A).",
        "",
        "necessary(separate_bedroom_for(A)) :-",
        "    privacy_loss(A).",
        "",
        "reasonable(separate_bedroom_for(A), HA) :-",
        "    medically_supported(separate_bedroom_for(A)),",
        "    necessary(separate_bedroom_for(A)),",
        "    not undue_burden(HA, separate_bedroom_for(A)),",
        "    not fundamental_alteration(HA, separate_bedroom_for(A)).",
        "",
        "duty_to_grant(HA, separate_bedroom_for(A)) :-",
        "    requested(T, separate_bedroom_for(A)),",
        "    live_in_aide_for(A, T),",
        "    disabled(T),",
        "    needs_live_in_aide(T),",
        "    reasonable(separate_bedroom_for(A), HA).",
        "",
        "effective(separate_bedroom_for(A)) :-",
        "    not denied(ha1, separate_bedroom_for(A)),",
        "    not sleep_interruption(A).",
        "",
        "not_effective(separate_bedroom_for(A)) :-",
        "    denied(ha1, separate_bedroom_for(A)),",
        "    sleep_interruption(A).",
        "",
        "constructive_denial(HA, separate_bedroom_for(A)) :-",
        "    approved_in_principle(HA, live_in_aide_status(A, T)),",
        "    denied(HA, separate_bedroom_for(A)),",
        "    live_in_aide_for(A, T),",
        "    not_effective(separate_bedroom_for(A)).",
        "",
        "violates_duty_to_accommodate(HA, separate_bedroom_for(A)) :-",
        "    duty_to_grant(HA, separate_bedroom_for(A)),",
        "    denied(HA, separate_bedroom_for(A)).",
        "",
        "violates_duty_to_accommodate(HA, separate_bedroom_for(A)) :-",
        "    constructive_denial(HA, separate_bedroom_for(A)).",
        "",
        "% ---------- Canonical theorem ----------",
        "claim_valid(HA, Aide, Tenant) :-",
        "    housing_authority(HA),",
        "    live_in_aide_for(Aide, Tenant),",
        "    disabled(Tenant),",
        "    needs_live_in_aide(Tenant),",
        "    requested(Tenant, separate_bedroom_for(Aide)),",
        "    medical_verification(Tenant, separate_bedroom_for(Aide)),",
        "    sleep_interruption(Aide),",
        "    not undue_burden(HA, separate_bedroom_for(Aide)),",
        "    not fundamental_alteration(HA, separate_bedroom_for(Aide)).",
        "",
        "result(HA, Aide, violation_and_constructive_denial) :-",
        "    claim_valid(HA, Aide, _),",
        "    approved_in_principle(HA, live_in_aide_status(Aide, _)),",
        "    denied(HA, separate_bedroom_for(Aide)).",
    ])
    return "\n".join(lines) + "\n"


def build_event_calculus(case_payload: Dict[str, Any]) -> str:
    events = case_payload.get("events", [])
    lines = [
        "% event_calculus.pl",
        "% Event calculus style export for the live-in aide accommodation dispute",
        "",
        "% Happens(Event, Time)",
        "% HoldsAt(Fluent, Time)",
        "% Initiates(Event, Fluent, Time)",
        "% Terminates(Event, Fluent, Time)",
        "",
    ]
    event_map = {
        "request_accommodation": lambda e: f"happens(request_accommodation(mother, separate_bedroom_for(aide)), {e['time']}).",
        "submit_medical_verification": lambda e: f"happens(submit_medical_verification(mother, separate_bedroom_for(aide)), {e['time']}).",
        "approve_aide_in_principle": lambda e: f"happens(approve_aide_in_principle(ha1, aide, mother), {e['time']}).",
        "deny_separate_bedroom": lambda e: f"happens(deny_separate_bedroom(ha1, aide), {e['time']}).",
        "night_use": lambda e: f"happens(night_use(mother, living1), {e['time']}).",
    }
    for event in events:
        renderer = event_map.get(event["event"])
        if renderer:
            lines.append(renderer(event))
    lines.extend([
        "",
        "initiates(request_accommodation(T, A), requested(T, A), Tm).",
        "initiates(submit_medical_verification(T, A), medically_supported(A), Tm).",
        "initiates(approve_aide_in_principle(HA, Aide, T), approved_in_principle(HA, live_in_aide_status(Aide, T)), Tm).",
        "initiates(deny_separate_bedroom(HA, Aide), denied(HA, separate_bedroom_for(Aide)), Tm).",
        "initiates(night_use(T, living1), shared_night_conflict(living1), Tm).",
        "",
        "holds_at(sleeps_in(aide, living1), t5).",
        "holds_at(shared_night_conflict(living1), t5).",
        "",
        "holds_at(sleep_interruption(aide), Tm) :-",
        "    holds_at(sleeps_in(aide, living1), Tm),",
        "    holds_at(shared_night_conflict(living1), Tm).",
        "",
        "holds_at(not_effective(separate_bedroom_for(aide)), Tm) :-",
        "    holds_at(sleep_interruption(aide), Tm),",
        "    holds_at(denied(ha1, separate_bedroom_for(aide)), Tm).",
        "",
        "holds_at(constructive_denial(separate_bedroom_for(aide)), Tm) :-",
        "    holds_at(approved_in_principle(ha1, live_in_aide_status(aide, mother)), Tm),",
        "    holds_at(not_effective(separate_bedroom_for(aide)), Tm).",
    ])
    return "\n".join(lines) + "\n"


def build_context() -> Dict[str, Any]:
    return {
        "@context": {
            "id": "@id",
            "type": "@type",
            "Person": "https://example.org/legal/Person",
            "Tenant": "https://example.org/legal/Tenant",
            "LiveInAide": "https://example.org/legal/LiveInAide",
            "HousingAuthority": "https://example.org/legal/HousingAuthority",
            "DwellingUnit": "https://example.org/legal/DwellingUnit",
            "Room": "https://example.org/legal/Room",
            "Bedroom": "https://example.org/legal/Bedroom",
            "LivingRoom": "https://example.org/legal/LivingRoom",
            "AccommodationRequest": "https://example.org/legal/AccommodationRequest",
            "MedicalVerification": "https://example.org/legal/MedicalVerification",
            "Evidence": "https://example.org/legal/Evidence",
            "Decision": "https://example.org/legal/Decision",
            "Event": "https://example.org/legal/Event",
            "hasDisability": "https://example.org/legal/hasDisability",
            "needsLiveInAide": "https://example.org/legal/needsLiveInAide",
            "liveInAideFor": {"@id": "https://example.org/legal/liveInAideFor", "@type": "@id"},
            "occupies": {"@id": "https://example.org/legal/occupies", "@type": "@id"},
            "requestedBy": {"@id": "https://example.org/legal/requestedBy", "@type": "@id"},
            "forAccommodation": {"@id": "https://example.org/legal/forAccommodation", "@type": "@id"},
            "supportedBy": {"@id": "https://example.org/legal/supportedBy", "@type": "@id"},
            "deniedBy": {"@id": "https://example.org/legal/deniedBy", "@type": "@id"},
            "approvedInPrincipleBy": {"@id": "https://example.org/legal/approvedInPrincipleBy", "@type": "@id"},
            "sleepsIn": {"@id": "https://example.org/legal/sleepsIn", "@type": "@id"},
            "sharedSpace": "https://example.org/legal/sharedSpace",
            "nightAccessNeeded": {"@id": "https://example.org/legal/nightAccessNeeded", "@type": "@id"},
            "worksRemotely": "https://example.org/legal/worksRemotely",
            "workInterference": "https://example.org/legal/workInterference",
            "sleepInterruption": "https://example.org/legal/sleepInterruption",
            "caregivingImpairment": "https://example.org/legal/caregivingImpairment",
            "privacyLoss": "https://example.org/legal/privacyLoss",
            "necessaryForEqualUseEnjoyment": "https://example.org/legal/necessaryForEqualUseEnjoyment",
            "reasonable": "https://example.org/legal/reasonable",
            "effective": "https://example.org/legal/effective",
            "constructiveDenial": "https://example.org/legal/constructiveDenial",
            "undueBurden": "https://example.org/legal/undueBurden",
            "fundamentalAlteration": "https://example.org/legal/fundamentalAlteration",
            "triggersDutyToGrant": "https://example.org/legal/triggersDutyToGrant",
            "violatesDutyToAccommodate": "https://example.org/legal/violatesDutyToAccommodate",
            "time": "https://example.org/legal/time",
            "eventType": "https://example.org/legal/eventType"
        }
    }


def build_case_instance(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    facts = case_payload.get("acceptedFindings") or case_payload["assertedFacts"]
    evidence = case_payload.get("evidence", [])
    events = case_payload.get("events", [])
    graph: List[Dict[str, Any]] = [
        {
            "id": "person:mother",
            "type": ["Person", "Tenant"],
            "hasDisability": facts["disabled_tenant"],
            "needsLiveInAide": facts["needs_live_in_aide"],
            "occupies": "unit:u1",
        },
        {
            "id": "person:aide",
            "type": ["Person", "LiveInAide"],
            "liveInAideFor": "person:mother",
            "worksRemotely": facts.get("works_remotely", False),
            "sleepsIn": "room:living1" if facts["aide_sleeps_in_living_room"] else "room:bed1",
            "workInterference": facts.get("works_remotely", False) and facts["night_access_needed"] and facts["aide_sleeps_in_living_room"],
            "sleepInterruption": facts["night_access_needed"] and facts["aide_sleeps_in_living_room"],
            "caregivingImpairment": facts["night_access_needed"] and facts["aide_sleeps_in_living_room"],
            "privacyLoss": facts.get("privacy_loss", False) or facts["aide_sleeps_in_living_room"],
        },
        {"id": "org:ha1", "type": "HousingAuthority"},
        {"id": "unit:u1", "type": "DwellingUnit"},
        {"id": "room:bed1", "type": ["Room", "Bedroom"]},
        {"id": "room:living1", "type": ["Room", "LivingRoom"], "sharedSpace": True},
        {
            "id": "req:sep-bedroom-aide",
            "type": "AccommodationRequest",
            "requestedBy": "person:mother",
            "forAccommodation": "acc:separate-bedroom-for-aide",
            "supportedBy": "med:mv1",
            "deniedBy": "org:ha1" if facts["denied_separate_bedroom"] else None,
            "approvedInPrincipleBy": "org:ha1" if facts["approved_aide_in_principle"] else None,
        },
        {
            "id": "med:mv1",
            "type": "MedicalVerification",
            "sourceText": "Physician verified need for live-in aide and separate functional arrangement.",
            "confidence": 0.9,
        },
    ]
    for item in evidence:
        graph.append(
            {
                "id": item["id"],
                "type": ["Evidence"],
                "supports": item.get("supports", []),
                "status": item["status"],
                "sourceText": item.get("sourceText"),
                "assertedBy": item.get("assertedBy"),
                "confidence": item.get("confidence"),
            }
        )
    for item in events:
        graph.append(
            {
                "id": item["id"],
                "type": ["Event"],
                "eventType": item["event"],
                "time": item["time"],
                "actors": item.get("actors", []),
                "details": item.get("details", {}),
            }
        )
    return {"@context": "context.json", "@graph": graph}


def build_decision_tree(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    return {
        "decisionTree": {
            "id": "dt_reasonable_accommodation_live_in_aide",
            "root": "q1",
            "branch": result["branch"],
            "nodes": {
                "q1": {"question": "Is the tenant disabled?", "yes": "q2", "no": "deny_no_disability"},
                "q2": {"question": "Is a live-in aide needed?", "yes": "q3", "no": "deny_no_aide_need"},
                "q3": {"question": "Was a separate bedroom requested?", "yes": "q4", "no": "insufficient_no_request"},
                "q4": {"question": "Is the request medically or functionally supported?", "yes": "q5", "no": "insufficient_support"},
                "q5": {"question": "Does denial create sleep, work, privacy, or caregiving impairment?", "yes": "q6", "no": "deny_no_necessity"},
                "q6": {"question": "Did the provider prove undue burden or fundamental alteration?", "yes": "balancing_required", "no": "q7"},
                "q7": {"question": "Was the accommodation denied or only nominally approved?", "yes": "violation", "no": "no_violation"},
            },
            "outcomes": {
                "deny_no_disability": "Claim fails at disability element",
                "deny_no_aide_need": "Claim fails at necessity of aide",
                "insufficient_no_request": "Need accommodation request",
                "insufficient_support": "Need medical or functional support",
                "deny_no_necessity": "No functional necessity shown",
                "balancing_required": "Provider defense requires further analysis",
                "violation": "Duty to accommodate violated or constructively denied",
                "no_violation": "No denial shown",
            },
            "activeOutcome": "violation" if result["outcome"]["violation"] else "no_violation",
        }
    }


def build_dependency_graph(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    payload = dependency_graph_payload(case_payload)
    return {
        "branch": payload["branch"],
        "activeOutcome": payload["activeOutcome"],
        "nodes": DEPENDENCY_NODES,
        "edges": DEPENDENCY_EDGES,
    }


def build_tests() -> List[Dict[str, Any]]:
    return [
        {
            "testId": "positive_constructive_denial",
            "branch": "constructive_denial",
            "policy": {"privacy_mode": "inferred_from_living_room_sleeping"},
            "facts": {
                "disabled_tenant": True,
                "needs_live_in_aide": True,
                "medical_verification": True,
                "requested_separate_bedroom": True,
                "approved_aide_in_principle": True,
                "denied_separate_bedroom": True,
                "aide_sleeps_in_living_room": True,
                "night_access_needed": True,
                "undue_burden": False,
                "fundamental_alteration": False,
            },
            "expected": {
                "sleep_interruption": True,
                "necessary": True,
                "reasonable": True,
                "duty_to_grant": True,
                "not_effective": True,
                "constructive_denial": True,
                "violation": True,
            },
        },
        {
            "testId": "defeated_by_undue_burden",
            "branch": "undue_burden_constructive_denial",
            "policy": {"privacy_mode": "inferred_from_living_room_sleeping"},
            "facts": {
                "disabled_tenant": True,
                "needs_live_in_aide": True,
                "medical_verification": True,
                "requested_separate_bedroom": True,
                "approved_aide_in_principle": True,
                "denied_separate_bedroom": True,
                "aide_sleeps_in_living_room": True,
                "night_access_needed": True,
                "undue_burden": True,
                "fundamental_alteration": False,
            },
            "expected": {
                "sleep_interruption": True,
                "necessary": True,
                "reasonable": False,
                "duty_to_grant": False,
                "constructive_denial": True,
                "violation": True,
            },
        },
        {
            "testId": "nominal_approval_no_harm_shown",
            "branch": "evidentiary_gap",
            "policy": {"privacy_mode": "explicit_only"},
            "facts": {
                "disabled_tenant": True,
                "needs_live_in_aide": True,
                "medical_verification": True,
                "requested_separate_bedroom": True,
                "approved_aide_in_principle": True,
                "denied_separate_bedroom": True,
                "aide_sleeps_in_living_room": True,
                "night_access_needed": False,
                "privacy_loss": False,
                "undue_burden": False,
                "fundamental_alteration": False,
            },
            "expected": {
                "sleep_interruption": False,
                "necessary": False,
                "reasonable": False,
                "duty_to_grant": False,
                "constructive_denial": False,
                "violation": False,
            },
            "notes": "This fixture uses explicit_only privacy mode to preserve the original chat expectation.",
        },
        {
            "testId": "alternative_private_sleeping_space",
            "branch": "evidentiary_gap",
            "policy": {"privacy_mode": "inferred_from_living_room_sleeping"},
            "facts": {
                "disabled_tenant": True,
                "needs_live_in_aide": True,
                "medical_verification": True,
                "requested_separate_bedroom": True,
                "approved_aide_in_principle": True,
                "denied_separate_bedroom": True,
                "aide_sleeps_in_living_room": False,
                "night_access_needed": False,
                "undue_burden": False,
                "fundamental_alteration": False,
            },
            "expected": {
                "sleep_interruption": False,
                "necessary": False,
                "constructive_denial": False,
            },
        },
    ]


def build_summary(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    return {
        "caseId": result["caseId"],
        "branch": result["branch"],
        "confidence": result["confidence"],
        "activeOutcome": "violation" if result["outcome"]["violation"] else "no_violation",
        "topFindings": {
            "necessary": result["outcome"]["necessary"],
            "reasonable": result["outcome"]["reasonable"],
            "dutyToGrant": result["outcome"]["dutyToGrant"],
            "constructiveDenial": result["outcome"]["constructiveDenial"],
            "violation": result["outcome"]["violation"],
        },
        "defeatersConsidered": result["defeatersConsidered"],
        "missingEvidence": result["missingEvidence"],
    }


def build_authority_review(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    bucket_map: Dict[str, List[str]] = {}
    for bucket, refs in result.get("authoritySupport", {}).items():
        for ref in refs:
            bucket_map.setdefault(ref["id"], []).append(bucket)
    authorities = []
    for authority in case_payload.get("authorities", []):
        excerpt_kind = authority.get("excerptKind", "paraphrase")
        excerpt_text = authority.get("excerptText", authority.get("notes", ""))
        if authority.get("sourceUrl") and excerpt_kind == "verified_quote":
            support_status = "verified_quote"
        elif excerpt_text:
            support_status = "paraphrase"
        else:
            support_status = "missing"
        authorities.append(
            {
                "id": authority["id"],
                "label": authority["label"],
                "kind": authority["kind"],
                "citation": authority.get("citation"),
                "court": authority.get("court"),
                "year": authority.get("year"),
                "pincite": authority.get("pincite"),
                "sourceUrl": authority.get("sourceUrl"),
                "excerptKind": excerpt_kind,
                "excerptText": excerpt_text,
                "proposition": authority.get("proposition", authority.get("notes", "")),
                "fitKind": infer_fit_kind(authority),
                **_source_flags(authority),
                "supportStatus": support_status,
                "buckets": sorted(bucket_map.get(authority["id"], [])),
            }
        )
    return {
        "caseId": result["caseId"],
        "branch": result["branch"],
        "authorities": authorities,
    }


def build_authority_research_note(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    review = build_authority_review(case_payload)
    entries = []
    for authority in review["authorities"]:
        entries.append(
            {
                "id": authority["id"],
                "label": authority["label"],
                "citation": authority.get("citation"),
                "court": authority.get("court"),
                "year": authority.get("year"),
                "pincite": authority.get("pincite"),
                "sourceUrl": authority.get("sourceUrl"),
                "sourceReference": authority.get("pincite") or authority.get("year") or "unpaged",
                "excerptKind": authority["excerptKind"],
                "excerptText": authority["excerptText"],
                "proposition": authority["proposition"],
                "fitKind": authority["fitKind"],
                "sourceVerified": authority["sourceVerified"],
                "sourceNormalized": authority["sourceNormalized"],
                "supportStatus": authority["supportStatus"],
                "buckets": authority.get("buckets", []),
            }
        )
    return {
        "caseId": review["caseId"],
        "branch": review["branch"],
        "entryCount": len(entries),
        "entries": entries,
    }


def build_authority_summary(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    review = build_authority_review(case_payload)
    status_counts: Dict[str, int] = {}
    bucket_counts: Dict[str, int] = {}
    for authority in review["authorities"]:
        status = authority["supportStatus"]
        status_counts[status] = status_counts.get(status, 0) + 1
        for bucket in authority.get("buckets", []):
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    return {
        "caseId": review["caseId"],
        "branch": review["branch"],
        "verifiedOnly": False,
        "supportStatus": None,
        "fitKind": None,
        "authorityCount": len(review["authorities"]),
        "statusCounts": dict(sorted(status_counts.items())),
        "bucketCounts": dict(sorted(bucket_counts.items())),
    }


def _build_fit_summary(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    review = build_authority_review(case_payload)
    direct_count = sum(1 for authority in review["authorities"] if authority["fitKind"] == "direct")
    analogical_count = sum(1 for authority in review["authorities"] if authority["fitKind"] == "analogical")
    record_support_count = sum(1 for authority in review["authorities"] if authority["fitKind"] == "record_support")
    authority_count = len(review["authorities"])
    if direct_count == authority_count and authority_count > 0:
        fit_status = "All authority mappings are marked as direct."
    elif analogical_count > 0:
        fit_status = "This package includes analogical authority mappings."
    elif record_support_count > 0:
        fit_status = "This package includes record-support authority mappings."
    else:
        fit_status = "No fit-kind mappings were recorded."
    return {
        "authorityCount": authority_count,
        "directCount": direct_count,
        "analogicalCount": analogical_count,
        "recordSupportCount": record_support_count,
        "fitStatus": fit_status,
    }


def _build_fit_finding(fit_summary: Dict[str, Any]) -> Dict[str, str]:
    if fit_summary["recordSupportCount"] > 0:
        return {
            "label": "record_support_heavy",
            "note": "This package relies in part on record-support mappings, so direct controlling authority should be distinguished from factual or background support.",
        }
    if fit_summary["analogicalCount"] > 0:
        return {
            "label": "analogical_support",
            "note": "This package includes analogical mappings, so the legal fit should be described as mixed direct and analogical support.",
        }
    if fit_summary["directCount"] == fit_summary["authorityCount"] and fit_summary["authorityCount"] > 0:
        return {
            "label": "direct_only",
            "note": "This package currently relies on direct-fit authority mappings only.",
        }
    return {
        "label": "unclassified",
        "note": "This package does not yet carry a stable fit finding classification.",
    }


def _build_fit_finding_summary(fit_summary: Dict[str, Any]) -> Dict[str, Any]:
    fit_finding = _build_fit_finding(fit_summary)
    return {
        "hasFitFinding": fit_finding["label"] != "unclassified",
        "fitFinding": fit_finding["label"],
        "fitFindingNote": fit_finding["note"],
    }


def _build_source_summary(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    source_flags = [_source_flags(authority) for authority in case_payload.get("authorities", [])]
    authority_count = len(source_flags)
    source_verified_count = sum(1 for flags in source_flags if flags["sourceVerified"])
    source_normalized_count = sum(1 for flags in source_flags if flags["sourceNormalized"])
    return {
        "authorityCount": authority_count,
        "sourceVerifiedCount": source_verified_count,
        "sourceNormalizedCount": source_normalized_count,
        "fullySourceVerified": authority_count > 0 and source_verified_count == authority_count,
        "fullySourceNormalized": authority_count > 0 and source_normalized_count == authority_count,
        "sourceStatus": (
            "All authority entries are sourceVerified and sourceNormalized."
            if authority_count > 0
            and source_verified_count == authority_count
            and source_normalized_count == authority_count
            else "Some authority entries still need source verification or normalization cleanup."
        ),
    }


def build_authority_review_markdown(case_payload: Dict[str, Any]) -> str:
    review = build_authority_review(case_payload)
    authority_count = len(review["authorities"])
    source_verified_count = sum(1 for authority in review["authorities"] if authority["sourceVerified"])
    source_normalized_count = sum(1 for authority in review["authorities"] if authority["sourceNormalized"])
    fit_summary = _build_fit_summary(case_payload)
    fit_finding = _build_fit_finding(fit_summary)
    source_status = (
        "All listed authorities are sourceVerified and sourceNormalized."
        if authority_count and source_verified_count == authority_count and source_normalized_count == authority_count
        else "Some listed authorities still need source verification or normalization cleanup."
    )
    lines = [
        f"# Authority Review: {review['caseId']}",
        "",
        f"Branch: `{review['branch']}`",
        f"Authority Count: `{authority_count}`",
        f"Source Verified Count: `{source_verified_count}`",
        f"Source Normalized Count: `{source_normalized_count}`",
        f"Source Status: {source_status}",
        f"Direct Fit Count: `{fit_summary['directCount']}`",
        f"Analogical Fit Count: `{fit_summary['analogicalCount']}`",
        f"Record-Support Fit Count: `{fit_summary['recordSupportCount']}`",
        f"Fit Status: {fit_summary['fitStatus']}",
        f"Fit Finding: `{fit_finding['label']}`",
        f"Fit Finding Note: {fit_finding['note']}",
        "",
    ]
    for authority in review["authorities"]:
        badges = []
        if authority["sourceVerified"]:
            badges.append("sourceVerified")
        if authority["sourceNormalized"]:
            badges.append("sourceNormalized")
        lines.extend(
            [
                f"## {authority['label']}",
                "",
                f"Badges: {' '.join(f'`{badge}`' for badge in badges) or '`none`'}",
                "",
                f"- ID: `{authority['id']}`",
                f"- Kind: `{authority['kind']}`",
                f"- Citation: {authority.get('citation') or 'none'}",
                f"- Court: {authority.get('court') or 'none'}",
                f"- Year: {authority.get('year') or 'none'}",
                f"- Pincite: {authority.get('pincite') or 'none'}",
                f"- Support Status: `{authority['supportStatus']}`",
                f"- Fit Kind: `{authority['fitKind']}`",
                f"- Source Verified: `{authority['sourceVerified']}`",
                f"- Source Normalized: `{authority['sourceNormalized']}`",
                f"- Buckets: {', '.join(authority['buckets']) or 'none'}",
                f"- Source URL: {authority.get('sourceUrl') or 'none'}",
                "",
                f"Excerpt Kind: `{authority['excerptKind']}`",
                "",
                authority["excerptText"] or "No excerpt text recorded.",
                "",
                f"Proposition: {authority['proposition']}",
                "",
            ]
        )
    return "\n".join(lines)


def build_authority_research_note_markdown(case_payload: Dict[str, Any]) -> str:
    note = build_authority_research_note(case_payload)
    source_verified_count = sum(1 for authority in note["entries"] if authority["sourceVerified"])
    source_normalized_count = sum(1 for authority in note["entries"] if authority["sourceNormalized"])
    fit_summary = _build_fit_summary(case_payload)
    fit_finding = _build_fit_finding(fit_summary)
    source_status = (
        "All listed authorities are sourceVerified and sourceNormalized."
        if note["entryCount"] and source_verified_count == note["entryCount"] and source_normalized_count == note["entryCount"]
        else "Some listed authorities still need source verification or normalization cleanup."
    )
    lines = [
        f"# Authority Research Note: {note['caseId']}",
        "",
        f"Branch: `{note['branch']}`",
        f"Authority Entries: `{note['entryCount']}`",
        f"Source Verified Count: `{source_verified_count}`",
        f"Source Normalized Count: `{source_normalized_count}`",
        f"Source Status: {source_status}",
        f"Direct Fit Count: `{fit_summary['directCount']}`",
        f"Analogical Fit Count: `{fit_summary['analogicalCount']}`",
        f"Record-Support Fit Count: `{fit_summary['recordSupportCount']}`",
        f"Fit Status: {fit_summary['fitStatus']}",
        f"Fit Finding: `{fit_finding['label']}`",
        f"Fit Finding Note: {fit_finding['note']}",
        "",
    ]
    for authority in note["entries"]:
        badges = []
        if authority["sourceVerified"]:
            badges.append("sourceVerified")
        if authority["sourceNormalized"]:
            badges.append("sourceNormalized")
        lines.extend(
            [
                f"## {authority['label']}",
                "",
                f"Badges: {' '.join(f'`{badge}`' for badge in badges) or '`none`'}",
                "",
                f"- ID: `{authority['id']}`",
                f"- Citation: {authority.get('citation') or 'none'}",
                f"- Court: {authority.get('court') or 'none'}",
                f"- Year: {authority.get('year') or 'none'}",
                f"- Pincite: {authority.get('pincite') or 'none'}",
                f"- Source URL: {authority.get('sourceUrl') or 'none'}",
                f"- Source Reference: `{authority['sourceReference']}`",
                f"- Excerpt Kind: `{authority['excerptKind']}`",
                f"- Fit Kind: `{authority['fitKind']}`",
                f"- Support Status: `{authority['supportStatus']}`",
                f"- Source Verified: `{authority['sourceVerified']}`",
                f"- Source Normalized: `{authority['sourceNormalized']}`",
                f"- Buckets: {', '.join(authority['buckets']) or 'none'}",
                "",
                authority["excerptText"] or "No excerpt text recorded.",
                "",
                f"Proposition: {authority['proposition']}",
                "",
            ]
        )
    return "\n".join(lines)


def build_brief_index(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    active_outcome = "violation" if result["outcome"]["violation"] else "no_violation"
    authority_trust = build_authority_trust_profile(case_payload)
    fit_summary = _build_fit_summary(case_payload)
    fit_finding_summary = _build_fit_finding_summary(fit_summary)
    source_summary = _build_source_summary(case_payload)

    def label_for(priority: int) -> str:
        if priority == 1:
            return "primary"
        if priority <= 3:
            return "secondary"
        return "supporting"

    def entry(
        *,
        kind: str,
        path: str,
        format: str,
        description: str,
    ) -> Dict[str, Any]:
        item = {
            "kind": kind,
            "path": path,
            "format": format,
            "description": description,
            "priority": priority_map[kind],
            "priorityLabel": label_for(priority_map[kind]),
            "whyOpenThis": _entry_why_open_this(kind, branch, primary_kind),
        }
        if authority_trust["severity"] == "warning":
            item["trustWarning"] = {
                "severity": authority_trust["severity"],
                "label": authority_trust["label"],
                "message": authority_trust["advisory"],
            }
        return item

    branch = result["branch"]
    if branch == "evidentiary_gap":
        primary_kind = "summary"
        priority_map = {
            "summary": 1,
            "demand_letter_markdown": 2,
            "memorandum_markdown": 3,
            "result": 4,
            "advocacy_bundle": 5,
            "hearing_script_markdown": 6,
            "negotiation_summary_markdown": 7,
            "complaint_outline_markdown": 8,
            "memorandum_pdf": 9,
            "dependency_graph": 10,
            "memorandum_json": 11,
            "dependency_citations": 12,
            "authority_review": 13,
            "authority_research_note": 14,
            "authority_summary": 15,
            "decision_tree": 16,
        }
    elif branch == "effective_accommodation":
        primary_kind = "memorandum_markdown"
        priority_map = {
            "memorandum_markdown": 1,
            "summary": 2,
            "hearing_script_markdown": 3,
            "memorandum_pdf": 4,
            "result": 5,
            "advocacy_bundle": 6,
            "negotiation_summary_markdown": 7,
            "demand_letter_markdown": 8,
            "complaint_outline_markdown": 9,
            "dependency_graph": 10,
            "memorandum_json": 11,
            "dependency_citations": 12,
            "authority_review": 13,
            "authority_research_note": 14,
            "authority_summary": 15,
            "decision_tree": 16,
        }
    else:
        primary_kind = "memorandum_pdf"
        priority_map = {
            "memorandum_pdf": 1,
            "memorandum_markdown": 2,
            "summary": 3,
            "result": 4,
            "advocacy_bundle": 5,
            "demand_letter_markdown": 6,
            "negotiation_summary_markdown": 7,
            "hearing_script_markdown": 8,
            "complaint_outline_markdown": 9,
            "dependency_graph": 10,
            "memorandum_json": 11,
            "dependency_citations": 12,
            "authority_review": 13,
            "authority_research_note": 14,
            "authority_summary": 15,
            "decision_tree": 16,
        }

    entries = [
        entry(kind="summary", path="summary.json", format="json", description="Compact branch-aware summary for downstream tooling."),
        entry(kind="result", path=f"../{result['caseId']}.result.json", format="json", description="Full evaluator output with findings, explanations, and provenance."),
        entry(kind="advocacy_bundle", path="advocacy_bundle.json", format="json", description="Structured advocacy citations and drafting metadata."),
        entry(kind="hearing_script_markdown", path="hearing_script.md", format="markdown", description="Hearing script draft grounded in the evaluated case state."),
        entry(kind="complaint_outline_markdown", path="complaint_outline.md", format="markdown", description="Complaint outline draft for the current branch posture."),
        entry(kind="demand_letter_markdown", path="demand_letter.md", format="markdown", description="Demand-letter draft for the current branch posture."),
        entry(kind="negotiation_summary_markdown", path="negotiation_summary.md", format="markdown", description="Negotiation summary draft with branch-aware leverage framing."),
        entry(kind="memorandum_json", path="memorandum.json", format="json", description="Structured memorandum sections with citation rollups and paragraph support."),
        entry(kind="memorandum_markdown", path="memorandum.md", format="markdown", description="Human-readable memorandum with visible section and paragraph support blocks."),
        entry(kind="memorandum_pdf", path="memorandum_of_law.pdf", format="pdf", description="Printable memorandum of law with paragraph-level support lines."),
        entry(kind="dependency_graph", path="dependency_graph.json", format="json", description="Dependency graph nodes and edges for the active reasoning branch."),
        entry(kind="dependency_citations", path="dependency_citations.jsonld", format="jsonld", description="JSON-LD grounding that links dependency targets to authority excerpts."),
        entry(kind="authority_review", path="authority_review.json", format="json", description="Audit view of authority excerpts, propositions, source URLs, and support status."),
        entry(kind="authority_research_note", path="authority_research_note.json", format="json", description="Research-note view of verified source references, excerpts, fit, and proposition mapping."),
        entry(kind="authority_summary", path="authority_summary.json", format="json", description="Compact counts by authority support status and reasoning bucket."),
        entry(kind="decision_tree", path="decision_tree.json", format="json", description="Decision-tree representation of the accommodation analysis."),
    ]
    warning_counts: Dict[str, int] = {}
    for item in entries:
        if not item.get("trustWarning"):
            continue
        label = item["trustWarning"]["label"]
        warning_counts[label] = warning_counts.get(label, 0) + 1
    recommended_first_stop = next(item["path"] for item in entries if item["kind"] == primary_kind)
    why_open_this = _recommended_first_stop_note(primary_kind, result["branch"])
    return {
        "caseId": result["caseId"],
        "branch": result["branch"],
        "activeOutcome": active_outcome,
        "primaryKind": primary_kind,
        "recommendedFirstStop": recommended_first_stop,
        "whyOpenThis": why_open_this,
        "authorityTrust": authority_trust,
        "sourceSummary": source_summary,
        "fitSummary": fit_summary,
        "fitFindingSummary": fit_finding_summary,
        "warningSummary": {
            "hasWarnings": any("trustWarning" in item for item in entries),
            "warningEntryCount": sum(warning_counts.values()),
            "warningCounts": dict(sorted(warning_counts.items())),
        },
        "warningLabelSummary": {
            "hasWarningLabel": authority_trust["severity"] == "warning",
            "warningLabel": authority_trust["label"] if authority_trust["severity"] == "warning" else None,
            "warningEntryCount": sum(warning_counts.values()),
        },
        "entries": entries,
    }


def build_manifest(case_payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(case_payload)
    authority_trust = build_authority_trust_profile(case_payload)
    fit_summary = _build_fit_summary(case_payload)
    fit_finding_summary = _build_fit_finding_summary(fit_summary)
    source_summary = _build_source_summary(case_payload)
    brief_index = build_brief_index(case_payload)
    return {
        "caseId": case_payload["caseId"],
        "branch": result["branch"],
        "authorityTrust": authority_trust,
        "sourceSummary": source_summary,
        "fitSummary": fit_summary,
        "fitFindingSummary": fit_finding_summary,
        "recommendedFirstStop": brief_index["recommendedFirstStop"],
        "whyOpenThis": brief_index["whyOpenThis"],
        "artifactBundle": "live_in_aide_reasoning_package",
        "artifacts": [
            "README.md",
            "legal_reasoning.pl",
            "event_calculus.pl",
            "context.json",
            "case_instance.jsonld",
            "hearing_script.txt",
            "hearing_script.md",
            "complaint_outline.txt",
            "complaint_outline.md",
            "demand_letter.txt",
            "demand_letter.md",
            "negotiation_summary.txt",
            "negotiation_summary.md",
            "advocacy_bundle.json",
            "memorandum.json",
            "memorandum.md",
            "memorandum_of_law.pdf",
            "dependency_graph.json",
            "dependency_citations.jsonld",
            "authority_review.json",
            "authority_review.md",
            "authority_research_note.json",
            "authority_research_note.md",
            "authority_summary.json",
            "decision_tree.json",
            "summary.json",
            "brief_index.json",
            "tests.json",
            "manifest.json",
        ],
        "artifactGuidance": _manifest_artifact_guidance(brief_index, result["branch"]),
        "notes": [
            "This package is generated from the canonical workspace2 fixture.",
            "The manifest exists so exported bundles can be validated without relying on repo conventions.",
            f"Canonical branch for this package: {result['branch']}.",
        ],
    }


def build_readme(case_payload: Dict[str, Any]) -> str:
    result = evaluate_case(case_payload)
    authority_trust = build_authority_trust_profile(case_payload)
    source_summary = _build_source_summary(case_payload)
    fit_summary = _build_fit_summary(case_payload)
    fit_finding = _build_fit_finding(fit_summary)
    brief_index = build_brief_index(case_payload)
    manifest = build_manifest(case_payload)
    recommended_first_stop = brief_index["recommendedFirstStop"]
    why_open_this = brief_index["whyOpenThis"]
    notes = [
        "This is a modeling package, not verified legal advice.",
        "It encodes asserted facts and legal theories into computational structures.",
        "Separate asserted facts, accepted findings, and legal conclusions in production use.",
    ]
    if authority_trust["label"] == "fully_verified":
        notes.append("Authority grounding note: all currently attached authority support is marked as verified_quote.")
    else:
        notes.append(f"Authority grounding note: {authority_trust['advisory']}")
    return f"""# Legal Reasoning Package

This package contains a prototype formalization of the live-in aide accommodation dispute in:
- Prolog/Datalog-style rules
- Event-calculus export
- JSON-LD context and case instance
- Advocacy drafts and structured bundle
- Memorandum bundle with PDF output
- Dependency graph
- Decision tree
- Regression test fixtures
- Bundle manifest

Case Metadata:
- Case ID: `{result['caseId']}`
- Branch: `{result['branch']}`
- Active Outcome: `{'violation' if result['outcome']['violation'] else 'no_violation'}`
- Authority Trust: `{authority_trust['label']}`
- Source Verified Count: `{source_summary['sourceVerifiedCount']}`
- Source Normalized Count: `{source_summary['sourceNormalizedCount']}`
- Source Status: {source_summary['sourceStatus']}
- Direct Fit Count: `{fit_summary['directCount']}`
- Analogical Fit Count: `{fit_summary['analogicalCount']}`
- Record-Support Fit Count: `{fit_summary['recordSupportCount']}`
- Fit Status: {fit_summary['fitStatus']}
- Fit Finding: `{fit_finding['label']}`
- Fit Finding Note: {fit_finding['note']}
- Recommended First Stop: `{recommended_first_stop}`
- Why Open This: {why_open_this}

Files:
- legal_reasoning.pl
- event_calculus.pl
- context.json
- case_instance.jsonld
- hearing_script.txt
- hearing_script.md
- complaint_outline.txt
- complaint_outline.md
- demand_letter.txt
- demand_letter.md
- negotiation_summary.txt
- negotiation_summary.md
- advocacy_bundle.json
- memorandum.json
- memorandum.md
- memorandum_of_law.pdf
- dependency_graph.json
- dependency_citations.jsonld
- authority_review.json
- authority_review.md
- authority_research_note.json
- authority_research_note.md
- authority_summary.json
- decision_tree.json
- summary.json
- brief_index.json
- tests.json
- manifest.json

Notes:
{chr(10).join(f"- {note}" for note in notes)}

Artifact Guide:
{chr(10).join(f"- `{item['path']}`: {item['whyOpenThis']}" for item in manifest["artifactGuidance"])}
"""


def export_package(fixture_path: Path) -> Path:
    case_payload = load_case(fixture_path)
    export_dir = ROOT / "outputs" / f"{case_payload['caseId']}_package"
    export_dir.mkdir(parents=True, exist_ok=True)
    grounding = build_dependency_citations_jsonld(case_payload)
    memorandum = generate_memorandum_bundle(case_payload)
    advocacy_outputs = generate_advocacy_outputs(case_payload)
    advocacy_bundle = generate_advocacy_bundle(case_payload)
    _write_text_atomic(export_dir / "legal_reasoning.pl", build_prolog(case_payload))
    _write_text_atomic(export_dir / "event_calculus.pl", build_event_calculus(case_payload))
    _write_text_atomic(export_dir / "context.json", json.dumps(build_context(), indent=2) + "\n")
    _write_text_atomic(export_dir / "case_instance.jsonld", json.dumps(build_case_instance(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "decision_tree.json", json.dumps(build_decision_tree(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "dependency_graph.json", json.dumps(build_dependency_graph(case_payload), indent=2) + "\n")
    write_advocacy_artifacts(export_dir, advocacy_outputs, advocacy_bundle, include_readme=False)
    write_memorandum_artifacts(export_dir, memorandum, grounding, include_readme=False)
    _write_text_atomic(export_dir / "authority_review.json", json.dumps(build_authority_review(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "authority_review.md", build_authority_review_markdown(case_payload) + "\n")
    _write_text_atomic(export_dir / "authority_research_note.json", json.dumps(build_authority_research_note(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "authority_research_note.md", build_authority_research_note_markdown(case_payload) + "\n")
    _write_text_atomic(export_dir / "authority_summary.json", json.dumps(build_authority_summary(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "summary.json", json.dumps(build_summary(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "brief_index.json", json.dumps(build_brief_index(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "tests.json", json.dumps(build_tests(), indent=2) + "\n")
    _write_text_atomic(export_dir / "manifest.json", json.dumps(build_manifest(case_payload), indent=2) + "\n")
    _write_text_atomic(export_dir / "README.md", build_readme(case_payload))
    return export_dir


def main() -> int:
    fixture_path = ROOT / "fixtures" / "live_in_aide_case.json"
    export_dir = export_package(fixture_path)
    print(export_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
