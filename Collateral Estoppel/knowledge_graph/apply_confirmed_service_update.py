#!/usr/bin/env python3
"""Apply one confirmed service-event update to the active service log.

This script is intentionally explicit to avoid accidental fabrication.
It updates exactly one recipient row and creates a backup copy first.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path
import shutil

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
ACTIVE_LOG = ROOT / 'drafts/final_filing_set/28_active_service_log_2026-04-07.csv'
BACKUP_DIR = ROOT / 'drafts/final_filing_set'

VALID_STATUSES = {
    'served',
    'awaiting_production',
    'production_received',
    'deficiency_notice_stage',
    'motion_to_compel_stage',
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Apply confirmed service update to active log.')
    p.add_argument('--recipient', required=True, help='Exact recipient column value to update.')
    p.add_argument('--date-served', required=True, help='YYYY-MM-DD date served.')
    p.add_argument('--service-method', required=True, help='Service method text.')
    p.add_argument('--person-served', required=True, help='Person/entity served.')
    p.add_argument('--production-due', required=True, help='YYYY-MM-DD production due date.')
    p.add_argument('--status', default='awaiting_production', choices=sorted(VALID_STATUSES), help='Post-service status.')
    p.add_argument('--notes-append', default='', help='Optional note text to append.')
    p.add_argument(
        '--acknowledge',
        required=True,
        help='Safety acknowledgement string: I CONFIRM THESE SERVICE FACTS ARE TRUE',
    )
    return p.parse_args()


def is_iso(d: str) -> bool:
    if len(d) != 10:
        return False
    y, m, dd = d.split('-')
    return y.isdigit() and m.isdigit() and dd.isdigit()


def main() -> None:
    args = parse_args()

    required_ack = 'I CONFIRM THESE SERVICE FACTS ARE TRUE'
    if args.acknowledge.strip() != required_ack:
        raise SystemExit(f'Acknowledgement mismatch. Use exactly: {required_ack}')

    for label, value in (('date-served', args.date_served), ('production-due', args.production_due)):
        if not is_iso(value):
            raise SystemExit(f'Invalid {label}: {value}. Use YYYY-MM-DD.')

    if not ACTIVE_LOG.exists():
        raise SystemExit(f'Active log not found: {ACTIVE_LOG}')

    with ACTIVE_LOG.open('r', encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = list(rows[0].keys()) if rows else []

    if not rows:
        raise SystemExit('Active log is empty.')

    matched = [r for r in rows if (r.get('recipient') or '').strip() == args.recipient.strip()]
    if len(matched) != 1:
        raise SystemExit(f"Expected exactly one row for recipient '{args.recipient}', found {len(matched)}.")

    target = matched[0]
    target['status'] = args.status
    target['date_served'] = args.date_served
    target['service_method'] = args.service_method
    target['person_served'] = args.person_served
    target['production_due'] = args.production_due

    if args.notes_append:
        cur = (target.get('notes') or '').strip()
        if cur:
            target['notes'] = f"{cur} | {args.notes_append.strip()}"
        else:
            target['notes'] = args.notes_append.strip()

    backup = BACKUP_DIR / f"28_active_service_log_2026-04-07.backup_{date.today().isoformat()}.csv"
    shutil.copy2(ACTIVE_LOG, backup)

    with ACTIVE_LOG.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f'Updated recipient: {args.recipient}')
    print(f'Backup written: {backup}')
    print(f'Updated log: {ACTIVE_LOG}')


if __name__ == '__main__':
    main()
