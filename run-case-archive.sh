#!/usr/bin/env bash
# run-case-archive.sh — Collect Takeout, Voice, and history bundle artifacts into one case archive
#
# Examples:
#   ./run-case-archive.sh --case-slug housing-case \
#     --takeout-manifest ./downloads/takeout_acquisition_manifest.json \
#     --voice-bundle-result ./materialized/google_voice_case_bundle.json \
#     --history-bundle-result ./research_results/history_index_20260404_120000/history_index_bundle.json
#   ./run-case-archive.sh --case-slug housing-case \
#     --takeout-manifest ./downloads/takeout_acquisition_manifest.json \
#     --output-dir ./case-archives \
#     --bundle-format zip --bundle-format car
#   ./run-case-archive.sh --case-slug housing-case --discover

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"

CASE_SLUG=""
TAKEOUT_MANIFEST=""
VOICE_BUNDLE_RESULT=""
HISTORY_BUNDLE_RESULT=""
OUTPUT_DIR=""
BUNDLE_FORMATS=()
DISCOVER=false
DISCOVER_ROOT="${HACC_CASE_ARCHIVE_DISCOVER_ROOT:-$SCRIPT_DIR}"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --case-slug)
            CASE_SLUG="$2"
            shift 2
            ;;
        --case-slug=*)
            CASE_SLUG="${1#*=}"
            shift
            ;;
        --takeout-manifest)
            TAKEOUT_MANIFEST="$2"
            shift 2
            ;;
        --takeout-manifest=*)
            TAKEOUT_MANIFEST="${1#*=}"
            shift
            ;;
        --voice-bundle-result)
            VOICE_BUNDLE_RESULT="$2"
            shift 2
            ;;
        --voice-bundle-result=*)
            VOICE_BUNDLE_RESULT="${1#*=}"
            shift
            ;;
        --history-bundle-result)
            HISTORY_BUNDLE_RESULT="$2"
            shift 2
            ;;
        --history-bundle-result=*)
            HISTORY_BUNDLE_RESULT="${1#*=}"
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
        --bundle-format)
            BUNDLE_FORMATS+=("$2")
            shift 2
            ;;
        --bundle-format=*)
            BUNDLE_FORMATS+=("${1#*=}")
            shift
            ;;
        --discover)
            DISCOVER=true
            shift
            ;;
        --discover-root)
            DISCOVER_ROOT="$2"
            shift 2
            ;;
        --discover-root=*)
            DISCOVER_ROOT="${1#*=}"
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$CASE_SLUG" ]]; then
    CASE_SLUG="case-archive-$(date +%Y%m%d_%H%M%S)"
fi

if [[ -z "$OUTPUT_DIR" ]]; then
    OUTPUT_DIR="${SCRIPT_DIR}/research_results/case_archives"
fi

mkdir -p "$OUTPUT_DIR"
OUTPUT_DIR="$(realpath -m "$OUTPUT_DIR")"

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

if [[ "$DISCOVER" == true ]]; then
    if [[ -z "$CASE_SLUG" || "$CASE_SLUG" == case-archive-* ]]; then
        echo "ERROR: --discover requires an explicit --case-slug" >&2
        exit 2
    fi
    DISCOVERY_OUTPUT="$("$VENV_PYTHON" - <<'EOF_PY' "$DISCOVER_ROOT" "$CASE_SLUG"
from pathlib import Path
import json
import sys

root = Path(sys.argv[1]).expanduser().resolve()
case_slug = sys.argv[2]

def newest_matching(paths):
    candidates = [path for path in paths if case_slug in str(path)]
    if not candidates:
        return ""
    candidates.sort(key=lambda path: path.stat().st_mtime, reverse=True)
    return str(candidates[0])

takeout = newest_matching(root.glob("**/takeout_acquisition_manifest.json"))
voice = newest_matching(root.glob("**/google_voice_case_bundle.json"))
history = newest_matching(root.glob("**/history_index_bundle.json"))

print(json.dumps({
    "takeout_manifest": takeout,
    "voice_bundle_result": voice,
    "history_bundle_result": history,
}, ensure_ascii=False))
EOF_PY
)"
    TAKEOUT_MANIFEST="${TAKEOUT_MANIFEST:-$("$VENV_PYTHON" - <<'EOF_PY' "$DISCOVERY_OUTPUT"
