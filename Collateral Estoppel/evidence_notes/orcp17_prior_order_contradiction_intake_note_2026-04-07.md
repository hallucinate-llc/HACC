# ORCP 17 Prior-Order Contradiction Intake Note - 2026-04-07

Use this note when a prior appointment or prior authority order is staged and you need to decide whether the `unsupported_factual_assertion_mapped` predicate should be promoted.

## Purpose

This note is the bridge between:

1. raw prior-order material being present in [certified_records](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/README.md); and
2. a decision to mark the petition-side factual-assertion contradiction as actually mapped.

## Current target assertion

The current candidate contradiction is:

1. the petition-side statement that no guardian had previously been appointed for Jane Cortez

Primary source anchors:

1. [solomon_motion_for_guardianship_ocr.txt](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt)
2. [48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md)

## Intake questions

Do not promote the predicate unless all of these questions can be answered from staged source material:

1. Does the prior order actually concern Jane Cortez?
2. Does the prior order actually appoint a guardian, conservator, or other authority relevant to the petition assertion?
3. Is the order dated before the challenged filing dated March 31, 2026?
4. Is the identity match strong enough that the contradiction does not depend on speculation?
5. Can the contradiction be described from the order itself rather than from secondary memory or theory?

## Minimum contradiction package

The safest minimum package is:

1. one staged prior-order file in `evidence_notes/certified_records`
2. one short note identifying the contradictory language or effect of that order
3. one updated worksheet entry in [48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/48_orcp17_unsupported_factual_assertion_worksheet_2026-04-07.md)
4. one manifest update in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)

## Do not promote if

Leave `unsupported_factual_assertion_mapped` as `false` if any of the following remains unresolved:

1. the order is not yet staged;
2. the order does not clearly match Jane Cortez;
3. the order does not clearly establish the relevant prior authority;
4. the contradiction still depends on inference rather than direct record comparison.

## After promotion

If the contradiction is clean enough to promote:

1. update the worksheet;
2. update the note and boolean in [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json);
3. rerun the generators; and
4. confirm the updated state in [orcp17_readiness_snapshot.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/orcp17_readiness_snapshot.md), [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md), and [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md).
