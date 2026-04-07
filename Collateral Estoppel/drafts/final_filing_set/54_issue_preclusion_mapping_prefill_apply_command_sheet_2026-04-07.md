# Issue-Preclusion Prefill Apply Command Sheet

Generated: 2026-04-07

Review first:
```bash
sed -n "1,260p" "/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/53_issue_preclusion_mapping_prefill_review_packet_2026-04-07.md"
sed -n "1,220p" "/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json"
```

Optional apply (manual review strongly recommended):
```bash
python3 - << "PY"
import json
pref=json.load(open("/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/issue_preclusion_mapping_prefill_2026-04-07.json"))
target="/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json"
snapshot=pref["proposed_mapping_snapshot"]
open(target,"w",encoding="utf-8").write(json.dumps(snapshot,indent=2)+"\n")
print(target)
PY
```

Recompute after any mapping edit:
```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
```
