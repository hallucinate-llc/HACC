#!/usr/bin/env python3
"""
Deep Analysis Script - Extract specific DEI provisions
Identifies exact statutory/regulatory requirements with context
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
RAW_DOCS_DIR = BASE_DIR / "raw_documents"
ANALYSIS_DIR = BASE_DIR / "analysis"
EXTRACT_DIR = ANALYSIS_DIR / "extracts"

DEI_TERMS = [
    r"\b(diversity|diverse)\b",
    r"\b(equity|equitable)\b", 
    r"\b(inclusion|inclusive)\b",
    r"\b(underrepresented minority|minorities)\b",
    r"\b(underserved communit(y|ies))\b",
    r"\b(disadvantaged business enterprise|DBE)\b",
    r"\b(minority[- ]owned business|MBE)\b",
    r"\b(wom[ae]n[- ]owned business|WBE)\b",
    r"\b(MWESB|ESB)\b",
    r"\b(affirmative action)\b",
    r"\b(protected class(es)?)\b",
    r"\b(disparate (impact|treatment))\b",
    r"\b(cultural competen(cy|ce))\b",
    r"\b(implicit bias|unconscious bias)\b",
    r"\b(racial equity)\b",
    r"\b(social equity)\b",
    r"\b(environmental justice)\b",
    r"\b(historically underrepresented)\b",
    r"\b(marginalized communit(y|ies))\b",
    r"\b(BIPOC)\b",
    r"\b(equal opportunity)\b",
    r"\b(fair housing)\b",
    r"\b(Section 3)\b",
    r"\b(community benefit(s)?)\b",
    r"\b(socially disadvantaged)\b",
    r"\b(economically disadvantaged)\b",
]

class ProvisionExtractor:
    def __init__(self):
        EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
        self.extracts = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def extract_ors_provisions(self, filepath, chapter):
        """Extract specific ORS provisions with context"""
        self.log(f"Extracting provisions from ORS Chapter {chapter}...")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            html = f.read()
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find all statute sections
        provisions = []
        
        # Look for sections and subsections
        text = soup.get_text()
        
        # Split by statute numbers (e.g., "456.055" or "279A.110")
        statute_pattern = re.compile(rf'{chapter}\.\d{{3}}\s+[A-Z]')
        
        lines = text.split('\n')
        current_statute = None
        current_text = []
        
        for line in lines:
            # Check if line starts a new statute section
            if re.search(rf'{chapter}\.\d{{3}}', line):
                # Save previous statute if it had DEI terms
                if current_statute and current_text:
                    full_text = '\n'.join(current_text)
                    if any(re.search(term, full_text, re.IGNORECASE) for term in DEI_TERMS):
                        provisions.append({
                            'statute': current_statute,
                            'chapter': chapter,
                            'text': full_text[:2000],  # Limit length
                            'found_terms': self._find_terms(full_text)
                        })
                
                current_statute = line.strip()[:20]  # Get statute number
                current_text = [line]
            else:
                if current_statute and len(current_text) < 100:  # Limit collection
                    current_text.append(line)
        
        # Check last statute
        if current_statute and current_text:
            full_text = '\n'.join(current_text)
            if any(re.search(term, full_text, re.IGNORECASE) for term in DEI_TERMS):
                provisions.append({
                    'statute': current_statute,
                    'chapter': chapter,
                    'text': full_text[:2000],
                    'found_terms': self._find_terms(full_text)
                })
        
        self.log(f"  Found {len(provisions)} relevant provisions")
        return provisions
    
    def _find_terms(self, text):
        """Find which DEI terms appear in text"""
        found = []
        for term_pattern in DEI_TERMS:
            matches = re.findall(term_pattern, text, re.IGNORECASE)
            if matches:
                found.append(re.sub(r'\\[^a-zA-Z]', '', term_pattern).replace('\\b', '').replace('(', '').replace(')?', '').split('|')[0])
        return list(set(found))[:10]  # Unique terms, limit 10
    
    def analyze_key_documents(self):
        """Analyze the most important documents"""
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
                
                for prov in provisions:
                    prov['source'] = description
                    all_provisions.append(prov)
        
        # Save extracts
        with open(EXTRACT_DIR / "statutory_provisions.json", 'w') as f:
            json.dump(all_provisions, f, indent=2)
        
        # Create readable report
        self.generate_provision_report(all_provisions)
        
        return all_provisions
    
    def generate_provision_report(self, provisions):
        """Generate human-readable report of provisions"""
        self.log("Generating provision report...")
        
        report = []
        report.append("=" * 100)
        report.append("SPECIFIC OREGON STATUTORY PROVISIONS RELATED TO DEI")
        report.append("Potentially Binding on Housing Authority of Clackamas County")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("=" * 100)
        report.append("")
        
        # Group by source
        by_source = {}
        for prov in provisions:
            source = prov['source']
            if source not in by_source:
                by_source[source] = []
            by_source[source].append(prov)
        
        for source, provs in by_source.items():
            report.append(f"\n{'=' * 100}")
            report.append(f"{source.upper()} - {len(provs)} Relevant Provision(s)")
            report.append("=" * 100)
            
            for i, prov in enumerate(provs, 1):
                report.append(f"\n[{i}] {prov['statute']}")
                report.append(f"    Terms Found: {', '.join(prov['found_terms'])}")
                report.append(f"    Text Preview:")
                
                # Clean and format text
                text_lines = prov['text'].split('\n')
                for line in text_lines[:15]:  # First 15 lines
                    line = line.strip()
                    if line:
                        report.append(f"      {line}")
                
                if len(text_lines) > 15:
                    report.append(f"      ... (text continues)")
                
                report.append("")
        
        report.append("=" * 100)
        report.append("CRITICAL ANALYSIS NOTES")
        report.append("=" * 100)
        report.append("")
        report.append("ORS Chapter 456 - Housing Authorities:")
        report.append("  • Establishes powers and duties of housing authorities in Oregon")
        report.append("  • May contain non-discrimination and equal opportunity requirements")
        report.append("")
        report.append("ORS Chapter 659A - Discrimination:")
        report.append("  • Oregon's primary anti-discrimination statute")
        report.append("  • Applies to employment, housing, and public accommodations")
        report.append("  • Enforced by Oregon Bureau of Labor and Industries (BOLI)")
        report.append("")
        report.append("ORS Chapter 279A/279C - Public Contracting:")
        report.append("  • Governs public agency contracting (including housing authorities)")
        report.append("  • May include MWESB (Minority/Women/Emerging Small Business) requirements")
        report.append("  • Disadvantaged Business Enterprise (DBE) provisions")
        report.append("")
        
        report_text = '\n'.join(report)
        
        with open(EXTRACT_DIR / "statutory_provisions_report.txt", 'w') as f:
            f.write(report_text)
        
        self.log("Provision report complete")
        
        return report_text
    
    def create_compliance_matrix(self):
        """Create a matrix of potential compliance requirements"""
        self.log("Creating compliance matrix...")
        
        # Load the DEI findings
        findings_path = ANALYSIS_DIR / "dei_findings.json"
        if not findings_path.exists():
            self.log("No findings file found")
            return
        
        with open(findings_path, 'r') as f:
            findings = json.load(f)
        
        matrix = []
        matrix.append("=" * 120)
        matrix.append("COMPLIANCE MATRIX - DEI REQUIREMENTS FOR HOUSING AUTHORITY OF CLACKAMAS COUNTY")
        matrix.append("=" * 120)
        matrix.append("")
        matrix.append(f"{'SOURCE':<40} | {'BINDING?':<10} | {'KEY TERMS':<40} | SCORE")
        matrix.append("-" * 120)
        
        for finding in findings[:20]:  # Top 20
            source = finding['source'][:39]
            
            # Determine if likely binding
            binding = "LIKELY" if any(x in source for x in ['ORS', 'OAR', 'Chapter']) else "REVIEW"
            if 'Federal' in source or 'HUD' in source:
                binding = "FEDERAL"
            
            # Get top terms
            terms = ', '.join([t['term'][:15] for t in finding['terms_found'][:3]])[:39]
            score = finding['relevance_score']
            
            matrix.append(f"{source:<40} | {binding:<10} | {terms:<40} | {score:>5}")
        
        matrix.append("")
        matrix.append("LEGEND:")
        matrix.append("  LIKELY  = Oregon statute (ORS) or administrative rule (OAR) - likely binding")
        matrix.append("  FEDERAL = Federal requirement - binding through HUD funding/oversight")
        matrix.append("  REVIEW  = Agency guidance or executive order - review for applicability")
        matrix.append("")
        
        matrix_text = '\n'.join(matrix)
        
        with open(EXTRACT_DIR / "compliance_matrix.txt", 'w') as f:
            f.write(matrix_text)
        
        print("\n" + matrix_text)
        
        return matrix_text

def main():
    print("\n" + "=" * 100)
    print("DEEP ANALYSIS - EXTRACTING SPECIFIC DEI PROVISIONS")
    print("=" * 100 + "\n")
    
    extractor = ProvisionExtractor()
    
    # Extract provisions from key statutes
    provisions = extractor.analyze_key_documents()
    
    # Create compliance matrix
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
