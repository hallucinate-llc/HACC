# Motion for Joinder — Court Filing Package & Checklist

**Case:** HACC v. Barber/Cortez (Eviction), Clackamas County Circuit Court  
**Date Prepared:** April 5, 2026  
**Filing Deadline:** [**CONFIRM WITH YOUR ATTORNEY — depends on eviction hearing date**]  
**Court:** Clackamas County Circuit Court, Civil Division  

---

## ⚠️ CRITICAL — BEFORE FILING

### 1. EVICTION HEARING DATE (URGENT)
**ACTION ITEM:**  
- [ ] Obtain eviction hearing date from court docket or HACC notice
- [ ] Calculate filing deadline: Motion must be filed **AT LEAST 14 days before hearing** (ORCP 6A allows expedited motions but 14 days is standard)
- [ ] **TODAY IS APRIL 5** — if hearing is in April, motion must file **by April 18 at latest** (accounting for 14-day standard notice)
- [ ] If hearing is sooner than April 19, file motion as EXPEDITED with certification of good cause

### 2. CASE CAPTION & INFORMATION
**OBTAIN FROM COURT SYSTEM:**
- [ ] **Case Number:** _________________ (e.g., "21CV12345")
- [ ] **Trial Judge:** _________________ (from order or docket)
- [ ] **Judge's Email/Clerk:** _________________ (for filing instructions)
- [ ] **Court-Specific Rules:** Download Clackamas County local rules (https://www.clackamasccourt.us/)

---

## Court-Ready Motion Template (with customization fields)

### CAPTION FORMAT

```
IN THE CIRCUIT COURT OF THE STATE OF OREGON
FOR THE COUNTY OF CLACKAMAS

HOUSING AUTHORITY OF CLACKAMAS COUNTY ("HACC"),
                                                         Plaintiff,
v.                                                       Case No. [CASE NUMBER]
                                                         
[BARBER/CORTEZ — FULL NAMES],                           
                         Defendants,                     MOTION FOR JOINDER OF
                                                         NECESSARY AND INDISPENSABLE
__________________________________________               PARTY UNDER ORCP 29A
                                                         AND 22B
[IF PRESENT] ___________________________,
                         Intervening Defendant(s).
__________________________________________
```

---

## Step-by-Step Filing Instructions

### PHASE 1: Document Preparation (3-4 hours)

#### Step 1A: Customize the Motion for Joinder
**File to use:** `/outputs/joinder_quantum_001_motion_for_joinder.md`

**Customizations required:**

1. **Case Number & Judge Name** (Section I.INTRODUCTION — top of document)
   - Replace `[CASE NUMBER]` with actual case number (e.g., "21CV-12345")
   - Add judge's name if known

2. **Exhibit Callouts** (Sections II.FACTUAL BASIS)
   - Current template references: Exhibit M, Exhibit L, Exhibit C, Exhibit I
   - **VERIFY ALL EXHIBITS** — see Exhibit List below
   - If any exhibit missing, note "TO BE PRODUCED" and adjust argument

3. **Section 18 Phase II Notice Date** (Section II.A)
   - Verify from HACC notice: Replace "September 19, 2024" if different
   
4. **Admin Plan Details** (Section II.B)
   - Verify line numbers in HACC Administrative Plan
   - Current template uses **line 37308** (Hillside Manor entry) — confirm this is correct
   - Run grep search in case file: `grep -n "Quantum Residential" /path/to/admin_plan.txt`

5. **Ferron Email Details** (Section II.C)
   - Verify email date: currently "1/26/2026" — confirm
   - If email has been amended or supplemented, cite correct version
   - Include actual quotes from email (already in template, just verify)

6. **Household Declaration** (Section II.D)
   - Verify household member names and declaration date
   - If declaration is Exhibit C, confirm page number where quote appears

7. **Disability Accommodation** (Section II.G) — OPTIONAL
   - If household has documented disability and accessibility claim, include
   - If not applicable, remove this subsection

8. **Proposed Third-Party Defendant Name & Address** (throughout)
   - Replace "Quantum Residential Property Management, L.P." if exact entity name differs
   - Gather entity's registered address for service (see Service section below)
   - Confirm whether Quantum is a Limited Partnership, LLC, or other entity type

#### Step 1B: Edit and Finalize Motion
**Instructions:**
1. Open `/outputs/joinder_quantum_001_motion_for_joinder.md` in MS Word or Google Docs
2. Apply these formatting rules:
   - **Font:** Times New Roman, 12 point
   - **Line spacing:** Double-spaced (1.5 is acceptable)
   - **Margins:** 1" all sides
   - **Page numbers:** Bottom center
   - **Caption alignment:** Left-aligned, single-spaced
   - **Headings:** Bold, all caps (Roman numerals for main sections)

3. Save as: `[CASE_NUMBER]_Motion_for_Joinder_Barber_v_HACC.docx`

#### Step 1C: Prepare Memorandum of Law (Supporting Document)
**File to use:** `/outputs/joinder_quantum_001_memorandum.md`

**Customizations:**
1. Change case number in caption to match motion
2. Verify all 11 authorities cited (ORCP 29A/22B, 42 USC 1437p, 24 CFR 970.7/970.21, PIH 2019-23, CFR 8 disability, FHA 3604, giebeler case, ORS 105.135, HACC Admin Plan)
3. If any authority is local/unreported, add pinpoint cites (page numbers) where applicable
4. **Check Giebeler case:** If Oregon case, verify West headnotes and current citation format
5. Expand any section that feels weak (especially Section 18 compliance gaps)

**Formatting:**
- Same as motion (Times New Roman, 12 pt, double-spaced)
- Should be 5-8 pages max
- Save as: `[CASE_NUMBER]_Memorandum_Compulsory_Joinder.docx`

---

### PHASE 2: Exhibit Preparation (2-3 hours)

#### EXHIBIT LIST & SOURCING

| Exhibit | Description | Source | Status | Pages |
|---------|-------------|--------|--------|-------|
| **A** | HACC Admin Plan, Chapter 17 (Section 18 authority) | HACC official file | ☐ Attach | 5-10 |
| **B** | HACC Admin Plan, Chapter 18, Exhibit 18-1 (property list) | HACC official file | ☐ Attach | 10-20 |
| **C** | Household Declaration (falsely claimed intake denial) | Your client file | ☐ Attach | 2-3 |
| **D** | Hillside Park Phase II General Information Notice | HACC notice dated 9/19/24 | ☐ Attach | 2-3 |
| **E** | Relocation Counseling Records (if any) | HACC case file | ☐ Attach or "None" | 1-2 |
| **F** | HQS Comparability Analysis (if any) | HACC case file | ☐ Attach or "None" | 1-2 |
| **G** | Relocation Moving Expense Authorization (if any) | HACC case file | ☐ Attach or "None" | 1-2 |
| **H** | Household Accommodation Request & Response | Your client file | ☐ Attach | 2-3 |
| **I** | Medical/disability documentation (if applicable) | Your client file | ☐ Attach | 1-2 |
| **J** | RAD HAP Contract for Hillside Manor (dated 1/1/2021) | HACC file or HUD | ☐ Attach | 3-5 |
| **K** | HUD Notice PIH 2019-23 (excerpts) | HUD website or case file | ☐ Attach | 3-5 |
| **L** | Email from Ashley Ferron (1/26/2026) re: intake obstruction | Your client file | ☐ Attach | 1-2 |
| **M** | Phase II General Information Notice (Sept 19, 2024) | HACC notice | ☐ Attach | 2-3 |

#### EXHIBIT ORGANIZATION
1. **Numbering:** Label each exhibit in footer: "[Case Number] - Exhibit A", "[Case Number] - Exhibit B", etc.
2. **Bates Stamps (optional but recommended):** If you have access to bates stamping software, stamp bottom-right of each page (e.g., "00001", "00002"). This helps court track multi-page exhibits.
3. **Exhibit Cover Sheet:** For each exhibit, add a cover sheet reading:
   ```
   EXHIBIT [LETTER]
   
   [Description of Exhibit]
   
   Pages [X] – [Y]
   ```
4. **Collection:** Bind exhibits in order A–M. Exhibits can be:
   - Separately bound (one exhibit notebook)
   - Collectively bound at end of motion packet (motion → memo → exhibits A–M)

---

### PHASE 3: Declaration Preparation (1-2 hours)

#### AFFIDAVIT/DECLARATION BY HOUSEHOLD MEMBER (IF NEEDED)

If household member has not yet submitted a declaration, create one supporting joinder.

**Declaration Template** (see below — customize with actual facts):

```
IN THE CIRCUIT COURT OF THE STATE OF OREGON
FOR THE COUNTY OF CLACKAMAS

HOUSING AUTHORITY OF CLACKAMAS COUNTY,
                                                        Plaintiff,
v.                                                  Case No. [CASE_NUMBER]
                                                     
[HOUSEHOLD NAMES],                                  
                         Defendants.                Affidavit of [HOUSEHOLD MEMBER]


I, [FULL NAME], declare under penalty of perjury under the laws of the State of Oregon that the
following facts are true and correct:

1. I reside at [ADDRESS]. I am a defendant in the above-captioned eviction action.

2. On or about [DATE IN 2024], HACC notified me that Hillside Park public housing, where I was living,
   was being demolished under Section 18 of the U.S. Housing Act of 1937, 42 U.S.C. § 1437p.

3. As part of the relocation process, I was instructed to submit an intake application to determine
   my eligibility for relocation housing.

4. On or about [DATE], I submitted my intake application packet to Quantum Residential Property
   Management at the Hillside Manor leasing office.

5. I was subsequently told by Quantum Residential staff that Quantum did not have my application.
   This was false; I personally submitted it to Quantum's office.

6. On January 26, 2026, I received an email from HACC Housing Resource Manager Ashley Ferron
   confirming that my intake packet was submitted to Quantum and was not provided to HACC.
   Ms. Ferron's email specifically stated: "The intake packet was submitted to Quantum Residential
   staff at the Hillside Manor leasing office, it was not provided to The Housing Authority of
   Clackamas County." Ms. Ferron then directed me to "Ask Quantum Residential staff at the Hillside
   Manor leasing office to send the previously submitted intake packet directly to me."

7. This confirms that Quantum received my intake packet but failed to transmit it to HACC.

8. As a result of Quantum's failure, my relocation application was never processed by HACC.

9. To date (April 5, 2026), I remain in the evicted unit with no relocation offer or approved
   housing. No HQS comparability analysis has been performed. No relocation moving expenses have
   been provided. No relocation counseling has been completed.

10. I cannot obtain complete relief without Quantum Residential being joined because:
    a. Quantum controls whether my intake packet is transmitted to HACC;
    b. Quantum, as property manager of relocation housing, controls access to furnished housing;
    c. I cannot be compensated for the intake failure without Quantum's liability being determined.

I declare under penalty of perjury that the foregoing is true and correct.

Executed on this _________ day of April, 2026.


                                    ____________________________________
                                    [HOUSEHOLD MEMBER NAME]


STATE OF OREGON
County of [COUNTY]:

I, [NOTARY NAME], a notary public in and for the County of [COUNTY], State of Oregon, do hereby
certify that [HOUSEHOLD MEMBER NAME] is personally known to me (or has produced [ID TYPE] as
identification), and that said person executed the foregoing affidavit willingly as their own free
act.

IN WITNESS WHEREOF, I have hereunto set my hand and affixed my official seal on this _________
day of April, 2026.


                                    ____________________________________
                                    [NOTARY NAME], Notary Public
                                    Commission Expires: _______________
                                    
[Affix notary seal here]
```

**Notarization Rules:**
- Declaration must be **notarized** — bring government-issued ID to notary public
- Oregon notaries are available at banks, title companies, many law offices
- Cost typically $5-10
- Notary will stamp/seal the document (must be original, not photocopy of seal)

---

### PHASE 4: Service of Process (1-2 hours)

#### SERVICE REQUIREMENTS UNDER ORCP 5 & 7

Before filing motion, you must have a plan to **serve** the motion and memorandum on:
1. Opposing counsel (HACC attorney)
2. Quantum Residential (to be joined)

#### A. Service on HACC Attorney

**Method:** Email or mail (ORCP 7(2)(a) allows electronic service if attorney consents)

**Step 1: Identify HACC's attorney**
- [ ] Obtain from case docket: HACC attorney name, email, mailing address
- [ ] Verify email address is listed on Oregon State Bar website

**Step 2: Prepare service transmittal** (email or cover letter)
```
Subject: Service of Motion for Joinder — HACC v. Barber/Cortez, Case No. [CASE_NUMBER]

Dear [Attorney Name]:

Please find attached the Motion for Joinder of Necessary and Indispensable Party [and Memorandum 
in Support thereof] in the above-captioned case, filed in Clackamas County Circuit Court.

A hearing on the motion is requested [DATE], or at such time as the court deems appropriate.
All exhibits are attached in PDF format.

Service on behalf of [household defendant names]:
[Your name / attorney name]

[Signature block]
```

**Step 3: Send via email with read receipt** (or publish via court e-filing system if available)

#### B. Service on Quantum Residential (Third-Party Defendant)

**Critical:** Quantum must be served with the motion and must have opportunity to respond.

**Step 1: Locate Quantum's address**
- [ ] Search Oregon corporate registry: https://sos.oregon.gov/business/pages/index.aspx
  - Search for "Quantum Residential Property Management" or similar
  - Registered agent address should be listed
- [ ] Alternative: Search for Quantum's address in Hillside Manor property records (county assessor)
- [ ] If LLC/LP: Agent address is often law firm; call Quantum directly to confirm mailing address

**Step 2: Prepare Notice of Motion for Joinder**
```
NOTICE OF MOTION FOR JOINDER OF NECESSARY AND INDISPENSABLE PARTY

TO: Quantum Residential Property Management, L.P., and its officers, agents, and employees:

PLEASE TAKE NOTICE that Defendants [Barber/Cortez] will move the above-captioned court on the
_________ day of April, 2026, at _________ o'clock, or as soon thereafter as counsel may be heard,
for an order joining Quantum Residential Property Management, L.P. as a necessary and indispensable
party to this action under Oregon Rules of Civil Procedure 29A and 22B.

The grounds for this motion are set forth in the Memorandum in Support of Motion for Joinder,
filed herewith.

DATED this _________ day of April, 2026.

                                        ____________________________
                                        [Your Name]
                                        Attorney for Defendants
                                        [Your Address]
                                        [Your Phone]
                                        [Your Email]
```

**Step 3: Service method (choose one):**
- [ ] **Personal Service:** Hire process server to deliver to Quantum's registered agent address
- [ ] **Certified Mail / Return Receipt Requested:** Send to Quantum's address with signature confirmation
- [ ] **Substituted Service:** If Quantum cannot be located, follow ORCP 7(3) procedures (mail to last known address + publication if needed)

**Proof of Service:** After serving, file "Certificate of Service" or "Affidavit of Service" with court showing:
- Date served
- Method (email, certified mail, personal service)
- Parties served
- Your signature

---

### PHASE 5: FILING WITH COURT (1 hour)

#### CLACKAMAS COUNTY FILING OPTIONS

**Option A: Electronic Filing (e-filing)**
- [ ] Check Clackamas County website: https://www.clackamasccourt.us/
- [ ] Register for e-filing system (usually Oregon's eCourt or similar)
- [ ] File motion, memorandum, and exhibits online
- [ ] Court issues filing confirmation immediately
- [ ] Filing fee (typically $50–200 for motion; verify with court)

**Option B: In-Person Filing at Courthouse**
- [ ] Clackamas County Circuit Court Clerk
  - Address: 2200 Kaen Road, Oregon City, OR 97045
  - Phone: (503) 650-3079
- [ ] Bring: 
  - [ ] 2–3 copies of motion + memorandum
  - [ ] 2–3 copies of exhibit packet
  - [ ] Filing fee (check or card)
  - [ ] Proof of service on opposing parties
- [ ] File originals; keep copies for your records

**Option C: Mail Filing**
- [ ] Send via certified mail with return receipt
- [ ] Include cover letter with case number and filing fee (check)
- [ ] Request clerk to file and return conformed copy

#### FILING DOCUMENTS CHECKLIST
- [ ] Motion for Joinder (signed and formatted)
- [ ] Memorandum in Support (signed and formatted)
- [ ] Certificate of Service (showing service on HACC attorney and Quantum)
- [ ] Exhibits A–M (labeled, organized, in order)
- [ ] Declaration/Affidavit of Household Member (notarized)
- [ ] Filing fee payment (check/card/cash as accepted)

#### FILING DEADLINE CONFIRMATION
- [ ] File at least **14 days before eviction hearing** (per ORCP 6A/7A)
- [ ] If deadline is tight (<7 days away), seek expedited consideration (filing fee may increase)
- [ ] Request hearing date in motion: "Hearing requested [DATE], or such date as court deems appropriate"

---

## PHASE 6: POST-FILING ACTIONS (Ongoing)

### IMMEDIATE (within 24 hours of filing)
- [ ] Confirm filing with clerk: Call (503) 650-3079 to confirm receipt
- [ ] Obtain case number update or docket entry showing motion was filed
- [ ] Save filing confirmation email/receipt

### WITHIN 5–7 DAYS
- [ ] Wait for responses:
  - [ ] HACC's opposition (if any)
  - [ ] Quantum's response or motion to quash service (if served)
- [ ] Monitor court docket for any rulings or scheduling orders
- [ ] Prepare reply if needed (reply brief due 7 days after opposition, per local rules)

### WITHIN 10–14 DAYS
- [ ] Prepare for motion hearing:
  - [ ] Print dependency graph for courtroom display (optional but powerful)
  - [ ] Prepare opening statement (see hearining script: `/outputs/joinder_quantum_001_hearing_script.md`)
  - [ ] Organize exhibit index for easy reference
  - [ ] Brief key cases (especially Giebeler if it's Oregon authority)

### HEARING DAY
- [ ] Arrive 15 minutes early
- [ ] Bring originals of all exhibits (in case court wants to examine)
- [ ] Bring motion + memorandum (for bench reference)
- [ ] Use hearing script for oral argument
- [ ] Be prepared for court to ask questions about:
  - Joinder standard (complete relief impossible?)
  - Quantum's connection to relocation process (who is PM? What duties?)
  - Section 18 compliance gaps (yes, but is Quantum responsible?)

---

## CLACKAMAS COUNTY LOCAL RULES (KEY PROVISIONS)

Download full rules from: https://www.clackamasccourt.us/general-info/local-rules

### Rules That Apply to Motion for Joinder:
- **Rule 7.005** — Motion practice generally
- **Rule 7.010** — Filing and service
- **Rule 7.020** — Page limits (typically 15 pages for motion + memorandum combined)
- **Rule 7.030** — Reply briefs (7 days after opposition)
- **Rule 7.040** — Hearing requirements (request date in motion)

### Rules for Joinder Specifically:
- **ORCP 29A** — Persons to be joined (compulsory joinder)
- **ORCP 22B** — Impleader (third-party practice)
- **ORCP 15(C)(2)** — Relation back of amendments (if joinder becomes amendment to complaint)

---

## CRITICAL EXHIBITS — ACQUISITION CHECKLIST

### Exhibit A: HACC Administrative Plan, Chapter 17
**Acquisition:**
- [ ] Contact HACC: Email or call requesting "Chapter 17 of HACC Administrative Plan (effective 7/1/2025)"
- [ ] If not available by email, request via public records request (Oregon Public Records Law, ORS 192.311)
- [ ] Expect: 5–10 pages
- [ ] Key sections: Section 18 authority, relocation requirements, property ownership authority

### Exhibit B: HACC Administrative Plan Chapter 18, Exhibit 18-1
**Acquisition:**
- [ ] Request "Chapter 18 Exhibit 18-1 (Property Inventory)" from HACC
- [ ] This is large; request only the sections relevant to Hillside Park/Hillside Manor
- [ ] Key line: **Line 37308** — Hillside Manor entry with Quantum PM, RAD HAP, 1/1/2021 closing
- [ ] Expect: 10–20 pages

### Exhibit C: Household Declaration
**Acquisition:**
- [ ] Work with household member to prepare written declaration
- [ ] Use template above (affidavit format)
- [ ] Have notarized before filing
- [ ] Expect: 2–3 pages

### Exhibit L: Ashley Ferron Email (1/26/2026)
**Acquisition:**
- [ ] Already in household's case file
- [ ] Email to household stating: "intake packet was submitted to Quantum Residential staff... it was not provided to HACC"
- [ ] Request to household to "ask Quantum to send the previously submitted intake packet"
- [ ] Print/save as PDF
- [ ] Expect: 1–2 pages

### Exhibit J: RAD HAP Contract (Hillside Manor, 1/1/2021)
**Acquisition:**
- [ ] Request from HACC: "RAD HAP contract for Hillside Manor Apartments LP, effective 1/1/2021"
- [ ] Alternative: HUD LIHTC database (https://www.huduser.gov/portal/datasets/lihtc.html) or similar
- [ ] Key sections: Property manager identified as Quantum, tenant protections, right-to-return clause
- [ ] Expect: 3–5 pages

### Exhibit K: HUD Notice PIH 2019-23
**Acquisition:**
- [ ] Download from HUD website: https://www.hud.gov/program_offices/public_indian_housing/notices
- [ ] Search for "PIH 2019-23" (Rent Assistance Demonstration — Successor Owner Obligations)
- [ ] Key sections: Property manager duties, relocation responsibilities, right-to-return
- [ ] Expect: 3–5 pages

---

## TIMING ROADMAP

| Phase | Task | Timeline | Deadline |
|-------|------|----------|----------|
| **URGENT** | Confirm eviction hearing date | TODAY (4/5) | — |
| **Phase 1** | Customize motion + memorandum | 4/5–4/6 | 4/6 end of day |
| **Phase 2** | Prepare exhibits A–M | 4/6–4/7 | 4/7 end of day |
| **Phase 3** | Prepare + notarize household declaration | 4/7–4/8 | 4/8 afternoon |
| **Phase 4** | Arrange service on HACC attorney + Quantum | 4/8–4/9 | 4/9 end of day |
| **Phase 5** | File with court | 4/9 | 4/9 (or earliest possible before hearing) |
| **Phase 6** | Monitor docket for responses | 4/9–4/16 | Ongoing |
| **Hearing** | Motion hearing in front of judge | 4/18–4/25 | [Court date] |

---

## WHAT TO DO IF MOTION IS OPPOSED

### If HACC Files Opposition
1. **Read opposition carefully** — note strongest arguments
2. **Prepare reply brief** (due 7 days after opposition, per ORCP 7(3)(A))
3. **Reply should address:**
   - HACC claim that Quantum is "not indispensable" (yes it is; complete relief impossible without Quantum)
   - HACC argument that joinder is improper (no; ORCP 29A/22B standard clearly satisfied)
   - Any new facts HACC raises (prepare household declaration response if needed)
4. **File reply with clerk** — at least 3 days before hearing

### If Quantum Files Response
1. **Likely arguments:** "Not properly served," "not indispensable," "already party via implied joinder"
2. **Counter-arguments (prepare in advance):**
   - Service was proper → affidavit of service proves it
   - Indispensability: Complete relief impossible without Quantum's liability determined
   - Implied joinder: Taking job as property manager of relocation housing = necessary party

### If Either Party Opposes Hearing
1. Request expedited consideration: "This motion is ripe for immediate hearing given April [XX] eviction hearing date"
2. Cite ORCP 6A (short time may require expedited relief)
3. File declaration of good cause if court requires justification

---

## WHAT TO DO IF MOTION IS GRANTED

1. **Amend Complaint:** Within 14 days, file First Amended Complaint adding Quantum as defendant
2. **Serve Quantum:** Serve amended complaint + summons on Quantum (formal service, not informal notice)
3. **Quantum's Answer Due:** Quantum has 30 days to file answer (unless extended)
4. **Revised Hearing:** Eviction hearing may be postponed to allow Quantum to respond → **this buys you time**
5. **Continue with Discovery:** Use RFPs and interrogatories from DEPOSITION_DISCOVERY_STRATEGY doc

---

## WHAT TO DO IF MOTION IS DENIED

1. **Preserve Record:** Request court to state reasons for denial on record (oral or in writing)
2. **Object:** File objection to ruling if there's legal error (optional)
3. **Appeal:** After final judgment, you may appeal joinder denial as part of appellate brief
4. **Continue Litigation:** Proceed with affirmative defenses (Section 18 non-compliance, disability accommodation) even without Quantum joined
5. **Strategic Pivot:** 
   - File counterclaim against HACC for Section 18 violations
   - Argue Quantum's absence prevents HACC from obtaining complete relief (leverage this for future joinder motion if new evidence emerges)

---

## CONTACT INFORMATION & RESOURCES

### Clackamas County Circuit Court
- **Phone:** (503) 650-3079
- **Clerk's Office Hours:** 8:30 AM – 4:30 PM, Monday–Friday
- **Website:** https://www.clackamasccourt.us/
- **Local Rules:** https://www.clackamasccourt.us/general-info/local-rules

### Oregon Judicial Department
- **Court Rules:** https://oregon.gov/osca/pages/rule-pages.aspx
- **ORCP (Oregon Rules of Civil Procedure):** https://oregon.gov/osca/pages/rule-pages.aspx

### HUD Resources
- **PHN 2019-23 (RAD Successor Obligations):** Search "PIH 2019-23" on HUD website
- **Section 18 Relocation Requirements:** 24 CFR 970.7 and 970.21
- **FHA Fair Housing Act:** 42 USC 3601 et seq.

### Notary Public Locator
- **Oregon State Bar:** https://www.osbar.org/public-services/find-legal-help/
- **Local banks/title companies:** Yellow Pages or Google "notary public Oregon City"

---

## FINAL CHECKLIST BEFORE HITTING FILE BUTTON

- [ ] Case number confirmed with court
- [ ] Judge name (if assigned) confirmed
- [ ] Eviction hearing date confirmed — filing deadline calculated and met
- [ ] Motion customized with all case-specific information
- [ ] Memorandum reviewed for legal accuracy and local rule compliance
- [ ] All exhibits (A–M) acquired, organized, labeled
- [ ] Household declaration prepared and notarized
- [ ] Service plan finalized (HACC attorney email + Quantum address obtained)
- [ ] Filing method selected (e-filing, in-person, or mail)
- [ ] Filing fee amount confirmed and payment method arranged
- [ ] Local rules reviewed (page limits, formatting, hearing requests)
- [ ] Hearing script `/outputs/joinder_quantum_001_hearing_script.md` printed and reviewed
- [ ] Dependency graph printed (optional but recommended for courtroom use)

---

**Ready to File.** Use this checklist step-by-step. File the motion by your deadline. Victory awaits.**
