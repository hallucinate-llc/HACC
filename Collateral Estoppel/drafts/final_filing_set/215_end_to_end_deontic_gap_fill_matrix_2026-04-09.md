## End-to-End Deontic Gap-Fill Matrix (2026-04-09)

Purpose: close remaining legal/factual gaps by mapping each live rule branch to admissible evidence status and concrete next retrieval action.

### Status keys
- `Admissible-now`: currently supportable by filed/staged exhibit record.
- `Proof-gated`: requires certified/official record before dispositive use.
- `Context-only`: usable only for scope management, not merits findings.

| Rule ID | Actor | Modality | Trigger | Required Proof | Current Evidence | Status | Gap | Next Action |
|---|---|---|---|---|---|---|---|---|
| R-GAL-01 (appointment sub-branch) | Court | `P` appoint GAL | Material conflict on protective facts | Motion + declarations showing conflict/need | `01`, `04`, `177`, Exhibit 2 | Admissible-now | None for threshold appointment ask | Keep request narrow to investigation/reporting |
| R-GAL-01 (continuity sub-branch) | Court | `P/O` align prior GAL continuity if confirmed | Certified prior case shows same protected person + prior GAL role | Certified order/docket from `25PO11530` | Exhibit 1 sequence + narrative references | Proof-gated | Certified continuity proof not lodged | Obtain/lodge certified `25PO11530` order+docket pages |
| R-PI-01 | Court | `F` relitigate identical finalized issue | Identity + finality + privity + full/fair opportunity | Certified prior proceeding packet | `02`, `188`, overlap trackers | Proof-gated | Finality/identity packets incomplete | Lodge certified `26FE0586` and federal docket status records |
| R-JN-01 | Court | `O` narrow collateral housing merits | Housing merits are collateral to guardianship function | Petition text + overlap declarations | `02`, `151`, `152`, `157` | Admissible-now | None for narrowing-only ask | Maintain threshold scope framing |
| R-SC-01 | Solomon Barber | `O` comply with operative order terms | Entry/effect of order + notice/appearance language | Signed order text and linked proof | Exhibit 1/1A; `03`; declarations | Admissible-now (threshold) | Violation merits still factual | Proceed via show-cause hearing, not punitive shortcut |
| R-SC-01 (remedial branch) | Movant/Court | `P` seek remedial contempt branch | Proven violation of specific term | Admissible violation evidence | `03`, `04`, `177` + comms | Proof-gated (sanctions phase) | Court finding not yet made | Ask for appearance/explanation first, remedial only if proven |
| R-SC-02 (appearance-enforcement sub-branch) | Court | `P` compel appearance escalation | Served order to appear + nonappearance | Served OSC + nonappearance minute entry | none yet in this branch | Proof-gated | OSC service + nonappearance record absent | File OSC first; if violated, lodge service + minute entry |
| R-SVC-01 | Solomon/Counsel track | `O` respond after effective notice pathway | Effective order language + notice chain | Order text + text/email transmission + service return | Exhibit 1/1A, comms threads, reported sheriff event | Context-only to Admissible-now mix | Official sheriff return not yet lodged | Lodge sheriff return immediately on receipt |
| R-JN-01 (29B factor sub-branch) | Court | `O` evaluate fallback factors if joinder infeasible | Nonfeasible joinder posture | Prejudice/adequacy/remedy analysis on record | `151`, `156`, `161`, `166` | Admissible-now (argument) | Service feasibility facts could be tighter | Add short supplemental declaration of service channels/timeline |
| R-JN-02 (22C derivative-liability sub-branch) | Defending party | `O` plead derivative liability for third-party claim | Third-party claim attempted | Liability-over pleading facts | `151`, `156` analysis | Admissible-now (negative fit) | No liability-over facts identified | Keep ORCP 22C as non-primary branch unless facts emerge |

### Highest-priority evidence pulls
1. Certified `25PO11530` docket/order pages showing any GAL-role continuity language.
2. Official sheriff return/proof for April 9, 2026 service event.
3. Clackamas Justice Court `26FE0586` certified docket/order packet (identity/finality elements).
4. District of Oregon docket sheet and filed-stamped entries for the HACC/Quantum track.
5. Any minute entry or audio-backed record that can verify appearance/nonappearance events tied to show-cause sequencing.

### Filing-discipline gates
1. Keep dispositive estoppel relief conditional until `R-PI-01` is promoted from `Proof-gated` to `Admissible-now`.
2. Keep prior-GAL continuity as context unless `R-GAL-01 (continuity sub-branch)` certified proof is lodged.
3. Keep contempt relief strictly remedial and sequential (`appearance -> proof -> remedy`) unless statutory predicates are fully documented.
4. Do not file placeholder certificates or declarations with bracketed fields.
