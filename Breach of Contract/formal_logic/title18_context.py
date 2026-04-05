"""
Shared render-context loader for Title 18 filing artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OVERRIDES_PATH = ROOT / "title18_render_context_overrides.json"


def _load_context_overrides(override_path: Path | None = None) -> Dict[str, Any]:
    override_path = override_path or OVERRIDES_PATH
    if not override_path.exists():
        return {"substitutions": {}, "requiredUserInputs": {}}
    payload = json.loads(override_path.read_text())
    substitutions = {
        key: value
        for key, value in payload.get("substitutions", {}).items()
        if value is not None
    }
    required_user_inputs = {
        key: value
        for key, value in payload.get("requiredUserInputs", {}).items()
        if value is not None
    }
    return {
        "substitutions": substitutions,
        "requiredUserInputs": required_user_inputs,
    }


def build_render_context(override_path: Path | None = None) -> Dict[str, Any]:
    substitutions = {
        "[DATE]": "April 5, 2026",
        "[date]": "April 5, 2026",
        "[FOR THE COUNTY OF [COUNTY]]": "FOR THE COUNTY OF CLACKAMAS",
        "[COUNTY]": "CLACKAMAS",
        "[IN THE CIRCUIT COURT OF THE STATE OF OREGON]": "IN THE CIRCUIT COURT OF THE STATE OF OREGON",
        "[TENANT FIRST NAMES]": "Benjamin Jay Barber and Jane Kay Cortez",
        "[TENANT NAMES]": "Benjamin Jay Barber and Jane Kay Cortez",
        "[DEFENDANT NAME]": "Benjamin Jay Barber and Jane Kay Cortez",
        "[DEFENDANT NAMES]": "Benjamin Jay Barber and Jane Kay Cortez",
        "[PLAINTIFF NAME]": "HOUSING AUTHORITY OF CLACKAMAS COUNTY",
        "[STATE OF OREGON / COUNTY / COURT NAME]": "IN THE CIRCUIT COURT OF THE STATE OF OREGON FOR THE COUNTY OF CLACKAMAS",
        "[Insert third option as reflected in documents/communications]": "Blossom & Community Apartments intake and PBV replacement-housing path",
    }
    required_user_inputs = {
        "[CASE NUMBER]": None,
        "[COUNTY]": None,
        "[JUDGE NAME]": None,
        "[YOUR NAME & BAR NUMBER]": None,
        "[YOUR ADDRESS]": None,
        "[YOUR PHONE]": None,
        "[YOUR EMAIL]": None,
        "[ADDRESS]": None,
        "[Address]": None,
        "[EMAIL]": None,
        "[Email]": None,
        "[PHONE]": None,
        "[Phone]": None,
        "[HACC COUNSEL NAME]": None,
        "[HACC COUNSEL ADDRESS]": None,
        "[HACC COUNSEL PHONE]": None,
        "[HACC COUNSEL EMAIL]": None,
        "[QUANTUM'S REGISTERED AGENT NAME]": None,
        "[QUANTUM'S REGISTERED AGENT ADDRESS]": None,
        "[FULL LEGAL ENTITY NAME]": None,
        "[full legal entity name]": None,
        "[Defendant name]": None,
        "[insert schedule]": None,
        "[GRANTED / DENIED]": None,
        "[GRANTED / DENIED / STAYED]": None,
        "[IN THE CIRCUIT COURT OF THE STATE OF OREGON]": None,
        "[FOR THE COUNTY OF [COUNTY]]": None,
        "[SIGNATURE]": None,
        "[Signature]": None,
        "[Signature block]": None,
        "[NAME]": None,
        "[Name]": None,
        "[name]": None,
        "[SERVICE METHOD]": None,
    }
    overrides = _load_context_overrides(override_path)
    substitutions.update(overrides["substitutions"])
    required_user_inputs.update(overrides["requiredUserInputs"])
    return {
        "meta": {
            "contextId": "title18_render_context_001",
            "description": "Shared placeholder substitutions for generated Title 18 filings.",
            "overridePath": str(override_path or OVERRIDES_PATH),
        },
        "substitutions": substitutions,
        "requiredUserInputs": required_user_inputs,
    }