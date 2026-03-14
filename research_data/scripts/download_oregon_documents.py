#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""
Download Oregon state documents from extracted links.
Prioritizes regulatory documents, housing policies, and civil rights guidance.
"""

import os
import json
import time
import requests
import logging
from pathlib import Path
from urllib.parse import urlparse, unquote
from typing import List, Dict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OregonDownloadManager:
    def __init__(self, output_dir: str = "research_results/oregon_documents"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Research Assistant)'
        })
        self.downloaded_files = []
        self.failed_downloads = []
        
    def get_filename_from_url(self, url: str) -> str:
        """Extract a reasonable filename from URL."""
        parsed = urlparse(url)
        filename = unquote(parsed.path.split('/')[-1])
        
        if not filename or len(filename) < 3:
            # Use the last path component before filename
            parts = parsed.path.strip('/').split('/')
            if len(parts) > 1:
                filename = f"{parts[-2]}_{parts[-1]}.pdf"
            else:
                filename = "oregon_document.pdf"
        
        return filename or "document.pdf"
    
    def is_priority_document(self, doc_title: str, doc_url: str) -> tuple:
        """
        Determine priority level and category for a document.
        Returns: (priority_level, category)
        where priority_level: 1=critical, 2=high, 3=medium, 4=low
        """
        title_lower = doc_title.lower()
        url_lower = doc_url.lower()
        
        # CRITICAL: Housing, civil rights, discrimination, fair housing
        critical_keywords = [
            'fair housing', 'civil rights', 'discrimination',
            'affirmative action', 'housing authority', 'public housing',
            'housing policy', 'equal opportunity', 'aar ', 'oars',
            'chapter 813', 'chapter 659', 'bondi'
        ]
        
        # HIGH: Procurement, employment, contracting
        high_keywords = [
            'procurement', 'contracting', 'employment',
            'hiring', 'federal requirements', 'hud',
            'chapter 137', 'das', 'regulation'
        ]
        
        # MEDIUM: Other regulatory documents
        medium_keywords = [
            'policy', 'procedure', 'guideline', 'standard',
            'rule', 'statute', 'oregon', 'department'
        ]
        
        for keyword in critical_keywords:
            if keyword in title_lower or keyword in url_lower:
                return 1, 'Critical Civil Rights'
        
        for keyword in high_keywords:
            if keyword in title_lower or keyword in url_lower:
                return 2, 'Procurement & Rules'
        
        for keyword in medium_keywords:
            if keyword in title_lower or keyword in url_lower:
                return 3, 'Regulatory'
        
        return 4, 'Reference'
    
    def download_file(self, url: str, filename: str, retry: int = 3) -> bool:
        """Download a file with retry logic."""
        filepath = self.output_dir / filename
        
        # Skip if already downloaded
        if filepath.exists():
            logger.info(f"Already downloaded: {filename}")
            return True
        
        # Skip certain file types that are too large or problematic
        if any(x in url.lower() for x in ['youtube', 'video', 'stream']):
            logger.warning(f"Skipping non-document URL: {filename}")
            return False
        
        for attempt in range(retry):
            try:
                logger.info(f"Downloading: {filename} (attempt {attempt + 1}/{retry})")
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                # Check if response is actually a document
                content_type = response.headers.get('content-type', '').lower()
                if 'html' in content_type and '.pdf' in filename:
                    logger.warning(f"URL returned HTML instead of PDF: {filename}")
                    return False
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"✓ Downloaded: {filename} ({len(response.content)} bytes)")
                self.downloaded_files.append({
                    'filename': filename,
                    'url': url,
                    'size': len(response.content)
                })
                return True
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout downloading {filename}, retrying...")
                time.sleep(2 ** attempt)
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    logger.error(f"File not found (404): {filename}")
                    self.failed_downloads.append({
                        'filename': filename,
                        'url': url,
                        'error': 'HTTP 404 Not Found'
                    })
                    return False
                logger.warning(f"HTTP error {response.status_code}, retrying...")
                time.sleep(2 ** attempt)
            except Exception as e:
                logger.error(f"Error downloading {filename}: {e}")
                if attempt == retry - 1:
                    self.failed_downloads.append({
                        'filename': filename,
                        'url': url,
                        'error': str(e)
                    })
                    return False
                time.sleep(2 ** attempt)
        
        return False
    
    def process_documents_from_json(self, json_file: str):
        """Process and download documents from extracted JSON."""
        
        if not os.path.exists(json_file):
            logger.error(f"JSON file not found: {json_file}")
            return
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Create priority lists
        priority_docs = {1: [], 2: [], 3: [], 4: []}
        
        for doc in data.get('documents', []):
            title = doc.get('text', 'Unknown')
            url = doc.get('url', '')
            
            # Skip certain domains
            if any(x in url for x in ['youtube.com', 'twitter.com', 'facebook.com']):
                continue
            
            priority, category = self.is_priority_document(title, url)
            
            priority_docs[priority].append({
                'title': title,
                'url': url,
                'category': category,
                'parent': doc.get('parent', '')
            })
        
        # Download in priority order
        total_to_download = sum(len(docs) for docs in priority_docs.values())
        downloaded = 0
        
        for priority in [1, 2, 3, 4]:
            docs = priority_docs[priority]
            if not docs:
                continue
            
            priority_name = ['Critical', 'High', 'Medium', 'Low'][priority - 1]
            logger.info(f"\n{'='*70}")
            logger.info(f"Priority {priority} ({priority_name}): {len(docs)} documents")
            logger.info('='*70)
            
            for doc in docs:
                if not doc['url'].startswith('http'):
                    logger.warning(f"Skipping invalid URL: {doc['url']}")
                    continue
                
                filename = self.get_filename_from_url(doc['url'])
                # Add priority prefix to filename
                filename = f"P{priority}_{doc['category'].replace(' ', '_')}_{filename}"
                
                success = self.download_file(doc['url'], filename)
                if success:
                    downloaded += 1
                
                # Rate limiting
                time.sleep(0.3)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"DOWNLOAD SUMMARY")
        logger.info('='*70)
        logger.info(f"Total documents found: {total_to_download}")
        logger.info(f"Total downloaded: {downloaded}/{total_to_download}")
        if total_to_download > 0:
            logger.info(f"Success rate: {100*downloaded/total_to_download:.1f}%")
        logger.info(f"Output directory: {self.output_dir}")
        
        if self.failed_downloads:
            logger.warning(f"\nFailed downloads ({len(self.failed_downloads)}):")
            for fail in self.failed_downloads[:10]:
                logger.warning(f"  - {fail['filename']}: {fail['error']}")
            if len(self.failed_downloads) > 10:
                logger.warning(f"  ... and {len(self.failed_downloads) - 10} more")
        
        # Save summary
        summary = {
            'total_found': len(data.get('documents', [])),
            'total_downloaded': len(self.downloaded_files),
            'failed_count': len(self.failed_downloads),
            'downloaded_files': self.downloaded_files,
            'failed_files': self.failed_downloads[:20]
        }
        
        summary_file = self.output_dir / 'download_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nSummary saved to: {summary_file}")

def main():
    logger.info("Oregon Documents Download Manager")
    logger.info("=" * 70)
    
    json_file = "research_results/oregon_extracted_documents.json"
    
    downloader = OregonDownloadManager()
    downloader.process_documents_from_json(json_file)

if __name__ == "__main__":
    main()
