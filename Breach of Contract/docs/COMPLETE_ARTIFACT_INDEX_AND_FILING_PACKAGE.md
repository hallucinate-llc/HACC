# Complete Joinder Case Artifact Index & Filing Package

**Case:** HACC v. Barber/Cortez (Eviction Action, Clackamas County Circuit Court)  
**Motion:** Motion for Joinder of Quantum Residential Property Management  
**Status:** Ready for Filing (April 5, 2026)  
**Case ID:** [TO BE INSERTED: ____________]  

---

## ARTIFACT ORGANIZATION GUIDE

All artifacts are organized in two directories:

1. **`outputs/`** — Ready-to-file motion + advocacy documents (court/hearing materials)
2. **`docs/`** — Litigation strategy guides + detailed roadmaps

---

## SECTION I: COURT-FILING ARTIFACTS (IN `outputs/`)

### Category A: Motion & Supporting Memorandum

#### 1. **joinder_quantum_001_motion_for_joinder.md** (6.4 KB)
**Purpose:** Court pleading requesting joinder of Quantum Residential  
**Format:** Plain-text markdown; customizable for court filing  
**Customization Required:**
- [CASE NUMBER]
- [JUDGE NAME] 
- [YOUR BAR REGISTRATION]
- [HEARING DATE]
- [HACC COUNSEL NAME]
- [QUANTUM RESIDENTIAL REGISTERED AGENT ADDRESS]

**How to Use:**
1. Open file
2. Replace all [BRACKETED] placeholders with actual case details
3. Convert to PDF or Word document for filing
4. Sign (or obtain signature from counsel of record)
5. File with court clerk (include proof of service)

**Key Sections:**
- Caption (plaintiff, defendant, case number)
- Numbered arguments (joinder proper under ORCP 29A, facts showing need, complete relief impossible without joinder)
- Prayer for relief
- Signature block

**Court Rule Reference:** ORCP 29A (Compulsory Joinder)

---

#### 2. **joinder_quantum_001_memorandum.md** (6.4 KB)
**Purpose:** Detailed legal argument supporting motion  
**Format:** Plain-text markdown; customizable for court filing  
**Structure:**
- INTRODUCTION (1 page: case background, joinder standard)
- STATEMENT OF FACTS (3 pages: RAD conversion, intake obstruction, Section 18 non-compliance)
- LEGAL ARGUMENT (5 pages):
  - Point 1: Joinder is Mandatory under ORCP 29A
  - Point 2: Quantum's Interest is Jeopardized
  - Point 3: RAD Successor Obligations Bind Quantum
  - Point 4: Complete Relief Impossible Without Joinder
- CONCLUSION (requesting joinder)

**How to Use:**
1. Convert to PDF/Word for filing
2. Customize case number, judge name, dates
3. Ensure all footnote citations match actual authorities
4. File with motion + exhibits

**Exhibits Referenced:** A (Admin Plan), K (Phase II notice), L (Ferron email)

**Length:** ~2000 words (typical for court motion)

---

#### 3. **joinder_quantum_001_motion_for_joinder.json** (7 KB)
**Purpose:** Structured JSON version of motion (for software/database use)  
**Format:** Nested JSON with motion structure  
**Contains:** All text + metadata (author, date, status, version)  
**How to Use:**
- If you're integrating motion into litigation management software
- If you want to track versions/changes programmatically
- Reference copy; print the .md version for actual filing

---

#### 4. **joinder_quantum_001_memorandum.json** (20 KB)
**Purpose:** Structured JSON version of memorandum  
**Format:** Nested JSON with sections, arguments, citations  
**Contains:** All text + metadata  
**How to Use:**
- Parallel to motion.json (for integration scenarios)
- Reference; use .md version for actual filing

---

### Category B: Advocacy Hearing Materials

#### 5. **joinder_quantum_001_hearing_script.md** (1.5 KB)
**Purpose:** Verbatim speaking notes for oral argument before judge  
**Format:** Plain-text markdown; designed for speaker reference  
**Contains:**
- Opening statement (2 min)
- 4 Key points (one per 3-4 minutes):
  1. Joinder is proper under ORCP 29A (3 elements)
  2. Facts show Quantum obstruction (Ferron email proves receipt)
  3. Quantum is RAD successor bound by PIH 2019-23
  4. Complete relief impossible without Quantum bound by judgment
