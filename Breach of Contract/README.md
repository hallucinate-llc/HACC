# Breach of Contract

This directory contains the Title 18 demolition/relocation analysis pipeline, downstream filing artifacts, and the earlier legal reasoning prototype materials.

## Title 18 Packet Regeneration

The Title 18 filing set can now be regenerated from a single override file:

- Edit `title18_render_context_overrides.json` with case-specific values.
- Run one of the wrapper commands below from this directory.

HACC-oriented merged packet and final packet set:

```bash
cd "/home/barberb/HACC/Breach of Contract"
bash ./regen_title18_hacc.sh
```

Equivalent `make` target:

```bash
cd "/home/barberb/HACC/Breach of Contract"
make regen-hacc
```

Quantum-oriented merged packet and final packet set:

```bash
cd "/home/barberb/HACC/Breach of Contract"
bash ./regen_title18_quantum.sh
```

Equivalent `make` target:

```bash
cd "/home/barberb/HACC/Breach of Contract"
make regen-quantum
```

Direct Python entry point if you want to pass the merged track yourself:

```bash
cd "/home/barberb/HACC/Breach of Contract"
python3 -m formal_logic.title18_regenerate_packets --merged-order-track hacc
python3 -m formal_logic.title18_regenerate_packets --merged-order-track quantum
```

The most useful outputs after regeneration are:

- `outputs/title18_hacc_final_packet.md`
- `outputs/title18_quantum_final_packet.md`
- `outputs/title18_filing_index.md`
- `outputs/title18_render_context.json`

VS Code users can also run the tasks `Regenerate Title18 HACC Packet` and `Regenerate Title18 Quantum Packet` from the command palette or tasks runner.

Below is the earlier workspace2 prototype documentation preserved in place.

# workspace2

This directory contains an MVP legal reasoning prototype derived from the extracted shared chat.

Current scope:
- one domain schema for a live-in-aide accommodation dispute
- four sample case fixtures with authority metadata
- authority records can now carry `court`, `year`, `pincite`, `sourceUrl`, `excerptText`, `excerptKind`, and `proposition`
- one rule-based evaluator
- one explanation/proof-trace output path
- one advocacy-output generator
- one memorandum/PDF generator with dependency-graph citation grounding
- one asserted-facts vs accepted-findings split
- dependency-free regression checks

Start here:
- `docs/implementation_plan.md`
- `docs/output_modes.md`
- `fixtures/live_in_aide_case.json`
- `fixtures/live_in_aide_case_effective_accommodation.json`
- `fixtures/live_in_aide_case_no_violation.json`
- `fixtures/live_in_aide_case_undue_burden.json`
- `engine/evaluate_case.py`

## Run
Print a result:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/evaluate_case.py fixtures/live_in_aide_case.json
```

Write a result file:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/evaluate_case.py fixtures/live_in_aide_case.json --write
```

Generate advocacy-oriented draft outputs:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/generate_advocacy.py fixtures/live_in_aide_case.json
```

Write advocacy-oriented draft outputs:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/generate_advocacy.py fixtures/live_in_aide_case.json --write
```

