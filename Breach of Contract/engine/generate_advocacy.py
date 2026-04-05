#!/usr/bin/env python3
"""Generate advocacy-oriented text outputs from an evaluated case."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.evaluate_case import evaluate_case
from engine.authority_fit import infer_fit_kind
from engine.authority_trust import build_authority_trust_profile


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)


def _placeholders(branch: str) -> Dict[str, str]:
    requested_remedy = "[Approve a separate bedroom for the live-in aide]"
    if branch == "effective_accommodation":
        requested_remedy = "[Maintain the effective separate-bedroom accommodation for the live-in aide]"
    return {
        "requesting_party": "[Requesting Party]",
        "recipient": "[Housing Authority or Decision-Maker]",
        "tenant_name": "[Tenant Name]",
        "aide_name": "[Aide Name]",
        "requested_remedy": requested_remedy,
        "response_deadline": "[10 business days]",
    }


def _authority_labels(result: Dict[str, Any], bucket: str) -> str:
    labels = [item["label"] for item in result.get("authoritySupport", {}).get(bucket, [])]
    return ", ".join(labels) if labels else "the authorities attached to this case"


def _authority_meta_map(payload: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in payload.get("authorities", [])}


def _harm_lines(result: Dict[str, Any]) -> list[str]:
    outcome = result["outcome"]
    lines = []
    if outcome["sleepInterruption"]:
        lines.append("The aide's sleep is disrupted because the sleeping space is shared and used at night.")
    if outcome["workInterference"]:
        lines.append("The shared sleeping arrangement interferes with the aide's remote software work.")
    if outcome["caregivingImpairment"]:
        lines.append("Fatigue from the arrangement undermines caregiving effectiveness.")
    if outcome["privacyLoss"]:
        lines.append("The arrangement creates a meaningful privacy loss within the home.")
    if not lines:
        lines.append("No functional harms were established on the accepted findings.")
    return lines


def _defense_lines(result: Dict[str, Any]) -> list[str]:
    lines = []
    defeaters = result.get("defeatersConsidered", {})
    if defeaters.get("undueBurden"):
        lines.append("The provider asserts an undue-burden defense against the requested accommodation.")
    if defeaters.get("fundamentalAlteration"):
        lines.append("The provider asserts a fundamental-alteration defense against the requested accommodation.")
    return lines


def _branch_type(result: Dict[str, Any]) -> str:
    if result.get("branch") == "undue_burden_constructive_denial":
        return "undue_burden"
    if result.get("branch") == "constructive_denial":
        return "constructive_denial"
    if result.get("branch") == "effective_accommodation":
        return "effective_accommodation"
    return "evidentiary_gap"


def _branch_language(result: Dict[str, Any]) -> Dict[str, str]:
    branch = _branch_type(result)
    if branch == "undue_burden":
        return {
            "hearing_position": (
                "The evaluated record supports constructive denial even though the provider has raised an undue-burden defense to the requested configuration."
            ),
            "hearing_close": (
                "Even with that asserted defense, an accommodation that exists on paper but fails in practice is not an effective accommodation."
            ),
            "complaint_theory": (
                "The accepted findings support a constructive-denial theory, while preserving a live dispute over the provider's undue-burden defense."
            ),
            "demand_position": (
                "The current evaluated record supports the conclusion that the separate-bedroom denial amounts to constructive denial of accommodation, even if the provider intends to rely on undue burden."
            ),
            "demand_subject": "Subject: Demand to Cure Constructive Denial Despite Undue-Burden Defense",
            "demand_request": "Please confirm in writing whether the approved accommodation will now include a separate bedroom for the live-in aide notwithstanding the asserted undue-burden position.",
            "demand_closing": "If the provider maintains its undue-burden position, please identify the factual basis for that defense and the alternative effective arrangement being offered.",
            "negotiation_posture": (
                "The strongest current theory is constructive denial, while the provider's likely negotiation position will center on undue burden rather than on the absence of harm."
            ),
        }
    if branch == "constructive_denial":
        return {
            "hearing_position": (
                "The evaluated record supports constructive denial because the aide was approved in principle but denied the separate bedroom needed to function."
            ),
            "hearing_close": (
                "An accommodation that exists on paper but fails in practice is not an effective accommodation."
            ),
            "complaint_theory": (
                "The accepted findings support a constructive denial theory because the accommodation was nominally recognized but denied in effective form."
            ),
            "demand_position": (
                "The current evaluated record supports the conclusion that the separate-bedroom denial amounts to constructive denial of accommodation."
            ),
            "demand_subject": "Subject: Demand to Cure Constructive Denial of Live-In Aide Accommodation",
            "demand_request": "Please confirm in writing whether the approved accommodation includes a separate bedroom for the live-in aide.",
            "demand_closing": "Please provide that confirmation by the requested deadline so this matter can be resolved without further escalation.",
            "negotiation_posture": (
                "The strongest current theory is constructive denial."
            ),
        }
    if branch == "effective_accommodation":
        return {
            "hearing_position": (
                "The current evaluated record reflects that the provider recognized the accommodation duty and implemented an arrangement that appears effective in practice."
            ),
            "hearing_close": (
                "On the accepted findings, this record looks more like a successfully implemented accommodation than a denial."
            ),
            "complaint_theory": (
                "The accepted findings currently point away from a denial theory because the requested accommodation appears to have been satisfied in effective form."
            ),
            "demand_position": (
                "The current evaluated record suggests the accommodation has been implemented in a workable form, so the immediate focus should be preserving that arrangement rather than escalating a denial claim."
            ),
            "demand_subject": "Subject: Request to Preserve Effective Live-In Aide Accommodation",
            "demand_request": "Please confirm in writing that the current separate-bedroom arrangement for the live-in aide will be maintained.",
            "demand_closing": "Please preserve the current arrangement and identify any future changes early enough for the household to respond without disruption.",
            "negotiation_posture": (
                "The current record indicates the accommodation is functioning in practice, so negotiations should focus on maintaining compliance and documenting the effective arrangement."
            ),
        }
    return {
        "hearing_position": (
            "The current record does not establish constructive denial, but it does identify concrete accommodation questions that should be resolved before the matter hardens into a denial."
        ),
        "hearing_close": (
            "The current record should be supplemented until the decision-maker can determine whether the accommodation is effective in practice."
        ),
        "complaint_theory": (
            "The accepted findings currently support further factual development rather than a finished constructive-denial theory."
        ),
        "demand_position": (
            "The current evaluated record shows accommodation concerns and evidentiary gaps that should be resolved cooperatively without further escalation."
        ),
        "demand_subject": "Subject: Request for Clarification and Completion of Live-In Aide Accommodation",
        "demand_request": "Please confirm in writing what effective accommodation is currently being provided and what additional information is needed to complete the request.",
        "demand_closing": "If additional documentation is needed, please identify it specifically so the record can be completed promptly.",
        "negotiation_posture": (
            "The current record does not yet prove constructive denial, so the negotiation posture should focus on filling the remaining evidentiary gaps and clarifying whether an effective accommodation is actually being provided."
        ),
    }


def _mode_citations(payload: Dict[str, Any], result: Dict[str, Any], finding_names: list[str]) -> Dict[str, Any]:
    authority_meta = _authority_meta_map(payload)
    authority_label_by_id = {}
    for bucket in result.get("authoritySupport", {}).values():
        for item in bucket:
            authority_label_by_id[item["id"]] = item["label"]

    authority_ids = []
    evidence_ids = []
    event_ids = []
    proof_steps = []
    for finding_name in finding_names:
        provenance = result.get("provenance", {}).get(finding_name, {})
        authority_ids.extend(provenance.get("authorityIds", []))
        evidence_ids.extend(provenance.get("evidenceIds", []))
        event_ids.extend(provenance.get("eventIds", []))
        proof_steps.extend(provenance.get("proofSteps", []))
    authority_ids = sorted(set(authority_ids))
    authority_details = []
    for authority_id in authority_ids:
        meta = authority_meta.get(authority_id, {})
        authority_details.append(
            {
                "id": authority_id,
                "label": authority_label_by_id.get(authority_id, meta.get("label", authority_id)),
                "court": meta.get("court"),
                "year": meta.get("year"),
                "pincite": meta.get("pincite"),
                "sourceUrl": meta.get("sourceUrl"),
                "excerptKind": meta.get("excerptKind", "paraphrase"),
                "excerptText": meta.get("excerptText", meta.get("notes", "")),
                "proposition": meta.get("proposition", meta.get("notes", "")),
                "fitKind": infer_fit_kind(meta),
            }
        )
    return {
        "findingIds": finding_names,
        "authorityIds": authority_ids,
        "authorityLabels": [authority_label_by_id[item] for item in authority_ids if item in authority_label_by_id],
        "authorityDetails": authority_details,
        "evidenceIds": sorted(set(evidence_ids)),
        "eventIds": sorted(set(event_ids)),
        "proofSteps": sorted(set(proof_steps)),
    }


def _citation_line(citations: Dict[str, Any]) -> str:
    return (
        "Citations: "
        f"findings={', '.join(citations['findingIds']) or 'none'}; "
        f"authorities={', '.join(citations.get('authorityLabels', [])) or 'none'}; "
        f"evidence={', '.join(citations['evidenceIds']) or 'none'}; "
        f"events={', '.join(citations['eventIds']) or 'none'}"
    )


def generate_advocacy_bundle(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(payload)
    case_id = result["caseId"]
    constructive = result["outcome"]["constructiveDenial"]
    violation = result["outcome"]["violation"]
    branch = _branch_type(result)
    placeholders = _placeholders(branch)
    harms = _harm_lines(result)
    defenses = _defense_lines(result)
    branch_language = _branch_language(result)
    authority_trust = build_authority_trust_profile(payload)
    violation_authorities = _authority_labels(result, "violation")
    duty_authorities = _authority_labels(result, "dutyToGrant")

    mode_findings = {
        "hearing_script": ["dutyToGrant", "constructiveDenial", "violation"],
        "complaint_outline": ["necessary", "reasonable", "constructiveDenial", "violation"],
        "demand_letter": ["constructiveDenial", "violation"],
        "negotiation_summary": ["reasonable", "constructiveDenial", "violation"],
    }
    citations = {
        mode: _mode_citations(payload, result, finding_names)
        for mode, finding_names in mode_findings.items()
    }

    intro_block = [
        f"Case: {case_id}",
        f"Requested remedy: {placeholders['requested_remedy']}",
        f"Requesting party: {placeholders['requesting_party']}",
        "",
    ]

    texts = {
        "hearing_script": "\n".join(
            intro_block + [
                "Opening:",
                "This case asks whether the approved live-in aide accommodation is effective in practice.",
                branch_language["hearing_position"],
                f"Authority grounding note: {authority_trust['advisory']}",
                _citation_line(citations["hearing_script"]),
                "",
                "Core points:",
                *[f"- {line}" for line in harms],
                *[f"- {line}" for line in defenses],
                f"- Supporting authorities for the accommodation duty include: {duty_authorities}.",
                "",
                "Closing:",
                branch_language["hearing_close"] if violation else branch_language["hearing_close"],
            ]
        ),
        "complaint_outline": "\n".join(
            intro_block + [
                f"Complaint Outline For {case_id}",
                "",
                "Claim:",
                "Failure to provide a reasonable accommodation under the Fair Housing Act.",
                f"Authority grounding note: {authority_trust['advisory']}",
                _citation_line(citations["complaint_outline"]),
                "",
                "Core allegations:",
                "- The tenant is disabled and needs a live-in aide.",
                "- Medical verification supports the requested accommodation.",
                "- A separate bedroom was requested for the aide.",
                (
                    "- The housing provider approved the aide in principle but denied the separate bedroom."
                    if result["facts"]["resolved"]["denied_separate_bedroom"]
                    else "- The housing provider approved the aide in principle and the current record indicates the separate-bedroom request was satisfied in practice."
                ),
                *[f"- {line}" for line in harms],
                *[f"- {line}" for line in defenses],
                "",
                "Theory:",
                branch_language["complaint_theory"],
                "",
                f"Authorities to cite: {violation_authorities}.",
            ]
        ),
        "demand_letter": "\n".join(
            [
                branch_language["demand_subject"],
                "",
                f"To: {placeholders['recipient']}",
                "",
                f"From: {placeholders['requesting_party']}",
                f"Requested remedy: {placeholders['requested_remedy']}",
                f"Requested response deadline: {placeholders['response_deadline']}",
                "",
                "This letter requests prompt approval of an accommodation that is effective in practice, not merely nominal.",
                branch_language["demand_position"],
                f"Authority grounding note: {authority_trust['advisory']}",
                _citation_line(citations["demand_letter"]),
                f"The present reasoning output identifies these harms: {' '.join(harms)}",
                *defenses,
                f"Supporting authorities include {violation_authorities}.",
                "",
                branch_language["demand_request"],
                branch_language["demand_closing"],
                "",
                "Sincerely,",
                placeholders["requesting_party"],
            ]
        ),
        "negotiation_summary": "\n".join(
            intro_block + [
                f"Negotiation Summary For {case_id}",
                "",
                "Leverage points:",
                "- The issue is whether the accommodation is effective in practice.",
                f"- {branch_language['negotiation_posture']}",
                f"- Authority grounding note: {authority_trust['advisory']}",
                *[f"- {line}" for line in defenses],
                _citation_line(citations["negotiation_summary"]),
                f"- The evaluator confidence score is {result['confidence']:.2f}.",
                f"- Missing elements or evidence gaps: {', '.join(result['missingEvidence']) or 'none'}.",
                f"- Authorities currently grouped under violation: {violation_authorities}.",
            ]
        ),
    }

    return {
        "meta": {
            "caseId": case_id,
            "branch": result["branch"],
            "placeholders": placeholders,
            "supportedModes": [
                "hearing_script",
                "complaint_outline",
                "demand_letter",
                "negotiation_summary",
            ],
            "confidence": result["confidence"],
            "authorityTrust": authority_trust,
        },
        "citations": citations,
        "texts": texts,
    }


def generate_advocacy_outputs(payload: Dict[str, Any]) -> Dict[str, str]:
    bundle = generate_advocacy_bundle(payload)
    return {
        "meta": json.dumps(bundle["meta"], indent=2),
        **bundle["texts"],
    }


def _as_markdown(title: str, content: str) -> str:
    lines = content.splitlines()
    out = [f"# {title}", ""]
    in_list = False
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if in_list:
                out.append("")
                in_list = False
            else:
                out.append("")
            continue
        if stripped.endswith(":") and not stripped.startswith("- "):
            if in_list:
                out.append("")
                in_list = False
            out.append(f"## {stripped[:-1]}")
            out.append("")
            continue
        if stripped.startswith("- "):
            out.append(stripped)
            in_list = True
            continue
        if in_list:
            out.append("")
            in_list = False
        out.append(stripped)
    return "\n".join(out).rstrip() + "\n"


def write_advocacy_artifacts(
    output_dir: Path,
    outputs: Dict[str, str],
    bundle: Dict[str, Any],
    include_readme: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in outputs.items():
        _write_text_atomic(output_dir / f"{name}.txt", content + "\n")
        title = name.replace("_", " ").title()
        _write_text_atomic(output_dir / f"{name}.md", _as_markdown(title, content))
    _write_text_atomic(output_dir / "advocacy_bundle.json", json.dumps(bundle, indent=2) + "\n")
    if include_readme:
        index = "\n".join(
            [
                "# Advocacy Outputs",
                "",
                "Files:",
                *[f"- {name}.txt" for name in outputs.keys()],
                *[f"- {name}.md" for name in outputs.keys()],
                "- advocacy_bundle.json",
                "",
            ]
        )
        _write_text_atomic(output_dir / "README.md", index)
    return output_dir


def write_advocacy_outputs(fixture_path: Path, outputs: Dict[str, str]) -> Path:
    output_dir = fixture_path.resolve().parent.parent / "outputs" / f"{fixture_path.stem}_advocacy"
    payload = json.loads(fixture_path.read_text())
    bundle = generate_advocacy_bundle(payload)
    return write_advocacy_artifacts(output_dir, outputs, bundle, include_readme=True)


def write_advocacy_bundle(fixture_path: Path, bundle: Dict[str, Any]) -> Path:
    output_dir = fixture_path.resolve().parent.parent / "outputs" / f"{fixture_path.stem}_advocacy"
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_text_atomic(output_dir / "advocacy_bundle.json", json.dumps(bundle, indent=2) + "\n")
    return output_dir


def main(argv: list[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: generate_advocacy.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    write_output = len(argv) == 3 and argv[2] == "--write"
    if len(argv) == 3 and not write_output:
        print("usage: generate_advocacy.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text())
    outputs = generate_advocacy_outputs(payload)
    bundle = generate_advocacy_bundle(payload)
    print(json.dumps(outputs, indent=2))
    if write_output:
        output_dir = write_advocacy_outputs(path, outputs)
        write_advocacy_bundle(path, bundle)
        print(f"\nWrote advocacy outputs to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
