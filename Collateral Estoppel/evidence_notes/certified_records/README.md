# Certified Records Staging Folder

Place future certified prior-proceeding materials here so the formal logic layer can detect them automatically.

## Important note

This folder is for staged clerk-issued or later-added prior-proceeding materials.
It does not mean the workspace lacks prior source materials now.

Current initial prior-proceeding source set:

1. [initial_prior_proceeding_source_set_note_2026-04-08.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/initial_prior_proceeding_source_set_note_2026-04-08.md)

## Suggested filename markers

1. prior order / judgment:
`prior_order_...`, `signed_order_...`, `judgment_...`

2. docket / register:
`docket_...`, `register_...`, `register_of_actions_...`, `roa_...`

3. hearing / appearance:
`hearing_...`, `appearance_...`, `minutes_...`, `transcript_...`

## Current logic behavior

The generator promotes issue-preclusion audit elements when this folder contains:

1. a prior-order file;
2. a docket/register file; and
3. a hearing/appearance file.

This only upgrades the audit state. It does not itself prove issue preclusion on the merits.
