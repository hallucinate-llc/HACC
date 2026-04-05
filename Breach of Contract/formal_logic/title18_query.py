"""
Query and summarize the generated Title 18 obligation analysis artifacts.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"
REPORT_PATH = OUTPUTS / "title18_graphrag_obligations.json"


PRESET_FILTERS: Dict[str, Dict[str, str]] = {
    "hacc-overdue": {"actor": "org:hacc", "temporal_status": "overdue"},
    "quantum-overdue": {"actor": "org:quantum", "temporal_status": "overdue"},
    "hud-oversight": {"actor": "org:hud"},
    "resident-prohibitions": {"modality": "prohibited"},
    "potential-breaches": {"breach_state": "potential_breach"},
    "overdue": {"temporal_status": "overdue"},
    "quantum-intake": {"actor": "org:quantum"},
    "benjamin-owed": {"recipient": "person:benjamin_barber"},
    "jane-owed": {"recipient": "person:jane_cortez"},
    "hacc-prohibited": {"actor": "org:hacc", "modality": "prohibited"},
}


def load_report() -> Dict[str, Any]:
    return json.loads(REPORT_PATH.read_text())


def query_obligations(
    report: Dict[str, Any],
    *,
    actor: Optional[str] = None,
    recipient: Optional[str] = None,
    modality: Optional[str] = None,
    temporal_status: Optional[str] = None,
    breach_state: Optional[str] = None,
) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for item in report.get("obligations", []):
        if actor and item["actor"] != actor:
            continue
        if recipient and item["recipient"] != recipient:
            continue
        if modality and item["modality"] != modality:
            continue
        if temporal_status and item["temporal_status"] != temporal_status:
            continue
        if breach_state and item["breach_state"] != breach_state:
            continue
        results.append(item)
    return results


def build_query_summary(obligations: Sequence[Dict[str, Any]], report: Dict[str, Any]) -> Dict[str, Any]:
    by_actor: Dict[str, int] = {}
    by_recipient: Dict[str, int] = {}
    by_status: Dict[str, int] = {}
    by_breach: Dict[str, int] = {}
    for item in obligations:
        by_actor[item["actor"]] = by_actor.get(item["actor"], 0) + 1
        by_recipient[item["recipient"]] = by_recipient.get(item["recipient"], 0) + 1
        by_status[item["temporal_status"]] = by_status.get(item["temporal_status"], 0) + 1
        by_breach[item["breach_state"]] = by_breach.get(item["breach_state"], 0) + 1
    return {
        "count": len(obligations),
        "byActor": dict(sorted(by_actor.items())),
        "byRecipient": dict(sorted(by_recipient.items())),
        "byTemporalStatus": dict(sorted(by_status.items())),
        "byBreachState": dict(sorted(by_breach.items())),
        "documentsScanned": report["metadata"]["documentsScanned"],
        "eventsExtracted": report["metadata"]["eventsExtracted"],
    }


def build_dashboard(report: Dict[str, Any]) -> Dict[str, Any]:
    overdue = query_obligations(report, temporal_status="overdue")
    prohibited = query_obligations(report, modality="prohibited")
    hacc = query_obligations(report, actor="org:hacc")
    quantum = query_obligations(report, actor="org:quantum")
    hud = query_obligations(report, actor="org:hud")
    return {
        "meta": {
            "generatedAt": report["metadata"]["generatedAt"],
            "source": str(REPORT_PATH),
        },
        "headline": {
            "totalObligations": len(report["obligations"]),
            "overdueObligations": len(overdue),
            "prohibitedActsTracked": len(prohibited),
            "potentialBreaches": len(query_obligations(report, breach_state="potential_breach")),
        },
        "byParty": {
            "org:hacc": build_query_summary(hacc, report),
            "org:quantum": build_query_summary(quantum, report),
            "org:hud": build_query_summary(hud, report),
        },
        "overdue": overdue,
        "prohibited": prohibited,
    }


def available_presets() -> List[str]:
    return sorted(PRESET_FILTERS)


def run_preset(report: Dict[str, Any], preset: str) -> Dict[str, Any]:
    if preset not in PRESET_FILTERS:
        raise KeyError(preset)
    obligations = query_obligations(report, **PRESET_FILTERS[preset])
    return {
        "preset": preset,
        "filters": PRESET_FILTERS[preset],
        "summary": build_query_summary(obligations, report),
        "obligations": obligations,
    }


def render_query_markdown(summary: Dict[str, Any], obligations: Sequence[Dict[str, Any]]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Obligation Query")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Obligation count: {summary['count']}")
    lines.append(f"- Documents scanned: {summary['documentsScanned']}")
    lines.append(f"- Events extracted: {summary['eventsExtracted']}")
    if summary["byActor"]:
        lines.append(f"- By actor: {summary['byActor']}")
    if summary["byTemporalStatus"]:
        lines.append(f"- By temporal status: {summary['byTemporalStatus']}")
    if summary["byBreachState"]:
        lines.append(f"- By breach state: {summary['byBreachState']}")
    lines.append("")
    lines.append("## Obligations")
    lines.append("")
    for item in obligations:
        lines.append(f"- {item['actor']} -> {item['recipient']}: {item['action']}")
        lines.append(f"  Modality: {item['modality']}; Status: {item['temporal_status']}; Breach: {item['breach_state']}")
        if item.get("trigger_date") or item.get("due_date"):
            lines.append(f"  Trigger: {item.get('trigger_date')}; Due: {item.get('due_date')}")
    return "\n".join(lines).rstrip() + "\n"


def render_dashboard_markdown(dashboard: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# Title 18 Obligation Dashboard")
    lines.append("")
    lines.append("## Headline")
    lines.append("")
    for key, value in dashboard["headline"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("## By Party")
    lines.append("")
    for party_id, summary in dashboard["byParty"].items():
        lines.append(f"- {party_id}: {summary['count']} obligations")
        lines.append(f"  Statuses: {summary['byTemporalStatus']}")
        lines.append(f"  Breach states: {summary['byBreachState']}")
    lines.append("")
    lines.append("## Overdue")
    lines.append("")
    for item in dashboard["overdue"]:
        lines.append(f"- {item['actor']} -> {item['recipient']}: {item['action']} (due {item.get('due_date')})")
    lines.append("")
    lines.append("## Prohibited")
    lines.append("")
    for item in dashboard["prohibited"]:
        lines.append(f"- {item['actor']} -> {item['recipient']}: {item['action']} ({item['breach_state']})")
    return "\n".join(lines).rstrip() + "\n"


def write_dashboard(report: Dict[str, Any] | None = None) -> Dict[str, Path]:
    report = report or load_report()
    dashboard = build_dashboard(report)
    outputs = {
        "json": OUTPUTS / "title18_obligation_dashboard.json",
        "markdown": OUTPUTS / "title18_obligation_dashboard.md",
    }
    outputs["json"].write_text(json.dumps(dashboard, indent=2) + "\n")
    outputs["markdown"].write_text(render_dashboard_markdown(dashboard))
    return outputs


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Query the generated Title 18 obligation report.")
    parser.add_argument("--preset")
    parser.add_argument("--list-presets", action="store_true")
    parser.add_argument("--actor")
    parser.add_argument("--recipient")
    parser.add_argument("--modality")
    parser.add_argument("--status", dest="temporal_status")
    parser.add_argument("--breach-state")
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--write-dashboard", action="store_true")
    args = parser.parse_args(argv)

    report = load_report()
    if args.list_presets:
        for item in available_presets():
            print(item)
        return 0
    if args.write_dashboard:
        outputs = write_dashboard(report)
        for path in outputs.values():
            print(path)
        return 0

    if args.dashboard:
        dashboard = build_dashboard(report)
        if args.as_json:
            print(json.dumps(dashboard, indent=2))
        else:
            print(render_dashboard_markdown(dashboard))
        return 0

    if args.preset:
        payload = run_preset(report, args.preset)
        if args.as_json:
            print(json.dumps(payload, indent=2))
        else:
            print(render_query_markdown(payload["summary"], payload["obligations"]))
        return 0

    obligations = query_obligations(
        report,
        actor=args.actor,
        recipient=args.recipient,
        modality=args.modality,
        temporal_status=args.temporal_status,
        breach_state=args.breach_state,
    )
    summary = build_query_summary(obligations, report)
    if args.as_json:
        print(json.dumps({"summary": summary, "obligations": obligations}, indent=2))
    else:
        print(render_query_markdown(summary, obligations))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())