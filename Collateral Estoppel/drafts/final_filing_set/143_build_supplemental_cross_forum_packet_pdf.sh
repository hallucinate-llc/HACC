#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"
RENDER="$BASE/131_render_pleading_pdf.py"

CF1="${1:-}"
CF2="${2:-}"
CF3="${3:-}"
CF4="${4:-}"

mkdir -p "$OUT"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd python3
need_cmd pdfunite
need_cmd pdfinfo
[[ -f "$RENDER" ]] || {
  echo "Missing renderer: $RENDER" >&2
  exit 1
}

render_file() {
  local src="$1"
  local out="$2"
  local title="$3"
  python3 "$RENDER" "$src" "$out" "$title"
}

# Render packet docs (court-style letter)
render_file "$BASE/138_notice_of_filing_supplemental_cross_forum_docket_records_final.md" "$OUT/138_notice_of_filing_supplemental_cross_forum_docket_records_final.pdf" "Notice of Filing Supplemental Cross Forum Docket Order Records"
render_file "$BASE/139_supplemental_declaration_authenticating_cross_forum_docket_records_final.md" "$OUT/139_supplemental_declaration_authenticating_cross_forum_docket_records_final.pdf" "Supplemental Declaration Authenticating Cross Forum Docket Order Records"
render_file "$BASE/140_certificate_of_service_for_supplemental_cross_forum_docket_records_final.md" "$OUT/140_certificate_of_service_for_supplemental_cross_forum_docket_records_final.pdf" "Certificate of Service Supplemental Cross Forum Docket Order Records"
render_file "$BASE/141_proposed_order_re_supplemental_cross_forum_docket_records_final.md" "$OUT/141_proposed_order_re_supplemental_cross_forum_docket_records_final.pdf" "Proposed Order Re Supplemental Cross Forum Docket Order Records"

# Core packet (without external exhibits)
pdfunite \
  "$OUT/138_notice_of_filing_supplemental_cross_forum_docket_records_final.pdf" \
  "$OUT/139_supplemental_declaration_authenticating_cross_forum_docket_records_final.pdf" \
  "$OUT/140_certificate_of_service_for_supplemental_cross_forum_docket_records_final.pdf" \
  "$OUT/141_proposed_order_re_supplemental_cross_forum_docket_records_final.pdf" \
  "$OUT/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf"

echo "Built: $OUT/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf"

# Full packet if CF exhibits provided
if [[ -n "$CF1" && -n "$CF2" && -n "$CF3" && -n "$CF4" ]]; then
  for f in "$CF1" "$CF2" "$CF3" "$CF4"; do
    [[ -f "$f" ]] || {
      echo "Missing CF exhibit path: $f" >&2
      exit 1
    }
  done

  pdfunite \
    "$OUT/138_notice_of_filing_supplemental_cross_forum_docket_records_final.pdf" \
    "$OUT/139_supplemental_declaration_authenticating_cross_forum_docket_records_final.pdf" \
    "$OUT/140_certificate_of_service_for_supplemental_cross_forum_docket_records_final.pdf" \
    "$CF1" "$CF2" "$CF3" "$CF4" \
    "$OUT/141_proposed_order_re_supplemental_cross_forum_docket_records_final.pdf" \
    "$OUT/Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf"

  echo "Built: $OUT/Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf"
else
  echo "Skipped full packet (pass CF1 CF2 CF3 CF4 paths as args)."
fi

pdfinfo "$OUT/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf" | sed -n '1,18p'
