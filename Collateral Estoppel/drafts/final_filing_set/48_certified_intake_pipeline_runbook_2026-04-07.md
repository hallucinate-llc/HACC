# Certified Intake Pipeline Runbook

Generated: 2026-04-07

## Standard run (no apply)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py"
```

Use this to validate tracker rows and recompute reports without modifying override CSV.

## Apply run (after certified confirmation)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py" \
  --apply \
  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"
```

Use this only when tracker rows are confirmed certified and identity-matched.

## Outputs to inspect

1. `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_promotion_pipeline_status_2026-04-07.md`
2. `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_tracker_validation_2026-04-07.md`
3. `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_override_suggestions_2026-04-07.md`
4. `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json`

## Success indicators

- pipeline `Success: True`
- suggestion warnings reduced to expected residuals
- `fact_override_summary.applied_status_or_value_changes` increases after apply run
- strict unresolved count decreases when promoted facts unlock rules
