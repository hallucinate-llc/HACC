#!/usr/bin/env python3
"""Run complaint-generator's adversarial harness against HACC evidence."""

from __future__ import annotations

import argparse
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
        "local": "local",
    }
    resolved_provider = provider_mapping.get(normalized)
    if resolved_provider is None:
        return None

    autopatch_timeout = _resolve_autopatch_timeout(profile=profile, target_files=target_files)

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
            model_name = str(kwargs.pop("model_name", "") or os.environ.get("IPFS_DATASETS_PY_CODEX_MODEL", "")).strip()
            if self.provider == "codex_cli" and not model_name:
                model_name = _default_codex_model()
            if autopatch_timeout is not None:
                kwargs.setdefault("timeout", autopatch_timeout)
            kwargs.setdefault("disable_model_retry", True)
            try:
                return generate_text(
                    prompt=prompt,
                    provider=self.provider,
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
                        provider=self.provider,
                        model_name=fallback_model,
                        max_new_tokens=max_tokens,
                        temperature=temperature,
                        **kwargs,
                    )
                raise

        def get_usage_stats(self) -> Dict[str, Any]:
            return {"provider": self.provider}

    return _PinnedRunnerLLMRouter(resolved_provider)


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
        "repair_attempts": [],
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
            llm_router=_build_agentic_llm_router(
                provider_name,
                profile=profile,
                target_files=target_files,
            ),
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
        optimizer_validation = _sanitize_for_json(getattr(result, "validation", None))
        summary["validation"] = {
            "optimizer_result_validation": optimizer_validation,
            "patch_validation": None,
        }
        result_error = getattr(result, "error_message", None)
        if result_error:
            summary["error"] = str(result_error)

        if summary["patch_path"]:
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

        should_apply_patch = bool(summary["patch_path"]) and (apply_patch or _autopatch_auto_apply_enabled())
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
    provider: str = "copilot_cli",
    model: Optional[str] = None,
    emit_autopatch: bool = False,
    apply_autopatch: bool = False,
    autopatch_method: str = "test_driven",
    autopatch_profile: str = "question_flow",
    autopatch_target_files: Optional[List[str]] = None,
    use_recommended_autopatch_targets: bool = False,
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
        "profile": selected_autopatch_profile,
        "target_files": [str(path) for path in autopatch_target_paths],
        "recommended_profile": recommended_autopatch_profile,
        "recommended_target_files": [str(path) for path in recommended_autopatch_targets],
        "used_recommended_targets": bool(use_recommended_autopatch_targets and recommended_autopatch_targets),
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
            profile=selected_autopatch_profile,
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

    router_diagnostics = _router_diagnostics()
    search_summary = _adversarial_search_summary(
        requested_mode=hacc_search_mode,
        use_vector=use_hacc_vector_search,
        router_diagnostics=router_diagnostics,
    )

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
            "hacc_search_mode": hacc_search_mode,
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
        },
        "autopatch": _sanitize_for_json(autopatch_summary),
        "best_complaint": {
            "session_id": getattr(best_result, "session_id", None),
            "initial_complaint_text": getattr(best_result, "initial_complaint_text", ""),
            "score": float(getattr(getattr(best_result, "critic_score", None), "overall_score", 0.0) or 0.0) if best_result else 0.0,
            "seed_type": str((getattr(best_result, "seed_complaint", {}) or {}).get("type") or "") if best_result else "",
            "seed_summary": str((getattr(best_result, "seed_complaint", {}) or {}).get("summary") or "") if best_result else "",
            "search_summary": search_summary,
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
    parser.add_argument(
        "--hacc-search-mode",
        choices=("auto", "lexical", "hybrid", "vector", "package"),
        default="package",
        help="Search strategy used for HACC evidence retrieval during adversarial seed generation.",
    )
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
    parser.add_argument(
        "--use-recommended-autopatch-targets",
        action="store_true",
        help="Use the optimizer's intake-driven recommended autopatch target files/profile instead of the requested profile defaults.",
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
        if summary["search_summary"].get("fallback_note"):
            print(f"HACC search fallback: {summary['search_summary']['fallback_note']}")
        print(f"Best complaint seed: {summary['best_complaint']['seed_type']} - {summary['best_complaint']['seed_summary']}")
        print(f"Recommended preset: {summary['optimization_report']['recommended_hacc_preset'] or summary['inputs']['hacc_preset']}")
        if summary["autopatch"]["requested"]:
            print(f"Autopatch success: {summary['autopatch']['success']}")
            print(f"Autopatch applied: {summary['autopatch']['apply_success']}")
            print(f"Using recommended autopatch targets: {summary['autopatch'].get('used_recommended_targets', False)}")
            if summary["autopatch"].get("recommended_profile"):
                print(f"Recommended autopatch profile: {summary['autopatch']['recommended_profile']}")
            recommended_targets = list(summary["autopatch"].get("recommended_target_files") or [])
            if recommended_targets:
                print(f"Recommended autopatch targets: {', '.join(str(path) for path in recommended_targets)}")
            if summary["autopatch"]["patch_path"]:
                print(f"Autopatch patch: {summary['autopatch']['patch_path']}")
        print(f"Results JSON: {summary['artifacts']['results_json']}")
        print(f"Optimization report: {summary['artifacts']['optimization_report_json']}")
        print(f"Best complaint bundle: {summary['artifacts']['best_complaint_bundle_json']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
