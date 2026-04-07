#!/usr/bin/env python3
"""Generate daily action brief from issue-preclusion follow-up calendar and tracker."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
FINAL = ROOT / 'drafts' / 'final_filing_set'
GEN = ROOT / 'knowledge_graph' / 'generated'
TRACKER = FINAL / '57_issue_preclusion_case_request_tracker_2026-04-07.csv'
CAL_JSON = GEN / f'issue_preclusion_followup_calendar_{date.today().isoformat()}.json'
OUT_MD = GEN / f'issue_preclusion_daily_action_brief_{date.today().isoformat()}.md'


def parse_iso(v: str):
    try:
        return date.fromisoformat((v or '').strip())
    except Exception:
        return None


def load_rows() -> list[dict[str, str]]:
    if not TRACKER.exists():
        return []
    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        return list(csv.DictReader(fh))


def load_calendar() -> dict:
    if not CAL_JSON.exists():
        return {'calendar': []}
    try:
        return json.loads(CAL_JSON.read_text(encoding='utf-8'))
    except Exception:
        return {'calendar': []}


def main() -> None:
    today = date.today()
    rows = { (r.get('case_number') or '').strip(): r for r in load_rows() }
    cal = load_calendar().get('calendar', [])

    due_today = []
    upcoming = []
    for item in cal:
        case_no = item.get('case_number', '')
        f = item.get('followup_dates', {})
        markers = {
            'followup_1': parse_iso(f.get('followup_1', '')),
            'followup_2': parse_iso(f.get('followup_2', '')),
            'due_date_check': parse_iso(f.get('followup_3_due_date_check', '')),
            'escalation': parse_iso(f.get('escalation_if_no_response', '')),
        }

        for label, d in markers.items():
            if not d:
                continue
            delta = (d - today).days
            entry = {'case_number': case_no, 'label': label, 'date': str(d), 'days_from_today': delta}
            if delta == 0:
                due_today.append(entry)
            elif 0 < delta <= 7:
                upcoming.append(entry)

    due_today.sort(key=lambda x: (x['case_number'], x['label']))
    upcoming.sort(key=lambda x: (x['days_from_today'], x['case_number'], x['label']))

    lines = []
    lines.append('# Issue-Preclusion Daily Action Brief')
    lines.append('')
    lines.append(f'Generated: {today.isoformat()}')
    lines.append('')
    lines.append(f'- cases_tracked={len(rows)}')
    lines.append(f'- due_today={len(due_today)}')
    lines.append(f'- upcoming_7_days={len(upcoming)}')
    lines.append('')

    lines.append('## Due Today')
    if due_today:
        for x in due_today:
            contact = (rows.get(x['case_number'], {}).get('clerk_contact') or '').strip() or '(missing contact)'
            lines.append(f"- {x['case_number']} {x['label']} on {x['date']} | contact: {contact}")
    else:
        lines.append('- None due today.')
    lines.append('')

    lines.append('## Upcoming (Next 7 Days)')
    if upcoming:
        for x in upcoming:
            lines.append(f"- {x['case_number']} {x['label']} on {x['date']} (in {x['days_from_today']} day(s))")
    else:
        lines.append('- None in next 7 days.')
    lines.append('')

    lines.append('## Immediate Next Step')
    if due_today:
        lines.append('- Send due-today follow-ups using the outreach packet drafts and log any response dates immediately in tracker row 57.')
    else:
        lines.append('- No send action required today; next scheduled follow-up date(s) are listed above.')

    OUT_MD.write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')
    print(OUT_MD)


if __name__ == '__main__':
    main()
