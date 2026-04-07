# Fact Override Promotion Runbook

Use this file when certified records arrive and you want to promote facts from allegation/theory to verified in a controlled way.

## File to edit

- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/evidence_fact_overrides_2026-04-07.csv`

## Promotion pattern

For a target row, set:
- `override_status=verified`
- `override_value=true` (or `false` if certified evidence disproves the fact)
- `override_source=<absolute path to certified record or certified packet file>`
- `override_date=<YYYY-MM-DD>`

## Example edits

- `f_client_solomon_failed_appearance`
  - status: `verified`
  - value: `true`
  - source: certified hearing register/minute order path
  - date: hearing record date

- `f_client_solomon_barred_refile`
- `f_collateral_estoppel_candidate`
  - status: `verified`
  - value: `true`
  - source: certified prior proceeding packet + completed mapping artifacts
  - date: date mapping completed or certified filing date

## Recompute

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Verify

- Check `generated/deontic_reasoning_report.json`:
  - `fact_override_summary.applied_count` increments.
- Confirm target strict blocker rule is no longer unresolved/inactive where expected.
