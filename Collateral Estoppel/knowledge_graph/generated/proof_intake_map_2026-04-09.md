# Proof Intake Map

Generated: 2026-04-09

## Mode: strict
- Active: 42
- Unresolved: 6
- Inactive: 4

### UNRESOLVED - r1_guardian_permission_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.

### UNRESOLVED - r2_target_noninterference_prohibition_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists and interference is alleged, the alleged interfering actor is forbidden from interference.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_solomon_housing_interference: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/motion_exhibit_index.md
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r3_target_obligation_comply_or_seek_relief_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment is in force and an alleged actor disregarded the order, that actor was obligated to comply or seek relief.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_solomon_order_disregard: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r5_solomon_obligated_appear_and_answer
- Track: hypothesis
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Authority refs: order:eppdapa_restraining_order
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_restraining_order_no_further_service_needed: value=True status=verified source=sam_barber_restraining_order_ocr.txt
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### UNRESOLVED - r7_solomon_forbidden_refile_precluded_issue
- Track: hypothesis
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Authority refs: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_issue_preclusion_elements_official_oregon_cases: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_authority_issue_preclusion_requires_prior_separate_proceeding: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_collateral_estoppel_candidate: value=True status=theory source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md
- Action: Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency.
- f_client_solomon_barred_refile: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md
- Action: Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart.

### UNRESOLVED - r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved
- Track: filing
- Description: If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.
- Authority refs: auth:ors_33_075
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_33_075_compel_appearance: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### INACTIVE - r17_responding_custodian_obligated_execute_or_query_protocol_upon_service
- Track: workflow
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Authority refs: auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_subpoena_service_completed_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_or_joined_search_protocol_defined: value=True status=verified source=11B_attachment_a2_definitions_and_instructions_final.md
- Action: No immediate action required for this antecedent.

### INACTIVE - r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response
- Track: workflow
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_subpoena_response_incomplete_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage
- Track: workflow
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_deficiency_notice_sent_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r22_case_obligated_finalize_authority_citations_before_filing
- Track: filing
- Description: If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.
- Authority refs: auth:orcp_17_c
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_authority_table_placeholders_unresolved: value=False status=verified source=06_oregon_authority_table_final.md
- Action: Replace placeholder citations with finalized ORS/ORCP/case authority entries, then regenerate artifacts.

## Mode: inclusive
- Active: 43
- Unresolved: 5
- Inactive: 4

### UNRESOLVED - r1_guardian_permission_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.

### UNRESOLVED - r2_target_noninterference_prohibition_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists and interference is alleged, the alleged interfering actor is forbidden from interference.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_solomon_housing_interference: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/motion_exhibit_index.md
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r3_target_obligation_comply_or_seek_relief_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment is in force and an alleged actor disregarded the order, that actor was obligated to comply or seek relief.
- Authority refs: auth:ors_125_050
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_125_050_protective_orcp_oec: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_prior_appointment: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_solomon_order_disregard: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r5_solomon_obligated_appear_and_answer
- Track: hypothesis
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Authority refs: order:eppdapa_restraining_order
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_restraining_order_no_further_service_needed: value=True status=verified source=sam_barber_restraining_order_ocr.txt
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### UNRESOLVED - r7_solomon_forbidden_refile_precluded_issue
- Track: hypothesis
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Authority refs: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_issue_preclusion_elements_official_oregon_cases: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_authority_issue_preclusion_requires_prior_separate_proceeding: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_collateral_estoppel_candidate: value=True status=theory source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md
- Action: Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency.
- f_client_solomon_barred_refile: value=True status=alleged source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md
- Action: Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart.

### INACTIVE - r17_responding_custodian_obligated_execute_or_query_protocol_upon_service
- Track: workflow
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Authority refs: auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_subpoena_service_completed_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_or_joined_search_protocol_defined: value=True status=verified source=11B_attachment_a2_definitions_and_instructions_final.md
- Action: No immediate action required for this antecedent.

### INACTIVE - r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response
- Track: workflow
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_subpoena_response_incomplete_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage
- Track: workflow
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_deficiency_notice_sent_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r22_case_obligated_finalize_authority_citations_before_filing
- Track: filing
- Description: If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.
- Authority refs: auth:orcp_17_c
- Activation estimate: 2026-04-09
- Antecedent intake:
- f_authority_table_placeholders_unresolved: value=False status=verified source=06_oregon_authority_table_final.md
- Action: Replace placeholder citations with finalized ORS/ORCP/case authority entries, then regenerate artifacts.

