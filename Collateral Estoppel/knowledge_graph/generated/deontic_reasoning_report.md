# Deontic Reasoning Report

Generated: 2026-04-09

## Fact Override Intake
- Override file: /home/barberb/HACC/Collateral Estoppel/knowledge_graph/evidence_fact_overrides_2026-04-07.csv
- Rows read: 7
- Applied: 7
- Skipped: 0
- Applied status changes: 0
- Applied value changes: 0
- Applied status/value changes: 0
- Applied source changes: 7
- Applied date additions: 7

## Temporal Intervals
- ti_restraining_order_effective_period: 2025-11-20 -> 2026-11-20 [estimated; tags: order_effective_period, estimated_expiration]
- ti_probate_notice_objection_window: 2026-03-31 -> 2026-04-05 [verified; tags: notice_window, objection_window]
- ti_hacc_lease_change_sequence: 2026-01-01 -> 2026-01-12 [verified; tags: hacc_lease_change, authority_chain_gap]
- ti_exhibit_r_compelled_production_track: 2026-04-09 -> None [open; tags: subpoena_workflow, compelled_production]

## Element Audits
- audit_remedial_contempt_timing: Remedial contempt timing audit
- Authority: ['auth:ors_33_055', 'auth:ors_33_075', 'auth:ors_33_105']
- Intervals: ['ti_restraining_order_effective_period']
- Element valid_order: verified (facts=['f_restraining_order_granted', 'f_restraining_order_in_effect'])
- Element notice: verified (facts=['f_solomon_actual_notice_on_2025_11_17', 'f_restraining_order_no_further_service_needed'])
- Element post_notice_conduct: verified (facts=['f_solomon_service_position_statement', 'f_solomon_noncooperation_statement'])
- Element service_or_appearance_record: proof_gated (facts=[])
- Note: The local repository supports notice strongly, but a cleaner certified docket / appearance record remains preferable for filing-grade contempt proof.

- audit_probate_objection_hearing_timing: Probate objection and hearing timing audit
- Authority: ['auth:ors_125_075', 'auth:ors_125_080']
- Intervals: ['ti_probate_notice_objection_window']
- Element notice_issued: verified (facts=['f_notice_to_respondent'])
- Element objection_presented: verified (facts=['f_respondent_objection_form_present'])
- Element hearing_required: verified (facts=['f_notice_to_respondent', 'f_respondent_objection_form_present'])

- audit_exhibit_r_subpoena_timing: Exhibit R subpoena timing audit
- Authority: ['auth:orcp_55', 'auth:orcp_46']
- Intervals: ['ti_exhibit_r_compelled_production_track']
- Element local_search_negative: verified (facts=['f_hacc_actor_identification_record_not_found_locally'])
- Element compelled_production_needed: verified (facts=['f_hacc_exhibit_r_requires_compelled_production'])
- Element service_stage_complete: missing (facts=['f_subpoena_service_completed_any'])
- Note: Promotes automatically from the active service log once any subpoena service is logged.
- Element deficiency_or_compel_stage: missing (facts=['f_deficiency_notice_sent_any', 'f_motion_to_compel_stage_any'])
- Note: Promotes automatically from the active service log when a deficiency notice or motion-to-compel stage is entered.
- Element pre_service_only: verified (facts=['f_subpoena_pre_service_phase_only'])
- Note: This captures the current no-service-yet posture when the service log has been initialized but no service entries have been completed.