Write memorandum outputs, including PDF and JSON-LD grounding:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/generate_memorandum.py fixtures/live_in_aide_case.json --write
```

Advocacy output directories now include:
- `.txt` drafts
- `.md` companions
- `advocacy_bundle.json`
- a small `README.md` index

Memorandum output directories now include:
- `memorandum.json`
- `memorandum.md`
- `memorandum_of_law.pdf`
- `dependency_citations.jsonld`
- a small `README.md` index

The grounding layer now distinguishes:
- `verified_quote`: a short excerpt backed by a source URL and pincite metadata
- `paraphrase`: a fallback grounding summary when a verified quote has not been loaded yet

Human-facing advocacy and memorandum outputs now also surface an `authorityTrust` profile:
- `fully_verified`
- `mixed_support`
- `paraphrase_heavy`

When authority support is mixed or paraphrase-heavy, the generated drafts include an authority-grounding caution so reviewers and downstream tools do not overstate citation confidence.

Exported package directories now also include the memorandum set:
- advocacy `.txt` and `.md` drafts
- `advocacy_bundle.json`
- `memorandum.json`
- `memorandum.md`
- `memorandum_of_law.pdf`
- `authority_review.json`
- `authority_review.md`
- `authority_research_note.json`
- `authority_research_note.md`
- `authority_summary.json`
- `brief_index.json`

`brief_index.json` now also carries:
- `primaryKind`
- `authorityTrust`
- `warningSummary`
- `warningLabelSummary`
- per-entry `priority`
- per-entry `priorityLabel`

`manifest.json` now also carries:
- `authorityTrust`

Run checks:

```bash
cd /home/barberb/HACC/workspace2
PYTHONPATH=. python3 tests/run_checks.py
```

Refresh the canonical snapshot after an intentional output change:

```bash
cd /home/barberb/HACC/workspace2
PYTHONPATH=. python3 tests/update_snapshot.py
```

Print the generated case/package matrix:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/print_case_matrix.py
python3 engine/print_case_matrix.py --warned-only
```

The matrix view now includes each package's `authorityTrust` label so lower-trust citation sets are visible at a glance.
The detail, top-n, and describe-kind views now also show the compact package warning label from `brief_index.json.warningLabelSummary` alongside the package-level warning counts.
The main matrix JSON payload now also carries package-level discovery guidance through `recommendedFirstStop` and `whyOpenThis`, so downstream tools do not need to reopen `brief_index.json` just to decide which artifact to open first.

Print the matrix as JSON or filter by branch:

