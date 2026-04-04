# Communications Ingest

This repo now supports a combined Gmail + Google Voice evidence workflow, including:

- consumer Google Takeout Voice exports
- Google Workspace Vault Voice exports
- Google Workspace Data Export Voice bundles, including `gs://` staging
- local watch-folder automation that hydrates newly dropped Voice exports

## Main Entry Points

### 1. Google Voice only

Use [run-google-voice-ingest.sh](/home/barberb/HACC/run-google-voice-ingest.sh):

```bash
./run-google-voice-ingest.sh --source ~/Downloads/takeout-voice.zip
```

Vault export example:

```bash
./run-google-voice-ingest.sh \
  --source ./vault-voice-export.zip \
  --source-mode vault
```

Workspace Data Export example:

```bash
./run-google-voice-ingest.sh \
  --source gs://workspace-export/voice \
  --source-mode data-export \
  --import-arg --upload-to-workspace
```

To export portable bundle artifacts for the materialized Voice corpus:

```bash
./run-google-voice-ingest.sh \
  --source ~/Downloads/takeout-voice.zip \
  --bundle-output-dir ./voice-bundles \
  --bundle-format zip \
  --bundle-format parquet \
  --bundle-format car
```

What it does:

1. Materializes Google Voice Takeout data with `ipfs-datasets email google-voice`.
2. Reuses the generated `google_voice_manifest.json` with [import_gmail_evidence.py](/home/barberb/HACC/import_gmail_evidence.py).
3. Rebuilds the history index unless `--skip-index` is used.

Useful options:

- `--case-slug my-case`
- `--materialized-dir ./voice-bundles`
- `--skip-index`
- `--import-arg ...`
- `--index-arg ...`
- `--bundle-output-dir ./voice-bundles`
- `--bundle-format zip|parquet|car`

### 2. Gmail + Google Voice together

Use [run-communications-ingest.sh](/home/barberb/HACC/run-communications-ingest.sh):

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --google-voice-source ~/Downloads/takeout-voice.zip
```

Useful examples:

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --gmail-arg --address --gmail-arg tenant@example.com \
  --google-voice-source ./voice-bundles/google_voice_manifest.json
```

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --google-voice-source ./Takeout/Voice \
  --index-arg --fast
```

If you want the combined wrapper to export Google Voice bundle artifacts too:

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --google-voice-source ./Takeout/Voice \
  --voice-bundle-output-dir ./voice-bundles \
  --voice-bundle-format zip
```

## Lower-Level Building Blocks

### Package CLI: parse or materialize Google Voice

```bash
ipfs-datasets email google-voice ./Takeout/Voice --summary-only
ipfs-datasets email google-voice ./Takeout/Voice --materialize --output-dir ./voice-bundles
ipfs-datasets email google-voice-vault ./vault-voice-export.zip --summary-only
ipfs-datasets email google-voice-data-export gs://workspace-export/voice --materialize --output-dir ./voice-bundles --staging-dir ./gcs-stage
```

Materialized output includes:

- `google_voice_manifest.json`
- one bundle directory per event
- `event.json`
- `transcript.txt`
- copied `source.html`
- copied sidecar attachments
- `mediator_evidence_records` in the manifest

### Package CLI: watch a folder and auto-hydrate new exports

```bash
ipfs-datasets email google-voice-watch ./voice-dropbox \
  --output-dir ./hydrated-voice \
  --source-kind takeout
```

One-shot scan example:

```bash
ipfs-datasets email google-voice-watch ./voice-dropbox \
  --output-dir ./hydrated-voice \
  --source-kind vault_export \
  --once
```

### Package CLI: consumer Takeout URL and browser capture

Build a documented custom Takeout URL:

```bash
ipfs-datasets email google-voice-takeout-url \
  --product-id voice \
  --dest drive
```

Use saved Takeout page source to infer likely Voice `data-id` values:

```bash
ipfs-datasets email google-voice-takeout-url \
  --page-source ./takeout_page.html \
  --dest drive
```

