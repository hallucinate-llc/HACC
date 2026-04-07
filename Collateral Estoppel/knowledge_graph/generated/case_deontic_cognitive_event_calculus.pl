% Deontic Cognitive Event Calculus program
% Fluents: notice/2, valid_order/1, interference/2, preclusion_applies/1

% Event declarations
event(file_petition(solomon, case_26PR00641)).
event(issue_notice(case_26PR00641, jane_cortez)).
event(grant_restraining_order(eppdapa_order, jane_cortez, solomon)).
event(assert_prior_appointment(jane_cortez, benjamin_barber)).
event(assert_interference(benjamin_barber, hacc_housing_contract)).
event(assert_refiled_barred_issue(solomon, guardianship_authority)).

% Initiates / terminates
initiates(grant_restraining_order(Order, _, _), valid_order(Order), T).
initiates(issue_notice(Case, Person), notice(Person, Case), T).
initiates(assert_interference(Person, Process), interference(Person, Process), T).
initiates(assert_prior_appointment(Jane, Ben), prior_appointment(Jane, Ben), T).
initiates(assert_refiled_barred_issue(solomon, Issue), relitigates(solomon, Issue), T).

% Cognitive state
holdsAt(knows(solomon, valid_order(eppdapa_order)), T) :- holdsAt(notice(solomon, case_26PR00641), T).

% Truth anchors for model facts
fact_true('f_petition_exists').
fact_true('f_notice_to_respondent').
fact_true('f_respondent_objection_form_present').
fact_true('f_petition_claims_no_prior_guardian').
fact_true('f_prior_appointment_source_order_not_found').
fact_true('f_client_prior_appointment').
fact_true('f_client_benjamin_avoided_service').
fact_true('f_client_benjamin_order_disregard').
fact_true('f_client_benjamin_housing_interference').
fact_true('f_solomon_actual_notice_on_2025_11_17').
fact_true('f_solomon_order_filed_on_2025_11_19').
fact_true('f_client_solomon_failed_appearance').
fact_true('f_client_solomon_barred_refile').
fact_true('f_restraining_order_granted').
fact_true('f_restraining_order_in_effect').
fact_true('f_restraining_order_no_further_service_needed').
fact_true('f_restraining_order_contact_restrictions').
fact_true('f_restraining_order_residence_restrictions').
fact_true('f_restraining_order_property_restrictions').
fact_true('f_restraining_order_one_year_duration').
fact_true('f_solomon_noncooperation_statement').
fact_true('f_solomon_service_position_statement').
fact_true('f_hacc_lease_adjustment_effective_2026_01_01').
fact_true('f_hacc_removed_benjamin_effective_2026_01_01').
fact_true('f_hacc_internal_review_claimed').
fact_true('f_hacc_court_documentation_basis_claimed').
fact_true('f_hacc_actor_identification_record_not_found_locally').
fact_true('f_hacc_exhibit_r_requires_compelled_production').
fact_true('f_january_2026_hacc_removed_benjamin_restored_restrained_party').
fact_true('f_solomon_interference_with_hacc_lease_theory').
fact_true('f_hacc_named_notice_to_solomon_order_not_found').
fact_true('f_ashley_ferron_case_26P000432_denied').
fact_true('f_ashley_ferron_case_26P000433_denied').
fact_true('f_julio_order_case_25PO11318_exists').
fact_true('f_hacc_process_exists').
fact_true('f_collateral_estoppel_candidate').
fact_true('f_actor_assignment_conflict_benjamin_vs_solomon_interference').
fact_true('f_subpoena_workflow_components_staged').
fact_true('f_or_joined_search_protocol_defined').
fact_true('f_authority_table_placeholders_unresolved').
fact_true('f_authority_ors_33_055_remedial_contempt_procedure').
fact_true('f_authority_ors_33_075_compel_appearance').
fact_true('f_authority_ors_33_105_remedial_sanctions').
fact_true('f_authority_orcp_17_improper_purpose_and_support').
fact_true('f_authority_orcp_46_discovery_sanctions').
fact_true('f_authority_orcp_55_subpoena_obedience').
fact_true('f_authority_ors_125_050_protective_orcp_oec').
fact_true('f_authority_ors_125_060_notice_recipients').
fact_true('f_authority_ors_125_065_notice_manner_and_timing').
fact_true('f_authority_ors_125_075_objections').
fact_true('f_authority_ors_125_080_hearing_and_counsel').
fact_true('f_authority_ors_125_120_protected_person_special_advocate').
fact_true('f_authority_orcp_9_service_of_later_filed_papers').
fact_true('f_authority_orcp_10_time_computation').
fact_true('f_authority_issue_preclusion_elements_official_oregon_cases').
fact_true('f_authority_issue_preclusion_requires_prior_separate_proceeding').
fact_true('f_feed_ev_hacc_notice_brother_calls_after_granted_order').
fact_true('f_feed_ev_hacc_notice_third_party_contact_with_restrained_person').
fact_true('f_feed_ev_msg_claim_restraining_order_filed').
fact_true('f_feed_ev_msg_claim_restraining_order_granted').
fact_true('f_feed_ev_msg_request_service_address').
fact_true('f_feed_ev_solomon_ack_already_have_order').
fact_true('f_feed_ev_solomon_ack_heard_restraining_order').
fact_true('f_feed_ev_solomon_arrival_statement_for_pickup').
fact_true('f_feed_ev_solomon_conditionally_cancel_pickup').
fact_true('f_feed_ev_solomon_entrapment_statement').
fact_true('f_feed_ev_solomon_identified_aps_contact').
fact_true('f_feed_ev_solomon_judge_overturn_statement').
fact_true('f_feed_ev_solomon_not_incentivized_eml').
fact_true('f_feed_ev_solomon_not_incentivized_statement').
fact_true('f_feed_ev_solomon_order_not_in_effect_statement').
fact_true('f_feed_ev_solomon_pickup_plan_for_jane').
fact_true('f_feed_ev_solomon_provided_aps_reference_number').
fact_true('f_feed_ev_solomon_wait_for_service_eml').
fact_true('f_feed_ev_solomon_wait_for_service_statement').
fact_true('f_repo_solomon_mention_1').
fact_true('f_repo_solomon_mention_2').
fact_true('f_repo_solomon_mention_3').
fact_true('f_repo_solomon_mention_4').
fact_true('f_repo_solomon_mention_5').
fact_true('f_repo_solomon_mention_6').
fact_true('f_repo_solomon_mention_7').
fact_true('f_repo_solomon_mention_8').
fact_true('f_repo_solomon_mention_9').
fact_true('f_repo_solomon_mention_10').
fact_true('f_repo_solomon_mention_11').
fact_true('f_repo_solomon_mention_12').
fact_true('f_repo_solomon_mention_13').
fact_true('f_repo_solomon_mention_14').
fact_true('f_repo_solomon_mention_15').
fact_true('f_repo_solomon_mention_16').
fact_true('f_repo_solomon_mention_17').
fact_true('f_repo_solomon_mention_18').
fact_true('f_repo_solomon_mention_19').
fact_true('f_repo_solomon_mention_20').
fact_true('f_repo_solomon_mention_21').
fact_true('f_repo_solomon_mention_22').
fact_true('f_repo_solomon_mention_23').
fact_true('f_repo_solomon_mention_24').
fact_true('f_repo_solomon_mention_25').
fact_true('f_repo_solomon_mention_26').
fact_true('f_repo_solomon_mention_27').
fact_true('f_repo_solomon_mention_28').
fact_true('f_repo_solomon_mention_29').
fact_true('f_repo_solomon_mention_30').
fact_true('f_repo_solomon_mention_31').
fact_true('f_repo_solomon_mention_32').
fact_true('f_repo_solomon_mention_33').
fact_true('f_repo_solomon_mention_34').
fact_true('f_repo_solomon_mention_35').
fact_true('f_repo_solomon_mention_36').
fact_true('f_repo_solomon_mention_37').
fact_true('f_repo_solomon_mention_38').
fact_true('f_repo_solomon_mention_39').
fact_true('f_repo_solomon_mention_40').
fact_true('f_repo_solomon_mention_41').
fact_true('f_repo_solomon_mention_42').
fact_true('f_repo_solomon_mention_43').
fact_true('f_repo_solomon_mention_44').
fact_true('f_repo_solomon_mention_45').
fact_true('f_repo_solomon_mention_46').
fact_true('f_repo_solomon_mention_47').
fact_true('f_repo_solomon_mention_48').
fact_true('f_repo_solomon_mention_49').
fact_true('f_repo_solomon_mention_50').
fact_true('f_repo_solomon_mention_51').
fact_true('f_repo_solomon_mention_52').
fact_true('f_repo_solomon_mention_53').
fact_true('f_repo_solomon_mention_54').
fact_true('f_repo_solomon_mention_55').
fact_true('f_repo_solomon_mention_56').
fact_true('f_repo_solomon_mention_57').
fact_true('f_repo_solomon_mention_58').
fact_true('f_repo_solomon_mention_59').
fact_true('f_repo_solomon_mention_60').
fact_true('f_repo_solomon_mention_61').
fact_true('f_repo_solomon_mention_62').
fact_true('f_repo_solomon_mention_63').
fact_true('f_repo_solomon_mention_64').
fact_true('f_repo_solomon_mention_65').
fact_true('f_repo_solomon_mention_66').
fact_true('f_repo_solomon_mention_67').
fact_true('f_repo_solomon_mention_68').
fact_true('f_repo_solomon_mention_69').
fact_true('f_repo_solomon_mention_70').
fact_true('f_repo_solomon_mention_71').
fact_true('f_repo_solomon_mention_72').
fact_true('f_repo_solomon_mention_73').
fact_true('f_repo_solomon_mention_74').
fact_true('f_repo_solomon_mention_75').
fact_true('f_repo_solomon_mention_76').
fact_true('f_repo_solomon_mention_77').
fact_true('f_repo_solomon_mention_78').
fact_true('f_repo_solomon_mention_79').
fact_true('f_repo_solomon_mention_80').
fact_true('f_repo_solomon_mention_81').
fact_true('f_repo_solomon_mention_82').
fact_true('f_repo_solomon_mention_83').
fact_true('f_repo_solomon_mention_84').
fact_true('f_repo_solomon_mention_85').
fact_true('f_repo_solomon_mention_86').
fact_true('f_repo_solomon_mention_87').
fact_true('f_repo_solomon_mention_88').
fact_true('f_repo_solomon_mention_89').
fact_true('f_repo_solomon_mention_90').
fact_true('f_repo_solomon_mention_91').
fact_true('f_repo_solomon_mention_92').
fact_true('f_repo_solomon_mention_93').
fact_true('f_repo_solomon_mention_94').
fact_true('f_repo_solomon_mention_95').
fact_true('f_repo_solomon_mention_96').
fact_true('f_repo_solomon_mention_97').
fact_true('f_repo_solomon_mention_98').
fact_true('f_repo_solomon_mention_99').
fact_true('f_repo_solomon_mention_100').
fact_true('f_repo_solomon_mention_101').
fact_true('f_repo_solomon_mention_102').
fact_true('f_repo_solomon_mention_103').
fact_true('f_repo_solomon_mention_104').
fact_true('f_repo_solomon_mention_105').
fact_true('f_repo_solomon_mention_106').
fact_true('f_repo_solomon_mention_107').
fact_true('f_repo_solomon_mention_108').
fact_true('f_repo_solomon_mention_109').
fact_true('f_repo_solomon_mention_110').
fact_true('f_repo_solomon_mention_111').
fact_true('f_repo_solomon_mention_112').
fact_true('f_repo_solomon_mention_113').
fact_true('f_repo_solomon_mention_114').
fact_true('f_repo_solomon_mention_115').
fact_true('f_repo_solomon_mention_116').
fact_true('f_repo_solomon_mention_117').
fact_true('f_repo_solomon_mention_118').
fact_true('f_repo_solomon_mention_119').
fact_true('f_repo_solomon_mention_120').
fact_true('f_repo_solomon_mention_121').
fact_true('f_repo_solomon_mention_122').
fact_true('f_repo_solomon_mention_123').
fact_true('f_repo_solomon_mention_124').
fact_true('f_repo_solomon_mention_125').
fact_true('f_repo_solomon_mention_126').
fact_true('f_repo_solomon_mention_127').
fact_true('f_repo_solomon_mention_128').
fact_true('f_repo_solomon_mention_129').
fact_true('f_repo_solomon_mention_130').
fact_true('f_repo_solomon_mention_131').
fact_true('f_repo_solomon_mention_132').
fact_true('f_repo_solomon_mention_133').
fact_true('f_repo_solomon_mention_134').
fact_true('f_repo_solomon_mention_135').
fact_true('f_repo_solomon_mention_136').
fact_true('f_repo_solomon_mention_137').
fact_true('f_repo_solomon_mention_138').
fact_true('f_repo_solomon_mention_139').
fact_true('f_repo_solomon_mention_140').
fact_true('f_repo_solomon_mention_141').
fact_true('f_repo_solomon_mention_142').
fact_true('f_repo_solomon_mention_143').
fact_true('f_repo_solomon_mention_144').
fact_true('f_repo_solomon_mention_145').
fact_true('f_repo_solomon_mention_146').
fact_true('f_repo_solomon_mention_147').
fact_true('f_repo_solomon_mention_148').
fact_true('f_repo_solomon_mention_149').
fact_true('f_repo_solomon_mention_150').
fact_true('f_repo_solomon_mention_151').
fact_true('f_repo_solomon_mention_152').
fact_true('f_repo_solomon_mention_153').
fact_true('f_repo_solomon_mention_154').
fact_true('f_repo_solomon_mention_155').
fact_true('f_repo_solomon_mention_156').
fact_true('f_repo_solomon_mention_157').
fact_true('f_repo_solomon_mention_158').
fact_true('f_repo_solomon_mention_159').
fact_true('f_repo_solomon_mention_160').
fact_true('f_repo_solomon_mention_161').
fact_true('f_repo_solomon_mention_162').
fact_true('f_repo_solomon_mention_163').
fact_true('f_repo_solomon_mention_164').
fact_true('f_repo_solomon_mention_165').
fact_true('f_repo_solomon_mention_166').
fact_true('f_repo_solomon_mention_167').
fact_true('f_repo_solomon_mention_168').
fact_true('f_repo_solomon_mention_169').
fact_true('f_repo_solomon_mention_170').
fact_true('f_repo_solomon_mention_171').
fact_true('f_repo_solomon_mention_172').
fact_true('f_repo_solomon_mention_173').
fact_true('f_repo_solomon_mention_174').
fact_true('f_repo_solomon_mention_175').
fact_true('f_repo_solomon_mention_176').
fact_true('f_repo_solomon_mention_177').
fact_true('f_repo_solomon_mention_178').
fact_true('f_repo_solomon_mention_179').
fact_true('f_repo_solomon_mention_180').
fact_true('f_repo_solomon_mention_181').
fact_true('f_repo_solomon_mention_182').
fact_true('f_repo_solomon_mention_183').
fact_true('f_repo_solomon_mention_184').
fact_true('f_repo_solomon_mention_185').
fact_true('f_repo_solomon_mention_186').
fact_true('f_repo_solomon_mention_187').
fact_true('f_repo_solomon_mention_188').
fact_true('f_repo_solomon_mention_189').
fact_true('f_repo_solomon_mention_190').
fact_true('f_repo_solomon_mention_191').
fact_true('f_repo_solomon_mention_192').
fact_true('f_repo_solomon_mention_193').
fact_true('f_repo_solomon_mention_194').
fact_true('f_repo_solomon_mention_195').
fact_true('f_repo_solomon_mention_196').
fact_true('f_repo_solomon_mention_197').
fact_true('f_repo_solomon_mention_198').
fact_true('f_repo_solomon_mention_199').
fact_true('f_repo_solomon_mention_200').
fact_true('f_repo_solomon_mention_201').
fact_true('f_repo_solomon_mention_202').
fact_true('f_repo_solomon_mention_203').
fact_true('f_repo_solomon_mention_204').
fact_true('f_repo_solomon_mention_205').
fact_true('f_repo_solomon_mention_206').
fact_true('f_repo_solomon_mention_207').
fact_true('f_repo_solomon_mention_208').
fact_true('f_repo_solomon_mention_209').
fact_true('f_repo_solomon_mention_210').
fact_true('f_repo_solomon_mention_211').
fact_true('f_repo_solomon_mention_212').
fact_true('f_repo_solomon_mention_213').
fact_true('f_repo_solomon_mention_214').
fact_true('f_repo_solomon_mention_215').
fact_true('f_repo_solomon_mention_216').
fact_true('f_repo_solomon_mention_217').
fact_true('f_repo_solomon_mention_218').
fact_true('f_repo_solomon_mention_219').
fact_true('f_repo_solomon_mention_220').
fact_true('f_repo_solomon_mention_221').
fact_true('f_repo_solomon_mention_222').
fact_true('f_repo_solomon_mention_223').
fact_true('f_repo_solomon_mention_224').
fact_true('f_repo_solomon_mention_225').
fact_true('f_repo_solomon_mention_226').
fact_true('f_repo_solomon_mention_227').
fact_true('f_repo_solomon_mention_228').
fact_true('f_repo_solomon_mention_229').
fact_true('f_repo_solomon_mention_230').
fact_true('f_repo_solomon_mention_231').
fact_true('f_repo_solomon_mention_232').
fact_true('f_repo_solomon_mention_233').
fact_true('f_repo_solomon_mention_234').
fact_true('f_repo_solomon_mention_235').
fact_true('f_repo_solomon_mention_236').
fact_true('f_repo_solomon_mention_237').
fact_true('f_repo_solomon_mention_238').
fact_true('f_repo_solomon_mention_239').
fact_true('f_repo_solomon_mention_240').
fact_true('f_repo_solomon_mention_241').
fact_true('f_repo_solomon_mention_242').
fact_true('f_repo_solomon_mention_243').
fact_true('f_repo_solomon_mention_244').
fact_true('f_repo_solomon_mention_245').
fact_true('f_repo_solomon_mention_246').
fact_true('f_repo_solomon_mention_247').
fact_true('f_repo_solomon_mention_248').
fact_true('f_repo_solomon_mention_249').
fact_true('f_repo_solomon_mention_250').
fact_true('f_repo_solomon_mention_251').
fact_true('f_repo_solomon_mention_252').
fact_true('f_repo_solomon_mention_253').
fact_true('f_repo_solomon_mention_254').
fact_true('f_repo_solomon_mention_255').
fact_true('f_repo_solomon_mention_256').
fact_true('f_repo_solomon_mention_257').
fact_true('f_repo_solomon_mention_258').
fact_true('f_repo_solomon_mention_259').
fact_true('f_repo_solomon_mention_260').
fact_true('f_repo_solomon_mention_261').
fact_true('f_repo_solomon_mention_262').
fact_true('f_repo_solomon_mention_263').
fact_true('f_repo_solomon_mention_264').
fact_true('f_repo_solomon_mention_265').
fact_true('f_repo_solomon_mention_266').
fact_true('f_repo_solomon_mention_267').
fact_true('f_repo_solomon_mention_268').
fact_true('f_repo_solomon_mention_269').
fact_true('f_repo_solomon_mention_270').
fact_true('f_repo_solomon_mention_271').
fact_true('f_repo_solomon_mention_272').
fact_true('f_repo_solomon_mention_273').
fact_true('f_repo_solomon_mention_274').
fact_true('f_repo_solomon_mention_275').
fact_true('f_repo_solomon_mention_276').
fact_true('f_repo_solomon_mention_277').
fact_true('f_repo_solomon_mention_278').
fact_true('f_repo_solomon_mention_279').
fact_true('f_repo_solomon_mention_280').
fact_true('f_repo_solomon_mention_281').
fact_true('f_repo_solomon_mention_282').
fact_true('f_repo_solomon_mention_283').
fact_true('f_repo_solomon_mention_284').
fact_true('f_repo_solomon_mention_285').
fact_true('f_repo_solomon_mention_286').
fact_true('f_repo_solomon_mention_287').
fact_true('f_repo_solomon_mention_288').
fact_true('f_repo_solomon_mention_289').
fact_true('f_repo_solomon_mention_290').
fact_true('f_repo_solomon_mention_291').
fact_true('f_repo_solomon_mention_292').
fact_true('f_active_service_log_initialized').
fact_true('f_subpoena_recipients_ready_to_serve').
fact_true('f_subpoena_pre_service_phase_only').

