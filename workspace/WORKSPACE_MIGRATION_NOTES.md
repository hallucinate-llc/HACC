# Workspace Migration Notes

This workspace contains a migrated snapshot of source evidence directories requested by the user:

- `/home/barberb/HACC/hacc_research`
- `/home/barberb/HACC/hacc_website`
- `/home/barberb/HACC/legal_data`
- `/home/barberb/HACC/research_data`
- `/home/barberb/HACC/research_results`

## Migration mode

- Target: `/home/barberb/HACC/workspace/migrated_sources`
- Method: `cp -al` hardlinked snapshot
- Reason: preserve full content in workspace while avoiding unnecessary disk duplication for large trees (notably `research_results`).

## Generated artifacts

- Improved complaint: `improved-complaint-from-temporary-session.md`
- Run summary: `improved-complaint-from-temporary-session.summary.json`
- Runner script: `improve_temporary_session_complaint.py`
- Migration manifest: `migration_manifest.json`

## Evidence usage update

`improve_temporary_session_complaint.py` now resolves evidence from `workspace/migrated_sources` when present and includes targeted `research_results` materials in imports.
