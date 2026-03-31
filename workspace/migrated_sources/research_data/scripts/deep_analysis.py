#!/usr/bin/env python3
"""Deep analysis wrapper over complaint-generator complaint_analysis modules."""

from __future__ import annotations

import json
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))

from complaint_analysis.dei_provision_extractor import DEIProvisionExtractor
from complaint_analysis.dei_risk_scoring import DEIRiskScorer


BASE_DIR = Path(__file__).parent.parent
RAW_DOCS_DIR = BASE_DIR / "raw_documents"
ANALYSIS_DIR = BASE_DIR / "analysis"
EXTRACT_DIR = ANALYSIS_DIR / "extracts"


class ProvisionExtractor:
    """Compatibility wrapper preserving the older deep-analysis workflow."""

    def __init__(self):
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        self.extractor = DEIProvisionExtractor()
        self.risk_scorer = DEIRiskScorer()
        self.extracts = []

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

    def extract_ors_provisions(self, filepath, chapter):
        self.log(f"Extracting provisions from ORS Chapter {chapter}...")
        html = Path(filepath).read_text(encoding="utf-8")
        text = re.sub(r"<script\b[^>]*>.*?</script>", " ", html, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<style\b[^>]*>.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</(p|div|section|article|li|tr|h[1-6])>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)

        provisions = self.extractor.extract_statute_provisions(text, chapter)
        normalized = []
        for provision in provisions:
            normalized.append(
                {
                    "statute": provision.get("statute", ""),
                    "chapter": chapter,
                    "text": provision.get("text", ""),
                    "found_terms": list(provision.get("dei_terms", []) or [])[:10],
                    "binding_terms": list(provision.get("binding_terms", []) or []),
                    "is_binding": bool(provision.get("is_binding", False)),
                }
            )
        self.log(f"  Found {len(normalized)} relevant provisions")
        return normalized

    def analyze_key_documents(self):
        self.log("Starting deep analysis of key documents...")
        key_docs = [
            ("ORS_Chapter_456_Housing_Authorities.html", "456", "Housing Authorities"),
            ("ORS_Chapter_659A_Discrimination_Definitions_and_Procedures.html", "659A", "Discrimination"),
            ("ORS_Chapter_279A_Public_Contracting___General.html", "279A", "Public Contracting General"),
            ("ORS_Chapter_279C_Public_Contracting___Construction.html", "279C", "Public Contracting Construction"),
        ]

        all_provisions = []
        for filename, chapter, description in key_docs:
            filepath = RAW_DOCS_DIR / filename
            if filepath.exists():
                self.log(f"\nAnalyzing: {description} (ORS Chapter {chapter})")
                provisions = self.extract_ors_provisions(filepath, chapter)
                for provision in provisions:
                    provision["source"] = description
                    all_provisions.append(provision)

        (EXTRACT_DIR / "statutory_provisions.json").write_text(json.dumps(all_provisions, indent=2), encoding="utf-8")
        self.generate_provision_report(all_provisions)
        return all_provisions

    def generate_provision_report(self, provisions):
        self.log("Generating provision report...")
        report_lines = [
            "=" * 100,
            "SPECIFIC OREGON STATUTORY PROVISIONS RELATED TO DEI",
            "Potentially Binding on Housing Authority of Clackamas County",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 100,
            "",
        ]
        grouped = {}
        for provision in provisions:
            grouped.setdefault(provision.get("source", "Unknown"), []).append(provision)

        for source, items in grouped.items():
            report_lines.extend(
                [
                    f"\n{'=' * 100}",
                    f"{source.upper()} - {len(items)} Relevant Provision(s)",
                    "=" * 100,
                ]
            )
            for index, provision in enumerate(items, 1):
                report_lines.append(f"\n[{index}] {provision.get('statute', '')}")
                report_lines.append(f"    Terms Found: {', '.join(provision.get('found_terms', []))}")
                if provision.get("binding_terms"):
                    report_lines.append(f"    Binding Terms: {', '.join(provision.get('binding_terms', []))}")
                report_lines.append("    Text Preview:")
                for line in str(provision.get("text", "")).splitlines()[:15]:
                    line = line.strip()
                    if line:
                        report_lines.append(f"      {line}")
                report_lines.append("")

        report_text = "\n".join(report_lines)
        (EXTRACT_DIR / "statutory_provisions_report.txt").write_text(report_text, encoding="utf-8")
        self.log("Provision report complete")
        return report_text

    def create_compliance_matrix(self):
        self.log("Creating compliance matrix...")
        findings_path = ANALYSIS_DIR / "dei_findings.json"
        if not findings_path.exists():
            self.log("No findings file found")
            return

        findings = json.loads(findings_path.read_text(encoding="utf-8"))
        matrix = [
            "=" * 120,
            "COMPLIANCE MATRIX - DEI REQUIREMENTS FOR HOUSING AUTHORITY OF CLACKAMAS COUNTY",
            "=" * 120,
            "",
            f"{'SOURCE':<40} | {'BINDING?':<10} | {'KEY TERMS':<40} | SCORE",
            "-" * 120,
        ]

        for finding in findings[:20]:
            source = str(finding.get("source", ""))[:39]
            risk = self.risk_scorer.calculate_risk(
                json.dumps(finding),
                metadata={"source": source},
            )
            binding = "LIKELY" if any(x in source for x in ["ORS", "OAR", "Chapter"]) else "REVIEW"
            if "Federal" in source or "HUD" in source:
                binding = "FEDERAL"
            terms = ", ".join((finding.get("terms_found") or [])[:3])[:39]
            score = int(risk.get("score", finding.get("relevance_score", 0)) or 0)
            matrix.append(f"{source:<40} | {binding:<10} | {terms:<40} | {score:>5}")

        matrix.extend(
            [
                "",
                "LEGEND:",
                "  LIKELY  = Oregon statute (ORS) or administrative rule (OAR) - likely binding",
                "  FEDERAL = Federal requirement - binding through HUD funding/oversight",
                "  REVIEW  = Agency guidance or executive order - review for applicability",
                "",
            ]
        )

        matrix_text = "\n".join(matrix)
        (EXTRACT_DIR / "compliance_matrix.txt").write_text(matrix_text, encoding="utf-8")
        print("\n" + matrix_text)
        return matrix_text


def main():
    print("\n" + "=" * 100)
    print("DEEP ANALYSIS - EXTRACTING SPECIFIC DEI PROVISIONS")
    print("=" * 100 + "\n")
    extractor = ProvisionExtractor()
    provisions = extractor.analyze_key_documents()
    extractor.create_compliance_matrix()
    print("\n" + "=" * 100)
    print("DEEP ANALYSIS COMPLETE")
    print("=" * 100)
    print(f"\nExtracted {len(provisions)} specific statutory provisions")
    print(f"\nOutput files:")
    print(f"  • {EXTRACT_DIR}/statutory_provisions.json")
    print(f"  • {EXTRACT_DIR}/statutory_provisions_report.txt")
    print(f"  • {EXTRACT_DIR}/compliance_matrix.txt")
    print()


if __name__ == "__main__":
    main()
