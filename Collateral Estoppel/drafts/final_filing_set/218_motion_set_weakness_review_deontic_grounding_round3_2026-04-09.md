# Motion Set Weakness Review (Round 3) - 2026-04-09

This review identifies filing-risk weaknesses in motions, declarations, and memoranda, with emphasis on legal/factual grounding and deontic sequencing (what is obligatory, permitted, prohibited, and conditionally deferred).

## High Severity

1. Exhibit-reference mismatch in show-cause branch (authentication risk)
- Risk: The show-cause motion cites "Exhibit 7 communication sequence" for counsel-email/notice points, but the global legend defines Exhibit 7 as `HACC vawa violation.pdf`, not the communication chain. This creates a direct evidentiary mismatch and undermines clause-level proof mapping.
- Sources:
  - `03_motion_to_show_cause...` cites Exhibit 7 communication sequence: lines 40-41.
  - `00_exhibit_legend_global.md` defines Exhibit 7 as HACC VAWA file: line 14.
- Deontic gap:
  - O: every factual allegation used for show-cause should map to a correctly numbered authenticated exhibit.
  - Current state: violated for at least the counsel-email chain citation.

2. Undefined/unstable exhibit label in alternative show-cause motion
- Risk: `03A` relies on "Exhibits ... and AC" but "AC" is not defined in the global exhibit legend. Court may disregard unsupported references or treat packet as internally inconsistent.
- Source:
  - `03A_motion_to_show_cause...`: line 83.
- Deontic gap:
  - O: exhibit labels must be globally consistent and defined.
  - F: filing undefined exhibit labels in operative motions.

3. Fallback motion still uses internal ID-style citations instead of court-facing references
- Risk: `152_fallback_motion...` still cites sources as `(139, 149, 169)` and `(04, 151, 157)`, which reads like internal indexing rather than admissible exhibit/declaration citation format.
- Source:
  - `152_fallback_motion_to_exclude...`: lines 33-34.
- Deontic gap:
  - O: dispositive/scope arguments should cite named pleadings/exhibits directly.
  - Current state: internal shorthand remains in filed-facing text.

4. Long-form declaration remains overinclusive and internally scoped as non-primary evidence
- Risk: `04_declaration...` includes broad narrative material and itself asks the Court to treat it as context, not the primary evidentiary vehicle. If filed as principal support, opponent can attack relevance/foundation and internal inconsistency with the court-safe declaration strategy.
- Sources:
  - Internal limitation language: lines 105-109.
  - Non-core narrative branches (dog/transport/research background): lines 50-68.
  - Internal-style repository/source wording in operative fact sections: lines 28, 39, 57-61, 83-88.
- Deontic gap:
  - O: declarations supporting threshold relief should be tightly element-linked.
  - P: keep long-form narrative as background appendix only.

## Medium Severity

5. Supplemental Google Voice declaration contains raw local filesystem paths
- Risk: Court-facing declaration includes absolute local paths in body text, which is unnecessary and invites format objections.
- Source:
  - `117_supplemental_declaration_authenticating_google_voice_sms_service_chain_final.md`: lines 21-36.
- Deontic gap:
  - O: authenticate records by exhibit identifier and custodian statement, not workstation path strings.

6. Bench memorandum still exposes internal workflow framing (`188` row IDs/backticks)
- Risk: Memo language remains partly implementation-oriented (`188` row tracking), which can read as internal workflow rather than neutral adjudicative presentation.
- Source:
  - `86_short_bench_memo...`: lines 18-19, 49-58.
- Deontic gap:
  - O: bench memo should present legal test and evidentiary status in court-facing terms first, tracker terms second.

7. Residual wording artifact in objection motion
- Risk: "current staged record" remains in `152_objection...`, which is weaker style than the now-standard "current filed/lodged record" phrasing.
- Source:
  - `152_objection_to_first_amended_guardianship_petition...`: line 51.
- Deontic gap:
  - O: maintain consistent court-facing language across related motions.

8. GAL motion relies heavily on general Chapter 125 management authority without a sharper appointment-specific anchor
- Risk: Opponent can argue requested GAL appointment authority is too generally framed and insufficiently tied to explicit appointment mechanism.
- Source:
  - `01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md`: lines 36-42.
- Deontic gap:
  - O: provide direct authority-to-relief bridge for appointment standard, not only broad case-management authority.

## Low Severity

9. Internal-style backtick formatting persists in some filed-facing pleadings
- Risk: Not usually dispositive, but can reduce professionalism/readability.
- Examples:
  - `01_motion_for_appointment...`: lines 26, 57.
  - `08_proposed_order_dismiss...`: lines 17-19, 27.
  - `152_objection...`: lines 26, 61, 65, 79, 83.

## Deontic Summary (Cross-Document)

1. Obligations that are mostly satisfied
- O: keep dispositive preclusion conditional on certified proof (strongly present in `02`, `08`, `86`).
- O: separate non-subpoena sanctions from immediate compel relief (present in `24`, `88`, `88A`, `09`).

2. Obligations not yet fully satisfied
- O: one-to-one exhibit mapping for each show-cause factual allegation (currently broken by Exhibit 7/AC inconsistencies).
- O: court-facing citations in all fallback/companion motions (broken in `152_fallback`).
- O: keep primary evidentiary declarations narrow and element-driven (risk if `04` is treated as primary filing declaration).

3. Prohibitions to maintain
- F: do not file templates/prefills with unresolved placeholders.
- F: do not seek sanctions findings on writ-branch allegations without the separately noticed sanctions vehicle already preserved in motion text.

## Priority Fix Order

1. Repair exhibit map consistency first (Exhibit 7/AC issue in `03`/`03A` + legend alignment).
2. Convert `152_fallback` internal numeric source cites to court-facing citation style.
3. Keep `177` as primary threshold declaration and quarantine `04` to context/background use only (or trim `04`).
4. Normalize `117` authentication declaration to exhibit labels instead of local path references.
5. Final style pass on residual "staged record" and backtick artifacts in filed-facing motions.
