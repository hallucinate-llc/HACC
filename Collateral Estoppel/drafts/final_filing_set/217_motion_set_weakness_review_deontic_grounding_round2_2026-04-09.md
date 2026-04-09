IN THE CIRCUIT COURT OF THE STATE OF OREGON
FOR THE COUNTY OF CLACKAMAS
PROBATE DEPARTMENT

Case No. 26PR00641

In the Matter of:
Jane Kay Cortez,
Protected Person.

MOTION/DECLARATION/MEMORANDUM WEAKNESS REVIEW (ROUND 2)
RE: LAW/FACT GROUNDING + DEONTIC TRACKING

Date: 2026-04-09
Scope reviewed: 01, 02, 03, 23, 24, 86, 151, 152, 157, 168, 172, 183.

Severity scale:
1. High = likely attack point affecting admissibility/credibility or requested relief.
2. Medium = materially improvable grounding/scope precision issue.
3. Low = cleanup/readiness issue that should be corrected before filing.

I. HIGH-SEVERITY FINDINGS

1. Court-facing filing still contains markdown hyperlink syntax and an absolute filesystem path.
   a. Location: `152_objection_to_first_amended_guardianship_petition_and_emergency_relief_final.md` paragraph 10 source-anchor sentence (line 38 in current draft).
   b. Risk: appears non-pleading/non-court format and can undercut seriousness/reliability of the filing packet.
   c. Deontic:
      1) O (obligation): convert all court-filed references to pleading-style text citations (Exhibit/Declaration paragraph cites) without local file paths.
      2) F (prohibition): do not file with local path links or markdown artifacts.

2. `24` compel motion remains template state with unresolved `[INSERT]` fields and a recipient placeholder.
   a. Location: `24_motion_to_compel_subpoena_compliance_and_sanctions_final.md` lines 18-23 and 68.
   b. Risk: filing an unfilled motion can trigger immediate credibility and procedural defects.
   c. Deontic:
      1) O: complete service chronology and due-date fields from service tracker before filing.
      2) F: do not file this form until all placeholders are replaced and recipient-specific facts match the attached declaration/service proof.

3. Dispositive preclusion branch remains proof-gated (still correctly conditioned, but evidentiary gap persists).
   a. Location: `02_motion_to_dismiss_for_collateral_estoppel_final.md` paragraphs 15, 21, 66-72.
   b. Risk: dismissal request remains vulnerable if certified finality/identity/privity/opportunity support is not lodged row-by-row.
   c. Deontic:
      1) O: keep dismissal branch conditional and row-specific under `188`.
      2) F: no final estoppel finding request without fully supported row(s).

II. MEDIUM-SEVERITY FINDINGS

4. Bench memorandum uses markdown heading format in a court-facing document.
   a. Location: `86_short_bench_memo_supplemental_exhibits_8_9_10_and_threshold_issue_preclusion_2026-04-07.md` lines 15, 21, 32, etc.
   b. Risk: stylistic mismatch with court memo format; can look internal rather than filing-ready.
   c. Deontic:
      1) O: convert to plain pleading section headers for filing copy.

5. Cross-reference style mixes internal file IDs and narrative citations, creating readability friction.
   a. Location: 01/02/03/151/152/157 (multiple paragraphs citing `177`, `169`, `148`, etc. by numeric file ID).
   b. Risk: judge/opposing counsel may not know internal numbering unless docket-exhibit map is simultaneously crystal-clear.
   c. Deontic:
      1) O: ensure every numeric file-id cite corresponds to a clearly labeled exhibit in the filed index.
      2) P (permission): retain numeric shorthand only if exhibit legend/crosswalk is filed and attached.

6. Show-cause filing uses broad wording about writ conduct that may be construed as sanction-seeking beyond ORS 33 branch unless tightly sequenced.
   a. Location: `03_motion_to_show_cause_re_solomon_failure_to_appear_and_barred_claim_final.md` paragraphs 22, 40-42, 59.
   b. Risk: opponent can argue the motion blends contempt, writ-validity challenge, and filer-misconduct sanctions in one paper.
   c. Deontic:
      1) O: keep explicit sequence: show-cause facts first, contempt elements second, any non-ORS 33 sanctions only via separate noticed briefing (already partially present at paragraph 25A).

7. ORCP 27 pathway in GAL motion remains hedge-based and may need one cleaner statutory anchor for appointment authority in this probate posture.
   a. Location: `01_motion_for_appointment_and_appearance_of_guardian_ad_litem_final.md` paragraphs 18-27.
   b. Risk: opposing side can characterize ORCP 27 branch as overcomplicated or inapplicable if not tied to a clear Chapter 125 appointment-management basis.
   c. Deontic:
      1) O: keep Chapter 125 branch primary and reduce ORCP 27 dependency language in oral argument.

III. LOW-SEVERITY FINDINGS

8. Some filings still use internal workflow phrases that are stronger as attorney work-product than court text.
   a. Example phrases: "repository", "staged record", "organizational aid".
   b. Locations: multiple, including 03/151/152/157/168/172.
   c. Risk: minor style/credibility drag, not usually dispositive.
   d. Deontic:
      1) P: keep in internal dashboards.
      2) O: in filing copy, prefer "current record" + specific exhibit/declaration cites.

9. Declaration 23 is intentionally blank-template, but should never travel alone without recipient-specific completion.
   a. Location: `23_declaration_re_subpoena_noncompliance_final.md` lines 17-38 and date/signature fields.
   b. Risk: accidental filing of unfilled declaration.
   c. Deontic:
      1) F: do not file unfilled declaration template.

IV. DEONTIC CLOSURE CHECK (ROUND 2)

1. OBLIGATIONS (O):
   a. Replace non-court markdown/path artifacts in filing copies.
   b. Keep dispositive preclusion row-gated to admissible certified support.
   c. Maintain separate-briefing guard for any non-subpoena sanctions theories.
   d. Ensure exhibit-number citations are intelligible without internal repo context.

2. PROHIBITIONS (F):
   a. Do not file placeholder templates (`[INSERT]`, blanks) as operative motions/declarations.
   b. Do not seek final estoppel findings on uncertified/unsupported rows.
   c. Do not let writ-misconduct allegations outpace the selected sanction vehicle and notice sequence.

3. PERMISSIONS (P):
   a. Threshold narrowing and scope-control relief remains fully supportable now.
   b. Conditional prior-GAL continuity argument remains permissible as context pending certification.

V. PRACTICAL NEXT CURE SET (HIGHEST VALUE)

1. Produce a "court-safe formatting pass" for 86 and 152 (remove markdown artifacts and internal-path text).
2. Lock `24`/`23` to recipient-specific completed variants before any filing event.
3. Keep `02` dismissal prayer conditional unless at least one `188` row is fully closed with admissible support.
4. For hearing, use `183` crosswalk as oral script and state status first: `Admissible-now` vs `Proof-gated`.

Prepared by:
____________________________________
Benjamin Barber, Pro Se (working audit memo)
