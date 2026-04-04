#!/usr/bin/env bash
# run-consumer-google-voice-takeout.sh — Consumer Google Voice Takeout acquisition + hydration
#
# Examples:
#   ./run-consumer-google-voice-takeout.sh --product-id voice
#   ./run-consumer-google-voice-takeout.sh --page-source ./takeout_page.html --auto-submit
#   ./run-consumer-google-voice-takeout.sh --page-source ./takeout_page.html --skip-index --import-arg --upload-to-workspace
#   ./run-consumer-google-voice-takeout.sh --capture-page-source --page-source ./takeout_page.html
#   ./run-consumer-google-voice-takeout.sh --resume-from-downloads ./takeout-downloads
#   ./run-consumer-google-voice-takeout.sh --dest drive --drive-client-secrets ./google-client-secret.json --drive-account-hint user@gmail.com
#   ./run-consumer-google-voice-takeout.sh --product-id voice --bundle-output-dir ./takeout-bundles --bundle-format zip --bundle-format car

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PYTHON="${HACC_VENV_PYTHON:-${SCRIPT_DIR}/.venv/bin/python}"
IPFS_DATASETS_CLI="${HACC_IPFS_DATASETS_CLI:-${SCRIPT_DIR}/complaint-generator/ipfs_datasets_py/ipfs_datasets_cli.py}"
VOICE_WRAPPER="${HACC_VOICE_WRAPPER:-${SCRIPT_DIR}/run-google-voice-ingest.sh}"

PAGE_SOURCE=""
CASE_SLUG=""
DEST="drive"
FREQUENCY="one_time"
AUTO_SUBMIT=false
HEADLESS=false
RUN_INDEX=true
DOWNLOAD_TIMEOUT_MS=300000
POLL_ONLY=false
CAPTURE_PAGE_SOURCE=false
PRODUCT_IDS=()
IMPORT_ARGS=()
INDEX_ARGS=()
USER_DATA_DIR=""
DOWNLOADS_DIR=""
CAPTURE_JSON=""
RESUME_FROM_DOWNLOADS=""
DRIVE_CLIENT_SECRETS=""
DRIVE_ACCOUNT_HINT=""
DRIVE_TOKEN_CACHE=""
DRIVE_NAME_CONTAINS="takeout"
ACQUISITION_MANIFEST=""
RESUME_FROM_MANIFEST=""
ACQUISITION_HISTORY_DIR=""
BUNDLE_OUTPUT_DIR=""
BUNDLE_FORMATS=()
BUNDLE_RESULT_JSON=""

