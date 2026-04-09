# Deontic Closure Workplan - 2026-04-07

## Summary
- Strict active: 42
- Strict unresolved: 6
- Strict inactive: 4
- Closure items: 10

## Execution Sequence
- 1) Confirm and log first subpoena service event to activate r17.
- 2) Monitor due dates and log true incomplete-response trigger to activate r18.
- 3) Issue and log deficiency notice to activate r19 when criteria are met.
- 4) Assemble certified nonappearance packet for r24.
- 5) Assemble certified issue-preclusion packet for r7.
- 6) Convert remaining hypothesis-track antecedents from alleged/theory to verified as records are obtained.

## Prioritized Rule Closure Items
### Priority: high
- [inactive] r17_responding_custodian_obligated_execute_or_query_protocol_upon_service (workflow)
- Action: Log first confirmed service event in active service log (status/date/method/person served/production due).
- Expected effect: r17 becomes active.
- Authority refs: auth:orcp_55
- [inactive] r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response (workflow)
- Action: Log true incomplete-response trigger (overdue production, missing required artifacts after production, or deficiency stage).
- Expected effect: r18 becomes active.
- Authority refs: auth:orcp_46, auth:orcp_55
- [inactive] r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage (workflow)
- Action: Log deficiency notice sent/date (or deficiency stage status).
- Expected effect: r19 becomes active.
- Authority refs: auth:orcp_46, auth:orcp_55
- [unresolved] r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved (filing)
- Action: Add certified hearing register/minute entry and service/order-to-appear record proving nonappearance.
- Expected effect: r24 moves from unresolved to active in strict mode.
- Authority refs: auth:ors_33_075
- [unresolved] r7_solomon_forbidden_refile_precluded_issue (hypothesis)
- Action: Add certified prior final order/judgment, identity-of-issue comparison, and full/fair opportunity record.
- Expected effect: r7 moves from unresolved to active in strict mode.
- Authority refs: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
### Priority: medium
- [unresolved] r1_guardian_permission_if_prior_appointment (hypothesis)
- Action: Add certified prior guardianship appointment order and supporting service/compliance records.
- Expected effect: r1-r3 move from unresolved to active in strict mode (if all antecedents verified).
- Authority refs: auth:ors_125_050
- [unresolved] r2_target_noninterference_prohibition_if_prior_appointment (hypothesis)
- Action: Add certified prior guardianship appointment order and supporting service/compliance records.
- Expected effect: r1-r3 move from unresolved to active in strict mode (if all antecedents verified).
- Authority refs: auth:ors_125_050
- [unresolved] r3_target_obligation_comply_or_seek_relief_if_prior_appointment (hypothesis)
- Action: Add certified prior guardianship appointment order and supporting service/compliance records.
- Expected effect: r1-r3 move from unresolved to active in strict mode (if all antecedents verified).
- Authority refs: auth:ors_125_050
- [unresolved] r5_solomon_obligated_appear_and_answer (hypothesis)
- Action: Add certified record proving failure to appear in related hearing context.
- Expected effect: r5 moves from unresolved to active in strict mode.
- Authority refs: order:eppdapa_restraining_order
### Priority: low
- [inactive] r22_case_obligated_finalize_authority_citations_before_filing (filing)
- Action: If authority placeholders are now resolved, keep r22 inactive by design; if placeholders reappear, update source file and regenerate.
- Expected effect: Maintains accurate filing-readiness signal.
- Authority refs: auth:orcp_17_c
