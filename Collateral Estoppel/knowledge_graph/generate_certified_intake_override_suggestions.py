#!/usr/bin/env python3
"""Generate override suggestions from certified-record intake tracker."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OUT = ROOT / 'generated'
TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/45_certified_records_intake_tracker_template_2026-04-07.csv')
FACTS_FLOGIC = OUT / 'case_flogic.flr'
VALID_BUCKETS = {
    'prior_order',
    'docket',
    'hearing',
    'appointment',
    'service',
    'enforcement',
    'other_certified',
}


def _split_fact_ids(raw: str) -> List[str]:
    vals = []
    for p in (raw or '').replace(';', ',').split(','):
        v = p.strip()
        if v:
            vals.append(v)
    return vals


def _truthy(raw: str) -> bool:
    return (raw or '').strip().lower() in {'1', 'true', 'yes', 'y'}


def load_rows() -> List[Dict[str, str]]:
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        rdr = csv.DictReader(fh)
        return [{k: (v or '').strip() for k, v in row.items()} for row in rdr]


def load_known_fact_ids() -> set[str]:
    out: set[str] = set()
    if not FACTS_FLOGIC.exists():
        return out
    txt = FACTS_FLOGIC.read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith('fact('):
            continue
        # fact(fact_id, Predicate(...), ...)
        rest = line[len('fact('):]
        fid = rest.split(',', 1)[0].strip()
        if fid:
            out.add(fid)
    return out


def build(rows: List[Dict[str, str]]) -> Dict[str, object]:
    suggestions = []
    warnings = []
    known_facts = load_known_fact_ids()

    for i, row in enumerate(rows, start=2):  # header is row 1
        fname = row.get('file_name', '')
        path = row.get('absolute_path', '')
        if not fname and not path:
            continue

        bucket = (row.get('bucket', '') or '').strip().lower()
        if bucket and bucket not in VALID_BUCKETS:
            warnings.append({'row': i, 'reason': 'invalid_bucket', 'bucket': bucket, 'file_name': fname})
            continue

        fact_ids = _split_fact_ids(row.get('target_fact_ids', ''))
        if not fact_ids:
            warnings.append({'row': i, 'reason': 'missing_target_fact_ids'})
            continue

        unknown_fact_ids = [fid for fid in fact_ids if known_facts and fid not in known_facts]
        if unknown_fact_ids:
            warnings.append({'row': i, 'reason': 'unknown_target_fact_ids', 'fact_ids': unknown_fact_ids, 'file_name': fname})
            continue

        is_certified = _truthy(row.get('is_certified', ''))
        id_match = _truthy(row.get('party_identity_matched', ''))

        if not is_certified:
            warnings.append({'row': i, 'reason': 'not_marked_certified', 'file_name': fname})
            continue
        if not id_match:
            warnings.append({'row': i, 'reason': 'party_identity_not_marked_matched', 'file_name': fname})
            continue

        rec_status = row.get('recommended_override_status', '').lower() or 'verified'
        rec_value = row.get('recommended_override_value', '').lower() or 'true'
        rec_date = row.get('override_source_date', '') or str(date.today())
        rec_source = path or fname
        rec_source_path = Path(path) if path else None
        if rec_source_path and not rec_source_path.exists():
            warnings.append({'row': i, 'reason': 'source_path_not_found', 'file_name': fname, 'absolute_path': path})
            continue

        for fid in fact_ids:
            suggestions.append(
                {
                    'fact_id': fid,
                    'override_status': rec_status,
                    'override_value': rec_value,
                    'override_source': rec_source,
                    'override_date': rec_date,
                    'note': f"From certified intake tracker row {i}",
                }
            )

    return {
        'generated_at': str(date.today()),
        'tracker_file': str(TRACKER),
        'known_fact_count': len(known_facts),
        'suggestion_count': len(suggestions),
        'warning_count': len(warnings),
        'suggestions': suggestions,
        'warnings': warnings,
    }


def to_markdown(obj: Dict[str, object]) -> str:
    lines = [
        '# Certified Intake Override Suggestions',
        '',
        f"Generated: {obj['generated_at']}",
        f"Tracker: {obj['tracker_file']}",
        f"Known facts: {obj.get('known_fact_count', 0)}",
        f"Suggestions: {obj['suggestion_count']}",
        f"Warnings: {obj['warning_count']}",
        '',
        '## Suggested override rows',
    ]
    for s in obj.get('suggestions', []):
        lines.append(
            f"- {s['fact_id']}: status={s['override_status']} value={s['override_value']} "
            f"source={s['override_source']} date={s['override_date']}"
        )

    if not obj.get('suggestions'):
        lines.append('- none')

    lines.append('')
    lines.append('## Warnings')
    for w in obj.get('warnings', []):
        extra = ''
        if w.get('bucket'):
            extra = f", bucket={w.get('bucket')}"
        if w.get('fact_ids'):
            extra = f", fact_ids={w.get('fact_ids')}"
        if w.get('absolute_path'):
            extra = f", path={w.get('absolute_path')}"
        lines.append(f"- row {w.get('row')}: {w.get('reason')} ({w.get('file_name', 'n/a')}{extra})")
    if not obj.get('warnings'):
        lines.append('- none')
    lines.append('')
    return '\n'.join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = load_rows()
    obj = build(rows)

    json_path = OUT / 'certified_intake_override_suggestions_2026-04-07.json'
    md_path = OUT / 'certified_intake_override_suggestions_2026-04-07.md'

    json_path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
    md_path.write_text(to_markdown(obj), encoding='utf-8')


if __name__ == '__main__':
    main()
