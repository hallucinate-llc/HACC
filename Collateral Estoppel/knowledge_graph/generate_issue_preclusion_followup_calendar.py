#!/usr/bin/env python3
"""Generate follow-up calendar and templates from issue-preclusion request tracker."""

from __future__ import annotations

import csv
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
GEN = ROOT / 'knowledge_graph' / 'generated'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
OUT_JSON = GEN / f'issue_preclusion_followup_calendar_{date.today().isoformat()}.json'
OUT_MD = FINAL / f'61_issue_preclusion_followup_calendar_and_templates_{date.today().isoformat()}.md'


def parse_iso(v: str):
    try:
        return date.fromisoformat((v or '').strip())
    except Exception:
        return None


def load_rows():
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def compute_schedule(row: dict[str, str]):
    today = date.today()
    req_date = parse_iso(row.get('request_date', '')) or today
    due = parse_iso(row.get('response_due_date', '')) or (req_date + timedelta(days=14))
    recv = parse_iso(row.get('response_received_date', ''))
    channel = (row.get('request_channel') or '').strip().lower()

    followup_1 = req_date + timedelta(days=3)
    followup_2 = req_date + timedelta(days=7)
    followup_3 = due
    escalation = due + timedelta(days=2)

    stage = 'closed' if recv else ('pre_submit' if channel in {'', 'to_submit'} else 'awaiting_response')

    return {
        'case_number': row.get('case_number', ''),
        'request_date': str(req_date),
        'response_due_date': str(due),
        'response_received_date': str(recv) if recv else '',
        'stage': stage,
        'followup_dates': {
            'followup_1': str(followup_1),
            'followup_2': str(followup_2),
            'followup_3_due_date_check': str(followup_3),
            'escalation_if_no_response': str(escalation),
        },
    }


def main():
    rows = load_rows()
    items = [compute_schedule(r) for r in rows]

    payload = {
        'generated_at': str(date.today()),
        'source_tracker': str(TRACKER),
        'calendar': items,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Issue-Preclusion Follow-Up Calendar And Templates')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')

    for it in items:
        case_no = it['case_number']
        f = it['followup_dates']
        lines.append(f'## Case `{case_no}`')
        lines.append(f"- stage: {it['stage']}")
        lines.append(f"- request_date: {it['request_date']}")
        lines.append(f"- due_date: {it['response_due_date']}")
        lines.append(f"- followup_1: {f['followup_1']}")
        lines.append(f"- followup_2: {f['followup_2']}")
        lines.append(f"- due_date_check: {f['followup_3_due_date_check']}")
        lines.append(f"- escalation_date: {f['escalation_if_no_response']}")
        lines.append('')
        lines.append('Follow-up email template:')
        lines.append('```text')
        lines.append(f'Subject: Follow-Up Request for Certified Records - Case {case_no}')
        lines.append('')
        lines.append('Clerk/Records Custodian,')
        lines.append('')
        lines.append(f'This is a follow-up regarding our certified records request for case {case_no}.')
        lines.append('Please advise current processing status and estimated completion date.')
        lines.append('If additional information is required, please identify what is needed so we can respond promptly.')
        lines.append('')
        lines.append('Requested record groups include: final disposition order/judgment, register of actions, hearing/appearance records, and service/notice records.')
        lines.append('')
        lines.append('Thank you,')
        lines.append('________________')
        lines.append('```')
        lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
