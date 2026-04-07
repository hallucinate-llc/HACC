# Certified Records Staging Folder

Place future certified prior-proceeding materials here so the formal logic layer can detect them automatically.

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
