#!/usr/bin/env python3
"""Compatibility wrapper for the HACC grounded pipeline."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any
import sys


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
IPFS_DATASETS_ROOT = COMPLAINT_GENERATOR_ROOT / "ipfs_datasets_py"
for root in (str(IPFS_DATASETS_ROOT), str(COMPLAINT_GENERATOR_ROOT)):
    if root not in sys.path:
        sys.path.insert(0, root)

_IMPL = import_module("ipfs_datasets_py.processors.legal_data_hacc.grounded_pipeline")
_SYNC_NAMES = {
    "HACCResearchEngine",
    "run_hacc_adversarial_batch",
    "_run_complaint_synthesis",
}

for _name, _value in _IMPL.__dict__.items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value


def _sync_impl_globals() -> None:
    for name in _SYNC_NAMES:
        if name in globals():
            setattr(_IMPL, name, globals()[name])


def run_hacc_grounded_pipeline(*args: Any, **kwargs: Any):
    _sync_impl_globals()
    return _IMPL.run_hacc_grounded_pipeline(*args, **kwargs)


def main(argv: list[str] | None = None) -> int:
    _sync_impl_globals()
    return _IMPL.main(argv)
