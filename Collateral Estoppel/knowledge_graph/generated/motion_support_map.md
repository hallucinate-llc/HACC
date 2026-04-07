# Motion Support Map

Generated: 2026-04-07

## Mode: strict
- Rules mapped: 13
- Rule: r4_solomon_forbidden_abuse_contact_property_control
- Conclusion: F(person:solomon, abuse_contact_or_control_property, person:jane_cortez)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_solomon_actual_notice_on_2025_11_17 [verified] ActualNotice dates=['2025-11-17'] source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=None(None) kind=None
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_contact_restrictions [verified] OrderRestrictsContact dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_property_restrictions [verified] OrderRestrictsPropertyControl dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r4b_solomon_forbidden_enter_residence
- Conclusion: F(person:solomon, enter_or_remain_at_petitioner_residence, location:10043_se_32nd_ave)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_solomon_actual_notice_on_2025_11_17 [verified] ActualNotice dates=['2025-11-17'] source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=None(None) kind=None
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_residence_restrictions [verified] OrderRestrictsResidenceAccess dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r5b_solomon_obligated_seek_hearing_or_comply
- Conclusion: O(person:solomon, seek_hearing_or_comply_with_existing_order, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_solomon_service_position_statement [verified] ServicePositionStatement dates=['2026-03-10'] source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r5c_solomon_forbidden_self_help_noncooperation
- Conclusion: F(person:solomon, adopt_self_help_noncooperation_posture, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_solomon_noncooperation_statement [verified] NoncooperationStatement dates=['2026-03-10'] source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r6b_hacc_obligated_document_lease_basis
- Conclusion: O(org:hacc, document_basis_for_household_composition_or_lease_adjustment, household:jane_cortez_household)
- Activation date estimate: 2026-01-01
- Antecedent evidence:
- f_hacc_lease_adjustment_effective_2026_01_01 [verified] LeaseAdjustmentEffective dates=['2026-01-01'] source=HACC vawa violation.pdf confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r6c_solomon_interference_not_proved_by_named_hacc_notice_gap
- Conclusion: P(case:guardianship_collateral_estoppel, treat_solomon_hacc_interference_as_inference_not_direct_proof, person:solomon)
- Activation date estimate: 2026-04-07
- Antecedent evidence:
- f_hacc_named_notice_to_solomon_order_not_found [verified] NamedHaccNoticeMessageNotFound dates=['2026-04-07'] source=protective_order_and_hacc_notice_timeline.md confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

- Rule: r8_solomon_notice_ack_triggers_court_relief_path
- Conclusion: O(person:solomon, seek_clarification_or_relief_through_court, order:eppdapa_restraining_order)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_feed_ev_solomon_ack_heard_restraining_order [verified] StatementHeardAboutRestrainingOrder dates=['2025-11-17'] source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=high(0.9) kind=direct_message
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r9_solomon_wait_for_service_conflicts_with_no_further_service
- Conclusion: F(person:solomon, condition_compliance_on_additional_service, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_wait_for_service_statement [verified] StatementWaitForServiceBeforeCompliance dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_no_further_service_needed [verified] NoFurtherServiceNeeded dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r10_solomon_noncooperation_statement_conflicts_with_effective_order
- Conclusion: F(person:solomon, intentional_noncooperation_with_effective_order, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_not_incentivized_statement [verified] StatementNotIncentivizedToCooperate dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r11_solomon_already_have_order_statement_supports_notice
- Conclusion: O(person:solomon, recognize_existing_order_status, order:eppdapa_restraining_order)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_feed_ev_solomon_ack_already_have_order [verified] StatementAlreadyHaveRestrainingOrder dates=['2025-11-17'] source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660690_Mon--17-Nov-2025-20-56-22--0000_New-text-message-from-solomon--503--381-6911.eml confidence=high(0.9) kind=direct_message
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order
- Conclusion: F(person:solomon, assert_order_ineffective_without_court_relief, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_order_not_in_effect_statement [verified] StatementOrderNotInEffect dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743131_Tue--10-Mar-2026-17-45-54--0000_New-text-message-from-solomon--503--381-6911.eml confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r13_solomon_judge_overturn_statement_triggers_motion_path
- Conclusion: O(person:solomon, file_motion_to_modify_or_vacate_before_noncompliance, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_judge_overturn_statement [verified] StatementWillHaveJudgeOverturn dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743129_Tue--10-Mar-2026-17-39-27--0000_New-text-message-from-solomon--503--381-6911.eml confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling
- Conclusion: O(org:hacc, avoid_third_party_housing_contact_with_restrained_person_and_document_response, person:jane_cortez)
- Activation date estimate: 2026-03-26
- Antecedent evidence:
- f_feed_ev_hacc_notice_brother_calls_after_granted_order [verified] MessageReportedBrotherCallsAfterGrantedOrder dates=['2026-03-26'] source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json confidence=medium(0.7) kind=json_export_extract
- f_feed_ev_hacc_notice_third_party_contact_with_restrained_person [verified] MessageObjectedThirdPartyContactWithRestrainedPerson dates=['2026-03-26'] source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json confidence=medium(0.7) kind=json_export_extract
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

## Mode: inclusive
- Rules mapped: 18
- Rule: r1_guardian_permission_if_prior_appointment
- Conclusion: P(person:benjamin_barber, act_within_valid_guardian_scope, person:jane_cortez)
- Activation date estimate: None
- Antecedent evidence:
- f_client_prior_appointment [alleged] PriorAppointmentExists dates=[] source=client_assertion confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

- Rule: r2_noninterference_prohibition_for_benjamin
- Conclusion: F(person:benjamin_barber, interfere_with_guardian_or_housing_process, process:hacc_housing_contract)
- Activation date estimate: None
- Antecedent evidence:
- f_client_prior_appointment [alleged] PriorAppointmentExists dates=[] source=client_assertion confidence=None(None) kind=None
- f_client_benjamin_housing_interference [alleged] Interference dates=[] source=client_assertion confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

- Rule: r3_benjamin_obligation_comply_or_seek_relief
- Conclusion: O(person:benjamin_barber, comply_with_order_or_seek_relief, order:prior_guardianship_order)
- Activation date estimate: None
- Antecedent evidence:
- f_client_prior_appointment [alleged] PriorAppointmentExists dates=[] source=client_assertion confidence=None(None) kind=None
- f_client_benjamin_order_disregard [alleged] DisregardedOrder dates=[] source=client_assertion confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r4_solomon_forbidden_abuse_contact_property_control
- Conclusion: F(person:solomon, abuse_contact_or_control_property, person:jane_cortez)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_solomon_actual_notice_on_2025_11_17 [verified] ActualNotice dates=['2025-11-17'] source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=None(None) kind=None
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_contact_restrictions [verified] OrderRestrictsContact dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_property_restrictions [verified] OrderRestrictsPropertyControl dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r4b_solomon_forbidden_enter_residence
- Conclusion: F(person:solomon, enter_or_remain_at_petitioner_residence, location:10043_se_32nd_ave)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_solomon_actual_notice_on_2025_11_17 [verified] ActualNotice dates=['2025-11-17'] source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=None(None) kind=None
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_residence_restrictions [verified] OrderRestrictsResidenceAccess dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r5_solomon_obligated_appear_and_answer
- Conclusion: O(person:solomon, appear_and_answer_show_cause, proceeding:related_order_hearing)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_restraining_order_no_further_service_needed [verified] NoFurtherServiceNeeded dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_client_solomon_failed_appearance [alleged] FailedToAppear dates=['2026-03-10'] source=client_assertion confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r5b_solomon_obligated_seek_hearing_or_comply
- Conclusion: O(person:solomon, seek_hearing_or_comply_with_existing_order, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_solomon_service_position_statement [verified] ServicePositionStatement dates=['2026-03-10'] source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r5c_solomon_forbidden_self_help_noncooperation
- Conclusion: F(person:solomon, adopt_self_help_noncooperation_posture, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_restraining_order_granted [verified] OrderGranted dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- f_solomon_noncooperation_statement [verified] NoncooperationStatement dates=['2026-03-10'] source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r6_hacc_obligated_process_consistently_with_valid_authority
- Conclusion: O(org:hacc, process_housing_consistent_with_valid_guardian_authority, person:jane_cortez)
- Activation date estimate: None
- Antecedent evidence:
- f_hacc_process_exists [alleged] HousingProcessActive dates=[] source=client_assertion confidence=None(None) kind=None
- f_client_prior_appointment [alleged] PriorAppointmentExists dates=[] source=client_assertion confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

- Rule: r6b_hacc_obligated_document_lease_basis
- Conclusion: O(org:hacc, document_basis_for_household_composition_or_lease_adjustment, household:jane_cortez_household)
- Activation date estimate: 2026-01-01
- Antecedent evidence:
- f_hacc_lease_adjustment_effective_2026_01_01 [verified] LeaseAdjustmentEffective dates=['2026-01-01'] source=HACC vawa violation.pdf confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r6c_solomon_interference_not_proved_by_named_hacc_notice_gap
- Conclusion: P(case:guardianship_collateral_estoppel, treat_solomon_hacc_interference_as_inference_not_direct_proof, person:solomon)
- Activation date estimate: 2026-04-07
- Antecedent evidence:
- f_hacc_named_notice_to_solomon_order_not_found [verified] NamedHaccNoticeMessageNotFound dates=['2026-04-07'] source=protective_order_and_hacc_notice_timeline.md confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_for_appointment_and_appearance_of_guardian_ad_litem.md

- Rule: r8_solomon_notice_ack_triggers_court_relief_path
- Conclusion: O(person:solomon, seek_clarification_or_relief_through_court, order:eppdapa_restraining_order)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_feed_ev_solomon_ack_heard_restraining_order [verified] StatementHeardAboutRestrainingOrder dates=['2025-11-17'] source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml confidence=high(0.9) kind=direct_message
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r9_solomon_wait_for_service_conflicts_with_no_further_service
- Conclusion: F(person:solomon, condition_compliance_on_additional_service, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_wait_for_service_statement [verified] StatementWaitForServiceBeforeCompliance dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_no_further_service_needed [verified] NoFurtherServiceNeeded dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r10_solomon_noncooperation_statement_conflicts_with_effective_order
- Conclusion: F(person:solomon, intentional_noncooperation_with_effective_order, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_not_incentivized_statement [verified] StatementNotIncentivizedToCooperate dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r11_solomon_already_have_order_statement_supports_notice
- Conclusion: O(person:solomon, recognize_existing_order_status, order:eppdapa_restraining_order)
- Activation date estimate: 2025-11-20
- Antecedent evidence:
- f_feed_ev_solomon_ack_already_have_order [verified] StatementAlreadyHaveRestrainingOrder dates=['2025-11-17'] source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660690_Mon--17-Nov-2025-20-56-22--0000_New-text-message-from-solomon--503--381-6911.eml confidence=high(0.9) kind=direct_message
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order
- Conclusion: F(person:solomon, assert_order_ineffective_without_court_relief, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_order_not_in_effect_statement [verified] StatementOrderNotInEffect dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743131_Tue--10-Mar-2026-17-45-54--0000_New-text-message-from-solomon--503--381-6911.eml confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r13_solomon_judge_overturn_statement_triggers_motion_path
- Conclusion: O(person:solomon, file_motion_to_modify_or_vacate_before_noncompliance, order:eppdapa_restraining_order)
- Activation date estimate: 2026-03-10
- Antecedent evidence:
- f_feed_ev_solomon_judge_overturn_statement [verified] StatementWillHaveJudgeOverturn dates=['2026-03-10'] source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743129_Tue--10-Mar-2026-17-39-27--0000_New-text-message-from-solomon--503--381-6911.eml confidence=medium_high(0.8) kind=transcript_extract
- f_restraining_order_in_effect [verified] OrderInEffect dates=['2025-11-20'] source=sam_barber_restraining_order_ocr.txt confidence=None(None) kind=None
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

- Rule: r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling
- Conclusion: O(org:hacc, avoid_third_party_housing_contact_with_restrained_person_and_document_response, person:jane_cortez)
- Activation date estimate: 2026-03-26
- Antecedent evidence:
- f_feed_ev_hacc_notice_brother_calls_after_granted_order [verified] MessageReportedBrotherCallsAfterGrantedOrder dates=['2026-03-26'] source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json confidence=medium(0.7) kind=json_export_extract
- f_feed_ev_hacc_notice_third_party_contact_with_restrained_person [verified] MessageObjectedThirdPartyContactWithRestrainedPerson dates=['2026-03-26'] source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json confidence=medium(0.7) kind=json_export_extract
- Recommended motions:
- /home/barberb/HACC/Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md

