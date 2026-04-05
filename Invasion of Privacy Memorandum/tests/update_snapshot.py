#!/usr/bin/env python3
"""Refresh canonical snapshots from the live-in-aide fixture."""

from __future__ import annotations

import json
from pathlib import Path
from datetime import datetime, timezone

from engine.evaluate_case import evaluate_case
from engine.export_artifacts import export_package
from engine.generate_advocacy import generate_advocacy_bundle, generate_advocacy_outputs
from engine.generate_memorandum import generate_memorandum_bundle, write_memorandum_outputs
from engine.legal_grounding import build_dependency_citations_jsonld
from engine.print_case_matrix import (
    build_authority_summary_matrix,
    build_warning_summary_data,
    render_authority_summary_matrix_markdown,
    render_warning_summary,
)


ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT_DIR = ROOT / "tests" / "snapshots"
FIXTURE_NAMES = [
    "live_in_aide_case.json",
    "live_in_aide_case_effective_accommodation.json",
    "live_in_aide_case_no_violation.json",
    "live_in_aide_case_undue_burden.json",
]


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)


def _write_json_atomic(path: Path, payload: dict) -> None:
    _write_text_atomic(path, json.dumps(payload, indent=2) + "\n")


def _refresh_state_path() -> Path:
    return ROOT / "outputs" / ".refresh_state.json"


def _write_refresh_state(status: str, started_at: str, completed_at: str | None = None) -> None:
    payload = {
        "status": status,
        "startedAt": started_at,
        "completedAt": completed_at,
    }
    _write_json_atomic(_refresh_state_path(), payload)


def _sanity_check_refresh_outputs() -> None:
    json_paths = [
        ROOT / "outputs" / "index.json",
        ROOT / "outputs" / "dashboard_overview.json",
        ROOT / "outputs" / "fit_summary.json",
        ROOT / "outputs" / "warning_entry_summary.json",
        ROOT / "outputs" / "case_audit_matrix.json",
        ROOT / "outputs" / "trust_matrix.json",
    ]
    for path in json_paths:
        payload = json.loads(path.read_text())
        if not isinstance(payload, dict):
            raise ValueError(f"sanity check failed: {path} did not parse to an object")
    text_paths = [
        ROOT / "outputs" / "dashboard_overview.md",
        ROOT / "outputs" / "case_audit_matrix.md",
        ROOT / "outputs" / "trust_matrix.md",
    ]
    for path in text_paths:
        content = path.read_text()
        if not content.strip():
            raise ValueError(f"sanity check failed: {path} was empty")


def count_labels(rows: list[dict], key: str) -> dict:
    counts = {}
    for row in rows:
        value = row.get(key)
        if value is None:
            continue
        counts[value] = counts.get(value, 0) + 1
    return counts


def build_package_snapshot(export_dir: Path) -> dict:
    snapshot = {}
    for path in sorted(export_dir.iterdir()):
        if not path.is_file():
            continue
        if path.suffix in {".json", ".jsonld"}:
            snapshot[path.name] = json.loads(path.read_text())
        elif path.suffix == ".pdf":
            snapshot[path.name] = {
                "kind": "binary",
                "size": path.stat().st_size,
            }
        else:
            snapshot[path.name] = path.read_text()
    return snapshot


def build_outputs_index() -> dict:
    cases = []
    for fixture_name in FIXTURE_NAMES:
        fixture_path = ROOT / "fixtures" / fixture_name
        payload = json.loads(fixture_path.read_text())
        result = evaluate_case(payload)
        case_id = result["caseId"]
        cases.append(
            {
                "fixture": fixture_name,
                "caseId": case_id,
                "branch": result["branch"],
                "confidence": result["confidence"],
                "activeOutcome": "violation" if result["outcome"]["violation"] else "no_violation",
                "resultPath": f"outputs/{case_id}.result.json",
                "packagePath": f"outputs/{case_id}_package",
                "advocacyPath": f"outputs/{fixture_path.stem}_advocacy",
                "memorandumPath": f"outputs/{fixture_path.stem}_memorandum",
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }


def render_outputs_index_markdown(report: dict) -> str:
    lines = [
        "# Outputs Index",
        "",
        "Fixture | Case ID | Branch | Confidence | Outcome | Result | Package | Advocacy | Memorandum",
        "--- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
        lines.append(
            " | ".join(
                [
                    case["fixture"],
                    case["caseId"],
                    case["branch"],
                    f"{case['confidence']:.2f}",
                    case["activeOutcome"],
                    case["resultPath"],
                    case["packagePath"],
                    case["advocacyPath"],
                    case["memorandumPath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_authority_findings_report(authority_summary_matrix: dict) -> dict:
    findings = []
    fully_verified_cases = 0
    mixed_support_cases = 0
    paraphrase_heavy_cases = 0
    for case in authority_summary_matrix["cases"]:
        verified_count = case["statusCounts"].get("verified_quote", 0)
        paraphrase_count = case["statusCounts"].get("paraphrase", 0)
        if paraphrase_count == 0:
            fully_verified_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "info",
                    "title": "Fully verified authority baseline",
                    "detail": "All currently attached authority support is marked as verified_quote.",
                }
            )
            continue
        mixed_support_cases += 1
        if paraphrase_count >= verified_count:
            paraphrase_heavy_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "warning",
                    "title": "Paraphrase-heavy authority support",
                    "detail": (
                        f"This case uses {paraphrase_count} paraphrase supports and {verified_count} verified quotes, "
                        "so advocacy and memorandum outputs should be presented as lower-trust authority grounding."
                    ),
                }
            )
        else:
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "warning",
                    "title": "Mixed authority support",
                    "detail": (
                        f"This case mixes {verified_count} verified quotes with {paraphrase_count} paraphrase supports, "
                        "so downstream consumers should distinguish direct support from fallback grounding."
                    ),
                }
            )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(authority_summary_matrix["cases"]),
            "fullyVerifiedCases": fully_verified_cases,
            "mixedSupportCases": mixed_support_cases,
            "paraphraseHeavyCases": paraphrase_heavy_cases,
        },
        "findings": findings,
    }


def render_authority_findings_markdown(report: dict) -> str:
    lines = [
        "# Authority Findings Report",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Fully Verified Cases: `{report['summary']['fullyVerifiedCases']}`",
        f"Mixed Support Cases: `{report['summary']['mixedSupportCases']}`",
        f"Paraphrase-Heavy Cases: `{report['summary']['paraphraseHeavyCases']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['caseId']} [{finding['severity']}]",
                "",
                f"- Branch: `{finding['branch']}`",
                f"- Title: {finding['title']}",
                f"- Detail: {finding['detail']}",
                "",
            ]
        )
    return "\n".join(lines)