Open the Takeout flow in Playwright and wait for a downloaded archive:

```bash
ipfs-datasets email google-voice-takeout-capture \
  --page-source ./takeout_page.html \
  --dest drive \
  --downloads-dir ./takeout-downloads
```

Capture Takeout page source directly:

```bash
ipfs-datasets email google-voice-takeout-source \
  --output ./takeout_page.html
```

Poll later for a completed archive in an existing downloads directory:

```bash
ipfs-datasets email google-voice-takeout-poll \
  --downloads-dir ./takeout-downloads
```

Poll Google Drive for a Takeout artifact and download it locally:

```bash
ipfs-datasets email google-voice-takeout-drive \
  --client-secrets ./google-client-secret.json \
  --account-hint user@gmail.com \
  --download-dir ./takeout-downloads
```

### Repo wrapper: consumer Takeout acquisition plus hydration

Use [run-consumer-google-voice-takeout.sh](/home/barberb/HACC/run-consumer-google-voice-takeout.sh):

```bash
./run-consumer-google-voice-takeout.sh \
  --page-source ./takeout_page.html \
  --dest drive
```

To auto-export portable case bundles after hydration:

```bash
./run-consumer-google-voice-takeout.sh \
  --product-id voice \
  --bundle-output-dir ./takeout-bundles \
  --bundle-format zip \
  --bundle-format parquet \
  --bundle-format car
```

If you need the wrapper to capture page source first:

```bash
./run-consumer-google-voice-takeout.sh \
  --capture-page-source \
  --page-source ./takeout_page.html \
  --dest drive
```

If Google is still building the export, resume later from the same downloads directory:

```bash
./run-consumer-google-voice-takeout.sh \
  --resume-from-downloads ./takeout-downloads \
  --skip-index
```

Or resume directly from the saved acquisition manifest:

```bash
./run-consumer-google-voice-takeout.sh \
  --resume-from-manifest ./takeout-acquisition.json \
  --skip-index
```

If the Takeout destination is Drive, let the wrapper fall back to Drive polling/download:

```bash
./run-consumer-google-voice-takeout.sh \
  --page-source ./takeout_page.html \
  --dest drive \
  --drive-client-secrets ./google-client-secret.json \
  --drive-account-hint user@gmail.com
```

This wrapper:

1. Builds the consumer Takeout URL from `--product-id` values or inferred page-source `data-id` values.
2. Opens the Takeout page in Playwright and waits for a downloadable archive.
3. Hands the downloaded archive to [run-google-voice-ingest.sh](/home/barberb/HACC/run-google-voice-ingest.sh) for hydration/import/indexing.

By default it also writes an acquisition record next to the downloads directory:

- `takeout_acquisition_manifest.json`

You can override that path with:

```bash
./run-consumer-google-voice-takeout.sh \
  --page-source ./takeout_page.html \
  --acquisition-manifest ./takeout-acquisition.json
```

The acquisition manifest records:

- case slug
- selected product ids
- page source path
- capture JSON path
- Drive fallback settings
- capture/poll/Drive fallback payloads
- final hydrated archive path when successful
- lifecycle events like `initialized`, `capture_attempted`, `drive_fallback_attempted`, and `hydrated`

Quick status summary for a saved acquisition manifest:

```bash
ipfs-datasets email google-voice-takeout-status ./takeout_acquisition_manifest.json
```

Case-level summary for a Takeout downloads directory or manifest:

```bash
ipfs-datasets email google-voice-takeout-case-summary ./takeout_acquisition_manifest.json
```

Export a markdown or HTML case report:

```bash
ipfs-datasets email google-voice-takeout-case-report \
  ./takeout_acquisition_manifest.json \
  --format markdown \
  --output ./takeout-report.md
```

Bundle the latest manifest, recent history snapshots, and reports into one archival folder:

```bash
ipfs-datasets email google-voice-takeout-case-bundle \
  ./takeout_acquisition_manifest.json \
  --output-dir ./takeout-bundles
```

