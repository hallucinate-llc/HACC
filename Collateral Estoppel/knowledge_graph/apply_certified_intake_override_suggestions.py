#!/usr/bin/env python3
"""Apply certified-intake override suggestions into evidence_fact_overrides CSV.

Safety:
- requires explicit acknowledgement flag
- creates dated backup before write
- upserts rows by fact_id
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
import json
from pathlib import Path
import shutil

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OVERRIDES = ROOT / 'evidence_fact_overrides_2026-04-07.csv'
SUGGESTIONS_JSON = ROOT / 'generated/certified_intake_override_suggestions_2026-04-07.json'

FIELDS = [
    'fact_id',
    'override_status',
    'override_value',
    'override_source',
    'override_date',
    'note',
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Apply certified intake suggestions to override CSV')
    p.add_argument('--acknowledge', required=True, help='Must equal: I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED')
    p.add_argument('--suggestions-json', default=str(SUGGESTIONS_JSON), help='Path to suggestions JSON')
    p.add_argument('--overrides-csv', default=str(OVERRIDES), help='Path to overrides CSV')
    return p.parse_args()


def load_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open('r', encoding='utf-8', newline='') as fh:
        rdr = csv.DictReader(fh)
        return [{k: (v or '').strip() for k, v in row.items()} for row in rdr]


def save_csv(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            out = {k: (r.get(k, '') or '').strip() for k in FIELDS}
            w.writerow(out)


def main() -> None:
    args = parse_args()
    required_ack = 'I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED'
    if args.acknowledge.strip() != required_ack:
        raise SystemExit(f'Acknowledgement mismatch. Use exactly: {required_ack}')

    suggestions_path = Path(args.suggestions_json)
    overrides_path = Path(args.overrides_csv)

    if not suggestions_path.exists():
        raise SystemExit(f'Suggestions JSON not found: {suggestions_path}')

    if not overrides_path.exists():
        raise SystemExit(f'Overrides CSV not found: {overrides_path}')

    obj = json.loads(suggestions_path.read_text(encoding='utf-8'))
    suggestions = list(obj.get('suggestions', []))
    if not suggestions:
        print('No suggestions to apply. Overrides CSV unchanged.')
        print(f'Suggestions file: {suggestions_path}')
        return

    rows = load_csv(overrides_path)
    by_id = {r.get('fact_id', '').strip(): r for r in rows if (r.get('fact_id') or '').strip()}

    applied = 0
    for s in suggestions:
        fid = (s.get('fact_id') or '').strip()
        if not fid:
            continue
        row = by_id.get(fid, {'fact_id': fid})
        row['override_status'] = str(s.get('override_status', '')).strip()
        row['override_value'] = str(s.get('override_value', '')).strip()
        row['override_source'] = str(s.get('override_source', '')).strip()
        row['override_date'] = str(s.get('override_date', '')).strip()
        row['note'] = str(s.get('note', '')).strip()
        by_id[fid] = row
        applied += 1

    ordered = []
    seen = set()
    for r in rows:
        fid = (r.get('fact_id') or '').strip()
        if not fid:
            continue
        ordered.append(by_id[fid])
        seen.add(fid)

    for fid, r in sorted(by_id.items()):
        if fid in seen:
            continue
        ordered.append(r)

    backup = overrides_path.with_name(f"{overrides_path.stem}.backup_apply_{date.today().isoformat()}{overrides_path.suffix}")
    shutil.copy2(overrides_path, backup)
    save_csv(overrides_path, ordered)

    print(f'Applied {applied} suggestion row(s).')
    print(f'Backup: {backup}')
    print(f'Updated overrides: {overrides_path}')


if __name__ == '__main__':
    main()
