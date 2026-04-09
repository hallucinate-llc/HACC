#!/usr/bin/env python3
"""Generate rule-closure trace matrix for strict unresolved/inactive rules."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

GEN = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
REPORT = GEN / 'deontic_reasoning_report.json'
KG = GEN / 'full_case_knowledge_graph.json'
OUT_JSON = GEN / 'rule_closure_trace_matrix_2026-04-07.json'
OUT_MD = GEN / 'rule_closure_trace_matrix_2026-04-07.md'


def load(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def suggested_evidence(fact_id: str, status: str, value: str, source: str) -> str:
    if fact_id in {'f_client_solomon_failed_appearance'}:
        return 'Certified hearing register/minute entry + proof of service/order-to-appear record.'
    if fact_id in {'f_collateral_estoppel_candidate', 'f_client_solomon_barred_refile'}:
        return 'Certified prior final order/judgment + identity-of-issue chart + later filing copy.'
    if fact_id in {'f_client_prior_appointment'}:
        return 'Certified guardianship appointment order and docket extract.'
    if fact_id in {'f_client_solomon_housing_interference', 'f_client_solomon_order_disregard'}:
        return 'Authenticated communications, certified court records, and timeline corroboration.'
    if fact_id in {'f_subpoena_service_completed_any'}:
        return 'Confirmed service return entry in active service log (date/method/person served).'
    if fact_id in {'f_subpoena_response_incomplete_any'}:
        return 'Overdue production record, or production-received record with missing required artifacts, or deficiency stage entry.'
    if fact_id in {'f_deficiency_notice_sent_any'}:
        return 'Deficiency notice date/status entry in active service log.'
    if fact_id in {'f_authority_table_placeholders_unresolved'}:
        return 'No additional evidence needed if false by design; keep source table finalized.'
    if status in {'alleged', 'theory'}:
        return 'Convert to verified with certified docket/order/transcript or authenticated documentary evidence.'
    if value.lower() == 'false':
        return 'Record objective event/state transition in source log and regenerate.'
    return f'Validate and supplement source evidence ({source}) as needed.'


def main() -> None:
    report = load(REPORT)
    kg = load(KG)

    fact_nodes = {}
    for n in kg.get('nodes', []):
        if n.get('kind') == 'fact' and str(n.get('id', '')).startswith('fact:'):
            fid = str(n.get('id'))[5:]
            fact_nodes[fid] = n

    strict = report['modes']['strict']

    items: List[Dict[str, object]] = []
    for cls in ('unresolved_rules', 'inactive_rules'):
        c = 'unresolved' if cls == 'unresolved_rules' else 'inactive'
        for r in strict.get(cls, []):
            antecedents = []
            for a in r.get('antecedents', []):
                fid = str(a.get('fact_id'))
                node = fact_nodes.get(fid, {})
                status = str(a.get('status'))
                value = str(a.get('value'))
                source = str(node.get('source', ''))
                antecedents.append(
                    {
                        'fact_id': fid,
                        'predicate': node.get('predicate'),
                        'status': status,
                        'value': value,
                        'source': source,
                        'dates': a.get('dates', []),
                        'suggested_evidence_or_action': suggested_evidence(fid, status, value, source),
                    }
                )

            items.append(
                {
                    'classification': c,
                    'rule_id': r.get('rule_id'),
                    'track': r.get('track'),
                    'authority_refs': r.get('authority_refs', []),
                    'description': r.get('description'),
                    'activation_date_estimate': r.get('activation_date_estimate'),
                    'antecedent_trace': antecedents,
                }
            )

    out = {
        'generated_at': str(date.today()),
        'strict_counts': {
            'active': len(strict.get('active_rules', [])),
            'unresolved': len(strict.get('unresolved_rules', [])),
            'inactive': len(strict.get('inactive_rules', [])),
        },
        'items': items,
    }

    OUT_JSON.write_text(json.dumps(out, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Rule Closure Trace Matrix - 2026-04-07')
    lines.append('')
    s = out['strict_counts']
    lines.append(f"Strict counts: active={s['active']} unresolved={s['unresolved']} inactive={s['inactive']}")
    lines.append('')

    for it in items:
        lines.append(f"## [{it['classification']}] {it['rule_id']} ({it['track']})")
        lines.append(f"- Authority refs: {', '.join(it['authority_refs']) if it['authority_refs'] else 'none'}")
        lines.append(f"- Description: {it['description']}")
        lines.append(f"- Activation estimate: {it.get('activation_date_estimate')}")
        lines.append('- Antecedent trace:')
        for a in it['antecedent_trace']:
            lines.append(f"- {a['fact_id']} :: {a['predicate']} :: status={a['status']} value={a['value']} source={a['source']}")
            lines.append(f"- Action: {a['suggested_evidence_or_action']}")
        lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
