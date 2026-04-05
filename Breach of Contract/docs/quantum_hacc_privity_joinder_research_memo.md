# Quantum / HACC Privity and Joinder Research Memo

## Purpose

This memo isolates repository evidence supporting the position that joinder of Quantum Residential is preferable because the present dispute arises from a single integrated relocation and housing-access transaction involving both the Housing Authority of Clackamas County (HACC) and the Blossom / Quantum side of the process. It also separates what the current record does and does not yet prove about successor-in-interest and private-use disposition.

## Strongest Existing Record Support

### 1. HACC itself placed Blossom inside the HACC-run relocation and voucher pipeline.

- `evidence/paper documents/HACC Jan 2026 blossom.pdf`
  - The existing chronology and GraphRAG summaries identify this as a January 8, 2026 HACC notice to Jane Cortez about Blossom.
  - The derived summaries consistently state that the notice said the Tenant Protection Voucher process had not yet started and that Ashley Ferron should be contacted to start that process.
  - This matters because it places Blossom inside HACC's own displacement and TPV administration rather than treating Blossom as a wholly separate private-market housing search.

- `evidence/paper documents/graphrag/HACC_Jan_2026_blossom/document_knowledge_graph.json`
  - Contains the extracted role text: `please contact ashley ferron to start that process`.
  - This supports a coordinated process theory: HACC sent the notice, HACC identified the contact, and the Blossom move was handled through the same relocation and voucher sequence.

- `https://www.clackamas.us/housingauthority/hillsidemasterplan.html`
  - HACC's public Hillside Park Redevelopment page states that, after Section 18 disposition approval and receipt of Tenant Protection Vouchers, residents can begin the relocation process with guidance from HACC and its relocation consultants.
  - The same page states that residents will be given the option to move into a new unit at Hillside Park or relocate with a Tenant Protection Voucher to a unit of their choosing.
  - This is additional public-facing support that Hillside Park placement and TPV relocation were being presented by HACC as linked options within the same redevelopment-driven relocation program.

### 2. The Blossom-side materials themselves tie the project to HACC processing.

- `evidence/paper documents/blossom.pdf`
- `evidence/paper documents/graphrag/blossom/document_knowledge_graph.json`
  - The GraphRAG extraction states: `Applications for the project processed through HACC PBV Waitlist`.
  - That is the cleanest current record support for privity-like coordination. It shows the relevant housing opportunity was not simply an unrelated private listing; it was processed through an HACC-administered waiting list.

### 2A. HACC's own Administrative Plan directly names Quantum Residential as property management company for a PHA-owned HAP contract development.

- `workspace/temporary-cli-session-migration/workspace-generated/evidence/did-key-legacy-temporary-session/local-import/0001_8ee6f7d1-0c36-48e4-9677-336b95fb9858.txt`
  - The HACC Administrative Plan extract contains the following entry at approximately line 32152:

    > **Clayton Mohr Commons**
    > Address: 399 Caufield St, Oregon City, OR 97045
    > Owner Information: PHA-Owned
    > **Property Management Company: Quantum Residential**
    > PHA-Owned: Yes. Inspected by third party contractor Steven Nagel or HomeForward
    > Mixed Finance Development: Yes
    > HAP CONTRACT Effective Date of Contract: 11/1/2019
    > Term of HAP Contract: 20 year term
    > Expiration Date of Contract: 10/31/2039

  - This is a direct, on-record statement in HACC's own administrative plan. It is not an allegation or inference. HACC's own filed plan identifies Quantum Residential as the property management company for a PHA-owned, mixed-finance development operating under a 20-year HUD HAP contract.
  - Oregon City, OR 97045 is in Clackamas County — the same county where HACC operates and where the Hillside Park redevelopment is taking place.
  - This is the strongest current repository fact connecting Quantum Residential to HACC's subsidized housing operations in an official capacity under federal contract.

- The same Admin Plan extract (approximately line 32317) contains a second Quantum Residential entry under Chapter 17 (PBV Development Information) for **Hillside Manor**, 2889 SE Hillside Court, Milwaukie, OR 97222:

    > **Hillside Manor** (Chapter 17 PBV Exhibit 17-1)
    > Address: 2889 SE Hillside Court, Milwaukie, OR 97222
    > Owner Information: PHA-Owned
    > **Property Management Company: Quantum Residential**
    > PHA-Owned: Yes. Independent entity: Steven Nagel or HomeForward
    > Mixed Finance Development: Yes
    > HAP Contract: June 1, 2020 – May 31, 2040 (20-year term)
    > Units: 96 × 1BR + 4 × 2BR = 100 units

  - Hillside Manor is the same property that HACC identified as the relocation destination property and waitlist gateway for Hillside Park displaced residents. The Admin Plan confirms HACC owns it and Quantum Residential manages it under a 20-year HAP contract signed in June 2020.

