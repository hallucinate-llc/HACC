#!/usr/bin/env python3
"""Import Gmail messages and attachments into the local evidence folder."""

from __future__ import annotations

import argparse
import email
import email.policy
import getpass
import hashlib
import json
import os
import re
import sys
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import getaddresses
from pathlib import Path
from typing import Any, Iterable

import anyio


REPO_ROOT = Path(__file__).resolve().parent
COMPLAINT_GENERATOR_ROOT = REPO_ROOT / "complaint-generator"
IPFS_DATASETS_ROOT = COMPLAINT_GENERATOR_ROOT / "ipfs_datasets_py"
if str(COMPLAINT_GENERATOR_ROOT) not in sys.path:
    sys.path.insert(0, str(COMPLAINT_GENERATOR_ROOT))
if str(IPFS_DATASETS_ROOT) not in sys.path:
    sys.path.insert(0, str(IPFS_DATASETS_ROOT))

from ipfs_datasets_py.processors.multimedia.email_processor import EmailProcessor
from upload_email_evidence_manifest import upload_manifest


DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence" / "email_imports"
DEFAULT_GMAIL_SERVER = "imap.gmail.com"
DEFAULT_GMAIL_FOLDER = "[Gmail]/All Mail"


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", str(value or "").strip())
    cleaned = cleaned.strip(".-")
    return cleaned or "item"


def _normalize_address_values(values: Iterable[str]) -> set[str]:
    normalized: set[str] = set()
    for value in values:
        for _display, address in getaddresses([str(value or "")]):
            cleaned = address.strip().lower()
            if cleaned:
                normalized.add(cleaned)
    return normalized


def _load_address_targets(raw_addresses: list[str], address_files: list[str]) -> set[str]:
    values = list(raw_addresses)
    for file_path in address_files:
        path = Path(file_path).expanduser().resolve()
        values.extend(path.read_text(encoding="utf-8").splitlines())
    return _normalize_address_values(values)


def _message_participants(email_message: EmailMessage) -> set[str]:
    return _normalize_address_values(
        [
            email_message.get("From", ""),
            email_message.get("To", ""),
            email_message.get("Cc", ""),
            email_message.get("Reply-To", ""),
            email_message.get("Sender", ""),
        ]
    )


def _message_matches_addresses(email_message: EmailMessage, targets: set[str]) -> bool:
    if not targets:
        return True
    return bool(_message_participants(email_message) & targets)


def _sanitize_filename(filename: str, fallback: str) -> str:
    raw = str(filename or "").strip()
    if not raw:
        return fallback
    raw = raw.replace("/", "_").replace("\\", "_").replace("\x00", "")
    return _slugify(raw)


def _extract_attachment_bytes(part: email.message.Message) -> bytes:
    payload = part.get_payload(decode=True)
    return payload or b""


