#!/usr/bin/env python3
"""Update one row in issue-preclusion request tracker (dry-run by default)."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv')


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Update one issue-preclusion request tracker row')
    p.add_argument('--case-number', required=True, help='Case number to update (exact match)')
    p.add_argument('--field', required=True, help='CSV column name to update')
    p.add_argument('--value', required=True, help='New value')
    p.add_argument('--write', action='store_true', help='Persist change; dry-run if omitted')
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not TRACKER.exists():
        raise SystemExit(f'Missing tracker: {TRACKER}')

    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if args.field not in fieldnames:
        raise SystemExit(f'Unknown field: {args.field}. Available: {", ".join(fieldnames)}')

    match_idx = None
    for i, row in enumerate(rows):
        if (row.get('case_number') or '').strip() == args.case_number:
            match_idx = i
            break

    if match_idx is None:
        raise SystemExit(f'Case number not found: {args.case_number}')

    before = rows[match_idx].get(args.field, '')
    after = args.value

    print(f'case_number={args.case_number}')
    print(f'field={args.field}')
    print(f'before={before}')
    print(f'after={after}')
    print(f'write={args.write}')

    if not args.write:
        return

    rows[match_idx][args.field] = after
    with TRACKER.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(TRACKER)


if __name__ == '__main__':
    main()
