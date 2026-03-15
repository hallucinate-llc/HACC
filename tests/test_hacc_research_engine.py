from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hacc_research import HACCResearchEngine
from hacc_research import engine as engine_module


class HACCResearchEngineTests(unittest.TestCase):
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
