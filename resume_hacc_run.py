#!/usr/bin/env python3
"""Resume the latest grounded or adversarial HACC run using saved artifacts."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List


REPO_ROOT = Path(__file__).resolve().parent
GROUNDED_RUNS_DIR = REPO_ROOT / "research_results" / "grounded_runs"
ADVERSARIAL_RUNS_DIR = REPO_ROOT / "research_results" / "adversarial_runs"
GROUNDED_PIPELINE = REPO_ROOT / "hacc_grounded_pipeline.py"
ADVERSARIAL_RUNNER = REPO_ROOT / "hacc_adversarial_runner.py"


def _latest_run_dir(root: Path) -> Path:
    if not root.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {root}")
    candidates = [path for path in root.iterdir() if path.is_dir()]
    if not candidates:
        raise FileNotFoundError(f"No run directories found under {root}")
    candidates.sort(key=lambda path: (path.stat().st_mtime, str(path)), reverse=True)
    return candidates[0]


def _resolve_run_dir(kind: str, path_or_none: str | None, latest: bool) -> Path:
    if latest:
        return _latest_run_dir(GROUNDED_RUNS_DIR if kind == "grounded" else ADVERSARIAL_RUNS_DIR)
    if not path_or_none:
        raise FileNotFoundError("Either provide a run directory or use --latest.")
    candidate = Path(path_or_none).expanduser().resolve()
    if not candidate.is_dir():
        raise FileNotFoundError(f"Run directory does not exist: {candidate}")
    return candidate


def _resume_command(kind: str, run_dir: Path, passthrough_args: List[str]) -> List[str]:
    script = GROUNDED_PIPELINE if kind == "grounded" else ADVERSARIAL_RUNNER
    return [
        sys.executable,
        str(script),
        "--output-dir",
        str(run_dir),
        "--reuse-existing-artifacts",
        *passthrough_args,
    ]


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Resume the latest grounded or adversarial HACC run using saved artifacts.",
    )
    parser.add_argument("kind", choices=("grounded", "adversarial"))
    parser.add_argument("run_dir", nargs="?", help="Existing grounded/adversarial output directory.")
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Auto-discover the newest run in research_results/grounded_runs or research_results/adversarial_runs.",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = create_parser()
    args, runner_args = parser.parse_known_args(argv)
    run_dir = _resolve_run_dir(args.kind, args.run_dir, args.latest)
    if runner_args and runner_args[0] == "--":
        runner_args = runner_args[1:]
    cmd = _resume_command(args.kind, run_dir, runner_args)
    print(f"Resuming {args.kind} run: {run_dir}")
    result = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
