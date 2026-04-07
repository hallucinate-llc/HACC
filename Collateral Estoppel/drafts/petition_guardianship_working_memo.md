# Petition for Guardianship Working Memo

## Purpose

This memo is a working intake document for a guardianship petition and related motion practice involving Jane Cortez. It is not yet a court-ready filing. It is a staging memo that separates:
- known source leads
- allegations needing proof
- legal theories that may be available if the underlying documents support them

## Core Working Narrative

Current working theory to evaluate:
- Solomon is applying for guardianship.
- There may already be a guardianship or related appointment involving Jane Cortez and Benjamin Barber.
- There may be a prior enforceable order that another actor tried to avoid by avoiding service or pretending the order was not enforceable.
- There may be a sanctions theory tied to interference with a housing contract or housing-placement process.

Each of those points needs documentary confirmation before being stated as fact in a filing.

## Source Leads Already Located

- `evidence/history/Solomon Motion for Guardianship.pdf`
  Current status: scanned PDF, OCR completed into `Collateral Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt`.
- Prior HACC relational and deontic work in:
  - `Breach of Contract/outputs/`
  - `Breach of Contract/formal_logic/title18_temporal_deontic_logic.py`
  - `Invasion of Privacy Memorandum/chat_extract.md`

## Verified From Existing Repo Context

The broader HACC workspace already reflects these contextual points:
- Benjamin Barber and Jane Cortez appear together in multiple HACC housing and accommodation materials.
- Prior graph artifacts already model HACC, Jane Cortez, and Benjamin Barber as linked actors.
- Prior deontic work formalized obligations, permissions, and prohibitions around housing and accommodation processes.

These points help structure the case graph, but they do not by themselves establish guardianship facts.

## Claims Ledger

### Provisionally supported by folder-level source leads

- A Clackamas County guardianship filing exists for Jane Kay Cortez under case number `26PR00641`.
- The filing is styled as a first amended petition seeking temporary and indefinite guardianship, waiver of notice, and a writ of assistance.
- Solomon Barber is identified in the filing as petitioner and as Jane Cortez's son.
- The filing contains allegations against Benjamin Barber relating to housing, access, and interference.
- The packet includes a notice to respondent and an apparent respondent objection form.
- The repo contains prior formal-logic and knowledge-graph work involving Jane Cortez, Benjamin Barber, and HACC.

### Alleged and still needs proof

- That a guardianship has already been appointed to Jane Cortez as to Benjamin Barber or through Benjamin Barber.
- That Solomon had notice of a prior order and intentionally avoided service.
- That a prior order was enforceable at the relevant time.
- That interference occurred with a specific housing contract, application, relocation path, or placement process.
- That sanctions are available against a specific person in the relevant court for that interference.

### Tension requiring immediate verification

- The OCR text of Solomon's petition states that no guardian had previously been appointed for Jane Cortez.
- That directly conflicts with the current theory that a guardianship may already have been appointed.
- Before building a collateral-estoppel or sanctions filing around an existing appointment, we need the actual earlier order if one exists.

## Documents To Pull Next

- any prior guardianship appointment order
- register of actions or docket for case `26PR00641`
- any signed temporary or indefinite guardianship order in `26PR00641`
- letters of guardianship or conservatorship, if any
- proof of service or attempted service records
- docket sheet and case number for the guardianship matter
- housing contract, lease, voucher paperwork, relocation paperwork, or application packet allegedly interfered with
- emails, texts, notices, or declarations showing notice, avoidance, interference, or noncompliance

## Drafting Notes

Before a court-ready petition or response is prepared, we should pin down:
- exact court and case caption
- who is the petitioner, respondent, protected person, guardian, and any existing fiduciary
- whether the prior appointment was temporary, permanent, limited, or expired
- whether the housing-contract issue belongs in the guardianship case, a contempt motion, a separate civil case, or a declaration attached as context

