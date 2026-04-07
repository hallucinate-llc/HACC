#!/usr/bin/env python3
"""Generate non-destructive service activation scenarios for r17-r19.

This tool does not edit the active service log.
It simulates minimal confirmed updates and reports expected rule-state changes.
"""

from __future__ import annotations

import csv
import json
from datetime import date
from datetime import timedelta
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
ACTIVE_LOG = ROOT / 'drafts/final_filing_set/28_active_service_log_2026-04-07.csv'
OUT_DIR = ROOT / 'knowledge_graph/generated'

OUT_JSON = OUT_DIR / 'service_activation_scenarios_2026-04-07.json'
OUT_MD = OUT_DIR / 'service_activation_scenarios_2026-04-07.md'


def load_rows() -> List[Dict[str, str]]:
    if not ACTIVE_LOG.exists():
        return []
    with ACTIVE_LOG.open('r', encoding='utf-8', newline='') as fh:
        return [{k: (v or '').strip() for k, v in row.items()} for row in csv.DictReader(fh)]


def derive_flags(rows: List[Dict[str, str]]) -> Dict[str, bool]:
    served_any = False
    incomplete_any = False
    deficiency_any = False

    for row in rows:
        status = (row.get('status') or '').strip().lower()
        date_served = bool((row.get('date_served') or '').strip())
        production_due = (row.get('production_due') or '').strip()
        production_received = bool((row.get('date_production_received') or '').strip())
        deficiency_sent = bool((row.get('deficiency_notice_sent') or '').strip())
        checklist = (row.get('checklist_received') or '').strip().lower()
        search_report = (row.get('search_report_received') or '').strip().lower()
        overdue_after_service = bool(date_served and production_due and production_due < str(date.today()))
        artifacts_missing = checklist in {'', 'n', 'no', 'false'} or search_report in {'', 'n', 'no', 'false'}

        row_served = status in {'served', 'awaiting_production', 'production_received', 'deficiency_notice_stage', 'motion_to_compel_stage'} or date_served
        row_incomplete = status in {'deficiency_notice_stage', 'motion_to_compel_stage'} or (status == 'production_received' and artifacts_missing) or (overdue_after_service and (not production_received or artifacts_missing))
        row_def = status in {'deficiency_notice_stage', 'motion_to_compel_stage'} or deficiency_sent

        served_any = served_any or row_served
        incomplete_any = incomplete_any or row_incomplete
        deficiency_any = deficiency_any or row_def

    return {
        'f_subpoena_service_completed_any': served_any,
        'f_subpoena_response_incomplete_any': incomplete_any,
        'f_deficiency_notice_sent_any': deficiency_any,
    }


def scenario_first_service(rows: List[Dict[str, str]], idx: int) -> List[Dict[str, str]]:
    cloned = [dict(r) for r in rows]
    r = cloned[idx]
    r['status'] = 'awaiting_production'
    r['date_served'] = str(date.today())
    if not r.get('production_due'):
        # Keep due date in the future so service-only scenario does not auto-trigger deficiency logic.
        r['production_due'] = str(date.today() + timedelta(days=7))
    if not r.get('service_method'):
        r['service_method'] = 'TO_BE_FILLED_CONFIRMED_METHOD'
    if not r.get('person_served'):
        r['person_served'] = 'TO_BE_FILLED_CONFIRMED_PERSON'
    return cloned


def scenario_deficiency(rows: List[Dict[str, str]], idx: int) -> List[Dict[str, str]]:
    cloned = scenario_first_service(rows, idx)
    r = cloned[idx]
    r['status'] = 'deficiency_notice_stage'
    r['deficiency_notice_sent'] = str(date.today())
    r['checklist_received'] = 'N'
    r['search_report_received'] = 'N'
    return cloned


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows()

    baseline = derive_flags(rows)

    scenarios = []
    for i, row in enumerate(rows):
        recipient = row.get('recipient', f'row_{i+1}')

        s1_rows = scenario_first_service(rows, i)
        s1 = derive_flags(s1_rows)

        s2_rows = scenario_deficiency(rows, i)
        s2 = derive_flags(s2_rows)

        scenarios.append(
            {
                'recipient': recipient,
                'scenario_service_only': {
                    'derived_flags': s1,
                    'expected_rule_state': {
                        'r17': 'active' if s1['f_subpoena_service_completed_any'] else 'inactive',
                        'r18': 'active' if s1['f_subpoena_response_incomplete_any'] else 'inactive',
                        'r19': 'active' if s1['f_deficiency_notice_sent_any'] else 'inactive',
                    },
                },
                'scenario_with_deficiency_notice': {
                    'derived_flags': s2,
                    'expected_rule_state': {
                        'r17': 'active' if s2['f_subpoena_service_completed_any'] else 'inactive',
                        'r18': 'active' if s2['f_subpoena_response_incomplete_any'] else 'inactive',
                        'r19': 'active' if s2['f_deficiency_notice_sent_any'] else 'inactive',
                    },
                },
            }
        )

    out = {
        'generated_at': str(date.today()),
        'source_log': str(ACTIVE_LOG),
        'baseline_derived_flags': baseline,
        'baseline_expected_rule_state': {
            'r17': 'active' if baseline['f_subpoena_service_completed_any'] else 'inactive',
            'r18': 'active' if baseline['f_subpoena_response_incomplete_any'] else 'inactive',
            'r19': 'active' if baseline['f_deficiency_notice_sent_any'] else 'inactive',
        },
        'scenarios': scenarios,
        'note': 'Simulation only. No service log rows were modified.',
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = []
    lines.append('# Service Activation Scenarios - 2026-04-07')
    lines.append('')
    lines.append(f"Source log: `{ACTIVE_LOG}`")
    lines.append('')
    lines.append('## Baseline')
    lines.append(f"- r17: {out['baseline_expected_rule_state']['r17']}")
    lines.append(f"- r18: {out['baseline_expected_rule_state']['r18']}")
    lines.append(f"- r19: {out['baseline_expected_rule_state']['r19']}")
    lines.append('')
    lines.append('## Recipient Scenarios')

    for s in scenarios:
        lines.append(f"### {s['recipient']}")
        a = s['scenario_service_only']['expected_rule_state']
        b = s['scenario_with_deficiency_notice']['expected_rule_state']
        lines.append('- Service-only scenario (status -> awaiting_production):')
        lines.append(f"- r17={a['r17']} r18={a['r18']} r19={a['r19']}")
        lines.append('- Service + deficiency scenario:')
        lines.append(f"- r17={b['r17']} r18={b['r18']} r19={b['r19']}")
        lines.append('')

    lines.append('## Interpretation')
    lines.append('- Any confirmed first service event should activate r17.')
    lines.append('- r18 activates after a true incomplete-response trigger (overdue production, missing required artifacts after production, or explicit deficiency/compel stage).')
    lines.append('- r19 requires a logged deficiency notice stage/date.')
    lines.append('- This file is a projection only; update the real service log only with confirmed facts.')

    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
