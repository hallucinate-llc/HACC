# Element Audit Layer Note

The formal reasoning system now includes element-level timing audits in addition to rule activation and interval tracking.

## Current audits

The generated reasoning report now includes:

1. `audit_remedial_contempt_timing`
2. `audit_probate_objection_hearing_timing`
3. `audit_exhibit_r_subpoena_timing`

## Why this matters

These audits let the workspace separate:

1. legal doctrine from legal elements;
2. verified elements from proof-gated elements; and
3. currently mature requests from workflow-open requests.

## Present status

### Remedial contempt timing

The current audit treats the following as verified from the local record:

1. a valid restraining order in effect;
2. notice or equivalent appearance-based notice to Solomon; and
3. later post-notice conduct inconsistent with compliance.

The remaining proof gate is a cleaner certified service / appearance / docket record for filing-grade contempt support.

### Probate objection and hearing timing

The current audit treats the following as verified:

1. notice issued to Jane Cortez;
2. objection presented; and
3. hearing path triggered under `ORS 125.075` and `ORS 125.080`.

### Exhibit R subpoena timing

The current audit treats the following as verified:

1. local repository search did not produce the HACC actor-identification record; and
2. compelled production is therefore presently justified as a workflow path.

The service stage and deficiency / compel stage remain open because those are real-world litigation events, not yet repository facts.

## Best next upgrade

The next useful extension would be to add:

1. `ORCP 17` element audits for improper purpose, unsupported legal position, and unsupported factual assertion;
2. issue-preclusion element audits for identical issue, prior separate proceeding, finality, party/privity, and full-and-fair opportunity; and
3. service-timing audits once subpoena service actually occurs.
