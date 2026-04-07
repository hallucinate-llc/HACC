# Certification Sequence Recommendation

Generated: 2026-04-07

Based on `certified_promotion_what_if_scenarios_2026-04-07.md`.

## Highest-yield sequence

1. **Nonappearance packet first**
   - Promote: `f_client_solomon_failed_appearance`
   - Immediate strict effect: activates `r5` and `r24`.
   - Strict counts shift (simulated): `31/6/4` -> `33/4/4`.

2. **Issue-preclusion pair second**
   - Promote: `f_collateral_estoppel_candidate`, `f_client_solomon_barred_refile`
   - Immediate strict effect: activates `r7`.
   - Strict counts shift (from baseline simulation): `31/6/4` -> `32/5/4`.

3. **Prior-appointment cluster third**
   - Promote: `f_client_prior_appointment`, `f_client_benjamin_housing_interference`, `f_client_benjamin_order_disregard`
   - Immediate strict effect: activates `r1`, `r2`, `r3`.
   - Strict counts shift (from baseline simulation): `31/6/4` -> `34/3/4`.

## End state if all three tracks are certified

- Simulated strict counts: `37/0/4`
- All major strict unresolved rules clear (`r1`, `r2`, `r3`, `r5`, `r7`, `r24`).
- Remaining inactive rules are workflow predicates (`r17`, `r18`, `r19`) and design-false `r22`.

## Operational implication

If you need the fastest strict-mode filing lift with the fewest records first, prioritize **nonappearance** before broader issue-preclusion and prior-appointment bundles.
