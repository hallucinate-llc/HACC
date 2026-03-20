# HACC — Housing Authority of Clackamas County Audit & Complaint System

An **adversarial evidence collection and complaint generation system** for investigating and documenting potential civil rights violations related to DEI policies and discriminatory practices in housing authorities and local government entities.

The system collects Oregon state statutes, administrative rules, and federal regulations; indexes them into a searchable corpus; grounds complaint evidence against the corpus; and produces adversarially tested draft complaint packages ready for filing with HUD, state agencies, or courts.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Architecture](#architecture)
- [Python Modules](#python-modules)
  - [hacc\_research — Core Research Engine](#hacc_research--core-research-engine)
  - [hacc\_grounded\_pipeline.py — Grounded Complaint Pipeline](#hacc_grounded_pipelinepy--grounded-complaint-pipeline)
  - [hacc\_adversarial\_runner.py — Adversarial Testing Harness](#hacc_adversarial_runnerpy--adversarial-testing-harness)
- [CLI Reference](#cli-reference)
  - [hacc\_research CLI](#hacc_research-cli)
  - [hacc\_grounded\_pipeline CLI](#hacc_grounded_pipeline-cli)
  - [hacc\_adversarial\_runner CLI](#hacc_adversarial_runner-cli)
- [Collection & Analysis Scripts](#collection--analysis-scripts)
- [Research Data & Corpus](#research-data--corpus)
- [Output Structure](#output-structure)
- [Configuration](#configuration)
- [Testing](#testing)
- [Key Concepts](#key-concepts)
- [Disclaimers](#disclaimers)

---

## Overview

HACC is built around four main activities:

1. **Collect** — Download Oregon statutes (ORS), administrative rules (OAR), executive orders, state agency guidance, and federal regulations (HUD) into a local corpus.
2. **Index & Search** — Build lexical and vector search indexes over the corpus; support hybrid search with semantic tokenization.
3. **Ground** — Select the most relevant evidence documents, generate synthetic prompts and mediator evidence packets, and simulate evidence upload to the `complaint-generator` mediator.
4. **Generate** — Run multiple adversarial complaint generation sessions in parallel, score results, optionally auto-patch the complaint-generator codebase, and synthesize a final draft complaint package.

The system integrates with the [`complaint-generator`](./complaint-generator/) submodule, which provides the mediator, phase manager, denoiser, and complaint synthesis scripts.

---

## Quick Start

### Option 0 — Run the Full Grounded Complaint Pipeline (Recommended)

Turns evidence already collected in this repository into an adversarially tested draft complaint package. No API keys required in demo mode.

```bash
python3 hacc_grounded_pipeline.py \
  --demo \
  --num-sessions 1 \
  --max-turns 2 \
  --top-k 2 \
  --synthesize-complaint \
  --filing-forum hud
```

Artifacts land in `research_results/grounded_runs/<timestamp>/`:

| File | Description |
|------|-------------|
| `grounding_bundle.json` | Ranked repository evidence + synthetic prompts |
| `mediator_evidence_packets.json` | Pre-loadable evidence packets for the mediator |
| `evidence_upload_report.json` | Upload and claim-support summary |
| `adversarial/adversarial_results.json` | Scored adversarial session results |
| `adversarial/best_session_bundle.json` | Best scoring complaint session |
| `complaint_synthesis/draft_complaint_package.json` | Structured complaint (JSON) |
| `complaint_synthesis/draft_complaint_package.md` | Draft complaint (Markdown) |
| `run_summary.json` | Consolidated workflow summary |

### Option A — Manual Evidence Collection (No API Keys)

```bash
# 1. Request documents using the evidence request template
cat EVIDENCE_REQUEST_TEMPLATE.md

# 2. Place PDFs in the raw documents folder
mkdir -p research_results/documents/raw/
# (copy PDFs here)

# 3. Run the collection pipeline
python3 research_data/scripts/run_collection.py --pdf-dir research_results/documents/raw/

# 4. Review findings
cat research_results/FINDINGS_*.txt
```

### Option B — Automated Web Collection (Requires Brave API Key)

```bash
export BRAVE_API_KEY="your_api_key_here"
python3 research_data/scripts/run_collection.py

cat research_results/FINDINGS_*.txt
cat research_results/summary_*.csv
```

### Option C — Hybrid (Manual + API)

```bash
mkdir -p research_results/documents/raw/
# (copy any existing PDFs)

export BRAVE_API_KEY="your_key"
python3 research_data/scripts/run_collection.py --pdf-dir research_results/documents/raw/
```

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│  COLLECTION (research_data/scripts/)                              │
│  Download PDFs · Parse text · Index & tag · Generate reports     │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  CORPUS (hacc_research/engine.py — HACCResearchEngine)            │
│  Load parsed docs · Load repo evidence · Load knowledge graphs   │
│  Build lexical index · Build vector index                        │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  SEARCH & DISCOVERY                                               │
│  Lexical · Vector · Hybrid · Web (Brave) · Legal (FR/USC/RECAP)  │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  GROUNDING (HACCResearchEngine.build_grounding_bundle)            │
│  Select top-K evidence · Generate synthetic prompts              │
│  Build mediator evidence packets                                 │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  EVIDENCE UPLOAD SIMULATION (HACCResearchEngine.simulate_upload)  │
│  Upload to complaint-generator mediator · Evaluate support       │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  ADVERSARIAL TESTING (hacc_adversarial_runner.py)                 │
│  Parallel sessions · Turn-based interaction · Autopatch system   │
│  Score & rank best complaint output                              │
└────────────────────────┬─────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│  COMPLAINT SYNTHESIS (complaint-generator/scripts/)               │
│  draft_complaint_package.json · draft_complaint_package.md       │
└──────────────────────────────────────────────────────────────────┘
```

---

## Python Modules

### `hacc_research` — Core Research Engine

**Package:** `hacc_research/`

```python
from hacc_research import HACCResearchEngine

engine = HACCResearchEngine()
results = engine.search("housing discrimination", top_k=10)
```

#### `CorpusDocument` (dataclass)

Represents a single document in the research corpus.

| Field | Type | Description |
|-------|------|-------------|
| `document_id` | `str` | Unique document identifier |
| `title` | `str` | Document title |
| `text` | `str` | Full document text |
| `source_type` | `str` | Source category (e.g., `parsed`, `repository`, `knowledge_graph`) |
| `source_path` | `Path` | Path to the source file |
| `metadata` | `dict` | Arbitrary metadata (URL, timestamps, etc.) |
| `rules` | `list` | Extracted rule/provision records |
| `entities` | `list` | Named entities |
| `relationships` | `list` | Entity relationships |

#### `HACCResearchEngine` — Key Methods

**Corpus loading:**

| Method | Description |
|--------|-------------|
| `load_corpus()` | Load parsed documents, repository evidence, and knowledge graphs |
| `corpus_records()` | Serialize all documents to a list of dicts |
| `integration_status()` | Report availability of optional integrations |

**Index building:**

| Method | Description |
|--------|-------------|
| `build_index(output_path)` | Build a lexical search index (JSON manifest + JSONL records) |
| `build_vector_index(output_dir, index_name, batch_size)` | Build a vector embedding index via the `ipfs_datasets` integration |
| `ensure_vector_index(index_dir, index_name)` | Create or locate an existing vector index |

**Search (5 modes):**

| Method | Description |
|--------|-------------|
| `search(query, top_k, ...)` | High-level entry point; auto-selects strategy |
| `search_package(query, top_k, ...)` | Auto-routes to hybrid or lexical with auto-indexing |
| `search_local(query, top_k, ...)` | Lexical search on loaded corpus |
| `search_vector(query, top_k, ...)` | Vector similarity search |
| `hybrid_search(query, top_k, ...)` | Combined lexical + vector ranked results |

**Discovery:**

| Method | Description |
|--------|-------------|
| `discover(query, max_results, ...)` | Web search via Brave API or multi-engine |
| `discover_seeded_commoncrawl(queries, ...)` | Historical Common Crawl discovery |
| `discover_legal_authorities(query, max_results, ...)` | Federal Register, U.S. Code, RECAP |
| `research(query, top_k, max_results, ...)` | Combined local + web + legal search |

**Grounding & evidence:**

| Method | Description |
|--------|-------------|
| `build_grounding_bundle(query, top_k, ...)` | Select top-K evidence + generate synthetic prompts |
| `simulate_evidence_upload(query, top_k, ...)` | Upload evidence to mediator and evaluate support quality |

---

### `hacc_grounded_pipeline.py` — Grounded Complaint Pipeline

Orchestrates the full workflow in a single call: grounding → evidence upload → adversarial testing → (optional) complaint synthesis.

```python
from hacc_grounded_pipeline import run_hacc_grounded_pipeline

summary = run_hacc_grounded_pipeline(
    output_dir="research_results/grounded_runs/my_run",
    demo=True,
    num_sessions=2,
    max_turns=3,
    top_k=5,
    synthesize_complaint=True,
    filing_forum="hud",
)
```

**Key parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_dir` | *(required)* | Directory for all output artifacts |
| `query` | `None` | Explicit grounding query; defaults to the selected preset's first query |
| `hacc_preset` | `"core_hacc_policies"` | Named query preset |
| `claim_type` | `None` | Claim type for upload simulation (e.g., `"housing_discrimination"`) |
| `top_k` | `5` | Maximum evidence files to upload |
| `num_sessions` | `3` | Number of adversarial sessions to run |
| `max_turns` | `4` | Maximum turns per adversarial session |
| `max_parallel` | `1` | Maximum parallel sessions |
| `demo` | `False` | Use deterministic demo backends (no LLM API calls) |
| `provider` | `"codex"` | LLM router provider override for HACC runs |
| `model` | `"gpt-5.3-codex"` | Default HACC model override |
| `synthesize_complaint` | `False` | Run complaint synthesis after adversarial batch |
| `filing_forum` | `"court"` | Filing forum: `"court"`, `"hud"`, or `"state_agency"` |
| `use_hacc_vector_search` | `False` | Blend lexical and vector search |

---

### `hacc_adversarial_runner.py` — Adversarial Testing Harness

Runs multiple parallel adversarial complaint generation sessions against the `complaint-generator` backends.

```python
from hacc_adversarial_runner import run_hacc_adversarial_batch

summary = run_hacc_adversarial_batch(
    output_dir="research_results/adversarial_runs/my_run",
    num_sessions=3,
    max_turns=4,
    demo=True,
    hacc_preset="core_hacc_policies",
)
```

**Key parameters:**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `output_dir` | *(required)* | Directory for adversarial run artifacts |
| `num_sessions` | `3` | Number of parallel complaint sessions |
| `max_turns` | `4` | Maximum turns per session |
| `max_parallel` | `1` | Maximum concurrent sessions |
| `demo` | `False` | Use deterministic demo backends |
| `hacc_preset` | `"core_hacc_policies"` | Named HACC evidence query preset |
| `hacc_count` | `None` | Maximum evidence files per session |
| `personalities` | `None` | Pin specific complainant personalities |
| `provider` | `"codex"` | Default LLM router provider for HACC runs |
| `model` | `"gpt-5.3-codex"` | Default HACC model override |
| `emit_autopatch` | `False` | Generate an optimizer patch artifact |
| `apply_autopatch` | `False` | Generate and apply optimizer patch to `complaint-generator` |
| `autopatch_method` | `"test_driven"` | Agentic optimization method |
| `autopatch_profile` | `"question_flow"` | Requested autopatch target profile |
| `autopatch_target_files` | `None` | Explicit target-file override list |
| `use_recommended_autopatch_targets` | `False` | Let the optimizer replace the requested autopatch scope with intake-driven recommended files/profile |

**Autopatch recommendation fields** in the run summary:

- `requested_profile` / `requested_target_files` — the original scope requested by the caller
- `recommended_profile` / `recommended_target_files` — the optimizer's intake-driven recommendation
- `profile` / `target_files` — the actual scope selected for the autopatch run
- `used_recommended_targets` — whether the optimizer recommendation replaced the requested scope

**Autopatch profiles** (targeted code optimization):

| Profile | Target | Description |
|---------|--------|-------------|
| `denoiser_select_candidates_only` | `denoiser.py` | Optimize `select_question_candidates` |
| `denoiser_standard_intake_only` | `denoiser.py` | Optimize `_ensure_standard_intake_questions` |
| `denoiser_process_answer_only` | `denoiser.py` | Optimize `process_answer` |
| `phase_manager_action_only` | `phase_manager.py` | Optimize `_get_intake_action` |
| `phase_manager_only` | `phase_manager.py` | Optimize `_is_intake_complete` + `_get_intake_action` |
| `question_flow` | `phase_manager.py` + `inquiries.py` | Full question flow optimization |
| `denoiser_focus` | `denoiser.py` + `phase_manager.py` | Denoiser + phase manager together |
| `full_mediator` | `mediator.py` + `phase_manager.py` | Full mediator optimization |

---

## CLI Reference

### `hacc_research` CLI

```bash
python3 -m hacc_research <command> [options]
```

| Command | Description |
|---------|-------------|
| `build-index` | Build a searchable lexical corpus summary index |
| `build-vector-index` | Build a vector embedding index |
| `search` | Search the local HACC corpus (lexical or hybrid) |
| `vector-search` | Search the local HACC vector index |
| `discover` | Run web discovery via the `ipfs_datasets` adapter |
| `seeded-commoncrawl` | Run seeded Common Crawl discovery |
| `discover-legal` | Search Federal Register, U.S. Code, and RECAP |
| `research` | Combined local search + web discovery + legal |
| `grounding-bundle` | Build a grounding evidence bundle |
| `simulate-upload` | Simulate evidence upload to the mediator |

**Examples:**

```bash
# Search the local corpus
python3 -m hacc_research search "housing discrimination" --top-k 10

# Hybrid search (lexical + vector)
python3 -m hacc_research search "reasonable accommodation" --use-vector --top-k 5

# Vector-only search
python3 -m hacc_research vector-search "DEI proxy language"

# Web discovery
python3 -m hacc_research discover "Oregon DEI policies" --max-results 20 --scrape

# Legal authority search
python3 -m hacc_research discover-legal "Fair Housing Act" --max-results 10

# Combined research
python3 -m hacc_research research "housing discrimination policy" \
  --top-k 5 --max-results 10 --scrape

# Build grounding evidence bundle
python3 -m hacc_research grounding-bundle "reasonable accommodation" --top-k 5

# Simulate evidence upload to mediator
python3 -m hacc_research simulate-upload "housing discrimination" --top-k 5

# Build lexical index
python3 -m hacc_research build-index --output-path research_results/search_indexes/

# Build vector index
python3 -m hacc_research build-vector-index --index-name hacc_corpus
```

### `hacc_grounded_pipeline` CLI

```bash
python3 hacc_grounded_pipeline.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `research_results/grounded_runs/<timestamp>` | Output directory |
| `--query` | *preset default* | Explicit grounding query |
| `--hacc-preset` | `core_hacc_policies` | Named query preset |
| `--claim-type` | *preset default* | Claim type for evidence upload |
| `--top-k` | `5` | Maximum evidence files to upload |
| `--num-sessions` | `3` | Number of adversarial sessions |
| `--max-turns` | `4` | Maximum turns per session |
| `--max-parallel` | `1` | Maximum parallel sessions |
| `--use-hacc-vector-search` | off | Use vector search for grounding |
| `--demo` | off | Use deterministic demo backends |
| `--config` | `None` | Optional complaint-generator config JSON |
| `--backend-id` | `None` | Backend id from config |
| `--provider` | `codex` | Default LLM router provider for HACC runs |
| `--model` | `gpt-5.3-codex` | Default HACC model override |
| `--synthesize-complaint` | off | Run complaint synthesis after adversarial batch |
| `--filing-forum` | `court` | `court`, `hud`, or `state_agency` |
| `--json` | off | Print the full workflow summary JSON |

**Examples:**

```bash
# Full pipeline in demo mode (no API keys needed)
python3 hacc_grounded_pipeline.py \
  --demo \
  --num-sessions 1 \
  --max-turns 2 \
  --top-k 2 \
  --synthesize-complaint \
  --filing-forum hud

# Live run pinned to Codex through llm_router
python3 hacc_grounded_pipeline.py \
  --num-sessions 3 \
  --max-turns 4 \
  --top-k 5 \
  --synthesize-complaint \
  --filing-forum court \
  --provider codex \
  --model gpt-5.3-codex

# Custom query with vector search
python3 hacc_grounded_pipeline.py \
  --query "reasonable accommodation denial" \
  --use-hacc-vector-search \
  --top-k 8 \
  --num-sessions 2
```

### `hacc_adversarial_runner` CLI

```bash
python3 hacc_adversarial_runner.py [options]
```

| Option | Default | Description |
|--------|---------|-------------|
| `--output-dir` | `research_results/adversarial_runs/<timestamp>` | Output directory |
| `--num-sessions` | `3` | Number of parallel sessions |
| `--max-turns` | `4` | Maximum turns per session |
| `--max-parallel` | `1` | Maximum concurrent sessions |
| `--personality` | *(all)* | Pin complainant personality (repeatable) |
| `--hacc-preset` | `core_hacc_policies` | Named HACC evidence query preset |
| `--hacc-count` | `None` | Maximum evidence files per session |
| `--use-hacc-vector-search` | off | Use vector search for evidence |
| `--demo` | off | Use deterministic demo backends |
| `--config` | `None` | Optional complaint-generator config JSON |
| `--backend-id` | `None` | Backend id from config |
| `--provider` | `codex` | Default LLM router provider for HACC runs |
| `--model` | `gpt-5.3-codex` | Default HACC model name |
| `--emit-autopatch` | off | Generate an optimizer patch artifact without applying it |
| `--apply-autopatch` | off | Generate and apply the optimizer patch |
| `--no-apply-autopatch` | off | Keep the run artifact-only and never apply the generated patch |
| `--autopatch-method` | `test_driven` | Agentic optimization method |
| `--autopatch-profile` | `question_flow` | Requested autopatch target profile |
| `--autopatch-target-file` | *(repeatable)* | Explicit complaint-generator target file override |
| `--use-recommended-autopatch-targets` | off | Replace the requested autopatch scope with the optimizer's recommended files/profile |
| `--json` | off | Print the full summary JSON |

**Examples:**

```bash
# Demo run (no API keys)
python3 hacc_adversarial_runner.py --demo --num-sessions 2 --max-turns 3

# Live run pinned to Codex through llm_router
python3 hacc_adversarial_runner.py \
  --num-sessions 5 \
  --max-turns 4 \
  --provider codex \
  --model gpt-5.3-codex

# Live run pinned to OpenAI through llm_router
python3 hacc_adversarial_runner.py \
  --num-sessions 5 \
  --max-turns 4 \
  --provider openai

# Emit an autopatch artifact with the recommended live Codex route (without applying)
python3 hacc_adversarial_runner.py \
  --provider codex \
  --model gpt-5.3-codex \
  --emit-autopatch \
  --no-apply-autopatch \
  --autopatch-method test_driven

# Emit an autopatch artifact using intake-driven recommended targets
python3 hacc_adversarial_runner.py \
  --provider codex \
  --model gpt-5.3-codex \
  --emit-autopatch \
  --use-recommended-autopatch-targets

# Apply autopatch to complaint-generator codebase through Codex
python3 hacc_adversarial_runner.py \
  --provider codex \
  --model gpt-5.3-codex \
  --apply-autopatch \
  --autopatch-method test_driven
```

**Autopatch dependency note:**

If the runner prints `Autopatch preflight ready: False`, install the complaint-generator Python dependencies first:

```bash
python3 -m pip install -r complaint-generator/requirements.txt
```

The current live autopatch path specifically requires `cachetools` in addition to the broader complaint-generator stack.

Autopatch apply note:

- If you pass `--apply-autopatch`, the runner applies the generated patch explicitly.
- If you pass `--emit-autopatch` without `--apply-autopatch`, the runner stays artifact-only and will not modify `complaint-generator`.
- If you pass `--no-apply-autopatch`, the runner stays artifact-only even when other automation or environment defaults would have allowed apply.
- The CLI summary still prints `env_default` so you can see legacy environment state, but explicit `--apply-autopatch` is now required for live patch application.

---

## Collection & Analysis Scripts

Located in `research_data/scripts/`. See `research_data/scripts/README.md` for full documentation.

### Core Pipeline

| Script | Description |
|--------|-------------|
| `run_collection.py` | Main orchestration: download → parse → index → report |
| `download_manager.py` | Download and deduplicate PDF URLs |
| `parse_pdfs.py` | Extract text from PDFs (with OCR fallback via `ocrmypdf`) |
| `index_and_tag.py` | Keyword indexing, risk scoring (0–3), applicability tagging |
| `report_generator.py` | Generate executive summaries, CSV spreadsheets, JSON indexes |
| `collect_brave.py` | Brave Search API integration for automated discovery |

### Advanced Discovery

| Script | Description |
|--------|-------------|
| `seeded_commoncrawl_discovery.py` | Historical web archive search via Common Crawl |
| `kg_violation_seed_queries.py` | Knowledge graph violation detection queries |
| `topic_triage_risk_gt0.py` | Risk-based document triage (filter Score > 0) |
| `audit_policy_kg_and_summaries.py` | Policy knowledge graph analysis |
| `extract_quantum_residential_documents.py` | Quantum Residential-specific document extraction |
| `download_hacc_documents.py` | Download HACC-specific public documents |
| `download_oregon_documents.py` | Download Oregon government documents |
| `batch_ocr_parallel.py` | Parallel OCR processing for scanned PDFs |
| `ingest_third_party_into_corpus.py` | Ingest third-party documents into the corpus |

### Risk Scoring (0–3)

Documents are scored by `index_and_tag.py`:

| Score | Meaning | Action |
|-------|---------|--------|
| 0 | No DEI/proxy language | Likely compliant |
| 1 | DEI/proxy terms present | Review context |
| 2 | DEI/proxy + mandatory language | Probable issue, review detail |
| 3 | Explicit DEI policy + binding language | Clear issue, immediate action |

### Red Flag Keywords

- **Explicit:** `diversity statement`, `BIPOC-only`, `underrepresented`, `minority-only`
- **Proxy:** `cultural competence`, `lived experience`, `safe space`, `equity plan`, `implicit bias`
- **Binding indicators:** `policy`, `shall`, `must`, `required`, `mandatory`

---

## Research Data & Corpus

### Pre-collected Documents (48+)

The repository contains a pre-collected corpus of Oregon government documents:

| Source | Documents | Coverage |
|--------|-----------|----------|
| Oregon Revised Statutes (ORS) | 7 chapters | ORS 456, 659, 659A, 279A, 279B, 279C, 183 |
| Oregon Administrative Rules (OAR) | 3 chapters | OAR 137, 659, 813 |
| Executive Orders | 30 orders | Governor's recent executive orders |
| State Agency Guidance | 7 sources | OHCS, BOLI, DAS |
| Federal Requirements | 1 source | HUD Fair Housing Act |

### Key Statutory Provisions Extracted (59)

| Statute | Provisions | Topic |
|---------|-----------|-------|
| ORS 456 (Housing Authorities) | 17 | Housing authority powers and duties |
| ORS 659A (Discrimination) | 15 | Protected class definitions and procedures |
| ORS 279A/C (Public Contracting) | 27 | MWESB requirements, procurement |

### DEI Term Analysis

- **703** total DEI-related term occurrences across the corpus
- **17 of 48** documents (35%) contain DEI-related terms
- Top sources: ORS 456 (169), ORS 659A (119), ORS 659 (102), ORS 279C (101), ORS 183 (75)

---

## Output Structure

```
research_results/
├── documents/
│   ├── raw/                         # Raw PDFs and HTML files
│   └── parsed/                      # Extracted text files (.txt)
├── search_indexes/                  # Lexical and vector search indexes
│   ├── hacc_index_manifest.json     # Lexical index manifest
│   ├── hacc_index_records.jsonl     # Lexical index records
│   └── hacc_corpus/                 # Vector index (if built)
├── adversarial_runs/
│   └── <timestamp>/
│       ├── adversarial_results.json
│       └── best_session_bundle.json
└── grounded_runs/
    └── <timestamp>/
        ├── grounding_bundle.json
        ├── mediator_evidence_packets.json
        ├── evidence_upload_report.json
        ├── mediator_state/           # DuckDB artifacts
        ├── adversarial/
        │   ├── adversarial_results.json
        │   └── best_session_bundle.json
        ├── complaint_synthesis/
        │   ├── draft_complaint_package.json
        │   └── draft_complaint_package.md
        └── run_summary.json
```

---

## Configuration

### Environment Variables

| Variable | Description |
|----------|-------------|
| `BRAVE_API_KEY` | Brave Search API key (free tier at [api.search.brave.com](https://api.search.brave.com)) |
| `HACC_AGENTIC_AUTOPATCH_TIMEOUT` | Timeout in seconds for agentic autopatch operations. Set to `none` / `0` to disable. |

### Autopatch Timeout Defaults

| Profile | Default Timeout |
|---------|----------------|
| `phase_manager_action_only` | 120 s |
| `denoiser_select_candidates_only` | 150 s |
| `denoiser_standard_intake_only` | 150 s |
| `denoiser_process_answer_only` | 180 s |
| `phase_manager_only` | 180 s |
| `denoiser_focus` | 240 s |
| `question_flow` | 300 s |
| `full_mediator` | 420 s |

### Optional Integrations

The `hacc_research` engine integrates with the following optional packages from `complaint-generator/integrations/`:

| Integration | Capability | Fallback |
|-------------|-----------|---------|
| `ipfs_datasets` | Vector indexing, web search, web scraping | Lexical search only |
| `ipfs_datasets.legal` | Federal Register, U.S. Code, RECAP search | Disabled |
| `ipfs_datasets.graphs` | Knowledge graph extraction from text | Disabled |

All integrations degrade gracefully — the engine works in lexical-only mode when integrations are unavailable.

### LLM Provider Routing

The adversarial runner and grounded pipeline support multiple LLM providers via `complaint-generator`'s router:

| Provider | Flag |
|----------|------|
| Codex | `--provider codex --model gpt-5.3-codex` |
| OpenAI (GPT) | `--provider openai` |
| Anthropic (Claude) | `--provider anthropic` |
| Google Gemini | `--provider gemini` |
| Demo (deterministic) | `--demo` |

---

## Testing

The `tests/` directory contains 13+ test files:

| File | Coverage |
|------|----------|
| `test_hacc_research_engine.py` | `HACCResearchEngine` — corpus loading, search, grounding |
| `test_hacc_grounded_pipeline.py` | End-to-end grounded pipeline |
| `test_hacc_adversarial_runner.py` | Adversarial batch runner |
| `test_hacc_evidence_seed_generation.py` | Evidence seed generation |
| `test_phase_manager.py` | Complaint phase manager (base) |
| `test_phase_manager_additional.py` | Phase manager additional cases |
| `test_phase_manager_additional_comprehensive.py` | Comprehensive phase manager |
| `test_phase_manager_advanced.py` | Advanced phase manager scenarios |
| `test_phase_manager_comprehensive.py` | Phase manager full coverage |
| `test_phase_manager_extra_coverage.py` | Phase manager edge cases |
| `test_phase_manager_optimizer.py` | Phase manager optimizer |
| `test_workflow_wrappers.py` | Workflow integration tests |

**Run all tests:**

```bash
python -m pytest tests/ -v
```

**Run a specific module:**

```bash
python -m pytest tests/test_hacc_research_engine.py -v
python -m pytest tests/test_hacc_grounded_pipeline.py -v
```

---

## Key Concepts

### Applicability Areas

Oregon policies are tagged against four areas of Housing Authority operations:

| Area | Description |
|------|-------------|
| **Hiring** | Employment decisions and job postings |
| **Procurement** | Vendor and contractor selection (MWESB) |
| **Training** | Mandatory staff trainings |
| **Housing** | Program eligibility, leases, and operations |

### Compliance Categories

| Category | Binding? |
|----------|---------|
| Oregon Revised Statutes (ORS 456, 659A, 279A/C) | Likely binding |
| Oregon Administrative Rules (OAR 137, 659, 813) | Likely binding |
| Fair Housing Act / HUD requirements | Federal binding |
| Governor's Executive Orders | Advisory — review for applicability |
| State Agency Guidance (OHCS, BOLI, DAS) | Advisory — review for applicability |

### Filing Forums

| Forum | Flag | Description |
|-------|------|-------------|
| Federal court | `--filing-forum court` | Civil rights lawsuit |
| HUD | `--filing-forum hud` | HUD fair housing complaint |
| State agency | `--filing-forum state_agency` | Oregon state agency complaint |

---

## Disclaimers

> ⚠️ **NOT LEGAL ADVICE.** This system produces research only. Consult qualified legal counsel before taking any action based on these findings.

> ⚠️ **INTERPRETATION REQUIRED.** Statutory language requires legal interpretation. What applies to HACC depends on specific circumstances, funding sources, and current case law.

> ⚠️ **POINT IN TIME.** The pre-collected corpus was assembled December 30–31, 2025. Laws and regulations may have changed. Verify current status before relying on findings.

> ⚠️ **VERIFICATION NEEDED.** While sources are official government documents, verify critical information through direct consultation with Oregon legal resources.

---

## References

- **Agent Audit Guide:** [`agent.md`](./agent.md)
- **Evidence Request Template:** [`EVIDENCE_REQUEST_TEMPLATE.md`](./EVIDENCE_REQUEST_TEMPLATE.md)
- **Collection Toolkit Docs:** [`research_data/scripts/README.md`](./research_data/scripts/README.md)
- **Research Methodology:** [`RESEARCH_SUMMARY.md`](./RESEARCH_SUMMARY.md)
- **Executive Brief:** [`EXECUTIVE_BRIEF.txt`](./EXECUTIVE_BRIEF.txt)
- **Source Memo:** Attorney General Bondi, *Guidance for Recipients of Federal Funding Regarding Unlawful Discrimination* (July 2025) — [`Memo from Attorney General Bondi Guidance.md`](./Memo%20from%20Attorney%20General%20Bondi%20Guidance.md)