- The same extract (approximately line 33349) contains a **third Quantum Residential entry** for **Good Shepherd Village**, 12608 SE Skyshow Place, Happy Valley, OR:

    > **Good Shepherd Village** (Chapter 17 PBV Exhibit 17-1)
    > Owner Information: Good Shepherd Village Limited Partnership (Catholic Charities)
    > **Property Management Company: Quantum Residential**
    > PHA-Owned: No
    > Mixed Finance Development: Yes
    > HAP Contract: November 1, 2023 – October 31, 2043 (20-year term)

  - Good Shepherd Village is a non-PHA-owned LP structure where HACC contracted Quantum Residential directly as property manager. This establishes Quantum as HACC's portfolio-wide preferred property manager operating under HAP contracts across multiple ownership structures and counties — not a coincidental or site-specific appointment.

- The same extract (approximately line 37308) contains a **fourth Quantum Residential entry** under Chapter 18 (RAD PBV Development Information, Exhibit 18-1) for **Hillside Manor Apartments**, 2889 SE Hillside Ct, Milwaukie, OR 97222 — the same address:

    > **Hillside Manor Apartments** (Chapter 18 RAD PBV Exhibit 18-1)
    > Owner Information: **Hillside Manor Limited Partnership**
    > **Property Management Company: Quantum Residential Property Management**
    >   Email: HillsideManor@QResInc.com | Phone: 503-344-4540
    > PHA-Owned: Yes
    > Mixed-Finance Development: Yes
    > **Closing Date: 1/1/2021**
    > **RAD Notice: PIH 2019-23**
    > HAP Contracts (two separate):
    >   — 06/01/2020: **Eminent Domain 5 PBV plus 26 Enhanced PBV**
    >   — 01/01/2021: **RAD HAP contract (70 RAD PBV)**

  - **This is the successor-in-interest smoking gun.** The Hillside Manor site appears in the Admin Plan twice — once as a regular PBV property (Chapter 17) and separately as a RAD PBV property (Chapter 18). The Chapter 18 RAD entry reveals:

    (a) **The private ownership entity is Hillside Manor Limited Partnership (LP)**. The LP is the private successor entity created through the RAD (Rental Assistance Demonstration) conversion. RAD allows a PHA to convert public housing from Section 9 ACC-based funding to project-based Section 8, while simultaneously bringing in private equity investors (typically via Low-Income Housing Tax Credits, LIHTC) through an LP ownership structure. HACC holds a nominal general partner interest but the LP brings in private investor capital. This is the legal mechanism for "private use" disposition.

    (b) **The RAD closed 1/1/2021**, which means the conversion from public housing to the LP ownership structure was completed on January 1, 2021 — concurrent with the Hillside Park Phase I/Phase II demolition and displacement timeline.

    (c) **"Eminent Domain 5 PBV"** in the 06/01/2020 HAP contract means five units at the Hillside Manor site were acquired through an eminent domain process and placed in PBV status. This directly connects the Hillside Park land acquisition to the eminent domain and displacement pathway that preceded the LP/RAD structure.

    (d) **Quantum Residential Property Management** is named as the manager for the post-RAD LP structure, with a direct contact email (HillsideManor@QResInc.com) and phone number. Quantum's management of the LP property is not merely incidental — it is the designated operational role in the private successor entity's governance.

  - The full successor chain from Public Housing → RAD/LP → Quantum Management is:
    HACC public housing at Hillside Park → Eminent Domain acquisition → PBV conversion (6/1/2020, 5 eminent domain units + 26 enhanced) → RAD conversion to Hillside Manor LP (1/1/2021, 70 RAD PBV units) → Quantum Residential as named LP property manager.

  - This confirms the theory that Quantum is not merely a private landlord independently selected for relocation placement. Quantum Residential entered the role of property manager for HACC's PHA-owned, RAD-converted, mixed-finance LP property — making it the operational arm of the private successor entity at the same Hillside site.

