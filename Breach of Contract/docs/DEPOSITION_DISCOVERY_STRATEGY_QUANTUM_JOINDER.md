# Deposition and Discovery Strategy — Quantum Residential & HACC

**Case:** HACC v. Barber/Cortez (Eviction) with Joinder of Quantum Residential  
**Focus:** Establish facts supporting dependency graph nodes and defeat Quantum/HACC defenses  
**Date:** April 5, 2026  

---

## Deposition Targets and Key Questions

### DEPONENT 1: Ashley Ferron, HACC Housing Resource Manager

**Deposition Objective:**  
Lock in facts establishing the intake failure and Quantum's role; undermine "clerical error" defense; establish HACC's knowledge that Quantum was the intake gatekeeper.

#### Key Areas of Questioning

**A. Intake Process and Quantum's Role**

1. **Intake Design**
   - Q: "Explain how HACC's intake process works for households in transition due to Section 18 demolition. Who receives intake packets?"
   - Q: "In Ms. [Household Member]'s case, why was the intake packet submitted to Quantum Residential's office at Hillside Manor instead of directly to HACC?"
   - Q: "Does HACC have a formal agreement with Quantum to receive and forward intake packets from households at Hillside Manor?"
   - **Dependency Graph Node:** `hacc_quantum_contractual_relationship`

2. **Receipt and Non-Transmission**
   - Q: "In your January 26, 2026 email, you stated: 'The intake packet was submitted to Quantum Residential staff at the Hillside Manor leasing office, it was not provided to The Housing Authority of Clackamas County.' Describe what you know about how the packet got to Quantum and why it did not reach HACC."
   - Q: "Based on your statement that the packet was 'submitted to Quantum Residential staff,' did you have any belief or knowledge that Quantum staff had received it?"
   - Q: "In that same email, you directed the household: 'Ask Quantum Residential staff at the Hillside Manor leasing office to send the previously submitted intake packet directly to me.' Why did you ask them to send the 'previously submitted' packet if they had not received it?"
   - **Dependency Graph Node:** `quantum_received_cortez_documents`, `quantum_failed_to_transmit_to_hacc`

3. **False Denial and Household Response**
   - Q: "The household's March 12, 2026 email states: 'Quantum Residential, who falsely claimed that we did not provide them with an application.' Did you ever receive any communication from Quantum claiming they did not receive the application?"
   - Q: "If Quantum claimed they did not receive the application, is that consistent or inconsistent with your own January 26 statement that the packet was 'submitted to Quantum Residential staff'?"
   - Q: "What did you understand the phrase 'falsely claimed' to mean? Did you believe the household's characterization that Quantum's denial was false?"
   - **Dependency Graph Node:** `quantum_falsely_denied_receiving_application`

**B. "Separate from County" Statement**

4. **The Ferron Contradiction**
   - Q: "In your January 26 email, you wrote: 'Hillside Manor and Quantum Residential are separate from the county and are not able to provide assistance to households.' Explain what you meant by this statement."
   - Q: "Is it accurate that Hillside Manor is PHA-owned (publicly owned) according to HACC's Administrative Plan, Chapter 18, Exhibit 18-1, at line 37308?"
   - Q: "At the same line 37308, does the HACC Administrative Plan identify Quantum Residential Property Management as the property manager for Hillside Manor Apartments Limited Partnership?"
   - Q: "If Hillside Manor is PHA-owned and Quantum is the named property manager, how could you characterize them as 'separate from the county'?"
   - Q: "Was your statement that Quantum is 'separate from the county' accurate, and if not, why was it made?"
   - **Dependency Graph Node:** `ferron_misrepresentation_quantum_separate`, `ferron_misrepresentation_contradicted_by_admin_plan`

