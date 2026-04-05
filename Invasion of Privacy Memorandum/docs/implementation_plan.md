# Implementation Plan

## Goal
Build a traceable legal reasoning MVP for the live-in-aide accommodation fact pattern extracted from the shared chat.

## Product framing
The system should accept a structured fact pattern, derive intermediate conclusions, and produce:
- human-readable analysis
- machine-readable output
- advocacy-oriented drafting scaffolds derived from the same reasoning state

## Current baseline
The repo now supports:
1. structured case input
2. asserted-vs-accepted fact separation
3. evidence objects linked to findings
4. timeline/event objects
5. configurable privacy policy
6. rule evaluation for the main accommodation theory
7. proof trace generation
8. authority attachment in output
9. result artifact writing
10. package-style export artifacts aligned to the updated chat
11. per-finding provenance objects that unify facts, evidence, events, authorities, and proof steps
12. snapshot refresh tooling for canonical result output
13. schema validation in the dependency-free checks
14. package snapshot regression coverage for exported artifacts
15. advocacy-oriented draft generation for hearing, complaint, demand-letter, and negotiation modes
16. canonical branch labels shared across result, advocacy, and package exports
17. memorandum generation with PDF output and dependency-to-authority grounding

## Export targets taken from the updated chat
`workspace2` now treats these as first-class artifact targets:
- `legal_reasoning.pl`
- `context.json`
- `case_instance.jsonld`
- `memorandum.json`
- `memorandum.md`
- `memorandum_of_law.pdf`
- advocacy drafts and `advocacy_bundle.json`
- `dependency_graph.json`
- `decision_tree.json`
- `brief_index.json`
- `tests.json`
- `README.md`

## MVP deliverables
1. Input schema for a single accommodation case
2. Rule set for the first reasoning path
3. Evaluator that computes derived findings
4. Proof trace generation
5. Regression tests for positive and negative scenarios
6. Output artifact generation for evaluated cases
7. Package export matching the updated chat
8. Evidence and timeline support
9. Configurable privacy/necessity interpretation

## MVP rule path
The first implemented reasoning path is:
- sleep interruption
- work interference
- caregiving impairment
- privacy loss
- necessity
- reasonableness
- duty to grant
- not effective
- constructive denial
- violation

## Architecture
- `schema/`: JSON schemas and shape notes
- `fixtures/`: example inputs
- `rules/`: human-readable rule definitions
- `engine/`: evaluator and exporters
- `tests/`: regression tests
- `outputs/`: generated evaluation artifacts
- `docs/`: planning and design notes

## Output modes
Documented in [output_modes.md](/home/barberb/HACC/workspace2/docs/output_modes.md):
- `result`
- `package`
- `memorandum`
- `hearing_script`
- `complaint_outline`
- `demand_letter`
- `negotiation_summary`

## Branch model
The current implementation now emits a canonical branch label for each evaluated case:
- `constructive_denial`
- `evidentiary_gap`
- `undue_burden_constructive_denial`
- `effective_accommodation`

That branch is now carried through:
- evaluator result JSON
- advocacy bundle metadata
- package export metadata such as `manifest.json`, `decision_tree.json`, `dependency_graph.json`, `summary.json`, and `tests.json`
- memorandum outputs such as `memorandum.json`, `memorandum.md`, `memorandum_of_law.pdf`, and `dependency_citations.jsonld`

## Current modeling choices
- facts are split into `assertedFacts` and optional `acceptedFindings`
- accepted findings override asserted facts during evaluation
- authorities are attached to the case fixture and grouped into support buckets in output
- evidence objects are attached to supported findings
- timeline events are preserved in evaluation output
- the CLI can print JSON or write a result file under `outputs/`
- package exports mirror the file-level artifact design described in the updated chat
- package exports now bundle the memorandum JSON, Markdown, and PDF artifacts alongside the reasoning/export files
- package exports now include a compact `brief_index.json` entry point for downstream discovery
- privacy harm policy is configurable per case
- advocacy outputs are generated from the same evaluated case state rather than from a separate hand-authored layer

## Important design decisions
Documented in [design_decisions.md](/home/barberb/HACC/workspace2/docs/design_decisions.md):
- privacy/necessity interpretation is a policy setting
- accepted findings override asserted facts
- evidence and event layers are modeled explicitly

## Milestones
### Milestone 1
- represent one case
- evaluate one rule set
- produce one traceable output
- export one package matching the chat artifact surface

### Milestone 2
- add explicit provenance from findings to evidence IDs
- add authority weighting and more explicit rule-authority mapping
- add result snapshot comparison tests

### Milestone 3
- add event-calculus export
- add multiple legal theories and jurisdictions
- add explanation text generation beyond proof traces
- add configurable policy bundles beyond privacy mode

### Milestone 4
- add richer advocacy outputs with authority snippets and placeholders
- add jurisdiction-aware templates
- add snapshot coverage for advocacy artifacts
- add explicit neutral-analysis versus persuasive-drafting modes

## Data model priorities
Keep these separate:
- asserted facts
- accepted findings
- evidence
- events
- derived conclusions
- defenses
- authorities
- provenance

## Immediate next engineering tasks
1. Add schema validation for generated outputs, not just inputs
2. Expand unified provenance to include explicit finding-to-authority text snippets or rule IDs
3. Add snapshot coverage for advocacy artifacts
4. Add multiple fixtures covering alternative legal theories and jurisdictions
5. Add configurable policy bundles for additional reasoning choices
