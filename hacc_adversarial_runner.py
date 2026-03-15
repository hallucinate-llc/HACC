#!/usr/bin/env python3
"""Run complaint-generator's adversarial harness against HACC evidence."""

from __future__ import annotations

import argparse
import os
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


def _autopatch_target_profiles() -> Dict[str, List[Path]]:
    return {
        "phase_manager_action_only": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "phase_manager.py",
        ],
        "phase_manager_only": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "phase_manager.py",
        ],
        "question_flow": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "phase_manager.py",
            COMPLAINT_GENERATOR_ROOT / "mediator" / "inquiries.py",
        ],
        "denoiser_focus": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "denoiser.py",
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "phase_manager.py",
        ],
        "full_mediator": [
            COMPLAINT_GENERATOR_ROOT / "mediator" / "mediator.py",
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "phase_manager.py",
        ],
    }


def _default_autopatch_target_files() -> List[Path]:
    return list(_autopatch_target_profiles()["question_flow"])


def _autopatch_constraints_for_profile(profile: str, target_files: List[Path]) -> Dict[str, Any]:
    if profile == "phase_manager_action_only":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "phase_manager.py":
                target_map[str(path.resolve())] = [
                    "_get_intake_action",
                ]
        if target_map:
            return {"target_symbols": target_map}
    if profile == "phase_manager_only":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "phase_manager.py":
                target_map[str(path.resolve())] = [
                    "_is_intake_complete",
                    "_get_intake_action",
                ]
        if target_map:
            return {"target_symbols": target_map}
    return {}


def _resolve_autopatch_target_files(target_files: Optional[List[str]], profile: str = "question_flow") -> List[Path]:
    if not target_files:
        return list(_autopatch_target_profiles().get(profile, _default_autopatch_target_files()))

    resolved: List[Path] = []
    for raw_path in target_files:
        candidate = Path(raw_path)
        if not candidate.is_absolute():
            candidate = (COMPLAINT_GENERATOR_ROOT / candidate).resolve()
        else:
            candidate = candidate.resolve()
        resolved.append(candidate)
    return resolved


