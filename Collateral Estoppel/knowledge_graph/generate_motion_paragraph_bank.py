#!/usr/bin/env python3
"""Generate motion paragraph bank from motion support map."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


GEN = Path("/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated")
IN_MAP = GEN / "motion_support_map.json"
OUT_JSON = GEN / "motion_paragraph_bank.json"
OUT_MD = GEN / "motion_paragraph_bank.md"
PER_MOTION_DIR = GEN / "paragraph_bank_by_motion"


def basename(path: str | None) -> str:
    if not path:
        return "unknown_source"
    return Path(path).name


def build_paragraph(entry: Dict[str, object]) -> str:
    c = entry.get("conclusion", {})
    ants = entry.get("antecedents", [])
    evid_parts = []
    for ant in ants:
        evid_parts.append(
            f"{ant.get('fact_id')} ({ant.get('status')}, dates={ant.get('dates')}, "
            f"source={basename(ant.get('source'))}, confidence={ant.get('confidence_level')}({ant.get('confidence_score')}), "
            f"kind={ant.get('evidence_kind')})"
        )
    evid_blob = "; ".join(evid_parts) if evid_parts else "no antecedent evidence listed"

    return (
        f"Based on {evid_blob}, the rule {entry.get('rule_id')} yields "
        f"{c.get('modality')}({c.get('actor')}, {c.get('action')}, {c.get('target')}) "
        f"with activation estimate {entry.get('activation_date_estimate')}. "
        f"Movant requests relief consistent with this rule-grounded posture."
    )


def build_bank(data: Dict[str, object]) -> Dict[str, object]:
    out: Dict[str, object] = {
        "generated_at": data.get("generated_at"),
        "modes": {},
    }

    for mode, mdata in data.get("modes", {}).items():
        by_motion: Dict[str, List[Dict[str, object]]] = {}

        for entry in mdata.get("entries", []):
            para = build_paragraph(entry)
            for motion in entry.get("recommended_motions", []):
                by_motion.setdefault(motion, []).append(
                    {
                        "rule_id": entry.get("rule_id"),
                        "activation_date_estimate": entry.get("activation_date_estimate"),
                        "paragraph": para,
                    }
                )

        out["modes"][mode] = {
            "motions": by_motion,
        }

    return out


def to_markdown(bank: Dict[str, object]) -> str:
    lines = ["# Motion Paragraph Bank", "", f"Generated: {bank.get('generated_at')}", ""]

    for mode, mdata in bank.get("modes", {}).items():
        lines.append(f"## Mode: {mode}")
        motions = mdata.get("motions", {})
        for motion_path, paras in motions.items():
            lines.append(f"- Motion: {motion_path}")
            for idx, p in enumerate(paras, start=1):
                lines.append(f"- Paragraph {idx} [{p.get('rule_id')} @ {p.get('activation_date_estimate')}]")
                lines.append(f"- {p.get('paragraph')}")
            lines.append("")

    return "\n".join(lines) + "\n"


def _slug(s: str) -> str:
    out = []
    for ch in s.lower():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("_")
    # collapse underscores
    slug = "".join(out)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_")


def write_per_motion_files(bank: Dict[str, object]) -> None:
    PER_MOTION_DIR.mkdir(parents=True, exist_ok=True)
    for mode, mdata in bank.get("modes", {}).items():
        motions = mdata.get("motions", {})
        for motion_path, paras in motions.items():
            motion_name = basename(motion_path)
            slug = _slug(motion_name)
            target = PER_MOTION_DIR / f"{mode}__{slug}.md"
            lines = [
                "# Motion Paragraph Bank Slice",
                "",
                f"Generated: {bank.get('generated_at')}",
                f"Mode: {mode}",
                f"Motion: {motion_path}",
                "",
            ]
            for idx, p in enumerate(paras, start=1):
                lines.append(f"## Paragraph {idx}")
                lines.append(f"Rule: {p.get('rule_id')}")
                lines.append(f"Activation: {p.get('activation_date_estimate')}")
                lines.append("")
                lines.append(p.get("paragraph", ""))
                lines.append("")
            target.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    data = json.loads(IN_MAP.read_text(encoding="utf-8"))
    bank = build_bank(data)
    OUT_JSON.write_text(json.dumps(bank, indent=2), encoding="utf-8")
    OUT_MD.write_text(to_markdown(bank), encoding="utf-8")
    write_per_motion_files(bank)


if __name__ == "__main__":
    main()