def build_trust_matrix(outputs_index: dict) -> dict:
    cases = []
    for item in outputs_index["cases"]:
        package_dir = ROOT / item["packagePath"]
        brief_index = json.loads((package_dir / "brief_index.json").read_text())
        warning_entry_count = sum(1 for entry in brief_index["entries"] if "trustWarning" in entry)
        cases.append(
            {
                "caseId": item["caseId"],
                "branch": item["branch"],
                "activeOutcome": item["activeOutcome"],
                "authorityTrust": brief_index["authorityTrust"]["label"],
                "primaryKind": brief_index["primaryKind"],
                "hasEntryWarnings": warning_entry_count > 0,
                "warningEntryCount": warning_entry_count,
                "packagePath": item["packagePath"],
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }


def build_source_metadata_matrix(outputs_index: dict) -> dict:
    cases = []
    total_authorities = 0
    total_verified = 0
    total_normalized = 0
    for item in outputs_index["cases"]:
        package_dir = ROOT / item["packagePath"]
        research = json.loads((package_dir / "authority_research_note.json").read_text())
        entries = research["entries"]
        authority_count = len(entries)
        verified_count = sum(1 for entry in entries if entry.get("sourceVerified"))
        normalized_count = sum(1 for entry in entries if entry.get("sourceNormalized"))
        cases.append(
            {
                "caseId": item["caseId"],
                "branch": item["branch"],
                "authorityCount": authority_count,
                "sourceVerifiedCount": verified_count,
                "sourceNormalizedCount": normalized_count,
                "unnormalizedAuthorityIds": sorted(
                    entry["id"] for entry in entries if not entry.get("sourceNormalized")
                ),
            }
        )
        total_authorities += authority_count
        total_verified += verified_count
        total_normalized += normalized_count
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(cases),
            "authorityCount": total_authorities,
            "sourceVerifiedCount": total_verified,
            "sourceNormalizedCount": total_normalized,
        },
        "cases": cases,
    }


def build_fit_matrix(outputs_index: dict) -> dict:
    cases = []
    total_authorities = 0
    total_direct = 0
    total_analogical = 0
    total_record_support = 0
    for item in outputs_index["cases"]:
        package_dir = ROOT / item["packagePath"]
        brief_index = json.loads((package_dir / "brief_index.json").read_text())
        fit_summary = brief_index["fitSummary"]
        cases.append(
            {
                "caseId": item["caseId"],
                "branch": item["branch"],
                "authorityCount": fit_summary["authorityCount"],
                "directCount": fit_summary["directCount"],
                "analogicalCount": fit_summary["analogicalCount"],
                "recordSupportCount": fit_summary["recordSupportCount"],
                "fitStatus": fit_summary["fitStatus"],
            }
        )
        total_authorities += fit_summary["authorityCount"]
        total_direct += fit_summary["directCount"]
        total_analogical += fit_summary["analogicalCount"]
        total_record_support += fit_summary["recordSupportCount"]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(cases),
            "authorityCount": total_authorities,
            "directCount": total_direct,
            "analogicalCount": total_analogical,
            "recordSupportCount": total_record_support,
        },
        "cases": cases,
    }


def render_fit_matrix_markdown(report: dict) -> str:
    lines = [
        "# Fit Matrix",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Authority Count: `{report['summary']['authorityCount']}`",
        f"Direct Count: `{report['summary']['directCount']}`",
        f"Analogical Count: `{report['summary']['analogicalCount']}`",
        f"Record-Support Count: `{report['summary']['recordSupportCount']}`",
        "",
        "Case ID | Branch | Authorities | Direct | Analogical | Record Support | Fit Status",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
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


def build_fit_summary(fit_matrix: dict) -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": dict(fit_matrix["summary"]),
        "singleCaseGuide": None,
        "cases": [
            {
                "caseId": case["caseId"],
                "branch": case["branch"],
                "directCount": case["directCount"],
                "analogicalCount": case["analogicalCount"],
                "recordSupportCount": case["recordSupportCount"],
                "fitStatus": case["fitStatus"],
            }
            for case in fit_matrix["cases"]
        ],
    }


def render_fit_summary_markdown(report: dict) -> str:
    lines = [
        "# Fit Summary",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Authority Count: `{report['summary']['authorityCount']}`",
        f"Direct Count: `{report['summary']['directCount']}`",
        f"Analogical Count: `{report['summary']['analogicalCount']}`",
        f"Record-Support Count: `{report['summary']['recordSupportCount']}`",
        "",
        "Case ID | Branch | Direct | Analogical | Record Support | Fit Status",
        "--- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    str(case["directCount"]),
                    str(case["analogicalCount"]),
                    str(case["recordSupportCount"]),
                    case["fitStatus"],
                ]
            )
        )
    if report["singleCaseGuide"]:
        guide = report["singleCaseGuide"]
        lines.extend(
            [
                "",
                "## Single-Case Guide",
                "",
                f"- Case ID: `{guide['caseId']}`",
                f"- Recommended First Stop: `{guide['recommendedFirstStop']}`",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_fit_findings_report(fit_matrix: dict) -> dict:
    findings = []
    direct_only_cases = 0
    analogical_cases = 0
    record_support_cases = 0
    for case in fit_matrix["cases"]:
        direct_count = case["directCount"]
        analogical_count = case["analogicalCount"]
        record_support_count = case["recordSupportCount"]
        if record_support_count > 0:
            record_support_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "warning",
                    "title": "Record-support-heavy fit posture",
                    "detail": (
                        f"This case includes {record_support_count} record-support mappings, "
                        f"{analogical_count} analogical mappings, and {direct_count} direct mappings, "
                        "so downstream readers should distinguish record support from directly controlling authority."
                    ),
                }
            )
        elif analogical_count > 0:
            analogical_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "warning",
                    "title": "Analogical fit posture",
                    "detail": (
                        f"This case includes {analogical_count} analogical mappings and {direct_count} direct mappings, "
                        "so the authority fit should be presented as mixed direct and analogical support."
                    ),
                }
            )
        else:
            direct_only_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "info",
                    "title": "Direct-fit authority baseline",
                    "detail": "All currently attached fit mappings for this case are direct.",
                }
            )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(fit_matrix["cases"]),
            "directOnlyCases": direct_only_cases,
            "analogicalCases": analogical_cases,
            "recordSupportCases": record_support_cases,
        },
        "findings": findings,
    }


def build_fit_findings_summary(report: dict) -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": report["summary"]["caseCount"],
            "directOnlyCases": report["summary"]["directOnlyCases"],
            "analogicalCases": report["summary"]["analogicalCases"],
            "recordSupportCases": report["summary"]["recordSupportCases"],
            "severityCounts": count_labels(report["findings"], "severity"),
        },
        "singleCaseGuide": None,
        "cases": [
            {
                "caseId": finding["caseId"],
                "branch": finding["branch"],
                "severity": finding["severity"],
                "title": finding["title"],
            }
            for finding in report["findings"]
        ],
    }


