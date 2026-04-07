# ORCP 17 Issue-Preclusion Bridge Intake Note - 2026-04-07

Use this note when deciding whether the `unsupported_legal_position_mapped` predicate can move from candidate theory to mapped predicate.

## Purpose

This note is the bridge between:

1. a staged and mapped issue-preclusion record; and
2. a later decision that the challenged filing advanced an unsupported legal position under `ORCP 17`.

## Current target legal position

The current candidate legal-position issue is:

1. the petition-side request by Solomon Barber to obtain guardianship authority despite the unresolved prior-authority / issue-preclusion conflict

Primary anchors:

1. [49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md)
2. [motion_to_dismiss_for_collateral_estoppel.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/motion_to_dismiss_for_collateral_estoppel.md)
3. [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)

## Intake questions

Do not promote the predicate unless all of these can be answered from staged record material and grounded authority:

1. Is there a certified or otherwise reliable prior separate proceeding record?
2. Are the doctrine authorities already grounded in the authority table and motion set?
3. Has [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json) been completed enough to support identical issue, finality, party/privity, and full/fair opportunity?
4. Can the challenged filing's legal position be described specifically enough to compare it to the mapped prior proceeding?
5. Can the unsupported-legal-position theory be stated from the staged record and authority without depending on unresolved factual assumptions?

## Minimum bridge package

The safest minimum package is:

1. staged prior-order and docket/register materials in `evidence_notes/certified_records`
2. completed or materially completed [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)
3. one updated legal-position worksheet entry in [49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/49_orcp17_unsupported_legal_position_worksheet_2026-04-07.md)
4. one manifest update in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)

## Do not promote if

Leave `unsupported_legal_position_mapped` as `false` if any of the following remains unresolved:

1. the prior separate proceeding is still not established from source records;
2. any key issue-preclusion element remains unmapped;
3. the filing-side legal position is still described only in broad theory terms;
4. the conclusion still depends on assumptions about prior authority that the certified record does not yet resolve.

## After promotion

If the doctrine-application record is strong enough to promote:

1. update the worksheet;
2. update the note and boolean in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json);
3. rerun the generators; and
4. confirm the updated state in [orcp17_readiness_snapshot.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.md), [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md), and [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md).
