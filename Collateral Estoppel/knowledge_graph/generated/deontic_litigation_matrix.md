# Deontic Litigation Matrix

Generated: 2026-04-07

## Mode: strict
- Active rules: 29
- Unresolved rules: 6
- Inactive rules: 4
- Party: case:26PR00641
- Counts: O=2 P=2 F=0
- Obligations:
- preserve_statutory_notice_and_objection_window_for_protective_petition -> person:jane_cortez (r29_case_obligated_preserve_notice_and_objection_window, at 2026-04-07)
- schedule_and_process_hearing_on_guardianship_objection -> person:jane_cortez (r30_case_obligated_schedule_hearing_on_presented_objection, at 2026-04-07)
- Permissions:
- apply_orcp_and_oec_subject_to_specific_chapter_125_overrides -> proceeding:protective_proceeding (r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding, at 2026-04-07)
- assert_respondent_right_to_appear_in_person_or_by_counsel -> person:jane_cortez (r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel, at 2026-04-07)

- Party: case:guardianship_collateral_estoppel
- Counts: O=2 P=8 F=0
- Obligations:
- treat_prior_appointment_theory_as_hypothesis_until_source_order_found -> issue:prior_appointment_for_jane_cortez (r6d_case_obligated_treat_prior_appointment_as_hypothesis_only, at 2026-04-07)
- resolve_benjamin_vs_solomon_interference_actor_assignment_with_source_record -> issue:interference_actor_assignment (r21_case_obligated_resolve_actor_assignment_conflict, at 2026-04-07)
- Permissions:
- treat_solomon_hacc_interference_as_inference_not_direct_proof -> person:solomon (r6c_solomon_interference_not_proved_by_named_hacc_notice_gap, at 2026-04-07)
- seek_compelled_production_of_hacc_actor_document_authority_chain -> issue:lease_change_actor_identification (r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain, at 2026-04-07)
- treat_subpoena_enforcement_motion_path_as_pending_until_service -> case:26PR00641 (r20_case_permitted_treat_enforcement_path_as_pending_pre_service, at 2026-04-07)
- initiate_remedial_contempt_or_show_cause_path -> person:solomon (r23_case_permitted_initiate_remedial_contempt_path, at 2026-04-07)
- seek_compensatory_or_compliance_oriented_remedial_sanctions_if_contempt_is_proved -> issue:prejudice_and_noninterference_relief (r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved, at 2026-04-07)
- seek_orcp_17_sanctions_if_filing_is_shown_improper_or_factually_or_legally_unsupported -> issue:sanctions_track (r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown, at 2026-04-07)
- seek_subpoena_enforcement_and_related_expenses_after_nonparty_noncompliance -> org:hacc (r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46, at 2026-04-07)
- use_orcp9_service_and_orcp10_deadline_computation_for_later_filed_motion_packets -> issue:service_and_deadlines (r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines, at 2026-04-07)

- Party: org:hacc
- Counts: O=3 P=0 F=0
- Obligations:
- identify_actor_document_and_authority_chain_for_lease_change -> household:jane_cortez_household (r6_hacc_obligated_document_authority_chain_for_lease_change, at 2026-01-12)
- document_basis_for_household_composition_or_lease_adjustment -> household:jane_cortez_household (r6b_hacc_obligated_document_lease_basis, at 2026-01-12)
- avoid_third_party_housing_contact_with_restrained_person_and_document_response -> person:jane_cortez (r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling, at 2026-03-26)

- Party: person:benjamin_barber
- Counts: O=1 P=1 F=0
- Obligations:
- maintain_service_and_deadline_tracking -> case:26PR00641 (r16_benjamin_obligated_track_service_and_deadlines, at 2026-04-07)
- Permissions:
- serve_staged_subpoena_packets -> case:26PR00641 (r15_benjamin_permitted_serve_subpoena_packets, at 2026-04-07)

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
- Active rules: 30
- Unresolved rules: 5
- Inactive rules: 4
- Party: case:26PR00641
- Counts: O=2 P=2 F=0
- Obligations:
- preserve_statutory_notice_and_objection_window_for_protective_petition -> person:jane_cortez (r29_case_obligated_preserve_notice_and_objection_window, at 2026-04-07)
- schedule_and_process_hearing_on_guardianship_objection -> person:jane_cortez (r30_case_obligated_schedule_hearing_on_presented_objection, at 2026-04-07)
- Permissions:
- apply_orcp_and_oec_subject_to_specific_chapter_125_overrides -> proceeding:protective_proceeding (r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding, at 2026-04-07)
- assert_respondent_right_to_appear_in_person_or_by_counsel -> person:jane_cortez (r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel, at 2026-04-07)

- Party: case:guardianship_collateral_estoppel
- Counts: O=2 P=9 F=0
- Obligations:
- treat_prior_appointment_theory_as_hypothesis_until_source_order_found -> issue:prior_appointment_for_jane_cortez (r6d_case_obligated_treat_prior_appointment_as_hypothesis_only, at 2026-04-07)
- resolve_benjamin_vs_solomon_interference_actor_assignment_with_source_record -> issue:interference_actor_assignment (r21_case_obligated_resolve_actor_assignment_conflict, at 2026-04-07)
- Permissions:
- treat_solomon_hacc_interference_as_inference_not_direct_proof -> person:solomon (r6c_solomon_interference_not_proved_by_named_hacc_notice_gap, at 2026-04-07)
- seek_compelled_production_of_hacc_actor_document_authority_chain -> issue:lease_change_actor_identification (r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain, at 2026-04-07)
- treat_subpoena_enforcement_motion_path_as_pending_until_service -> case:26PR00641 (r20_case_permitted_treat_enforcement_path_as_pending_pre_service, at 2026-04-07)
- initiate_remedial_contempt_or_show_cause_path -> person:solomon (r23_case_permitted_initiate_remedial_contempt_path, at 2026-04-07)
- seek_order_or_warrant_to_compel_appearance_if_order_to_appear_is_served_and_ignored -> person:solomon (r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved, at 2026-04-07)
- seek_compensatory_or_compliance_oriented_remedial_sanctions_if_contempt_is_proved -> issue:prejudice_and_noninterference_relief (r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved, at 2026-04-07)
- seek_orcp_17_sanctions_if_filing_is_shown_improper_or_factually_or_legally_unsupported -> issue:sanctions_track (r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown, at 2026-04-07)
- seek_subpoena_enforcement_and_related_expenses_after_nonparty_noncompliance -> org:hacc (r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46, at 2026-04-07)
- use_orcp9_service_and_orcp10_deadline_computation_for_later_filed_motion_packets -> issue:service_and_deadlines (r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines, at 2026-04-07)

- Party: org:hacc
- Counts: O=3 P=0 F=0
- Obligations:
- identify_actor_document_and_authority_chain_for_lease_change -> household:jane_cortez_household (r6_hacc_obligated_document_authority_chain_for_lease_change, at 2026-01-12)
- document_basis_for_household_composition_or_lease_adjustment -> household:jane_cortez_household (r6b_hacc_obligated_document_lease_basis, at 2026-01-12)
- avoid_third_party_housing_contact_with_restrained_person_and_document_response -> person:jane_cortez (r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling, at 2026-03-26)

- Party: person:benjamin_barber
- Counts: O=1 P=1 F=0
- Obligations:
- maintain_service_and_deadline_tracking -> case:26PR00641 (r16_benjamin_obligated_track_service_and_deadlines, at 2026-04-07)
- Permissions:
- serve_staged_subpoena_packets -> case:26PR00641 (r15_benjamin_permitted_serve_subpoena_packets, at 2026-04-07)

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

