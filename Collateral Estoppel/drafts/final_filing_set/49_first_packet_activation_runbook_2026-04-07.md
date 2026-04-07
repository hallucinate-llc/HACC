# First Packet Activation Runbook

Generated: 2026-04-07

Use this when your first certified packet arrives and you want immediate strict-mode uplift.

## Recommended first packet

- Nonappearance packet for `f_client_solomon_failed_appearance`
- Expected rule impact: activates `r5` and `r24` once promoted.

## Step 1: Dry-run tracker confirmation

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" \
  --row 2 \
  --file-path "/ABSOLUTE/PATH/TO/CERTIFIED/NONAPPEARANCE/FILE.pdf"
```

## Step 2: Persist tracker confirmation

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" \
  --row 2 \
  --file-path "/ABSOLUTE/PATH/TO/CERTIFIED/NONAPPEARANCE/FILE.pdf" \
  --write
```

## Step 3: Run apply pipeline

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py" \
  --apply \
  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"
```

## Step 4: Verify strict-mode effect

Check:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_promotion_pipeline_status_2026-04-07.md`
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json`

Focus on:
- `fact_override_summary.applied_status_or_value_changes`
- strict count delta from baseline (`active=31 unresolved=6 inactive=4`)
- target rules: `r5`, `r24`
