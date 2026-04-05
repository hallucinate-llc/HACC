# Invasion of Privacy Memorandum Workspace

This workspace contains a traceable legal-reasoning prototype for a live-in-aide accommodation dispute, with structured case fixtures, rule evaluation, memorandum generation, and audit-oriented exports.

## What is here
- schema-first case modeling with asserted-facts vs accepted-findings separation
- rule-based case evaluation with proof traces and provenance
- advocacy draft generation from evaluated case state
- memorandum generation (JSON, Markdown, PDF, and citation-grounding JSON-LD)
- package export artifacts for downstream tooling
- dependency-free regression checks and snapshot refresh tooling

## Repository map
- docs/: implementation notes and design choices
- fixtures/: sample case payloads
- engine/: evaluator, exporters, memorandum and advocacy generators
- schema/: JSON Schemas for inputs and generated artifacts
- outputs/: generated artifacts and cross-case audit reports
- tests/: checks and snapshots

## Start here
- docs/implementation_plan.md
- docs/design_decisions.md
- docs/output_modes.md
- fixtures/live_in_aide_case.json

## Quick start

Run a single evaluation:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
python3 engine/evaluate_case.py fixtures/live_in_aide_case.json
```

Write evaluation output under outputs/:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
python3 engine/evaluate_case.py fixtures/live_in_aide_case.json --write
```

Generate advocacy drafts:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
python3 engine/generate_advocacy.py fixtures/live_in_aide_case.json --write
```

Generate memorandum outputs (including PDF and dependency grounding):

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
python3 engine/generate_memorandum.py fixtures/live_in_aide_case.json --write
```

## Validation and snapshots

Run dependency-free checks:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
PYTHONPATH=. python3 tests/run_checks.py
```

Refresh canonical snapshots after intentional output changes:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
PYTHONPATH=. python3 tests/update_snapshot.py
```

## Matrix and audit views

Common discovery commands:

```bash
cd "/home/barberb/HACC/Invasion of Privacy Memorandum"
python3 engine/print_case_matrix.py
python3 engine/print_case_matrix.py --detail --case-id live_in_aide_case_001
python3 engine/print_case_matrix.py --json --trust paraphrase_heavy
python3 engine/print_case_matrix.py --dashboard-overview --json
python3 engine/print_case_matrix.py --warning-summary
python3 engine/print_case_matrix.py --authority-summary
python3 engine/print_case_matrix.py --fit-summary
```

For the full option surface, run:

```bash
python3 engine/print_case_matrix.py --help
```

## Authority-trust and grounding notes

Generated bundles expose authority trust posture:
- fully_verified
- mixed_support
- paraphrase_heavy

Grounding support distinguishes:
- verified_quote: excerpt tied to source URL and citation metadata
- paraphrase: fallback summary when a verified quote is not present

When trust is mixed or paraphrase-heavy, outputs include explicit cautions to avoid overstating citation confidence.
