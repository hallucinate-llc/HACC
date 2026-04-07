# Issue-Preclusion Batch Update And Follow-Up Command Sheet - 2026-04-07

## 1) Dry-run: mark all cases as submitted

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/batch_update_issue_preclusion_request_tracker.py" \
  --cases all \
  --field request_channel \
  --value submitted
```

## 2) Persist: mark all cases as submitted

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/batch_update_issue_preclusion_request_tracker.py" \
  --cases all \
  --field request_channel \
  --value submitted \
  --write
```

## 3) Batch set a shared due date

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/batch_update_issue_preclusion_request_tracker.py" \
  --cases all \
  --field response_due_date \
  --value 2026-04-21 \
  --write
```

## 4) Set one-off case fields with row updater

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field clerk_contact \
  --value "<name/email/phone>" \
  --write
```

## 5) Refresh dashboards and follow-up calendar

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_status_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_next_actions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_followup_calendar.py"
```

## 6) Recompute formal logic layer after any certified intake/mapping update

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_system_gap_refresh.py"
```
