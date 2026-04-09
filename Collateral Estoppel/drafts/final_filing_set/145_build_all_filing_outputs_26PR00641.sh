#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"

# Optional args:
# 1-3 => EX8 EX9 EX10 for master/exhibit booklet full build
# 4-7 => CF1 CF2 CF3 CF4 for supplemental full build
EX8="${1:-}"
EX9="${2:-}"
EX10="${3:-}"
CF1="${4:-}"
CF2="${5:-}"
CF3="${6:-}"
CF4="${7:-}"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd pdfinfo
need_cmd ls

mkdir -p "$OUT"

if [[ -n "$EX8" && -n "$EX9" && -n "$EX10" ]]; then
  "$BASE/129_build_master_filing_packet_pdf.sh" "$EX8" "$EX9" "$EX10"
else
  "$BASE/129_build_master_filing_packet_pdf.sh"
fi

if [[ -n "$CF1" && -n "$CF2" && -n "$CF3" && -n "$CF4" ]]; then
  "$BASE/143_build_supplemental_cross_forum_packet_pdf.sh" "$CF1" "$CF2" "$CF3" "$CF4"
else
  "$BASE/143_build_supplemental_cross_forum_packet_pdf.sh"
fi

echo

echo "=== Built Filing Outputs ==="
ls -lh \
  "$OUT"/Master_Filing_Packet_26PR00641.pdf \
  "$OUT"/Exhibit_Booklet_Current_Exhibits_1_7.pdf \
  "$OUT"/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf 2>/dev/null || true

[[ -f "$OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf" ]] && ls -lh "$OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf"
[[ -f "$OUT/Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf" ]] && ls -lh "$OUT/Supplemental_Cross_Forum_Full_Packet_26PR00641.pdf"

echo

echo "=== Quick PDF Stats ==="
for f in \
  "$OUT/Master_Filing_Packet_26PR00641.pdf" \
  "$OUT/Supplemental_Cross_Forum_Core_Packet_26PR00641.pdf"; do
  if [[ -f "$f" ]]; then
    echo "-- $f"
    pdfinfo "$f" | sed -n '1,14p' | rg 'Pages|Page size|File size|Title|PDF version' || true
  fi
done
