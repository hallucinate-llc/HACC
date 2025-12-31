#!/usr/bin/env python3
"""
Enhanced DEI research script with deeper crawling, PDF extraction, and document analysis
"""

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
import time
import hashlib

# Expanded DEI keywords based on DOJ guidance
DEI_KEYWORDS = [
    # Direct DEI terms
    'diversity', 'equity', 'inclusion', 'DEI', 'DEIB', 'belonging',
    'diverse', 'equitable', 'inclusive',
    
    # Justice frameworks
    'social justice', 'racial justice', 'environmental justice', 'economic justice',
    'housing justice', 'climate justice', 'health equity',
    
    # Disparity language
    'disparate impact', 'disparity', 'disparities', 'gap', 'gaps',
    'underrepresented', 'underserved', 'marginalized', 'vulnerable populations',
    'historically excluded', 'historically marginalized', 'historically underserved',
    'underinvested communities', 'disinvested communities',
    
    # Protected classes and identity
    'protected class', 'protected classes', 'protected characteristic',
    'BIPOC', 'people of color', 'communities of color', 'Black', 'Indigenous',
    'LGBTQ', 'LGBTQIA', 'LGBTQIA+', 'gender identity', 'sexual orientation',
    'transgender', 'non-binary', 'disability', 'disabled',
    
    # Bias and discrimination frameworks
    'implicit bias', 'unconscious bias', 'anti-bias', 'bias training',
    'anti-racism', 'antiracism', 'racial equity', 'race equity',
    'systemic racism', 'structural racism', 'institutional racism',
    'white privilege', 'privilege', 'oppression', 'power and privilege',
    
    # Affirmative/preferential treatment
    'affirmative action', 'equal opportunity', 'preferential treatment',
    'quotas', 'set-aside', 'proportional representation',
    
    # Cultural competency
    'cultural competency', 'cultural competence', 'culturally responsive',
    'culturally sensitive', 'cultural humility', 'cultural awareness',
    
    # Intersectionality
    'intersectionality', 'intersectional', 'multiple identities',
    
    # Microaggressions and safe spaces
    'microaggression', 'microaggressions', 'safe space', 'brave space',
    'trigger warning', 'content warning',
    
    # Justice approaches
    'restorative justice', 'transformative justice', 'reparations',
    'truth and reconciliation',
    
    # Engagement euphemisms
    'community engagement', 'stakeholder engagement', 'authentic engagement',
    'lived experience', 'lived experiences', 'centering voices', 'elevating voices',
    'community voices', 'marginalized voices',
    
    # Accessibility
    'accessibility', 'accessible', 'universal design', 'accommodation',
    
    # Fair housing related
    'fair housing', 'housing discrimination', 'redlining', 'gentrification',
    'displacement', 'housing affordability crisis',
    
    # Wealth and opportunity
    'wealth gap', 'wealth inequality', 'opportunity gap', 'achievement gap',
    'economic mobility', 'intergenerational wealth',
    
    # Power and systems
    'power dynamics', 'power imbalance', 'systems of oppression',
    'structural barriers', 'systemic barriers',
    
    # Allyship
    'allyship', 'ally', 'co-conspirator', 'accomplice',
    
    # Decolonization
    'decolonize', 'decolonization', 'decolonizing',
    
    # Specific programs/initiatives
    'equity framework', 'equity plan', 'equity toolkit', 'equity lens',
    'racial equity toolkit', 'racial equity lens',
    'diversity committee', 'equity committee', 'inclusion committee',
    'diversity training', 'equity training', 'inclusion training',
    'diversity officer', 'equity officer', 'inclusion officer',
    'chief diversity officer', 'CDO',
]

