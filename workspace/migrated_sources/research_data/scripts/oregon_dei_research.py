#!/usr/bin/env python3
"""
Oregon DEI Research Script
Collects Oregon state documents related to DEI requirements that may bind
the Housing Authority of Clackamas County
"""

import asyncio
import json
import re
import os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import requests
from bs4 import BeautifulSoup
import time

# Research configuration
BASE_DIR = Path(__file__).parent.parent
RAW_DOCS_DIR = BASE_DIR / "raw_documents"
ANALYSIS_DIR = BASE_DIR / "analysis"

# DEI-related search terms and euphemisms
DEI_TERMS = [
    "diversity equity inclusion",
    "DEI",
    "underrepresented minority",
    "underserved communities",
    "disadvantaged business enterprise",
    "DBE",
    "minority-owned business",
    "women-owned business",
    "MWESB",
    "equity in contracting",
    "affirmative action",
    "protected classes",
    "disparate impact",
    "cultural competency",
    "implicit bias",
    "racial equity",
    "social equity",
    "environmental justice",
    "historically underrepresented",
    "marginalized communities",
    "BIPOC",
    "equal opportunity",
    "fair housing",
    "Section 3",
    "community benefits",
]

# Oregon government sources to search
OREGON_SOURCES = [
    {
        "name": "Oregon Revised Statutes - ORS Search",
        "url": "https://www.oregonlegislature.gov/bills_laws/pages/ors.aspx",
        "type": "statutes"
    },
    {
        "name": "Oregon Administrative Rules",
        "url": "https://secure.sos.state.or.us/oard/index.html",
        "type": "rules"
    },
    {
        "name": "Oregon Housing and Community Services",
        "url": "https://www.oregon.gov/ohcs",
        "type": "agency"
    },
    {
        "name": "Oregon Bureau of Labor and Industries",
        "url": "https://www.oregon.gov/boli",
        "type": "agency"
    },
    {
        "name": "Oregon Department of Administrative Services",
        "url": "https://www.oregon.gov/das",
        "type": "agency"
    },
    {
        "name": "Governor's Executive Orders",
        "url": "https://www.oregon.gov/gov/pages/executive-orders.aspx",
        "type": "executive"
    },
]

