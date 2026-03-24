from __future__ import annotations

import email.policy
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import import_gmail_evidence as module


def _build_sample_message() -> EmailMessage:
    message = EmailMessage()
    message["Subject"] = "Termination Notice"
    message["From"] = "Case Manager <manager@example.org>"
    message["To"] = "tenant@example.com"
    message["Cc"] = "lawyer@example.com"
    message["Message-ID"] = "<abc123@example.org>"
    message["Date"] = "Mon, 23 Mar 2026 10:15:00 +0000"
    message.set_content("Please see the attached notice.")
    message.add_attachment(
        b"notice-bytes",
        maintype="application",
        subtype="pdf",
        filename="notice.pdf",
    )
    return message


def test_message_matches_addresses_across_headers() -> None:
    message = _build_sample_message()

    assert module._message_matches_addresses(message, {"manager@example.org"})
    assert module._message_matches_addresses(message, {"tenant@example.com"})
    assert module._message_matches_addresses(message, {"lawyer@example.com"})
    assert not module._message_matches_addresses(message, {"other@example.com"})


def test_message_matches_from_address_filter() -> None:
    message = _build_sample_message()

    assert module._message_matches_addresses(message, set(), from_targets={"manager@example.org"})
    assert not module._message_matches_addresses(message, set(), from_targets={"tenant@example.com"})


def test_message_matches_recipient_address_filter() -> None:
    message = _build_sample_message()

    assert module._message_matches_addresses(message, set(), recipient_targets={"tenant@example.com"})
    assert module._message_matches_addresses(message, set(), recipient_targets={"lawyer@example.com"})
    assert not module._message_matches_addresses(message, set(), recipient_targets={"manager@example.org"})


def test_load_address_targets_supports_file(tmp_path: Path) -> None:
    address_file = tmp_path / "targets.txt"
    address_file.write_text("Manager <manager@example.org>\nTENANT@example.com\n", encoding="utf-8")

    targets = module._load_address_targets(["lawyer@example.com"], [str(address_file)])

    assert targets == {"manager@example.org", "tenant@example.com", "lawyer@example.com"}


def test_load_address_targets_handles_empty_inputs() -> None:
    assert module._load_address_targets([], []) == set()


def test_save_email_bundle_writes_eml_and_attachments(tmp_path: Path) -> None:
    message = _build_sample_message()
    raw_bytes = message.as_bytes(policy=email.policy.default)
    parsed_email = {
        "subject": "Termination Notice",
        "from": "manager@example.org",
        "to": "tenant@example.com",
        "cc": "lawyer@example.com",
        "date": "2026-03-23T10:15:00+00:00",
        "message_id_header": "<abc123@example.org>",
        "attachments": [{"filename": "notice.pdf"}],
    }

    record = module._save_email_bundle(
        root_dir=tmp_path,
        folder_name="[Gmail]/All Mail",
        email_message=message,
        raw_bytes=raw_bytes,
        parsed_email=parsed_email,
        sequence_number=1,
    )

    assert Path(record["email_path"]).exists()
    assert Path(record["parsed_path"]).exists()
    assert len(record["attachment_paths"]) == 1
    assert Path(record["attachment_paths"][0]).read_bytes() == b"notice-bytes"


def test_run_prompts_securely_for_missing_credentials() -> None:
    args = SimpleNamespace(
        username=None,
        password=None,
        prompt_credentials=True,
        prompt_password=False,
        folder=None,
        address=[],
        address_file=[],
        search="ALL",
        case_slug="demo",
        output_dir="evidence/email_imports",
        server="imap.gmail.com",
        port=993,
        timeout=30,
        no_ssl=False,
        limit=None,
    )

    with (
        mock.patch.object(module, "import_gmail_evidence", return_value={"status": "success"}) as import_mock,
        mock.patch.object(module, "input", return_value="user@gmail.com"),
        mock.patch.object(module.getpass, "getpass", return_value="secret-app-password"),
    ):
        result = module.anyio.run(module._run, args)

    assert result == 0
    forwarded_args = import_mock.call_args.args[0]
    assert forwarded_args.username == "user@gmail.com"
    assert forwarded_args.password == "secret-app-password"
    assert forwarded_args.folder == [module.DEFAULT_GMAIL_FOLDER]


