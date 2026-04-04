#!/usr/bin/env bash
# watch-consumer-google-voice-takeout.sh — Poll a Takeout acquisition manifest and advance it until complete
#
# Examples:
#   ./watch-consumer-google-voice-takeout.sh --manifest ./takeout_acquisition_manifest.json
#   ./watch-consumer-google-voice-takeout.sh --manifest ./takeout_acquisition_manifest.json --interval-seconds 60 --resume-arg --skip-index

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
IPFS_DATASETS_CLI="${HACC_IPFS_DATASETS_CLI:-${SCRIPT_DIR}/complaint-generator/ipfs_datasets_py/ipfs_datasets_cli.py}"
CONSUMER_WRAPPER="${HACC_CONSUMER_TAKEOUT_WRAPPER:-${SCRIPT_DIR}/run-consumer-google-voice-takeout.sh}"

MANIFEST=""
INTERVAL_SECONDS=30
MAX_ITERATIONS=120
RESUME_ARGS=()

run_doctor_json() {
    "$VENV_PYTHON" - <<'PY' "$VENV_PYTHON" "$IPFS_DATASETS_CLI" "$MANIFEST"
import json
import subprocess
import sys

python_bin, cli_path, manifest_path = sys.argv[1:]
proc = subprocess.run(
    [python_bin, cli_path, "email", "google-voice-takeout-doctor", manifest_path, "--json"],
    capture_output=True,
    text=True,
    check=False,
)
combined = (proc.stdout or "").strip()
if not combined:
    combined = (proc.stderr or "").strip()
start = combined.find("{")
end = combined.rfind("}")
if start != -1 and end != -1 and end >= start:
    payload = json.loads(combined[start:end+1])
else:
    payload = {}
    for line in combined.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        normalized = key.strip().lower().replace(" ", "_")
        payload[normalized] = value.strip()
    if not payload:
        raise SystemExit(f"Could not parse doctor output: {combined}")
print(json.dumps(payload))
PY
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --manifest)
            MANIFEST="$2"
            shift 2
            ;;
        --manifest=*)
            MANIFEST="${1#*=}"
            shift
            ;;
        --interval-seconds)
            INTERVAL_SECONDS="$2"
            shift 2
            ;;
        --interval-seconds=*)
            INTERVAL_SECONDS="${1#*=}"
            shift
            ;;
        --max-iterations)
            MAX_ITERATIONS="$2"
            shift 2
            ;;
        --max-iterations=*)
            MAX_ITERATIONS="${1#*=}"
            shift
            ;;
        --resume-arg)
            RESUME_ARGS+=("$2")
            shift 2
            ;;
        --resume-arg=*)
            RESUME_ARGS+=("${1#*=}")
            shift
            ;;
        *)
            echo "Unknown argument: $1" >&2
            exit 2
            ;;
    esac
done

if [[ -z "$MANIFEST" ]]; then
    echo "ERROR: --manifest is required" >&2
    exit 2
fi

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

MANIFEST="$(realpath -m "$MANIFEST")"
if [[ ! -f "$MANIFEST" ]]; then
    echo "ERROR: manifest not found: $MANIFEST" >&2
    exit 2
fi

for (( iteration=1; iteration<=MAX_ITERATIONS; iteration++ )); do
    echo "=== Takeout watch iteration ${iteration}/${MAX_ITERATIONS} ==="
    DIAGNOSIS_JSON="$(run_doctor_json)"
    DIAGNOSIS="$("$VENV_PYTHON" - <<'PY' "$DIAGNOSIS_JSON"
import json, sys
payload = json.loads(sys.argv[1])
print(payload.get("diagnosis") or "")
PY
)"
    STATUS="$("$VENV_PYTHON" - <<'PY' "$DIAGNOSIS_JSON"
import json, sys
payload = json.loads(sys.argv[1])
print(payload.get("status") or "")
PY
)"
    NEXT_STEP="$("$VENV_PYTHON" - <<'PY' "$DIAGNOSIS_JSON"
import json, sys
payload = json.loads(sys.argv[1])
print(payload.get("next_step") or "")
PY
)"

    echo "Diagnosis : ${DIAGNOSIS:-unknown}"
    echo "Status    : ${STATUS:-unknown}"
    echo "Next step : ${NEXT_STEP:-unknown}"

    if [[ "$DIAGNOSIS" == "complete" ]]; then
        echo "Takeout acquisition is complete."
        exit 0
    fi
    if [[ "$DIAGNOSIS" == "manual_browser_required" ]]; then
        echo "Takeout acquisition requires a desktop browser session before it can continue."
        exit 0
    fi

    "$CONSUMER_WRAPPER" --resume-from-manifest "$MANIFEST" "${RESUME_ARGS[@]}"

    POST_JSON="$(run_doctor_json)"
    POST_DIAGNOSIS="$("$VENV_PYTHON" - <<'PY' "$POST_JSON"
import json, sys
payload = json.loads(sys.argv[1])
print(payload.get("diagnosis") or "")
PY
)"
    if [[ "$POST_DIAGNOSIS" == "complete" ]]; then
        echo "Takeout acquisition completed during watch iteration ${iteration}."
        exit 0
    fi
    if [[ "$POST_DIAGNOSIS" == "manual_browser_required" ]]; then
        echo "Takeout acquisition is waiting for a desktop browser session."
        exit 0
    fi

    if (( iteration < MAX_ITERATIONS )); then
        sleep "$INTERVAL_SECONDS"
    fi
done

echo "Timed out after ${MAX_ITERATIONS} watch iterations." >&2
exit 1