5. **Knowledge of Quantum's Relationship to HACC**
   - Q: "At the time you wrote the January 26 email, were you aware that Quantum Residential was the property manager for Hillside Manor, a PHA-owned property?"
   - Q: "Were you aware that Hillside Manor was created through a Rent Assistance Demonstration (RAD) conversion from Hillside Park public housing?"
   - Q: "Does HACC treat property managers of PHA-owned properties as part of the relocation and intake process?"
   - **Dependency Graph Nodes:** `quantum_is_successor_in_interest`, `hacc_quantum_contractual_relationship`

**C. Relocation Failure**

6. **Section 18 Preconditions**
   - Q: "What relocation counseling was offered to the household before the September 19, 2024 Phase II notice?"
   - Q: "What HQS comparability analysis was performed for the household's relocation?"
   - Q: "Were relocation moving expenses paid or committed to for this household?"
   - Q: "What is the status of relocation to date (April 5, 2026)?"
   - **Dependency Graph Node:** `section18_compliance_deficient`, `household_still_in_eviction_no_completed_relocation`

---

### DEPONENT 2: [Quantum Residential Manager or Superintendent at Hillside Manor]

**Deposition Objective:**  
Establish Quantum's receipt of the intake packet; lock in their failure to transmit; undermine "we never received it" defense; establish Quantum's control over access to relocation opportunities.

#### Key Areas of Questioning

**A. Intake Packet Receipt**

1. **Intake Procedures at Hillside Manor**
   - Q: "Describe the procedures for receiving and processing intake packets from HACC at Hillside Manor."
   - Q: "Who at Quantum Residential's Hillside Manor office would receive an intake packet from a resident or their representative?"
   - Q: "In [date], did anyone at Hillside Manor receive an intake packet from the household on behalf of Ms./Mr. [Household Member]?"
   - Q: "What records does Quantum maintain of intake packets received at the Hillside Manor office?"
   - **Dependency Graph Node:** `quantum_received_cortez_documents`

2. **Non-Transmission**
   - Q: "If an intake packet was received at Hillside Manor, what is Quantum's procedure for forwarding it to HACC?"
   - Q: "Did anyone at Quantum forward the household's intake packet to HACC between [date of receipt] and [date of Ferron's email, 1/26/2026]?"
   - Q: "What would prevent Quantum from forwarding such a packet?"
   - Q: "In January 2026, did Ashley Ferron or anyone from HACC request that Quantum send the 'previously submitted intake packet' to her?"
   - Q: "Did Quantum comply with that request?"
   - **Dependency Graph Node:** `quantum_failed_to_transmit_to_hacc`

3. **False Denial**
   - Q: "At any time, did anyone at Quantum tell the household that Quantum had not received their intake packet?"
   - Q: "Was that statement true or false?"
   - Q: "If Quantum did receive the packet, why would anyone at Quantum deny receiving it?"
   - **Dependency Graph Node:** `quantum_falsely_denied_receiving_application`

**B. Property Manager Role and Relocation Duties**

4. **RAD Successor Status and Obligations**
   - Q: "Describe Quantum Residential's relationship to Hillside Manor Apartments Limited Partnership."
   - Q: "What is Quantum's role at Hillside Manor?"
   - Q: "Is Hillside Manor the property resulting from a Rent Assistance Demonstration (RAD) conversion of Hillside Park public housing?"
   - Q: "When did the RAD conversion close?"
   - Q: "Is Quantum bound by HUD Notice PIH 2019-23 and its successor-owner obligations?"
   - Q: "What relocation and tenant-protection obligations does HUD PIH 2019-23 impose on Quantum as property manager of the RAD successor?"
   - **Dependency Graph Nodes:** `rad_conversion_to_lp`, `quantum_named_lp_manager`, `quantum_bound_by_rad_obligations`

5. **Relocation Interference**
   - Q: "Did Quantum cooperate with HACC in facilitating the household's relocation from Hillside Park/Hillside Manor?"
   - Q: "If relocation requires cooperation between Quantum (property manager) and HACC (PHA), what role does Quantum play in that process?"
   - Q: "Whether or not Quantum received the intake packet, does Quantum have a duty under PIH 2019-23 to cooperate in the household's relocation from the RAD property?"
   - **Dependency Graph Node:** `quantum_prevented_application_processing`, `quantum_prevented_relocation`

