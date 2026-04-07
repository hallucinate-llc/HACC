# Issue Preclusion Mapping Guide

Use [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json) after certified prior-proceeding materials have been staged in this folder.

## Purpose

This file is the structured bridge between:

1. raw certified materials being present; and
2. actual issue-preclusion elements being mapped.

## Fields

Set these booleans to `true` only when the certified materials support the element:

1. `identical_issue_mapped`
2. `finality_mapped`
3. `party_privity_mapped`
4. `full_fair_opportunity_mapped`

Use the paired `..._note` fields to record the short explanation and citation basis.

## Effect on the logic layer

The issue-preclusion audit will promote:

1. the individual element rows when their booleans are set to `true`; and
2. the aggregate `identical_issue_and_finality_mapping` row when the certified materials are present and all four mapping booleans are true.

This still does not automatically prove that the court should apply issue preclusion. It only upgrades the formal record from “materials present” to “elements mapped.”
