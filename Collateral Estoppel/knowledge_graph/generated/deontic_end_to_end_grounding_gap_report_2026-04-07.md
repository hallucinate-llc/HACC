# Deontic End-to-End Grounding Gap Report - 2026-04-07

## Summary
- Strict: active=42 unresolved=6 inactive=4
- Inclusive: active=43 unresolved=5 inactive=4
- Rules total: 52
- Authority facts: 19
- Authority refs used by rules: 22

## Authority Linkage Gaps
- Missing authority-fact links: 2
- Rules without authority refs: 0
- Non-hypothesis rules without authority refs: 0
- Unused authority facts: 0

## Strict Unresolved Rules (Proof Gated)
- r1_guardian_permission_if_prior_appointment (hypothesis)
- antecedent f_client_prior_appointment status=alleged value=true
- r2_target_noninterference_prohibition_if_prior_appointment (hypothesis)
- antecedent f_client_prior_appointment status=alleged value=true
- antecedent f_client_solomon_housing_interference status=alleged value=true
- r3_target_obligation_comply_or_seek_relief_if_prior_appointment (hypothesis)
- antecedent f_client_prior_appointment status=alleged value=true
- antecedent f_client_solomon_order_disregard status=alleged value=true
- r5_solomon_obligated_appear_and_answer (hypothesis)
- antecedent f_client_solomon_failed_appearance status=alleged value=true
- r7_solomon_forbidden_refile_precluded_issue (hypothesis)
- antecedent f_collateral_estoppel_candidate status=theory value=true
- antecedent f_client_solomon_barred_refile status=alleged value=true
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved (filing)
- antecedent f_client_solomon_failed_appearance status=alleged value=true

## Strict Inactive Rules (Antecedent False)
- r17_responding_custodian_obligated_execute_or_query_protocol_upon_service (workflow)
- antecedent f_subpoena_service_completed_any status=verified value=false
- r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response (workflow)
- antecedent f_subpoena_response_incomplete_any status=verified value=false
- r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage (workflow)
- antecedent f_deficiency_notice_sent_any status=verified value=false
- r22_case_obligated_finalize_authority_citations_before_filing (filing)
- antecedent f_authority_table_placeholders_unresolved status=verified value=false

## Strict Active Dependency Exposure
- No strict-active rules depend on alleged/theory/client_assertion antecedents.

## Recommended Closure Actions
- Convert strict unresolved allegation/theory antecedents to verified with certified docket/order/service records.
- Activate workflow rules r17-r19 by entering confirmed service/deficiency events in the active service log.
- Keep strict-active set free of client_assertion/theory antecedents before filing-grade reliance.
