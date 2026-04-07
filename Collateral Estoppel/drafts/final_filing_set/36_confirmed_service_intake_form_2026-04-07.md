# Confirmed Service Intake Form - 2026-04-07

Use one block per confirmed service event. Do not enter estimates.

## Recipient Values (must match log exactly)

1. Solomon Barber
2. HACC / Clackamas County Custodian
3. ODHS / APS Custodian
4. Jason Hopkins
5. Tillamook County Sheriff's Office Custodian
6. Tillamook 911 Custodian

## Event Block (copy/paste)

- Recipient (exact):
- Date served (YYYY-MM-DD):
- Service method:
- Person/entity served:
- Production due (YYYY-MM-DD):
- Status after service (`served` or `awaiting_production`):
- Notes (proof reference, process server, return id):

## Single-Event Apply Command

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/apply_confirmed_service_update.py" \
  --recipient "<exact recipient>" \
  --date-served "<YYYY-MM-DD>" \
  --service-method "<method>" \
  --person-served "<served person/entity>" \
  --production-due "<YYYY-MM-DD>" \
  --status "<served|awaiting_production|production_received|deficiency_notice_stage|motion_to_compel_stage>" \
  --notes-append "<proof reference + server details>" \
  --acknowledge "I CONFIRM THESE SERVICE FACTS ARE TRUE"
```

## Recompute Sequence

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

## Verification Check

```bash
jq '.modes.strict.inactive_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```

Target after first confirmed service:
- `r17_responding_custodian_obligated_execute_or_query_protocol_upon_service` should drop from inactive rules.
