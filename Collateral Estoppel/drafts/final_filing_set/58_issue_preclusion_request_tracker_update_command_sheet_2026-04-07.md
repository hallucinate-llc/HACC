# Issue-Preclusion Request Tracker Update Command Sheet - 2026-04-07

Use this after updating:
- [57_issue_preclusion_case_request_tracker_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/57_issue_preclusion_case_request_tracker_2026-04-07.csv)
- [45_certified_records_intake_tracker_template_2026-04-07.csv](/home/barberb/HACC/Collateral Estoppel/drafts/final_filing_set/45_certified_records_intake_tracker_template_2026-04-07.csv)

## 1) Validate current issue-preclusion candidate and prefill state

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_evidence_candidates.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_issue_preclusion_mapping_prefill.py"
```

## 2) Recompute full formal/deontic outputs

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_gap_closure_matrix.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_system_gap_refresh.py"
```

## 3) Quick verification queries

```bash
python3 - << "PY"
import json
r='/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json'
o=json.load(open(r))
s=o['modes']['strict']
print('strict_counts',len(s['active_rules']),len(s['unresolved_rules']),len(s['inactive_rules']))
print('r7_state',next((x['rule_id'] for x in s['active_rules'] if x['rule_id']=='r7_solomon_forbidden_refile_precluded_issue'),'not_active'))
PY
```

```bash
python3 - << "PY"
import json
p='/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/issue_preclusion_mapping_prefill_2026-04-07.json'
o=json.load(open(p))
m=o['proposed_mapping_snapshot']
print('mapping_flags',m['identical_issue_mapped'],m['finality_mapped'],m['party_privity_mapped'],m['full_fair_opportunity_mapped'])
PY
```

## 4) Safety reminder

Do not set any `*_mapped` boolean to `true` until certified records are staged and citation-checked.
