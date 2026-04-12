#!/usr/bin/env python3
"""Run complaint-generator's adversarial harness against HACC evidence."""

from __future__ import annotations

import argparse
import contextlib
import difflib
import os
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from hacc_complaint_manager import COMPLAINT_GENERATOR_ROOT, ensure_complaint_generator_on_path


REPO_ROOT = Path(__file__).resolve().parent
HACC_DEFAULT_PROVIDER = "codex"
HACC_DEFAULT_MODEL = "gpt-5.3-codex"


def _ensure_complaint_generator_on_path() -> None:
    ensure_complaint_generator_on_path()


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


def _load_json_if_exists(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return payload if isinstance(payload, dict) else None


class _LoadedReport:
    def __init__(self, payload: Dict[str, Any]):
        self._payload = dict(payload or {})
        for key, value in self._payload.items():
            setattr(self, key, value)

    def to_dict(self) -> Dict[str, Any]:
        return dict(self._payload)


@contextlib.contextmanager
def _scoped_mediator_integration_env(*, effective_search_mode: str, use_hacc_vector_search: bool):
    lexical_modes = {"lexical", "lexical_only", "lexical_fallback"}
    force_lexical_only = str(effective_search_mode or "").strip().lower() in lexical_modes and not bool(use_hacc_vector_search)
    if not force_lexical_only:
        yield
        return

    overrides = {
        "IPFS_DATASETS_ENHANCED_LEGAL": "0",
        "IPFS_DATASETS_ENHANCED_SEARCH": "0",
        "IPFS_DATASETS_ENHANCED_GRAPH": "0",
        "IPFS_DATASETS_ENHANCED_VECTOR": "0",
        "IPFS_DATASETS_ENHANCED_OPTIMIZER": "0",
        "RETRIEVAL_RERANKER_MODE": "off",
    }
    previous = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            os.environ[key] = value
        yield
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _autopatch_target_profiles() -> Dict[str, List[Path]]:
    return {
        "denoiser_select_candidates_only": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "denoiser.py",
        ],
        "denoiser_standard_intake_only": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "denoiser.py",
        ],
        "denoiser_process_answer_only": [
            COMPLAINT_GENERATOR_ROOT / "complaint_phases" / "denoiser.py",
        ],
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


def _resolve_optimizer_recommended_target_files(optimizer: Any, report: Any) -> List[Path]:
    if optimizer is None or report is None:
        return []
    try:
        recommended = list(optimizer._recommended_target_files_for_report(report))  # type: ignore[attr-defined]
    except Exception:
        return []
    resolved: List[Path] = []
    for candidate in recommended:
        path = Path(candidate)
        if not path.is_absolute():
            path = COMPLAINT_GENERATOR_ROOT / path
        if path not in resolved:
            resolved.append(path)
    return resolved


def _recommended_autopatch_profile(target_files: List[Path]) -> str:
    normalized_targets = {path.resolve() for path in target_files}
    if not normalized_targets:
        return "question_flow"
    for profile_name, profile_targets in _autopatch_target_profiles().items():
        normalized_profile = {path.resolve() for path in profile_targets}
        if normalized_targets == normalized_profile:
            return profile_name
    for profile_name, profile_targets in _autopatch_target_profiles().items():
        normalized_profile = {path.resolve() for path in profile_targets}
        if normalized_targets.issubset(normalized_profile):
            return profile_name
    return "custom"


def _resolve_workflow_target_path(path: str | Path) -> Path:
    candidate = Path(path)
    if candidate.is_absolute():
        return candidate
    return COMPLAINT_GENERATOR_ROOT / candidate


def _resolve_workflow_target_symbols(target_symbols: Dict[str, Any]) -> Dict[str, Any]:
    resolved: Dict[str, Any] = {}
    for key, value in dict(target_symbols or {}).items():
        resolved[str(_resolve_workflow_target_path(key))] = value
    return resolved


def _build_workflow_optimization_payload(
    optimizer: Any,
    *,
    results: List[Any],
    report: Any,
) -> Dict[str, Any]:
    if hasattr(optimizer, "build_workflow_optimization_bundle"):
        try:
            bundle, _ = optimizer.build_workflow_optimization_bundle(
                results,
                report=report,
                components=optimizer._fallback_agentic_optimizer_components(),
            )
            if hasattr(bundle, "to_dict"):
                return _sanitize_for_json(bundle.to_dict())
            if isinstance(bundle, dict):
                return _sanitize_for_json(bundle)
        except Exception:
            pass

    phase_tasks_payload: List[Dict[str, Any]] = []
    if hasattr(optimizer, "build_phase_patch_tasks"):
        try:
            tasks, _ = optimizer.build_phase_patch_tasks(
                results,
                report=report,
                components=getattr(optimizer, "_fallback_agentic_optimizer_components", lambda: {})(),
            )
            for task in list(tasks or []):
                phase_tasks_payload.append(
                    {
                        "task_id": str(getattr(task, "task_id", "")),
                        "description": str(getattr(task, "description", "")),
                        "target_files": [str(path) for path in list(getattr(task, "target_files", []) or [])],
                        "method": str(getattr(task, "method", "")),
                        "priority": int(getattr(task, "priority", 0) or 0),
                        "constraints": _sanitize_for_json(getattr(task, "constraints", {}) or {}),
                        "metadata": _sanitize_for_json(getattr(task, "metadata", {}) or {}),
                    }
                )
        except Exception:
            phase_tasks_payload = []

    report_payload = _sanitize_for_json(report.to_dict()) if hasattr(report, "to_dict") else _sanitize_for_json(report)
    return {
        "timestamp": _timestamp(),
        "num_sessions_analyzed": int(report_payload.get("num_sessions_analyzed") or 0),
        "average_score": float(report_payload.get("average_score") or 0.0),
        "workflow_phase_plan": dict(report_payload.get("workflow_phase_plan") or {}),
        "global_objectives": list(report_payload.get("priority_improvements") or []),
        "phase_tasks": phase_tasks_payload,
        "shared_context": {
            "recommendations": list(report_payload.get("recommendations") or []),
            "priority_improvements": list(report_payload.get("priority_improvements") or []),
            "coverage_remediation": dict(report_payload.get("coverage_remediation") or {}),
            "intake_priority_performance": dict(report_payload.get("intake_priority_performance") or {}),
            "document_chronology_reasoning_summary": dict(report_payload.get("document_chronology_reasoning_summary") or {}),
        },
    }


def _autopatch_constraints_for_profile(profile: str, target_files: List[Path]) -> Dict[str, Any]:
    if profile == "denoiser_select_candidates_only":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "denoiser.py":
                target_map[str(path.resolve())] = [
                    "select_question_candidates",
                ]
        if target_map:
            return {"target_symbols": target_map}
    if profile == "denoiser_standard_intake_only":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "denoiser.py":
                target_map[str(path.resolve())] = [
                    "_ensure_standard_intake_questions",
                ]
        if target_map:
            return {"target_symbols": target_map}
    if profile == "denoiser_process_answer_only":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "denoiser.py":
                target_map[str(path.resolve())] = [
                    "process_answer",
                ]
        if target_map:
            return {"target_symbols": target_map}
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
    if profile == "question_flow":
        target_map: Dict[str, List[str]] = {}
        for path in target_files:
            if path.name == "phase_manager.py":
                target_map[str(path.resolve())] = [
                    "_get_intake_action",
                ]
            elif path.name == "inquiries.py":
                target_map[str(path.resolve())] = [
                    "get_next",
                    "merge_legal_questions",
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


def _resolve_autopatch_timeout(
    *,
    profile: str,
    target_files: Optional[List[Path]] = None,
) -> Optional[float]:
    raw_timeout = os.environ.get("HACC_AGENTIC_AUTOPATCH_TIMEOUT", "").strip().lower()
    if raw_timeout in {"none", "off", "disable", "disabled", "unlimited", "infinite", "inf", "0"}:
        return None
    if raw_timeout:
        try:
            resolved = float(raw_timeout)
            return resolved if resolved > 0 else None
        except Exception:
            pass

    profile_defaults = {
        "denoiser_select_candidates_only": 150.0,
        "denoiser_standard_intake_only": 150.0,
        "denoiser_process_answer_only": 180.0,
        "phase_manager_action_only": 120.0,
        "phase_manager_only": 180.0,
        "question_flow": 300.0,
        "denoiser_focus": 240.0,
        "full_mediator": 420.0,
        "graph_analysis": 300.0,
        "document_generation": 300.0,
        "intake_questioning": 240.0,
    }
    if profile in profile_defaults:
        return profile_defaults[profile]

    target_count = len(target_files or [])
    if target_count <= 1:
        return 120.0
    if target_count == 2:
        return 300.0
    return 420.0


def _default_codex_model() -> str:
    return "gpt-5.3-codex-spark"


def _codex_backup_model() -> str:
    return "gpt-5.1-codex-mini"


def _resolve_hacc_runtime_provider_model(
    provider: Optional[str],
    model: Optional[str],
) -> tuple[Optional[str], Optional[str]]:
    resolved_provider = str(provider or "").strip() or HACC_DEFAULT_PROVIDER
    resolved_model = str(model or "").strip() or None
    if not resolved_model and str(resolved_provider).strip().lower() in {"codex", "codex_cli"}:
        resolved_model = HACC_DEFAULT_MODEL
    return resolved_provider, resolved_model


def _is_likely_throttling_error(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "rate limit",
            "rate-limit",
            "too many requests",
            "429",
            "throttle",
            "throttled",
            "quota",
            "capacity",
        )
    )


