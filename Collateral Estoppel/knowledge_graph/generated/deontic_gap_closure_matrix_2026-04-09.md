# Deontic Gap Closure Matrix

Generated: 2026-04-09

## Strict Mode Counts
- active=42 unresolved=6 inactive=4

## Rule Closure Matrix
### r1_guardian_permission_if_prior_appointment (unresolved)
- Track: hypothesis
- Authority refs: auth:ors_125_050
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Blocking antecedents:
- f_client_prior_appointment status=alleged value=true
- Closure actions:
- f_client_prior_appointment: Obtain certified guardianship appointment order/docket showing appointment identity and effective date. (source: /home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md)
- Recommended packets/workstreams: packet_prior_appointment_r1_r2_r3
- F-logic requirements:
- `need_verified(f_client_prior_appointment).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r1_guardian_permission_if_prior_appointment, f_client_prior_appointment).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_prior_appointment, true, T).`

### r2_target_noninterference_prohibition_if_prior_appointment (unresolved)
- Track: hypothesis
- Authority refs: auth:ors_125_050
- Description: If prior appointment exists and interference is alleged, the alleged interfering actor is forbidden from interference.
- Blocking antecedents:
- f_client_prior_appointment status=alleged value=true
- f_client_solomon_housing_interference status=alleged value=true
- Closure actions:
- f_client_prior_appointment: Obtain certified guardianship appointment order/docket showing appointment identity and effective date. (source: /home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md)
- f_client_solomon_housing_interference: Convert allegation to verified with certified records, transcripts, or authenticated communications. (source: /home/barberb/HACC/Collateral Estoppel/evidence_notes/motion_exhibit_index.md)
- Recommended packets/workstreams: packet_prior_appointment_r1_r2_r3
- F-logic requirements:
- `need_verified(f_client_prior_appointment).`
- `need_verified(f_client_solomon_housing_interference).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r2_target_noninterference_prohibition_if_prior_appointment, f_client_prior_appointment).`
- `requires_need_verified(r2_target_noninterference_prohibition_if_prior_appointment, f_client_solomon_housing_interference).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_prior_appointment, true, T).`
- `requires_holds_at(f_client_solomon_housing_interference, true, T).`

### r3_target_obligation_comply_or_seek_relief_if_prior_appointment (unresolved)
- Track: hypothesis
- Authority refs: auth:ors_125_050
- Description: If prior appointment is in force and an alleged actor disregarded the order, that actor was obligated to comply or seek relief.
- Blocking antecedents:
- f_client_prior_appointment status=alleged value=true
- f_client_solomon_order_disregard status=alleged value=true
- Closure actions:
- f_client_prior_appointment: Obtain certified guardianship appointment order/docket showing appointment identity and effective date. (source: /home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md)
- f_client_solomon_order_disregard: Convert allegation to verified with certified records, transcripts, or authenticated communications. (source: /home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md)
- Recommended packets/workstreams: packet_prior_appointment_r1_r2_r3
- F-logic requirements:
- `need_verified(f_client_prior_appointment).`
- `need_verified(f_client_solomon_order_disregard).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r3_target_obligation_comply_or_seek_relief_if_prior_appointment, f_client_prior_appointment).`
- `requires_need_verified(r3_target_obligation_comply_or_seek_relief_if_prior_appointment, f_client_solomon_order_disregard).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_prior_appointment, true, T).`
- `requires_holds_at(f_client_solomon_order_disregard, true, T).`

### r5_solomon_obligated_appear_and_answer (unresolved)
- Track: hypothesis
- Authority refs: order:eppdapa_restraining_order
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Blocking antecedents:
- f_client_solomon_failed_appearance status=alleged value=true
- Closure actions:
- f_client_solomon_failed_appearance: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation. (source: /home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md)
- Recommended packets/workstreams: packet_nonappearance_r24
- F-logic requirements:
- `need_verified(f_client_solomon_failed_appearance).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r5_solomon_obligated_appear_and_answer, f_client_solomon_failed_appearance).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_solomon_failed_appearance, true, T).`