class EnhancedHAACCResearcher:
    def __init__(self):
        self.base_urls = [
            "https://www.clackamas.us/housingauthority",
            "https://www.clackamas.us",  # Main county site
        ]
        self.results_dir = Path("research_results")
        self.results_dir.mkdir(exist_ok=True)
        self.documents_dir = self.results_dir / "documents"
        self.documents_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.collected_urls = set()
        self.collected_documents = set()
        self.findings = []
        self.max_urls = 500  # Increased crawl depth
        
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.results_dir / "research.log", "a") as f:
            f.write(log_msg + "\n")
    
    def search_duckduckgo_html(self, query):
        """Enhanced DuckDuckGo search"""
        try:
            self.log(f"Searching DuckDuckGo: {query}")
            results = []
            
            # Try multiple pages
            for page in range(3):
                url = "https://html.duckduckgo.com/html/"
                params = {'q': query}
                if page > 0:
                    params['s'] = page * 30
                
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                }
                
                response = requests.post(url, data=params, headers=headers, timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')
                
                for result in soup.find_all('div', class_='result'):
                    title_elem = result.find('a', class_='result__a')
                    snippet_elem = result.find('a', class_='result__snippet')
                    
                    if title_elem:
                        url_found = title_elem.get('href', '')
                        if url_found:
                            results.append({
                                'title': title_elem.get_text(strip=True),
                                'url': url_found,
                                'description': snippet_elem.get_text(strip=True) if snippet_elem else '',
                                'source': 'duckduckgo',
                                'query': query
                            })
                
                time.sleep(3)  # Rate limiting
            
            self.log(f"Found {len(results)} results")
            return results
        except Exception as e:
            self.log(f"DuckDuckGo search error: {e}")
            return []
    
    def download_pdf(self, url):
        """Download and extract text from PDF"""
        try:
            self.log(f"Downloading PDF: {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            # Save PDF
            url_hash = hashlib.md5(url.encode()).hexdigest()
            pdf_path = self.documents_dir / f"doc_{url_hash}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            self.collected_documents.add(url)
            
            # Try to extract text using pdfplumber if available
            try:
                import pdfplumber
                text = ""
                with pdfplumber.open(pdf_path) as pdf:
                    for page in pdf.pages:
                        text += page.extract_text() or ""
                return text
            except ImportError:
                self.log("pdfplumber not available, will install")
                os.system("pip install -q pdfplumber")
                return self.download_pdf(url)  # Retry
                
        except Exception as e:
            self.log(f"Error downloading PDF {url}: {e}")
            return None
    
    def download_document(self, url):
        """Download various document types"""
        try:
            ext = Path(urlparse(url).path).suffix.lower()
            
            if ext == '.pdf':
                return self.download_pdf(url)
            elif ext in ['.doc', '.docx', '.txt', '.rtf']:
                self.log(f"Downloading document: {url}")
                response = requests.get(url, timeout=60)
                response.raise_for_status()
                
                url_hash = hashlib.md5(url.encode()).hexdigest()
                doc_path = self.documents_dir / f"doc_{url_hash}{ext}"
                with open(doc_path, 'wb') as f:
                    f.write(response.content)
                
                self.collected_documents.add(url)
                
                # For .docx, try to extract text
                if ext == '.docx':
                    try:
                        import docx
                        doc = docx.Document(doc_path)
                        return '\n'.join([para.text for para in doc.paragraphs])
                    except ImportError:
                        os.system("pip install -q python-docx")
                        return self.download_document(url)
                
                return response.text
                
        except Exception as e:
            self.log(f"Error downloading document {url}: {e}")
            return None
    
    async def scrape_page_enhanced(self, url, browser):
        """Enhanced page scraping with JavaScript execution"""
        try:
            self.log(f"Scraping: {url}")
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            # Go to page
            response = await page.goto(url, wait_until='networkidle', timeout=45000)
            
            # Check if it's a document
            content_type = response.headers.get('content-type', '')
            if 'pdf' in content_type or 'document' in content_type:
                await context.close()
                text = self.download_document(url)
                if text:
                    self.analyze_content(url, text, text)
                return None
            
            # Get content
            content = await page.content()
            text = await page.evaluate('document.body.innerText')
            
            # Save HTML
            url_hash = hashlib.md5(url.encode()).hexdigest()
            with open(self.results_dir / f"page_{url_hash}.html", "w", encoding='utf-8') as f:
                f.write(content)
            
            # Find documents
            links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                return links.map(a => ({
                    href: a.href,
                    text: a.textContent.trim()
                }));
            }''')
            
            await context.close()
            
            # Analyze content
            matches = self.analyze_content(url, text, content)
            if matches:
                self.findings.extend(matches)
            
            return {'content': content, 'text': text, 'links': links}
            
        except Exception as e:
            self.log(f"Error scraping {url}: {e}")
            return None
    
    def analyze_content(self, url, text, html):
        """Enhanced content analysis"""
        matches = []
        text_lower = text.lower()
        
        for keyword in DEI_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            found = list(re.finditer(pattern, text_lower))
            
            if found:
                contexts = []
                for match in found[:10]:  # Up to 10 examples
                    start = max(0, match.start() - 200)
                    end = min(len(text), match.end() + 200)
                    context = text[start:end].strip()
                    contexts.append(context)
                
                matches.append({
                    'url': url,
                    'keyword': keyword,
                    'count': len(found),
                    'contexts': contexts,
                    'timestamp': datetime.now().isoformat()
                })
        
        return matches
    
    def discover_urls(self, page_data, base_url):
        """Extract and filter URLs"""
        if not page_data or 'links' not in page_data:
            return set()
        
        urls = set()
        for link in page_data['links']:
            href = link['href']
            
            # Skip javascript, mailto, tel, etc.
            if any(href.startswith(x) for x in ['javascript:', 'mailto:', 'tel:', '#']):
                continue
            
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)
            
            # Only clackamas.us domain
            if 'clackamas.us' in parsed.netloc and full_url not in self.collected_urls:
                urls.add(full_url)
            
            # Collect documents
            if any(full_url.endswith(ext) for ext in ['.pdf', '.doc', '.docx']):
                if full_url not in self.collected_documents:
                    urls.add(full_url)
        
        return urls
    
    async def crawl_site_deep(self):
        """Deep site crawl"""
        self.log("Starting deep site crawl...")
        
        # Seed URLs - housing authority and related pages
        seed_urls = [
            "https://www.clackamas.us/housingauthority",
            "https://www.clackamas.us/housingauthority/about",
            "https://www.clackamas.us/housingauthority/programs",
            "https://www.clackamas.us/housingauthority/resources",
            "https://www.clackamas.us/housingauthority/contact",
            "https://www.clackamas.us/housingauthority/news",
            "https://www.clackamas.us/housingauthority/documents",
            "https://www.clackamas.us/",
            "https://www.clackamas.us/communitydevelopment",
            "https://www.clackamas.us/socialservices",
            "https://www.clackamas.us/diversity",
            "https://www.clackamas.us/equity",
        ]
        
        urls_to_visit = set(seed_urls)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            iteration = 0
            while urls_to_visit and len(self.collected_urls) < self.max_urls:
                iteration += 1
                self.log(f"Crawl iteration {iteration}: {len(urls_to_visit)} URLs queued, {len(self.collected_urls)} visited")
                
                # Process batch
                batch = []
                for _ in range(min(10, len(urls_to_visit))):
                    if urls_to_visit:
                        batch.append(urls_to_visit.pop())
                
                for url in batch:
                    if url in self.collected_urls:
                        continue
                    
                    self.collected_urls.add(url)
                    page_data = await self.scrape_page_enhanced(url, browser)
                    
                    if page_data:
                        new_urls = self.discover_urls(page_data, url)
                        urls_to_visit.update(new_urls)
                    
                    await asyncio.sleep(1.5)  # Rate limiting
            
            await browser.close()
        
        self.log(f"Crawl complete: {len(self.collected_urls)} URLs visited")
    
    async def run_comprehensive_research(self):
        """Run comprehensive research"""
        self.log("=" * 80)
        self.log("COMPREHENSIVE DEI RESEARCH - HOUSING AUTHORITY OF CLACKAMAS COUNTY")
        self.log("=" * 80)
        
        # 1. Multiple search queries
        search_queries = [
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
        
        all_search_results = []
        for query in search_queries:
            results = self.search_duckduckgo_html(query)
            all_search_results.extend(results)
            time.sleep(3)
        
        # Save search results
        with open(self.results_dir / f"all_search_results_{self.timestamp}.json", "w") as f:
            json.dump(all_search_results, f, indent=2)
        
        self.log(f"Total search results collected: {len(all_search_results)}")
        
        # 2. Deep crawl
        await self.crawl_site_deep()
        
        # 3. Compile comprehensive report
        self.compile_comprehensive_report()
        
        self.log("=" * 80)
        self.log("RESEARCH COMPLETE")
        self.log(f"Results directory: {self.results_dir.absolute()}")
        self.log("=" * 80)
    
    def compile_comprehensive_report(self):
        """Compile detailed report"""
        # Group findings
        by_keyword = {}
        by_url = {}
        
        for finding in self.findings:
            kw = finding['keyword']
            url = finding['url']
            
            if kw not in by_keyword:
                by_keyword[kw] = []
            by_keyword[kw].append(finding)
            
            if url not in by_url:
                by_url[url] = []
            by_url[url].append(finding)
        
        # Calculate statistics
        total_occurrences = sum(f['count'] for f in self.findings)
        
        report = {
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'total_urls_analyzed': len(self.collected_urls),
                'total_documents_collected': len(self.collected_documents),
                'total_findings': len(self.findings),
                'total_keyword_occurrences': total_occurrences,
                'keywords_searched': DEI_KEYWORDS
            },
            'urls_analyzed': list(self.collected_urls),
            'documents_collected': list(self.collected_documents),
            'findings_by_keyword': {k: len(v) for k, v in by_keyword.items()},
            'findings_by_url': {k: len(v) for k, v in by_url.items()},
            'detailed_findings': self.findings
        }
        
        # Save JSON
        with open(self.results_dir / f"comprehensive_report_{self.timestamp}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Create detailed summary
        summary = []
        summary.append("=" * 80)
        summary.append("COMPREHENSIVE DEI RESEARCH REPORT")
        summary.append("HOUSING AUTHORITY OF CLACKAMAS COUNTY")
        summary.append("=" * 80)
        summary.append(f"\nReport Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Research Duration: See research.log for details")
        summary.append("\n" + "-" * 80)
        summary.append("EXECUTIVE SUMMARY")
        summary.append("-" * 80)
        summary.append(f"Total URLs Analyzed: {len(self.collected_urls)}")
        summary.append(f"Total Documents Collected: {len(self.collected_documents)}")
        summary.append(f"Unique DEI Keywords Found: {len(by_keyword)}")
        summary.append(f"Total Keyword Occurrences: {total_occurrences}")
        summary.append(f"URLs with DEI Content: {len(by_url)}")
        
        summary.append("\n" + "=" * 80)
        summary.append("FINDINGS BY KEYWORD (Ranked by Frequency)")
        summary.append("=" * 80)
        
        keyword_totals = {}
        for kw, findings in by_keyword.items():
            keyword_totals[kw] = sum(f['count'] for f in findings)
        
        for keyword, count in sorted(keyword_totals.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"\n{keyword.upper()}: {count} total occurrences")
            summary.append(f"  Found on {len(by_keyword[keyword])} pages")
            
            # Show examples from different pages
            examples = by_keyword[keyword][:3]
            for i, example in enumerate(examples, 1):
                summary.append(f"\n  Example {i} from: {example['url']}")
                if example['contexts']:
                    context = example['contexts'][0][:250].replace('\n', ' ')
                    summary.append(f"    \"...{context}...\"")
        
        summary.append("\n" + "=" * 80)
        summary.append("URLS WITH DEI CONTENT (Ranked by Keyword Density)")
        summary.append("=" * 80)
        
        url_scores = {}
        for url, findings in by_url.items():
            url_scores[url] = sum(f['count'] for f in findings)
        
        for url, score in sorted(url_scores.items(), key=lambda x: x[1], reverse=True)[:50]:
            summary.append(f"\n{url}")
            summary.append(f"  Total DEI references: {score}")
            keywords_found = [f['keyword'] for f in by_url[url]]
            summary.append(f"  Keywords: {', '.join(set(keywords_found[:10]))}")
        
        if self.collected_documents:
            summary.append("\n" + "=" * 80)
            summary.append("DOCUMENTS COLLECTED")
            summary.append("=" * 80)
            for doc in sorted(self.collected_documents):
                summary.append(f"  {doc}")
        
        summary.append("\n" + "=" * 80)
        summary.append("ALL URLS ANALYZED")
        summary.append("=" * 80)
        for url in sorted(self.collected_urls):
            summary.append(f"  {url}")
        
        summary_text = "\n".join(summary)
        
        with open(self.results_dir / f"detailed_summary_{self.timestamp}.txt", "w") as f:
            f.write(summary_text)
        
        # Also create a CSV for easy analysis
        try:
            import csv
            with open(self.results_dir / f"findings_{self.timestamp}.csv", "w", newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Keyword', 'Count', 'First Context'])
                for finding in self.findings:
                    context = finding['contexts'][0][:500] if finding['contexts'] else ''
                    writer.writerow([
                        finding['url'],
                        finding['keyword'],
                        finding['count'],
                        context
                    ])
        except Exception as e:
            self.log(f"Error creating CSV: {e}")
        
        print("\n" + summary_text)

if __name__ == "__main__":
    researcher = EnhancedHAACCResearcher()
    asyncio.run(researcher.run_comprehensive_research())
