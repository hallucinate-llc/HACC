# Motion Paragraph Bank Slice

Generated: 2026-04-07
Mode: strict
Motion: /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

## Paragraph 1
Rule: r4_solomon_forbidden_abuse_contact_property_control
Activation: 2025-11-20

Based on f_solomon_actual_notice_on_2025_11_17 (verified, dates=['2025-11-17'], source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=None(None), kind=None); f_restraining_order_granted (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_contact_restrictions (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_property_restrictions (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r4_solomon_forbidden_abuse_contact_property_control yields F(person:solomon, abuse_contact_or_control_property, person:jane_cortez) with activation estimate 2025-11-20. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 2
Rule: r4b_solomon_forbidden_enter_residence
Activation: 2025-11-20

Based on f_solomon_actual_notice_on_2025_11_17 (verified, dates=['2025-11-17'], source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=None(None), kind=None); f_restraining_order_granted (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_residence_restrictions (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r4b_solomon_forbidden_enter_residence yields F(person:solomon, enter_or_remain_at_petitioner_residence, location:10043_se_32nd_ave) with activation estimate 2025-11-20. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 3
Rule: r5b_solomon_obligated_seek_hearing_or_comply
Activation: 2026-03-10

Based on f_restraining_order_granted (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_solomon_service_position_statement (verified, dates=['2026-03-10'], source=transcript.txt, confidence=None(None), kind=None), the rule r5b_solomon_obligated_seek_hearing_or_comply yields O(person:solomon, seek_hearing_or_comply_with_existing_order, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 4
Rule: r5c_solomon_forbidden_self_help_noncooperation
Activation: 2026-03-10

Based on f_restraining_order_granted (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None); f_solomon_noncooperation_statement (verified, dates=['2026-03-10'], source=transcript.txt, confidence=None(None), kind=None), the rule r5c_solomon_forbidden_self_help_noncooperation yields F(person:solomon, adopt_self_help_noncooperation_posture, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 5
Rule: r6b_hacc_obligated_document_lease_basis
Activation: 2026-01-01

Based on f_hacc_lease_adjustment_effective_2026_01_01 (verified, dates=['2026-01-01'], source=HACC vawa violation.pdf, confidence=None(None), kind=None), the rule r6b_hacc_obligated_document_lease_basis yields O(org:hacc, document_basis_for_household_composition_or_lease_adjustment, household:jane_cortez_household) with activation estimate 2026-01-01. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 6
Rule: r6c_solomon_interference_not_proved_by_named_hacc_notice_gap
Activation: 2026-04-07

Based on f_hacc_named_notice_to_solomon_order_not_found (verified, dates=['2026-04-07'], source=protective_order_and_hacc_notice_timeline.md, confidence=None(None), kind=None), the rule r6c_solomon_interference_not_proved_by_named_hacc_notice_gap yields P(case:guardianship_collateral_estoppel, treat_solomon_hacc_interference_as_inference_not_direct_proof, person:solomon) with activation estimate 2026-04-07. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 7
Rule: r8_solomon_notice_ack_triggers_court_relief_path
Activation: 2025-11-20

Based on f_feed_ev_solomon_ack_heard_restraining_order (verified, dates=['2025-11-17'], source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=high(0.9), kind=direct_message); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r8_solomon_notice_ack_triggers_court_relief_path yields O(person:solomon, seek_clarification_or_relief_through_court, order:eppdapa_restraining_order) with activation estimate 2025-11-20. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 8
Rule: r9_solomon_wait_for_service_conflicts_with_no_further_service
Activation: 2026-03-10

Based on f_feed_ev_solomon_wait_for_service_statement (verified, dates=['2026-03-10'], source=transcript.txt, confidence=medium_high(0.8), kind=transcript_extract); f_restraining_order_no_further_service_needed (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r9_solomon_wait_for_service_conflicts_with_no_further_service yields F(person:solomon, condition_compliance_on_additional_service, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 9
Rule: r10_solomon_noncooperation_statement_conflicts_with_effective_order
Activation: 2026-03-10

Based on f_feed_ev_solomon_not_incentivized_statement (verified, dates=['2026-03-10'], source=transcript.txt, confidence=medium_high(0.8), kind=transcript_extract); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r10_solomon_noncooperation_statement_conflicts_with_effective_order yields F(person:solomon, intentional_noncooperation_with_effective_order, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 10
Rule: r11_solomon_already_have_order_statement_supports_notice
Activation: 2025-11-20

Based on f_feed_ev_solomon_ack_already_have_order (verified, dates=['2025-11-17'], source=uid_660690_Mon--17-Nov-2025-20-56-22--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=high(0.9), kind=direct_message); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r11_solomon_already_have_order_statement_supports_notice yields O(person:solomon, recognize_existing_order_status, order:eppdapa_restraining_order) with activation estimate 2025-11-20. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 11
Rule: r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order
Activation: 2026-03-10

Based on f_feed_ev_solomon_order_not_in_effect_statement (verified, dates=['2026-03-10'], source=uid_743131_Tue--10-Mar-2026-17-45-54--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=medium_high(0.8), kind=transcript_extract); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order yields F(person:solomon, assert_order_ineffective_without_court_relief, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 12
Rule: r13_solomon_judge_overturn_statement_triggers_motion_path
Activation: 2026-03-10

Based on f_feed_ev_solomon_judge_overturn_statement (verified, dates=['2026-03-10'], source=uid_743129_Tue--10-Mar-2026-17-39-27--0000_New-text-message-from-solomon--503--381-6911.eml, confidence=medium_high(0.8), kind=transcript_extract); f_restraining_order_in_effect (verified, dates=['2025-11-20'], source=sam_barber_restraining_order_ocr.txt, confidence=None(None), kind=None), the rule r13_solomon_judge_overturn_statement_triggers_motion_path yields O(person:solomon, file_motion_to_modify_or_vacate_before_noncompliance, order:eppdapa_restraining_order) with activation estimate 2026-03-10. Movant requests relief consistent with this rule-grounded posture.

## Paragraph 13
Rule: r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling
Activation: 2026-03-26

Based on f_feed_ev_hacc_notice_brother_calls_after_granted_order (verified, dates=['2026-03-26'], source=message.json, confidence=medium(0.7), kind=json_export_extract); f_feed_ev_hacc_notice_third_party_contact_with_restrained_person (verified, dates=['2026-03-26'], source=message.json, confidence=medium(0.7), kind=json_export_extract), the rule r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling yields O(org:hacc, avoid_third_party_housing_contact_with_restrained_person_and_document_response, person:jane_cortez) with activation estimate 2026-03-26. Movant requests relief consistent with this rule-grounded posture.

