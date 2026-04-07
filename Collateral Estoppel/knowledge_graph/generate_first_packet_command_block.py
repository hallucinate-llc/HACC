#!/usr/bin/env python3
"""Generate copy/paste command block for first certified packet activation."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
KG = ROOT / 'knowledge_graph'
OUT = KG / 'generated'


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Generate first-packet activation command block')
    p.add_argument('--row', type=int, default=2, help='Tracker row number (2-based)')
    p.add_argument('--file-path', required=True, help='Absolute path to certified file')
    p.add_argument('--case-number', default='26PR00641', help='Case number')
    p.add_argument(
        '--output-name',
        default='',
        help='Optional output markdown filename (written under knowledge_graph/generated)',
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    fp = Path(args.file_path)
    exists = fp.exists() and fp.is_file()

    default_name = f'packet_activation_commands_row{args.row}_{date.today().isoformat()}.md'
    md = OUT / (args.output_name or default_name)
    report_path = OUT / 'deontic_reasoning_report.json'
    pipeline_status_path = OUT / 'certified_intake_promotion_pipeline_status_2026-04-07.md'

    verify_py = [
        'python3 - << "PY"',
        'import json',
        f'p = "{report_path}"',
        'o = json.load(open(p))',
        's = o["modes"]["strict"]',
        'print("strict", len(s["active_rules"]), len(s["unresolved_rules"]), len(s["inactive_rules"]))',
        'print("status_or_value_changes", o.get("fact_override_summary", {}).get("applied_status_or_value_changes"))',
        'PY',
    ]

    lines = [
        '# First Packet Activation Commands',
        '',
        f'Generated: {date.today().isoformat()}',
        f'Row: {args.row}',
        f'Case number: {args.case_number}',
        f'File path: {fp}',
        f'File exists now: {exists}',
        '',
        '## 1) Dry-run row confirmation',
        '```bash',
        f'python3 "{KG / "confirm_certified_intake_row.py"}" \\\\',
        f'  --row {args.row} \\\\',
        f'  --file-path "{fp}" \\\\',
        f'  --case-number "{args.case_number}"',
        '```',
        '',
        '## 2) Persist row confirmation',
        '```bash',
        f'python3 "{KG / "confirm_certified_intake_row.py"}" \\\\',
        f'  --row {args.row} \\\\',
        f'  --file-path "{fp}" \\\\',
        f'  --case-number "{args.case_number}" \\\\',
        '  --write',
        '```',
        '',
        '## 3) Apply certified intake promotion pipeline',
        '```bash',
        f'python3 "{KG / "run_certified_intake_promotion_pipeline.py"}" \\\\',
        '  --apply \\\\',
        '  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"',
        '```',
        '',
        '## 4) Verify outcomes',
        '```bash',
        f'sed -n "1,220p" "{pipeline_status_path}"',
        *verify_py,
        '```',
        '',
    ]
    md.write_text('\n'.join(lines), encoding='utf-8')
    print(md)


if __name__ == '__main__':
    main()
