# Confirmed Service Entry Command Sheet - 2026-04-07

Use this only after you have confirmed, true service facts.

## Step 1: Apply one confirmed service update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_confirmed_service_update.py" \
  --recipient "REPLACE EXACT RECIPIENT" \
  --date-served "YYYY-MM-DD" \
  --service-method "personal service|substituted service|certified mail|other" \
  --person-served "NAME OR ENTITY SERVED" \
  --production-due "YYYY-MM-DD" \
  --status "awaiting_production" \
  --notes-append "service return ref + who served + proof reference" \
  --acknowledge "I CONFIRM THESE SERVICE FACTS ARE TRUE"
```

Allowed `--status` values:
- `served`
- `awaiting_production`
- `production_received`
- `deficiency_notice_stage`
- `motion_to_compel_stage`

## Step 2: Recompute logic outputs

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

## Step 3: Verify `r17` activation

```bash
jq '.modes.strict.inactive_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```

Expected after first confirmed service event:
- `r17` should no longer appear in `inactive_rules`.

## Optional quick count check

```bash
jq '{strict:{active:(.modes.strict.active_rules|length),unresolved:(.modes.strict.unresolved_rules|length),inactive:(.modes.strict.inactive_rules|length)},inclusive:{active:(.modes.inclusive.active_rules|length),unresolved:(.modes.inclusive.unresolved_rules|length),inactive:(.modes.inclusive.inactive_rules|length)}}' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```
