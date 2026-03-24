from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from hacc_research import HACCResearchEngine
from hacc_research import engine as engine_module


class HACCResearchEngineTests(unittest.TestCase):
    def test_load_corpus_includes_repository_evidence_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("README.md").write_text(
                "Repository Evidence\nReasonable accommodation notices must be reviewable.",
                encoding="utf-8",
            )
            correspondence_dir = root / "correspondances"
            correspondence_dir.mkdir(parents=True, exist_ok=True)
            correspondence_dir.joinpath("notice.txt").write_text(
                "Notice of adverse action and hearing rights.",
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            documents = engine.load_corpus()

            repository_docs = [document for document in documents if document.source_type == "repository_evidence"]
            self.assertEqual(len(repository_docs), 2)
            self.assertEqual(
                {document.document_id for document in repository_docs},
                {"repo::README.md", "repo::correspondances/notice.txt"},
            )
            readme_doc = next(document for document in repository_docs if document.document_id == "repo::README.md")
            self.assertEqual(readme_doc.metadata["document_ingest_status"], "success")
            self.assertTrue(readme_doc.metadata["parse_summary"])
            self.assertTrue(readme_doc.entities)
            self.assertTrue(readme_doc.rules)

    def test_repository_text_evidence_does_not_require_ingest_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            evidence_path = root / "README.md"
            evidence_path.write_text(
                "Repository Evidence\nReasonable accommodation hearing rights and written notice.",
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            with mock.patch.object(
                engine_module,
                "ingest_local_document",
                side_effect=AssertionError("plain text repository evidence should not hit ingest adapter"),
            ):
                documents = engine.load_corpus(force_reload=True)

            repository_docs = [document for document in documents if document.source_type == "repository_evidence"]
            self.assertEqual(len(repository_docs), 1)
            self.assertIn("hearing rights", repository_docs[0].text.lower())

    def test_load_corpus_skips_generated_runtime_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("README.md").write_text("Source evidence", encoding="utf-8")
            generated_dir = root / "research_results" / "adversarial_runs" / "demo"
            generated_dir.mkdir(parents=True, exist_ok=True)
            generated_dir.joinpath("run_summary.json").write_text(
                json.dumps({"status": "generated"}),
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            documents = engine.load_corpus()
            self.assertEqual(
                [document.document_id for document in documents if document.source_type == "repository_evidence"],
                ["repo::README.md"],
            )

    def test_load_corpus_reads_parsed_and_knowledge_graph_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            text_path = parsed_dir / "doc1.txt"
            text_path.write_text(
                "Reasonable Accommodation Policy\nHACC must approve accommodations when required.",
                encoding="utf-8",
            )
            text_path.with_suffix(".json").write_text(
                json.dumps({"title": "Parsed Accommodation Policy", "source": "unit_test"}),
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(
                    {
                        "parsed_documents": [
                            {
                                "parsed_text_path": "research_results/documents/parsed/doc1.txt",
                                "pdf_path": "research_results/documents/raw/doc1.pdf",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("kg1.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "kg1",
                        "text": "Housing search assistance must include reasonable accommodation support.",
                        "document": {
                            "title": "Knowledge Graph Housing Policy",
                            "source_path": "/tmp/kg1.pdf",
                        },
                        "rules": [
                            {
                                "text": "Housing search assistance must include reasonable accommodation support.",
                                "rule_type": "obligation",
                                "section_title": "Housing Search Assistance",
                            }
                        ],
                        "entities": [{"id": "entity1", "type": "concept", "name": "reasonable accommodation"}],
                        "relationships": [],
                        "metadata": {"provider": "ipfs_datasets_py"},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            documents = engine.load_corpus()

            self.assertEqual(len(documents), 2)
            self.assertEqual({document.source_type for document in documents}, {"parsed_document", "knowledge_graph"})

    def test_build_index_writes_summary_and_records_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            text_path = parsed_dir / "doc1.txt"
            text_path.write_text("Fair Housing Policy\nHousing programs must remain accessible.", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps({"parsed_documents": [{"parsed_text_path": "research_results/documents/parsed/doc1.txt"}]}),
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            output_path = root / "research_results/search_index.json"
            payload = engine.build_index(output_path=output_path)

            self.assertEqual(payload["status"], "success")
            self.assertTrue(output_path.exists())
            self.assertTrue(Path(payload["records_path"]).exists())
            self.assertTrue(Path(payload["manifest_path"]).exists())

    def test_search_prioritizes_rule_and_entity_matches(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("housing_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "housing_policy",
                        "text": "HACC must approve additional search time if needed as a reasonable accommodation.",
                        "document": {
                            "title": "Housing Search Accommodation Policy",
                            "source_path": "/tmp/housing_policy.pdf",
                        },
                        "rules": [
                            {
                                "text": "HACC must approve additional search time if needed as a reasonable accommodation.",
                                "rule_type": "obligation",
                                "section_title": "Voucher Search Term",
                            }
                        ],
                        "entities": [
                            {"id": "entity1", "type": "concept", "name": "reasonable accommodation"},
                            {"id": "entity2", "type": "concept", "name": "search time"},
                        ],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )
            kg_dir.joinpath("procurement_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "procurement_policy",
                        "text": "Procurement staff may review vendor paperwork before approval.",
                        "document": {
                            "title": "Procurement Review Policy",
                            "source_path": "/tmp/procurement_policy.pdf",
                        },
                        "rules": [],
                        "entities": [{"id": "entity3", "type": "concept", "name": "vendor paperwork"}],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            result = engine.search_local("reasonable accommodation search time", top_k=2)

            self.assertEqual(result["results"][0]["document_id"], "housing_policy")
            self.assertTrue(result["results"][0]["matched_rules"])
            self.assertTrue(result["results"][0]["matched_entities"])

    def test_search_public_method_exposes_capability_status(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("housing_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "housing_policy",
                        "text": "Reasonable accommodation support is available.",
                        "document": {
                            "title": "Housing Policy",
                            "source_path": "/tmp/housing_policy.pdf",
                        },
                        "rules": [],
                        "entities": [],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            result = engine.search("reasonable accommodation", top_k=1)

            self.assertEqual(result["status"], "success")
            self.assertIn("integration_status", result)
            self.assertIn("capabilities", result["integration_status"])
            self.assertIn("capability_report", result["integration_status"])

    def test_document_chronology_metadata_skips_shared_parser_for_large_text(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            long_text = ("HACC sent written notice on January 4, 2024 " + ("timeline " * 1200)).strip()
            with mock.patch.object(engine_module, "build_shared_temporal_context", side_effect=AssertionError("shared parser should be skipped")):
                payload = engine._build_document_chronology_metadata(
                    long_text,
                    title="Long chronology",
                    source_path="/tmp/long.txt",
                )

            self.assertEqual(payload["timeline_anchor_count"], 1)
            self.assertEqual(payload["timeline_anchor_preview"][0]["start_date"], "2024-01-04")

    def test_extract_timeline_anchors_skips_policy_revision_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            text = (
                "ADMINISTRATIVE PLAN Revision Date May 1, 2005 February 1, 2006 October 1, 2006. "
                "HACC sent written notice on March 4, 2024 and denied the review on March 8, 2024."
            )
            with mock.patch.object(engine_module, "build_shared_temporal_context", None):
                anchors = engine._extract_timeline_anchors_from_text(
                    text,
                    title="Administrative Plan",
                    source_path="/tmp/policy.txt",
                    claim_type="housing_discrimination",
                )

            self.assertEqual([anchor["start_date"] for anchor in anchors], ["2024-03-04", "2024-03-08"])

    def test_shared_timeline_extraction_skips_policy_revision_sentences(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            text = (
                "ADMINISTRATIVE PLAN Revision Date May 1, 2005 February 1, 2006 October 1, 2006. "
                "HACC sent written notice on March 4, 2024."
            )

            def fake_temporal_context(sentence, fallback_text=None):
                self.assertNotIn("Revision Date", sentence)
                if "March 4, 2024" in sentence:
                    return {
                        "start_date": "2024-03-04",
                        "matched_text": "March 4, 2024",
                        "granularity": "day",
                    }
                return {}

            with mock.patch.object(engine_module, "build_shared_temporal_context", side_effect=fake_temporal_context):
                anchors = engine._extract_shared_timeline_anchors_from_text(
                    text,
                    title="Administrative Plan",
                    source_path="/tmp/policy.txt",
                    claim_type="housing_discrimination",
                )

            self.assertEqual(len(anchors), 1)
            self.assertEqual(anchors[0]["start_date"], "2024-03-04")

    def test_extract_timeline_anchors_skips_regulatory_history_dates(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            text = (
                "Plan 7/1/2025 Administrative Plan -Table of Contents Chapter 2 FAIR HOUSING. "
                "On September 29, 2023, HUD issued Notice PIH 2023-27. "
                "HACC sent the tenant a written notice of denial on March 4, 2024."
            )
            with mock.patch.object(engine_module, "build_shared_temporal_context", None):
                anchors = engine._extract_timeline_anchors_from_text(
                    text,
                    title="Administrative Plan",
                    source_path="/tmp/policy.txt",
                    claim_type="housing_discrimination",
                )

            self.assertEqual([anchor["start_date"] for anchor in anchors], ["2024-03-04"])

    def test_grounding_chronology_uses_full_text_only_for_repository_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            knowledge_graph_candidate = {
                "title": "Administrative Plan",
                "source_path": "/tmp/policy.pdf",
                "source_type": "knowledge_graph",
                "snippet": "Hearing rights and appeal procedures.",
            }
            repository_candidate = {
                "title": "Tenant Notice",
                "source_path": "/tmp/tenant_notice.txt",
                "source_type": "repository_evidence",
                "snippet": "Written notice details.",
            }

            upload_texts = {
                "/tmp/policy.pdf": "Revision Date May 1, 2005 February 1, 2006 October 1, 2006.",
                "/tmp/tenant_notice.txt": "HACC sent the tenant a written notice on March 4, 2024 and denied review on March 8, 2024.",
            }

            with mock.patch.object(engine, "_resolve_candidate_upload_text", side_effect=lambda candidate: upload_texts[str(candidate.get("source_path"))]):
                analysis = engine._build_grounding_chronology_analysis(
                    [knowledge_graph_candidate, repository_candidate],
                    claim_type="housing_discrimination",
                    query_text="hearing appeal notice",
                )

            self.assertEqual([anchor["start_date"] for anchor in analysis["timeline_anchors"]], ["2024-03-04"])
            self.assertEqual(analysis["timeline_anchor_count"], 1)

    def test_document_chronology_metadata_uses_focused_text_for_knowledge_graph_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            raw_text = (
                "ADMINISTRATIVE PLAN FOR THE HOUSING AUTHORITY Effective: July 1, 2025 Approved by the HA Board. "
                "Revision Date May 1, 2005 February 1, 2006 October 1, 2006."
            )
            metadata = engine._build_document_chronology_metadata(
                raw_text,
                title="Administrative Plan",
                source_path="/tmp/policy.pdf",
                source_type="knowledge_graph",
                rules=[{"text": "The tenant may request an informal review of the decision."}],
                entities=[{"name": "informal review"}],
            )

            self.assertEqual(metadata["timeline_anchor_count"], 0)
            self.assertEqual(metadata["timeline_anchor_preview"], [])

    def test_build_grounding_bundle_emits_synthetic_prompts_for_file_backed_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("README.md").write_text(
                "Reasonable Accommodation Policy\nUploadable repository evidence about hearing rights.",
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            with mock.patch.object(
                engine,
                "discover",
                return_value={
                    "status": "success",
                    "result_count": 1,
                    "results": [{"title": "Tenant advocacy article", "url": "https://example.com/article"}],
                },
            ), mock.patch.object(
                engine,
                "discover_legal_authorities",
                return_value={
                    "status": "success",
                    "result_count": 1,
                    "results": [{"title": "HUD regulation", "citation": "24 C.F.R. 982.555"}],
                },
            ):
                payload = engine.build_grounding_bundle(
                    "reasonable accommodation hearing rights",
                    top_k=1,
                    claim_type="housing_discrimination",
                    search_mode="lexical",
                )

            self.assertEqual(payload["status"], "success")
            self.assertEqual(len(payload["upload_candidates"]), 1)
            self.assertEqual(payload["upload_candidates"][0]["relative_path"], "README.md")
            self.assertEqual(payload["evidence_summary"], "Reasonable Accommodation Policy Uploadable repository evidence about hearing rights.")
            self.assertEqual(set(payload["anchor_sections"]), {"reasonable_accommodation"})
            self.assertEqual(
                set(payload["anchor_passages"][0]["section_labels"]),
                {"reasonable_accommodation"},
            )
            prompts = payload["synthetic_prompts"]
            self.assertEqual(len(prompts["evidence_upload_prompts"]), 1)
            self.assertIn("Upload the evidence file", prompts["evidence_upload_prompts"][0]["text"])
            self.assertEqual(
                set(prompts["evidence_upload_prompts"][0]["anchor_sections"]),
                {"reasonable_accommodation"},
            )
            self.assertIn("Evaluate each uploaded evidence item", prompts["mediator_evaluation_prompt"])
            self.assertIn("Prioritize these anchor sections", prompts["mediator_evaluation_prompt"])
            self.assertIn("production_upload_prompt", prompts)
            self.assertIn("court_complaint_synthesis_prompt", prompts)
            self.assertIn("evidence_upload_simulation_prompt", prompts)
            self.assertIn("production_evidence_intake_steps", prompts)
            self.assertIn("mediator_upload_checklist", prompts)
            self.assertIn("document_generation_checklist", prompts)
            self.assertIn("evidence_upload_form_seed", prompts)
            self.assertIn("mediator_evidence_review_prompt", prompts)
            self.assertIn("document_generation_prompt", prompts)
            self.assertIn("timeline_consistency_summary", prompts)
            self.assertIn("complaint_manager_interfaces", prompts)
            self.assertEqual(
                prompts["complaint_manager_interfaces"]["package"]["service_class"],
                "ComplaintWorkspaceService",
            )
            self.assertEqual(
                prompts["workflow_phase_priorities"],
                ["intake_questioning", "evidence_upload", "graph_analysis", "document_generation"],
            )
            self.assertIn("actor_role_mapping", prompts["extraction_targets"])
            self.assertIn("document_identifier_mapping", prompts["extraction_targets"])
            self.assertIn("claim_support_mapping", prompts["extraction_targets"])
            self.assertIn("intake_questionnaire_prompt", prompts)
            self.assertIn("What happened, and what adverse action did HACC take", prompts["intake_questionnaire_prompt"])
            self.assertIn("Anchor the intake to these policy sections", prompts["intake_questionnaire_prompt"])
            self.assertEqual(len(prompts["intake_questions"]), 6)
            self.assertEqual(set(prompts["anchor_sections"]), {"reasonable_accommodation"})
            self.assertEqual(prompts["evidence_upload_form_seed"]["claim_type"], "housing_discrimination")
            self.assertEqual(prompts["evidence_upload_form_seed"]["recommended_files"], ["Reasonable Accommodation Policy"])
            self.assertEqual(
                prompts["evidence_upload_form_seed"]["selected_upload_candidates"],
                [
                    {
                        "title": "Reasonable Accommodation Policy",
                        "source_type": "repository_evidence",
                        "relative_path": "README.md",
                        "selection_priority": 0.0,
                        "anchor_sections": ["reasonable_accommodation"],
                    }
                ],
            )
            self.assertIn("claim_support_temporal_handoff", payload)
            self.assertIn("drafting_readiness", payload)
            self.assertIn("document_generation_handoff", payload)
            self.assertIn("graph_completeness_signals", payload)
            self.assertIn("query_context", payload)
            self.assertIn("retrieval_support_bundle", payload)
            self.assertIn("external_research_bundle", payload)
            self.assertIn("complaint_manager_interfaces", payload)
            self.assertEqual(
                payload["external_research_bundle"]["summary"]["top_web_titles"],
                ["Tenant advocacy article"],
            )
            self.assertEqual(
                payload["external_research_bundle"]["summary"]["top_legal_titles"],
                ["24 C.F.R. 982.555"],
            )
            self.assertGreaterEqual(
                int((payload["retrieval_support_bundle"].get("summary") or {}).get("total_records", 0) or 0),
                1,
            )
            self.assertEqual(len(payload["mediator_evidence_packets"]), 1)
            self.assertEqual(payload["mediator_evidence_packets"][0]["relative_path"], "README.md")
            self.assertEqual(
                set(payload["mediator_evidence_packets"][0]["metadata"]["anchor_sections"]),
                {"reasonable_accommodation"},
            )
            self.assertIn("document_text", payload["mediator_evidence_packets"][0])
            self.assertIn("claim_support_temporal_handoff", payload["mediator_evidence_packets"][0]["metadata"])
            self.assertIn("web_evidence_research_prompt", prompts)
            self.assertIn("legal_authority_research_prompt", prompts)
            self.assertIn("24 C.F.R. 982.555", prompts["court_complaint_synthesis_prompt"])

    def test_build_external_research_bundle_aggregates_query_variants_for_legal_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            web_calls = []
            legal_calls = []

            def fake_discover(query, *, max_results=10, engines=None, domain_filter=None, scrape=False):
                web_calls.append(query)
                if "fair housing retaliation" in query.lower():
                    return {
                        "status": "success",
                        "query": query,
                        "result_count": 1,
                        "results": [
                            {
                                "title": "HUD fair housing retaliation guidance",
                                "url": "https://example.org/hud-retaliation",
                            }
                        ],
                    }
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 0,
                    "results": [],
                }

            def fake_discover_legal_authorities(query, *, max_results=10, title=None, court=None, start_date=None, end_date=None):
                legal_calls.append(query)
                if "24 c.f.r. 982.555" in query.lower():
                    return {
                        "status": "success",
                        "query": query,
                        "result_count": 1,
                        "results": [
                            {
                                "title": "Informal hearing for participants",
                                "citation": "24 C.F.R. 982.555",
                                "authority_source": "federal_register",
                            }
                        ],
                    }
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 0,
                    "results": [],
                }

            with mock.patch.object(engine, "discover", side_effect=fake_discover), mock.patch.object(
                engine,
                "discover_legal_authorities",
                side_effect=fake_discover_legal_authorities,
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertGreaterEqual(len(web_calls), 2)
            self.assertGreaterEqual(len(legal_calls), 2)
            self.assertIn("fair housing retaliation", " ".join(payload["web_discovery"]["queries"]).lower())
            self.assertIn("24 c.f.r. 982.555", " ".join(payload["legal_authorities"]["queries"]).lower())
            self.assertEqual(payload["summary"]["top_web_titles"], ["HUD fair housing retaliation guidance"])
            self.assertEqual(payload["summary"]["top_legal_titles"], ["24 C.F.R. 982.555"])
            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "24 C.F.R. 982.555")

    def test_build_external_research_bundle_promotes_legal_domain_web_results_when_legal_search_is_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            web_payload = {
                "status": "success",
                "query": "fair housing retaliation",
                "result_count": 2,
                "results": [
                    {
                        "title": "24 CFR Part 966 Subpart B -- Grievance Procedures and Requirements",
                        "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-966/subpart-B",
                        "description": "Grievance procedures for public housing tenants.",
                    },
                    {
                        "title": "PDFGrievance Procedures - HUD.gov",
                        "url": "https://www.hud.gov/sites/dfiles/PIH/documents/PHOG_GrievanceProcedures.pdf",
                        "description": "HUD grievance procedure guidance.",
                    },
                ],
            }

            with mock.patch.object(engine, "discover", return_value=web_payload), mock.patch.object(
                engine,
                "discover_legal_authorities",
                return_value={"status": "success", "query": "fair housing retaliation", "result_count": 0, "results": []},
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertGreater(payload["legal_authorities"]["result_count"], 0)
            self.assertEqual(payload["legal_authorities"]["results"][0]["authority_source"], "web_fallback")
            self.assertIn("24 CFR Part 966", payload["summary"]["top_legal_titles"][0])
            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "24 CFR Part 966 Subpart B")
            self.assertGreater(payload["legal_authorities"]["results"][0]["research_priority_score"], 0.0)
            self.assertIn("has formal citation", payload["legal_authorities"]["results"][0]["research_priority_reasons"])
            self.assertEqual(
                payload["legal_authorities"]["results"][1]["citation"],
                "Grievance Procedures (HUD guidance)",
            )

    def test_build_external_research_bundle_extracts_us_code_citation_from_web_fallback(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            web_payload = {
                "status": "success",
                "query": "fair housing retaliation",
                "result_count": 1,
                "results": [
                    {
                        "title": "34 U.S. Code § 12494 - Prohibition on retaliation | U.S. Code | US Law | LII / Legal Information Institute",
                        "url": "https://www.law.cornell.edu/uscode/text/34/12494",
                        "description": "Federal retaliation authority.",
                    }
                ],
            }

            with mock.patch.object(engine, "discover", return_value=web_payload), mock.patch.object(
                engine,
                "discover_legal_authorities",
                return_value={"status": "success", "query": "fair housing retaliation", "result_count": 0, "results": []},
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "34 U.S. Code § 12494")
            self.assertEqual(payload["summary"]["top_legal_titles"][0], "34 U.S. Code § 12494")

    def test_build_external_research_bundle_prefers_title_over_opaque_legal_identifier_in_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            def fake_discover_legal_authorities(query, *, max_results=10, title=None, court=None, start_date=None, end_date=None):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 1,
                    "results": [
                        {
                            "title": "Public Housing Notice Requirements for Informal Hearings",
                            "citation": "2024-29824",
                            "authority_source": "federal_register",
                            "summary": "Federal Register material discussing HUD public housing notice and hearing procedures.",
                        }
                    ],
                }

            with mock.patch.object(
                engine,
                "discover",
                return_value={"status": "success", "query": "", "result_count": 0, "results": []},
            ), mock.patch.object(
                engine,
                "discover_legal_authorities",
                side_effect=fake_discover_legal_authorities,
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "2024-29824")
            self.assertEqual(payload["summary"]["top_legal_titles"][0], "Public Housing Notice Requirements for Informal Hearings")

    def test_build_synthetic_prompts_filters_stale_external_research_titles(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            prompts = engine._build_synthetic_prompts(
                query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                claim_type="housing_discrimination",
                upload_candidates=[],
                grounding_overview={},
                chronology_analysis={},
                grounding_signals={},
                external_research_bundle={
                    "web_discovery": {
                        "results": [
                            {
                                "title": "34 U.S. Code § 12494 - Prohibition on retaliation | U.S. Code | LII / Legal Information Institute",
                                "url": "https://www.law.cornell.edu/uscode/text/34/12494",
                                "description": "Federal retaliation authority.",
                            },
                            {
                                "title": "PDFGrievance Procedures - HUD.gov",
                                "url": "https://www.hud.gov/sites/dfiles/PIH/documents/PHOG_GrievanceProcedures.pdf",
                                "description": "HUD grievance procedure guidance for public housing tenants.",
                            },
                        ]
                    },
                    "legal_authorities": {
                        "results": [
                            {
                                "title": "HOME Program allocations notice",
                                "citation": "2024-29824",
                                "authority_source": "federal_register",
                                "url": "https://www.federalregister.gov/documents/2024/11/01/2024-29824/home-program-allocations",
                            },
                            {
                                "title": "Informal hearing for participants",
                                "citation": "24 C.F.R. 982.555",
                                "authority_source": "ecfr",
                                "url": "https://www.law.cornell.edu/cfr/text/24/982.555",
                            },
                        ]
                    },
                },
            )

            self.assertIn("Grievance Procedures (HUD guidance)", prompts["complaint_chatbot_prompt"])
            self.assertIn("24 C.F.R. 982.555", prompts["complaint_chatbot_prompt"])
            self.assertIn("Grievance Procedures (HUD guidance)", prompts["web_evidence_research_prompt"])
            self.assertIn("24 C.F.R. 982.555", prompts["legal_authority_research_prompt"])
            self.assertNotIn("34 U.S. Code § 12494", prompts["complaint_chatbot_prompt"])
            self.assertNotIn("2024-29824", prompts["complaint_chatbot_prompt"])
            self.assertNotIn("34 U.S. Code § 12494", prompts["web_evidence_research_prompt"])
            self.assertNotIn("2024-29824", prompts["legal_authority_research_prompt"])

    def test_build_synthetic_prompts_excludes_broad_uscode_releasepoints_without_grievance_fit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            prompts = engine._build_synthetic_prompts(
                query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                claim_type="housing_discrimination",
                upload_candidates=[],
                grounding_overview={},
                chronology_analysis={},
                grounding_signals={},
                external_research_bundle={
                    "web_discovery": {
                        "results": [
                            {
                                "title": "Litigation | NHLP",
                                "url": "https://www.nhlp.org/advocacy-and-litigation/nhlp-litigation/",
                                "description": "Public housing litigation and grievance support.",
                            }
                        ]
                    },
                    "legal_authorities": {
                        "results": [
                            {
                                "title": "Title 42 § 1437f.",
                                "citation": "Title 42 § 1437f.",
                                "authority_source": "us_code",
                                "url": "https://uscode.house.gov/download/releasepoints/us/pl/118/158/PRELIMusc42.htm",
                                "research_priority_reasons": ["grievance-process authority"],
                                "summary": "Snippet mentions a grievance procedure under 42 U.S.C. 1437d(k).",
                                "metadata": {"query": "42 U.S.C. 1437d(k) grievance procedure"},
                            },
                            {
                                "title": "Informal hearing for participants",
                                "citation": "24 C.F.R. 982.555",
                                "authority_source": "web_fallback",
                                "url": "https://www.law.cornell.edu/cfr/text/24/982.555",
                                "research_priority_reasons": ["promoted grievance-process authority", "grievance-process authority"],
                            },
                        ]
                    },
                },
            )

            self.assertIn("24 C.F.R. 982.555", prompts["legal_authority_research_prompt"])
            self.assertNotIn("Title 42 § 1437f", prompts["legal_authority_research_prompt"])
            self.assertNotIn("24 CFR § 982.555", prompts["legal_authority_research_prompt"])

    def test_build_external_research_bundle_blocks_mismatched_uscode_releasepoints(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            payload = engine._rank_external_research_payload(
                {
                    "results": [
                        {
                            "title": "Title 42 § 1437f.",
                            "citation": "Title 42 § 1437f.",
                            "authority_source": "us_code",
                            "url": "https://uscode.house.gov/download/releasepoints/us/pl/118/158/PRELIMusc42.htm",
                            "summary": "Administrative grievance procedure conducted under 42 U.S.C. 1437d(k).",
                            "metadata": {"query": "42 U.S.C. 1437d(k) grievance procedure"},
                        },
                        {
                            "title": "Informal hearing for participants",
                            "citation": "24 C.F.R. 982.555",
                            "authority_source": "ecfr",
                            "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-982/subpart-L/section-982.555",
                            "summary": "A PHA must give a participant family an opportunity for an informal hearing.",
                        },
                    ]
                },
                query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                claim_type="housing_discrimination",
                result_kind="legal",
                max_results=3,
            )

            citations = [str(item.get("citation") or "") for item in payload["results"]]
            self.assertIn("24 C.F.R. 982.555", citations)
            self.assertNotIn("Title 42 § 1437f.", citations)

    def test_build_external_research_bundle_ranks_web_and_legal_results_by_claim_and_chronology_fit(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            def fake_discover(query, *, max_results=10, engines=None, domain_filter=None, scrape=False):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 2,
                    "results": [
                        {
                            "title": "City blog roundup",
                            "url": "https://example.org/blog",
                            "snippet": "General housing update with no hearing timeline.",
                        },
                        {
                            "title": "HUD hearing notice retaliation guidance",
                            "url": "https://www.hud.gov/example/hearing-rights",
                            "snippet": "Guidance about grievance hearing notice, retaliation, appeal rights, and adverse action timing.",
                        },
                    ],
                }

            def fake_discover_legal_authorities(query, *, max_results=10, title=None, court=None, start_date=None, end_date=None):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 2,
                    "results": [
                        {
                            "title": "General housing article",
                            "authority_source": "secondary",
                        },
                        {
                            "title": "Informal hearing for participants",
                            "citation": "24 C.F.R. 982.555",
                            "authority_source": "federal_register",
                            "summary": "Discusses informal hearing notice, appeal rights, and decision timing.",
                        },
                    ],
                }

            with mock.patch.object(engine, "discover", side_effect=fake_discover), mock.patch.object(
                engine,
                "discover_legal_authorities",
                side_effect=fake_discover_legal_authorities,
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=2,
                )

            self.assertEqual(
                payload["web_discovery"]["results"][0]["title"],
                "HUD hearing notice retaliation guidance",
            )
            self.assertEqual(
                payload["legal_authorities"]["results"][0]["citation"],
                "24 C.F.R. 982.555",
            )
            self.assertIn(
                "contains chronology cues",
                " ".join(payload["web_discovery"]["results"][0]["research_priority_reasons"]).lower(),
            )

    def test_build_external_research_bundle_prefers_housing_domain_filtered_web_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            web_calls = []

            def fake_discover(query, *, max_results=10, engines=None, domain_filter=None, scrape=False):
                web_calls.append({"query": query, "domain_filter": list(domain_filter or [])})
                if domain_filter:
                    return {
                        "status": "success",
                        "query": query,
                        "result_count": 1,
                        "results": [
                            {
                                "title": "HUD grievance hearing notice guidance",
                                "url": "https://www.hud.gov/example/hearing-rights",
                                "snippet": "HUD guidance about grievance hearing notice, appeal rights, and adverse action timing.",
                            }
                        ],
                    }
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 1,
                    "results": [
                        {
                            "title": "RETALIATION Definition",
                            "url": "https://www.merriam-webster.com/dictionary/retaliation",
                            "snippet": "Dictionary definition of retaliation.",
                        }
                    ],
                }

            with mock.patch.object(engine, "discover", side_effect=fake_discover), mock.patch.object(
                engine,
                "discover_legal_authorities",
                return_value={"status": "success", "query": "", "result_count": 0, "results": []},
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=2,
                )

            self.assertTrue(any("hud.gov" in call["domain_filter"] for call in web_calls if call["domain_filter"]))
            self.assertEqual(payload["web_discovery"]["results"][0]["title"], "HUD grievance hearing notice guidance")
            self.assertIn("preferred housing domain", " ".join(payload["web_discovery"]["results"][0]["research_priority_reasons"]).lower())

    def test_build_external_research_bundle_filters_generic_federal_register_and_non_housing_grievance_noise(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            def fake_discover(query, *, max_results=10, engines=None, domain_filter=None, scrape=False):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 2,
                    "results": [
                        {
                            "title": "Discrimination, Harassment, Sexual Misconduct, & Retaliation",
                            "url": "https://www.ucmo.edu/offices/general-counsel/university-policy-library/procedures/discrimination-harassment-and-sexual-misconduct-grievance-process/index.php",
                            "summary": "University grievance procedures for sexual misconduct investigations and appeals.",
                        },
                        {
                            "title": "HUD grievance hearing notice guidance",
                            "url": "https://www.hud.gov/example/hearing-rights",
                            "summary": "HUD guidance about tenant grievance hearing notice, appeal rights, and adverse action timing.",
                        },
                    ],
                }

            def fake_discover_legal_authorities(query, *, max_results=10, title=None, court=None, start_date=None, end_date=None):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 2,
                    "results": [
                        {
                            "title": "HOME Investment Partnerships Program: Program Updates and Streamlining",
                            "citation": "2024-29824",
                            "authority_source": "federal_register",
                            "url": "https://www.govinfo.gov/content/pkg/FR-2025-01-06/pdf/2024-29824.pdf",
                            "summary": "General HOME program updates without grievance or hearing procedures for tenant disputes.",
                        },
                        {
                            "title": "Informal hearing for participants",
                            "citation": "24 C.F.R. 982.555",
                            "authority_source": "ecfr",
                            "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-982/subpart-L/section-982.555",
                            "summary": "Requires notice and an opportunity for an informal hearing for Section 8 participants.",
                        },
                    ],
                }

            with mock.patch.object(engine, "discover", side_effect=fake_discover), mock.patch.object(
                engine,
                "discover_legal_authorities",
                side_effect=fake_discover_legal_authorities,
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertEqual(payload["web_discovery"]["result_count"], 1)
            self.assertEqual(payload["web_discovery"]["results"][0]["title"], "HUD grievance hearing notice guidance")
            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "24 C.F.R. 982.555")
            self.assertNotIn(
                "2024-29824",
                [str(item.get("citation") or "") for item in payload["legal_authorities"]["results"]],
            )

    def test_build_external_research_bundle_promotes_web_legal_authority_when_generic_federal_register_results_are_filtered(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            web_payload = {
                "status": "success",
                "query": "fair housing retaliation",
                "result_count": 2,
                "results": [
                    {
                        "title": "24 CFR Part 966 Subpart B -- Grievance Procedures and Requirements",
                        "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-966/subpart-B",
                        "description": "Grievance procedures for public housing tenants.",
                    },
                    {
                        "title": "HOME Investment Partnerships Program updates",
                        "url": "https://www.govinfo.gov/content/pkg/FR-2025-01-06/pdf/2024-29824.pdf",
                        "description": "General HOME program updates.",
                    },
                ],
            }

            with mock.patch.object(engine, "discover", return_value=web_payload), mock.patch.object(
                engine,
                "discover_legal_authorities",
                return_value={
                    "status": "success",
                    "query": "fair housing retaliation",
                    "result_count": 1,
                    "results": [
                        {
                            "title": "HOME Investment Partnerships Program: Program Updates and Streamlining",
                            "citation": "2024-29824",
                            "authority_source": "federal_register",
                            "url": "https://www.govinfo.gov/content/pkg/FR-2025-01-06/pdf/2024-29824.pdf",
                            "summary": "General HOME program updates without grievance or hearing procedures for tenant disputes.",
                        }
                    ],
                },
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertGreater(payload["legal_authorities"]["result_count"], 0)
            self.assertEqual(payload["legal_authorities"]["results"][0]["authority_source"], "web_fallback")
            self.assertEqual(payload["legal_authorities"]["results"][0]["citation"], "24 CFR Part 966 Subpart B")
            self.assertNotIn(
                "2024-29824",
                [str(item.get("citation") or "") for item in payload["legal_authorities"]["results"]],
            )

    def test_build_external_research_bundle_prefers_grievance_process_authorities_over_broad_statutes_and_complaint_pages(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            def fake_discover(query, *, max_results=10, engines=None, domain_filter=None, scrape=False):
                return {
                    "status": "success",
                    "query": query,
                    "result_count": 3,
                    "results": [
                        {
                            "title": "34 U.S. Code § 12494 - Prohibition on retaliation | U.S. Code | US Law ...",
                            "url": "https://www.law.cornell.edu/uscode/text/34/12494",
                            "description": "Retaliation authority cross-referencing the Fair Housing Act.",
                        },
                        {
                            "title": "BOLI : Housing Discrimination Complaint : Civil Rights : State of Oregon",
                            "url": "https://www.oregon.gov/boli/civil-rights/Pages/housing-discrimination-complaint.aspx",
                            "description": "File a housing discrimination complaint with Oregon BOLI.",
                        },
                        {
                            "title": "PDFHCV Grievance Procedures - files.hudexchange.info",
                            "url": "https://files.hudexchange.info/resources/documents/HCV-Grievance-Procedures.pdf",
                            "description": "Housing Choice Voucher grievance procedures and informal hearing rights.",
                        },
                    ],
                }

            def fake_discover_legal_authorities(query, *, max_results=10, title=None, court=None, start_date=None, end_date=None):
                query_lower = query.lower()
                if "982.555" in query_lower:
                    return {
                        "status": "success",
                        "query": query,
                        "result_count": 1,
                        "results": [
                            {
                                "title": "Informal hearing for participants",
                                "citation": "24 C.F.R. 982.555",
                                "authority_source": "ecfr",
                                "url": "https://www.ecfr.gov/current/title-24/subtitle-B/chapter-IX/part-982/subpart-L/section-982.555",
                                "summary": "A PHA must give a participant family an opportunity for an informal hearing.",
                            }
                        ],
                    }
                if "1437d" in query_lower:
                    return {
                        "status": "success",
                        "query": query,
                        "result_count": 2,
                        "results": [
                            {
                                "title": "Title 42 § 12705.",
                                "citation": "Title 42 § 12705.",
                                "authority_source": "us_code",
                                "url": "https://uscode.house.gov/download/releasepoints/us/pl/118/158/PRELIMusc42.htm",
                                "summary": "General housing planning statute without grievance-process language.",
                            },
                            {
                                "title": "Title 42 § 1437d.",
                                "citation": "Title 42 § 1437d.",
                                "authority_source": "us_code",
                                "url": "https://uscode.house.gov/download/releasepoints/us/pl/118/158/PRELIMusc42.htm",
                                "summary": "Broad public housing statute excerpt without hearing text in this result.",
                            },
                        ],
                    }
                return {"status": "success", "query": query, "result_count": 0, "results": []}

            with mock.patch.object(engine, "discover", side_effect=fake_discover), mock.patch.object(
                engine,
                "discover_legal_authorities",
                side_effect=fake_discover_legal_authorities,
            ):
                payload = engine._build_external_research_bundle(
                    query_text="retaliation grievance complaint appeal hearing due process tenant policy adverse action",
                    claim_type="housing_discrimination",
                    max_results=3,
                )

            self.assertIn(
                payload["legal_authorities"]["results"][0]["citation"],
                {"24 C.F.R. 982.555", "HCV Grievance Procedures (HUD guidance)"},
            )
            self.assertNotIn(
                "Title 42 § 12705.",
                [str(item.get("citation") or "") for item in payload["legal_authorities"]["results"]],
            )
            self.assertNotIn(
                "https://www.oregon.gov/boli/civil-rights/Pages/housing-discrimination-complaint.aspx",
                [str(item.get("url") or "") for item in payload["web_discovery"]["results"]],
            )
            self.assertIn(
                "https://files.hudexchange.info/resources/documents/HCV-Grievance-Procedures.pdf",
                [str(item.get("url") or "") for item in payload["web_discovery"]["results"]],
            )

    def test_search_local_surfaces_chronology_summary_and_prioritizes_timeline_ready_documents(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            dated_path = root / "dated_notice.txt"
            dated_path.write_text(
                "HACC sent written notice on March 4, 2024 and denied the review on March 8, 2024.",
                encoding="utf-8",
            )
            plain_path = root / "plain_note.txt"
            plain_path.write_text(
                "HACC discussed a hearing and notice without any date details.",
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            payload = engine.search_local("hearing notice response date", top_k=2)

            self.assertEqual(payload["status"], "success")
            self.assertIn("support_bundle", payload)
            self.assertIn("query_context", payload)
            self.assertEqual(payload["chronology_ready_result_count"], 1)
            self.assertEqual(payload["results"][0]["document_id"], "repo::dated_notice.txt")
            self.assertGreaterEqual(payload["results"][0]["chronology_summary"]["timeline_anchor_count"], 1)
            self.assertEqual(payload["results"][1]["chronology_summary"]["timeline_anchor_count"], 0)

    def test_select_uploadable_results_preserves_match_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            evidence_path = root / "policy.txt"
            evidence_path.write_text("hearing rights", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "results": [
                        {
                            "document_id": "kg::policy",
                            "title": "Policy",
                            "source_type": "knowledge_graph",
                            "source_path": str(evidence_path),
                            "score": 10.0,
                            "snippet": "Residents may request an informal hearing.",
                            "matched_rules": [
                                {
                                    "text": "Residents may request an informal hearing.",
                                    "section_title": "Appeal Procedures",
                                }
                            ],
                            "matched_entities": [{"name": "informal hearing", "type": "policy_rule"}],
                            "metadata": {},
                        }
                    ]
                },
                top_k=1,
            )

            self.assertEqual(candidates[0]["matched_rules"][0]["section_title"], "Appeal Procedures")
            self.assertEqual(candidates[0]["matched_entities"][0]["name"], "informal hearing")

    def test_candidate_anchor_sections_uses_matched_entity_context_for_appeal_rights(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            labels = engine._candidate_anchor_sections(
                {
                    "title": "ADMISSIONS AND CONTINUED OCCUPANCY POLICY",
                    "snippet": "Grievance: Any dispute a tenant may have with respect to HACC action or failure to act.",
                    "matched_rules": [
                        {
                            "text": "In states without due process determinations, HACC must grant opportunity for grievance procedures.",
                            "section_title": "Sample Grievance Procedure",
                        }
                    ],
                    "matched_entities": [
                        {"name": "The notice must also state that the tenant may request a grievance hearing", "type": "policy_rule"},
                        {"name": "right to appeal HACC's decision", "type": "policy_rule"},
                    ],
                }
            )

            self.assertIn("grievance_hearing", labels)
            self.assertIn("appeal_rights", labels)

    def test_select_uploadable_results_prefers_stronger_scores_over_source_type_bias(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            strong_path = root / "policy.txt"
            weak_path = root / "note.txt"
            strong_path.write_text("strong", encoding="utf-8")
            weak_path.write_text("weak", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "results": [
                        {
                            "document_id": "repo::note.txt",
                            "title": "Weak repo evidence",
                            "source_type": "repository_evidence",
                            "source_path": str(weak_path),
                            "score": 5.0,
                            "metadata": {},
                        },
                        {
                            "document_id": "kg::policy",
                            "title": "Strong policy evidence",
                            "source_type": "knowledge_graph",
                            "source_path": str(strong_path),
                            "score": 99.0,
                            "metadata": {},
                        },
                    ]
                },
                top_k=2,
            )

            self.assertEqual(candidates[0]["document_id"], "kg::policy")

    def test_select_uploadable_results_prefers_case_like_notice_evidence_for_chronology_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            policy_path = root / "policy.txt"
            notice_path = root / "notice.txt"
            policy_path.write_text("policy", encoding="utf-8")
            notice_path.write_text("notice", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "query": "retaliation grievance complaint appeal hearing due process tenant notice response date",
                    "results": [
                        {
                            "document_id": "kg::policy",
                            "title": "Administrative Plan Policy",
                            "source_type": "knowledge_graph",
                            "source_path": str(policy_path),
                            "score": 95.0,
                            "snippet": "General housing policy overview.",
                            "matched_rules": [
                                {
                                    "text": "General program rules and policy summary.",
                                    "section_title": "Policy Overview",
                                }
                            ],
                            "metadata": {},
                        },
                        {
                            "document_id": "repo::notice.txt",
                            "title": "Tenant Notice",
                            "source_type": "repository_evidence",
                            "source_path": str(notice_path),
                            "score": 82.0,
                            "snippet": "HACC sent written notice and described the right to request an informal review.",
                            "matched_rules": [
                                {
                                    "text": "The notice must describe how to obtain the informal review and explain the denial of assistance.",
                                    "section_title": "Notice to Applicant",
                                }
                            ],
                            "matched_entities": [
                                {"name": "written notice of denial", "type": "policy_rule"},
                            ],
                            "metadata": {},
                        },
                    ],
                },
                top_k=2,
            )

            self.assertEqual(candidates[0]["document_id"], "repo::notice.txt")
            self.assertGreater(candidates[0]["selection_priority"], candidates[1]["selection_priority"])

    def test_select_uploadable_results_penalizes_noisy_review_markup_for_chronology_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            noisy_path = root / "reviews.html"
            policy_path = root / "policy.txt"
            noisy_path.write_text("reviews", encoding="utf-8")
            policy_path.write_text("policy", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "query": "retaliation grievance appeal hearing notice response date",
                    "results": [
                        {
                            "document_id": "repo::reviews.html",
                            "title": "Apartment Reviews",
                            "source_type": "repository_evidence",
                            "source_path": str(noisy_path),
                            "score": 88.0,
                            "snippet": '<script>window.__FEATURE_FLAG_STATE__={"featureFlags":[]};</script> "previewText":"I asked to cancel my application"',
                            "matched_rules": [],
                            "matched_entities": [],
                            "metadata": {},
                        },
                        {
                            "document_id": "kg::policy",
                            "title": "ADMISSIONS AND CONTINUED OCCUPANCY POLICY",
                            "source_type": "knowledge_graph",
                            "source_path": str(policy_path),
                            "score": 75.0,
                            "snippet": "The notice must also state that the tenant may request a grievance hearing on the HACC decision.",
                            "matched_rules": [
                                {
                                    "text": "The notice must also state that the tenant may request a grievance hearing on the HACC decision.",
                                    "section_title": "Sample Grievance Procedure",
                                }
                            ],
                            "matched_entities": [{"name": "HACC grievance hearing", "type": "policy_rule"}],
                            "metadata": {},
                        },
                    ],
                },
                top_k=2,
            )

            self.assertEqual(candidates[0]["document_id"], "kg::policy")
            self.assertLess(candidates[1]["selection_priority"], 0.0)

    def test_select_uploadable_results_penalizes_audit_reports_for_chronology_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            report_path = root / "audit.md"
            policy_path = root / "policy.txt"
            report_path.write_text("audit", encoding="utf-8")
            policy_path.write_text("policy", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "query": "retaliation grievance appeal hearing notice response date",
                    "results": [
                        {
                            "document_id": "repo::audit.md",
                            "title": "Housing Authority Audit Summary",
                            "source_type": "repository_evidence",
                            "source_path": str(report_path),
                            "score": 88.0,
                            "snippet": "Date December 31, 2025. Audit summary of housing authority review findings.",
                            "matched_rules": [],
                            "matched_entities": [],
                            "metadata": {},
                        },
                        {
                            "document_id": "kg::policy",
                            "title": "ADMISSIONS AND CONTINUED OCCUPANCY POLICY",
                            "source_type": "knowledge_graph",
                            "source_path": str(policy_path),
                            "score": 75.0,
                            "snippet": "The notice must also state that the tenant may request a grievance hearing on the HACC decision.",
                            "matched_rules": [
                                {
                                    "text": "The notice must also state that the tenant may request a grievance hearing on the HACC decision.",
                                    "section_title": "Sample Grievance Procedure",
                                }
                            ],
                            "matched_entities": [{"name": "HACC grievance hearing", "type": "policy_rule"}],
                            "metadata": {},
                        },
                    ],
                },
                top_k=2,
            )

            self.assertEqual(candidates[0]["document_id"], "kg::policy")
            self.assertLess(candidates[1]["selection_priority"], candidates[0]["selection_priority"])

    def test_select_uploadable_results_penalizes_repository_documentation_for_chronology_queries(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            readme_path = root / "README.md"
            policy_path = root / "policy.txt"
            readme_path.write_text("readme", encoding="utf-8")
            policy_path.write_text("policy", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            candidates = engine._select_uploadable_results(
                {
                    "query": "retaliation grievance appeal hearing notice response date",
                    "results": [
                        {
                            "document_id": "repo::README.md",
                            "title": "# HACC Audit and Complaint System",
                            "source_type": "repository_evidence",
                            "source_path": str(readme_path),
                            "relative_path": "README.md",
                            "score": 90.0,
                            "snippet": "```python from hacc_adversarial_runner import run_hacc_adversarial_batch ``` CLI reference with key parameters and output_dir values.",
                            "matched_rules": [],
                            "matched_entities": [],
                            "metadata": {},
                        },
                        {
                            "document_id": "kg::policy",
                            "title": "ADMINISTRATIVE PLAN",
                            "source_type": "knowledge_graph",
                            "source_path": str(policy_path),
                            "score": 75.0,
                            "snippet": "The notice must also state that the tenant may request an informal review of the decision.",
                            "matched_rules": [
                                {
                                    "text": "The notice must also state that the tenant may request an informal review of the decision.",
                                    "section_title": "Notice to Applicant",
                                }
                            ],
                            "matched_entities": [{"name": "informal review", "type": "policy_rule"}],
                            "metadata": {},
                        },
                    ],
                },
                top_k=2,
            )

            self.assertEqual(candidates[0]["document_id"], "kg::policy")
            self.assertLess(candidates[1]["selection_priority"], candidates[0]["selection_priority"])

    def test_simulate_evidence_upload_uses_mediator_submit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            evidence_path = root / "README.md"
            evidence_path.write_text(
                "Reasonable Accommodation Policy\nThis file should be uploaded into the mediator.",
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            class FakeMediator:
                def __init__(self):
                    self.calls = []
                    self.evidence_analysis = self

                def submit_evidence_file(self, **kwargs):
                    self.calls.append(kwargs)
                    return {"cid": "bafy-test", "record_id": 7, "claim_type": kwargs.get("claim_type")}

                def get_user_evidence(self, user_id):
                    return [{"id": 7, "cid": "bafy-test", "user_id": user_id}]

                def summarize_claim_support(self, user_id, claim_type=None):
                    return {"user_id": user_id, "claim_type": claim_type, "total_links": 1}

                def analyze_evidence_for_claim(self, user_id, claim_type):
                    return {"user_id": user_id, "claim_type": claim_type, "total_evidence": 1, "has_evidence": True}

            mediator = FakeMediator()
            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )
            payload = engine.simulate_evidence_upload(
                "reasonable accommodation hearing rights",
                top_k=1,
                claim_type="housing_discrimination",
                user_id="test-user",
                search_mode="lexical",
                mediator=mediator,
            )

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["upload_count"], 1)
            self.assertEqual(payload["support_summary"]["total_links"], 1)
            self.assertEqual(payload["evidence_analysis"]["total_evidence"], 1)
            self.assertEqual(len(mediator.calls), 1)
            self.assertEqual(mediator.calls[0]["file_path"], str(evidence_path.resolve()))
            self.assertEqual(mediator.calls[0]["claim_type"], "housing_discrimination")
            self.assertEqual(payload["mediator_evidence_packets"][0]["relative_path"], "README.md")
            self.assertIn("external_research_bundle", payload)

    def test_simulate_evidence_upload_uses_extracted_text_fallback_for_extensionless_pdf_sources(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdf_source = root / "hacc_website" / "policy-source"
            pdf_source.parent.mkdir(parents=True, exist_ok=True)
            pdf_source.write_bytes(b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\n")

            kg_dir = root / "hacc_website" / "knowledge_graph" / "documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "policy",
                        "text": "Reasonable accommodation hearing rights are explained in this policy.",
                        "document": {
                            "title": "Extensionless Policy PDF",
                            "source_path": str(pdf_source),
                        },
                        "rules": [
                            {
                                "text": "Reasonable accommodation hearing rights are explained in this policy.",
                                "rule_type": "obligation",
                                "section_title": "Hearing Rights",
                            }
                        ],
                        "entities": [{"id": "entity1", "type": "concept", "name": "reasonable accommodation"}],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            class FakeMediator:
                def __init__(self):
                    self.calls = []
                    self.evidence_analysis = self

                def submit_evidence(self, **kwargs):
                    self.calls.append(("submit_evidence", kwargs))
                    return {"cid": "bafy-test", "record_id": 8}

                def submit_evidence_file(self, **kwargs):
                    self.calls.append(("submit_evidence_file", kwargs))
                    return {"cid": "bafy-test", "record_id": 8}

                def get_user_evidence(self, user_id):
                    return [{"id": 8, "cid": "bafy-test", "user_id": user_id}]

                def summarize_claim_support(self, user_id, claim_type=None):
                    return {"user_id": user_id, "claim_type": claim_type, "total_links": 1}

                def analyze_evidence_for_claim(self, user_id, claim_type):
                    return {"user_id": user_id, "claim_type": claim_type, "total_evidence": 1, "has_evidence": True}

            mediator = FakeMediator()
            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            payload = engine.simulate_evidence_upload(
                "reasonable accommodation hearing rights",
                top_k=1,
                claim_type="housing_discrimination",
                user_id="test-user",
                search_mode="lexical",
                mediator=mediator,
            )

            self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["mediator_evidence_packets"][0]["mime_type"], "text/plain")
        self.assertEqual(payload["mediator_evidence_packets"][0]["metadata"]["upload_strategy"], "extracted_text_fallback")
        self.assertEqual(mediator.calls[0][0], "submit_evidence")
        self.assertIn(b"Reasonable accommodation hearing rights", mediator.calls[0][1]["data"])
        self.assertEqual(mediator.calls[0][1]["metadata"]["mime_type"], "text/plain")
        self.assertEqual(mediator.calls[0][1]["metadata"]["original_mime_type"], "application/pdf")
        self.assertEqual(mediator.calls[0][1]["metadata"]["filename"], "policy-source.txt")

    def test_search_package_builds_shared_vector_index_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_vector_available = engine_module.VECTOR_STORE_AVAILABLE
            original_embeddings_available = engine_module.EMBEDDINGS_AVAILABLE
            try:
                engine_module.VECTOR_STORE_AVAILABLE = True
                engine_module.EMBEDDINGS_AVAILABLE = True

                build_calls = []
                hybrid_calls = []
                has_index_states = iter([False, True])

                original_build_vector_index = engine.build_vector_index
                original_hybrid_search = engine.hybrid_search
                original_has_preferred_vector_index = engine._has_preferred_vector_index

                def fake_build_vector_index(*, output_dir=None, index_name="hacc_corpus", batch_size=32):
                    build_calls.append({
                        "output_dir": output_dir,
                        "index_name": index_name,
                        "batch_size": batch_size,
                    })
                    return {"status": "success", "index_name": index_name}

                def fake_hybrid_search(query, *, top_k=10, vector_top_k=None, index_name="hacc_corpus", index_dir=None, source_types=None):
                    hybrid_calls.append({
                        "query": query,
                        "top_k": top_k,
                        "index_name": index_name,
                        "index_dir": index_dir,
                    })
                    return {"status": "success", "query": query, "results": [{"document_id": "vector-doc"}]}

                def fake_has_preferred_vector_index(*, index_name="hacc_corpus", index_dir=None):
                    return next(has_index_states)

                engine.build_vector_index = fake_build_vector_index
                engine.hybrid_search = fake_hybrid_search
                engine._has_preferred_vector_index = fake_has_preferred_vector_index
                payload = engine.search("reasonable accommodation", top_k=2, search_mode="package")
            finally:
                engine.build_vector_index = original_build_vector_index
                engine.hybrid_search = original_hybrid_search
                engine._has_preferred_vector_index = original_has_preferred_vector_index
                engine_module.VECTOR_STORE_AVAILABLE = original_vector_available
                engine_module.EMBEDDINGS_AVAILABLE = original_embeddings_available

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["backend_mode"], "shared_hybrid")
            self.assertEqual(payload["effective_search_mode"], "shared_hybrid")
            self.assertEqual(payload["results"][0]["document_id"], "vector-doc")
            self.assertEqual(len(build_calls), 1)
            self.assertEqual(len(hybrid_calls), 1)

    def test_search_package_rewrites_hybrid_fallback_note_for_package_requests(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_hybrid_search = engine.hybrid_search
            original_has_preferred_vector_index = engine._has_preferred_vector_index
            try:
                engine.hybrid_search = lambda *args, **kwargs: {
                    "status": "success",
                    "results": [],
                    "effective_search_mode": "lexical_only",
                    "vector_status": "unavailable",
                    "vector_error": "numpy unavailable",
                    "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead.",
                }
                engine._has_preferred_vector_index = lambda **kwargs: True

                payload = engine.search("reasonable accommodation", top_k=2, search_mode="package")
            finally:
                engine.hybrid_search = original_hybrid_search
                engine._has_preferred_vector_index = original_has_preferred_vector_index

            self.assertEqual(payload["backend_mode"], "shared_hybrid")
            self.assertEqual(payload["effective_search_mode"], "lexical_only")
            self.assertIn("Requested package/shared hybrid search", payload["fallback_note"])
            self.assertIn("numpy unavailable", payload["fallback_note"])

    def test_search_package_normalizes_successful_hybrid_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_hybrid_search = engine.hybrid_search
            original_has_preferred_vector_index = engine._has_preferred_vector_index
            try:
                engine.hybrid_search = lambda *args, **kwargs: {
                    "status": "success",
                    "results": [{"document_id": "vector-doc"}],
                    "effective_search_mode": "hybrid",
                    "vector_status": "success",
                    "vector_error": "",
                    "fallback_note": "",
                }
                engine._has_preferred_vector_index = lambda **kwargs: True

                payload = engine.search("reasonable accommodation", top_k=2, search_mode="package")
            finally:
                engine.hybrid_search = original_hybrid_search
                engine._has_preferred_vector_index = original_has_preferred_vector_index

            self.assertEqual(payload["backend_mode"], "shared_hybrid")
            self.assertEqual(payload["effective_search_mode"], "shared_hybrid")
            self.assertEqual(payload["fallback_note"], "")

    def test_search_package_falls_back_to_lexical_when_shared_vector_backend_is_unavailable(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            text_path = parsed_dir / "doc1.txt"
            text_path.write_text("Reasonable Accommodation Policy\nSearch time extensions are available.", encoding="utf-8")
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps({"parsed_documents": [{"parsed_text_path": "research_results/documents/parsed/doc1.txt"}]}),
                encoding="utf-8",
            )

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_vector_available = engine_module.VECTOR_STORE_AVAILABLE
            original_embeddings_available = engine_module.EMBEDDINGS_AVAILABLE
            original_create_vector_index = engine_module.create_vector_index
            try:
                engine_module.VECTOR_STORE_AVAILABLE = False
                engine_module.EMBEDDINGS_AVAILABLE = False
                engine_module.create_vector_index = None
                payload = engine.search("reasonable accommodation", top_k=1, search_mode="package")
            finally:
                engine_module.VECTOR_STORE_AVAILABLE = original_vector_available
                engine_module.EMBEDDINGS_AVAILABLE = original_embeddings_available
                engine_module.create_vector_index = original_create_vector_index

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["backend_mode"], "lexical_fallback")
            self.assertEqual(payload["effective_search_mode"], "lexical_fallback")
            self.assertEqual(payload["results"][0]["document_id"], "doc1")
            self.assertEqual(payload["vector_status"], "unavailable")
            self.assertIn("using lexical results instead", payload["fallback_note"])

    def test_hybrid_search_merges_lexical_and_vector_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("housing_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "housing_policy",
                        "text": "HACC must approve additional search time if needed as a reasonable accommodation.",
                        "document": {
                            "title": "Housing Search Accommodation Policy",
                            "source_path": "/tmp/housing_policy.pdf",
                        },
                        "rules": [],
                        "entities": [],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            original_search_vector_index = engine_module.search_vector_index
            try:
                engine_module.search_vector_index = lambda *args, **kwargs: {
                    "status": "success",
                    "results": [
                        {
                            "id": "housing_policy:chunk:0",
                            "text": "reasonable accommodation search time",
                            "metadata": {
                                "document_id": "housing_policy",
                                "title": "Housing Search Accommodation Policy",
                                "source_type": "knowledge_graph",
                            },
                            "score": 0.9,
                        }
                    ],
                }
                engine = HACCResearchEngine(
                    repo_root=root,
                    parsed_dir=parsed_dir,
                    parse_manifest_path=manifest_path,
                    knowledge_graph_dir=root / "hacc_website/knowledge_graph",
                )
                payload = engine.hybrid_search("reasonable accommodation search time", top_k=3)
            finally:
                engine_module.search_vector_index = original_search_vector_index

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["results"][0]["document_id"], "housing_policy")
            self.assertIn("vector", payload["results"][0]["search_modes"])

    def test_hybrid_search_forces_lexical_base_search_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_search = engine.search
            original_search_vector = engine.search_vector
            try:
                captured_modes = []

                def fake_search(query, *, top_k=10, use_vector=False, search_mode="auto", vector_top_k=None, index_name="hacc_corpus", index_dir=None, source_types=None, min_score=0.0):
                    captured_modes.append(search_mode)
                    return {"status": "success", "results": []}

                engine.search = fake_search
                engine.search_vector = lambda *args, **kwargs: {"status": "success", "results": []}
                payload = original_search("reasonable accommodation", search_mode="hybrid")
            finally:
                engine.search = original_search
                engine.search_vector = original_search_vector

            self.assertEqual(payload["status"], "success")
            self.assertEqual(captured_modes[0], "lexical")

    def test_hybrid_search_handles_unavailable_vector_backend(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("housing_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "housing_policy",
                        "text": "HACC must approve additional search time if needed as a reasonable accommodation.",
                        "document": {
                            "title": "Housing Search Accommodation Policy",
                            "source_path": "/tmp/housing_policy.pdf",
                        },
                        "rules": [],
                        "entities": [],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            original_search_vector_index = engine_module.search_vector_index
            try:
                engine_module.search_vector_index = lambda *args, **kwargs: {
                    "status": "unavailable",
                    "results": [],
                    "error": "numpy unavailable",
                }
                engine = HACCResearchEngine(
                    repo_root=root,
                    parsed_dir=parsed_dir,
                    parse_manifest_path=manifest_path,
                    knowledge_graph_dir=root / "hacc_website/knowledge_graph",
                )
                payload = engine.hybrid_search("reasonable accommodation search time", top_k=3)
            finally:
                engine_module.search_vector_index = original_search_vector_index

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["vector_status"], "unavailable")
            self.assertEqual(payload["effective_search_mode"], "lexical_only")
            self.assertIn("using lexical results instead", payload["fallback_note"])
            self.assertEqual(payload["results"][0]["document_id"], "housing_policy")

    def test_hybrid_search_surfaces_vector_backend_error_details(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            kg_dir = root / "hacc_website/knowledge_graph/documents"
            kg_dir.mkdir(parents=True, exist_ok=True)
            kg_dir.joinpath("housing_policy.json").write_text(
                json.dumps(
                    {
                        "status": "success",
                        "source_id": "housing_policy",
                        "text": "HACC must approve additional search time if needed as a reasonable accommodation.",
                        "document": {
                            "title": "Housing Search Accommodation Policy",
                            "source_path": "/tmp/housing_policy.pdf",
                        },
                        "rules": [],
                        "entities": [],
                        "relationships": [],
                        "metadata": {},
                        "provider": "ipfs_datasets_py",
                    }
                ),
                encoding="utf-8",
            )

            original_search_vector_index = engine_module.search_vector_index
            try:
                engine_module.search_vector_index = lambda *args, **kwargs: {
                    "status": "error",
                    "results": [],
                    "error": "transformers/torch not available for HF embeddings",
                }
                engine = HACCResearchEngine(
                    repo_root=root,
                    parsed_dir=parsed_dir,
                    parse_manifest_path=manifest_path,
                    knowledge_graph_dir=root / "hacc_website/knowledge_graph",
                )
                payload = engine.hybrid_search("reasonable accommodation search time", top_k=3)
            finally:
                engine_module.search_vector_index = original_search_vector_index

            self.assertEqual(payload["status"], "success")
            self.assertEqual(payload["vector_status"], "error")
            self.assertIn("hacc_policy_graph: transformers/torch not available for HF embeddings", payload["vector_error"])
            self.assertIn("hacc_text_chunks: transformers/torch not available for HF embeddings", payload["vector_error"])
            self.assertIn("hacc_corpus: transformers/torch not available for HF embeddings", payload["vector_error"])
            self.assertIn("transformers/torch not available for HF embeddings", payload["fallback_note"])

    def test_search_auto_prefers_hybrid_when_shared_vector_index_exists(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            embeddings_dir = root / "hacc_website/knowledge_graph/embeddings"
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            (embeddings_dir / "hacc_policy_graph.manifest.json").write_text("{}", encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_hybrid_search = engine.hybrid_search
            try:
                calls = []

                def fake_hybrid_search(query, *, top_k=10, vector_top_k=None, index_name="hacc_corpus", index_dir=None, source_types=None):
                    calls.append(
                        {
                            "query": query,
                            "top_k": top_k,
                            "vector_top_k": vector_top_k,
                            "index_name": index_name,
                            "index_dir": index_dir,
                        }
                    )
                    return {"status": "success", "query": query, "results": [{"document_id": "vector-doc"}]}

                engine.hybrid_search = fake_hybrid_search
                payload = engine.search("reasonable accommodation", top_k=2, search_mode="auto")
            finally:
                engine.hybrid_search = original_hybrid_search

            self.assertEqual(payload["results"][0]["document_id"], "vector-doc")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["query"], "reasonable accommodation")

    def test_search_defaults_to_package_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_search_package = engine.search_package
            try:
                calls = []

                def fake_search_package(query, *, top_k=10, vector_top_k=None, index_name="hacc_corpus", index_dir=None, source_types=None, auto_build_index=True):
                    calls.append(
                        {
                            "query": query,
                            "top_k": top_k,
                            "index_name": index_name,
                            "index_dir": index_dir,
                            "auto_build_index": auto_build_index,
                        }
                    )
                    return {"status": "success", "query": query, "results": [{"document_id": "package-doc"}]}

                engine.search_package = fake_search_package
                payload = engine.search("reasonable accommodation", top_k=2)
            finally:
                engine.search_package = original_search_package

            self.assertEqual(payload["results"][0]["document_id"], "package-doc")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["query"], "reasonable accommodation")

    def test_research_defaults_to_package_mode_for_local_search(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_search = engine.search
            original_discover = engine.discover
            original_discover_legal_authorities = engine.discover_legal_authorities
            try:
                search_calls = []

                def fake_search(query, *, top_k=10, use_vector=False, search_mode="auto", vector_top_k=None, index_name="hacc_corpus", index_dir=None, source_types=None, min_score=0.0):
                    search_calls.append(
                        {
                            "query": query,
                            "top_k": top_k,
                            "search_mode": search_mode,
                            "use_vector": use_vector,
                        }
                    )
                    return {"status": "success", "query": query, "results": []}

                engine.search = fake_search
                engine.discover = lambda *args, **kwargs: {"status": "success", "results": []}
                engine.discover_legal_authorities = lambda *args, **kwargs: {"status": "success", "results": [], "result_count": 0}
                payload = engine.research("reasonable accommodation retaliation", local_top_k=1, web_max_results=1)
            finally:
                engine.search = original_search
                engine.discover = original_discover
                engine.discover_legal_authorities = original_discover_legal_authorities

            self.assertEqual(payload["status"], "success")
            self.assertEqual(search_calls[0]["search_mode"], "package")
            self.assertEqual(search_calls[0]["top_k"], 1)

    def test_research_surfaces_local_search_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_search = engine.search
            original_discover = engine.discover
            original_discover_legal_authorities = engine.discover_legal_authorities
            try:
                engine.search = lambda *args, **kwargs: {
                    "status": "success",
                    "effective_search_mode": "lexical_only",
                    "vector_status": "unavailable",
                    "fallback_note": "Requested hybrid search, but vector support is unavailable; using lexical results instead.",
                    "results": [],
                }
                engine.discover = lambda *args, **kwargs: {"status": "success", "results": []}
                engine.discover_legal_authorities = lambda *args, **kwargs: {"status": "success", "results": [], "result_count": 0}
                payload = engine.research(
                    "reasonable accommodation retaliation",
                    local_top_k=1,
                    web_max_results=1,
                    search_mode="hybrid",
                )
            finally:
                engine.search = original_search
                engine.discover = original_discover
                engine.discover_legal_authorities = original_discover_legal_authorities

            self.assertEqual(payload["local_search_summary"]["requested_search_mode"], "hybrid")
            self.assertEqual(payload["local_search_summary"]["effective_search_mode"], "lexical_only")
            self.assertIn("using lexical results instead", payload["local_search_summary"]["fallback_note"])
            self.assertEqual(payload["local_chronology_summary"]["chronology_ready_result_count"], 0)
            self.assertEqual(payload["research_grounding_summary"]["upload_ready_candidate_count"], 0)
            self.assertIn("seeded_discovery_plan", payload)
            self.assertEqual(payload["research_action_queue"][0]["action"], "run_seeded_discovery")
            self.assertEqual(payload["recommended_next_action"]["action"], "run_seeded_discovery")

    def test_research_builds_grounding_summary_and_seeded_discovery_plan(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            root.joinpath("notice.txt").write_text(
                "HACC sent written notice on March 4, 2024 and denied the review on March 8, 2024.",
                encoding="utf-8",
            )
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=root / "research_results/documents/parsed",
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_discover = engine.discover
            original_discover_legal_authorities = engine.discover_legal_authorities
            try:
                engine.discover = lambda *args, **kwargs: {
                    "status": "success",
                    "results": [{"url": "https://example.org/policies/hearing-rights"}],
                }
                engine.discover_legal_authorities = lambda *args, **kwargs: {
                    "status": "success",
                    "results": [{"title": "42 U.S.C. 1437d", "authority_source": "us_code"}],
                    "result_count": 1,
                }
                payload = engine.research(
                    "notice review date",
                    local_top_k=1,
                    web_max_results=1,
                    search_mode="lexical",
                )
            finally:
                engine.discover = original_discover
                engine.discover_legal_authorities = original_discover_legal_authorities

            grounding_summary = payload["research_grounding_summary"]
            self.assertEqual(grounding_summary["upload_ready_candidate_count"], 1)
            self.assertEqual(grounding_summary["recommended_upload_paths"], ["notice.txt"])
            self.assertGreaterEqual(grounding_summary["timeline_anchor_count"], 1)
            self.assertIn("evidence_upload_form_seed", grounding_summary)
            self.assertIn("production_evidence_intake_steps", grounding_summary)
            self.assertIn("mediator_upload_checklist", grounding_summary)
            self.assertIn("document_generation_handoff", grounding_summary)
            self.assertIn("seeded_discovery_plan", grounding_summary)
            self.assertEqual(grounding_summary["seeded_discovery_plan"]["has_web_results"], True)
            self.assertEqual(grounding_summary["seeded_discovery_plan"]["has_legal_results"], True)
            self.assertIn("example.org", grounding_summary["seeded_discovery_plan"]["recommended_domains"])
            self.assertEqual(payload["seeded_discovery_plan"]["priority"], "chronology_first")
            self.assertEqual(payload["research_action_queue"][0]["action"], "upload_local_repository_evidence")
            self.assertEqual(payload["research_action_queue"][1]["action"], "fill_chronology_gaps")
            self.assertEqual(payload["recommended_next_action"]["action"], "upload_local_repository_evidence")

    def test_research_includes_shared_legal_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_search_us_code = engine_module.search_us_code
            original_search_federal_register = engine_module.search_federal_register
            original_search_recap_documents = engine_module.search_recap_documents
            original_legal_available = engine_module.LEGAL_SCRAPERS_AVAILABLE
            try:
                engine_module.LEGAL_SCRAPERS_AVAILABLE = True
                engine_module.search_us_code = lambda query, **kwargs: [
                    {"title": "42 U.S.C. 3604", "citation": "42 U.S.C. 3604", "url": "https://example.com/uscode", "relevance_score": 0.9}
                ]
                engine_module.search_federal_register = lambda query, **kwargs: [
                    {"title": "HUD Notice", "citation": "HUD-2024-1", "url": "https://example.com/fr", "relevance_score": 0.7}
                ]
                engine_module.search_recap_documents = lambda query, **kwargs: []

                payload = engine.research("reasonable accommodation retaliation", local_top_k=1, web_max_results=1)
            finally:
                engine_module.search_us_code = original_search_us_code
                engine_module.search_federal_register = original_search_federal_register
                engine_module.search_recap_documents = original_search_recap_documents
                engine_module.LEGAL_SCRAPERS_AVAILABLE = original_legal_available

            self.assertIn("legal_discovery", payload)
            self.assertEqual(payload["legal_discovery"]["status"], "success")
            self.assertEqual(payload["legal_discovery"]["result_count"], 2)
            self.assertEqual(
                {item["authority_source"] for item in payload["legal_discovery"]["results"]},
                {"us_code", "federal_register"},
            )

    def test_discover_seeded_commoncrawl_uses_shared_adapter(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            engine = HACCResearchEngine(
                repo_root=root,
                parsed_dir=parsed_dir,
                parse_manifest_path=manifest_path,
                knowledge_graph_dir=root / "hacc_website/knowledge_graph",
            )

            original_discover_seeded_commoncrawl = engine_module.discover_seeded_commoncrawl
            try:
                calls = []

                def fake_discover_seeded_commoncrawl(queries_file, **kwargs):
                    calls.append((str(queries_file), kwargs))
                    return {"status": "success", "candidates": {"sites": {"example.org": {"top": [{"url": "https://example.org/policy.pdf"}]}}}}

                engine_module.discover_seeded_commoncrawl = fake_discover_seeded_commoncrawl
                payload = engine.discover_seeded_commoncrawl(
                    ['site:example.org "grievance policy"'],
                    cc_limit=25,
                    top_per_site=5,
                    fetch_top=1,
                    sleep_seconds=0.0,
                )
            finally:
                engine_module.discover_seeded_commoncrawl = original_discover_seeded_commoncrawl

            self.assertEqual(payload["status"], "success")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0][1]["cc_limit"], 25)
            self.assertEqual(calls[0][1]["top_per_site"], 5)
            self.assertEqual(calls[0][1]["fetch_top"], 1)

    def test_search_vector_prefers_knowledge_graph_embedding_indexes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            parsed_dir = root / "research_results/documents/parsed"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            manifest_path = root / "research_results/documents/parse_manifest.json"
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(json.dumps({"parsed_documents": []}), encoding="utf-8")

            embeddings_dir = root / "hacc_website/knowledge_graph/embeddings"
            embeddings_dir.mkdir(parents=True, exist_ok=True)
            (embeddings_dir / "hacc_policy_graph.manifest.json").write_text("{}", encoding="utf-8")
            (embeddings_dir / "hacc_text_chunks.manifest.json").write_text("{}", encoding="utf-8")

            original_search_vector_index = engine_module.search_vector_index
            calls = []
            try:
                def fake_search_vector_index(query, *, index_name, index_dir, top_k):
                    calls.append((index_name, index_dir, top_k))
                    return {
                        "status": "success",
                        "results": [
                            {
                                "id": f"{index_name}:1",
                                "text": f"match from {index_name}",
                                "metadata": {"document_id": f"{index_name}-doc"},
                                "score": 0.9 if index_name == "hacc_policy_graph" else 0.8,
                            }
                        ],
                    }

                engine_module.search_vector_index = fake_search_vector_index
                engine = HACCResearchEngine(
                    repo_root=root,
                    parsed_dir=parsed_dir,
                    parse_manifest_path=manifest_path,
                    knowledge_graph_dir=root / "hacc_website/knowledge_graph",
                )
                payload = engine.search_vector("reasonable accommodation", top_k=3)
            finally:
                engine_module.search_vector_index = original_search_vector_index

            self.assertEqual(payload["status"], "success")
            self.assertEqual(
                [item["index_name"] for item in payload["searched_indexes"]],
                ["hacc_policy_graph", "hacc_text_chunks"],
            )
            self.assertEqual(calls[0][0], "hacc_policy_graph")
            self.assertEqual(calls[1][0], "hacc_text_chunks")
            self.assertEqual(payload["results"][0]["vector_index_name"], "hacc_policy_graph")


if __name__ == "__main__":
    unittest.main()
