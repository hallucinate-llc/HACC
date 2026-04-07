# Certified Promotion Gap Memo

Generated: 2026-04-07

## Current promotion outcome

- Override rows processed: 7
- Status/value promotions: 0
- Source/date trace upgrades: 7
- Strict rule counts remain: active 30, unresolved 6, inactive 4

## Why no verified promotions happened

The certified-records staging folder currently contains only guidance and empty mapping templates:
- `issue_preclusion_mapping.json` (all mapping booleans false)
- `orcp17_filing_mapping.json` (all mapping booleans false)
- no certified prior order/judgment file
- no certified docket/register file
- no certified hearing/appearance/minute file

## Promotion blockers by fact

- `f_client_solomon_failed_appearance`
  - Needed: certified hearing register/minute order proving Solomon nonappearance.

- `f_client_solomon_barred_refile`
- `f_collateral_estoppel_candidate`
  - Needed: certified prior proceeding packet and completed issue-preclusion mapping with element booleans set true where supported.

- `f_client_prior_appointment`
  - Needed: certified prior appointment/authority order naming Benjamin.

- `f_client_benjamin_avoided_service`
- `f_client_benjamin_order_disregard`
  - Needed: certified service/appearance/noncompliance records linked to the relevant order/proceeding.

- `f_client_benjamin_housing_interference`
  - Needed: documentary chain identifying actor-to-HACC communications and causal tie to lease/contract impact.

## Immediate next intake targets

1. Drop certified prior-order, docket/register, and hearing/appearance files into `evidence_notes/certified_records` using filename markers in that folder's `README.md`.
2. Complete `issue_preclusion_mapping.json` once certified materials are staged.
3. Update `evidence_fact_overrides_2026-04-07.csv` rows with `override_status=verified` only for facts actually proven by those records.
