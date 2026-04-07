#!/usr/bin/env python3
"""Batch update issue-preclusion request tracker rows by case list."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

TRACKER = Path('/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv')


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Batch update issue-preclusion request tracker rows')
    p.add_argument('--cases', required=True, help='Comma-separated case numbers (or "all")')
    p.add_argument('--field', required=True, help='Field name to update')
    p.add_argument('--value', required=True, help='Field value to set')
    p.add_argument('--write', action='store_true', help='Persist updates (dry-run default)')
    return p.parse_args()


def parse_cases(value: str, rows: list[dict[str, str]]) -> set[str]:
    v = (value or '').strip()
    if v.lower() == 'all':
        return {(r.get('case_number') or '').strip() for r in rows if (r.get('case_number') or '').strip()}
    return {x.strip() for x in v.split(',') if x.strip()}


def main() -> None:
    args = parse_args()
    if not TRACKER.exists():
        raise SystemExit(f'Missing tracker: {TRACKER}')

    with TRACKER.open('r', encoding='utf-8', newline='') as fh:
        reader = csv.DictReader(fh)
        fieldnames = reader.fieldnames or []
        rows = list(reader)

    if args.field not in fieldnames:
        raise SystemExit(f'Unknown field: {args.field}')

    target_cases = parse_cases(args.cases, rows)
    changed = []

    for r in rows:
        case_no = (r.get('case_number') or '').strip()
        if case_no not in target_cases:
            continue
        before = r.get(args.field, '')
        after = args.value
        if before != after:
            r[args.field] = after
            changed.append((case_no, before, after))

    print(f'target_cases={sorted(target_cases)}')
    print(f'changed_count={len(changed)}')
    for case_no, before, after in changed:
        print(f'- {case_no}: {args.field}: {before} -> {after}')

    if not args.write:
        print('dry_run=True (no file changes)')
        return

    with TRACKER.open('w', encoding='utf-8', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(TRACKER)


if __name__ == '__main__':
    main()
