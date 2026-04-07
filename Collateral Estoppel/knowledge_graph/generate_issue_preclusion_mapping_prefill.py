#!/usr/bin/env python3
"""Create conservative prefill artifacts for issue_preclusion_mapping.json.

This generator does NOT set element booleans true.
It only proposes note text and source candidates for review.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
EVID = ROOT / 'evidence_notes' / 'certified_records'
KG_GEN = ROOT / 'knowledge_graph' / 'generated'
DRAFTS = ROOT / 'drafts' / 'final_filing_set'

CANDIDATES = KG_GEN / f'issue_preclusion_evidence_candidates_{date.today().isoformat()}.json'
MAPPING = EVID / 'issue_preclusion_mapping.json'

OUT_JSON = KG_GEN / f'issue_preclusion_mapping_prefill_{date.today().isoformat()}.json'
OUT_MD = DRAFTS / f'53_issue_preclusion_mapping_prefill_review_packet_{date.today().isoformat()}.md'
OUT_CMD = DRAFTS / f'54_issue_preclusion_mapping_prefill_apply_command_sheet_{date.today().isoformat()}.md'


def load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def top_sources(rows: List[Dict[str, object]], n: int = 4) -> List[str]:
    out: List[str] = []
    for r in rows[:n]:
        st = r.get('source_type')
        if st == 'repository_index_hit':
            p = str(r.get('relative_path', '')).strip()
            if p:
                out.append(p)
        elif st == 'path_scan_hit':
            p = str(r.get('relative_path', '')).strip()
            if p:
                out.append(p)
        else:
            src = str(r.get('source', '')).strip()
            ev = str(r.get('event_id', '')).strip()
            if src:
                out.append(f'{src} ({ev})' if ev else src)
    return out


def compose_note(element: str, count: int, sources: List[str]) -> str:
    if count <= 0:
        return (
            'No candidate evidence located in current repository index/feed. '
            'Keep this element false until certified prior-proceeding records are obtained and mapped.'
        )

    lead = {
        'identical_issue': 'Candidate sources indicate potential overlap of the guardianship authority issue across filings.',
        'finality': 'Current index did not yield reliable finality artifacts; certified final order and register are still required.',
        'party_privity': 'Candidate sources indicate party-name overlap, but party/privity mapping remains uncertified.',
        'full_fair_opportunity': 'Current index did not yield reliable hearing/opportunity artifacts; certified appearance/hearing records are still required.',
    }.get(element, 'Candidate sources identified; mapping remains proof-gated pending certified support.')

    if sources:
        return f"{lead} Candidate references: " + '; '.join(sources)
    return lead


def main() -> None:
    c = load_json(CANDIDATES)
    m = load_json(MAPPING)

    grouped = c.get('candidates_by_element', {}) if isinstance(c, dict) else {}

    by_element = {}
    for element in ('identical_issue', 'finality', 'party_privity', 'full_fair_opportunity'):
        rows = grouped.get(element, []) if isinstance(grouped, dict) else []
        rows = rows if isinstance(rows, list) else []
        sources = top_sources(rows)
        by_element[element] = {
            'candidate_count': len(rows),
            'top_sources': sources,
            'proposed_note': compose_note(element, len(rows), sources),
            'proposed_boolean': False,
        }

    proposed_mapping = {
        'prior_proceeding_caption': m.get('prior_proceeding_caption', ''),
        'prior_proceeding_case_number': m.get('prior_proceeding_case_number', ''),
        'identical_issue_mapped': False,
        'identical_issue_note': by_element['identical_issue']['proposed_note'],
        'finality_mapped': False,
        'finality_note': by_element['finality']['proposed_note'],
        'party_privity_mapped': False,
        'party_privity_note': by_element['party_privity']['proposed_note'],
        'full_fair_opportunity_mapped': False,
        'full_fair_opportunity_note': by_element['full_fair_opportunity']['proposed_note'],
        'mapping_completed_by': m.get('mapping_completed_by', ''),
        'mapping_completed_on': m.get('mapping_completed_on', ''),
    }

    payload = {
        'generated_at': str(date.today()),
        'source_candidates_file': str(CANDIDATES),
        'target_mapping_file': str(MAPPING),
        'safety_rule': 'Prefill does not set any *_mapped boolean to true.',
        'element_prefill': by_element,
        'proposed_mapping_snapshot': proposed_mapping,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')

    md_lines: List[str] = []
    md_lines.append('# Issue-Preclusion Mapping Prefill Review Packet')
    md_lines.append('')
    md_lines.append(f'Generated: {date.today().isoformat()}')
    md_lines.append('')
    md_lines.append('Safety rule: this prefill keeps all `*_mapped` booleans as `false`.')
    md_lines.append('')
    md_lines.append('## Proposed Notes by Element')
    for element in ('identical_issue', 'finality', 'party_privity', 'full_fair_opportunity'):
        row = by_element[element]
        md_lines.append(f'### {element}')
        md_lines.append(f"- Candidate count: {row['candidate_count']}")
        md_lines.append('- Top sources:')
        if row['top_sources']:
            for s in row['top_sources']:
                md_lines.append(f'- {s}')
        else:
            md_lines.append('- (none)')
        md_lines.append(f"- Proposed note: {row['proposed_note']}")
        md_lines.append('')

    md_lines.append('## Proposed Mapping Snapshot (Do Not Auto-Assert)')
    md_lines.append('```json')
    md_lines.append(json.dumps(proposed_mapping, indent=2))
    md_lines.append('```')
    md_lines.append('')
    md_lines.append('## Suggested Review Sequence')
    md_lines.append('1. Replace generic notes with certified-document citations once certified records arrive.')
    md_lines.append('2. Keep booleans false until each element is supported by certified material.')
    md_lines.append('3. After updates, rerun formal artifact generators and verify r7 state transition.')
    OUT_MD.write_text('\n'.join(md_lines).rstrip() + '\n', encoding='utf-8')

    cmd_lines: List[str] = []
    cmd_lines.append('# Issue-Preclusion Prefill Apply Command Sheet')
    cmd_lines.append('')
    cmd_lines.append(f'Generated: {date.today().isoformat()}')
    cmd_lines.append('')
    cmd_lines.append('Review first:')
    cmd_lines.append('```bash')
    cmd_lines.append(f'sed -n "1,260p" "{OUT_MD}"')
    cmd_lines.append(f'sed -n "1,220p" "{MAPPING}"')
    cmd_lines.append('```')
    cmd_lines.append('')
    cmd_lines.append('Optional apply (manual review strongly recommended):')
    cmd_lines.append('```bash')
    cmd_lines.append('python3 - << "PY"')
    cmd_lines.append('import json')
    cmd_lines.append(f'pref=json.load(open("{OUT_JSON}"))')
    cmd_lines.append(f'target="{MAPPING}"')
    cmd_lines.append('snapshot=pref["proposed_mapping_snapshot"]')
    cmd_lines.append('open(target,"w",encoding="utf-8").write(json.dumps(snapshot,indent=2)+"\\n")')
    cmd_lines.append('print(target)')
    cmd_lines.append('PY')
    cmd_lines.append('```')
    cmd_lines.append('')
    cmd_lines.append('Recompute after any mapping edit:')
    cmd_lines.append('```bash')
    cmd_lines.append(f'python3 "{ROOT / "knowledge_graph" / "generate_formal_reasoning_artifacts.py"}"')
    cmd_lines.append(f'python3 "{ROOT / "knowledge_graph" / "generate_grounding_gap_report.py"}"')
    cmd_lines.append(f'python3 "{ROOT / "knowledge_graph" / "generate_deontic_gap_closure_matrix.py"}"')
    cmd_lines.append('```')
    OUT_CMD.write_text('\n'.join(cmd_lines).rstrip() + '\n', encoding='utf-8')

    print(OUT_JSON)
    print(OUT_MD)
    print(OUT_CMD)


if __name__ == '__main__':
    main()
