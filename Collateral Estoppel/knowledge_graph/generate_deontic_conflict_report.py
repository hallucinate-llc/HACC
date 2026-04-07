#!/usr/bin/env python3
"""Detect deontic modality conflicts in active rule outputs."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List, Tuple

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
REPORT = ROOT / 'deontic_reasoning_report.json'
OUT_JSON = ROOT / 'deontic_conflict_report_2026-04-07.json'
OUT_MD = ROOT / 'deontic_conflict_report_2026-04-07.md'


def key(c: Dict[str, object]) -> Tuple[str, str, str]:
    return (str(c.get('actor', '')), str(c.get('action', '')), str(c.get('target', '')))


def analyze_mode(mode_block: Dict[str, object]) -> Dict[str, object]:
    grouped: Dict[Tuple[str, str, str], List[Dict[str, object]]] = {}

    for r in mode_block.get('active_rules', []):
        c = r.get('conclusion', {})
        k = key(c)
        grouped.setdefault(k, []).append(
            {
                'rule_id': r.get('rule_id'),
                'modality': c.get('modality'),
                'activation_date_estimate': r.get('activation_date_estimate'),
                'track': r.get('track'),
                'authority_refs': r.get('authority_refs', []),
            }
        )

    hard_fp = []
    hard_fo = []
    tension_op = []

    for k, rows in grouped.items():
        mods = {str(x.get('modality')) for x in rows}
        payload = {
            'actor': k[0],
            'action': k[1],
            'target': k[2],
            'modalities': sorted(mods),
            'supporting_rules': rows,
        }
        if 'F' in mods and 'P' in mods:
            hard_fp.append(payload)
        if 'F' in mods and 'O' in mods:
            hard_fo.append(payload)
        if 'O' in mods and 'P' in mods:
            tension_op.append(payload)

    return {
        'active_rule_count': len(mode_block.get('active_rules', [])),
        'hard_conflict_FP': hard_fp,
        'hard_conflict_FO': hard_fo,
        'tension_OP': tension_op,
        'conflict_counts': {
            'hard_conflict_FP': len(hard_fp),
            'hard_conflict_FO': len(hard_fo),
            'tension_OP': len(tension_op),
        },
    }


def main() -> None:
    report = json.loads(REPORT.read_text(encoding='utf-8'))

    out = {
        'generated_at': str(date.today()),
        'modes': {
            'strict': analyze_mode(report['modes']['strict']),
            'inclusive': analyze_mode(report['modes']['inclusive']),
        },
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Deontic Conflict Report - 2026-04-07')
    lines.append('')

    for mode in ('strict', 'inclusive'):
        m = out['modes'][mode]
        lines.append(f'## Mode: {mode}')
        lines.append(f"- Active rules: {m['active_rule_count']}")
        cc = m['conflict_counts']
        lines.append(f"- Hard F/P conflicts: {cc['hard_conflict_FP']}")
        lines.append(f"- Hard F/O conflicts: {cc['hard_conflict_FO']}")
        lines.append(f"- O/P tensions: {cc['tension_OP']}")

        if cc['hard_conflict_FP'] == 0 and cc['hard_conflict_FO'] == 0 and cc['tension_OP'] == 0:
            lines.append('- No modality conflicts detected among active rules.')
            lines.append('')
            continue

        if m['hard_conflict_FP']:
            lines.append('- Hard F/P conflicts:')
            for c in m['hard_conflict_FP']:
                lines.append(f"- {c['actor']} :: {c['action']} :: {c['target']} :: {c['modalities']}")
        if m['hard_conflict_FO']:
            lines.append('- Hard F/O conflicts:')
            for c in m['hard_conflict_FO']:
                lines.append(f"- {c['actor']} :: {c['action']} :: {c['target']} :: {c['modalities']}")
        if m['tension_OP']:
            lines.append('- O/P tensions:')
            for c in m['tension_OP']:
                lines.append(f"- {c['actor']} :: {c['action']} :: {c['target']} :: {c['modalities']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
