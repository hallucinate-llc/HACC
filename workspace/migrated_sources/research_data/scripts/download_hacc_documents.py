#!/usr/bin/env python3
# DEPRECATED: historical corpus-bootstrapping helper; prefer shared HACC/complaint-generator workflows.
"""
Download Housing Authority of Clackamas County (HACC) documents from discovered links.
Prioritizes Annual Plans, Audited Financials, Board Minutes, and policy documents.
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

class HADownloadManager:
    def __init__(self, output_dir: str = "research_results/hacc_documents"):
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
        
        if not filename or filename.startswith('drupal'):
            # For dochub URLs, use the ID as filename
            doc_id = parsed.path.split('/')[-1]
            return f"hacc_doc_{doc_id}.pdf"
        
        return filename or "document.pdf"
    
    def is_priority_document(self, doc_title: str) -> tuple:
        """
        Determine priority level and category for a document.
        Returns: (priority_level, category)
        where priority_level: 1=critical, 2=high, 3=medium, 4=low
        """
        title_lower = doc_title.lower()
        
        # CRITICAL: Current policies and plans
        critical_keywords = [
            'annual plan fy 2025', 'annual plan fy 2024', 'five year plan',
            'admissions', 'lease', 'procurement', 'equal opportunity',
            'fair housing', 'non-discrimination', 'diversity', 'equity'
        ]
        
        # HIGH: Recent audits and governance
        high_keywords = [
            'audited financial 202[34]', '2024 audit', '2023 audit',
            'board minutes', 'board rule', 'board meeting',
            'annual plan fy 202[23]'
        ]
        
        # MEDIUM: Background and history
        medium_keywords = [
            'audited financial', 'annual plan', 'strategic plan',
            'policy', 'procedure', 'guideline', 'homeless', 'affordable'
        ]
        
        for keyword in critical_keywords:
            if keyword in title_lower:
                return 1, 'Critical Policy'
        
        for keyword in high_keywords:
            if keyword in title_lower:
                return 2, 'Governance & Audit'
        
        for keyword in medium_keywords:
            if keyword in title_lower:
                return 3, 'Plans & Background'
        
        return 4, 'Reference'
    
    def download_file(self, url: str, filename: str, retry: int = 3) -> bool:
        """Download a file with retry logic."""
        filepath = self.output_dir / filename
        
        # Skip if already downloaded
        if filepath.exists():
            logger.info(f"Already downloaded: {filename}")
            return True
        
        for attempt in range(retry):
            try:
                logger.info(f"Downloading: {filename} (attempt {attempt + 1}/{retry})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
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
                time.sleep(2 ** attempt)  # Exponential backoff
            except requests.exceptions.HTTPError as e:
                if response.status_code == 404:
                    logger.error(f"File not found: {filename}")
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
        
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Create priority lists
        priority_docs = {1: [], 2: [], 3: [], 4: []}
        
        for doc in data['documents']:
            title = doc.get('text', 'Unknown')
            url = doc.get('url', '')
            priority, category = self.is_priority_document(title)
            
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
                
                # Skip non-dochub URLs for now (focus on primary repository)
                if 'dochub.clackamas.us' not in doc['url']:
                    if priority < 3:  # Still get critical/high priority external files
                        pass
                    else:
                        continue
                
                filename = self.get_filename_from_url(doc['url'])
                # Add priority prefix to filename
                filename = f"P{priority}_{doc['category'].replace(' ', '_')}_{filename}"
                
                success = self.download_file(doc['url'], filename)
                if success:
                    downloaded += 1
                
                # Rate limiting
                time.sleep(0.5)
        
        logger.info(f"\n{'='*70}")
        logger.info(f"DOWNLOAD SUMMARY")
        logger.info('='*70)
        logger.info(f"Total downloaded: {downloaded}/{total_to_download}")
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
            'total_found': len(data['documents']),
            'total_downloaded': len(self.downloaded_files),
            'failed_count': len(self.failed_downloads),
            'downloaded_files': self.downloaded_files,
            'failed_files': self.failed_downloads[:20]  # Keep first 20
        }
        
        summary_file = self.output_dir / 'download_summary.json'
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"\nSummary saved to: {summary_file}")

def main():
    logger.info("HACC Document Download Manager")
    logger.info("=" * 70)
    
    json_file = "research_results/clackamas_extracted_documents.json"
    
    if not os.path.exists(json_file):
        logger.error(f"JSON file not found: {json_file}")
        return
    
    downloader = HADownloadManager()
    downloader.process_documents_from_json(json_file)

if __name__ == "__main__":
    main()
