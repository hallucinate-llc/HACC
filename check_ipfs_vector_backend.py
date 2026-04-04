#!/usr/bin/env python3
"""Health check for ipfs_datasets/ipfs_accelerate embedding vector generation.

This script verifies:
1) vector backend readiness
2) optional smoke-test vector index generation

Exit codes:
0 = healthy
1 = unhealthy (backend unavailable or smoke test failed)
2 = usage/environment failure
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from hacc_complaint_manager import COMPLAINT_GENERATOR_ROOT, ensure_complaint_generator_on_path


def _jsonable(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    if isinstance(value, dict):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "as_dict") and callable(getattr(value, "as_dict")):
        return _jsonable(value.as_dict())
    if hasattr(value, "dict") and callable(getattr(value, "dict")):
        return _jsonable(value.dict())
    return str(value)


def _smoke_docs() -> List[Dict[str, Any]]:
    return [
        {
            "id": "smoke-1",
            "text": "Tenant complaint evidence timeline with notice and lease terms.",
            "metadata": {"source": "healthcheck", "kind": "sample"},
        },
        {
            "id": "smoke-2",
            "text": "Housing authority correspondence and potential policy violations.",
            "metadata": {"source": "healthcheck", "kind": "sample"},
        },
    ]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check ipfs_datasets/ipfs_accelerate vector embedding backend health"
    )
    parser.add_argument(
        "--skip-smoke-test",
        action="store_true",
        help="Only run backend readiness checks; skip embedding/index smoke test",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=2,
        help="Batch size for smoke-test embedding",
    )
    parser.add_argument(
        "--output-json",
        default="",
        help="Optional path to write full health report JSON",
    )
    args = parser.parse_args()

    if not COMPLAINT_GENERATOR_ROOT.exists():
        print(
            json.dumps(
                {
                    "status": "error",
                    "error": f"complaint-generator root not found: {COMPLAINT_GENERATOR_ROOT}",
                },
                indent=2,
            )
        )
        return 2

    ensure_complaint_generator_on_path()

    from integrations.ipfs_datasets.vector_store import (
        create_vector_index,
        embeddings_backend_status,
        vector_index_backend_status,
    )

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "unknown",
        "checks": {},
    }

    emb_status = _jsonable(embeddings_backend_status(perform_probe=True))
    vec_status = _jsonable(vector_index_backend_status(require_local_persistence=True))

    report["checks"]["embeddings_backend_status"] = emb_status
    report["checks"]["vector_index_backend_status"] = vec_status

    smoke_status: Dict[str, Any] = {
        "status": "skipped" if args.skip_smoke_test else "pending"
    }
    smoke_ok = True
    if not args.skip_smoke_test:
        tmp_dir = Path(tempfile.mkdtemp(prefix="ipfs_vector_health_"))
        try:
            result = _jsonable(
                create_vector_index(
                    _smoke_docs(),
                    index_name="healthcheck_vector_index",
                    output_dir=str(tmp_dir),
                    batch_size=args.batch_size,
                )
            )
            smoke_status = {
                "status": str(result.get("status") or "unknown"),
                "error": result.get("error") or "",
                "provider": result.get("provider") or "",
                "dimension": result.get("dimension") or 0,
                "metadata": result.get("metadata") or {},
            }
            smoke_ok = smoke_status["status"] == "success"
        except Exception as exc:
            smoke_status = {"status": "error", "error": str(exc)}
            smoke_ok = False
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)

    report["checks"]["smoke_test_vector_index"] = smoke_status

    emb_ok = str(emb_status.get("status") or "").lower() in {"available", "degraded"}
    vec_ok = str(vec_status.get("status") or "").lower() == "available"
    healthy = emb_ok and vec_ok and smoke_ok
    report["status"] = "healthy" if healthy else "unhealthy"

    if args.output_json:
        output_path = Path(args.output_json).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if healthy else 1


if __name__ == "__main__":
    raise SystemExit(main())
