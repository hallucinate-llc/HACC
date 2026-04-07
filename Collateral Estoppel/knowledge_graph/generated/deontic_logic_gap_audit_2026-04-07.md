# Deontic Logic Gap Audit - 2026-04-07

Scope audited:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py`
- generated artifacts in `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated`
- subpoena workflow files in `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set`

## Findings (ordered by impact)

1. High - Actor attribution conflict remains unresolved in the legal-theory layer.
   - Signal: `r21_case_obligated_resolve_actor_assignment_conflict` is active.
   - Closure evidence needed: source-grounded timeline assigning each alleged act to the correct actor (Solomon vs Benjamin).

2. High - Subpoena enforcement chain remains inactive pending real service lifecycle events.
   - Inactive rules: `r17`, `r18`, `r19`.
   - Activation path: update `28_active_service_log_2026-04-07.csv` with confirmed service/deficiency dates and regenerate.

3. Medium - Collateral-estoppel prohibition remains proof-gated.
   - Unresolved rule: `r7_solomon_forbidden_refile_precluded_issue`.
   - Closure evidence needed: certified prior final judgment/order, identity-of-issue proof, full/fair opportunity record.

4. Medium - Hypothesis-track rules remain unresolved in inclusive mode by design policy.
   - Inclusive unresolved: `r1`, `r2`, `r3`, `r5`, `r7`.
   - Additional strict-only unresolved: `r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved`.

5. Medium - Remaining authority-ref gaps are limited to hypothesis-track rules only.
   - See `deontic_end_to_end_grounding_gap_report_2026-04-07.md`.
   - Non-hypothesis rules missing explicit `authority_refs`: none (closed in this pass).


6. Low - No active O/P/F modality contradictions are currently present.
   - Source: `deontic_conflict_report_2026-04-07.md`.
   - strict: F/P=0, F/O=0, O/P=0; inclusive: F/P=0, F/O=0, O/P=0.

## Current mode snapshot

From `deontic_reasoning_report.json` generated 2026-04-07:
- strict: active=30, unresolved=6, inactive=4
- inclusive: active=31, unresolved=5, inactive=4

## Completed in this pass

- Added `r33_case_permitted_request_special_advocate_or_gal_under_chapter_125` grounded to `auth:ors_125_120`.
- Eliminated unused-authority gap for ORS 125.120.
- Added formal end-to-end grounding diagnostics:
  - `deontic_end_to_end_grounding_gap_report_2026-04-07.md`
  - `deontic_end_to_end_grounding_gap_report_2026-04-07.json`

## Recommended next closure steps

1. Enter first confirmed service event to activate `r17`.
2. Add certified nonappearance record to close `r24` and support show-cause path.
3. Add certified prior-final-order and issue-identity proof to close `r7`.