- Closing argument (1-2 min)

**How to Use:**
1. Print + highlight key phrases
2. Practice aloud 2-3 times (timing: 30-40 min total including judge interactions)
3. Bring to courtroom; refer to during motion hearing
4. Gesture to Visual Exhibits (see **SECTION II: STRATEGY DOCUMENTS** below) as you speak

**Delivery Tips:**
- Maintain eye contact with judge (not memorized reading)
- Use Visual Exhibits as visual aids (refer judge to them by name)
- Pause after key facts to let judge absorb
- Tone: respectful, confident, matter-of-fact (not emotional)

---

### Category C: Dependency Graph (Machine-Readable Case Logic)

#### 6. **joinder_quantum_001_dependency_graph.json** (4.4 KB)
**Purpose:** Graph-structured representation of case logic  
**Format:** JSON (nodes + edges + metadata)  
**Contains:**
- 31 dependency nodes (e.g., "quantum_received_cortez_documents", "joinder_required", "section18_compliance_deficient")
- 36 directed edges (logical dependencies)
- Active outcome: "quantum_joinder_viable" (true)
- Confidence: 0.85

**Structure:**
```json
{
  "branch": "joinder_eviction_defense",
  "activeOutcome": "quantum_joinder_viable",
  "nodes": [...],
  "edges": [...]
}
```

**How to Use:**
- **For you (counsel):** Open in text editor; review node names and edges to ensure all key facts are captured
- **For visualization:** Import into graph visualization tool (e.g., Cytoscape, D3.js) to create poster for trial
- **For appeal:** Hand to appellate counsel as evidence of case theory (shows all dependencies if case is appealed)

**Key Nodes to Know:**
- `quantum_received_cortez_documents` → Proven by Ferron email
- `quantum_failed_to_transmit_to_hacc` → Proven by Ferron email + household testimony
- `hacc_quantum_contractual_relationship` → Proven by Admin Plan + RAD HAP contract
- `quantum_is_successor_in_interest` → Proven by Admin Plan + RAD conversion facts
- `section18_compliance_deficient` → Proven by HACC director testimony (4 preconditions missing)
- `joinder_required` → Logically follows from all above

---

#### 7. **joinder_quantum_001_dependency_citations.jsonld** (90 KB)
**Purpose:** Linked-data representation of case authorities + dependencies  
**Format:** JSON-LD (@context + @graph) for semantic web compatibility  
**Contains:**
- 232 nodes (authorities + dependency nodes + dependency relationships)
- Full citation text for all 11 authorities
- Mappings showing which authorities support which dependency nodes

**Structure:**
```json
{
  "@context": { ... },
  "@graph": [
    {
      "@id": "urn:uuid:...",
      "@type": "DependencySupport",
      "authority": "ORCP 29A",
      "supportedDependency": "joinder_required",
      ...
    },
    ...  (232 such nodes)
  ]
}
```

**How to Use:**
- **For you:** Validate that all 11 authorities are grounded to correct dependency nodes
- **For appellate brief:** Export quotes + citations for appeal
- **For judge (visual):** If court has linked-data visualization capability, can display interactive authority map on courthouse screen

**Authorities Included:**
1. ORCP 29A (joinder standard)
2. ORCP 22B (third-party practice—not primary, but cited for relationship context)
3. 42 USC 1437p Section 18 (HUD relocation preconditions)
4. 24 CFR 970.7 & 970.21 (PHA rules)
5. HUD Notice PIH 2019-23 (RAD successor obligations)
6. 24 CFR Part 8 (disability accommodations)
7. FHA 42 USC 3604 (fair housing)
8. *Giebeler* case law (joinder precedent)
9. ORS 105.135 (Oregon eviction defense)
10. HACC Administrative Plan (Exhibit 18-1 + chapters 17-18)
11. Household facts (from fixture)

---

### Category D: Advocacy & Hearing Materials

