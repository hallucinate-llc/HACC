# Certified Records Filename Convention

Generated: 2026-04-07

## Goal

Standardize certified file names so intake is human-auditable and machine-detectable.

## Directory

- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`

## Required filename format

`<bucket>__<case>__<yyyymmdd_or_unknown>__<short_desc>.pdf`

Examples:
- `prior_order__26PR00641__20260409__signed_order_guardianship.pdf`
- `docket__26PR00641__20260409__register_of_actions.pdf`
- `hearing__26PR00641__20260409__appearance_minutes.pdf`
- `appointment__26PR00641__20260409__letters_of_guardianship.pdf`
- `service__26PR00641__20260409__proof_of_service.pdf`

## Bucket values (use exactly)

1. `prior_order`
2. `docket`
3. `hearing`
4. `appointment`
5. `service`
6. `enforcement`
7. `other_certified`

## Mapping to deontic fact targets

- `prior_order` + `docket` + `hearing`
  - unlocks issue-preclusion record completeness checks (`r7` path support)
- `hearing` (nonappearance minute/entry)
  - supports `f_client_solomon_failed_appearance`
- `appointment`
  - supports `f_client_prior_appointment`
- `service` / `enforcement`
  - supports service/evasion/disregard fact promotion when record contents match

## Intake quality checks

1. Verify file stamp/seal indicates certified copy.
2. Verify case number and caption match the target proceeding.
3. Verify date legibility.
4. Verify named party identity alignment.
5. Record each file in the intake tracker CSV.

## Notes

- If date unknown, use `unknown` in the date slot.
- If document is multi-case, include primary case and note secondary case in tracker notes.