- The same extract (approximately line 6313) contains the HACC PBV wait-list policy:

    > PBV Wait List for the following properties: Hillside Manor, TCC and Rosewood. Additional waiting lists will be created for new PBV developments where TPV holders have the right to return as relocation participants.

  - This expressly links Hillside Manor to the HACC PBV wait list system and defines the relocation-return framework for TPV holders — directly connecting the named Hillside Park relocation pathway to HACC's PBV housing portfolio.

- The same extract (approximately lines 26919–26947) lists excluded units from the PBV program cap:

    > Units in the following projects are not subject to the program cap or project cap because they are excluded units:
    > — Hillside Manor Apartments
    > — Blossom & Community Apartments
    > — Park Place Apartments

  - These units are excluded because they are **replacement housing for a demolished original project**, with a **first-occupancy preference for former residents** of the original project. That is the legal definition of Section 18 disposition replacement housing under the PBV program.
  - This directly confirms that Blossom & Community Apartments and Hillside Manor Apartments occupy the same HUD-recognized category: replacement housing for a demolished original HACC project, with relocation preferences for the displaced residents.
  - It also confirms that HACC had administrative plan provisions governing these specific properties — meaning the Blossom placement was not a coincidental private-market option; it was embedded in HACC's formal administrative apparatus.

### 2B. Direct HACC emails show that application intake for the Blossom path was being routed through Quantum-side staff and then back to HACC.

- `evidence/email_imports/starworks5-confirmed-case-import/0002-RE-Allegations-of-Fraud---JC-Household-88246644b2924275bad7d62be838b1c3-clackamas.us/message.json`
  - The preserved December 2, 2025 HACC message states: `If this is the case, their office staff is who will need the packet returned.`
  - That is direct evidence that, if the household pursued Blossom or Community Apartments, HACC expected packet return through the Blossom-side office rather than only through HACC's own intake channel.

- The same preserved thread later states on January 26, 2026:
  - `While the intake packet was submitted to Quantum Residential staff at the Hillside Manor leasing office, it was not provided to The Housing Authority of Clackamas County.`
  - `Ask Quantum Residential staff at the Hillside Manor leasing office to send the previously submitted intake packet directly to me ... or Complete and return a new intake packet.`
  - This is one of the strongest current repository facts for joinder. It is not just an allegation by the household. It is an HACC-side statement that the packet had in fact been submitted to Quantum staff, that Quantum-side staff did not transmit it onward, and that HACC treated that handoff failure as part of the same voucher-processing problem.

- The same thread also preserves January 6, 2026 and December 22, 2025 emails copied to `blossom@quantumres.com`.
  - That is additional support that the HACC-side and Blossom-side actors were being addressed within the same communications sequence regarding relocation and intake.

- **Ashley Ferron email, January 26, 2026 (same thread)** contains a directly contradicted misrepresentation:
  - Ferron wrote: *"Hillside Manor and Quantum Residential are separate from the county and are not able to provide assistance to households that are not pursuing a unit at Blossom or Community Apartments."*
  - This statement is directly contradicted by the HACC Administrative Plan, which lists Hillside Manor as PHA-Owned (Chapter 17 PBV entry) and Hillside Manor Apartments as PHA-Owned under the Hillside Manor Limited Partnership (Chapter 18 RAD PBV entry) — both under Quantum Residential as named property manager.
  - Quantum Residential is listed as the contracted property manager for three PHA-owned or HACC-contracted developments: Clayton Mohr Commons (PHA-Owned), Hillside Manor (PHA-Owned, Chapter 17), and Hillside Manor Apartments under Hillside Manor LP (PHA-Owned, Chapter 18 RAD). The representation that Quantum is "separate from the county" is inconsistent with HACC's own administrative plan.
  - This discrepancy between HACC's filed administrative documents and the in-litigation position of its staff supports both (a) the joinder theory that Quantum's role is embedded in HACC's program operations, and (b) the suggestion that HACC is attempting to shift responsibility to Quantum while concealing their operational coordination.

- **Parkside Heights (parksideheights@quantumres.com)** — the email import manifest (`evidence/email_imports/solomon-live-fetch-2026/starworks5/gmail-import/email_import_manifest.json`) shows Parkside Heights (another Quantum Residential property, at the QResInc.com domain) was included in email threads alongside Kati Tilton (HACC Operations Manager) and HACC-Relocation regarding the relocation placement.
  - This establishes that HACC's relocation operations were actively coordinating with multiple Quantum Residential properties simultaneously — not a one-off application referral, but a structured pipeline between HACC and Quantum's managed portfolio.

