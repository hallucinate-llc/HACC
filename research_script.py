#!/usr/bin/env python3
"""
Research script to collect DEI-related information from Housing Authority of Clackamas County
"""

import asyncio
import argparse
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
    def __init__(self, base_url: str = "https://www.clackamas.us/housingauthority", allowed_domains: set[str] | None = None):
        self.base_url = base_url
        self.results_dir = Path("research_results")
        self.results_dir.mkdir(exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.allowed_domains = allowed_domains or {"clackamas.us"}
        
        self.collected_urls = set()
        self.findings = []

        # Keep a persistent DDG session; DDG often returns a 202 homepage response
        # unless a session is established (warmup GET) before searching.
        self._ddg_session = requests.Session()
        self._ddg_warmed = False
        
    def log(self, message):
        """Log message to console and file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)
        with open(self.results_dir / "research.log", "a") as f:
            f.write(log_msg + "\n")
    
    def search_brave(self, query: str):
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
                'q': query,
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
    
    def search_duckduckgo(self, query: str):
        """Search using DuckDuckGo HTML scraping"""
        def is_ddg_interstitial(html: str) -> bool:
            if not html:
                return True
            h = html.lower()
            # DDG sometimes returns a Next.js 50x page (not results HTML)
            if "duckduckgo.com/50x" in h or "page\":\"/50x\"" in h:
                return True
            if "unexpected error" in h and "duckduckgo" in h:
                return True
            if "query entered was too long" in h:
                return True
            return False

        def simplify_query_for_ddg(q: str, max_chars: int, *, aggressive: bool = False) -> str:
            # Keep site restriction(s) and the first quoted phrase (often the entity),
            # then add a small number of remaining terms.
            qn = re.sub(r"\s+", " ", (q or "").strip())
            if not qn:
                return qn

            # Extract site: tokens and quoted phrases.
            site_tokens = re.findall(r"\bsite:[^\s)]+", qn)
            quoted = re.findall(r"\"([^\"]+)\"", qn)
            entity = f'"{quoted[0]}"' if quoted else ""

            # Remove parenthetical OR blocks entirely (they are what makes queries blow up).
            q2 = re.sub(r"\([^)]*\)", " ", qn)
            q2 = re.sub(r"\s+", " ", q2).strip()

            # Tokenize the remaining pieces, dropping OR and punctuation-ish tokens.
            raw_tokens = [t for t in re.split(r"\s+", q2) if t]
            drop = {"or", "and", "(" ,")"}
            tokens: list[str] = []
            for t in raw_tokens:
                tl = t.lower()
                if tl in drop:
                    continue
                if tl.startswith("site:"):
                    continue
                if t in {"-", "+"}:
                    continue
                tokens.append(t)

            # Prefer a few meaningful tokens.
            keep_tokens: list[str] = []
            for t in tokens:
                if len(keep_tokens) >= (4 if aggressive else 6):
                    break
                keep_tokens.append(t)

            parts: list[str] = []
            parts.extend(site_tokens[:2])
            if entity:
                parts.append(entity if not aggressive else quoted[0])
            parts.extend(keep_tokens)
            out = re.sub(r"\s+", " ", " ".join(parts)).strip()

            # Hard cap
            if len(out) > max_chars:
                out = out[:max_chars].rsplit(" ", 1)[0]
            return out

        try:
            self.log(f"Searching DuckDuckGo for: {query}")
            url = "https://html.duckduckgo.com/html/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
            }

            # Warm up the session once to reduce 202 responses.
            if not self._ddg_warmed:
                try:
                    _ = self._ddg_session.get(url, headers=headers, timeout=30)
                except Exception:
                    # Non-fatal: we'll still try POST below.
                    pass
                self._ddg_warmed = True

            max_chars = 320
            q = re.sub(r"\s+", " ", (query or "").strip())
            backoff = 2.0
            last_status: int | None = None
            last_html: str | None = None

            # Increase attempts and backoff cap to be more tolerant of DDG rate-limiting
            for attempt in range(6):
                params = {'q': q}
                response = self._ddg_session.post(url, data=params, headers=headers, timeout=30)
                last_status = response.status_code
                last_html = response.text or ""

                # DDG occasionally returns 202 (rate limiting / queued) with non-result HTML.
                if response.status_code == 202:
                    # Try a quick warmup GET (DDG sometimes returns a 202 homepage until warmed).
                    try:
                        _ = self._ddg_session.get(url, headers=headers, timeout=30)
                    except Exception:
                        pass

                    # Some query shapes trigger persistent 202 responses.
                    # Try simplifying the query between attempts.
                    if attempt == 0:
                        shorter = simplify_query_for_ddg(q, max_chars=max_chars, aggressive=True)
                        if shorter and shorter != q:
                            self.log("DuckDuckGo returned 202; retrying with a simplified query")
                            q = shorter
                    elif attempt == 1:
                        shorter = simplify_query_for_ddg(q, max_chars=200, aggressive=True)
                        if shorter and shorter != q:
                            self.log("DuckDuckGo returned 202 again; retrying with a more aggressive simplification")
                            q = shorter

                    self.log(f"DuckDuckGo returned 202; backing off {backoff:.1f}s and retrying")
                    time.sleep(backoff)
                    backoff = min(60.0, backoff * 2.0)
                    continue

                # If we hit a DDG interstitial/error page, try a shorter query.
                if is_ddg_interstitial(last_html):
                    shorter = simplify_query_for_ddg(q, max_chars=max_chars)
                    if shorter and shorter != q:
                        self.log("DuckDuckGo returned an error/too-long page; retrying with a simplified query")
                        q = shorter
                        time.sleep(1.5)
                        continue
                    break

                if response.status_code >= 400:
                    response.raise_for_status()

                soup = BeautifulSoup(last_html, 'html.parser')
                results: list[dict] = []

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

                # If parsing yields 0 results, it may still be a non-standard response; try simplifying once.
                if not results and attempt == 0 and (len(q) > max_chars or " or " in q.lower() or "(" in q):
                    shorter = simplify_query_for_ddg(q, max_chars=max_chars)
                    if shorter and shorter != q:
                        self.log("DuckDuckGo returned 0 parsed results; retrying with a simplified query")
                        q = shorter
                        time.sleep(1.5)
                        continue

                self.log(f"Found {len(results)} results from DuckDuckGo")
                time.sleep(3)  # Rate limiting — increased slightly
                return results

            # Optional: store a debug artifact if we repeatedly get non-result pages.
            if last_html and is_ddg_interstitial(last_html):
                debug_path = self.results_dir / f"ddg_interstitial_{self.timestamp}.html"
                debug_path.write_text(last_html, encoding="utf-8")
                self.log(f"Saved DuckDuckGo interstitial HTML for debugging: {debug_path}")
            if last_status is not None:
                self.log(f"DuckDuckGo produced no parseable results (status={last_status})")
            return []
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

            parsed = urlparse(full_url)
            host = (parsed.netloc or "").lower()
            if not host:
                continue
            if any(host == d or host.endswith("." + d) for d in self.allowed_domains):
                if full_url not in self.collected_urls:
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
            q = f"Clackamas County Housing Authority {keyword} site:clackamas.us"
            all_search_results.extend(self.search_brave(q))
            all_search_results.extend(self.search_duckduckgo(q))
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

    def run_seeded_search(self, queries_file: str, enable_brave: bool = True, enable_duckduckgo: bool = True) -> list[dict]:
        """Run search using a file of fully-formed queries (one per line)."""
        path = Path(queries_file)
        if not path.exists():
            raise FileNotFoundError(queries_file)

        queries: list[str] = []
        for line in path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            queries.append(s)

        self.log(f"Loaded {len(queries)} seeded queries from {queries_file}")
        all_search_results: list[dict] = []

        for q in queries:
            # Prefer Brave if enabled and API key is configured
            brave_key = os.environ.get('BRAVE_API_KEY')
            if enable_brave and brave_key:
                self.log("BRAVE_API_KEY detected — using Brave for this query")
                try:
                    all_search_results.extend(self.search_brave(q))
                except Exception as e:
                    self.log(f"Brave search error, falling back to DuckDuckGo: {e}")

            # Always try DuckDuckGo if enabled (as a secondary source / fallback)
            if enable_duckduckgo:
                all_search_results.extend(self.search_duckduckgo(q))

            # Respect a slightly longer inter-query sleep to avoid DDG throttling
            time.sleep(3)

        out = self.results_dir / f"seeded_search_results_{self.timestamp}.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(all_search_results, f, indent=2)
        self.log(f"Wrote seeded search results: {out}")
        return all_search_results

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


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Collect research results via search engines, CommonCrawl, and crawling.")
    p.add_argument("--queries-file", help="Path to a file with one search query per line (fully formed).")
    p.add_argument("--allowed-domain", action="append", default=[], help="Allowed domain for Playwright crawling (repeatable). Default: clackamas.us")
    p.add_argument("--no-crawl", action="store_true", help="Skip Playwright crawling step.")
    p.add_argument("--no-commoncrawl", action="store_true", help="Skip CommonCrawl step.")
    p.add_argument("--commoncrawl-domain", action="append", default=["clackamas.us/housingauthority"], help="CommonCrawl domain/path to query (repeatable).")
    p.add_argument("--no-brave", action="store_true", help="Disable Brave search (uses BRAVE_API_KEY).")
    p.add_argument("--no-duckduckgo", action="store_true", help="Disable DuckDuckGo search.")
    return p.parse_args()

if __name__ == "__main__":
    args = _parse_args()
    allowed_domains = set(args.allowed_domain) if args.allowed_domain else {"clackamas.us"}
    researcher = HAACCResearcher(allowed_domains=allowed_domains)

    async def _main() -> None:
        if args.queries_file:
            researcher.run_seeded_search(
                args.queries_file,
                enable_brave=not args.no_brave,
                enable_duckduckgo=not args.no_duckduckgo,
            )
        else:
            if args.no_brave and args.no_duckduckgo:
                researcher.log("Both Brave and DuckDuckGo disabled; skipping search step")
            else:
                # keep the original default behavior
                pass

        if not args.no_commoncrawl:
            all_cc = []
            for dom in args.commoncrawl_domain:
                all_cc.extend(researcher.search_commoncrawl(dom))
            with open(researcher.results_dir / f"commoncrawl_results_{researcher.timestamp}.json", "w") as f:
                json.dump(all_cc, f, indent=2)

        if not args.no_crawl:
            await researcher.crawl_site()

        researcher.compile_report()

    # If no args were provided, run original full flow.
    if not any(
        [
            args.queries_file,
            args.allowed_domain,
            args.no_crawl,
            args.no_commoncrawl,
            args.commoncrawl_domain != ["clackamas.us/housingauthority"],
            args.no_brave,
            args.no_duckduckgo,
        ]
    ):
        asyncio.run(researcher.run_full_research())
    else:
        asyncio.run(_main())