- audit_orcp17_sanctions_elements: ORCP 17 sanctions element audit
- Authority: ['auth:orcp_17_c']
- Intervals: []
- Element sanctions_authority_available: verified (facts=['f_authority_orcp_17_improper_purpose_and_support'])
- Element proof_state_caution_present: verified (facts=['f_hacc_named_notice_to_solomon_order_not_found', 'f_prior_appointment_source_order_not_found'])
- Element improper_purpose_or_unsupported_filing_proof: proof_gated (facts=['f_client_solomon_barred_refile'])
- Note: The current record supports inquiry and caution, but final ORCP 17 findings still require the filing-by-filing manifest to identify the challenged filing and map the specific sanction predicates.
- Element challenged_filing_identified: verified (facts=[])
- Note: Current best candidate target is the Solomon Barber first amended guardianship petition reflected in solomon_motion_for_guardianship_ocr.txt, dated March 31, 2026. This identifies the filing only and does not by itself establish any ORCP 17 predicate.
- Element improper_purpose_mapped: proof_gated (facts=[])
- Note: Current candidate theory only: the challenged filing may have functioned to obtain control, create delay, or exert collateral pressure rather than to seek only properly bounded judicial relief. This remains proof-gated and should not be treated as established absent stronger filing-specific record support.
- Element unsupported_legal_position_mapped: proof_gated (facts=[])
- Note: Current candidate theory only: the challenged filing may depend on a legal position that becomes unsupported if certified prior-proceeding materials and completed issue-preclusion mapping later show that the filing sought to relitigate an already-resolved authority issue. This remains proof-gated.
- Element unsupported_factual_assertion_mapped: proof_gated (facts=[])
- Note: Current candidate theory only: the petition-side statement that no guardian had previously been appointed for Jane Cortez may become a contradicted factual assertion if a certified prior appointment order is later staged and verified. This remains proof-gated.

- audit_issue_preclusion_elements: Issue-preclusion element audit
- Authority: ['auth:oregon_issue_preclusion_cases', 'auth:oregon_issue_preclusion_prior_separate_proceeding_cases']
- Intervals: []
- Element doctrine_grounded: verified (facts=['f_authority_issue_preclusion_elements_official_oregon_cases', 'f_authority_issue_preclusion_requires_prior_separate_proceeding'])
- Element candidate_refile_theory: proof_gated (facts=['f_collateral_estoppel_candidate', 'f_client_solomon_barred_refile'])
- Note: The local model carries a barred-refile candidate theory, but not yet a certified prior proceeding record proving application of the doctrine.
- Element prior_separate_proceeding_record: missing (facts=['f_certified_prior_order_material_present', 'f_certified_prior_docket_material_present'])
- Note: Promotes automatically when certified prior-order and docket/register materials are staged in evidence_notes/certified_records.
- Element identical_issue_and_finality_mapping: proof_gated (facts=['f_certified_prior_order_material_present', 'f_certified_prior_docket_material_present', 'f_certified_prior_hearing_material_present'])
- Note: These elements remain open until certified prior-order, docket, and hearing materials are staged and the issue_preclusion_mapping.json manifest marks the element mapping complete.
- Element identical_issue_mapped: proof_gated (facts=['f_certified_prior_order_material_present', 'f_certified_prior_docket_material_present'])
- Note: Candidate sources indicate potential overlap of the guardianship authority issue across filings. Candidate references: Collateral Estoppel/evidence_notes/missing_exhibit_search_status_2026-04-07.md; Collateral Estoppel/evidence_notes/repeated_usurpation_pattern_memo.md; Collateral Estoppel/drafts/petition_guardianship_packet_stage1.md; Collateral Estoppel/drafts/petition_guardianship_court_ready_shell.md
- Element finality_mapped: proof_gated (facts=['f_certified_prior_order_material_present', 'f_certified_prior_docket_material_present'])
- Note: Current index did not yield reliable finality artifacts; certified final order and register are still required. Candidate references: Collateral Estoppel/evidence_notes/sam_barber_restraining_order_ocr.txt; Collateral Estoppel/evidence_notes/solomon_order_completeness_checklist.md; Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md; Collateral Estoppel/drafts/petition_guardianship_working_memo.md
- Element party_privity_mapped: proof_gated (facts=['f_certified_prior_order_material_present', 'f_certified_prior_docket_material_present'])
- Note: Candidate sources indicate party-name overlap, but party/privity mapping remains uncertified. Candidate references: Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.md; Collateral Estoppel/drafts/motion_for_leave_or_to_compel_exhibit_r_production.md; Collateral Estoppel/drafts/final_filing_set/11B_attachment_a2_definitions_and_instructions_final.md; Collateral Estoppel/evidence_notes/protective_order_and_hacc_notice_timeline.md
- Element full_fair_opportunity_mapped: proof_gated (facts=['f_certified_prior_hearing_material_present'])
- Note: Current index did not yield reliable hearing/opportunity artifacts; certified appearance/hearing records are still required. Candidate references: Collateral Estoppel/drafts/final_filing_set/06_oregon_authority_table_final.md; Collateral Estoppel/evidence_notes/formal_case_state_dashboard_2026-04-07.md; Collateral Estoppel/evidence_notes/element_audit_layer_note_2026-04-07.md; Collateral Estoppel/evidence_notes/solomon_order_completeness_checklist.md

