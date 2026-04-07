# Certified Records Intake Quickstart

Generated: 2026-04-07

## Immediate use

1. Receive certified file from clerk.
2. Save it in:
   - `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`
3. Update matching row in:
   - `45_certified_records_intake_tracker_template_2026-04-07.csv`

## Required row edits when file is confirmed

1. Replace `unknown` filename/date fields as needed.
2. Set `is_certified` from `no` to `yes`.
3. Set `party_identity_matched` from `no` to `yes` after caption/name check.
4. Confirm `absolute_path` and `target_fact_ids` are correct.

## Run after each intake update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_certified_intake_override_suggestions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
```

## Expected behavior

- Suggestion file moves from warnings to actionable override rows:
  - `knowledge_graph/generated/certified_intake_override_suggestions_2026-04-07.md`
- Once you apply those suggestions into `evidence_fact_overrides_2026-04-07.csv`, strict-mode blockers can clear on recompute.
