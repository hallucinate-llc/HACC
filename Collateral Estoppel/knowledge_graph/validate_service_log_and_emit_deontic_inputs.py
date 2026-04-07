#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path
import re

ROOT = Path('/home/barberb/HACC/Collateral Estoppel')
ACTIVE_LOG = ROOT / 'drafts/final_filing_set/28_active_service_log_2026-04-07.csv'
OUT_DIR = ROOT / 'knowledge_graph/generated'

VALID_STATUSES = {
    'ready_to_serve',
    'served',
    'awaiting_production',
    'production_received',
    'deficiency_notice_stage',
    'motion_to_compel_stage',
}

DATE_FIELDS = [
    'log_date',
    'date_served',
    'production_due',
    'date_production_received',
    'deficiency_notice_sent',
    'cure_deadline',
    'cure_received',
    'motion_to_compel_filed',
]


def iso_date(s: str) -> str | None:
    s = (s or '').strip()
    if not s:
        return None
    m = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", s)
    return m.group(1) if m else None


def truthy(s: str) -> bool:
    return (s or '').strip().lower() in {'y', 'yes', 'true', '1'}


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    if ACTIVE_LOG.exists():
        with ACTIVE_LOG.open('r', encoding='utf-8', newline='') as fh:
            rows = list(csv.DictReader(fh))

    issues = []
    warnings = []
    per_row = []

    served_any = False
    incomplete_any = False
    deficiency_any = False
    compel_any = False

    for i, row in enumerate(rows, start=1):
        recipient = (row.get('recipient') or f'row_{i}').strip()
        status = (row.get('status') or '').strip().lower()

        row_issues = []
        row_warnings = []

        if status not in VALID_STATUSES:
            row_issues.append(f"invalid_status:{status or 'EMPTY'}")

        parsed_dates = {}
        for f in DATE_FIELDS:
            raw = row.get(f, '')
            d = iso_date(raw)
            parsed_dates[f] = d
            if raw and not d:
                row_issues.append(f"invalid_date_format:{f}:{raw}")

        date_served = parsed_dates.get('date_served')
        deficiency_sent = parsed_dates.get('deficiency_notice_sent')
        compel_filed = parsed_dates.get('motion_to_compel_filed')

        checklist = (row.get('checklist_received') or '').strip().lower()
        search_report = (row.get('search_report_received') or '').strip().lower()

        if status == 'ready_to_serve' and date_served:
            row_warnings.append('status_ready_but_date_served_present')

        if status in {'served', 'awaiting_production', 'production_received', 'deficiency_notice_stage', 'motion_to_compel_stage'} and not date_served:
            row_warnings.append('served_like_status_without_date_served')

        if status in {'deficiency_notice_stage', 'motion_to_compel_stage'} and not deficiency_sent:
            row_warnings.append('deficiency_stage_without_deficiency_notice_date')

        if status == 'motion_to_compel_stage' and not compel_filed:
            row_warnings.append('motion_to_compel_stage_without_motion_date')

        if date_served and status in {'served', 'awaiting_production', 'deficiency_notice_stage', 'motion_to_compel_stage'}:
            if checklist in {'', 'n', 'no', 'false'} or search_report in {'', 'n', 'no', 'false'}:
                row_warnings.append('served_with_missing_required_return_artifacts')

        # derived activations (mirror generator semantics)
        row_served = (status in {'served', 'awaiting_production', 'production_received', 'deficiency_notice_stage', 'motion_to_compel_stage'}) or bool(date_served)
        row_incomplete = (
            status in {'awaiting_production', 'deficiency_notice_stage', 'motion_to_compel_stage'}
            or (bool(date_served) and (checklist in {'', 'n', 'no', 'false'} or search_report in {'', 'n', 'no', 'false'}))
        )
        row_deficiency = status in {'deficiency_notice_stage', 'motion_to_compel_stage'} or bool(deficiency_sent)
        row_compel = status == 'motion_to_compel_stage' or bool(compel_filed)

        served_any = served_any or row_served
        incomplete_any = incomplete_any or row_incomplete
        deficiency_any = deficiency_any or row_deficiency
        compel_any = compel_any or row_compel

        for it in row_issues:
            issues.append({'recipient': recipient, 'issue': it})
        for it in row_warnings:
            warnings.append({'recipient': recipient, 'warning': it})

        per_row.append({
            'recipient': recipient,
            'status': status,
            'date_served': date_served,
            'derived': {
                'served': row_served,
                'incomplete': row_incomplete,
                'deficiency': row_deficiency,
                'compel': row_compel,
            },
            'issues': row_issues,
            'warnings': row_warnings,
        })

    derived_summary = {
        'f_subpoena_service_completed_any': served_any,
        'f_subpoena_response_incomplete_any': incomplete_any,
        'f_deficiency_notice_sent_any': deficiency_any,
        'f_motion_to_compel_stage_any': compel_any,
    }

    out = {
        'generated_at': str(date.today()),
        'source_log': str(ACTIVE_LOG),
        'row_count': len(rows),
        'valid_statuses': sorted(VALID_STATUSES),
        'issues': issues,
        'warnings': warnings,
        'derived_summary': derived_summary,
        'rows': per_row,
    }

    (OUT_DIR / 'service_log_validation_report_2026-04-07.json').write_text(
        json.dumps(out, indent=2), encoding='utf-8'
    )

    lines = [
        '# Service Log Validation Report - 2026-04-07',
        '',
        f"Source: `{ACTIVE_LOG}`",
        f"Rows: {len(rows)}",
        '',
        '## Derived Deontic Activation Summary',
        '',
    ]
    for k, v in derived_summary.items():
        lines.append(f"- {k}: {str(v).lower()}")

    lines.extend(['', '## Issues'])
    if issues:
        for x in issues:
            lines.append(f"- {x['recipient']}: {x['issue']}")
    else:
        lines.append('- none')

    lines.extend(['', '## Warnings'])
    if warnings:
        for x in warnings:
            lines.append(f"- {x['recipient']}: {x['warning']}")
    else:
        lines.append('- none')

    lines.extend(['', '## Per-Recipient Derived State'])
    for r in per_row:
        d = r['derived']
        lines.append(f"- {r['recipient']}: status={r['status'] or 'EMPTY'}, served={d['served']}, incomplete={d['incomplete']}, deficiency={d['deficiency']}, compel={d['compel']}")

    (OUT_DIR / 'service_log_validation_report_2026-04-07.md').write_text(
        '\n'.join(lines) + '\n', encoding='utf-8'
    )


if __name__ == '__main__':
    main()