## Candidate Issues To Research Further

- collateral estoppel / issue preclusion if a prior guardianship issue was actually litigated and decided
- claim preclusion if the same core dispute was already reduced to judgment
- contempt or sanctions if a party violated an enforceable order after notice
- evidentiary linkage between guardianship authority and housing-contract interference

## Repeated Usurpation Theory

One theory now emerging across this folder is a repeated usurpation pattern.

Working formulation:
- an authority status or protective order is granted;
- the affected actor has notice of it or behaves as though he knows of it;
- instead of seeking formal modification or relief through the court, the actor continues through collateral channels;
- those collateral acts are then used to shape authority, control, housing, or access outcomes.

Applied here, that pattern currently appears in two related ways:

### Guardianship-side version

- If an earlier guardian ad litem, guardianship, or comparable authority order existed involving Jane Cortez and Benjamin Barber, then a later filing by Solomon that attempts to relitigate or bypass that authority may support a collateral-estoppel or issue-preclusion theory.
- That proposition remains conditional because the present OCR petition in `26PR00641` says no prior guardian had been appointed, so the earlier authority order must be located before this can become a filing-grade factual assertion.

### Housing-side version

- The Solomon restraining-order record strongly supports that Solomon had notice of the order and later treated service / enforceability as something he could define for himself.
- The March 23 inspection declarations support that Charley Skee later explained Benjamin's lease removal in substance by reference to outside document flows from Benjamin's brother and stepfather.
- The present theory is therefore that outside influence may have continued through collateral housing communications despite the restraining-order framework.

### Safe current pleading form

The safest current formulation is:

- `On information and belief, the same usurpation pattern repeated across the guardianship and housing contexts: once legal authority or protective boundaries were in place, Solomon continued seeking practical control through collateral channels rather than by obtaining formal court relief.`

This is safer than the stronger assertion:

- `The current record already fully proves that Solomon used collateral estoppel to defeat prior guardianship authority and also personally carried out prohibited collateral housing conversations with HACC.`

The current folder does not yet fully prove that broader statement directly.

## Best Current Argument Section For Later Filing

If the proof gates are later satisfied, the argument can be framed this way:

1. The Court had already created or recognized a legal authority structure protecting Jane Cortez or allocating authority over her affairs.
2. Solomon had notice of the relevant order or proceedings.
3. Rather than comply or seek orderly relief, Solomon attempted to work around that structure through collateral action.
4. The same workaround pattern also appears in the housing record, where outside document flows and restrained-party communications allegedly influenced HACC lease or relocation handling.
5. That repeated pattern matters because it tends to show not mistake, but purposeful bypass of court-created authority boundaries.

Until the missing proof is obtained, this section should be used as theory-development language only.

## Stage 1 Artifacts Added In This Folder

- `drafts/petition_guardianship_packet_stage1.md` for filing-structure blocks, exhibit gates, and allegation-safe language.
- `drafts/petition_guardianship_court_ready_shell.md` for a court-format shell with conditional findings and conflict-disclosure language.
- `drafts/sanctions_motion_shell_conflict_aware.md` for sanctions drafting that preserves unresolved actor conflicts.
- `drafts/stage1_fill_instructions.md` for immediate conversion steps to filing-ready drafts.
- `knowledge_graph/guardianship_case_graph.json` updated to include client-asserted allegations and explicit proof-target nodes.
- `knowledge_graph/deontic_theorem_workbook.md` for theorem-level mapping of obligations, permissions, prohibitions, and sanctions pathways.
- `knowledge_graph/generate_formal_reasoning_artifacts.py` to compute formal artifacts from one shared fact/rule model.
- `knowledge_graph/generated/` outputs for full knowledge graph, dependency graph, F-logic program, temporal deontic FOL program, deontic cognitive event-calculus program, and computed deontic state report.
- `evidence_notes/allegation_proof_matrix.md` for claim-by-claim proof tracking.
