# Graph System Index

This index is the top-level map for the knowledge-graph and deontic-reasoning workspace in `Collateral Estoppel`.

Quick navigation dashboard:

- [graph_navigation_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_navigation_dashboard.md)
- [graph_navigation_dashboard.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_navigation_dashboard.json)

## Core case graph

- [guardianship_case_graph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/guardianship_case_graph.json)
- [guardianship_case_graph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/guardianship_case_graph.md)

Use this as the main case graph for parties, events, proof targets, findings, and broad issues.

## Modular workflow subgraphs

### ORCP 17 sanctions workflow

- [orcp17_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/orcp17_workflow_subgraph.json)
- [orcp17_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/orcp17_workflow_subgraph.md)

Use this branch for:
- challenged-filing identification
- predicate-level sanctions gating
- intake-gated promotion workflow

### Exhibit R subpoena workflow

- [exhibit_r_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/exhibit_r_workflow_subgraph.json)
- [exhibit_r_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/exhibit_r_workflow_subgraph.md)

Use this branch for:
- HACC nonparty production path
- service-state tracking
- deficiency and compel escalation path

### Issue-preclusion certified-records workflow

- [issue_preclusion_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.json)
- [issue_preclusion_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.md)

Use this branch for:
- certified-record staging
- record-presence gates
- element-by-element mapping progression

## Deontic architecture notes

- [authority_and_proof_state_schema.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/authority_and_proof_state_schema.md)
- [deontic_theorem_workbook.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/deontic_theorem_workbook.md)

Use these files to understand:
- the authority / fact / proof-state / filing-safe stack
- the theorem candidates behind the guardianship track

## Engine and generators

- [generate_formal_reasoning_artifacts.py](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py)
- [generate_motion_support_map.py](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generate_motion_support_map.py)
- [generate_motion_paragraph_bank.py](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generate_motion_paragraph_bank.py)

These are the main generators that turn the graph and workflow inputs into live reasoning artifacts.

## Generated live outputs

- [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md)
- [orcp17_readiness_snapshot.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.md)
- [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md)
- [motion_support_map.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/motion_support_map.md)
- [motion_paragraph_bank.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/motion_paragraph_bank.md)
- [first_live_branch_update_protocol.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/first_live_branch_update_protocol.md)
- [promotion_trigger_matrix.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/promotion_trigger_matrix.md)
- [graph_system_closure_roadmap_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_system_closure_roadmap_2026-04-07.md)

Use these as the live output layer for:
- branch status
- sanction/readiness state
- audit and deontic reasoning
- draft support and reusable language

## Practical reading order

1. [guardianship_case_graph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/guardianship_case_graph.md)
2. [graph_system_index.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_system_index.md)
3. the relevant workflow subgraph for the branch you are updating
4. [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md)
5. [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md)

## Current best read

The graph system now has four layers:

1. a main case graph
2. modular workflow subgraphs
3. generator-backed deontic logic
4. generated live-status outputs

That means the workspace can now represent both substantive case facts and procedural promotion systems without collapsing them into one oversized graph file.
