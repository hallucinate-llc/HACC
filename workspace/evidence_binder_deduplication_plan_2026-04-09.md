# Evidence Binder Deduplication Plan

Use this note to reduce unnecessary physical duplication in the printed binder while keeping the proposition-level record clear.

## Governing Rule

If the same underlying source file is being printed more than once, prefer one of these approaches:

1. keep one full printed copy as the `master exhibit`;
2. let the other exhibit cover pages remain, but replace the repeated exhibit body with a short `reference note`;
3. or keep both only if the second copy is genuinely needed in a separate binder family for courtroom handling.

For the current binder system, the default `master exhibit` volume should be the `Shared Housing / State-Court Binder` whenever the repeated source is already part of that housing/state-court common volume.

See:

- [state_housing_state_court_binder_incorporation_note_2026-04-09.md](/home/barberb/HACC/workspace/state_housing_state_court_binder_incorporation_note_2026-04-09.md)
- [filing_specific_exhibit_schedule.md](/home/barberb/HACC/workspace/filing_specific_exhibit_schedule.md)
- [evidence_binder_duplicate_analysis_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_duplicate_analysis_2026-04-09.md)
- [evidence_binder_page_embedding_analysis_lean_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_page_embedding_analysis_lean_2026-04-09.md)
- [evidence_binder_safe_to_collapse_now_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_safe_to_collapse_now_2026-04-09.md)

## 1. Strongest Current Duplication

### A. `JC Household` chain

Master source:

- [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)

Currently reused as:

- `Exhibit V` in the shared housing / state-court binder
- `Exhibit X` in the shared housing / state-court binder
- `Exhibit AA` in the shared housing / state-court binder
- `Exhibit W` in the shared motion / probate / sanctions binder

Recommended treatment:

1. Keep `Exhibit V` as the `master printed copy` in the housing binder.
2. Keep the `Exhibit X` and `Exhibit AA` tab cover page and exhibit cover page, but replace the repeated body with a one-page note saying:
   - `Source incorporated by reference from the Shared Housing / State-Court Binder, Exhibit V`
   - and identify the distinct proposition being drawn from that same thread.
3. In the motion / probate / sanctions binder, either:
   - keep `Exhibit W` as a separate printed copy only if you want that binder to stand alone; or
   - replace its repeated body with a cross-reference note to the state housing/state-court master binder if you are carrying the binders together.

Reason:

- the propositions are genuinely different;
- the underlying file is the same;
- this is the cleanest place to cut binder bulk.

## 2. Waterleaf Application Duplication

Underlying artifacts:

- [waterleaf_application.png](/home/barberb/HACC/evidence/history/waterleaf_application.png)
- [waterleaf_application.png](/home/barberb/HACC/evidence/paper%20documents/waterleaf_application.png)

Current uses:

- `Exhibit W` in the housing binder
- `Exhibit B-1` in the supplemental background appendix

Recommended treatment:

1. Keep `Exhibit W` as the `master printed copy` in the housing binder.
2. In the supplemental appendix, keep the `Exhibit B-1` tab cover page and exhibit cover page, but replace the repeated image body with:
   - `Source incorporated by reference from the Shared Housing / State-Court Binder, Exhibit W`
   - unless you want the supplemental appendix to be fully self-contained.

Reason:

- this is the same basic artifact being used for two overlapping propositions;
- the housing binder is the stronger place to keep the full printed copy.

## 3. Repeated Exhibit Letters That Are Not True Duplicates

These can stay as-is because the sources differ:

- `Exhibit B`
  - housing: redevelopment materials
  - motion/probate: order digest
- `Exhibit C`
  - housing: December notice material
  - motion/probate: Solomon text
- `Exhibit D`
  - housing: December notice material
  - motion/probate: Solomon text
- `Exhibit E`
  - housing: December notice material
  - motion/probate: Google Voice message
- `Exhibit G`
  - housing: January 8 HACC notice
  - motion/probate: March 10 Solomon text
- `Exhibit H`
  - housing: HACC housing-history document
  - motion/probate: March 10 Solomon text
- `Exhibit X`
  - housing: Waterleaf / port-out sequence
  - motion/probate: Julio termination notice
- `Exhibit AA`
  - housing: March 26 HACC three-option email
  - motion/probate: federal-track proffer note

These are labeling overlaps, not true exhibit-body duplication.

## 4. Additional Duplicates Found By Semantic/OCR Review

The repository-wide duplicate pass also found these additional overlaps:

### A. Shared motion / probate `Exhibit C` and `Exhibit D`

Master source:

- [uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml](/home/barberb/HACC/workspace/solomon-sms-eml-2026-04-04/uid_660753_Mon--17-Nov-2025-22-59-36--0000_New-text-message-from-solomon--503--381-6911.eml)

Current uses:

- `Exhibit C` in the shared motion / probate / sanctions binder
- `Exhibit D` in the shared motion / probate / sanctions binder

Recommended treatment:

1. Keep one full printed copy as the master source inside that binder family.
2. Keep the second exhibit's tab cover page and exhibit cover page.
3. Replace the second repeated body with a one-page note saying the source is incorporated by reference from the master copy in the same binder.

Reason:

- this is a true same-source duplicate;
- the propositions differ slightly, but the underlying file does not.

### B. Secondary-housing `Exhibit T` is likely a same-thread variant of the `JC Household` chain

Likely related sources:

- [message.eml](/home/barberb/HACC/evidence/email_imports/starworks5-fraud-reimport-20260404/0047-Re-Allegations-of-Fraud---JC-Household-CAMTdTS-00cFTv4dFf8yZ3NpPztCKwr2LB-on4Xxz-BFEv9_5jA-mail.gmail.com/message.eml)
- [message.eml](/home/barberb/HACC/workspace/manual-imap-download-2026-03-31/20260202-164227_Re-Allegations-of-Fraud---JC-Household/message.eml)

Recommended treatment:

1. Keep `Exhibit T` as a separate printed source.
2. Do not collapse it into the `Exhibit V` by-reference structure.

Reason:

- the semantic/OCR pass correctly flagged it as the same thread family;
- but manual review shows it is a later separate message, with a different `Message-ID`, different recipients, and materially different added complaint text.

## 5. Recommended Lean Binder Mode

If the goal is the leanest printed binder:

1. print only one full copy of the `JC Household` chain;
2. print only one full copy of the Waterleaf application artifact;
3. keep all corresponding tab cover pages and exhibit cover pages;
4. use one-page cross-reference sheets in place of repeated exhibit bodies; and
5. expressly state that the repeated source is incorporated by reference from the `Shared Housing / State-Court Binder`.

## 6. Recommended Full Standalone Mode

If the goal is for each binder family to stand alone without any dependency on another binder:

1. keep the current separate printed copies;
2. accept the duplication as intentional;
3. rely on the exhibit cover pages to explain the different proposition each repeated source supports.

## 7. Best Practical Recommendation

For court carry:

1. use `Lean Binder Mode` for the `JC Household` chain and Waterleaf application;
2. treat the `Shared Housing / State-Court Binder` as the master incorporated volume;
3. also collapse the duplicated Solomon SMS pair within the shared motion / probate / sanctions binder;
4. keep `Exhibit T` as a separate same-thread complaint exhibit;
5. keep housing `Exhibit C` and `Exhibit D` as separate notice exhibits;
6. do not spend time deduplicating the repeated exhibit letters that point to different source files.