```bash
cd /home/barberb/HACC/workspace2
python3 engine/print_case_matrix.py --json
python3 engine/print_case_matrix.py --branch constructive_denial
python3 engine/print_case_matrix.py --trust paraphrase_heavy
python3 engine/print_case_matrix.py --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --sort confidence
python3 engine/print_case_matrix.py --json --case-id live_in_aide_case_001 --top-n 2
python3 engine/print_case_matrix.py --case-id live_in_aide_case_undue_burden_001
python3 engine/print_case_matrix.py --detail --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --top-n 3 --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --detail --case-id live_in_aide_case_no_violation_001 --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --detail --case-id live_in_aide_case_no_violation_001 --warned-only
python3 engine/print_case_matrix.py --kinds --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --primary-only --case-id live_in_aide_case_no_violation_001
python3 engine/print_case_matrix.py --describe-kind --case-id live_in_aide_case_001 --kind memorandum_pdf
python3 engine/print_case_matrix.py --path-only --case-id live_in_aide_case_001 --kind memorandum_pdf
python3 engine/print_case_matrix.py --authority-review --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-review --verified-only --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-review --support-status verified_quote --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-review --case-id live_in_aide_case_001 --fit analogical
python3 engine/print_case_matrix.py --authority-review --case-id live_in_aide_case_no_violation_001 --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --authority-review --json --support-status verified_quote --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-summary --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-summary --case-id live_in_aide_case_001 --fit analogical
python3 engine/print_case_matrix.py --authority-summary --json --case-id live_in_aide_case_no_violation_001 --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --authority-summary --json --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --authority-summary
python3 engine/print_case_matrix.py --authority-summary --trust paraphrase_heavy
python3 engine/print_case_matrix.py --authority-summary --json --support-status verified_quote
python3 engine/print_case_matrix.py --authority-findings
python3 engine/print_case_matrix.py --authority-findings --trust mixed_support
python3 engine/print_case_matrix.py --authority-findings --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --authority-findings --json --severity warning
python3 engine/print_case_matrix.py --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --fit-index --json
python3 engine/print_case_matrix.py --fit-matrix --json --fit record_support
python3 engine/print_case_matrix.py --fit-matrix --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --fit-summary --json --fit record_support
python3 engine/print_case_matrix.py --fit-summary --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --fit-findings --json --severity warning
python3 engine/print_case_matrix.py --fit-findings-summary --json --severity warning
python3 engine/print_case_matrix.py --fit-findings --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --fit-findings-summary --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --fit-findings --json --case-id live_in_aide_case_no_violation_001
python3 engine/print_case_matrix.py --fit-findings-summary --json --case-id live_in_aide_case_no_violation_001
python3 engine/print_case_matrix.py --refresh-state
python3 engine/print_case_matrix.py --refresh-state --json
python3 engine/print_case_matrix.py --refresh-state --wait-for-refresh-complete --json
python3 engine/print_case_matrix.py --refresh-state --fail-if-refresh-running --json
python3 engine/print_case_matrix.py --dashboard-overview --json --fit record_support
python3 engine/print_case_matrix.py --warning-summary
python3 engine/print_case_matrix.py --warning-summary --json --trust mixed_support
python3 engine/print_case_matrix.py --warning-summary --json --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --warning-label-matrix
python3 engine/print_case_matrix.py --warning-label-matrix --json --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --warning-entry-matrix
python3 engine/print_case_matrix.py --warning-entry-matrix --json --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --warning-entry-matrix --json --trust mixed_support
python3 engine/print_case_matrix.py --warning-entry-matrix --json --sort warningCount
python3 engine/print_case_matrix.py --warning-entry-matrix --json --warned-kind summary
python3 engine/print_case_matrix.py --warning-entry-matrix --json --sort warningCount --top-n 2
python3 engine/print_case_matrix.py --warning-entry-summary
python3 engine/print_case_matrix.py --warning-entry-summary --json
python3 engine/print_case_matrix.py --warning-entry-summary --json --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --warning-entry-summary --json --sort warningCount --top-n 2
python3 engine/print_case_matrix.py --warning-kind-matrix
python3 engine/print_case_matrix.py --warning-kind-matrix --json --warned-kind summary
python3 engine/print_case_matrix.py --warning-kind-matrix --json --trust mixed_support
python3 engine/print_case_matrix.py --warning-kind-matrix --json --sort warningCount
python3 engine/print_case_matrix.py --warning-kind-matrix --json --sort warningCount --top-n 5
python3 engine/print_case_matrix.py --warning-kind-summary
python3 engine/print_case_matrix.py --warning-kind-summary --json
python3 engine/print_case_matrix.py --warning-kind-summary --json --trust mixed_support
python3 engine/print_case_matrix.py --warning-kind-summary --json --sort warningCount --top-n 5
python3 engine/print_case_matrix.py --summary-index
python3 engine/print_case_matrix.py --summary-index --json
python3 engine/print_case_matrix.py --dashboard-index
python3 engine/print_case_matrix.py --dashboard-index --json
python3 engine/print_case_matrix.py --dashboard-overview
python3 engine/print_case_matrix.py --dashboard-overview --json
python3 engine/print_case_matrix.py --dashboard-overview --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --source-findings
python3 engine/print_case_matrix.py --source-findings --json
python3 engine/print_case_matrix.py --audit-index
python3 engine/print_case_matrix.py --audit-index --json
python3 engine/print_case_matrix.py --case-audit-matrix
python3 engine/print_case_matrix.py --case-audit-matrix --json
python3 engine/print_case_matrix.py --case-audit-matrix --json --sort confidence
python3 engine/print_case_matrix.py --case-audit-matrix --json --warning-label paraphrase_heavy
python3 engine/print_case_matrix.py --case-audit-matrix --json --fit-finding record_support_heavy
python3 engine/print_case_matrix.py --case-audit-matrix --json --warned-only
python3 engine/print_case_matrix.py --trust-matrix
python3 engine/print_case_matrix.py --trust-matrix --warned-only
python3 engine/print_case_matrix.py --trust-matrix --json --trust paraphrase_heavy
python3 engine/print_case_matrix.py --trust-matrix --json --warning-label paraphrase_heavy
```

