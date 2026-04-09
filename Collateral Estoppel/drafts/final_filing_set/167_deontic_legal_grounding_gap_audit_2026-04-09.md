# Deontic + Legal Grounding Gap Audit (2026-04-09)

Scope reviewed:
- 01, 02, 03, 04, 06, 34, 86, 117, 139, 149, 151, 152, 157, 152_objection

## High-severity gaps

1. `04_declaration_of_benjamin_barber_in_support_of_motions_final.md` has numbering/control defects that can undermine reliability of the declaration format.
- Duplicate paragraph number appears (`64.` repeated), and sequence continuity is broken around lines 90-97.
- Fix: renumber all declaration paragraphs and lock citation references to new paragraph map.

2. `34_strict_mode_evidentiary_addendum_bundle_2026-04-07.md` includes actor-misaligned deontic rules that conflict with your litigation position.
- Rules `r2_noninterference_prohibition_for_benjamin` and `r3_benjamin_obligation_comply_or_seek_relief` frame Benjamin as prohibited/obligated actor for interference/order-disregard in a posture where Solomon is the adverse interference target.
- Fix: split actor-specific rules with explicit predicates and avoid publishing contradictory actor assignment.

3. `01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md` relies on a prior GAL grant claim while also admitting certified proof is pending.
- The core asserted anchor is proof-gated (`25PO11530`), yet requested relief presumes cross-case effect.
- Fix: convert this to alternative pleading: "if prior grant confirmed, recognize/align; if not, appoint now based on present protective need."

4. `02_motion_to_dismiss_for_collateral_estoppel_final.md` mixes threshold preclusion posture with broad collateral merits narratives not yet tied to admissible records.
- Repeated "repository records reflect" statements increase hearsay/vagueness vulnerability unless each is anchored to filed exhibit IDs.
- Fix: every factual paragraph should end with an exhibit cite or be moved to a "background only, not for merits finding" subsection.

## Medium-severity gaps

5. `01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md` uses ORCP 27 as primary GAL authority without fully reconciling protective-proceeding-specific statutory structure.
- `06_oregon_authority_table_final.md` itself warns not to conflate `ORS 125.120` special-advocate authority with general GAL authority.
- Fix: tighten authority section to a specific, harmonized lane: ORS chapter 125 protective powers + ORCP applicability + explicit requested functional role.

6. `03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.md` requests sanctions and contempt-path relief but does not map each requested sanction to exact proved elements in the pleading body.
- Deontic posture (obligation/prohibition breach) is implied but not fully element-by-element mapped.
- Fix: add a short element table: duty source, trigger event, breach act, evidence ID, requested remedy.

7. `151_motion_for_limited_orcp29_joinder_or_separate_forum_order_re_hacc_quantum_final.md` and `152_fallback_motion...` are strong on ORCP 29B/22C framing but still rely on generalized "record identifies" assertions.
- This creates an evidentiary attack point at hearing.
- Fix: attach a mini exhibit map with one line per asserted overlap fact (fact -> source doc/exhibit -> admissibility status).

8. `157_supplemental_declaration_re_orcp29a_complete_relief_and_inconsistent_obligations_final.md` repeatedly uses "I understand" framing.
- That wording is safe but weakens force for contested factual predicates.
- Fix: separate personal-knowledge facts from legal conclusions and tie each conclusion to a specific attached record.

9. `139_supplemental_declaration_authenticating_cross_forum_docket_records_final.md` authenticates source channels broadly but does not specify retrieval date/time, clerk endpoint, or unique docket identifiers in each paragraph.
- Fix: add retrieval metadata fields per exhibit (source URL/system, date pulled, custodian/portal, document title).

10. `152_objection_to_first_amended_guardianship_petition_and_emergency_relief_final.md` is substantively rich but dense, with many contested assertions grouped in single sections.
- Risk: court may treat portions as argumentative rather than evidentiary.
- Fix: split into "proven now" and "proof-gated" subsections with explicit labels.

## Low-severity but credibility-sensitive gaps

11. `02_motion_to_dismiss_for_collateral_estoppel_final.md` includes constitutional-prospective challenge discussion (`ORS 163.472`) that may be viewed as collateral to threshold preclusion management.
- Fix: move to reserved supplemental memo unless and until directly raised by opposing pleadings.

12. `149_notice_of_clerk_relayed_federal_advisement_status_pending_docket_confirmation_final.md` is properly caveated but still depends on clerk-relayed oral status.
- Fix: keep notice strictly procedural and attach docket proof before relying on assignment/advisement assertions.

## Deontic-logic model gaps (cross-document)

13. Missing explicit trigger-time fields in motions for many claimed obligations/prohibitions.
- Current drafting often states obligations abstractly, but not always as: source order + trigger date + actor + prohibited/permitted act + breach event.
- Fix: add one "Deontic Trigger Table" exhibit with columns:
  `Rule_ID | Actor | Modality(O/P/F) | Source Authority | Trigger Event | Time Window | Alleged Breach/Compliance Event | Evidence ID | Status(proved/proof-gated)`.

14. Missing remedy-binding map from deontic breach to requested court action.
- Fix: add `Breach -> Remedy` matrix, e.g., `F-breach (noncooperation with effective order) -> ORS 33.055 show cause`, `proof-gated preclusion branch -> threshold hearing only`.

15. Inconsistent status labels across documents (`proof-gated`, `repository`, `understanding`, `asserted`) can blur what is currently admissible.
- Fix: normalize evidence status labels globally: `Admissible-now`, `Authentication-complete-pending-admission`, `Proof-gated`, `Context-only`.

## Fast hardening steps (recommended order)

1. Correct numbering/actor inconsistencies in `04` and `34`.
2. Add exhibit-pin cites for each factual paragraph in `01`, `02`, `03`, `151`, and `152`.
3. Add one-page deontic trigger-and-remedy table as a shared attachment used by all major motions.
4. Trim or reserve collateral constitutional arguments unless immediately necessary to the pending threshold ruling.