% Rule-level derivations from fact truth
rule_holds('r1_guardian_permission_if_prior_appointment') :- fact_true('f_client_prior_appointment').
rule_holds('r2_noninterference_prohibition_for_benjamin') :- fact_true('f_client_prior_appointment'), fact_true('f_client_benjamin_housing_interference').
rule_holds('r3_benjamin_obligation_comply_or_seek_relief') :- fact_true('f_client_prior_appointment'), fact_true('f_client_benjamin_order_disregard').
rule_holds('r4_solomon_forbidden_abuse_contact_property_control') :- fact_true('f_solomon_actual_notice_on_2025_11_17'), fact_true('f_restraining_order_granted'), fact_true('f_restraining_order_in_effect'), fact_true('f_restraining_order_contact_restrictions'), fact_true('f_restraining_order_property_restrictions').
rule_holds('r4b_solomon_forbidden_enter_residence') :- fact_true('f_solomon_actual_notice_on_2025_11_17'), fact_true('f_restraining_order_granted'), fact_true('f_restraining_order_residence_restrictions').
rule_holds('r5_solomon_obligated_appear_and_answer') :- fact_true('f_restraining_order_no_further_service_needed'), fact_true('f_client_solomon_failed_appearance').
rule_holds('r5b_solomon_obligated_seek_hearing_or_comply') :- fact_true('f_restraining_order_granted'), fact_true('f_restraining_order_in_effect'), fact_true('f_solomon_service_position_statement').
rule_holds('r5c_solomon_forbidden_self_help_noncooperation') :- fact_true('f_restraining_order_granted'), fact_true('f_restraining_order_in_effect'), fact_true('f_solomon_noncooperation_statement').
rule_holds('r6_hacc_obligated_document_authority_chain_for_lease_change') :- fact_true('f_hacc_removed_benjamin_effective_2026_01_01'), fact_true('f_hacc_internal_review_claimed'), fact_true('f_hacc_court_documentation_basis_claimed').
rule_holds('r6b_hacc_obligated_document_lease_basis') :- fact_true('f_hacc_lease_adjustment_effective_2026_01_01'), fact_true('f_hacc_removed_benjamin_effective_2026_01_01').
rule_holds('r6c_solomon_interference_not_proved_by_named_hacc_notice_gap') :- fact_true('f_hacc_named_notice_to_solomon_order_not_found').
rule_holds('r6d_case_obligated_treat_prior_appointment_as_hypothesis_only') :- fact_true('f_prior_appointment_source_order_not_found').
rule_holds('r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain') :- fact_true('f_hacc_actor_identification_record_not_found_locally'), fact_true('f_hacc_exhibit_r_requires_compelled_production').
rule_holds('r7_solomon_forbidden_refile_precluded_issue') :- fact_true('f_authority_issue_preclusion_elements_official_oregon_cases'), fact_true('f_authority_issue_preclusion_requires_prior_separate_proceeding'), fact_true('f_collateral_estoppel_candidate'), fact_true('f_client_solomon_barred_refile').
rule_holds('r8_solomon_notice_ack_triggers_court_relief_path') :- fact_true('f_feed_ev_solomon_ack_heard_restraining_order'), fact_true('f_restraining_order_in_effect').
rule_holds('r9_solomon_wait_for_service_conflicts_with_no_further_service') :- fact_true('f_feed_ev_solomon_wait_for_service_statement'), fact_true('f_restraining_order_no_further_service_needed').
rule_holds('r10_solomon_noncooperation_statement_conflicts_with_effective_order') :- fact_true('f_feed_ev_solomon_not_incentivized_statement'), fact_true('f_restraining_order_in_effect').
rule_holds('r11_solomon_already_have_order_statement_supports_notice') :- fact_true('f_feed_ev_solomon_ack_already_have_order'), fact_true('f_restraining_order_in_effect').
rule_holds('r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order') :- fact_true('f_feed_ev_solomon_order_not_in_effect_statement'), fact_true('f_restraining_order_in_effect').
rule_holds('r13_solomon_judge_overturn_statement_triggers_motion_path') :- fact_true('f_feed_ev_solomon_judge_overturn_statement'), fact_true('f_restraining_order_in_effect').
rule_holds('r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling') :- fact_true('f_feed_ev_hacc_notice_brother_calls_after_granted_order'), fact_true('f_feed_ev_hacc_notice_third_party_contact_with_restrained_person').
rule_holds('r15_benjamin_permitted_serve_subpoena_packets') :- fact_true('f_subpoena_workflow_components_staged'), fact_true('f_subpoena_recipients_ready_to_serve').
rule_holds('r16_benjamin_obligated_track_service_and_deadlines') :- fact_true('f_active_service_log_initialized'), fact_true('f_subpoena_workflow_components_staged').
rule_holds('r17_responding_custodian_obligated_execute_or_query_protocol_upon_service') :- fact_true('f_subpoena_service_completed_any'), fact_true('f_or_joined_search_protocol_defined').
rule_holds('r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response') :- fact_true('f_subpoena_response_incomplete_any'), fact_true('f_subpoena_workflow_components_staged').
rule_holds('r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage') :- fact_true('f_deficiency_notice_sent_any'), fact_true('f_subpoena_workflow_components_staged').
rule_holds('r20_case_permitted_treat_enforcement_path_as_pending_pre_service') :- fact_true('f_subpoena_pre_service_phase_only').
rule_holds('r21_case_obligated_resolve_actor_assignment_conflict') :- fact_true('f_actor_assignment_conflict_benjamin_vs_solomon_interference').
rule_holds('r22_case_obligated_finalize_authority_citations_before_filing') :- fact_true('f_authority_table_placeholders_unresolved').
rule_holds('r23_case_permitted_initiate_remedial_contempt_path') :- fact_true('f_authority_ors_33_055_remedial_contempt_procedure'), fact_true('f_restraining_order_in_effect'), fact_true('f_solomon_service_position_statement').
rule_holds('r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved') :- fact_true('f_authority_ors_33_075_compel_appearance'), fact_true('f_client_solomon_failed_appearance').
rule_holds('r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved') :- fact_true('f_authority_ors_33_105_remedial_sanctions'), fact_true('f_hacc_removed_benjamin_effective_2026_01_01').
rule_holds('r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown') :- fact_true('f_authority_orcp_17_improper_purpose_and_support'), fact_true('f_hacc_named_notice_to_solomon_order_not_found').
rule_holds('r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46') :- fact_true('f_authority_orcp_55_subpoena_obedience'), fact_true('f_authority_orcp_46_discovery_sanctions'), fact_true('f_hacc_exhibit_r_requires_compelled_production').
rule_holds('r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding') :- fact_true('f_authority_ors_125_050_protective_orcp_oec'), fact_true('f_petition_exists').
rule_holds('r29_case_obligated_preserve_notice_and_objection_window') :- fact_true('f_authority_ors_125_060_notice_recipients'), fact_true('f_authority_ors_125_065_notice_manner_and_timing'), fact_true('f_notice_to_respondent').
rule_holds('r30_case_obligated_schedule_hearing_on_presented_objection') :- fact_true('f_authority_ors_125_075_objections'), fact_true('f_authority_ors_125_080_hearing_and_counsel'), fact_true('f_respondent_objection_form_present').
rule_holds('r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel') :- fact_true('f_authority_ors_125_080_hearing_and_counsel'), fact_true('f_notice_to_respondent').
rule_holds('r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines') :- fact_true('f_authority_orcp_9_service_of_later_filed_papers'), fact_true('f_authority_orcp_10_time_computation'), fact_true('f_petition_exists').

