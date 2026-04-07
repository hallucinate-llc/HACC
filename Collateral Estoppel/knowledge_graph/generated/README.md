# Generated Formal Reasoning Artifacts

These files are generated from:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py`
and may ingest feed data from:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_evidence_graph_feed.json`
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.json`
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/evidence_fact_overrides_2026-04-07.csv` (optional fact-status/value override intake)
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/evidence_fact_override_prefill_memo_2026-04-07.md` (prefill rationale and certification gates)
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/fact_override_promotion_runbook_2026-04-07.md` (how to promote facts to verified on certified intake)

## Recompute command

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/marshal_solomon_repository_evidence.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/collect_solomon_evidence_events.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_conflict_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_service_activation_scenarios.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_closure_workplan.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_rule_closure_trace_matrix.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_certified_intake_tracker.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_certified_intake_override_suggestions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" --row 2 --file-path "/ABSOLUTE/PATH/TO/CERTIFIED/FILE"  # dry-run
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_system_gap_refresh.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/simulate_certified_promotion_scenarios.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_certification_packet_manifests.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_evidence_candidates.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_mapping_prefill.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_clerk_request_letters.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_status_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_next_actions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_followup_calendar.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_contact_completion_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_daily_action_brief.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_followup_send_queue.py" --date 2026-04-10
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_first_packet_command_block.py" --row 2 --file-path "/ABSOLUTE/PATH/TO/PACKET/CHECKLIST.md"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

## Utility apply command

Use this only after certified-intake suggestions are reviewed and confirmed:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_certified_intake_override_suggestions.py" \
  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"
```

Or run the single-pipeline command:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py"
```

Tracker confirmation helper (dry-run by default; add `--write` to persist):

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" \
  --row 2 \
  --file-path "/ABSOLUTE/PATH/TO/CERTIFIED/FILE"
