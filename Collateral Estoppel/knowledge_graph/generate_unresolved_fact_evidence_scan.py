#!/usr/bin/env python3
"""Scan repository for candidate evidence tied to strict unresolved facts."""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
KG = ROOT / 'knowledge_graph' / 'generated'
REPORT = KG / 'deontic_reasoning_report.json'
OUT_JSON = KG / f'unresolved_fact_evidence_scan_{date.today().isoformat()}.json'
OUT_MD = KG / f'unresolved_fact_evidence_scan_{date.today().isoformat()}.md'

MAX_HITS_PER_FACT = 25
MAX_FILE_BYTES = 1_500_000

FACT_PATTERNS: Dict[str, List[str]] = {
    'f_client_prior_appointment': [
        r'prior appointment', r'appointed guardian', r'guardian appointed', r'letters of guardianship',
        r'guardianship order', r'prior guardian', r'appointment order'
    ],
    'f_client_solomon_housing_interference': [
        r'solomon', r'interfer', r'housing contract', r'lease', r'household composition', r'hacc'
    ],
    'f_client_solomon_order_disregard': [
        r'solomon', r'disregard', r'order (?:wasn.t|not) enforceable', r'avoid(?:ed)? service',
        r'service', r'noncompliance'
    ],
    'f_client_solomon_failed_appearance': [
        r'solomon', r'failed to appear', r'failure to appear', r'nonappearance', r'order to appear', r'show cause'
    ],
    'f_collateral_estoppel_candidate': [
        r'collateral estoppel', r'issue preclusion', r'identical issue', r'prior separate proceeding',
        r'full and fair', r'privity', r'final(?:ity| order| judgment)'
    ],
    'f_client_solomon_barred_refile': [
        r'solomon', r'refile', r'barred claim', r'precluded claim', r'collateral estoppel', r'issue preclusion'
    ],
}

TEXT_EXTS = {'.md', '.txt', '.json', '.csv', '.eml'}
SKIP_DIRS = {'.git', '__pycache__', 'node_modules'}
SKIP_PATH_FRAGMENTS = {
    '/knowledge_graph/generated/',
}


def load_report() -> Dict[str, object]:
    return json.loads(REPORT.read_text(encoding='utf-8'))


def unresolved_fact_ids(report: Dict[str, object]) -> List[str]:
    out = set()
    rows = report.get('modes', {}).get('strict', {}).get('unresolved_rules', [])
    for r in rows:
        for a in r.get('antecedents', []):
            fid = str(a.get('fact_id', '')).strip()
            status = str(a.get('status', '')).strip().lower()
            value = str(a.get('value', '')).strip().lower()
            if fid and (status != 'verified' or value != 'true'):
                out.add(fid)
    return sorted(out)


def iter_text_files() -> List[Path]:
    files: List[Path] = []
    for p in ROOT.rglob('*'):
        if not p.is_file():
            continue
        if any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix.lower() not in TEXT_EXTS:
            continue
        pstr = str(p)
        if any(fragment in pstr for fragment in SKIP_PATH_FRAGMENTS):
            continue
        try:
            if p.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        files.append(p)
    return files


def score_hit(text: str, patterns: List[str]) -> int:
    s = 0
    for pat in patterns:
        if re.search(pat, text, flags=re.IGNORECASE):
            s += 1
    return s


def find_line_snippet(content: str, patterns: List[str]) -> Tuple[int, str]:
    lines = content.splitlines()
    for i, line in enumerate(lines, start=1):
        for pat in patterns:
            if re.search(pat, line, flags=re.IGNORECASE):
                return i, line.strip()
    return 1, (lines[0].strip() if lines else '')


def scan_fact(fid: str, files: List[Path]) -> List[Dict[str, object]]:
    pats = FACT_PATTERNS.get(fid, [re.escape(fid.replace('f_', '').replace('_', ' '))])
    hits: List[Dict[str, object]] = []

    for p in files:
        try:
            txt = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        low = txt.lower()
        s = score_hit(low, pats)
        if s <= 0:
            continue
        lineno, snippet = find_line_snippet(txt, pats)
        rel = p.relative_to(ROOT)
        hits.append({
            'path': str(rel),
            'score': s,
            'line': lineno,
            'snippet': snippet[:240],
        })

    hits.sort(key=lambda x: (-int(x['score']), str(x['path'])))
    return hits[:MAX_HITS_PER_FACT]


def main() -> None:
    report = load_report()
    unresolved = unresolved_fact_ids(report)
    files = iter_text_files()

    by_fact: Dict[str, List[Dict[str, object]]] = {}
    for fid in unresolved:
        by_fact[fid] = scan_fact(fid, files)

    payload = {
        'generated_at': str(date.today()),
        'source_report': str(REPORT),
        'unresolved_fact_ids': unresolved,
        'max_hits_per_fact': MAX_HITS_PER_FACT,
        'results': by_fact,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Unresolved Fact Evidence Scan')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    lines.append(f'- Unresolved non-verified/false fact count: {len(unresolved)}')
    lines.append(f'- Max hits per fact: {MAX_HITS_PER_FACT}')
    lines.append('')

    for fid in unresolved:
        hits = by_fact.get(fid, [])
        lines.append(f'## {fid}')
        lines.append(f'- Candidate hits: {len(hits)}')
        if not hits:
            lines.append('- (none)')
            lines.append('')
            continue
        for h in hits:
            lines.append(f"- {h['path']}:{h['line']} (score={h['score']})")
            if h.get('snippet'):
                lines.append(f"- snippet: {h['snippet']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
