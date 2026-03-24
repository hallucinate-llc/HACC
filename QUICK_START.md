# Quick Start Guide — DEI Compliance Audit

**Last Updated:** December 31, 2025

## What Was Created

You now have a complete audit toolkit comprising:

1. **`agent.md`** — Structured audit guide with strategy, checklist, and search/collection approach
2. **`EVIDENCE_REQUEST_TEMPLATE.md`** — Email-ready template to request documents from organizations
3. **Collection & Analysis Scripts** (`research_data/scripts/`):
   - `download_manager.py` — Download and deduplicate PDFs
   - `parse_pdfs.py` — Extract text from PDFs (with OCR fallback)
   - `index_and_tag.py` — Index documents and tag with keywords/risk scores
   - `report_generator.py` — Generate executive summaries and detailed reports
   - `collect_brave.py` — Search via Brave Search API (requires API key)
   - `run_collection.py` — Main orchestration script (full workflow)
   - `README.md` — Comprehensive toolkit documentation

## How to Get Started

### Option 0: Run The Grounded Complaint Pipeline

**Best for:** Turning the evidence already collected in this repo into an adversarially tested draft complaint package.

If you want package-mode search to run with shared hybrid retrieval instead of lexical fallback, install the optional HACC search extras into an isolated environment first:

```bash
python3 -m venv .venv-hacc-search --system-site-packages
.venv-hacc-search/bin/pip install -r requirements-hacc-search.txt
```

Then invoke the grounded pipeline with that interpreter:

```bash
# Recommended live route via Codex-backed llm_router
.venv-hacc-search/bin/python hacc_grounded_pipeline.py \
  --provider codex \
  --model gpt-5.3-codex \
  --num-sessions 1 \
  --max-turns 2 \
  --top-k 2 \
  --synthesize-complaint \
  --filing-forum hud

# Demo mode if you want deterministic no-API behavior
.venv-hacc-search/bin/python hacc_grounded_pipeline.py \
  --demo \
  --num-sessions 1 \
  --max-turns 2 \
  --top-k 2 \
  --synthesize-complaint \
  --filing-forum hud
```

The first vector-backed run may download the embedding model used by the search adapter.

Artifacts land in `research_results/grounded_runs/<timestamp>/` and include:

- `grounding_bundle.json` — ranked repository evidence plus synthetic prompts
- `mediator_evidence_packets.json` — preloadable evidence packets for the mediator
- `evidence_upload_report.json` — upload and claim-support summary
- `adversarial/` — batch results and best session bundle
- `complaint_synthesis/draft_complaint_package.json`
- `complaint_synthesis/draft_complaint_package.md`
- `complaint_synthesis/intake_follow_up_worksheet.json`
- `complaint_synthesis/intake_follow_up_worksheet.md`

When shared hybrid search is active, `run_summary.json` reports `effective_hacc_search_mode: shared_hybrid` and the search summary will not include a fallback note.

If a grounded run already finished grounding/adversarial work and you only want to regenerate the complaint package, reuse the saved artifacts instead of rerunning the expensive stages:

```bash
.venv-hacc-search/bin/python hacc_grounded_pipeline.py \
  --output-dir research_results/grounded_runs/<existing-run> \
  --provider codex \
  --model gpt-5.3-codex \
  --hacc-search-mode lexical \
  --synthesize-complaint \
  --reuse-existing-artifacts
```

### Option 0B: Fill Missing Facts And Rerun

**Best for:** Taking the generated worksheet, filling in the missing case-specific facts, and rerunning the grounded complaint pipeline with those answers merged back in.

```bash
# 1. Validate the worksheet and fail fast if required answers are still missing
python3 complaint-generator/scripts/validate_intake_follow_up_worksheet.py \
  research_results/grounded_runs/<timestamp>/complaint_synthesis/intake_follow_up_worksheet.json \
  --require-complete \
  --in-place

# 2. Rerun the full grounded complaint pipeline with the completed worksheet
python3 rerun_hacc_with_intake_worksheet.py \
  research_results/grounded_runs/<timestamp>/complaint_synthesis/intake_follow_up_worksheet.json \
  -- \
  --demo \
  --synthesize-complaint \
  --filing-forum hud
```