import json, sys
print(json.loads(sys.argv[1]).get("takeout_manifest") or "")
EOF_PY
)}"
    VOICE_BUNDLE_RESULT="${VOICE_BUNDLE_RESULT:-$("$VENV_PYTHON" - <<'EOF_PY' "$DISCOVERY_OUTPUT"
import json, sys
print(json.loads(sys.argv[1]).get("voice_bundle_result") or "")
EOF_PY
)}"
    HISTORY_BUNDLE_RESULT="${HISTORY_BUNDLE_RESULT:-$("$VENV_PYTHON" - <<'EOF_PY' "$DISCOVERY_OUTPUT"
import json, sys
print(json.loads(sys.argv[1]).get("history_bundle_result") or "")
EOF_PY
)}"
fi

if [[ -z "$TAKEOUT_MANIFEST" && -z "$VOICE_BUNDLE_RESULT" && -z "$HISTORY_BUNDLE_RESULT" ]]; then
    echo "ERROR: provide at least one of --takeout-manifest, --voice-bundle-result, or --history-bundle-result, or use --discover" >&2
    exit 2
fi

ARCHIVE_RESULT_JSON="${OUTPUT_DIR}/${CASE_SLUG}.json"

"$VENV_PYTHON" - <<'EOF_PY' "$CASE_SLUG" "$OUTPUT_DIR" "$ARCHIVE_RESULT_JSON" "$SCRIPT_DIR" "${TAKEOUT_MANIFEST:-}" "${VOICE_BUNDLE_RESULT:-}" "${HISTORY_BUNDLE_RESULT:-}" "${BUNDLE_FORMATS[@]}"
import json
import shutil
import sys
import zipfile
from pathlib import Path

case_slug = sys.argv[1]
output_dir = Path(sys.argv[2]).resolve()
result_json = Path(sys.argv[3]).resolve()
script_dir = Path(sys.argv[4]).resolve()
takeout_manifest_arg = sys.argv[5].strip()
voice_bundle_result_arg = sys.argv[6].strip()
history_bundle_result_arg = sys.argv[7].strip()
requested_formats = list(dict.fromkeys(arg for arg in sys.argv[8:] if arg))

archive_dir = output_dir / case_slug
archive_dir.mkdir(parents=True, exist_ok=True)

components = []
inventory_rows = []

def copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    inventory_rows.append(
        {
            "record_type": "archive_file",
            "component": str(dst.parts[len(archive_dir.parts)]) if len(dst.parts) > len(archive_dir.parts) else "",
            "relative_path": str(dst.relative_to(archive_dir)),
            "artifact_path": str(dst),
            "artifact_name": dst.name,
            "size_bytes": dst.stat().st_size,
            "suffix": dst.suffix,
        }
    )

def copy_tree(src: Path, dst: Path) -> None:
    for child in sorted(src.rglob("*")):
        if child.is_file():
            copy_file(child, dst / child.relative_to(src))

def load_json(path_str: str) -> tuple[Path, dict] | tuple[None, dict]:
    if not path_str:
        return None, {}
    path = Path(path_str).expanduser().resolve()
    payload = json.loads(path.read_text(encoding="utf-8"))
    return path, payload

takeout_manifest_path, takeout_payload = load_json(takeout_manifest_arg)
if takeout_manifest_path is not None:
    component_dir = archive_dir / "takeout"
    component_dir.mkdir(parents=True, exist_ok=True)
    copy_file(takeout_manifest_path, component_dir / takeout_manifest_path.name)
    downloads_dir = Path(str(takeout_payload.get("downloads_dir") or "")).expanduser()
    if downloads_dir.exists():
        history_dir = downloads_dir / "takeout_acquisition_history"
        if history_dir.exists():
            copy_tree(history_dir, component_dir / "takeout_acquisition_history")
    bundle_result = dict(takeout_payload.get("bundle_result") or {})
    if bundle_result:
        bundle_result_path = component_dir / "takeout_case_bundle.json"
        bundle_result_path.write_text(json.dumps(bundle_result, indent=2, ensure_ascii=False), encoding="utf-8")
        inventory_rows.append(
            {
                "record_type": "archive_file",
                "component": "takeout",
                "relative_path": str(bundle_result_path.relative_to(archive_dir)),
                "artifact_path": str(bundle_result_path),
                "artifact_name": bundle_result_path.name,
                "size_bytes": bundle_result_path.stat().st_size,
                "suffix": bundle_result_path.suffix,
            }
        )
        for key, value in (bundle_result.get("bundle_artifacts") or {}).items():
            if key == "car_result":
                continue
            if not value:
                continue
            src = Path(str(value)).expanduser()
            if src.is_file():
                copy_file(src, component_dir / "bundle_artifacts" / src.name)
            elif src.is_dir():
                copy_tree(src, component_dir / "bundle_artifacts" / src.name)
    components.append({"component": "takeout", "source": str(takeout_manifest_path)})

