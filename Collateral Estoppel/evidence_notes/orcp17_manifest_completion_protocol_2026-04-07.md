# ORCP 17 Manifest Completion Protocol - 2026-04-07

Use this note when deciding whether a sanctions predicate in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json) should remain staged, become mapped, or stay proof-gated.

## Current posture

The current safe state is:

1. `challenged_filing_identified = true`
2. `unsupported_factual_assertion_mapped = false`
3. `unsupported_legal_position_mapped = false`
4. `improper_purpose_mapped = false`

That means the sanctions branch is filing-specific, but no sanctions predicate has yet been promoted.

## Promotion thresholds

### Unsupported factual assertion

Promote only when a specific factual assertion in the challenged filing is contradicted by a staged source record that has been reviewed directly.

Current candidate:

1. the petition-side statement that no guardian had previously been appointed for Jane Cortez

Do not promote unless the conflicting prior order is actually staged and checked.

Use [orcp17_prior_order_contradiction_intake_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_prior_order_contradiction_intake_note_2026-04-07.md) to decide whether the contradiction is strong enough to move from candidate theory to mapped predicate.

### Unsupported legal position

Promote only when:

1. the challenged legal position is identified in the filing;
2. the controlling authority is grounded in the authority table; and
3. the record facts needed to apply that authority are staged and mapped.

Current candidate:

1. a guardianship filing that may become legally unsupported if certified prior-proceeding materials and completed issue-preclusion mapping show impermissible relitigation

Do not promote unless the prior-proceeding record and issue-preclusion mapping are complete enough to support the doctrinal application.

Use [orcp17_issue_preclusion_bridge_intake_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_issue_preclusion_bridge_intake_note_2026-04-07.md) to decide whether the issue-preclusion branch is mature enough to support a legal-position promotion.

### Improper purpose

Promote only when the filing-specific record supports a purpose such as delay, pressure, or collateral control strongly enough to describe the theory as mapped rather than merely suspected.

Current candidate:

1. a filing used to obtain control, create delay, or exert collateral pressure in parallel with collateral-channel conduct

Do not promote unless stronger filing-specific motive support is staged.

Use [orcp17_improper_purpose_intake_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/orcp17_improper_purpose_intake_note_2026-04-07.md) to decide whether the filing-specific motive record is strong enough to support promotion.

## Required update sequence

When any predicate is ready to promote:

1. update the corresponding worksheet in `/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set`;
2. update the note field and boolean in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json);
3. rerun the formal generators;
4. confirm the new audit state in [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md); and
5. verify the resulting branch status in [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md).

## Failure condition

If the record improves only partially, update the note fields but leave the boolean `false`. Partial improvement should sharpen the explanation before it changes the logic state.
