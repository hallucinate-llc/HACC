# Oregon Authority Grounding Memo

Date: 2026-04-07

## Scope

This memo grounds the current contempt, sanctions, and subpoena logic to official Oregon statute and rule sources.

## Official source set reviewed

- Oregon Legislature, `ORS chapter 33`
- Oregon Legislature, `ORCP 17`
- Oregon Legislature, `ORCP 46`
- Oregon Legislature, `ORCP 55`

## Authority anchors

### 0. Protective-proceeding procedural framework

- `ORS 125.050`
- `ORS 125.060`
- `ORS 125.065`
- `ORS 125.075`
- `ORS 125.080`
- `ORS 125.120`
- Working proposition:
  chapter 125 supplies the protective-proceeding framework for application of ORCP/OEC, notice, objections, hearings, counsel, and the distinct protected-person special-advocate mechanism.

Use in this workspace:
- grounds probate/protective procedure without overstating a generic GAL power
- supports the objection/hearing path in the Jane Cortez guardianship track
- distinguishes a protected person special advocate from other representative roles

### 1. Remedial contempt initiation

- `ORS 33.055`
- Working proposition:
  an aggrieved party may initiate a proceeding to impose remedial sanctions for contempt and may request that the contempt defendant be ordered to appear.

Use in this workspace:
- supports the show-cause / remedial-contempt procedural path
- supports requiring specific alleged acts to be identified in supporting documentation

### 2. Compelling attendance after nonappearance

- `ORS 33.075`
- Working proposition:
  if a person served with an order to appear under `ORS 33.055` fails to appear, the court may issue orders or a warrant necessary to compel appearance.

Use in this workspace:
- supports the structured show-cause appearance path
- supports escalation from notice to compelled appearance if a valid order to appear is ignored

### 3. Remedial sanctions available for contempt

- `ORS 33.105(1)`
- Working proposition:
  available remedial sanctions may include compensation for loss, injury, or costs; compliance-oriented orders; attorney fees; and other effective remedial sanctions unless otherwise limited by statute.

Use in this workspace:
- supports compensation / corrective relief framing in contempt-related drafts
- supports noninterference and compliance-oriented remedial requests

### 4. Improper-purpose and unsupported-filing certification

- `ORCP 17 C(2)-(4)`
- Working proposition:
  a signer certifies that filings are not presented for an improper purpose, that legal positions are warranted by existing law or a nonfrivolous argument, and that factual assertions are supported by evidence or specifically identified as expected to be supported after investigation or discovery.

Use in this workspace:
- strongest current authority anchor for a frivolous / abusive filing theory
- supports keeping unsupported factual assertions clearly identified and proof-gated

### 5. Discovery-expense and discovery-order sanctions

- `ORCP 46 A(4)`
- `ORCP 46 B(2)`
- Working proposition:
  the court may award reasonable expenses on a motion to compel, and may make just orders when a party fails to obey an order to provide or permit discovery.

Use in this workspace:
- supports the compel / deficiency / sanctions branch once subpoena disputes mature into discovery-order practice
- should be used carefully because some portions apply most directly after motion-to-compel or discovery-order posture is reached

### 6. Subpoena obedience baseline

- `ORCP 55 A(1)(a)(vi)(A)-(B)`
- Working proposition:
  a subpoena must warn that it must be obeyed unless a judge orders otherwise and that disobedience is punishable by a fine or jail time.

Use in this workspace:
- supports the nonparty production / subpoena compliance branch
- supports the proposition that subpoena noncompliance can trigger coercive enforcement

### 7. Service and time computation for later-filed papers

- `ORCP 9 A-B`
- `ORCP 10 A-B`
- Working proposition:
  later-filed motions, notices, and similar papers generally must be served on parties; ORCP 10 governs time computation and adds three days after certain service methods.

Use in this workspace:
- supports service and deadline computation for motion packets
- should be read together with chapter 125 where chapter 125 gives more specific notice rules for protective petitions

### 8. Issue preclusion / collateral estoppel

- `Nelson v. Emerald People's Utility Dist., 318 Or 99, 104-06, 862 P2d 1293 (1993)`
- `Rawls v. Evans, 234 Or App 316, 321, 227 P3d 1200 (2010)`
- `Hayes Oyster Co. v. Dulcich, 199 Or App 43, 50, 54, 110 P3d 615, rev den, 339 Or 544 (2005)`
- `Westwood Construction Co. v. Hallmark Inns, 182 Or App 624, 631-32, 637 n 10, 50 P3d 238, rev den, 335 Or 42 (2002)`
- Working proposition:
  Oregon issue preclusion requires a prior separate proceeding and identity of issue, among other elements; it does not apply merely because arguments or phases arise within the same action, and it does not apply when the issues are only similar rather than identical.

Use in this workspace:
- supports the doctrinal frame for the collateral-estoppel branch
- does not eliminate the proof gap concerning the actual prior order / judgment / proceeding record in this matter

## Formal-logic translation notes

The safest current formalization is:
- `AuthorityAvailable(ors_33_055_remedial_contempt_procedure)`
- `AuthorityAvailable(ors_33_075_compel_appearance)`
- `AuthorityAvailable(ors_33_105_remedial_sanctions)`
- `AuthorityAvailable(orcp_17_certification_and_improper_purpose)`
- `AuthorityAvailable(orcp_46_discovery_motion_expenses_and_orders)`
- `AuthorityAvailable(orcp_55_subpoena_obedience_warning)`

These authority objects should support procedural permissions and remedy pathways, not merits findings by themselves.

## Caution

This memo is for logic-grounding and drafting support. Final filing use still requires:
- posture-specific fit checking
- final Oregon citation formatting
- confirmation that the selected remedy path matches the exact probate and nonparty context