def render_fit_findings_summary_markdown(report: dict) -> str:
    lines = [
        "# Fit Findings Summary",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Direct-Only Cases: `{report['summary']['directOnlyCases']}`",
        f"Analogical Cases: `{report['summary']['analogicalCases']}`",
        f"Record-Support Cases: `{report['summary']['recordSupportCases']}`",
        f"Severity Counts: `{report['summary']['severityCounts']}`",
        "",
        "Case ID | Branch | Severity | Title",
        "--- | --- | --- | ---",
    ]
    for case in report["cases"]:
        lines.append(" | ".join([case["caseId"], case["branch"], case["severity"], case["title"]]))
    if report["singleCaseGuide"]:
        guide = report["singleCaseGuide"]
        lines.extend(
            [
                "",
                "## Single-Case Guide",
                "",
                f"- Case ID: `{guide['caseId']}`",
                f"- Recommended First Stop: `{guide['recommendedFirstStop']}`",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def render_fit_findings_markdown(report: dict) -> str:
    lines = [
        "# Fit Findings Report",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Direct-Only Cases: `{report['summary']['directOnlyCases']}`",
        f"Analogical Cases: `{report['summary']['analogicalCases']}`",
        f"Record-Support Cases: `{report['summary']['recordSupportCases']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['caseId']} [{finding['severity']}]",
                "",
                f"- Branch: `{finding['branch']}`",
                f"- Title: {finding['title']}",
                f"- Detail: {finding['detail']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_source_metadata_matrix_markdown(report: dict) -> str:
    lines = [
        "# Source Metadata Matrix",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Authority Count: `{report['summary']['authorityCount']}`",
        f"Source Verified Count: `{report['summary']['sourceVerifiedCount']}`",
        f"Source Normalized Count: `{report['summary']['sourceNormalizedCount']}`",
        "",
        "Case ID | Branch | Authorities | Verified | Normalized | Unnormalized IDs",
        "--- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
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


def build_source_findings_report(source_metadata_matrix: dict) -> dict:
    findings = []
    fully_normalized_cases = 0
    partially_normalized_cases = 0
    for case in source_metadata_matrix["cases"]:
        if case["sourceNormalizedCount"] == case["authorityCount"]:
            fully_normalized_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "info",
                    "title": "All authority metadata normalized",
                    "detail": "Every authority entry in this case is marked as sourceNormalized.",
                }
            )
        else:
            partially_normalized_cases += 1
            findings.append(
                {
                    "caseId": case["caseId"],
                    "branch": case["branch"],
                    "severity": "warning",
                    "title": "Some authority metadata still unnormalized",
                    "detail": (
                        f"This case still has unnormalized authority metadata for: "
                        f"{', '.join(case['unnormalizedAuthorityIds']) or 'none'}."
                    ),
                }
            )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(source_metadata_matrix["cases"]),
            "fullyNormalizedCases": fully_normalized_cases,
            "partiallyNormalizedCases": partially_normalized_cases,
        },
        "findings": findings,
    }