snapshot_manifest() {
    local reason="${1:-snapshot}"
    if [[ -z "${ACQUISITION_MANIFEST:-}" || -z "${ACQUISITION_HISTORY_DIR:-}" ]]; then
        return
    fi
    if [[ ! -f "$ACQUISITION_MANIFEST" ]]; then
        return
    fi
    mkdir -p "$ACQUISITION_HISTORY_DIR"
    local timestamp
    timestamp="$(date +%Y%m%d_%H%M%S)"
    cp "$ACQUISITION_MANIFEST" "${ACQUISITION_HISTORY_DIR}/${timestamp}_${reason}.json"
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --product-id)
            PRODUCT_IDS+=("$2")
            shift 2
            ;;
        --product-id=*)
            PRODUCT_IDS+=("${1#*=}")
            shift
            ;;
        --page-source)
            PAGE_SOURCE="$2"
            shift 2
            ;;
        --page-source=*)
            PAGE_SOURCE="${1#*=}"
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
        --dest)
            DEST="$2"
            shift 2
            ;;
        --dest=*)
            DEST="${1#*=}"
            shift
            ;;
        --frequency)
            FREQUENCY="$2"
            shift 2
            ;;
        --frequency=*)
            FREQUENCY="${1#*=}"
            shift
            ;;
        --auto-submit)
            AUTO_SUBMIT=true
            shift
            ;;
        --capture-page-source)
            CAPTURE_PAGE_SOURCE=true
            shift
            ;;
        --headless)
            HEADLESS=true
            shift
            ;;
        --poll-only)
            POLL_ONLY=true
            shift
            ;;
        --skip-index)
            RUN_INDEX=false
            shift
            ;;
        --download-timeout-ms)
            DOWNLOAD_TIMEOUT_MS="$2"
            shift 2
            ;;
        --download-timeout-ms=*)
            DOWNLOAD_TIMEOUT_MS="${1#*=}"
            shift
            ;;
        --user-data-dir)
            USER_DATA_DIR="$2"
            shift 2
            ;;
        --user-data-dir=*)
            USER_DATA_DIR="${1#*=}"
            shift
            ;;
        --downloads-dir)
            DOWNLOADS_DIR="$2"
            shift 2
            ;;
        --downloads-dir=*)
            DOWNLOADS_DIR="${1#*=}"
            shift
            ;;
        --resume-from-downloads)
            RESUME_FROM_DOWNLOADS="$2"
            shift 2
            ;;
        --resume-from-downloads=*)
            RESUME_FROM_DOWNLOADS="${1#*=}"
            shift
            ;;
        --capture-json)
            CAPTURE_JSON="$2"
            shift 2
            ;;
        --capture-json=*)
            CAPTURE_JSON="${1#*=}"
            shift
            ;;
        --drive-client-secrets)
            DRIVE_CLIENT_SECRETS="$2"
            shift 2
            ;;
        --drive-client-secrets=*)
            DRIVE_CLIENT_SECRETS="${1#*=}"
            shift
            ;;
        --drive-account-hint)
            DRIVE_ACCOUNT_HINT="$2"
            shift 2
            ;;
        --drive-account-hint=*)
            DRIVE_ACCOUNT_HINT="${1#*=}"
            shift
            ;;
        --drive-token-cache)
            DRIVE_TOKEN_CACHE="$2"
            shift 2
            ;;
        --drive-token-cache=*)
            DRIVE_TOKEN_CACHE="${1#*=}"
            shift
            ;;
        --drive-name-contains)
            DRIVE_NAME_CONTAINS="$2"
            shift 2
            ;;
        --drive-name-contains=*)
            DRIVE_NAME_CONTAINS="${1#*=}"
            shift
            ;;
        --acquisition-manifest)
            ACQUISITION_MANIFEST="$2"
            shift 2
            ;;
        --acquisition-manifest=*)
            ACQUISITION_MANIFEST="${1#*=}"
            shift
            ;;
        --resume-from-manifest)
            RESUME_FROM_MANIFEST="$2"
            shift 2
            ;;
        --resume-from-manifest=*)
            RESUME_FROM_MANIFEST="${1#*=}"
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

if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "ERROR: venv python not found at $VENV_PYTHON" >&2
    exit 2
fi

if [[ -n "$RESUME_FROM_MANIFEST" ]]; then
    RESUME_FROM_MANIFEST="$(realpath -m "$RESUME_FROM_MANIFEST")"
    if [[ ! -f "$RESUME_FROM_MANIFEST" ]]; then
        echo "ERROR: acquisition manifest not found: $RESUME_FROM_MANIFEST" >&2
        exit 2
    fi
    LOADED_FIELDS=()
    LOAD_RESULT="$("$VENV_PYTHON" - <<'PY' "$RESUME_FROM_MANIFEST"
import json, sys
payload = json.load(open(sys.argv[1], "r", encoding="utf-8"))
fields = [
    payload.get("case_slug") or "",
    payload.get("delivery_destination") or "",
    payload.get("frequency") or "",
    payload.get("page_source_path") or "",
    payload.get("downloads_dir") or "",
    payload.get("capture_json_path") or "",
    str(((payload.get("drive_fallback") or {}).get("name_contains")) or ""),
    str(((payload.get("drive_fallback") or {}).get("client_secrets_path")) or ""),
    str(((payload.get("drive_fallback") or {}).get("account_hint")) or ""),
]
print("\n".join(fields))
for item in list(payload.get("product_ids") or []):
    print(f"PRODUCT::{item}")
