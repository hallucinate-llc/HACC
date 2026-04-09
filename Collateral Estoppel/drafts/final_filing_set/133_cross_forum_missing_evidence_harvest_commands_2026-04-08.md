# Cross-Forum Missing Evidence Harvest Commands (2026-04-08)

Use these commands to locate any already-downloaded filing confirmations, docket snapshots, or order entries for the Justice Court and federal tracks.

## 1) Search local workspace for filed/docket indicators

```bash
rg -n -i "26FE0586|docket|register of actions|filed|entered|judgment|dismissed|final order|minute" \
  "/home/barberb/HACC/workspace" \
  "/home/barberb/HACC/Collateral Estoppel" \
  "/home/barberb/HACC/evidence"
```

## 2) Search email-import trees for filing confirmations

```bash
rg -n -i "notice of electronic filing|ecf|cm/ecf|civil action no\.|district of oregon|case no\. 26FE0586|filed" \
  "/home/barberb/HACC/evidence/email_imports" \
  "/home/barberb/HACC/workspace/manual-imap-download-2026-03-31" \
  "/home/barberb/HACC/workspace/manual-imap-download-focused-2026-03-31"
```

## 3) Find likely federal-complaint artifacts by caption terms

```bash
rg -n -i "IN THE UNITED STATES DISTRICT COURT|FOR THE DISTRICT OF OREGON|Housing Authority of Clackamas County and Quantum Residential|Civil Action No\." \
  "/home/barberb/HACC/workspace"
```

## 4) Build a targeted candidate-file list for manual review (litigation folders only)

```bash
find "/home/barberb/HACC/workspace" "/home/barberb/HACC/Collateral Estoppel" "/home/barberb/HACC/evidence" -type f | \
  rg -i "(docket|register|judgment|final order|notice of electronic filing|cm-ecf|26FE0586|district of oregon|civil action no\\.|filed stamp|conformed copy)" > \
  "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/133_candidate_files_for_preclusion_review_2026-04-08.txt"
```

## 5) Manual verification checklist after command run

1. Confirm whether any file shows a real federal case number (not placeholder).
2. Confirm whether any file is filed-stamped or conformed by the court.
3. Confirm whether any order is final/dispositive versus interim.
4. Confirm exact issue text decided for identity-of-issue analysis.
