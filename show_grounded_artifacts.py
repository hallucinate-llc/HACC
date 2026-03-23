#!/usr/bin/env python3
"""Print the most useful grounded-run artifacts in a compact human-readable view."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent
GROUNDED_RUNS_DIR = REPO_ROOT / "research_results" / "grounded_runs"


def _latest_run_dir(root: Path) -> Path:
    if not root.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {root}")
    candidates = [path for path in root.iterdir() if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No grounded run directories found under {root}")
    candidates.sort(key=lambda path: (path.stat().st_mtime, str(path)), reverse=True)
    return candidates[0]


def _resolve_run_dir(path_or_none: str | None, latest: bool) -> Path:
    if latest:
        return _latest_run_dir(GROUNDED_RUNS_DIR)
    if not path_or_none:
        raise FileNotFoundError("Either provide a grounded run directory or use --latest.")
    candidate = Path(path_or_none).expanduser().resolve()
    if not candidate.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {candidate}")
    return candidate


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text())


def _collect_summary(run_dir: Path, top_n: int) -> dict[str, Any]:
    prompts = _read_json(run_dir / "synthetic_prompts.json")
    complaint_package = _read_json(run_dir / "complaint_synthesis" / "draft_complaint_package.json")
    grounding_bundle = _read_json(run_dir / "grounding_bundle.json")
    external_research = _read_json(run_dir / "external_research_bundle.json")
    run_summary = _read_json(run_dir / "run_summary.json")

    authority_basis = complaint_package.get("authorities_and_research_basis", {})
    authority_records = authority_basis.get("authority_records", [])[:top_n]
    web_records = authority_basis.get("corroborating_web_research_records", [])[:top_n]
    upload_prompts = prompts.get("evidence_upload_prompts", [])[:top_n]
    upload_candidates = grounding_bundle.get("upload_candidates", [])[:top_n]
    evidence_attachments = complaint_package.get("evidence_attachments", [])[:top_n]

    external_summary = external_research.get("summary", {})
    progress = _read_json(run_dir / "progress.json")
    return {
        "run_dir": str(run_dir),
        "query": grounding_bundle.get("query") or external_research.get("query") or "",
        "claim_type": grounding_bundle.get("claim_type") or external_research.get("claim_type") or "",
        "status": run_summary.get("status", ""),
        "progress_stage": progress.get("stage", ""),
        "upload_prompts": upload_prompts,
        "upload_candidates": upload_candidates,
        "evidence_attachments": evidence_attachments,
        "authority_records": authority_records,
        "corroborating_web_research_records": web_records,
        "mediator_questions": prompts.get("mediator_questions", [])[:top_n],
        "blocker_objectives": prompts.get("blocker_objectives", [])[:top_n],
        "production_evidence_intake_steps": prompts.get("production_evidence_intake_steps", [])[:top_n],
        "mediator_upload_checklist": prompts.get("mediator_upload_checklist", [])[:top_n],
        "external_research_summary": {
            "web_result_count": external_summary.get("web_result_count", 0),
            "legal_result_count": external_summary.get("legal_result_count", 0),
            "top_web_titles": external_summary.get("top_web_titles", [])[:top_n],
            "top_legal_titles": external_summary.get("top_legal_titles", [])[:top_n],
        },
    }


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Show upload prompts, evidence candidates, and ranked authority records from a grounded run.",
    )
    parser.add_argument("run_dir", nargs="?", help="Existing grounded output directory.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Auto-discover the newest grounded run under research_results/grounded_runs.",
    )
    parser.add_argument(
        "--top-n",
        type=int,
        default=3,
        help="Maximum items to print for each section.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the collected summary as JSON instead of formatted text.",
    )
    parser.add_argument(
        "--section",
        action="append",
        choices=(
            "upload-prompts",
            "evidence-candidates",
            "attachments",
            "mediator-questions",
            "blockers",
            "intake-steps",
            "upload-checklist",
            "authorities",
            "web-research",
            "top-web",
            "top-legal",
            "paths",
        ),
        help="Limit output to one or more specific sections. May be passed multiple times.",
    )
    parser.add_argument(
        "--write-brief",
        action="store_true",
        help="Write a compact Markdown brief into the grounded run directory.",
    )
    return parser


def _print_section(title: str, rows: list[str]) -> None:
    print(f"\n{title}")
    if not rows:
        print("- none")
        return
    for row in rows:
        print(f"- {row}")


def _format_upload_prompts(items: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for item in items:
        title = item.get("title", "Untitled evidence")
        relative_path = item.get("relative_path", "")
        anchor_sections = ", ".join(item.get("anchor_sections", []))
        rows.append(f"{title} [{relative_path}] anchors={anchor_sections}")
    return rows


def _format_upload_candidates(items: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for item in items:
        title = item.get("title", "Untitled candidate")
        priority = item.get("metadata", {}).get("selection_priority", item.get("selection_priority", ""))
        snippet = item.get("snippet", "").strip()
        snippet = snippet[:120] + ("..." if len(snippet) > 120 else "")
        rows.append(f"{title} priority={priority} snippet={snippet}")
    return rows


def _format_authorities(items: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for item in items:
        label = item.get("label", "Untitled authority")
        authority_type = item.get("type", "Authority")
        why = item.get("why_it_matters", "")
        url = item.get("url", "")
        rows.append(f"{authority_type}: {label} | {why} | {url}")
    return rows


def _format_attachment_rows(items: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for item in items:
        title = item.get("title", "Untitled attachment")
        uploaded = item.get("uploaded_to_mediator", False)
        source_path = item.get("relative_path", "")
        rows.append(f"{title} uploaded_to_mediator={uploaded} path={source_path}")
    return rows


def _should_print(selections: set[str], name: str) -> bool:
    return not selections or name in selections


def _markdown_lines(summary: dict[str, Any], run_dir: Path) -> list[str]:
    ext = summary["external_research_summary"]
    lines = [
        "# Grounded Run Brief",
        "",
        f"- Run: `{summary['run_dir']}`",
        f"- Query: `{summary['query']}`" if summary["query"] else "- Query: ",
        f"- Claim type: `{summary['claim_type']}`" if summary["claim_type"] else "- Claim type: ",
        f"- Status: `{summary['status']}`" if summary["status"] else "- Status: ",
        f"- Progress stage: `{summary['progress_stage']}`" if summary["progress_stage"] else "- Progress stage: ",
        f"- External research: web_results={ext['web_result_count']} legal_results={ext['legal_result_count']}",
        "",
        "## Key Artifact Paths",
        "",
        f"- `{run_dir / 'synthetic_prompts.json'}`",
        f"- `{run_dir / 'grounding_bundle.json'}`",
        f"- `{run_dir / 'external_research_bundle.json'}`",
        f"- `{run_dir / 'complaint_manager_interfaces.json'}`",
        f"- `{run_dir / 'complaint_synthesis' / 'draft_complaint_package.json'}`",
        f"- `{run_dir / 'complaint_synthesis' / 'draft_complaint_package.md'}`",
        "",
        "## Upload Prompts",
        "",
    ]
    for row in _format_upload_prompts(summary["upload_prompts"]) or ["none"]:
        lines.append(f"- {row}")
    lines.extend(["", "## Mediator Questions", ""])
    for row in summary["mediator_questions"] or ["none"]:
        lines.append(f"- {row}")
    lines.extend(["", "## Blocker Objectives", ""])
    for row in summary["blocker_objectives"] or ["none"]:
        lines.append(f"- {row}")
    lines.extend(["", "## Authorities", ""])
    for row in _format_authorities(summary["authority_records"]) or ["none"]:
        lines.append(f"- {row}")
    lines.extend(["", "## Top Evidence Candidates", ""])
    for row in _format_upload_candidates(summary["upload_candidates"]) or ["none"]:
        lines.append(f"- {row}")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)
    run_dir = _resolve_run_dir(args.run_dir, args.latest)
    summary = _collect_summary(run_dir, max(args.top_n, 1))

    if args.json:
        print(json.dumps(summary, indent=2))
        return 0

    if args.write_brief:
        brief_path = run_dir / "grounded_run_brief.md"
        brief_path.write_text("\n".join(_markdown_lines(summary, run_dir)) + "\n")
        print(f"Wrote brief: {brief_path}")

    print(f"Grounded run: {summary['run_dir']}")
    if summary["query"]:
        print(f"Query: {summary['query']}")
    if summary["claim_type"]:
        print(f"Claim type: {summary['claim_type']}")
    if summary["status"]:
        print(f"Run status: {summary['status']}")
    if summary["progress_stage"]:
        print(f"Progress stage: {summary['progress_stage']}")

    ext = summary["external_research_summary"]
    print(
        "External research: "
        f"web_results={ext['web_result_count']} legal_results={ext['legal_result_count']}"
    )
    selections = set(args.section or [])

    if _should_print(selections, "paths"):
        _print_section(
            "Key Artifact Paths",
            [
                str(run_dir / "synthetic_prompts.json"),
                str(run_dir / "grounding_bundle.json"),
                str(run_dir / "external_research_bundle.json"),
                str(run_dir / "complaint_manager_interfaces.json"),
                str(run_dir / "complaint_synthesis" / "draft_complaint_package.json"),
                str(run_dir / "complaint_synthesis" / "draft_complaint_package.md"),
            ],
        )
    if _should_print(selections, "upload-prompts"):
        _print_section("Upload Prompts", _format_upload_prompts(summary["upload_prompts"]))
    if _should_print(selections, "evidence-candidates"):
        _print_section("Top Evidence Candidates", _format_upload_candidates(summary["upload_candidates"]))
    if _should_print(selections, "attachments"):
        _print_section("Mediator Attachments", _format_attachment_rows(summary["evidence_attachments"]))
    if _should_print(selections, "mediator-questions"):
        _print_section("Mediator Questions", list(summary["mediator_questions"]))
    if _should_print(selections, "blockers"):
        _print_section("Blocker Objectives", list(summary["blocker_objectives"]))
    if _should_print(selections, "intake-steps"):
        _print_section("Production Intake Steps", list(summary["production_evidence_intake_steps"]))
    if _should_print(selections, "upload-checklist"):
        _print_section("Mediator Upload Checklist", list(summary["mediator_upload_checklist"]))
    if _should_print(selections, "authorities"):
        _print_section("Authorities", _format_authorities(summary["authority_records"]))
    if _should_print(selections, "web-research"):
        _print_section(
            "Corroborating Web Research",
            _format_authorities(summary["corroborating_web_research_records"]),
        )
    if _should_print(selections, "top-web"):
        _print_section("Top Web Titles", list(summary["external_research_summary"]["top_web_titles"]))
    if _should_print(selections, "top-legal"):
        _print_section("Top Legal Titles", list(summary["external_research_summary"]["top_legal_titles"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