def render_source_findings_markdown(report: dict) -> str:
    lines = [
        "# Source Findings Report",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Fully Normalized Cases: `{report['summary']['fullyNormalizedCases']}`",
        f"Partially Normalized Cases: `{report['summary']['partiallyNormalizedCases']}`",
        "",
        "## Findings",
        "",
    ]
    for finding in report["findings"]:
        lines.extend(
            [
                f"### {finding['caseId']} [{finding['severity']}]",
                "",
                f"- Branch: `{finding['branch']}`",
                f"- Title: {finding['title']}",
                f"- Detail: {finding['detail']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_trust_matrix_markdown(report: dict) -> str:
    lines = [
        "# Trust Matrix",
        "",
        "Case ID | Branch | Outcome | Authority Trust | Primary Kind | Entry Warnings | Warning Count | Package",
        "--- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["activeOutcome"],
                    case["authorityTrust"],
                    case["primaryKind"],
                    "yes" if case["hasEntryWarnings"] else "no",
                    str(case["warningEntryCount"]),
                    case["packagePath"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_warning_label_matrix() -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "labels": {
            "mixed_support": build_warning_summary_data(ROOT, warning_label="mixed_support"),
            "paraphrase_heavy": build_warning_summary_data(ROOT, warning_label="paraphrase_heavy"),
        },
    }


def render_warning_label_matrix_markdown(report: dict) -> str:
    lines = [
        "# Warning Label Matrix",
        "",
    ]
    for label in ["mixed_support", "paraphrase_heavy"]:
        payload = report["labels"][label]
        lines.extend(
            [
                f"## {label}",
                "",
                f"Warned Cases: `{payload['summary']['warnedCaseCount']}`",
                f"Warning Counts: `{payload['summary']['warningCounts']}`",
                "",
                "Case ID | Branch | Outcome | Trust | Primary | Warning Count | Package",
                "--- | --- | --- | --- | --- | --- | ---",
            ]
        )
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
        lines.append("")
    return "\n".join(lines)


def build_warning_entry_matrix(outputs_index: dict) -> dict:
    cases = []
    for item in outputs_index["cases"]:
        brief_index = json.loads((ROOT / item["packagePath"] / "brief_index.json").read_text())
        warning_summary = brief_index["warningSummary"]
        if not warning_summary["hasWarnings"]:
            continue
        warned_kinds = [
            entry["kind"]
            for entry in sorted(brief_index["entries"], key=lambda value: (value["priority"], value["kind"]))
            if entry.get("trustWarning")
        ]
        cases.append(
            {
                "caseId": item["caseId"],
                "branch": item["branch"],
                "authorityTrust": brief_index["authorityTrust"]["label"],
                "warningLabel": brief_index["warningLabelSummary"]["warningLabel"],
                "warningEntryCount": warning_summary["warningEntryCount"],
                "warningCounts": warning_summary["warningCounts"],
                "warnedKinds": warned_kinds,
                "packagePath": item["packagePath"],
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }


def render_warning_entry_matrix_markdown(report: dict) -> str:
    lines = [
        "# Warning Entry Matrix",
        "",
        "Case ID | Branch | Trust | Warning Label | Warning Count | Warned Kinds | Package",
        "--- | --- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
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


def build_warning_entry_summary(warning_entry_matrix: dict) -> dict:
    warning_labels: dict[str, int] = {}
    for case in warning_entry_matrix["cases"]:
        warning_labels[case["warningLabel"]] = warning_labels.get(case["warningLabel"], 0) + 1
    cases = [
        {
            "caseId": case["caseId"],
            "branch": case["branch"],
            "authorityTrust": case["authorityTrust"],
            "warningLabel": case["warningLabel"],
            "warningEntryCount": case["warningEntryCount"],
        }
        for case in warning_entry_matrix["cases"]
    ]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(cases),
            "warningLabels": dict(sorted(warning_labels.items())),
        },
        "singleCaseGuide": None,
        "cases": cases,
    }


def render_warning_entry_summary_markdown(report: dict) -> str:
    lines = [
        "# Warning Entry Summary",
        "",
        f"Case Count: `{report['summary']['caseCount']}`",
        f"Warning Labels: `{report['summary']['warningLabels']}`",
        "",
        "Case ID | Branch | Trust | Warning Label | Warning Count",
        "--- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
        lines.append(
            " | ".join(
                [
                    case["caseId"],
                    case["branch"],
                    case["authorityTrust"],
                    case["warningLabel"],
                    str(case["warningEntryCount"]),
                ]
            )
        )
    if report["singleCaseGuide"]:
        guide = report["singleCaseGuide"]
        lines.extend(
            [
                "",
                "## Single-Case Guide",
                "",
                f"- Case ID: `{guide['caseId']}`",
                f"- Recommended First Stop: `{guide['recommendedFirstStop']}`",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_warning_kind_matrix(outputs_index: dict) -> dict:
    kinds: dict[str, dict] = {}
    warned_case_ids = set()
    for item in outputs_index["cases"]:
        brief_index = json.loads((ROOT / item["packagePath"] / "brief_index.json").read_text())
        warning_label = brief_index["warningLabelSummary"]["warningLabel"]
        if not warning_label:
            continue
        warned_case_ids.add(item["caseId"])
        for entry in brief_index["entries"]:
            if not entry.get("trustWarning"):
                continue
            bucket = kinds.setdefault(
                entry["kind"],
                {
                    "kind": entry["kind"],
                    "warningLabels": {},
                    "cases": [],
                },
            )
            bucket["warningLabels"][warning_label] = bucket["warningLabels"].get(warning_label, 0) + 1
            bucket["cases"].append(
                {
                    "caseId": item["caseId"],
                    "branch": item["branch"],
                    "authorityTrust": brief_index["authorityTrust"]["label"],
                    "warningLabel": warning_label,
                    "packagePath": item["packagePath"],
                }
            )
    rows = []
    for kind in sorted(kinds):
        bucket = kinds[kind]
        rows.append(
            {
                "kind": kind,
                "warningCaseCount": len(bucket["cases"]),
                "warningLabels": dict(sorted(bucket["warningLabels"].items())),
                "cases": sorted(bucket["cases"], key=lambda value: value["caseId"]),
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "kindCount": len(rows),
            "caseCount": len(warned_case_ids),
        },
        "kinds": rows,
    }


def render_warning_kind_matrix_markdown(report: dict) -> str:
    lines = [
        "# Warning Kind Matrix",
        "",
        f"Kind Count: `{report['summary']['kindCount']}`",
        f"Case Count: `{report['summary']['caseCount']}`",
        "",
        "Kind | Warning Cases | Warning Labels | Case IDs",
        "--- | --- | --- | ---",
    ]
    for item in report["kinds"]:
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


def build_warning_kind_summary(warning_kind_matrix: dict) -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": dict(warning_kind_matrix["summary"]),
        "singleCaseGuide": None,
        "kinds": [
            {
                "kind": item["kind"],
                "warningCaseCount": item["warningCaseCount"],
                "warningLabels": item["warningLabels"],
            }
            for item in warning_kind_matrix["kinds"]
        ],
    }


def render_warning_kind_summary_markdown(report: dict) -> str:
    lines = [
        "# Warning Kind Summary",
        "",
        f"Kind Count: `{report['summary']['kindCount']}`",
        f"Case Count: `{report['summary']['caseCount']}`",
        "",
        "Kind | Warning Cases | Warning Labels",
        "--- | --- | ---",
    ]
    for item in report["kinds"]:
        lines.append(
            " | ".join(
                [
                    item["kind"],
                    str(item["warningCaseCount"]),
                    str(item["warningLabels"]),
                ]
            )
        )
    if report["singleCaseGuide"]:
        guide = report["singleCaseGuide"]
        lines.extend(
            [
                "",
                "## Single-Case Guide",
                "",
                f"- Case ID: `{guide['caseId']}`",
                f"- Recommended First Stop: `{guide['recommendedFirstStop']}`",
                f"- Why Open This: {guide['whyOpenThis']}",
            ]
        )
    return "\n".join(lines) + "\n"


def build_summary_index() -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "recommendedFirstStop": "outputs/warning_entry_summary.json",
        "whyOpenThis": "Start with the warning-entry summary because it is the quickest dashboard-style orientation to which cases currently carry lower-trust warning posture.",
        "entries": [
            {
                "kind": "warning_entry_summary",
                "jsonPath": "outputs/warning_entry_summary.json",
                "markdownPath": "outputs/warning_entry_summary.md",
                "description": "Compact case-first warning summary for dashboard-style audit views.",
                "priorityHint": "recommended",
                "whyOpenThis": "Open this first when you want the fastest compact view of which cases currently carry warning posture.",
            },
            {
                "kind": "warning_kind_summary",
                "jsonPath": "outputs/warning_kind_summary.json",
                "markdownPath": "outputs/warning_kind_summary.md",
                "description": "Compact kind-first warning summary for dashboard-style audit views.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the warning surface grouped by artifact kind instead of by case.",
            },
        ],
    }


def build_fit_index() -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "recommendedFirstStop": "outputs/fit_summary.json",
        "whyOpenThis": "Start with the fit summary because it is the quickest dashboard-style orientation to direct, analogical, and record-support posture across the current case set.",
        "entries": [
            {
                "kind": "fit_matrix",
                "jsonPath": "outputs/fit_matrix.json",
                "markdownPath": "outputs/fit_matrix.md",
                "description": "Cross-case fit-quality matrix with per-case direct, analogical, and record-support counts.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the fuller cross-case fit breakdown instead of the compact summary.",
            },
            {
                "kind": "fit_summary",
                "jsonPath": "outputs/fit_summary.json",
                "markdownPath": "outputs/fit_summary.md",
                "description": "Compact fit-quality summary for dashboard-style audit views.",
                "priorityHint": "recommended",
                "whyOpenThis": "Open this first when you want the quickest compact view of direct, analogical, and record-support posture.",
            },
            {
                "kind": "fit_findings",
                "jsonPath": "outputs/fit_findings.json",
                "markdownPath": "outputs/fit_findings.md",
                "description": "Repo-level findings report for analogical and record-support fit posture.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want case-level interpretation of fit risk rather than just fit counts.",
            },
            {
                "kind": "fit_findings_summary",
                "jsonPath": "outputs/fit_findings_summary.json",
                "markdownPath": "outputs/fit_findings_summary.md",
                "description": "Compact case-first summary of fit findings severity and posture.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want a lighter case-first fit findings view without the full report detail.",
            },
        ],
    }


def build_dashboard_index() -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "recommendedFirstStop": "outputs/dashboard_overview.json",
        "whyOpenThis": "Start with the dashboard overview because it is the single best top-level entry point into counts, warnings, fit posture, and the main discovery surfaces.",
        "entries": [
            {
                "kind": "outputs_index",
                "jsonPath": "outputs/index.json",
                "markdownPath": "outputs/index.md",
                "description": "Primary generated case index across all fixtures and package paths.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want the complete generated case inventory before drilling into audit surfaces.",
            },
            {
                "kind": "summary_index",
                "jsonPath": "outputs/summary_index.json",
                "markdownPath": "outputs/summary_index.md",
                "description": "Compact discovery file for lightweight warning summary artifacts.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the lightweight warning-summary discovery path instead of the broader dashboard surface.",
            },
            {
                "kind": "fit_index",
                "jsonPath": "outputs/fit_index.json",
                "markdownPath": "outputs/fit_index.md",
                "description": "Compact discovery file for fit-quality matrix and summary artifacts.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want the compact fit discovery path without scanning the full audit index.",
            },
            {
                "kind": "fit_findings",
                "jsonPath": "outputs/fit_findings.json",
                "markdownPath": "outputs/fit_findings.md",
                "description": "Repo-level findings report for analogical and record-support fit posture.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want immediate case-level fit-risk findings from the dashboard layer.",
            },
            {
                "kind": "fit_findings_summary",
                "jsonPath": "outputs/fit_findings_summary.json",
                "markdownPath": "outputs/fit_findings_summary.md",
                "description": "Compact case-first summary of fit findings severity and posture.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want a lighter fit findings view from the dashboard layer.",
            },
            {
                "kind": "refresh_state",
                "jsonPath": "outputs/.refresh_state.json",
                "markdownPath": "outputs/dashboard_overview.md",
                "description": "Snapshot refresh sentinel showing whether generation is running or complete.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want the current refresh state and timing without scanning the larger dashboard rollup.",
            },
            {
                "kind": "audit_index",
                "jsonPath": "outputs/audit_index.json",
                "markdownPath": "outputs/audit_index.md",
                "description": "Broader discovery file for the full repo-level audit surface.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the broadest audit discovery path across trust, warning, source, and fit reports.",
            },
            {
                "kind": "dashboard_overview",
                "jsonPath": "outputs/dashboard_overview.json",
                "markdownPath": "outputs/dashboard_overview.md",
                "description": "Single-file dashboard rollup of case counts, trust posture, warnings, and discovery entry points.",
                "priorityHint": "recommended",
                "whyOpenThis": "Open this first when you want the strongest single top-level dashboard rollup before following linked surfaces.",
            },
        ],
    }


def render_dashboard_index_markdown(report: dict) -> str:
    lines = [
        "# Dashboard Index",
        "",
        f"Recommended First Stop: `{report['recommendedFirstStop']}`",
        f"Why Open This: {report['whyOpenThis']}",
        "",
        "Priority | Kind | JSON | Markdown | Why Open This | Description",
        "--- | --- | --- | --- | --- | ---",
    ]
    for entry in report["entries"]:
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


def render_fit_index_markdown(report: dict) -> str:
    lines = [
        "# Fit Index",
        "",
        f"Recommended First Stop: `{report['recommendedFirstStop']}`",
        f"Why Open This: {report['whyOpenThis']}",
        "",
        "Priority | Kind | JSON | Markdown | Description",
        "--- | --- | --- | --- | ---",
    ]
    for entry in report["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_dashboard_overview(
    outputs_index: dict,
    trust_matrix: dict,
    warning_summary: dict,
    case_audit_matrix: dict,
    source_metadata_matrix: dict,
    fit_matrix: dict,
    fit_findings: dict,
) -> dict:
    highest_confidence = sorted(case_audit_matrix["cases"], key=lambda item: (-item["confidence"], item["caseId"]))[0]
    lowest_confidence = sorted(case_audit_matrix["cases"], key=lambda item: (item["confidence"], item["caseId"]))[0]
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "caseCount": len(outputs_index["cases"]),
            "violationCount": sum(1 for case in outputs_index["cases"] if case["activeOutcome"] == "violation"),
            "noViolationCount": sum(1 for case in outputs_index["cases"] if case["activeOutcome"] == "no_violation"),
            "warnedCaseCount": warning_summary["summary"]["warnedCaseCount"],
            "fullyVerifiedCount": sum(1 for case in trust_matrix["cases"] if case["authorityTrust"] == "fully_verified"),
            "mixedSupportCount": sum(1 for case in trust_matrix["cases"] if case["authorityTrust"] == "mixed_support"),
            "paraphraseHeavyCount": sum(1 for case in trust_matrix["cases"] if case["authorityTrust"] == "paraphrase_heavy"),
            "sourceVerifiedCount": source_metadata_matrix["summary"]["sourceVerifiedCount"],
            "sourceNormalizedCount": source_metadata_matrix["summary"]["sourceNormalizedCount"],
            "sourceStatus": (
                "All authority entries are sourceVerified and sourceNormalized across the current case set."
                if source_metadata_matrix["summary"]["sourceVerifiedCount"] == source_metadata_matrix["summary"]["authorityCount"]
                and source_metadata_matrix["summary"]["sourceNormalizedCount"] == source_metadata_matrix["summary"]["authorityCount"]
                else "Some authority entries still require source-verification or normalization cleanup."
            ),
            "directFitCount": fit_matrix["summary"]["directCount"],
            "analogicalFitCount": fit_matrix["summary"]["analogicalCount"],
            "recordSupportFitCount": fit_matrix["summary"]["recordSupportCount"],
            "analogicalCases": fit_findings["summary"]["analogicalCases"],
            "recordSupportCases": fit_findings["summary"]["recordSupportCases"],
            "fitStatus": (
                "The current case set includes record-support and analogical authority mappings."
                if fit_matrix["summary"]["recordSupportCount"] > 0
                else (
                    "The current case set includes analogical authority mappings."
                    if fit_matrix["summary"]["analogicalCount"] > 0
                    else "The current case set relies on direct authority mappings."
                )
            ),
        },
        "discovery": {
            "recommendedFirstStop": "outputs/dashboard_overview.json",
            "recommendedFirstStopWhyOpenThis": "Start here because this overview is the single best top-level entry point into counts, warnings, fit posture, and linked audit surfaces.",
            "refreshState": "outputs/.refresh_state.json",
            "refreshStateWhyOpenThis": "Open the refresh state when you want to confirm whether snapshot generation is currently running or has completed cleanly.",
            "outputsIndex": "outputs/index.json",
            "outputsIndexWhyOpenThis": "Open the outputs index to see the full generated case inventory across fixtures, packages, advocacy outputs, and memorandum outputs.",
            "summaryIndex": "outputs/summary_index.json",
            "summaryIndexWhyOpenThis": "Open the summary index when you want the compact warning-summary discovery path instead of the broader audit surface.",
            "fitIndex": "outputs/fit_index.json",
            "fitIndexWhyOpenThis": "Open the fit index when you want the compact discovery path for fit-quality matrix, summary, and findings artifacts.",
            "auditIndex": "outputs/audit_index.json",
            "auditIndexWhyOpenThis": "Open the audit index when you want the broadest repo-level audit discovery surface across trust, warning, source, and fit reports.",
            "dashboardIndex": "outputs/dashboard_index.json",
            "dashboardIndexWhyOpenThis": "Open the dashboard index when you want the top-level discovery file that links the repo's main human-facing and dashboard-style surfaces.",
            "fitSummary": "outputs/fit_summary.json",
            "fitSummaryWhyOpenThis": "Open the fit summary for the quickest compact rollup of direct, analogical, and record-support counts across the current case set.",
            "fitFindings": "outputs/fit_findings.json",
            "fitFindingsWhyOpenThis": "Open the fit findings report when you want case-level interpretation of analogical and record-support-heavy posture.",
            "fitFindingsSummary": "outputs/fit_findings_summary.json",
            "fitFindingsSummaryWhyOpenThis": "Open the fit findings summary when you want a lighter case-first fit-posture view without the full findings detail.",
        },
        "featured": {
            "highestConfidenceCaseId": highest_confidence["caseId"],
            "highestConfidence": highest_confidence["confidence"],
            "lowestConfidenceCaseId": lowest_confidence["caseId"],
            "lowestConfidence": lowest_confidence["confidence"],
            "primaryKinds": count_labels(case_audit_matrix["cases"], "primaryKind"),
            "warningLabels": count_labels(
                [case for case in case_audit_matrix["cases"] if case["warningLabel"]],
                "warningLabel",
            ),
            "singleCaseGuide": None,
        },
    }


