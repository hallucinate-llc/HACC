#!/usr/bin/env python3
"""Run complaint-generator's adversarial harness against HACC evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"


def _ensure_complaint_generator_on_path() -> None:
    root = str(COMPLAINT_GENERATOR_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y%m%d_%H%M%S")


def _sanitize_for_json(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(key): _sanitize_for_json(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_sanitize_for_json(item) for item in value]
    if hasattr(value, "to_dict") and callable(value.to_dict):
        try:
            return _sanitize_for_json(value.to_dict())
        except Exception:
            return str(value)
    return str(value)


def _load_runtime(demo: bool, config_path: Optional[str], backend_id: Optional[str], provider: str, model: Optional[str]) -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()

    from adversarial_harness import AdversarialHarness, Optimizer

    if demo:
        from adversarial_harness.demo_autopatch import DemoBatchLLMBackend, DemoBatchMediator

        complainant_backend = DemoBatchLLMBackend()
        critic_backend = DemoBatchLLMBackend()
        mediator_factory = DemoBatchMediator
        runtime = {
            "mode": "demo",
            "provider": "demo",
            "model": "demo",
        }
        return {
            "AdversarialHarness": AdversarialHarness,
            "Optimizer": Optimizer,
            "complainant_backend": complainant_backend,
            "critic_backend": critic_backend,
            "mediator_factory": mediator_factory,
            "runtime": runtime,
        }

    from backends import LLMRouterBackend
    from mediator import Mediator

    if config_path:
        agentic_cli_path = COMPLAINT_GENERATOR_ROOT / "scripts" / "agentic_scraper_cli.py"
        spec = importlib.util.spec_from_file_location("complaint_generator_agentic_scraper_cli", agentic_cli_path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Unable to load config helper module: {agentic_cli_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        build_backends = module.build_backends
        load_config = module.load_config

        config = load_config(config_path)

        def build_role_backend(role_name: str) -> Any:
            backends = build_backends(config, backend_id=backend_id)
            if not backends:
                raise RuntimeError(f"No backends could be built from config: {config_path}")
            backend = backends[0]
            if hasattr(backend, "id"):
                try:
                    backend.id = role_name
                except Exception:
                    pass
            return backend

        def mediator_factory() -> Any:
            return Mediator(backends=build_backends(config, backend_id=backend_id))

        selected_backend_id = backend_id
        if not selected_backend_id:
            mediator_config = config.get("MEDIATOR", {})
            backend_ids = list(mediator_config.get("backends") or [])
            selected_backend_id = backend_ids[0] if backend_ids else None

        runtime = {
            "mode": "config",
            "config_path": str(Path(config_path).resolve()),
            "backend_id": selected_backend_id,
            "provider": "config",
            "model": model,
            "complainant_backend_class": type(build_role_backend("complainant")).__name__,
            "critic_backend_class": type(build_role_backend("critic")).__name__,
        }
        complainant_backend = build_role_backend("complainant")
        critic_backend = build_role_backend("critic")
        return {
            "AdversarialHarness": AdversarialHarness,
            "Optimizer": Optimizer,
            "complainant_backend": complainant_backend,
            "critic_backend": critic_backend,
            "mediator_factory": mediator_factory,
            "runtime": runtime,
        }

    complainant_backend = LLMRouterBackend(id="complainant", provider=provider, model=model)
    critic_backend = LLMRouterBackend(id="critic", provider=provider, model=model)

    def mediator_factory() -> Any:
        return Mediator(backends=[LLMRouterBackend(id="mediator", provider=provider, model=model)])

    runtime = {
        "mode": "llm_router",
        "provider": provider,
        "model": model or getattr(complainant_backend, "model", None),
        "complainant_backend_class": type(complainant_backend).__name__,
        "critic_backend_class": type(critic_backend).__name__,
    }
    return {
        "AdversarialHarness": AdversarialHarness,
        "Optimizer": Optimizer,
        "complainant_backend": complainant_backend,
        "critic_backend": critic_backend,
        "mediator_factory": mediator_factory,
        "runtime": runtime,
    }


def _select_best_result(results: List[Any]) -> Optional[Any]:
    successful = [result for result in results if getattr(result, "success", False) and getattr(result, "critic_score", None)]
    if not successful:
        return None
    return max(successful, key=lambda result: float(getattr(result.critic_score, "overall_score", 0.0) or 0.0))


def _router_diagnostics() -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()
    diagnostics: Dict[str, Any] = {}

    try:
        from integrations.ipfs_datasets.storage import storage_backend_status

        diagnostics["ipfs_router"] = _sanitize_for_json(storage_backend_status())
    except Exception as exc:
        diagnostics["ipfs_router"] = {
            "status": "error",
            "error": str(exc),
        }

    try:
        from integrations.ipfs_datasets.vector_store import create_vector_index

        with tempfile.TemporaryDirectory() as tmpdir:
            diagnostics["embeddings_router"] = _sanitize_for_json(
                create_vector_index(
                    [
                        {"id": "diag-a", "text": "reasonable accommodation grievance hearing"},
                        {"id": "diag-b", "text": "procurement vendor selection policy"},
                    ],
                    index_name="router_diag",
                    output_dir=tmpdir,
                )
            )
    except Exception as exc:
        diagnostics["embeddings_router"] = {
            "status": "error",
            "error": str(exc),
        }

    return diagnostics


def run_hacc_adversarial_batch(
    *,
    output_dir: str | Path,
    num_sessions: int = 3,
    max_turns: int = 4,
    max_parallel: int = 1,
    personalities: Optional[List[str]] = None,
    hacc_preset: str = "core_hacc_policies",
    hacc_count: Optional[int] = None,
    use_hacc_vector_search: bool = False,
    demo: bool = False,
    config_path: Optional[str] = None,
    backend_id: Optional[str] = None,
    provider: str = "copilot_cli",
    model: Optional[str] = None,
) -> Dict[str, Any]:
    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    session_dir = output_root / "sessions"
    session_dir.mkdir(parents=True, exist_ok=True)

    runtime_bundle = _load_runtime(demo, config_path, backend_id, provider, model)
    AdversarialHarness = runtime_bundle["AdversarialHarness"]
    Optimizer = runtime_bundle["Optimizer"]

    harness = AdversarialHarness(
        llm_backend_complainant=runtime_bundle["complainant_backend"],
        llm_backend_critic=runtime_bundle["critic_backend"],
        mediator_factory=runtime_bundle["mediator_factory"],
        max_parallel=max_parallel,
        session_state_dir=str(session_dir),
    )

    results = harness.run_batch(
        num_sessions=num_sessions,
        personalities=personalities,
        max_turns_per_session=max_turns,
        include_hacc_evidence=True,
        hacc_count=hacc_count,
        hacc_preset=hacc_preset,
        use_hacc_vector_search=use_hacc_vector_search,
    )

    optimizer = Optimizer()
    report = optimizer.analyze(results)
    stats = harness.get_statistics()
    best_result = _select_best_result(results)

    run_results_path = output_root / "adversarial_results.json"
    optimization_report_path = output_root / "optimization_report.json"
    anchor_report_path = output_root / "anchor_section_coverage.csv"
    best_complaint_path = output_root / "best_complaint_bundle.json"
    summary_path = output_root / "run_summary.json"

    harness.save_results(str(run_results_path))
    harness.save_anchor_section_report(str(anchor_report_path), format="csv")

    optimization_payload = _sanitize_for_json(report.to_dict())
    optimization_report_path.write_text(
        json.dumps(optimization_payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    best_bundle = {
        "seed_complaint": _sanitize_for_json(best_result.seed_complaint if best_result else None),
        "initial_complaint_text": getattr(best_result, "initial_complaint_text", ""),
        "conversation_history": _sanitize_for_json(getattr(best_result, "conversation_history", [])),
        "critic_score": _sanitize_for_json(getattr(best_result, "critic_score", None)),
        "final_state": _sanitize_for_json(getattr(best_result, "final_state", {})),
        "knowledge_graph_summary": _sanitize_for_json(getattr(best_result, "knowledge_graph_summary", {})),
        "dependency_graph_summary": _sanitize_for_json(getattr(best_result, "dependency_graph_summary", {})),
    }
    best_complaint_path.write_text(
        json.dumps(best_bundle, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    summary = {
        "timestamp": _timestamp(),
        "runtime": runtime_bundle["runtime"],
        "router_diagnostics": _router_diagnostics(),
        "inputs": {
            "num_sessions": num_sessions,
            "max_turns": max_turns,
            "max_parallel": max_parallel,
            "personalities": list(personalities or []),
            "hacc_preset": hacc_preset,
            "hacc_count": hacc_count,
            "use_hacc_vector_search": use_hacc_vector_search,
        },
        "statistics": _sanitize_for_json(stats),
        "optimization_report": {
            "average_score": optimization_payload.get("average_score"),
            "score_trend": optimization_payload.get("score_trend"),
            "recommended_hacc_preset": optimization_payload.get("recommended_hacc_preset"),
            "priority_improvements": optimization_payload.get("priority_improvements"),
            "recommendations": optimization_payload.get("recommendations"),
            "best_session_id": optimization_payload.get("best_session_id"),
        },
        "best_complaint": {
            "session_id": getattr(best_result, "session_id", None),
            "initial_complaint_text": getattr(best_result, "initial_complaint_text", ""),
            "score": float(getattr(getattr(best_result, "critic_score", None), "overall_score", 0.0) or 0.0) if best_result else 0.0,
            "seed_type": str((getattr(best_result, "seed_complaint", {}) or {}).get("type") or "") if best_result else "",
            "seed_summary": str((getattr(best_result, "seed_complaint", {}) or {}).get("summary") or "") if best_result else "",
        },
        "artifacts": {
            "output_dir": str(output_root),
            "results_json": str(run_results_path),
            "optimization_report_json": str(optimization_report_path),
            "anchor_section_csv": str(anchor_report_path),
            "best_complaint_bundle_json": str(best_complaint_path),
            "session_state_dir": str(session_dir),
        },
    }
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run complaint-generator's adversarial harness with HACC evidence grounding.",
    )
    parser.add_argument("--output-dir", default=str(REPO_ROOT / "research_results" / "adversarial_runs" / _timestamp()))
    parser.add_argument("--num-sessions", type=int, default=3)
    parser.add_argument("--max-turns", type=int, default=4)
    parser.add_argument("--max-parallel", type=int, default=1)
    parser.add_argument("--personality", action="append", dest="personalities", help="Repeat to pin one or more complainant personalities.")
    parser.add_argument("--hacc-preset", default="core_hacc_policies")
    parser.add_argument("--hacc-count", type=int, default=None)
    parser.add_argument("--use-hacc-vector-search", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Use deterministic demo backends instead of live LLM routing.")
    parser.add_argument("--config", default=None, help="Optional complaint-generator config JSON to source backends from.")
    parser.add_argument("--backend-id", default=None, help="Optional backend id from the selected config.")
    parser.add_argument("--provider", default="copilot_cli", help="LLM router provider when not using --demo or --config.")
    parser.add_argument("--model", default=None, help="Optional model name when using the direct llm_router path.")
    parser.add_argument("--json", action="store_true", help="Print the full summary JSON.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = create_parser().parse_args(argv)
    summary = run_hacc_adversarial_batch(
        output_dir=args.output_dir,
        num_sessions=args.num_sessions,
        max_turns=args.max_turns,
        max_parallel=args.max_parallel,
        personalities=args.personalities,
        hacc_preset=args.hacc_preset,
        hacc_count=args.hacc_count,
        use_hacc_vector_search=args.use_hacc_vector_search,
        demo=args.demo,
        config_path=args.config,
        backend_id=args.backend_id,
        provider=args.provider,
        model=args.model,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Output directory: {summary['artifacts']['output_dir']}")
        print(f"Best complaint score: {summary['best_complaint']['score']:.3f}")
        print(f"Best complaint seed: {summary['best_complaint']['seed_type']} - {summary['best_complaint']['seed_summary']}")
        print(f"Recommended preset: {summary['optimization_report']['recommended_hacc_preset'] or summary['inputs']['hacc_preset']}")
        print(f"Results JSON: {summary['artifacts']['results_json']}")
        print(f"Optimization report: {summary['artifacts']['optimization_report_json']}")
        print(f"Best complaint bundle: {summary['artifacts']['best_complaint_bundle_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
