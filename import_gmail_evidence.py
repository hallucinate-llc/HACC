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

from complaint_generator.email_credentials import resolve_gmail_credentials
from ipfs_datasets_py.processors.multimedia.email_processor import EmailProcessor
from ipfs_datasets_py.processors.multimedia.google_voice_processor import (
    GoogleVoiceProcessor,
    materialize_google_voice_events,
)
from upload_email_evidence_manifest import upload_manifest

try:
    from ipfs_datasets_py import ipfs_backend_router as _ipfs_router  # type: ignore
except Exception:  # pragma: no cover - optional runtime integration
    _ipfs_router = None

try:
    from multiformats import CID as _CID, multihash as _multihash  # type: ignore
except Exception:  # pragma: no cover - optional runtime integration
    _CID = None
    _multihash = None


DEFAULT_EVIDENCE_ROOT = REPO_ROOT / "evidence" / "email_imports"
DEFAULT_GMAIL_SERVER = "imap.gmail.com"
DEFAULT_GMAIL_FOLDER = "[Gmail]/All Mail"
VALID_AUTH_MODES = ("imap_password", "gmail_app_password", "gmail_oauth")
DEFAULT_CACHE_DIRNAME = "_email_cache"


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


def _load_domain_targets(raw_domains: list[str], domain_files: list[str]) -> set[str]:
    values = list(raw_domains)
    for file_path in domain_files:
        path = Path(file_path).expanduser().resolve()
        values.extend(
            line.strip()
            for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        )
    normalized: set[str] = set()
    for value in values:
        cleaned = str(value or "").strip().lower().lstrip("@")
        if cleaned:
            normalized.add(cleaned)
    return normalized


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


def _addresses_match_domains(addresses: set[str], domains: set[str]) -> bool:
    if not domains:
        return False
    for address in addresses:
        if "@" not in address:
            continue
        domain = address.rsplit("@", 1)[-1].lower()
        if domain in domains:
            return True
    return False


def _message_matches_addresses(
    email_message: EmailMessage,
    targets: set[str],
    *,
    from_targets: set[str] | None = None,
    recipient_targets: set[str] | None = None,
    domain_targets: set[str] | None = None,
    from_domain_targets: set[str] | None = None,
    recipient_domain_targets: set[str] | None = None,
) -> bool:
    if not targets:
        targets = set()
    from_targets = from_targets or set()
    recipient_targets = recipient_targets or set()
    domain_targets = domain_targets or set()
    from_domain_targets = from_domain_targets or set()
    recipient_domain_targets = recipient_domain_targets or set()
    if (
        not targets
        and not from_targets
        and not recipient_targets
        and not domain_targets
        and not from_domain_targets
        and not recipient_domain_targets
    ):
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
    if domain_targets and _addresses_match_domains(participants, domain_targets):
        return True
    if from_domain_targets and _addresses_match_domains(senders, from_domain_targets):
        return True
    if recipient_domain_targets and _addresses_match_domains(recipients, recipient_domain_targets):
        return True
    return False


def _sanitize_filename(filename: str, fallback: str) -> str:
    raw = str(filename or "").strip()
    if not raw:
        return fallback
    raw = raw.replace("/", "_").replace("\\", "_").replace("\x00", "")
    return _slugify(raw)


def _cache_root(output_root: Path) -> Path:
    return output_root / DEFAULT_CACHE_DIRNAME


def _cache_index_path(output_root: Path) -> Path:
    return _cache_root(output_root) / "email_cache_index.json"


def _load_email_cache(output_root: Path) -> dict[str, Any]:
    path = _cache_index_path(output_root)
    if not path.exists():
        return {"version": 1, "entries": {}}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"version": 1, "entries": {}}


