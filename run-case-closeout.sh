#!/usr/bin/env bash
# run-case-closeout.sh — One-shot communications ingest, history bundling, and final case archive
#
# Examples:
#   ./run-case-closeout.sh \
#     --case-slug housing-case \
#     --google-voice-source ~/Downloads/takeout-voice.zip \
#     --voice-bundle-format zip \
#     --history-bundle-format zip \
#     --archive-bundle-format zip
#   ./run-case-closeout.sh \
#     --case-slug housing-case \
#     --gmail-folder "[Gmail]/All Mail" \
#     --google-voice-source ./Takeout/Voice \
#     --archive-output-dir ./case-archives

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
COMMUNICATIONS_WRAPPER="${HACC_COMMUNICATIONS_WRAPPER:-${SCRIPT_DIR}/run-communications-ingest.sh}"
HISTORY_WRAPPER="${HACC_HISTORY_WRAPPER:-${SCRIPT_DIR}/run-history-index.sh}"
CASE_ARCHIVE_WRAPPER="${HACC_CASE_ARCHIVE_WRAPPER:-${SCRIPT_DIR}/run-case-archive.sh}"

CASE_SLUG=""
ARCHIVE_OUTPUT_DIR=""
VOICE_BUNDLE_OUTPUT_DIR=""
HISTORY_BUNDLE_OUTPUT_DIR=""
RESULT_JSON=""
ARCHIVE_BUNDLE_FORMATS=()
VOICE_BUNDLE_FORMATS=()
HISTORY_BUNDLE_FORMATS=()
COMMUNICATIONS_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --case-slug)
            CASE_SLUG="$2"
            COMMUNICATIONS_ARGS+=("$1" "$2")
            shift 2
            ;;
        --case-slug=*)
            CASE_SLUG="${1#*=}"
            COMMUNICATIONS_ARGS+=("$1")
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
        --history-bundle-output-dir)
            HISTORY_BUNDLE_OUTPUT_DIR="$2"
            shift 2
            ;;
        --history-bundle-output-dir=*)
            HISTORY_BUNDLE_OUTPUT_DIR="${1#*=}"
            shift
            ;;
        --history-bundle-format)
            HISTORY_BUNDLE_FORMATS+=("$2")
            shift 2
            ;;
        --history-bundle-format=*)
            HISTORY_BUNDLE_FORMATS+=("${1#*=}")
            shift
            ;;
        --archive-output-dir)
            ARCHIVE_OUTPUT_DIR="$2"
            shift 2
            ;;
        --archive-output-dir=*)
            ARCHIVE_OUTPUT_DIR="${1#*=}"
            shift
            ;;
        --result-json)
            RESULT_JSON="$2"
            shift 2
            ;;
        --result-json=*)
            RESULT_JSON="${1#*=}"
            shift
            ;;
        --archive-bundle-format)
            ARCHIVE_BUNDLE_FORMATS+=("$2")
            shift 2
            ;;
        --archive-bundle-format=*)
            ARCHIVE_BUNDLE_FORMATS+=("${1#*=}")
            shift
            ;;
        *)
            COMMUNICATIONS_ARGS+=("$1")
            shift
            ;;
    esac
done

if [[ -z "$CASE_SLUG" ]]; then
    CASE_SLUG="case-closeout-$(date +%Y%m%d_%H%M%S)"
    COMMUNICATIONS_ARGS=(--case-slug "$CASE_SLUG" "${COMMUNICATIONS_ARGS[@]}")
fi

if [[ -z "$VOICE_BUNDLE_OUTPUT_DIR" ]]; then
    VOICE_BUNDLE_OUTPUT_DIR="${SCRIPT_DIR}/evidence/email_imports/google-voice-case-bundles"
fi

if [[ -z "$HISTORY_BUNDLE_OUTPUT_DIR" ]]; then
    HISTORY_BUNDLE_OUTPUT_DIR="${SCRIPT_DIR}/research_results/history_index_bundles"
fi

if [[ -z "$ARCHIVE_OUTPUT_DIR" ]]; then
    ARCHIVE_OUTPUT_DIR="${SCRIPT_DIR}/research_results/case_archives"
fi

mkdir -p "$VOICE_BUNDLE_OUTPUT_DIR" "$HISTORY_BUNDLE_OUTPUT_DIR" "$ARCHIVE_OUTPUT_DIR"

if [[ -z "$RESULT_JSON" ]]; then
    RESULT_JSON="${ARCHIVE_OUTPUT_DIR%/}/${CASE_SLUG}.closeout.json"
fi

COMM_LOG="${ARCHIVE_OUTPUT_DIR%/}/${CASE_SLUG}.communications.log"
HISTORY_LOG="${ARCHIVE_OUTPUT_DIR%/}/${CASE_SLUG}.history.log"
ARCHIVE_LOG="${ARCHIVE_OUTPUT_DIR%/}/${CASE_SLUG}.archive.log"

