#!/usr/bin/env bash
# run-and-watch-consumer-google-voice-takeout.sh — Bootstrap a new consumer Takeout run, then watch it to completion
#
# Examples:
#   ./run-and-watch-consumer-google-voice-takeout.sh --product-id voice
#   ./run-and-watch-consumer-google-voice-takeout.sh --page-source ./takeout_page.html --watch-interval-seconds 60
#   ./run-and-watch-consumer-google-voice-takeout.sh --product-id voice --bundle-output-dir ./takeout-bundles --bundle-format zip

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONSUMER_WRAPPER="${HACC_CONSUMER_TAKEOUT_WRAPPER:-${SCRIPT_DIR}/run-consumer-google-voice-takeout.sh}"
WATCH_WRAPPER="${HACC_CONSUMER_TAKEOUT_WATCH_WRAPPER:-${SCRIPT_DIR}/watch-consumer-google-voice-takeout.sh}"

ACQUISITION_MANIFEST=""
WATCH_INTERVAL_SECONDS=""
WATCH_MAX_ITERATIONS=""
RUN_ARGS=()
WATCH_RESUME_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --acquisition-manifest)
            ACQUISITION_MANIFEST="$2"
            RUN_ARGS+=("$1" "$2")
            shift 2
            ;;
        --acquisition-manifest=*)
            ACQUISITION_MANIFEST="${1#*=}"
            RUN_ARGS+=("$1")
            shift
            ;;
        --watch-interval-seconds)
            WATCH_INTERVAL_SECONDS="$2"
            shift 2
            ;;
        --watch-interval-seconds=*)
            WATCH_INTERVAL_SECONDS="${1#*=}"
            shift
            ;;
        --watch-max-iterations)
            WATCH_MAX_ITERATIONS="$2"
            shift 2
            ;;
        --watch-max-iterations=*)
            WATCH_MAX_ITERATIONS="${1#*=}"
            shift
            ;;
        --watch-resume-arg)
            WATCH_RESUME_ARGS+=("$2")
            shift 2
            ;;
        --watch-resume-arg=*)
            WATCH_RESUME_ARGS+=("${1#*=}")
            shift
            ;;
        --bundle-output-dir)
            RUN_ARGS+=("$1" "$2")
            WATCH_RESUME_ARGS+=("--bundle-output-dir" "$2")
            shift 2
            ;;
        --bundle-output-dir=*)
            RUN_ARGS+=("$1")
            WATCH_RESUME_ARGS+=("$1")
            shift
            ;;
        --bundle-format)
            RUN_ARGS+=("$1" "$2")
            WATCH_RESUME_ARGS+=("--bundle-format" "$2")
            shift 2
            ;;
        --bundle-format=*)
            RUN_ARGS+=("$1")
            WATCH_RESUME_ARGS+=("$1")
            shift
            ;;
        *)
            RUN_ARGS+=("$1")
            shift
            ;;
    esac
done

echo "=== Starting consumer Google Voice Takeout run ==="
"$CONSUMER_WRAPPER" "${RUN_ARGS[@]}"

if [[ -z "$ACQUISITION_MANIFEST" ]]; then
    ACQUISITION_MANIFEST="$(
        python3 - <<'PY' "$SCRIPT_DIR"
import json
import pathlib
import sys
script_dir = pathlib.Path(sys.argv[1])
candidates = sorted(
    script_dir.glob("evidence/email_imports/*-takeout-downloads/takeout_acquisition_manifest.json"),
    key=lambda path: path.stat().st_mtime,
    reverse=True,
)
print(str(candidates[0]) if candidates else "")
PY
)"
fi

if [[ -z "$ACQUISITION_MANIFEST" || ! -f "$ACQUISITION_MANIFEST" ]]; then
    echo "ERROR: acquisition manifest not found after initial run." >&2
    exit 2
fi

echo ""
echo "=== Watching acquisition manifest ==="
WATCH_CMD=(
    "$WATCH_WRAPPER"
    --manifest "$ACQUISITION_MANIFEST"
)
if [[ -n "$WATCH_INTERVAL_SECONDS" ]]; then
    WATCH_CMD+=(--interval-seconds "$WATCH_INTERVAL_SECONDS")
fi
if [[ -n "$WATCH_MAX_ITERATIONS" ]]; then
    WATCH_CMD+=(--max-iterations "$WATCH_MAX_ITERATIONS")
fi
for arg in "${WATCH_RESUME_ARGS[@]}"; do
    WATCH_CMD+=(--resume-arg "$arg")
done
"${WATCH_CMD[@]}"
