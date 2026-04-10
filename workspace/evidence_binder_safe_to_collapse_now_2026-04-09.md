# Evidence Binder Safe To Collapse Now

Use this note as the conservative deduplication list for the current lean binder.

It is based on:

- [evidence_binder_duplicate_analysis_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_duplicate_analysis_2026-04-09.md)
- [evidence_binder_page_embedding_analysis_lean_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_page_embedding_analysis_lean_2026-04-09.md)
- [evidence_binder_deduplication_plan_2026-04-09.md](/home/barberb/HACC/workspace/evidence_binder_deduplication_plan_2026-04-09.md)

## Safe To Collapse Now

### 1. `JC Household` chain

Keep as master:

1. `Shared Housing / State-Court Binder - Exhibit V`

Collapse by reference:

1. `Shared Housing / State-Court Binder - Exhibit X`
2. `Shared Housing / State-Court Binder - Exhibit AA`
3. `Shared Motion / Probate / Sanctions Binder - Exhibit W`

Reason:

- exact same source file reuse;
- already implemented in the current lean build.

### 2. Waterleaf application artifact

Keep as master:

1. `Shared Housing / State-Court Binder - Exhibit W`

Collapse by reference:

1. `Supplemental Background Appendix - Exhibit B-1`

Reason:

- exact same source/image reuse;
- already implemented in the current lean build.

### 3. Shared motion / probate `Exhibit C` and `Exhibit D`

Keep as master:

1. `Shared Motion / Probate / Sanctions Binder - Exhibit C`

Collapse by reference:

1. `Shared Motion / Probate / Sanctions Binder - Exhibit D`

Reason:

- exact same source EML;
- exact duplicate text page in the page-level embedding run;
- different propositions can still be tracked on the cover page.
- implemented in the lean build after rebuild.

## Review Before Collapsing

### 1. `Shared Housing / State-Court Binder - Exhibit T`

Decision after review:

1. keep `Exhibit T` as a separate printed source.

Why:

- it is part of the same thread family as `Exhibit V`, but not the same message;
- it has a different `Message-ID`;
- it has a different `To` line, including `blossom@quantumres.com`;
- it adds materially different body text, including the later Balfour Park / tort-claim / race-discrimination complaint content.

### 2. `Shared Housing / State-Court Binder - Exhibit C` and `Exhibit D`

Decision after review:

1. keep both as separate printed exhibits.

Why:

- they are different source PDFs;
- they differ in title, length, and body content;
- one is a three-page `30 Day Lease Termination Notice without Cause` file;
- the other is a two-page `90 Day Lease Termination Notice without Cause` file with different HUD-disclosure language.

## Do Not Auto-Collapse From Embeddings Alone

Do not auto-collapse these without manual review:

1. repeated internal pages inside `Shared Housing / State-Court Binder - Exhibit Z`
2. visually similar Google Maps / appendix pages in the supplemental background appendix
3. placeholder or source-note pages that match only because the generated layout is similar

Reason:

- those hits are often template or packet-repetition artifacts, not necessarily binder-level duplicate exhibits.

Administrative Plan note:

1. `Exhibit Z` should be carried as the prepared excerpt file, not the full Administrative Plan text dump.
2. The full Administrative Plan dump should remain repository-side source support and be cited by reference when needed.

## Best Practical Next Move

If you want the next safe cleanup step:

1. collapse `Shared Motion / Probate / Sanctions Binder - Exhibit D` by reference to `Exhibit C`;
2. keep `Exhibit T` separate from `Exhibit V`;
3. keep housing `Exhibit C` and `Exhibit D` notices as separate exhibits;
4. leave the rest of the embedding-only hits as review targets, not automatic removals.
