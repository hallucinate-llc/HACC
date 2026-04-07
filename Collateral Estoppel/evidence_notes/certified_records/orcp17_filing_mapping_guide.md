# ORCP 17 Filing Mapping Guide

Use [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json) to map sanctions predicates to a specific challenged filing.

## Purpose

This file keeps the sanctions branch filing-specific instead of collapsing everything into a general accusation.

## Core fields

Set these booleans to `true` only when you can support them for a specific challenged filing:

1. `challenged_filing_identified`
2. `improper_purpose_mapped`
3. `unsupported_legal_position_mapped`
4. `unsupported_factual_assertion_mapped`

Use the paired note fields to capture the short explanation and citation basis.

Conservative current example:

1. a challenged filing can be identified now; but
2. an `unsupported_factual_assertion` row should remain false unless the conflicting source record is actually staged and checked.
3. an `unsupported_legal_position` row should remain false unless the prior-proceeding record and issue-preclusion mapping are actually staged and checked.
4. an `improper_purpose` row should remain false unless the filing-specific control / delay / collateral-pressure theory is tied to stronger direct record support.

## Effect on the logic layer

The `ORCP 17` audit will promote:

1. the individual filing-specific rows when their booleans are set to `true`; and
2. the aggregate `improper_purpose_or_unsupported_filing_proof` row when all filing-specific booleans are true.

This does not itself impose sanctions. It only formalizes whether the current record has actually mapped the sanction predicates to a specific filing.

## Boolean flip rules

Use the following threshold rules before changing a predicate from `false` to `true`:

1. `challenged_filing_identified`
Set to `true` only when the challenged filing is identified by caption or equivalent description, date, and source file or docket anchor.

2. `unsupported_factual_assertion_mapped`
Set to `true` only when:
- the specific factual assertion is quoted or summarized from the challenged filing;
- the conflicting record is staged in the repository;
- the conflict is checked against the source record rather than memory or theory alone; and
- the note identifies both the filing assertion and the conflicting source.

3. `unsupported_legal_position_mapped`
Set to `true` only when:
- the challenged legal position is identified from the filing;
- the governing authority is already grounded in the authority table;
- the required record facts for applying that authority are staged; and
- the note states why the filing position fails under the grounded authority.

4. `improper_purpose_mapped`
Set to `true` only when:
- the challenged filing is tied to a concrete improper-purpose theory;
- the theory is supported by filing-specific conduct or record material, not only generalized suspicion;
- the note identifies the supporting documents or communications; and
- the record is strong enough that the claim can be described as mapped rather than merely suspected.

## Recommended verification sequence

Before flipping any predicate to `true`:

1. update the relevant worksheet in the final filing set;
2. update the paired note in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json);
3. rerun the formal artifact generator;
4. confirm the promotion in [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md); and
5. check [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md) to make sure the branch status still matches the proof state you intended.
