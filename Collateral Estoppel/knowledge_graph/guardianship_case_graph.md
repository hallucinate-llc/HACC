# Guardianship Case Graph Notes

System index:
- [graph_system_index.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_system_index.md)
- [graph_system_index.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/graph_system_index.json)

## Main actors

- `person:solomon`
- `person:jane_cortez`
- `person:benjamin_barber`
- `org:hacc`

## Main event chain under review

1. On `2026-03-31`, Solomon Barber filed a first amended petition seeking temporary and indefinite guardianship over Jane Kay Cortez in case `26PR00641`.
2. On `2026-04-02`, the packet included a notice to respondent explaining objection rights.
3. On `2026-04-05`, the packet appears to include a signed respondent objection form.
4. The petition itself states that no prior guardian had been appointed.
5. The earlier Solomon restraining-order packet itself supports that `Benjamin Jay Barber` appeared there in the guardian ad litem / guardian petitioner role for `Jane Kay Cortez`.
6. Additional client-side allegations assert broader prior appointment, service, enforceability, and housing-interference theories that still require separate proof.
7. The main verification issue is therefore narrower than before: whether the petition's denial of prior appointment can stand in light of the earlier GAL-linked protective-order record and any other source orders that may still exist.

## Client-asserted allegations now staged in graph form

- `evt:client_asserts_prior_appointment_to_benjamin`
- `evt:client_asserts_benjamin_avoided_service`
- `evt:client_asserts_benjamin_disregarded_enforceable_order`
- `evt:client_asserts_benjamin_interfered_housing_contract`
- `evt:skee_reported_outside_document_flows_caused_lease_removal`
- `evt:inference_solomon_or_stepfather_outside_influence_on_lease_change`

Status rule: all four are tracked as `asserted_by_client_pending_documentary_proof`.
Clarification:
- the separate proposition that `Benjamin Jay Barber` appeared in the Solomon order packet as Jane's guardian ad litem / guardian petitioner is source-backed from that packet and is not merely client assertion.
Extended status rule:
- the `skee_reported_outside_document_flows` node is tracked as `declaration_supported_statement_of_what_was_heard`
- the `solomon_or_stepfather_outside_influence` node is tracked as `bounded_inference_pending_source_actor_proof`

## Proof-gate nodes added for this stage

- `proof:prior_appointment_order`
- `proof:service_or_evasion_record`
- `proof:order_enforceability_timeline`
- `proof:housing_contract_and_interference_record`
- `proof:lease_change_request_source_record`
- `proof:claimed_authority_or_poa_record`
- `proof:second_benjamin_vs_solomon_matter_packet`
- `proof:mail_packet_contents_identification`
- `proof:solomon_order_docket_metadata`
- `proof:image_authentication_record`
- `proof:damages_quantification_record`

No sanctions, contempt, or collateral-estoppel claim should move to final filing status until these proof gates are satisfied.

Current gap summary memo:
- [remaining_evidentiary_gaps_memo_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/remaining_evidentiary_gaps_memo_2026-04-07.md)
  This memo consolidates the main remaining proof gaps after the current mailing-trail and notice work:
  1. packet identity;
  2. Solomon-order docket metadata;
  3. prior-order / prior-appointment materials;
  4. direct Solomon-to-HACC attribution;
  5. service / evasion specificity;
  6. damages quantification; and
  7. image authentication.

Current damages support tools:
- [hacc_damages_worksheet_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/hacc_damages_worksheet_2026-04-07.md)
- [declaration_of_benjamin_barber_re_hacc_damages_and_costs.md](/home/barberb/HACC/Collateral%20Estoppel/drafts/declaration_of_benjamin_barber_re_hacc_damages_and_costs.md)
  Best current use:
  1. the worksheet structures postage, copying, transport, moving, delay, and instability categories;
  2. the declaration preserves the damages theory in witness form; and
  3. the branch is staged but still needs actual amounts and supporting records.

## March 23 inspection / lease-removal branch

The graph now separately tracks the March 23, 2026 inspection declarations as a distinct branch:
- Benjamin and Jane both say they personally heard Charley Skee explain, in substance, that Benjamin had been taken off the lease because Benjamin's brother and stepfather had been emailing documents to HACC.
- That branch supports an `outside document flows influenced lease decision` theory.
- It does not yet directly prove that Solomon specifically exercised lawful or unlawful authority, or that HACC relied on a power of attorney.
- A January 12, 2026 HACC email now directly supports that HACC removed Benjamin effective January 1, 2026 after `internal review` and based on `court documentation currently on file`, but it still does not identify which actor supplied the decisive authority record.

Best current use:
- preserve the Skee discussion as declaration-supported evidence of outside influence on HACC's lease handling;
- preserve the Solomon / claimed-authority proposition as a bounded inference and discovery target.

Primary follow-up memo:
- [lease_removal_authority_discovery_memo.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/lease_removal_authority_discovery_memo.md)
  This memo isolates the concrete records, admissions, and deposition questions most likely to identify who requested Benjamin's lease removal and what claimed authority HACC relied on.

## Deontic linkage included in graph

The graph now includes deontic theorem nodes tied to this case posture:
- `theorem:t1_valid_appointment_confers_guardian_permission`
- `theorem:t2_notice_plus_valid_order_creates_noninterference_prohibition`
- `theorem:t3_disregard_after_notice_supports_sanctions_path`
- `theorem:t4_housing_interference_against_valid_authority_supports_remedial_request`

