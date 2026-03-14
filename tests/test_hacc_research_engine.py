from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from hacc_research import HACCResearchEngine


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


if __name__ == "__main__":
    unittest.main()
