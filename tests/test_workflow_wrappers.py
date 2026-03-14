from __future__ import annotations

import importlib.util
import json
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


if __name__ == "__main__":
    unittest.main()
