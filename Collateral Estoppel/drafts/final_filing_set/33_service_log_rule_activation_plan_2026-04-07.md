# Service Log Rule Activation Plan - 2026-04-07

Purpose: convert the current all-`ready_to_serve` queue into a tracked enforcement sequence that activates workflow rules `r17`, then `r18`, then `r19`.

Current computed state (from strict mode):
- `r17_responding_custodian_obligated_execute_or_query_protocol_upon_service`: inactive
- `r18_benjamin_permitted_issue_deficiency_notice_after_incomplete_subpoena_response`: inactive
- `r19_benjamin_permitted_move_to_compel_after_deficiency_notice_stage`: inactive

## Rule Activation Conditions

1. `r17` activates when:
- `f_subpoena_service_completed_any = true`
- `f_or_joined_search_protocol_defined = true` (already true)

2. `r18` activates when:
- `f_subpoena_response_incomplete_any = true`
- `f_subpoena_workflow_components_staged = true` (already true)

3. `r19` activates when:
- `f_deficiency_notice_sent_any = true`
- `f_subpoena_workflow_components_staged = true` (already true)

## Data Entry Protocol (28_active_service_log_2026-04-07.csv)

For each recipient row, use this sequence:

1. Service completed:
- Set `status=served` (or `awaiting_production`)
- Set `date_served=YYYY-MM-DD`
- Set `service_method`
- Set `person_served`
- Set `production_due=YYYY-MM-DD`
- Add return details in `notes`

2. Await production:
- Keep `status=awaiting_production` after service if production not yet received.

3. Production received:
- Set `date_production_received=YYYY-MM-DD`
- Set checklist/report flags:
- `checklist_received=Y|N`
- `search_report_received=Y|N`
- `privilege_log_received=Y|N`

4. Deficiency stage (if incomplete):
- Set `status=deficiency_notice_stage`
- Set `deficiency_notice_sent=YYYY-MM-DD`
- Set `cure_deadline=YYYY-MM-DD`
- Record missing items in `notes`

5. Cure tracking:
- If cured, set `cure_received=YYYY-MM-DD`
- If still incomplete, move to compel stage.

6. Motion-to-compel stage:
- Set `status=motion_to_compel_stage`
- Set `motion_to_compel_filed=YYYY-MM-DD`

## Recipient-by-Recipient Next Actions

1. Solomon Barber (`Manifest A`)
- Next status: `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

2. HACC / Clackamas County Custodian (`Manifest B`)
- Next status: `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

3. ODHS / APS Custodian (`Manifest C`)
- Confirm unit/attention line first, then set `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

4. Jason Hopkins (`Manifest D`)
- Serve at documented work-service endpoint(s), then set `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

5. Tillamook County Sheriff's Office Custodian (`Manifest E`)
- Next status: `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

6. Tillamook 911 Custodian (`Manifest F`)
- Next status: `served`
- Immediate fields: `date_served`, `service_method`, `person_served`, `production_due`

## Minimum Rule Activation Milestones

1. To activate `r17` now:
- At least one row must show completed service (`status` in served/awaiting/production/deficiency/compel path, or `date_served` populated).

2. To activate `r18`:
- At least one served row must show incomplete response (`awaiting_production`, `deficiency_notice_stage`, `motion_to_compel_stage`, or missing checklist/search report flags after service).

3. To activate `r19`:
- At least one row must show deficiency notice sent (`status=deficiency_notice_stage` or `deficiency_notice_sent` populated).

## Recompute Sequence After Each Update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/validate_service_log_and_emit_deontic_inputs.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_proof_intake_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_support_map.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_motion_paragraph_bank.py"
```

## Output Checkpoints

Confirm updates in:
- `knowledge_graph/generated/deontic_reasoning_report.json`
- `knowledge_graph/generated/proof_intake_map_2026-04-07.json`
- `knowledge_graph/generated/service_log_validation_report_2026-04-07.json`

Expected movement after first completed service:
- `r17`: inactive -> active
- `r18`: remains inactive until incomplete response signal appears
- `r19`: remains inactive until deficiency notice signal appears