% Deontic conclusions generated for all rules
deontic_conclusion('r1_guardian_permission_if_prior_appointment', 'P', 'person:benjamin_barber', 'act_within_valid_guardian_scope', 'person:jane_cortez') :- rule_holds('r1_guardian_permission_if_prior_appointment').
deontic_conclusion('r2_noninterference_prohibition_for_benjamin', 'F', 'person:benjamin_barber', 'interfere_with_guardian_or_housing_process', 'process:hacc_housing_contract') :- rule_holds('r2_noninterference_prohibition_for_benjamin').
deontic_conclusion('r3_benjamin_obligation_comply_or_seek_relief', 'O', 'person:benjamin_barber', 'comply_with_order_or_seek_relief', 'order:prior_guardianship_order') :- rule_holds('r3_benjamin_obligation_comply_or_seek_relief').
deontic_conclusion('r4_solomon_forbidden_abuse_contact_property_control', 'F', 'person:solomon', 'abuse_contact_or_control_property', 'person:jane_cortez') :- rule_holds('r4_solomon_forbidden_abuse_contact_property_control').
deontic_conclusion('r4b_solomon_forbidden_enter_residence', 'F', 'person:solomon', 'enter_or_remain_at_petitioner_residence', 'location:10043_se_32nd_ave') :- rule_holds('r4b_solomon_forbidden_enter_residence').
deontic_conclusion('r5_solomon_obligated_appear_and_answer', 'O', 'person:solomon', 'appear_and_answer_show_cause', 'proceeding:related_order_hearing') :- rule_holds('r5_solomon_obligated_appear_and_answer').
deontic_conclusion('r5b_solomon_obligated_seek_hearing_or_comply', 'O', 'person:solomon', 'seek_hearing_or_comply_with_existing_order', 'order:eppdapa_restraining_order') :- rule_holds('r5b_solomon_obligated_seek_hearing_or_comply').
deontic_conclusion('r5c_solomon_forbidden_self_help_noncooperation', 'F', 'person:solomon', 'adopt_self_help_noncooperation_posture', 'order:eppdapa_restraining_order') :- rule_holds('r5c_solomon_forbidden_self_help_noncooperation').
deontic_conclusion('r6_hacc_obligated_document_authority_chain_for_lease_change', 'O', 'org:hacc', 'identify_actor_document_and_authority_chain_for_lease_change', 'household:jane_cortez_household') :- rule_holds('r6_hacc_obligated_document_authority_chain_for_lease_change').
deontic_conclusion('r6b_hacc_obligated_document_lease_basis', 'O', 'org:hacc', 'document_basis_for_household_composition_or_lease_adjustment', 'household:jane_cortez_household') :- rule_holds('r6b_hacc_obligated_document_lease_basis').
deontic_conclusion('r6c_solomon_interference_not_proved_by_named_hacc_notice_gap', 'P', 'case:guardianship_collateral_estoppel', 'treat_solomon_hacc_interference_as_inference_not_direct_proof', 'person:solomon') :- rule_holds('r6c_solomon_interference_not_proved_by_named_hacc_notice_gap').
deontic_conclusion('r6d_case_obligated_treat_prior_appointment_as_hypothesis_only', 'O', 'case:guardianship_collateral_estoppel', 'treat_prior_appointment_theory_as_hypothesis_until_source_order_found', 'issue:prior_appointment_for_jane_cortez') :- rule_holds('r6d_case_obligated_treat_prior_appointment_as_hypothesis_only').
deontic_conclusion('r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain', 'P', 'case:guardianship_collateral_estoppel', 'seek_compelled_production_of_hacc_actor_document_authority_chain', 'issue:lease_change_actor_identification') :- rule_holds('r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain').
deontic_conclusion('r7_solomon_forbidden_refile_precluded_issue', 'F', 'person:solomon', 'relitigate_precluded_issue', 'issue:guardianship_authority') :- rule_holds('r7_solomon_forbidden_refile_precluded_issue').
deontic_conclusion('r8_solomon_notice_ack_triggers_court_relief_path', 'O', 'person:solomon', 'seek_clarification_or_relief_through_court', 'order:eppdapa_restraining_order') :- rule_holds('r8_solomon_notice_ack_triggers_court_relief_path').
deontic_conclusion('r9_solomon_wait_for_service_conflicts_with_no_further_service', 'F', 'person:solomon', 'condition_compliance_on_additional_service', 'order:eppdapa_restraining_order') :- rule_holds('r9_solomon_wait_for_service_conflicts_with_no_further_service').
deontic_conclusion('r10_solomon_noncooperation_statement_conflicts_with_effective_order', 'F', 'person:solomon', 'intentional_noncooperation_with_effective_order', 'order:eppdapa_restraining_order') :- rule_holds('r10_solomon_noncooperation_statement_conflicts_with_effective_order').
deontic_conclusion('r11_solomon_already_have_order_statement_supports_notice', 'O', 'person:solomon', 'recognize_existing_order_status', 'order:eppdapa_restraining_order') :- rule_holds('r11_solomon_already_have_order_statement_supports_notice').
deontic_conclusion('r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order', 'F', 'person:solomon', 'assert_order_ineffective_without_court_relief', 'order:eppdapa_restraining_order') :- rule_holds('r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order').
deontic_conclusion('r13_solomon_judge_overturn_statement_triggers_motion_path', 'O', 'person:solomon', 'file_motion_to_modify_or_vacate_before_noncompliance', 'order:eppdapa_restraining_order') :- rule_holds('r13_solomon_judge_overturn_statement_triggers_motion_path').
deontic_conclusion('r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling', 'O', 'org:hacc', 'avoid_third_party_housing_contact_with_restrained_person_and_document_response', 'person:jane_cortez') :- rule_holds('r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling').
deontic_conclusion('r15_benjamin_permitted_serve_subpoena_packets', 'P', 'person:benjamin_barber', 'serve_staged_subpoena_packets', 'case:26PR00641') :- rule_holds('r15_benjamin_permitted_serve_subpoena_packets').
deontic_conclusion('r16_benjamin_obligated_track_service_and_deadlines', 'O', 'person:benjamin_barber', 'maintain_service_and_deadline_tracking', 'case:26PR00641') :- rule_holds('r16_benjamin_obligated_track_service_and_deadlines').
deontic_conclusion('r17_responding_custodian_obligated_execute_or_query_protocol_upon_service', 'O', 'role:responding_custodian', 'execute_or_joined_identifier_queries_and_produce_search_execution_report', 'case:26PR00641') :- rule_holds('r17_responding_custodian_obligated_execute_or_query_protocol_upon_service').
deontic_conclusion('r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response', 'P', 'person:benjamin_barber', 'issue_subpoena_deficiency_notice_and_set_cure_deadline', 'case:26PR00641') :- rule_holds('r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response').
deontic_conclusion('r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage', 'P', 'person:benjamin_barber', 'move_to_compel_and_seek_sanctions_for_subpoena_noncompliance', 'case:26PR00641') :- rule_holds('r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage').
deontic_conclusion('r20_case_permitted_treat_enforcement_path_as_pending_pre_service', 'P', 'case:guardianship_collateral_estoppel', 'treat_subpoena_enforcement_motion_path_as_pending_until_service', 'case:26PR00641') :- rule_holds('r20_case_permitted_treat_enforcement_path_as_pending_pre_service').
deontic_conclusion('r21_case_obligated_resolve_actor_assignment_conflict', 'O', 'case:guardianship_collateral_estoppel', 'resolve_benjamin_vs_solomon_interference_actor_assignment_with_source_record', 'issue:interference_actor_assignment') :- rule_holds('r21_case_obligated_resolve_actor_assignment_conflict').
deontic_conclusion('r22_case_obligated_finalize_authority_citations_before_filing', 'O', 'case:guardianship_collateral_estoppel', 'finalize_governing_authority_citations_before_final_filing', 'doc:06_oregon_authority_table_placeholders.md') :- rule_holds('r22_case_obligated_finalize_authority_citations_before_filing').
deontic_conclusion('r23_case_permitted_initiate_remedial_contempt_path', 'P', 'case:guardianship_collateral_estoppel', 'initiate_remedial_contempt_or_show_cause_path', 'person:solomon') :- rule_holds('r23_case_permitted_initiate_remedial_contempt_path').
deontic_conclusion('r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved', 'P', 'case:guardianship_collateral_estoppel', 'seek_order_or_warrant_to_compel_appearance_if_order_to_appear_is_served_and_ignored', 'person:solomon') :- rule_holds('r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved').
deontic_conclusion('r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved', 'P', 'case:guardianship_collateral_estoppel', 'seek_compensatory_or_compliance_oriented_remedial_sanctions_if_contempt_is_proved', 'issue:prejudice_and_noninterference_relief') :- rule_holds('r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved').
deontic_conclusion('r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown', 'P', 'case:guardianship_collateral_estoppel', 'seek_orcp_17_sanctions_if_filing_is_shown_improper_or_factually_or_legally_unsupported', 'issue:sanctions_track') :- rule_holds('r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown').
deontic_conclusion('r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46', 'P', 'case:guardianship_collateral_estoppel', 'seek_subpoena_enforcement_and_related_expenses_after_nonparty_noncompliance', 'org:hacc') :- rule_holds('r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46').
deontic_conclusion('r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding', 'P', 'case:26PR00641', 'apply_orcp_and_oec_subject_to_specific_chapter_125_overrides', 'proceeding:protective_proceeding') :- rule_holds('r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding').
deontic_conclusion('r29_case_obligated_preserve_notice_and_objection_window', 'O', 'case:26PR00641', 'preserve_statutory_notice_and_objection_window_for_protective_petition', 'person:jane_cortez') :- rule_holds('r29_case_obligated_preserve_notice_and_objection_window').
deontic_conclusion('r30_case_obligated_schedule_hearing_on_presented_objection', 'O', 'case:26PR00641', 'schedule_and_process_hearing_on_guardianship_objection', 'person:jane_cortez') :- rule_holds('r30_case_obligated_schedule_hearing_on_presented_objection').
deontic_conclusion('r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel', 'P', 'case:26PR00641', 'assert_respondent_right_to_appear_in_person_or_by_counsel', 'person:jane_cortez') :- rule_holds('r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel').
deontic_conclusion('r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines', 'P', 'case:guardianship_collateral_estoppel', 'use_orcp9_service_and_orcp10_deadline_computation_for_later_filed_motion_packets', 'issue:service_and_deadlines') :- rule_holds('r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines').

