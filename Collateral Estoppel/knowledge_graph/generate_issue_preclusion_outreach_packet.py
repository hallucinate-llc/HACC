#!/usr/bin/env python3
"""Generate contact-prefilled outreach packet from issue-preclusion tracker."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
OUT = FINAL / f'64_issue_preclusion_outreach_packet_{date.today().isoformat()}.md'


def load_rows() -> list[dict[str, str]]:
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def main() -> None:
    rows = load_rows()
    lines: list[str] = []
    lines.append('# Issue-Preclusion Outreach Packet')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    lines.append('Use these drafts for clerk communication tracking per case.')
    lines.append('')

    for r in rows:
        case_no = (r.get('case_number') or '').strip()
        contact = (r.get('clerk_contact') or '').strip() or '<contact missing>'
        due = (r.get('response_due_date') or '').strip() or '________________'

        lines.append(f'## Case `{case_no}`')
        lines.append(f'- clerk_contact: {contact}')
        lines.append(f'- response_due_date: {due}')
        lines.append('')

        lines.append('Initial status-confirmation email:')
        lines.append('```text')
        lines.append(f'Subject: Certified Records Request Status - Case {case_no}')
        lines.append('')
        lines.append('Clerk/Records Custodian,')
        lines.append('')
        lines.append(f'I am writing to confirm receipt and processing status for our certified-records request in case {case_no}.')
        lines.append('Please confirm whether the request is in queue and provide an estimated completion date.')
        lines.append('')
        lines.append('Requested sets: final disposition order/judgment; register of actions; hearing/appearance records; service/notice records.')
        lines.append('')
        lines.append('Thank you,')
        lines.append('________________')
        lines.append('```')
        lines.append('')

        lines.append('Follow-up email (if no response by follow-up date):')
        lines.append('```text')
        lines.append(f'Subject: Follow-Up: Certified Records Request - Case {case_no}')
        lines.append('')
        lines.append('Clerk/Records Custodian,')
        lines.append('')
        lines.append(f'This is a follow-up regarding the certified-records request for case {case_no}.')
        lines.append('Please provide a status update and estimated date for completion.')
        lines.append('')
        lines.append(f'Current requested response date in our tracking record: {due}.')
        lines.append('')
        lines.append('Thank you,')
        lines.append('________________')
        lines.append('```')
        lines.append('')
        lines.append('---')
        lines.append('')

    OUT.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT)


if __name__ == '__main__':
    main()