## Mode: strict
- Active rules: 42
- Unresolved rules: 6
- Inactive rules: 4
- Party deontic state:
- case:26PR00641: O=3, P=3, F=0
- case:guardianship_collateral_estoppel: O=6, P=12, F=0
- org:hacc: O=3, P=0, F=0
- person:benjamin_barber: O=1, P=2, F=0
- person:solomon: O=5, P=0, F=7
- Active rule activation-date estimates:
- r40_benjamin_permitted_act_as_gal_under_signed_eppdapa_order: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r41_solomon_obligated_follow_petitioner_guardian_or_conservator_instructions: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r42_solomon_forbidden_disobey_guardian_instruction_term_after_appearance: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r4_solomon_forbidden_abuse_contact_property_control: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window, post_notice, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r4b_solomon_forbidden_enter_residence: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window, post_notice, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r5b_solomon_obligated_seek_hearing_or_comply: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r5c_solomon_forbidden_self_help_noncooperation: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r6_hacc_obligated_document_authority_chain_for_lease_change: 2026-01-12 [window 2026-01-01 -> 2026-01-12; tags: multi_date_window, post_hacc_lease_change; intervals: ti_hacc_lease_change_sequence]
- r6b_hacc_obligated_document_lease_basis: 2026-01-12 [window 2026-01-01 -> 2026-01-12; tags: multi_date_window, post_hacc_lease_change; intervals: ti_hacc_lease_change_sequence]
- r6c_solomon_interference_not_proved_by_named_hacc_notice_gap: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: ti_restraining_order_effective_period]
- r6d_case_obligated_treat_prior_appointment_as_hypothesis_only: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: none; intervals: ti_restraining_order_effective_period]
- r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r8_solomon_notice_ack_triggers_court_relief_path: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r9_solomon_wait_for_service_conflicts_with_no_further_service: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r10_solomon_noncooperation_statement_conflicts_with_effective_order: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r11_solomon_already_have_order_statement_supports_notice: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r13_solomon_judge_overturn_statement_triggers_motion_path: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling: 2026-03-26 [window 2026-03-26 -> 2026-03-26; tags: none; intervals: none]
- r15_benjamin_permitted_serve_subpoena_packets: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_exhibit_r_compelled_production_track]
- r16_benjamin_obligated_track_service_and_deadlines: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r20_case_permitted_treat_enforcement_path_as_pending_pre_service: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: none; intervals: ti_restraining_order_effective_period]
- r21_case_obligated_resolve_actor_assignment_conflict: 2026-04-09 [window 2026-04-09 -> 2026-04-09; tags: none; intervals: ti_restraining_order_effective_period]
- r23_case_permitted_initiate_remedial_contempt_path: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r23b_case_permitted_seek_court_direction_on_service_channel_if_evasion_pattern: 2026-04-07 [window 2025-11-17 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r23c_case_permitted_rely_on_court_notice_modification_order_if_documented: 2025-11-20 [window 2025-11-20 -> 2025-11-20; tags: none; intervals: ti_restraining_order_effective_period]
- r23d_case_permitted_characterize_counsel_contact_as_same_matter_notice_channel_for_collateral_estoppel_briefing: 2026-04-04 [window 2026-04-03 -> 2026-04-04; tags: multi_date_window; intervals: ti_restraining_order_effective_period, ti_probate_notice_objection_window]
- r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved: 2026-04-07 [window 2026-01-01 -> 2026-04-07; tags: multi_date_window, post_hacc_lease_change; intervals: ti_restraining_order_effective_period]
- r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: ti_probate_notice_objection_window]
- r29_case_obligated_preserve_notice_and_objection_window: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r30_case_obligated_schedule_hearing_on_presented_objection: 2026-04-07 [window 2026-04-05 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period, ti_probate_notice_objection_window]
- r33_case_permitted_request_special_advocate_or_gal_under_chapter_125: 2026-04-09 [window 2026-03-31 -> 2026-04-09; tags: multi_date_window; intervals: ti_probate_notice_objection_window]
- r34_case_obligated_check_clackamas_probate_slr_requirements_before_filing: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: none]
- r35_case_obligated_treat_issue_preclusion_as_provisional_until_certified_prior_record_staged: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r36_case_obligated_complete_issue_preclusion_element_mapping_before_merits_reliance: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: none]
- r37_case_obligated_add_targeted_record_citations_for_finality_and_full_fair_elements: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: none]
- r38_case_obligated_qualify_overclaim_language_until_elements_are_proved: 2026-04-09 [window 2026-04-09 -> 2026-04-09; tags: none; intervals: ti_restraining_order_effective_period]
- r39_case_permitted_seek_targeted_nonparty_production_for_missing_issue_preclusion_elements: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_exhibit_r_compelled_production_track]

