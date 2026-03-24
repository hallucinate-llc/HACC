#!/usr/bin/env python3
"""Import Gmail messages and attachments into the local evidence folder."""

from __future__ import annotations

import argparse
import email
import email.policy
import getpass
import hashlib
import imaplib
import json
import os
import re
import sys
from collections import Counter
from datetime import UTC, datetime
from email.message import EmailMessage
from email.utils import getaddresses
from pathlib import Path
from typing import Any, Iterable

import anyio

from gmail_oauth import resolve_gmail_oauth_access_token, build_xoauth2_bytes

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
VALID_AUTH_MODES = ("imap_password", "gmail_app_password", "gmail_oauth")


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
        values.extend(
            line
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return _normalize_address_values(values)


def _normalize_imap_date(value: str) -> str:
    parsed = datetime.fromisoformat(str(value).strip())
    return f"{parsed.day}-{parsed.strftime('%b')}-{parsed.year}"


def _build_search_criteria(args: argparse.Namespace) -> str:
    parts: list[str] = []
    explicit = str(getattr(args, "search", "") or "").strip()
    if explicit and explicit.upper() != "ALL":
        parts.append(f"({explicit})")
    if getattr(args, "since_date", None):
        parts.append(f'SINCE "{_normalize_imap_date(args.since_date)}"')
    if getattr(args, "before_date", None):
        parts.append(f'BEFORE "{_normalize_imap_date(args.before_date)}"')
    if getattr(args, "subject_contains", None):
        parts.append(f'SUBJECT "{str(args.subject_contains).strip()}"')
    return " ".join(part for part in parts if part) or "ALL"


def _quote_imap_mailbox(folder: str) -> str:
    text = str(folder or "")
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def _is_oversized_search_error(exc: Exception) -> bool:
    return "got more than 1000000 bytes" in str(exc or "").lower()


def _humanize_connection_error(exc: Exception) -> str:
    message = str(exc or "").strip()
    lowered = message.lower()
    if "application-specific password required" in lowered:
        return (
            "Gmail rejected the login because it requires an app password.\n"
            "Use a Google app password, not your normal Gmail password.\n"
            "Steps:\n"
            "1. Turn on 2-Step Verification for the Google account.\n"
            "2. Create an App Password for Mail.\n"
            "3. Re-run this command and paste that 16-character app password when prompted."
        )
    return message


def _resolve_auth_mode(args: argparse.Namespace) -> str:
    explicit = str(getattr(args, "auth_mode", "") or "").strip().lower()
    if explicit:
        if explicit not in VALID_AUTH_MODES:
            raise SystemExit(
                f"Unsupported auth mode '{explicit}'. Choose one of: {', '.join(VALID_AUTH_MODES)}."
            )
        return explicit
    if getattr(args, "use_gmail_oauth", False):
        return "gmail_oauth"
    if str(getattr(args, "server", "") or "").strip().lower() == DEFAULT_GMAIL_SERVER:
        return "gmail_app_password"
    return "imap_password"


async def _connect_processor_with_xoauth2(
    processor: EmailProcessor,
    *,
    gmail_user: str,
    access_token: str,
) -> None:
    def _connect() -> Any:
        if processor.use_ssl:
            connection = imaplib.IMAP4_SSL(processor.server, processor.port, timeout=processor.timeout)
        else:
            connection = imaplib.IMAP4(processor.server, processor.port)
        auth_bytes = build_xoauth2_bytes(gmail_user, access_token)
        connection.authenticate("XOAUTH2", lambda _challenge: auth_bytes)
        return connection

    processor.connection = await anyio.to_thread.run_sync(_connect)
    processor.connected = True


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


def _message_sender_addresses(email_message: EmailMessage) -> set[str]:
    return _normalize_address_values(
        [
            email_message.get("From", ""),
            email_message.get("Reply-To", ""),
            email_message.get("Sender", ""),
        ]
    )


def _message_recipient_addresses(email_message: EmailMessage) -> set[str]:
    return _normalize_address_values(
        [
            email_message.get("To", ""),
            email_message.get("Cc", ""),
        ]
    )


def _message_matches_addresses(
    email_message: EmailMessage,
    targets: set[str],
    *,
    from_targets: set[str] | None = None,
    recipient_targets: set[str] | None = None,
) -> bool:
    if not targets:
        targets = set()
    from_targets = from_targets or set()
    recipient_targets = recipient_targets or set()
    if not targets and not from_targets and not recipient_targets:
        return True
    participants = _message_participants(email_message)
    senders = _message_sender_addresses(email_message)
    recipients = _message_recipient_addresses(email_message)
    if targets and participants & targets:
        return True
    if from_targets and senders & from_targets:
        return True
    if recipient_targets and recipients & recipient_targets:
        return True
    return False


def _sanitize_filename(filename: str, fallback: str) -> str:
    raw = str(filename or "").strip()
    if not raw:
        return fallback
    raw = raw.replace("/", "_").replace("\\", "_").replace("\x00", "")
    return _slugify(raw)


def _extract_attachment_bytes(part: email.message.Message) -> bytes:
    payload = part.get_payload(decode=True)
    return payload or b""


def _collect_message_text(email_message: EmailMessage) -> str:
    parts: list[str] = []
    for key in ("Subject", "From", "To", "Cc", "Reply-To"):
        value = email_message.get(key, "")
        if value:
            parts.append(str(value))
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_maintype() == "multipart":
                continue
            if part.get_content_disposition() == "attachment":
                filename = part.get_filename()
                if filename:
                    parts.append(filename)
                continue
            if part.get_content_type() != "text/plain":
                continue
            try:
                text = part.get_content()
            except Exception:
                payload = part.get_payload(decode=True) or b""
                charset = part.get_content_charset() or "utf-8"
                text = payload.decode(charset, errors="ignore")
            if text:
                parts.append(str(text))
    else:
        try:
            text = email_message.get_content()
        except Exception:
            payload = email_message.get_payload(decode=True) or b""
            charset = email_message.get_content_charset() or "utf-8"
            text = payload.decode(charset, errors="ignore")
        if text:
            parts.append(str(text))
    return "\n".join(parts)


def _tokenize_text(value: str) -> list[str]:
    return [token for token in re.findall(r"[A-Za-z0-9][A-Za-z0-9'_-]*", str(value or "").lower()) if len(token) >= 3]


def _load_keywords(raw_keywords: list[str], keyword_files: list[str]) -> list[str]:
    values = list(raw_keywords)
    for file_path in keyword_files:
        path = Path(file_path).expanduser().resolve()
        values.extend(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    return values


def _build_complaint_terms(args: argparse.Namespace) -> list[str]:
    terms = _tokenize_text(getattr(args, "complaint_query", "") or "")
    for keyword in _load_keywords(
        list(getattr(args, "complaint_keyword", []) or []),
        list(getattr(args, "complaint_keyword_file", []) or []),
    ):
        terms.extend(_tokenize_text(keyword))
    counts = Counter(terms)
    return [term for term, _count in counts.most_common()]


def _score_message_relevance(email_message: EmailMessage, complaint_terms: list[str]) -> dict[str, Any]:
    if not complaint_terms:
        return {"score": 0.0, "matched_terms": [], "matched_fields": []}
    subject = str(email_message.get("Subject", "") or "")
    body_text = _collect_message_text(email_message)
    subject_tokens = set(_tokenize_text(subject))
    body_tokens = set(_tokenize_text(body_text))
    matched_subject_terms = [term for term in complaint_terms if term in subject_tokens]
    matched_body_terms = [term for term in complaint_terms if term in body_tokens and term not in matched_subject_terms]
    score = float(len(matched_subject_terms) * 3 + len(matched_body_terms))
    matched_fields: list[str] = []
    if matched_subject_terms:
        matched_fields.append("subject")
    if matched_body_terms:
        matched_fields.append("body")
    return {
        "score": score,
        "matched_terms": matched_subject_terms + matched_body_terms,
        "matched_fields": matched_fields,
    }


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
        status, count_data = processor.connection.select(_quote_imap_mailbox(folder), readonly=True)
        if status != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}: {status}")
        total_messages = int((count_data or [b"0"])[0] or b"0")
        if limit and (search_criteria or "ALL").strip().upper() == "ALL":
            # Skip SEARCH entirely for broad bounded previews/imports. Gmail can
            # emit a huge id list for All Mail that exceeds imaplib's line limit.
            start = max(1, total_messages - limit + 1)
            ids = [str(value).encode("ascii") for value in range(start, total_messages + 1)]
        else:
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
    from_targets = _load_address_targets(args.from_address, args.from_address_file)
    recipient_targets = _load_address_targets(args.to_address, args.to_address_file)
    complaint_terms = _build_complaint_terms(args)
    search_criteria = _build_search_criteria(args)
    output_root = Path(args.output_dir).expanduser().resolve()
    run_dir = output_root / (args.case_slug or datetime.now(UTC).strftime("%Y%m%d_%H%M%S"))
    run_dir.mkdir(parents=True, exist_ok=True)

    auth_mode = _resolve_auth_mode(args)
    processor = EmailProcessor(
        protocol="imap",
        server=args.server,
        port=args.port,
        username=args.username,
        password=args.password,
        use_ssl=not args.no_ssl,
        timeout=args.timeout,
    )
    if auth_mode == "gmail_oauth":
        access_token, token_payload = resolve_gmail_oauth_access_token(
            gmail_user=args.username,
            client_secrets_path=args.gmail_oauth_client_secrets,
            token_cache_path=getattr(args, "gmail_oauth_token_cache", None),
            open_browser=not getattr(args, "no_browser", False),
        )
        await _connect_processor_with_xoauth2(processor, gmail_user=args.username, access_token=access_token)
    else:
        token_payload = None
        await processor.connect()

    matched_records: list[dict[str, Any]] = []
    preview_records: list[dict[str, Any]] = []
    seen_keys: set[str] = set()

    try:
        for folder in args.folder:
            rows = await _fetch_folder_messages(
                processor,
                folder=folder,
                limit=args.limit,
                search_criteria=search_criteria,
            )
            for raw_bytes, email_message in rows:
                parsed = processor._parse_email_message(email_message, include_attachments=True)
                if not _message_matches_addresses(
                    email_message,
                    targets,
                    from_targets=from_targets,
                    recipient_targets=recipient_targets,
                ):
                    continue
                relevance = _score_message_relevance(email_message, complaint_terms)
                if complaint_terms and relevance["score"] < float(getattr(args, "min_relevance_score", 1.0)):
                    continue
                dedupe_key = parsed.get("message_id_header") or hashlib.sha256(raw_bytes).hexdigest()
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                if getattr(args, "dry_run", False):
                    preview_records.append(
                        {
                            "folder": folder,
                            "subject": parsed.get("subject", ""),
                            "date": parsed.get("date"),
                            "from": parsed.get("from", ""),
                            "to": parsed.get("to", ""),
                            "cc": parsed.get("cc", ""),
                            "message_id_header": parsed.get("message_id_header", ""),
                            "participants": sorted(_message_participants(email_message)),
                            "attachment_count": len(list(parsed.get("attachments") or [])),
                            "relevance_score": relevance["score"],
                            "matched_terms": relevance["matched_terms"],
                            "matched_fields": relevance["matched_fields"],
                        }
                    )
                    continue
                record = _save_email_bundle(
                    root_dir=run_dir,
                    folder_name=folder,
                    email_message=email_message,
                    raw_bytes=raw_bytes,
                    parsed_email=parsed,
                    sequence_number=len(matched_records) + 1,
                )
                record["relevance_score"] = relevance["score"]
                record["matched_terms"] = relevance["matched_terms"]
                record["matched_fields"] = relevance["matched_fields"]
                matched_records.append(record)
    finally:
        await processor.disconnect()

    manifest = {
        "status": "success",
        "server": args.server,
        "username": args.username,
        "auth_mode": auth_mode,
        "folders": list(args.folder),
        "search": search_criteria,
        "complaint_terms": complaint_terms,
        "min_relevance_score": float(getattr(args, "min_relevance_score", 1.0)),
        "address_targets": sorted(targets),
        "from_address_targets": sorted(from_targets),
        "recipient_address_targets": sorted(recipient_targets),
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
    if token_payload:
        manifest["gmail_oauth"] = {
            "token_cache_path": str(
                Path(getattr(args, "gmail_oauth_token_cache", "")).expanduser().resolve()
                if getattr(args, "gmail_oauth_token_cache", None)
                else ""
            ),
            "expires_at": token_payload.get("expires_at"),
            "has_refresh_token": bool(token_payload.get("refresh_token")),
        }
    if getattr(args, "dry_run", False):
        return {
            "status": "success",
            "dry_run": True,
            "server": args.server,
            "username": args.username,
            "auth_mode": auth_mode,
            "folders": list(args.folder),
            "search": search_criteria,
            "complaint_terms": complaint_terms,
            "min_relevance_score": float(getattr(args, "min_relevance_score", 1.0)),
            "address_targets": sorted(targets),
            "from_address_targets": sorted(from_targets),
            "recipient_address_targets": sorted(recipient_targets),
            "matched_email_count": len(preview_records),
            "preview": preview_records,
            "output_dir": str(run_dir),
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
        "--auth-mode",
        choices=list(VALID_AUTH_MODES),
        default=None,
        help="Authentication backend: plain IMAP password, Gmail app password, or Gmail OAuth.",
    )
    parser.add_argument(
        "--use-gmail-oauth",
        action="store_true",
        help="Compatibility alias for --auth-mode gmail_oauth.",
    )
    parser.add_argument(
        "--gmail-oauth-client-secrets",
        default=os.environ.get("GMAIL_OAUTH_CLIENT_SECRETS"),
        help="Path to a Google OAuth client secrets JSON file.",
    )
    parser.add_argument(
        "--gmail-oauth-token-cache",
        default=os.environ.get("GMAIL_OAUTH_TOKEN_CACHE"),
        help="Optional path to cache Gmail OAuth tokens.",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Do not try to open a browser automatically for Gmail OAuth; print the URL instead.",
    )
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
    parser.add_argument(
        "--from-address",
        action="append",
        default=[],
        help="Match only sender-side headers (From/Reply-To/Sender). Repeat as needed.",
    )
    parser.add_argument(
        "--from-address-file",
        action="append",
        default=[],
        help="Path to newline-delimited sender address list.",
    )
    parser.add_argument(
        "--to-address",
        action="append",
        default=[],
        help="Match only recipient-side headers (To/Cc). Repeat as needed.",
    )
    parser.add_argument(
        "--to-address-file",
        action="append",
        default=[],
        help="Path to newline-delimited recipient address list.",
    )
    parser.add_argument("--search", default="ALL", help='Raw IMAP search criteria, e.g. FROM "person@example.com"')
    parser.add_argument("--since-date", default=None, help="ISO date like 2026-01-01 to add a SINCE filter.")
    parser.add_argument("--before-date", default=None, help="ISO date like 2026-02-01 to add a BEFORE filter.")
    parser.add_argument("--subject-contains", default=None, help="Add a SUBJECT filter without writing raw IMAP syntax.")
    parser.add_argument(
        "--complaint-query",
        default=None,
        help="Free-text complaint description used to rank/filter likely relevant emails.",
    )
    parser.add_argument(
        "--complaint-keyword",
        action="append",
        default=[],
        help="Repeatable complaint keyword or phrase used for relevance filtering.",
    )
    parser.add_argument(
        "--complaint-keyword-file",
        action="append",
        default=[],
        help="Path to newline-delimited complaint keywords/phrases.",
    )
    parser.add_argument(
        "--min-relevance-score",
        type=float,
        default=1.0,
        help="Minimum complaint relevance score required when complaint terms are supplied.",
    )
    parser.add_argument("--limit", type=int, default=None, help="Per-folder message limit")
    parser.add_argument("--timeout", type=int, default=30, help="IMAP timeout seconds")
    parser.add_argument("--no-ssl", action="store_true", help="Disable SSL/TLS")
    parser.add_argument("--output-dir", default=str(DEFAULT_EVIDENCE_ROOT), help="Evidence output root")
    parser.add_argument("--case-slug", default=None, help="Optional folder name under the output root")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview matching emails without saving files or uploading to the workspace.",
    )
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
    auth_mode = _resolve_auth_mode(args)
    if (args.prompt_credentials or args.prompt_password) and not args.password and auth_mode != "gmail_oauth":
        args.password = getpass.getpass("Gmail app password: ")
    if not args.username:
        raise SystemExit(
            "Missing Gmail username. Use --prompt-credentials, set GMAIL_USER, or pass --username."
        )
    if auth_mode == "gmail_oauth":
        if not getattr(args, "gmail_oauth_client_secrets", None):
            raise SystemExit(
                "Gmail OAuth requires --gmail-oauth-client-secrets or GMAIL_OAUTH_CLIENT_SECRETS."
            )
    elif not args.password:
        raise SystemExit(
            "Missing Gmail credentials. Use --prompt-credentials, --prompt-password, or set "
            "GMAIL_USER and GMAIL_APP_PASSWORD."
        )
    try:
        manifest = await import_gmail_evidence(args)
    except ConnectionError as exc:
        raise SystemExit(_humanize_connection_error(exc)) from exc
    if getattr(args, "upload_to_workspace", False) and not getattr(args, "dry_run", False):
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