You can also point the rerun wrapper at the grounded run directory itself, and it will auto-discover `complaint_synthesis/intake_follow_up_worksheet.json`:

```bash
python3 rerun_hacc_with_intake_worksheet.py \
  research_results/grounded_runs/<timestamp> \
  -- \
  --demo \
  --synthesize-complaint \
  --filing-forum hud
```

Or let the wrapper pick the newest grounded run automatically:

```bash
python3 rerun_hacc_with_intake_worksheet.py \
  --latest \
  -- \
  --demo \
  --synthesize-complaint \
  --filing-forum hud
```

The rerun wrapper will:

- normalize and validate the worksheet
- print a short preflight summary of the selected grounded run plus answered/open/invalid items
- stop before rerun if required answers are still missing
- rerun `hacc_grounded_pipeline.py` with `--completed-intake-worksheet`
- print the refreshed grounded run output directory when the rerun completes
- print the refreshed complaint JSON path, complaint Markdown path, and worksheet path when synthesis artifacts are available

If you need to refresh only the adversarial summary for an existing run, you can also reuse the saved adversarial artifacts directly:

```bash
python3 hacc_adversarial_runner.py \
  --output-dir research_results/grounded_runs/repo_evidence_adversarial_v7_progress \
  --provider codex \
  --model gpt-5.3-codex \
  --hacc-search-mode lexical \
  --reuse-existing-artifacts
```

If you want a shorter wrapper for either case, use `resume_hacc_run.py`:

```bash
# Resume the newest grounded run and regenerate complaint synthesis
python3 resume_hacc_run.py grounded --latest -- --synthesize-complaint

# Resume a specific adversarial run and rebuild its summary
python3 resume_hacc_run.py adversarial \
  research_results/grounded_runs/repo_evidence_adversarial_v7_progress \
  -- --hacc-search-mode lexical --provider codex --model gpt-5.3-codex
```

If you want a quick human-readable view of the best grounded artifacts from a completed run, use `show_grounded_artifacts.py`:

```bash
python3 show_grounded_artifacts.py research_results/grounded_runs/repo_evidence_grounded_v10_lexical_ranked
python3 show_grounded_artifacts.py --latest
```

If you want to exercise the current complaint manager through its package, MCP, or CLI interface from HACC, use `invoke_complaint_manager.py`:

```bash
python3 invoke_complaint_manager.py package --tool complaint.list_intake_questions
python3 invoke_complaint_manager.py mcp --tool complaint.list_claim_elements
python3 invoke_complaint_manager.py cli -- tools
```

If you want to import Gmail evidence into the repo with the `ipfs_datasets_py` email processor, use `import_gmail_evidence.py`:

```bash
python3 import_gmail_evidence.py \
  --auth-mode gmail_oauth \
  --gmail-oauth-client-secrets /path/to/google-client-secret.json \
  --prompt-credentials \
  --upload-to-workspace \
  --review-after-upload \
  --generate-after-upload \
  --export-packet-after-upload \
  --export-markdown-after-upload \
  --user-id demo-user \
  --claim-element-id causation \
  --address housing.specialist@example.org \
  --address hearings@example.org \
  --since-date 2026-01-01 \
  --subject-contains termination \
  --case-slug hacc-email-import
```

That uses the IMAP email pipeline with the `gmail_oauth` auth backend, opens a browser-based Google OAuth flow, caches the Gmail token locally, creates `evidence/email_imports/<case-slug>/` with raw `.eml` files, extracted attachments, per-message JSON, and `email_import_manifest.json`, uploads the imported messages into the complaint workspace as saved document evidence, returns the updated complaint review payload, generates a draft complaint, and captures packet/markdown export payloads.

Address filtering options:

```bash
# Match anywhere in From/To/Cc/Reply-To/Sender
python3 import_gmail_evidence.py --prompt-credentials --address-file target_addresses.txt

# Match only sender-side headers
python3 import_gmail_evidence.py --prompt-credentials --from-address housing.specialist@example.org

# Match only recipient-side headers
python3 import_gmail_evidence.py --prompt-credentials --to-address hearings@example.org
```

Preview matching emails before downloading anything:

```bash
python3 import_gmail_evidence.py \
  --auth-mode gmail_oauth \
  --gmail-oauth-client-secrets /path/to/google-client-secret.json \
  --prompt-credentials \
  --dry-run \
  --address-file target_addresses.txt \
  --since-date 2026-01-01 \
  --subject-contains termination
```

Auth backend options:

```bash
# Generic IMAP username/password
python3 import_gmail_evidence.py --auth-mode imap_password --server mail.example.org --username you@example.org

# Gmail IMAP with app password
python3 import_gmail_evidence.py --auth-mode gmail_app_password --prompt-credentials

# Gmail IMAP with OAuth
python3 import_gmail_evidence.py --auth-mode gmail_oauth --gmail-oauth-client-secrets /path/to/google-client-secret.json
```

For unattended runs, you can still use environment variables:

```bash
export GMAIL_USER="you@gmail.com"
export GMAIL_APP_PASSWORD="your-16-char-app-password"
python3 import_gmail_evidence.py --address hearings@example.org
```

If you want to push an existing import manifest later as a separate step:

```bash
python3 upload_email_evidence_manifest.py \
  evidence/email_imports/hacc-email-import/email_import_manifest.json \
  --user-id demo-user \
  --claim-element-id causation \
  --review-after-upload \
  --generate-after-upload \
  --export-packet-after-upload \
  --export-markdown-after-upload
```

### Option A: Manual Evidence Collection (No API Keys Required)

**Best for:** Immediate audit with documents you already have or can request.

```bash
# 1. Use the evidence request template to ask organizations for policies
cat EVIDENCE_REQUEST_TEMPLATE.md

# 2. Collect PDFs into research_results/documents/raw/
mkdir -p research_results/documents/raw/
# (Copy PDFs here)

# 3. Run the analysis pipeline
cd /path/to/project
python3 research_data/scripts/run_collection.py --pdf-dir research_results/documents/raw/

# 4. Read the findings
cat research_results/FINDINGS_*.txt
```

### Option B: Automated Web Collection + API (Requires Brave API Key)

**Best for:** Discovering all Oregon.gov references to DEI/proxies.

```bash
# 1. Get a Brave API key (free tier at https://api.search.brave.com)

# 2. Set the API key
export BRAVE_API_KEY="your_api_key_here"

# 3. Run the full workflow
python3 research_data/scripts/run_collection.py

# 4. Review results
cat research_results/FINDINGS_*.txt
cat research_results/summary_*.csv
```

### Option C: Hybrid (Combine Manual + API)

```bash
# 1. Copy any existing PDFs to research_results/documents/raw/

# 2. Run with API to discover more
export BRAVE_API_KEY="your_key"
python3 research_data/scripts/run_collection.py --pdf-dir research_results/documents/raw/
```

## Understanding the Output

After running the workflow, check these files:

| File | Purpose | Who Reads It |
|------|---------|-------------|
| `FINDINGS_YYYYMMDD.txt` | One-page summary (high-risk docs) | Executives, decision-makers |
| `DETAILED_REPORT_YYYYMMDD.txt` | Full technical analysis | Compliance officers, lawyers |
| `summary_YYYYMMDD.csv` | Spreadsheet (all documents, scores) | Analysts, spreadsheet review |
| `document_index_YYYYMMDD.json` | Machine-readable index | Scripts, automation |

## Key Audit Concepts

### Risk Scoring (0–3)

- **Score 0**: No DEI/proxy language → Compliant
- **Score 1**: DEI/proxy present → Possible issue, review context
- **Score 2**: DEI/proxy + mandatory language → Probable issue, review detail
- **Score 3**: Explicit DEI policy + binding language → Clear violation, immediate action

### Red Flag Keywords to Watch

