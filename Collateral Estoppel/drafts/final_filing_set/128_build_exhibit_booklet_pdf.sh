#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"
RENDER="$BASE/131_render_pleading_pdf.py"

EX8="${1:-}"
EX9="${2:-}"
EX10="${3:-}"

mkdir -p "$OUT"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "Missing required command: $1" >&2
    exit 1
  }
}

need_cmd python3
need_cmd pdfunite
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

render_file "$BASE/123_exhibit_booklet_cover_sheet_2026-04-08.md" "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" "Exhibit Booklet Cover Sheet"
render_file "$BASE/00_exhibit_legend_global.md" "$OUT/00_exhibit_legend_global.pdf" "Global Exhibit Legend"
render_file "$BASE/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.md" "$OUT/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.pdf" "Exhibit Proof and Reliance Summary Matrix"
render_file "$BASE/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.md" "$OUT/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.pdf" "Exhibit Tab Sheets 1 through 10"
render_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/sam_barber_restraining_order_ocr.txt" "$OUT/sam_barber_restraining_order_ocr.pdf" "Exhibit 1 OCR Extract"
render_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt" "$OUT/solomon_motion_for_guardianship_ocr.pdf" "Exhibit 2 OCR Extract"
render_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_evidence_graph_feed.json" "$OUT/solomon_evidence_graph_feed.pdf" "Exhibit 3 Evidence Graph Feed"
render_file "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json" "$OUT/deontic_reasoning_report.pdf" "Exhibit 4 Deontic Reasoning Report"
render_file "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/motion_support_map.json" "$OUT/motion_support_map.pdf" "Exhibit 5 Motion Support Map"
render_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/protective_order_and_hacc_notice_timeline.md" "$OUT/protective_order_and_hacc_notice_timeline.pdf" "Exhibit 6 Protective Order and HACC Timeline"

pdfunite \
  "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" \
  "$OUT/00_exhibit_legend_global.pdf" \
  "$OUT/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.pdf" \
  "$OUT/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.pdf" \
  "$OUT/sam_barber_restraining_order_ocr.pdf" \
  "$OUT/solomon_motion_for_guardianship_ocr.pdf" \
  "$OUT/solomon_evidence_graph_feed.pdf" \
  "$OUT/deontic_reasoning_report.pdf" \
  "$OUT/motion_support_map.pdf" \
  "$OUT/protective_order_and_hacc_notice_timeline.pdf" \
  "/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf" \
  "$OUT/Exhibit_Booklet_Current_Exhibits_1_7.pdf"

echo "Built: $OUT/Exhibit_Booklet_Current_Exhibits_1_7.pdf"

if [[ -n "$EX8" && -n "$EX9" && -n "$EX10" ]]; then
  pdfunite \
    "$OUT/123_exhibit_booklet_cover_sheet_2026-04-08.pdf" \
    "$OUT/00_exhibit_legend_global.pdf" \
    "$OUT/124_exhibit_proof_and_reliance_summary_matrix_2026-04-08.pdf" \
    "$OUT/125_exhibit_tab_sheets_1_10_header_only_2026-04-08.pdf" \
    "$OUT/sam_barber_restraining_order_ocr.pdf" \
    "$OUT/solomon_motion_for_guardianship_ocr.pdf" \
    "$OUT/solomon_evidence_graph_feed.pdf" \
    "$OUT/deontic_reasoning_report.pdf" \
    "$OUT/motion_support_map.pdf" \
    "$OUT/protective_order_and_hacc_notice_timeline.pdf" \
    "/home/barberb/HACC/evidence/paper documents/HACC vawa violation.pdf" \
    "$EX8" "$EX9" "$EX10" \
    "$OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf"

  echo "Built: $OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf"
else
  echo "Skipped full booklet (pass EX8 EX9 EX10 paths as args to include certified exhibits)."
fi
