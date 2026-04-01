#!/usr/bin/env python3
"""
Enhanced Oregon DEI Research Script
Properly downloads full statute text, administrative rules, and PDFs
"""

import asyncio
import json
import re
import os
import subprocess
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import time

BASE_DIR = Path(__file__).parent.parent
RAW_DOCS_DIR = BASE_DIR / "raw_documents"
ANALYSIS_DIR = BASE_DIR / "analysis"
PDF_DIR = RAW_DOCS_DIR / "pdfs"

DEI_TERMS = [
    "diversity", "equity", "inclusion", "DEI",
    "underrepresented minority", "underserved communities",
    "disadvantaged business enterprise", "DBE",
    "minority-owned business", "minority owned business",
    "women-owned business", "woman-owned business",
    "MWESB", "MBE", "WBE", "ESB",
    "equity in contracting", "affirmative action",
    "protected class", "disparate impact",
    "cultural competency", "cultural competence",
    "implicit bias", "unconscious bias",
    "racial equity", "social equity",
    "environmental justice",
    "historically underrepresented",
    "marginalized communities", "BIPOC",
    "equal opportunity", "fair housing",
    "Section 3", "community benefit",
    "socially disadvantaged", "economically disadvantaged",
    "certified minority", "certified disadvantaged",
]

