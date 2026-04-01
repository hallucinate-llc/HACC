# DEI Compliance Collection & Analysis Toolkit

A Python-based toolkit for collecting, parsing, and analyzing State of Oregon policy documents to identify references to DEI, equity, diversity, and related proxies/euphemisms that could be binding on the Housing Authority of Clackamas County.

## Overview

This toolkit supports the audit described in `agent.md` by automating:
1. **Collection**: Search and download PDFs from Oregon.gov, Clackamas.us, and related sources via Brave Search API, Common Crawl, or local file ingestion.
2. **Parsing**: Extract text from PDFs (with OCR fallback for scanned documents).
3. **Indexing**: Tag documents with keywords (DEI, proxies, binding indicators) and applicability areas.
4. **Reporting**: Generate one-page summaries and detailed technical reports.

## Components

### Scripts

- **`download_manager.py`** — Download and deduplicate URLs; store metadata and raw PDFs.
- **`parse_pdfs.py`** — Extract text from PDFs using `pdftotext` and OCR (fallback).
- **`index_and_tag.py`** — Build searchable index; score documents by risk (0–3).
- **`report_generator.py`** — Generate executive summaries and detailed findings.
- **`collect_brave.py`** — Search via Brave Search API (requires API key).
- **`collect_cc.py`** — Query Common Crawl historical index (TODO: implement).
- **`collect_google.py`** — Query Google Custom Search API (requires API key, TODO).
- **`run_collection.py`** — Main orchestration script; runs full workflow.

### Supporting Files

- **`agent.md`** — Audit guide and strategy (in parent directory).
- **`EVIDENCE_REQUEST_TEMPLATE.md`** — Template for requesting evidence from organizations.

## Installation & Setup

### Requirements

- Python 3.8+
- `pdftotext` (from `poppler-utils`): Extract text from PDFs
- `ocrmypdf` (optional): OCR for scanned PDFs
- `tesseract-ocr` (optional): OCR engine used by `ocrmypdf`
- `requests` library: HTTP requests

### Install Dependencies (Ubuntu/Debian)

```bash
# System packages
sudo apt-get update
sudo apt-get install -y poppler-utils ocrmypdf tesseract-ocr

# Python packages
pip install requests
```

### API Keys (Optional)

To enable search via APIs, set environment variables:

```bash
export BRAVE_API_KEY="your_brave_api_key_here"
export GOOGLE_API_KEY="your_google_api_key_here"
export GOOGLE_CX="your_google_custom_search_engine_id"
```

