# Accommodation Rules

## Evidence model
The evaluator now distinguishes between:
- `assertedFacts`: what a party claims
- `acceptedFindings`: what the system currently treats as established for reasoning

If an `acceptedFindings` field is present, it overrides the corresponding asserted fact for rule evaluation.

## Implemented rules
1. `sleep_interruption`
   - true when the aide sleeps in the living room and night access is needed
2. `work_interference`
   - true when sleep interruption exists and the aide works remotely
3. `caregiving_impairment`
   - true when sleep interruption exists
4. `privacy_loss`
   - true when the fixture marks privacy loss or when the aide sleeps in the living room
5. `necessary`
   - true when any of sleep interruption, work interference, caregiving impairment, or privacy loss is true
6. `reasonable`
   - true when medical verification and necessity are true and no defenses apply
7. `duty_to_grant`
   - true when the tenant is disabled, needs a live-in aide, requested a separate bedroom, and the accommodation is reasonable
8. `not_effective`
   - true when the separate bedroom is denied and sleep interruption exists
9. `constructive_denial`
   - true when the aide was approved in principle, the separate bedroom was denied, and the resulting arrangement is not effective
10. `violation`
   - true when there is either a denied duty-to-grant or constructive denial

## Authority attachment
The evaluator also groups the supplied authorities into support buckets such as:
- `necessary`
- `reasonable`
- `dutyToGrant`
- `constructiveDenial`
- `violation`

This is still heuristic, but it gives us a place to hang provenance for later weighting.

## Deliberate MVP limits
- no probabilistic authority weighting yet
- no time model yet
- no conflict-resolution policy beyond accepted-finding override
