# Bulk Service Rows Apply Instructions - 2026-04-07

Use this when you have completed `110_bulk_service_fact_intake_one_page_2026-04-07.md`.

## Files

1. Source rows template:
- `111_bulk_service_fact_intake_paste_ready_rows_2026-04-07.csv`

2. Target live log:
- `28_active_service_log_2026-04-07.csv`

## Step-by-step

1. Open file `111_bulk_service_fact_intake_paste_ready_rows_2026-04-07.csv`.
2. Fill each row fields:
- `date_served`
- `service_method`
- `person_served`
- `production_due`
- `notes` (append proof reference)
3. Keep unknown fields blank; do not estimate dates.
4. Replace rows 2-7 in `28_active_service_log_2026-04-07.csv` with the completed rows from file `111`.
5. Confirm status values:
- `served` (if served and waiting)
- `awaiting_production` (if due date set and waiting production)
- `deficiency_notice_stage` (after deficiency notice sent)
- `motion_to_compel_stage` (only after cure deadline lapses)

## Validation quick-check

After update, verify:
1. No recipient remains `ready_to_serve` if `date_served` is filled.
2. `production_due` is present for each served row.
3. `notes` has at least one proof reference token (`tracking`, `receipt`, `affidavit`, `email`, or file path).

## Next file promotions

1. Update `17_certificate_of_service_subpoenas_final.md` per recipient.
2. Update recipient-specific compel pair only when deficiency and cure fields are complete.

