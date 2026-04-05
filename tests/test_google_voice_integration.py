from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from email.message import EmailMessage
import email.policy
import importlib
import json
import os
import subprocess
import pytest

import import_gmail_evidence as gmail_module
import index_evidence_history_with_ipfs_datasets as history_index_module
import search_history_duckdb as duckdb_search_module


def _build_voice_takeout(tmp_path: Path) -> Path:
    voice_dir = tmp_path / "Takeout" / "Voice" / "Messages" / "thread-001"
    voice_dir.mkdir(parents=True)
    html_path = voice_dir / "Text - Housing Advocate.html"
    html_path.write_text(
        """
        <html>
          <head><title>Text conversation with (503) 555-0100</title></head>
          <body>
            <div>2026-03-24T04:56:14Z</div>
            <div>Tenant: Please send the inspection notice.</div>
            <div>Advocate: I will send it tonight.</div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    (voice_dir / "metadata.json").write_text(
        '{"participants":["(503) 555-0100"],"labels":["housing"]}',
        encoding="utf-8",
    )
    (voice_dir / "notice.jpg").write_bytes(b"fake-jpg")
    (voice_dir / "voicemail.mp3").write_bytes(b"fake-mp3")
    return tmp_path


def _build_voice_vault_export(tmp_path: Path) -> Path:
    voice_dir = tmp_path / "Exports" / "Voice" / "users" / "tenant@example.com" / "conversation-001"
    voice_dir.mkdir(parents=True)
    (voice_dir / "conversation.html").write_text(
        """
        <html>
          <head><title>Voicemail from (503) 555-0101</title></head>
          <body>
            <div>2026-03-25T09:15:00Z</div>
            <div>Voicemail transcript: Please call me back about the inspection.</div>
          </body>
        </html>
        """,
        encoding="utf-8",
    )
    (voice_dir / "call-log.json").write_text(
        '{"direction":"incoming","participants":["(503) 555-0101"]}',
        encoding="utf-8",
    )
    (voice_dir / "voicemail.mp3").write_bytes(b"vault-mp3")
    return tmp_path


def _build_voice_data_export(tmp_path: Path) -> Path:
    voice_dir = tmp_path / "workspace-export" / "voice" / "tenant-001"
    voice_dir.mkdir(parents=True)
    (voice_dir / "messages.txt").write_text(
        "2026-03-26T12:30:00Z Tenant +1 (503) 555-0102 asked for a copy of the notice.",
        encoding="utf-8",
    )
    (voice_dir / "metadata.json").write_text(
        '{"participants":["+1 (503) 555-0102"],"type":"text"}',
        encoding="utf-8",
    )
    return tmp_path


def test_google_voice_processor_parses_takeout_directory(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path)
    processor = gmail_module.GoogleVoiceProcessor()
    try:
        result = processor.parse_takeout(takeout_root)
    finally:
        processor.close()

    assert result["status"] == "success"
    assert result["event_count"] == 1
    event = result["events"][0]
    assert event["event_type"] == "text_message"
    assert "(503) 555-0100" in event["phone_numbers"]
    assert event["timestamp"] == "2026-03-24T04:56:14+00:00"
    assert "inspection notice" in event["text_content"].lower()
    assert any(path.endswith("voicemail.mp3") for path in event["sidecar_paths"])


def test_google_voice_materialization_appends_attachment_enrichments_to_transcript(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")
    voice_module = importlib.import_module("ipfs_datasets_py.processors.multimedia.google_voice_processor")

    def _fake_ocr(path: Path) -> tuple[str, dict[str, object]]:
        assert path.name == "notice.jpg"
        return "Scanned inspection notice from image", {"status": "success", "backend": "test_ocr"}

    def _fake_transcribe(path: Path) -> tuple[str, dict[str, object]]:
        assert path.name == "voicemail.mp3"
        return "Voicemail says the inspector will arrive at 9 AM", {
            "status": "success",
            "backend": "test_whisper",
        }

    monkeypatch.setattr(voice_module, "_ocr_image_path", _fake_ocr)
    monkeypatch.setattr(voice_module, "_transcribe_audio_path", _fake_transcribe)

    processor = gmail_module.GoogleVoiceProcessor()
    try:
        exported = processor.export_bundles(takeout_root, output_dir=tmp_path / "materialized")
    finally:
        processor.close()

    bundle = exported["bundles"][0]
    transcript_text = Path(bundle["transcript_path"]).read_text(encoding="utf-8")
    event_payload = json.loads(Path(bundle["event_json_path"]).read_text(encoding="utf-8"))

    assert "inspection notice" in transcript_text.lower()
    assert "Scanned inspection notice from image" in transcript_text
    assert "Voicemail says the inspector will arrive at 9 AM" in transcript_text
    assert len(bundle["enrichments"]) == 2
    assert all(Path(path).is_file() for path in bundle["enrichment_paths"])
    assert event_payload["enrichment_count"] == 2
    assert {item["metadata"]["backend"] for item in event_payload["enrichments"]} == {"test_ocr", "test_whisper"}


def test_google_voice_plain_text_extraction_skips_style_and_script_blocks() -> None:
    voice_module = importlib.import_module("ipfs_datasets_py.processors.multimedia.google_voice_processor")
    html_text = """
    <html>
      <head>
        <style>body { color: red; }</style>
        <script>console.log('hidden');</script>
        <title>Missed call from Tenant</title>
      </head>
      <body>
        <div>2026-04-05T01:02:03Z</div>
        <div>Please call me back about the inspection notice.</div>
      </body>
    </html>
    """

    text = voice_module._extract_plain_text(html_text)

    assert "inspection notice" in text.lower()
    assert "body { color: red; }" not in text
    assert "console.log" not in text


def test_google_voice_processor_parses_vault_export(tmp_path: Path) -> None:
    export_root = _build_voice_vault_export(tmp_path)
    processor = gmail_module.GoogleVoiceProcessor()
    try:
        result = processor.parse_vault_export(export_root)
    finally:
        processor.close()

    assert result["status"] == "success"
    assert result["source_kind"] == "vault_export"
    assert result["event_count"] == 1
    event = result["events"][0]
    assert event["event_type"] == "voicemail"
    assert "(503) 555-0101" in event["phone_numbers"]
    assert "inspection" in event["text_content"].lower()


def test_google_voice_processor_parses_local_data_export(tmp_path: Path) -> None:
    export_root = _build_voice_data_export(tmp_path)
    processor = gmail_module.GoogleVoiceProcessor()
    try:
        result = processor.parse_data_export(export_root)
    finally:
        processor.close()

    assert result["status"] == "success"
    assert result["source_kind"] == "data_export"
    assert result["event_count"] == 1
    event = result["events"][0]
    assert event["event_type"] == "text_message"
    assert "copy of the notice" in event["text_content"].lower()


def test_history_index_image_ocr_uses_tesseract_cli_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    image_path = tmp_path / "notice.png"
    image_path.write_bytes(b"fake-png")

    def _fake_run(command: list[str], check: bool, capture_output: bool, text: bool, timeout: int):
        assert command[:2] == ["tesseract", str(image_path)]
        return SimpleNamespace(returncode=0, stdout="Inspection photo text", stderr="")

    monkeypatch.setattr(history_index_module.shutil, "which", lambda name: "/usr/bin/tesseract" if name == "tesseract" else None)
    monkeypatch.setattr(history_index_module.subprocess, "run", _fake_run)

    text = history_index_module._extract_image_text_ocr(image_path)

    assert "Inspection photo text" in text


def test_import_gmail_evidence_supports_google_voice_without_gmail_login(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")
    args = SimpleNamespace(
        address=[],
        address_file=[],
        from_address=[],
        from_address_file=[],
        to_address=[],
        to_address_file=[],
        address_domain=[],
        address_domain_file=[],
        from_domain=[],
        from_domain_file=[],
        to_domain=[],
        to_domain_file=[],
        complaint_query=None,
        complaint_keyword=[],
        complaint_keyword_file=[],
        min_relevance_score=1.0,
        search="ALL",
        since_date=None,
        before_date=None,
        subject_contains=None,
        output_dir=str(tmp_path / "imports"),
        case_slug="voice-demo",
        server="imap.gmail.com",
        port=993,
        username=None,
        password=None,
        no_ssl=False,
        timeout=30,
        auth_mode="gmail_app_password",
        gmail_oauth_client_secrets=None,
        gmail_oauth_token_cache=None,
        no_browser=False,
        folder=[],
        google_voice_source=[str(takeout_root)],
        limit=10,
        dry_run=False,
        crawl_max_messages=None,
        crawl_batch_size=250,
        crawl_start_offset=0,
    )

    result = gmail_module.anyio.run(lambda: gmail_module.import_gmail_evidence(args))

    assert result["matched_email_count"] == 0
    assert result["matched_google_voice_count"] == 1
    record = result["google_voice_events"][0]
    assert Path(record["parsed_path"]).is_file()
    assert Path(record["transcript_path"]).read_text(encoding="utf-8")
    assert record["event_type"] == "text_message"


def test_import_gmail_evidence_can_reuse_google_voice_manifest(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")
    processor = gmail_module.GoogleVoiceProcessor()
    try:
        exported = processor.export_bundles(takeout_root, output_dir=tmp_path / "materialized")
    finally:
        processor.close()

    args = SimpleNamespace(
        address=[],
        address_file=[],
        from_address=[],
        from_address_file=[],
        to_address=[],
        to_address_file=[],
        address_domain=[],
        address_domain_file=[],
        from_domain=[],
        from_domain_file=[],
        to_domain=[],
        to_domain_file=[],
        complaint_query=None,
        complaint_keyword=[],
        complaint_keyword_file=[],
        min_relevance_score=1.0,
        search="ALL",
        since_date=None,
        before_date=None,
        subject_contains=None,
        output_dir=str(tmp_path / "imports"),
        case_slug="voice-manifest-demo",
        server="imap.gmail.com",
        port=993,
        username=None,
        password=None,
        no_ssl=False,
        timeout=30,
        auth_mode="gmail_app_password",
        gmail_oauth_client_secrets=None,
        gmail_oauth_token_cache=None,
        no_browser=False,
        folder=[],
        google_voice_source=[exported["manifest_path"]],
        limit=10,
        dry_run=False,
        crawl_max_messages=None,
        crawl_batch_size=250,
        crawl_start_offset=0,
    )

    result = gmail_module.anyio.run(lambda: gmail_module.import_gmail_evidence(args))

    assert result["matched_google_voice_count"] == 1
    record = result["google_voice_events"][0]
    assert record["parsed_path"].endswith("event.json")
    assert Path(record["parsed_path"]).is_file()


def test_import_gmail_evidence_dedupes_google_voice_gmail_notifications(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")

    gmail_message = EmailMessage()
    gmail_message["Subject"] = "New text message from (503) 555-0100"
    gmail_message["From"] = '"(503) 555-0100" <15555550100@txt.voice.google.com>'
    gmail_message["To"] = "starworks5@gmail.com"
    gmail_message["Message-ID"] = "<voice-1@txt.voice.google.com>"
    gmail_message.set_content(
        "2026-03-24T04:56:14Z Tenant: Please send the inspection notice. "
        "Advocate: I will send it tonight. "
        "To respond to this text message, reply to this email or visit Google Voice."
    )
    raw_bytes = gmail_message.as_bytes(policy=email.policy.default)

    class _FakeProcessor:
        def __init__(self, **_kwargs: object) -> None:
            self.connection = object()

        async def connect(self) -> None:
            return None

        async def disconnect(self) -> None:
            return None

        def _parse_email_message(self, message: EmailMessage, include_attachments: bool = True) -> dict[str, object]:
            body = str(message.get_content() or "")
            return {
                "subject": message.get("Subject", ""),
                "from": message.get("From", ""),
                "to": message.get("To", ""),
                "cc": message.get("Cc", ""),
                "date": "2026-03-24T04:56:14+00:00",
                "message_id_header": message.get("Message-ID", ""),
                "attachments": [],
                "body_text": body,
            }

    args = SimpleNamespace(
        address=[],
        address_file=[],
        from_address=[],
        from_address_file=[],
        to_address=[],
        to_address_file=[],
        address_domain=[],
        address_domain_file=[],
        from_domain=[],
        from_domain_file=[],
        to_domain=[],
        to_domain_file=[],
        complaint_query=None,
        complaint_keyword=[],
        complaint_keyword_file=[],
        min_relevance_score=1.0,
        search="ALL",
        since_date=None,
        before_date=None,
        subject_contains=None,
        output_dir=str(tmp_path / "imports"),
        case_slug="voice-dedupe-demo",
        server="imap.gmail.com",
        port=993,
        username="starworks5@gmail.com",
        password="secret",
        no_ssl=False,
        timeout=30,
        auth_mode="gmail_app_password",
        gmail_oauth_client_secrets=None,
        gmail_oauth_token_cache=None,
        no_browser=False,
        folder=["[Gmail]/All Mail"],
        google_voice_source=[str(takeout_root)],
        limit=10,
        dry_run=False,
        crawl_max_messages=None,
        crawl_batch_size=250,
        crawl_start_offset=0,
    )

    async def _run_import() -> dict[str, object]:
        from unittest import mock

        with (
            mock.patch.object(gmail_module, "EmailProcessor", _FakeProcessor),
            mock.patch.object(
                gmail_module,
                "_fetch_folder_messages",
                return_value=[(raw_bytes, gmail_message)],
            ),
        ):
            return await gmail_module.import_gmail_evidence(args)

    result = gmail_module.anyio.run(_run_import)

    assert result["matched_email_count"] == 0
    assert result["matched_google_voice_count"] == 1
    assert result["deduped_gmail_google_voice_count"] == 1
    assert result["deduped_gmail_google_voice_records"][0]["message_id_header"] == "<voice-1@txt.voice.google.com>"
    assert result["google_voice_events"][0]["deduped_gmail_message_ids"] == ["<voice-1@txt.voice.google.com>"]


def test_write_duckdb_index_persists_history_tables(tmp_path: Path) -> None:
    result = history_index_module._write_duckdb_index(
        output_root=tmp_path / "duckdb",
        document_rows=[
            {
                "doc_id": "doc:1",
                "relative_path": "voice/transcript.txt",
                "absolute_path": "/tmp/voice/transcript.txt",
                "status": "success",
                "text_length": 42,
                "chunk_count": 1,
                "metadata": {"source_type": "google_voice"},
            }
        ],
        chunk_rows=[
            {
                "id": "doc:1:chunk:0",
                "doc_id": "doc:1",
                "chunk_index": 0,
                "text": "Tenant asked for inspection notice by text message.",
                "metadata": {"relative_path": "voice/transcript.txt"},
            }
        ],
        entity_rows=[
            {
                "entity_id": "entity:tenant",
                "entity_type": "Person",
                "name": "Tenant",
                "confidence": 0.9,
                "attributes": {"source": "voice"},
            }
        ],
        relationship_rows=[
            {
                "relationship_id": "rel:1",
                "source_id": "entity:tenant",
                "target_id": "entity:notice",
                "relation_type": "requested",
                "confidence": 0.8,
                "attributes": {"channel": "google_voice"},
            }
        ],
    )

    assert Path(result["duckdb_path"]).is_file()


def test_iter_files_supports_multiple_roots_without_duplicates(tmp_path: Path) -> None:
    root_a = tmp_path / "history"
    root_b = tmp_path / "email_imports"
    root_a.mkdir()
    root_b.mkdir()
    (root_a / "a.txt").write_text("alpha", encoding="utf-8")
    (root_b / "b.txt").write_text("beta", encoding="utf-8")

    paths = list(history_index_module._iter_files([root_a, root_b], max_bytes=1000))

    assert [path.name for path in paths] == ["a.txt", "b.txt"]


def test_search_history_duckdb_finds_chunk_text_and_source_filter(tmp_path: Path) -> None:
    index_result = history_index_module._write_duckdb_index(
        output_root=tmp_path / "duckdb",
        document_rows=[
            {
                "doc_id": "doc:voice:1",
                "relative_path": "email_imports/voice/transcript.txt",
                "absolute_path": "/tmp/email_imports/voice/transcript.txt",
                "status": "success",
                "text_length": 55,
                "chunk_count": 1,
                "metadata": {"source_type": "google_voice"},
            }
        ],
        chunk_rows=[
            {
                "id": "doc:voice:1:chunk:0",
                "doc_id": "doc:voice:1",
                "chunk_index": 0,
                "text": "Tenant requested the inspection notice over Google Voice text.",
                "metadata": {"relative_path": "email_imports/voice/transcript.txt", "source_type": "google_voice"},
            }
        ],
        entity_rows=[],
        relationship_rows=[],
    )

    payload = duckdb_search_module.search_duckdb(
        db_path=index_result["duckdb_path"],
        query="inspection notice",
        table="chunks",
        limit=5,
        source_like="google_voice",
    )

    assert payload["result_count"] == 1
    assert payload["results"][0]["chunk_id"] == "doc:voice:1:chunk:0"


def test_search_history_duckdb_finds_entities(tmp_path: Path) -> None:
    index_result = history_index_module._write_duckdb_index(
        output_root=tmp_path / "duckdb",
        document_rows=[],
        chunk_rows=[],
        entity_rows=[
            {
                "entity_id": "entity:tenant",
                "entity_type": "Person",
                "name": "Tenant",
                "confidence": 0.91,
                "attributes": {"channel": "google_voice"},
            }
        ],
        relationship_rows=[],
    )

    payload = duckdb_search_module.search_duckdb(
        db_path=index_result["duckdb_path"],
        query="tenant",
        table="entities",
        limit=5,
    )

    assert payload["result_count"] == 1
    assert payload["results"][0]["entity_id"] == "entity:tenant"


@pytest.mark.communications_smoke
def test_run_google_voice_ingest_wrapper_smoke(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")
    repo_root = Path("/home/barberb/HACC")
    case_slug = "smoke-voice-wrapper"
    materialized_dir = tmp_path / "materialized"
    bundle_dir = tmp_path / "bundles"

    result = subprocess.run(
        [
            str(repo_root / "run-google-voice-ingest.sh"),
            "--source",
            str(takeout_root),
            "--materialized-dir",
            str(materialized_dir),
            "--case-slug",
            case_slug,
            "--skip-index",
            "--import-arg",
            "--dry-run",
            "--bundle-output-dir",
            str(bundle_dir),
            "--bundle-format",
            "zip",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (materialized_dir / "google_voice_manifest.json").is_file()
    assert (materialized_dir / "google_voice_case_bundle.json").is_file()
    bundle_payload = json.loads((materialized_dir / "google_voice_case_bundle.json").read_text(encoding="utf-8"))
    assert bundle_payload["bundle_formats"] == ["dir", "zip"]
    assert Path(bundle_payload["bundle_artifacts"]["zip"]).is_file()
    assert "matched_google_voice_count" in result.stdout


@pytest.mark.communications_smoke
def test_run_google_voice_ingest_wrapper_vault_mode_smoke(tmp_path: Path) -> None:
    vault_root = _build_voice_vault_export(tmp_path / "source")
    repo_root = Path("/home/barberb/HACC")
    case_slug = "smoke-voice-vault-wrapper"
    materialized_dir = tmp_path / "materialized-vault"

    result = subprocess.run(
        [
            str(repo_root / "run-google-voice-ingest.sh"),
            "--source",
            str(vault_root),
            "--source-mode",
            "vault",
            "--materialized-dir",
            str(materialized_dir),
            "--case-slug",
            case_slug,
            "--skip-index",
            "--import-arg",
            "--dry-run",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert (materialized_dir / "google_voice_manifest.json").is_file()
    assert "matched_google_voice_count" in result.stdout


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_mocked_capture(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    fake_zip = downloads_dir / "voice-takeout.zip"
    fake_zip.write_bytes(b"fake-takeout-zip")
    manifest_path = downloads_dir / "acquisition.json"

    cli_stub = tmp_path / "ipfs-cli-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "command = ' '.join(args)\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "if 'google-voice-takeout-case-bundle' in command:\n"
        "    output_dir = pathlib.Path(args[args.index('--output-dir') + 1])\n"
        "    bundle_dir = output_dir / 'consumer-google-voice-smoke'\n"
        "    bundle_dir.mkdir(parents=True, exist_ok=True)\n"
        "    payload = {\n"
        "      'status': 'success',\n"
        "      'case_slug': 'consumer-google-voice-smoke',\n"
        "      'bundle_formats': ['dir', 'zip'],\n"
        "      'bundle_dir': str(bundle_dir),\n"
        "      'bundle_artifacts': {'dir': str(bundle_dir), 'zip': str(bundle_dir.with_suffix('.zip'))}\n"
        "    }\n"
        "else:\n"
        "    payload = {\n"
        "      'status': 'success',\n"
        "      'browser_capture': {\n"
        "        'status': 'success',\n"
        "        'download_status': 'captured',\n"
        "        'download_path': r'" + str(fake_zip) + "'\n"
        "      }\n"
        "    }\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    voice_stub = tmp_path / "voice-wrapper-stub.sh"
    voice_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'VOICE_WRAPPER_STUB $*'\n",
        encoding="utf-8",
    )
    voice_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--downloads-dir",
            str(downloads_dir),
            "--acquisition-manifest",
            str(manifest_path),
            "--skip-index",
            "--bundle-output-dir",
            str(tmp_path / "bundles"),
            "--bundle-format",
            "zip",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "HACC_VOICE_WRAPPER": str(voice_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Opening Google Takeout" in result.stdout
    assert "Hydrating captured Google Voice archive" in result.stdout
    assert "VOICE_WRAPPER_STUB" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "hydrated"
    assert payload["product_ids"] == ["voice"]
    assert payload["final_archive_path"] == str(fake_zip)
    assert payload["bundle_result"]["bundle_formats"] == ["dir", "zip"]
    history_dir = downloads_dir / "takeout_acquisition_history"
    assert history_dir.is_dir()
    assert any(history_dir.glob("*.json"))


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_resume_from_downloads(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    fake_zip = downloads_dir / "voice-takeout.zip"
    fake_zip.write_bytes(b"fake-takeout-zip")
    manifest_path = downloads_dir / "acquisition.json"

    cli_stub = tmp_path / "ipfs-cli-poll-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "payload = {\n"
        "  'status': 'success',\n"
        "  'download_path': r'" + str(fake_zip) + "'\n"
        "}\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    voice_stub = tmp_path / "voice-wrapper-stub.sh"
    voice_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'VOICE_WRAPPER_RESUME_STUB $*'\n",
        encoding="utf-8",
    )
    voice_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--resume-from-downloads",
            str(downloads_dir),
            "--acquisition-manifest",
            str(manifest_path),
            "--skip-index",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "HACC_VOICE_WRAPPER": str(voice_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Polling existing download directory" in result.stdout
    assert "VOICE_WRAPPER_RESUME_STUB" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "hydrated"
    assert payload["final_archive_path"] == str(fake_zip)


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_resume_from_manifest(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    fake_zip = downloads_dir / "voice-takeout.zip"
    fake_zip.write_bytes(b"fake-takeout-zip")
    manifest_path = downloads_dir / "acquisition.json"
    manifest_path.write_text(
        json.dumps(
            {
                "case_slug": "resume-manifest-case",
                "delivery_destination": "drive",
                "frequency": "one_time",
                "page_source_path": str(downloads_dir / "takeout_page.html"),
                "downloads_dir": str(downloads_dir),
                "capture_json_path": str(downloads_dir / "takeout_capture.json"),
                "drive_fallback": {
                    "enabled": False,
                    "name_contains": "takeout",
                    "client_secrets_path": None,
                    "account_hint": None,
                },
                "product_ids": ["voice"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    cli_stub = tmp_path / "ipfs-cli-poll-manifest-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "payload = {\n"
        "  'status': 'success',\n"
        "  'download_path': r'" + str(fake_zip) + "'\n"
        "}\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    voice_stub = tmp_path / "voice-wrapper-manifest-stub.sh"
    voice_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'VOICE_WRAPPER_MANIFEST_STUB $*'\n",
        encoding="utf-8",
    )
    voice_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--resume-from-manifest",
            str(manifest_path),
            "--skip-index",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "HACC_VOICE_WRAPPER": str(voice_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Polling existing download directory" in result.stdout
    assert "VOICE_WRAPPER_MANIFEST_STUB" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "hydrated"
    assert payload["product_ids"] == ["voice"]


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_no_display_falls_back_cleanly(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    manifest_path = downloads_dir / "acquisition.json"

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--downloads-dir",
            str(downloads_dir),
            "--acquisition-manifest",
            str(manifest_path),
            "--skip-index",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "DISPLAY": "",
            "HACC_DISABLE_X_DISPLAY_AUTO_DETECT": "1",
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "paused safely" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "manual_browser_required"
    assert payload["capture"]["browser_capture"]["status"] == "manual_browser_required"


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_system_browser_handoff(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    manifest_path = downloads_dir / "acquisition.json"

    cli_stub = tmp_path / "ipfs-cli-url-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "command = ' '.join(args)\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "if 'google-voice-takeout-url' in command:\n"
        "    payload = {\n"
        "      'status': 'success',\n"
        "      'product_ids': ['voice'],\n"
        "      'takeout_url': 'https://takeout.google.com/settings/takeout/custom/voice?dest=drive'\n"
        "    }\n"
        "else:\n"
        "    payload = {'status': 'success'}\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    xdg_stub = tmp_path / "xdg-open"
    xdg_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"XDG_OPEN_STUB $*\"\n",
        encoding="utf-8",
    )
    xdg_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--downloads-dir",
            str(downloads_dir),
            "--acquisition-manifest",
            str(manifest_path),
            "--skip-index",
            "--system-browser",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "DISPLAY": ":10",
            "XAUTHORITY": str(tmp_path / ".Xauthority"),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "desktop browser" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "pending_archive"
    assert payload["capture"]["browser_capture"]["mode"] == "system_browser"
    assert payload["capture"]["browser_capture"]["launcher"] == "xdg-open"


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_email_poll_records_match(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    manifest_path = downloads_dir / "acquisition.json"

    cli_stub = tmp_path / "ipfs-cli-email-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "command = ' '.join(args)\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "if 'google-voice-takeout-email' in command:\n"
        "    payload = {\n"
        "      'status': 'success',\n"
        "      'matched_email_count': 1,\n"
        "      'latest_match': {\n"
        "        'subject': 'Your Google data is ready to download',\n"
        "        'best_download_link': 'https://takeout.google.com/downloads/example'\n"
        "      }\n"
        "    }\n"
        "else:\n"
        "    payload = {'status': 'pending'}\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    xdg_stub = tmp_path / "xdg-open"
    xdg_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"XDG_OPEN_STUB $*\"\n",
        encoding="utf-8",
    )
    xdg_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--downloads-dir",
            str(downloads_dir),
            "--acquisition-manifest",
            str(manifest_path),
            "--skip-index",
            "--email-poll",
            "--email-open-link",
            "--email-username",
            "user@gmail.com",
            "--email-password",
            "app-pass",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "PATH": f"{tmp_path}:{os.environ['PATH']}",
            "DISPLAY": ":10",
            "XAUTHORITY": str(tmp_path / ".Xauthority"),
            "HACC_DISABLE_X_DISPLAY_AUTO_DETECT": "1",
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "polling email" in result.stdout.lower()
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["email_result"]["matched_email_count"] == 1
    assert payload["email_result"]["latest_match"]["best_download_link"].startswith("https://takeout.google.com/")


@pytest.mark.communications_smoke
def test_watch_consumer_google_voice_takeout_wrapper_advances_to_complete(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    manifest_path = tmp_path / "takeout_acquisition_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "status": "pending_archive",
                "downloads_dir": str(tmp_path / "downloads"),
                "events": [{"type": "pending_archive", "timestamp": "2026-04-04T12:00:00Z"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    cli_stub = tmp_path / "ipfs-cli-doctor-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        "manifest = args[-2] if args[-1] == '--json' else args[-1]\n"
        "payload = json.load(open(manifest, 'r', encoding='utf-8'))\n"
        "status = payload.get('status') or 'unknown'\n"
        "diagnosis = 'complete' if status == 'hydrated' else 'waiting_for_archive'\n"
        "print(json.dumps({'status': status, 'diagnosis': diagnosis, 'next_step': 'resume'}))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    wrapper_stub = tmp_path / "consumer-wrapper-stub.sh"
    wrapper_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "args = sys.argv[1:]\n"
        "manifest = args[args.index('--resume-from-manifest') + 1]\n"
        "payload = json.load(open(manifest, 'r', encoding='utf-8'))\n"
        "payload['status'] = 'hydrated'\n"
        "payload['final_archive_path'] = '/tmp/fake-takeout.zip'\n"
        "events = list(payload.get('events') or [])\n"
        "events.append({'type': 'hydrated', 'timestamp': '2026-04-04T12:30:00Z'})\n"
        "payload['events'] = events\n"
        "json.dump(payload, open(manifest, 'w', encoding='utf-8'), indent=2)\n"
        "print('WRAPPER_ADVANCED')\n",
        encoding="utf-8",
    )
    wrapper_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "watch-consumer-google-voice-takeout.sh"),
            "--manifest",
            str(manifest_path),
            "--interval-seconds",
            "0",
            "--max-iterations",
            "2",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "HACC_CONSUMER_TAKEOUT_WRAPPER": str(wrapper_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Takeout acquisition completed" in result.stdout
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["status"] == "hydrated"


@pytest.mark.communications_smoke
def test_watch_consumer_google_voice_takeout_wrapper_stops_cleanly_for_manual_browser_required(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    manifest_path = tmp_path / "takeout_acquisition_manifest.json"
    manifest_path.write_text(
        json.dumps(
            {
                "status": "manual_browser_required",
                "downloads_dir": str(tmp_path / "downloads"),
                "events": [{"type": "manual_browser_required", "timestamp": "2026-04-04T12:00:00Z"}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            str(repo_root / "watch-consumer-google-voice-takeout.sh"),
            "--manifest",
            str(manifest_path),
            "--interval-seconds",
            "0",
            "--max-iterations",
            "2",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "requires a desktop browser session" in result.stdout


@pytest.mark.communications_smoke
def test_run_and_watch_consumer_google_voice_takeout_wrapper_smoke(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    manifest_path = tmp_path / "takeout_acquisition_manifest.json"
    consumer_stub = tmp_path / "consumer-bootstrap-stub.sh"
    consumer_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "manifest = pathlib.Path(args[args.index('--acquisition-manifest') + 1])\n"
        "manifest.write_text(json.dumps({'status': 'pending_archive', 'events': []}), encoding='utf-8')\n"
        "print('CONSUMER_BOOTSTRAP_STUB')\n",
        encoding="utf-8",
    )
    consumer_stub.chmod(0o755)

    watch_stub = tmp_path / "watch-bootstrap-stub.sh"
    watch_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"WATCH_BOOTSTRAP_STUB $*\"\n",
        encoding="utf-8",
    )
    watch_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-and-watch-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--acquisition-manifest",
            str(manifest_path),
            "--watch-interval-seconds",
            "0",
            "--bundle-output-dir",
            str(tmp_path / "bundles"),
            "--bundle-format",
            "zip",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_CONSUMER_TAKEOUT_WRAPPER": str(consumer_stub),
            "HACC_CONSUMER_TAKEOUT_WATCH_WRAPPER": str(watch_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "CONSUMER_BOOTSTRAP_STUB" in result.stdout
    assert "WATCH_BOOTSTRAP_STUB" in result.stdout
    assert "--bundle-output-dir" in result.stdout
    assert "--resume-arg --bundle-format --resume-arg zip" in result.stdout


@pytest.mark.communications_smoke
def test_run_consumer_google_voice_takeout_wrapper_drive_fallback(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    downloads_dir = tmp_path / "downloads"
    downloads_dir.mkdir()
    fake_zip = downloads_dir / "drive-takeout.zip"
    fake_zip.write_bytes(b"fake-drive-zip")

    cli_stub = tmp_path / "ipfs-cli-drive-stub.py"
    cli_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output = None\n"
        "command = ' '.join(args)\n"
        "for idx, arg in enumerate(args):\n"
        "    if arg in ('--output', '-o') and idx + 1 < len(args):\n"
        "        output = args[idx + 1]\n"
        "if 'google-voice-takeout-capture' in command:\n"
        "    payload = {'status': 'pending', 'browser_capture': {'status': 'pending', 'started_at': '2026-04-04T12:00:00Z'}}\n"
        "else:\n"
        "    payload = {\n"
        "      'status': 'success',\n"
        "      'modified_after': '2026-04-04T12:00:00Z',\n"
        "      'artifact': {'id': 'file-1', 'name': 'drive-takeout.zip'},\n"
        "      'download': {'output_path': r'" + str(fake_zip) + "'}\n"
        "    }\n"
        "if output:\n"
        "    pathlib.Path(output).write_text(json.dumps(payload), encoding='utf-8')\n"
        "print(json.dumps(payload))\n",
        encoding="utf-8",
    )
    cli_stub.chmod(0o755)

    voice_stub = tmp_path / "voice-wrapper-stub.sh"
    voice_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo 'VOICE_WRAPPER_DRIVE_STUB $*'\n",
        encoding="utf-8",
    )
    voice_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-consumer-google-voice-takeout.sh"),
            "--product-id",
            "voice",
            "--dest",
            "drive",
            "--downloads-dir",
            str(downloads_dir),
            "--drive-client-secrets",
            str(tmp_path / "client.json"),
            "--drive-account-hint",
            "user@gmail.com",
            "--skip-index",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IPFS_DATASETS_CLI": str(cli_stub),
            "HACC_VOICE_WRAPPER": str(voice_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "polling Google Drive" in result.stdout
    assert "VOICE_WRAPPER_DRIVE_STUB" in result.stdout


@pytest.mark.communications_smoke
def test_run_communications_ingest_wrapper_voice_only_smoke(tmp_path: Path) -> None:
    takeout_root = _build_voice_takeout(tmp_path / "source")
    repo_root = Path("/home/barberb/HACC")
    case_slug = "smoke-communications-wrapper"

    result = subprocess.run(
        [
            str(repo_root / "run-communications-ingest.sh"),
            "--google-voice-source",
            str(takeout_root),
            "--case-slug",
            case_slug,
            "--skip-index",
            "--voice-index-arg",
            "--dry-run",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "Google Voice ingest" in result.stdout
    assert "matched_google_voice_count" in result.stdout


@pytest.mark.communications_smoke
def test_run_communications_ingest_wrapper_mocked_gmail_and_voice(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    source_dir = tmp_path / "voice-source"
    source_dir.mkdir()

    gmail_stub = tmp_path / "gmail-import-stub.sh"
    gmail_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, sys\n"
        "print('GMAIL_STUB ' + ' '.join(sys.argv[1:]))\n"
        "print(json.dumps({'matched_email_count': 2, 'status': 'success'}))\n",
        encoding="utf-8",
    )
    voice_stub = tmp_path / "voice-wrapper-stub.sh"
    voice_stub.write_text(
        "#!/usr/bin/env bash\n"
        "echo \"VOICE_STUB $*\"\n"
        "echo '{\"matched_google_voice_count\": 1, \"status\": \"success\"}'\n",
        encoding="utf-8",
    )
    gmail_stub.chmod(0o755)
    voice_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-communications-ingest.sh"),
            "--gmail-folder",
            "[Gmail]/All Mail",
            "--gmail-arg",
            "--dry-run",
            "--google-voice-source",
            str(source_dir),
            "--voice-index-arg",
            "--dry-run",
            "--voice-bundle-output-dir",
            str(tmp_path / "voice-bundles"),
            "--voice-bundle-format",
            "zip",
            "--skip-index",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_IMPORT_SCRIPT": str(gmail_stub),
            "HACC_VOICE_WRAPPER": str(voice_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    assert "GMAIL_STUB" in result.stdout
    assert "VOICE_STUB" in result.stdout
    assert "--bundle-output-dir" in result.stdout
    assert "--bundle-format zip" in result.stdout


@pytest.mark.communications_smoke
def test_run_history_index_wrapper_bundle_exports(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    output_dir = tmp_path / "history-index-output"
    bundle_dir = tmp_path / "history-index-bundles"

    index_stub = tmp_path / "indexer-stub.py"
    index_stub.write_text(
        "#!/usr/bin/env python3\n"
        "import json, pathlib, sys\n"
        "args = sys.argv[1:]\n"
        "output_dir = pathlib.Path(args[args.index('--output-dir') + 1])\n"
        "vector_dir = output_dir / 'vector'\n"
        "duckdb_dir = output_dir / 'duckdb'\n"
        "vector_dir.mkdir(parents=True, exist_ok=True)\n"
        "duckdb_dir.mkdir(parents=True, exist_ok=True)\n"
        "(vector_dir / 'evidence_history.records.jsonl').write_text('{\"id\":\"chunk-1\",\"text\":\"google voice text\"}\\n', encoding='utf-8')\n"
        "(vector_dir / 'evidence_history.vectors.npy').write_bytes(b'FAKEVECTORS')\n"
        "(duckdb_dir / 'evidence_index.duckdb').write_bytes(b'DUCKDB')\n"
        "(output_dir / 'manifest.json').write_text(json.dumps({'document_count': 1, 'chunk_count': 1, 'entity_count': 0, 'relationship_count': 0, 'vector_index': {'dimension': 384, 'provider': 'stub', 'status': 'success'}}), encoding='utf-8')\n"
        "print(json.dumps({'status':'success'}))\n",
        encoding="utf-8",
    )
    index_stub.chmod(0o755)

    duckdb_stub = tmp_path / "duckdb-search-stub.py"
    duckdb_stub.write_text(
        "#!/usr/bin/env python3\n"
        "print('DUCKDB_SPOT_STUB')\n",
        encoding="utf-8",
    )
    duckdb_stub.chmod(0o755)

    semantic_stub = tmp_path / "semantic-search-stub.py"
    semantic_stub.write_text(
        "#!/usr/bin/env python3\n"
        "print('SEMANTIC_SPOT_STUB')\n",
        encoding="utf-8",
    )
    semantic_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-history-index.sh"),
            "--skip-preflight",
            "--output-dir",
            str(output_dir),
            "--bundle-output-dir",
            str(bundle_dir),
            "--bundle-format",
            "zip",
            "--bundle-format",
            "parquet",
            "--bundle-format",
            "car",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_HISTORY_INDEX_SCRIPT": str(index_stub),
            "HACC_DUCKDB_SEARCH_SCRIPT": str(duckdb_stub),
            "HACC_SEMANTIC_SEARCH_SCRIPT": str(semantic_stub),
            "HACC_HISTORY_INPUT_DIR": str(tmp_path / "history-input"),
            "HACC_EMAIL_IMPORTS_INPUT_DIR": str(tmp_path / "email-input"),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    bundle_result = json.loads((output_dir / "history_index_bundle.json").read_text(encoding="utf-8"))
    assert bundle_result["bundle_formats"] == ["dir", "zip", "parquet", "car"]
    assert Path(bundle_result["bundle_artifacts"]["zip"]).is_file()
    assert Path(bundle_result["bundle_artifacts"]["parquet"]).is_file()
    assert Path(bundle_result["bundle_artifacts"]["car"]).is_file()


@pytest.mark.communications_smoke
def test_run_case_archive_wrapper_collects_takeout_voice_and_history_artifacts(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")

    takeout_downloads = tmp_path / "takeout-downloads"
    takeout_downloads.mkdir()
    takeout_history = takeout_downloads / "takeout_acquisition_history"
    takeout_history.mkdir()
    (takeout_history / "20260404_120000_initialized.json").write_text("{}", encoding="utf-8")
    takeout_bundle_dir = tmp_path / "takeout-bundle"
    takeout_bundle_dir.mkdir()
    (takeout_bundle_dir / "takeout-case-report.md").write_text("# report\n", encoding="utf-8")
    takeout_bundle_zip = tmp_path / "takeout-bundle.zip"
    takeout_bundle_zip.write_bytes(b"ZIP")
    takeout_manifest = takeout_downloads / "takeout_acquisition_manifest.json"
    takeout_manifest.write_text(
        json.dumps(
            {
                "status": "hydrated",
                "case_slug": "archive-case",
                "downloads_dir": str(takeout_downloads),
                "bundle_result": {
                    "bundle_dir": str(takeout_bundle_dir),
                    "bundle_formats": ["dir", "zip"],
                    "bundle_artifacts": {
                        "dir": str(takeout_bundle_dir),
                        "zip": str(takeout_bundle_zip),
                    },
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    voice_bundle_dir = tmp_path / "voice-bundle"
    voice_bundle_dir.mkdir()
    (voice_bundle_dir / "event.json").write_text("{}", encoding="utf-8")
    voice_bundle_zip = tmp_path / "voice-bundle.zip"
    voice_bundle_zip.write_bytes(b"ZIP")
    voice_bundle_result = tmp_path / "google_voice_case_bundle.json"
    voice_bundle_result.write_text(
        json.dumps(
            {
                "status": "success",
                "bundle_dir": str(voice_bundle_dir),
                "bundle_formats": ["dir", "zip"],
                "bundle_artifacts": {
                    "dir": str(voice_bundle_dir),
                    "zip": str(voice_bundle_zip),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    history_bundle_dir = tmp_path / "history-bundle"
    history_bundle_dir.mkdir()
    (history_bundle_dir / "manifest.json").write_text("{}", encoding="utf-8")
    history_bundle_zip = tmp_path / "history-bundle.zip"
    history_bundle_zip.write_bytes(b"ZIP")
    history_bundle_result = tmp_path / "history_index_bundle.json"
    history_bundle_result.write_text(
        json.dumps(
            {
                "status": "success",
                "bundle_dir": str(history_bundle_dir),
                "bundle_formats": ["dir", "zip"],
                "bundle_artifacts": {
                    "dir": str(history_bundle_dir),
                    "zip": str(history_bundle_zip),
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "case-archives"
    result = subprocess.run(
        [
            str(repo_root / "run-case-archive.sh"),
            "--case-slug",
            "archive-case",
            "--takeout-manifest",
            str(takeout_manifest),
            "--voice-bundle-result",
            str(voice_bundle_result),
            "--history-bundle-result",
            str(history_bundle_result),
            "--output-dir",
            str(output_dir),
            "--bundle-format",
            "zip",
            "--bundle-format",
            "parquet",
            "--bundle-format",
            "car",
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    archive_result = json.loads((output_dir / "archive-case.json").read_text(encoding="utf-8"))
    assert archive_result["bundle_formats"] == ["dir", "zip", "parquet", "car"]
    assert archive_result["component_count"] == 3
    assert Path(archive_result["bundle_artifacts"]["zip"]).is_file()
    assert Path(archive_result["bundle_artifacts"]["parquet"]).is_file()
    assert Path(archive_result["bundle_artifacts"]["car"]).is_file()


@pytest.mark.communications_smoke
def test_run_case_archive_wrapper_can_auto_discover_by_case_slug(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    discover_root = tmp_path / "discover-root"
    case_slug = "archive-discover-case"

    takeout_downloads = discover_root / "evidence" / "email_imports" / f"{case_slug}-takeout-downloads"
    takeout_downloads.mkdir(parents=True)
    takeout_manifest = takeout_downloads / "takeout_acquisition_manifest.json"
    takeout_manifest.write_text(
        json.dumps(
            {
                "status": "hydrated",
                "case_slug": case_slug,
                "downloads_dir": str(takeout_downloads),
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    voice_materialized = discover_root / "evidence" / "email_imports" / f"{case_slug}-materialized"
    voice_materialized.mkdir(parents=True)
    voice_bundle_result = voice_materialized / "google_voice_case_bundle.json"
    voice_bundle_result.write_text(
        json.dumps(
            {
                "status": "success",
                "bundle_dir": str(voice_materialized / case_slug),
                "bundle_artifacts": {},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    history_output = discover_root / "research_results" / f"history_index_{case_slug}_20260404"
    history_output.mkdir(parents=True)
    history_bundle_result = history_output / "history_index_bundle.json"
    history_bundle_result.write_text(
        json.dumps(
            {
                "status": "success",
                "bundle_dir": str(history_output / case_slug),
                "bundle_artifacts": {},
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    output_dir = tmp_path / "case-archives"
    result = subprocess.run(
        [
            str(repo_root / "run-case-archive.sh"),
            "--case-slug",
            case_slug,
            "--discover",
            "--discover-root",
            str(discover_root),
            "--output-dir",
            str(output_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    assert result.returncode == 0, result.stderr or result.stdout
    archive_result = json.loads((output_dir / f"{case_slug}.json").read_text(encoding="utf-8"))
    assert archive_result["component_count"] == 3
    component_names = {item["component"] for item in archive_result["components"]}
    assert component_names == {"takeout", "voice", "history_index"}


@pytest.mark.communications_smoke
def test_run_case_closeout_wrapper_chains_ingest_history_and_archive(tmp_path: Path) -> None:
    repo_root = Path("/home/barberb/HACC")
    case_slug = "closeout-case"
    log_path = tmp_path / "closeout.log"
    archive_output_dir = tmp_path / "case-archives"

    communications_stub = tmp_path / "communications-stub.sh"
    communications_stub.write_text(
        "#!/usr/bin/env bash\n"
        "printf 'COMM %s\\n' \"$*\" >> \"" + str(log_path) + "\"\n",
        encoding="utf-8",
    )
    communications_stub.chmod(0o755)

    history_stub = tmp_path / "history-stub.sh"
    history_stub.write_text(
        "#!/usr/bin/env bash\n"
        "printf 'HISTORY %s\\n' \"$*\" >> \"" + str(log_path) + "\"\n",
        encoding="utf-8",
    )
    history_stub.chmod(0o755)

    archive_stub = tmp_path / "archive-stub.sh"
    archive_stub.write_text(
        "#!/usr/bin/env bash\n"
        "printf 'ARCHIVE %s\\n' \"$*\" >> \"" + str(log_path) + "\"\n",
        encoding="utf-8",
    )
    archive_stub.chmod(0o755)

    result = subprocess.run(
        [
            str(repo_root / "run-case-closeout.sh"),
            "--case-slug",
            case_slug,
            "--google-voice-source",
            str(tmp_path / "voice-source"),
            "--voice-bundle-format",
            "zip",
            "--history-bundle-format",
            "zip",
            "--archive-bundle-format",
            "zip",
            "--archive-output-dir",
            str(archive_output_dir),
        ],
        cwd=repo_root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
        env={
            **os.environ,
            "HACC_COMMUNICATIONS_WRAPPER": str(communications_stub),
            "HACC_HISTORY_WRAPPER": str(history_stub),
            "HACC_CASE_ARCHIVE_WRAPPER": str(archive_stub),
        },
    )

    assert result.returncode == 0, result.stderr or result.stdout
    log_lines = log_path.read_text(encoding="utf-8").splitlines()
    assert log_lines[0].startswith("COMM ")
    assert log_lines[1].startswith("HISTORY ")
    assert log_lines[2].startswith("ARCHIVE ")
    assert "--voice-bundle-format zip" in log_lines[0]
    assert "--bundle-format zip" in log_lines[1]
    assert "--discover" in log_lines[2]
    closeout_result = json.loads((archive_output_dir / f"{case_slug}.closeout.json").read_text(encoding="utf-8"))
    assert closeout_result["status"] == "success"
    assert closeout_result["case_slug"] == case_slug
    assert Path(closeout_result["logs"]["communications"]).is_file()
    assert Path(closeout_result["logs"]["history"]).is_file()
    assert Path(closeout_result["logs"]["archive"]).is_file()
