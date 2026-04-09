#!/usr/bin/env bash
set -euo pipefail

DEST="/home/barberb/HACC/workspace/working-probate-missing-evidence-2026-04-09"

mkdir -p "$DEST/writ"
mkdir -p "$DEST/trust-authority"
mkdir -p "$DEST/support-notes"

copy_file() {
  local src="$1"
  local dst_dir="$2"
  if [[ -f "$src" ]]; then
    cp "$src" "$dst_dir/"
  else
    printf 'Missing file: %s\n' "$src" >&2
  fi
}

# Writ / predicate / notice packet
copy_file "/home/barberb/HACC/evidence/paper documents/writ of assistance solomon barber.pdf" "$DEST/writ"
copy_file "/home/barberb/HACC/evidence/email_imports/starworks5-live-fetch-2026-04-08/0053-Re-SERVICE-Jane-Kay-Cortez-vs-Solomon-Samuel-Barber-Benjamin-Jay-Barber-vs-Solomon-Samuel-Barber-CAMTdTS_Z0mYtELRxp-Q2jqsX6VFHwoe-i3BePhHA-TxYM6L5yw-mail.gmail.com/attachments/writ-of-assistance-solomon-barber.pdf" "$DEST/writ"
copy_file "/home/barberb/HACC/evidence/history/Solomon Motion for Guardianship.pdf" "$DEST/writ"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt" "$DEST/writ"

# Trust / authority packet
copy_file "/home/barberb/HACC/evidence/paper documents/Gerald miller jane cortez trust.pdf" "$DEST/trust-authority"
copy_file "/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml" "$DEST/trust-authority"
copy_file "/home/barberb/HACC/evidence/history/sam barber restraining order.pdf" "$DEST/trust-authority"
copy_file "/home/barberb/HACC/evidence/history/Benjamin Barber vs Julio Cortez protective order.pdf" "$DEST/trust-authority"

# Support notes
copy_file "/home/barberb/HACC/workspace/probate_missing_evidence_staging_sheet_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/probate_primary_source_record_ladder_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/repository_marshal_of_missing_records_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/missing_evidence_master_table_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/proof_gap_matrix_housing_probate_2026-04-09.md" "$DEST/support-notes"

printf 'Built working folder at: %s\n' "$DEST"
find "$DEST" -maxdepth 2 -type f | sort
