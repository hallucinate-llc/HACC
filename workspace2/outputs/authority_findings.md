# Authority Findings Report

Case Count: `4`
Fully Verified Cases: `1`
Mixed Support Cases: `3`
Paraphrase-Heavy Cases: `1`

## Findings

### live_in_aide_case_001 [info]

- Branch: `constructive_denial`
- Title: Fully verified authority baseline
- Detail: All currently attached authority support is marked as verified_quote.

### live_in_aide_case_effective_accommodation_001 [warning]

- Branch: `effective_accommodation`
- Title: Mixed authority support
- Detail: This case mixes 3 verified quotes with 2 paraphrase supports, so downstream consumers should distinguish direct support from fallback grounding.

### live_in_aide_case_no_violation_001 [warning]

- Branch: `evidentiary_gap`
- Title: Paraphrase-heavy authority support
- Detail: This case uses 3 paraphrase supports and 2 verified quotes, so advocacy and memorandum outputs should be presented as lower-trust authority grounding.

### live_in_aide_case_undue_burden_001 [warning]

- Branch: `undue_burden_constructive_denial`
- Title: Mixed authority support
- Detail: This case mixes 4 verified quotes with 1 paraphrase supports, so downstream consumers should distinguish direct support from fallback grounding.

