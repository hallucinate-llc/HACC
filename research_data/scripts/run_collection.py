#!/usr/bin/env python3
"""
run_collection.py — Main orchestration script to collect, parse, and index documents.
Supports multiple collection methods: Brave API, fallback web scraping, local file ingestion.
Includes queue management, backoff strategy, and link extraction.
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime
import logging
import time
from queue import Queue
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from collections import deque

# Import custom modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'research_data', 'scripts'))
try:
    from download_manager import DownloadManager
    from parse_pdfs import PDFParser
    from index_and_tag import DocumentIndexer
    from report_generator import ReportGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure all scripts are in research_data/scripts/")
    sys.exit(1)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CollectionOrchestrator:
    """Orchestrate the full collection, parsing, and reporting workflow."""
    
    def __init__(self):
        self.dm = DownloadManager()
        self.parser = PDFParser()
        self.indexer = DocumentIndexer()
        self.reporter = ReportGenerator()
        self.visited_urls = set()
        self.link_queue = deque()
        self.backoff_delay = 1  # Start with 1 second
        self.max_backoff_delay = 32  # Max 32 seconds
        self.rate_limit_retries = 0
        self.max_retries = 3
    
    def collect_from_brave_api(self) -> list:
        """
        Collect URLs from Brave Search API using the provided API key.
        Includes queue management and link extraction.
        Returns list of discovered URLs.
        """
        api_key = os.getenv('BRAVE_API_KEY')
        if not api_key:
            logger.warning("BRAVE_API_KEY not set; falling back to query list only")
            return self._get_default_queries()
        
        logger.info("Starting Brave Search API collection with backoff strategy...")
        
        queries = [
            # Clackamas County Housing Authority - Primary Focus
            'site:clackamas.us "housing authority"',
            'site:clackamas.us filetype:pdf "housing" policy',
            'site:clackamas.us filetype:pdf "affordable housing" OR "housing assistance"',
            'site:clackamas.us filetype:pdf board minutes housing',
            'site:clackamas.us filetype:pdf housing diversity OR equity',
            # Clackamas County General Policies
            'site:clackamas.us filetype:pdf procurement policy',
            'site:clackamas.us filetype:pdf hiring OR employment',
            'site:clackamas.us filetype:pdf diversity OR "equal opportunity"',
            # Clackamas County Coordinated Housing Access
            'site:clackamas.us "coordinated housing access" OR CCHA',
        ]
        
        urls_found = []
        
        for query in queries:
            results = self._api_query_with_backoff(query, api_key)
            
            # Extract PDF URLs and web pages
            for result in results:
                result_url = result.get("url")
                if not result_url or result_url in self.visited_urls:
                    continue
                
                self.visited_urls.add(result_url)
                
                url_entry = {
                    "url": result_url,
                    "title": result.get("title"),
                    "description": result.get("description"),
                    "source": "brave_api",
                    "query": query
                }
                
                # If it's a PDF, add directly
                if ".pdf" in result_url.lower():
                    urls_found.append(url_entry)
                    logger.info(f"  PDF: {result_url[:70]}")
                else:
                    # Queue non-PDF pages for link extraction
                    self.link_queue.append(result_url)
                    logger.info(f"  Page: {result_url[:70]} (queued for link extraction)")
        
        logger.info(f"Discovered {len(urls_found)} PDF URLs directly from API")
        logger.info(f"Queued {len(self.link_queue)} pages for link extraction")
        
        # Extract links from queued pages
        logger.info("\n[LINK EXTRACTION] Processing queued pages...")
        while self.link_queue and len(urls_found) < 100:  # Safety limit
            page_url = self.link_queue.popleft()
            
            if page_url in self.visited_urls:
                continue
            
            logger.info(f"Fetching page: {page_url[:70]}...")
            html_content, status = self._fetch_page_with_backoff(page_url)
            
            if html_content:
                extracted_links = self._extract_links(html_content, page_url)
                for link in extracted_links:
                    if link['url'] not in self.visited_urls and link not in urls_found:
                        urls_found.append(link)
                        logger.info(f"  Extracted: {link['url'][:70]}")
        
        logger.info(f"\nTotal URLs discovered: {len(urls_found)}")
        return urls_found
    
    def _get_default_queries(self) -> list:
        """Fallback: return list of intended queries for manual collection."""
        return [
            {
                "query": "site:oregon.gov filetype:pdf diversity equity inclusion",
                "description": "Oregon DEI Policies"
            },
            {
                "query": "site:clackamas.us filetype:pdf diversity equity",
                "description": "Clackamas County Diversity"
            }
        ]
    
    def _handle_rate_limit(self) -> None:
        """Exponential backoff for rate limiting."""
        wait_time = self.backoff_delay
        logger.warning(f"Rate limited. Waiting {wait_time}s before retry...")
        time.sleep(wait_time)
        self.backoff_delay = min(self.backoff_delay * 2, self.max_backoff_delay)
    
    def _extract_links(self, html_content: str, base_url: str) -> list:
        """Extract PDF and policy links from HTML content."""
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                text = link.get_text(strip=True)
                
                # Convert relative URLs to absolute
                full_url = urljoin(base_url, href)
                
                # Skip if already visited
                if full_url in self.visited_urls:
                    continue
                
                # Filter for relevant document links
                if any(x in full_url.lower() for x in ['.pdf', 'policy', 'housing', 'board', 'plan', 'report']):
                    links.append({
                        'url': full_url,
                        'text': text,
                        'source': 'extracted_link',
                        'parent_url': base_url
                    })
                    self.visited_urls.add(full_url)
            
            logger.info(f"Extracted {len(links)} relevant links from {base_url}")
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        return links
    
    def _fetch_page_with_backoff(self, url: str) -> tuple:
        """Fetch a page with exponential backoff for rate limiting."""
        retries = 0
        while retries < self.max_retries:
            try:
                resp = requests.get(url, timeout=30)
                
                if resp.status_code == 429:
                    self._handle_rate_limit()
                    retries += 1
                    continue
                
                resp.raise_for_status()
                self.backoff_delay = 1  # Reset backoff on success
                return resp.text, resp.status_code
            
            except requests.exceptions.RequestException as e:
                logger.error(f"Request error for {url}: {e}")
                retries += 1
                if retries < self.max_retries:
                    self._handle_rate_limit()
        
        return None, None
    
    def _api_query_with_backoff(self, query: str, api_key: str) -> list:
        """Execute API query with exponential backoff for rate limiting."""
        retries = 0
        while retries < self.max_retries:
            try:
                logger.info(f"API Query: {query[:60]}... (attempt {retries + 1}/{self.max_retries})")
                
                url = "https://api.search.brave.com/res/v1/web/search"
                headers = {
                    "Accept": "application/json",
                    "X-Subscription-Token": api_key
                }
                params = {
                    "q": query,
                    "count": 20
                }
                
                resp = requests.get(url, headers=headers, params=params, timeout=30)
                
                if resp.status_code == 429:
                    self._handle_rate_limit()
                    retries += 1
                    continue
                
                resp.raise_for_status()
                self.backoff_delay = 1  # Reset backoff on success
                
                data = resp.json()
                results = data.get("web", {}).get("results", [])
                logger.info(f"  Found {len(results)} results")
                
                return results
            
            except requests.exceptions.RequestException as e:
                logger.error(f"API error: {e}")
                retries += 1
                if retries < self.max_retries:
                    self._handle_rate_limit()
        
        return []
    
    def collect_from_web_simple(self) -> list:
        """
        Simple fallback: collect URLs from Oregon.gov using requests (no API key needed).
        This is a demonstration using basic web search technique.
        Returns list of URLs found.
        """
        logger.info("Starting simple web collection (fallback, no API key required)...")
        
        queries = [
            {
                "query": "site:oregon.gov/biz diversity equity inclusion",
                "description": "Oregon Business & Industry DEI"
            },
            {
                "query": "site:oregon.gov/hcs housing communities services diversity",
                "description": "Oregon HCS Diversity"
            },
            {
                "query": "site:clackamas.us housing diversity equity",
                "description": "Clackamas County Housing Diversity"
            }
        ]
        
        urls_found = []
        
        # Simple fallback: search via DuckDuckGo (no key required)
        for q_obj in queries:
            logger.info(f"Searching: {q_obj['description']}")
            
            # Use requests to get HTML from a simple search
            # (In production, use a proper search API or web crawler)
            # For demo, we'll just note the intended queries
            logger.info(f"  Query: {q_obj['query']}")
            urls_found.append(q_obj)
        
        logger.info(f"Identified {len(urls_found)} search topics for manual/API collection")
        return urls_found
    
    def run_full_workflow(self, pdf_dir: str = None) -> dict:
        """
        Run full workflow:
        1. Collect from web (API or fallback)
        2. Download PDFs
        3. Parse PDFs
        4. Index and tag
        5. Generate reports
        """
        logger.info("=" * 80)
        logger.info("Starting DEI Compliance Collection & Analysis Workflow")
        logger.info("=" * 80)
        
        # Step 1: Identify PDFs to collect
        logger.info("\n[STEP 1] Identifying documents to collect...")
        queries = self.collect_from_brave_api()  # Try API first, fallback to defaults
        
        # Step 2: Download PDFs from discovered URLs
        logger.info("\n[STEP 2] Downloading PDFs...")
        pdf_files = []
        if queries and isinstance(queries[0], dict) and "url" in queries[0]:
            # We got URLs from Brave API
            for url_item in queries:
                fp = self.dm.download_pdf(url_item["url"], url_item.get("source", "brave"))
                if fp:
                    pdf_files.append(fp)
        else:
            # No API results; check for local directory
            if pdf_dir and Path(pdf_dir).exists():
                logger.info(f"Using local PDF directory: {pdf_dir}")
                pdf_files = list(Path(pdf_dir).glob("*.pdf"))
                logger.info(f"Found {len(pdf_files)} PDFs to parse")
            else:
                logger.info("No PDFs discovered. (Provide Brave API key or use --pdf-dir for local files)")
        
        logger.info(f"Downloaded/available: {len(pdf_files)} PDF(s)")
        
        # Step 3: Parse PDFs
        logger.info("\n[STEP 3] Parsing PDFs...")
        parsed_count = 0
        if pdf_files:
            for pdf_file in pdf_files:
                # Create minimal metadata
                metadata = {
                    "url": f"file://{pdf_file}",
                    "source": "local_file",
                    "download_date": datetime.now().isoformat()
                }
                self.parser.parse_pdf(str(pdf_file), metadata)
                parsed_count += 1
            logger.info(f"Parsed {parsed_count} PDFs")
        else:
            logger.info("No PDFs to parse. (Collect PDFs first, then re-run)")
        
        # Step 4: Index and tag
        logger.info("\n[STEP 4] Indexing and tagging documents...")
        self.indexer.batch_index()
        index_file = self.indexer.save_index()
        csv_file = self.indexer.export_csv_summary()
        logger.info(f"Index saved to {index_file}")
        logger.info(f"CSV summary saved to {csv_file}")
        
        # Step 5: Generate reports
        logger.info("\n[STEP 5] Generating reports...")
        self.reporter.load_index(index_file)
        summary_file = self.reporter.save_summary()
        detailed_file = self.reporter.save_detailed_report()
        
        # Print summary to console
        logger.info("\n" + "=" * 80)
        logger.info("SUMMARY REPORT")
        logger.info("=" * 80)
        logger.info(self.reporter.generate_one_page_summary())
        
        results = {
            "queries_identified": len(queries),
            "pdfs_parsed": parsed_count,
            "documents_indexed": len(self.indexer.index),
            "index_file": index_file,
            "csv_file": csv_file,
            "summary_file": summary_file,
            "detailed_report_file": detailed_file,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info("\n" + "=" * 80)
        logger.info("WORKFLOW COMPLETE")
        logger.info("=" * 80)
        logger.info(f"Results: {json.dumps(results, indent=2)}")
        
        return results

def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="DEI Compliance Collection & Analysis Workflow"
    )
    parser.add_argument(
        '--pdf-dir',
        type=str,
        help='Directory containing PDFs to parse (e.g., research_results/documents/raw/)'
    )
    parser.add_argument(
        '--brave-key',
        type=str,
        help='Brave API key (or set BRAVE_API_KEY env var)'
    )
    
    args = parser.parse_args()
    
    # Set API key if provided
    if args.brave_key:
        os.environ['BRAVE_API_KEY'] = args.brave_key
    
    # Run orchestrator
    orchestrator = CollectionOrchestrator()
    results = orchestrator.run_full_workflow(pdf_dir=args.pdf_dir)
    
    # Save results summary
    results_file = Path("research_results") / f"workflow_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\nResults saved to {results_file}")

if __name__ == "__main__":
    main()
