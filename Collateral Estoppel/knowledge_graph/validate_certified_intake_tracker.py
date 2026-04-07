#!/usr/bin/env python3
"""Validate certified-record intake tracker quality and emit a report."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

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

REQ = ['file_name', 'absolute_path', 'bucket', 'case_number', 'target_fact_ids']


def truthy(raw: str) -> bool:
    return (raw or '').strip().lower() in {'1', 'true', 'yes', 'y'}


def split_fact_ids(raw: str) -> list[str]:
    vals = []
    for p in (raw or '').replace(';', ',').split(','):
        v = p.strip()
        if v:
            vals.append(v)
    return vals


def load_known_fact_ids() -> set[str]:
    out: set[str] = set()
    if not FACTS_FLOGIC.exists():
        return out
    txt = FACTS_FLOGIC.read_text(encoding='utf-8', errors='ignore')
    for line in txt.splitlines():
        line = line.strip()
        if not line.startswith('fact('):
            continue
        fid = line[len('fact('):].split(',', 1)[0].strip()
        if fid:
            out.add(fid)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    known_facts = load_known_fact_ids()

    if not TRACKER.exists():
        raise SystemExit(f'Tracker not found: {TRACKER}')

    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        rows = [{k: (v or '').strip() for k, v in row.items()} for row in csv.DictReader(fh)]

    findings = []
    summary = {
        'rows_total': 0,
        'rows_nonempty': 0,
        'rows_marked_certified': 0,
        'rows_identity_matched': 0,
        'rows_candidate_promotable': 0,
    }

    for i, row in enumerate(rows, start=2):
        summary['rows_total'] += 1
        if not any((row.get(c, '') or '').strip() for c in row.keys()):
            continue
        summary['rows_nonempty'] += 1

        row_findings = []
        for c in REQ:
            if not row.get(c):
                row_findings.append({'severity': 'error', 'reason': f'missing_required_field:{c}'})

        bucket = (row.get('bucket', '') or '').lower()
        if bucket and bucket not in VALID_BUCKETS:
            row_findings.append({'severity': 'error', 'reason': f'invalid_bucket:{bucket}'})

        fact_ids = split_fact_ids(row.get('target_fact_ids', ''))
        if not fact_ids:
            row_findings.append({'severity': 'error', 'reason': 'missing_target_fact_ids'})
        else:
            unknown = [fid for fid in fact_ids if known_facts and fid not in known_facts]
            if unknown:
                row_findings.append({'severity': 'error', 'reason': f'unknown_target_fact_ids:{unknown}'})

        abs_path = row.get('absolute_path', '')
        if abs_path and not Path(abs_path).exists():
            row_findings.append({'severity': 'warn', 'reason': 'source_path_not_found'})

        is_cert = truthy(row.get('is_certified', ''))
        id_match = truthy(row.get('party_identity_matched', ''))
        if is_cert:
            summary['rows_marked_certified'] += 1
        if id_match:
            summary['rows_identity_matched'] += 1

        promotable = bool(is_cert and id_match and not any(f['severity'] == 'error' for f in row_findings))
        if promotable:
            summary['rows_candidate_promotable'] += 1

        if row_findings:
            findings.append(
                {
                    'row': i,
                    'file_name': row.get('file_name', ''),
                    'case_number': row.get('case_number', ''),
                    'is_certified': is_cert,
                    'party_identity_matched': id_match,
                    'issues': row_findings,
                }
            )

    report = {
        'generated_at': str(date.today()),
        'tracker_file': str(TRACKER),
        'known_fact_count': len(known_facts),
        'summary': summary,
        'finding_count': len(findings),
        'findings': findings,
    }

    j = OUT / 'certified_intake_tracker_validation_2026-04-07.json'
    m = OUT / 'certified_intake_tracker_validation_2026-04-07.md'
    j.write_text(json.dumps(report, indent=2), encoding='utf-8')

    lines = [
        '# Certified Intake Tracker Validation',
        '',
        f"Generated: {report['generated_at']}",
        f"Tracker: {report['tracker_file']}",
        f"Known facts: {report['known_fact_count']}",
        '',
        '## Summary',
    ]
    for k, v in report['summary'].items():
        lines.append(f"- {k}: {v}")
    lines.append('')
    lines.append('## Findings')
    if not findings:
        lines.append('- none')
    else:
        for f in findings:
            lines.append(f"- row {f['row']} ({f['file_name']}):")
            for iss in f['issues']:
                lines.append(f"- {iss['severity']}: {iss['reason']}")
            lines.append('')

    m.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
