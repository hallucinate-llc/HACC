from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

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
            payload = engine.build_grounding_bundle(
                "reasonable accommodation hearing rights",
                top_k=1,
                claim_type="housing_discrimination",
                search_mode="lexical",
            )

            self.assertEqual(payload["status"], "success")
            self.assertEqual(len(payload["upload_candidates"]), 1)
            self.assertEqual(payload["upload_candidates"][0]["relative_path"], "README.md")
            prompts = payload["synthetic_prompts"]
            self.assertEqual(len(prompts["evidence_upload_prompts"]), 1)
            self.assertIn("Upload the evidence file", prompts["evidence_upload_prompts"][0]["text"])
            self.assertIn("Evaluate each uploaded evidence item", prompts["mediator_evaluation_prompt"])
            self.assertIn("production_upload_prompt", prompts)
            self.assertIn("intake_questionnaire_prompt", prompts)
            self.assertIn("What happened, and what adverse action did HACC take", prompts["intake_questionnaire_prompt"])
            self.assertEqual(len(prompts["intake_questions"]), 6)
            self.assertEqual(len(payload["mediator_evidence_packets"]), 1)
            self.assertEqual(payload["mediator_evidence_packets"][0]["relative_path"], "README.md")

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
            self.assertEqual(payload["results"][0]["document_id"], "vector-doc")
            self.assertEqual(len(build_calls), 1)
            self.assertEqual(len(hybrid_calls), 1)

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
            self.assertEqual(payload["results"][0]["document_id"], "doc1")
            self.assertEqual(payload["vector_status"], "unavailable")

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
            self.assertEqual(payload["results"][0]["document_id"], "housing_policy")

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
            self.assertEqual(payload["legal_discovery"]["results"][0]["authority_source"], "us_code")

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