PY
)"
    while IFS= read -r line; do
        case "$line" in
            PRODUCT::*)
                product_id="${line#PRODUCT::}"
                if [[ -n "$product_id" ]]; then
                    PRODUCT_IDS+=("$product_id")
                fi
                ;;
            *)
                LOADED_FIELDS+=("$line")
                ;;
        esac
    done <<< "$LOAD_RESULT"
    if [[ ${#LOADED_FIELDS[@]} -ge 9 ]]; then
        [[ -z "$CASE_SLUG" ]] && CASE_SLUG="${LOADED_FIELDS[0]}"
        [[ "$DEST" == "drive" ]] && [[ -n "${LOADED_FIELDS[1]}" ]] && DEST="${LOADED_FIELDS[1]}"
        [[ "$FREQUENCY" == "one_time" ]] && [[ -n "${LOADED_FIELDS[2]}" ]] && FREQUENCY="${LOADED_FIELDS[2]}"
        [[ -z "$PAGE_SOURCE" ]] && PAGE_SOURCE="${LOADED_FIELDS[3]}"
        [[ -z "$DOWNLOADS_DIR" ]] && DOWNLOADS_DIR="${LOADED_FIELDS[4]}"
        [[ -z "$CAPTURE_JSON" ]] && CAPTURE_JSON="${LOADED_FIELDS[5]}"
        [[ "$DRIVE_NAME_CONTAINS" == "takeout" ]] && [[ -n "${LOADED_FIELDS[6]}" ]] && DRIVE_NAME_CONTAINS="${LOADED_FIELDS[6]}"
        [[ -z "$DRIVE_CLIENT_SECRETS" ]] && DRIVE_CLIENT_SECRETS="${LOADED_FIELDS[7]}"
        [[ -z "$DRIVE_ACCOUNT_HINT" ]] && DRIVE_ACCOUNT_HINT="${LOADED_FIELDS[8]}"
    fi
    if [[ -z "$RESUME_FROM_DOWNLOADS" && -n "$DOWNLOADS_DIR" ]]; then
        RESUME_FROM_DOWNLOADS="$DOWNLOADS_DIR"
    fi
    [[ -z "$ACQUISITION_MANIFEST" ]] && ACQUISITION_MANIFEST="$RESUME_FROM_MANIFEST"
fi

if [[ -n "$RESUME_FROM_DOWNLOADS" ]]; then
    DOWNLOADS_DIR="$RESUME_FROM_DOWNLOADS"
fi

if [[ ${#PRODUCT_IDS[@]} -eq 0 && -z "$PAGE_SOURCE" && "$CAPTURE_PAGE_SOURCE" == false && -z "$RESUME_FROM_DOWNLOADS" ]]; then
    echo "ERROR: supply at least one --product-id or a --page-source file" >&2
    exit 2
fi

if [[ -n "$PAGE_SOURCE" && -z "$RESUME_FROM_DOWNLOADS" ]]; then
    PAGE_SOURCE="$(realpath -m "$PAGE_SOURCE")"
    if [[ ! -f "$PAGE_SOURCE" ]]; then
        echo "ERROR: page source not found: $PAGE_SOURCE" >&2
        exit 2
    fi
fi

if [[ -z "$CASE_SLUG" ]]; then
    CASE_SLUG="consumer-google-voice-$(date +%Y%m%d_%H%M%S)"
fi

if [[ -z "$DOWNLOADS_DIR" ]]; then
    DOWNLOADS_DIR="${SCRIPT_DIR}/evidence/email_imports/${CASE_SLUG}-takeout-downloads"
fi
mkdir -p "$DOWNLOADS_DIR"

if [[ "$CAPTURE_PAGE_SOURCE" == true && -z "$PAGE_SOURCE" ]]; then
    PAGE_SOURCE="${DOWNLOADS_DIR}/takeout_page.html"
fi

if [[ -z "$CAPTURE_JSON" ]]; then
    CAPTURE_JSON="${DOWNLOADS_DIR}/takeout_capture.json"
fi

if [[ -z "$ACQUISITION_MANIFEST" ]]; then
    ACQUISITION_MANIFEST="${DOWNLOADS_DIR}/takeout_acquisition_manifest.json"
fi

if [[ -z "$ACQUISITION_HISTORY_DIR" ]]; then
    ACQUISITION_HISTORY_DIR="${DOWNLOADS_DIR}/takeout_acquisition_history"
fi

NO_DISPLAY_BROWSER=false
if [[ -z "${DISPLAY:-}" && "$HEADLESS" == false && -z "$RESUME_FROM_DOWNLOADS" && "$POLL_ONLY" == false ]]; then
    NO_DISPLAY_BROWSER=true
fi

if [[ -z "$BUNDLE_OUTPUT_DIR" && ${#BUNDLE_FORMATS[@]} -gt 0 ]]; then
    BUNDLE_OUTPUT_DIR="${SCRIPT_DIR}/evidence/email_imports/takeout-case-bundles"
fi

if [[ -n "$BUNDLE_OUTPUT_DIR" ]]; then
    mkdir -p "$BUNDLE_OUTPUT_DIR"
    BUNDLE_OUTPUT_DIR="$(realpath -m "$BUNDLE_OUTPUT_DIR")"
    BUNDLE_RESULT_JSON="${DOWNLOADS_DIR}/takeout_case_bundle.json"
fi

"$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CASE_SLUG" "$DEST" "$FREQUENCY" "$PAGE_SOURCE" "$DOWNLOADS_DIR" "$CAPTURE_JSON" "$DRIVE_NAME_CONTAINS" "$DRIVE_CLIENT_SECRETS" "$DRIVE_ACCOUNT_HINT"
import json, sys
from datetime import datetime, UTC
manifest_path, case_slug, dest, frequency, page_source, downloads_dir, capture_json, drive_name_contains, drive_client_secrets, drive_account_hint = sys.argv[1:]
payload = {
    "status": "initialized",
    "updated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    "case_slug": case_slug,
    "delivery_destination": dest,
    "frequency": frequency,
    "page_source_path": page_source or None,
    "downloads_dir": downloads_dir,
    "capture_json_path": capture_json,
    "drive_fallback": {
        "enabled": bool(drive_client_secrets and drive_account_hint),
        "name_contains": drive_name_contains,
        "client_secrets_path": drive_client_secrets or None,
        "account_hint": drive_account_hint or None,
    },
    "product_ids": [],
    "events": [
        {
            "type": "initialized",
            "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        }
    ],
}
with open(manifest_path, "w", encoding="utf-8") as handle:
    json.dump(payload, handle, indent=2, ensure_ascii=False)
PY
snapshot_manifest "initialized"

for product_id in "${PRODUCT_IDS[@]}"; do
    "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$product_id"
import json, sys
manifest_path, product_id = sys.argv[1:]
payload = json.load(open(manifest_path, "r", encoding="utf-8"))
product_ids = list(payload.get("product_ids") or [])
if product_id not in product_ids:
    product_ids.append(product_id)
payload["product_ids"] = product_ids
json.dump(payload, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
done
if [[ ${#PRODUCT_IDS[@]} -gt 0 ]]; then
    snapshot_manifest "products"
fi

if [[ "$NO_DISPLAY_BROWSER" == true ]]; then
    "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CAPTURE_JSON" "$DOWNLOADS_DIR"
import json, sys
from datetime import datetime, UTC
manifest_path, capture_json_path, downloads_dir = sys.argv[1:]
timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
capture_payload = {
    "status": "pending",
    "browser_capture": {
        "status": "manual_browser_required",
        "reason": "no_display",
        "message": "No X server / DISPLAY is available for the interactive Google Takeout browser flow.",
        "downloads_dir": downloads_dir,
        "started_at": timestamp,
    },
}
with open(capture_json_path, "w", encoding="utf-8") as handle:
    json.dump(capture_payload, handle, indent=2, ensure_ascii=False)
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
manifest["capture"] = capture_payload
manifest["status"] = "manual_browser_required"
manifest["updated_at"] = timestamp
manifest.setdefault("events", []).append({
    "type": "manual_browser_required",
    "timestamp": timestamp,
    "reason": "no_display",
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
    snapshot_manifest "manual_browser_required"
    echo ""
    echo "Interactive Google Takeout capture requires a desktop browser session."
    echo "No DISPLAY/X server is available in this environment, so the run was paused safely."
    echo "Capture JSON: $CAPTURE_JSON"
    echo "Acquisition manifest: $ACQUISITION_MANIFEST"
    echo "Next step: rerun this command on a machine with a browser/display, or resume later from the manifest."
    exit 0
fi

if [[ -n "$RESUME_FROM_DOWNLOADS" ]]; then
    echo "=== Polling existing download directory for completed archive ==="
    "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-poll \
        --downloads-dir "$DOWNLOADS_DIR" \
        --timeout-ms "$DOWNLOAD_TIMEOUT_MS" \
        --output "$CAPTURE_JSON"
else
    if [[ "$CAPTURE_PAGE_SOURCE" == true ]]; then
        echo "=== Capturing Google Takeout page source ==="
        SOURCE_CMD=(
            "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-source
            --output "$PAGE_SOURCE"
        )
        if [[ "$HEADLESS" == true ]]; then
            SOURCE_CMD+=(--headless)
        fi
        if [[ -n "$USER_DATA_DIR" ]]; then
            SOURCE_CMD+=(--user-data-dir "$USER_DATA_DIR")
        fi
        "${SOURCE_CMD[@]}"
        "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$PAGE_SOURCE"
import json, sys
from datetime import datetime, UTC
manifest_path, page_source = sys.argv[1:]
payload = json.load(open(manifest_path, "r", encoding="utf-8"))
payload["status"] = "page_source_captured"
payload["page_source_path"] = page_source
payload["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
payload.setdefault("events", []).append({
    "type": "page_source_captured",
    "timestamp": payload["updated_at"],
    "page_source_path": page_source,
})
        json.dump(payload, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
        snapshot_manifest "page_source_captured"
    fi

    if [[ "$POLL_ONLY" == false ]]; then
        CAPTURE_CMD=(
            "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-capture
            --dest "$DEST"
            --frequency "$FREQUENCY"
            --downloads-dir "$DOWNLOADS_DIR"
            --download-timeout-ms "$DOWNLOAD_TIMEOUT_MS"
            --output "$CAPTURE_JSON"
        )

        for product_id in "${PRODUCT_IDS[@]}"; do
            CAPTURE_CMD+=(--product-id "$product_id")
        done
        if [[ -n "$PAGE_SOURCE" ]]; then
            CAPTURE_CMD+=(--page-source "$PAGE_SOURCE")
        fi
        if [[ "$AUTO_SUBMIT" == true ]]; then
            CAPTURE_CMD+=(--auto-submit)
        fi
        if [[ "$HEADLESS" == true ]]; then
            CAPTURE_CMD+=(--headless)
        fi
        if [[ -n "$USER_DATA_DIR" ]]; then
            CAPTURE_CMD+=(--user-data-dir "$USER_DATA_DIR")
        fi

        echo "=== Opening Google Takeout and waiting for download ==="
        "${CAPTURE_CMD[@]}"
        "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CAPTURE_JSON"
import json, sys
from datetime import datetime, UTC
manifest_path, capture_json = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
capture_payload = json.load(open(capture_json, "r", encoding="utf-8"))
manifest["capture"] = capture_payload
manifest["status"] = "capture_attempted"
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest.setdefault("events", []).append({
    "type": "capture_attempted",
    "timestamp": manifest["updated_at"],
    "capture_status": (capture_payload.get("browser_capture") or capture_payload).get("status"),
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
        snapshot_manifest "capture_attempted"
    else
        echo "=== Poll-only mode: waiting for archive in existing downloads dir ==="
        "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-poll \
            --downloads-dir "$DOWNLOADS_DIR" \
            --timeout-ms "$DOWNLOAD_TIMEOUT_MS" \
            --output "$CAPTURE_JSON"
        "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CAPTURE_JSON"
import json, sys
from datetime import datetime, UTC
manifest_path, capture_json = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
capture_payload = json.load(open(capture_json, "r", encoding="utf-8"))
manifest["poll_result"] = capture_payload
manifest["status"] = "poll_attempted"
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest.setdefault("events", []).append({
    "type": "poll_attempted",
    "timestamp": manifest["updated_at"],
    "poll_status": capture_payload.get("status"),
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
        snapshot_manifest "poll_attempted"
    fi
fi

DOWNLOAD_PATH="$("$VENV_PYTHON" - <<'PY' "$CAPTURE_JSON"
import json, sys
path = sys.argv[1]
payload = json.load(open(path, "r", encoding="utf-8"))
capture = payload.get("browser_capture") or payload
print(capture.get("download_path") or "")
PY
)"

CAPTURE_STATUS="$("$VENV_PYTHON" - <<'PY' "$CAPTURE_JSON"
import json, sys
path = sys.argv[1]
payload = json.load(open(path, "r", encoding="utf-8"))
capture = payload.get("browser_capture") or payload
print(capture.get("status") or "")
PY
)"

if [[ -z "$DOWNLOAD_PATH" || ! -f "$DOWNLOAD_PATH" ]]; then
    if [[ "$DEST" == "drive" && -n "$DRIVE_CLIENT_SECRETS" && -n "$DRIVE_ACCOUNT_HINT" ]]; then
        echo ""
        echo "=== No local download captured yet; polling Google Drive ==="
        MODIFIED_AFTER="$("$VENV_PYTHON" - <<'PY' "$CAPTURE_JSON"
import json, sys
payload = json.load(open(sys.argv[1], "r", encoding="utf-8"))
capture = payload.get("browser_capture") or payload
print(capture.get("started_at") or payload.get("started_at") or "")
PY
)"
        DRIVE_CMD=(
            "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-drive
            --client-secrets "$DRIVE_CLIENT_SECRETS"
            --account-hint "$DRIVE_ACCOUNT_HINT"
            --name-contains "$DRIVE_NAME_CONTAINS"
            --timeout-ms "$DOWNLOAD_TIMEOUT_MS"
            --download-dir "$DOWNLOADS_DIR"
            --output "$CAPTURE_JSON"
        )
        if [[ -n "$DRIVE_TOKEN_CACHE" ]]; then
            DRIVE_CMD+=(--token-cache "$DRIVE_TOKEN_CACHE")
        fi
        if [[ -n "$MODIFIED_AFTER" ]]; then
            DRIVE_CMD+=(--modified-after "$MODIFIED_AFTER")
        fi
        "${DRIVE_CMD[@]}"
        "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CAPTURE_JSON"
import json, sys
from datetime import datetime, UTC
manifest_path, capture_json = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
drive_payload = json.load(open(capture_json, "r", encoding="utf-8"))
manifest["drive_result"] = drive_payload
manifest["status"] = "drive_fallback_attempted"
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest.setdefault("events", []).append({
    "type": "drive_fallback_attempted",
    "timestamp": manifest["updated_at"],
    "drive_status": drive_payload.get("status"),
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
        snapshot_manifest "drive_fallback_attempted"
        DOWNLOAD_PATH="$("$VENV_PYTHON" - <<'PY' "$CAPTURE_JSON"
import json, sys
payload = json.load(open(sys.argv[1], "r", encoding="utf-8"))
download = payload.get("download") or {}
print(download.get("output_path") or "")
PY
)"
    fi
fi

if [[ -z "$DOWNLOAD_PATH" || ! -f "$DOWNLOAD_PATH" ]]; then
    "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$CAPTURE_STATUS"
import json, sys
from datetime import datetime, UTC
manifest_path, capture_status = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
manifest["status"] = "pending_archive"
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest.setdefault("events", []).append({
    "type": "pending_archive",
    "timestamp": manifest["updated_at"],
    "capture_status": capture_status or None,
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
    snapshot_manifest "pending_archive"
    echo ""
    echo "Takeout capture did not produce a local archive yet."
    echo "Status: ${CAPTURE_STATUS:-unknown}"
    echo "Capture JSON: $CAPTURE_JSON"
    echo "Acquisition manifest: $ACQUISITION_MANIFEST"
    exit 0
fi

echo ""
echo "=== Hydrating captured Google Voice archive ==="
VOICE_CMD=(
    "$VOICE_WRAPPER"
    --source "$DOWNLOAD_PATH"
    --source-mode takeout
    --case-slug "$CASE_SLUG"
)
if [[ "$RUN_INDEX" == false ]]; then
    VOICE_CMD+=(--skip-index)
fi
for arg in "${IMPORT_ARGS[@]}"; do
    VOICE_CMD+=(--import-arg "$arg")
done
for arg in "${INDEX_ARGS[@]}"; do
    VOICE_CMD+=(--index-arg "$arg")
done
"${VOICE_CMD[@]}"

"$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$DOWNLOAD_PATH"
import json, sys
from datetime import datetime, UTC
manifest_path, download_path = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
manifest["status"] = "hydrated"
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest["final_archive_path"] = download_path
manifest.setdefault("events", []).append({
    "type": "hydrated",
    "timestamp": manifest["updated_at"],
    "final_archive_path": download_path,
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
snapshot_manifest "hydrated"

if [[ -n "$BUNDLE_OUTPUT_DIR" ]]; then
    echo ""
    echo "=== Bundling Takeout acquisition artifacts ==="
    BUNDLE_CMD=(
        "$VENV_PYTHON" "$IPFS_DATASETS_CLI" email google-voice-takeout-case-bundle
        "$ACQUISITION_MANIFEST"
        --output-dir "$BUNDLE_OUTPUT_DIR"
    )
    for fmt in "${BUNDLE_FORMATS[@]}"; do
        BUNDLE_CMD+=(--bundle-format "$fmt")
    done
    "${BUNDLE_CMD[@]}" > "$BUNDLE_RESULT_JSON"
    "$VENV_PYTHON" - <<'PY' "$ACQUISITION_MANIFEST" "$BUNDLE_RESULT_JSON"
import json, sys
from datetime import datetime, UTC
manifest_path, bundle_result_path = sys.argv[1:]
manifest = json.load(open(manifest_path, "r", encoding="utf-8"))
bundle_result = json.load(open(bundle_result_path, "r", encoding="utf-8"))
manifest["bundle_result"] = bundle_result
manifest["updated_at"] = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
manifest.setdefault("events", []).append({
    "type": "bundled",
    "timestamp": manifest["updated_at"],
    "bundle_dir": bundle_result.get("bundle_dir"),
    "bundle_formats": list(bundle_result.get("bundle_formats") or []),
})
json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
PY
    snapshot_manifest "bundled"
    echo "Bundle result JSON: $BUNDLE_RESULT_JSON"
fi

echo "Acquisition manifest: $ACQUISITION_MANIFEST"
