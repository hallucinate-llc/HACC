# Issue-Preclusion Tracker Row Update Command Sheet - 2026-04-07

Use this helper script:
- `python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py"`

Dry-run is default. Add `--write` to persist.

## 1) Mark request submitted (example: 26PR00641)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field request_channel \
  --value submitted
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field request_channel \
  --value submitted \
  --write
```

## 2) Record clerk contact and due date

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field clerk_contact \
  --value "<name/email/phone>" \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field response_due_date \
  --value 2026-04-21 \
  --write
```

## 3) Mark records received and intake logged

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field response_received_date \
  --value 2026-04-18 \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field certified_records_received \
  --value yes \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field intake_logged \
  --value yes \
  --write
```

## 4) Mark element-completion flags after citation review

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field finality_records_complete \
  --value yes \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field opportunity_records_complete \
  --value yes \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field party_identity_records_complete \
  --value yes \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field mapping_updated \
  --value yes \
  --write
```

## 5) Refresh status dashboards

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_status_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_next_actions.py"
```
