#!/usr/bin/env python3
"""Dependency-free regression checks for workspace2."""

import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from jsonschema import Draft202012Validator

from engine.evaluate_case import evaluate_case
from engine.export_artifacts import export_package
from engine.generate_advocacy import generate_advocacy_bundle, generate_advocacy_outputs
from engine.generate_memorandum import generate_memorandum_bundle, write_memorandum_outputs
from engine.legal_grounding import build_dependency_citations_jsonld
from engine.print_case_matrix import (
    build_audit_index_data,
    build_authority_findings_data,
    build_authority_research_note_data,
    build_authority_review_data,
    build_authority_review_summary,
    build_authority_summary_matrix,
    build_case_matrix_data,
    build_case_audit_matrix_data,
    build_trust_matrix_data,
    build_dashboard_index_data,
    build_dashboard_overview_data,
    build_fit_findings_data,
    build_fit_findings_summary_data,
    build_fit_index_data,
    build_fit_matrix_data,
    build_fit_summary_data,
    build_refresh_state_data,
    build_source_metadata_matrix_data,
    build_warning_entry_matrix_data,
    build_warning_entry_summary_data,
    build_warning_kind_matrix_data,
    build_warning_kind_summary_data,
    build_warning_label_matrix_data,
    build_warning_summary_data,
    build_summary_index_data,
    describe_artifact_kind,
    list_artifact_kinds,
    render_authority_findings,
    render_authority_research_note,
    render_authority_review,
    render_authority_review_summary,
    render_authority_summary_matrix,
    render_authority_summary_matrix_markdown,
    render_audit_index,
    render_case_audit_matrix,
    render_case_detail,
    render_case_matrix,
    render_dashboard_index,
    render_dashboard_overview,
    render_fit_findings,
    render_fit_findings_summary,
    render_fit_index,
    render_fit_matrix,
    render_fit_summary,
    render_refresh_state,
    render_source_findings,
    render_source_metadata_matrix,
    render_summary_index,
    render_trust_matrix,
    render_warning_entry_matrix,
    render_warning_entry_summary,
    render_warning_kind_matrix,
    render_warning_kind_summary,
    render_warning_label_matrix,
    render_warning_summary,
    render_top_artifacts,
    resolve_artifact_path,
    resolve_primary_artifact_path,
    fail_if_refresh_running,
    prepend_refresh_warning,
    wait_for_refresh_complete,
)


ROOT = Path(__file__).resolve().parent.parent
FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures"
SNAPSHOT_DIR = Path(__file__).resolve().parent / "snapshots"
SCHEMA_DIR = ROOT / "schema"
PACKAGE_DIR = ROOT / "outputs" / "live_in_aide_case_001_package"


def load_fixture(name: str):
    return json.loads((FIXTURE_DIR / name).read_text())


def load_snapshot(name: str):
    return json.loads((SNAPSHOT_DIR / name).read_text())


def load_schema(name: str):
    return json.loads((SCHEMA_DIR / name).read_text())


def inline_case_schema_refs():
    case_schema = deepcopy(load_schema("case.schema.json"))
    authority_schema = load_schema("authority.schema.json")
    case_schema["properties"]["authorities"]["items"] = authority_schema
    return case_schema


def validate_with_schema(instance, schema):
    Draft202012Validator(schema).validate(instance)


def build_package_snapshot(export_dir: Path):
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


