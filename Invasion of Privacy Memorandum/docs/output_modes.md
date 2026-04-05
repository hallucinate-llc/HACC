# Output Modes

## Purpose
The updated shared chat now implies that this workspace should support more than one kind of output.

The system already produces:
- `result`
- `package`
- `memorandum`

The next layer is advocacy-oriented output built from the same evaluated case.

## Current Modes
### `result`
- canonical structured evaluation output
- includes findings, provenance, explanations, and timeline
- now includes a top-level branch label such as `constructive_denial`, `evidentiary_gap`, `undue_burden_constructive_denial`, or `effective_accommodation`
- target user: developer, analyst, downstream systems

### `package`
- exported machine-readable artifact bundle
- includes rule, graph, decision-tree, test, advocacy, memorandum, and manifest files
- now includes a compact `brief_index.json` entry point that points to the summary, memorandum, graph, and grounding artifacts
- target user: tooling, experimentation, formalization workflows

### `memorandum`
- formal analysis output with sectioned legal reasoning
- emits Markdown, JSON, PDF, and citation-grounding JSON-LD
- maps dependency-graph targets to authority excerpts and propositions
- target user: legal analysis, internal review, polished output generation

## New Advocacy Modes
### `hearing_script`
- short speaking outline for grievance or hearing use
- should frame the dispute as an effectiveness problem, not only a policy dispute
- should emphasize constructive denial when supported

### `complaint_outline`
- structured claim summary
- should identify the core legal theory, key facts, harms, and authorities
- should stay scaffold-like rather than pretending to be a filed pleading

### `demand_letter`
- short pressure-oriented written request
- should emphasize effectiveness, urgency, and requested remedy
- should remain easy to edit for a real sender

### `negotiation_summary`
- concise leverage and risk summary
- should identify strongest current theory, evidentiary gaps, and likely pressure points

## Current Implementation Choice
This workspace now includes a lightweight advocacy generator:
- [generate_advocacy.py](../engine/generate_advocacy.py)

This generator is intentionally conservative:
- it derives text from the evaluated case output
- it does not claim to be verified legal advice
- it uses the same accepted findings and authorities already present in the case model
- it includes explicit placeholder metadata for names, recipients, remedies, and deadlines
- it now varies the placeholder remedy text by branch so successful-accommodation cases ask to preserve the working arrangement rather than approve a denied one
- it now emits a structured advocacy bundle with section-level citations to findings, authorities, evidence, events, and proof steps
- it writes both plain-text and Markdown draft files for easier review

## Follow-On Upgrades
- add authority snippets or rule IDs inside each advocacy mode
- add templates for jurisdiction-specific variants
- add editable placeholders for names, dates, and requested remedies
- add snapshot coverage for generated advocacy files
- add explicit distinction between neutral analysis mode and persuasive drafting mode