You can also emit portable bundle artifacts alongside the bundle directory:

```bash
ipfs-datasets email google-voice-takeout-case-bundle \
  ./takeout_acquisition_manifest.json \
  --output-dir ./takeout-bundles \
  --bundle-format zip \
  --bundle-format parquet \
  --bundle-format car
```

Supported bundle formats:
- `dir`: the default bundle directory
- `zip`: compressed archive of the bundle directory
- `parquet`: flattened case summary/history/report metadata table
- `car`: IPFS CAR archive of the bundle directory

Archived manifest history snapshots:

```bash
ipfs-datasets email google-voice-takeout-history ./takeout_acquisition_manifest.json
```

Prune old archived snapshots, keeping the newest 20:

```bash
ipfs-datasets email google-voice-takeout-prune ./takeout_acquisition_manifest.json --keep 20
```

Suggested next action for a saved acquisition manifest:

```bash
ipfs-datasets email google-voice-takeout-doctor ./takeout_acquisition_manifest.json
```

Watch a saved acquisition manifest and keep advancing it until complete:

```bash
./watch-consumer-google-voice-takeout.sh \
  --manifest ./takeout_acquisition_manifest.json
```

One-command bootstrap plus watch:

```bash
./run-and-watch-consumer-google-voice-takeout.sh \
  --product-id voice \
  --acquisition-manifest ./takeout_acquisition_manifest.json
```

The bootstrap wrapper also accepts bundle-export flags and forwards them into both the initial run and any watch-time resume pass:

```bash
./run-and-watch-consumer-google-voice-takeout.sh \
  --product-id voice \
  --acquisition-manifest ./takeout_acquisition_manifest.json \
  --bundle-output-dir ./takeout-bundles \
  --bundle-format zip
```

Important:

- This is still human-assisted browser automation, not an official consumer Takeout archive-creation API.
- Google may require login, 2FA, re-authentication, or extra confirmation before export creation.
- If the export is still processing after timeout, the wrapper stops after writing `takeout_capture.json`; rerun later or point the archive into the normal ingest path directly.
- If no desktop display is available, the consumer wrapper now records a `manual_browser_required` state in the acquisition manifest instead of crashing, so you can resume later on a machine with a browser session.
- The Drive fallback uses Drive read-only OAuth and searches for files whose names contain `takeout` by default; adjust the wrapper/CLI if your Drive export naming differs.
- If Google Drive first exposes a Takeout folder and only later places zip parts inside it, the Drive fallback now traverses that folder automatically to find downloadable archive files.
- When the wrapper has a recorded export kickoff time, the Drive fallback also narrows its search to artifacts modified after that timestamp so older unrelated Takeout files are less likely to match.

### Repo importer: Gmail and/or Google Voice

[import_gmail_evidence.py](/home/barberb/HACC/import_gmail_evidence.py) supports:

- Gmail IMAP import
- Google Voice raw Takeout import
- Google Voice raw Vault export import
- Google Voice raw Data Export import after package materialization
- Google Voice manifest reuse
- Gmail/Google Voice dedupe

Examples:

```bash
/home/barberb/HACC/.venv/bin/python import_gmail_evidence.py \
  --google-voice-source ./voice-bundles/google_voice_manifest.json \
  --case-slug voice-demo
```

```bash
/home/barberb/HACC/.venv/bin/python import_gmail_evidence.py \
  --folder "[Gmail]/All Mail" \
  --google-voice-source ./voice-bundles/google_voice_manifest.json \
  --case-slug communications-demo
```

### Combined wrapper with Voice mode selection

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --google-voice-source ./vault-voice-export.zip \
  --google-voice-mode vault
```

## Indexing and Search

### Rebuild the index

Use [run-history-index.sh](/home/barberb/HACC/run-history-index.sh):

```bash
./run-history-index.sh
```

To export portable bundle artifacts for the finished index:

```bash
./run-history-index.sh \
  --bundle-output-dir ./history-index-bundles \
  --bundle-format zip \
  --bundle-format parquet \
  --bundle-format car