```

## Outputs

- `full_case_knowledge_graph.json`: full entity/fact/rule/conclusion graph
- `case_dependency_graph.json`: explicit fact -> rule -> conclusion dependency graph
- `case_dependency_graph.dot`: Graphviz dependency rendering input
- `case_flogic.flr`: frame-logic program
- `case_temporal_deontic_fol.tfol`: temporal deontic first-order logic model
- `case_deontic_cognitive_event_calculus.pl`: deontic cognitive event-calculus program
- `deontic_reasoning_report.json`: computed rule activation and party deontic state
- `deontic_reasoning_report.md`: quick human-readable summary
- `evidence_fact_overrides_2026-04-07.csv` controls promoted/demoted fact status/value before rule evaluation
- `deontic_litigation_matrix.json`: party-by-party litigation matrix from computed O/P/F
- `deontic_litigation_matrix.md`: human-readable litigation matrix
- `deontic_logic_gap_audit_2026-04-07.md`: prioritized reasoning-system gap audit and closure plan
- `deontic_logic_gap_audit_2026-04-07.json`: machine-readable unresolved-rule snapshot
- `deontic_service_status_rule_activation_map_2026-04-07.md`: CSV status-field mapping that auto-activates subpoena enforcement rules
- `service_log_validation_report_2026-04-07.md`: QA report for service-log status/date integrity and derived activation summary
- `service_log_validation_report_2026-04-07.json`: machine-readable validation findings and per-row derived state
- `proof_intake_map_2026-04-07.md`: antecedent-level checklist for unresolved/inactive rule closure
- `proof_intake_map_2026-04-07.json`: machine-readable proof-intake map for automation
- `deontic_end_to_end_grounding_gap_report_2026-04-07.md`: formal end-to-end grounding gap audit (authority/fact/rule coverage)
- `deontic_end_to_end_grounding_gap_report_2026-04-07.json`: machine-readable grounding-gap diagnostics
- `deontic_conflict_report_2026-04-07.md`: O/P/F conflict check across active rules by mode
- `deontic_conflict_report_2026-04-07.json`: machine-readable deontic conflict diagnostics
- `service_activation_scenarios_2026-04-07.md`: non-destructive what-if activation outcomes for r17/r18/r19 by recipient
- `service_activation_scenarios_2026-04-07.json`: machine-readable scenario projections for service-log rule activation
- `deontic_closure_workplan_2026-04-07.md`: prioritized rule-closure sequence for remaining unresolved/inactive strict-mode rules
- `deontic_closure_workplan_2026-04-07.json`: machine-readable closure plan with per-rule actions and expected effects
- `deontic_readiness_dashboard_2026-04-07.md`: consolidated strict/inclusive readiness scoreboard and blocker summary
- `deontic_readiness_dashboard_2026-04-07.json`: machine-readable readiness dashboard (counts, conflicts, service projections, top closures)
- `rule_closure_trace_matrix_2026-04-07.md`: per-blocker rule->fact->source->action trace matrix for strict unresolved/inactive closure
- `rule_closure_trace_matrix_2026-04-07.json`: machine-readable rule closure trace matrix
- `deontic_next_proof_targets_2026-04-07.md`: compact highest-impact strict-mode fact gaps with sample blocked rules
- `certified_promotion_gap_memo_2026-04-07.md`: current certified-intake blockers preventing allegation/theory -> verified promotion
- `certified_intake_override_suggestions_2026-04-07.json`: machine-readable suggested override rows from certified intake tracker
- `certified_intake_override_suggestions_2026-04-07.md`: human-readable certified intake override suggestions and warnings
- `certified_intake_tracker_validation_2026-04-07.json`: machine-readable validation findings for certified intake tracker rows
- `certified_intake_tracker_validation_2026-04-07.md`: human-readable validation report for certified intake readiness
- `certified_intake_promotion_pipeline_status_2026-04-07.json`: machine-readable status of end-to-end certified intake promotion pipeline run
- `certified_intake_promotion_pipeline_status_2026-04-07.md`: human-readable status summary for end-to-end certified intake promotion pipeline run
- `deontic_system_gap_refresh_2026-04-07.json`: machine-readable refresh of law-grounding and remaining evidence-gated gaps
- `deontic_system_gap_refresh_2026-04-07.md`: human-readable law/evidence gap refresh summary
- `certified_promotion_what_if_scenarios_2026-04-07.json`: machine-readable what-if strict-count/rule-state projections under simulated certified fact promotion
- `certified_promotion_what_if_scenarios_2026-04-07.md`: human-readable what-if projections for prioritized certified promotion tracks
- `certification_sequence_recommendation_2026-04-07.md`: recommended certification order based on scenario yield
- `certification_packet_manifests_2026-04-07.json`: machine-readable packet manifests mapping target facts to required certified records and expected rule unlocks
- `certification_packet_manifests_2026-04-07.md`: human-readable certification packet manifests for unresolved strict blockers
- `deontic_gap_closure_matrix_2026-04-07.json`: machine-readable consolidated strict blocker matrix (rule -> antecedent -> action -> packet -> formal requirement)
- `deontic_gap_closure_matrix_2026-04-07.md`: human-readable consolidated strict blocker matrix with open element audits
- `issue_preclusion_evidence_candidates_2026-04-07.json`: machine-readable candidate evidence map for issue-preclusion element completion (repository index + event feed + direct path/content scan)
- `issue_preclusion_evidence_candidates_2026-04-07.md`: human-readable candidate evidence shortlist grouped by issue-preclusion element
- `issue_preclusion_mapping_prefill_2026-04-07.json`: machine-readable conservative prefill snapshot for issue_preclusion_mapping.json notes (booleans remain false)
- `issue_preclusion_request_status_dashboard_2026-04-07.json`: machine-readable status dashboard for case-specific issue-preclusion certified-record requests
- `issue_preclusion_request_status_dashboard_2026-04-07.md`: human-readable status dashboard for case-specific issue-preclusion certified-record requests
- `issue_preclusion_request_next_actions_2026-04-07.json`: machine-readable urgency-ranked next-action queue from issue-preclusion request tracker
- `issue_preclusion_request_next_actions_2026-04-07.md`: human-readable urgency-ranked next-action queue from issue-preclusion request tracker
- `issue_preclusion_followup_calendar_2026-04-07.json`: machine-readable follow-up calendar for case-specific issue-preclusion certified-record requests
- `issue_preclusion_contact_completion_dashboard_2026-04-07.json`: machine-readable contact-completion status for issue-preclusion request tracker
- `issue_preclusion_contact_completion_dashboard_2026-04-07.md`: human-readable contact-completion status for issue-preclusion request tracker
- `issue_preclusion_daily_action_brief_2026-04-07.md`: human-readable day-of action brief (due today + next 7 days) for issue-preclusion request operations
- `issue_preclusion_followup_send_queue_2026-04-10.json`: machine-readable send queue for a target follow-up date
- `packet_activation_commands_nonappearance_row2_2026-04-07.md`: command sheet for certified nonappearance row confirmation and promotion run
- `packet_activation_commands_issue_preclusion_row3_2026-04-07.md`: command sheet for certified issue-preclusion row confirmation and promotion run
- `packet_activation_commands_prior_appointment_row4_2026-04-07.md`: command sheet for certified prior-appointment row confirmation and promotion run
- `motion_support_map.json`: Source -> Fact -> Rule -> Motion linkage map
- `motion_support_map.md`: human-readable motion support map
- `motion_paragraph_bank.json`: motion-ready paragraph payload grouped by mode and target motion
- `motion_paragraph_bank.md`: human-readable paragraph bank for drafting

## Computation modes

- `strict`: uses only `verified` facts for activation
- `inclusive`: uses `verified` + `alleged` facts for activation
- OCR date extraction: parser ingests dates from
  - `evidence_notes/solomon_motion_for_guardianship_ocr.txt`
  - `evidence_notes/sam_barber_restraining_order_ocr.txt`
  and computes rule `activation_date_estimate` from dated antecedents.

This separation is intentional so legal theory can be explored without treating allegations as adjudicated facts.
