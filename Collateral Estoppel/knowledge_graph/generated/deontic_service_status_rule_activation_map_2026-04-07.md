# Deontic Service Status -> Rule Activation Map (2026-04-07)

This map describes how updates to `28_active_service_log_2026-04-07.csv` are promoted into facts and then activate subpoena-enforcement deontic rules.

## Source file parsed

- `Collateral Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv`

## Key derived facts

1. `f_subpoena_service_completed_any`
   - True if any row has status in:
     - `served`, `awaiting_production`, `production_received`, `deficiency_notice_stage`, `motion_to_compel_stage`
   - Or if any row has non-empty `date_served` (YYYY-MM-DD recognized).

2. `f_subpoena_response_incomplete_any`
   - True if any row has status in:
     - `awaiting_production`, `deficiency_notice_stage`, `motion_to_compel_stage`
   - Or if row has `date_served` and either:
     - `checklist_received` is empty/No/False, or
     - `search_report_received` is empty/No/False.

3. `f_deficiency_notice_sent_any`
   - True if any row has status `deficiency_notice_stage` or `motion_to_compel_stage`,
   - Or non-empty `deficiency_notice_sent` date.

4. `f_motion_to_compel_stage_any`
   - True if any row has status `motion_to_compel_stage`,
   - Or non-empty `motion_to_compel_filed` date.

## Rule activation gates

1. `r17_responding_custodian_obligated_execute_or_query_protocol_upon_service`
   - Requires: `f_subpoena_service_completed_any` + `f_or_joined_search_protocol_defined`
   - Practical trigger: mark any recipient as served (status/date_served).

2. `r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response`
   - Requires: `f_subpoena_response_incomplete_any` + `f_subpoena_workflow_components_staged`
   - Practical trigger: served recipient with missing checklist/search report, or explicit incomplete status.

3. `r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage`
   - Requires: `f_deficiency_notice_sent_any` + `f_subpoena_workflow_components_staged`
   - Practical trigger: set deficiency status or fill `deficiency_notice_sent`.

## Minimal operator workflow

1. Update service row status/date after each service event.
2. Update checklist/search report columns when production arrives.
3. Set deficiency fields if cure needed.
4. Re-run generator:
   - `python3 Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py`
5. Confirm activation changes in:
   - `knowledge_graph/generated/deontic_reasoning_report.json`