```

By default it indexes:

- [evidence/history](/home/barberb/HACC/evidence/history)
- [evidence/email_imports](/home/barberb/HACC/evidence/email_imports)

It writes:

- `chunks.jsonl`
- `graph.jsonld`
- vector artifacts
- DuckDB index
- optional bundle artifacts: `zip`, `parquet`, `car`

### DuckDB search

```bash
/home/barberb/HACC/.venv/bin/python search_history_duckdb.py "inspection notice"
ipfs-datasets history-index --table entities tenant
ipfs-datasets history-index --table documents --source-like google_voice voice --json
```

### Semantic search

```bash
/home/barberb/HACC/.venv/bin/python search_history_index.py "google voice text"
```

## Case Archival

To collect the latest Takeout, Voice, and history bundle artifacts into one case archive:

```bash
./run-case-archive.sh \
  --case-slug housing-case \
  --takeout-manifest ./takeout-downloads/takeout_acquisition_manifest.json \
  --voice-bundle-result ./materialized/google_voice_case_bundle.json \
  --history-bundle-result ./research_results/history_index_20260404_120000/history_index_bundle.json \
  --output-dir ./case-archives \
  --bundle-format zip \
  --bundle-format parquet \
  --bundle-format car
```

This wrapper gathers the referenced component artifacts into one archive directory and can also emit a top-level `zip`, `parquet`, and `car` for the whole case.

If your artifacts already live under the repo’s normal output layout, you can also let the wrapper auto-discover the newest matching Takeout, Voice, and history bundle results by case slug:

```bash
./run-case-archive.sh \
  --case-slug housing-case \
  --discover \
  --bundle-format zip
```

## One-Shot Closeout

To run communications ingest, bundle the rebuilt history index, and produce the final case archive in one command:

```bash
./run-case-closeout.sh \
  --case-slug housing-case \
  --google-voice-source ./Takeout/Voice \
  --voice-bundle-format zip \
  --history-bundle-format zip \
  --archive-bundle-format zip
```

This wrapper orchestrates:
1. [run-communications-ingest.sh](/home/barberb/HACC/run-communications-ingest.sh)
2. [run-history-index.sh](/home/barberb/HACC/run-history-index.sh)
3. [run-case-archive.sh](/home/barberb/HACC/run-case-archive.sh) in discovery mode

It also writes a closeout result JSON under the archive output directory, plus per-step logs for communications ingest, history indexing, and final archival.

## Dedupe Behavior

If the same Google Voice content appears both:

- as a Gmail notification email from `txt.voice.google.com`
- and as a direct Google Voice event

the direct Google Voice event is treated as the source of truth and the Gmail notification copy is suppressed from the imported communication corpus.

## Recommended Workflow

For a full combined run:

```bash
./run-communications-ingest.sh \
  --gmail-folder "[Gmail]/All Mail" \
  --google-voice-source ~/Downloads/takeout-voice.zip \
  --case-slug housing-communications
```

For a Voice-only run:

```bash
./run-google-voice-ingest.sh \
  --source ~/Downloads/takeout-voice.zip \
  --case-slug housing-voice
```

## Smoke Tests

The wrapper-level smoke tests live in [test_google_voice_integration.py](/home/barberb/HACC/tests/test_google_voice_integration.py) and use the `communications_smoke` pytest marker.

Run just the communications smoke tests:

```bash
/home/barberb/HACC/.venv/bin/python -m pytest -q -m communications_smoke /home/barberb/HACC/tests/test_google_voice_integration.py
```

Run the full focused Gmail/Google Voice suite:

```bash
/home/barberb/HACC/.venv/bin/python -m pytest -q /home/barberb/HACC/tests/test_google_voice_integration.py /home/barberb/HACC/tests/test_import_gmail_evidence.py
```
