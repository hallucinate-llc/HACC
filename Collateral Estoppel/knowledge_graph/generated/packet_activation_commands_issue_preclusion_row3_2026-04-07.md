# First Packet Activation Commands

Generated: 2026-04-07
Row: 3
Case number: 26PR00641
File path: /home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md
File exists now: True

## 1) Dry-run row confirmation
```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" \\
  --row 3 \\
  --file-path "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md" \\
  --case-number "26PR00641"
```

## 2) Persist row confirmation
```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/confirm_certified_intake_row.py" \\
  --row 3 \\
  --file-path "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/42_issue_preclusion_certified_packet_checklist_r7_2026-04-07.md" \\
  --case-number "26PR00641" \\
  --write
```

## 3) Apply certified intake promotion pipeline
```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/run_certified_intake_promotion_pipeline.py" \\
  --apply \\
  --acknowledge "I CONFIRM CERTIFIED INTAKE SUGGESTIONS ARE VERIFIED"
```

## 4) Verify outcomes
```bash
sed -n "1,220p" "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/certified_intake_promotion_pipeline_status_2026-04-07.md"
python3 - << "PY"
import json
p = "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
o = json.load(open(p))
s = o["modes"]["strict"]
print("strict", len(s["active_rules"]), len(s["unresolved_rules"]), len(s["inactive_rules"]))
print("status_or_value_changes", o.get("fact_override_summary", {}).get("applied_status_or_value_changes"))
PY
```
