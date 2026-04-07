# Auto-Promotion Hooks Note

The formal reasoning system now has two automatic promotion hooks.

## 1. Certified prior-proceeding materials

The issue-preclusion audit now watches:

`/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`

When that folder gains appropriately named files for:

1. prior order / judgment,
2. docket / register, and
3. hearing / appearance materials,

the issue-preclusion audit will promote the corresponding elements automatically from `missing` or `proof_gated` toward `verified`.

## 2. Subpoena workflow state

The Exhibit R subpoena audit now reads from the active service log in:

[28_active_service_log_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv)

That means:

1. `service_stage_complete` promotes automatically when service is logged;
2. `deficiency_or_compel_stage` promotes automatically when a deficiency or compel stage is logged; and
3. `pre_service_only` stays verified only while the workflow is still in the no-service-yet posture.

## Why this matters

These hooks reduce manual theory maintenance. The logic layer can now respond to new record material and workflow events with less hand-editing and a smaller risk of drift between evidence status and legal modeling.