- Explicit: `diversity statement`, `BIPOC-only`, `underrepresented`, `minority-only`
- Proxies: `cultural competence`, `lived experience`, `safe space`, `equity plan`
- Binding: `policy`, `shall`, `must`, `required`, `mandatory`, `applicable to`

### Applicability Areas

Which HA decisions are affected by Oregon policies?
- **Hiring** — Employment decisions
- **Procurement** — Vendor/contractor selection
- **Training** — Mandatory trainings
- **Housing** — Program eligibility, lease, operations

## What to Do With Findings

1. **High-Risk Documents (Score ≥ 2)**
   - Read in full
   - Check if they apply to housing authorities
   - Assess how they conflict with Bondi memo guidance
   - Flag for legal review

2. **Collect HA Evidence**
   - Use `EVIDENCE_REQUEST_TEMPLATE.md` to ask HA for current policies
   - Compare against Oregon requirements
   - Identify gaps and conflicts

3. **Develop Remediation Plan**
   - Use `agent.md` checklist
   - Prioritize by risk score
   - Set implementation timeline
   - Assign ownership

## Next Steps (In Order)

### This Week
- [ ] Read `agent.md` (audit strategy overview)
- [ ] Collect initial PDF evidence (manual or API)
- [ ] Run `run_collection.py` to generate findings
- [ ] Review `FINDINGS_*.txt` and `summary_*.csv`

### Next Week
- [ ] Send `EVIDENCE_REQUEST_TEMPLATE.md` to HA, Clackamas County, and state agencies
- [ ] Perform detailed review of high-risk documents (Score ≥ 2)
- [ ] Interview stakeholders (HR, procurement, program managers)
- [ ] Compile list of HA policies that need review

### Following Weeks
- [ ] Cross-reference Oregon policies with HA policies
- [ ] Identify conflicts with Bondi memo guidance
- [ ] Draft remediation plan
- [ ] Present findings to leadership

## Examples: Quick Queries

Want to search for something specific? Use the scripts individually:

```python
# Search for a single term in parsed documents
from pathlib import Path
import json

search_term = "underrepresented"
parsed_dir = Path("research_results/documents/parsed")

for txt_file in parsed_dir.glob("*.txt"):
    with open(txt_file, 'r') as f:
        text = f.read()
        if search_term.lower() in text.lower():
            print(f"Found in: {txt_file.name}")
```

## Common Questions

**Q: Do I need API keys?**
A: No. You can use manual file upload (Option A). API keys (Brave, Google) are optional for automated discovery.

**Q: How many documents will I find?**
A: Depends on Oregon's publications. Likely 50–200 relevant policy documents across state agencies.

**Q: What if PDFs are scanned (images)?**
A: The `parse_pdfs.py` script will auto-detect and run OCR (requires `ocrmypdf` installed).

**Q: How do I update the toolkit?**
A: All scripts are modular. Edit `index_and_tag.py` to add new keywords, or modify `report_generator.py` for different report formats.

**Q: Can I automate periodic re-scans?**
A: Yes. Wrap `run_collection.py` in a cron job or scheduled task. Results are timestamped and deduplicated.

## Troubleshooting

**Script import errors?**
```bash
cd /path/to/project
export PYTHONPATH="${PYTHONPATH}:$(pwd)/research_data/scripts"
```

**`pdftotext` not found?**
```bash
sudo apt-get install poppler-utils
```

**Out of disk space?**
- Parsed text files are much smaller than PDFs. Delete raw PDFs after parsing if needed.
- `git` the important outputs (index JSON, CSV, findings) and archive raw PDFs.

## References

- **Agent Audit Guide**: `agent.md`
- **Evidence Request**: `EVIDENCE_REQUEST_TEMPLATE.md`
- **Toolkit README**: `research_data/scripts/README.md`
- **Source Memo**: Attorney General Bondi, "Guidance for Recipients of Federal Funding Regarding Unlawful Discrimination" (July 29, 2025)

---

**Ready to start?** Run:

```bash
python3 research_data/scripts/run_collection.py --help
```

Then follow Option A, B, or C above.