These are staged as formal modeling aids, not final legal conclusions.

## ORCP 17 workflow extension

The sanctions branch now also has a modular workflow subgraph:
- [orcp17_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/orcp17_workflow_subgraph.json)
- [orcp17_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/orcp17_workflow_subgraph.md)

That subgraph tracks the live manifest, readiness snapshot, branch checklist, and the three intake-gated predicates for:
- unsupported factual assertion
- unsupported legal position
- improper purpose

Best current use:
- keep the main guardianship graph focused on parties, events, proof targets, and deontic issues;
- use the ORCP 17 workflow subgraph for sanctions-branch state transitions and promotion logic.

## Exhibit R workflow extension

The HACC authority-chain production branch now also has a modular workflow subgraph:
- [exhibit_r_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/exhibit_r_workflow_subgraph.json)
- [exhibit_r_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/exhibit_r_workflow_subgraph.md)

That subgraph tracks:
- the nonparty HACC production path,
- the main proof targets behind Benjamin's lease removal,
- the prefilled packet documents,
- and the live service-log states from `ready_to_serve` through `motion_to_compel_stage`.

Best current use:
- keep the main graph centered on underlying case facts and proof gates;
- use the Exhibit R workflow subgraph for subpoena-path execution, service-state transitions, and compel escalation logic.

Related bounded notice theory:
- [hacc_order_notice_candidate_note_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/hacc_order_notice_candidate_note_2026-04-07.md)
  This now preserves two related but distinct points:
  1. preserved March 17, 2026 emails directly show written HACC notice of restraining-order concerns; and
  2. the narrower claim that Benjamin emailed the actual Solomon protective order to HACC remains client-supported pending identification of the preserved order-transmission message.
- [hacc_feb_2_restraining_order_documents_notice_memo_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/hacc_feb_2_restraining_order_documents_notice_memo_2026-04-07.md)
  This preserves an earlier February 2, 2026 HACC email in which Benjamin said he was going to send `the restraining order documents` to HACC's office.
  Best current use:
  1. it supports an earlier HACC-side notice / routing point; and
  2. it still does not confirm that the preserved attached images in that email are the Solomon order itself.
- [hacc_mail_photo_and_tracking_candidate_memo_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/hacc_mail_photo_and_tracking_candidate_memo_2026-04-07.md)
  This preserves a stronger mailing trail:
  1. a January 26, 2026 photo sequence consistent with a packet prepared for HACC;
  2. [Delivery Feb 2nd.HEIC](/home/barberb/HACC/evidence/history/Delivery%20Feb%202nd.HEIC), a direct photo of a USPS Priority Mail envelope at a mailbox with a visible label consistent with HACC's address; and
  3. a later USPS tracking screenshot showing delivery in Oregon City on January 27, 2026.
  Best current use:
  1. it strongly supports a real mailing to HACC; and
  2. it still does not conclusively identify the mailed contents as the restraining-order packet itself.

## Second Solomon matter now separately tracked

The graph now separately preserves the April 3-4, 2026 counsel-service chain as evidence that a second Solomon-related matter was being asserted:

- preserved subject line: `Jane Kay Cortez vs Solomon Samuel Barber, Benjamin Jay Barber vs Solomon Samuel Barber`
- direct transmission to `alex@salemprobate.com`
- linked file name in the email body: `sam barber restraining order.pdf`
- preserved attached image `IMG_2167.jpeg` OCRs as a same-day FedEx receipt to Alexander M. Bluestone in Salem, Oregon, with tracking `870305656111`
- reply acknowledging the message while declining service acceptance
- preserved same-subject follow-up content also asserts that guardianship had already been granted in a case involving the same exact parties

Best current use:
- preserve the existence of a separately referenced `Benjamin Jay Barber vs Solomon Samuel Barber` matter at the notice level;
- preserve that the underlying linked order packet already supports a narrower, source-backed proposition that `Benjamin Jay Barber` appears there as Jane's guardian ad litem / guardian petitioner;
- do not yet treat the underlying court packet, case number, or exact operative filing as proven until the source documents are staged.

Primary memo:
- [second_solomon_matter_service_chain_memo_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/second_solomon_matter_service_chain_memo_2026-04-07.md)

Related distinction memo:
- [solomon_sms_notice_vs_service_distinction_memo_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/solomon_sms_notice_vs_service_distinction_memo_2026-04-07.md)
  This memo preserves the narrower, stronger SMS record:
  1. Solomon texted that he had heard about the restraining order;
  2. Solomon later claimed the order was not in effect until service; but
  3. the repository does not currently show the April 3 attorney-service language inside the preserved Solomon SMS archive.

## Issue-preclusion workflow extension

The certified-records and issue-preclusion intake branch now also has a modular workflow subgraph:
- [issue_preclusion_workflow_subgraph.json](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.json)
- [issue_preclusion_workflow_subgraph.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/issue_preclusion_workflow_subgraph.md)

That subgraph tracks:
- certified-records staging gates,
- the live issue-preclusion mapping manifest,
- separate predicate states for record presence and mapped elements,
- and the relationship between those stages and the proof-gated merits branch.

Best current use:
- keep the main graph centered on case facts and broad issues;
- use the issue-preclusion workflow subgraph for certified-record intake, element mapping, and later promotion into the live deontic branch.