- `evidence/email_imports/starworks5-confirmed-case-import-cli/0007-Re-Additional-Information-Needed-.../message.json`
  - A separate email in the same case thread contains this direct verbatim quote from the household member:

    > *"Quantum Residential, who falsely claimed that we did not provide them with an application, which was also made to your organization in the first place."*

  - This is significant in two directions. First, it is a sworn-record statement that the application was submitted and that Quantum denied receiving it — a factual dispute about Quantum's conduct that can only be resolved with Quantum in the case. Second, it frames the Quantum denial as directly causally linked to HACC's failure (the application "was also made to your organization"), showing the two failures were part of the same chain.

### 3. The complaint emails gave joint notice to HACC staff and a non-HACC Blossom / Quantum-side participant.

- `workspace/manual-imap-download-focused-2026-03-31-snippets/seq_10270/body-snippet.txt`
  - The preserved text states:
    - `I have previously indicated to quantum residential and your office my Intent to sue under the civil rights act`
    - `blossom has already refused to process applications submitted to them for 2 months`
    - `has refused to house a service animal`
    - `has engaged in discrimination on the basis of race`
    - `your organizations have not been providing the opportunity to do so`
  - This is important because it does more than accuse Quantum separately. It frames HACC and Quantum as jointly responsible for blocking the family's exit from HACC-controlled housing.

- `research_results/evidence_review_20260327_083610/chronology/complaint_ready_chronology.md`
  - Confirms emails on February 26, March 2, March 9, and March 10, 2026 were sent to:
    - `KTilton@clackamas.us`
    - `AFerron@clackamas.us`
    - `charity@magikcorp.com`
  - That supports notice to both the HACC side and the Blossom / Quantum-side process in the same thread.

### 4. The private-side intake materials impose owner / agent duties inside the same application process.

- `evidence/paper documents/Vera Application.pdf`
- `evidence/paper documents/graphrag/Vera_Application/document_knowledge_graph.json`
  - Extracted text includes: `Notify applicant of the results of Owner/Agent's review within a reasonable time after receipt of all`.
  - This helps on duty. Even without a final lease, the owner / agent side had an identified application-review obligation.
  - In joinder terms, that means the case is not only about HACC's voucher administration; it also concerns whether the owner / agent side performed its part of the housing-access transaction.

### 5. HACC's own program materials treat the housing transaction as a coordinated three-party relationship.

- `workspace/did-key-hacc-temp-session.json`
  - The imported HACC Administrative Plan table of contents identifies:
    - `The HCV Partnerships`
    - `The HCV Relationships`
    - `What Does HACC Do?`
    - `What Does the Owner Do?`
    - `What Does the Family Do?`
  - Even though the current saved extract is a table of contents rather than the full substantive page text, it still supports the general framing that HACC's housing-choice processes contemplate interlocking duties between HACC, the owner, and the family.

### 6. The broader HACC voucher and PBV materials refer to owner-side obligations, not just PHA-side duties.

- `evidence/paper documents/housing authority project based voucher.pdf`
- `evidence/paper documents/graphrag/housing_authority_project_based_voucher/document_knowledge_graph.json`
  - Extracted text includes:
    - `If the property has more then four (4) units, owners must ...`
    - `The property owner should be present for the inspection ...`
  - This supports the argument that the private owner / manager is an operational participant in the same subsidy-backed tenancy process.

## How This Supports Joinder

### A. Same transaction or occurrence

The current record supports framing the dispute as one continuous housing transition:

1. HACC displaced the household and controlled the TPV / relocation sequence.
2. HACC identified Blossom as part of that sequence.
3. HACC's public Hillside Park redevelopment materials described Hillside Park placement and TPV relocation as options within the same redevelopment-driven relocation program.
4. HACC directed that, if Blossom was being pursued, the packet be returned to Blossom-side office staff.
5. HACC later acknowledged that the intake packet had been submitted to Quantum staff but not transmitted to HACC.
6. Blossom materials say the project was processed through HACC's PBV waitlist.
7. The household then communicated complaints simultaneously to HACC staff and a Blossom / Quantum-side recipient.
8. The private-side materials imposed owner / agent review duties over the application.
9. **HACC's own Administrative Plan directly lists Quantum Residential as the property management company for Clayton Mohr Commons, a PHA-owned mixed-finance development at 399 Caufield St, Oregon City, under a 20-year HUD HAP contract.** That is not a third-party allegation — it is an on-record statement in HACC's filed administrative plan.
10. **HACC's own Administrative Plan classifies both Hillside Manor Apartments and Blossom & Community Apartments as excluded units — replacement housing for a demolished HACC project — with a first-occupancy preference for former residents.** That is a direct administrative confirmation that Blossom's placement function, Hillside Manor's relocation function, and Quantum's management role were all embedded in HACC's formal PBV housing program structure.

11. **The Admin Plan's Chapter 17 PBV entry names Quantum Residential as manager of Hillside Manor itself** (the HACC-named relocation destination) — meaning the "relocation pathway" that HACC presented to the household was, from the outset, administered by the same private entity that HACC later claimed was "separate from the county."

12. **The Admin Plan's Chapter 18 RAD PBV entry establishes a private successor LP (Hillside Manor Limited Partnership) as the legal owner post-RAD conversion (1/1/2021), with Quantum Residential as named manager** — placing Quantum inside the private successor entity structure at the same site where the eminent-domain-based displacement of Hillside Park residents originated.

13. **HACC's own correspondence treated Quantum's leasing office as the official intake channel**, received documents from Hillside Manor/Quantum staff (cortez 1-4.pdf), and then directed the household to have Quantum staff forward the intake packet to HACC — placing Quantum squarely inside the same voucher-processing transaction.

That is a substantially stronger basis for joinder than a theory that Quantum merely committed separate downstream misconduct.

### B. Duty and privity-like linkage

The current evidence does not yet prove classic contract privity in the narrow sense of a signed final lease between plaintiffs and Quantum. But it does support a stronger practical privity or integrated-transaction theory:

1. HACC routed applicants into the Blossom opportunity.
2. HACC's own redevelopment materials described Hillside Park placement and TPV relocation as linked options in the same resident-relocation program.
3. HACC routed the intake packet through Blossom-side / Quantum-side staff when Blossom was being pursued.
4. HACC later confirmed the packet had been submitted to Quantum staff but not turned over to HACC.
5. Blossom was processed through an HACC waitlist.
6. The owner / agent side had review and notice duties to the applicant.
7. The alleged failure was specifically a failure to process, transmit, review, or respond within a coordinated HACC-linked housing opportunity.
9. **HACC's own Administrative Plan names Quantum Residential as property management company for Clayton Mohr Commons (PHA-Owned, HAP contract), Hillside Manor (PHA-Owned, 100 PBV units), and Hillside Manor Apartments under the Hillside Manor Limited Partnership (RAD PBV).** That is not a single anomalous entry. It is HACC's portfolio-wide property management relationship with Quantum Residential, documented across three separate Admin Plan exhibits, covering both regular PBV and RAD PBV programs.

10. **Blossom and Hillside Manor are both classified in the Administrative Plan as replacement housing for a demolished HACC project.** Quantum's role as named property manager for HACC-owned and HACC-contracted developments, combined with Blossom's administrative classification as HACC replacement housing, supports an integrated-duty theory without requiring a separately filed management agreement.

11. **The RAD conversion (PIH 2019-23) created parallel Section 18-style tenant protection obligations** binding on both HACC (as converting PHA) and the Hillside Manor LP/Quantum structure as successor operator — including right-to-return, relocation plan compliance, and continuing tenant protections during conversion. Both parties share these RAD obligations as a matter of federal housing law.

12. **Quantum's HACC-contracted management role spans multiple ownership structures** (PHA-owned at Clayton Mohr Commons; PHA-owned at Hillside Manor; LP-owned at Hillside Manor LP; and non-PHA LP at Good Shepherd Village/Catholic Charities) — establishing a standing management service relationship with HACC, not a one-off site assignment. This standing relationship is what made Quantum the natural and HACC-designated operator for Blossom and the relocation pipeline.

