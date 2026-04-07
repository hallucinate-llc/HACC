# Issue-Preclusion Follow-Up Day Command Sheet - 2026-04-07

## 1) Generate send queue for follow-up day (`2026-04-10`)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_followup_send_queue.py" \
  --date 2026-04-10
```

Review queue:
- [65_issue_preclusion_followup_send_queue_2026-04-10.md](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/65_issue_preclusion_followup_send_queue_2026-04-10.md)

## 2) Send messages and log activity

Update log rows in:
- [66_issue_preclusion_followup_send_log_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/66_issue_preclusion_followup_send_log_2026-04-07.csv)

## 3) If a clerk responds, update tracker immediately

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field response_received_date \
  --value 2026-04-10 \
  --write
```

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field notes \
  --value "Clerk acknowledged request; estimated completion pending." \
  --write
```

## 4) Refresh dashboards after updates

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_status_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_next_actions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_daily_action_brief.py"
```

## 5) If certified records are received, push intake + logic refresh

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_system_gap_refresh.py"
```
