#!/usr/bin/env python3
"""Build Source -> Fact -> Rule -> Motion support map from generated reasoning artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


KG_DIR = Path("/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated")
OUT_JSON = KG_DIR / "motion_support_map.json"
OUT_MD = KG_DIR / "motion_support_map.md"

MOTION_FILES = {
    "gal": "/home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md",
    "dismiss": "/home/barberb/HACC/Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md",
    "show_cause": "/home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md",
}


def load_json(path: Path) -> Dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def recommend_motions(rule_id: str, action: str, actor: str) -> List[str]:
    text = f"{rule_id} {action} {actor}".lower()
    out: List[str] = []

    if any(k in text for k in ["show_cause", "appear", "service", "noncooperation", "abuse", "interfere", "comply"]):
        out.append(MOTION_FILES["show_cause"])

    if any(k in text for k in ["preclud", "relitigate", "collateral", "issue"]):
        out.append(MOTION_FILES["dismiss"])

    if any(k in text for k in ["guardian", "guardianship", "incapacitated", "protect"]):
        out.append(MOTION_FILES["gal"])

    if not out:
        out = [MOTION_FILES["show_cause"]]

    # stable unique
    seen = set()
    uniq = []
    for x in out:
        if x in seen:
            continue
        seen.add(x)
        uniq.append(x)
    return uniq


def build_map() -> Dict[str, object]:
    report = load_json(KG_DIR / "deontic_reasoning_report.json")
    kg = load_json(KG_DIR / "full_case_knowledge_graph.json")

    fact_index: Dict[str, Dict[str, object]] = {}
    for node in kg.get("nodes", []):
        if node.get("kind") == "fact" and str(node.get("id", "")).startswith("fact:"):
            fid = str(node["id"])[len("fact:") :]
            fact_index[fid] = node

    out: Dict[str, object] = {
        "generated_at": report.get("generated_at"),
        "modes": {},
    }

    for mode in ("strict", "inclusive"):
        entries = []
        active_rules = report["modes"][mode]["active_rules"]
        for rule in active_rules:
            c = rule["conclusion"]
            antecedent_details = []
            for ant in rule["antecedents"]:
                fid = ant["fact_id"]
                fn = fact_index.get(fid, {})
                antecedent_details.append(
                    {
                        "fact_id": fid,
                        "predicate": fn.get("predicate"),
                        "status": ant.get("status"),
                        "dates": ant.get("dates"),
                        "source": fn.get("source"),
                        "confidence_level": fn.get("confidence_level"),
                        "confidence_score": fn.get("confidence_score"),
                        "evidence_kind": fn.get("evidence_kind"),
                    }
                )

            motions = recommend_motions(rule["rule_id"], c.get("action", ""), c.get("actor", ""))
            entries.append(
                {
                    "rule_id": rule["rule_id"],
                    "track": rule.get("track"),
                    "authority_refs": rule.get("authority_refs", []),
                    "description": rule.get("description"),
                    "activation_date_estimate": rule.get("activation_date_estimate"),
                    "conclusion": c,
                    "antecedents": antecedent_details,
                    "recommended_motions": motions,
                }
            )

        out["modes"][mode] = {
            "entry_count": len(entries),
            "entries": entries,
        }

    return out


def to_markdown(data: Dict[str, object]) -> str:
    lines = ["# Motion Support Map", "", f"Generated: {data.get('generated_at')}", ""]

    for mode in ("strict", "inclusive"):
        block = data["modes"][mode]
        lines.append(f"## Mode: {mode}")
        lines.append(f"- Rules mapped: {block['entry_count']}")
        for e in block["entries"]:
            c = e["conclusion"]
            lines.append(f"- Rule: {e['rule_id']}")
            lines.append(f"- Track: {e.get('track')}")
            lines.append(f"- Authority refs: {e.get('authority_refs')}")
            lines.append(f"- Conclusion: {c.get('modality')}({c.get('actor')}, {c.get('action')}, {c.get('target')})")
            lines.append(f"- Activation date estimate: {e.get('activation_date_estimate')}")
            lines.append("- Antecedent evidence:")
            for ant in e["antecedents"]:
                lines.append(
                    f"- {ant['fact_id']} [{ant.get('status')}] {ant.get('predicate')} dates={ant.get('dates')} "
                    f"source={ant.get('source')} confidence={ant.get('confidence_level')}({ant.get('confidence_score')}) "
                    f"kind={ant.get('evidence_kind')}"
                )
            lines.append("- Recommended motions:")
            for m in e["recommended_motions"]:
                lines.append(f"- {m}")
            lines.append("")

    return "\n".join(lines) + "\n"


def main() -> None:
    data = build_map()
    OUT_JSON.write_text(json.dumps(data, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(data), encoding="utf-8")


if __name__ == "__main__":
    main()
