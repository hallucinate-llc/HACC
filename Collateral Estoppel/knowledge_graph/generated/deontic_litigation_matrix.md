# Deontic Litigation Matrix

Generated: 2026-04-07

## Mode: strict
- Active rules: 13
- Unresolved rules: 6
- Party: case:guardianship_collateral_estoppel
- Counts: O=0 P=1 F=0
- Permissions:
- treat_solomon_hacc_interference_as_inference_not_direct_proof -> person:solomon (r6c_solomon_interference_not_proved_by_named_hacc_notice_gap, at 2026-04-07)

- Party: org:hacc
- Counts: O=2 P=0 F=0
- Obligations:
- document_basis_for_household_composition_or_lease_adjustment -> household:jane_cortez_household (r6b_hacc_obligated_document_lease_basis, at 2026-01-01)
- avoid_third_party_housing_contact_with_restrained_person_and_document_response -> person:jane_cortez (r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling, at 2026-03-26)

- Party: person:solomon
- Counts: O=4 P=0 F=6
- Obligations:
- seek_hearing_or_comply_with_existing_order -> order:eppdapa_restraining_order (r5b_solomon_obligated_seek_hearing_or_comply, at 2026-03-10)
- seek_clarification_or_relief_through_court -> order:eppdapa_restraining_order (r8_solomon_notice_ack_triggers_court_relief_path, at 2025-11-20)
- recognize_existing_order_status -> order:eppdapa_restraining_order (r11_solomon_already_have_order_statement_supports_notice, at 2025-11-20)
- file_motion_to_modify_or_vacate_before_noncompliance -> order:eppdapa_restraining_order (r13_solomon_judge_overturn_statement_triggers_motion_path, at 2026-03-10)
- Prohibitions:
- abuse_contact_or_control_property -> person:jane_cortez (r4_solomon_forbidden_abuse_contact_property_control, at 2025-11-20)
- enter_or_remain_at_petitioner_residence -> location:10043_se_32nd_ave (r4b_solomon_forbidden_enter_residence, at 2025-11-20)
- adopt_self_help_noncooperation_posture -> order:eppdapa_restraining_order (r5c_solomon_forbidden_self_help_noncooperation, at 2026-03-10)
- condition_compliance_on_additional_service -> order:eppdapa_restraining_order (r9_solomon_wait_for_service_conflicts_with_no_further_service, at 2026-03-10)
- intentional_noncooperation_with_effective_order -> order:eppdapa_restraining_order (r10_solomon_noncooperation_statement_conflicts_with_effective_order, at 2026-03-10)
- assert_order_ineffective_without_court_relief -> order:eppdapa_restraining_order (r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order, at 2026-03-10)

## Mode: inclusive
- Active rules: 18
- Unresolved rules: 1
- Party: case:guardianship_collateral_estoppel
- Counts: O=0 P=1 F=0
- Permissions:
- treat_solomon_hacc_interference_as_inference_not_direct_proof -> person:solomon (r6c_solomon_interference_not_proved_by_named_hacc_notice_gap, at 2026-04-07)

- Party: org:hacc
- Counts: O=3 P=0 F=0
- Obligations:
- process_housing_consistent_with_valid_guardian_authority -> person:jane_cortez (r6_hacc_obligated_process_consistently_with_valid_authority, at None)
- document_basis_for_household_composition_or_lease_adjustment -> household:jane_cortez_household (r6b_hacc_obligated_document_lease_basis, at 2026-01-01)
- avoid_third_party_housing_contact_with_restrained_person_and_document_response -> person:jane_cortez (r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling, at 2026-03-26)

- Party: person:benjamin_barber
- Counts: O=1 P=1 F=1
- Obligations:
- comply_with_order_or_seek_relief -> order:prior_guardianship_order (r3_benjamin_obligation_comply_or_seek_relief, at None)
- Permissions:
- act_within_valid_guardian_scope -> person:jane_cortez (r1_guardian_permission_if_prior_appointment, at None)
- Prohibitions:
- interfere_with_guardian_or_housing_process -> process:hacc_housing_contract (r2_noninterference_prohibition_for_benjamin, at None)

- Party: person:solomon
- Counts: O=5 P=0 F=6
- Obligations:
- appear_and_answer_show_cause -> proceeding:related_order_hearing (r5_solomon_obligated_appear_and_answer, at 2026-03-10)
- seek_hearing_or_comply_with_existing_order -> order:eppdapa_restraining_order (r5b_solomon_obligated_seek_hearing_or_comply, at 2026-03-10)
- seek_clarification_or_relief_through_court -> order:eppdapa_restraining_order (r8_solomon_notice_ack_triggers_court_relief_path, at 2025-11-20)
- recognize_existing_order_status -> order:eppdapa_restraining_order (r11_solomon_already_have_order_statement_supports_notice, at 2025-11-20)
- file_motion_to_modify_or_vacate_before_noncompliance -> order:eppdapa_restraining_order (r13_solomon_judge_overturn_statement_triggers_motion_path, at 2026-03-10)
- Prohibitions:
- abuse_contact_or_control_property -> person:jane_cortez (r4_solomon_forbidden_abuse_contact_property_control, at 2025-11-20)
- enter_or_remain_at_petitioner_residence -> location:10043_se_32nd_ave (r4b_solomon_forbidden_enter_residence, at 2025-11-20)
- adopt_self_help_noncooperation_posture -> order:eppdapa_restraining_order (r5c_solomon_forbidden_self_help_noncooperation, at 2026-03-10)
- condition_compliance_on_additional_service -> order:eppdapa_restraining_order (r9_solomon_wait_for_service_conflicts_with_no_further_service, at 2026-03-10)
- intentional_noncooperation_with_effective_order -> order:eppdapa_restraining_order (r10_solomon_noncooperation_statement_conflicts_with_effective_order, at 2026-03-10)
- assert_order_ineffective_without_court_relief -> order:eppdapa_restraining_order (r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order, at 2026-03-10)

