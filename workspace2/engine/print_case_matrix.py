#!/usr/bin/env python3
"""Print a readable matrix of generated case/package artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
import time
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parent.parent


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text())


def _kind_map(entries: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {entry["kind"]: entry for entry in entries}


def _sort_cases(cases: List[Dict[str, Any]], sort_key: str) -> List[Dict[str, Any]]:
    if sort_key == "confidence":
        return sorted(cases, key=lambda case: (-case["confidence"], case["caseId"]))
    if sort_key == "warningCount":
        return sorted(cases, key=lambda case: (-case.get("warningEntryCount", -1), case["caseId"]))
    if sort_key == "branch":
        return sorted(cases, key=lambda case: (case["branch"], case["caseId"]))
    return sorted(cases, key=lambda case: case["caseId"])


def _count_labels(items: List[Dict[str, Any]], key: str) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        label = item.get(key)
        if not label:
            continue
        counts[label] = counts.get(label, 0) + 1
    return dict(sorted(counts.items()))


def _sort_kind_rows(rows: List[Dict[str, Any]], sort_key: str) -> List[Dict[str, Any]]:
    if sort_key == "warningCaseCount":
        return sorted(rows, key=lambda item: (-item["warningCaseCount"], item["kind"]))
    return sorted(rows, key=lambda item: item["kind"])


def _compute_elapsed_seconds(started_at: str | None, completed_at: str | None) -> float | None:
    if not started_at or not completed_at:
        return None
    started = datetime.fromisoformat(started_at)
    completed = datetime.fromisoformat(completed_at)
    return max((completed - started).total_seconds(), 0.0)


def _format_elapsed_duration(elapsed_seconds: float | None) -> str | None:
    if elapsed_seconds is None:
        return None
    if elapsed_seconds < 1:
        return f"{round(elapsed_seconds * 1000)} ms"
    if elapsed_seconds < 60:
        return f"{elapsed_seconds:.3f} s"
    minutes, seconds = divmod(elapsed_seconds, 60)
    if minutes < 60:
        return f"{int(minutes)}m {seconds:.1f}s"
    hours, minutes = divmod(int(minutes), 60)
    return f"{hours}h {minutes}m {seconds:.0f}s"


def _load_case_rows(
    root: Path,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    warned_only: bool = False,
) -> List[Dict[str, Any]]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    outputs_index = _load_json(root / "outputs" / "index.json")
    cases = []
    for case in outputs_index["cases"]:
        if branch and case["branch"] != branch:
            continue
        if case_id and case["caseId"] != case_id:
            continue
        package_dir = root / case["packagePath"]
        brief_index = _load_json(package_dir / "brief_index.json")
        if trust and brief_index["authorityTrust"]["label"] != trust:
            continue
        if warning_label and brief_index["authorityTrust"]["label"] != warning_label:
            continue
        if fit_finding and brief_index["fitFindingSummary"]["fitFinding"] != fit_finding:
            continue
        brief_entries = brief_index["entries"]
        if warned_only:
            brief_entries = [entry for entry in brief_entries if entry.get("trustWarning")]
        kinds = _kind_map(brief_entries)
        cases.append(
            {
                "caseId": case["caseId"],
                "branch": case["branch"],
                "activeOutcome": case["activeOutcome"],
                "confidence": case["confidence"],
                "authorityTrust": brief_index["authorityTrust"]["label"],
                "sourceSummary": brief_index["sourceSummary"],
                "fitSummary": brief_index["fitSummary"],
                "fitFindingSummary": brief_index["fitFindingSummary"],
                "warningSummary": brief_index["warningSummary"],
                "warningLabelSummary": brief_index["warningLabelSummary"],
                "recommendedFirstStop": brief_index["recommendedFirstStop"],
                "whyOpenThis": brief_index["whyOpenThis"],
                "packagePath": case["packagePath"],
                "primaryKind": brief_index["primaryKind"],
                "entries": {
                    "summary": kinds.get("summary", {}).get("path"),
                    "advocacy": kinds.get("advocacy_bundle", {}).get("path"),
                    "memorandum": kinds.get("memorandum_pdf", {}).get("path"),
                    "dependencyGraph": kinds.get("dependency_graph", {}).get("path"),
                },
                "briefEntries": brief_entries,
            }
        )
    return cases


def build_case_matrix_data(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only and case_id is not None,
    )
    if fit_finding:
        cases = [case for case in cases if case["fitFindingSummary"]["fitFinding"] == fit_finding]
    if warned_only and case_id is None:
        cases = [case for case in cases if case["warningSummary"]["hasWarnings"]]
    if top_n is not None:
        if top_n < 1:
            raise ValueError("top-n mode requires a positive integer")
        for case in cases:
            case["briefEntries"] = sorted(case["briefEntries"], key=lambda item: (item["priority"], item["kind"]))[:top_n]
            case["topEntries"] = case["briefEntries"]
    for case in cases:
        primary_entry = next((entry for entry in case["briefEntries"] if entry["kind"] == case["primaryKind"]), None)
        case["primaryEntryWhyOpenThis"] = primary_entry["whyOpenThis"] if primary_entry else case["whyOpenThis"]
        case.pop("briefEntries", None)
    return {"cases": _sort_cases(cases, sort_key)}


def render_case_matrix(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
) -> str:
    matrix = build_case_matrix_data(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        fit_finding=fit_finding,
        warned_only=warned_only,
        sort_key=sort_key,
    )
    lines = [
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        "",
        "Case ID | Branch | Outcome | Conf | Trust | Fit Finding | Warn | WarnCt | Primary | Primary Why | Package | Key Package Entries",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in matrix["cases"]:
        key_entries = [
            f"summary={case['entries']['summary']}",
            f"advocacy={case['entries']['advocacy']}",
            f"memo={case['entries']['memorandum']}",
            f"graph={case['entries']['dependencyGraph']}",
        ]
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["activeOutcome"],
                    f"{case['confidence']:.2f}",
                    case["authorityTrust"],
                    case["fitFindingSummary"]["fitFinding"],
                    "yes" if case["warningSummary"]["hasWarnings"] else "no",
                    str(case["warningSummary"]["warningEntryCount"]),
                    case["primaryKind"],
                    case["primaryEntryWhyOpenThis"],
                    case["packagePath"],
                    "; ".join(key_entries),
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_case_detail(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
) -> str:
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"detail view requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    lines = [
        f"Case ID: {case['caseId']}",
        f"Branch: {case['branch']}",
        f"Outcome: {case['activeOutcome']}",
        f"Confidence: {case['confidence']:.2f}",
        f"Authority Trust: {case['authorityTrust']}",
        f"Source Verified Count: {case['sourceSummary']['sourceVerifiedCount']}",
        f"Source Normalized Count: {case['sourceSummary']['sourceNormalizedCount']}",
        f"Source Status: {case['sourceSummary']['sourceStatus']}",
        f"Direct Fit Count: {case['fitSummary']['directCount']}",
        f"Analogical Fit Count: {case['fitSummary']['analogicalCount']}",
        f"Record-Support Fit Count: {case['fitSummary']['recordSupportCount']}",
        f"Fit Status: {case['fitSummary']['fitStatus']}",
        f"Fit Finding: {case['fitFindingSummary']['fitFinding']}",
        f"Fit Finding Note: {case['fitFindingSummary']['fitFindingNote']}",
        f"Warnings: {'yes' if case['warningSummary']['hasWarnings'] else 'no'}",
        f"Warning Label: {case['warningLabelSummary']['warningLabel'] or 'none'}",
        f"Warning Entry Count: {case['warningSummary']['warningEntryCount']}",
        f"Warning Counts: {case['warningSummary']['warningCounts'] or {}}",
        f"Primary Kind: {case['primaryKind']}",
        f"Recommended First Stop: {case['recommendedFirstStop']}",
        f"Why Open This: {case['whyOpenThis']}",
        f"Package: {case['packagePath']}",
        "",
        "Entries:",
    ]
    for entry in sorted(case["briefEntries"], key=lambda item: (item["priority"], item["kind"])):
        marker = " [primary]" if entry["kind"] == case["primaryKind"] else ""
        lines.append(
            f"- {entry['kind']} [{entry['format']}] priority={entry['priority']} ({entry['priorityLabel']}){marker} -> {entry['path']}"
        )
        lines.append(f"  whyOpenThis: {entry['whyOpenThis']}")
        lines.append(f"  {entry['description']}")
        if entry.get("trustWarning"):
            lines.append(
                f"  trustWarning: {entry['trustWarning']['label']} ({entry['trustWarning']['severity']}) - {entry['trustWarning']['message']}"
            )
    return "\n".join(lines) + "\n"


def render_top_artifacts(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
    top_n: int = 3,
) -> str:
    if top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"top-n mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    ranked = sorted(case["briefEntries"], key=lambda item: (item["priority"], item["kind"]))[:top_n]
    lines = [
        f"Case ID: {case['caseId']}",
        f"Authority Trust: {case['authorityTrust']}",
        f"Source Verified Count: {case['sourceSummary']['sourceVerifiedCount']}",
        f"Source Normalized Count: {case['sourceSummary']['sourceNormalizedCount']}",
        f"Source Status: {case['sourceSummary']['sourceStatus']}",
        f"Direct Fit Count: {case['fitSummary']['directCount']}",
        f"Analogical Fit Count: {case['fitSummary']['analogicalCount']}",
        f"Record-Support Fit Count: {case['fitSummary']['recordSupportCount']}",
        f"Fit Status: {case['fitSummary']['fitStatus']}",
        f"Fit Finding: {case['fitFindingSummary']['fitFinding']}",
        f"Fit Finding Note: {case['fitFindingSummary']['fitFindingNote']}",
        f"Warnings: {'yes' if case['warningSummary']['hasWarnings'] else 'no'}",
        f"Warning Label: {case['warningLabelSummary']['warningLabel'] or 'none'}",
        f"Warning Entry Count: {case['warningSummary']['warningEntryCount']}",
        f"Warning Counts: {case['warningSummary']['warningCounts'] or {}}",
        f"Primary Kind: {case['primaryKind']}",
        f"Recommended First Stop: {case['recommendedFirstStop']}",
        f"Why Open This: {case['whyOpenThis']}",
        f"Top {top_n} Entries:",
    ]
    for entry in ranked:
        marker = " [primary]" if entry["kind"] == case["primaryKind"] else ""
        lines.append(
            f"- {entry['kind']} [{entry['format']}] priority={entry['priority']} ({entry['priorityLabel']}){marker} -> {entry['path']}"
        )
        lines.append(f"  whyOpenThis: {entry['whyOpenThis']}")
        lines.append(f"  {entry['description']}")
        if entry.get("trustWarning"):
            lines.append(
                f"  trustWarning: {entry['trustWarning']['label']} ({entry['trustWarning']['severity']}) - {entry['trustWarning']['message']}"
            )
    return "\n".join(lines) + "\n"


def resolve_artifact_path(
    root: Path = ROOT,
    kind: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
) -> str:
    if not kind:
        raise ValueError("path-only mode requires --kind")
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"path-only mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    for entry in case["briefEntries"]:
        if entry["kind"] == kind:
            return str((root / case["packagePath"] / entry["path"]).resolve())
    available_kinds = ", ".join(entry["kind"] for entry in case["briefEntries"])
    raise ValueError(f"unknown kind '{kind}' for case {case['caseId']}; available kinds: {available_kinds}")


def resolve_primary_artifact_path(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
) -> str:
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"primary-only mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    return resolve_artifact_path(
        root,
        kind=case["primaryKind"],
        case_id=case["caseId"],
        warning_label=warning_label,
    )


def list_artifact_kinds(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
) -> str:
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"kinds mode requires exactly one matching case, found {len(cases)}: {available}")
    kinds = [entry["kind"] for entry in cases[0]["briefEntries"]]
    return "\n".join(kinds) + "\n"


def describe_artifact_kind(
    root: Path = ROOT,
    kind: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
) -> str:
    if not kind:
        raise ValueError("describe-kind mode requires --kind")
    cases = _load_case_rows(
        root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
    )
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"describe-kind mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    for entry in case["briefEntries"]:
        if entry["kind"] == kind:
            primary_marker = " [primary]" if entry["kind"] == case["primaryKind"] else ""
            warning_line = ""
            if entry.get("trustWarning"):
                warning = entry["trustWarning"]
                warning_line = f"trustWarning: {warning['label']} ({warning['severity']}) - {warning['message']}\n"
            return (
                f"{entry['kind']}{primary_marker}\n"
                f"authorityTrust: {case['authorityTrust']}\n"
                f"sourceVerifiedCount: {case['sourceSummary']['sourceVerifiedCount']}\n"
                f"sourceNormalizedCount: {case['sourceSummary']['sourceNormalizedCount']}\n"
                f"sourceStatus: {case['sourceSummary']['sourceStatus']}\n"
                f"directFitCount: {case['fitSummary']['directCount']}\n"
                f"analogicalFitCount: {case['fitSummary']['analogicalCount']}\n"
                f"recordSupportFitCount: {case['fitSummary']['recordSupportCount']}\n"
                f"fitStatus: {case['fitSummary']['fitStatus']}\n"
                f"fitFinding: {case['fitFindingSummary']['fitFinding']}\n"
                f"fitFindingNote: {case['fitFindingSummary']['fitFindingNote']}\n"
                f"warnings: {'yes' if case['warningSummary']['hasWarnings'] else 'no'}\n"
                f"warningLabel: {case['warningLabelSummary']['warningLabel'] or 'none'}\n"
                f"warningEntryCount: {case['warningSummary']['warningEntryCount']}\n"
                f"warningCounts: {case['warningSummary']['warningCounts'] or {}}\n"
                f"recommendedFirstStop: {case['recommendedFirstStop']}\n"
                f"whyOpenThis: {case['whyOpenThis']}\n"
                f"format: {entry['format']}\n"
                f"path: {entry['path']}\n"
                f"priority: {entry['priority']}\n"
                f"priorityLabel: {entry['priorityLabel']}\n"
                f"entryWhyOpenThis: {entry['whyOpenThis']}\n"
                f"{warning_line}"
                f"description: {entry['description']}\n"
            )
    available_kinds = ", ".join(entry["kind"] for entry in case["briefEntries"])
    raise ValueError(f"unknown kind '{kind}' for case {case['caseId']}; available kinds: {available_kinds}")


def render_authority_review(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    verified_only: bool = False,
    support_status: str | None = None,
    fit_kind: str | None = None,
) -> str:
    payload = build_authority_review_data(
        root=root,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        verified_only=verified_only,
        support_status=support_status,
        fit_kind=fit_kind,
    )
    authorities = payload["authorities"]
    lines = [
        f"Case ID: {payload['caseId']}",
        f"Branch: {payload['branch']}",
        f"Authorities: {len(authorities)}",
        f"Verified Only: {'yes' if payload['verifiedOnly'] else 'no'}",
        f"Support Status: {payload['supportStatus'] or 'any'}",
        f"Fit Kind: {payload['fitKind'] or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
        "Authority Review:",
    ]
    for authority in authorities:
        lines.append(
            f"- {authority['id']} [{authority['supportStatus']}] "
            f"{authority['label']} ({authority.get('court') or 'none'}, {authority.get('year') or 'none'}, {authority.get('pincite') or 'none'})"
        )
        lines.append(f"  buckets: {', '.join(authority.get('buckets', [])) or 'none'}")
        lines.append(f"  fit: {authority.get('fitKind') or 'none'}")
        lines.append(f"  source: {authority.get('sourceUrl') or 'none'}")
        lines.append(f"  proposition: {authority.get('proposition') or 'none'}")
    return "\n".join(lines) + "\n"


def build_authority_review_data(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    verified_only: bool = False,
    support_status: str | None = None,
    fit_kind: str | None = None,
) -> Dict[str, Any]:
    cases = _load_case_rows(root, branch=branch, case_id=case_id, trust=trust, warning_label=warning_label)
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"authority-review mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    review = _load_json(root / case["packagePath"] / "authority_review.json")
    authorities = review["authorities"]
    if support_status and support_status not in {"verified_quote", "paraphrase", "missing"}:
        raise ValueError("support-status must be one of: verified_quote, paraphrase, missing")
    if fit_kind and fit_kind not in {"direct", "analogical", "record_support"}:
        raise ValueError("fit must be one of: direct, analogical, record_support")
    if verified_only:
        support_status = "verified_quote"
    if support_status:
        authorities = [item for item in authorities if item["supportStatus"] == support_status]
    if fit_kind:
        authorities = [item for item in authorities if item.get("fitKind") == fit_kind]
    return {
        "caseId": review["caseId"],
        "branch": review["branch"],
        "verifiedOnly": verified_only,
        "supportStatus": support_status,
        "fitKind": fit_kind,
        "authorities": authorities,
    }


def build_authority_review_summary(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    verified_only: bool = False,
    support_status: str | None = None,
    fit_kind: str | None = None,
) -> Dict[str, Any]:
    payload = build_authority_review_data(
        root=root,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        verified_only=verified_only,
        support_status=support_status,
        fit_kind=fit_kind,
    )
    status_counts: Dict[str, int] = {}
    bucket_counts: Dict[str, int] = {}
    for authority in payload["authorities"]:
        status = authority["supportStatus"]
        status_counts[status] = status_counts.get(status, 0) + 1
        for bucket in authority.get("buckets", []):
            bucket_counts[bucket] = bucket_counts.get(bucket, 0) + 1
    return {
        "caseId": payload["caseId"],
        "branch": payload["branch"],
        "verifiedOnly": payload["verifiedOnly"],
        "supportStatus": payload["supportStatus"],
        "fitKind": payload["fitKind"],
        "authorityCount": len(payload["authorities"]),
        "statusCounts": dict(sorted(status_counts.items())),
        "bucketCounts": dict(sorted(bucket_counts.items())),
    }


def build_authority_research_note_data(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    source_verified_only: bool = False,
    source_normalized_only: bool = False,
    fit_kind: str | None = None,
) -> Dict[str, Any]:
    cases = _load_case_rows(root, branch=branch, case_id=case_id, trust=trust, warning_label=warning_label)
    if len(cases) != 1:
        available = ", ".join(case["caseId"] for case in _sort_cases(cases, "caseId")) or "none"
        raise ValueError(f"authority-research-note mode requires exactly one matching case, found {len(cases)}: {available}")
    case = cases[0]
    payload = _load_json(root / case["packagePath"] / "authority_research_note.json")
    entries = payload["entries"]
    if fit_kind and fit_kind not in {"direct", "analogical", "record_support"}:
        raise ValueError("fit must be one of: direct, analogical, record_support")
    if source_verified_only:
        entries = [entry for entry in entries if entry.get("sourceVerified")]
    if source_normalized_only:
        entries = [entry for entry in entries if entry.get("sourceNormalized")]
    if fit_kind:
        entries = [entry for entry in entries if entry.get("fitKind") == fit_kind]
    filtered = dict(payload)
    filtered["entryCount"] = len(entries)
    filtered["fitKind"] = fit_kind
    filtered["entries"] = entries
    return filtered


def render_authority_research_note(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    source_verified_only: bool = False,
    source_normalized_only: bool = False,
    fit_kind: str | None = None,
) -> str:
    payload = build_authority_research_note_data(
        root=root,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        source_verified_only=source_verified_only,
        source_normalized_only=source_normalized_only,
        fit_kind=fit_kind,
    )
    entries = payload["entries"]
    lines = [
        f"Case ID: {payload['caseId']}",
        f"Branch: {payload['branch']}",
        f"Authority Entries: {payload['entryCount']}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Source Verified Only: {'yes' if source_verified_only else 'no'}",
        f"Source Normalized Only: {'yes' if source_normalized_only else 'no'}",
        f"Fit Kind: {payload.get('fitKind') or 'any'}",
        "",
        "Authority Research Note:",
    ]
    for authority in entries:
        lines.append(
            f"- {authority['id']} [{authority['excerptKind']}] "
            f"{authority['label']} ({authority.get('court') or 'none'}, {authority.get('year') or 'none'}, {authority.get('pincite') or 'none'})"
        )
        lines.append(f"  fit: {authority.get('fitKind') or 'none'}")
        lines.append(f"  support: {authority.get('supportStatus') or 'none'}")
        lines.append(f"  source verified: {'yes' if authority.get('sourceVerified') else 'no'}")
        lines.append(f"  source normalized: {'yes' if authority.get('sourceNormalized') else 'no'}")
        lines.append(f"  source ref: {authority.get('sourceReference') or 'none'}")
        lines.append(f"  source: {authority.get('sourceUrl') or 'none'}")
        lines.append(f"  proposition: {authority.get('proposition') or 'none'}")
    return "\n".join(lines) + "\n"


def build_authority_summary_matrix(
    root: Path = ROOT,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    support_status: str | None = None,
    fit_kind: str | None = None,
    verified_only: bool = False,
    sort_key: str = "caseId",
) -> Dict[str, Any]:
    cases = _load_case_rows(root, branch=branch, trust=trust, warning_label=warning_label)
    rows = []
    for case in _sort_cases(cases, sort_key):
        summary = build_authority_review_summary(
            root=root,
            case_id=case["caseId"],
            trust=trust,
            warning_label=warning_label,
            verified_only=verified_only,
            support_status=support_status,
            fit_kind=fit_kind,
        )
        rows.append(summary)
    return {
        "verifiedOnly": verified_only,
        "supportStatus": "verified_quote" if verified_only else support_status,
        "fitKind": fit_kind,
        "cases": rows,
    }


def render_authority_review_summary(
    root: Path = ROOT,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    verified_only: bool = False,
    support_status: str | None = None,
    fit_kind: str | None = None,
) -> str:
    summary = build_authority_review_summary(
        root=root,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        verified_only=verified_only,
        support_status=support_status,
        fit_kind=fit_kind,
    )
    lines = [
        f"Case ID: {summary['caseId']}",
        f"Branch: {summary['branch']}",
        f"Verified Only: {'yes' if summary['verifiedOnly'] else 'no'}",
        f"Support Status: {summary['supportStatus'] or 'any'}",
        f"Fit Kind: {summary['fitKind'] or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Authority Count: {summary['authorityCount']}",
        "",
        "Status Counts:",
    ]
    if summary["statusCounts"]:
        for status, count in summary["statusCounts"].items():
            lines.append(f"- {status}: {count}")
    else:
        lines.append("- none")
    lines.extend(["", "Bucket Counts:"])
    if summary["bucketCounts"]:
        for bucket, count in summary["bucketCounts"].items():
            lines.append(f"- {bucket}: {count}")
    else:
        lines.append("- none")
    return "\n".join(lines) + "\n"


def render_authority_summary_matrix(
    root: Path = ROOT,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    support_status: str | None = None,
    fit_kind: str | None = None,
    verified_only: bool = False,
    sort_key: str = "caseId",
) -> str:
    matrix = build_authority_summary_matrix(
        root=root,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        support_status=support_status,
        fit_kind=fit_kind,
        verified_only=verified_only,
        sort_key=sort_key,
    )
    lines = [
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Kind: {fit_kind or 'any'}",
        "",
        "Case ID | Branch | Authorities | Verified Only | Support Status | Status Counts | Bucket Counts",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in matrix["cases"]:
        status_counts = ", ".join(f"{k}={v}" for k, v in case["statusCounts"].items()) or "none"
        bucket_counts = ", ".join(f"{k}={v}" for k, v in case["bucketCounts"].items()) or "none"
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    str(case["authorityCount"]),
                    "yes" if case["verifiedOnly"] else "no",
                    case["supportStatus"] or "any",
                    status_counts,
                    bucket_counts,
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_authority_summary_matrix_markdown(
    root: Path = ROOT,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    support_status: str | None = None,
    fit_kind: str | None = None,
    verified_only: bool = False,
    sort_key: str = "caseId",
) -> str:
    matrix = render_authority_summary_matrix(
        root=root,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
        support_status=support_status,
        fit_kind=fit_kind,
        verified_only=verified_only,
        sort_key=sort_key,
    ).rstrip()
    lines = [
        "# Authority Summary Matrix",
        "",
        f"Verified Only: `{'yes' if verified_only else 'no'}`",
        f"Support Status: `{('verified_quote' if verified_only else support_status) or 'any'}`",
        f"Fit Kind: `{fit_kind or 'any'}`",
        f"Warning Label Filter: `{warning_label or 'any'}`",
        "",
        matrix,
        "",
    ]
    return "\n".join(lines)


def build_source_metadata_matrix_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "source_metadata_matrix.json")
    cases = payload["cases"]
    if trust or warning_label:
        allowed = {
            case["caseId"]
            for case in _load_case_rows(root=root, trust=trust, warning_label=warning_label)
        }
        cases = [case for case in cases if case["caseId"] in allowed]
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(cases),
            "authorityCount": sum(case["authorityCount"] for case in cases),
            "sourceVerifiedCount": sum(case["sourceVerifiedCount"] for case in cases),
            "sourceNormalizedCount": sum(case["sourceNormalizedCount"] for case in cases),
        },
        "cases": cases,
    }


def render_source_metadata_matrix(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
) -> str:
    payload = build_source_metadata_matrix_data(root=root, trust=trust, warning_label=warning_label)
    lines = [
        "Source Metadata Matrix",
        "",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Authority Count: {payload['summary']['authorityCount']}",
        f"Source Verified Count: {payload['summary']['sourceVerifiedCount']}",
        f"Source Normalized Count: {payload['summary']['sourceNormalizedCount']}",
        "",
        "Case ID | Branch | Authorities | Verified | Normalized | Unnormalized IDs",
        "--- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    str(case["authorityCount"]),
                    str(case["sourceVerifiedCount"]),
                    str(case["sourceNormalizedCount"]),
                    ", ".join(case["unnormalizedAuthorityIds"]) or "none",
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_fit_matrix_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "fit_matrix.json")
    cases = payload["cases"]
    if fit_kind and fit_kind not in {"direct", "analogical", "record_support"}:
        raise ValueError("fit must be one of: direct, analogical, record_support")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    if trust or warning_label or fit_finding:
        allowed = {
            case["caseId"]
            for case in _load_case_rows(
                root=root,
                trust=trust,
                warning_label=warning_label,
                fit_finding=fit_finding,
            )
        }
        cases = [case for case in cases if case["caseId"] in allowed]
    if fit_kind == "direct":
        cases = [case for case in cases if case["directCount"] > 0]
    elif fit_kind == "analogical":
        cases = [case for case in cases if case["analogicalCount"] > 0]
    elif fit_kind == "record_support":
        cases = [case for case in cases if case["recordSupportCount"] > 0]
    return {
        "generatedAt": payload["generatedAt"],
        "summary": {
            "caseCount": len(cases),
            "authorityCount": sum(case["authorityCount"] for case in cases),
            "directCount": sum(case["directCount"] for case in cases),
            "analogicalCount": sum(case["analogicalCount"] for case in cases),
            "recordSupportCount": sum(case["recordSupportCount"] for case in cases),
        },
        "cases": cases,
    }


def render_fit_matrix(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
) -> str:
    payload = build_fit_matrix_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        fit_kind=fit_kind,
        fit_finding=fit_finding,
    )
    lines = [
        "Fit Matrix",
        "",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Filter: {fit_kind or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Authority Count: {payload['summary']['authorityCount']}",
        f"Direct Count: {payload['summary']['directCount']}",
        f"Analogical Count: {payload['summary']['analogicalCount']}",
        f"Record-Support Count: {payload['summary']['recordSupportCount']}",
        "",
        "Case ID | Branch | Authorities | Direct | Analogical | Record Support | Fit Status",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    str(case["authorityCount"]),
                    str(case["directCount"]),
                    str(case["analogicalCount"]),
                    str(case["recordSupportCount"]),
                    case["fitStatus"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_fit_summary_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if sort_key not in {"caseId", "branch", "warningCount"}:
        raise ValueError("fit-summary sort must be one of: caseId, branch, warningCount")
    if top_n is not None and top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    payload = _load_json(root / "outputs" / "fit_summary.json")
    cases = payload["cases"]
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    if trust or warning_label or fit_finding:
        allowed = {
            case["caseId"]
            for case in _load_case_rows(
                root=root,
                trust=trust,
                warning_label=warning_label,
                fit_finding=fit_finding,
            )
        }
        cases = [case for case in cases if case["caseId"] in allowed]
    if fit_kind and fit_kind not in {"direct", "analogical", "record_support"}:
        raise ValueError("fit must be one of: direct, analogical, record_support")
    if fit_kind == "direct":
        cases = [case for case in cases if case["directCount"] > 0]
    elif fit_kind == "analogical":
        cases = [case for case in cases if case["analogicalCount"] > 0]
    elif fit_kind == "record_support":
        cases = [case for case in cases if case["recordSupportCount"] > 0]
    cases = _sort_cases(cases, "warningCount" if sort_key == "warningCount" else sort_key)
    if top_n is not None:
        cases = cases[:top_n]
    single_case_guide = None
    if len(cases) == 1:
        case_row = next((row for row in _load_case_rows(root=root) if row["caseId"] == cases[0]["caseId"]), None)
        if case_row:
            single_case_guide = {
                "caseId": case_row["caseId"],
                "recommendedFirstStop": case_row["recommendedFirstStop"],
                "whyOpenThis": case_row["whyOpenThis"],
            }
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(cases),
            "authorityCount": sum(
                case["directCount"] + case["analogicalCount"] + case["recordSupportCount"]
                for case in cases
            ),
            "directCount": sum(case["directCount"] for case in cases),
            "analogicalCount": sum(case["analogicalCount"] for case in cases),
            "recordSupportCount": sum(case["recordSupportCount"] for case in cases),
        },
        "singleCaseGuide": single_case_guide,
        "cases": cases,
    }


def render_fit_summary(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> str:
    payload = build_fit_summary_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        fit_kind=fit_kind,
        fit_finding=fit_finding,
        sort_key=sort_key,
        top_n=top_n,
    )
    ranked = sort_key == "warningCount"
    lines = [
        "Fit Summary",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Filter: {fit_kind or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        f"Sort: {sort_key}",
        f"Top N: {top_n if top_n is not None else 'all'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Authority Count: {payload['summary']['authorityCount']}",
        f"Direct Count: {payload['summary']['directCount']}",
        f"Analogical Count: {payload['summary']['analogicalCount']}",
        f"Record-Support Count: {payload['summary']['recordSupportCount']}",
        "",
        "Rank | Case ID | Branch | Direct | Analogical | Record Support | Fit Status"
        if ranked
        else "Case ID | Branch | Direct | Analogical | Record Support | Fit Status",
        "--- | --- | --- | --- | --- | --- | ---"
        if ranked
        else "--- | --- | --- | --- | --- | ---",
    ]
    for index, case in enumerate(payload["cases"], start=1):
        row = [
            case["caseId"],
            case["branch"],
            str(case["directCount"]),
            str(case["analogicalCount"]),
            str(case["recordSupportCount"]),
            case["fitStatus"],
        ]
        if ranked:
            row.insert(0, str(index))
        lines.append(" | ".join(row))
    if payload["singleCaseGuide"]:
        guide = payload["singleCaseGuide"]
        lines.extend(
            [
                "",
                "Single-Case Guide",
                f"- Case ID: {guide['caseId']}",
                f"- Recommended First Stop: {guide['recommendedFirstStop']}",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_fit_findings_data(
    root: Path = ROOT,
    severity: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
) -> Dict[str, Any]:
    report = _load_json(root / "outputs" / "fit_findings.json")
    findings = report["findings"]
    if severity and severity not in {"info", "warning"}:
        raise ValueError("severity must be one of: info, warning")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    if severity:
        findings = [item for item in findings if item["severity"] == severity]
    if trust or warning_label or fit_finding or case_id or branch:
        allowed = {
            case["caseId"]
            for case in _load_case_rows(
                root=root,
                branch=branch,
                case_id=case_id,
                trust=trust,
                warning_label=warning_label,
                fit_finding=fit_finding,
            )
        }
        findings = [item for item in findings if item["caseId"] in allowed]
    return {
        "generatedAt": report["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(findings),
            "directOnlyCases": sum(1 for item in findings if item["title"] == "Direct-fit authority baseline"),
            "analogicalCases": sum(1 for item in findings if item["title"] == "Analogical fit posture"),
            "recordSupportCases": sum(1 for item in findings if item["title"] == "Record-support-heavy fit posture"),
        },
        "findings": findings,
    }


def build_fit_findings_summary_data(
    root: Path = ROOT,
    severity: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "fit_findings_summary.json")
    cases = payload["cases"]
    if severity and severity not in {"info", "warning"}:
        raise ValueError("severity must be one of: info, warning")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    if severity:
        cases = [item for item in cases if item["severity"] == severity]
    if trust or warning_label or fit_finding or case_id or branch:
        allowed = {
            case["caseId"]
            for case in _load_case_rows(
                root=root,
                branch=branch,
                case_id=case_id,
                trust=trust,
                warning_label=warning_label,
                fit_finding=fit_finding,
            )
        }
        cases = [item for item in cases if item["caseId"] in allowed]
    single_case_guide = None
    if len(cases) == 1:
        case_row = next((row for row in _load_case_rows(root=root) if row["caseId"] == cases[0]["caseId"]), None)
        if case_row:
            single_case_guide = {
                "caseId": case_row["caseId"],
                "recommendedFirstStop": case_row["recommendedFirstStop"],
                "whyOpenThis": case_row["whyOpenThis"],
            }
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(cases),
            "directOnlyCases": sum(1 for item in cases if item["title"] == "Direct-fit authority baseline"),
            "analogicalCases": sum(1 for item in cases if item["title"] == "Analogical fit posture"),
            "recordSupportCases": sum(1 for item in cases if item["title"] == "Record-support-heavy fit posture"),
            "severityCounts": _count_labels(cases, "severity"),
        },
        "singleCaseGuide": single_case_guide,
        "cases": cases,
    }


def render_fit_findings(
    root: Path = ROOT,
    severity: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
) -> str:
    payload = build_fit_findings_data(
        root=root,
        severity=severity,
        trust=trust,
        warning_label=warning_label,
        fit_finding=fit_finding,
        case_id=case_id,
        branch=branch,
    )
    lines = [
        "Fit Findings",
        f"Generated At: {payload['generatedAt']}",
        f"Severity Filter: {severity or 'any'}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Direct-Only Cases: {payload['summary']['directOnlyCases']}",
        f"Analogical Cases: {payload['summary']['analogicalCases']}",
        f"Record-Support Cases: {payload['summary']['recordSupportCases']}",
        "",
    ]
    for finding in payload["findings"]:
        lines.extend(
            [
                f"{finding['caseId']} [{finding['severity']}]",
                f"- Branch: {finding['branch']}",
                f"- Title: {finding['title']}",
                f"- Detail: {finding['detail']}",
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def render_fit_findings_summary(
    root: Path = ROOT,
    severity: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
) -> str:
    payload = build_fit_findings_summary_data(
        root=root,
        severity=severity,
        trust=trust,
        warning_label=warning_label,
        fit_finding=fit_finding,
        case_id=case_id,
        branch=branch,
    )
    lines = [
        "Fit Findings Summary",
        f"Generated At: {payload['generatedAt']}",
        f"Severity Filter: {severity or 'any'}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Direct-Only Cases: {payload['summary']['directOnlyCases']}",
        f"Analogical Cases: {payload['summary']['analogicalCases']}",
        f"Record-Support Cases: {payload['summary']['recordSupportCases']}",
        f"Severity Counts: {payload['summary']['severityCounts']}",
        "",
        "Case ID | Branch | Severity | Title",
        "--- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(" | ".join([case["caseId"], case["branch"], case["severity"], case["title"]]))
    if payload["singleCaseGuide"]:
        guide = payload["singleCaseGuide"]
        lines.extend(
            [
                "",
                "Single-Case Guide",
                f"- Case ID: {guide['caseId']}",
                f"- Recommended First Stop: {guide['recommendedFirstStop']}",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_source_findings_data(
    root: Path = ROOT,
    severity: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
) -> Dict[str, Any]:
    report = _load_json(root / "outputs" / "source_findings.json")
    findings = report["findings"]
    if severity and severity not in {"info", "warning"}:
        raise ValueError("severity must be one of: info, warning")
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if severity:
        findings = [item for item in findings if item["severity"] == severity]
    if case_id:
        findings = [item for item in findings if item["caseId"] == case_id]
    if branch:
        findings = [item for item in findings if item["branch"] == branch]
    if trust or warning_label:
        allowed_case_ids = {
            case["caseId"]
            for case in _load_case_rows(root=root, branch=branch, trust=trust, warning_label=warning_label)
        }
        findings = [item for item in findings if item["caseId"] in allowed_case_ids]
    return {
        "generatedAt": report["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": report["summary"],
        "findings": findings,
    }


def render_source_findings(
    root: Path = ROOT,
    severity: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
) -> str:
    payload = build_source_findings_data(
        root=root,
        severity=severity,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
    )
    lines = [
        "Source Findings",
        f"Generated At: {payload['generatedAt']}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Fully Normalized Cases: {payload['summary']['fullyNormalizedCases']}",
        f"Partially Normalized Cases: {payload['summary']['partiallyNormalizedCases']}",
        f"Severity Filter: {severity or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
        "Findings:",
    ]
    if not payload["findings"]:
        lines.append("- none")
    else:
        for finding in payload["findings"]:
            lines.append(
                f"- {finding['caseId']} [{finding['severity']}] {finding['title']} ({finding['branch']})"
            )
            lines.append(f"  {finding['detail']}")
    return "\n".join(lines) + "\n"


def build_refresh_state_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / ".refresh_state.json")
    elapsed_seconds = _compute_elapsed_seconds(payload.get("startedAt"), payload.get("completedAt"))
    return {
        **payload,
        "elapsedSeconds": elapsed_seconds,
        "elapsedHuman": _format_elapsed_duration(elapsed_seconds),
    }


def wait_for_refresh_complete(
    root: Path = ROOT,
    timeout_seconds: float = 30.0,
    poll_interval_seconds: float = 0.1,
) -> Dict[str, Any]:
    if timeout_seconds < 0:
        raise ValueError("wait-timeout must be zero or greater")
    if poll_interval_seconds <= 0:
        raise ValueError("wait-interval must be greater than zero")
    deadline = time.monotonic() + timeout_seconds
    payload = build_refresh_state_data(root=root)
    while payload["status"] != "complete":
        if time.monotonic() >= deadline:
            raise ValueError(
                f"refresh did not complete within {timeout_seconds:.3f} seconds; current status: {payload['status']}"
            )
        time.sleep(min(poll_interval_seconds, max(deadline - time.monotonic(), 0)))
        payload = build_refresh_state_data(root=root)
    return payload


def fail_if_refresh_running(root: Path = ROOT) -> Dict[str, Any]:
    payload = build_refresh_state_data(root=root)
    if payload["status"] == "running":
        raise ValueError(
            "refresh is currently running; rerun later or use --wait-for-refresh-complete"
        )
    return payload


def build_refresh_runtime_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = build_refresh_state_data(root=root)
    return {
        "status": payload["status"],
        "running": payload["status"] == "running",
        "startedAt": payload["startedAt"],
        "completedAt": payload["completedAt"],
        "elapsedSeconds": payload["elapsedSeconds"],
        "elapsedHuman": payload["elapsedHuman"],
    }


def render_refresh_state(root: Path = ROOT) -> str:
    payload = build_refresh_state_data(root=root)
    lines = [
        "Refresh State",
        f"Status: {payload['status']}",
        f"Started At: {payload['startedAt']}",
        f"Completed At: {payload['completedAt'] or 'pending'}",
        f"Elapsed Seconds: {payload['elapsedSeconds'] if payload['elapsedSeconds'] is not None else 'pending'}",
        f"Elapsed: {payload['elapsedHuman'] or 'pending'}",
    ]
    return "\n".join(lines) + "\n"


def prepend_refresh_warning(text: str, root: Path = ROOT) -> str:
    try:
        payload = build_refresh_state_data(root=root)
    except (FileNotFoundError, json.JSONDecodeError):
        return text
    if payload["status"] != "running":
        return text
    lines = [
        "Refresh Warning",
        "Outputs are currently being regenerated, so this view may reflect a mid-refresh state.",
        f"Started At: {payload['startedAt']}",
        f"Elapsed: {payload['elapsedHuman'] or 'pending'}",
        "",
    ]
    return "\n".join(lines) + "\n" + text


def build_authority_findings_data(
    root: Path = ROOT,
    severity: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
) -> Dict[str, Any]:
    report = _load_json(root / "outputs" / "authority_findings.json")
    findings = report["findings"]
    if severity and severity not in {"info", "warning"}:
        raise ValueError("severity must be one of: info, warning")
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if severity:
        findings = [item for item in findings if item["severity"] == severity]
    if case_id:
        findings = [item for item in findings if item["caseId"] == case_id]
    if branch:
        findings = [item for item in findings if item["branch"] == branch]
    if trust:
        allowed_case_ids = {case["caseId"] for case in _load_case_rows(root, branch=branch, trust=trust)}
        findings = [item for item in findings if item["caseId"] in allowed_case_ids]
    if warning_label:
        findings = [item for item in findings if item["caseId"] in {
            case["caseId"] for case in build_warning_summary_data(root=root, branch=branch, trust=warning_label)["cases"]
        }]
    return {
        "generatedAt": report["generatedAt"],
        "summary": report["summary"],
        "findings": findings,
    }


def render_authority_findings(
    root: Path = ROOT,
    severity: str | None = None,
    case_id: str | None = None,
    branch: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
) -> str:
    payload = build_authority_findings_data(
        root=root,
        severity=severity,
        case_id=case_id,
        branch=branch,
        trust=trust,
        warning_label=warning_label,
    )
    lines = [
        "Authority Findings",
        f"Generated At: {payload['generatedAt']}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Fully Verified Cases: {payload['summary']['fullyVerifiedCases']}",
        f"Mixed Support Cases: {payload['summary']['mixedSupportCases']}",
        f"Paraphrase-Heavy Cases: {payload['summary']['paraphraseHeavyCases']}",
        f"Severity Filter: {severity or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
        "Findings:",
    ]
    if not payload["findings"]:
        lines.append("- none")
    else:
        for finding in payload["findings"]:
            lines.append(
                f"- {finding['caseId']} [{finding['severity']}] {finding['title']} ({finding['branch']})"
            )
            lines.append(f"  {finding['detail']}")
    return "\n".join(lines) + "\n"


def build_trust_matrix_data(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    payload = _load_json(root / "outputs" / "trust_matrix.json")
    cases = payload["cases"]
    if branch:
        cases = [item for item in cases if item["branch"] == branch]
    if case_id:
        cases = [item for item in cases if item["caseId"] == case_id]
    if trust:
        cases = [item for item in cases if item["authorityTrust"] == trust]
    if warning_label:
        cases = [item for item in cases if item["authorityTrust"] == warning_label]
    if warned_only:
        cases = [item for item in cases if item["hasEntryWarnings"]]
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "cases": _sort_cases(cases, sort_key),
    }


def render_trust_matrix(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
) -> str:
    payload = build_trust_matrix_data(
        root=root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        warned_only=warned_only,
        sort_key=sort_key,
    )
    lines = [
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
        "Case ID | Branch | Outcome | Trust | WarnLabels | Primary | Entry Warnings | Warning Count | Package",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        warning_labels = case["authorityTrust"] if case["hasEntryWarnings"] else "none"
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["activeOutcome"],
                    case["authorityTrust"],
                    warning_labels,
                    case["primaryKind"],
                    "yes" if case["hasEntryWarnings"] else "no",
                    str(case["warningEntryCount"]),
                    case["packagePath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_warning_summary_data(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "caseId",
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    payload = build_trust_matrix_data(
        root=root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warned_only=True,
        sort_key=sort_key,
    )
    if warning_label:
        payload["cases"] = [case for case in payload["cases"] if case["authorityTrust"] == warning_label]
    warning_counts: Dict[str, int] = {}
    cases = []
    for case in payload["cases"]:
        label = case["authorityTrust"]
        warning_counts[label] = warning_counts.get(label, 0) + 1
        cases.append(
            {
                "caseId": case["caseId"],
                "branch": case["branch"],
                "activeOutcome": case["activeOutcome"],
                "authorityTrust": case["authorityTrust"],
                "primaryKind": case["primaryKind"],
                "warningEntryCount": case["warningEntryCount"],
                "warningCounts": {label: case["warningEntryCount"]},
                "packagePath": case["packagePath"],
            }
        )
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(payload["cases"]),
            "warnedCaseCount": len(cases),
            "warningCounts": dict(sorted(warning_counts.items())),
        },
        "cases": cases,
    }


def render_warning_summary(
    root: Path = ROOT,
    branch: str | None = None,
    case_id: str | None = None,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "caseId",
) -> str:
    payload = build_warning_summary_data(
        root=root,
        branch=branch,
        case_id=case_id,
        trust=trust,
        warning_label=warning_label,
        sort_key=sort_key,
    )
    lines = [
        "Warning Summary",
        f"Generated At: {payload['generatedAt']}",
        f"Warned Cases: {payload['summary']['warnedCaseCount']}",
        f"Warning Labels: {payload['summary']['warningCounts'] or {}}",
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
        "Case ID | Branch | Outcome | Trust | Primary | Warning Count | Package",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["activeOutcome"],
                    case["authorityTrust"],
                    case["primaryKind"],
                    str(case["warningEntryCount"]),
                    case["packagePath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_warning_label_matrix_data(
    root: Path = ROOT,
    warning_label: str | None = None,
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    payload = _load_json(root / "outputs" / "warning_label_matrix.json")
    if warning_label:
        return {
            "generatedAt": payload["generatedAt"],
            "refreshRuntime": build_refresh_runtime_data(root),
            "labels": {warning_label: payload["labels"][warning_label]},
        }
    payload["refreshRuntime"] = build_refresh_runtime_data(root)
    return payload


def render_warning_label_matrix(
    root: Path = ROOT,
    warning_label: str | None = None,
) -> str:
    payload = build_warning_label_matrix_data(root=root, warning_label=warning_label)
    lines = [
        "Warning Label Matrix",
        f"Generated At: {payload['generatedAt']}",
        f"Warning Label Filter: {warning_label or 'any'}",
        "",
    ]
    for label, label_payload in payload["labels"].items():
        lines.extend(
            [
                f"{label}:",
                f"  Warned Cases: {label_payload['summary']['warnedCaseCount']}",
                f"  Warning Counts: {label_payload['summary']['warningCounts'] or {}}",
                "  Case ID | Branch | Outcome | Trust | Primary | Warning Count | Package",
                "  --- | --- | --- | --- | --- | --- | ---",
            ]
        )
        for case in label_payload["cases"]:
            lines.append(
                "  "
                + " | ".join(
                    [
                        case["caseId"],
                        case["branch"],
                        case["activeOutcome"],
                        case["authorityTrust"],
                        case["primaryKind"],
                        str(case["warningEntryCount"]),
                        case["packagePath"],
                    ]
                )
            )
        lines.append("")
    return "\n".join(lines)


def build_warning_entry_matrix_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_kind: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if top_n is not None and top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    payload = _load_json(root / "outputs" / "warning_entry_matrix.json")
    cases = payload["cases"]
    if trust:
        cases = [case for case in cases if case["authorityTrust"] == trust]
    if warning_label:
        cases = [case for case in cases if case["warningLabel"] == warning_label]
    if warned_kind:
        cases = [case for case in cases if warned_kind in case["warnedKinds"]]
    sorted_cases = _sort_cases(cases, sort_key)
    if top_n is not None:
        sorted_cases = sorted_cases[:top_n]
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "cases": sorted_cases,
    }


def render_warning_entry_matrix(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    warned_kind: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> str:
    payload = build_warning_entry_matrix_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        warned_kind=warned_kind,
        sort_key=sort_key,
        top_n=top_n,
    )
    lines = [
        "Warning Entry Matrix",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Warned Kind Filter: {warned_kind or 'any'}",
        f"Sort: {sort_key}",
        f"Top N: {top_n if top_n is not None else 'all'}",
        "",
        "Case ID | Branch | Trust | Warning Label | Warning Count | Warned Kinds | Package",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["authorityTrust"],
                    case["warningLabel"],
                    str(case["warningEntryCount"]),
                    ", ".join(case["warnedKinds"]),
                    case["packagePath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_warning_kind_matrix_data(
    root: Path = ROOT,
    trust: str | None = None,
    warned_kind: str | None = None,
    sort_key: str = "kind",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if top_n is not None and top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    payload = _load_json(root / "outputs" / "warning_kind_matrix.json")
    kinds = []
    for item in payload["kinds"]:
        cases = item["cases"]
        if trust:
            cases = [case for case in cases if case["authorityTrust"] == trust]
        if not cases:
            continue
        kinds.append(
            {
                "kind": item["kind"],
                "warningCaseCount": len(cases),
                "warningLabels": _count_labels(cases, "warningLabel"),
                "cases": cases,
            }
        )
    if warned_kind:
        kinds = [item for item in kinds if item["kind"] == warned_kind]
    sorted_kinds = _sort_kind_rows(kinds, sort_key)
    if top_n is not None:
        sorted_kinds = sorted_kinds[:top_n]
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "kindCount": len(sorted_kinds),
            "caseCount": len({case["caseId"] for item in sorted_kinds for case in item["cases"]}),
        },
        "kinds": sorted_kinds,
    }


def render_warning_kind_matrix(
    root: Path = ROOT,
    trust: str | None = None,
    warned_kind: str | None = None,
    sort_key: str = "kind",
    top_n: int | None = None,
) -> str:
    payload = build_warning_kind_matrix_data(
        root=root,
        trust=trust,
        warned_kind=warned_kind,
        sort_key=sort_key,
        top_n=top_n,
    )
    lines = [
        "Warning Kind Matrix",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warned Kind Filter: {warned_kind or 'any'}",
        f"Sort: {sort_key}",
        f"Top N: {top_n if top_n is not None else 'all'}",
        f"Kind Count: {payload['summary']['kindCount']}",
        f"Case Count: {payload['summary']['caseCount']}",
        "",
        "Kind | Warning Cases | Warning Labels | Case IDs",
        "--- | --- | --- | ---",
    ]
    for item in payload["kinds"]:
        lines.append(
            " | ".join(
                [
                    item["kind"],
                    str(item["warningCaseCount"]),
                    str(item["warningLabels"]),
                    ", ".join(case["caseId"] for case in item["cases"]),
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_warning_entry_summary_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if sort_key not in {"caseId", "branch", "warningCount"}:
        raise ValueError("warning-entry-summary sort must be one of: caseId, branch, warningCount")
    if top_n is not None and top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    payload = _load_json(root / "outputs" / "warning_entry_summary.json")
    cases = payload["cases"]
    if trust:
        cases = [case for case in cases if case["authorityTrust"] == trust]
    if warning_label:
        cases = [case for case in cases if case["warningLabel"] == warning_label]
    cases = _sort_cases(cases, sort_key)
    if top_n is not None:
        cases = cases[:top_n]
    single_case_guide = None
    if len(cases) == 1:
        case_row = next((row for row in _load_case_rows(root=root) if row["caseId"] == cases[0]["caseId"]), None)
        if case_row:
            single_case_guide = {
                "caseId": case_row["caseId"],
                "recommendedFirstStop": case_row["recommendedFirstStop"],
                "whyOpenThis": case_row["whyOpenThis"],
            }
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "caseCount": len(cases),
            "warningLabels": _count_labels(cases, "warningLabel"),
        },
        "singleCaseGuide": single_case_guide,
        "cases": cases,
    }


def render_warning_entry_summary(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "caseId",
    top_n: int | None = None,
) -> str:
    payload = build_warning_entry_summary_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        sort_key=sort_key,
        top_n=top_n,
    )
    ranked = sort_key == "warningCount"
    lines = [
        "Warning Entry Summary",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Sort: {sort_key}",
        f"Top N: {top_n if top_n is not None else 'all'}",
        f"Case Count: {payload['summary']['caseCount']}",
        f"Warning Labels: {payload['summary']['warningLabels']}",
        "",
        "Rank | Case ID | Branch | Trust | Warning Label | Warning Count"
        if ranked
        else "Case ID | Branch | Trust | Warning Label | Warning Count",
        "--- | --- | --- | --- | --- | ---"
        if ranked
        else "--- | --- | --- | --- | ---",
    ]
    for index, case in enumerate(payload["cases"], start=1):
        row = [
            case["caseId"],
            case["branch"],
            case["authorityTrust"],
            case["warningLabel"],
            str(case["warningEntryCount"]),
        ]
        if ranked:
            row.insert(0, str(index))
        lines.append(" | ".join(row))
    if payload["singleCaseGuide"]:
        guide = payload["singleCaseGuide"]
        lines.extend(
            [
                "",
                "Single-Case Guide",
                f"- Case ID: {guide['caseId']}",
                f"- Recommended First Stop: {guide['recommendedFirstStop']}",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_warning_kind_summary_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "kind",
    top_n: int | None = None,
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if sort_key not in {"kind", "warningCaseCount"}:
        raise ValueError("warning-kind-summary sort must be one of: kind, warningCaseCount")
    if top_n is not None and top_n < 1:
        raise ValueError("top-n mode requires a positive integer")
    payload = _load_json(root / "outputs" / "warning_kind_summary.json")
    raw_matrix = _load_json(root / "outputs" / "warning_kind_matrix.json")
    kinds = []
    case_ids = set()
    for item in raw_matrix["kinds"]:
        if warning_label:
            label_count = item["warningLabels"].get(warning_label, 0)
            if not label_count:
                continue
        cases = item.get("cases")
        if not cases:
            # fallback to summary artifact rows if case lists are not present
            cases = []
        if trust:
            cases = [case for case in cases if case["authorityTrust"] == trust]
        if warning_label:
            cases = [case for case in cases if case["warningLabel"] == warning_label]
        if trust or warning_label:
            if not cases:
                continue
            warning_labels = _count_labels(cases, "warningLabel")
            warning_case_count = len(cases)
        else:
            warning_labels = item["warningLabels"]
            warning_case_count = item["warningCaseCount"]
        for case in cases:
            case_ids.add(case["caseId"])
        kinds.append(
            {
                "kind": item["kind"],
                "warningCaseCount": warning_case_count,
                "warningLabels": warning_labels,
            }
        )
    if not (trust or warning_label):
        kinds = payload["kinds"]
        case_count = payload["summary"]["caseCount"]
        single_case_guide = payload.get("singleCaseGuide")
    else:
        kinds = _sort_kind_rows(kinds, sort_key)
        case_count = len(case_ids)
        single_case_guide = None
    if not (trust or warning_label):
        kinds = _sort_kind_rows(kinds, sort_key)
    if top_n is not None:
        kinds = kinds[:top_n]
    selected_kind_names = {item["kind"] for item in kinds}
    selected_case_ids = {
        case["caseId"]
        for item in raw_matrix["kinds"]
        if item["kind"] in selected_kind_names
        for case in item.get("cases", [])
        if (not trust or case["authorityTrust"] == trust)
        and (not warning_label or case["warningLabel"] == warning_label)
    }
    if len(selected_case_ids) == 1:
        case_id = next(iter(selected_case_ids))
        case_row = next((row for row in _load_case_rows(root=root) if row["caseId"] == case_id), None)
        if case_row:
            single_case_guide = {
                "caseId": case_row["caseId"],
                "recommendedFirstStop": case_row["recommendedFirstStop"],
                "whyOpenThis": case_row["whyOpenThis"],
            }
    else:
        single_case_guide = None
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "summary": {
            "kindCount": len(kinds),
            "caseCount": case_count,
        },
        "singleCaseGuide": single_case_guide,
        "kinds": kinds,
    }


def render_warning_kind_summary(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    sort_key: str = "kind",
    top_n: int | None = None,
) -> str:
    payload = build_warning_kind_summary_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        sort_key=sort_key,
        top_n=top_n,
    )
    ranked = sort_key == "warningCaseCount"
    lines = [
        "Warning Kind Summary",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Sort: {sort_key}",
        f"Top N: {top_n if top_n is not None else 'all'}",
        f"Kind Count: {payload['summary']['kindCount']}",
        f"Case Count: {payload['summary']['caseCount']}",
        "",
        "Rank | Kind | Warning Cases | Warning Labels"
        if ranked
        else "Kind | Warning Cases | Warning Labels",
        "--- | --- | --- | ---"
        if ranked
        else "--- | --- | ---",
    ]
    for index, item in enumerate(payload["kinds"], start=1):
        row = [
            item["kind"],
            str(item["warningCaseCount"]),
            str(item["warningLabels"]),
        ]
        if ranked:
            row.insert(0, str(index))
        lines.append(" | ".join(row))
    if payload["singleCaseGuide"]:
        guide = payload["singleCaseGuide"]
        lines.extend(
            [
                "",
                "Single-Case Guide",
                f"- Case ID: {guide['caseId']}",
                f"- Recommended First Stop: {guide['recommendedFirstStop']}",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_summary_index_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "summary_index.json")
    payload["refreshRuntime"] = build_refresh_runtime_data(root)
    return payload


def render_summary_index(root: Path = ROOT) -> str:
    payload = build_summary_index_data(root=root)
    lines = [
        "Summary Index",
        f"Generated At: {payload['generatedAt']}",
        "",
        f"Recommended First Stop: {payload['recommendedFirstStop']}",
        f"Why Open This: {payload['whyOpenThis']}",
        f"Refresh Runtime: {payload['refreshRuntime']['status']} ({payload['refreshRuntime']['elapsedHuman'] or 'pending'})",
        "",
        "Priority | Kind | JSON | Markdown | Why Open This | Description",
        "--- | --- | --- | --- | --- | ---",
    ]
    for entry in payload["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["whyOpenThis"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_fit_index_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "fit_index.json")
    payload["refreshRuntime"] = build_refresh_runtime_data(root)
    return payload


def render_fit_index(root: Path = ROOT) -> str:
    payload = build_fit_index_data(root=root)
    lines = [
        "Fit Index",
        f"Generated At: {payload['generatedAt']}",
        "",
        f"Recommended First Stop: {payload['recommendedFirstStop']}",
        f"Why Open This: {payload['whyOpenThis']}",
        f"Refresh Runtime: {payload['refreshRuntime']['status']} ({payload['refreshRuntime']['elapsedHuman'] or 'pending'})",
        "",
        "Priority | Kind | JSON | Markdown | Why Open This | Description",
        "--- | --- | --- | --- | --- | ---",
    ]
    for entry in payload["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["whyOpenThis"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_dashboard_index_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "dashboard_index.json")
    payload["refreshRuntime"] = build_refresh_runtime_data(root)
    return payload


def render_dashboard_index(root: Path = ROOT) -> str:
    payload = build_dashboard_index_data(root=root)
    lines = [
        "Dashboard Index",
        f"Generated At: {payload['generatedAt']}",
        "",
        f"Recommended First Stop: {payload['recommendedFirstStop']}",
        f"Why Open This: {payload['whyOpenThis']}",
        f"Refresh Runtime: {payload['refreshRuntime']['status']} ({payload['refreshRuntime']['elapsedHuman'] or 'pending'})",
        "",
        "Priority | Kind | JSON | Markdown | Why Open This | Description",
        "--- | --- | --- | --- | --- | ---",
    ]
    for entry in payload["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["whyOpenThis"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_dashboard_overview_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "dashboard_overview.json")
    if not any([trust, warning_label, fit_kind, fit_finding]):
        payload["refreshRuntime"] = build_refresh_runtime_data(root)
        return payload
    case_rows = _load_case_rows(root=root, trust=trust, warning_label=warning_label)
    if fit_kind:
        fit_payload = build_fit_matrix_data(root=root, trust=trust, warning_label=warning_label, fit_kind=fit_kind)
        allowed_case_ids = {case["caseId"] for case in fit_payload["cases"]}
        case_rows = [case for case in case_rows if case["caseId"] in allowed_case_ids]
    if fit_finding:
        case_rows = [case for case in case_rows if case["fitFindingSummary"]["fitFinding"] == fit_finding]
    allowed_case_ids = {row["caseId"] for row in case_rows}
    fit_payload = build_fit_matrix_data(root=root, trust=trust, warning_label=warning_label, fit_kind=fit_kind)
    fit_payload = {
        **fit_payload,
        "summary": {
            "caseCount": len([case for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids]),
            "authorityCount": sum(
                case["authorityCount"] for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids
            ),
            "directCount": sum(case["directCount"] for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids),
            "analogicalCount": sum(
                case["analogicalCount"] for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids
            ),
            "recordSupportCount": sum(
                case["recordSupportCount"] for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids
            ),
        },
        "cases": [case for case in fit_payload["cases"] if case["caseId"] in allowed_case_ids],
    }
    fit_findings_payload = build_fit_findings_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
    )
    if fit_kind or fit_finding:
        fit_findings_payload = {
            **fit_findings_payload,
            "summary": {
                "caseCount": len([f for f in fit_findings_payload["findings"] if f["caseId"] in allowed_case_ids]),
                "directOnlyCases": sum(
                    1
                    for f in fit_findings_payload["findings"]
                    if f["caseId"] in allowed_case_ids and f["title"] == "Direct-fit authority baseline"
                ),
                "analogicalCases": sum(
                    1
                    for f in fit_findings_payload["findings"]
                    if f["caseId"] in allowed_case_ids and f["title"] == "Analogical fit posture"
                ),
                "recordSupportCases": sum(
                    1
                    for f in fit_findings_payload["findings"]
                    if f["caseId"] in allowed_case_ids and f["title"] == "Record-support-heavy fit posture"
                ),
            },
            "findings": [f for f in fit_findings_payload["findings"] if f["caseId"] in allowed_case_ids],
        }
    outputs_index = _load_json(root / "outputs" / "index.json")
    filtered_cases = [case for case in outputs_index["cases"] if case["caseId"] in {row["caseId"] for row in case_rows}]
    if case_rows:
        highest_confidence = sorted(case_rows, key=lambda item: (-item["confidence"], item["caseId"]))[0]
        lowest_confidence = sorted(case_rows, key=lambda item: (item["confidence"], item["caseId"]))[0]
        single_case_guide = None
        if len(case_rows) == 1:
            single_case_guide = {
                "caseId": case_rows[0]["caseId"],
                "recommendedFirstStop": case_rows[0]["recommendedFirstStop"],
                "whyOpenThis": case_rows[0]["whyOpenThis"],
            }
        featured = {
            "highestConfidenceCaseId": highest_confidence["caseId"],
            "highestConfidence": highest_confidence["confidence"],
            "lowestConfidenceCaseId": lowest_confidence["caseId"],
            "lowestConfidence": lowest_confidence["confidence"],
            "primaryKinds": _count_labels(case_rows, "primaryKind"),
            "warningLabels": _count_labels(
                [case for case in case_rows if case["warningLabelSummary"]["warningLabel"]],
                "authorityTrust",
            ),
            "singleCaseGuide": single_case_guide,
        }
    else:
        featured = payload["featured"]
    return {
        "generatedAt": payload["generatedAt"],
        "summary": {
            "caseCount": len(filtered_cases),
            "violationCount": sum(1 for case in filtered_cases if case["activeOutcome"] == "violation"),
            "noViolationCount": sum(1 for case in filtered_cases if case["activeOutcome"] == "no_violation"),
            "warnedCaseCount": sum(1 for case in case_rows if case["warningSummary"]["hasWarnings"]),
            "fullyVerifiedCount": sum(1 for case in case_rows if case["authorityTrust"] == "fully_verified"),
            "mixedSupportCount": sum(1 for case in case_rows if case["authorityTrust"] == "mixed_support"),
            "paraphraseHeavyCount": sum(1 for case in case_rows if case["authorityTrust"] == "paraphrase_heavy"),
            "sourceVerifiedCount": sum(case["sourceSummary"]["sourceVerifiedCount"] for case in case_rows),
            "sourceNormalizedCount": sum(case["sourceSummary"]["sourceNormalizedCount"] for case in case_rows),
            "sourceStatus": (
                "All authority entries are sourceVerified and sourceNormalized across the current case set."
                if case_rows
                and sum(case["sourceSummary"]["sourceVerifiedCount"] for case in case_rows)
                == sum(case["sourceSummary"]["authorityCount"] for case in case_rows)
                and sum(case["sourceSummary"]["sourceNormalizedCount"] for case in case_rows)
                == sum(case["sourceSummary"]["authorityCount"] for case in case_rows)
                else payload["summary"]["sourceStatus"]
            ),
            "directFitCount": fit_payload["summary"]["directCount"],
            "analogicalFitCount": fit_payload["summary"]["analogicalCount"],
            "recordSupportFitCount": fit_payload["summary"]["recordSupportCount"],
            "analogicalCases": fit_findings_payload["summary"]["analogicalCases"],
            "recordSupportCases": fit_findings_payload["summary"]["recordSupportCases"],
            "fitStatus": payload["summary"]["fitStatus"],
        },
        "discovery": payload["discovery"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "featured": featured,
    }


def render_dashboard_overview(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_kind: str | None = None,
    fit_finding: str | None = None,
) -> str:
    payload = build_dashboard_overview_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        fit_kind=fit_kind,
        fit_finding=fit_finding,
    )
    lines = [
        "Dashboard Overview",
        f"Generated At: {payload['generatedAt']}",
        "",
        "Summary",
        f"- Trust Filter: {trust or 'any'}",
        f"- Warning Label Filter: {warning_label or 'any'}",
        f"- Fit Filter: {fit_kind or 'any'}",
        f"- Fit Finding Filter: {fit_finding or 'any'}",
        f"- Refresh Runtime: {payload['refreshRuntime']['status']} ({payload['refreshRuntime']['elapsedHuman'] or 'pending'})",
        f"- Case Count: {payload['summary']['caseCount']}",
        f"- Violation Count: {payload['summary']['violationCount']}",
        f"- No-Violation Count: {payload['summary']['noViolationCount']}",
        f"- Warned Case Count: {payload['summary']['warnedCaseCount']}",
        f"- Fully Verified Count: {payload['summary']['fullyVerifiedCount']}",
        f"- Mixed Support Count: {payload['summary']['mixedSupportCount']}",
        f"- Paraphrase-Heavy Count: {payload['summary']['paraphraseHeavyCount']}",
        f"- Source Verified Count: {payload['summary']['sourceVerifiedCount']}",
        f"- Source Normalized Count: {payload['summary']['sourceNormalizedCount']}",
        f"- Source Status: {payload['summary']['sourceStatus']}",
        f"- Direct Fit Count: {payload['summary']['directFitCount']}",
        f"- Analogical Fit Count: {payload['summary']['analogicalFitCount']}",
        f"- Record-Support Fit Count: {payload['summary']['recordSupportFitCount']}",
        f"- Analogical Cases: {payload['summary']['analogicalCases']}",
        f"- Record-Support Cases: {payload['summary']['recordSupportCases']}",
        f"- Fit Status: {payload['summary']['fitStatus']}",
        "",
        "Discovery",
        f"- Recommended First Stop: {payload['discovery']['recommendedFirstStop']}",
        f"- Why Open This First: {payload['discovery']['recommendedFirstStopWhyOpenThis']}",
        f"- Refresh State: {payload['discovery']['refreshState']}",
        f"- Refresh State Why: {payload['discovery']['refreshStateWhyOpenThis']}",
        f"- Outputs Index: {payload['discovery']['outputsIndex']}",
        f"- Outputs Index Why: {payload['discovery']['outputsIndexWhyOpenThis']}",
        f"- Summary Index: {payload['discovery']['summaryIndex']}",
        f"- Summary Index Why: {payload['discovery']['summaryIndexWhyOpenThis']}",
        f"- Fit Index: {payload['discovery']['fitIndex']}",
        f"- Fit Index Why: {payload['discovery']['fitIndexWhyOpenThis']}",
        f"- Audit Index: {payload['discovery']['auditIndex']}",
        f"- Audit Index Why: {payload['discovery']['auditIndexWhyOpenThis']}",
        f"- Dashboard Index: {payload['discovery']['dashboardIndex']}",
        f"- Dashboard Index Why: {payload['discovery']['dashboardIndexWhyOpenThis']}",
        f"- Fit Summary: {payload['discovery']['fitSummary']}",
        f"- Fit Summary Why: {payload['discovery']['fitSummaryWhyOpenThis']}",
        f"- Fit Findings: {payload['discovery']['fitFindings']}",
        f"- Fit Findings Why: {payload['discovery']['fitFindingsWhyOpenThis']}",
        f"- Fit Findings Summary: {payload['discovery']['fitFindingsSummary']}",
        f"- Fit Findings Summary Why: {payload['discovery']['fitFindingsSummaryWhyOpenThis']}",
        "",
        "Featured",
        f"- Highest Confidence Case: {payload['featured']['highestConfidenceCaseId']} ({payload['featured']['highestConfidence']:.2f})",
        f"- Lowest Confidence Case: {payload['featured']['lowestConfidenceCaseId']} ({payload['featured']['lowestConfidence']:.2f})",
        f"- Primary Kinds: {payload['featured']['primaryKinds']}",
        f"- Warning Labels: {payload['featured']['warningLabels']}",
    ]
    if payload["featured"]["singleCaseGuide"]:
        guide = payload["featured"]["singleCaseGuide"]
        lines.extend(
            [
                "",
                "Single-Case Guide",
                f"- Case ID: {guide['caseId']}",
                f"- Recommended First Stop: {guide['recommendedFirstStop']}",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_audit_index_data(root: Path = ROOT) -> Dict[str, Any]:
    payload = _load_json(root / "outputs" / "audit_index.json")
    payload["refreshRuntime"] = build_refresh_runtime_data(root)
    return payload


def render_audit_index(root: Path = ROOT) -> str:
    payload = build_audit_index_data(root=root)
    lines = [
        "Audit Index",
        f"Generated At: {payload['generatedAt']}",
        "",
        f"Recommended First Stop: {payload['recommendedFirstStop']}",
        f"Why Open This: {payload['whyOpenThis']}",
        f"Refresh Runtime: {payload['refreshRuntime']['status']} ({payload['refreshRuntime']['elapsedHuman'] or 'pending'})",
        "",
        "Priority | Kind | JSON | Markdown | Why Open This | Description",
        "--- | --- | --- | --- | --- | ---",
    ]
    for entry in payload["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["whyOpenThis"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_case_audit_matrix_data(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
) -> Dict[str, Any]:
    if warning_label and warning_label not in {"mixed_support", "paraphrase_heavy"}:
        raise ValueError("warning-label must be one of: mixed_support, paraphrase_heavy")
    if fit_finding and fit_finding not in {
        "direct_only",
        "analogical_support",
        "record_support_heavy",
        "unclassified",
    }:
        raise ValueError(
            "fit-finding must be one of: direct_only, analogical_support, record_support_heavy, unclassified"
        )
    payload = _load_json(root / "outputs" / "case_audit_matrix.json")
    cases = payload["cases"]
    if trust:
        cases = [case for case in cases if case["authorityTrust"] == trust]
    if warning_label:
        cases = [case for case in cases if case["warningLabel"] == warning_label]
    if fit_finding:
        cases = [case for case in cases if case["fitFinding"] == fit_finding]
    if warned_only:
        cases = [case for case in cases if case["hasWarnings"]]
    return {
        "generatedAt": payload["generatedAt"],
        "refreshRuntime": build_refresh_runtime_data(root),
        "cases": _sort_cases(cases, sort_key),
    }


def render_case_audit_matrix(
    root: Path = ROOT,
    trust: str | None = None,
    warning_label: str | None = None,
    fit_finding: str | None = None,
    warned_only: bool = False,
    sort_key: str = "caseId",
) -> str:
    payload = build_case_audit_matrix_data(
        root=root,
        trust=trust,
        warning_label=warning_label,
        fit_finding=fit_finding,
        warned_only=warned_only,
        sort_key=sort_key,
    )
    lines = [
        "Case Audit Matrix",
        f"Generated At: {payload['generatedAt']}",
        f"Trust Filter: {trust or 'any'}",
        f"Warning Label Filter: {warning_label or 'any'}",
        f"Fit Finding Filter: {fit_finding or 'any'}",
        f"Warned Only: {'yes' if warned_only else 'no'}",
        "",
        "Case ID | Branch | Outcome | Confidence | Trust | Fit Finding | Primary | Primary Why | Warnings | Warning Count | Warning Label | Package",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in payload["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["activeOutcome"],
                    f"{case['confidence']:.2f}",
                    case["authorityTrust"],
                    case["fitFinding"],
                    case["primaryKind"],
                    case["primaryWhy"],
                    "yes" if case["hasWarnings"] else "no",
                    str(case["warningEntryCount"]),
                    case["warningLabel"] or "none",
                    case["packagePath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", dest="as_json", help="print structured JSON instead of a table")
    parser.add_argument("--branch", help="filter to a single branch label")
    parser.add_argument("--case-id", help="filter to a single case id")
    parser.add_argument(
        "--trust",
        choices=["fully_verified", "mixed_support", "paraphrase_heavy"],
        help="filter to one authority-trust label",
    )
    parser.add_argument("--detail", action="store_true", help="print the full brief-index entry list for one matching case")
    parser.add_argument("--warned-only", action="store_true", help="limit artifact-entry views to entries carrying trust warnings")
    parser.add_argument("--top-n", type=int, help="print only the top N prioritized entries for one matching case")
    parser.add_argument("--kinds", action="store_true", help="list available artifact kinds for one matching case")
    parser.add_argument("--primary-only", action="store_true", help="print only the resolved filesystem path for the package's primary artifact")
    parser.add_argument("--describe-kind", action="store_true", help="print the description and metadata for one artifact kind")
    parser.add_argument("--authority-review", action="store_true", help="print the authority review for one matching case")
    parser.add_argument("--authority-research-note", action="store_true", help="print the authority research note for one matching case")
    parser.add_argument("--source-verified-only", action="store_true", help="limit authority research-note output to sourceVerified entries")
    parser.add_argument("--source-normalized-only", action="store_true", help="limit authority research-note output to sourceNormalized entries")
    parser.add_argument("--authority-summary", action="store_true", help="print a compact authority-review summary for one matching case")
    parser.add_argument("--authority-findings", action="store_true", help="print the repo-level authority findings report")
    parser.add_argument("--source-metadata-matrix", action="store_true", help="print the repo-level source metadata rollup")
    parser.add_argument("--fit-matrix", action="store_true", help="print the repo-level fit-quality matrix")
    parser.add_argument("--fit-summary", action="store_true", help="print the compact repo-level fit-quality summary")
    parser.add_argument("--fit-findings", action="store_true", help="print the repo-level fit findings report")
    parser.add_argument("--fit-findings-summary", action="store_true", help="print the compact repo-level fit findings summary")
    parser.add_argument("--source-findings", action="store_true", help="print the repo-level source findings report")
    parser.add_argument("--refresh-state", action="store_true", help="print the snapshot refresh state sentinel")
    parser.add_argument("--wait-for-refresh-complete", action="store_true", help="wait for the refresh sentinel to reach complete before printing refresh state")
    parser.add_argument("--fail-if-refresh-running", action="store_true", help="exit with an error instead of printing refresh state while refresh is running")
    parser.add_argument("--wait-timeout", type=float, default=30.0, help="max seconds to wait for refresh completion")
    parser.add_argument("--wait-interval", type=float, default=0.1, help="poll interval in seconds while waiting for refresh completion")
    parser.add_argument("--trust-matrix", action="store_true", help="print the repo-level trust matrix")
    parser.add_argument("--warning-summary", action="store_true", help="print the repo-level warning summary")
    parser.add_argument("--warning-label-matrix", action="store_true", help="print the repo-level warning-label matrix")
    parser.add_argument("--warning-entry-matrix", action="store_true", help="print the repo-level warning-entry matrix")
    parser.add_argument("--warning-kind-matrix", action="store_true", help="print the repo-level warning-kind matrix")
    parser.add_argument("--warning-entry-summary", action="store_true", help="print the repo-level warning-entry summary")
    parser.add_argument("--warning-kind-summary", action="store_true", help="print the repo-level warning-kind summary")
    parser.add_argument("--summary-index", action="store_true", help="print the compact repo-level summary index")
    parser.add_argument("--fit-index", action="store_true", help="print the compact repo-level fit index")
    parser.add_argument("--dashboard-index", action="store_true", help="print the compact dashboard discovery index")
    parser.add_argument("--dashboard-overview", action="store_true", help="print the compact repo-level dashboard overview")
    parser.add_argument("--audit-index", action="store_true", help="print the repo-level audit index")
    parser.add_argument("--case-audit-matrix", action="store_true", help="print the repo-level joined case-audit matrix")
    parser.add_argument("--verified-only", action="store_true", help="limit authority review output to verified quotes")
    parser.add_argument(
        "--severity",
        choices=["info", "warning"],
        help="limit authority findings output to one severity level",
    )
    parser.add_argument(
        "--support-status",
        choices=["verified_quote", "paraphrase", "missing"],
        help="limit authority review output to one support status",
    )
    parser.add_argument(
        "--fit",
        choices=["direct", "analogical", "record_support"],
        help="limit authority output to one fit-kind label",
    )
    parser.add_argument(
        "--fit-finding",
        choices=["direct_only", "analogical_support", "record_support_heavy", "unclassified"],
        help="limit case-audit output to one fit-finding label",
    )
    parser.add_argument(
        "--warning-label",
        choices=["mixed_support", "paraphrase_heavy"],
        help="limit warning-oriented output to one warning label",
    )
    parser.add_argument("--warned-kind", help="limit warning-entry output to cases warning on one artifact kind")
    parser.add_argument("--path-only", action="store_true", help="print only the resolved filesystem path for one artifact kind")
    parser.add_argument("--kind", help="artifact kind to use with --path-only")
    parser.add_argument(
        "--sort",
        choices=["caseId", "confidence", "branch", "warningCount"],
        default="caseId",
        help="sort the rendered cases",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    if args.warning_summary:
        payload = build_warning_summary_data(
            ROOT,
            branch=args.branch,
            case_id=args.case_id,
            trust=args.trust,
            warning_label=args.warning_label,
            sort_key=args.sort,
        )
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(
                prepend_refresh_warning(
                    render_warning_summary(
                        ROOT,
                        branch=args.branch,
                        case_id=args.case_id,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        sort_key=args.sort,
                    ),
                    ROOT,
                )
            )
        return 0
    if args.warning_label_matrix:
        try:
            payload = build_warning_label_matrix_data(
                ROOT,
                warning_label=args.warning_label,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_warning_label_matrix(
                            ROOT,
                            warning_label=args.warning_label,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.warning_entry_matrix:
        try:
            payload = build_warning_entry_matrix_data(
                ROOT,
                trust=args.trust,
                warning_label=args.warning_label,
                warned_kind=args.warned_kind,
                sort_key=args.sort,
                top_n=args.top_n,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_warning_entry_matrix(
                            ROOT,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            warned_kind=args.warned_kind,
                            sort_key=args.sort,
                            top_n=args.top_n,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.warning_kind_matrix:
        payload = build_warning_kind_matrix_data(
            ROOT,
            trust=args.trust,
            warned_kind=args.warned_kind,
            sort_key="warningCaseCount" if args.sort == "warningCount" else "kind",
            top_n=args.top_n,
        )
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(
                prepend_refresh_warning(
                    render_warning_kind_matrix(
                        ROOT,
                        trust=args.trust,
                        warned_kind=args.warned_kind,
                        sort_key="warningCaseCount" if args.sort == "warningCount" else "kind",
                        top_n=args.top_n,
                    ),
                    ROOT,
                )
            )
        return 0
    if args.warning_entry_summary:
        try:
            payload = build_warning_entry_summary_data(
                ROOT,
                trust=args.trust,
                warning_label=args.warning_label,
                sort_key=args.sort,
                top_n=args.top_n,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_warning_entry_summary(
                            ROOT,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            sort_key=args.sort,
                            top_n=args.top_n,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.warning_kind_summary:
        try:
            payload = build_warning_kind_summary_data(
                ROOT,
                trust=args.trust,
                warning_label=args.warning_label,
                sort_key="warningCaseCount" if args.sort == "warningCount" else "kind",
                top_n=args.top_n,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_warning_kind_summary(
                            ROOT,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            sort_key="warningCaseCount" if args.sort == "warningCount" else "kind",
                            top_n=args.top_n,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.summary_index:
        payload = build_summary_index_data(ROOT)
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(prepend_refresh_warning(render_summary_index(ROOT), ROOT))
        return 0
    if args.fit_index:
        payload = build_fit_index_data(ROOT)
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(prepend_refresh_warning(render_fit_index(ROOT), ROOT))
        return 0
    if args.dashboard_index:
        payload = build_dashboard_index_data(ROOT)
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(prepend_refresh_warning(render_dashboard_index(ROOT), ROOT))
        return 0
    if args.dashboard_overview:
        payload = build_dashboard_overview_data(
            ROOT,
            trust=args.trust,
            warning_label=args.warning_label,
            fit_kind=args.fit,
            fit_finding=args.fit_finding,
        )
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(
                prepend_refresh_warning(
                    render_dashboard_overview(
                        ROOT,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        fit_kind=args.fit,
                        fit_finding=args.fit_finding,
                    ),
                    ROOT,
                )
            )
        return 0
    if args.source_findings:
        try:
            payload = build_source_findings_data(
                ROOT,
                severity=args.severity,
                case_id=args.case_id,
                branch=args.branch,
                trust=args.trust,
                warning_label=args.warning_label,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_source_findings(
                            ROOT,
                            severity=args.severity,
                            case_id=args.case_id,
                            branch=args.branch,
                            trust=args.trust,
                            warning_label=args.warning_label,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.refresh_state:
        try:
            payload = build_refresh_state_data(ROOT)
            if args.fail_if_refresh_running:
                payload = fail_if_refresh_running(ROOT)
            if args.wait_for_refresh_complete:
                payload = wait_for_refresh_complete(
                    ROOT,
                    timeout_seconds=args.wait_timeout,
                    poll_interval_seconds=args.wait_interval,
                )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                lines = [
                    "Refresh State",
                    f"Status: {payload['status']}",
                    f"Started At: {payload['startedAt']}",
                    f"Completed At: {payload['completedAt'] or 'pending'}",
                    f"Elapsed Seconds: {payload['elapsedSeconds'] if payload['elapsedSeconds'] is not None else 'pending'}",
                    f"Elapsed: {payload['elapsedHuman'] or 'pending'}",
                ]
                sys.stdout.write("\n".join(lines) + "\n")
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.audit_index:
        payload = build_audit_index_data(ROOT)
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(prepend_refresh_warning(render_audit_index(ROOT), ROOT))
        return 0
    if args.case_audit_matrix:
        try:
            payload = build_case_audit_matrix_data(
                ROOT,
                trust=args.trust,
                warning_label=args.warning_label,
                fit_finding=args.fit_finding,
                warned_only=args.warned_only,
                sort_key=args.sort,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_case_audit_matrix(
                            ROOT,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            fit_finding=args.fit_finding,
                            warned_only=args.warned_only,
                            sort_key=args.sort,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.trust_matrix:
        try:
            payload = build_trust_matrix_data(
                ROOT,
                branch=args.branch,
                case_id=args.case_id,
                trust=args.trust,
                warning_label=args.warning_label,
                warned_only=args.warned_only,
                sort_key=args.sort,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_trust_matrix(
                            ROOT,
                            branch=args.branch,
                            case_id=args.case_id,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            warned_only=args.warned_only,
                            sort_key=args.sort,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.authority_findings:
        try:
            payload = build_authority_findings_data(
                ROOT,
                severity=args.severity,
                case_id=args.case_id,
                branch=args.branch,
                trust=args.trust,
                warning_label=args.warning_label,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    render_authority_findings(
                        ROOT,
                        severity=args.severity,
                        case_id=args.case_id,
                        branch=args.branch,
                        trust=args.trust,
                        warning_label=args.warning_label,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.source_metadata_matrix:
        payload = build_source_metadata_matrix_data(
            ROOT,
            trust=args.trust,
            warning_label=args.warning_label,
        )
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(
                prepend_refresh_warning(
                    render_source_metadata_matrix(
                        ROOT,
                        trust=args.trust,
                        warning_label=args.warning_label,
                    ),
                    ROOT,
                )
            )
        return 0
    if args.fit_matrix:
        payload = build_fit_matrix_data(
            ROOT,
            trust=args.trust,
            warning_label=args.warning_label,
            fit_kind=args.fit,
            fit_finding=args.fit_finding,
        )
        if args.as_json:
            sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        else:
            sys.stdout.write(
                prepend_refresh_warning(
                    render_fit_matrix(
                        ROOT,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        fit_kind=args.fit,
                        fit_finding=args.fit_finding,
                    ),
                    ROOT,
                )
            )
        return 0
    if args.fit_summary:
        try:
            payload = build_fit_summary_data(
                ROOT,
                trust=args.trust,
                warning_label=args.warning_label,
                fit_kind=args.fit,
                fit_finding=args.fit_finding,
                sort_key=args.sort,
                top_n=args.top_n,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_fit_summary(
                            ROOT,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            fit_kind=args.fit,
                            fit_finding=args.fit_finding,
                            sort_key=args.sort,
                            top_n=args.top_n,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.fit_findings:
        try:
            payload = build_fit_findings_data(
                ROOT,
                severity=args.severity,
                trust=args.trust,
                warning_label=args.warning_label,
                fit_finding=args.fit_finding,
                case_id=args.case_id,
                branch=args.branch,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_fit_findings(
                            ROOT,
                            severity=args.severity,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            fit_finding=args.fit_finding,
                            case_id=args.case_id,
                            branch=args.branch,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.fit_findings_summary:
        try:
            payload = build_fit_findings_summary_data(
                ROOT,
                severity=args.severity,
                trust=args.trust,
                warning_label=args.warning_label,
                fit_finding=args.fit_finding,
                case_id=args.case_id,
                branch=args.branch,
            )
            if args.as_json:
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    prepend_refresh_warning(
                        render_fit_findings_summary(
                            ROOT,
                            severity=args.severity,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            fit_finding=args.fit_finding,
                            case_id=args.case_id,
                            branch=args.branch,
                        ),
                        ROOT,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.authority_summary:
        try:
            if args.case_id:
                if args.as_json:
                    payload = build_authority_review_summary(
                        ROOT,
                        case_id=args.case_id,
                        branch=args.branch,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        verified_only=args.verified_only,
                        support_status=args.support_status,
                        fit_kind=args.fit,
                    )
                    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
                else:
                    sys.stdout.write(
                        render_authority_review_summary(
                            ROOT,
                            case_id=args.case_id,
                            branch=args.branch,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            verified_only=args.verified_only,
                            support_status=args.support_status,
                            fit_kind=args.fit,
                        )
                    )
            else:
                if args.as_json:
                    payload = build_authority_summary_matrix(
                        ROOT,
                        branch=args.branch,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        verified_only=args.verified_only,
                        support_status=args.support_status,
                        fit_kind=args.fit,
                        sort_key=args.sort,
                    )
                    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
                else:
                    sys.stdout.write(
                        render_authority_summary_matrix(
                            ROOT,
                            branch=args.branch,
                            trust=args.trust,
                            warning_label=args.warning_label,
                            verified_only=args.verified_only,
                            support_status=args.support_status,
                            fit_kind=args.fit,
                            sort_key=args.sort,
                        )
                    )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.authority_review:
        try:
            if args.as_json:
                payload = build_authority_review_data(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    verified_only=args.verified_only,
                    support_status=args.support_status,
                    fit_kind=args.fit,
                )
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    render_authority_review(
                        ROOT,
                        case_id=args.case_id,
                        branch=args.branch,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        verified_only=args.verified_only,
                        support_status=args.support_status,
                        fit_kind=args.fit,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.authority_research_note:
        try:
            if args.as_json:
                payload = build_authority_research_note_data(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    source_verified_only=args.source_verified_only,
                    source_normalized_only=args.source_normalized_only,
                    fit_kind=args.fit,
                )
                sys.stdout.write(json.dumps(payload, indent=2) + "\n")
            else:
                sys.stdout.write(
                    render_authority_research_note(
                        ROOT,
                        case_id=args.case_id,
                        branch=args.branch,
                        trust=args.trust,
                        warning_label=args.warning_label,
                        source_verified_only=args.source_verified_only,
                        source_normalized_only=args.source_normalized_only,
                        fit_kind=args.fit,
                    )
                )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.describe_kind:
        try:
            sys.stdout.write(
                describe_artifact_kind(
                    ROOT,
                    kind=args.kind,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                )
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.primary_only:
        try:
            sys.stdout.write(
                resolve_primary_artifact_path(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                )
                + "\n"
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.kinds:
        try:
            sys.stdout.write(
                list_artifact_kinds(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                )
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.path_only:
        try:
            sys.stdout.write(
                resolve_artifact_path(
                    ROOT,
                    kind=args.kind,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                )
                + "\n"
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.detail:
        try:
            sys.stdout.write(
                render_case_detail(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                )
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    if args.as_json:
        try:
            payload = build_case_matrix_data(
                ROOT,
                branch=args.branch,
                case_id=args.case_id,
                trust=args.trust,
                warning_label=args.warning_label,
                fit_finding=args.fit_finding,
                warned_only=args.warned_only,
                sort_key=args.sort,
                top_n=args.top_n,
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        sys.stdout.write(json.dumps(payload, indent=2) + "\n")
        return 0
    if args.top_n is not None:
        try:
            sys.stdout.write(
                render_top_artifacts(
                    ROOT,
                    case_id=args.case_id,
                    branch=args.branch,
                    trust=args.trust,
                    warning_label=args.warning_label,
                    warned_only=args.warned_only,
                    top_n=args.top_n,
                )
            )
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return 0
    sys.stdout.write(
        render_case_matrix(
            ROOT,
            branch=args.branch,
            case_id=args.case_id,
            trust=args.trust,
            warning_label=args.warning_label,
            fit_finding=args.fit_finding,
            warned_only=args.warned_only,
            sort_key=args.sort,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
