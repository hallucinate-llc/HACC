# Guardianship Case Graph Notes

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
5. Client-side allegations assert that a prior appointment involving Jane Cortez and Benjamin Barber already existed, and that Benjamin Barber avoided service, disregarded enforceability, and interfered with housing contract processes.
6. The contradiction between item 4 and item 5 is the current highest-priority verification issue.

## Client-asserted allegations now staged in graph form

- `evt:client_asserts_prior_appointment_to_benjamin`
- `evt:client_asserts_benjamin_avoided_service`
- `evt:client_asserts_benjamin_disregarded_enforceable_order`
- `evt:client_asserts_benjamin_interfered_housing_contract`
- `evt:skee_reported_outside_document_flows_caused_lease_removal`
- `evt:inference_solomon_or_stepfather_outside_influence_on_lease_change`

Status rule: all four are tracked as `asserted_by_client_pending_documentary_proof`.
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

No sanctions, contempt, or collateral-estoppel claim should move to final filing status until these proof gates are satisfied.

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
