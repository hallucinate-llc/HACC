#!/usr/bin/env bash
set -euo pipefail

DEST="/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09"

mkdir -p "$DEST/routing"
mkdir -p "$DEST/portability"
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

# Routing / deficiency packet
copy_file "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml" "$DEST/routing"
copy_file "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.json" "$DEST/routing"
copy_file "/home/barberb/HACC/evidence/history/Quantum application.pdf" "$DEST/routing"
copy_file "/home/barberb/HACC/evidence/history/Quantum application filled.pdf" "$DEST/routing"
copy_file "/home/barberb/HACC/evidence/history/Quantum Pet Amendment.pdf" "$DEST/routing"
copy_file "/home/barberb/HACC/evidence/history/Quantum Pet Amendment filled.pdf" "$DEST/routing"
copy_file "/home/barberb/HACC/evidence/history/Application 3-29-2026 Parkside Heights.pdf" "$DEST/routing"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-1.pdf.txt" "$DEST/routing"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-2.pdf.txt" "$DEST/routing"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-3.pdf.txt" "$DEST/routing"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-4.pdf.txt" "$DEST/routing"

# Portability / Waterleaf packet
copy_file "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml" "$DEST/portability"
copy_file "/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0006-RE-Allegations-of-Fraud---JC-Household-34ac4fce79eb42d1872ad12efa21dcdb-clackamas.us/attachments/Port-Out-Request-Form.pdf" "$DEST/portability"
copy_file "/home/barberb/HACC/evidence/history/waterleaf_application.png" "$DEST/portability"
copy_file "/home/barberb/HACC/workspace/exhibit-binder-court-ready/exhibits/Exhibit_W_waterleaf_application.png" "$DEST/portability"
copy_file "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_1.eml" "$DEST/portability"
copy_file "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_3.eml" "$DEST/portability"
copy_file "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-18_additional-info_bwilliams_1.eml" "$DEST/portability"

# Support notes
copy_file "/home/barberb/HACC/workspace/hacc_routing_deficiency_exhibit_shortlist_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/workspace/mailbox_portability_exhibit_shortlist_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/workspace/housing_missing_evidence_staging_sheet_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/housing_primary_source_record_ladder_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/household_submission_and_participation_chronology_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/repository_marshal_of_missing_records_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/missing_evidence_master_table_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/Collateral Estoppel/evidence_notes/imap_mailbox_portability_evidence_note_2026-04-09.md" "$DEST/support-notes"
copy_file "/home/barberb/HACC/workspace/housing_missing_evidence_folder_build_commands_2026-04-09.md" "$DEST/support-notes"

printf 'Built working folder at: %s\n' "$DEST"
find "$DEST" -maxdepth 2 -type f | sort