% Temporal anchors inferred from OCR
happens(fact_event(f_petition_exists), 2026-03-31).
happens(fact_event(f_notice_to_respondent), 2026-03-31).
happens(fact_event(f_respondent_objection_form_present), 2026-04-05).
happens(fact_event(f_petition_claims_no_prior_guardian), 2026-03-31).
happens(fact_event(f_prior_appointment_source_order_not_found), 2026-04-07).
happens(fact_event(f_solomon_actual_notice_on_2025_11_17), 2025-11-17).
happens(fact_event(f_solomon_order_filed_on_2025_11_19), 2025-11-19).
happens(fact_event(f_client_solomon_failed_appearance), 2026-03-10).
happens(fact_event(f_client_solomon_barred_refile), 2026-03-31).
happens(fact_event(f_restraining_order_granted), 2025-11-20).
happens(fact_event(f_restraining_order_in_effect), 2025-11-20).
happens(fact_event(f_restraining_order_no_further_service_needed), 2025-11-20).
happens(fact_event(f_restraining_order_contact_restrictions), 2025-11-20).
happens(fact_event(f_restraining_order_residence_restrictions), 2025-11-20).
happens(fact_event(f_restraining_order_property_restrictions), 2025-11-20).
happens(fact_event(f_restraining_order_one_year_duration), 2025-11-20).
happens(fact_event(f_solomon_noncooperation_statement), 2026-03-10).
happens(fact_event(f_solomon_service_position_statement), 2026-03-10).
happens(fact_event(f_hacc_lease_adjustment_effective_2026_01_01), 2026-01-01).
happens(fact_event(f_hacc_removed_benjamin_effective_2026_01_01), 2026-01-01).
happens(fact_event(f_hacc_removed_benjamin_effective_2026_01_01), 2026-01-12).
happens(fact_event(f_hacc_internal_review_claimed), 2026-01-12).
happens(fact_event(f_hacc_court_documentation_basis_claimed), 2026-01-12).
happens(fact_event(f_hacc_actor_identification_record_not_found_locally), 2026-04-07).
happens(fact_event(f_hacc_exhibit_r_requires_compelled_production), 2026-04-07).
happens(fact_event(f_january_2026_hacc_removed_benjamin_restored_restrained_party), 2026-01).
happens(fact_event(f_solomon_interference_with_hacc_lease_theory), 2026-01).
happens(fact_event(f_hacc_named_notice_to_solomon_order_not_found), 2026-04-07).
happens(fact_event(f_ashley_ferron_case_26P000432_denied), 2026-01-26).
happens(fact_event(f_ashley_ferron_case_26P000433_denied), 2026-01-26).
happens(fact_event(f_julio_order_case_25PO11318_exists), 2025-11-17).
happens(fact_event(f_hacc_process_exists), 2026-01-12).
happens(fact_event(f_actor_assignment_conflict_benjamin_vs_solomon_interference), 2026-04-07).
happens(fact_event(f_subpoena_workflow_components_staged), 2026-04-07).
happens(fact_event(f_or_joined_search_protocol_defined), 2026-04-07).
happens(fact_event(f_authority_table_placeholders_unresolved), 2026-04-07).
happens(fact_event(f_authority_ors_33_055_remedial_contempt_procedure), 2026-04-07).
happens(fact_event(f_authority_ors_33_075_compel_appearance), 2026-04-07).
happens(fact_event(f_authority_ors_33_105_remedial_sanctions), 2026-04-07).
happens(fact_event(f_authority_orcp_17_improper_purpose_and_support), 2026-04-07).
happens(fact_event(f_authority_orcp_46_discovery_sanctions), 2026-04-07).
happens(fact_event(f_authority_orcp_55_subpoena_obedience), 2026-04-07).
happens(fact_event(f_authority_ors_125_050_protective_orcp_oec), 2026-04-07).
happens(fact_event(f_authority_ors_125_060_notice_recipients), 2026-04-07).
happens(fact_event(f_authority_ors_125_065_notice_manner_and_timing), 2026-04-07).
happens(fact_event(f_authority_ors_125_075_objections), 2026-04-07).
happens(fact_event(f_authority_ors_125_080_hearing_and_counsel), 2026-04-07).
happens(fact_event(f_authority_ors_125_120_protected_person_special_advocate), 2026-04-07).
happens(fact_event(f_authority_orcp_9_service_of_later_filed_papers), 2026-04-07).
happens(fact_event(f_authority_orcp_10_time_computation), 2026-04-07).
happens(fact_event(f_authority_issue_preclusion_elements_official_oregon_cases), 2026-04-07).
happens(fact_event(f_authority_issue_preclusion_requires_prior_separate_proceeding), 2026-04-07).
happens(fact_event(f_feed_ev_hacc_notice_brother_calls_after_granted_order), 2026-03-26).
happens(fact_event(f_feed_ev_hacc_notice_third_party_contact_with_restrained_person), 2026-03-26).
happens(fact_event(f_feed_ev_msg_claim_restraining_order_filed), 2025-11-19).
happens(fact_event(f_feed_ev_msg_claim_restraining_order_granted), 2025-11-20).
happens(fact_event(f_feed_ev_msg_request_service_address), 2025-11-20).
happens(fact_event(f_feed_ev_solomon_ack_already_have_order), 2025-11-17).
happens(fact_event(f_feed_ev_solomon_ack_heard_restraining_order), 2025-11-17).
happens(fact_event(f_feed_ev_solomon_arrival_statement_for_pickup), 2025-11-19).
happens(fact_event(f_feed_ev_solomon_conditionally_cancel_pickup), 2025-11-19).
happens(fact_event(f_feed_ev_solomon_entrapment_statement), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_identified_aps_contact), 2025-11-19).
happens(fact_event(f_feed_ev_solomon_judge_overturn_statement), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_not_incentivized_eml), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_not_incentivized_statement), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_order_not_in_effect_statement), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_pickup_plan_for_jane), 2025-11-19).
happens(fact_event(f_feed_ev_solomon_provided_aps_reference_number), 2025-11-19).
happens(fact_event(f_feed_ev_solomon_wait_for_service_eml), 2026-03-10).
happens(fact_event(f_feed_ev_solomon_wait_for_service_statement), 2026-03-10).
happens(fact_event(f_repo_solomon_mention_1), 01/03/2026).
happens(fact_event(f_repo_solomon_mention_1), 01/08/2026).
happens(fact_event(f_repo_solomon_mention_1), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_2), 03-31-2026).
happens(fact_event(f_repo_solomon_mention_2), 03/31/2026).
happens(fact_event(f_repo_solomon_mention_2), 04-15-2026).
happens(fact_event(f_repo_solomon_mention_3), 01/03/2026).
happens(fact_event(f_repo_solomon_mention_3), 01/08/2026).
happens(fact_event(f_repo_solomon_mention_3), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_4), 2021-01-42).
happens(fact_event(f_repo_solomon_mention_4), 2021-02-15).
happens(fact_event(f_repo_solomon_mention_4), 2021-19-53).
happens(fact_event(f_repo_solomon_mention_5), 2021-01-42).
happens(fact_event(f_repo_solomon_mention_5), 2021-02-15).
happens(fact_event(f_repo_solomon_mention_5), 2021-19-53).
happens(fact_event(f_repo_solomon_mention_6), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_6), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_6), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_7), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_7), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_7), 03/20/2026).
happens(fact_event(f_repo_solomon_mention_8), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_8), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_8), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_9), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_9), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_9), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_10), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_11), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_11), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_11), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_12), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_12), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_12), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_14), 2025-01-39).
happens(fact_event(f_repo_solomon_mention_14), 2025-01-43).
happens(fact_event(f_repo_solomon_mention_14), 2025-01-44).
happens(fact_event(f_repo_solomon_mention_15), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_15), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_15), 12/16/2025).
happens(fact_event(f_repo_solomon_mention_16), 11/17/2025).
happens(fact_event(f_repo_solomon_mention_16), 11/19/2025).
happens(fact_event(f_repo_solomon_mention_19), 2026-01-12).
happens(fact_event(f_repo_solomon_mention_19), 2026-03-23).
happens(fact_event(f_repo_solomon_mention_19), 2026-03-31).
happens(fact_event(f_repo_solomon_mention_22), 3/22/2026).
happens(fact_event(f_repo_solomon_mention_23), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_23), 2026-01-12).
happens(fact_event(f_repo_solomon_mention_23), 2026-03-10).
happens(fact_event(f_repo_solomon_mention_26), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_26), 2026-01-12).
happens(fact_event(f_repo_solomon_mention_26), 2026-03-10).
happens(fact_event(f_repo_solomon_mention_27), 3/31/2026).
happens(fact_event(f_repo_solomon_mention_28), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_28), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_28), 12/16/2025).
happens(fact_event(f_repo_solomon_mention_30), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_30), 2025-20-56).
happens(fact_event(f_repo_solomon_mention_30), 2026-04-04).
happens(fact_event(f_repo_solomon_mention_31), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_31), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_31), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_32), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_32), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_32), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_34), 03/20/2026).
happens(fact_event(f_repo_solomon_mention_34), 1/31/2028).
happens(fact_event(f_repo_solomon_mention_34), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_35), 03/20/2026).
happens(fact_event(f_repo_solomon_mention_35), 1/31/2028).
happens(fact_event(f_repo_solomon_mention_35), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_36), 03/20/2026).
happens(fact_event(f_repo_solomon_mention_36), 1/31/2028).
happens(fact_event(f_repo_solomon_mention_36), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_37), 3/18/2026).
happens(fact_event(f_repo_solomon_mention_38), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_38), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_38), 03/20/2026).
happens(fact_event(f_repo_solomon_mention_39), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_39), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_39), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_40), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_40), 2026-01-12).
happens(fact_event(f_repo_solomon_mention_40), 2026-03-10).
happens(fact_event(f_repo_solomon_mention_42), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_42), 2025-20-56).
happens(fact_event(f_repo_solomon_mention_42), 2026-04-04).
happens(fact_event(f_repo_solomon_mention_46), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_46), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_46), 12/16/2025).
happens(fact_event(f_repo_solomon_mention_47), 2026-03-31).
happens(fact_event(f_repo_solomon_mention_47), 2026-04-02).
happens(fact_event(f_repo_solomon_mention_47), 2026-04-05).
happens(fact_event(f_repo_solomon_mention_49), 04-15-2026).
happens(fact_event(f_repo_solomon_mention_49), 04/15/2026).
happens(fact_event(f_repo_solomon_mention_51), 02/20/2026).
happens(fact_event(f_repo_solomon_mention_51), 03/04/2026).
happens(fact_event(f_repo_solomon_mention_51), 12/16/2025).
happens(fact_event(f_repo_solomon_mention_56), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_56), 2026-03-17).
happens(fact_event(f_repo_solomon_mention_56), 2026-03-25).
happens(fact_event(f_repo_solomon_mention_60), 3/18/2026).
happens(fact_event(f_repo_solomon_mention_61), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_61), 2025-20-56).
happens(fact_event(f_repo_solomon_mention_61), 2026-04-04).
happens(fact_event(f_repo_solomon_mention_65), 2026-03-31).
happens(fact_event(f_repo_solomon_mention_65), 2026-04-02).
happens(fact_event(f_repo_solomon_mention_65), 2026-04-05).
happens(fact_event(f_repo_solomon_mention_68), 11-20-2025).
happens(fact_event(f_repo_solomon_mention_68), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_68), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_71), 2025-20-38).
happens(fact_event(f_repo_solomon_mention_71), 2025-20-56).
happens(fact_event(f_repo_solomon_mention_71), 2026-04-04).
happens(fact_event(f_repo_solomon_mention_78), 04-15-2026).
happens(fact_event(f_repo_solomon_mention_78), 04/15/2026).
happens(fact_event(f_repo_solomon_mention_89), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_89), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_89), 2025-11-20).
happens(fact_event(f_repo_solomon_mention_98), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_99), 11-20-2025).
happens(fact_event(f_repo_solomon_mention_99), 2025-11-17).
happens(fact_event(f_repo_solomon_mention_99), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_100), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_101), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_102), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_103), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_115), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_117), 11-20-2025).
happens(fact_event(f_repo_solomon_mention_117), 12/12/2025).
happens(fact_event(f_repo_solomon_mention_117), 2025-11-19).
happens(fact_event(f_repo_solomon_mention_127), 04/15/2026).
happens(fact_event(f_repo_solomon_mention_141), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_141), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_141), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_142), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_142), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_142), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_143), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_143), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_143), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_144), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_144), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_144), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_145), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_145), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_145), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_146), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_146), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_146), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_147), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_148), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_149), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_150), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_151), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_152), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_153), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_154), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_155), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_156), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_157), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_158), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_159), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_160), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_161), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_162), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_163), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_164), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_165), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_166), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_167), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_168), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_169), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_170), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_171), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_174), 12/9/2025).
happens(fact_event(f_repo_solomon_mention_175), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_175), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_175), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_176), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_176), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_176), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_177), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_177), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_177), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_178), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_178), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_178), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_179), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_179), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_179), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_180), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_180), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_180), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_181), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_181), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_181), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_182), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_182), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_182), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_183), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_183), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_183), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_184), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_184), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_184), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_185), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_185), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_185), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_186), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_186), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_186), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_187), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_187), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_187), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_188), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_188), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_188), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_189), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_189), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_189), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_190), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_190), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_190), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_191), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_191), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_191), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_192), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_192), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_192), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_193), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_193), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_193), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_194), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_194), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_194), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_195), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_195), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_195), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_196), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_196), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_196), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_197), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_197), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_197), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_198), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_198), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_198), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_199), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_199), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_199), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_221), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_221), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_221), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_228), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_228), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_228), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_235), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_235), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_235), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_242), 12-1-2024).
happens(fact_event(f_repo_solomon_mention_242), 12-1-2025).
happens(fact_event(f_repo_solomon_mention_242), 12-31-2025).
happens(fact_event(f_repo_solomon_mention_272), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_278), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_279), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_280), 2026-04-07).
happens(fact_event(f_repo_solomon_mention_281), 2026-04-07).
happens(fact_event(f_active_service_log_initialized), 2026-04-07).
happens(fact_event(f_subpoena_recipients_ready_to_serve), 2026-04-07).
happens(fact_event(f_subpoena_service_completed_any), 2026-04-07).
happens(fact_event(f_subpoena_pre_service_phase_only), 2026-04-07).
happens(fact_event(f_deficiency_notice_sent_any), 2026-04-07).
happens(fact_event(f_subpoena_response_incomplete_any), 2026-04-07).
happens(fact_event(f_motion_to_compel_stage_any), 2026-04-07).

