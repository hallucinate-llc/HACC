#!/usr/bin/env python3
"""Generate urgency-ranked next actions from issue-preclusion request tracker."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv')
GEN = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
OUT_JSON = GEN / f'issue_preclusion_request_next_actions_{date.today().isoformat()}.json'
OUT_MD = GEN / f'issue_preclusion_request_next_actions_{date.today().isoformat()}.md'

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


def parse_iso(d: str):
    try:
        return date.fromisoformat((d or '').strip())
    except Exception:
        return None


def load_rows():
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def compute_priority(row):
    today = date.today()
    due = parse_iso(row.get('response_due_date', ''))
    recv = parse_iso(row.get('response_received_date', ''))
    channel = (row.get('request_channel') or '').strip().lower()

    flags = {k: yn(row.get(k, '')) for k in FLAG_FIELDS}
    pending = [k for k, v in flags.items() if not v]

    if channel in {'to_submit', ''}:
        stage = 'submit_request'
    elif not flags['certified_records_received']:
        stage = 'await_response'
    elif not flags['intake_logged']:
        stage = 'log_intake'
    elif not flags['mapping_updated']:
        stage = 'update_mapping'
    elif pending:
        stage = 'complete_remaining'
    else:
        stage = 'complete'

    urgency = 'normal'
    days_to_due = None
    if due:
        days_to_due = (due - today).days
        if days_to_due < 0:
            urgency = 'overdue'
        elif days_to_due <= 2:
            urgency = 'high'
        elif days_to_due <= 7:
            urgency = 'medium'

    if stage == 'submit_request':
        urgency = 'high' if urgency == 'normal' else urgency
    if recv and pending:
        urgency = 'high' if urgency in {'normal', 'medium'} else urgency

    next_action = {
        'submit_request': 'Submit clerk request letter and set request_channel to submitted.',
        'await_response': 'Follow up with clerk and update response_received_date when records arrive.',
        'log_intake': 'Log received certified files into the certified intake tracker.',
        'update_mapping': 'Update issue_preclusion_mapping.json notes from certified records and rerun generators.',
        'complete_remaining': 'Finish remaining pending tracker flags and recompute outputs.',
        'complete': 'No immediate action; monitor for supplemental records.',
    }[stage]

    return {
        'case_number': row.get('case_number', ''),
        'stage': stage,
        'urgency': urgency,
        'days_to_due': days_to_due,
        'pending_fields': pending,
        'next_action': next_action,
        'request_channel': row.get('request_channel', ''),
        'response_due_date': row.get('response_due_date', ''),
        'response_received_date': row.get('response_received_date', ''),
        'notes': row.get('notes', ''),
    }


def main():
    rows = load_rows()
    actions = [compute_priority(r) for r in rows]
    order = {'overdue': 0, 'high': 1, 'medium': 2, 'normal': 3}
    actions.sort(key=lambda x: (order.get(x['urgency'], 9), x['days_to_due'] if x['days_to_due'] is not None else 9999, x['case_number']))

    payload = {
        'generated_at': str(date.today()),
        'source_tracker': str(TRACKER),
        'actions': actions,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Issue-Preclusion Request Next Actions')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    for a in actions:
        lines.append(f"## {a['case_number']} [{a['urgency']}]")
        lines.append(f"- stage: {a['stage']}")
        lines.append(f"- due: {a['response_due_date']} (days_to_due={a['days_to_due']})")
        lines.append(f"- channel: {a['request_channel']} received: {a['response_received_date'] or '(none)'}")
        lines.append('- pending:')
        if a['pending_fields']:
            for p in a['pending_fields']:
                lines.append(f'- {p}')
        else:
            lines.append('- (none)')
        lines.append(f"- next_action: {a['next_action']}")
        if a['notes']:
            lines.append(f"- notes: {a['notes']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