#### 8. **JOINDER_QUANTUM_ARTIFACTS_MANIFEST.md** (3 KB)
**Purpose:** Index of all outputs with descriptions + file sizes  
**Format:** Markdown table  
**Contains:**
- File name
- Purpose (one-liner)
- File size
- Format
- How to use
- Customization notes

**How to Use:**
- Reference when looking for a specific artifact
- Share with co-counsel to orient them to the package
- Confirm all 7+ files are present before filing

---

## SECTION II: LITIGATION STRATEGY DOCUMENTS (IN `docs/`)

### Category A: Court Filing & Hearing Strategy

#### 1. **COURT_FILING_SEQUENCE_JOINDER_QUANTUM.md** (2000+ lines)
**Purpose:** Comprehensive roadmap for filing phases + hearing strategy  
**Sections:**
- **Phase 1: Motion for Joinder Filing** (timing, local rules, service, exhibits checklist)
- **Phase 2: Affirmative Defenses** (if needed; joinder makes this easier)
- **Phase 3: Supporting Memoranda** (if court allows post-issue briefs)
- **Exhibit Strategy** (master list A–M, what each proves)
- **Timing & Court Rules** (pre-motion deadlines, motion hearing structure, post-joinder sequencing)
- **Evidence Management During Hearing** (exhibit presentation order, what to highlight)
- **Oral Argument Framework** (30-40 min, time allocations per point)
- **Post-Joinder Action Plan**:
  - If granted: amend complaint, serve Quantum, issue RFPs
  - If denied: preserve record, continue with defenses, prepare appeal
- **Compliance Checklist** (15 items: confirm local rules, flag exhibits, notarize, prepare visuals, schedule service, etc.)
- **Visual Exhibits for Hearing** (3 printable posters: Hillside Park timeline, intake failure timeline, Section 18 deficiency map w/ templates)

**How to Use:**
1. Read Phases 1-2 before filing motion (ensure all procedural boxes checked)
2. Print Exhibit Strategy section before hearing (organize physical exhibits in correct order)
3. Print Compliance Checklist; check off items as you complete them
4. Print Visual Exhibits section; use templates to create 3 posters (24"×36" minimum)

**Critical Deliverable:** This document is your operational guide through the motion hearing phase.

---

#### 2. **HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md** (3000+ lines)
**Purpose:** Speaking outline + visual exhibit templates for courtroom oral argument  
**Sections:**
- **Part I: Speaking Outline for Oral Argument** (verbatim text for 30-40 min hearing)
  - Opening (2-3 min)
  - Point 1: Joinder Mandatory (3-4 min) + 3 elements
  - Point 2: Quantum Obstruction (5-6 min) + timeline walkthrough  
  - Point 3: RAD Successor Status (3-4 min) + PIH 2019-23 explanation
  - Point 4: Complete Relief Impossible (2-3 min)
  - Closing (1-2 min)

- **Part II: Visual Exhibits for Courtroom Display** (3 printable posters)
  - Visual Exhibit 1: RAD Successor Chain (timeline format)
  - Visual Exhibit 2: Intake Obstruction Timeline (with email quotes + key points annotated)
  - Visual Exhibit 3: Section 18 & RAD Legal Structure (flowchart showing all 3 legal regimes)

- **Part III: Exhibit Handling During Hearing** (physical exhibits A, K, L, M + presentation sequence)
  - When to show each visual
  - What to highlight
  - How to hand judge individual exhibits

- **Part IV: Judicial Questions & Response Strategy** (5+ likely Q&A pairs)
  - Q1: "Why didn't household follow up after first denial?" → A1: [prepared answer]
  - Q2: "Is Quantum already a party?" → A2: [prepared answer]
  - Q3-5: (pre-answered defensive questions)

- **Part V: Courtroom Logistics** (pre-hearing checklist, testimony coordination, visual exhibit printing, etc.)

