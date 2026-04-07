#!/usr/bin/env python3
"""Generate case-specific clerk request letter drafts from issue-preclusion tracker."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
OUT = FINAL / f'59_issue_preclusion_clerk_request_letters_{date.today().isoformat()}.md'


def load_rows() -> list[dict[str, str]]:
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def block_for_case(r: dict[str, str]) -> list[str]:
    case_no = (r.get('case_number') or '').strip()
    req_date = (r.get('request_date') or '').strip() or str(date.today())
    due = (r.get('response_due_date') or '').strip() or '________________'
    channel = (r.get('request_channel') or '').strip() or 'to_submit'

    lines: list[str] = []
    lines.append(f'## Clerk Request Letter - Case `{case_no}`')
    lines.append('')
    lines.append(f'Date: {req_date}')
    lines.append('To: Clackamas County Circuit Court Clerk / Records Custodian')
    lines.append('')
    lines.append('Re: Request for Certified Court Records')
    lines.append(f'Case Number: `{case_no}`')
    lines.append('')
    lines.append('Please provide certified copies of the following records for the case identified above:')
    lines.append('1. Final signed disposition order / judgment (grant, denial, dismissal, or equivalent final ruling).')
    lines.append('2. Register of actions / docket printout showing filing and disposition history.')
    lines.append('3. Hearing setting notices and orders to appear, if any.')
    lines.append('4. Hearing minutes, appearance register, and transcript/minute summaries (if available).')
    lines.append('5. Proof(s) of service and notice tied to the hearing(s) and disposition event(s).')
    lines.append('6. Caption and party-identification pages sufficient to identify parties and procedural roles.')
    lines.append('')
    lines.append('Certification request:')
    lines.append('- Please include clerk certification for each document set and identify certification date(s).')
    lines.append('')
    lines.append('Requested delivery:')
    lines.append('- Certified paper copies and, if permitted, secure electronic duplicates.')
    lines.append('')
    lines.append('Case processing note:')
    lines.append('- These records are requested to complete issue-preclusion element mapping (finality and full/fair opportunity) in related guardianship litigation support materials.')
    lines.append('')
    lines.append('Requestor: ________________________________')
    lines.append('Contact: _________________________________')
    lines.append('Preferred channel: ________________________')
    lines.append('')
    lines.append(f'Tracker status at generation: channel=`{channel}` due=`{due}`')
    lines.append('')
    lines.append('---')
    lines.append('')
    return lines


def main() -> None:
    rows = load_rows()
    lines: list[str] = []
    lines.append('# Issue-Preclusion Clerk Request Letters')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    lines.append(f'Source tracker: `{TRACKER}`')
    lines.append('')

    if not rows:
        lines.append('No tracker rows found.')
    else:
        for r in rows:
            lines.extend(block_for_case(r))

    OUT.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT)


if __name__ == '__main__':
    main()
