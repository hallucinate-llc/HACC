# Formal Case State Dashboard

This dashboard summarizes which formal-logic branches are presently filing-ready, which remain proof-gated, and what exact file, record, or workflow event would promote each branch.

## 1. Filing-ready now

### A. Remedial contempt / show-cause timing branch

- Status: substantially filing-ready
- Why:
  - valid order verified
  - notice verified
  - post-notice conduct verified
- Current remaining caution:
  - a cleaner certified service / appearance / docket record would strengthen filing-grade contempt support
- Promotion trigger:
  - stage certified appearance or docket materials in the record set if available

### B. Probate objection / hearing branch

- Status: filing-ready
- Why:
  - notice issued verified
  - objection presented verified
  - hearing-required path verified
- Promotion trigger:
  - none required for baseline objection/hearing posture

### C. HACC authority-chain / Exhibit R production branch

- Status: filing-ready for subpoena / compelled-production posture
- Why:
  - local negative search verified
  - compelled-production need verified
  - nonparty production packet already staged
- Current remaining caution:
  - actor attribution is still not proved
- Promotion trigger:
  - service of the subpoena packet

## 2. Proof-gated now

### A. Issue-preclusion merits branch

- Status: doctrine grounded, application proof-gated
- Why:
  - doctrine grounded verified
  - candidate barred-refile theory only proof-gated
  - prior separate proceeding record still missing
  - element mapping not yet completed
- Promotion triggers:
  - add certified prior-order material to [README.md](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/README.md)’s staging folder
  - add certified docket / register material to that folder
  - add hearing / appearance material to that folder
  - complete [issue_preclusion_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/issue_preclusion_mapping.json)

### B. ORCP 17 sanctions merits branch

- Status: authority grounded, filing-specific proof still gated
- Why:
  - sanctions authority verified
  - proof-state caution verified
  - no challenged filing has yet been formally mapped
  - no improper-purpose / unsupported-law / unsupported-fact mapping has yet been completed
- Promotion triggers:
  - complete [orcp17_filing_mapping.json](/home/barberb/HACC/Collateral%20Estoppel/evidence_notes/certified_records/orcp17_filing_mapping.json)

### C. Direct Solomon-to-HACC interference attribution branch

- Status: inference-level only
- Why:
  - HACC lease-change basis verified
  - actor-identification record still missing
  - named Solomon-to-HACC notice chain not directly proved from preserved mail
- Promotion triggers:
  - production of the HACC actor / document / authority-chain record through `Exhibit R`

## 3. Workflow-open now

### A. Exhibit R subpoena workflow

- Status: staged but not yet served
- Current audit posture:
  - `pre_service_only`: verified
  - `service_stage_complete`: missing
  - `deficiency_or_compel_stage`: missing
- Promotion triggers:
  - log service in [28_active_service_log_2026-04-07.csv](/home/barberb/HACC/Collateral%20Estoppel/drafts/final_filing_set/28_active_service_log_2026-04-07.csv)
  - later log any deficiency notice or compel stage in the same file

### B. Certified prior-proceeding audit hook

- Status: enabled but dormant
- Current audit posture:
  - certified prior-order material: absent
  - certified docket material: absent
  - certified hearing material: absent
- Promotion triggers:
  - place appropriately named files in `/home/barberb/HACC/Collateral Estoppel/evidence_notes/certified_records`

## 4. Strongest next moves

If the goal is to improve filing posture fastest, the highest-value next events are:

1. serve the Exhibit R nonparty HACC packet and update the active service log;
2. obtain or stage certified prior-proceeding materials for the issue-preclusion branch;
3. complete the issue-preclusion mapping manifest once those materials exist; and
4. identify the specific filing to target in the `ORCP 17` manifest and map the sanctions predicates there.
