# Issue-Preclusion Certified Retrieval Queue - 2026-04-07

Purpose:
- Convert row-3 issue-preclusion branch from theory/alleged state to certified element support, focusing on `finality` and `full_fair_opportunity`.

## Priority case targets

1. `26PR00641` (current guardianship proceeding context)
2. `25PO11530` (Julio-related protective order record referenced in timeline)
3. `26P000432` (Jane Kay Cortez v. Ashley Ferron protective-proceeding filing noted as denied)
4. `26P000433` (Benjamin Jay Barber v. Ashley Ferron protective-proceeding filing noted as denied)

## Certified record requests by element

### A) Finality element

Request certified copies of:
1. Signed final order/judgment or disposition order for each target case above.
2. Register of actions / docket printout showing final disposition status and date.
3. Any denial/grant minute entry tied to the same disposition date.

Use labels in request packet:
- `finality_record__<case>__signed_disposition_order`
- `finality_record__<case>__register_of_actions`
- `finality_record__<case>__disposition_minutes`

### B) Full and fair opportunity element

Request certified copies of:
1. Hearing setting notices / orders to appear.
2. Appearance minutes / hearing minutes / appearance register.
3. Service/notice proof tied to the hearing date.

Use labels in request packet:
- `opportunity_record__<case>__hearing_setting_notice`
- `opportunity_record__<case>__appearance_or_minutes`
- `opportunity_record__<case>__service_or_notice_proof`

### C) Party/privity and identical-issue support

Request certified copies of:
1. Caption pages and party-identification pages for prior proceeding records.
2. Pleadings/orders that define the adjudicated issue.
3. Any line-item register text describing issue disposition scope.

Use labels:
- `identity_record__<case>__caption_and_parties`
- `issue_record__<case>__pleading_or_order_issue_scope`

## Repository sources to cross-check while requesting

1. [protective_order_and_hacc_notice_timeline.md](/home/barberb/HACC/Collateral Estoppel/evidence_notes/protective_order_and_hacc_notice_timeline.md)
2. [00_exhibit_legend_global.md](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/00_exhibit_legend_global.md)
3. [42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md)
4. [53_issue_preclusion_mapping_prefill_review_packet_2026-04-07.md](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/53_issue_preclusion_mapping_prefill_review_packet_2026-04-07.md)

## Intake routing

1. Save all certified files under:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`
2. Log each item in:
- [45_certified_records_intake_tracker_template_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/45_certified_records_intake_tracker_template_2026-04-07.csv)
3. Update mapping notes in:
- `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json`

## Promotion safety

Do not set any of these to `true` until certified records are actually staged and cited:
- `finality_mapped`
- `full_fair_opportunity_mapped`
- `identical_issue_mapped`
- `party_privity_mapped`

## Recompute commands after each certified intake batch

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_evidence_candidates.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_mapping_prefill.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
```
