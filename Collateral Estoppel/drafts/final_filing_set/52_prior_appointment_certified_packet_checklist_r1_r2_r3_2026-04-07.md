# Prior Appointment Certified Packet Checklist (r1/r2/r3) - 2026-04-07

Target rules:
- `r1_guardian_permission_if_prior_appointment`
- `r2_target_noninterference_prohibition_if_prior_appointment`
- `r3_target_obligation_comply_or_seek_relief_if_prior_appointment`

Goal:
- Convert the prior-appointment cluster facts to verified so strict mode can activate the related permission/prohibition/obligation rules.

## Required Certified Components

1. Certified appointment or authority order naming Benjamin Barber (if such order exists).
2. Certified register/docket entry showing effective date and current status of the appointment/authority.
3. Certified or authenticated records supporting housing-contract interference conduct tied to Solomon Barber (as alleged target actor in this branch).
4. Certified or authenticated records supporting order noncompliance/disregard tied to the same authority context and actor.

## Evidence Integrity Checks

1. Case number and party identity match (`26PR00641` unless linked case relation is documented).
2. Appointment record is final/effective for the relevant period.
3. Interference record has clear actor/date/action linkage.
4. Noncompliance record links to the same order or authority source.

## Logic Ingestion Targets

- Facts to verify:
  - `f_client_prior_appointment`
  - `f_client_solomon_housing_interference`
  - `f_client_solomon_order_disregard`
- Rules expected to change:
  - `r1`: unresolved -> active (strict)
  - `r2`: unresolved -> active (strict)
  - `r3`: unresolved -> active (strict)

## Post-Ingestion Recompute

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Verification Query

```bash
jq '.modes.strict.unresolved_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```

Expected result:
- `r1_guardian_permission_if_prior_appointment` no longer listed as unresolved.
- `r2_target_noninterference_prohibition_if_prior_appointment` no longer listed as unresolved.
- `r3_target_obligation_comply_or_seek_relief_if_prior_appointment` no longer listed as unresolved.