def render_dashboard_overview_markdown(report: dict) -> str:
    lines = [
        "# Dashboard Overview",
        "",
        "## Summary",
        "",
        f"- Case Count: `{report['summary']['caseCount']}`",
        f"- Violation Count: `{report['summary']['violationCount']}`",
        f"- No-Violation Count: `{report['summary']['noViolationCount']}`",
        f"- Warned Case Count: `{report['summary']['warnedCaseCount']}`",
        f"- Fully Verified Count: `{report['summary']['fullyVerifiedCount']}`",
        f"- Mixed Support Count: `{report['summary']['mixedSupportCount']}`",
        f"- Paraphrase-Heavy Count: `{report['summary']['paraphraseHeavyCount']}`",
        f"- Source Verified Count: `{report['summary']['sourceVerifiedCount']}`",
        f"- Source Normalized Count: `{report['summary']['sourceNormalizedCount']}`",
        f"- Source Status: {report['summary']['sourceStatus']}",
        f"- Direct Fit Count: `{report['summary']['directFitCount']}`",
        f"- Analogical Fit Count: `{report['summary']['analogicalFitCount']}`",
        f"- Record-Support Fit Count: `{report['summary']['recordSupportFitCount']}`",
        f"- Analogical Cases: `{report['summary']['analogicalCases']}`",
        f"- Record-Support Cases: `{report['summary']['recordSupportCases']}`",
        f"- Fit Status: {report['summary']['fitStatus']}",
        "",
        "## Discovery",
        "",
        f"- Recommended First Stop: `{report['discovery']['recommendedFirstStop']}`",
        f"- Why Open This First: {report['discovery']['recommendedFirstStopWhyOpenThis']}",
        f"- Refresh State: `{report['discovery']['refreshState']}`",
        f"- Refresh State Why: {report['discovery']['refreshStateWhyOpenThis']}",
        f"- Outputs Index: `{report['discovery']['outputsIndex']}`",
        f"- Outputs Index Why: {report['discovery']['outputsIndexWhyOpenThis']}",
        f"- Summary Index: `{report['discovery']['summaryIndex']}`",
        f"- Summary Index Why: {report['discovery']['summaryIndexWhyOpenThis']}",
        f"- Fit Index: `{report['discovery']['fitIndex']}`",
        f"- Fit Index Why: {report['discovery']['fitIndexWhyOpenThis']}",
        f"- Audit Index: `{report['discovery']['auditIndex']}`",
        f"- Audit Index Why: {report['discovery']['auditIndexWhyOpenThis']}",
        f"- Dashboard Index: `{report['discovery']['dashboardIndex']}`",
        f"- Dashboard Index Why: {report['discovery']['dashboardIndexWhyOpenThis']}",
        f"- Fit Summary: `{report['discovery']['fitSummary']}`",
        f"- Fit Summary Why: {report['discovery']['fitSummaryWhyOpenThis']}",
        f"- Fit Findings: `{report['discovery']['fitFindings']}`",
        f"- Fit Findings Why: {report['discovery']['fitFindingsWhyOpenThis']}",
        f"- Fit Findings Summary: `{report['discovery']['fitFindingsSummary']}`",
        f"- Fit Findings Summary Why: {report['discovery']['fitFindingsSummaryWhyOpenThis']}",
        "",
        "## Featured",
        "",
        f"- Highest Confidence Case: `{report['featured']['highestConfidenceCaseId']}` ({report['featured']['highestConfidence']:.2f})",
        f"- Lowest Confidence Case: `{report['featured']['lowestConfidenceCaseId']}` ({report['featured']['lowestConfidence']:.2f})",
        f"- Primary Kinds: `{report['featured']['primaryKinds']}`",
        f"- Warning Labels: `{report['featured']['warningLabels']}`",
        "",
    ]
    if report["featured"]["singleCaseGuide"]:
        guide = report["featured"]["singleCaseGuide"]
        lines.extend(
            [
                "## Single-Case Guide",
                "",
                f"- Case ID: `{guide['caseId']}`",
                f"- Recommended First Stop: `{guide['recommendedFirstStop']}`",
                f"- Why Open This: {guide['whyOpenThis']}",
                "",
            ]
        )
    return "\n".join(lines)