def _save_email_bundle(
    *,
    root_dir: Path,
    folder_name: str,
    email_message: EmailMessage,
    raw_bytes: bytes,
    parsed_email: dict[str, Any],
    sequence_number: int,
) -> dict[str, Any]:
    date_token = parsed_email.get("date") or datetime.now(UTC).isoformat()
    message_key = parsed_email.get("message_id_header") or hashlib.sha256(raw_bytes).hexdigest()[:16]
    subject_slug = _slugify(parsed_email.get("subject") or "email")
    bundle_dir = root_dir / f"{sequence_number:04d}-{subject_slug}-{_slugify(message_key)}"
    attachments_dir = bundle_dir / "attachments"
    attachments_dir.mkdir(parents=True, exist_ok=True)

    eml_path = bundle_dir / "message.eml"
    eml_path.write_bytes(raw_bytes)

    attachment_records: list[dict[str, Any]] = []
    seen_names: dict[str, int] = {}
    for index, part in enumerate(email_message.walk(), start=1):
        if part.get_content_maintype() == "multipart":
            continue
        if part.get("Content-Disposition") is None:
            continue
        filename = part.get_filename()
        if not filename:
            filename = f"attachment-{index}.bin"
        safe_name = _sanitize_filename(filename, f"attachment-{index}.bin")
        count = seen_names.get(safe_name, 0)
        seen_names[safe_name] = count + 1
        if count:
            stem = Path(safe_name).stem
            suffix = Path(safe_name).suffix
            safe_name = f"{stem}-{count + 1}{suffix}"
        payload = _extract_attachment_bytes(part)
        attachment_path = attachments_dir / safe_name
        attachment_path.write_bytes(payload)
        attachment_records.append(
            {
                "filename": safe_name,
                "path": str(attachment_path),
                "size": len(payload),
                "content_type": part.get_content_type(),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )

    parsed_payload = {
        "folder": folder_name,
        "date_token": date_token,
        "participants": sorted(_message_participants(email_message)),
        "attachment_count": len(attachment_records),
        **parsed_email,
    }
    parsed_path = bundle_dir / "message.json"
    parsed_path.write_text(json.dumps(parsed_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "folder": folder_name,
        "bundle_dir": str(bundle_dir),
        "email_path": str(eml_path),
        "parsed_path": str(parsed_path),
        "participants": sorted(_message_participants(email_message)),
        "subject": parsed_email.get("subject", ""),
        "date": parsed_email.get("date"),
        "from": parsed_email.get("from", ""),
        "to": parsed_email.get("to", ""),
        "cc": parsed_email.get("cc", ""),
        "message_id_header": parsed_email.get("message_id_header", ""),
        "attachment_paths": [item["path"] for item in attachment_records],
        "attachments": attachment_records,
        "evidence_title": parsed_email.get("subject") or f"Email from {parsed_email.get('from', '')}",
    }


async def _fetch_folder_messages(
    processor: EmailProcessor,
    *,
    folder: str,
    limit: int | None,
    search_criteria: str,
) -> list[tuple[bytes, EmailMessage]]:
    def _fetch() -> list[tuple[bytes, EmailMessage]]:
        status, _count = processor.connection.select(folder, readonly=True)
        if status != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}: {status}")
        status, message_ids = processor.connection.search(None, search_criteria or "ALL")
        if status != "OK":
            raise RuntimeError(f"Search failed for folder {folder!r}: {status}")
        ids = message_ids[0].split()
        if limit:
            ids = ids[-limit:]
        rows: list[tuple[bytes, EmailMessage]] = []
        for msg_id in ids:
            status, msg_data = processor.connection.fetch(msg_id, "(RFC822)")
            if status != "OK":
                continue
            raw_bytes = msg_data[0][1]
            msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
            rows.append((raw_bytes, msg))
        return rows

    return await anyio.to_thread.run_sync(_fetch)


async def import_gmail_evidence(args: argparse.Namespace) -> dict[str, Any]:
    targets = _load_address_targets(args.address, args.address_file)
    output_root = Path(args.output_dir).expanduser().resolve()
    run_dir = output_root / (args.case_slug or datetime.now(UTC).strftime("%Y%m%d_%H%M%S"))
    run_dir.mkdir(parents=True, exist_ok=True)

    processor = EmailProcessor(
        protocol="imap",
        server=args.server,
        port=args.port,
        username=args.username,
        password=args.password,
        use_ssl=not args.no_ssl,
        timeout=args.timeout,
    )
    await processor.connect()

    matched_records: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    try:
        for folder in args.folder:
            rows = await _fetch_folder_messages(
                processor,
                folder=folder,
                limit=args.limit,
                search_criteria=args.search,
            )
            for raw_bytes, email_message in rows:
                parsed = processor._parse_email_message(email_message, include_attachments=True)
                if not _message_matches_addresses(email_message, targets):
                    continue
                dedupe_key = parsed.get("message_id_header") or hashlib.sha256(raw_bytes).hexdigest()
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                record = _save_email_bundle(
                    root_dir=run_dir,
                    folder_name=folder,
                    email_message=email_message,
                    raw_bytes=raw_bytes,
                    parsed_email=parsed,
                    sequence_number=len(matched_records) + 1,
                )
                matched_records.append(record)
    finally:
        await processor.disconnect()

    manifest = {
        "status": "success",
        "server": args.server,
        "username": args.username,
        "folders": list(args.folder),
        "search": args.search,
        "address_targets": sorted(targets),
        "matched_email_count": len(matched_records),
        "output_dir": str(run_dir),
        "emails": matched_records,
        "mediator_evidence_records": [
            {
                "title": item["evidence_title"],
                "kind": "document",
                "source": "gmail_import",
                "content": (
                    f"Subject: {item['subject']}\n"
                    f"From: {item['from']}\n"
                    f"To: {item['to']}\n"
                    f"Date: {item['date']}\n"
                    f"Saved email: {item['email_path']}"
                ),
                "attachment_names": [Path(path).name for path in item["attachment_paths"]],
                "metadata": {
                    "email_path": item["email_path"],
                    "parsed_path": item["parsed_path"],
                    "folder": item["folder"],
                    "message_id_header": item["message_id_header"],
                },
            }
            for item in matched_records
        ],
    }
    manifest_path = run_dir / "email_import_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Import Gmail messages and attachments into HACC evidence storage."
    )
    parser.add_argument("--server", default=DEFAULT_GMAIL_SERVER, help="IMAP server hostname")
    parser.add_argument("--port", type=int, default=993, help="IMAP server port")
    parser.add_argument("--username", default=None, help="Email account username")
    parser.add_argument("--password", default=None, help="Email account app password")
    parser.add_argument(
        "--prompt-credentials",
        action="store_true",
        help="Prompt securely for username/password instead of passing them on the command line.",
    )
    parser.add_argument(
        "--prompt-password",
        action="store_true",
        help="Prompt securely for the password if it is not already available.",
    )
    parser.add_argument(
        "--folder",
        action="append",
        default=None,
        help="IMAP folder to scan. Repeat to include multiple folders.",
    )
    parser.add_argument(
        "--address",
        action="append",
        default=[],
        help="Email address to match in from/to/cc/reply-to headers. Repeat as needed.",
    )
    parser.add_argument(
        "--address-file",
        action="append",
        default=[],
        help="Path to newline-delimited address list.",
    )
    parser.add_argument("--search", default="ALL", help='IMAP search criteria, e.g. SINCE "1-Jan-2026"')
    parser.add_argument("--limit", type=int, default=None, help="Per-folder message limit")
    parser.add_argument("--timeout", type=int, default=30, help="IMAP timeout seconds")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL/TLS")
    parser.add_argument("--output-dir", default=str(DEFAULT_EVIDENCE_ROOT), help="Evidence output root")
    parser.add_argument("--case-slug", default=None, help="Optional folder name under the output root")
    parser.add_argument(
        "--upload-to-workspace",
        action="store_true",
        help="Upload the generated manifest into the complaint workspace after import.",
    )
    parser.add_argument(
        "--review-after-upload",
        action="store_true",
        help="After uploading, call complaint.review_case and include the updated review payload.",
    )
    parser.add_argument(
        "--generate-after-upload",
        action="store_true",
        help="Generate a complaint draft after upload and include it in the result.",
    )
    parser.add_argument(
        "--export-packet-after-upload",
        action="store_true",
        help="Export the complaint packet after upload and include it in the result.",
    )
    parser.add_argument(
        "--export-markdown-after-upload",
        action="store_true",
        help="Export complaint markdown after upload and include it in the result.",
    )
    parser.add_argument("--user-id", default="demo-user", help="Complaint workspace user id for optional upload.")
    parser.add_argument(
        "--claim-element-id",
        default="causation",
        help="Claim element id to use when uploading imported email evidence.",
    )
    return parser


