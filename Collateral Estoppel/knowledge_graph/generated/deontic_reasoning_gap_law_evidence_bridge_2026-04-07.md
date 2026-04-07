# Deontic Reasoning Gap Bridge (Law + Caselaw + Evidence)

Generated: 2026-04-07

## Purpose

This memo maps each remaining strict unresolved rule to:
- governing law/caselaw already grounded in the workspace, and
- the specific evidence packet needed to convert unresolved predicates to verified predicates.

## Current unresolved strict rules

1. `r1_guardian_permission_if_prior_appointment`
2. `r2_noninterference_prohibition_for_benjamin`
3. `r3_benjamin_obligation_comply_or_seek_relief`
4. `r5_solomon_obligated_appear_and_answer`
5. `r7_solomon_forbidden_refile_precluded_issue`
6. `r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved`

## Newly grounded and activated in this pass

1. `r40_benjamin_permitted_act_as_gal_under_signed_eppdapa_order`
2. `r41_solomon_obligated_follow_petitioner_guardian_or_conservator_instructions`
3. `r42_solomon_forbidden_disobey_guardian_instruction_term_after_appearance`

Grounding basis used:
- law: `ORS 124.020` (EPPDAPA restraining-order relief framework)
- evidence: [restraining_order_visual_verification_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/restraining_order_visual_verification_2026-04-07.md)
- source scan: `/home/barberb/HACC/evidence/history/sam barber restraining order.pdf`

## Rule-by-rule bridge

### r1 / r2 / r3 (prior appointment and derivative interference/disregard claims)

Blocking facts:
- `f_client_prior_appointment` (alleged)
- `f_client_benjamin_housing_interference` (alleged, r2)
- `f_client_benjamin_order_disregard` (alleged, r3)

Law/caselaw anchors:
- `ORS 125.050` (protective proceeding ORCP/OEC procedural framework)
- `ORCP 17 C(2)-(4)` (unsupported factual assertions must remain proof-gated)

Evidence record needed:
- Certified appointment order for Jane Cortez and any modification/termination order.
- Certified docket/register tying order status to relevant dates.
- If interference/disregard is asserted, add source-backed event records (housing notices, communications, or court filings) with actor/date alignment.

Local packet/workstream:
- `drafts/final_filing_set/52_prior_appointment_certified_packet_checklist_r1_r2_r3_2026-04-07.md`

### r5 / r24 (nonappearance to show-cause/compel appearance path)

Blocking fact:
- `f_client_solomon_failed_appearance` (alleged)

Newly staged supporting-but-not-dispositive service-chain evidence:
- `f_message_requested_service_address_2025_11_17` (verified)
- `f_message_requested_service_address_2025_11_20` (verified)
- `f_message_stated_intent_alternative_service_if_avoidance_2025_11_21` (verified)
- `f_solomon_service_position_statement` + `f_solomon_wait_for_service...` chain (verified)
- `f_counsel_disclaimed_accepting_service_for_solomon_2026_04_04` (verified)
- grouped in: [r5_r24_service_evasion_text_chain_2026-04-07.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/r5_r24_service_evasion_text_chain_2026-04-07.md)

Interpretation note:
- This chain supports documented service-channel conflict/evasion posture and diligence.
- It does **not** replace certified proof of actual nonappearance after a served order to appear.

Law/caselaw anchors:
- `ORS 33.055` (appearance order and remedial contempt procedure)
- `ORS 33.075` (compelling appearance after failure to appear)

Evidence record needed:
- Certified register/minute entry proving nonappearance.
- Service record/order-to-appear record proving the duty to appear was properly served.
- Identity tie-in for case number/date/person.

Local packet/workstream:
- `drafts/final_filing_set/41_certified_nonappearance_packet_checklist_r24_2026-04-07.md`

### r7 (issue preclusion / collateral estoppel merits prohibition)

Blocking facts:
- `f_collateral_estoppel_candidate` (theory)
- `f_client_solomon_barred_refile` (alleged)

Law/caselaw anchors:
- `Nelson v. Emerald PUD (1993)`
- `Rawls v. Evans (2010)`
- `Hayes Oyster v. Dulcich (2005)`
- `Westwood Construction v. Hallmark Inns (2002)`

Evidence record needed:
- Certified prior final order/judgment from separate prior proceeding.
- Certified docket/register proving finality and party/privity alignment.
- Refiled/current pleading proving same issue relitigation.
- Hearing/appearance record support for full-and-fair opportunity element.

Local packet/workstream:
- `drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md`
- `evidence_notes/certified_records/issue_preclusion_mapping.json`

## Mapping status improvements completed in this pass

- `issue_preclusion_mapping.json` now has populated element notes and candidate references.
- All element booleans remain `false` pending certified record support.
- This keeps ORCP 17 compliance posture conservative while preserving structured intake targets.

## Formal closure statements (for f-logic / TDFOL / event calculus alignment)

- `need_verified(f_client_prior_appointment).`
- `need_verified(f_client_solomon_failed_appearance).`
- `need_verified(f_collateral_estoppel_candidate).`
- `need_verified(f_client_solomon_barred_refile).`
- `requires_holds_at(f_client_solomon_failed_appearance, true, T).`
- `requires_holds_at(f_collateral_estoppel_candidate, true, T).`

## Practical closure order

1. Close `r5`/`r24` together by certifying nonappearance + service records.
2. Close `r7` via certified prior proceeding + mapped issue-preclusion elements.
3. Close `r1`/`r2`/`r3` only after certified appointment chain and actor-specific interference/disregard proofs are staged.
