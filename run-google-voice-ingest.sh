#!/usr/bin/env bash
# run-google-voice-ingest.sh — End-to-end Google Voice ingest workflow
#
# Usage:
#   ./run-google-voice-ingest.sh --source PATH [--source-mode MODE] [--materialized-dir DIR] [--case-slug SLUG]
#       [--import-arg ARG ...] [--index-arg ARG ...] [--bundle-output-dir DIR] [--bundle-format FMT ...]
#
# Examples:
#   ./run-google-voice-ingest.sh --source ~/Downloads/takeout-voice.zip
#   ./run-google-voice-ingest.sh --source ./Takeout/Voice --case-slug housing-voice
#   ./run-google-voice-ingest.sh --source ./voice-bundles/google_voice_manifest.json
#   ./run-google-voice-ingest.sh --source ./vault-voice-export.zip --source-mode vault
#   ./run-google-voice-ingest.sh --source gs://workspace-export/voice --source-mode data-export --import-arg --upload-to-workspace
#   ./run-google-voice-ingest.sh --source ~/Downloads/takeout-voice.zip --bundle-output-dir ./voice-bundles --bundle-format zip --bundle-format car

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
IMPORT_SCRIPT="${HACC_IMPORT_SCRIPT:-${SCRIPT_DIR}/import_gmail_evidence.py}"
INDEX_SCRIPT="${HACC_INDEX_SCRIPT:-${SCRIPT_DIR}/run-history-index.sh}"
IPFS_DATASETS_CLI="${HACC_IPFS_DATASETS_CLI:-${SCRIPT_DIR}/complaint-generator/ipfs_datasets_py/ipfs_datasets_cli.py}"

SOURCE=""
SOURCE_MODE="takeout"
MATERIALIZED_DIR=""
CASE_SLUG=""
RUN_INDEX=true
IMPORT_ARGS=()
INDEX_ARGS=()
BUNDLE_OUTPUT_DIR=""
BUNDLE_FORMATS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --source)
            SOURCE="$2"
            shift 2
            ;;
        --source=*)
            SOURCE="${1#*=}"
            shift
            ;;
        --source-mode)
            SOURCE_MODE="$2"
            shift 2
            ;;
        --source-mode=*)
            SOURCE_MODE="${1#*=}"
            shift
            ;;
        --materialized-dir)
            MATERIALIZED_DIR="$2"
            shift 2
            ;;
        --materialized-dir=*)
            MATERIALIZED_DIR="${1#*=}"
            shift
            ;;
        --case-slug)
            CASE_SLUG="$2"
            shift 2
            ;;
        --case-slug=*)
            CASE_SLUG="${1#*=}"
            shift
            ;;
        --skip-index)
            RUN_INDEX=false
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
        --import-arg)
            IMPORT_ARGS+=("$2")
            shift 2
            ;;
        --import-arg=*)
            IMPORT_ARGS+=("${1#*=}")
            shift
            ;;
        --index-arg)
            INDEX_ARGS+=("$2")
            shift 2
            ;;
        --index-arg=*)
            INDEX_ARGS+=("${1#*=}")
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$SOURCE" ]]; then
    echo "ERROR: --source is required" >&2
    exit 2
fi

case "$SOURCE_MODE" in
    takeout|vault|data-export)
        ;;
    *)
        echo "ERROR: unsupported --source-mode '$SOURCE_MODE' (use takeout, vault, or data-export)" >&2
        exit 2
        ;;
esac

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

