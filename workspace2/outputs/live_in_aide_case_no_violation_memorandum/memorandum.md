# Memorandum of Law: live_in_aide_case_no_violation_001

Branch: `evidentiary_gap`
Confidence: `0.57`
Authority Trust: `paraphrase_heavy`
Source Verified Count: `5`
Source Normalized Count: `5`
Source Status: All listed authorities are sourceVerified and sourceNormalized.
Direct Fit Count: `1`
Analogical Fit Count: `1`
Record-Support Fit Count: `3`
Fit Status: This package includes analogical authority mappings.
Fit Finding: `record_support_heavy`
Fit Finding Note: This package relies in part on record-support mappings, so direct controlling authority should be distinguished from factual or background support.

This case relies heavily on paraphrase support, so downstream consumers should present the authority grounding as lower-trust.

## Question Presented

Whether the current record establishes an accommodation violation or instead shows either a functioning accommodation or an evidentiary gap that must be resolved.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:violation

## Summary of Conclusion

Under the present rule set, the memorandum does not conclude a violation on the accepted findings.

The current record is not yet mature enough to support a finished denial theory, so the memorandum should emphasize factual development and clarification of the accommodation's practical operation.

Dependency targets: dep:node:violation, dep:node:constructive_denial

## Accepted Facts

The tenant is disabled: True.

A live-in aide is needed: True.

A separate bedroom was requested: True.

The aide was approved in principle: True.

The separate bedroom was denied: True.

The aide sleeps in the living room: False.

Night access is needed: False.

No functional harms were established on the accepted findings.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:disabled_tenant, dep:node:requested_separate_bedroom

## Dependency Graph Analysis

The dependency graph moves from foundational facts into harm findings, then into necessity, reasonableness, duty to grant, effectiveness, constructive denial, and violation.

Active branch: evidentiary_gap.

Active outcome: no_violation.

The graph currently stops before violation because the record does not establish the harm and effectiveness predicates needed to complete the path.

### Section Support

- McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Giebeler v. M&B Associates (9th Cir., 2003, 1155): Accommodation analysis should stay connected to disability-related housing access. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
- United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): Accommodation disputes should be evaluated against a concrete factual record. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
- HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]

### Paragraph Support

- Paragraph 1:
  - McGary v. City of Portland (9th Cir., 2004, 1265): "The lien the City put on McGary's house prevents the full use and enjoyment of his property." Housing-related financial burdens can impair the full use and enjoyment of a dwelling. [dep:node:necessary] [fit=analogical] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:necessary] [fit=direct] [sourceVerified sourceNormalized]
- Paragraph 2:
  - Giebeler v. M&B Associates (9th Cir., 2003, 1155): Accommodation analysis should stay connected to disability-related housing access. [dep:node:reasonable] [fit=analogical] [sourceVerified sourceNormalized]
  - United States v. California Mobile Home Park Management Co. (9th Cir., 1994, 1416): Accommodation disputes should be evaluated against a concrete factual record. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]
  - HUD/DOJ Joint Statement on Reasonable Accommodations (HUD/DOJ, 2004, Question 1, p. 2): "Reasonable accommodations may be necessary to afford a person with a disability equal opportunity to use and enjoy a dwelling." Equal use and enjoyment may require necessary accommodation changes. [dep:node:reasonable] [fit=direct] [sourceVerified sourceNormalized]

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

The current record is not yet mature enough to support a finished denial theory, so the memorandum should emphasize factual development and clarification of the accommodation's practical operation.

The evaluator confidence score is 0.57.

Authority grounding note: This case relies heavily on paraphrase support, so downstream consumers should present the authority grounding as lower-trust.

The missing elements remain: functional_harm.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316

Dependency targets: dep:node:constructive_denial, dep:node:violation

## Conclusion

Under the present rule set, the memorandum does not conclude a violation on the accepted findings.

Dependency targets: dep:node:violation

## Authorities Relied On

Giebeler v. M&B Associates (343 F.3d 1143 (9th Cir. 2003)): Accommodation analysis should remain tied to disability-related housing access and a sufficiently developed factual record.

United States v. California Mobile Home Park Management Co. (29 F.3d 1413 (9th Cir. 1994)): Administrative review should identify the requested accommodation and the factual gaps in the record before the matter hardens into a denial dispute.

McGary v. City of Portland (386 F.3d 1259 (9th Cir. 2004)): Housing-related financial burdens can impair the full use and enjoyment of a dwelling.

HUD/DOJ Joint Statement on Reasonable Accommodations (Joint Statement of the Department of Housing and Urban Development and the Department of Justice, Reasonable Accommodations under the Fair Housing Act (May 2004)): Equal use and enjoyment requires necessary accommodation changes.

24 CFR 982.316 (24 C.F.R. § 982.316(a)): Program accessibility requires approval of a live-in aide when the accommodation need is established.

Authorities: giebeler, california_mobile_home, mcgary, hud_joint_statement, cfr_982_316
