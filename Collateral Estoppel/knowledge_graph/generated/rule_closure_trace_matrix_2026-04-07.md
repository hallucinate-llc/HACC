# Rule Closure Trace Matrix - 2026-04-07

Strict counts: active=42 unresolved=6 inactive=4

## [unresolved] r1_guardian_permission_if_prior_appointment (hypothesis)
- Authority refs: auth:ors_125_050
- Description: If prior appointment exists, Benjamin is permitted to act within valid guardian scope for Jane.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_authority_ors_125_050_protective_orcp_oec :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_client_prior_appointment :: PriorAppointmentExists :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Certified guardianship appointment order and docket extract.

## [unresolved] r2_target_noninterference_prohibition_if_prior_appointment (hypothesis)
- Authority refs: auth:ors_125_050
- Description: If prior appointment exists and interference is alleged, the alleged interfering actor is forbidden from interference.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_authority_ors_125_050_protective_orcp_oec :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_client_prior_appointment :: PriorAppointmentExists :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Certified guardianship appointment order and docket extract.
- f_client_solomon_housing_interference :: Interference :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/motion_exhibit_index.md
- Action: Authenticated communications, certified court records, and timeline corroboration.

## [unresolved] r3_target_obligation_comply_or_seek_relief_if_prior_appointment (hypothesis)
- Authority refs: auth:ors_125_050
- Description: If prior appointment is in force and an alleged actor disregarded the order, that actor was obligated to comply or seek relief.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_authority_ors_125_050_protective_orcp_oec :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_client_prior_appointment :: PriorAppointmentExists :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Certified guardianship appointment order and docket extract.
- f_client_solomon_order_disregard :: DisregardedOrder :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/knowledge_graph/guardianship_case_graph.md
- Action: Authenticated communications, certified court records, and timeline corroboration.

## [unresolved] r5_solomon_obligated_appear_and_answer (hypothesis)
- Authority refs: order:eppdapa_restraining_order
- Description: If no further service was required because Solomon appeared, later failure to appear supports an obligation to appear and answer.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_restraining_order_no_further_service_needed :: NoFurtherServiceNeeded :: status=verified value=true source=sam_barber_restraining_order_ocr.txt
- Action: Validate and supplement source evidence (sam_barber_restraining_order_ocr.txt) as needed.
- f_client_solomon_failed_appearance :: FailedToAppear :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md
- Action: Certified hearing register/minute entry + proof of service/order-to-appear record.

## [unresolved] r7_solomon_forbidden_refile_precluded_issue (hypothesis)
- Authority refs: auth:oregon_issue_preclusion_cases, auth:oregon_issue_preclusion_prior_separate_proceeding_cases
- Description: If issue preclusion applies, Solomon is forbidden from relitigating the precluded issue.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_authority_issue_preclusion_elements_official_oregon_cases :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_authority_issue_preclusion_requires_prior_separate_proceeding :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_collateral_estoppel_candidate :: PotentialIssuePreclusion :: status=theory value=true source=/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md
- Action: Certified prior final order/judgment + identity-of-issue chart + later filing copy.
- f_client_solomon_barred_refile :: RefiledBarredIssue :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md
- Action: Certified prior final order/judgment + identity-of-issue chart + later filing copy.

## [unresolved] r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved (filing)
- Authority refs: auth:ors_33_075
- Description: If compel-appearance authority is available and the claimed nonappearance predicate is later proved, the case posture may seek compelled appearance.
- Activation estimate: 2026-04-07
- Antecedent trace:
- f_authority_ors_33_075_compel_appearance :: AuthorityAvailable :: status=verified value=true source=oregon_authority_grounding_memo_2026-04-07.md
- Action: Validate and supplement source evidence (oregon_authority_grounding_memo_2026-04-07.md) as needed.
- f_client_solomon_failed_appearance :: FailedToAppear :: status=alleged value=true source=/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md
- Action: Certified hearing register/minute entry + proof of service/order-to-appear record.

## [inactive] r17_responding_custodian_obligated_execute_or_query_protocol_upon_service (workflow)
- Authority refs: auth:orcp_55
- Description: If any subpoena service is completed and OR-joined protocol is defined, responding custodians are obligated in this model to execute the protocol and produce a search execution report.
- Activation estimate: 2026-04-09
- Antecedent trace:
- f_subpoena_service_completed_any :: SubpoenaServiceCompletedAny :: status=verified value=false source=28_active_service_log_2026-04-07.csv
- Action: Confirmed service return entry in active service log (date/method/person served).
- f_or_joined_search_protocol_defined :: OrJoinedSearchProtocolDefined :: status=verified value=true source=11B_attachment_a2_definitions_and_instructions_final.md
- Action: Validate and supplement source evidence (11B_attachment_a2_definitions_and_instructions_final.md) as needed.

## [inactive] r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response (workflow)
- Authority refs: auth:orcp_46, auth:orcp_55
- Description: If an incomplete subpoena response is present and workflow components are staged, Benjamin is permitted in this model to issue a deficiency notice and cure deadline.
- Activation estimate: 2026-04-09
- Antecedent trace:
- f_subpoena_response_incomplete_any :: SubpoenaResponseIncompleteAny :: status=verified value=false source=28_active_service_log_2026-04-07.csv
- Action: Overdue production record, or production-received record with missing required artifacts, or deficiency stage entry.
- f_subpoena_workflow_components_staged :: SubpoenaWorkflowComponentsStaged :: status=verified value=true source=final_filing_set
- Action: Validate and supplement source evidence (final_filing_set) as needed.

## [inactive] r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage (workflow)
- Authority refs: auth:orcp_46, auth:orcp_55
- Description: If deficiency notices are in play and compel templates are staged, Benjamin is permitted in this model to move to compel and seek sanctions for noncompliance.
- Activation estimate: 2026-04-09
- Antecedent trace:
- f_deficiency_notice_sent_any :: DeficiencyNoticeSentAny :: status=verified value=false source=28_active_service_log_2026-04-07.csv
- Action: Deficiency notice date/status entry in active service log.
- f_subpoena_workflow_components_staged :: SubpoenaWorkflowComponentsStaged :: status=verified value=true source=final_filing_set
- Action: Validate and supplement source evidence (final_filing_set) as needed.

## [inactive] r22_case_obligated_finalize_authority_citations_before_filing (filing)
- Authority refs: auth:orcp_17_c
- Description: If authority table placeholders remain unresolved, the case posture is obligated to finalize governing citations before final filing use.
- Activation estimate: 2026-04-09
- Antecedent trace:
- f_authority_table_placeholders_unresolved :: AuthorityCitationsUnresolved :: status=verified value=false source=06_oregon_authority_table_final.md
- Action: No additional evidence needed if false by design; keep source table finalized.
