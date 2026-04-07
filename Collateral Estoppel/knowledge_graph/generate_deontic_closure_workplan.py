#!/usr/bin/env python3
"""Generate prioritized deontic closure workplan from current reasoning outputs."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

GEN = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
REPORT = GEN / 'deontic_reasoning_report.json'
OUT_JSON = GEN / 'deontic_closure_workplan_2026-04-07.json'
OUT_MD = GEN / 'deontic_closure_workplan_2026-04-07.md'


def classify_rule(rule_id: str) -> Dict[str, str]:
    # Targeted closure strategy per remaining gap class.
    if rule_id in {'r17_responding_custodian_obligated_execute_or_query_protocol_upon_service'}:
        return {
            'priority': 'high',
            'closure_type': 'service_event',
            'action': 'Log first confirmed service event in active service log (status/date/method/person served/production due).',
            'expected_effect': 'r17 becomes active.',
        }
    if rule_id in {'r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response'}:
        return {
            'priority': 'high',
            'closure_type': 'response_timing_or_deficiency',
            'action': 'Log true incomplete-response trigger (overdue production, missing required artifacts after production, or deficiency stage).',
            'expected_effect': 'r18 becomes active.',
        }
    if rule_id in {'r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage'}:
        return {
            'priority': 'high',
            'closure_type': 'deficiency_notice_event',
            'action': 'Log deficiency notice sent/date (or deficiency stage status).',
            'expected_effect': 'r19 becomes active.',
        }
    if rule_id in {'r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved'}:
        return {
            'priority': 'high',
            'closure_type': 'certified_nonappearance_record',
            'action': 'Add certified hearing register/minute entry and service/order-to-appear record proving nonappearance.',
            'expected_effect': 'r24 moves from unresolved to active in strict mode.',
        }
    if rule_id in {'r7_solomon_forbidden_refile_precluded_issue'}:
        return {
            'priority': 'high',
            'closure_type': 'issue_preclusion_proof_packet',
            'action': 'Add certified prior final order/judgment, identity-of-issue comparison, and full/fair opportunity record.',
            'expected_effect': 'r7 moves from unresolved to active in strict mode.',
        }
    if rule_id in {'r1_guardian_permission_if_prior_appointment', 'r2_noninterference_prohibition_for_benjamin', 'r3_benjamin_obligation_comply_or_seek_relief'}:
        return {
            'priority': 'medium',
            'closure_type': 'prior_appointment_proof',
            'action': 'Add certified prior guardianship appointment order and supporting service/compliance records.',
            'expected_effect': 'r1-r3 move from unresolved to active in strict mode (if all antecedents verified).',
        }
    if rule_id in {'r5_solomon_obligated_appear_and_answer'}:
        return {
            'priority': 'medium',
            'closure_type': 'nonappearance_proof',
            'action': 'Add certified record proving failure to appear in related hearing context.',
            'expected_effect': 'r5 moves from unresolved to active in strict mode.',
        }
    if rule_id in {'r22_case_obligated_finalize_authority_citations_before_filing'}:
        return {
            'priority': 'low',
            'closure_type': 'predicate_state_confirmation',
            'action': 'If authority placeholders are now resolved, keep r22 inactive by design; if placeholders reappear, update source file and regenerate.',
            'expected_effect': 'Maintains accurate filing-readiness signal.',
        }
    return {
        'priority': 'medium',
        'closure_type': 'manual_review',
        'action': 'Manual evidentiary and authority review required.',
        'expected_effect': 'Rule-state clarification.',
    }


def mode_block(name: str, rules: List[Dict[str, object]], cls: str) -> List[Dict[str, object]]:
    out = []
    for r in rules:
        rid = str(r.get('rule_id'))
        plan = classify_rule(rid)
        out.append(
            {
                'mode': name,
                'classification': cls,
                'rule_id': rid,
                'track': r.get('track'),
                'authority_refs': r.get('authority_refs', []),
                'activation_date_estimate': r.get('activation_date_estimate'),
                'plan': plan,
                'antecedents': r.get('antecedents', []),
            }
        )
    return out


def main() -> None:
    report = json.loads(REPORT.read_text(encoding='utf-8'))

    strict_unresolved = report['modes']['strict'].get('unresolved_rules', [])
    strict_inactive = report['modes']['strict'].get('inactive_rules', [])

    entries = []
    entries.extend(mode_block('strict', strict_unresolved, 'unresolved'))
    entries.extend(mode_block('strict', strict_inactive, 'inactive'))

    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    entries.sort(key=lambda x: (priority_order.get(x['plan']['priority'], 9), x['classification'], x['rule_id']))

    workplan = {
        'generated_at': str(date.today()),
        'summary': {
            'strict_active_count': len(report['modes']['strict'].get('active_rules', [])),
            'strict_unresolved_count': len(strict_unresolved),
            'strict_inactive_count': len(strict_inactive),
            'closure_items': len(entries),
        },
        'execution_sequence': [
            '1) Confirm and log first subpoena service event to activate r17.',
            '2) Monitor due dates and log true incomplete-response trigger to activate r18.',
            '3) Issue and log deficiency notice to activate r19 when criteria are met.',
            '4) Assemble certified nonappearance packet for r24.',
            '5) Assemble certified issue-preclusion packet for r7.',
            '6) Convert remaining hypothesis-track antecedents from alleged/theory to verified as records are obtained.',
        ],
        'items': entries,
    }

    OUT_JSON.write_text(json.dumps(workplan, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Deontic Closure Workplan - 2026-04-07')
    lines.append('')
    s = workplan['summary']
    lines.append('## Summary')
    lines.append(f"- Strict active: {s['strict_active_count']}")
    lines.append(f"- Strict unresolved: {s['strict_unresolved_count']}")
    lines.append(f"- Strict inactive: {s['strict_inactive_count']}")
    lines.append(f"- Closure items: {s['closure_items']}")
    lines.append('')

    lines.append('## Execution Sequence')
    for step in workplan['execution_sequence']:
        lines.append(f'- {step}')
    lines.append('')

    lines.append('## Prioritized Rule Closure Items')
    current = None
    for item in entries:
        p = item['plan']['priority']
        if p != current:
            current = p
            lines.append(f'### Priority: {p}')
        lines.append(f"- [{item['classification']}] {item['rule_id']} ({item['track']})")
        lines.append(f"- Action: {item['plan']['action']}")
        lines.append(f"- Expected effect: {item['plan']['expected_effect']}")
        auth = ', '.join(item.get('authority_refs', [])) or 'none'
        lines.append(f"- Authority refs: {auth}")
    lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