def render_summary_index_markdown(report: dict) -> str:
    lines = [
        "# Summary Index",
        "",
        f"Recommended First Stop: `{report['recommendedFirstStop']}`",
        f"Why Open This: {report['whyOpenThis']}",
        "",
        "Priority | Kind | JSON | Markdown | Description",
        "--- | --- | --- | --- | ---",
    ]
    for entry in report["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def render_audit_index_markdown(report: dict) -> str:
    lines = [
        "# Audit Index",
        "",
        f"Recommended First Stop: `{report['recommendedFirstStop']}`",
        f"Why Open This: {report['whyOpenThis']}",
        "",
        "Priority | Kind | JSON | Markdown | Description",
        "--- | --- | --- | --- | ---",
    ]
    for entry in report["entries"]:
        lines.append(
            " | ".join(
                [
                    entry["priorityHint"],
                    entry["kind"],
                    entry["jsonPath"],
                    entry["markdownPath"],
                    entry["description"],
                ]
            )
        )
    return "\n".join(lines) + "\n"


def build_audit_index() -> dict:
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "recommendedFirstStop": "outputs/case_audit_matrix.json",
        "whyOpenThis": "Start with the case-audit matrix because it is the strongest joined repo-level view of confidence, trust, fit findings, warnings, and package posture.",
        "entries": [
            {
                "kind": "authority_summary_matrix",
                "jsonPath": "outputs/authority_summary_matrix.json",
                "markdownPath": "outputs/authority_summary_matrix.md",
                "description": "Cross-case authority support counts by status and reasoning bucket.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want cross-case authority support counts before reading findings prose.",
            },
            {
                "kind": "authority_findings",
                "jsonPath": "outputs/authority_findings.json",
                "markdownPath": "outputs/authority_findings.md",
                "description": "Repo-level findings report for authority trust and support quality.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want case-level authority-support warnings rather than just support counts.",
            },
            {
                "kind": "source_findings",
                "jsonPath": "outputs/source_findings.json",
                "markdownPath": "outputs/source_findings.md",
                "description": "Repo-level findings report for normalized versus unnormalized source metadata.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want source-hardening findings rather than the raw source metadata rollup.",
            },
            {
                "kind": "source_metadata_matrix",
                "jsonPath": "outputs/source_metadata_matrix.json",
                "markdownPath": "outputs/source_metadata_matrix.md",
                "description": "Cross-case rollup of sourceVerified and sourceNormalized authority metadata.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the raw cross-case source-hardening counts and unnormalized IDs.",
            },
            {
                "kind": "fit_matrix",
                "jsonPath": "outputs/fit_matrix.json",
                "markdownPath": "outputs/fit_matrix.md",
                "description": "Cross-case fit-quality matrix showing direct, analogical, and record-support counts.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the fuller cross-case fit breakdown instead of the compact fit summary.",
            },
            {
                "kind": "fit_summary",
                "jsonPath": "outputs/fit_summary.json",
                "markdownPath": "outputs/fit_summary.md",
                "description": "Compact fit-quality summary for dashboard-style audit views.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want a compact fit rollup from the broader audit surface.",
            },
            {
                "kind": "fit_findings",
                "jsonPath": "outputs/fit_findings.json",
                "markdownPath": "outputs/fit_findings.md",
                "description": "Repo-level findings report for direct, analogical, and record-support fit posture.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want case-level fit findings from the broader audit surface.",
            },
            {
                "kind": "fit_findings_summary",
                "jsonPath": "outputs/fit_findings_summary.json",
                "markdownPath": "outputs/fit_findings_summary.md",
                "description": "Compact case-first summary of fit findings severity and posture.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want a lighter fit findings view from the audit surface.",
            },
            {
                "kind": "trust_matrix",
                "jsonPath": "outputs/trust_matrix.json",
                "markdownPath": "outputs/trust_matrix.md",
                "description": "Cross-case trust overview with primary artifact and warning counts.",
                "priorityHint": "primary",
                "whyOpenThis": "Open this when you want the clearest cross-case trust overview before drilling into warning details.",
            },
            {
                "kind": "warning_summary",
                "jsonPath": "outputs/warning_summary.json",
                "markdownPath": "outputs/warning_summary.md",
                "description": "Warned-case summary across all lower-trust packages.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the compact warned-case rollup instead of the more detailed warning matrices.",
            },
            {
                "kind": "warning_label_matrix",
                "jsonPath": "outputs/warning_label_matrix.json",
                "markdownPath": "outputs/warning_label_matrix.md",
                "description": "Label-sliced warning summaries for mixed-support and paraphrase-heavy cases.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want warning posture sliced directly by label.",
            },
            {
                "kind": "warning_entry_matrix",
                "jsonPath": "outputs/warning_entry_matrix.json",
                "markdownPath": "outputs/warning_entry_matrix.md",
                "description": "Per-case warned artifact kinds and warning-label counts across package entries.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want to see which artifact kinds are warned inside each package.",
            },
            {
                "kind": "warning_entry_summary",
                "jsonPath": "outputs/warning_entry_summary.json",
                "markdownPath": "outputs/warning_entry_summary.md",
                "description": "Compact ranked warning-entry summary without per-case warned-kind lists.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want the lightest case-first warning summary from the audit surface.",
            },
            {
                "kind": "warning_kind_matrix",
                "jsonPath": "outputs/warning_kind_matrix.json",
                "markdownPath": "outputs/warning_kind_matrix.md",
                "description": "Artifact-kind-first warning matrix showing which warned cases include each kind.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want the warning surface grouped by artifact kind instead of by case.",
            },
            {
                "kind": "warning_kind_summary",
                "jsonPath": "outputs/warning_kind_summary.json",
                "markdownPath": "outputs/warning_kind_summary.md",
                "description": "Compact ranked warning-kind summary without per-case detail rows.",
                "priorityHint": "supporting",
                "whyOpenThis": "Open this when you want the lightest kind-first warning summary.",
            },
            {
                "kind": "summary_index",
                "jsonPath": "outputs/summary_index.json",
                "markdownPath": "outputs/summary_index.md",
                "description": "Compact discovery file for lightweight audit summary artifacts.",
                "priorityHint": "secondary",
                "whyOpenThis": "Open this when you want the lightweight warning-summary discovery path from within the broader audit surface.",
            },
            {
                "kind": "case_audit_matrix",
                "jsonPath": "outputs/case_audit_matrix.json",
                "markdownPath": "outputs/case_audit_matrix.md",
                "description": "Joined case-level audit matrix with confidence, trust, primary artifact, and warning posture.",
                "priorityHint": "recommended",
                "whyOpenThis": "Open this first when you want the strongest joined repo-level audit view before following narrower reports.",
            },
        ],
    }


