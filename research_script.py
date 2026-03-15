#!/usr/bin/env python3
"""
Compatibility wrapper for HACC research collection.

This script now routes search and discovery through ``hacc_research.HACCResearchEngine``
instead of maintaining a separate ad hoc web-search implementation.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Iterable, List, Optional

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_research import HACCResearchEngine


DEFAULT_QUERY_FOCUSES = [
    "diversity equity inclusion",
    "DEI",
    "fair housing",
    "racial equity",
    "social justice",
    "community engagement",
]


class HAACCResearcher:
    def __init__(
        self,
        base_url: str = "https://www.clackamas.us/housingauthority",
        allowed_domains: set[str] | None = None,
    ) -> None:
        self.base_url = base_url
        self.allowed_domains = allowed_domains or {"clackamas.us"}
        self.results_dir = Path("research_results")
        self.results_dir.mkdir(exist_ok=True)
        self.report_dir = self.results_dir / "search_reports"
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.engine = HACCResearchEngine(repo_root=REPO_ROOT)

    def _report_path(self, stem: str) -> Path:
        return self.report_dir / f"{stem}_{self.timestamp}.json"

    def _index_path(self, stem: str) -> Path:
        return self.engine.default_index_dir / f"{stem}_{self.timestamp}.summary.json"

    def _write_json(self, path: Path, payload: dict) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return str(path)

    def _build_report(self, *, report_type: str, query_runs: List[dict], commoncrawl_runs: Optional[List[dict]] = None) -> dict:
        index_payload = self.engine.build_index(output_path=self._index_path(report_type))
        report = {
            "status": "success",
            "report_type": report_type,
            "timestamp": self.timestamp,
            "base_url": self.base_url,
            "allowed_domains": sorted(self.allowed_domains),
            "query_count": len(query_runs),
            "query_runs": query_runs,
            "commoncrawl_runs": commoncrawl_runs or [],
            "index": index_payload,
            "integration_status": self.engine.integration_status(),
        }
        return report

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with (self.results_dir / "research.log").open("a", encoding="utf-8") as handle:
            handle.write(log_msg + "\n")

    def search_brave(self, query: str) -> List[dict]:
        payload = self.engine.discover(query, max_results=20, engines=["brave"])
        return list(payload.get("results", []) or [])

    def search_duckduckgo(self, query: str) -> List[dict]:
        payload = self.engine.discover(query, max_results=20, engines=["duckduckgo"])
        return list(payload.get("results", []) or [])

    def search_commoncrawl(self, domain: str) -> List[dict]:
        seeded_query = f'site:{domain} "housing authority" OR grievance OR appeal OR policy'
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as handle:
            handle.write(seeded_query + "\n")
            query_file = Path(handle.name)
        try:
            payload = self.engine.discover_seeded_commoncrawl(
                query_file,
                cc_limit=1000,
                top_per_site=50,
                fetch_top=0,
            )
        finally:
            query_file.unlink(missing_ok=True)
        sites = ((payload.get("candidates") or {}).get("sites") or {}) if isinstance(payload, dict) else {}
        site_payload = sites.get(domain) or {}
        top_results = list(site_payload.get("top", []) or [])
        if top_results:
            return top_results
        return list(site_payload.get("rows", []) or [])

    def run_seeded_search(
        self,
        queries_file: str,
        enable_brave: bool = True,
        enable_duckduckgo: bool = True,
        use_vector: bool = False,
        search_mode: str = "auto",
    ) -> List[dict]:
        path = Path(queries_file)
        if not path.exists():
            raise FileNotFoundError(queries_file)

        queries = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
        self.log(f"Loaded {len(queries)} seeded queries from {queries_file}")

        all_search_results: List[dict] = []
        for query in queries:
            engines: Optional[List[str]] = []
            if enable_brave:
                engines.append("brave")
            if enable_duckduckgo:
                engines.append("duckduckgo")
            payload = self.engine.research(
                query,
                local_top_k=10,
                web_max_results=20,
                use_vector=use_vector,
                search_mode=search_mode,
                engines=engines or None,
                domain_filter=self.allowed_domains,
            )
            all_search_results.append(payload)

        report = self._build_report(report_type="seeded_search", query_runs=all_search_results)
        report_path = self._report_path("seeded_search")
        self._write_json(report_path, report)
        self.log(f"Wrote seeded search report: {report_path}")
        return all_search_results

    async def run_full_research(self, *, use_vector: bool = False, search_mode: str = "auto") -> dict:
        self.log("=" * 80)
        self.log("Starting HACC research via shared search engine")
        self.log("=" * 80)

        query_payloads = []
        for focus in DEFAULT_QUERY_FOCUSES:
            query = f'Clackamas County Housing Authority "{focus}" site:clackamas.us'
            query_payloads.append(
                self.engine.research(
                    query,
                    local_top_k=10,
                    web_max_results=20,
                    use_vector=use_vector,
                    search_mode=search_mode,
                    engines=["brave", "duckduckgo"],
                    domain_filter=self.allowed_domains,
                )
            )

        commoncrawl_payloads = []
        for domain in sorted(self.allowed_domains):
            commoncrawl_payloads.append(
                {
                    "domain": domain,
                    "results": self.search_commoncrawl(domain),
                }
            )

        summary = self._build_report(
            report_type="research_report",
            query_runs=query_payloads,
            commoncrawl_runs=commoncrawl_payloads,
        )
        report_path = self._report_path("research_report")
        self._write_json(report_path, summary)
        self.log(f"Wrote shared-engine research report: {report_path}")
        return summary


def main(argv: Optional[Iterable[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Collect HACC research results via the shared search engine.")
    parser.add_argument("--queries-file", help="Path to a file with one search query per line.")
    parser.add_argument(
        "--commoncrawl-domain",
        action="append",
        default=["clackamas.us/housingauthority"],
        help="Domain/path to query through the discovery adapter (repeatable).",
    )
    parser.add_argument("--no-brave", action="store_true", help="Disable Brave-backed discovery.")
    parser.add_argument("--no-duckduckgo", action="store_true", help="Disable DuckDuckGo-backed discovery.")
    parser.add_argument("--use-vector", action="store_true", help="Blend lexical and vector local search.")
    parser.add_argument(
        "--search-mode",
        choices=["auto", "lexical", "hybrid", "vector"],
        default="auto",
        help="Shared search strategy for the local HACC corpus.",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    allowed_domains = {item.split("/")[0] for item in args.commoncrawl_domain}
    researcher = HAACCResearcher(allowed_domains=allowed_domains)

    if args.queries_file:
        researcher.run_seeded_search(
            args.queries_file,
            enable_brave=not args.no_brave,
            enable_duckduckgo=not args.no_duckduckgo,
            use_vector=args.use_vector,
            search_mode=args.search_mode,
        )
        return 0

    asyncio.run(researcher.run_full_research(use_vector=args.use_vector, search_mode=args.search_mode))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
