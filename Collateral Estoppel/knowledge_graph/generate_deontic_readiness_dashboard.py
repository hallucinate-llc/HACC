#!/usr/bin/env python3
"""Generate consolidated deontic readiness dashboard from generated artifacts."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

GEN = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
OUT_JSON = GEN / 'deontic_readiness_dashboard_2026-04-07.json'
OUT_MD = GEN / 'deontic_readiness_dashboard_2026-04-07.md'


def load(name: str) -> Dict[str, object]:
    return json.loads((GEN / name).read_text(encoding='utf-8'))


def main() -> None:
    report = load('deontic_reasoning_report.json')
    grounding = load('deontic_end_to_end_grounding_gap_report_2026-04-07.json')
    conflicts = load('deontic_conflict_report_2026-04-07.json')
    workplan = load('deontic_closure_workplan_2026-04-07.json')
    scenarios = load('service_activation_scenarios_2026-04-07.json')

    strict = report['modes']['strict']
    inclusive = report['modes']['inclusive']

    top_high = [x for x in workplan.get('items', []) if x.get('plan', {}).get('priority') == 'high']
    top_medium = [x for x in workplan.get('items', []) if x.get('plan', {}).get('priority') == 'medium']

    dashboard = {
        'generated_at': str(date.today()),
        'scoreboard': {
            'strict': {
                'active': len(strict.get('active_rules', [])),
                'unresolved': len(strict.get('unresolved_rules', [])),
                'inactive': len(strict.get('inactive_rules', [])),
            },
            'inclusive': {
                'active': len(inclusive.get('active_rules', [])),
                'unresolved': len(inclusive.get('unresolved_rules', [])),
                'inactive': len(inclusive.get('inactive_rules', [])),
            },
            'non_hypothesis_authority_ref_gaps': len(grounding.get('authority_linkage', {}).get('non_hypothesis_rules_without_authority_refs', [])),
            'active_modality_conflicts_strict': conflicts.get('modes', {}).get('strict', {}).get('conflict_counts', {}),
            'active_modality_conflicts_inclusive': conflicts.get('modes', {}).get('inclusive', {}).get('conflict_counts', {}),
        },
        'service_workflow_projection': {
            'baseline': scenarios.get('baseline_expected_rule_state', {}),
            'first_service_projection': (scenarios.get('scenarios') or [{}])[0].get('scenario_service_only', {}).get('expected_rule_state', {}),
            'service_plus_deficiency_projection': (scenarios.get('scenarios') or [{}])[0].get('scenario_with_deficiency_notice', {}).get('expected_rule_state', {}),
        },
        'top_priority_closure_items': top_high,
        'secondary_priority_closure_items': top_medium,
        'strict_unresolved_rule_ids': [x.get('rule_id') for x in strict.get('unresolved_rules', [])],
        'strict_inactive_rule_ids': [x.get('rule_id') for x in strict.get('inactive_rules', [])],
    }

    OUT_JSON.write_text(json.dumps(dashboard, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Deontic Readiness Dashboard - 2026-04-07')
    lines.append('')
    s = dashboard['scoreboard']
    lines.append('## Scoreboard')
    lines.append(f"- Strict: active={s['strict']['active']} unresolved={s['strict']['unresolved']} inactive={s['strict']['inactive']}")
    lines.append(f"- Inclusive: active={s['inclusive']['active']} unresolved={s['inclusive']['unresolved']} inactive={s['inclusive']['inactive']}")
    lines.append(f"- Non-hypothesis authority-ref gaps: {s['non_hypothesis_authority_ref_gaps']}")
    c1 = s['active_modality_conflicts_strict']
    c2 = s['active_modality_conflicts_inclusive']
    lines.append(f"- Strict modality conflicts: F/P={c1.get('hard_conflict_FP', 0)} F/O={c1.get('hard_conflict_FO', 0)} O/P={c1.get('tension_OP', 0)}")
    lines.append(f"- Inclusive modality conflicts: F/P={c2.get('hard_conflict_FP', 0)} F/O={c2.get('hard_conflict_FO', 0)} O/P={c2.get('tension_OP', 0)}")
    lines.append('')

    lines.append('## Service Workflow Projection')
    p = dashboard['service_workflow_projection']
    b = p.get('baseline', {})
    f = p.get('first_service_projection', {})
    d = p.get('service_plus_deficiency_projection', {})
    lines.append(f"- Baseline: r17={b.get('r17')} r18={b.get('r18')} r19={b.get('r19')}")
    lines.append(f"- First confirmed service: r17={f.get('r17')} r18={f.get('r18')} r19={f.get('r19')}")
    lines.append(f"- Service + deficiency logged: r17={d.get('r17')} r18={d.get('r18')} r19={d.get('r19')}")
    lines.append('')

    lines.append('## Highest-Priority Closures')
    for item in dashboard['top_priority_closure_items']:
        lines.append(f"- {item['rule_id']} [{item['classification']}]: {item['plan']['action']}")
    lines.append('')

    lines.append('## Remaining Strict Blockers')
    lines.append('- Unresolved:')
    for rid in dashboard['strict_unresolved_rule_ids']:
        lines.append(f'- {rid}')
    lines.append('- Inactive:')
    for rid in dashboard['strict_inactive_rule_ids']:
        lines.append(f'- {rid}')
    lines.append('')

    lines.append('## Suggested Immediate Execution')
    lines.append('- 1) Log one confirmed service event to activate r17.')
    lines.append('- 2) Keep r18 inactive until true incomplete trigger occurs (overdue or deficiency evidence).')
    lines.append('- 3) Add certified nonappearance record (r24) and certified issue-preclusion packet (r7).')

    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