## Mode: inclusive
- Active rules: 43
- Unresolved rules: 5
- Inactive rules: 4
- Party deontic state:
- case:26PR00641: O=3, P=3, F=0
- case:guardianship_collateral_estoppel: O=6, P=13, F=0
- org:hacc: O=3, P=0, F=0
- person:benjamin_barber: O=1, P=2, F=0
- person:solomon: O=5, P=0, F=7
- Active rule activation-date estimates:
- r40_benjamin_permitted_act_as_gal_under_signed_eppdapa_order: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r41_solomon_obligated_follow_petitioner_guardian_or_conservator_instructions: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r42_solomon_forbidden_disobey_guardian_instruction_term_after_appearance: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r4_solomon_forbidden_abuse_contact_property_control: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window, post_notice, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r4b_solomon_forbidden_enter_residence: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window, post_notice, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r5b_solomon_obligated_seek_hearing_or_comply: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r5c_solomon_forbidden_self_help_noncooperation: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r6_hacc_obligated_document_authority_chain_for_lease_change: 2026-01-12 [window 2026-01-01 -> 2026-01-12; tags: multi_date_window, post_hacc_lease_change; intervals: ti_hacc_lease_change_sequence]
- r6b_hacc_obligated_document_lease_basis: 2026-01-12 [window 2026-01-01 -> 2026-01-12; tags: multi_date_window, post_hacc_lease_change; intervals: ti_hacc_lease_change_sequence]
- r6c_solomon_interference_not_proved_by_named_hacc_notice_gap: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: ti_restraining_order_effective_period]
- r6d_case_obligated_treat_prior_appointment_as_hypothesis_only: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: none; intervals: ti_restraining_order_effective_period]
- r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r8_solomon_notice_ack_triggers_court_relief_path: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r9_solomon_wait_for_service_conflicts_with_no_further_service: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r10_solomon_noncooperation_statement_conflicts_with_effective_order: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r11_solomon_already_have_order_statement_supports_notice: 2025-11-20 [window 2025-11-17 -> 2025-11-20; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r13_solomon_judge_overturn_statement_triggers_motion_path: 2026-03-10 [window 2025-11-20 -> 2026-03-10; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling: 2026-03-26 [window 2026-03-26 -> 2026-03-26; tags: none; intervals: none]
- r15_benjamin_permitted_serve_subpoena_packets: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_exhibit_r_compelled_production_track]
- r16_benjamin_obligated_track_service_and_deadlines: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r20_case_permitted_treat_enforcement_path_as_pending_pre_service: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: none; intervals: ti_restraining_order_effective_period]
- r21_case_obligated_resolve_actor_assignment_conflict: 2026-04-09 [window 2026-04-09 -> 2026-04-09; tags: none; intervals: ti_restraining_order_effective_period]
- r23_case_permitted_initiate_remedial_contempt_path: 2026-04-07 [window 2025-11-20 -> 2026-04-07; tags: multi_date_window, post_notice, post_order_effective, within_estimated_order_lifespan; intervals: ti_restraining_order_effective_period]
- r23b_case_permitted_seek_court_direction_on_service_channel_if_evasion_pattern: 2026-04-07 [window 2025-11-17 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r23c_case_permitted_rely_on_court_notice_modification_order_if_documented: 2025-11-20 [window 2025-11-20 -> 2025-11-20; tags: none; intervals: ti_restraining_order_effective_period]
- r23d_case_permitted_characterize_counsel_contact_as_same_matter_notice_channel_for_collateral_estoppel_briefing: 2026-04-04 [window 2026-04-03 -> 2026-04-04; tags: multi_date_window; intervals: ti_restraining_order_effective_period, ti_probate_notice_objection_window]
- r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: 2026-04-07 [window 2026-03-10 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved: 2026-04-07 [window 2026-01-01 -> 2026-04-07; tags: multi_date_window, post_hacc_lease_change; intervals: ti_restraining_order_effective_period]
- r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46: 2026-04-07 [window 2026-04-07 -> 2026-04-07; tags: post_hacc_lease_change; intervals: none]
- r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: ti_probate_notice_objection_window]
- r29_case_obligated_preserve_notice_and_objection_window: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r30_case_obligated_schedule_hearing_on_presented_objection: 2026-04-07 [window 2026-04-05 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window, objection_window_or_later; intervals: ti_probate_notice_objection_window]
- r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: ti_restraining_order_effective_period, ti_probate_notice_objection_window]
- r33_case_permitted_request_special_advocate_or_gal_under_chapter_125: 2026-04-09 [window 2026-03-31 -> 2026-04-09; tags: multi_date_window; intervals: ti_probate_notice_objection_window]
- r34_case_obligated_check_clackamas_probate_slr_requirements_before_filing: 2026-04-07 [window 2026-03-31 -> 2026-04-07; tags: multi_date_window; intervals: none]
- r35_case_obligated_treat_issue_preclusion_as_provisional_until_certified_prior_record_staged: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_restraining_order_effective_period]
- r36_case_obligated_complete_issue_preclusion_element_mapping_before_merits_reliance: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: none]
- r37_case_obligated_add_targeted_record_citations_for_finality_and_full_fair_elements: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: none]
- r38_case_obligated_qualify_overclaim_language_until_elements_are_proved: 2026-04-09 [window 2026-04-09 -> 2026-04-09; tags: none; intervals: ti_restraining_order_effective_period]
- r39_case_permitted_seek_targeted_nonparty_production_for_missing_issue_preclusion_elements: 2026-04-09 [window 2026-04-07 -> 2026-04-09; tags: multi_date_window; intervals: ti_exhibit_r_compelled_production_track]

## Litigation Matrix Snapshot
- strict: 5 parties with active O/P/F states
- inclusive: 5 parties with active O/P/F states