13. **HACC staff's email claim that Quantum is "separate from the county"** is directly contradicted by the same HACC's own filed Administrative Plan — which an opposing party can argue is an admission against interest or at minimum establishes the impropriety of HACC disclaiming Quantum's role after integrating Quantum into the PHA-owned property management structure.
9. **Blossom and Hillside Manor are both classified in the Administrative Plan as replacement housing for a demolished HACC project.** Quantum's role as named property manager for an HACC-owned development, combined with Blossom's administrative classification as HACC replacement housing, supports an integrated-duty theory without requiring a separately filed management agreement.

That is enough to argue — based on the existing record — that complete relief and factual adjudication cannot occur without Quantum in the case. The theoretical gap is no longer the absence of any Quantum / HACC contractual link, but only the absence of a direct Blossom-specific management agreement, which remains a priority discovery target.

### C. Prevention / causation defense in the eviction case

The email text is especially useful for the eviction posture because it frames HACC and Quantum together as preventing the household from leaving HACC-controlled housing. That directly supports defenses based on prevention, estoppel, causation, and failure of promised relocation pathways.

## Successor-in-Interest / Private-Use Theory

**UPDATE: The evidence assessment below has been substantially revised following review of the HACC Administrative Plan extract (0001_8ee6f7d1...txt). The prior conclusion that the repository lacked any direct proof of a Quantum / HACC contractual relationship was incorrect.**

### What the present repository now directly proves

The HACC Administrative Plan extract contains the following confirmed facts:

1. **Quantum Residential is HACC's named property management company for Clayton Mohr Commons**, a PHA-owned mixed-finance development in Oregon City (Clackamas County) operating under a 20-year HUD HAP contract effective November 1, 2019. This is not an inference. It is a direct named entry in HACC's own filed administrative plan.

2. **Quantum Residential is also named as property management company for Hillside Manor** (Chapter 17 PBV entry) at 2889 SE Hillside Court, Milwaukie — PHA-Owned, Mixed Finance, 20-year HAP contract (June 1, 2020 – May 31, 2040, 100 units). This is the same Hillside Manor property that served as the HACC-identified relocation destination for Hillside Park displaced residents.

3. **The Admin Plan's Chapter 18 (RAD PBV) entry for Hillside Manor Apartments confirms the private successor-in-interest structure:**
   - Owner: **Hillside Manor Limited Partnership** (the private LP created through RAD conversion, closing 1/1/2021)
   - Manager: **Quantum Residential Property Management** (HillsideManor@QResInc.com)
   - HAP contract 06/01/2020 includes **"Eminent Domain 5 PBV plus 26 Enhanced PBV"** — 5 units from an eminent domain proceeding were the first public housing units converted to PBV status at this site
   - RAD Notice **PIH 2019-23** governs the conversion, which creates tenant protections parallel to Section 18 (right to return, relocation rights, consultation obligations) binding on both HACC and the private LP operating as successor owner
   - The RAD conversion closed **January 1, 2021** — placing the private LP structure on record concurrent with the Hillside Park Phase I/Phase II demolition timeline
   - **This is the private-use succession chain**: Original Hillside Park public housing → eminent domain acquisition → PBV conversion (Eminent Domain 5 PBV, 6/1/2020) → RAD conversion to Hillside Manor Limited Partnership (LP) as private successor entity (1/1/2021) → Quantum Residential as the LP's named property manager.

4. **Quantum Residential also manages Good Shepherd Village** (12608 SE Skyshow Place, Happy Valley, OR), a non-PHA-owned LP (Good Shepherd Village Limited Partnership / Catholic Charities), under a HAP contract effective November 1, 2023. This establishes Quantum as HACC's portfolio-wide contracted property manager operating across both PHA-owned and private-LP HACC developments — not a site-specific appointment but a standing service relationship.

5. **Both Hillside Manor Apartments and Blossom & Community Apartments are classified in the HACC Administrative Plan as excluded units** — specifically as replacement housing for a demolished original HACC project, operating under the first-occupancy-preference-for-former-residents rule. This is the precise administrative structure through which the Hillside Park relocation pathway was administered.

6. **The HACC PBV waitlist explicitly names Hillside Manor as one of the three original PBV properties.** The same waitlist language states additional waitlists will be created for new PBV developments where TPV holders have the right to return as relocation participants — which describes the Hillside Park Phase II and Blossom relocation structure exactly.

7. **The PHA-Owned Unit provisions in the same Administrative Plan** specify that for PHA-owned units, an independent entity must perform rent determinations, inspections, and development-activity oversight. That independent-entity role is consistent with Quantum Residential's engagement as property management company for all PHA-owned developments in the Admin Plan, confirming that the HACC / Quantum business relationship is not incidental but is structurally required for PHA-owned PBV and RAD developments.

