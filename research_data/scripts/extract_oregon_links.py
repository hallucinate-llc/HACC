#!/usr/bin/env python3
"""
Extract hyperlinks from Oregon state HTML documents.
Focuses on policy documents, regulatory guidance, and housing-related PDFs.
"""

import os
import json
import time
import logging
from pathlib import Path
from urllib.parse import urljoin, urlparse
from collections import deque
from bs4 import BeautifulSoup

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OregonLinkExtractor:
    def __init__(self, html_dir: str = "research_data/raw_documents"):
        self.html_dir = Path(html_dir)
        self.visited_docs = set()
        self.documents_found = {}
        self.base_urls = {
            'boli': 'https://www.oregon.gov/boli/',
            'das': 'https://das.oregon.gov/',
            'das_proc': 'https://das.oregon.gov/procurement/',
            'hud': 'https://www.hud.gov/',
            'oregon_laws': 'https://oregon.gov/',
            'housing': 'https://www.oregon.gov/housing/',
        }
        
    def infer_base_url(self, filename: str) -> str:
        """Infer the base URL for a document based on filename."""
        filename_lower = filename.lower()
        
        if 'boli' in filename_lower:
            return self.base_urls['boli']
        elif 'das' in filename_lower:
            if 'procurement' in filename_lower:
                return self.base_urls['das_proc']
            return self.base_urls['das']
        elif 'hud' in filename_lower:
            return self.base_urls['hud']
        elif 'housing' in filename_lower or 'hcs' in filename_lower:
            return self.base_urls['housing']
        else:
            return self.base_urls['oregon_laws']
    
    def is_relevant_link(self, href: str) -> bool:
        """Check if a link is relevant (PDF, policy, regulation, etc.)."""
        href_lower = href.lower()
        
        relevant_extensions = ['.pdf', '.docx', '.doc', '.xlsx', '.txt']
        relevant_keywords = [
            'policy', 'procedure', 'regulation', 'rule', 'statute',
            'guideline', 'standard', 'requirement', 'housing',
            'discrimination', 'civil rights', 'equal opportunity',
            'affirmative action', 'diversity', 'equity',
            'fair housing', 'accommodation', 'aar', 'oas'
        ]
        
        # Check extension
        if any(ext in href_lower for ext in relevant_extensions):
            return True
        
        # Check keywords
        if any(kw in href_lower for kw in relevant_keywords):
            return True
        
        return False
    
    def extract_links_from_html(self, html_content: str, source_url: str) -> list:
        """Extract links from HTML content."""
        links = []
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').strip()
                if not href or href.startswith('javascript:') or href.startswith('#'):
                    continue
                
                # Convert relative URLs to absolute
                full_url = urljoin(source_url, href)
                
                # Check if relevant
                if self.is_relevant_link(full_url):
                    link_text = link.get_text(strip=True)[:100]
                    links.append({
                        'url': full_url,
                        'text': link_text,
                        'source': 'extracted_link'
                    })
        except Exception as e:
            logger.warning(f"Error parsing HTML: {e}")
        
        return links
    
    def process_html_files(self):
        """Process all HTML files in raw_documents directory."""
        html_files = list(self.html_dir.glob('*.html'))
        logger.info(f"Found {len(html_files)} HTML files to process")
        
        for html_file in html_files:
            filename = html_file.name
            if filename in self.visited_docs:
                continue
            
            self.visited_docs.add(filename)
            logger.info(f"\nProcessing: {filename}")
            
            try:
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                # Infer base URL for proper URL resolution
                base_url = self.infer_base_url(filename)
                
                # Extract links
                links = self.extract_links_from_html(html_content, base_url)
                
                if links:
                    logger.info(f"  Found {len(links)} relevant links")
                    for link in links:
                        url = link['url']
                        if url not in self.documents_found:
                            self.documents_found[url] = {
                                'url': url,
                                'text': link['text'],
                                'parent': filename,
                                'source': 'oregon_documents'
                            }
                else:
                    logger.info(f"  No relevant links found")
                    
            except Exception as e:
                logger.error(f"Error processing {filename}: {e}")
        
        logger.info(f"\n{'='*70}")
        logger.info(f"Extraction Complete")
        logger.info(f"{'='*70}")
        logger.info(f"HTML documents processed: {len(self.visited_docs)}")
        logger.info(f"Unique document links found: {len(self.documents_found)}")
        
        # Save results
        output_file = Path("research_results") / "oregon_extracted_documents.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        results = {
            'documents_processed': len(self.visited_docs),
            'documents_found': len(self.documents_found),
            'documents': list(self.documents_found.values())
        }
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Results saved to: {output_file}")
        
        # Show summary by type
        logger.info(f"\n{'='*70}")
        logger.info("DOCUMENTS BY TYPE")
        logger.info(f"{'='*70}")
        
        type_counts = {}
        for doc_url in self.documents_found.keys():
            doc_type = 'PDF' if '.pdf' in doc_url.lower() else 'Other'
            type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
        
        for doc_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            logger.info(f"{doc_type}: {count} documents")
        
        # Show sample documents
        logger.info(f"\n{'='*70}")
        logger.info("SAMPLE EXTRACTED DOCUMENTS")
        logger.info(f"{'='*70}")
        
        for i, doc in enumerate(list(self.documents_found.values())[:10], 1):
            logger.info(f"\n{i}. {doc['text'][:60]}")
            logger.info(f"   URL: {doc['url'][:80]}...")
            logger.info(f"   Parent: {doc['parent']}")

def main():
    logger.info("Oregon State Documents Link Extractor")
    logger.info("=" * 70)
    
    extractor = OregonLinkExtractor()
    extractor.process_html_files()

if __name__ == "__main__":
    main()
