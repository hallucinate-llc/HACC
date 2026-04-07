# Unresolved Fact Promotion Decision Matrix - 2026-04-07

## Scope

This matrix governs whether unresolved strict-mode fact predicates may be promoted to `verified`.

Inputs used:
- `deontic_reasoning_report.json`
- `unresolved_fact_evidence_scan_2026-04-07.md`
- `evidence_notes/certified_records/` current contents

## Promotion rule

A fact may be promoted to `verified` only if source material is both:
1. specific to the predicate; and
2. filing-grade reliable (certified court record, authenticated return, or equivalent official record).

Repository drafts, memos, and generated artifacts are support context, not final proof by themselves.

## Decisions by unresolved fact

1. `f_client_prior_appointment`
- Current status: `alleged`
- Current evidence class: draft/memo-level references to possible prior appointment.
- Required proof to promote: certified appointment/authority order + docket/register showing effective status.
- Decision: `DO NOT PROMOTE`

2. `f_client_benjamin_housing_interference`
- Current status: `alleged`
- Current evidence class: allegation and inference narratives, plus subpoena discovery targets.
- Required proof to promote: authenticated/certified records tying specific interfering acts by Benjamin to housing-contract process.
- Decision: `DO NOT PROMOTE`

3. `f_client_benjamin_order_disregard`
- Current status: `alleged`
- Current evidence class: allegation-level assertions and proof-target placeholders.
- Required proof to promote: certified order + service/notice + noncompliance record tied to Benjamin.
- Decision: `DO NOT PROMOTE`

4. `f_client_solomon_failed_appearance`
- Current status: `alleged`
- Current evidence class: checklist and motion references, but no staged certified nonappearance minute/register file.
- Required proof to promote: certified register/minute nonappearance entry + service/order-to-appear record.
- Decision: `DO NOT PROMOTE`

5. `f_collateral_estoppel_candidate`
- Current status: `theory`
- Current evidence class: doctrine and mapping framework present; element proof remains incomplete.
- Required proof to promote: certified prior final order/judgment + issue identity + privity + full/fair opportunity mapping.
- Decision: `DO NOT PROMOTE`

6. `f_client_solomon_barred_refile`
- Current status: `alleged`
- Current evidence class: pleading theory and packet/checklist references only.
- Required proof to promote: certified prior final record + current refile pleading + mapped element chart.
- Decision: `DO NOT PROMOTE`

## Immediate next best actions

1. Keep current statuses unchanged in `evidence_fact_overrides_2026-04-07.csv`.
2. Continue certified record intake using packets:
- `41_certified_nonappearance_packet_checklist_r24_2026-04-07.md`
- `42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md`
- `52_prior_appointment_certified_packet_checklist_r1_r2_r3_2026-04-07.md`
3. Re-run formal generators immediately after any certified packet arrival.

