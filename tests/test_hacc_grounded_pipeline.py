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
                "evidence_summary": "Reasonable accommodation policy language supporting hearing rights.",
                "anchor_sections": ["reasonable_accommodation", "grievance_hearing"],
                "anchor_passages": [
                    {
                        "title": "README",
                        "snippet": "Residents may request an informal hearing as an accommodation-related safeguard.",
                        "section_labels": ["reasonable_accommodation", "grievance_hearing"],
                    }
                ],
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
                ) as batch_mock:
                    summary = pipeline.run_hacc_grounded_pipeline(
                        output_dir=tmpdir,
                        query="reasonable accommodation hearing rights",
                        hacc_preset="core_hacc_policies",
                        hacc_search_mode="hybrid",
                        demo=True,
                    )

            output_root = Path(tmpdir)
            self.assertTrue((output_root / "grounding_bundle.json").is_file())
            self.assertTrue((output_root / "synthetic_prompts.json").is_file())
            self.assertTrue((output_root / "evidence_upload_report.json").is_file())
            self.assertTrue((output_root / "adversarial_summary.json").is_file())
            self.assertTrue((output_root / "run_summary.json").is_file())
            self.assertEqual(summary["grounding_query"], "reasonable accommodation hearing rights")
            self.assertEqual(summary["hacc_search_mode"], "hybrid")
            self.assertEqual(summary["evidence_upload"]["upload_count"], 1)
            self.assertEqual(summary["adversarial"]["best_complaint"]["score"], 0.91)
            self.assertEqual(summary["grounding"]["anchor_sections"], ["reasonable_accommodation", "grievance_hearing"])
            self.assertEqual(batch_mock.call_args.kwargs["hacc_search_mode"], "hybrid")

            prompts_payload = json.loads((output_root / "synthetic_prompts.json").read_text(encoding="utf-8"))
            self.assertIn("evidence_upload_prompts", prompts_payload)

    def test_run_grounded_pipeline_can_trigger_complaint_synthesis(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_grounding = {
                "status": "success",
                "query": "reasonable accommodation hearing rights",
                "claim_type": "housing_discrimination",
                "upload_candidates": [],
                "mediator_evidence_packets": [],
                "synthetic_prompts": {},
            }
            fake_upload = {
                "status": "success",
                "upload_count": 0,
                "uploads": [],
                "support_summary": {},
                "synthetic_prompts": {},
            }
            fake_adversarial_summary = {
                "statistics": {"successful_sessions": 1, "total_sessions": 1},
                "best_complaint": {"score": 0.91},
                "artifacts": {"output_dir": str(Path(tmpdir) / "adversarial")},
            }
            fake_synthesis = {
                "output_dir": str(Path(tmpdir) / "complaint_synthesis"),
                "draft_complaint_package_json": str(Path(tmpdir) / "complaint_synthesis" / "draft_complaint_package.json"),
                "draft_complaint_package_md": str(Path(tmpdir) / "complaint_synthesis" / "draft_complaint_package.md"),
                "intake_follow_up_worksheet_json": str(Path(tmpdir) / "complaint_synthesis" / "intake_follow_up_worksheet.json"),
                "intake_follow_up_worksheet_md": str(Path(tmpdir) / "complaint_synthesis" / "intake_follow_up_worksheet.md"),
            }
            completed_worksheet = str(Path(tmpdir) / "completed_intake_follow_up_worksheet.json")

            with mock.patch.object(pipeline, "HACCResearchEngine") as engine_cls:
                engine = engine_cls.return_value
                engine.build_grounding_bundle.return_value = fake_grounding
                engine.simulate_evidence_upload.return_value = fake_upload
                with mock.patch.object(
                    pipeline,
                    "run_hacc_adversarial_batch",
                    return_value=fake_adversarial_summary,
                ):
                    with mock.patch.object(pipeline, "_run_complaint_synthesis", return_value=fake_synthesis) as synth_mock:
                        summary = pipeline.run_hacc_grounded_pipeline(
                            output_dir=tmpdir,
                            query="reasonable accommodation hearing rights",
                            hacc_preset="core_hacc_policies",
                            demo=True,
                            synthesize_complaint=True,
                            filing_forum="hud",
                            completed_intake_worksheet=completed_worksheet,
                        )

            synth_mock.assert_called_once()
            self.assertEqual(synth_mock.call_args.kwargs["completed_intake_worksheet"], completed_worksheet)
            self.assertEqual(summary["complaint_synthesis"]["draft_complaint_package_json"], fake_synthesis["draft_complaint_package_json"])
            self.assertEqual(summary["artifacts"]["draft_complaint_package_md"], fake_synthesis["draft_complaint_package_md"])
            self.assertEqual(summary["artifacts"]["intake_follow_up_worksheet_json"], fake_synthesis["intake_follow_up_worksheet_json"])


if __name__ == "__main__":
    unittest.main()
