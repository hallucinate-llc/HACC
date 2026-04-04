#!/usr/bin/env python3
"""Authority fit helpers shared across grounding and review outputs."""

from __future__ import annotations

from typing import Any, Dict


FIT_KIND_BY_ID = {
    "giebeler": "analogical",
    "california_mobile_home": "direct",
    "mcgary": "analogical",
    "hud_joint_statement": "direct",
    "cfr_982_316": "direct",
}


def infer_fit_kind(authority: Dict[str, Any]) -> str:
    explicit = authority.get("fitKind")
    if explicit in {"direct", "analogical", "record_support"}:
        return explicit

    text = " ".join(
        str(authority.get(key, "")).lower()
        for key in ("notes", "proposition", "excerptText")
    )
    if any(token in text for token in ("record", "documentation", "clarif", "factual")):
        return "record_support"

    return FIT_KIND_BY_ID.get(authority.get("id"), "analogical")
