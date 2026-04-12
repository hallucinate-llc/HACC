"""Compatibility wrapper for the HACC research engine."""

from __future__ import annotations

from importlib import import_module
from pathlib import Path
from typing import Any
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
IPFS_DATASETS_ROOT = COMPLAINT_GENERATOR_ROOT / "ipfs_datasets_py"
for root in (str(IPFS_DATASETS_ROOT), str(COMPLAINT_GENERATOR_ROOT)):
    if root not in sys.path:
        sys.path.insert(0, root)

_IMPL = import_module("ipfs_datasets_py.processors.legal_data_hacc.research_engine")
_SKIP_SYNC = {
    "HACCResearchEngine",
    "CorpusDocument",
    "main",
}

for _name, _value in _IMPL.__dict__.items():
    if _name.startswith("__"):
        continue
    globals()[_name] = _value


def _sync_impl_globals() -> None:
    for name, value in globals().items():
        if name.startswith("__") or name in _SKIP_SYNC:
            continue
        if name in _IMPL.__dict__:
            setattr(_IMPL, name, value)


class HACCResearchEngine(_IMPL.HACCResearchEngine):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        _sync_impl_globals()
        super().__init__(*args, **kwargs)


def main(argv: list[str] | None = None) -> int:
    _sync_impl_globals()
    return _IMPL.main(argv)
