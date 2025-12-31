#!/usr/bin/env python3
"""
report_generator.py — Generate one-page findings and detailed reports from indexed documents.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ReportGenerator:
    """Generate findings reports from document index."""
    
    def __init__(self, index_data: List[Dict] = None, output_dir: str = "research_results/"):
        self.index_data = index_data or []
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    def load_index(self, index_file: str):
        """Load index from JSON file."""
        with open(index_file, 'r') as f:
            self.index_data = json.load(f)
        logger.info(f"Loaded {len(self.index_data)} documents from {index_file}")
    
    def _summarize_high_risk(self) -> List[Dict]:
        """Get high-risk documents (score >= 2)."""
        return [doc for doc in self.index_data if doc.get('risk_score', 0) >= 2]
    
    def _summarize_medium_risk(self) -> List[Dict]:
        """Get medium-risk documents (score = 1)."""
        return [doc for doc in self.index_data if doc.get('risk_score', 0) == 1]
    
    def generate_one_page_summary(self) -> str:
        """Generate a one-page executive summary."""
        high_risk = self._summarize_high_risk()
        medium_risk = self._summarize_medium_risk()
        
        summary = f"""
================================================================================
FINDINGS SUMMARY — Oregon DEI References Audit
Generated: {self.timestamp}
================================================================================

SCOPE
- Search for State of Oregon policies and rules referencing DEI, equity, diversity,
  or proxies/euphemisms (cultural competence, lived experience, etc.) that could
  be binding on the Housing Authority of Clackamas County.
- Source: oregon.gov, clackamas.us, and partner domains.
- Analysis: Keyword matching + risk scoring (0-3 scale).

HIGH-RISK DOCUMENTS (Score >= 2, {len(high_risk)} found)
- These documents contain both DEI/proxy language AND binding indicators
  ("policy", "shall", "required", "contract", etc.)
{self._format_doc_list(high_risk)}

MEDIUM-RISK DOCUMENTS (Score = 1, {len(medium_risk)} found)
- These contain DEI/proxy language but may lack explicit binding indicators.
- Review to assess applicability and intent.
{self._format_doc_list(medium_risk[:5]) if medium_risk else "  None"}

KEY APPLICABILITY AREAS IDENTIFIED
{self._summarize_applicability()}

NEXT STEPS
1. Review high-risk documents in detail; prioritize those tagged "hiring" or "procurement".
2. Check if Oregon policies explicitly apply to local housing authorities.
3. Collect evidence of current HA policies to compare against findings.
4. Assess risk and draft remediation plan.

For detailed analysis, see:
  - Full index: {self.output_dir}/document_index_{self.timestamp}.json
  - CSV summary: {self.output_dir}/summary_{self.timestamp}.csv
================================================================================
"""
        return summary.strip()
    
    def _format_doc_list(self, docs: List[Dict], limit: int = 10) -> str:
        """Format document list for display."""
        if not docs:
            return "  None"
        
        lines = []
        for doc in docs[:limit]:
            lines.append(f"  [{doc.get('risk_score')}] {doc.get('id')}")
            if doc.get('dei_keywords'):
                lines.append(f"      DEI: {', '.join(doc['dei_keywords'][:3])}")
            if doc.get('applicability_tags'):
                lines.append(f"      Areas: {', '.join(doc['applicability_tags'])}")
        return "\n".join(lines)
    
    def _summarize_applicability(self) -> str:
        """Summarize applicability areas found."""
        areas = {}
        for doc in self.index_data:
            for tag in doc.get('applicability_tags', []):
                areas[tag] = areas.get(tag, 0) + 1
        
        if not areas:
            return "  No specific applicability areas identified."
        
        lines = []
        for area, count in sorted(areas.items(), key=lambda x: x[1], reverse=True):
            lines.append(f"  - {area.capitalize()}: {count} document(s)")
        return "\n".join(lines)
    
    def save_summary(self) -> str:
        """Save one-page summary to file."""
        summary = self.generate_one_page_summary()
        summary_file = self.output_dir / f"FINDINGS_{self.timestamp}.txt"
        
        with open(summary_file, 'w') as f:
            f.write(summary)
        
        logger.info(f"Saved summary to {summary_file}")
        return str(summary_file)
    
    def generate_detailed_report(self) -> str:
        """Generate a detailed technical report."""
        report = f"""
================================================================================
DETAILED TECHNICAL REPORT — Oregon DEI References Audit
Generated: {self.timestamp}
================================================================================

METHODOLOGY
- Parsed {len(self.index_data)} documents from Oregon state and local government sources.
- Applied keyword matching for DEI terms (e.g., "diversity", "equity") and proxies
  (e.g., "cultural competence", "lived experience").
- Scored based on presence of binding indicators ("policy", "shall", "required").
- Tagged by applicability area: hiring, procurement, training, housing.

SCORING RUBRIC
- Score 0: No DEI/proxy language detected (compliant).
- Score 1: DEI/proxy present but weak binding indicators (possible issue).
- Score 2: DEI/proxy + multiple binding indicators (probable issue).
- Score 3: Explicit DEI policy with mandatory language (clear violation).

DOCUMENT BREAKDOWN
"""
        report += f"\nTotal Documents: {len(self.index_data)}\n"
        
        by_score = {}
        for doc in self.index_data:
            score = doc.get('risk_score', 0)
            if score not in by_score:
                by_score[score] = []
            by_score[score].append(doc)
        
        for score in sorted(by_score.keys(), reverse=True):
            docs = by_score[score]
            report += f"  Score {score}: {len(docs)} document(s)\n"
        
        report += f"""

APPLICABILITY BY AREA
"""
        areas = {}
        for doc in self.index_data:
            for tag in doc.get('applicability_tags', []):
                if tag not in areas:
                    areas[tag] = []
                areas[tag].append(doc['id'])
        
        for area in sorted(areas.keys()):
            report += f"  {area.capitalize()}: {len(areas[area])} document(s)\n"
        
        report += f"""

HIGH-RISK DOCUMENTS (DETAILED)
"""
        for doc in self._summarize_high_risk()[:20]:
            report += f"""
  [{doc['id']}]
    File: {doc['file_path']}
    Risk Score: {doc['risk_score']}
    DEI Keywords: {', '.join(doc.get('dei_keywords', []))}
    Proxy Keywords: {', '.join(doc.get('proxy_keywords', []))}
    Binding Indicators: {', '.join(doc.get('binding_keywords', []))}
    Applicability: {', '.join(doc.get('applicability_tags', []))}
    Text Length: {doc.get('text_length', 0)} chars
"""
        
        report += """
================================================================================
END OF REPORT
================================================================================
"""
        return report
    
    def save_detailed_report(self) -> str:
        """Save detailed report to file."""
        report = self.generate_detailed_report()
        report_file = self.output_dir / f"DETAILED_REPORT_{self.timestamp}.txt"
        
        with open(report_file, 'w') as f:
            f.write(report)
        
        logger.info(f"Saved detailed report to {report_file}")
        return str(report_file)

if __name__ == "__main__":
    gen = ReportGenerator()
    # Example: load index and generate reports
    # gen.load_index("research_results/document_index_20251230.json")
    # gen.save_summary()
    # gen.save_detailed_report()
    logger.info("Report generator ready.")
