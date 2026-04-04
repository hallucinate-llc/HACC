# Dashboard Index

Recommended First Stop: `outputs/dashboard_overview.json`
Why Open This: Start with the dashboard overview because it is the single best top-level entry point into counts, warnings, fit posture, and the main discovery surfaces.

Priority | Kind | JSON | Markdown | Why Open This | Description
--- | --- | --- | --- | --- | ---
primary | outputs_index | outputs/index.json | outputs/index.md | Open this when you want the complete generated case inventory before drilling into audit surfaces. | Primary generated case index across all fixtures and package paths.
secondary | summary_index | outputs/summary_index.json | outputs/summary_index.md | Open this when you want the lightweight warning-summary discovery path instead of the broader dashboard surface. | Compact discovery file for lightweight warning summary artifacts.
primary | fit_index | outputs/fit_index.json | outputs/fit_index.md | Open this when you want the compact fit discovery path without scanning the full audit index. | Compact discovery file for fit-quality matrix and summary artifacts.
primary | fit_findings | outputs/fit_findings.json | outputs/fit_findings.md | Open this when you want immediate case-level fit-risk findings from the dashboard layer. | Repo-level findings report for analogical and record-support fit posture.
secondary | fit_findings_summary | outputs/fit_findings_summary.json | outputs/fit_findings_summary.md | Open this when you want a lighter fit findings view from the dashboard layer. | Compact case-first summary of fit findings severity and posture.
supporting | refresh_state | outputs/.refresh_state.json | outputs/dashboard_overview.md | Open this when you want the current refresh state and timing without scanning the larger dashboard rollup. | Snapshot refresh sentinel showing whether generation is running or complete.
secondary | audit_index | outputs/audit_index.json | outputs/audit_index.md | Open this when you want the broadest audit discovery path across trust, warning, source, and fit reports. | Broader discovery file for the full repo-level audit surface.
recommended | dashboard_overview | outputs/dashboard_overview.json | outputs/dashboard_overview.md | Open this first when you want the strongest single top-level dashboard rollup before following linked surfaces. | Single-file dashboard rollup of case counts, trust posture, warnings, and discovery entry points.
