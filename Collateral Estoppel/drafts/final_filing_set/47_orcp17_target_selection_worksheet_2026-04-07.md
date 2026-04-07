# ORCP 17 Target Selection Worksheet - 2026-04-07

Use this worksheet before turning the `ORCP 17` mapping file into a filing-specific sanctions theory.

## Current recommended first target

- Filing: Solomon Barber first amended guardianship petition
- Date anchor: March 31, 2026
- Primary source: [solomon_motion_for_guardianship_ocr.txt](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/solomon_motion_for_guardianship_ocr.txt)

## Step 1. Confirm filing identity

Record into:

- [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)

Fields to fill first:

1. `challenged_filing_caption`
2. `challenged_filing_date`
3. `challenged_filing_identified`
4. `challenged_filing_note`

## Step 2. Decide whether to map sanctions predicates now

Do not set the remaining booleans to `true` unless you can tie them to the filing with record support:

1. `improper_purpose_mapped`
2. `unsupported_legal_position_mapped`
3. `unsupported_factual_assertion_mapped`

## Step 3. Preserve proof-state discipline

Safe current formulation:

- the filing is the present candidate target for `ORCP 17` review

Unsafe current formulation:

- the filing has already been proved sanctionable under `ORCP 17`

## Step 4. Recompute after any update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

Then check:

1. [formal_case_state_dashboard.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/formal_case_state_dashboard.md)
2. [deontic_reasoning_report.md](/home/barberb/HACC/Collateral%20Estoppel/knowledge_graph/generated/deontic_reasoning_report.md)
