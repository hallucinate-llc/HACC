#!/usr/bin/env python3
"""
Compatibility wrapper for the old enhanced HACC research flow.

This now delegates discovery and local corpus search to ``hacc_research.HACCResearchEngine``.
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Optional

REPO_ROOT = Path(__file__).resolve().parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from hacc_research import HACCResearchEngine


COMPREHENSIVE_QUERIES = [
    'site:clackamas.us/housingauthority diversity',
    'site:clackamas.us/housingauthority equity',
    'site:clackamas.us/housingauthority inclusion',
    'site:clackamas.us/housingauthority DEI',
    'site:clackamas.us/housingauthority "racial equity"',
    'site:clackamas.us/housingauthority "social justice"',
    'site:clackamas.us/housingauthority "fair housing"',
    'site:clackamas.us/housingauthority "marginalized"',
    'site:clackamas.us/housingauthority "underserved"',
    'site:clackamas.us/housingauthority "BIPOC"',
    'site:clackamas.us "diversity" housing',
    'site:clackamas.us "equity plan"',
    'site:clackamas.us "racial equity toolkit"',
]


class EnhancedHAACCResearcher:
    def __init__(self) -> None:
        self.base_urls = [
            "https://www.clackamas.us/housingauthority",
            "https://www.clackamas.us",
        ]
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

    def log(self, message: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with (self.results_dir / "research.log").open("a", encoding="utf-8") as handle:
            handle.write(log_msg + "\n")

    async def run_comprehensive_research(self, *, use_vector: bool = False) -> dict:
        self.log("=" * 80)
        self.log("COMPREHENSIVE HACC RESEARCH VIA SHARED ENGINE")
        self.log("=" * 80)

        payloads: List[dict] = []
        for query in COMPREHENSIVE_QUERIES:
            payloads.append(
                self.engine.research(
                    query,
                    local_top_k=15,
                    web_max_results=25,
                    use_vector=use_vector,
                    engines=["brave", "duckduckgo"],
                    domain_filter=["clackamas.us"],
                    scrape=True,
                )
            )

        summary = {
            "status": "success",
            "report_type": "comprehensive_research",
            "timestamp": self.timestamp,
            "query_count": len(COMPREHENSIVE_QUERIES),
            "base_urls": list(self.base_urls),
            "query_runs": payloads,
            "index": self.engine.build_index(output_path=self._index_path("hacc_enhanced_index")),
            "integration_status": self.engine.integration_status(),
        }
        summary_path = self._report_path("comprehensive_report")
        self._write_json(summary_path, summary)
        self.log(f"Wrote comprehensive shared-engine report: {summary_path}")
        return summary


def main(argv: Optional[List[str]] = None) -> int:
    use_vector = bool(argv and "--use-vector" in argv)
    researcher = EnhancedHAACCResearcher()
    asyncio.run(researcher.run_comprehensive_research(use_vector=use_vector))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
