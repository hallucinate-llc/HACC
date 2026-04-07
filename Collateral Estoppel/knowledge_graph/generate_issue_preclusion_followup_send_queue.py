#!/usr/bin/env python3
"""Generate follow-up send queue for a target date from tracker/calendar."""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
GEN = ROOT / 'knowledge_graph' / 'generated'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
CAL_JSON = GEN / f'issue_preclusion_followup_calendar_{date.today().isoformat()}.json'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Generate issue-preclusion follow-up send queue for a date')
    p.add_argument('--date', default=str(date.today()), help='Target date YYYY-MM-DD')
    return p.parse_args()


def parse_iso(v: str):
    try:
        return date.fromisoformat((v or '').strip())
    except Exception:
        return None


def load_tracker() -> dict[str, dict[str, str]]:
    if not TRACKER.exists():
        return {}
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
    return {(r.get('case_number') or '').strip(): r for r in rows}


def load_calendar() -> list[dict]:
    if not CAL_JSON.exists():
        return []
    try:
        obj = json.loads(CAL_JSON.read_text(encoding='utf-8'))
        return obj.get('calendar', [])
    except Exception:
        return []


def due_labels(item: dict, target: date) -> list[str]:
    out = []
    f = item.get('followup_dates', {})
    for label, field in [
        ('followup_1', 'followup_1'),
        ('followup_2', 'followup_2'),
        ('due_date_check', 'followup_3_due_date_check'),
        ('escalation', 'escalation_if_no_response'),
    ]:
        d = parse_iso(f.get(field, ''))
        if d and d == target:
            out.append(label)
    return out


def main() -> None:
    args = parse_args()
    target = parse_iso(args.date)
    if not target:
        raise SystemExit('Invalid --date; expected YYYY-MM-DD')

    tracker = load_tracker()
    cal = load_calendar()

    queue = []
    for item in cal:
        case_no = item.get('case_number', '')
        labels = due_labels(item, target)
        if not labels:
            continue

        row = tracker.get(case_no, {})
        contact = (row.get('clerk_contact') or '').strip() or '(missing contact)'
        due = (row.get('response_due_date') or '').strip() or ''
        queue.append(
            {
                'case_number': case_no,
                'labels_due': labels,
                'clerk_contact': contact,
                'response_due_date': due,
            }
        )

    out_json = GEN / f'issue_preclusion_followup_send_queue_{target.isoformat()}.json'
    out_md = FINAL / f'65_issue_preclusion_followup_send_queue_{target.isoformat()}.md'

    payload = {
        'generated_at': str(date.today()),
        'target_date': target.isoformat(),
        'queue_count': len(queue),
        'queue': queue,
    }
    out_json.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines: list[str] = []
    lines.append('# Issue-Preclusion Follow-Up Send Queue')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append(f'Target date: {target.isoformat()}')
    lines.append(f'Queue count: {len(queue)}')
    lines.append('')

    if not queue:
        lines.append('No follow-up sends due on target date.')
    else:
        for q in queue:
            case_no = q['case_number']
            labels = ', '.join(q['labels_due'])
            contact = q['clerk_contact']
            due = q['response_due_date']
            lines.append(f'## Case `{case_no}`')
            lines.append(f'- due_label(s): {labels}')
            lines.append(f'- clerk_contact: {contact}')
            lines.append(f'- response_due_date: {due}')
            lines.append('')
            lines.append('Send template:')
            lines.append('```text')
            lines.append(f'Subject: Follow-Up: Certified Records Request - Case {case_no}')
            lines.append('')
            lines.append('Clerk/Records Custodian,')
            lines.append('')
            lines.append(f'This is a scheduled follow-up regarding the certified-records request for case {case_no}.')
            lines.append('Please provide current status and estimated completion date.')
            if due:
                lines.append(f'Our current requested response date in tracking is {due}.')
            lines.append('')
            lines.append('Thank you,')
            lines.append('________________')
            lines.append('```')
            lines.append('')

    out_md.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(out_json)
    print(out_md)


if __name__ == '__main__':
    main()
