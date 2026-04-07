# Proof Intake Map

Generated: 2026-04-07

## Mode: strict
- Active: 30
- Unresolved: 6
- Inactive: 3

### UNRESOLVED - r1_guardian_permission_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.

### UNRESOLVED - r2_noninterference_prohibition_for_benjamin
- Track: hypothesis
- Description: If prior appointment exists and interference is alleged, Benjamin is forbidden from interference.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_benjamin_housing_interference: value=True status=alleged source=client_assertion
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r3_benjamin_obligation_comply_or_seek_relief
- Track: hypothesis
- Description: If prior appointment is in force and Benjamin disregarded order, Benjamin was obligated to comply or seek relief.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_benjamin_order_disregard: value=True status=alleged source=client_assertion
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r5_solomon_obligated_appear_and_answer
- Track: hypothesis
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Authority refs: order:eppdapa_restraining_order
- Activation estimate: 2026-03-10
- Antecedent intake:
- f_restraining_order_no_further_service_needed: value=True status=verified source=sam_barber_restraining_order_ocr.txt
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=client_assertion
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### UNRESOLVED - r7_solomon_forbidden_refile_precluded_issue
- Track: hypothesis
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Authority refs: none
- Activation estimate: 2026-03-31
- Antecedent intake:
- f_collateral_estoppel_candidate: value=True status=theory source=motion_to_dismiss_for_collateral_estoppel.md
- Action: Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency.
- f_client_solomon_barred_refile: value=True status=alleged source=client_assertion
- Action: Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart.

### UNRESOLVED - r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved
- Track: filing
- Description: If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.
- Authority refs: auth:ors_33_075
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_authority_ors_33_075_compel_appearance: value=True status=verified source=oregon_authority_grounding_memo_2026-04-07.md
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=client_assertion
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### INACTIVE - r17_responding_custodian_obligated_execute_or_query_protocol_upon_service
- Track: workflow
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Authority refs: auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_subpoena_service_completed_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_or_joined_search_protocol_defined: value=False status=verified source=11B_attachment_a2_definitions_and_instructions_final.md
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.

### INACTIVE - r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response
- Track: workflow
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_subpoena_response_incomplete_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage
- Track: workflow
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_deficiency_notice_sent_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

## Mode: inclusive
- Active: 31
- Unresolved: 5
- Inactive: 3

### UNRESOLVED - r1_guardian_permission_if_prior_appointment
- Track: hypothesis
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.

### UNRESOLVED - r2_noninterference_prohibition_for_benjamin
- Track: hypothesis
- Description: If prior appointment exists and interference is alleged, Benjamin is forbidden from interference.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_benjamin_housing_interference: value=True status=alleged source=client_assertion
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r3_benjamin_obligation_comply_or_seek_relief
- Track: hypothesis
- Description: If prior appointment is in force and Benjamin disregarded order, Benjamin was obligated to comply or seek relief.
- Authority refs: none
- Activation estimate: None
- Antecedent intake:
- f_client_prior_appointment: value=True status=alleged source=client_assertion
- Action: Obtain certified guardianship appointment order/docket showing appointment identity and effective date.
- f_client_benjamin_order_disregard: value=True status=alleged source=client_assertion
- Action: Convert allegation to verified with certified records, transcripts, or authenticated communications.

### UNRESOLVED - r5_solomon_obligated_appear_and_answer
- Track: hypothesis
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Authority refs: order:eppdapa_restraining_order
- Activation estimate: 2026-03-10
- Antecedent intake:
- f_restraining_order_no_further_service_needed: value=True status=verified source=sam_barber_restraining_order_ocr.txt
- Action: No immediate action required for this antecedent.
- f_client_solomon_failed_appearance: value=True status=alleged source=client_assertion
- Action: Collect hearing register, appearance minute entry, and proof of service/order-to-appear documentation.

### UNRESOLVED - r7_solomon_forbidden_refile_precluded_issue
- Track: hypothesis
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Authority refs: none
- Activation estimate: 2026-03-31
- Antecedent intake:
- f_collateral_estoppel_candidate: value=True status=theory source=motion_to_dismiss_for_collateral_estoppel.md
- Action: Promote theory to verified only after documentary proof is collected and reviewed for actor/date consistency.
- f_client_solomon_barred_refile: value=True status=alleged source=client_assertion
- Action: Collect the newer filing plus certified prior final judgment/order and issue-identity comparison chart.

### INACTIVE - r17_responding_custodian_obligated_execute_or_query_protocol_upon_service
- Track: workflow
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Authority refs: auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_subpoena_service_completed_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_or_joined_search_protocol_defined: value=False status=verified source=11B_attachment_a2_definitions_and_instructions_final.md
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.

### INACTIVE - r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response
- Track: workflow
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_subpoena_response_incomplete_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Update active service log statuses/dates to reflect executed service or response milestones, then regenerate artifacts.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

### INACTIVE - r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage
- Track: workflow
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Authority refs: auth:orcp_46, auth:orcp_55
- Activation estimate: 2026-04-07
- Antecedent intake:
- f_deficiency_notice_sent_any: value=False status=verified source=28_active_service_log_2026-04-07.csv
- Action: Provide records that make this antecedent true, or revise the dependent rule if the predicate should remain false.
- f_subpoena_workflow_components_staged: value=True status=verified source=final_filing_set
- Action: No immediate action required for this antecedent.