def _save_email_cache(output_root: Path, cache_payload: dict[str, Any]) -> None:
    root = _cache_root(output_root)
    root.mkdir(parents=True, exist_ok=True)
    path = _cache_index_path(output_root)
    path.write_text(json.dumps(cache_payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _raw_email_sha256(raw_bytes: bytes) -> str:
    return hashlib.sha256(raw_bytes).hexdigest()


def _build_cache_key(message_id_header: str, raw_sha256: str) -> str:
    cleaned = str(message_id_header or "").strip()
    return cleaned or f"sha256:{raw_sha256}"


def _ipfs_add_bytes(data: bytes) -> str | None:
    if _ipfs_router is None:
        return _offline_raw_cid(data)
    try:
        cid = _ipfs_router.add_bytes(data)
    except Exception:
        return _offline_raw_cid(data)
    return str(cid or "").strip() or None


def _offline_raw_cid(data: bytes) -> str | None:
    if _CID is None or _multihash is None:
        return None
    try:
        digest = _multihash.digest(data, "sha2-256")
        return str(_CID("base32", 1, "raw", digest))
    except Exception:
        return None


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


def _normalize_voice_text(value: str) -> str:
    text = str(value or "")
    markers = [
        "To respond to this text message, reply to this email or visit Google Voice.",
        "YOUR ACCOUNT",
        "HELP CENTER",
        "HELP FORUM",
        "This email was sent to you because you indicated that you'd like to receive",
        "Google LLC",
        "1600 Amphitheatre Pkwy",
        "<https://voice.google.com>",
    ]
    for marker in markers:
        index = text.find(marker)
        if index >= 0:
            text = text[:index]
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip().lower()


def _extract_phone_candidates(*values: str) -> set[str]:
    candidates: set[str] = set()
    for value in values:
        for match in re.findall(r"\+?\d[\d().\-\s]{6,}\d|\(\d{3}\)\s*\d{3}[-.\s]?\d{4}", str(value or "")):
            digits = "".join(char for char in match if char.isdigit())
            if 7 <= len(digits) <= 15:
                candidates.add(digits)
    return candidates


def _is_google_voice_gmail_record(record: dict[str, Any]) -> bool:
    participants = [str(item or "").lower() for item in list(record.get("participants") or [])]
    from_value = str(record.get("from") or "").lower()
    message_id = str(record.get("message_id_header") or "").lower()
    return any("voice.google.com" in value for value in participants) or "voice.google.com" in from_value or "voice.google.com" in message_id


def _find_matching_google_voice_event(
    email_record: dict[str, Any],
    voice_records: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not _is_google_voice_gmail_record(email_record):
        return None
    email_text_source = str(email_record.get("text_content") or "")
    if not email_text_source and email_record.get("email_path") and Path(str(email_record["email_path"])).is_file():
        email_text_source = _collect_message_text(
            email.message_from_bytes(Path(email_record["email_path"]).read_bytes(), policy=email.policy.default)
        )
    email_text = _normalize_voice_text(email_text_source)
    if not email_text:
        return None
    email_numbers = _extract_phone_candidates(
        email_record.get("subject", ""),
        email_record.get("from", ""),
        *list(email_record.get("participants") or []),
    )
    for voice_record in voice_records:
        voice_text = _normalize_voice_text(str(voice_record.get("text_content") or ""))
        if not voice_text:
            continue
        voice_numbers = _extract_phone_candidates(
            voice_record.get("title", ""),
            *list(voice_record.get("participants") or []),
            *list(voice_record.get("phone_numbers") or []),
        )
        phone_match = not email_numbers or not voice_numbers or bool(email_numbers & voice_numbers)
        text_match = email_text == voice_text or email_text in voice_text or voice_text in email_text
        if phone_match and text_match:
            return voice_record
    return None


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
        "source_type": "gmail_email",
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
        "text_content": parsed_email.get("body_text", ""),
        "attachment_paths": [item["path"] for item in attachment_records],
        "attachments": attachment_records,
        "evidence_title": parsed_email.get("subject") or f"Email from {parsed_email.get('from', '')}",
    }


def _cache_entry_from_email(
    *,
    folder_name: str,
    email_message: EmailMessage,
    raw_bytes: bytes,
    parsed_email: dict[str, Any],
    relevance: dict[str, Any],
    bundle_record: dict[str, Any] | None,
) -> dict[str, Any]:
    raw_sha256 = _raw_email_sha256(raw_bytes)
    attachment_shas = []
    if bundle_record:
        attachment_shas = [item.get("sha256") for item in bundle_record.get("attachments", []) if item.get("sha256")]
    return {
        "message_id_header": parsed_email.get("message_id_header", ""),
        "folder": folder_name,
        "subject": parsed_email.get("subject", ""),
        "date": parsed_email.get("date"),
        "from": parsed_email.get("from", ""),
        "to": parsed_email.get("to", ""),
        "cc": parsed_email.get("cc", ""),
        "participants": sorted(_message_participants(email_message)),
        "attachment_count": len(list(parsed_email.get("attachments") or [])),
        "text_content": parsed_email.get("body_text", ""),
        "raw_sha256": raw_sha256,
        "raw_cid": _ipfs_add_bytes(raw_bytes),
        "relevance_score": float(relevance.get("score", 0.0) or 0.0),
        "matched_terms": list(relevance.get("matched_terms") or []),
        "matched_fields": list(relevance.get("matched_fields") or []),
        "bundle_dir": (bundle_record or {}).get("bundle_dir"),
        "email_path": (bundle_record or {}).get("email_path"),
        "parsed_path": (bundle_record or {}).get("parsed_path"),
        "attachment_paths": list((bundle_record or {}).get("attachment_paths") or []),
        "attachment_shas": attachment_shas,
    }


def _cached_bundle_paths(cached_entry: dict[str, Any]) -> tuple[Path | None, Path | None, list[Path]]:
    email_raw = str(cached_entry.get("email_path") or "").strip()
    parsed_raw = str(cached_entry.get("parsed_path") or "").strip()
    attachment_values = [str(path or "").strip() for path in list(cached_entry.get("attachment_paths") or [])]

    def _clean_file_path(raw_value: str) -> Path | None:
        if not raw_value or raw_value == ".":
            return None
        path = Path(raw_value)
        if path.name in {"", "."}:
            return None
        return path

    email_path = _clean_file_path(email_raw)
    parsed_path = _clean_file_path(parsed_raw)
    attachment_paths = [path for path in (_clean_file_path(value) for value in attachment_values) if path is not None]
    return email_path, parsed_path, attachment_paths


def _cached_bundle_is_materialized(cached_entry: dict[str, Any]) -> bool:
    email_path, parsed_path, attachment_paths = _cached_bundle_paths(cached_entry)
    if email_path is None or parsed_path is None:
        return False
    if not email_path.is_file() or not parsed_path.is_file():
        return False
    return all(path.is_file() for path in attachment_paths)


def _resolve_google_voice_manifest_path(source: str | os.PathLike[str]) -> Path | None:
    path = Path(source).expanduser().resolve()
    if path.is_file() and path.name == "google_voice_manifest.json":
        return path
    if path.is_dir():
        candidate = path / "google_voice_manifest.json"
        if candidate.is_file():
            return candidate
    return None


def _load_google_voice_manifest_bundles(source: str | os.PathLike[str]) -> list[dict[str, Any]] | None:
    manifest_path = _resolve_google_voice_manifest_path(source)
    if manifest_path is None:
        return None
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    bundles = []
    for bundle in list(payload.get("bundles") or []):
        item = dict(bundle)
        item.setdefault("source_type", "google_voice")
        item.setdefault("parsed_path", item.get("event_json_path", ""))
        item.setdefault("subject", item.get("title", ""))
        item.setdefault("date", item.get("timestamp"))
        item.setdefault("participants", list(item.get("phone_numbers") or []))
        item.setdefault("attachments", [])
        item.setdefault("text_content", "")
        item.setdefault("deduped_gmail_message_ids", [])
        item.setdefault("evidence_title", item.get("title") or item.get("event_type") or "Google Voice event")
        bundles.append(item)
    return bundles


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


async def _fetch_folder_messages_batched(
    processor: EmailProcessor,
    *,
    folder: str,
    batch_size: int,
    max_messages: int,
    start_offset: int = 0,
) -> list[tuple[bytes, EmailMessage]]:
    def _fetch() -> list[tuple[bytes, EmailMessage]]:
        status, count_data = processor.connection.select(_quote_imap_mailbox(folder), readonly=True)
        if status != "OK":
            raise RuntimeError(f"Failed to select folder {folder!r}: {status}")
        total_messages = int((count_data or [b"0"])[0] or b"0")
        if total_messages <= 0:
            return []
        total_window = max(0, int(max_messages))
        if total_window <= 0:
            return []
        rows: list[tuple[bytes, EmailMessage]] = []
        offset = max(0, int(start_offset))
        high_bound = max(0, total_messages - offset)
        low_bound = max(1, high_bound - total_window + 1)
        step = max(1, int(batch_size))
        low = low_bound
        while low <= high_bound and high_bound > 0:
            high = min(high_bound, low + step - 1)
            ids = [str(value).encode("ascii") for value in range(low, high + 1)]
            for msg_id in ids:
                status, msg_data = processor.connection.fetch(msg_id, "(RFC822)")
                if status != "OK":
                    continue
                raw_bytes = msg_data[0][1]
                msg = email.message_from_bytes(raw_bytes, policy=email.policy.default)
                rows.append((raw_bytes, msg))
            low = high + 1
        return rows

    return await anyio.to_thread.run_sync(_fetch)


async def import_gmail_evidence(args: argparse.Namespace) -> dict[str, Any]:
    targets = _load_address_targets(getattr(args, "address", []), getattr(args, "address_file", []))
    from_targets = _load_address_targets(getattr(args, "from_address", []), getattr(args, "from_address_file", []))
    recipient_targets = _load_address_targets(getattr(args, "to_address", []), getattr(args, "to_address_file", []))
    domain_targets = _load_domain_targets(
        getattr(args, "address_domain", []),
        getattr(args, "address_domain_file", []),
    )
    from_domain_targets = _load_domain_targets(
        getattr(args, "from_domain", []),
        getattr(args, "from_domain_file", []),
    )
    recipient_domain_targets = _load_domain_targets(
        getattr(args, "to_domain", []),
        getattr(args, "to_domain_file", []),
    )
    complaint_terms = _build_complaint_terms(args)
    search_criteria = _build_search_criteria(args)
    output_root = Path(args.output_dir).expanduser().resolve()
    run_dir = output_root / (args.case_slug or datetime.now(UTC).strftime("%Y%m%d_%H%M%S"))
    run_dir.mkdir(parents=True, exist_ok=True)
    cache_payload = _load_email_cache(output_root)
    cache_entries = cache_payload.setdefault("entries", {})

    auth_mode = _resolve_auth_mode(args)
    include_gmail = bool(list(getattr(args, "folder", []) or []))
    processor: EmailProcessor | None = None
    token_payload = None
    if include_gmail:
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
            await processor.connect()

    matched_records: list[dict[str, Any]] = []
    matched_voice_records: list[dict[str, Any]] = []
    preview_records: list[dict[str, Any]] = []
    seen_keys: set[str] = set()
    scanned_message_count = 0

    try:
        for folder in list(getattr(args, "folder", []) or []):
            assert processor is not None
            if getattr(args, "crawl_max_messages", None):
                rows = await _fetch_folder_messages_batched(
                    processor,
                    folder=folder,
                    batch_size=int(getattr(args, "crawl_batch_size", 250) or 250),
                    max_messages=int(getattr(args, "crawl_max_messages", 0) or 0),
                    start_offset=int(getattr(args, "crawl_start_offset", 0) or 0),
                )
            else:
                rows = await _fetch_folder_messages(
                    processor,
                    folder=folder,
                    limit=args.limit,
                    search_criteria=search_criteria,
                )
            for raw_bytes, email_message in rows:
                scanned_message_count += 1
                parsed = processor._parse_email_message(email_message, include_attachments=True)
                if not _message_matches_addresses(
                    email_message,
                    targets,
                    from_targets=from_targets,
                    recipient_targets=recipient_targets,
                    domain_targets=domain_targets,
                    from_domain_targets=from_domain_targets,
                    recipient_domain_targets=recipient_domain_targets,
                ):
                    continue
                relevance = _score_message_relevance(email_message, complaint_terms)
                if complaint_terms and relevance["score"] < float(getattr(args, "min_relevance_score", 1.0)):
                    continue
                raw_sha256 = _raw_email_sha256(raw_bytes)
                dedupe_key = _build_cache_key(parsed.get("message_id_header", ""), raw_sha256)
                if dedupe_key in seen_keys:
                    continue
                seen_keys.add(dedupe_key)
                cached_entry = cache_entries.get(dedupe_key) or {}
                cached_raw_cid = cached_entry.get("raw_cid")
                if not cached_raw_cid:
                    cached_raw_cid = _ipfs_add_bytes(raw_bytes)
                    if cached_entry:
                        cached_entry = {**cached_entry, "raw_cid": cached_raw_cid, "raw_sha256": raw_sha256}
                        cache_entries[dedupe_key] = cached_entry
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
                            "cache_hit": bool(cached_entry),
                            "raw_sha256": raw_sha256,
                            "raw_cid": cached_raw_cid,
                        }
                    )
                    cache_entries[dedupe_key] = _cache_entry_from_email(
                        folder_name=folder,
                        email_message=email_message,
                        raw_bytes=raw_bytes,
                        parsed_email=parsed,
                        relevance=relevance,
                        bundle_record=None,
                    )
                    continue
                if cached_entry:
                    email_path, parsed_path, attachment_paths = _cached_bundle_paths(cached_entry)
                    if _cached_bundle_is_materialized(cached_entry) and email_path and parsed_path:
                        record = {
                            "folder": cached_entry.get("folder", folder),
                            "bundle_dir": str(cached_entry.get("bundle_dir") or email_path.parent),
                            "email_path": str(email_path),
                            "parsed_path": str(parsed_path),
                            "participants": list(cached_entry.get("participants") or []),
                            "subject": cached_entry.get("subject", ""),
                            "date": cached_entry.get("date"),
                            "from": cached_entry.get("from", ""),
                            "to": cached_entry.get("to", ""),
                            "cc": cached_entry.get("cc", ""),
                            "message_id_header": cached_entry.get("message_id_header", ""),
                            "text_content": cached_entry.get("text_content", ""),
                            "attachment_paths": [str(path) for path in attachment_paths],
                            "attachments": [],
                            "evidence_title": cached_entry.get("subject") or f"Email from {cached_entry.get('from', '')}",
                            "relevance_score": relevance["score"],
                            "matched_terms": relevance["matched_terms"],
                            "matched_fields": relevance["matched_fields"],
                            "cache_hit": True,
                            "raw_sha256": raw_sha256,
                            "raw_cid": cached_entry.get("raw_cid"),
                        }
                        matched_records.append(record)
                        cache_entries[dedupe_key] = {
                            **cached_entry,
                            "relevance_score": float(relevance["score"]),
                            "matched_terms": list(relevance["matched_terms"]),
                            "matched_fields": list(relevance["matched_fields"]),
                        }
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
                record["cache_hit"] = False
                record["raw_sha256"] = raw_sha256
                record["raw_cid"] = _ipfs_add_bytes(raw_bytes)
                matched_records.append(record)
                cache_entries[dedupe_key] = _cache_entry_from_email(
                    folder_name=folder,
                    email_message=email_message,
                    raw_bytes=raw_bytes,
                    parsed_email=parsed,
                    relevance=relevance,
                    bundle_record=record,
                )

        voice_sources = [str(item or "").strip() for item in list(getattr(args, "google_voice_source", []) or []) if str(item or "").strip()]
        if voice_sources:
            voice_processor = GoogleVoiceProcessor()
            try:
                seen_voice_ids: set[str] = set()
                pending_voice_events: list[dict[str, Any]] = []
                for source in voice_sources:
                    manifest_bundles = _load_google_voice_manifest_bundles(source)
                    if manifest_bundles is not None:
                        for bundle in manifest_bundles:
                            event_id = str(bundle.get("event_id") or "")
                            if not event_id or event_id in seen_voice_ids:
                                continue
                            seen_voice_ids.add(event_id)
                            if getattr(args, "dry_run", False):
                                preview_records.append(
                                    {
                                        "source_type": "google_voice",
                                        "event_id": event_id,
                                        "event_type": bundle.get("event_type"),
                                        "subject": bundle.get("title"),
                                        "date": bundle.get("date"),
                                        "participants": list(bundle.get("participants") or []),
                                        "attachment_count": len(list(bundle.get("attachment_paths") or [])),
                                        "source_html": bundle.get("source_html_path"),
                                        "manifest_reused": True,
                                    }
                                )
                                continue
                            matched_voice_records.append(bundle)
                        continue

                    parsed_voice = voice_processor.parse_takeout(source)
                    for event in list(parsed_voice.get("events") or []):
                        event_id = str(event.get("event_id") or "")
                        if not event_id or event_id in seen_voice_ids:
                            continue
                        seen_voice_ids.add(event_id)
                        if getattr(args, "dry_run", False):
                            preview_records.append(
                                {
                                    "source_type": "google_voice",
                                    "event_id": event_id,
                                    "event_type": event.get("event_type"),
                                    "subject": event.get("title"),
                                    "date": event.get("timestamp"),
                                    "participants": list(event.get("phone_numbers") or []),
                                    "attachment_count": len(list(event.get("sidecar_paths") or [])),
                                    "source_html": event.get("source_html"),
                                    "manifest_reused": False,
                                }
                            )
                            continue
                        pending_voice_events.append(event)
                if pending_voice_events:
                    materialized = materialize_google_voice_events(
                        pending_voice_events,
                        output_dir=run_dir,
                        start_index=1,
                        filename_prefix="voice",
                        manifest_name="google_voice_manifest.json",
                        source=", ".join(voice_sources),
                    )
                    matched_voice_records.extend(list(materialized.get("bundles") or []))
            finally:
                voice_processor.close()

        deduped_email_records: list[dict[str, Any]] = []
        deduped_gmail_records: list[dict[str, Any]] = []
        if matched_voice_records:
            for email_record in matched_records:
                matched_voice = _find_matching_google_voice_event(email_record, matched_voice_records)
                if matched_voice is None:
                    deduped_email_records.append(email_record)
                    continue
                dedupe_metadata = {
                    "duplicate_of_source_type": "google_voice",
                    "duplicate_of_event_id": matched_voice.get("event_id"),
                    "duplicate_reason": "google_voice_takeout_match",
                }
                email_record["deduped"] = True
                email_record["dedupe_metadata"] = dedupe_metadata
                deduped_gmail_records.append(email_record)
                matched_voice.setdefault("deduped_gmail_message_ids", []).append(email_record.get("message_id_header", ""))
            matched_records = deduped_email_records
        else:
            deduped_gmail_records = []
    finally:
        if processor is not None:
            await processor.disconnect()
        _save_email_cache(output_root, cache_payload)

    manifest = {
        "status": "success",
        "server": args.server,
        "username": args.username,
        "auth_mode": auth_mode,
        "folders": list(getattr(args, "folder", []) or []),
        "search": search_criteria,
        "complaint_terms": complaint_terms,
        "min_relevance_score": float(getattr(args, "min_relevance_score", 1.0)),
        "address_targets": sorted(targets),
        "from_address_targets": sorted(from_targets),
        "recipient_address_targets": sorted(recipient_targets),
        "domain_targets": sorted(domain_targets),
        "from_domain_targets": sorted(from_domain_targets),
        "recipient_domain_targets": sorted(recipient_domain_targets),
        "scanned_message_count": scanned_message_count,
        "matched_email_count": len(matched_records),
        "matched_google_voice_count": len(matched_voice_records),
        "deduped_gmail_google_voice_count": len(deduped_gmail_records),
        "google_voice_sources": [str(item or "") for item in list(getattr(args, "google_voice_source", []) or [])],
        "output_dir": str(run_dir),
        "cache_index_path": str(_cache_index_path(output_root)),
        "emails": matched_records,
        "google_voice_events": matched_voice_records,
        "deduped_gmail_google_voice_records": deduped_gmail_records,
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
        ]
        + [
            {
                "title": item["evidence_title"],
                "kind": "document",
                "source": "google_voice_import",
                "content": (
                    f"Title: {item['title']}\n"
                    f"Event type: {item['event_type']}\n"
                    f"Date: {item['date']}\n"
                    f"Participants: {', '.join(item['participants'])}\n"
                    f"Transcript path: {item['transcript_path']}"
                ),
                "attachment_names": [Path(path).name for path in item["attachment_paths"]],
                "metadata": {
                    "event_id": item["event_id"],
                    "parsed_path": item["parsed_path"],
                    "transcript_path": item["transcript_path"],
                    "source_html_path": item["source_html_path"],
                    "event_type": item["event_type"],
                },
            }
            for item in matched_voice_records
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
            "folders": list(getattr(args, "folder", []) or []),
            "search": search_criteria,
            "complaint_terms": complaint_terms,
            "min_relevance_score": float(getattr(args, "min_relevance_score", 1.0)),
            "address_targets": sorted(targets),
            "from_address_targets": sorted(from_targets),
            "recipient_address_targets": sorted(recipient_targets),
            "domain_targets": sorted(domain_targets),
            "from_domain_targets": sorted(from_domain_targets),
            "recipient_domain_targets": sorted(recipient_domain_targets),
            "scanned_message_count": scanned_message_count,
            "matched_email_count": len([item for item in preview_records if item.get("source_type") != "google_voice"]),
            "matched_google_voice_count": len([item for item in preview_records if item.get("source_type") == "google_voice"]),
            "deduped_gmail_google_voice_count": 0,
            "preview": preview_records,
            "google_voice_sources": [str(item or "") for item in list(getattr(args, "google_voice_source", []) or [])],
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
        "--use-keyring",
        action="store_true",
        help="Load the Gmail app password from the OS keyring when available.",
    )
    parser.add_argument(
        "--save-to-keyring",
        action="store_true",
        help="Save the resolved Gmail app password to the OS keyring when available.",
    )
    parser.add_argument(
        "--use-ipfs-secrets-vault",
        action="store_true",
        help="Load the Gmail app password from the ipfs_datasets_py DID-derived secrets vault.",
    )
    parser.add_argument(
        "--save-to-ipfs-secrets-vault",
        action="store_true",
        help="Save the resolved Gmail app password to the ipfs_datasets_py DID-derived secrets vault.",
    )
    parser.add_argument(
        "--folder",
        action="append",
        default=None,
        help="IMAP folder to scan. Repeat to include multiple folders.",
    )
    parser.add_argument(
        "--google-voice-source",
        action="append",
        default=[],
        help="Path to a Google Voice Takeout directory or zip archive. Repeat to include multiple exports.",
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
        "--address-domain",
        action="append",
        default=[],
        help="Email domain to match in any participant header, e.g. clackamas.us. Repeat as needed.",
    )
    parser.add_argument(
        "--address-domain-file",
        action="append",
        default=[],
        help="Path to newline-delimited participant domain list.",
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
        "--from-domain",
        action="append",
        default=[],
        help="Match only sender-side domains, e.g. clackamas.us. Repeat as needed.",
    )
    parser.add_argument(
        "--from-domain-file",
        action="append",
        default=[],
        help="Path to newline-delimited sender domain list.",
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
    parser.add_argument(
        "--to-domain",
        action="append",
        default=[],
        help="Match only recipient-side domains, e.g. clackamas.us. Repeat as needed.",
    )
    parser.add_argument(
        "--to-domain-file",
        action="append",
        default=[],
        help="Path to newline-delimited recipient domain list.",
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
    parser.add_argument(
        "--crawl-max-messages",
        type=int,
        default=None,
        help="Client-side batched crawl cap. Scans up to this many recent messages directly and ranks locally.",
    )
    parser.add_argument(
        "--crawl-batch-size",
        type=int,
        default=250,
        help="Batch size for client-side batched crawling.",
    )
    parser.add_argument(
        "--crawl-start-offset",
        type=int,
        default=0,
        help="Skip this many newest messages before starting a batched crawl.",
    )
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
    if not args.folder and not list(getattr(args, "google_voice_source", []) or []):
        args.folder = [DEFAULT_GMAIL_FOLDER]
    include_gmail = bool(list(getattr(args, "folder", []) or []))
    auth_mode = _resolve_auth_mode(args)
    if include_gmail:
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
    if not args.username:
        args.username = os.environ.get("GMAIL_USER") or os.environ.get("EMAIL_USER")
    if not args.password:
        args.password = os.environ.get("GMAIL_APP_PASSWORD") or os.environ.get("EMAIL_PASS")
    auth_mode = _resolve_auth_mode(args)
    include_gmail = bool(list(getattr(args, "folder", []) or [])) or not list(getattr(args, "google_voice_source", []) or [])
    if include_gmail and auth_mode != "gmail_oauth":
        args.username, args.password = resolve_gmail_credentials(
            gmail_user=str(args.username or ""),
            gmail_app_password=str(args.password or ""),
            prompt_for_credentials=bool(args.prompt_credentials or args.prompt_password),
            use_keyring=bool(getattr(args, "use_keyring", False)),
            save_to_keyring_flag=bool(getattr(args, "save_to_keyring", False)),
            use_ipfs_secrets_vault=bool(getattr(args, "use_ipfs_secrets_vault", False)),
            save_to_ipfs_secrets_vault_flag=bool(getattr(args, "save_to_ipfs_secrets_vault", False)),
            parser=parser,
        )
    return anyio.run(_run, args)


if __name__ == "__main__":
    raise SystemExit(main())
