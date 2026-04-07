#!/usr/bin/env python3
"""Generate end-to-end deontic grounding gap report.

Checks coverage across:
- authority facts -> authority refs -> rules
- rule tracks vs authority grounding
- unresolved/inactive rule cause classes
- source/proof-state exposure in strict mode
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated')
OUT_JSON = ROOT / 'deontic_end_to_end_grounding_gap_report_2026-04-07.json'
OUT_MD = ROOT / 'deontic_end_to_end_grounding_gap_report_2026-04-07.md'


def load(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding='utf-8'))


def main() -> None:
    kg = load(ROOT / 'full_case_knowledge_graph.json')
    report = load(ROOT / 'deontic_reasoning_report.json')

    fact_nodes = {}
    rule_nodes = {}
    for n in kg.get('nodes', []):
        kind = n.get('kind')
        nid = str(n.get('id', ''))
        if kind == 'fact' and nid.startswith('fact:'):
            fact_nodes[nid.replace('fact:', '', 1)] = n
        if kind == 'rule' and nid.startswith('rule:'):
            rule_nodes[nid.replace('rule:', '', 1)] = n

    authority_fact_auth_ids = set()
    for f in fact_nodes.values():
        if f.get('predicate') == 'AuthorityAvailable':
            args = f.get('args') or []
            if args:
                authority_fact_auth_ids.add(str(args[0]))

    referenced_authorities = set()
    missing_authority_fact_links: List[Dict[str, str]] = []
    rules_without_authority_refs: List[Dict[str, str]] = []
    non_hypothesis_rules_without_authority_refs: List[Dict[str, str]] = []

    for rid, r in sorted(rule_nodes.items()):
        auth = list(r.get('authority_refs') or [])
        track = str(r.get('track', ''))
        if not auth:
            item = {'rule_id': rid, 'track': track}
            rules_without_authority_refs.append(item)
            if track != 'hypothesis':
                non_hypothesis_rules_without_authority_refs.append(item)
        for a in auth:
            referenced_authorities.add(a)
            if not a.startswith('order:') and a not in authority_fact_auth_ids:
                missing_authority_fact_links.append({'rule_id': rid, 'authority_ref': a})

    unused_authority_facts = sorted(authority_fact_auth_ids - referenced_authorities)

    strict = report['modes']['strict']
    inclusive = report['modes']['inclusive']

    unresolved_analysis = []
    for r in strict.get('unresolved_rules', []):
        non_verified = [a for a in r.get('antecedents', []) if a.get('status') != 'verified']
        unresolved_analysis.append(
            {
                'rule_id': r.get('rule_id'),
                'track': r.get('track'),
                'non_verified_antecedents': [
                    {
                        'fact_id': a.get('fact_id'),
                        'status': a.get('status'),
                        'value': a.get('value'),
                    }
                    for a in non_verified
                ],
            }
        )

    inactive_analysis = []
    for r in strict.get('inactive_rules', []):
        false_ants = [a for a in r.get('antecedents', []) if str(a.get('value')).lower() != 'true']
        inactive_analysis.append(
            {
                'rule_id': r.get('rule_id'),
                'track': r.get('track'),
                'false_antecedents': [
                    {
                        'fact_id': a.get('fact_id'),
                        'status': a.get('status'),
                        'value': a.get('value'),
                    }
                    for a in false_ants
                ],
            }
        )

    strict_active_client_assertion_deps = []
    for r in strict.get('active_rules', []):
        risky = []
        for a in r.get('antecedents', []):
            fid = str(a.get('fact_id'))
            fn = fact_nodes.get(fid, {})
            src = str(fn.get('source', ''))
            if src == 'client_assertion' or str(a.get('status')) in {'alleged', 'theory'}:
                risky.append({'fact_id': fid, 'status': a.get('status'), 'source': src})
        if risky:
            strict_active_client_assertion_deps.append({'rule_id': r.get('rule_id'), 'risky_antecedents': risky})

    recommended = [
        'Convert strict unresolved allegation/theory antecedents to verified with certified docket/order/service records.',
        'Activate workflow rules r17-r19 by entering confirmed service/deficiency events in the active service log.',
        'Keep strict-active set free of client_assertion/theory antecedents before filing-grade reliance.',
    ]
    if non_hypothesis_rules_without_authority_refs:
        recommended.insert(
            2,
            'Add authority_refs for non-hypothesis rules intentionally relying on formal legal authority but currently untagged.',
        )

    output = {
        'generated_at': str(date.today()),
        'summary': {
            'strict_counts': {
                'active': len(strict.get('active_rules', [])),
                'unresolved': len(strict.get('unresolved_rules', [])),
                'inactive': len(strict.get('inactive_rules', [])),
            },
            'inclusive_counts': {
                'active': len(inclusive.get('active_rules', [])),
                'unresolved': len(inclusive.get('unresolved_rules', [])),
                'inactive': len(inclusive.get('inactive_rules', [])),
            },
            'rules_total': len(rule_nodes),
            'authority_available_facts': len(authority_fact_auth_ids),
            'authority_refs_in_rules': len(referenced_authorities),
        },
        'authority_linkage': {
            'missing_authority_fact_links': missing_authority_fact_links,
            'rules_without_authority_refs': rules_without_authority_refs,
            'non_hypothesis_rules_without_authority_refs': non_hypothesis_rules_without_authority_refs,
            'unused_authority_facts': unused_authority_facts,
        },
        'strict_unresolved_analysis': unresolved_analysis,
        'strict_inactive_analysis': inactive_analysis,
        'strict_active_client_assertion_or_nonverified_dependencies': strict_active_client_assertion_deps,
        'recommended_closure_actions': recommended,
    }

    OUT_JSON.write_text(json.dumps(output, indent=2), encoding='utf-8')

    lines: List[str] = []
    lines.append('# Deontic End-to-End Grounding Gap Report - 2026-04-07')
    lines.append('')
    s = output['summary']
    lines.append('## Summary')
    lines.append(f"- Strict: active={s['strict_counts']['active']} unresolved={s['strict_counts']['unresolved']} inactive={s['strict_counts']['inactive']}")
    lines.append(f"- Inclusive: active={s['inclusive_counts']['active']} unresolved={s['inclusive_counts']['unresolved']} inactive={s['inclusive_counts']['inactive']}")
    lines.append(f"- Rules total: {s['rules_total']}")
    lines.append(f"- Authority facts: {s['authority_available_facts']}")
    lines.append(f"- Authority refs used by rules: {s['authority_refs_in_rules']}")
    lines.append('')

    al = output['authority_linkage']
    lines.append('## Authority Linkage Gaps')
    lines.append(f"- Missing authority-fact links: {len(al['missing_authority_fact_links'])}")
    lines.append(f"- Rules without authority refs: {len(al['rules_without_authority_refs'])}")
    lines.append(f"- Non-hypothesis rules without authority refs: {len(al['non_hypothesis_rules_without_authority_refs'])}")
    lines.append(f"- Unused authority facts: {len(al['unused_authority_facts'])}")
    if al['non_hypothesis_rules_without_authority_refs']:
        lines.append('- Non-hypothesis rules missing authority refs:')
        for x in al['non_hypothesis_rules_without_authority_refs']:
            lines.append(f"- {x['rule_id']} ({x['track']})")
    lines.append('')

    lines.append('## Strict Unresolved Rules (Proof Gated)')
    for r in output['strict_unresolved_analysis']:
        lines.append(f"- {r['rule_id']} ({r['track']})")
        for a in r['non_verified_antecedents']:
            lines.append(f"- antecedent {a['fact_id']} status={a['status']} value={a['value']}")
    lines.append('')

    lines.append('## Strict Inactive Rules (Antecedent False)')
    for r in output['strict_inactive_analysis']:
        lines.append(f"- {r['rule_id']} ({r['track']})")
        for a in r['false_antecedents']:
            lines.append(f"- antecedent {a['fact_id']} status={a['status']} value={a['value']}")
    lines.append('')

    lines.append('## Strict Active Dependency Exposure')
    if output['strict_active_client_assertion_or_nonverified_dependencies']:
        lines.append('- Active rules with non-verified/client-assertion dependencies were found (review required).')
        for r in output['strict_active_client_assertion_or_nonverified_dependencies']:
            lines.append(f"- {r['rule_id']}")
    else:
        lines.append('- No strict-active rules depend on alleged/theory/client_assertion antecedents.')
    lines.append('')

    lines.append('## Recommended Closure Actions')
    for x in output['recommended_closure_actions']:
        lines.append(f'- {x}')
    lines.append('')

    OUT_MD.write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
