"""
Export the Title 18 GraphRAG obligation report into machine-consumable reasoning formats.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any, Dict, Iterable, List


ROOT = Path("/home/barberb/HACC/Breach of Contract")
REPORT_PATH = ROOT / "outputs" / "title18_graphrag_obligations.json"
OUTPUT_DIR = ROOT / "outputs"


def _load_report() -> Dict[str, Any]:
    return json.loads(REPORT_PATH.read_text())


def _atom(value: str) -> str:
    token = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return token or "unknown"


def _quote(value: str) -> str:
    escaped = (value or "").replace("\\", "\\\\").replace("\"", "\\\"")
    return f'"{escaped}"'


def _iter_obligations(report: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
    return report.get("obligations", [])


def build_prolog_export(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "% title18_obligations.pl",
        "% Generated from the Title 18 GraphRAG obligation analysis",
        "",
        "% ---------- Parties ----------",
    ]
    for party_id, party in sorted(report["parties"].items()):
        party_atom = _atom(party_id)
        lines.append(f"party({party_atom}).")
        lines.append(f"party_name({party_atom}, {_quote(party['name'])}).")
        lines.append(f"party_role({party_atom}, {_quote(party['role'])}).")
    lines.extend([
        "",
        "% ---------- Obligations ----------",
    ])
    for item in _iter_obligations(report):
        obligation_atom = _atom(item["obligation_id"])
        actor_atom = _atom(item["actor"])
        recipient_atom = _atom(item["recipient"])
        action_atom = _atom(item["action"])
        lines.append(f"obligation({obligation_atom}).")
        lines.append(f"actor({obligation_atom}, {actor_atom}).")
        lines.append(f"recipient({obligation_atom}, {recipient_atom}).")
        lines.append(f"modality({obligation_atom}, {_atom(item['modality'])}).")
        lines.append(f"action({obligation_atom}, {action_atom}).")
        lines.append(f"action_text({obligation_atom}, {_quote(item['action'])}).")
        lines.append(f"temporal_status({obligation_atom}, {_atom(item['temporal_status'])}).")
        lines.append(f"breach_state({obligation_atom}, {_atom(item['breach_state'])}).")
        if item.get("trigger_date"):
            lines.append(f"trigger_date({obligation_atom}, {_quote(item['trigger_date'])}).")
        if item.get("due_date"):
            lines.append(f"due_date({obligation_atom}, {_quote(item['due_date'])}).")
        lines.append(f"legal_basis({obligation_atom}, {_quote(item['legal_basis'])}).")
        for event_id in item.get("event_ids", []):
            lines.append(f"triggered_by({obligation_atom}, {_atom(event_id)}).")
        for document in item.get("source_documents", []):
            lines.append(f"source_document({obligation_atom}, {_quote(document)}).")
        lines.append("")
    lines.extend([
        "% ---------- Derived predicates ----------",
        "active_obligation(O) :- modality(O, obligatory), temporal_status(O, active).",
        "overdue_obligation(O) :- modality(O, obligatory), breach_state(O, overdue).",
        "potential_prohibition_breach(O) :- modality(O, prohibited), breach_state(O, potential_breach).",
    ])
    return "\n".join(lines).rstrip() + "\n"


def build_dcec_export(report: Dict[str, Any]) -> str:
    formal_models = report["formalModels"]
    dcec = formal_models["deonticCognitiveEventCalculus"]
    lines: List[str] = [
        "% title18_obligations_dcec.pl",
        "% Deontic cognitive event calculus export for the Title 18 demolition record",
        "",
        "% Happens(Event, Time)",
        "% Initiates(Event, Fluent, Time)",
        "% HoldsAt(Fluent, Time)",
        "",
    ]
    for formula in dcec.get("happens", []):
        lines.append(f"{formula}.")
    lines.append("")
    for item in dcec.get("initiates", []):
        lines.append(f"{item['formula']}.")
    lines.append("")
    for item in dcec.get("holdsAt", []):
        lines.append(f"{item['formula']}.")
    if dcec.get("breaches"):
        lines.append("")
        for item in dcec.get("breaches", []):
            lines.append(f"{item['formula']}.")
    return "\n".join(lines).rstrip() + "\n"


def build_flogic_export(report: Dict[str, Any]) -> str:
    lines: List[str] = [
        "%% title18_obligations.flogic",
        "%% F-logic style export for the Title 18 demolition obligation graph",
        "",
    ]
    for party_id, party in sorted(report["parties"].items()):
        party_atom = _atom(party_id)
        lines.append(f"{party_atom}:party[")
        lines.append(f"  name -> {_quote(party['name'])};")
        lines.append(f"  role -> {_quote(party['role'])};")
        lines.append(f"  mentions -> {party['mentions']}")
        lines.append("] .")
        lines.append("")
    for item in _iter_obligations(report):
        obligation_atom = _atom(item["obligation_id"])
        documents = ", ".join(_quote(doc) for doc in item.get("source_documents", [])) or ""
        events = ", ".join(_quote(event_id) for event_id in item.get("event_ids", [])) or ""
        lines.append(f"{obligation_atom}:obligation[")
        lines.append(f"  actor -> {_atom(item['actor'])};")
        lines.append(f"  recipient -> {_atom(item['recipient'])};")
        lines.append(f"  modality -> {_quote(item['modality'])};")
        lines.append(f"  actionText -> {_quote(item['action'])};")
        lines.append(f"  legalBasis -> {_quote(item['legal_basis'])};")
        lines.append(f"  temporalStatus -> {_quote(item['temporal_status'])};")
        lines.append(f"  breachState -> {_quote(item['breach_state'])};")
        if item.get("trigger_date"):
            lines.append(f"  triggerDate -> {_quote(item['trigger_date'])};")
        if item.get("due_date"):
            lines.append(f"  dueDate -> {_quote(item['due_date'])};")
        lines.append(f"  sourceDocuments -> set{{{documents}}};")
        lines.append(f"  triggerEvents -> set{{{events}}}")
        lines.append("] .")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_manifest(report: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "generatedFrom": str(REPORT_PATH),
        "generatedAt": report["metadata"]["generatedAt"],
        "documentsScanned": report["metadata"]["documentsScanned"],
        "eventsExtracted": report["metadata"]["eventsExtracted"],
        "obligationCount": len(report.get("obligations", [])),
        "exports": [
            "title18_obligations.pl",
            "title18_obligations_dcec.pl",
            "title18_obligations.flogic",
        ],
    }


def write_reasoning_exports(report: Dict[str, Any] | None = None) -> Dict[str, Path]:
    report = report or _load_report()
    outputs = {
        "prolog": OUTPUT_DIR / "title18_obligations.pl",
        "dcec": OUTPUT_DIR / "title18_obligations_dcec.pl",
        "flogic": OUTPUT_DIR / "title18_obligations.flogic",
        "manifest": OUTPUT_DIR / "title18_reasoning_exports_manifest.json",
    }
    outputs["prolog"].write_text(build_prolog_export(report))
    outputs["dcec"].write_text(build_dcec_export(report))
    outputs["flogic"].write_text(build_flogic_export(report))
    outputs["manifest"].write_text(json.dumps(build_manifest(report), indent=2) + "\n")
    return outputs


def main() -> int:
    paths = write_reasoning_exports()
    for path in paths.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())