# First Live Branch Update Protocol

Use this note when the workspace receives its first real promotion event, such as:

1. HACC service is actually completed;
2. a deficiency or compel event actually occurs; or
3. certified prior-proceeding materials are actually staged.

## Goal

Move from prepared workflow state to updated graph state without losing proof-state discipline.

## Choose the correct branch first

### HACC Exhibit R service or production event

Start with:

1. [exhibit_r_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/exhibit_r_workflow_subgraph.md)
2. [43_branch_promotion_protocol_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/43_branch_promotion_protocol_2026-04-07.md)
3. [29_active_service_log_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/29_active_service_log_2026-04-07.md)

Edit first:

1. [28_active_service_log_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv)

### Certified-record / issue-preclusion event

Start with:

1. [issue_preclusion_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.md)
2. [README.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/README.md)
3. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)

Edit first:

1. the staged files in `evidence_notes/certified_records`
2. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)

### Fact promotion from certified proof

Start with:

1. [fact_override_promotion_runbook_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/fact_override_promotion_runbook_2026-04-07.md)

Edit first:

1. [evidence_fact_overrides_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/evidence_fact_overrides_2026-04-07.csv)

## Recompute sequence

After the source data is updated, rerun:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

If fact overrides were changed, also rerun:

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Verify in this order

1. [graph_navigation_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_navigation_dashboard.md)
2. [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md)
3. [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md)

Then verify the branch-specific output:

1. [orcp17_readiness_snapshot.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.md), if sanctions state changed
2. [29_active_service_log_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/29_active_service_log_2026-04-07.md), if service state changed
3. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json), if certified-record state changed

## Conservative rule

If a real-world event improves the record only partially, update the source file and rerun the generators, but do not manually overstate the branch status in the graph notes. Let the live outputs reflect the promotion that the updated record actually supports.
