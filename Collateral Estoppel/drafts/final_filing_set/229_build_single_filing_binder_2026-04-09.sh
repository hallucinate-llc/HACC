#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"
RENDER="$BASE/131_render_pleading_pdf.py"
BINDER="$OUT/Court_Ready_Single_Filing_Binder_26PR00641_2026-04-09_rev1.pdf"

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

mkdir -p "$OUT"

# Filing-safe package (excludes known prefill/template compel docs 24/88/89).
FILES=(
  "195_filing_transmittal_note_authoritative_packet_2026-04-09.md"
  "194_court_filing_packet_version_index_2026-04-09.md"
  "00_exhibit_legend_global.md"
  "01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md"
  "02_motion_to_dismiss_for_collateral_estoppel_final.md"
  "03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.md"
  "03A_motion_to_show_cause_re_solomon_housing_interference_final.md"
  "151_motion_for_limited_orcp29_joinder_or_separate_forum_order_re_hacc_quantum_final.md"
  "152_objection_to_first_amended_guardianship_petition_and_emergency_relief_final.md"
  "152_fallback_motion_to_exclude_or_strike_collateral_housing_merits_from_probate_final.md"
  "157_supplemental_declaration_re_orcp29a_complete_relief_and_inconsistent_obligations_final.md"
  "177_declaration_of_benjamin_barber_court_safe_trimmed_final_2026-04-09.md"
  "219_declaration_of_benjamin_barber_short_form_threshold_relief_final_2026-04-09.md"
  "182_supplemental_declaration_re_sheriff_service_event_2026-04-09.md"
  "189_notice_of_filing_supplemental_service_and_certified_record_status_update_2026-04-09.md"
  "190_certificate_of_service_for_notice_of_filing_supplemental_service_and_certified_record_status_update_2026-04-09.md"
  "196_supplemental_declaration_authenticating_april_9_2026_transmission_records.md"
  "197_notice_of_filing_supplemental_declaration_april_9_transmission_records.md"
  "198_certificate_of_service_for_notice_and_supplemental_declaration_april_9_transmission_records.md"
  "07_proposed_order_appoint_gal_final.md"
  "08_proposed_order_dismiss_collateral_estoppel_final.md"
  "09_proposed_order_show_cause_final.md"
  "153_proposed_order_on_objection_to_guardianship_petition_and_emergency_relief_final.md"
  "154_proposed_order_re_limited_orcp29_joinder_or_separate_forum_final.md"
  "155_proposed_order_re_fallback_exclusion_or_strike_of_collateral_housing_merits_final.md"
)

PDFS=()
for f in "${FILES[@]}"; do
  src="$BASE/$f"
  [[ -f "$src" ]] || {
    echo "Missing source file: $src" >&2
    exit 1
  }
  out_pdf="$OUT/${f%.md}.pdf"
  python3 "$RENDER" "$src" "$out_pdf"
  PDFS+=("$out_pdf")
done

pdfunite "${PDFS[@]}" "$BINDER"

echo "Built binder: $BINDER"
pdfinfo "$BINDER" | sed -n '1,18p'

