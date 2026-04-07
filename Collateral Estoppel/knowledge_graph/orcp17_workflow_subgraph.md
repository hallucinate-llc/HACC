# ORCP 17 Workflow Subgraph

This subgraph isolates the sanctions-branch workflow so it can be reasoned about as a graph, not just as scattered notes.

## Core branch

- `issue:orcp17_sanctions_merits`
- tracked by `doc:orcp17_manifest`
- monitored by `doc:orcp17_readiness_snapshot`
- controlled by `doc:orcp17_branch_promotion_checklist`

## Predicate states

- `pred:challenged_filing_identified`
  Current status: `verified`
- `pred:unsupported_factual_assertion_mapped`
  Current status: `proof_gated`
- `pred:unsupported_legal_position_mapped`
  Current status: `proof_gated`
- `pred:improper_purpose_mapped`
  Current status: `proof_gated`

## Promotion gates

### Branch 1

- predicate: `pred:unsupported_factual_assertion_mapped`
- gate: `doc:orcp17_factual_assertion_gate`
- required package: `proof:prior_order_contradiction_package`

### Branch 2

- predicate: `pred:unsupported_legal_position_mapped`
- gate: `doc:orcp17_legal_position_gate`
- required package: `proof:issue_preclusion_bridge_package`
- linked manifest: `doc:issue_preclusion_manifest`

### Branch 3

- predicate: `pred:improper_purpose_mapped`
- gate: `doc:orcp17_improper_purpose_gate`
- required package: `proof:filing_specific_motive_package`

## Workflow control documents

- [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)
- [orcp17_filing_mapping_guide.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping_guide.md)
- [orcp17_manifest_completion_protocol_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_manifest_completion_protocol_2026-04-07.md)
- [orcp17_branch_promotion_checklist_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_branch_promotion_checklist_2026-04-07.md)
- [orcp17_readiness_snapshot.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.md)

## Current best read

The sanctions branch is now graph-structured in a way that matches the live logic:

1. the challenged filing is identified;
2. the three substantive predicates remain proof-gated;
3. each predicate has its own intake gate and required proof package;
4. the generated readiness snapshot remains the fastest way to see which gate is next.
