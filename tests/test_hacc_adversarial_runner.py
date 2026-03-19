import inspect
import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
import sys
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_adversarial_runner import (
    _best_complaint_grounding_overview,
    _autopatch_constraints_for_profile,
    _autopatch_target_profiles,
    _build_diff_from_replacements,
    _build_agentic_llm_router,
    _codex_backup_model,
    _default_codex_model,
    _extract_file_replacements,
    _resolve_autopatch_timeout,
    main,
    run_hacc_adversarial_batch,
)


class HACCAdversarialRunnerTests(unittest.TestCase):
    @staticmethod
    def _available_router_diagnostics() -> dict:
        return {
            "ipfs_router": {"status": "available"},
            "embeddings_router": {"status": "available"},
            "vector_index": {"status": "available"},
        }

    @staticmethod
    def _build_fake_llm_router_runtime_bundle(*, provider: str, model: str):
        import hacc_adversarial_runner as runner_module

        original_load_runtime = runner_module._load_runtime
        runtime_bundle = original_load_runtime(False, None, None, provider, model)

        class FakeHarness:
            def __init__(
                self,
                *,
                llm_backend_complainant,
                llm_backend_critic,
                mediator_factory,
                max_parallel,
                session_state_dir,
            ):
                self._complainant_backend = llm_backend_complainant
                self._critic_backend = llm_backend_critic
                self._mediator_factory = mediator_factory
                self._session_state_dir = Path(session_state_dir)
                self._max_parallel = max_parallel

            def run_batch(self, *, num_sessions, personalities, max_turns_per_session, **kwargs):
                mediator = self._mediator_factory(
                    evidence_db_path=self._session_state_dir / "evidence.duckdb",
                    legal_authority_db_path=self._session_state_dir / "legal_authorities.duckdb",
                    claim_support_db_path=self._session_state_dir / "claim_support.duckdb",
                )
                intake_state = mediator.start_three_phase_process(
                    "The housing authority denied my request after I complained about the policy."
                )
                questions = list(intake_state.get("initial_questions") or [])

                turns_remaining = max(1, int(max_turns_per_session or 1))
                while questions and turns_remaining > 0:
                    question = dict(questions.pop(0))
                    answer = self._complainant_backend(question.get("question") or "Provide more detail.")
                    result = mediator.process_denoising_answer(question.get("question"), answer)
                    if result.get("converged"):
                        break
                    questions = list(result.get("next_questions") or [])
                    turns_remaining -= 1

                self._critic_backend(
                    "Evaluate this mediation session and return SCORES: question_quality, information_extraction, empathy, efficiency, coverage."
                )

                return [
                    SimpleNamespace(
                        success=True,
                        session_id="session-1",
                        initial_complaint_text="Grounded complaint text",
                        seed_complaint={
                            "type": "grounded_hacc_seed",
                            "summary": "Grounded complaint based on HACC evidence.",
                            "key_facts": {},
                            "hacc_evidence": [],
                        },
                        critic_score=SimpleNamespace(overall_score=0.8),
                    )
                ]

            def get_statistics(self):
                return {"total_sessions": 1, "max_parallel": self._max_parallel}

            def save_results(self, path):
                Path(path).write_text(json.dumps({"results": [{"session_id": "session-1"}]}), encoding="utf-8")

            def save_anchor_section_report(self, path, format="csv"):
                Path(path).write_text("anchor_section,covered\n", encoding="utf-8")

        class FakeReport:
            def to_dict(self):
                return {
                    "average_score": 0.8,
                    "score_trend": "stable",
                    "recommended_hacc_preset": "core_hacc_policies",
                    "priority_improvements": [],
                    "recommendations": [],
                    "intake_priority_performance": {},
                    "coverage_remediation": {},
                    "best_session_id": "session-1",
                }

        class FakeOptimizer:
            def analyze(self, results):
                return FakeReport()

            @staticmethod
            def _recommended_target_files_for_report(report):
                return []

        runtime_bundle["AdversarialHarness"] = FakeHarness
        runtime_bundle["Optimizer"] = FakeOptimizer
        return runtime_bundle

    @staticmethod
    def _build_fake_demo_runtime_bundle():
        import adversarial_harness.optimizer as optimizer_module

        class FakeHarness:
            def __init__(
                self,
                *,
                llm_backend_complainant,
                llm_backend_critic,
                mediator_factory,
                max_parallel,
                session_state_dir,
            ):
                self._max_parallel = max_parallel
                self._session_state_dir = Path(session_state_dir)
                self._results = []

            def run_batch(self, *, num_sessions, personalities, max_turns_per_session, **kwargs):
                result = SimpleNamespace(
                    success=True,
                    session_id="session-1",
                    initial_complaint_text="Grounded complaint text",
                    conversation_history=[{"role": "mediator", "content": "Please describe the denial."}],
                    seed_complaint={
                        "type": "grounded_hacc_seed",
                        "summary": "Grounded complaint based on HACC policy evidence.",
                        "hacc_preset": kwargs.get("hacc_preset"),
                        "key_facts": {
                            "evidence_summary": "HACC grievance procedure language anchored to intake gaps.",
                            "anchor_sections": ["grievance_hearing"],
                        },
                        "hacc_evidence": [
                            {"title": "ADMINISTRATIVE PLAN", "snippet": "Informal hearing language."}
                        ],
                    },
                    critic_score=SimpleNamespace(
                        overall_score=0.82,
                        question_quality=0.81,
                        information_extraction=0.8,
                        empathy=0.77,
                        efficiency=0.79,
                        coverage=0.83,
                        strengths=["Good sequencing"],
                        weaknesses=["Needs more timeline detail"],
                        suggestions=["Ask for documentary evidence earlier"],
                        anchor_sections_missing=["timeline"],
                        anchor_sections_covered=["grievance_hearing"],
                    ),
                    final_state={},
                    knowledge_graph_summary={},
                    dependency_graph_summary={},
                )
                self._results = [result]
                return list(self._results)

            def get_statistics(self):
                return {"total_sessions": len(self._results), "max_parallel": self._max_parallel}

            def save_results(self, path):
                Path(path).write_text(json.dumps({"results": [{"session_id": "session-1"}]}), encoding="utf-8")

            def save_anchor_section_report(self, path, format="csv"):
                Path(path).write_text("anchor_section,covered\ngrievance_hearing,1\n", encoding="utf-8")

        return {
            "AdversarialHarness": FakeHarness,
            "Optimizer": optimizer_module.Optimizer,
            "complainant_backend": object(),
            "critic_backend": object(),
            "mediator_factory": lambda **kwargs: object(),
            "runtime": {"mode": "demo", "provider": "demo", "model": "demo"},
        }

    def test_runner_path_imports_file_based_hacc_loader(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) in sys.path:
            sys.path.remove(str(complaint_generator_root))

        from hacc_adversarial_runner import _ensure_complaint_generator_on_path

        _ensure_complaint_generator_on_path()

        import adversarial_harness.hacc_evidence as hacc_evidence_module

        source = inspect.getsource(hacc_evidence_module._load_hacc_engine)

        self.assertIn(str(complaint_generator_root), sys.path)
        self.assertIn("spec_from_file_location", source)
        self.assertIn("module_from_spec", source)
        self.assertNotIn('importlib.import_module("hacc_research")', source)

    def test_best_complaint_grounding_overview_summarizes_anchor_context(self) -> None:
        best_result = SimpleNamespace(
            seed_complaint={
                "summary": "Retaliation complaint grounded in HACC grievance procedures.",
                "key_facts": {
                    "evidence_summary": "HACC policy language supporting grievance and appeal protections.",
                    "anchor_sections": ["grievance_hearing", "appeal_rights"],
                    "anchor_passages": [
                        {"title": "ADMINISTRATIVE PLAN", "snippet": "Informal hearing language."},
                        {"title": "ACOP", "snippet": "Appeal notice language."},
                    ],
                },
                "hacc_evidence": [
                    {"title": "ADMINISTRATIVE PLAN", "snippet": "Informal hearing language."},
                    {"title": "ACOP", "snippet": "Appeal notice language."},
                ],
            }
        )

        overview = _best_complaint_grounding_overview(best_result)

        self.assertEqual(overview["evidence_summary"], "HACC policy language supporting grievance and appeal protections.")
        self.assertEqual(overview["anchor_sections"], ["grievance_hearing", "appeal_rights"])
        self.assertEqual(overview["anchor_passage_count"], 2)
        self.assertEqual(overview["evidence_item_count"], 2)
        self.assertEqual(overview["top_documents"], ["ADMINISTRATIVE PLAN", "ACOP"])

    def test_run_hacc_adversarial_batch_passes_hacc_grounding_flags(self) -> None:
        run_batch_kwargs = {}

        class FakeHarness:
            def __init__(self, *args, **kwargs):
                self._init_kwargs = kwargs

            def run_batch(self, **kwargs):
                run_batch_kwargs.update(kwargs)
                return []

            def get_statistics(self):
                return {"total_sessions": 0}

            def save_results(self, path):
                Path(path).write_text(json.dumps({"results": []}), encoding="utf-8")

            def save_anchor_section_report(self, path, format="csv"):
                Path(path).write_text("anchor_section,covered\n", encoding="utf-8")

        class FakeReport:
            def to_dict(self):
                return {
                    "average_score": 0.0,
                    "score_trend": "insufficient_data",
                    "recommended_hacc_preset": "core_hacc_policies",
                    "priority_improvements": [],
                    "recommendations": [],
                    "intake_priority_performance": {},
                    "coverage_remediation": {},
                    "best_session_id": None,
                }

        class FakeOptimizer:
            def analyze(self, results):
                return FakeReport()

            @staticmethod
            def _recommended_target_files_for_report(report):
                return []

        runtime_bundle = {
            "AdversarialHarness": FakeHarness,
            "Optimizer": FakeOptimizer,
            "complainant_backend": object(),
            "critic_backend": object(),
            "mediator_factory": lambda **kwargs: object(),
            "runtime": {"mode": "demo"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
                with mock.patch(
                    "hacc_adversarial_runner._router_diagnostics",
                    return_value={
                        "ipfs_router": {"status": "available"},
                        "embeddings_router": {"status": "available"},
                        "vector_index": {"status": "available"},
                    },
                ):
                    summary = run_hacc_adversarial_batch(
                        output_dir=tmpdir,
                        num_sessions=2,
                        max_turns=3,
                        max_parallel=1,
                        hacc_preset="core_hacc_policies",
                        hacc_count=2,
                        hacc_search_mode="package",
                        use_hacc_vector_search=False,
                        demo=True,
                    )

        self.assertTrue(run_batch_kwargs["include_hacc_evidence"])
        self.assertEqual(run_batch_kwargs["hacc_preset"], "core_hacc_policies")
        self.assertEqual(run_batch_kwargs["hacc_count"], 2)
        self.assertEqual(run_batch_kwargs["hacc_search_mode"], "package")
        self.assertFalse(run_batch_kwargs["use_hacc_vector_search"])
        self.assertEqual(summary["inputs"]["hacc_search_mode"], "package")
        self.assertEqual(summary["search_summary"]["requested_search_mode"], "package")
        self.assertEqual(summary["best_complaint"]["grounding_overview"], {})
        self.assertEqual(summary["best_complaint"]["search_summary"], summary["search_summary"])

    def test_run_hacc_adversarial_batch_reports_package_fallback_when_vector_unavailable(self) -> None:
        class FakeHarness:
            def __init__(self, *args, **kwargs):
                self._init_kwargs = kwargs

            def run_batch(self, **kwargs):
                return []

            def get_statistics(self):
                return {"total_sessions": 0}

            def save_results(self, path):
                Path(path).write_text(json.dumps({"results": []}), encoding="utf-8")

            def save_anchor_section_report(self, path, format="csv"):
                Path(path).write_text("anchor_section,covered\n", encoding="utf-8")

        class FakeReport:
            def to_dict(self):
                return {
                    "average_score": 0.0,
                    "score_trend": "insufficient_data",
                    "recommended_hacc_preset": "core_hacc_policies",
                    "priority_improvements": [],
                    "recommendations": [],
                    "intake_priority_performance": {},
                    "coverage_remediation": {},
                    "best_session_id": None,
                }

        class FakeOptimizer:
            def analyze(self, results):
                return FakeReport()

            @staticmethod
            def _recommended_target_files_for_report(report):
                return []

        runtime_bundle = {
            "AdversarialHarness": FakeHarness,
            "Optimizer": FakeOptimizer,
            "complainant_backend": object(),
            "critic_backend": object(),
            "mediator_factory": lambda **kwargs: object(),
            "runtime": {"mode": "demo"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
                with mock.patch(
                    "hacc_adversarial_runner._router_diagnostics",
                    return_value={
                        "ipfs_router": {"status": "available"},
                        "embeddings_router": {"status": "available"},
                        "vector_index": {"status": "error", "error": "numpy unavailable"},
                    },
                ):
                    summary = run_hacc_adversarial_batch(
                        output_dir=tmpdir,
                        num_sessions=1,
                        max_turns=1,
                        max_parallel=1,
                        hacc_preset="core_hacc_policies",
                        hacc_search_mode="package",
                        use_hacc_vector_search=False,
                        demo=True,
                    )

        self.assertEqual(summary["search_summary"]["requested_search_mode"], "package")
        self.assertEqual(summary["search_summary"]["effective_search_mode"], "lexical_fallback")
        self.assertIn("vector support is unavailable", summary["search_summary"]["fallback_note"])
        self.assertIn("numpy unavailable", summary["search_summary"]["fallback_note"])
        self.assertEqual(summary["best_complaint"]["search_summary"], summary["search_summary"])

    def test_run_hacc_adversarial_batch_reports_hybrid_fallback_when_vector_unavailable(self) -> None:
        class FakeHarness:
            def __init__(self, *args, **kwargs):
                self._init_kwargs = kwargs

            def run_batch(self, **kwargs):
                return []

            def get_statistics(self):
                return {"total_sessions": 0}

            def save_results(self, path):
                Path(path).write_text(json.dumps({"results": []}), encoding="utf-8")

            def save_anchor_section_report(self, path, format="csv"):
                Path(path).write_text("anchor_section,covered\n", encoding="utf-8")

        class FakeReport:
            def to_dict(self):
                return {
                    "average_score": 0.0,
                    "score_trend": "insufficient_data",
                    "recommended_hacc_preset": "core_hacc_policies",
                    "priority_improvements": [],
                    "recommendations": [],
                    "intake_priority_performance": {},
                    "coverage_remediation": {},
                    "best_session_id": None,
                }

        class FakeOptimizer:
            def analyze(self, results):
                return FakeReport()

            @staticmethod
            def _recommended_target_files_for_report(report):
                return []

        runtime_bundle = {
            "AdversarialHarness": FakeHarness,
            "Optimizer": FakeOptimizer,
            "complainant_backend": object(),
            "critic_backend": object(),
            "mediator_factory": lambda **kwargs: object(),
            "runtime": {"mode": "demo"},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
                with mock.patch(
                    "hacc_adversarial_runner._router_diagnostics",
                    return_value={
                        "ipfs_router": {"status": "available"},
                        "embeddings_router": {"status": "available"},
                        "vector_index": {"status": "error", "error": "numpy unavailable"},
                    },
                ):
                    summary = run_hacc_adversarial_batch(
                        output_dir=tmpdir,
                        num_sessions=1,
                        max_turns=1,
                        max_parallel=1,
                        hacc_preset="core_hacc_policies",
                        hacc_search_mode="hybrid",
                        use_hacc_vector_search=True,
                        demo=True,
                    )

        self.assertEqual(summary["search_summary"]["requested_search_mode"], "hybrid")
        self.assertTrue(summary["search_summary"]["requested_use_vector"])
        self.assertEqual(summary["search_summary"]["effective_search_mode"], "lexical_only")
        self.assertIn("vector support is unavailable", summary["search_summary"]["fallback_note"])
        self.assertIn("numpy unavailable", summary["search_summary"]["fallback_note"])
        self.assertEqual(summary["best_complaint"]["search_summary"], summary["search_summary"])

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
        runtime_bundle = self._build_fake_demo_runtime_bundle()

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch(
                "hacc_adversarial_runner._router_diagnostics",
                return_value=self._available_router_diagnostics(),
            ):
                with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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
            self.assertEqual(summary["search_summary"]["requested_search_mode"], "hybrid")
            self.assertIn("intake_priority_performance", summary["optimization_report"])
            self.assertIn("coverage_remediation", summary["optimization_report"])
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
            self.assertEqual(summary["best_complaint"]["search_summary"], summary["search_summary"])
            self.assertIn("grounding_overview", summary["best_complaint"])

            best_bundle = json.loads(best_path.read_text(encoding="utf-8"))
            optimization_payload = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertIn("initial_complaint_text", best_bundle)
            self.assertTrue(best_bundle["initial_complaint_text"])
            self.assertIn("conversation_history", best_bundle)
            self.assertIn("intake_priority_performance", optimization_payload)
            self.assertIn("coverage_remediation", optimization_payload)

    def test_main_prints_effective_search_mode_and_fallback(self) -> None:
        fake_summary = {
            "artifacts": {
                "output_dir": "/tmp/adversarial",
                "results_json": "/tmp/adversarial/adversarial_results.json",
                "optimization_report_json": "/tmp/adversarial/optimization_report.json",
                "best_complaint_bundle_json": "/tmp/adversarial/best_complaint_bundle.json",
            },
            "best_complaint": {
                "score": 0.525,
                "seed_type": "housing_discrimination",
                "seed_summary": "seed summary",
            },
            "search_summary": {
                "requested_search_mode": "hybrid",
                "effective_search_mode": "lexical_only",
                "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead.",
            },
            "optimization_report": {"recommended_hacc_preset": "retaliation_focus"},
            "inputs": {"hacc_preset": "retaliation_focus"},
            "autopatch": {"requested": False},
        }

        stdout = StringIO()
        with mock.patch("hacc_adversarial_runner.run_hacc_adversarial_batch", return_value=fake_summary):
            with mock.patch("sys.stdout", stdout):
                exit_code = main(["--demo", "--output-dir", "/tmp/adversarial"])

        rendered = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("HACC search mode: requested=hybrid effective=lexical_only", rendered)
        self.assertIn("HACC search fallback:", rendered)

    def test_main_prints_recommended_autopatch_profile_and_targets(self) -> None:
        fake_summary = {
            "artifacts": {
                "output_dir": "/tmp/adversarial",
                "results_json": "/tmp/adversarial/adversarial_results.json",
                "optimization_report_json": "/tmp/adversarial/optimization_report.json",
                "best_complaint_bundle_json": "/tmp/adversarial/best_complaint_bundle.json",
            },
            "best_complaint": {
                "score": 0.725,
                "seed_type": "housing_discrimination",
                "seed_summary": "seed summary",
            },
            "search_summary": {
                "requested_search_mode": "package",
                "effective_search_mode": "package",
            },
            "optimization_report": {"recommended_hacc_preset": "core_hacc_policies"},
            "inputs": {"hacc_preset": "core_hacc_policies"},
            "autopatch": {
                "requested": True,
                "success": False,
                "apply_success": False,
                "patch_path": None,
                "requested_profile": "question_flow",
                "requested_target_files": [
                    "/home/barberb/HACC/complaint-generator/complaint_phases/phase_manager.py",
                    "/home/barberb/HACC/complaint-generator/mediator/inquiries.py",
                ],
                "preflight": {
                    "ready": False,
                    "error": "No module named 'cachetools'",
                },
                "used_recommended_targets": True,
                "profile": "question_flow",
                "target_files": [
                    "/home/barberb/HACC/complaint-generator/adversarial_harness/session.py",
                    "/home/barberb/HACC/complaint-generator/mediator/mediator.py",
                ],
                "recommended_profile": "question_flow",
                "recommended_target_files": [
                    "/home/barberb/HACC/complaint-generator/adversarial_harness/session.py",
                    "/home/barberb/HACC/complaint-generator/mediator/mediator.py",
                ],
            },
        }

        stdout = StringIO()
        with mock.patch("hacc_adversarial_runner.run_hacc_adversarial_batch", return_value=fake_summary):
            with mock.patch("sys.stdout", stdout):
                exit_code = main(["--demo", "--output-dir", "/tmp/adversarial", "--emit-autopatch"])

        rendered = stdout.getvalue()
        self.assertEqual(exit_code, 0)
        self.assertIn("Using recommended autopatch targets: True", rendered)
        self.assertIn("Autopatch preflight ready: False", rendered)
        self.assertIn("Autopatch preflight error: No module named 'cachetools'", rendered)
        self.assertIn("Requested autopatch profile: question_flow", rendered)
        self.assertIn(
            "Requested autopatch targets: /home/barberb/HACC/complaint-generator/complaint_phases/phase_manager.py, "
            "/home/barberb/HACC/complaint-generator/mediator/inquiries.py",
            rendered,
        )
        self.assertIn("Recommended autopatch profile: question_flow", rendered)
        self.assertIn(
            "Recommended autopatch targets: /home/barberb/HACC/complaint-generator/adversarial_harness/session.py, "
            "/home/barberb/HACC/complaint-generator/mediator/mediator.py",
            rendered,
        )
        self.assertIn("Selected autopatch profile: question_flow", rendered)
        self.assertIn(
            "Selected autopatch targets: /home/barberb/HACC/complaint-generator/adversarial_harness/session.py, "
            "/home/barberb/HACC/complaint-generator/mediator/mediator.py",
            rendered,
        )

    def test_runner_can_use_recommended_autopatch_targets(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        runtime_bundle = self._build_fake_demo_runtime_bundle()

        import adversarial_harness.optimizer as optimizer_module

        fake_patch = Path("/tmp/fake-recommended.patch")
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(
                optimizer_module.Optimizer,
                "run_agentic_autopatch",
                return_value=SimpleNamespace(
                    success=True,
                    patch_path=fake_patch,
                    patch_cid="bafy-recommended",
                    metadata={
                        "report_summary": {
                            "recommended_target_files": [
                                "adversarial_harness/session.py",
                                "mediator/mediator.py",
                                "adversarial_harness/complainant.py",
                            ]
                        }
                    },
                ),
            ) as autopatch_mock:
                with mock.patch.object(
                    optimizer_module.Optimizer,
                    "_recommended_target_files_for_report",
                    return_value=[
                        "adversarial_harness/session.py",
                        "mediator/mediator.py",
                        "adversarial_harness/complainant.py",
                    ],
                ):
                    with mock.patch(
                        "hacc_adversarial_runner._validate_generated_patch",
                        return_value={
                            "passed": True,
                            "level": "standard",
                            "target_files": ["adversarial_harness/session.py"],
                            "file_results": [],
                            "errors": [],
                            "warnings": [],
                        },
                    ):
                        with mock.patch(
                            "hacc_adversarial_runner._router_diagnostics",
                            return_value=self._available_router_diagnostics(),
                        ):
                            with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
                                summary = run_hacc_adversarial_batch(
                                    output_dir=tmpdir,
                                    num_sessions=1,
                                    max_turns=1,
                                    max_parallel=1,
                                    hacc_preset="core_hacc_policies",
                                    demo=True,
                                    emit_autopatch=True,
                                    use_recommended_autopatch_targets=True,
                                )

            autopatch_kwargs = autopatch_mock.call_args.kwargs
            self.assertTrue(summary["autopatch"]["requested"])
            self.assertTrue(summary["autopatch"]["used_recommended_targets"])
            self.assertEqual(summary["autopatch"]["requested_profile"], "question_flow")
            self.assertTrue(any(str(path).endswith("complaint_phases/phase_manager.py") for path in summary["autopatch"]["requested_target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/inquiries.py") for path in summary["autopatch"]["requested_target_files"]))
            self.assertEqual(summary["autopatch"]["profile"], "custom")
            self.assertTrue(any(str(path).endswith("adversarial_harness/session.py") for path in summary["autopatch"]["target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/mediator.py") for path in summary["autopatch"]["target_files"]))
            self.assertTrue(any(str(path).endswith("adversarial_harness/complainant.py") for path in summary["autopatch"]["target_files"]))
            self.assertTrue(any(str(path).endswith("adversarial_harness/session.py") for path in autopatch_kwargs["target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/mediator.py") for path in autopatch_kwargs["target_files"]))
            self.assertTrue(any(str(path).endswith("adversarial_harness/complainant.py") for path in autopatch_kwargs["target_files"]))

    def test_runner_reports_autopatch_preflight_failure_without_calling_optimizer(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        runtime_bundle = self._build_fake_demo_runtime_bundle()

        import adversarial_harness.optimizer as optimizer_module

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(
                optimizer_module.Optimizer,
                "_load_agentic_optimizer_components",
                side_effect=RuntimeError("No module named 'cachetools'"),
            ):
                with mock.patch.object(
                    optimizer_module.Optimizer,
                    "run_agentic_autopatch",
                ) as autopatch_mock:
                    with mock.patch(
                        "hacc_adversarial_runner._router_diagnostics",
                        return_value=self._available_router_diagnostics(),
                    ):
                        with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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
        self.assertFalse(summary["autopatch"]["success"])
        self.assertEqual(summary["autopatch"]["preflight"]["ready"], False)
        self.assertIn("cachetools", str(summary["autopatch"]["preflight"]["error"]))
        self.assertIn("Autopatch dependency preflight failed", str(summary["autopatch"]["error"]))
        autopatch_mock.assert_not_called()

    def test_demo_runner_uses_demo_patch_optimizer_for_autopatch(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        runtime_bundle = self._build_fake_demo_runtime_bundle()

        import adversarial_harness.demo_autopatch as demo_autopatch_module
        import adversarial_harness.optimizer as optimizer_module

        captured_optimizer = {}

        class FakeDemoPatchOptimizer:
            def __init__(self, *, project_root, output_dir, marker_prefix):
                captured_optimizer["project_root"] = str(project_root)
                captured_optimizer["output_dir"] = str(output_dir)
                captured_optimizer["marker_prefix"] = marker_prefix

            def optimize(self, task):
                patch_path = Path(captured_optimizer["output_dir"]) / "demo.patch"
                patch_path.parent.mkdir(parents=True, exist_ok=True)
                patch_path.write_text("demo patch", encoding="utf-8")
                return SimpleNamespace(
                    success=True,
                    patch_path=patch_path,
                    patch_cid="demo-cid",
                    metadata={"demo": True},
                )

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(demo_autopatch_module, "DemoPatchOptimizer", FakeDemoPatchOptimizer):
                with mock.patch(
                    "hacc_adversarial_runner._router_diagnostics",
                    return_value=self._available_router_diagnostics(),
                ):
                    with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
                        with mock.patch(
                            "hacc_adversarial_runner._agentic_autopatch_preflight",
                            return_value={"ready": True, "error": None},
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
        self.assertEqual(summary["autopatch"]["patch_cid"], "demo-cid")
        self.assertEqual(summary["autopatch"]["metadata"]["demo"], True)
        self.assertFalse(summary["autopatch"]["applied"])
        self.assertFalse(summary["autopatch"]["apply_success"])
        self.assertIsNone(summary["autopatch"]["error"])
        self.assertEqual(summary["autopatch"]["validation"]["patch_validation"]["level"], "demo")
        self.assertEqual(captured_optimizer["project_root"], str(complaint_generator_root))
        self.assertTrue(captured_optimizer["output_dir"].endswith("/autopatch"))
        self.assertEqual(captured_optimizer["marker_prefix"], "Demo autopatch recommendation")

    def test_live_runner_uses_llm_router_backend(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        runtime_bundle = self._build_fake_llm_router_runtime_bundle(provider="copilot_cli", model="gpt-5-mini")

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

        runtime_bundle["mediator_factory"] = lambda **kwargs: FakeMediator(**kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(llm_router_backend_module, "generate_text", side_effect=fake_generate_text):
                with mock.patch.object(mediator_module, "Mediator", FakeMediator):
                    with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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

        runtime_bundle = self._build_fake_llm_router_runtime_bundle(provider="copilot_cli", model="gpt-5-mini")

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

        runtime_bundle["mediator_factory"] = lambda **kwargs: FakeMediator(**kwargs)

        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(llm_router_backend_module, "generate_text", side_effect=fake_generate_text):
                with mock.patch.object(mediator_module, "Mediator", FakeMediator):
                    with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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

        runtime_bundle = self._build_fake_demo_runtime_bundle()

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
                    with mock.patch.object(
                        optimizer_module.Optimizer,
                        "_recommended_target_files_for_report",
                        return_value=[
                            "complaint_phases/phase_manager.py",
                            "mediator/inquiries.py",
                        ],
                    ):
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
                            with mock.patch(
                                "hacc_adversarial_runner._router_diagnostics",
                                return_value=self._available_router_diagnostics(),
                            ):
                                with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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
            self.assertEqual(summary["autopatch"]["recommended_profile"], "question_flow")
            self.assertTrue(any(str(path).endswith("complaint_phases/phase_manager.py") for path in summary["autopatch"]["recommended_target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/inquiries.py") for path in summary["autopatch"]["recommended_target_files"]))
            self.assertGreaterEqual(len(autopatch_kwargs["target_files"]), 2)
            self.assertTrue(any(str(path).endswith("complaint_phases/phase_manager.py") for path in autopatch_kwargs["target_files"]))
            self.assertTrue(any(str(path).endswith("mediator/inquiries.py") for path in autopatch_kwargs["target_files"]))

    def test_runner_auto_applies_valid_patch_by_default(self) -> None:
        complaint_generator_root = REPO_ROOT / "complaint-generator"
        if str(complaint_generator_root) not in sys.path:
            sys.path.insert(0, str(complaint_generator_root))

        runtime_bundle = self._build_fake_demo_runtime_bundle()
        runtime_bundle["runtime"] = {"mode": "llm_router", "provider": "copilot_cli", "model": "gpt-5-mini"}

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
                            with mock.patch(
                                "hacc_adversarial_runner._router_diagnostics",
                                return_value=self._available_router_diagnostics(),
                            ):
                                with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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

        runtime_bundle = self._build_fake_demo_runtime_bundle()
        runtime_bundle["runtime"] = {"mode": "llm_router", "provider": "copilot_cli", "model": "gpt-5-mini"}

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
                            with mock.patch(
                                "hacc_adversarial_runner._router_diagnostics",
                                return_value=self._available_router_diagnostics(),
                            ):
                                with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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

        runtime_bundle = self._build_fake_demo_runtime_bundle()
        runtime_bundle["runtime"] = {"mode": "llm_router", "provider": "copilot_cli", "model": "gpt-5-mini"}

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
                        with mock.patch(
                            "hacc_adversarial_runner._router_diagnostics",
                            return_value=self._available_router_diagnostics(),
                        ):
                            with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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

        runtime_bundle = self._build_fake_demo_runtime_bundle()
        runtime_bundle["runtime"] = {"mode": "llm_router", "provider": "copilot_cli", "model": "gpt-5-mini"}

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
                                with mock.patch(
                                    "hacc_adversarial_runner._router_diagnostics",
                                    return_value=self._available_router_diagnostics(),
                                ):
                                    with mock.patch("hacc_adversarial_runner._load_runtime", return_value=runtime_bundle):
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
