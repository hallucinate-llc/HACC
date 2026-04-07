# Authority And Proof-State Schema

## Purpose

This note defines the intended end-to-end grounding path for the deontic layer in this workspace.

## Target stack

1. Authority layer
- signed orders
- statutes or procedural rules
- agency or custodian duty sources

2. Verified fact layer
- document-backed events
- date-stamped communications
- order terms
- repository-negative findings

3. Proof-state layer
- direct proof available
- inference only
- contradicted
- unresolved
- local search negative
- compelled production required

4. Filing-safe conclusion layer
- obligations
- permissions
- prohibitions
- conflict flags
- discovery / subpoena permissions

## Current implementation status

Implemented now:
- rule tracks: `filing`, `hypothesis`, `workflow`
- HACC January 12 authority-chain predicates
- prior-appointment source-order-not-found predicate
- compelled-production-required predicate

Still to build:
- formal citation objects for governing law
- interval-aware temporal predicates
- element-by-element contempt and sanctions schemas

## Working rule discipline

- `filing` rules should depend only on verified facts, proof-state predicates, or explicit authority anchors.
- `hypothesis` rules may model theories but should not activate filing-facing outputs.
- `workflow` rules may drive subpoena and production operations without being treated as merits findings.