% Fact status comments
% f_petition_exists: status=verified, source=solomon_motion_for_guardianship_ocr.txt, dates=['2026-03-31']
% f_notice_to_respondent: status=verified, source=solomon_motion_for_guardianship_ocr.txt, dates=['2026-03-31']
% f_respondent_objection_form_present: status=verified, source=guardianship_timeline.md, dates=['2026-04-05']
% f_petition_claims_no_prior_guardian: status=verified, source=solomon_motion_for_guardianship_ocr.txt, dates=['2026-03-31']
% f_prior_appointment_source_order_not_found: status=verified, source=deontic_logic_gap_review_2026-04-07.md, dates=['2026-04-07']
% f_client_prior_appointment: status=alleged, source=client_assertion, dates=[]
% f_client_benjamin_avoided_service: status=alleged, source=client_assertion, dates=[]
% f_client_benjamin_order_disregard: status=alleged, source=client_assertion, dates=[]
% f_client_benjamin_housing_interference: status=alleged, source=client_assertion, dates=[]
% f_solomon_actual_notice_on_2025_11_17: status=verified, source=uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-17']
% f_solomon_order_filed_on_2025_11_19: status=verified, source=14161-Me-to-solomon-gv-b2df7cbf8706d9fe/transcript.txt, dates=['2025-11-19']
% f_client_solomon_failed_appearance: status=alleged, source=client_assertion, dates=['2026-03-10']
% f_client_solomon_barred_refile: status=alleged, source=client_assertion, dates=['2026-03-31']
% f_restraining_order_granted: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_in_effect: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_no_further_service_needed: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_contact_restrictions: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_residence_restrictions: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_property_restrictions: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_restraining_order_one_year_duration: status=verified, source=sam_barber_restraining_order_ocr.txt, dates=['2025-11-20']
% f_solomon_noncooperation_statement: status=verified, source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt, dates=['2026-03-10']
% f_solomon_service_position_statement: status=verified, source=14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt, dates=['2026-03-10']
% f_hacc_lease_adjustment_effective_2026_01_01: status=verified, source=HACC vawa violation.pdf, dates=['2026-01-01']
% f_hacc_removed_benjamin_effective_2026_01_01: status=verified, source=0014-Re-Allegations-of-Fraud---JC-Household/message.eml, dates=['2026-01-01', '2026-01-12']
% f_hacc_internal_review_claimed: status=verified, source=0014-Re-Allegations-of-Fraud---JC-Household/message.eml, dates=['2026-01-12']
% f_hacc_court_documentation_basis_claimed: status=verified, source=0014-Re-Allegations-of-Fraud---JC-Household/message.eml, dates=['2026-01-12']
% f_hacc_actor_identification_record_not_found_locally: status=verified, source=missing_exhibit_search_status_2026-04-07.md, dates=['2026-04-07']
% f_hacc_exhibit_r_requires_compelled_production: status=verified, source=subpoena_target_memo_hacc_lease_authority_record.md, dates=['2026-04-07']
% f_january_2026_hacc_removed_benjamin_restored_restrained_party: status=alleged, source=did-key-hacc-temp-session.json, dates=['2026-01']
% f_solomon_interference_with_hacc_lease_theory: status=alleged, source=solomon_interference_and_lease_tampering_theory.md, dates=['2026-01']
% f_hacc_named_notice_to_solomon_order_not_found: status=verified, source=protective_order_and_hacc_notice_timeline.md, dates=['2026-04-07']
% f_ashley_ferron_case_26P000432_denied: status=verified, source=protective_order_and_hacc_notice_timeline.md, dates=['2026-01-26']
% f_ashley_ferron_case_26P000433_denied: status=verified, source=protective_order_and_hacc_notice_timeline.md, dates=['2026-01-26']
% f_julio_order_case_25PO11318_exists: status=verified, source=protective_order_and_hacc_notice_timeline.md, dates=['2025-11-17']
% f_hacc_process_exists: status=verified, source=0014-Re-Allegations-of-Fraud---JC-Household/message.eml, dates=['2026-01-12']
% f_collateral_estoppel_candidate: status=theory, source=motion_to_dismiss_for_collateral_estoppel.md, dates=[]
% f_actor_assignment_conflict_benjamin_vs_solomon_interference: status=verified, source=generate_formal_reasoning_artifacts.py, dates=['2026-04-07']
% f_subpoena_workflow_components_staged: status=verified, source=final_filing_set, dates=['2026-04-07']
% f_or_joined_search_protocol_defined: status=verified, source=11B_attachment_a2_definitions_and_instructions_final.md, dates=['2026-04-07']
% f_authority_table_placeholders_unresolved: status=verified, source=06_oregon_authority_table_placeholders.md, dates=['2026-04-07']
% f_authority_ors_33_055_remedial_contempt_procedure: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_33_075_compel_appearance: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_33_105_remedial_sanctions: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_orcp_17_improper_purpose_and_support: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_orcp_46_discovery_sanctions: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_orcp_55_subpoena_obedience: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_050_protective_orcp_oec: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_060_notice_recipients: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_065_notice_manner_and_timing: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_075_objections: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_080_hearing_and_counsel: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_ors_125_120_protected_person_special_advocate: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_orcp_9_service_of_later_filed_papers: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_orcp_10_time_computation: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_issue_preclusion_elements_official_oregon_cases: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_authority_issue_preclusion_requires_prior_separate_proceeding: status=verified, source=oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_feed_ev_hacc_notice_brother_calls_after_granted_order: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=['2026-03-26']
% f_feed_ev_hacc_notice_third_party_contact_with_restrained_person: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=['2026-03-26']
% f_feed_ev_msg_claim_restraining_order_filed: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14161-Me-to-solomon-gv-b2df7cbf8706d9fe/transcript.txt | /home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14163-Me-to-solomon-gv-7540e6c07566a84a/transcript.txt, dates=['2025-11-19']
% f_feed_ev_msg_claim_restraining_order_granted: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt, dates=['2025-11-20']
% f_feed_ev_msg_request_service_address: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt, dates=['2025-11-20']
% f_feed_ev_solomon_ack_already_have_order: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660690_Mon--17-Nov-2025-20-56-22--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-17']
% f_feed_ev_solomon_ack_heard_restraining_order: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660669_Mon--17-Nov-2025-20-38-24--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-17']
% f_feed_ev_solomon_arrival_statement_for_pickup: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_661192_Wed--19-Nov-2025-02-27-03--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-19']
% f_feed_ev_solomon_conditionally_cancel_pickup: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_661182_Wed--19-Nov-2025-01-44-55--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-19']
% f_feed_ev_solomon_entrapment_statement: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743136_Tue--10-Mar-2026-17-51-15--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2026-03-10']
% f_feed_ev_solomon_identified_aps_contact: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_661180_Wed--19-Nov-2025-01-43-39--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-19']
% f_feed_ev_solomon_judge_overturn_statement: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743129_Tue--10-Mar-2026-17-39-27--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2026-03-10']
% f_feed_ev_solomon_not_incentivized_eml: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743129_Tue--10-Mar-2026-17-39-27--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2026-03-10']
% f_feed_ev_solomon_not_incentivized_statement: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt, dates=['2026-03-10']
% f_feed_ev_solomon_order_not_in_effect_statement: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt | /home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743131_Tue--10-Mar-2026-17-45-54--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2026-03-10']
% f_feed_ev_solomon_pickup_plan_for_jane: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_661177_Wed--19-Nov-2025-01-39-25--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-19']
% f_feed_ev_solomon_provided_aps_reference_number: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_661181_Wed--19-Nov-2025-01-44-03--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2025-11-19']
% f_feed_ev_solomon_wait_for_service_eml: status=verified, source=/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_743131_Tue--10-Mar-2026-17-45-54--0000_New-text-message-from-solomon--503--381-6911.eml, dates=['2026-03-10']
% f_feed_ev_solomon_wait_for_service_statement: status=verified, source=/home/barberb/HACC/evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt, dates=['2026-03-10']
% f_repo_solomon_mention_1: status=verified, source=Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.md, dates=['01/03/2026', '01/08/2026', '02/20/2026']
% f_repo_solomon_mention_2: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/email_import_manifest.json, dates=['03-31-2026', '03/31/2026', '04-15-2026']
% f_repo_solomon_mention_3: status=verified, source=Collateral Estoppel/knowledge_graph/generated/full_case_knowledge_graph.json, dates=['01/03/2026', '01/08/2026', '02/20/2026']
% f_repo_solomon_mention_4: status=verified, source=evidence/email_imports/starworks5-master-case-email-import/email_import_manifest.json, dates=['2021-01-42', '2021-02-15', '2021-19-53']
% f_repo_solomon_mention_5: status=verified, source=evidence/email_imports/starworks5-solomon-sms-import/email_import_manifest.json, dates=['2021-01-42', '2021-02-15', '2021-19-53']
% f_repo_solomon_mention_6: status=verified, source=Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json, dates=['2025-11-17', '2025-11-19', '2025-11-20']
% f_repo_solomon_mention_7: status=verified, source=evidence/email_imports/starworks5-master-case-email-import/graphrag/email_corpus_records.json, dates=['02/20/2026', '03/04/2026', '03/20/2026']
% f_repo_solomon_mention_8: status=verified, source=Collateral Estoppel/knowledge_graph/generated/motion_support_map.json, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_9: status=verified, source=Collateral Estoppel/knowledge_graph/generated/motion_support_map.md, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_10: status=verified, source=Collateral Estoppel/knowledge_graph/generated/case_dependency_graph.json, dates=['2026-04-07']
% f_repo_solomon_mention_11: status=verified, source=Collateral Estoppel/knowledge_graph/generated/motion_paragraph_bank.json, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_12: status=verified, source=Collateral Estoppel/knowledge_graph/generated/motion_paragraph_bank.md, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_13: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_14: status=verified, source=Collateral Estoppel/evidence_notes/solomon_evidence_graph_feed.json, dates=['2025-01-39', '2025-01-43', '2025-01-44']
% f_repo_solomon_mention_15: status=verified, source=evidence/email_imports/starworks5-additional-info-import/graphrag/email_corpus_records.json, dates=['02/20/2026', '03/04/2026', '12/16/2025']
% f_repo_solomon_mention_16: status=verified, source=Collateral Estoppel/evidence_notes/sam_barber_restraining_order_ocr.txt, dates=['11/17/2025', '11/19/2025']
% f_repo_solomon_mention_17: status=verified, source=evidence/email_imports/starworks5-additional-info-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_18: status=verified, source=evidence/email_imports/starworks5-additional-reimport-20260404/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_19: status=verified, source=Collateral Estoppel/knowledge_graph/guardianship_case_graph.json, dates=['2026-01-12', '2026-03-23', '2026-03-31']
% f_repo_solomon_mention_20: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/event.json, dates=[]
% f_repo_solomon_mention_21: status=verified, source=Collateral Estoppel/drafts/petition_guardianship_working_memo.md, dates=[]
% f_repo_solomon_mention_22: status=verified, source=evidence/email_imports/_email_cache/email_cache_index.json, dates=['3/22/2026']
% f_repo_solomon_mention_23: status=verified, source=Collateral Estoppel/knowledge_graph/generated/deontic_litigation_matrix.json, dates=['2025-11-20', '2026-01-12', '2026-03-10']
% f_repo_solomon_mention_24: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_25: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_26: status=verified, source=Collateral Estoppel/knowledge_graph/generated/deontic_litigation_matrix.md, dates=['2025-11-20', '2026-01-12', '2026-03-10']
% f_repo_solomon_mention_27: status=verified, source=Collateral Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt, dates=['3/31/2026']
% f_repo_solomon_mention_28: status=verified, source=evidence/email_imports/starworks5-recommended-packet-email-import/graphrag/email_corpus_records.json, dates=['02/20/2026', '03/04/2026', '12/16/2025']
% f_repo_solomon_mention_29: status=verified, source=evidence/email_imports/starworks5-clackamas-followup-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_30: status=verified, source=Collateral Estoppel/drafts/motion_to_show_cause_re_contempt_and_collateral_interference.md, dates=['2025-20-38', '2025-20-56', '2026-04-04']
% f_repo_solomon_mention_31: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/inclusive__motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_md.md, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_32: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/strict__motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_md.md, dates=['2025-11-17', '2025-11-20', '2025-20-38']
% f_repo_solomon_mention_33: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/event.json, dates=[]
% f_repo_solomon_mention_34: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/graphrag/email_corpus_records.json, dates=['03/20/2026', '1/31/2028', '12-1-2024']
% f_repo_solomon_mention_35: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/graphrag/email_corpus_records.json, dates=['03/20/2026', '1/31/2028', '12-1-2024']
% f_repo_solomon_mention_36: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/graphrag/email_corpus_records.json, dates=['03/20/2026', '1/31/2028', '12-1-2024']
% f_repo_solomon_mention_37: status=verified, source=evidence/email_imports/starworks5-ktilton-orientation-import/graphrag/email_corpus_records.json, dates=['3/18/2026']
% f_repo_solomon_mention_38: status=verified, source=evidence/email_imports/starworks5-master-case-email-import/graphrag/email_knowledge_graph.json, dates=['02/20/2026', '03/04/2026', '03/20/2026']
% f_repo_solomon_mention_39: status=verified, source=Collateral Estoppel/evidence_notes/solomon_order_evidence_inventory.md, dates=['2025-11-17', '2025-11-19', '2025-11-20']
% f_repo_solomon_mention_40: status=verified, source=Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.md, dates=['2025-11-20', '2026-01-12', '2026-03-10']
% f_repo_solomon_mention_41: status=verified, source=evidence/email_imports/starworks5-ktilton-orientation-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_42: status=verified, source=Collateral Estoppel/drafts/motion_for_sanctions_re_frivolous_and_abusive_practice.md, dates=['2025-20-38', '2025-20-56', '2026-04-04']
% f_repo_solomon_mention_43: status=verified, source=Collateral Estoppel/README.md, dates=[]
% f_repo_solomon_mention_44: status=verified, source=Collateral Estoppel/drafts/motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim.md, dates=[]
% f_repo_solomon_mention_45: status=verified, source=Collateral Estoppel/drafts/petition_guardianship_packet_stage1.md, dates=[]
% f_repo_solomon_mention_46: status=verified, source=evidence/email_imports/starworks5-recommended-packet-email-import/graphrag/email_knowledge_graph.json, dates=['02/20/2026', '03/04/2026', '12/16/2025']
% f_repo_solomon_mention_47: status=verified, source=Collateral Estoppel/evidence_notes/guardianship_timeline.md, dates=['2026-03-31', '2026-04-02', '2026-04-05']
% f_repo_solomon_mention_48: status=verified, source=Collateral Estoppel/evidence_notes/repeated_usurpation_pattern_memo.md, dates=[]
% f_repo_solomon_mention_49: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS88AOeCYdOwG67zOMVTo7MZdNA-4EqmReikbECQvp-SRA-mail.gmail.com_20260401_Re-Request-for-additional-information-Cortez---DUE-04-15-2026/message.json, dates=['04-15-2026', '04/15/2026']
% f_repo_solomon_mention_50: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_jUi7EBW-d4uabncxb0bNXeOuJUp59T-d1nJFwnymZbA-mail.gmail.com_20260329_Re-HCV-Orientation/message.json, dates=[]
% f_repo_solomon_mention_51: status=verified, source=evidence/email_imports/starworks5-additional-info-import/graphrag/email_knowledge_graph.json, dates=['02/20/2026', '03/04/2026', '12/16/2025']
% f_repo_solomon_mention_52: status=verified, source=evidence/email_imports/starworks5-recommended-packet-email-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_53: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8NwnM6aAhiY-HeY2Bs4EosOn2W790KYdvq-tzDKZUwPQ-mail.gmail.com_20260328_Re-HCV-Orientation/message.json, dates=[]
% f_repo_solomon_mention_54: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9bg00mw8vaCYD5PrG_sc-6Piz_Ws17GmeD-4-tPZHx-A-mail.gmail.com_20260327_Re-HCV-Orientation/message.json, dates=[]
% f_repo_solomon_mention_55: status=verified, source=Collateral Estoppel/drafts/petition_guardianship_court_ready_shell.md, dates=[]
% f_repo_solomon_mention_56: status=verified, source=Collateral Estoppel/evidence_notes/solomon_repository_evidence_memo.md, dates=['2025-11-20', '2026-03-17', '2026-03-25']
% f_repo_solomon_mention_57: status=verified, source=Collateral Estoppel/evidence_notes/source_register.md, dates=[]
% f_repo_solomon_mention_58: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-P2WrnnNn7ZHJVGwyxmidnr-LsfQR-wGbZckgYnKMyfQ-mail.gmail.com_20260327_Re-HCV-Orientation/message.json, dates=[]
% f_repo_solomon_mention_59: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_9t6E-hCO1rJiZE0dufMSTv54c2Omihyzsp4KaiDZN6Q-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_60: status=verified, source=evidence/email_imports/starworks5-ktilton-orientation-import/graphrag/email_knowledge_graph.json, dates=['3/18/2026']
% f_repo_solomon_mention_61: status=verified, source=Collateral Estoppel/evidence_notes/motion_exhibit_index.md, dates=['2025-20-38', '2025-20-56', '2026-04-04']
% f_repo_solomon_mention_62: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0027-Fwd-Allegations-of-Fraud---JC-Household-CAMTdTS8Qs6qAUfLmxrRp6h8BsEgpXTKn9sf6d5bgg9RjJrjvHA-mail.gmail.com/message.eml, dates=[]
% f_repo_solomon_mention_63: status=verified, source=Collateral Estoppel/drafts/final_filing_set/11B_attachment_a2_definitions_and_instructions_final.md, dates=[]
% f_repo_solomon_mention_64: status=verified, source=Collateral Estoppel/drafts/final_filing_set/12A_attachment_b1_hacc_county_requests_final.md, dates=[]
% f_repo_solomon_mention_65: status=verified, source=Collateral Estoppel/knowledge_graph/guardianship_case_graph.md, dates=['2026-03-31', '2026-04-02', '2026-04-05']
% f_repo_solomon_mention_66: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_cvnTsxdNGtjzvAtUPDj31MU--P3vsRFenpigq-kWWuw-mail.gmail.com_20260404_Re-SERVICE-Jane-Kay-Cortez-vs-Solomon-Samuel-Barber-Benjamin-Jay-Barber-vs-Solom/message.json, dates=[]
% f_repo_solomon_mention_67: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CO1PR10MB44826703707F0BD1A5D81F64AC5FA-CO1PR10MB4482.namprd10.prod.outlook.com_20260404_Re-SERVICE-Jane-Kay-Cortez-vs-Solomon-Samuel-Barber-Benjamin-Jay-Barber-vs-Solom/message.json, dates=[]
% f_repo_solomon_mention_68: status=verified, source=Collateral Estoppel/evidence_notes/solomon_restraining_order_review.md, dates=['11-20-2025', '2025-11-19', '2025-11-20']
% f_repo_solomon_mention_69: status=verified, source=evidence/email_imports/starworks5-cortez-case-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_70: status=verified, source=Collateral Estoppel/drafts/final_filing_set/03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.md, dates=[]
% f_repo_solomon_mention_71: status=verified, source=Collateral Estoppel/drafts/memorandum_in_support_of_show_cause_and_sanctions.md, dates=['2025-20-38', '2025-20-56', '2026-04-04']
% f_repo_solomon_mention_72: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/transcript.txt, dates=[]
% f_repo_solomon_mention_73: status=verified, source=Collateral Estoppel/evidence_notes/guardianship_exhibit_index.md, dates=[]
% f_repo_solomon_mention_74: status=verified, source=Collateral Estoppel/evidence_notes/skee_declaration_and_lease_removal_inference_memo.md, dates=[]
% f_repo_solomon_mention_75: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14160-Me-to-solomon-gv-7cb858000dea7723/event.json, dates=[]
% f_repo_solomon_mention_76: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14163-Me-to-solomon-gv-7540e6c07566a84a/event.json, dates=[]
% f_repo_solomon_mention_77: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14165-Me-to-solomon-gv-e6594297d713efde/event.json, dates=[]
% f_repo_solomon_mention_78: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8RGx6e6geqARYxO6Qgy71ggYc9hVCeVcJJ11TKsL3u5A-mail.gmail.com_20260401_Re-Request-for-additional-information-Cortez---DUE-04-15-2026/message.json, dates=['04-15-2026', '04/15/2026']
% f_repo_solomon_mention_79: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0026-Fwd-Allegations-of-Fraud---JC-Household-CAMTdTS8n7D-f43RH-QrFommUiuyG3-bM-rd_x4sNW-U-vR6v8Q-mail.gmail.com/message.eml, dates=[]
% f_repo_solomon_mention_80: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14158-Me-to-solomon-gv-9ec3655706570c02/event.json, dates=[]
% f_repo_solomon_mention_81: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-ycD2U_DWV5a_FGyXonCu2RWwkO_ve4see6S_fbH0JJg-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_82: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9KrbGkCP2VbfEA3R4fKRY68Lb3WqC0v6M5OkjJOXnvCg-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_83: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_pLTSkF-VvG_ax7crJGdcYncMfvusLbyABYbK3pu8aPQ-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_84: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB9270EA8C18BD803B47035C289450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_85: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14167-Voicemail-from-solomon-gv-ff8c96ec1900a29b/event.json, dates=[]
% f_repo_solomon_mention_86: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14168-Voicemail-from-solomon-gv-9a25799b310757d3/event.json, dates=[]
% f_repo_solomon_mention_87: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14169-Voicemail-from-solomon-gv-bb37d1d3d6f744d3/event.json, dates=[]
% f_repo_solomon_mention_88: status=verified, source=Collateral Estoppel/evidence_notes/allegation_proof_matrix.md, dates=[]
% f_repo_solomon_mention_89: status=verified, source=Collateral Estoppel/evidence_notes/solomon_evidence_graph_bridge.md, dates=['2025-11-17', '2025-11-19', '2025-11-20']
% f_repo_solomon_mention_90: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-MWcr-C4pH93xkp7-ASGd99A2dZU1nxUe6BsDnJq-97Q-mail.gmail.com_20260401_Fwd-Annual-Certification-Income-Verification/message.json, dates=[]
% f_repo_solomon_mention_91: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_DS7PR08MB69740F395676C0CD72D36F6CB457A-DS7PR08MB6974.namprd08.prod.outlook.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.eml, dates=[]
% f_repo_solomon_mention_92: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_93: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_94: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/email_import_manifest.json, dates=[]
% f_repo_solomon_mention_95: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/transcript.txt, dates=[]
% f_repo_solomon_mention_96: status=verified, source=Collateral Estoppel/drafts/declaration_of_benjamin_barber_in_support_of_motions.md, dates=[]
% f_repo_solomon_mention_97: status=verified, source=Collateral Estoppel/drafts/final_filing_set/11_subpoena_duces_tecum_to_solomon_barber_final.md, dates=[]
% f_repo_solomon_mention_98: status=verified, source=Collateral Estoppel/evidence_notes/missing_exhibit_search_status_2026-04-07.md, dates=['2026-04-07']
% f_repo_solomon_mention_99: status=verified, source=Collateral Estoppel/evidence_notes/solomon_order_completeness_checklist.md, dates=['11-20-2025', '2025-11-17', '2025-11-19']
% f_repo_solomon_mention_100: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/inclusive__motion_for_appointment_and_appearance_of_guardian_ad_litem_md.md, dates=['2026-04-07']
% f_repo_solomon_mention_101: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/inclusive__motion_to_dismiss_for_collateral_estoppel_md.md, dates=['2026-04-07']
% f_repo_solomon_mention_102: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/strict__motion_for_appointment_and_appearance_of_guardian_ad_litem_md.md, dates=['2026-04-07']
% f_repo_solomon_mention_103: status=verified, source=Collateral Estoppel/knowledge_graph/generated/paragraph_bank_by_motion/strict__motion_to_dismiss_for_collateral_estoppel_md.md, dates=['2026-04-07']
% f_repo_solomon_mention_104: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-s81pANZQM_LBw2UPOuS-HYVmUU-Ru-ncu79k-G_ophw-mail.gmail.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_105: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-tpa5JJxpJKROzkZp8-HJnSuyj85JmqTzMQsJtVXUEtQ-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_106: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8g3aU6XEn9WFRwenyv-As8gj1ZhHJv6WTxNCS6RGBudA-mail.gmail.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_107: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8xJsxeFWD-1HLz6SUFOECiY87ZwsfR8-dy6xEbEYBJoA-mail.gmail.com_20260401_Fwd-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_108: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8y9qrmXm-6srw7hs5v7vEh_WEix63e_vz7rfs96J33cA-mail.gmail.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_109: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9t8aVDAB3uNAsTxV-yS2c9ivKSo8gbZKZubUs4F-QUmA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_110: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_9t6E-hCO1rJiZE0dufMSTv54c2Omihyzsp4KaiDZN6Q-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_111: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_e3fgfZaiOiCZ-BJia-5_C43Vh5FA-JjeYhTO6Mk-ZXA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_112: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_fFKVhJr-CeQpP6cccn3-iNWGb4wFdV-r-gMniyKn5AA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_113: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_o71dzQxsfpPO-h5g2_OXVNcqH8cSYu1kun6h8JJ-zQg-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_114: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB927099B3341222255481768E9450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_115: status=verified, source=Collateral Estoppel/drafts/final_filing_set/10_prefill_sources_and_verification_note.md, dates=['2026-04-07']
% f_repo_solomon_mention_116: status=verified, source=Collateral Estoppel/drafts/motion_for_leave_or_to_compel_exhibit_r_production.md, dates=[]
% f_repo_solomon_mention_117: status=verified, source=Collateral Estoppel/evidence_notes/solomon_order_digest.md, dates=['11-20-2025', '12/12/2025', '2025-11-19']
% f_repo_solomon_mention_118: status=verified, source=Collateral Estoppel/knowledge_graph/deontic_theorem_workbook.md, dates=[]
% f_repo_solomon_mention_119: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS-ycD2U_DWV5a_FGyXonCu2RWwkO_ve4see6S_fbH0JJg-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_120: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8he-NNyTiycEvkY6dRN32L02UM-Bgf80oU2QDU_mkT9Q-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_121: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9Faig-yNo8O9UzxFoVncs4z-3EigK_oLsujFJGmP5MLA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_122: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9KrbGkCP2VbfEA3R4fKRY68Lb3WqC0v6M5OkjJOXnvCg-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_123: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS9t8aVDAB3uNAsTxV-yS2c9ivKSo8gbZKZubUs4F-QUmA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_124: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_Vz2pMtLfz89QVVpncUd1ceYCX_WSDw1ZCJKnwysc_CQ-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.eml, dates=[]
% f_repo_solomon_mention_125: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_Vz2pMtLfz89QVVpncUd1ceYCX_WSDw1ZCJKnwysc_CQ-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_126: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_e3fgfZaiOiCZ-BJia-5_C43Vh5FA-JjeYhTO6Mk-ZXA-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_127: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_iDmMe5270abQ6KJ8SNkTnhyUgtYrzgGma6cOS-YhApA-mail.gmail.com_20260401_Re-Request-for-additional-information-Cortez---DUE-04-15-2026/message.eml, dates=['04/15/2026']
% f_repo_solomon_mention_128: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_pLTSkF-VvG_ax7crJGdcYncMfvusLbyABYbK3pu8aPQ-mail.gmail.com_20260401_Re-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_129: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_DS7PR08MB69744AC53FD7853FFDC9275EB457A-DS7PR08MB6974.namprd08.prod.outlook.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_130: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB9270307B75F0B68C05E6C1A29450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_131: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB92704B4FF93F6F65B33740199450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_132: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB927067A6ABFA9F05FFC7D2159450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_133: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB9270AECC65285A5596F6D51C9450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_134: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_SJ0PR09MB9270C4BC73990095C02B84E89450A-SJ0PR09MB9270.namprd09.prod.outlook.com_20260401_RE-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_135: status=verified, source=Collateral Estoppel/drafts/final_filing_set/04_declaration_of_benjamin_barber_in_support_of_motions_final.md, dates=[]
% f_repo_solomon_mention_136: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8XHfbEop7LSQB4MfGq3xJC-eQaWXyf-Bhptq1-scrM-w-mail.gmail.com_20260401_Fwd-Additional-Information-Needed/message.json, dates=[]
% f_repo_solomon_mention_137: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8rowgBct-5GFqbfUtOoJ3GBJFK10x7u2ieGTrH7nMojw-mail.gmail.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_138: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_qiaz6qpb-RLGHTddt3-MRycKyq-p9yKH-WgY-dXGt9g-mail.gmail.com_20260401_Re-Home-Forward-intake-packet/message.eml, dates=[]
% f_repo_solomon_mention_139: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_td3-bUMfrSqC-hw1-8z-T-n9WWZfK-yrTkUYRbuh1w-mail.gmail.com_20260327_Re-Home-Forward-intake-packet/message.json, dates=[]
% f_repo_solomon_mention_140: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_DS7PR08MB69740F395676C0CD72D36F6CB457A-DS7PR08MB6974.namprd08.prod.outlook.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_141: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0002-RE-Allegations-of-Fraud---JC-Household-72787eff4e5c4548bd1588bd9666f7c6-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_142: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0003-RE-Allegations-of-Fraud---JC-Household-8c104fe9322e4b528564e0cce04bab16-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_143: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0003-RE-Allegations-of-Fraud---JC-Household-72787eff4e5c4548bd1588bd9666f7c6-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_144: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0004-RE-Allegations-of-Fraud---JC-Household-8c104fe9322e4b528564e0cce04bab16-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_145: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0003-RE-Allegations-of-Fraud---JC-Household-72787eff4e5c4548bd1588bd9666f7c6-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_146: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0004-RE-Allegations-of-Fraud---JC-Household-8c104fe9322e4b528564e0cce04bab16-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_147: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0001-RE-Allegations-of-Fraud---JC-Household-e2acad46d8c743e9832ba3394350649f-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_148: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0002-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_-podn24hj6z0CzYzd1NgZ6V3CeF70SFo-k9Mo0kqP1Q-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_149: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0003-RE-Allegations-of-Fraud---JC-Household-51e29d4e881c463b817acfa07ba03501-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_150: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0004-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-QV6tDjyNxDccCRZTaX7ODcZwENYtG_RFKDhW5t2ZYmA-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_151: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0005-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_C3hZU40Kw1vBUviLQVK4-Z9XzCruocBWxnuvCR1JScA-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_152: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0006-RE-Allegations-of-Fraud---JC-Household-34ac4fce79eb42d1872ad12efa21dcdb-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_153: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0007-Re-Allegations-of-Fraud---JC-Household-CAMTdTS81WZ_rwpD7cX2edqjUMWXNd3hYe7oQTyXg_H-Hqmu5tA-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_154: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0008-RE-Allegations-of-Fraud---JC-Household-42d8c8e7ea0845c7ba039a669c32fc39-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_155: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0009-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-Ju0-vKZVkOUNe_1bzXc1jm_0xfbZwURHs1LC1dJW8QA-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_156: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0010-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_o-4qWcddDMrGzdA4rd5OvzXiOok2g_-BKCWJWF3qJFg-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_157: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0011-RE-Allegations-of-Fraud---JC-Household-c714b4b1e07348b08e939bd0c8f10431-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_158: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0012-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9_XT-RJqkeGndyUUwF-gUpo9vGeLevTdB2oHu-x8d88g-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_159: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0013-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8TA8O897A7r3HzpSkcXRnEdL9SffAD3pyjhVTQrQm94g-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_160: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0014-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_8pxVnRAMoaQ0n2oi1yBNnLNAiFSu4MFsTet-jJWJogQ-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_161: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0015-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-PY6irtR9JqOHMXPzbGj3nmEasRLYKWzcxj8kREPJ4rw-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_162: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0016-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8YkECQ4nXYCpk2WA0ebtLg-tjb-su85-sFK4Gy22B8mQ-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_163: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0017-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8tVRM73c2Pv36NZMV_ysr-0hTCW4rj-RECrGg5NmyCWw-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_164: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0018-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9BVkWkztr1qQBS-44j-TwOdH3x4jsJya847ej1nVKNTQ-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_165: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0019-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9_rTXe5kUn5Qea5gNfwanuQFM2RE-dQSkq9-NBquZv7g-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_166: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0020-RE-Allegations-of-Fraud---JC-Household-f55865f310fd4072ab3ccc58db2a8fa4-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_167: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0021-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8W-itOb6yrONyx42542HQJw-3Fg3kYD0mpBcGVdGDVPQ-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_168: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0022-RE-Allegations-of-Fraud---JC-Household-ff009564725a4e4c8b8bd8035a039c2b-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_169: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0023-RE-Allegations-of-Fraud---JC-Household-afab2672a15446ff849ee9c8d26441ce-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_170: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0024-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9FmdAP-2AfTjO4sKvByFvU072GzV_TfnThWCPpQtJcmQ-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_171: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0025-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8od6xLe4G-W16QCXpE2A0F5EgYY1b-7ncVZzMdJB9Ng-mail.gmail.com/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_172: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0026-Fwd-Allegations-of-Fraud---JC-Household-CAMTdTS8n7D-f43RH-QrFommUiuyG3-bM-rd_x4sNW-U-vR6v8Q-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_173: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0027-Fwd-Allegations-of-Fraud---JC-Household-CAMTdTS8Qs6qAUfLmxrRp6h8BsEgpXTKn9sf6d5bgg9RjJrjvHA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_174: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0028-RE-Allegations-of-Fraud---JC-Household-a9ee145bf1bd4c4b8799348137522007-clackamas.us/message.json, dates=['12/9/2025']
% f_repo_solomon_mention_175: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0029-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_1S-HhLQJd-W9qQce0PKVxZY_s-qeWnQJu8vo5xCr-nA-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_176: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0030-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8hJFZFApXJ_M-2KDpbdpp-xmiuPpmZMozt6W8wCgpCSw-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_177: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0031-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_mAMHJpYSHx4rzFOXJOrcdibzmTsGWhSB2srL-Qdr2GA-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_178: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0032-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-i6JBupA-zNyoaBoW_x9k3TxWGiu2eFv4Ded-WnM-V9A-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_179: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0033-RE-Allegations-of-Fraud---JC-Household-ec8a42cced534bb6b409dcd331d0129b-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_180: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0034-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9-M_ZLOAD-Tcg2FJAvRQ63sF8SGj_fQ02ajaxnvpe6_A-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_181: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0035-RE-Allegations-of-Fraud---JC-Household-601be3c663fe4a8c88b8536d33195032-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_182: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0036-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-K-FyjnOdwGC9tmC4Si5AUxKwfYk-GhTRQL1RoB74x-w-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_183: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0037-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9k8sGyni1u4UCq1SJq_2yBZ_UXXOCMGEHQBYDO1-oMPQ-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_184: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0038-RE-Allegations-of-Fraud---JC-Household-939eaa17e2694e0f8bd6f1c0cb83c729-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_185: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0039-Re-Allegations-of-Fraud---JC-Household-CAMTdTS8n7Wcg3KQZ_0f5qKDqtqzZvf8v0VWmNUp5TNAVYp2AoA-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_186: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0040-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_-9Le3G-MTpCW7W0PzDxM80hj9SqfCQWDBy1b9zEayUA-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_187: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0041-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9_z_FKWd-01Y-jg0iFqnH-QETocXkPd_rhe9oi3RfzMw-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_188: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0042-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9qJxwBU-BEWJJbH9-YEu0sYGuSa96naD--P8NQDfX9vw-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_189: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0043-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-3ZeyQLTEt4W-gdWhCzp4CtPQ3qkSd6yu3hUV-PVBa_A-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_190: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0044-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_dYgKzE9egEnAZ68dgzC9QuFSPMjMpE9DET-QX3dJPsg-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_191: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0045-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-OMJ-DVvS_nQH9mtK7wNAkC3-2O-1bOFSCAO5x0eZHzg-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_192: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0046-Re-Allegations-of-Fraud---JC-Household-CAMTdTS986uh21GjsGQoevv42N3OX9gqz-BhC-m4Fns-rEqTYFQ-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_193: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0047-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-00cFTv4dFf8yZ3NpPztCKwr2LB-on4Xxz-BFEv9_5jA-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_194: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0048-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-EBH-Kk7XM2aU5btp7WByE3F09iYJksws9fYbHfhHkw-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_195: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0050-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9sEsy4ed1KX7MexWW7tsdJA7h5uBVBEUtWhOOfPkggyg-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_196: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0051-Re-Allegations-of-Fraud---JC-Household-CAMTdTS9SiWxL2K2TbyYjWnSA1eFfgzeKxP6Z3o1CbF2cDBmUYw-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_197: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0052-RE-Allegations-of-Fraud---JC-Household-72787eff4e5c4548bd1588bd9666f7c6-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_198: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0053-Re-Allegations-of-Fraud---JC-Household-CAMTdTS_AduXnR9-vvL5riGMhm-39Z5jFZN1m_xzcXxsghkpNFQ-mail.gmail.com/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_199: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0054-RE-Allegations-of-Fraud---JC-Household-8c104fe9322e4b528564e0cce04bab16-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_200: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14159-solomon-gv-ed9289921a300dc7/event.json, dates=[]
% f_repo_solomon_mention_201: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14161-Me-to-solomon-gv-b2df7cbf8706d9fe/event.json, dates=[]
% f_repo_solomon_mention_202: status=verified, source=Collateral Estoppel/drafts/final_filing_set/05_certificate_of_service_final.md, dates=[]
% f_repo_solomon_mention_203: status=verified, source=Collateral Estoppel/drafts/final_filing_set/09_proposed_order_show_cause_final.md, dates=[]
% f_repo_solomon_mention_204: status=verified, source=Collateral Estoppel/drafts/final_filing_set/12_subpoena_duces_tecum_to_hacc_clackamas_county_final.md, dates=[]
% f_repo_solomon_mention_205: status=verified, source=Collateral Estoppel/drafts/final_filing_set/13_subpoena_duces_tecum_to_odhs_aps_custodian_final.md, dates=[]
% f_repo_solomon_mention_206: status=verified, source=Collateral Estoppel/drafts/final_filing_set/14_subpoena_duces_tecum_to_jason_hopkins_final.md, dates=[]
% f_repo_solomon_mention_207: status=verified, source=Collateral Estoppel/drafts/final_filing_set/15A_attachment_e1_tillamook_sheriff_requests_final.md, dates=[]
% f_repo_solomon_mention_208: status=verified, source=Collateral Estoppel/drafts/final_filing_set/15_subpoena_duces_tecum_to_tillamook_county_sheriff_custodian_final.md, dates=[]
% f_repo_solomon_mention_209: status=verified, source=Collateral Estoppel/drafts/final_filing_set/16_subpoena_duces_tecum_to_tillamook_911_custodian_final.md, dates=[]
% f_repo_solomon_mention_210: status=verified, source=Collateral Estoppel/drafts/final_filing_set/25_ready_to_serve_recipient_manifests_final.md, dates=[]
% f_repo_solomon_mention_211: status=verified, source=Collateral Estoppel/drafts/subpoena_schedule_hacc_re_exhibit_r.md, dates=[]
% f_repo_solomon_mention_212: status=verified, source=Collateral Estoppel/evidence_notes/motion_exhibit_crosswalk.md, dates=[]
% f_repo_solomon_mention_213: status=verified, source=Collateral Estoppel/drafts/final_filing_set/11A_attachment_a1_solomon_requests_final.md, dates=[]
% f_repo_solomon_mention_214: status=verified, source=Collateral Estoppel/drafts/final_filing_set/14A_attachment_d1_jason_hopkins_requests_final.md, dates=[]
% f_repo_solomon_mention_215: status=verified, source=Collateral Estoppel/drafts/final_filing_set/16A_attachment_f1_tillamook_911_requests_final.md, dates=[]
% f_repo_solomon_mention_216: status=verified, source=Collateral Estoppel/drafts/hacc_subpoena_target_list_re_exhibit_r.md, dates=[]
% f_repo_solomon_mention_217: status=verified, source=Collateral Estoppel/knowledge_graph/generated/README.md, dates=[]
% f_repo_solomon_mention_218: status=verified, source=evidence/email_imports/starworks5-additional-reimport-20260404/0033-Re-Additional-Information-Needed-CAMTdTS83ocm2akm6F9UWysjF6nz3pna0q9-aZ7Jvz-74gmqGdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_219: status=verified, source=evidence/email_imports/starworks5-additional-reimport-20260404/0034-Re-Additional-Information-Needed-CAMTdTS8PJBemAGgLrSov4AcGUQyokAi8hVr768y915Rrcrqbyw-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_220: status=verified, source=evidence/email_imports/starworks5-additional-reimport-20260404/0035-Re-Additional-Information-Needed-CAMTdTS9-_UtXTEBVmvh9sP3J3Hp2n1iFghSNJi97XukevU5aaA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_221: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0001-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_222: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0005-Re-Additional-Information-Needed-CAMTdTS83ocm2akm6F9UWysjF6nz3pna0q9-aZ7Jvz-74gmqGdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_223: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0006-Re-Additional-Information-Needed-CAMTdTS8PJBemAGgLrSov4AcGUQyokAi8hVr768y915Rrcrqbyw-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_224: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0009-Re-Additional-Information-Needed-CAMTdTS9-_UtXTEBVmvh9sP3J3Hp2n1iFghSNJi97XukevU5aaA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_225: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0010-RE-HCV-Orientation-f1e37f0f59304f0d8bcbcb606ee2f8be-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_226: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0011-RE-HCV-Orientation-07246b509c0f4d7c8d69f58da8f5e205-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_227: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli-filtered/0012-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_228: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0002-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_229: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0006-Re-Additional-Information-Needed-CAMTdTS83ocm2akm6F9UWysjF6nz3pna0q9-aZ7Jvz-74gmqGdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_230: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0007-Re-Additional-Information-Needed-CAMTdTS8PJBemAGgLrSov4AcGUQyokAi8hVr768y915Rrcrqbyw-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_231: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0012-Re-Additional-Information-Needed-CAMTdTS9-_UtXTEBVmvh9sP3J3Hp2n1iFghSNJi97XukevU5aaA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_232: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0013-RE-HCV-Orientation-f1e37f0f59304f0d8bcbcb606ee2f8be-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_233: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0014-RE-HCV-Orientation-07246b509c0f4d7c8d69f58da8f5e205-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_234: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import-cli/0015-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_235: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0002-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_236: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0006-Re-Additional-Information-Needed-CAMTdTS83ocm2akm6F9UWysjF6nz3pna0q9-aZ7Jvz-74gmqGdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_237: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0007-Re-Additional-Information-Needed-CAMTdTS8PJBemAGgLrSov4AcGUQyokAi8hVr768y915Rrcrqbyw-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_238: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0012-Re-Additional-Information-Needed-CAMTdTS9-_UtXTEBVmvh9sP3J3Hp2n1iFghSNJi97XukevU5aaA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_239: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0013-RE-HCV-Orientation-f1e37f0f59304f0d8bcbcb606ee2f8be-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_240: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0014-RE-HCV-Orientation-07246b509c0f4d7c8d69f58da8f5e205-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_241: status=verified, source=evidence/email_imports/starworks5-confirmed-case-import/0015-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_242: status=verified, source=evidence/email_imports/starworks5-fraud-reimport-20260404/0049-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/message.json, dates=['12-1-2024', '12-1-2025', '12-31-2025']
% f_repo_solomon_mention_243: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0016-Re-HCV-Orientation-CAMTdTS8krRLqrv62_DYwGHwvNiuLomQBb6guRUxLxFqbOv16ZA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_244: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_245: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0018-Re-HCV-Orientation-CAMTdTS_8qnH3NG-ZNPUa-uAJG6tCH2aBdJZ7RA-TccPo-e5vQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_246: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0019-RE-HCV-Orientation-07246b509c0f4d7c8d69f58da8f5e205-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_247: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0020-Re-HCV-Orientation-CAMTdTS8wxYC9a01Qyhgzhk7C19ocZ2gpEc-P78V_wRTQkDN7hg-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_248: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0021-RE-HCV-Orientation-f1e37f0f59304f0d8bcbcb606ee2f8be-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_249: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0022-Re-HCV-Orientation-CAMTdTS8ufb7ONCc-MorzA4j49Wc_DZj1sXURpHSut-uyAE7QdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_250: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0023-Re-HCV-Orientation-CAMTdTS-P2WrnnNn7ZHJVGwyxmidnr-LsfQR-wGbZckgYnKMyfQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_251: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0024-Re-HCV-Orientation-CAMTdTS9bg00mw8vaCYD5PrG_sc-6Piz_Ws17GmeD-4-tPZHx-A-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_252: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0025-Re-HCV-Orientation-CAMTdTS8NwnM6aAhiY-HeY2Bs4EosOn2W790KYdvq-tzDKZUwPQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_253: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404-narrow/0026-Re-HCV-Orientation-CAMTdTS_jUi7EBW-d4uabncxb0bNXeOuJUp59T-d1nJFwnymZbA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_254: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0016-Re-HCV-Orientation-CAMTdTS8krRLqrv62_DYwGHwvNiuLomQBb6guRUxLxFqbOv16ZA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_255: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0017-RE-HCV-Orientation-a0136cad0c5f44b984403575346f8d34-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_256: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0018-Re-HCV-Orientation-CAMTdTS_8qnH3NG-ZNPUa-uAJG6tCH2aBdJZ7RA-TccPo-e5vQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_257: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0019-RE-HCV-Orientation-07246b509c0f4d7c8d69f58da8f5e205-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_258: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0020-Re-HCV-Orientation-CAMTdTS8wxYC9a01Qyhgzhk7C19ocZ2gpEc-P78V_wRTQkDN7hg-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_259: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0021-RE-HCV-Orientation-f1e37f0f59304f0d8bcbcb606ee2f8be-clackamas.us/message.json, dates=[]
% f_repo_solomon_mention_260: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0022-Re-HCV-Orientation-CAMTdTS8ufb7ONCc-MorzA4j49Wc_DZj1sXURpHSut-uyAE7QdA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_261: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0023-Re-HCV-Orientation-CAMTdTS-P2WrnnNn7ZHJVGwyxmidnr-LsfQR-wGbZckgYnKMyfQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_262: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0024-Re-HCV-Orientation-CAMTdTS9bg00mw8vaCYD5PrG_sc-6Piz_Ws17GmeD-4-tPZHx-A-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_263: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0025-Re-HCV-Orientation-CAMTdTS8NwnM6aAhiY-HeY2Bs4EosOn2W790KYdvq-tzDKZUwPQ-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_264: status=verified, source=evidence/email_imports/starworks5-hcv-reimport-20260404/0026-Re-HCV-Orientation-CAMTdTS_jUi7EBW-d4uabncxb0bNXeOuJUp59T-d1nJFwnymZbA-mail.gmail.com/message.json, dates=[]
% f_repo_solomon_mention_265: status=verified, source=Collateral Estoppel/drafts/defendants_first_targeted_discovery_requests_re_exhibit_r.md, dates=[]
% f_repo_solomon_mention_266: status=verified, source=Collateral Estoppel/drafts/final_filing_set/00_exhibit_legend_global.md, dates=[]
% f_repo_solomon_mention_267: status=verified, source=Collateral Estoppel/drafts/final_filing_set/20_subpoena_packet_assembly_matrix_final.md, dates=[]
% f_repo_solomon_mention_268: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS8rowgBct-5GFqbfUtOoJ3GBJFK10x7u2ieGTrH7nMojw-mail.gmail.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.eml, dates=[]
% f_repo_solomon_mention_269: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_CAMTdTS_J-aa213z8ZxDUrHziZ5q6o4FajDX1s9gZHdnQwRfpFg-mail.gmail.com_20260401_Re-Automatic-reply-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.json, dates=[]
% f_repo_solomon_mention_270: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_DS7PR08MB69744AC53FD7853FFDC9275EB457A-DS7PR08MB6974.namprd08.prod.outlook.com_20260327_Re-Application-to-live-at-the-Vera---Jane-Cortez-Benjamin-Barber/message.eml, dates=[]
% f_repo_solomon_mention_271: status=verified, source=Collateral Estoppel/drafts/final_filing_set/17_certificate_of_service_subpoenas_final.md, dates=[]
% f_repo_solomon_mention_272: status=verified, source=Collateral Estoppel/drafts/final_filing_set/32_deadline_update_log_2026-04-07.md, dates=['2026-04-07']
% f_repo_solomon_mention_273: status=verified, source=Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md, dates=[]
% f_repo_solomon_mention_274: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14160-Me-to-solomon-gv-7cb858000dea7723/transcript.txt, dates=[]
% f_repo_solomon_mention_275: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14165-Me-to-solomon-gv-e6594297d713efde/transcript.txt, dates=[]
% f_repo_solomon_mention_276: status=verified, source=Collateral Estoppel/drafts/final_filing_set/13A_attachment_c1_odhs_aps_requests_final.md, dates=[]
% f_repo_solomon_mention_277: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14163-Me-to-solomon-gv-7540e6c07566a84a/transcript.txt, dates=[]
% f_repo_solomon_mention_278: status=verified, source=Collateral Estoppel/drafts/final_filing_set/29_active_service_log_2026-04-07.md, dates=['2026-04-07']
% f_repo_solomon_mention_279: status=verified, source=Collateral Estoppel/knowledge_graph/generated/service_log_validation_report_2026-04-07.json, dates=['2026-04-07']
% f_repo_solomon_mention_280: status=verified, source=Collateral Estoppel/knowledge_graph/generated/service_log_validation_report_2026-04-07.md, dates=['2026-04-07']
% f_repo_solomon_mention_281: status=verified, source=Collateral Estoppel/research/oregon_authority_grounding_memo_2026-04-07.md, dates=['2026-04-07']
% f_repo_solomon_mention_282: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_4fkbwL67GdzMwfhs-pca303smtpl135_20260329_Signature-status-of-Rental-Criteria/message.eml, dates=[]
% f_repo_solomon_mention_283: status=verified, source=evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/0000000-0000999/msg_4fkcZd6yLSzMwj2f-pca303smtpl135_20260329_Signature-status-of-Rental-Criteria/message.eml, dates=[]
% f_repo_solomon_mention_284: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/10078-Group-Conversation-gv-a65a0e92fa1a752c/event.json, dates=[]
% f_repo_solomon_mention_285: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/13484-Me-to-lawyer-gv-cafab0f59301f626/event.json, dates=[]
% f_repo_solomon_mention_286: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/13484-Me-to-lawyer-gv-cafab0f59301f626/transcript.txt, dates=[]
% f_repo_solomon_mention_287: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14159-solomon-gv-ed9289921a300dc7/transcript.txt, dates=[]
% f_repo_solomon_mention_288: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14161-Me-to-solomon-gv-b2df7cbf8706d9fe/transcript.txt, dates=[]
% f_repo_solomon_mention_289: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14164-Me-to-solomon-gv-3f38fb3f900d4de1/enrichments/solomon - Text - 2025-11-20T19_06_58Z-13-1.image_ocr.txt, dates=[]
% f_repo_solomon_mention_290: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/14166-Me-to-solomon-gv-0eb16863d122188b/enrichments/solomon - Text - 2026-03-10T17_36_48Z-3-1.image_ocr.txt, dates=[]
% f_repo_solomon_mention_291: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/9921-Me-to-Commissioner-Bob-Terry-gv-f6e4974c25e3c5e5/event.json, dates=[]
% f_repo_solomon_mention_292: status=verified, source=evidence/email_imports/starworks5-google-voice-takeout-20260404-fixed-materialized/9921-Me-to-Commissioner-Bob-Terry-gv-f6e4974c25e3c5e5/transcript.txt, dates=[]
% f_active_service_log_initialized: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_subpoena_recipients_ready_to_serve: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_subpoena_service_completed_any: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_subpoena_pre_service_phase_only: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_deficiency_notice_sent_any: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_subpoena_response_incomplete_any: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']
% f_motion_to_compel_stage_any: status=verified, source=28_active_service_log_2026-04-07.csv, dates=['2026-04-07']

