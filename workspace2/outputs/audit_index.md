# Audit Index

Recommended First Stop: `outputs/case_audit_matrix.json`
Why Open This: Start with the case-audit matrix because it is the strongest joined repo-level view of confidence, trust, fit findings, warnings, and package posture.

Priority | Kind | JSON | Markdown | Description
--- | --- | --- | --- | ---
primary | authority_summary_matrix | outputs/authority_summary_matrix.json | outputs/authority_summary_matrix.md | Cross-case authority support counts by status and reasoning bucket.
primary | authority_findings | outputs/authority_findings.json | outputs/authority_findings.md | Repo-level findings report for authority trust and support quality.
secondary | source_findings | outputs/source_findings.json | outputs/source_findings.md | Repo-level findings report for normalized versus unnormalized source metadata.
secondary | source_metadata_matrix | outputs/source_metadata_matrix.json | outputs/source_metadata_matrix.md | Cross-case rollup of sourceVerified and sourceNormalized authority metadata.
secondary | fit_matrix | outputs/fit_matrix.json | outputs/fit_matrix.md | Cross-case fit-quality matrix showing direct, analogical, and record-support counts.
secondary | fit_summary | outputs/fit_summary.json | outputs/fit_summary.md | Compact fit-quality summary for dashboard-style audit views.
primary | fit_findings | outputs/fit_findings.json | outputs/fit_findings.md | Repo-level findings report for direct, analogical, and record-support fit posture.
secondary | fit_findings_summary | outputs/fit_findings_summary.json | outputs/fit_findings_summary.md | Compact case-first summary of fit findings severity and posture.
primary | trust_matrix | outputs/trust_matrix.json | outputs/trust_matrix.md | Cross-case trust overview with primary artifact and warning counts.
secondary | warning_summary | outputs/warning_summary.json | outputs/warning_summary.md | Warned-case summary across all lower-trust packages.
supporting | warning_label_matrix | outputs/warning_label_matrix.json | outputs/warning_label_matrix.md | Label-sliced warning summaries for mixed-support and paraphrase-heavy cases.
supporting | warning_entry_matrix | outputs/warning_entry_matrix.json | outputs/warning_entry_matrix.md | Per-case warned artifact kinds and warning-label counts across package entries.
supporting | warning_entry_summary | outputs/warning_entry_summary.json | outputs/warning_entry_summary.md | Compact ranked warning-entry summary without per-case warned-kind lists.
supporting | warning_kind_matrix | outputs/warning_kind_matrix.json | outputs/warning_kind_matrix.md | Artifact-kind-first warning matrix showing which warned cases include each kind.
supporting | warning_kind_summary | outputs/warning_kind_summary.json | outputs/warning_kind_summary.md | Compact ranked warning-kind summary without per-case detail rows.
secondary | summary_index | outputs/summary_index.json | outputs/summary_index.md | Compact discovery file for lightweight audit summary artifacts.
recommended | case_audit_matrix | outputs/case_audit_matrix.json | outputs/case_audit_matrix.md | Joined case-level audit matrix with confidence, trust, primary artifact, and warning posture.
