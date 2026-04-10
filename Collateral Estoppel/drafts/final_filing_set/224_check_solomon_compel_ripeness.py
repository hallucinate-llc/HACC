#!/usr/bin/env python3
"""Check ripeness for Solomon compel/sanctions prefill promotion.

Reads the active service log CSV and evaluates whether the Solomon row meets
the gate for filing the compel/sanctions packet (88/89/88A).
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Optional


@dataclass
class GateResult:
    label: str
    passed: bool
    detail: str


def parse_date(value: str) -> Optional[date]:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def yesno(v: bool) -> str:
    return "PASS" if v else "FAIL"


def load_solomon_row(csv_path: Path) -> dict:
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        if "solomon" in (row.get("recipient", "").lower()):
            return row
    raise SystemExit(f"No Solomon row found in {csv_path}")


def evaluate(row: dict, today: date) -> tuple[list[GateResult], bool]:
    status = (row.get("status", "") or "").strip()
    date_served = parse_date(row.get("date_served", ""))
    service_method = (row.get("service_method", "") or "").strip()
    person_served = (row.get("person_served", "") or "").strip()
    production_due = parse_date(row.get("production_due", ""))
    date_prod_received = parse_date(row.get("date_production_received", ""))
    deficiency_sent = parse_date(row.get("deficiency_notice_sent", ""))
    cure_deadline = parse_date(row.get("cure_deadline", ""))
    cure_received = parse_date(row.get("cure_received", ""))

    service_completed = bool(date_served and service_method and person_served)
    response_matured = bool((production_due and today >= production_due) or date_prod_received)
    deficiency_completed = bool(deficiency_sent)

    cure_window_expired = bool(cure_deadline and today >= cure_deadline and not cure_received)
    cure_received_flag = bool(cure_received)
    cure_gate = cure_window_expired

    gates = [
        GateResult(
            "Service completed",
            service_completed,
            f"date_served={row.get('date_served','') or 'blank'}, "
            f"service_method={service_method or 'blank'}, "
            f"person_served={person_served or 'blank'}, "
            f"status={status or 'blank'}",
        ),
        GateResult(
            "Response window matured",
            response_matured,
            f"production_due={row.get('production_due','') or 'blank'}, "
            f"date_production_received={row.get('date_production_received','') or 'blank'}",
        ),
        GateResult(
            "Deficiency notice sent",
            deficiency_completed,
            f"deficiency_notice_sent={row.get('deficiency_notice_sent','') or 'blank'}",
        ),
        GateResult(
            "Cure window expired/failed",
            cure_gate,
            (
                f"cure_deadline={row.get('cure_deadline','') or 'blank'}, "
                f"cure_received={row.get('cure_received','') or 'blank'}, "
                f"cure_received_flag={'yes' if cure_received_flag else 'no'}"
            ),
        ),
    ]
    overall = all(g.passed for g in gates)
    return gates, overall


def render_markdown(row: dict, gates: list[GateResult], overall: bool, today: date) -> str:
    lines = []
    lines.append("SOLOMON COMPEL RIPENESS CHECK")
    lines.append(f"Date: {today.isoformat()}")
    lines.append("")
    lines.append("Source row:")
    lines.append(f"- recipient: {row.get('recipient','')}")
    lines.append(f"- packet_id: {row.get('packet_id','')}")
    lines.append(f"- status: {row.get('status','') or 'blank'}")
    lines.append("")
    lines.append("Gate evaluation:")
    for idx, g in enumerate(gates, start=1):
        lines.append(f"{idx}. {g.label}: {yesno(g.passed)}")
        lines.append(f"   - {g.detail}")
    lines.append("")
    lines.append(f"Overall promotion status: {'READY' if overall else 'NOT READY'}")
    if not overall:
        lines.append("")
        lines.append("Missing/failed gates:")
        for g in gates:
            if not g.passed:
                lines.append(f"- {g.label}")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        default="28_active_service_log_2026-04-07.csv",
        help="Path to active service log CSV",
    )
    parser.add_argument(
        "--today",
        default=date.today().isoformat(),
        help="Date override in YYYY-MM-DD",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Optional markdown output path",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    today = date.fromisoformat(args.today)
    row = load_solomon_row(csv_path)
    gates, overall = evaluate(row, today)
    report = render_markdown(row, gates, overall, today)
    print(report, end="")

    if args.out:
        out_path = Path(args.out)
        out_path.write_text(report, encoding="utf-8")

    raise SystemExit(0 if overall else 2)


if __name__ == "__main__":
    main()

