#!/usr/bin/env python3
"""
collect_brave.py — Collect search results from Brave Search API.
Requires BRAVE_API_KEY environment variable.
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BraveCollector:
    """Collect search results from Brave Search API."""
    
    def __init__(self, api_key: str = None, output_dir: str = "research_results/"):
        self.api_key = api_key or os.getenv('BRAVE_API_KEY')
        if not self.api_key:
            logger.warning("BRAVE_API_KEY not set. Brave searches will fail.")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_file = self.output_dir / f"brave_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self.results = []
    
    def search(self, query: str, count: int = 20) -> List[Dict]:
        """Execute a Brave search query. Return list of results."""
        if not self.api_key:
            logger.error("Brave API key not configured.")
            return []
        
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.api_key
        }
        params = {
            "q": query,
            "count": count
        }
        
        try:
            logger.info(f"Searching Brave: {query}")
            resp = requests.get(url, headers=headers, params=params, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract web results
            results = data.get("web", {}).get("results", [])
            logger.info(f"Got {len(results)} results from Brave")
            
            # Store results with metadata
            for result in results:
                self.results.append({
                    "query": query,
                    "title": result.get("title"),
                    "url": result.get("url"),
                    "description": result.get("description"),
                    "timestamp": datetime.now().isoformat(),
                    "source": "brave"
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Brave search failed: {e}")
            return []
    
    def batch_search(self, queries: List[str]) -> Dict[str, List[Dict]]:
        """Execute multiple searches. Return dict of query -> results."""
        all_results = {}
        for query in queries:
            results = self.search(query)
            all_results[query] = results
        return all_results
    
    def save_results(self):
        """Save all collected results to JSON."""
        with open(self.results_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        logger.info(f"Saved {len(self.results)} results to {self.results_file}")

if __name__ == "__main__":
    collector = BraveCollector()
    
    queries = [
        'site:oregon.gov "diversity" OR "equity" OR "DEI" filetype:pdf',
        'site:oregon.gov "underrepresented" OR "underserved" filetype:pdf',
        'site:clackamas.us "diversity" OR "equity" filetype:pdf'
    ]
    
    collector.batch_search(queries)
    collector.save_results()
    logger.info(f"Results saved to {collector.results_file}")
