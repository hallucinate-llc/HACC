# Motion Paragraph Bank Slice

Generated: 2026-04-07
Mode: inclusive
Motion: /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

## Paragraph 1
Rule: r1_guardian_permission_if_prior_appointment
Activation: None

Based on f_client_prior_appointment (alleged, dates=[], source=client_assertion, confidence=None(None), kind=None), the rule r1_guardian_permission_if_prior_appointment yields P(person:benjamin_barber, act_within_valid_guardian_scope, person:jane_cortez) with activation estimate None. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 2
Rule: r2_noninterference_prohibition_for_benjamin
Activation: None

Based on f_client_prior_appointment (alleged, dates=[], source=client_assertion, confidence=None(None), kind=None); f_client_benjamin_housing_interference (alleged, dates=[], source=client_assertion, confidence=None(None), kind=None), the rule r2_noninterference_prohibition_for_benjamin yields F(person:benjamin_barber, interfere_with_guardian_or_housing_process, process:hacc_housing_contract) with activation estimate None. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 3
Rule: r6_hacc_obligated_process_consistently_with_valid_authority
Activation: None

Based on f_hacc_process_exists (alleged, dates=[], source=client_assertion, confidence=None(None), kind=None); f_client_prior_appointment (alleged, dates=[], source=client_assertion, confidence=None(None), kind=None), the rule r6_hacc_obligated_process_consistently_with_valid_authority yields O(org:hacc, process_housing_consistent_with_valid_guardian_authority, person:jane_cortez) with activation estimate None. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 4
Rule: r6c_solomon_interference_not_proved_by_named_hacc_notice_gap
Activation: 2026-04-07

Based on f_hacc_named_notice_to_solomon_order_not_found (verified, dates=['2026-04-07'], source=protective_order_and_hacc_notice_timeline.md, confidence=None(None), kind=None), the rule r6c_solomon_interference_not_proved_by_named_hacc_notice_gap yields P(case:guardianship_collateral_estoppel, treat_solomon_hacc_interference_as_inference_not_direct_proof, person:solomon) with activation estimate 2026-04-07. Movant requests relief consistent with this rule-grounded posture.