`--refresh-state` reports `status`, timestamps, computed `elapsedSeconds`, and a small human-friendly elapsed label after a refresh completes. Add `--wait-for-refresh-complete` to block until the sentinel reaches `complete`, or `--fail-if-refresh-running` to exit immediately if refresh is still in progress. While refresh is `running`, the repo’s human-facing summary, findings, and matrix views now prepend a refresh warning banner, including `--summary-index`, `--fit-index`, `--audit-index`, `--dashboard-index`, `--dashboard-overview`, `--warning-summary`, `--warning-label-matrix`, `--warning-entry-matrix`, `--warning-kind-matrix`, `--warning-entry-summary`, `--warning-kind-summary`, `--trust-matrix`, `--source-findings`, `--source-metadata-matrix`, `--fit-matrix`, `--fit-summary`, `--fit-findings`, `--fit-findings-summary`, and `--case-audit-matrix`.

Those same text views now also show a settled-state line, `Stale While Refreshing: yes|no`, so the human-facing output has the same quick refresh guard as the JSON surfaces.

`--summary-index`, `--fit-index`, `--audit-index`, `--dashboard-index`, `--dashboard-overview`, `--trust-matrix`, `--warning-summary`, `--warning-label-matrix`, `--warning-entry-matrix`, `--warning-kind-matrix`, `--warning-entry-summary`, `--warning-kind-summary`, `--source-metadata-matrix`, `--source-findings`, `--fit-matrix`, `--fit-summary`, `--fit-findings`, `--fit-findings-summary`, and `--case-audit-matrix` JSON now include a machine-readable `refreshRuntime` block so consumers can detect running refresh state without opening the sentinel separately.

These discovery and primary audit JSON views also include a lightweight `staleWhileRefreshing` boolean shortcut:
- `--summary-index --json`
- `--fit-index --json`
- `--dashboard-index --json`
- `--dashboard-overview --json`
- `--audit-index --json`
- `--trust-matrix --json`
- `--warning-summary --json`
- `--warning-label-matrix --json`
- `--warning-entry-matrix --json`
- `--warning-kind-matrix --json`
- `--warning-entry-summary --json`
- `--warning-kind-summary --json`
- `--source-metadata-matrix --json`
- `--source-findings --json`
- `--fit-matrix --json`
- `--fit-summary --json`
- `--fit-findings --json`
- `--fit-findings-summary --json`
- `--case-audit-matrix --json`

Current note:
- the four sample fixtures now intentionally vary their authority support mix, so cross-case authority summaries can distinguish:
  - a fully verified baseline
  - mixed verified/paraphrase support
  - thinner evidentiary-gap support
