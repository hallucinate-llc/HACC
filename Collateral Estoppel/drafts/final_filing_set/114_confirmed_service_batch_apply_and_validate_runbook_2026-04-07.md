# Confirmed Service Batch Apply And Validate Runbook - 2026-04-07

Case: `26PR00641`

This runbook applies confirmed service facts into the live service log and validates deontic activation outputs.

## Input file

- `113_confirmed_service_updates_batch_prefill_2026-04-07.csv`

Required columns:
- `recipient`
- `date_served` (`YYYY-MM-DD`)
- `service_method`
- `person_served`
- `production_due` (`YYYY-MM-DD`)
- `status` (`served` / `awaiting_production` / `production_received` / `deficiency_notice_stage` / `motion_to_compel_stage`)
- `notes_append`

## Step 1: Fill confirmed facts only

Fill each recipient row in `113` using true service facts only.
Do not estimate dates.

## Step 2: Apply updates

Run:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_confirmed_service_updates_batch.py" \
  --input-csv "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/113_confirmed_service_updates_batch_prefill_2026-04-07.csv" \
  --acknowledge "I CONFIRM THESE SERVICE FACTS ARE TRUE"
```

Expected:
- backup file created in `drafts/final_filing_set`
- `28_active_service_log_2026-04-07.csv` updated

## Step 3: Validate and emit derived outputs

Run:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
```

Review outputs:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/service_log_validation_report_2026-04-07.md`
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/service_log_validation_report_2026-04-07.json`

## Step 4: Promote filing artifacts

After validation:
1. Update `17_certificate_of_service_subpoenas_final.md` with the same per-recipient method/date/proof references.
2. If a recipient is overdue and incomplete, move corresponding compel pair from prefill toward filing-ready.

## Stop conditions (do not promote compel yet)

Do not promote compel packet if any of these are missing for target recipient:
1. `date_served`
2. `production_due`
3. service proof reference
4. deficiency notice + cure chronology (when required)

