# Design Decisions

## 1. Privacy Harm Policy
The updated shared chat contains a modeling tension:
- some examples imply that living-room sleeping alone creates privacy loss and therefore necessity
- one example expected `necessary = false` even when the aide still slept in the living room

For this workspace, this is now an explicit policy setting rather than a hidden assumption.

Supported modes:
- `inferred_from_living_room_sleeping`
- `explicit_only`

### `inferred_from_living_room_sleeping`
- living-room sleeping is treated as an independent privacy harm
- privacy harm is sufficient to support `necessary`

### `explicit_only`
- privacy harm must be explicitly present in facts/findings
- living-room sleeping alone does not imply privacy loss

Current default:
- `inferred_from_living_room_sleeping`

Reason:
- it aligns better with the broader legal theory in the extracted chat that common-area sleeping itself undermines dignity, autonomy, and livability

Use case for `explicit_only`:
- preserving the original chat's `nominal_approval_no_harm_shown` expectation

## 2. Accepted Findings Override Asserted Facts
The evaluator uses `acceptedFindings` when present and records conflicts against `assertedFacts`.

Reason:
- the updated chat strongly emphasized separating allegation from accepted finding

## 3. Evidence And Timeline Layer
The case fixture now supports:
- `evidence[]`
- `events[]`

Reason:
- the updated chat explicitly called for separating evidence from findings and for supporting event sequencing / event calculus

## 4. Artifact Surface
The updated chat described a downloadable artifact package with these outputs:
- Prolog rules
- JSON-LD context
- JSON-LD case instance
- decision tree JSON
- dependency graph JSON
- tests JSON
- README

This workspace now treats that package shape as an implementation target.

## 5. Provenance Shape
The evaluator now preserves provenance in two layers:
- bucketed support maps such as `authoritySupport`, `evidenceSupport`, and `eventSupport`
- a per-finding `provenance` object that combines fact inputs, evidence IDs, event IDs, authority IDs, and matching proof steps

Reason:
- downstream consumers usually need one place to answer "why did this conclusion fire?"
- keeping the older bucketed maps alongside the unified object avoids breaking simpler consumers while making richer explanations easier to build
