#!/usr/bin/env python3
"""report_generator.py — compatibility wrapper over complaint-generator DEI reports."""

from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.dei_report_generator import DEIReportGenerator


class ReportGenerator:
    """Compatibility wrapper preserving the older report interface."""

    def __init__(self, index_data: List[Dict] = None, output_dir: str = "research_results/"):
        self.index_data = index_data or []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    def load_index(self, index_file: str):
        with open(index_file, "r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if isinstance(payload, dict) and isinstance(payload.get("documents"), list):
            self.index_data = payload["documents"]
        elif isinstance(payload, list):
            self.index_data = payload
        else:
            self.index_data = []
        logger.info("Loaded %s documents from %s", len(self.index_data), index_file)

    def _to_dei_report_generator(self) -> DEIReportGenerator:
        generator = DEIReportGenerator(project_name="Oregon DEI References Audit")
        for doc in self.index_data:
            if not isinstance(doc, dict):
                continue
            risk_result = {
                "score": int(doc.get("risk_score", 0) or 0),
                "level": {0: "compliant", 1: "low", 2: "medium", 3: "high"}.get(int(doc.get("risk_score", 0) or 0), "unknown"),
                "dei_count": len(doc.get("dei_keywords", []) or []),
                "proxy_count": len(doc.get("proxy_keywords", []) or []),
                "binding_count": len(doc.get("binding_keywords", []) or []),
                "issues": [],
                "recommendations": [],
                "flagged_keywords": {
                    "dei": list(doc.get("dei_keywords", []) or []),
                    "proxy": list(doc.get("proxy_keywords", []) or []),
                    "binding": list(doc.get("binding_keywords", []) or []),
                },
            }
            metadata = {
                "id": doc.get("id", ""),
                "source": doc.get("file_path", ""),
                "title": doc.get("title", ""),
                "applicability_tags": list(doc.get("applicability_tags", []) or []),
                "text_length": int(doc.get("text_length", 0) or 0),
            }
            generator.add_document_analysis(risk_result, provisions=[], metadata=metadata)
        return generator

    def _summarize_high_risk(self) -> List[Dict]:
        return [doc for doc in self.index_data if int(doc.get("risk_score", 0) or 0) >= 2]

    def _summarize_medium_risk(self) -> List[Dict]:
        return [doc for doc in self.index_data if int(doc.get("risk_score", 0) or 0) == 1]

    def generate_one_page_summary(self) -> str:
        return self._to_dei_report_generator().generate_executive_summary()

    def generate_detailed_report(self) -> str:
        return self._to_dei_report_generator().generate_detailed_report()

    def save_summary(self) -> str:
        summary = self.generate_one_page_summary()
        summary_file = self.output_dir / f"FINDINGS_{self.timestamp}.txt"
        summary_file.write_text(summary, encoding="utf-8")
        logger.info("Saved summary to %s", summary_file)
        return str(summary_file)

    def save_detailed_report(self) -> str:
        report = self.generate_detailed_report()
        report_file = self.output_dir / f"DETAILED_REPORT_{self.timestamp}.txt"
        report_file.write_text(report, encoding="utf-8")
        logger.info("Saved detailed report to %s", report_file)
        return str(report_file)


if __name__ == "__main__":
    logger.info("Report generator compatibility wrapper ready.")
