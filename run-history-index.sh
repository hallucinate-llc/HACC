#!/usr/bin/env bash
# run-history-index.sh — Health check + dated evidence history indexing run
#
# Usage:
#   ./run-history-index.sh [--full-smoke-test] [--output-dir DIR] [--skip-preflight] [--cpu-only] [--fast|--max-throughput] [EXTRA_ARGS...]
#
# Options:
#   --full-smoke-test   Run the vector smoke test in the pre-run health check (slower, more thorough)
#   --output-dir DIR    Override the auto-generated dated output directory
#   --skip-preflight    Skip the external health check (built-in preflight still runs inside indexer)
#   --cpu-only          Force CPU embeddings (disables CUDA usage)
#   --fast              Favor lower memory footprint and shorter startup
#   --max-throughput    Favor maximum sustained throughput (default profile)
#   --duckdb-query Q    Add a post-run DuckDB spot-check query (repeatable)
#   --semantic-query Q  Add a post-run semantic spot-check query (repeatable)
#   --bundle-output-dir DIR  Export the finished index into a bundle directory/archive location
#   --bundle-format FMT      Add bundle artifact(s): zip, parquet, car (repeatable)
#   Any remaining args are forwarded verbatim to the indexer.
#
# Exit codes:
#   0  Indexing completed successfully
#   1  External health check failed (venv/backend unhealthy)
#   2  Health check script environment failure
#   3  Indexer built-in preflight failed
#   4  Indexer itself failed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
HEALTH_SCRIPT="${HACC_HEALTH_SCRIPT:-${SCRIPT_DIR}/check_ipfs_vector_backend.py}"
INDEX_SCRIPT="${HACC_HISTORY_INDEX_SCRIPT:-${SCRIPT_DIR}/index_evidence_history_with_ipfs_datasets.py}"
DUCKDB_SEARCH_SCRIPT="${HACC_DUCKDB_SEARCH_SCRIPT:-${SCRIPT_DIR}/search_history_duckdb.py}"
SEMANTIC_SEARCH_SCRIPT="${HACC_SEMANTIC_SEARCH_SCRIPT:-${SCRIPT_DIR}/search_history_index.py}"
INPUT_DIR_HISTORY="${HACC_HISTORY_INPUT_DIR:-${SCRIPT_DIR}/evidence/history}"
INPUT_DIR_EMAIL_IMPORTS="${HACC_EMAIL_IMPORTS_INPUT_DIR:-${SCRIPT_DIR}/evidence/email_imports}"

# ── Defaults ────────────────────────────────────────────────────────────────
FULL_SMOKE_TEST=false
OUTPUT_DIR=""
SKIP_PREFLIGHT=false
FORCE_CPU=false
PROFILE="max-throughput"
DUCKDB_QUERIES=()
SEMANTIC_QUERIES=()
EXTRA_ARGS=()
BUNDLE_OUTPUT_DIR=""
BUNDLE_FORMATS=()

# ── Argument parsing ─────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case "$1" in
        --full-smoke-test)
            FULL_SMOKE_TEST=true
            shift
            ;;
        --output-dir)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --output-dir=*)
            OUTPUT_DIR="${1#*=}"
            shift
            ;;
        --skip-preflight)
            SKIP_PREFLIGHT=true
            shift
            ;;
        --cpu-only)
            FORCE_CPU=true
            shift
            ;;
        --fast)
            PROFILE="fast"
            shift
            ;;
        --max-throughput)
            PROFILE="max-throughput"
            shift
            ;;
        --duckdb-query)
            DUCKDB_QUERIES+=("$2")
            shift 2
            ;;
        --duckdb-query=*)
            DUCKDB_QUERIES+=("${1#*=}")
            shift
            ;;
        --semantic-query)
            SEMANTIC_QUERIES+=("$2")
            shift 2
            ;;
        --semantic-query=*)
            SEMANTIC_QUERIES+=("${1#*=}")
            shift
            ;;
        --bundle-output-dir)
            BUNDLE_OUTPUT_DIR="$2"
            shift 2
            ;;
        --bundle-output-dir=*)
            BUNDLE_OUTPUT_DIR="${1#*=}"
            shift
            ;;
        --bundle-format)
            BUNDLE_FORMATS+=("$2")
            shift 2
            ;;
        --bundle-format=*)
            BUNDLE_FORMATS+=("${1#*=}")
            shift
            ;;
        *)
            EXTRA_ARGS+=("$1")
            shift
            ;;
    esac
done

# ── Auto-generate dated output dir if not specified ──────────────────────────
if [[ -z "$OUTPUT_DIR" ]]; then
    TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
    OUTPUT_DIR="${SCRIPT_DIR}/research_results/history_index_${TIMESTAMP}"
fi

