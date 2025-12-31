#!/usr/bin/env python3
"""
download_manager.py — Download, dedupe, and manage URLs and PDF artifacts.
Stores metadata alongside raw files for tracking and reproducibility.
"""

import os
import json
import hashlib
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DownloadManager:
    """Manage downloads, deduplication, and metadata storage."""
    
    def __init__(self, raw_dir: str = "research_results/documents/raw", 
                 metadata_file: str = "research_results/documents/download_manifest.json"):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = Path(metadata_file)
        self.manifest = self._load_manifest()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Housing Authority Research Agent)'
        })
    
    def _load_manifest(self) -> Dict:
        """Load existing manifest or create new."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        return {"downloads": [], "dedupe_index": {}}
    
    def _save_manifest(self):
        """Save manifest to disk."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.manifest, f, indent=2)
    
    def compute_hash(self, url: str) -> str:
        """Compute hash of URL for deduplication."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def is_downloaded(self, url: str) -> Optional[str]:
        """Check if URL already downloaded; return filepath if yes."""
        url_hash = self.compute_hash(url)
        return self.manifest["dedupe_index"].get(url_hash)
    
    def download_pdf(self, url: str, source: str, timeout: int = 30) -> Optional[str]:
        """
        Download a PDF from URL. Return local filepath or None on failure.
        Store metadata in manifest.
        """
        # Check if already downloaded
        existing = self.is_downloaded(url)
        if existing:
            logger.info(f"Already downloaded: {url} -> {existing}")
            return existing
        
        try:
            logger.info(f"Downloading: {url}")
            resp = self.session.get(url, timeout=timeout, allow_redirects=True)
            resp.raise_for_status()
            
            if resp.headers.get('content-type', '').lower() not in ['application/pdf', 'application/octet-stream']:
                logger.warning(f"Unexpected content-type for {url}: {resp.headers.get('content-type')}")
            
            # Generate safe filename
            filename = hashlib.md5(url.encode()).hexdigest() + ".pdf"
            filepath = self.raw_dir / filename
            
            # Save file
            with open(filepath, 'wb') as f:
                f.write(resp.content)
            
            # Record metadata
            metadata = {
                "url": url,
                "source": source,
                "filepath": str(filepath),
                "download_date": datetime.now().isoformat(),
                "file_size": len(resp.content),
                "content_type": resp.headers.get('content-type', 'unknown')
            }
            self.manifest["downloads"].append(metadata)
            self.manifest["dedupe_index"][self.compute_hash(url)] = str(filepath)
            self._save_manifest()
            
            logger.info(f"Downloaded to: {filepath}")
            return str(filepath)
        
        except Exception as e:
            logger.error(f"Failed to download {url}: {e}")
            return None
    
    def batch_download(self, urls: List[Dict]) -> List[str]:
        """
        Batch download URLs. Each item in urls should be:
        {"url": "...", "source": "..."}
        Returns list of successfully downloaded filepaths.
        """
        filepaths = []
        for item in urls:
            fp = self.download_pdf(item["url"], item["source"])
            if fp:
                filepaths.append(fp)
        return filepaths

if __name__ == "__main__":
    # Example usage
    dm = DownloadManager()
    test_urls = [
        {"url": "https://www.example.com/sample.pdf", "source": "test"}
    ]
    filepaths = dm.batch_download(test_urls)
    print(f"Downloaded: {filepaths}")