voice_bundle_path, voice_bundle_payload = load_json(voice_bundle_result_arg)
if voice_bundle_path is not None:
    component_dir = archive_dir / "voice"
    component_dir.mkdir(parents=True, exist_ok=True)
    copy_file(voice_bundle_path, component_dir / voice_bundle_path.name)
    for key, value in (voice_bundle_payload.get("bundle_artifacts") or {}).items():
        if key == "car_result":
            continue
        if not value:
            continue
        src = Path(str(value)).expanduser()
        if src.is_file():
            copy_file(src, component_dir / "bundle_artifacts" / src.name)
        elif src.is_dir():
            copy_tree(src, component_dir / "bundle_artifacts" / src.name)
    components.append({"component": "voice", "source": str(voice_bundle_path)})

history_bundle_path, history_bundle_payload = load_json(history_bundle_result_arg)
if history_bundle_path is not None:
    component_dir = archive_dir / "history_index"
    component_dir.mkdir(parents=True, exist_ok=True)
    copy_file(history_bundle_path, component_dir / history_bundle_path.name)
    for key, value in (history_bundle_payload.get("bundle_artifacts") or {}).items():
        if key == "car_result":
            continue
        if not value:
            continue
        src = Path(str(value)).expanduser()
        if src.is_file():
            copy_file(src, component_dir / "bundle_artifacts" / src.name)
        elif src.is_dir():
            copy_tree(src, component_dir / "bundle_artifacts" / src.name)
    components.append({"component": "history_index", "source": str(history_bundle_path)})

summary_path = archive_dir / "case_archive_summary.json"
summary_payload = {
    "status": "success",
    "case_slug": case_slug,
    "component_count": len(components),
    "components": components,
}
summary_path.write_text(json.dumps(summary_payload, indent=2, ensure_ascii=False), encoding="utf-8")
inventory_rows.append(
    {
        "record_type": "archive_file",
        "component": "summary",
        "relative_path": str(summary_path.relative_to(archive_dir)),
        "artifact_path": str(summary_path),
        "artifact_name": summary_path.name,
        "size_bytes": summary_path.stat().st_size,
        "suffix": summary_path.suffix,
    }
)

bundle_artifacts = {"dir": str(archive_dir)}
bundle_formats = ["dir"] + [fmt for fmt in requested_formats if fmt != "dir"]

if "zip" in requested_formats:
    zip_path = archive_dir.with_suffix(".zip")
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for child in sorted(archive_dir.rglob("*")):
            if child.is_file():
                archive.write(child, child.relative_to(archive_dir.parent))
    bundle_artifacts["zip"] = str(zip_path)

if "parquet" in requested_formats:
    import pyarrow as pa
    import pyarrow.parquet as pq
    parquet_path = archive_dir / "case-archive-inventory.parquet"
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
    spec = importlib.util.spec_from_file_location("case_archive_car_manager", car_manager_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load CAR manager from {car_manager_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    manager = module.CARManager()
    car_path = archive_dir.with_suffix(".car")
    car_result = manager.create_car(str(archive_dir), str(car_path))
    if not car_result.get("success"):
        raise RuntimeError(str(car_result.get("error") or "Failed to create CAR archive"))
    bundle_artifacts["car"] = str(car_path)
    bundle_artifacts["car_result"] = car_result

payload = {
    "status": "success",
    "case_slug": case_slug,
    "archive_dir": str(archive_dir),
    "bundle_formats": bundle_formats,
    "bundle_artifacts": bundle_artifacts,
    "component_count": len(components),
    "components": components,
    "inventory_count": len(inventory_rows),
    "summary_path": str(summary_path),
}
result_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(payload, indent=2, ensure_ascii=False))
EOF_PY

echo "Case archive result: $ARCHIVE_RESULT_JSON"
