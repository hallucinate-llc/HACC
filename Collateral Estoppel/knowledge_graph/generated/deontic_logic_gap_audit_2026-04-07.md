# Deontic Logic Gap Audit - 2026-04-07

Scope audited:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py`
- generated artifacts in `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated`
- subpoena workflow files in `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set`

## Findings (ordered by impact)

1. High - Actor attribution conflict remains unresolved in the legal-theory layer.
   - Signal: `r21_case_obligated_resolve_actor_assignment_conflict` is active.
   - Closure evidence needed: source-grounded timeline assigning each alleged act to the correct actor (Solomon vs Benjamin).

2. High - Authority table placeholder finalization still remains open.
   - Signal: `r22_case_obligated_finalize_authority_citations_before_filing` is active.
   - Closure evidence needed: finalized ORS/ORCP/case-citation table replacing placeholder tokens.

3. High - Subpoena enforcement chain is staged but currently inactive pending service events.
   - Inactive rules: `r17`, `r18`, `r19`.
   - Activation path: update `28_active_service_log_2026-04-07.csv` status/date fields (service, deficiency notice, cure, compel) and regenerate.

4. Medium - Collateral-estoppel prohibition remains unresolved in both strict and inclusive modes.
   - Unresolved rule: `r7_solomon_forbidden_refile_precluded_issue`.
   - Closure evidence needed: certified prior final judgment/order, identity-of-issue proof, and full/fair opportunity record.

5. Medium - Hypothesis-track rules remain unresolved in inclusive mode by design policy.
   - Inclusive unresolved: `r1`, `r2`, `r3`, `r5`, `r7`.
   - Additional strict-only unresolved: `r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved`.

## Current mode snapshot

From `deontic_reasoning_report.json` generated 2026-04-07:
- strict: active=30, unresolved=6, inactive=3
- inclusive: active=31, unresolved=5, inactive=3

## Rule-set classification fix completed in this pass

- Non-active rules are split into:
  - `unresolved_rules` (antecedents true, but mode proof-status gating not met), and
  - `inactive_rules` (one or more antecedents false).

## New output

- `proof_intake_map_2026-04-07.{md,json}` now maps each unresolved/inactive rule to antecedent-level closure actions.
