#!/usr/bin/env python3
"""Generate proof-intake checklist from current deontic reasoning outputs.

Outputs:
- knowledge_graph/generated/proof_intake_map_2026-04-07.json
- knowledge_graph/generated/proof_intake_map_2026-04-07.md
"""

from __future__ import annotations

from datetime import date
import json
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
OUT = ROOT / 'generated'
REPORT = OUT / 'deontic_reasoning_report.json'
KG = OUT / 'full_case_knowledge_graph.json'


def closure_action(fact: Dict[str, object], *, reason: str) -> str:
    predicate = str(fact.get('predicate', ''))
    source = str(fact.get('source', ''))
    status = str(fact.get('status', ''))

    if reason == 'false_value':
        if predicate.startswith('Subpoena') or 'subpoena' in predicate.lower():
            return 'Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.'
        if 'AuthorityCitationsUnresolved' in predicate:
            return 'Replace placeholder citations with finalized ORS/ORCP/case authority entries, then regenerate artifacts.'
        return 'Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.'

    if status == 'alleged':
        if 'PriorAppointment' in predicate:
            return 'Obtain certified guardianship appointment order/docket showing appointment identity and effective date.'
        if 'FailedToAppear' in predicate:
            return 'Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.'
        if 'RefiledBarredIssue' in predicate:
            return 'Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart.'
        return 'Convert allegation to verified with certified records, transcripts, or authenticated communications.'

    if status == 'theory':
        return 'Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency.'

    if source:
        return f'Validate and supplement evidence linked to `{source}` to satisfy proof-state requirements.'
    return 'Collect documentary evidence and promote this antecedent to verified where required.'


def build() -> Dict[str, object]:
    report = json.loads(REPORT.read_text(encoding='utf-8'))
    kg = json.loads(KG.read_text(encoding='utf-8'))

    fact_nodes: Dict[str, Dict[str, object]] = {}
    for n in kg.get('nodes', []):
        if n.get('kind') == 'fact':
            fact_nodes[str(n.get('id', '')).replace('fact:', '', 1)] = n

    out = {
        'generated_at': str(date.today()),
        'modes': {},
    }

    for mode in ('strict', 'inclusive'):
        mode_block = report['modes'][mode]
        unresolved_rules = mode_block.get('unresolved_rules', [])
        inactive_rules = mode_block.get('inactive_rules', [])

        rule_items: List[Dict[str, object]] = []
        for class_name, rules in (('unresolved', unresolved_rules), ('inactive', inactive_rules)):
            for rule in rules:
                antecedent_items: List[Dict[str, object]] = []
                for ant in rule.get('antecedents', []):
                    fid = ant.get('fact_id')
                    fact = fact_nodes.get(str(fid), {})
                    value = str(ant.get('value', 'false')).lower() == 'true'
                    status = str(ant.get('status', ''))

                    needs_action = False
                    reason = ''
                    if class_name == 'inactive' and not value:
                        needs_action = True
                        reason = 'false_value'
                    elif class_name == 'unresolved' and status != 'verified':
                        needs_action = True
                        reason = 'proof_gated'

                    antecedent_items.append(
                        {
                            'fact_id': fid,
                            'predicate': fact.get('predicate'),
                            'current_value': value,
                            'current_status': status,
                            'source': fact.get('source'),
                            'dates': ant.get('dates', []),
                            'needs_action': needs_action,
                            'closure_action': closure_action(fact, reason=reason) if needs_action else 'No immediate action required for this antecedent.',
                        }
                    )

                rule_items.append(
                    {
                        'classification': class_name,
                        'rule_id': rule.get('rule_id'),
                        'track': rule.get('track'),
                        'description': rule.get('description'),
                        'authority_refs': rule.get('authority_refs', []),
                        'activation_date_estimate': rule.get('activation_date_estimate'),
                        'antecedent_intake': antecedent_items,
                    }
                )

        out['modes'][mode] = {
            'counts': {
                'active': len(mode_block.get('active_rules', [])),
                'unresolved': len(unresolved_rules),
                'inactive': len(inactive_rules),
            },
            'rules_needing_intake': rule_items,
        }

    return out


def to_markdown(obj: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append('# Proof Intake Map')
    lines.append('')
    lines.append(f"Generated: {obj['generated_at']}")
    lines.append('')

    for mode in ('strict', 'inclusive'):
        block = obj['modes'][mode]
        counts = block['counts']
        lines.append(f'## Mode: {mode}')
        lines.append(f"- Active: {counts['active']}")
        lines.append(f"- Unresolved: {counts['unresolved']}")
        lines.append(f"- Inactive: {counts['inactive']}")
        lines.append('')

        for r in block['rules_needing_intake']:
            lines.append(f"### {r['classification'].upper()} - {r['rule_id']}")
            lines.append(f"- Track: {r.get('track')}")
            lines.append(f"- Description: {r.get('description')}")
            auth = ', '.join(r.get('authority_refs', [])) or 'none'
            lines.append(f"- Authority refs: {auth}")
            lines.append(f"- Activation estimate: {r.get('activation_date_estimate')}")
            lines.append('- Antecedent intake:')
            for a in r['antecedent_intake']:
                lines.append(f"- {a['fact_id']}: value={a['current_value']} status={a['current_status']} source={a.get('source')}")
                lines.append(f"- Action: {a['closure_action']}")
            lines.append('')

    return '\n'.join(lines) + '\n'


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    obj = build()
    stamp = str(date.today())
    json_path = OUT / f'proof_intake_map_{stamp}.json'
    md_path = OUT / f'proof_intake_map_{stamp}.md'
    json_path.write_text(json.dumps(obj, indent=2), encoding='utf-8')
    md_path.write_text(to_markdown(obj), encoding='utf-8')


if __name__ == '__main__':
    main()
