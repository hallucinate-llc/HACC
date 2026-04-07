# Deontic Bridge Memo

## Why reuse deontic logic here

The existing HACC workspace already contains a temporal deontic logic model that is useful for this folder because the new dispute also appears to involve:
- role assignments
- duties arising from a legal status or order
- prohibitions on interference
- timeline-sensitive notice and enforcement questions

## Reusable deontic pattern

Prior work modeled:
- obligations: what an actor must do
- permissions: what an actor may do
- prohibitions: what an actor must not do
- triggering events: what activates a duty
- evidence-to-finding links: what supports a conclusion

That same pattern can be reused in a guardianship context.

## Candidate guardianship deontic forms

Possible formal statements to test once documents are collected:
- if a guardianship order exists and is in force, the named guardian may act within the scope of the order
- if a party has notice of the order, that party must not interfere with acts authorized by the order
- if service was valid or evasion is shown, a later claim of ignorance may be weakened
- if a housing contract or application was disrupted in defiance of a valid order, sanctions or contempt theories may become available

## Repeated-pattern bridge

The same modeled pattern may appear across both the guardianship and housing branches:
- a legal status or order is granted
- the affected actor has notice or acts as if they know of the order
- instead of seeking formal relief, the actor continues through collateral channels
- those collateral acts are then used to shape housing, authority, or control outcomes

Candidate cross-branch formulation:
- if `ValidOrder(order, t1)` and `Notice(actor, order, t2)` and `t1 <= t2`, then `F(actor, UseCollateralChannelsToDefeatOrderPurpose)`
- if `F(actor, UseCollateralChannelsToDefeatOrderPurpose)` and `CollateralConversation(actor, org:hacc, subject, t3)`, then `PotentialInterferenceFinding(actor, subject, t3)`
- if `F(actor, UseCollateralChannelsToDefeatOrderPurpose)` and `ReassertedAuthorityClaim(actor, ward_or_case, t3)`, then `PotentialUsurpationFinding(actor, ward_or_case, t3)`

These remain modeling aids. They are useful because the user theory is that the same usurpation pattern repeats:
- granted guardian or guardian-ad-litem-like authority is bypassed and later defended through preclusion positioning
- granted restraining-order boundaries are bypassed through collateral housing communications

## Candidate symbols

- `O(actor, act)` for obligation
- `P(actor, act)` for permission
- `F(actor, act)` for prohibition
- `At(t, fact)` for time-indexed facts
- `Notice(person, order, t)`
- `ValidOrder(order, t)`
- `GuardianAuthority(person, ward, scope, t)`
- `Interference(person, contract_or_process, t)`
- `AvoidedService(person, proceeding, t)`

## Example rule skeletons

- If `ValidOrder(order, t1)` and `Appoints(order, guardian, Jane_Cortez, scope)`, then `P(guardian, ActWithinScope(scope))`.
- If `ValidOrder(order, t1)` and `Notice(person, order, t2)` and `t1 <= t2`, then `F(person, InterfereWith(order_scope))`.
- If `F(person, InterfereWith(order_scope))` and `Interference(person, housing_process, t3)`, then `PotentialSanctions(person, t3)`.

These are only modeling placeholders. They are not legal conclusions until connected to actual authority and facts.