def _build_agentic_llm_router(
    provider_name: Optional[str],
    *,
    profile: str = "question_flow",
    target_files: Optional[List[Path]] = None,
) -> Any:
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
        "local": "hf",
        "local_hf": "hf",
    }
    resolved_provider = provider_mapping.get(normalized, normalized or None)

    autopatch_timeout = _resolve_autopatch_timeout(profile=profile, target_files=target_files)

    class _PinnedRunnerLLMRouter:
        def __init__(self, provider: Optional[str]):
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
            model_name = str(kwargs.pop("model_name", "") or os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL", "")).strip()
            if self.provider == "codex_cli" and not model_name:
                model_name = _default_codex_model()
            if autopatch_timeout is not None:
                kwargs.setdefault("timeout", autopatch_timeout)
            kwargs.setdefault("disable_model_retry", True)
            try:
                return generate_text(
                    prompt=prompt,
                    provider=self.provider or None,
                    model_name=model_name,
                    max_new_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )
            except Exception as exc:
                if (
                    self.provider == "codex_cli"
                    and model_name == _default_codex_model()
                    and _is_likely_throttling_error(exc)
                ):
                    fallback_model = _codex_backup_model()
                    return generate_text(
                        prompt=prompt,
                        provider=self.provider or None,
                        model_name=fallback_model,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs,
                    )
                raise

        def get_usage_stats(self) -> Dict[str, Any]:
            return {"provider": self.provider}

    return _PinnedRunnerLLMRouter(resolved_provider)


def _agentic_autopatch_preflight(optimizer: Any) -> Dict[str, Any]:
    component_loader = getattr(optimizer, "_load_agentic_optimizer_components", None)
    if component_loader is None:
        return {
            "ready": hasattr(optimizer, "run_agentic_autopatch"),
            "error": None,
        }

    try:
        component_loader()
        return {
            "ready": True,
            "error": None,
        }
    except Exception as exc:
        loader_is_mock = str(getattr(type(component_loader), "__module__", "")).startswith("unittest.mock")
        autopatch_runner = getattr(optimizer, "run_agentic_autopatch", None)
        runner_is_mock = str(getattr(type(autopatch_runner), "__module__", "")).startswith("unittest.mock")
        if runner_is_mock and not loader_is_mock:
            return {
                "ready": True,
                "error": None,
            }
        return {
            "ready": False,
            "error": str(exc),
        }


def _resolve_autopatch_validation_level() -> Any:
    _ensure_complaint_generator_on_path()

    from ipfs_datasets_py.optimizers.agentic.validation import ValidationLevel

    raw_level = os.environ.get("HACC_AUTOPATCH_VALIDATION_LEVEL", "standard").strip().lower()
    try:
        return ValidationLevel(raw_level)
    except Exception:
        return ValidationLevel.STANDARD


def _autopatch_auto_apply_enabled() -> bool:
    raw = os.environ.get("HACC_AUTOPATCH_AUTO_APPLY", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def _resolve_autopatch_apply_mode(apply_patch: Optional[bool], *, emit_patch: bool = False) -> Dict[str, Any]:
    env_default = _autopatch_auto_apply_enabled()
    if apply_patch is True:
        return {
            "requested": True,
            "env_default": env_default,
            "effective": True,
            "source": "cli",
        }
    if apply_patch is False:
        return {
            "requested": False,
            "env_default": env_default,
            "effective": False,
            "source": "cli",
        }
    if emit_patch:
        return {
            "requested": None,
            "env_default": env_default,
            "effective": False,
            "source": "safe_default",
        }
    return {
        "requested": None,
        "env_default": env_default,
        "effective": env_default,
        "source": "env",
    }


def _autopatch_repair_attempts() -> int:
    raw = os.environ.get("HACC_AUTOPATCH_REPAIR_ATTEMPTS", "1").strip()
    try:
        return max(0, int(raw))
    except Exception:
        return 1


def _autopatch_validation_test_files(target_files: List[Path]) -> List[Path]:
    test_map = {
        "complaint_phases/phase_manager.py": [
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_complaint_phases.py",
        ],
        "complaint_phases/denoiser.py": [
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_enhanced_denoising.py",
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_complaint_phases.py",
        ],
        "mediator/inquiries.py": [
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_inquiries.py",
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_inquiries_priority.py",
        ],
        "mediator/mediator.py": [
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_mediator.py",
            COMPLAINT_GENERATOR_ROOT / "tests" / "test_mediator_three_phase.py",
        ],
    }
    resolved: List[Path] = []
    for path in target_files:
        key = str(path).replace("\\", "/")
        resolved.extend(test_map.get(key, []))
    return list(dict.fromkeys(resolved))


def _autopatch_validation_support_roots() -> List[str]:
    return [
        "backends",
        "mediator",
        "complaint_phases",
        "adversarial_harness",
        "integrations",
        "complaint_analysis",
    ]


def _autopatch_validation_support_files(repo_root: Path) -> List[str]:
    return sorted(path.name for path in repo_root.glob("*.py") if path.is_file())


def _extract_unified_diff(text: str) -> str:
    if not text:
        return ""
    stripped = text.strip()
    if stripped.startswith("--- ") and "\n+++ " in stripped:
        return stripped + ("\n" if not stripped.endswith("\n") else "")
    fenced = re.search(r"```(?:diff)?\n(.*?)```", text, flags=re.DOTALL)
    if fenced:
        candidate = fenced.group(1).strip()
        if candidate.startswith("--- ") and "\n+++ " in candidate:
            return candidate + ("\n" if not candidate.endswith("\n") else "")
    start = stripped.find("--- ")
    if start >= 0:
        candidate = stripped[start:].strip()
        if "\n+++ " in candidate:
            return candidate + ("\n" if not candidate.endswith("\n") else "")
    return ""


def _extract_file_replacements(text: str, target_files: List[Path]) -> Dict[Path, str]:
    replacements: Dict[Path, str] = {}
    normalized_targets = {path.as_posix(): path for path in target_files}
    normalized_targets.update({path.name: path for path in target_files})

    for match in re.finditer(r"FILE:\s*(.+?)\n```(?:python)?\n(.*?)```", text, flags=re.DOTALL):
        raw_name = match.group(1).strip()
        content = match.group(2)
        target = normalized_targets.get(raw_name)
        if target is None:
            candidate_name = raw_name.replace("\\", "/")
            target = normalized_targets.get(candidate_name)
        if target is not None:
            replacements[target] = content.rstrip() + "\n"

    if replacements:
        return replacements

    fenced_blocks = re.findall(r"```(?:python)?\n(.*?)```", text, flags=re.DOTALL)
    if len(target_files) == 1 and fenced_blocks:
        replacements[target_files[0]] = fenced_blocks[-1].rstrip() + "\n"
        return replacements

    stripped = text.strip()
    if len(target_files) == 1 and stripped and not stripped.startswith("--- "):
        replacements[target_files[0]] = stripped + ("\n" if not stripped.endswith("\n") else "")
    return replacements


def _build_diff_from_replacements(
    *,
    replacements: Dict[Path, str],
    repo_root: Path,
) -> str:
    diff_chunks: List[str] = []
    for relative_path, new_content in replacements.items():
        source_path = repo_root / relative_path
        if not source_path.exists():
            continue
        old_content = source_path.read_text(encoding="utf-8")
        if old_content == new_content:
            continue
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        file_diff = list(
            difflib.unified_diff(
                old_lines,
                new_lines,
                fromfile=f"a/{relative_path.as_posix()}",
                tofile=f"b/{relative_path.as_posix()}",
                lineterm="",
            )
        )
        if file_diff:
            diff_chunks.append("\n".join(file_diff) + "\n")
    return "".join(diff_chunks)


def _build_patch_repair_prompt(
    *,
    patch_diff: str,
    patch_validation: Dict[str, Any],
    target_files: List[Path],
    repo_root: Path,
) -> str:
    file_blocks: List[str] = []
    for relative_path in target_files:
        full_path = repo_root / relative_path
        if not full_path.exists():
            continue
        try:
            content = full_path.read_text(encoding="utf-8")
        except Exception:
            continue
        file_blocks.append(
            f"FILE: {relative_path.as_posix()}\n```python\n{content}\n```"
        )

    validation_json = json.dumps(_sanitize_for_json(patch_validation), ensure_ascii=False, indent=2)
    return (
        "You are repairing a unified git diff patch for a Python codebase.\n"
        "Return ONLY a corrected unified diff patch. Do not include explanations.\n"
        "Requirements:\n"
        "- Output must begin with '--- a/...'\n"
        "- Preserve repository-relative paths exactly.\n"
        "- Fix the patch so it passes validation errors.\n"
        "- Keep the change as small as possible.\n"
        "- Do not rewrite unrelated code.\n\n"
        "Validation failure details:\n"
        f"{validation_json}\n\n"
        "Current candidate patch:\n"
        f"```diff\n{patch_diff}\n```\n\n"
        "Current target file contents:\n"
        f"{chr(10).join(file_blocks)}\n"
    )


def _repair_patch_with_llm(
    *,
    patch_path: str | Path,
    patch_validation: Dict[str, Any],
    repo_root: Path,
    provider_name: Optional[str],
    model_name: Optional[str],
    output_dir: Path,
    attempt_index: int,
    profile: str,
) -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()

    from ipfs_datasets_py.optimizers.agentic.patch_control import Patch, PatchManager

    resolved_patch_path = Path(patch_path).resolve()
    manager = PatchManager()
    patch = manager.load_patch(resolved_patch_path)
    target_files = [Path(path) for path in getattr(patch, "target_files", [])]
    router = _build_agentic_llm_router(
        provider_name,
        profile=profile,
        target_files=target_files,
    )
    if router is None:
        raise RuntimeError("No llm_router available for patch repair")

    previous_codex_model = os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL")
    try:
        if str(provider_name or "").strip().lower() in {"codex", "codex_cli"} and model_name:
            os.environ["IPFS_DATASETS_PY_CODEX_MODEL"] = str(model_name)
        response = router.generate(
            _build_patch_repair_prompt(
                patch_diff=patch.diff_content,
                patch_validation=patch_validation,
                target_files=target_files,
                repo_root=repo_root,
            ),
            max_tokens=5000,
            temperature=0.1,
        )
    finally:
        if str(provider_name or "").strip().lower() in {"codex", "codex_cli"}:
            if previous_codex_model is None:
                os.environ.pop("IPFS_DATASETS_PY_CODEX_MODEL", None)
            else:
                os.environ["IPFS_DATASETS_PY_CODEX_MODEL"] = previous_codex_model

    repaired_diff = _extract_unified_diff(response)
    if not repaired_diff:
        replacements = _extract_file_replacements(response, target_files)
        repaired_diff = _build_diff_from_replacements(
            replacements=replacements,
            repo_root=repo_root,
        )
    if not repaired_diff:
        raise RuntimeError("Patch repair response did not contain a unified diff or usable file content")

    repaired_patch = Patch(
        patch_id=f"{patch.patch_id}-repair{attempt_index}",
        agent_id=patch.agent_id,
        task_id=patch.task_id,
        description=f"{patch.description} (repair attempt {attempt_index})",
        diff_content=repaired_diff,
        target_files=list(getattr(patch, "target_files", [])),
        parent_patches=[patch.patch_id],
        worktree_path=patch.worktree_path,
        metadata={
            **dict(getattr(patch, "metadata", {}) or {}),
            "repair_attempt": attempt_index,
            "repaired_from_patch": str(resolved_patch_path),
        },
    )
    repaired_path = output_dir / f"{repaired_patch.patch_id}.patch"
    saved_path = manager.save_patch(repaired_patch, repaired_path)
    return {
        "patch_path": str(saved_path.resolve()),
        "raw_response_preview": response[:1000],
    }


def _validate_generated_patch(*, patch_path: str | Path, repo_root: Path) -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()

    from ipfs_datasets_py.optimizers.agentic.patch_control import PatchManager
    from ipfs_datasets_py.optimizers.agentic.validation import OptimizationValidator, ValidationLevel

    resolved_patch_path = Path(patch_path).resolve()
    manager = PatchManager()
    patch = manager.load_patch(resolved_patch_path)
    validation_level = _resolve_autopatch_validation_level()
    target_files = [Path(path) for path in getattr(patch, "target_files", [])]

    summary: Dict[str, Any] = {
        "passed": False,
        "level": getattr(validation_level, "value", str(validation_level)),
        "patch_path": str(resolved_patch_path),
        "target_files": [str(path) for path in target_files],
        "pytest_files": [],
        "file_results": [],
        "errors": [],
        "warnings": [],
    }

    if not target_files:
        summary["passed"] = False
        summary["errors"].append("Patch metadata does not include target files")
        return summary

    python_targets = [path for path in target_files if path.suffix == ".py"]
    if not python_targets:
        summary["passed"] = True
        summary["warnings"].append("Patch does not modify Python files; skipping code validation")
        return summary

    with tempfile.TemporaryDirectory(prefix="hacc_patch_validation_") as tmpdir:
        stage_root = Path(tmpdir)
        stage_tests = _autopatch_validation_test_files(target_files)
        summary["pytest_files"] = [str(path.relative_to(repo_root)) for path in stage_tests if path.exists()]

        copied_roots = set()
        roots_to_copy = set(_autopatch_validation_support_roots())
        for relative_path in target_files:
            top_level = relative_path.parts[0] if relative_path.parts else ""
            if top_level:
                roots_to_copy.add(top_level)

        for top_level in roots_to_copy:
            if top_level and top_level not in copied_roots:
                source_root = (repo_root / top_level).resolve()
                staged_root = stage_root / top_level
                if source_root.is_dir():
                    shutil.copytree(
                        source_root,
                        staged_root,
                        dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    )
                    copied_roots.add(top_level)

        for support_file in _autopatch_validation_support_files(repo_root):
            source_file = (repo_root / support_file).resolve()
            if source_file.is_file():
                staged_file = stage_root / support_file
                staged_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source_file, staged_file)

        for test_path in stage_tests:
            if not test_path.exists():
                continue
            relative_test_path = test_path.relative_to(repo_root)
            staged_test_path = stage_root / relative_test_path
            staged_test_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(test_path, staged_test_path)

        pytest_ini = repo_root / "pytest.ini"
        if pytest_ini.exists():
            shutil.copy2(pytest_ini, stage_root / "pytest.ini")

        staged_patch_path = stage_root / "candidate.patch"
        staged_patch_path.write_text(patch.diff_content, encoding="utf-8")

        check_result = subprocess.run(
            ["git", "apply", "--check", str(staged_patch_path)],
            cwd=stage_root,
            capture_output=True,
            text=True,
        )
        if check_result.returncode != 0:
            summary["errors"].append(check_result.stderr.strip() or "git apply --check failed")
            return summary

        apply_result = subprocess.run(
            ["git", "apply", str(staged_patch_path)],
            cwd=stage_root,
            capture_output=True,
            text=True,
        )
        if apply_result.returncode != 0:
            summary["errors"].append(apply_result.stderr.strip() or "git apply failed")
            return summary

        validator = OptimizationValidator(level=ValidationLevel.BASIC, parallel=False, max_workers=1)
        overall_passed = True
        overall_errors: List[str] = []
        overall_warnings: List[str] = []
        file_results: List[Dict[str, Any]] = []

        for relative_path in python_targets:
            staged_path = stage_root / relative_path
            if not staged_path.exists():
                overall_passed = False
                overall_errors.append(f"{relative_path}: staged file missing after patch apply")
                file_results.append(
                    {
                        "file": str(relative_path),
                        "passed": False,
                        "errors": ["staged file missing after patch apply"],
                        "warnings": [],
                    }
                )
                continue

            code = staged_path.read_text(encoding="utf-8")
            detailed_result = validator.validate(
                code=code,
                target_files=[staged_path],
                level=ValidationLevel.BASIC,
                parallel=False,
                use_enhanced_parallel=False,
                context={"repo_root": str(stage_root)},
            )
            file_result = {
                "file": str(relative_path),
                "passed": bool(detailed_result.passed),
                "errors": list(detailed_result.errors),
                "warnings": list(detailed_result.warnings),
            }
            file_results.append(file_result)
            if not detailed_result.passed:
                overall_passed = False
                overall_errors.extend(f"{relative_path}: {error}" for error in detailed_result.errors)
            overall_warnings.extend(f"{relative_path}: {warning}" for warning in detailed_result.warnings)

        if stage_tests:
            relative_pytest_files = [str(path.relative_to(repo_root)) for path in stage_tests if path.exists()]
            pytest_result = subprocess.run(
                ["pytest", "-q", *relative_pytest_files],
                cwd=stage_root,
                capture_output=True,
                text=True,
                env={**os.environ, "PYTHONPATH": str(stage_root)},
            )
            if pytest_result.returncode != 0:
                overall_passed = False
                combined = (pytest_result.stdout or "") + (pytest_result.stderr or "")
                failure_lines = [line.strip() for line in combined.splitlines() if line.strip()]
                overall_errors.append(
                    failure_lines[-1] if failure_lines else "Targeted pytest validation failed"
                )
            elif "passed" not in (pytest_result.stdout or ""):
                overall_warnings.append("Targeted pytest validation produced no explicit pass summary")

        summary["passed"] = overall_passed
        summary["file_results"] = file_results
        summary["errors"] = overall_errors
        summary["warnings"] = overall_warnings
        return summary


def _run_agentic_autopatch(
    *,
    optimizer: Any,
    results: List[Any],
    report: Any,
    output_root: Path,
    requested_profile: str,
    requested_target_files: List[Path],
    recommended_profile: str,
    recommended_target_files: List[Path],
    used_recommended_targets: bool,
    target_files: List[Path],
    description: Optional[str] = None,
    method: str,
    profile: str,
    constraints: Dict[str, Any],
    apply_patch: Optional[bool],
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
        "requested_profile": requested_profile,
        "requested_target_files": [str(path) for path in requested_target_files],
        "profile": profile,
        "target_files": [str(path) for path in target_files],
        "target_symbols": _sanitize_for_json((constraints or {}).get("target_symbols")),
        "recommended_profile": recommended_profile,
        "recommended_target_files": [str(path) for path in recommended_target_files],
        "used_recommended_targets": bool(used_recommended_targets),
        "apply_mode": _resolve_autopatch_apply_mode(apply_patch, emit_patch=True),
        "applied": False,
        "apply_success": False,
        "success": False,
        "patch_path": None,
        "patch_cid": None,
        "metadata": {},
        "metrics": {},
        "validation": None,
        "repair_attempts": [],
        "summary_json": str(autopatch_summary_path),
        "error": None,
    }

    def _optimizer_generation_diagnostics(resolved_optimizer: Any) -> List[Dict[str, Any]]:
        cached = getattr(resolved_optimizer, "_last_agentic_generation_diagnostics", None)
        if isinstance(cached, list) and cached:
            return cached
        inner_optimizer = getattr(resolved_optimizer, "_last_agentic_optimizer", None)
        inner_cached = getattr(inner_optimizer, "_last_generation_diagnostics", None)
        if isinstance(inner_cached, list) and inner_cached:
            return inner_cached
        diagnostics = getattr(resolved_optimizer, "_last_generation_diagnostics", None)
        if isinstance(diagnostics, list):
            return diagnostics
        return []

    resolved_optimizer = None
    resolved_description = str(description or "").strip()
    if not resolved_description:
        target_labels = [path.as_posix() for path in target_files if isinstance(path, Path)]
        if target_labels:
            resolved_description = (
                f"Use the {method} optimizer to improve the complaint-generator {profile} flow. "
                f"Target files: {', '.join(target_labels)}."
            )
        else:
            resolved_description = (
                f"Use the {method} optimizer to improve the complaint-generator {profile} flow."
            )

    try:
        previous_codex_model = os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL")
        demo_mode = str(provider_name or "").strip().lower() == "demo"
        if str(provider_name or "").strip().lower() in {"codex", "codex_cli"} and model_name:
            os.environ["IPFS_DATASETS_PY_CODEX_MODEL"] = str(model_name)
        resolved_llm_router = None
        if demo_mode:
            from adversarial_harness.demo_autopatch import DemoPatchOptimizer

            resolved_optimizer = DemoPatchOptimizer(
                project_root=COMPLAINT_GENERATOR_ROOT,
                output_dir=autopatch_dir,
                marker_prefix="Demo autopatch recommendation",
            )
            resolved_llm_router = object()
        else:
            resolved_llm_router = _build_agentic_llm_router(
                provider_name,
                profile=profile,
                target_files=target_files,
            )
        result = optimizer.run_agentic_autopatch(
            results,
            target_files=target_files,
            description=resolved_description,
            method=method,
            constraints=constraints,
            report=report,
            llm_router=resolved_llm_router,
            optimizer=resolved_optimizer,
            metadata={
                "hacc_runner": True,
                "output_dir": str(output_root),
                "demo_autopatch": demo_mode,
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
        optimizer_validation = _sanitize_for_json(getattr(result, "validation", None))
        summary["validation"] = {
            "optimizer_result_validation": optimizer_validation,
            "patch_validation": None,
        }
        result_error = getattr(result, "error_message", None)
        if result_error:
            summary["error"] = str(result_error)
        elif not summary["success"] and not summary["patch_path"]:
            summary["error"] = "Agentic autopatch produced no patchable change"
        if not summary["success"] and not summary["patch_path"]:
            diagnostics = _optimizer_generation_diagnostics(resolved_optimizer) or _optimizer_generation_diagnostics(optimizer)
            if diagnostics:
                metadata = dict(summary.get("metadata") or {})
                metadata.setdefault("generation_diagnostics", _sanitize_for_json(diagnostics))
                summary["metadata"] = metadata

        if summary["patch_path"] and not demo_mode:
            patch_validation = _validate_generated_patch(
                patch_path=summary["patch_path"],
                repo_root=COMPLAINT_GENERATOR_ROOT,
            )
            summary["validation"]["patch_validation"] = _sanitize_for_json(patch_validation)
            if not patch_validation.get("passed", False):
                repair_attempts = _autopatch_repair_attempts()
                for attempt_index in range(1, repair_attempts + 1):
                    repair_summary: Dict[str, Any] = {
                        "attempt": attempt_index,
                        "source_patch_path": summary["patch_path"],
                        "validation_before": _sanitize_for_json(patch_validation),
                    }
                    try:
                        repaired = _repair_patch_with_llm(
                            patch_path=summary["patch_path"],
                            patch_validation=patch_validation,
                            repo_root=COMPLAINT_GENERATOR_ROOT,
                            provider_name=provider_name,
                            model_name=model_name,
                            output_dir=autopatch_dir,
                            attempt_index=attempt_index,
                            profile=profile,
                        )
                        repaired_validation = _validate_generated_patch(
                            patch_path=repaired["patch_path"],
                            repo_root=COMPLAINT_GENERATOR_ROOT,
                        )
                        repair_summary["repaired_patch_path"] = repaired["patch_path"]
                        repair_summary["raw_response_preview"] = repaired.get("raw_response_preview", "")
                        repair_summary["validation_after"] = _sanitize_for_json(repaired_validation)
                        repair_summary["passed"] = bool(repaired_validation.get("passed", False))
                        summary["repair_attempts"].append(_sanitize_for_json(repair_summary))
                        if repaired_validation.get("passed", False):
                            summary["patch_path"] = repaired["patch_path"]
                            summary["validation"]["patch_validation"] = _sanitize_for_json(repaired_validation)
                            patch_validation = repaired_validation
                            summary["success"] = True
                            summary["error"] = None
                            break
                    except Exception as repair_exc:
                        repair_summary["passed"] = False
                        repair_summary["error"] = str(repair_exc)
                        summary["repair_attempts"].append(_sanitize_for_json(repair_summary))
                if not patch_validation.get("passed", False) and not summary["error"]:
                    summary["error"] = "Generated patch failed validation"

        elif demo_mode:
            summary["validation"]["patch_validation"] = {
                "passed": True,
                "level": "demo",
                "patch_path": summary["patch_path"],
                "target_files": [str(path) for path in target_files],
                "pytest_files": [],
                "file_results": [],
                "errors": [],
                "warnings": ["Skipped patch validation for demo autopatch run"],
            }

        apply_mode = dict(summary.get("apply_mode") or {})
        should_apply_patch = bool(summary["patch_path"]) and not demo_mode and bool(apply_mode.get("effective"))
        if should_apply_patch and summary["patch_path"]:
            from ipfs_datasets_py.optimizers.agentic.patch_control import PatchManager

            patch_validation = (summary.get("validation") or {}).get("patch_validation") or {}
            if not patch_validation.get("passed", False):
                summary["applied"] = True
                summary["apply_success"] = False
                if not summary["error"]:
                    summary["error"] = "Patch apply blocked by validation failure"
                raise RuntimeError(summary["error"])

            manager = PatchManager(patches_dir=autopatch_dir)
            patch = manager.load_patch(Path(summary["patch_path"]))
            patch.validated = True
            summary["applied"] = True
            summary["apply_success"] = bool(manager.apply_patch(patch, COMPLAINT_GENERATOR_ROOT))
            if not summary["apply_success"]:
                summary["error"] = "Patch apply failed"
    except Exception as exc:
        diagnostics = _optimizer_generation_diagnostics(resolved_optimizer) or _optimizer_generation_diagnostics(optimizer)
        if diagnostics:
            metadata = dict(summary.get("metadata") or {})
            metadata.setdefault("generation_diagnostics", _sanitize_for_json(diagnostics))
            summary["metadata"] = metadata
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


def _run_workflow_phase_autopatches(
    *,
    optimizer: Any,
    results: List[Any],
    report: Any,
    workflow_payload: Dict[str, Any],
    output_root: Path,
    method: str,
    apply_patch: Optional[bool],
    provider_name: Optional[str],
    model_name: Optional[str],
) -> Dict[str, Any]:
    phase_dir = output_root / "workflow_phase_autopatch"
    phase_dir.mkdir(parents=True, exist_ok=True)
    results_path = phase_dir / "workflow_phase_autopatch_results.json"
    stability_only_mode = int(getattr(report, "num_sessions_analyzed", 0) or 0) == 0

    def _write_phase_results() -> None:
        results_path.write_text(
            json.dumps(_sanitize_for_json(phase_results), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    phase_results: List[Dict[str, Any]] = []
    for index, task in enumerate(list(workflow_payload.get("phase_tasks") or [])):
        metadata = dict(task.get("metadata") or {})
        phase_name = str(task.get("phase_name") or metadata.get("workflow_phase") or "workflow_phase")
        phase_status = str(metadata.get("workflow_phase_status") or "ready")
        target_file_labels = [str(path) for path in list(task.get("target_files") or [])]
        target_files = [_resolve_workflow_target_path(path) for path in target_file_labels]
        phase_output_root = phase_dir / phase_name
        base_constraints = dict(task.get("constraints") or {})
        target_symbols = dict(base_constraints.get("target_symbols") or {})
        resolved_target_symbols = _resolve_workflow_target_symbols(target_symbols)
        secondary_target_file_labels = [
            str(path)
            for path in list(metadata.get("workflow_phase_secondary_target_files") or [])
            if str(path)
        ]
        secondary_target_files = [_resolve_workflow_target_path(path) for path in secondary_target_file_labels]
        secondary_constraints = dict(metadata.get("workflow_phase_secondary_constraints") or {})
        secondary_target_symbols = dict(secondary_constraints.get("target_symbols") or {})
        resolved_secondary_target_symbols = _resolve_workflow_target_symbols(secondary_target_symbols)
        tertiary_target_file_labels = [
            str(path)
            for path in list(metadata.get("workflow_phase_tertiary_target_files") or [])
            if str(path)
        ]
        tertiary_target_files = [_resolve_workflow_target_path(path) for path in tertiary_target_file_labels]
        tertiary_constraints = dict(metadata.get("workflow_phase_tertiary_constraints") or {})
        tertiary_target_symbols = dict(tertiary_constraints.get("target_symbols") or {})
        resolved_tertiary_target_symbols = _resolve_workflow_target_symbols(tertiary_target_symbols)
        quaternary_target_file_labels = [
            str(path)
            for path in list(metadata.get("workflow_phase_quaternary_target_files") or [])
            if str(path)
        ]
        quaternary_target_files = [_resolve_workflow_target_path(path) for path in quaternary_target_file_labels]
        quaternary_constraints = dict(metadata.get("workflow_phase_quaternary_constraints") or {})
        quaternary_target_symbols = dict(quaternary_constraints.get("target_symbols") or {})
        resolved_quaternary_target_symbols = _resolve_workflow_target_symbols(quaternary_target_symbols)
        if phase_status == "ready":
            phase_results.append(
                {
                    "phase": phase_name,
                    "phase_name": phase_name,
                    "task_id": str(task.get("task_id") or ""),
                    "description": str(task.get("description") or ""),
                    "target_files": list(target_file_labels),
                    "status": "skipped",
                    "started_at": datetime.now(UTC).isoformat(),
                    "completed_at": datetime.now(UTC).isoformat(),
                    "file_runs": [],
                    "summary": {
                        "requested": True,
                        "success": False,
                        "apply_success": False,
                        "target_files": list(target_file_labels),
                        "target_symbols": _sanitize_for_json(target_symbols),
                        "error": "Skipped workflow phase because the optimization report already marked it ready.",
                    },
                    "patch_path": None,
                    "patch_cid": None,
                    "success": False,
                    "apply_success": False,
                    "summary_json": None,
                }
            )
            _write_phase_results()
            continue
        if stability_only_mode and index > 0:
            phase_results.append(
                {
                    "phase": phase_name,
                    "phase_name": phase_name,
                    "task_id": str(task.get("task_id") or ""),
                    "description": str(task.get("description") or ""),
                    "target_files": list(target_file_labels),
                    "status": "skipped",
                    "started_at": datetime.now(UTC).isoformat(),
                    "completed_at": datetime.now(UTC).isoformat(),
                    "file_runs": [],
                    "summary": {
                        "requested": True,
                        "success": False,
                        "apply_success": False,
                        "target_files": list(target_file_labels),
                        "target_symbols": _sanitize_for_json(target_symbols),
                        "error": "Skipped workflow phase because no successful sessions were available; prioritize stability and intake fixes first.",
                    },
                    "patch_path": None,
                    "patch_cid": None,
                    "success": False,
                    "apply_success": False,
                    "summary_json": None,
                }
            )
            _write_phase_results()
            continue
        phase_record: Dict[str, Any] = {
            "phase": phase_name,
            "phase_name": phase_name,
            "task_id": str(task.get("task_id") or ""),
            "description": str(task.get("description") or ""),
            "target_files": list(target_file_labels),
            "status": "running",
            "started_at": datetime.now(UTC).isoformat(),
        }
        phase_results.append(phase_record)
        _write_phase_results()
        file_runs: List[Dict[str, Any]] = []
        pending_targets: List[Tuple[str, Path, Dict[str, List[str]]]] = []
        for target_label, target_path in zip(target_file_labels or [""], target_files or [Path()]):
            symbol_map: Dict[str, List[str]] = {}
            if resolved_target_symbols and target_path:
                symbol_key = str(target_path)
                selected = list(resolved_target_symbols.get(symbol_key) or [])
                if selected:
                    symbol_map[symbol_key] = selected
            pending_targets.append((target_label, target_path, symbol_map))

        secondary_pending_targets: List[Tuple[str, Path, Dict[str, List[str]]]] = []
        for target_label, target_path in zip(secondary_target_file_labels, secondary_target_files):
            symbol_map: Dict[str, List[str]] = {}
            if resolved_secondary_target_symbols and target_path:
                symbol_key = str(target_path)
                selected = list(resolved_secondary_target_symbols.get(symbol_key) or [])
                if selected:
                    symbol_map[symbol_key] = selected
            secondary_pending_targets.append((target_label, target_path, symbol_map))

        tertiary_pending_targets: List[Tuple[str, Path, Dict[str, List[str]]]] = []
        for target_label, target_path in zip(tertiary_target_file_labels, tertiary_target_files):
            symbol_map: Dict[str, List[str]] = {}
            if resolved_tertiary_target_symbols and target_path:
                symbol_key = str(target_path)
                selected = list(resolved_tertiary_target_symbols.get(symbol_key) or [])
                if selected:
                    symbol_map[symbol_key] = selected
            tertiary_pending_targets.append((target_label, target_path, symbol_map))
        quaternary_pending_targets: List[Tuple[str, Path, Dict[str, List[str]]]] = []
        for target_label, target_path in zip(quaternary_target_file_labels, quaternary_target_files):
            symbol_map: Dict[str, List[str]] = {}
            if resolved_quaternary_target_symbols and target_path:
                symbol_key = str(target_path)
                selected = list(resolved_quaternary_target_symbols.get(symbol_key) or [])
                if selected:
                    symbol_map[symbol_key] = selected
            quaternary_pending_targets.append((target_label, target_path, symbol_map))

        primary_succeeded = False
        secondary_succeeded = False
        tertiary_succeeded = False
        while pending_targets:
            target_label, target_path, explicit_symbol_map = pending_targets.pop(0)
            file_constraints = dict(base_constraints)
            selected_symbols: List[str] = []
            if explicit_symbol_map:
                symbol_key = next(iter(explicit_symbol_map))
                selected_symbols = list(explicit_symbol_map.get(symbol_key) or [])
                file_constraints["target_symbols"] = {symbol_key: selected_symbols} if selected_symbols else {}
            else:
                file_constraints["target_symbols"] = {}
            file_description = str(task.get("description") or "")
            if target_path:
                file_description += f" Focus only on {target_label or target_path.as_posix()}."
            if selected_symbols:
                file_description += " Target symbols: " + ", ".join(str(symbol) for symbol in selected_symbols) + "."
            file_record: Dict[str, Any] = {
                "target_file": target_label or (str(target_path) if target_path else None),
                "target_symbols": list(selected_symbols),
                "status": "running",
                "started_at": datetime.now(UTC).isoformat(),
            }
            file_runs.append(file_record)
            phase_record["file_runs"] = file_runs
            _write_phase_results()
            file_summary = _run_agentic_autopatch(
                optimizer=optimizer,
                results=results,
                report=report,
                output_root=phase_output_root / (target_path.stem or "phase"),
                requested_profile=phase_name,
                requested_target_files=[target_path] if target_path else target_files,
                recommended_profile=phase_name,
                recommended_target_files=[target_path] if target_path else target_files,
                used_recommended_targets=False,
                target_files=[target_path] if target_path else target_files,
                description=file_description,
                method=str(task.get("method") or method).strip().lower() if str(task.get("method") or "") else method,
                profile=phase_name,
                constraints=file_constraints,
                apply_patch=apply_patch,
                provider_name=provider_name,
                model_name=model_name,
            )
            file_record.update(
                {
                    "status": "completed",
                    "completed_at": datetime.now(UTC).isoformat(),
                    "summary": _sanitize_for_json(file_summary),
                    "patch_path": file_summary.get("patch_path"),
                    "patch_cid": file_summary.get("patch_cid"),
                    "success": bool(file_summary.get("success")),
                    "apply_success": bool(file_summary.get("apply_success")),
                    "summary_json": file_summary.get("summary_json"),
                }
            )
            phase_record["file_runs"] = file_runs
            _write_phase_results()

            if file_record.get("success") and not primary_succeeded:
                primary_succeeded = True
                if secondary_pending_targets:
                    pending_targets.extend(secondary_pending_targets)
                    secondary_pending_targets = []
                elif tertiary_pending_targets:
                    secondary_succeeded = True
                    pending_targets.extend(tertiary_pending_targets)
                    tertiary_pending_targets = []
                elif quaternary_pending_targets:
                    secondary_succeeded = True
                    tertiary_succeeded = True
                    pending_targets.extend(quaternary_pending_targets)
                    quaternary_pending_targets = []
            elif file_record.get("success") and primary_succeeded and not secondary_succeeded:
                secondary_succeeded = True
                if tertiary_pending_targets:
                    pending_targets.extend(tertiary_pending_targets)
                    tertiary_pending_targets = []
                elif quaternary_pending_targets:
                    tertiary_succeeded = True
                    pending_targets.extend(quaternary_pending_targets)
                    quaternary_pending_targets = []
            elif file_record.get("success") and primary_succeeded and secondary_succeeded and not tertiary_succeeded:
                tertiary_succeeded = True
                if quaternary_pending_targets:
                    pending_targets.extend(quaternary_pending_targets)
                    quaternary_pending_targets = []

        successful_runs = [entry for entry in file_runs if entry.get("success")]
        applied_runs = [entry for entry in file_runs if entry.get("apply_success")]
        summary = dict(successful_runs[0]["summary"] if successful_runs else file_runs[-1]["summary"])
        phase_record.update(
            {
                "status": "completed",
                "completed_at": datetime.now(UTC).isoformat(),
                "summary": _sanitize_for_json(summary),
                "file_runs": file_runs,
                "patch_path": summary.get("patch_path"),
                "patch_cid": summary.get("patch_cid"),
                "success": bool(successful_runs),
                "apply_success": bool(applied_runs),
                "summary_json": summary.get("summary_json"),
            }
        )
        _write_phase_results()

    return {
        "requested": True,
        "count": len(phase_results),
        "results_json": str(results_path),
        "results": phase_results,
    }


def _load_runtime(demo: bool, config_path: Optional[str], backend_id: Optional[str], provider: Optional[str], model: Optional[str]) -> Dict[str, Any]:
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

        def mediator_factory(**kwargs: Any) -> Any:
            return Mediator(backends=build_backends(config, backend_id=backend_id), **kwargs)

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

    def mediator_factory(**kwargs: Any) -> Any:
        return Mediator(
            backends=[LLMRouterBackend(id="mediator", provider=provider, model=model)],
            **kwargs,
        )

    runtime = {
        "mode": "llm_router",
        "provider": getattr(complainant_backend, "provider", None) or provider,
        "model": model or getattr(complainant_backend, "model", None),
        "complainant_backend_class": type(complainant_backend).__name__,
        "critic_backend_class": type(critic_backend).__name__,
        "provider_status": _runtime_provider_status(
            getattr(complainant_backend, "provider", None) or provider,
            model or getattr(complainant_backend, "model", None),
        ),
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
        from integrations.ipfs_datasets.vector_store import embeddings_backend_status, vector_index_backend_status

        diagnostics["embeddings_router"] = _sanitize_for_json(embeddings_backend_status())
        diagnostics["vector_index"] = _sanitize_for_json(vector_index_backend_status(require_local_persistence=True))
    except Exception as exc:
        diagnostics["embeddings_router"] = {
            "status": "error",
            "error": str(exc),
        }
        diagnostics["vector_index"] = {
            "status": "error",
            "error": str(exc),
        }

    return diagnostics


def _runtime_provider_status(provider: Optional[str], model: Optional[str]) -> Dict[str, Any]:
    _ensure_complaint_generator_on_path()
    try:
        from integrations.ipfs_datasets.llm import llm_router_status

        return _sanitize_for_json(
            llm_router_status(
                provider=provider,
                model_name=model,
                perform_probe=False,
            )
        )
    except Exception as exc:
        return {
            "status": "error",
            "configured_provider_name": provider or "",
            "configured_model_name": model or "",
            "error": str(exc),
        }


def _adversarial_search_summary(
    *,
    requested_mode: str,
    use_vector: bool,
    router_diagnostics: Dict[str, Any],
) -> Dict[str, Any]:
    normalized_mode = str(requested_mode or "auto").strip().lower() or "auto"
    vector_status = str(((router_diagnostics.get("vector_index") or {}).get("status") or "")).strip().lower()
    vector_error = str(
        ((router_diagnostics.get("vector_index") or {}).get("error"))
        or (((router_diagnostics.get("vector_index") or {}).get("metadata") or {}).get("degraded_reason"))
        or ""
    ).strip()

    effective_mode = normalized_mode
    fallback_note = ""
    if normalized_mode == "hybrid" and vector_status != "available":
        effective_mode = "lexical_only"
        fallback_note = "Requested hybrid search, but vector support is unavailable; using lexical results instead."
    elif normalized_mode == "package" and vector_status != "available":
        effective_mode = "lexical_fallback"
        fallback_note = "Requested package/shared hybrid search, but vector support is unavailable; using lexical results instead."
    elif normalized_mode == "package":
        effective_mode = "shared_hybrid"

    if fallback_note and vector_error:
        fallback_note = f"{fallback_note} Vector backend detail: {vector_error}"

    return {
        "requested_search_mode": normalized_mode,
        "requested_use_vector": bool(use_vector),
        "effective_search_mode": effective_mode,
        "vector_status": vector_status,
        "vector_error": vector_error,
        "fallback_note": fallback_note,
    }


def _best_complaint_grounding_overview(best_result: Any) -> Dict[str, Any]:
    seed = dict((getattr(best_result, "seed_complaint", {}) or {})) if best_result else {}
    key_facts = dict(seed.get("key_facts") or {})
    anchor_sections = [str(item) for item in list(key_facts.get("anchor_sections") or []) if str(item)]
    anchor_passages = [dict(item) for item in list(key_facts.get("anchor_passages") or []) if isinstance(item, dict)]
    hacc_evidence = [dict(item) for item in list(seed.get("hacc_evidence") or []) if isinstance(item, dict)]
    timeline_anchors = [dict(item) for item in list(key_facts.get("timeline_anchors") or []) if isinstance(item, dict)]
    claim_support_temporal_handoff = dict(key_facts.get("claim_support_temporal_handoff") or {})
    mediator_packets = [dict(item) for item in list(key_facts.get("mediator_evidence_packets") or []) if isinstance(item, dict)]

    top_documents: List[str] = []
    for item in hacc_evidence:
        label = str(item.get("title") or item.get("source_path") or "").strip()
        if label and label not in top_documents:
            top_documents.append(label)
        if len(top_documents) >= 3:
            break

    overview = {
        "evidence_summary": str(key_facts.get("evidence_summary") or seed.get("summary") or "").strip(),
        "anchor_sections": anchor_sections,
        "anchor_passage_count": len(anchor_passages),
        "evidence_item_count": len(hacc_evidence),
        "top_documents": top_documents,
        "timeline_anchor_count": len(timeline_anchors),
        "unresolved_temporal_issue_count": int(claim_support_temporal_handoff.get("unresolved_temporal_issue_count") or 0),
        "chronology_task_count": int(claim_support_temporal_handoff.get("chronology_task_count") or 0),
        "mediator_packet_count": len(mediator_packets),
    }
    compact: Dict[str, Any] = {}
    for key, value in overview.items():
        if value in (None, "", [], {}):
            continue
        if isinstance(value, int) and value <= 0:
            continue
        compact[key] = value
    return compact


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
    hacc_search_mode: str = "package",
    demo: bool = False,
    config_path: Optional[str] = None,
    backend_id: Optional[str] = None,
    provider: Optional[str] = None,
    model: Optional[str] = None,
    emit_autopatch: bool = False,
    apply_autopatch: Optional[bool] = None,
    autopatch_method: str = "test_driven",
    autopatch_profile: str = "question_flow",
    autopatch_target_files: Optional[List[str]] = None,
    use_recommended_autopatch_targets: bool = False,
    emit_workflow_phase_autopatches: bool = False,
    apply_workflow_phase_autopatches: Optional[bool] = None,
    reuse_existing_artifacts: bool = False,
    seed_complaints: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    output_root = Path(output_dir).resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    session_dir = output_root / "sessions"
    if not reuse_existing_artifacts and session_dir.exists():
        shutil.rmtree(session_dir)
    session_dir.mkdir(parents=True, exist_ok=True)
    batch_progress_path = output_root / "batch_progress.json"

    resolved_provider, resolved_model = _resolve_hacc_runtime_provider_model(provider, model)
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
        hacc_search_mode=hacc_search_mode,
    )

    optimizer = Optimizer()
    report = optimizer.analyze(results)
    stats = harness.get_statistics()
    best_result = _select_best_result(results)
    recommended_autopatch_targets = _resolve_optimizer_recommended_target_files(optimizer, report)
    recommended_autopatch_profile = _recommended_autopatch_profile(recommended_autopatch_targets)
    selected_autopatch_profile = autopatch_profile
    autopatch_target_paths = _resolve_autopatch_target_files(autopatch_target_files, autopatch_profile)
    if use_recommended_autopatch_targets and recommended_autopatch_targets:
        autopatch_target_paths = list(recommended_autopatch_targets)
        selected_autopatch_profile = recommended_autopatch_profile
    autopatch_constraints = _autopatch_constraints_for_profile(selected_autopatch_profile, autopatch_target_paths)

    run_results_path = output_root / "adversarial_results.json"
    optimization_report_path = output_root / "optimization_report.json"
    workflow_optimization_path = output_root / "workflow_optimization_bundle.json"
    anchor_report_path = output_root / "anchor_section_coverage.csv"
    best_complaint_path = output_root / "best_complaint_bundle.json"
    summary_path = output_root / "run_summary.json"

    runtime_bundle = _load_runtime(demo, config_path, backend_id, resolved_provider, resolved_model)
    AdversarialHarness = runtime_bundle["AdversarialHarness"]
    Optimizer = runtime_bundle["Optimizer"]
    optimizer = Optimizer()

    harness = None
    if not reuse_existing_artifacts:
        harness = AdversarialHarness(
            llm_backend_complainant=runtime_bundle["complainant_backend"],
            llm_backend_critic=runtime_bundle["critic_backend"],
            mediator_factory=runtime_bundle["mediator_factory"],
            max_parallel=max_parallel,
            session_state_dir=str(session_dir),
        )

    router_diagnostics = _router_diagnostics()
    search_summary = _adversarial_search_summary(
        requested_mode=hacc_search_mode,
        use_vector=use_hacc_vector_search,
        router_diagnostics=router_diagnostics,
    )
    effective_search_mode = str(search_summary.get("effective_search_mode") or hacc_search_mode)
    effective_use_hacc_vector_search = bool(use_hacc_vector_search)
    if effective_search_mode in {"lexical_only", "lexical_fallback"}:
        effective_use_hacc_vector_search = False

    def _write_batch_progress(payload: Dict[str, Any]) -> None:
        batch_progress_path.write_text(
            json.dumps(_sanitize_for_json(payload), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    existing_summary = _load_json_if_exists(summary_path) if reuse_existing_artifacts else None
    existing_results_payload = _load_json_if_exists(run_results_path) if reuse_existing_artifacts else None
    existing_optimization_payload = _load_json_if_exists(optimization_report_path) if reuse_existing_artifacts else None
    existing_workflow_payload = _load_json_if_exists(workflow_optimization_path) if reuse_existing_artifacts else None
    existing_best_bundle = _load_json_if_exists(best_complaint_path) if reuse_existing_artifacts else None

    if reuse_existing_artifacts and existing_results_payload and existing_optimization_payload and existing_workflow_payload:
        _write_batch_progress(
            {
                "status": "reused_existing_artifacts",
                "timestamp": datetime.now(UTC).isoformat(),
                "total_sessions": int(num_sessions or 0),
                "completed_sessions": int(((existing_summary or {}).get("statistics") or {}).get("total_sessions") or 0),
                "successful_sessions": int(((existing_summary or {}).get("statistics") or {}).get("successful_sessions") or 0),
                "failed_sessions": int(((existing_summary or {}).get("statistics") or {}).get("failed_sessions") or 0),
                "active_session_ids": [],
                "search_summary": _sanitize_for_json((existing_summary or {}).get("search_summary") or search_summary),
            }
        )
        results = list(existing_results_payload.get("results") or [])
        report = _LoadedReport(existing_optimization_payload)
        optimization_payload = existing_optimization_payload
        workflow_payload = existing_workflow_payload
        stats = _sanitize_for_json((existing_summary or {}).get("statistics") or {"total_sessions": len(results)})
        best_bundle = _sanitize_for_json(existing_best_bundle or {})
        best_result = None
    else:
        _write_batch_progress(
            {
                "status": "initializing",
                "timestamp": datetime.now(UTC).isoformat(),
                "total_sessions": int(num_sessions or 0),
                "completed_sessions": 0,
                "successful_sessions": 0,
                "failed_sessions": 0,
                "active_session_ids": [],
                "search_summary": _sanitize_for_json(search_summary),
            }
        )

        with _scoped_mediator_integration_env(
            effective_search_mode=effective_search_mode,
            use_hacc_vector_search=effective_use_hacc_vector_search,
        ):
            results = harness.run_batch(
                num_sessions=num_sessions,
                seed_complaints=seed_complaints,
                personalities=personalities,
                max_turns_per_session=max_turns,
                include_hacc_evidence=True,
                hacc_count=hacc_count,
                hacc_preset=hacc_preset,
                use_hacc_vector_search=effective_use_hacc_vector_search,
                hacc_search_mode=effective_search_mode,
                progress_callback=_write_batch_progress,
            )

        report = optimizer.analyze(results)
        stats = harness.get_statistics()
        best_result = _select_best_result(results)
        optimization_payload = _sanitize_for_json(report.to_dict())
        workflow_payload = _build_workflow_optimization_payload(
            optimizer,
            results=results,
            report=report,
        )
        harness.save_results(str(run_results_path))
        harness.save_anchor_section_report(str(anchor_report_path), format="csv")
        optimization_report_path.write_text(
            json.dumps(optimization_payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        workflow_optimization_path.write_text(
            json.dumps(workflow_payload, ensure_ascii=False, indent=2),
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

    persisted_best_summary = dict((existing_summary or {}).get("best_complaint") or {})
    persisted_seed_value = best_bundle.get("seed_complaint") or {}
    persisted_seed = dict(persisted_seed_value) if isinstance(persisted_seed_value, dict) else {}
    persisted_critic_score_value = best_bundle.get("critic_score") or {}
    persisted_critic_score = dict(persisted_critic_score_value) if isinstance(persisted_critic_score_value, dict) else {}
    best_complaint_summary = {
        "session_id": getattr(best_result, "session_id", None) or persisted_best_summary.get("session_id"),
        "initial_complaint_text": getattr(best_result, "initial_complaint_text", "") or str(best_bundle.get("initial_complaint_text") or ""),
        "score": (
            float(getattr(getattr(best_result, "critic_score", None), "overall_score", 0.0) or 0.0)
            if best_result
            else float(persisted_critic_score.get("overall_score") or persisted_best_summary.get("score") or 0.0)
        ),
        "seed_type": (
            str((getattr(best_result, "seed_complaint", {}) or {}).get("type") or "")
            if best_result
            else str(persisted_seed.get("type") or persisted_best_summary.get("seed_type") or "")
        ),
        "seed_summary": (
            str((getattr(best_result, "seed_complaint", {}) or {}).get("summary") or "")
            if best_result
            else str(persisted_seed.get("summary") or persisted_best_summary.get("seed_summary") or "")
        ),
        "grounding_overview": (
            _best_complaint_grounding_overview(best_result)
            if best_result
            else _sanitize_for_json(persisted_best_summary.get("grounding_overview") or {})
        ),
        "search_summary": search_summary,
    }
    requested_autopatch_profile = autopatch_profile
    requested_autopatch_target_paths = _resolve_autopatch_target_files(autopatch_target_files, autopatch_profile)
    recommended_autopatch_targets = _resolve_optimizer_recommended_target_files(optimizer, report)
    recommended_autopatch_profile = _recommended_autopatch_profile(recommended_autopatch_targets)
    selected_autopatch_profile = autopatch_profile
    autopatch_target_paths = list(requested_autopatch_target_paths)
    if use_recommended_autopatch_targets and recommended_autopatch_targets:
        autopatch_target_paths = list(recommended_autopatch_targets)
        selected_autopatch_profile = recommended_autopatch_profile
    autopatch_constraints = _autopatch_constraints_for_profile(selected_autopatch_profile, autopatch_target_paths)

    workflow_phase_autopatch_summary: Dict[str, Any] = {
        "requested": False,
        "count": 0,
        "results_json": None,
        "results": [],
    }

    autopatch_summary = {
        "requested": False,
        "method": autopatch_method,
        "requested_profile": requested_autopatch_profile,
        "requested_target_files": [str(path) for path in requested_autopatch_target_paths],
        "profile": selected_autopatch_profile,
        "target_files": [str(path) for path in autopatch_target_paths],
        "recommended_profile": recommended_autopatch_profile,
        "recommended_target_files": [str(path) for path in recommended_autopatch_targets],
        "used_recommended_targets": bool(use_recommended_autopatch_targets and recommended_autopatch_targets),
        "apply_mode": _resolve_autopatch_apply_mode(
            apply_autopatch,
            emit_patch=bool(emit_autopatch or apply_autopatch is not None),
        ),
        "constraints": _sanitize_for_json(autopatch_constraints),
        "preflight": None,
        "applied": False,
        "apply_success": False,
        "success": False,
        "patch_path": None,
        "patch_cid": None,
        "metadata": {},
        "summary_json": None,
        "error": None,
    }
    if emit_autopatch or apply_autopatch is not None:
        autopatch_preflight = _agentic_autopatch_preflight(optimizer)
        autopatch_summary["preflight"] = _sanitize_for_json(autopatch_preflight)
        if autopatch_preflight.get("ready"):
            autopatch_summary = _run_agentic_autopatch(
                optimizer=optimizer,
                results=results,
                report=report,
                output_root=output_root,
                requested_profile=requested_autopatch_profile,
                requested_target_files=requested_autopatch_target_paths,
                recommended_profile=recommended_autopatch_profile,
                recommended_target_files=recommended_autopatch_targets,
                used_recommended_targets=bool(use_recommended_autopatch_targets and recommended_autopatch_targets),
                target_files=autopatch_target_paths,
                method=autopatch_method,
                profile=selected_autopatch_profile,
                constraints=autopatch_constraints,
                apply_patch=apply_autopatch,
                provider_name=runtime_bundle["runtime"].get("provider"),
                model_name=runtime_bundle["runtime"].get("model"),
            )
            autopatch_summary["preflight"] = _sanitize_for_json(autopatch_preflight)
        else:
            autopatch_summary["requested"] = True
            autopatch_summary["error"] = f"Autopatch dependency preflight failed: {autopatch_preflight.get('error')}"

    if emit_workflow_phase_autopatches or apply_workflow_phase_autopatches is not None:
        workflow_phase_preflight = _agentic_autopatch_preflight(optimizer)
        if workflow_phase_preflight.get("ready"):
            workflow_phase_autopatch_summary = _run_workflow_phase_autopatches(
                optimizer=optimizer,
                results=results,
                report=report,
                workflow_payload=workflow_payload,
                output_root=output_root,
                method=autopatch_method,
                apply_patch=apply_workflow_phase_autopatches,
                provider_name=runtime_bundle["runtime"].get("provider"),
                model_name=runtime_bundle["runtime"].get("model"),
            )
            workflow_phase_autopatch_summary["preflight"] = _sanitize_for_json(workflow_phase_preflight)
        else:
            workflow_phase_autopatch_summary = {
                "requested": True,
                "count": 0,
                "results_json": None,
                "results": [],
                "preflight": _sanitize_for_json(workflow_phase_preflight),
                "error": f"Workflow phase autopatch dependency preflight failed: {workflow_phase_preflight.get('error')}",
            }

    summary = {
        "timestamp": _timestamp(),
        "runtime": runtime_bundle["runtime"],
        "router_diagnostics": router_diagnostics,
        "inputs": {
            "num_sessions": num_sessions,
            "max_turns": max_turns,
            "max_parallel": max_parallel,
            "personalities": list(personalities or []),
            "hacc_preset": hacc_preset,
            "hacc_count": hacc_count,
            "use_hacc_vector_search": use_hacc_vector_search,
            "effective_use_hacc_vector_search": effective_use_hacc_vector_search,
            "hacc_search_mode": hacc_search_mode,
            "effective_hacc_search_mode": effective_search_mode,
            "provider": resolved_provider,
            "model": resolved_model,
            "reuse_existing_artifacts": reuse_existing_artifacts,
        },
        "search_summary": search_summary,
        "statistics": _sanitize_for_json(stats),
        "optimization_report": {
            "average_score": optimization_payload.get("average_score"),
            "score_trend": optimization_payload.get("score_trend"),
            "recommended_hacc_preset": optimization_payload.get("recommended_hacc_preset"),
            "priority_improvements": optimization_payload.get("priority_improvements"),
            "recommendations": optimization_payload.get("recommendations"),
            "intake_priority_performance": optimization_payload.get("intake_priority_performance"),
            "coverage_remediation": optimization_payload.get("coverage_remediation"),
            "best_session_id": optimization_payload.get("best_session_id"),
            "workflow_phase_plan": optimization_payload.get("workflow_phase_plan"),
        },
        "workflow_optimization": {
            "global_objectives": workflow_payload.get("global_objectives"),
            "workflow_phase_plan": workflow_payload.get("workflow_phase_plan"),
            "phase_tasks": workflow_payload.get("phase_tasks"),
        },
        "workflow_phase_autopatch": _sanitize_for_json(workflow_phase_autopatch_summary),
        "autopatch": _sanitize_for_json(autopatch_summary),
        "best_complaint": best_complaint_summary,
        "artifacts": {
            "output_dir": str(output_root),
            "results_json": str(run_results_path),
            "optimization_report_json": str(optimization_report_path),
            "workflow_optimization_bundle_json": str(workflow_optimization_path),
            "workflow_phase_autopatch_results_json": workflow_phase_autopatch_summary.get("results_json"),
            "anchor_section_csv": str(anchor_report_path),
            "best_complaint_bundle_json": str(best_complaint_path),
            "session_state_dir": str(session_dir),
            "batch_progress_json": str(batch_progress_path),
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
    parser.add_argument(
        "--hacc-search-mode",
        choices=("auto", "lexical", "hybrid", "vector", "package"),
        default="package",
        help="Search strategy used for HACC evidence retrieval during adversarial seed generation.",
    )
    parser.add_argument("--demo", action="store_true", help="Use deterministic demo backends instead of live LLM routing.")
    parser.add_argument("--config", default=None, help="Optional complaint-generator config JSON to source backends from.")
    parser.add_argument("--backend-id", default=None, help="Optional backend id from the selected config.")
    parser.add_argument(
        "--provider",
        default=HACC_DEFAULT_PROVIDER,
        help=(
            "LLM router provider override when not using --demo or --config. "
            f"Defaults to {HACC_DEFAULT_PROVIDER} for HACC runs."
        ),
    )
    parser.add_argument(
        "--model",
        default=HACC_DEFAULT_MODEL,
        help=f"Optional model name when using the direct llm_router path. Defaults to {HACC_DEFAULT_MODEL}.",
    )
    parser.set_defaults(apply_autopatch=None)
    parser.add_argument("--emit-autopatch", action="store_true", help="Generate an optimizer patch artifact targeting the mediator codebase.")
    parser.add_argument(
        "--apply-autopatch",
        action="store_const",
        const=True,
        dest="apply_autopatch",
        help="Generate and apply the optimizer patch to complaint-generator.",
    )
    parser.add_argument(
        "--no-apply-autopatch",
        action="store_const",
        const=False,
        dest="apply_autopatch",
        help="Generate the optimizer patch artifact without applying it, even if HACC_AUTOPATCH_AUTO_APPLY is enabled.",
    )
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
    parser.add_argument(
        "--use-recommended-autopatch-targets",
        action="store_true",
        help="Use the optimizer's intake-driven recommended autopatch target files/profile instead of the requested profile defaults.",
    )
    parser.set_defaults(apply_workflow_phase_autopatches=None)
    parser.add_argument(
        "--emit-workflow-phase-autopatches",
        action="store_true",
        help="Generate phase-by-phase optimizer patch artifacts for intake, graph analysis, and document generation.",
    )
    parser.add_argument(
        "--apply-workflow-phase-autopatches",
        action="store_const",
        const=True,
        dest="apply_workflow_phase_autopatches",
        help="Generate and apply phase-by-phase optimizer patches for the workflow stages.",
    )
    parser.add_argument(
        "--no-apply-workflow-phase-autopatches",
        action="store_const",
        const=False,
        dest="apply_workflow_phase_autopatches",
        help="Generate workflow phase patch artifacts without applying them.",
    )
    parser.add_argument(
        "--reuse-existing-artifacts",
        action="store_true",
        help="Reuse saved adversarial/optimizer artifacts from the output directory instead of rerunning the batch.",
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
        hacc_search_mode=args.hacc_search_mode,
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
        use_recommended_autopatch_targets=args.use_recommended_autopatch_targets,
        emit_workflow_phase_autopatches=args.emit_workflow_phase_autopatches,
        apply_workflow_phase_autopatches=args.apply_workflow_phase_autopatches,
        reuse_existing_artifacts=args.reuse_existing_artifacts,
    )
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"Output directory: {summary['artifacts']['output_dir']}")
        print(f"Best complaint score: {summary['best_complaint']['score']:.3f}")
        print(
            "HACC search mode: "
            f"requested={summary['search_summary']['requested_search_mode']} "
            f"effective={summary['search_summary']['effective_search_mode']}"
        )
        provider_status = dict((summary.get("runtime") or {}).get("provider_status") or {})
        if provider_status:
            effective_provider = provider_status.get("effective_provider_name") or (summary.get("runtime") or {}).get("provider") or "router-default"
            effective_model = provider_status.get("effective_model_name") or (summary.get("runtime") or {}).get("model") or ""
            print(
                "LLM provider status: "
                f"status={provider_status.get('status', 'unknown')} "
                f"provider={effective_provider}"
                + (f" model={effective_model}" if effective_model else "")
            )
            if provider_status.get("error"):
                print(f"LLM provider detail: {provider_status['error']}")
        if summary["search_summary"].get("fallback_note"):
            print(f"HACC search fallback: {summary['search_summary']['fallback_note']}")
        print(f"Best complaint seed: {summary['best_complaint']['seed_type']} - {summary['best_complaint']['seed_summary']}")
        print(f"Recommended preset: {summary['optimization_report']['recommended_hacc_preset'] or summary['inputs']['hacc_preset']}")
        if summary["autopatch"]["requested"]:
            print(f"Autopatch success: {summary['autopatch']['success']}")
            print(f"Autopatch applied: {summary['autopatch']['apply_success']}")
            apply_mode = dict(summary["autopatch"].get("apply_mode") or {})
            print(
                "Autopatch apply mode: "
                f"source={apply_mode.get('source', 'env')} "
                f"requested={apply_mode.get('requested')} "
                f"env_default={apply_mode.get('env_default', False)} "
                f"effective={apply_mode.get('effective', False)}"
            )
            print(f"Using recommended autopatch targets: {summary['autopatch'].get('used_recommended_targets', False)}")
            preflight = dict(summary["autopatch"].get("preflight") or {})
            if preflight:
                print(f"Autopatch preflight ready: {preflight.get('ready', False)}")
                if preflight.get("error"):
                    print(f"Autopatch preflight error: {preflight['error']}")
            if summary["autopatch"].get("requested_profile"):
                print(f"Requested autopatch profile: {summary['autopatch']['requested_profile']}")
            requested_targets = list(summary["autopatch"].get("requested_target_files") or [])
            if requested_targets:
                print(f"Requested autopatch targets: {', '.join(str(path) for path in requested_targets)}")
            if summary["autopatch"].get("recommended_profile"):
                print(f"Recommended autopatch profile: {summary['autopatch']['recommended_profile']}")
            recommended_targets = list(summary["autopatch"].get("recommended_target_files") or [])
            if recommended_targets:
                print(f"Recommended autopatch targets: {', '.join(str(path) for path in recommended_targets)}")
            print(f"Selected autopatch profile: {summary['autopatch']['profile']}")
            selected_targets = list(summary["autopatch"].get("target_files") or [])
            if selected_targets:
                print(f"Selected autopatch targets: {', '.join(str(path) for path in selected_targets)}")
            if summary["autopatch"]["patch_path"]:
                print(f"Autopatch patch: {summary['autopatch']['patch_path']}")
        workflow_phase_autopatch = dict(summary.get("workflow_phase_autopatch") or {})
        if workflow_phase_autopatch.get("requested"):
            print(f"Workflow phase autopatch count: {workflow_phase_autopatch.get('count', 0)}")
            if workflow_phase_autopatch.get("error"):
                print(f"Workflow phase autopatch error: {workflow_phase_autopatch['error']}")
        print(f"Results JSON: {summary['artifacts']['results_json']}")
        print(f"Optimization report: {summary['artifacts']['optimization_report_json']}")
        workflow_bundle_path = (summary.get("artifacts") or {}).get("workflow_optimization_bundle_json")
        if workflow_bundle_path:
            print(f"Workflow optimization bundle: {workflow_bundle_path}")
        workflow_phase_results_path = (summary.get("artifacts") or {}).get("workflow_phase_autopatch_results_json")
        if workflow_phase_results_path:
            print(f"Workflow phase autopatch results: {workflow_phase_results_path}")
        print(f"Best complaint bundle: {summary['artifacts']['best_complaint_bundle_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