class EnhancedOregonResearcher:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        PDF_DIR.mkdir(parents=True, exist_ok=True)
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        with open(ANALYSIS_DIR / "research_log.txt", "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    async def download_ors_chapters(self):
        """Download Oregon Revised Statutes directly via HTTP"""
        self.log("Downloading Oregon Revised Statutes...")
        
        chapters = {
            "183": "Administrative Procedures Act",
            "279A": "Public Contracting - General",
            "279B": "Public Contracting - Procurement", 
            "279C": "Public Contracting - Construction",
            "659": "Unlawful Discrimination",
            "659A": "Discrimination Definitions and Procedures",
            "456": "Housing Authorities",
            "90": "Residential Landlord-Tenant",
        }
        
        for chapter, description in chapters.items():
            self.log(f"  Downloading ORS Chapter {chapter}: {description}")
            try:
                url = f"https://www.oregonlegislature.gov/bills_laws/ors/ors{chapter}.html"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    filename = f"ORS_Chapter_{chapter}_{description.replace(' ', '_').replace('-', '_')}.html"
                    filepath = RAW_DOCS_DIR / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    self.results.append({
                        "source": f"Oregon Revised Statutes - Chapter {chapter}",
                        "description": description,
                        "file": filename,
                        "url": url,
                        "date_collected": datetime.now().isoformat()
                    })
                    self.log(f"    ✓ Downloaded {len(response.text)} bytes")
                else:
                    self.log(f"    ✗ HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"    ✗ Error: {str(e)}")
            
            await asyncio.sleep(1)
    
    async def download_oar_chapters(self):
        """Download Oregon Administrative Rules"""
        self.log("Downloading Oregon Administrative Rules...")
        
        # Key OAR chapters for housing authorities
        chapters = {
            "137": "Public Contracting Rules",
            "659": "Civil Rights Division",
            "813": "Housing and Community Services",
        }
        
        for chapter, description in chapters.items():
            self.log(f"  Downloading OAR Chapter {chapter}: {description}")
            try:
                # Try direct OAR URL
                url = f"https://secure.sos.state.or.us/oard/displayDivisionRules.action?selectedDivision={chapter}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    filename = f"OAR_Chapter_{chapter}_{description.replace(' ', '_')}.html"
                    filepath = RAW_DOCS_DIR / filename
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    self.results.append({
                        "source": f"Oregon Administrative Rules - Chapter {chapter}",
                        "description": description,
                        "file": filename,
                        "url": url,
                        "date_collected": datetime.now().isoformat()
                    })
                    self.log(f"    ✓ Downloaded {len(response.text)} bytes")
                else:
                    self.log(f"    ✗ HTTP {response.status_code}")
                    
            except Exception as e:
                self.log(f"    ✗ Error: {str(e)}")
            
            await asyncio.sleep(1)
    
    async def download_executive_orders_pdfs(self, page):
        """Download executive order PDFs using curl"""
        self.log("Downloading Executive Orders...")
        
        try:
            await page.goto("https://www.oregon.gov/gov/pages/executive-orders.aspx", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            # Find all PDF links
            pdf_links = []
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if href.endswith('.pdf') and ('eo-' in href.lower() or 'executive' in href.lower()):
                    if not href.startswith('http'):
                        href = f"https://www.oregon.gov{href}"
                    pdf_links.append(href)
            
            self.log(f"  Found {len(pdf_links)} executive order PDFs")
            
            # Download PDFs (limit to recent ones)
            for i, pdf_url in enumerate(pdf_links[:30]):
                try:
                    pdf_name = pdf_url.split('/')[-1]
                    pdf_path = PDF_DIR / pdf_name
                    
                    self.log(f"    Downloading {pdf_name}...")
                    
                    # Use curl to download
                    result = subprocess.run(
                        ['curl', '-s', '-L', '-o', str(pdf_path), pdf_url],
                        capture_output=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0 and pdf_path.exists():
                        # Extract text from PDF using pdftotext if available
                        try:
                            text_result = subprocess.run(
                                ['pdftotext', str(pdf_path), '-'],
                                capture_output=True,
                                text=True,
                                timeout=10
                            )
                            
                            if text_result.returncode == 0:
                                text_path = RAW_DOCS_DIR / f"{pdf_name}.txt"
                                with open(text_path, 'w') as f:
                                    f.write(text_result.stdout)
                                
                                self.results.append({
                                    "source": "Governor's Executive Order",
                                    "file": f"{pdf_name}.txt",
                                    "pdf_file": pdf_name,
                                    "url": pdf_url,
                                    "date_collected": datetime.now().isoformat()
                                })
                                self.log(f"      ✓ Extracted text")
                            else:
                                # Keep PDF reference even if text extraction fails
                                self.results.append({
                                    "source": "Governor's Executive Order (PDF only)",
                                    "file": pdf_name,
                                    "url": pdf_url,
                                    "date_collected": datetime.now().isoformat()
                                })
                                
                        except FileNotFoundError:
                            self.log(f"      ⚠ pdftotext not available, keeping PDF")
                            self.results.append({
                                "source": "Governor's Executive Order (PDF only)",
                                "file": pdf_name,
                                "url": pdf_url,
                                "date_collected": datetime.now().isoformat()
                            })
                    else:
                        self.log(f"      ✗ Download failed")
                        
                except Exception as e:
                    self.log(f"      ✗ Error: {str(e)}")
                
                await asyncio.sleep(0.5)
                
        except Exception as e:
            self.log(f"Error downloading executive orders: {str(e)}")
    
    async def search_oregon_agencies(self, page):
        """Search key Oregon agency websites"""
        self.log("Searching Oregon agency websites...")
        
        agencies = [
            ("https://www.oregon.gov/ohcs/pages/index.aspx", "OHCS_Homepage"),
            ("https://www.oregon.gov/ohcs/housing-assistance/Pages/public-housing.aspx", "OHCS_Public_Housing"),
            ("https://www.oregon.gov/ohcs/compliance-management/Pages/compliance.aspx", "OHCS_Compliance"),
            ("https://www.oregon.gov/boli/pages/index.aspx", "BOLI_Homepage"),
            ("https://www.oregon.gov/boli/civil-rights/Pages/default.aspx", "BOLI_Civil_Rights"),
            ("https://www.oregon.gov/boli/employers/Pages/employment-discrimination.aspx", "BOLI_Employment_Discrimination"),
            ("https://www.oregon.gov/das/procurement/pages/index.aspx", "DAS_Procurement"),
        ]
        
        for url, name in agencies:
            self.log(f"  Accessing {name}...")
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                content = await page.content()
                filename = f"{name}.html"
                
                with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.results.append({
                    "source": name.replace('_', ' '),
                    "file": filename,
                    "url": url,
                    "date_collected": datetime.now().isoformat()
                })
                self.log(f"    ✓ Downloaded")
                
            except Exception as e:
                self.log(f"    ✗ Error: {str(e)}")
    
    async def search_federal_hud_requirements(self):
        """Search for federal HUD requirements that Oregon housing authorities must follow"""
        self.log("Downloading federal HUD requirements...")
        
        hud_urls = [
            ("https://www.hud.gov/program_offices/fair_housing_equal_opp/fair_housing_act_overview", "HUD_Fair_Housing_Act"),
            ("https://www.hud.gov/section3", "HUD_Section3"),
        ]
        
        for url, name in hud_urls:
            self.log(f"  Downloading {name}...")
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    filename = f"{name}.html"
                    with open(RAW_DOCS_DIR / filename, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    
                    self.results.append({
                        "source": name.replace('_', ' '),
                        "file": filename,
                        "url": url,
                        "date_collected": datetime.now().isoformat()
                    })
                    self.log(f"    ✓ Downloaded")
                else:
                    self.log(f"    ✗ HTTP {response.status_code}")
            except Exception as e:
                self.log(f"    ✗ Error: {str(e)}")
            
            await asyncio.sleep(1)
    
    async def run_enhanced_research(self):
        """Main research workflow"""
        self.log("Starting enhanced research...")
        
        # Download statutes directly via HTTP
        await self.download_ors_chapters()
        await self.download_oar_chapters()
        
        # Use Playwright for dynamic content
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                await self.download_executive_orders_pdfs(page)
                await self.search_oregon_agencies(page)
            finally:
                await browser.close()
        
        # Download federal requirements
        await self.search_federal_hud_requirements()
        
        self.log(f"Research complete. Collected {len(self.results)} documents.")
    
    def analyze_documents(self):
        """Analyze collected documents for DEI terms"""
        self.log("Starting document analysis...")
        
        findings = []
        
        for doc_info in self.results:
            file_path = RAW_DOCS_DIR / doc_info["file"]
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors='ignore') as f:
                    content = f.read()
                
                # Parse HTML if applicable
                if file_path.suffix == '.html':
                    soup = BeautifulSoup(content, 'html.parser')
                    text = soup.get_text()
                else:
                    text = content
                
                # Search for DEI terms (case-insensitive)
                found_terms = {}
                text_lower = text.lower()
                
                for term in DEI_TERMS:
                    count = text_lower.count(term.lower())
                    if count > 0:
                        if term not in found_terms:
                            found_terms[term] = count
                
                if found_terms:
                    findings.append({
                        "document": doc_info["file"],
                        "source": doc_info["source"],
                        "url": doc_info.get("url", ""),
                        "terms_found": [{"term": k, "count": v} for k, v in found_terms.items()],
                        "relevance_score": sum(found_terms.values()),
                        "unique_terms": len(found_terms)
                    })
                    
                    self.log(f"  ✓ Found {len(found_terms)} unique DEI terms in {doc_info['file']} ({sum(found_terms.values())} total occurrences)")
                    
            except Exception as e:
                self.log(f"  ✗ Error analyzing {doc_info['file']}: {str(e)}")
        
        # Sort by relevance
        findings.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Save findings
        with open(ANALYSIS_DIR / "dei_findings.json", "w") as f:
            json.dump(findings, f, indent=2)
        
        self.log(f"Analysis complete. Found DEI terms in {len(findings)} documents.")
        
        return findings
    
    def generate_detailed_report(self, findings):
        """Generate comprehensive report"""
        self.log("Generating detailed report...")
        
        report_lines = []
        report_lines.append("=" * 100)
        report_lines.append("OREGON DEI REQUIREMENTS RESEARCH REPORT")
        report_lines.append("Housing Authority of Clackamas County")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 100)
        report_lines.append("")
        
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 100)
        report_lines.append(f"Total documents collected: {len(self.results)}")
        report_lines.append(f"Documents containing DEI-related terms: {len(findings)}")
        
        if findings:
            total_occurrences = sum(f["relevance_score"] for f in findings)
            total_unique_terms = sum(f["unique_terms"] for f in findings)
            report_lines.append(f"Total DEI term occurrences: {total_occurrences}")
            report_lines.append(f"Average occurrences per document: {total_occurrences / len(findings):.1f}")
        
        report_lines.append("")
        report_lines.append("SEARCH TERMS MONITORED:")
        for i, term in enumerate(DEI_TERMS, 1):
            report_lines.append(f"  {i:2d}. {term}")
        
        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append("DETAILED FINDINGS BY RELEVANCE")
        report_lines.append("=" * 100)
        report_lines.append("")
        
        if not findings:
            report_lines.append("No DEI terms found in collected documents.")
            report_lines.append("")
        else:
            for i, finding in enumerate(findings, 1):
                report_lines.append(f"[{i}] {finding['source']}")
                report_lines.append(f"    File: {finding['document']}")
                report_lines.append(f"    URL: {finding['url']}")
                report_lines.append(f"    Relevance Score: {finding['relevance_score']} (Unique Terms: {finding['unique_terms']})")
                report_lines.append(f"    Terms Found:")
                
                # Sort terms by count
                sorted_terms = sorted(finding['terms_found'], key=lambda x: x['count'], reverse=True)
                for term_info in sorted_terms[:20]:  # Top 20 terms
                    report_lines.append(f"      • {term_info['term']}: {term_info['count']} occurrence(s)")
                
                if len(sorted_terms) > 20:
                    report_lines.append(f"      ... and {len(sorted_terms) - 20} more terms")
                
                report_lines.append("")
        
        report_lines.append("=" * 100)
        report_lines.append("DOCUMENT CATEGORIES")
        report_lines.append("=" * 100)
        
        # Categorize findings
        categories = {
            "Statutes (ORS)": [],
            "Administrative Rules (OAR)": [],
            "Executive Orders": [],
            "State Agencies": [],
            "Federal Requirements": []
        }
        
        for finding in findings:
            source = finding['source']
            if 'ORS' in source or 'Statute' in source:
                categories["Statutes (ORS)"].append(finding)
            elif 'OAR' in source or 'Administrative Rule' in source:
                categories["Administrative Rules (OAR)"].append(finding)
            elif 'Executive Order' in source:
                categories["Executive Orders"].append(finding)
            elif 'HUD' in source or 'Federal' in source:
                categories["Federal Requirements"].append(finding)
            else:
                categories["State Agencies"].append(finding)
        
        for category, items in categories.items():
            report_lines.append(f"\n{category}: {len(items)} document(s)")
            for item in items:
                report_lines.append(f"  - {item['document']} (Score: {item['relevance_score']})")
        
        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append("RECOMMENDATIONS")
        report_lines.append("=" * 100)
        report_lines.append("")
        report_lines.append("1. PRIORITY REVIEW: Focus on high-scoring statutes (ORS) and administrative rules (OAR)")
        report_lines.append("2. LEGAL ANALYSIS: Consult with legal counsel on binding requirements")
        report_lines.append("3. POLICY AUDIT: Review current HACC policies against identified requirements")
        report_lines.append("4. COMPLIANCE GAP: Identify areas where requirements may not be met")
        report_lines.append("5. DOCUMENTATION: Maintain records showing compliance efforts")
        report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        with open(ANALYSIS_DIR / "comprehensive_report.txt", "w") as f:
            f.write(report_text)
        
        # Also save a CSV for easy analysis
        try:
            import csv
            with open(ANALYSIS_DIR / "findings_summary.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Source", "Document", "URL", "Relevance Score", "Unique Terms", "Top Terms"])
                
                for i, finding in enumerate(findings, 1):
                    top_terms = ", ".join([f"{t['term']}({t['count']})" for t in sorted(finding['terms_found'], key=lambda x: x['count'], reverse=True)[:5]])
                    writer.writerow([
                        i,
                        finding['source'],
                        finding['document'],
                        finding['url'],
                        finding['relevance_score'],
                        finding['unique_terms'],
                        top_terms
                    ])
        except Exception as e:
            self.log(f"Could not create CSV: {str(e)}")
        
        self.log("Report generation complete")
        
        return report_text

async def main():
    print("\n" + "=" * 100)
    print("ENHANCED OREGON DEI RESEARCH")
    print("Housing Authority of Clackamas County")
    print("=" * 100 + "\n")
    
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    researcher = EnhancedOregonResearcher()
    
    await researcher.run_enhanced_research()
    findings = researcher.analyze_documents()
    report = researcher.generate_detailed_report(findings)
    
    print("\n" + "=" * 100)
    print("RESEARCH COMPLETE")
    print("=" * 100)
    print(f"\nResults:")
    print(f"  • Documents collected: {len(researcher.results)}")
    print(f"  • Documents with DEI terms: {len(findings)}")
    
    if findings:
        print(f"  • Total DEI occurrences: {sum(f['relevance_score'] for f in findings)}")
        print(f"\nTop 5 Most Relevant Documents:")
        for i, finding in enumerate(findings[:5], 1):
            print(f"    {i}. {finding['source']} (Score: {finding['relevance_score']})")
    
    print(f"\nOutput files:")
    print(f"  • {ANALYSIS_DIR}/comprehensive_report.txt")
    print(f"  • {ANALYSIS_DIR}/dei_findings.json")
    print(f"  • {ANALYSIS_DIR}/findings_summary.csv")
    print(f"  • {ANALYSIS_DIR}/research_log.txt")
    print()

if __name__ == "__main__":
    asyncio.run(main())
