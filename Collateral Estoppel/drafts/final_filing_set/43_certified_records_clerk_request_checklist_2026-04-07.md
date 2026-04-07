# Certified Records Clerk Request Checklist (Case Support)

Generated: 2026-04-07
Working target case: `26PR00641` (confirm from certified docket before filing)

## Purpose

This checklist is for requesting certified records needed to promote key proof-gated facts from `alleged/theory` to `verified` in the formal deontic layer.

## Request packet header (fill before use)

1. Requestor name: ________________________________
2. Requestor contact: ______________________________
3. Court: Clackamas County Circuit Court
4. Department/division: ____________________________
5. Case number(s): ________________________________
6. Date requested: ________________________________
7. Delivery method requested (paper/email/portal): __________________

## Certified document set A: prior-proceeding record (issue preclusion)

Request certified copies of:
1. Prior signed order/judgment (or equivalent final appealable order).
2. Register of actions / docket sheet for the prior proceeding.
3. Hearing minutes, appearance register, or transcript showing participation/opportunity.

Primary logic targets:
- `f_collateral_estoppel_candidate`
- `f_client_solomon_barred_refile`

## Certified document set B: nonappearance/appearance record

Request certified copies of:
1. Register/minutes entry identifying hearing date and nonappearance (if any).
2. Order-to-appear, notice, or hearing setting tied to the same date.
3. Identity tie-in showing the entry pertains to Solomon Barber.

Primary logic target:
- `f_client_solomon_failed_appearance`

## Certified document set C: prior appointment/authority record

Request certified copies of:
1. Appointment order or fiduciary authority order naming Benjamin Barber (if it exists).
2. Any letters of guardianship/conservatorship or equivalent authority instrument.
3. Docket entry showing effective date and status.

Primary logic target:
- `f_client_prior_appointment`

## Optional set D: service / enforceability / noncompliance tie-ins

Request certified copies of:
1. Proof/service return records.
2. Appearance and notice records.
3. Any court-entered noncompliance or enforcement findings.

Primary logic targets:
- `f_client_benjamin_avoided_service`
- `f_client_benjamin_order_disregard`

## Intake and naming requirements for automation

1. Save received files into:
   - `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`
2. Use filename markers documented in:
   - `44_certified_records_filename_convention_2026-04-07.md`
3. Log each received file in:
   - `45_certified_records_intake_tracker_template_2026-04-07.csv`

## Post-intake run sequence

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Promotion safety rule

Do not set `override_status=verified` in `evidence_fact_overrides_2026-04-07.csv` unless the certified file path is entered and date-linked for that specific fact.