def validate_package_json_files(export_dir: Path):
    validate_with_schema(
        json.loads((export_dir / "context.json").read_text()),
        load_schema("context.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "manifest.json").read_text()),
        load_schema("manifest.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "decision_tree.json").read_text()),
        load_schema("decision_tree.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "dependency_graph.json").read_text()),
        load_schema("dependency_graph.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "tests.json").read_text()),
        load_schema("tests_export.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "summary.json").read_text()),
        load_schema("summary.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "advocacy_bundle.json").read_text()),
        load_schema("advocacy_bundle.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "brief_index.json").read_text()),
        load_schema("brief_index.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "authority_review.json").read_text()),
        load_schema("authority_review.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "authority_research_note.json").read_text()),
        load_schema("authority_research_note.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "authority_summary.json").read_text()),
        load_schema("authority_summary.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "dependency_citations.jsonld").read_text()),
        load_schema("dependency_citations.schema.json"),
    )
    validate_with_schema(
        json.loads((export_dir / "case_instance.jsonld").read_text()),
        load_schema("case_instance.schema.json"),
    )


def load_outputs_index():
    return json.loads((ROOT / "outputs" / "index.json").read_text())


def test_fixture_matches_schema():
    fixture = load_fixture("live_in_aide_case.json")
    validate_with_schema(fixture, inline_case_schema_refs())


def test_generated_positive_result_matches_schema():
    result = evaluate_case(load_fixture("live_in_aide_case.json"))
    validate_with_schema(result, load_schema("result.schema.json"))


def test_generated_positive_advocacy_bundle_matches_schema():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case.json"))
    validate_with_schema(bundle, load_schema("advocacy_bundle.schema.json"))
    assert bundle["citations"]["hearing_script"]["authorityDetails"][0]["sourceUrl"]
    assert bundle["citations"]["hearing_script"]["authorityDetails"][0]["excerptKind"] == "verified_quote"
    assert bundle["citations"]["hearing_script"]["authorityDetails"][0]["fitKind"] in {"direct", "analogical", "record_support"}
    assert bundle["meta"]["authorityTrust"]["label"] == "fully_verified"
    assert "Authority grounding note:" in bundle["texts"]["hearing_script"]


def test_authority_schema_rejects_missing_weight():
    schema = load_schema("authority.schema.json")
    invalid = {
        "id": "bad_authority",
        "label": "Bad Authority",
        "kind": "case",
    }
    try:
        validate_with_schema(invalid, schema)
    except Exception:
        return
    raise AssertionError("authority schema should reject objects missing required weight")


def test_context_schema_rejects_missing_type_alias():
    schema = load_schema("context.schema.json")
    invalid = {
        "@context": {
            "id": "@id",
            "Person": "https://example.org/legal/Person",
        }
    }
    try:
        validate_with_schema(invalid, schema)
    except Exception:
        return
    raise AssertionError("context schema should reject contexts missing required type alias")


def test_positive_constructive_denial_case():
    result = evaluate_case(load_fixture("live_in_aide_case.json"))
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case.json"))
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case.json"))
    assert result["branch"] == "constructive_denial"
    assert result["policy"]["privacy_mode"] == "inferred_from_living_room_sleeping"
    assert result["outcome"]["sleepInterruption"] is True
    assert result["outcome"]["necessary"] is True
    assert result["outcome"]["reasonable"] is True
    assert result["outcome"]["dutyToGrant"] is True
    assert result["outcome"]["constructiveDenial"] is True
    assert result["outcome"]["violation"] is True
    assert result["missingEvidence"] == []
    assert result["authoritySupport"]["reasonable"]
    assert result["evidenceSupport"]["medical_verification"]
    assert result["findingEvidence"]["reasonable"] == ["evidence:medical_verification"]
    assert result["findingEvents"]["reasonable"] == ["evt:t2"]
    assert result["findingAuthorities"]["violation"]
    assert result["provenance"]["reasonable"]["active"] is True
    assert result["provenance"]["reasonable"]["evidenceIds"] == ["evidence:medical_verification"]
    assert result["provenance"]["constructiveDenial"]["eventIds"] == ["evt:t3", "evt:t4", "evt:t5"]
    assert result["provenance"]["violation"]["authorityIds"]
    assert result["provenance"]["sleepInterruption"]["proofSteps"]
    assert result["timeline"][0]["event"] == "request_accommodation"
    assert "constructive denial" in result["narrative"].lower()
    assert "Supporting authorities" in result["explanations"]["violation"]
    assert "cure constructive denial" in outputs["demand_letter"].lower()
    assert "resolved without further escalation" in outputs["demand_letter"].lower()
    assert bundle["meta"]["branch"] == "constructive_denial"
    assert bundle["meta"]["placeholders"]["requested_remedy"] == "[Approve a separate bedroom for the live-in aide]"


def test_snapshot_matches_current_result():
    result = evaluate_case(load_fixture("live_in_aide_case.json"))
    snapshot = load_snapshot("live_in_aide_case_001.result.snapshot.json")
    assert result == snapshot


def test_exported_package_matches_snapshot():
    export_dir = export_package(FIXTURE_DIR / "live_in_aide_case.json")
    validate_package_json_files(export_dir)
    current_snapshot = build_package_snapshot(export_dir)
    saved_snapshot = load_snapshot("live_in_aide_case_001.package.snapshot.json")
    assert current_snapshot == saved_snapshot
    assert "manifest.json" in current_snapshot
    assert "event_calculus.pl" in current_snapshot
    assert "summary.json" in current_snapshot
    assert "brief_index.json" in current_snapshot
    assert "dependency_citations.jsonld" in current_snapshot
    assert "authority_review.json" in current_snapshot
    assert "authority_review.md" in current_snapshot
    assert "authority_research_note.json" in current_snapshot
    assert "authority_research_note.md" in current_snapshot
    assert "authority_summary.json" in current_snapshot
    assert "advocacy_bundle.json" in current_snapshot
    assert "hearing_script.md" in current_snapshot
    assert "complaint_outline.md" in current_snapshot
    assert "demand_letter.md" in current_snapshot
    assert "negotiation_summary.md" in current_snapshot
    assert "memorandum.json" in current_snapshot
    assert "memorandum.md" in current_snapshot
    assert "memorandum_of_law.pdf" in current_snapshot
    assert current_snapshot["manifest.json"]["caseId"] == "live_in_aide_case_001"
    assert current_snapshot["manifest.json"]["branch"] == "constructive_denial"
    assert current_snapshot["manifest.json"]["authorityTrust"]["label"] == "fully_verified"
    assert current_snapshot["manifest.json"]["sourceSummary"]["authorityCount"] == 5
    assert current_snapshot["manifest.json"]["sourceSummary"]["sourceVerifiedCount"] == 5
    assert current_snapshot["manifest.json"]["sourceSummary"]["sourceNormalizedCount"] == 5
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["manifest.json"]["sourceSummary"]["sourceStatus"] == "All authority entries are sourceVerified and sourceNormalized."
    assert current_snapshot["manifest.json"]["fitSummary"]["authorityCount"] == 5
    assert current_snapshot["manifest.json"]["fitSummary"]["directCount"] == 3
    assert current_snapshot["manifest.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["manifest.json"]["fitSummary"]["recordSupportCount"] == 0
    assert current_snapshot["manifest.json"]["fitSummary"]["fitStatus"] == "This package includes analogical authority mappings."
    assert current_snapshot["manifest.json"]["fitFindingSummary"]["hasFitFinding"] is True
    assert current_snapshot["manifest.json"]["fitFindingSummary"]["fitFinding"] == "analogical_support"
    assert current_snapshot["manifest.json"]["recommendedFirstStop"] == "memorandum_of_law.pdf"
    assert (
        current_snapshot["manifest.json"]["whyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert any(
        item["path"] == "memorandum_of_law.pdf"
        and item["whyOpenThis"] == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        for item in current_snapshot["manifest.json"]["artifactGuidance"]
    )
    assert any(
        item["path"] == "brief_index.json"
        and item["whyOpenThis"] == "Open this when you want the package-local discovery index with entry priorities, warnings, and rationale."
        for item in current_snapshot["manifest.json"]["artifactGuidance"]
    )
    assert "manifest.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "summary.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "brief_index.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "advocacy_bundle.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "demand_letter.md" in current_snapshot["manifest.json"]["artifacts"]
    assert "dependency_citations.jsonld" in current_snapshot["manifest.json"]["artifacts"]
    assert "authority_review.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "authority_review.md" in current_snapshot["manifest.json"]["artifacts"]
    assert "authority_research_note.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "authority_research_note.md" in current_snapshot["manifest.json"]["artifacts"]
    assert "authority_summary.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "memorandum.json" in current_snapshot["manifest.json"]["artifacts"]
    assert "memorandum.md" in current_snapshot["manifest.json"]["artifacts"]
    assert "memorandum_of_law.pdf" in current_snapshot["manifest.json"]["artifacts"]
    assert current_snapshot["decision_tree.json"]["decisionTree"]["branch"] == "constructive_denial"
    assert current_snapshot["decision_tree.json"]["decisionTree"]["activeOutcome"] == "violation"
    assert current_snapshot["dependency_graph.json"]["branch"] == "constructive_denial"
    assert current_snapshot["dependency_graph.json"]["activeOutcome"] == "violation"
    assert any(item["type"] == "DependencySupport" for item in current_snapshot["dependency_citations.jsonld"]["@graph"])
    assert current_snapshot["memorandum.json"]["meta"]["branch"] == "constructive_denial"
    assert current_snapshot["memorandum_of_law.pdf"]["kind"] == "binary"
    assert current_snapshot["memorandum_of_law.pdf"]["size"] > 1000
    assert "Authority Trust: `fully_verified`" in current_snapshot["README.md"]
    assert "Source Verified Count: `5`" in current_snapshot["README.md"]
    assert "Source Normalized Count: `5`" in current_snapshot["README.md"]
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in current_snapshot["README.md"]
    assert "Direct Fit Count: `3`" in current_snapshot["README.md"]
    assert "Analogical Fit Count: `2`" in current_snapshot["README.md"]
    assert "Record-Support Fit Count: `0`" in current_snapshot["README.md"]
    assert "Fit Status: This package includes analogical authority mappings." in current_snapshot["README.md"]
    assert "Fit Finding: `analogical_support`" in current_snapshot["README.md"]
    assert "Recommended First Stop: `memorandum_of_law.pdf`" in current_snapshot["README.md"]
    assert (
        "Why Open This: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        in current_snapshot["README.md"]
    )
    assert "Artifact Guide:" in current_snapshot["README.md"]
    assert (
        "- `memorandum_of_law.pdf`: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        in current_snapshot["README.md"]
    )
    assert (
        "- `brief_index.json`: Open this when you want the package-local discovery index with entry priorities, warnings, and rationale."
        in current_snapshot["README.md"]
    )
    assert "all currently attached authority support is marked as verified_quote" in current_snapshot["README.md"].lower()
    assert current_snapshot["brief_index.json"]["branch"] == "constructive_denial"
    assert current_snapshot["brief_index.json"]["activeOutcome"] == "violation"
    assert current_snapshot["brief_index.json"]["primaryKind"] == "memorandum_pdf"
    assert current_snapshot["brief_index.json"]["recommendedFirstStop"] == "memorandum_of_law.pdf"
    assert (
        current_snapshot["brief_index.json"]["whyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert current_snapshot["brief_index.json"]["authorityTrust"]["label"] == "fully_verified"
    assert current_snapshot["brief_index.json"]["sourceSummary"]["authorityCount"] == 5
    assert current_snapshot["brief_index.json"]["sourceSummary"]["sourceVerifiedCount"] == 5
    assert current_snapshot["brief_index.json"]["sourceSummary"]["sourceNormalizedCount"] == 5
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["brief_index.json"]["sourceSummary"]["sourceStatus"] == "All authority entries are sourceVerified and sourceNormalized."
    assert current_snapshot["brief_index.json"]["fitSummary"]["authorityCount"] == 5
    assert current_snapshot["brief_index.json"]["fitSummary"]["directCount"] == 3
    assert current_snapshot["brief_index.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["brief_index.json"]["fitSummary"]["recordSupportCount"] == 0
    assert current_snapshot["brief_index.json"]["fitSummary"]["fitStatus"] == "This package includes analogical authority mappings."
    assert current_snapshot["brief_index.json"]["fitFindingSummary"]["hasFitFinding"] is True
    assert current_snapshot["brief_index.json"]["fitFindingSummary"]["fitFinding"] == "analogical_support"
    assert current_snapshot["brief_index.json"]["warningSummary"]["hasWarnings"] is False
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningEntryCount"] == 0
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningCounts"] == {}
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["hasWarningLabel"] is False
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningLabel"] is None
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningEntryCount"] == 0
    assert all("trustWarning" not in item for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["priority"] == 1 and item["kind"] == "memorandum_pdf" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "memorandum_pdf" and item["priorityLabel"] == "primary" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(
        item["kind"] == "memorandum_pdf"
        and item["whyOpenThis"] == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert any(
        item["kind"] == "summary"
        and item["whyOpenThis"] == "Open this when you want the quickest branch-aware orientation for constructive_denial review."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert any(item["kind"] == "advocacy_bundle" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "demand_letter_markdown" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "memorandum_pdf" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "dependency_citations" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "authority_review" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "authority_research_note" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "authority_summary" for item in current_snapshot["brief_index.json"]["entries"])
    assert current_snapshot["advocacy_bundle.json"]["meta"]["branch"] == "constructive_denial"
    assert current_snapshot["advocacy_bundle.json"]["citations"]["hearing_script"]["authorityDetails"][0]["sourceUrl"]
    assert current_snapshot["authority_review.json"]["authorities"][0]["supportStatus"] == "verified_quote"
    assert current_snapshot["authority_review.json"]["authorities"][0]["sourceVerified"] is True
    assert current_snapshot["authority_research_note.json"]["entryCount"] == 5
    assert current_snapshot["authority_research_note.json"]["entries"][0]["sourceReference"]
    assert current_snapshot["authority_summary.json"]["authorityCount"] == 5
    assert current_snapshot["authority_summary.json"]["statusCounts"]["verified_quote"] == 5
    assert current_snapshot["summary.json"]["branch"] == "constructive_denial"
    assert current_snapshot["summary.json"]["activeOutcome"] == "violation"
    assert current_snapshot["tests.json"][0]["branch"] == "constructive_denial"


def test_outputs_index_matches_schema_and_cases():
    index = load_outputs_index()
    validate_with_schema(index, load_schema("index.schema.json"))
    assert len(index["cases"]) == 4
    by_case = {item["caseId"]: item for item in index["cases"]}
    assert by_case["live_in_aide_case_001"]["branch"] == "constructive_denial"
    assert by_case["live_in_aide_case_effective_accommodation_001"]["branch"] == "effective_accommodation"
    assert by_case["live_in_aide_case_no_violation_001"]["branch"] == "evidentiary_gap"
    assert by_case["live_in_aide_case_undue_burden_001"]["branch"] == "undue_burden_constructive_denial"
    assert by_case["live_in_aide_case_effective_accommodation_001"]["activeOutcome"] == "no_violation"
    assert by_case["live_in_aide_case_001"]["resultPath"] == "outputs/live_in_aide_case_001.result.json"
    assert by_case["live_in_aide_case_001"]["memorandumPath"] == "outputs/live_in_aide_case_memorandum"


def test_outputs_authority_summary_matrix_matches_schema_and_cases():
    matrix = json.loads((ROOT / "outputs" / "authority_summary_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("authority_summary_matrix.schema.json"))
    assert len(matrix["cases"]) == 4
    by_case = {item["caseId"]: item for item in matrix["cases"]}
    assert by_case["live_in_aide_case_001"]["branch"] == "constructive_denial"
    assert by_case["live_in_aide_case_effective_accommodation_001"]["branch"] == "effective_accommodation"
    assert by_case["live_in_aide_case_no_violation_001"]["branch"] == "evidentiary_gap"
    assert by_case["live_in_aide_case_undue_burden_001"]["branch"] == "undue_burden_constructive_denial"
    assert by_case["live_in_aide_case_001"]["authorityCount"] == 5
    assert by_case["live_in_aide_case_001"]["statusCounts"]["verified_quote"] == 5
    assert by_case["live_in_aide_case_effective_accommodation_001"]["statusCounts"]["paraphrase"] == 2
    assert by_case["live_in_aide_case_no_violation_001"]["statusCounts"]["paraphrase"] == 3
    assert by_case["live_in_aide_case_undue_burden_001"]["statusCounts"]["paraphrase"] == 1
    matrix_markdown = (ROOT / "outputs" / "authority_summary_matrix.md").read_text()
    assert matrix_markdown.startswith("# Authority Summary Matrix")
    assert "live_in_aide_case_001 | constructive_denial | 5 | no | any | verified_quote=5" in matrix_markdown


def test_outputs_authority_findings_report_matches_schema_and_expectations():
    report = json.loads((ROOT / "outputs" / "authority_findings.json").read_text())
    validate_with_schema(report, load_schema("authority_findings.schema.json"))
    assert report["summary"]["caseCount"] == 4
    assert report["summary"]["fullyVerifiedCases"] == 1
    assert report["summary"]["mixedSupportCases"] == 3
    assert report["summary"]["paraphraseHeavyCases"] == 1
    findings_by_case = {item["caseId"]: item for item in report["findings"]}
    assert findings_by_case["live_in_aide_case_001"]["severity"] == "info"
    assert findings_by_case["live_in_aide_case_no_violation_001"]["severity"] == "warning"
    assert "Paraphrase-heavy" in findings_by_case["live_in_aide_case_no_violation_001"]["title"]
    report_markdown = (ROOT / "outputs" / "authority_findings.md").read_text()
    assert report_markdown.startswith("# Authority Findings Report")
    assert "Fully Verified Cases: `1`" in report_markdown
    assert "Paraphrase-Heavy Cases: `1`" in report_markdown


def test_outputs_trust_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "trust_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("trust_matrix.schema.json"))
    cases = {item["caseId"]: item for item in matrix["cases"]}
    assert cases["live_in_aide_case_001"]["authorityTrust"] == "fully_verified"
    assert cases["live_in_aide_case_001"]["hasEntryWarnings"] is False
    assert cases["live_in_aide_case_001"]["warningEntryCount"] == 0
    assert cases["live_in_aide_case_effective_accommodation_001"]["authorityTrust"] == "mixed_support"
    assert cases["live_in_aide_case_effective_accommodation_001"]["hasEntryWarnings"] is True
    assert cases["live_in_aide_case_effective_accommodation_001"]["warningEntryCount"] > 0
    assert cases["live_in_aide_case_no_violation_001"]["authorityTrust"] == "paraphrase_heavy"
    assert cases["live_in_aide_case_no_violation_001"]["hasEntryWarnings"] is True
    assert cases["live_in_aide_case_no_violation_001"]["warningEntryCount"] > 0
    matrix_markdown = (ROOT / "outputs" / "trust_matrix.md").read_text()
    assert matrix_markdown.startswith("# Trust Matrix")
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | paraphrase_heavy | summary | yes" in matrix_markdown


def test_outputs_warning_summary_matches_schema_and_expectations():
    summary = json.loads((ROOT / "outputs" / "warning_summary.json").read_text())
    validate_with_schema(summary, load_schema("warning_summary.schema.json"))
    assert summary["summary"]["caseCount"] == 3
    assert summary["summary"]["warnedCaseCount"] == 3
    assert summary["summary"]["warningCounts"]["mixed_support"] == 2
    assert summary["summary"]["warningCounts"]["paraphrase_heavy"] == 1
    by_case = {item["caseId"]: item for item in summary["cases"]}
    assert by_case["live_in_aide_case_no_violation_001"]["warningEntryCount"] == 16
    markdown = (ROOT / "outputs" / "warning_summary.md").read_text()
    assert markdown.startswith("Warning Summary")
    assert "Warned Cases: 3" in markdown


def test_outputs_warning_label_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "warning_label_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("warning_label_matrix.schema.json"))
    mixed = matrix["labels"]["mixed_support"]
    paraphrase = matrix["labels"]["paraphrase_heavy"]
    assert mixed["summary"]["warnedCaseCount"] == 2
    assert mixed["summary"]["warningCounts"]["mixed_support"] == 2
    assert {item["caseId"] for item in mixed["cases"]} == {
        "live_in_aide_case_effective_accommodation_001",
        "live_in_aide_case_undue_burden_001",
    }
    assert paraphrase["summary"]["warnedCaseCount"] == 1
    assert paraphrase["summary"]["warningCounts"]["paraphrase_heavy"] == 1
    assert paraphrase["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    markdown = (ROOT / "outputs" / "warning_label_matrix.md").read_text()
    assert markdown.startswith("# Warning Label Matrix")
    assert "## mixed_support" in markdown
    assert "## paraphrase_heavy" in markdown


def test_outputs_warning_entry_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "warning_entry_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("warning_entry_matrix.schema.json"))
    assert len(matrix["cases"]) == 3
    by_case = {item["caseId"]: item for item in matrix["cases"]}
    assert "live_in_aide_case_001" not in by_case
    assert by_case["live_in_aide_case_effective_accommodation_001"]["warningLabel"] == "mixed_support"
    assert by_case["live_in_aide_case_no_violation_001"]["warningLabel"] == "paraphrase_heavy"
    assert by_case["live_in_aide_case_undue_burden_001"]["warningLabel"] == "mixed_support"
    assert by_case["live_in_aide_case_no_violation_001"]["warningEntryCount"] == 16
    assert "summary" in by_case["live_in_aide_case_no_violation_001"]["warnedKinds"]
    markdown = (ROOT / "outputs" / "warning_entry_matrix.md").read_text()
    assert markdown.startswith("# Warning Entry Matrix")
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | paraphrase_heavy | paraphrase_heavy | 16" in markdown


def test_outputs_warning_entry_summary_matches_schema_and_expectations():
    summary = json.loads((ROOT / "outputs" / "warning_entry_summary.json").read_text())
    validate_with_schema(summary, load_schema("warning_entry_summary.schema.json"))
    assert summary["singleCaseGuide"] is None
    assert summary["summary"]["caseCount"] == 3
    assert summary["summary"]["warningLabels"]["mixed_support"] == 2
    assert summary["summary"]["warningLabels"]["paraphrase_heavy"] == 1
    by_case = {item["caseId"]: item for item in summary["cases"]}
    assert by_case["live_in_aide_case_no_violation_001"]["warningLabel"] == "paraphrase_heavy"
    assert by_case["live_in_aide_case_no_violation_001"]["warningEntryCount"] == 16
    markdown = (ROOT / "outputs" / "warning_entry_summary.md").read_text()
    assert markdown.startswith("# Warning Entry Summary")
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | paraphrase_heavy | paraphrase_heavy | 16" in markdown


def test_outputs_warning_kind_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "warning_kind_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("warning_kind_matrix.schema.json"))
    assert matrix["summary"]["kindCount"] >= 1
    assert matrix["summary"]["caseCount"] == 3
    by_kind = {item["kind"]: item for item in matrix["kinds"]}
    assert "summary" in by_kind
    assert by_kind["summary"]["warningCaseCount"] == 3
    assert by_kind["summary"]["warningLabels"]["mixed_support"] == 2
    assert by_kind["summary"]["warningLabels"]["paraphrase_heavy"] == 1
    markdown = (ROOT / "outputs" / "warning_kind_matrix.md").read_text()
    assert markdown.startswith("# Warning Kind Matrix")
    assert "summary | 3 | {'mixed_support': 2, 'paraphrase_heavy': 1}" in markdown


def test_outputs_warning_kind_summary_matches_schema_and_expectations():
    summary = json.loads((ROOT / "outputs" / "warning_kind_summary.json").read_text())
    validate_with_schema(summary, load_schema("warning_kind_summary.schema.json"))
    assert summary["singleCaseGuide"] is None
    assert summary["summary"]["kindCount"] >= 1
    assert summary["summary"]["caseCount"] == 3
    by_kind = {item["kind"]: item for item in summary["kinds"]}
    assert "summary" in by_kind
    assert by_kind["summary"]["warningCaseCount"] == 3
    assert by_kind["summary"]["warningLabels"]["mixed_support"] == 2
    assert by_kind["summary"]["warningLabels"]["paraphrase_heavy"] == 1
    markdown = (ROOT / "outputs" / "warning_kind_summary.md").read_text()
    assert markdown.startswith("# Warning Kind Summary")
    assert "summary | 3 | {'mixed_support': 2, 'paraphrase_heavy': 1}" in markdown


def test_outputs_summary_index_matches_schema_and_paths():
    summary_index = json.loads((ROOT / "outputs" / "summary_index.json").read_text())
    validate_with_schema(summary_index, load_schema("summary_index.schema.json"))
    entries = {item["kind"]: item for item in summary_index["entries"]}
    assert set(entries) == {"warning_entry_summary", "warning_kind_summary"}
    assert (ROOT / "outputs" / "summary_index.md").exists()
    for entry in summary_index["entries"]:
        assert (ROOT / entry["jsonPath"]).exists()
        assert (ROOT / entry["markdownPath"]).exists()
    assert entries["warning_entry_summary"]["jsonPath"] == "outputs/warning_entry_summary.json"
    assert entries["warning_kind_summary"]["jsonPath"] == "outputs/warning_kind_summary.json"


def test_outputs_fit_index_matches_schema_and_paths():
    fit_index = json.loads((ROOT / "outputs" / "fit_index.json").read_text())
    validate_with_schema(fit_index, load_schema("fit_index.schema.json"))
    entries = {item["kind"]: item for item in fit_index["entries"]}
    assert set(entries) == {"fit_matrix", "fit_summary", "fit_findings", "fit_findings_summary"}
    assert (ROOT / "outputs" / "fit_index.md").exists()
    for entry in fit_index["entries"]:
        assert (ROOT / entry["jsonPath"]).exists()
        assert (ROOT / entry["markdownPath"]).exists()
    assert entries["fit_matrix"]["jsonPath"] == "outputs/fit_matrix.json"
    assert entries["fit_summary"]["jsonPath"] == "outputs/fit_summary.json"
    assert entries["fit_findings"]["jsonPath"] == "outputs/fit_findings.json"
    assert entries["fit_findings_summary"]["jsonPath"] == "outputs/fit_findings_summary.json"


def test_outputs_dashboard_index_matches_schema_and_paths():
    dashboard_index = json.loads((ROOT / "outputs" / "dashboard_index.json").read_text())
    validate_with_schema(dashboard_index, load_schema("dashboard_index.schema.json"))
    entries = {item["kind"]: item for item in dashboard_index["entries"]}
    assert set(entries) == {"outputs_index", "summary_index", "fit_index", "fit_findings", "fit_findings_summary", "refresh_state", "audit_index", "dashboard_overview"}
    assert entries["outputs_index"]["jsonPath"] == "outputs/index.json"
    assert entries["outputs_index"]["markdownPath"] == "outputs/index.md"
    assert entries["summary_index"]["jsonPath"] == "outputs/summary_index.json"
    assert entries["summary_index"]["markdownPath"] == "outputs/summary_index.md"
    assert entries["fit_index"]["jsonPath"] == "outputs/fit_index.json"
    assert entries["fit_index"]["markdownPath"] == "outputs/fit_index.md"
    assert entries["fit_findings"]["jsonPath"] == "outputs/fit_findings.json"
    assert entries["fit_findings"]["markdownPath"] == "outputs/fit_findings.md"
    assert entries["fit_findings_summary"]["jsonPath"] == "outputs/fit_findings_summary.json"
    assert entries["fit_findings_summary"]["markdownPath"] == "outputs/fit_findings_summary.md"
    assert entries["refresh_state"]["jsonPath"] == "outputs/.refresh_state.json"
    assert entries["refresh_state"]["markdownPath"] == "outputs/dashboard_overview.md"
    assert entries["audit_index"]["jsonPath"] == "outputs/audit_index.json"
    assert entries["audit_index"]["markdownPath"] == "outputs/audit_index.md"
    assert entries["dashboard_overview"]["jsonPath"] == "outputs/dashboard_overview.json"
    assert entries["dashboard_overview"]["markdownPath"] == "outputs/dashboard_overview.md"
    for entry in dashboard_index["entries"]:
        assert (ROOT / entry["jsonPath"]).exists()
        assert (ROOT / entry["markdownPath"]).exists()


def test_outputs_dashboard_overview_matches_schema_and_expectations():
    overview = json.loads((ROOT / "outputs" / "dashboard_overview.json").read_text())
    validate_with_schema(overview, load_schema("dashboard_overview.schema.json"))
    assert overview["summary"]["caseCount"] == 4
    assert overview["summary"]["violationCount"] == 2
    assert overview["summary"]["noViolationCount"] == 2
    assert overview["summary"]["warnedCaseCount"] == 3
    assert overview["summary"]["fullyVerifiedCount"] == 1
    assert overview["summary"]["mixedSupportCount"] == 2
    assert overview["summary"]["paraphraseHeavyCount"] == 1
    assert overview["summary"]["sourceVerifiedCount"] == 20
    assert overview["summary"]["sourceNormalizedCount"] == 20
    assert overview["summary"]["sourceStatus"] == (
        "All authority entries are sourceVerified and sourceNormalized across the current case set."
    )
    assert overview["summary"]["analogicalCases"] == 3
    assert overview["summary"]["recordSupportCases"] == 1
    assert overview["discovery"]["refreshState"] == "outputs/.refresh_state.json"
    assert overview["discovery"]["outputsIndex"] == "outputs/index.json"
    assert overview["discovery"]["fitIndex"] == "outputs/fit_index.json"
    assert overview["discovery"]["fitSummary"] == "outputs/fit_summary.json"
    assert overview["discovery"]["fitFindings"] == "outputs/fit_findings.json"
    assert overview["discovery"]["fitFindingsSummary"] == "outputs/fit_findings_summary.json"
    assert overview["featured"]["highestConfidenceCaseId"] == "live_in_aide_case_001"
    assert overview["featured"]["singleCaseGuide"] is None
    assert overview["featured"]["lowestConfidenceCaseId"] in {
        "live_in_aide_case_effective_accommodation_001",
        "live_in_aide_case_no_violation_001",
    }
    markdown = (ROOT / "outputs" / "dashboard_overview.md").read_text()
    assert "Dashboard Overview" in markdown
    assert "Case Count" in markdown
    assert "Source Normalized Count" in markdown
    assert "Source Status" in markdown
    assert "Refresh State" in markdown
    assert "Fit Index" in markdown
    assert "Fit Findings" in markdown
    assert "Fit Summary" in markdown


def test_outputs_refresh_state_exists_and_is_complete():
    payload = json.loads((ROOT / "outputs" / ".refresh_state.json").read_text())
    assert payload["status"] == "complete"
    assert payload["startedAt"]
    assert payload["completedAt"]


def test_outputs_audit_index_matches_schema_and_paths():
    audit_index = json.loads((ROOT / "outputs" / "audit_index.json").read_text())
    validate_with_schema(audit_index, load_schema("audit_index.schema.json"))
    entries = {item["kind"]: item for item in audit_index["entries"]}
    assert set(entries) == {
        "authority_summary_matrix",
        "authority_findings",
        "source_findings",
        "source_metadata_matrix",
        "fit_matrix",
        "fit_summary",
        "fit_findings",
        "fit_findings_summary",
        "trust_matrix",
        "warning_summary",
        "warning_label_matrix",
        "warning_entry_matrix",
        "warning_entry_summary",
        "warning_kind_matrix",
        "warning_kind_summary",
        "summary_index",
        "case_audit_matrix",
    }
    assert (ROOT / "outputs" / "audit_index.md").exists()
    for entry in audit_index["entries"]:
        assert (ROOT / entry["jsonPath"]).exists()
        assert (ROOT / entry["markdownPath"]).exists()
    assert entries["source_metadata_matrix"]["jsonPath"] == "outputs/source_metadata_matrix.json"
    assert entries["fit_matrix"]["jsonPath"] == "outputs/fit_matrix.json"
    assert entries["fit_matrix"]["markdownPath"] == "outputs/fit_matrix.md"
    assert entries["fit_summary"]["jsonPath"] == "outputs/fit_summary.json"
    assert entries["fit_summary"]["markdownPath"] == "outputs/fit_summary.md"
    assert entries["fit_findings"]["jsonPath"] == "outputs/fit_findings.json"
    assert entries["fit_findings"]["markdownPath"] == "outputs/fit_findings.md"
    assert entries["fit_findings_summary"]["jsonPath"] == "outputs/fit_findings_summary.json"
    assert entries["fit_findings_summary"]["markdownPath"] == "outputs/fit_findings_summary.md"
    assert entries["warning_label_matrix"]["jsonPath"] == "outputs/warning_label_matrix.json"
    assert entries["warning_entry_matrix"]["jsonPath"] == "outputs/warning_entry_matrix.json"
    assert entries["warning_entry_summary"]["jsonPath"] == "outputs/warning_entry_summary.json"
    assert entries["warning_kind_matrix"]["jsonPath"] == "outputs/warning_kind_matrix.json"
    assert entries["warning_kind_summary"]["jsonPath"] == "outputs/warning_kind_summary.json"
    assert entries["summary_index"]["jsonPath"] == "outputs/summary_index.json"
    assert entries["summary_index"]["markdownPath"] == "outputs/summary_index.md"
    assert entries["case_audit_matrix"]["jsonPath"] == "outputs/case_audit_matrix.json"


def test_outputs_source_metadata_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "source_metadata_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("source_metadata_matrix.schema.json"))
    assert matrix["summary"]["caseCount"] == 4
    assert matrix["summary"]["authorityCount"] == 20
    assert matrix["summary"]["sourceVerifiedCount"] == 20
    assert matrix["summary"]["sourceNormalizedCount"] == 20
    by_case = {item["caseId"]: item for item in matrix["cases"]}
    assert by_case["live_in_aide_case_001"]["sourceVerifiedCount"] == 5
    assert by_case["live_in_aide_case_001"]["sourceNormalizedCount"] == 5
    assert by_case["live_in_aide_case_001"]["unnormalizedAuthorityIds"] == []
    markdown = (ROOT / "outputs" / "source_metadata_matrix.md").read_text()
    assert markdown.startswith("# Source Metadata Matrix")
    assert "live_in_aide_case_001 | constructive_denial | 5 | 5 | 5 | none" in markdown


def test_outputs_fit_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "fit_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("fit_matrix.schema.json"))
    assert matrix["summary"]["caseCount"] == 4
    assert matrix["summary"]["authorityCount"] == 20
    assert matrix["summary"]["directCount"] == 10
    assert matrix["summary"]["analogicalCount"] == 7
    assert matrix["summary"]["recordSupportCount"] == 3
    by_case = {item["caseId"]: item for item in matrix["cases"]}
    assert by_case["live_in_aide_case_001"]["directCount"] == 3
    assert by_case["live_in_aide_case_001"]["analogicalCount"] == 2
    assert by_case["live_in_aide_case_001"]["recordSupportCount"] == 0
    assert by_case["live_in_aide_case_no_violation_001"]["directCount"] == 1
    assert by_case["live_in_aide_case_no_violation_001"]["analogicalCount"] == 1
    assert by_case["live_in_aide_case_no_violation_001"]["recordSupportCount"] == 3
    markdown = (ROOT / "outputs" / "fit_matrix.md").read_text()
    assert markdown.startswith("# Fit Matrix")
    assert "Direct Count: `10`" in markdown


def test_outputs_fit_summary_matches_schema_and_expectations():
    summary = json.loads((ROOT / "outputs" / "fit_summary.json").read_text())
    validate_with_schema(summary, load_schema("fit_summary.schema.json"))
    assert summary["summary"]["caseCount"] == 4
    assert summary["summary"]["authorityCount"] == 20
    assert summary["summary"]["directCount"] == 10
    assert summary["summary"]["analogicalCount"] == 7
    assert summary["summary"]["recordSupportCount"] == 3
    assert summary["singleCaseGuide"] is None
    by_case = {item["caseId"]: item for item in summary["cases"]}
    assert by_case["live_in_aide_case_001"]["directCount"] == 3
    assert by_case["live_in_aide_case_no_violation_001"]["recordSupportCount"] == 3
    markdown = (ROOT / "outputs" / "fit_summary.md").read_text()
    assert markdown.startswith("# Fit Summary")
    assert "Direct Count: `10`" in markdown


def test_outputs_fit_findings_matches_schema_and_expectations():
    report = json.loads((ROOT / "outputs" / "fit_findings.json").read_text())
    validate_with_schema(report, load_schema("fit_findings.schema.json"))
    assert report["summary"]["caseCount"] == 4
    assert report["summary"]["directOnlyCases"] == 0
    assert report["summary"]["analogicalCases"] == 3
    assert report["summary"]["recordSupportCases"] == 1
    findings = {item["caseId"]: item for item in report["findings"]}
    assert findings["live_in_aide_case_no_violation_001"]["severity"] == "warning"
    assert findings["live_in_aide_case_no_violation_001"]["title"] == "Record-support-heavy fit posture"
    markdown = (ROOT / "outputs" / "fit_findings.md").read_text()
    assert markdown.startswith("# Fit Findings Report")
    assert "Record-Support Cases: `1`" in markdown


def test_outputs_fit_findings_summary_matches_schema_and_expectations():
    summary = json.loads((ROOT / "outputs" / "fit_findings_summary.json").read_text())
    validate_with_schema(summary, load_schema("fit_findings_summary.schema.json"))
    assert summary["summary"]["caseCount"] == 4
    assert summary["summary"]["analogicalCases"] == 3
    assert summary["summary"]["recordSupportCases"] == 1
    assert summary["summary"]["severityCounts"]["warning"] == 4
    assert summary["singleCaseGuide"] is None
    assert summary["cases"][0]["caseId"]
    markdown = (ROOT / "outputs" / "fit_findings_summary.md").read_text()
    assert markdown.startswith("# Fit Findings Summary")
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | warning | Record-support-heavy fit posture" in markdown


def test_outputs_source_findings_matches_schema_and_expectations():
    report = json.loads((ROOT / "outputs" / "source_findings.json").read_text())
    validate_with_schema(report, load_schema("source_findings.schema.json"))
    assert report["summary"]["caseCount"] == 4
    assert report["summary"]["fullyNormalizedCases"] == 4
    assert report["summary"]["partiallyNormalizedCases"] == 0
    findings = {item["caseId"]: item for item in report["findings"]}
    assert findings["live_in_aide_case_001"]["severity"] == "info"
    assert "Every authority entry in this case is marked as sourceNormalized." == findings["live_in_aide_case_001"]["detail"]
    markdown = (ROOT / "outputs" / "source_findings.md").read_text()
    assert markdown.startswith("# Source Findings Report")
    assert "Fully Normalized Cases: `4`" in markdown


def test_outputs_case_audit_matrix_matches_schema_and_expectations():
    matrix = json.loads((ROOT / "outputs" / "case_audit_matrix.json").read_text())
    validate_with_schema(matrix, load_schema("case_audit_matrix.schema.json"))
    by_case = {item["caseId"]: item for item in matrix["cases"]}
    assert by_case["live_in_aide_case_001"]["authorityTrust"] == "fully_verified"
    assert by_case["live_in_aide_case_001"]["fitFinding"] == "analogical_support"
    assert (
        by_case["live_in_aide_case_001"]["primaryWhy"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert by_case["live_in_aide_case_001"]["warningLabel"] is None
    assert by_case["live_in_aide_case_effective_accommodation_001"]["warningLabel"] == "mixed_support"
    assert by_case["live_in_aide_case_no_violation_001"]["fitFinding"] == "record_support_heavy"
    assert by_case["live_in_aide_case_no_violation_001"]["warningLabel"] == "paraphrase_heavy"
    assert (
        by_case["live_in_aide_case_no_violation_001"]["primaryWhy"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    assert by_case["live_in_aide_case_undue_burden_001"]["primaryKind"] == "memorandum_pdf"
    markdown = (ROOT / "outputs" / "case_audit_matrix.md").read_text()
    assert markdown.startswith("# Case Audit Matrix")
    assert (
        "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | 0.57 | paraphrase_heavy | record_support_heavy | summary | Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review. | yes | 16 | paraphrase_heavy"
        in markdown
    )


def test_case_matrix_cli_supports_trust_matrix_mode():
    matrix = render_trust_matrix(ROOT)
    assert "Warning Label Filter: any" in matrix
    assert "Case ID | Branch | Outcome | Trust | WarnLabels | Primary | Entry Warnings | Warning Count | Package" in matrix
    assert "live_in_aide_case_001 | constructive_denial | violation | fully_verified | none | memorandum_pdf | no | 0" in matrix
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | paraphrase_heavy | paraphrase_heavy | summary | yes" in matrix
    payload = build_trust_matrix_data(ROOT)
    validate_with_schema(payload, load_schema("trust_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    filtered = build_trust_matrix_data(ROOT, trust="mixed_support")
    assert len(filtered["cases"]) == 2
    assert filtered["cases"][0]["authorityTrust"] == "mixed_support"
    label_filtered = build_trust_matrix_data(ROOT, warning_label="paraphrase_heavy")
    assert len(label_filtered["cases"]) == 1
    assert label_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    warned_matrix = render_trust_matrix(ROOT, warned_only=True)
    assert "live_in_aide_case_001 | constructive_denial | violation | fully_verified" not in warned_matrix
    try:
        build_trust_matrix_data(ROOT, warning_label="bad_label")
    except ValueError as exc:
        assert "warning-label must be one of" in str(exc)
    else:
        raise AssertionError("trust-matrix mode should reject invalid warning labels")


def test_case_matrix_cli_supports_warning_summary_mode():
    summary = render_warning_summary(ROOT)
    assert "Warning Summary" in summary
    assert "Warned Cases: 3" in summary
    assert "Warning Labels: {'mixed_support': 2, 'paraphrase_heavy': 1}" in summary
    assert "Warning Label Filter: any" in summary
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | paraphrase_heavy | summary | 16" in summary
    filtered = build_warning_summary_data(ROOT, trust="mixed_support")
    validate_with_schema(filtered, load_schema("warning_summary.schema.json"))
    assert filtered["refreshRuntime"]["status"] == "complete"
    assert filtered["refreshRuntime"]["running"] is False
    assert filtered["refreshRuntime"]["elapsedHuman"] is not None
    assert filtered["summary"]["warnedCaseCount"] == 2
    assert filtered["summary"]["warningCounts"]["mixed_support"] == 2
    label_filtered = build_warning_summary_data(ROOT, warning_label="paraphrase_heavy")
    assert label_filtered["summary"]["warnedCaseCount"] == 1
    assert label_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_warning_label_matrix_mode():
    matrix = render_warning_label_matrix(ROOT)
    assert "Warning Label Matrix" in matrix
    assert "Warning Label Filter: any" in matrix
    assert "mixed_support:" in matrix
    assert "paraphrase_heavy:" in matrix
    filtered = build_warning_label_matrix_data(ROOT, warning_label="paraphrase_heavy")
    validate_with_schema(filtered, load_schema("warning_label_matrix.schema.json"))
    assert filtered["refreshRuntime"]["status"] == "complete"
    assert filtered["refreshRuntime"]["running"] is False
    assert list(filtered["labels"].keys()) == ["paraphrase_heavy"]
    assert filtered["labels"]["paraphrase_heavy"]["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_warning_entry_matrix_mode():
    matrix = render_warning_entry_matrix(ROOT)
    assert "Warning Entry Matrix" in matrix
    assert "Trust Filter: any" in matrix
    assert "Warning Label Filter: any" in matrix
    assert "Warned Kind Filter: any" in matrix
    assert "Sort: caseId" in matrix
    assert "Top N: all" in matrix
    assert "Case ID | Branch | Trust | Warning Label | Warning Count | Warned Kinds | Package" in matrix
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | paraphrase_heavy | paraphrase_heavy | 16" in matrix
    trust_filtered = build_warning_entry_matrix_data(ROOT, trust="mixed_support")
    validate_with_schema(trust_filtered, load_schema("warning_entry_matrix.schema.json"))
    assert trust_filtered["refreshRuntime"]["status"] == "complete"
    assert trust_filtered["refreshRuntime"]["running"] is False
    assert len(trust_filtered["cases"]) == 2
    assert all(item["authorityTrust"] == "mixed_support" for item in trust_filtered["cases"])
    warning_sorted = build_warning_entry_matrix_data(ROOT, sort_key="warningCount")
    assert warning_sorted["cases"][0]["caseId"] == "live_in_aide_case_effective_accommodation_001"
    filtered = build_warning_entry_matrix_data(ROOT, warning_label="paraphrase_heavy")
    validate_with_schema(filtered, load_schema("warning_entry_matrix.schema.json"))
    assert len(filtered["cases"]) == 1
    assert filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    kind_filtered = build_warning_entry_matrix_data(ROOT, warned_kind="summary")
    validate_with_schema(kind_filtered, load_schema("warning_entry_matrix.schema.json"))
    assert len(kind_filtered["cases"]) == 3
    assert all("summary" in item["warnedKinds"] for item in kind_filtered["cases"])
    top_payload = build_warning_entry_matrix_data(ROOT, sort_key="warningCount", top_n=2)
    assert len(top_payload["cases"]) == 2


def test_case_matrix_cli_supports_warning_kind_matrix_mode():
    matrix = render_warning_kind_matrix(ROOT)
    assert "Warning Kind Matrix" in matrix
    assert "Trust Filter: any" in matrix
    assert "Warned Kind Filter: any" in matrix
    assert "Sort: kind" in matrix
    assert "Top N: all" in matrix
    assert "Kind | Warning Cases | Warning Labels | Case IDs" in matrix
    assert "summary | 3 | {'mixed_support': 2, 'paraphrase_heavy': 1}" in matrix
    trust_filtered = build_warning_kind_matrix_data(ROOT, trust="mixed_support")
    validate_with_schema(trust_filtered, load_schema("warning_kind_matrix.schema.json"))
    assert trust_filtered["refreshRuntime"]["status"] == "complete"
    assert trust_filtered["refreshRuntime"]["running"] is False
    assert trust_filtered["summary"]["caseCount"] == 2
    assert all(
        all(case["authorityTrust"] == "mixed_support" for case in item["cases"])
        for item in trust_filtered["kinds"]
    )
    filtered = build_warning_kind_matrix_data(ROOT, warned_kind="summary")
    validate_with_schema(filtered, load_schema("warning_kind_matrix.schema.json"))
    assert filtered["summary"]["kindCount"] == 1
    assert filtered["kinds"][0]["kind"] == "summary"
    sorted_payload = build_warning_kind_matrix_data(ROOT, sort_key="warningCaseCount")
    assert sorted_payload["kinds"][0]["warningCaseCount"] >= sorted_payload["kinds"][-1]["warningCaseCount"]
    top_payload = build_warning_kind_matrix_data(ROOT, sort_key="warningCaseCount", top_n=5)
    assert top_payload["summary"]["kindCount"] == 5
    assert len(top_payload["kinds"]) == 5


def test_case_matrix_cli_supports_warning_entry_summary_mode():
    summary = render_warning_entry_summary(ROOT)
    assert "Warning Entry Summary" in summary
    assert "Trust Filter: any" in summary
    assert "Warning Label Filter: any" in summary
    assert "Sort: caseId" in summary
    assert "Top N: all" in summary
    assert "Case Count: 3" in summary
    assert "Warning Labels: {'mixed_support': 2, 'paraphrase_heavy': 1}" in summary
    payload = build_warning_entry_summary_data(ROOT)
    validate_with_schema(payload, load_schema("warning_entry_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 3
    trust_filtered = build_warning_entry_summary_data(ROOT, trust="mixed_support")
    assert trust_filtered["summary"]["caseCount"] == 2
    assert all(case["authorityTrust"] == "mixed_support" for case in trust_filtered["cases"])
    label_filtered = build_warning_entry_summary_data(ROOT, warning_label="paraphrase_heavy")
    assert label_filtered["summary"]["caseCount"] == 1
    assert label_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert label_filtered["singleCaseGuide"] == {
        "caseId": "live_in_aide_case_no_violation_001",
        "recommendedFirstStop": "summary.json",
        "whyOpenThis": "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review.",
    }
    sorted_payload = build_warning_entry_summary_data(ROOT, sort_key="warningCount")
    assert sorted_payload["cases"][0]["warningEntryCount"] >= sorted_payload["cases"][-1]["warningEntryCount"]
    top_payload = build_warning_entry_summary_data(ROOT, sort_key="warningCount", top_n=2)
    assert len(top_payload["cases"]) == 2
    ranked_summary = render_warning_entry_summary(ROOT, sort_key="warningCount", top_n=2)
    assert "Rank | Case ID | Branch | Trust | Warning Label | Warning Count" in ranked_summary
    assert "1 | " in ranked_summary
    filtered_summary = render_warning_entry_summary(ROOT, warning_label="paraphrase_heavy")
    assert "Single-Case Guide" in filtered_summary
    assert "Recommended First Stop: summary.json" in filtered_summary


def test_case_matrix_cli_supports_warning_kind_summary_mode():
    summary = render_warning_kind_summary(ROOT)
    assert "Warning Kind Summary" in summary
    assert "Trust Filter: any" in summary
    assert "Warning Label Filter: any" in summary
    assert "Sort: kind" in summary
    assert "Top N: all" in summary
    assert "Kind Count: 16" in summary
    assert "Case Count: 3" in summary
    payload = build_warning_kind_summary_data(ROOT)
    validate_with_schema(payload, load_schema("warning_kind_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["kindCount"] == 16
    trust_filtered = build_warning_kind_summary_data(ROOT, trust="mixed_support")
    assert trust_filtered["summary"]["caseCount"] == 2
    label_filtered = build_warning_kind_summary_data(ROOT, warning_label="paraphrase_heavy")
    assert label_filtered["summary"]["caseCount"] == 1
    assert label_filtered["kinds"][0]["warningLabels"] == {"paraphrase_heavy": 1}
    assert label_filtered["singleCaseGuide"] == {
        "caseId": "live_in_aide_case_no_violation_001",
        "recommendedFirstStop": "summary.json",
        "whyOpenThis": "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review.",
    }
    sorted_payload = build_warning_kind_summary_data(ROOT, sort_key="warningCaseCount")
    assert sorted_payload["kinds"][0]["warningCaseCount"] >= sorted_payload["kinds"][-1]["warningCaseCount"]
    top_payload = build_warning_kind_summary_data(ROOT, sort_key="warningCaseCount", top_n=5)
    assert len(top_payload["kinds"]) == 5
    ranked_summary = render_warning_kind_summary(ROOT, sort_key="warningCaseCount", top_n=5)
    assert "Rank | Kind | Warning Cases | Warning Labels" in ranked_summary
    assert "1 | " in ranked_summary
    filtered_summary = render_warning_kind_summary(ROOT, warning_label="paraphrase_heavy")
    assert "Single-Case Guide" in filtered_summary
    assert "Recommended First Stop: summary.json" in filtered_summary


def test_case_matrix_cli_supports_summary_index_mode():
    summary_index = render_summary_index(ROOT)
    assert "Summary Index" in summary_index
    assert "Recommended First Stop: outputs/warning_entry_summary.json" in summary_index
    assert (
        "Why Open This: Start with the warning-entry summary because it is the quickest dashboard-style orientation to which cases currently carry lower-trust warning posture."
        in summary_index
    )
    assert "Priority | Kind | JSON | Markdown | Why Open This | Description" in summary_index
    payload = build_summary_index_data(ROOT)
    validate_with_schema(payload, load_schema("summary_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    assert payload["recommendedFirstStop"] == "outputs/warning_entry_summary.json"
    assert (
        payload["whyOpenThis"]
        == "Start with the warning-entry summary because it is the quickest dashboard-style orientation to which cases currently carry lower-trust warning posture."
    )
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"warning_entry_summary", "warning_kind_summary"}
    by_kind = {item["kind"]: item for item in payload["entries"]}
    assert by_kind["warning_entry_summary"]["priorityHint"] == "recommended"
    assert (
        by_kind["warning_entry_summary"]["whyOpenThis"]
        == "Open this first when you want the fastest compact view of which cases currently carry warning posture."
    )


def test_case_matrix_cli_supports_fit_index_mode():
    fit_index = render_fit_index(ROOT)
    assert "Fit Index" in fit_index
    assert "Recommended First Stop: outputs/fit_summary.json" in fit_index
    assert (
        "Why Open This: Start with the fit summary because it is the quickest dashboard-style orientation to direct, analogical, and record-support posture across the current case set."
        in fit_index
    )
    assert "Priority | Kind | JSON | Markdown | Why Open This | Description" in fit_index
    payload = build_fit_index_data(ROOT)
    validate_with_schema(payload, load_schema("fit_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    assert payload["recommendedFirstStop"] == "outputs/fit_summary.json"
    assert (
        payload["whyOpenThis"]
        == "Start with the fit summary because it is the quickest dashboard-style orientation to direct, analogical, and record-support posture across the current case set."
    )
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"fit_matrix", "fit_summary", "fit_findings", "fit_findings_summary"}
    by_kind = {item["kind"]: item for item in payload["entries"]}
    assert by_kind["fit_summary"]["priorityHint"] == "recommended"
    assert by_kind["fit_findings"]["priorityHint"] == "primary"
    assert (
        by_kind["fit_summary"]["whyOpenThis"]
        == "Open this first when you want the quickest compact view of direct, analogical, and record-support posture."
    )


def test_case_matrix_cli_supports_dashboard_index_mode():
    dashboard_index = render_dashboard_index(ROOT)
    assert "Dashboard Index" in dashboard_index
    assert "Recommended First Stop: outputs/dashboard_overview.json" in dashboard_index
    assert (
        "Why Open This: Start with the dashboard overview because it is the single best top-level entry point into counts, warnings, fit posture, and the main discovery surfaces."
        in dashboard_index
    )
    assert "Priority | Kind | JSON | Markdown | Why Open This | Description" in dashboard_index
    payload = build_dashboard_index_data(ROOT)
    validate_with_schema(payload, load_schema("dashboard_index.schema.json"))
    assert payload["recommendedFirstStop"] == "outputs/dashboard_overview.json"
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    assert (
        payload["whyOpenThis"]
        == "Start with the dashboard overview because it is the single best top-level entry point into counts, warnings, fit posture, and the main discovery surfaces."
    )
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"outputs_index", "summary_index", "fit_index", "fit_findings", "fit_findings_summary", "refresh_state", "audit_index", "dashboard_overview"}
    by_kind = {item["kind"]: item for item in payload["entries"]}
    assert by_kind["dashboard_overview"]["priorityHint"] == "recommended"
    assert by_kind["fit_index"]["priorityHint"] == "primary"
    assert by_kind["refresh_state"]["priorityHint"] == "supporting"
    assert (
        by_kind["dashboard_overview"]["whyOpenThis"]
        == "Open this first when you want the strongest single top-level dashboard rollup before following linked surfaces."
    )


def test_case_matrix_cli_supports_dashboard_overview_mode():
    overview = render_dashboard_overview(ROOT)
    assert "Dashboard Overview" in overview
    assert "Summary" in overview
    assert "Fit Finding Filter: any" in overview
    assert "Refresh Runtime: complete" in overview
    assert "Source Normalized Count" in overview
    assert "Source Status" in overview
    assert "Recommended First Stop: outputs/dashboard_overview.json" in overview
    assert "Why Open This First: Start here because this overview is the single best top-level entry point into counts, warnings, fit posture, and linked audit surfaces." in overview
    assert "Refresh State: outputs/.refresh_state.json" in overview
    assert "Refresh State Why: Open the refresh state when you want to confirm whether snapshot generation is currently running or has completed cleanly." in overview
    assert "Fit Index: outputs/fit_index.json" in overview
    assert "Fit Index Why: Open the fit index when you want the compact discovery path for fit-quality matrix, summary, and findings artifacts." in overview
    assert "Direct Fit Count" in overview
    assert "Record-Support Fit Count" in overview
    assert "Analogical Cases: 3" in overview
    assert "Record-Support Cases: 1" in overview
    assert "Fit Status" in overview
    assert "Fit Summary: outputs/fit_summary.json" in overview
    assert "Fit Findings: outputs/fit_findings.json" in overview
    assert "Fit Findings Summary: outputs/fit_findings_summary.json" in overview
    payload = build_dashboard_overview_data(ROOT)
    validate_with_schema(payload, load_schema("dashboard_overview.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    assert payload["summary"]["caseCount"] == 4
    assert payload["discovery"]["recommendedFirstStop"] == "outputs/dashboard_overview.json"
    assert (
        payload["discovery"]["recommendedFirstStopWhyOpenThis"]
        == "Start here because this overview is the single best top-level entry point into counts, warnings, fit posture, and linked audit surfaces."
    )
    assert payload["discovery"]["refreshState"] == "outputs/.refresh_state.json"
    assert (
        payload["discovery"]["refreshStateWhyOpenThis"]
        == "Open the refresh state when you want to confirm whether snapshot generation is currently running or has completed cleanly."
    )
    assert payload["discovery"]["outputsIndex"] == "outputs/index.json"
    assert (
        payload["discovery"]["outputsIndexWhyOpenThis"]
        == "Open the outputs index to see the full generated case inventory across fixtures, packages, advocacy outputs, and memorandum outputs."
    )
    assert payload["discovery"]["fitIndex"] == "outputs/fit_index.json"
    assert (
        payload["discovery"]["fitIndexWhyOpenThis"]
        == "Open the fit index when you want the compact discovery path for fit-quality matrix, summary, and findings artifacts."
    )
    assert payload["discovery"]["fitSummary"] == "outputs/fit_summary.json"
    assert (
        payload["discovery"]["fitSummaryWhyOpenThis"]
        == "Open the fit summary for the quickest compact rollup of direct, analogical, and record-support counts across the current case set."
    )
    assert payload["discovery"]["fitFindings"] == "outputs/fit_findings.json"
    assert (
        payload["discovery"]["fitFindingsWhyOpenThis"]
        == "Open the fit findings report when you want case-level interpretation of analogical and record-support-heavy posture."
    )
    assert payload["discovery"]["fitFindingsSummary"] == "outputs/fit_findings_summary.json"
    assert (
        payload["discovery"]["fitFindingsSummaryWhyOpenThis"]
        == "Open the fit findings summary when you want a lighter case-first fit-posture view without the full findings detail."
    )
    assert payload["summary"]["sourceNormalizedCount"] == 20
    assert payload["summary"]["directFitCount"] == 10
    assert payload["summary"]["analogicalFitCount"] == 7
    assert payload["summary"]["recordSupportFitCount"] == 3
    assert payload["summary"]["analogicalCases"] == 3
    assert payload["summary"]["recordSupportCases"] == 1
    fit_filtered = build_dashboard_overview_data(ROOT, fit_kind="record_support")
    assert fit_filtered["summary"]["caseCount"] == 1
    assert fit_filtered["summary"]["recordSupportFitCount"] == 3
    assert fit_filtered["summary"]["directFitCount"] == 1
    assert fit_filtered["summary"]["analogicalFitCount"] == 1
    assert fit_filtered["summary"]["recordSupportCases"] == 1
    assert fit_filtered["featured"]["singleCaseGuide"] == {
        "caseId": "live_in_aide_case_no_violation_001",
        "recommendedFirstStop": "summary.json",
        "whyOpenThis": "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review.",
    }
    fit_finding_filtered = build_dashboard_overview_data(ROOT, fit_finding="record_support_heavy")
    assert fit_finding_filtered["summary"]["caseCount"] == 1
    assert fit_finding_filtered["summary"]["recordSupportCases"] == 1
    assert fit_finding_filtered["featured"]["singleCaseGuide"]["caseId"] == "live_in_aide_case_no_violation_001"
    filtered_render = render_dashboard_overview(ROOT, fit_finding="record_support_heavy")
    assert "Single-Case Guide" in filtered_render
    assert "Recommended First Stop: summary.json" in filtered_render


def test_case_matrix_cli_supports_source_metadata_matrix_mode():
    matrix = render_source_metadata_matrix(ROOT)
    assert "Source Metadata Matrix" in matrix
    assert "Case Count: 4" in matrix
    assert "Source Verified Count: 20" in matrix
    payload = build_source_metadata_matrix_data(ROOT)
    validate_with_schema(payload, load_schema("source_metadata_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    filtered = build_source_metadata_matrix_data(ROOT, trust="paraphrase_heavy")
    assert filtered["summary"]["caseCount"] == 1
    assert filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_refresh_state_mode():
    refresh_state = render_refresh_state(ROOT)
    assert "Refresh State" in refresh_state
    assert "Status: complete" in refresh_state
    assert "Elapsed Seconds:" in refresh_state
    assert "Elapsed:" in refresh_state
    payload = build_refresh_state_data(ROOT)
    assert payload["status"] == "complete"
    assert payload["startedAt"]
    assert payload["completedAt"]
    assert payload["elapsedSeconds"] is not None
    assert payload["elapsedSeconds"] >= 0
    assert payload["elapsedHuman"] is not None
    guarded = fail_if_refresh_running(ROOT)
    assert guarded["status"] == "complete"
    waited = wait_for_refresh_complete(ROOT, timeout_seconds=0.5, poll_interval_seconds=0.01)
    assert waited["status"] == "complete"


def test_prepend_refresh_warning_only_when_running():
    with TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        outputs_dir = temp_root / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        (outputs_dir / ".refresh_state.json").write_text(
            json.dumps(
                {
                    "status": "running",
                    "startedAt": "2026-04-04T19:00:00+00:00",
                    "completedAt": None,
                }
            )
        )
        warned = prepend_refresh_warning("Body\n", temp_root)
        assert warned.startswith("Refresh Warning\n")
        assert "Outputs are currently being regenerated" in warned
        assert warned.endswith("Body\n")
        (outputs_dir / ".refresh_state.json").write_text(
            json.dumps(
                {
                    "status": "complete",
                    "startedAt": "2026-04-04T19:00:00+00:00",
                    "completedAt": "2026-04-04T19:00:01+00:00",
                }
            )
        )
        assert prepend_refresh_warning("Body\n", temp_root) == "Body\n"


def test_prepend_refresh_warning_wraps_remaining_text_audit_views():
    with TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        outputs_dir = temp_root / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        (outputs_dir / ".refresh_state.json").write_text(
            json.dumps(
                {
                    "status": "running",
                    "startedAt": "2026-04-04T19:00:00+00:00",
                    "completedAt": None,
                }
            )
        )
        for body in (
            render_warning_summary(ROOT),
            render_warning_label_matrix(ROOT),
            render_warning_entry_matrix(ROOT),
            render_warning_kind_matrix(ROOT),
            render_warning_entry_summary(ROOT),
            render_warning_kind_summary(ROOT),
            render_trust_matrix(ROOT),
            render_source_findings(ROOT),
            render_source_metadata_matrix(ROOT),
            render_fit_matrix(ROOT),
            render_fit_summary(ROOT),
            render_fit_findings(ROOT),
            render_fit_findings_summary(ROOT),
            render_case_audit_matrix(ROOT),
        ):
            warned = prepend_refresh_warning(body, temp_root)
            assert warned.startswith("Refresh Warning\n")
            assert "Outputs are currently being regenerated" in warned
            assert "may reflect a mid-refresh state" in warned


def test_fail_if_refresh_running_raises_for_running_state():
    with TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir)
        outputs_dir = temp_root / "outputs"
        outputs_dir.mkdir(parents=True, exist_ok=True)
        (outputs_dir / ".refresh_state.json").write_text(
            json.dumps(
                {
                    "status": "running",
                    "startedAt": "2026-04-04T19:00:00+00:00",
                    "completedAt": None,
                }
            )
        )
        try:
            fail_if_refresh_running(temp_root)
        except ValueError as exc:
            assert "refresh is currently running" in str(exc)
            return
        raise AssertionError("fail_if_refresh_running should raise while refresh is running")


def test_case_matrix_cli_supports_fit_matrix_mode():
    matrix = render_fit_matrix(ROOT)
    assert "Fit Matrix" in matrix
    assert "Case Count: 4" in matrix
    assert "Direct Count: 10" in matrix
    assert "Fit Finding Filter: any" in matrix
    payload = build_fit_matrix_data(ROOT)
    validate_with_schema(payload, load_schema("fit_matrix.schema.json"))
    filtered = build_fit_matrix_data(ROOT, trust="paraphrase_heavy")
    assert filtered["summary"]["caseCount"] == 1
    assert filtered["summary"]["directCount"] == 1
    assert filtered["summary"]["recordSupportCount"] == 3
    assert filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_filtered = build_fit_matrix_data(ROOT, fit_kind="record_support")
    assert fit_filtered["summary"]["caseCount"] == 1
    assert fit_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert fit_filtered["summary"]["recordSupportCount"] == 3
    fit_finding_filtered = build_fit_matrix_data(ROOT, fit_finding="record_support_heavy")
    assert fit_finding_filtered["summary"]["caseCount"] == 1
    assert fit_finding_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_fit_summary_mode():
    summary = render_fit_summary(ROOT)
    assert "Fit Summary" in summary
    assert "Case Count: 4" in summary
    assert "Direct Count: 10" in summary
    assert "Fit Finding Filter: any" in summary
    payload = build_fit_summary_data(ROOT)
    validate_with_schema(payload, load_schema("fit_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    filtered = build_fit_summary_data(ROOT, trust="paraphrase_heavy")
    assert filtered["summary"]["caseCount"] == 1
    assert filtered["summary"]["recordSupportCount"] == 3
    assert filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert filtered["singleCaseGuide"] == {
        "caseId": "live_in_aide_case_no_violation_001",
        "recommendedFirstStop": "summary.json",
        "whyOpenThis": "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review.",
    }
    fit_filtered = build_fit_summary_data(ROOT, fit_kind="record_support")
    assert fit_filtered["summary"]["caseCount"] == 1
    assert fit_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_finding_filtered = build_fit_summary_data(ROOT, fit_finding="record_support_heavy")
    assert fit_finding_filtered["summary"]["caseCount"] == 1
    assert fit_finding_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    filtered_render = render_fit_summary(ROOT, fit_kind="record_support")
    assert "Single-Case Guide" in filtered_render
    assert "Recommended First Stop: summary.json" in filtered_render
    ranked = build_fit_summary_data(ROOT, sort_key="warningCount", top_n=2)
    assert len(ranked["cases"]) == 2


def test_case_matrix_cli_supports_fit_findings_mode():
    findings = render_fit_findings(ROOT)
    assert "Fit Findings" in findings
    assert "Analogical Cases: 3" in findings
    assert "Record-Support Cases: 1" in findings
    assert "Fit Finding Filter: any" in findings
    payload = build_fit_findings_data(ROOT)
    validate_with_schema(payload, load_schema("fit_findings.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    warning_only = build_fit_findings_data(ROOT, severity="warning")
    assert warning_only["summary"]["caseCount"] == 4
    gap_only = build_fit_findings_data(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert gap_only["summary"]["recordSupportCases"] == 1
    assert gap_only["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_finding_only = build_fit_findings_data(ROOT, fit_finding="record_support_heavy")
    assert fit_finding_only["summary"]["caseCount"] == 1
    assert fit_finding_only["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_fit_findings_summary_mode():
    summary = render_fit_findings_summary(ROOT)
    assert "Fit Findings Summary" in summary
    assert "Analogical Cases: 3" in summary
    assert "Record-Support Cases: 1" in summary
    assert "Fit Finding Filter: any" in summary
    payload = build_fit_findings_summary_data(ROOT)
    validate_with_schema(payload, load_schema("fit_findings_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    warning_only = build_fit_findings_summary_data(ROOT, severity="warning")
    assert warning_only["summary"]["caseCount"] == 4
    gap_only = build_fit_findings_summary_data(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert gap_only["summary"]["recordSupportCases"] == 1
    assert gap_only["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_finding_only = build_fit_findings_summary_data(ROOT, fit_finding="record_support_heavy")
    assert fit_finding_only["summary"]["caseCount"] == 1
    assert fit_finding_only["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert gap_only["singleCaseGuide"] == {
        "caseId": "live_in_aide_case_no_violation_001",
        "recommendedFirstStop": "summary.json",
        "whyOpenThis": "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review.",
    }
    gap_render = render_fit_findings_summary(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert "Single-Case Guide" in gap_render
    assert "Recommended First Stop: summary.json" in gap_render


def test_case_matrix_cli_supports_audit_index_mode():
    audit_index = render_audit_index(ROOT)
    assert "Audit Index" in audit_index
    assert "Recommended First Stop: outputs/case_audit_matrix.json" in audit_index
    assert (
        "Why Open This: Start with the case-audit matrix because it is the strongest joined repo-level view of confidence, trust, fit findings, warnings, and package posture."
        in audit_index
    )
    assert "Priority | Kind | JSON | Markdown | Why Open This | Description" in audit_index
    payload = build_audit_index_data(ROOT)
    validate_with_schema(payload, load_schema("audit_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["refreshRuntime"]["elapsedHuman"] is not None
    assert payload["recommendedFirstStop"] == "outputs/case_audit_matrix.json"
    assert (
        payload["whyOpenThis"]
        == "Start with the case-audit matrix because it is the strongest joined repo-level view of confidence, trust, fit findings, warnings, and package posture."
    )
    entries = {item["kind"] for item in payload["entries"]}
    assert "authority_summary_matrix" in entries
    assert "source_metadata_matrix" in entries
    assert "warning_label_matrix" in entries
    by_kind = {item["kind"]: item for item in payload["entries"]}
    assert by_kind["case_audit_matrix"]["priorityHint"] == "recommended"
    assert (
        by_kind["case_audit_matrix"]["whyOpenThis"]
        == "Open this first when you want the strongest joined repo-level audit view before following narrower reports."
    )


def test_case_matrix_cli_supports_case_audit_matrix_mode():
    matrix = render_case_audit_matrix(ROOT)
    assert "Case Audit Matrix" in matrix
    assert "Trust Filter: any" in matrix
    assert "Warning Label Filter: any" in matrix
    assert "Fit Finding Filter: any" in matrix
    assert "Warned Only: no" in matrix
    assert "Case ID | Branch | Outcome | Confidence | Trust | Fit Finding | Primary | Primary Why | Warnings | Warning Count | Warning Label | Package" in matrix
    payload = build_case_audit_matrix_data(ROOT)
    validate_with_schema(payload, load_schema("case_audit_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    by_case = {item["caseId"]: item for item in payload["cases"]}
    assert by_case["live_in_aide_case_001"]["fitFinding"] == "analogical_support"
    assert (
        by_case["live_in_aide_case_001"]["primaryWhy"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert by_case["live_in_aide_case_no_violation_001"]["warningLabel"] == "paraphrase_heavy"
    assert by_case["live_in_aide_case_no_violation_001"]["fitFinding"] == "record_support_heavy"
    assert (
        by_case["live_in_aide_case_no_violation_001"]["primaryWhy"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    sorted_payload = build_case_audit_matrix_data(ROOT, sort_key="confidence")
    assert sorted_payload["cases"][0]["caseId"] == "live_in_aide_case_001"
    branch_sorted = build_case_audit_matrix_data(ROOT, sort_key="branch")
    assert branch_sorted["cases"][0]["branch"] == "constructive_denial"
    trust_filtered = build_case_audit_matrix_data(ROOT, trust="mixed_support")
    assert len(trust_filtered["cases"]) == 2
    warning_label_filtered = build_case_audit_matrix_data(ROOT, warning_label="paraphrase_heavy")
    assert len(warning_label_filtered["cases"]) == 1
    assert warning_label_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_finding_filtered = build_case_audit_matrix_data(ROOT, fit_finding="record_support_heavy")
    assert len(fit_finding_filtered["cases"]) == 1
    assert fit_finding_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    warned_only = build_case_audit_matrix_data(ROOT, warned_only=True)
    assert len(warned_only["cases"]) == 3
    assert all(item["hasWarnings"] for item in warned_only["cases"])


def test_case_matrix_cli_render_contains_all_branches():
    matrix = render_case_matrix(ROOT)
    assert "Warning Label Filter: any" in matrix
    assert "Fit Finding Filter: any" in matrix
    assert "Case ID | Branch | Outcome | Conf | Trust | Fit Finding | Warn | WarnCt | Primary | Primary Why | Package | Key Package Entries" in matrix
    assert "live_in_aide_case_001 | constructive_denial | violation | 0.93 | fully_verified | analogical_support | no | 0 | memorandum_pdf | Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review." in matrix
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | no_violation | 0.58 | mixed_support | analogical_support | yes | 16 | memorandum_markdown | Start with the editable memorandum because it is the clearest working draft for effective_accommodation review." in matrix
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | 0.57 | paraphrase_heavy | record_support_heavy | yes | 16 | summary | Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review." in matrix
    assert "live_in_aide_case_undue_burden_001 | undue_burden_constructive_denial | violation | 0.83 | mixed_support | analogical_support | yes | 16 | memorandum_pdf | Start with the printable memorandum because it is the strongest branch-aligned narrative for undue_burden_constructive_denial review." in matrix
    assert "advocacy=advocacy_bundle.json" in matrix
    assert "memo=memorandum_of_law.pdf" in matrix


def test_case_matrix_cli_supports_json_and_branch_filter():
    data = build_case_matrix_data(ROOT, branch="constructive_denial")
    assert len(data["cases"]) == 1
    case = data["cases"][0]
    assert case["caseId"] == "live_in_aide_case_001"
    assert case["branch"] == "constructive_denial"
    assert case["authorityTrust"] == "fully_verified"
    assert case["sourceSummary"]["sourceVerifiedCount"] == 5
    assert case["sourceSummary"]["sourceNormalizedCount"] == 5
    assert case["fitFindingSummary"]["fitFinding"] == "analogical_support"
    assert case["warningSummary"]["hasWarnings"] is False
    assert case["primaryKind"] == "memorandum_pdf"
    assert (
        case["primaryEntryWhyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert case["recommendedFirstStop"] == "memorandum_of_law.pdf"
    assert (
        case["whyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
    )
    assert case["entries"]["advocacy"] == "advocacy_bundle.json"
    assert case["entries"]["memorandum"] == "memorandum_of_law.pdf"
    assert "topEntries" not in case
    filtered_matrix = render_case_matrix(ROOT, branch="effective_accommodation")
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | no_violation" in filtered_matrix
    assert "live_in_aide_case_001 | constructive_denial | violation" not in filtered_matrix


def test_case_matrix_cli_supports_trust_filter():
    data = build_case_matrix_data(ROOT, trust="paraphrase_heavy")
    assert len(data["cases"]) == 1
    assert data["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert data["cases"][0]["authorityTrust"] == "paraphrase_heavy"
    assert (
        data["cases"][0]["primaryEntryWhyOpenThis"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    assert data["cases"][0]["recommendedFirstStop"] == "summary.json"
    assert (
        data["cases"][0]["whyOpenThis"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    warning_label_data = build_case_matrix_data(ROOT, warning_label="paraphrase_heavy")
    assert len(warning_label_data["cases"]) == 1
    assert warning_label_data["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    fit_finding_data = build_case_matrix_data(ROOT, fit_finding="record_support_heavy")
    assert len(fit_finding_data["cases"]) == 1
    assert fit_finding_data["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    filtered_matrix = render_case_matrix(ROOT, trust="mixed_support")
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | no_violation | 0.58 | mixed_support | analogical_support" in filtered_matrix
    assert "live_in_aide_case_undue_burden_001 | undue_burden_constructive_denial | violation | 0.83 | mixed_support | analogical_support" in filtered_matrix
    assert "live_in_aide_case_001 | constructive_denial | violation | 0.93 | fully_verified | analogical_support" not in filtered_matrix
    label_filtered_matrix = render_case_matrix(ROOT, warning_label="paraphrase_heavy")
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | 0.57 | paraphrase_heavy | record_support_heavy" in label_filtered_matrix
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | no_violation" not in label_filtered_matrix
    fit_filtered_matrix = render_case_matrix(ROOT, fit_finding="record_support_heavy")
    assert "Fit Finding Filter: record_support_heavy" in fit_filtered_matrix
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | no_violation | 0.57 | paraphrase_heavy | record_support_heavy" in fit_filtered_matrix
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | no_violation" not in fit_filtered_matrix
    warned_cases = build_case_matrix_data(ROOT, warned_only=True)
    assert len(warned_cases["cases"]) == 3
    assert all(case["warningSummary"]["hasWarnings"] for case in warned_cases["cases"])
    try:
        build_case_matrix_data(ROOT, warning_label="bad_label")
    except ValueError as exc:
        assert "warning-label must be one of" in str(exc)
    else:
        raise AssertionError("case-matrix mode should reject invalid warning labels")
    try:
        build_case_matrix_data(ROOT, fit_finding="bad_finding")
    except ValueError as exc:
        assert "fit-finding must be one of" in str(exc)
    else:
        raise AssertionError("case-matrix mode should reject invalid fit-finding labels")


def test_case_matrix_cli_supports_sort_and_case_id_filter():
    sorted_data = build_case_matrix_data(ROOT, sort_key="confidence")
    assert sorted_data["cases"][0]["caseId"] == "live_in_aide_case_001"
    assert sorted_data["cases"][-1]["caseId"] == "live_in_aide_case_no_violation_001"
    branch_sorted = build_case_matrix_data(ROOT, sort_key="branch")
    assert branch_sorted["cases"][0]["branch"] == "constructive_denial"
    single_case = build_case_matrix_data(ROOT, case_id="live_in_aide_case_undue_burden_001")
    assert len(single_case["cases"]) == 1
    assert single_case["cases"][0]["caseId"] == "live_in_aide_case_undue_burden_001"
    filtered_matrix = render_case_matrix(ROOT, case_id="live_in_aide_case_undue_burden_001")
    assert "live_in_aide_case_undue_burden_001 | undue_burden_constructive_denial | violation" in filtered_matrix
    assert "live_in_aide_case_001 | constructive_denial | violation" not in filtered_matrix


def test_case_matrix_cli_supports_detail_view():
    detail = render_case_detail(ROOT, case_id="live_in_aide_case_001")
    assert "Case ID: live_in_aide_case_001" in detail
    assert "Authority Trust: fully_verified" in detail
    assert "Source Verified Count: 5" in detail
    assert "Source Normalized Count: 5" in detail
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in detail
    assert "Direct Fit Count: 3" in detail
    assert "Analogical Fit Count: 2" in detail
    assert "Record-Support Fit Count: 0" in detail
    assert "Fit Status: This package includes analogical authority mappings." in detail
    assert "Fit Finding: analogical_support" in detail
    assert "Warnings: no" in detail
    assert "Warning Label: none" in detail
    assert "Warning Entry Count: 0" in detail
    assert "Primary Kind: memorandum_pdf" in detail
    assert "Recommended First Stop: memorandum_of_law.pdf" in detail
    assert (
        "Why Open This: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        in detail
    )
    assert "Entries:" in detail
    assert "- advocacy_bundle [json] priority=5 (supporting) -> advocacy_bundle.json" in detail
    assert "whyOpenThis: Open this when you want the structured drafting and citation payload that drives the advocacy outputs." in detail
    assert "- memorandum_pdf [pdf] priority=1 (primary) [primary] -> memorandum_of_law.pdf" in detail
    assert "whyOpenThis: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review." in detail
    assert "- dependency_citations [jsonld] priority=12 (supporting) -> dependency_citations.jsonld" in detail
    try:
        render_case_detail(ROOT)
    except ValueError as exc:
        assert "detail view requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("detail view should reject ambiguous requests")
    effective_detail = render_case_detail(ROOT, case_id="live_in_aide_case_effective_accommodation_001")
    assert "Warnings: yes" in effective_detail
    assert "Warning Label: mixed_support" in effective_detail
    assert "Source Verified Count: 5" in effective_detail
    assert "Source Normalized Count: 5" in effective_detail
    assert "Direct Fit Count: 3" in effective_detail
    assert "Analogical Fit Count: 2" in effective_detail
    assert "Warning Entry Count: 15" in effective_detail
    assert "Warning Counts: {'mixed_support': 15}" in effective_detail
    assert "Primary Kind: memorandum_markdown" in effective_detail
    assert "Recommended First Stop: memorandum.md" in effective_detail
    assert (
        "Why Open This: Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
        in effective_detail
    )
    assert "whyOpenThis: Start with the editable memorandum because it is the clearest working draft for effective_accommodation review." in effective_detail
    assert "- memorandum_markdown [markdown] priority=1 (primary) [primary] -> memorandum.md" in effective_detail
    assert "trustWarning: mixed_support (warning)" in effective_detail
    gap_detail = render_case_detail(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert "Warnings: yes" in gap_detail
    assert "Warning Label: paraphrase_heavy" in gap_detail
    assert "Source Verified Count: 5" in gap_detail
    assert "Source Normalized Count: 5" in gap_detail
    assert "Direct Fit Count: 1" in gap_detail
    assert "Analogical Fit Count: 1" in gap_detail
    assert "Recommended First Stop: summary.json" in gap_detail
    assert (
        "Why Open This: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        in gap_detail
    )
    assert "whyOpenThis: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review." in gap_detail
    assert "Record-Support Fit Count: 3" in gap_detail
    assert "Warning Entry Count: 15" in gap_detail
    assert "Warning Counts: {'paraphrase_heavy': 15}" in gap_detail
    assert "Primary Kind: summary" in gap_detail
    assert "- summary [json] priority=1 (primary) [primary] -> summary.json" in gap_detail
    assert "trustWarning: paraphrase_heavy (warning)" in gap_detail
    assert "lower-trust" in gap_detail.lower()
    label_filtered_detail = render_case_detail(ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy")
    assert "Case ID: live_in_aide_case_no_violation_001" in label_filtered_detail
    warned_detail = render_case_detail(ROOT, case_id="live_in_aide_case_no_violation_001", warned_only=True)
    assert "trustWarning: paraphrase_heavy (warning)" in warned_detail
    clean_warned_detail = render_case_detail(ROOT, case_id="live_in_aide_case_001", warned_only=True)
    assert "Entries:" in clean_warned_detail
    assert "- " not in clean_warned_detail.split("Entries:\n", 1)[1]


def test_case_matrix_cli_supports_path_only_mode():
    path = resolve_artifact_path(ROOT, case_id="live_in_aide_case_001", kind="memorandum_pdf")
    assert path.endswith("/workspace2/outputs/live_in_aide_case_001_package/memorandum_of_law.pdf")
    advocacy_path = resolve_artifact_path(ROOT, branch="constructive_denial", kind="advocacy_bundle")
    assert advocacy_path.endswith("/workspace2/outputs/live_in_aide_case_001_package/advocacy_bundle.json")
    label_filtered_path = resolve_artifact_path(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy", kind="summary"
    )
    assert label_filtered_path.endswith("/workspace2/outputs/live_in_aide_case_no_violation_001_package/summary.json")
    try:
        resolve_artifact_path(ROOT, case_id="live_in_aide_case_001")
    except ValueError as exc:
        assert "path-only mode requires --kind" in str(exc)
    else:
        raise AssertionError("path-only mode should require a kind")


def test_case_matrix_cli_supports_kinds_mode():
    kinds = list_artifact_kinds(ROOT, case_id="live_in_aide_case_001")
    assert "summary" in kinds
    assert "advocacy_bundle" in kinds
    assert "memorandum_pdf" in kinds
    assert "dependency_citations" in kinds
    warned_kinds = list_artifact_kinds(ROOT, case_id="live_in_aide_case_no_violation_001", warned_only=True)
    assert "summary" in warned_kinds
    label_filtered_kinds = list_artifact_kinds(ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy")
    assert "summary" in label_filtered_kinds
    try:
        list_artifact_kinds(ROOT)
    except ValueError as exc:
        assert "kinds mode requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("kinds mode should reject ambiguous requests")


def test_case_matrix_cli_supports_primary_only_mode():
    path = resolve_primary_artifact_path(ROOT, case_id="live_in_aide_case_001")
    assert path.endswith("/workspace2/outputs/live_in_aide_case_001_package/memorandum_of_law.pdf")
    effective_path = resolve_primary_artifact_path(ROOT, case_id="live_in_aide_case_effective_accommodation_001")
    assert effective_path.endswith("/workspace2/outputs/live_in_aide_case_effective_accommodation_001_package/memorandum.md")
    gap_path = resolve_primary_artifact_path(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert gap_path.endswith("/workspace2/outputs/live_in_aide_case_no_violation_001_package/summary.json")
    label_filtered_gap_path = resolve_primary_artifact_path(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy"
    )
    assert label_filtered_gap_path.endswith("/workspace2/outputs/live_in_aide_case_no_violation_001_package/summary.json")
    warned_gap_path = resolve_primary_artifact_path(ROOT, case_id="live_in_aide_case_no_violation_001", warned_only=True)
    assert warned_gap_path.endswith("/workspace2/outputs/live_in_aide_case_no_violation_001_package/summary.json")
    try:
        resolve_primary_artifact_path(ROOT)
    except ValueError as exc:
        assert "primary-only mode requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("primary-only mode should reject ambiguous requests")


def test_case_matrix_cli_supports_describe_kind_mode():
    description = describe_artifact_kind(ROOT, case_id="live_in_aide_case_001", kind="memorandum_pdf")
    assert "memorandum_pdf [primary]" in description
    assert "authorityTrust: fully_verified" in description
    assert "sourceVerifiedCount: 5" in description
    assert "sourceNormalizedCount: 5" in description
    assert "sourceStatus: All authority entries are sourceVerified and sourceNormalized." in description
    assert "directFitCount: 3" in description
    assert "analogicalFitCount: 2" in description
    assert "recordSupportFitCount: 0" in description
    assert "fitStatus: This package includes analogical authority mappings." in description
    assert "fitFinding: analogical_support" in description
    assert "warnings: no" in description
    assert "warningLabel: none" in description
    assert "warningEntryCount: 0" in description
    assert "recommendedFirstStop: memorandum_of_law.pdf" in description
    assert (
        "whyOpenThis: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review."
        in description
    )
    assert "entryWhyOpenThis: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review." in description
    assert "format: pdf" in description
    assert "path: memorandum_of_law.pdf" in description
    assert "priority: 1" in description
    assert "priorityLabel: primary" in description
    assert "trustWarning:" not in description
    gap_description = describe_artifact_kind(ROOT, case_id="live_in_aide_case_no_violation_001", kind="summary")
    assert "authorityTrust: paraphrase_heavy" in gap_description
    assert "sourceVerifiedCount: 5" in gap_description
    assert "sourceNormalizedCount: 5" in gap_description
    assert "directFitCount: 1" in gap_description
    assert "analogicalFitCount: 1" in gap_description
    assert "recordSupportFitCount: 3" in gap_description
    assert "fitFinding: record_support_heavy" in gap_description
    assert "recommendedFirstStop: summary.json" in gap_description
    assert (
        "whyOpenThis: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        in gap_description
    )
    assert "entryWhyOpenThis: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review." in gap_description
    assert "warnings: yes" in gap_description
    assert "warningLabel: paraphrase_heavy" in gap_description
    assert "warningEntryCount: 16" in gap_description
    assert "trustWarning: paraphrase_heavy (warning)" in gap_description
    assert "lower-trust" in gap_description.lower()
    warned_gap_description = describe_artifact_kind(ROOT, case_id="live_in_aide_case_no_violation_001", kind="summary", warned_only=True)
    assert "trustWarning: paraphrase_heavy (warning)" in warned_gap_description
    label_filtered_gap_description = describe_artifact_kind(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy", kind="summary"
    )
    assert "authorityTrust: paraphrase_heavy" in label_filtered_gap_description
    try:
        describe_artifact_kind(ROOT, case_id="live_in_aide_case_001", kind="missing_kind")
    except ValueError as exc:
        assert "unknown kind 'missing_kind'" in str(exc)
    else:
        raise AssertionError("describe-kind mode should reject unknown kinds")


def test_case_matrix_cli_supports_authority_review_mode():
    review = render_authority_review(ROOT, case_id="live_in_aide_case_001")
    assert "Case ID: live_in_aide_case_001" in review
    assert "Authority Review:" in review
    assert "- giebeler [verified_quote]" in review
    assert "fit:" in review
    assert "source: https://law.justia.com/cases/federal/appellate-courts/F3/343/1143/636375/" in review
    assert "Warning Label Filter: any" in review
    filtered = render_authority_review(ROOT, case_id="live_in_aide_case_001", verified_only=True)
    assert "Verified Only: yes" in filtered
    assert "Support Status: verified_quote" in filtered
    assert "- giebeler [verified_quote]" in filtered
    fit_filtered = render_authority_review(ROOT, case_id="live_in_aide_case_001", fit_kind="analogical")
    assert "Fit Kind: analogical" in fit_filtered
    assert "- giebeler [verified_quote]" in fit_filtered
    assert "- mcgary [verified_quote]" in fit_filtered
    assert "california_mobile_home" not in fit_filtered
    json_payload = build_authority_review_data(ROOT, case_id="live_in_aide_case_001", support_status="verified_quote")
    assert json_payload["supportStatus"] == "verified_quote"
    assert json_payload["authorities"][0]["supportStatus"] == "verified_quote"
    fit_payload = build_authority_review_data(ROOT, case_id="live_in_aide_case_001", fit_kind="analogical")
    assert fit_payload["fitKind"] == "analogical"
    assert len(fit_payload["authorities"]) == 2
    assert all(item["fitKind"] == "analogical" for item in fit_payload["authorities"])
    label_filtered_payload = build_authority_review_data(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy"
    )
    assert label_filtered_payload["caseId"] == "live_in_aide_case_no_violation_001"
    try:
        render_authority_review(ROOT)
    except ValueError as exc:
        assert "authority-review mode requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("authority-review mode should reject ambiguous requests")
    try:
        build_authority_review_data(ROOT, case_id="live_in_aide_case_001", support_status="bad_status")
    except ValueError as exc:
        assert "support-status must be one of" in str(exc)
    else:
        raise AssertionError("authority-review mode should reject invalid support-status values")
    try:
        build_authority_review_data(ROOT, case_id="live_in_aide_case_001", fit_kind="bad_fit")
    except ValueError as exc:
        assert "fit must be one of" in str(exc)
    else:
        raise AssertionError("authority-review mode should reject invalid fit values")


def test_case_matrix_cli_supports_authority_research_note_mode():
    note = render_authority_research_note(ROOT, case_id="live_in_aide_case_001")
    assert "Case ID: live_in_aide_case_001" in note
    assert "Authority Research Note:" in note
    assert "- giebeler [verified_quote]" in note
    assert "source verified: yes" in note
    assert "source normalized: yes" in note
    assert "source ref: 1155" in note
    assert "Warning Label Filter: any" in note
    assert "Source Verified Only: no" in note
    assert "Source Normalized Only: no" in note
    assert "Fit Kind: any" in note
    json_payload = build_authority_research_note_data(ROOT, case_id="live_in_aide_case_001")
    assert json_payload["caseId"] == "live_in_aide_case_001"
    assert json_payload["entryCount"] == 5
    assert json_payload["entries"][0]["sourceVerified"] is True
    assert json_payload["entries"][0]["sourceNormalized"] is True
    verified_only_payload = build_authority_research_note_data(
        ROOT, case_id="live_in_aide_case_001", source_verified_only=True
    )
    assert verified_only_payload["entryCount"] == 5
    normalized_only_payload = build_authority_research_note_data(
        ROOT, case_id="live_in_aide_case_001", source_normalized_only=True
    )
    assert normalized_only_payload["entryCount"] == 5
    fit_only_payload = build_authority_research_note_data(
        ROOT, case_id="live_in_aide_case_001", fit_kind="analogical"
    )
    assert fit_only_payload["fitKind"] == "analogical"
    assert fit_only_payload["entryCount"] == 2
    assert all(item["fitKind"] == "analogical" for item in fit_only_payload["entries"])
    label_filtered_payload = build_authority_research_note_data(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy"
    )
    assert label_filtered_payload["caseId"] == "live_in_aide_case_no_violation_001"
    fit_note = render_authority_research_note(ROOT, case_id="live_in_aide_case_001", fit_kind="analogical")
    assert "Fit Kind: analogical" in fit_note
    assert "- giebeler [verified_quote]" in fit_note
    assert "- mcgary [verified_quote]" in fit_note
    assert "california_mobile_home" not in fit_note
    try:
        render_authority_research_note(ROOT)
    except ValueError as exc:
        assert "authority-research-note mode requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("authority-research-note mode should reject ambiguous requests")
    try:
        build_authority_research_note_data(ROOT, case_id="live_in_aide_case_001", fit_kind="bad_fit")
    except ValueError as exc:
        assert "fit must be one of" in str(exc)
    else:
        raise AssertionError("authority-research-note mode should reject invalid fit values")


def test_case_matrix_cli_subprocess_supports_authority_review_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-review",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
            "--support-status",
            "verified_quote",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_001"
    assert payload["supportStatus"] == "verified_quote"
    assert payload["authorities"]
    assert all(item["supportStatus"] == "verified_quote" for item in payload["authorities"])


def test_case_matrix_cli_subprocess_supports_authority_review_fit_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-review",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
            "--fit",
            "analogical",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["fitKind"] == "analogical"
    assert len(payload["authorities"]) == 2
    assert all(item["fitKind"] == "analogical" for item in payload["authorities"])


def test_case_matrix_cli_subprocess_supports_authority_review_warning_label_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-review",
            "--json",
            "--case-id",
            "live_in_aide_case_no_violation_001",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_authority_research_note_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-research-note",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_001"
    assert payload["entryCount"] == 5
    assert payload["entries"][0]["sourceReference"]
    assert len(payload["entries"]) == 5


def test_case_matrix_cli_subprocess_supports_authority_research_note_source_filters():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-research-note",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
            "--source-normalized-only",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_001"
    assert payload["entryCount"] == 5
    assert all(item["sourceNormalized"] for item in payload["entries"])


def test_case_matrix_cli_subprocess_supports_authority_research_note_fit_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-research-note",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
            "--fit",
            "analogical",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_001"
    assert payload["fitKind"] == "analogical"
    assert payload["entryCount"] == 2
    assert all(item["fitKind"] == "analogical" for item in payload["entries"])


def test_case_matrix_cli_supports_authority_summary_mode():
    summary = render_authority_review_summary(ROOT, case_id="live_in_aide_case_001")
    assert "Case ID: live_in_aide_case_001" in summary
    assert "Warning Label Filter: any" in summary
    assert "Fit Kind: any" in summary
    assert "Authority Count: 5" in summary
    assert "Status Counts:" in summary
    assert "- verified_quote: 5" in summary
    assert "Bucket Counts:" in summary
    assert "- violation: 3" in summary
    filtered_summary = build_authority_review_summary(
        ROOT,
        case_id="live_in_aide_case_001",
        support_status="verified_quote",
    )
    validate_with_schema(filtered_summary, load_schema("authority_summary.schema.json"))
    assert filtered_summary["authorityCount"] == 5
    assert filtered_summary["statusCounts"]["verified_quote"] == 5
    fit_filtered_summary = build_authority_review_summary(
        ROOT,
        case_id="live_in_aide_case_001",
        fit_kind="analogical",
    )
    assert fit_filtered_summary["fitKind"] == "analogical"
    assert fit_filtered_summary["authorityCount"] == 2
    full_summary = build_authority_review_summary(ROOT, case_id="live_in_aide_case_001")
    validate_with_schema(full_summary, load_schema("authority_summary.schema.json"))
    assert full_summary["supportStatus"] is None
    label_filtered_summary = build_authority_review_summary(
        ROOT, case_id="live_in_aide_case_no_violation_001", warning_label="paraphrase_heavy"
    )
    assert label_filtered_summary["caseId"] == "live_in_aide_case_no_violation_001"
    try:
        render_authority_review_summary(ROOT)
    except ValueError as exc:
        assert "authority-review mode requires exactly one matching case" in str(exc)
    else:
        raise AssertionError("authority-summary mode should reject ambiguous requests")


def test_case_matrix_cli_subprocess_supports_authority_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-summary",
            "--json",
            "--case-id",
            "live_in_aide_case_001",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_001"
    assert payload["authorityCount"] == 5
    assert payload["statusCounts"]["verified_quote"] == 5
    assert payload["bucketCounts"]["violation"] == 4


def test_case_matrix_cli_subprocess_supports_authority_summary_warning_label_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-summary",
            "--json",
            "--case-id",
            "live_in_aide_case_no_violation_001",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["authorityCount"] == 5


def test_case_matrix_cli_supports_authority_summary_matrix_mode():
    matrix = render_authority_summary_matrix(ROOT)
    markdown_matrix = render_authority_summary_matrix_markdown(ROOT)
    assert "Warning Label Filter: any" in matrix
    assert "Case ID | Branch | Authorities | Verified Only | Support Status | Status Counts | Bucket Counts" in matrix
    assert "live_in_aide_case_001 | constructive_denial | 5 | no | any | verified_quote=5 | constructiveDenial=2, dutyToGrant=4, necessary=2, reasonable=4, violation=4" in matrix
    assert "live_in_aide_case_effective_accommodation_001 | effective_accommodation | 5 | no | any | paraphrase=2, verified_quote=3 | constructiveDenial=1, dutyToGrant=3, necessary=2, reasonable=4, violation=2" in matrix
    assert "live_in_aide_case_no_violation_001 | evidentiary_gap | 5 | no | any | paraphrase=3, verified_quote=2 | constructiveDenial=1, dutyToGrant=2, necessary=2, reasonable=4, violation=1" in matrix
    assert markdown_matrix.startswith("# Authority Summary Matrix")
    assert "Verified Only: `no`" in markdown_matrix
    filtered = build_authority_summary_matrix(ROOT, branch="constructive_denial", support_status="verified_quote")
    validate_with_schema(filtered, load_schema("authority_summary_matrix.schema.json"))
    assert filtered["supportStatus"] == "verified_quote"
    assert len(filtered["cases"]) == 1
    assert filtered["cases"][0]["caseId"] == "live_in_aide_case_001"
    full_matrix = build_authority_summary_matrix(ROOT)
    validate_with_schema(full_matrix, load_schema("authority_summary_matrix.schema.json"))
    assert len(full_matrix["cases"]) == 4
    trust_filtered = build_authority_summary_matrix(ROOT, trust="paraphrase_heavy")
    assert len(trust_filtered["cases"]) == 1
    assert trust_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    label_filtered = build_authority_summary_matrix(ROOT, warning_label="paraphrase_heavy")
    assert len(label_filtered["cases"]) == 1
    assert label_filtered["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_supports_authority_findings_mode():
    findings = render_authority_findings(ROOT)
    assert "Authority Findings" in findings
    assert "Fully Verified Cases: 1" in findings
    assert "- live_in_aide_case_001 [info] Fully verified authority baseline (constructive_denial)" in findings
    warning_only = build_authority_findings_data(ROOT, severity="warning")
    assert len(warning_only["findings"]) == 3
    assert all(item["severity"] == "warning" for item in warning_only["findings"])
    mixed_only = build_authority_findings_data(ROOT, trust="mixed_support")
    assert len(mixed_only["findings"]) == 2
    assert all(item["caseId"] in {"live_in_aide_case_effective_accommodation_001", "live_in_aide_case_undue_burden_001"} for item in mixed_only["findings"])
    paraphrase_only = build_authority_findings_data(ROOT, warning_label="paraphrase_heavy")
    assert len(paraphrase_only["findings"]) == 1
    assert paraphrase_only["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    gap_only = build_authority_findings_data(ROOT, case_id="live_in_aide_case_no_violation_001")
    assert len(gap_only["findings"]) == 1
    assert gap_only["findings"][0]["title"] == "Paraphrase-heavy authority support"


def test_case_matrix_cli_subprocess_supports_authority_findings_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-findings",
            "--json",
            "--severity",
            "warning",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("authority_findings.schema.json"))
    assert len(payload["findings"]) == 3
    assert all(item["severity"] == "warning" for item in payload["findings"])


def test_case_matrix_cli_subprocess_supports_authority_findings_trust_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-findings",
            "--json",
            "--trust",
            "mixed_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["findings"]) == 2
    assert {item["caseId"] for item in payload["findings"]} == {
        "live_in_aide_case_effective_accommodation_001",
        "live_in_aide_case_undue_burden_001",
    }


def test_case_matrix_cli_subprocess_supports_authority_findings_warning_label_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-findings",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["findings"]) == 1
    assert payload["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_authority_summary_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-summary",
            "--json",
            "--support-status",
            "verified_quote",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("authority_summary_matrix.schema.json"))
    assert payload["supportStatus"] == "verified_quote"
    assert len(payload["cases"]) == 4
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_001"


def test_case_matrix_cli_subprocess_supports_authority_summary_trust_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--authority-summary",
            "--json",
            "--trust",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_trust_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--trust-matrix",
            "--json",
            "--trust",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("trust_matrix.schema.json"))
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_trust_matrix_warning_label_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--trust-matrix",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("trust_matrix.schema.json"))
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_warning_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-summary",
            "--json",
            "--trust",
            "mixed_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["warnedCaseCount"] == 2
    assert payload["summary"]["warningCounts"]["mixed_support"] == 2


def test_case_matrix_cli_subprocess_supports_warning_summary_warning_label_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-summary",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_summary.schema.json"))
    assert payload["summary"]["warnedCaseCount"] == 1
    assert payload["summary"]["warningCounts"]["paraphrase_heavy"] == 1


def test_case_matrix_cli_subprocess_supports_warning_label_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-label-matrix",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_label_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert list(payload["labels"].keys()) == ["paraphrase_heavy"]
    assert payload["labels"]["paraphrase_heavy"]["summary"]["warnedCaseCount"] == 1


def test_case_matrix_cli_subprocess_supports_warning_entry_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-matrix",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_warning_entry_matrix_trust_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-matrix",
            "--json",
            "--trust",
            "mixed_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_matrix.schema.json"))
    assert len(payload["cases"]) == 2
    assert {item["caseId"] for item in payload["cases"]} == {
        "live_in_aide_case_effective_accommodation_001",
        "live_in_aide_case_undue_burden_001",
    }


def test_case_matrix_cli_subprocess_supports_warning_entry_matrix_sort_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-matrix",
            "--json",
            "--sort",
            "warningCount",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_matrix.schema.json"))
    assert len(payload["cases"]) == 3
    assert payload["cases"][0]["warningEntryCount"] >= payload["cases"][-1]["warningEntryCount"]


def test_case_matrix_cli_subprocess_supports_warning_entry_matrix_warned_kind_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-matrix",
            "--json",
            "--warned-kind",
            "summary",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_matrix.schema.json"))
    assert len(payload["cases"]) == 3
    assert all("summary" in item["warnedKinds"] for item in payload["cases"])


def test_case_matrix_cli_subprocess_supports_warning_entry_matrix_top_n_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-matrix",
            "--json",
            "--sort",
            "warningCount",
            "--top-n",
            "2",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_matrix.schema.json"))
    assert len(payload["cases"]) == 2


def test_case_matrix_cli_subprocess_supports_warning_kind_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-matrix",
            "--json",
            "--warned-kind",
            "summary",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["kindCount"] == 1
    assert payload["kinds"][0]["kind"] == "summary"


def test_case_matrix_cli_subprocess_supports_warning_kind_matrix_trust_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-matrix",
            "--json",
            "--trust",
            "mixed_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_matrix.schema.json"))
    assert payload["summary"]["caseCount"] == 2
    assert all(
        all(case["authorityTrust"] == "mixed_support" for case in item["cases"])
        for item in payload["kinds"]
    )


def test_case_matrix_cli_subprocess_supports_warning_kind_matrix_sort_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-matrix",
            "--json",
            "--sort",
            "warningCount",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_matrix.schema.json"))
    assert payload["kinds"][0]["warningCaseCount"] >= payload["kinds"][-1]["warningCaseCount"]


def test_case_matrix_cli_subprocess_supports_warning_kind_matrix_top_n_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-matrix",
            "--json",
            "--sort",
            "warningCount",
            "--top-n",
            "5",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_matrix.schema.json"))
    assert payload["summary"]["kindCount"] == 5
    assert len(payload["kinds"]) == 5


def test_case_matrix_cli_subprocess_supports_warning_entry_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-summary",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 3
    assert payload["singleCaseGuide"] is None


def test_case_matrix_cli_subprocess_supports_warning_entry_summary_filters():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-summary",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["singleCaseGuide"]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_warning_entry_summary_sort_and_top_n():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-entry-summary",
            "--json",
            "--sort",
            "warningCount",
            "--top-n",
            "2",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_entry_summary.schema.json"))
    assert len(payload["cases"]) == 2


def test_case_matrix_cli_subprocess_supports_warning_kind_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-summary",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["kindCount"] == 16
    assert payload["singleCaseGuide"] is None


def test_case_matrix_cli_subprocess_supports_warning_kind_summary_filters():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-summary",
            "--json",
            "--trust",
            "mixed_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 2
    assert all(item["warningLabels"] == {"mixed_support": 2} for item in payload["kinds"])
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-summary",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_summary.schema.json"))
    assert payload["singleCaseGuide"]["recommendedFirstStop"] == "summary.json"


def test_case_matrix_cli_subprocess_supports_warning_kind_summary_sort_and_top_n():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--warning-kind-summary",
            "--json",
            "--sort",
            "warningCount",
            "--top-n",
            "5",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("warning_kind_summary.schema.json"))
    assert len(payload["kinds"]) == 5


def test_case_matrix_cli_subprocess_supports_summary_index_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--summary-index",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("summary_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"warning_entry_summary", "warning_kind_summary"}


def test_case_matrix_cli_subprocess_supports_fit_index_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-index",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"fit_matrix", "fit_summary", "fit_findings", "fit_findings_summary"}


def test_case_matrix_cli_subprocess_supports_dashboard_index_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--dashboard-index",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("dashboard_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    entries = {item["kind"] for item in payload["entries"]}
    assert entries == {"outputs_index", "summary_index", "fit_index", "fit_findings", "fit_findings_summary", "refresh_state", "audit_index", "dashboard_overview"}


def test_case_matrix_cli_subprocess_supports_trust_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--trust-matrix",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("trust_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False


def test_case_matrix_cli_subprocess_supports_fit_summary_json_refresh_runtime():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-summary",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False


def test_case_matrix_cli_subprocess_supports_case_audit_matrix_refresh_runtime():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--case-audit-matrix",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("case_audit_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False


def test_case_matrix_cli_subprocess_supports_dashboard_overview_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--dashboard-overview",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("dashboard_overview.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 4


def test_case_matrix_cli_subprocess_supports_dashboard_overview_fit_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--dashboard-overview",
            "--json",
            "--fit",
            "record_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("dashboard_overview.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportFitCount"] == 3
    assert payload["featured"]["singleCaseGuide"]["recommendedFirstStop"] == "summary.json"


def test_case_matrix_cli_subprocess_supports_dashboard_overview_fit_finding_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--dashboard-overview",
            "--json",
            "--fit-finding",
            "record_support_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("dashboard_overview.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["featured"]["singleCaseGuide"]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["summary"]["recordSupportCases"] == 1


def test_case_matrix_cli_subprocess_supports_source_metadata_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--source-metadata-matrix",
            "--json",
            "--trust",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("source_metadata_matrix.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-matrix",
            "--json",
            "--trust",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_matrix.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["directCount"] == 1
    assert payload["summary"]["recordSupportCount"] == 3
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_matrix_fit_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-matrix",
            "--json",
            "--fit",
            "record_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_matrix.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportCount"] == 3
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_matrix_fit_finding_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-matrix",
            "--json",
            "--fit-finding",
            "record_support_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_matrix.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-summary",
            "--json",
            "--trust",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportCount"] == 3
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["singleCaseGuide"]["recommendedFirstStop"] == "summary.json"


def test_case_matrix_cli_subprocess_supports_fit_summary_fit_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-summary",
            "--json",
            "--fit",
            "record_support",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportCount"] == 3
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_summary_fit_finding_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-summary",
            "--json",
            "--fit-finding",
            "record_support_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_findings_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-findings",
            "--json",
            "--case-id",
            "live_in_aide_case_no_violation_001",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_findings.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportCases"] == 1
    assert payload["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_findings_fit_finding_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-findings",
            "--json",
            "--fit-finding",
            "record_support_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_findings.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["findings"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_findings_summary_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-findings-summary",
            "--json",
            "--case-id",
            "live_in_aide_case_no_violation_001",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_findings_summary.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["caseCount"] == 1
    assert payload["summary"]["recordSupportCases"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["singleCaseGuide"]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_fit_findings_summary_fit_finding_filter():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--fit-findings-summary",
            "--json",
            "--fit-finding",
            "record_support_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("fit_findings_summary.schema.json"))
    assert payload["summary"]["caseCount"] == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_source_findings_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--source-findings",
            "--json",
            "--severity",
            "info",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("source_findings.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    assert payload["summary"]["fullyNormalizedCases"] == 4
    assert len(payload["findings"]) == 4
    assert all(item["severity"] == "info" for item in payload["findings"])


def test_case_matrix_cli_subprocess_supports_refresh_state_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--refresh-state",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "complete"
    assert payload["startedAt"]
    assert payload["completedAt"]
    assert payload["elapsedSeconds"] is not None
    assert payload["elapsedSeconds"] >= 0
    assert payload["elapsedHuman"] is not None


def test_case_matrix_cli_subprocess_supports_refresh_state_wait_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--refresh-state",
            "--wait-for-refresh-complete",
            "--wait-timeout",
            "0.5",
            "--wait-interval",
            "0.01",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "complete"
    assert payload["elapsedHuman"] is not None


def test_case_matrix_cli_subprocess_supports_refresh_state_fail_fast_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--refresh-state",
            "--fail-if-refresh-running",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["status"] == "complete"
    assert payload["elapsedHuman"] is not None


def test_case_matrix_cli_subprocess_supports_audit_index_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--audit-index",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("audit_index.schema.json"))
    assert payload["refreshRuntime"]["status"] == "complete"
    assert payload["refreshRuntime"]["running"] is False
    entries = {item["kind"] for item in payload["entries"]}
    assert "trust_matrix" in entries
    assert "warning_summary" in entries


def test_case_matrix_cli_subprocess_supports_case_audit_matrix_json_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--case-audit-matrix",
            "--json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    validate_with_schema(payload, load_schema("case_audit_matrix.schema.json"))
    by_case = {item["caseId"]: item for item in payload["cases"]}
    assert by_case["live_in_aide_case_effective_accommodation_001"]["warningLabel"] == "mixed_support"
    assert (
        by_case["live_in_aide_case_effective_accommodation_001"]["primaryWhy"]
        == "Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
    )


def test_case_matrix_cli_subprocess_supports_case_audit_matrix_sort_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--case-audit-matrix",
            "--json",
            "--sort",
            "confidence",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_001"


def test_case_matrix_cli_subprocess_supports_case_audit_matrix_filter_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--case-audit-matrix",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"


def test_case_matrix_cli_subprocess_supports_case_audit_matrix_warned_only_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--case-audit-matrix",
            "--json",
            "--warned-only",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 3
    assert all(item["hasWarnings"] for item in payload["cases"])


def test_case_matrix_cli_subprocess_supports_warned_only_case_matrix_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--json",
            "--warned-only",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 3
    assert {item["caseId"] for item in payload["cases"]} == {
        "live_in_aide_case_effective_accommodation_001",
        "live_in_aide_case_no_violation_001",
        "live_in_aide_case_undue_burden_001",
    }
    assert all(item["warningSummary"]["hasWarnings"] for item in payload["cases"])


def test_case_matrix_cli_subprocess_supports_warning_label_case_matrix_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--json",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["cases"][0]["authorityTrust"] == "paraphrase_heavy"


def test_case_matrix_cli_supports_top_n_mode():
    top = render_top_artifacts(ROOT, case_id="live_in_aide_case_001", top_n=3)
    assert "Case ID: live_in_aide_case_001" in top
    assert "Authority Trust: fully_verified" in top
    assert "Source Verified Count: 5" in top
    assert "Source Normalized Count: 5" in top
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in top
    assert "Direct Fit Count: 3" in top
    assert "Analogical Fit Count: 2" in top
    assert "Record-Support Fit Count: 0" in top
    assert "Fit Status: This package includes analogical authority mappings." in top
    assert "Fit Finding: analogical_support" in top
    assert "Warnings: no" in top
    assert "Warning Label: none" in top
    assert "Warning Entry Count: 0" in top
    assert "Top 3 Entries:" in top
    assert "- memorandum_pdf [pdf] priority=1 (primary) [primary] -> memorandum_of_law.pdf" in top
    assert "whyOpenThis: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review." in top
    assert "- memorandum_markdown [markdown] priority=2 (secondary) -> memorandum.md" in top
    assert "- summary [json] priority=3 (secondary) -> summary.json" in top
    warned_top = render_top_artifacts(ROOT, case_id="live_in_aide_case_no_violation_001", warned_only=True, top_n=2)
    assert "Source Verified Count: 5" in warned_top
    assert "Source Normalized Count: 5" in warned_top
    assert "Direct Fit Count: 1" in warned_top
    assert "Analogical Fit Count: 1" in warned_top
    assert "Record-Support Fit Count: 3" in warned_top
    assert "Fit Finding: record_support_heavy" in warned_top
    assert "Warnings: yes" in warned_top
    assert "Warning Label: paraphrase_heavy" in warned_top
    assert "Warning Entry Count: 15" in warned_top
    assert "- summary [json] priority=1 (primary) [primary] -> summary.json" in warned_top
    assert "whyOpenThis: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review." in warned_top
    assert "trustWarning: paraphrase_heavy (warning)" in warned_top
    try:
        render_top_artifacts(ROOT, case_id="live_in_aide_case_001", top_n=0)
    except ValueError as exc:
        assert "top-n mode requires a positive integer" in str(exc)
    else:
        raise AssertionError("top-n mode should reject non-positive values")


def test_case_matrix_cli_supports_json_top_n_mode():
    data = build_case_matrix_data(ROOT, case_id="live_in_aide_case_001", top_n=2)
    assert len(data["cases"]) == 1
    top_entries = data["cases"][0]["topEntries"]
    assert len(top_entries) == 2
    assert top_entries[0]["kind"] == "memorandum_pdf"
    assert top_entries[0]["priorityLabel"] == "primary"
    assert top_entries[1]["kind"] == "memorandum_markdown"
    warned_data = build_case_matrix_data(ROOT, case_id="live_in_aide_case_no_violation_001", warned_only=True, top_n=2)
    assert warned_data["cases"][0]["topEntries"][0]["kind"] == "summary"
    try:
        build_case_matrix_data(ROOT, case_id="live_in_aide_case_001", top_n=0)
    except ValueError as exc:
        assert "top-n mode requires a positive integer" in str(exc)
    else:
        raise AssertionError("json top-n mode should reject non-positive values")


def test_case_matrix_cli_subprocess_supports_json_top_n_mode():
    result = subprocess.run(
        [sys.executable, "engine/print_case_matrix.py", "--json", "--case-id", "live_in_aide_case_001", "--top-n", "2"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 1
    top_entries = payload["cases"][0]["topEntries"]
    assert len(top_entries) == 2
    assert top_entries[0]["kind"] == "memorandum_pdf"
    assert top_entries[1]["kind"] == "memorandum_markdown"


def test_case_matrix_cli_subprocess_supports_warned_only_mode():
    result = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--detail",
            "--case-id",
            "live_in_aide_case_no_violation_001",
            "--warned-only",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "trustWarning: paraphrase_heavy (warning)" in result.stdout
    clean = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--detail",
            "--case-id",
            "live_in_aide_case_001",
            "--warned-only",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Entries:\n" in clean.stdout
    assert "trustWarning:" not in clean.stdout


def test_case_matrix_cli_subprocess_supports_warning_label_single_case_modes():
    detail = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--detail",
            "--case-id",
            "live_in_aide_case_no_violation_001",
            "--warning-label",
            "paraphrase_heavy",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert "Case ID: live_in_aide_case_no_violation_001" in detail.stdout
    path_only = subprocess.run(
        [
            sys.executable,
            "engine/print_case_matrix.py",
            "--path-only",
            "--case-id",
            "live_in_aide_case_no_violation_001",
            "--warning-label",
            "paraphrase_heavy",
            "--kind",
            "summary",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    assert path_only.stdout.strip().endswith("/workspace2/outputs/live_in_aide_case_no_violation_001_package/summary.json")


def test_case_matrix_cli_subprocess_supports_trust_filter():
    result = subprocess.run(
        [sys.executable, "engine/print_case_matrix.py", "--json", "--trust", "paraphrase_heavy"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    assert len(payload["cases"]) == 1
    assert payload["cases"][0]["caseId"] == "live_in_aide_case_no_violation_001"
    assert payload["cases"][0]["authorityTrust"] == "paraphrase_heavy"


def test_advocacy_outputs_cover_new_chat_modes():
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case.json"))
    assert "supportedModes" in outputs["meta"]
    assert "constructive denial" in outputs["hearing_script"].lower()
    assert "effective in practice" in outputs["hearing_script"].lower()
    assert "fair housing act" in outputs["complaint_outline"].lower()
    assert "separate bedroom" in outputs["demand_letter"].lower()
    assert "leverage points" in outputs["negotiation_summary"].lower()
    assert "Requested remedy:" in outputs["hearing_script"]
    assert "Requested response deadline:" in outputs["demand_letter"]
    assert "Citations:" in outputs["hearing_script"]
    assert "Citations:" in outputs["complaint_outline"]


def test_generated_positive_memorandum_matches_schema():
    bundle = generate_memorandum_bundle(load_fixture("live_in_aide_case.json"))
    validate_with_schema(bundle, load_schema("memorandum.schema.json"))
    assert bundle["meta"]["authorityTrust"]["label"] == "fully_verified"
    assert bundle["meta"]["sourceSummary"]["sourceVerifiedCount"] == 5
    assert bundle["meta"]["sourceSummary"]["sourceNormalizedCount"] == 5
    assert bundle["meta"]["fitSummary"]["directCount"] == 3
    assert bundle["meta"]["fitSummary"]["analogicalCount"] == 2
    assert bundle["meta"]["fitSummary"]["recordSupportCount"] == 0
    assert bundle["sections"][0]["citations"]["targetIds"] == ["dep:node:violation"]
    assert bundle["sections"][1]["citations"]["authorityIds"]
    assert len(bundle["sections"][0]["paragraphCitations"]) == len(bundle["sections"][0]["paragraphs"])
    assert bundle["sections"][0]["paragraphCitations"][0]["targetIds"] == ["dep:node:violation"]
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["court"]
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["year"]
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["pincite"]
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["excerptKind"] == "verified_quote"
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["fitKind"] in {"direct", "analogical", "record_support"}
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["sourceUrl"]
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["sourceVerified"] is True
    assert bundle["sections"][0]["paragraphCitations"][0]["supportLinks"][0]["sourceNormalized"] is True
    assert any(
        item["supportKind"] == "node"
        for item in bundle["sections"][4]["citations"]["supportLinks"]
    )
    assert "### Section Support" in bundle["markdown"]
    assert "### Paragraph Support" in bundle["markdown"]
    assert "[dep:node:violation]" in bundle["markdown"]
    assert "[sourceVerified sourceNormalized]" in bundle["markdown"]
    assert "9th Cir." in bundle["markdown"]
    assert "\"Imposition of burdensome policies" in bundle["markdown"]
    assert "Authority Trust: `fully_verified`" in bundle["markdown"]
    assert "Source Status: All listed authorities are sourceVerified and sourceNormalized." in bundle["markdown"]
    assert "Direct Fit Count: `3`" in bundle["markdown"]
    assert "Analogical Fit Count: `2`" in bundle["markdown"]
    assert "Record-Support Fit Count: `0`" in bundle["markdown"]
    assert "Fit Status: This package includes analogical authority mappings." in bundle["markdown"]
    assert "Fit Finding: `analogical_support`" in bundle["markdown"]


def test_generated_dependency_citations_match_schema():
    grounding = build_dependency_citations_jsonld(load_fixture("live_in_aide_case.json"))
    validate_with_schema(grounding, load_schema("dependency_citations.schema.json"))
    assert any(item["type"] == "DependencySupport" for item in grounding["@graph"])
    assert any(item["type"] == "AuthorityExcerpt" for item in grounding["@graph"])
    authority_nodes = [item for item in grounding["@graph"] if item.get("type") == "LegalAuthority"]
    excerpt_nodes = [item for item in grounding["@graph"] if item.get("type") == "AuthorityExcerpt"]
    assert authority_nodes[0]["court"]
    assert authority_nodes[0]["year"]
    assert authority_nodes[0]["pincite"]
    assert authority_nodes[0]["sourceUrl"]
    assert excerpt_nodes[0]["court"]
    assert excerpt_nodes[0]["year"]
    assert excerpt_nodes[0]["pincite"]
    assert excerpt_nodes[0]["excerptKind"] == "verified_quote"
    assert excerpt_nodes[0]["fitKind"] in {"direct", "analogical", "record_support"}
    assert excerpt_nodes[0]["sourceUrl"]


def test_memorandum_outputs_write_pdf_and_grounding():
    fixture_path = FIXTURE_DIR / "live_in_aide_case.json"
    payload = load_fixture("live_in_aide_case.json")
    bundle = generate_memorandum_bundle(payload)
    grounding = build_dependency_citations_jsonld(payload)
    output_dir = write_memorandum_outputs(fixture_path, bundle, grounding)
    pdf_path = output_dir / "memorandum_of_law.pdf"
    memo_json_path = output_dir / "memorandum.json"
    grounding_path = output_dir / "dependency_citations.jsonld"
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 1000
    validate_with_schema(json.loads(memo_json_path.read_text()), load_schema("memorandum.schema.json"))
    grounding_json = json.loads(grounding_path.read_text())
    validate_with_schema(grounding_json, load_schema("dependency_citations.schema.json"))
    markdown_text = (output_dir / "memorandum.md").read_text()
    assert "Memorandum of Law" in markdown_text
    assert "Source Status: All listed authorities are sourceVerified and sourceNormalized." in markdown_text
    assert "Direct Fit Count: `3`" in markdown_text
    assert "Analogical Fit Count: `2`" in markdown_text
    assert "Record-Support Fit Count: `0`" in markdown_text
    assert "Fit Status: This package includes analogical authority mappings." in markdown_text
    assert "Fit Finding: `analogical_support`" in markdown_text
    assert "### Section Support" in markdown_text
    assert "### Paragraph Support" in markdown_text
    assert "[sourceVerified sourceNormalized]" in markdown_text
    legal_authorities = [item for item in grounding_json["@graph"] if item.get("type") == "LegalAuthority"]
    authority_excerpts = [item for item in grounding_json["@graph"] if item.get("type") == "AuthorityExcerpt"]
    assert legal_authorities
    assert authority_excerpts
    assert all(item["court"] for item in legal_authorities)
    assert all(item["year"] for item in legal_authorities)
    assert all(item["pincite"] for item in legal_authorities)
    assert all(item["court"] for item in authority_excerpts)
    assert all(item["year"] for item in authority_excerpts)
    assert all(item["pincite"] for item in authority_excerpts)


def test_authority_review_markdown_shows_source_badges():
    markdown = build_package_snapshot(ROOT / "outputs" / "live_in_aide_case_001_package")["authority_review.md"]
    assert "Source Verified Count: `5`" in markdown
    assert "Source Normalized Count: `5`" in markdown
    assert "Source Status: All listed authorities are sourceVerified and sourceNormalized." in markdown
    assert "Direct Fit Count: `3`" in markdown
    assert "Analogical Fit Count: `2`" in markdown
    assert "Record-Support Fit Count: `0`" in markdown
    assert "Fit Status: This package includes analogical authority mappings." in markdown
    assert "Fit Finding: `analogical_support`" in markdown
    assert "Badges: `sourceVerified` `sourceNormalized`" in markdown


def test_authority_research_note_markdown_shows_source_badges():
    markdown = build_package_snapshot(ROOT / "outputs" / "live_in_aide_case_001_package")["authority_research_note.md"]
    assert "Source Verified Count: `5`" in markdown
    assert "Source Normalized Count: `5`" in markdown
    assert "Source Status: All listed authorities are sourceVerified and sourceNormalized." in markdown
    assert "Direct Fit Count: `3`" in markdown
    assert "Analogical Fit Count: `2`" in markdown
    assert "Record-Support Fit Count: `0`" in markdown
    assert "Fit Status: This package includes analogical authority mappings." in markdown
    assert "Fit Finding: `analogical_support`" in markdown
    assert "Badges: `sourceVerified` `sourceNormalized`" in markdown


def test_advocacy_bundle_contains_structured_citations():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case.json"))
    assert bundle["meta"]["caseId"] == "live_in_aide_case_001"
    assert bundle["meta"]["branch"] == "constructive_denial"
    assert bundle["meta"]["supportedModes"]
    assert bundle["citations"]["hearing_script"]["findingIds"]
    assert "constructiveDenial" in bundle["citations"]["hearing_script"]["findingIds"]
    assert bundle["citations"]["demand_letter"]["authorityIds"]
    assert bundle["texts"]["demand_letter"]


def test_positive_memorandum_snapshot_matches_current_output():
    bundle = generate_memorandum_bundle(load_fixture("live_in_aide_case.json"))
    snapshot = load_snapshot("live_in_aide_case_001.memorandum.snapshot.json")
    assert bundle == snapshot


def test_effective_accommodation_memorandum_snapshot_matches_current_output():
    bundle = generate_memorandum_bundle(load_fixture("live_in_aide_case_effective_accommodation.json"))
    snapshot = load_snapshot("live_in_aide_case_effective_accommodation_001.memorandum.snapshot.json")
    assert bundle == snapshot


def test_no_violation_memorandum_snapshot_matches_current_output():
    bundle = generate_memorandum_bundle(load_fixture("live_in_aide_case_no_violation.json"))
    snapshot = load_snapshot("live_in_aide_case_no_violation_001.memorandum.snapshot.json")
    assert bundle == snapshot


def test_undue_burden_memorandum_snapshot_matches_current_output():
    bundle = generate_memorandum_bundle(load_fixture("live_in_aide_case_undue_burden.json"))
    snapshot = load_snapshot("live_in_aide_case_undue_burden_001.memorandum.snapshot.json")
    assert bundle == snapshot


def test_no_violation_fixture_and_advocacy_path():
    fixture = load_fixture("live_in_aide_case_no_violation.json")
    validate_with_schema(fixture, inline_case_schema_refs())
    result = evaluate_case(fixture)
    outputs = generate_advocacy_outputs(fixture)
    bundle = generate_advocacy_bundle(fixture)
    assert result["branch"] == "evidentiary_gap"
    assert result["outcome"]["violation"] is False
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["necessary"] is False
    assert bundle["meta"]["authorityTrust"]["label"] == "paraphrase_heavy"
    assert "does not establish constructive denial" in outputs["hearing_script"].lower()
    assert "supplemented until the decision-maker can determine" in outputs["hearing_script"].lower()
    assert "clarification and completion" in outputs["demand_letter"].lower()
    assert "identify it specifically" in outputs["demand_letter"].lower()
    assert "authority grounding as lower-trust" in outputs["demand_letter"].lower()
    assert bundle["citations"]["demand_letter"]["authorityIds"] == []
    assert bundle["citations"]["demand_letter"]["evidenceIds"] == []
    assert bundle["citations"]["demand_letter"]["eventIds"] == []
    assert bundle["meta"]["branch"] == "evidentiary_gap"
    assert bundle["meta"]["placeholders"]["requested_remedy"] == "[Approve a separate bedroom for the live-in aide]"


def test_effective_accommodation_fixture_and_advocacy_path():
    fixture = load_fixture("live_in_aide_case_effective_accommodation.json")
    validate_with_schema(fixture, inline_case_schema_refs())
    result = evaluate_case(fixture)
    outputs = generate_advocacy_outputs(fixture)
    bundle = generate_advocacy_bundle(fixture)
    assert result["branch"] == "effective_accommodation"
    assert result["facts"]["resolved"]["approved_aide_in_principle"] is True
    assert result["facts"]["resolved"]["denied_separate_bedroom"] is False
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is False
    assert bundle["meta"]["authorityTrust"]["label"] == "mixed_support"
    assert "implemented an arrangement that appears effective in practice" in outputs["hearing_script"].lower()
    assert "successfully implemented accommodation" in outputs["hearing_script"].lower()
    assert "preserve effective live-in aide accommodation" in outputs["demand_letter"].lower()
    assert "preserving that arrangement rather than escalating a denial claim" in outputs["demand_letter"].lower()
    assert "will be maintained" in outputs["demand_letter"].lower()
    assert "maintaining compliance and documenting the effective arrangement" in outputs["negotiation_summary"].lower()
    assert bundle["citations"]["demand_letter"]["authorityIds"] == []
    assert bundle["citations"]["demand_letter"]["evidenceIds"] == []
    assert bundle["citations"]["demand_letter"]["eventIds"] == []
    assert bundle["meta"]["branch"] == "effective_accommodation"
    assert bundle["meta"]["placeholders"]["requested_remedy"] == "[Maintain the effective separate-bedroom accommodation for the live-in aide]"


def test_generated_effective_accommodation_result_matches_schema():
    result = evaluate_case(load_fixture("live_in_aide_case_effective_accommodation.json"))
    validate_with_schema(result, load_schema("result.schema.json"))


def test_generated_effective_accommodation_advocacy_bundle_matches_schema():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_effective_accommodation.json"))
    validate_with_schema(bundle, load_schema("advocacy_bundle.schema.json"))


def test_effective_accommodation_result_snapshot_matches_current_output():
    result = evaluate_case(load_fixture("live_in_aide_case_effective_accommodation.json"))
    snapshot = load_snapshot("live_in_aide_case_effective_accommodation_001.result.snapshot.json")
    assert result == snapshot


def test_effective_accommodation_package_snapshot_matches_current_output():
    export_dir = export_package(FIXTURE_DIR / "live_in_aide_case_effective_accommodation.json")
    validate_package_json_files(export_dir)
    current_snapshot = build_package_snapshot(export_dir)
    saved_snapshot = load_snapshot("live_in_aide_case_effective_accommodation_001.package.snapshot.json")
    assert current_snapshot == saved_snapshot
    assert current_snapshot["manifest.json"]["branch"] == "effective_accommodation"
    assert current_snapshot["manifest.json"]["authorityTrust"]["label"] == "mixed_support"
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["manifest.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["manifest.json"]["recommendedFirstStop"] == "memorandum.md"
    assert (
        current_snapshot["manifest.json"]["whyOpenThis"]
        == "Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
    )
    assert any(
        item["path"] == "memorandum.md"
        and item["whyOpenThis"] == "Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
        for item in current_snapshot["manifest.json"]["artifactGuidance"]
    )
    assert current_snapshot["advocacy_bundle.json"]["meta"]["branch"] == "effective_accommodation"
    assert current_snapshot["memorandum.json"]["meta"]["branch"] == "effective_accommodation"
    assert current_snapshot["brief_index.json"]["branch"] == "effective_accommodation"
    assert current_snapshot["brief_index.json"]["primaryKind"] == "memorandum_markdown"
    assert current_snapshot["brief_index.json"]["recommendedFirstStop"] == "memorandum.md"
    assert (
        current_snapshot["brief_index.json"]["whyOpenThis"]
        == "Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
    )
    assert current_snapshot["brief_index.json"]["authorityTrust"]["label"] == "mixed_support"
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["brief_index.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["brief_index.json"]["warningSummary"]["hasWarnings"] is True
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningEntryCount"] == 16
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningCounts"]["mixed_support"] == 16
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["hasWarningLabel"] is True
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningLabel"] == "mixed_support"
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningEntryCount"] == 16
    assert all(item.get("trustWarning", {}).get("label") == "mixed_support" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "memorandum_markdown" and item["priority"] == 1 for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "summary" and item["priorityLabel"] == "secondary" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(
        item["kind"] == "memorandum_markdown"
        and item["whyOpenThis"] == "Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert current_snapshot["decision_tree.json"]["decisionTree"]["activeOutcome"] == "no_violation"
    assert current_snapshot["dependency_graph.json"]["branch"] == "effective_accommodation"
    assert current_snapshot["dependency_graph.json"]["activeOutcome"] == "no_violation"
    assert current_snapshot["summary.json"]["branch"] == "effective_accommodation"
    assert current_snapshot["summary.json"]["activeOutcome"] == "no_violation"
    assert "Authority Trust: `mixed_support`" in current_snapshot["README.md"]
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in current_snapshot["README.md"]
    assert "Direct Fit Count: `3`" in current_snapshot["README.md"]
    assert "Analogical Fit Count: `2`" in current_snapshot["README.md"]
    assert "Fit Status: This package includes analogical authority mappings." in current_snapshot["README.md"]
    assert "Recommended First Stop: `memorandum.md`" in current_snapshot["README.md"]
    assert (
        "Why Open This: Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
        in current_snapshot["README.md"]
    )
    assert (
        "- `memorandum.md`: Start with the editable memorandum because it is the clearest working draft for effective_accommodation review."
        in current_snapshot["README.md"]
    )


def test_effective_accommodation_advocacy_snapshot_matches_current_output():
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case_effective_accommodation.json"))
    snapshot = load_snapshot("live_in_aide_case_effective_accommodation_001.advocacy.snapshot.json")
    assert outputs == snapshot


def test_effective_accommodation_advocacy_bundle_snapshot_matches_current_output():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_effective_accommodation.json"))
    snapshot = load_snapshot("live_in_aide_case_effective_accommodation_001.advocacy_bundle.snapshot.json")
    assert bundle == snapshot


def test_generated_no_violation_result_matches_schema():
    result = evaluate_case(load_fixture("live_in_aide_case_no_violation.json"))
    validate_with_schema(result, load_schema("result.schema.json"))


def test_generated_no_violation_advocacy_bundle_matches_schema():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_no_violation.json"))
    validate_with_schema(bundle, load_schema("advocacy_bundle.schema.json"))


def test_undue_burden_fixture_and_advocacy_path():
    fixture = load_fixture("live_in_aide_case_undue_burden.json")
    validate_with_schema(fixture, inline_case_schema_refs())
    result = evaluate_case(fixture)
    outputs = generate_advocacy_outputs(fixture)
    bundle = generate_advocacy_bundle(fixture)
    assert result["branch"] == "undue_burden_constructive_denial"
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["dutyToGrant"] is False
    assert result["outcome"]["constructiveDenial"] is True
    assert result["outcome"]["violation"] is True
    assert "strongest current theory is constructive denial" in outputs["negotiation_summary"].lower()
    assert "undue-burden defense" in outputs["negotiation_summary"].lower()
    assert "despite undue-burden defense" in outputs["demand_letter"].lower()
    assert "factual basis for that defense" in outputs["demand_letter"].lower()
    assert bundle["citations"]["demand_letter"]["authorityIds"]
    assert bundle["citations"]["demand_letter"]["evidenceIds"]
    assert bundle["meta"]["branch"] == "undue_burden_constructive_denial"
    assert bundle["meta"]["placeholders"]["requested_remedy"] == "[Approve a separate bedroom for the live-in aide]"


def test_undue_burden_package_exports_branch_metadata():
    export_dir = export_package(FIXTURE_DIR / "live_in_aide_case_undue_burden.json")
    validate_package_json_files(export_dir)
    current_snapshot = build_package_snapshot(export_dir)
    assert current_snapshot["manifest.json"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["manifest.json"]["authorityTrust"]["label"] == "mixed_support"
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["manifest.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["manifest.json"]["recommendedFirstStop"] == "memorandum_of_law.pdf"
    assert (
        current_snapshot["manifest.json"]["whyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for undue_burden_constructive_denial review."
    )
    assert any(
        item["path"] == "memorandum_of_law.pdf"
        and item["whyOpenThis"] == "Start with the printable memorandum because it is the strongest branch-aligned narrative for undue_burden_constructive_denial review."
        for item in current_snapshot["manifest.json"]["artifactGuidance"]
    )
    assert current_snapshot["advocacy_bundle.json"]["meta"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["memorandum.json"]["meta"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["brief_index.json"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["brief_index.json"]["recommendedFirstStop"] == "memorandum_of_law.pdf"
    assert (
        current_snapshot["brief_index.json"]["whyOpenThis"]
        == "Start with the printable memorandum because it is the strongest branch-aligned narrative for undue_burden_constructive_denial review."
    )
    assert current_snapshot["brief_index.json"]["authorityTrust"]["label"] == "mixed_support"
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["brief_index.json"]["fitSummary"]["analogicalCount"] == 2
    assert current_snapshot["brief_index.json"]["warningSummary"]["hasWarnings"] is True
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningCounts"]["mixed_support"] == 16
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["hasWarningLabel"] is True
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningLabel"] == "mixed_support"
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningEntryCount"] == 16
    assert all(item.get("trustWarning", {}).get("label") == "mixed_support" for item in current_snapshot["brief_index.json"]["entries"])
    assert any(
        item["kind"] == "memorandum_pdf"
        and item["whyOpenThis"] == "Start with the printable memorandum because it is the strongest branch-aligned narrative for undue_burden_constructive_denial review."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert current_snapshot["decision_tree.json"]["decisionTree"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["decision_tree.json"]["decisionTree"]["activeOutcome"] == "violation"
    assert current_snapshot["dependency_graph.json"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["dependency_graph.json"]["activeOutcome"] == "violation"
    assert current_snapshot["summary.json"]["branch"] == "undue_burden_constructive_denial"
    assert current_snapshot["summary.json"]["activeOutcome"] == "violation"
    assert any(item["branch"] == "undue_burden_constructive_denial" for item in current_snapshot["tests.json"])


def test_generated_undue_burden_result_matches_schema():
    result = evaluate_case(load_fixture("live_in_aide_case_undue_burden.json"))
    validate_with_schema(result, load_schema("result.schema.json"))


def test_generated_undue_burden_advocacy_bundle_matches_schema():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_undue_burden.json"))
    validate_with_schema(bundle, load_schema("advocacy_bundle.schema.json"))


def test_no_violation_result_snapshot_matches_current_output():
    result = evaluate_case(load_fixture("live_in_aide_case_no_violation.json"))
    snapshot = load_snapshot("live_in_aide_case_no_violation_001.result.snapshot.json")
    assert result == snapshot


def test_no_violation_package_snapshot_matches_current_output():
    export_dir = export_package(FIXTURE_DIR / "live_in_aide_case_no_violation.json")
    validate_package_json_files(export_dir)
    current_snapshot = build_package_snapshot(export_dir)
    saved_snapshot = load_snapshot("live_in_aide_case_no_violation_001.package.snapshot.json")
    assert current_snapshot == saved_snapshot
    assert current_snapshot["brief_index.json"]["primaryKind"] == "summary"
    assert current_snapshot["brief_index.json"]["recommendedFirstStop"] == "summary.json"
    assert current_snapshot["manifest.json"]["authorityTrust"]["label"] == "paraphrase_heavy"
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["manifest.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["manifest.json"]["fitSummary"]["directCount"] == 1
    assert current_snapshot["manifest.json"]["fitSummary"]["analogicalCount"] == 1
    assert current_snapshot["manifest.json"]["fitSummary"]["recordSupportCount"] == 3
    assert current_snapshot["manifest.json"]["fitFindingSummary"]["fitFinding"] == "record_support_heavy"
    assert current_snapshot["manifest.json"]["recommendedFirstStop"] == "summary.json"
    assert (
        current_snapshot["manifest.json"]["whyOpenThis"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    assert any(
        item["path"] == "summary.json"
        and item["whyOpenThis"] == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        for item in current_snapshot["manifest.json"]["artifactGuidance"]
    )
    assert current_snapshot["brief_index.json"]["authorityTrust"]["label"] == "paraphrase_heavy"
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceVerified"] is True
    assert current_snapshot["brief_index.json"]["sourceSummary"]["fullySourceNormalized"] is True
    assert current_snapshot["brief_index.json"]["fitSummary"]["directCount"] == 1
    assert current_snapshot["brief_index.json"]["fitSummary"]["analogicalCount"] == 1
    assert current_snapshot["brief_index.json"]["fitSummary"]["recordSupportCount"] == 3
    assert current_snapshot["brief_index.json"]["fitFindingSummary"]["fitFinding"] == "record_support_heavy"
    assert (
        current_snapshot["brief_index.json"]["whyOpenThis"]
        == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
    )
    assert current_snapshot["brief_index.json"]["warningSummary"]["hasWarnings"] is True
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningEntryCount"] == 16
    assert current_snapshot["brief_index.json"]["warningSummary"]["warningCounts"]["paraphrase_heavy"] == 16
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["hasWarningLabel"] is True
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningLabel"] == "paraphrase_heavy"
    assert current_snapshot["brief_index.json"]["warningLabelSummary"]["warningEntryCount"] == 16
    assert all(item.get("trustWarning", {}).get("label") == "paraphrase_heavy" for item in current_snapshot["brief_index.json"]["entries"])
    assert all("lower-trust" in item.get("trustWarning", {}).get("message", "").lower() for item in current_snapshot["brief_index.json"]["entries"])
    assert any(
        item["kind"] == "summary"
        and item["whyOpenThis"] == "Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert any(
        item["kind"] == "memorandum_pdf"
        and item["whyOpenThis"] == "Open this when you want the printable memorandum with paragraph-level support lines."
        for item in current_snapshot["brief_index.json"]["entries"]
    )
    assert "Authority Trust: `paraphrase_heavy`" in current_snapshot["README.md"]
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in current_snapshot["README.md"]
    assert "Direct Fit Count: `1`" in current_snapshot["README.md"]
    assert "Analogical Fit Count: `1`" in current_snapshot["README.md"]
    assert "Record-Support Fit Count: `3`" in current_snapshot["README.md"]
    assert "Recommended First Stop: `summary.json`" in current_snapshot["README.md"]
    assert (
        "Why Open This: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        in current_snapshot["README.md"]
    )
    assert (
        "- `summary.json`: Start with the summary because it is the quickest branch-aligned orientation for evidentiary_gap review."
        in current_snapshot["README.md"]
    )
    assert "Fit Status: This package includes analogical authority mappings." in current_snapshot["README.md"]
    assert "Fit Finding: `record_support_heavy`" in current_snapshot["README.md"]
    assert "lower-trust" in current_snapshot["README.md"].lower()
    assert any(item["kind"] == "summary" and item["priority"] == 1 for item in current_snapshot["brief_index.json"]["entries"])
    assert any(item["kind"] == "demand_letter_markdown" and item["priorityLabel"] == "secondary" for item in current_snapshot["brief_index.json"]["entries"])


def test_no_violation_advocacy_snapshot_matches_current_output():
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case_no_violation.json"))
    snapshot = load_snapshot("live_in_aide_case_no_violation_001.advocacy.snapshot.json")
    assert outputs == snapshot


def test_no_violation_advocacy_bundle_snapshot_matches_current_output():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_no_violation.json"))
    snapshot = load_snapshot("live_in_aide_case_no_violation_001.advocacy_bundle.snapshot.json")
    assert bundle == snapshot


def test_undue_burden_result_snapshot_matches_current_output():
    result = evaluate_case(load_fixture("live_in_aide_case_undue_burden.json"))
    snapshot = load_snapshot("live_in_aide_case_undue_burden_001.result.snapshot.json")
    assert result == snapshot


def test_undue_burden_package_snapshot_matches_current_output():
    export_dir = export_package(FIXTURE_DIR / "live_in_aide_case_undue_burden.json")
    validate_package_json_files(export_dir)
    current_snapshot = build_package_snapshot(export_dir)
    saved_snapshot = load_snapshot("live_in_aide_case_undue_burden_001.package.snapshot.json")
    assert current_snapshot == saved_snapshot
    assert "Authority Trust: `mixed_support`" in current_snapshot["README.md"]
    assert "Source Status: All authority entries are sourceVerified and sourceNormalized." in current_snapshot["README.md"]
    assert "Direct Fit Count: `3`" in current_snapshot["README.md"]
    assert "Analogical Fit Count: `2`" in current_snapshot["README.md"]
    assert "Fit Status: This package includes analogical authority mappings." in current_snapshot["README.md"]


def test_undue_burden_advocacy_snapshot_matches_current_output():
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case_undue_burden.json"))
    snapshot = load_snapshot("live_in_aide_case_undue_burden_001.advocacy.snapshot.json")
    assert outputs == snapshot


def test_undue_burden_advocacy_bundle_snapshot_matches_current_output():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case_undue_burden.json"))
    snapshot = load_snapshot("live_in_aide_case_undue_burden_001.advocacy_bundle.snapshot.json")
    assert bundle == snapshot


def test_advocacy_snapshot_matches_current_output():
    outputs = generate_advocacy_outputs(load_fixture("live_in_aide_case.json"))
    snapshot = load_snapshot("live_in_aide_case_001.advocacy.snapshot.json")
    assert outputs == snapshot


def test_advocacy_bundle_snapshot_matches_current_output():
    bundle = generate_advocacy_bundle(load_fixture("live_in_aide_case.json"))
    snapshot = load_snapshot("live_in_aide_case_001.advocacy_bundle.snapshot.json")
    assert bundle == snapshot


def test_undue_burden_defeats_reasonable_but_not_constructive_denial():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "undue_burden_case"
    payload["acceptedFindings"]["undue_burden"] = True
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is True
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["dutyToGrant"] is False
    assert result["outcome"]["constructiveDenial"] is True
    assert result["outcome"]["violation"] is True


def test_living_room_sleeping_still_counts_as_privacy_harm_in_inferred_mode():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "privacy_harm_case"
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is False
    assert result["outcome"]["workInterference"] is False
    assert result["outcome"]["privacyLoss"] is True
    assert result["outcome"]["necessary"] is True
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is True


def test_explicit_privacy_mode_preserves_no_harm_case():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "explicit_privacy_mode_case"
    payload["policy"]["privacy_mode"] = "explicit_only"
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    result = evaluate_case(payload)
    assert result["policy"]["privacy_mode"] == "explicit_only"
    assert result["outcome"]["sleepInterruption"] is False
    assert result["outcome"]["privacyLoss"] is False
    assert result["outcome"]["necessary"] is False
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is False


def test_alternative_private_sleeping_space_avoids_violation():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "alternative_private_sleeping_space"
    payload["acceptedFindings"]["aide_sleeps_in_living_room"] = False
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["sleepInterruption"] is False
    assert result["outcome"]["privacyLoss"] is False
    assert result["outcome"]["necessary"] is False
    assert result["outcome"]["reasonable"] is False
    assert result["outcome"]["dutyToGrant"] is False
    assert result["outcome"]["constructiveDenial"] is False
    assert result["outcome"]["violation"] is False


def test_missing_request_blocks_duty_to_grant():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "missing_request_case"
    payload["acceptedFindings"]["requested_separate_bedroom"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["dutyToGrant"] is False
    assert "requested_separate_bedroom" in result["missingEvidence"]


def test_accepted_findings_override_asserted_facts_and_report_conflicts():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "conflict_case"
    payload["acceptedFindings"]["works_remotely"] = False
    result = evaluate_case(payload)
    assert result["facts"]["resolved"]["works_remotely"] is False
    assert any(item["fact"] == "works_remotely" for item in result["facts"]["conflicts"])


def test_inactive_findings_have_empty_provenance_links():
    payload = load_fixture("live_in_aide_case.json")
    payload["caseId"] = "inactive_finding_case"
    payload["policy"]["privacy_mode"] = "explicit_only"
    payload["acceptedFindings"]["aide_sleeps_in_living_room"] = False
    payload["acceptedFindings"]["night_access_needed"] = False
    payload["acceptedFindings"]["privacy_loss"] = False
    payload["acceptedFindings"]["works_remotely"] = False
    result = evaluate_case(payload)
    assert result["outcome"]["violation"] is False
    assert result["findingAuthorities"]["violation"] == []
    assert result["provenance"]["violation"]["active"] is False
    assert result["provenance"]["violation"]["evidenceIds"] == []
    assert result["provenance"]["violation"]["eventIds"] == []
    assert result["provenance"]["violation"]["authorityIds"] == []


def main() -> int:
    tests = [
        test_fixture_matches_schema,
        test_generated_positive_result_matches_schema,
        test_generated_positive_advocacy_bundle_matches_schema,
        test_authority_schema_rejects_missing_weight,
        test_context_schema_rejects_missing_type_alias,
        test_positive_constructive_denial_case,
        test_snapshot_matches_current_result,
        test_exported_package_matches_snapshot,
        test_outputs_index_matches_schema_and_cases,
        test_outputs_trust_matrix_matches_schema_and_expectations,
        test_outputs_warning_summary_matches_schema_and_expectations,
        test_outputs_warning_label_matrix_matches_schema_and_expectations,
        test_outputs_warning_entry_matrix_matches_schema_and_expectations,
        test_outputs_warning_entry_summary_matches_schema_and_expectations,
        test_outputs_warning_kind_matrix_matches_schema_and_expectations,
        test_outputs_warning_kind_summary_matches_schema_and_expectations,
        test_outputs_summary_index_matches_schema_and_paths,
        test_outputs_fit_index_matches_schema_and_paths,
        test_outputs_dashboard_overview_matches_schema_and_expectations,
        test_outputs_refresh_state_exists_and_is_complete,
        test_outputs_audit_index_matches_schema_and_paths,
        test_outputs_fit_matrix_matches_schema_and_expectations,
        test_outputs_fit_summary_matches_schema_and_expectations,
        test_outputs_fit_findings_matches_schema_and_expectations,
        test_outputs_fit_findings_summary_matches_schema_and_expectations,
        test_outputs_case_audit_matrix_matches_schema_and_expectations,
        test_case_matrix_cli_supports_trust_matrix_mode,
        test_case_matrix_cli_supports_warning_summary_mode,
        test_case_matrix_cli_supports_warning_label_matrix_mode,
        test_case_matrix_cli_supports_warning_entry_matrix_mode,
        test_case_matrix_cli_supports_warning_kind_matrix_mode,
        test_case_matrix_cli_supports_warning_entry_summary_mode,
        test_case_matrix_cli_supports_warning_kind_summary_mode,
        test_case_matrix_cli_supports_summary_index_mode,
        test_case_matrix_cli_supports_fit_index_mode,
        test_case_matrix_cli_supports_dashboard_index_mode,
        test_case_matrix_cli_supports_dashboard_overview_mode,
        test_case_matrix_cli_supports_refresh_state_mode,
        test_prepend_refresh_warning_only_when_running,
        test_prepend_refresh_warning_wraps_remaining_text_audit_views,
        test_fail_if_refresh_running_raises_for_running_state,
        test_case_matrix_cli_supports_fit_matrix_mode,
        test_case_matrix_cli_supports_fit_summary_mode,
        test_case_matrix_cli_supports_fit_findings_mode,
        test_case_matrix_cli_supports_fit_findings_summary_mode,
        test_case_matrix_cli_supports_audit_index_mode,
        test_case_matrix_cli_supports_case_audit_matrix_mode,
        test_case_matrix_cli_supports_authority_review_mode,
        test_case_matrix_cli_supports_authority_research_note_mode,
        test_case_matrix_cli_supports_authority_summary_mode,
        test_advocacy_outputs_cover_new_chat_modes,
        test_generated_positive_memorandum_matches_schema,
        test_generated_dependency_citations_match_schema,
        test_memorandum_outputs_write_pdf_and_grounding,
        test_advocacy_bundle_contains_structured_citations,
        test_positive_memorandum_snapshot_matches_current_output,
        test_authority_review_markdown_shows_source_badges,
        test_authority_research_note_markdown_shows_source_badges,
        test_case_matrix_cli_subprocess_supports_warning_entry_matrix_json_mode,
        test_case_matrix_cli_subprocess_supports_warning_entry_matrix_trust_filter,
        test_case_matrix_cli_subprocess_supports_warning_entry_matrix_sort_mode,
        test_case_matrix_cli_subprocess_supports_warning_entry_matrix_warned_kind_filter,
        test_case_matrix_cli_subprocess_supports_warning_entry_matrix_top_n_mode,
        test_case_matrix_cli_subprocess_supports_warning_kind_matrix_json_mode,
        test_case_matrix_cli_subprocess_supports_warning_kind_matrix_trust_filter,
        test_case_matrix_cli_subprocess_supports_warning_kind_matrix_sort_mode,
        test_case_matrix_cli_subprocess_supports_warning_kind_matrix_top_n_mode,
        test_case_matrix_cli_subprocess_supports_warning_entry_summary_json_mode,
        test_case_matrix_cli_subprocess_supports_warning_entry_summary_filters,
        test_case_matrix_cli_subprocess_supports_warning_entry_summary_sort_and_top_n,
        test_case_matrix_cli_subprocess_supports_warning_kind_summary_json_mode,
        test_case_matrix_cli_subprocess_supports_warning_kind_summary_filters,
        test_case_matrix_cli_subprocess_supports_warning_kind_summary_sort_and_top_n,
        test_case_matrix_cli_subprocess_supports_summary_index_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_index_json_mode,
        test_case_matrix_cli_subprocess_supports_dashboard_index_json_mode,
        test_case_matrix_cli_subprocess_supports_trust_matrix_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_summary_json_refresh_runtime,
        test_case_matrix_cli_subprocess_supports_case_audit_matrix_refresh_runtime,
        test_case_matrix_cli_subprocess_supports_dashboard_overview_json_mode,
        test_case_matrix_cli_subprocess_supports_dashboard_overview_fit_filter,
        test_case_matrix_cli_subprocess_supports_dashboard_overview_fit_finding_filter,
        test_case_matrix_cli_subprocess_supports_refresh_state_json_mode,
        test_case_matrix_cli_subprocess_supports_refresh_state_wait_mode,
        test_case_matrix_cli_subprocess_supports_refresh_state_fail_fast_mode,
        test_case_matrix_cli_subprocess_supports_fit_matrix_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_matrix_fit_filter,
        test_case_matrix_cli_subprocess_supports_fit_matrix_fit_finding_filter,
        test_case_matrix_cli_subprocess_supports_fit_summary_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_summary_fit_filter,
        test_case_matrix_cli_subprocess_supports_fit_summary_fit_finding_filter,
        test_case_matrix_cli_subprocess_supports_fit_findings_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_findings_fit_finding_filter,
        test_case_matrix_cli_subprocess_supports_fit_findings_summary_json_mode,
        test_case_matrix_cli_subprocess_supports_fit_findings_summary_fit_finding_filter,
        test_case_matrix_cli_subprocess_supports_authority_review_json_mode,
        test_case_matrix_cli_subprocess_supports_authority_review_fit_filter,
        test_case_matrix_cli_subprocess_supports_authority_review_warning_label_filter,
        test_case_matrix_cli_subprocess_supports_authority_research_note_json_mode,
        test_case_matrix_cli_subprocess_supports_authority_research_note_source_filters,
        test_case_matrix_cli_subprocess_supports_authority_research_note_fit_filter,
        test_effective_accommodation_fixture_and_advocacy_path,
        test_generated_effective_accommodation_result_matches_schema,
        test_generated_effective_accommodation_advocacy_bundle_matches_schema,
        test_effective_accommodation_result_snapshot_matches_current_output,
        test_effective_accommodation_package_snapshot_matches_current_output,
        test_effective_accommodation_advocacy_snapshot_matches_current_output,
        test_effective_accommodation_advocacy_bundle_snapshot_matches_current_output,
        test_effective_accommodation_memorandum_snapshot_matches_current_output,
        test_no_violation_fixture_and_advocacy_path,
        test_generated_no_violation_result_matches_schema,
        test_generated_no_violation_advocacy_bundle_matches_schema,
        test_no_violation_result_snapshot_matches_current_output,
        test_no_violation_package_snapshot_matches_current_output,
        test_no_violation_advocacy_snapshot_matches_current_output,
        test_no_violation_advocacy_bundle_snapshot_matches_current_output,
        test_no_violation_memorandum_snapshot_matches_current_output,
        test_undue_burden_fixture_and_advocacy_path,
        test_generated_undue_burden_result_matches_schema,
        test_generated_undue_burden_advocacy_bundle_matches_schema,
        test_undue_burden_package_exports_branch_metadata,
        test_undue_burden_result_snapshot_matches_current_output,
        test_undue_burden_package_snapshot_matches_current_output,
        test_undue_burden_advocacy_snapshot_matches_current_output,
        test_undue_burden_advocacy_bundle_snapshot_matches_current_output,
        test_undue_burden_memorandum_snapshot_matches_current_output,
        test_advocacy_snapshot_matches_current_output,
        test_advocacy_bundle_snapshot_matches_current_output,
        test_undue_burden_defeats_reasonable_but_not_constructive_denial,
        test_living_room_sleeping_still_counts_as_privacy_harm_in_inferred_mode,
        test_explicit_privacy_mode_preserves_no_harm_case,
        test_alternative_private_sleeping_space_avoids_violation,
        test_missing_request_blocks_duty_to_grant,
        test_accepted_findings_override_asserted_facts_and_report_conflicts,
        test_inactive_findings_have_empty_provenance_links,
    ]
    failures = []
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except Exception as exc:
            failures.append((test.__name__, exc))
            print(f"FAIL {test.__name__}: {exc}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
