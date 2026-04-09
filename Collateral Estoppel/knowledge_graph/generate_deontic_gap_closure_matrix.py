#!/usr/bin/env python3
"""Generate consolidated deontic gap-closure matrix across law/evidence/formal layers."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel/knowledge_graph')
GEN = ROOT / 'generated'

REPORT = GEN / 'deontic_reasoning_report.json'
OUT_JSON = GEN / f'deontic_gap_closure_matrix_{date.today().isoformat()}.json'
OUT_MD = GEN / f'deontic_gap_closure_matrix_{date.today().isoformat()}.md'

FACT_PACKET_MAP = {
    'f_client_solomon_failed_appearance': 'packet_nonappearance_r24',
    'f_collateral_estoppel_candidate': 'packet_issue_preclusion_r7',
    'f_client_solomon_barred_refile': 'packet_issue_preclusion_r7',
    'f_client_prior_appointment': 'packet_prior_appointment_r1_r2_r3',
    'f_client_solomon_housing_interference': 'packet_prior_appointment_r1_r2_r3',
    'f_client_solomon_order_disregard': 'packet_prior_appointment_r1_r2_r3',
    'f_subpoena_service_completed_any': 'service_log_progression_r17_r18_r19',
    'f_subpoena_response_incomplete_any': 'service_log_progression_r17_r18_r19',
    'f_deficiency_notice_sent_any': 'service_log_progression_r17_r18_r19',
    'f_authority_table_placeholders_unresolved': 'authority_table_finalization_r22',
}


def load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding='utf-8'))


def latest_proof_map() -> Dict[str, object]:
    candidates = sorted(GEN.glob('proof_intake_map_*.json'))
    if candidates:
        return load_json(candidates[-1])
    return load_json(GEN / 'proof_intake_map_2026-04-07.json')


def blocker_from_antecedent(a: Dict[str, object]) -> bool:
    status = str(a.get('status', '')).strip().lower()
    value = str(a.get('value', '')).strip().lower()
    if status != 'verified':
        return True
    return value != 'true'


def normalize_rule_intake_index(proof_obj: Dict[str, object]) -> Dict[str, Dict[str, object]]:
    out: Dict[str, Dict[str, object]] = {}
    strict = proof_obj.get('modes', {}).get('strict', {})
    for row in strict.get('rules_needing_intake', []):
        rid = str(row.get('rule_id', '')).strip()
        if rid:
            out[rid] = row
    return out


def derive_formal_requirements(rule_id: str, blockers: List[Dict[str, object]]) -> Dict[str, object]:
    requirements: List[tuple[str, str]] = []
    for b in blockers:
        fid = str(b.get('fact_id', '')).strip()
        if not fid:
            continue
        status = str(b.get('status', '')).strip().lower()
        value = str(b.get('value', '')).strip().lower()
        if status != 'verified':
            requirements.append((fid, 'need_verified'))
        if value != 'true':
            requirements.append((fid, 'need_true'))
    requirements = sorted(set(requirements))

    flogo = [f'{kind}({fid}).' for fid, kind in requirements]
    tdfol = [f'requires_{kind}({rule_id}, {fid}).' for fid, kind in requirements]
    dec = [f'requires_holds_at({fid}, true, T).' for fid, _kind in requirements]
    return {
        'f_logic_requirements': flogo,
        'temporal_deontic_fol_requirements': tdfol,
        'deontic_event_calculus_requirements': dec,
    }


def build_matrix(report: Dict[str, object], proof: Dict[str, object]) -> Dict[str, object]:
    unresolved = report.get('modes', {}).get('strict', {}).get('unresolved_rules', [])
    inactive = report.get('modes', {}).get('strict', {}).get('inactive_rules', [])
    intake_idx = normalize_rule_intake_index(proof)

    rules = []
    for group, rows in [('unresolved', unresolved), ('inactive', inactive)]:
        for r in rows:
            rid = str(r.get('rule_id', '')).strip()
            if not rid:
                continue
            antecedents = list(r.get('antecedents', []))
            blockers = [a for a in antecedents if blocker_from_antecedent(a)]

            intake = intake_idx.get(rid, {})
            actions = []
            for ai in intake.get('antecedent_intake', []):
                if ai.get('needs_action'):
                    actions.append({
                        'fact_id': ai.get('fact_id'),
                        'closure_action': ai.get('closure_action'),
                        'source': ai.get('source'),
                    })

            packets = sorted(
                {
                    FACT_PACKET_MAP.get(str(a.get('fact_id', '')).strip(), 'manual_follow_up')
                    for a in blockers
                }
            )
            formal = derive_formal_requirements(rid, blockers)

            rules.append(
                {
                    'rule_id': rid,
                    'classification': group,
                    'track': r.get('track'),
                    'authority_refs': list(r.get('authority_refs', [])),
                    'description': r.get('description'),
                    'blocking_antecedents': blockers,
                    'closure_actions': actions,
                    'recommended_packets': packets,
                    'formal_requirements': formal,
                }
            )

    open_audits = []
    for audit in report.get('element_audits', []):
        open_elements = [
            e for e in audit.get('elements', []) if str(e.get('status', '')).strip().lower() != 'verified'
        ]
        if open_elements:
            open_audits.append(
                {
                    'audit_id': audit.get('audit_id'),
                    'label': audit.get('label'),
                    'governing_authority': audit.get('governing_authority', []),
                    'interval_refs': audit.get('interval_refs', []),
                    'open_elements': open_elements,
                }
            )

    strict = report.get('modes', {}).get('strict', {})
    strict_counts = strict.get('counts', {})
    if not strict_counts:
        strict_counts = {
            'active_rules': len(strict.get('active_rules', [])),
            'unresolved_rules': len(strict.get('unresolved_rules', [])),
            'inactive_rules': len(strict.get('inactive_rules', [])),
        }

    return {
        'generated_at': str(date.today()),
        'strict_counts': strict_counts,
        'matrix_rules': rules,
        'open_element_audits': open_audits,
    }


def to_markdown(matrix: Dict[str, object]) -> str:
    lines: List[str] = []
    c = matrix.get('strict_counts', {})

    lines.append('# Deontic Gap Closure Matrix')
    lines.append('')
    lines.append(f"Generated: {matrix.get('generated_at')}")
    lines.append('')
    lines.append('## Strict Mode Counts')
    lines.append(f"- active={c.get('active_rules')} unresolved={c.get('unresolved_rules')} inactive={c.get('inactive_rules')}")
    lines.append('')

    lines.append('## Rule Closure Matrix')
    for r in matrix.get('matrix_rules', []):
        lines.append(f"### {r.get('rule_id')} ({r.get('classification')})")
        lines.append(f"- Track: {r.get('track')}")
        refs = ', '.join(r.get('authority_refs', [])) or '(none)'
        lines.append(f"- Authority refs: {refs}")
        lines.append(f"- Description: {r.get('description')}")
        lines.append('- Blocking antecedents:')
        blockers = r.get('blocking_antecedents', [])
        if blockers:
            for b in blockers:
                lines.append(
                    f"- {b.get('fact_id')} status={b.get('status')} value={b.get('value')}"
                )
        else:
            lines.append('- (none)')

        lines.append('- Closure actions:')
        actions = r.get('closure_actions', [])
        if actions:
            for a in actions:
                lines.append(f"- {a.get('fact_id')}: {a.get('closure_action')} (source: {a.get('source')})")
        else:
            lines.append('- manual_follow_up: no explicit proof-intake action row found')

        packets = ', '.join(r.get('recommended_packets', [])) or 'manual_follow_up'
        lines.append(f"- Recommended packets/workstreams: {packets}")

        formal = r.get('formal_requirements', {})
        lines.append('- F-logic requirements:')
        for x in formal.get('f_logic_requirements', []):
            lines.append(f'- `{x}`')
        if not formal.get('f_logic_requirements'):
            lines.append('- `(none)`')

        lines.append('- Temporal-deontic FOL requirements:')
        for x in formal.get('temporal_deontic_fol_requirements', []):
            lines.append(f'- `{x}`')
        if not formal.get('temporal_deontic_fol_requirements'):
            lines.append('- `(none)`')

        lines.append('- Deontic event-calculus requirements:')
        for x in formal.get('deontic_event_calculus_requirements', []):
            lines.append(f'- `{x}`')
        if not formal.get('deontic_event_calculus_requirements'):
            lines.append('- `(none)`')
        lines.append('')

    lines.append('## Open Element Audits')
    for a in matrix.get('open_element_audits', []):
        lines.append(f"### {a.get('audit_id')}")
        lines.append(f"- Label: {a.get('label')}")
        gov = ', '.join(a.get('governing_authority', [])) or '(none)'
        lines.append(f"- Governing authority: {gov}")
        ivals = ', '.join(a.get('interval_refs', [])) or '(none)'
        lines.append(f"- Interval refs: {ivals}")
        lines.append('- Open elements:')
        for e in a.get('open_elements', []):
            note = str(e.get('note', '')).strip()
            if note:
                lines.append(f"- {e.get('element_id')} status={e.get('status')} note={note}")
            else:
                lines.append(f"- {e.get('element_id')} status={e.get('status')}")
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main() -> None:
    report = load_json(REPORT)
    proof = latest_proof_map()

    if not report:
        raise SystemExit(f'Missing report input: {REPORT}')

    matrix = build_matrix(report, proof)
    OUT_JSON.write_text(json.dumps(matrix, indent=2), encoding='utf-8')
    OUT_MD.write_text(to_markdown(matrix), encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