echo "=== Case closeout: communications ingest ==="
COMM_CMD=("$COMMUNICATIONS_WRAPPER")
COMM_CMD+=("${COMMUNICATIONS_ARGS[@]}")
if [[ -n "$VOICE_BUNDLE_OUTPUT_DIR" ]]; then
    COMM_CMD+=(--voice-bundle-output-dir "$VOICE_BUNDLE_OUTPUT_DIR")
fi
for fmt in "${VOICE_BUNDLE_FORMATS[@]}"; do
    COMM_CMD+=(--voice-bundle-format "$fmt")
done
set +e
"${COMM_CMD[@]}" | tee "$COMM_LOG"
COMM_EXIT=${PIPESTATUS[0]}
set -e
if [[ $COMM_EXIT -ne 0 ]]; then
    echo "ERROR: communications ingest failed (exit $COMM_EXIT)" >&2
    exit $COMM_EXIT
fi

echo ""
echo "=== Case closeout: history index bundle ==="
HISTORY_CMD=("$HISTORY_WRAPPER")
if [[ -n "$HISTORY_BUNDLE_OUTPUT_DIR" ]]; then
    HISTORY_CMD+=(--bundle-output-dir "$HISTORY_BUNDLE_OUTPUT_DIR")
fi
for fmt in "${HISTORY_BUNDLE_FORMATS[@]}"; do
    HISTORY_CMD+=(--bundle-format "$fmt")
done
set +e
"${HISTORY_CMD[@]}" | tee "$HISTORY_LOG"
HISTORY_EXIT=${PIPESTATUS[0]}
set -e
if [[ $HISTORY_EXIT -ne 0 ]]; then
    echo "ERROR: history indexing failed (exit $HISTORY_EXIT)" >&2
    exit $HISTORY_EXIT
fi

echo ""
echo "=== Case closeout: final archive ==="
ARCHIVE_CMD=(
    "$CASE_ARCHIVE_WRAPPER"
    --case-slug "$CASE_SLUG"
    --discover
    --output-dir "$ARCHIVE_OUTPUT_DIR"
)
for fmt in "${ARCHIVE_BUNDLE_FORMATS[@]}"; do
    ARCHIVE_CMD+=(--bundle-format "$fmt")
done
set +e
"${ARCHIVE_CMD[@]}" | tee "$ARCHIVE_LOG"
ARCHIVE_EXIT=${PIPESTATUS[0]}
set -e
if [[ $ARCHIVE_EXIT -ne 0 ]]; then
    echo "ERROR: case archive failed (exit $ARCHIVE_EXIT)" >&2
    exit $ARCHIVE_EXIT
fi

"$VENV_PYTHON" - <<'EOF_PY' "$RESULT_JSON" "$CASE_SLUG" "$VOICE_BUNDLE_OUTPUT_DIR" "$HISTORY_BUNDLE_OUTPUT_DIR" "$ARCHIVE_OUTPUT_DIR" "$COMM_LOG" "$HISTORY_LOG" "$ARCHIVE_LOG"
import json
import sys
from pathlib import Path

result_json = Path(sys.argv[1]).resolve()
case_slug = sys.argv[2]
voice_bundle_output_dir = Path(sys.argv[3]).resolve()
history_bundle_output_dir = Path(sys.argv[4]).resolve()
archive_output_dir = Path(sys.argv[5]).resolve()
comm_log = Path(sys.argv[6]).resolve()
history_log = Path(sys.argv[7]).resolve()
archive_log = Path(sys.argv[8]).resolve()

archive_result_path = archive_output_dir / f"{case_slug}.json"
archive_result = {}
if archive_result_path.exists():
    archive_result = json.loads(archive_result_path.read_text(encoding="utf-8"))

payload = {
    "status": "success",
    "case_slug": case_slug,
    "voice_bundle_output_dir": str(voice_bundle_output_dir),
    "history_bundle_output_dir": str(history_bundle_output_dir),
    "archive_output_dir": str(archive_output_dir),
    "archive_result_path": str(archive_result_path) if archive_result_path.exists() else "",
    "archive_dir": archive_result.get("archive_dir") or "",
    "archive_bundle_artifacts": archive_result.get("bundle_artifacts") or {},
    "logs": {
        "communications": str(comm_log),
        "history": str(history_log),
        "archive": str(archive_log),
    },
}
result_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
print("")
print("=== Case closeout complete ===")
print(f"Closeout result: {result_json}")
if payload["archive_result_path"]:
    print(f"Archive result: {payload['archive_result_path']}")
if payload["archive_dir"]:
    print(f"Archive dir: {payload['archive_dir']}")
EOF_PY
