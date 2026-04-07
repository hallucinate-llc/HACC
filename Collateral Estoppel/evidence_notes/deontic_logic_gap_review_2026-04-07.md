# Deontic Logic Gap Review

Date: 2026-04-07

## Scope

This memo reviews the current deontic/formal-logic layer in the `Collateral Estoppel` workspace and identifies where the reasoning system is not yet grounded end-to-end from legal authority to verified facts to filing-safe conclusions.

Reviewed materials:
- `knowledge_graph/generate_formal_reasoning_artifacts.py`
- `knowledge_graph/deontic_theorem_workbook.md`
- `research/deontic_bridge_memo.md`
- `knowledge_graph/generated/deontic_reasoning_report.md`
- `knowledge_graph/generated/motion_support_map.md`

## Findings

### 1. High severity: inclusive mode still activates Benjamin-centered conclusions from alleged predicates.

Current problem:
- The generator still defines alleged client-assertion facts for a prior Benjamin appointment, Benjamin order disregard, and Benjamin housing interference.
- Those alleged predicates directly activate deontic rules in inclusive mode.
- The generated outputs therefore still present Benjamin permissions, obligations, and prohibitions as active even though those predicates remain unverified and partly conflict with the current Solomon-centered and source-record-centered posture.

Key locations:
- `knowledge_graph/generate_formal_reasoning_artifacts.py:193`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:195`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:196`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:582`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:595`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:607`
- `knowledge_graph/generated/deontic_reasoning_report.md:42`
- `knowledge_graph/generated/deontic_reasoning_report.md:44`
- `knowledge_graph/generated/motion_support_map.md:179`
- `knowledge_graph/generated/motion_support_map.md:197`

Why it matters:
- This is the biggest risk of logic drift. The model can still manufacture active Benjamin conclusions from allegations alone, which can contaminate downstream motion maps and paragraph banks.

Recommended fix:
- Split the model into `verified`, `inference`, and `pleading` tracks instead of letting inclusive mode treat alleged predicates as active conclusions.
- Move Benjamin-centered prior-appointment rules into a quarantined theorem or hypothesis layer until the source order exists.

### 2. High severity: the system still lacks a true law-source layer.

Current problem:
- The workbook and bridge memo expressly say the logic is only a modeling aid until tied to governing authority.
- The generator does not yet encode statutes, procedural rules, or signed orders as first-class authority nodes with citation provenance and rule-to-authority mapping.

Key locations:
- `knowledge_graph/deontic_theorem_workbook.md:3`
- `knowledge_graph/deontic_theorem_workbook.md:89`
- `research/deontic_bridge_memo.md:24`
- `research/deontic_bridge_memo.md:65`
- `knowledge_graph/generated/motion_support_map.md:168`

Why it matters:
- Right now the model is mainly fact-to-conclusion, not authority-to-rule-to-fact-to-conclusion.
- That means it can support drafting, but not yet an end-to-end formal grounding of legal propositions.

Recommended fix:
- Add authority facts and authority objects such as:
- `Authority(ors_or_rule_id)`
- `OrderAuthority(order_id, signed_date, expiration_date)`
- `Requires(authority, predicate_set, legal_effect)`
- `SupportsRule(authority, rule_id)`
- Then require every filing-facing rule to cite at least one authority source.

### 3. High severity: the HACC January 12 internal-review / court-document fact is present in the graph layer but not properly elevated in the formal rule layer.

Current problem:
- The live evidence set now includes direct HACC language that Benjamin was no longer listed effective January 1, 2026 and that the change followed internal review and court documentation currently on file.
- The formal generator still relies on a broader lease-adjustment fact sourced to `HACC vawa violation.pdf`.
- The formal rules do not yet separately encode the stronger January 12 authority-chain fact.

Key locations:
- `knowledge_graph/generate_formal_reasoning_artifacts.py:315`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:708`
- `knowledge_graph/generated/motion_support_map.md:49`
- `knowledge_graph/guardianship_case_graph.md:50`

Why it matters:
- The graph and the formal logic are now out of sync.
- The missing `internal review` and `court documentation on file` predicate is exactly the bridge needed for subpoena logic and source-authority reasoning.

Recommended fix:
- Add verified facts for:
- `HaccInternalReviewClaimed`
- `HaccCourtDocumentationBasisClaimed`
- `HaccRemovedBenjaminEffective2026_01_01`
- Build a separate rule that HACC must identify the actor, document, and authority chain behind the lease change when it expressly claims a court-document basis.

### 4. High severity: the current temporal model is too weak for order-effectiveness and contempt analysis.

Current problem:
- Rule activation currently uses the maximum known date among antecedents.
- There is no interval logic for order lifespan, no explicit `before/after` relation, no expiration handling, and no distinction between event date, knowledge date, and operative date.

