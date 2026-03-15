#!/usr/bin/env python3
"""Run a grounded HACC evidence workflow plus adversarial optimization."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, Optional


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))


from hacc_adversarial_runner import run_hacc_adversarial_batch
from hacc_research import HACCResearchEngine


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def _default_grounding_request(hacc_preset: str) -> Dict[str, str]:
    try:
        from adversarial_harness.hacc_evidence import get_hacc_query_specs
    except Exception:
        return {
            "query": hacc_preset.replace("_", " "),
            "claim_type": "housing_discrimination",
        }

    specs = get_hacc_query_specs(preset=hacc_preset)
    if not specs:
        return {
            "query": hacc_preset.replace("_", " "),
            "claim_type": "housing_discrimination",
        }
    first = dict(specs[0] or {})
    return {
        "query": str(first.get("query") or hacc_preset.replace("_", " ")),
        "claim_type": str(first.get("type") or "housing_discrimination"),
    }


def run_hacc_grounded_pipeline(
    *,
    output_dir: str | Path,
    query: Optional[str] = None,
    hacc_preset: str = "core_hacc_policies",
    claim_type: Optional[str] = None,
    top_k: int = 5,
    demo: bool = False,
    num_sessions: int = 3,
    max_turns: int = 4,
    max_parallel: int = 1,
    use_hacc_vector_search: bool = False,
    config_path: Optional[str] = None,
    backend_id: Optional[str] = None,
    provider: str = "copilot_cli",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    default_request = _default_grounding_request(hacc_preset)
    grounding_query = str(query or default_request["query"])
    resolved_claim_type = str(claim_type or default_request["claim_type"] or "housing_discrimination")

    engine = HACCResearchEngine(repo_root=REPO_ROOT)
    grounding_bundle = engine.build_grounding_bundle(
        grounding_query,
        top_k=top_k,
        claim_type=resolved_claim_type,
        search_mode="package",
        use_vector=use_hacc_vector_search,
    )
    upload_report = engine.simulate_evidence_upload(
        grounding_query,
        top_k=top_k,
        claim_type=resolved_claim_type,
        user_id="hacc-grounded-pipeline",
        search_mode="package",
        use_vector=use_hacc_vector_search,
        db_dir=output_root / "mediator_state",
    )
    adversarial_summary = run_hacc_adversarial_batch(
        output_dir=output_root / "adversarial",
        num_sessions=num_sessions,
        max_turns=max_turns,
        max_parallel=max_parallel,
        hacc_preset=hacc_preset,
        hacc_count=top_k,
        use_hacc_vector_search=use_hacc_vector_search,
        demo=demo,
        config_path=config_path,
        backend_id=backend_id,
        provider=provider,
        model=model,
    )

    grounding_path = output_root / "grounding_bundle.json"
    prompts_path = output_root / "synthetic_prompts.json"
    upload_path = output_root / "evidence_upload_report.json"
    adversarial_path = output_root / "adversarial_summary.json"
    summary_path = output_root / "run_summary.json"

    grounding_path.write_text(json.dumps(grounding_bundle, ensure_ascii=False, indent=2), encoding="utf-8")
    prompts_path.write_text(
        json.dumps(grounding_bundle.get("synthetic_prompts", {}), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    upload_path.write_text(json.dumps(upload_report, ensure_ascii=False, indent=2), encoding="utf-8")
    adversarial_path.write_text(json.dumps(adversarial_summary, ensure_ascii=False, indent=2), encoding="utf-8")

    summary = {
        "timestamp": datetime.now(UTC).isoformat(),
        "grounding_query": grounding_query,
        "claim_type": resolved_claim_type,
        "hacc_preset": hacc_preset,
        "use_hacc_vector_search": bool(use_hacc_vector_search),
        "grounding": grounding_bundle,
        "evidence_upload": upload_report,
        "adversarial": adversarial_summary,
        "artifacts": {
            "output_dir": str(output_root),
            "grounding_bundle_json": str(grounding_path),
            "synthetic_prompts_json": str(prompts_path),
            "evidence_upload_report_json": str(upload_path),
            "adversarial_summary_json": str(adversarial_path),
            "adversarial_output_dir": str(output_root / "adversarial"),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run repository-grounded evidence upload simulation plus HACC adversarial optimization.",
    )
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "research_results" / "grounded_runs" / _timestamp()))
    parser.add_argument("--query", default=None, help="Optional explicit grounding query. Defaults to the first query in the selected preset.")
    parser.add_argument("--hacc-preset", default="core_hacc_policies")
    parser.add_argument("--claim-type", default=None, help="Optional explicit claim type for upload simulation.")
    parser.add_argument("--top-k", type=int, default=5, help="Maximum number of repository evidence files to upload.")
    parser.add_argument("--num-sessions", type=int, default=3)
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--max-parallel", type=int, default=1)
    parser.add_argument("--use-hacc-vector-search", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Use deterministic demo backends for the adversarial run.")
    parser.add_argument("--config", default=None, help="Optional complaint-generator config JSON.")
    parser.add_argument("--backend-id", default=None, help="Optional backend id from the selected config.")
    parser.add_argument("--provider", default="copilot_cli")
    parser.add_argument("--model", default=None)
    parser.add_argument("--json", action="store_true", help="Print the full workflow summary JSON.")
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    args = create_parser().parse_args(argv)
    summary = run_hacc_grounded_pipeline(
        output_dir=args.output_dir,
        query=args.query,
        hacc_preset=args.hacc_preset,
        claim_type=args.claim_type,
        top_k=args.top_k,
        demo=args.demo,
        num_sessions=args.num_sessions,
        max_turns=args.max_turns,
        max_parallel=args.max_parallel,
        use_hacc_vector_search=args.use_hacc_vector_search,
        config_path=args.config,
        backend_id=args.backend_id,
        provider=args.provider,
        model=args.model,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Output directory: {summary['artifacts']['output_dir']}")
        print(f"Grounding query: {summary['grounding_query']}")
        print(f"Uploaded evidence count: {summary['evidence_upload']['upload_count']}")
        print(f"Adversarial output directory: {summary['artifacts']['adversarial_output_dir']}")
        print(f"Synthetic prompts: {summary['artifacts']['synthetic_prompts_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())