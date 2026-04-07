#!/usr/bin/env python3
"""Generate certification packet manifests from strict unresolved blockers."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OUT = ROOT / 'generated'
REPORT = OUT / 'deontic_reasoning_report.json'


def main() -> None:
    if not REPORT.exists():
        raise SystemExit(f'Missing report: {REPORT}')

    obj = json.loads(REPORT.read_text(encoding='utf-8'))
    strict_unresolved = obj.get('modes', {}).get('strict', {}).get('unresolved_rules', [])

    packet_defs = {
        'packet_nonappearance_r24': {
            'label': 'Certified Nonappearance Packet',
            'target_fact_ids': ['f_client_solomon_failed_appearance'],
            'required_record_types': [
                'certified hearing register/minute entry for relevant hearing date',
                'certified order-to-appear or hearing setting record',
                'identity tie-in showing entry pertains to Solomon Barber',
            ],
            'suggested_filenames': [
                'hearing__26PR00641__YYYYMMDD__nonappearance_minutes.pdf',
                'hearing__26PR00641__YYYYMMDD__order_to_appear.pdf',
                'docket__26PR00641__YYYYMMDD__appearance_register_extract.pdf',
            ],
            'expected_rule_unlocks': [
                'r5_solomon_obligated_appear_and_answer',
                'r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved',
            ],
        },
        'packet_issue_preclusion_r7': {
            'label': 'Certified Issue-Preclusion Packet',
            'target_fact_ids': ['f_collateral_estoppel_candidate', 'f_client_solomon_barred_refile'],
            'required_record_types': [
                'certified prior final order/judgment from separate proceeding',
                'certified register/docket for prior proceeding',
                'certified hearing/appearance material showing full and fair opportunity',
                'later filing copy and issue-identity comparison chart',
                'completed issue_preclusion_mapping.json entries',
            ],
            'suggested_filenames': [
                'prior_order__26PR00641__YYYYMMDD__prior_final_order.pdf',
                'docket__26PR00641__YYYYMMDD__register_of_actions.pdf',
                'hearing__26PR00641__YYYYMMDD__appearance_minutes_or_transcript.pdf',
                'other_certified__26PR00641__YYYYMMDD__issue_identity_chart.pdf',
            ],
            'expected_rule_unlocks': [
                'r7_solomon_forbidden_refile_precluded_issue',
            ],
        },
        'packet_prior_appointment_r1_r2_r3': {
            'label': 'Certified Prior-Appointment Cluster Packet',
            'target_fact_ids': [
                'f_client_prior_appointment',
                'f_client_benjamin_housing_interference',
                'f_client_benjamin_order_disregard',
            ],
            'required_record_types': [
                'certified appointment/authority order naming Benjamin Barber (if it exists)',
                'certified docket entry showing appointment effective date/status',
                'authenticated communications/records tying interference conduct to housing contract effects',
                'certified or authenticated noncompliance/disregard records tied to order context',
            ],
            'suggested_filenames': [
                'appointment__26PR00641__YYYYMMDD__appointment_order_benjamin_barber.pdf',
                'docket__26PR00641__YYYYMMDD__appointment_status_extract.pdf',
                'other_certified__26PR00641__YYYYMMDD__housing_interference_record.pdf',
                'enforcement__26PR00641__YYYYMMDD__order_disregard_record.pdf',
            ],
            'expected_rule_unlocks': [
                'r1_guardian_permission_if_prior_appointment',
                'r2_noninterference_prohibition_for_benjamin',
                'r3_benjamin_obligation_comply_or_seek_relief',
            ],
        },
    }

    unresolved_rule_ids = {r.get('rule_id', '') for r in strict_unresolved}
    fact_to_rules: dict[str, list[str]] = {}
    for r in strict_unresolved:
        rid = r.get('rule_id', '')
        for ant in r.get('antecedents', []):
            fid = ant.get('fact_id', '')
            if not fid:
                continue
            fact_to_rules.setdefault(fid, []).append(rid)

    manifests = []
    for pid, meta in packet_defs.items():
        facts = list(meta['target_fact_ids'])
        blocking_rules = sorted({rid for f in facts for rid in fact_to_rules.get(f, []) if rid in unresolved_rule_ids})
        manifests.append(
            {
                'packet_id': pid,
                'label': meta['label'],
                'target_fact_ids': facts,
                'blocking_rules': blocking_rules,
                'required_record_types': meta['required_record_types'],
                'suggested_filenames': meta['suggested_filenames'],
                'expected_rule_unlocks': meta['expected_rule_unlocks'],
            }
        )

    out = {
        'generated_at': str(date.today()),
        'strict_unresolved_rule_count': len(strict_unresolved),
        'packet_manifests': manifests,
    }

    j = OUT / 'certification_packet_manifests_2026-04-07.json'
    m = OUT / 'certification_packet_manifests_2026-04-07.md'
    j.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines = [
        '# Certification Packet Manifests',
        '',
        f"Generated: {out['generated_at']}",
        f"Strict unresolved rules: {out['strict_unresolved_rule_count']}",
        '',
    ]

    for p in manifests:
        lines.append(f"## {p['packet_id']} - {p['label']}")
        lines.append(f"- Target facts: {', '.join(p['target_fact_ids'])}")
        lines.append(f"- Currently blocking rules: {', '.join(p['blocking_rules']) or 'none'}")
        lines.append(f"- Expected rule unlocks: {', '.join(p['expected_rule_unlocks'])}")
        lines.append('- Required record types:')
        for r in p['required_record_types']:
            lines.append(f"- {r}")
        lines.append('- Suggested filenames:')
        for f in p['suggested_filenames']:
            lines.append(f"- {f}")
        lines.append('')

    m.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
