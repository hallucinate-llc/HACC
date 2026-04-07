#!/usr/bin/env python3
"""Run certified-intake promotion pipeline end-to-end with status output."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OUT = ROOT / 'generated'

VALIDATOR = ROOT / 'validate_certified_intake_tracker.py'
SUGGEST = ROOT / 'generate_certified_intake_override_suggestions.py'
APPLY = ROOT / 'apply_certified_intake_override_suggestions.py'
GEN = ROOT / 'generate_formal_reasoning_artifacts.py'
PROOF = ROOT / 'generate_proof_intake_map.py'
GAP = ROOT / 'generate_grounding_gap_report.py'
DASH = ROOT / 'generate_deontic_readiness_dashboard.py'

SUGGESTIONS_JSON = OUT / 'certified_intake_override_suggestions_2026-04-07.json'
REPORT_JSON = OUT / 'deontic_reasoning_report.json'



def run_step(label: str, cmd: list[str]) -> dict[str, object]:
    p = subprocess.run(cmd, capture_output=True, text=True)
    return {
        'label': label,
        'cmd': cmd,
        'returncode': p.returncode,
        'stdout': (p.stdout or '').strip(),
        'stderr': (p.stderr or '').strip(),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description='Run certified-intake promotion pipeline')
    p.add_argument('--apply', action='store_true', help='Apply certified suggestions to override CSV')
    p.add_argument('--acknowledge', default='', help='Required only with --apply')
    return p.parse_args()


def read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def main() -> None:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    steps = []
    failed = False

    for label, cmd in [
        ('validate_tracker', ['python3', str(VALIDATOR)]),
        ('generate_suggestions', ['python3', str(SUGGEST)]),
    ]:
        s = run_step(label, cmd)
        steps.append(s)
        if s['returncode'] != 0:
            failed = True
            break

    apply_result = None
    if not failed and args.apply:
        if not args.acknowledge:
            failed = True
            apply_result = {
                'label': 'apply_suggestions',
                'cmd': ['python3', str(APPLY), '--acknowledge', '<missing>'],
                'returncode': 2,
                'stdout': '',
                'stderr': 'Missing --acknowledge for --apply run.',
            }
            steps.append(apply_result)
        else:
            apply_result = run_step(
                'apply_suggestions',
                ['python3', str(APPLY), '--acknowledge', args.acknowledge],
            )
            steps.append(apply_result)
            if apply_result['returncode'] != 0:
                failed = True

    if not failed:
        for label, cmd in [
            ('recompute_formal_artifacts', ['python3', str(GEN)]),
            ('recompute_proof_map', ['python3', str(PROOF)]),
            ('recompute_grounding_gap', ['python3', str(GAP)]),
            ('recompute_readiness_dashboard', ['python3', str(DASH)]),
        ]:
            s = run_step(label, cmd)
            steps.append(s)
            if s['returncode'] != 0:
                failed = True
                break

    suggestions = read_json(SUGGESTIONS_JSON)
    report = read_json(REPORT_JSON)
    fos = report.get('fact_override_summary', {}) if isinstance(report, dict) else {}
    strict = report.get('modes', {}).get('strict', {}) if isinstance(report, dict) else {}

    summary = {
        'generated_at': str(date.today()),
        'apply_requested': bool(args.apply),
        'success': not failed,
        'steps': [
            {
                'label': s['label'],
                'returncode': s['returncode'],
                'stderr': s['stderr'],
                'stdout': s['stdout'],
            }
            for s in steps
        ],
        'suggestion_count': suggestions.get('suggestion_count', 0),
        'suggestion_warning_count': suggestions.get('warning_count', 0),
        'override_summary': {
            'rows_read': fos.get('rows_read', 0),
            'applied_count': fos.get('applied_count', 0),
            'applied_status_or_value_changes': fos.get('applied_status_or_value_changes', 0),
            'applied_source_changes': fos.get('applied_source_changes', 0),
            'skipped_count': fos.get('skipped_count', 0),
        },
        'strict_counts': {
            'active': len(strict.get('active_rules', [])),
            'unresolved': len(strict.get('unresolved_rules', [])),
            'inactive': len(strict.get('inactive_rules', [])),
        },
    }

    j = OUT / 'certified_intake_promotion_pipeline_status_2026-04-07.json'
    m = OUT / 'certified_intake_promotion_pipeline_status_2026-04-07.md'

    j.write_text(json.dumps(summary, indent=2), encoding='utf-8')

    lines = [
        '# Certified Intake Promotion Pipeline Status',
        '',
        f"Generated: {summary['generated_at']}",
        f"Apply requested: {summary['apply_requested']}",
        f"Success: {summary['success']}",
        '',
        '## Suggestions',
        f"- suggestion_count: {summary['suggestion_count']}",
        f"- warning_count: {summary['suggestion_warning_count']}",
        '',
        '## Override summary',
        f"- rows_read: {summary['override_summary']['rows_read']}",
        f"- applied_count: {summary['override_summary']['applied_count']}",
        f"- applied_status_or_value_changes: {summary['override_summary']['applied_status_or_value_changes']}",
        f"- applied_source_changes: {summary['override_summary']['applied_source_changes']}",
        f"- skipped_count: {summary['override_summary']['skipped_count']}",
        '',
        '## Strict counts',
        f"- active: {summary['strict_counts']['active']}",
        f"- unresolved: {summary['strict_counts']['unresolved']}",
        f"- inactive: {summary['strict_counts']['inactive']}",
        '',
        '## Step results',
    ]
    for s in summary['steps']:
        lines.append(f"- {s['label']}: returncode={s['returncode']}")
        if s.get('stderr'):
            lines.append(f"- stderr: {s['stderr']}")
    lines.append('')
    m.write_text('\n'.join(lines), encoding='utf-8')

    print(f"Wrote: {j}")
    print(f"Wrote: {m}")

    if failed:
        sys.exit(1)


if __name__ == '__main__':
    main()
