# Certified Intake Missing-File Repair - 2026-04-07

## Current blocker

The certified intake tracker is populated, but all three tracked source files are missing from disk, so no fact promotion can occur.

Validation source:
- `generated/certified_intake_tracker_validation_2026-04-07.md`

## Missing files

1. `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/hearing__26PR00641__unknown__nonappearance_minutes.pdf`
2. `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/prior_order__26PR00641__unknown__prior_final_order.pdf`
3. `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/appointment__26PR00641__unknown__appointment_order_benjamin_barber.pdf`

## Operational consequence

- `rows_marked_certified = 0`
- `rows_candidate_promotable = 0`
- strict unresolved set remains unchanged (`r1 r2 r3 r5 r7 r24`)

## Repair steps

1. Place the actual certified files at the exact paths above, or update tracker paths to exact received filenames.
2. Mark tracker fields `is_certified=yes` and `identity_match=yes` only after document review.
3. Re-run:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_certified_intake_tracker.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_certified_intake_override_suggestions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_certified_intake_override_suggestions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
```

## Expected first promotions

- Nonappearance packet should target `f_client_solomon_failed_appearance`.
- Prior-order packet should target issue-preclusion mapping and `f_collateral_estoppel_candidate`/`f_client_solomon_barred_refile` once element mapping is complete.
- Appointment packet should target `f_client_prior_appointment` and then `r1/r2/r3` closure prerequisites.

