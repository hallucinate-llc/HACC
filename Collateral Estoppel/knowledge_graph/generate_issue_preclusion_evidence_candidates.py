#!/usr/bin/env python3
"""Generate candidate evidence map for issue-preclusion element mapping."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Dict, List

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
EVID = ROOT / 'evidence_notes'
KG_GEN = ROOT / 'knowledge_graph' / 'generated'
GLOBAL_EVID = Path('/home/barberb/HACC/evidence/history')

REPO_INDEX = EVID / 'solomon_repository_evidence_index.json'
FEED = EVID / 'solomon_evidence_graph_feed.json'
IP_MAP = EVID / 'certified_records' / 'issue_preclusion_mapping.json'

OUT_JSON = KG_GEN / f'issue_preclusion_evidence_candidates_{date.today().isoformat()}.json'
OUT_MD = KG_GEN / f'issue_preclusion_evidence_candidates_{date.today().isoformat()}.md'


ELEMENT_KEYWORDS = {
    'identical_issue': [
        'guardianship', 'petition', 'prior guardian', 'same issue', 'authority', 're-file', 'refile', 'collateral estoppel'
    ],
    'finality': [
        'final', 'judgment', 'granted', 'denied', 'dismissed', 'register of actions', 'register', 'docket', 'order'
    ],
    'party_privity': [
        'solomon', 'jane cortez', 'benjamin barber', 'julio cortez', 'party', 'privity'
    ],
    'full_fair_opportunity': [
        'notice', 'served', 'service', 'hearing', 'appearance', 'failed to appear', 'opportunity'
    ],
}


def load_json(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {}
    try:
        obj = json.loads(path.read_text(encoding='utf-8'))
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}


def is_text_candidate(path: Path) -> bool:
    return path.suffix.lower() in {'.md', '.txt', '.json', '.eml', '.csv'}


def safe_read_text(path: Path, limit: int = 12000) -> str:
    if not is_text_candidate(path):
        return ''
    try:
        return path.read_text(encoding='utf-8', errors='ignore')[:limit]
    except Exception:
        return ''


def score_text(text: str, words: List[str]) -> int:
    low = text.lower()
    return sum(1 for w in words if w in low)


def collect_repo_hits(index_obj: Dict[str, object]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for hit in index_obj.get('hits', []):
        rel = str(hit.get('relevance', '')).strip().lower()
        if rel not in {'high', 'medium'}:
            continue
        rel_path = str(hit.get('relative_path', '')).strip()
        if not rel_path:
            continue
        snippet = str(hit.get('snippet', '') or '')
        combined = f"{rel_path} {snippet}"

        elem_scores = {
            eid: score_text(combined, kws)
            for eid, kws in ELEMENT_KEYWORDS.items()
        }
        best_eid, best_score = max(elem_scores.items(), key=lambda kv: kv[1])
        if best_score <= 0:
            continue

        out.append(
            {
                'source_type': 'repository_index_hit',
                'relative_path': rel_path,
                'relevance': rel,
                'dates_found': hit.get('dates_found', []),
                'snippet': snippet,
                'element_scores': elem_scores,
                'best_element': best_eid,
                'best_score': best_score,
            }
        )
    return out


def collect_feed_hits(feed_obj: Dict[str, object]) -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    for ev in feed_obj.get('events', []):
        predicate = str(ev.get('predicate', '')).strip()
        source = str(ev.get('source', '')).strip()
        actor = str(ev.get('actor', '')).strip()
        target = str(ev.get('target', '')).strip()
        evidence_kind = str(ev.get('evidence_kind', '')).strip()
        combined = ' '.join([predicate, source, actor, target, evidence_kind])

        elem_scores = {
            eid: score_text(combined, kws)
            for eid, kws in ELEMENT_KEYWORDS.items()
        }
        best_eid, best_score = max(elem_scores.items(), key=lambda kv: kv[1])
        if best_score <= 0:
            continue

        out.append(
            {
                'source_type': 'event_feed',
                'event_id': ev.get('event_id'),
                'date': ev.get('date'),
                'status': ev.get('status'),
                'source': source,
                'predicate': predicate,
                'actor': actor,
                'target': target,
                'element_scores': elem_scores,
                'best_element': best_eid,
                'best_score': best_score,
            }
        )
    return out


def collect_path_scan_hits() -> List[Dict[str, object]]:
    out: List[Dict[str, object]] = []
    roots = [ROOT / 'evidence_notes', ROOT / 'drafts', GLOBAL_EVID]
    exts = {'.md', '.txt', '.json', '.eml', '.pdf'}

    seen = set()
    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob('*'):
            if not p.is_file():
                continue
            if p.suffix.lower() not in exts:
                continue
            rp = str(p)
            if rp in seen:
                continue
            seen.add(rp)

            rel = rp.replace('/home/barberb/HACC/', '')
            text = safe_read_text(p)
            combined = f'{rel} {text}'
            elem_scores = {eid: score_text(combined, kws) for eid, kws in ELEMENT_KEYWORDS.items()}
            best_eid, best_score = max(elem_scores.items(), key=lambda kv: kv[1])
            if best_score <= 0:
                continue

            out.append(
                {
                    'source_type': 'path_scan_hit',
                    'absolute_path': rp,
                    'relative_path': rel,
                    'element_scores': elem_scores,
                    'best_element': best_eid,
                    'best_score': best_score,
                }
            )
    return out


def group_candidates(items: List[Dict[str, object]]) -> Dict[str, List[Dict[str, object]]]:
    out: Dict[str, List[Dict[str, object]]] = {k: [] for k in ELEMENT_KEYWORDS.keys()}
    for row in items:
        scores = row.get('element_scores', {})
        if isinstance(scores, dict):
            for eid in out.keys():
                s = int(scores.get(eid, 0) or 0)
                if s > 0:
                    x = dict(row)
                    x['element_score'] = s
                    out[eid].append(x)
        else:
            eid = str(row.get('best_element', '')).strip()
            if eid in out:
                x = dict(row)
                x['element_score'] = int(row.get('best_score', 0) or 0)
                out[eid].append(x)
    for eid in out:
        out[eid] = sorted(
            out[eid],
            key=lambda x: (
                int(x.get('element_score', x.get('best_score', 0))),
                str(x.get('relevance', '')) == 'high',
            ),
            reverse=True,
        )[:15]
    return out


def to_markdown(payload: Dict[str, object]) -> str:
    lines: List[str] = []
    lines.append('# Issue-Preclusion Evidence Candidates')
    lines.append('')
    lines.append(f"Generated: {payload.get('generated_at')}")
    lines.append('')
    lines.append('Use this report to populate `issue_preclusion_mapping.json` notes and collect certified proofs.')
    lines.append('')

    for eid, rows in payload.get('candidates_by_element', {}).items():
        lines.append(f'## {eid}')
        lines.append(f"- Candidate count: {len(rows)}")
        if not rows:
            lines.append('- No candidates found from current index/feed.')
            lines.append('')
            continue

        for r in rows:
            st = r.get('source_type')
            if st == 'repository_index_hit':
                lines.append(
                    f"- repo:{r.get('relative_path')} | relevance={r.get('relevance')} | score={r.get('element_score', r.get('best_score'))}"
                )
            elif st == 'path_scan_hit':
                lines.append(
                    f"- path:{r.get('relative_path')} | score={r.get('element_score', r.get('best_score'))}"
                )
            else:
                lines.append(
                    f"- event:{r.get('event_id')} | predicate={r.get('predicate')} | date={r.get('date')} | score={r.get('element_score', r.get('best_score'))}"
                )
        lines.append('')

    return '\n'.join(lines).rstrip() + '\n'


def main() -> None:
    repo = load_json(REPO_INDEX)
    feed = load_json(FEED)
    ip = load_json(IP_MAP)

    repo_hits = collect_repo_hits(repo)
    feed_hits = collect_feed_hits(feed)
    path_hits = collect_path_scan_hits()
    grouped = group_candidates(repo_hits + feed_hits + path_hits)

    payload = {
        'generated_at': str(date.today()),
        'issue_preclusion_mapping_present': bool(ip),
        'mapping_status': {
            'identical_issue_mapped': bool(ip.get('identical_issue_mapped', False)),
            'finality_mapped': bool(ip.get('finality_mapped', False)),
            'party_privity_mapped': bool(ip.get('party_privity_mapped', False)),
            'full_fair_opportunity_mapped': bool(ip.get('full_fair_opportunity_mapped', False)),
        },
        'source_mix': {
            'repository_index_hits': len(repo_hits),
            'event_feed_hits': len(feed_hits),
            'path_scan_hits': len(path_hits),
        },
        'candidate_counts': {k: len(v) for k, v in grouped.items()},
        'candidates_by_element': grouped,
    }

    OUT_JSON.write_text(json.dumps(payload, indent=2), encoding='utf-8')
    OUT_MD.write_text(to_markdown(payload), encoding='utf-8')
    print(OUT_JSON)
    print(OUT_MD)


if __name__ == '__main__':
    main()