**How to Use:**
1. **Initial preparation (1 week before hearing):**
   - Read Part I aloud 2-3 times
   - Practice timing (should be 30-40 min for full argument)
   - Mark key transition points (where you'll pause for judge questions)

2. **Visual exhibit prep (2 weeks before hearing):**
   - Use Part II templates to create 3 posters
   - Print on 24"×36" poster board (or at least 18"×24")
   - Bring markers & highlighters to hearing (for in-real-time annotations if judge questions flow)

3. **Hearing day (morning of):**
   - Review Part IV (Q&A responses) one more time
   - Print Part III (exhibit handling guide) and bring a copy to courtroom
   - Bring all physical exhibits organized per Part III sequence

---

#### 3. **MASTER_ACTION_PLAN_JOINDER_THROUGH_RESOLUTION.md** (2000+ lines)
**Purpose:** Step-by-step roadmap from today (April 5) through trial/settlement and resolution  
**Phases:**
- **Phase 1: Pre-Motion Prep (Days 1-7)** — 8 steps (verify local rules, serve Ferron email on opposing counsel, locate Quantum, customize motion, obtain exhibits, etc.)
- **Phase 2: Motion Filing (Days 8-10)** — 3 steps (serve motion, file with court, prepare supporting affidavit)
- **Phase 3: Motion Hearing (Days 11-21)** — 5 steps (pre-hearing conference if needed, prepare courtroom materials, coordinate witnesses, final prep, actual hearing)
- **Phase 4: Post-Joinder Actions (Days 22-60)** — 4 steps (serve Quantum as defendant, issue RFPs, depose Ferron, depose Quantum, depose HACC director)
- **Phase 5: Summary Judgment (If Available, Days 90-120)** — decide if facts warrant motion for summary judgment
- **Phase 6: Trial Prep (Days 120-180)** — prepare exhibit notebook, prepare witnesses, draft trial brief + closing argument
- **Phase 7: Trial/Settlement (Days 180-210)** — either go to trial or accept settlement
- **Phase 8: Post-Judgment (Days 210+)** — enforce relocation remedies
- **Phase 9: Long-Term** — appeal if needed, document precedent

**For Each Phase:**
- Owner (who does the work)
- Due date
- Action (detailed steps)
- Deliverable (what you'll have when done)
- Key Questions (to answer before moving forward)

**Also Includes:**
- Success metrics (how to know you're winning)
- Timeline summary table (all 9 phases + deliverables)
- Contact checklist (who to call for each phase)
- Critical documents to keep in one trial-ready folder

**How to Use:**
1. **Week 1:** Complete Phase 1 steps; check off each as done
2. **Week 2:** Complete Phase 2 steps (motion filing)
3. **Week 3:** Complete Phase 3 steps (hearing prep + hearing)
4. **Weeks 4-8:** Complete Phase 4 steps (discovery + depositions)
5. **Weeks 9+:** Follow phases 5-9 based on case trajectory

**This is your master operational guide through judgment.**

---

### Category B: Discovery & Deposition Strategy

#### 4. **DEPOSITION_DISCOVERY_STRATEGY_QUANTUM_JOINDER.md** (1200+ lines)
**Purpose:** Detailed deposition targets, questions, RFP strategy, discovery roadmap  
**Sections:**

**A. Deposition Targets & Key Questions**
- **Deponent 1: Ashley Ferron (HACC Housing Resource Manager)**
  - 6 areas of questioning (29 specific Q&A pairs)
  - Focus: Intake process, Quantum's role, receipt/non-transmission, false denial, "separate from county" contradiction, Section 18 preconditions
  - Dependency nodes to lock in: hacc_quantum_contractual_relationship, quantum_received_cortez_documents, quantum_failed_to_transmit_to_hacc, section18_compliance_deficient

- **Deponent 2: Quantum Residential Manager**
  - 6 areas of questioning (24 specific Q&A pairs)
  - Focus: Intake receipt, non-transmission, false denial, property manager role, RAD obligations, portfolio-wide HACC relationship
  - Dependency nodes: quantum_received_cortez_documents, quantum_failed_to_transmit_to_hacc, quantum_is_successor_in_interest

- **Deponent 3: HACC Director or Finance Officer**
  - 4 areas of questioning (16 specific Q&A pairs)
  - Focus: Admin Plan accuracy, RAD successor chain, Section 18 relocation compliance, Quantum's intake role
  - Dependency nodes: hacc_admin_plan_rad_obligations, rad_conversion_closed_2021_01_01, section18_compliance_deficient

**B. Requests for Production (RFPs)**
- RFP 1-4 to Quantum (intake packets, RAD documents, relocation communications, intake procedures)
- RFP 5-7 to HACC (Admin Plan + RAD documents, household relocation records, Section 18 Phase II documentation)

**C. Interrogatories (Sample Format)**
- 4 specific questions to Quantum (receipt Y/N, forwarding Y/N, communications, RAD understanding)

**D. Subpoena Targets**
- Quantum: Business records (intake register, RAP contract, training materials)
- HACC: Administrative records (Admin Plan, HUD approval, relocation plan, consultation docs, board resolution)

**E. Dependency Graph Node Verification Checklist**
- Table mapping 8 key nodes to specific testimony/evidence needed to establish them

**F. Trial Preparation: Witness Use Matrix**
- How to use each deponent on direct/cross-examination
- Who will cross-examine whom
- What facts each deponent will establish

**G. Litigation Strategy Notes**
- "Ferron is the linchpin" (her email proves intake failure)
- "Admin Plan is the smoking gun" (Quantum's name is right there)
- "Quantum's false denial creates estoppel" (even if they claim misfiling)
- "Section 18 preconditions are missing on every front" (RFP will likely show no docs)

**How to Use:**
1. **Before first deposition:** Print Deponent 1 section (Ferron); review 29 Q&A pairs; highlight 8-10 critical questions
2. **Deposition day:** Bring printed questions; follow line-by-line; let court reporter record; request transcript
3. **After deposition:** Compare witness's sworn answers to your dependency graph; note any admissions or contradictions
4. **Before trial:** Use Witness Use Matrix to orchestrate which deponent testifies to which facts

---

### Category C: Cross-Reference Documents

#### 5. **section18_evidence_to_element_crosswalk.md** (Updated, in `docs/`)
**Purpose:** Map HUD Section 18 legal requirements to evidence in this case  
**Structure:** Rows for each HUD element; columns for "Evidence in Record" + "Status"  
**Contains:**
- 9 HUD relocation preconditions (from 42 USC 1437p)
- For each precondition, evidence proving whether it was satisfied or not
- Recent additions (from previous session's updates):
  - Hillside Manor RAD PBV entry + Quantum PM identification
  - RAD successor-LP bound by tenant protections (PIH 2019-23)
  - Right to return guaranteed (RAD) (PIH 2019-23 § 3.3)
  - Updated priority RFP list to 7 items (includes RAD HAP contract, PIH cert, right-to-return relocation plan)

**How to Use:**
- Reference during testimony (e.g., "Your Honor, the witness just confirmed HQS analysis was not done—that covers Element #3 in the crosswalk")
- Share with co-counsel to show what evidence is missing
- Use as checklist during trial (check off each element as you prove it)

---

## SUMMARY TABLE: Which Document for What Task?

| Task | Document(s) | Quick Link | Time to Read |
|---|---|---|---|
| *File the motion* | `joinder_quantum_001_motion_for_joinder.md` + `.json` | outputs/ | 15 min |
| *Support with legal argument* | `joinder_quantum_001_memorandum.md` + `.json` | outputs/ | 30 min |
| *Understand case logic* | `joinder_quantum_001_dependency_graph.json` | outputs/ | 10 min |
| *Prepare oral argument* | `HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md` (Part I) | docs/ | 60 min |
| *Create visual exhibits* | `HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md` (Part II) | docs/ | 90 min (printing + setup) |
| *Get courtroom logistics right* | `HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md` (Part V) | docs/ | 20 min |
| *Understand case timeline* | `COURT_FILING_SEQUENCE_JOINDER_QUANTUM.md` | docs/ | 120 min |
| *Plan years-long litigation* | `MASTER_ACTION_PLAN_JOINDER_THROUGH_RESOLUTION.md` | docs/ | 90 min |
| *Prepare deposition questions* | `DEPOSITION_DISCOVERY_STRATEGY_QUANTUM_JOINDER.md` | docs/ | 120 min |
| *Check what evidence is missing* | `section18_evidence_to_element_crosswalk.md` | docs/ | 30 min |

---

## CRITICAL NEXT STEPS (TODAY, APRIL 5, 2026)

### STEP 1: Confirm Case Details (2 hours)
- [ ] Clackamas County case number
- [ ] Judge name (if assigned)
- [ ] Eviction hearing date
- [ ] Quantum Residential registered agent address
- [ ] HACC counsel name & address

### STEP 2: Customize Court-Filing Artifacts (2 hours)
- [ ] Open `outputs/joinder_quantum_001_motion_for_joinder.md`
- [ ] Replace all [BRACKETED] placeholders
- [ ] Save as PDF
- [ ] Have reviewed by attorney of record (if applicable)

### STEP 3: Gather Physical Exhibits (4 hours)
- [ ] Ferron email (January 26, 2026) — print in 18pt, multiple copies
- [ ] HACC Admin Plan lines 32317, 37308 — obtain from HACC, print
- [ ] Section 18 Phase II approval letter — obtain from court docket or HACC
- [ ] Household affidavit or declaration — obtain signatures

### STEP 4: Verify Service Requirements (1 hour)
- [ ] Confirm ORCP 54 notice period (typically 7-14 days before hearing)
- [ ] Identify earliest filing deadline (calculate backwards from eviction hearing date)
- [ ] Plan service method for Quantum (certified mail? in-person? substituted service?)

### STEP 5: Create Visual Exhibits (6-8 hours)
- [ ] Use `HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md` Part II templates
- [ ] Create 3 posters (RAD chain, intake timeline, legal structure)
- [ ] Print on poster board (24"×36" minimum)
- [ ] Bring to hearing + easel for display

---

## DEPENDENCIES & RISKS

### Critical Assumptions (All OK per prior research):
✅ HACC Admin Plan line 37308 accurately names Quantum as PM  
✅ Ferron email is authentic + was sent 1/26/2026  
✅ Hillside Park was demolished under Section 18 (Phase II approved 9/19/2024)  
✅ Hillside Manor LP was created via RAD conversion on 1/1/2021  
✅ Household can testify to intake packet submission + Quantum's denial  

### If These Fail:
⚠️ If Admin Plan is challenged: Obtain certified copy from HACC director; have director authenticate at hearing  
⚠️ If Ferron email doubted: Subpoena email server logs from HACC; call Ferron to authenticate  
⚠️ If RAD conversion details unclear: Obtain full RAD closing documents from HACC; get expert declaration if needed  
⚠️ If household unavailable: Use affidavit instead of live testimony; less credible but workable  

---

## SUCCESS METRICS (WHAT WINNING LOOKS LIKE)

**Motion Hearing:**
- Judge grants motion for joinder (oral ruling or written order within 7 days)
- Quantum Residential named as co-defendant
- Order signed and filed in court docket

**Post-Joinder:**
- Quantum served with summons + complaint within 5 days of order
- Quantum files answer (within 20 days of service)
- Discovery produces intake packet itself (via RFP)
- Depositions lock in Ferron's testimony + Quantum manager's admissions + HACC director's facts
- All 6 dependency graph nodes confirmed TRUE

**Trial/Settlement:**
- Case settles with:
  - HQS-comparable unit offered to household
  - Moving expenses paid ($3K-$10K typical)
  - Disability accommodation (accessible unit) provided
  - Eviction dismissed with prejudice
- OR judgment grants same relief + names Quantum as jointly liable with HACC

**Long-Term:**
- Household rehoused before eviction judgment
- Joinder precedent cited in future RAD cases in Clackamas County
- HACC revises intake procedures to eliminate property manager gatekeeping

---

**This complete artifact package is now ready for filing. All motion, hearing, discovery, and strategic documents are prepared. Execute Phase 1 checklist above, then proceed to filing.**

**Questions? Refer to:**
- **Procedure:** MASTER_ACTION_PLAN_JOINDER_THROUGH_RESOLUTION.md
- **Oral argument:** HEARING_OUTLINE_VISUAL_EXHIBITS_JOINDER.md
- **Discovery:** DEPOSITION_DISCOVERY_STRATEGY_QUANTUM_JOINDER.md
- **Timeline:** COURT_FILING_SEQUENCE_JOINDER_QUANTUM.md
- **Case logic:** joinder_quantum_001_dependency_graph.json (visual logic)