def test_run_uses_prompt_password_when_username_already_set() -> None:
    args = SimpleNamespace(
        username="user@gmail.com",
        password=None,
        prompt_credentials=False,
        prompt_password=True,
        folder=["INBOX"],
        address=[],
        address_file=[],
        search="ALL",
        case_slug="demo",
        output_dir="evidence/email_imports",
        server="imap.gmail.com",
        port=993,
        timeout=30,
        no_ssl=False,
        limit=None,
    )

    with (
        mock.patch.object(module, "import_gmail_evidence", return_value={"status": "success"}) as import_mock,
        mock.patch.object(module.getpass, "getpass", return_value="secret-app-password"),
    ):
        result = module.anyio.run(module._run, args)

    assert result == 0
    forwarded_args = import_mock.call_args.args[0]
    assert forwarded_args.username == "user@gmail.com"
    assert forwarded_args.password == "secret-app-password"


def test_run_can_upload_manifest_to_workspace() -> None:
    args = SimpleNamespace(
        username="user@gmail.com",
        password="secret-app-password",
        prompt_credentials=False,
        prompt_password=False,
        folder=["INBOX"],
        address=[],
        address_file=[],
        search="ALL",
        case_slug="demo",
        output_dir="evidence/email_imports",
        server="imap.gmail.com",
        port=993,
        timeout=30,
        no_ssl=False,
        limit=None,
        upload_to_workspace=True,
        review_after_upload=True,
        generate_after_upload=True,
        export_packet_after_upload=True,
        export_markdown_after_upload=True,
        user_id="case-user",
        claim_element_id="notice",
    )

    with (
        mock.patch.object(
            module,
            "import_gmail_evidence",
            return_value={"status": "success", "output_dir": "/tmp/email-import"},
        ),
        mock.patch.object(
            module,
            "upload_manifest",
            return_value={"status": "success", "uploaded_count": 1},
        ) as upload_mock,
    ):
        result = module.anyio.run(module._run, args)

    assert result == 0
    upload_mock.assert_called_once_with(
        "/tmp/email-import/email_import_manifest.json",
        user_id="case-user",
        claim_element_id="notice",
        source="gmail_import",
        review_after_upload=True,
        generate_after_upload=True,
        export_packet_after_upload=True,
        export_markdown_after_upload=True,
    )


def test_run_dry_run_skips_workspace_upload() -> None:
    args = SimpleNamespace(
        username="user@gmail.com",
        password="secret-app-password",
        prompt_credentials=False,
        prompt_password=False,
        folder=["INBOX"],
        address=[],
        address_file=[],
        from_address=[],
        from_address_file=[],
        to_address=[],
        to_address_file=[],
        search="ALL",
        case_slug="demo",
        output_dir="evidence/email_imports",
        server="imap.gmail.com",
        port=993,
        timeout=30,
        no_ssl=False,
        limit=None,
        upload_to_workspace=True,
        review_after_upload=True,
        generate_after_upload=True,
        export_packet_after_upload=True,
        export_markdown_after_upload=True,
        dry_run=True,
        user_id="case-user",
        claim_element_id="notice",
    )

    with (
        mock.patch.object(
            module,
            "import_gmail_evidence",
            return_value={"status": "success", "dry_run": True, "output_dir": "/tmp/email-import"},
        ),
        mock.patch.object(module, "upload_manifest") as upload_mock,
    ):
        result = module.anyio.run(module._run, args)

    assert result == 0
    upload_mock.assert_not_called()
