# Generated Formal Reasoning Artifacts

These files are generated from:
- `/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py`
and may ingest feed data from:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_evidence_graph_feed.json`
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/solomon_repository_evidence_index.json`

## Recompute command

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/marshal_solomon_repository_evidence.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/collect_solomon_evidence_events.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
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
- `deontic_litigation_matrix.json`: party-by-party litigation matrix from computed O/P/F
- `deontic_litigation_matrix.md`: human-readable litigation matrix
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