class OregonDEIResearcher:
    def __init__(self):
        self.results = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        })
        
    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")
        with open(ANALYSIS_DIR / "research_log.txt", "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    async def search_oregon_legislature_ors(self, page):
        """Search Oregon Revised Statutes"""
        self.log("Searching Oregon Revised Statutes...")
        
        try:
            # Navigate to ORS search
            await page.goto("https://www.oregonlegislature.gov/bills_laws/Pages/ORS.aspx", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # Look for relevant chapters that might contain DEI requirements
            relevant_chapters = [
                ("ORS 183", "Administrative Procedures Act"),
                ("ORS 279A", "Public Contracting - General Provisions"),
                ("ORS 279B", "Public Contracting - Procurement"),
                ("ORS 659", "Unlawful Discrimination in Employment, Public Accommodations and Real Property"),
                ("ORS 659A", "Discrimination"),
                ("ORS 456", "Housing Authorities"),
                ("ORS 90", "Residential Landlord and Tenant"),
            ]
            
            for chapter, description in relevant_chapters:
                self.log(f"  Checking {chapter}: {description}")
                
                # Try to find and download the chapter
                try:
                    search_input = await page.query_selector("input[type='text']")
                    if search_input:
                        await search_input.fill(chapter)
                        await page.keyboard.press("Enter")
                        await page.wait_for_load_state("networkidle")
                        await asyncio.sleep(2)
                        
                        # Get the page content
                        content = await page.content()
                        
                        # Save the raw HTML
                        filename = f"ORS_{chapter.replace(' ', '_')}.html"
                        with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        self.results.append({
                            "source": f"Oregon Revised Statutes - {chapter}",
                            "description": description,
                            "file": filename,
                            "url": page.url,
                            "date_collected": datetime.now().isoformat()
                        })
                        
                        # Go back for next search
                        await page.goto("https://www.oregonlegislature.gov/bills_laws/Pages/ORS.aspx", timeout=60000)
                        await page.wait_for_load_state("networkidle")
                        
                except Exception as e:
                    self.log(f"    Error searching {chapter}: {str(e)}")
                    
        except Exception as e:
            self.log(f"Error in ORS search: {str(e)}")
    
    async def search_oregon_admin_rules(self, page):
        """Search Oregon Administrative Rules"""
        self.log("Searching Oregon Administrative Rules...")
        
        try:
            await page.goto("https://secure.sos.state.or.us/oard/index.html", timeout=60000)
            await page.wait_for_load_state("networkidle")
            
            # Relevant OAR chapters for housing authorities and DEI
            relevant_oars = [
                ("137", "Public Contracting"),
                ("659", "Civil Rights Division"),
                ("813", "Housing and Community Services Department"),
            ]
            
            for oar_num, description in relevant_oars:
                self.log(f"  Checking OAR Chapter {oar_num}: {description}")
                
                try:
                    # Save the page content
                    content = await page.content()
                    filename = f"OAR_Chapter_{oar_num}_{description.replace(' ', '_')}.html"
                    
                    with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                        f.write(content)
                    
                    self.results.append({
                        "source": f"Oregon Administrative Rules - Chapter {oar_num}",
                        "description": description,
                        "file": filename,
                        "url": page.url,
                        "date_collected": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    self.log(f"    Error with OAR {oar_num}: {str(e)}")
                    
        except Exception as e:
            self.log(f"Error in OAR search: {str(e)}")
    
    async def search_ohcs(self, page):
        """Search Oregon Housing and Community Services"""
        self.log("Searching Oregon Housing and Community Services...")
        
        urls_to_check = [
            "https://www.oregon.gov/ohcs/pages/index.aspx",
            "https://www.oregon.gov/ohcs/housing-assistance/Pages/public-housing.aspx",
            "https://www.oregon.gov/ohcs/compliance-management/Pages/compliance.aspx",
        ]
        
        for url in urls_to_check:
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                content = await page.content()
                filename = f"OHCS_{url.split('/')[-1].replace('.aspx', '')}.html"
                
                with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.results.append({
                    "source": "Oregon Housing and Community Services",
                    "file": filename,
                    "url": url,
                    "date_collected": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.log(f"  Error accessing {url}: {str(e)}")
    
    async def search_boli(self, page):
        """Search Oregon Bureau of Labor and Industries"""
        self.log("Searching Oregon Bureau of Labor and Industries...")
        
        urls_to_check = [
            "https://www.oregon.gov/boli/pages/index.aspx",
            "https://www.oregon.gov/boli/civil-rights/Pages/default.aspx",
            "https://www.oregon.gov/boli/employers/Pages/default.aspx",
        ]
        
        for url in urls_to_check:
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                content = await page.content()
                filename = f"BOLI_{url.split('/')[-2]}_{url.split('/')[-1].replace('.aspx', '')}.html"
                
                with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.results.append({
                    "source": "Oregon Bureau of Labor and Industries",
                    "file": filename,
                    "url": url,
                    "date_collected": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.log(f"  Error accessing {url}: {str(e)}")
    
    async def search_executive_orders(self, page):
        """Search Governor's Executive Orders"""
        self.log("Searching Governor's Executive Orders...")
        
        try:
            await page.goto("https://www.oregon.gov/gov/pages/executive-orders.aspx", timeout=60000)
            await page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)
            
            content = await page.content()
            
            with open(RAW_DOCS_DIR / "Executive_Orders_Index.html", "w", encoding="utf-8") as f:
                f.write(content)
            
            # Parse to find individual executive orders
            soup = BeautifulSoup(content, 'html.parser')
            links = soup.find_all('a', href=True)
            
            eo_count = 0
            for link in links:
                href = link.get('href', '')
                if 'executive-order' in href.lower() or 'eo-' in href.lower():
                    try:
                        if not href.startswith('http'):
                            href = f"https://www.oregon.gov{href}"
                        
                        await page.goto(href, timeout=60000)
                        await page.wait_for_load_state("networkidle")
                        
                        eo_content = await page.content()
                        eo_filename = f"Executive_Order_{eo_count}.html"
                        
                        with open(RAW_DOCS_DIR / eo_filename, "w", encoding="utf-8") as f:
                            f.write(eo_content)
                        
                        self.results.append({
                            "source": "Governor's Executive Order",
                            "file": eo_filename,
                            "url": href,
                            "date_collected": datetime.now().isoformat()
                        })
                        
                        eo_count += 1
                        if eo_count >= 20:  # Limit to recent orders
                            break
                            
                    except Exception as e:
                        self.log(f"  Error accessing executive order {href}: {str(e)}")
            
            self.log(f"  Collected {eo_count} executive orders")
            
        except Exception as e:
            self.log(f"Error in executive orders search: {str(e)}")
    
    async def search_das_procurement(self, page):
        """Search Oregon DAS for procurement policies"""
        self.log("Searching Oregon Department of Administrative Services...")
        
        urls_to_check = [
            "https://www.oregon.gov/das/pages/index.aspx",
            "https://www.oregon.gov/das/procurement/pages/index.aspx",
        ]
        
        for url in urls_to_check:
            try:
                await page.goto(url, timeout=60000)
                await page.wait_for_load_state("networkidle")
                await asyncio.sleep(2)
                
                content = await page.content()
                filename = f"DAS_{url.split('/')[-2]}.html"
                
                with open(RAW_DOCS_DIR / filename, "w", encoding="utf-8") as f:
                    f.write(content)
                
                self.results.append({
                    "source": "Oregon Department of Administrative Services",
                    "file": filename,
                    "url": url,
                    "date_collected": datetime.now().isoformat()
                })
                
            except Exception as e:
                self.log(f"  Error accessing {url}: {str(e)}")
    
    async def run_playwright_research(self):
        """Main research function using Playwright"""
        self.log("Starting Playwright-based research...")
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            try:
                # Run all searches
                await self.search_oregon_legislature_ors(page)
                await self.search_oregon_admin_rules(page)
                await self.search_ohcs(page)
                await self.search_boli(page)
                await self.search_executive_orders(page)
                await self.search_das_procurement(page)
                
            finally:
                await browser.close()
        
        self.log(f"Playwright research complete. Collected {len(self.results)} documents.")
    
    def analyze_documents(self):
        """Analyze collected documents for DEI terms"""
        self.log("Starting document analysis...")
        
        findings = []
        
        for doc_info in self.results:
            file_path = RAW_DOCS_DIR / doc_info["file"]
            
            if not file_path.exists():
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Parse HTML
                soup = BeautifulSoup(content, 'html.parser')
                text = soup.get_text()
                
                # Search for DEI terms
                found_terms = []
                for term in DEI_TERMS:
                    pattern = re.compile(re.escape(term), re.IGNORECASE)
                    matches = pattern.findall(text)
                    if matches:
                        found_terms.append({
                            "term": term,
                            "count": len(matches)
                        })
                
                if found_terms:
                    findings.append({
                        "document": doc_info["file"],
                        "source": doc_info["source"],
                        "url": doc_info.get("url", ""),
                        "terms_found": found_terms,
                        "relevance_score": len(found_terms)
                    })
                    
                    self.log(f"  Found {len(found_terms)} DEI-related terms in {doc_info['file']}")
                    
            except Exception as e:
                self.log(f"  Error analyzing {doc_info['file']}: {str(e)}")
        
        # Sort findings by relevance
        findings.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        # Save findings
        with open(ANALYSIS_DIR / "dei_findings.json", "w") as f:
            json.dump(findings, f, indent=2)
        
        self.log(f"Analysis complete. Found DEI terms in {len(findings)} documents.")
        
        return findings
    
    def generate_report(self, findings):
        """Generate a human-readable report"""
        self.log("Generating report...")
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("OREGON DEI REQUIREMENTS RESEARCH REPORT")
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("=" * 80)
        report_lines.append("")
        report_lines.append("EXECUTIVE SUMMARY")
        report_lines.append("-" * 80)
        report_lines.append(f"Total documents collected: {len(self.results)}")
        report_lines.append(f"Documents containing DEI terms: {len(findings)}")
        report_lines.append("")
        report_lines.append("SEARCH TERMS USED:")
        for term in DEI_TERMS:
            report_lines.append(f"  - {term}")
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("FINDINGS BY DOCUMENT")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        for i, finding in enumerate(findings, 1):
            report_lines.append(f"{i}. {finding['source']}")
            report_lines.append(f"   Document: {finding['document']}")
            report_lines.append(f"   URL: {finding['url']}")
            report_lines.append(f"   Relevance Score: {finding['relevance_score']}")
            report_lines.append("   Terms Found:")
            for term_info in finding['terms_found']:
                report_lines.append(f"     - {term_info['term']}: {term_info['count']} occurrences")
            report_lines.append("")
        
        report_lines.append("=" * 80)
        report_lines.append("RECOMMENDED NEXT STEPS")
        report_lines.append("=" * 80)
        report_lines.append("1. Review high-relevance documents in detail")
        report_lines.append("2. Extract specific statutory/regulatory requirements")
        report_lines.append("3. Determine which requirements are binding on housing authorities")
        report_lines.append("4. Consult with legal counsel on applicability")
        report_lines.append("")
        
        report_text = "\n".join(report_lines)
        
        with open(ANALYSIS_DIR / "research_report.txt", "w") as f:
            f.write(report_text)
        
        self.log("Report generated: research_report.txt")
        
        return report_text

async def main():
    """Main entry point"""
    print("=" * 80)
    print("OREGON DEI RESEARCH - Housing Authority of Clackamas County")
    print("=" * 80)
    print()
    
    # Ensure directories exist
    RAW_DOCS_DIR.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Initialize researcher
    researcher = OregonDEIResearcher()
    
    # Run research
    await researcher.run_playwright_research()
    
    # Analyze documents
    findings = researcher.analyze_documents()
    
    # Generate report
    report = researcher.generate_report(findings)
    
    print("\n" + "=" * 80)
    print("RESEARCH COMPLETE")
    print("=" * 80)
    print(f"\nDocuments saved to: {RAW_DOCS_DIR}")
    print(f"Analysis saved to: {ANALYSIS_DIR}")
    print(f"\nGenerated files:")
    print(f"  - research_report.txt (main findings)")
    print(f"  - dei_findings.json (detailed analysis)")
    print(f"  - research_log.txt (activity log)")
    print()

if __name__ == "__main__":
    asyncio.run(main())
