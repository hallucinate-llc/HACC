"""
Shared render-context loader for Title 18 filing artifacts.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, List


ROOT = Path("/home/barberb/HACC/Breach of Contract")
OVERRIDES_PATH = ROOT / "title18_render_context_overrides.json"


def _normalize_override_paths(
    override_path: Path | str | None = None,
    override_paths: Iterable[Path | str] | None = None,
) -> List[Path]:
    if override_paths is not None:
        raw_paths = list(override_paths)
    elif override_path is not None:
        raw_paths = [override_path]
    else:
        raw_paths = [OVERRIDES_PATH]
    normalized: List[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path not in normalized:
            normalized.append(path)
    return normalized


def _load_context_overrides(
    override_path: Path | str | None = None,
    override_paths: Iterable[Path | str] | None = None,
) -> Dict[str, Any]:
    substitutions: Dict[str, Any] = {}
    required_user_inputs: Dict[str, Any] = {}
    loaded_paths: List[str] = []
    for path in _normalize_override_paths(override_path=override_path, override_paths=override_paths):
        if not path.exists():
            continue
        payload = json.loads(path.read_text())
        substitutions.update(
            {
                key: value
                for key, value in payload.get("substitutions", {}).items()
                if value is not None
            }
        )
        required_user_inputs.update(
            {
                key: value
                for key, value in payload.get("requiredUserInputs", {}).items()
                if value is not None
            }
        )
        loaded_paths.append(str(path))
    return {
        "substitutions": substitutions,
        "requiredUserInputs": required_user_inputs,
        "overridePaths": loaded_paths,
    }


def build_render_context(
    override_path: Path | str | None = None,
    override_paths: Iterable[Path | str] | None = None,
) -> Dict[str, Any]:
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
    normalized_paths = _normalize_override_paths(override_path=override_path, override_paths=override_paths)
    overrides = _load_context_overrides(override_paths=normalized_paths)
    substitutions.update(overrides["substitutions"])
    required_user_inputs.update(overrides["requiredUserInputs"])
    return {
        "meta": {
            "contextId": "title18_render_context_001",
            "description": "Shared placeholder substitutions for generated Title 18 filings.",
            "overridePath": str(normalized_paths[0]),
            "overridePaths": overrides["overridePaths"] or [str(path) for path in normalized_paths],
        },
        "substitutions": substitutions,
        "requiredUserInputs": required_user_inputs,
    }