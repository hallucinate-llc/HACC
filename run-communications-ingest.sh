#!/usr/bin/env bash
# run-communications-ingest.sh — Combined Gmail + Google Voice ingest workflow
#
# Examples:
#   ./run-communications-ingest.sh --gmail-folder "[Gmail]/All Mail" --google-voice-source ~/Downloads/takeout-voice.zip
#   ./run-communications-ingest.sh --gmail-arg --address --gmail-arg tenant@example.com --google-voice-source ./voice-bundles/google_voice_manifest.json
#   ./run-communications-ingest.sh --google-voice-source ./vault-voice-export.zip --google-voice-mode vault
#   ./run-communications-ingest.sh --google-voice-source ~/Downloads/takeout-voice.zip --voice-bundle-output-dir ./voice-bundles --voice-bundle-format zip

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
IMPORT_SCRIPT="${HACC_IMPORT_SCRIPT:-${SCRIPT_DIR}/import_gmail_evidence.py}"
VOICE_WRAPPER="${HACC_VOICE_WRAPPER:-${SCRIPT_DIR}/run-google-voice-ingest.sh}"
INDEX_SCRIPT="${HACC_INDEX_SCRIPT:-${SCRIPT_DIR}/run-history-index.sh}"

CASE_SLUG=""
RUN_INDEX=true
RUN_GMAIL=false
RUN_VOICE=false
GOOGLE_VOICE_SOURCE=""
GOOGLE_VOICE_MODE=""
GMAIL_ARGS=()
VOICE_INDEX_ARGS=()
INDEX_ARGS=()
VOICE_BUNDLE_OUTPUT_DIR=""
VOICE_BUNDLE_FORMATS=()

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
        --gmail-folder)
            RUN_GMAIL=true
            GMAIL_ARGS+=("--folder" "$2")
            shift 2
            ;;
        --gmail-folder=*)
            RUN_GMAIL=true
            GMAIL_ARGS+=("--folder" "${1#*=}")
            shift
            ;;
        --gmail-arg)
            RUN_GMAIL=true
            GMAIL_ARGS+=("$2")
            shift 2
            ;;
        --gmail-arg=*)
            RUN_GMAIL=true
            GMAIL_ARGS+=("${1#*=}")
            shift
            ;;
        --google-voice-source)
            RUN_VOICE=true
            GOOGLE_VOICE_SOURCE="$2"
            shift 2
            ;;
        --google-voice-source=*)
            RUN_VOICE=true
            GOOGLE_VOICE_SOURCE="${1#*=}"
            shift
            ;;
        --google-voice-mode)
            GOOGLE_VOICE_MODE="$2"
            shift 2
            ;;
        --google-voice-mode=*)
            GOOGLE_VOICE_MODE="${1#*=}"
            shift
            ;;
        --voice-index-arg)
            VOICE_INDEX_ARGS+=("$2")
            shift 2
            ;;
        --voice-index-arg=*)
            VOICE_INDEX_ARGS+=("${1#*=}")
            shift
            ;;
        --voice-bundle-output-dir)
            VOICE_BUNDLE_OUTPUT_DIR="$2"
            shift 2
            ;;
        --voice-bundle-output-dir=*)
            VOICE_BUNDLE_OUTPUT_DIR="${1#*=}"
            shift
            ;;
        --voice-bundle-format)
            VOICE_BUNDLE_FORMATS+=("$2")
            shift 2
            ;;
        --voice-bundle-format=*)
            VOICE_BUNDLE_FORMATS+=("${1#*=}")
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
        --skip-index)
            RUN_INDEX=false
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

if [[ "$RUN_GMAIL" == false && "$RUN_VOICE" == false ]]; then
    echo "ERROR: specify Gmail args and/or --google-voice-source" >&2
    exit 2
fi

if [[ -z "$CASE_SLUG" ]]; then
    CASE_SLUG="communications-$(date +%Y%m%d_%H%M%S)"
fi

if [[ "$RUN_GMAIL" == true ]]; then
    echo "=== Gmail import ==="
    GMAIL_CMD=(
        "$VENV_PYTHON" "$IMPORT_SCRIPT"
        --case-slug "$CASE_SLUG"
    )
    GMAIL_CMD+=("${GMAIL_ARGS[@]}")
    "${GMAIL_CMD[@]}"
fi

if [[ "$RUN_VOICE" == true ]]; then
    echo ""
    echo "=== Google Voice ingest ==="
    VOICE_CMD=(
        "$VOICE_WRAPPER"
        --source "$GOOGLE_VOICE_SOURCE"
        --case-slug "$CASE_SLUG"
        --skip-index
    )
    if [[ -n "$GOOGLE_VOICE_MODE" ]]; then
        VOICE_CMD+=(--source-mode "$GOOGLE_VOICE_MODE")
    fi
    if [[ -n "$VOICE_BUNDLE_OUTPUT_DIR" ]]; then
        VOICE_CMD+=(--bundle-output-dir "$VOICE_BUNDLE_OUTPUT_DIR")
    fi
    for fmt in "${VOICE_BUNDLE_FORMATS[@]}"; do
        VOICE_CMD+=(--bundle-format "$fmt")
    done
    for arg in "${VOICE_INDEX_ARGS[@]}"; do
        VOICE_CMD+=(--import-arg "$arg")
    done
    "${VOICE_CMD[@]}"
fi

if [[ "$RUN_INDEX" == true ]]; then
    echo ""
    echo "=== Rebuilding history index ==="
    INDEX_CMD=("$INDEX_SCRIPT")
    INDEX_CMD+=("${INDEX_ARGS[@]}")
    "${INDEX_CMD[@]}"
fi
