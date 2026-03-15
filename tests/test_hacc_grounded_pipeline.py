import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import hacc_grounded_pipeline as pipeline


class HACCGroundedPipelineTests(unittest.TestCase):
    def test_run_grounded_pipeline_writes_expected_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_grounding = {
                "status": "success",
                "query": "reasonable accommodation hearing rights",
                "claim_type": "housing_discrimination",
                "upload_candidates": [
                    {
                        "title": "README",
                        "relative_path": "README.md",
                        "source_path": "/tmp/README.md",
                    }
                ],
                "synthetic_prompts": {
                    "evidence_upload_prompts": [{"text": "Upload README.md"}],
                    "complaint_chatbot_prompt": "Ground the chatbot.",
                    "mediator_evaluation_prompt": "Evaluate the upload.",
                },
            }
            fake_upload = {
                "status": "success",
                "upload_count": 1,
                "uploads": [{"title": "README"}],
                "support_summary": {"total_links": 1},
                "synthetic_prompts": fake_grounding["synthetic_prompts"],
            }
            fake_adversarial_summary = {
                "statistics": {"successful_sessions": 1, "total_sessions": 1},
                "best_complaint": {"score": 0.91},
                "artifacts": {"output_dir": str(Path(tmpdir) / "adversarial")},
            }

            with mock.patch.object(pipeline, "HACCResearchEngine") as engine_cls:
                engine = engine_cls.return_value
                engine.build_grounding_bundle.return_value = fake_grounding
                engine.simulate_evidence_upload.return_value = fake_upload
                with mock.patch.object(
                    pipeline,
                    "run_hacc_adversarial_batch",
                    return_value=fake_adversarial_summary,
                ):
                    summary = pipeline.run_hacc_grounded_pipeline(
                        output_dir=tmpdir,
                        query="reasonable accommodation hearing rights",
                        hacc_preset="core_hacc_policies",
                        demo=True,
                    )

            output_root = Path(tmpdir)
            self.assertTrue((output_root / "grounding_bundle.json").is_file())
            self.assertTrue((output_root / "synthetic_prompts.json").is_file())
            self.assertTrue((output_root / "evidence_upload_report.json").is_file())
            self.assertTrue((output_root / "adversarial_summary.json").is_file())
            self.assertTrue((output_root / "run_summary.json").is_file())
            self.assertEqual(summary["grounding_query"], "reasonable accommodation hearing rights")
            self.assertEqual(summary["evidence_upload"]["upload_count"], 1)
            self.assertEqual(summary["adversarial"]["best_complaint"]["score"], 0.91)

            prompts_payload = json.loads((output_root / "synthetic_prompts.json").read_text(encoding="utf-8"))
            self.assertIn("evidence_upload_prompts", prompts_payload)


if __name__ == "__main__":
    unittest.main()