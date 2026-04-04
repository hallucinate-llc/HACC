# Legal Reasoning Package

This package contains a prototype formalization of the live-in aide accommodation dispute in:
- Prolog/Datalog-style rules
- Event-calculus export
- JSON-LD context and case instance
- Advocacy drafts and structured bundle
- Memorandum bundle with PDF output
- Dependency graph
- Decision tree
- Regression test fixtures
- Bundle manifest

Case Metadata:
- Case ID: `live_in_aide_case_001`
- Branch: `constructive_denial`
- Active Outcome: `violation`
- Authority Trust: `fully_verified`
- Source Verified Count: `5`
- Source Normalized Count: `5`
- Source Status: All authority entries are sourceVerified and sourceNormalized.
- Direct Fit Count: `3`
- Analogical Fit Count: `2`
- Record-Support Fit Count: `0`
- Fit Status: This package includes analogical authority mappings.
- Fit Finding: `analogical_support`
- Fit Finding Note: This package includes analogical mappings, so the legal fit should be described as mixed direct and analogical support.
- Recommended First Stop: `memorandum_of_law.pdf`
- Why Open This: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review.

Files:
- legal_reasoning.pl
- event_calculus.pl
- context.json
- case_instance.jsonld
- hearing_script.txt
- hearing_script.md
- complaint_outline.txt
- complaint_outline.md
- demand_letter.txt
- demand_letter.md
- negotiation_summary.txt
- negotiation_summary.md
- advocacy_bundle.json
- memorandum.json
- memorandum.md
- memorandum_of_law.pdf
- dependency_graph.json
- dependency_citations.jsonld
- authority_review.json
- authority_review.md
- authority_research_note.json
- authority_research_note.md
- authority_summary.json
- decision_tree.json
- summary.json
- brief_index.json
- tests.json
- manifest.json

Notes:
- This is a modeling package, not verified legal advice.
- It encodes asserted facts and legal theories into computational structures.
- Separate asserted facts, accepted findings, and legal conclusions in production use.
- Authority grounding note: all currently attached authority support is marked as verified_quote.

Artifact Guide:
- `README.md`: Open this when you want the package landing page with branch, trust, source, fit, and first-stop guidance in one place.
- `legal_reasoning.pl`: Open this when you want the rule-based legal formalization for constructive_denial review.
- `event_calculus.pl`: Open this when you want the event-calculus export for constructive_denial review.
- `context.json`: Open this when you want the JSON-LD context aliases and type mappings used by the package.
- `case_instance.jsonld`: Open this when you want the JSON-LD case instance representation instead of the prose-facing drafts.
- `hearing_script.txt`: Open this when you want the hearing-oriented draft rather than the fuller memorandum package.
- `hearing_script.md`: Open this when you want the hearing-oriented draft rather than the fuller memorandum package.
- `complaint_outline.txt`: Open this when you want the complaint framing and issue outline instead of prose briefing.
- `complaint_outline.md`: Open this when you want the complaint framing and issue outline instead of prose briefing.
- `demand_letter.txt`: Open this when you want the demand-letter posture and requested remedy framing.
- `demand_letter.md`: Open this when you want the demand-letter posture and requested remedy framing.
- `negotiation_summary.txt`: Open this when you want the shortest negotiation-oriented leverage summary.
- `negotiation_summary.md`: Open this when you want the shortest negotiation-oriented leverage summary.
- `advocacy_bundle.json`: Open this when you want the structured drafting and citation payload that drives the advocacy outputs.
- `memorandum.json`: Open this when you want the structured memorandum bundle for downstream tooling instead of the human-readable draft.
- `memorandum.md`: Open this when you want the editable human-readable memorandum draft.
- `memorandum_of_law.pdf`: Start with the printable memorandum because it is the strongest branch-aligned narrative for constructive_denial review.
- `dependency_graph.json`: Open this when you want the reasoning graph behind the active branch analysis.
- `dependency_citations.jsonld`: Open this when you want the JSON-LD grounding that links dependency targets to authority excerpts.
- `authority_review.json`: Open this when you want the authority audit view with support status, excerpts, and source metadata.
- `authority_review.md`: Open this when you want the authority audit view with support status, excerpts, and source metadata.
- `authority_research_note.json`: Open this when you want the source-verification and proposition-mapping research note.
- `authority_research_note.md`: Open this when you want the source-verification and proposition-mapping research note.
- `authority_summary.json`: Open this when you want the compact authority count view instead of the fuller authority audit.
- `decision_tree.json`: Open this when you want the compact decision-tree representation of the accommodation analysis.
- `summary.json`: Open this when you want the quickest branch-aware orientation for constructive_denial review.
- `brief_index.json`: Open this when you want the package-local discovery index with entry priorities, warnings, and rationale.
- `tests.json`: Open this when you want the regression fixture inventory that accompanies the package exports.
- `manifest.json`: Open this when you want the package contract and artifact inventory for validation and downstream tooling.
