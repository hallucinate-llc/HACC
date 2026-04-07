# Issue Preclusion Workflow Subgraph

This subgraph isolates the certified-records and element-mapping workflow for the issue-preclusion branch.

## Core branch

- `issue:issue_preclusion_merits`
- staged by `doc:certified_records_staging_readme`
- mapped by `doc:issue_preclusion_manifest`
- audited in `doc:deontic_reasoning_report`
- status reported in `doc:formal_case_state_dashboard`

## Record-presence gates

- `proof:prior_order_material_present`
- `proof:docket_register_material_present`
- `proof:hearing_appearance_material_present`

These capture the first promotion layer: record presence.

## Mapping predicates

- `pred:prior_separate_proceeding_record`
- `pred:identical_issue_mapped`
- `pred:finality_mapped`
- `pred:party_privity_mapped`
- `pred:full_fair_opportunity_mapped`
- `pred:identical_issue_and_finality_mapping`

These capture the second promotion layer: mapped doctrine elements.

## Control documents

- [README.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/README.md)
- [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)
- [issue_preclusion_mapping_guide.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md)
- [issue_preclusion_mapping_layer_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/issue_preclusion_mapping_layer_note_2026-04-07.md)

## Current best read

The issue-preclusion branch is now graph-structured in two distinct stages:

1. certified materials become present;
2. mapped elements move from proof-gated to verified.

That matches the safe logic posture already reflected in the generated dashboard and reasoning report: doctrine grounded, but application still proof-gated until records are staged and mapped.
