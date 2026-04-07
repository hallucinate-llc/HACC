# Certification Packet Manifest Runbook

Generated: 2026-04-07

## Source manifest

- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certification_packet_manifests_2026-04-07.md`

## Use sequence

1. Choose packet lane:
   - `packet_nonappearance_r24`
   - `packet_issue_preclusion_r7`
   - `packet_prior_appointment_r1_r2_r3`
2. Collect documents matching required record types.
3. Save documents using suggested filename patterns in `evidence_notes/certified_records`.
4. Update matching tracker row in:
   - `45_certified_records_intake_tracker_template_2026-04-07.csv`
5. Confirm row with:
   - `confirm_certified_intake_row.py`
6. Run:
   - `run_certified_intake_promotion_pipeline.py --apply ...`

## Fast-start recommendation

Start with `packet_nonappearance_r24` first for highest immediate strict-mode lift (`r5` + `r24`).