if [[ -z "$BUNDLE_OUTPUT_DIR" && ${#BUNDLE_FORMATS[@]} -gt 0 ]]; then
    BUNDLE_OUTPUT_DIR="${SCRIPT_DIR}/research_results/history_index_bundles"
fi

# ── Verify python venv ───────────────────────────────────────────────────────
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

echo "=== HACC History Indexer ==="
echo "Output dir : $OUTPUT_DIR"
echo "Input dirs : $INPUT_DIR_HISTORY ; $INPUT_DIR_EMAIL_IMPORTS"
echo "Timestamp  : $(date -Iseconds)"
echo ""

if [[ ${#DUCKDB_QUERIES[@]} -eq 0 && -n "${HACC_DUCKDB_SPOT_QUERIES:-}" ]]; then
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            DUCKDB_QUERIES+=("$line")
        fi
    done <<< "${HACC_DUCKDB_SPOT_QUERIES}"
fi

if [[ ${#SEMANTIC_QUERIES[@]} -eq 0 && -n "${HACC_SEMANTIC_SPOT_QUERIES:-}" ]]; then
    while IFS= read -r line; do
        if [[ -n "$line" ]]; then
            SEMANTIC_QUERIES+=("$line")
        fi
    done <<< "${HACC_SEMANTIC_SPOT_QUERIES}"
fi

if [[ ${#DUCKDB_QUERIES[@]} -eq 0 ]]; then
    DUCKDB_QUERIES=("voice" "gmail")
fi

if [[ ${#SEMANTIC_QUERIES[@]} -eq 0 ]]; then
    SEMANTIC_QUERIES=("inspection notice" "google voice text")
fi

# ── Runtime tuning defaults (override via env or forwarded CLI args) ─────────
CPU_COUNT="$(nproc 2>/dev/null || echo 1)"
if [[ "$CPU_COUNT" -lt 1 ]]; then
    CPU_COUNT=1
fi

if [[ "$PROFILE" == "fast" ]]; then
    PROFILE_WORKERS="$(( CPU_COUNT > 4 ? 4 : CPU_COUNT ))"
    PROFILE_ROUTER_BATCH=24
    PROFILE_EMBED_BATCH=24
else
    PROFILE_WORKERS="$(( CPU_COUNT > 8 ? 8 : CPU_COUNT ))"
    PROFILE_ROUTER_BATCH=64
    PROFILE_EMBED_BATCH=64
fi

CPU_WORKERS_DEFAULT="${HACC_INDEX_WORKERS:-$PROFILE_WORKERS}"
if [[ "$CPU_WORKERS_DEFAULT" -lt 1 ]]; then
    CPU_WORKERS_DEFAULT=1
fi

EMBED_BATCH_DEFAULT="${HACC_EMBED_BATCH_SIZE:-$PROFILE_EMBED_BATCH}"
ROUTER_BATCH_DEFAULT="${HACC_ROUTER_BATCH_SIZE:-$PROFILE_ROUTER_BATCH}"
EMBED_NUM_WORKERS_DEFAULT="${HACC_EMBED_NUM_WORKERS:-0}"
VECTOR_PROVIDER_DEFAULT="${HACC_VECTOR_PROVIDER:-adapter}"
VECTOR_MODEL_DEFAULT="${HACC_VECTOR_MODEL:-}"

if [[ "$FORCE_CPU" == "true" ]]; then
    VECTOR_DEVICE_DEFAULT="cpu"
else
    if "$VENV_PYTHON" - <<'EOF_PY' >/dev/null 2>&1
import torch
raise SystemExit(0 if torch.cuda.is_available() else 1)
EOF_PY
    then
        VECTOR_DEVICE_DEFAULT="${HACC_VECTOR_DEVICE:-cuda}"
    else
        VECTOR_DEVICE_DEFAULT="${HACC_VECTOR_DEVICE:-cpu}"
    fi
fi

# ── Step 1: External vector backend health check ─────────────────────────────
if [[ "$SKIP_PREFLIGHT" == "false" ]]; then
    echo "--- Vector backend health check ---"
    HEALTH_ARGS=("--output-json" "${OUTPUT_DIR%/}_healthcheck.json")
    if [[ "$FULL_SMOKE_TEST" == "false" ]]; then
        HEALTH_ARGS+=("--skip-smoke-test")
        echo "(Skipping smoke test — use --full-smoke-test for thorough check)"
    else
        echo "(Full smoke test enabled)"
    fi

    mkdir -p "$(dirname "${OUTPUT_DIR%/}_healthcheck.json")"

    set +e
    "$VENV_PYTHON" "$HEALTH_SCRIPT" "${HEALTH_ARGS[@]}"
    HEALTH_EXIT=$?
    set -e

    if [[ $HEALTH_EXIT -eq 0 ]]; then
        echo "Health check: PASSED"
    elif [[ $HEALTH_EXIT -eq 1 ]]; then
        echo ""
        echo "ERROR: Vector backend is unhealthy. Aborting indexing run." >&2
        echo "Run the following for details:" >&2
        echo "  $VENV_PYTHON $HEALTH_SCRIPT" >&2
        exit 1
    else
        echo ""
        echo "ERROR: Health check script failed (exit $HEALTH_EXIT). Environment issue?" >&2
        exit 2
    fi
    echo ""
fi

# ── Step 2: Run the indexer ──────────────────────────────────────────────────
echo "--- Starting indexing run ---"
echo "Output: $OUTPUT_DIR"
echo "Profile: $PROFILE"
echo "Workers: $CPU_WORKERS_DEFAULT ($([[ "$FORCE_CPU" == "true" ]] && echo "forced-cpu" || echo "$VECTOR_DEVICE_DEFAULT"))"
echo "Batches: router=$ROUTER_BATCH_DEFAULT embed=$EMBED_BATCH_DEFAULT"
echo ""

INDEXER_ARGS=(
    "--input-dir" "$INPUT_DIR_HISTORY"
    "--input-dir" "$INPUT_DIR_EMAIL_IMPORTS"
    "--output-dir" "$OUTPUT_DIR"
    "--workers" "$CPU_WORKERS_DEFAULT"
    "--cpu-worker-backend" "process"
    "--vector-provider" "$VECTOR_PROVIDER_DEFAULT"
    "--vector-device" "$VECTOR_DEVICE_DEFAULT"
    "--batch-size" "$ROUTER_BATCH_DEFAULT"
    "--embedding-batch-size" "$EMBED_BATCH_DEFAULT"
    "--embedding-num-workers" "$EMBED_NUM_WORKERS_DEFAULT"
)

if [[ -n "$VECTOR_MODEL_DEFAULT" ]]; then
    INDEXER_ARGS+=("--vector-model" "$VECTOR_MODEL_DEFAULT")
fi

# If we already ran the external health check with smoke test, skip the
# built-in preflight smoke test to avoid running embeddings twice.
if [[ "$SKIP_PREFLIGHT" == "false" && "$FULL_SMOKE_TEST" == "true" ]]; then
    INDEXER_ARGS+=("--skip-vector-preflight-smoke-test")
fi

INDEXER_ARGS+=("${EXTRA_ARGS[@]+"${EXTRA_ARGS[@]}"}")

set +e
"$VENV_PYTHON" "$INDEX_SCRIPT" "${INDEXER_ARGS[@]}"
INDEXER_EXIT=$?
set -e

echo ""
if [[ $INDEXER_EXIT -eq 0 ]]; then
    echo "=== Indexing complete ==="
    echo "Results: $OUTPUT_DIR"
    if [[ -f "$OUTPUT_DIR/manifest.json" ]]; then
        echo ""
        echo "--- Manifest summary ---"
        "$VENV_PYTHON" - <<'EOF_PY' "$OUTPUT_DIR/manifest.json"
import json, sys
with open(sys.argv[1]) as f:
    m = json.load(f)
vi = m.get("vector_index", {})
print(f"  Documents : {m.get('documents_indexed', m.get('document_count', '?'))}")
print(f"  Chunks    : {m.get('chunk_records', vi.get('chunk_count', m.get('chunk_count','?')))}")
print(f"  Entities  : {m.get('entities', m.get('entity_count', '?'))}")
print(f"  Relations : {m.get('relationships', m.get('relationship_count', '?'))}")
print(f"  Dimension : {vi.get('dimension', '?')}")
print(f"  Provider  : {vi.get('provider', '?')}")
print(f"  Status    : {vi.get('status', '?')}")
EOF_PY
    fi
    if [[ -x "$VENV_PYTHON" && -f "$DUCKDB_SEARCH_SCRIPT" && -f "$OUTPUT_DIR/duckdb/evidence_index.duckdb" ]]; then
        echo ""
        echo "--- DuckDB spot checks ---"
        for query in "${DUCKDB_QUERIES[@]}"; do
            echo "DuckDB documents query: $query"
            set +e
            "$VENV_PYTHON" "$DUCKDB_SEARCH_SCRIPT" \
                --index-path "$OUTPUT_DIR/duckdb/evidence_index.duckdb" \
                --table documents \
                --top-k 3 \
                "$query"
            DUCKDB_SEARCH_EXIT=$?
            set -e
            if [[ $DUCKDB_SEARCH_EXIT -ne 0 ]]; then
                echo "  [warn] DuckDB spot check failed for query: $query"
            fi
            echo ""
        done
    fi
    if [[ -x "$VENV_PYTHON" && -f "$SEMANTIC_SEARCH_SCRIPT" ]]; then
        echo ""
        echo "--- Semantic spot checks ---"
        for query in "${SEMANTIC_QUERIES[@]}"; do
            echo "Semantic search: $query"
            set +e
            "$VENV_PYTHON" "$SEMANTIC_SEARCH_SCRIPT" \
                --index-dir "$OUTPUT_DIR" \
                --top-k 3 \
                "$query"
            SEMANTIC_SEARCH_EXIT=$?
            set -e
            if [[ $SEMANTIC_SEARCH_EXIT -ne 0 ]]; then
                echo "  [warn] Semantic spot check failed for query: $query"
            fi
            echo ""
        done
    fi
    if [[ -n "$BUNDLE_OUTPUT_DIR" ]]; then
        echo ""
        echo "--- Bundling history index artifacts ---"
        mkdir -p "$BUNDLE_OUTPUT_DIR"
        BUNDLE_OUTPUT_DIR="$(realpath -m "$BUNDLE_OUTPUT_DIR")"
        BUNDLE_RESULT_JSON="${OUTPUT_DIR}/history_index_bundle.json"
        "$VENV_PYTHON" - <<'EOF_PY' "$OUTPUT_DIR" "$BUNDLE_OUTPUT_DIR" "$SCRIPT_DIR" "$BUNDLE_RESULT_JSON" "${BUNDLE_FORMATS[@]}"
import json
import shutil
import sys
import zipfile
from pathlib import Path

output_dir = Path(sys.argv[1]).resolve()
bundle_output_dir = Path(sys.argv[2]).resolve()
script_dir = Path(sys.argv[3]).resolve()
bundle_result_json = Path(sys.argv[4]).resolve()
requested_formats = list(dict.fromkeys(sys.argv[5:]))

bundle_dir = bundle_output_dir / output_dir.name
bundle_dir.mkdir(parents=True, exist_ok=True)

manifest_src = output_dir / "manifest.json"
manifest_copy = bundle_dir / "manifest.json"
if manifest_src.exists():
    shutil.copy2(manifest_src, manifest_copy)

inventory_rows = []
for path in sorted(output_dir.rglob("*")):
    if not path.is_file():
        continue
    rel = path.relative_to(output_dir)
    target = bundle_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, target)
    inventory_rows.append(
        {
            "record_type": "index_file",
            "relative_path": str(rel),
            "artifact_path": str(target),
            "artifact_name": path.name,
            "size_bytes": path.stat().st_size,
            "suffix": path.suffix,
        }
    )

bundle_artifacts = {"dir": str(bundle_dir)}
bundle_formats = ["dir"] + [fmt for fmt in requested_formats if fmt != "dir"]

if "zip" in requested_formats:
    zip_path = bundle_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for child in sorted(bundle_dir.rglob("*")):
            if child.is_file():
                archive.write(child, child.relative_to(bundle_dir.parent))
    bundle_artifacts["zip"] = str(zip_path)

if "parquet" in requested_formats:
    import pyarrow as pa
    import pyarrow.parquet as pq
    parquet_path = bundle_dir / "history-index-bundle.parquet"
    table = pa.Table.from_pylist(inventory_rows)
    pq.write_table(table, parquet_path)
    bundle_artifacts["parquet"] = str(parquet_path)

if "car" in requested_formats:
    import importlib.util

    car_manager_path = (
        script_dir
        / "complaint-generator"
        / "ipfs_datasets_py"
        / "ipfs_kit_py"
        / "ipfs_kit_py"
        / "mcp"
        / "storage_manager"
        / "formats"
        / "car_manager.py"
    )
    spec = importlib.util.spec_from_file_location("history_index_car_manager", car_manager_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load CAR manager from {car_manager_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manager = module.CARManager()
    car_path = bundle_dir.with_suffix(".car")
    car_result = manager.create_car(str(bundle_dir), str(car_path))
    if not car_result.get("success"):
        raise RuntimeError(str(car_result.get("error") or "Failed to create CAR bundle"))
    bundle_artifacts["car"] = str(car_path)
    bundle_artifacts["car_result"] = car_result

payload = {
    "status": "success",
    "bundle_dir": str(bundle_dir),
    "bundle_formats": bundle_formats,
    "bundle_artifacts": bundle_artifacts,
    "file_count": len(inventory_rows),
    "manifest_copy": str(manifest_copy) if manifest_copy.exists() else "",
}
bundle_result_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
EOF_PY
        echo "History bundle result: $BUNDLE_RESULT_JSON"
    fi
    exit 0
elif [[ $INDEXER_EXIT -eq 3 ]]; then
    echo "ERROR: Indexer built-in preflight detected unhealthy vector backend (exit 3)." >&2
    if [[ -f "$OUTPUT_DIR/vector_preflight.json" ]]; then
        echo "Preflight report: $OUTPUT_DIR/vector_preflight.json" >&2
    fi
    exit 3
else
    echo "ERROR: Indexer failed (exit $INDEXER_EXIT)." >&2
    exit 4
fi