(Brave Search API: https://api.search.brave.com — free tier available)

## Usage

### Quick Start: Full Workflow

Run the complete collection, parsing, and reporting pipeline:

```bash
cd /path/to/project
python3 research_data/scripts/run_collection.py
```

This will:
1. Identify search topics for Oregon DEI references
2. (Skip downloads if no API key — manual upload needed)
3. Index any existing PDFs in `research_results/documents/raw/`
4. Generate JSON index, CSV summary, and one-page findings report

### With Local PDFs

If you have PDFs already downloaded (manual process or prior run):

```bash
python3 research_data/scripts/run_collection.py --pdf-dir research_results/documents/raw/
```

### With Brave API Key

To enable automatic PDF downloads:

```bash
export BRAVE_API_KEY="your_key"
python3 research_data/scripts/run_collection.py
```

### Individual Script Usage

#### Download PDFs

```python
from download_manager import DownloadManager

dm = DownloadManager()
urls = [
    {"url": "https://example.oregon.gov/policy.pdf", "source": "oregon.gov"},
]
filepaths = dm.batch_download(urls)
```

#### Parse PDFs

```python
from parse_pdfs import PDFParser

parser = PDFParser()
metadata = {"url": "...", "source": "..."}
parsed_path = parser.parse_pdf("path/to/file.pdf", metadata)
```

#### Index & Tag

```python
from index_and_tag import DocumentIndexer

indexer = DocumentIndexer()
indexer.batch_index()
index_file = indexer.save_index()
csv_file = indexer.export_csv_summary()
```

#### Generate Reports

```python
from report_generator import ReportGenerator

gen = ReportGenerator()
gen.load_index("research_results/document_index_YYYYMMDD.json")
summary = gen.save_summary()
detailed = gen.save_detailed_report()
```

## Output Files

After running the workflow, you'll find:

- **`research_results/document_index_YYYYMMDD_HHMMSS.json`** — Full searchable index
- **`research_results/summary_YYYYMMDD_HHMMSS.csv`** — CSV summary (risk score, keywords, areas)
- **`research_results/FINDINGS_YYYYMMDD_HHMMSS.txt`** — One-page executive summary
- **`research_results/DETAILED_REPORT_YYYYMMDD_HHMMSS.txt`** — Technical deep-dive
- **`research_results/download_manifest.json`** — Metadata for downloaded PDFs
- **`research_results/documents/parse_manifest.json`** — Metadata for parsed PDFs
- **`research_results/documents/raw/`** — Raw PDF files
- **`research_results/documents/parsed/`** — Extracted text and metadata

## Keyword & Scoring Reference

### DEI Keywords
`diversity`, `equity`, `inclusion`, `dei`, `deia`, `deib`, `underrepresented`, `underserved`

### Proxy Keywords (Red Flags)
`cultural competence`, `lived experience`, `diversity statement`, `safe space`, `bipoc`, `minority-only`, `first-generation`, `low-income targeting`, `equity plan`

### Binding Indicators
`policy`, `ordinance`, `statewide`, `contract`, `agreement`, `required`, `must`, `shall`, `mandatory`, `applicable to`

### Applicability Tags
- `hiring` — Affects employment decisions
- `procurement` — Affects vendor/contractor selection
- `training` — Affects mandatory trainings or development
- `housing` — Affects housing eligibility or operation

### Risk Scoring

| Score | Meaning | Action |
|-------|---------|--------|
| 0 | Compliant; no DEI/proxy language | Review noted; no issue |
| 1 | Possible issue; DEI/proxy present but weak binding indicators | Review for context |
| 2 | Probable issue; DEI/proxy + binding indicators | Prioritize for detailed review |
| 3 | Clear violation; explicit mandatory DEI policy | Immediate legal review & remediation |

## Troubleshooting

### `pdftotext` not found

Install poppler-utils:
```bash
sudo apt-get install poppler-utils
```

### PDF extraction returns little/no text

Try OCR:
```bash
ocrmypdf input.pdf output.pdf
pdftotext -layout output.pdf output.txt
```

### API key errors

Verify your API key is set and valid:
```bash
echo $BRAVE_API_KEY
```

### Out of memory on large PDFs

Reduce batch size or increase system RAM.

## Next Steps

1. **Collect Evidence**: Use `EVIDENCE_REQUEST_TEMPLATE.md` to request documents from relevant organizations.
2. **Manual Downloads**: Manually download PDFs from Oregon.gov and place in `research_results/documents/raw/`.
3. **Run Analysis**: Execute `run_collection.py` to parse and index.
4. **Review Findings**: Read `FINDINGS_*.txt` for high-risk documents.
5. **Detailed Review**: Open `DETAILED_REPORT_*.txt` and the CSV for full analysis.
6. **Remediation**: Use `agent.md` checklist to assess HA policies against findings.

## Integration with Agent Audit Framework

This toolkit is designed to support the agent-based audit framework in `agent.md`. Results feed directly into:
- The **Search & Collection Strategy** section
- Evidence collection for the **Audit Checklist**
- Supporting the **Red Flags / Indicators** identification
- Providing data for the **Remediation Steps**

## Tips

- **Prioritize High-Risk**: Focus first on documents with score ≥ 2.
- **Cross-Reference**: Check if documents are "statewide policy" or "model policy" — these often apply to local entities.
- **Interview Stakeholders**: Use findings to guide questions for HR, procurement, and program staff.
- **Document Everything**: Keep copies of all original PDFs and parsed texts for audit trail.

## Support & Questions

Refer to `agent.md` for audit strategy and to `EVIDENCE_REQUEST_TEMPLATE.md` for evidence requests.

---

**Version**: 1.0  
**Last Updated**: 2025-12-31  
**Author**: Housing Authority Compliance Team