**C. Portfolio-Wide HACC Relationship**

6. **Broader Quantum-HACC Relationship**
   - Q: "Does Quantum manage other properties besides Hillside Manor that are owned or financed by HACC?"
   - Q: "What is the nature of Quantum's relationship with HACC across its portfolio?"
   - Q: "Does Quantum understand itself to be working in coordination with HACC on tenant relocation and relocation counseling?"
   - [If "yes" to any:] "Explain how that coordination works."
   - **Dependency Graph Node:** `quantum_portfolio_wide_hacc_relationship`

---

### DEPONENT 3: HACC Director or Finance Officer

**Deposition Objective:**  
Establish HACC's knowledge of Quantum's intake processing role; confirm Administrative Plan contents; establish RAD successor chain; lock in failure to satisfy Section 18 preconditions.

#### Key Areas of Questioning

**A. Administrative Plan Verification**

1. **Hillside Manor in Admin Plan**
   - Q: "Is Exhibit 18-1 of HACC's Administrative Plan (effective 7/1/2025) an accurate and complete representation of HACC's current property inventory?"
   - Q: "At source line 37308 of that exhibit, does HACC's Administrative Plan state that Hillside Manor Apartments is PHA-Owned, with Quantum Residential Property Management, closing date 1/1/2021, and HAP Contracts including Eminent Domain 5 PBV and RAD HAP (70 RAD PBV units)?"
   - Q: "When HACC filed that Administrative Plan with HUD, did HACC verify the accuracy of the property and property manager information?"
   - Q: "Is the entry for Hillside Manor at line 37308 accurate?"
   - **Dependency Graph Node:** `hacc_admin_plan_rad_obligations`

2. **RAD Successor Chain**
   - Q: "When Hillside Park was demolished/disposed of under Section 18, was a RAD conversion conducted to create Hillside Manor LP?"
   - Q: "Was Hillside Manor LP created with the proceeds from the Hillside Park disposition and Eminent Domain compensation?"
   - Q: "Is Quantum Residential named in the RAD HAP contract as property manager of Hillside Manor LP?"
   - Q: "Does HACC understand Quantum to be bound by HUD Notice PIH 2019-23 and all RAD successor obligations?"
   - **Dependency Graph Nodes:** `eminent_domain_acquisition_documented`, `rad_conversion_closed_2021_01_01`, `rad_pih_2019_23_governs`

**B. Section 18 Relocation Compliance**

3. **Missing Preconditions**
   - Q: "For Section 18 demolitions or dispositions, what HUD-required preconditions must HACC satisfy before displacement?"
   - Q: "Were each of the following completed for the household's relocation from Hillside Park?
     - Relocation counseling referral and assignment
     - HQS comparability analysis for offered units
     - Commitment to pay actual relocation moving expenses
     - Resident consultation (meetings + documentation)
   - Q: "If counseling was not provided, why not?"
   - Q: "If HQS comparability analysis was not performed, why not?"
   - Q: "If moving expenses were not paid, why not?"
   - Q: "If consultation was not documented, why not?"
   - **Dependency Graph Node:** `section18_compliance_deficient`

4. **Quantum's Role in Section 18 Compliance**
   - Q: "Does HACC rely on property managers at its PHA-owned properties (like Quantum at Hillside Manor) to facilitate relocation and provide updates to residents?"
   - Q: "Did HACC expect Quantum to cooperate in the household's intake and relocation process?"
   - Q: "When the household's intake packet was submitted to Quantum at Hillside Manor, did HACC understand Quantum to be part of the intake and relocation chain?"
   - **Dependency Graph Node:** `hacc_controls_displacement`, `quantum_controls_intake_processing`

---

