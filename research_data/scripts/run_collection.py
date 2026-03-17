#!/usr/bin/env python3
"""
run_collection.py — compatibility workflow wrapper over shared discovery/download APIs.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from integrations.ipfs_datasets.search import search_multi_engine_web
from download_manager import DownloadManager
from hacc_research import HACCResearchEngine
from parse_pdfs import PDFParser
from index_and_tag import DocumentIndexer
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


DEFAULT_QUERIES = [
    'site:clackamas.us "housing authority"',
    'site:clackamas.us filetype:pdf "housing" policy',
    'site:clackamas.us filetype:pdf "affordable housing" OR "housing assistance"',
    'site:clackamas.us filetype:pdf board minutes housing',
    'site:clackamas.us filetype:pdf housing diversity OR equity',
    'site:clackamas.us filetype:pdf procurement policy',
    'site:clackamas.us filetype:pdf hiring OR employment',
    'site:clackamas.us filetype:pdf diversity OR "equal opportunity"',
    'site:clackamas.us "coordinated housing access" OR CCHA',
]


class CollectionOrchestrator:
    """Orchestrate collection, parsing, indexing, and reporting via shared APIs."""

    def __init__(self):
        self.dm = DownloadManager()
        self.parser = PDFParser()
        self.indexer = DocumentIndexer()
        self.reporter = ReportGenerator()
        self.engine = HACCResearchEngine(repo_root=REPO_ROOT)
        self.allowed_domains = ["clackamas.us"]

    def collect_from_brave_api(
        self,
        *,
        max_results_per_query: int = 10,
        engines: Optional[Sequence[str]] = None,
        domain_filter: Optional[Sequence[str]] = None,
    ) -> List[Dict]:
        logger.info("Starting shared-engine discovery collection...")
        urls_found: List[Dict] = []
        seen: set[str] = set()
        configured_engines = list(engines or ["brave", "duckduckgo"])
        configured_domains = list(domain_filter or self.allowed_domains)

        for query in DEFAULT_QUERIES:
            try:
                payload = self.engine.discover(
                    query,
                    max_results=max_results_per_query,
                    engines=configured_engines,
                    domain_filter=configured_domains,
                    scrape=False,
                )
                results = list(payload.get("results", []) or [])
            except Exception as exc:
                logger.warning("Shared discovery failed for query %s: %s", query, exc)
                try:
                    results = search_multi_engine_web(query, max_results=max_results_per_query)
                except Exception as fallback_exc:
                    logger.warning("Fallback search failed for query %s: %s", query, fallback_exc)
                    continue

            for result in results:
                url = str(result.get("url") or "")
                if not url or url in seen:
                    continue
                seen.add(url)
                if ".pdf" not in url.lower() and "pdf" not in str((result.get("metadata") or {}).get("content_type", "")).lower():
                    continue
                urls_found.append(
                    {
                        "url": url,
                        "title": result.get("title", ""),
                        "description": result.get("description", ""),
                        "source": str(result.get("source_type") or "search"),
                        "query": query,
                    }
                )
        logger.info("Discovered %s candidate PDF URL(s)", len(urls_found))
        return urls_found

    def collect_from_web_simple(self) -> List[Dict]:
        logger.info("Falling back to query inventory only.")
        return [{"query": query, "description": "search query"} for query in DEFAULT_QUERIES]

    def run_full_workflow(self, pdf_dir: str | None = None) -> Dict:
        logger.info("=" * 80)
        logger.info("Starting DEI Compliance Collection & Analysis Workflow")
        logger.info("=" * 80)

        logger.info("\n[STEP 1] Identifying documents to collect...")
        queries = self.collect_from_brave_api()
        if not queries:
            queries = self.collect_from_web_simple()

        logger.info("\n[STEP 2] Downloading PDFs...")
        pdf_files: List[Path] = []
        if queries and isinstance(queries[0], dict) and "url" in queries[0]:
            for url_item in queries:
                filepath = self.dm.download_pdf(url_item["url"], url_item.get("source", "search"))
                if filepath:
                    pdf_files.append(Path(filepath))
        elif pdf_dir and Path(pdf_dir).exists():
            logger.info("Using local PDF directory: %s", pdf_dir)
            pdf_files = list(Path(pdf_dir).glob("*.pdf"))
        else:
            logger.info("No PDFs discovered. Provide --pdf-dir to parse local files.")

        logger.info("Downloaded/available: %s PDF(s)", len(pdf_files))

        logger.info("\n[STEP 3] Parsing PDFs...")
        parsed_count = 0
        for pdf_file in pdf_files:
            metadata = {
                "url": f"file://{pdf_file}",
                "source": "local_file" if pdf_dir else "downloaded_file",
                "download_date": datetime.now().isoformat(),
            }
            if self.parser.parse_pdf(str(pdf_file), metadata):
                parsed_count += 1
        logger.info("Parsed %s PDFs", parsed_count)

        logger.info("\n[STEP 4] Indexing and tagging documents...")
        self.indexer.batch_index()
        index_file = self.indexer.save_index()
        csv_file = self.indexer.export_csv_summary()

        logger.info("\n[STEP 5] Generating reports...")
        self.reporter.load_index(index_file)
        summary_file = self.reporter.save_summary()
        detailed_file = self.reporter.save_detailed_report()

        logger.info("\n%s", "=" * 80)
        logger.info("SUMMARY REPORT")
        logger.info("%s", "=" * 80)
        logger.info(self.reporter.generate_one_page_summary())

        results = {
            "queries_identified": len(queries),
            "pdfs_parsed": parsed_count,
            "documents_indexed": len(self.indexer.index),
            "index_file": index_file,
            "csv_file": csv_file,
            "summary_file": summary_file,
            "detailed_report_file": detailed_file,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info("\n%s", "=" * 80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("%s", "=" * 80)
        logger.info("Results: %s", json.dumps(results, indent=2))
        return results


def main() -> None:
    parser = argparse.ArgumentParser(description="DEI Compliance Collection & Analysis Workflow")
    parser.add_argument(
        "--pdf-dir",
        type=str,
        help="Directory containing PDFs to parse (e.g., research_results/documents/raw/)",
    )
    parser.add_argument(
        "--brave-key",
        type=str,
        help="Brave API key (or set BRAVE_API_KEY env var)",
    )
    args = parser.parse_args()

    if args.brave_key:
        os.environ["BRAVE_API_KEY"] = args.brave_key

    orchestrator = CollectionOrchestrator()
    results = orchestrator.run_full_workflow(pdf_dir=args.pdf_dir)

    results_file = Path("research_results") / f"workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w", encoding="utf-8") as handle:
        json.dump(results, handle, indent=2)
    logger.info("\nResults saved to %s", results_file)


if __name__ == "__main__":
    main()
