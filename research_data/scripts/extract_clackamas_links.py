#!/usr/bin/env python3
"""
extract_clackamas_links.py - Extract and follow links from Clackamas County Housing Authority pages
"""

import requests
import logging
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import deque

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Key Clackamas County Housing pages to crawl
SEED_URLS = [
    "https://www.clackamas.us/housingauthority",
    "https://www.clackamas.us/housingauthority/plansandreports.html",
    "https://www.clackamas.us/housingauthority/housing-authority-of-clackamas-county-board",
    "https://www.clackamas.us/communitydevelopment/cccha",  # Coordinated Housing Access
]

def extract_pdf_links(html_content, base_url):
    """Extract PDF links and policy document links from HTML."""
    links = []
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.get_text(strip=True)
            
            if not href:
                continue
            
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Filter for PDFs and relevant documents
            if any(x in full_url.lower() for x in ['.pdf', 'dochub', 'docs.clackamas']):
                links.append({
                    'url': full_url,
                    'text': text,
                    'parent': base_url
                })
        
        logger.info(f"Found {len(links)} document links in {base_url[:60]}")
        
    except Exception as e:
        logger.error(f"Error parsing HTML: {e}")
    
    return links

def fetch_page(url, timeout=30):
    """Fetch a page with error handling."""
    try:
        logger.info(f"Fetching: {url[:70]}...")
        resp = requests.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text
    except Exception as e:
        logger.warning(f"Failed to fetch {url}: {e}")
        return None

def main():
    visited = set()
    all_documents = []
    queue = deque(SEED_URLS)
    
    logger.info(f"Starting Clackamas County link extraction from {len(SEED_URLS)} seed URLs\n")
    
    while queue and len(visited) < 50:  # Safety limit
        url = queue.popleft()
        
        if url in visited:
            continue
        
        visited.add(url)
        
        html = fetch_page(url)
        if not html:
            continue
        
        # Extract document links
        doc_links = extract_pdf_links(html, url)
        all_documents.extend(doc_links)
        
        # Extract more pages to crawl
        try:
            soup = BeautifulSoup(html, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link.get('href')
                if href:
                    full_url = urljoin(url, href)
                    
                    # Queue if it's a housing-related page
                    if 'housing' in full_url.lower() or 'clackamas.us' in full_url:
                        if full_url not in visited and full_url not in queue:
                            queue.append(full_url)
        
        except Exception as e:
            logger.error(f"Error extracting links: {e}")
        
        time.sleep(0.5)  # Rate limiting
    
    logger.info(f"\n\nExtraction Complete")
    logger.info(f"Visited pages: {len(visited)}")
    logger.info(f"Documents found: {len(all_documents)}\n")
    
    # Deduplicate and display results
    unique_docs = {}
    for doc in all_documents:
        if doc['url'] not in unique_docs:
            unique_docs[doc['url']] = doc
    
    logger.info("=== CLACKAMAS COUNTY HOUSING DOCUMENTS ===\n")
    
    for i, (url, doc) in enumerate(unique_docs.items(), 1):
        logger.info(f"{i}. {doc['text'][:60]}")
        logger.info(f"   URL: {url}")
        logger.info(f"   Parent: {doc['parent'][:70]}")
        logger.info("-" * 70)
    
    # Save to JSON
    output = {
        "visited_pages": len(visited),
        "documents_found": len(unique_docs),
        "documents": list(unique_docs.values()),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    output_file = "research_results/clackamas_extracted_documents.json"
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)
    
    logger.info(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
