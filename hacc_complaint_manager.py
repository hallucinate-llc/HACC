#!/usr/bin/env python3
"""Compatibility alias for the HACC complaint-manager bridge."""

from importlib import import_module
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
IPFS_DATASETS_ROOT = COMPLAINT_GENERATOR_ROOT / "ipfs_datasets_py"
for root in (str(IPFS_DATASETS_ROOT), str(COMPLAINT_GENERATOR_ROOT)):
    if root not in sys.path:
        sys.path.insert(0, root)

_MODULE = import_module("ipfs_datasets_py.processors.legal_data_hacc.complaint_manager")
globals().update(_MODULE.__dict__)
sys.modules[__name__] = _MODULE