### r7_solomon_forbidden_refile_precluded_issue (unresolved)
- Track: hypothesis
- Authority refs: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Blocking antecedents:
- f_collateral_estoppel_candidate status=theory value=true
- f_client_solomon_barred_refile status=alleged value=true
- Closure actions:
- f_collateral_estoppel_candidate: Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency. (source: /home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md)
- f_client_solomon_barred_refile: Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart. (source: /home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md)
- Recommended packets/workstreams: packet_issue_preclusion_r7
- F-logic requirements:
- `need_verified(f_client_solomon_barred_refile).`
- `need_verified(f_collateral_estoppel_candidate).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r7_solomon_forbidden_refile_precluded_issue, f_client_solomon_barred_refile).`
- `requires_need_verified(r7_solomon_forbidden_refile_precluded_issue, f_collateral_estoppel_candidate).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_solomon_barred_refile, true, T).`
- `requires_holds_at(f_collateral_estoppel_candidate, true, T).`

### r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved (unresolved)
- Track: filing
- Authority refs: auth:ors_33_075
- Description: If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.
- Blocking antecedents:
- f_client_solomon_failed_appearance status=alleged value=true
- Closure actions:
- f_client_solomon_failed_appearance: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation. (source: /home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md)
- Recommended packets/workstreams: packet_nonappearance_r24
- F-logic requirements:
- `need_verified(f_client_solomon_failed_appearance).`
- Temporal-deontic FOL requirements:
- `requires_need_verified(r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved, f_client_solomon_failed_appearance).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_client_solomon_failed_appearance, true, T).`

### r17_responding_custodian_obligated_execute_or_query_protocol_upon_service (inactive)
- Track: workflow
- Authority refs: auth:orcp_55
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Blocking antecedents:
- f_subpoena_service_completed_any status=verified value=false
- Closure actions:
- f_subpoena_service_completed_any: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts. (source: 28_active_service_log_2026-04-07.csv)
- Recommended packets/workstreams: service_log_progression_r17_r18_r19
- F-logic requirements:
- `need_true(f_subpoena_service_completed_any).`
- Temporal-deontic FOL requirements:
- `requires_need_true(r17_responding_custodian_obligated_execute_or_query_protocol_upon_service, f_subpoena_service_completed_any).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_subpoena_service_completed_any, true, T).`

### r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response (inactive)
- Track: workflow
- Authority refs: auth:orcp_46, auth:orcp_55
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Blocking antecedents:
- f_subpoena_response_incomplete_any status=verified value=false
- Closure actions:
- f_subpoena_response_incomplete_any: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts. (source: 28_active_service_log_2026-04-07.csv)
- Recommended packets/workstreams: service_log_progression_r17_r18_r19
- F-logic requirements:
- `need_true(f_subpoena_response_incomplete_any).`
- Temporal-deontic FOL requirements:
- `requires_need_true(r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response, f_subpoena_response_incomplete_any).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_subpoena_response_incomplete_any, true, T).`

### r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage (inactive)
- Track: workflow
- Authority refs: auth:orcp_46, auth:orcp_55
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Blocking antecedents:
- f_deficiency_notice_sent_any status=verified value=false
- Closure actions:
- f_deficiency_notice_sent_any: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false. (source: 28_active_service_log_2026-04-07.csv)
- Recommended packets/workstreams: service_log_progression_r17_r18_r19
- F-logic requirements:
- `need_true(f_deficiency_notice_sent_any).`
- Temporal-deontic FOL requirements:
- `requires_need_true(r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage, f_deficiency_notice_sent_any).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_deficiency_notice_sent_any, true, T).`

### r22_case_obligated_finalize_authority_citations_before_filing (inactive)
- Track: filing
- Authority refs: auth:orcp_17_c
- Description: If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.
- Blocking antecedents:
- f_authority_table_placeholders_unresolved status=verified value=false
- Closure actions:
- f_authority_table_placeholders_unresolved: Replace placeholder citations with finalized ORS/ORCP/case authority entries, then regenerate artifacts. (source: 06_oregon_authority_table_final.md)
- Recommended packets/workstreams: authority_table_finalization_r22
- F-logic requirements:
- `need_true(f_authority_table_placeholders_unresolved).`
- Temporal-deontic FOL requirements:
- `requires_need_true(r22_case_obligated_finalize_authority_citations_before_filing, f_authority_table_placeholders_unresolved).`
- Deontic event-calculus requirements:
- `requires_holds_at(f_authority_table_placeholders_unresolved, true, T).`