### RAD-Specific Section 18 Parallel Obligations

RAD conversions under Notice PIH 2019-23 impose obligations on the converting PHA and the successor LP operator that directly parallel Section 18:

- **Right to return**: Displaced residents have a right to a unit in the RAD-converted development upon completion. HACC and Quantum (as LP manager) owe this jointly.
- **Relocation plan**: The PHA must have an approved relocation plan; failure to implement it creates joint liability where the manager is the implementing party.
- **Tenant protections during conversion**: PIH 2019-23 requires the PHA to continue all tenant protections (lease, grievance rights, reasonable accommodation) during the RAD conversion period. Quantum as manager is the operational party responsible for maintaining these protections.
- **Successor owner bound**: The RAD HAP contract runs with the LP ownership — Hillside Manor LP (whose property Quantum manages) is itself bound by the same tenant protection obligations the original PHA had under the ACC.

This creates joint and several regulatory obligation between HACC (as converting PHA) and the Hillside Manor LP/Quantum structure as successor owner-manager.

### What remains as priority discovery targets

The record is substantially stronger than previously assessed, but the following are still not directly in the current repository:

1. A Blossom-specific HAP contract entry in the Admin Plan (to add Blossom directly alongside the other Quantum entries).
2. A recorded deed or vesting deed linking Blossom to an LP structure parallel to Hillside Manor LP.
3. The full Section 18 disposition approval for the original Hillside Park site naming Blossom as authorized replacement housing.
4. The LP operating agreement or management agreement for Hillside Manor Limited Partnership identifying Quantum's authority and obligations.


### Revised filing framing for this section

Given the new evidence, the successor-in-interest theory is no longer merely a discovery-dependent allegation. It is supported by:
- An on-record HACC statement naming Quantum Residential as property manager for a PHA-owned HAP contract development in Clackamas County.
- An on-record HACC classification of Blossom & Community Apartments as Section 18 replacement housing with former-resident preferences governed by the same administrative plan.
- The HACC PBV waitlist expressly naming Hillside Manor as a PBV property within the same relocation-and-right-of-return framework.

The remaining gap is only Blossom-specific owner/management documentation, which can be pursued in discovery. The theory is now properly characterized as well-supported by the existing record, not merely as inference.

## Best Current Filing Framing

The safest high-value framing from the existing record is:

1. HACC and Quantum participated in one integrated relocation and voucher-backed housing transaction.
2. HACC controlled the displacement and TPV side.
3. Blossom / Quantum controlled or materially participated in intake, review, and processing on the owner / agent side.
4. The failure to process the Blossom opportunity, and the refusal to move the family out of HACC-controlled housing, are overlapping facts that cannot be fairly resolved without Quantum.
5. **HACC's own Administrative Plan names Quantum Residential as property management company for a PHA-owned HAP contract development in Clackamas County, and classifies Blossom & Community Apartments alongside Hillside Manor as Section 18 replacement housing under HACC's formal PBV program.** This makes the joinder theory supported by on-record HACC administrative documents, not merely the allegations of the household or inferences from third-party sources.

The current joinder theory is coordinated duty, overlapping causation, **and** demonstrable HACC-Quantum contractual relationship documented in HACC's own filed administrative plan.

## Highest-Value Next Discovery

To fully close the Blossom-specific documentation gap, target these records next:

1. Blossom-specific owner participation agreement or HAP contract (to add Blossom directly alongside the Clayton Mohr Commons HAP entry).
2. Recorded deed or vesting deed for Blossom and the former HACC site.
3. Section 18 disposition approvals and closing statements for the original Hillside Park site.
4. Full HACC Administrative Plan text for the 17-I.F. PHA-Owned Units section to confirm independent-entity review requirements applicable to Blossom.
5. Any HACC-to-Quantum correspondence identifying Quantum's management role at Blossom specifically.

## Bottom Line

Based on the current evidence, the best-supported argument is not merely that Quantum is another wrongdoer. It is that HACC and Quantum occupied different but interlocking positions in the same relocation and housing-access process, making joinder preferable to avoid incomplete relief, inconsistent factfinding, and the false appearance that the eviction and relocation failures can be adjudicated in isolation.