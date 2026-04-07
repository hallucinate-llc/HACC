# Service Update Pipeline Quick Run - 2026-04-07

Use this after filling `113_confirmed_service_updates_batch_prefill_2026-04-07.csv`.

## Run commands

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_confirmed_service_updates_batch.py" \
  --input-csv "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/113_confirmed_service_updates_batch_prefill_2026-04-07.csv" \
  --acknowledge "I CONFIRM THESE SERVICE FACTS ARE TRUE"

python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
```

## Then update

1. `115_recipient_compel_promotion_gate_matrix_2026-04-07.csv`
- flip `service_completed`, `production_due_set`, and `proof_ref_present` to `yes` where true.

2. `17_certificate_of_service_subpoenas_final.md`
- copy exact date/method/proof for each served recipient.

3. Promote any recipient compel pair only if `eligible_for_compel_packet=yes`.

## Promotion rule (simple)

Set `eligible_for_compel_packet=yes` only when all are `yes`:
1. `service_completed`
2. `production_due_set`
3. `proof_ref_present`
4. `response_incomplete`
5. and (if deficiency track used) `deficiency_notice_sent` + `cure_deadline_set`

