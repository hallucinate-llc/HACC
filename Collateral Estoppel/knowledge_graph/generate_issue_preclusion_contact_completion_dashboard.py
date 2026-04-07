#!/usr/bin/env python3
"""Generate contact-completion dashboard for issue-preclusion request tracker."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv')
GEN = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
OUT_JSON = GEN / f'issue_preclusion_contact_completion_dashboard_{date.today().isoformat()}.json'
OUT_MD = GEN / f'issue_preclusion_contact_completion_dashboard_{date.today().isoformat()}.md'


def load_rows():
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def main():
    rows = load_rows()
    case_rows = []
    missing = 0
    for r in rows:
        case_no = (r.get('case_number') or '').strip()
        contact = (r.get('clerk_contact') or '').strip()
        channel = (r.get('request_channel') or '').strip()
        due = (r.get('response_due_date') or '').strip()
        has_contact = bool(contact)
        if not has_contact:
            missing += 1
        case_rows.append(
            {
                'case_number': case_no,
                'request_channel': channel,
                'response_due_date': due,
                'clerk_contact': contact,
                'contact_present': has_contact,
                'next_action': 'Fill clerk_contact with verified name/email/phone.' if not has_contact else 'Contact recorded; use for scheduled follow-ups.',
            }
        )

    payload = {
        'generated_at': str(date.today()),
        'source_tracker': str(TRACKER),
        'cases_total': len(case_rows),
        'cases_missing_contact': missing,
        'cases': case_rows,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Issue-Preclusion Contact Completion Dashboard')
    lines.append('')
    lines.append(f'Generated: {date.today().isoformat()}')
    lines.append('')
    lines.append(f"- cases_total={payload['cases_total']}")
    lines.append(f"- cases_missing_contact={payload['cases_missing_contact']}")
    lines.append('')
    for c in case_rows:
        lines.append(f"## {c['case_number']}")
        lines.append(f"- channel: {c['request_channel']}")
        lines.append(f"- due: {c['response_due_date']}")
        lines.append(f"- clerk_contact_present: {c['contact_present']}")
        lines.append(f"- clerk_contact: {c['clerk_contact'] or '(missing)'}")
        lines.append(f"- next_action: {c['next_action']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
