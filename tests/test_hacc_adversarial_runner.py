import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
import sys
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_adversarial_runner import (
    _autopatch_constraints_for_profile,
    _autopatch_target_profiles,
    _build_diff_from_replacements,
    _build_agentic_llm_router,
    _codex_backup_model,
    _default_codex_model,
    _extract_file_replacements,
    _resolve_autopatch_timeout,
    run_hacc_adversarial_batch,
)


class HACCAdversarialRunnerTests(unittest.TestCase):
    def test_resolve_autopatch_timeout_uses_profile_defaults_and_can_disable(self) -> None:
        with mock.patch.dict("os.environ", {}, clear=False):
            self.assertEqual(_resolve_autopatch_timeout(profile="denoiser_select_candidates_only"), 150.0)
            self.assertEqual(_resolve_autopatch_timeout(profile="denoiser_standard_intake_only"), 150.0)
            self.assertEqual(_resolve_autopatch_timeout(profile="denoiser_process_answer_only"), 180.0)
            self.assertEqual(_resolve_autopatch_timeout(profile="phase_manager_action_only"), 120.0)
            self.assertEqual(_resolve_autopatch_timeout(profile="question_flow"), 300.0)
            self.assertEqual(_resolve_autopatch_timeout(profile="full_mediator"), 420.0)

        with mock.patch.dict("os.environ", {"HACC_AGENTIC_AUTOPATCH_TIMEOUT": "0"}, clear=False):
            self.assertIsNone(_resolve_autopatch_timeout(profile="question_flow"))

        with mock.patch.dict("os.environ", {"HACC_AGENTIC_AUTOPATCH_TIMEOUT": "180"}, clear=False):
            self.assertEqual(_resolve_autopatch_timeout(profile="question_flow"), 180.0)

    def test_denoiser_process_answer_profile_targets_symbol(self) -> None:
        target_files = _autopatch_target_profiles()["denoiser_process_answer_only"]
        constraints = _autopatch_constraints_for_profile("denoiser_process_answer_only", target_files)
        target_map = constraints["target_symbols"]
        self.assertEqual(len(target_map), 1)
        only_target, symbols = next(iter(target_map.items()))
        self.assertTrue(only_target.endswith("complaint_phases/denoiser.py"))
        self.assertEqual(symbols, ["process_answer"])

    def test_denoiser_standard_intake_profile_targets_symbol(self) -> None:
        target_files = _autopatch_target_profiles()["denoiser_standard_intake_only"]
        constraints = _autopatch_constraints_for_profile("denoiser_standard_intake_only", target_files)
        target_map = constraints["target_symbols"]
        self.assertEqual(len(target_map), 1)
        only_target, symbols = next(iter(target_map.items()))
        self.assertTrue(only_target.endswith("complaint_phases/denoiser.py"))
        self.assertEqual(symbols, ["_ensure_standard_intake_questions"])

    def test_denoiser_select_candidates_profile_targets_symbol(self) -> None:
        target_files = _autopatch_target_profiles()["denoiser_select_candidates_only"]
        constraints = _autopatch_constraints_for_profile("denoiser_select_candidates_only", target_files)
        target_map = constraints["target_symbols"]
        self.assertEqual(len(target_map), 1)
        only_target, symbols = next(iter(target_map.items()))
        self.assertTrue(only_target.endswith("complaint_phases/denoiser.py"))
        self.assertEqual(symbols, ["select_question_candidates"])

    def test_repair_helpers_can_build_diff_from_file_content_response(self) -> None:
        target = Path("mediator/inquiries.py")
        response = (
            "FILE: mediator/inquiries.py\n"
            "```python\n"
            "def generate():\n"
            "    return ['What happened?']\n"
            "```\n"
        )

        replacements = _extract_file_replacements(response, [target])
        self.assertIn(target, replacements)
        self.assertIn("What happened?", replacements[target])

        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            file_path = repo_root / target
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text("def generate():\n    return []\n", encoding="utf-8")

            diff = _build_diff_from_replacements(replacements=replacements, repo_root=repo_root)
            self.assertIn("--- a/mediator/inquiries.py", diff)
            self.assertIn("+++ b/mediator/inquiries.py", diff)
            self.assertIn("What happened?", diff)

    def test_codex_router_defaults_to_spark(self) -> None:
        with mock.patch("ipfs_datasets_py.llm_router.generate_text", return_value="OK") as generate_mock:
            router = _build_agentic_llm_router("codex_cli", profile="question_flow")
            self.assertIsNotNone(router)
            result = router.generate("Reply with OK", max_tokens=10, temperature=0)

        self.assertEqual(result, "OK")
        self.assertEqual(generate_mock.call_args.kwargs["model_name"], _default_codex_model())

    def test_codex_router_falls_back_to_mini_on_throttling(self) -> None:
        calls = []

        def fake_generate_text(**kwargs):
            calls.append(kwargs["model_name"])
            if len(calls) == 1:
                raise RuntimeError("Rate limit exceeded for this model")
            return "OK"

        with mock.patch("ipfs_datasets_py.llm_router.generate_text", side_effect=fake_generate_text):
            router = _build_agentic_llm_router("codex_cli", profile="question_flow")
            self.assertIsNotNone(router)
            result = router.generate("Reply with OK", max_tokens=10, temperature=0)

        self.assertEqual(result, "OK")
        self.assertEqual(calls[0], _default_codex_model())
        self.assertEqual(calls[1], _codex_backup_model())

    def test_demo_runner_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = run_hacc_adversarial_batch(
                output_dir=tmpdir,
                num_sessions=1,
                max_turns=2,
                max_parallel=1,
                hacc_preset="core_hacc_policies",
                hacc_search_mode="hybrid",
                demo=True,
            )

            artifacts = summary["artifacts"]
            results_path = Path(artifacts["results_json"])
            report_path = Path(artifacts["optimization_report_json"])
            best_path = Path(artifacts["best_complaint_bundle_json"])
            summary_path = Path(tmpdir) / "run_summary.json"

            self.assertTrue(results_path.is_file())
            self.assertTrue(report_path.is_file())
            self.assertTrue(best_path.is_file())
            self.assertTrue(summary_path.is_file())
            self.assertIn("router_diagnostics", summary)
            self.assertEqual(summary["inputs"]["hacc_search_mode"], "hybrid")
            self.assertIn(
                summary["router_diagnostics"]["embeddings_router"]["status"],
                {"available", "degraded", "error", "unavailable"},
            )
            self.assertIn("vector_index", summary["router_diagnostics"])
            self.assertIn(
                summary["router_diagnostics"]["vector_index"]["status"],
                {"available", "error", "unavailable"},
            )
            self.assertIn(
                summary["router_diagnostics"]["ipfs_router"]["status"],
                {"available", "unavailable"},
            )

            best_bundle = json.loads(best_path.read_text(encoding="utf-8"))
            self.assertIn("initial_complaint_text", best_bundle)
            self.assertTrue(best_bundle["initial_complaint_text"])
            self.assertIn("conversation_history", best_bundle)

    def test_live_runner_uses_llm_router_backend(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import backends.llm_router_backend as llm_router_backend_module
        import mediator as mediator_module

        router_calls = []

        def fake_generate_text(*, prompt, provider, model_name, **kwargs):
            router_calls.append(
                {
                    "prompt": prompt,
                    "provider": provider,
                    "model_name": model_name,
                }
            )
            lower_prompt = prompt.lower()
            if "scores:" in lower_prompt or "evaluate" in lower_prompt:
                return """SCORES:
question_quality: 0.80
information_extraction: 0.78
empathy: 0.74
efficiency: 0.76
coverage: 0.79

FEEDBACK:
The mediator asked strong questions grounded in the available evidence.

STRENGTHS:
- Good sequencing

WEAKNESSES:
- Could ask for a little more timeline detail

SUGGESTIONS:
- Ask for documentary evidence earlier
"""
            if "when" in lower_prompt or "date" in lower_prompt:
                return "The denial happened on February 2, 2026."
            if "witness" in lower_prompt or "document" in lower_prompt:
                return "I have emails and a witness statement."
            return "The housing authority denied my request after I complained about the policy."

        class FakeMediator:
            def __init__(self, *args, **kwargs):
                self.phase_manager = mock.Mock()
                self.phase_manager.get_phase_data.side_effect = lambda phase, key: None
                self.questions_asked = 0

            def start_three_phase_process(self, complaint_text):
                return {
                    "phase": "intake",
                    "initial_questions": [
                        {"question": "When did the denial happen?", "type": "timeline"}
                    ],
                }

            def process_denoising_answer(self, question, answer):
                self.questions_asked += 1
                return {
                    "converged": self.questions_asked >= 2,
                    "next_questions": [] if self.questions_asked >= 2 else [
                        {"question": "What documents support that?", "type": "evidence"}
                    ],
                }

            def get_three_phase_status(self):
                return {
                    "current_phase": "intake",
                    "iteration_count": self.questions_asked,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(llm_router_backend_module, "generate_text", side_effect=fake_generate_text):
                with mock.patch.object(mediator_module, "Mediator", FakeMediator):
                    summary = run_hacc_adversarial_batch(
                        output_dir=tmpdir,
                        num_sessions=1,
                        max_turns=2,
                        max_parallel=1,
                        hacc_preset="core_hacc_policies",
                        demo=False,
                        provider="copilot_cli",
                        model="gpt-5-mini",
                    )

        self.assertEqual(summary["runtime"]["mode"], "llm_router")
        self.assertEqual(summary["runtime"]["complainant_backend_class"], "LLMRouterBackend")
        self.assertEqual(summary["runtime"]["critic_backend_class"], "LLMRouterBackend")
        self.assertGreater(len(router_calls), 0)
        self.assertTrue(any(call["provider"] == "copilot_cli" for call in router_calls))
        self.assertTrue(any(call["model_name"] == "gpt-5-mini" for call in router_calls))

    def test_live_runner_passes_session_db_paths_to_mediator(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import backends.llm_router_backend as llm_router_backend_module
        import mediator as mediator_module

        init_kwargs = []

        def fake_generate_text(*, prompt, provider, model_name, **kwargs):
            lower_prompt = prompt.lower()
            if "scores:" in lower_prompt or "evaluate" in lower_prompt:
                return """SCORES:
question_quality: 0.80
information_extraction: 0.78
empathy: 0.74
efficiency: 0.76
coverage: 0.79

FEEDBACK:
The mediator asked strong questions grounded in the available evidence.

STRENGTHS:
- Good sequencing

WEAKNESSES:
- Could ask for a little more timeline detail

SUGGESTIONS:
- Ask for documentary evidence earlier
"""
            return "The housing authority denied my request after I complained about the policy."

        class FakeMediator:
            def __init__(self, *args, **kwargs):
                init_kwargs.append(kwargs)
                self.phase_manager = mock.Mock()
                self.phase_manager.get_phase_data.side_effect = lambda phase, key: None

            def save_claim_support_document(self, **kwargs):
                return {"cid": "cid-123", "record_id": 1, "metadata": kwargs.get("metadata", {})}

            def start_three_phase_process(self, complaint_text):
                return {
                    "phase": "intake",
                    "initial_questions": [],
                }

            def process_denoising_answer(self, question, answer):
                return {
                    "converged": True,
                    "next_questions": [],
                }

            def get_three_phase_status(self):
                return {
                    "current_phase": "intake",
                    "iteration_count": 1,
                }

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(llm_router_backend_module, "generate_text", side_effect=fake_generate_text):
                with mock.patch.object(mediator_module, "Mediator", FakeMediator):
                    run_hacc_adversarial_batch(
                        output_dir=tmpdir,
                        num_sessions=1,
                        max_turns=1,
                        max_parallel=1,
                        hacc_preset="core_hacc_policies",
                        demo=False,
                        provider="copilot_cli",
                        model="gpt-5-mini",
                    )

        self.assertTrue(init_kwargs)
        mediator_kwargs = init_kwargs[0]
        self.assertTrue(str(mediator_kwargs["evidence_db_path"]).endswith("evidence.duckdb"))
        self.assertTrue(str(mediator_kwargs["legal_authority_db_path"]).endswith("legal_authorities.duckdb"))
        self.assertTrue(str(mediator_kwargs["claim_support_db_path"]).endswith("claim_support.duckdb"))

    def test_runner_can_emit_autopatch_summary(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import adversarial_harness.optimizer as optimizer_module

        fake_patch = Path("/tmp/fake-mediator.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_patch.write_text("diff --git a/file b/file\n", encoding="utf-8")
            with mock.patch.dict("os.environ", {"HACC_AUTOPATCH_AUTO_APPLY": "0"}):
                with mock.patch.object(
                    optimizer_module.Optimizer,
                    "run_agentic_autopatch",
                    return_value=SimpleNamespace(
                        success=True,
                        patch_path=fake_patch,
                        patch_cid="bafy-autopatch",
                        metadata={"kind": "runner-test"},
                    ),
                ) as autopatch_mock:
                    with mock.patch(
                        "hacc_adversarial_runner._validate_generated_patch",
                        return_value={
                            "passed": True,
                            "level": "standard",
                            "target_files": ["mediator/inquiries.py"],
                            "file_results": [],
                            "errors": [],
                            "warnings": [],
                        },
                    ):
                        summary = run_hacc_adversarial_batch(
                            output_dir=tmpdir,
                            num_sessions=1,
                            max_turns=1,
                            max_parallel=1,
                            hacc_preset="core_hacc_policies",
                            demo=True,
                            emit_autopatch=True,
                        )

            self.assertTrue(summary["autopatch"]["requested"])
            self.assertTrue(summary["autopatch"]["success"])
            self.assertEqual(summary["autopatch"]["patch_cid"], "bafy-autopatch")
            self.assertEqual(summary["artifacts"]["autopatch_patch_path"], str(fake_patch.resolve()))
            self.assertTrue(Path(summary["artifacts"]["autopatch_summary_json"]).is_file())
            self.assertTrue(summary["autopatch"]["validation"]["patch_validation"]["passed"])
            autopatch_kwargs = autopatch_mock.call_args.kwargs
            self.assertEqual(autopatch_kwargs["method"], "test_driven")
            self.assertEqual(summary["autopatch"]["profile"], "question_flow")
            self.assertGreaterEqual(len(autopatch_kwargs["target_files"]), 2)
            self.assertTrue(any(str(path).endswith("complaint_phases/phase_manager.py") for path in autopatch_kwargs["target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/inquiries.py") for path in autopatch_kwargs["target_files"]))

    def test_runner_auto_applies_valid_patch_by_default(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import adversarial_harness.optimizer as optimizer_module
        import ipfs_datasets_py.optimizers.agentic.patch_control as patch_control_module

        fake_patch = Path("/tmp/fake-auto-apply.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_patch.write_text("diff --git a/file b/file\n", encoding="utf-8")
            patch_instance = SimpleNamespace(validated=False)
            with mock.patch.object(
                optimizer_module.Optimizer,
                "run_agentic_autopatch",
                return_value=SimpleNamespace(
                    success=True,
                    patch_path=fake_patch,
                    patch_cid="bafy-auto-apply",
                    metadata={"kind": "auto-apply-test"},
                ),
            ):
                with mock.patch(
                    "hacc_adversarial_runner._validate_generated_patch",
                    return_value={
                        "passed": True,
                        "level": "standard",
                        "target_files": ["complaint_phases/phase_manager.py"],
                        "file_results": [],
                        "errors": [],
                        "warnings": [],
                    },
                ):
                    with mock.patch.object(
                        patch_control_module.PatchManager,
                        "load_patch",
                        return_value=patch_instance,
                    ) as load_mock:
                        with mock.patch.object(
                            patch_control_module.PatchManager,
                            "apply_patch",
                            return_value=True,
                        ) as apply_mock:
                            summary = run_hacc_adversarial_batch(
                                output_dir=tmpdir,
                                num_sessions=1,
                                max_turns=1,
                                max_parallel=1,
                                hacc_preset="core_hacc_policies",
                                demo=True,
                                emit_autopatch=True,
                            )

            self.assertTrue(summary["autopatch"]["applied"])
            self.assertTrue(summary["autopatch"]["apply_success"])
            load_mock.assert_called_once_with(fake_patch)
            apply_mock.assert_called_once()

    def test_runner_can_apply_autopatch_via_patch_manager(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import adversarial_harness.optimizer as optimizer_module
        import ipfs_datasets_py.optimizers.agentic.patch_control as patch_control_module

        fake_patch = Path("/tmp/fake-apply.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_patch.write_text("diff --git a/file b/file\n", encoding="utf-8")
            patch_instance = SimpleNamespace(validated=False)
            with mock.patch.object(
                optimizer_module.Optimizer,
                "run_agentic_autopatch",
                return_value=SimpleNamespace(
                    success=True,
                    patch_path=fake_patch,
                    patch_cid="bafy-apply",
                    metadata={"kind": "apply-test"},
                ),
            ):
                with mock.patch.object(
                    patch_control_module.PatchManager,
                    "load_patch",
                    return_value=patch_instance,
                ) as load_mock:
                    with mock.patch.object(
                        patch_control_module.PatchManager,
                        "apply_patch",
                        return_value=True,
                    ) as apply_mock:
                        with mock.patch(
                            "hacc_adversarial_runner._validate_generated_patch",
                            return_value={
                                "passed": True,
                                "level": "standard",
                                "target_files": ["mediator/mediator.py"],
                                "file_results": [],
                                "errors": [],
                                "warnings": [],
                            },
                        ):
                            summary = run_hacc_adversarial_batch(
                                output_dir=tmpdir,
                                num_sessions=1,
                                max_turns=1,
                                max_parallel=1,
                                hacc_preset="core_hacc_policies",
                                demo=True,
                                apply_autopatch=True,
                                autopatch_target_files=["mediator/mediator.py"],
                            )

            self.assertTrue(summary["autopatch"]["requested"])
            self.assertTrue(summary["autopatch"]["success"])
            self.assertTrue(summary["autopatch"]["applied"])
            self.assertTrue(summary["autopatch"]["apply_success"])
            load_mock.assert_called_once_with(fake_patch)
            apply_mock.assert_called_once()
            self.assertEqual(apply_mock.call_args.args[0], patch_instance)
            self.assertEqual(apply_mock.call_args.args[1], complaint_generator_root)

    def test_runner_blocks_autopatch_apply_when_patch_validation_fails(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import adversarial_harness.optimizer as optimizer_module
        import ipfs_datasets_py.optimizers.agentic.patch_control as patch_control_module

        fake_patch = Path("/tmp/fake-invalid.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_patch.write_text("diff --git a/file b/file\n", encoding="utf-8")
            with mock.patch.object(
                optimizer_module.Optimizer,
                "run_agentic_autopatch",
                return_value=SimpleNamespace(
                    success=True,
                    patch_path=fake_patch,
                    patch_cid="bafy-invalid",
                    metadata={"kind": "invalid-apply-test"},
                ),
            ):
                with mock.patch(
                    "hacc_adversarial_runner._validate_generated_patch",
                    return_value={
                        "passed": False,
                        "level": "standard",
                        "target_files": ["complaint_phases/phase_manager.py"],
                        "file_results": [
                            {
                                "file": "complaint_phases/phase_manager.py",
                                "passed": False,
                                "errors": ["syntax failure"],
                                "warnings": [],
                            }
                        ],
                        "errors": ["complaint_phases/phase_manager.py: syntax failure"],
                        "warnings": [],
                    },
                ):
                    with mock.patch.object(
                        patch_control_module.PatchManager,
                        "apply_patch",
                        return_value=True,
                    ) as apply_mock:
                        summary = run_hacc_adversarial_batch(
                            output_dir=tmpdir,
                            num_sessions=1,
                            max_turns=1,
                            max_parallel=1,
                            hacc_preset="core_hacc_policies",
                            demo=True,
                            apply_autopatch=True,
                            autopatch_target_files=["complaint_phases/phase_manager.py"],
                        )

            self.assertTrue(summary["autopatch"]["requested"])
            self.assertTrue(summary["autopatch"]["success"])
            self.assertTrue(summary["autopatch"]["applied"])
            self.assertFalse(summary["autopatch"]["apply_success"])
            self.assertFalse(summary["autopatch"]["validation"]["patch_validation"]["passed"])
            self.assertIn("validation", str(summary["autopatch"]["error"]).lower())
            apply_mock.assert_not_called()

    def test_runner_repairs_invalid_patch_before_apply(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        import adversarial_harness.optimizer as optimizer_module
        import ipfs_datasets_py.optimizers.agentic.patch_control as patch_control_module

        bad_patch = Path("/tmp/fake-bad.patch")
        repaired_patch = Path("/tmp/fake-bad-repair1.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            bad_patch.write_text("diff --git a/file b/file\n", encoding="utf-8")
            patch_instance = SimpleNamespace(validated=False)
            with mock.patch.object(
                optimizer_module.Optimizer,
                "run_agentic_autopatch",
                return_value=SimpleNamespace(
                    success=True,
                    patch_path=bad_patch,
                    patch_cid="bafy-bad",
                    metadata={"kind": "repair-test"},
                ),
            ):
                with mock.patch(
                    "hacc_adversarial_runner._validate_generated_patch",
                    side_effect=[
                        {
                            "passed": False,
                            "level": "standard",
                            "target_files": ["complaint_phases/phase_manager.py"],
                            "file_results": [],
                            "errors": ["targeted pytest failed"],
                            "warnings": [],
                        },
                        {
                            "passed": True,
                            "level": "standard",
                            "target_files": ["complaint_phases/phase_manager.py"],
                            "file_results": [],
                            "errors": [],
                            "warnings": [],
                        },
                    ],
                ):
                    with mock.patch(
                        "hacc_adversarial_runner._repair_patch_with_llm",
                        return_value={
                            "patch_path": str(repaired_patch),
                            "raw_response_preview": "--- a/file\n+++ b/file\n",
                        },
                    ) as repair_mock:
                        with mock.patch.object(
                            patch_control_module.PatchManager,
                            "load_patch",
                            return_value=patch_instance,
                        ) as load_mock:
                            with mock.patch.object(
                                patch_control_module.PatchManager,
                                "apply_patch",
                                return_value=True,
                            ) as apply_mock:
                                summary = run_hacc_adversarial_batch(
                                    output_dir=tmpdir,
                                    num_sessions=1,
                                    max_turns=1,
                                    max_parallel=1,
                                    hacc_preset="core_hacc_policies",
                                    demo=True,
                                    emit_autopatch=True,
                                )

            self.assertTrue(summary["autopatch"]["success"])
            self.assertEqual(summary["autopatch"]["patch_path"], str(repaired_patch))
            self.assertEqual(len(summary["autopatch"]["repair_attempts"]), 1)
            self.assertTrue(summary["autopatch"]["repair_attempts"][0]["passed"])
            self.assertTrue(summary["autopatch"]["apply_success"])
            repair_mock.assert_called_once()
            load_mock.assert_called_once_with(repaired_patch)
            apply_mock.assert_called_once()


if __name__ == "__main__":
    unittest.main()
