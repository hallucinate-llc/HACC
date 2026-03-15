from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class WorkflowWrapperTests(unittest.TestCase):
    def test_ingest_third_party_wrapper_uses_shared_ingest_and_writes_results(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/ingest_third_party_into_corpus.py"),
            "ingest_third_party_into_corpus_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest = root / "manifest.json"
            manifest.write_text(json.dumps([]), encoding="utf-8")
            parsed_dir = root / "parsed"
            output_dir = root / "output"
            parsed_dir.mkdir(parents=True, exist_ok=True)
            output_dir.mkdir(parents=True, exist_ok=True)

            fake_record = {"status": "success", "content_type": "application/pdf"}

            class FakeIndexer:
                def __init__(self, *args, **kwargs):
                    self.index = [{"id": "doc-1"}]

                def batch_index(self):
                    return self.index

                def save_index(self):
                    path = output_dir / "index.json"
                    path.write_text("{}", encoding="utf-8")
                    return str(path)

                def export_csv_summary(self):
                    path = output_dir / "summary.csv"
                    path.write_text("", encoding="utf-8")
                    return str(path)

            class FakeReporter:
                def __init__(self, *args, **kwargs):
                    pass

                def load_index(self, index_file):
                    self.index_file = index_file

                def save_summary(self):
                    path = output_dir / "summary.txt"
                    path.write_text("summary", encoding="utf-8")
                    return str(path)

                def save_detailed_report(self):
                    path = output_dir / "detailed.txt"
                    path.write_text("detail", encoding="utf-8")
                    return str(path)

            with patch.object(module, "DEFAULT_MANIFEST", manifest):
                with patch.object(module, "PARSED_DIR", parsed_dir):
                    with patch.object(module, "OUTPUT_DIR", output_dir):
                        with patch.object(module, "ingest_download_manifest", return_value={"status": "success", "records": [fake_record]}):
                            with patch.object(module, "DocumentIndexer", FakeIndexer):
                                with patch.object(module, "ReportGenerator", FakeReporter):
                                    with patch("sys.argv", ["ingest_third_party_into_corpus.py", "--manifest", str(manifest)]):
                                        module.main()

            results = list(output_dir.glob("workflow_results_third_party_*.json"))
            self.assertEqual(len(results), 1)
            payload = json.loads(results[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["ingested_records"], 1)
            self.assertEqual(payload["parsed_pdf"], 1)

    def test_run_collection_orchestrator_uses_wrappers_for_local_pdf_dir(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/run_collection.py"),
            "run_collection_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdf_dir = root / "pdfs"
            pdf_dir.mkdir(parents=True, exist_ok=True)
            (pdf_dir / "sample.pdf").write_bytes(b"%PDF-1.7 sample")

            class FakeParser:
                def parse_pdf(self, pdf_path, metadata):
                    return pdf_path

            class FakeIndexer:
                def __init__(self):
                    self.index = [{"id": "doc-1"}]

                def batch_index(self):
                    return self.index

                def save_index(self):
                    path = root / "index.json"
                    path.write_text("{}", encoding="utf-8")
                    return str(path)

                def export_csv_summary(self):
                    path = root / "summary.csv"
                    path.write_text("", encoding="utf-8")
                    return str(path)

            class FakeReporter:
                def load_index(self, index_file):
                    self.index_file = index_file

                def save_summary(self):
                    path = root / "summary.txt"
                    path.write_text("summary", encoding="utf-8")
                    return str(path)

                def save_detailed_report(self):
                    path = root / "detailed.txt"
                    path.write_text("detail", encoding="utf-8")
                    return str(path)

                def generate_one_page_summary(self):
                    return "summary"

            orchestrator = module.CollectionOrchestrator()
            orchestrator.parser = FakeParser()
            orchestrator.indexer = FakeIndexer()
            orchestrator.reporter = FakeReporter()

            with patch.object(orchestrator, "collect_from_brave_api", return_value=[]):
                with patch.object(orchestrator, "collect_from_web_simple", return_value=[]):
                    results = orchestrator.run_full_workflow(pdf_dir=str(pdf_dir))

            self.assertEqual(results["pdfs_parsed"], 1)
            self.assertEqual(results["documents_indexed"], 1)

    def test_report_generator_wrapper_loads_index_payload_and_writes_legacy_files(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/report_generator.py"),
            "report_generator_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            index_file = root / "index.json"
            index_file.write_text(
                json.dumps(
                    {
                        "documents": [
                            {
                                "id": "doc-1",
                                "file_path": "/tmp/doc-1.txt",
                                "risk_score": 2,
                                "dei_keywords": ["equity"],
                                "proxy_keywords": ["lived experience"],
                                "binding_keywords": ["must"],
                                "applicability_tags": ["housing"],
                                "text_length": 120,
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            generator = module.ReportGenerator(output_dir=str(root))
            generator.load_index(str(index_file))
            summary_file = Path(generator.save_summary())
            detailed_file = Path(generator.save_detailed_report())

            self.assertTrue(summary_file.exists())
            self.assertTrue(detailed_file.exists())
            self.assertIn("EXECUTIVE SUMMARY", summary_file.read_text(encoding="utf-8"))

    def test_deep_analysis_wrapper_uses_upstream_extractor_and_writes_outputs(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/deep_analysis.py"),
            "deep_analysis_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            raw_docs = root / "raw_documents"
            analysis_dir = root / "analysis"
            extract_dir = analysis_dir / "extracts"
            raw_docs.mkdir(parents=True, exist_ok=True)
            analysis_dir.mkdir(parents=True, exist_ok=True)
            extract_dir.mkdir(parents=True, exist_ok=True)
            (raw_docs / "ORS_Chapter_456_Housing_Authorities.html").write_text(
                "<html><body>456.001 Housing authority must support fair housing and equity.</body></html>",
                encoding="utf-8",
            )
            (analysis_dir / "dei_findings.json").write_text(
                json.dumps([{"source": "ORS Chapter 456", "terms_found": ["equity"], "relevance_score": 2}]),
                encoding="utf-8",
            )

            with patch.object(module, "RAW_DOCS_DIR", raw_docs):
                with patch.object(module, "ANALYSIS_DIR", analysis_dir):
                    with patch.object(module, "EXTRACT_DIR", extract_dir):
                        extractor = module.ProvisionExtractor()
                        provisions = extractor.analyze_key_documents()
                        matrix = extractor.create_compliance_matrix()

            self.assertEqual(len(provisions), 1)
            self.assertTrue((extract_dir / "statutory_provisions.json").exists())
            self.assertTrue((extract_dir / "statutory_provisions_report.txt").exists())
            self.assertTrue((extract_dir / "compliance_matrix.txt").exists())
            self.assertIn("COMPLIANCE MATRIX", matrix)

    def test_kg_followup_search_wrapper_uses_shared_engine(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/kg_followup_search.py"),
            "kg_followup_search_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kg_path = root / "kg.json"
            audit_csv = root / "audit.csv"
            out_md = root / "followup.md"
            out_csv = root / "followup.csv"
            out_queue = root / "followup.txt"
            kg_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"id": "ent:1", "label": "Housing Authority", "type": "government_body"},
                        ],
                        "edges": [
                            {"type": "MENTIONS", "target": "ent:1", "weight": 3},
                        ],
                    }
                ),
                encoding="utf-8",
            )
            audit_csv.write_text("document_id,assessment,classification,domain,url\n", encoding="utf-8")

            class FakeEngine:
                def __init__(self, *args, **kwargs):
                    pass

                def search_local(self, query, top_k=5):
                    return {
                        "results": [
                            {
                                "document_id": "doc-1",
                                "source_path": "/tmp/doc-1.txt",
                                "snippet": "Housing Authority procurement policy",
                            }
                        ]
                    }

                def load_corpus(self):
                    return ["doc-1"]

            with patch.object(module, "KG_JSON", str(kg_path)):
                with patch.object(module, "AUDIT_CSV", str(audit_csv)):
                    with patch.object(module, "OUT_MD", str(out_md)):
                        with patch.object(module, "OUT_CSV", str(out_csv)):
                            with patch.object(module, "OUT_QUEUE", str(out_queue)):
                                with patch.object(module, "HACCResearchEngine", FakeEngine):
                                    module.main()

            self.assertTrue(out_md.exists())
            self.assertTrue(out_csv.exists())
            self.assertTrue(out_queue.exists())

    def test_kg_seed_pack_wrapper_delegates_to_violation_seed_builder(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/kg_seed_pack.py"),
            "kg_seed_pack_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kg_path = root / "kg.json"
            out_json = root / "seed_pack.json"
            out_txt = root / "seed_queries.txt"
            kg_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"id": "ent:1", "label": "Housing Authority", "type": "government_body"},
                            {"id": "ent:2", "label": "Procurement Policy", "type": "policy_or_law"},
                        ],
                        "edges": [],
                    }
                ),
                encoding="utf-8",
            )

            class FakeEntity:
                def __init__(self, label, type, score):
                    self.label = label
                    self.type = type
                    self.score = score

            fake_module = type(
                "FakeViolationModule",
                (),
                {
                    "load_kg_nodes": staticmethod(lambda path: json.loads(Path(path).read_text(encoding="utf-8")).get("nodes_by_label", {})),
                    "entity_label_ok": staticmethod(lambda label: True),
                    "ENTITY_TYPE_ALLOW": {"government_body", "policy_or_law", "entity"},
                    "CATEGORY_TERMS": {"selection_contracting": ["procurement"], "proxies": ["equity lens"], "retaliation_protections": ["retaliation"]},
                    "DEFAULT_SITES": ["clackamas.us"],
                    "Entity": FakeEntity,
                    "make_queries": staticmethod(lambda **kwargs: ["site:clackamas.us \"Housing Authority\" procurement"]),
                    "datetime": __import__("datetime").datetime,
                },
            )

            nodes_by_label = {
                "housing authority": {"label": "Housing Authority", "type": "government_body"},
                "procurement policy": {"label": "Procurement Policy", "type": "policy_or_law"},
            }

            with patch.object(module, "KG_JSON", str(kg_path)):
                with patch.object(module, "OUT_JSON", str(out_json)):
                    with patch.object(module, "OUT_TXT", str(out_txt)):
                        with patch.object(module, "violation_seed_queries", fake_module):
                            with patch.object(fake_module, "load_kg_nodes", return_value=nodes_by_label):
                                module.main()

            self.assertTrue(out_json.exists())
            self.assertTrue(out_txt.exists())
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["generated_by"], "kg_violation_seed_queries.make_queries")

    def test_kg_violation_seed_queries_wrapper_uses_upstream_seed_generator(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/kg_violation_seed_queries.py"),
            "kg_violation_seed_queries_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            reviews_path = root / "reviews.csv"
            kg_path = root / "kg.json"
            results_dir = root / "research_results"
            results_dir.mkdir(parents=True, exist_ok=True)

            reviews_path.write_text(
                "\n".join(
                    [
                        "document_id,max_checklist_score,assessment,max_checklist_category,top_entities",
                        'doc-1,3,likely-violation-indicator,selection_contracting,"Housing Authority(3); Procurement Policy(2)"',
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            kg_path.write_text(
                json.dumps(
                    {
                        "nodes": [
                            {"id": "ent:1", "label": "Housing Authority", "type": "government_body"},
                            {"id": "ent:2", "label": "Procurement Policy", "type": "policy_or_law"},
                        ]
                    }
                ),
                encoding="utf-8",
            )

            old_cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch("sys.argv", ["kg_violation_seed_queries.py", "--reviews", str(reviews_path), "--kg", str(kg_path)]):
                    module.main()
            finally:
                os.chdir(old_cwd)

            pack_files = list(results_dir.glob("kg_violation_seed_pack_*.json"))
            query_files = list(results_dir.glob("kg_violation_seed_queries_*.txt"))
            self.assertEqual(len(pack_files), 1)
            self.assertEqual(len(query_files), 1)

            payload = json.loads(pack_files[0].read_text(encoding="utf-8"))
            self.assertEqual(payload["generated_by"], "complaint_analysis.research_seed_generator")
            self.assertEqual(payload["selected_docs"], 1)
            self.assertTrue(payload["queries"])

    def test_kg_prioritize_queues_uses_consolidated_entity_loader(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/kg_prioritize_queues.py"),
            "kg_prioritize_queues_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            kg_path = root / "kg.json"
            queue_path = root / "sample_queue.json"
            out_json = root / "prioritized.json"
            out_csv = root / "prioritized.csv"
            kg_path.write_text(json.dumps({"nodes": []}), encoding="utf-8")
            queue_path.write_text(json.dumps({"items": [{"url": "https://clackamas.us/housing-authority/procurement-policy.pdf"}]}), encoding="utf-8")

            fake_violation_module = type(
                "FakeViolationModule",
                (),
                {
                    "load_kg_nodes": staticmethod(lambda path: {"housing authority": {"label": "Housing Authority", "type": "government_body"}}),
                    "ENTITY_TYPE_ALLOW": {"government_body"},
                    "entity_label_ok": staticmethod(lambda label: True),
                },
            )

            with patch.object(module, "KG_JSON", str(kg_path)):
                with patch.object(module, "QUEUE_GLOBS", [str(queue_path)]):
                    with patch.object(module, "OUT_JSON", str(out_json)):
                        with patch.object(module, "OUT_CSV", str(out_csv)):
                            with patch.object(module, "violation_seed_queries", fake_violation_module):
                                module.main()

            self.assertTrue(out_json.exists())
            self.assertTrue(out_csv.exists())
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["items"]), 1)

    def test_generate_third_party_download_queue_wrapper_uses_shared_queue_builder(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/generate_third_party_download_queue.py"),
            "generate_third_party_download_queue_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            candidates_path = root / "candidates.json"
            output_path = root / "queue.json"
            candidates_path.write_text(json.dumps({"candidates": [{"candidate_type": "domain", "candidate": "example.org"}]}), encoding="utf-8")

            fake_queue = {"domain_count": 1, "items": [{"domain": "example.org", "score": 60}], "notes": "ok"}

            with patch.object(module, "CANDIDATES_JSON", candidates_path):
                with patch.object(module, "OUTPUT_JSON", output_path):
                    with patch.object(module, "build_download_queue", return_value=fake_queue):
                        module.main()

            payload = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["source"], str(candidates_path))
            self.assertEqual(payload["domain_count"], 1)

    def test_filter_third_party_download_queue_wrapper_uses_shared_filter(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/filter_third_party_download_queue.py"),
            "filter_third_party_download_queue_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            in_path = root / "queue.json"
            out_path = root / "filtered.json"
            summary_path = root / "summary.json"
            in_path.write_text(json.dumps({"items": [{"domain": "example.org", "score": 60}]}), encoding="utf-8")

            fake_filtered = {"domain_count": 1, "items": [{"domain": "example.org", "score": 60}]}
            fake_summary = {"output_domain_count": 1}

            with patch.object(module, "filter_download_queue", return_value=(fake_filtered, fake_summary)):
                with patch(
                    "sys.argv",
                    [
                        "filter_third_party_download_queue.py",
                        "--in",
                        str(in_path),
                        "--out",
                        str(out_path),
                        "--summary",
                        str(summary_path),
                    ],
                ):
                    module.main()

            payload = json.loads(out_path.read_text(encoding="utf-8"))
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["source"], str(in_path))
            self.assertEqual(summary["output"], str(out_path))

    def test_download_third_party_queue_wrapper_uses_shared_downloader(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/download_third_party_queue.py"),
            "download_third_party_queue_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            queue_path = root / "queue.json"
            manifest_json = root / "manifest.json"
            manifest_csv = root / "manifest.csv"
            queue_path.write_text(json.dumps({"items": [{"domain": "example.org", "seed_urls": ["https://example.org"]}]}), encoding="utf-8")

            with patch.object(
                module,
                "download_queue",
                return_value={"domains_processed": 1, "ok_downloads": 1, "manifest_rows": 1, "manifest_json": str(manifest_json), "manifest_csv": str(manifest_csv)},
            ) as patched:
                with patch(
                    "sys.argv",
                    [
                        "download_third_party_queue.py",
                        "--queue",
                        str(queue_path),
                        "--manifest-json",
                        str(manifest_json),
                        "--manifest-csv",
                        str(manifest_csv),
                    ],
                ):
                    module.main()

            self.assertTrue(patched.called)

    def test_extract_third_party_candidates_wrapper_uses_shared_bootstrap_workflow(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/extract_third_party_candidates.py"),
            "extract_third_party_candidates_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            workspace_root = root / "workspace"
            output_json = root / "third_party_candidates.json"
            output_csv = root / "third_party_candidates.csv"
            workspace_root.mkdir(parents=True, exist_ok=True)

            fake_payload = {"scanned_files": 1, "candidate_count": 1, "candidates": [{"candidate": "example.org"}]}

            with patch.object(module, "WORKSPACE_ROOT", workspace_root):
                with patch.object(module, "OUTPUT_JSON", output_json):
                    with patch.object(module, "OUTPUT_CSV", output_csv):
                        with patch.object(module, "extract_third_party_candidates_from_corpus", return_value=fake_payload):
                            with patch.object(module, "write_candidates_csv") as write_csv:
                                module.main()

            payload = json.loads(output_json.read_text(encoding="utf-8"))
            self.assertEqual(payload["candidate_count"], 1)
            self.assertTrue(write_csv.called)

    def test_extract_external_documents_wrapper_uses_shared_bootstrap_workflow(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/extract_external_documents_from_quantum_pages.py"),
            "extract_external_documents_from_quantum_pages_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            manifest_path = root / "manifest.json"
            out_queue = root / "queue.json"
            out_evidence = root / "evidence.json"
            manifest_path.write_text("[]", encoding="utf-8")

            fake_queue = {"stats": {"candidate_domains": 1}, "items": [{"domain": "example.org"}]}
            fake_evidence = {"rows": [{"candidate_url": "https://example.org/policy.pdf"}]}

            with patch.object(module, "load_manifest_rows", return_value=[]):
                with patch.object(module, "extract_external_document_queue", return_value=(fake_queue, fake_evidence)):
                    with patch(
                        "sys.argv",
                        [
                            "extract_external_documents_from_quantum_pages.py",
                            "--manifest",
                            str(manifest_path),
                            "--out-queue",
                            str(out_queue),
                            "--out-evidence",
                            str(out_evidence),
                        ],
                    ):
                        module.main()

            queue_payload = json.loads(out_queue.read_text(encoding="utf-8"))
            evidence_payload = json.loads(out_evidence.read_text(encoding="utf-8"))
            self.assertEqual(queue_payload["source"]["manifest"], str(manifest_path))
            self.assertEqual(evidence_payload["source"]["manifest"], str(manifest_path))

    def test_seeded_commoncrawl_wrapper_uses_shared_search_adapter(self) -> None:
        module = _load_module(
            Path("/home/barberb/HACC/research_data/scripts/seeded_commoncrawl_discovery.py"),
            "seeded_commoncrawl_discovery_test",
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            queries_file = root / "queries.txt"
            results_dir = root / "research_results"
            queries_file.write_text('site:example.org "procurement policy"\n', encoding="utf-8")
            results_dir.mkdir(parents=True, exist_ok=True)

            fake_result = {
                "status": "success",
                "candidates": {"sites": {"example.org": {"top": [{"url": "https://example.org/policy.pdf"}]}}},
                "fetched": {"sites": {"example.org": {"rows": [{"url": "https://example.org/policy.pdf"}]}}},
            }

            old_cwd = os.getcwd()
            try:
                os.chdir(root)
                with patch.object(module, "discover_seeded_commoncrawl", return_value=fake_result):
                    with patch(
                        "sys.argv",
                        [
                            "seeded_commoncrawl_discovery.py",
                            "--queries-file",
                            str(queries_file),
                            "--fetch-top",
                            "1",
                        ],
                    ):
                        module.main()
            finally:
                os.chdir(old_cwd)

            self.assertEqual(len(list(results_dir.glob("seeded_commoncrawl_candidates_*.json"))), 1)
            self.assertEqual(len(list(results_dir.glob("seeded_commoncrawl_fetch_*.json"))), 1)


if __name__ == "__main__":
    unittest.main()