% Rule mapping comments
% r1_guardian_permission_if_prior_appointment: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
% r2_noninterference_prohibition_for_benjamin: If prior appointment exists and interference is alleged, Benjamin is forbidden from interference.
% r3_benjamin_obligation_comply_or_seek_relief: If prior appointment is in force and Benjamin disregarded order, Benjamin was obligated to comply or seek relief.
% r4_solomon_forbidden_abuse_contact_property_control: Given granted in-effect restraining order with property restrictions, Solomon is forbidden to abuse/contact/interfere/control property.
% r4b_solomon_forbidden_enter_residence: Given the granted restraining order and residence restriction, Solomon is forbidden from entering or remaining at the protected residence.
% r5_solomon_obligated_appear_and_answer: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
% r5b_solomon_obligated_seek_hearing_or_comply: If Solomon stated he would comply only once served despite an already in-effect order, he was obligated to seek a hearing or comply rather than self-suspend effectiveness.
% r5c_solomon_forbidden_self_help_noncooperation: If Solomon adopted an explicit noncooperation posture after the granted in-effect order, self-help noncooperation is forbidden.
% r6_hacc_obligated_document_authority_chain_for_lease_change: If HACC states that a lease change followed internal review and court documentation on file, HACC is obligated in this model to identify the actor, document, and authority chain behind that change.
% r6b_hacc_obligated_document_lease_basis: If HACC implemented a January 1, 2026 lease adjustment, HACC was obligated to document the basis for that household-composition change.
% r6c_solomon_interference_not_proved_by_named_hacc_notice_gap: Because no named HACC notice message about the Solomon order has been found in preserved mail, the HACC-interference theory should presently be treated as an inference rather than direct proof.
% r6d_case_obligated_treat_prior_appointment_as_hypothesis_only: If no source order has been found for the claimed prior appointment, the prior-appointment theory must remain hypothesis-only in filing-facing outputs.
% r6e_case_permitted_seek_compelled_production_for_hacc_actor_chain: If local search did not locate the HACC actor-identification record and compelled production is required, the case posture is permitted to pursue Exhibit R production.
% r7_solomon_forbidden_refile_precluded_issue: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
% r8_solomon_notice_ack_triggers_court_relief_path: If Solomon acknowledged awareness of restraining order and the order is in effect, Solomon is obligated to seek court relief rather than self-help noncompliance.
% r9_solomon_wait_for_service_conflicts_with_no_further_service: If Solomon stated he would wait for service but the order states no further service needed due to appearance, conditioning compliance on extra service is forbidden in this model.
% r10_solomon_noncooperation_statement_conflicts_with_effective_order: If Solomon states non-incentivized cooperation while order is in effect, intentional noncooperation is forbidden in this model.
% r11_solomon_already_have_order_statement_supports_notice: If Solomon stated the other party already had the restraining order and order is in effect, Solomon is obligated to recognize existing order status.
% r12_solomon_order_not_in_effect_claim_conflicts_with_effective_order: If Solomon states the order is not in effect while the order is in effect, asserting ineffectiveness without court relief is forbidden in this model.
% r13_solomon_judge_overturn_statement_triggers_motion_path: If Solomon states he would have the judge overturn the order while it is in effect, he is obligated to seek court modification before noncompliance.
% r14_hacc_notice_of_restrained_party_contact_triggers_noncontact_handling: If HACC is told that Jane is receiving calls about a restrained brother and third-party housing contact is occurring with a restrained person, HACC is obligated in this model to stop that contact path and document the response.
% r15_benjamin_permitted_serve_subpoena_packets: If subpoena workflow components are staged and recipients are ready-to-serve, Benjamin is permitted to serve the staged subpoena packets.
% r16_benjamin_obligated_track_service_and_deadlines: If service log and workflow components exist, Benjamin is obligated in this model to maintain service/deadline tracking.
% r17_responding_custodian_obligated_execute_or_query_protocol_upon_service: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
% r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
% r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
% r20_case_permitted_treat_enforcement_path_as_pending_pre_service: If no subpoena service is yet completed, subpoena-enforcement motion path remains pending pre-service in this model.
% r21_case_obligated_resolve_actor_assignment_conflict: If the model contains a Benjamin-vs-Solomon interference actor conflict, the case posture is obligated to resolve that assignment with source records before final legal attribution.
% r22_case_obligated_finalize_authority_citations_before_filing: If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.
% r23_case_permitted_initiate_remedial_contempt_path: If remedial-contempt authority is available and the record includes an in-effect order plus Solomon's service-position statement, the case posture is permitted to pursue a remedial contempt or show-cause path.
% r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved: If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.
% r25_case_permitted_seek_remedial_contempt_sanctions_if_elements_proved: If remedial-sanctions authority is available and prejudice-related housing change is documented, the case posture may seek compensatory or compliance-oriented remedial sanctions if contempt elements are later proved.
% r26_case_permitted_seek_orcp17_sanctions_if_improper_purpose_or_no_support_is_shown: If ORCP 17 authority is available, the case posture may seek filing-related sanctions if improper purpose or inadequate factual/legal support is shown; current proof-state cautions remain in force.
% r27_case_permitted_seek_subpoena_enforcement_under_orcp55_and_orcp46: If subpoena-obedience and discovery-sanctions authority are available and compelled production is required, the case posture may pursue subpoena enforcement and related expense-shifting when the required noncompliance predicate is met.
% r28_case_permitted_apply_orcp_and_oec_in_protective_proceeding: If ORS 125.050 authority is available and the protective petition is filed, the proceeding may apply ORCP and the Oregon Evidence Code except where chapter 125 provides otherwise.
% r29_case_obligated_preserve_notice_and_objection_window: If chapter 125 notice authorities are available and notice issued to the respondent, the proceeding is obligated to preserve the statutory notice and objection framework.
% r30_case_obligated_schedule_hearing_on_presented_objection: If objection and hearing authorities are available and the packet includes a respondent objection form, the proceeding is obligated in this model to route the matter through the objection-hearing path.
% r31_case_permitted_assert_protective_person_right_to_appear_or_have_counsel: If ORS 125.080 authority is available and notice has issued, the case posture may assert the protected person's right to appear in person or by counsel at hearing.
% r32_case_permitted_use_orcp9_and_orcp10_for_motion_packet_service_and_deadlines: If ORCP 9 and ORCP 10 authority are available, the case posture may use those rules for service and deadline computation on later-filed motion packets, subject to more specific chapter 125 notice rules where applicable.