Key locations:
- `knowledge_graph/generate_formal_reasoning_artifacts.py:945`
- `knowledge_graph/generated/deontic_reasoning_report.md:13`

Why it matters:
- This case depends heavily on whether conduct occurred after grant, after notice, within the one-year order window, or after March 10 position statements.
- A simple `max(date)` estimate is not enough for temporal deontic first-order logic or event-calculus-style reasoning.

Recommended fix:
- Replace single activation dates with interval-aware predicates:
- `EffectiveFrom(order, t1)`
- `EffectiveUntil(order, t2)`
- `Occurs(event, t)`
- `After(t_event, t_notice)`
- `WithinInterval(t_event, t1, t2)`
- Distinguish `noticed_on`, `entered_on`, `effective_on`, and `acted_on`.

### 5. Medium-high severity: proof-state handling is ad hoc instead of systematic.

Current problem:
- The system has a useful rule saying Solomon-HACC interference should presently be treated as inference, not direct proof.
- But that caution exists as a single bespoke rule rather than as a general proof-state ontology.

Key locations:
- `knowledge_graph/generate_formal_reasoning_artifacts.py:720`
- `knowledge_graph/generated/motion_support_map.md:57`

Why it matters:
- The workspace now repeatedly uses categories like verified, alleged, theory, not found locally, and subpoena target.
- The formal layer should be able to reason over those states directly instead of hard-coding one exception.

Recommended fix:
- Add proof-state predicates such as:
- `DirectProofAvailable(claim)`
- `OnlyInferenceAvailable(claim)`
- `LocalSearchNegative(claim)`
- `ThirdPartyCustodianLikely(claim, custodian)`
- `CompelledProductionRequired(claim, custodian)`
- Then make downstream filing conclusions depend on proof state.

### 6. Medium severity: HACC duty rules still depend on alleged appointment assumptions.

Current problem:
- The rule making HACC obligated to process housing consistent with valid authority depends on `f_hacc_process_exists` and `f_client_prior_appointment`.
- Both are still alleged or client-assertion based.

Key locations:
- `knowledge_graph/generate_formal_reasoning_artifacts.py:377`
- `knowledge_graph/generate_formal_reasoning_artifacts.py:696`
- `knowledge_graph/generated/deontic_reasoning_report.md:50`

Why it matters:
- This mixes two different propositions:
- HACC had a process affecting Jane's household.
- HACC had a verified legal duty to honor a specific appointment order.
- Only the first is currently well supported.

Recommended fix:
- Split HACC rules into:
- verified process duties triggered by HACC’s own lease-change and internal-review statements
- conditional authority-honor duties triggered only by a verified order or appointment record

### 7. Medium severity: sanctions and contempt remain conceptual, not fully authority-grounded.

Current problem:
- The bridge memo and theorem workbook use `PotentialSanctions` and related concepts, but the formal layer does not yet map specific sanctions or contempt predicates to identified governing authority and required elements.

Key locations:
- `knowledge_graph/deontic_theorem_workbook.md:55`
- `research/deontic_bridge_memo.md:63`

Why it matters:
- The model can say a sanctions path is plausible, but it cannot yet prove which element set is satisfied, which remain open, and which authority governs.

Recommended fix:
- Create separate authority-grounded element sets for:
- contempt / show-cause
- sanctions for abusive practice
- subpoena noncompliance
- Tie each element set to verified facts, disputed facts, and missing proof.

## Structural gaps in the current reasoning architecture

The present system is strongest at:
- storing facts
- generating deontic hypotheses
- surfacing conflicts and missing proof

It is weaker at:
- authority provenance
- temporal interval reasoning
- proof-state semantics
- separating hypothesis logic from filing-safe logic

## Recommended next build sequence

1. Create an authority layer.
- Add law and order sources as first-class nodes with citations, dates, and scope.

2. Create a proof-state layer.
- Encode verified, inferred, contradicted, unresolved, negative-search, and subpoena-required states formally.

3. Refactor Benjamin-centered rules into a hypothesis partition.
- Keep them available for exploration, but stop activating them in filing-facing outputs.

4. Synchronize the HACC formal facts with the January 12 internal-review record.
- Promote the direct HACC statement into formal predicates and update the lease-authority rules.

5. Upgrade temporal semantics.
- Move from single activation-date heuristics to interval and event ordering predicates.

6. Rebuild filing outputs from only authority-grounded and proof-gated conclusions.
- The motion-support map should default to rules that are both authority-backed and fact-backed.

## Bottom line

The current deontic layer is useful and already catches some of the right issues, especially actor-assignment conflicts, authority-citation gaps, and proof cautions. But it is not yet an end-to-end formal legal reasoning system. The main breaks are:
- alleged predicates still activating conclusions,
- no real law-source layer,
- incomplete temporal semantics,
- incomplete proof-state modeling,
- and drift between the updated HACC evidence record and the formal generator.
