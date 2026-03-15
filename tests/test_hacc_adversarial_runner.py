import json
import tempfile
import unittest
from pathlib import Path
import sys
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_adversarial_runner import run_hacc_adversarial_batch


class HACCAdversarialRunnerTests(unittest.TestCase):
    def test_demo_runner_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            summary = run_hacc_adversarial_batch(
                output_dir=tmpdir,
                num_sessions=1,
                max_turns=2,
                max_parallel=1,
                hacc_preset="core_hacc_policies",
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
            self.assertEqual(summary["router_diagnostics"]["embeddings_router"]["status"], "success")
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


if __name__ == "__main__":
    unittest.main()
