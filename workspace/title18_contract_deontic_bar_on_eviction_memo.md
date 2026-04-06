# Title 18 And Contract Deontic Logic Memo Re Why HACC Was Barred From Filing Eviction

## Bottom Line

Yes. Using the current Section 18 and contract findings, the cleanest deontic logic is that HACC was not merely expected to do certain things before eviction. HACC was **obligated** to complete core relocation steps and **forbidden** from filing eviction while those steps remained incomplete.

In deontic terms:

- `O(HACC, complete triggered relocation duties before displacement is treated as complete)`
- `O(HACC, provide counseling, comparable replacement housing, and relocation support once the process is triggered)`
- `O(HACC, carry through the specific relocation / replacement-housing path it directed the household to use)`
- `F(HACC, file eviction while those duties remain materially unperformed)`

That prohibition is supported two different ways at once:

1. `public-law / Title 18 side`
2. `private-law / contract and implied-contract side`

Those two layers reinforce each other.

## I. Title 18 Deontic Structure

The existing Section 18 analysis already states the core prohibition in source-linked form.

From [title18_breach_report.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_breach_report.json):

- finding `breach:hacc:premature_eviction`
- rule: `A PHA may not evict before completing triggered Section 18 relocation duties.`
- legal basis on the obligation node: `42 U.S.C. 1437p(d) read against the recorded eviction and relocation timeline`

So the first deontic statement is:

- `O1`: `O(HACC, complete Section 18 relocation duties once triggered)`
- `F1`: `F(HACC, evict before relocation duties are completed)`

The same report adds the component duties:

- `O2`: `O(HACC, provide relocation counseling before displacement)`
- `O3`: `O(HACC, pay or commit relocation moving expenses)`
- `O4`: `O(HACC, offer comparable replacement housing)`

Those come from findings:

- `breach:hacc:relocation_services`
- `breach:hacc:inaccessible_replacement_offer`

So the barred-eviction logic is not abstract. It works like this:

1. Section 18 relocation was triggered.
2. Triggering created affirmative duties.
3. Those duties were still materially incomplete.
4. Therefore the prohibition on premature eviction was still in force.

In compact deontic form:

```text
triggered_section18_relocation(HACC, household)
  -> O(relocation_counseling)
  & O(relocation_expense_support)
  & O(comparable_replacement_housing)

not completed(relocation_counseling)
or not completed(relocation_expense_support)
or not completed(comparable_replacement_housing)
  -> F(file_eviction)
```

## II. Contract And Implied-Contract Deontic Structure

The contract side makes the same point from a second angle.

From [contract_breach_report.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/contract_breach_report.json):

- `contract:hacc:relocation_commitment`
- `implied_contract:hacc:relocation_process`
- `promissory_estoppel:hacc:relocation_reliance`

The strongest line in the contract report is:

- HACC `put the household into a specific relocation transaction and then failed to carry that transaction through before suing for possession`

That gives the second deontic layer:

- `O5`: `O(HACC, perform the relocation commitment it undertook)`
- `O6`: `O(HACC, administer the implied relocation-process agreement with continuity and ordinary care)`
- `F2`: `F(HACC, terminate the household's possession rights on the theory of nonperformance while HACC's own undertaken relocation performance remains unfinished)`

This matters because even if HACC tried to argue:

- “this is only a statutory issue,”

the contract side says:

- “no, HACC also undertook a household-specific process and induced reliance on it.”

That means filing eviction before carrying through the process is not just statutory noncompliance. It is also inconsistent with HACC's own undertaken performance obligations.

## III. The Combined Deontic Bar

The strongest version uses both layers together.

### Public-law side

- Section 18 imposed a relocation-before-displacement structure.

### Undertaking side

- HACC then concretized that structure by directing this household into specific replacement-housing paths:
  - Blossom / Hillside Manor
  - Waterleaf / Multnomah portability

So once both are true, the bar is stronger:

```text
Section18_triggered
and HACC_directed_specific_relocation_path
and household_substantially_performed_that_path
and HACC_left_path_incomplete
  -> F(HACC, file_eviction_as_if_household_defaulted)
```

That is the cleanest deontic expression of the theory.

## IV. Why This Is Better Than Saying Only “Eviction Was Unfair”

This framing is stronger because it distinguishes:

- `discretionary choices`
from
- `conditions precedent to lawful displacement`

Under this theory, HACC was not free to say:

- “we can still evict now, and sort out relocation later.”

Instead, the logic is:

- relocation completion duties were a prerequisite condition;
- HACC had not satisfied them;
- therefore eviction was not yet normatively permitted.

So the deontic relation is not merely:

- `O(HACC, do relocation well)`

It is:

- `F(HACC, file eviction before relocation completion)`

That is the more powerful proposition.

## V. Role Of Household Performance

This theory also gets stronger because the current record does **not** strongly support that Benjamin Barber or Jane Cortez materially breached the application or cooperation path.

From [title18_breach_report.json](/home/barberb/HACC/Breach%20of%20Contract/outputs/title18_breach_report.json):

- `no_breach:household:submission_duty`
- current disposition: `no_current_breach_shown`

That means the deontic defense is not:

- “HACC had duties, but the household defaulted first.”

The current formal record instead supports:

- the household substantially performed enough to keep HACC's duties live;
- HACC and Quantum then failed on the processing side.

So the stronger deontic inference is:

```text
substantial_performance(household)
and noncompletion(hacc_relocation_duties)
  -> prohibition_on_eviction_remains
```

## VI. Best Litigation Sentence

If you want the shortest strong sentence for a motion or memorandum, it is:

`Once Section 18 relocation duties were triggered, and once HACC directed the Barber-Cortez household into specific replacement-housing and portability paths, HACC was not merely expected but legally obligated to complete those relocation steps before displacement was treated as complete, and was correspondingly barred from filing eviction while counseling, comparable replacement housing, intake processing, and related relocation performance remained materially unfinished.`

## VII. Best Short Deontic Formula

```text
O(HACC, complete triggered Section 18 relocation duties)
O(HACC, perform undertaken relocation-process commitments)
not completed(triggered relocation duties)
  -> F(HACC, file eviction)
```

## VIII. Main Caveat

The safest version is:

- `barred from filing eviction before relocation completion`

not necessarily:

- `every later eviction filing is forever impossible`

The prohibition is tied to the state of the duties at the time of filing. On the current record, that is exactly why the March 2026 eviction theory is strong: the relocation path was still incomplete when HACC moved toward possession.
