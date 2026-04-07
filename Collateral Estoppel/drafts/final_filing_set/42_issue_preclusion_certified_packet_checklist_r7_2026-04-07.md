# Issue Preclusion Certified Packet Checklist (r7) - 2026-04-07

Target rule:
- `r7_solomon_forbidden_refile_precluded_issue`

Goal:
- Convert `f_collateral_estoppel_candidate` (`theory`) and `f_client_solomon_barred_refile` (`alleged`) into verified strict-mode predicates.

## Required Certified Components

1. Certified prior final judgment/order from separate prior proceeding.
2. Certified docket/register showing finality and parties.
3. Current/re-filed pleading copy showing same issue being relitigated.
4. Identity-of-issue comparison chart (prior issue vs present issue) with record citations.
5. Full-and-fair-opportunity record support (notice, participation/opportunity, or equivalent procedural record).

## Evidence Integrity Checks

1. Prior decision is final and on the relevant issue.
2. Issue identity is specific, not generalized.
3. Party/privity alignment is documented.
4. Full/fair opportunity element has record support.

## Logic Ingestion Targets

- Facts to verify:
  - `f_collateral_estoppel_candidate`
  - `f_client_solomon_barred_refile`
- Rule expected to change:
  - `r7`: unresolved -> active (strict)

## Post-Ingestion Recompute

```bash
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_formal_reasoning_artifacts.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_grounding_gap_report.py"
python3 "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generate_deontic_readiness_dashboard.py"
```

## Verification Query

```bash
jq '.modes.strict.unresolved_rules[]?.rule_id' \
  "/home/barberb/HACC/Collateral Estoppel/knowledge_graph/generated/deontic_reasoning_report.json"
```

Expected result:
- `r7_solomon_forbidden_refile_precluded_issue` no longer listed as unresolved.
