# Branch Promotion Protocol - 2026-04-07

Use this note when new service events or certified records arrive and the packet needs to be updated quickly without losing proof-state discipline.

## 1. If HACC Exhibit R is served

Update first:

1. [28_active_service_log_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv)
2. [29_active_service_log_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/29_active_service_log_2026-04-07.md)
3. regenerate the formal artifacts

Expected promotion:

1. `service_stage_complete` in the Exhibit R audit should move from `missing` to `verified`
2. `pre_service_only` should stop being the controlling workflow description

## 2. If a deficiency notice or compel stage occurs

Update first:

1. [28_active_service_log_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv)
2. [32_deadline_update_log_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/32_deadline_update_log_2026-04-07.md)
3. [24_motion_to_compel_subpoena_compliance_and_sanctions_final.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/24_motion_to_compel_subpoena_compliance_and_sanctions_final.md), if filing is needed

Expected promotion:

1. `deficiency_or_compel_stage` in the Exhibit R audit should move from `missing` to `verified`

## 3. If certified prior-proceeding materials arrive

Stage first in:

1. [README.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/README.md)

Then update:

1. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)
2. [42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md)

Expected promotion:

1. `prior_separate_proceeding_record` should move from `missing` once prior-order and docket/register materials are staged
2. the individual issue-preclusion mapping rows should move from `proof_gated` to `verified` as the mapping manifest is completed

## 4. If a specific ORCP 17 target filing is chosen

Update first:

1. [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)
2. [47_orcp17_target_selection_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/47_orcp17_target_selection_worksheet_2026-04-07.md)
3. [motion_for_sanctions_re_frivolous_and_abusive_practice.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/motion_for_sanctions_re_frivolous_and_abusive_practice.md), if argument language needs to become more specific

Expected promotion:

1. `challenged_filing_identified`
2. `improper_purpose_mapped`
3. `unsupported_legal_position_mapped`
4. `unsupported_factual_assertion_mapped`

Conservative current next worksheet:

4. [48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md)
5. [49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md)
6. [50_orcp17_improper_purpose_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/50_orcp17_improper_purpose_worksheet_2026-04-07.md)
7. [51_orcp17_mapping_priority_protocol_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/51_orcp17_mapping_priority_protocol_2026-04-07.md)

## 5. After any promotion event

Regenerate:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

Then check:

1. [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md)
2. [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md)

Those generated files are the fastest way to confirm whether the branch actually promoted.
