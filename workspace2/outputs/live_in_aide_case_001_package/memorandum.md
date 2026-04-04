# Memorandum of Law: live_in_aide_case_001

Branch: `constructive_denial`
Confidence: `0.93`
Authority Trust: `fully_verified`
Source Verified Count: `5`
Source Normalized Count: `5`
Source Status: All listed authorities are sourceVerified and sourceNormalized.
Direct Fit Count: `3`
Analogical Fit Count: `2`
Record-Support Fit Count: `0`
Fit Status: This package includes analogical authority mappings.
Fit Finding: `analogical_support`
Fit Finding Note: This package includes analogical mappings, so the legal fit should be described as mixed direct and analogical support.

All currently attached authority support is marked as verified_quote.

## Question Presented

Whether the housing provider violated its accommodation duties by denying, or constructively denying, a separate-bedroom accommodation for the live-in aide.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
- 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
  - 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:violation

## Summary of Conclusion

Under the present rule set, the memorandum concludes that the accommodation duty was violated.

The strongest memorandum position is that the provider constructively denied an accommodation by approving the aide in principle while denying the separate bedroom required for effective use and enjoyment.

### Section Support

- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:constructive_denial] [fit=direct] [sourceVerified sourceNormalized]
- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
- 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:constructive_denial] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
  - 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

Authorities: california_mobile_home, cfr_982_316, giebeler

Dependency targets: dep:node:violation, dep:node:constructive_denial

## Accepted Facts

The tenant is disabled: True.

A live-in aide is needed: True.

A separate bedroom was requested: True.

The aide was approved in principle: True.

The separate bedroom was denied: True.

The aide sleeps in the living room: True.

Night access is needed: True.

Accepted functional harms: sleep interruption, work interference, caregiving impairment, privacy loss.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:disabled_tenant, dep:node:requested_separate_bedroom

## Dependency Graph Analysis

The dependency graph moves from foundational facts into harm findings, then into necessity, reasonableness, duty to grant, effectiveness, constructive denial, and violation.

Active branch: constructive_denial.

Active outcome: violation.

The graph is currently anchored on the path approved_aide_in_principle -> constructive_denial -> violation.

### Section Support

- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 3:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
  - 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:necessary, dep:node:reasonable, dep:node:violation

## Authority Grounding

node:necessary is grounded by McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): The lien the City put on McGary's house prevents the full use and enjoyment of his property.

edge:sleep_interruption->necessary is grounded by McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): The lien the City put on McGary's house prevents the full use and enjoyment of his property.

edge:work_interference->necessary is grounded by McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): The lien the City put on McGary's house prevents the full use and enjoyment of his property.

edge:caregiving_impairment->necessary is grounded by McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): The lien the City put on McGary's house prevents the full use and enjoyment of his property.

edge:privacy_loss->necessary is grounded by McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): The lien the City put on McGary's house prevents the full use and enjoyment of his property.

node:necessary is grounded by HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling.

edge:sleep_interruption->necessary is grounded by HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling.

edge:work_interference->necessary is grounded by HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling.

### Section Support

- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:sleep_interruption->necessary] [fit=analogical] [sourceVerified sourceNormalized]
- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:work_interference->necessary] [fit=analogical] [sourceVerified sourceNormalized]
- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:caregiving_impairment->necessary] [fit=analogical] [sourceVerified sourceNormalized]
- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:privacy_loss->necessary] [fit=analogical] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:caregiving_impairment->necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:edge:caregiving_impairment->necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:privacy_loss->necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:edge:privacy_loss->necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 3:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:sleep_interruption->necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:edge:sleep_interruption->necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 4:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:edge:work_interference->necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:edge:work_interference->necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 5:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:necessary, dep:edge:sleep_interruption->necessary, dep:edge:work_interference->necessary, dep:edge:caregiving_impairment->necessary, dep:edge:privacy_loss->necessary, dep:node:necessary, dep:edge:sleep_interruption->necessary, dep:edge:work_interference->necessary

## Application

The strongest memorandum position is that the provider constructively denied an accommodation by approving the aide in principle while denying the separate bedroom required for effective use and enjoyment.

The evaluator confidence score is 0.93.

Authority grounding note: All currently attached authority support is marked as verified_quote.

The current record does not identify missing elements in the implemented rule path.

### Section Support

- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:constructive_denial] [fit=direct] [sourceVerified sourceNormalized]
- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
- 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:constructive_denial] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
  - 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:constructive_denial, dep:node:violation

## Conclusion

Under the present rule set, the memorandum concludes that the accommodation duty was violated.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
- 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): "The FHAA imposes an affirmative duty upon landlords reasonably to accommodate the needs of handicapped persons." Reasonable accommodation may require landlords to shoulder reasonable financial burdens. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]
  - 24 CFR 982.316 (24 C.F.R., current, (a)): "The PHA must approve a live-in aide if needed as a reasonable accommodation." A PHA must approve a live-in aide when needed as a reasonable accommodation. [dep:node:violation] [fit=direct] [sourceVerified sourceNormalized]

Authorities: california_mobile_home, cfr_982_316, giebeler

Dependency targets: dep:node:violation

## Authorities Relied On

Giebeler v. M&B Associates (343 F.3d 1143 (9th Cir. 2003)): Accommodation rules must bend where necessary for disability-related housing access.

United States v. California Mobile Home Park Management Co. (29 F.3d 1413 (9th Cir. 1994)): Refusal of reasonable accommodation can violate the FHA.

McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): Housing-related financial burdens can impair the full use and enjoyment of a dwelling.

HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Equal use and enjoyment requires necessary accommodation changes.

24 CFR 982.316 (24 C.F.R. § 982.316(a)): PHAs must allow a live-in aide when needed as a reasonable accommodation.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316