if [[ "$SOURCE" == gs://* ]]; then
    SOURCE_PATH="$SOURCE"
else
    SOURCE_PATH="$(realpath -m "$SOURCE")"
    if [[ ! -e "$SOURCE_PATH" ]]; then
        echo "ERROR: source not found: $SOURCE_PATH" >&2
        exit 2
    fi
fi

if [[ -z "$CASE_SLUG" ]]; then
    CASE_SLUG="google-voice-$(date +%Y%m%d_%H%M%S)"
fi

if [[ -z "$MATERIALIZED_DIR" ]]; then
    MATERIALIZED_DIR="${SCRIPT_DIR}/evidence/email_imports/${CASE_SLUG}-materialized"
fi

if [[ -z "$BUNDLE_OUTPUT_DIR" && ${#BUNDLE_FORMATS[@]} -gt 0 ]]; then
    BUNDLE_OUTPUT_DIR="${SCRIPT_DIR}/evidence/email_imports/google-voice-case-bundles"
fi

MANIFEST_PATH="$SOURCE_PATH"
if [[ "$SOURCE_PATH" != "google_voice_manifest.json" && "$(basename "$SOURCE_PATH")" != "google_voice_manifest.json" ]]; then
    echo "=== Materializing Google Voice export ==="
    VOICE_SUBCOMMAND="google-voice"
    if [[ "$SOURCE_MODE" == "vault" ]]; then
        VOICE_SUBCOMMAND="google-voice-vault"
    elif [[ "$SOURCE_MODE" == "data-export" ]]; then
        VOICE_SUBCOMMAND="google-voice-data-export"
    fi
    MATERIALIZE_CMD=(
        "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email "$VOICE_SUBCOMMAND" "$SOURCE_PATH"
        --materialize
        --output-dir "$MATERIALIZED_DIR"
        --json
    )
    if [[ "$SOURCE_MODE" == "data-export" ]]; then
        MATERIALIZE_CMD+=(--staging-dir "${MATERIALIZED_DIR}/_stage")
    fi
    "${MATERIALIZE_CMD[@]}"
    MANIFEST_PATH="${MATERIALIZED_DIR}/google_voice_manifest.json"
fi

if [[ ! -f "$MANIFEST_PATH" ]]; then
    echo "ERROR: Google Voice manifest not found: $MANIFEST_PATH" >&2
    exit 2
fi

echo ""
echo "=== Importing materialized Google Voice bundles ==="
IMPORT_CMD=(
    "$VENV_PYTHON" "$IMPORT_SCRIPT"
    --google-voice-source "$MANIFEST_PATH"
    --case-slug "$CASE_SLUG"
)
IMPORT_CMD+=("${IMPORT_ARGS[@]}")
"${IMPORT_CMD[@]}"

if [[ -n "$BUNDLE_OUTPUT_DIR" ]]; then
    echo ""
    echo "=== Bundling Google Voice materialized artifacts ==="
    mkdir -p "$BUNDLE_OUTPUT_DIR"
    BUNDLE_OUTPUT_DIR="$(realpath -m "$BUNDLE_OUTPUT_DIR")"
    BUNDLE_MANIFEST_PATH="${MATERIALIZED_DIR}/takeout_acquisition_manifest.json"
    BUNDLE_RESULT_JSON="${MATERIALIZED_DIR}/google_voice_case_bundle.json"
    "$VENV_PYTHON" - <<'PY' "$BUNDLE_MANIFEST_PATH" "$CASE_SLUG" "$SOURCE_MODE" "$SOURCE_PATH" "$MANIFEST_PATH" "$MATERIALIZED_DIR"
import json, sys
from datetime import datetime, UTC
bundle_manifest_path, case_slug, source_mode, source_path, materialized_manifest, materialized_dir = sys.argv[1:]
timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
payload = {
    "status": "hydrated",
    "updated_at": timestamp,
    "case_slug": case_slug,
    "delivery_destination": source_mode,
    "frequency": "one_time",
    "page_source_path": None,
    "downloads_dir": materialized_dir,
    "capture_json_path": None,
    "drive_fallback": {"enabled": False},
    "product_ids": ["voice"],
    "materialized_manifest_path": materialized_manifest,
    "final_archive_path": source_path,
    "events": [
        {
            "type": "hydrated",
            "timestamp": timestamp,
            "final_archive_path": source_path,
            "materialized_manifest_path": materialized_manifest,
        }
    ],
}
with open(bundle_manifest_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
PY
    BUNDLE_CMD=(
        "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-case-bundle
        "$BUNDLE_MANIFEST_PATH"
        --output-dir "$BUNDLE_OUTPUT_DIR"
    )
    for fmt in "${BUNDLE_FORMATS[@]}"; do
        BUNDLE_CMD+=(--bundle-format "$fmt")
    done
    "${BUNDLE_CMD[@]}" > "$BUNDLE_RESULT_JSON"
    echo "Bundle result JSON: $BUNDLE_RESULT_JSON"
fi

if [[ "$RUN_INDEX" == true ]]; then
    echo ""
    echo "=== Rebuilding history index ==="
    INDEX_CMD=("$INDEX_SCRIPT")
    INDEX_CMD+=("${INDEX_ARGS[@]}")
    "${INDEX_CMD[@]}"
fi
