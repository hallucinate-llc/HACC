# Evidence Fact Override Prefill Memo

Generated: 2026-04-07

This memo documents conservative prefill choices for `evidence_fact_overrides_2026-04-07.csv`.
The prefill updates source/date anchors only. It does not automatically upgrade allegation/theory facts to `verified`.

## Rows Prefilled

- `f_client_solomon_failed_appearance`
  - Source anchor: `drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md`
  - Gate to verified: certified hearing register/minute order and identity tie-in.

- `f_client_solomon_barred_refile`
  - Source anchor: `drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md`
  - Gate to verified: certified prior proceeding packet + mapped issue-preclusion elements.

- `f_collateral_estoppel_candidate`
  - Source anchor: `evidence_notes/certified_records/issue_preclusion_mapping_guide.md`
  - Gate to verified: fully completed `issue_preclusion_mapping.json` backed by certified records.

- `f_client_prior_appointment`
  - Source anchor: `knowledge_graph/guardianship_case_graph.md`
  - Gate to verified: certified appointment order naming Benjamin.

- `f_client_benjamin_avoided_service`
- `f_client_benjamin_order_disregard`
  - Source anchor: `knowledge_graph/guardianship_case_graph.md`
  - Gate to verified: certified service/appearance/noncompliance records.

- `f_client_benjamin_housing_interference`
  - Source anchor: `evidence_notes/motion_exhibit_index.md` (Exhibits I-M branch)
  - Gate to verified: documentary chain identifying actor-to-HACC communication and causal tie to lease/contract impact.

## Why this prefill is conservative

- It improves traceability immediately (each blocker fact now has a concrete local source anchor).
- It preserves proof discipline (status remains allegation/theory unless certification-level evidence exists).
- It keeps strict-mode outputs honest while still preparing quick promotion once records arrive.
