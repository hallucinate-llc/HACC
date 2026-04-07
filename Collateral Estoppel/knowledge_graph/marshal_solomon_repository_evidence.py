#!/usr/bin/env python3
"""Marshal Solomon-related evidence mentions across the repository.

Outputs:
- evidence_notes/solomon_repository_evidence_index.json
- evidence_notes/solomon_repository_evidence_index.md

This index is designed as a bridge artifact for the formal reasoning generator.
"""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Dict, List, Tuple

ROOT = Path('/home/barberb/HACC')
SCAN_ROOTS = [
    Path('/home/barberb/HACC/Collateral Estoppel'),
    Path('/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04'),
    Path('/home/barberb/HACC/evidence/email_imports'),
    Path('/home/barberb/HACC/workspace/imap-confirmed-messages'),
    Path('/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31'),
]
OUT_JSON = Path('/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.json')
OUT_MD = Path('/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.md')

TEXT_EXTS = {'.md', '.txt', '.json', '.eml'}
SKIP_PARTS = {
    '.git',
    '__pycache__',
    '.venv',
    'venv',
    'node_modules',
    '.mypy_cache',
    '.pytest_cache',
    'dist',
    'build',
}

KEYWORDS = [
    'solomon',
    'solomon barber',
    'restraining order',
    'guardianship',
    '26pr00641',
    '25po11318',
    'eppdapa',
    'jane cortez',
    'benjamin barber',
]

DATE_PATTERNS = [
    re.compile(r'\b\d{4}-\d{2}-\d{2}\b'),
    re.compile(r'\b\d{1,2}/\d{1,2}/\d{4}\b'),
    re.compile(r'\b\d{1,2}-\d{1,2}-\d{4}\b'),
]
MAX_FILE_BYTES = 1_500_000


def should_skip(path: Path) -> bool:
    return any(part in SKIP_PARTS for part in path.parts)


def score_line(line: str) -> Tuple[int, List[str]]:
    ll = line.lower()
    matched = [k for k in KEYWORDS if k in ll]
    score = len(matched)
    return score, matched


def extract_dates(text: str) -> List[str]:
    out = set()
    for pat in DATE_PATTERNS:
        for m in pat.findall(text):
            out.add(m)
    return sorted(out)


def gather() -> Dict[str, object]:
    files_scanned = 0
    hits: List[Dict[str, object]] = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for p in scan_root.rglob('*'):
            if not p.is_file():
                continue
            if should_skip(p):
                continue
            if p.suffix.lower() not in TEXT_EXTS:
                continue
            try:
                if p.stat().st_size > MAX_FILE_BYTES:
                    continue
            except OSError:
                continue

            files_scanned += 1
            try:
                text = p.read_text(encoding='utf-8', errors='ignore')
            except OSError:
                continue

            lines = text.splitlines()
            line_hits = []
            total_score = 0

            for i, line in enumerate(lines, start=1):
                score, matched = score_line(line)
                if score <= 0:
                    continue
                total_score += score
                line_hits.append(
                    {
                        'line': i,
                        'score': score,
                        'matched_keywords': matched,
                        'snippet': line.strip()[:260],
                    }
                )

            if not line_hits:
                continue

            # Keep only top snippets to stay compact.
            line_hits.sort(key=lambda x: (x['score'], x['line']), reverse=True)
            top = line_hits[:8]

            max_score = max(h['score'] for h in line_hits)
            if max_score >= 4 or total_score >= 18:
                relevance = 'high'
            elif max_score >= 2 or total_score >= 8:
                relevance = 'medium'
            else:
                relevance = 'low'

            hits.append(
                {
                    'path': str(p),
                    'relative_path': str(p.relative_to(ROOT)),
                    'relevance': relevance,
                    'total_keyword_score': total_score,
                    'hit_count': len(line_hits),
                    'dates_found': extract_dates(text),
                    'top_snippets': top,
                }
            )

    hits.sort(key=lambda h: (h['relevance'] != 'high', h['relevance'] != 'medium', -h['total_keyword_score'], h['relative_path']))

    return {
        'generated_at': datetime.now(timezone.utc).isoformat(),
        'root': str(ROOT),
        'files_scanned': files_scanned,
        'hits': hits,
        'summary': {
            'hit_files': len(hits),
            'high_relevance': sum(1 for h in hits if h['relevance'] == 'high'),
            'medium_relevance': sum(1 for h in hits if h['relevance'] == 'medium'),
            'low_relevance': sum(1 for h in hits if h['relevance'] == 'low'),
        },
    }


def to_md(data: Dict[str, object]) -> str:
    lines = [
        '# Solomon Repository Evidence Index',
        '',
        f"Generated: {data['generated_at']}",
        f"Files scanned: {data['files_scanned']}",
        f"Hit files: {data['summary']['hit_files']}",
        f"High relevance: {data['summary']['high_relevance']}",
        f"Medium relevance: {data['summary']['medium_relevance']}",
        f"Low relevance: {data['summary']['low_relevance']}",
        '',
    ]

    for hit in data['hits']:
        lines.append(f"## {hit['relative_path']}")
        lines.append(f"- Relevance: {hit['relevance']}")
        lines.append(f"- Total keyword score: {hit['total_keyword_score']}")
        lines.append(f"- Hit count: {hit['hit_count']}")
        lines.append(f"- Dates found: {hit['dates_found']}")
        lines.append('- Top snippets:')
        for sn in hit['top_snippets']:
            lines.append(
                f"- line {sn['line']} (score={sn['score']}, keywords={sn['matched_keywords']}): {sn['snippet']}"
            )
        lines.append('')

    return '\n'.join(lines) + '\n'


def main() -> None:
    data = gather()
    OUT_JSON.write_text(json.dumps(data, indent=2), encoding='utf-8')
    OUT_MD.write_text(to_md(data), encoding='utf-8')


if __name__ == '__main__':
    main()
