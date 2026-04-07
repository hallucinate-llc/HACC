#!/usr/bin/env python3
"""Apply multiple confirmed service updates from a CSV file.

CSV columns required:
recipient,date_served,service_method,person_served,production_due,status,notes_append

Safety:
- requires explicit acknowledgement flag
- updates only rows with exact recipient matches
- creates backup before write
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

REQ = ['recipient', 'date_served', 'service_method', 'person_served', 'production_due', 'status']


def is_iso(d: str) -> bool:
    d = (d or '').strip()
    if len(d) != 10:
        return False
    y, m, dd = d.split('-')
    return y.isdigit() and m.isdigit() and dd.isdigit()


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Apply confirmed service updates from CSV')
    p.add_argument('--input-csv', required=True, help='Path to confirmed update CSV')
    p.add_argument('--acknowledge', required=True, help='Must equal: I CONFIRM THESE SERVICE FACTS ARE TRUE')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    required_ack = 'I CONFIRM THESE SERVICE FACTS ARE TRUE'
    if args.acknowledge.strip() != required_ack:
        raise SystemExit(f'Acknowledgement mismatch. Use exactly: {required_ack}')

    in_csv = Path(args.input_csv)
    if not in_csv.exists():
        raise SystemExit(f'Input CSV not found: {in_csv}')

    with ACTIVE_LOG.open('r', encoding='utf-8', newline='') as fh:
        rows = list(csv.DictReader(fh))
        fieldnames = list(rows[0].keys()) if rows else []

    if not rows:
        raise SystemExit('Active service log is empty.')

    by_recipient = {(r.get('recipient') or '').strip(): r for r in rows}

    with in_csv.open('r', encoding='utf-8', newline='') as fh:
        updates = list(csv.DictReader(fh))

    if not updates:
        raise SystemExit('Input CSV has no rows.')

    for idx, u in enumerate(updates, start=1):
        for c in REQ:
            if not (u.get(c) or '').strip():
                raise SystemExit(f'Row {idx}: missing required field {c}')

        rec = (u.get('recipient') or '').strip()
        if rec not in by_recipient:
            raise SystemExit(f"Row {idx}: recipient not found in active log: {rec}")

        status = (u.get('status') or '').strip()
        if status not in VALID_STATUSES:
            raise SystemExit(f"Row {idx}: invalid status {status}")

        if not is_iso(u.get('date_served', '')):
            raise SystemExit(f"Row {idx}: invalid date_served {u.get('date_served')}")
        if not is_iso(u.get('production_due', '')):
            raise SystemExit(f"Row {idx}: invalid production_due {u.get('production_due')}")

    backup = BACKUP_DIR / f"28_active_service_log_2026-04-07.backup_batch_{date.today().isoformat()}.csv"
    shutil.copy2(ACTIVE_LOG, backup)

    for u in updates:
        rec = (u.get('recipient') or '').strip()
        row = by_recipient[rec]
        row['status'] = (u.get('status') or '').strip()
        row['date_served'] = (u.get('date_served') or '').strip()
        row['service_method'] = (u.get('service_method') or '').strip()
        row['person_served'] = (u.get('person_served') or '').strip()
        row['production_due'] = (u.get('production_due') or '').strip()

        notes_append = (u.get('notes_append') or '').strip()
        if notes_append:
            cur = (row.get('notes') or '').strip()
            row['notes'] = f"{cur} | {notes_append}" if cur else notes_append

    with ACTIVE_LOG.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f'Applied {len(updates)} update(s).')
    print(f'Backup: {backup}')
    print(f'Updated log: {ACTIVE_LOG}')


if __name__ == '__main__':
    main()
