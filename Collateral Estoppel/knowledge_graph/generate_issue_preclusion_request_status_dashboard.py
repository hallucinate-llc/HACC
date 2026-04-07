#!/usr/bin/env python3
"""Generate dashboard for issue-preclusion certified request tracking."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
GEN = ROOT / 'knowledge_graph' / 'generated'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
OUT_JSON = GEN / f'issue_preclusion_request_status_dashboard_{date.today().isoformat()}.json'
OUT_MD = GEN / f'issue_preclusion_request_status_dashboard_{date.today().isoformat()}.md'


FLAG_FIELDS = [
    'certified_records_received',
    'finality_records_complete',
    'opportunity_records_complete',
    'party_identity_records_complete',
    'intake_logged',
    'mapping_updated',
]


def yn(v: str) -> bool:
    return (v or '').strip().lower() in {'y', 'yes', 'true', '1'}


def load_rows() -> list[dict[str, str]]:
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    rows = load_rows()

    case_rows = []
    for r in rows:
        flags = {k: yn(r.get(k, '')) for k in FLAG_FIELDS}
        complete = all(flags.values())
        pending = [k for k, v in flags.items() if not v]
        case_rows.append(
            {
                'case_number': r.get('case_number', ''),
                'request_channel': r.get('request_channel', ''),
                'response_due_date': r.get('response_due_date', ''),
                'response_received_date': r.get('response_received_date', ''),
                'flags': flags,
                'complete': complete,
                'pending_fields': pending,
                'notes': r.get('notes', ''),
            }
        )

    totals = {
        'cases_total': len(case_rows),
        'cases_complete': sum(1 for c in case_rows if c['complete']),
        'cases_incomplete': sum(1 for c in case_rows if not c['complete']),
    }

    pending_by_field = {k: 0 for k in FLAG_FIELDS}
    for c in case_rows:
        for k in c['pending_fields']:
            pending_by_field[k] += 1

    payload = {
        'generated_at': str(date.today()),
        'source_tracker': str(TRACKER),
        'totals': totals,
        'pending_by_field': pending_by_field,
        'cases': case_rows,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines: list[str] = []
    lines.append('# Issue-Preclusion Request Status Dashboard')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    lines.append('## Totals')
    lines.append(f"- cases_total={totals['cases_total']} complete={totals['cases_complete']} incomplete={totals['cases_incomplete']}")
    lines.append('')
    lines.append('## Pending by Field')
    for k, v in pending_by_field.items():
        lines.append(f'- {k}: {v}')
    lines.append('')
    lines.append('## Case Rows')
    for c in case_rows:
        lines.append(f"### {c['case_number']}")
        lines.append(f"- channel: {c['request_channel']}")
        lines.append(f"- due: {c['response_due_date']} received: {c['response_received_date'] or '(none)'}")
        lines.append(f"- complete: {c['complete']}")
        lines.append('- pending:')
        if c['pending_fields']:
            for p in c['pending_fields']:
                lines.append(f'- {p}')
        else:
            lines.append('- (none)')
        if c.get('notes'):
            lines.append(f"- notes: {c['notes']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
