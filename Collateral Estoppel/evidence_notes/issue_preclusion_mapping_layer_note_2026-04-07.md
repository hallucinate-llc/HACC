# Issue Preclusion Mapping Layer Note

The workspace now has a third-stage promotion layer for issue preclusion.

## Promotion ladder

The issue-preclusion branch now progresses in three stages:

1. doctrine grounded;
2. certified materials present; and
3. elements mapped.

That is a better structure than jumping directly from “we found a docket” to “issue preclusion applies.”

## Structured mapping file

The new structured mapping file is:

[issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)

Its guide is:

[issue_preclusion_mapping_guide.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping_guide.md)

## What the generator now does

The generator now keeps these rows separate:

1. `prior_separate_proceeding_record`
2. `identical_issue_mapped`
3. `finality_mapped`
4. `party_privity_mapped`
5. `full_fair_opportunity_mapped`
6. `identical_issue_and_finality_mapping`

That means the audit can now distinguish:

1. whether certified materials exist at all; and
2. whether someone has actually mapped the materials to the Oregon issue-preclusion elements.

## Why this is useful

This reduces a common failure mode in legal graph-building: treating record presence as if it were already element satisfaction. The new layer forces the workspace to pause between:

1. locating records; and
2. asserting that the doctrine applies.
