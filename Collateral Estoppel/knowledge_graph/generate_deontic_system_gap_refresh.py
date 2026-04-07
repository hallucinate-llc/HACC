#!/usr/bin/env python3
"""Emit a compact system gap refresh from current deontic outputs."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OUT = ROOT / 'generated'

REPORT = OUT / 'deontic_reasoning_report.json'
GROUND = OUT / 'deontic_end_to_end_grounding_gap_report_2026-04-07.md'


def main() -> None:
    if not REPORT.exists():
        raise SystemExit(f'Missing report: {REPORT}')

    obj = json.loads(REPORT.read_text(encoding='utf-8'))
    strict = obj['modes']['strict']
    incl = obj['modes']['inclusive']

    unresolved = strict.get('unresolved_rules', [])
    inactive = strict.get('inactive_rules', [])

    unresolved_fact_gaps = []
    for r in unresolved:
        blockers = [a for a in r.get('antecedents', []) if str(a.get('status')) != 'verified' or str(a.get('value')).lower() != 'true']
        unresolved_fact_gaps.append(
            {
                'rule_id': r['rule_id'],
                'track': r.get('track'),
                'blockers': blockers,
            }
        )

    inactive_fact_gaps = []
    for r in inactive:
        blockers = [a for a in r.get('antecedents', []) if str(a.get('value')).lower() != 'true']
        inactive_fact_gaps.append(
            {
                'rule_id': r['rule_id'],
                'track': r.get('track'),
                'blockers': blockers,
            }
        )

    grounding_text = GROUND.read_text(encoding='utf-8') if GROUND.exists() else ''
    rules_without_authority_refs = None
    for line in grounding_text.splitlines():
        if line.strip().startswith('- Rules without authority refs:'):
            try:
                rules_without_authority_refs = int(line.rsplit(':', 1)[1].strip())
            except Exception:
                rules_without_authority_refs = None

    out = {
        'generated_at': str(date.today()),
        'strict_counts': {
            'active': len(strict.get('active_rules', [])),
            'unresolved': len(unresolved),
            'inactive': len(inactive),
        },
        'inclusive_counts': {
            'active': len(incl.get('active_rules', [])),
            'unresolved': len(incl.get('unresolved_rules', [])),
            'inactive': len(incl.get('inactive_rules', [])),
        },
        'law_grounding_status': {
            'rules_without_authority_refs': rules_without_authority_refs,
            'local_rule_authority_objects_present': True,
            'local_rule_workflow_rule_present': True,
        },
        'remaining_evidence_gaps': {
            'strict_unresolved': unresolved_fact_gaps,
            'strict_inactive': inactive_fact_gaps,
        },
        'priority_closure_targets': [
            'certified_nonappearance_packet_for_f_client_solomon_failed_appearance',
            'certified_issue_preclusion_packet_for_f_collateral_estoppel_candidate_and_f_client_solomon_barred_refile',
            'certified_prior_appointment_order_for_f_client_prior_appointment',
            'active_service_log_updates_to_activate_r17_r18_r19',
        ],
    }

    j = OUT / 'deontic_system_gap_refresh_2026-04-07.json'
    m = OUT / 'deontic_system_gap_refresh_2026-04-07.md'
    j.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = [
        '# Deontic System Gap Refresh',
        '',
        f"Generated: {out['generated_at']}",
        '',
        '## Counts',
        f"- Strict: active={out['strict_counts']['active']} unresolved={out['strict_counts']['unresolved']} inactive={out['strict_counts']['inactive']}",
        f"- Inclusive: active={out['inclusive_counts']['active']} unresolved={out['inclusive_counts']['unresolved']} inactive={out['inclusive_counts']['inactive']}",
        '',
        '## Law/Caselaw Grounding',
        f"- Rules without authority refs: {out['law_grounding_status']['rules_without_authority_refs']}",
        f"- Local-rule authority objects present: {out['law_grounding_status']['local_rule_authority_objects_present']}",
        f"- Local-rule workflow rule present: {out['law_grounding_status']['local_rule_workflow_rule_present']}",
        '',
        '## Remaining Evidence-Gated Gaps',
        '- Strict unresolved rules still blocked by allegation/theory predicates or unverified facts:',
    ]

    for item in unresolved_fact_gaps:
        lines.append(f"- {item['rule_id']} ({item['track']})")
        for b in item['blockers']:
            lines.append(f"- antecedent {b.get('fact_id')} status={b.get('status')} value={b.get('value')}")

    lines.append('')
    lines.append('- Strict inactive workflow rules still blocked by false antecedents:')
    for item in inactive_fact_gaps:
        lines.append(f"- {item['rule_id']} ({item['track']})")
        for b in item['blockers']:
            lines.append(f"- antecedent {b.get('fact_id')} status={b.get('status')} value={b.get('value')}")

    lines.append('')
    lines.append('## Priority Closure Targets')
    for t in out['priority_closure_targets']:
        lines.append(f"- {t}")
    lines.append('')

    m.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