- `outputs/authority_summary_matrix.json` is now generated alongside `outputs/index.json` as a repo-level summary artifact for downstream tooling.
- `outputs/authority_summary_matrix.md` is generated alongside the JSON companion as a human-readable audit report.
- `outputs/authority_findings.json` and `outputs/authority_findings.md` are generated as repo-level warning reports that flag fully verified, mixed-support, and paraphrase-heavy cases.
- `outputs/trust_matrix.json` and `outputs/trust_matrix.md` are generated as repo-level trust overviews that summarize branch, authority trust, primary artifact, and whether package entries carry trust warnings.
- `outputs/warning_summary.json` and `outputs/warning_summary.md` are generated as focused warning-overview artifacts for warned cases only.
- `outputs/warning_label_matrix.json` and `outputs/warning_label_matrix.md` are generated as label-sliced warning reports so downstream tools can inspect `mixed_support` and `paraphrase_heavy` cases separately without invoking the CLI.
- `outputs/warning_entry_matrix.json` and `outputs/warning_entry_matrix.md` are generated as per-case warning-entry audits that show which artifact kinds are carrying lower-trust warnings inside each package.
- `outputs/warning_entry_summary.json` and `outputs/warning_entry_summary.md` are generated as compact ranked warning-entry summaries without per-case warned-kind lists.
- `outputs/warning_kind_matrix.json` and `outputs/warning_kind_matrix.md` are generated as artifact-kind-first warning reports that show which warned cases include each kind.
- `outputs/warning_kind_summary.json` and `outputs/warning_kind_summary.md` are generated as compact ranked warning-kind summaries without per-case detail rows.
- `outputs/index.json` and `outputs/index.md` are generated as the primary case discovery layer across fixtures, packages, advocacy outputs, and memorandum outputs.
- `outputs/summary_index.json` and `outputs/summary_index.md` are generated as compact discovery artifacts for the lightweight warning summary reports.
- `outputs/fit_index.json` and `outputs/fit_index.md` are generated as compact discovery artifacts for the fit-quality matrix, summary, findings, and compact findings-summary reports.
- `outputs/dashboard_index.json` and `outputs/dashboard_index.md` are generated as top-level discovery artifacts that point to the main repo surfaces: `outputs/index.json`, `outputs/summary_index.json`, `outputs/fit_index.json`, `outputs/fit_findings.json`, `outputs/fit_findings_summary.json`, and `outputs/audit_index.json`.
- `outputs/dashboard_overview.json` and `outputs/dashboard_overview.md` are generated as a single-file rollup of case counts, trust posture, warning posture, source-hardening counts and status, featured cases, and main discovery entry points, including the compact fit summary pointer and refresh-state pointer.
- `outputs/audit_index.json` and `outputs/audit_index.md` are generated as repo-level discovery artifacts for the main audit reports and their JSON/Markdown companions.
- `outputs/fit_matrix.json` and `outputs/fit_matrix.md` are generated as cross-case fit-quality rollups that summarize direct, analogical, and record-support mappings.
- `outputs/fit_summary.json` and `outputs/fit_summary.md` are generated as compact fit-quality summaries for dashboard-style audit views.
- `outputs/fit_findings.json` and `outputs/fit_findings.md` are generated as repo-level findings reports that flag analogical and record-support-heavy fit posture by case.
- `outputs/fit_findings_summary.json` and `outputs/fit_findings_summary.md` are generated as compact case-first fit findings summaries for lighter dashboard and CLI use.
- `outputs/case_audit_matrix.json` and `outputs/case_audit_matrix.md` are generated as joined case-level audit reports that combine confidence, trust, primary artifact, and warning-label posture.

What the checks now cover:
- fixture validation against the JSON schemas
- generated result schema validation
- generated advocacy-bundle schema validation
- authority-review schema validation
- authority-summary schema validation
- cross-case authority-summary matrix schema validation
- authority-findings report schema validation
- trust-matrix report schema validation
- warning-summary report schema validation
- warning-label-matrix report schema validation
- warning-entry-matrix report schema validation
- audit-index schema validation
- case-audit-matrix report schema validation
- generated memorandum schema validation
- generated dependency-citations JSON-LD schema validation
- exported package JSON schema validation for `context.json`, `manifest.json`, `decision_tree.json`, `dependency_graph.json`, `dependency_citations.jsonld`, `summary.json`, `tests.json`, `case_instance.jsonld`, and bundled `advocacy_bundle.json`
- exported package audit validation for `authority_review.json`
- exported package audit validation for `authority_research_note.json`
- exported package audit validation for `authority_summary.json`
- exported package entry-point validation for `brief_index.json`
- package export completeness checks for bundled memorandum artifacts including `memorandum.json`, `memorandum.md`, and `memorandum_of_law.pdf`
- generated `outputs/index.json` schema validation and branch/path consistency checks
- branch metadata consistency across evaluator, advocacy bundle, memorandum outputs, and exported package artifacts including `manifest.json`, `decision_tree.json`, `dependency_graph.json`, and `summary.json`
- result snapshot regression across multiple fixtures
- exported package snapshot regression across multiple fixtures
- advocacy-output coverage
- advocacy-output snapshot regression across multiple fixtures
- structured advocacy-bundle snapshot regression across multiple fixtures
- policy and reasoning edge cases

- `python3 engine/print_case_matrix.py --authority-research-note --case-id live_in_aide_case_001`
- `python3 engine/print_case_matrix.py --authority-research-note --json --case-id live_in_aide_case_001 --source-normalized-only`
- `python3 engine/print_case_matrix.py --authority-research-note --json --case-id live_in_aide_case_001 --fit analogical`
- `python3 engine/print_case_matrix.py --source-metadata-matrix --json`

- `outputs/source_findings.json`
- `python3 engine/print_case_matrix.py --source-findings --json`
