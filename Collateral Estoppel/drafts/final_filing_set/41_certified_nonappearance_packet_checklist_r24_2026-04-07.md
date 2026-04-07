# Certified Nonappearance Packet Checklist (r24) - 2026-04-07

Target rule:
- `r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved`

Goal:
- Convert `f_client_solomon_failed_appearance` from `alleged` to `verified` for strict-mode activation.

## Required Certified Components

1. Certified hearing register of actions showing the relevant hearing date and nonappearance entry.
2. Minute order or hearing notes reflecting nonappearance or failure to appear.
3. Proof of service / order-to-appear service record tied to the same hearing event.
4. Identity tie-in (name/case number/date alignment) showing the nonappearance record pertains to Solomon Barber.

## Evidence Integrity Checks

1. Case number matches (`26PR00641` or linked proceeding documented with relation statement).
2. Hearing date in record aligns with modeled date sequence.
3. Service record predates hearing date.
4. Document source is certified court record or authenticated agency return.

## Logic Ingestion Target

- Fact to verify:
  - `f_client_solomon_failed_appearance`
- Rule expected to change:
  - `r24`: unresolved -> active (strict)

## Post-Ingestion Recompute

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Verification Query

```bash
jq '.modes.strict.unresolved_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```

Expected result:
- `r24_case_permitted_seek_compelled_appearance_after_nonappearance_if_proved` no longer listed as unresolved.
