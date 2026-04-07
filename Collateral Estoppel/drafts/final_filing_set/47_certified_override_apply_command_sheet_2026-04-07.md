# Certified Override Apply Command Sheet

Generated: 2026-04-07

## 1) Generate suggestions from intake tracker

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_certified_intake_tracker.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_certified_intake_override_suggestions.py"
```

Review:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_tracker_validation_2026-04-07.md`
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_override_suggestions_2026-04-07.md`

## 2) Apply suggestions into override CSV (safe apply)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_certified_intake_override_suggestions.py" \
  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"
```

Safety behavior:
- creates backup of `evidence_fact_overrides_2026-04-07.csv`
- upserts by `fact_id`
- no-op if no suggestions exist

## 3) Recompute formal outputs

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## 4) Check promotion effect

Inspect:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json`

Focus fields:
- `fact_override_summary.applied_status_or_value_changes`
- strict `active_rules` / `unresolved_rules` / `inactive_rules`
