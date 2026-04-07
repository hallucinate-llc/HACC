# Graph System Closure Roadmap - 2026-04-07

Use this roadmap to distinguish:

1. what the graph/deontic workspace is already ready to do;
2. what should wait for a real-world event; and
3. what structural upgrades are still optional rather than urgent.

## Current operating state

The system is already structured enough to support:

1. core case-fact review through the main graph;
2. sanctions-branch tracking through the `ORCP 17` workflow subgraph;
3. HACC production tracking through the `Exhibit R` workflow subgraph;
4. certified-record and element-mapping tracking through the issue-preclusion workflow subgraph;
5. live audit and branch-state confirmation through the generated dashboards and reports.

## Highest-value real event triggers

These are the events that will now create the biggest actual gain:

### 1. HACC service logged

Expected effect:

1. Exhibit R workflow moves beyond pre-service state
2. service-stage audit should improve
3. compel path becomes more concrete if production does not follow

Start with:

1. [first_live_branch_update_protocol.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/first_live_branch_update_protocol.md)
2. [promotion_trigger_matrix.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/promotion_trigger_matrix.md)

### 2. Certified prior-order and docket materials staged

Expected effect:

1. issue-preclusion record-presence gates improve
2. unsupported-factual-assertion branch may become promotable
3. dismissal / sanctions theories may become materially stronger

Start with:

1. [issue_preclusion_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.md)
2. [orcp17_prior_order_contradiction_intake_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_prior_order_contradiction_intake_note_2026-04-07.md)

### 3. Completed issue-preclusion mapping

Expected effect:

1. issue-preclusion element rows may promote
2. unsupported-legal-position branch may become promotable
3. collateral-estoppel dismissal theory may become less hypothetical

Start with:

1. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)
2. [orcp17_issue_preclusion_bridge_intake_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_issue_preclusion_bridge_intake_note_2026-04-07.md)

## Optional structural upgrades

These are still useful, but they are no longer more important than real evidence or service events:

1. generate a graph navigation dashboard automatically from [graph_system_index.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_system_index.json)
2. merge workflow-subgraph status summaries into one generated registry report
3. create a machine-readable branch-status export combining:
   - [formal_case_state_dashboard.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.json)
   - [orcp17_readiness_snapshot.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.json)
   - workflow-state summaries from service and certified-record branches
4. add a generated “next best evidence” dashboard if future volume makes manual navigation too slow

## Stop rule

Do not add more structural graph scaffolding unless at least one of these is true:

1. a real branch update exposes a missing control point;
2. the current dashboards become hard to use in practice;
3. a new litigation branch appears that is not covered by the current modular workflow pattern.

## Best current working rule

If no real branch update has occurred yet, use the graph system as-is and wait for one of the live trigger events. The current system is mature enough to absorb the next real update without more redesign.
