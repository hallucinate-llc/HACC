# Memorandum of Law: live_in_aide_case_effective_accommodation_001

Branch: `effective_accommodation`
Confidence: `0.58`
Authority Trust: `mixed_support`
Source Verified Count: `5`
Source Normalized Count: `5`
Source Status: All listed authorities are sourceVerified and sourceNormalized.
Direct Fit Count: `3`
Analogical Fit Count: `2`
Record-Support Fit Count: `0`
Fit Status: This package includes analogical authority mappings.
Fit Finding: `analogical_support`
Fit Finding Note: This package includes analogical mappings, so the legal fit should be described as mixed direct and analogical support.

This case mixes verified quotes with paraphrase support, so downstream consumers should distinguish direct support from fallback grounding.

## Question Presented

Whether the current record establishes an accommodation violation or instead shows either a functioning accommodation or an evidentiary gap that must be resolved.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:violation

## Summary of Conclusion

Under the present rule set, the memorandum does not conclude a violation on the accepted findings.

The current record reads as a compliance-and-preservation matter, because the accommodation appears to have been implemented in effective form rather than denied.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

Dependency targets: dep:node:violation, dep:node:constructive_denial

## Accepted Facts

The tenant is disabled: True.

A live-in aide is needed: True.

A separate bedroom was requested: True.

The aide was approved in principle: True.

The separate bedroom was denied: False.

The aide sleeps in the living room: False.

Night access is needed: False.

No functional harms were established on the accepted findings.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:disabled_tenant, dep:node:requested_separate_bedroom

## Dependency Graph Analysis

The dependency graph moves from foundational facts into harm findings, then into necessity, reasonableness, duty to grant, effectiveness, constructive denial, and violation.

Active branch: effective_accommodation.

Active outcome: no_violation.

The graph currently stops short of not_effective and constructive_denial because denial and functional harm are not established.

### Section Support

- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): Reasonable accommodation analysis must stay tied to practical housing access. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): Reasonable accommodation analysis must stay tied to practical housing access. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 3:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

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

The current record reads as a compliance-and-preservation matter, because the accommodation appears to have been implemented in effective form rather than denied.

The evaluator confidence score is 0.58.

Authority grounding note: This case mixes verified quotes with paraphrase support, so downstream consumers should distinguish direct support from fallback grounding.

The missing elements remain: functional_harm.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:constructive_denial, dep:node:violation

## Conclusion

Under the present rule set, the memorandum does not conclude a violation on the accepted findings.

### Section Support

- Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): "Imposition of burdensome policies can interfere with disabled persons' right to use and enjoyment of their dwellings." Burdensome housing policies may require accommodation when they interfere with use and enjoyment. [dep:node:violation] [fit=analogical] [sourceVerified sourceNormalized]

Dependency targets: dep:node:violation

## Authorities Relied On

Giebeler v. M&B Associates (343 F.3d 1143 (9th Cir. 2003)): Accommodation rules must bend where necessary for disability-related housing access.

United States v. California Mobile Home Park Management Co. (29 F.3d 1413 (9th Cir. 1994)): Reasonable accommodation doctrine requires case-specific assessment of accessible tenancy arrangements.

McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): Housing-related financial burdens can impair the full use and enjoyment of a dwelling.

HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Equal use and enjoyment requires necessary accommodation changes.

24 CFR 982.316 (24 C.F.R. § 982.316(a)): Program accessibility requires approval of a live-in aide when the accommodation need is established.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316
