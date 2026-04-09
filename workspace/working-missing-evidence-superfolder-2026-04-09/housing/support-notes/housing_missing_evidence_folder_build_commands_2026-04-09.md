# Housing Missing Evidence Folder Build Commands

Use these commands to build a working folder from the strongest repository-side housing missing-evidence records.

They assume you want a folder at:

`/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09`

## 1. Create The Folder Structure

```bash
mkdir -p /home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing
mkdir -p /home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability
mkdir -p /home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes
```

## 2. Copy Routing / Deficiency Packet

```bash
cp "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.json" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/evidence/history/Quantum application.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/evidence/history/Quantum application filled.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/evidence/history/Quantum Pet Amendment.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/evidence/history/Quantum Pet Amendment filled.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/evidence/history/Application 3-29-2026 Parkside Heights.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-1.pdf.txt" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-2.pdf.txt" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-3.pdf.txt" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/attachment_pdf_text_scan_2026-04-07/cortez-4.pdf.txt" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/routing/"
```

## 3. Copy Portability / Waterleaf Packet

```bash
cp "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0006-RE-Allegations-of-Fraud---JC-Household-34ac4fce79eb42d1872ad12efa21dcdb-clackamas.us/attachments/Port-Out-Request-Form.pdf" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/evidence/history/waterleaf_application.png" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/workspace/exhibit-binder-court-ready/exhibits/Exhibit_W_waterleaf_application.png" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_1.eml" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-17_additional-info_bwilliams_3.eml" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
cp "/home/barberb/HACC/workspace/imap-confirmed-messages/2026-03-18_additional-info_bwilliams_1.eml" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/portability/"
```

## 4. Copy Support Notes

```bash
cp "/home/barberb/HACC/workspace/hacc_routing_deficiency_exhibit_shortlist_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/workspace/mailbox_portability_exhibit_shortlist_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/workspace/housing_missing_evidence_staging_sheet_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/housing_primary_source_record_ladder_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/household_submission_and_participation_chronology_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/repository_marshal_of_missing_records_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/missing_evidence_master_table_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
cp "/home/barberb/HACC/Collateral Estoppel/evidence_notes/imap_mailbox_portability_evidence_note_2026-04-09.md" "/home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09/support-notes/"
```

## 5. Verify Folder Contents

```bash
find /home/barberb/HACC/workspace/working-housing-missing-evidence-2026-04-09 -maxdepth 2 -type f | sort
```

## Practical Use

Use this folder for:

- a compact missing-evidence working packet
- rapid exhibit pulling
- preparing a print folder without mixing in the full case repository
