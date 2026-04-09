#!/usr/bin/env python3
"""Run what-if certified promotion scenarios (non-destructive)."""

from __future__ import annotations

import csv
from datetime import date
import json
from pathlib import Path
import subprocess

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OVERRIDES = ROOT / 'evidence_fact_overrides_2026-04-07.csv'
GENERATOR = ROOT / 'generate_formal_reasoning_artifacts.py'
OUT = ROOT / 'generated'
REPORT = OUT / 'deontic_reasoning_report.json'

TARGET_RULES = [
    'r1_guardian_permission_if_prior_appointment',
    'r2_target_noninterference_prohibition_if_prior_appointment',
    'r3_target_obligation_comply_or_seek_relief_if_prior_appointment',
    'r5_solomon_obligated_appear_and_answer',
    'r7_solomon_forbidden_refile_precluded_issue',
    'r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved',
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open('r', encoding='utf-8', newline='') as fh:
        return [{k: (v or '').strip() for k, v in row.items()} for row in csv.DictReader(fh)]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    fields = ['fact_id', 'override_status', 'override_value', 'override_source', 'override_date', 'note']
    with path.open('w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for r in rows:
            w.writerow({k: (r.get(k, '') or '').strip() for k in fields})


def upsert(rows: list[dict[str, str]], fact_id: str, status: str, value: str, note: str) -> None:
    found = None
    for r in rows:
        if (r.get('fact_id') or '').strip() == fact_id:
            found = r
            break
    if found is None:
        found = {'fact_id': fact_id}
        rows.append(found)
    found['override_status'] = status
    found['override_value'] = value
    found['override_source'] = '/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/SIMULATED_CERTIFIED_SOURCE.pdf'
    found['override_date'] = str(date.today())
    found['note'] = note


def run_generator() -> None:
    p = subprocess.run(['python3', str(GENERATOR)], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError(f'Generator failed: {p.stderr or p.stdout}')


def snapshot() -> dict[str, object]:
    obj = json.loads(REPORT.read_text(encoding='utf-8'))
    strict = obj['modes']['strict']
    active = {x['rule_id'] for x in strict['active_rules']}
    unresolved = {x['rule_id'] for x in strict['unresolved_rules']}
    inactive = {x['rule_id'] for x in strict['inactive_rules']}
    return {
        'strict_counts': {
            'active': len(active),
            'unresolved': len(unresolved),
            'inactive': len(inactive),
        },
        'target_rule_states': {
            rid: ('active' if rid in active else 'unresolved' if rid in unresolved else 'inactive' if rid in inactive else 'missing')
            for rid in TARGET_RULES
        },
    }


def main() -> None:
    original = OVERRIDES.read_text(encoding='utf-8')
    base_rows = read_csv(OVERRIDES)

    scenarios = [
        {
            'scenario_id': 'baseline_current_overrides',
            'promotions': [],
        },
        {
            'scenario_id': 'promote_nonappearance_only',
            'promotions': [
                ('f_client_solomon_failed_appearance', 'verified', 'true', 'Simulated certified nonappearance packet.'),
            ],
        },
        {
            'scenario_id': 'promote_issue_preclusion_pair',
            'promotions': [
                ('f_collateral_estoppel_candidate', 'verified', 'true', 'Simulated certified issue-preclusion mapping.'),
                ('f_client_solomon_barred_refile', 'verified', 'true', 'Simulated certified barred-refile record.'),
            ],
        },
        {
            'scenario_id': 'promote_prior_appointment_cluster',
            'promotions': [
                ('f_client_prior_appointment', 'verified', 'true', 'Simulated certified prior appointment order.'),
                ('f_client_solomon_housing_interference', 'verified', 'true', 'Simulated certified interference chain.'),
                ('f_client_solomon_order_disregard', 'verified', 'true', 'Simulated certified disregard findings.'),
            ],
        },
        {
            'scenario_id': 'promote_all_top_blockers',
            'promotions': [
                ('f_client_solomon_failed_appearance', 'verified', 'true', 'Simulated certified nonappearance packet.'),
                ('f_collateral_estoppel_candidate', 'verified', 'true', 'Simulated certified issue-preclusion mapping.'),
                ('f_client_solomon_barred_refile', 'verified', 'true', 'Simulated certified barred-refile record.'),
                ('f_client_prior_appointment', 'verified', 'true', 'Simulated certified prior appointment order.'),
                ('f_client_solomon_housing_interference', 'verified', 'true', 'Simulated certified interference chain.'),
                ('f_client_solomon_order_disregard', 'verified', 'true', 'Simulated certified disregard findings.'),
            ],
        },
    ]

    out = {
        'generated_at': str(date.today()),
        'target_rules': TARGET_RULES,
        'scenarios': [],
    }

    try:
        for s in scenarios:
            rows = [dict(r) for r in base_rows]
            for fid, st, val, note in s['promotions']:
                upsert(rows, fid, st, val, note)
            write_csv(OVERRIDES, rows)
            run_generator()
            snap = snapshot()
            out['scenarios'].append(
                {
                    'scenario_id': s['scenario_id'],
                    'promotion_count': len(s['promotions']),
                    'promoted_fact_ids': [x[0] for x in s['promotions']],
                    **snap,
                }
            )
    finally:
        OVERRIDES.write_text(original, encoding='utf-8')
        run_generator()

    j = OUT / 'certified_promotion_what_if_scenarios_2026-04-07.json'
    m = OUT / 'certified_promotion_what_if_scenarios_2026-04-07.md'
    j.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = [
        '# Certified Promotion What-If Scenarios',
        '',
        f"Generated: {out['generated_at']}",
        '',
    ]
    for s in out['scenarios']:
        c = s['strict_counts']
        lines.append(f"## {s['scenario_id']}")
        lines.append(f"- promotions: {s['promotion_count']} ({', '.join(s['promoted_fact_ids']) or 'none'})")
        lines.append(f"- strict counts: active={c['active']} unresolved={c['unresolved']} inactive={c['inactive']}")
        lines.append('- target rules:')
        for rid, state in s['target_rule_states'].items():
            lines.append(f"- {rid}: {state}")
        lines.append('')

    m.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
