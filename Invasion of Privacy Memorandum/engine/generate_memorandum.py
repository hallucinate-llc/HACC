#!/usr/bin/env python3
"""Generate a memorandum of law and PDF grounded in the dependency graph."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from engine.evaluate_case import evaluate_case
from engine.authority_fit import infer_fit_kind
from engine.authority_trust import build_authority_trust_profile
from engine.legal_grounding import build_dependency_citations_jsonld


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(f".{path.name}.tmp")
    tmp_path.write_text(content)
    tmp_path.replace(path)


def _build_source_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    authorities = payload.get("authorities", [])
    authority_count = len(authorities)
    source_verified_count = sum(1 for authority in authorities if authority.get("sourceVerified", True))
    source_normalized_count = sum(1 for authority in authorities if authority.get("sourceNormalized", True))
    source_status = (
        "All listed authorities are sourceVerified and sourceNormalized."
        if authority_count and source_verified_count == authority_count and source_normalized_count == authority_count
        else "Some listed authorities still need source verification or normalization cleanup."
    )
    return {
        "authorityCount": authority_count,
        "sourceVerifiedCount": source_verified_count,
        "sourceNormalizedCount": source_normalized_count,
        "sourceStatus": source_status,
    }


def _build_fit_summary(payload: Dict[str, Any]) -> Dict[str, Any]:
    authorities = payload.get("authorities", [])
    authority_count = len(authorities)
    fit_kinds = [authority.get("fitKind") or infer_fit_kind(authority) for authority in authorities]
    direct_count = sum(1 for fit_kind in fit_kinds if fit_kind == "direct")
    analogical_count = sum(1 for fit_kind in fit_kinds if fit_kind == "analogical")
    record_support_count = sum(1 for fit_kind in fit_kinds if fit_kind == "record_support")
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


def _section(
    section_id: str,
    heading: str,
    paragraphs: List[str],
    authority_ids: List[str],
    target_ids: List[str],
    grounding: Dict[str, Any],
) -> Dict[str, Any]:
    targets = sorted(set(target_ids))
    graph = grounding["@graph"]
    payload_authorities = {item["id"]: item for item in grounding.get("authorities", [])}
    authority_labels = {}
    excerpt_map = {}
    for item in graph:
        if item.get("type") == "LegalAuthority":
            authority_id = item["id"].replace("authority:", "")
            payload_authority = payload_authorities.get(authority_id, {})
            authority_labels[item["id"].replace("authority:", "")] = {
                "label": item.get("label", item["id"]),
                "court": item.get("court"),
                "year": item.get("year"),
                "pincite": item.get("pincite"),
                "sourceUrl": item.get("sourceUrl"),
                "sourceVerified": payload_authority.get("sourceVerified", True),
                "sourceNormalized": payload_authority.get("sourceNormalized", True),
            }
        if item.get("type") == "AuthorityExcerpt":
            excerpt_map[item["id"]] = {
                "excerptText": item.get("excerptText"),
                "proposition": item.get("proposition"),
                "excerptKind": item.get("excerptKind"),
                "court": item.get("court"),
                "year": item.get("year"),
                "pincite": item.get("pincite"),
                "sourceUrl": item.get("sourceUrl"),
            }
    support_links = []
    for item in graph:
        if item.get("type") != "DependencySupport":
            continue
        if item.get("target") not in targets:
            continue
        authority_id = item["authority"].replace("authority:", "")
        excerpt = excerpt_map.get(item["authorityExcerpt"], {})
        authority_meta = authority_labels.get(authority_id, {})
        support_links.append(
            {
                "target": item["target"],
                "supportKind": item.get("supportKind"),
                "findingBucket": item.get("findingBucket"),
                "authorityId": authority_id,
                "authorityLabel": authority_meta.get("label", authority_id),
                "authorityExcerpt": item.get("authorityExcerpt"),
                "excerptText": excerpt.get("excerptText"),
                "excerptKind": excerpt.get("excerptKind"),
                "proposition": excerpt.get("proposition"),
                "fitKind": excerpt.get("fitKind", infer_fit_kind({"id": authority_id})),
                "court": excerpt.get("court") or authority_meta.get("court"),
                "year": excerpt.get("year") or authority_meta.get("year"),
                "pincite": excerpt.get("pincite") or authority_meta.get("pincite"),
                "sourceUrl": excerpt.get("sourceUrl") or authority_meta.get("sourceUrl"),
                "sourceVerified": authority_meta.get("sourceVerified", True),
                "sourceNormalized": authority_meta.get("sourceNormalized", True),
            }
        )
    paragraph_citations = []
    paragraph_targets = targets if targets else []
    for index, paragraph in enumerate(paragraphs):
        target = paragraph_targets[index] if index < len(paragraph_targets) else None
        paragraph_support = [item for item in support_links if item["target"] == target] if target else []
        paragraph_authority_ids = sorted({item["authorityId"] for item in paragraph_support})
        paragraph_citations.append(
            {
                "paragraphIndex": index,
                "text": paragraph,
                "targetIds": [target] if target else [],
                "authorityIds": paragraph_authority_ids,
                "supportLinks": paragraph_support,
            }
        )
    return {
        "id": section_id,
        "heading": heading,
        "paragraphs": paragraphs,
        "authorityIds": authority_ids,
        "targetIds": target_ids,
        "citations": {
            "authorityIds": sorted(set(authority_ids)),
            "targetIds": targets,
            "supportLinks": support_links,
        },
        "paragraphCitations": paragraph_citations,
    }


def _active_harms(result: Dict[str, Any]) -> List[str]:
    harms = []
    if result["outcome"]["sleepInterruption"]:
        harms.append("sleep interruption")
    if result["outcome"]["workInterference"]:
        harms.append("work interference")
    if result["outcome"]["caregivingImpairment"]:
        harms.append("caregiving impairment")
    if result["outcome"]["privacyLoss"]:
        harms.append("privacy loss")
    return harms


def _branch_thesis(result: Dict[str, Any]) -> str:
    branch = result["branch"]
    if branch == "constructive_denial":
        return "The strongest memorandum position is that the provider constructively denied an accommodation by approving the aide in principle while denying the separate bedroom required for effective use and enjoyment."
    if branch == "undue_burden_constructive_denial":
        return "The memorandum position is that constructive denial remains the controlling theory even though the provider has raised an undue-burden defense against the requested room configuration."
    if branch == "effective_accommodation":
        return "The current record reads as a compliance-and-preservation matter, because the accommodation appears to have been implemented in effective form rather than denied."
    return "The current record is not yet mature enough to support a finished denial theory, so the memorandum should emphasize factual development and clarification of the accommodation's practical operation."


def _authority_lines(payload: Dict[str, Any], authority_ids: List[str]) -> List[str]:
    authorities = {item["id"]: item for item in payload.get("authorities", [])}
    lines = []
    for authority_id in authority_ids:
        authority = authorities.get(authority_id)
        if not authority:
            continue
        citation = authority.get("citation") or authority["label"]
        notes = authority.get("notes", "")
        lines.append(f"{authority['label']} ({citation}): {notes}")
    return lines


def _format_support_line(support: Dict[str, Any]) -> str:
    excerpt_prefix = ""
    if support.get("excerptKind") == "verified_quote" and support.get("excerptText"):
        excerpt_prefix = f"\"{support['excerptText']}\" "
    source_badges = []
    if support.get("sourceVerified"):
        source_badges.append("sourceVerified")
    if support.get("sourceNormalized"):
        source_badges.append("sourceNormalized")
    source_suffix = f" [{' '.join(source_badges)}]" if source_badges else ""
    return (
        f"{support['authorityLabel']} ({support.get('court')}, {support.get('year')}, {support.get('pincite')}): "
        f"{excerpt_prefix}{support['proposition']} "
        f"[{support['target']}] [fit={support.get('fitKind', 'analogical')}]{source_suffix}"
    )


def generate_memorandum_bundle(payload: Dict[str, Any]) -> Dict[str, Any]:
    result = evaluate_case(payload)
    grounding = build_dependency_citations_jsonld(payload)
    authority_trust = build_authority_trust_profile(payload)
    source_summary = _build_source_summary(payload)
    fit_summary = _build_fit_summary(payload)
    fit_finding = _build_fit_finding(fit_summary)
    authorities = payload.get("authorities", [])
    authority_ids = [item["id"] for item in authorities]
    harms = _active_harms(result)
    question = (
        "Whether the housing provider violated its accommodation duties by denying, or constructively denying, a separate-bedroom accommodation for the live-in aide."
        if result["outcome"]["violation"]
        else "Whether the current record establishes an accommodation violation or instead shows either a functioning accommodation or an evidentiary gap that must be resolved."
    )
    accepted = result["facts"]["resolved"]
    fact_lines = [
        f"The tenant is disabled: {accepted['disabled_tenant']}.",
        f"A live-in aide is needed: {accepted['needs_live_in_aide']}.",
        f"A separate bedroom was requested: {accepted['requested_separate_bedroom']}.",
        f"The aide was approved in principle: {accepted['approved_aide_in_principle']}.",
        f"The separate bedroom was denied: {accepted['denied_separate_bedroom']}.",
        f"The aide sleeps in the living room: {accepted['aide_sleeps_in_living_room']}.",
        f"Night access is needed: {accepted['night_access_needed']}.",
    ]
    if harms:
        fact_lines.append("Accepted functional harms: " + ", ".join(harms) + ".")
    else:
        fact_lines.append("No functional harms were established on the accepted findings.")

    dependency_lines = [
        "The dependency graph moves from foundational facts into harm findings, then into necessity, reasonableness, duty to grant, effectiveness, constructive denial, and violation.",
        f"Active branch: {result['branch']}.",
        f"Active outcome: {'violation' if result['outcome']['violation'] else 'no_violation'}.",
    ]
    if result["outcome"]["constructiveDenial"]:
        dependency_lines.append("The graph is currently anchored on the path approved_aide_in_principle -> constructive_denial -> violation.")
    elif result["branch"] == "effective_accommodation":
        dependency_lines.append("The graph currently stops short of not_effective and constructive_denial because denial and functional harm are not established.")
    else:
        dependency_lines.append("The graph currently stops before violation because the record does not establish the harm and effectiveness predicates needed to complete the path.")

    grounding_lines = []
    support_links = [item for item in grounding["@graph"] if item.get("type") == "DependencySupport"]
    for item in support_links[:8]:
        target = item["target"].replace("dep:", "")
        excerpt_id = item["authorityExcerpt"]
        excerpt = next(node for node in grounding["@graph"] if node.get("id") == excerpt_id)
        authority = next(node for node in grounding["@graph"] if node.get("id") == item["authority"])
        grounding_lines.append(
            f"{target} is grounded by {authority['label']} ({authority.get('citation') or authority['label']}): {excerpt['excerptText']}"
        )

    analysis_lines = [
        _branch_thesis(result),
        f"The evaluator confidence score is {result['confidence']:.2f}.",
        f"Authority grounding note: {authority_trust['advisory']}",
        (
            "The missing elements remain: " + ", ".join(result["missingEvidence"]) + "."
            if result["missingEvidence"]
            else "The current record does not identify missing elements in the implemented rule path."
        ),
    ]
    if result["defeatersConsidered"]["undueBurden"]:
        analysis_lines.append("The analysis must answer the provider's undue-burden defense while maintaining the constructive-denial theory.")
    if result["defeatersConsidered"]["fundamentalAlteration"]:
        analysis_lines.append("The analysis must answer the provider's fundamental-alteration defense.")

    conclusion = (
        "Under the present rule set, the memorandum concludes that the accommodation duty was violated."
        if result["outcome"]["violation"]
        else "Under the present rule set, the memorandum does not conclude a violation on the accepted findings."
    )

    sections = [
        _section("question_presented", "Question Presented", [question], authority_ids, ["dep:node:violation"], grounding),
        _section("summary_of_conclusion", "Summary of Conclusion", [conclusion, _branch_thesis(result)], result.get("findingAuthorities", {}).get("violation", []), ["dep:node:violation", "dep:node:constructive_denial"], grounding),
        _section("accepted_facts", "Accepted Facts", fact_lines, authority_ids, ["dep:node:disabled_tenant", "dep:node:requested_separate_bedroom"], grounding),
        _section("dependency_graph_analysis", "Dependency Graph Analysis", dependency_lines, authority_ids, ["dep:node:necessary", "dep:node:reasonable", "dep:node:violation"], grounding),
        _section("authority_grounding", "Authority Grounding", grounding_lines or ["No authority grounding links were generated for the active dependency targets."], authority_ids, [item["target"] for item in support_links[:8]], grounding),
        _section("application", "Application", analysis_lines, authority_ids, ["dep:node:constructive_denial", "dep:node:violation"], grounding),
        _section("conclusion", "Conclusion", [conclusion], result.get("findingAuthorities", {}).get("violation", []), ["dep:node:violation"], grounding),
        _section("authorities_relied_on", "Authorities Relied On", _authority_lines(payload, authority_ids), authority_ids, [], grounding),
    ]

    markdown_lines = [f"# Memorandum of Law: {result['caseId']}", ""]
    markdown_lines.append(f"Branch: `{result['branch']}`")
    markdown_lines.append(f"Confidence: `{result['confidence']:.2f}`")
    markdown_lines.append(f"Authority Trust: `{authority_trust['label']}`")
    markdown_lines.append(f"Source Verified Count: `{source_summary['sourceVerifiedCount']}`")
    markdown_lines.append(f"Source Normalized Count: `{source_summary['sourceNormalizedCount']}`")
    markdown_lines.append(f"Source Status: {source_summary['sourceStatus']}")
    markdown_lines.append(f"Direct Fit Count: `{fit_summary['directCount']}`")
    markdown_lines.append(f"Analogical Fit Count: `{fit_summary['analogicalCount']}`")
    markdown_lines.append(f"Record-Support Fit Count: `{fit_summary['recordSupportCount']}`")
    markdown_lines.append(f"Fit Status: {fit_summary['fitStatus']}")
    markdown_lines.append(f"Fit Finding: `{fit_finding['label']}`")
    markdown_lines.append(f"Fit Finding Note: {fit_finding['note']}")
    markdown_lines.append("")
    markdown_lines.append(authority_trust["advisory"])
    markdown_lines.append("")
    for section in sections:
        markdown_lines.append(f"## {section['heading']}")
        markdown_lines.append("")
        for paragraph in section["paragraphs"]:
            markdown_lines.append(paragraph)
            markdown_lines.append("")
        if section["citations"]["supportLinks"]:
            markdown_lines.append("### Section Support")
            markdown_lines.append("")
            for support in section["citations"]["supportLinks"][:5]:
                markdown_lines.append(f"- {_format_support_line(support)}")
            markdown_lines.append("")
        paragraph_support_items = [
            citation for citation in section["paragraphCitations"] if citation["supportLinks"]
        ]
        if paragraph_support_items:
            markdown_lines.append("### Paragraph Support")
            markdown_lines.append("")
            for paragraph_citation in paragraph_support_items:
                markdown_lines.append(f"- Paragraph {paragraph_citation['paragraphIndex'] + 1}:")
                for support in paragraph_citation["supportLinks"][:3]:
                    markdown_lines.append(f"  - {_format_support_line(support)}")
            markdown_lines.append("")
        if section["authorityIds"]:
            markdown_lines.append("Authorities: " + ", ".join(section["authorityIds"]))
            markdown_lines.append("")
        if section["targetIds"]:
            markdown_lines.append("Dependency targets: " + ", ".join(section["targetIds"]))
            markdown_lines.append("")

    return {
        "meta": {
            "caseId": result["caseId"],
            "branch": result["branch"],
            "confidence": result["confidence"],
            "title": f"Memorandum of Law: {result['caseId']}",
            "authorityTrust": authority_trust,
            "sourceSummary": source_summary,
            "fitSummary": fit_summary,
            "fitFinding": fit_finding,
        },
        "sections": sections,
        "markdown": "\n".join(markdown_lines).rstrip() + "\n",
    }


def _write_pdf(bundle: Dict[str, Any], pdf_path: Path) -> None:
    doc = SimpleDocTemplate(str(pdf_path), pagesize=LETTER, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    support_style = styles["Italic"]
    story = [Paragraph(bundle["meta"]["title"], styles["Title"]), Spacer(1, 12)]
    story.append(Paragraph(f"Branch: {bundle['meta']['branch']}", styles["Normal"]))
    story.append(Paragraph(f"Confidence: {bundle['meta']['confidence']:.2f}", styles["Normal"]))
    story.append(Paragraph(f"Authority Trust: {bundle['meta']['authorityTrust']['label']}", styles["Normal"]))
    story.append(Paragraph(f"Source Verified Count: {bundle['meta']['sourceSummary']['sourceVerifiedCount']}", styles["Normal"]))
    story.append(Paragraph(f"Source Normalized Count: {bundle['meta']['sourceSummary']['sourceNormalizedCount']}", styles["Normal"]))
    story.append(Paragraph(f"Source Status: {bundle['meta']['sourceSummary']['sourceStatus']}", styles["Normal"]))
    story.append(Paragraph(f"Direct Fit Count: {bundle['meta']['fitSummary']['directCount']}", styles["Normal"]))
    story.append(Paragraph(f"Analogical Fit Count: {bundle['meta']['fitSummary']['analogicalCount']}", styles["Normal"]))
    story.append(Paragraph(f"Record-Support Fit Count: {bundle['meta']['fitSummary']['recordSupportCount']}", styles["Normal"]))
    story.append(Paragraph(f"Fit Status: {bundle['meta']['fitSummary']['fitStatus']}", styles["Normal"]))
    story.append(Paragraph(f"Fit Finding: {bundle['meta']['fitFinding']['label']}", styles["Normal"]))
    story.append(Paragraph(f"Fit Finding Note: {bundle['meta']['fitFinding']['note']}", styles["Normal"]))
    story.append(Paragraph(bundle["meta"]["authorityTrust"]["advisory"], styles["Italic"]))
    story.append(Spacer(1, 12))
    for section in bundle["sections"]:
        story.append(Paragraph(section["heading"], styles["Heading2"]))
        story.append(Spacer(1, 6))
        for paragraph_citation in section["paragraphCitations"]:
            story.append(Paragraph(paragraph_citation["text"], styles["BodyText"]))
            story.append(Spacer(1, 6))
            if paragraph_citation["supportLinks"]:
                support_bits = []
                for support in paragraph_citation["supportLinks"]:
                    source_badges = []
                    if support.get("sourceVerified"):
                        source_badges.append("sourceVerified")
                    if support.get("sourceNormalized"):
                        source_badges.append("sourceNormalized")
                    badge_suffix = f" [{' '.join(source_badges)}]" if source_badges else ""
                    support_bits.append(
                        f"{support['authorityLabel']} ({support.get('court')}, {support.get('year')}, {support.get('pincite')}): {support['proposition']}{badge_suffix}"
                    )
                support_text = "Support: " + " | ".join(support_bits[:3])
                story.append(Paragraph(support_text, support_style))
                story.append(Spacer(1, 4))
        if section["authorityIds"]:
            story.append(Paragraph("Authorities: " + ", ".join(section["authorityIds"]), styles["Italic"]))
            story.append(Spacer(1, 6))
        if section["targetIds"]:
            story.append(Paragraph("Dependency targets: " + ", ".join(section["targetIds"]), styles["Italic"]))
            story.append(Spacer(1, 10))
    doc.build(story)


def write_memorandum_artifacts(
    output_dir: Path,
    bundle: Dict[str, Any],
    grounding: Dict[str, Any],
    include_readme: bool = True,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    _write_text_atomic(output_dir / "memorandum.json", json.dumps(bundle, indent=2) + "\n")
    _write_text_atomic(output_dir / "memorandum.md", bundle["markdown"])
    _write_text_atomic(output_dir / "dependency_citations.jsonld", json.dumps(grounding, indent=2) + "\n")
    _write_pdf(bundle, output_dir / "memorandum_of_law.pdf")
    if include_readme:
        _write_text_atomic(
            output_dir / "README.md",
            "# Memorandum Outputs\n\n- memorandum.json\n- memorandum.md\n- memorandum_of_law.pdf\n- dependency_citations.jsonld\n",
        )
    return output_dir


def write_memorandum_outputs(fixture_path: Path, bundle: Dict[str, Any], grounding: Dict[str, Any]) -> Path:
    output_dir = fixture_path.resolve().parent.parent / "outputs" / f"{fixture_path.stem}_memorandum"
    return write_memorandum_artifacts(output_dir, bundle, grounding, include_readme=True)


def main(argv: List[str]) -> int:
    if len(argv) not in {2, 3}:
        print("usage: generate_memorandum.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    write_output = len(argv) == 3 and argv[2] == "--write"
    if len(argv) == 3 and not write_output:
        print("usage: generate_memorandum.py <fixture.json> [--write]", file=sys.stderr)
        return 2
    path = Path(argv[1])
    payload = json.loads(path.read_text())
    bundle = generate_memorandum_bundle(payload)
    grounding = build_dependency_citations_jsonld(payload)
    print(json.dumps(bundle, indent=2))
    if write_output:
        output_dir = write_memorandum_outputs(path, bundle, grounding)
        print(f"\nWrote memorandum outputs to {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