def build_case_audit_matrix(outputs_index: dict) -> dict:
    cases = []
    for item in outputs_index["cases"]:
        brief_index = json.loads((ROOT / item["packagePath"] / "brief_index.json").read_text())
        primary_entry = next(
            (entry for entry in brief_index["entries"] if entry["kind"] == brief_index["primaryKind"]),
            None,
        )
        cases.append(
            {
                "caseId": item["caseId"],
                "branch": item["branch"],
                "activeOutcome": item["activeOutcome"],
                "confidence": item["confidence"],
                "authorityTrust": brief_index["authorityTrust"]["label"],
                "primaryKind": brief_index["primaryKind"],
                "primaryWhy": (
                    primary_entry["whyOpenThis"] if primary_entry else brief_index["whyOpenThis"]
                ),
                "hasWarnings": brief_index["warningSummary"]["hasWarnings"],
                "warningEntryCount": brief_index["warningSummary"]["warningEntryCount"],
                "warningLabel": brief_index["warningLabelSummary"]["warningLabel"],
                "fitFinding": brief_index["fitFindingSummary"]["fitFinding"],
                "packagePath": item["packagePath"],
            }
        )
    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "cases": cases,
    }


def render_case_audit_matrix_markdown(report: dict) -> str:
    lines = [
        "# Case Audit Matrix",
        "",
        "Case ID | Branch | Outcome | Confidence | Trust | Fit Finding | Primary | Primary Why | Warnings | Warning Count | Warning Label | Package",
        "--- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | ---",
    ]
    for case in report["cases"]:
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


