# Temporal Layer Upgrade Note

The formal reasoning system now carries a basic temporal profile for each rule in addition to its prior single activation-date estimate.

## What changed

For each rule, the generated reasoning artifacts now track:

1. earliest known antecedent date;
2. latest known antecedent date;
3. whether the rule spans multiple dates; and
4. simple temporal tags, such as:
   - `post_notice`
   - `post_order_effective`
   - `within_estimated_order_lifespan`
   - `post_hacc_lease_change`
   - `objection_window_or_later`

## Why this matters

This gives the workspace a stronger way to distinguish:

1. order issuance from later conduct;
2. notice from post-notice conduct;
3. HACC lease-change events from later compelled-production events; and
4. petition notice from objection and hearing-trigger events.

## What it now supports better

The upgraded outputs now make it easier to see, for example, that:

1. Solomon's March 10, 2026 service/effectiveness statements occurred after the November 20, 2025 order became effective;
2. the HACC authority-chain problem spans the January 1, 2026 removal effective date and the January 12, 2026 internal-review / court-documentation communication; and
3. the probate objection rules now visibly sit in the March 31 to April 5, 2026 notice-and-objection window.

## What it still does not do

This is still a first-pass temporal layer. It does not yet fully model:

1. formal intervals with start/end persistence semantics;
2. automatic expiration rules;
3. contradictions based on overlapping time periods; or
4. element-by-element contempt timing analysis such as service date versus conduct date versus hearing date.

## Next best upgrade

The next best temporal upgrade is to add interval objects for:

1. order effective period;
2. notice window;
3. objection window;
4. HACC lease-change sequence; and
5. subpoena service / deficiency / compel sequence.

That would allow the deontic engine to reason not just from sorted dates, but from explicit legal and factual time windows.
