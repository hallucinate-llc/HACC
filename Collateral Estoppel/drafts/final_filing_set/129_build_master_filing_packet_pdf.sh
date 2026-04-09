#!/usr/bin/env bash
set -euo pipefail

BASE="/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set"
OUT="$BASE/print_build_2026-04-08"
RENDER="$BASE/131_render_pleading_pdf.py"
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

# Build exhibit booklet first (current 1-7, or full 1-10 if args provided)
"$BASE/128_build_exhibit_booklet_pdf.sh" "$@"

# Convert filing packet markdown files to court-style PDF
render_file() {
  local src="$1"
  local out="$2"
  local title="$3"
  python3 "$RENDER" "$src" "$out" "$title"
}

render_file "$BASE/01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md" "$OUT/01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.pdf" "Motion for Appointment and Appearance of Guardian ad Litem"
render_file "$BASE/02_motion_to_dismiss_for_collateral_estoppel_final.md" "$OUT/02_motion_to_dismiss_for_collateral_estoppel_final.pdf" "Motion to Limit Issues Pending Threshold Issue Preclusion Record"
render_file "$BASE/03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.md" "$OUT/03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.pdf" "Motion to Show Cause re Failure to Appear and Barred Claim"
render_file "$BASE/03A_motion_to_show_cause_re_solomon_housing_interference_final.md" "$OUT/03A_motion_to_show_cause_re_solomon_housing_interference_final.pdf" "Motion to Show Cause re Housing Interference"
render_file "$BASE/04_declaration_of_benjamin_barber_in_support_of_motions_final.md" "$OUT/04_declaration_of_benjamin_barber_in_support_of_motions_final.pdf" "Declaration of Benjamin Barber in Support of Motions"
render_file "$BASE/05_certificate_of_service_final.md" "$OUT/05_certificate_of_service_final.pdf" "Certificate of Service"
render_file "$BASE/06_oregon_authority_table_final.md" "$OUT/06_oregon_authority_table_final.pdf" "Oregon Authority Table"
render_file "$BASE/07_proposed_order_appoint_gal_final.md" "$OUT/07_proposed_order_appoint_gal_final.pdf" "Proposed Order Appointing Guardian ad Litem"
render_file "$BASE/08_proposed_order_dismiss_collateral_estoppel_final.md" "$OUT/08_proposed_order_dismiss_collateral_estoppel_final.pdf" "Proposed Order on Threshold Issue Preclusion"
render_file "$BASE/09_proposed_order_show_cause_final.md" "$OUT/09_proposed_order_show_cause_final.pdf" "Proposed Order to Show Cause"
render_file "$BASE/74_motion_for_leave_to_file_supplemental_certified_exhibits_8_9_10_final.md" "$OUT/74_motion_for_leave_to_file_supplemental_certified_exhibits_8_9_10_final.pdf" "Motion for Leave to File Supplemental Certified Exhibits 8 9 and 10"
render_file "$BASE/75_certificate_of_service_for_supplemental_certified_exhibits_8_9_10_final.md" "$OUT/75_certificate_of_service_for_supplemental_certified_exhibits_8_9_10_final.pdf" "Certificate of Service for Supplemental Certified Exhibits 8 9 and 10"
render_file "$BASE/117_supplemental_declaration_authenticating_google_voice_sms_service_chain_final.md" "$OUT/117_supplemental_declaration_authenticating_google_voice_sms_service_chain_final.pdf" "Supplemental Declaration Authenticating Google Voice SMS Service Chain"
render_file "$BASE/118_notice_of_filing_supplemental_declaration_google_voice_sms_service_chain_final.md" "$OUT/118_notice_of_filing_supplemental_declaration_google_voice_sms_service_chain_final.pdf" "Notice of Filing Supplemental Declaration"
render_file "$BASE/119_certificate_of_service_for_supplemental_declaration_google_voice_sms_service_chain_final.md" "$OUT/119_certificate_of_service_for_supplemental_declaration_google_voice_sms_service_chain_final.pdf" "Certificate of Service for Supplemental Declaration"

BOOKLET_CURRENT="$OUT/Exhibit_Booklet_Current_Exhibits_1_7.pdf"
BOOKLET_FULL="$OUT/Exhibit_Booklet_Full_Exhibits_1_10.pdf"

BOOKLET="$BOOKLET_CURRENT"
if [[ -f "$BOOKLET_FULL" ]]; then
  BOOKLET="$BOOKLET_FULL"
fi

# Build one merged filing packet
pdfunite \
  "$OUT/01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.pdf" \
  "$OUT/02_motion_to_dismiss_for_collateral_estoppel_final.pdf" \
  "$OUT/03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.pdf" \
  "$OUT/03A_motion_to_show_cause_re_solomon_housing_interference_final.pdf" \
  "$OUT/04_declaration_of_benjamin_barber_in_support_of_motions_final.pdf" \
  "$OUT/05_certificate_of_service_final.pdf" \
  "$OUT/06_oregon_authority_table_final.pdf" \
  "$OUT/07_proposed_order_appoint_gal_final.pdf" \
  "$OUT/08_proposed_order_dismiss_collateral_estoppel_final.pdf" \
  "$OUT/09_proposed_order_show_cause_final.pdf" \
  "$OUT/74_motion_for_leave_to_file_supplemental_certified_exhibits_8_9_10_final.pdf" \
  "$OUT/75_certificate_of_service_for_supplemental_certified_exhibits_8_9_10_final.pdf" \
  "$OUT/117_supplemental_declaration_authenticating_google_voice_sms_service_chain_final.pdf" \
  "$OUT/118_notice_of_filing_supplemental_declaration_google_voice_sms_service_chain_final.pdf" \
  "$OUT/119_certificate_of_service_for_supplemental_declaration_google_voice_sms_service_chain_final.pdf" \
  "$BOOKLET" \
  "$OUT/Master_Filing_Packet_26PR00641.pdf"

echo "Built: $OUT/Master_Filing_Packet_26PR00641.pdf"
pdfinfo "$OUT/Master_Filing_Packet_26PR00641.pdf" | sed -n '1,18p'
