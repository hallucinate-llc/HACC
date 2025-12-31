#!/usr/bin/env python3
"""
index_and_tag.py — Build index of parsed documents and tag with keywords/applicability.
Produces a searchable JSON index and CSV summary.
"""

import json
import csv
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentIndexer:
    """Index and tag parsed documents."""
    
    # Keyword groups (from agent.md)
    DEI_KEYWORDS = [
        'diversity', 'equity', 'inclusion', 'dei', 'deia', 'deib', 'deij', 'racial justice',
        'social justice', 'accessibility', 'inclusive', 'marginalized', 'minority',
        'bipoc', 'people of color', 'underrepresented groups', 
        'underrepresented', 'underserved', 'underserviced', 'equitable', 'justice-centered',
        'justice oriented', 'anti-racist', 'anti discrimination', 'cultural humility',
        'cultural responsiveness', 'equity lens', 'equity framework', 'equity initiatives',
    ]
    
    PROXY_KEYWORDS = [
        'cultural competence', 'lived experience', 'diversity statement',
        'safe space', 'bipoc', 'minority-only', 'first-generation',
        'low-income targeting', 'equity plan', 'overcoming obstacles', 'equity lens',
        'inclusive environment', 'barrier reduction', 'equity framework', 'equity initiatives'
    ]
    
    BINDING_KEYWORDS = [
        'policy', 'ordinance', 'statewide', 'model policy', 'contract',
        'agreement', 'standard', 'required', 'must', 'shall', 'mandatory',
        'applicable to', 'applicability', 'enforceable', 'governing', 'binding',
        'regulation', 'rule', 'directive', 'compliance', 'obligated', 'stipulation'
    ]
    
    APPLICABILITY_KEYWORDS = {
        'hiring': ['hiring', 'recruit', 'employ', 'appointment', 'position', 'candidate', 'job'],
        'procurement': ['procurement', 'contract', 'vendor', 'supplier', 'bid', 'rfp', 'award', 'purchase'],
        'training': ['training', 'workshop', 'course', 'curriculum', 'education', 'seminar'],
        'housing': ['housing', 'lease', 'tenant', 'resident', 'affordable', 'public housing', 'section 8'],
        'community engagement': ['community engagement', 'public input', 'stakeholder', 'outreach', 'consultation'],
    }
    
    def __init__(
        self,
        parsed_dir: str = "research_results/documents/parsed",
        output_dir: str = "research_results/",
        exclude_source_substrings: List[str] | None = None,
    ):
        self.parsed_dir = Path(parsed_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.index = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.exclude_source_substrings = [s.lower() for s in (exclude_source_substrings or [])]
    
    def _extract_keywords(self, text: str, keyword_list: List[str]) -> List[str]:
        """Extract keywords from text (case-insensitive)."""
        found = []
        text_lower = text.lower()
        for kw in keyword_list:
            if kw.lower() in text_lower:
                found.append(kw)
        return list(set(found))  # dedupe
    
    def _tag_applicability(self, text: str) -> List[str]:
        """Tag document with applicability areas."""
        tags = []
        text_lower = text.lower()
        for area, keywords in self.APPLICABILITY_KEYWORDS.items():
            for kw in keywords:
                if kw.lower() in text_lower:
                    if area not in tags:
                        tags.append(area)
                    break
        return tags
    
    def _calculate_risk_score(self, dei_count: int, proxy_count: int, binding_count: int) -> int:
        """Simple risk scoring: 0-3 based on keyword presence."""
        if dei_count > 0 and binding_count > 0 and proxy_count > 0:
            return 3  # Clear issue
        elif (dei_count > 0 or proxy_count > 0) and binding_count > 0:
            return 2  # Probable issue
        elif dei_count > 0 or proxy_count > 0:
            return 1  # Possible issue
        return 0  # Compliant/no evidence
    
    def index_document(self, text_path: str, metadata: Dict = None) -> Dict:
        """Index a single parsed document."""
        text_path = Path(text_path)
        if not text_path.exists():
            logger.error(f"File not found: {text_path}")
            return None
        
        with open(text_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        
        # Extract keywords
        dei_keywords = self._extract_keywords(text, self.DEI_KEYWORDS)
        proxy_keywords = self._extract_keywords(text, self.PROXY_KEYWORDS)
        binding_keywords = self._extract_keywords(text, self.BINDING_KEYWORDS)
        
        # Tag applicability
        applicability = self._tag_applicability(text)
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            len(dei_keywords), len(proxy_keywords), len(binding_keywords)
        )
        
        # Build index entry
        entry = {
            "id": text_path.stem,
            "file_path": str(text_path),
            "metadata": metadata or {},
            "dei_keywords": dei_keywords,
            "proxy_keywords": proxy_keywords,
            "binding_keywords": binding_keywords,
            "applicability_tags": applicability,
            "risk_score": risk_score,
            "text_length": len(text),
            "indexed_date": datetime.now().isoformat()
        }
        
        self.index.append(entry)
        logger.info(f"Indexed: {text_path.name} (risk_score={risk_score})")
        return entry
    
    def batch_index(self, parsed_dir: str = None) -> List[Dict]:
        """Index all documents in parsed directory."""
        dir_path = Path(parsed_dir or self.parsed_dir)
        txt_files = list(dir_path.glob("*.txt"))
        logger.info(f"Found {len(txt_files)} text files to index")
        
        for txt_file in txt_files:
            # Try to load metadata JSON
            meta_file = txt_file.with_suffix('.json')
            metadata = None
            if meta_file.exists():
                with open(meta_file, 'r') as f:
                    metadata = json.load(f)

            if metadata and self.exclude_source_substrings:
                src = str(metadata.get('source', '')).lower()
                if any(s in src for s in self.exclude_source_substrings):
                    continue
            
            self.index_document(str(txt_file), metadata)
        
        return self.index
    
    def save_index(self):
        """Save index as JSON."""
        index_file = self.output_dir / f"document_index_{self.timestamp}.json"
        with open(index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
        logger.info(f"Saved index to {index_file}")
        return str(index_file)
    
    def export_csv_summary(self):
        """Export CSV summary for quick review."""
        csv_file = self.output_dir / f"summary_{self.timestamp}.csv"
        
        with open(csv_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'document_id', 'file_path', 'risk_score', 'dei_keywords', 'proxy_keywords',
                'binding_keywords', 'applicability_tags', 'text_length'
            ])
            
            for entry in sorted(self.index, key=lambda x: x['risk_score'], reverse=True):
                writer.writerow([
                    entry['id'],
                    entry['file_path'],
                    entry['risk_score'],
                    '; '.join(entry['dei_keywords']),
                    '; '.join(entry['proxy_keywords']),
                    '; '.join(entry['binding_keywords']),
                    '; '.join(entry['applicability_tags']),
                    entry['text_length']
                ])
        
        logger.info(f"Saved CSV summary to {csv_file}")
        return str(csv_file)

if __name__ == "__main__":
    indexer = DocumentIndexer()
    indexer.batch_index()
    indexer.save_index()
    indexer.export_csv_summary()
    logger.info(f"Indexed {len(indexer.index)} documents")