## Open Element Audits
### audit_remedial_contempt_timing
- Label: Remedial contempt timing audit
- Governing authority: auth:ors_33_055, auth:ors_33_075, auth:ors_33_105
- Interval refs: ti_restraining_order_effective_period
- Open elements:
- service_or_appearance_record status=proof_gated note=The local repository supports notice strongly, but a cleaner certified docket / appearance record remains preferable for filing-grade contempt proof.

### audit_exhibit_r_subpoena_timing
- Label: Exhibit R subpoena timing audit
- Governing authority: auth:orcp_55, auth:orcp_46
- Interval refs: ti_exhibit_r_compelled_production_track
- Open elements:
- service_stage_complete status=missing note=Promotes automatically from the active service log once any subpoena service is logged.
- deficiency_or_compel_stage status=missing note=Promotes automatically from the active service log when a deficiency notice or motion-to-compel stage is entered.

### audit_orcp17_sanctions_elements
- Label: ORCP 17 sanctions element audit
- Governing authority: auth:orcp_17_c
- Interval refs: (none)
- Open elements:
- improper_purpose_or_unsupported_filing_proof status=proof_gated note=The current record supports inquiry and caution, but final ORCP 17 findings still require the filing-by-filing manifest to identify the challenged filing and map the specific sanction predicates.
- improper_purpose_mapped status=proof_gated note=Current candidate theory only: the challenged filing may have functioned to obtain control, create delay, or exert collateral pressure rather than to seek only properly bounded judicial relief. This remains proof-gated and should not be treated as established absent stronger filing-specific record support.
- unsupported_legal_position_mapped status=proof_gated note=Current candidate theory only: the challenged filing may depend on a legal position that becomes unsupported if certified prior-proceeding materials and completed issue-preclusion mapping later show that the filing sought to relitigate an already-resolved authority issue. This remains proof-gated.
- unsupported_factual_assertion_mapped status=proof_gated note=Current candidate theory only: the petition-side statement that no guardian had previously been appointed for Jane Cortez may become a contradicted factual assertion if a certified prior appointment order is later staged and verified. This remains proof-gated.

### audit_issue_preclusion_elements
- Label: Issue-preclusion element audit
- Governing authority: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
- Interval refs: (none)
- Open elements:
- candidate_refile_theory status=proof_gated note=The local model carries a barred-refile candidate theory, but not yet a certified prior proceeding record proving application of the doctrine.
- prior_separate_proceeding_record status=missing note=Promotes automatically when certified prior-order and docket/register materials are staged in evidence_notes/certified_records.
- identical_issue_and_finality_mapping status=proof_gated note=These elements remain open until certified prior-order, docket, and hearing materials are staged and the issue_preclusion_mapping.json manifest marks the element mapping complete.
- identical_issue_mapped status=proof_gated note=Candidate sources indicate potential overlap of the guardianship authority issue across filings. Candidate references: Collateral Estoppel/evidence_notes/missing_exhibit_search_status_2026-04-07.md; Collateral Estoppel/evidence_notes/repeated_usurpation_pattern_memo.md; Collateral Estoppel/drafts/petition_guardianship_packet_stage1.md; Collateral Estoppel/drafts/petition_guardianship_court_ready_shell.md
- finality_mapped status=proof_gated note=Current index did not yield reliable finality artifacts; certified final order and register are still required. Candidate references: Collateral Estoppel/evidence_notes/sam_barber_restraining_order_ocr.txt; Collateral Estoppel/evidence_notes/solomon_order_completeness_checklist.md; Collateral Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md; Collateral Estoppel/drafts/petition_guardianship_working_memo.md
- party_privity_mapped status=proof_gated note=Candidate sources indicate party-name overlap, but party/privity mapping remains uncertified. Candidate references: Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.md; Collateral Estoppel/drafts/motion_for_leave_or_to_compel_exhibit_r_production.md; Collateral Estoppel/drafts/final_filing_set/11B_attachment_a2_definitions_and_instructions_final.md; Collateral Estoppel/evidence_notes/protective_order_and_hacc_notice_timeline.md
- full_fair_opportunity_mapped status=proof_gated note=Current index did not yield reliable hearing/opportunity artifacts; certified appearance/hearing records are still required. Candidate references: Collateral Estoppel/drafts/final_filing_set/06_oregon_authority_table_final.md; Collateral Estoppel/evidence_notes/formal_case_state_dashboard_2026-04-07.md; Collateral Estoppel/evidence_notes/element_audit_layer_note_2026-04-07.md; Collateral Estoppel/evidence_notes/solomon_order_completeness_checklist.md
