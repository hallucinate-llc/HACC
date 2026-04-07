# Issue-Preclusion Clerk Contact Verification Queue - 2026-04-07

Purpose:
- Fill the `clerk_contact` field in the issue-preclusion tracker with verified, case-usable contact details before follow-up dates begin.

Tracker source:
- [57_issue_preclusion_case_request_tracker_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv)

## Verification targets (all currently submitted)

1. `26PR00641` - contact needed
2. `25PO11530` - contact needed
3. `26P000432` - contact needed
4. `26P000433` - contact needed

## Contact data standard (enter in tracker `clerk_contact`)

Use this format:
- `Name | Office/Division | Email | Phone | VerificationDate`

Example:
- `Jane Doe | Clackamas Circuit Court Records | records@example.org | 503-000-0000 | 2026-04-07`

## Verification checklist per case

1. Confirm office (Clerk/Records/Probate as appropriate).
2. Confirm preferred request channel (email, portal, in-person, mail).
3. Confirm whether case-number-specific routing is required.
4. Record contact and date in `clerk_contact` field.

## Update commands (example)

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/update_issue_preclusion_request_tracker_row.py" \
  --case-number 26PR00641 \
  --field clerk_contact \
  --value "<Name | Office | Email | Phone | 2026-04-07>" \
  --write
```

## Recompute dashboard after updates

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_contact_completion_dashboard.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_request_next_actions.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_followup_calendar.py"
```
