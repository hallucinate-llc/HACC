"""
Render Title 18 filing drafts with a shared placeholder-substitution context.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping

from formal_logic.title18_context import build_render_context
from formal_logic.title18_merged_motion import build_title18_merged_motion, render_title18_merged_motion_markdown
from formal_logic.title18_party_drafts import (
    build_hacc_party_motion,
    build_quantum_party_motion,
    render_party_motion_markdown,
)


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OUTPUTS = ROOT / "outputs"
PLACEHOLDER_PATTERN = re.compile(r"\[[A-Za-z0-9&'._/ -]+\]")
PLACEHOLDER_ALIASES = {
    "[Address]": "[ADDRESS]",
    "[Email]": "[EMAIL]",
    "[Phone]": "[PHONE]",
    "[Name]": "[NAME]",
    "[name]": "[NAME]",
    "[Defendant name]": "[DEFENDANT NAME]",
    "[full legal entity name]": "[FULL LEGAL ENTITY NAME]",
    "[PRINTED NAME]": "[NAME]",
    "[Signature]": "[SIGNATURE]",
    "[Signature block]": "[SIGNATURE]",
}


def _apply_substitutions(text: str, context: Mapping[str, Any]) -> str:
    substitutions = context["substitutions"]
    required_inputs = context["requiredUserInputs"]
    rendered = text
    items = sorted(
        {**required_inputs, **substitutions}.items(),
        key=lambda item: len(item[0]),
        reverse=True,
    )
    for placeholder, value in items:
        if value:
            rendered = rendered.replace(placeholder, str(value))
    return rendered


def _render_value(value: Any, context: Mapping[str, Any]) -> Any:
    if isinstance(value, str):
        return _apply_substitutions(value, context)
    if isinstance(value, list):
        return [_render_value(item, context) for item in value]
    if isinstance(value, dict):
        return {key: _render_value(item, context) for key, item in value.items()}
    return value


def _collect_placeholders(values: Iterable[str]) -> List[str]:
    placeholders = set()
    for value in values:
        for match in PLACEHOLDER_PATTERN.findall(value):
            inner = match[1:-1].strip()
            if len(inner) < 4:
                continue
            if not any(character.isalpha() for character in inner):
                continue
            placeholders.add(PLACEHOLDER_ALIASES.get(match, match))
    return sorted(placeholders)


def _flatten_strings(value: Any) -> List[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        flattened: List[str] = []
        for item in value:
            flattened.extend(_flatten_strings(item))
        return flattened
    if isinstance(value, dict):
        flattened = []
        for item in value.values():
            flattened.extend(_flatten_strings(item))
        return flattened
    return []


def build_rendered_title18_filings(merged_order_track: str = "hacc") -> Dict[str, Any]:
    context = build_render_context()
    documents = {
        "merged_motion": {
            "sourceId": "title18_merged_motion_001",
            "json": build_title18_merged_motion(order_track=merged_order_track),
            "markdown": render_title18_merged_motion_markdown(build_title18_merged_motion(order_track=merged_order_track)),
        },
        "hacc_party_motion": {
            "sourceId": "title18_hacc_party_motion_001",
            "json": build_hacc_party_motion(),
            "markdown": render_party_motion_markdown(build_hacc_party_motion()),
        },
        "quantum_party_motion": {
            "sourceId": "title18_quantum_party_motion_001",
            "json": build_quantum_party_motion(),
            "markdown": render_party_motion_markdown(build_quantum_party_motion()),
        },
    }

    rendered_documents: Dict[str, Any] = {}
    manifest_documents: List[Dict[str, Any]] = []

    for key, payload in documents.items():
        rendered_json = _render_value(payload["json"], context)
        rendered_markdown = _apply_substitutions(payload["markdown"], context)
        unresolved = _collect_placeholders(_flatten_strings(rendered_json) + [rendered_markdown])
        rendered_documents[key] = {
            "sourceId": payload["sourceId"],
            "renderedJson": rendered_json,
            "renderedMarkdown": rendered_markdown,
            "unresolvedPlaceholders": unresolved,
        }
        manifest_documents.append(
            {
                "documentKey": key,
                "sourceId": payload["sourceId"],
                "unresolvedPlaceholders": unresolved,
            }
        )

    return {
        "context": context,
        "documents": rendered_documents,
        "manifest": {
            "renderId": "title18_render_manifest_001",
            "mergedOrderTrack": merged_order_track,
            "documents": manifest_documents,
        },
    }


def write_rendered_title18_filings(bundle: Dict[str, Any] | None = None, merged_order_track: str = "hacc") -> Dict[str, Path]:
    bundle = bundle or build_rendered_title18_filings(merged_order_track=merged_order_track)
    outputs = {
        "context_json": OUTPUTS / "title18_render_context.json",
        "manifest_json": OUTPUTS / "title18_render_manifest.json",
        "merged_json": OUTPUTS / "title18_merged_motion_rendered.json",
        "merged_markdown": OUTPUTS / "title18_merged_motion_rendered.md",
        "hacc_json": OUTPUTS / "title18_hacc_party_motion_rendered.json",
        "hacc_markdown": OUTPUTS / "title18_hacc_party_motion_rendered.md",
        "quantum_json": OUTPUTS / "title18_quantum_party_motion_rendered.json",
        "quantum_markdown": OUTPUTS / "title18_quantum_party_motion_rendered.md",
    }
    outputs["context_json"].write_text(json.dumps(bundle["context"], indent=2) + "\n")
    outputs["manifest_json"].write_text(json.dumps(bundle["manifest"], indent=2) + "\n")
    outputs["merged_json"].write_text(json.dumps(bundle["documents"]["merged_motion"]["renderedJson"], indent=2) + "\n")
    outputs["merged_markdown"].write_text(bundle["documents"]["merged_motion"]["renderedMarkdown"])
    outputs["hacc_json"].write_text(json.dumps(bundle["documents"]["hacc_party_motion"]["renderedJson"], indent=2) + "\n")
    outputs["hacc_markdown"].write_text(bundle["documents"]["hacc_party_motion"]["renderedMarkdown"])
    outputs["quantum_json"].write_text(json.dumps(bundle["documents"]["quantum_party_motion"]["renderedJson"], indent=2) + "\n")
    outputs["quantum_markdown"].write_text(bundle["documents"]["quantum_party_motion"]["renderedMarkdown"])
    return outputs


def main() -> int:
    outputs = write_rendered_title18_filings()
    for path in outputs.values():
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())