def main() -> int:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    started_at = datetime.now(timezone.utc).isoformat()
    _write_refresh_state("running", started_at)
    for fixture_name in FIXTURE_NAMES:
        export_package(ROOT / "fixtures" / fixture_name)
    outputs_index = build_outputs_index()
    _write_json_atomic(ROOT / "outputs" / "index.json", outputs_index)
    _write_text_atomic(ROOT / "outputs" / "index.md", render_outputs_index_markdown(outputs_index))
    trust_matrix = build_trust_matrix(outputs_index)
    warning_summary = build_warning_summary_data(ROOT)
    case_audit_matrix = build_case_audit_matrix(outputs_index)
    source_metadata_matrix = build_source_metadata_matrix(outputs_index)
    fit_matrix = build_fit_matrix(outputs_index)
    _write_json_atomic(ROOT / "outputs" / "source_metadata_matrix.json", source_metadata_matrix)
    _write_text_atomic(ROOT / "outputs" / "source_metadata_matrix.md", render_source_metadata_matrix_markdown(source_metadata_matrix))
    _write_json_atomic(ROOT / "outputs" / "fit_matrix.json", fit_matrix)
    _write_text_atomic(ROOT / "outputs" / "fit_matrix.md", render_fit_matrix_markdown(fit_matrix))
    fit_summary = build_fit_summary(fit_matrix)
    _write_json_atomic(ROOT / "outputs" / "fit_summary.json", fit_summary)
    _write_text_atomic(ROOT / "outputs" / "fit_summary.md", render_fit_summary_markdown(fit_summary))
    fit_findings = build_fit_findings_report(fit_matrix)
    _write_json_atomic(ROOT / "outputs" / "fit_findings.json", fit_findings)
    _write_text_atomic(ROOT / "outputs" / "fit_findings.md", render_fit_findings_markdown(fit_findings) + "\n")
    fit_findings_summary = build_fit_findings_summary(fit_findings)
    _write_json_atomic(ROOT / "outputs" / "fit_findings_summary.json", fit_findings_summary)
    _write_text_atomic(ROOT / "outputs" / "fit_findings_summary.md", render_fit_findings_summary_markdown(fit_findings_summary))
    dashboard_overview = build_dashboard_overview(
        outputs_index,
        trust_matrix,
        warning_summary,
        case_audit_matrix,
        source_metadata_matrix,
        fit_matrix,
        fit_findings,
    )
    _write_json_atomic(ROOT / "outputs" / "dashboard_overview.json", dashboard_overview)
    _write_text_atomic(ROOT / "outputs" / "dashboard_overview.md", render_dashboard_overview_markdown(dashboard_overview))
    authority_summary_matrix = build_authority_summary_matrix(ROOT)
    _write_json_atomic(ROOT / "outputs" / "authority_summary_matrix.json", authority_summary_matrix)
    _write_text_atomic(ROOT / "outputs" / "authority_summary_matrix.md", render_authority_summary_matrix_markdown(ROOT))
    authority_findings = build_authority_findings_report(authority_summary_matrix)
    _write_json_atomic(ROOT / "outputs" / "authority_findings.json", authority_findings)
    _write_text_atomic(ROOT / "outputs" / "authority_findings.md", render_authority_findings_markdown(authority_findings) + "\n")
    source_findings = build_source_findings_report(source_metadata_matrix)
    _write_json_atomic(ROOT / "outputs" / "source_findings.json", source_findings)
    _write_text_atomic(ROOT / "outputs" / "source_findings.md", render_source_findings_markdown(source_findings) + "\n")
    _write_json_atomic(ROOT / "outputs" / "warning_summary.json", warning_summary)
    _write_text_atomic(ROOT / "outputs" / "warning_summary.md", render_warning_summary(ROOT))
    warning_label_matrix = build_warning_label_matrix()
    _write_json_atomic(ROOT / "outputs" / "warning_label_matrix.json", warning_label_matrix)
    _write_text_atomic(ROOT / "outputs" / "warning_label_matrix.md", render_warning_label_matrix_markdown(warning_label_matrix) + "\n")
    warning_entry_matrix = build_warning_entry_matrix(outputs_index)
    _write_json_atomic(ROOT / "outputs" / "warning_entry_matrix.json", warning_entry_matrix)
    _write_text_atomic(ROOT / "outputs" / "warning_entry_matrix.md", render_warning_entry_matrix_markdown(warning_entry_matrix))
    warning_entry_summary = build_warning_entry_summary(warning_entry_matrix)
    _write_json_atomic(ROOT / "outputs" / "warning_entry_summary.json", warning_entry_summary)
    _write_text_atomic(ROOT / "outputs" / "warning_entry_summary.md", render_warning_entry_summary_markdown(warning_entry_summary))
    warning_kind_matrix = build_warning_kind_matrix(outputs_index)
    _write_json_atomic(ROOT / "outputs" / "warning_kind_matrix.json", warning_kind_matrix)
    _write_text_atomic(ROOT / "outputs" / "warning_kind_matrix.md", render_warning_kind_matrix_markdown(warning_kind_matrix))
    warning_kind_summary = build_warning_kind_summary(warning_kind_matrix)
    _write_json_atomic(ROOT / "outputs" / "warning_kind_summary.json", warning_kind_summary)
    _write_text_atomic(ROOT / "outputs" / "warning_kind_summary.md", render_warning_kind_summary_markdown(warning_kind_summary))
    summary_index = build_summary_index()
    _write_json_atomic(ROOT / "outputs" / "summary_index.json", summary_index)
    _write_text_atomic(ROOT / "outputs" / "summary_index.md", render_summary_index_markdown(summary_index))
    fit_index = build_fit_index()
    _write_json_atomic(ROOT / "outputs" / "fit_index.json", fit_index)
    _write_text_atomic(ROOT / "outputs" / "fit_index.md", render_fit_index_markdown(fit_index))
    dashboard_index = build_dashboard_index()
    _write_json_atomic(ROOT / "outputs" / "dashboard_index.json", dashboard_index)
    _write_text_atomic(ROOT / "outputs" / "dashboard_index.md", render_dashboard_index_markdown(dashboard_index))
    audit_index = build_audit_index()
    _write_json_atomic(ROOT / "outputs" / "audit_index.json", audit_index)
    _write_text_atomic(ROOT / "outputs" / "audit_index.md", render_audit_index_markdown(audit_index))
    _write_json_atomic(ROOT / "outputs" / "case_audit_matrix.json", case_audit_matrix)
    _write_text_atomic(ROOT / "outputs" / "case_audit_matrix.md", render_case_audit_matrix_markdown(case_audit_matrix))
    for fixture_name in FIXTURE_NAMES:
        fixture_path = ROOT / "fixtures" / fixture_name
        payload = json.loads(fixture_path.read_text())
        case_id = payload["caseId"]
        result = evaluate_case(payload)
        export_dir = export_package(fixture_path)
        package_snapshot = build_package_snapshot(export_dir)
        advocacy_snapshot = generate_advocacy_outputs(payload)
        advocacy_bundle_snapshot = generate_advocacy_bundle(payload)
        memorandum_snapshot = generate_memorandum_bundle(payload)
        write_memorandum_outputs(fixture_path, memorandum_snapshot, build_dependency_citations_jsonld(payload))

        result_path = SNAPSHOT_DIR / f"{case_id}.result.snapshot.json"
        package_path = SNAPSHOT_DIR / f"{case_id}.package.snapshot.json"
        advocacy_path = SNAPSHOT_DIR / f"{case_id}.advocacy.snapshot.json"
        advocacy_bundle_path = SNAPSHOT_DIR / f"{case_id}.advocacy_bundle.snapshot.json"
        memorandum_path = SNAPSHOT_DIR / f"{case_id}.memorandum.snapshot.json"

        _write_json_atomic(result_path, result)
        _write_json_atomic(package_path, package_snapshot)
        _write_json_atomic(advocacy_path, advocacy_snapshot)
        _write_json_atomic(advocacy_bundle_path, advocacy_bundle_snapshot)
        _write_json_atomic(memorandum_path, memorandum_snapshot)

        print(result_path)
        print(package_path)
        print(advocacy_path)
        print(advocacy_bundle_path)
        print(memorandum_path)
    _write_json_atomic(ROOT / "outputs" / "trust_matrix.json", trust_matrix)
    _write_text_atomic(ROOT / "outputs" / "trust_matrix.md", render_trust_matrix_markdown(trust_matrix))
    _sanity_check_refresh_outputs()
    _write_refresh_state("complete", started_at, datetime.now(timezone.utc).isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