async def _run(args: argparse.Namespace) -> int:
    if not args.username:
        args.username = (
            os.environ.get("GMAIL_USER")
            or os.environ.get("EMAIL_USER")
        )
    if not args.password:
        args.password = (
            os.environ.get("GMAIL_APP_PASSWORD")
            or os.environ.get("EMAIL_PASS")
        )
    if not args.folder:
        args.folder = [DEFAULT_GMAIL_FOLDER]
    if args.prompt_credentials and not args.username:
        args.username = input("Gmail username: ").strip()
    if (args.prompt_credentials or args.prompt_password) and not args.password:
        args.password = getpass.getpass("Gmail app password: ")
    if not args.username or not args.password:
        raise SystemExit(
            "Missing Gmail credentials. Use --prompt-credentials, --prompt-password, or set "
            "GMAIL_USER and GMAIL_APP_PASSWORD."
        )
    manifest = await import_gmail_evidence(args)
    if getattr(args, "upload_to_workspace", False):
        manifest["workspace_upload"] = upload_manifest(
            str(Path(manifest["output_dir"]) / "email_import_manifest.json"),
            user_id=getattr(args, "user_id", "demo-user"),
            claim_element_id=getattr(args, "claim_element_id", "causation"),
            source="gmail_import",
            review_after_upload=getattr(args, "review_after_upload", False),
            generate_after_upload=getattr(args, "generate_after_upload", False),
            export_packet_after_upload=getattr(args, "export_packet_after_upload", False),
            export_markdown_after_upload=getattr(args, "export_markdown_after_upload", False),
        )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return anyio.run(_run, args)


if __name__ == "__main__":
    raise SystemExit(main())
