#!/usr/bin/env python3
"""
Research script to collect DEI-related information from Housing Authority of Clackamas County
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

# DEI-related keywords and euphemisms
DEI_KEYWORDS = [
    # Direct terms
    'diversity', 'equity', 'inclusion', 'DEI', 'DEIB', 'belonging',
    'diverse', 'equitable', 'inclusive',
    
    # Euphemisms and proxies
    'social justice', 'racial justice', 'environmental justice',
    'disparate impact', 'disparity', 'disparities',
    'underrepresented', 'underserved', 'marginalized',
    'protected class', 'protected classes',
    'affirmative action', 'equal opportunity',
    'cultural competency', 'cultural competence', 'culturally responsive',
    'implicit bias', 'unconscious bias', 'anti-bias',
    'anti-racism', 'antiracism', 'racial equity',
    'systemic racism', 'structural racism', 'institutional racism',
    'white privilege', 'privilege',
    'intersectionality', 'intersectional',
    'microaggression', 'microaggressions',
    'safe space', 'brave space',
    'restorative justice', 'transformative justice',
    'community engagement', 'stakeholder engagement',
    'accessibility', 'accessible',
    'fair housing', 'housing justice',
    'economic justice', 'wealth gap',
    'opportunity gap', 'achievement gap',
    'historically excluded', 'historically marginalized',
    'underinvested communities',
    'BIPOC', 'people of color', 'communities of color',
    'LGBTQ', 'LGBTQIA', 'gender identity', 'sexual orientation',
    'lived experience',
    'centering voices', 'elevating voices',
    'power dynamics', 'power imbalance',
    'allyship', 'ally',
    'decolonize', 'decolonization',
]

class HAACCResearcher:
    def __init__(self):
        self.base_url = "https://www.clackamas.us/housingauthority"
        self.results_dir = Path("research_results")
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        self.collected_urls = set()
        self.findings = []
        
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.results_dir / "research.log", "a") as f:
            f.write(log_msg + "\n")
    
    def search_brave(self, query):
        """Search using Brave Search API (requires API key)"""
        api_key = os.environ.get('BRAVE_API_KEY')
        if not api_key:
            self.log("WARNING: BRAVE_API_KEY not set, skipping Brave search")
            return []
        
        try:
            self.log(f"Searching Brave for: {query}")
            headers = {
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip',
                'X-Subscription-Token': api_key
            }
            url = "https://api.search.brave.com/res/v1/web/search"
            params = {
                'q': f'{query} site:clackamas.us',
                'count': 20
            }
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = []
            if 'web' in data and 'results' in data['web']:
                for result in data['web']['results']:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'description': result.get('description', ''),
                        'source': 'brave'
                    })
            
            self.log(f"Found {len(results)} results from Brave")
            return results
        except Exception as e:
            self.log(f"Error with Brave search: {e}")
            return []
    
    def search_duckduckgo(self, query):
        """Search using DuckDuckGo HTML scraping"""
        try:
            self.log(f"Searching DuckDuckGo for: {query}")
            url = "https://html.duckduckgo.com/html/"
            params = {
                'q': f'{query} site:clackamas.us'
            }
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }
            
            response = requests.post(url, data=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            results = []
            
            for result in soup.find_all('div', class_='result'):
                title_elem = result.find('a', class_='result__a')
                snippet_elem = result.find('a', class_='result__snippet')
                
                if title_elem:
                    results.append({
                        'title': title_elem.get_text(strip=True),
                        'url': title_elem.get('href', ''),
                        'description': snippet_elem.get_text(strip=True) if snippet_elem else '',
                        'source': 'duckduckgo'
                    })
            
            self.log(f"Found {len(results)} results from DuckDuckGo")
            time.sleep(2)  # Rate limiting
            return results
        except Exception as e:
            self.log(f"Error with DuckDuckGo search: {e}")
            return []
    
    def search_commoncrawl(self, domain):
        """Search CommonCrawl index for domain"""
        try:
            self.log(f"Searching CommonCrawl for: {domain}")
            # Get latest index
            index_url = "https://index.commoncrawl.org/collinfo.json"
            response = requests.get(index_url, timeout=30)
            response.raise_for_status()
            indexes = response.json()
            
            if not indexes:
                return []
            
            latest_index = indexes[0]['cdx-api']
            
            # Search for URLs
            search_url = f"{latest_index}"
            params = {
                'url': f'{domain}/*',
                'output': 'json',
                'limit': 1000
            }
            
            response = requests.get(search_url, params=params, timeout=60)
            response.raise_for_status()
            
            results = []
            for line in response.text.strip().split('\n'):
                if line:
                    try:
                        data = json.loads(line)
                        results.append({
                            'url': data.get('url', ''),
                            'timestamp': data.get('timestamp', ''),
                            'source': 'commoncrawl'
                        })
                    except:
                        continue
            
            self.log(f"Found {len(results)} results from CommonCrawl")
            return results
        except Exception as e:
            self.log(f"Error with CommonCrawl search: {e}")
            return []
    
    async def scrape_page(self, url, browser):
        """Scrape a single page using Playwright"""
        try:
            self.log(f"Scraping: {url}")
            context = await browser.new_context(
                user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            )
            page = await context.new_page()
            
            await page.goto(url, wait_until='networkidle', timeout=30000)
            content = await page.content()
            text = await page.evaluate('document.body.innerText')
            
            await context.close()
            
            # Save full HTML
            filename = re.sub(r'[^\w\-_]', '_', url)[:100]
            with open(self.results_dir / f"{filename}_{self.timestamp}.html", "w") as f:
                f.write(content)
            
            # Analyze content for DEI keywords
            matches = self.analyze_content(url, text, content)
            if matches:
                self.findings.extend(matches)
            
            return text
        except Exception as e:
            self.log(f"Error scraping {url}: {e}")
            return None
    
    def analyze_content(self, url, text, html):
        """Analyze content for DEI keywords and context"""
        matches = []
        text_lower = text.lower()
        
        for keyword in DEI_KEYWORDS:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, text_lower):
                # Find context around matches
                contexts = []
                for match in re.finditer(pattern, text_lower):
                    start = max(0, match.start() - 150)
                    end = min(len(text), match.end() + 150)
                    context = text[start:end].strip()
                    contexts.append(context)
                
                matches.append({
                    'url': url,
                    'keyword': keyword,
                    'count': len(contexts),
                    'contexts': contexts[:5],  # First 5 contexts
                    'timestamp': datetime.now().isoformat()
                })
        
        return matches
    
    def discover_urls(self, html_content, base_url):
        """Extract URLs from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        urls = set()
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Only keep URLs from clackamas.us domain
            if 'clackamas.us' in full_url and full_url not in self.collected_urls:
                urls.add(full_url)
        
        return urls
    
    async def crawl_site(self):
        """Main crawling function"""
        self.log("Starting site crawl...")
        
        # Start with main housing authority pages
        initial_urls = [
            "https://www.clackamas.us/housingauthority",
            "https://www.clackamas.us/housingauthority/about",
            "https://www.clackamas.us/housingauthority/programs",
            "https://www.clackamas.us/housingauthority/resources",
            "https://www.clackamas.us/housingauthority/contact",
        ]
        
        urls_to_visit = set(initial_urls)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            while urls_to_visit and len(self.collected_urls) < 100:
                url = urls_to_visit.pop()
                if url in self.collected_urls:
                    continue
                
                self.collected_urls.add(url)
                content = await self.scrape_page(url, browser)
                
                if content:
                    # Discover new URLs
                    new_urls = self.discover_urls(content, url)
                    urls_to_visit.update(new_urls)
                
                await asyncio.sleep(1)  # Rate limiting
            
            await browser.close()
    
    async def run_full_research(self):
        """Run complete research process"""
        self.log("=" * 80)
        self.log("Starting DEI Research on Housing Authority of Clackamas County")
        self.log("=" * 80)
        
        # 1. Search engines
        all_search_results = []
        
        for keyword in ['diversity equity inclusion', 'DEI', 'fair housing', 
                       'racial equity', 'social justice', 'community engagement']:
            all_search_results.extend(self.search_brave(f"Clackamas County Housing Authority {keyword}"))
            all_search_results.extend(self.search_duckduckgo(f"Clackamas County Housing Authority {keyword}"))
            time.sleep(2)
        
        # Save search results
        with open(self.results_dir / f"search_results_{self.timestamp}.json", "w") as f:
            json.dump(all_search_results, f, indent=2)
        
        # 2. CommonCrawl
        cc_results = self.search_commoncrawl("clackamas.us/housingauthority")
        with open(self.results_dir / f"commoncrawl_results_{self.timestamp}.json", "w") as f:
            json.dump(cc_results, f, indent=2)
        
        # 3. Direct crawling
        await self.crawl_site()
        
        # 4. Compile findings
        self.compile_report()
        
        self.log("=" * 80)
        self.log("Research complete!")
        self.log(f"Results saved to: {self.results_dir}")
        self.log("=" * 80)
    
    def compile_report(self):
        """Compile final report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_urls_collected': len(self.collected_urls),
            'total_findings': len(self.findings),
            'urls_visited': list(self.collected_urls),
            'findings': self.findings,
            'keywords_searched': DEI_KEYWORDS
        }
        
        # Save JSON report
        with open(self.results_dir / f"dei_findings_{self.timestamp}.json", "w") as f:
            json.dump(report, f, indent=2)
        
        # Create human-readable summary
        summary = []
        summary.append("=" * 80)
        summary.append("DEI RESEARCH FINDINGS - HOUSING AUTHORITY OF CLACKAMAS COUNTY")
        summary.append("=" * 80)
        summary.append(f"\nResearch Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"Total URLs Analyzed: {len(self.collected_urls)}")
        summary.append(f"Total DEI References Found: {len(self.findings)}")
        summary.append("\n" + "=" * 80)
        summary.append("FINDINGS BY KEYWORD")
        summary.append("=" * 80)
        
        # Group by keyword
        keyword_counts = {}
        for finding in self.findings:
            kw = finding['keyword']
            keyword_counts[kw] = keyword_counts.get(kw, 0) + finding['count']
        
        for keyword, count in sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True):
            summary.append(f"\n{keyword}: {count} occurrences")
            
            # Show some examples
            examples = [f for f in self.findings if f['keyword'] == keyword][:3]
            for example in examples:
                summary.append(f"  URL: {example['url']}")
                if example['contexts']:
                    summary.append(f"  Context: ...{example['contexts'][0][:200]}...")
        
        summary.append("\n" + "=" * 80)
        summary.append("URLS ANALYZED")
        summary.append("=" * 80)
        for url in sorted(self.collected_urls):
            summary.append(f"  {url}")
        
        summary_text = "\n".join(summary)
        with open(self.results_dir / f"summary_report_{self.timestamp}.txt", "w") as f:
            f.write(summary_text)
        
        print("\n" + summary_text)

if __name__ == "__main__":
    researcher = HAACCResearcher()
    asyncio.run(researcher.run_full_research())
