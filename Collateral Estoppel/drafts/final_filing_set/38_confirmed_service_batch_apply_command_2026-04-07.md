# Confirmed Service Batch Apply Command - 2026-04-07

1. Fill this file with only confirmed service facts:
- `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/37_confirmed_service_batch_update_template_2026-04-07.csv`

2. Apply batch updates:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_confirmed_service_updates_batch.py" \
  --input-csv "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/37_confirmed_service_batch_update_template_2026-04-07.csv" \
  --acknowledge "I CONFIRM THESE SERVICE FACTS ARE TRUE"
```

3. Recompute:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

4. Verify workflow activation:

```bash
jq '.modes.strict.inactive_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```
