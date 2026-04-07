# Deontic Theorem Workbook (Guardianship Track)

This workbook formalizes initial deontic theorem candidates for Solomon, Jane Cortez, Benjamin Barber, and HACC context. These are modeling statements for drafting logic and must be tied to governing authority before filing use.

## Entity mapping

- `S` = Solomon Barber
- `J` = Jane Cortez
- `B` = Benjamin Barber
- `H` = Housing Authority of Clackamas County (HACC)
- `O1` = asserted prior appointment order
- `O2` = order(s) in case `26PR00641`
- `t` = relevant time index

## Predicate palette

- `ValidOrder(O, t)`
- `Appoints(O, guardian, ward, scope)`
- `Notice(person, O, t)`
- `AvoidedService(person, O, t)`
- `Interference(person, process, t)`
- `HousingProcess(process, H, J, t)`
- `Enforceable(O, t)`

## Modal operators

- `P(x, a)` : x is permitted to do action a
- `O(x, a)` : x is obligated to do action a
- `F(x, a)` : x is forbidden from doing action a

## Theorem candidates

### T1 - Authority from valid appointment

Formal shape:
- `ValidOrder(O1, t) ∧ Appoints(O1, B, J, scope) -> P(B, ActWithinScope(scope, t))`

Interpretation:
- if an appointment order is valid at time `t`, the appointed guardian is permitted to act within order scope.

Proof gate:
- requires the signed appointment order and effective dates.

### T2 - Noninterference after notice

Formal shape:
- `ValidOrder(O1, t) ∧ Notice(actor, O1, t) -> F(actor, InterfereWithScope(O1, t))`

Interpretation:
- once a valid order and notice are shown, interference with authorized scope is prohibited.

Proof gate:
- requires proof of notice or service/evasion evidence.

### T3 - Disregard of enforceable order implies sanctions path

Formal shape:
- `Enforceable(O1, t) ∧ Notice(B, O1, t) ∧ Interference(B, process, t) -> PotentialSanctions(B, t)`

Interpretation:
- disregard/interference after notice of an enforceable order may support sanctions or contempt arguments.

Proof gate:
- requires enforceability timeline + notice evidence + interference evidence.

### T4 - Housing-process interference tie

Formal shape:
- `HousingProcess(process, H, J, t) ∧ Interference(B, process, t) ∧ Enforceable(O1, t) -> RemedialRequestSupport(process, t)`

Interpretation:
- interference with HACC-related housing process during enforceable authority window may support remedial requests.

Proof gate:
- requires housing contract/process records and timeline alignment.

## Contradiction monitor theorem

### T5 - Prior-appointment conflict detector

Formal shape:
- `PetitionStatesNoPriorGuardian(O2) ∧ ClientAssertsPriorAppointment(O1) -> ConflictFlag(PriorGuardianStatus)`

Interpretation:
- this conflict must be resolved before final collateral-estoppel framing.

## Working use rule

Do not convert theorem output into filing-level factual statements until predicates are satisfied by attached documents.
