import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import hacc_grounded_pipeline as pipeline


class HACCGroundedPipelineTests(unittest.TestCase):
    def test_run_grounded_pipeline_preserves_package_search_summary_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_grounding = {
                "status": "success",
                "query": "retaliation grievance appeal",
                "claim_type": "housing_discrimination",
                "search_summary": {
                    "requested_search_mode": "package",
                    "requested_use_vector": False,
                    "effective_search_mode": "lexical_only",
                    "fallback_note": "Requested package/shared hybrid search, but vector support is unavailable; using lexical results instead.",
                },
                "anchor_sections": [],
                "anchor_passages": [],
                "upload_candidates": [],
                "mediator_evidence_packets": [],
                "synthetic_prompts": {},
            }
            fake_upload = {
                "status": "success",
                "upload_count": 0,
                "uploads": [],
                "search_summary": {
                    "requested_search_mode": "package",
                    "requested_use_vector": False,
                    "effective_search_mode": "lexical_only",
                    "fallback_note": "Requested package/shared hybrid search, but vector support is unavailable; using lexical results instead.",
                },
            }
            fake_adversarial_summary = {
                "search_summary": {
                    "requested_search_mode": "package",
                    "requested_use_vector": False,
                    "effective_search_mode": "lexical_fallback",
                    "fallback_note": "Requested package/shared hybrid search, but vector support is unavailable; using lexical results instead. Vector backend detail: numpy is required for local vector persistence and search",
                },
                "statistics": {"successful_sessions": 1, "total_sessions": 1},
                "best_complaint": {"score": 0.91},
                "artifacts": {"output_dir": str(Path(tmpdir) / "adversarial")},
            }

            with mock.patch.object(pipeline, "HACCResearchEngine") as engine_cls:
                engine = engine_cls.return_value
                engine.build_grounding_bundle.return_value = fake_grounding
                engine.simulate_evidence_upload.return_value = fake_upload
                with mock.patch.object(pipeline, "run_hacc_adversarial_batch", return_value=fake_adversarial_summary):
                    summary = pipeline.run_hacc_grounded_pipeline(
                        output_dir=tmpdir,
                        hacc_preset="core_hacc_policies",
                        hacc_search_mode="package",
                        use_hacc_vector_search=False,
                        demo=True,
                    )

            summary_payload = json.loads((Path(tmpdir) / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["search_summary"]["grounding"]["requested_search_mode"], "package")
            self.assertEqual(summary["search_summary"]["grounding"]["effective_search_mode"], "lexical_only")
            self.assertIn("Requested package/shared hybrid search", summary["search_summary"]["grounding"]["fallback_note"])
            self.assertEqual(summary["search_summary"]["adversarial"]["effective_search_mode"], "lexical_fallback")
            self.assertEqual(summary_payload["search_summary"]["grounding"], summary["search_summary"]["grounding"])
            self.assertEqual(summary_payload["search_summary"]["evidence_upload"], summary["search_summary"]["evidence_upload"])
            self.assertEqual(summary_payload["search_summary"]["adversarial"], summary["search_summary"]["adversarial"])

    def test_run_grounded_pipeline_preserves_hybrid_search_summary_in_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_grounding = {
                "status": "success",
                "query": "retaliation grievance appeal",
                "claim_type": "housing_discrimination",
                "search_summary": {
                    "requested_search_mode": "hybrid",
                    "requested_use_vector": True,
                    "effective_search_mode": "lexical_only",
                    "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead.",
                },
                "anchor_sections": [],
                "anchor_passages": [],
                "upload_candidates": [],
                "mediator_evidence_packets": [],
                "synthetic_prompts": {},
            }
            fake_upload = {
                "status": "success",
                "upload_count": 0,
                "uploads": [],
                "search_summary": {
                    "requested_search_mode": "hybrid",
                    "requested_use_vector": True,
                    "effective_search_mode": "lexical_only",
                    "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead.",
                },
            }
            fake_adversarial_summary = {
                "search_summary": {
                    "requested_search_mode": "hybrid",
                    "requested_use_vector": True,
                    "effective_search_mode": "lexical_only",
                    "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead. Vector backend detail: numpy is required for local vector persistence and search",
                },
                "statistics": {"successful_sessions": 1, "total_sessions": 1},
                "best_complaint": {"score": 0.91},
                "artifacts": {"output_dir": str(Path(tmpdir) / "adversarial")},
            }

            with mock.patch.object(pipeline, "HACCResearchEngine") as engine_cls:
                engine = engine_cls.return_value
                engine.build_grounding_bundle.return_value = fake_grounding
                engine.simulate_evidence_upload.return_value = fake_upload
                with mock.patch.object(pipeline, "run_hacc_adversarial_batch", return_value=fake_adversarial_summary):
                    summary = pipeline.run_hacc_grounded_pipeline(
                        output_dir=tmpdir,
                        hacc_preset="core_hacc_policies",
                        hacc_search_mode="hybrid",
                        use_hacc_vector_search=True,
                        demo=True,
                    )

            summary_payload = json.loads((Path(tmpdir) / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["search_summary"]["grounding"]["requested_search_mode"], "hybrid")
            self.assertTrue(summary["search_summary"]["grounding"]["requested_use_vector"])
            self.assertEqual(summary["search_summary"]["grounding"]["effective_search_mode"], "lexical_only")
            self.assertIn("Requested hybrid search", summary["search_summary"]["grounding"]["fallback_note"])
            self.assertEqual(summary["search_summary"]["adversarial"]["effective_search_mode"], "lexical_only")
            self.assertEqual(summary_payload["search_summary"]["grounding"], summary["search_summary"]["grounding"])
            self.assertEqual(summary_payload["search_summary"]["evidence_upload"], summary["search_summary"]["evidence_upload"])
            self.assertEqual(summary_payload["search_summary"]["adversarial"], summary["search_summary"]["adversarial"])

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
                "retrieval_support_bundle": {"summary": {"total_records": 1}},
                "synthetic_prompts": {
                    "evidence_upload_prompts": [{"text": "Upload README.md"}],
                    "complaint_chatbot_prompt": "Ground the chatbot.",
                    "mediator_evaluation_prompt": "Evaluate the upload.",
                    "court_complaint_synthesis_prompt": "Synthesize the complaint.",
                },
            }
            fake_upload = {
                "status": "success",
                "upload_count": 1,
                "uploads": [{"title": "README"}],
                "support_summary": {"total_links": 1},
                "retrieval_support_bundle": {"summary": {"total_records": 1}},
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
            self.assertTrue((output_root / "grounding_overview.json").is_file())
            self.assertTrue((output_root / "anchor_passages.json").is_file())
            self.assertTrue((output_root / "upload_candidates.json").is_file())
            self.assertTrue((output_root / "synthetic_prompts.json").is_file())
            self.assertTrue((output_root / "retrieval_support_bundle.json").is_file())
            self.assertTrue((output_root / "evidence_upload_report.json").is_file())
            self.assertTrue((output_root / "adversarial_summary.json").is_file())
            self.assertTrue((output_root / "run_summary.json").is_file())
            self.assertEqual(summary["grounding_query"], "reasonable accommodation hearing rights")
            self.assertEqual(summary["hacc_search_mode"], "hybrid")
            self.assertEqual(summary["evidence_upload"]["upload_count"], 1)
            self.assertEqual(summary["adversarial"]["best_complaint"]["score"], 0.91)
            self.assertEqual(summary["grounding"]["anchor_sections"], ["reasonable_accommodation", "grievance_hearing"])
            self.assertEqual(summary["grounding_overview"]["anchor_passage_count"], 1)
            self.assertEqual(summary["grounding_overview"]["upload_candidate_count"], 1)
            self.assertEqual(summary["grounding_overview"]["uploaded_evidence_count"], 1)
            self.assertEqual(summary["grounding_overview"]["top_documents"], ["README"])
            self.assertEqual(summary["artifacts"]["grounding_overview_json"], str(output_root / "grounding_overview.json"))
            self.assertEqual(summary["artifacts"]["retrieval_support_bundle_json"], str(output_root / "retrieval_support_bundle.json"))
            self.assertEqual(batch_mock.call_args.kwargs["hacc_search_mode"], "hybrid")

            prompts_payload = json.loads((output_root / "synthetic_prompts.json").read_text(encoding="utf-8"))
            self.assertIn("evidence_upload_prompts", prompts_payload)
            self.assertIn("court_complaint_synthesis_prompt", prompts_payload)
            retrieval_payload = json.loads((output_root / "retrieval_support_bundle.json").read_text(encoding="utf-8"))
            self.assertEqual(retrieval_payload["summary"]["total_records"], 1)
            overview_payload = json.loads((output_root / "grounding_overview.json").read_text(encoding="utf-8"))
            self.assertEqual(overview_payload["anchor_sections"], ["reasonable_accommodation", "grievance_hearing"])
            anchor_passages_payload = json.loads((output_root / "anchor_passages.json").read_text(encoding="utf-8"))
            self.assertEqual(anchor_passages_payload[0]["title"], "README")
            upload_candidates_payload = json.loads((output_root / "upload_candidates.json").read_text(encoding="utf-8"))
            self.assertEqual(upload_candidates_payload[0]["relative_path"], "README.md")

    def test_run_grounded_pipeline_defaults_to_codex_provider_and_model(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            fake_grounding = {
                "status": "success",
                "query": "reasonable accommodation hearing rights",
                "claim_type": "housing_discrimination",
                "anchor_sections": [],
                "anchor_passages": [],
                "upload_candidates": [],
                "synthetic_prompts": {},
            }
            fake_upload = {
                "status": "success",
                "upload_count": 0,
                "uploads": [],
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
                    pipeline.run_hacc_grounded_pipeline(
                        output_dir=tmpdir,
                        hacc_preset="core_hacc_policies",
                        demo=False,
                    )

        self.assertEqual(batch_mock.call_args.kwargs["provider"], pipeline.HACC_DEFAULT_PROVIDER)
        self.assertEqual(batch_mock.call_args.kwargs["model"], pipeline.HACC_DEFAULT_MODEL)

    def test_run_grounded_pipeline_can_trigger_complaint_synthesis(self) -> None:
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
                    def fake_synthesize(**kwargs):
                        grounded_run_dir = Path(kwargs["grounded_run_dir"])
                        self.assertTrue((grounded_run_dir / "grounding_bundle.json").is_file())
                        self.assertTrue((grounded_run_dir / "grounding_overview.json").is_file())
                        self.assertTrue((grounded_run_dir / "evidence_upload_report.json").is_file())
                        overview_payload = json.loads((grounded_run_dir / "grounding_overview.json").read_text(encoding="utf-8"))
                        self.assertEqual(overview_payload["anchor_sections"], ["reasonable_accommodation", "grievance_hearing"])
                        return fake_synthesis

                    with mock.patch.object(pipeline, "_run_complaint_synthesis", side_effect=fake_synthesize) as synth_mock:
                        summary = pipeline.run_hacc_grounded_pipeline(
                            output_dir=tmpdir,
                            query="reasonable accommodation hearing rights",
                            hacc_preset="core_hacc_policies",
                            demo=True,
                            synthesize_complaint=True,
                            filing_forum="hud",
                        )

            synth_mock.assert_called_once()
            self.assertEqual(summary["complaint_synthesis"]["draft_complaint_package_json"], fake_synthesis["draft_complaint_package_json"])
            self.assertEqual(summary["artifacts"]["draft_complaint_package_md"], fake_synthesis["draft_complaint_package_md"])


if __name__ == "__main__":
    unittest.main()
