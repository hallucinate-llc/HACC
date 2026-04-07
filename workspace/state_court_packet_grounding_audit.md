# State-Court Packet Grounding Audit

Case No. 26FE0586

This audit is meant to answer one question:

`Is every major point in the state-court packet grounded in actual law and record facts, and have we separated verified facts from inference?`

Short answer:

- `Yes` for the core anti-eviction theory, if stated carefully.
- `Yes` for the joinder and show-cause theories, if stated as process-chain theories.
- `No` if we overstate what the graph or prover establishes by itself.

## 1. What Is Verified By Primary Law

These points are grounded in primary legal sources:

### A. Section 18 relocation duties exist

Verified by:

- `42 U.S.C. § 1437p`
- `24 C.F.R. § 970.21`

Safe statement:

- HACC had real relocation and replacement-housing duties in connection with demolition/disposition-related displacement.

### B. RAD/PBV hearing-before-eviction requirement appears in HACC's own Administrative Plan

Verified by:

- HACC Administrative Plan, `18-VI.H. Informal Reviews and Hearings`

Safe statement:

- In the RAD/PBV structure HACC adopted, the owner had to provide an opportunity for an informal hearing before eviction.

### C. Blossom was represented as part of an HACC PBV waitlist process

Verified by:

- [blossom-community-apartments](/home/barberb/HACC/blossom-community-apartments)

Safe statement:

- HACC publicly stated that applications for Blossom and Community Apartments would be processed through HACC's PBV waitlist and that relocation households were priority groups.

## 2. What Is Verified By Record Facts

### A. HACC directed the household into a Blossom-or-TPV process

Verified by:

- [HACC Jan 2026 blossom.pdf](/home/barberb/HACC/evidence/paper%20documents/HACC%20Jan%202026%20blossom.pdf)

Safe statement:

- HACC told the household it had to choose between moving forward with Blossom and Community Apartments or using a Tenant Protection Voucher.

### B. HACC later admitted the intake packet had gone to Quantum staff and not reached HACC

Verified by:

- [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)

Safe statement:

- HACC later acknowledged in writing that the intake packet had been submitted to Quantum staff at the Hillside Manor leasing office but had not been provided to HACC.

### C. Waterleaf / Multnomah path remained incomplete across four calendar months

Verified by:

- [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
- [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)
- [message.eml](/home/barberb/HACC/workspace/temporary-cli-session-migration/prior-research-results/full-evidence-review-run/chronology/emergency_motion_packet/exhibits/Exhibit%20M%20-%20starworks5-ktilton-orientation-import/0008-Re-HCV-Orientation-CAMTdTS_hM81x2YFGZBGX3tGzBJjMjn5WhiFW-NwOC0k23-63LQ-mail.gmail.com/message.eml)

Safe statement:

- The Waterleaf application existed by December 23, 2025, HACC knew the path was active by January 12 and January 26, and it still remained incomplete in late March 2026.

## 3. What Is Verified By Law Plus Fact Together

These are the strongest packet theories because they are grounded both legally and factually.

### A. HACC had a barred-eviction problem if relocation remained materially incomplete

Law:

- `42 U.S.C. § 1437p`
- `24 C.F.R. § 970.21`

Facts:

- relocation was triggered;
- HACC directed the household into Blossom or TPV;
- HACC later admitted the intake-routing failure;
- Waterleaf / portability remained incomplete.

Safe statement:

- On the present record, HACC's push toward eviction occurred while the relocation and replacement-housing process remained materially incomplete.

Safer still:

- `The record supports that HACC was barred from filing eviction while those duties remained materially incomplete.`

### B. Quantum belongs in the case as part of the processing chain

Law / procedure:

- ORCP 29A
- ORCP 22C as fallback third-party-practice rule; ORCP 22B is limited to cross-claims between defendants already in the case

Facts:

- HACC identifies Quantum as Hillside Manor property manager in the Administrative Plan;
- HACC says the packet went to Quantum staff and did not reach HACC.

Safe statement:

- Quantum is not a stranger to the controversy; HACC's own records place Quantum inside the disputed replacement-housing intake chain.

### C. Show cause is justified as a record-clarification request

Law / procedure:

- inherent case-management and motion practice posture in the joined dispute

Facts:

- submitted application;
- HACC-directed intake route;
- HACC acknowledgment that the packet stalled at the Quantum side;
- no clear processing result shown in the current record.

Safe statement:

- Once Quantum is before the court, the court may reasonably require Quantum to explain what happened to the application materials.

## 4. What Is Still Inference Or Needs Cautious Framing

These points should not be presented as already proved historical fact.

### A. Exact percentage of delay attributable to HACC

Current status:

- `Not mathematically provable from the present record.`

Safe statement:

- `A substantial amount, and likely most, of the documented delay from January 8, 2026 through late March 2026 was caused by HACC's own administration.`

### B. Exact contents of the signed HAP contract or management agreement

Current status:

- `Not yet in the repository.`

Safe statement:

- We currently rely on HACC's Administrative Plan and notices describing the contracts and roles, not the executed contract texts themselves.

### C. The graph and prover prove all disputed facts

Current status:

- `False if stated that way.`

Safe statement:

- The graph and prover verify the encoded deontic model and dependency structure.
- They do not, by themselves, prove every disputed historical fact.

## 5. Graph Verification Status

### A. Knowledge graph basis

Current formal sources:

- [title18_contract_eviction_bar_knowledge_graph.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_contract_eviction_bar_knowledge_graph.json)
- [title18_contract_eviction_bar_dependency_graph.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_contract_eviction_bar_dependency_graph.json)
- [title18_contract_eviction_bar_report.md](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_contract_eviction_bar_report.md)
- [title18_contract_eviction_bar_tdfol_proof_audit.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_contract_eviction_bar_tdfol_proof_audit.json)

### B. What has been verified

Verified:

- the graph's central normative thesis is internally consistent;
- the TDFOL audit returns `proved` for the core obligation/prohibition nodes:
  - `section18_relocation_completion_required`
  - `hacc_relocation_counseling_required`
  - `hacc_moving_expenses_required`
  - `hacc_comparable_replacement_required`
  - `hacc_perform_relocation_commitment`
  - `hacc_administer_implied_relocation_process`
  - `eviction_forbidden_while_duties_incomplete`
  - `eviction_forbidden_while_undertaken_performance_incomplete`

Not verified in that same sense:

- every disputed historical event;
- the full contents of missing executed contract documents;
- every causal inference beyond the encoded record.

### C. Court-safe use of the graph

Court-safe statement:

- `The formal model confirms that if the source-linked factual predicates are true, the resulting deontic conclusion is that eviction was forbidden while relocation and undertaken processing duties remained incomplete.`

Not court-safe:

- `The graph itself proves all facts in the case.`

## 6. Recommended Court-Safe Language

Best phrasing:

- `The record supports`
- `HACC's own documents state`
- `HACC later acknowledged in writing`
- `On the present record`
- `The formal model confirms the normative consequence of the source-linked facts`

Normalized replacements:

- Use `The record supports` rather than `This conclusively proves`, unless the point is truly undisputed.
- Use the specific source name rather than `The contracts say` when the point actually comes from an Administrative Plan provision, a notice, or an email.
- Use `The formal model confirms the encoded normative consequence` rather than `The graph proves`, unless you are expressly discussing the model itself rather than the historical facts.

## 7. Bottom Line

The packet is in a strong position if we stay within the following boundaries:

- use primary law for the federal duties;
- use HACC's own Administrative Plan, public page, notices, and emails for the local process;
- describe the Quantum theory as a process-chain theory;
- describe the anti-eviction theory as a source-linked Title 18 plus undertaken-process bar;
- and describe the graph/prover as formal support for the legal consequence of the verified record, not as a substitute for the record itself.