## Requests for Production (Interrogatories)

### To Quantum Residential

**RFP 1: Intake and Intake Packet**
- All documents relating to the household's intake packet received on any date at the Hillside Manor office, including:
  - Original intake packet
  - Date stamp or receipt documentation
  - Email or memo confirming receipt
  - Any notes or logs recording the packet's receipt and status

**RFP 2: RAD Documents**
- Copy of the RAD HAP contract entered into 1/1/2021 for Hillside Manor LP (70 RAD PBV units)
- Copy of Hillside Manor LP's operating agreement
- Certification or declaration that Quantum Residential understands itself to be bound by HUD Notice PIH 2019-23 and all RAD successor obligations
- Any communications between Quantum and HACC regarding right-to-return obligations

**RFP 3: Relocation Communications**
- All email, memo, or written communications between Quantum and HACC regarding the household's relocation, including any requests for cooperation, updates, or status reports

**RFP 4: Hillside Manor Intake Procedures**
- Written procedures for receiving and processing intake packets at Hillside Manor
- Training materials or guidance provided to Hillside Manor staff on handling HACC intake packets
- Logbook or registry of intake packets received at Hillside Manor office

### To HACC

**RFP 5: Administrative Plan and RAD Successor Documents**
- Full Administrative Plan Chapter 17 and 18 (effective 7/1/2025) with all exhibits
- The decision to name Quantum Residential as property manager of Hillside Manor LP
- Documents establishing the RAD conversion of Hillside Park to Hillside Manor LP (1/1/2021)
- Copy of the RAD HAP contract and any amendments

**RFP 6: Household-Specific Relocation Documents**
- Relocation plan for the household (if any)
- HQS comparability analysis (if any)
- Relocation moving expense authorization or payment (if any)
- Counseling referral and assignment documentation
- Resident consultation meeting notes or records
- All communications with Quantum regarding the household's intake or relocation

**RFP 7: Section 18 Phase II Documentation**
- Full Section 18 Phase II approval packet including:
  - HUD approval letter
  - Relocation plan submitted to HUD
  - Consultation summary
  - Board resolution
  - Environmental review

---

## Interrogatories (Sample Format)

### To Quantum

**Interrogatory 1:**
State whether Quantum Residential received the household's intake packet at the Hillside Manor office (yes/no), and if yes, the date of receipt.

**Interrogatory 2:**
State whether Quantum Residential forwarded the household's intake packet to HACC (yes/no), and if no, explain why not.

**Interrogatory 3:**
Describe all communications between Quantum Residential and HACC regarding the household's intake, application, or relocation status.

**Interrogatory 4:**
Identify the RAD HAP contract(s) that Quantum Residential understands itself to be the property manager under, and describe each contract's relocation and tenant-protection obligations.

---

## Subpoena Targets

### 1. Quantum Residential — Business Records Subpoena
- **Documents to Request:**
  - Intake packet register or logbook for Hillside Manor (all dates)
  - Copy of the household's intake packet as received
  - Date stamp or email confirmation of receipt
  - All communications with HACC regarding the household
  - RAD HAP contract (1/1/2021)
  - Training materials on intake procedures
  
### 2. HACC — Administrative Records Production
- **Admin Plan Chapter 17 & 18** (full, with Exhibit 18-1 including lines 32317, 37308)
- **HUD Approval Letter** (Phase II, September 19, 2024)
- **Relocation Plan** (if submitted to HUD for this household or as part of Section 18 Phase II)
- **Consultation Records** (any documentation of consultation with residents about Section 18)
- **Board Resolution** (authorizing Section 18 demolition/disposition)

---

## Dependency Graph Node Verification Checklist

Use depositions to lock in facts supporting these key nodes:

| Dependency Graph Node | Evidence to Establish via Deposition |
|---|---|
| `quantum_received_cortez_documents` | Ferron email ("submitted to Quantum"), Admin Plan time stamp, Quantum manager testimony |
| `quantum_failed_to_transmit_to_hacc` | Ferron email ("not provided to HACC"), Ferron's request to "ask Quantum to send", household testimony on non-receipt |
| `quantum_falsely_denied_receiving_application` | Household declaration ("falsely claimed"), testimony that Ferron asked them to "ask Quantum to send" |
| `hacc_quantum_contractual_relationship` | Admin Plan (Quantum named PM), Ferron testimony on reliance on Quantum for intake, RAD HAP contract |
| `quantum_is_successor_in_interest` | Admin Plan Chapter 18, RAD HAP contract (1/1/2021), HACC director testimony on RAD conversion |
| `rad_obligations_bind_quantum` | PIH 2019-23, RAD HAP contract, HACC director testimony on successor obligations |
| `section18_compliance_deficient` | HACC director testimony: no counseling, no HQS analysis, no relocation expenses, no consultation record |
| `complete_relief_impossible` | Quantum manager testimony on role in relocation + Ferron testimony on intake obstruction |
| `inconsistent_obligations_risk` | Quantum testimony that it is both PHA property PM and "separate from county" — cannot be ordered by court while remaining PM |

---

## Trial Preparation: Witness Use Matrix

### Ferron (HACC Housing Resource Manager)
- **Direct Examination:** Intake process, reason for directing household to Quantum, why she characterized Quantum as "separate from county", Section 18 preconditions not satisfied
- **Cross (IF by Quantum):** Ferron's email confirms Quantum received packet; Ferron's own statement proves her characterization was false
- **Cross (IF by HACC):** Ferron directed household to ask Quantum to send packet—proves Ferron knew Quantum had it

### Quantum Manager
- **Direct Examination (by household):** Lock in receipt of packet; failure to transmit; false denial
- **Cross (by Quantum):** No questions; Quantum will not call own manager if possible
- **Cross (by HACC):** May try to blame HACC for not following up

### Household Member
- **Direct Examination:** Submitted packet to Quantum's office; Quantum falsely denied receiving it (per Ferron); relocation obstruction; disability accommodation
- **Cross (by Quantum):** Establish household did actually submit packet; confirm timeline
- **Cross (by HACC):** Confirm household attempted relocation; no alternatives offered

### HACC Director
- **Direct Examination (by household):** Admin Plan contents; RAD successor chain; Section 18 preconditions not met
- **Cross (by HACC):** Will testify to same facts on direct; may downplay missing preconditions
- **Cross (by Quantum):** Will be forced to confirm Quantum is property manager; Quantum is successor-in-interest

---

## Litigation Strategy Notes

1. **Ferron is the linchpin.** Her email proves the intake failure and her "separate from county" statement. Lock her into specifics via deposition before trial.

2. **Admin Plan is the smoking gun.** Get Ferron and the HACC director to confirm its accuracy. Quantum's name is right there as property manager.

3. **Quantum's false denial** creates estoppel argument. Even if Quantum claims the packet was "misfiled," Ferron's email proves Quantum staff had it.

4. **Section 18 preconditions** are missing on every front. RFP will likely show no documentation. Use HACC director's deposition to lock this in.

5. **PIH 2019-23** binds Quantum as successor. Even if Quantum claims it's "just a property manager," HUD Notice makes clear the PM inherits all obligations.

---

## Next Deposition Scheduling Steps

1. Serve Deposition Notice on HACC attorney (14 days notice, per ORCP 39)
2. Serve Deposition Notice on Quantum (if address obtained; may need substituted service)
3. Coordinate on convenient dates with opposing counsel
4. Prepare outline of questions (use above as template)
5. Bring dependency graph printout to deposition for reference
6. Have Admin Plan excerpt and Ferron email available (marked as exhibits)
7. Transcriber will record; request transcript for case file

---

**Ready for Discovery:** All deposition targets identified, key questions prepared, and RFP strategy laid out. Use this document as roadmap for depositions and production requests.
