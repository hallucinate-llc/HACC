# Certified Promotion What-If Scenarios

Generated: 2026-04-07

## baseline_current_overrides
- promotions: 0 (none)
- strict counts: active=31 unresolved=6 inactive=4
- target rules:
- r1_guardian_permission_if_prior_appointment: unresolved
- r2_noninterference_prohibition_for_benjamin: unresolved
- r3_benjamin_obligation_comply_or_seek_relief: unresolved
- r5_solomon_obligated_appear_and_answer: unresolved
- r7_solomon_forbidden_refile_precluded_issue: unresolved
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: unresolved

## promote_nonappearance_only
- promotions: 1 (f_client_solomon_failed_appearance)
- strict counts: active=33 unresolved=4 inactive=4
- target rules:
- r1_guardian_permission_if_prior_appointment: unresolved
- r2_noninterference_prohibition_for_benjamin: unresolved
- r3_benjamin_obligation_comply_or_seek_relief: unresolved
- r5_solomon_obligated_appear_and_answer: active
- r7_solomon_forbidden_refile_precluded_issue: unresolved
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: active

## promote_issue_preclusion_pair
- promotions: 2 (f_collateral_estoppel_candidate, f_client_solomon_barred_refile)
- strict counts: active=32 unresolved=5 inactive=4
- target rules:
- r1_guardian_permission_if_prior_appointment: unresolved
- r2_noninterference_prohibition_for_benjamin: unresolved
- r3_benjamin_obligation_comply_or_seek_relief: unresolved
- r5_solomon_obligated_appear_and_answer: unresolved
- r7_solomon_forbidden_refile_precluded_issue: active
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: unresolved

## promote_prior_appointment_cluster
- promotions: 3 (f_client_prior_appointment, f_client_benjamin_housing_interference, f_client_benjamin_order_disregard)
- strict counts: active=34 unresolved=3 inactive=4
- target rules:
- r1_guardian_permission_if_prior_appointment: active
- r2_noninterference_prohibition_for_benjamin: active
- r3_benjamin_obligation_comply_or_seek_relief: active
- r5_solomon_obligated_appear_and_answer: unresolved
- r7_solomon_forbidden_refile_precluded_issue: unresolved
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: unresolved

## promote_all_top_blockers
- promotions: 6 (f_client_solomon_failed_appearance, f_collateral_estoppel_candidate, f_client_solomon_barred_refile, f_client_prior_appointment, f_client_benjamin_housing_interference, f_client_benjamin_order_disregard)
- strict counts: active=37 unresolved=0 inactive=4
- target rules:
- r1_guardian_permission_if_prior_appointment: active
- r2_noninterference_prohibition_for_benjamin: active
- r3_benjamin_obligation_comply_or_seek_relief: active
- r5_solomon_obligated_appear_and_answer: active
- r7_solomon_forbidden_refile_precluded_issue: active
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: active
