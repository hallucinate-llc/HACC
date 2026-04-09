# Deontic System Gap Refresh

Generated: 2026-04-09

## Counts
- Strict: active=42 unresolved=6 inactive=4
- Inclusive: active=43 unresolved=5 inactive=4

## Law/Caselaw Grounding
- Rules without authority refs: 0
- Local-rule authority objects present: True
- Local-rule workflow rule present: True

## Remaining Evidence-Gated Gaps
- Strict unresolved rules still blocked by allegation/theory predicates or unverified facts:
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

- Strict inactive workflow rules still blocked by false antecedents:
- r17_responding_custodian_obligated_execute_or_query_protocol_upon_service (workflow)
- antecedent f_subpoena_service_completed_any status=verified value=false
- r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response (workflow)
- antecedent f_subpoena_response_incomplete_any status=verified value=false
- r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage (workflow)
- antecedent f_deficiency_notice_sent_any status=verified value=false
- r22_case_obligated_finalize_authority_citations_before_filing (filing)
- antecedent f_authority_table_placeholders_unresolved status=verified value=false

## Priority Closure Targets
- certified_nonappearance_packet_for_f_client_solomon_failed_appearance
- certified_issue_preclusion_packet_for_f_collateral_estoppel_candidate_and_f_client_solomon_barred_refile
- certified_prior_appointment_order_for_f_client_prior_appointment
- active_service_log_updates_to_activate_r17_r18_r19