def _build_agentic_llm_router(provider_name: Optional[str]) -> Any:
    _ensure_complaint_generator_on_path()

    try:
        from ipfs_datasets_py.llm_router import generate_text
    except Exception:
        return None

    normalized = str(provider_name or "").strip().lower()
    provider_mapping = {
        "codex": "codex_cli",
        "codex_cli": "codex_cli",
        "copilot": "copilot_cli",
        "copilot_cli": "copilot_cli",
        "copilot_sdk": "copilot_sdk",
        "openai": "openai",
        "gpt4": "openai",
        "anthropic": "anthropic",
        "claude": "anthropic",
        "claude_code": "claude_code",
        "claude_py": "claude_py",
        "gemini": "gemini_cli",
        "gemini_cli": "gemini_cli",
        "gemini_py": "gemini_py",
        "accelerate": "accelerate",
        "local": "local",
    }
    resolved_provider = provider_mapping.get(normalized)
    if resolved_provider is None:
        return None

    raw_timeout = os.environ.get("HACC_AGENTIC_AUTOPATCH_TIMEOUT", "").strip()
    try:
        autopatch_timeout = float(raw_timeout) if raw_timeout else 90.0
    except Exception:
        autopatch_timeout = 90.0

    class _PinnedRunnerLLMRouter:
        def __init__(self, provider: str):
            self.provider = provider

        def generate(
            self,
            prompt: str,
            method: Any = None,
            max_tokens: int = 2000,
            temperature: float = 0.7,
            router_kwargs: Optional[Dict[str, Any]] = None,
        ) -> str:
            kwargs = dict(router_kwargs or {})
            model_name = str(kwargs.pop("model_name", "") or os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL", ""))
            kwargs.setdefault("timeout", autopatch_timeout)
            return generate_text(
                prompt=prompt,
                provider=self.provider,
                model_name=model_name,
                max_new_tokens=max_tokens,
                temperature=temperature,
                **kwargs,
            )

        def get_usage_stats(self) -> Dict[str, Any]:
            return {"provider": self.provider}

    return _PinnedRunnerLLMRouter(resolved_provider)


def _run_agentic_autopatch(
    *,
    optimizer: Any,
    results: List[Any],
    report: Any,
    output_root: Path,
    target_files: List[Path],
    method: str,
    profile: str,
    constraints: Dict[str, Any],
    apply_patch: bool,
    provider_name: Optional[str],
    model_name: Optional[str],
) -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()

    autopatch_dir = output_root / "autopatch"
    autopatch_dir.mkdir(parents=True, exist_ok=True)
    autopatch_summary_path = autopatch_dir / "autopatch_summary.json"

    summary: Dict[str, Any] = {
        "requested": True,
        "method": method,
        "profile": profile,
        "target_files": [str(path) for path in target_files],
        "applied": False,
        "apply_success": False,
        "success": False,
        "patch_path": None,
        "patch_cid": None,
        "metadata": {},
        "metrics": {},
        "validation": None,
        "summary_json": str(autopatch_summary_path),
        "error": None,
    }

    try:
        previous_codex_model = os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL")
        if str(provider_name or "").strip().lower() in {"codex", "codex_cli"} and model_name:
            os.environ["IPFS_DATASETS_PY_CODEX_MODEL"] = str(model_name)
        result = optimizer.run_agentic_autopatch(
            results,
            target_files=target_files,
            method=method,
            constraints=constraints,
            report=report,
            llm_router=_build_agentic_llm_router(provider_name),
            metadata={
                "hacc_runner": True,
                "output_dir": str(output_root),
            },
        )
        summary["success"] = bool(getattr(result, "success", False))
        summary["patch_path"] = (
            str(Path(getattr(result, "patch_path")).resolve())
            if getattr(result, "patch_path", None)
            else None
        )
        summary["patch_cid"] = getattr(result, "patch_cid", None)
        summary["metadata"] = _sanitize_for_json(getattr(result, "metadata", {}))
        summary["metrics"] = _sanitize_for_json(getattr(result, "metrics", {}))
        summary["validation"] = _sanitize_for_json(getattr(result, "validation", None))
        result_error = getattr(result, "error_message", None)
        if result_error:
            summary["error"] = str(result_error)

        if apply_patch and summary["patch_path"]:
            from ipfs_datasets_py.optimizers.agentic.patch_control import PatchManager

            manager = PatchManager(patches_dir=autopatch_dir)
            patch = manager.load_patch(Path(summary["patch_path"]))
            summary["applied"] = True
            summary["apply_success"] = bool(manager.apply_patch(patch, COMPLAINT_GENERATOR_ROOT))
            if not summary["apply_success"]:
                summary["error"] = "Patch apply failed"
    except Exception as exc:
        summary["error"] = str(exc)
    finally:
        if str(provider_name or "").strip().lower() in {"codex", "codex_cli"}:
            if previous_codex_model is None:
                os.environ.pop("IPFS_DATASETS_PY_CODEX_MODEL", None)
            else:
                os.environ["IPFS_DATASETS_PY_CODEX_MODEL"] = previous_codex_model

    autopatch_summary_path.write_text(
        json.dumps(_sanitize_for_json(summary), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return summary


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
    emit_autopatch: bool = False,
    apply_autopatch: bool = False,
    autopatch_method: str = "test_driven",
    autopatch_profile: str = "question_flow",
    autopatch_target_files: Optional[List[str]] = None,
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
    autopatch_target_paths = _resolve_autopatch_target_files(autopatch_target_files, autopatch_profile)
    autopatch_constraints = _autopatch_constraints_for_profile(autopatch_profile, autopatch_target_paths)

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

    autopatch_summary = {
        "requested": False,
        "method": autopatch_method,
        "profile": autopatch_profile,
        "target_files": [str(path) for path in autopatch_target_paths],
        "constraints": _sanitize_for_json(autopatch_constraints),
        "applied": False,
        "apply_success": False,
        "success": False,
        "patch_path": None,
        "patch_cid": None,
        "metadata": {},
        "summary_json": None,
        "error": None,
    }
    if emit_autopatch or apply_autopatch:
        autopatch_summary = _run_agentic_autopatch(
            optimizer=optimizer,
            results=results,
            report=report,
            output_root=output_root,
            target_files=autopatch_target_paths,
            method=autopatch_method,
            profile=autopatch_profile,
            constraints=autopatch_constraints,
            apply_patch=apply_autopatch,
            provider_name=runtime_bundle["runtime"].get("provider"),
            model_name=runtime_bundle["runtime"].get("model"),
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
        "autopatch": _sanitize_for_json(autopatch_summary),
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
            "autopatch_summary_json": autopatch_summary.get("summary_json"),
            "autopatch_patch_path": autopatch_summary.get("patch_path"),
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
    parser.add_argument("--emit-autopatch", action="store_true", help="Generate an optimizer patch artifact targeting the mediator codebase.")
    parser.add_argument("--apply-autopatch", action="store_true", help="Generate and apply the optimizer patch to complaint-generator.")
    parser.add_argument("--autopatch-method", default="test_driven", help="Agentic optimization method for autopatch generation.")
    parser.add_argument(
        "--autopatch-profile",
        default="question_flow",
        choices=sorted(_autopatch_target_profiles().keys()),
        help=(
            "Named autopatch target profile. question_flow keeps the default scope small "
            "for live runs; explicit --autopatch-target-file values override the profile."
        ),
    )
    parser.add_argument(
        "--autopatch-target-file",
        action="append",
        dest="autopatch_target_files",
        help=(
            "Repeat to override autopatch target files. Relative paths are resolved from "
            "complaint-generator/. Default profile is question_flow "
            "(complaint_phases/phase_manager.py + mediator/inquiries.py)."
        ),
    )
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
        emit_autopatch=args.emit_autopatch,
        apply_autopatch=args.apply_autopatch,
        autopatch_method=args.autopatch_method,
        autopatch_profile=args.autopatch_profile,
        autopatch_target_files=args.autopatch_target_files,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Output directory: {summary['artifacts']['output_dir']}")
        print(f"Best complaint score: {summary['best_complaint']['score']:.3f}")
        print(f"Best complaint seed: {summary['best_complaint']['seed_type']} - {summary['best_complaint']['seed_summary']}")
        print(f"Recommended preset: {summary['optimization_report']['recommended_hacc_preset'] or summary['inputs']['hacc_preset']}")
        if summary["autopatch"]["requested"]:
            print(f"Autopatch success: {summary['autopatch']['success']}")
            print(f"Autopatch applied: {summary['autopatch']['apply_success']}")
            if summary["autopatch"]["patch_path"]:
                print(f"Autopatch patch: {summary['autopatch']['patch_path']}")
        print(f"Results JSON: {summary['artifacts']['results_json']}")
        print(f"Optimization report: {summary['artifacts']['optimization_report_json']}")
        print(f"Best complaint bundle: {summary['artifacts']['best_complaint_bundle_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
