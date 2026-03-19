#!/usr/bin/env python3
"""Validate an intake worksheet, then rerun the grounded HACC pipeline."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


REPO_ROOT = Path(__file__).resolve().parent
VALIDATOR_PATH = REPO_ROOT / "complaint-generator" / "scripts" / "validate_intake_follow_up_worksheet.py"
PIPELINE_PATH = REPO_ROOT / "hacc_grounded_pipeline.py"
GROUNDED_RUNS_DIR = REPO_ROOT / "research_results" / "grounded_runs"
DEFAULT_WORKSHEET_NAME = "intake_follow_up_worksheet.json"


def _validator_command(worksheet_json: str) -> List[str]:
    return [
        sys.executable,
        str(VALIDATOR_PATH),
        worksheet_json,
        "--require-complete",
        "--in-place",
    ]


def _pipeline_command(worksheet_json: str, pipeline_args: List[str]) -> List[str]:
    return [
        sys.executable,
        str(PIPELINE_PATH),
        "--completed-intake-worksheet",
        worksheet_json,
        *pipeline_args,
    ]


def _load_validation_summary(worksheet_json: str) -> Dict[str, Any]:
    worksheet_path = Path(worksheet_json)
    if not worksheet_path.exists():
        return {}
    try:
        payload = json.loads(worksheet_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict):
        return {}
    summary = payload.get("validation_summary")
    return dict(summary) if isinstance(summary, dict) else {}


def _infer_grounded_run_dir(worksheet_json: str) -> Path:
    worksheet_path = Path(worksheet_json).resolve()
    if worksheet_path.parent.name == "complaint_synthesis":
        return worksheet_path.parent.parent
    return worksheet_path.parent


def _extract_output_directory(stdout: str) -> str:
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith("Output directory:"):
            return stripped.split(":", 1)[1].strip()
    return ""


def _extract_named_output(stdout: str, label: str) -> str:
    prefix = f"{label}:"
    for line in stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped.split(":", 1)[1].strip()
    return ""


def _markdown_draft_path(draft_package: str) -> str:
    if not draft_package:
        return ""
    draft_path = Path(draft_package)
    if draft_path.name == "draft_complaint_package.json":
        return str(draft_path.with_name("draft_complaint_package.md"))
    return ""


def _print_validation_summary(worksheet_json: str) -> None:
    summary = _load_validation_summary(worksheet_json)
    if not summary:
        return
    status_counts = dict(summary.get("status_counts") or {})
    print("Worksheet preflight summary:")
    print(f"- grounded_run: {_infer_grounded_run_dir(worksheet_json)}")
    print(f"- worksheet: {worksheet_json}")
    print(f"- item_count: {summary.get('item_count', 0)}")
    print(f"- answered: {status_counts.get('answered', 0)}")
    print(f"- open: {summary.get('open_question_count', 0)}")
    print(f"- invalid: {summary.get('invalid_question_count', 0)}")


def _resolve_worksheet_path(path_or_run_dir: str) -> Path:
    candidate = Path(path_or_run_dir).expanduser().resolve()
    if candidate.is_file():
        return candidate
    if candidate.is_dir():
        direct_candidate = candidate / DEFAULT_WORKSHEET_NAME
        if direct_candidate.is_file():
            return direct_candidate
        synthesis_candidate = candidate / "complaint_synthesis" / DEFAULT_WORKSHEET_NAME
        if synthesis_candidate.is_file():
            return synthesis_candidate
        matches = sorted(
            candidate.glob(f"**/{DEFAULT_WORKSHEET_NAME}"),
            key=lambda path: (path.stat().st_mtime, str(path)),
            reverse=True,
        )
        if matches:
            return matches[0]
        raise FileNotFoundError(f"No {DEFAULT_WORKSHEET_NAME} found under {candidate}")
    raise FileNotFoundError(f"Worksheet path does not exist: {candidate}")


def _latest_grounded_run_worksheet() -> Path:
    if not GROUNDED_RUNS_DIR.is_dir():
        raise FileNotFoundError(f"Grounded runs directory does not exist: {GROUNDED_RUNS_DIR}")
    candidates = []
    for run_dir in GROUNDED_RUNS_DIR.iterdir():
        if not run_dir.is_dir():
            continue
        try:
            worksheet = _resolve_worksheet_path(str(run_dir))
        except FileNotFoundError:
            continue
        candidates.append((worksheet.stat().st_mtime, str(worksheet), worksheet))
    if not candidates:
        raise FileNotFoundError(f"No grounded run with {DEFAULT_WORKSHEET_NAME} found under {GROUNDED_RUNS_DIR}")
    candidates.sort(reverse=True)
    return candidates[0][2]


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate an intake worksheet, then rerun the grounded HACC pipeline with it.",
    )
    parser.add_argument(
        "worksheet_json",
        nargs="?",
        help="Path to intake_follow_up_worksheet.json, or a grounded run directory containing it.",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Auto-discover the newest grounded run worksheet under research_results/grounded_runs.",
    )
    parser.add_argument(
        "pipeline_args",
        nargs=argparse.REMAINDER,
        help="Additional arguments passed through to hacc_grounded_pipeline.py. Prefix with -- before pipeline flags.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    args = create_parser().parse_args(argv)
    if args.latest:
        worksheet_json = str(_latest_grounded_run_worksheet())
    elif args.worksheet_json:
        worksheet_json = str(_resolve_worksheet_path(args.worksheet_json))
    else:
        raise SystemExit("Either provide a worksheet path/run directory or use --latest.")
    pipeline_args = list(args.pipeline_args or [])
    if pipeline_args and pipeline_args[0] == "--":
        pipeline_args = pipeline_args[1:]

    validator_cmd = _validator_command(worksheet_json)
    validation = subprocess.run(validator_cmd, cwd=str(REPO_ROOT), check=False)
    if validation.returncode != 0:
        return validation.returncode
    _print_validation_summary(worksheet_json)

    pipeline_cmd = _pipeline_command(worksheet_json, pipeline_args)
    rerun = subprocess.run(
        pipeline_cmd,
        cwd=str(REPO_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )
    if rerun.stdout:
        print(rerun.stdout, end="" if rerun.stdout.endswith("\n") else "\n")
    if rerun.stderr:
        print(rerun.stderr, file=sys.stderr, end="" if rerun.stderr.endswith("\n") else "\n")
    output_dir = _extract_output_directory(rerun.stdout or "")
    draft_package = _extract_named_output(rerun.stdout or "", "Draft complaint package")
    intake_worksheet = _extract_named_output(rerun.stdout or "", "Intake worksheet")
    markdown_draft = _markdown_draft_path(draft_package)
    if rerun.returncode == 0 and output_dir:
        print(f"Rerun artifacts: {output_dir}")
    if rerun.returncode == 0 and draft_package:
        print(f"Refreshed complaint draft: {draft_package}")
    if rerun.returncode == 0 and markdown_draft:
        print(f"Refreshed complaint markdown: {markdown_draft}")
    if rerun.returncode == 0 and intake_worksheet:
        print(f"Refreshed intake worksheet: {intake_worksheet}")
    return rerun.returncode


if __name__ == "__main__":
    raise SystemExit(main())
