# Issue-Preclusion Case-Specific Clerk Request Packets - 2026-04-07

Purpose:
- Provide ready-to-use request language for certified records needed to complete issue-preclusion element mapping for row 3 (`r7`).

Court target:
- Clackamas County Circuit Court (confirm division/filing window before submission)

## Global request language (apply to each case)

Request certified copies of the following records for the case identified below:

1. Final signed disposition order / judgment (grant, denial, dismissal, or equivalent final ruling).
2. Register of actions / docket printout showing filing and disposition history.
3. Hearing setting notice(s), orders to appear, and hearing minute entries.
4. Appearance register and any transcript/minute summary identifying party participation/nonappearance.
5. Proof(s) of service and notice tied to the hearing(s) and disposition event(s).
6. Caption and party-identification pages sufficient to identify all parties and role alignment.

Certification requested:
- Please include clerk certification for each record set and indicate the certification date.

Delivery preference:
- Certified paper copies and, if permitted, parallel secure electronic copies.

## Case packet A: `26PR00641`

Record purpose:
- Current guardianship proceeding context and relation to later-filed issue-preclusion assertions.

Request emphasis:
1. Any prior-order references embedded in register entries.
2. Hearing/appearance entries relevant to objection and participation history.
3. Final disposition markers, if any.

Suggested intake filenames:
- `prior_order__26PR00641__YYYYMMDD__prior_final_order.pdf`
- `docket__26PR00641__YYYYMMDD__register_of_actions.pdf`
- `hearing__26PR00641__YYYYMMDD__appearance_minutes_or_transcript.pdf`

## Case packet B: `25PO11530`

Record purpose:
- Prior protective-order proceeding referenced as part of order-history and potential preclusion context.

Request emphasis:
1. Signed grant/continuation/disposition orders.
2. Register entries showing hearing dates and disposition status.
3. Appearance and service records proving notice/opportunity chronology.

Suggested intake filenames:
- `prior_order__25PO11530__YYYYMMDD__final_or_disposition_order.pdf`
- `docket__25PO11530__YYYYMMDD__register_of_actions.pdf`
- `hearing__25PO11530__YYYYMMDD__appearance_minutes_or_transcript.pdf`

## Case packet C: `26P000432`

Record purpose:
- Filing identified in timeline as denied; needed for finality and full/fair-opportunity mapping.

Request emphasis:
1. Signed denial order.
2. Register entries establishing finality date.
3. Notice/service and appearance/hearing records.

Suggested intake filenames:
- `prior_order__26P000432__YYYYMMDD__denial_or_final_order.pdf`
- `docket__26P000432__YYYYMMDD__register_of_actions.pdf`
- `hearing__26P000432__YYYYMMDD__appearance_minutes_or_transcript.pdf`

## Case packet D: `26P000433`

Record purpose:
- Filing identified in timeline as denied; needed for finality and full/fair-opportunity mapping.

Request emphasis:
1. Signed denial order.
2. Register entries establishing finality date.
3. Notice/service and appearance/hearing records.

Suggested intake filenames:
- `prior_order__26P000433__YYYYMMDD__denial_or_final_order.pdf`
- `docket__26P000433__YYYYMMDD__register_of_actions.pdf`
- `hearing__26P000433__YYYYMMDD__appearance_minutes_or_transcript.pdf`

## Mapping usage notes after receipt

1. `finality_mapped` may be considered only after signed disposition order + register support are both certified and reviewed.
2. `full_fair_opportunity_mapped` may be considered only after hearing/appearance + notice/service support are certified and reviewed.
3. Keep all `*_mapped` booleans false until certified support is actually staged and cited.

## Intake routing

1. Save files to:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`
2. Log files in:
- [45_certified_records_intake_tracker_template_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/45_certified_records_intake_tracker_template_2026-04-07.csv)
3. Update issue-preclusion mapping notes in:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json`

## Recompute after any certified intake update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_evidence_candidates.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_mapping_prefill.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
```
