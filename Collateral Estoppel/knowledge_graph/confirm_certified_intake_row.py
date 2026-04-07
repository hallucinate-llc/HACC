#!/usr/bin/env python3
"""Confirm a certified intake tracker row with safety checks.

By default runs in dry-run mode. Use --write to persist changes.
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/45_certified_records_intake_tracker_template_2026-04-07.csv')


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Confirm one certified intake row')
    p.add_argument('--row', type=int, required=True, help='CSV data row number (2-based, as shown in validation report)')
    p.add_argument('--file-path', required=True, help='Absolute path to certified file')
    p.add_argument('--file-name', default='', help='Optional explicit file name override')
    p.add_argument('--case-number', default='26PR00641', help='Case number to set on row')
    p.add_argument('--received-date', default=str(date.today()), help='Received date YYYY-MM-DD')
    p.add_argument('--override-source-date', default=str(date.today()), help='Override source date YYYY-MM-DD')
    p.add_argument('--write', action='store_true', help='Persist updates (default is dry-run)')
    return p.parse_args()


def load_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open('r', encoding='utf-8', newline='') as fh:
        rdr = csv.DictReader(fh)
        fields = list(rdr.fieldnames or [])
        rows = [{k: (v or '').strip() for k, v in row.items()} for row in rdr]
    return fields, rows


def save_rows(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> None:
    args = parse_args()
    if not TRACKER.exists():
        raise SystemExit(f'Tracker not found: {TRACKER}')

    file_path = Path(args.file_path)
    if not file_path.exists():
        raise SystemExit(f'Certified file path not found: {file_path}')
    if not file_path.is_file():
        raise SystemExit(f'Certified file path is not a file: {file_path}')

    fields, rows = load_rows(TRACKER)
    if args.row < 2:
        raise SystemExit('--row must be 2 or greater (CSV data rows start at 2).')

    idx = args.row - 2
    if idx < 0 or idx >= len(rows):
        raise SystemExit(f'Row out of range: {args.row}. Tracker has {len(rows)} data row(s).')

    row = dict(rows[idx])
    row['received_date'] = args.received_date
    row['absolute_path'] = str(file_path)
    row['file_name'] = args.file_name.strip() or file_path.name
    row['case_number'] = args.case_number
    row['is_certified'] = 'yes'
    row['party_identity_matched'] = 'yes'
    row['override_source_date'] = args.override_source_date
    note = (row.get('notes', '') or '').strip()
    suffix = f"confirmed_on_{date.today().isoformat()}"
    row['notes'] = f"{note} | {suffix}" if note else suffix

    print(f"Target row: {args.row}")
    print(f"- file_name: {row['file_name']}")
    print(f"- absolute_path: {row['absolute_path']}")
    print(f"- is_certified: {row['is_certified']}")
    print(f"- party_identity_matched: {row['party_identity_matched']}")

    if not args.write:
        print('Dry-run only. Re-run with --write to persist changes.')
        return

    rows[idx] = row
    save_rows(TRACKER, fields, rows)
    print(f'Updated tracker: {TRACKER}')


if __name__ == '__main__':
    main()
